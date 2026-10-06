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
 s=BeautifulSoup(content or '','html.parser')
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
 return f'<div class="section-top"><span class="eyebrow">/{n:02d} — {title}</span><span class="eyebrow">{end}</span></div>'
def media_video(source,title):
 info=MAP[source];poster=info.get('poster');
 return '<figure class="media-frame video-figure">'+f'<video controls playsinline preload="none" data-lazy-video aria-label="{esc(title)}"'+(f' poster="{esc(localpath(poster))}"' if poster else '')+f'><source src="{esc(asset(source))}" type="video/mp4">Votre navigateur ne prend pas en charge les vidéos. <a href="{esc(asset(source))}">Télécharger la vidéo</a></video></figure>'
def project_item(p,i=0,attrs=False):
 cats=' / '.join(p['categories']);stat=p['kpis'][0] if p['kpis'] else None
 if 'Stratégie Tiktok x ' in p['title']:
  client=p['title'].split('Stratégie Tiktok x ')[-1]
  stat=next((k for k in p['kpis'] if client.lower() in k['label'].lower()),stat)
 return f'<article class="project-item reveal"'+(f' data-project data-categories="{esc(json.dumps(p["categories"],ensure_ascii=False))}"' if attrs else '')+'>'+f'<a href="{esc(url(p["path"]))}"><div class="media-frame">{picture(p["thumbnail"],p["title"],sizes="(max-width: 800px) 100vw, 50vw")}</div><h3>{esc(p["title"])}</h3><div class="project-meta"><span>{esc(cats)}</span><span>/{i+1:02d}</span></div>'+ (f'<p class="inline-stat">{esc(stat["value"])} {esc(stat["label"])}</p>' if stat else '')+'</a></article>'
def hero_intro(title,kicker,description='',serif=False):
 return f'<section class="page-intro"><p class="eyebrow">{kicker}</p><h1 class="display{ " serif" if serif else ""}">{title}</h1>'+ (f'<p class="lead">{description}</p>' if description else '')+'</section>'
def header(active):
 nav=[('Agence','agence'),('Projets','hub-projets'),('Expertises','expertises'),('Newsroom','newsroom')]
 h='<a class="skip-link" href="#main">Aller au contenu</a><div class="reading-progress" aria-hidden="true"></div><header class="site-header"><a class="logo" href="'+url()+'" aria-label="Anekdote, accueil"><img src="'+asset(BASE+'/wp-content/uploads/2023/11/logo-anekdote.svg')+'" alt="Anekdote" width="145" height="34"></a><nav class="desktop-nav" aria-label="Navigation principale">'
 for label,p in nav:h+=f'<a href="{url(p)}"'+(' aria-current="page"' if active==p else '')+'>'+label+'</a>'
 h+='</nav><div class="header-actions"><a class="coffee" href="'+url('contact')+'">Un café ?</a><button class="menu-toggle" aria-controls="navigation-dialog" aria-expanded="false" aria-label="Ouvrir le menu" data-menu-open><span>Menu</span><span class="menu-icon" aria-hidden="true"><i></i><i></i></span></button></div></header>'
 h+='<dialog class="nav-dialog" id="navigation-dialog" aria-label="Navigation"><div class="nav-dialog-head"><a class="logo" href="'+url()+'"><img src="'+asset(BASE+'/wp-content/uploads/2023/11/logo-anekdote.svg')+'" alt="Anekdote" width="145" height="34"></a><button class="nav-close" data-menu-close>Fermer ×</button></div><div class="nav-grid"><nav class="nav-primary" aria-label="Toutes les pages">'
 for i,(label,p) in enumerate([('Accueil',''),('Agence','agence'),('Projets','hub-projets'),('Expertises','expertises'),('Équipe','equipe'),('Talents','talents'),('Newsroom','newsroom'),('Contact','contact')]):h+=f'<a href="{url(p)}">{label}<small>/{i+1:02d}</small></a>'
 h+='</nav><nav class="nav-secondary" aria-label="Expertises et réseaux"><p class="eyebrow">Nos expertises</p>'
 for label,p in SERVICES:h+=f'<a href="{url(p)}">{label}</a>'
 h+='<p class="eyebrow">Retrouvons-nous</p><a href="https://www.instagram.com/anekdotefr/" target="_blank" rel="noopener">Instagram</a><a href="https://linkedin.com/company/anekdote-influence" target="_blank" rel="noopener">LinkedIn</a><p class="eyebrow">4 rue Jules Lefebvre<br>Paris 75009</p></nav></div></dialog>'
 return h

