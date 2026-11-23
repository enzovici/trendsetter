# Camila Cingu · UGC & Creative Production site

Static one-page site in the `ugc/` folder of the `enzovici/trendsetter` repository. It is independent of the Python app in the rest of the repository. HTML, CSS and vanilla JavaScript. No framework, no npm. One small Python build step (standard library only) writes Camila's media into the page.

The look comes from the "Camila UGC Portfolio" design canvas (cream, ink, peach, terracotta; Bricolage Grotesque + Inter; torn-paper bands). The page structure follows angelicadrey.com.

Paths below are inside `ugc/` unless they start with `/` (repository root).

```
index.html        the page: structure, English text, and CMS regions filled by build.py
styles.css        all styling; colour and font tokens at the top
main.js           enhancements + Russian and Italian translations of the fixed text
stats.json        Instagram numbers for the stats slider (edited in Pages CMS)
content/          media lists edited in Pages CMS: videos.json, photos.json, media.json
build.py          writes content/*.json into index.html
/.pages.yml                         Pages CMS config: the forms Camila sees (must be at the repository root)
/.github/workflows/deploy-ugc.yml   on pushes that touch ugc/: build, then copy ugc/ to the VPS
.deployignore     files in ugc/ that stay in GitHub and never go to the server
assets/
  uploads/        files Camila uploads through Pages CMS (created on first upload)
  placeholders/   SVG stand-ins for every photo and poster
  videos/         placeholder MP4s
  icons/  og-image.png  media-kit.pdf
favicon.ico  site.webmanifest  robots.txt  sitemap.xml
```

## How it fits together

```
Camila ──► app.pagescms.org ──► commit to enzovici/trendsetter (ugc/content/*.json, ugc/stats.json, ugc/assets/uploads/)
                                        │
                                        ▼
                         GitHub Action: python3 build.py in ugc/ ──► rsync ugc/ ──► cerebrus VPS (Caddy)
```

```
index.html after build
    ├─ no JS ──► full page readable and indexable; video links open the MP4 directly
    └─ main.js ─► swaps in Russian or Italian, video previews, lightbox, stats slider
```

`build.py` only rewrites the parts of `index.html` between `<!-- cms:NAME -->` and `<!-- /cms:NAME -->`. Everything else in `index.html` is edited by hand as before. Do not edit inside those markers: the next build overwrites it.

## What Camila edits in Pages CMS

| Form | Controls |
|---|---|
| UGC videos | every video card: category, video, poster, brand, ad format, client or concept, short description in EN (RU, IT optional) |
| UGC photos | the photography grid: photo + description |
| Hero, About and Why me photos | 3 hero photos, intro video + poster, About photo, Why me photo |
| Instagram stats | the numbers in the stats slider |

The order in each list is the order on the page. A save goes live in about a minute.

Texts, case studies, headings and translations of the fixed text are not in the CMS. They change rarely and are edited in `index.html` and `main.js`.

**Descriptions.** For a video she writes only what happens, for example "morning lip routine". The page builds "Play: morning lip routine, concept for Dior" (or "client project for" when *Paid client project* is on). An empty Russian or Italian field shows the English text in that language.

**Honesty.** Leave *Paid client project* off for concept and spec work. The card then says "Concept for [Brand]".

## One-time setup

