import asyncio
import json
from types import SimpleNamespace
from openpilot.selfdrive.carrot.server.features import parking


def test_only_closed_local_osm_ways_become_map_markers():
  way={'type':'way','id':1,'tags':{'amenity':'parking'},'geometry':[{'lat':25.,'lon':121.},{'lat':25.,'lon':121.001},{'lat':25.001,'lon':121.001},{'lat':25.,'lon':121.}]}
  assert len(parking.parse_areas({'elements':[way]},25.,121.))==1
  for changed in [{**way,'type':'node'},{**way,'geometry':way['geometry'][:-1]},{**way,'tags':{'amenity':'cafe'}}]:
    assert parking.parse_areas({'elements':[changed]},25.,121.)==[]
  assert parking.parse_areas({'elements':[way]},20.,120.)==[]


def test_location_lookup_is_off_without_explicit_preference(monkeypatch):
  monkeypatch.setattr(parking,'read_web_settings',lambda:{'vision_parking_map':False})
  response=asyncio.run(parking.context(SimpleNamespace(app={})))
  assert json.loads(response.text)=={'status':'off','areas':[]}


def test_lookup_uses_vehicle_position_fixed_host_and_shared_cache(tmp_path,monkeypatch):
  monkeypatch.setattr(parking,'read_web_settings',lambda:{'vision_parking_map':True})
  view=tmp_path/'view.json';demand=tmp_path/'demand'
  monkeypatch.setattr(parking,'VIEW_PATH',view);monkeypatch.setattr(parking,'WEB_DEMAND_PATH',demand)
  view.write_text(json.dumps({'position':{'lat':25.,'lng':121.},'generated_at':parking.time.time()}))
  calls=[]
  class Content:
    async def iter_chunked(self,size):yield b'{"elements":[]}'
  class Response:
    status=200
    content=Content()
    async def __aenter__(self):return self
    async def __aexit__(self,*args):pass
  class HTTP:
    def post(self,url,**kwargs):calls.append((url,kwargs));return Response()
  async def run():
    req=SimpleNamespace(app={parking.KEY:parking.ParkingCache(),'http':HTTP()})
    a=await parking.context(req);b=await parking.context(req)
    assert json.loads(a.text)['status']==json.loads(b.text)['status']=='ready'
    assert len(calls)==1 and calls[0][0]=='https://overpass-api.de/api/interpreter'
    assert '25.00000,121.00000' in calls[0][1]['data']['data']
    view.write_text(json.dumps({'position':{'lat':25.,'lng':121.},'generated_at':parking.time.time()+30}))
    assert json.loads((await parking.context(req)).text)['status']=='no_position'
    assert len(calls)==1
  asyncio.run(run())
