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
]


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
    "shevchenko":       "#ukraine #acmilan #chelseafc #ballondor #footballnostalgia",
    "trezeguet":        "#france #juventus #worldcup98 #euro2000 #serieA",
    "podolski":         "#worldcup2014 #germany #arsenal #1fckoln #poldi",
    "eidur_gudjohnsen": "#iceland #chelseafc #fcbarcelona #boltonwanderers #cultheroes",
    "antonio_di_natale": "#italy #udinese #serieA #capocannoniere #cultheroes",
    "diego_simeone":    "#argentina #atleticomadrid #lazio #internazionale #cholo",
    "emile_heskey":     "#england #liverpoolfc #astonvilla #leicestercity #premierleague",
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
