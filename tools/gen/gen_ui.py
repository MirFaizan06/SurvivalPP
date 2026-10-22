"""Custom boss health bars.  The vanilla boss bar is left untouched underneath; for our bosses (matched by name) a themed track, fill and
ornate frame are drawn on top of it with JSON-UI `modifications`.  If anything here failed to render, the vanilla bar would still show."""
import math, random
from PIL import Image, ImageDraw
from common import *

# skin: (key substring of the boss name, palette dict)
SKINS = {
    'eclipse_sovereign': ('Eclipse Sovereign', dict(track='#0a0420', fill=('#2a1070', '#8a3ae0', '#f07aff'), edge='#b8a0ff', accent='#ff9cf0', motif='corona')),
    'hollow_king': ('Hollow King', dict(track='#06140c', fill=('#0f4a2a', '#22c060', '#b8ffd0'), edge='#d4a62c', accent='#f4d460', motif='crown')),
    'mosswood_colossus': ('Mosswood Colossus', dict(track='#1a0f06', fill=('#1a5a22', '#4cc450', '#c8ff90'), edge='#6a4726', accent='#9af07a', motif='leaves')),
    'silkqueen': ('Silkqueen', dict(track='#0a0716', fill=('#3a2a80', '#a898f0', '#f4f0ff'), edge='#8a6aff', accent='#f2c744', motif='web')),
    'veiled_blossom': ('Veiled Blossom', dict(track='#2a0e1e', fill=('#8a2a58', '#f070a8', '#ffe0ee'), edge='#ffc0d8', accent='#ffffff', motif='blossom')),
    'frost_cantor': ('Frost Cantor', dict(track='#06121e', fill=('#1c4f8a', '#62b8f0', '#f0fbff'), edge='#bfe4ff', accent='#ffffff', motif='snowflake')),
    'mire_lantern': ('Mire Lantern', dict(track='#08140c', fill=('#2a6a3a', '#9ae070', '#fff6a0'), edge='#c8b060', accent='#ffe27a', motif='lantern')),
    'cinder_bride': ('Cinder Bride', dict(track='#120606', fill=('#7a1d00', '#ff8a24', '#fff2b0'), edge='#ffb060', accent='#ffe27a', motif='forge')),
    'ashen_groom': ('Ashen Groom', dict(track='#060c14', fill=('#0a3a6a', '#3aa8f0', '#e0f8ff'), edge='#8ac8f0', accent='#ffffff', motif='vow')),
}
S = 2                                    # texture scale: drawn at 2x for smooth downsampling in the UI
BAR_W, BAR_H = 182, 7                    # UI size of the fill
BACK = (190, 11)
FRAME = (236, 26)


def hexc(h, a=255):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def lerpc(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(4))