def footer():
 h='<footer class="site-footer"><div class="footer-top"><span class="eyebrow">Embarquez dans l’aventure Anekdote !</span><span class="eyebrow">Paris, 75009</span></div><a href="'+url('contact')+'" class="footer-invitation"><h2>Un café ?</h2><span class="circle-link" aria-hidden="true">↗</span></a><div class="footer-grid"><div><p class="eyebrow">Localisation</p><p>4 rue Jules Lefebvre,<br>Paris 75009</p><a href="'+url('contact')+'">Contactez-nous</a></div><div><p class="eyebrow">L’agence</p>'
 for label,p in [('Agence','agence'),('Projets','hub-projets'),('Équipe','equipe'),('Talents','talents'),('Newsroom','newsroom')]:h+=f'<a href="{url(p)}">{label}</a>'
 h+='</div><div><p class="eyebrow">Expertises</p>'
 for label,p in SERVICES:h+=f'<a href="{url(p)}">{label}</a>'
 h+='</div><div><p class="eyebrow">Suivez-nous</p><a href="https://www.instagram.com/anekdotefr/" target="_blank" rel="noopener">Instagram</a><a href="https://linkedin.com/company/anekdote-influence" target="_blank" rel="noopener">LinkedIn</a><p class="eyebrow" style="margin-top:25px">Légal</p><a href="'+url('mentions-legales')+'">Mentions légales</a><a href="'+url('politique-de-confidentialite')+'">Confidentialité</a></div></div><div class="footer-bottom"><span>© Anekdote</span><span class="footer-partner">En partenariat avec <img src="'+asset(BASE+'/wp-content/uploads/2023/11/logo-arpp.png')+'" alt="ARPP et UMICC" width="84" height="32" loading="lazy"></span><button class="back-top" data-top>Retour en haut ↑</button></div><p class="footer-brand" aria-hidden="true">ANEKDOTE.</p></footer>'
 return h

def write(path,body,title,description,active='',schema=None):
 global page;assert page==path
 canonical=BASE+'/'+('' if path=='index.html' else str(Path(path).parent)+'/')
 css=''.join(f'<link rel="stylesheet" href="{rel("css/"+x+".css")}">' for x in ['fonts','variables','reset','typography','layout','components','animations','responsive'])
 scripts=''.join(f'<script defer src="{rel("js/"+x+".js")}"></script>' for x in ['navigation','animations','projects','main']+(['contact'] if active=='contact' else []))
 meta='<meta name="description" content="'+esc(description)+'"><link rel="canonical" href="'+canonical+'"><meta property="og:title" content="'+esc(title)+'"><meta property="og:description" content="'+esc(description)+'"><meta property="og:type" content="website"><meta property="og:url" content="'+canonical+'">'
 s={'@context':'https://schema.org','@type':'Organization','name':'Anekdote','url':BASE,'address':{'@type':'PostalAddress','streetAddress':'4 rue Jules Lefebvre','postalCode':'75009','addressLocality':'Paris','addressCountry':'FR'},'sameAs':['https://www.instagram.com/anekdotefr/','https://linkedin.com/company/anekdote-influence']}
 if schema:s=schema
 modal='<dialog id="video-dialog" class="video-dialog" aria-label="Vidéo"><div class="video-dialog-top"><span data-video-title>Le film Anekdote</span><button class="video-dialog-close" data-video-close>Fermer ×</button></div><video playsinline controls preload="none"></video></dialog>'
 output='<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#f4f2eb"><title>'+esc(title)+'</title>'+meta+css+'<link rel="icon" href="'+rel('assets/brand/favicon.svg')+'" type="image/svg+xml"><script type="application/ld+json">'+json.dumps(s,ensure_ascii=False).replace('</','<'+chr(92)+'/')+'</script>'+scripts+'</head><body>'+header(active)+'<main id="main">'+body+'</main>'+footer()+modal+'</body></html>'
 dest=ROOT/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(output);route_manifest.append({'path':path,'source':canonical,'title':title})

