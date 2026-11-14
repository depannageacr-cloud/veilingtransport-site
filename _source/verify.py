from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,re,xml.etree.ElementTree as ET
from collections import Counter,deque
from content import PAGES

R=Path(__file__).resolve().parent.parent;BASE='https://www.veilingtransport.be'
class Doc(HTMLParser):
 def __init__(self,text):
  super().__init__(convert_charrefs=True);self.ids=[];self.refs=[];self.canonical=[];self.title=[];self.h1=0;self.description=[];self.robots=[];self.skip=False;self.inTitle=False;self.words=[];self.feed(text)
 def handle_starttag(self,t,ats):
  a=dict(ats)
  if a.get('id'):self.ids.append(a['id'])
  if t=='h1':self.h1+=1
  if t=='title':self.inTitle=True
  if t in ['script','style']:self.skip=True
  if t=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href'))
  if t=='meta' and a.get('name')=='description':self.description.append(a.get('content'))
  if t=='meta' and a.get('name')=='robots':self.robots.append(a.get('content'))
  for k in ['href','src']:
   if k in a:self.refs.append(a[k])
  if t=='img' and 'alt' not in a:raise AssertionError('Image without alt')
 def handle_endtag(self,t):
  if t=='title':self.inTitle=False
  if t in ['script','style']:self.skip=False
 def handle_data(self,s):
  if self.inTitle:self.title.append(s)
  if not self.skip:self.words.append(s)

files=[R/'index.html']+[R/p['slug']/'index.html' for p in PAGES]
docs={p:Doc(p.read_text()) for p in files};errors=[];graph={p:set() for p in files}
titles=[];descs=[]
for p,d in docs.items():
 rel=p.relative_to(R).as_posix();expected=BASE+'/'+rel.removesuffix('index.html')
 if len(d.title)!=1:errors.append((rel,'title count',len(d.title)))
 if d.h1!=1:errors.append((rel,'h1 count',d.h1))
 if d.canonical!=[expected]:errors.append((rel,'canonical',d.canonical))
 if len(d.description)!=1 or not d.description[0]:errors.append((rel,'description'))
 if any('noindex' in x for x in d.robots):errors.append((rel,'noindex'))
 if len(d.ids)!=len(set(d.ids)):errors.append((rel,'duplicate ids',[x for x,c in Counter(d.ids).items() if c>1]))
 titles.append(''.join(d.title));descs.extend(d.description)
 for block in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',p.read_text(),re.S):json.loads(block)
 for ref in d.refs:
  u=urlsplit(ref)
  if u.scheme and u.scheme not in ['https','http']:continue
  if u.netloc and u.netloc!='www.veilingtransport.be':continue
  path=unquote(u.path)
  target=(R/path.lstrip('/')) if path.startswith('/') else ((p.parent/path) if path else p)
  if target.is_dir():target/='index.html'
  if not target.exists():errors.append((rel,'missing target',ref));continue
  if target in docs:graph[p].add(target)
  if u.fragment and target in docs and unquote(u.fragment) not in docs[target].ids:errors.append((rel,'missing anchor',ref))
assert len(set(titles))==41,'Duplicate titles'
assert len(set(descs))==41,'Duplicate descriptions'
xml=ET.parse(R/'sitemap.xml');locs=[x.text for x in xml.findall('.//{*}loc')]
assert len(locs)==len(set(locs))==41
assert set(locs)=={BASE+'/'+p.relative_to(R).as_posix().removesuffix('index.html') for p in files}
seen={R/'index.html'};q=deque(seen)
while q:
 for x in graph[q.popleft()]:
  if x not in seen:seen.add(x);q.append(x)
assert len(seen)==41,'Orphan pages'
assert all(len(graph[p])>=5 for p in files[1:]),'Insufficient internal linking'
assert not re.search(r'data:image/\w+;base64', (R/'index.html').read_text())
assert 'Sitemap: '+BASE+'/sitemap.xml' in (R/'robots.txt').read_text()
assert len(json.loads((R/'ai-info.json').read_text())['pages'])==40
summary={'new_pages':40,'indexable_pages':41,'sitemap_urls':len(locs),'reachable_from_home':len(seen),'minimum_internal_page_links':min(len(graph[p]) for p in files[1:]),'minimum_visible_word_count':min(len(' '.join(d.words).split()) for d in list(docs.values())[1:]),'unique_titles':len(set(titles)),'unique_descriptions':len(set(descs)),'errors':errors}
print(json.dumps(summary,ensure_ascii=False,indent=2))
(R/'validation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
assert not errors
