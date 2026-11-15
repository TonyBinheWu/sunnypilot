import copy
import importlib
import json
from pathlib import Path
import sys
import types

import numpy as np
import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from tools.carrot_mapping.pipeline import build_map, rotation, ply
from tools.carrot_mapping.__main__ import demo, write_new


def inputs():
  observation = {'schema':'carrot-lane-observations/v1','trip_id':'t1','vehicle_id':'v1','clock_id':'boot1',
                 'frame_id':10,'timestamp_ns':'1000000000','model_frame':'calibrated_FRD',
                 'valid':True,'calibration_valid':True,'lanes':[{'probability':.9,'std_m':.1,'points':[[10,2,1]]}]}
  poses = {'schema':'carrot-mapping-poses/v1','frame':{'id':'survey-a','axes':'ENU','units':'m'},
           'trajectories':[{'trip_id':'t1','vehicle_id':'v1','clock_id':'boot1','calibration_id':'cal1',
                            'source':'surveyed','poses':[{'timestamp_ns':'1000000000','frame_id':10,
                              'translation':[3,4,5],'quaternion_wxyz':[0,2**-.5,2**-.5,0],
                              'position_std_m':.1,'orientation_std_deg':.2}]}]}
  return observation, poses


def test_frd_to_enu_preserves_right_sign_height_and_origin():
  observation,poses=inputs()
  result=build_map([observation],poses)
  # Heading North: forward->North, right->East, down->negative Up.
  assert result['cells'][0]['xyz']==[5,14,4]
  assert not result['ground_truth'] and not result['control_eligible'] and not result['pose_verified']
  assert 'property float z' in ply(result)
  assert np.linalg.det(rotation(poses['trajectories'][0]['poses'][0]['quaternion_wxyz']))==pytest.approx(1)


@pytest.mark.parametrize('change,code',[
  (lambda o,p:o.update(calibration_valid=False),'invalid_model_or_calibration'),
  (lambda o,p:o.update(valid=False),'invalid_model_or_calibration'),
  (lambda o,p:p['trajectories'][0]['poses'][0].update(timestamp_ns='1025000001'),'pose_time_or_frame_mismatch'),
  (lambda o,p:p['trajectories'][0]['poses'][0].update(frame_id=11),'pose_time_or_frame_mismatch'),
  (lambda o,p:p['trajectories'][0]['poses'][0].update(position_std_m=1.01),'pose_uncertainty'),
  (lambda o,p:o['lanes'][0].update(probability=.69),'weak_lane'),
  (lambda o,p:o['lanes'][0].update(points=[[61,0,0]]),'range'),
  (lambda o,p:p['trajectories'][0]['poses'][0].update(position_std_m=1,orientation_std_deg=2),'combined_uncertainty'),
])
def test_admission_gates(change,code):
  o,p=inputs();change(o,p)
  # Farther point makes the combined indicator exceed 2m.
  if code=='combined_uncertainty':o['lanes'][0]['points']=[[55,0,0]]
  result=build_map([o],p)
  assert not result['cells'] and result['rejected'][code]>0


def test_time_boundary_and_nearest_pose_not_arrival_time():
  o,p=inputs();p['trajectories'][0]['poses'][0]['timestamp_ns']='1025000000'
  assert len(build_map([o],p)['cells'])==1


def test_duplicate_frames_one_vote_and_copied_trips_rejected():
  o,p=inputs();result=build_map([o,o],p)
  assert result['rejected']['duplicate_frame']==1
  assert result['cells'][0]['trip_ids']==['t1']
  other=copy.deepcopy(o);other['trip_id']='t2';other['vehicle_id']='v2'
  trip=copy.deepcopy(p['trajectories'][0]);trip['trip_id']='t2';trip['vehicle_id']='v2';p['trajectories'].append(trip)
  with pytest.raises(ValueError,match='duplicated_trip_content'):build_map([o,other],p)


def test_two_trips_support_and_overpass_not_merged():
  o,p=inputs();other=copy.deepcopy(o);other.update(trip_id='t2',vehicle_id='v2',frame_id=11)
  trip=copy.deepcopy(p['trajectories'][0]);trip.update(trip_id='t2',vehicle_id='v2');trip['poses'][0]['frame_id']=11
  trip['poses'][0]['translation'][0]+=.1;p['trajectories'].append(trip)
  result=build_map([o,other],p)
  assert len(result['cells'])==1 and result['cells'][0]['vehicle_count']==2
  assert result['cells'][0]['dispersion_m']==pytest.approx(.05)
  trip['poses'][0]['translation'][2]+=5
  assert len(build_map([o,other],p)['cells'])==2


def test_revisions_and_unobserved_not_deleted_road_claims():
  o,p=inputs();first=build_map([o],p)
  o['lanes'][0]['points']=[[12,2,1]]
  second=build_map([o],p,first)
  assert second['parent_revision']==first['revision'] and second['revision']!=first['revision']
  assert second['changes']['unobserved_cells']==[first['cells'][0]['id']]
  p['frame']['id']='other-origin'
  with pytest.raises(ValueError,match='frame_mismatch'):build_map([o],p,first)


