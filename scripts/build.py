from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse,urljoin
import json,re,html,os,unicodedata,shutil
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
def project_item(p,i=0,attrs=False):
 cats=' / '.join(p['categories']);stat=p['kpis'][0] if p['kpis'] else None
 if 'Stratégie Tiktok x ' in p['title']:
  client=p['title'].split('Stratégie Tiktok x ')[-1]
  stat=next((k for k in p['kpis'] if client.lower() in k['label'].lower()),stat)
 return f'<article class="project-item reveal"'+(f' data-project data-categories="{esc(json.dumps(p["categories"],ensure_ascii=False))}"' if attrs else '')+'>'+f'<a href="{esc(url(p["path"]))}"><div class="media-frame">{picture(p["thumbnail"],p["title"],sizes="(max-width: 800px) 100vw, 50vw")}</div><h3>{esc(p["title"])}</h3><div class="project-meta"><span>{esc(cats)}</span><span>{i+1:02d} •</span></div>'+ (f'<p class="inline-stat">{esc(stat["value"])} {esc(stat["label"])}</p>' if stat else '')+'</a></article>'
def hero_intro(title,kicker,description='',serif=False):
 return f'<section class="page-intro"><p class="eyebrow">{kicker}</p><h1 class="display{ " serif" if serif else ""}">{title}</h1>'+ (f'<p class="lead">{description}</p>' if description else '')+'</section>'
def header(active):
 nav=[('Agence','agence'),('Projets','hub-projets'),('Expertises','expertises'),('Équipe','equipe')]
 h='<a class="skip-link" href="#main">Aller au contenu</a><div class="reading-progress" aria-hidden="true"></div><header class="site-header"><a class="logo" href="'+url()+'" aria-label="Anekdote, accueil"><img src="'+asset(BASE+'/wp-content/uploads/2023/11/logo-anekdote.svg')+'" alt="Anekdote" width="145" height="34"></a><nav class="desktop-nav" aria-label="Navigation principale">'
 for label,p in nav:h+=f'<a href="{url(p)}"'+(' aria-current="page"' if active==p else '')+'>'+label+'</a>'
 h+='</nav><div class="header-actions"><a class="coffee" href="'+url('contact')+'">Un café ?</a><button class="menu-toggle" aria-controls="navigation-dialog" aria-expanded="false" aria-label="Ouvrir le menu" data-menu-open><span>Menu</span><span class="menu-icon" aria-hidden="true"><i></i><i></i></span></button></div></header>'
 h+='<dialog class="nav-dialog" id="navigation-dialog" aria-label="Navigation"><div class="nav-dialog-head"><a class="logo" href="'+url()+'"><img src="'+asset(BASE+'/wp-content/uploads/2023/11/logo-anekdote.svg')+'" alt="Anekdote" width="145" height="34"></a><button class="nav-close" data-menu-close>Fermer ×</button></div><div class="nav-grid"><nav class="nav-primary" aria-label="Toutes les pages">'
 for i,(label,p) in enumerate([('Accueil',''),('Agence','agence'),('Projets','hub-projets'),('Expertises','expertises'),('Équipe','equipe'),('Talents','talents'),('Contact','contact')]):h+=f'<a href="{url(p)}">{label}<small>{i+1:02d} •</small></a>'
 h+='</nav><nav class="nav-secondary" aria-label="Expertises et réseaux"><p class="eyebrow">Nos expertises</p>'
 for label,p in SERVICES:h+=f'<a href="{url(p)}">{label}</a>'
 h+='<p class="eyebrow">Retrouvons-nous</p><a href="https://www.instagram.com/anekdotefr/" target="_blank" rel="noopener">Instagram</a><a href="https://linkedin.com/company/anekdote-influence" target="_blank" rel="noopener">LinkedIn</a><p class="eyebrow">29 rue de Mogador<br>75009 Paris</p></nav></div></dialog>'
 return h

