#!/usr/bin/env python3
"""Generate Twitter profile picture (800x800) and banner (1500x500).

Uses the Batistuta silhouette as the brand mark.

Run: scripts/.venv/bin/python scripts/make_twitter_assets.py
Output: marketing_print/twitter_assets/
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
SILS = os.path.join(DOCS, "silhouettes")
OUT = os.path.join(ROOT, "marketing_print", "twitter_assets")
os.makedirs(OUT, exist_ok=True)

CREAM = (244, 239, 230)
INK   = (22, 38, 28)
GREEN = (15, 122, 62)
MUTED = (110, 120, 115)

SILHOUETTE = "batistuta.jpg"


def font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size, index=1 if bold else 0)
            except Exception:
                return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def make_profile_picture():
    """800x800 square — Twitter crops to circle on display."""
    SIZE = 800
    canvas = Image.new("RGB", (SIZE, SIZE), CREAM)

    sil = Image.open(os.path.join(SILS, SILHOUETTE)).convert("RGB")
    # Generous scale: fill ~85% of the canvas so when Twitter circle-crops,
    # the silhouette still reads big.
    target = int(SIZE * 0.85)
    sw, sh = sil.size
    scale = min(target / sw, target / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    sil = sil.resize((nw, nh), Image.LANCZOS)
    canvas.paste(sil, ((SIZE - nw) // 2, (SIZE - nh) // 2))

    out = os.path.join(OUT, "twitter_profile_picture.jpg")
    canvas.save(out, "JPEG", quality=92)
    print("wrote", os.path.relpath(out, ROOT))


def make_banner():
    """1500x500 — Twitter header banner.

    Layout: silhouette on the RIGHT, text on the LEFT-TOP.
    Avoids the bottom-left overlap zone where Twitter places the
    profile picture circle (~ bottom-left 220x220 region).
    """
    W, H = 1500, 500
    canvas = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(canvas)

    # Silhouette on the RIGHT, vertically centred, generous height
    sil = Image.open(os.path.join(SILS, SILHOUETTE)).convert("RGB")
    sil_target_h = int(H * 1.0)
    sw, sh = sil.size
    scale = sil_target_h / sh
    nw, nh = int(sw * scale), int(sh * scale)
    sil = sil.resize((nw, nh), Image.LANCZOS)
    # Anchor right edge with some padding from canvas right
    sil_x = W - nw - 40
    sil_y = (H - nh) // 2
    canvas.paste(sil, (sil_x, sil_y))

    # Text block on the LEFT, top-anchored so it sits above the
    # profile-picture overlap zone (which Twitter draws at the
    # bottom-left, ~60-280px from left, ~290-500px from top).
    text_x = 60

    # 1. Big brand mark
    f_brand = font(60, bold=True)
    draw.text((text_x, 50), "GOOD TO HEAR", fill=INK, font=f_brand)
    draw.text((text_x, 120), "THE NAME.", fill=INK, font=f_brand)

    # 2. Subtitle
    f_sub = font(26, bold=True)
    draw.text((text_x, 215),
              "A DAILY FOOTBALL SILHOUETTE QUIZ",
              fill=GREEN, font=f_sub)

    # 3. Mechanic
    f_body = font(24)
    draw.text((text_x, 258),
              "Five clues. Five guesses. New player every day.",
              fill=INK, font=f_body)

    # URL sits at the TOP-RIGHT to avoid bottom-left overlap zone
    f_url = font(24, bold=True)
    url_text = "goodtohearthename.co.uk"
    bb = draw.textbbox((0, 0), url_text, font=f_url)
    uw = bb[2] - bb[0]
    draw.text((W - uw - 40, 30), url_text,
              fill=GREEN, font=f_url)

    out = os.path.join(OUT, "twitter_banner.jpg")
    canvas.save(out, "JPEG", quality=92)
    print("wrote", os.path.relpath(out, ROOT))


if __name__ == "__main__":
    sil_path = os.path.join(SILS, SILHOUETTE)
    if not os.path.exists(sil_path):
        raise SystemExit(f"missing source silhouette: {sil_path}")
    make_profile_picture()
    make_banner()
    print("\nDone. Files in marketing_print/twitter_assets/")
