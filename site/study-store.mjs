import {parseBackup,mergeStudy} from './core.mjs';
export const STUDY_KEY='game-design-library.study.v1';
export function readStudy(storage){const raw=storage.getItem(STUDY_KEY);return raw?parseBackup(raw):{};}
function write(storage,records){
  const raw=JSON.stringify({schema:1,records});
  parseBackup(raw);
  storage.setItem(STUDY_KEY,raw);
  return records;
}
export function applyStudyPatch(storage,id,patch){
  const current=readStudy(storage);
  return write(storage,{...current,[id]:{note:'',saved:false,status:'todo',...current[id],...patch}});
}
export function importStudy(storage,incoming){return write(storage,mergeStudy(readStudy(storage),incoming));}
