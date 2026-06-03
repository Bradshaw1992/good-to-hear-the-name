#!/usr/bin/env python3
"""Distribute player photos from Player Pictures/ to every platform asset folder.

Honours the established silhouette protocol (see memory: feedback-silhouette-approach):
  base Vision segmentation -> tier-aware ImageMagick treatment -> brightness-adaptive recipe.

Workflow
========
1. Drop photos into Player Pictures/ named after the player id, e.g.:
     rafael_marquez.jpg                   (used as reveal AND silhouette source)
     rafael_marquez_sil.jpg               (optional dedicated silhouette source)
   Allowed extensions: .jpg .jpeg .png .webp .avif (auto-converted to .jpg).
2. Preview to silhouette_previews/ without writing platform folders:
     python3 scripts/distribute_player_pictures.py --review
3. Inspect silhouette_previews/.  Re-run with a higher tier on any that are too recognisable:
     python3 scripts/distribute_player_pictures.py --review --tier 3 --only rafael_marquez
4. Commit to all 6 platform folders once you're happy:
     python3 scripts/distribute_player_pictures.py --commit

Tiers (per feedback-silhouette-approach):
  1  No post-processing (Vision blackout only, background untouched)
  2  Slight blur + desaturate.  Brightness-adaptive: bright sources also darken.  DEFAULT.
  3  Heavy blur + darken + desaturate.  For backgrounds that still leak identity.
  4  Nuclear blackout.  Greyscale + heavy blur + multiply gray(12%).  For watermarked sources
     (e.g. the Yakubu rework that finally killed the Alamy watermark).

Min source resolution: 800x800.  Smaller sources are flagged (see Shevchenko 202x250 issue).

Flags
-----
--review       Write silhouettes only to silhouette_previews/ (no platform folders touched).
--commit       Write to all 6 platform folders.  Required to touch live assets.
--tier N       Override tier (1-4) for this run.  Default: 2.
--only ID      Only process this player_id.
--dry-run      Report what would happen without writing anything.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(ROOT, "Player Pictures")
PREVIEW_DIR = os.path.join(ROOT, "silhouette_previews")

# Reveal-image targets: same filename across all three platforms
IMAGES_TARGETS = [
    os.path.join(ROOT, "app/src/main/assets/images"),
    os.path.join(ROOT, "ios/GoodToHearTheName/GoodToHearTheName/Resources/images"),
    os.path.join(ROOT, "docs/images"),
]

# Silhouette targets: iOS uses a `sil_` prefix (verified in current asset tree)
SILHOUETTE_TARGETS = [
    {"dir": os.path.join(ROOT, "app/src/main/assets/silhouettes"), "prefix": ""},
    {"dir": os.path.join(ROOT, "ios/GoodToHearTheName/GoodToHearTheName/Resources/silhouettes"), "prefix": "sil_"},
    {"dir": os.path.join(ROOT, "docs/silhouettes"), "prefix": ""},
]

SILHOUETTE_SCRIPT = os.path.join(ROOT, "scripts/silhouette.swift")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}
SILHOUETTE_SUFFIX = "_sil"
MIN_RESOLUTION = 800
BRIGHTNESS_BREAKPOINT = 0.25  # fx:mean above this counts as a "bright" source


# ---------- helpers ----------

def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, **kw)

def normalize_to_jpg(src, dst):
    run(["sips", "--setProperty", "format", "jpeg",
         "-s", "formatOptions", "92",
         src, "--out", dst])

def measure_brightness(jpg_path):
    """Return mean luminance in [0,1]."""
    out = run(["magick", "identify", "-format", "%[fx:mean]", jpg_path]).stdout.decode().strip()
    try:
        return float(out)
    except ValueError:
        return 0.5  # default to middle if measurement fails

def measure_resolution(jpg_path):
    out = run(["magick", "identify", "-format", "%w %h", jpg_path]).stdout.decode().strip()
    w, h = (int(x) for x in out.split())
    return w, h

def generate_base_silhouette(jpg_in, jpg_out):
    """Run the Swift Vision base step.  Returns (ok, stderr)."""
    r = subprocess.run(["swift", SILHOUETTE_SCRIPT, jpg_in, jpg_out],
                       capture_output=True, text=True)
    return r.returncode == 0, r.stderr.strip()

def apply_tier_treatment(jpg_in, jpg_out, tier, mean_brightness):
    """Apply tier-specific post-processing on top of the base silhouette."""
    cmd = ["magick", jpg_in]

    if tier == 1:
        # No change, just copy through magick to re-encode at consistent quality
        pass
    elif tier == 2:
        # Slight blur + desaturate; brightness-adaptive
        cmd += ["-blur", "0x12", "-modulate", "100,15,100"]
        if mean_brightness > BRIGHTNESS_BREAKPOINT:
            cmd += ["-brightness-contrast", "-30x-15"]
    elif tier == 3:
        # Heavy blur + darken + desaturate.  Götze reference recipe.
        cmd += ["-blur", "0x12",
                "-brightness-contrast", "-60x-40",
                "-modulate", "100,15,100"]
    elif tier == 4:
        # Nuclear blackout for watermarked / hopeless sources
        cmd += ["-colorspace", "Gray",
                "-blur", "0x30",
                "-evaluate", "Multiply", "0.12"]
    else:
        raise ValueError(f"Unknown tier {tier}")

    cmd += ["-quality", "88", jpg_out]
    run(cmd)


# ---------- discovery ----------

def parse_drop_filename(filename):
    name, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        return None, None
    name = name.replace(" ", "_").replace("-", "_").replace("__", "_")
    if name.endswith(SILHOUETTE_SUFFIX):
        return name[:-len(SILHOUETTE_SUFFIX)], True
    return name, False

def collect_drops(only=None):
    by_player = {}
    for fn in sorted(os.listdir(SOURCE_DIR)):
        full = os.path.join(SOURCE_DIR, fn)
        if not os.path.isfile(full) or os.path.getsize(full) == 0:
            continue
        pid, is_sil = parse_drop_filename(fn)
        if pid is None:
            continue
        if only and pid != only:
            continue
        entry = by_player.setdefault(pid, {"reveal": None, "silhouette_source": None})
        slot = "silhouette_source" if is_sil else "reveal"
        if entry[slot]:
            print(f"  warn: multiple {slot} files for '{pid}', keeping {fn} (overwriting {os.path.basename(entry[slot])})")
        entry[slot] = full
    return by_player


# ---------- main ----------

def process(pid, slots, tier, tmp, preview_only):
    reveal_src = slots["reveal"] or slots["silhouette_source"]
    sil_src = slots["silhouette_source"] or reveal_src
    print(f"\n→ {pid}")

    # Normalise both inputs to JPEG in tmp
    reveal_jpg = os.path.join(tmp, f"{pid}.jpg")
    normalize_to_jpg(reveal_src, reveal_jpg)
    print(f"    reveal source: {os.path.basename(reveal_src)}")

    if sil_src != reveal_src:
        sil_input = os.path.join(tmp, f"{pid}_silsrc.jpg")
        normalize_to_jpg(sil_src, sil_input)
        print(f"    silhouette source: {os.path.basename(sil_src)}")
    else:
        sil_input = reveal_jpg
        print(f"    silhouette source: (same as reveal)")

    # Resolution check
    w, h = measure_resolution(sil_input)
    if min(w, h) < MIN_RESOLUTION:
        print(f"    WARN: source is {w}x{h}, below {MIN_RESOLUTION}px minimum.  See Shevchenko issue.")

    # Brightness measurement (drives tier-2 recipe branch)
    mean = measure_brightness(sil_input)
    print(f"    brightness: {mean:.2f}  ({'bright' if mean > BRIGHTNESS_BREAKPOINT else 'dark'} source)")

    # Step 1: Vision base silhouette
    base = os.path.join(tmp, f"{pid}_base.jpg")
    ok, err = generate_base_silhouette(sil_input, base)
    if not ok:
        print(f"    Vision segmentation FAILED: {err}")
        print(f"    using raw source as fallback (NO person blackout applied)")
        shutil.copyfile(sil_input, base)

    # Step 2: tier treatment
    final = os.path.join(tmp, f"{pid}_silhouette.jpg")
    apply_tier_treatment(base, final, tier, mean)
    print(f"    tier {tier} treatment applied")

    # Always write to preview folder
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    shutil.copyfile(final, os.path.join(PREVIEW_DIR, f"{pid}.jpg"))
    shutil.copyfile(reveal_jpg, os.path.join(PREVIEW_DIR, f"{pid}_reveal.jpg"))
    print(f"    preview: silhouette_previews/{pid}.jpg + {pid}_reveal.jpg")

    if preview_only:
        return

    # Write to all 6 platform folders
    for tgt in IMAGES_TARGETS:
        shutil.copyfile(reveal_jpg, os.path.join(tgt, f"{pid}.jpg"))
    for tgt in SILHOUETTE_TARGETS:
        shutil.copyfile(final, os.path.join(tgt["dir"], f"{tgt['prefix']}{pid}.jpg"))
    print(f"    committed to all 6 platform folders")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--review", action="store_true",
                      help="Write only to silhouette_previews/ (default if neither flag given)")
    mode.add_argument("--commit", action="store_true",
                      help="Write to all 6 platform folders")
    p.add_argument("--tier", type=int, default=2, choices=[1, 2, 3, 4],
                   help="Treatment tier 1-4 (default 2)")
    p.add_argument("--only", help="Only process this player_id")
    p.add_argument("--dry-run", action="store_true", help="Show what would happen without writing")
    args = p.parse_args()

    # Default to --review if no mode was given
    preview_only = not args.commit

    if not os.path.isdir(SOURCE_DIR):
        print(f"ERROR: {SOURCE_DIR} not found", file=sys.stderr); sys.exit(1)
    if not os.path.isfile(SILHOUETTE_SCRIPT):
        print(f"ERROR: {SILHOUETTE_SCRIPT} not found", file=sys.stderr); sys.exit(1)

    by_player = collect_drops(only=args.only)
    if not by_player:
        print("No valid drops in Player Pictures/.")
        return

    mode_label = "REVIEW (preview folder only)" if preview_only else "COMMIT (writing to all platforms)"
    print(f"\nMode: {mode_label}   Tier: {args.tier}")
    print(f"Found {len(by_player)} player(s):")
    for pid in sorted(by_player):
        s = by_player[pid]
        flag_r = "✓" if s["reveal"] else "·"
        flag_s = "✓" if s["silhouette_source"] else "(reuse reveal)"
        print(f"  {pid:30s}  reveal {flag_r}   silhouette source {flag_s}")

    if args.dry_run:
        print("\n(dry run — no files written)")
        return

    tmp = tempfile.mkdtemp(prefix="distribute_pics_")
    failed = []
    for pid in sorted(by_player):
        try:
            process(pid, by_player[pid], args.tier, tmp, preview_only)
        except subprocess.CalledProcessError as e:
            err = (e.stderr or b"").decode("utf-8", errors="replace").strip()
            print(f"    ERROR processing {pid}: {err or e}")
            failed.append(pid)
    shutil.rmtree(tmp, ignore_errors=True)

    print(f"\nDone.")
    if preview_only:
        print(f"Previews in {os.path.relpath(PREVIEW_DIR, ROOT)}/.  Re-run with --commit to publish.")
    if failed:
        print(f"{len(failed)} failure(s): {', '.join(failed)}")


if __name__ == "__main__":
    main()