def home():
 global page;page='index.html';ghd=DATA['projects'][3];big=DATA['projects'][5];soskin=DATA['projects'][6];az=DATA['projects'][8];te=soup('equipe');ho=soup('');ag=soup('agence');showreel=ho.select_one('source')['src']
 b='<section class="masthead"><div class="masthead-meta"><p class="eyebrow">Agence de conseil<br>Marketing d’influence & Brand Content</p><p class="eyebrow">Paris — 75009<br>Une équipe passionnée</p></div><h1 class="wordmark" aria-label="Anekdote">Anek<span class="italic">dote</span><span class="dot">.</span></h1></section>'
 b+='<section class="hero-stage"><a href="'+url(ghd['path'])+'" aria-label="Découvrir Concert Aya Nakamura x GHD x Juliette Has A Gun">'+picture(ghd['hero'],ghd['title'],eager=True)+'</a><div class="hero-overlay"><p class="eyebrow">GHD × Juliette Has a Gun · Évènements</p><div class="hero-overlay-bottom"><div><h2>Une expérience beauté<br><span class="italic">100% immersive.</span></h2><p class="hero-caption">Concert Aya Nakamura — Stade de France</p></div><span class="hero-open" aria-hidden="true">↗</span></div></div></section>'
 b+='<div class="hero-footnote"><p>Une équipe passionnée pour des campagnes<br>sur-mesure et performantes.</p><button class="text-link" style="min-width:0;padding:0;border:0;background:none" data-video-open="'+asset(showreel)+'" data-title="Le film Anekdote"><span>Le film Anekdote</span><span aria-hidden="true">▷</span></button></div>'
 b+='<section class="section intro reveal"><div><p class="eyebrow">/01 — Enchanté !</p></div><div><h2 class="section-title">Nous créons<br>vos <span class="italic">campagnes.</span></h2><div class="intro-copy"><p>Nous créons vos campagnes pour accélérer votre notoriété et optimiser votre conversion.</p>'+link('Embarquez avec nous','agence')+'</div></div></section>'
 b+='<section class="section project-editorial">'+section_top(2,'Nos expertises en action','Projets sélectionnés')+'<div class="work-heading"><h2 class="section-title">Des projets.<br><span class="italic">Des histoires.</span></h2>'+link('Tous les projets','hub-projets')+'</div>'
 b+='<a class="project-feature reveal" href="'+url(big['path'])+'"><figure><div class="media-frame">'+picture(big['thumbnail'],big['title'])+'<span class="project-number">/01 — Bpifrance · Big média</span></div><figcaption><h3>Et si le culot s’invitait<br>au <span class="italic">Festival de Cannes ?</span></h3><div><div class="project-caption-right"><span>Évènements</span><span aria-hidden="true">↗</span></div><p class="inline-stat light-stat">1,92M reach · 2,24M impressions</p></div></figcaption></figure></a>'
 b+='<div class="featured-pair">'+project_item(soskin,1)+project_item(az,2)+'</div></section>'
 b+='<section class="section proof reveal"><div class="proof-copy"><p class="eyebrow">/03 — Les résultats</p><h2 class="section-title" style="margin-top:30px">La créativité.<br><span class="italic">Et son impact.</span></h2><p style="margin-top:30px;max-width:360px">Une équipe passionnée pour des campagnes sur-mesure et performantes.</p></div><div class="proof-kpis">'
 for v,l,p in [('7.2M','de vues au total',ghd),('1,73 M','de reach',DATA['projects'][1]),('31 377','clics sur lien',DATA['projects'][0])]:b+='<a class="proof-row" href="'+url(p['path'])+'"><strong>'+v+'</strong><p>'+l+'<span>'+esc(p['title'])+'</span></p></a>'
 b+='</div></section>'
 b+='<section class="section expertise-block">'+section_top(4,'Nos expertises','Un accompagnement sur-mesure')+'<div class="expertise-layout"><div class="expertise-aside"><h2 class="section-title">L’idée.<br><span class="italic">Puis l’action.</span></h2><div class="media-frame">'+picture(bg(ho.select_one('.home-expertises-container')) or BASE+'/wp-content/uploads/2023/12/marcus-x-brand-content-1-min.jpg','Marcus — Brand Content')+'</div></div><ol class="expertise-list">'
 for i,(label,key) in enumerate(SERVICES):
  s=soup(key);desc=text(s.select_one('.page-header-banner-baseline'));b+='<li class="reveal"><a href="'+url(key)+'"><span class="number">/'+str(i+1).zfill(2)+'</span><div><h3>'+label+'</h3><p>'+esc(desc)+'</p></div><span class="plus" aria-hidden="true">+</span></a></li>'
 b+='</ol></div></section>'
 b+='<section class="section clients"><div class="client-intro"><h2>Nous vous adorons,<br><span class="italic">c’est réciproque.</span></h2><p>Nous avons plus de 50 partenaires qui nous font confiance dans la beauté, la mode, la tech/app, la food et le retail.</p></div><div class="client-logos">'
 seen=set()
 for im in ho.select('#content img'):
  u=im.get('src','')
  if 'logo-' in u and u not in seen and not 'anekdote' in u.split('/')[-1] and not 'arpp' in u:
   seen.add(u);label=re.split('-logo',u.split('/')[-1])[0].replace('_','’').replace('-',' ');b+=picture(u,label,sizes='130px')
 b+='</div></section>'
 b+='<section class="section human-home">'+section_top(5,'L’esprit d’équipe','Good vibes')+'<div class="human-grid"><div class="reveal"><div class="media-frame">'+picture(bg(te.select_one('.page-header-banner-container')),'L’équipe Anekdote')+'</div><div class="human-note"><p class="eyebrow">#TeamAnekdote</p><p class="annotation">L’échange est notre moteur.</p></div></div><div class="human-copy reveal"><h2 class="section-title">Une équipe<br><span class="italic">passionnée.</span></h2><p class="lead">L’échange est notre moteur, le partage est notre super-force, et la positivité est notre arme secrète.</p>'+link('Rencontrer l’équipe','equipe')+'</div></div><div class="culture-strip">'
 for src,title,tag,href in [(BASE+'/wp-content/uploads/2024/09/Design-sans-titre-7.png','Avril Dump','#TeamAnekdote','https://www.instagram.com/p/C6ZEPT8L_19/?img_index=1'),(BASE+'/wp-content/uploads/2023/11/paris-2024-anekdote.jpg','Soirée Paris 2024','#JO2024','https://www.instagram.com/p/CxdbJHXs-Nk/?hl=fr&img_index=1')]:b+='<a href="'+href+'" target="_blank" rel="noopener" class="reveal"><div class="media-frame">'+picture(src,title)+'</div><p class="eyebrow">'+tag+'</p><h3>'+title+'</h3></a>'
 b+='</div></section><section class="section news-home">'+section_top(6,'Anekdote — Newsroom','Actualités de l’agence')+'<div class="news-heading"><h2 class="section-title">Ce qui nous<br><span class="italic">anime.</span></h2>'+link('Toute la Newsroom','newsroom')+'</div><ol class="news-list">'
 for i,n in enumerate(DATA['news'][:3]):b+='<li class="reveal"><a href="'+url('newsroom/'+n['slug'])+'"><div class="media-frame">'+picture(n['image'],n['title'],sizes='180px')+'</div><div><h3>'+esc(n['title'])+'</h3><p class="eyebrow">Newsroom · Anekdote</p></div><span class="number">/'+str(i+1).zfill(2)+'</span></a></li>'
 b+='</ol></section>'
 write(page,b,PAGES[BASE+'/']['title'],PAGES[BASE+'/']['description'],'')

