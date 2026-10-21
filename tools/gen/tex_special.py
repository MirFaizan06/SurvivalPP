"""Textures for the Eclipse Altar, Stasis Chamber and Stasis Plate."""
import math, random
from PIL import Image
from common import *
from tex_blocks import shade_base, mer_from, write_block_texture, eclipse_motif, sparkle


def obsidian_base(seed, f=1.0):
    base = load('blocks/obsidian.png')
    return shade_base(base, f, hue_shift=(0.95, 0.85, 1.25))


def altar_top():
    img = obsidian_base(1, 0.9)
    glow = {}
    rng = random.Random(77)
    ramp = ECLIPSITE
    cx = cy = 7.5
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - cx, y - cy)
            ang = math.atan2(y - cy, x - cx)
            if d <= 3.6:
                over(img, x, y, ramp_at(ramp, 0.01 + 0.03 * d / 3.6) + (255,)); glow[(x, y)] = 0
            elif d <= 5.0:
                t = 0.5 + 0.5 * math.cos(ang - 3.9)
                over(img, x, y, ramp_at(ramp, 0.55 + 0.4 * t) + (255,)); glow[(x, y)] = int(130 + 125 * t)
            elif d <= 7.6:
                # corona rays at 8 compass points
                ray = abs(math.sin(ang * 4))
                if ray > 0.86 and d > 5.6:
                    t = 1 - (d - 5.6) / 2.2
                    over(img, x, y, ramp_at(ramp, 0.4 + 0.45 * t) + (255,)); glow[(x, y)] = int(60 + 120 * t)
    # frame and corner studs
    px = img.load()
    for i in range(16):
        for (x, y) in ((i, 0), (i, 15), (0, i), (15, i)):
            c = px[x, y]; f = 1.5 if (x == 0 or y == 0) else 0.5
            px[x, y] = tuple(min(255, int(v * f)) for v in c[:3]) + (255,)
    for (x, y) in [(2, 2), (13, 2), (2, 13), (13, 13)]:
        sparkle(img, glow, x, y, (159, 244, 255), 255)
    return img, mer_from(glow, metal=60, rough=70, gem_metal=100, gem_rough=45)


def altar_side():
    img = obsidian_base(2, 0.85)
    glow = {}
    ramp = ECLIPSITE
    px = img.load()
    # carved band with glyphs
    for x in range(16):
        for y in (4, 11):
            px[x, y] = ramp_at(ramp, 0.12) + (255,)
        for y in range(5, 11):
            c = px[x, y]
            px[x, y] = tuple(int(v * 0.55) for v in c[:3]) + (255,)
    glyphs = [(1, 6), (1, 7), (2, 8), (3, 6), (3, 9), (5, 7), (6, 6), (6, 8), (7, 9), (9, 6), (9, 7), (9, 8), (10, 8), (11, 6), (11, 9), (12, 7), (13, 6), (13, 8), (14, 9)]
    for (x, y) in glyphs:
        over(img, x, y, ramp_at(ramp, 0.72) + (255,)); glow[(x, y)] = 230
    for x in range(16):
        glow[(x, 4)] = 60; glow[(x, 11)] = 60
    return img, mer_from(glow, metal=60, rough=80, gem_metal=100, gem_rough=45)


def altar_bottom():
    img = obsidian_base(3, 0.8)
    return img, mer_from({}, metal=40, rough=120)


FRAME = [hx(x) for x in ['#0e0b14', '#1c1626', '#2d2540', '#453a63', '#6a5c96', '#9686c8']]


def stasis_frame():
    img = Image.new('RGBA', (16, 16))
    glow = {}
    for y in range(16):
        for x in range(16):
            n = fbm(55, x, y, 16, (2, 4, 8), (0.5, 0.3, 0.2))
            c = ramp_at(FRAME, 0.25 + n * 0.3)
            edge = min(x, y, 15 - x, 15 - y)
            if edge == 0:
                c = ramp_at(FRAME, 0.08)
            elif edge == 1:
                c = ramp_at(FRAME, 0.62 if (x <= 1 or y <= 1) and x + y < 16 else 0.18)
            elif edge == 2:
                c = tint(c, 0.8)
            img.putpixel((x, y), c + (255,))
    # rivets
    for (x, y) in [(3, 3), (12, 3), (3, 12), (12, 12)]:
        over(img, x, y, ramp_at(FRAME, 0.95) + (255,)); over(img, x + 1, y + 1, ramp_at(FRAME, 0.1) + (255,))
    # glowing rune line along the middle
    for x in range(5, 11):
        over(img, x, 8, ramp_at(ECLIPSITE, 0.78) + (255,)); glow[(x, 8)] = 220
    over(img, 7, 7, ramp_at(ECLIPSITE, 0.9) + (255,)); over(img, 8, 9, ramp_at(ECLIPSITE, 0.9) + (255,))
    glow[(7, 7)] = 255; glow[(8, 9)] = 255
    return img, mer_from(glow, metal=150, rough=70, gem_metal=60, gem_rough=60)


