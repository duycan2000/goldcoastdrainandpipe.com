"""Renders the blog illustrations (SVG drawn here) to WebP (+ JPG for covers) in public/blog/<slug>/,
and writes src/data/blog-images.json with each image's width and height.
Run from the project root: python3 scripts/blog_images.py"""
import json, os, io, pathlib
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = ROOT / "node_modules/@fontsource-variable"
OUT = ROOT / "public/blog"

NAVY, NAVY9, NAVY7 = "#12304A", "#0C2236", "#1D4366"
TEAL, TEAL7, TEAL_L, TEAL50 = "#157A80", "#10616A", "#5FD3C4", "#E9F4F5"
ORANGE, SAND, LINE, MUTED, TEXT = "#F26419", "#F6F7F8", "#E1E6EB", "#5B6875", "#2A3744"
CLAY, CLAY_D, ROOT_C, SOIL, LAWN = "#C98B5F", "#9C6440", "#7A5230", "#E8DCCB", "#9CC77A"
RED = "#C2410C"

import base64
def _b64(rel): return base64.b64encode((FONTS / rel).read_bytes()).decode()
CSS = f"""
@font-face {{ font-family: 'Bric'; src: url('data:font/woff2;base64,{_b64("bricolage-grotesque/files/bricolage-grotesque-latin-wght-normal.woff2")}') format('woff2'); font-weight: 200 800; }}
@font-face {{ font-family: 'Fig'; src: url('data:font/woff2;base64,{_b64("figtree/files/figtree-latin-wght-normal.woff2")}') format('woff2'); font-weight: 300 900; }}
html, body {{ margin: 0; padding: 0; background: #fff; }}
svg {{ display: block; }}
.d {{ font-family: 'Bric', sans-serif; }}
.b {{ font-family: 'Fig', sans-serif; }}
"""

def T(x, y, s, size=24, w=500, fill=TEXT, cls="b", anchor="start", extra=""):
    s = s.replace("&", "&amp;")
    return f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" font-weight="{w}" fill="{fill}" text-anchor="{anchor}" {extra}>{s}</text>'

def lines(x, y, rows, size=22, w=500, fill=TEXT, gap=1.35, cls="b", anchor="start"):
    return "".join(T(x, y + i * size * gap, r, size, w, fill, cls, anchor) for i, r in enumerate(rows))

def svg(w, h, body, bg="#fff"):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="{bg}"/>{body}</svg>'

def brand(x, y, fill="#9FB4C7"):
    return (f'<g transform="translate({x},{y})"><rect width="34" height="34" rx="8" fill="{NAVY}" stroke="#2C5679"/>'
            f'<path d="M8 11h10a5 5 0 0 1 5 5v9" fill="none" stroke="{ORANGE}" stroke-width="4.5" stroke-linecap="round"/></g>'
            + T(x + 46, y + 23, "Gold Coast Drain & Pipe", 18, 600, fill))

def pill(x, y, label, bg=TEAL50, fg=TEAL7, size=18, pad=16, w=None):
    width = w or int(len(label) * size * 0.56 + pad * 2)
    return f'<rect x="{x}" y="{y}" width="{width}" height="{size*2}" rx="{size}" fill="{bg}"/>' + T(x + width / 2, y + size * 1.36, label, size, 650, fg, anchor="middle")

# ---------- pipe pieces ----------
def cross_section(cx, cy, r, liner=True, crack=True, roots=False, label=False, scale=1):
    """End view of a pipe. Outer clay wall, optional liner ring, smooth bore."""
    wall = r * 0.22
    g = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{CLAY}"/>'
    g += f'<circle cx="{cx}" cy="{cy}" r="{r - wall}" fill="{"#fff" if not liner else TEAL}"/>'
    if liner:
        g += f'<circle cx="{cx}" cy="{cy}" r="{r - wall - r*0.11}" fill="#F3FAFA"/>'
    if crack:
        g += f'<path d="M{cx - r*0.15} {cy - r} l{r*0.06} {wall*0.45} l{-r*0.05} {wall*0.3} l{r*0.05} {wall*0.35}" stroke="{CLAY_D}" stroke-width="{3*scale}" fill="none" stroke-linecap="round"/>'
        g += f'<path d="M{cx + r*0.92} {cy + r*0.3} l{-wall*0.5} {r*0.03} l{-wall*0.3} {-r*0.05}" stroke="{CLAY_D}" stroke-width="{3*scale}" fill="none" stroke-linecap="round"/>'
    if roots:
        for a, b in ((0.0, -1), (0.4, -0.9)):
            g += f'<path d="M{cx + r*a} {cy + r*b} q{r*0.1} {r*0.35} {-r*0.05} {r*0.6} M{cx + r*a} {cy + r*b + r*0.3} q{r*0.2} {r*0.05} {r*0.3} {r*0.25}" stroke="{ROOT_C}" stroke-width="{4*scale}" fill="none" stroke-linecap="round"/>'
    # highlight on bore
    g += f'<path d="M{cx - r*0.45} {cy - r*0.2} a{r*0.5} {r*0.5} 0 0 1 {r*0.35} {-r*0.3}" stroke="#fff" stroke-opacity=".7" stroke-width="{5*scale}" fill="none" stroke-linecap="round"/>'
    return g

