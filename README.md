# Field Notes From Abroad

The website for *Field Notes From Abroad*, Chrystin McLelland's field notes from a spring 2026 Erasmus+ semester in Timișoara, Romania, and the trips around it. It replaces the WordPress site at fieldnotesfromabroad.com.

This file is the guide to how the site works. If you are opening this repository with Claude, Claude reads this file first.

## The short version

| To change | Edit this | Then |
|---|---|---|
| A summary on a card or in search | `tldr.json` | Commit. The site rebuilds itself. |
| Journeys, series, threads, intro lines, fixed titles | `site_config.py` | Commit |
| The header mark (luggage tag, suitcase, postmark, paper boat) | `MARK` in `site_config.py` | Commit |
| Colours and type | Variables at the top of `assets/site.css` | Commit |
| A post's text | `content/<id>-<slug>.json` (the `content` field is the post HTML) | Commit |

Every commit to `main` runs `.github/workflows/deploy.yml`, which runs `python build.py` and publishes the `site/` folder to GitHub Pages. If the build finds a problem (a post not placed in any journey, a missing summary, a broken link or image) it stops and the live site stays as it was. The Actions tab shows what went wrong.

## What is in this repository

| Path | What it is |
|---|---|
| `content/` | The 57 published posts and the About page, exported from WordPress. Text, dates, original addresses, categories and tags. |
| `tldr.json` | Two-sentence summaries used on cards and in search, keyed by post ID. Drafts, meant to be rewritten. |
| `site_config.py` | The site's structure: 7 journeys, 3 series, 7 threads, display titles, header mark. |
| `build.py` | Turns `content/` into the pages in `site/`. |
| `marks.py` | The four candidate marks as SVG. |
| `assets/` | `site.css` (all styling) and `search.js` (the search page). Copied into `site/assets/` on build. |
| `site/` | The finished website. Pages are rebuilt on every commit. `site/media/` holds the web-sized photos (472 files, about 75 MB). |
| `build_media.py` | Makes the web-sized photos from the original WordPress backup. Only needed when photos change. |

## What the website needs to run

Only the `site/` folder. It is plain HTML, CSS and JavaScript with relative links, no server code and no database:

- the pages: `index.html`, `404.html`, and folders for `journeys/`, `series/`, `threads/`, `archive/`, `about/`, `search/`, plus one folder per post at its original address (`2026/05/27/the-view-from-seat-41/`)
- `site/assets/`: `site.css`, `search.js`, `search-index.js`, `favicon.svg`
- `site/media/`: the photos (`media/2026/...` full size for posts, `media/thumbs/...` for cards)

Fonts (Barlow Condensed, Source Serif 4, IBM Plex Mono) load from Google Fonts. Without a connection the pages fall back to similar system fonts.

You can open `site/index.html` straight from your computer to preview it.

## Running a build yourself

```
pip install -r requirements.txt
python build.py
```

Python 3.10 or newer. To regenerate photos after adding or replacing images, you also need Pillow and the local backup folder:

```
pip install Pillow
python build_media.py /path/to/backups/2026-11-15T2342Z
```

## Publishing

| What | Where |
|---|---|
| Code and hosting | GitHub, `boonieca7/FieldNotesWebsite`, served by GitHub Pages |
| Pages setting | Settings, Pages, Source: **GitHub Actions** |
| Address until the domain moves | https://boonieca7.github.io/FieldNotesWebsite/ |
| Domain | fieldnotesfromabroad.com, currently pointing at WordPress.com |

### Moving fieldnotesfromabroad.com to this site (when ready)

1. In the repository: Settings, Pages, Custom domain: `fieldnotesfromabroad.com`. Tick "Enforce HTTPS" once it is offered.
2. Wherever the domain's DNS is managed, point it at GitHub Pages: four `A` records for the apex (185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153) and a `CNAME` record for `www` pointing to `boonieca7.github.io`. If the domain was bought through WordPress.com, its DNS is managed there.
3. Every post keeps its original address, so links people already have will keep working.
4. Keep the WordPress site until the new one has been live for a while. Pointing the DNS back restores it.

## Decisions worth knowing

- Post text, photos and captions are as published. Changes from WordPress: titles of the duplicate "Stories of Romania" and "Chronicles of Romania" posts carry their subtitles; "Field Notes:" is dropped from the start of titles; a short first line that worked as a subtitle shows under the title.
- 423 of the 424 photos had no alt text on WordPress. They are left empty rather than given invented descriptions. Adding real descriptions is the main accessibility task left.
- One image in "Stories of Romania: The Raven of Corvin Castle" was already missing from the WordPress backup and shows a labelled placeholder.
- No comments, likes or newsletter sign-up. They would need a service behind them.
- This repository is public. Do not put anything private in it.

## Notes for Claude

- Read this file and `site_config.py` before changing anything. Most requests are edits to `site_config.py`, `tldr.json` or `assets/site.css`.
- `python build.py` must finish with "Link check: every local link and image resolves." before committing.
- Brand: navy #1C2F3C, slate #4A6274, kraft #C9AE86, paper #F5EEE6, stone #CFCFCA, Mărțișor red #B3362C (accent only). Barlow Condensed for labels and navigation, Source Serif 4 for titles and reading, IBM Plex Mono for dates and captions.
- Voice: the author resists AI-sounding phrasing (em dashes, "it's not X, it's Y", punchy parallel lists). Keep any new site copy plain and specific, and never rewrite her post text.
