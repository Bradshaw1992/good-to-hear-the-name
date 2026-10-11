#!/usr/bin/env python3
"""Flatten the upcoming IG/FB photo posts into one copy-paste scheduling sheet.

For every POSTS entry from TODAY_DAY onward: date, image filename, caption, and the
first-comment hashtags — in date order, so scheduling in Business Suite is pure copy-paste
top to bottom with no cross-referencing.

Run: scripts/.venv/bin/python scripts/make_posting_schedule.py [START_DAY] [END_DAY]
     (defaults: START = TODAY_DAY, END = everything after it)
Output: marketing_print/instagram_posts/posting_schedule.txt
"""
import os
import sys
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from make_instagram_posts import (  # noqa: E402
    POSTS, TODAY_DAY, load_players, caption_for, hashtags_for,
)

EPOCH = datetime.date(2026, 5, 5)  # Day 1
OUT = os.path.join(ROOT, "marketing_print", "instagram_posts", "posting_schedule.txt")

START = int(sys.argv[1]) if len(sys.argv) > 1 else TODAY_DAY
END = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 9


def date_for(day):
    return EPOCH + datetime.timedelta(days=day - 1)


if __name__ == "__main__":
    players = load_players()
    upcoming = sorted((e for e in POSTS if START <= e[1] <= END), key=lambda e: e[1])

    lines = [
        "GOOD TO HEAR THE NAME — IG / FACEBOOK PHOTO POST SCHEDULE",
        "",
        "In date order. For each: attach the IMAGE, paste the CAPTION, then post the",
        "HASHTAGS as the first comment. The hook line is already on the image itself.",
        "",
    ]
    for pid, day, _is_arc, img in [(e[0], e[1], e[2], e[3]) for e in upcoming]:
        d = date_for(day)
        p = players[pid]
        bar = "=" * 60
        lines += [
            bar,
            f"{d.strftime('%a %d %b')}  —  DAY {day}  —  {p['name']}",
            bar,
            f"IMAGE:  marketing_print/instagram_posts/{img}",
            "",
            "CAPTION:",
            caption_for(p, day, is_today=day >= TODAY_DAY),
            "",
            "FIRST COMMENT:",
            hashtags_for(p),
            "",
            "",
        ]
    with open(OUT, "w") as f:
        f.write("\n".join(lines))
    print(f"wrote {os.path.relpath(OUT, ROOT)}  ({len(upcoming)} posts, day {upcoming[0][1]}-{upcoming[-1][1]})")
