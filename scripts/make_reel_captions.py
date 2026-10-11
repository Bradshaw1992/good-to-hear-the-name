#!/usr/bin/env python3
"""Generate the paste-ready Reel caption file for Google Keep.

Single source of truth:
  - day + hook line  <- CONFIGS in make_reel_frames.py (cover_tease)
  - player name      <- docs/players.js
  - hashtags         <- CORE_TAGS + NICHE_TAGS in make_instagram_posts.py

Current house voice: hint-only hook, ?day=N pin, "play it yourself" CTA, no name in caption.

Run: scripts/.venv/bin/python scripts/make_reel_captions.py [START_DAY] [END_DAY]
     (defaults to the live batch, 82-103)
Output: marketing_print/reel_captions.txt  (plain text — paste straight into Google Keep)
"""
import os
import re
import ast
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
OUT = os.path.join(ROOT, "marketing_print", "reel_captions.txt")

import sys
START = int(sys.argv[1]) if len(sys.argv) > 1 else 82
END = int(sys.argv[2]) if len(sys.argv) > 2 else 103

# Pull tag blocks from the IG post generator (import is safe: its render code is under __main__).
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from make_instagram_posts import CORE_TAGS, NICHE_TAGS, HOME_URL  # noqa: E402


def load_configs():
    """ast-parse the CONFIGS literal out of make_reel_frames.py (day + cover_tease per player)."""
    src = open(os.path.join(ROOT, "scripts", "make_reel_frames.py")).read()
    m = re.search(r"CONFIGS = (\{.*?\n\})\n", src, re.S)
    return ast.literal_eval(m.group(1))


def load_names():
    src = open(os.path.join(DOCS, "players.js")).read()
    src = src[src.index("["): src.rstrip().rstrip(";").rindex("]") + 1]
    return {p["id"]: p["name"] for p in json.loads(src)}


def hashtags(pid):
    niche = NICHE_TAGS.get(pid, "")
    return f"{CORE_TAGS} {niche}".strip()


def block(day, pid, name, hook):
    bar = "=" * 60
    tags = hashtags(pid)
    return f"""{bar}
DAY {day} — {name.upper()} — {pid}/{pid}_reel.mp4
{bar}
{hook}

Day {day}. You only get three clues here, so if you are stumped, that is rather the point.

The full puzzle is on the website. Five clues, five guesses, and the reveal. Have a proper go:
{HOME_URL}?day={day}

A new player every single day, with well over a hundred more to play.

Made by a fan, for the obsessives.

FIRST COMMENT (hashtags):
{tags}
"""


if __name__ == "__main__":
    configs = load_configs()
    names = load_names()
    # index configs by day for the requested range
    by_day = {c["day"]: (pid, c) for pid, c in configs.items() if "day" in c}

    header = (
        f"GOOD TO HEAR THE NAME — REEL CAPTIONS (Days {START}-{END})\n\n"
        "Paste the caption block when you post that day's reel.\n"
        "Drop the hashtag line as your first comment.\n"
        "Never put the answer in the caption. Keep replies playful — don't confirm the answer.\n\n"
    )

    parts = [header]
    missing = []
    for day in range(START, END + 1):
        if day not in by_day:
            missing.append(day)
            continue
        pid, cfg = by_day[day]
        hook = cfg.get("cover_tease") or cfg.get("tom_opener") or ""
        if not hook:
            missing.append(day)
            continue
        parts.append(block(day, pid, names.get(pid, pid), hook))
        parts.append("")  # blank spacer between days

    with open(OUT, "w") as f:
        f.write("\n".join(parts))
    print(f"wrote {os.path.relpath(OUT, ROOT)}  (days {START}-{END})")
    if missing:
        print(f"WARNING: no reel config/hook for days: {missing}")
