#!/usr/bin/env python3
"""Generate 1080x1920 portrait PNG frames for an Instagram Story sequence.

Each frame is a still you publish as a separate Story. Native IG stickers
(link, quiz, slider) get layered ON TOP at publish time, so each frame leaves
a clear "sticker zone" near the bottom.

Run: scripts/.venv/bin/python scripts/make_story_frames.py
Output: marketing_print/story_frames/<player_id>/
"""
import os
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
SILS = os.path.join(DOCS, "silhouettes")

CREAM = (244, 239, 230)
INK   = (22, 38, 28)
GREEN = (15, 122, 62)
MUTED = (110, 120, 115)

W, H = 1080, 1920
PAD = 70
STICKER_ZONE_TOP = 1500  # reserve bottom ~420px for native IG stickers

# ----- today's story -----
PLAYER_ID = "el_hadji_diouf"
DAY = 43
TEASE_LINE_1 = "The reigning World Cup champions"
TEASE_LINE_2 = "had just lifted the trophy."
TEASE_LINE_3 = "He helped knock them out of the next one."
STAT_HEADLINE = "£10 million."
STAT_BODY = "Liverpool transfer fee in 2002."
STAT_QUESTION = "Premier League goals in his two seasons?"
QUIZ_NOTE = "Add a quiz sticker over this frame: 3 / 8 / 15 / 22"  # correct: 3

OUT = os.path.join(ROOT, "marketing_print", "story_frames", PLAYER_ID)
os.makedirs(OUT, exist_ok=True)


def font(size, bold=False, italic=False):
    candidates_regular = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    candidates_serif = [
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/Times.ttc",
        "/Library/Fonts/Georgia.ttf",
    ]
    pool = candidates_serif if italic else candidates_regular
    for c in pool:
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


def top_bar(canvas, draw, color_left=GREEN, color_right=INK):
    f_top = font(28, bold=True)
    draw.text((PAD, PAD), "FIVE CLUES.  FIVE GUESSES.",
              fill=color_left, font=f_top)
    brand = "GOOD TO HEAR THE NAME"
    bb = draw.textbbox((0, 0), brand, font=f_top)
    draw.text((W - PAD - (bb[2] - bb[0]), PAD),
              brand, fill=color_right, font=f_top)