def long_pipe(x, y, length, h=70, joints=6, liner=None, patch=None, roots_at=(), crack_at=(), junction_at=None):
    """Side view of a clay pipe with joints. liner=(x0,x1) teal band; patch=(x0,x1)."""
    g = f'<rect x="{x}" y="{y}" width="{length}" height="{h}" rx="8" fill="{CLAY}"/>'
    g += f'<rect x="{x}" y="{y + h*0.18}" width="{length}" height="{h*0.64}" fill="#FBF6F1"/>'
    step = length / joints
    for i in range(1, joints):
        jx = x + i * step
        g += f'<rect x="{jx - 7}" y="{y - 6}" width="14" height="{h + 12}" rx="4" fill="{CLAY_D}"/>'
    for i in roots_at:
        jx = x + i * step
        g += (f'<path d="M{jx} {y - 30} C {jx + 6} {y - 10}, {jx - 8} {y + 10}, {jx + 4} {y + h*0.45} M{jx + 2} {y + 6} c 14 4 22 12 26 22 M{jx - 1} {y + 16} c -14 4 -20 12 -24 20" '
              f'stroke="{ROOT_C}" stroke-width="4" fill="none" stroke-linecap="round"/>')
    for i in crack_at:
        jx = x + i * step + step / 2
        g += f'<path d="M{jx - 10} {y} l8 10 l-6 8 l10 10" stroke="{CLAY_D}" stroke-width="3" fill="none" stroke-linecap="round"/>'
    if liner:
        a, b = liner
        g += f'<rect x="{a}" y="{y + h*0.18}" width="{b - a}" height="{h*0.64}" fill="{TEAL}"/>'
        g += f'<rect x="{a}" y="{y + h*0.18 + 9}" width="{b - a}" height="{h*0.64 - 18}" fill="#F3FAFA"/>'
    if patch:
        a, b = patch
        g += f'<rect x="{a}" y="{y + h*0.18}" width="{b - a}" height="{h*0.64}" rx="3" fill="{TEAL}"/>'
        g += f'<rect x="{a}" y="{y + h*0.18 + 9}" width="{b - a}" height="{h*0.64 - 18}" fill="#F3FAFA"/>'
    if junction_at is not None:
        jx = x + junction_at
        g += f'<path d="M{jx} {y} l-50 -70 h44 l40 70z" fill="{CLAY}"/><path d="M{jx + 8} {y + 4} l-44 -62 h22 l38 58z" fill="#FBF6F1"/>'
    return g

def callout(x, y, tx, ty, label_rows, size=20, color=TEXT, dot=TEAL, anchor="start", w=600):
    g = f'<path d="M{x} {y} L{tx} {ty}" stroke="{MUTED}" stroke-width="1.6" stroke-dasharray="4 4"/>'
    g += f'<circle cx="{x}" cy="{y}" r="6" fill="{dot}" stroke="#fff" stroke-width="2"/>'
    g += lines(tx + (8 if anchor == "start" else -8), ty + 6, label_rows, size, w, color, anchor=anchor)
    return g

def icon(name, x, y, s=48, color=TEAL):
    """Simple line icons on a 24 grid."""
    paths = {
        "camera": '<rect x="3" y="7" width="13" height="10" rx="2"/><path d="m16 11 5-3v8l-5-3"/><circle cx="9.5" cy="12" r="2.2"/>',
        "jet": '<path d="M3 12h9"/><path d="M12 9v6l3-3z"/><path d="M16 8l5-2M16 12h5M16 16l5 2"/>',
        "ruler": '<rect x="2" y="8" width="20" height="8" rx="1.5"/><path d="M6 8v3M10 8v4M14 8v3M18 8v4"/>',
        "liner": '<path d="M4 6h16M4 18h16"/><path d="M4 9h16v6H4z"/>',
        "push": '<path d="M3 12h13"/><path d="m12 7 5 5-5 5"/><path d="M20 5v14"/>',
        "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
        "cut": '<circle cx="6" cy="18" r="3"/><circle cx="6" cy="6" r="3"/><path d="M20 4 8.1 15.9M14.5 14.5 20 20M8.1 8.1 12 12"/>',
        "check": '<circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/>',
        "drop": '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11Z"/>',
        "toilet": '<path d="M7 3h7v6H7z"/><path d="M5 9h14a6 6 0 0 1-6 6h-2a6 6 0 0 1-6-6Z"/><path d="M9 15v6h6v-6"/>',
        "nose": '<path d="M12 3v9l3 3a3 3 0 0 1-3 3h-1"/><path d="M5 9c2 1 3 3 3 5M19 9c-2 1-3 3-3 5"/>',
        "repeat": '<path d="M17 2l4 4-4 4"/><path d="M3 11V9a3 3 0 0 1 3-3h15"/><path d="M7 22l-4-4 4-4"/><path d="M21 13v2a3 3 0 0 1-3 3H3"/>',
        "bubbles": '<circle cx="8" cy="15" r="4"/><circle cx="16" cy="9" r="3"/><circle cx="17" cy="17" r="2"/>',
        "grate": '<circle cx="12" cy="12" r="9"/><path d="M7 9h10M6 12h12M7 15h10"/>',
        "house": '<path d="M3 11 12 4l9 7"/><path d="M5 10v10h14V10"/>',
        "warn": '<path d="M12 3 2 20h20Z"/><path d="M12 10v4M12 17v.5"/>',
        "dig": '<path d="M14 4l6 6"/><path d="M17 7 9 15"/><path d="M4 20l5-5 3 3-5 5H4z" transform="translate(0 -3)"/>',
        "tree": '<path d="M12 21v-6"/><path d="M12 3a6 6 0 0 0-4 10.5A4 4 0 0 0 12 21a4 4 0 0 0 4-7.5A6 6 0 0 0 12 3Z"/>',
        "dollar": '<path d="M12 2v20"/><path d="M17 6H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
    }
    k = s / 24
    return f'<g transform="translate({x},{y}) scale({k})" fill="none" stroke="{color}" stroke-width="{1.8}" stroke-linecap="round" stroke-linejoin="round">{paths[name]}</g>'