def footer():
 h='<footer class="site-footer"><div class="footer-top"><span class="eyebrow">Embarquez dans l’aventure Anekdote !</span><span class="eyebrow">Paris, 75009</span></div><a href="'+url('contact')+'" class="footer-invitation"><h2>Un café ?</h2><span class="circle-link" aria-hidden="true">↗</span></a><div class="footer-grid"><div><p class="eyebrow">Localisation</p><p>29 rue de Mogador,<br>75009 Paris</p><a href="'+url('contact')+'">Contactez-nous</a></div><div><p class="eyebrow">L’agence</p>'
 for label,p in [('Agence','agence'),('Projets','hub-projets'),('Équipe','equipe'),('Talents','talents')]:h+=f'<a href="{url(p)}">{label}</a>'
 h+='</div><div><p class="eyebrow">Expertises</p>'
 for label,p in SERVICES:h+=f'<a href="{url(p)}">{label}</a>'
 h+='</div><div><p class="eyebrow">Suivez-nous</p><a href="https://www.instagram.com/anekdotefr/" target="_blank" rel="noopener">Instagram</a><a href="https://linkedin.com/company/anekdote-influence" target="_blank" rel="noopener">LinkedIn</a><p class="eyebrow" style="margin-top:25px">Légal</p><a href="'+url('mentions-legales')+'">Mentions légales</a><a href="'+url('politique-de-confidentialite')+'">Confidentialité</a></div></div><div class="footer-bottom"><span>© Anekdote</span><span class="footer-partner">En partenariat avec <img src="'+asset(BASE+'/wp-content/uploads/2023/11/logo-arpp.png')+'" alt="ARPP et UMICC" width="216" height="28" loading="lazy"></span><button class="back-top" data-top>Retour en haut ↑</button></div><div class="footer-brand" aria-hidden="true"><img src="'+asset(BASE+'/wp-content/uploads/2023/11/logo-anekdote.svg')+'" alt="" width="1162" height="270" loading="lazy"></div></footer>'
 return h

def write(path,body,title,description,active='',schema=None):
 global page;assert page==path
 canonical=BASE+'/'+('' if path=='index.html' else str(Path(path).parent)+'/')
 css=''.join(f'<link rel="stylesheet" href="{rel("css/"+x+".css")}">' for x in ['fonts','variables','reset','typography','layout','components','animations','responsive','editorial'])+'<noscript><link rel="stylesheet" href="'+rel('css/no-script.css')+'"></noscript>'
 scripts=''.join(f'<script defer src="{rel("js/"+x+".js")}"></script>' for x in ['navigation','animations','projects','main','editorial']+(['contact'] if active=='contact' else []))
 meta='<meta name="description" content="'+esc(description)+'"><link rel="canonical" href="'+canonical+'"><meta property="og:title" content="'+esc(title)+'"><meta property="og:description" content="'+esc(description)+'"><meta property="og:type" content="website"><meta property="og:url" content="'+canonical+'">'
 s={'@context':'https://schema.org','@type':'Organization','name':'Anekdote','url':BASE,'address':{'@type':'PostalAddress','streetAddress':'29 rue de Mogador','postalCode':'75009','addressLocality':'Paris','addressCountry':'FR'},'sameAs':['https://www.instagram.com/anekdotefr/','https://linkedin.com/company/anekdote-influence']}
 if schema:s=schema
 modal='<dialog id="video-dialog" class="video-dialog" aria-label="Vidéo"><div class="video-dialog-top"><span data-video-title>Le film Anekdote</span><button class="video-dialog-close" data-video-close>Fermer ×</button></div><video playsinline controls preload="none"></video></dialog>'
 output='<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#f4f2eb"><title>'+esc(title)+'</title>'+meta+css+'<link rel="icon" href="'+rel('assets/brand/favicon.svg')+'" type="image/svg+xml"><script type="application/ld+json">'+json.dumps(s,ensure_ascii=False).replace('</','<'+chr(92)+'/')+'</script>'+scripts+'</head><body>'+header(active)+'<main id="main">'+body+'</main>'+footer()+modal+'</body></html>'
 dest=ROOT/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(output);route_manifest.append({'path':path,'source':canonical,'title':title})


def deck(slides,label,cls=''):
 # Content is readable without JavaScript. Inert inactive slides are added on enhancement.
 h='<div class="deck '+cls+'" data-deck role="region" aria-roledescription="carrousel" aria-label="'+esc(label)+'"><div class="deck-stage">'
 for i,(title,body) in enumerate(slides):
  h+='<article class="deck-slide'+(' active' if i==0 else '')+'" data-slide role="group" aria-label="'+str(i+1)+' sur '+str(len(slides))+'"><p class="eyebrow deck-label">'+str(i+1).zfill(2)+' • '+esc(title)+'</p>'+body+'</article>'
 h+='</div><div class="deck-controls"><div class="deck-tabs" aria-label="Choisir une page">'
 for i,(title,body) in enumerate(slides):
  h+='<button type="button" data-deck-go="'+str(i)+'" aria-label="'+esc(title)+', page '+str(i+1)+'" aria-pressed="'+('true' if i==0 else 'false')+'">'+str(i+1).zfill(2)+'</button>'
 h+='</div><div class="deck-arrows"><span class="deck-status" aria-live="polite" aria-atomic="true" data-deck-status>1 / '+str(len(slides))+'</span><button type="button" data-deck-prev aria-label="Page précédente">←</button><button type="button" data-deck-next aria-label="Page suivante">→</button></div></div></div>'
 return h

