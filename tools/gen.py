# -*- coding: utf-8 -*-
import html, re, os, shutil, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from content import CASES, FREELANCE

ROOT = '/tmp/claude-0/-home-claude/09a16d60-b7d3-584b-8a37-da9665017baa/scratchpad/'
SRC_IMG = ROOT + 'build/site/img'
OUT = ROOT + 'build3/site'
os.makedirs(OUT, exist_ok=True)
if not os.path.exists(OUT + '/img'):
    shutil.copytree(SRC_IMG, OUT + '/img')
e = lambda x: html.escape(x, quote=True)
_dim = {}
def dim(n):
    if n not in _dim:
        _dim[n] = Image.open(f'{OUT}/img/{n}.webp').size
    return _dim[n]
def img(n, alt, lazy=True, cls=''):
    w, h = dim(n)
    return f'<img{" class=%s" % chr(34)+cls+chr(34) if cls else ""} src="img/{n}.webp" alt="{e(alt)}" width="{w}" height="{h}"{" loading=%slazy%s" % (chr(34),chr(34)) if lazy else ""} decoding="async">'
def tile(n, cap, lazy=True):
    return f'<button class="tile" type="button" data-cap="{e(cap)}" aria-label="Agrandir : {e(cap)}">{img(n, cap, lazy)}</button>'

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Instrument+Serif:ital@0;1&family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap">'

# ---------------------------------------------------------------- shared JS (lightbox + reveal)
CASE_JS = r"""
<script>
(function(){
  try{if('scrollRestoration' in history)history.scrollRestoration='manual'}catch(err){}
  function toTop(){if(!location.hash||location.hash==='#top')window.scrollTo(0,0)}
  toTop();addEventListener('pageshow',toTop);addEventListener('load',toTop);
  var reduce=matchMedia('(prefers-reduced-motion: reduce)').matches,root=document.documentElement;
  if(!reduce && 'IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){x.target.classList.remove('pending');io.unobserve(x.target)}})},{rootMargin:'0px 0px -8% 0px',threshold:0.02});
    document.querySelectorAll('[data-a]').forEach(function(el){if(el.getBoundingClientRect().top>innerHeight*0.92){el.classList.add('pending');io.observe(el)}});
  }
  addEventListener('scroll',function(){var m=root.scrollHeight-innerHeight;root.style.setProperty('--sp',m>0?scrollY/m:0)},{passive:true});
  document.querySelectorAll('.more button').forEach(function(b){b.addEventListener('click',function(){
    document.getElementById(b.dataset.gal).querySelectorAll('[hidden]').forEach(function(t){t.hidden=false});b.parentNode.remove();})});
  var lb=document.getElementById('lb'),li=document.getElementById('lb-img'),lc=document.getElementById('lb-cap'),ln=document.getElementById('lb-n'),set=[],cur=0,last=null;
  function show(i){cur=(i+set.length)%set.length;var it=set[cur];li.src=it.src;li.alt=it.cap;lc.textContent=it.cap;ln.textContent=(cur+1)+' / '+set.length;li.style.animation='none';void li.offsetWidth;li.style.animation=''}
  function open(items,i,from){set=items;last=from;lb.hidden=false;root.style.overflow='hidden';show(i);document.getElementById('lb-close').focus()}
  function close(){lb.hidden=true;root.style.overflow='';li.removeAttribute('src');if(last)last.focus()}
  document.querySelectorAll('.tile').forEach(function(t){t.addEventListener('click',function(){
    var box=t.closest('[data-set]');var tiles=[].slice.call(box.querySelectorAll('.tile'));
    open(tiles.map(function(x){var im=x.querySelector('img');return{src:im.getAttribute('src'),cap:x.dataset.cap}}),tiles.indexOf(t),t)})});
  document.getElementById('lb-close').addEventListener('click',close);
  document.getElementById('lb-prev').addEventListener('click',function(){show(cur-1)});
  document.getElementById('lb-next').addEventListener('click',function(){show(cur+1)});
  lb.addEventListener('click',function(x){if(x.target===lb||x.target.classList.contains('lb-stage'))close()});
  addEventListener('keydown',function(x){if(lb.hidden)return;if(x.key==='Escape')close();if(x.key==='ArrowLeft')show(cur-1);if(x.key==='ArrowRight')show(cur+1)});
  var sx=null;lb.addEventListener('touchstart',function(x){sx=x.touches[0].clientX},{passive:true});
  lb.addEventListener('touchend',function(x){if(sx===null)return;var d=x.changedTouches[0].clientX-sx;if(Math.abs(d)>50)show(cur+(d<0?1:-1));sx=null});
  // back to portfolio: prefer history when coming from it
  document.querySelectorAll('[data-back]').forEach(function(a){a.addEventListener('click',function(x){
    try{if(document.referrer&&new URL(document.referrer).origin===location.origin&&history.length>1){x.preventDefault();history.back()}}catch(err){}
  })});
})();
</script>"""

LIGHTBOX = '''<div class="lb" id="lb" hidden role="dialog" aria-modal="true" aria-label="Visuel agrandi">
  <div class="lb-top"><span class="mono" id="lb-n"></span><button type="button" class="lb-btn" id="lb-close">Fermer ✕</button></div>
  <div class="lb-stage"><img id="lb-img" alt=""><button type="button" class="lb-nav prev" id="lb-prev" aria-label="Visuel précédent">←</button><button type="button" class="lb-nav next" id="lb-next" aria-label="Visuel suivant">→</button></div>
  <p class="lb-cap" id="lb-cap"></p>
</div>'''

LB_CSS = """
.lb{position:fixed;inset:0;z-index:100;background:#0B0A08;height:100vh;height:100dvh;overflow:hidden;display:grid;grid-template-rows:auto 1fr auto;gap:12px;
  padding:calc(14px + env(safe-area-inset-top,0px)) max(16px,env(safe-area-inset-right,0px)) calc(16px + env(safe-area-inset-bottom,0px)) max(16px,env(safe-area-inset-left,0px));animation:fade .25s}
.lb[hidden]{display:none}
.lb .mono{color:#A49C8D}
.lb-top{display:flex;justify-content:space-between;align-items:center;gap:12px}
.lb-stage{position:relative;display:flex;align-items:center;justify-content:center;min-height:0;overflow:hidden}
.lb-stage img{max-height:calc(100vh - 170px);max-height:calc(100dvh - 170px - env(safe-area-inset-top,0px) - env(safe-area-inset-bottom,0px));max-width:calc(100% - 120px);width:auto;height:auto;object-fit:contain;border-radius:8px;animation:zoomin .35s cubic-bezier(.2,.7,.2,1)}
.lb-cap{text-align:center;color:#D8D1C3;font-size:.92rem;max-width:70ch;margin:0 auto}
.lb-btn{background:#17150F;color:#F3EEE4;border:1px solid #302B22;border-radius:999px;padding:9px 16px;font-weight:700;cursor:pointer;font-family:inherit}
.lb-nav{position:absolute;top:50%;translate:0 -50%;width:48px;height:48px;border-radius:50%;background:rgba(23,21,15,.85);border:1px solid #302B22;color:#F3EEE4;font-size:1.3rem;cursor:pointer}
.lb-nav.prev{left:0}.lb-nav.next{right:0}
@media (max-width:620px){.lb-stage img{max-width:100%}.lb-nav{top:auto;bottom:6px;translate:none;width:42px;height:42px}}
@keyframes fade{from{opacity:0}}
@keyframes zoomin{from{opacity:0;transform:scale(.95)}}
"""

