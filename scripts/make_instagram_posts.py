#!/usr/bin/env python3
"""Generate 1080x1080 Instagram post images: silhouette + first clue + day reveal.

Daily-style (today's player): silhouette + clue + "Day X." + "WHO IS IT?"
Archive-style (past day reveal): silhouette + clue + "Day X." + player name reveal.

Run: scripts/.venv/bin/python scripts/make_instagram_posts.py
Output: marketing_print/instagram_posts/
"""
import os
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
SILS = os.path.join(DOCS, "silhouettes")
OUT = os.path.join(ROOT, "marketing_print", "instagram_posts")
os.makedirs(OUT, exist_ok=True)

CREAM = (244, 239, 230)
INK   = (22, 38, 28)
GREEN = (15, 122, 62)
MUTED = (110, 120, 115)

SIZE = 1080
PADDING = 60


def load_players():
    src = open(os.path.join(DOCS, "players.js")).read()
    src = src[src.index("[") : src.rstrip().rstrip(";").rindex("]") + 1]
    return {p["id"]: p for p in json.loads(src)}


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


def center_text(draw, text, font_, y, color=INK):
    bb = draw.textbbox((0, 0), text, font=font_)
    w = bb[2] - bb[0]
    draw.text((SIZE // 2 - w // 2, y), text, fill=color, font=font_)
    return bb[3] - bb[1]


def build_post(player, day, is_archive, out_name, hook_text=None):
    canvas = Image.new("RGB", (SIZE, SIZE), CREAM)
    draw = ImageDraw.Draw(canvas)

    # --- TOP BAR ---
    f_top = font(22, bold=True)
    draw.text((PADDING, PADDING), "FIVE CLUES.  FIVE GUESSES.",
              fill=GREEN, font=f_top)
    brand = "GOOD TO HEAR THE NAME"
    bb = draw.textbbox((0, 0), brand, font=f_top)
    draw.text((SIZE - PADDING - (bb[2] - bb[0]), PADDING),
              brand, fill=INK, font=f_top)

    # --- SILHOUETTE ---
    sil_path = os.path.join(SILS, f"{player['id']}.jpg")
    sil = Image.open(sil_path).convert("RGB")
    sil_top = 130
    sil_bottom = 720
    max_h = sil_bottom - sil_top
    max_w = SIZE - PADDING * 2
    sw, sh = sil.size
    scale = min(max_w / sw, max_h / sh)
    new_w, new_h = int(sw * scale), int(sh * scale)
    sil = sil.resize((new_w, new_h), Image.LANCZOS)
    canvas.paste(sil, ((SIZE - new_w) // 2,
                       sil_top + (max_h - new_h) // 2))

    # --- HOOK TEXT (centered) ---
    # If hook_text is provided, render it raw (third-person teaser).
    # Otherwise render the player's first in-app clue, wrapped in smart quotes.
    f_clue = font(28)
    clue_max_w = SIZE - PADDING * 4
    if hook_text:
        clue_lines = wrap(hook_text, f_clue, clue_max_w, draw)
    else:
        clue_lines = wrap(f"“{player['clues'][0]}”",
                          f_clue, clue_max_w, draw)
    cy = 750
    for line in clue_lines[:3]:
        center_text(draw, line, f_clue, cy, color=INK)
        cy += 38

    # --- DAY + WHO IS IT? hook (no answer revealed, ever) ---
    bottom_y = SIZE - PADDING - 120
    f_day = font(36, bold=True)
    center_text(draw, f"Day {day}.", f_day, bottom_y, color=INK)
    f_who = font(54, bold=True)
    center_text(draw, "WHO IS IT?", f_who, bottom_y + 50, color=GREEN)

    path = os.path.join(OUT, out_name)
    canvas.save(path, "JPEG", quality=92)
    print("wrote", os.path.relpath(path, ROOT))


# (player_id, day_number, is_archive_reveal, output_filename, hook_text)
# hook_text=None falls back to rendering the player's first in-app clue.
# Daily "today" posts can override with a third-person teaser; archives keep the in-app clue.
# 9am archive posts + 4pm daily posts for Sun 14 Jun - Tue 23 Jun (next 10 days)
POSTS = [
    # Daily today's-player posts, Days 50-63 (Tue 23 Jun – Mon 6 Jul). Tom's-style hint hooks.
    ("joe_cole",          50, False, "01_tue23_today_joecole_day50.jpg",
     "Scorer of one of today's World Cup team's great goals."),
    ("maicon",            51, False, "02_wed24_today_maicon_day51.jpg",
     "Today's player was famously skinned by a teenager."),
    ("serge_aurier",      52, False, "03_thu25_today_aurier_day52.jpg",
     "Today's player got banned by his own club for what he said about his manager on a live video stream."),
    ("youri_djorkaeff",   53, False, "04_fri26_today_djorkaeff_day53.jpg",
     "Today's player is a cult hero in the Premier League."),
    ("chris_wood",        54, False, "05_sat27_today_wood_day54.jpg",
     "Today's player is at this World Cup. The last one he played in, his country didn't lose a single game."),
    ("mascherano",        55, False, "06_sun28_today_mascherano_day55.jpg",
     "Today's player won everything in club football, then lost the biggest game of his country's career in extra time."),
    ("sneijder",          56, False, "07_mon29_today_sneijder_day56.jpg",
     "Today's player came second in the Ballon d'Or in the year he won the treble and lost a World Cup final."),
    ("griezmann",         57, False, "08_tue30_today_griezmann_day57.jpg",
     "Today's player was rejected by every French football academy as a teenager. He went on to win the World Cup."),
    ("ashley_young",      58, False, "09_wed01_today_young_day58.jpg",
     "Today's player won a Serie A title at 35, after a career most people thought was over."),
    ("morientes",         59, False, "10_thu02_today_morientes_day59.jpg",
     "Today's player scored in a Champions League knockout against the club that owned his contract."),
    ("giroud",            60, False, "11_fri03_today_giroud_day60.jpg",
     "Today's player won the World Cup without scoring a single goal in the tournament."),
    ("asamoah_gyan",      61, False, "12_sat04_today_gyan_day61.jpg",
     "Today's player missed a penalty in the last minute of a World Cup quarter-final that would've sent his country to the semis."),
    ("nigel_de_jong",     62, False, "13_sun05_today_dejong_day62.jpg",
     "Today's player kicked an opponent in the chest during a World Cup final, and somehow wasn't sent off."),
    ("lucio",             63, False, "14_mon06_today_lucio_day63.jpg",
     "Today's player won the World Cup and the Champions League, but at one club he lost three finals in a single season."),
    ("tim_krul",          64, False, "15_tue07_today_krul_day64.jpg",
     "Today's player was brought on in the last minute of extra time of a World Cup quarter-final."),
    ("anelka",            65, False, "16_wed08_today_anelka_day65.jpg",
     "Today's player sparked one of the greatest controversies in World Cup history."),
    ("sofyan_amrabat",    66, False, "17_thu09_today_amrabat_day66.jpg",
     "Today's player was the midfield heartbeat of the first African team ever to reach a World Cup semi-final."),
    ("chiellini",         67, False, "18_fri10_today_chiellini_day67.jpg",
     "Today's player was famously bitten by an opponent during a World Cup."),
    ("pepe_portugal",     68, False, "19_sat11_today_pepe_day68.jpg",
     "Today's player scored at a World Cup aged 39, the oldest man ever to score in a knockout game."),
    ("mustafi",           69, False, "20_sun12_today_mustafi_day69.jpg",
     "Today's player won the World Cup, then a £35m move made him a cult figure at a Premier League club for all the wrong reasons."),
    ("koulibaly",         70, False, "21_mon13_today_koulibaly_day70.jpg",
     "Today's player scored in the shootout that won his country its first ever Africa Cup of Nations."),
    ("gattuso",           71, False, "22_tue14_today_gattuso_day71.jpg",
     "Today's player won a World Cup and two Champions Leagues, and once headbutted an assistant manager on the touchline."),
    ("daniele_de_rossi",  72, False, "23_wed15_today_derossi_day72.jpg",
     "Today's player scored a penalty in the shootout that won a World Cup final, and spent eighteen years at one club in the capital."),
    ("steven_nzonzi",     73, False, "24_thu16_today_nzonzi_day73.jpg",
     "Today's player won the World Cup a few years after being Stoke City's player of the year."),
    # Day 74 (Khedira) is before today — posts as archive (see TODAY_DAY). Hook mirrors its reel cover.
    ("sami_khedira",      74, True,  "24b_fri17_archive_khedira_day74.jpg",
     "Today's player's biggest night was over before it began."),
    # --- Days 75+: hint-only hooks. No country, club, trophy or signature-moment tell.
    # Same line used on the reel cover (make_reel_frames.py CONFIGS). Just enough to stop the scroll.
    ("mats_hummels",      75, False, "25_sat18_today_hummels_day75.jpg",
     "Today's player knew the highest high and the cruellest low."),
    ("luca_toni",         76, False, "26_sun19_today_lucatoni_day76.jpg",
     "Today's player was every defender's worst nightmare."),
    ("robbie_keane",      77, False, "27_mon20_today_keane_day77.jpg",
     "Today's player never went anywhere quietly."),
    ("heurelho_gomes",    78, False, "28_tue21_today_gomes_day78.jpg",
     "Today's player went from a punchline to a hero."),
    ("damien_duff",       79, False, "29_wed22_today_duff_day79.jpg",
     "Today's player could beat you before you'd blinked."),
    ("matt_le_tissier",   80, False, "30_thu23_today_letissier_day80.jpg",
     "Today's player had a gift the game never fully used."),
    ("clarence_seedorf",  81, False, "31_fri24_today_seedorf_day81.jpg",
     "Today's player holds a record no one else ever will."),
    ("ruud_van_nistelrooy", 82, False, "32_sat25_today_vannistelrooy_day82.jpg",
     "Today's player only ever needed one chance."),
    ("walter_samuel",     83, False, "33_sun26_today_samuel_day83.jpg",
     "Today's player was the wall strikers couldn't get past."),
    ("olof_mellberg",     84, False, "34_mon27_today_mellberg_day84.jpg",
     "Today's player was the quiet backbone of every side he joined."),
    ("yaya_toure",        85, False, "35_tue28_today_yayatoure_day85.jpg",
     "Today's player could take over a game whenever he pleased."),
    ("yossi_benayoun",    86, False, "36_wed29_today_benayoun_day86.jpg",
     "Today's player suited up for clubs that can't stand each other."),
    ("lucas_moura",       87, False, "37_thu30_today_lucasmoura_day87.jpg",
     "Today's player had one magical night no one saw coming."),
    ("memphis_depay",     88, False, "38_fri31_today_memphis_day88.jpg",
     "Today's player has a whole second career you'd never guess."),
    ("andy_carroll",      89, False, "39_sat01aug_today_carroll_day89.jpg",
     "Today's player carried a price tag he could never live up to."),
    ("nwankwo_kanu",      90, False, "40_sun02aug_today_kanu_day90.jpg",
     "Today's player moved like nothing you'd ever seen."),
    ("aaron_ramsey",      91, False, "41_mon03aug_today_ramsey_day91.jpg",
     "Today's player came back from an injury that should have finished him."),
    ("aaron_lennon",      92, False, "42_tue04aug_today_lennon_day92.jpg",
     "Today's player was as quick as anyone the league had seen."),
    ("michael_ballack",   93, False, "43_wed05aug_today_ballack_day93.jpg",
     "Today's player finished second more times than seemed fair."),
    ("ledley_king",       94, False, "44_thu06aug_today_king_day94.jpg",
     "Today's player was better on one leg than most are on two."),
    ("wayne_bridge",      95, False, "45_fri07aug_today_bridge_day95.jpg",
     "Today's player made his biggest headline off the pitch."),
    ("bojan_krkic",       96, False, "46_sat08aug_today_bojan_day96.jpg",
     "Today's player was the next big thing that never quite was."),
    ("andros_townsend",   97, False, "47_sun09aug_today_townsend_day97.jpg",
     "Today's player once scored the goal of the whole season."),
    ("dimitar_berbatov",  98, False, "48_mon10aug_today_berbatov_day98.jpg",
     "Today's player made the game look effortless, almost lazy."),
    ("wilfried_bony",     99, False, "49_tue11aug_today_bony_day99.jpg",
     "Today's player was unstoppable, right up until the big move."),
    ("park_ji_sung",     100, False, "50_wed12aug_today_park_day100.jpg",
     "Today's player seemed to run twice as far as anyone else."),
    ("mark_viduka",      101, False, "51_thu13aug_today_viduka_day101.jpg",
     "Today's player was all power, with a touch no one expected."),
    ("owen_hargreaves",  102, False, "52_fri14aug_today_hargreaves_day102.jpg",
     "Today's player could have played for three different countries."),
    ("yohan_cabaye",     103, False, "53_sat15aug_today_cabaye_day103.jpg",
     "Today's player pulled every string from midfield."),
]

# Today's live puzzle day (epoch 2026-05-05 = Day 1). Anything earlier is captioned
# as "from the archive" with a ?day=N replay link; this day and later post as "today's puzzle".
# Bump this as the calendar advances so past days auto-flip to archive framing.
TODAY_DAY = 91


HOME_URL = "https://goodtohearthename.co.uk"

# Niche hashtag blocks per player. Edit / extend as the roster grows.
NICHE_TAGS = {
    "rafael_marquez":   "#worldcup2026 #mexico #fcbarcelona #worldcuplegends",
    "batistuta":        "#batigol #argentina #fiorentina #serieA",
    "mario_gotze":      "#worldcup2026 #germany #borussiadortmund #worldcuplegends",
    "abidal":           "#fcbarcelona #championsleague #francefootball #footballnostalgia",
    "falcao":           "#atleticomadrid #colombia #europaleague #2010sfootball",
    "edin_dzeko":       "#worldcup2026 #bosnia #manchestercity #romacf #internazionale",
    "ramires":          "#brazil #chelsea #premierleague #2010sfootball",
    "hatem_ben_arfa":   "#france #newcastleunited #cultheroes #ligue1",
    "antonio_cassano":  "#italy #serieA #fantantonio #realmadrid",
    "oscar_brazil":     "#worldcup2026 #brazil #chelsea #2010sfootball",
    "arjen_robben":     "#worldcup2026 #netherlands #bayernmunich #realmadrid",
    "diego_forlan":     "#worldcup2026 #uruguay #atleticomadrid #goldenboot2010",
    "el_hadji_diouf":   "#worldcup2026 #senegal #liverpoolfc #2002worldcup",
    "james_rodriguez":  "#worldcup2026 #colombia #realmadrid #goldenboot2014",
    "pavel_nedved":     "#worldcup2026 #czechrepublic #juventus #lazio #ballondor",
    "tim_howard":       "#worldcup2026 #usmnt #everton #manchesterunited #2014worldcup",
    "wout_weghorst":    "#worldcup2026 #netherlands #burnleyfc #manchesterunited",
    "keisuke_honda":    "#worldcup2026 #japan #acmilan #cskamoscow",
    "maxi_rodriguez":   "#worldcup2026 #argentina #liverpoolfc #atleticomadrid #newellsoldboys",
    "joe_cole":         "#worldcup2026 #england #chelseafc #westham #liverpoolfc",
    "maicon":           "#brazil #intermilan #seriea #worldcup2010",
    "serge_aurier":     "#ivorycoast #psg #tottenhamhotspur #nottinghamforest",
    "youri_djorkaeff":  "#worldcup98 #france #boltonwanderers #intermilan #euro2000",
    "chris_wood":       "#worldcup2026 #newzealand #burnleyfc #nottinghamforest #leedsunited",
    "mascherano":       "#worldcup2014 #argentina #fcbarcelona #liverpoolfc",
    "sneijder":         "#worldcup2010 #netherlands #intermilan #ajax #realmadrid",
    "griezmann":        "#worldcup2018 #france #atleticomadrid #fcbarcelona",
    "ashley_young":     "#worldcup2018 #england #manchesterunited #astonvilla #intermilan",
    "morientes":        "#spain #realmadrid #liverpoolfc #monaco #championsleague",
    "giroud":           "#worldcup2018 #france #arsenal #chelseafc #acmilan",
    "asamoah_gyan":     "#ghana #worldcup2010 #sunderlandafc #blackstars #africanfootball",
    "nigel_de_jong":    "#worldcup2010 #netherlands #manchestercity #acmilan #ajax",
    "lucio":            "#brazil #worldcup2002 #bayernmunich #intermilan #leverkusen",
    "tim_krul":         "#netherlands #worldcup2014 #newcastleunited #norwichcity",
    "anelka":           "#france #worldcup2010 #arsenal #chelseafc #realmadrid",
    "sofyan_amrabat":   "#morocco #worldcup2022 #fiorentina #manchesterunited #atlaslions",
    "chiellini":        "#italy #juventus #euro2020 #azzurri #seriea",
    "pepe_portugal":    "#portugal #realmadrid #worldcup2022 #selecao",
    "mustafi":          "#germany #arsenal #worldcup2014 #sampdoria",
    "koulibaly":        "#senegal #napoli #chelseafc #afcon #seriea",
    "gattuso":          "#italy #acmilan #worldcup2006 #rinogattuso #championsleague",
    "daniele_de_rossi": "#italy #asroma #worldcup2006 #azzurri #capitano",
    "steven_nzonzi":    "#france #stokecity #sevillafc #worldcup2018",
    "shevchenko":       "#ukraine #acmilan #chelseafc #ballondor #footballnostalgia",
    "trezeguet":        "#france #juventus #worldcup98 #euro2000 #serieA",
    "podolski":         "#worldcup2014 #germany #arsenal #1fckoln #poldi",
    "eidur_gudjohnsen": "#iceland #chelseafc #fcbarcelona #boltonwanderers #cultheroes",
    "antonio_di_natale": "#italy #udinese #serieA #capocannoniere #cultheroes",
    "diego_simeone":    "#argentina #atleticomadrid #lazio #internazionale #cholo",
    "emile_heskey":     "#england #liverpoolfc #astonvilla #leicestercity #premierleague",
    "mats_hummels":     "#germany #borussiadortmund #bayernmunich #worldcup2014 #diemannschaft",
    "luca_toni":        "#italy #bayernmunich #fiorentina #worldcup2006 #seriea",
    "robbie_keane":     "#republicofireland #tottenhamhotspur #premierleague #cotp #lastage",
    "sami_khedira":     "#germany #realmadrid #juventus #worldcup2014 #diemannschaft",
    "heurelho_gomes":   "#brazil #tottenhamhotspur #watfordfc #premierleague #goalkeeper",
    "damien_duff":      "#republicofireland #chelseafc #blackburnrovers #fulhamfc #premierleague",
    "matt_le_tissier":  "#england #southamptonfc #leggod #premierleague #thedell",
    "clarence_seedorf": "#netherlands #acmilan #realmadrid #internazionale #ajax",
    "ruud_van_nistelrooy": "#netherlands #manchesterunited #realmadrid #psv #premierleague",
    "walter_samuel":    "#argentina #internazionale #asroma #bocajuniors #seriea",
    "olof_mellberg":    "#sweden #astonvilla #juventus #olympiacos #premierleague",
    "yaya_toure":       "#ivorycoast #manchestercity #fcbarcelona #premierleague #cityzens",
    "yossi_benayoun":   "#israel #liverpoolfc #westham #chelseafc #arsenal",
    "lucas_moura":      "#brazil #tottenhamhotspur #psg #saopaulo #championsleague",
    "memphis_depay":    "#netherlands #psv #manchesterunited #olympiquelyonnais #atleticomadrid",
    "andy_carroll":     "#england #liverpoolfc #newcastleunited #westham #premierleague",
    "nwankwo_kanu":     "#nigeria #arsenal #portsmouthfc #ajax #internazionale",
    "aaron_ramsey":     "#wales #arsenal #juventus #premierleague #euro2016",
    "aaron_lennon":     "#england #tottenhamhotspur #evertonfc #premierleague #winger",
    "michael_ballack":  "#germany #chelseafc #bayernmunich #bayerleverkusen #diemannschaft",
    "ledley_king":      "#england #tottenhamhotspur #premierleague #coys #legend",
    "wayne_bridge":     "#england #chelseafc #manchestercity #southamptonfc #premierleague",
    "bojan_krkic":      "#spain #fcbarcelona #stokecity #lamasia #cultheroes",
    "andros_townsend":  "#england #crystalpalace #tottenhamhotspur #evertonfc #premierleague",
    "dimitar_berbatov": "#bulgaria #manchesterunited #tottenhamhotspur #bayerleverkusen #fulhamfc",
    "wilfried_bony":    "#ivorycoast #swanseacity #manchestercity #afcon #premierleague",
    "park_ji_sung":     "#southkorea #manchesterunited #psveindhoven #premierleague #asianfootball",
    "mark_viduka":      "#australia #leedsunited #middlesbrough #celticfc #socceroos",
    "owen_hargreaves":  "#england #manchesterunited #bayernmunich #championsleague #premierleague",
    "yohan_cabaye":     "#france #newcastleunited #crystalpalace #psg #lillelosc",
}

CORE_TAGS = (
    "#footballquiz #footballquizdaily #guesstheplayer #footballtrivia #soccerquiz "
    "#footballnostalgia #cultheroes #retrofootball "
    "#footballcommunity #footballcliches #thefootballramble"
)


def caption_for(player, day, is_today):
    # ?day=N pins the day on the site without revealing the player id in the URL
    pinned = f"{HOME_URL}?day={day}"
    if is_today:
        return f"""Day {day}. Today's puzzle.

Five clues. Five guesses. Most people need three.

Play it now: {pinned}

Made by a fan, for the obsessives."""
    return f"""Day {day} from the archive.

Five clues. Five guesses. Most people need three.

Play this exact puzzle: {pinned}

Today's puzzle in the link in bio. Made by a fan, for the obsessives."""


def hashtags_for(player):
    niche = NICHE_TAGS.get(player["id"], "")
    return f"{CORE_TAGS} {niche}".strip()


if __name__ == "__main__":
    players = load_players()
    caption_lines = ["# Instagram captions (paste-ready)\n"]
    for entry in POSTS:
        pid, day, is_arc, out = entry[:4]
        hook = entry[4] if len(entry) > 4 else None
        # Day-based framing overrides the tuple flag: past days caption as archive,
        # today onward as the live puzzle. Keeps the batch self-maintaining over time.
        is_arc = day < TODAY_DAY
        if pid not in players:
            print(f"SKIP {pid}: id not found in players.js")
            continue
        sil_path = os.path.join(SILS, f"{pid}.jpg")
        if not os.path.exists(sil_path):
            print(f"SKIP {pid}: silhouette {sil_path} not found")
            continue
        build_post(players[pid], day, is_arc, out, hook_text=hook)
        # Append caption + hashtag block to the captions file
        caption_lines.append(f"## {out}\n")
        caption_lines.append("**Caption:**\n```")
        caption_lines.append(caption_for(players[pid], day, is_today=not is_arc))
        caption_lines.append("```\n")
        caption_lines.append("**First comment (hashtags):**\n```")
        caption_lines.append(hashtags_for(players[pid]))
        caption_lines.append("```\n")
        caption_lines.append("---\n")
    captions_path = os.path.join(OUT, "captions.md")
    with open(captions_path, "w") as f:
        f.write("\n".join(caption_lines))
    print(f"\nwrote {os.path.relpath(captions_path, ROOT)}")
    print("\nDone. Image files + paste-ready captions in "
          "marketing_print/instagram_posts/")
