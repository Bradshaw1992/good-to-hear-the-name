#!/usr/bin/env python3
"""Generate 1080x1920 portrait PNG frames for an Instagram Reel.

Each frame is a still — assemble into a Reel inside CapCut (or iMovie) using
the timings printed at the end of the run. Frames match the brand language of
the square IG posts: cream + ink + green, same top bar.

Run: scripts/.venv/bin/python scripts/make_reel_frames.py [player_id]
     (defaults to first config below)
Output: marketing_print/reel_frames/<player_id>/
"""
import os
import sys
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
SILS = os.path.join(DOCS, "silhouettes")
IMGS = os.path.join(DOCS, "images")

CREAM = (244, 239, 230)
INK   = (22, 38, 28)
GREEN = (15, 122, 62)
MUTED = (110, 120, 115)

W, H = 1080, 1920
PAD = 70

# IG Reels safe band — researched June 2026, cross-checked across multiple sources.
# Reels playback overlays:
#   top ~250px (status bar + IG nav + username/audio pill)
#   bottom ~350px (caption up to 4 lines, audio attribution, follow CTA)
#   right ~210px (like/comment/share/save/profile action column)
# Profile grid thumb crops centred 3:4 (keeps y=240..1680) and 1:1 (keeps y=420..1500).
# Everything critical must sit inside the rectangle below to survive all surfaces.
SAFE_LEFT   = 90
SAFE_TOP    = 500           # content (silhouette, hooks) starts here
SAFE_RIGHT  = 870
SAFE_BOTTOM = 1450          # content ends here (well above the 1570 caption floor)
BRAND_BAR_Y = 430           # brand bar sits above content but inside grid crop band

