#!/usr/bin/env python3
"""Generate print-ready marketing HTML (stickers, A4 poster, hand-out cards).

Run with the project venv: scripts/.venv/bin/python scripts/make_print_assets.py
Outputs into marketing_print/. Open the .html files and print from the browser.
"""
import base64
import io
import json
import os

import segno

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
OUT = os.path.join(ROOT, "marketing_print")
HOME_URL = "https://bradshaw1992.github.io/good-to-hear-the-name/"

GREEN = "#0f7a3e"
CREAM = "#f4efe6"
INK = "#16261c"

os.makedirs(OUT, exist_ok=True)


def load_players():
    src = open(os.path.join(DOCS, "players.js")).read()
    src = src[src.index("["): src.rstrip().rstrip(";").rindex("]") + 1]
    return {p["id"]: p for p in json.loads(src)}


def qr_data_uri(url):
    qr = segno.make(url, error="m")
    buf = io.BytesIO()
    qr.save(buf, kind="png", scale=12, border=2, dark="#000000", light="#ffffff")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"


def img_data_uri(path):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = "jpeg" if path.lower().endswith((".jpg", ".jpeg")) else "png"
    return f"data:image/{ext};base64,{b64}"



BASE_CSS = f"""
  * {{ box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  html, body {{ margin: 0; padding: 0; font-family: 'Helvetica Neue', Arial, sans-serif; color: {INK}; }}
  .qr {{ background: #fff; border-radius: 6px; }}
  @media screen {{
    body {{ background: #ccc; padding: 20px; }}
    .sheet {{ box-shadow: 0 2px 12px rgba(0,0,0,.3); margin: 0 auto 20px; background: #fff; }}
  }}
"""


def write(name, html):
    path = os.path.join(OUT, name)
    with open(path, "w") as f:
        f.write(html)
    print("wrote", os.path.relpath(path, ROOT))


# ----------------------------------------------------------------------------
# 1. STICKERS  (player-specific: real silhouette + clue + pinned QR.
#    6 per A4 (~89 x 86mm). QR pins the exact player so the scan matches.)
# ----------------------------------------------------------------------------
def build_stickers(player, silhouette_filename, out_name, day_label, teaser_override=None):
    sil = img_data_uri(os.path.join(DOCS, "silhouettes", silhouette_filename))
    qr = qr_data_uri(HOME_URL + "?player=" + player["id"])
    teaser = teaser_override or (
        player["clues"][1] if len(player["clues"]) > 1 else player["clues"][0])
    sticker = f"""
      <div class="sticker">
        <div class="top">
          <div class="brand">GOOD TO HEAR THE NAME</div>
          <div class="prompt">Name this player</div>
        </div>
        <img class="sil" src="{sil}" alt="mystery silhouette"/>
        <div class="teaser">&ldquo;{teaser}&rdquo;</div>
        <div class="foot">
          <img class="qr" src="{qr}" alt="scan to play"/>
          <div class="cta"><span class="scan">Scan to play</span>
            <span class="meta">5 clues &middot; 5 guesses<br>new player every day</span></div>
        </div>
      </div>"""
    grid = sticker * 6
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Stickers &ndash; {player['name']} ({day_label})</title><style>
{BASE_CSS}
@page {{ size: A4 portrait; margin: 8mm; }}
.sheet {{ width: 210mm; height: 281mm; padding: 6mm; display: grid;
  grid-template-columns: repeat(2, 1fr); grid-template-rows: repeat(3, 1fr); gap: 4mm; }}
.sticker {{ border: 1px dashed #ccc; border-radius: 4mm; background: {CREAM};
  padding: 5mm 6mm; display: flex; flex-direction: column; overflow: hidden; }}
.top {{ flex: 0 0 auto; }}
.brand {{ font-size: 7pt; font-weight: 800; letter-spacing: .6px; color: {GREEN}; }}
.prompt {{ font-size: 17pt; font-weight: 900; margin-top: 1mm; }}
.sil {{ flex: 1 1 auto; min-height: 0; width: 100%; object-fit: contain;
  object-position: center; margin: 3mm 0; }}
