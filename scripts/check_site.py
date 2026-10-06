from pathlib import Path
from urllib.parse import urlparse,unquote
from bs4 import BeautifulSoup
import json,re
root=Path(__file__).resolve().parents[1];errors=[];pages=[p for p in root.rglob('*.html') if not any(part.startswith('.') for part in p.relative_to(root).parts)];refs=set()
for path in pages:
 s=BeautifulSoup(path.read_text(),'html.parser')
 if s.select_one('meta[http-equiv="refresh"]'):continue
 if len(s.select('h1'))!=1:errors.append([str(path),'h1',len(s.select('h1'))])
 if not s.title or not s.select_one('meta[name=description]'):errors.append([str(path),'metadata'])
 if s.html.get('lang')!='fr':errors.append([str(path),'language'])
 for x in s.select('[src],a[href],link[href]'):
  a=x.get('src') or x.get('href') or '';u=urlparse(a)
  if u.scheme or a.startswith('#') or not a:continue
  p=(path.parent/unquote(u.path)).resolve()
  if not p.exists():errors.append([str(path.relative_to(root)),'missing',a])
  refs.add(str(p))
 for x in s.select('img'):
  if 'alt' not in x.attrs:errors.append([str(path),'alt missing'])
 for x in s.select('script[type="application/ld+json"]'):
  try:json.loads(x.string)
  except Exception:errors.append([str(path),'invalid jsonld'])
# Exact project prose and KPI checks.
def norm(t):return re.sub(r'\s+',' ',t).strip()
D=json.loads((root/'content/site-content.json').read_text())
for p in D['projects']:
 path=root/p['path']/'index.html';s=BeautifulSoup(path.read_text(),'html.parser');t=norm(s.get_text(' ',strip=True))
 for sec in p['sections']:
  ss=BeautifulSoup(sec['html'],'html.parser')
  for par in ss.select('p,li'):
   original=norm(par.get_text(' ',strip=True))
   if original not in t:errors.append([p['path'],'missing source paragraph',original[:150]])
 for k in p['kpis']:
  if norm(k['value']) not in t or norm(k['label']) not in t:errors.append([p['path'],'KPI mismatch',k])
# Source biographies, anecdotes and article paragraphs remain available in full.
for t in D['team']:
 target=root/'equipe/index.html';dest=norm(BeautifulSoup(target.read_text(),'html.parser').get_text(' ',strip=True))
 for field in ['bio','anecdote']:
  for par in BeautifulSoup(t[field],'html.parser').select('p,li'):
   original=norm(par.get_text(' ',strip=True))
   if original not in dest:errors.append(['equipe',t['name'],'missing source paragraph',original[:150]])
for n in D['news']:
 target=root/'newsroom'/n['slug']/'index.html';dest=norm(BeautifulSoup(target.read_text(),'html.parser').get_text(' ',strip=True))
 for par in BeautifulSoup(n['html'],'html.parser').select('p,li'):
  original=norm(par.get_text(' ',strip=True))
  if original not in dest:errors.append(['newsroom',n['slug'],'missing source paragraph',original[:150]])
report={'html_pages':len(pages),'projects':len(D['projects']),'team':len(D['team']),'news':len(D['news']),'errors':errors}
(root/'docs/static-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))

raise SystemExit(1 if errors else 0)
