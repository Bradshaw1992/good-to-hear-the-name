#!/usr/bin/env python3
"""Square 1080x1080 Reel frames for Reddit (a 9:16 portrait shows as a tiny strip
on Reddit's desktop player). Fills the frame; works on desktop + mobile Reddit.

Reuses the per-player config (day, hooks) from make_reel_frames.py and the clues
from content.json. End card is Reddit-appropriate: guess below, answer/link in post.

Add "hard" as a second arg for a tougher variant: the cover frame gives NOTHING
away — no hooks, just the silhouette + "WHO IS IT?" — so the first thing a
scroller sees is a pure mystery. Writes to <player_id>_square_hard/.

Run:   scripts/.venv/bin/python scripts/make_reel_square.py <player_id> [hard]
Then:  scripts/.venv/bin/python scripts/render_reel.py <player_id>_square[_hard]
Output: marketing_print/reel_frames/<player_id>_square[_hard]/
"""
import os, re, json, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SILS = os.path.join(ROOT, "docs", "silhouettes")

CREAM = (244, 239, 230); INK = (22, 38, 28); GREEN = (15, 122, 62); MUTED = (110, 120, 115)
S = 1080; PAD = 70
URL = "goodtohearthename.co.uk"   # baked into the video so no group link-rule can strip it

PLAYER_ID = sys.argv[1] if len(sys.argv) > 1 else "morientes"
HARD = len(sys.argv) > 2 and sys.argv[2].lower() == "hard"
# Hard mode: crop the silhouette to a top fraction (head / head+shoulders) on the
# cover and the opening clue(s), so a distinctive pose isn't given away early.
#   crop  = fraction of the silhouette height kept (smaller = shows less)
#   clues = how many opening clue frames stay cropped (cover is always cropped)
HARD_CROP = 0.5
HARD_CROP_CLUES = 1
# Per-player tuning for players who need more (or less) hidden.
HARD_OVERRIDES = {
    "lucio": {"crop": 0.4, "clues": 2},   # generic standing pose: hide harder + longer
}
if PLAYER_ID in HARD_OVERRIDES:
    HARD_CROP = HARD_OVERRIDES[PLAYER_ID].get("crop", HARD_CROP)
    HARD_CROP_CLUES = HARD_OVERRIDES[PLAYER_ID].get("clues", HARD_CROP_CLUES)

# ---- read config from make_reel_frames.py (no import: avoids its module-level side effects)
src = open(os.path.join(ROOT, "scripts/make_reel_frames.py")).read()
m = re.search(r'"%s":\s*\{([^}]*)\}' % re.escape(PLAYER_ID), src)
if not m:
    raise SystemExit(f"no reel config for {PLAYER_ID}")
blk = m.group(1)
def field(name):
    mm = re.search(r'"%s":\s*"((?:[^"\\]|\\.)*)"' % name, blk)
    return mm.group(1).encode().decode("unicode_escape") if mm else ""
DAY = int(re.search(r'"day":\s*(\d+)', blk).group(1))
HOOK_TOP = field("hook_top"); HOOK_BOTTOM = field("hook_bottom")

content = json.load(open(os.path.join(ROOT, "app/src/main/assets/content.json")))
CLUES = next(p["clues"] for p in content["footballers"] if p["id"] == PLAYER_ID)

OUT = os.path.join(ROOT, "marketing_print", "reel_frames",
                    PLAYER_ID + ("_square_hard" if HARD else "_square"))
os.makedirs(OUT, exist_ok=True)


