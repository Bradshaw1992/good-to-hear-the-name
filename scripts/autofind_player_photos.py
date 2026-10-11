#!/usr/bin/env python3
"""Find a photo for every player automatically, so you don't have to search for any of them.

Queries the Wikipedia API for each player, takes the article's lead image at full original
resolution, and writes the URL back into the URL list file. You then review what it picked
and override anything you don't like, rather than sourcing all 86 by hand.

Wikipedia is used because in testing it was the only source that worked every time, returns
the largest images, resolves mononyms and disambiguation on its own (Guti, Dida, Hulk, Raul,
Marcelo all resolved correctly), and is not login-walled or scraper-blocked.

If the lead image is too small, it falls back to searching Wikimedia Commons for a bigger one.

Usage
=====
    # fill in every id that has no URL yet, writing results into the list file
    python3 scripts/autofind_player_photos.py planning/v1_8_photo_urls.txt

    # overwrite URLs that are already there too
    python3 scripts/autofind_player_photos.py planning/v1_8_photo_urls.txt --replace

    # then review and fetch as normal
    python3 scripts/fetch_player_photos.py planning/v1_8_photo_urls.txt --commit
    python3 scripts/distribute_player_pictures.py --review
"""
import argparse, json, re, sys, time, urllib.error, urllib.parse, urllib.request

API = "https://en.wikipedia.org/w/api.php"
COMMONS = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "GoodToHearTheName/1.0 (daily football quiz; goodtohearthename.co.uk)"}
MIN_SHORT = 500          # matches the floor in distribute_player_pictures.py

# A silhouette of a retired player in a TV studio suit is useless, and the reveal is confusing.
# We want them in kit, on the pitch, during their playing career. Commons filenames are
# unusually informative about this, so we score on them.
WRONG_ERA = ("coach", "manager", "pundit", "interview", "press", "conference", "suit",
             "award", "gala", "ceremony", "signing", "autograph", "fan", "charity",
             "studio", "commentator", "director", "ambassador", "retired", "legends",
             "veterans", "golf", "premiere", "red carpet", "book", "podcast")
NOT_A_PLAYER = ("statue", "mural", "graffiti", "banner", "plaque", "dress", "tenue",
                "stadium", "logo", "badge", "crest", "flag", "signature", "shirt only",
                "boot", "trophy only", "stamp", "coin", "poster", "cartoon", "drawing",
                "artwork", "grave", "memorial", "museum", "tifo", "mosaic")
ON_PITCH = ("v ", " vs", "match", "training", "warm", "friendly", "cup", "league",
            "derby", "goal", "kick", "cap", "debut", "euro", "world cup", "qualifier")
THROTTLE = 0.7           # be polite; the API 429s if you hammer it


def api(base, **params):
    params.setdefault("format", "json")
    url = base + "?" + urllib.parse.urlencode(params)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25) as r:
                time.sleep(THROTTLE)
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(3 * (attempt + 1))
                continue
            raise
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2)
    return None


def lead_image(display_name):
    """Best Wikipedia lead image for this player. Returns (title, url, w, h) or None."""
    try:
        s = api(API, action="query", list="search", srlimit=3,
                srsearch=f"{display_name} footballer")
    except Exception as e:
        return None, f"search failed: {e}"
    if not s:
        return None, "Wikipedia search returned nothing (rate limited?)"
    hits = [h["title"] for h in s.get("query", {}).get("search", [])]
    if not hits:
        return None, "no Wikipedia article found"
    for title in hits:
        try:
            q = api(API, action="query", prop="pageimages", piprop="original", titles=title)
        except Exception:
            continue
        if not q:
            continue
        page = next(iter(q.get("query", {}).get("pages", {}).values()), {})
        o = page.get("original")
        if o:
            return (title, o["source"], o["width"], o["height"]), None
    return None, f"article '{hits[0]}' has no lead image"


def career_window(title):
    """Earliest and latest playing year from the article infobox, so we can judge a photo's era."""
    try:
        q = api(API, action="query", prop="revisions", rvprop="content", rvslots="main",
                titles=title, redirects=1)
    except Exception:
        return None
    if not q:
        return None
    page = next(iter(q.get("query", {}).get("pages", {}).values()), {})
    try:
        wt = page["revisions"][0]["slots"]["main"]["*"]
    except Exception:
        return None
    years = [int(y) for y in re.findall(r"\|\s*years\d*\s*=\s*(\d{4})", wt)]
    years += [int(y) for y in re.findall(r"\|\s*caps?\d*years\s*=\s*(\d{4})", wt)]
    if not years:
        years = [int(y) for y in re.findall(r"(19[5-9]\d|20[0-2]\d)", wt[:4000])]
    if not years:
        return None
    return min(years), max(years) + 2        # +2 slack: photos often post-date the last season


def score_candidate(filename, window):
    """Higher is better. Rejects return None."""
    low = filename.lower()
    if any(w in low for w in NOT_A_PLAYER):
        return None
    sc = 0
    if any(w in low for w in WRONG_ERA):
        sc -= 40
    if any(w in low for w in ON_PITCH):
        sc += 12
    yrs = [int(y) for y in re.findall(r"\b(19[5-9]\d|20[0-2]\d)\b", filename)]
    if yrs and window:
        lo, hi = window
        if any(lo <= y <= hi for y in yrs):
            sc += 45                          # in-career year in the filename: the strongest signal
        else:
            sc -= 35                          # dated, and outside his playing years
    elif yrs:
        sc += 5
    else:
        sc -= 8                               # undated files are a coin flip
    return sc


