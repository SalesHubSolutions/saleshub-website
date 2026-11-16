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
<link rel="stylesheet" href="/assets/site.css">
<script type="application/ld+json">{ld}</script>
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
 <div class="fbot"><span>© {YEAR} SalesHub, LLC. All rights reserved.</span><span><a href="https://www.linkedin.com/company/12673581">LinkedIn</a> · <a href="https://www.youtube.com/@saleshubllc">YouTube</a> · <a href="https://tracanything.com">TracAnything</a></span></div>
</div></footer>
<script>
(function(){{var b=document.querySelector('.menu'),u=document.getElementById('navlist');b.addEventListener('click',function(){{var o=u.classList.toggle('open');b.setAttribute('aria-expanded',o)}});
var f=document.querySelector('form.lead');if(f)f.addEventListener('submit',function(){{var s=f.querySelector('#int'),m=f.querySelector('#msg'),d=document.createElement('input');d.type='hidden';d.name='description';d.value=s.value+(m.value?': '+m.value:'')+' ('+location.pathname+')';s.removeAttribute('name');m.removeAttribute('name');f.appendChild(d);}});}})();
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
    return f'''<form class="lead" action="https://webto.salesforce.com/servlet/servlet.WebToLead?encoding=UTF-8" method="POST">
  <input type="hidden" name="oid" value="00D6g000001VQio">
  <input type="hidden" name="retURL" value="https://www.npssurveys.com/thanks.html">
  <input type="hidden" name="lead_source" value="Web">
  <div><label for="fn">First name</label><input id="fn" name="first_name" autocomplete="given-name" required></div>
  <div><label for="ln">Last name</label><input id="ln" name="last_name" autocomplete="family-name" required></div>
  <div><label for="em">Work email</label><input id="em" name="email" type="email" autocomplete="email" required></div>
  <div><label for="co">Company or agency</label><input id="co" name="company" autocomplete="organization" required></div>
  <div><label for="ph">Phone (optional)</label><input id="ph" name="phone" type="tel" autocomplete="tel"></div>
  <div><label for="int">What can we help with?</label><select id="int" name="int">{o}</select></div>
  <div class="full"><label for="msg">Tell us a little more (optional)</label><textarea id="msg" name="msg"></textarea></div>
  <div class="full"><button class="btn k" type="submit">Send</button> <span class="note">&nbsp;We reply within one business day and use your details only to reply.</span></div>
 </form>'''


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
def home():
    body = f'''<section class="hero blue"><div class="wrap grid">
 <div>
  <h1>We build NPS Survey, and the teams that make Salesforce work.</h1>
  <p class="lead">SalesHub makes NPS Survey CX OS, the customer feedback app on Salesforce AppExchange. We also run dedicated QA and Salesforce teams for commercial and government clients.</p>
  <div class="cta"><a class="btn w" href="{NPS}hero">Explore NPS Survey</a><a class="btn o" href="#services">See our services</a></div>
 </div>
 <div class="prod">
  <div class="top">{MARK}<div><b>NPS Survey</b><span>CX OS by SalesHub</span></div></div>
  <ul>
   <li>{TICK}NPS, CSAT and CES surveys that run inside Salesforce</li>
   <li>{TICK}Every unhappy customer gets an owner and a follow-up</li>
   <li>{TICK}Surveys in each customer's language, events and check-in</li>
   <li>{TICK}Your data never leaves Salesforce</li>
  </ul>
  <div class="meta"><span>Rated 5.0 on AppExchange · 7-day free trial</span><a href="{TRIAL}">Start free trial</a></div>
 </div>
</div></section>

<section class="s" id="services"><div class="wrap">
 <div class="kick">Services</div>
 <h2>Three ways we help, for commercial and government teams.</h2>
 <p class="intro">The same people who build NPS Survey on Salesforce deliver our services, with a U.S. delivery lead and our client innovation center in Dhaka.</p>
 <div class="cards">
  <div class="card lead"><span class="tag">Fixed monthly fee</span><h3>Offshore Delivery Pod</h3><p>A dedicated QA and development team that works your hours and your tools. Manual, automation and performance testing, with a named account manager and weekly reporting.</p><a class="more" href="/offshore-delivery-pod">How the pod works</a></div>
  <div class="card"><h3>Salesforce Services</h3><p>Implementation, integrations, custom apps and managed admin support for Sales Cloud, Service Cloud and the rest of the platform, plus NPS Survey setup and migration.</p><a class="more" href="/salesforce-services">Salesforce services</a></div>
  <div class="card"><h3>Government Services</h3><p>Salesforce, QA, data and IT program support for federal, state and local agencies. A Georgia-certified small business with a published capability statement.</p><a class="more" href="/government-services">Government services</a></div>
 </div>
</div></section>

<section class="s tint"><div class="wrap">
 <div class="kick">Why SalesHub</div>
 <h2>A Salesforce product company that also delivers.</h2>
 <p class="intro">Building our own AppExchange product keeps our engineering standards high. Clients get a team that ships production Salesforce software, not just advice.</p>
 <div class="facts">
  <div class="fact"><b>Since 2018</b><span>Salesforce consulting partner and AppExchange ISV</span></div>
  <div class="fact"><b>Marietta, Georgia</b><span>Headquarters and U.S. delivery</span></div>
  <div class="fact"><b>Dhaka, Bangladesh</b><span>Client innovation center</span></div>
  <div class="fact"><b>Certified small business</b><span>State of Georgia, minority owned</span></div>
 </div>
</div></section>
{band('Tell us what you are working on.', 'A 30-minute call is enough to tell you whether we are the right fit.')}'''
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
 {checks(['Available to agencies through Carahsoft, our public-sector distributor', 'Certified Small Business, Georgia Department of Administrative Services', 'Minority-owned business, certified by USPAACC', 'Recognized by USPAACC among the Top 10 Asian American businesses in the Southeast', 'Lifetime member, Association of the United States Army (AUSA), Atlanta chapter', 'Salesforce AppExchange ISV partner', 'Research collaboration with Georgia Tech'])}</div>
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
    home(); pod(); sf(); gov(); about(); contact(); careers(); security()
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