# ----- per-player reel configs -----
CONFIGS = {
    "diego_forlan": {
        "day": 42,
        "hook_top": "PREMIER LEAGUE FLOP.",
        "hook_bottom": "WORLD CUP LEGEND.",
        "tom_opener": "World cup icon who got his big move after a breakout world cup.",
    },
    "joe_cole": {
        "day": 50,
        "hook_top": "DIPPING VOLLEY.",
        "hook_bottom": "ENGLAND HERO.",
        "tom_opener": "Scorer of one of today's World Cup team's great goals.",
    },
    "maicon": {
        "day": 51,
        "hook_top": "INTER TREBLE WINNER.",
        "hook_bottom": "SKINNED BY A TEENAGER.",
        "tom_opener": "Today's player was famously skinned by a teenager.",
    },
    "serge_aurier": {
        "day": 52,
        "hook_top": "BANNED BY HIS OWN CLUB.",
        "hook_bottom": "PSG TO FOREST.",
        "tom_opener": "Today's player got banned by his own club for what he said about his manager on a live video stream.",
    },
    "youri_djorkaeff": {
        "day": 53,
        "hook_top": "WORLD CUP AND EUROS WINNER.",
        "hook_bottom": "BOLTON CULT HERO.",
        "tom_opener": "Today's player is a cult hero in the Premier League.",
    },
    "mario_gotze": {
        "day": 25,
        "hook_top": "BAYERN MUNICH SUB.",
        "hook_bottom": "WORLD CUP WINNER.",
        "tom_opener": "A world cup winner is today's player. How many clues will it take you to guess him?",
    },
    "el_hadji_diouf": {
        "day": 43,
        "hook_top": "WORLD CUP BREAKOUT.",
        "hook_bottom": "PREMIER LEAGUE FLOP.",
        "tom_opener": "World cup icon who got his big move after a breakout world cup.",
    },
    "victor_moses": {
        "day": 29,
        "hook_top": "FIVE LOAN SPELLS.",
        "hook_bottom": "PREMIER LEAGUE CHAMPION.",
        "tom_opener": "A real test today for those with elite ball knowledge. How many clues will it take?",
    },
    "edin_dzeko": {
        "day": 39,
        "hook_top": "BUNDESLIGA TOP SCORER.",
        "hook_bottom": "PREMIER LEAGUE CHAMPION.",
        "tom_opener": "How good is your football knowledge? Five clues to guess this player.",
    },
    "james_rodriguez": {
        "day": 44,
        "hook_top": "WORLD CUP GOLDEN BOOT.",
        "hook_bottom": "REAL MADRID NUMBER 10.",
        "tom_opener": "Scorer of one of the World Cup's great goals.",
    },
    "pavel_nedved": {
        "day": 45,
        "hook_top": "ONE WORLD CUP.",
        "hook_bottom": "LOST A EUROS FINAL.",
        "tom_opener": "Today is a tough one. One World Cup, lost a Euros final. Who is this football legend?",
    },
    "tim_howard": {
        "day": 46,
        "hook_top": "16 SAVES IN ONE GAME.",
        "hook_bottom": "WORLD CUP RECORD HOLDER.",
        "tom_opener": "A World Cup performance so good it changed a Wikipedia page.",
    },
    "wout_weghorst": {
        "day": 47,
        "hook_top": "BOOKED BEFORE HE PLAYED.",
        "hook_bottom": "SCORED TWICE OFF THE BENCH.",
        "tom_opener": "Today's player was booked at a World Cup before he even came on. Then he scored twice.",
    },
    "keisuke_honda": {
        "day": 48,
        "hook_top": "THREE WORLD CUPS.",
        "hook_bottom": "RUSSIAN LEAGUE CHAMPION.",
        "tom_opener": "Three World Cups, four goals, and a Russian league title in between.",
    },
    "maxi_rodriguez": {
        "day": 49,
        "hook_top": "GOAL OF THE TOURNAMENT.",
        "hook_bottom": "WORLD CUP RUNNER-UP.",
        "tom_opener": "Today's player scored one of the greatest World Cup goals, against a 2026 host nation.",
    },
    "chris_wood": {
        "day": 54,
        "hook_top": "AT THIS WORLD CUP.",
        "hook_bottom": "UNBEATEN AT THE LAST ONE.",
        "tom_opener": "Today's player is at this World Cup. The last one he played in, his country didn't lose a single game.",
    },
    "mascherano": {
        "day": 55,
        "hook_top": "WON EVERYTHING.",
        "hook_bottom": "LOST THE BIG ONE.",
        "tom_opener": "Today's player won everything in club football and lost the biggest game of his country's career in extra time.",
    },
    "sneijder": {
        "day": 56,
        "hook_top": "BALLON D'OR RUNNER-UP.",
        "hook_bottom": "TREBLE WINNER.",
        "tom_opener": "Today's player came second in the Ballon d'Or in the year he won the treble and lost a World Cup final.",
    },
    "griezmann": {
        "day": 57,
        "hook_top": "REJECTED BY EVERY ACADEMY.",
        "hook_bottom": "WORLD CUP WINNER.",
        "tom_opener": "Today's player was rejected by every academy as a teenager. Came back to win the World Cup.",
    },
    "ashley_young": {
        "day": 58,
        "hook_top": "MOCKED FOR DIVING.",
        "hook_bottom": "TITLES IN TWO COUNTRIES.",
        "tom_opener": "Today's player was mocked his whole career for going down too easy. Won league titles in two countries.",
    },
    "morientes": {
        "day": 59,
        "hook_top": "REPLACED BY RONALDO.",
        "hook_bottom": "THREE CHAMPIONS LEAGUES.",
        "tom_opener": "Today's player got replaced at his club by Ronaldo. Won three Champions Leagues anyway.",
    },
    "giroud": {
        "day": 60,
        "hook_top": "SCORPION KICK PUSKÁS WINNER.",
        "hook_bottom": "RECORD INTERNATIONAL SCORER.",
        "tom_opener": "Today's player scored the goal of the year with a scorpion kick on New Year's Day.",
    },
    "asamoah_gyan": {
        "day": 61,
        "hook_top": "120TH MINUTE PENALTY.",
        "hook_bottom": "HIT THE BAR.",
        "tom_opener": "Today's player took a penalty in the last minute of a World Cup quarter-final. It hit the bar.",
    },
}

PLAYER_ID = sys.argv[1] if len(sys.argv) > 1 else "diego_forlan"
if PLAYER_ID not in CONFIGS:
    raise SystemExit(f"no reel config for {PLAYER_ID}. add it to CONFIGS.")
