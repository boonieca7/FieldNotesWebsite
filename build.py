"""Build the Field Notes From Abroad static site.

    python build.py           # reads content/ and tldr.json, writes the pages into site/

The output is plain HTML/CSS/JS with relative links, so site/index.html opens straight from
disk, and GitHub Pages serves the site/ folder as is. Images in site/media/ are made once by
build_media.py from the original photos and committed; build.py only links to them. Posts keep their original permalinks
(YYYY/MM/DD/slug/), so old links keep working once the site is hosted at the same domain.
The build stops with an error if any published post is not placed in a journey or has no
summary, rather than silently leaving it out.
"""
import html
import json
import os
import re
import shutil
import sys
from datetime import datetime
from urllib.parse import urlparse

from bs4 import BeautifulSoup, NavigableString

import site_config as C
from marks import svg, NAVY, PAPER, RED

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, "content")
DIST = os.path.join(ROOT, "site")
MANIFEST = json.load(open(os.path.join(DIST, "media", "manifest.json"), encoding="utf-8"))
TLDR = json.load(open(os.path.join(ROOT, "tldr.json"), encoding="utf-8"))
FONTS = ("https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700"
         "&family=IBM+Plex+Mono:wght@400;500&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;"
         "0,8..60,600;1,8..60,400;1,8..60,600&display=swap")

esc = html.escape
CUR = ' aria-current="page"'
CURCLS = ' class="current"'


# ---------------------------------------------------------------- content model

def norm(s):
    return re.sub(r"[^a-z0-9ăâîșțşţ ]", "", html.unescape(s).lower().replace("…", " ")).split()


def load_posts():
    posts, about = {}, None
    for name in sorted(os.listdir(CONTENT)):
        if not name.endswith(".json"):
            continue
        d = json.load(open(os.path.join(CONTENT, name), encoding="utf-8"))
        if d["type"] == "page":
            about = d
            continue
        pid = d["ID"]
        raw_title = html.unescape(d["title"]).strip()
        title = C.DISPLAY_TITLES.get(pid) or re.sub(r"^Field Notes:\s*", "", raw_title).rstrip(":").strip()
        u = urlparse(d["URL"])
        path = u.path.strip("/") + "/index.html"
        dt = datetime.fromisoformat(d["date"])
        cats = list(d.get("categories") or [])
        tags = list(d.get("tags") or [])
        posts[pid] = dict(id=pid, raw_title=raw_title, title=title, path=path, old_url=d["URL"],
                          date=dt, content=d["content"], featured=(d.get("featured_image") or "").split("?")[0],
                          cats=cats, tags=tags, words=len(d.get("text", "").split()), text=d.get("text", ""))
    return posts, about


POSTS, ABOUT = load_posts()

problems = []
JOURNEY_OF, SERIES_OF, THREADS_OF = {}, {}, {}
for j in C.JOURNEYS:
    for pid in j["posts"]:
        if pid in JOURNEY_OF:
            problems.append(f"post {pid} is in two journeys")
        JOURNEY_OF[pid] = j
for s in C.SERIES:
    for pid in s["posts"]:
        SERIES_OF.setdefault(pid, []).append(s)
for t in C.THREADS:
    for pid in t["posts"]:
        THREADS_OF.setdefault(pid, []).append(t)
for pid, p in POSTS.items():
    if pid not in JOURNEY_OF:
        problems.append(f"post {pid} '{p['title']}' is not in any journey")
    if str(pid) not in TLDR:
        problems.append(f"post {pid} '{p['title']}' has no summary in tldr.json")
    p["tldr"] = TLDR.get(str(pid), {}).get("tldr", "")
for pid in list(JOURNEY_OF) + [x for s in C.SERIES for x in s["posts"]] + [x for t in C.THREADS for x in t["posts"]]:
    if pid not in POSTS:
        problems.append(f"config names post {pid}, which is not in the backup")
if problems:
    sys.exit("Build stopped:\n  " + "\n  ".join(problems))


def kind(p):
    labels = [s["label"] for s in SERIES_OF.get(p["id"], []) if s["slug"] != "leadership"]
    if labels:
        return labels[0]
    if p["raw_title"].startswith("Reflection") or (p["cats"] == ["Reflections"]):
        return "Reflection"
    return "Field Note"


