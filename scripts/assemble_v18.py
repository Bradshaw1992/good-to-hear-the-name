#!/usr/bin/env python3
"""Assemble the 86 v1.8 records from the four separate working files.

derived.json      mechanical fields (id, aliases, kickoff, numbers, flag, honours...)
v1_8_picked_clues.md  the 5 clues the user chose, per player
stories.md        the reveal paragraph
youtube.json      the oEmbed-verified video link

Writes planning/v1_8_build/new_players.json in exactly the shipped field order.
"""
import json
import re
import sys

BUILD = "planning/v1_8_build"

# field order copied from the shipped records so a diff of content.json stays readable
ORDER = ["id", "name", "country", "countryFlag", "years", "aliases", "clues",
         "image", "silhouette", "position", "yearsActive", "kickoff", "story",
         "numbers", "honours", "didYouKnow", "youtube", "clubs"]



def strip_note(clue):
    """Drop my own working annotations, e.g. "...Villa.  [GOES STALE if he moves]"."""
    return re.sub(r"\s*\[[^\]]*\]\s*$", "", clue).strip()

def read_clues(path):
    text = open(path).read()
    out = {}
    for name, body in re.findall(r"^## (.+?)\n(.*?)(?=\n## |\Z)", text, re.M | re.S):
        clues = re.findall(r"^\s*([1-5])\.\s+(.+?)\s*$", body, re.M)
        if clues:
            out[name.strip()] = [strip_note(c) for _, c in clues[:5]]
    return out


def read_stories(path):
    text = open(path).read()
    return {n.strip(): b.strip()
            for n, b in re.findall(r"^## (.+?)\n(.+?)(?=\n\n## |\Z)", text, re.M | re.S)}


def main():
    derived = json.load(open(f"{BUILD}/derived.json"))
    clues = read_clues("planning/v1_8_picked_clues.md")
    stories = read_stories(f"{BUILD}/stories.md")
    videos = {v["name"]: v["youtube"] for v in json.load(open(f"{BUILD}/youtube.json"))}

    records, problems = [], []
    for p in derived:
        name = p["name"]
        if name not in clues:
            problems.append(f"{name}: no clues")
            continue
        if len(clues[name]) != 5:
            problems.append(f"{name}: {len(clues[name])} clues, expected 5")
        if name not in stories:
            problems.append(f"{name}: no story")
        if name not in videos:
            problems.append(f"{name}: no video")

        p = dict(p, clues=clues.get(name, []),
                 story=stories.get(name, ""),
                 youtube=videos.get(name, ""))
        records.append({k: p[k] for k in ORDER if k in p})

    for n in clues:
        if n not in {p["name"] for p in derived}:
            problems.append(f"{n}: has clues but is not in derived.json")

    if problems:
        print("PROBLEMS:")
        for x in problems:
            print("  " + x)
        sys.exit(1)

    out = f"{BUILD}/new_players.json"
    with open(out, "w") as f:
        json.dump(records, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {len(records)} complete records to {out}")


if __name__ == "__main__":
    main()
