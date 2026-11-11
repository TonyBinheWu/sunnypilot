import copy
import json
import sqlite3
import time
import uuid
from types import SimpleNamespace

import pytest

from formosalink.tests.test_platform import client, pair, ORIGIN
from openpilot.sunnypilot.formosalink.device_settings import SettingsProvider
from openpilot.sunnypilot.formosalink.management_protocol import validate_snapshot
from openpilot.sunnypilot.formosalink.protocol import sign
from openpilot.sunnypilot.formosalink.settings import rule_value, revision

SCHEMA = {"panels":[{"label":"Display","remote_configurable":True,"sections":[{"items":[
  {"key":"QuietMode","title":"Quiet Mode","widget":"toggle"},
  {"key":"CameraOffset","title":"Adjust Camera Offset","widget":"option","min":-.35,"max":.35,"step":.01},
  {"key":"Count","title":"Count","widget":"option","min":0,"max":10,"step":1},
  {"key":"SshEnabled","title":"SSH","widget":"toggle"}]}]}]}


class Params:
  def __init__(self):
    self.values={"QuietMode":False,"CameraOffset":0.0,"Count":1,"FormosaLinkEnabled":True,"FormosaLinkRemoteSettings":True,"ParamsVersion":0}
    self.writes=[]

  def get_type(self,key):
    if key not in self.values:
      raise KeyError(key)
    return SimpleNamespace(name={bool:"BOOL",float:"FLOAT",int:"INT"}[type(self.values[key])])

  def get(self,key,return_default=False):
    return self.values.get(key)

  def get_bool(self,key):
    return bool(self.get(key))

  def put(self,key,value):
    self.values[key]=value
    self.writes.append((key,value))


def provider():
  params=Params()
  guard=SimpleNamespace(parked=True)
  return SettingsProvider(params,SCHEMA,lambda:{},lambda:guard.parked,lambda:{"serial":"TEST"}),params,guard


def command(state,key="QuietMode",value=True,device_id=None):
  now=time.time()
  return {"id":str(uuid.uuid4()),"device_id":device_id or str(uuid.uuid4()),"key":key,"value":value,
          "session":state["session"],"expected_revision":state["revision"],"created_at":now,"expires_at":now+20}


def sync(client,device,private,state):
  return client.post("/api/v1/agent/sync",json=sign(private,device,"sync",state))


def test_apply_reads_back_and_refresh_stamp():
  source,params,_=provider(); state=source.capture(); cmd=command(state)
  assert "SshEnabled" not in state["values"]
  assert validate_snapshot(state)==state
  assert source.apply(cmd,cmd["device_id"],time.monotonic()+10)=={"id":cmd["id"],"status":"applied","reason":"applied"}
  assert params.values["QuietMode"] is True
  assert params.values["ParamsVersion"]==1 and params.values["FormosaLinkSettingsVersion"]
  assert source.capture()["revision"]!=state["revision"]


def test_write_without_matching_device_readback_is_not_applied():
  source,params,_=provider()
  cmd=command(source.capture())
  params.put=lambda key,value,block=True: None
  receipt=source.apply(cmd,cmd["device_id"],time.monotonic()+10)
  assert receipt=={"id":cmd["id"],"status":"rejected","reason":"write_failed"}
  assert params.values["QuietMode"] is False
  assert params.values["ParamsVersion"]==0


@pytest.mark.parametrize("failure",["onroad","disabled","revision","session","expired","wrong_device","range","type","secret"])
def test_device_rejects_unsafe_or_conflicting_writes(failure):
  source,params,guard=provider();cmd=command(source.capture());device=cmd["device_id"];deadline=time.monotonic()+5
  if failure=="onroad":guard.parked=False
  if failure=="disabled":params.values["FormosaLinkRemoteSettings"]=False
  if failure=="revision":params.values["Count"]=2
  if failure=="session":cmd["session"]=str(uuid.uuid4())
  if failure=="expired":deadline=time.monotonic()-1
  if failure=="wrong_device":device=str(uuid.uuid4())
  if failure=="range":cmd.update(key="CameraOffset",value=.355)
  if failure=="type":cmd["value"]=1
  if failure=="secret":cmd["key"]="SshEnabled"
  assert source.apply(cmd,device,deadline)["status"]=="rejected"
  assert not params.writes


