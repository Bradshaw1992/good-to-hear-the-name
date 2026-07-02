#!/usr/bin/env python3
"""Insert 53 v1.6 players into content.json (Days 72-124).

WC-themed (Days 72-76): Daniele De Rossi, Steven Nzonzi, Sami Khedira,
Mats Hummels, Luca Toni.

Normal v1.6 (Days 77-124): 48 players in the user-confirmed shuffled order
sourced from /tmp/shuffled_48.txt.

Existing Days 72-77 players (Carvalho, Tioté, Icardi, Essien, Bullard,
Phillips) are displaced to Days 125-130 (kept in roster, just moved past
the new v1.6 batch).

Reads from planning/v1.6_final_clues.md, v1.6_bios.md, v1.6_videos.md.
Writes Android + iOS content.json. clubs / honours / didYouKnow left
empty per user; numbers derived from clue 1 stats.

Run: scripts/.venv/bin/python scripts/insert_v1_6.py
"""
import json
import os
import re
import subprocess
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANDROID = os.path.join(ROOT, "app/src/main/assets/content.json")
IOS = os.path.join(ROOT, "ios/GoodToHearTheName/GoodToHearTheName/Resources/content.json")
PLANNING = os.path.join(ROOT, "planning")
FINAL_CLUES = os.path.join(PLANNING, "v1.6_final_clues.md")
BIOS = os.path.join(PLANNING, "v1.6_bios.md")
VIDEOS = os.path.join(PLANNING, "v1.6_videos.md")
SHUFFLED = "/tmp/shuffled_48.txt"

WC_PLAYERS = ["Daniele De Rossi", "Steven Nzonzi", "Sami Khedira", "Mats Hummels", "Luca Toni"]

COUNTRY_FLAGS = {
    "Italy": "🇮🇹", "France": "🇫🇷", "Germany": "🇩🇪", "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "Republic of Ireland": "🇮🇪", "Ireland": "🇮🇪", "Brazil": "🇧🇷",
    "Trinidad and Tobago": "🇹🇹", "Bulgaria": "🇧🇬", "South Korea": "🇰🇷",
    "Nigeria": "🇳🇬", "Ivory Coast": "🇨🇮", "Spain": "🇪🇸", "Netherlands": "🇳🇱",
    "Sweden": "🇸🇪", "Argentina": "🇦🇷", "Belgium": "🇧🇪", "Czech Republic": "🇨🇿",
    "Finland": "🇫🇮", "Israel": "🇮🇱", "Russia": "🇷🇺", "Australia": "🇦🇺",
    "Wales": "🏴󠁧󠁢󠁷󠁬󠁳󠁿",
}

# Map player display name -> id (matches silhouette filenames)
NAME_TO_ID = {
    "Daniele De Rossi": "daniele_de_rossi",
    "Steven Nzonzi": "steven_nzonzi",
    "Sami Khedira": "sami_khedira",
    "Mats Hummels": "mats_hummels",
    "Luca Toni": "luca_toni",
    "Matt Le Tissier": "matt_le_tissier",
    "Robbie Keane": "robbie_keane",
    "Dwight Yorke": "dwight_yorke",
    "Dimitar Berbatov": "dimitar_berbatov",
    "Park Ji-sung": "park_ji_sung",
    "Nwankwo Kanu": "nwankwo_kanu",
    "Adriano": "adriano",
    "Yaya Touré": "yaya_toure",
    "Dimitri Payet": "dimitri_payet",
    "Wilfried Bony": "wilfried_bony",
    "Bojan Krkić": "bojan_krkic",
    "Aaron Lennon": "aaron_lennon",
    "Olof Mellberg": "olof_mellberg",
    "Sami Hyypiä": "sami_hyypia",
    "Walter Samuel": "walter_samuel",
    "Wayne Bridge": "wayne_bridge",
    "Joleon Lescott": "joleon_lescott",
    "Thomas Vermaelen": "thomas_vermaelen",
    "Florent Malouda": "florent_malouda",
    "David Villa": "david_villa",
    "Clarence Seedorf": "clarence_seedorf",
    "Michael Ballack": "michael_ballack",
    "Fabien Barthez": "fabien_barthez",
    "Ruud van Nistelrooy": "ruud_van_nistelrooy",
    "Tomáš Rosický": "tomas_rosicky",
    "Henrik Larsson": "henrik_larsson",
    "Jamie Carragher": "jamie_carragher",
    "Ledley King": "ledley_king",
    "Yossi Benayoun": "yossi_benayoun",
    "Owen Hargreaves": "owen_hargreaves",
    "Jermain Defoe": "jermain_defoe",
    "Darren Bent": "darren_bent",
    "Andrey Arshavin": "andrey_arshavin",
    "Heurelho Gomes": "heurelho_gomes",
    "Jonathan Woodgate": "jonathan_woodgate",
    "Michael Carrick": "michael_carrick",
    "Damien Duff": "damien_duff",
    "Stewart Downing": "stewart_downing",
    "Yohan Cabaye": "yohan_cabaye",
    "Mark Viduka": "mark_viduka",
    "Esteban Cambiasso": "esteban_cambiasso",
    "Marco Reus": "marco_reus",
    "Aaron Ramsey": "aaron_ramsey",
    "Daley Blind": "daley_blind",
    "Lucas Moura": "lucas_moura",
    "Andros Townsend": "andros_townsend",
    "Andy Carroll": "andy_carroll",
    "Memphis Depay": "memphis_depay",
}