def stasis_glass():
    img = Image.new('RGBA', (16, 16), (150, 220, 235, 40))
    px = img.load()
    for y in range(16):
        for x in range(16):
            edge = min(x, y, 15 - x, 15 - y)
            a = 36
            col = (160, 225, 240)
            if edge == 0:
                a, col = 150, (190, 240, 255)
            elif edge == 1:
                a = 70
            px[x, y] = col + (a,)
    for k in range(3, 9):   # diagonal sheen
        px[k, 11 - k + 3] = (235, 252, 255, 170)
    for (x, y) in [(11, 4), (12, 3), (5, 11)]:
        px[x, y] = (255, 255, 255, 200)
    return img, None


def stasis_pearl():
    """Ender pearl skin used on a small faceted ball inside the chamber."""
    img = Image.new('RGBA', (16, 16))
    pal = [hx(x) for x in ['#062a24', '#0b4a3e', '#127a62', '#22b08a', '#5be8b8', '#c8fff0']]
    for y in range(16):
        for x in range(16):
            n = fbm(31, x, y, 16, (2, 4, 8), (0.5, 0.3, 0.2))
            sw = 0.5 + 0.5 * math.sin((x * 0.7 + y * 0.35) + n * 5)
            img.putpixel((x, y), ramp_at(pal, 0.15 + 0.6 * sw * (0.6 + 0.4 * n)) + (255,))
    glow = {(x, y): 90 for x in range(16) for y in range(16)}
    return img, mer_from(glow, metal=20, rough=40, gem_metal=20, gem_rough=40)


def plate_top():
    img = obsidian_base(4, 0.9)
    glow = {}
    ramp = ECLIPSITE
    cx = cy = 7.5
    px = img.load()
    for y in range(16):
        for x in range(16):
            dx, dy = (x - cx) / 6.2, (y - cy) / 3.4
            d = dx * dx + dy * dy
            if d <= 1.0:   # eye shape
                if d <= 0.18:
                    over(img, x, y, (5, 2, 12, 255)); glow[(x, y)] = 0
                elif d <= 0.45:
                    over(img, x, y, ramp_at(ramp, 0.72) + (255,)); glow[(x, y)] = 255
                else:
                    t = d
                    over(img, x, y, ramp_at(ramp, 0.28 + 0.35 * (1 - t)) + (255,)); glow[(x, y)] = int(90 + 80 * (1 - t))
    for i in range(16):
        for (x, y) in ((i, 0), (i, 15), (0, i), (15, i)):
            c = px[x, y]; f = 1.5 if (x == 0 or y == 0) else 0.5
            px[x, y] = tuple(min(255, int(v * f)) for v in c[:3]) + (255,)
    return img, mer_from(glow, metal=60, rough=70, gem_metal=90, gem_rough=45)


def plate_side():
    img = obsidian_base(5, 0.8)
    return img, mer_from({}, metal=40, rough=120)


def build():
    jobs = {'eclipse_altar_top': altar_top, 'eclipse_altar_side': altar_side, 'eclipse_altar_bottom': altar_bottom,
            'stasis_frame': stasis_frame, 'stasis_glass': stasis_glass, 'stasis_pearl': stasis_pearl,
            'stasis_plate_top': plate_top, 'stasis_plate_side': plate_side}
    for n, fn in jobs.items():
        img, mer = fn()
        write_block_texture(n, img, mer)
    return list(jobs)


if __name__ == '__main__':
    names = build()
    up_sheet([f'{RP}/textures/blocks/{n}.png' for n in names], PREVIEW + '/special_a.png', 10, 8)


# ----------------------------------------------------------------------------- Sanctum Warden
WATCH = [hx(x) for x in ['#06161f', '#0b3a52', '#127aa6', '#2ec4f0', '#8ff0ff', '#e8ffff']]