# ---------------------------------------------------------------- CASE PAGE CSS (light, ivory)
CASE_CSS = """
/* Layout: case-study reading page — ivory paper, ink type, project tint; sticky section labels on the left, content on the right.
   Single light look by choice (the home page is the dark one). */
:root{
  --bg:#F5F0E6; --paper:#FBF8F2; --ink:#16130E; --muted:#6B6355; --line:#E1D8C6; --gold:#9C7A2E;
  --tint:#9C7A2E; --tint-soft:#F1E6CC;
  --f-poster:"Anton","Impact","Arial Narrow",sans-serif;
  --f-serif:"Instrument Serif","Times New Roman",Georgia,serif;
  --f-body:"Manrope","Segoe UI",system-ui,sans-serif;
  --f-mono:"JetBrains Mono",ui-monospace,Menlo,monospace;
  --max:1180px; --ease:cubic-bezier(.2,.7,.2,1);
  color-scheme:light;
}
*{box-sizing:border-box}
html{overflow-x:clip}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--f-body);font-size:17px;line-height:1.65;-webkit-font-smoothing:antialiased;overflow-x:clip}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:60;background:var(--bg)}
a{color:inherit}
img{display:block;max-width:100%;height:auto}
button{font:inherit;color:inherit}
:focus-visible{outline:2px solid var(--tint);outline-offset:3px;border-radius:6px}
h1,h2,h3,h4{margin:0;font-weight:400;text-wrap:balance}
p{margin:0}
[hidden]{display:none!important}
.wrap{max-width:var(--max);margin:0 auto;padding-left:max(20px,env(safe-area-inset-left,0px));padding-right:max(20px,env(safe-area-inset-right,0px))}
.mono{font-family:var(--f-mono);font-size:.74rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.serif{font-family:var(--f-serif);font-style:italic;text-transform:none;letter-spacing:0}
.progress{position:fixed;top:env(safe-area-inset-top,0px);left:0;right:0;height:3px;z-index:70;background:var(--tint);transform-origin:0 50%;transform:scaleX(var(--sp,0))}

nav{position:sticky;top:env(safe-area-inset-top,0px);z-index:50;background:color-mix(in srgb,var(--bg) 85%,transparent);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}
nav .wrap{display:flex;align-items:center;justify-content:space-between;gap:14px;padding-block:12px}
.back{display:inline-flex;align-items:center;gap:8px;text-decoration:none;font-weight:700;font-size:.9rem;white-space:nowrap}
.back b{font-family:var(--f-poster);font-weight:400;font-size:1.15rem;letter-spacing:.03em}
.navlinks{display:flex;gap:6px;align-items:center;overflow-x:auto;scrollbar-width:none}
.navlinks a{text-decoration:none;font-size:.82rem;font-weight:600;color:var(--muted);padding:6px 11px;border-radius:999px;white-space:nowrap}
.navlinks a:hover{color:var(--ink);background:var(--paper)}
.navlinks a.on{color:var(--ink);background:var(--tint-soft)}
.btn{display:inline-flex;align-items:center;gap:8px;padding:11px 20px;border-radius:999px;font-weight:700;font-size:.9rem;text-decoration:none;border:1px solid var(--ink);background:var(--ink);color:var(--bg);white-space:nowrap;transition:transform .25s var(--ease)}
.btn:hover{transform:translateY(-2px)}
.btn.ghost{background:transparent;color:var(--ink);border-color:var(--line)}
@media (max-width:860px){.navlinks{display:none}}

/* header */
.c-hero{padding-block:64px 40px}
.kicker{display:flex;align-items:center;gap:12px}
.kicker::before{content:"";width:30px;height:2px;background:var(--tint)}
.kicker .mono{color:var(--tint)}
.c-title{font-family:var(--f-poster);text-transform:uppercase;font-size:clamp(3.4rem,10vw,8.6rem);line-height:.88;margin-top:18px}
.c-title .serif{display:block;color:var(--tint);font-size:.62em;line-height:1;margin-top:.12em}
.c-lede{max-width:58ch;font-size:clamp(1.08rem,1.6vw,1.28rem);margin-top:26px;line-height:1.55}
.fiche{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:0;border-top:1px solid var(--ink);margin-top:44px}
.fiche div{padding:14px 18px 14px 0;border-bottom:1px solid var(--line);display:flex;flex-direction:column;gap:3px}
.fiche dt{font-family:var(--f-mono);font-size:.68rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.fiche dd{margin:0;font-weight:600;font-size:.95rem;line-height:1.45}
.cover{margin-top:40px;border-radius:18px;overflow:hidden;border:1px solid var(--line);background:var(--paper);cursor:zoom-in;padding:0;display:block;width:100%}
.cover img{width:100%;max-height:78vh;object-fit:cover}

/* sections with sticky label */
.c-sec{display:grid;grid-template-columns:240px 1fr;gap:40px;padding-block:64px;border-top:1px solid var(--line)}
.c-sec > *{min-width:0}
.c-label{position:sticky;top:90px;align-self:start;display:flex;flex-direction:column;gap:6px}
.c-label .no{font-family:var(--f-poster);font-size:2.6rem;line-height:1;color:var(--tint)}
.c-label h2{font-family:var(--f-body);font-weight:800;font-size:1.25rem;letter-spacing:-.01em}
.c-body{display:flex;flex-direction:column;gap:18px;max-width:72ch}
.c-body p{font-size:1.05rem}
.c-body .intro{font-weight:700}
.goals{list-style:none;margin:0;padding:0;display:grid;gap:12px;counter-reset:g}
.goals li{counter-increment:g;display:grid;grid-template-columns:44px 1fr;gap:10px;align-items:baseline;padding:16px 18px;background:var(--paper);border:1px solid var(--line);border-radius:14px}
.goals li::before{content:"0" counter(g);font-family:var(--f-mono);font-size:.8rem;color:var(--tint);font-weight:500}
.bul{margin:0;padding:0;list-style:none;display:grid;gap:10px}
.bul li{position:relative;padding-left:26px}
.bul li::before{content:"";position:absolute;left:0;top:.62em;width:12px;height:2px;background:var(--tint)}
.steps{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;max-width:none}
.step{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:22px;display:flex;flex-direction:column;gap:8px}
.step .mono{color:var(--tint)}
.step h3{font-family:var(--f-body);font-weight:800;font-size:1.08rem}
.step p{font-size:.97rem;color:var(--ink);opacity:.86}
@media (max-width:860px){.c-sec{grid-template-columns:1fr;gap:18px;padding-block:48px}.c-label{position:static;flex-direction:row;align-items:baseline;gap:12px}.c-label .no{font-size:1.8rem}.steps{grid-template-columns:1fr}}

/* realisations */
.grp{padding-block:56px;border-top:1px solid var(--line)}
.grp-head{display:grid;grid-template-columns:1fr 1.1fr;gap:30px;align-items:end;margin-bottom:26px}
.grp-head h3{font-family:var(--f-serif);font-style:italic;font-size:clamp(1.9rem,3.6vw,2.8rem);line-height:1.05}
.grp-head p{color:var(--muted);font-size:1rem}
@media (max-width:860px){.grp-head{grid-template-columns:1fr;gap:10px}}
.gal{columns:3 260px;column-gap:18px}
.fig{break-inside:avoid;margin:0 0 22px;display:flex;flex-direction:column;gap:9px}
.tile{display:block;width:100%;padding:0;border:1px solid var(--line);border-radius:12px;overflow:hidden;background:var(--paper);cursor:zoom-in;position:relative}
.tile img{width:100%;transition:transform .8s var(--ease)}
.tile:hover img{transform:scale(1.035)}
.fig figcaption{font-size:.88rem;line-height:1.45;color:var(--muted);padding-right:6px}
.fig figcaption b{color:var(--ink);font-weight:700}
.more{display:flex;justify-content:center;margin-top:6px}
.strip{display:flex;gap:16px;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:14px;scrollbar-width:thin;scrollbar-color:var(--line) transparent}
.strip .fig{flex:none;width:300px;scroll-snap-align:start;margin:0}
.strip .tile img{height:400px;width:100%;object-fit:cover;object-position:top}
@media (max-width:620px){.gal{columns:1}.strip .fig{width:240px}.strip .tile img{height:320px}}

/* results */
.res{background:var(--ink);color:#F3EEE4;border-radius:24px;padding:48px;margin-block:64px;display:grid;grid-template-columns:1fr 1fr;gap:40px}
.res .mono{color:#A49C8D}
.res h2{font-family:var(--f-poster);text-transform:uppercase;font-size:clamp(2.4rem,5vw,3.8rem);line-height:.95;margin-top:10px}
.res h2 .serif{color:var(--tint-soft)}
.res-kpis{display:grid;gap:12px}
.res-kpi{border:1px solid #302B22;border-radius:14px;padding:16px 18px;display:flex;align-items:baseline;gap:14px}
.res-kpi b{font-family:var(--f-poster);font-weight:400;font-size:clamp(2rem,4vw,2.8rem);line-height:1;color:var(--tint-soft);white-space:nowrap}
.res-kpi span{font-size:.92rem;color:#CFC7B8}
.res-text{display:flex;flex-direction:column;gap:14px;margin-top:20px;color:#E6E0D4}
.res-note{font-size:.8rem;color:#A49C8D}
@media (max-width:860px){.res{grid-template-columns:1fr;padding:30px 22px;gap:24px}}
.learn{padding-block:30px 70px}
.learn blockquote{margin:0;font-family:var(--f-serif);font-style:italic;font-size:clamp(1.5rem,3vw,2.2rem);line-height:1.3;max-width:34ch}
.learn blockquote::before{content:"« ";color:var(--tint)}
.learn blockquote::after{content:" »";color:var(--tint)}

/* freelance */
.client{padding-block:60px;border-top:1px solid var(--line);scroll-margin-top:70px}
.client-head{display:grid;grid-template-columns:1fr 1fr;gap:36px;margin-bottom:28px}
.client-head h2{font-family:var(--f-poster);text-transform:uppercase;font-size:clamp(2.2rem,5vw,3.6rem);line-height:.95;margin-top:10px}
.client-head h2 .serif{display:block;color:var(--tint);font-size:.62em}
.client-body{display:flex;flex-direction:column;gap:14px}
.feedback{border-left:3px solid var(--tint);padding:12px 18px;background:var(--paper);border-radius:0 12px 12px 0;font-size:.98rem}
.feedback .mono{display:block;margin-bottom:4px}
@media (max-width:860px){.client-head{grid-template-columns:1fr;gap:16px}}

/* next */
.next{display:block;text-decoration:none;background:var(--ink);color:#F3EEE4;border-radius:24px;padding:40px;margin-block:30px 50px;position:relative;overflow:hidden}
.next .mono{color:#A49C8D}
.next h2{font-family:var(--f-poster);text-transform:uppercase;font-size:clamp(2.6rem,7vw,5.4rem);line-height:.9;margin-top:12px;transition:transform .5s var(--ease)}
.next h2 .serif{color:var(--ntint,#D9B36C)}
.next:hover h2{transform:translateX(12px)}
.next .arrow{position:absolute;right:40px;top:50%;translate:0 -50%;font-size:3rem;transition:transform .5s var(--ease)}
.next:hover .arrow{transform:translateX(8px)}
@media (max-width:620px){.next{padding:28px 22px}.next .arrow{display:none}}
footer{padding-block:26px;border-top:1px solid var(--line)}
footer .wrap{display:flex;flex-wrap:wrap;justify-content:space-between;gap:14px;align-items:center}

@media (prefers-reduced-motion: no-preference){
  .c-hero > *{animation:rise .9s var(--ease) both}
  .c-hero > :nth-child(2){animation-delay:.08s}.c-hero > :nth-child(3){animation-delay:.16s}.c-hero > :nth-child(4){animation-delay:.24s}.c-hero > :nth-child(5){animation-delay:.32s}
  @keyframes rise{from{opacity:0;transform:translateY(24px)}}
  [data-a]{transition:opacity .9s var(--ease),transform .9s var(--ease)}
  [data-a].pending{opacity:0;transform:translateY(50px)}
}
""" + LB_CSS