def fmt_date(dt):
    return dt.strftime("%d.%m.%Y")


def minutes(p):
    return max(1, round(p["words"] / 230))


def media(url, size="full"):
    m = MANIFEST.get(url.split("?")[0])
    return m[size] if m else None


# ---------------------------------------------------------------- links

def rel(frm, to):
    r = os.path.relpath(to, os.path.dirname(frm) or ".").replace(os.sep, "/")
    return r


INTERNAL = {urlparse(p["old_url"]).path.strip("/"): p["path"] for p in POSTS.values()}
INTERNAL["about"] = "about/index.html"
INTERNAL["category/florence"] = "journeys/firenze/index.html"
BACKLINKS = {}


def internal_target(href):
    u = urlparse(href)
    if u.netloc.replace("www.", "") in ("fieldnotesfromabroad.com", "camclelland-jhibt.wordpress.com"):
        return INTERNAL.get(u.path.strip("/"))
    return None


# ---------------------------------------------------------------- post body

KEEP_CLASSES = re.compile(r"^(wp-block-(image|media-text|media-text__media|media-text__content|gallery|separator|heading|quote|list|group)"
                          r"|has-media-on-the-right|aligncenter|alignwide|has-text-align-(center|left|right))$")


def clean_body(p):
    soup = BeautifulSoup(p["content"], "lxml")
    body = soup.body
    if body is None:
        return "", [], None
    # Jetpack tiled galleries -> simple gallery of figures
    for tg in body.select("div.wp-block-jetpack-tiled-gallery"):
        fig = soup.new_tag("figure", attrs={"class": "wp-block-gallery"})
        for item in tg.select("figure.tiled-gallery__item"):
            item.attrs = {}
            fig.append(item.extract())
        tg.replace_with(fig)
    for sp in body.select(".wp-block-spacer"):
        sp.decompose()
    images = []
    for img in body.find_all("img"):
        src = img.get("src", "").split("?")[0]
        m = MANIFEST.get(src)
        alt = img.get("alt", "")
        if not m:
            ph = soup.new_tag("span", attrs={"class": "img-missing", "role": "img",
                                             "aria-label": "Image not available in the backup"})
            ph.string = "Image not available in the backup"
            img.replace_with(ph)
            continue
        images.append(src)
        img.attrs = {"src": rel(p["path"], m["full"]), "alt": alt, "width": str(m["w"]), "height": str(m["h"]),
                     "loading": "lazy", "decoding": "async"}
    for a in body.find_all("a"):
        href = a.get("href", "")
        tgt = internal_target(href)
        if tgt:
            a.attrs = {"href": rel(p["path"], tgt)}
            BACKLINKS.setdefault(tgt, set()).add(p["id"])
        else:
            a.attrs = {"href": href, "rel": "noopener"}
    for t in body.find_all(True):
        if t.name in ("img", "a"):
            continue
        cls = [c for c in t.get("class", []) if KEEP_CLASSES.match(c)]
        t.attrs = {"class": cls} if cls else {}
    for d in body.find_all("div"):
        if not d.attrs and not d.get_text(strip=True) and not d.find(["img", "span"]):
            d.decompose()
    # Opening line: drop it if it repeats the title, mark it as a subtitle if it is a short line.
    first = next((c for c in body.children if getattr(c, "name", None)), None)
    lede = None
    if first is not None and first.name in ("p", "h2", "h3", "h4") and not first.find("img"):
        words = first.get_text(" ", strip=True)
        if words and len(words.split()) <= 14:
            tw, fw = norm(p["title"]), norm(words)
            if fw and " ".join(fw) in " ".join(tw):
                first.decompose()
            else:
                lede = words
                first.decompose()
    out = "".join(str(c) for c in body.children).strip()
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out, images, lede


# ---------------------------------------------------------------- layout

def mark(size, fg=PAPER, bg=NAVY, label=None):
    return svg(C.MARK, size, fg, bg, label)


NAV = [("Journeys", "journeys/index.html"), ("Stories", "series/stories/index.html"),
       ("Chronicles", "series/chronicles/index.html"), ("Leadership", "series/leadership/index.html"),
       ("Archive", "archive/index.html"), ("About", "about/index.html")]