def test_final_guard_is_checked_immediately_before_write():
  source,params,_=provider();cmd=command(source.capture())
  calls=iter([True,True,False]);source.guard=lambda:next(calls)
  assert source.apply(cmd,cmd["device_id"],time.monotonic()+10)["reason"]=="offroad_required"
  assert not params.writes


def test_offroad_transition_invalidates_old_session():
  source,_,guard=provider();cmd=command(source.capture())
  guard.parked=False;source.capture();guard.parked=True
  assert source.apply(cmd,cmd["device_id"],time.monotonic()+5)["reason"]=="wrong_session"


def test_full_owner_scoped_signed_sync_and_acknowledged_readback(client):
  device,private,_=pair(client);source,params,_=provider();state=source.capture()
  assert sync(client,device,private,state).status_code==200
  path=f"/api/v1/devices/{device}/settings"
  body={"key":"QuietMode","value":True,"expected_revision":state["revision"],"session":state["session"]}
  queued=client.post(path,json=body,headers={"Origin":ORIGIN});assert queued.status_code==200
  assert client.post(path,json=body,headers={"Origin":ORIGIN}).status_code==409
  delivery=sync(client,device,private,source.capture()).json();cmd=delivery["command"]
  assert cmd["id"]==queued.json()["id"]
  assert sync(client,device,private,source.capture()).json()["command"] is None
  receipt=source.apply(cmd,device,time.monotonic()+10)
  assert params.values["QuietMode"] is True
  state=source.capture();state["receipts"]=[receipt]
  assert sync(client,device,private,state).json()["acknowledged"]==[cmd["id"]]
  details=client.get(path).json()
  assert details["snapshot"]["values"]["QuietMode"] is True
  assert details["commands"][0]["status"]=="applied"
  assert client.post(path,json=body,headers={"Origin":ORIGIN}).status_code==409
  store=client.app.state.store
  other=store.github_user("55555","other")
  client.cookies.set("formosalink_session",store.session(other),domain="formosapilot.dinglu-t.com",path="/api")
  assert client.get(path).status_code==404
  assert client.post(path,json=body,headers={"Origin":ORIGIN}).status_code==404


@pytest.mark.parametrize("state_change",["stale","onroad","disabled","revoke"])
def test_server_guards(client,state_change):
  device,private,_=pair(client);source,_,_=provider();state=source.capture()
  if state_change=="onroad":state["offroad"]=False
  if state_change=="disabled":state["remote_enabled"]=False
  assert sync(client,device,private,state).status_code==200
  store=client.app.state.store
  if state_change=="stale":
    with store.connection() as db:db.execute("UPDATE device_management SET received_at=0")
  if state_change=="revoke":store.revoke(device)
  response=client.post(f"/api/v1/devices/{device}/settings",json={"key":"QuietMode","value":True,"expected_revision":state["revision"],"session":state["session"]},headers={"Origin":ORIGIN})
  assert response.status_code==(404 if state_change=="revoke" else 409)
  if state_change=="revoke":assert sync(client,device,private,state).status_code==403


def test_sync_signature_replay_and_origin(client):
  device,private,_=pair(client);source,_,_=provider();envelope=sign(private,device,"sync",source.capture())
  assert client.post("/api/v1/agent/sync",json=envelope).status_code==200
  assert client.post("/api/v1/agent/sync",json=envelope).status_code==403
  envelope=sign(private,device,"sync",source.capture());envelope["payload"]["offroad"]=False
  assert client.post("/api/v1/agent/sync",json=envelope).status_code==403
  assert client.post(f"/api/v1/devices/{device}/settings",json={}).status_code==403


