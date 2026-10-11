#!/usr/bin/env python3
"""Fetch player photos from a list of URLs, measure them, and stage them for distribution.

Solves the slow half of the photo job: you find a picture and paste the link, this handles
downloading, format conversion, dimension checking and watermark-risk flagging. It then hands
straight off to distribute_player_pictures.py, which does the silhouettes.

Input file format -- one player per line, id then whitespace then URL. Blank lines and # ignored:

    seamus_coleman   https://example.com/path/coleman.jpg
    ricardo_quaresma https://example.com/path/quaresma.png

Usage
=====
    # download to a temp dir, report sizes, keep nothing. Always do this first.
    python3 scripts/fetch_player_photos.py planning/v1_8_photo_urls.txt --check

    # download and stage into Player Pictures/ ready for the silhouette step
    python3 scripts/fetch_player_photos.py planning/v1_8_photo_urls.txt --commit

    # then, as normal:
    python3 scripts/distribute_player_pictures.py --review

Thresholds match distribute_player_pictures.py:
    short side >= 700   fine
    500-699             usable, slightly soft
    400-499             warn, it will show
    under 400           refused, find another
"""
import argparse, html, os, re, subprocess, sys, tempfile, shutil
from urllib.parse import urljoin, urlparse, parse_qs, unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGE_DIR = os.path.join(ROOT, "Player Pictures")

HARD_FLOOR, FLOOR, SOFT = 400, 500, 700

# Hosts that commonly serve watermarked comps. The Yakubu and Okocha reworks were both
# caused by watermarks that only became obvious after silhouetting.
WATERMARK_HOSTS = ("alamy", "gettyimages", "shutterstock", "istockphoto", "dreamstime",
                   "depositphotos", "123rf", "agefotostock", "imago-images", "profimedia",
                   "backpagepix", "actionplus", "sportsfile", "offside-sports")

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")


def unwrap_redirect(url):
    """Google/Bing search results wrap the real destination in a ?url= parameter."""
    for _ in range(3):
        p = urlparse(url)
        if p.netloc.endswith(("google.com", "google.co.uk", "bing.com")) and p.path in ("/url", "/aclk"):
            q = parse_qs(p.query)
            nxt = (q.get("url") or q.get("q") or q.get("u") or [None])[0]
            if nxt and nxt.startswith(("http://", "https://")):
                url = unquote(nxt)
                continue
        break
    return url


def upsize_wikimedia(url):
    """Wikimedia thumb URLs carry their width. Bump it so we get a usable size, not a 220px lead image.
    .../thumb/a/ab/Name.jpg/220px-Name.jpg  ->  .../thumb/a/ab/Name.jpg/1280px-Name.jpg
    """
    m = re.search(r"/thumb/(.+)/(\d+)px-([^/]+)$", url)
    if m and "wikimedia.org" in url or (m and "wikipedia.org" in url):
        width = int(m.group(2))
        if width < 1280:
            return url[:m.start(2)] + "1280" + url[m.end(2):]
    return url


