#!/usr/bin/env python3
"""Generate 1080x1080 IG carousel slides for an archive player.

Seven-slide format:
  01_cover.png     — silhouette + two-line contrast hook
  02_clue1.png … 06_clue5.png — silhouette + clue text
  07_endcard.png   — CTA: play this day + plus 40+ more days

Run: scripts/.venv/bin/python scripts/make_carousel_slides.py [player_id]
     (defaults to first config below)
Output: marketing_print/carousel_slides/<player_id>/
"""
import os
import sys
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
SILS = os.path.join(DOCS, "silhouettes")

CREAM = (244, 239, 230)
INK   = (22, 38, 28)
GREEN = (15, 122, 62)
MUTED = (110, 120, 115)

SIZE = 1080
PAD = 60

# ----- per-player carousel configs -----
# Edit the hook lines to match each player's career arc.
CONFIGS = {
    "shevchenko": {
        "day": 16,
        "hook_top": "BALLON D'OR WINNER.",
        "hook_bottom": "PREMIER LEAGUE FLOP.",
    },
    "wes_morgan": {
        "day": 1,
        "hook_top": "CHAMPIONSHIP JOURNEYMAN.",
        "hook_bottom": "PREMIER LEAGUE CHAMPION.",
    },
}

PLAYER_ID = sys.argv[1] if len(sys.argv) > 1 else "shevchenko"
if PLAYER_ID not in CONFIGS:
    raise SystemExit(f"no carousel config for {PLAYER_ID}. add it to CONFIGS.")
cfg = CONFIGS[PLAYER_ID]
DAY = cfg["day"]
HOOK_TOP = cfg["hook_top"]
HOOK_BOTTOM = cfg["hook_bottom"]
DAY_URL = f"goodtohearthename.co.uk?day={DAY}"

OUT = os.path.join(ROOT, "marketing_print", "carousel_slides", PLAYER_ID)
os.makedirs(OUT, exist_ok=True)


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


