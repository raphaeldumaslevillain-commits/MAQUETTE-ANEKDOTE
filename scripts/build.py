from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse,urljoin
import json,re,html,os,unicodedata,shutil,hashlib
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'content/site-content.json').read_text())
MAP=json.loads((ROOT/'content/media-map.json').read_text())
PAGES=json.loads((ROOT/'content/source-pages.json').read_text())
BASE='https://www.anekdote.fr'
SERVICES=[('Campagne d’influence','campagne-dinfluence'),('Stratégie','strategie'),('Évènements','evenements'),('Brand Content','brand-content'),('RSE / Corporate','rse-corporate'),('Performance / Affiliation','performance-affiliation')]
page='index.html';used=set();route_manifest=[]
def esc(s):return html.escape(str(s or ''),quote=True)
def soup(key):return BeautifulSoup((ROOT/'content/source-html'/((key.replace('/','__') or 'home')+'.html.txt')).read_text(),'html.parser')
def text(e):return e.get_text(' ',strip=True).replace('\u2068','') if e else ''
def bg(e):
 m=re.search(r'url\([\'\"]?(.*?)[\'\"]?\)',str(e));return m.group(1) if m else ''
def rel(path):
 return os.path.relpath(path,Path(page).parent).replace(os.sep,'/')
def versioned(path):
 return rel(path)+'?v='+hashlib.sha256((ROOT/path).read_bytes()).hexdigest()[:12]
def url(path=''):
 if path.startswith('http') or path.startswith('mailto:'):return path
 return rel((path.strip('/')+'/' if path.strip('/') else '')+'index.html')
def asset(source):
 if source not in MAP or 'error' in MAP[source]:raise RuntimeError('Missing media '+str(source))
 p=MAP[source]['path'];used.add(p);return rel(p)
def localpath(path):used.add(path);return rel(path)
def picture(source,alt='',cls='',eager=False,sizes='(max-width: 800px) 100vw, 90vw'):
 info=MAP.get(source)
 if not info or 'error' in info:return ''
 src=asset(source);props=''
 if info.get('width'):
  props=f' width="{info["width"]}" height="{info["height"]}"'
 variants=[(x['path'],x['width']) for x in info.get('variants',[])]+([(info['path'],info['width'])] if info.get('width') else [])
 srcset=''
 if variants:
  for p,w in variants:used.add(p)
  srcset=' srcset="'+', '.join(esc(rel(p))+' '+str(w)+'w' for p,w in variants)+'" sizes="'+esc(sizes)+'"'
 return f'<picture class="{cls}"><img src="{esc(src)}"{srcset} alt="{esc(alt)}"{props} loading="{"eager" if eager else "lazy"}" decoding="async"'+(' fetchpriority="high"' if eager else '')+'></picture>'
def clean(content,strip_heading=False):
 s=BeautifulSoup((content or '').replace('4 rue Jules Lefebvre','29 rue de Mogador').replace('9 RUE ARISTIDE BRUANT 75018 PARIS','29 rue de Mogador 75009 Paris'),'html.parser')
 if strip_heading:
  h=s.find(['h1','h2','h3']);h.decompose() if h else None
 for x in s.select('style,script,video,iframe,button'):x.decompose()
 for x in s.find_all(True):
  if x.name=='h1':x.name='h3'
  if x.name=='img':
   u=x.get('src');alt=x.get('alt','');x.attrs={'src':asset(u),'alt':alt,'loading':'lazy','decoding':'async'} if u in MAP else {};continue
  x.attrs={k:v for k,v in x.attrs.items() if k=='href'}
  if x.name=='a' and x.get('href'):
   u=urljoin(BASE,x['href']);parsed=urlparse(u)
   if parsed.netloc in ('www.anekdote.fr','anekdote.fr'):
    path=parsed.path.strip('/')
    x['href']=url('performance-affiliation')+'#coaching' if path=='coaching' else url(path)
   elif parsed.scheme in ['http','https']:x['target']='_blank';x['rel']='noopener noreferrer'
 return str(s)
def inner(e,strip_heading=False):
 return clean(''.join(str(x) for x in e.contents) if e else '',strip_heading)
def link(label,path,cls='text-link'):
 return f'<a class="{cls}" href="{esc(url(path))}">{label}<span class="link-symbol" aria-hidden="true">+</span></a>'
def section_top(n,title,end='Anekdote'):
 return f'<div class="section-top"><span class="eyebrow">{n:02d} • {title}</span><span class="eyebrow">{end}</span></div>'
def media_video(source,title):
 info=MAP[source];poster=info.get('poster');
 return '<figure class="media-frame video-figure">'+f'<video controls playsinline preload="none" data-lazy-video aria-label="{esc(title)}"'+(f' poster="{esc(localpath(poster))}"' if poster else '')+f'><source src="{esc(asset(source))}" type="video/mp4">Votre navigateur ne prend pas en charge les vidéos. <a href="{esc(asset(source))}">Télécharger la vidéo</a></video></figure>'
def counter(value):
 # Animate the numeric part only; preserve the exact published final value and units.
 m=re.fullmatch(r'([^0-9]*)([0-9]+(?:[ \u00a0][0-9]{3})*(?:[.,][0-9]+)?)(.*)',value)
 if not m or m.group(1)=='N°':return esc(value)
 prefix,n,suffix=m.groups();separator=',' if ',' in n else ('.' if '.' in n else ' ')
 decimals=len(re.split('[.,]',n)[-1]) if ',' in n or '.' in n else 0
 number=float(n.replace(' ','').replace('\u00a0','').replace(',','.'))
 return '<span class="sr-only">'+esc(value)+'</span><span aria-hidden="true" data-count="'+str(number)+'" data-decimals="'+str(decimals)+'" data-prefix="'+esc(prefix)+'" data-suffix="'+esc(suffix)+'" data-separator="'+separator+'">'+esc(value)+'</span>'

