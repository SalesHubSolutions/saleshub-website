#!/usr/bin/env python3
"""Build saleshub.info as static pages for GitHub Pages.

Pages live as <name>.html so the old GoDaddy URLs (no trailing slash) keep working.
Old URLs that no longer have their own page get a small forwarding page.
Blog posts are rebuilt from the backup taken on 2026-11-15 (../saleshub-backup/posts).
"""
import html, json, os, re, glob, shutil, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP = os.path.join(os.path.dirname(ROOT), 'saleshub-backup')
SITE = 'https://saleshub.info'
NPS = 'https://www.npssurveys.com/?utm_source=saleshub.info&utm_medium=website&utm_campaign=company_site&utm_content='
TRIAL = 'https://appexchange.salesforce.com/appxListingDetail?listingId=a0N3A00000FtRTKUA3&tab=e&utm_source=saleshub.info&utm_medium=website&utm_campaign=company_site'
PHONE, PHONE_TEL, EMAIL = '(833) 733-2468', '+18337332468', 'support@saleshub.info'
ADDR = '1853 Piedmont Rd NE, Suite 301<br>Marietta, GA 30066'
YEAR = datetime.date.today().year
SITEMAP = []

NAV = [('NPS Survey', NPS + 'nav', None), ('Offshore Delivery Pod', '/offshore-delivery-pod', 'pod'),
       ('Salesforce Services', '/salesforce-services', 'sf'), ('Government', '/government-services', 'gov'),
       ('About', '/about', 'about'), ('Contact', '/contact-us', 'contact')]

MARK = ('<svg viewBox="0 0 100 100" width="52" height="52" aria-hidden="true"><rect width="100" height="100" rx="22" fill="#002FA7"/>'
        '<g transform="translate(18 16) scale(.64)"><path d="M31.07 77.03 A33 33 0 1 1 68.93 77.03" fill="none" stroke="#fff" stroke-width="15" stroke-linecap="round"/>'
        '<circle cx="50" cy="83" r="7.5" fill="#fff"/></g></svg>')
TICK = ('<span class="tick"><svg width="12" height="12" viewBox="0 0 20 20"><path d="M4 10.5l4 4 8-9" fill="none" stroke="#002FA7" '
        'stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg></span>')

ORG = {"@context": "https://schema.org", "@type": "Organization", "name": "SalesHub, LLC", "url": SITE + "/",
       "logo": "https://www.npssurveys.com/brand/logo-kit/png/nps-survey-app-icon.png", "email": EMAIL,
       "telephone": "+1-833-733-2468", "foundingDate": "2018",
       "address": {"@type": "PostalAddress", "streetAddress": "1853 Piedmont Rd NE, Suite 301", "addressLocality": "Marietta",
                   "addressRegion": "GA", "postalCode": "30066", "addressCountry": "US"},
       "sameAs": ["https://www.linkedin.com/company/12673581", "https://www.youtube.com/@saleshubllc", "https://www.npssurveys.com"]}


def page(path, title, desc, body, active=None, schema=None, canonical=None, noindex=False):
    nav = ''.join(f'<li><a href="{h}"{" aria-current=page" if k and k == active else ""}>{n}</a></li>' for n, h, k in NAV)
    url = SITE + (canonical or ('/' if path == 'index' else '/' + path))
    ld = json.dumps(schema or ORG, ensure_ascii=False)
    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="theme-color" content="#002FA7">
{'<meta name="robots" content="noindex">' if noindex else ''}
<link rel="icon" type="image/svg+xml" href="https://www.npssurveys.com/favicon.svg">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:image" content="https://www.npssurveys.com/share.png">
<meta property="og:url" content="{url}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css?v=20261116b">
<script type="application/ld+json">{ld}</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-BF2FDR6KMM"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag("js",new Date());gtag("config","G-BF2FDR6KMM",{{linker:{{domains:["saleshub.info","npssurveys.com"]}}}});</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="blue"><div class="wrap nav">
 <a class="word" href="/" aria-label="SalesHub home">SalesHub</a>
 <button class="menu" aria-expanded="false" aria-controls="navlist">Menu</button>
 <ul id="navlist">{nav}</ul>
 <a class="btn w" href="/contact-us">Talk to us</a>
</div></header>
<main id="main">
{body}
</main>
<footer><div class="wrap">
 <div class="fgrid">
  <div><b>SalesHub, LLC</b>Makers of NPS Survey CX OS for Salesforce.<br>{ADDR}<br><a href="tel:{PHONE_TEL}">{PHONE}</a> · <a href="mailto:{EMAIL}">{EMAIL}</a></div>
  <div><b>Product</b><ul><li><a href="{NPS}footer">NPS Survey CX OS</a></li><li><a href="{TRIAL}">AppExchange listing</a></li><li><a href="/security-&amp;-trust">Security &amp; Trust</a></li></ul></div>
  <div><b>Services</b><ul><li><a href="/offshore-delivery-pod">Offshore Delivery Pod</a></li><li><a href="/salesforce-services">Salesforce Services</a></li><li><a href="/government-services">Government Services</a></li></ul></div>
  <div><b>Company</b><ul><li><a href="/about">About</a></li><li><a href="/blog">Blog</a></li><li><a href="/careers">Careers</a></li><li><a href="/contact-us">Contact</a></li><li><a href="/privacy-policy">Privacy Policy</a></li><li><a href="/data-processing-addendum">Data Processing Addendum</a></li></ul></div>
 </div>
 <div class="fbot"><span>© {YEAR} SalesHub, LLC. All rights reserved.</span><span><a href="https://www.linkedin.com/company/12673581">LinkedIn</a> · <a href="https://www.youtube.com/@saleshubllc">YouTube</a></span></div>
</div></footer>
<script>
(function(){{var b=document.querySelector('.menu'),u=document.getElementById('navlist');b.addEventListener('click',function(){{var o=u.classList.toggle('open');b.setAttribute('aria-expanded',o)}});
var f=document.querySelector('form.lead');if(f)f.addEventListener('submit',function(){{var s=f.querySelector('#int'),m=f.querySelector('#msg'),d=document.createElement('input');d.type='hidden';d.name='description';d.value=s.value+(m.value?': '+m.value:'')+' ('+location.pathname+')';s.removeAttribute('name');m.removeAttribute('name');f.appendChild(d);try{{gtag('event','ads_conversion_Contact_Us_1');gtag('event','generate_lead',{{form:'saleshub.info',interest:s.value}})}}catch(_){{}}}});}})();
</script>
</body>
</html>
'''
    write(path + '.html', doc)
    if not noindex:
        SITEMAP.append(url)


def write(rel, text):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(text)


def forward(rel, target):
    t = html.escape(target)
    write(rel, f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Moved</title>
<meta http-equiv="refresh" content="0; url={t}"><link rel="canonical" href="{t if target.startswith('http') else SITE + t}">
<meta name="robots" content="noindex"><script>location.replace({json.dumps(target)}+location.hash)</script></head>
<body><p>This page has moved to <a href="{t}">{t}</a>.</p></body></html>''')