def page(path, title, main, description="", section=None, scripts="", head_extra=""):
    r = lambda to: rel(path, to)
    nav = "".join(
        f'<li><a href="{r(to)}"{CUR if section == label else ""}>{label}</a></li>' for label, to in NAV)
    full_title = f"{title} · {C.SITE_TITLE}" if title != C.SITE_TITLE else C.SITE_TITLE
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(description)}">{head_extra}
<link rel="icon" href="{r('assets/favicon.svg')}" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{r('assets/site.css')}">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="{r('index.html')}">
      {mark(46)}
      <span class="brand-words"><span class="brand-name">Field Notes</span><span class="brand-sub">From Abroad</span></span>
    </a>
    <nav aria-label="Main">
      <ul class="nav">{nav}
        <li><a class="nav-search" href="{r('search/index.html')}"{CUR if section == "Search" else ""}>
          <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5 L21 21"/></svg>
          <span>Search</span></a></li>
      </ul>
    </nav>
  </div>
</header>
<main id="main">
{main}
</main>
<footer class="site-footer">
  <div class="wrap footer-inner">
    <div class="footer-about">
      {mark(64, label="Field Notes From Abroad mark")}
      <div>
        <p class="footer-name">{C.AUTHOR}</p>
        <p>Doctoral student, Gonzaga University Doctoral Program in Leadership Studies. Erasmus+ scholar at West University of Timișoara, spring 2026.</p>
      </div>
    </div>
    <div class="footer-links">
      <a class="btn btn-outline-light" href="{C.PORTFOLIO_URL}">Leadership portfolio</a>
      <p class="mono">Field notes written Feb–Jun 2026. Words and photographs © {C.AUTHOR}.</p>
    </div>
  </div>
</footer>
{scripts}
</body>
</html>
'''


def card(p, frm, show_place=True):
    thumb = media(p["featured"], "thumb") if p["featured"] else None
    j = JOURNEY_OF[p["id"]]
    img = (f'<img src="{rel(frm, thumb)}" alt="" loading="lazy" decoding="async">' if thumb
           else f'<span class="card-noimg">{mark(72)}</span>')
    meta = f'{fmt_date(p["date"])}' + (f' · {esc(j["place"])}' if show_place else "")
    return f'''<article class="card">
  <a href="{rel(frm, p["path"])}">
    <span class="card-img">{img}</span>
    <span class="card-body">
      <span class="meta">{meta}<span class="kind">{esc(kind(p))}</span></span>
      <span class="card-title">{esc(p["title"])}</span>
      <span class="card-text">{esc(p["tldr"])}</span>
    </span>
  </a>
