"""Download every source URL in mirror/urls.json that is not mirrored yet; write mirror/map.json.

Stills over 1 MB are resized to at most 1920 px wide and re-encoded (JPEG q86, or WebP when they have
transparency); animated images and small files are kept byte for byte. Nothing is ever deleted.
"""
import concurrent.futures as cf, hashlib, io, json, os, urllib.request
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, "mirror")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/124 Safari/537.36 nuvio-art"}
urls = json.load(open(os.path.join(M, "urls.json")))
mp = json.load(open(os.path.join(M, "map.json"))) if os.path.exists(os.path.join(M, "map.json")) else {}


def ext_of(b):
    if b[:6] in (b"GIF87a", b"GIF89a"): return "gif"
    if b[:8] == b"\x89PNG\r\n\x1a\n": return "png"
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP": return "webp"
    if b[:3] == b"\xff\xd8\xff": return "jpg"
    if b[4:8] == b"ftyp": return "mp4"
    return "bin"


def optimise(b, ext):
    if len(b) < 1_000_000 or ext not in ("png", "jpg", "webp"):
        return b, ext
    im = Image.open(io.BytesIO(b))
    if getattr(im, "is_animated", False):
        return b, ext
    if im.width > 1920:
        im = im.resize((1920, round(im.height * 1920 / im.width)), Image.LANCZOS)
    out = io.BytesIO()
    alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
    if alpha:
        im.convert("RGBA").save(out, "WEBP", quality=88, method=6); ext = "webp"
    else:
        im.convert("RGB").save(out, "JPEG", quality=86, optimize=True, progressive=True); ext = "jpg"
    return (out.getvalue(), ext) if out.tell() < len(b) else (b, ext_of(b))


def get(u):
    try:
        b = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
        return u, b
    except Exception as e:
        print("FAIL", u, e)
        return u, None


todo = [u for u in urls if u not in mp or not os.path.exists(os.path.join(ROOT, mp[u]))]
print(f"{len(urls)} sources, {len(todo)} to fetch")
with cf.ThreadPoolExecutor(12) as ex:
    for u, b in ex.map(get, todo):
        if not b:
            continue
        ext = ext_of(b)
        b, ext = optimise(b, ext)
        h = hashlib.sha1(u.encode()).hexdigest()[:16]
        rel = f"mirror/files/{h[:2]}/{h}.{ext}"
        os.makedirs(os.path.dirname(os.path.join(ROOT, rel)), exist_ok=True)
        open(os.path.join(ROOT, rel), "wb").write(b)
        mp[u] = rel
json.dump(mp, open(os.path.join(M, "map.json"), "w"), indent=0, sort_keys=True)
print(f"mirrored {len(mp)} / {len(urls)}")