def agency():
 global page;page='agence/index.html';s=soup('agence');m=s.select_one('#content');b=hero_intro('L’agence<span class="orange">.</span>','/01 — Anekdote',text(s.select_one('.page-header-banner-baseline')),True)
 b+='<div class="page-visual">'+picture(bg(s.select_one('.page-header-banner-container')),'Anekdote — l’agence',eager=True)+'</div>'
 for i,h in enumerate(m.select('h2')):
  title=text(h)
  if title=='Pourquoi Anekdote ?':
   b+='<section class="agency-quote"><p class="eyebrow">Pourquoi Anekdote ?</p><blockquote>'+inner(h.parent,True)+'</blockquote></section>';continue
  b+='<section class="story-section reveal"><div><p class="eyebrow">/'+str(i+1).zfill(2)+'</p><h2>'+esc(title)+'</h2></div><div class="prose">'+inner(h.parent,True)+'</div></section>'
 b+='<section class="section"><div class="human-grid">'
 for im in m.select('.bloc-column-visual img')[:2]:b+='<div class="media-frame reveal">'+picture(im['src'],'La vie de l’agence Anekdote')+'</div>'
 b+='</div><div class="divider-label">'+link('Notre équipe','equipe')+link('Nos engagements','rse-corporate')+'</div></section>'
 write(page,b,PAGES[BASE+'/agence/']['title'],PAGES[BASE+'/agence/']['description'],'agence')