</article>'''


def post_list(ids, frm, show_place=True):
    items = sorted((POSTS[i] for i in ids), key=lambda p: (p["date"], p["id"]))
    return '<div class="cards">' + "".join(card(p, frm, show_place) for p in items) + "</div>"


def write(path, text):
    full = os.path.join(DIST, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(text)


# ---------------------------------------------------------------- pages

def journey_cover(j):
    return media(POSTS[j["cover"]]["featured"], "thumb")


def build_posts():
    order = [pid for j in C.JOURNEYS for pid in sorted(j["posts"], key=lambda i: (POSTS[i]["date"], i))]
    bodies = {pid: clean_body(POSTS[pid]) for pid in order}
    for idx, pid in enumerate(order):
        p = POSTS[pid]
        path = p["path"]
        r = lambda to: rel(path, to)
        body, images, lede = bodies[pid]
        j = JOURNEY_OF[pid]
        jposts = sorted(j["posts"], key=lambda i: (POSTS[i]["date"], i))
        pos = jposts.index(pid) + 1
        feat = ""
        if p["featured"] and p["featured"] not in images and media(p["featured"]):
            m = MANIFEST[p["featured"]]
            feat = (f'<figure class="feature"><img src="{r(m["full"])}" alt="" width="{m["w"]}" height="{m["h"]}"></figure>')
        prev_p = POSTS[order[idx - 1]] if idx > 0 else None
        next_p = POSTS[order[idx + 1]] if idx + 1 < len(order) else None
        trip = "".join(
            f'<li{CURCLS if i == pid else ""}><span class="num">{n:02d}</span>'
            f'<a href="{r(POSTS[i]["path"])}"{CUR if i == pid else ""}>{esc(POSTS[i]["title"])}</a></li>'
            for n, i in enumerate(jposts, 1))
        chips = "".join(f'<li><a class="chip" href="{r("series/" + s["slug"] + "/index.html")}">{esc(s["label"])}</a></li>'
                        for s in SERIES_OF.get(pid, []))
        chips += "".join(f'<li><a class="chip chip-thread" href="{r("threads/" + t["slug"] + "/index.html")}">{esc(t["name"])}</a></li>'
                         for t in THREADS_OF.get(pid, []))
        back = BACKLINKS.get(path, set()) - {pid}
        backhtml = ""
        if back:
            backhtml = ('<section class="backlinks"><h2>Mentioned in</h2><ul>' + "".join(
                f'<li><a href="{r(POSTS[b]["path"])}">{esc(POSTS[b]["title"])}</a></li>' for b in sorted(back)) + "</ul></section>")
        pn = '<nav class="prevnext" aria-label="More field notes"><div class="wrap prevnext-inner">'
        pn += (f'<a class="prev" href="{r(prev_p["path"])}"><span class="mono">← Previous</span><span class="pn-title">{esc(prev_p["title"])}</span></a>'
               if prev_p else '<span></span>')
        pn += (f'<a class="next" href="{r(next_p["path"])}"><span class="mono">Next →</span><span class="pn-title">{esc(next_p["title"])}</span></a>'
               if next_p else '<span></span>')
        pn += "</div></nav>"
        main = f'''<article class="post">
  <header class="wrap post-head">
    <p class="crumbs mono"><a href="{r('journeys/' + j['slug'] + '/index.html')}">Journey {j['num']} · {esc(j['place'])}</a>
      <span aria-hidden="true">/</span> <span>Note {pos} of {len(jposts)}</span> <span class="badge">{esc(kind(p))}</span></p>
    <h1>{esc(p['title'])}</h1>
    {f'<p class="lede-sub">{esc(lede)}</p>' if lede else ''}
    <p class="meta-line mono"><time datetime="{p['date'].date().isoformat()}">{fmt_date(p['date'])}</time><span>{p['words']:,} words · {minutes(p)} min</span></p>
    <hr class="thread">
  </header>
  <div class="wrap post-grid">
    <div class="prose">
      {feat}
      {body}
      {backhtml}
      <p class="source mono">Originally published at <a href="{esc(p['old_url'])}">{esc(p['old_url'].replace('http://', ''))}</a></p>
    </div>
    <aside class="post-aside">
      <section class="aside-box">
        <h2>On this journey</h2>
        <ol class="trip">{trip}</ol>
      </section>
      {f'<section><h2>Part of</h2><ul class="chips">{chips}</ul></section>' if chips else ''}
    </aside>
  </div>
</article>
{pn}'''
        write(path, page(path, p["title"], main, p["tldr"], section=None))
    return order


def build_home(order):
    path = "index.html"
    r = lambda to: rel(path, to)
    hero = MANIFEST[C.HERO_IMAGE]
    start = [3, 33, 59, 122]
    journeys = ""
    for j in C.JOURNEYS:
        cov = journey_cover(j)
        months = j["when"]
        journeys += f'''<article class="card journey-card">
  <a href="{r('journeys/' + j['slug'] + '/index.html')}">
    <span class="card-img">{f'<img src="{r(cov)}" alt="" loading="lazy">' if cov else ''}</span>
    <span class="card-body">
      <span class="meta">{j['num']} · {months}<span class="kind">{len(j['posts'])} notes</span></span>
      <span class="card-title caps">{esc(j['place'])}</span>
      <span class="card-text">{esc(j['intro'])}</span>
    </span>
  </a>
</article>'''
    series = ""
    for s in C.SERIES:
        series += f'''<div class="series-block">
  <span class="badge badge-{s['slug']}">{esc(s['label'])}</span>
  <h3><a href="{r('series/' + s['slug'] + '/index.html')}">{esc(s['name'])}</a></h3>
  <p>{esc(s['intro'])}</p>
  <p class="mono">{len(s['posts'])} posts</p>