def accordion(cls=''):
 h='<div class="expertise-accordion '+cls+'">'
 for i,(label,key) in enumerate(SERVICES):
  desc=text(soup(key).select_one('.page-header-banner-baseline'))
  h+='<details'+(' open' if i==0 else '')+'><summary><span class="eyebrow">'+str(i+1).zfill(2)+' •</span><h3>'+label+'</h3><span class="accordion-symbol" aria-hidden="true">+</span></summary><div class="expertise-answer"><p>'+esc(desc)+'</p>'+link('Découvrir cette expertise',key)+'</div></details>'
 return h+'</div>'

def client_marquees():
 ho=soup('');sources=[]
 for im in ho.select('#content img'):
  u=im.get('src','')
  if 'logo-' in u and u not in sources and 'anekdote' not in u.split('/')[-1] and 'arpp' not in u:sources.append(u)
 h='<div class="marquee" data-marquee><div class="marquee-controls"><span class="eyebrow">Ils nous font confiance</span><button type="button" data-marquee-toggle aria-pressed="false">Pause <span aria-hidden="true">Ⅱ</span></button></div>'
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
  if text(x)=='Une Anekdote ?':x.decompose()
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
 global page;page='index.html';ag=soup('agence');ho=soup('');showreel=ho.select_one('source')['src'];ghd=DATA['projects'][3]
 b='<section class="masthead"><div class="masthead-meta"><p class="eyebrow">Agence de conseil<br>Marketing d’influence & Brand Content</p></div><h1 class="wordmark" aria-label="Anekdote">Anek<span class="italic">dote</span><span class="dot">.</span></h1></section>'
 b+='<section class="company-stage">'+picture(bg(ag.select_one('.page-header-banner-container')),'L’équipe Anekdote dans un escalier parisien',eager=True)+'<div class="company-overlay"><p class="eyebrow">01 • Enchanté !</p><h2>Nous créons<br>vos <span class="italic">campagnes.</span></h2><div class="company-actions">'+link('L’agence','agence')+'<button type="button" class="film-link" data-video-open="'+asset(showreel)+'" data-title="Le film Anekdote">Le film <span aria-hidden="true">▷</span></button></div></div></section>'
 b+='<section class="section home-services"><div class="home-services-heading"><div><p class="eyebrow">02 • Nos expertises</p><h2 class="section-title">L’idée.<br><span class="italic">Puis l’action.</span></h2></div><p class="lead">Nous créons vos campagnes pour accélérer votre notoriété et optimiser votre conversion.</p></div>'+accordion('home-accordion')+'</section>'
 b+='<section class="section clients"><div class="client-intro"><h2>Nous vous adorons,<br><span class="italic">c’est réciproque.</span></h2><p>Nous avons plus de 50 partenaires qui nous font confiance dans la beauté, la mode, la tech/app, la food et le retail.</p></div>'+client_marquees()+'</section>'
 b+='<section class="section home-agency"><div class="home-agency-photo media-frame reveal">'+picture(BASE+'/wp-content/uploads/2024/09/Design-sans-titre-3.png','Un moment partagé par l’équipe Anekdote')+'</div><div class="home-agency-copy"><p class="eyebrow">03 • L’esprit d’équipe</p><h2 class="section-title">Une équipe<br><span class="italic">passionnée.</span></h2><p class="lead">L’échange est notre moteur, le partage est notre super-force, et la positivité est notre arme secrète.</p><div class="home-agency-links">'+link('Rencontrer l’équipe','equipe')+link('Notre histoire','agence')+'</div></div></section>'
 b+='<section class="section proof"><div class="proof-copy"><p class="eyebrow">04 • Les résultats</p><h2 class="section-title">La créativité.<br><span class="italic">Et son impact.</span></h2><p>Une équipe passionnée pour des campagnes sur-mesure et performantes.</p>'+link('Découvrir nos projets','hub-projets')+'</div><div class="proof-kpis">'
 for v,l,p,number,decimals,suffix,separator in [('7.2M','de vues au total',ghd,7.2,1,'M','.'),('1,73 M','de reach',DATA['projects'][1],1.73,2,' M',','),('31 377','clics sur lien',DATA['projects'][0],31377,0,'',' ')]:
  b+='<a class="proof-row" href="'+url(p['path'])+'"><strong><span class="sr-only">'+v+'</span><span aria-hidden="true" data-count="'+str(number)+'" data-decimals="'+str(decimals)+'" data-suffix="'+suffix+'" data-separator="'+separator+'">'+v+'</span></strong><p>'+l+'<span>'+esc(p['title'])+'</span></p></a>'
 b+='</div></section>'
 write(page,b,PAGES[BASE+'/']['title'],PAGES[BASE+'/']['description'],'')