def project_item(p,i=0,attrs=False):
 cats=' / '.join(p['categories']);stats=p['kpis']
 if 'Stratégie Tiktok x ' in p['title']:
  client=p['title'].split('Stratégie Tiktok x ')[-1]
  selected=[k for k in stats if client.lower() in k['label'].lower()]
  stats=selected or stats
 if not attrs:
  stat=stats[0] if stats else None
  return '<article class="project-item reveal"><a href="'+esc(url(p['path']))+'"><div class="media-frame">'+picture(p['thumbnail'],p['title'],sizes="(max-width: 800px) 100vw, 50vw")+'</div><h3>'+esc(p['title'])+'</h3><div class="project-meta"><span>'+esc(cats)+'</span></div>'+(('<p class="inline-stat">'+esc(stat['value'])+' '+esc(stat['label'])+'</p>') if stat else '')+'</a></article>'
 description=p['description']
 if not description:
  paragraphs=[text(x) for sec in p['sections'] if sec['title']!='Les résultats' for x in BeautifulSoup(sec['html'],'html.parser').select('p') if text(x)]
  description=paragraphs[0] if paragraphs else p['h1']
 h='<article class="project-row reveal" data-project data-categories="'+esc(json.dumps(p['categories'],ensure_ascii=False))+'"><a class="project-row-link" href="'+esc(url(p['path']))+'" aria-label="'+esc('Découvrir le projet '+p['title'])+'"><div class="project-row-photo media-frame">'+picture(p['thumbnail'],p['title'],sizes="(max-width: 800px) 100vw, 42vw")+'<span class="project-photo-arrow" aria-hidden="true">↗</span></div><div class="project-row-copy"><div class="project-row-top"><span class="eyebrow">'+esc(cats)+'</span><span class="project-row-arrow" aria-hidden="true">↗</span></div><h2>'+esc(p['title'])+'</h2><p class="project-description">'+esc(description)+'</p><dl class="project-row-kpis">'
 for k in stats:
  if k['value'] and k['label']:h+='<div><dt>'+esc(k['label'])+'</dt><dd>'+counter(k['value'])+'</dd></div>'
 return h+'</dl>'+('<p class="project-results-unpublished">Résultats chiffrés non publiés.</p>' if not stats else '')+'<span class="project-discover">Voir le projet <span aria-hidden="true">→</span></span></div></a></article>'

def hero_intro(title,kicker,description='',serif=False,cls=''):
 eyebrow=f'<p class="eyebrow">{kicker}</p>' if kicker else ''
 heading_class='display serif' if serif else 'display'
 return f'<section class="page-intro {cls}">{eyebrow}<h1 class="{heading_class}">{title}</h1>'+(f'<p class="lead">{description}</p>' if description else '')+'</section>'
def header(active):
 nav=[('Agence','agence'),('Projets','hub-projets'),('Expertises','expertises'),('Équipe','equipe')]
 h='<a class="skip-link" href="#main">Aller au contenu</a><div class="reading-progress" aria-hidden="true"></div><header class="site-header"><a class="logo" href="'+url()+'" aria-label="Anekdote, accueil"><img src="'+asset(BASE+'/wp-content/uploads/2023/11/logo-anekdote.svg')+'" alt="Anekdote" width="145" height="34"></a><nav class="desktop-nav" aria-label="Navigation principale">'
 for label,p in nav:h+=f'<a href="{url(p)}"'+(' aria-current="page"' if active==p else '')+'>'+label+'</a>'
 h+='</nav><div class="header-actions"><a class="coffee" href="'+url('contact')+'">Un café ?</a><button class="theme-toggle" type="button" data-theme-toggle role="switch" aria-checked="false" aria-label="Thème sombre" title="Passer au thème sombre"><span class="theme-icon" aria-hidden="true"><svg class="theme-sun" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg><svg class="theme-moon" viewBox="0 0 24 24"><path d="M20.5 13.4A8.6 8.6 0 0 1 10.6 3.5a8.6 8.6 0 1 0 9.9 9.9Z"/></svg></span></button><button class="menu-toggle" aria-controls="navigation-dialog" aria-expanded="false" aria-label="Ouvrir le menu" data-menu-open><span>Menu</span><span class="menu-icon" aria-hidden="true"><i></i><i></i></span></button></div></header><span class="sr-only" data-theme-status role="status" aria-live="polite"></span>'
 h+='<dialog class="nav-dialog" id="navigation-dialog" aria-label="Navigation"><div class="nav-dialog-head"><a class="logo" href="'+url()+'"><img src="'+asset(BASE+'/wp-content/uploads/2023/11/logo-anekdote.svg')+'" alt="Anekdote" width="145" height="34"></a><button class="nav-close" data-menu-close>Fermer ×</button></div><div class="nav-grid"><nav class="nav-primary" aria-label="Toutes les pages">'
 for i,(label,p) in enumerate([('Accueil',''),('Agence','agence'),('Projets','hub-projets'),('Expertises','expertises'),('Équipe','equipe'),('Talents','talents'),('Contact','contact')]):h+=f'<a href="{url(p)}">{label}<small>{i+1:02d} •</small></a>'
 h+='</nav><nav class="nav-secondary" aria-label="Expertises et réseaux"><p class="eyebrow">Nos expertises</p>'
 for label,p in SERVICES:h+=f'<a href="{url(p)}">{label}</a>'
 h+='<p class="eyebrow">Retrouvons-nous</p><a href="https://www.instagram.com/anekdotefr/" target="_blank" rel="noopener">Instagram</a><a href="https://linkedin.com/company/anekdote-influence" target="_blank" rel="noopener">LinkedIn</a><p class="eyebrow">29 rue de Mogador<br>75009 Paris</p></nav></div></dialog>'
 return h

