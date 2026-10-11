#!/usr/bin/env python3
"""Merge the 86 new v1.8 players into every platform's content, in day order.

Native (Android + iOS) read content.json, where the array index is the day
offset from the 2026-05-05 epoch. Web reads docs/players.js (the puzzle) and
docs/bios.js (the reveal), plus docs/names.json for guess autocomplete.

Run with --check to see what would change; --commit to write.
"""
import argparse
import json
import shutil
import unicodedata
from datetime import date, timedelta

BUILD = "planning/v1_8_build"
EPOCH = date(2026, 5, 5)

NATIVE = [
    "app/src/main/assets/content.json",
    "ios/GoodToHearTheName/GoodToHearTheName/Resources/content.json",
]
WEB_PLAYERS = "docs/players.js"
WEB_BIOS = "docs/bios.js"
# all three platforms carry the same guess-autocomplete database
NAMES = [
    "app/src/main/assets/names.json",
    "ios/GoodToHearTheName/GoodToHearTheName/Resources/names.json",
    "docs/names.json",
]

# content.json field -> what the web puzzle file calls it
WEB_PLAYER_FIELDS = ["id", "name", "country", "flag", "years", "approved",
                     "aliases", "clues", "kickoff"]
WEB_BIO_FIELDS = ["position", "yearsActive", "story", "numbers", "honours",
                  "didYouKnow", "youtube"]



def fold(text):
    """Compare names ignoring accents: Kaka and Kaka are the same person."""
    return "".join(c for c in unicodedata.normalize("NFD", text)
                   if unicodedata.category(c) != "Mn").lower()

def ordered_new():
    players = {p["name"]: p for p in json.load(open(f"{BUILD}/new_players.json"))}
    order = json.load(open(f"{BUILD}/day_order.json"))
    assert len(order) == len(players) == 86, "day order and player count disagree"
    return [players[n] for n in order]


def load_js(path, open_ch, close_ch):
    """docs/*.js are a JS assignment wrapping one JSON literal."""
    text = open(path).read()
    start = text.index(open_ch)
    end = text.rindex(close_ch) + 1
    return text[:start], json.loads(text[start:end]), text[end:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", action="store_true")
    args = ap.parse_args()
    new = ordered_new()

    # ---- native -------------------------------------------------------
    for path in NATIVE:
        data = json.load(open(path))
        existing = data["footballers"]
        ids = {p["id"] for p in existing}
        clash = ids & {p["id"] for p in new}
        if clash:
            raise SystemExit(f"{path}: ids already present: {sorted(clash)}")
        first = len(existing)
        merged = existing + new
        print(f"{path}\n  {len(existing)} -> {len(merged)} players "
              f"(new block starts at index {first}, "
              f"{EPOCH + timedelta(days=first):%d %b %Y})")
        if args.commit:
            shutil.copy(path, path + ".bak")
            data["footballers"] = merged
            with open(path, "w") as f:
                json.dump(data, f, indent=1, ensure_ascii=False)
                f.write("\n")

    # ---- web puzzle ---------------------------------------------------
    head, players, tail = load_js(WEB_PLAYERS, "[", "]")
    ids = {p["id"] for p in players}
    web_new = []
    for p in new:
        if p["id"] in ids:
            raise SystemExit(f"{WEB_PLAYERS}: {p['id']} already present")
        w = {"id": p["id"], "name": p["name"], "country": p["country"],
             "flag": p["countryFlag"], "years": p["years"], "approved": True,
             "aliases": p["aliases"], "clues": p["clues"], "kickoff": p["kickoff"]}
        web_new.append({k: w[k] for k in WEB_PLAYER_FIELDS})
    print(f"{WEB_PLAYERS}\n  {len(players)} -> {len(players) + len(web_new)} players")
    if args.commit:
        shutil.copy(WEB_PLAYERS, WEB_PLAYERS + ".bak")
        body = json.dumps(players + web_new, indent=2, ensure_ascii=False)
        open(WEB_PLAYERS, "w").write(head + body + tail)

    # ---- web reveal ---------------------------------------------------
    head_b, bios, tail_b = load_js(WEB_BIOS, "{", "}")
    added = 0
    for p in new:
        if p["id"] in bios:
            raise SystemExit(f"{WEB_BIOS}: {p['id']} already present")
        bios[p["id"]] = {k: p[k] for k in WEB_BIO_FIELDS}
        added += 1
    print(f"{WEB_BIOS}\n  {len(bios) - added} -> {len(bios)} bios (+{added})")
    if args.commit:
        shutil.copy(WEB_BIOS, WEB_BIOS + ".bak")
        body = json.dumps(bios, indent=2, ensure_ascii=False, sort_keys=True)
        open(WEB_BIOS, "w").write(head_b + body + tail_b)

    # ---- guess autocomplete, all three platforms ----------------------
    # The web dedupes this list against players.js by exact lowercase name, so a
    # name already present in an accented spelling needs no unaccented twin. Only
    # genuinely absent names get added.
    names = json.load(open(NAMES[0]))
    by_fold = {fold(n["n"]) for n in names}
    missing = [p for p in new if fold(p["name"]) not in by_fold]
    print("names.json (x3)")
    print(f"  {len(names)} names, {len(missing)} of the 86 genuinely absent")
    for p in missing:
        print(f"    + {p['name']}")
    if missing:
        names = names + [{"n": p["name"], "f": p["countryFlag"], "y": p["years"]}
                         for p in missing]
        names.sort(key=lambda n: fold(n["n"]))
        body = json.dumps(names, ensure_ascii=False, separators=(", ", ": "))
        for path in NAMES:
            if args.commit:
                shutil.copy(path, path + ".bak")
                open(path, "w").write(body)

    print("\ncommitted" if args.commit else "\ndry run, nothing written")


if __name__ == "__main__":
    main()