</div>'''
    latest = sorted(POSTS.values(), key=lambda p: (p["date"], p["id"]), reverse=True)[:6]
    about_first = BeautifulSoup(ABOUT["content"], "lxml").find("p")
    main = f'''<section class="wrap hero">
  <div class="hero-text">
    <p class="mono kicker">Spring 2026 · Erasmus+ · West University of Timișoara</p>
    <h1>A home for my field notes.</h1>
    <p class="hero-lede">Stories and observations from Romania and beyond. Honest reflections on transition, identity, and learning, and on what leadership looks like in the real world.</p>
    <p class="hero-actions"><a class="btn" href="{r(POSTS[3]['path'])}">Start at the beginning</a>
      <a class="btn btn-outline" href="#route">Browse the route</a></p>
  </div>
  <figure class="hero-photo pinned">
    <img src="{r(hero['full'])}" alt="A tower of Corvin Castle with a steep tiled roof against a blue sky" width="{hero['w']}" height="{hero['h']}">
    <figcaption class="mono"><span>{C.HERO_CAPTION[0]}</span><span>{C.HERO_CAPTION[1]}</span></figcaption>
  </figure>
</section>
<div class="wrap"><hr class="thread"></div>
<section class="wrap section" aria-labelledby="start">
  <div class="section-head"><h2 id="start" class="caps">Start here</h2><p class="mono">The first four notes, written in the week I left</p></div>
  {post_list(start, path, show_place=False)}
</section>
<section class="wrap section" id="route" aria-labelledby="route-h">
  <div class="section-head"><h2 id="route-h" class="caps">The route</h2><p class="mono">{len(C.JOURNEYS)} journeys · {len(POSTS)} field notes · Feb to Jun 2026</p></div>
  <div class="cards">{journeys}</div>
</section>
<section class="band" aria-labelledby="series-h">
  <div class="wrap section">
    <div class="section-head"><h2 id="series-h" class="caps">Ongoing series</h2></div>
    <div class="series-grid">{series}</div>
  </div>
</section>
<section class="wrap section" aria-labelledby="latest-h">
  <div class="section-head"><h2 id="latest-h" class="caps">Latest field notes</h2><p class="mono"><a href="{r('archive/index.html')}">All {len(POSTS)} in the archive →</a></p></div>
  <ol class="latest">''' + "".join(
        f'''<li><a href="{r(p['path'])}"><span class="mono latest-meta"><span>{fmt_date(p['date'])}</span><span class="accent">{esc(JOURNEY_OF[p['id']]['place'])}</span></span>
      <span class="latest-body"><span class="latest-title">{esc(p['title'])}</span><span class="card-text">{esc(p['tldr'])}</span></span></a></li>'''
        for p in latest) + f'''</ol>
</section>
<section class="wrap section about-strip" aria-labelledby="about-h">
  <h2 id="about-h" class="caps">About these notes</h2>
  <p>{about_first.get_text(" ", strip=True) if about_first else ''}</p>
  <p><a href="{r('about/index.html')}">Read the full introduction →</a></p>
</section>'''
    write(path, page(path, C.SITE_TITLE, main, "Field notes from a semester in Romania and beyond."))


def build_journeys():
    idx_path = "journeys/index.html"
    blocks = ""
    for n, j in enumerate(C.JOURNEYS):
        path = f"journeys/{j['slug']}/index.html"
        cov = media(POSTS[j["cover"]]["featured"])
        nxt = C.JOURNEYS[n + 1] if n + 1 < len(C.JOURNEYS) else None
        main = f'''<header class="wrap list-head journey-head">
  <div>
    <p class="mono kicker"><a href="{rel(path, idx_path)}">Journeys</a> / {j['num']} · {j['when']}</p>
    <h1 class="caps">{esc(j['name'])}</h1>
    <p class="hero-lede">{esc(j['intro'])}</p>
    <p class="mono">{len(j['posts'])} field notes</p>
  </div>
  {f'<figure class="pinned"><img src="{rel(path, cov)}" alt="" loading="lazy"></figure>' if cov else ''}