def footer():
 h='<footer class="site-footer"><a href="'+url('contact')+'" class="footer-invitation"><h2>Un café ?</h2><span class="circle-link" aria-hidden="true">↗</span></a><div class="footer-grid"><div><p class="eyebrow">Localisation</p><p>29 rue de Mogador,<br>75009 Paris</p><a href="'+url('contact')+'">Contactez-nous</a></div><div><p class="eyebrow">L’agence</p>'
 for label,p in [('Agence','agence'),('Projets','hub-projets'),('Équipe','equipe'),('Talents','talents')]:h+=f'<a href="{url(p)}">{label}</a>'
 h+='</div><div><p class="eyebrow">Expertises</p>'
 for label,p in SERVICES:h+=f'<a href="{url(p)}">{label}</a>'
 h+='</div><div><p class="eyebrow">Suivez-nous</p><a href="https://www.instagram.com/anekdotefr/" target="_blank" rel="noopener">Instagram</a><a href="https://linkedin.com/company/anekdote-influence" target="_blank" rel="noopener">LinkedIn</a><p class="eyebrow" style="margin-top:25px">Légal</p><a href="'+url('mentions-legales')+'">Mentions légales</a><a href="'+url('politique-de-confidentialite')+'">Confidentialité</a></div></div><div class="footer-bottom"><span>© Anekdote</span><span class="footer-partner">En partenariat avec <img src="'+asset(BASE+'/wp-content/uploads/2023/11/logo-arpp.png')+'" alt="ARPP et UMICC" width="216" height="28" loading="lazy"></span><button class="back-top" data-top>Retour en haut ↑</button></div><div class="footer-brand" aria-hidden="true"><img src="'+asset(BASE+'/wp-content/uploads/2023/11/logo-anekdote.svg')+'" alt="" width="1162" height="270" loading="lazy"></div></footer>'
 return h

def write(path,body,title,description,active='',schema=None):
 global page;assert page==path
 canonical=BASE+'/'+('' if path=='index.html' else str(Path(path).parent)+'/')
 css='<script src="'+versioned('js/theme-init.js')+'"></script>'+''.join(f'<link rel="stylesheet" href="{versioned("css/"+x+".css")}">' for x in ['fonts','variables','reset','typography','layout','components','animations','responsive','editorial','theme'])+'<noscript><link rel="stylesheet" href="'+versioned('css/no-script.css')+'"></noscript>'
 scripts=''.join(f'<script defer src="{versioned("js/"+x+".js")}"></script>' for x in ['theme','navigation','animations','projects','main','editorial']+(['contact'] if active=='contact' else []))
 meta='<meta name="description" content="'+esc(description)+'"><link rel="canonical" href="'+canonical+'"><meta property="og:title" content="'+esc(title)+'"><meta property="og:description" content="'+esc(description)+'"><meta property="og:type" content="website"><meta property="og:url" content="'+canonical+'">'
 s={'@context':'https://schema.org','@type':'Organization','name':'Anekdote','url':BASE,'address':{'@type':'PostalAddress','streetAddress':'29 rue de Mogador','postalCode':'75009','addressLocality':'Paris','addressCountry':'FR'},'sameAs':['https://www.instagram.com/anekdotefr/','https://linkedin.com/company/anekdote-influence']}
 if schema:s=schema
 modal='<dialog id="video-dialog" class="video-dialog" aria-label="Vidéo"><div class="video-dialog-top"><span data-video-title>Le film Anekdote</span><button class="video-dialog-close" data-video-close>Fermer ×</button></div><video playsinline controls preload="none"></video></dialog>'
 output='<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#f4f2eb"><title>'+esc(title)+'</title>'+meta+css+'<link rel="icon" href="'+rel('assets/brand/favicon.svg')+'" type="image/svg+xml"><script type="application/ld+json">'+json.dumps(s,ensure_ascii=False).replace('</','<'+chr(92)+'/')+'</script>'+scripts+'</head><body>'+header(active)+'<main id="main">'+body+'</main>'+footer()+modal+'</body></html>'
 dest=ROOT/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(output);route_manifest.append({'path':path,'source':canonical,'title':title})


def arrow(previous=False):
 return '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="'+('M19 12H5m7-7-7 7 7 7' if previous else 'M5 12h14m-7-7 7 7-7 7')+'"/></svg>'

def deck(slides,label,cls='',next_only=False,labels=True,autoplay=False):
 # Content is readable without JavaScript. Inert inactive slides are added on enhancement.
 h='<div class="deck '+cls+'" data-deck'+(' data-autoplay="3000"' if autoplay else '')+' role="region" aria-roledescription="carrousel" aria-label="'+esc(label)+'"><div class="deck-stage">'
 for i,(title,body) in enumerate(slides):
  h+='<article class="deck-slide'+(' active' if i==0 else '')+'" data-slide role="group" aria-label="'+str(i+1)+' sur '+str(len(slides))+'">'+('<p class="eyebrow deck-label">'+str(i+1).zfill(2)+' • '+esc(title)+'</p>' if labels else '')+body+'</article>'
 if autoplay:return h+'</div></div>'
 if next_only:return h+'</div><div class="deck-controls deck-next-only"><span class="sr-only" aria-live="polite" aria-atomic="true" data-deck-status>'+esc(slides[0][0])+'</span><button type="button" data-deck-next aria-label="Lire la section suivante">'+arrow()+'</button></div></div>'
 h+='</div><div class="deck-controls"><div class="deck-tabs" aria-label="Choisir une page">'
 for i,(title,body) in enumerate(slides):
  h+='<button type="button" data-deck-go="'+str(i)+'" aria-label="'+esc(title)+', page '+str(i+1)+'" aria-pressed="'+('true' if i==0 else 'false')+'">'+str(i+1).zfill(2)+'</button>'
 h+='</div><div class="deck-arrows"><span class="deck-status" aria-live="polite" aria-atomic="true" data-deck-status>1 / '+str(len(slides))+'</span><button type="button" data-deck-prev aria-label="Page précédente">←</button><button type="button" data-deck-next aria-label="Page suivante">→</button></div></div></div>'
 return h

