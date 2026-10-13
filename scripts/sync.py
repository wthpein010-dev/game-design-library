"""Bounded public metadata ingestion; never download article bodies or media to disk."""
import argparse
import hashlib
import html
import json
import re
import time
import urllib.request
import urllib.parse
import urllib.robotparser
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
UA = 'GameDesignLibrary/1.0 (+https://github.com/wthpein010-dev/game-design-library)'
MAX_BYTES = 5_000_000

def read_json(path, fallback):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else fallback

def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(path)

def canonical_url(url):
    p = urllib.parse.urlsplit(html.unescape(url.strip()))
    if p.scheme not in ('https', 'http') or not p.hostname or p.username or p.password:
        raise ValueError('Unsupported URL')
    args = [(k,v) for k,v in urllib.parse.parse_qsl(p.query,keep_blank_values=True)
            if not k.lower().startswith('utm_') and k.lower() not in ('spm_id_from','from','fbclid','gclid')]
    scheme='https' if p.hostname in ('www.designer-notes.com','gdkeys.com','gamedesignconcepts.wordpress.com') else p.scheme
    return urllib.parse.urlunsplit((scheme, p.netloc.lower(), p.path or '/', urllib.parse.urlencode(sorted(args)), ''))

def relevant(row, source):
    pattern=source.get('exclude_pattern')
    return not pattern or not re.search(pattern,row.get('title','')+' '+row['url'],re.I)

def resource_id(url):
    return 'r-' + hashlib.sha256(canonical_url(url).encode()).hexdigest()[:16]

class TextParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.hidden=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'): self.hidden+=1
    def handle_endtag(self,tag):
        if tag in ('script','style'): self.hidden=max(0,self.hidden-1)
    def handle_data(self,data):
        if not self.hidden:self.parts.append(data)

def plain(value, limit=280):
    p=TextParser();p.feed(value or '')
    return re.sub(r'\s+',' ',html.unescape(' '.join(p.parts))).strip()[:limit]

def category(title, fallback):
    text=title.lower()
    for name, words in [
        ('关卡与叙事',('level design','narrative','storytell','quest','关卡','叙事')),
        ('经济与商业',('econom','monetiz','pricing','business','经济','商业')),
        ('玩家与心理',('psycholog','motivation','accessib','player experience','心理')),
        ('数值与概率',('balanc','probabil','math','数值','概率')),
        ('制作与工具',('prototyp','production','team','tool','制作','工具'))]:
        if any(w in text for w in words):return name
    return fallback

def parse_feed(data, source):
    root=ET.fromstring(data); result=[]
    for item in root.findall('./channel/item'):
        url=item.findtext('link','').strip()
        if not url:continue
        url=canonical_url(url)
        title=plain(item.findtext('title',''),300)
        if not title:continue
        date=item.findtext('pubDate','')
        try:date=parsedate_to_datetime(date).isoformat()
        except (ValueError,TypeError):date=''
        result.append({'id':resource_id(url),'title':title,'url':url,'source_id':source['id'],
          'source':source['name'],'author':plain(item.findtext('{http://purl.org/dc/elements/1.1/}creator',''),100),
          'kind':'文章','category':category(title,source['category']),
          'language':source['language'],'summary':plain(item.findtext('description','')),
          'summary_type':'来源订阅摘要','published_at':date,'review':'自动索引',
          'tags':[plain(x.text,60) for x in item.findall('category') if x.text][:8]})
    return result

def merge_records(old, incoming, now):
    records={canonical_url(r['url']):dict(r) for r in old};changes=[]
    for row in incoming:
        row=dict(row);url=canonical_url(row['url']);row['url']=url
        previous=records.get(url)
        if previous:
            if previous.get('review')=='人工整理':continue
            row['id']=previous['id'];row['first_seen']=previous.get('first_seen',now)
            changed=any(previous.get(k)!=row.get(k) for k in ('title','summary','author'))
            row['updated_at']=now if changed else previous.get('updated_at',now)
            row['checked_at']=now
            records[url]={**previous,**row}
            if changed:changes.append({'id':row['id'],'action':'updated','at':now,'title':row['title']})
        else:
            row.update(first_seen=now,updated_at=now,checked_at=now)
            records[url]=row;changes.append({'id':row['id'],'action':'added','at':now,'title':row['title']})
    return list(records.values()),changes

class MetadataParser(HTMLParser):
    def __init__(self):super().__init__();self.meta={};self.title=[];self.in_title=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='title':self.in_title=True
        if tag=='meta':self.meta[a.get('property',a.get('name',''))]=a.get('content','')
    def handle_endtag(self,tag):
        if tag=='title':self.in_title=False
    def handle_data(self,data):
        if self.in_title:self.title.append(data)