def portfolio():
 global page;page='hub-projets/index.html';s=soup('hub-projets');b=hero_intro('Nos <span class="italic">projets.</span>','/02 — Nos expertises en action',text(s.select_one('.page-header-banner-baseline')))
 b+='<div class="project-filters" data-filters role="group" aria-label="Filtrer les projets par expertise"><button type="button" data-filter="all" aria-pressed="true">Tous les projets</button>'
 for label,_ in SERVICES:b+='<button type="button" data-filter="'+esc(label if label!='Campagne d’influence' else "Campagne d'influence")+'" aria-pressed="false">'+label+'</button>'
 b+='<span class="project-count" data-project-count role="status">'+str(len(DATA['projects']))+' projets</span></div><section class="portfolio" aria-label="Portfolio">'
 for i,p in enumerate(DATA['projects']):b+=project_item(p,i,True)
 b+='</section><p class="empty-filter" data-empty-projects hidden>Aucun projet pour cette expertise.</p>'
 write(page,b,PAGES[BASE+'/hub-projets/']['title'],PAGES[BASE+'/hub-projets/']['description'],'hub-projets')

def cases():
 global page
 for i,p in enumerate(DATA['projects']):
  page=p['path']+'/index.html';desc=PAGES[p['url']]['description'];b='<section class="page-intro case-intro"><nav class="breadcrumbs" aria-label="Fil d’Ariane"><a href="'+url()+'">Anekdote</a><span>/</span><a href="'+url('hub-projets')+'">Projets</a></nav><p class="eyebrow">'+esc(' / '.join(p['categories']))+'</p><h1 class="display">'+esc(p['h1'])+'</h1><div class="case-meta"><span>'+esc(p['title'])+'</span><span>Anekdote · Étude de cas /'+str(i+1).zfill(2)+'</span></div></section>'
  b+='<div class="case-hero">'+picture(p['hero'],p['title'],eager=True)+'</div>'
  if p['description']:b+='<section class="case-description"><p class="eyebrow">Le projet</p><p class="lead">'+esc(p['description'])+'</p></section>'
  chapters=[x for x in p['sections'] if x['title']!='Les résultats'];result=next((x for x in p['sections'] if x['title']=='Les résultats'),None);b+='<div class="case-body">'
  for j,c in enumerate(chapters):
   med=p['media'][j] if j<len(p['media']) else None
   b+='<section class="case-chapter reveal'+(' no-visual' if not med else '')+'"><div class="chapter-heading"><p class="eyebrow">/'+str(j+1).zfill(2)+'</p><h2>'+esc(c['title'])+'</h2></div><div class="prose">'+clean(c['html'],True)+'</div>'
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
 global page;page='expertises/index.html';b=hero_intro('Nos <span class="italic">expertises.</span>','/03 — Anekdote')+'<section class="section expertise-layout"><div class="expertise-aside"><p class="lead">Une équipe passionnée pour des campagnes sur-mesure et performantes.</p><div class="media-frame">'+picture(BASE+'/wp-content/uploads/2023/12/marcus-x-brand-content-1-min.jpg','Marcus — Brand Content')+'</div></div><ol class="expertise-list">'
 for i,(label,key) in enumerate(SERVICES):
  s=soup(key);b+='<li class="reveal"><a href="'+url(key)+'"><span class="number">/'+str(i+1).zfill(2)+'</span><div><h3>'+label+'</h3><p>'+esc(text(s.select_one('.page-header-banner-baseline')))+'</p></div><span class="plus" aria-hidden="true">+</span></a></li>'
 b+='</ol></section>';write(page,b,'Anekdote | Nos expertises en influence et création','Campagne d’influence, stratégie, évènements, Brand Content, RSE / Corporate, Performance / Affiliation.','expertises')
 for i,(label,key) in enumerate(SERVICES):
  page=key+'/index.html';s=soup(key);m=s.select_one('#content');b=hero_intro(esc(text(s.h1))+'<span class="orange">.</span>','/0'+str(i+1)+' — Nos expertises',text(s.select_one('.page-header-banner-baseline')),True)
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
 global page;page='equipe/index.html';s=soup('equipe');b=hero_intro('L’équipe<br><span class="italic">Anekdote.</span>','/04 — #TeamAnekdote',text(s.select_one('.page-header-banner-baseline')))+'<div class="page-visual">'+picture(bg(s.select_one('.page-header-banner-container')),'L’équipe Anekdote',eager=True)+'</div>'
 spirit=s.select_one('.bloc-column-text');im=s.select_one('.bloc-column-visual img');b+='<section class="team-spirit"><div><h2 class="section-title">L’esprit<br><span class="italic">d’équipe.</span></h2><div class="prose">'+inner(spirit,True)+'</div></div><div class="media-frame">'+picture(im['src'],'Un moment partagé par l’équipe Anekdote')+'</div></section><section class="team-people">'
 for i,t in enumerate(DATA['team']):
  b+='<article class="person reveal" id="'+t['name'].lower()+'-'+str(i+1)+'"><div class="person-photo"><div class="media-frame">'+picture(t['portrait'],t['name']+' — portrait Anekdote',sizes='(max-width: 800px) 90vw, 40vw')+(picture(t['fun'],t['name']+' — photo spontanée','fun-photo',sizes='(max-width: 800px) 90vw, 40vw') if t['fun']!=t['portrait'] else '')+'</div><div class="person-index"><span class="eyebrow">#TeamAnekdote</span><span class="eyebrow">/'+str(i+1).zfill(2)+'</span></div></div><div class="person-story"><h2>'+esc(t['name'])+'</h2><div class="prose">'+clean(t['bio'])+'</div><details><summary>Une Anekdote ?</summary><div class="prose">'+clean(t['anecdote'])+'</div></details></div></article>'
 b+='</section>';write(page,b,PAGES[BASE+'/equipe/']['title'],PAGES[BASE+'/equipe/']['description'],'equipe')