def commons_image(display_name, window=None):
    """Biggest Commons photo that is demonstrably OF this player AND from his playing era.

    Deliberately strict. A loose earlier version returned a Bergkamp statue, a group photo
    containing Harry Styles for Fowler, and a woman in traditional Dida dress. A wrong or
    wrong-era photo shipped silently is worse than asking for one by hand.
    """
    surname = display_name.split()[-1].lower()
    if len(surname) < 4:
        return None
    cands = []
    for query in (f"{display_name} footballer", display_name):
        try:
            s = api(COMMONS, action="query", list="search", srnamespace=6, srlimit=25,
                    srsearch=query)
        except Exception:
            continue
        if not s:
            continue
        for h in s.get("query", {}).get("search", []):
            t = h["title"]
            if not re.search(r"\.(jpe?g|png)$", t, re.I) or surname not in t.lower():
                continue
            stem = re.sub(r"^File:|\.[a-z]+$", "", t)
            others = [w for w in re.findall(r"\b[A-Z][a-z]{3,}\b", stem)
                      if w.lower() not in display_name.lower()
                      and not re.match(r"(19|20)\d\d", w)]
            if len(others) >= 3:               # a crowd of names means a group shot
                continue
            sc = score_candidate(stem, window)
            if sc is None:
                continue
            cands.append((sc, t))
        if cands:
            break
    if not cands:
        return None
    cands.sort(key=lambda x: -x[0])
    best = None
    for sc, t in cands[:12]:
        try:
            q = api(COMMONS, action="query", prop="imageinfo", iiprop="url|size", titles=t)
        except Exception:
            continue
        if not q:
            continue
        for page in q.get("query", {}).get("pages", {}).values():
            for ii in page.get("imageinfo", []):
                w, h = ii.get("width", 0), ii.get("height", 0)
                if min(w, h) < MIN_SHORT:
                    continue
                # score first, size as the tie-break
                if best is None or sc > best[4] or (sc == best[4] and min(w, h) > min(best[2], best[3])):
                    best = (page["title"], ii["url"], w, h, sc)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("listfile")
    ap.add_argument("--replace", action="store_true",
                    help="also overwrite ids that already have a URL")
    args = ap.parse_args()

    lines = open(args.listfile).read().splitlines()
    # display names come from the clues file so the search gets a real name, not an id
    names = {}
    try:
        import unicodedata
        for l in open("planning/v1_8_picked_clues.md"):
            if l.startswith("## ") and not any(k in l for k in ("OUTSTANDING", "STILL TO DO", "RECHECK")):
                dn = l[3:].strip()
                key = unicodedata.normalize("NFKD", dn).encode("ascii", "ignore").decode()
                key = re.sub(r"[^a-z0-9]+", "_", key.replace("'", "").replace("-", " ").lower()).strip("_")
                names[key] = dn
    except OSError:
        pass

    out, found, small, missed = [], 0, [], []
    for raw in lines:
        line = raw.rstrip()
        s = line.strip()
        if not s or s.startswith("#"):
            out.append(line); continue
        parts = s.split(None, 1)
        pid = parts[0]
        if not re.fullmatch(r"[a-z0-9_]+", pid):
            out.append(line); continue
        if len(parts) == 2 and not args.replace:
            out.append(line); continue

        display = names.get(pid, pid.replace("_", " ").title())

        # 1. find the article, and from it the playing-career years
        res, err = lead_image(display)
        title = res[0] if res else None
        window = career_window(title) if title else None

        # 2. Commons first, scored for playing era, because Wikipedia lead images for
        #    retired players are usually them now, in a suit, as a pundit or coach
        pick = commons_image(display, window)
        src = "commons"

        # 3. fall back to the article lead image only if Commons offers nothing
        if pick is None and res:
            _, url, w, h = res
            pick = (title, url, w, h, 0)
            src = "lead"

        if pick is None:
            print(f"  MISS  {pid:<26} {err or 'nothing found'}")
            out.append(line)
            missed.append((pid, err or "nothing found"))
            continue

        label, url, w, h, sc = pick
        short = min(w, h)
        tag = "GOOD " if short >= 700 else ("ok   " if short >= MIN_SHORT else "SMALL")
        era = ""
        if src == "lead":
            era = "  <- article lead, may be a modern photo"
        elif window:
            era = f"  (career {window[0]}-{window[1] - 2})"
        name = re.sub(r"^File:|\.[a-z]+$", "", label)[:44]
        print(f"  {tag} {pid:<26} {w}x{h:<6} {name}{era}")
        out.append(f"{pid} {url}")
        found += 1
        if short < MIN_SHORT:
            small.append((pid, f"{w}x{h}"))

    open(args.listfile, "w").write("\n".join(out) + "\n")
    print(f"\nfilled {found}   too small {len(small)}   not found {len(missed)}")
    for pid, d in small:
        print(f"  small: {pid} ({d}) -- may still be usable, check the preview")
    for pid, e in missed:
        print(f"  manual: {pid} -- {e}")
    if found:
        print(f"\nnext:  python3 scripts/fetch_player_photos.py {args.listfile} --commit")


if __name__ == "__main__":
    main()