# Aliases per player (lowercase). Always include full name lowercase + last name
ALIASES_EXTRA = {
    "daniele_de_rossi": ["de rossi", "rossi"],
    "steven_nzonzi": ["nzonzi"],
    "sami_khedira": ["khedira"],
    "mats_hummels": ["hummels"],
    "luca_toni": ["toni"],
    "matt_le_tissier": ["le tissier", "le god"],
    "robbie_keane": ["keane"],
    "dwight_yorke": ["yorke"],
    "dimitar_berbatov": ["berbatov"],
    "park_ji_sung": ["park", "ji sung park", "ji-sung park"],
    "nwankwo_kanu": ["kanu"],
    "adriano": ["l'imperatore", "imperatore", "the emperor"],
    "yaya_toure": ["yaya", "toure", "yaya toure"],
    "dimitri_payet": ["payet"],
    "wilfried_bony": ["bony"],
    "bojan_krkic": ["bojan", "krkic", "bojan krkic"],
    "aaron_lennon": ["lennon"],
    "olof_mellberg": ["mellberg"],
    "sami_hyypia": ["hyypia", "hyypiä"],
    "walter_samuel": ["samuel", "the wall", "el muro"],
    "wayne_bridge": ["bridge"],
    "joleon_lescott": ["lescott"],
    "thomas_vermaelen": ["vermaelen", "the verminator"],
    "florent_malouda": ["malouda"],
    "david_villa": ["villa", "el guaje", "guaje"],
    "clarence_seedorf": ["seedorf"],
    "michael_ballack": ["ballack"],
    "fabien_barthez": ["barthez"],
    "ruud_van_nistelrooy": ["van nistelrooy", "nistelrooy", "ruud"],
    "tomas_rosicky": ["rosicky", "rosický", "little mozart"],
    "henrik_larsson": ["larsson"],
    "jamie_carragher": ["carragher", "carra"],
    "ledley_king": ["king", "ledley"],
    "yossi_benayoun": ["benayoun", "yossi"],
    "owen_hargreaves": ["hargreaves"],
    "jermain_defoe": ["defoe"],
    "darren_bent": ["bent"],
    "andrey_arshavin": ["arshavin"],
    "heurelho_gomes": ["gomes", "heurelho"],
    "jonathan_woodgate": ["woodgate"],
    "michael_carrick": ["carrick"],
    "damien_duff": ["duff"],
    "stewart_downing": ["downing"],
    "yohan_cabaye": ["cabaye"],
    "mark_viduka": ["viduka"],
    "esteban_cambiasso": ["cambiasso", "cuchu"],
    "marco_reus": ["reus"],
    "aaron_ramsey": ["ramsey"],
    "daley_blind": ["blind"],
    "lucas_moura": ["moura", "lucas"],
    "andros_townsend": ["townsend"],
    "andy_carroll": ["carroll"],
    "memphis_depay": ["depay", "memphis"],
}