def talents():
 global page;page='talents/index.html';s=soup('talents');b=hero_intro('Notre <span class="italic">talent ?</span>','/05 — Anekdote','Un network puissant de créateurs de contenu !')
 # All testimonials on this page are exact published quotations, not fabricated.
 b+='<div class="talent-photo wrap"><div class="media-frame">'+picture(DATA['projects'][8]['thumbnail'],'Meganvlt — Festival de Cannes x Aroma-Zone',eager=True)+'</div></div><section class="talent-wall">'
 first=s.select_one('.talents-header-citation');b+='<blockquote class="talent-quote reveal">'+inner(first)+'</blockquote>'
 for c in s.select('.bloc-talents-container > div'):
  b+=('<blockquote class="talent-quote reveal">'+inner(c)+'</blockquote>') if 'bloc-talents-citation' in c.get('class',[]) else '<div class="prose reveal">'+inner(c)+'</div>'
 b+='</section>';write(page,b,PAGES[BASE+'/talents/']['title'],PAGES[BASE+'/talents/']['description'],'talents')

def newsroom():
 global page;page='newsroom/index.html';s=soup('newsroom');b=hero_intro('La <span class="italic">Newsroom.</span>','/06 — Actualités Anekdote',text(s.select_one('.page-header-banner-baseline')))+'<section class="news-portfolio">'
 for i,n in enumerate(DATA['news']):
  ex=text(BeautifulSoup(n['html'],'html.parser').find('p'))
  b+='<article class="reveal"><a href="'+url('newsroom/'+n['slug'])+'" class="media-frame">'+picture(n['image'],n['title'],eager=i==0)+'</a><div><p class="eyebrow">/'+str(i+1).zfill(2)+' — Newsroom</p><h2><a href="'+url('newsroom/'+n['slug'])+'">'+esc(n['title'])+'</a></h2><p class="excerpt">'+esc(ex[:260]+('…' if len(ex)>260 else ''))+'</p>'+link('Lire l’article','newsroom/'+n['slug'])+'</div></article>'
 b+='</section>';write(page,b,PAGES[BASE+'/newsroom/']['title'],PAGES[BASE+'/newsroom/']['description'],'newsroom')
 for n in DATA['news']:
  page='newsroom/'+n['slug']+'/index.html';b=hero_intro(esc(n['title']),'Anekdote — Newsroom',serif=True)+'<div class="article-hero">'+picture(n['image'],n['title'],eager=True)+'</div><article class="article-layout"><aside><p class="eyebrow">Newsroom — Anekdote</p>'+link('Tous les articles','newsroom')+'</aside><div class="prose">'+clean(n['html'],True)+'</div></article>'
  write(page,b,n['title']+' | Newsroom Anekdote',text(BeautifulSoup(n['html'],'html.parser').find('p'))[:160],'newsroom')

