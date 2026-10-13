import test from 'node:test';
import assert from 'node:assert/strict';
import {applyStudyPatch,importStudy} from '../site/study-store.mjs';
const key='game-design-library.study.v1';
function storage(){const d=new Map();return {getItem:k=>d.get(k)||null,setItem:(k,v)=>d.set(k,v)};}
test('a stale page patches latest records, not its old snapshot',()=>{
 const s=storage();applyStudyPatch(s,'L01',{note:'A original'});applyStudyPatch(s,'L02',{saved:true});
 let records=JSON.parse(s.getItem(key)).records;
 assert.equal(records.L01.note,'A original');assert.equal(records.L02.saved,true);
 applyStudyPatch(s,'L01',{status:'reading'});assert.equal(JSON.parse(s.getItem(key)).records.L01.note,'A original');
});
test('invalid existing storage is never overwritten',()=>{
 const s=storage(),raw='{"schema":1,"records":{"L01":{"note":"recover me","status":"old"}}}';s.setItem(key,raw);
 assert.throws(()=>applyStudyPatch(s,'L02',{saved:true}));assert.equal(s.getItem(key),raw);
 assert.throws(()=>importStudy(s,{L02:{note:'new',saved:true,status:'todo'}}));assert.equal(s.getItem(key),raw);
});
test('import merges against latest persisted data',()=>{
 const s=storage();applyStudyPatch(s,'L01',{note:'newest'});
 importStudy(s,{L01:{note:'stale',saved:true,status:'done'},L02:{note:'import',saved:true,status:'todo'}});
 const records=JSON.parse(s.getItem(key)).records;assert.equal(records.L01.note,'newest');assert.equal(records.L02.note,'import');
});