CASE_NAV = [('sushi-2-go', 'Sushi 2 Go'), ('hem-8', 'Hẻm 8'), ('cafe-koem', 'Café Koem'), ('duckee', 'Duckee'), ('freelance', 'Freelance')]

def page(title, desc, tint, tint_soft, body, active):
    nav = ''.join(f'<a href="{s}.html#top"{" class=%son%s" % (chr(34),chr(34)) if s==active else ""}>{e(n)}</a>' for s, n in CASE_NAV)
    return f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{FONTS}
<style>{CASE_CSS}</style>
<style>:root{{--tint:{tint};--tint-soft:{tint_soft}}}</style>
</head>
<body>
<span id="top"></span><div class="progress" aria-hidden="true"></div>
<nav aria-label="Navigation"><div class="wrap">
  <a class="back" href="index.html#projets" data-back>← <b>KEVIN NGUYEN</b></a>
  <div class="navlinks">{nav}</div>
  <a class="btn" href="index.html#contact">Me contacter</a>
</div></nav>
<main>
{body}
</main>
<footer><div class="wrap"><p class="mono">Duc Kien (Kevin) Nguyen · Portfolio 2026</p><a class="btn ghost" href="index.html#projets" data-back>← Tous les projets</a></div></footer>
{LIGHTBOX}
{CASE_JS}
</body>
</html>'''

def sec(no, title, inner):
    return f'<section class="wrap c-sec" data-a><div class="c-label"><span class="no">{no}</span><h2>{e(title)}</h2></div><div class="c-body">{inner}</div></section>'

def gallery(gid, items, n=9):
    figs = []
    for i, (f, cap) in enumerate(items):
        figs.append(f'<figure class="fig"{" hidden" if i >= n else ""}>{tile(f, cap)}<figcaption>{e(cap)}</figcaption></figure>')
    out = f'<div class="gal" id="{gid}" data-set>' + ''.join(figs) + '</div>'
    if len(items) > n:
        out += f'<div class="more"><button class="btn ghost" type="button" data-gal="{gid}">Voir les {len(items)-n} autres visuels ↓</button></div>'
    return out

def build_case(i, c):
    nxt = CASES[i + 1] if i + 1 < len(CASES) else None
    fiche = ''.join(f'<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k, v in c['fiche'])
    cap_cover = next((cap for g in c['groups'] for f, cap in g[2] if f == c['cover']), c['title'])
    body = f'''<header class="wrap c-hero">
  <div class="kicker"><span class="mono">{e(c["kicker"])}</span></div>
  <h1 class="c-title">{e(c["title"])}<span class="serif">{e(c["title_s"])}</span></h1>
  <p class="c-lede">{e(c["lede"])}</p>
  <dl class="fiche">{fiche}</dl>
  <div data-set><button class="cover tile" type="button" data-cap="{e(cap_cover)}" aria-label="Agrandir l’image de couverture">{img(c["cover"], cap_cover, lazy=False)}</button></div>