# ---------- Parsers ----------

def parse_clues_file():
    """Return dict: name -> {country, position, era, clues}"""
    with open(FINAL_CLUES) as f:
        text = f.read()
    entries = {}
    # Split into sections per "## " heading
    sections = re.split(r'(?m)^## ', text)
    for section in sections[1:]:  # skip preamble
        lines = section.split('\n')
        header = lines[0].strip()
        # strip "(Day NN)" suffix if present
        name = re.sub(r'\s*\(Day \d+\)\s*$', '', header).strip()
        # Find Country | Position | Era line
        country = position = era = None
        clues = []
        for line in lines[1:]:
            line = line.strip()
            if line.startswith('Country:'):
                m = re.match(r'Country:\s*(.+?)\s*\|\s*Position:\s*(.+?)\s*\|\s*Era:\s*(.+?)\s*$', line)
                if m:
                    country = m.group(1).strip()
                    position = m.group(2).strip()
                    era = m.group(3).strip()
            else:
                m = re.match(r'^(\d+)\.\s*(.+)$', line)
                if m:
                    clue_text = m.group(2)
                    # strip HTML comments
                    clue_text = re.sub(r'<!--.*?-->', '', clue_text).strip()
                    clues.append(clue_text)
        if country and len(clues) >= 5:
            entries[name] = {
                "country": country,
                "position": position,
                "era": era,
                "clues": clues[:5],
            }
    return entries


def parse_bios_file():
    """Return dict: name -> story text"""
    with open(BIOS) as f:
        text = f.read()
    entries = {}
    pat = re.compile(r'(?m)^## (?P<name>[^\n]+?)\s*\n(?P<body>.*?)(?=^## |\Z)', re.S)
    for m in pat.finditer(text):
        name = m.group("name").strip()
        body = m.group("body").strip()
        # remove any embedded headings / blank lines
        body = re.sub(r'\n+', ' ', body).strip()
        entries[name] = body
    return entries


def parse_videos_file():
    """Return dict: name (accent-stripped lowercase) -> url"""
    with open(VIDEOS) as f:
        text = f.read()
    entries = {}
    pat = re.compile(r'(?m)^## (?P<name>[^\n]+?)\s*\nURL:\s*(?P<url>\S+)', re.S)
    for m in pat.finditer(text):
        name = m.group("name").strip()
        url = m.group("url").strip()
        key = strip_accents(name).lower()
        entries[key] = url
    return entries


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def pluralise(n, singular, plural=None):
    return singular if n == 1 else (plural or singular + "s")


def derive_numbers(clue1, country):
    """Sensible `numbers` string from clue 1. Handles three formats:
      A) WC stat: "...playing N games and scoring M goals."
      B) Normal:  "...I played N times for my country, scoring M goals."
      C) Singular: "I played 1 time for my country, scoring 0 goals."
    Pluralisation is correct for 1 goal / 1 cap / 1 game.
    """
    # Format A: World Cup
    m = re.search(r'playing\s+(\d+)\s+games?\s+and\s+scoring\s+(\d+)\s+goals?', clue1)
    if m and 'World Cup' in clue1:
        games, goals = int(m.group(1)), int(m.group(2))
        return f"{goals} {pluralise(goals, 'goal')} in {games} World Cup {pluralise(games, 'game')} for {country}"
    # Format B / C: caps + goals for country
    m = re.search(r'played\s+(\d+)\s+times?\s+for my country,\s+scoring\s+(\d+)\s+goals?', clue1)
    if m:
        caps, goals = int(m.group(1)), int(m.group(2))
        return f"{goals} {pluralise(goals, 'goal')} in {caps} {pluralise(caps, 'cap')} for {country}"
    return ""


