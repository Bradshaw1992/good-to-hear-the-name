#!/usr/bin/env python3
"""Generate 1080x1920 portrait PNG frames for an Instagram Reel.

Each frame is a still — assemble into a Reel inside CapCut (or iMovie) using
the timings printed at the end of the run. Frames match the brand language of
the square IG posts: cream + ink + green, same top bar.

Run: scripts/.venv/bin/python scripts/make_reel_frames.py [player_id]
     (defaults to first config below)
Output: marketing_print/reel_frames/<player_id>/
"""
import os
import sys
import glob
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
SILS = os.path.join(DOCS, "silhouettes")
IMGS = os.path.join(DOCS, "images")

CREAM = (244, 239, 230)
INK   = (22, 38, 28)
GREEN = (15, 122, 62)
MUTED = (110, 120, 115)

W, H = 1080, 1920
PAD = 70

# IG Reels safe band — researched June 2026, cross-checked across multiple sources.
# Reels playback overlays:
#   top ~250px (status bar + IG nav + username/audio pill)
#   bottom ~350px (caption up to 4 lines, audio attribution, follow CTA)
#   right ~210px (like/comment/share/save/profile action column)
# Profile grid thumb crops centred 3:4 (keeps y=240..1680) and 1:1 (keeps y=420..1500).
# Everything critical must sit inside the rectangle below to survive all surfaces.
SAFE_LEFT   = 90
SAFE_TOP    = 500           # content (silhouette, hooks) starts here
SAFE_RIGHT  = 870
SAFE_BOTTOM = 1450          # content ends here (well above the 1570 caption floor)
BRAND_BAR_Y = 430           # brand bar sits above content but inside grid crop band