class Client:
    def __init__(self, source):
        self.source=source;self.host=urllib.parse.urlsplit(source['url']).hostname
        self.last=0;self.robots=urllib.robotparser.RobotFileParser()
        robots_url=urllib.parse.urljoin(source['url'],'/robots.txt')
        data=self.fetch(robots_url,check=False)
        self.robots.parse(data.decode('utf-8','replace').splitlines())
    def fetch(self,url,check=True):
        url=canonical_url(url)
        if urllib.parse.urlsplit(url).hostname!=self.host:raise ValueError('Outside source host')
        if check and not self.robots.can_fetch(UA,url):raise ValueError('robots.txt disallows URL')
        time.sleep(max(0,1.2-(time.monotonic()-self.last)))
        # Redirect destinations must stay in this source, too.
        host=self.host
        class Redirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,req,fp,code,msg,headers,newurl):
                if urllib.parse.urlsplit(newurl).hostname!=host:raise ValueError('Redirect outside source host')
                return super().redirect_request(req,fp,code,msg,headers,newurl)
        opener=urllib.request.build_opener(Redirect())
        with opener.open(urllib.request.Request(url,headers={'User-Agent':UA}),timeout=25) as response:
            data=response.read(MAX_BYTES+1)
            if len(data)>MAX_BYTES:raise ValueError('Response too large')
        self.last=time.monotonic();return data

def sitemap_urls(client,url,depth=0):
    if depth>2:return []
    data=client.fetch(url);root=ET.fromstring(data);ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
    if root.tag.endswith('sitemapindex'):
        children=[x.text for x in root.findall('s:sitemap/s:loc',ns) if x.text]
        children=[u for u in children if not any(w in u for w in ('image-sitemap','video-sitemap','category','tag-sitemap','page-sitemap','author'))]
        result=[]
        for child in children[:8]:result+=sitemap_urls(client,child.replace('http://','https://',1),depth+1)
        return result
    return [canonical_url(x.text) for x in root.findall('s:url/s:loc',ns) if x.text]

def archive_record(client,url,source):
    p=MetadataParser();p.feed(client.fetch(url).decode('utf-8','replace'))
    title=plain(p.meta.get('og:title') or ''.join(p.title),300)
    if not title:raise ValueError('No public title')
    return {'id':resource_id(url),'title':title,'url':url,'source_id':source['id'],'source':source['name'],
      'author':plain(p.meta.get('author',source.get('author','')),100),'kind':'文章',
      'category':category(title,source['category']),'language':source['language'],
      'summary':plain(p.meta.get('description',p.meta.get('og:description',''))),
      'summary_type':'原页元数据摘要','published_at':p.meta.get('article:published_time',''),
      'review':'自动索引','tags':['历史资料']}

def sync(limit=8):
    now=datetime.now(timezone.utc).isoformat(timespec='seconds')
    sources=read_json(ROOT/'data/sources.json',[])
    records=read_json(ROOT/'data/resources.json',[])
    state=read_json(ROOT/'data/sync-state.json',{})
    all_changes=[];reports=[]
    for source in sources:
        if not source.get('enabled'):continue
        source_state=state.setdefault(source['id'],{'done':[],'retry':{}})
        report={'source_id':source['id'],'source':source['name'],'at':now,'new':0,'updated':0,'errors':[]}
        incoming=[]
        try:
            client=Client(source)
            try:
                incoming+=[r for r in parse_feed(client.fetch(source['feed']),source) if relevant(r,source)]
            except Exception as error:report['errors'].append('RSS: '+str(error)[:180])
            try:
                urls=sitemap_urls(client,source['sitemap'])
                known={canonical_url(r['url']) for r in records+incoming}
                todo=sorted(set(urls)-known-set(source_state['done']))
                todo=[u for u in todo if re.search(source.get('archive_pattern','.'),u) and relevant({'url':u},source)]
                # Deferred failures do not starve the queue; retry at most once per day.
                eligible=[u for u in todo if source_state['retry'].get(u,{}).get('at','')[:10]!=now[:10]]
                eligible.sort(key=lambda u:(source_state['retry'].get(u,{}).get('count',0),u))
                for url in eligible[:limit]:
                    try:
                        record=archive_record(client,url,source)
                        if relevant(record,source):incoming.append(record)
                        source_state['done'].append(url)
                        source_state['retry'].pop(url,None)
                    except Exception as error:
                        retry=source_state['retry'].get(url,{'count':0})
                        source_state['retry'][url]={'count':retry['count']+1,'at':now,'error':str(error)[:180]}
                        report['errors'].append(url+': '+str(error)[:120])
                report['archive_remaining']=max(0,len(todo)-sum(1 for u in eligible[:limit] if u in source_state['done']))
            except Exception as error:report['errors'].append('Archive: '+str(error)[:180])
        except Exception as error:report['errors'].append('Source: '+str(error)[:180])
        records,changes=merge_records(records,incoming,now)
        report['new']=sum(c['action']=='added' for c in changes)
        report['updated']=sum(c['action']=='updated' for c in changes)
        report['status']='partial' if report['errors'] and incoming else 'failed' if report['errors'] else 'ok'
        report['fetched']=len(incoming)
        all_changes+=changes;reports.append(report)
        print(json.dumps(report,ensure_ascii=True))
    save_json(ROOT/'data/resources.json',records)
    save_json(ROOT/'data/sync-state.json',state)
    history=read_json(ROOT/'data/updates.json',[])
    run={'at':now,'sources':reports,'changes':all_changes}
    save_json(ROOT/'data/updates.json',([run]+history)[:90])
    # Persist evidence even if every source failed; the workflow subsequently reports failure.
    return bool(reports) and not all(r['status']=='failed' for r in reports)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int,default=8)
    args=parser.parse_args()
    raise SystemExit(0 if sync(max(0,min(args.limit,30))) else 1)