def accordion(cls='',numbered=True):
 h='<div class="expertise-accordion '+cls+'">'
 for i,(label,key) in enumerate(SERVICES):
  desc=text(soup(key).select_one('.page-header-banner-baseline'))
  h+='<details><summary>'+('<span class="eyebrow">'+str(i+1).zfill(2)+' •</span>' if numbered else '')+'<h3>'+label+'</h3><span class="accordion-symbol" aria-hidden="true">+</span></summary><div class="expertise-answer"><p>'+esc(desc)+'</p>'+link('Découvrir cette expertise',key)+'</div></details>'
 return h+'</div>'

def client_marquees():
 ho=soup('');sources=[]
 for im in ho.select('#content img'):
  u=im.get('src','')
  if 'logo-' in u and u not in sources and 'anekdote' not in u.split('/')[-1] and 'arpp' not in u:sources.append(u)
 h='<div class="marquee" data-marquee><div class="marquee-controls"><span class="eyebrow">Ils nous font confiance</span></div>'
 for i,group in enumerate([sources[::2],sources[1::2]]):
  h+='<div class="marquee-row'+(' reverse' if i else '')+'"><div class="marquee-track">'
  for copy in range(2):
   h+='<div class="marquee-group"'+(' aria-hidden="true"' if copy else '')+'>'
   for u in group:
    label=re.split('-logo',u.split('/')[-1])[0].replace('_','’').replace('-',' ')
    h+=picture(u,label if not copy else '',sizes='160px')
   h+='</div>'
  h+='</div></div>'
 return h+'</div>'

def heart(cross=False):
 return '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8Z"/>'+('<path d="M3 3l18 18"/>' if cross else '')+'</svg>'

def portrait_content(content):
 node=BeautifulSoup(content,'html.parser')
 for x in node.select('ul'):x.decompose()
 for x in node.select('h3'):
  if text(x) in ['Une Anekdote ?','2 mantras qui m’animent :','2 mantras qui m’animent:']:x.decompose()
 return clean(str(node))

def bio_chunks(content,limit=530):
 node=BeautifulSoup(content,'html.parser');paras=node.select('p')
 if not paras:return [clean(content)]
 chunks=[];current=[];length=0
 for par in paras:
  if not text(par):continue
  size=len(text(par))
  if current and length+size>limit:chunks.append(clean(''.join(current)));current=[];length=0
  current.append(str(par));length+=size
 if current:chunks.append(clean(''.join(current)))
 return chunks

def home():
 global page;page='index.html';ag=soup('agence');ho=soup('');ghd=DATA['projects'][3]
 b='<section class="masthead"><div class="masthead-meta"><p class="eyebrow">Agence de conseil<br>Marketing d’influence & Brand Content</p></div><h1 class="wordmark" aria-label="Anekdote">Anek<span class="italic">dote</span><span class="dot">.</span></h1></section>'
 b+='<section class="company-stage">'+picture(bg(ag.select_one('.page-header-banner-container')),'L’équipe Anekdote dans un escalier parisien',eager=True)+'<div class="company-overlay"><p class="eyebrow">Enchanté !</p><h2>Nous créons<br>vos <span class="italic">campagnes.</span></h2></div></section>'
 b+='<section class="section home-services"><div class="home-services-heading"><div><h2 class="section-title">L’idée.<br><span class="italic">Puis l’action.</span></h2></div><p class="lead">Nous créons vos campagnes pour accélérer votre notoriété et optimiser votre conversion.</p></div>'+accordion('home-accordion',numbered=False)+'</section>'
 b+='<section class="section clients"><div class="client-intro"><h2>Nous vous adorons,<br><span class="italic">c’est réciproque.</span></h2><p>Nous avons plus de 50 partenaires qui nous font confiance dans la beauté, la mode, la tech/app, la food et le retail.</p></div>'+client_marquees()+'</section>'
 b+='<section class="section home-agency"><div class="home-agency-photo media-frame reveal">'+picture(BASE+'/wp-content/uploads/2024/09/Design-sans-titre-3.png','Un moment partagé par l’équipe Anekdote')+'</div><div class="home-agency-copy"><h2 class="section-title">Une équipe<br><span class="italic">passionnée.</span></h2><p class="lead">L’échange est notre moteur, le partage est notre super-force, et la positivité est notre arme secrète.</p></div></section>'
 b+='<section class="section proof"><div class="proof-copy"><h2 class="section-title">La créativité.<br><span class="italic">Et son impact.</span></h2><p>Une équipe passionnée pour des campagnes sur-mesure et performantes.</p></div><div class="proof-kpis">'
 for v,l,p,number,decimals,suffix,separator in [('7.2M','de vues au total',ghd,7.2,1,'M','.'),('1,73 M','de reach',DATA['projects'][1],1.73,2,' M',','),('31 377','clics sur lien',DATA['projects'][0],31377,0,'',' ')]:
  b+='<a class="proof-row" href="'+url(p['path'])+'"><strong><span class="sr-only">'+v+'</span><span aria-hidden="true" data-count="'+str(number)+'" data-decimals="'+str(decimals)+'" data-suffix="'+suffix+'" data-separator="'+separator+'">'+v+'</span></strong><p>'+l+'<span>'+esc(p['title'])+'</span></p></a>'
 b+='</div></section>'
 write(page,b,PAGES[BASE+'/']['title'],PAGES[BASE+'/']['description'],'')

