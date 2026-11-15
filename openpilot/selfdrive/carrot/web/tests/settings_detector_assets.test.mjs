import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import test from 'node:test';
test('the bundled local inference artifacts match their pinned hashes and native binary formats',async()=>{
  const root=new URL('../vendor/bev-detector/',import.meta.url);
  const manifest=JSON.parse(await readFile(new URL('manifest.json',root),'utf8'));
  assert.equal(manifest.version,'0.10.21');
  assert.equal(manifest.files.length,6);
  for(const item of manifest.files){
    assert.ok(!item.path.includes('..'));
    const bytes=await readFile(new URL(item.path,root));
    assert.equal(bytes.length,item.bytes,item.path);
    assert.equal(createHash('sha256').update(bytes).digest('hex'),item.sha256,item.path);
    if(item.path.endsWith('.wasm'))assert.deepEqual([...bytes.subarray(0,4)],[0,97,115,109]);
    if(item.path.endsWith('.tflite'))assert.equal(bytes.subarray(4,8).toString(),'TFL3');
  }
});