@pytest.mark.parametrize('field,value', [('clock_id','other-boot'),('vehicle_id','other-car')])
def test_identity_and_clocks_never_silently_aligned(field,value):
  o,p=inputs();o[field]=value
  with pytest.raises(ValueError,match='clock_mismatch'):build_map([o],p)


def test_invalid_quaternion_nan_and_rewinding_clock_rejected():
  o,p=inputs();p['trajectories'][0]['poses'][0]['quaternion_wxyz']=[1,1,1,1]
  with pytest.raises(ValueError):build_map([o],p)
  o,p=inputs();o['lanes'][0]['points']=[[float('nan'),0,0]]
  with pytest.raises(ValueError):build_map([o],p)
  o,p=inputs();before=copy.deepcopy(o);before['timestamp_ns']='999999999'
  with pytest.raises(ValueError,match='clock_not_increasing'):build_map([o,before],p)


def test_immutable_write_and_deterministic_demo(tmp_path):
  project=demo();assert project==demo() and project['cells']
  path=tmp_path/'map.json';write_new(path,json.dumps(project))
  with pytest.raises(FileExistsError):write_new(path,'overwrite')
  assert json.loads(path.read_text())==project


def test_modified_parent_revision_is_not_a_valid_comparison():
  o,p=inputs();previous=build_map([o],p);previous['cells'][0]['xyz'][0]+=2
  with pytest.raises(ValueError,match='revision_invalid'):build_map([o],p,previous)


def test_rounded_optimizer_rotations_stay_rigid_and_boolean_frame_ids_are_invalid():
  o,p=inputs()
  q=[0,.7070,.7070,0]
  r=rotation(q)
  assert np.allclose(r.T @ r,np.eye(3),atol=1e-12)
  assert np.linalg.norm(r @ np.array([60,0,0]))==pytest.approx(60)
  p['trajectories'][0]['poses'][0]['frame_id']=True
  with pytest.raises(ValueError,match='invalid_pose_frame_id'):build_map([o],p)


def load_feature():
  # Do not import the full server registry/native Params for isolated HTTP tests.
  folder=Path(__file__).resolve().parents[2]/'openpilot/selfdrive/carrot/server/features'
  package=types.ModuleType('_mapping_feature_tests');package.__path__=[str(folder)];sys.modules[package.__name__]=package
  return importlib.import_module(package.__name__+'.lane_mapping')


def test_readonly_http_catalog_revision_limits_and_paths(tmp_path):
  import asyncio
  feature=load_feature()
  project=demo();write_new(tmp_path/'sample.json',json.dumps(project))
  write_new(tmp_path/'corrupt.json','{}')
  async def check():
    app=web.Application();feature.register(app,tmp_path)
    async with TestClient(TestServer(app)) as client:
      response=await client.get('/api/lane-mapping/projects')
      assert (await response.json())['projects']==['corrupt','sample']
      response=await client.get('/api/lane-mapping/projects/sample');assert response.status==200
      assert (await response.json())['revision']==project['revision']
      assert (await client.get('/api/lane-mapping/projects/corrupt')).status==404
      assert (await client.post('/api/lane-mapping/projects/sample',json={})).status==405
      project['cells'][0]['xyz'][0]+=1
      (tmp_path/'sample.json').write_text(json.dumps(project))
      assert (await client.get('/api/lane-mapping/projects/sample')).status==404
  asyncio.run(check())
  with pytest.raises(ValueError):feature.read_project(tmp_path,'../secrets')
  oversized=tmp_path/'large.json'
  oversized.write_bytes(b' '*(feature.MAX_BYTES+1))
  with pytest.raises(ValueError,match='too_large'):feature.read_project(tmp_path,'large')


def test_local_only_extractor_contract_with_full_service_names(tmp_path,monkeypatch):
  from tools.carrot_mapping.__main__ import extract
  class Event:
    def __init__(self,kind,time,body):self.kind=kind;self.logMonoTime=time;self.valid=True;setattr(self,kind,body)
    def which(self):return self.kind
  calibration=types.SimpleNamespace(calStatus='calibrated',to_dict=lambda:{'rpyCalib':[0,0,0]})
  lane=types.SimpleNamespace(x=[10.],y=[2.],z=[1.])
  model=types.SimpleNamespace(timestampEof=1_000_000_000,frameId=10,laneLines=[lane],laneLineProbs=[.9],laneLineStds=[.1])
  events=[Event('liveCalibration',1_000_000_000,calibration),Event('modelV2',1_000_000_000,model),Event('modelV2',4_000_000_000,model)]
  module=types.ModuleType('openpilot.tools.lib.logreader');module.LogReader=lambda *a,**k:iter(events)
  monkeypatch.setitem(sys.modules,module.__name__,module)
  path=tmp_path/'rlog';path.touch();out=tmp_path/'observations.jsonl'
  extract(types.SimpleNamespace(trip='t1',vehicle='v1',clock='boot1',rlog=str(path),output=out))
  rows=[json.loads(line) for line in out.read_text().splitlines()]
  assert rows[0]['timestamp_ns']=='1000000000' and rows[0]['calibration_valid']
  assert not rows[1]['calibration_valid']
  assert not Path(str(out)+'.partial').exists()
