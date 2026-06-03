#!/usr/bin/env python3
"""Add `todayMatch` field to the 17 WC group-stage players in all four data files.

Field is shown in the UI as:
  - Pre-reveal: a "🏆 WC 2026" chip (driven by presence of todayMatch)
  - Post-reveal: a "Today's match: <fixture>" line under the player name
"""
import json, re, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANDROID = os.path.join(ROOT, "app/src/main/assets/content.json")
IOS     = os.path.join(ROOT, "ios/GoodToHearTheName/GoodToHearTheName/Resources/content.json")
WEB_PL  = os.path.join(ROOT, "docs/players.js")
WEB_BIO = os.path.join(ROOT, "docs/bios.js")

# Verified UK-calendar fixtures (16 of 17 PASS, Day 44 has the accepted 3am-quirk)
TODAY_MATCH = {
    "rafael_marquez":  "Mexico v South Africa",
    "edin_dzeko":      "Canada v Bosnia & Herzegovina",
    "oscar_brazil":    "Brazil v Morocco",
    "arjen_robben":    "Netherlands v Japan",
    "diego_forlan":    "Saudi Arabia v Uruguay",
    "el_hadji_diouf":  "France v Senegal",
    "james_rodriguez": "Uzbekistan v Colombia",
    "pavel_nedved":    "Czechia v South Africa",
    "tim_howard":      "USA v Australia",
    "wout_weghorst":   "Netherlands v Sweden",
    "keisuke_honda":   "Tunisia v Japan",
    "maxi_rodriguez":  "Argentina v Austria",
    "joe_cole":        "England v Ghana",
    "maicon":          "Scotland v Brazil",
    "serge_aurier":    "Curaçao v Côte d'Ivoire",
    "youri_djorkaeff": "Norway v France",
    "davor_suker":     "Croatia v Ghana",
}

def update_json(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    count = 0
    for p in data["footballers"]:
        if p["id"] in TODAY_MATCH:
            p["todayMatch"] = TODAY_MATCH[p["id"]]
            count += 1
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  {path}: set todayMatch on {count} players")

def update_players_js():
    with open(WEB_PL, encoding="utf-8") as f:
        src = f.read()
    m = re.search(r"window\.PLAYERS\s*=\s*(\[.*\])\s*;?\s*\Z", src, re.DOTALL)
    players = json.loads(m.group(1))
    count = 0
    for p in players:
        if p["id"] in TODAY_MATCH:
            p["todayMatch"] = TODAY_MATCH[p["id"]]
            count += 1
    new_src = "window.PLAYERS = " + json.dumps(players, ensure_ascii=False, indent=2) + ";\n"
    with open(WEB_PL, "w", encoding="utf-8") as f:
        f.write(new_src)
    print(f"  {WEB_PL}: set todayMatch on {count} players")

if __name__ == "__main__":
    print("Adding todayMatch field…")
    update_json(ANDROID)
    update_json(IOS)
    update_players_js()
    # bios.js is for post-reveal detail; todayMatch belongs with the player record (players.js),
    # not the bio, so we leave bios.js alone.
    print("Done.")
