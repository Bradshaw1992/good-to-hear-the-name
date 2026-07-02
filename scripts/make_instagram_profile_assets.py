#!/usr/bin/env python3
"""Generate Instagram profile picture + pinned welcome post.

- Profile picture: 1080x1080 of the Batistuta silhouette (IG crops to circle).
- Welcome post: 1080x1080 with brand + mechanic + audience + URL. Designed to
  be pinned to the top of the grid as the Instagram equivalent of a banner.

Run: scripts/.venv/bin/python scripts/make_instagram_profile_assets.py
Output: marketing_print/instagram_profile/
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
SILS = os.path.join(DOCS, "silhouettes")
OUT = os.path.join(ROOT, "marketing_print", "instagram_profile")
os.makedirs(OUT, exist_ok=True)

CREAM = (244, 239, 230)
INK   = (22, 38, 28)
GREEN = (15, 122, 62)
MUTED = (110, 120, 115)

SILHOUETTE = "batistuta.jpg"
SIZE = 1080


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


def center_text(draw, text, fnt, y, color=INK):
    bb = draw.textbbox((0, 0), text, font=fnt)
    w = bb[2] - bb[0]
    draw.text((SIZE // 2 - w // 2, y), text, fill=color, font=fnt)


def make_profile_picture():
    """Square 1080x1080. Instagram crops to circle on display."""
    canvas = Image.new("RGB", (SIZE, SIZE), CREAM)
    sil = Image.open(os.path.join(SILS, SILHOUETTE)).convert("RGB")
    # Fill ~85% so the silhouette stays prominent inside the circle crop
    target = int(SIZE * 0.85)
    sw, sh = sil.size
    scale = min(target / sw, target / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    sil = sil.resize((nw, nh), Image.LANCZOS)
    canvas.paste(sil, ((SIZE - nw) // 2, (SIZE - nh) // 2))

    out = os.path.join(OUT, "instagram_profile_picture.jpg")
    canvas.save(out, "JPEG", quality=92)
    print("wrote", os.path.relpath(out, ROOT))


def make_welcome_post():
    """1080x1080 welcome / about card to pin to the top of the grid."""
    canvas = Image.new("RGB", (SIZE, SIZE), CREAM)
    draw = ImageDraw.Draw(canvas)

    # 1. Top brand mark
    f_brand_big = font(72, bold=True)
    center_text(draw, "GOOD TO HEAR THE NAME.", f_brand_big, 70, color=INK)

    # 2. Subtitle below brand
    f_sub = font(32, bold=True)
    center_text(draw, "A DAILY FOOTBALL SILHOUETTE QUIZ",
                f_sub, 165, color=GREEN)

    # 3. Silhouette in the middle band
    sil = Image.open(os.path.join(SILS, SILHOUETTE)).convert("RGB")
    target_h = 500
    target_w = SIZE - 240
    sw, sh = sil.size
    scale = min(target_w / sw, target_h / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    sil = sil.resize((nw, nh), Image.LANCZOS)
    sil_x = (SIZE - nw) // 2
    sil_y = 230
    canvas.paste(sil, (sil_x, sil_y))

    # 4. Mechanic line
    f_body = font(34)
    center_text(draw, "Five clues.  Five guesses.  New player every day.",
                f_body, 770, color=INK)

    # 5. Audience signal
    center_text(draw,
                "Cult heroes.  Journeymen.  World Cup legends.",
                f_body, 820, color=MUTED)

    # 6. Made-by-a-fan line
    f_small = font(26)
    center_text(draw,
                "Free, no signup. Made by a fan, for the obsessives.",
                f_small, 880, color=MUTED)

    # 7. URL at bottom in green
    f_url = font(36, bold=True)
    center_text(draw, "goodtohearthename.co.uk",
                f_url, SIZE - 90, color=GREEN)

    out = os.path.join(OUT, "instagram_welcome_post.jpg")
    canvas.save(out, "JPEG", quality=92)
    print("wrote", os.path.relpath(out, ROOT))


if __name__ == "__main__":
    sil_path = os.path.join(SILS, SILHOUETTE)
    if not os.path.exists(sil_path):
        raise SystemExit(f"missing source silhouette: {sil_path}")
    make_profile_picture()
    make_welcome_post()
    print("\nDone. Files in marketing_print/instagram_profile/")