def cover(kicker, title_rows, chips, art, accent=ORANGE):
    W, H = 1200, 630
    bg = (f'<defs><radialGradient id="g" cx="0" cy="0" r="1.2"><stop offset="0" stop-color="{NAVY7}"/><stop offset=".55" stop-color="{NAVY}"/><stop offset="1" stop-color="{NAVY9}"/></radialGradient>'
          f'<pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse"><path d="M28 0H0V28" fill="none" stroke="#fff" stroke-opacity=".04"/></pattern></defs>'
          f'<rect width="{W}" height="{H}" fill="url(#g)"/><rect width="{W}" height="{H}" fill="url(#grid)"/>')
    body = bg + art
    body += T(64, 120, kicker.upper(), 18, 700, TEAL_L, extra='letter-spacing="2"')
    body += lines(64, 190, title_rows, 58, 750, "#fff", 1.12, "d")
    yy = 190 + len(title_rows) * 58 * 1.12 + 26
    x = 64
    for c in chips:
        wdt = int(len(c) * 18 * 0.55 + 36)
        body += f'<rect x="{x}" y="{yy}" width="{wdt}" height="40" rx="20" fill="#fff" fill-opacity=".08" stroke="#fff" stroke-opacity=".18"/>' + T(x + wdt / 2, yy + 26, c, 18, 600, "#E6EEF5", anchor="middle")
        x += wdt + 12
    body += brand(64, 548)
    body += f'<rect x="64" y="{yy - 8 - 0}" width="0" height="0"/>'
    body += f'<rect x="0" y="{H-8}" width="{W}" height="8" fill="{accent}"/>'
    return svg(W, H, body)

IMAGES = {}  # path -> (svg, also_jpg)
def add(slug, name, s, jpg=False):
    IMAGES[f"/blog/{slug}/{name}.webp"] = (s, jpg)

# ======================= POST 1: pipe relining cost =======================
S = "pipe-relining-cost"
art = cross_section(920, 300, 190, liner=True, crack=True, scale=1.5)
art += f'<circle cx="920" cy="300" r="214" fill="none" stroke="{TEAL_L}" stroke-opacity=".25" stroke-width="2" stroke-dasharray="6 8"/>'
add(S, "cover", cover("2026 price guide", ["Pipe relining", "cost on the", "Gold Coast"], ["$2,000 first metre", "~$550 per extra metre", "$300+ patch"], art), jpg=True)

# cost by length bar chart
W, H = 1200, 700
lengths = [1, 3, 5, 8, 10, 15]
vals = [2000 + (m - 1) * 550 for m in lengths]
x0, y0, cw, ch = 140, 150, 980, 430
mx = 10000
b = T(60, 70, "Estimated pipe relining cost by length", 34, 700, NAVY, "d")
b += T(60, 108, "Average of $2,000 for the first metre plus $550 for each extra metre. Includes GST.", 20, 500, MUTED)
for v in range(0, mx + 1, 2500):
    yy = y0 + ch - v / mx * ch
    b += f'<line x1="{x0}" y1="{yy}" x2="{x0 + cw}" y2="{yy}" stroke="{LINE}" stroke-width="1.5"/>' + T(x0 - 16, yy + 7, f"${v:,}", 18, 500, MUTED, anchor="end")
bw = 100
gap = (cw - bw * len(lengths)) / len(lengths)
for i, (m, v) in enumerate(zip(lengths, vals)):
    bx = x0 + gap / 2 + i * (bw + gap)
    bh = v / mx * ch
    col = TEAL if m != 1 else NAVY7
    b += f'<rect x="{bx}" y="{y0 + ch - bh}" width="{bw}" height="{bh}" rx="6" fill="{col}"/>'
    b += T(bx + bw / 2, y0 + ch - bh - 14, f"${v:,}", 22, 700, NAVY, "d", "middle")
    b += T(bx + bw / 2, y0 + ch + 34, f"{m} m", 20, 650, TEXT, anchor="middle")
b += f'<line x1="{x0}" y1="{y0 + ch}" x2="{x0 + cw}" y2="{y0 + ch}" stroke="{MUTED}" stroke-width="2"/>'
b += T(x0 + cw / 2, y0 + ch + 72, "Length of pipe relined", 18, 600, MUTED, anchor="middle")
b += T(60, H - 24, "Source: Oneflare sewer pipe relining costs. Estimates only, before junctions and inspection.", 16, 500, MUTED)
add(S, "cost-by-length", svg(W, H, b))

# patch vs full
W, H = 1200, 660
b = T(60, 70, "Patch relining vs full relining", 34, 700, NAVY, "d")
b += T(60, 108, "Same pipe, two different fixes.", 20, 500, MUTED)
b += f'<rect x="40" y="140" width="1120" height="230" rx="16" fill="{SAND}"/>'
b += T(70, 186, "Patch relining", 26, 700, NAVY, "d") + T(70, 216, "One short liner over one damaged joint", 19, 500, MUTED)
b += pill(900, 160, "$300 to $1,000", ORANGE, "#1A1206", 20, w=220)
b += long_pipe(80, 260, 1040, 70, 6, patch=(80 + 1040 / 6 * 3 - 70, 80 + 1040 / 6 * 3 + 70), roots_at=(3,))
b += f'<rect x="40" y="400" width="1120" height="230" rx="16" fill="{SAND}"/>'
b += T(70, 446, "Full relining", 26, 700, NAVY, "d") + T(70, 476, "One continuous liner covering every joint", 19, 500, MUTED)
b += pill(830, 420, "$2,000 + ~$550 per metre", ORANGE, "#1A1206", 20, w=290)
b += long_pipe(80, 520, 1040, 70, 6, liner=(80, 1120), roots_at=())
b += T(80 + 1040 / 6 * 3, 368, "", 10)
add(S, "patch-vs-full", svg(W, H, b))

# quote breakdown (stacked bar) for Example 2
W, H = 1200, 600
parts = [("Liner, 6 metres", 4750, TEAL), ("CCTV and cleaning", 525, NAVY7), ("Junction reinstatement", 450, ORANGE)]
total = sum(p[1] for p in parts)
b = T(60, 70, "Where the money goes in a relining quote", 34, 700, NAVY, "d")
b += T(60, 108, "Example: six metres of root-damaged clay pipe with one branch junction", 20, 500, MUTED)
x, y, w, h = 60, 170, 1080, 90
cx = x
for lab, v, col in parts:
    pw = v / total * w
    b += f'<rect x="{cx}" y="{y}" width="{pw}" height="{h}" fill="{col}"/>'
    cx += pw
