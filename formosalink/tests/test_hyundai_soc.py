import ast
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from openpilot.sunnypilot.formosalink.hyundai_soc import SocTracker,profile,verify_aux_dbc

def frame(soc=72,voltage=12.6):
 return ((soc<<16)|(int(round((voltage-6)*1000))<<24)|(1<<47)).to_bytes(8,'little')

def tracker():
 t=SocTracker();t.configure(profile('hyundai','AUTO_MODEL',False,True));return t

def test_aux_12v_never_becomes_traction_soc():
 t=tracker();assert not t.configuration['traction_supported'];t.feed(0x549,0,frame(),10,10);assert t.snapshot(10)['aux_soc_percent'] is None
 t.feed(0x549,0,frame(),10.1,10.1);assert t.snapshot(10.1)['aux_soc_percent']==72;assert t.snapshot(10.1)['aux_battery_voltage']==12.6
 assert 'vehicle_soc_percent' not in t.snapshot(10.1)
 assert t.snapshot(13)['aux_soc_percent'] is None

@pytest.mark.parametrize('address,bus,data',[(0x542,0,frame()),(0x549,2,frame()),(0x549,0,b'\x01'),(0x549,0,bytes(8)),(0x549,0,b'\xff'*8),(0x549,0,frame(101)),(0x549,0,frame(72,20))])
def test_wrong_bus_length_sentinels_and_range_do_not_publish(address,bus,data):
 t=tracker()
 for at in [10,10.1]:t.feed(address,bus,data,at,at)
 assert t.snapshot(10.1)['aux_soc_percent'] is None

def test_zero_is_valid_but_duplicate_and_old_frames_are_not():
 t=tracker();t.feed(0x549,0,frame(0),10,10);t.feed(0x549,0,frame(0),10,10.1);assert t.snapshot(10.1)['aux_soc_percent'] is None
 t.feed(0x549,0,frame(0),10.2,10.2);assert t.snapshot(10.2)['aux_soc_percent']==0
 t.configure(profile('hyundai','OTHER_CAR',True,False));assert t.snapshot(10.2)['aux_soc_percent'] is None
 t.feed(0x549,0,frame(),11,11);assert t.snapshot(11)['aux_soc_percent'] is None

def test_decoder_is_gated_by_native_protocol_and_exact_dbc():
 assert not profile('toyota','x',False,True)['aux_supported'];assert not profile('hyundai','x',True,True)['aux_supported']
 signal=NS(start_bit=16,size=8,factor=1,offset=0,is_little_endian=True);voltage=NS(start_bit=24,size=14,factor=.001,offset=6,is_little_endian=True)
 db=NS(name_to_msg={'BAT11':NS(address=0x549,size=8,sigs={'BAT_SOC':signal,'BAT_SNSR_V':voltage})})
 assert verify_aux_dbc(db);signal.factor=.5;assert not verify_aux_dbc(db)

def test_adapter_has_no_can_transmitter_or_param_writes():
 tree=ast.parse(Path('openpilot/sunnypilot/formosalink/hyundai_soc.py').read_text(encoding='utf-8'))
 calls=[n.func.attr for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
 assert not {'PubMaster','put','put_bool','send','sendcan'}.intersection(calls)
