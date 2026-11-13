import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const code=readFileSync(new URL('../js/realtime/web_sound.js',import.meta.url),'utf8');
function browser(enabled=true){
  const gains=[],sockets=[];
  class AudioContext {
    state='running';currentTime=0;destination={};
    createBufferSource(){return {connect(){},start(){},stop(){},loop:false};}
    createGain(){const node={gain:{value:0,setValueAtTime(value){this.value=value;}},connect(){}};gains.push(node);return node;}
    async decodeAudioData(){return {};}
  }
  class WebSocket {static CLOSED=3;static OPEN=1;constructor(){sockets.push(this);this.readyState=1;}close(){}}
  const scope={AudioContext,WebSocket,location:{host:'fixture.test',protocol:'https:'},
    document:{getElementById:()=>null,addEventListener(){}},
    localStorage:{getItem:key=>key.endsWith('enabled.v1')&&enabled?'1':null,setItem(){}},
    setTimeout(){return 1;},clearTimeout(){},addEventListener(){},
    fetch:async url=>url==='/api/web_settings'?{ok:false}:url.startsWith('/api/params_bulk')
      ?{ok:true,json:async()=>({values:{SoundLanguageVolume:200}})}:{ok:true,arrayBuffer:async()=>new ArrayBuffer(0)},
  };
  scope.window=scope;
  vm.runInNewContext(code,scope);
  return {sound:scope.CarrotWebSound,gains,sockets,emit:state=>sockets[0].onmessage({data:JSON.stringify({type:'soundState',alert:0,countdown:100,...state})})};
}

test('browser voice boost reaches audio gain while Web volume and warning tones stay independent',async()=>{
  const b=browser();b.sound.setVolume(.5);
  b.emit({voiceVolume:2,volume:.1,engageVolume:.1});
  await b.sound.preview(9);
  assert.equal(b.gains.at(-1).gain.value,1);
  b.emit({voiceVolume:3});
  assert.equal(b.gains.at(-1).gain.value,1.5);
  b.sound.setVolume(.2);
  assert.ok(Math.abs(b.gains.at(-1).gain.value-.6)<1e-10);
  await b.sound.preview(5);
  assert.equal(b.gains.at(-1).gain.value,.2);
  for(const alert of [21,24,33]){await b.sound.preview(alert);assert.ok(Math.abs(b.gains.at(-1).gain.value-.6)<1e-10);}
  b.emit({voiceVolume:999});assert.equal(b.sound.status().voiceVolume,3);
  b.emit({voiceVolume:'bad'});assert.equal(b.sound.status().voiceVolume,1);
  b.emit({});await b.sound.preview(9);assert.equal(b.gains.at(-1).gain.value,.2);
});

test('language and volume auditions use fresh device gain without enabling live web audio',async()=>{
  const b=browser(false);
  b.sound.setVolume(.5);
  await b.sound.previewLanguage('sounds_chs');
  assert.equal(b.sound.isEnabled(),false);
  assert.equal(b.sockets.length,0);
  assert.equal(b.gains.at(-1).gain.value,1);
  await assert.rejects(b.sound.previewLanguage('invalid'));
});
