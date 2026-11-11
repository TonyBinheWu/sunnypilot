import time
from types import SimpleNamespace as NS
import pytest
from openpilot.sunnypilot.formosalink.device_health import collect_health
from openpilot.sunnypilot.formosalink.navigation import destination,encode
from formosalink.tests.test_settings import provider,command

class Sources(dict):
 def __init__(self,**values):
  super().__init__(values);self.seen={k:True for k in values};self.valid={k:True for k in values};self.logMonoTime={k:time.monotonic()*1e9 for k in values}

def sources(present=False):
 return Sources(deviceState=NS(deviceType='mici',cpuTempC=[44,45],gpuTempC=[43],pmicTempC=[37],modemTempC=[],memoryTempC=42,dspTempC=0,intakeTempC=30,exhaustTempC=38,gnssTempC=35,bottomSocTempC=46,maxTempC=46,thermalZones=[NS(name='cpu0',temp=44)],chestnutPresent=present),chestnutGpuState=NS(tempC=65,memoryTempC=62),carState=NS(canValid=True,fuelGauge=.73))

def test_hardware_and_vehicle_battery_are_distinct():
 sm=sources();health=collect_health(sm,'hyundai');assert health['vehicle_soc_percent'] is None and health['soc_status']=='unsupported';assert health['bottom_soc_temp_c']==46
 assert health['cpu_temperatures']==[44,45] and health['egpu_status']=='not_installed';assert health['dsp_temp_c'] is None
 assert collect_health(sm,'body')['vehicle_soc_percent']==73
 sm['carState'].fuelGauge=0;assert collect_health(sm,'body')['vehicle_soc_percent']==0
 sm.logMonoTime['carState']=0;assert collect_health(sm,'body')['vehicle_soc_percent'] is None

def test_egpu_installation_and_temperature_freshness():
 sm=sources(True);health=collect_health(sm,'hyundai');assert health['egpu_status']=='available' and health['egpu_temp_c']==65
 sm.valid['chestnutGpuState']=False;health=collect_health(sm,'hyundai');assert health['egpu_status']=='installed_unavailable' and health['egpu_temp_c'] is None
 sm.valid['deviceState']=False;health=collect_health(sm,'hyundai');assert health['egpu_status']=='unknown' and not health['health_valid']

@pytest.mark.parametrize('value',['{}','{"latitude":999,"longitude":0,"place_name":"a"}','{"latitude":true,"longitude":0,"place_name":"a"}','{"latitude":1,"longitude":2,"place_name":"a","shell":"run"}'])
def test_navigation_codec_rejects_invalid_fields(value):
 with pytest.raises(ValueError):destination(value)

def test_navigation_uses_typed_native_json_and_offroad_guard():
 source,params,guard=provider();source.navigation=True;params.values.update(NavDestination=None,NavigationEnabled=True)
 value=encode({'latitude':25.03,'longitude':121.56,'place_name':'Taipei'})
 cmd=command(source.capture(),'NavDestination',value)
 assert source.apply(cmd,cmd['device_id'],time.monotonic()+5)['status']=='applied'
 assert params.values['NavDestination']==destination(value)
 cmd=command(source.capture(),'NavDestination',value);guard.parked=False
 assert source.apply(cmd,cmd['device_id'],time.monotonic()+5)['reason']=='offroad_required'
 guard.parked=True;params.values['NavigationEnabled']=False;cmd=command(source.capture(),'NavDestination',value)
 assert source.apply(cmd,cmd['device_id'],time.monotonic()+5)['reason']=='setting_unavailable'
from formosalink.tests.test_platform import client,pair,ORIGIN
from openpilot.sunnypilot.formosalink.protocol import sign

def test_signed_navigation_and_owner_isolated_health_summary(client):
 device,private,_=pair(client);source,params,_=provider();source.navigation=True;params.values.update(NavDestination=None,NavigationEnabled=True)
 source.info=lambda:{'health_valid':True,'vehicle_soc_percent':0,'soc_status':'available','egpu_status':'not_installed'}
 def sync(state):
  response=client.post('/api/v1/agent/sync',json=sign(private,device,'sync',state));assert response.status_code==200;return response.json()
 snapshot=source.capture();sync(snapshot)
 row=client.get('/api/v1/devices').json()['devices'][0];assert row['health']['vehicle_soc_percent']==0 and row['health_fresh'];assert 'catalog' not in row['health']
 value=encode({'latitude':25.03,'longitude':121.56,'place_name':'test'})
 response=client.post('/api/v1/devices/'+device+'/settings',json={'key':'NavDestination','value':value,'session':snapshot['session'],'expected_revision':snapshot['revision']},headers={'Origin':ORIGIN});assert response.status_code==200
 cmd=sync(source.capture())['command'];receipt=source.apply(cmd,device,time.monotonic()+5);assert receipt['status']=='applied';snapshot=source.capture();snapshot['receipts']=[receipt];sync(snapshot)
 assert params.values['NavDestination']['latitude']==25.03
 store=client.app.state.store;other=store.github_user('98234','health-other');client.cookies.set('formosalink_session',store.session(other),domain='formosapilot.dinglu-t.com',path='/api')
 assert client.get('/api/v1/devices').json()['devices']==[]
 assert client.get('/api/v1/devices/'+device+'/settings').status_code==404

def test_monitoring_only_does_not_export_native_destination():
 source,params,_=provider();source.navigation=True;params.values.update(NavDestination={'latitude':25,'longitude':121,'place_name':'private'},NavigationEnabled=True,FormosaLinkRemoteSettings=False)
 state=source.capture();assert state['values']['NavDestination']==''
 assert not next(x for x in state['catalog'] if x['key']=='NavDestination')['enabled']