def images_from_html(path, base_url):
    """Pull candidate image URLs out of a page, best guess first.
    og:image and twitter:image are what news sites and Wikipedia set for sharing, so they are
    almost always the main photo. Falls back to the longest <img> list.
    """
    try:
        doc = open(path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return []
    cands = []
    for pat in (r'<meta[^>]+property=["\']og:image(?::secure_url)?["\'][^>]+content=["\']([^"\']+)',
                r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image',
                r'<meta[^>]+name=["\']twitter:image(?::src)?["\'][^>]+content=["\']([^"\']+)'):
        cands += re.findall(pat, doc, re.I)
    # then any <img> that looks like a photo rather than an icon or tracking pixel
    for src in re.findall(r'<img[^>]+?src=["\']([^"\']+)', doc, re.I):
        if re.search(r"\.(jpe?g|png|webp|avif)(\?|$)", src, re.I) and not re.search(
                r"(sprite|logo|icon|avatar|placeholder|1x1|pixel|badge|crest)", src, re.I):
            cands.append(src)
    out, seen = [], set()
    for c in cands:
        u = upsize_wikimedia(urljoin(base_url, html.unescape(c.strip())))
        if u.startswith(("http://", "https://")) and u not in seen:
            seen.add(u)
            out.append(u)
    return out[:6]


def curl_to(url, dest):
    r = subprocess.run(["curl", "-sSL", "--max-time", "45", "--max-filesize", "40000000",
                        "-A", UA, "-o", dest, url], capture_output=True, text=True)
    ok = r.returncode == 0 and os.path.exists(dest) and os.path.getsize(dest) > 0
    return ok, (r.stderr or "empty response").strip().split("\n")[0][:90]


def probe(path):
    """Returns (format, w, h) or None if ImageMagick cannot read it as an image."""
    r = subprocess.run(["identify", "-format", "%m %w %h", path + "[0]"],
                       capture_output=True, text=True)
    if r.returncode != 0 or len(r.stdout.split()) < 3:
        return None
    f, w, h = r.stdout.split()[:3]
    return f, int(w), int(h)


def parse_list(path):
    """Returns (jobs, malformed, unfilled_count).

    A line that is just an id with no URL is an unfilled slot, not an error -- the template
    is seeded with all 86 ids so it can be filled in over several sittings. Only genuinely
    broken lines are reported.
    """
    out, bad, unfilled = [], [], 0
    for n, raw in enumerate(open(path), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        pid = parts[0].strip()
        if not re.fullmatch(r"[a-z0-9_]+", pid):
            bad.append((n, f"{line}   <- id must be lowercase and underscores only"))
            continue
        if len(parts) == 1:
            unfilled += 1          # seeded slot, no URL yet
            continue
        url = parts[1].strip()
        if not url.lower().startswith(("http://", "https://")):
            bad.append((n, f"{line}   <- second field is not a URL"))
            continue
        out.append((pid, url))
    return out, bad, unfilled


def download(url, dest_noext):
    """Fetch url. If it turns out to be a web page, find the best image on it and fetch that.
    Returns (jpg_path, note, actual_url) or (None, reason, actual_url).
    """
    url = unwrap_redirect(url)
    url = upsize_wikimedia(url)
    tmp = dest_noext + ".download"

    ok, err = curl_to(url, tmp)
    if not ok:
        return None, err, url
    info = probe(tmp)

    page_note = ""
    if info is None:
        # Not an image. Treat it as a page and look for the photo on it.
        found = images_from_html(tmp, url)
        os.remove(tmp)
        if not found:
            return None, "page had no usable image (try the image address directly)", url
        best = None
        for cand in found:
            ok, err = curl_to(cand, tmp)
            if not ok:
                continue
            i = probe(tmp)
            if i is None:
                continue
            if best is None or min(i[1], i[2]) > min(best[1][1], best[1][2]):
                if best is not None and os.path.exists(best[0]):
                    os.remove(best[0])
                keep = dest_noext + ".best"
                shutil.move(tmp, keep)
                best = (keep, i, cand)
            else:
                os.remove(tmp)
        if best is None:
            return None, "found images on the page but none downloadable", url
        shutil.move(best[0], tmp)
        info, url = best[1], best[2]
        page_note = " (pulled from the page)"

    fmt, w, h = info
    jpg = dest_noext + ".jpg"
    conv = subprocess.run(["magick", tmp + "[0]", "-strip", "-quality", "95", jpg],
                          capture_output=True, text=True)
    os.remove(tmp)
    if conv.returncode != 0:
        return None, "conversion failed: " + conv.stderr.strip()[:70], url
    return jpg, f"{fmt} {w}x{h}{page_note}", url


def verdict(short):
    if short < HARD_FLOOR:  return "REFUSED", f"{short}px short side, too small to use"
    if short < FLOOR:       return "WARN   ", f"{short}px, usable but it will show"
    if short < SOFT:        return "ok     ", f"{short}px, slightly soft"
    return "GOOD   ", f"{short}px"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("listfile")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="download, report, keep nothing")
    g.add_argument("--commit", action="store_true", help="stage into Player Pictures/")
    ap.add_argument("--force", action="store_true", help="overwrite an existing staged photo")
    args = ap.parse_args()

    for tool in ("curl", "identify", "magick"):
        if not shutil.which(tool):
            sys.exit(f"missing required tool: {tool}  (brew install imagemagick curl)")

    jobs, bad, unfilled = parse_list(args.listfile)
    for n, line in bad:
        print(f"line {n}: could not parse -- {line}")
    if not jobs:
        sys.exit(f"No URLs filled in yet. {unfilled} ids are waiting in {args.listfile} -- "
                 f"paste a link after any of them and run this again.")

    work = tempfile.mkdtemp(prefix="gthn_photos_")
    results, refused, failed = [], [], []
    tail = f"   ({unfilled} ids still have no URL)" if unfilled else ""
    print(f"{len(jobs)} to fetch{tail}\n")

    for pid, url in jobs:
        staged = os.path.join(STAGE_DIR, pid + ".jpg")
        if args.commit and os.path.exists(staged) and not args.force:
            print(f"  skip    {pid:<32} already staged (use --force to replace)")
            continue
        jpg, info, used = download(url, os.path.join(work, pid))
        if jpg is None:
            print(f"  FAILED  {pid:<32} {info}")
            failed.append((pid, info))
            continue
        w, h = subprocess.run(["identify", "-format", "%w %h", jpg],
                              capture_output=True, text=True).stdout.split()
        w, h = int(w), int(h)
        tag, note = verdict(min(w, h))
        wm = " [watermark risk: " + next(k for k in WATERMARK_HOSTS if k in used.lower()) + "]" \
             if any(k in used.lower() for k in WATERMARK_HOSTS) else ""
        kb = os.path.getsize(jpg) // 1024
        print(f"  {tag} {pid:<32} {w}x{h}  {kb}kB  {note}{wm}")
        if tag.strip() == "REFUSED":
            refused.append((pid, f"{w}x{h}"))
            continue
        results.append((pid, jpg))
        if args.commit:
            os.makedirs(STAGE_DIR, exist_ok=True)
            shutil.copy2(jpg, staged)

    print(f"\n{'staged' if args.commit else 'would stage'}: {len(results)}"
          f"   refused: {len(refused)}   failed: {len(failed)}")
    if refused:
        print("\nneed a different source for:")
        for pid, dims in refused:
            print(f"  {pid}  ({dims})")
    if failed:
        print("\ndownload failed for:")
        for pid, why in failed:
            print(f"  {pid}  {why}")
    if args.commit and results:
        print(f"\nnext:  python3 scripts/distribute_player_pictures.py --review")
    shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
