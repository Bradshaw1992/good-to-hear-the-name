#!/usr/bin/env python3
"""Sync docs/players.js (web) with content.json (Android/iOS).

players.js has a simpler schema:
    id, name, country, flag, years, approved, aliases, clues

content.json has more fields (story, youtube, clubs, honours, didYouKnow, etc.)
which players.js does not consume. This script extracts the players.js subset
from content.json and rewrites docs/players.js as a JS module
(window.PLAYERS = [...]).

Run: scripts/.venv/bin/python scripts/sync_players_js.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "app/src/main/assets/content.json")
PLAYERS_JS = os.path.join(ROOT, "docs/players.js")


def main():
    with open(CONTENT) as f:
        data = json.load(f)

    out = []
    for p in data["footballers"]:
        out.append({
            "id": p["id"],
            "name": p["name"],
            "country": p["country"],
            "flag": p.get("countryFlag", ""),
            "years": p.get("yearsActive", p.get("years", "")),
            "approved": True,
            "aliases": p.get("aliases", []),
            "clues": p.get("clues", []),
        })

    body = json.dumps(out, ensure_ascii=False, indent=2)
    js = f"window.PLAYERS = {body};\n"
    with open(PLAYERS_JS, "w") as f:
        f.write(js)
    print(f"wrote {len(out)} players to {os.path.relpath(PLAYERS_JS, ROOT)}")


if __name__ == "__main__":
    main()
