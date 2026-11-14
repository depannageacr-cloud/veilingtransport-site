from pathlib import Path
from html import escape as E
from urllib.parse import quote
import re, json, base64
from content import PAGES

ROOT=Path(__file__).resolve().parent.parent
BASE='https://www.veilingtransport.be'
DATE='2026-11-14'
HOME=(ROOT/'_source/homepage-source.html').read_text()
ASSETS=ROOT/'assets';ASSETS.mkdir(exist_ok=True)
LOOKUP={p['slug']:p for p in PAGES}
GROUPS=['Voertuigen','Goederen','Platformen','Routes','Voorbereiding']
GROUP_IDS={g:'onderwerpen-'+str(i+1) for i,g in enumerate(GROUPS)}
HUBS={'Voertuigen':'veilingtransport-voertuigen','Goederen':'veilingtransport-goederen','Platformen':'veilingtransport-documenten','Routes':'veilingtransport-belgie','Voorbereiding':'veilingtransport-checklist'}
assert len(PAGES)==40 and len(LOOKUP)==40

# Existing assets and styling are retained; embedded pictures become cacheable files.
images=list(re.finditer(r'data:image/(\w+);base64,([A-Za-z0-9+/=]+)',HOME))
for i,m in enumerate(images):
    name='veilinglogistiek.webp' if i==0 else 'voertuigtransport.webp'
    (ASSETS/name).write_bytes(base64.b64decode(m.group(2)))
    HOME=HOME.replace(m.group(0),'/assets/'+name)
styles=re.findall(r'<style[^>]*>(.*?)</style>',HOME,re.S)
basecss='\n'.join(styles)
(ASSETS/'veiling.css').write_text(basecss)

