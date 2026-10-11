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
    ("thomas_vermaelen", 104, False, "54_sun16aug_today_vermaelen_day104.jpg",
     "Today's player belonged to a golden generation that promised more than it won."),
    ("michael_carrick",  105, False, "55_mon17aug_today_carrick_day105.jpg",
     "Today's player did the quiet work while others took the glory."),
    ("marco_reus",       106, False, "56_tue18aug_today_reus_day106.jpg",
     "Today's player was as gifted as he was unlucky."),
    ("esteban_cambiasso", 107, False, "57_wed19aug_today_cambiasso_day107.jpg",
     "Today's player did his best work where nobody was looking."),
    ("adriano",          108, False, "58_thu20aug_today_adriano_day108.jpg",
     "Today's player had a left foot like a sledgehammer."),
    ("jonathan_woodgate", 109, False, "59_fri21aug_today_woodgate_day109.jpg",
     "Today's player survived the most disastrous debut imaginable."),
    ("florent_malouda",  110, False, "60_sat22aug_today_malouda_day110.jpg",
     "Today's player took a while to win everyone over, then never looked back."),
    ("dimitri_payet",    111, False, "61_sun23aug_today_payet_day111.jpg",
     "Today's player scored goals that made rival managers applaud."),
    ("daley_blind",      112, False, "62_mon24aug_today_blind_day112.jpg",
     "Today's player could slot in anywhere and never let you down."),
    ("sami_hyypia",      113, False, "63_tue25aug_today_hyypia_day113.jpg",
     "Today's player was a giant who never got his moment on the biggest stage."),
    # --- Days 114-123: picture hooks lean punchier / give a bit more away to earn the click,
    # while the reel covers (make_reel_frames.py) stay deliberately hard. Two different lines per player.
    ("stewart_downing",  114, False, "64_wed26aug_today_downing_day114.jpg",
     "Today's player was a £20m winger who couldn't buy a goal in his first season."),
    ("fabien_barthez",   115, False, "65_thu27aug_today_barthez_day115.jpg",
     "Today's player won a World Cup, a Euros and a European Cup, and never scored a goal."),
    ("jermain_defoe",    116, False, "66_fri28aug_today_defoe_day116.jpg",
     "Today's player scored 150+ Premier League goals and left the same club twice."),
    ("david_villa",      117, False, "67_sat29aug_today_villa_day117.jpg",
     "Today's player is his country's all-time top scorer, and a World Cup winner."),
    ("henrik_larsson",   118, False, "68_sun30aug_today_larsson_day118.jpg",
     "Today's player was a goal machine in Britain, but barely scored in the Premier League."),
    ("darren_bent",      119, False, "69_mon31aug_today_bent_day119.jpg",
     "Today's player scored a goal off a beach ball that still causes arguments."),
    ("andrey_arshavin",  120, False, "70_tue01sep_today_arshavin_day120.jpg",
     "Today's player scored four goals in one game and still didn't win."),
    ("joleon_lescott",   121, False, "71_wed02sep_today_lescott_day121.jpg",
     "Today's player survived a fractured skull as a child to lift the Premier League."),
    ("dwight_yorke",     122, False, "72_thu03sep_today_yorke_day122.jpg",
     "Today's player won the treble and formed one of the league's great strike partnerships."),
    ("jamie_carragher",  123, False, "73_fri04sep_today_carragher_day123.jpg",
     "Today's player gave one club his whole career, and won the most dramatic final of all."),
]

