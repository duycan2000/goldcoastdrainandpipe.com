"""Homepage illustrations, drawn as SVG and rendered to WebP in public/img/home/.
Run from the project root: python3 scripts/home_images.py
Adds each image's size to src/data/blog-images.json (same manifest the blog uses)."""
import json, io, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from blog_images import CSS, T, lines, icon, NAVY, NAVY9, NAVY7, TEAL, TEAL7, TEAL_L, TEAL50, ORANGE, SAND, LINE, MUTED, TEXT, CLAY, CLAY_D, ROOT_C
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "public/img/home"
IMGS = {}  # name -> (svg, w, h, scale, transparent)

def svg(w, h, body, bg=None):
    rect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{rect}{body}</svg>'

def label(x, y, text, size=11, anchor="start", bg="#fff", fg=NAVY, dot=None):
    w = len(text) * size * 0.56 + 18
    x0 = x if anchor == "start" else (x - w if anchor == "end" else x - w / 2)
    g = f'<g filter="url(#sh)"><rect x="{x0}" y="{y - size - 5}" width="{w}" height="{size + 12}" rx="{(size + 12) / 2}" fill="{bg}"/></g>'
    if dot: g += f'<circle cx="{x0 + 10}" cy="{y - size / 2 + 1}" r="3.5" fill="{dot}"/>'
    g += T(x0 + (16 if dot else 9), y, text, size, 650, fg)
    return g