def center_text(draw, text, fnt, y, color=INK):
    bb = draw.textbbox((0, 0), text, font=fnt)
    w = bb[2] - bb[0]
    draw.text((SIZE // 2 - w // 2, y), text, fill=color, font=fnt)


def top_bar(canvas, draw):
    f_top = font(22, bold=True)
    draw.text((PAD, PAD), "FIVE CLUES.  FIVE GUESSES.",
              fill=GREEN, font=f_top)
    brand = "GOOD TO HEAR THE NAME"
    bb = draw.textbbox((0, 0), brand, font=f_top)
    draw.text((SIZE - PAD - (bb[2] - bb[0]), PAD),
              brand, fill=INK, font=f_top)


def paste_silhouette(canvas, path, top, bottom):
    sil = Image.open(path).convert("RGB")
    max_h = bottom - top
    max_w = SIZE - PAD * 2
    sw, sh = sil.size
    scale = min(max_w / sw, max_h / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    sil = sil.resize((nw, nh), Image.LANCZOS)
    canvas.paste(sil, ((SIZE - nw) // 2, top + (max_h - nh) // 2))


# ---------- slide builders ----------

def slide_cover(out_name):
    """Slide 1 — silhouette + two-line contrast hook. The scroll-stopper."""
    c = Image.new("RGB", (SIZE, SIZE), CREAM)
    d = ImageDraw.Draw(c)
    top_bar(c, d)

    sil_path = os.path.join(SILS, f"{PLAYER_ID}.jpg")

    f_hook = font(56, bold=True)
    center_text(d, HOOK_TOP, f_hook, 130, color=INK)

    paste_silhouette(c, sil_path, top=220, bottom=820)

    center_text(d, HOOK_BOTTOM, f_hook, 850, color=GREEN)

    f_sub = font(28, bold=True)
    center_text(d, f"DAY {DAY}  ·  WHO IS IT?", f_sub,
                SIZE - PAD - 36, color=MUTED)
    c.save(os.path.join(OUT, out_name), "PNG")
    print("wrote", out_name)


def slide_clue(idx, clue_text, out_name):
    """Slides 2–6 — silhouette + clue text. Same language as the daily IG card."""
    c = Image.new("RGB", (SIZE, SIZE), CREAM)
    d = ImageDraw.Draw(c)
    top_bar(c, d)

    sil_path = os.path.join(SILS, f"{PLAYER_ID}.jpg")
    paste_silhouette(c, sil_path, top=140, bottom=680)

    # clue label
    f_label = font(26, bold=True)
    center_text(d, f"CLUE {idx} OF 5", f_label, 700, color=GREEN)

    # clue text
    f_clue = font(30)
    clue_lines = wrap(f"“{clue_text}”", f_clue, SIZE - PAD * 4, d)
    cy = 760
    for line in clue_lines[:5]:
        center_text(d, line, f_clue, cy, color=INK)
        cy += 42

    # bottom day strip
    f_day = font(24, bold=True)
    center_text(d, f"DAY {DAY}  ·  WHO IS IT?", f_day,
                SIZE - PAD - 30, color=MUTED)
    c.save(os.path.join(OUT, out_name), "PNG")
    print("wrote", out_name)


def slide_endcard(out_name):
    """Final slide — two-tier CTA. Silhouette stays mysterious; never reveal the name."""
    c = Image.new("RGB", (SIZE, SIZE), CREAM)
    d = ImageDraw.Draw(c)
    top_bar(c, d)

    sil_path = os.path.join(SILS, f"{PLAYER_ID}.jpg")
    paste_silhouette(c, sil_path, top=130, bottom=560)

    # tier 1
    f_hook = font(46, bold=True)
    center_text(d, "THINK YOU'VE GOT IT?", f_hook, 600, color=INK)

    f_label = font(28)
    center_text(d, f"Play Day {DAY}:", f_label, 670, color=MUTED)

    f_url = font(32, bold=True)
    center_text(d, DAY_URL, f_url, 710, color=GREEN)

    # divider
    d.rectangle([(SIZE // 2 - 60, 790), (SIZE // 2 + 60, 793)], fill=MUTED)

    # tier 2
    f_more = font(32, bold=True)
    center_text(d, "Plus 40+ more days to play.", f_more, 830, color=INK)

    f_more_sub = font(26)
    center_text(d, "A new one every day at:", f_more_sub, 880, color=MUTED)

    f_home = font(32, bold=True)
    center_text(d, "goodtohearthename.co.uk", f_home, 920, color=GREEN)

    c.save(os.path.join(OUT, out_name), "PNG")
    print("wrote", out_name)


# ---------- driver ----------

def load_player():
    with open(os.path.join(ROOT, "app/src/main/assets/content.json")) as f:
        d = json.load(f)
    for p in d["footballers"]:
        if p["id"] == PLAYER_ID:
            return p
    raise SystemExit(f"player {PLAYER_ID} not found")


if __name__ == "__main__":
    player = load_player()
    clues = player["clues"]

    slide_cover("01_cover.png")
    for i, clue in enumerate(clues, start=1):
        slide_clue(i, clue, f"0{1+i}_clue{i}.png")
    slide_endcard("07_endcard.png")

    manifest = [
        f"# Carousel — {player['name']} (Day {DAY} archive)",
        "Seven 1080x1080 slides. Post as a single IG feed carousel.",
        "",
        "| Slide | File          | What's on it |",
        "|-------|---------------|--------------|",
        "| 1     | 01_cover.png  | Silhouette + contrast hook (scroll-stopper) |",
        "| 2     | 02_clue1.png  | Clue 1 of 5 |",
        "| 3     | 03_clue2.png  | Clue 2 of 5 |",
        "| 4     | 04_clue3.png  | Clue 3 of 5 |",
        "| 5     | 05_clue4.png  | Clue 4 of 5 |",
        "| 6     | 06_clue5.png  | Clue 5 of 5 |",
        "| 7     | 07_endcard.png| CTA — play this day + plus 40+ more days at homepage |",
        "",
        "## Caption (paste-ready)",
        "",
        f"{HOOK_TOP.rstrip('.').title()} {HOOK_BOTTOM.rstrip('.').lower()}. "
        f"Five clues, five guesses.",
        "",
        f"Day {DAY} from the archive. Most people need three.",
        "",
        f"Swipe for the clues. Play it cold at {DAY_URL} (link in bio). "
        "40+ more days waiting. New one every day.",
        "",
        "Made by a fan, for the obsessives.",
        "",
        "## First comment (hashtags)",
        "",
        "Edit hashtags per player. Core block:",
        "#footballquiz #footballnostalgia #cultheroes #retrofootball "
        "#footballcommunity #thefootballramble",
    ]
    path = os.path.join(OUT, "CAROUSEL_PLAN.md")
    with open(path, "w") as f:
        f.write("\n".join(manifest))
    print(f"\nwrote {os.path.relpath(path, ROOT)}")
    print(f"\nDone. Slides + plan in {os.path.relpath(OUT, ROOT)}/")
