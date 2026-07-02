#!/usr/bin/env python3
"""Generate Facebook Page assets (profile picture + cover photo).

- Profile picture: 800x800 (Facebook crops to circle).
- Cover photo: 1640x624 (Facebook's recommended Page banner size).
  Layout respects the profile-picture overlap zone at the bottom-left.

Run: scripts/.venv/bin/python scripts/make_facebook_assets.py
Output: marketing_print/facebook_assets/
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
SILS = os.path.join(DOCS, "silhouettes")
OUT = os.path.join(ROOT, "marketing_print", "facebook_assets")
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
    """800x800 square — Facebook crops to circle on display."""
    SIZE = 800
    canvas = Image.new("RGB", (SIZE, SIZE), CREAM)

    sil = Image.open(os.path.join(SILS, SILHOUETTE)).convert("RGB")
    target = int(SIZE * 0.85)
    sw, sh = sil.size
    scale = min(target / sw, target / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    sil = sil.resize((nw, nh), Image.LANCZOS)
    canvas.paste(sil, ((SIZE - nw) // 2, (SIZE - nh) // 2))

    out = os.path.join(OUT, "facebook_profile_picture.jpg")
    canvas.save(out, "JPEG", quality=92)
    print("wrote", os.path.relpath(out, ROOT))


def make_cover_photo():
    """1640x624 — Facebook Page cover photo.

    Profile picture circle overlays the bottom-left at roughly
    24-180px from left, 444-624px from top (desktop view).
    Mobile crops the centre 640x360, so important content sits
    in the central horizontal band.
    """
    W, H = 1640, 624
    canvas = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(canvas)

    # Silhouette on the RIGHT
    sil = Image.open(os.path.join(SILS, SILHOUETTE)).convert("RGB")
    target_h = int(H * 1.0)
    sw, sh = sil.size
    scale = target_h / sh
    nw, nh = int(sw * scale), int(sh * scale)
    sil = sil.resize((nw, nh), Image.LANCZOS)
    sil_x = W - nw - 50
    sil_y = (H - nh) // 2
    canvas.paste(sil, (sil_x, sil_y))

    # Text block on LEFT, TOP-aligned to avoid bottom-left profile-pic overlap
    text_x = 70

    # 1. Big brand mark (two lines)
    f_brand = font(70, bold=True)
    draw.text((text_x, 60), "GOOD TO HEAR", fill=INK, font=f_brand)
    draw.text((text_x, 140), "THE NAME.", fill=INK, font=f_brand)

    # 2. Subtitle
    f_sub = font(32, bold=True)
    draw.text((text_x, 250),
              "A DAILY FOOTBALL SILHOUETTE QUIZ",
              fill=GREEN, font=f_sub)

    # 3. Mechanic
    f_body = font(28)
    draw.text((text_x, 300),
              "Five clues. Five guesses. New player every day.",
              fill=INK, font=f_body)

    # 4. Audience signal
    draw.text((text_x, 340),
              "Cult heroes. Journeymen. World Cup legends.",
              fill=MUTED, font=f_body)

    # URL at TOP-RIGHT to avoid bottom-left overlap zone
    f_url = font(30, bold=True)
    url_text = "goodtohearthename.co.uk"
    bb = draw.textbbox((0, 0), url_text, font=f_url)
    uw = bb[2] - bb[0]
    draw.text((W - uw - 50, 35), url_text,
              fill=GREEN, font=f_url)

    out = os.path.join(OUT, "facebook_cover_photo.jpg")
    canvas.save(out, "JPEG", quality=92)
    print("wrote", os.path.relpath(out, ROOT))


if __name__ == "__main__":
    sil_path = os.path.join(SILS, SILHOUETTE)
    if not os.path.exists(sil_path):
        raise SystemExit(f"missing source silhouette: {sil_path}")
    make_profile_picture()
    make_cover_photo()
    print("\nDone. Files in marketing_print/facebook_assets/")