def hero(h1, lead, crumb=None, cta=''):
    c = f'<div class="crumb">{crumb}</div>' if crumb else ''
    return f'<section class="hero page blue"><div class="wrap">{c}<h1>{h1}</h1><p class="lead">{lead}</p>{cta}</div></section>'


def checks(items):
    return '<ul class="checks">' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'


def band(title, text, btn='Book a call', href='/contact-us'):
    return f'<section class="s"><div class="wrap"><div class="band blue"><div><h2>{title}</h2><p>{text}</p></div><a class="btn w" href="{href}">{btn}</a></div></div></section>'


def form(default=''):
    opts = ['Offshore Delivery Pod', 'Salesforce Services', 'Government Services', 'NPS Survey CX OS demo',
            'NPS Survey setup or migration', 'Something else']
    o = ''.join(f'<option{" selected" if x == default else ""}>{x}</option>' for x in opts)
    return f'''<form class="lead" action="#" data-w2l method="POST"><input type="text" name="hp_website" value="" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px;width:1px;height:1px;opacity:0">
  <input type="hidden" name="oid" value="00D6g000001VQio">
  <input type="hidden" name="retURL" value="https://saleshub.info/thanks">
  <input type="hidden" name="lead_source" value="Web - saleshub.info">
  <input type="hidden" name="Campaign_ID" value="701QK00000qxtAc"><input type="hidden" name="member_status" value="Responded">
  <input type="hidden" name="00NQK00000MJn21" value="Paused"><input type="hidden" name="description" value="">
  <div><label for="fn">First name</label><input id="fn" name="first_name" autocomplete="given-name" required></div>
  <div><label for="ln">Last name</label><input id="ln" name="last_name" autocomplete="family-name" required></div>
  <div><label for="em">Work email</label><input id="em" name="email" type="email" autocomplete="email" required></div>
  <div><label for="co">Company or agency</label><input id="co" name="company" autocomplete="organization" required></div>
  <div><label for="ph">Phone (optional)</label><input id="ph" name="phone" type="tel" autocomplete="tel"></div>
  <div><label for="int">What can we help with?</label><select id="int" name="int">{o}</select></div>
  <div class="full"><label for="msg">Tell us a little more (optional)</label><textarea id="msg" name="msg"></textarea></div>
  <div class="full"><button class="btn k" type="submit">Send</button> <span class="note">&nbsp;We reply within one business day and use your details only to reply.</span></div>
 </form><script>document.querySelectorAll("form[data-w2l]").forEach(function(f){{var t=Date.now();f.addEventListener("submit",function(e){{var h=f.querySelector("[name=hp_website]");if((h&&h.value)||Date.now()-t<4000){{e.preventDefault();return}}h&&h.parentNode.removeChild(h);f.action="https://webto."+"salesforce.com/servlet/servlet.WebToLead?encoding=UTF-8"}})}});</script>'''


DOCS = {
    'capability': ('/files/Capability Statement.pdf', 'Capability Statement', 'PDF'),
    'gov': ('/files/SalesHub - Gov Services.pdf', 'SalesHub Services for Local Government', 'PDF'),
    'smb': ('/files/Certified Small Minority Owned.pdf', 'Certified Small Business, State of Georgia', 'PDF'),
    'uspaacc': ('/files/SalesHub USPAACC Certificate.pdf', 'USPAACC certificate', 'PDF'),
    'appdev': ('/files/Service Offering - AppDev - SF -2025.pdf', 'Salesforce app development service offering', 'PDF'),
    'services': ('/files/SalesHub Services.pdf', 'SalesHub services overview', 'PDF'),
    'privacy': ('/files/01_Privacy_Policy.pdf', 'Privacy Policy', 'PDF'),
    'dpa': ('/files/02_Data_Processing_Addendum.pdf', 'Data Processing Addendum', 'PDF'),
}


def docs(keys):
    out = []
    for k in keys:
        href, name, kind = DOCS[k]
        out.append(f'<li><a href="{href.replace(" ", "%20")}"><span>{name}</span><small>{kind}</small></a></li>')
    return '<ul class="docs">' + ''.join(out) + '</ul>'


# ---------------------------------------------------------------- pages
ICON = {
 'pod': '<path d="M16 19v-1.5a3.5 3.5 0 0 0-3.5-3.5h-5A3.5 3.5 0 0 0 4 17.5V19"/><circle cx="10" cy="7.5" r="3.5"/><path d="M20 19v-1.5a3.5 3.5 0 0 0-2.5-3.35M15.5 4.2a3.5 3.5 0 0 1 0 6.6"/>',
 'cloud': '<path d="M7 18h10.5a4 4 0 0 0 .6-7.95A6 6 0 0 0 6.5 9.5 4.25 4.25 0 0 0 7 18z"/><path d="M10 13.5l1.8 1.8L15 12"/>',
 'gov': '<path d="M3 10h18M5 10v8M9.5 10v8M14.5 10v8M19 10v8M3 20h18M12 3l9 5H3z"/>',
 'star': '<path d="M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.8l-5.2 2.8 1-5.8-4.3-4.1 5.9-.9z"/>',
 'pin': '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
 'globe': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z"/>',
 'badge': '<circle cx="12" cy="9" r="6"/><path d="M8.5 14l-1.5 7 5-2.5 5 2.5-1.5-7"/><path d="M9.5 9l1.8 1.8L14.5 7.6"/>',
 'calc': '<rect x="5" y="3" width="14" height="18" rx="2.5"/><path d="M8.5 7h7M8.5 11.5h.01M12 11.5h.01M15.5 11.5h.01M8.5 15h.01M12 15h.01M15.5 15v2.5"/>',
 'doc': '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
 'swap': '<path d="M4 8h13l-3.5-3.5M20 16H7l3.5 3.5"/>',
 'play': '<circle cx="12" cy="12" r="9"/><path d="M10 8.5v7l6-3.5z"/>',
 'chat': '<path d="M20 15a2 2 0 0 1-2 2H8l-4 4V5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2z"/><path d="M8.5 9.5h7M8.5 13h4"/>',
 'flag': '<path d="M5 21V4M5 4h11l-2 4 2 4H5"/>',
 'check': '<circle cx="12" cy="12" r="9"/><path d="M8 12.3l2.7 2.7L16 9.6"/>',
}
def ico(k, cls='ico'):
    return f'<span class="{cls}" aria-hidden="true"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ICON[k]}</svg></span>'

