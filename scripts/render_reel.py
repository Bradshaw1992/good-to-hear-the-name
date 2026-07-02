#!/usr/bin/env python3
"""Render an archive-player Reel as a 1080x1920 MP4 from the frame PNGs.

Pipeline:
  - ffmpeg loops each PNG for its visible duration
  - xfade filter chains between clips (hard cut → small fade → big dissolve at reveal)
  - Audio: filtered pink noise stadium ambience + synthesized net-ripple SFX at reveal

Run: scripts/.venv/bin/python scripts/render_reel.py [player_id]
     (defaults to diego_forlan)
Output: marketing_print/reel_frames/<player_id>/<player_id>_reel.mp4
"""
import os
import sys
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAYER_ID = sys.argv[1] if len(sys.argv) > 1 else "diego_forlan"
FRAMES = os.path.join(ROOT, "marketing_print", "reel_frames", PLAYER_ID)
OUT = os.path.join(FRAMES, f"{PLAYER_ID}_reel.mp4")

# (filename, visible_seconds, xfade_to_next_seconds, xfade_kind)
# Last entry has xfade_to_next=None.
SEGMENTS = [
    ("01_brand.png",   2.2,  0.20, "fade"),
    ("02_clue1.png",   3.5,  0.20, "fade"),
    ("03_clue2.png",   3.5,  0.20, "fade"),
    ("04_clue3.png",   3.5,  0.20, "fade"),
    ("05_clue4.png",   4.5,  0.20, "fade"),
    ("06_clue5.png",   4.5,  0.60, "fade"),  # gentle fade into endcard (no reveal)
    ("07_endcard.png", 6.5,  None, None),
]

FPS = 30


def build_filter_complex():
    """Build the xfade chain. Each clip is input N. Pad inputs so they survive the xfade overlap."""
    # Padded input length per clip: visible + the xfade duration we'll be the FIRST half of.
    # The xfade filter consumes T seconds of each side, so the input must be >= visible + T.
    parts = []
    # running total = current length of the compound result
    running = SEGMENTS[0][1] + SEGMENTS[0][2]   # first clip pad: vis + xfade
    label_in = "[0:v]"
    for i in range(1, len(SEGMENTS)):
        vis_i = SEGMENTS[i][1]
        xf_prev = SEGMENTS[i - 1][2]
        xf_kind = SEGMENTS[i - 1][3]
        offset = running - xf_prev
        next_label = f"[v{i}]" if i < len(SEGMENTS) - 1 else "[vout]"
        parts.append(
            f"{label_in}[{i}:v]xfade=transition={xf_kind}:duration={xf_prev}:offset={offset}{next_label}"
        )
        label_in = next_label
        # update running: previous compound length + new clip - overlap
        running = offset + vis_i + (SEGMENTS[i][2] if SEGMENTS[i][2] else 0)
    return ";".join(parts), running


def input_duration(idx):
    """Each input loops for visible + outgoing xfade (to give xfade material)."""
    vis = SEGMENTS[idx][1]
    xf = SEGMENTS[idx][2] or 0
    # incoming-side xfade material: previous segment's outgoing xfade overlaps INTO this clip,
    # but xfade reuses the tail of the first input and head of the second, so we add only the
    # OUTGOING xfade time on top of visible.
    return round(vis + xf + 0.2, 3)


def build_audio_filter(total_dur):
    """Stadium ambience (filtered pink noise) for full duration + net-ripple SFX at the reveal.
    Reveal SFX timing is computed using the same xfade-offset math as the video filter, so the
    swoosh peak lands mid-dissolve regardless of segment edits above.
    """
    # Walk the same chain as build_filter_complex to find where the FINAL dissolve begins.
    running = SEGMENTS[0][1] + SEGMENTS[0][2]
    dissolve_start = 0
    for i in range(1, len(SEGMENTS)):
        xf_prev = SEGMENTS[i - 1][2]
        offset = running - xf_prev
        if i == len(SEGMENTS) - 1:
            dissolve_start = offset  # filter offset for the LAST xfade
            break
        running = offset + SEGMENTS[i][1] + (SEGMENTS[i][2] or 0)
    # The "magic" beat is mid-dissolve. Fire the swoosh so its peak (~0.12s in) lands there.
    last_xf = SEGMENTS[-2][2]
    reveal_start = dissolve_start + (last_xf / 2) - 0.12

    # Audio chain:
    #   src 0: pink noise -> lowpass -> volume -> ambience
    #   src 1: white noise burst windowed -> the net ripple at reveal_start
    f = (
        # ambience
        f"anoisesrc=color=pink:amplitude=0.35:duration={total_dur}:sample_rate=44100[ambsrc];"
        f"[ambsrc]lowpass=f=700,highpass=f=80,volume=0.18[amb];"
        # reveal swoosh: 0.6s white noise window, lowpass for "ripple" feel
        f"anoisesrc=color=white:amplitude=0.9:duration=0.6:sample_rate=44100[swsh];"
        f"[swsh]lowpass=f=1800,highpass=f=200,"
        f"afade=t=in:st=0:d=0.15,afade=t=out:st=0.20:d=0.40,volume=0.22[ripple];"
        f"[ripple]adelay={int(reveal_start*1000)}|{int(reveal_start*1000)}[rip_delayed];"
        f"[amb][rip_delayed]amix=inputs=2:duration=longest:dropout_transition=0[aout]"
    )
    return f, reveal_start


def main():
    # build ffmpeg input args (loop each PNG)
    in_args = []
    for i, (name, _, _, _) in enumerate(SEGMENTS):
        path = os.path.join(FRAMES, name)
        dur = input_duration(i)
        in_args += ["-loop", "1", "-t", str(dur), "-i", path]

    vfilter, total = build_filter_complex()
    afilter, reveal_t = build_audio_filter(total)
    filter_complex = vfilter + ";" + afilter

    cmd = [
        "ffmpeg", "-y",
        *in_args,
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-r", str(FPS),
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        OUT,
    ]
    print(f"Total video length: {total:.2f}s")
    print(f"Reveal SFX at: {reveal_t:.2f}s")
    print("Running ffmpeg...")
    subprocess.run(cmd, check=True)
    print(f"\nDone: {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