# --- Days 124-173: bulk batch for scheduled posting. Compact (day, id, hook) rows;
# filenames auto-derived as day<N>_<id>.jpg so the R2 upload + Metricool CSV stay deterministic.
# Picture-hook voice: punchier, gives a bit more away to earn the click.
BULK_124_173 = [
    (124, "tomas_rosicky",        "Today's player had the talent, if only his body had let him show it."),
    (125, "ricardo_carvalho",     "Today's player followed one manager everywhere he went."),
    (126, "cheick_tiote",         "Today's player scored a goal his fans will never forget."),
    (127, "mauro_icardi",         "Today's player made as many headlines off the pitch as on it."),
    (128, "michael_essien",       "Today's player hit the ball harder than just about anyone."),
    (129, "jimmy_bullard",        "Today's player took the unlikeliest road to the top."),
    (130, "kevin_phillips",       "Today's player was one of the deadliest finishers around."),
    (131, "steve_bruce",          "Today's player had a surprising second career with a pen."),
    (132, "wilfried_zaha",        "Today's player got his dream move, then found where he belonged."),
    (133, "thiago_alcantara",     "Today's player was a winner, and it ran in the family."),
    (134, "titus_bramble",        "Today's player could win you the game, or lose it."),
    (135, "keylor_navas",         "Today's player reached the very top from the unlikeliest place."),
    (136, "ruud_gullit",          "Today's player was once the biggest name in the game."),
    (137, "troy_deeney",          "Today's player scored a goal an entire club will never forget."),
    (138, "javier_zanetti",       "Today's player looked like he could play forever."),
    (139, "rafael_van_der_vaart", "Today's player made the game look effortlessly elegant."),
    (140, "shay_given",           "Today's player was on the wrong end of a famous injustice."),
    (141, "faustino_asprilla",    "Today's player had one magical European night."),
    (142, "robert_huth",          "Today's player was part of the most unlikely triumph of all."),
    (143, "scott_parker",         "Today's player shone brightest as his team fell apart."),
    (144, "emmanuel_adebayor",    "Today's player once celebrated a goal in the most provocative way imaginable."),
    (145, "paolo_maldini",        "Today's player gave everything to one club, for a very long time."),
    (146, "ross_barkley",         "Today's player carried the hopes of his hometown."),
    (147, "samuel_etoo",          "Today's player was a winning machine."),
    (148, "nani",                 "Today's player lived in the shadow of a countryman legend."),
    (149, "rory_delap",           "Today's player had one weapon defenders genuinely feared."),
    (150, "fabio_da_silva",       "Today's player had an identical twin who played too."),
    (151, "paolo_di_canio",       "Today's player once chose sportsmanship over an open goal."),
    (152, "marc_albrighton",      "Today's player was a free transfer who ended up winning it all."),
    (153, "leandro_paredes",      "Today's player shared a pitch with the biggest names in the game."),
    (154, "nuno_espirito_santo",  "Today's player is better known now for the dugout than the pitch."),
    (155, "ryan_bertrand",        "Today's player's first big night was the biggest of all."),
    (156, "peter_odemwingie",     "Today's player was involved in one of deadline day's funniest moments."),
    (157, "marek_hamsik",         "Today's player rewrote the record books at one club."),
    (158, "richard_dunne",        "Today's player holds a record most defenders would rather forget."),
    (159, "edinson_cavani",       "Today's player once sent a global superstar home from a World Cup."),
    (160, "marc_overmars",        "Today's player was lightning down the wing."),
    (161, "paul_ince",            "Today's player broke barriers and crossed a great divide."),
    (162, "mikael_silvestre",     "Today's player crossed one of football's fiercest divides."),
    (163, "victor_wanyama",       "Today's player was a trailblazer for his nation."),
    (164, "nigel_martyn",         "Today's player once set a record between the posts."),
    (165, "mario_gomez",          "Today's player was a born finisher who missed his crowning moment."),
    (166, "harry_kewell",         "Today's player might be the finest his country ever produced."),
    (167, "leighton_baines",      "Today's player barely ever seemed to miss."),
    (168, "louis_saha",           "Today's player had all the talent, if not the luck."),
    (169, "john_obi_mikel",       "Today's player was fought over by two giants before he'd made it."),
    (170, "jermaine_pennant",     "Today's player was a wonderkid who reached the biggest stage."),
    (171, "boudewijn_zenden",     "Today's player went by a nickname his fans still love."),
    (172, "mario_balotelli",      "Today's player was as unpredictable as football gets."),
    (173, "david_james",          "Today's player was as famous for his mistakes as his saves."),
]
for _day, _pid, _hook in BULK_124_173:
    POSTS.append((_pid, _day, False, f"day{_day}_{_pid}.jpg", _hook))