PX = 'https://images.pexels.com/photos/{0}/pexels-photo-{0}.jpeg?auto=compress&cs=tinysrgb&w={1}'
def photo(pid, alt, w=900, cls='ph'):
    return f'<img class="{cls}" src="{PX.format(pid, w)}" srcset="{PX.format(pid, w)} 1x, {PX.format(pid, w*2)} 2x" alt="{alt}" loading="lazy" decoding="async">'
FILM = 'https://www.npssurveys.com/files/'
NPSR = 'https://www.npssurveys.com/'
UTM = '?utm_source=saleshub.info&utm_medium=website&utm_campaign=company_site&utm_content='


def home():
    body = f'''<section class="hero blue"><div class="wrap grid">
 <div>
  <h1>We build NPS Survey, and the teams that make Salesforce work.</h1>
  <p class="lead">SalesHub makes NPS Survey CX OS, the customer feedback app on Salesforce AppExchange. We also run dedicated QA and Salesforce teams for commercial and government clients.</p>
  <div class="cta"><a class="btn w" href="{NPS}hero">Explore NPS Survey</a><a class="btn o" href="#film">{ico('play','bi')}Watch the 75-second film</a></div>
  <p class="proof">{ico('star','bi')}5.0 on Salesforce AppExchange · 15-day free trial</p>
 </div>
 <div><div class="panel" role="img" aria-label="Product illustration of the NPS Survey CX Command Center with sample data">
  <div class="ph">{MARK}<b>CX Command Center</b><span class="scope">All accounts · this quarter</span></div>
  <div class="kpis"><div class="kpi"><small>NPS</small><b>+42</b><em>up 9 this quarter</em></div><div class="kpi"><small>Detractors followed up</small><b>96%</b><em>within 5 days</em></div><div class="kpi"><small>Responses</small><b>4,812</b><em>this quarter</em></div></div>
  <div class="trend"><svg viewBox="0 0 300 70" width="100%" height="64" preserveAspectRatio="none" aria-hidden="true"><defs><linearGradient id="ga" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#002FA7" stop-opacity=".22"/><stop offset="1" stop-color="#002FA7" stop-opacity="0"/></linearGradient></defs><path d="M0 52 L43 46 L86 49 L129 38 L172 41 L215 30 L258 26 L300 18 L300 70 L0 70Z" fill="url(#ga)"/><path d="M0 52 L43 46 L86 49 L129 38 L172 41 L215 30 L258 26 L300 18" fill="none" stroke="#002FA7" stroke-width="3" stroke-linejoin="round"/><circle cx="300" cy="18" r="4.5" fill="#002FA7"/></svg><small>Satisfaction, last 8 weeks</small></div>
  <div class="feed"><div class="row"><span class="d" style="background:#EB5757"></span><span class="n">Acme Corp · Case 08812 closed</span><span class="a" style="color:#D64545">Follow-up opened</span><span class="s">3</span></div><div class="row"><span class="d" style="background:#E9A52B"></span><span class="n">Northwind · Renewal won</span><span class="a" style="color:#B9801A">30-day check-in</span><span class="s">7</span></div><div class="row"><span class="d" style="background:#23A96A"></span><span class="n">Lakeside Clinics · Onboarding done</span><span class="a" style="color:#1E9A5B">Review request sent</span><span class="s">10</span></div></div>
 </div><div class="sample">Product illustration · sample data</div></div>
</div></section>

<section class="statband" aria-label="At a glance"><div class="wrap"><div><b>5.0</b> on AppExchange · 7 reviews</div><div><b>2018</b> Salesforce partner since</div><div><b>2</b> delivery centers, Marietta and Dhaka</div><div><b>GA</b> certified small business</div></div></section>
<section class="badges"><div class="wrap"><span class="bdg"><img src="/assets/ill/salesforce.svg" alt="Salesforce" width="56" height="40"><span>Salesforce partner · <b>NPS Survey on AppExchange</b></span></span><span class="bdg"><img src="/assets/ill/carahsoft.svg" alt="Carahsoft" width="120" height="30"><span>Public-sector buying<br><b>through Carahsoft</b></span></span><span class="bdg">{ico('gov','ti')}<span>Cooperative contract<br><b>CoreTrust 24COR-018GR</b></span></span></div></section>

<section class="s" id="services"><div class="wrap">
 <div class="kick">Services</div>
 <h2>Three ways we help, for commercial and government teams.</h2>
 <p class="intro">The same people who build NPS Survey on Salesforce deliver our services, with a U.S. delivery lead and our client innovation center in Dhaka.</p>
 <div class="cards">
  <div class="card lead">{ico('pod')}<span class="tag">Fixed monthly fee</span><h3>Offshore Delivery Pod</h3><p>A dedicated QA and development team that works your hours and your tools. Manual, automation and performance testing, with a named account manager and weekly reporting.</p><a class="more" href="/offshore-delivery-pod">How the pod works</a></div>
  <div class="card">{ico('cloud')}<h3>Salesforce Services</h3><p>Implementation, integrations, custom apps and managed admin support for Sales Cloud, Service Cloud and the rest of the platform, plus NPS Survey setup and migration.</p><a class="more" href="/salesforce-services">Salesforce services</a></div>
  <div class="card">{ico('gov')}<h3>Government Services</h3><p>Salesforce, QA, data and IT program support for federal, state and local agencies. A Georgia-certified small business with a published capability statement.</p><a class="more" href="/government-services">Government services</a></div>
 </div>
</div></section>

<section class="s tint" id="film"><div class="wrap split mid">
 <div>
  <div class="kick">See it in 75 seconds</div>
  <h2>A customer gives you a 3 out of 10. What happens next?</h2>
  <p class="intro">In most companies that answer sits in a spreadsheet. In NPS Survey CX OS it opens a follow-up for the right person, inside Salesforce, so the customer hears back. Sound on, or read the captions.</p>
  <a class="btn k" href="{NPS}film">See how it works</a>
 </div>
 <div class="film">
  <video controls preload="none" playsinline poster="{FILM}NPS-CXOS-Film-poster.jpg" width="1920" height="1080">
   <source src="{FILM}NPS-CXOS-Film-1080p.mp4" type="video/mp4">
   <track kind="captions" src="{FILM}NPS-CXOS-Film.vtt" srclang="en" label="English" default>
  </video>
 </div>
</div></section>

<section class="s tint" id="resources"><div class="wrap">
 <div class="kick">Free resources</div>
 <h2>Take something useful, no call needed.</h2>
 <div class="cards res">
  <a class="card r" href="{NPSR}roi/{UTM}res_roi">{ico('calc')}<h3>CX ROI calculator</h3><p>Estimate the revenue you keep by following up with unhappy customers.</p><span class="more">Open the calculator</span></a>
  <a class="card r" href="{NPSR}business-case/{UTM}res_case">{ico('doc')}<h3>Business case builder</h3><p>A ready-to-share case for your CFO or IT leadership, filled in with your numbers.</p><span class="more">Build your case</span></a>
  <a class="card r" href="{NPSR}switch/{UTM}res_switch">{ico('swap')}<h3>Switching from GetFeedback</h3><p>The steps, timeline and what moves over when you switch survey tools inside Salesforce.</p><span class="more">Read the guide</span></a>
  <a class="card r" href="{FILM}SalesHub-NPS-CXOS-Public-Sector-Kit.pdf">{ico('gov')}<h3>Public-sector kit (PDF)</h3><p>Resident feedback for agencies: use cases, security and how to buy through Carahsoft or CoreTrust.</p><span class="more">Download the kit</span></a>
  <a class="card r" href="{FILM}SalesHub-Capability-Statement.pdf">{ico('badge')}<h3>Capability statement (PDF)</h3><p>NAICS codes, certifications and past performance for contracting officers.</p><span class="more">Download the statement</span></a>
  <a class="card r" href="{TRIAL}">{ico('check')}<h3>15-day free trial</h3><p>Install NPS Survey CX OS from AppExchange into a sandbox and try it on your own data.</p><span class="more">Start the trial</span></a>
 </div>
</div></section>

<section class="s"><div class="wrap">
 <div>
  <div class="kick">Why SalesHub</div>
  <h2>A Salesforce product company that also delivers.</h2>
  <p class="intro">Building our own AppExchange product keeps our engineering standards high. Clients get a team that ships production Salesforce software, not just advice.</p>
  <div class="facts">
   <div class="fact">{ico('cloud')}<b>Since 2018</b><span>Salesforce consulting partner and AppExchange ISV</span></div>
   <div class="fact">{ico('pin')}<b>Marietta, Georgia</b><span>Headquarters and U.S. delivery</span></div>
   <div class="fact">{ico('globe')}<b>Dhaka, Bangladesh</b><span>Client innovation center</span></div>
   <div class="fact">{ico('badge')}<b>Certified small business</b><span>State of Georgia, minority owned</span></div>
  </div>
 </div>
</div></section>

<section class="s tint" id="talk"><div class="wrap split">
 <div>
  <div class="kick">Talk to us</div>
  <h2>Tell us what you are working on.</h2>
  <p class="intro">A 30-minute call is enough to tell you whether we are the right fit. We reply within one business day.</p>
  {checks(['A demo of NPS Survey CX OS on your type of customer', 'A sized quote for an Offshore Delivery Pod', 'Salesforce help, from a fix to a full project'])}
  <p class="small">{ico('chat','bi')}Prefer email? <a href="mailto:{EMAIL}">{EMAIL}</a> · <a href="tel:{PHONE_TEL}">{PHONE}</a></p>
 </div>
 <div class="card">{form()}</div>
</div></section>
'''
    page('index', 'SalesHub | Makers of NPS Survey CX OS, Salesforce and QA services', 'SalesHub builds NPS Survey CX OS for Salesforce and runs dedicated QA and Salesforce teams for commercial and government clients.', body)