# ----- per-player reel configs -----
CONFIGS = {
    "diego_forlan": {
        "day": 42,
        "hook_top": "PREMIER LEAGUE FLOP.",
        "hook_bottom": "WORLD CUP LEGEND.",
        "tom_opener": "World cup icon who got his big move after a breakout world cup.",
    },
    "joe_cole": {
        "day": 50,
        "hook_top": "DIPPING VOLLEY.",
        "hook_bottom": "ENGLAND HERO.",
        "tom_opener": "Scorer of one of today's World Cup team's great goals.",
    },
    "maicon": {
        "day": 51,
        "hook_top": "INTER TREBLE WINNER.",
        "hook_bottom": "SKINNED BY A TEENAGER.",
        "tom_opener": "Today's player was famously skinned by a teenager.",
    },
    "serge_aurier": {
        "day": 52,
        "hook_top": "BANNED BY HIS OWN CLUB.",
        "hook_bottom": "PSG TO FOREST.",
        "tom_opener": "Today's player got banned by his own club for what he said about his manager on a live video stream.",
    },
    "youri_djorkaeff": {
        "day": 53,
        "hook_top": "WORLD CUP AND EUROS WINNER.",
        "hook_bottom": "BOLTON CULT HERO.",
        "tom_opener": "Today's player is a cult hero in the Premier League.",
    },
    "mario_gotze": {
        "day": 25,
        "hook_top": "BAYERN MUNICH SUB.",
        "hook_bottom": "WORLD CUP WINNER.",
        "tom_opener": "A world cup winner is today's player. How many clues will it take you to guess him?",
    },
    "el_hadji_diouf": {
        "day": 43,
        "hook_top": "WORLD CUP BREAKOUT.",
        "hook_bottom": "PREMIER LEAGUE FLOP.",
        "tom_opener": "World cup icon who got his big move after a breakout world cup.",
    },
    "victor_moses": {
        "day": 29,
        "hook_top": "FIVE LOAN SPELLS.",
        "hook_bottom": "PREMIER LEAGUE CHAMPION.",
        "tom_opener": "A real test today for those with elite ball knowledge. How many clues will it take?",
    },
    "edin_dzeko": {
        "day": 39,
        "hook_top": "BUNDESLIGA TOP SCORER.",
        "hook_bottom": "PREMIER LEAGUE CHAMPION.",
        "tom_opener": "How good is your football knowledge? Five clues to guess this player.",
    },
    "james_rodriguez": {
        "day": 44,
        "hook_top": "WORLD CUP GOLDEN BOOT.",
        "hook_bottom": "REAL MADRID NUMBER 10.",
        "tom_opener": "Scorer of one of the World Cup's great goals.",
    },
    "pavel_nedved": {
        "day": 45,
        "hook_top": "ONE WORLD CUP.",
        "hook_bottom": "LOST A EUROS FINAL.",
        "tom_opener": "Today is a tough one. One World Cup, lost a Euros final. Who is this football legend?",
    },
    "tim_howard": {
        "day": 46,
        "hook_top": "16 SAVES IN ONE GAME.",
        "hook_bottom": "WORLD CUP RECORD HOLDER.",
        "tom_opener": "A World Cup performance so good it changed a Wikipedia page.",
    },
    "wout_weghorst": {
        "day": 47,
        "hook_top": "BOOKED BEFORE HE PLAYED.",
        "hook_bottom": "SCORED TWICE OFF THE BENCH.",
        "tom_opener": "Today's player was booked at a World Cup before he even came on. Then he scored twice.",
    },
    "keisuke_honda": {
        "day": 48,
        "hook_top": "THREE WORLD CUPS.",
        "hook_bottom": "RUSSIAN LEAGUE CHAMPION.",
        "tom_opener": "Three World Cups, four goals, and a Russian league title in between.",
    },
    "maxi_rodriguez": {
        "day": 49,
        "hook_top": "GOAL OF THE TOURNAMENT.",
        "hook_bottom": "WORLD CUP RUNNER-UP.",
        "tom_opener": "Today's player scored one of the greatest World Cup goals, against a 2026 host nation.",
    },
    "chris_wood": {
        "day": 54,
        "hook_top": "AT THIS WORLD CUP.",
        "hook_bottom": "UNBEATEN AT THE LAST ONE.",
        "tom_opener": "Today's player is at this World Cup. The last one he played in, his country didn't lose a single game.",
    },
    "mascherano": {
        "day": 55,
        "hook_top": "WON EVERYTHING.",
        "hook_bottom": "LOST THE BIG ONE.",
        "tom_opener": "Today's player won everything in club football and lost the biggest game of his country's career in extra time.",
    },
    "sneijder": {
        "day": 56,
        "hook_top": "BALLON D'OR RUNNER-UP.",
        "hook_bottom": "TREBLE WINNER.",
        "tom_opener": "Today's player came second in the Ballon d'Or in the year he won the treble and lost a World Cup final.",
    },
    "griezmann": {
        "day": 57,
        "hook_top": "REJECTED BY EVERY ACADEMY.",
        "hook_bottom": "WORLD CUP WINNER.",
        "tom_opener": "Today's player was rejected by every academy as a teenager. Came back to win the World Cup.",
    },
    "ashley_young": {
        "day": 58,
        "hook_top": "MOCKED FOR DIVING.",
        "hook_bottom": "TITLES IN TWO COUNTRIES.",
        "tom_opener": "Today's player was mocked his whole career for going down too easy. Won league titles in two countries.",
    },
    "morientes": {
        "day": 59,
        "hook_top": "REPLACED BY THE BRAZILIAN RONALDO.",
        "hook_bottom": "THREE CHAMPIONS LEAGUES.",
        "tom_opener": "Today's player got replaced at his club by the Brazilian Ronaldo. Won three Champions Leagues anyway.",
    },
    "giroud": {
        "day": 60,
        "hook_top": "SCORPION KICK PUSKÁS WINNER.",
        "hook_bottom": "RECORD INTERNATIONAL SCORER.",
        "tom_opener": "Today's player scored the goal of the year with a scorpion kick on New Year's Day.",
    },
    "asamoah_gyan": {
        "day": 61,
        "hook_top": "120TH MINUTE PENALTY.",
        "hook_bottom": "HIT THE BAR.",
        "tom_opener": "Today's player took a penalty in the last minute of a World Cup quarter-final. It hit the bar.",
    },
    "nigel_de_jong": {
        "day": 62,
        "hook_top": "KUNG-FU KICK IN A WORLD CUP FINAL.",
        "hook_bottom": "AND STAYED ON THE PITCH.",
        "tom_opener": "Today's player kicked an opponent in the chest in a World Cup final, and somehow stayed on the pitch.",
    },
    "lucio": {
        "day": 63,
        "hook_top": "LOST THREE FINALS IN ONE SEASON.",
        "hook_bottom": "THEN WON THE LOT.",
        "tom_opener": "Today's player lost three finals in a single season, then went on to win a World Cup and a treble.",
    },
    "tim_krul": {
        "day": 64,
        "hook_top": "BROUGHT ON IN THE LAST MINUTE",
        "hook_bottom": "OF EXTRA TIME.",
        "tom_opener": "Today's player was brought on in the last minute of extra time of a World Cup quarter-final.",
    },
    # --- reminder-to-play reels (cover_tease only): difficult, non-revealing covers.
    # Deliberately give LESS away as the days progress (followers growing over time).
    "anelka": {
        "day": 65,
        "cover_tease": "Today's player was at the heart of a World Cup controversy.",
    },
    "sofyan_amrabat": {
        "day": 66,
        "cover_tease": "Today's player was the engine of a historic World Cup run.",
    },
    "chiellini": {
        "day": 67,
        "cover_tease": "Today's player was part of one of football's most infamous moments.",
    },
    "pepe_portugal": {
        "day": 68,
        "cover_tease": "Today's player was still making history long after most retire.",
    },
    "mustafi": {
        "day": 69,
        "cover_tease": "Today's player owns a winner's medal you might have forgotten.",
    },
    "koulibaly": {
        "day": 70,
        "cover_tease": "Can you name today's player from five clues?",
    },
    # Days 71-81: covers lean lighter still. Vague curiosity hooks, no event that
    # points at the player. Just enough intrigue to stop the scroll.
    "gattuso": {
        "day": 71,
        "cover_tease": "Today's player left everything on the pitch, and sometimes a bit more.",
    },
    "daniele_de_rossi": {
        "day": 72,
        "cover_tease": "Today's player was one city's favourite son.",
    },
    "steven_nzonzi": {
        "day": 73,
        "cover_tease": "Today's player won the biggest prize of all, then all but vanished.",
    },
    "sami_khedira": {
        "day": 74,
        "cover_tease": "Today's player's biggest night was over before it began.",
    },
    "mats_hummels": {
        "day": 75,
        "cover_tease": "Today's player knew the highest high and the cruellest low.",
    },
    "luca_toni": {
        "day": 76,
        "cover_tease": "Today's player was every defender's worst nightmare.",
    },
    "robbie_keane": {
        "day": 77,
        "cover_tease": "Today's player never went anywhere quietly.",
    },
    "heurelho_gomes": {
        "day": 78,
        "cover_tease": "Today's player went from a punchline to a hero.",
    },
    "damien_duff": {
        "day": 79,
        "cover_tease": "Today's player could beat you before you'd blinked.",
    },
    "matt_le_tissier": {
        "day": 80,
        "cover_tease": "Today's player had a gift the game never fully used.",
    },
    "clarence_seedorf": {
        "day": 81,
        "cover_tease": "Today's player holds a record no one else ever will.",
    },
    "ruud_van_nistelrooy": {
        "day": 82,
        "cover_tease": "Today's player only ever needed one chance.",
    },
    "walter_samuel": {
        "day": 83,
        "cover_tease": "Today's player was the wall strikers couldn't get past.",
    },
    "olof_mellberg": {
        "day": 84,
        "cover_tease": "Today's player was the quiet backbone of every side he joined.",
    },
    "yaya_toure": {
        "day": 85,
        "cover_tease": "Today's player could take over a game whenever he pleased.",
    },
    "yossi_benayoun": {
        "day": 86,
        "cover_tease": "Today's player suited up for clubs that can't stand each other.",
    },
    "lucas_moura": {
        "day": 87,
        "cover_tease": "Today's player had one magical night no one saw coming.",
    },
    "memphis_depay": {
        "day": 88,
        "cover_tease": "Today's player has a whole second career you'd never guess.",
    },
    "andy_carroll": {
        "day": 89,
        "cover_tease": "Today's player carried a price tag he could never live up to.",
    },
    "nwankwo_kanu": {
        "day": 90,
        "cover_tease": "Today's player moved like nothing you'd ever seen.",
    },
    "aaron_ramsey": {
        "day": 91,
        "cover_tease": "Today's player came back from an injury that should have finished him.",
    },
    "aaron_lennon": {
        "day": 92,
        "cover_tease": "Today's player was as quick as anyone the league had seen.",
    },
    "michael_ballack": {
        "day": 93,
        "cover_tease": "Today's player finished second more times than seemed fair.",
    },
    "ledley_king": {
        "day": 94,
        "cover_tease": "Today's player was better on one leg than most are on two.",
    },
    "wayne_bridge": {
        "day": 95,
        "cover_tease": "Today's player made his biggest headline off the pitch.",
    },
    "bojan_krkic": {
        "day": 96,
        "cover_tease": "Today's player was the next big thing that never quite was.",
    },
    "andros_townsend": {
        "day": 97,
        "cover_tease": "Today's player once scored the goal of the whole season.",
    },
    "dimitar_berbatov": {
        "day": 98,
        "cover_tease": "Today's player made the game look effortless, almost lazy.",
    },
    "wilfried_bony": {
        "day": 99,
        "cover_tease": "Today's player was unstoppable, right up until the big move.",
    },
    "park_ji_sung": {
        "day": 100,
        "cover_tease": "Today's player seemed to run twice as far as anyone else.",
    },
    "mark_viduka": {
        "day": 101,
        "cover_tease": "Today's player was all power, with a touch no one expected.",
    },
    "owen_hargreaves": {
        "day": 102,
        "cover_tease": "Today's player could have played for three different countries.",
    },
    "yohan_cabaye": {
        "day": 103,
        "cover_tease": "Today's player pulled every string from midfield.",
    },
    "thomas_vermaelen": {
        "day": 104,
        "cover_tease": "Today's player belonged to a golden generation that promised more than it won.",
    },
    "michael_carrick": {
        "day": 105,
        "cover_tease": "Today's player did the quiet work while others took the glory.",
    },
    "marco_reus": {
        "day": 106,
        "cover_tease": "Today's player was as gifted as he was unlucky.",
    },
    "esteban_cambiasso": {
        "day": 107,
        "cover_tease": "Today's player did his best work where nobody was looking.",
    },
    "adriano": {
        "day": 108,
        "cover_tease": "Today's player had a left foot like a sledgehammer.",
    },
    "jonathan_woodgate": {
        "day": 109,
        "cover_tease": "Today's player survived the most disastrous debut imaginable.",
    },
    "florent_malouda": {
        "day": 110,
        "cover_tease": "Today's player took a while to win everyone over, then never looked back.",
    },
    "dimitri_payet": {
        "day": 111,
        "cover_tease": "Today's player scored goals that made rival managers applaud.",
    },
    "daley_blind": {
        "day": 112,
        "cover_tease": "Today's player could slot in anywhere and never let you down.",
    },
    "sami_hyypia": {
        "day": 113,
        "cover_tease": "Today's player was a giant who never got his moment on the biggest stage.",
    },
    # --- Days 114-123: reel covers stay HARD (deliberately vague from the first frame),
    # while the IG picture hooks give a bit more away. See hook_text in make_instagram_posts.py.
    "stewart_downing": {
        "day": 114,
        "cover_tease": "Today's player never quite lived up to the hype.",
    },
    "fabien_barthez": {
        "day": 115,
        "cover_tease": "Today's player had ice in his veins on the biggest nights.",
    },
    "jermain_defoe": {
        "day": 116,
        "cover_tease": "Today's player was a born finisher who kept coming home.",
    },
    "david_villa": {
        "day": 117,
        "cover_tease": "Today's player always turned up when it mattered most.",
    },
    "henrik_larsson": {
        "day": 118,
        "cover_tease": "Today's player was worshipped at one club above all others.",
    },
    "darren_bent": {
        "day": 119,
        "cover_tease": "Today's player scored goals wherever he went, and never got his due.",
    },
    "andrey_arshavin": {
        "day": 120,
        "cover_tease": "Today's player had one unforgettable night in front of goal.",
    },
    "joleon_lescott": {
        "day": 121,
        "cover_tease": "Today's player overcame more than most to reach the top.",
    },
    "dwight_yorke": {
        "day": 122,
        "cover_tease": "Today's player made the big nights look like fun.",
    },
    "jamie_carragher": {
        "day": 123,
        "cover_tease": "Today's player left it all out there, every single game.",
    },
    # --- Days 125-134: reel covers stay HARD (vague from the first frame; the reel walks all 5 clues).
    "ricardo_carvalho": {
        "day": 125,
        "cover_tease": "Today's player was a defender the very best managers built around.",
    },
    "cheick_tiote": {
        "day": 126,
        "cover_tease": "Today's player scored a goal his fans will never forget.",
    },
    "mauro_icardi": {
        "day": 127,
        "cover_tease": "Today's player made as many headlines off the pitch as on it.",
    },
    "michael_essien": {
        "day": 128,
        "cover_tease": "Today's player was pure power in the middle of the park.",
    },
    "jimmy_bullard": {
        "day": 129,
        "cover_tease": "Today's player took the unlikeliest road to the top.",
    },
    "kevin_phillips": {
        "day": 130,
        "cover_tease": "Today's player just kept finding the net.",
    },
    "steve_bruce": {
        "day": 131,
        "cover_tease": "Today's player was a born leader at the back.",
    },
    "wilfried_zaha": {
        "day": 132,
        "cover_tease": "Today's player was a nightmare to defend against on his day.",
    },
    "thiago_alcantara": {
        "day": 133,
        "cover_tease": "Today's player made the middle of the pitch look like art.",
    },
    "titus_bramble": {
        "day": 134,
        "cover_tease": "Today's player could win it, or lose it, on any given day.",
    },
    "keylor_navas": {
        "day": 135,
        "cover_tease": "Today's player kept goal on the biggest nights of all.",
    },
    "ruud_gullit": {
        "day": 136,
        "cover_tease": "Today's player was once the biggest name in the game.",
    },
    "troy_deeney": {
        "day": 137,
        "cover_tease": "Today's player scored a goal an entire club will never forget.",
    },
    "javier_zanetti": {
        "day": 138,
        "cover_tease": "Today's player looked like he could play forever.",
    },
    "rafael_van_der_vaart": {
        "day": 139,
        "cover_tease": "Today's player made the game look effortlessly elegant.",
    },
    "shay_given": {
        "day": 140,
        "cover_tease": "Today's player was on the wrong end of a famous injustice.",
    },
    "robert_huth": {
        "day": 142,
        "cover_tease": "Today's player was part of the most unlikely triumph of all.",
    },
    "scott_parker": {
        "day": 143,
        "cover_tease": "Today's player shone brightest as his team fell apart.",
    },
    "emmanuel_adebayor": {
        "day": 144,
        "cover_tease": "Today's player once celebrated a goal in the most provocative way imaginable.",
    },
    "paolo_maldini": {
        "day": 145,
        "cover_tease": "Today's player gave everything to one club, for a very long time.",
    },
    "ross_barkley": {
        "day": 146,
        "cover_tease": "Today's player carried the hopes of his hometown.",
    },
    "samuel_etoo": {
        "day": 147,
        "cover_tease": "Today's player was a winning machine.",
    },
    "nani": {
        "day": 148,
        "cover_tease": "Today's player lived in the shadow of a countryman legend.",
    },
    "rory_delap": {
        "day": 149,
        "cover_tease": "Today's player had one weapon defenders genuinely feared.",
    },
    "fabio_da_silva": {
        "day": 150,
        "cover_tease": "Today's player had an identical twin who played too.",
    },
    "paolo_di_canio": {
        "day": 151,
        "cover_tease": "Today's player once chose sportsmanship over an open goal.",
    },
    "marc_albrighton": {
        "day": 152,
        "cover_tease": "Today's player was a free transfer who ended up winning it all.",
    },
    "leandro_paredes": {
        "day": 153,
        "cover_tease": "Today's player shared a pitch with the biggest names in the game.",
    },
    "nuno_espirito_santo": {
        "day": 154,
        "cover_tease": "Today's player is better known now for the dugout than the pitch.",
    },
    "ryan_bertrand": {
        "day": 155,
        "cover_tease": "Today's player's first big night was the biggest of all.",
    },
    "peter_odemwingie": {
        "day": 156,
        "cover_tease": "Today's player was involved in one of deadline day's funniest moments.",
    },
    "marek_hamsik": {
        "day": 157,
        "cover_tease": "Today's player rewrote the record books at one club.",
    },
    "richard_dunne": {
        "day": 158,
        "cover_tease": "Today's player holds a record most defenders would rather forget.",
    },
    "edinson_cavani": {
        "day": 159,
        "cover_tease": "Today's player once sent a global superstar home from a World Cup.",
    },
    "marc_overmars": {
        "day": 160,
        "cover_tease": "Today's player was lightning down the wing.",
    },
    "paul_ince": {
        "day": 161,
        "cover_tease": "Today's player broke barriers and crossed a great divide.",
    },
    # --- Throwback archive reels (launch-roster classics, Days 1-50). "This player" phrasing
    # instead of "Today's player" since these are reposted out of sequence.
    "batistuta": {
        "day": 10,
        "cover_tease": "This player scored for fun, and loved one club too much to leave.",
    },
}

