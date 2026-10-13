import json
import re
import sqlite3
import hashlib
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

ROOT=Path(__file__).resolve().parents[1]
BASE='https://wthpein010-dev.github.io/ai-application-hub/projects/game-design-textbook/'

class SafeHTML(HTMLParser):
    allowed={'p','b','strong','em','i','u','ul','ol','li','table','thead','tbody','tr','td','th','code','pre','blockquote','br','sub','sup','h3','h4','a','img'}
    def __init__(self):super().__init__();self.parts=[];self.hidden=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style','iframe'):self.hidden+=1;return
        if tag not in self.allowed or self.hidden:return
        safe=[]
        for key,val in attrs:
            if key in ('href','src'):
                val=urljoin(BASE,val or '')
                if urlsplit(val).scheme!='https':continue
            elif key not in ('alt','title','colspan','rowspan'):continue
            safe.append(f' {key}="{escape(val or "",quote=True)}"')
        self.parts.append('<'+tag+''.join(safe)+'>')
    def handle_endtag(self,tag):
        if tag in ('script','style','iframe'):self.hidden=max(0,self.hidden-1);return
        if tag in self.allowed and not self.hidden:self.parts.append('</'+tag+'>')
    def handle_data(self,data):
        if not self.hidden:self.parts.append(escape(data))

def sanitize(value):
    p=SafeHTML();p.feed(value);return ''.join(p.parts)

def build():
    site=ROOT/'site/data';site.mkdir(parents=True,exist_ok=True)
    load=lambda name:json.loads((ROOT/'data'/name).read_text(encoding='utf-8'))
    resources=load('resources.json');sources=load('sources.json');lessons=load('lessons.json');topics=load('topics.json')
    updates=load('updates.json') if (ROOT/'data/updates.json').exists() else []
    for lesson in lessons:
        for section in lesson['sections']:section['html']=sanitize(section['html'])
    catalog={'resources':resources,'sources':sources,'topics':topics,'updates':updates[:30],
             'lesson_count':len(lessons),'video_count':sum(r['kind']=='视频' for r in resources)}
    (site/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    (site/'lessons.json').write_text(json.dumps(lessons,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    path=site/'knowledge.sqlite';tmp=path.with_suffix('.tmp')
    if tmp.exists():tmp.unlink()
    db=sqlite3.connect(tmp)
    db.executescript('''
      CREATE TABLE resources(id TEXT PRIMARY KEY,title TEXT NOT NULL,url TEXT UNIQUE NOT NULL,kind TEXT,category TEXT,source_id TEXT,author TEXT,language TEXT,summary TEXT,published_at TEXT,first_seen TEXT,updated_at TEXT,checked_at TEXT,review TEXT,payload TEXT NOT NULL);
      CREATE INDEX resource_category ON resources(category,kind);
      CREATE TABLE sources(id TEXT PRIMARY KEY,name TEXT,url TEXT,enabled INTEGER,payload TEXT);
      CREATE TABLE lessons(id TEXT PRIMARY KEY,title TEXT,payload TEXT);
      CREATE TABLE sections(lesson_id TEXT REFERENCES lessons(id),position INTEGER,title TEXT,html TEXT,PRIMARY KEY(lesson_id,position));
      CREATE TABLE sync_runs(at TEXT PRIMARY KEY,payload TEXT);
      CREATE TABLE revisions(resource_id TEXT,at TEXT,action TEXT,title TEXT);
      PRAGMA user_version=1;
    ''')
    for r in resources:
        fields=['id','title','url','kind','category','source_id','author','language','summary','published_at','first_seen','updated_at','checked_at','review']
        db.execute('INSERT INTO resources VALUES('+','.join('?' for _ in range(15))+')',[r.get(k,'') for k in fields]+[json.dumps(r,ensure_ascii=False)])
    for s in sources:db.execute('INSERT INTO sources VALUES(?,?,?,?,?)',(s['id'],s['name'],s['url'],int(s['enabled']),json.dumps(s,ensure_ascii=False)))
    for l in lessons:
        db.execute('INSERT INTO lessons VALUES(?,?,?)',(l['id'],l['title'],json.dumps(l,ensure_ascii=False)))
        for i,s in enumerate(l['sections']):db.execute('INSERT INTO sections VALUES(?,?,?,?)',(l['id'],i,s['title'],s['html']))
    for u in updates:
        db.execute('INSERT INTO sync_runs VALUES(?,?)',(u['at'],json.dumps(u,ensure_ascii=False)))
        for c in u['changes']:db.execute('INSERT INTO revisions VALUES(?,?,?,?)',(c['id'],c['at'],c['action'],c['title']))
    db.commit();assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok';db.close();tmp.replace(path)
    text=(ROOT/'DESIGN.md').read_text(encoding='utf-8')
    colors=re.findall(r"^  ([a-z]+): '(#[0-9a-f]{6})'",text,re.M)
    (ROOT/'site/tokens.css').write_text(':root{'+''.join(f'--{k}:{v};' for k,v in colors)+'}\n',encoding='utf-8')
    manifest={'schema':1,'resources':len(resources),'lessons':len(lessons),'videos':catalog['video_count'],
              'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (site/'catalog.json',site/'lessons.json',path)}}
    (site/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps(manifest))

if __name__=='__main__':build()