def pod():
    body = hero('Offshore Delivery Pod', 'A dedicated QA and development team for a fixed monthly fee. Led from the U.S., delivered from our client innovation center in Dhaka, and working inside your tools and your scrum.',
                cta='<div class="cta"><a class="btn w" href="/contact-us?topic=pod">Book a discovery call</a></div>') + f'''
<section class="s"><div class="wrap">
 <div class="kick">What you get</div>
 <h2>A team that feels like part of yours.</h2>
 <div class="cards">
  <div class="card"><h3>Dedicated engineers</h3><p>QA, Salesforce and full-stack engineers assigned only to you, trained on your product and ramped up with a documented onboarding checklist.</p></div>
  <div class="card"><h3>A named account manager</h3><p>A Dhaka-based key account manager runs the team day to day: daily check-ins, time and leave tracking, and the first call for any concern.</p></div>
  <div class="card"><h3>U.S. delivery executive</h3><p>A U.S.-based executive meets your stakeholders monthly and prepares quarterly business reviews for IT leadership.</p></div>
 </div>
</div></section>

<section class="s tint"><div class="wrap split">
 <div><div class="kick">Commercial model</div><h2>One fixed monthly rate.</h2>
  <p class="intro">You pay one predictable fee for the pod, not hourly invoices. The pod is sized to your release plan, and we add backup engineers when someone is out so delivery does not stop.</p></div>
 <div>{checks(['Engineers sized to your workload, from a small team to a full pod', 'Offshore key account manager and U.S. delivery executive included', 'Daily standups in your scrum, with Slack, Teams and Jira access', 'Secure access through your VDI or Windows 365', 'Transparent hours and outcomes: a tracked defect list backed by tickets', 'Weekly status report (PowerPoint and PDF) and quarterly business reviews'])}</div>
</div></section>

<section class="s"><div class="wrap">
 <div class="kick">How we deliver quality</div>
 <h2>Testing that finds problems early.</h2>
 <div class="cards">
  <div class="card"><h3>Test automation</h3><p>AI-assisted automation suites shorten test cycles, widen coverage and catch regressions before release.</p></div>
  <div class="card"><h3>Shift-left QA</h3><p>QA joins at requirements, so issues are found before they reach development, let alone production.</p></div>
  <div class="card"><h3>Root cause analysis</h3><p>We don't just log defects. We trace each one to its source so the same problem does not come back.</p></div>
  <div class="card"><h3>Regression runs</h3><p>Regular regression runs make sure new changes don't break what already works.</p></div>
  <div class="card"><h3>Peer review</h3><p>Code and test scripts are peer reviewed and checked against agreed standards.</p></div>
  <div class="card"><h3>Client feedback</h3><p>We ask your engineers, managers and leaders how we are doing every quarter, and act on what we hear.</p></div>
 </div>
</div></section>

<section class="s tint"><div class="wrap">
 <div class="kick">Getting started</div>
 <h2>From first call to a working pod.</h2>
 <ol class="steps">
  <li><div><b>Discovery call</b><span>We learn your product, release cadence, tools and what good looks like.</span></div></li>
  <li><div><b>Pod proposal</b><span>A team plan, fixed monthly rate and service levels, in writing.</span></div></li>
  <li><div><b>Onboarding</b><span>Accounts, tool access, environment setup and knowledge transfer, run from a checklist with your IT team.</span></div></li>
  <li><div><b>Delivery and reporting</b><span>Daily standups, weekly reports and quarterly reviews from day one.</span></div></li>
 </ol>
 <p class="intro">Read how the pod works in practice: <a class="kick" href="/blog/f/revolutionizing-qa-how-saleshubs-offshore-team-in-bangladesh">our Dhaka QA team's work for an F&amp;I client</a> and <a class="kick" href="/blog/f/abdul-gaffars-success-story-a-masterclass-in-sqa-leadership">how our key account manager leads delivery</a>.</p>
</div></section>
{band('See if a pod fits your team.', 'Tell us about your product and release plan. We will come back with a team plan and a fixed monthly rate.', 'Book a discovery call', '/contact-us?topic=pod')}'''
    page('offshore-delivery-pod', 'Offshore Delivery Pod | Dedicated QA and development teams | SalesHub', 'A dedicated QA and development team for a fixed monthly fee, led from the U.S. and delivered from our client innovation center in Dhaka.', body, 'pod')


