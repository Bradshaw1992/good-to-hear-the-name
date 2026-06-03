#!/usr/bin/env python3
"""Apply second-pass fact-check fixes to all four data files.

Edits clues, bios (story), honours, and didYouKnow per player. Idempotent —
each replacement either matches the old string exactly and applies, or the
old string is not found (already applied) and the script reports it.
"""
import json
import re
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ANDROID = os.path.join(ROOT, "app/src/main/assets/content.json")
IOS     = os.path.join(ROOT, "ios/GoodToHearTheName/GoodToHearTheName/Resources/content.json")
WEB_PL  = os.path.join(ROOT, "docs/players.js")
WEB_BIO = os.path.join(ROOT, "docs/bios.js")


# ============================================================================
# FIXES per player. Each player can have:
#   "clue_replacements":   list of (old, new) substrings, applied to ALL clues
#   "clue_set":            {index: new_string} to fully replace a clue
#   "story":               full-rewrite string for the bio
#   "story_replacements":  list of (old, new) substring replacements
#   "honours_replacements": same shape for honours array
#   "didYouKnow_set":      {index: new_string} to fully replace a didYouKnow
# ============================================================================
FIXES = {
    "edin_dzeko": {
        "clue_set": {
            2: "I had a goal controversially disallowed for offside against Nigeria at the 2014 World Cup, my country's first ever appearance at the tournament.",
        },
    },
    "oscar_brazil": {
        "clue_set": {
            1: "I won the Silver Ball at the 2011 FIFA Under-20 World Cup in Colombia, scoring a hat-trick in the final as my country beat Portugal 3-2 from 2-1 down.",
        },
        "story": "Oscar was Brazil's golden boy. The São Paulo academy graduate who came through Internacional, lit up the FIFA U-20 World Cup in 2011 with a hat-trick in the final, and was sold to Chelsea at twenty for around £25 million. He won two Premier League titles and the Europa League at Stamford Bridge before, in January 2017 aged twenty-five, taking a £60 million Asian-record move to Shanghai SIPG on £400,000-a-week wages and effectively vanishing from elite European football. The 2014 World Cup at home was bookended by his clipped toe-poke against Croatia in the opener and his lone goal in the 7-1 humiliation by Germany. Retired April 2026, aged thirty-four, after a health problem was detected in pre-season screening.",
    },
    "arjen_robben": {
        "clue_set": {
            3: "Iker Casillas stuck out a leg to save my one-on-one in the 2010 World Cup final. Andrés Iniesta won it for Spain in extra time.",
        },
        "didYouKnow_set": {
            0: "Iker Casillas saved his one-on-one in the 2010 World Cup final. Andrés Iniesta scored the winner for Spain in extra time.",
        },
    },
    "diego_forlan": {
        "clue_set": {
            2: "It took me nine months and thirteen Premier League games to score my first goal.",
            3: "I won the European Golden Shoe twice, with two different Spanish clubs.",
            4: "I won the Golden Ball as best player at the 2010 World Cup, finishing as joint top scorer on five goals with Müller, Villa and Sneijder.",
        },
        "story_replacements": [
            ("eight months and twenty-seven games", "nine months and thirteen Premier League games"),
        ],
        "didYouKnow_set": {
            0: "He won the Golden Ball as best player at the 2010 World Cup, finishing as joint top scorer on 5 goals with Thomas Müller, David Villa and Wesley Sneijder.",
        },
    },
    "james_rodriguez": {
        "clue_set": {
            1: "I have played for clubs on Merseyside, in Munich and in Madrid.",
        },
        "story_replacements": [
            ("He scored seventeen in his first season under Carlo Ancelotti.",
             "He scored seventeen across all competitions in his first season under Carlo Ancelotti."),
        ],
    },
    "tim_howard": {
        "story": "Tim Howard spent a decade at Everton, more than 350 Premier League games as the Toffees' goalkeeper from 2006 to 2016. Before that, Sir Alex Ferguson had signed him from the New York MetroStars in 2003 to replace Fabien Barthez at Manchester United, where he won the FA Cup in his first season before losing his place. The defining game came at the 2014 World Cup in Salvador, where he made sixteen saves over 120 minutes against Belgium, the most by any goalkeeper in any World Cup match since records began in 1966. The United States still lost 2-1 in extra time. He is his country's most-capped goalkeeper ever.",
    },
    "wout_weghorst": {
        "story": "A 6'6\" striker who started in the Dutch second tier with FC Emmen and didn't make his Eredivisie debut until twenty-one. Wout Weghorst then became one. Fifty-nine Bundesliga goals at Wolfsburg, second only to Robert Lewandowski during his stint. A £12 million transfer to Burnley in January 2022 produced two Premier League goals in twenty appearances as the Clarets were relegated. An emergency loan to Manchester United under fellow Dutchman Erik ten Hag the next season won him his first trophy at thirty, the EFL Cup. At the 2022 World Cup he came off the bench in the quarter-final against Argentina and scored twice in the last twelve minutes to force extra time, a back-post header and then an audacious low free-kick finish in stoppage time. The Netherlands lost on penalties.",
    },
    "keisuke_honda": {
        "story_replacements": [
            ("he was briefly head coach of Cambodia while still playing for Botafogo",
             "he was briefly general manager of Cambodia while still playing for Botafogo"),
        ],
    },
    "maxi_rodriguez": {
        "story": "La Fiera, the Beast. Maxi Rodríguez made his name in eight seasons in La Liga with Espanyol and Atlético Madrid (he didn't feature in Atlético's 2009-10 Europa League win), then signed for Liverpool in 2010 on a free transfer. He scored hat-tricks against Birmingham and Fulham in the same Premier League season. He played in three World Cups for Argentina, scored Goal of the Tournament with an extra-time volley at the 2006 round of 16 against Mexico, and slotted home the decisive penalty in the 2014 semi-final shootout against the Netherlands. He started and ended his career at Newell's Old Boys in Rosario, twenty-two years apart.",
    },
    "joe_cole": {
        "story_replacements": [
            ("Then five years at Chelsea under Mourinho and Ancelotti",
             "Then seven years at Chelsea under Mourinho and Ancelotti"),
        ],
    },
    "maicon": {
        "story_replacements": [
            ("Manchester City signed him in 2012 as a marquee replacement for Pablo Zabaleta. One season later he was gone.",
             "Manchester City signed him in 2012 to compete at right-back. One season later he was gone, never having dislodged Pablo Zabaleta."),
            ("ended at San Marino's Tre Penne at the age of forty-one",
             "ended at San Marino's Tre Penne in his thirty-ninth year"),
        ],
    },
    "serge_aurier": {
        "story_replacements": [
            ("Three seasons of Ligue 1 titles and domestic cups followed",
             "Three seasons of Ligue 1 success and domestic cups followed"),
        ],
    },
    "youri_djorkaeff": {
        "clue_set": {
            4: "In the 1998 World Cup final, I insisted on taking the corner that Zinedine Zidane headed home for our second goal. I told him to 'stay here, you're good with the head'.",
        },
        "story_replacements": [
            ("won the UEFA Cup in 1998 alongside Ronaldo, scoring in the final",
             "won the UEFA Cup in 1998 alongside Ronaldo"),
            ("His father Jean captained France and played at the 1966 World Cup",
             "His father Jean played for France at the 1966 World Cup"),
        ],
        "honours_replacements": [
            ("UEFA Cup (Inter, 1997–98), scored in the final", "UEFA Cup (Inter, 1997–98)"),
        ],
        "didYouKnow_set": {
            0: "He took the corner in the 1998 World Cup final that Zinedine Zidane headed in for France's second goal. He had told Zidane to 'stay here, you're good with the head'.",
            2: "His father Jean Djorkaeff played for France at the 1966 World Cup.",
        },
    },
    "davor_suker": {
        "clue_set": {
            3: "I won the Champions League with Real Madrid in 1997–98, weeks before that World Cup.",
        },
        "story_replacements": [
            ("two months before the 1998 World Cup", "weeks before the 1998 World Cup"),
        ],
        "didYouKnow_set": {
            1: "Weeks before the 1998 World Cup he won the Champions League with Real Madrid.",
        },
    },
}