def font(size, bold=False):
    for c in ["/System/Library/Fonts/Helvetica.ttc",
              "/System/Library/Fonts/Supplemental/Arial Bold.ttf"]:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size, index=1 if bold else 0)
            except Exception:
                return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def center(d, text, f, y, color=INK):
    bb = d.textbbox((0, 0), text, font=f)
    d.text((S // 2 - (bb[2] - bb[0]) // 2, y), text, fill=color, font=f)


def fit_font(text, maxsize, maxw, d, bold=True):
    for s in range(maxsize, 26, -2):
        f = font(s, bold=bold)
        bb = d.textbbox((0, 0), text, font=f)
        if bb[2] - bb[0] <= maxw:
            return f
    return font(26, bold=bold)


def wrap(text, f, maxw, d):
    words, lines, cur = text.split(), [], []
    for w in words:
        if d.textbbox((0, 0), " ".join(cur + [w]), font=f)[2] <= maxw:
            cur.append(w)
        else:
            lines.append(" ".join(cur)); cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def top_bar(d):
    f = font(24, bold=True)
    d.text((PAD, PAD - 8), "FIVE CLUES.  FIVE GUESSES.", fill=GREEN, font=f)
    brand = "GOOD TO HEAR THE NAME"
    bb = d.textbbox((0, 0), brand, font=f)
    d.text((S - PAD - (bb[2] - bb[0]), PAD - 8), brand, fill=INK, font=f)


def paste_sil(c, top, bottom, crop_frac=None):
    """crop_frac: keep only the top fraction of the silhouette (head + shoulders)
    so a distinctive full-body pose isn't revealed on the opening frames."""
    sil = Image.open(os.path.join(SILS, f"{PLAYER_ID}.jpg")).convert("RGB")
    if crop_frac:
        sw0, sh0 = sil.size
        sil = sil.crop((0, 0, sw0, int(sh0 * crop_frac)))
    max_h, max_w = bottom - top, S - PAD * 2
    sw, sh = sil.size
    sc = min(max_w / sw, max_h / sh)
    nw, nh = int(sw * sc), int(sh * sc)
    sil = sil.resize((nw, nh), Image.LANCZOS)
    c.paste(sil, ((S - nw) // 2, top + (max_h - nh) // 2))


SAFE_W = S - PAD * 2


def frame_brand(name):
    c = Image.new("RGB", (S, S), CREAM); d = ImageDraw.Draw(c); top_bar(d)
    center(d, HOOK_TOP, fit_font(HOOK_TOP, 60, SAFE_W, d), 150, INK)
    paste_sil(c, 235, 730)
    center(d, HOOK_BOTTOM, fit_font(HOOK_BOTTOM, 60, SAFE_W, d), 770, GREEN)
    center(d, f"DAY {DAY}  ·  WHO IS IT?", font(30, bold=True), 880, MUTED)
    c.save(os.path.join(OUT, name)); print("wrote", name)


def frame_brand_hard(name):
    """Explainer cover for cold audiences (first-time Facebook pages): says how the
    game works and where to play, while keeping the player anonymous (cropped pose)."""
    c = Image.new("RGB", (S, S), CREAM); d = ImageDraw.Draw(c); top_bar(d)
    center(d, "GUESS THE FOOTBALLER",
           fit_font("GUESS THE FOOTBALLER", 66, SAFE_W, d), 135, GREEN)
    paste_sil(c, 235, 590, crop_frac=HARD_CROP)
    center(d, "5 CLUES.  5 GUESSES.", font(46, bold=True), 640, INK)
    center(d, "A new mystery player every day.", font(32), 712, MUTED)
    d.rectangle([(S // 2 - 80, 785), (S // 2 + 80, 789)], fill=MUTED)
    center(d, "PLAY FREE AT", font(28, bold=True), 815, MUTED)
    center(d, URL, fit_font(URL, 62, SAFE_W, d), 855, INK)
    c.save(os.path.join(OUT, name)); print("wrote", name)


def frame_clue(idx, clue, name, crop_frac=None):
    c = Image.new("RGB", (S, S), CREAM); d = ImageDraw.Draw(c); top_bar(d)
    center(d, f"CLUE {idx} OF 5", font(40, bold=True), 140, GREEN)
    paste_sil(c, 205, 630, crop_frac=crop_frac)
    f_clue = font(40)
    lines = wrap(f"“{clue}”", f_clue, SAFE_W, d)[:4]
    line_h = 54; block = len(lines) * line_h
    cy = 680 + max(0, (300 - block) // 2)
    for ln in lines:
        center(d, ln, f_clue, cy, INK); cy += line_h
    center(d, f"DAY {DAY}  ·  {URL}", font(28, bold=True), 1005, MUTED)
    c.save(os.path.join(OUT, name)); print("wrote", name)


def frame_endcard(name):
    c = Image.new("RGB", (S, S), CREAM); d = ImageDraw.Draw(c); top_bar(d)
    paste_sil(c, 150, 545)
    base = 590
    center(d, "THINK YOU KNOW HIM?", font(46, bold=True), base, INK)
    center(d, "PLAY TODAY'S PLAYER FREE",
           fit_font("PLAY TODAY'S PLAYER FREE", 52, SAFE_W, d), base + 62, GREEN)
    d.rectangle([(S // 2 - 80, base + 150), (S // 2 + 80, base + 154)], fill=MUTED)
    center(d, URL, fit_font(URL, 64, SAFE_W, d), base + 180, INK)
    center(d, "A new one every day.", font(30), base + 262, MUTED)
    c.save(os.path.join(OUT, name)); print("wrote", name)


if __name__ == "__main__":
    if HARD:
        frame_brand_hard("01_brand.png")
    else:
        frame_brand("01_brand.png")
    for i, clue in enumerate(CLUES, 1):
        # In hard mode, keep the opening clue(s) anonymous too (crop the pose).
        crop = HARD_CROP if (HARD and i <= HARD_CROP_CLUES) else None
        frame_clue(i, clue, f"0{1+i}_clue{i}.png", crop_frac=crop)
    frame_endcard("07_endcard.png")
    label = "hard " if HARD else ""
    print(f"\nDone. Square {label}frames in {os.path.relpath(OUT, ROOT)}/")
