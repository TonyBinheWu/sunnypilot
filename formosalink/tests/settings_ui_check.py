"""Native Params and actual C3X/C4 control integration, explicitly invoked."""
from pathlib import Path
import tempfile
import time
import unittest
import uuid
from unittest.mock import patch

import pyray as rl
from openpilot.common.params import Params
from openpilot.system.ui.lib.application import gui_app
from openpilot.sunnypilot.formosalink.device_settings import SettingsProvider, NativeSettingsProvider
from openpilot.sunnypilot.formosalink.ui_sync import refresh_controls


def command(snapshot,device_id):
  now=time.time()
  return {"id":str(uuid.uuid4()),"device_id":device_id,"key":"QuietMode","value":True,"session":snapshot["session"],
          "expected_revision":snapshot["revision"],"created_at":now,"expires_at":now+20}


class TestSettingsProfile(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    rl.set_config_flags(rl.ConfigFlags.FLAG_WINDOW_HIDDEN)
    gui_app.init_window("FormosaLink settings integration")

  @classmethod
  def tearDownClass(cls):
    gui_app.close()

  def test_native_catalog_and_params_write(self):
    with tempfile.TemporaryDirectory() as directory:
      params=Params(directory)
      self.assertFalse(params.get_bool("FormosaLinkRemoteSettings"))
      params.put_bool("FormosaLinkEnabled",True,block=True)
      params.put_bool("FormosaLinkRemoteSettings",True,block=True)
      params.put_bool("QuietMode",False,block=True)
      native=NativeSettingsProvider()
      self.assertIn("version",native.info())
      source=SettingsProvider(params,native.schema,lambda:{},lambda:True,translate=native.translate)
      snapshot=source.capture()
      self.assertGreater(len(snapshot["catalog"]),40)
      self.assertNotIn("RecordFront",snapshot["values"])
      cmd=command(snapshot,device_id="00000000-0000-0000-0000-000000000001")
      receipt=source.apply(cmd,cmd["device_id"],time.monotonic()+5)
      self.assertEqual(receipt["status"],"applied")
      self.assertTrue(params.get_bool("QuietMode"))
      self.assertTrue(params.get("FormosaLinkSettingsVersion"))

  def test_navigation_native_json_readback(self):
    from openpilot.sunnypilot.formosalink.navigation import encode
    with tempfile.TemporaryDirectory() as directory:
      params=Params(directory)
      for key in ("FormosaLinkEnabled","FormosaLinkRemoteSettings","NavigationEnabled"):
        params.put_bool(key,True,block=True)
      source=SettingsProvider(params,{"panels":[]},lambda:{},lambda:True,navigation=True)
      cmd=command(source.capture(),"00000000-0000-0000-0000-000000000001")
      cmd.update(key="NavDestination",value=encode({"latitude":25.03,"longitude":121.56,"place_name":"DEMO"}))
      self.assertEqual(source.apply(cmd,cmd["device_id"],time.monotonic()+5)["status"],"applied")
      self.assertEqual(params.get("NavDestination")["latitude"],25.03)

  def test_all_hyundai_kia_profiles_and_native_dbc(self):
    import json,os
    from opendbc.car import Bus
    from opendbc.car.hyundai.values import CAR,DBC,HyundaiFlags
    from opendbc.can.dbc import DBC as Database
    from opendbc.can import CANPacker
    from openpilot.sunnypilot.formosalink.hyundai_soc import SocTracker,profile,verify_aux_dbc
    rows=[]
    for model in CAR:
      canfd=bool(model.config.flags&HyundaiFlags.CANFD)
      verified=verify_aux_dbc(Database(DBC[model][Bus.pt])) if not canfd else False
      detected=profile("hyundai",str(model),canfd,verified)
      self.assertFalse(detected["traction_supported"])
      self.assertFalse(canfd and detected["aux_supported"])
      rows.append(detected)
    self.assertGreater(len(rows),50)
    output=Path(os.environ.get("FORMOSALINK_QR_OUTPUT","build/formosalink-soc"));output.mkdir(parents=True,exist_ok=True)
    (output/"soc_profiles.json").write_text(json.dumps(rows,indent=2))
    packer=CANPacker(DBC[CAR.HYUNDAI_SONATA][Bus.pt])
    tracker=SocTracker();tracker.configure(profile("hyundai",str(CAR.HYUNDAI_SONATA),False,True))
    for index in range(2):
      frame=packer.make_can_msg("BAT11",0,{"BAT_SOC":72,"BAT_SNSR_V":12.6,"BAT_SNSR_State":1})
      tracker.feed(frame[0],frame[2],frame[1],10+index*.1,10+index*.1)
    self.assertEqual(tracker.snapshot(10.1)["aux_soc_percent"],72)
    self.assertEqual(tracker.snapshot(10.1)["aux_battery_voltage"],12.6)

  def test_native_vehicle_identity_selects_soc_without_user_choice(self):
    from types import SimpleNamespace
    from opendbc.car.structs import car
    from opendbc.car.hyundai.values import CAR,HyundaiFlags
    from openpilot.sunnypilot.formosalink.hyundai_soc import NativeSocObserver
    cp=car.CarParams.new_message(brand="hyundai",carFingerprint=str(CAR.HYUNDAI_SONATA),flags=0)
    raw=[cp.to_bytes()];params=SimpleNamespace(get=lambda key:raw[0])
    observer=NativeSocObserver(params)
    with patch("threading.Thread.start") as start:
      state=observer.capture();self.assertEqual(state["aux_soc_status"],"waiting");start.assert_called_once()
      cp=car.CarParams.new_message(brand="hyundai",carFingerprint=str(CAR.HYUNDAI_IONIQ_5),flags=int(HyundaiFlags.CANFD|HyundaiFlags.EV));raw[0]=cp.to_bytes()
      state=observer.capture();self.assertEqual(state["aux_soc_status"],"unsupported");self.assertEqual(state["vehicle_powertrain"],"EV")

  def test_cached_native_controls_refresh_without_writing(self):
    from openpilot.system.ui.sunnypilot.widgets.toggle import ToggleSP
    from openpilot.system.ui.sunnypilot.widgets.option_control import OptionControlSP
    from openpilot.system.ui.sunnypilot.widgets.list_view import MultipleButtonActionSP
    from openpilot.selfdrive.ui.mici.widgets.button import BigParamControl, BigMultiParamToggle
    with tempfile.TemporaryDirectory() as directory:
      params=Params(directory);params.put_bool("QuietMode",False,block=True);params.put("CameraOffset",0.0,block=True);params.put("LongitudinalPersonality",1,block=True)
      with patch("openpilot.system.ui.sunnypilot.widgets.toggle.Params",return_value=params),patch("openpilot.system.ui.sunnypilot.widgets.option_control.Params",return_value=params),patch("openpilot.system.ui.sunnypilot.widgets.list_view.Params",return_value=params),patch("openpilot.selfdrive.ui.mici.widgets.button.Params",return_value=params):
        widgets=[ToggleSP(param="QuietMode",callback=lambda _:self.fail("must not call toggle callback")),OptionControlSP("CameraOffset",-35,35,use_float_scaling=True),MultipleButtonActionSP(["0","1","2"],100,param="LongitudinalPersonality"),BigParamControl("Quiet","QuietMode"),BigMultiParamToggle("Style","LongitudinalPersonality",["0","1","2"])]
      params.put_bool("QuietMode",True,block=True);params.put("CameraOffset",.12,block=True);params.put("LongitudinalPersonality",2,block=True)
      with patch.object(params,"put",side_effect=AssertionError("refresh must not write")),patch.object(params,"put_bool",side_effect=AssertionError("refresh must not write")):
        refresh_controls(widgets)
      self.assertTrue(widgets[0]._state)
      self.assertEqual(widgets[1].current_value,12)
      self.assertEqual(widgets[2].selected_button,2)
      self.assertTrue(widgets[3]._checked)
      self.assertEqual(widgets[4].value,"2")

  def test_local_permission_button(self):
    from openpilot.sunnypilot.formosalink import ui
    with tempfile.TemporaryDirectory() as directory:
      params=Params(directory)
      with patch.object(ui.ui_state,"params",params),patch.object(ui.ui_state,"is_offroad",return_value=True) as parked:
        dialog=ui.FormosaPairingDialog()
        dialog._toggle_remote();self.assertTrue(params.get_bool("FormosaLinkRemoteSettings"))
        parked.return_value=False;dialog._toggle_remote();self.assertTrue(params.get_bool("FormosaLinkRemoteSettings"))
        parked.return_value=True;dialog._disable_monitoring();self.assertFalse(params.get_bool("FormosaLinkRemoteSettings"))
        dialog.hide_event()