def sanctum_stone():
    img = obsidian_base(6, 0.85)
    glow = {}
    px = img.load()
    for (x, y) in [(2, 3), (3, 4), (3, 5), (11, 2), (12, 3), (12, 4), (5, 11), (6, 12), (7, 12), (13, 10), (13, 11), (14, 12), (9, 7)]:
        over(img, x, y, ramp_at(WATCH, 0.45) + (255,)); glow[(x, y)] = 150
    return img, mer_from(glow, metal=60, rough=70, gem_metal=90, gem_rough=45)


def sanctum_eye():
    img = obsidian_base(7, 0.7)
    glow = {}
    px = img.load()
    cx, cy = 7.5, 7.5
    for y in range(16):
        for x in range(16):
            dx, dy = (x - cx) / 7.0, (y - cy) / 3.6
            d = dx * dx + dy * dy
            if d <= 1.0:
                if d <= 0.10:
                    over(img, x, y, (3, 6, 10, 255)); glow[(x, y)] = 0                    # pupil
                elif d <= 0.30:
                    t = 1 - (d - 0.1) / 0.2
                    over(img, x, y, ramp_at(WATCH, 0.55 + 0.4 * t) + (255,)); glow[(x, y)] = 255   # iris
                else:
                    over(img, x, y, ramp_at(ECLIPSITE, 0.2 + 0.12 * (1 - d)) + (255,)); glow[(x, y)] = 70
            elif d <= 1.35:
                over(img, x, y, ramp_at(WATCH, 0.7) + (255,)); glow[(x, y)] = 200            # lid outline
    # brow lines + rivets
    for x in range(2, 14):
        over(img, x, 2, ramp_at(ECLIPSITE, 0.35) + (255,))
        over(img, x, 13, ramp_at(ECLIPSITE, 0.35) + (255,))
    for (x, y) in [(1, 1), (14, 1), (1, 14), (14, 14)]:
        sparkle(img, glow, x, y, (159, 244, 255), 255)
    return img, mer_from(glow, metal=60, rough=70, gem_metal=90, gem_rough=45)


def sanctum_top():
    img = obsidian_base(8, 0.9)
    glow = {}
    cx = cy = 7.5
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - cx, y - cy)
            ang = math.atan2(y - cy, x - cx)
            if 4.2 <= d <= 5.6:
                over(img, x, y, ramp_at(WATCH, 0.55 + 0.3 * math.cos(ang * 2)) + (255,)); glow[(x, y)] = 220
            elif d <= 2.2:
                over(img, x, y, ramp_at(WATCH, 0.9) + (255,)); glow[(x, y)] = 255
            elif d <= 7.4 and abs(math.sin(ang * 2)) > 0.93 and d > 5.8:
                over(img, x, y, ramp_at(WATCH, 0.4) + (255,)); glow[(x, y)] = 150
    px = img.load()
    for i in range(16):
        for (x, y) in ((i, 0), (i, 15), (0, i), (15, i)):
            c = px[x, y]; f = 1.5 if (x == 0 or y == 0) else 0.5
            px[x, y] = tuple(min(255, int(v * f)) for v in c[:3]) + (255,)
    return img, mer_from(glow, metal=60, rough=70, gem_metal=90, gem_rough=45)


def build_sanctum():
    for n, fn in (('sanctum_stone', sanctum_stone), ('sanctum_eye', sanctum_eye), ('sanctum_top', sanctum_top)):
        img, mer = fn()
        write_block_texture(n, img, mer)
    # Sanctum Pass item sprite (a glowing key-card)
    from tex_items import ascii_sprite
    pal = {'k': hx('#06050d'), 'd': hx('#150a2b'), 'p': hx('#34136a'), 'g': hx('#ffd35e'), 'G': hx('#fff0b0'), 'c': hx('#2ec4f0'), 'C': hx('#e8ffff'), 'b': hx('#0b3a52')}
    rows = [
        '...kkkkkkkk...',
        '..kgGGGGGGgk..',
        '.kgddddddddgk.',
        '.kgdppppppdgk.',
        '.kgdpbbbbpdgk.',
        '.kgdbcCCcbdgk.',
        '.kgdbcCkcbdgk.',
        '.kgdbcCCcbdgk.',
        '.kgdpbbbbpdgk.',
        '.kgdppppppdgk.',
        '.kgddddddddgk.',
        '.kgGGGGGGGGgk.',
        '..kgggggggggk.'[:14],
        '...kkkkkkkk...',
    ]
    rows = [r.ljust(14, '.')[:14] for r in rows]
    img = ascii_sprite(rows, pal)
    from tex_items import save_item
    save_item('sanctum_pass', img)
    return ['sanctum_stone', 'sanctum_eye', 'sanctum_top']