</header>'''
    body += sec('01', 'Contexte', ''.join(f'<p>{e(p)}</p>' for p in c['contexte']))
    body += sec('02', 'Objectifs', '<ol class="goals">' + ''.join(f'<li>{e(o)}</li>' for o in c['objectifs']) + '</ol>')
    body += sec('03', 'Mon rôle', f'<p class="intro">{e(c["role_intro"])}</p><ul class="bul">' + ''.join(f'<li>{e(r)}</li>' for r in c['role']) + '</ul>')
    steps = ''.join(f'<div class="step"><span class="mono">Étape {k+1}</span><h3>{e(t)}</h3><p>{e(d)}</p></div>' for k, (t, d) in enumerate(c['demarche']))
    body += sec('04', 'Démarche', f'<div class="steps">{steps}</div>')
    body += '<section class="wrap" id="realisations" style="padding-top:20px"><div class="c-sec" style="padding-bottom:0"><div class="c-label"><span class="no">05</span><h2>Réalisations</h2></div><div class="c-body"><p>Chaque visuel est présenté avec son contexte. Cliquez sur une image pour l’agrandir, puis utilisez les flèches pour parcourir la série.</p></div></div>'
    for k, (gt, gi, items) in enumerate(c['groups']):
        body += f'<div class="grp" data-a><div class="grp-head"><h3>{e(gt)}</h3><p>{e(gi)}</p></div>{gallery(f"g-{c["slug"]}-{k}", items)}</div>'
    if c.get('strip'):
        st, si, items = c['strip']
        figs = ''.join(f'<figure class="fig">{tile(f, cap)}<figcaption>{e(cap)}</figcaption></figure>' for f, cap in items)
        body += f'<div class="grp" data-a><div class="grp-head"><h3>{e(st)}</h3><p>{e(si)}</p></div><div class="strip" data-set>{figs}</div></div>'
    body += '</section>'
    kp = ''.join(f'<div class="res-kpi"><b>{e(a)}</b><span>{e(b)}</span></div>' for a, b in c['kpis'])
    note = f'<p class="res-note">{e(c["kpi_note"])}</p>' if c.get('kpi_note') else ''
    body += f'''<section class="wrap"><div class="res" data-a>
  <div><p class="mono">06 · Résultats</p><h2>Ce que le projet <span class="serif">a changé.</span></h2><div class="res-text">{"".join(f"<p>{e(p)}</p>" for p in c["resultats"])}</div></div>
  <div class="res-kpis">{kp}{note}</div>
</div></section>
<section class="wrap learn" data-a><p class="mono" style="margin-bottom:14px">07 · Ce que j’ai appris</p><blockquote>{e(c["appris"])}</blockquote></section>'''
    if nxt:
        body += f'<section class="wrap"><a class="next" href="{nxt["slug"]}.html#top" style="--ntint:{nxt["tint_soft"]}"><p class="mono">Projet suivant · {nxt["no"]}</p><h2>{e(nxt["title"])} <span class="serif">{e(nxt["title_s"])}</span></h2><span class="arrow" aria-hidden="true">→</span></a></section>'
    else:
        body += '<section class="wrap"><a class="next" href="freelance.html#top"><p class="mono">Et aussi</p><h2>Freelance <span class="serif">6 clients, 6 univers.</span></h2><span class="arrow" aria-hidden="true">→</span></a></section>'
    return page(f'{c["title"]} · Kevin Nguyen', c['lede'], c['tint'], c['tint_soft'], body, c['slug'])

def build_freelance():
    f = FREELANCE
    body = f'''<header class="wrap c-hero">
  <div class="kicker"><span class="mono">{e(f["kicker"])}</span></div>
  <h1 class="c-title">{e(f["title"])}<span class="serif">{e(f["title_s"])}</span></h1>
  <p class="c-lede">{e(f["lede"])}</p>
  <dl class="fiche">{"".join(f"<div><dt>{e(c['place'])}</dt><dd><a href='#{c['id']}' style='text-decoration:none'>{e(c['name'])} · {e(c['what'])} ↓</a></dd></div>" for c in f["clients"])}</dl>
</header>'''
    for k, c in enumerate(f['clients']):
        liv = ''.join(f'<li>{e(x)}</li>' for x in c['livrables'])
        fb = f'<div class="feedback"><span class="mono">Retour client</span>{e(c["retour"])}</div>' if c['retour'] else ''
        body += f'''<section class="wrap client" id="{c["id"]}" data-a>
  <div class="client-head">
    <div><p class="mono" style="color:var(--tint)">Client {k+1:02d} · {e(c["place"])}</p><h2>{e(c["name"])}<span class="serif">{e(c["what"])}</span></h2></div>
    <div class="client-body"><p>{e(c["contexte"])}</p><p class="mono">Ce que j’ai livré</p><ul class="bul">{liv}</ul>{fb}</div>
  </div>
  {gallery("g-fl-"+c["id"], c["imgs"], 6)}
