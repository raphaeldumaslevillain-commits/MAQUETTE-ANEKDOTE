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
def norm(t):return re.sub(r'\s+',' ',t.replace('\u2068','')).strip()
def approved(t):
 return t.replace('4 rue Jules Lefebvre','29 rue de Mogador').replace('9 RUE ARISTIDE BRUANT 75018 PARIS','29 rue de Mogador 75009 Paris').replace('– Christelle, CEO.','Christelle, Co-Founder')
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
# Newsroom was explicitly removed from the published experience by the user.
if (root/'newsroom').exists():errors.append(['newsroom','retired routes still exist'])
for path in pages:
 ss=BeautifulSoup(path.read_text(),'html.parser')
 if ss.select('a[href*="newsroom"]'):errors.append([str(path.relative_to(root)),'retired Newsroom link'])
 if '4 rue Jules Lefebvre' in ss.get_text():errors.append([str(path.relative_to(root)),'old office address'])
# Verify all institutional, expertise, talent and legal source paragraphs too.
for key in ['agence','campagne-dinfluence','strategie','evenements','brand-content','rse-corporate','performance-affiliation','talents','mentions-legales','politique-de-confidentialite']:
 src=BeautifulSoup((root/'content/source-html'/(key+'.html.txt')).read_text(),'html.parser').select_one('#content')
 dest=norm(BeautifulSoup((root/key/'index.html').read_text(),'html.parser').get_text(' ',strip=True))
 for par in src.select('p,li'):
  original=approved(norm(par.get_text(' ',strip=True)))
  if len(original)>10 and original not in dest:errors.append([key,'missing source paragraph',original[:150]])
report={'html_pages':len(pages),'projects':len(D['projects']),'team':len(D['team']),'news':0,'approved_changes':['Newsroom removed','Office: 29 rue de Mogador','Agency quote: Christelle, Co-Founder'],'errors':errors}
(root/'docs/static-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))

raise SystemExit(1 if errors else 0)