def paste_silhouette(canvas, path, top, bottom):
    sil = Image.open(path).convert("RGB")
    max_h = bottom - top
    max_w = W - PAD * 2
    sw, sh = sil.size
    scale = min(max_w / sw, max_h / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    sil = sil.resize((nw, nh), Image.LANCZOS)
    canvas.paste(sil, ((W - nw) // 2, top + (max_h - nh) // 2))


def sticker_hint(draw, label):
    """No-op. Sticker placement is documented in STORY_PLAN.md only — the published
    frame must stay clean because IG stickers don't fully cover printed hints."""
    return


# ---------- frame builders ----------

def frame1_intro(out_name):
    """Day-live announcement with silhouette. Bottom space reserved for link sticker."""
    c = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(c)
    top_bar(c, d)

    sil_path = os.path.join(SILS, f"{PLAYER_ID}.jpg")
    paste_silhouette(c, sil_path, top=200, bottom=1000)

    f_day = font(82, bold=True)
    center_text(d, f"Day {DAY} is live.", f_day, 1080, color=INK)

    f_sub = font(44)
    center_text(d, "Five clues. Five guesses.", f_sub, 1190, color=MUTED)
    center_text(d, "Most people need three.", f_sub, 1250, color=MUTED)

    f_who = font(96, bold=True)
    center_text(d, "WHO IS IT?", f_who, 1370, color=GREEN)

    sticker_hint(d, "↓ ADD LINK STICKER  →  goodtohearthename.co.uk?day=43 ↓")
    c.save(os.path.join(OUT, out_name), "PNG")
    print("wrote", out_name)


def frame2_tease(out_name):
    """Black + serif teaser. No silhouette. Pure cinematic mystery."""
    c = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(c)

    f_top = font(28, bold=True)
    center_text(d, "DAY 43.  FIVE CLUES.  FIVE GUESSES.", f_top, PAD, color=GREEN)

    f_tease = font(64, italic=True)
    cy = 700
    for line in (TEASE_LINE_1, TEASE_LINE_2):
        center_text(d, line, f_tease, cy, color=CREAM)
        cy += 95

    # gap, then punchline
    cy += 60
    f_punch = font(64, italic=True)
    lines = wrap(TEASE_LINE_3, f_punch, W - PAD * 4, d)
    for line in lines:
        center_text(d, line, f_punch, cy, color=CREAM)
        cy += 95

    f_who = font(46, bold=True)
    center_text(d, "WHO IS IT?", f_who, 1400, color=GREEN)

    sticker_hint(d, "(no sticker — pure tease)")
    c.save(os.path.join(OUT, out_name), "PNG")
    print("wrote", out_name)


def frame3_stat(out_name):
    """Stat card with reserved zone for native IG quiz sticker."""
    c = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(c)
    top_bar(c, d)

    f_eyebrow = font(34, bold=True)
    center_text(d, "DAY 43  ·  WITHOUT NAMING HIM", f_eyebrow, 200, color=MUTED)

    # big stat
    f_stat = font(180, bold=True)
    center_text(d, STAT_HEADLINE, f_stat, 360, color=GREEN)

    f_stat_body = font(48)
    body_lines = wrap(STAT_BODY, f_stat_body, W - PAD * 2, d)
    cy = 600
    for line in body_lines:
        center_text(d, line, f_stat_body, cy, color=INK)
        cy += 60

    # question that leads into the quiz sticker
    f_q = font(54, bold=True)
    q_lines = wrap(STAT_QUESTION, f_q, W - PAD * 2, d)
    cy = 850
    for line in q_lines:
        center_text(d, line, f_q, cy, color=INK)
        cy += 70

    f_hint = font(32)
    center_text(d, "Take a guess below.", f_hint,
                cy + 30, color=MUTED)

    sticker_hint(d, "↓ ADD QUIZ STICKER  →  3 / 8 / 15 / 22  (answer: 3) ↓")
    c.save(os.path.join(OUT, out_name), "PNG")
    print("wrote", out_name)


def frame4_outro(out_name):
    """Silhouette returns. Final push to play."""
    c = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(c)
    top_bar(c, d)

    sil_path = os.path.join(SILS, f"{PLAYER_ID}.jpg")
    paste_silhouette(c, sil_path, top=200, bottom=1000)

    f_hook = font(74, bold=True)
    center_text(d, "FIVE GUESSES.", f_hook, 1080, color=INK)
    center_text(d, "MOST PEOPLE NEED THREE.", f_hook, 1170, color=INK)

    f_cta = font(48, bold=True)
    center_text(d, "Tap to play Day 43.", f_cta, 1320, color=GREEN)

    f_url = font(38)
    center_text(d, "goodtohearthename.co.uk?day=43", f_url, 1395, color=MUTED)

    sticker_hint(d, "↓ ADD LINK STICKER  →  goodtohearthename.co.uk?day=43 ↓")
    c.save(os.path.join(OUT, out_name), "PNG")
    print("wrote", out_name)


# ---------- driver ----------

if __name__ == "__main__":
    frame1_intro("01_intro.png")
    frame2_tease("02_tease.png")
    frame3_stat("03_stat_quiz.png")
    frame4_outro("04_outro.png")

    manifest = [
        f"# Story sequence — Day {DAY} (Diouf, no name reveal)",
        "Aspect: 1080x1920 portrait. Four frames, posted as separate Story slides.",
        "",
        "| Slide | File           | Sticker to add in IG                                                |",
        "|-------|----------------|---------------------------------------------------------------------|",
        "| 1     | 01_intro.png   | Link sticker → goodtohearthename.co.uk?day=43                       |",
        "| 2     | 02_tease.png   | None — pure cinematic tease                                          |",
        "| 3     | 03_stat_quiz.png | Quiz sticker. Question: \"PL goals in two seasons?\" — options: 3 / 8 / 15 / 22. Correct: 3 |",
        "| 4     | 04_outro.png   | Link sticker → goodtohearthename.co.uk?day=43                       |",
        "",
        "Pace: leave each frame as default 5s on IG. Don't add music — restraint is the brand.",
        "Order matters: 1 → 2 → 3 → 4. Post all four in one batch.",
    ]
    path = os.path.join(OUT, "STORY_PLAN.md")
    with open(path, "w") as f:
        f.write("\n".join(manifest))
    print(f"\nwrote {os.path.relpath(path, ROOT)}")
    print(f"\nDone. Frames + plan in {os.path.relpath(OUT, ROOT)}/")