def sf():
    body = hero('Salesforce Services', 'Implementation, integrations, custom apps and ongoing support from the team that builds NPS Survey CX OS on Salesforce.',
                cta='<div class="cta"><a class="btn w" href="/contact-us?topic=sf">Book a free consultation</a></div>') + f'''
<section class="s"><div class="wrap">
 <div class="kick">Consulting</div>
 <h2>Get Salesforce right the first time, then keep it improving.</h2>
 <div class="cards two">
  <div class="card"><h3>Implementation</h3><p>Sales Cloud, Service Cloud and Experience Cloud set up around how your team actually sells and serves. We start by understanding your process, then design, build, test and launch.</p></div>
  <div class="card"><h3>Integrations</h3><p>Connect Salesforce to your ERP, data warehouse and home-grown systems so your teams work from one accurate record.</p></div>
  <div class="card"><h3>Custom apps</h3><p>Lightning components, Apex and flows for the processes standard Salesforce does not cover.</p></div>
  <div class="card"><h3>Training and support</h3><p>Hands-on training for admins and users, and a support team for the questions that come up every week.</p></div>
 </div>
</div></section>

<section class="s tint"><div class="wrap">
 <div class="kick">Managed services</div>
 <h2>Salesforce skills on demand, for a monthly fee.</h2>
 <div class="cards">
  <div class="card"><h3>Standard</h3><p>For small orgs on Sales, Service or Marketing Cloud.</p><ul><li>User administration</li><li>Data import, export and backups</li><li>Reports and dashboards</li><li>Org optimization and adoption</li><li>One admin, 20 hours a week</li></ul></div>
  <div class="card lead"><span class="tag">Most chosen</span><h3>Professional</h3><p>For growing orgs with several clouds.</p><ul><li>Everything in Standard</li><li>Strategic planning and integration analysis</li><li>Data cleansing</li><li>Dedicated account manager</li><li>One developer, 40 hours a week</li></ul></div>
  <div class="card"><h3>Enterprise</h3><p>For large orgs that need a full team.</p><ul><li>Everything in Professional</li><li>Ongoing enhancements and integrations</li><li>Quarterly business reviews</li><li>Licensing and ROI review, change management</li><li>App development team; QA and DevOps on demand</li></ul></div>
 </div>
</div></section>

<section class="s"><div class="wrap split">
 <div><div class="kick">NPS Survey CX OS</div><h2>Setup and migration for our own product.</h2>
  <p class="intro">Go live with surveys, triggers, field mapping and close-the-loop follow-up. Moving from another survey tool? We bring your surveys and history across.</p>
  <p style="margin-top:20px"><a class="btn ko" href="{NPS}sf_services">About NPS Survey</a></p></div>
 <div>{checks(['Free first consultation, no obligation', 'Design your org around your business process', 'Plan integrations with your home-grown apps', 'A reliable front office across sales, service, marketing and operations'])}{docs(['appdev','services'])}</div>
</div></section>
{band('Start with a free consultation.', 'Bring your Salesforce questions. Leave with a clear plan.', 'Book a free consultation', '/contact-us?topic=sf')}'''
    page('salesforce-services', 'Salesforce Services | Implementation, integration and managed services | SalesHub', 'Salesforce implementation, integrations, custom apps and managed services from the team that builds NPS Survey CX OS.', body, 'sf')