# ============================================================================
# Helpers
# ============================================================================
report = {"applied": 0, "skipped": 0, "errors": []}

def apply_clue_set(player, fixes):
    """Replace clue at index with new string. Index is 0-based."""
    for i, new in (fixes.get("clue_set") or {}).items():
        if 0 <= i < len(player["clues"]):
            old = player["clues"][i]
            if old != new:
                player["clues"][i] = new
                report["applied"] += 1
                print(f"  • {player['id']} clue[{i}] replaced")
            else:
                report["skipped"] += 1

def apply_story_replacements(player, fixes):
    for old, new in fixes.get("story_replacements", []):
        if old in player["story"]:
            player["story"] = player["story"].replace(old, new)
            report["applied"] += 1
            print(f"  • {player['id']} story sub: '{old[:40]}…'")
        else:
            report["skipped"] += 1
            print(f"  ◦ {player['id']} story sub NOT FOUND: '{old[:40]}…'")

def apply_full_story(player, fixes):
    if "story" in fixes:
        if player["story"] != fixes["story"]:
            player["story"] = fixes["story"]
            report["applied"] += 1
            print(f"  • {player['id']} story REPLACED in full")
        else:
            report["skipped"] += 1

def apply_honours(player, fixes):
    for old, new in fixes.get("honours_replacements", []):
        replaced = False
        for i, h in enumerate(player.get("honours", [])):
            if old in h:
                player["honours"][i] = h.replace(old, new)
                replaced = True
                report["applied"] += 1
                print(f"  • {player['id']} honour[{i}] sub: '{old[:40]}…'")
                break
        if not replaced:
            report["skipped"] += 1
            print(f"  ◦ {player['id']} honour sub NOT FOUND: '{old[:40]}…'")