b = b.replace(f'<rect x="{x}" y="{y}"', f'<rect x="{x}" y="{y}" rx="0"', 1)
b += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="none" stroke="#fff" stroke-width="0"/>'
yy = 330
for i, (lab, v, col) in enumerate(parts):
    bx = 60 + i * 370
    b += f'<rect x="{bx}" y="{yy}" width="340" height="170" rx="16" fill="{SAND}"/>'
    b += f'<rect x="{bx + 24}" y="{yy + 28}" width="18" height="18" rx="4" fill="{col}"/>' + T(bx + 54, yy + 44, lab, 20, 650, NAVY)
    b += T(bx + 24, yy + 104, f"about ${v:,}", 38, 750, NAVY, "d")
    b += T(bx + 24, yy + 140, f"{round(v / total * 100)}% of the total", 18, 500, MUTED)
b += T(60, H - 30, f"Estimated total about ${total:,}. Based on 2026 Australian price-guide averages. Your plumber's quote may differ.", 17, 500, MUTED)
add(S, "quote-breakdown", svg(W, H, b))

# ======================= POST 2: what is pipe relining =======================
S = "what-is-pipe-relining"
art = cross_section(900, 310, 200, liner=True, crack=True, roots=False, scale=1.5)
art += callout(900 - 200 * 0.95, 310 - 40, 640, 470, [], 1)
add(S, "cover", cover("Plain-English guide", ["What is", "pipe relining?"], ["No digging", "Done in a day", "Pipe inside a pipe"], cross_section(920, 310, 200, liner=True, crack=True, scale=1.5)), jpg=True)

W, H = 1200, 680
b = T(60, 70, "A new pipe built inside the old one", 34, 700, NAVY, "d")
b += T(60, 108, "Cross-section of a clay sewer pipe before and after relining", 20, 500, MUTED)
b += f'<rect x="40" y="140" width="540" height="500" rx="16" fill="{SAND}"/><rect x="620" y="140" width="540" height="500" rx="16" fill="{TEAL50}"/>'
b += T(310, 190, "Before", 26, 700, NAVY, "d", "middle") + T(890, 190, "After", 26, 700, NAVY, "d", "middle")
b += cross_section(310, 380, 140, liner=False, crack=True, roots=True, scale=1.2)
b += cross_section(890, 380, 140, liner=True, crack=True, roots=False, scale=1.2)
b += lines(310, 568, ["Cracks, open joints and", "roots catch waste"], 20, 550, TEXT, anchor="middle")
b += lines(890, 568, ["Smooth, joint-free liner", "seals cracks and joints"], 20, 550, TEXT, anchor="middle")
b += f'<path d="M1010 290 L1080 240" stroke="{MUTED}" stroke-width="1.6"/><circle cx="1010" cy="290" r="5" fill="{NAVY}"/>' + T(1086, 238, "Liner", 18, 650, NAVY)
b += f'<path d="M1020 440 L1084 486" stroke="{MUTED}" stroke-width="1.6"/><circle cx="1020" cy="440" r="5" fill="{NAVY}"/>' + T(1046, 510, "Old pipe", 18, 650, NAVY)
add(S, "cross-section", svg(W, H, b))

steps = [("camera", "CCTV inspection", "Find and measure"), ("jet", "Clean the pipe", "Jetting and root cutting"), ("ruler", "Measure", "Cut liner, add resin"),
         ("push", "Install liner", "Inversion or pull-in"), ("clock", "Cure", "Resin hardens in place"), ("cut", "Reopen junctions", "Robotic cutter"), ("check", "Final camera check", "Footage for you")]
W, H = 1200, 720
b = T(60, 70, "How pipe relining works, step by step", 34, 700, NAVY, "d")
b += T(60, 108, "A typical house sewer is relined in one day", 20, 500, MUTED)
for i, (ic, h1, h2) in enumerate(steps):
    row, col = (0, i) if i < 4 else (1, i - 4)
    cw_ = 255
    bx = 60 + col * (cw_ + 20) + (0 if row == 0 else 137)
    by = 150 + row * 270
    b += f'<rect x="{bx}" y="{by}" width="{cw_}" height="240" rx="16" fill="{SAND}" stroke="{LINE}"/>'
    b += f'<circle cx="{bx + 44}" cy="{by + 46}" r="22" fill="{NAVY}"/>' + T(bx + 44, by + 54, str(i + 1), 22, 750, "#fff", "d", "middle")
    b += f'<rect x="{bx + 24}" y="{by + 88}" width="72" height="72" rx="14" fill="{TEAL50}"/>' + icon(ic, bx + 36, by + 100, 48)
    b += T(bx + 24, by + 196, h1, 21, 700, NAVY) + T(bx + 24, by + 222, h2, 17, 500, MUTED)
add(S, "process-steps", svg(W, H, b))

W, H = 1200, 700
b = T(60, 70, "Three types of pipe relining", 34, 700, NAVY, "d")
b += T(60, 108, "Which one you need depends on where the damage is", 20, 500, MUTED)
rows = [("Patch liner", "Fixes one crack or one bad joint", dict(patch=(80 + 1040 / 6 * 2 - 70, 80 + 1040 / 6 * 2 + 70), roots_at=(2,))),
        ("Full liner", "Covers every joint in the run", dict(liner=(80, 1120))),
        ("Junction liner", "Seals the point where a branch joins", dict(junction_at=610))]