EXTRA_CSS='''
.vt-site [hidden]{display:none!important}
.vt-site .vt-breadcrumb{display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:13px;padding:23px 0;color:var(--muted)}
.vt-site .vt-breadcrumb a{text-decoration:none}.vt-site .vt-breadcrumb a:hover{text-decoration:underline}
.vt-site .vt-guide-hero{padding:38px 0 58px;border-bottom:1px solid var(--line);background:radial-gradient(ellipse at 95% 0,#ffda0021,transparent 50%)}
.vt-site .vt-guide-hero h1{font-size:clamp(35px,4.7vw,63px);max-width:890px;line-height:1.06;overflow-wrap:normal}
.vt-site .vt-guide-hero .vt-lead{max-width:850px;font-size:clamp(18px,2vw,22px)}
.vt-site .vt-guide-meta{font-size:13px;color:var(--muted);margin-top:25px}.vt-site .vt-guide-meta a{font-weight:700}
.vt-site .vt-guide-layout{display:grid;grid-template-columns:minmax(0,2fr) minmax(240px,1fr);gap:68px;padding-top:52px;padding-bottom:64px;align-items:start}
.vt-site .vt-guide-body{min-width:0}.vt-site .vt-guide-body section{margin-bottom:42px;scroll-margin-top:24px}
.vt-site .vt-guide-body h2{font-size:clamp(24px,2.7vw,33px);line-height:1.15;letter-spacing:-.035em}
.vt-site .vt-guide-body p{font-size:17px;line-height:1.8;max-width:76ch}.vt-site .vt-guide-body a{font-weight:700}
.vt-site .vt-guide-side{position:sticky;top:24px;background:#fff;border:1px solid var(--line);border-top:5px solid var(--yellow);padding:25px}
.vt-site .vt-guide-side h2{font-size:23px;line-height:1.2}.vt-site .vt-guide-side ul{padding-left:20px;font-size:15px;line-height:1.65}.vt-site .vt-guide-side li{margin-bottom:11px}
.vt-site .vt-guide-side .vt-btn{width:100%;margin-top:8px}.vt-site .vt-guide-side .vt-small{display:block;margin-top:15px}
.vt-site .vt-toc{background:#eeeee5;padding:25px 28px;margin-bottom:40px}.vt-site .vt-toc strong{display:block;margin-bottom:10px}.vt-site .vt-toc ol{margin:0;padding-left:22px}.vt-site .vt-toc li{margin:7px 0;font-size:15px}
.vt-site .vt-related{background:#eeeee5;padding-block:58px}.vt-site .vt-related h2,.vt-site .vt-topic-directory h2{font-size:clamp(28px,3.5vw,42px)}
.vt-site .vt-topic-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;list-style:none;padding:0;margin:22px 0 0}
.vt-site .vt-topic-grid>li{margin:0;min-width:0}.vt-site .vt-topic-card{display:flex;flex-direction:column;height:100%;background:#fff;border:1px solid var(--line);padding:24px;text-decoration:none;border-radius:3px;transition:border-color .18s,transform .18s}
.vt-site .vt-topic-card:hover{border-color:var(--ink);transform:translateY(-2px)}
.vt-site .vt-topic-card span{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);font-weight:800;margin-bottom:13px}
.vt-site .vt-topic-card strong{font-size:20px;line-height:1.2;letter-spacing:-.025em;display:block;margin-bottom:12px}
.vt-site .vt-topic-card p{font-size:14px;line-height:1.65;margin-bottom:18px;color:var(--muted)}.vt-site .vt-topic-card em{font-size:13px;font-style:normal;font-weight:800;margin-top:auto}
.vt-site .vt-topic-directory{padding:68px 0}.vt-site .vt-topic-directory>div>p{max-width:770px}.vt-site .vt-topic-group{margin-top:48px;scroll-margin-top:25px}.vt-site .vt-topic-group h3{font-size:26px;line-height:1.2}
.vt-site .vt-topic-tabs{display:flex;gap:9px;flex-wrap:wrap;margin-top:25px}.vt-site .vt-topic-tabs a{border:1px solid var(--line);padding:8px 14px;font-size:14px;font-weight:700;text-decoration:none;background:#fff}.vt-site .vt-topic-tabs a:hover{background:var(--yellow)}
.vt-site .vt-guide-steps{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;margin:30px 0}.vt-site .vt-guide-steps div{border-left:3px solid var(--yellow);padding-left:17px;font-size:14px}.vt-site .vt-guide-steps strong{display:block;font-size:16px;margin-bottom:7px}
.vt-site .vt-source{font-size:13px!important;border-top:1px solid var(--line);padding-top:18px;color:var(--muted)}
.vt-site .vt-tool{padding:28px;border:1px solid var(--line);background:#fff;margin:35px 0}.vt-site .vt-tool h2{font-size:28px}.vt-site .vt-tool-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.vt-site .vt-tool label{font-size:14px;display:flex;flex-direction:column;gap:7px;font-weight:700}.vt-site .vt-tool input,.vt-site .vt-tool textarea{width:100%;min-width:0;padding:11px;border:1px solid #999f94;background:#fff;color:var(--ink);border-radius:2px;font-size:16px}.vt-site .vt-tool textarea{min-height:100px}.vt-site .vt-tool .vt-full{grid-column:1/-1}
.vt-site .vt-tool output{display:block;white-space:pre-wrap;font-size:14px;padding:18px;background:#eeeee5;margin-top:22px;line-height:1.7;overflow-wrap:anywhere}
.vt-site .vt-tool button{cursor:pointer}.vt-site .vt-tool-status{font-size:14px;min-height:24px;margin-top:10px}
.vt-site .vt-inpage-faq{border-top:1px solid var(--line);padding-top:30px}.vt-site .vt-inpage-faq details{border-bottom:1px solid var(--line);padding:18px 0}.vt-site .vt-inpage-faq summary{cursor:pointer;font-weight:800;line-height:1.5;padding-right:20px}.vt-site .vt-inpage-faq details p{margin:16px 0 0;font-size:16px}
@media(max-width:960px){.vt-site .vt-guide-layout{gap:30px;grid-template-columns:minmax(0,1fr) 280px}.vt-site .vt-topic-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:720px){.vt-site .vt-guide-layout{grid-template-columns:1fr;padding-top:32px;gap:15px}.vt-site .vt-guide-side{position:static;grid-row:1}.vt-site .vt-guide-side ul{columns:2;column-gap:26px}.vt-site .vt-guide-hero{padding:22px 0 35px}.vt-site .vt-guide-hero h1{font-size:clamp(32px,8.4vw,48px)}.vt-site .vt-guide-steps{grid-template-columns:1fr;gap:15px}.vt-site .vt-guide-body p{font-size:16px}.vt-site .vt-tool-grid{grid-template-columns:1fr}.vt-site .vt-tool{padding:20px}.vt-site .vt-guide-side .vt-btn{width:auto}.vt-site .vt-breadcrumb{font-size:12px;padding:18px 0}}
@media(max-width:480px){.vt-site .vt-topic-grid{grid-template-columns:1fr}.vt-site .vt-guide-side ul{columns:auto}.vt-site .vt-topic-directory,.vt-site .vt-related{padding-block:42px}.vt-site .vt-topic-card{padding:22px}.vt-site .vt-guide-hero h1{overflow-wrap:break-word}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto!important}.vt-site .vt-topic-card{transition:none;transform:none!important}}
@media print{.vt-header,.vt-sticky,.vt-footer,.vt-related,.vt-bottom-cta,.vt-guide-side,.vt-toc,.vt-tool .vt-actions,.vt-topic-tabs{display:none!important}.vt-guide-layout{display:block!important}.vt-site,.vt-tool{background:#fff!important}.vt-wrap{width:100%!important}.vt-site .vt-guide-hero{padding:10px 0}.vt-site .vt-guide-hero h1{font-size:30px}.vt-tool output{break-inside:avoid}.vt-inpage-faq details:not([open])>p{display:block!important}}
'''
(ASSETS/'guides.css').write_text(EXTRA_CSS)

