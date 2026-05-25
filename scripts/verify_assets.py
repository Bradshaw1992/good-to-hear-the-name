#!/usr/bin/env python3
"""
Pre-build asset verification script.
Run before every Xcode archive to catch missing/misplaced files.

Usage: python3 scripts/verify_assets.py
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

IOS_IMAGES = os.path.join(ROOT, "ios/GoodToHearTheName/GoodToHearTheName/Resources/images")
IOS_SILHOUETTES = os.path.join(ROOT, "ios/GoodToHearTheName/GoodToHearTheName/Resources/silhouettes")
ANDROID_IMAGES = os.path.join(ROOT, "app/src/main/assets/images")
ANDROID_SILHOUETTES = os.path.join(ROOT, "app/src/main/assets/silhouettes")
WEB_IMAGES = os.path.join(ROOT, "docs/images")
WEB_SILHOUETTES = os.path.join(ROOT, "docs/silhouettes")

CONTENT_JSON = os.path.join(ROOT, "ios/GoodToHearTheName/GoodToHearTheName/Resources/content.json")
ANDROID_JSON = os.path.join(ROOT, "app/src/main/assets/content.json")
PLAYERS_JS = os.path.join(ROOT, "docs/players.js")
BIOS_JS = os.path.join(ROOT, "docs/bios.js")

errors = []
warnings = []


def error(msg):
    errors.append(msg)
    print(f"  ERROR: {msg}")


def warn(msg):
    warnings.append(msg)
    print(f"  WARN:  {msg}")


def check_file(path, description, min_size=1024):
    if not os.path.exists(path):
        error(f"MISSING {description}: {os.path.basename(path)}")
        return False
    size = os.path.getsize(path)
    if size < min_size:
        warn(f"TINY {description}: {os.path.basename(path)} ({size} bytes)")
    return True


# --- Load content ---
print("\n=== Loading content files ===")

with open(CONTENT_JSON) as f:
    ios_data = json.load(f)
players = ios_data["footballers"]
print(f"  iOS content.json: {len(players)} players")

with open(ANDROID_JSON) as f:
    android_data = json.load(f)
print(f"  Android content.json: {len(android_data['footballers'])} players")

with open(PLAYERS_JS) as f:
    raw = f.read()
js = raw.replace("window.PLAYERS = ", "", 1).rstrip()
if js.endswith(";"):
    js = js[:-1]
web_players = json.loads(js)
print(f"  Web players.js: {len(web_players)} players")

with open(BIOS_JS) as f:
    raw = f.read()
js = raw.replace("window.BIOS = ", "", 1).rstrip()
if js.endswith(";"):
    js = js[:-1]
web_bios = json.loads(js)
print(f"  Web bios.js: {len(web_bios)} entries")

# --- Check counts match ---
print("\n=== Player count check ===")
if len(players) != len(android_data["footballers"]):
    error(f"Player count mismatch: iOS={len(players)}, Android={len(android_data['footballers'])}")
if len(players) != len(web_players):
    error(f"Player count mismatch: iOS={len(players)}, Web={len(web_players)}")
if len(players) != len(web_bios):
    error(f"Player count mismatch: iOS={len(players)}, Bios={len(web_bios)}")

# --- Check iOS vs Android identical ---
print("\n=== iOS/Android sync check ===")
if json.dumps(ios_data, sort_keys=True) == json.dumps(android_data, sort_keys=True):
    print("  iOS and Android content.json are identical")
else:
    error("iOS and Android content.json DIFFER")

# --- Check each player ---
print(f"\n=== Checking {len(players)} players ===")
web_players_by_id = {p["id"]: p for p in web_players}

for i, p in enumerate(players):
    pid = p["id"]
    img = p.get("image", "")
    sil = p.get("silhouette", "") or img

    # Content fields
    if not p.get("story"):
        error(f"[{pid}] empty story")
    if not p.get("youtube"):
        error(f"[{pid}] empty youtube")
    if len(p.get("clues", [])) != 5:
        error(f"[{pid}] has {len(p.get('clues', []))} clues (expected 5)")
    if not p.get("position"):
        warn(f"[{pid}] empty position")

    # iOS files
    check_file(os.path.join(IOS_IMAGES, img), f"[{pid}] iOS image")
    check_file(os.path.join(IOS_SILHOUETTES, f"sil_{img}"), f"[{pid}] iOS silhouette")

    # Android files
    check_file(os.path.join(ANDROID_IMAGES, img), f"[{pid}] Android image")
    check_file(os.path.join(ANDROID_SILHOUETTES, sil), f"[{pid}] Android silhouette")

    # Web files (uses player ID, not image field)
    check_file(os.path.join(WEB_IMAGES, f"{pid}.jpg"), f"[{pid}] Web image")
    check_file(os.path.join(WEB_SILHOUETTES, f"{pid}.jpg"), f"[{pid}] Web silhouette")

    # Web data sync
    if pid not in web_players_by_id:
        error(f"[{pid}] missing from players.js")
    if pid not in web_bios:
        error(f"[{pid}] missing from bios.js")

    # Player order check
    if i < len(web_players) and web_players[i]["id"] != pid:
        error(f"Order mismatch at index {i}: iOS={pid}, Web={web_players[i]['id']}")

# --- Check for orphaned files in iOS silhouettes ---
print("\n=== Orphan check (iOS silhouettes) ===")
expected_sils = {f"sil_{p['image']}" for p in players}
actual_sils = set(os.listdir(IOS_SILHOUETTES))
orphans = actual_sils - expected_sils
if orphans:
    for o in sorted(orphans):
        if not o.startswith("."):
            warn(f"Orphaned file in iOS silhouettes: {o}")
else:
    print("  No orphans found")

# --- Summary ---
print(f"\n{'='*50}")
print(f"ERRORS: {len(errors)}")
print(f"WARNINGS: {len(warnings)}")

if errors:
    print("\nDO NOT BUILD — fix errors first!")
    sys.exit(1)
elif warnings:
    print("\nOK to build, but review warnings above.")
    sys.exit(0)
else:
    print("\nAll clear — safe to archive and submit.")
    sys.exit(0)