def build_aliases(player_id, name):
    name_lower = name.lower()
    name_stripped = strip_accents(name_lower)
    last = name_stripped.split()[-1]
    base = [name_lower]
    if name_stripped != name_lower:
        base.append(name_stripped)
    if last not in base:
        base.append(last)
    base.extend(ALIASES_EXTRA.get(player_id, []))
    # dedupe preserving order
    seen = set()
    out = []
    for a in base:
        if a not in seen:
            seen.add(a)
            out.append(a)
    return out


def build_player(name, clues_data, bios_data, videos_data):
    pid = NAME_TO_ID[name]
    info = clues_data[name]
    country = info["country"]
    era = info["era"].replace("-", "–")  # use en-dash
    flag = COUNTRY_FLAGS.get(country, "")
    if not flag:
        raise ValueError(f"No flag for country: {country!r} ({name})")
    story = bios_data.get(name)
    if not story:
        raise ValueError(f"No bio found for {name}")
    video_key = strip_accents(name).lower()
    youtube = videos_data.get(video_key, "")
    numbers = derive_numbers(info["clues"][0], country)

    return {
        "id": pid,
        "name": name,
        "country": country,
        "countryFlag": flag,
        "years": era,
        "aliases": build_aliases(pid, name),
        "clues": info["clues"],
        "image": f"{pid}.jpg",
        "silhouette": f"{pid}.jpg",
        "position": info["position"],
        "yearsActive": era,
        "story": story,
        "youtube": youtube,
        "clubs": [],
        "honours": [],
        "numbers": numbers,
        "didYouKnow": [],
    }


# ---------- Main ----------

def main():
    clues_data = parse_clues_file()
    bios_data = parse_bios_file()
    videos_data = parse_videos_file()

    print(f"Parsed {len(clues_data)} clue entries")
    print(f"Parsed {len(bios_data)} bio entries")
    print(f"Parsed {len(videos_data)} video entries")

    # Shuffled order for 48 normal players
    with open(SHUFFLED) as f:
        shuffled_normal = [l.strip() for l in f if l.strip()]
    assert len(shuffled_normal) == 48, f"Expected 48 in shuffle, got {len(shuffled_normal)}"

    # Build all 53 entries
    wc_entries = [build_player(name, clues_data, bios_data, videos_data) for name in WC_PLAYERS]
    normal_entries = [build_player(name, clues_data, bios_data, videos_data) for name in shuffled_normal]

    # Load existing content
    with open(ANDROID) as f:
        data = json.load(f)
    existing = data["footballers"]

    # First 71 unchanged (Days 1-71)
    preserved = existing[:71]
    # Existing Days 72-77 to displace (6 players)
    displaced = existing[71:77]

    # Fix Ricardo Carvalho years (was 1997-2017, correct is 1997-2018)
    for p in displaced:
        if p["id"] == "ricardo_carvalho" and p["years"].endswith("2017"):
            p["years"] = p["years"].replace("2017", "2018")
            p["yearsActive"] = p["yearsActive"].replace("2017", "2018") if p.get("yearsActive", "").endswith("2017") else p.get("yearsActive", "")
            print(f"  Fixed Carvalho years: 2017 → 2018")

    # Build new ordered list
    new_list = preserved + wc_entries + normal_entries + displaced
    data["footballers"] = new_list

    print(f"\nNew roster:")
    print(f"  Days 1-71: existing {len(preserved)} players (unchanged)")
    print(f"  Days 72-76: WC-themed {len(wc_entries)} players (NEW)")
    print(f"  Days 77-124: normal v1.6 {len(normal_entries)} players (NEW, shuffled)")
    print(f"  Days 125-130: displaced {len(displaced)} players ({', '.join(p['name'] for p in displaced)})")
    print(f"  Total: {len(new_list)} players (was 77)")

    # Sanity: ids unique
    ids = [p["id"] for p in new_list]
    if len(ids) != len(set(ids)):
        from collections import Counter
        dupes = [k for k, v in Counter(ids).items() if v > 1]
        raise SystemExit(f"DUPLICATE IDs: {dupes}")

    # Write Android
    with open(ANDROID, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"\nWrote Android: {ANDROID}")

    # Copy to iOS
    with open(IOS, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Wrote iOS: {IOS}")


if __name__ == "__main__":
    main()