def apply_didYouKnow(player, fixes):
    for i, new in (fixes.get("didYouKnow_set") or {}).items():
        if "didYouKnow" not in player:
            continue
        if 0 <= i < len(player["didYouKnow"]):
            old = player["didYouKnow"][i]
            if old != new:
                player["didYouKnow"][i] = new
                report["applied"] += 1
                print(f"  • {player['id']} didYouKnow[{i}] replaced")
            else:
                report["skipped"] += 1

def apply_to_player(player, fixes):
    apply_clue_set(player, fixes)
    apply_full_story(player, fixes)
    apply_story_replacements(player, fixes)
    apply_honours(player, fixes)
    apply_didYouKnow(player, fixes)


# ============================================================================
# Update content.json (Android + iOS share schema)
# ============================================================================
def update_content_json(path):
    print(f"\n→ {path}")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for p in data["footballers"]:
        if p["id"] in FIXES:
            apply_to_player(p, FIXES[p["id"]])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ============================================================================
# Update web players.js (only clues live here, plus name/country/etc.)
# ============================================================================
def update_players_js():
    print(f"\n→ {WEB_PL}")
    with open(WEB_PL, encoding="utf-8") as f:
        src = f.read()
    m = re.search(r"window\.PLAYERS\s*=\s*(\[.*\])\s*;?\s*\Z", src, re.DOTALL)
    players = json.loads(m.group(1))
    for p in players:
        if p["id"] in FIXES:
            # Only clue_set applies here
            for i, new in (FIXES[p["id"]].get("clue_set") or {}).items():
                if 0 <= i < len(p["clues"]):
                    if p["clues"][i] != new:
                        p["clues"][i] = new
                        report["applied"] += 1
                        print(f"  • {p['id']} clue[{i}] replaced (web)")
                    else:
                        report["skipped"] += 1
    new_src = "window.PLAYERS = " + json.dumps(players, ensure_ascii=False, indent=2) + ";\n"
    with open(WEB_PL, "w", encoding="utf-8") as f:
        f.write(new_src)


# ============================================================================
# Update web bios.js (story, honours, didYouKnow live here)
# ============================================================================
def update_bios_js():
    print(f"\n→ {WEB_BIO}")
    with open(WEB_BIO, encoding="utf-8") as f:
        src = f.read()
    m = re.search(r"window\.BIOS\s*=\s*(\{.*\})\s*;?\s*\Z", src, re.DOTALL)
    bios = json.loads(m.group(1))
    for pid, fixes in FIXES.items():
        if pid not in bios:
            continue
        bio = bios[pid]
        # Apply story full-rewrite or substitutions
        if "story" in fixes:
            if bio.get("story") != fixes["story"]:
                bio["story"] = fixes["story"]
                report["applied"] += 1
                print(f"  • {pid} story REPLACED (web)")
        for old, new in fixes.get("story_replacements", []):
            if old in bio.get("story", ""):
                bio["story"] = bio["story"].replace(old, new)
                report["applied"] += 1
                print(f"  • {pid} story sub (web)")
        # Honours
        for old, new in fixes.get("honours_replacements", []):
            for i, h in enumerate(bio.get("honours", [])):
                if old in h:
                    bio["honours"][i] = h.replace(old, new)
                    report["applied"] += 1
                    print(f"  • {pid} honour[{i}] sub (web)")
                    break
        # didYouKnow
        for i, new in (fixes.get("didYouKnow_set") or {}).items():
            if 0 <= i < len(bio.get("didYouKnow", [])):
                if bio["didYouKnow"][i] != new:
                    bio["didYouKnow"][i] = new
                    report["applied"] += 1
                    print(f"  • {pid} didYouKnow[{i}] replaced (web)")
    new_src = "window.BIOS = " + json.dumps(bios, ensure_ascii=False, indent=2) + ";\n"
    with open(WEB_BIO, "w", encoding="utf-8") as f:
        f.write(new_src)


# ============================================================================
# Run
# ============================================================================
if __name__ == "__main__":
    update_content_json(ANDROID)
    update_content_json(IOS)
    update_players_js()
    update_bios_js()
    print(f"\n{'=' * 50}")
    print(f"Applied: {report['applied']}    Skipped (already-applied or not-found): {report['skipped']}")
    if report["errors"]:
        print("Errors:", report["errors"])
