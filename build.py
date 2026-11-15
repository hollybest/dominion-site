#!/usr/bin/env python3
"""Сборка сайта Dominion Enterprises SL. Без внешних зависимостей (Python 3).

Использование:
  python3 build.py            # тестовая сборка (noindex, без аналитики), адреса относительно /dominion-site
  python3 build.py --prod     # боевая сборка для домена dominion-enterprises-sl.com (в корне)

Исходники: src/pages/<язык>/*.html (с заголовком front matter), src/partials/, src/assets/.
Результат: папка docs/ (её отдаёт GitHub Pages).
"""
import json, re, shutil, sys, urllib.parse
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
OUT = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else ROOT / "docs"
PROD = "--prod" in sys.argv
SITE = json.loads((SRC / "site.json").read_text(encoding="utf-8"))
BASE = "" if PROD else SITE["test_base"]  # префикс адресов
DOMAIN = SITE["domain"]

ICONS = {
    "wa": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M12 2a10 10 0 0 0-8.7 14.9L2 22l5.3-1.3A10 10 0 1 0 12 2Zm-2.6 5.2c.2 0 .5 0 .6.4l.8 1.9c.1.2 0 .4-.1.6l-.6.8c.7 1.3 1.7 2.3 3.1 3l.8-1c.2-.2.4-.2.6-.1l1.8.9c.3.1.4.3.3.6-.2 1-1 1.7-2 1.8-2.9.2-7-3.7-7.2-6.8 0-1 .5-1.8 1.3-2.1h.6Z"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25c1.1.4 2.3.6 3.6.6a1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.3.2 2.5.6 3.6a1 1 0 0 1-.25 1l-2.25 2.2Z"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7Zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5Z"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>',
    "tool": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>',
    "star": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="m12 2.5 2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.3 6.1 20.5l1.2-6.5L2.5 9.4l6.6-.9z"/></svg>',
}


def wa_url(msg):
    return "https://wa.me/%s?text=%s" % (SITE["phone_wa"], urllib.parse.quote(msg, safe=""))


def render_tokens(s):
    s = re.sub(r"\[\[wa:(.*?)\]\]", lambda m: wa_url(m.group(1)), s)
    s = re.sub(r"\[\[icon:(\w+)\]\]", lambda m: ICONS[m.group(1)], s)
    s = s.replace('"@/', '"%s/' % BASE).replace("'@/", "'%s/" % BASE)
    s = s.replace("{{maps}}", SITE["maps_url"]).replace("{{maps_embed}}", SITE["maps_embed"])
    for k in ("phone_display", "phone_tel", "email", "street", "postal", "city", "name"):
        s = s.replace("{{%s}}" % k, SITE[k])
    return s