def gov():
    body = hero('Government Services', 'Salesforce, QA, data and IT program support for federal, state and local agencies, from a Georgia-certified, minority-owned small business.',
                cta='<div class="cta"><a class="btn w" href="/files/Capability%20Statement.pdf">Capability statement</a><a class="btn o" href="/contact-us?topic=gov">Contact our government team</a></div>') + f'''
<section class="s"><div class="wrap">
 <div class="kick">What we deliver</div>
 <h2>Modern systems for public-sector missions.</h2>
 <div class="cards">
  <div class="card"><h3>Salesforce for agencies</h3><p>Constituent and case management, licensing and permitting, grants and public health programs on Salesforce, designed, built and supported by our team.</p></div>
  <div class="card"><h3>QA and test engineering</h3><p>Dedicated test teams, automation and independent verification for mission systems, delivered through our Offshore Delivery Pod or onshore staff.</p></div>
  <div class="card"><h3>Data, AI and analytics</h3><p>Data integration, master data management, dashboards and AI-assisted analysis that turn agency data into decisions.</p></div>
  <div class="card"><h3>IT program support</h3><p>Project and program management, DevSecOps, help desk (Tier I to III) and network operations support.</p></div>
  <div class="card"><h3>Research and SBIR</h3><p>Prototype and MVP development for SBIR, STTR and xTech programs, with university research partners.</p></div>
  <div class="card"><h3>NPS Survey for government</h3><p>Measure resident and employee satisfaction inside your Salesforce org, with data that never leaves it.</p><a class="more" href="https://www.npssurveys.com/public-sector/?utm_source=saleshub.info&utm_medium=website&utm_campaign=company_site&utm_content=gov">NPS Survey for the public sector</a></div>
 </div>
</div></section>

<section class="s tint"><div class="wrap split">
 <div><div class="kick">Credentials</div><h2>Small business, trusted partners.</h2>
 {checks(['Available to agencies through <a class="kick" href="https://www.carahsoft.com/saleshub">Carahsoft</a>, our public-sector distributor', 'Certified Small Business, Georgia Department of Administrative Services', 'Minority-owned business, certified by USPAACC', 'Recognized by USPAACC among the Top 10 Asian American businesses in the Southeast', 'Lifetime member, Association of the United States Army (AUSA), Atlanta chapter', 'Salesforce AppExchange ISV partner', 'Research collaboration with Georgia Tech'])}</div>
 <div><div class="kick">Downloads</div><h2>For your contracting team.</h2>{docs(['capability','gov','smb','uspaacc'])}</div>
</div></section>
{band('Working on a solicitation or a program?', 'Talk to our government team about teaming, subcontracting or a direct engagement.', 'Contact our government team', '/contact-us?topic=gov')}'''
    page('government-services', 'Government Services | Salesforce, QA and IT for agencies | SalesHub', 'Salesforce, QA, data and IT program support for federal, state and local agencies from a Georgia-certified, minority-owned small business.', body, 'gov')


def about():
    body = hero('About SalesHub', 'A Salesforce product and services company, founded in 2018 in Atlanta.') + f'''
<section class="s"><div class="wrap split">
 <div><div class="kick">Our story</div><h2>From consulting partner to product company.</h2>
 <p class="intro">SalesHub began as a Salesforce consulting partner, helping companies improve how they sell, serve and operate. What we learned project after project became NPS Survey CX OS, our app on Salesforce AppExchange, which is now our focus.</p>
 <p class="intro">Our services teams carry the same standard: QA and development pods, Salesforce delivery and government programs, led from Georgia and delivered with our client innovation center in Dhaka.</p></div>
 <div><div class="kick">How we work</div>
 {checks(['Transparent with clients and with each other', 'One owner for every commitment', 'Long-term teams: our engineers often stay with a client for years', 'We invest in our people, through training and fair recognition'])}</div>
</div></section>
<section class="s tint"><div class="wrap">
 <div class="facts">
  <div class="fact"><b>2018</b><span>Founded in Atlanta, Georgia</span></div>
  <div class="fact"><b>Marietta, GA</b><span>Headquarters</span></div>
  <div class="fact"><b>Dhaka, Bangladesh</b><span>Client innovation center</span></div>
  <div class="fact"><b>AppExchange ISV</b><span>Makers of NPS Survey CX OS</span></div>
 </div>
</div></section>
<section class="s"><div class="wrap">
 <div class="kick">Our products</div><h2>What we build.</h2>
 <div class="cards two">
  <div class="card lead"><span class="tag">Flagship</span><h3>NPS Survey CX OS</h3><p>Customer feedback and close-the-loop follow-up, built natively on Salesforce.</p><a class="more" href="{NPS}about">npssurveys.com</a></div>
  <div class="card"><h3>TracAnything</h3><p>Project management and enterprise planning on Salesforce.</p><a class="more" href="https://tracanything.com">tracanything.com</a></div>
 </div>
</div></section>
{band('Want to work with us?', 'Clients, partners and future teammates are all welcome.', 'Contact us')}'''
    page('about', 'About SalesHub | Makers of NPS Survey CX OS', 'SalesHub is a Salesforce product and services company founded in 2018 in Atlanta, makers of NPS Survey CX OS.', body, 'about')


def contact():
    body = f'''<section class="s"><div class="wrap contact">
 <div class="info">
  <div class="kick">Contact</div>
  <h2>Let's talk.</h2>
  <p>Tell us what you're working on: a QA pod, a Salesforce project, a government program or NPS Survey. We reply within one business day.</p>
  <p><a href="mailto:{EMAIL}">{EMAIL}</a><br><a href="tel:{PHONE_TEL}">{PHONE}</a></p>
  <p>{ADDR}</p>
  <p>Monday to Friday, 9am to 5pm Eastern</p>
 </div>
 {form()}
</div></section>
<script>(function(){{var t=new URLSearchParams(location.search).get('topic');var m={{pod:'Offshore Delivery Pod',sf:'Salesforce Services',gov:'Government Services',nps:'NPS Survey CX OS demo'}};if(t&&m[t])document.getElementById('int').value=m[t];}})();</script>'''
    page('contact-us', 'Contact SalesHub | Book a call', 'Contact SalesHub about an Offshore Delivery Pod, Salesforce services, government programs or NPS Survey CX OS.', body, 'contact')


def careers():
    body = hero('Careers', 'We hire QA engineers, Salesforce developers and business development people in Dhaka and the U.S.') + f'''
<section class="s"><div class="wrap narrow">
 <p class="intro">We don't have open roles listed right now, but we're always glad to hear from good people. Email your resume and a short note about the work you want to do to <a class="kick" href="mailto:admin@saleshub.info?subject=Careers">admin@saleshub.info</a>.</p>
</div></section>'''
    page('careers', 'Careers at SalesHub', 'Join SalesHub: QA engineers, Salesforce developers and business development roles in Dhaka and the U.S.', body)


def legal(path, title, key, desc):
    href = DOCS[key][0].replace(' ', '%20')
    body = hero(title, desc) + f'''<section class="s"><div class="wrap narrow"><p class="intro">The current version is available as a PDF.</p>{docs([key])}
<p class="intro">Questions about privacy or data processing? Email <a class="kick" href="mailto:{EMAIL}">{EMAIL}</a>.</p></div></section>'''
    page(path, title + ' | SalesHub', desc, body)


