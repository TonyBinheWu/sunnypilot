import math

import pytest

from openpilot.selfdrive.ui.onroad.scene_motion import SceneMotion
from openpilot.selfdrive.ui.onroad.scene_junction import junction_arms


@pytest.mark.parametrize('speed,right,angle', [(8,0,0),(-6,0,math.pi),(0,4,math.pi/2),(0,-4,-math.pi/2)])
def test_world_motion_compensates_ego(speed,right,angle):
  tracker = SceneMotion()
  for i in range(6):
    kind, d, y, h = tracker.update([('car',30+(speed-5)*.25*i,right*.25*i)],i*.25,(5,0))[0]
    if i < 3:
      assert h is None
  assert abs(abs(h)-math.pi) < 1e-6 if angle==math.pi else h == pytest.approx(angle)


def test_static_object_during_turn_and_loss_of_pose():
  tracker = SceneMotion()
  for i in range(7):
    t = i * .25
    yaw, speed, rate = .2*t,4,.2
    df,dr = math.sin(yaw)*speed/rate,(1-math.cos(yaw))*speed/rate
    f,r = 35-df,2-dr
    obs = ('truck',math.cos(yaw)*f+math.sin(yaw)*r,-math.sin(yaw)*f+math.cos(yaw)*r)
    assert tracker.update([obs],t,(speed,rate))[0][3] is None
  assert tracker.update([obs],t+1,None)[0][3] is None


def test_crossing_tracks_ambiguous_and_duplicate_frames_have_no_heading():
  t=SceneMotion()
  for i in range(5):
    t.update([('car',20,-4+i),('car',20,4-i)],.25*i,(0,0))
  for frame in (1.,1.25):
    assert all(row[3] is None for row in t.update([('car',20,0)],frame,(0,0)))


def test_map_junction_follows_real_branches_and_ignores_visual_crossings():
  n=(0.,20.)
  segments=[((0.,0.),n),(n,(0.,28.)),((0.,28.),(4.,48.)),(n,(15.,21.)),(n,(-16.,20.))]
  arms = junction_arms(segments)
  assert len(arms)==4 and any((4.,48.) in line for line in arms)
  assert junction_arms([((0,0),(0,48)),((-16,20),(16,20))]) == []


def test_camera_and_map_provenance_expire_together(tmp_path, monkeypatch):
  import json
  from openpilot.selfdrive.ui.onroad import scene_objects as scene
  path = tmp_path/'observations'
  monkeypatch.setattr(scene,'PACKET',path)
  path.write_text(json.dumps({'eof':10**9,'objects':[['car',12,2,-1.5]],'junction':[[(0,10),(5,10)]],'unplaced':{'person':2}}))
  assert scene.read_scene(1.2) == ((('car',12,2,-1.5),),(((0,10),(5,10)),),(('person',2),))
  assert scene.read_scene(1.7) == ((),(),())
