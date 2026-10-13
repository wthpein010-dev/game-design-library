import test from 'node:test';
import assert from 'node:assert/strict';
import {filterResources,parseBackup,mergeStudy} from '../site/core.mjs';
test('search filters combine and keep original records',()=>{
 const rows=[{id:'1',title:'核心循环',summary:'反馈',kind:'课程',category:'玩法与系统',language:'zh'},{id:'2',title:'Balance',kind:'文章',category:'数值与概率',language:'en'}];
 assert.equal(filterResources(rows,{q:'反馈',kind:'课程'},{}).length,1);
 assert.equal(filterResources(rows,{q:'核心',language:'en'},{}).length,0);
});
test('invalid backup cannot inject URLs or replace state',()=>{
 assert.throws(()=>parseBackup('{"schema":1,"records":{"x":{"status":"mastered"}}}'));
 assert.throws(()=>parseBackup('{"schema":1,"records":{"__proto__":{"note":"x"}}}'));
});
test('merge preserves existing notes and imports new records',()=>{
 const incoming=parseBackup(JSON.stringify({schema:1,records:{a:{note:'old',status:'reading',saved:true},b:{note:'new',status:'todo',saved:false}}}));
 assert.equal(mergeStudy({a:{note:'current'}},incoming).a.note,'current');
 assert.equal(mergeStudy({},incoming).b.note,'new');
});