MAPPING={'#vt-top':'/','#voertuigen':'/veilingtransport-voertuigen/','#goederen':'/veilingtransport-goederen/','#kosten':'/veilingtransport-kosten/','#afhalen':'/afhaaldag-veiling-regelen/','#vragen':'/veelgestelde-vragen-veilingtransport/','#troostwijk':'/troostwijk-transport/','#vavato':'/vavato-transport/','#belgie-nederland':'/veilingtransport-nederland-belgie/','#duitsland-luxemburg':'/veilingtransport-duitsland-belgie/','#internationaal':'/veilingtransport-spanje/'}
header=re.search(r'<header class="vt-header"[\s\S]*?</header>',HOME).group()
header=header.replace('<a href="#vragen">Vragen</a>','<a href="/#kennis">Alle onderwerpen</a>')
for before,after in MAPPING.items():header=header.replace('href="'+before+'"','href="'+after+'"')
footer=re.search(r'<footer class="vt-footer"[\s\S]*?</footer>',HOME).group()
footer=re.sub(r'<button class="vt-cookie-settings"[\s\S]*?</button>','',footer)
for before,after in MAPPING.items():footer=footer.replace('href="'+before+'"','href="'+after+'"')
footer=footer.replace('<h3>Goed voorbereid</h3>','<h3>Goed voorbereid</h3><p><a href="/veilingtransport-checklist/">Invulbare afhaalchecklist</a><br><a href="/veilingtransport-acr-informatie/">Diensten en contactgegevens</a><br><a href="/#kennis">Alle 40 onderwerpen</a></p>')
footer=footer.replace('<h3>Uw veilingtransport</h3>','<h3>Uw veilingtransport</h3><p><a href="/auctim-transport/">Auctim ophalen</a><br><a href="/veilingtransport-italie/">Levering naar Italië</a></p>')
sticky='<div aria-label="Snel contact" class="vt-sticky"><a href="tel:+32471379064">Bel 0471 37 90 64</a><a href="https://wa.me/32471379064?text='+quote('Ik wil veilingtransport aanvragen. Mijn kavellink en route: ')+'" target="_blank" rel="noopener noreferrer">WhatsApp ↗</a></div>'
commonjs="""(()=>{const r=document.querySelector('.vt-site'),b=r?.querySelector('.vt-menu-toggle'),n=r?.querySelector('.vt-nav');if(b&&n){b.addEventListener('click',()=>{const o=b.getAttribute('aria-expanded')!=='true';b.setAttribute('aria-expanded',String(o));n.classList.toggle('vt-is-open',o);b.textContent=o?'Sluiten':'Menu'});n.addEventListener('keydown',e=>{if(e.key==='Escape'){b.setAttribute('aria-expanded','false');n.classList.remove('vt-is-open');b.textContent='Menu';b.focus()}})}r?.querySelectorAll('.vt-nav details').forEach(d=>d.addEventListener('toggle',()=>{if(d.open)r.querySelectorAll('.vt-nav details').forEach(x=>{if(x!==d)x.open=false})}))})();"""
(ASSETS/'guides.js').write_text(commonjs)

