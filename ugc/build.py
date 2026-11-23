"""Write the CMS content (content/*.json) into index.html.

Run: python3 build.py
Each region between <!-- cms:NAME --> and <!-- /cms:NAME --> in index.html is
regenerated. Everything outside those markers is left as it is.
Russian and Italian texts go into a JSON block that main.js reads.
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
PAGE = ROOT / "index.html"

CATEGORIES = {"beauty": "Beauty", "pets": "Pets", "home": "Home &amp; Flowers"}
FORMATS = {
    "organic": "Organic style",
    "organicText": "Organic style with text",
    "testimonial": "Ad style testimonial",
    "voiceover": "Ad style voiceover",
}
# Alt text of a video card: "<play>: <description>, <concept|client> <brand>"
CARD_ALT = {
    "en": ("Play: {d}, concept for {b}", "Play: {d}, client project for {b}"),
    "ru": ("Смотреть: {d}, концепт для {b}", "Смотреть: {d}, проект для {b}"),
    "it": ("Guarda: {d}, concept per {b}", "Guarda: {d}, progetto per {b}"),
}
LANGS = ("ru", "it")
IMG = 'loading="lazy" decoding="async"'

translations = {lang: {} for lang in LANGS}


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def esc(text):
    return html.escape(text or "", quote=True)


def alt_attr(key, item, compose=None):
    """English alt in the HTML, Russian and Italian into the translations block.
    An empty RU or IT field is skipped, so the page falls back to English."""
    compose = compose or (lambda lang, text: text)
    for lang in LANGS:
        text = (item.get("alt_" + lang) or "").strip()
        if text:
            translations[lang][key] = compose(lang, text)
    return f'alt="{esc(compose("en", item["alt_en"]))}" data-i18n-attr="alt:{key}"'


def hero(media):
    imgs = []
    for i, item in enumerate(media["hero"], 1):
        imgs.append(f'<img src="{esc(item["image"])}" width="800" height="1000" fetchpriority="high" '
                    f'{alt_attr(f"cms.hero{i}", item)}>')
    return imgs


def about(media):
    intro, photo = media["intro"], media["about_photo"]
    return [
        f'<a class="phone phone--tall js-video" href="{esc(intro["video"])}" data-caption-key="about.introCaption">',
        f'  <img src="{esc(intro["poster"])}" width="1080" height="1920" {IMG} {alt_attr("cms.intro", intro)}>',
        '  <span class="play" aria-hidden="true"></span>',
        '</a>',
        '<figure class="phone">',
        f'  <img src="{esc(photo["image"])}" width="1080" height="1920" {IMG} {alt_attr("cms.aboutPhoto", photo)}>',
        '</figure>',
    ]


def why(media):
    photo = media["why_photo"]
    return [f'<img src="{esc(photo["image"])}" width="1200" height="1500" {IMG} {alt_attr("cms.whyPhoto", photo)}>']


def videos(items):
    out = []
    for cat, title in CATEGORIES.items():
        cards = [v for v in items if v["category"] == cat]
        if not cards:
            continue
        out += [f'<section class="group" aria-labelledby="g-{cat}">',
                f'  <h3 class="label-lg" id="g-{cat}" data-i18n="cat.{cat}">{title}</h3>',
                '  <ul class="grid">']
        for n, v in enumerate(cards, 1):
            brand = v["brand"].strip()
            client = bool(v.get("client"))

            def compose(lang, text, brand=brand, client=client):
                return CARD_ALT[lang][client].format(d=text, b=brand)

            label = ('<span data-i18n="card.clientFor">Client project for</span>' if client
                     else '<span data-i18n="card.conceptFor">Concept for</span>')
            out += ['    <li class="card">',
                    f'      <a class="card__media js-video" href="{esc(v["video"])}">',
                    f'        <img src="{esc(v["poster"])}" width="1080" height="1560" {IMG} '
                    f'{alt_attr(f"cms.v.{cat}{n}", v, compose)}>',
                    '        <span class="play" aria-hidden="true"></span>',
                    '      </a>',
                    f'      <p class="card__format" data-i18n="fmt.{v["format"]}">{FORMATS[v["format"]]}</p>',
                    f'      <p class="card__brand">{label} {esc(brand)}</p>',
                    '    </li>']
        out += ['  </ul>', '</section>']
    return out


def photos(items):
    return [f'<li><img src="{esc(p["image"])}" width="1200" height="1500" {IMG} {alt_attr(f"cms.ph{i}", p)}></li>'
            for i, p in enumerate(items, 1)]


def i18n_block():
    data = json.dumps(translations, ensure_ascii=False, indent=1).replace("</", "<\\/")
    return [f'<script type="application/json" id="cms-i18n">{data}</script>']


def replace_region(page, name, lines):
    pattern = re.compile(rf"([ \t]*)<!-- cms:{name} -->\n.*?\n[ \t]*<!-- /cms:{name} -->", re.S)
    match = pattern.search(page)
    if not match:
        raise SystemExit(f"index.html has no <!-- cms:{name} --> region")
    indent = match.group(1)
    body = "\n".join(indent + line for line in lines)
    new = f"{indent}<!-- cms:{name} -->\n{body}\n{indent}<!-- /cms:{name} -->"
    return page[:match.start()] + new + page[match.end():]


def main():
    media = load("content/media.json")
    regions = {
        "hero": hero(media),
        "about": about(media),
        "why": why(media),
        "videos": videos(load("content/videos.json")),
        "photos": photos(load("content/photos.json")),
    }
    regions["i18n"] = i18n_block()  # last: the other regions fill `translations`
    page = PAGE.read_text(encoding="utf-8")
    for name, lines in regions.items():
        page = replace_region(page, name, lines)
    PAGE.write_text(page, encoding="utf-8")
    print("index.html built")


if __name__ == "__main__":
    main()