PLAYER_ID = sys.argv[1] if len(sys.argv) > 1 else "diego_forlan"
if PLAYER_ID not in CONFIGS:
    raise SystemExit(f"no reel config for {PLAYER_ID}. add it to CONFIGS.")
cfg = CONFIGS[PLAYER_ID]
DAY = cfg["day"]
HOOK_TOP = cfg.get("hook_top", "")
HOOK_BOTTOM = cfg.get("hook_bottom", "")
TOM_OPENER = cfg.get("tom_opener", "")
# cover_tease: a single difficult, non-revealing line for the cover frame. When set
# it replaces the two-line HOOK_TOP/HOOK_BOTTOM (which tend to give the player away).
# Used for reminder-to-play reels aimed at existing followers.
COVER_TEASE = cfg.get("cover_tease", "")
URL_TEXT = f"goodtohearthename.co.uk?day={DAY}"

# How many clues the reel shows. Full walkthrough = 5. Teaser = 3 (withhold the giveaway
# clues, drive to the website to play the full puzzle). Override per run: REEL_CLUE_LIMIT=3
CLUE_LIMIT = int(os.environ.get("REEL_CLUE_LIMIT", "5"))

OUT = os.path.join(ROOT, "marketing_print", "reel_frames", PLAYER_ID)
os.makedirs(OUT, exist_ok=True)


