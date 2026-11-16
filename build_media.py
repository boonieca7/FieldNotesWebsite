"""Make the web-sized copies of every image the posts use, into site/media/.

Only needed when posts or photos change. It reads the original photos from the local
WordPress backup, which is not in this repository:

    python build_media.py /path/to/backups/2026-11-15T2342Z [seconds]

Originals are never modified. Re-running skips images already done, so it can run in
short passes. Writes site/media/manifest.json mapping each source URL to its local copy.
"""
import json, glob, os, sys, time
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.abspath(__file__))
if len(sys.argv) < 2:
    sys.exit(__doc__)
BACKUP = sys.argv[1]
DIST = os.path.join(ROOT, 'site')
MEDIA = os.path.join(DIST, 'media')
FULL, THUMB = 1600, 800
deadline = time.time() + float(sys.argv[2] if len(sys.argv) > 2 else 600)

def local_source(url):
    p = urlparse(url)
    for host in [p.netloc, 'camclelland-jhibt.wordpress.com', 'camclelland-jhibt.files.wordpress.com']:
        for path in [p.path, p.path.replace('/wp-content/uploads', '')]:
            fp = os.path.join(BACKUP, 'raw', host, path.lstrip('/'))
            if os.path.isfile(fp):
                return fp
    return None

def out_rel(url):
    path = urlparse(url).path.replace('/wp-content/uploads/', '')
    stem = os.path.splitext(path)[0]
    return stem + '.jpg'

urls = set()
for f in glob.glob(os.path.join(ROOT, 'content', '*.json')):
    d = json.load(open(f, encoding='utf-8'))
    s = BeautifulSoup(d['content'], 'lxml')
    for img in s.find_all('img'):
        urls.add(img['src'].split('?')[0])
    fi = d.get('featured_image')
    if fi:
        urls.add(fi.split('?')[0])

manifest_path = os.path.join(MEDIA, 'manifest.json')
manifest = json.load(open(manifest_path)) if os.path.exists(manifest_path) else {}
done = skipped = 0
for url in sorted(urls):
    rel = out_rel(url)
    full = os.path.join(MEDIA, rel)
    thumb = os.path.join(MEDIA, 'thumbs', rel)
    if os.path.exists(full) and os.path.exists(thumb) and url in manifest:
        continue
    if time.time() > deadline:
        skipped += 1
        continue
    src = local_source(url)
    if not src:
        manifest[url] = None
        continue
    im = ImageOps.exif_transpose(Image.open(src))
    if im.mode not in ('RGB', 'L'):
        bg = Image.new('RGB', im.size, (255, 255, 255))
        im = im.convert('RGBA'); bg.paste(im, mask=im.split()[-1]); im = bg
    im = im.convert('RGB')
    os.makedirs(os.path.dirname(full), exist_ok=True)
    os.makedirs(os.path.dirname(thumb), exist_ok=True)
    w, h = im.size
    a = im.copy(); a.thumbnail((FULL, FULL)); a.save(full, quality=80, optimize=True, progressive=True)
    b = im.copy(); b.thumbnail((THUMB, THUMB)); b.save(thumb, quality=78, optimize=True, progressive=True)
    manifest[url] = {'full': 'media/' + rel, 'thumb': 'media/thumbs/' + rel, 'w': a.size[0], 'h': a.size[1]}
    done += 1

os.makedirs(MEDIA, exist_ok=True)
json.dump(manifest, open(manifest_path, 'w'), indent=1, sort_keys=True)
missing = [u for u, v in manifest.items() if v is None]
print(f'urls={len(urls)} processed_now={done} remaining={skipped} missing={len(missing)}')
for u in missing:
    print('MISSING', u)
