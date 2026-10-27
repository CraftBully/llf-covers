"""Render Love, Lies & Fallout part covers (1080x1350 JPG) into the repo root.

Usage (from anywhere):
  python3 kit/make_cover.py 31 Sabine "Short Cover Title" [32 Odessa "Another Title" ...]
  python3 kit/make_cover.py --story exit-plan 1 Celeste "Short Cover Title" ...

The Unraveling (default) writes Part_<N>_cover.jpg in the repo root.
--story exit-plan writes exit-plan/Part_<N>_cover.jpg with the title THE EXIT PLAN.
--story ashes-of-a-friendship writes ashes-of-a-friendship/Part_<N>_cover.jpg with the title ASHES OF A FRIENDSHIP.
Needs: pip install playwright (Chromium already installed).
"""
import sys, html
from pathlib import Path
from playwright.sync_api import sync_playwright

KIT = Path(__file__).resolve().parent
OUT = KIT.parent
ACCENT = {"Sabine": "#e3263a", "Odessa": "#e0a43a", "Rhys": "#8fb4d9", "Lucian": "#e07a2e",
          "Juno": "#e46aa0", "Imogene": "#b394e6",
          "Celeste": "#e3263a", "Dash": "#8fb4d9", "Desmond": "#e0a43a", "Tamsin": "#e46aa0",
          "Marguerite": "#b394e6", "Wren": "#4fd1a5",
          "Lani": "#e3263a", "Seven": "#ff7a1a", "Tez": "#8fb4d9", "Legend": "#e0a43a", "Brielle": "#b394e6"}
STORIES = {"unraveling": ("THE", "UNRAVELING", 140, "", "A Fallout Story"), "exit-plan": ("THE", "EXIT PLAN", 150, "exit-plan", "A Love Story"), "ashes-of-a-friendship": ("ASHES OF A", "FRIENDSHIP", 132, "ashes-of-a-friendship", "A Lies Story")}
STORY = "unraveling"

CSS = """
@font-face{font-family:PF;font-weight:900;src:url(fonts/playfair-display-latin-900-normal.woff2)}
@font-face{font-family:PF;font-weight:700;font-style:italic;src:url(fonts/playfair-display-latin-700-italic.woff2)}
@font-face{font-family:Mont;font-weight:600;src:url(fonts/montserrat-latin-600-normal.woff2)}
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000}
.c{position:relative;overflow:hidden;background:#050304;color:#f4eee8}
.bg{position:absolute;inset:0;background:url(art/bg_kdp.png) center bottom/cover;opacity:.55;filter:saturate(1.1)}
.shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.92) 0%,rgba(0,0,0,.35) 38%,rgba(0,0,0,.25) 60%,rgba(0,0,0,.85) 100%)}
.logo{position:absolute;left:0;right:0;top:0;width:100%;-webkit-mask-image:linear-gradient(180deg,#000 72%,transparent 100%);mask-image:linear-gradient(180deg,#000 72%,transparent 100%)}
.chrome{background:linear-gradient(180deg,#ffffff 0%,#d9dde3 28%,#7d838c 50%,#e9ecef 62%,#9aa1aa 82%,#f5f7f9 100%);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 3px 0 rgba(0,0,0,.6)) drop-shadow(0 10px 24px rgba(0,0,0,.9))}
.mont{font-family:Mont;font-weight:600;text-transform:uppercase}
.mid{position:absolute;left:0;right:0;text-align:center}
.num{font-family:PF;font-weight:900;line-height:.9;letter-spacing:.02em}
.who{letter-spacing:.42em}
.title{font-family:PF;font-weight:700;font-style:italic;line-height:1.08;text-wrap:balance;text-shadow:0 2px 0 #000,0 8px 22px #000}
.rule{height:3px;margin:0 auto}
.foot{position:absolute;left:0;right:0;text-align:center;letter-spacing:.3em;color:#cfc6c0}
"""

def cover(n, narrator, title):
    top, big, bigsize, _, lane = STORIES[STORY]
    acc = ACCENT.get(narrator, "#e3263a")
    return f"""<div class="c" id="cv" style="width:1080px;height:1350px">
<div class="bg"></div><div class="shade"></div>
<img class="logo" src="art/logo.png">
<div class="mid" style="top:540px">
  <div class="num chrome" style="font-size:96px">{top}</div>
  <div class="num chrome" style="font-size:{bigsize}px;margin-top:-4px">{big}</div>
  <div class="rule" style="width:120px;background:{acc};margin-top:26px"></div>
  <div class="mont" style="font-size:44px;letter-spacing:.3em;margin-top:24px;color:#f1ece6">Part {n}</div>
  <div class="mont who" style="font-size:30px;margin-top:14px;color:{acc}">{html.escape(narrator)}</div>
  <div class="title" style="font-size:62px;margin:34px 80px 0">{html.escape(title)}</div>
</div>
<div class="foot mont" style="bottom:46px;font-size:22px">{lane} · Love, Lies &amp; Fallout</div>
</div>"""

if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--story"]:
        STORY = a[1]; a = a[2:]
    sub = STORIES[STORY][3]
    if sub:
        (OUT / sub).mkdir(exist_ok=True)
    if not a or len(a) % 3:
        sys.exit(__doc__)
    jobs = [(int(a[i]), a[i + 1].title(), a[i + 2]) for i in range(0, len(a), 3)]
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 1500})
        for n, who, title in jobs:
            tmp = KIT / "_tmp.html"
            tmp.write_text(f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{cover(n, who, title)}</body></html>")
            pg.goto(f"file://{tmp}"); pg.wait_for_timeout(300); pg.evaluate("document.fonts.ready")
            dest = (OUT / sub if sub else OUT) / f"Part_{n:02d}_cover.jpg"
            pg.locator("#cv").screenshot(path=str(dest), type="jpeg", quality=90)
            print("wrote", dest.name)
        b.close()
        (KIT / "_tmp.html").unlink(missing_ok=True)
