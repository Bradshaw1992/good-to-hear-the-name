#!/usr/bin/env python3
"""
Fake tester: simulates playing through every player and verifying
the photo reveal works. Catches the class of bug where image files
exist but are actually silhouettes (or vice versa).

Checks per player:
  1. Photo and silhouette are different files (MD5)
  2. Photo isn't suspiciously dark (likely a silhouette in disguise)
  3. Silhouette is darker than the photo (generation worked)
  4. Cross-platform: same image used on iOS, Android, and web

Usage: python3 scripts/fake_tester.py
"""

import hashlib
import json
import os
import subprocess
import sys
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

IOS_IMAGES = os.path.join(ROOT, "ios/GoodToHearTheName/GoodToHearTheName/Resources/images")
IOS_SILS = os.path.join(ROOT, "ios/GoodToHearTheName/GoodToHearTheName/Resources/silhouettes")
ANDROID_IMAGES = os.path.join(ROOT, "app/src/main/assets/images")
ANDROID_SILS = os.path.join(ROOT, "app/src/main/assets/silhouettes")
WEB_IMAGES = os.path.join(ROOT, "docs/images")
WEB_SILS = os.path.join(ROOT, "docs/silhouettes")

CONTENT_JSON = os.path.join(ROOT, "app/src/main/assets/content.json")
BRIGHTNESS_SCRIPT = "/tmp/check_brightness.swift"

EPOCH = date(2026, 5, 5)
MIN_PHOTO_BRIGHTNESS = 0.20
MAX_SILHOUETTE_BRIGHTNESS = 0.55

errors = []
warnings = []


def error(msg):
    errors.append(msg)
    print(f"  FAIL: {msg}")


def warn(msg):
    warnings.append(msg)
    print(f"  WARN: {msg}")


def md5(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def brightness(path):
    try:
        result = subprocess.run(
            ["swift", BRIGHTNESS_SCRIPT, path],
            capture_output=True, text=True, timeout=30
        )
        return float(result.stdout.strip())
    except Exception:
        return -1


with open(CONTENT_JSON) as f:
    players = json.load(f)["footballers"]

total = len(players)
today = date.today()

print(f"\n{'='*60}")
print(f"FAKE TESTER — simulating {total} player reveals")
print(f"{'='*60}")

# Phase 1: check every player's images
print(f"\n--- Phase 1: Image integrity ({total} players) ---\n")

for i, p in enumerate(players):
    pid = p["id"]
    img = p["image"]
    sil_field = p.get("silhouette", "") or img

    ios_photo = os.path.join(IOS_IMAGES, img)
    ios_sil = os.path.join(IOS_SILS, f"sil_{img}")
    android_photo = os.path.join(ANDROID_IMAGES, img)
    android_sil = os.path.join(ANDROID_SILS, sil_field)
    web_photo = os.path.join(WEB_IMAGES, f"{pid}.jpg")
    web_sil = os.path.join(WEB_SILS, f"{pid}.jpg")

    # Check files exist
    for label, path in [("iOS photo", ios_photo), ("iOS sil", ios_sil),
                         ("Android photo", android_photo), ("Android sil", android_sil),
                         ("Web photo", web_photo), ("Web sil", web_sil)]:
        if not os.path.exists(path):
            error(f"[{pid}] MISSING {label}: {os.path.basename(path)}")

    if not os.path.exists(ios_photo) or not os.path.exists(ios_sil):
        continue

    # Check photo != silhouette (MD5)
    photo_hash = md5(ios_photo)
    sil_hash = md5(ios_sil)
    if photo_hash == sil_hash:
        error(f"[{pid}] Photo and silhouette are IDENTICAL — reveal will show no change")

    # Brightness check
    photo_bright = brightness(ios_photo)
    sil_bright = brightness(ios_sil)

    if photo_bright < 0 or sil_bright < 0:
        warn(f"[{pid}] Could not measure brightness")
        continue

    if photo_bright < MIN_PHOTO_BRIGHTNESS:
        error(f"[{pid}] Photo is suspiciously dark ({photo_bright:.3f}) — likely a silhouette in disguise")

    if sil_bright > MAX_SILHOUETTE_BRIGHTNESS:
        warn(f"[{pid}] Silhouette is unusually bright ({sil_bright:.3f}) — may not look like a silhouette")

    if photo_bright > 0 and sil_bright >= photo_bright:
        warn(f"[{pid}] Silhouette ({sil_bright:.3f}) is brighter than photo ({photo_bright:.3f}) — unusual")

    # Cross-platform sync: iOS photo should match Android and web
    if os.path.exists(android_photo) and md5(android_photo) != photo_hash:
        error(f"[{pid}] Android photo differs from iOS")
    if os.path.exists(web_photo) and md5(web_photo) != photo_hash:
        error(f"[{pid}] Web photo differs from iOS")

    android_sil_hash = md5(android_sil) if os.path.exists(android_sil) else None
    web_sil_hash = md5(web_sil) if os.path.exists(web_sil) else None
    if android_sil_hash and android_sil_hash != sil_hash:
        error(f"[{pid}] Android silhouette differs from iOS")
    if web_sil_hash and web_sil_hash != sil_hash:
        error(f"[{pid}] Web silhouette differs from iOS")

    status = "OK" if pid not in [e.split("]")[0].strip("[") for e in errors] else "FAIL"
    print(f"  [{i+1:2d}/{total}] {pid:30s} photo={photo_bright:.3f}  sil={sil_bright:.3f}  {status}")


# Phase 2: simulate the next 30 days of gameplay
print(f"\n--- Phase 2: Simulating next 30 days of reveals ---\n")

for day_offset in range(30):
    play_date = today + timedelta(days=day_offset)
    day_number = (play_date - EPOCH).days + 1
    player_index = (day_number - 1) % total
    p = players[player_index]
    pid = p["id"]

    ios_photo = os.path.join(IOS_IMAGES, p["image"])
    ios_sil = os.path.join(IOS_SILS, f"sil_{p['image']}")

    photo_ok = os.path.exists(ios_photo)
    sil_ok = os.path.exists(ios_sil)
    different = md5(ios_photo) != md5(ios_sil) if (photo_ok and sil_ok) else False

    if photo_ok and sil_ok and different:
        status = "PASS"
    else:
        status = "FAIL"
        reason = []
        if not photo_ok: reason.append("no photo")
        if not sil_ok: reason.append("no silhouette")
        if not different: reason.append("photo=silhouette")
        error(f"Day {day_number} ({play_date}) {pid}: {', '.join(reason)}")

    print(f"  {play_date} (day {day_number:3d}) → [{player_index:2d}] {pid:30s} {status}")


# Summary
print(f"\n{'='*60}")
print(f"ERRORS:   {len(errors)}")
print(f"WARNINGS: {len(warnings)}")

if errors:
    print("\nDO NOT SHIP — image reveal is broken for at least one player!")
    sys.exit(1)
elif warnings:
    print("\nOK to ship, but review warnings above.")
    sys.exit(0)
else:
    print("\nAll players pass — reveals will work correctly.")
    sys.exit(0)