def agency():
 global page;page='agence/index.html';s=soup('agence');m=s.select_one('#content');sections={text(h):h.parent for h in m.select('h2')}
 b='<section class="agency-intro page-intro"><p class="eyebrow">01 • Anekdote</p><div class="editorial-heading"><h1 class="display">L’<span class="italic">agence.</span></h1><p class="lead">'+esc(text(s.select_one('.page-header-banner-baseline')))+'</p></div></section>'
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
 b+='<section class="agency-about wrap"><div class="agency-photo media-frame">'+picture(bg(s.select_one('.page-header-banner-container')),'L’équipe Anekdote',eager=True)+'</div>'+deck(slides,'L’histoire et les engagements Anekdote','agency-deck')+'</section>'
 q=sections['Pourquoi Anekdote ?'];paras=q.select('p');b+='<section class="agency-quote"><div><p class="eyebrow">02 • Pourquoi Anekdote ?</p><span class="quote-glyph" aria-hidden="true">“</span></div><blockquote>'+''.join(clean(str(x)) for x in paras[:2])+'<footer>Christelle, Co-Founder</footer></blockquote></section>'
 manifest=sections['Manifeste'];slides=[]
 for item in manifest.select('.agence-manifeste-text'):
  h=item.select_one('h3');copy=item.select_one('p');slides.append(('Manifeste','<h3>'+esc(text(h))+'</h3><p>'+esc(text(copy))+'</p>'))
 b+='<section class="manifest-section section"><div class="manifest-heading"><p class="eyebrow">03 • Notre manifeste</p><h2>Ce qui nous<br><span class="italic">anime.</span></h2></div>'+deck(slides,'Le manifeste Anekdote','manifest-deck')+'</section>'
 b+='<div class="agency-outro wrap">'+link('Notre équipe','equipe')+link('Nos engagements','rse-corporate')+'</div>'
 write(page,b,PAGES[BASE+'/agence/']['title'],PAGES[BASE+'/agence/']['description'],'agence')

def portfolio():
 global page;page='hub-projets/index.html';s=soup('hub-projets');b=hero_intro('Nos <span class="italic">projets.</span>','02 • Nos expertises en action',text(s.select_one('.page-header-banner-baseline')))
 b+='<div class="project-filters" data-filters role="group" aria-label="Filtrer les projets par expertise"><button type="button" data-filter="all" aria-pressed="true">Tous les projets</button>'
 for label,_ in SERVICES:b+='<button type="button" data-filter="'+esc(label if label!='Campagne d’influence' else "Campagne d'influence")+'" aria-pressed="false">'+label+'</button>'
 b+='<span class="project-count" data-project-count role="status">'+str(len(DATA['projects']))+' projets</span></div><section class="portfolio" aria-label="Portfolio">'
 for i,p in enumerate(DATA['projects']):b+=project_item(p,i,True)
 b+='</section><p class="empty-filter" data-empty-projects hidden>Aucun projet pour cette expertise.</p>'
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
   b+='</div></div><div class="kpi-grid">'
   for k in p['kpis']:b+='<div class="kpi'+(' long' if len(k['value'])>8 else '')+'"><strong>'+esc(k['value'])+'</strong><span>'+esc(k['label'])+'</span></div>'
   b+='</div></section>'
  extras=list(dict.fromkeys(p['extra']))
  if extras:b+='<section class="case-extra prose">'+''.join('<p>'+esc(x)+'</p>' for x in extras)+'</section>'
  if len(p['media'])>len(chapters):
   b+='<section class="case-gallery" aria-label="Contenus de la campagne">'
   for med in p['media'][len(chapters):]:b+=media_video(med['src'],p['title']) if MAP[med['src']]['path'].endswith('.mp4') else '<div class="media-frame">'+picture(med['src'],med['alt'])+'</div>'
   b+='</section>'
  nxt=DATA['projects'][(i+1)%len(DATA['projects'])];b+='<a class="next-project" href="'+url(nxt['path'])+'">'+picture(nxt['thumbnail'],nxt['title'])+'<div><p class="eyebrow">Le projet suivant</p><h2>'+esc(nxt['title'])+'</h2></div></a>'
  schema={'@context':'https://schema.org','@type':'CreativeWork','name':p['title'],'description':p['description'],'creator':{'@type':'Organization','name':'Anekdote'},'url':p['url']}
  write(page,b,PAGES[p['url']]['title'],desc,'hub-projets',schema)

