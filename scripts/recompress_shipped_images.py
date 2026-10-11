#!/usr/bin/env python3
"""Recompress the already-shipped photos to the same recipe as new ones.

Reveal photos and silhouettes added before v1.8 were committed at whatever size
the source happened to be, up to 2835px, while the distribute script now caps
everything at 1600px on the long edge. That left the shipped set roughly four
times larger than it needs to be, which costs app download size, R2 bandwidth
and Pages traffic.

Recipe is copied from scripts/distribute_player_pictures.py so old and new match:
  reveal      1600px long edge, -strip, quality 82
  silhouette  1600px long edge, -strip, quality 88

docs/ is the canonical copy and is tracked in git, so a bad run is recoverable
with `git checkout -- docs/images docs/silhouettes`. The other platform folders
are mirrored from docs/ afterwards rather than converted separately, so every
platform ships byte-identical files.
"""
import argparse
import json
import os
import shutil
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_PX = 1600
REVEAL_QUALITY = 82
SIL_QUALITY = 88

WEB_IMAGES = os.path.join(ROOT, "docs/images")
WEB_SILS = os.path.join(ROOT, "docs/silhouettes")
IOS_IMAGES = os.path.join(ROOT, "ios/GoodToHearTheName/GoodToHearTheName/Resources/images")
IOS_SILS = os.path.join(ROOT, "ios/GoodToHearTheName/GoodToHearTheName/Resources/silhouettes")
ANDROID_SILS = os.path.join(ROOT, "app/src/main/assets/silhouettes")


def new_ids():
    path = os.path.join(ROOT, "planning/v1_8_build/new_players.json")
    return {p["id"] for p in json.load(open(path))}


def recompress(path, quality, dry):
    """Shrink-and-reencode in place. Returns (before, after) bytes."""
    before = os.path.getsize(path)
    if dry:
        out = subprocess.run(
            ["magick", path, "-resize", f"{MAX_PX}x{MAX_PX}>", "-strip",
             "-quality", str(quality), "jpg:-"],
            capture_output=True)
        return before, len(out.stdout)
    subprocess.run(
        ["magick", path, "-resize", f"{MAX_PX}x{MAX_PX}>", "-strip",
         "-quality", str(quality), path], check=True)
    return before, os.path.getsize(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", action="store_true")
    args = ap.parse_args()
    dry = not args.commit
    skip = new_ids()

    total_b = total_a = 0
    for folder, quality, label in [(WEB_IMAGES, REVEAL_QUALITY, "reveal photos"),
                                   (WEB_SILS, SIL_QUALITY, "silhouettes")]:
        files = sorted(f for f in os.listdir(folder)
                       if f.endswith(".jpg") and f[:-4] not in skip)
        fb = fa = 0
        for f in files:
            b, a = recompress(os.path.join(folder, f), quality, dry)
            # never make a file bigger: skip the write if the recipe does not help
            if a >= b and not dry:
                subprocess.run(["git", "checkout", "--",
                                os.path.join(folder, f)], cwd=ROOT)
                a = b
            fb += b
            fa += min(a, b)
        total_b += fb
        total_a += fa
        print(f"  {label:16} {len(files):3} files  "
              f"{fb / 1e6:6.1f} MB -> {fa / 1e6:5.1f} MB  "
              f"(saves {(fb - fa) / 1e6:5.1f} MB)")

    print(f"  {'TOTAL':16}      {total_b / 1e6:10.1f} MB -> {total_a / 1e6:5.1f} MB"
          f"  (saves {(total_b - total_a) / 1e6:.1f} MB)")

    if not args.commit:
        print("\ndry run, nothing written")
        return

    # mirror docs/ out to the other platforms so every copy is byte-identical
    print("\nmirroring to the other platform folders")
    n = 0
    for f in os.listdir(WEB_IMAGES):
        if f.endswith(".jpg") and os.path.exists(os.path.join(IOS_IMAGES, f)):
            shutil.copyfile(os.path.join(WEB_IMAGES, f), os.path.join(IOS_IMAGES, f))
            n += 1
    print(f"  ios images       {n}")
    n = 0
    for f in os.listdir(WEB_SILS):
        if not f.endswith(".jpg"):
            continue
        shutil.copyfile(os.path.join(WEB_SILS, f), os.path.join(ANDROID_SILS, f))
        shutil.copyfile(os.path.join(WEB_SILS, f), os.path.join(IOS_SILS, "sil_" + f))
        n += 1
    print(f"  android + ios silhouettes  {n} each")
    print("\ndone")


if __name__ == "__main__":
    main()