def contact():
 global page;page='contact/index.html';s=soup('contact');b=hero_intro('Un <span class="italic">café ?</span>','/07 — Contactez-nous',text(s.select_one('.page-header-banner-baseline')))
 b+='<section class="contact-layout"><aside class="contact-aside"><div class="media-frame">'+picture(bg(s.select_one('.page-header-banner-container')),'Le rooftop Anekdote — Paris',eager=True)+'</div><p class="eyebrow">4 rue Jules Lefebvre — Paris 75009</p><p class="annotation">On a hâte d’écouter vos projets.</p></aside><form class="contact-form" data-contact-form data-endpoint="https://www.anekdote.fr/wp-json/contact-form-7/v1/contact-forms/547/feedback" action="https://www.anekdote.fr/contact/#wpcf7-f547-o1" method="post"><input type="hidden" name="_wpcf7" value="547"><input type="hidden" name="_wpcf7_version" value="6.1.6"><input type="hidden" name="_wpcf7_locale" value="fr_FR"><input type="hidden" name="_wpcf7_unit_tag" value="wpcf7-f547-o1"><input type="hidden" name="_wpcf7_container_post" value="0"><input type="hidden" name="_wpcf7_posted_data_hash" value=""><div class="form-progress"><span data-step-indicator class="active"><b>01</b> Une boisson</span><span data-step-indicator><b>02</b> Un endroit</span><span data-step-indicator><b>03</b> Rencontrons-nous</span></div><section class="form-step" data-step="0"><h2 tabindex="-1">Quelle est votre<br><span class="italic">boisson préférée ?</span></h2><fieldset class="choice-grid"><legend class="sr-only">Choisissez une boisson</legend>'
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

home();agency();portfolio();cases();expertises();team();talents();newsroom();contact();legal()
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
