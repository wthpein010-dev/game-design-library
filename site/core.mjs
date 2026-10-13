export function filterResources(rows, filters={}, study={}) {
  const q=(filters.q||'').trim().toLocaleLowerCase();
  return rows.filter(r=>(!q||[r.title,r.summary,r.author,r.source,...(r.tags||[])].join(' ').toLocaleLowerCase().includes(q))
    &&(!filters.category||r.category===filters.category)&&(!filters.kind||r.kind===filters.kind)
    &&(!filters.language||r.language===filters.language)&&(!filters.saved||study[r.id]?.saved)
    &&(!filters.status||study[r.id]?.status===filters.status))
    .sort((a,b)=>filters.sort==='published'?(b.published_at||'').localeCompare(a.published_at||''):
      filters.sort==='recent'?(b.first_seen||'').localeCompare(a.first_seen||''):
      ({课程:0,视频:1,文章:2,'资源导航':3}[a.kind]-{课程:0,视频:1,文章:2,'资源导航':3}[b.kind])||a.id.localeCompare(b.id,undefined,{numeric:true}));
}
export function parseBackup(text) {
  if(text.length>5_000_000)throw new Error('备份超过5MB，请检查文件。');
  const data=JSON.parse(text);
  if(data.schema!==1||!data.records||Array.isArray(data.records)||typeof data.records!=='object')throw new Error('请选择本网站导出的学习记录JSON。');
  const clean=Object.create(null);
  for(const [id,r] of Object.entries(data.records)){
    if(!/^[A-Za-z0-9_-]{1,80}$/.test(id)||['__proto__','prototype','constructor'].includes(id)||!r||typeof r!=='object')throw new Error('备份中含有无效记录。');
    if(!['todo','reading','done',undefined].includes(r.status)||typeof r.note!=='string'||r.note.length>20000||typeof r.saved!=='boolean')throw new Error('学习记录字段不符合格式。');
    clean[id]={note:r.note,status:r.status||'todo',saved:r.saved};
  }
  return clean;
}
export function mergeStudy(current,incoming){return {...incoming,...current};}
export function escapeHtml(text){return String(text??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