def card(p):
    return '<li><a class="vt-topic-card" href="/'+p['slug']+'/"><span>'+E(p['group'])+'</span><strong>'+E(p['title'])+'</strong><p>'+E(p['description'])+'</p><em>Lees de uitleg ↗</em></a></li>'

directory='<section class="vt-topic-directory" id="kennis" aria-labelledby="vt-kennis-title"><div class="vt-wrap"><span class="vt-eyebrow">Kies uw transportvraag</span><h2 id="vt-kennis-title">Van kavel naar een goed voorbereide rit.</h2><p>Praktische uitleg voor uw voertuig, goederen, veilingplatform en route. Kies uw onderwerp of gebruik de <a href="/veilingtransport-checklist/">invulbare afhaalchecklist</a> om meteen de juiste gegevens door te geven.</p><nav class="vt-topic-tabs" aria-label="Onderwerpen">'+''.join('<a href="#'+GROUP_IDS[g]+'">'+E(g)+'</a>' for g in GROUPS)+'</nav>'
for g in GROUPS:
    directory+='<section class="vt-topic-group" id="'+GROUP_IDS[g]+'"><h3>'+E(g)+'</h3><ul class="vt-topic-grid">'+''.join(card(p) for p in PAGES if p['group']==g)+'</ul></section>'
directory+='</div></section>'
HOME=re.sub(r'<header class="vt-header"[\s\S]*?</header>',lambda _:header,HOME,count=1)
HOME=re.sub(r'<footer class="vt-footer"[\s\S]*?</footer>',lambda _:footer,HOME,count=1)
HOME=HOME.replace('<section class="vt-section" id="vragen">',directory+'<section class="vt-section" id="vragen">',1)
HOME=HOME.replace('</head>','<link rel="stylesheet" href="/assets/guides.css"><link rel="icon" href="/favicon.svg" type="image/svg+xml"></head>',1)
HOME=HOME.replace('data-ready="true"','')
HOME=re.sub(r'<div aria-label="Snel contact" class="vt-sticky">[\s\S]*?</div>',lambda _:sticky,HOME,count=1)
(ROOT/'index.html').write_text(HOME)