def agency():
 global page;page='agence/index.html';s=soup('agence');m=s.select_one('#content');sections={text(h):h.parent for h in m.select('h2')}
 b='<section class="agency-intro page-intro"><div class="editorial-heading"><h1 class="display">L’<span class="italic">agence.</span></h1></div></section>'
 slides=[]
 for title in ['Notre histoire','Notre raison d’être','Nos engagements']:
  node=sections[title];paras=node.select('p');chunks=[];group=[];length=0
  for par in paras:
   if group and length+len(text(par))>650:chunks.append(group);group=[];length=0
   group.append(par);length+=len(text(par))
  if group:
   if chunks and sum(len(text(x)) for x in group)<100:chunks[-1].extend(group)
   else:chunks.append(group)
  for chunk in chunks:slides.append((title,'<h2>'+esc(title)+'</h2><div class="prose">'+clean(''.join(str(x) for x in chunk))+'</div>'))
 b+='<section class="agency-about wrap"><div class="agency-photo media-frame">'+picture(bg(s.select_one('.page-header-banner-container')),'L’équipe Anekdote',eager=True)+'</div>'+deck(slides,'L’histoire et les engagements Anekdote','agency-deck',True,labels=False)+'</section>'
 q=sections['Pourquoi Anekdote ?'];paras=q.select('p');b+='<section class="agency-quote"><blockquote>'+''.join(clean(str(x)) for x in paras[:2])+'<footer>Christelle, Co-Founder</footer></blockquote></section>'
 manifest=sections['Manifeste'];slides=[]
 for item in manifest.select('.agence-manifeste-text'):
  h=item.select_one('h3');copy=item.select_one('p');slides.append(('Manifeste','<h3>'+esc(text(h))+'</h3><p>'+esc(text(copy))+'</p>'))
 b+='<section class="manifest-section section"><div class="manifest-heading"><h2>Ce qui nous<br><span class="italic">anime.</span></h2></div>'+deck(slides,'Le manifeste Anekdote','manifest-deck',labels=False,autoplay=True)+'</section>'
 write(page,b,PAGES[BASE+'/agence/']['title'],PAGES[BASE+'/agence/']['description'],'agence')

def portfolio():
 global page;page='hub-projets/index.html';s=soup('hub-projets');b=hero_intro('Nos <span class="italic">projets.</span>','',text(s.select_one('.page-header-banner-baseline')),cls='portfolio-intro')
 b+='<section class="portfolio" aria-label="Portfolio">'
 for i,p in enumerate(DATA['projects']):b+=project_item(p,i,True)
 b+='</section>'
 write(page,b,PAGES[BASE+'/hub-projets/']['title'],PAGES[BASE+'/hub-projets/']['description'],'hub-projets')

def cases():
 global page
 for i,p in enumerate(DATA['projects']):
  page=p['path']+'/index.html';desc=PAGES[p['url']]['description'];b='<section class="page-intro case-intro"><nav class="breadcrumbs" aria-label="Fil d’Ariane"><a href="'+url()+'">Anekdote</a><span>/</span><a href="'+url('hub-projets')+'">Projets</a></nav><p class="eyebrow">'+esc(' / '.join(p['categories']))+'</p><h1 class="display">'+esc(p['h1'])+'</h1><div class="case-meta"><span>'+esc(p['title'])+'</span><span>Anekdote · Étude de cas • '+str(i+1).zfill(2)+'</span></div></section>'
  b+='<div class="case-hero">'+picture(p['hero'],p['title'],eager=True)+'</div>'
  if p['description']:b+='<section class="case-description"><p class="eyebrow">Le projet</p><p class="lead">'+esc(p['description'])+'</p></section>'
  chapters=[x for x in p['sections'] if x['title']!='Les résultats'];result=next((x for x in p['sections'] if x['title']=='Les résultats'),None);b+='<div class="case-body">'
  for j,c in enumerate(chapters):
   med=p['media'][j] if j<len(p['media']) else None
   b+='<section class="case-chapter reveal'+(' no-visual' if not med else '')+'"><div class="chapter-heading"><p class="eyebrow">'+str(j+1).zfill(2)+' •</p><h2>'+esc(c['title'])+'</h2></div><div class="prose">'+clean(c['html'],True)+'</div>'
   if med:
    info=MAP[med['src']];b+=media_video(med['src'],p['title']) if info['path'].endswith('.mp4') else '<div class="media-frame">'+picture(med['src'],med['alt'])+'</div>'
   b+='</section>'
  b+='</div>'
  if result or p['kpis']:
   b+='<section class="case-results"><div class="case-results-top"><h2>Les <span class="italic">résultats.</span></h2><div class="prose">'+clean(result['html'],True) if result else '<section class="case-results"><div class="case-results-top"><h2>Les résultats.</h2><div>'
   b+='</div></div><div class="kpi-grid'+(' long-values' if any(len(k['value'])>6 for k in p['kpis']) else '')+'">'
   for k in p['kpis']:b+='<div class="kpi'+(' long' if len(k['value'])>6 else '')+'"><strong>'+counter(k['value'])+'</strong><span>'+esc(k['label'])+'</span></div>'
   b+='</div></section>'
  else:b+='<section class="case-results"><div class="case-results-top"><h2>Les <span class="italic">résultats.</span></h2><p class="prose">Résultats chiffrés non publiés.</p></div></section>'
  extras=list(dict.fromkeys(p['extra']))
  if extras:b+='<section class="case-extra prose">'+''.join('<p>'+esc(x)+'</p>' for x in extras)+'</section>'
  if len(p['media'])>len(chapters):
   b+='<section class="case-gallery" aria-label="Contenus de la campagne">'
   for med in p['media'][len(chapters):]:b+=media_video(med['src'],p['title']) if MAP[med['src']]['path'].endswith('.mp4') else '<div class="media-frame">'+picture(med['src'],med['alt'])+'</div>'
   b+='</section>'
  nxt=DATA['projects'][(i+1)%len(DATA['projects'])];b+='<a class="next-project" href="'+url(nxt['path'])+'">'+picture(nxt['thumbnail'],nxt['title'])+'<div><p class="eyebrow">Le projet suivant</p><h2>'+esc(nxt['title'])+'</h2></div></a>'
  schema={'@context':'https://schema.org','@type':'CreativeWork','name':p['title'],'description':p['description'],'creator':{'@type':'Organization','name':'Anekdote'},'url':p['url']}
  write(page,b,PAGES[p['url']]['title'],desc,'hub-projets',schema)