1. **GitHub.** The site lives in `ugc/` of `enzovici/trendsetter`, which is a **public** repository: anyone can see the site files and Camila's uploads (they are public on the website anyway). Pushing a change under `ugc/` to `main` deploys it. Changes to the Python app do not trigger a deploy.
2. **Deploy key** (done 2026-11-23). An ed25519 key pair for the server user `camila-deploy`; see [Hosting](#hosting). The private key exists only in the GitHub secret below. To rotate it, generate a new pair, replace the public key in `/home/camila-deploy/.ssh/authorized_keys` on the server (keep the `command="/usr/bin/rrsync /var/www/camila",restrict` prefix), and update the secret.
3. **Repository secrets** (done; GitHub › Settings › Secrets and variables › Actions):
   - `SSH_PRIVATE_KEY`: the deploy private key
   - `SSH_KNOWN_HOSTS`: output of `ssh-keyscan -t ed25519 83.228.205.131`
   - `DEPLOY_TARGET`: `camila-deploy@83.228.205.131:./` (`./` is `/var/www/camila`, because rrsync anchors paths there)

   Never commit a private key: the repository is public. To check the deploy, run the workflow by hand (Actions › Deploy UGC site › Run workflow).
4. **Pages CMS.** Sign in at https://app.pagescms.org with GitHub, install the Pages CMS GitHub App on `enzovici/trendsetter` only, open the repository. Camila's forms only show the files listed in `/.pages.yml`.
5. **Invite Camila** in Pages CMS (Collaborators, by email). She does not need a GitHub account.

## Preview locally

From the `ugc/` folder:

```bash
python3 build.py
```

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000. Run `git pull` first to get Camila's latest changes.

## Before launch checklist

Everything below is placeholder content.

- [x] Contact email `camila@milanoprive.com` forwards to Camila's Gmail (Namecheap › milanoprive.com › Domain › Redirect Email). It is in `index.html` in three places: hero, contact and JSON-LD in `<head>`. Namecheap forwarding only works for `@milanoprive.com` addresses, not for the `camila.` subdomain.
- [ ] In Pages CMS: 3 hero photos (light and soft: the name sits on them in dark ink), intro video + poster, About photo, Why me photo
- [ ] In Pages CMS: replace the 12 placeholder videos and the 8 placeholder photos
- [ ] Both case studies: the concepts, kits, numbers and AI note are invented examples. Replace them with real projects.
- [ ] `assets/media-kit.pdf`
- [ ] Camila proofreads the Italian and Russian text in `main.js` and `content/*.json`

## Updating the stats

In Pages CMS, open **Instagram stats** about once a month. In Instagram: Professional dashboard, period 30 days.

| Field | Where in the Instagram dashboard |
|---|---|
| Views | Performance › Views |
| Accounts reached | Performance › Viewers |
| Interactions | Performance › Interactions by content type, sum of all rows |
| Followers | Home › Followers |
| Top audience languages | Audience › Top languages, top 3, as two-letter codes (`en`, `ru`, `it`) |
| Date | the day she copied the numbers |

The numbers are formatted for each language automatically (165K, 165 тыс.). If `stats.json` cannot be read, the slider stays hidden rather than showing anything wrong.

Only copy real numbers from the dashboard. A 30-day window moves a lot: a viral reel lifts it, and the next quiet month drops it.

**Later: automatic updates.** A scheduled GitHub Action can call the Instagram Graph API and commit the same `stats.json`. Nothing else changes. It needs Camila's account set as Business or Creator and linked to a Facebook Page, a Meta developer app, and a token that is refreshed every 60 days.

## Media sizes

The page crops to these shapes, so keep the subject centred.

| Where | Shape | Export size |
|---|---|---|
| Hero, 3 photos | 4:5 | 1000×1250, light and soft |
| Intro video poster, About photo | 9:16 (the intro phone crops a little taller) | 1080×1920 |
| Why me photo | 4:5 | 1200×1500 |
| Video card posters | 9:13 | 1080×1560 |
| UGC photos | 4:5 | 1200×1500 |
| Videos | 9:16 | H.264 MP4, 1080×1920, under 5 MB |

Keep photos under about 300 KB. Large files make the page slow and the repository heavy. On a Mac, this resizes and compresses a photo with nothing to install:

```bash
sips -Z 1600 -s format jpeg -s formatOptions 80 IMG_1234.HEIC --out photo.jpg
```

Video export and a poster frame with ffmpeg (`brew install ffmpeg`):

```bash
ffmpeg -i input.mov -vf scale=1080:1920 -c:v libx264 -crf 23 -preset slow -c:a aac -b:a 128k -movflags +faststart video.mp4
```

```bash
ffmpeg -ss 0.5 -i video.mp4 -frames:v 1 -q:v 3 poster.jpg
```

**Replacing a file.** Upload a new file with a new name instead of overwriting the old one. The server tells browsers to cache images and videos for a year, so a file replaced under the same name may keep showing the old version.

Videos never load on page load. Each card shows its poster. The video starts downloading only when the visitor hovers (desktop) or taps (phone).

When every placeholder is replaced, delete `assets/placeholders/` and the placeholder MP4s in `assets/videos/`.

## Developer notes

**New video category.** Add it in three places: `CATEGORIES` in `build.py`, the category select in `/.pages.yml`, and `cat.<name>` in the `ru` and `it` blocks of `main.js`.

**New editable field.** Add it to `/.pages.yml`, to the matching `content/*.json` entries, and to the function in `build.py` that renders that region.

**Adding a case study.** Copy a whole `<article class="case">` inside `<section class="campaigns">`. Give every case-specific `data-i18n` key a new prefix, for example `c3.`, and add the Russian and Italian strings to `main.js`. Shared labels (`cs.*`, `role.*`, `pr.*`) already exist. Change `aria-labelledby` and the title `id` to `c3-title`. Keep the AI note honest: delete it if no AI was used.

## Editing the fixed text in three languages

- **English** is the text inside `index.html`, outside the CMS regions.
- **Russian** and **Italian** are in the `ru` and `it` blocks of `I18N` at the top of `main.js`. Each element with `data-i18n="key"` gets the string with the same key. Every key must exist in both blocks.
- Media descriptions are not in `main.js`. They are in `content/*.json`, and `build.py` writes them into a JSON block at the end of `index.html` that `main.js` reads.
- The Italian was written by Claude. Have Camila read it before launch, especially About and Why me, which are in her own voice.
- Strings shown only by JavaScript (lightbox caption, tap hint, stats note) have an English version in the `en` block of `main.js`.

**Adding another language.** Copy the `it` block in `main.js`, rename it (for example `fr`), translate every value, add `alt_fr` fields to `/.pages.yml` and `build.py`, then add a button to the `.lang` group in `index.html`:

```html
<button type="button" data-lang="fr" aria-pressed="false" lang="fr">FR</button>
```

Only English is indexed by search engines; the other languages appear when a visitor clicks the switcher. The visitor's choice is saved in `localStorage`.

**Fonts.** Headings use Bricolage Grotesque, which has no Cyrillic. In Russian, `styles.css` switches headings to Onest. Body text is Inter, which covers both. Italian uses Bricolage as it is.

## Hosting

```
camila.milanoprive.com ──DNS A (Namecheap)──► 83.228.205.131 (cerebrus, Infomaniak)
                                               Caddy ──► /var/www/camila
```

- **DNS.** A record `camila` → `83.228.205.131` in Namecheap › milanoprive.com › Advanced DNS.
- **Web server.** Caddy, not nginx. The site block `camila.milanoprive.com { … }` is in `/etc/caddy/Caddyfile` on cerebrus, next to other sites. Caddy gets and renews the HTTPS certificate itself. After editing the Caddyfile: back it up, run `sudo caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile`, then `sudo systemctl reload caddy`.
- **Caching.** `/assets/*` is cached for a year. HTML, CSS, JS and `stats.json` are sent with `no-cache`, so browsers recheck them on every visit and changes show at once.
- **Security headers.** The Content-Security-Policy allows the inline `<script>` in `<head>` (the one that sets `class="js"`) by its sha256 hash. If you change that line, update the hash in the Caddyfile, or the script is blocked. Fonts may only come from Google Fonts. Adding any other external script, font or embed also needs a CSP change.
- **Deploy user.** `camila-deploy` has no password and no sudo. Its key may only run `rrsync` into `/var/www/camila`: no shell, no port forwarding, no paths outside that folder. It is listed in `AllowUsers` in `/etc/ssh/sshd_config.d/50-cerebrus.conf`.
- **No access log**, like the other marketing site on the server.

## Deploying

Normally the GitHub Action deploys on every push to `main` that touches `ugc/`. To deploy by hand from your computer (as the `ubuntu` admin user, writing as `camila-deploy` so file ownership stays the same), in the `ugc/` folder:

```bash
python3 build.py && rsync -avz --delete --exclude-from=.deployignore --rsync-path="sudo -u camila-deploy rsync" ./ cerebrus:/var/www/camila/
```

`cerebrus` is the SSH host alias in `~/.ssh/config`. No server restart is needed after a deploy.