TOOL='''<section class="vt-tool" id="aanvraag-maken"><h2>Maak uw transportaanvraag compleet</h2><p>Vul in wat u al weet. Ontbrekende gegevens blijven zichtbaar in het overzicht. Uw invoer wordt hier niet opgeslagen of automatisch verstuurd.</p><form id="vt-request-builder"><div class="vt-tool-grid">
<label>Platform en kavelnummer<input name="kavel" placeholder="Bijvoorbeeld: platform, kavelnummer" maxlength="250"></label><label>Kavellink<input name="link" type="url" placeholder="https://…" maxlength="1200"></label>
<label>Afhaaladres<input name="laden" autocomplete="off" placeholder="Adres, postcode en land" maxlength="350"></label><label>Afleveradres<input name="lossen" autocomplete="off" placeholder="Adres, postcode en land" maxlength="350"></label>
<label>Afhaaldag en tijdslot<input name="tijd" placeholder="Datum, begin- en eindtijd" maxlength="200"></label><label>Vrijgave en locatiecontact<input name="vrijgave" placeholder="Is vrijgave klaar? Wie is bereikbaar?" maxlength="350"></label>
<label class="vt-full">Lading, aantallen, maten en massa<textarea name="lading" maxlength="2000" placeholder="Voertuiggegevens of goederen per eenheid. Vermeld ook accessoires."></textarea></label>
<label class="vt-full">Toestand, verpakking en laad- en loshulp<textarea name="toestand" maxlength="2000" placeholder="Voertuig: starten, rollen, sturen, remmen, sleutels. Goederen: verpakking, toegang en hulpmiddelen op beide adressen."></textarea></label>
</div><div class="vt-actions"><button class="vt-btn" type="submit">Maak mijn overzicht</button><button class="vt-btn vt-outline" type="reset">Wis invoer</button></div></form>
<output id="vt-request-output" aria-label="Overzicht van uw transportaanvraag">Vul de velden in en kies ‘Maak mijn overzicht’.</output><div class="vt-actions" id="vt-send-actions" hidden><a class="vt-btn" id="vt-send-wa" target="_blank" rel="noopener noreferrer">Open in WhatsApp ↗</a><a class="vt-btn vt-outline" id="vt-send-mail">Open in e-mail</a><button class="vt-btn vt-outline" id="vt-copy" type="button">Kopieer tekst</button><button class="vt-btn vt-outline" id="vt-print" type="button">Afdrukken</button></div><p class="vt-tool-status" id="vt-tool-status" role="status"></p><p class="vt-small">Controleer het overzicht vóór u het zelf verzendt. Een klaargezet bericht is geen bevestigde transportopdracht. Op mobiel opent WhatsApp in de toepassing of browser.</p></section>'''
tooljs="""(()=>{const f=document.getElementById('vt-request-builder');if(!f)return;const o=document.getElementById('vt-request-output'),a=document.getElementById('vt-send-actions'),s=document.getElementById('vt-tool-status');let message='';const fields={kavel:'Platform en kavel',link:'Kavellink',laden:'Afhaaladres',lossen:'Afleveradres',tijd:'Afhaaldag en tijdslot',vrijgave:'Vrijgave en locatiecontact',lading:'Lading, maten en massa',toestand:'Toestand, verpakking en laad- en loshulp'};f.addEventListener('submit',e=>{e.preventDefault();const d=new FormData(f);message='Aanvraag veilingtransport bij ACR\\n\\n'+Object.entries(fields).map(([k,v])=>v+': '+(String(d.get(k)||'').trim()||'Nog aan te vullen')).join('\\n\\n');o.textContent=message;document.getElementById('vt-send-wa').href='https://wa.me/32471379064?text='+encodeURIComponent(message);document.getElementById('vt-send-mail').href='mailto:depannageacr@hotmail.com?subject='+encodeURIComponent('Aanvraag veilingtransport')+'&body='+encodeURIComponent(message);a.hidden=false;s.textContent='Overzicht klaargezet. Controleer en verzend het zelf via uw gekozen toepassing.'});f.addEventListener('reset',()=>{message='';o.textContent='Vul de velden in en kies ‘Maak mijn overzicht’.';a.hidden=true;s.textContent='Invoer gewist.'});document.getElementById('vt-copy').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(message);s.textContent='Tekst gekopieerd.'}catch{s.textContent='Kopiëren niet beschikbaar. Selecteer de tekst uit het overzicht.'}});document.getElementById('vt-print').addEventListener('click',()=>window.print())})();"""
(ASSETS/'checklist.js').write_text(tooljs)