</header>
<div class="wrap"><hr class="thread"></div>
<section class="wrap section">{post_list(j['posts'], path, show_place=False)}</section>
{f'<nav class="wrap section next-journey" aria-label="Next journey"><a class="btn" href="{rel(path, "journeys/" + nxt["slug"] + "/index.html")}">Next journey: {esc(nxt["place"])} →</a></nav>' if nxt else ''}'''
        write(path, page(path, j["name"], main, j["intro"], section="Journeys"))
        cov_t = journey_cover(j)
        blocks += f'''<article class="card journey-card">
  <a href="{rel(idx_path, path)}">
    <span class="card-img">{f'<img src="{rel(idx_path, cov_t)}" alt="" loading="lazy">' if cov_t else ''}</span>
    <span class="card-body"><span class="meta">{j['num']} · {j['when']}<span class="kind">{len(j['posts'])} notes</span></span>
    <span class="card-title caps">{esc(j['place'])}</span><span class="card-text">{esc(j['intro'])}</span></span>
  </a>
</article>'''
    main = f'''<header class="wrap list-head"><h1 class="caps">Journeys</h1>
<p class="hero-lede">The semester in the order it happened, from leaving home in February to Bran Castle in June.</p></header>
<div class="wrap"><hr class="thread"></div>
<section class="wrap section"><div class="cards">{blocks}</div></section>'''
    write(idx_path, page(idx_path, "Journeys", main, "The semester, journey by journey.", section="Journeys"))


def build_collections():
    labels = {"stories": "Stories", "chronicles": "Chronicles", "leadership": "Leadership"}
    for s in C.SERIES:
        path = f"series/{s['slug']}/index.html"
        main = f'''<header class="wrap list-head"><p><span class="badge badge-{s['slug']}">{esc(s['label'])}</span></p>
<h1>{esc(s['name'])}</h1><p class="hero-lede">{esc(s['intro'])}</p><p class="mono">{len(s['posts'])} posts</p></header>
<div class="wrap"><hr class="thread"></div>
<section class="wrap section">{post_list(s['posts'], path)}</section>'''
        write(path, page(path, s["label"], main, s["intro"], section=labels[s["slug"]]))
    for t in C.THREADS:
        path = f"threads/{t['slug']}/index.html"
        main = f'''<header class="wrap list-head"><p class="mono kicker">Thread</p><h1>{esc(t['name'])}</h1>
<p class="mono">{len(t['posts'])} posts across the semester</p></header>
<div class="wrap"><hr class="thread"></div>
<section class="wrap section">{post_list(t['posts'], path)}</section>'''
        write(path, page(path, t["name"], main, f"Posts about {t['name'].lower()}."))


def build_archive():
    path = "archive/index.html"
    by_month = {}
    for p in sorted(POSTS.values(), key=lambda p: (p["date"], p["id"])):
        by_month.setdefault(p["date"].strftime("%B %Y"), []).append(p)
    out = ""
    for month, ps in by_month.items():
        out += f'<section class="archive-month"><h2 class="caps">{month}</h2><ol class="latest">' + "".join(
            f'''<li><a href="{rel(path, p['path'])}"><span class="mono latest-meta"><span>{fmt_date(p['date'])}</span><span class="accent">{esc(JOURNEY_OF[p['id']]['place'])}</span></span>
<span class="latest-body"><span class="latest-title">{esc(p['title'])}</span><span class="card-text">{esc(p['tldr'])}</span></span></a></li>''' for p in ps) + "</ol></section>"
    main = f'''<header class="wrap list-head"><h1 class="caps">Archive</h1><p class="mono">All {len(POSTS)} field notes, in the order they were published</p></header>
<div class="wrap"><hr class="thread"></div><div class="wrap section">{out}</div>'''
    write(path, page(path, "Archive", main, "Every field note in publishing order.", section="Archive"))


def build_about():
    path = "about/index.html"
    soup = BeautifulSoup(ABOUT["content"], "lxml")
    for img in soup.find_all("img"):
        m = MANIFEST.get(img.get("src", "").split("?")[0])
        if m:
            img.attrs = {"src": rel(path, m["full"]), "alt": img.get("alt", ""), "loading": "lazy"}
        else:
            img.decompose()
    for t in soup.body.find_all(True):
        if t.name not in ("img", "a"):
            t.attrs = {}
    body = "".join(str(c) for c in soup.body.children)
    main = f'''<article class="post"><header class="wrap post-head"><p class="mono kicker">About</p><h1>{esc(html.unescape(ABOUT['title']))}</h1><hr class="thread"></header>