def parse_page(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, m.group(2)


def schema_graph(meta, slug_url):
    s = SITE
    biz = {
        "@type": "AutoRepair",
        "@id": DOMAIN + "/#negocio",
        "name": s["name"],
        "url": DOMAIN + "/",
        "telephone": "+" + s["phone_wa"],
        "email": s["email"],
        "address": {"@type": "PostalAddress", "streetAddress": s["street"], "postalCode": s["postal"],
                    "addressLocality": s["city"], "addressRegion": "Alicante", "addressCountry": "ES"},
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "08:30", "closes": "18:30"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "08:30", "closes": "14:00"},
        ],
        "areaServed": {"@type": "City", "name": "Alicante"},
        "hasMap": s["maps_url"],
        "image": DOMAIN + "/assets/img/" + s["og_image"],
    }
    graph = [biz]
    svc = meta.get("service_schema")
    if svc == "neumaticos":
        graph.append({"@type": "Service", "name": "Montaje de neumáticos en Alicante", "provider": {"@id": DOMAIN + "/#negocio"},
                      "areaServed": {"@type": "City", "name": "Alicante"}, "url": slug_url,
                      "offers": {"@type": "Offer", "priceCurrency": "EUR", "priceSpecification": {"@type": "UnitPriceSpecification", "price": "15", "priceCurrency": "EUR", "unitText": "por rueda"}}})
    elif svc == "puente":
        graph.append({"@type": "Service", "name": "Alquiler de puente elevador en Alicante", "provider": {"@id": DOMAIN + "/#negocio"},
                      "areaServed": {"@type": "City", "name": "Alicante"}, "url": slug_url,
                      "offers": {"@type": "Offer", "priceCurrency": "EUR", "priceSpecification": {"@type": "UnitPriceSpecification", "price": "15", "priceCurrency": "EUR", "unitText": "por hora"}}})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(SRC / "assets", OUT / "assets")
    (OUT / ".nojekyll").write_text("")
    if PROD:
        (OUT / "CNAME").write_text(DOMAIN.replace("https://", "").replace("http://", "") + "\n")

    header_t = (SRC / "partials" / "header.html").read_text(encoding="utf-8")
    footer_t = (SRC / "partials" / "footer.html").read_text(encoding="utf-8")
    cookie_t = (SRC / "partials" / "cookie.html").read_text(encoding="utf-8")
    layout_t = (SRC / "partials" / "layout.html").read_text(encoding="utf-8")

    pages = []
    for lang_dir in sorted((SRC / "pages").iterdir()):
        for f in sorted(lang_dir.glob("*.html")):
            meta, body = parse_page(f)
            meta["lang"] = lang_dir.name
            meta["body"] = body
            pages.append(meta)

    nav_items = sorted([p for p in pages if p.get("nav") and p["lang"] == "es"], key=lambda p: int(p["nav_order"]))

    for p in pages:
        slug = p["slug"]
        url_path = slug  # "/" или "/neumaticos/"
        canonical = DOMAIN + url_path
        nav = "".join(
            '<a href="%s%s"%s>%s</a>' % (BASE, n["slug"], ' aria-current="page"' if n["slug"] == slug else "", n["nav"])
            for n in nav_items)
        header = header_t.replace("{{nav}}", nav)
        css_extra = ""
        if p.get("css"):
            css_extra = '<link rel="stylesheet" href="@/assets/css/%s.css">' % p["css"]
        robots = '<meta name="robots" content="noindex, nofollow">' if (not PROD or p.get("noindex")) else '<meta name="robots" content="index, follow, max-image-preview:large">'
        og_img = DOMAIN + "/assets/img/" + SITE["og_image"]
        page_html = layout_t
        repl = {
            "{{lang}}": p["lang"],
            "{{title}}": p["title"],
            "{{description}}": p["description"],
            "{{canonical}}": canonical,
            "{{robots}}": robots,
            "{{og_image}}": og_img,
            "{{css_extra}}": css_extra,
            "{{schema}}": schema_graph(p, canonical),
            "{{service}}": p.get("service", "general"),
            "{{analytics}}": "1" if PROD else "0",
            "{{ga_id}}": SITE["ga_id"],
            "{{header}}": header,
            "{{body}}": p["body"],
            "{{footer}}": footer_t,
            "{{cookie}}": cookie_t,
            "{{base}}": BASE,
        }
        for k, v in repl.items():
            page_html = page_html.replace(k, v)
        page_html = render_tokens(page_html)
        target = OUT / url_path.strip("/") / "index.html" if url_path != "/" else OUT / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page_html, encoding="utf-8")

    # 404
    nf = (SRC / "partials" / "404.html").read_text(encoding="utf-8")
    (OUT / "404.html").write_text(render_tokens(nf.replace("{{base}}", BASE)), encoding="utf-8")

    # заглушки со старых адресов Creatium (GitHub Pages не умеет настоящие 301):
    # мгновенная переадресация + canonical на новый адрес; якоря старой страницы переносим на новые блоки
    import json as _json
    redirects = SITE.get("redirects", {})
    anchors = SITE.get("redirect_anchors", {})
    for old, new in redirects.items():
        dest = BASE + new
        dest_abs = DOMAIN + new
        amap = _json.dumps(anchors.get(old, {}), ensure_ascii=False)
        stub = (
            '<!doctype html><html lang="es"><head><meta charset="utf-8">'
            '<script>(function(){var m=%s,h=location.hash;location.replace("%s"+location.search+(m[h]||""));})();</script>'
            '<title>Esta página se ha movido | Dominion Enterprises</title>'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<link rel="canonical" href="%s"><meta http-equiv="refresh" content="0;url=%s">'
            '</head><body><p>Esta página se ha movido. <a href="%s">Continuar</a>.</p></body></html>'
        ) % (amap, dest, dest_abs, dest, dest)
        t = OUT / old.strip("/") / "index.html"
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text(stub, encoding="utf-8")

    # sitemap и robots
    urls = "".join("<url><loc>%s%s</loc></url>" % (DOMAIN, p["slug"]) for p in pages if p.get("sitemap", "yes") == "yes")
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>\n' % urls, encoding="utf-8")
    if PROD:
        bots = ["Googlebot", "Bingbot", "OAI-SearchBot", "GPTBot", "ClaudeBot", "PerplexityBot", "Google-Extended"]
        robots_txt = "".join("User-agent: %s\nAllow: /\n\n" % b for b in bots)
        robots_txt += "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % DOMAIN
    else:
        robots_txt = "User-agent: *\nDisallow: /\n"
    (OUT / "robots.txt").write_text(robots_txt, encoding="utf-8")
    print("OK: %d страниц, %s сборка, база '%s'" % (len(pages), "боевая" if PROD else "тестовая", BASE))


if __name__ == "__main__":
    main()