.teaser {{ flex: 0 0 auto; font-size: 9pt; font-style: italic; line-height: 1.3;
  color: #2c3a30; margin-bottom: 4mm; }}
.foot {{ flex: 0 0 auto; display: flex; align-items: center; gap: 4mm; }}
.qr {{ width: 24mm; height: 24mm; padding: 1.5mm; }}
.cta {{ display: flex; flex-direction: column; }}
.scan {{ font-size: 13pt; font-weight: 900; color: {GREEN}; }}
.meta {{ font-size: 8pt; font-weight: 600; color: #2c3a30; margin-top: 1mm; line-height: 1.3; }}
</style></head><body>
<div class="sheet">{grid}</div>
</body></html>"""
    write(out_name, html)


# ----------------------------------------------------------------------------
# 2. A4 POSTER  (player-specific: big silhouette + clue + pinned QR.
#    The silhouette and clue are the hook; the QR pins that exact player.)
# ----------------------------------------------------------------------------
def build_poster(player, silhouette_filename, out_name, day_label, teaser_override=None):
    sil = img_data_uri(os.path.join(DOCS, "silhouettes", silhouette_filename))
    qr = qr_data_uri(HOME_URL + "?player=" + player["id"])
    teaser = teaser_override or (
        player["clues"][1] if len(player["clues"]) > 1 else player["clues"][0])
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Poster &ndash; {player['name']} ({day_label})</title><style>
{BASE_CSS}
@page {{ size: A4 portrait; margin: 0; }}
.sheet {{ width: 210mm; height: 297mm; background: {CREAM};
  display: flex; flex-direction: column; align-items: center;
  text-align: center; padding: 14mm 16mm; }}
.brand {{ flex: 0 0 auto; font-size: 13pt; font-weight: 800; letter-spacing: 1px; color: {GREEN}; }}
.head {{ flex: 0 0 auto; font-size: 40pt; font-weight: 900; line-height: 1.0; margin: 4mm 0 5mm; }}
.sil {{ flex: 1 1 auto; min-height: 0; width: 100%; object-fit: contain;
  object-position: center; margin-bottom: 4mm; }}
.teaser {{ flex: 0 0 auto; font-size: 17pt; font-style: italic; font-weight: 600;
  line-height: 1.35; max-width: 165mm; color: {INK}; margin-bottom: 6mm; }}
.qr {{ flex: 0 0 auto; width: 56mm; height: 56mm; padding: 3mm; border: 2px solid {GREEN}; }}
.scan {{ flex: 0 0 auto; font-size: 18pt; font-weight: 900; color: {GREEN}; margin-top: 3mm; }}
.rules {{ flex: 0 0 auto; font-size: 13pt; font-weight: 600; margin-top: 4mm; line-height: 1.45; }}
</style></head><body>
<div class="sheet">
  <div class="brand">GOOD TO HEAR THE NAME</div>
  <div class="head">Name this player.</div>
  <img class="sil" src="{sil}" alt="mystery silhouette"/>
  <div class="teaser">&ldquo;{teaser}&rdquo;</div>
  <img class="qr" src="{qr}" alt="scan to play"/>
  <div class="scan">Scan to play &rarr;</div>
  <div class="rules">5 clues. 5 guesses. A new player every day.<br>Free, plays in your browser, no app needed.</div>
</div>
</body></html>"""
    write(out_name, html)


ABIDAL_CLUE = ("Less than two months after surgery, I played the full 90 "
               "minutes of a Champions League final.")
RONDON_CLUE = ("I am my country's all-time leading goalscorer, but I have never "
               "played at a World Cup, because my country has never qualified.")

if __name__ == "__main__":
    players = load_players()
    build_stickers(players["abidal"], "abidal.jpg",
                   "stickers_saturday_abidal.html", "Sat 30 May", ABIDAL_CLUE)
    build_stickers(players["salomon_rondon"], "salomon_rondon.jpg",
                   "stickers_sunday_rondon.html", "Sun 31 May", RONDON_CLUE)
    build_poster(players["abidal"], "abidal.jpg",
                 "poster_saturday_abidal.html", "Sat 30 May", ABIDAL_CLUE)
    build_poster(players["salomon_rondon"], "salomon_rondon.jpg",
                 "poster_sunday_rondon.html", "Sun 31 May", RONDON_CLUE)
    print("\nOpen the files in marketing_print/ and print from your browser.")
