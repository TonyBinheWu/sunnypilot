import test from 'node:test';
import assert from 'node:assert/strict';
import {sampleProject,validateProject,visibleCells,projectPoints} from '../src/features/lane_mapping/model.js';
import {messages} from '../src/features/lane_mapping/messages.js';

test('synthetic provenance and FRD-derived ENU display, filtering',()=>{
  const p=sampleProject();assert.equal(p.ground_truth,false);assert.equal(p.control_eligible,false);
  assert.equal(visibleCells(p,new Set(['demo-a']),2).length,0);
  assert.equal(visibleCells(p,new Set(['demo-a','demo-b']),2).length,p.cells.length);
  const cells=[{xyz:[-2,0,0]},{xyz:[2,0,0]},{xyz:[0,5,0]}];
  const projected=projectPoints(cells,{width:500,height:500});
  assert.ok(projected[0].x<projected[1].x);assert.ok(projected[2].y<projected[0].y);
});
test('strict bounded data excludes unknown trips, duplicates, truth claims and non-finite geometry',()=>{
  for(const mutate of [p=>{p.ground_truth=true;},p=>{p.pose_verified=true;},p=>{p.cells[0].xyz[0]=Infinity;},
    p=>{p.cells[0].trip_ids=['unknown'];},p=>{p.cells.push(p.cells[0]);},p=>{p.revision='bad';},
    p=>{p.frame.axes='FRD';},p=>{p.trips['<script>']={};}]){
    const p=sampleProject();mutate(p);assert.throws(()=>validateProject(p));
  }
});
test('projection stays finite at bounded full size; local labels are complete',()=>{
  const p=sampleProject(),cells=Array.from({length:25000},(_,i)=>({...p.cells[i%p.cells.length]}));
  const points=projectPoints(cells,{width:390,height:420,pitch:Math.PI/4,yaw:Math.PI/3});
  assert.equal(points.length,25000);assert.ok(points.every(p=>Number.isFinite(p.x)&&Number.isFinite(p.y)));
  assert.deepEqual(Object.keys(messages('zh-TW')).sort(),Object.keys(messages('en')).sort());
});
