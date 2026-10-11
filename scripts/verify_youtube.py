#!/usr/bin/env python3
"""Verify YouTube links against the oEmbed endpoint before they go anywhere near content.json.

Video IDs are opaque 11-character strings, exactly the kind of thing a language model will
invent without noticing. oEmbed returns the real title and channel for a live video and a
404 for a dead or fabricated one, so this catches both a broken link and a video that is
about the wrong person.

Usage:  python3 scripts/verify_youtube.py candidates.json
        -> writes planning/v1_8_build/youtube.json with only the links that passed
"""
import json
import unicodedata, re, sys, time, urllib.error, urllib.parse, urllib.request

OUT = 'planning/v1_8_build/youtube.json'
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"}



def strip_accents(text):
    """Kanoute should match Kanoute. YouTube titles use the real spelling."""
    return "".join(c for c in unicodedata.normalize("NFD", text)
                   if unicodedata.category(c) != "Mn")

def oembed(url):
    """Returns (title, author) for a live video, or None."""
    q = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(url, safe="")
    try:
        with urllib.request.urlopen(urllib.request.Request(q, headers=UA), timeout=20) as r:
            d = json.load(r)
            return d.get("title", ""), d.get("author_name", "")
    except urllib.error.HTTPError:
        return None            # 404 = no such video, 401 = private/embed-disabled
    except Exception:
        return None


def surname_tokens(name):
    """Tokens that ought to appear in a title about this player."""
    parts = [p for p in re.split(r"[\s'-]+", name) if len(p) > 2]
    return [strip_accents(p.lower()) for p in parts]


def main():
    cands = json.load(open(sys.argv[1]))
    passed, failed, mismatch = [], [], []
    for c in cands:
        name, url = c["name"], c.get("youtube")
        if not url:
            failed.append((name, "no candidate found"))
            continue
        m = re.search(r"[?&]v=([A-Za-z0-9_-]{11})", url)
        if not m:
            failed.append((name, f"not a standard watch URL: {url[:50]}"))
            continue
        clean = f"https://www.youtube.com/watch?v={m.group(1)}"
        res = oembed(clean)
        time.sleep(0.3)
        if res is None:
            failed.append((name, "video does not exist or is not embeddable"))
            continue
        title, author = res
        toks = surname_tokens(name)
        hay = strip_accents((title + " " + author).lower())
        hit = any(t in hay for t in toks)
        row = {"name": name, "youtube": clean, "title": title, "channel": author}
        if hit:
            passed.append(row)
            print(f"  OK       {name:<26} {title[:56]}")
        else:
            mismatch.append(row)
            print(f"  MISMATCH {name:<26} {title[:56]}  <- title does not name the player")
    json.dump(passed, open(OUT, 'w'), indent=1, ensure_ascii=False)
    print(f"\npassed {len(passed)}   title mismatch {len(mismatch)}   failed {len(failed)}")
    for n, why in failed:
        print(f"  no link: {n}  ({why})")
    for r in mismatch:
        print(f"  check by hand: {r['name']}  {r['youtube']}  \"{r['title']}\"")
    print(f"\nwrote {len(passed)} verified links to {OUT}")


if __name__ == "__main__":
    main()
