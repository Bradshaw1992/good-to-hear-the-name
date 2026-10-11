#!/usr/bin/env python3
"""Merge a batch of researched player metadata into planning/v1_8_build/metadata.json.

Normalises on the way in, because the research agents return honours as season spans
("Serie A (Inter Milan, 2009-10)") while content.json uses a single year
("Champions League (Real Madrid, 2014)").

Usage:  python3 scripts/merge_v18_metadata.py batch.json
"""
import json, re, sys, os

STORE = 'planning/v1_8_build/metadata.json'
REQUIRED = {"name","dob","country","position","yearsActive","caps","goals","clubs","honours","didYouKnow"}


def single_year(honour):
    """'Serie A (Inter Milan, 2009-10)' -> 'Serie A (Inter Milan, 2010)'"""
    def fix(m):
        a, b = m.group(1), m.group(2)
        # 2009-10 -> 2010 ; 1999-2000 -> 2000
        end = b if len(b) == 4 else a[:2] + b if int(b) >= int(a[2:]) else str(int(a[:2]) + 1) + b
        return f", {end})"
    return re.sub(r", (\d{4})-(\d{2,4})\)$", fix, honour)


def main():
    incoming = json.load(open(sys.argv[1]))
    store = json.load(open(STORE)) if os.path.exists(STORE) else []
    by_name = {p["name"]: p for p in store}
    added = updated = 0
    problems = []
    for p in incoming:
        missing = REQUIRED - set(p)
        if missing:
            problems.append(f'{p.get("name","?")}: missing {sorted(missing)}')
            continue
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(p["dob"] or "")):
            problems.append(f'{p["name"]}: bad dob {p["dob"]!r}')
        if len(p["didYouKnow"]) != 3:
            problems.append(f'{p["name"]}: {len(p["didYouKnow"])} facts, expected 3')
        p["honours"] = [single_year(h) for h in p["honours"]]
        if len(p["honours"]) > 12:
            problems.append(f'{p["name"]}: {len(p["honours"])} honours, trim to the biggest 12')
        if p["name"] in by_name:
            by_name[p["name"]].update(p); updated += 1
        else:
            by_name[p["name"]] = p; added += 1
    out = sorted(by_name.values(), key=lambda x: x["name"])
    json.dump(out, open(STORE, 'w'), indent=1, ensure_ascii=False)
    print(f"added {added}, updated {updated}, total {len(out)} of 86")
    for pr in problems:
        print(f"  ! {pr}")


if __name__ == "__main__":
    main()