</section>'''
    body += '<section class="wrap"><a class="next" href="sushi-2-go.html#top"><p class="mono">Retour aux projets</p><h2>Sushi 2 Go <span class="serif">de zéro à l’ouverture.</span></h2><span class="arrow" aria-hidden="true">→</span></a></section>'
    return page('Freelance · Kevin Nguyen', f['lede'], f['tint'], f['tint_soft'], body, 'freelance')

for i, c in enumerate(CASES):
    open(f'{OUT}/{c["slug"]}.html', 'w').write(build_case(i, c))
open(f'{OUT}/freelance.html', 'w').write(build_freelance())

# ---------------------------------------------------------------- HOME
s = open(ROOT + 'build/site/index.html').read()

HOME_CSS = """
/* ---- projets à la une ---- */
.pcards{display:flex;flex-direction:column;gap:22px;margin-top:50px}
.pcard{display:grid;grid-template-columns:1.1fr 1fr;gap:0;border:1px solid var(--line);border-radius:24px;overflow:hidden;background:var(--surface);text-decoration:none;color:inherit;position:relative;transition:border-color .4s,transform .5s var(--ease)}
.pcard:hover{border-color:var(--pt);transform:translateY(-4px)}
.pcard:nth-child(even){grid-template-columns:1fr 1.1fr}
.pcard:nth-child(even) .pc-media{order:2}
.pc-media{position:relative;overflow:hidden;aspect-ratio:16/11;background:var(--surface-2)}
.pc-media img{width:100%;height:100%;object-fit:cover;display:block;transition:transform 1.2s var(--ease)}
.pcard:hover .pc-media img{transform:scale(1.04)}
.pc-text{padding:34px 36px;display:flex;flex-direction:column;gap:14px;min-width:0}
.pc-text .mono{color:var(--pt)}
.pc-text h3{font-family:var(--f-poster);text-transform:uppercase;font-size:clamp(2.4rem,4.6vw,3.8rem);line-height:.92}
.pc-text h3 .serif{display:block;color:var(--pt);font-size:.62em;line-height:1.05}
.pc-text p{color:var(--muted)}
.pc-kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:4px}
.pc-kpis div{border:1px solid var(--line);border-radius:12px;padding:12px;display:flex;flex-direction:column;gap:2px}
.pc-kpis b{font-family:var(--f-poster);font-weight:400;font-size:1.55rem;line-height:1;color:var(--fg)}
.pc-kpis span{font-size:.74rem;color:var(--muted);line-height:1.3}
.pc-cta{margin-top:auto;display:inline-flex;align-items:center;gap:10px;font-weight:800;padding-top:10px}
.pc-cta i{font-style:normal;display:inline-grid;place-items:center;width:38px;height:38px;border-radius:50%;background:var(--pt);color:#0D0C0A;transition:transform .4s var(--ease)}
.pcard:hover .pc-cta i{transform:translateX(6px) rotate(-45deg)}
@media (max-width:900px){.pcard,.pcard:nth-child(even){grid-template-columns:1fr}.pcard:nth-child(even) .pc-media{order:0}.pc-text{padding:24px 22px}}
@media (max-width:420px){.pc-kpis{grid-template-columns:1fr 1fr}.pc-kpis div:last-child{grid-column:span 2}}

/* ---- à propos ---- */
.about{display:grid;grid-template-columns:.8fr 1.2fr;gap:56px;align-items:center}
.about-photo{position:relative;max-width:380px}
.about-photo img{border-radius:20px;aspect-ratio:4/5;object-fit:cover;width:100%;filter:grayscale(.15)}
.about-photo .tag{position:absolute;left:-14px;bottom:24px;background:var(--gold);color:var(--gold-ink);padding:10px 14px;border-radius:12px;font-family:var(--f-mono);font-size:.7rem;text-transform:uppercase;letter-spacing:.06em;rotate:-4deg}
.about-photo .tag b{display:block;font-family:var(--f-poster);font-weight:400;font-size:1.5rem;letter-spacing:0}
.about-text{display:flex;flex-direction:column;gap:16px;font-size:1.05rem;max-width:62ch}
.about-text p{opacity:.88}
.values{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:8px}
.values div{border:1px solid var(--line);border-radius:14px;padding:14px;background:var(--surface)}
.values b{display:block;font-family:var(--f-serif);font-style:italic;font-weight:400;font-size:1.35rem;color:var(--gold)}
.values span{font-size:.86rem;color:var(--muted)}
@media (max-width:900px){.about{grid-template-columns:1fr;gap:30px}.about-photo{max-width:280px}}
@media (max-width:560px){.values{grid-template-columns:1fr}}

/* ---- méthode ---- */
.method{display:grid;grid-template-columns:repeat(5,1fr);gap:0;margin-top:50px;border-top:1px solid var(--line)}
.mstep{padding:24px 20px 10px 0;display:flex;flex-direction:column;gap:10px;position:relative}
.mstep::before{content:"";position:absolute;top:-5px;left:0;width:9px;height:9px;border-radius:50%;background:var(--gold)}
.mstep .mono{color:var(--gold)}
.mstep h3{font-family:var(--f-body);font-weight:800;font-size:1.08rem}
.mstep p{font-size:.92rem;color:var(--muted)}
.mstep em{font-style:normal;font-size:.8rem;color:var(--fg);border:1px solid var(--line);border-radius:999px;padding:3px 10px;align-self:flex-start;background:var(--surface)}
@media (max-width:1000px){.method{grid-template-columns:1fr 1fr;row-gap:10px}}
@media (max-width:560px){.method{grid-template-columns:1fr}}

/* ---- planning ---- */
.plan{border:1px solid var(--line);border-radius:var(--r);background:var(--surface);padding:40px;display:grid;grid-template-columns:.85fr 1.15fr;gap:44px;align-items:start}
.plan-chart{min-width:0}
.bars{display:grid;grid-template-columns:repeat(12,1fr);gap:8px;align-items:end;height:240px;border-bottom:1px solid var(--line);padding-bottom:0}
.bar{display:flex;flex-direction:column-reverse;gap:3px;height:100%;justify-content:flex-start}
.bar i{display:block;border-radius:5px;min-height:2px;transform-origin:bottom}
.bar .ent{background:var(--gold)}
.bar .eco{background:var(--surface-2);border:1px solid var(--line)}
.bar-l{display:grid;grid-template-columns:repeat(12,1fr);gap:8px;margin-top:8px;font-family:var(--f-mono);font-size:.62rem;color:var(--muted);text-align:center;text-transform:uppercase}
.plan-tot{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:22px}
.plan-tot div{border:1px solid var(--line);border-radius:12px;padding:12px 14px;background:var(--bg)}
.plan-tot b{display:block;font-family:var(--f-poster);font-weight:400;font-size:1.8rem;line-height:1.1}
.plan-tot span{font-size:.8rem;color:var(--muted)}
.now{display:inline-flex;align-items:center;gap:10px;background:color-mix(in srgb,var(--good) 14%,transparent);border:1px solid color-mix(in srgb,var(--good) 40%,transparent);color:var(--fg);padding:9px 14px;border-radius:12px;font-weight:700;font-size:.92rem;margin-top:20px}
@media (max-width:900px){.plan{grid-template-columns:1fr;padding:26px 18px;gap:28px}.bars{height:180px;gap:4px}.bar-l{gap:4px;font-size:.52rem}}
@media (prefers-reduced-motion: no-preference){
  .bars i{transition:transform .9s var(--ease);transition-delay:calc(var(--i) * 50ms)}
  .bars.pending{opacity:1}.bars.pending i{transform:scaleY(0)}
}

/* ---- FAQ ---- */
.faq{margin-top:44px;border-top:1px solid var(--line)}
.faq details{border-bottom:1px solid var(--line)}
.faq summary{list-style:none;cursor:pointer;display:flex;justify-content:space-between;gap:20px;align-items:center;padding:22px 0;font-weight:800;font-size:1.1rem}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";font-family:var(--f-mono);font-size:1.3rem;color:var(--gold);transition:transform .3s}
.faq details[open] summary::after{transform:rotate(45deg)}
.faq details p{padding:0 0 22px;max-width:70ch;color:var(--muted)}
.faq details p b{color:var(--fg)}

.fcard a.cover{cursor:pointer}
"""
HERO_CSS = r'''
/* ---- hero portrait v2 ---- */
.hero-visual{position:relative;justify-self:center;width:100%;max-width:400px;display:flex;flex-direction:column;align-items:stretch}
.arch{position:relative;aspect-ratio:4/5;border-radius:999px 999px 26px 26px;overflow:hidden;border:1px solid color-mix(in srgb,var(--gold) 45%,var(--line));
  background:radial-gradient(120% 80% at 50% 18%,color-mix(in srgb,var(--gold) 38%,transparent),transparent 62%),linear-gradient(180deg,#2A2418,#14120E 75%)}
.arch::before{content:"";position:absolute;inset:14px;border-radius:999px 999px 18px 18px;border:1px solid color-mix(in srgb,var(--gold) 22%,transparent);pointer-events:none;z-index:1}
.arch img{position:absolute;left:50%;bottom:0;width:96%;transform:translateX(-50%);height:auto;max-width:none}
.nameplate{margin-top:-1px;background:var(--surface);border:1px solid var(--line);border-top:0;border-radius:0 0 18px 18px;padding:14px 18px;display:flex;justify-content:space-between;align-items:center;gap:12px}
.nameplate b{white-space:nowrap;font-family:var(--f-poster);font-weight:400;font-size:clamp(1rem,3.4vw,1.25rem);letter-spacing:.02em;text-transform:uppercase}
.nameplate span{font-family:var(--f-mono);font-size:.66rem;letter-spacing:.07em;text-transform:uppercase;color:var(--gold);text-align:right}
.hchip{position:absolute;display:flex;flex-direction:column;gap:1px;padding:10px 14px;border-radius:14px;background:color-mix(in srgb,var(--bg) 70%,transparent);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border:1px solid var(--line);box-shadow:0 16px 40px rgba(0,0,0,.35);z-index:2}
.hchip b{font-family:var(--f-poster);font-weight:400;font-size:1.5rem;line-height:1.05;color:var(--gold)}
.hchip span{font-size:.72rem;color:var(--muted);line-height:1.3}
.hchip.c1{left:-12%;top:30%}.hchip.c2{right:-10%;top:58%}
@media (max-width:900px){.hero-visual{max-width:300px}.hchip.c1{left:-6%}.hchip.c2{right:-6%}}
/* ---- hero CTA v2 ---- */
.cta{align-items:center}
.btn-alt{position:relative;display:inline-flex;align-items:center;gap:14px;padding:12px 14px 12px 20px;border-radius:999px;background:var(--gold);color:var(--gold-ink);text-decoration:none;font-weight:800;font-size:1rem;transition:transform .25s var(--ease)}
.btn-alt small{display:block;font-family:var(--f-mono);font-weight:500;font-size:.64rem;letter-spacing:.07em;text-transform:uppercase;opacity:.75}
.btn-alt i{font-style:normal;display:grid;place-items:center;width:36px;height:36px;border-radius:50%;background:var(--gold-ink);color:var(--gold);transition:transform .3s var(--ease)}
.btn-alt:hover{transform:translateY(-2px)}.btn-alt:hover i{transform:translateY(3px)}
.btn-about{display:inline-flex;align-items:center;gap:10px;padding:12px 20px;border-radius:999px;border:1px solid color-mix(in srgb,var(--gold) 60%,var(--line));color:var(--fg);text-decoration:none;font-weight:700;transition:background .25s,transform .25s var(--ease)}
.btn-about:hover{background:var(--surface-2);transform:translateY(-2px)}
.btn-link{color:var(--muted);font-weight:700;font-size:.92rem;text-decoration:none;border-bottom:1px solid var(--line);padding-bottom:2px}
.btn-link:hover{color:var(--fg)}
@media (prefers-reduced-motion: no-preference){
  .btn-alt{animation:glow 2.6s 2.2s infinite}
  @keyframes glow{0%{box-shadow:0 0 0 0 color-mix(in srgb,var(--gold) 55%,transparent)}70%{box-shadow:0 0 0 14px transparent}100%{box-shadow:0 0 0 0 transparent}}
  .hero-visual{animation:rise 1.1s 1s var(--ease) both}
  .hchip.c1{animation:pop .7s 1.7s cubic-bezier(.3,1.5,.5,1) both}.hchip.c2{animation:pop .7s 1.85s cubic-bezier(.3,1.5,.5,1) both}
}
'''
s = s.replace('</style>', HOME_CSS + HERO_CSS + '</style>', 1)

import re as _re
pw, ph = dim('portrait-cut')
s, n1 = _re.subn(r'<div class="card-photo">.*?<div class="core">↓</div>\s*</div>\s*</div>', f'''<div class="hero-visual">
        <div class="arch"><img src="img/portrait-cut.webp" alt="Portrait de Duc Kien (Kevin) Nguyen" width="{pw}" height="{ph}"></div>
        <div class="nameplate"><b>Kevin Nguyen</b><span>Assistant marketing<br>Alternance · Master 2</span></div>
        <div class="hchip c1"><b>+50 %</b><span>de CA en 2 mois</span></div>
        <div class="hchip c2"><b>9 marques</b><span>accompagnées en 6 ans</span></div>
      </div>''', s, count=1, flags=_re.S)
assert n1 == 1
s, n2 = _re.subn(r'<div class="cta">\s*<a class="btn gold" href="#projets">Voir les résultats →</a>.*?</div>', '''<div class="cta">
          <a class="btn-alt" href="#alternance"><span><small>Disponible immédiatement</small>Je cherche une alternance</span><i>↓</i></a>
          <a class="btn-about" href="#apropos">Qui suis-je ?</a>
          <a class="btn-link" href="#projets">Voir les projets ↓</a>
        </div>''', s, count=1, flags=_re.S)
assert n2 == 1
# hero status
s = s.replace('Assistant marketing en alternance · dès novembre 2026 · Île-de-France', 'Disponible immédiatement · alternance 12 mois · Île-de-France')
s = s.replace('Oct. 2024 – avr. 2025', 'Oct. 2024 – juin 2025')
s = s.replace('<a href="#atouts" class="hide-sm">Atouts</a>', '<a href="#atouts" class="hide-sm">Atouts</a><a href="#apropos" class="hide-sm">À propos</a>')
s = s.replace('<a href="#parcours" class="hide-sm">Parcours</a>', '<a href="#alternance" class="hide-sm">Alternance</a>')

# projects + about + method + planning replace alternance..reel
pc = ''
for c in CASES:
    COV = {'sushi-2-go':'cover-sushi','hem-8':'cover-hem8','cafe-koem':'cover-koem','duckee':'cover-duckee'}
    imgs = img(COV[c['slug']], 'Aperçu des visuels du projet ' + c['title'], True)
    k = ''.join(f'<div><b>{e(a)}</b><span>{e(b)}</span></div>' for a, b in c['card_kpis'])
    pc += f'''<a class="pcard" href="{c["slug"]}.html#top" style="--pt:{c["tint_soft"] if False else c["tint"]}" data-a="up">
  <div class="pc-media" aria-hidden="true">{imgs}</div>
  <div class="pc-text"><p class="mono">{e(c["kicker"])}</p><h3>{e(c["title"])}<span class="serif">{e(c["title_s"])}</span></h3><p>{e(c["card_line"])}</p><div class="pc-kpis">{k}</div><span class="pc-cta">Lire l’étude de cas <i>→</i></span></div>
</a>'''
# brighter tints on dark
BRIGHT = {'sushi-2-go': '#F37A52', 'hem-8': '#F59A3A', 'cafe-koem': '#EE6670', 'duckee': '#EE6FAA'}
for slug, col in BRIGHT.items():
    pc = pc.replace(f'href="{slug}.html#top" style="--pt:', f'href="{slug}.html#top" style="--pt:{col};--x:')

# planning data (Sup de Pub, nov. 2026 – oct. 2027)
months = ['Nov','Déc','Janv','Févr','Mars','Avr','Mai','Juin','Juil','Août','Sept','Oct']
ent = [15,17,10,15,15,15,14,13,21,22,16,16]
eco = [5,5,10,5,7,7,6,9,0,0,6,5]
mx = max(a + b for a, b in zip(ent, eco))
bars = ''.join(f'<div class="bar" title="{m} : {a} jours en entreprise, {b} à l’école"><i class="ent" style="height:{a/mx*100:.1f}%;--i:{k}"></i><i class="eco" style="height:{b/mx*100:.1f}%;--i:{k}"></i></div>' for k, (m, a, b) in enumerate(zip(months, ent, eco)))
labels = ''.join(f'<span>{m}</span>' for m in months)
TE, TS = sum(ent), sum(eco)

NEW_MID = f'''
  <div id="projets"></div>
  <section data-tint="#D9B36C" style="padding-top:0">
    <div class="wrap">
      <div class="kicker" data-a="left"><span class="mono">Projets à la une</span></div>
      <h2 class="big" data-a="title">Quatre marques, <span class="serif">quatre résultats.</span></h2>
      <p class="lead" data-a="up">Chaque projet a sa propre étude de cas : le contexte, mon rôle exact, la démarche, tous les visuels expliqués un par un, et les résultats.</p>
      <div class="pcards">{pc}</div>
    </div>
  </section>

  <section id="apropos" data-tint="#D9B36C">
    <div class="wrap about">
      <div class="about-photo" data-a="left"><img src="img/portrait.webp" alt="Duc Kien (Kevin) Nguyen" width="{dim('portrait')[0]}" height="{dim('portrait')[1]}" loading="lazy"><div class="tag"><b>DELF B2</b>Français professionnel</div></div>
      <div class="about-text" data-a="up">
        <div class="kicker"><span class="mono">À propos</span></div>
        <h2 class="big" style="font-size:clamp(2.4rem,5.4vw,4.2rem)">Entre <span class="serif">Hanoï</span> et <span class="serif">Paris.</span></h2>
        <p>Je m’appelle Duc Kien Nguyen, et tout le monde m’appelle Kevin. J’ai lancé ma première marque à Hanoï en 2019, puis j’ai dirigé le marketing de restaurants et de cafés avant de m’installer en France en 2022 pour mes études.</p>
        <p>Depuis, j’ai travaillé sur des projets à Nantes, Luçon et Aix-en-Provence. Ce que j’aime le plus : partir d’une idée, la transformer en marque visible, puis mesurer ce qu’elle rapporte.</p>
        <p>Je cherche une équipe où apprendre vite, et où mon expérience du terrain et ma double culture Europe – Asie peuvent servir dès la première semaine.</p>
        <div class="values">
          <div><b>Autonome</b><span>J’ai porté seul le lancement de Sushi 2 Go et ma propre entreprise.</span></div>
          <div><b>Orienté résultats</b><span>Chaque action est suivie d’un chiffre : CA, abonnés, interactions.</span></div>
          <div><b>Créatif</b><span>Je conçois moi-même les visuels, du post Instagram au roll-up.</span></div>
        </div>
      </div>
    </div>
  </section>

  <section id="methode" data-tint="#D9B36C" style="padding-top:0">
    <div class="wrap">
      <div class="kicker" data-a="left"><span class="mono">Ma méthode</span></div>
      <h2 class="big" data-a="title">Comprendre, créer, <span class="serif">mesurer.</span></h2>
      <div class="method" data-a="up">
        <div class="mstep"><span class="mono">01</span><h3>Comprendre</h3><p>Qui est le client, pourquoi il ne vient pas, ce qui le ferait revenir.</p><em>Hẻm 8 après le Covid</em></div>
        <div class="mstep"><span class="mono">02</span><h3>Positionner</h3><p>Un angle clair et un nom qui le portent.</p><em>Sushi 2 Go</em></div>
        <div class="mstep"><span class="mono">03</span><h3>Créer</h3><p>Une identité et des contenus reconnaissables au premier coup d’œil.</p><em>Série Fruit tea</em></div>
        <div class="mstep"><span class="mono">04</span><h3>Lancer</h3><p>Réseaux sociaux, publicité ciblée, terrain et événements, ensemble.</p><em>Meta Ads + flyers</em></div>
        <div class="mstep"><span class="mono">05</span><h3>Mesurer</h3><p>Suivre les chiffres et ajuster l’action suivante.</p><em>+50 % de CA</em></div>
      </div>
    </div>
  </section>

  <section id="alternance" data-tint="#D9B36C" style="padding-top:0">
    <div class="wrap">
      <div class="plan" data-a="zoom">
        <div>
          <div class="kicker"><span class="mono">Ma recherche</span></div>
          <h2 class="big" style="font-size:clamp(2.2rem,4.6vw,3.6rem)">Assistant marketing <span class="serif">en alternance</span></h2>
          <div class="facts">
            <div class="fact"><span>Contrat</span><span>Alternance · 12 mois</span></div>
            <div class="fact"><span>Démarrage</span><span>Immédiat</span></div>
            <div class="fact"><span>Rythme</span><span>En moyenne 1 semaine à l’école, 2 à 3 semaines en entreprise</span></div>
            <div class="fact"><span>Été</span><span>100 % en entreprise en juillet et août</span></div>
            <div class="fact"><span>École</span><span>Sup de Pub Paris · Master 2</span></div>
            <div class="fact"><span>Lieu</span><span>Île-de-France en priorité</span></div>
          </div>
          <p class="now"><span class="dot" aria-hidden="true"></span>Je peux commencer dès cette semaine.</p>
        </div>
        <div class="plan-chart">
          <p class="mono" style="margin-bottom:14px">Calendrier officiel Sup de Pub · nov. 2026 → oct. 2027 · jours par mois</p>
          <div class="bars" data-a="bars" role="img" aria-label="Sur 12 mois : {TE} jours en entreprise et {TS} jours à l’école">{bars}</div>
          <div class="bar-l" aria-hidden="true">{labels}</div>
          <div class="legend"><span><i style="background:var(--gold)"></i>Entreprise</span><span><i style="background:var(--surface-2);border:1px solid var(--line)"></i>École</span></div>
          <div class="plan-tot">
            <div><b>{TE}</b><span>jours en entreprise</span></div>
            <div><b>{TS}</b><span>jours à l’école</span></div>
            <div><b>{round(TE/(TE+TS)*100)} %</b><span>du temps dans votre équipe</span></div>
          </div>
        </div>
      </div>
    </div>
  </section>
'''
a = s.index('  <section id="alternance"')
b = s.index('  <!-- FREELANCE reel -->')
s = s[:a] + NEW_MID + s[b:]
# remove leftover anchor div from old template (projets was before chapters, now inside NEW_MID)
s = s.replace('<div id="projets"></div>\n\n  <!-- 01 SUSHI 2 GO -->', '')

# reel: covers become links to freelance page
reel_cards = ''
covers = {'vietway-sale': 'fl-sa-3', 'vietway-sucre': 'fl-sw-a1t', 'leclerc': 'fl-lc-17', 'aix': 'fl-aix-1', 'komi': 'fl-komi-1', 'tarot': 'fl-tarot-logo'}
short = {'vietway-sale': 'Panneaux illustrés pour 9 spécialités et 3 roll-ups.', 'vietway-sucre': 'Affiches A1, roll-ups bilingues, bannières du comptoir.',
         'leclerc': 'Affiches, flyer et bannières du corner sushi en supermarché.', 'aix': 'Trois déclinaisons de menu pour un comptoir japonais.',
         'komi': 'Menus des boissons et des toppings, doux et lisibles.', 'tarot': 'Logo, menus, bon cadeau, et le logo d’une boutique de fleurs.'}
for c in FREELANCE['clients']:
    cv = covers[c['id']]
    reel_cards += f'<article class="fcard"><a class="cover" href="freelance.html#{c["id"]}" aria-label="Voir le projet {e(c["name"])} : {e(c["what"])}">{img(cv, c["what"])}<span>{len(c["imgs"])} visuels · voir le projet</span></a><p class="mono">{e(c["name"])} · {e(c["place"])}</p><h3>{e(c["what"])}</h3><p>{e(short[c["id"]])}</p></article>'
s = re.sub(r'<div class="track">.*?</div></div>', '<div class="track">' + reel_cards + '</div></div>', s, count=1, flags=re.S)
s = re.sub(r'\s*<div hidden id="fl-data">.*?</div>\n', '\n', s, count=1, flags=re.S)
s = s.replace('<h2 class="big" style="font-size:clamp(2.4rem,6vw,4.6rem)">6 clients, <span class="serif">6 univers.</span></h2>',
              '<h2 class="big" style="font-size:clamp(2.4rem,6vw,4.6rem)">6 clients, <span class="serif">6 univers.</span></h2><p style="margin-top:12px"><a class="btn" href="freelance.html">Voir tous les projets freelance →</a></p>')

# FAQ before contact
FAQ = '''
  <section id="faq" data-tint="#D9B36C" style="padding-top:0">
    <div class="wrap">
      <div class="kicker" data-a="left"><span class="mono">Questions fréquentes</span></div>
      <h2 class="big" data-a="title">Vos questions, <span class="serif">mes réponses.</span></h2>
      <div class="faq" data-a="up">
        <details open><summary>Quand pouvez-vous commencer ?</summary><p><b>Immédiatement.</b> Le calendrier de Sup de Pub prévoit déjà des périodes en entreprise en novembre 2026 : je peux rejoindre votre équipe dès cette semaine.</p></details>
        <details><summary>Quel est votre rythme d’alternance ?</summary><p>Un contrat de <b>12 mois</b>, avec en moyenne <b>1 semaine à l’école pour 2 à 3 semaines en entreprise</b>, et <b>100 % en entreprise en juillet et août</b>. Sur un an, cela représente environ 189 jours dans votre équipe pour 65 jours de cours.</p></details>
        <details><summary>Quel est votre niveau de français ?</summary><p>J’ai le <b>DELF B2</b>. J’étudie et je travaille en français depuis 2022, à Reims, Rennes, Serris et Nantes.</p></details>
        <details><summary>Où souhaitez-vous travailler ?</summary><p><b>En Île-de-France en priorité.</b> J’ai déjà travaillé sur des projets dans plusieurs villes de France (Nantes, Luçon, Aix-en-Provence) : les déplacements ponctuels ne me posent aucun problème.</p></details>
        <details><summary>Pouvez-vous travailler en autonomie ?</summary><p>Oui. J’ai géré seul le pôle marketing de Vietinnovation jusqu’à l’ouverture de Sushi 2 Go, et j’ai dirigé ma propre entreprise pendant trois ans. Je sais aussi travailler en binôme : chez Fusio, nous étions deux au marketing.</p></details>
        <details><summary>Quels outils maîtrisez-vous ?</summary><p>Illustrator, Photoshop, InDesign, Premiere Pro, Canva, CapCut pour la création ; Meta Ads, Google Ads et Google Analytics pour l’acquisition et le suivi ; le Pack Office au quotidien. Certification Adobe Illustrator (ColorME, 2019).</p></details>
      </div>
    </div>
  </section>
'''
s = s.replace('  <section class="contact" id="contact"', FAQ + '  <section class="contact" id="contact"', 1)
s = s.replace('Je recherche une alternance d’assistant marketing à partir de novembre 2026, au rythme 1 semaine école / 2 semaines entreprise.',
              'Je recherche une alternance d’assistant marketing de 12 mois, disponible immédiatement, au rythme d’une semaine à l’école pour deux à trois semaines en entreprise.')

# JS: drop lightbox-from-cover handler; bars reveal handled by data-a
s = re.sub(r"  document\.querySelectorAll\('\.fcard \.cover'\)\.forEach\(function\(b\)\{b\.addEventListener\('click',function\(\)\{\n.*?\n.*?\n  \}\)\}\);\n", '', s, count=1, flags=re.S)
s = s.replace('[data-a="title"],[data-a="bars"],[data-a="tiles"]{transition:none}', '[data-a="title"],[data-a="bars"],[data-a="tiles"]{transition:none}\n  .bars[data-a="bars"] i{transition:transform .9s var(--ease);transition-delay:calc(var(--i) * 50ms)}\n  .bars[data-a="bars"].pending i{transform:scaleY(0)}')
a_ = "if(!reduce)heroIn.style.setProperty('--hp',"
assert a_ in s
s = s.replace(a_, "if(!reduce&&matchMedia('(min-width:901px) and (min-height:700px)').matches)heroIn.style.setProperty('--hp',", 1)
b_ = "(el.closest('.proof')?1400:0)"
assert b_ in s
s = s.replace(b_, "(el.closest('.proof')&&performance.now()<2500?1400:0)", 1)
assert '{{' not in s
open(f'{OUT}/index.html', 'w').write(s)
print('ok', [f for f in os.listdir(OUT) if f.endswith('.html')])