SOURCES={
'troostwijk-transport':('Troostwijk: ophalen en transport','https://service.troostwijkauctions.com/hc/nl/articles/17378592568604-Alles-over-ophalen-en-transport-van-je-aankoop'),
'vavato-transport':('Vavato: informatie over transport','https://www.vavato.com/transportpartners'),
'auctim-transport':('Auctim: een transporteur inschakelen','https://support.auctim.com/nl/support/solutions/articles/201000083006-kan-ik-een-transporteur-inhuren-om-mijn-goederen-op-te-halen-of-iemand-namens-mij-sturen-')}

for p in PAGES:
    slug=p['slug'];url=BASE+'/'+slug+'/'
    groupurl=BASE+'/#'+GROUP_IDS[p['group']]
    short=p['title'];title=short+' | ACR'
    schema={'@context':'https://schema.org','@graph':[
        {'@type':'Organization','@id':BASE+'/#acr','name':'Takeldienst ACR','url':'https://www.takeldienstacr.be/','telephone':'+32471379064','email':'depannageacr@hotmail.com'},
        {'@type':'WebSite','@id':BASE+'/#website','url':BASE+'/','name':'Veilingtransport by ACR','inLanguage':'nl-BE','publisher':{'@id':BASE+'/#acr'}},
        {'@type':'WebPage','@id':url+'#webpage','url':url,'name':short,'description':p['description'],'inLanguage':'nl-BE','dateModified':DATE,'isPartOf':{'@id':BASE+'/#website'},'publisher':{'@id':BASE+'/#acr'},'breadcrumb':{'@id':url+'#breadcrumb'}},
        {'@type':'BreadcrumbList','@id':url+'#breadcrumb','itemListElement':[{'@type':'ListItem','position':1,'name':'Veilingtransport','item':BASE+'/'},{'@type':'ListItem','position':2,'name':p['group'],'item':groupurl},{'@type':'ListItem','position':3,'name':short,'item':url}]}
    ]}
    if slug=='veelgestelde-vragen-veilingtransport':
        schema['@graph'].append({'@type':'FAQPage','@id':url+'#faq','mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}} for q,a in p['faq']]})
    elif slug!='veilingtransport-acr-informatie':
        schema['@graph'].append({'@type':'Service','@id':url+'#service','name':short,'serviceType':'Beoordeling en uitvoering van veilingtransport op aanvraag','url':url,'provider':{'@id':BASE+'/#acr'}})
    toc='<nav class="vt-toc" aria-label="Op deze pagina"><strong>Op deze pagina</strong><ol>'+''.join('<li><a href="#uitleg-'+str(i)+'">'+E(h)+'</a></li>' for i,(h,t) in enumerate(p['sections'],1))+'<li><a href="#vragen">Vragen over dit transport</a></li></ol></nav>'
    sections=''.join('<section id="uitleg-'+str(i)+'"><h2>'+E(h)+'</h2><p>'+E(t.replace('\u00ad',''))+'</p></section>' for i,(h,t) in enumerate(p['sections'],1))
    # Contextual links in the editorial body, not just in a sitewide footer.
    context='<p class="vt-small">Ga verder met <a href="/'+p['related'][0]+'/">'+E(LOOKUP[p['related'][0]]['title'].lower())+'</a> of bekijk <a href="/'+p['related'][1]+'/">'+E(LOOKUP[p['related'][1]]['title'].lower())+'</a>.</p>'
    sections=sections.replace('</section>',context+'</section>',1)
    faq='<section class="vt-inpage-faq" id="vragen"><h2>Vragen over dit transport</h2>'+''.join('<details><summary>'+E(q)+'</summary><p>'+E(a)+'</p></details>' for q,a in p['faq'])+'</section>'
    source=''
    if slug in SOURCES:
        label,link=SOURCES[slug];source='<p class="vt-source">Aanvullende bron: <a href="'+link+'" target="_blank" rel="noopener noreferrer">'+E(label)+'</a>. Geraadpleegd op 14 november 2026. Controleer altijd de actuele instructies bij uw eigen kavel.</p>'
    related=p['related'][:]
    hub=HUBS[p['group']]
    if hub!=slug and hub not in related:related.append(hub)
    aside='<aside class="vt-guide-side"><span class="vt-eyebrow">Voor uw aanvraag</span><h2>Geef dit meteen door</h2><ul>'+''.join('<li>'+E(c)+'</li>' for c in p['checks'])+'</ul><a class="vt-btn" href="https://www.autorepatriering.be/#offerte">Vraag transport aan ↗</a><a class="vt-btn vt-outline" href="tel:+32471379064">0471 37 90 64</a><a class="vt-small" href="/veilingtransport-checklist/#aanvraag-maken">Maak een compleet aanvraagoverzicht</a></aside>'
    html='<!doctype html><html lang="nl-BE"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+E(title)+'</title><meta name="description" content="'+E(p['description'],quote=True)+'"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="'+url+'"><meta property="og:type" content="website"><meta property="og:locale" content="nl_BE"><meta property="og:site_name" content="Veilingtransport by ACR"><meta property="og:title" content="'+E(title,quote=True)+'"><meta property="og:description" content="'+E(p['description'],quote=True)+'"><meta property="og:url" content="'+url+'"><meta property="og:image" content="'+BASE+'/share.webp"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/veiling.css"><link rel="stylesheet" href="/assets/guides.css"><script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('</','<\\/')+'</script><script src="/assets/guides.js" defer></script>'+('<script src="/assets/checklist.js" defer></script>' if slug=='veilingtransport-checklist' else '')+'</head><body><div class="vt-site" id="vt-top"><a class="vt-skip" href="#inhoud">Naar de inhoud</a>'+header+'<main id="inhoud"><div class="vt-wrap"><nav class="vt-breadcrumb" aria-label="Broodkruimels"><a href="/">Veilingtransport</a><span aria-hidden="true">/</span><a href="/#'+GROUP_IDS[p['group']]+'">'+E(p['group'])+'</a><span aria-hidden="true">/</span><span aria-current="page">'+E(short)+'</span></nav></div><section class="vt-guide-hero"><div class="vt-wrap"><span class="vt-eyebrow">'+E(p['group'])+' · Veilingtransport by ACR</span><h1>'+E(short)+'</h1><p class="vt-lead">'+E(p['intro'])+'</p><div class="vt-actions"><a class="vt-btn" href="https://www.autorepatriering.be/#offerte">Bespreek uw kavel ↗</a><a class="vt-btn vt-outline" href="tel:+32471379064">Bel 0471 37 90 64</a></div><p class="vt-guide-meta">Informatie van <a href="/veilingtransport-acr-informatie/">ACR</a> · Bijgewerkt op 14 november 2026 · Uitvoering na bevestiging</p></div></section><div class="vt-wrap vt-guide-layout"><article class="vt-guide-body" aria-label="Transportinformatie">'+toc+sections+(TOOL if slug=='veilingtransport-checklist' else '')+faq+source+'</article>'+aside+'</div><section class="vt-related"><div class="vt-wrap"><span class="vt-eyebrow">Verder met uw aankoop</span><h2>Dit helpt bij de volgende stap.</h2><ul class="vt-topic-grid">'+''.join(card(LOOKUP[x]) for x in related)+'</ul><p style="margin-top:25px"><a href="/#kennis">Bekijk alle 40 transportonderwerpen ↗</a></p></div></section><section class="vt-bottom-cta"><div class="vt-wrap"><div><h2>Van kavel naar een concrete afspraak.</h2><p>Stuur kavellink, route, afhaalvenster en laadgegevens. ACR bespreekt uitvoering, prijs en planning met u.</p></div><div class="vt-actions"><a class="vt-btn" href="https://www.autorepatriering.be/#offerte">Transport aanvragen ↗</a><a class="vt-btn vt-outline" href="tel:+32471379064">Bel ACR</a></div></div></section></main>'+footer+sticky+'</div></body></html>'
    dest=ROOT/slug;dest.mkdir(exist_ok=True);(dest/'index.html').write_text(html)

urls=[BASE+'/']+[BASE+'/'+p['slug']+'/' for p in PAGES]
xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('  <url><loc>'+E(u)+'</loc><lastmod>'+DATE+'</lastmod></url>\n' for u in urls)+'</urlset>\n'
(ROOT/'sitemap.xml').write_text(xml)
(ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+BASE+'/sitemap.xml\n')
(ROOT/'llms.txt').write_text('# Veilingtransport by ACR\n\n> Onafhankelijke aanvragen voor transport van veilingaankopen. Rit, prijs en planning worden per opdracht bevestigd. Geen officiële vertegenwoordiging van de genoemde veilingplatformen.\n\nContact: +32 471 37 90 64 | depannageacr@hotmail.com\n\n## Feiten en praktische informatie\n\n'+''.join('- ['+p['title']+']('+BASE+'/'+p['slug']+'/): '+p['description']+'\n' for p in PAGES)+'\nDeze verwijslijst is aanvullend. De zichtbare webpagina’s bevatten de volledige informatie; er wordt geen opname in AI-antwoorden of zoekresultaten gegarandeerd.\n')
(ROOT/'ai-info.json').write_text(json.dumps({'name':'Veilingtransport by ACR','url':BASE+'/','contact':{'telephone':'+32471379064','email':'depannageacr@hotmail.com'},'provider':'ACR','requestRequirements':['kavellink en kavelnummer','laad- en losadres','afhaalvenster','maten, massa en toestand','laad- en losmogelijkheden'],'booking':'Uitvoering, prijs en planning na individuele bevestiging','platformRelationship':'Geen officiële samenwerking of vertegenwoordiging geclaimd','lastUpdated':DATE,'pages':[{'name':p['title'],'url':BASE+'/'+p['slug']+'/','category':p['group']} for p in PAGES]},ensure_ascii=False,indent=2))
(ROOT/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" rx="8" fill="#ffda00"/><text x="50" y="64" text-anchor="middle" font-family="Arial,sans-serif" font-size="37" font-style="italic" font-weight="900" fill="#141713">ACR</text></svg>')
(ROOT/'404.html').write_text('<!doctype html><html lang="nl-BE"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,follow"><title>Pagina niet gevonden | Veilingtransport ACR</title><link rel="stylesheet" href="/assets/veiling.css"></head><body><main class="vt-site" style="min-height:100vh;padding:60px 0"><div class="vt-wrap"><span class="vt-eyebrow">Veilingtransport by ACR · 404</span><h1>Deze pagina is niet gevonden.</h1><p>Kies een transportonderwerp of neem rechtstreeks contact op met ACR.</p><div class="vt-actions"><a class="vt-btn" href="/#kennis">Bekijk alle onderwerpen</a><a class="vt-btn vt-outline" href="tel:+32471379064">Bel 0471 37 90 64</a></div></div></main></body></html>')
(ROOT/'.htaccess').write_text('''Options -Indexes
DirectoryIndex index.html
ErrorDocument 404 /404.html
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteRule ^\\.git(?:/|$) - [F,L]
RewriteRule ^_source(?:/|$) - [F,L]
RewriteRule ^\\.well-known/acme-challenge/ - [L]
RewriteCond %{HTTPS} !=on [OR]
RewriteCond %{HTTP_HOST} !^www\\.veilingtransport\\.be$ [NC]
RewriteRule ^ https://www.veilingtransport.be%{REQUEST_URI} [R=301,L,NE]
</IfModule>
<IfModule mod_expires.c>
ExpiresActive On
ExpiresByType image/webp "access plus 1 month"
ExpiresByType image/svg+xml "access plus 1 week"
ExpiresByType text/css "access plus 1 week"
ExpiresByType application/javascript "access plus 1 week"
</IfModule>
<IfModule mod_headers.c>
Header always set X-Content-Type-Options "nosniff"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
Header always set X-Frame-Options "SAMEORIGIN"
</IfModule>
''')
print(json.dumps({'new_pages':len(PAGES),'sitemap_urls':len(urls),'homepage_bytes':len(HOME.encode())}))
