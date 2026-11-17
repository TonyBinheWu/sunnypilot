import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const code=readFileSync(new URL('../js/realtime/compact_connection.js',import.meta.url),'utf8');
function fixture(){
 let time=0,id=0;const timers=new Map(),listeners=new Map(),lost=[],sent=[];
 const ws={readyState:1,send:data=>sent.push(data),addEventListener:(n,f)=>listeners.set(n,f),removeEventListener:n=>listeners.delete(n)};
 const window={performance:{now:()=>time},setTimeout:(fn,ms)=>{timers.set(++id,{fn,at:time+ms});return id;},clearTimeout:n=>timers.delete(n)};
 vm.runInNewContext(code,{window,performance:window.performance});
 const guard=window.CarrotCompactConnection.watch(ws,reason=>lost.push(reason));
 return {ws,guard,timers,lost,sent,pong(){listeners.get('message')?.({data:'{"type":"pong"}'});},run(ms){const end=time+ms;while(time<end){time+=Math.min(1000,end-time);for(const [id,t] of [...timers])if(t.at<=time){timers.delete(id);t.fn();}}}};
}
test('six hours of quiet parked heartbeats keep one bounded timer and send only fixed pings',()=>{
 const h=fixture();for(let i=0;i<6*3600;i++){if(i%5===0)h.pong();h.run(1000);assert.equal(h.timers.size,1);}
 assert.equal(h.lost.length,0);assert.equal(h.sent.length,4320);assert.deepEqual([...new Set(h.sent)],['{"type":"ping"}']);
 h.guard.stop();assert.equal(h.timers.size,0);
});
test('an open but silent socket times out without needing a close event',()=>{
 const h=fixture();h.run(11999);assert.equal(h.lost.length,0);h.run(1001);assert.deepEqual(h.lost,['heartbeat-timeout']);assert.equal(h.timers.size,0);
});
test('hung connection establishment is bounded and cancellation cannot trigger recovery',()=>{
 const h=fixture();h.ws.readyState=0;h.run(8000);assert.deepEqual(h.lost,['connect-timeout']);
 const stopped=fixture();stopped.guard.stop();stopped.run(60000);assert.equal(stopped.lost.length,0);assert.equal(stopped.sent.length,0);
});
test('actual accepted data can prove liveness against older servers without application pong',()=>{
 const h=fixture();for(let i=0;i<100;i++){h.guard.received();h.run(1000);}assert.equal(h.lost.length,0);
 h.ws.send=()=>{throw Error('offline');};h.run(6000);assert.deepEqual(h.lost,['send-failed']);
});