<div class="wrap post-grid"><div class="prose">{body}
<p><a class="btn" href="{rel(path, POSTS[3]['path'])}">Start at the beginning</a></p></div>
<aside class="post-aside"><section class="aside-box"><h2>Elsewhere</h2><p><a href="{C.PORTFOLIO_URL}">Leadership portfolio</a></p></section></aside></div></article>'''
    write(path, page(path, "About", main, "About Field Notes From Abroad.", section="About"))


def build_search():
    path = "search/index.html"
    index = [dict(t=p["title"], u=p["path"], d=fmt_date(p["date"]), j=JOURNEY_OF[p["id"]]["place"], s=p["tldr"],
                  x=" ".join((p["title"] + " " + p["text"]).split()))
             for p in sorted(POSTS.values(), key=lambda p: (p["date"], p["id"]))]
    write("assets/search-index.js", "window.FN_INDEX = " + json.dumps(index, ensure_ascii=False) + ";\n")
    main = f'''<header class="wrap list-head"><h1 class="caps">Search</h1></header>
<div class="wrap section search">
  <form class="search-form" role="search" action="">
    <label for="q" class="mono">Search all {len(POSTS)} field notes</label>
    <div class="search-row"><input id="q" name="q" type="search" autocomplete="off" placeholder="castle, liver, Florence…">
    <button class="btn" type="submit">Search</button></div>
  </form>
  <p id="status" class="mono" role="status" aria-live="polite"></p>
  <ol id="results" class="latest"></ol>
</div>'''
    scripts = (f'<script src="{rel(path, "assets/search-index.js")}"></script>\n'
               f'<script src="{rel(path, "assets/search.js")}"></script>')
    write(path, page(path, "Search", main, "Search the field notes.", section="Search", scripts=scripts))


def build_404():
    path = "404.html"
    main = f'''<section class="wrap list-head"><p class="mono kicker">404</p><h1>This page wandered off.</h1>
<p class="hero-lede">The link may be from the old site. Try the <a href="{rel(path, 'archive/index.html')}">archive</a> or <a href="{rel(path, 'search/index.html')}">search</a>.</p></section>'''
    # GitHub Pages serves 404.html at whatever address was missing, so relative links need a base.
    # The base is the repository folder on github.io, or the root once a custom domain is set.
    base = ('\n<script>(function(){var p=location.pathname.split("/")[1]||"";'
            'var b=p.toLowerCase()==="fieldnoteswebsite"?"/"+p+"/":"/";'
            'document.write(\'<base href="\'+b+\'">\');})();</script>')
    write(path, page(path, "Not found", main, head_extra=base))


def main():
    # Pages are overwritten in place (nothing is deleted), so renamed pages can leave stale copies behind.
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(DIST, "assets"), dirs_exist_ok=True)
    open(os.path.join(DIST, "assets", "favicon.svg"), "w").write(svg(C.MARK, 64, NAVY, PAPER))
    order = build_posts()
    build_home(order)
    build_journeys()
    build_collections()
    build_archive()
    build_about()
    build_search()
    build_404()
    n = sum(len(f) for _, _, f in os.walk(DIST))
    broken = check_links()
    print(f"Built {len(POSTS)} posts + about into {DIST} ({n} files). Mark: {C.MARK}")
    if broken:
        sys.exit("Broken links:\n  " + "\n  ".join(broken[:50]))
    print("Link check: every local link and image resolves.")


def check_links():
    broken = []
    for folder, _, files in os.walk(DIST):
        for f in files:
            if not f.endswith(".html"):
                continue
            p = os.path.join(folder, f)
            text = re.sub(r"<script>.*?</script>", "", open(p, encoding="utf-8").read(), flags=re.S)
            for u in re.findall(r'(?:src|href)="([^"]+)"', text):
                if u.startswith(("http", "#", "mailto")):
                    continue
                target = os.path.normpath(os.path.join(folder, u.split("#")[0].split("?")[0]))
                if not os.path.exists(target):
                    broken.append(f"{os.path.relpath(p, DIST)} -> {u}")
    return broken


if __name__ == "__main__":
    main()