for i, (h1, h2, kw) in enumerate(rows):
    by = 140 + i * 180
    b += f'<rect x="40" y="{by}" width="1120" height="160" rx="16" fill="{SAND}"/>'
    b += T(70, by + 44, h1, 24, 700, NAVY, "d") + T(70, by + 72, h2, 18, 500, MUTED)
    b += long_pipe(80, by + 92 if i != 2 else by + 92, 1040, 48, 6, **kw)
    if i == 2:
        b += f'<path d="M{80 + 610 - 22} {by + 92 + 4} q 20 -6 44 0" stroke="{TEAL}" stroke-width="14" fill="none"/>'
add(S, "liner-types", svg(W, H, b))

# ======================= POST 3: how to clear a blocked drain =======================
S = "how-to-clear-a-blocked-drain"
art = (f'<g transform="translate(780 90)">'
       f'<ellipse cx="190" cy="420" rx="230" ry="36" fill="#000" fill-opacity=".18"/>'
       f'<path d="M0 260 h380 a30 30 0 0 1 -30 30 h-320 a30 30 0 0 1 -30 -30z" fill="#E6EEF5"/>'
       f'<rect x="-10" y="240" width="400" height="26" rx="10" fill="#fff"/>'
       f'<path d="M170 290 v60 a30 30 0 0 0 60 0 v-14" stroke="#B9C7D4" stroke-width="22" fill="none" stroke-linecap="round"/>'
       f'<rect x="178" y="40" width="22" height="170" rx="10" fill="{ROOT_C}"/>'
       f'<path d="M110 250 a80 52 0 0 1 158 0 z" fill="{ORANGE}"/>'
       f'<rect x="100" y="244" width="178" height="12" rx="6" fill="#C24E10"/>'
       f'<circle cx="80" cy="120" r="14" fill="{TEAL_L}" fill-opacity=".5"/><circle cx="56" cy="160" r="9" fill="{TEAL_L}" fill-opacity=".4"/><circle cx="300" cy="140" r="11" fill="{TEAL_L}" fill-opacity=".45"/>'
       f'</g>')
add(S, "cover", cover("Safe DIY guide", ["How to clear", "a blocked drain"], ["6 easy fixes", "What not to do", "When to stop"], art), jpg=True)

W, H = 1200, 560
b = T(60, 70, "First, work out what's blocked", 34, 700, NAVY, "d")
b += T(60, 108, "Run a little water in each fixture and look for the pattern", 20, 500, MUTED)
cols = [("drop", "One fixture is slow", ["Just the basin, just the", "shower or just the sink"], "Usually a DIY fix", TEAL, TEAL50),
        ("bubbles", "Several are slow or gurgle", ["Toilet bubbles when the", "shower or washer drains"], "Main line, call a plumber", ORANGE, "#FFF1E8"),
        ("grate", "Water comes up outside", ["Sewage spills from the", "gully grate in the yard"], "Stop using water and call", RED, "#FDECEC")]
for i, (ic, h1, rows_, verdict, col, bgc) in enumerate(cols):
    bx = 60 + i * 370
    b += f'<rect x="{bx}" y="150" width="340" height="360" rx="18" fill="{SAND}" stroke="{LINE}"/>'
    b += f'<rect x="{bx + 28}" y="182" width="84" height="84" rx="18" fill="{bgc}"/>' + icon(ic, bx + 40, bx * 0 + 194, 60, col)
    b += T(bx + 28, 320, h1, 24, 700, NAVY, "d")
    b += lines(bx + 28, 362, rows_, 19, 500, MUTED)
    b += f'<rect x="{bx + 28}" y="426" width="284" height="56" rx="12" fill="{col}"/>' + T(bx + 170, 461, verdict, 19, 700, "#fff" if col != ORANGE else "#1A1206", anchor="middle")
add(S, "what-is-blocked", svg(W, H, b))

W, H = 1200, 660
b = T(60, 70, "Use the right plunger, and seal it properly", 34, 700, NAVY, "d")
b += T(60, 108, "Cup plunger for sinks and showers. Flange plunger for toilets.", 20, 500, MUTED)
# sink panel
b += f'<rect x="40" y="140" width="540" height="480" rx="16" fill="{SAND}"/>' + T(70, 186, "Sink, basin or shower", 24, 700, NAVY, "d")
b += f'<path d="M100 360 h420 v20 a90 90 0 0 1 -90 90 h-240 a90 90 0 0 1 -90 -90z" fill="#fff" stroke="#B9C7D4" stroke-width="3"/>'
b += f'<path d="M110 392 h400 a80 70 0 0 1 -80 70 h-240 a80 70 0 0 1 -80 -70z" fill="#CFE6F0"/>'
b += f'<rect x="300" y="226" width="20" height="140" rx="8" fill="{ROOT_C}"/><path d="M250 410 a60 40 0 0 1 120 0 z" fill="{ORANGE}"/>'
b += f'<circle cx="470" cy="378" r="12" fill="#fff" stroke="{TEAL}" stroke-width="4"/>'
b += f'<path d="M476 372 L530 300" stroke="{MUTED}" stroke-width="1.6" stroke-dasharray="4 4"/>' + lines(450, 270, ["Cover the", "overflow hole"], 18, 650, TEAL7)
b += lines(70, 530, ["Leave 5 cm of water in the sink.", "Pump firmly 15 to 20 times."], 19, 500, TEXT)
# toilet panel
b += f'<rect x="620" y="140" width="540" height="480" rx="16" fill="{SAND}"/>' + T(650, 186, "Toilet", 24, 700, NAVY, "d")
b += f'<path d="M760 300 h260 a20 20 0 0 1 20 20 c0 80 -60 130 -150 130 c-90 0 -150 -50 -150 -130 a20 20 0 0 1 20 -20z" fill="#fff" stroke="#B9C7D4" stroke-width="3"/>'
b += f'<path d="M790 330 h200 c0 60 -40 96 -100 96 c-60 0 -100 -36 -100 -96z" fill="#CFE6F0"/>'
b += f'<rect x="880" y="200" width="20" height="170" rx="8" fill="{ROOT_C}"/><path d="M836 400 a54 38 0 0 1 108 0 z" fill="{ORANGE}"/><rect x="872" y="396" width="36" height="28" rx="6" fill="#C24E10"/>'
b += f'<path d="M915 418 L1040 470" stroke="{MUTED}" stroke-width="1.6" stroke-dasharray="4 4"/>' + lines(1000, 492, ["Flange fits", "the outlet"], 18, 650, TEAL7)
b += lines(650, 530, ["Don't flush if the bowl is high.", "Stop after two rounds."], 19, 500, TEXT)
add(S, "plunger-technique", svg(W, H, b))

