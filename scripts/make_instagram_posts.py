#!/usr/bin/env python3
"""Generate 1080x1080 Instagram post images: silhouette + first clue + day reveal.

Daily-style (today's player): silhouette + clue + "Day X." + "WHO IS IT?"
Archive-style (past day reveal): silhouette + clue + "Day X." + player name reveal.

Run: scripts/.venv/bin/python scripts/make_instagram_posts.py
Output: marketing_print/instagram_posts/
"""
import os
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
SILS = os.path.join(DOCS, "silhouettes")
OUT = os.path.join(ROOT, "marketing_print", "instagram_posts")
os.makedirs(OUT, exist_ok=True)

CREAM = (244, 239, 230)
INK   = (22, 38, 28)
GREEN = (15, 122, 62)
MUTED = (110, 120, 115)

SIZE = 1080
PADDING = 60


def load_players():
    src = open(os.path.join(DOCS, "players.js")).read()
    src = src[src.index("[") : src.rstrip().rstrip(";").rindex("]") + 1]
    return {p["id"]: p for p in json.loads(src)}


def font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size, index=1 if bold else 0)
            except Exception:
                return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def wrap(text, fnt, max_w, draw):
    words = text.split()
    lines, cur = [], []
    for w in words:
        test = " ".join(cur + [w])
        bb = draw.textbbox((0, 0), test, font=fnt)
        if bb[2] - bb[0] <= max_w:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
                cur = [w]
            else:
                lines.append(w)
    if cur:
        lines.append(" ".join(cur))
    return lines


def center_text(draw, text, font_, y, color=INK):
    bb = draw.textbbox((0, 0), text, font=font_)
    w = bb[2] - bb[0]
    draw.text((SIZE // 2 - w // 2, y), text, fill=color, font=font_)
    return bb[3] - bb[1]


def build_post(player, day, is_archive, out_name):
    canvas = Image.new("RGB", (SIZE, SIZE), CREAM)
    draw = ImageDraw.Draw(canvas)

    # --- TOP BAR ---
    f_top = font(22, bold=True)
    draw.text((PADDING, PADDING), "FIVE CLUES.  FIVE GUESSES.",
              fill=GREEN, font=f_top)
    brand = "GOOD TO HEAR THE NAME"
    bb = draw.textbbox((0, 0), brand, font=f_top)
    draw.text((SIZE - PADDING - (bb[2] - bb[0]), PADDING),
              brand, fill=INK, font=f_top)

    # --- SILHOUETTE ---
    sil_path = os.path.join(SILS, f"{player['id']}.jpg")
    sil = Image.open(sil_path).convert("RGB")
    sil_top = 130
    sil_bottom = 720
    max_h = sil_bottom - sil_top
    max_w = SIZE - PADDING * 2
    sw, sh = sil.size
    scale = min(max_w / sw, max_h / sh)
    new_w, new_h = int(sw * scale), int(sh * scale)
    sil = sil.resize((new_w, new_h), Image.LANCZOS)
    canvas.paste(sil, ((SIZE - new_w) // 2,
                       sil_top + (max_h - new_h) // 2))

    # --- FIRST CLUE (italic-feel, centered) ---
    f_clue = font(28)
    clue_max_w = SIZE - PADDING * 4
    clue_lines = wrap(f"“{player['clues'][0]}”",
                      f_clue, clue_max_w, draw)
    cy = 750
    for line in clue_lines[:3]:
        center_text(draw, line, f_clue, cy, color=INK)
        cy += 38

    # --- DAY + WHO IS IT? hook (no answer revealed, ever) ---
    bottom_y = SIZE - PADDING - 120
    f_day = font(36, bold=True)
    center_text(draw, f"Day {day}.", f_day, bottom_y, color=INK)
    f_who = font(54, bold=True)
    center_text(draw, "WHO IS IT?", f_who, bottom_y + 50, color=GREEN)

    path = os.path.join(OUT, out_name)
    canvas.save(path, "JPEG", quality=92)
    print("wrote", os.path.relpath(path, ROOT))


# (player_id, day_number, is_archive_reveal, output_filename)
POSTS = [
    ("rafael_marquez", 38, False, "01_today_marquez_day38_v2.jpg"),
    ("batistuta",      10, True,  "02_archive_batistuta_day10_v2.jpg"),
    ("mario_gotze",    25, True,  "03_archive_gotze_day25_v2.jpg"),
    ("abidal",         26, True,  "04_archive_abidal_day26_v2.jpg"),
    ("falcao",         33, True,  "05_archive_falcao_day33_v2.jpg"),
]


HOME_URL = "https://goodtohearthename.co.uk"

# Niche hashtag blocks per player. Edit / extend as the roster grows.
NICHE_TAGS = {
    "rafael_marquez": "#worldcup2026 #mexico #fcbarcelona #worldcuplegends",
    "batistuta":      "#batigol #argentina #fiorentina #serieA",
    "mario_gotze":    "#worldcup2026 #germany #borussiadortmund #worldcuplegends",
    "abidal":         "#fcbarcelona #championsleague #francefootball #footballnostalgia",
    "falcao":         "#atleticomadrid #colombia #europaleague #2010sfootball",
}

CORE_TAGS = (
    "#footballquiz #footballnostalgia #cultheroes #retrofootball "
    "#footballcommunity #footballcliches #thefootballramble"
)


def caption_for(player, day, is_today):
    # ?day=N pins the day on the site without revealing the player id in the URL
    pinned = f"{HOME_URL}?day={day}"
    if is_today:
        return f"""Day {day}. Today's puzzle.

Five clues. Five guesses. Most people need three.

Play it now: {pinned}

Made by a fan, for the obsessives."""
    return f"""Day {day} from the archive.

Five clues. Five guesses. Most people need three.

Play this exact puzzle: {pinned}

Today's puzzle in the link in bio. Made by a fan, for the obsessives."""


def hashtags_for(player):
    niche = NICHE_TAGS.get(player["id"], "")
    return f"{CORE_TAGS} {niche}".strip()


if __name__ == "__main__":
    players = load_players()
    caption_lines = ["# Instagram captions (paste-ready)\n"]
    for pid, day, is_arc, out in POSTS:
        if pid not in players:
            print(f"SKIP {pid}: id not found in players.js")
            continue
        sil_path = os.path.join(SILS, f"{pid}.jpg")
        if not os.path.exists(sil_path):
            print(f"SKIP {pid}: silhouette {sil_path} not found")
            continue
        build_post(players[pid], day, is_arc, out)
        # Append caption + hashtag block to the captions file
        caption_lines.append(f"## {out}\n")
        caption_lines.append("**Caption:**\n```")
        caption_lines.append(caption_for(players[pid], day, is_today=not is_arc))
        caption_lines.append("```\n")
        caption_lines.append("**First comment (hashtags):**\n```")
        caption_lines.append(hashtags_for(players[pid]))
        caption_lines.append("```\n")
        caption_lines.append("---\n")
    captions_path = os.path.join(OUT, "captions.md")
    with open(captions_path, "w") as f:
        f.write("\n".join(caption_lines))
    print(f"\nwrote {os.path.relpath(captions_path, ROOT)}")
    print("\nDone. Image files + paste-ready captions in "
          "marketing_print/instagram_posts/")
