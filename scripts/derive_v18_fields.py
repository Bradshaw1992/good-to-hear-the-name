#!/usr/bin/env python3
"""Derive the mechanical content.json fields from the researched metadata.

Produces, for each of the 86 players: id, aliases, numbers, kickoff, years, yearsActive,
countryFlag, image, silhouette. Formats are copied exactly from the shipped 193 so the
new entries are indistinguishable:

  kickoff (capped)   "I was born on the 5th of August 1989. I played 19 times for my
                      country, scoring 1 goal."
  kickoff (uncapped) "I was born on the 31st of December 1960. I was never capped by my
                      country."
  numbers            "0 goals in 30 caps for Jamaica"   (singular for 1 goal / 1 cap)

The country is deliberately never named in the kickoff line, per the Kick-off design.
"""
import json, re, sys, unicodedata
from datetime import date

META = 'planning/v1_8_build/metadata.json'
OUT = 'planning/v1_8_build/derived.json'
CONTENT = 'app/src/main/assets/content.json'

MONTHS = ["January","February","March","April","May","June","July","August",
          "September","October","November","December"]

# Accented spellings worth accepting as answers, since the metadata is plain ASCII
ACCENTS = {
 "Ngolo Kante":"n'golo kanté","Jussi Jaaskelainen":"jussi jääskeläinen",
 "Angel Di Maria":"ángel di maría","Gonzalo Higuain":"gonzalo higuaín",
 "Nemanja Matic":"nemanja matić","Emmanuel Eboue":"emmanuel eboué","Raul":"raúl",
 "Nemanja Vidic":"nemanja vidić","Kim Kallstrom":"kim källström",
 "Frederic Kanoute":"frédéric kanouté","Joaquin":"joaquín","Victor Valdes":"víctor valdés",
 "Juan Roman Riquelme":"juan román riquelme","Hernan Crespo":"hernán crespo",
 "Juan Pablo Angel":"juan pablo ángel","Thomas Gravesen":"thomas gravesen",
 "Helder Postiga":"hélder postiga","Raul Meireles":"raúl meireles",
 "Pascal Gross":"pascal groß","Oriol Romeu":"oriol romeu","Luis Garcia":"luis garcía",
 "Santi Cazorla":"santi cazorla","Kaka":"kaká","Dida":"dida",
}


# Countries in the v1.8 batch that do not appear in the shipped 193, so have no flag yet.
# Scotland uses the GB subdivision flag, matching how England is already stored.
NEW_FLAGS = {
    "Ecuador": "\U0001F1EA\U0001F1E8",
    "Scotland": "\U0001F3F4\U000E0067\U000E0062\U000E0073\U000E0063\U000E0074\U000E007F",
    "Mali": "\U0001F1F2\U0001F1F1",
    "DR Congo": "\U0001F1E8\U0001F1E9",
    "Denmark": "\U0001F1E9\U0001F1F0",
}



EN_DASH = "\u2013"


def en_dash(years):
    """All 193 shipped records use an en dash in the years range. Match them."""
    return years.replace("-", EN_DASH)

def pid(n):
    n = unicodedata.normalize('NFKD', n).encode('ascii','ignore').decode()
    n = n.replace("'", "").replace("-", " ")
    return re.sub(r'[^a-z0-9]+', '_', n.lower()).strip('_')


def ordinal(d):
    if 11 <= d <= 13: return f"{d}th"
    return f"{d}{ {1:'st',2:'nd',3:'rd'}.get(d % 10, 'th') }"


def kickoff(dob, caps, goals):
    y, m, d = (int(x) for x in dob.split('-'))
    born = f"I was born on the {ordinal(d)} of {MONTHS[m-1]} {y}."
    if caps == 0:
        return f"{born} I was never capped by my country."
    g = "1 goal" if goals == 1 else f"{goals} goals"
    return f"{born} I played {caps} times for my country, scoring {g}."


def numbers(caps, goals, country):
    if caps == 0:
        return f"Never capped by {country}"
    g = "1 goal" if goals == 1 else f"{goals} goals"
    c = "1 cap" if caps == 1 else f"{caps} caps"
    return f"{g} in {c} for {country}"


def aliases(name):
    base = unicodedata.normalize('NFKD', name).encode('ascii','ignore').decode()
    out = [base.lower()]
    parts = base.split()
    if len(parts) > 1:
        out.append(parts[-1].lower())                      # surname
        if len(parts) > 2:
            out.append(f"{parts[0]} {parts[-1]}".lower())   # first + surname
    acc = ACCENTS.get(name)
    if acc and acc not in out:
        out.append(acc)
    return list(dict.fromkeys(out))


def main():
    meta = json.load(open(META))
    flags = {}
    for p in json.load(open(CONTENT))['footballers']:
        flags.setdefault(p['country'], p['countryFlag'])
    for c, f in NEW_FLAGS.items():
        flags.setdefault(c, f)

    out, missing_flag = [], []
    for p in meta:
        i = pid(p['name'])
        flag = flags.get(p['country'])
        if not flag:
            missing_flag.append((p['name'], p['country']))
        out.append({
            "id": i,
            "name": p['name'],
            "country": p['country'],
            "countryFlag": flag,
            "years": en_dash(p['yearsActive']),
            "yearsActive": en_dash(p['yearsActive']),
            "aliases": aliases(p['name']),
            "image": f"{i}.jpg",
            "silhouette": f"{i}.jpg",
            "position": p['position'],
            "kickoff": kickoff(p['dob'], p['caps'], p['goals']),
            "numbers": numbers(p['caps'], p['goals'], p['country']),
            "honours": p['honours'],
            "didYouKnow": p['didYouKnow'],
            "clubs": p['clubs'],
        })
    json.dump(sorted(out, key=lambda x: x['name']), open(OUT,'w'), indent=1, ensure_ascii=False)
    print(f"derived {len(out)} players -> {OUT}")
    if missing_flag:
        print("\ncountries with no flag in the shipped set (need adding):")
        for n,c in missing_flag: print(f"  {n}: {c}")


if __name__ == "__main__":
    main()