def solar_metrics(c):
 paras=[x for x in c.select('p') if text(x)];groups=c.select('ul')
 h='<section class="solar-section" id="coaching"><div class="solar-heading reveal"><div><h2>Solar <span class="italic">Metrics.</span></h2></div></div><div class="solar-main"><div class="solar-narrative reveal"><h3>Pourquoi <span class="italic">Solar Metrics ?</span></h3><div class="prose">'+''.join(clean(str(x)) for x in paras[:2])+'</div></div><div class="solar-orbit reveal" aria-hidden="true"><svg viewBox="0 0 400 400" fill="none"><circle class="orbit-guide" cx="200" cy="200" r="166"/><circle class="orbit-guide" cx="200" cy="200" r="120"/><path class="orbit-line" d="M34 200a166 166 0 0 1 332 0"/><path class="orbit-line inner" d="M200 80a120 120 0 0 1 0 240"/><circle class="orbit-point" cx="200" cy="34" r="5"/><circle class="orbit-point" cx="366" cy="200" r="5"/><circle class="orbit-point" cx="200" cy="366" r="5"/><circle class="orbit-point" cx="34" cy="200" r="5"/></svg><div class="orbit-core"><strong>100<span>%</span></strong><span>Acquisition<br>digitale</span></div><span class="orbit-caption">Une vision hybride de l’influence</span></div></div><div class="solar-expertises reveal"><p class="eyebrow">'+esc(text(paras[2]))+'</p><ol>'
 for i,li in enumerate(groups[0].select('li')):
  h+='<li><span class="solar-step">'+str(i+1).zfill(2)+'</span><h3>'+esc(text(li))+'</h3></li>'
 h+='</ol></div><div class="solar-measures reveal"><p>'+esc(text(paras[3]))+'</p><ul>'
 for li in groups[1].select('li'):h+='<li>'+esc(text(li))+'</li>'
 return h+'</ul></div></section>'

def expertises():
 global page;page='expertises/index.html'
 b='<section class="page-intro expertise-intro"><p class="eyebrow">01 • Nos expertises</p><div class="editorial-heading"><h1 class="display">L’idée.<br><span class="italic">Puis l’action.</span></h1></div></section>'
 b+='<section class="expertise-overview wrap"><h2 class="sr-only">Nos expertises</h2><figure class="expertise-new-photo media-frame">'+picture(DATA['projects'][6]['hero'],'Activation influence Anekdote — Festival de Cannes x Soskin',eager=True)+'</figure>'+accordion('overview-accordion',numbered=False)+'</section>'
 write(page,b,'Anekdote | Nos expertises en influence et création','Campagne d’influence, stratégie, évènements, Brand Content, RSE / Corporate, Performance / Affiliation.','expertises')
 for i,(label,key) in enumerate(SERVICES):
  page=key+'/index.html';s=soup(key);m=s.select_one('#content');b=hero_intro(esc(text(s.h1))+'<span class="orange">.</span>','',text(s.select_one('.page-header-banner-baseline')),True,'service-intro')
  b+='<div class="page-visual media-frame">'+picture(bg(s.select_one('.page-header-banner-container')),label,eager=True)+'</div>'
  for c in m.select('.bloc-column-text'):
   if key=='performance-affiliation':b+=solar_metrics(c)
   else:
    title=text(c.find('h2'))
    heading='' if key=='evenements' else '<div><h2>'+esc(title)+'</h2></div>'
    b+='<section class="story-section reveal'+(' approach-copy-only' if key=='evenements' else '')+'">'+heading+'<div class="prose">'+inner(c,True)+'</div></section>'
  # Annotation revision: the expertise page ends after its approach / Solar Metrics.
  write(page,b,PAGES[BASE+'/'+key+'/']['title'],PAGES[BASE+'/'+key+'/']['description'],'expertises')

def member_paragraphs(member):
 # Preserve every supplied sentence while restoring meaningful paragraph breaks.
 paragraphs=[]
 for field in ['bio','anecdote']:
  fragment=BeautifulSoup(member[field],'html.parser')
  nodes=fragment.select('p')
  if not nodes:nodes=[node for node in fragment.select('div') if not node.find(['div','p','ul'])]
  for node in nodes:
   value=text(node)
   if not value:continue
   for start in ['Gestionnaire aguerrie,','Toujours à l’affût des dernières tendances,','Curieux, créatif et toujours à la recherche','Ma mission ? Donner du sens','Toujours un projet ou une idée en tête,']:
    value=value.replace(' '+start,'\n'+start)
   paragraphs.extend(part.strip() for part in value.split('\n') if part.strip())
 return ''.join('<p>'+esc(part)+'</p>' for part in paragraphs)