W, H = 1200, 700
b = T(60, 70, "Cleaning the trap under a basin", 34, 700, NAVY, "d")
b += T(60, 108, "Only if it unscrews by hand. Glued joints or a leak mean call a plumber.", 20, 500, MUTED)
b += f'<rect x="40" y="140" width="1120" height="520" rx="16" fill="{SAND}"/>'
# basin
b += f'<path d="M180 200 h420 v18 a70 70 0 0 1 -70 70 h-280 a70 70 0 0 1 -70 -70z" fill="#fff" stroke="#B9C7D4" stroke-width="3"/>'
b += f'<rect x="372" y="288" width="36" height="70" fill="#D9E1E8" stroke="#B9C7D4" stroke-width="2"/>'
b += f'<rect x="364" y="352" width="52" height="16" rx="4" fill="{TEAL}"/>'
b += f'<path d="M390 368 v60 a50 50 0 0 0 100 0 v-30 h150" stroke="#D9E1E8" stroke-width="34" fill="none"/>'
b += f'<path d="M390 368 v60 a50 50 0 0 0 100 0 v-30 h150" stroke="#B9C7D4" stroke-width="2" fill="none"/>'
b += f'<rect x="474" y="386" width="32" height="16" rx="4" fill="{TEAL}"/><rect x="560" y="382" width="16" height="32" rx="4" fill="{TEAL}"/>'
b += f'<rect x="640" y="372" width="120" height="52" fill="#C9D3DC"/><path d="M760 360 v76" stroke="{MUTED}" stroke-width="6"/>'
# bucket
b += f'<path d="M330 540 h220 l-18 100 h-184z" fill="{TEAL}"/><rect x="322" y="530" width="236" height="16" rx="6" fill="{TEAL7}"/>'
b += f'<path d="M384 360 L250 360" stroke="{MUTED}" stroke-width="1.6" stroke-dasharray="4 4"/><circle cx="390" cy="360" r="6" fill="{TEAL}" stroke="#fff" stroke-width="2"/>' + lines(240, 356, ["Slip nut", "(hand tight)"], 18, 650, NAVY, anchor="end")
b += callout(440, 470, 620, 520, ["The trap holds water", "and collects gunk"], 18, NAVY)
b += callout(440, 560, 620, 600, ["Bucket and towel", "underneath first"], 18, NAVY)
steps3 = ["1  Bucket and towel under the trap", "2  Unscrew slip nuts by hand", "3  Empty and scrub the trap", "4  Check washers, refit firmly", "5  Run the tap, check for leaks"]
b += f'<rect x="830" y="190" width="300" height="250" rx="14" fill="#fff" stroke="{LINE}"/>' + T(856, 232, "Steps", 22, 700, NAVY, "d")
b += lines(856, 274, steps3, 17, 550, TEXT, 2.0)
add(S, "sink-trap", svg(W, H, b))

W, H = 1200, 660
b = T(60, 70, "Signs it's time to call a plumber", 34, 700, NAVY, "d")
b += T(60, 108, "If you see any of these, stop using water and get help", 20, 500, MUTED)
signs = [("grate", "Water from the outdoor gully"), ("bubbles", "Several fixtures slow"), ("toilet", "Toilet gurgles when the shower runs"),
         ("nose", "Sewage smell outside"), ("repeat", "Same drain blocks again"), ("warn", "Two rounds of plunging failed")]
for i, (ic, lab) in enumerate(signs):
    r_, c_ = divmod(i, 3)
    bx, by = 60 + c_ * 370, 150 + r_ * 240
    b += f'<rect x="{bx}" y="{by}" width="340" height="210" rx="16" fill="#FFF5EE" stroke="#F8D6C2"/>'
    b += f'<rect x="{bx + 26}" y="{by + 26}" width="72" height="72" rx="16" fill="#fff"/>' + icon(ic, bx + 38, by + 38, 48, ORANGE)
    words = lab.split(" ")
    rows_, cur = [], ""
    for w_ in words:
        if len(cur + " " + w_) > 20: rows_.append(cur.strip()); cur = w_
        else: cur += " " + w_
    rows_.append(cur.strip())
    b += lines(bx + 26, by + 138, rows_, 22, 700, NAVY, 1.25, "d")
add(S, "warning-signs", svg(W, H, b))

# ======================= POST 4: is pipe relining worth it =======================
S = "is-pipe-relining-worth-it"
art = ""
for i, (ic, lab, col) in enumerate([("repeat", "Keep clearing", "#9FB4C7"), ("liner", "Reline", TEAL_L), ("dig", "Dig up", "#9FB4C7")]):
    bx, by = 760 + (i % 2) * 0, 110 + i * 150
    hi = i == 1
    art += f'<rect x="{bx}" y="{by}" width="360" height="124" rx="18" fill="{"#fff" if hi else "#fff"}" fill-opacity="{1 if hi else .07}" stroke="#fff" stroke-opacity="{0 if hi else .16}"/>'
    art += icon(ic, bx + 28, by + 34, 56, TEAL if hi else "#C8D6E3")
    art += T(bx + 108, by + 74, lab, 32, 700, NAVY if hi else "#E6EEF5", "d")
    if hi:
        art += f'<rect x="{bx + 250}" y="{by + 44}" width="86" height="36" rx="18" fill="{ORANGE}"/>' + T(bx + 293, by + 69, "Often", 18, 700, "#1A1206", anchor="middle")