def font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size, index=1 if bold else 0)
            except Exception:
                return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def wrap(text, fnt, max_w, draw):
    words = text.split()
    lines, cur = [], []
    for w in words:
        test = " ".join(cur + [w])
        bb = draw.textbbox((0, 0), test, font=fnt)
        if bb[2] - bb[0] <= max_w:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
                cur = [w]
            else:
                lines.append(w)
    if cur:
        lines.append(" ".join(cur))
    return lines


def center_text(draw, text, fnt, y, color=INK):
    bb = draw.textbbox((0, 0), text, font=fnt)
    w = bb[2] - bb[0]
    draw.text((W // 2 - w // 2, y), text, fill=color, font=fnt)


def fit_font(text, max_size, max_width, draw, bold=True):
    """Return the largest font (up to max_size) where text fits within max_width."""
    for size in range(max_size, 28, -2):
        f = font(size, bold=bold)
        bb = draw.textbbox((0, 0), text, font=f)
        if bb[2] - bb[0] <= max_width:
            return f
    return font(28, bold=bold)


def top_bar(canvas, draw):
    # Single-line centred brand strap — narrower than W to stay inside the right action column.
    f_top = font(28, bold=True)
    parts = [("FIVE CLUES.  FIVE GUESSES.", GREEN),
             ("   |   ", MUTED),
             ("GOOD TO HEAR THE NAME", INK)]
    # measure total width
    total = 0
    sizes = []
    for text, _ in parts:
        bb = draw.textbbox((0, 0), text, font=f_top)
        sizes.append(bb[2] - bb[0])
        total += bb[2] - bb[0]
    x = W // 2 - total // 2
    for (text, color), w in zip(parts, sizes):
        draw.text((x, BRAND_BAR_Y), text, fill=color, font=f_top)
        x += w


def blurred_fill(canvas, path, dim_factor=1.0):
    """Cover the entire canvas with a heavily blurred copy of the source.
    Optionally darkens with dim_factor < 1.0 (e.g. 0.45 for cold-open)."""
    img = Image.open(path).convert("RGB")
    iw, ih = img.size
    # cover (scale to fill, may crop)
    scale = max(W / iw, H / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    img = img.filter(ImageFilter.GaussianBlur(radius=40))
    if dim_factor < 1.0:
        img = img.point(lambda p: int(p * dim_factor))
    canvas.paste(img, ((W - nw) // 2, (H - nh) // 2))


def paste_silhouette(canvas, path, top, bottom):
    """Crisp silhouette pasted into a band, contained inside the horizontal safe zone."""
    sil = Image.open(path).convert("RGB")
    max_h = bottom - top
    max_w = SAFE_RIGHT - SAFE_LEFT
    sw, sh = sil.size
    scale = min(max_w / sw, max_h / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    sil = sil.resize((nw, nh), Image.LANCZOS)
    canvas.paste(sil, ((W - nw) // 2, top + (max_h - nh) // 2))


def paste_photo(canvas, path, top, bottom):
    img = Image.open(path).convert("RGB")
    max_h = bottom - top
    max_w = W - PAD * 2
    iw, ih = img.size
    scale = min(max_w / iw, max_h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    canvas.paste(img, ((W - nw) // 2, top + (max_h - nh) // 2))


# ---------- frame builders ----------

def frame_cold_open(out_name):
    """0.0 – 0.4s. Spoiler-flash. Dark blurred silhouette + giant hook text."""
    c = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(c)
    blurred_fill(c, os.path.join(SILS, f"{PLAYER_ID}.jpg"), dim_factor=0.35)
    # giant hook text, centered vertically
    f_hook = font(110, bold=True)
    lines = COLD_OPEN.split("\n")
    line_h = 130
    total_h = len(lines) * line_h
    y = H // 2 - total_h // 2
    for line in lines:
        center_text(d, line, f_hook, y, color=CREAM)
        y += line_h
    c.save(os.path.join(OUT, out_name), "PNG")
    print("wrote", out_name)


def frame_brand_tom(out_name):
    """Tom's Version cover. Caption opener as the hook, silhouette below.
    Editorial layout — full sentence wraps above the silhouette, no split contrast."""
    if not TOM_OPENER:
        return  # nothing to render for players without an opener configured
    c = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(c)
    top_bar(c, d)

    sil_path = os.path.join(SILS, f"{PLAYER_ID}.jpg")
    safe_w = SAFE_RIGHT - SAFE_LEFT

    # Caption opener text — auto-pick font size so the WHOLE sentence fits in
    # at most 4 lines, leaving the silhouette room below.
    chosen = None
    for size in range(56, 32, -2):
        f = font(size, bold=True)
        lines = wrap(TOM_OPENER, f, safe_w, d)
        if len(lines) <= 4:
            chosen = (f, lines, size)
            break
    if chosen is None:
        f = font(34, bold=True)
        chosen = (f, wrap(TOM_OPENER, f, safe_w, d)[:4], 34)
    f_text, lines, size = chosen
    line_h = int(size * 1.25)

    # text block sits in the upper portion of the safe band
    text_top = SAFE_TOP + 20
    cy = text_top
    for line in lines:
        center_text(d, line, f_text, cy, color=INK)
        cy += line_h

    # silhouette fills the rest of the safe band
    sil_top = cy + 30
    sil_bottom = SAFE_BOTTOM - 110
    paste_silhouette(c, sil_path, top=sil_top, bottom=sil_bottom)

    # bottom marker
    f_who = font(40, bold=True)
    center_text(d, "WHO IS IT?", f_who, SAFE_BOTTOM - 90, color=GREEN)
    f_day = font(28, bold=True)
    center_text(d, f"DAY {DAY}  ·  FIVE CLUES.  FIVE GUESSES.", f_day,
                SAFE_BOTTOM - 40, color=MUTED)

    c.save(os.path.join(OUT, out_name), "PNG")
    print("wrote", out_name)


def frame_brand(out_name):
    """Cold-scroll hook frame. All critical text sits in the IG safe band."""
    c = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(c)
    top_bar(c, d)

    sil_path = os.path.join(SILS, f"{PLAYER_ID}.jpg")
    safe_w = SAFE_RIGHT - SAFE_LEFT

    # Difficult, non-revealing cover: a single teasing sentence instead of the two
    # giveaway hooks. Editorial layout — sentence wraps above the full silhouette.
    if COVER_TEASE:
        chosen = None
        for size in range(60, 34, -2):
            f = font(size, bold=True)
            lines = wrap(COVER_TEASE, f, safe_w, d)
            if len(lines) <= 4:
                chosen = (f, lines, size)
                break
        if chosen is None:
            f = font(34, bold=True)
            chosen = (f, wrap(COVER_TEASE, f, safe_w, d)[:4], 34)
        f_text, lines, size = chosen
        line_h = int(size * 1.25)
        cy = SAFE_TOP + 20
        for line in lines:
            center_text(d, line, f_text, cy, color=INK)
            cy += line_h
        paste_silhouette(c, sil_path, top=cy + 30, bottom=SAFE_BOTTOM - 110)
        center_text(d, "WHO IS IT?", font(40, bold=True), SAFE_BOTTOM - 90, color=GREEN)
        center_text(d, f"DAY {DAY}  ·  FIVE CLUES.  FIVE GUESSES.", font(28, bold=True),
                    SAFE_BOTTOM - 40, color=MUTED)
        c.save(os.path.join(OUT, out_name), "PNG")
        print("wrote", out_name)
        return

    # hook lines auto-fit to the safe width so longer phrases don't overflow.
    f_top_hook = fit_font(HOOK_TOP, max_size=74, max_width=safe_w, draw=d)
    f_bot_hook = fit_font(HOOK_BOTTOM, max_size=74, max_width=safe_w, draw=d)

    # top hook line
    center_text(d, HOOK_TOP, f_top_hook, SAFE_TOP + 20, color=INK)

    # silhouette in the middle band
    paste_silhouette(c, sil_path, top=SAFE_TOP + 130, bottom=SAFE_BOTTOM - 180)

    # bottom hook line
    center_text(d, HOOK_BOTTOM, f_bot_hook, SAFE_BOTTOM - 150, color=GREEN)

    # day stamp just above the safe-bottom floor
    f_sub = font(30, bold=True)
    center_text(d, f"DAY {DAY}  ·  WHO IS IT?", f_sub,
                SAFE_BOTTOM - 50, color=MUTED)
    c.save(os.path.join(OUT, out_name), "PNG")
    print("wrote", out_name)


def frame_clue(idx, clue_text, out_name):
    """Clean cream bg, silhouette band, clue text. Sits entirely in the safe band."""
    c = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(c)
    sil_path = os.path.join(SILS, f"{PLAYER_ID}.jpg")

    top_bar(c, d)

    # 'CLUE N OF 5' label
    f_label = font(38, bold=True)
    center_text(d, f"CLUE {idx} OF 5", f_label, SAFE_TOP + 10, color=GREEN)

    # silhouette in the upper portion of the safe band
    paste_silhouette(c, sil_path, top=SAFE_TOP + 70, bottom=SAFE_TOP + 520)

    # clue text — sits in the lower portion, max width = safe width
    safe_w = SAFE_RIGHT - SAFE_LEFT
    f_clue = font(46)
    clue_lines = wrap(f"“{clue_text}”", f_clue, safe_w, d)[:5]
    line_h = 60
    block_h = len(clue_lines) * line_h
    bottom_band_top = SAFE_TOP + 580
    bottom_band_bot = SAFE_BOTTOM - 80
    cy = bottom_band_top + ((bottom_band_bot - bottom_band_top - block_h) // 2)
    for line in clue_lines:
        center_text(d, line, f_clue, cy, color=INK)
        cy += line_h

    # day strip just above the safe-bottom floor
    f_day_small = font(30, bold=True)
    center_text(d, f"DAY {DAY}  ·  FROM THE ARCHIVE", f_day_small,
                SAFE_BOTTOM - 50, color=MUTED)

    c.save(os.path.join(OUT, out_name), "PNG")
    print("wrote", out_name)


def frame_endcard(out_name):
    """No-reveal end card. Leads with the comments-guessing CTA (the Reel's job is
    engagement + the follow, not the click), then a soft 'link in bio' website nudge.
    No day-specific URL: a Reel has no clickable link, so we point people to the bio."""
    c = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(c)
    sil_path = os.path.join(SILS, f"{PLAYER_ID}.jpg")

    top_bar(c, d)

    # silhouette occupies the upper portion of the safe band (still no reveal)
    paste_silhouette(c, sil_path, top=SAFE_TOP, bottom=SAFE_TOP + 420)

    safe_w = SAFE_RIGHT - SAFE_LEFT

    # tier 1: the primary ask — guess in the comments (keeps the mystery, drives engagement)
    base_y = SAFE_TOP + 470
    f_hook = font(46, bold=True)
    center_text(d, "THINK YOU KNOW HIM?", f_hook, base_y, color=INK)

    f_cta = fit_font("GUESS IN THE COMMENTS", max_size=56, max_width=safe_w, draw=d, bold=True)
    center_text(d, "GUESS IN THE COMMENTS", f_cta, base_y + 70, color=GREEN)

    # divider
    div_y = base_y + 175
    d.rectangle([(W // 2 - 80, div_y), (W // 2 + 80, div_y + 4)], fill=MUTED)

    # tier 2: soft website funnel — no clickable URL on a Reel, so point at the bio
    f_more = font(40, bold=True)
    center_text(d, "More than 50 to play.", f_more, div_y + 45, color=INK)

    f_more_sub = fit_font("A new one every day. Link in bio.",
                          max_size=36, max_width=safe_w, draw=d, bold=True)
    center_text(d, "A new one every day. Link in bio.", f_more_sub, div_y + 100, color=GREEN)

    c.save(os.path.join(OUT, out_name), "PNG")
    print("wrote", out_name)


def frame_endcard_teaser(out_name):
    """Teaser end card (3-clue reels). Withholds the answer and drives to the website to
    play the FULL puzzle. Keeps a light comments nudge, since comments still feed reach.
    No 'the missing clues are on the site' promise: the site plays fresh from clue 1."""
    c = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(c)
    sil_path = os.path.join(SILS, f"{PLAYER_ID}.jpg")

    top_bar(c, d)
    paste_silhouette(c, sil_path, top=SAFE_TOP, bottom=SAFE_TOP + 400)

    safe_w = SAFE_RIGHT - SAFE_LEFT
    base_y = SAFE_TOP + 450

    # primary ask: go and play the full thing (the answer lives on the site, not here)
    center_text(d, "STILL GUESSING?", font(46, bold=True), base_y, color=INK)
    f_cta = fit_font("PLAY THE FULL PUZZLE", max_size=58, max_width=safe_w, draw=d, bold=True)
    center_text(d, "PLAY THE FULL PUZZLE", f_cta, base_y + 70, color=GREEN)
    center_text(d, "Five clues, five guesses. Free.", font(34, bold=True), base_y + 150, color=INK)

    # divider
    div_y = base_y + 215
    d.rectangle([(W // 2 - 80, div_y), (W // 2 + 80, div_y + 4)], fill=MUTED)

    # website funnel (no clickable link on a Reel, so point at the bio) + light comment nudge
    center_text(d, "Link in bio  ·  goodtohearthename.co.uk", font(30, bold=True),
                div_y + 30, color=GREEN)
    f_nudge = fit_font("New player every day. Or guess in the comments.",
                       max_size=28, max_width=safe_w, draw=d, bold=True)
    center_text(d, "New player every day. Or guess in the comments.", f_nudge,
                div_y + 78, color=MUTED)

    c.save(os.path.join(OUT, out_name), "PNG")
    print("wrote", out_name)


# ---------- driver ----------

def load_player():
    with open(os.path.join(ROOT, "app/src/main/assets/content.json")) as f:
        d = json.load(f)
    for p in d["footballers"]:
        if p["id"] == PLAYER_ID:
            return p
    raise SystemExit(f"player {PLAYER_ID} not found")


if __name__ == "__main__":
    player = load_player()
    all_clues = player["clues"]
    clues = all_clues[:CLUE_LIMIT]
    teaser = CLUE_LIMIT < len(all_clues)

    # Clear stale frames first so a shorter (teaser) rebuild can't leave old clue4/clue5
    # frames behind for render_reel.py to pick up.
    for old in glob.glob(os.path.join(OUT, "*.png")):
        os.remove(old)

    frame_brand("01_brand.png")
    frame_brand_tom("01_brand_tom.png")
    for i, clue in enumerate(clues, start=1):
        frame_clue(i, clue, f"0{1+i}_clue{i}.png")
    if teaser:
        frame_endcard_teaser("07_endcard.png")
    else:
        frame_endcard("07_endcard.png")

    mode = f"{len(clues)}-clue teaser (drive to site)" if teaser else "full 5-clue walkthrough"
    manifest = [
        f"# Reel storyboard — {player['name']} (Day {DAY}) — {mode}",
        "Aspect: 1080x1920 portrait. Audio: stadium hum bed + soft cue under the end card.",
        f"Frames: 01_brand + {len(clues)} clue frames + 07_endcard.",
        "Render to MP4 with: scripts/render_reel.py " + PLAYER_ID + " (auto-detects the clue count).",
        "",
        ("Endcard: no reveal. Withholds the answer and points to the website to play the full "
         "puzzle; keeps a light comments nudge." if teaser
         else "Endcard: no reveal. Guess-in-comments CTA + link in bio."),
        "",
        f"Caption + hashtags: see marketing_print/reel_captions.txt for Day {DAY}.",
    ]
    manifest_path = os.path.join(OUT, "STORYBOARD.md")
    with open(manifest_path, "w") as f:
        f.write("\n".join(manifest))
    print(f"\nwrote {os.path.relpath(manifest_path, ROOT)}")
    print(f"\nDone ({mode}). Frames + storyboard in {os.path.relpath(OUT, ROOT)}/")