def expertises():
 global page;page='expertises/index.html'
 b='<section class="page-intro expertise-intro"><p class="eyebrow">01 • Nos expertises</p><div class="editorial-heading"><h1 class="display">L’idée.<br><span class="italic">Puis l’action.</span></h1><p class="lead">Une équipe passionnée pour des campagnes sur-mesure et performantes.</p></div></section>'
 b+='<section class="expertise-overview wrap"><h2 class="sr-only">Nos expertises</h2><figure class="expertise-new-photo media-frame">'+picture(DATA['projects'][6]['hero'],'Activation influence Anekdote — Festival de Cannes x Soskin',eager=True)+'<figcaption class="eyebrow">L’influence, sur le terrain.</figcaption></figure>'+accordion()+'</section>'
 write(page,b,'Anekdote | Nos expertises en influence et création','Campagne d’influence, stratégie, évènements, Brand Content, RSE / Corporate, Performance / Affiliation.','expertises')
 for i,(label,key) in enumerate(SERVICES):
  page=key+'/index.html';s=soup(key);m=s.select_one('#content');b=hero_intro(esc(text(s.h1))+'<span class="orange">.</span>',str(i+1).zfill(2)+' • Nos expertises',text(s.select_one('.page-header-banner-baseline')),True)
  b+='<div class="page-visual">'+picture(bg(s.select_one('.page-header-banner-container')),label,eager=True)+'</div>'
  for c in m.select('.bloc-column-text'):
   h=c.find('h2');title=text(h) or 'Solar Metrics';b+='<section class="story-section reveal"'+(' id="coaching"' if key=='performance-affiliation' else '')+'><div><p class="eyebrow">Notre expertise</p><h2>'+esc(title)+'</h2></div><div class="prose">'+inner(c,True)+'</div></section>'
  med=m.select_one('.bloc-column-visual source,.bloc-column-visual img')
  if med and med.get('src') in MAP:b+='<section class="section">'+(media_video(med['src'],label) if MAP[med['src']]['path'].endswith('.mp4') else '<div class="page-visual">'+picture(med['src'],label)+'</div>')+'</section>'
  # Preserve source-selected project relationships before adding category matching.
  related=[]
  for c in m.select('.page-project-container a[href]'):
   p=next((x for x in DATA['projects'] if x['url'].rstrip('/')==c['href'].rstrip('/')),None)
   if p and p not in related:related.append(p)
  if not related:related=[x for x in DATA['projects'] if label in x['categories'] or label.replace('’',"'") in x['categories']][:2]
  if related:b+='<section class="section">'+section_top(2,'Les derniers projets','Nos expertises en action')+'<div class="featured-pair">'+''.join(project_item(x,j) for j,x in enumerate(related))+'</div></section>'
  write(page,b,PAGES[BASE+'/'+key+'/']['title'],PAGES[BASE+'/'+key+'/']['description'],'expertises')