EXTRA = {"user": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
         "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>'}
def icon2(name, x, y, s=48, color=TEAL):
    return f'<g transform="translate({x},{y}) scale({s/24})" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{EXTRA[name]}</g>'

SHADOW = '<filter id="sh" x="-20%" y="-40%" width="140%" height="200%"><feDropShadow dx="0" dy="2" stdDeviation="2.5" flood-color="#06121F" flood-opacity=".35"/></filter>'

# ============ 1. HERO SCENE (transparent, sits on the navy hero) ============
W, H = 640, 300
g = f'''<defs>{SHADOW}
<linearGradient id="soil" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6E4C33"/><stop offset=".55" stop-color="#4A3424"/><stop offset="1" stop-color="#4A3424" stop-opacity="0"/></linearGradient>
<linearGradient id="grass" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6CC070"/><stop offset="1" stop-color="#3F8F4E"/></linearGradient>
<radialGradient id="glow" cx=".72" cy=".55" r=".55"><stop offset="0" stop-color="{ORANGE}" stop-opacity=".45"/><stop offset=".5" stop-color="{ORANGE}" stop-opacity=".12"/><stop offset="1" stop-color="{ORANGE}" stop-opacity="0"/></radialGradient>
<linearGradient id="pipe" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9D7C6"/><stop offset=".5" stop-color="#C99B76"/><stop offset="1" stop-color="#8E623F"/></linearGradient>
<linearGradient id="beam" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#FFE7A3" stop-opacity=".95"/><stop offset="1" stop-color="#FFE7A3" stop-opacity="0"/></linearGradient>
<linearGradient id="van" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#D5DEE7"/></linearGradient>
<mask id="fade"><rect width="{W}" height="{H}" fill="url(#fadeG)"/></mask>
<linearGradient id="fadeG" x1="0" y1="0" x2="0" y2="1"><stop offset=".7" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>
</defs>'''
g += f'<rect x="0" y="0" width="{W}" height="160" fill="url(#glow)"/>'
# skyline (Surfers Paradise towers, generic silhouettes)
towers = [(330, 70, 18), (352, 46, 16), (372, 84, 20), (396, 30, 14), (414, 62, 22), (440, 92, 16), (460, 54, 18), (482, 100, 14), (500, 76, 20), (524, 110, 16), (546, 88, 18), (568, 118, 14)]
for x, top, w in towers:
    g += f'<rect x="{x}" y="{top}" width="{w}" height="{150 - top}" fill="#2A5478" opacity=".55"/>'
    for yy in range(top + 8, 140, 10):
        g += f'<rect x="{x + 4}" y="{yy}" width="{w - 8}" height="2" fill="#FFD58A" opacity=".18"/>'
g += f'<path d="M396 30 l7 -14 l7 14z" fill="#2A5478" opacity=".55"/>'  # spire
g += f'<g mask="url(#fade)"><rect x="0" y="156" width="{W}" height="{H - 156}" fill="url(#soil)"/></g>'
g += f'<rect x="0" y="149" width="{W}" height="9" fill="url(#grass)"/>'
# footpath + kerb at the street side
g += f'<rect x="392" y="149" width="248" height="9" fill="#9AA9B6"/><rect x="392" y="147" width="248" height="3" fill="#C9D3DC"/>'
g += f'<line x1="388" y1="150" x2="388" y2="300" stroke="#fff" stroke-opacity=".35" stroke-dasharray="3 4"/>'
g += T(380, 292, "Your property", 9, 650, "#E9D9C9", anchor="end") + T(396, 292, "Council sewer", 9, 650, "#E9D9C9")
# house
g += f'''<g filter="url(#sh)">
<rect x="56" y="98" width="142" height="52" rx="2" fill="#F4F7FA"/>
<path d="M46 101 L127 58 L208 101 Z" fill="#2C4A66"/><path d="M46 101 L127 58 L208 101" fill="none" stroke="#1B354D" stroke-width="3"/>
<rect x="138" y="70" width="40" height="14" rx="1.5" fill="#3C6A92" transform="skewX(-20) translate(30 0)"/>
<rect x="72" y="112" width="34" height="22" rx="1.5" fill="#FFD58A"/><path d="M89 112v22M72 123h34" stroke="#F4F7FA" stroke-width="2"/>
<rect x="150" y="112" width="30" height="38" rx="1.5" fill="#1D4366"/><circle cx="174" cy="132" r="1.6" fill="#FFD58A"/>
</g>'''
# palm tree
g += f'<path d="M262 150 C 260 120, 266 96, 274 74" stroke="#8A6A45" stroke-width="6" fill="none" stroke-linecap="round"/>'
for d in ("M274 74 c -18 -4 -32 2 -40 12", "M274 74 c -10 -14 -26 -18 -38 -14", "M274 74 c 6 -16 22 -22 36 -18", "M274 74 c 18 -2 32 6 38 18", "M274 74 c 2 -14 -4 -26 -12 -32"):
    g += f'<path d="{d}" stroke="#4CAF6A" stroke-width="7" fill="none" stroke-linecap="round"/>'
# underground pipe: house drop, slope to the sewer main
g += f'<path d="M150 158 V 200 Q 150 208 158 208 L 590 236" stroke="#5B3E28" stroke-width="22" fill="none" stroke-linecap="round" opacity=".6"/>'
g += f'<path d="M150 158 V 200 Q 150 208 158 208 L 590 236" stroke="url(#pipe)" stroke-width="16" fill="none" stroke-linecap="round"/>'
for jx in range(200, 580, 46):
    jy = 208 + (jx - 158) / (590 - 158) * 28
    g += f'<rect x="{jx - 2.5}" y="{jy - 10}" width="5" height="20" rx="1.5" fill="#7A5232" transform="rotate(3.7 {jx} {jy})"/>'
# inspection opening riser
g += f'<rect x="336" y="148" width="12" height="70" fill="#C99B76"/><rect x="331" y="143" width="22" height="8" rx="2" fill="#E9D7C6"/>'
# sewer main
g += f'<circle cx="604" cy="238" r="22" fill="#2E6F75"/><circle cx="604" cy="238" r="15" fill="#18484D"/>'
# roots from the palm into a joint
rx, ry = 246, 211
for d in (f"M262 158 C 258 176, 250 190, {rx} {ry - 4}", f"M262 158 C 270 178, 258 196, {rx + 6} {ry - 2}", f"M258 168 C 244 178, 238 192, {rx - 4} {ry}", f"M{rx} {ry - 2} c 4 3 6 6 2 9", f"M{rx + 4} {ry} c -5 2 -7 6 -3 8"):
    g += f'<path d="{d}" stroke="#D9B48A" stroke-width="2.2" fill="none" stroke-linecap="round"/>'
g += f'<circle cx="{rx + 2}" cy="{ry + 1}" r="17" fill="none" stroke="{ORANGE}" stroke-width="2.5"/><circle cx="{rx + 2}" cy="{ry + 1}" r="24" fill="none" stroke="{ORANGE}" stroke-width="1.5" opacity=".45"/>'
# CCTV camera crawler heading towards the roots, with light beam
cx, cy = 300, 214
g += f'<path d="M{cx - 6} {cy - 4} L {rx + 18} {ry - 10} L {rx + 18} {ry + 12} L {cx - 6} {cy + 3} Z" fill="url(#beam)"/>'
g += f'<rect x="{cx - 6}" y="{cy - 6}" width="20" height="10" rx="3" fill="#F2F5F8" stroke="#1D4366" stroke-width="1.5"/><circle cx="{cx - 6}" cy="{cy - 1}" r="3" fill="#FFE7A3"/>'
g += f'<path d="M{cx + 14} {cy - 1} L 338 218" stroke="#FFB27A" stroke-width="1.5" fill="none"/>'
# van at the kerb
g += f'''<g filter="url(#sh)" transform="translate(452 104)">
<path d="M0 10 Q0 2 8 2 H86 Q96 2 104 14 L118 30 Q122 34 122 40 V44 H0 Z" fill="url(#van)"/>
<path d="M90 8 H100 L114 28 H90 Z" fill="#9CC3DE"/>
<rect x="0" y="24" width="88" height="6" fill="{ORANGE}"/>
<rect x="6" y="10" width="26" height="9" rx="2" fill="{NAVY}"/><path d="M10 14.5h18" stroke="{ORANGE}" stroke-width="2"/>
<circle cx="24" cy="44" r="9" fill="#1B2A38"/><circle cx="24" cy="44" r="3.5" fill="#B9C7D4"/>
<circle cx="98" cy="44" r="9" fill="#1B2A38"/><circle cx="98" cy="44" r="3.5" fill="#B9C7D4"/>
</g>'''
# labels
g += label(150, 272, "Roots found at a joint, 4.2 m in", 13, dot=ORANGE)
g += label(14, 186, "Camera inspection, no digging", 13, dot=TEAL_L)
g += f'<path d="M150 186 L 292 210" stroke="#fff" stroke-opacity=".5" stroke-width="1" stroke-dasharray="2 3"/>'
g += label(430, 90, "Local, licensed plumber", 13, dot="#6CC070")
IMGS["hero-scene"] = (svg(W, H, g), W, H, 2, True)

# ============ 2. HOW IT WORKS: three illustrated panels (transparent) ============
W, H = 1200, 360
def card(x, inner, tint):
    return (f'<g filter="url(#sh2)"><rect x="{x}" y="10" width="370" height="330" rx="20" fill="#fff"/></g>'
            f'<rect x="{x + 14}" y="24" width="342" height="302" rx="14" fill="{tint}"/>' + inner)
g = f'<defs><filter id="sh2" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#0C2236" flood-opacity=".12"/></filter>{SHADOW}</defs>'
# 1: phone call
p = f'<g transform="translate(118 44)"><rect width="150" height="270" rx="24" fill="{NAVY9}"/><rect x="8" y="8" width="134" height="254" rx="18" fill="#163A5A"/>'
p += f'<rect x="55" y="16" width="40" height="7" rx="3.5" fill="{NAVY9}"/>'
p += f'<circle cx="75" cy="86" r="30" fill="{TEAL}"/>' + icon2("user", 57, 68, 36, "#fff")
p += T(75, 140, "Drain & Pipe", 14, 700, "#fff", "d", "middle") + T(75, 160, "Gold Coast", 11, 500, "#9FB4C7", anchor="middle")
p += T(75, 186, "Calling…  0:12", 11, 600, TEAL_L, anchor="middle")
p += f'<circle cx="44" cy="226" r="17" fill="#E5484D"/><circle cx="106" cy="226" r="17" fill="#30A46C"/>' + icon2("phone", 33, 215, 22, "#fff") + icon2("phone", 95, 215, 22, "#fff")
p += '</g>'
p += f'<g transform="translate(272 70)">{label(0, 0, "Under a minute", 11, bg=ORANGE, fg="#1A1206")}</g>'
g += card(20, p, TEAL50)
# 2: plumber on the way (map)
m = '<g transform="translate(414 24)"><clipPath id="mc"><rect width="342" height="302" rx="14"/></clipPath><g clip-path="url(#mc)">'
m += '<rect width="342" height="302" fill="#EAF0F4"/>'
for x in (40, 120, 210, 290): m += f'<rect x="{x}" y="0" width="14" height="302" fill="#fff"/>'
for y in (50, 130, 210, 270): m += f'<rect x="0" y="{y}" width="342" height="14" fill="#fff"/>'
m += '<rect x="140" y="150" width="60" height="45" rx="6" fill="#CFE6D2"/><rect x="230" y="70" width="50" height="50" rx="6" fill="#CFE6D2"/>'
m += f'<path d="M47 285 V 137 H 217 V 57 H 297" stroke="{TEAL}" stroke-width="5" fill="none" stroke-dasharray="1 10" stroke-linecap="round"/>'
m += f'<g transform="translate(22 252)"><rect width="50" height="26" rx="6" fill="#fff" stroke="{NAVY}" stroke-width="2"/><rect y="12" width="34" height="4" fill="{ORANGE}"/><circle cx="12" cy="27" r="5" fill="{NAVY}"/><circle cx="40" cy="27" r="5" fill="{NAVY}"/></g>'
m += f'<g transform="translate(297 57)"><path d="M0 0 c -14 -16 -14 -34 0 -34 c 14 0 14 18 0 34z" fill="{ORANGE}" transform="translate(0 -2)"/><circle cx="0" cy="-22" r="5" fill="#fff"/></g>'
m += '</g>' + label(18, 32, "Plumber on the way", 12, dot=TEAL) + '</g>'
g += card(415, m, "#EAF0F4")
# 3: camera result + price agreed
c = f'<g transform="translate(830 50)"><rect width="300" height="200" rx="14" fill="{NAVY9}"/><rect x="10" y="10" width="280" height="180" rx="8" fill="#0E1B26"/>'
c += '<defs><radialGradient id="tun" cx=".5" cy=".55" r=".6"><stop offset="0" stop-color="#05090D"/><stop offset=".35" stop-color="#3B4D57"/><stop offset=".75" stop-color="#8FA8B2"/><stop offset="1" stop-color="#C9D8DE"/></radialGradient></defs>'
c += '<rect x="10" y="10" width="280" height="180" rx="8" fill="url(#tun)" opacity=".9"/>'
for r_ in (110, 80, 54, 32): c += f'<ellipse cx="150" cy="108" rx="{r_}" ry="{r_ * .62}" fill="none" stroke="#E6F1F4" stroke-opacity=".25" stroke-width="2"/>'
c += f'<circle cx="28" cy="28" r="5" fill="#E5484D"/>' + T(38, 32, "REC", 11, 700, "#fff") + T(280, 32, "04.2 m", 11, 700, "#fff", anchor="end")
c += '</g>'
c += f'<g transform="translate(850 268)">{label(0, 14, "Drain cleared", 13, dot="#30A46C")}{label(140, 14, "Price agreed first", 13, dot=ORANGE)}</g>'
g += card(810, c, "#EEF1F6")
IMGS["how-it-works"] = (svg(W, H, g), W, H, 1, True)

# ============ 3. CCTV BEFORE / AFTER ============
W, H = 1200, 600
def tunnel(x, y, w, h, kind):
    cx, cy = x + w / 2, y + h * .55
    gid = f"t{kind}"
    if kind == "before":
        stops = '<stop offset="0" stop-color="#020304"/><stop offset=".22" stop-color="#2A1A10"/><stop offset=".6" stop-color="#7A4E30"/><stop offset="1" stop-color="#C8946A"/>'
    else:
        stops = '<stop offset="0" stop-color="#020304"/><stop offset=".22" stop-color="#14262A"/><stop offset=".6" stop-color="#5E8C8F"/><stop offset="1" stop-color="#B9D9D8"/>'
    s = f'<defs><radialGradient id="{gid}" cx="{(cx - x) / w}" cy="{(cy - y) / h}" r=".75">{stops}</radialGradient><clipPath id="c{gid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/></clipPath></defs>'
    s += f'<g clip-path="url(#c{gid})"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{gid})"/>'
    if kind == "before":
        for k, r_ in enumerate((330, 230, 160, 110, 74, 48)):
            s += f'<ellipse cx="{cx}" cy="{cy}" rx="{r_}" ry="{r_ * .74}" fill="none" stroke="#3A2416" stroke-width="{7 - k}" opacity=".75"/>'
            s += f'<ellipse cx="{cx}" cy="{cy - 2}" rx="{r_}" ry="{r_ * .74}" fill="none" stroke="#E2B48C" stroke-width="1.5" opacity=".35"/>'
        # roots hanging from the joint at r=160
        import random
        random.seed(7)
        for i in range(34):
            a = random.uniform(-2.6, -0.5)
            import math
            sx, sy = cx + 160 * math.cos(a), cy + 160 * .74 * math.sin(a)
            ex, ey = cx + random.uniform(-60, 60), cy + random.uniform(-20, 70)
            mx, my = (sx + ex) / 2 + random.uniform(-40, 40), (sy + ey) / 2 + random.uniform(-10, 40)
            col = random.choice(["#C9A27A", "#B08660", "#E3C59E", "#8A6340"])
            s += f'<path d="M{sx:.0f} {sy:.0f} Q {mx:.0f} {my:.0f} {ex:.0f} {ey:.0f}" stroke="{col}" stroke-width="{random.uniform(1.2, 3.4):.1f}" fill="none" stroke-linecap="round" opacity=".9"/>'
        # crack + standing water
        s += f'<path d="M{cx + 120} {cy - 150} l -10 30 l 14 20 l -8 34" stroke="#1A0F08" stroke-width="3" fill="none"/>'
        s += f'<ellipse cx="{cx}" cy="{cy + 150}" rx="230" ry="46" fill="#3E3324" opacity=".85"/><ellipse cx="{cx - 30}" cy="{cy + 140}" rx="120" ry="10" fill="#E9D3B0" opacity=".25"/>'
    else:
        for k, r_ in enumerate((330, 200, 120, 70)):
            s += f'<ellipse cx="{cx}" cy="{cy}" rx="{r_}" ry="{r_ * .74}" fill="none" stroke="#E8F6F5" stroke-width="1.2" opacity=".18"/>'
        s += f'<path d="M{cx - 260} {cy - 120} Q {cx - 120} {cy - 190} {cx + 40} {cy - 170}" stroke="#fff" stroke-width="22" fill="none" opacity=".18" stroke-linecap="round"/>'
        s += f'<ellipse cx="{cx}" cy="{cy + 160}" rx="200" ry="18" fill="#DDF3F1" opacity=".28"/>'
    s += f'<ellipse cx="{cx}" cy="{cy}" rx="36" ry="26" fill="#000" opacity=".9"/></g>'
    # HUD
    s += f'<circle cx="{x + 26}" cy="{y + 28}" r="6" fill="#E5484D"/>' + T(x + 40, y + 34, "REC", 15, 700, "#fff")
    s += T(x + w - 20, y + 34, "04.2 m" if kind == "before" else "04.2 m", 15, 700, "#fff", anchor="end")
    s += T(x + w - 20, y + h - 18, "CAM 1 · 100 mm SEWER", 12, 650, "#fff", anchor="end", extra='opacity=".85"')
    s += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="none" stroke="#0C2236" stroke-width="10"/>'
    return s
g = f'<defs>{SHADOW}</defs>'
g += T(60, 62, "What the drain camera sees", 34, 700, NAVY, "d") + T(60, 98, "Illustration of a root-damaged clay sewer before and after relining", 19, 500, MUTED)
g += tunnel(40, 130, 548, 380, "before") + tunnel(612, 130, 548, 380, "after")
g += f'<rect x="60" y="458" width="300" height="38" rx="19" fill="{ORANGE}"/>' + T(210, 483, "Before: roots at a joint", 18, 750, "#1A1206", anchor="middle")
g += f'<rect x="632" y="458" width="330" height="38" rx="19" fill="{TEAL}"/>' + T(797, 483, "After: relined, smooth, sealed", 18, 750, "#fff", anchor="middle")
g += lines(60, 552, ["Blocks every few months: roots keep", "growing back through the open joint."], 18, 600, TEXT, 1.3)
g += lines(632, 552, ["No joints for roots to find.", "Usually done in a day, no digging."], 18, 600, TEXT, 1.3)
IMGS["cctv-before-after"] = (svg(W, H, g, "#fff"), W, H, 1, False)

# ============ 4. GOLD COAST COVERAGE MAP ============
W, H = 420, 508
LON0, LON1, LAT0, LAT1 = 153.20, 153.60, -27.74, -28.215
def P(lon, lat): return ((lon - LON0) / (LON1 - LON0) * W, (lat - LAT0) / (LAT1 - LAT0) * H)
coast = [(153.432, -27.74), (153.430, -27.86), (153.428, -27.955), (153.432, -28.0), (153.44, -28.05), (153.455, -28.09), (153.47, -28.115), (153.487, -28.145), (153.52, -28.16), (153.545, -28.166), (153.56, -28.2)]
land = "M0 0 " + " ".join(f"L{P(*c)[0]:.1f} {P(*c)[1]:.1f}" for c in coast) + f" L0 {H} Z"
bw = [(153.405, -27.80), (153.418, -27.84), (153.42, -27.90), (153.415, -27.95), (153.405, -27.965), (153.396, -27.95), (153.395, -27.90), (153.40, -27.84)]
broadwater = "M" + " L".join(f"{P(*c)[0]:.1f} {P(*c)[1]:.1f}" for c in bw) + "Z"
g = f'''<defs>{SHADOW}
<linearGradient id="sea" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#BFE3EA"/><stop offset="1" stop-color="#8FCFDB"/></linearGradient>
<linearGradient id="hinter" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#CFE3C7"/><stop offset=".55" stop-color="#F3EFE6" stop-opacity="0"/></linearGradient>
<pattern id="waves" width="28" height="12" patternUnits="userSpaceOnUse"><path d="M0 9 q10 -6 20 0 t20 0" fill="none" stroke="#fff" stroke-opacity=".35"/></pattern></defs>'''
g += f'<rect width="{W}" height="{H}" fill="url(#sea)"/><rect width="{W}" height="{H}" fill="url(#waves)"/>'
g += f'<path d="{land}" fill="#F3EFE6"/><path d="{land}" fill="url(#hinter)"/>'
g += f'<path d="{land}" fill="none" stroke="#fff" stroke-width="5" opacity=".9"/>'
g += f'<path d="{broadwater}" fill="#A9D9E2"/>'
# M1 motorway
m1 = [(153.24, -27.74), (153.27, -27.80), (153.31, -27.86), (153.325, -27.93), (153.34, -28.0), (153.37, -28.06), (153.42, -28.11), (153.47, -28.15), (153.52, -28.17)]
g += f'<path d="M' + " L".join(f"{P(*c)[0]:.1f} {P(*c)[1]:.1f}" for c in m1) + '" fill="none" stroke="#F0B43C" stroke-width="5" stroke-linecap="round" opacity=".8"/>'
x, y = P(153.31, -27.86); g += f'<rect x="{x - 18}" y="{y - 10}" width="36" height="20" rx="4" fill="#2E7D32"/>' + T(x, y + 6, "M1", 13, 800, "#fff", anchor="middle")
# NSW border
bx1, by1 = P(153.55, -28.168); bx2, by2 = P(153.20, -28.19)
g += f'<path d="M{bx1} {by1} L{bx2} {by2}" stroke="{MUTED}" stroke-width="2" stroke-dasharray="8 6"/>' + T(250, by2 - 8, "QLD", 11, 700, MUTED) + T(250, by2 + 14, "NSW", 11, 700, MUTED)
x, y = P(153.53, -27.9); g += T(x, y, "Coral Sea", 15, 600, "#2C7A88", "d", "middle", 'font-style="italic"')
x, y = P(153.408, -27.88); g += T(x, y, "Broadwater", 11, 600, "#2C7A88", anchor="middle", extra=f'transform="rotate(-80 {x} {y})"')
REG = {"N": TEAL, "C": NAVY, "S": ORANGE}
subs = [  # name, lon, lat, region, label side, has own page
    ("Ormeau", 153.255, -27.77, "N", "e", 0), ("Pimpama", 153.30, -27.81, "N", "e", 0), ("Upper Coomera", 153.29, -27.875, "N", "", 0),
    ("Coomera", 153.34, -27.855, "N", "e", 1), ("Hope Island", 153.36, -27.875, "N", "", 0), ("Oxenford", 153.31, -27.89, "N", "", 0),
    ("Helensvale", 153.335, -27.92, "N", "w", 1), ("Paradise Point", 153.39, -27.885, "N", "", 0), ("Runaway Bay", 153.395, -27.915, "N", "", 0), ("Coombabah", 153.37, -27.91, "N", "", 0),
    ("Labrador", 153.40, -27.945, "C", "", 0), ("Southport", 153.405, -27.97, "C", "w", 1), ("Arundel", 153.37, -27.94, "C", "", 0), ("Ashmore", 153.38, -27.99, "C", "", 0),
    ("Surfers Paradise", 153.43, -28.0, "C", "e", 0), ("Benowa", 153.39, -28.005, "C", "", 0), ("Bundall", 153.405, -28.01, "C", "", 0), ("Nerang", 153.335, -28.0, "C", "w", 1),
    ("Carrara", 153.37, -28.02, "C", "", 0), ("Broadbeach", 153.432, -28.03, "C", "e", 0), ("Mermaid Beach", 153.437, -28.045, "C", "", 0), ("Worongary", 153.345, -28.05, "C", "", 0),
    ("Robina", 153.385, -28.075, "C", "w", 1), ("Mudgeeraba", 153.36, -28.083, "C", "", 0), ("Varsity Lakes", 153.41, -28.085, "C", "", 0),
    ("Miami", 153.442, -28.07, "S", "", 0), ("Burleigh Heads", 153.452, -28.09, "S", "e", 0), ("Palm Beach", 153.466, -28.115, "S", "", 0), ("Elanora", 153.45, -28.135, "S", "", 0),
    ("Currumbin", 153.481, -28.137, "S", "", 0), ("Tugun", 153.496, -28.148, "S", "", 0), ("Bilinga", 153.51, -28.158, "S", "", 0), ("Coolangatta", 153.538, -28.167, "S", "s", 0),
]
dots, labels = "", ""
for name, lon, lat, r, side, page in subs:
    x, y = P(lon, lat); col = REG[r]
    if page:
        dots += f'<g filter="url(#sh)"><path d="M{x} {y} c -11 -13 -11 -28 0 -28 c 11 0 11 15 0 28z" fill="{col}"/></g><circle cx="{x}" cy="{y - 18}" r="4.5" fill="#fff"/>'
    else:
        dots += f'<circle cx="{x}" cy="{y}" r="5.5" fill="{col}" stroke="#fff" stroke-width="2"/>'
    if side:
        size = 15 if page else 13
        ly = y - 18 if page else y
        if side == "e": labels += label(x + (14 if page else 10), ly + 5, name, size, bg="#fff", fg=NAVY)
        elif side == "w": labels += label(x - (14 if page else 10), ly + 5, name, size, anchor="end", bg="#fff", fg=NAVY)
        elif side == "s": labels += label(x, y + 28, name, size, anchor="middle", bg="#fff", fg=NAVY)
g += dots + labels
# legend + title card
LY = H - 62
g += f'<g filter="url(#sh)"><rect x="12" y="{LY}" width="222" height="50" rx="12" fill="#fff"/></g>'
for i, (nm, col) in enumerate((("North", TEAL), ("Central", NAVY), ("South", ORANGE))):
    g += f'<circle cx="{28 + i * 70}" cy="{LY + 18}" r="6" fill="{col}"/>' + T(38 + i * 70, LY + 23, nm, 12, 650, TEXT)
g += f'<path d="M28 {LY + 44} c -5 -6 -5 -13 0 -13 c 5 0 5 7 0 13z" fill="{NAVY}"/>' + T(38, LY + 42, "Suburb page on this site", 11, 500, MUTED)
g += T(W - 10, H - 8, "Not to scale", 10, 500, MUTED, anchor="end")
IMGS["coverage-map"] = (svg(W, H, g), W, H, 2, False)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    mpath = ROOT / "src/data/blog-images.json"
    manifest = json.loads(mpath.read_text()) if mpath.exists() else {}
    with sync_playwright() as p:
        br = p.chromium.launch()
        for name, (markup, w, h, scale, transparent) in IMGS.items():
            pg = br.new_page(viewport={"width": w, "height": h}, device_scale_factor=scale)
            pg.set_content(f"<html><head><style>{CSS} html,body{{background:transparent}}</style></head><body>{markup}</body></html>")
            pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(150)
            img = Image.open(io.BytesIO(pg.screenshot(omit_background=transparent))).convert("RGBA" if transparent else "RGB")
            pg.close()
            W2, H2 = img.size
            out = OUT / f"{name}.webp"
            img.save(out, "WEBP", quality=86, method=6)
            half = img.resize((W2 // 2, H2 // 2), Image.LANCZOS)
            half.save(OUT / f"{name}-600.webp" if W2 >= 1200 else OUT / f"{name}-sm.webp", "WEBP", quality=84, method=6)
            manifest[f"/img/home/{name}.webp"] = {"w": W2, "h": H2}
            print(f"{name:20} {W2}x{H2} {out.stat().st_size // 1024} KB")
        br.close()
    mpath.write_text(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