def gradient_bar(w, h, stops, seed, motif):
    img = Image.new('RGBA', (w, h))
    px = img.load()
    rng = random.Random(seed)
    cs = [hexc(c) for c in stops]
    for y in range(h):
        v = abs((y + 0.5) / h - 0.5) * 2                        # 0 centre .. 1 edge
        for x in range(w):
            u = x / (w - 1)
            base = lerpc(cs[0], cs[1], u * 2) if u < 0.5 else lerpc(cs[1], cs[2], (u - 0.5) * 2)
            shade = 1.18 - 0.5 * v
            c = tuple(min(255, int(base[i] * shade)) for i in range(3)) + (255,)
            px[x, y] = c
    d = ImageDraw.Draw(img)
    for _ in range(w // 9):                                      # fine glints
        x = rng.randint(0, w - 1)
        d.line([(x, h // 5), (x + rng.randint(2, 6) * S, h // 5)], fill=(255, 255, 255, 70))
    if motif == 'web':
        for x in range(0, w, 22 * S):
            d.line([(x, 0), (x + 10 * S, h)], fill=(255, 255, 255, 60))
    if motif == 'blossom':
        for _ in range(w // 18):
            x, y = rng.randint(0, w - 1), rng.randint(1, h - 2)
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(255, 235, 245, 120))
    if motif == 'corona':
        for _ in range(w // 10):
            x, y = rng.randint(0, w - 1), rng.randint(1, h - 2)
            d.point((x, y), fill=(255, 255, 255, 200))
    # top highlight line
    d.line([(0, 1), (w, 1)], fill=(255, 255, 255, 60))
    return img


def track(w, h, col, edge):
    img = Image.new('RGBA', (w, h), hexc(col))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], outline=hexc(edge, 160))
    d.line([(2, 2), (w - 3, 2)], fill=(0, 0, 0, 90))
    d.line([(2, h - 3), (w - 3, h - 3)], fill=(255, 255, 255, 25))
    return img


def petal(d, cx, cy, r, ang, fill, outline=None):
    pts = []
    for k in range(14):
        t = k / 13 * math.tau
        rr = r * (0.55 + 0.45 * abs(math.sin(t / 2)))
        pts.append((cx + math.cos(t + ang) * rr * 0.62, cy + math.sin(t + ang) * rr))
    d.polygon(pts, fill=fill, outline=outline)


def blossom(d, cx, cy, r, fill, centre):
    for k in range(5):
        a = k / 5 * math.tau - math.pi / 2
        petal(d, cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55, r * 0.8, a + math.pi / 2, fill, hexc('#a8466f'))
    d.ellipse([cx - r * 0.22, cy - r * 0.22, cx + r * 0.22, cy + r * 0.22], fill=centre)


def frame(w, h, p, seed):
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    edge, accent, motif = hexc(p['edge']), hexc(p['accent']), p['motif']
    bx0, bx1 = (w - BACK[0] * S) // 2 - 3, (w + BACK[0] * S) // 2 + 3
    by0, by1 = (h - BACK[1] * S) // 2 - 3, (h + BACK[1] * S) // 2 + 3
    d.rectangle([bx0, by0, bx1, by1], outline=edge, width=3)                           # outer border (inner stays transparent)
    d.rectangle([bx0 + 3, by0 + 3, bx1 - 3, by1 - 3], outline=lerpc(edge, (0, 0, 0, 255), 0.5), width=1)
    cy = h // 2
    if motif == 'corona':
        for side in (-1, 1):
            cx = w // 2 + side * (bx1 - w // 2 + 8)
            d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(8, 4, 16, 255), outline=edge, width=2)
            for k in range(16):
                a = k / 16 * math.tau
                r1, r2 = 14, 20 if k % 2 == 0 else 17
                d.line([(cx + math.cos(a) * r1, cy + math.sin(a) * r1), (cx + math.cos(a) * r2, cy + math.sin(a) * r2)], fill=accent, width=2)
    elif motif == 'crown':
        cx = w // 2
        d.polygon([(cx - 22, by0 + 1), (cx - 22, by0 - 12), (cx - 11, by0 - 5), (cx, by0 - 16), (cx + 11, by0 - 5), (cx + 22, by0 - 12), (cx + 22, by0 + 1)], fill=accent, outline=hexc('#4a3408'))
        for gx in (-14, 0, 14):
            d.ellipse([cx + gx - 3, by0 - 8, cx + gx + 3, by0 - 2], fill=hexc('#4cf0a0'))
        for side in (-1, 1):
            sx = w // 2 + side * (bx1 - w // 2 + 8)
            d.rounded_rectangle([sx - 11, cy - 12, sx + 11, cy + 10], radius=6, fill=hexc('#e6dfc6'), outline=hexc('#1c1a14'), width=2)
            for ex in (-4, 4):
                d.ellipse([sx + ex - 3, cy - 6, sx + ex + 3, cy], fill=hexc('#06140c'))
            d.rectangle([sx - 5, cy + 4, sx + 5, cy + 9], fill=hexc('#06140c'))
    elif motif == 'leaves':
        for side in (-1, 1):
            sx = w // 2 + side * (bx1 - w // 2 + 4)
            for k, (dx, dy, ang) in enumerate(((0, -9, -0.9), (6, 0, 0.1), (0, 9, 1.0), (-6, 2, 2.4))):
                petal(d, sx + dx * side, cy + dy, 16, ang * side, hexc('#4cc450'), hexc('#0a3a14'))
            d.ellipse([sx - 6, cy - 6, sx + 6, cy + 6], fill=hexc('#664726'), outline=hexc('#1a0f06'), width=2)
            d.ellipse([sx - 3, cy - 3, sx + 3, cy + 3], fill=hexc('#6af07a'))
        for x in range(bx0 + 20, bx1 - 20, 34):
            petal(d, x, by0 - 1, 10, 0.3, hexc('#2f8f36'), hexc('#0a3a14'))
            petal(d, x + 12, by1 + 1, 9, -0.4, hexc('#2f8f36'), hexc('#0a3a14'))
    elif motif == 'web':
        for side in (-1, 1):
            sx = w // 2 + side * (bx1 - w // 2 + 4)
            for k in range(8):
                a = k / 8 * math.tau
                d.line([(sx, cy), (sx + math.cos(a) * 20, cy + math.sin(a) * 20)], fill=hexc('#eeebfb'), width=1)
            for rr in (7, 13, 19):
                d.regular_polygon((sx, cy, rr), 8, fill=None, outline=hexc('#cfc8f0'))
            d.ellipse([sx - 5, cy - 5, sx + 5, cy + 5], fill=hexc('#0a0716'), outline=accent, width=2)
        for k, x in enumerate(range(bx0 + 30, bx1 - 30, 46)):
            d.arc([x, by0 - 14, x + 30, by0 + 10], 180, 360, fill=accent, width=2)
    elif motif == 'snowflake':
        for side in (-1, 1):
            sx = w // 2 + side * (bx1 - w // 2 + 6)
            for k in range(6):
                a = k / 6 * math.tau
                ex, ey = sx + math.cos(a) * 20, cy + math.sin(a) * 20
                d.line([(sx, cy), (ex, ey)], fill=hexc('#eaf8ff'), width=2)
                for t in (0.55, 0.8):
                    bx, by = sx + math.cos(a) * 20 * t, cy + math.sin(a) * 20 * t
                    for sg in (-1, 1):
                        d.line([(bx, by), (bx + math.cos(a + sg * 0.9) * 7, by + math.sin(a + sg * 0.9) * 7)], fill=hexc('#bfe4ff'), width=1)
            d.ellipse([sx - 4, cy - 4, sx + 4, cy + 4], fill=hexc('#06121e'), outline=accent, width=2)
        for x in range(bx0 + 24, bx1 - 24, 26):                                         # icicles hanging from the frame
            ln = 8 + (x * 7) % 9
            d.polygon([(x - 4, by1 + 1), (x + 4, by1 + 1), (x, by1 + ln)], fill=hexc('#dff3ff'), outline=hexc('#7ab8e0'))
    elif motif == 'forge':
        for side in (-1, 1):
            sx = w // 2 + side * (bx1 - w // 2 + 6)
            d.polygon([(sx - 16, cy - 8), (sx + 16, cy - 8), (sx + 12, cy - 2), (sx + 5, cy - 2), (sx + 5, cy + 6), (sx + 11, cy + 10), (sx - 11, cy + 10), (sx - 5, cy + 6), (sx - 5, cy - 2), (sx - 12, cy - 2)], fill=hexc('#1c1c26'), outline=edge)
            d.line([(sx - 12, cy - 6), (sx + 12, cy - 6)], fill=accent, width=2)
            for k in range(4):
                d.ellipse([sx - 14 + k * 9, cy - 20 - (k % 2) * 4, sx - 10 + k * 9, cy - 16 - (k % 2) * 4], fill=hexc('#ff8a24'))
        cx = w // 2
        for k in range(7):
            x = bx0 + 30 + k * 52
            d.polygon([(x - 3, by1 + 1), (x + 3, by1 + 1), (x, by1 + 9 + (k % 3) * 3)], fill=hexc('#ff6a1c'), outline=hexc('#7a1d00'))
    elif motif == 'vow':
        for side in (-1, 1):
            sx = w // 2 + side * (bx1 - w // 2 + 6)
            d.ellipse([sx - 17, cy - 11, sx + 3, cy + 9], outline=hexc('#cfe8f8'), width=3)
            d.ellipse([sx - 3, cy - 11, sx + 17, cy + 9], outline=edge, width=3)
            d.ellipse([sx - 6, cy - 16, sx + 6, cy - 6], fill=hexc('#5ac8ff'))
        cx = w // 2
        for k in range(5):
            x = cx - 60 + k * 30
            d.polygon([(x, by0 - 12 - (k % 2) * 5), (x + 4, by0 - 4), (x - 4, by0 - 4)], fill=hexc('#5ac8ff'))
    elif motif == 'lantern':
        for side in (-1, 1):
            sx = w // 2 + side * (bx1 - w // 2 + 6)
            d.rectangle([sx - 9, cy - 13, sx + 9, cy - 9], fill=hexc('#3a2e14'), outline=edge)
            d.rectangle([sx - 9, cy + 9, sx + 9, cy + 13], fill=hexc('#3a2e14'), outline=edge)
            d.rounded_rectangle([sx - 8, cy - 9, sx + 8, cy + 9], radius=3, fill=hexc('#ffe27a'), outline=edge, width=2)
            d.ellipse([sx - 4, cy - 5, sx + 4, cy + 5], fill=hexc('#fffbd0'))
            d.arc([sx - 6, cy - 20, sx + 6, cy - 10], 180, 360, fill=edge, width=2)
        cx = w // 2
        for k in range(5):                                                                # wisps rising above the bar
            x = cx - 60 + k * 30
            d.ellipse([x - 3, by0 - 10 - (k % 2) * 4, x + 3, by0 - 4 - (k % 2) * 4], fill=hexc('#fff6a0') if k % 2 else hexc('#b8f08a'))
    else:  # blossom
        for side in (-1, 1):
            sx = w // 2 + side * (bx1 - w // 2 + 6)
            blossom(d, sx, cy, 18, hexc('#ffc0d8'), hexc('#f7d466'))
            blossom(d, sx - side * 22, cy - 9, 9, hexc('#ffe0ee'), hexc('#f7d466'))
            blossom(d, sx - side * 20, cy + 10, 8, hexc('#f6a8c8'), hexc('#f7d466'))
        cx = w // 2
        for k, ang in enumerate((-64, -32, 0, 32, 64)):                                 # a folded fan above the bar
            a = math.radians(ang - 90)
            d.polygon([(cx, by0 + 2), (cx + math.cos(a - 0.3) * 24, by0 + 2 + math.sin(a - 0.3) * 24), (cx + math.cos(a + 0.3) * 24, by0 + 2 + math.sin(a + 0.3) * 24)],
                      fill=hexc('#ffc0d8') if k % 2 == 0 else hexc('#ffe6f0'), outline=hexc('#a8466f'))
        for k in range(6):
            x = bx0 + 40 + k * 60
            d.line([(x, by1 + 1), (x, by1 + 10)], fill=accent, width=2)
            d.ellipse([x - 3, by1 + 9, x + 3, by1 + 15], fill=hexc('#f6a8c8'))
    return img


# --------------------------------------------------------------------------------------------- glyph bar
# The script-driven bar: a custom font page (font/glyph_E4.png).  Every skin owns 8 consecutive characters starting at
# U+E400 + 8 * skin_index:  +0 left emblem, +1 right emblem, +2..+6 bar cell (empty, 1/4, 1/2, 3/4, full).
# bossbar.js draws it on the action bar, which needs no JSON-UI bindings and therefore cannot fall back to the vanilla bar.
GLYPH_PAGE = 'E4'
GLYPH_BASE = 0xE400
CELL = 16


def emblem(motif, p):
    """16x16 emblem for the end caps, drawn at 4x and reduced."""
    big = 64
    img = Image.new('RGBA', (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    edge, accent = hexc(p['edge']), hexc(p['accent'])
    dark = hexc(p['track'])
    c = big // 2
    if motif == 'corona':
        d.ellipse([c - 14, c - 14, c + 14, c + 14], fill=dark, outline=edge, width=3)
        for k in range(16):
            a = k / 16 * math.tau
            r2 = 29 if k % 2 == 0 else 23
            d.line([(c + math.cos(a) * 17, c + math.sin(a) * 17), (c + math.cos(a) * r2, c + math.sin(a) * r2)], fill=accent, width=3)
    elif motif == 'crown':
        d.polygon([(8, 44), (8, 16), (22, 30), (32, 10), (42, 30), (56, 16), (56, 44)], fill=accent, outline=hexc('#4a3408'))
        d.rectangle([8, 44, 56, 52], fill=hexc('#d4a62c'), outline=hexc('#4a3408'))
        for gx in (18, 32, 46):
            d.ellipse([gx - 4, 38, gx + 4, 46], fill=hexc('#4cf0a0'))
    elif motif == 'leaves':
        for ang in (-0.9, 0.2, 1.4, 2.6):
            petal(d, c + math.cos(ang) * 10, c + math.sin(ang) * 10, 30, ang + 1.5, hexc('#4cc450'), hexc('#0a3a14'))
        d.ellipse([c - 6, c - 6, c + 6, c + 6], fill=hexc('#664726'), outline=hexc('#1a0f06'), width=2)
    elif motif == 'web':
        for k in range(8):
            a = k / 8 * math.tau
            d.line([(c, c), (c + math.cos(a) * 29, c + math.sin(a) * 29)], fill=hexc('#eeebfb'), width=2)
        for rr in (10, 19, 28):
            d.regular_polygon((c, c, rr), 8, outline=hexc('#cfc8f0'))
        d.ellipse([c - 6, c - 6, c + 6, c + 6], fill=dark, outline=accent, width=2)
    elif motif == 'snowflake':
        for k in range(6):
            a = k / 6 * math.tau
            d.line([(c, c), (c + math.cos(a) * 29, c + math.sin(a) * 29)], fill=hexc('#eaf8ff'), width=4)
            for t in (0.5, 0.78):
                bx, by = c + math.cos(a) * 29 * t, c + math.sin(a) * 29 * t
                for sg in (-1, 1):
                    d.line([(bx, by), (bx + math.cos(a + sg * 0.9) * 11, by + math.sin(a + sg * 0.9) * 11)], fill=edge, width=3)
        d.ellipse([c - 5, c - 5, c + 5, c + 5], fill=dark, outline=accent, width=2)
    elif motif == 'forge':
        d.polygon([(6, 18), (58, 18), (50, 30), (40, 30), (40, 40), (52, 50), (12, 50), (24, 40), (24, 30), (14, 30)], fill=hexc('#2a2a36'), outline=edge)
        d.line([(12, 22), (52, 22)], fill=accent, width=3)
        for k in range(3):
            d.ellipse([12 + k * 16, 6 - (k % 2) * 3, 20 + k * 16, 14 - (k % 2) * 3], fill=hexc('#ff8a24'))
    elif motif == 'vow':
        d.ellipse([6, 18, 38, 50], outline=hexc('#cfe8f8'), width=5)
        d.ellipse([26, 18, 58, 50], outline=edge, width=5)
        d.ellipse([26, 6, 38, 18], fill=hexc('#5ac8ff'))
    elif motif == 'lantern':
        d.rectangle([c - 14, 8, c + 14, 16], fill=hexc('#3a2e14'), outline=edge, width=2)
        d.rectangle([c - 14, 50, c + 14, 58], fill=hexc('#3a2e14'), outline=edge, width=2)
        d.rounded_rectangle([c - 12, 16, c + 12, 50], radius=6, fill=accent, outline=edge, width=3)
        d.ellipse([c - 6, 26, c + 6, 42], fill=hexc('#fffbd0'))
    else:  # blossom
        blossom(d, c, c, 28, hexc('#ffc0d8'), hexc('#f7d466'))
    return img.resize((CELL, CELL), Image.LANCZOS)


def glyph_cell(p, quarters):
    """One bar cell: 16 px wide, bar body in rows 3..12 with a 1 px frame; `quarters` 0..4 of its width are filled."""
    img = Image.new('RGBA', (CELL, CELL), (0, 0, 0, 0))
    px = img.load()
    edge = hexc(p['edge'])
    track = hexc(p['track'])
    lo, mid, hi = (hexc(c) for c in p['fill'])
    for y in range(3, 13):
        for x in range(CELL):
            if y in (3, 12):
                px[x, y] = lerpc(edge, (0, 0, 0, 255), 0.35)
            elif x < quarters * 4:
                t = (y - 4) / 7                                          # bright top, dark bottom, with a gloss line
                px[x, y] = lerpc(hi, lo, min(1.0, t * 1.15)) if y > 4 else lerpc(hi, (255, 255, 255, 255), 0.35)
                if (x + y) % 8 == 0:
                    px[x, y] = lerpc(px[x, y], (255, 255, 255, 255), 0.25)
            else:
                px[x, y] = lerpc(track, (0, 0, 0, 255), 0.0) if y < 11 else lerpc(track, (255, 255, 255, 255), 0.08)
    return img


def build_glyphs():
    sheet = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    for i, (skin, (key, p)) in enumerate(SKINS.items()):
        base = i * 8
        em = emblem(p['motif'], p)
        tiles = [em, em.transpose(Image.FLIP_LEFT_RIGHT)] + [glyph_cell(p, q) for q in range(5)]
        for j, t in enumerate(tiles):
            n = base + j
            sheet.paste(t, ((n % 16) * CELL, (n // 16) * CELL))
    assert len(SKINS) * 8 <= 256
    save_png(sheet, f'{RP}/font/glyph_{GLYPH_PAGE}.png')
    return sheet


def ui_json():
    controls = []
    for skin, (key, p) in SKINS.items():
        controls.append({f'ecr_{skin}@hud.ecr_boss_skin': {
            '$ecr_boss_name': f"'{key}'", '$tex_back': f'textures/ui/ecr_boss_{skin}_back', '$tex_fill': f'textures/ui/ecr_boss_{skin}_fill', '$tex_frame': f'textures/ui/ecr_boss_{skin}_frame'}})
    return {
        'namespace': 'hud',
        'ecr_boss_skin': {
            'type': 'panel', 'size': [FRAME[0], FRAME[1]], 'anchor_from': 'top_middle', 'anchor_to': 'top_middle', 'offset': [0, 4],
            'bindings': [
                {'binding_name': '#bossName', 'binding_type': 'collection', 'binding_collection_name': 'boss_bars'},
                {'binding_type': 'view', 'source_property_name': '(not ((#bossName - $ecr_boss_name) = #bossName))', 'target_property_name': '#visible'}],
            'controls': [
                {'ecr_back': {'type': 'image', 'texture': '$tex_back', 'layer': 5, 'size': list(BACK), 'anchor_from': 'center', 'anchor_to': 'center'}},
                {'ecr_fill': {
                    'type': 'image', 'texture': '$tex_fill', 'layer': 6, 'size': [BAR_W, BAR_H], 'anchor_from': 'center', 'anchor_to': 'center',
                    'clip_direction': 'left', 'clip_pixelperfect': False,
                    'bindings': [{'binding_name': '#progress_percentage', 'binding_name_override': '#clip_ratio', 'binding_type': 'collection', 'binding_collection_name': 'boss_bars'}]}},
                {'ecr_frame': {'type': 'image', 'texture': '$tex_frame', 'layer': 7, 'size': list(FRAME), 'anchor_from': 'center', 'anchor_to': 'center'}}]},
        'boss_health_panel': {'modifications': [{'array_name': 'controls', 'operation': 'insert_back', 'value': controls}]},
    }


def build():
    for i, (skin, (key, p)) in enumerate(SKINS.items()):
        save_png(track(BACK[0] * S, BACK[1] * S, p['track'], p['edge']), f'{RP}/textures/ui/ecr_boss_{skin}_back.png')
        save_png(gradient_bar(BAR_W * S, BAR_H * S, p['fill'], 900 + i, p['motif']), f'{RP}/textures/ui/ecr_boss_{skin}_fill.png')
        save_png(frame(FRAME[0] * S, FRAME[1] * S, p, i), f'{RP}/textures/ui/ecr_boss_{skin}_frame.png')
    wjson(f'{RP}/ui/hud_screen.json', ui_json())
    build_glyphs()


if __name__ == '__main__':
    build()
    # preview: composite each skin at 2x like the game would
    sheet = Image.new('RGBA', (FRAME[0] * S, FRAME[1] * S * len(SKINS)), (40, 44, 60, 255))
    for i, skin in enumerate(SKINS):
        y = i * FRAME[1] * S
        back = Image.open(f'{RP}/textures/ui/ecr_boss_{skin}_back.png'); fill = Image.open(f'{RP}/textures/ui/ecr_boss_{skin}_fill.png'); fr = Image.open(f'{RP}/textures/ui/ecr_boss_{skin}_frame.png')
        sheet.alpha_composite(back, ((FRAME[0] * S - back.width) // 2, y + (FRAME[1] * S - back.height) // 2))
        f2 = fill.crop((0, 0, int(fill.width * 0.72), fill.height))
        sheet.alpha_composite(f2, ((FRAME[0] * S - fill.width) // 2, y + (FRAME[1] * S - fill.height) // 2))
        sheet.alpha_composite(fr, (0, y))
    sheet.save(f'{PREVIEW}/bossbars.png')
    print('ok')