def team():
 global page;page='equipe/index.html';s=soup('equipe')
 b=hero_intro('L’équipe <span class="italic">Anekdote.</span>','01 • #TeamAnekdote',text(s.select_one('.page-header-banner-baseline')))
 spirit=s.select_one('.bloc-column-text');im=s.select_one('.bloc-column-visual img')
 b+='<section class="team-spirit"><div><h2 class="section-title">L’esprit<br><span class="italic">d’équipe.</span></h2><div class="prose">'+inner(spirit,True)+'</div></div><div class="media-frame">'+picture(im['src'],'Un moment partagé par l’équipe Anekdote',eager=True)+'</div></section><section class="team-people">'
 for i,t in enumerate(DATA['team']):
  key='person-'+str(i+1);an=BeautifulSoup(t['anecdote'],'html.parser');lists=an.select('ul');groups=[[text(li) for li in ul.select('li')] for ul in lists]
  overlay=''
  if groups:
   for j,items in enumerate(groups[:2]):
    overlay+='<div class="taste-group"><h3>'+('J’aime' if j==0 else 'Je n’aime pas')+'</h3><ul>'
    for item in items:overlay+='<li>'+heart(j==1)+'<span>'+esc(item)+'</span></li>'
    overlay+='</ul></div>'
  else:
   # Christelle has no published preference lists: keep her real anecdote, without inventing tastes.
   overlay='<div class="photo-anecdote"><p class="eyebrow">Une Anekdote</p>'+clean(str(an.select_one('p')))+'</div>'
  b+='<article class="person reveal" id="'+key+'"><div class="person-photo"><div class="person-portrait media-frame">'+picture(t['portrait'],t['name']+' — portrait Anekdote',sizes='(max-width: 800px) 90vw, 45vw')+'<div class="photo-tastes" id="'+key+'-tastes">'+overlay+'</div><button type="button" class="taste-toggle" data-tastes-toggle aria-controls="'+key+'-tastes" aria-expanded="false">'+heart()+'<span>'+('J’aime / Je n’aime pas' if groups else 'Une Anekdote')+'</span></button></div><div class="person-index"><span class="eyebrow">#TeamAnekdote</span><span class="eyebrow">'+str(i+1).zfill(2)+' •</span></div></div><div class="person-story"><header class="person-heading"><h2>'+esc(t['name'])+'</h2><span class="eyebrow person-view-label" data-person-label>Le portrait</span></header><div class="person-content" id="'+key+'-content"><div data-person-bio>'
  chunks=bio_chunks(t['bio'])
  if len(chunks)>1:b+=deck([('Le portrait','<div class="prose">'+x+'</div>') for x in chunks],'Le portrait de '+t['name'],'bio-deck')
  else:b+='<div class="prose">'+chunks[0]+'</div>'
  b+='</div><div class="prose person-anecdote" data-person-anecdote hidden>'+portrait_content(t['anecdote'])+(picture(BASE+'/wp-content/uploads/2023/11/Group-1798.svg','Les deux mantras de Christelle') if t['name']=='Christelle' else '')+'</div></div><button class="person-toggle text-link" type="button" data-person-toggle aria-controls="'+key+'-content" aria-pressed="false"><span>Une Anekdote</span><span class="link-symbol" aria-hidden="true">↗</span></button></div></article>'
 b+='</section>';write(page,b,PAGES[BASE+'/equipe/']['title'],PAGES[BASE+'/equipe/']['description'],'equipe')

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
 global page;page='contact/index.html';s=soup('contact');b=hero_intro('Un <span class="italic">café ?</span>','07 • Contactez-nous',text(s.select_one('.page-header-banner-baseline')))
 b+='<section class="contact-layout"><aside class="contact-aside"><div class="media-frame">'+picture(bg(s.select_one('.page-header-banner-container')),'Le rooftop Anekdote — Paris',eager=True)+'</div><p class="eyebrow">29 rue de Mogador • 75009 Paris</p><p class="annotation">On a hâte d’écouter vos projets.</p></aside><form class="contact-form" data-contact-form data-endpoint="https://www.anekdote.fr/wp-json/contact-form-7/v1/contact-forms/547/feedback" action="https://www.anekdote.fr/contact/#wpcf7-f547-o1" method="post"><input type="hidden" name="_wpcf7" value="547"><input type="hidden" name="_wpcf7_version" value="6.1.6"><input type="hidden" name="_wpcf7_locale" value="fr_FR"><input type="hidden" name="_wpcf7_unit_tag" value="wpcf7-f547-o1"><input type="hidden" name="_wpcf7_container_post" value="0"><input type="hidden" name="_wpcf7_posted_data_hash" value=""><div class="form-progress"><span data-step-indicator class="active"><b>01</b> Une boisson</span><span data-step-indicator><b>02</b> Un endroit</span><span data-step-indicator><b>03</b> Rencontrons-nous</span></div><section class="form-step" data-step="0"><h2 tabindex="-1">Quelle est votre<br><span class="italic">boisson préférée ?</span></h2><fieldset class="choice-grid"><legend class="sr-only">Choisissez une boisson</legend>'
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