cfg = CONFIGS[PLAYER_ID]
DAY = cfg["day"]
HOOK_TOP = cfg["hook_top"]
HOOK_BOTTOM = cfg["hook_bottom"]
TOM_OPENER = cfg.get("tom_opener", "")
URL_TEXT = f"goodtohearthename.co.uk?day={DAY}"

OUT = os.path.join(ROOT, "marketing_print", "reel_frames", PLAYER_ID)
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
    draw.text((W // 2 - w // 2, y), text, fill=color, font=fnt)


def fit_font(text, max_size, max_width, draw, bold=True):
    """Return the largest font (up to max_size) where text fits within max_width."""
    for size in range(max_size, 28, -2):
        f = font(size, bold=bold)
        bb = draw.textbbox((0, 0), text, font=f)
        if bb[2] - bb[0] <= max_width:
            return f
    return font(28, bold=bold)


def top_bar(canvas, draw):
    # Single-line centred brand strap — narrower than W to stay inside the right action column.
    f_top = font(28, bold=True)
    parts = [("FIVE CLUES.  FIVE GUESSES.", GREEN),
             ("   |   ", MUTED),
             ("GOOD TO HEAR THE NAME", INK)]
    # measure total width
    total = 0
    sizes = []
    for text, _ in parts:
        bb = draw.textbbox((0, 0), text, font=f_top)
        sizes.append(bb[2] - bb[0])
        total += bb[2] - bb[0]
    x = W // 2 - total // 2
    for (text, color), w in zip(parts, sizes):
        draw.text((x, BRAND_BAR_Y), text, fill=color, font=f_top)
        x += w


def blurred_fill(canvas, path, dim_factor=1.0):
    """Cover the entire canvas with a heavily blurred copy of the source.
    Optionally darkens with dim_factor < 1.0 (e.g. 0.45 for cold-open)."""
    img = Image.open(path).convert("RGB")
    iw, ih = img.size
    # cover (scale to fill, may crop)
    scale = max(W / iw, H / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    img = img.filter(ImageFilter.GaussianBlur(radius=40))
    if dim_factor < 1.0:
        img = img.point(lambda p: int(p * dim_factor))
    canvas.paste(img, ((W - nw) // 2, (H - nh) // 2))


def paste_silhouette(canvas, path, top, bottom):
    """Crisp silhouette pasted into a band, contained inside the horizontal safe zone."""
    sil = Image.open(path).convert("RGB")
    max_h = bottom - top
    max_w = SAFE_RIGHT - SAFE_LEFT
    sw, sh = sil.size
    scale = min(max_w / sw, max_h / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    sil = sil.resize((nw, nh), Image.LANCZOS)
    canvas.paste(sil, ((W - nw) // 2, top + (max_h - nh) // 2))


def paste_photo(canvas, path, top, bottom):
    img = Image.open(path).convert("RGB")
    max_h = bottom - top
    max_w = W - PAD * 2
    iw, ih = img.size
    scale = min(max_w / iw, max_h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    canvas.paste(img, ((W - nw) // 2, top + (max_h - nh) // 2))


# ---------- frame builders ----------

def frame_cold_open(out_name):
    """0.0 – 0.4s. Spoiler-flash. Dark blurred silhouette + giant hook text."""
    c = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(c)
    blurred_fill(c, os.path.join(SILS, f"{PLAYER_ID}.jpg"), dim_factor=0.35)
    # giant hook text, centered vertically
    f_hook = font(110, bold=True)
    lines = COLD_OPEN.split("\n")
    line_h = 130
    total_h = len(lines) * line_h
    y = H // 2 - total_h // 2
    for line in lines:
        center_text(d, line, f_hook, y, color=CREAM)
        y += line_h
    c.save(os.path.join(OUT, out_name), "PNG")
    print("wrote", out_name)


def frame_brand_tom(out_name):
    """Tom's Version cover. Caption opener as the hook, silhouette below.
    Editorial layout — full sentence wraps above the silhouette, no split contrast."""
    if not TOM_OPENER:
        return  # nothing to render for players without an opener configured
    c = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(c)
    top_bar(c, d)

    sil_path = os.path.join(SILS, f"{PLAYER_ID}.jpg")
    safe_w = SAFE_RIGHT - SAFE_LEFT

    # Caption opener text — auto-pick font size so the WHOLE sentence fits in
    # at most 4 lines, leaving the silhouette room below.
    chosen = None
    for size in range(56, 32, -2):
        f = font(size, bold=True)
        lines = wrap(TOM_OPENER, f, safe_w, d)
        if len(lines) <= 4:
            chosen = (f, lines, size)
            break
    if chosen is None:
        f = font(34, bold=True)
        chosen = (f, wrap(TOM_OPENER, f, safe_w, d)[:4], 34)
    f_text, lines, size = chosen
    line_h = int(size * 1.25)

    # text block sits in the upper portion of the safe band
    text_top = SAFE_TOP + 20
    cy = text_top
    for line in lines:
        center_text(d, line, f_text, cy, color=INK)
        cy += line_h

    # silhouette fills the rest of the safe band
    sil_top = cy + 30
    sil_bottom = SAFE_BOTTOM - 110
    paste_silhouette(c, sil_path, top=sil_top, bottom=sil_bottom)

    # bottom marker
    f_who = font(40, bold=True)
    center_text(d, "WHO IS IT?", f_who, SAFE_BOTTOM - 90, color=GREEN)
    f_day = font(28, bold=True)
    center_text(d, f"DAY {DAY}  ·  FIVE CLUES.  FIVE GUESSES.", f_day,
                SAFE_BOTTOM - 40, color=MUTED)

    c.save(os.path.join(OUT, out_name), "PNG")
    print("wrote", out_name)


def frame_brand(out_name):
    """Cold-scroll hook frame. All critical text sits in the IG safe band."""
    c = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(c)
    top_bar(c, d)

    sil_path = os.path.join(SILS, f"{PLAYER_ID}.jpg")

    # hook lines auto-fit to the safe width so longer phrases don't overflow.
    safe_w = SAFE_RIGHT - SAFE_LEFT
    f_top_hook = fit_font(HOOK_TOP, max_size=74, max_width=safe_w, draw=d)
    f_bot_hook = fit_font(HOOK_BOTTOM, max_size=74, max_width=safe_w, draw=d)

    # top hook line
    center_text(d, HOOK_TOP, f_top_hook, SAFE_TOP + 20, color=INK)

    # silhouette in the middle band
    paste_silhouette(c, sil_path, top=SAFE_TOP + 130, bottom=SAFE_BOTTOM - 180)

    # bottom hook line
    center_text(d, HOOK_BOTTOM, f_bot_hook, SAFE_BOTTOM - 150, color=GREEN)

    # day stamp just above the safe-bottom floor
    f_sub = font(30, bold=True)
    center_text(d, f"DAY {DAY}  ·  WHO IS IT?", f_sub,
                SAFE_BOTTOM - 50, color=MUTED)
    c.save(os.path.join(OUT, out_name), "PNG")
    print("wrote", out_name)


def frame_clue(idx, clue_text, out_name):
    """Clean cream bg, silhouette band, clue text. Sits entirely in the safe band."""
    c = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(c)
    sil_path = os.path.join(SILS, f"{PLAYER_ID}.jpg")

    top_bar(c, d)

    # 'CLUE N OF 5' label
    f_label = font(38, bold=True)
    center_text(d, f"CLUE {idx} OF 5", f_label, SAFE_TOP + 10, color=GREEN)

    # silhouette in the upper portion of the safe band
    paste_silhouette(c, sil_path, top=SAFE_TOP + 70, bottom=SAFE_TOP + 520)

    # clue text — sits in the lower portion, max width = safe width
    safe_w = SAFE_RIGHT - SAFE_LEFT
    f_clue = font(46)
    clue_lines = wrap(f"“{clue_text}”", f_clue, safe_w, d)[:5]
    line_h = 60
    block_h = len(clue_lines) * line_h
    bottom_band_top = SAFE_TOP + 580
    bottom_band_bot = SAFE_BOTTOM - 80
    cy = bottom_band_top + ((bottom_band_bot - bottom_band_top - block_h) // 2)
    for line in clue_lines:
        center_text(d, line, f_clue, cy, color=INK)
        cy += line_h

    # day strip just above the safe-bottom floor
    f_day_small = font(30, bold=True)
    center_text(d, f"DAY {DAY}  ·  FROM THE ARCHIVE", f_day_small,
                SAFE_BOTTOM - 50, color=MUTED)

    c.save(os.path.join(OUT, out_name), "PNG")
    print("wrote", out_name)


def frame_endcard(out_name):
    """No-reveal end card. All content inside the verified IG safe band."""
    c = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(c)
    sil_path = os.path.join(SILS, f"{PLAYER_ID}.jpg")

    top_bar(c, d)

    # silhouette occupies the upper portion of the safe band
    paste_silhouette(c, sil_path, top=SAFE_TOP, bottom=SAFE_TOP + 420)

    # tier 1: hook + day-specific URL
    base_y = SAFE_TOP + 470
    f_hook = font(54, bold=True)
    center_text(d, "THINK YOU'VE GOT IT?", f_hook, base_y, color=INK)

    f_label = font(32)
    center_text(d, f"Play Day {DAY}:", f_label, base_y + 80, color=MUTED)

    f_url = font(38, bold=True)
    center_text(d, URL_TEXT, f_url, base_y + 130, color=GREEN)

    # divider
    div_y = base_y + 210
    d.rectangle([(W // 2 - 80, div_y), (W // 2 + 80, div_y + 4)], fill=MUTED)

    # tier 2: archive funnel — last item lands no lower than SAFE_BOTTOM - 60
    f_more = font(36, bold=True)
    center_text(d, "Plus 40+ more days to play.", f_more, div_y + 45, color=INK)

    f_more_sub = font(30)
    center_text(d, "A new one every day at:", f_more_sub, div_y + 100, color=MUTED)

    f_home = font(40, bold=True)
    center_text(d, "goodtohearthename.co.uk", f_home, div_y + 150, color=GREEN)

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

    frame_brand("01_brand.png")
    frame_brand_tom("01_brand_tom.png")
    for i, clue in enumerate(clues, start=1):
        frame_clue(i, clue, f"0{1+i}_clue{i}.png")
    frame_endcard("07_endcard.png")

    # write a timing manifest
    manifest = [
        f"# Reel storyboard — {player['name']} (Day {DAY} archive, no-reveal CTA)",
        "Total runtime: ~26.5 seconds.",
        "Aspect: 1080x1920 portrait. Audio: low stadium hum bed, soft transition cue under end card.",
        "",
        "| t (s)        | Frame             | Duration |",
        "|--------------|-------------------|----------|",
        "| 0.0 – 1.0    | 01_brand.png      | 1.0s     |",
        "| 1.0 – 4.5    | 02_clue1.png      | 3.5s     |",
        "| 4.5 – 8.0    | 03_clue2.png      | 3.5s     |",
        "| 8.0 – 11.5   | 04_clue3.png      | 3.5s     |",
        "| 11.5 – 16.0  | 05_clue4.png      | 4.5s     |",
        "| 16.0 – 20.5  | 06_clue5.png      | 4.5s     |",
        "| 20.5 – 27.0  | 07_endcard.png    | 6.5s     |",
        "",
        "Transitions: quick fade (0.2s) between clue frames. Slow fade (0.6s) between clue 5 and end card.",
        "",
        "Caption: \"Day 42 from the archive. Think you've got it? Five clues. Five guesses. Play it cold at the link.\"",
        "Hashtags: see captions.md from the daily IG batch.",
    ]
    manifest_path = os.path.join(OUT, "STORYBOARD.md")
    with open(manifest_path, "w") as f:
        f.write("\n".join(manifest))
    print(f"\nwrote {os.path.relpath(manifest_path, ROOT)}")
    print(f"\nDone. Frames + storyboard in {os.path.relpath(OUT, ROOT)}/")
