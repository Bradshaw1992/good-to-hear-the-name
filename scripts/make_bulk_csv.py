#!/usr/bin/env python3
"""Build a Metricool bulk-import CSV for the upcoming IG + Facebook photo posts.

Each row: caption text, date, 08:00 time, the image's public R2 URL, and the hashtags as
the first comment; Facebook + Instagram set TRUE, every other network FALSE.

Prereq: the images must already be live at cdn.goodtohearthename.co.uk/social/<file>.jpg
(run scripts/upload_social_r2.sh first) — Metricool fetches the media by URL at import time.

Run: scripts/.venv/bin/python scripts/make_bulk_csv.py [START_DAY] [END_DAY] [HH:MM]
     defaults: 124 173 08:00
Output: marketing_print/instagram_posts/bulk_schedule_metricool.csv
"""
import os
import sys
import csv
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from make_instagram_posts import POSTS, load_players, caption_for, hashtags_for  # noqa: E402

EPOCH = datetime.date(2026, 5, 5)  # Day 1
# Images live in docs/social/ and are served by the website (GitHub Pages) after a normal push.
SOCIAL_BASE = "https://goodtohearthename.co.uk/social"
OUT = os.path.join(ROOT, "marketing_print", "instagram_posts", "bulk_schedule_metricool.csv")

START = int(sys.argv[1]) if len(sys.argv) > 1 else 124
END = int(sys.argv[2]) if len(sys.argv) > 2 else 173
TIME = sys.argv[3] if len(sys.argv) > 3 else "08:00"

# Metricool template columns. TRUE only for Facebook + Instagram.
HEADERS = [
    "Text", "Date", "Time", "Draft",
    "Facebook", "Instagram", "Twitter", "LinkedIn", "Pinterest",
    "TikTok", "YouTube", "GBP", "Threads", "Bluesky",
    "Picture Url 1", "First Comment Text",
]


def date_for(day):
    return EPOCH + datetime.timedelta(days=day - 1)


if __name__ == "__main__":
    players = load_players()
    rows = sorted(
        ((pid, day, img) for (pid, day, _arc, img, *rest) in POSTS if START <= day <= END),
        key=lambda r: r[1],
    )

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(HEADERS)
        for pid, day, img in rows:
            p = players[pid]
            w.writerow([
                caption_for(p, day, is_today=True),         # Text
                date_for(day).strftime("%Y-%m-%d"),         # Date  (YYYY-MM-DD)
                TIME,                                        # Time  (24h)
                "FALSE",                                     # Draft
                "TRUE", "TRUE",                              # Facebook, Instagram
                "FALSE", "FALSE", "FALSE",                   # Twitter, LinkedIn, Pinterest
                "FALSE", "FALSE", "FALSE", "FALSE", "FALSE",  # TikTok, YouTube, GBP, Threads, Bluesky
                f"{SOCIAL_BASE}/{img}",                      # Picture Url 1
                hashtags_for(p),                             # First Comment Text
            ])

    print(f"wrote {os.path.relpath(OUT, ROOT)}  ({len(rows)} posts, day {START}-{END}, {TIME} daily)")
    print("Remember: the day<N>_<id>.jpg images must be in docs/social/ and pushed live")
    print("(https://goodtohearthename.co.uk/social/...) BEFORE importing, so Metricool can fetch them.")