def security():
    src = open(os.path.join(BACKUP, 'text', 'security---trust.md'), encoding='utf-8').read()
    lines = [l for l in src.split('\n')[4:] if l and not l.startswith('![img]') and not l.startswith('[button]')]
    stop = next((i for i, l in enumerate(lines) if l.startswith('- Home') or l.startswith('SalesHub, LLC')), len(lines))
    lines = [l for l in lines[:stop] if 'Network Design and Implementation' not in l]
    out, inlist = [], False
    for l in lines[1:]:
        if l.startswith('- '):
            if not inlist: out.append('<ul>'); inlist = True
            out.append('<li>' + html.escape(l[2:]) + '</li>'); continue
        if inlist: out.append('</ul>'); inlist = False
        m = re.match(r'^(#+) (.*)', l)
        if m:
            lvl = min(4, len(m.group(1)) + (0 if len(m.group(1)) > 1 else 1))
            out.append(f'<h{lvl}>{html.escape(m.group(2))}</h{lvl}>')
        else:
            out.append('<p>' + html.escape(l) + '</p>')
    if inlist: out.append('</ul>')
    intro = lines[0] if lines else ''
    body = hero('Security &amp; Trust', html.escape(intro)) + '<section class="s"><div class="wrap narrow prose">' + '\n'.join(out) + '</div></section>'
    page('security-&-trust', 'Security & Trust | NPS Survey CX OS by SalesHub', 'How SalesHub and NPS Survey CX OS protect customer data: built natively on Salesforce, sub-processors, encryption and incident response.', body, canonical='/security-%26-trust')


# ---------------------------------------------------------------- blog
def safe_slug(s):
    return re.sub(r'[^a-zA-Z0-9/_-]+', '-', s)


def inline(text, ents):
    """Draft.js text with link entities -> html."""
    spans = sorted([e for e in ents if e.get('e') and e['e'].get('type') == 'LINK'], key=lambda e: e['o'])
    out, pos = [], 0
    for e in spans:
        o, l = e['o'], e['l']
        if o < pos: continue
        out.append(html.escape(text[pos:o]))
        url = e['e'].get('data', {}).get('url') or e['e'].get('data', {}).get('href') or '#'
        url = re.sub(r'^https?://(www\.)?saleshub\.info', '', url) or '/'
        out.append(f'<a href="{html.escape(url)}">{html.escape(text[o:o + l])}</a>')
        pos = o + l
    out.append(html.escape(text[pos:]))
    return ''.join(out)


def post_html(blocks, imgmap):
    out, lst = [], None
    for b in blocks:
        t = b['type']
        if t in ('unordered-list-item', 'ordered-list-item'):
            tag = 'ul' if t[0] == 'u' else 'ol'
            if lst != tag:
                if lst: out.append(f'</{lst}>')
                out.append(f'<{tag}>'); lst = tag
            out.append('<li>' + inline(b['text'], b['ents']) + '</li>'); continue
        if lst: out.append(f'</{lst}>'); lst = None
        if t == 'atomic':
            for e in b['ents']:
                ent = e.get('e') or {}
                d = ent.get('data', {})
                if ent.get('type') == 'IMAGE' and d.get('src'):
                    src = ('https:' + d['src'] if d['src'].startswith('//') else d['src']).split('/:/')[0]
                    local = imgmap.get(src) or imgmap.get(html.unescape(src))
                    if not local and ('/isteam/stock/' in src or '/isteam/getty/' in src):
                        continue  # licensed stock from the old site builder: not carried over
                    out.append(f'<figure><img loading="lazy" src="{html.escape(local or src + "/:/rs=w:1200")}" alt="{html.escape(d.get("alt", ""))}"></figure>')
                elif ent.get('type') == 'DIVIDER':
                    out.append('<hr>')
                elif ent.get('type') == 'VIDEO':
                    u = d.get('src') or d.get('url') or ''
                    if u: out.append(f'<p><a href="{html.escape(u)}">Watch the video</a></p>')
            continue
        if not b['text'].strip(): continue
        tag = {'header-one': 'h2', 'header-two': 'h2', 'header-three': 'h3', 'header-four': 'h4'}.get(t, 'p')
        out.append(f'<{tag}>' + inline(b['text'], b['ents']) + f'</{tag}>')
    if lst: out.append(f'</{lst}>')
    return '\n'.join(out)


def topic(slug, title):
    s = (slug + ' ' + title).lower()
    if 'tracanything' in s or 'fp&a' in s or 'scenario-planning' in s or 'project-management' in s: return 'TracAnything'
    if 'nps' in s or 'voc' in s or 'csat' in s or 'customer-experience' in s or 'closed-loop' in s: return 'Customer experience'
    if 'qa' in s or 'gaffar' in s or 'intern' in s: return 'QA and delivery'
    if 'government' in s or 'procurement' in s: return 'Government'
    return 'Salesforce'