# Today's live puzzle day (epoch 2026-05-05 = Day 1). Anything earlier is captioned
# as "from the archive" with a ?day=N replay link; this day and later post as "today's puzzle".
# Bump this as the calendar advances so past days auto-flip to archive framing.
TODAY_DAY = 142


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
    "thomas_vermaelen": "#belgium #arsenal #fcbarcelona #ajax #premierleague",
    "michael_carrick":  "#england #manchesterunited #tottenhamhotspur #premierleague #championsleague",
    "marco_reus":       "#germany #borussiadortmund #bvb #bundesliga #diemannschaft",
    "esteban_cambiasso": "#argentina #internazionale #leicestercity #realmadrid #seriea",
    "adriano":          "#brazil #internazionale #flamengo #seriea #selecao",
    "jonathan_woodgate": "#england #leedsunited #middlesbrough #tottenhamhotspur #realmadrid",
    "florent_malouda":  "#france #chelseafc #olympiquelyonnais #premierleague #lesbleus",
    "dimitri_payet":    "#france #westham #olympiquemarseille #euro2016 #premierleague",
    "daley_blind":      "#netherlands #ajax #manchesterunited #eredivisie #oranje",
    "sami_hyypia":      "#finland #liverpoolfc #bayerleverkusen #championsleague #premierleague",
    "stewart_downing":  "#england #liverpoolfc #middlesbrough #astonvilla #premierleague",
    "fabien_barthez":   "#france #manchesterunited #olympiquemarseille #worldcup98 #lesbleus",
    "jermain_defoe":    "#england #tottenhamhotspur #sunderlandafc #westham #premierleague",
    "david_villa":      "#spain #fcbarcelona #valenciacf #atleticomadrid #worldcup2010",
    "henrik_larsson":   "#sweden #celticfc #fcbarcelona #manchesterunited #cultheroes",
    "darren_bent":      "#england #sunderlandafc #astonvilla #tottenhamhotspur #premierleague",
    "andrey_arshavin":  "#russia #arsenal #zenit #premierleague #cultheroes",
    "joleon_lescott":   "#england #manchestercity #evertonfc #premierleague #cityzens",
    "dwight_yorke":     "#trinidadandtobago #manchesterunited #astonvilla #premierleague #treble99",
    "jamie_carragher":  "#england #liverpoolfc #premierleague #istanbul2005 #ynwa",
    "tomas_rosicky":       "#czechrepublic #arsenal #borussiadortmund #premierleague #euro2012",
    "ricardo_carvalho":    "#portugal #chelsea #realmadrid #fcporto #premierleague",
    "cheick_tiote":        "#ivorycoast #newcastleunited #premierleague #cskamoscow #nufc",
    "mauro_icardi":        "#argentina #internazionale #psg #seriea #galatasaray",
    "michael_essien":      "#ghana #chelsea #realmadrid #premierleague #thebison",
    "jimmy_bullard":       "#england #fulhamfc #hullcity #wiganathletic #premierleague",
    "kevin_phillips":      "#england #sunderlandafc #astonvilla #premierleague #goldenboot",
    "steve_bruce":         "#england #manchesterunited #premierleague #birminghamcity #captain",
    "wilfried_zaha":       "#ivorycoast #crystalpalace #manchesterunited #galatasaray #premierleague",
    "thiago_alcantara":    "#spain #bayernmunich #liverpoolfc #fcbarcelona #lamasia",
    "titus_bramble":       "#england #newcastleunited #wiganathletic #ipswichtown #premierleague",
    "keylor_navas":        "#costarica #realmadrid #psg #nottinghamforest #championsleague",
    "ruud_gullit":         "#netherlands #acmilan #chelsea #ballondor #footballnostalgia",
    "troy_deeney":         "#england #watfordfc #birminghamcity #premierleague #captain",
    "javier_zanetti":      "#argentina #internazionale #seriea #capitano #legend",
    "rafael_van_der_vaart": "#netherlands #tottenhamhotspur #realmadrid #hamburgersv #ajax",
    "shay_given":          "#ireland #newcastleunited #manchestercity #premierleague #goalkeeper",
    "faustino_asprilla":   "#colombia #newcastleunited #parmacalcio #premierleague #90sfootball",
    "robert_huth":         "#germany #leicestercity #chelsea #premierleague #foxes",
    "scott_parker":        "#england #westham #chelsea #tottenhamhotspur #premierleague",
    "emmanuel_adebayor":   "#togo #arsenal #manchestercity #tottenhamhotspur #realmadrid",
    "paolo_maldini":       "#italy #acmilan #seriea #championsleague #legend",
    "ross_barkley":        "#england #evertonfc #chelsea #premierleague #europaleague",
    "samuel_etoo":         "#cameroon #fcbarcelona #internazionale #treble #africanfootball",
    "nani":                "#portugal #manchesterunited #sportinglisbon #premierleague #selecao",
    "rory_delap":          "#ireland #stokecity #premierleague #longthrow #southamptonfc",
    "fabio_da_silva":      "#brazil #manchesterunited #premierleague #gremio #fullback",
    "paolo_di_canio":      "#italy #westham #celticfc #laziofc #premierleague",
    "marc_albrighton":     "#england #leicestercity #astonvilla #premierleague #foxes",
    "leandro_paredes":     "#argentina #psg #asroma #bocajuniors #worldcup2022",
    "nuno_espirito_santo": "#portugal #wolves #nottinghamforest #fcporto #manager",
    "ryan_bertrand":       "#england #chelsea #southamptonfc #premierleague #championsleague",
    "peter_odemwingie":    "#nigeria #westbromwichalbion #stokecity #premierleague #deadlineday",
    "marek_hamsik":        "#slovakia #napoli #seriea #brescia #mohawk",
    "richard_dunne":       "#ireland #manchestercity #astonvilla #premierleague #coybig",
    "edinson_cavani":      "#uruguay #psg #napoli #manchesterunited #elmatador",
    "marc_overmars":       "#netherlands #arsenal #ajax #fcbarcelona #premierleague",
    "paul_ince":           "#england #manchesterunited #liverpoolfc #westham #internazionale",
    "mikael_silvestre":    "#france #manchesterunited #arsenal #premierleague #defender",
    "victor_wanyama":      "#kenya #tottenhamhotspur #celticfc #southamptonfc #premierleague",
    "nigel_martyn":        "#england #leedsunited #crystalpalace #evertonfc #goalkeeper",
    "mario_gomez":         "#germany #bayernmunich #vfbstuttgart #fiorentina #diemannschaft",
    "harry_kewell":        "#australia #liverpoolfc #leedsunited #premierleague #socceroos",
    "leighton_baines":     "#england #evertonfc #wiganathletic #premierleague #leftback",
    "louis_saha":          "#france #manchesterunited #evertonfc #fulhamfc #premierleague",
    "john_obi_mikel":      "#nigeria #chelsea #premierleague #afcon #supereagles",
    "jermaine_pennant":    "#england #liverpoolfc #arsenal #stokecity #premierleague",
    "boudewijn_zenden":    "#netherlands #liverpoolfc #middlesbrough #chelsea #fcbarcelona",
    "mario_balotelli":     "#italy #manchestercity #acmilan #internazionale #supermario",
    "david_james":         "#england #liverpoolfc #portsmouthfc #astonvilla #premierleague",
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