def test_native_rules_unknown_fail_closed_and_numeric_equality():
  assert rule_value({"type":"not","condition":{"type":"unknown"}},{},{},True) is None
  assert rule_value({"type":"param","key":"X","equals":1},{"X":1.0},{},True) is True
  assert rule_value({"type":"param","key":"X","equals":True},{"X":1},{},True) is False


@pytest.mark.parametrize("bad",[{"key":[]},{"key":"QuietMode","type":"BYTES"},"invalid"])
def test_malformed_catalog_rejected_without_server_error(bad):
  source,_,_=provider();state=source.capture();state["catalog"]=[bad];state["catalog_revision"]=revision(state["catalog"]);state["revision"]=revision({"catalog":state["catalog_revision"],"values":state["values"]})
  with pytest.raises(ValueError):validate_snapshot(state)


def test_schema2_migration_preserves_users_devices_and_credentials(client):
  from formosalink.server.store import Store
  device,_,_=pair(client);store=client.app.state.store
  before=store.devices()
  with store.connection() as db:
    db.executescript("DROP TABLE setting_commands; DROP TABLE device_management; PRAGMA user_version=2;")
  migrated=Store(store.path)
  assert migrated.devices()==before
  assert migrated.principal(client.cookies.get("formosalink_session"))["id"]=="local-admin"
  with sqlite3.connect(store.path+".before-v3.sqlite3") as db:assert db.execute("PRAGMA user_version").fetchone()[0]==2


def test_real_management_client_receipts_survive_lost_ack(client,tmp_path):
  from openpilot.sunnypilot.formosalink.management import ManagementClient
  device,private,_=pair(client);source,params,_=provider()
  identity={"device_id":device,"origin":ORIGIN}
  class Response:
    def __init__(self,value):self.value=value
    def raise_for_status(self):self.value.raise_for_status()
    def iter_content(self,size):yield self.value.content
    def close(self):pass
  class Session:
    fail=False
    def post(self,url,json,**kwargs):
      value=client.post(url,json=json)
      if self.fail:raise OSError("lost response after server commit")
      return Response(value)
  session=Session();agent=ManagementClient(identity,private,source,tmp_path)
  agent.once(session);state=source.capture()
  queued=client.app.state.store.queue_setting(device,"local-admin","QuietMode",True,state["revision"],state["session"])
  agent.once(session)
  assert params.values["QuietMode"] is True
  assert len([x for x in params.writes if x[0]=="QuietMode"])==1
  session.fail=True
  with pytest.raises(OSError):agent.once(session)
  assert len(agent.receipts)==1
  # A restarted client retransmits the persisted receipt, never a Params write.
  agent=ManagementClient(identity,private,source,tmp_path);session.fail=False;agent.once(session)
  assert not agent.receipts
  assert client.app.state.store.management(device,"local-admin")["commands"][0]["status"]=="applied"
  assert len([x for x in params.writes if x[0]=="QuietMode"])==1


def test_expired_delivery_is_not_replayed_and_revocation_cancels(client):
  device,private,_=pair(client);source,_,_=provider();state=source.capture();sync(client,device,private,state)
  store=client.app.state.store
  queued=store.queue_setting(device,"local-admin","QuietMode",True,state["revision"],state["session"])
  with store.connection() as db:db.execute("UPDATE setting_commands SET expires_at=0")
  assert sync(client,device,private,source.capture()).json()["command"] is None
  assert store.management(device,"local-admin")["commands"][0]["status"]=="expired"
  store.queue_setting(device,"local-admin","QuietMode",True,state["revision"],state["session"])
  store.revoke(device)
  with store.connection() as db:
    assert db.execute("SELECT COUNT(*) FROM device_management").fetchone()[0]==0
    assert db.execute("SELECT COUNT(*) FROM setting_commands WHERE status='cancelled'").fetchone()[0]==1