add(S, "cover", cover("Honest comparison", ["Is pipe relining", "worth it?"], ["10-year cost maths", "9 pros and cons"], art), jpg=True)

# ten-year cumulative cost
W, H = 1200, 700
x0, y0, cw, ch = 150, 160, 900, 420
mx = 15000
b = T(60, 70, "Ten-year cost: repeat clearing vs one reline", 34, 700, NAVY, "d")
b += T(60, 108, "Six metres of root-damaged pipe. $700 per clear, relining about $5,500 once.", 20, 500, MUTED)
for v in range(0, mx + 1, 5000):
    yy = y0 + ch - v / mx * ch
    b += f'<line x1="{x0}" y1="{yy}" x2="{x0 + cw}" y2="{yy}" stroke="{LINE}" stroke-width="1.5"/>' + T(x0 - 16, yy + 7, f"${v:,}", 18, 500, MUTED, anchor="end")
for yr in range(0, 11, 2):
    xx = x0 + yr / 10 * cw
    b += T(xx, y0 + ch + 34, f"Year {yr}", 18, 550, MUTED, anchor="middle")
def ptsf(f): return " ".join(f"{x0 + t / 10 * cw:.1f},{y0 + ch - f(t) / mx * ch:.1f}" for t in [i / 4 for i in range(41)])
import math
twice = lambda t: 700 * math.floor(t * 2 + 1e-9) + 0
once = lambda t: 700 * math.floor(t + 1e-9)
step_pts = lambda per: " ".join(f"{x0 + t / 10 * cw:.1f},{y0 + ch - min(per(t), mx) / mx * ch:.1f}" for t in [i / 100 for i in range(1001)])
b += f'<polyline points="{step_pts(twice)}" fill="none" stroke="{ORANGE}" stroke-width="4"/>'
b += f'<polyline points="{step_pts(once)}" fill="none" stroke="#E0A030" stroke-width="4" stroke-dasharray="10 6"/>'
ry = y0 + ch - 5500 / mx * ch
b += f'<line x1="{x0}" y1="{ry}" x2="{x0 + cw}" y2="{ry}" stroke="{TEAL}" stroke-width="5"/>'
b += f'<line x1="{x0}" y1="{y0 + ch}" x2="{x0 + cw}" y2="{y0 + ch}" stroke="{MUTED}" stroke-width="2"/>'
b += T(x0 + cw + 12, y0 + ch - 14000 / mx * ch + 6, "Clear twice", 18, 700, "#C24E10") + T(x0 + cw + 12, y0 + ch - 14000 / mx * ch + 28, "a year", 18, 700, "#C24E10")
b += T(x0 + cw + 12, y0 + ch - 7000 / mx * ch - 24, "Clear once", 18, 700, "#A86E0C") + T(x0 + cw + 12, y0 + ch - 7000 / mx * ch - 2, "a year", 18, 700, "#A86E0C")
b += T(x0 + cw + 12, ry + 30, "Reline", 18, 700, TEAL7) + T(x0 + cw + 12, ry + 52, "once", 18, 700, TEAL7)
for yr_, lab in ((4, "about year 4"), (8, "about year 8")):
    xx = x0 + yr_ / 10 * cw
    b += f'<circle cx="{xx}" cy="{ry}" r="9" fill="#fff" stroke="{NAVY}" stroke-width="3"/>' + T(xx + 14, ry + 40, lab, 17, 700, NAVY, anchor="start", extra='stroke="#fff" stroke-width="5" paint-order="stroke"')
b += T(60, H - 24, "Illustration based on 2026 Australian price guides (Oneflare, The Quote Yard). Your numbers will differ.", 16, 500, MUTED)
add(S, "ten-year-cost", svg(W, H, b))

W, H = 1200, 720
b = T(60, 70, "Pipe relining: pros and cons", 34, 700, NAVY, "d")
b += T(60, 108, "Strongest when the pipe still holds its shape and sits under something you don't want to dig up", 20, 500, MUTED)
pros = ["No trench, yard stays intact", "Usually done in one day", "Roots can't get in along the liner", "Smooth inside, flows well", "25 to 50 year warranties are common"]
cons = ["Can't fix a collapsed or sagging pipe", "Digging can be cheaper under lawn", "Quality depends on the installer", "Usually a one-time fix per section"]
for side, (title, items, col, bgc, mark) in enumerate([("Pros", pros, TEAL, TEAL50, "+"), ("Cons", cons, ORANGE, "#FFF5EE", "–")]):
    bx = 60 + side * 550
    b += f'<rect x="{bx}" y="150" width="520" height="520" rx="18" fill="{bgc}"/>'
    b += T(bx + 32, 204, title, 30, 750, NAVY, "d")
    for j, it in enumerate(items):
        yy = 260 + j * 82
        b += f'<circle cx="{bx + 50}" cy="{yy}" r="18" fill="{col}"/>' + T(bx + 50, yy + 8, mark, 24, 800, "#fff" if col == TEAL else "#1A1206", anchor="middle")
        b += T(bx + 84, yy + 8, it, 21, 600, TEXT)
add(S, "pros-cons", svg(W, H, b))

W, H = 1200, 800
b = T(60, 70, "Is relining right for your pipe?", 34, 700, NAVY, "d")
b += T(60, 108, "A simple way to decide. Start with the camera footage.", 20, 500, MUTED)
def box(x, y, w, h, rows_, fill, fg, size=21):
    g = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}"/>'
    n = len(rows_)
    return g + lines(x + w / 2, y + h / 2 - (n - 1) * size * 0.67 + size * 0.35, rows_, size, 700, fg, 1.35, "b", "middle")
