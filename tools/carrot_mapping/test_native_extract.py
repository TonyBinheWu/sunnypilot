"""Native CI only: real full-cereal rlog -> extracted observations -> 3D map."""
import json
from types import SimpleNamespace

from openpilot.cereal import log
from tools.carrot_mapping.__main__ import extract
from tools.carrot_mapping.pipeline import build_map


def test_real_rlog_model_and_calibration(tmp_path):
  calibration=log.Event.new_message()
  calibration.logMonoTime=1_000_000_000
  calibration.valid=True
  calibration.init('liveCalibration')
  calibration.liveCalibration.calStatus='calibrated'
  calibration.liveCalibration.rpyCalib=[0.,0.,0.]
  event=log.Event.new_message()
  event.logMonoTime=1_050_000_000
  event.valid=True
  event.init('modelV2')
  model=event.modelV2
  model.timestampEof=1_040_000_000
  model.frameId=10
  model.init('laneLines',1)
  model.laneLines[0].x=[10.]
  model.laneLines[0].y=[2.]
  model.laneLines[0].z=[1.]
  model.laneLineProbs=[.9]
  model.laneLineStds=[.1]
  path=tmp_path/'rlog';path.write_bytes(calibration.to_bytes()+event.to_bytes())
  out=tmp_path/'observations.jsonl'
  extract(SimpleNamespace(trip='trip-a',vehicle='car-a',clock='boot-a',rlog=str(path),output=out))
  rows=[json.loads(line) for line in out.read_text().splitlines()]
  assert len(rows)==1 and rows[0]['calibration_valid'] and rows[0]['timestamp_ns']=='1040000000'
  assert rows[0]['native_calibration']['calStatus']=='calibrated'
  pose={'schema':'carrot-mapping-poses/v1','frame':{'id':'test','axes':'ENU','units':'m'},'trajectories':[
    {'trip_id':'trip-a','vehicle_id':'car-a','clock_id':'boot-a','calibration_id':'cal-a','source':'synthetic',
     'poses':[{'timestamp_ns':'1040000000','frame_id':10,'translation':[0,0,0],
               'quaternion_wxyz':[0,2**-.5,2**-.5,0],'position_std_m':.1,'orientation_std_deg':.1}]}]}
  assert build_map(rows,pose)['cells'][0]['xyz']==[2.,10.,-1.]