def team():
 global page;page='equipe/index.html';s=soup('equipe');christelle=DATA['team'][0]
 members=[dict(t,display_name=('Emma.L' if j==2 else 'Emma.c' if j==3 else t['name'])) for j,t in enumerate(DATA['team']) if j>0 and t['name']!='Pauline']
 b=hero_intro('L’équipe <span class="italic">Anekdote.</span>','01 • #TeamAnekdote',text(s.select_one('.page-header-banner-baseline')),cls='team-intro')
 spirit=s.select_one('.bloc-column-text');im=s.select_one('.bloc-column-visual img')
 b+='<section class="team-spirit"><div><h2 class="section-title">L’esprit<br><span class="italic">d’équipe.</span></h2><div class="prose">'+inner(spirit,True)+'</div></div><div class="media-frame team-group-photo">'+picture(im['src'],'Un moment partagé par l’équipe Anekdote',eager=True)+'</div></section>'
 b+='<section class="founder-section wrap" aria-labelledby="founder-name"><div class="founder-heading reveal"><h2 id="founder-name">Christelle<span class="italic">.</span></h2><span class="founder-role">Co-Founder</span></div><div class="founder-layout"><div class="founder-photo media-frame reveal">'+picture(christelle['portrait'],'Christelle — Co-Founder d’Anekdote',sizes='(max-width: 800px) 90vw, 42vw')+'</div><div class="founder-story prose reveal">'+clean(christelle['bio'])+'</div></div><div class="founder-anecdote reveal"><div><p class="eyebrow">Une Anekdote</p><div class="prose">'+portrait_content(christelle['anecdote'])+'</div></div><div class="founder-mantras">'+picture(BASE+'/wp-content/uploads/2023/11/Group-1798.svg','Les deux mantras de Christelle')+'</div></div></section>'
 b+='<section class="team-carousel-section wrap" id="team-members" aria-label="L’équipe Anekdote"><div class="deck team-carousel" data-deck role="region" aria-roledescription="carrousel" aria-label="Les membres de l’équipe"><div class="deck-stage">'
 for i,t in enumerate(members):
  key='member-'+str(i+1);an=BeautifulSoup(t['anecdote'],'html.parser');groups=[[text(li) for li in ul.select('li')] for ul in an.select('ul')];overlay=''
  for j,items in enumerate(groups[:2]):
   overlay+='<div class="taste-group"><h4>'+('J’aime' if j==0 else 'Je n’aime pas')+'</h4><ul>'
   for item in items:overlay+='<li>'+heart(j==1)+'<span>'+esc(item)+'</span></li>'
   overlay+='</ul></div>'
  b+='<article class="deck-slide team-slide'+(' active' if i==0 else '')+'" data-slide role="group" aria-label="'+esc(t['display_name'])+', '+str(i+1)+' sur '+str(len(members))+'"><header class="member-heading"><h3>'+esc(t['display_name'])+'</h3><span class="eyebrow">#TeamAnekdote · '+str(i+1).zfill(2)+'</span></header><div class="member-layout"><div class="member-photo media-frame" data-profile-photo tabindex="0" role="button" aria-label="Découvrir les goûts de '+esc(t['display_name'])+'" aria-expanded="false" aria-controls="'+key+'-tastes">'+picture(t['portrait'],t['display_name']+' — portrait Anekdote',sizes='(max-width: 800px) 180px, 400px')+'<div class="photo-tastes" id="'+key+'-tastes" aria-hidden="true">'+overlay+'</div></div><div class="member-story" tabindex="0" role="region" aria-label="Le portrait de '+esc(t['display_name'])+'">'+member_paragraphs(t)+'</div></div></article>'
 b+='</div><div class="deck-controls"><div class="deck-tabs member-tabs" aria-label="Choisir un membre">'
 for i,t in enumerate(members):b+='<button type="button" data-deck-go="'+str(i)+'" aria-label="'+esc(t['display_name'])+', membre '+str(i+1)+'" aria-pressed="'+('true' if i==0 else 'false')+'"><span class="member-name-index" aria-hidden="true">'+str(i+1).zfill(2)+'</span>'+esc(t['display_name'])+'</button>'
 b+='</div><div class="deck-arrows"><span class="deck-status" data-deck-status aria-live="polite" aria-atomic="true">1 / '+str(len(members))+'</span><button type="button" data-deck-prev aria-label="Membre précédent">'+arrow(True)+'</button><button type="button" data-deck-next aria-label="Membre suivant">'+arrow()+'</button></div></div></div></section>'
 write(page,b,PAGES[BASE+'/equipe/']['title'],PAGES[BASE+'/equipe/']['description'],'equipe')

def talents():
 global page;page='talents/index.html';s=soup('talents')
 b='<section class="page-intro talents-intro"><p class="eyebrow">01 • Les talents</p><div class="editorial-heading"><h1 class="display">Notre<br><span class="italic">talent ?</span></h1><p class="lead">Un network puissant de créateurs de contenu !</p></div></section>'
 b+='<section class="talents-feature wrap"><div class="talents-feature-photo media-frame">'+picture(DATA['projects'][8]['thumbnail'],'Meganvlt — Festival de Cannes x Aroma-Zone',eager=True)+'</div><div class="talents-principles">'
 for i,node in enumerate(s.select('.bloc-talents-text')):
  b+='<article><span class="eyebrow">'+str(i+1).zfill(2)+' •</span><h2>'+esc(text(node.select_one('h2')))+'</h2><div class="prose">'+clean(''.join(str(x) for x in node.select('p')))+'</div></article>'
 b+='</div></section>'
 slides=[]
 for node in s.select('.talents-header-citation,.bloc-talents-citation'):
  # Quotation and attribution remain word-for-word as published.
  p=node.select_one('p');parts=p.decode_contents().split('<br/>');quote=text(BeautifulSoup(parts[0],'html.parser'));author=text(BeautifulSoup(parts[-1],'html.parser'));name=author.lstrip('- ').strip()
  slides.append((name,'<blockquote><p>'+esc(quote)+'</p><footer>'+esc(author)+'</footer></blockquote>'))
 b+='<section class="talents-voices section"><div><p class="eyebrow">02 • Leurs mots</p><h2 class="section-title">Le plaisir<br>de <span class="italic">collaborer.</span></h2></div>'+deck(slides,'Les témoignages publiés des talents','voices-deck')+'</section>'
 write(page,b,PAGES[BASE+'/talents/']['title'],PAGES[BASE+'/talents/']['description'],'talents')