def blog():
    sm = os.path.join(BACKUP, 'raw-html', 'blog', 'f')
    # original slugs from the sitemap backup, keyed by the sanitized name used in the backup
    orig = {}
    allmd = open(os.path.join(BACKUP, 'ALL-PAGES-TEXT.md'), encoding='utf-8').read()
    for u in re.findall(r'^URL: https://saleshub\.info/blog/f/(\S+)$', allmd, re.M):
        from urllib.parse import unquote
        orig[safe_slug(unquote(u))] = unquote(u)
    imgdir = os.path.join(ROOT, 'blog', 'img')
    imgmap = {}
    if os.path.isdir(imgdir):
        for p in glob.glob(os.path.join(imgdir, '**', '*'), recursive=True):
            if os.path.isfile(p):
                rel = os.path.relpath(p, imgdir).replace(os.sep, '/')
                from urllib.parse import quote
                imgmap['https://img1.wsimg.com/isteam/' + quote(rel, safe='/')] = '/blog/img/' + quote(rel, safe='/')
                imgmap['https://img1.wsimg.com/isteam/' + rel] = '/blog/img/' + quote(rel, safe='/')
                imgmap['https://img1.wsimg.com/isteam/' + quote(rel, safe="/'()&")] = '/blog/img/' + quote(rel, safe='/')
                if rel.endswith('.tif.png') or rel.endswith('.tif.tiff') or '.tif.' in rel:
                    base = rel.split('.tif.')[0] + '.tif'
                    imgmap['https://img1.wsimg.com/isteam/' + quote(base, safe='/')] = '/blog/img/' + quote(rel, safe='/')
    posts = []
    for f in sorted(glob.glob(os.path.join(BACKUP, 'posts', '*.json'))):
        p = json.load(open(f, encoding='utf-8'))
        slug = orig.get(p['slug'], p['slug'])
        title = html.unescape(p['title']).strip() or slug.replace('-', ' ').title()
        raw = open(os.path.join(sm, p['slug'] + '.html'), encoding='utf-8').read()
        dm = re.search(r'<meta name="description" content="([^"]*)"', raw)
        desc = html.unescape(dm.group(1)) if dm else ''
        date = (p.get('date') or '')[:10]
        tp = topic(slug, title)
        bodyhtml = post_html(p['blocks'], imgmap)
        when = datetime.date.fromisoformat(date).strftime('%B %-d, %Y') if date else ''
        old = (date and date < '2025-01-01')
        note = '<div class="note-old">This post is from our archive. Some product names, offers and details may have changed since it was published.</div>' if old else ''
        schema = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": title, "datePublished": date,
                  "author": {"@type": "Organization", "name": "SalesHub"}, "publisher": {"@type": "Organization", "name": "SalesHub, LLC"},
                  "mainEntityOfPage": SITE + '/blog/f/' + slug}
        body = f'''<section class="hero page blue"><div class="wrap narrow"><div class="crumb"><a href="/blog">Blog</a> · {tp}</div><h1>{html.escape(title)}</h1><p class="lead">{when}</p></div></section>
<section class="s"><div class="wrap narrow prose">{note}{bodyhtml}</div></section>'''
        page('blog/f/' + slug, title + ' | SalesHub Blog', desc or title, body, schema=schema,
             canonical='/blog/f/' + __import__('urllib.parse').parse.quote(slug))
        posts.append((date, slug, title, desc, tp))
    posts.sort(reverse=True)
    topics = ['All'] + sorted({p[4] for p in posts})
    items = ''.join(f'<li data-t="{html.escape(t)}"><a href="/blog/f/{html.escape(s)}">{html.escape(ti)}</a><p>{(datetime.date.fromisoformat(d).strftime("%b %Y") + " · ") if d else ""}{html.escape(t)}{(" · " + html.escape(de[:150])) if de else ""}</p></li>' for d, s, ti, de, t in posts)
    btns = ''.join(f'<button type="button" aria-pressed="{"true" if t == "All" else "false"}" data-t="{html.escape(t)}">{html.escape(t)}</button>' for t in topics)
    body = hero('Blog', 'News, case studies and how-tos from the SalesHub team. For customer experience playbooks, see <a href="https://www.npssurveys.com/insights/" style="color:#fff">NPS Survey Insights</a>.') + f'''
<section class="s"><div class="wrap narrow"><div class="filters" role="group" aria-label="Filter by topic">{btns}</div><ul class="postlist">{items}</ul></div></section>
<script>document.querySelectorAll('.filters button').forEach(function(b){{b.addEventListener('click',function(){{var t=b.dataset.t;document.querySelectorAll('.filters button').forEach(function(x){{x.setAttribute('aria-pressed',x===b)}});document.querySelectorAll('.postlist li').forEach(function(li){{li.hidden=!(t==='All'||li.dataset.t===t)}})}})}})</script>'''
    page('blog', 'Blog | SalesHub', 'News, case studies and how-tos from SalesHub: QA delivery, Salesforce, government and customer experience.', body)
    return len(posts)


# ---------------------------------------------------------------- old URLs
REDIRECTS = {
    'saleshub-gov-services': '/government-services', 'it-program-services': '/government-services',
    'nps-survey': NPS + 'old_nps_page', 'nps-survey-for-government': NPS + 'old_gov_page', 'nps-survey-for-defense': NPS + 'old_defense_page',
    'tracanything': 'https://tracanything.com', 'sales-plan': '/salesforce-services',
    'outsourcing-capabilities': '/offshore-delivery-pod', 'staffing': '/offshore-delivery-pod', 'microservices-bpo': '/offshore-delivery-pod',
    'buy-services': '/offshore-delivery-pod',
    'it-managed-services': '/salesforce-services', 'data-integration-services': '/salesforce-services', 'digital-marketing': '/salesforce-services',
    'salesforce-sales-cloud': '/salesforce-services', 'salesforce-solutions': '/salesforce-services', 'salesforce-coc': '/blog/f/salesforce-center-of-competencies-coc-for-saleshub',
    'salesforce-book': '/salesforce-services', 'pmo,-framework': '/salesforce-services', 'roadmap': '/salesforce-services',
    'business-card-automation': '/salesforce-services', 'force-academy': '/about', 'istudentcentral': '/about',
    'georgia-tech-partnership': '/about', 'tech-marietta-innovation': '/about', 'salesforce-for-veterans': '/about', 'newcomers-program-1': '/about',
    'faq': '/contact-us', 'online-appointments': '/contact-us', 'm/login': '/', 'm/reset': '/', 'm/create': '/', 'm/create-account': '/',
}


def build():
    # clean generated output, keep repo files
    for d in ('blog/f',):
        shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)
    # homepage is hand-built (QA pod focus): tools/home.html
    shutil.copyfile(os.path.join(ROOT, 'tools', 'home.html'), os.path.join(ROOT, 'index.html')); SITEMAP.append(SITE + '/')
    pod(); sf(); gov(); about(); contact(); careers(); security()
    legal('privacy-policy', 'Privacy Policy', 'privacy', 'How SalesHub collects, uses and protects personal information.')
    legal('data-processing-addendum', 'Data Processing Addendum', 'dpa', 'The terms under which SalesHub processes personal data on behalf of customers.')
    n = blog()
    for old, new in REDIRECTS.items():
        forward(old + '.html', new)
    forward('online-appointments/index.html', '/contact-us')
    forward('saleshub-gov-services/index.html', '/government-services')
    # 404 page sends people somewhere useful
    write('404.html', open(os.path.join(ROOT, 'contact-us.html'), encoding='utf-8').read()
          .replace('<title>Contact SalesHub | Book a call</title>', '<title>Page not found | SalesHub</title>')
          .replace("<h2>Let's talk.</h2>", "<h2>We couldn't find that page.</h2>")
          .replace('<p>Tell us what you', '<p><a href="/">Go to the homepage</a>, or tell us what you'))
    today = datetime.date.today().isoformat()
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
          ''.join(f'<url><loc>{html.escape(u)}</loc><lastmod>{today}</lastmod></url>\n' for u in SITEMAP) + '</urlset>\n')
    write('robots.txt', f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
    write('.nojekyll', '')
    print(f'built {len(SITEMAP)} indexed pages, {n} blog posts, {len(REDIRECTS) + 2} forwards')


if __name__ == '__main__':
    build()
