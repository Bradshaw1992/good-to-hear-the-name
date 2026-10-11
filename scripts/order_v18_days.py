#!/usr/bin/env python3
"""Order the 86 new players across days 193-278 (2026-11-14 to 2027-02-07).

Priorities:
  1. keep cross-referencing players far apart, so one day's clue does not
     give away another day that falls close by
  2. no two consecutive days with the same country or the same position
  3. spread countries, positions and eras, and keep the six goalkeepers apart
  4. avoid back-to-back players whose careers centre on the same club

Hill climbing. A swap only changes pairs touching the two moved slots, so the
soft score is updated from those two windows instead of all 86 players. The
clash term is only a dozen pairs, so it is recomputed whole each time.
Fixed seed, so re-running gives the same order.
"""
import json
import random
from datetime import date, timedelta

BUILD = "planning/v1_8_build"
EPOCH = date(2026, 5, 5)
START = 193
SEED = 20261114
CLASH_MIN_GAP = 21
WINDOW = 7
RESTARTS = 25
PATIENCE = 4000

# Christmas Day is index 234. Crouch is the most purely enjoyable reveal here.
PINS = {234: "Peter Crouch"}

# "Marcelo" in these two clue sets is Marcelo Bielsa, not our Marcelo.
BIELSA = {frozenset(("Kalvin Phillips", "Marcelo")),
          frozenset(("Marcelo", "Patrick Bamford"))}

W_COUNTRY = {1: 120, 2: 50, 3: 25}
W_POSITION = {1: 90, 2: 35, 3: 15}
W_DECADE = {1: 20, 2: 8}


def attrs(p):
    return (p["country"], p["position"], int(p["years"][:4]) // 10,
            frozenset(p["clubs"]))


def pen(a, b, d):
    """Penalty for two players sitting d days apart."""
    s = 0
    if a[0] == b[0]:
        s += W_COUNTRY.get(d, 8)
    if a[1] == b[1]:
        s += W_POSITION.get(d, 4)
        if a[1] == "Goalkeeper" and d < 10:
            s += 300
    if a[2] == b[2]:
        s += W_DECADE.get(d, 0)
    if d <= 2 and a[3] & b[3]:
        s += 60 if d == 1 else 20
    return s


def soft_total(seq):
    n = len(seq)
    return sum(pen(seq[i], seq[j], j - i)
               for i in range(n) for j in range(i + 1, min(i + WINDOW + 1, n)))


def window(seq, i, skip):
    """Penalties between slot i and its neighbours, optionally skipping one."""
    n = len(seq)
    lo, hi = max(0, i - WINDOW), min(n, i + WINDOW + 1)
    return sum(pen(seq[i], seq[k], abs(k - i))
               for k in range(lo, hi) if k != i and k != skip)


def clash_total(at, clashes):
    return sum(400 * (CLASH_MIN_GAP - gap)
               for gap in (abs(at[a] - at[b]) for a, b in clashes)
               if gap < CLASH_MIN_GAP)


def main():
    players = json.load(open(f"{BUILD}/new_players.json"))
    clashes = [tuple(c) for c in json.load(open(f"{BUILD}/clashes.json"))
               if frozenset(c) not in BIELSA]
    by_name = {p["name"]: p for p in players}
    A = {name: attrs(p) for name, p in by_name.items()}

    n = len(players)
    pinned = {i - START: name for i, name in PINS.items()}
    movable = [p["name"] for p in players if p["name"] not in pinned.values()]
    free = [i for i in range(n) if i not in pinned]

    rng = random.Random(SEED)
    best, best_score = None, None

    for _ in range(RESTARTS):
        names = [None] * n
        for i, nm in pinned.items():
            names[i] = nm
        shuffled = movable[:]
        rng.shuffle(shuffled)
        it = iter(shuffled)
        for i in range(n):
            if names[i] is None:
                names[i] = next(it)

        seq = [A[x] for x in names]
        at = {x: i for i, x in enumerate(names)}
        soft = soft_total(seq)
        clash = clash_total(at, clashes)

        stale = 0
        while stale < PATIENCE:
            i, j = rng.sample(free, 2)
            skip_i = j if abs(i - j) <= WINDOW else -1

            before = window(seq, i, skip_i) + window(seq, j, -1)
            seq[i], seq[j] = seq[j], seq[i]
            names[i], names[j] = names[j], names[i]
            at[names[i]], at[names[j]] = i, j
            after = window(seq, i, skip_i) + window(seq, j, -1)

            new_soft = soft - before + after
            new_clash = clash_total(at, clashes)
            if new_soft + new_clash <= soft + clash:
                if new_soft + new_clash < soft + clash:
                    stale = 0
                else:
                    stale += 1
                soft, clash = new_soft, new_clash
            else:
                seq[i], seq[j] = seq[j], seq[i]
                names[i], names[j] = names[j], names[i]
                at[names[i]], at[names[j]] = i, j
                stale += 1

        total = soft + clash
        if best_score is None or total < best_score:
            best, best_score = names[:], total
            # sanity: the incremental score must match a full recount
            full = soft_total([A[x] for x in names]) + clash_total(
                {x: k for k, x in enumerate(names)}, clashes)
            assert full == total, f"incremental score drifted: {full} vs {total}"

    report(best, best_score, clashes, A)


def report(names, total, clashes, A):
    at = {x: i for i, x in enumerate(names)}
    print(f"score {total}")
    print(f"\nclash spacing (target {CLASH_MIN_GAP}+ days apart):")
    for gap, a, b in sorted((abs(at[a] - at[b]), a, b) for a, b in clashes):
        print(f"  {gap:3d} days  {a} / {b}"
              + ("" if gap >= CLASH_MIN_GAP else "   <-- TOO CLOSE"))

    adj_c = [(names[i], names[i + 1]) for i in range(len(names) - 1)
             if A[names[i]][0] == A[names[i + 1]][0]]
    adj_p = [(names[i], names[i + 1]) for i in range(len(names) - 1)
             if A[names[i]][1] == A[names[i + 1]][1]]
    print(f"\nadjacent same country: {len(adj_c)}   adjacent same position: {len(adj_p)}")
    for a, b in adj_c + adj_p:
        print(f"  {a} / {b}")

    json.dump(names, open(f"{BUILD}/day_order.json", "w"), indent=1)
    with open(f"{BUILD}/day_order.md", "w") as f:
        f.write("# v1.8 day order (days 194-279)\n\n")
        for i, nm in enumerate(names):
            d = EPOCH + timedelta(days=START + i)
            star = "   <- Christmas Day" if (START + i) in PINS else ""
            f.write(f"{START + i:3d}  {d:%a %d %b %Y}  {nm:26} "
                    f"{A[nm][0]:20} {A[nm][1]}{star}\n")
    print(f"\nwrote {BUILD}/day_order.json and day_order.md")


if __name__ == "__main__":
    main()