def contact():
 global page;page='contact/index.html';s=soup('contact');b=hero_intro('Un <span class="italic">café ?</span>','07 • Contactez-nous',text(s.select_one('.page-header-banner-baseline')),cls='contact-intro')
 b+='<section class="contact-layout"><aside class="contact-aside"><div class="media-frame">'+picture(bg(s.select_one('.page-header-banner-container')),'Le rooftop Anekdote — Paris',eager=True)+'</div><p class="eyebrow">29 rue de Mogador • 75009 Paris</p><p class="annotation">On a hâte d’écouter vos projets.</p></aside><form class="contact-form" data-contact-form data-endpoint="https://www.anekdote.fr/wp-json/contact-form-7/v1/contact-forms/547/feedback" action="https://www.anekdote.fr/contact/#wpcf7-f547-o1" method="post"><input type="hidden" name="_wpcf7" value="547"><input type="hidden" name="_wpcf7_version" value="6.1.6"><input type="hidden" name="_wpcf7_locale" value="fr_FR"><input type="hidden" name="_wpcf7_unit_tag" value="wpcf7-f547-o1"><input type="hidden" name="_wpcf7_container_post" value="0"><input type="hidden" name="_wpcf7_posted_data_hash" value=""><section class="form-step" data-step="0"><h2 tabindex="-1">Quelle est votre<br><span class="italic">boisson préférée ?</span></h2><fieldset class="choice-grid"><legend class="sr-only">Choisissez une boisson</legend>'
 for c in s.select('.drink-slide-content'):
  im=c.find('img');label=text(c);b+='<label class="choice"><input type="radio" name="your-drink" value="'+esc(label)+'" required>'+picture(im['src'],'',sizes='70px')+'<span>'+esc(label)+'</span></label>'
 b+='</fieldset><div class="form-actions"><span class="eyebrow">À votre goût.</span><button class="button" type="button" data-next>Continuer</button></div></section><section class="form-step" data-step="1"><h2 tabindex="-1">Où voulez-vous<br><span class="italic">vous installer ?</span></h2><fieldset class="choice-grid"><legend class="sr-only">Choisissez un lieu</legend>'
 for c in s.select('.where-slide-content'):
  im=c.find('img');label=text(c);b+='<label class="choice"><input type="radio" name="your-place" value="'+esc(label)+'" required>'+picture(im['src'],'',sizes='70px')+'<span>'+esc(label)+'</span></label>'
 b+='</fieldset><div class="form-actions"><button class="button secondary" type="button" data-prev>Retour</button><button class="button" type="button" data-next>Continuer</button></div></section><section class="form-step" data-step="2"><h2 tabindex="-1">Rencontrons<span class="italic">-nous.</span></h2><p class="form-recap" data-recap></p><div class="form-grid"><div class="form-field full"><label for="gender">Civilité*</label><select id="gender" name="your-gender" required><option value="">Choisissez</option><option>Mademoiselle</option><option>Madame</option><option>Monsieur</option><option>Autre</option></select></div>'
 for label,name,kind,required,autocomplete in [('Nom*','your-name','text',True,'family-name'),('Prénom*','your-firstname','text',True,'given-name'),('Téléphone','your-tel','tel',False,'tel'),('Adresse mail*','your-email','email',True,'email')]:
  b+='<div class="form-field"><label for="'+name+'">'+label+'</label><input id="'+name+'" name="'+name+'" type="'+kind+'" maxlength="400" autocomplete="'+autocomplete+'"'+(' required' if required else '')+'></div>'
 b+='<div class="form-field full"><label for="message">Votre message</label><textarea id="message" name="your-message" maxlength="2000" rows="5"></textarea></div></div><p class="form-consent">Les champs marqués * sont obligatoires. Vos informations servent à répondre à votre demande. <a href="'+url('politique-de-confidentialite')+'">Politique de confidentialité</a>.</p><div class="form-actions"><button class="button secondary" type="button" data-prev>Retour</button><button class="button" type="submit">Envoyer</button></div><p class="form-status" role="status" aria-live="polite" data-form-status></p><p class="form-consent"><a href="https://www.anekdote.fr/contact/" target="_blank" rel="noopener">Accéder au formulaire Anekdote</a></p></section></form></section>'
 write(page,b,PAGES[BASE+'/contact/']['title'],PAGES[BASE+'/contact/']['description'],'contact')

def legal():
 global page
 for key in ['mentions-legales','politique-de-confidentialite']:
  page=key+'/index.html';s=soup(key);m=s.select_one('#content');b=hero_intro(esc(text(s.h1)),'Anekdote — Informations légales',serif=True)+'<article class="legal-layout"><div class="prose">'+inner(m,True)+'</div></article>'
  write(page,b,PAGES[BASE+'/'+key+'/']['title'],PAGES[BASE+'/'+key+'/']['description'])

shutil.rmtree(ROOT/'newsroom',ignore_errors=True)
home();agency();portfolio();cases();expertises();team();talents();contact();legal()
# Keep legacy archive routes usable; their contents now point to the complete portfolio.
for path in ['projets','projets/page/2','projets/page/3','projets/page/4','hub-projets/page/1','hub-projets/page/2','hub-projets/page/3','hub-projets/page/4','coaching']:
 page=path+'/index.html';dest=url('performance-affiliation' if path=='coaching' else 'hub-projets');p=ROOT/page;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text('<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0;url='+dest+'"><link rel="canonical" href="'+BASE+('/performance-affiliation/' if path=='coaching' else '/hub-projets/')+'"><title>Anekdote — Projets et expertises</title></head><body><a href="'+dest+'">Continuer vers Anekdote</a></body></html>')
page='404.html';write(page,hero_intro('Cette page<br>fait <span class="italic">une pause.</span>','Anekdote — 404')+'<section class="section">'+link('Retour à l’accueil','')+'</section>','Anekdote — Page introuvable','Retrouvez les projets et expertises Anekdote.')
(ROOT/'assets/brand/favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="#171716"/><text x="8" y="49" font-family="Arial,sans-serif" font-weight="700" font-size="51" fill="#f4f2eb">A</text><circle cx="53" cy="51" r="5" fill="#ff471f"/></svg>')
(ROOT/'docs/routes.json').write_text(json.dumps(route_manifest,ensure_ascii=False,indent=2))
(ROOT/'docs/assets.json').write_text(json.dumps([v for v in MAP.values() if v.get('path') in used],ensure_ascii=False,indent=2))
(ROOT/'content/site-content.json').write_text(json.dumps(DATA,ensure_ascii=False,indent=2))
(ROOT/'content/source-pages.json').write_text(json.dumps(PAGES,ensure_ascii=False,indent=2))
(ROOT/'content/media-map.json').write_text(json.dumps(MAP,ensure_ascii=False,indent=2))
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+r['source']+'</loc></url>' for r in route_manifest if not r['path'].endswith('404.html'))+'</urlset>')
(ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://www.anekdote.fr/sitemap.xml\n')
(ROOT/'.nojekyll').touch()
(ROOT/'docs/used-assets.json').write_text(json.dumps(sorted(used),indent=2))
print('BUILT',len(route_manifest),'pages;',len(used),'asset files')
