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
# 1. LABELS  (Avery L7165 layout: 99.1 x 67.7mm, 8 per A4 sheet.
#    Margins: 13mm top, 4.65mm sides, 2.5mm column gap, no row gap.
#    No border lines - labels are pre-cut.)
# ----------------------------------------------------------------------------
def build_labels(player, silhouette_filename, out_name, day_label, teaser_override=None):
    sil = img_data_uri(os.path.join(DOCS, "silhouettes", silhouette_filename))
    qr = qr_data_uri(HOME_URL + "?player=" + player["id"])
    teaser = teaser_override or (
        player["clues"][1] if len(player["clues"]) > 1 else player["clues"][0])
    label = f"""
      <div class="label">
        <div class="left">
          <div class="brand">GOOD TO HEAR THE NAME</div>
          <div class="prompt">Name this player</div>
          <img class="sil" src="{sil}" alt="mystery silhouette"/>
          <div class="teaser">&ldquo;{teaser}&rdquo;</div>
        </div>
        <div class="right">
          <img class="qr" src="{qr}" alt="scan to play"/>
          <div class="scan">Scan to play</div>
          <div class="meta">5 clues &middot; 5 guesses<br>new player every day</div>
        </div>
      </div>"""
    grid = label * 8
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Labels &ndash; {player['name']} ({day_label})</title><style>
{BASE_CSS}
@page {{ size: A4 portrait; margin: 0; }}
.sheet {{ width: 210mm; height: 297mm; background: #fff;
  padding: 13mm 4.65mm 13.2mm 4.65mm; display: grid;
  grid-template-columns: 99.1mm 99.1mm;
  grid-template-rows: repeat(4, 67.7mm);
  column-gap: 2.5mm; row-gap: 0; }}
.label {{ width: 99.1mm; height: 67.7mm; background: {CREAM};
  padding: 4mm 5mm; display: flex; gap: 4mm; overflow: hidden; }}
.left {{ flex: 1.45; display: flex; flex-direction: column; min-width: 0; }}
.brand {{ flex: 0 0 auto; font-size: 7pt; font-weight: 800; letter-spacing: .6px; color: {GREEN}; }}
.prompt {{ flex: 0 0 auto; font-size: 15pt; font-weight: 900; margin: 1mm 0 2mm; }}
.sil {{ flex: 1 1 auto; min-height: 0; width: 100%; object-fit: contain;
  object-position: left center; }}
.teaser {{ flex: 0 0 auto; font-size: 8pt; font-style: italic; line-height: 1.3;
  color: #2c3a30; margin-top: 2mm; }}
.right {{ flex: 1; display: flex; flex-direction: column; align-items: center;
  justify-content: center; text-align: center; gap: 1.5mm; }}
.qr {{ width: 32mm; height: 32mm; padding: 1.5mm; }}
.scan {{ font-size: 11pt; font-weight: 900; color: {GREEN}; }}
.meta {{ font-size: 7.5pt; font-weight: 600; color: #2c3a30; line-height: 1.3; }}
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
    build_labels(players["abidal"], "abidal.jpg",
                 "labels_saturday_abidal.html", "Sat 30 May", ABIDAL_CLUE)
    build_labels(players["salomon_rondon"], "salomon_rondon.jpg",
                 "labels_sunday_rondon.html", "Sun 31 May", RONDON_CLUE)
    build_poster(players["abidal"], "abidal.jpg",
                 "poster_saturday_abidal.html", "Sat 30 May", ABIDAL_CLUE)
    build_poster(players["salomon_rondon"], "salomon_rondon.jpg",
                 "poster_sunday_rondon.html", "Sun 31 May", RONDON_CLUE)
    print("\nOpen the files in marketing_print/ and print from your browser.")