def arrow(x1, y1, x2, y2, lab=None, lx=None, ly=None):
    g = f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{MUTED}" stroke-width="2.5" marker-end="url(#ah)"/>'
    if lab: g += T(lx, ly, lab, 17, 700, MUTED, anchor="middle")
    return g
b += f'<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 0 10 5 0 10z" fill="{MUTED}"/></marker></defs>'
b += '<g transform="translate(-150 0)">' + box(420, 140, 360, 70, ["Camera inspection"], NAVY, "#fff")
b += arrow(600, 210, 600, 250)
b += box(380, 252, 440, 84, ["Is the pipe collapsed", "or sagging?"], SAND, NAVY)
b += arrow(820, 294, 900, 294, "Yes", 860, 284)
b += box(902, 252, 260, 84, ["Dig up that section", "(reline the rest)"], "#FFF1E8", "#9A3A0A", 19)
b += arrow(600, 336, 600, 380, "No", 624, 364)
b += box(380, 382, 440, 84, ["Under concrete, tiles,", "a pool or trees?"], SAND, NAVY)
b += arrow(820, 424, 900, 424, "Yes", 860, 414)
b += box(902, 382, 260, 84, ["Relining is", "usually best"], TEAL, "#fff", 20)
b += arrow(600, 466, 600, 510, "No", 624, 494)
b += box(380, 512, 440, 84, ["Blocks more than", "once a year?"], SAND, NAVY)
b += arrow(820, 554, 900, 554, "Yes", 860, 544)
b += box(902, 512, 260, 84, ["Compare reline and", "dig-up quotes"], TEAL50, TEAL7, 19)
b += arrow(600, 596, 600, 640, "No", 624, 624)
b += box(380, 642, 440, 84, ["Clear it and keep an eye", "on it for now"], SAND, NAVY) + "</g>"
b += T(60, H - 30, "A general guide only. A licensed plumber's camera inspection decides what your pipe needs.", 16, 500, MUTED)
add(S, "decision-flowchart", svg(W, H, b))

W, H = 1200, 600
b = T(60, 70, "How long pipes last: commonly quoted ranges", 34, 700, NAVY, "d")
b += T(60, 108, "Years of service. Real life depends on the product, installation and what goes down the drain.", 20, 500, MUTED)
x0, cw = 330, 780
mxy = 70
for v in range(0, mxy + 1, 10):
    xx = x0 + v / mxy * cw
    b += f'<line x1="{xx}" y1="150" x2="{xx}" y2="470" stroke="{LINE}" stroke-width="1.5"/>' + T(xx, 500, f"{v}", 18, 500, MUTED, anchor="middle")
b += T(x0 + cw / 2, 534, "Years", 18, 600, MUTED, anchor="middle")
xx = x0 + 51 / mxy * cw
b += f'<line x1="{xx}" y1="150" x2="{xx}" y2="470" stroke="{ORANGE}" stroke-width="3" stroke-dasharray="6 5"/>'
bars = [("Relining warranty", 25, 50, TEAL), ("New PVC sewer pipe", 40, 60, NAVY7), ("Clay sewer pipe", 50, 60, CLAY)]
for i, (lab, a, z, col) in enumerate(bars):
    yy = 180 + i * 100
    b += T(60, yy + 30, lab, 21, 650, NAVY)
    b += f'<rect x="{x0 + a / mxy * cw}" y="{yy}" width="{(z - a) / mxy * cw}" height="44" rx="10" fill="{col}"/>'
    b += T(x0 + (a + z) / 2 / mxy * cw, yy + 29, f"{a} to {z}", 19, 700, "#fff", anchor="middle")
xx = x0 + 51 / mxy * cw
b += T(xx - 10, 160, "A 1975 clay pipe today: 51 years", 17, 700, "#C24E10", anchor="end")
b += T(60, H - 24, "Sources: North East Plumbing; The Quote Yard. Warranty terms vary by installer.", 16, 500, MUTED)
add(S, "lifespan", svg(W, H, b))

# ======================= logo for schema =======================
LOGO = svg(512, 512, f'<rect width="512" height="512" rx="112" fill="{NAVY}"/><path d="M128 166h147a77 77 0 0 1 77 77v128" fill="none" stroke="{ORANGE}" stroke-width="64" stroke-linecap="round"/><path d="M128 166h147a77 77 0 0 1 77 77v128" fill="none" stroke="#fff" stroke-width="20" stroke-linecap="round"/>', NAVY)

def main():
    manifest = {}
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(device_scale_factor=1)
        def shot(markup):
            w = int(markup.split('width="')[1].split('"')[0]); h = int(markup.split('height="')[1].split('"')[0])
            pg.set_viewport_size({"width": w, "height": h})
            pg.set_content(f"<html><head><style>{CSS}</style></head><body>{markup}</body></html>")
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(120)
            return Image.open(io.BytesIO(pg.screenshot(full_page=False))).convert("RGB"), w, h
        for path, (markup, jpg) in IMAGES.items():
            img, w, h = shot(markup)
            out = ROOT / "public" / path.lstrip("/")
            out.parent.mkdir(parents=True, exist_ok=True)
            img.save(out, "WEBP", quality=84, method=6)
            small = img.resize((600, round(h * 600 / w)), Image.LANCZOS)
            small.save(out.with_name(out.stem + "-600.webp"), "WEBP", quality=82, method=6)
            if jpg:
                img.save(out.with_suffix(".jpg"), "JPEG", quality=84, optimize=True, progressive=True)
            manifest[path] = {"w": w, "h": h}
            print(f"{path:60} {w}x{h} {out.stat().st_size // 1024} KB")
        img, _, _ = shot(LOGO)
        img.save(ROOT / "public/logo.png", "PNG", optimize=True)
        br.close()
    (ROOT / "src/data/blog-images.json").write_text(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
