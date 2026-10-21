"""Procedural block textures for the three ores and their storage blocks.
Everything is painted from scratch on top of the vanilla stone textures so that it
sits naturally next to vanilla blocks (16x16, vanilla light direction = top-left)."""
import math, random
from PIL import Image
import numpy as np
from common import *


# ------------------------------------------------------------------ helpers
def shade_base(img, f, hue_shift=None, desat=0.0):
    out = img.copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if desat:
                l = int(0.3 * r + 0.59 * g + 0.11 * b)
                r, g, b = [int(c + (l - c) * desat) for c in (r, g, b)]
            if hue_shift:
                r, g, b = [max(0, min(255, int(c * s))) for c, s in zip((r, g, b), hue_shift)]
            px[x, y] = (max(0, min(255, int(r * f))), max(0, min(255, int(g * f))), max(0, min(255, int(b * f))), a)
    return out


def blob_pixels(cx, cy, rx, ry, rng, rough=0.35):
    pts = set()
    for y in range(int(cy - ry - 2), int(cy + ry + 3)):
        for x in range(int(cx - rx - 2), int(cx + rx + 3)):
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            d += rng.uniform(-rough, rough)
            if d < 1.0:
                pts.add((x, y))
    return pts


def paint_facets(img, glow, pts, ramp, rng, light=(-1, -1), nseeds=3, glow_v=200, lo=1, hi=5, rimdark=True):
    """Paint a set of pixels as a faceted gem. Writes ramp colours, records emissive in glow dict."""
    if not pts:
        return
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    seeds = []
    for _ in range(nseeds):
        seeds.append((rng.uniform(minx, maxx), rng.uniform(miny, maxy), rng.uniform(0.2, 1.0)))
    for (x, y) in pts:
        best = min(seeds, key=lambda s: (s[0] - x) ** 2 + (s[1] - y) ** 2)
        t = best[2]
        # directional light across blob
        dl = ((x - (minx + maxx) / 2) * light[0] + (y - (miny + maxy) / 2) * light[1])
        span = max(1.0, (maxx - minx + maxy - miny) / 2)
        t = t * 0.55 + (-dl / span + 0.5) * 0.45
        idx = lo + t * (hi - lo)
        edge = any((x + dx, y + dy) not in pts for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if edge and rimdark:
            lit = ((x + light[0] * -1, y + light[1] * -1) not in pts)  # edge facing away from light
            idx = max(0.2, idx - (1.6 if (x + 1, y) not in pts or (x, y + 1) not in pts else 0.7))
        col = ramp_at(ramp, idx / (len(ramp) - 1))
        over(img, x, y, col + (255,))
        glow[(x, y)] = glow_v if idx > 2.5 else glow_v // 2


def sparkle(img, glow, x, y, col=(255, 255, 255), glow_v=255):
    over(img, x, y, col + (255,))
    glow[(x, y)] = glow_v


def mer_from(glow, size=16, metal=0, rough=215, gem_metal=70, gem_rough=45, mask=None):
    mer = Image.new('RGB', (size, size), (metal, 0, rough))
    px = mer.load()
    for (x, y), g in glow.items():
        if 0 <= x < size and 0 <= y < size:
            px[x, y] = (gem_metal, g, gem_rough)
    return mer


def texture_set(name, folder='blocks', mer=True):
    return {"format_version": "1.21.30",
            "minecraft:texture_set": {"color": name, **({"metalness_emissive_roughness": name + "_mer"} if mer else {})}}


def write_block_texture(name, img, mer_img=None, folder='textures/blocks'):
    save_png(img, f'{RP}/{folder}/{name}.png')
    if mer_img is not None:
        save_png(mer_img, f'{RP}/{folder}/{name}_mer.png')
        wjson(f'{RP}/{folder}/{name}.texture_set.json', texture_set(name))


# ------------------------------------------------------------------ AZURITE ORE (deepslate)
def azurite_ore():
    base = load('blocks/deepslate/deepslate.png')
    img = shade_base(base, 0.92, hue_shift=(0.9, 0.97, 1.12))
    glow = {}
    rng = random.Random(1101)
    ramp = AZURITE
    # tall crystal shards, vanilla-ore-like distribution (5 clusters)
    shards = [(3, 3, 5, 2), (10, 2, 4, 2), (6, 9, 5, 3), (12, 10, 4, 2), (2, 12, 3, 2)]
    for (sx, sy, h, w) in shards:
        pts = set()
        for k in range(h):
            half = w if k >= 1 else max(1, w - 1)
            if k == h - 1:
                half = max(1, w - 1)
            for dx in range(-half // 2 if half > 1 else 0, (half + 1) // 2 + (1 if half > 1 else 1)):
                pts.add((sx + dx, sy + k))
        # tip
        pts.add((sx, sy - 1))
        paint_facets(img, glow, pts, ramp, rng, light=(-1, -1), nseeds=2, glow_v=150, lo=1.2, hi=5.2)
    # highlights
    for (x, y) in [(3, 2), (10, 1), (6, 8), (12, 9), (2, 11)]:
        sparkle(img, glow, x, y, (235, 250, 255), 255)
    for (x, y) in [(8, 6), (14, 5), (1, 8), (9, 13)]:
        over(img, x, y, ramp[2] + (255,)); glow[(x, y)] = 90
    return img, mer_from(glow, rough=210)


# ------------------------------------------------------------------ PYRELITE ORE (netherrack, molten cracks)
def pyrelite_ore():
    base = load('blocks/netherrack.png')
    img = shade_base(base, 0.62, hue_shift=(0.95, 0.7, 0.62), desat=0.25)
    glow = {}
    rng = random.Random(2202)
    ramp = PYRELITE
    px = img.load()
    # obsidian-ish scorched chunks
    for (cx, cy, rx, ry) in [(4, 4, 3, 3), (11, 8, 3.4, 3), (5, 12, 2.6, 2.2), (13, 2, 2.2, 2.2)]:
        pts = blob_pixels(cx, cy, rx, ry, rng, 0.3)
        for (x, y) in pts:
            if 0 <= x < 16 and 0 <= y < 16:
                n = fbm(int(cx * 3 + cy), x, y)
                dark = ramp_at(ramp, 0.06 + n * 0.18)
                over(img, x, y, dark + (255,))
    # lava cracks (noise ridges)
    for y in range(16):
        for x in range(16):
            n = fbm(77, x * 1.0, y * 1.0, 16, (2, 4, 8), (0.55, 0.3, 0.15))
            ridge = abs(n - 0.48)
            if ridge < 0.03:
                t = 1.0 - ridge / 0.03
                col = ramp_at(ramp, 0.45 + t * 0.5)
                over(img, x, y, col + (255,))
                glow[(x, y)] = int(120 + 135 * t)
            elif ridge < 0.052:
                # hot rim
                r, g, b, a = px[x, y]
                over(img, x, y, mix((r, g, b), ramp[3], 0.45) + (255,))
                glow[(x, y)] = 45
    # molten gem core nodules
    for (cx, cy) in [(4, 4), (11, 8), (5, 12)]:
        pts = {(cx, cy), (cx + 1, cy), (cx, cy + 1), (cx - 1, cy)}
        paint_facets(img, glow, pts, ramp, rng, nseeds=2, glow_v=255, lo=3.2, hi=5.6, rimdark=False)
        sparkle(img, glow, cx, cy, (255, 246, 200), 255)
    return img, mer_from(glow, rough=235, gem_metal=20, gem_rough=90)


# ------------------------------------------------------------------ ECLIPSITE ORE (end stone with eclipse motifs)
def eclipse_motif(img, glow, cx, cy, rng, ramp, r=1.6, ring=1.1):
    """An 'eclipse': black disc with a bright corona ring that is brightest to the upper-left."""
    R = int(r + ring + 2)
    for y in range(-R, R + 1):
        for x in range(-R, R + 1):
            d = math.hypot(x, y)
            px_, py_ = cx + x, cy + y
            if d <= r:
                col = ramp_at(ramp, 0.01 + 0.04 * (1 - d / (r + 1)))
                over(img, px_, py_, col + (255,)); glow[(px_, py_)] = 0
            elif d <= r + ring:
                ang = math.atan2(y, x)
                t = 0.5 + 0.5 * math.cos(ang - 3.9)
                col = ramp_at(ramp, 0.58 + 0.34 * t)
                over(img, px_, py_, col + (255,)); glow[(px_, py_)] = int(120 + 135 * t)


def eclipsite_ore():
    base = load('blocks/end_stone.png')
    img = shade_base(base, 0.5, hue_shift=(0.82, 0.62, 1.0), desat=0.1)
    glow = {}
    rng = random.Random(3303)
    ramp = ECLIPSITE
    # dark crystalline ribs
    for (cx, cy, rx, ry) in [(11, 4, 2.8, 3.4), (4, 12, 2.6, 2.6), (14, 9, 1.6, 2.2)]:
        pts = blob_pixels(cx, cy, rx, ry, rng, 0.28)
        paint_facets(img, glow, pts, ramp, rng, nseeds=3, glow_v=170, lo=0.4, hi=3.6)
    eclipse_motif(img, glow, 4, 4, rng, ramp, 1.6, 1.0)
    eclipse_motif(img, glow, 11, 11, rng, ramp, 1.5, 1.0)
    # cyan star sparkles (iridescent)
    for (x, y) in [(1, 9), (9, 1), (14, 8), (2, 14), (12, 11), (8, 7)]:
        sparkle(img, glow, x, y, (170, 246, 255), 255)
    return img, mer_from(glow, rough=200, gem_metal=90, gem_rough=40)


# ------------------------------------------------------------------ STORAGE BLOCKS
def bevel(img, ramp, hi=4.6, lo=1.0, edge=1):
    px = img.load()
    for y in range(16):
        for x in range(16):
            r, g, b, a = px[x, y]
            f = None
            if x < edge or y < edge:
                f = 1.28
            if x >= 16 - edge or y >= 16 - edge:
                f = 0.62
            if f:
                px[x, y] = (min(255, int(r * f)), min(255, int(g * f)), min(255, int(b * f)), 255)


def azurite_block():
    img = Image.new('RGBA', (16, 16))
    glow = {}
    rng = random.Random(404)
    ramp = AZURITE
    seeds = [(rng.uniform(0, 16), rng.uniform(0, 16), rng.uniform(0.1, 1.0)) for _ in range(9)]
    for y in range(16):
        for x in range(16):
            best = sorted(seeds, key=lambda s: (s[0] - x) ** 2 + (s[1] - y) ** 2)
            d1 = math.hypot(best[0][0] - x, best[0][1] - y)
            d2 = math.hypot(best[1][0] - x, best[1][1] - y)
            t = best[0][2]
            t = t * 0.6 + (1 - (x + y) / 32) * 0.4
            col = ramp_at(ramp, 0.18 + t * 0.62)
            if d2 - d1 < 0.7:  # facet edge
                col = ramp_at(ramp, 0.12 + t * 0.35)
            img.putpixel((x, y), col + (255,))
            glow[(x, y)] = 25 + int(60 * t)
    # light streaks
    for k in range(3, 9):
        over(img, k, 12 - k + 1, ramp[5] + (255,)); glow[(k, 12 - k + 1)] = 140
    for (x, y) in [(11, 3), (12, 2), (4, 11), (3, 12)]:
        sparkle(img, glow, x, y, (255, 255, 255), 200)
    bevel(img, ramp)
    return img, mer_from(glow, metal=40, rough=70, gem_metal=40, gem_rough=70)


def pyrelite_block():
    img = Image.new('RGBA', (16, 16))
    glow = {}
    ramp = PYRELITE
    for y in range(16):
        for x in range(16):
            seam = (x == 7) or (y == 7) or x == 0 or y == 0 or x == 15 or y == 15
            lx, ly = (x - 1) % 7 if x < 7 else (x - 8) % 7, (y - 1) % 7 if y < 7 else (y - 8) % 7
            n = fbm(909, x, y, 16, (2, 4, 8), (0.5, 0.3, 0.2))
            plate = ramp_at(ramp, 0.05 + n * 0.2)
            # per-plate bevel
            if lx == 0 or ly == 0:
                plate = tint(plate, 1.6)
            elif lx == 6 or ly == 6:
                plate = tint(plate, 0.55)
            if seam:
                t = fbm(11, x, y, 16, (4, 8, 16), (0.5, 0.3, 0.2))
                col = ramp_at(ramp, 0.42 + t * 0.4)
                img.putpixel((x, y), col + (255,)); glow[(x, y)] = int(110 + 120 * t)
            else:
                img.putpixel((x, y), plate + (255,))
    # glowing cores
    for (cx, cy) in [(3, 3), (11, 3), (3, 11), (11, 11)]:
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            col = ramp[5] if (dx, dy) == (0, 0) else (ramp[4] if (dx + dy) < 2 else ramp[3])
            over(img, cx + dx, cy + dy, col + (255,)); glow[(cx + dx, cy + dy)] = 230
    # hairline lava cracks across plates
    for (x, y) in [(2, 5), (3, 6), (5, 5), (12, 1), (13, 2), (13, 5), (2, 9), (1, 10), (4, 14), (5, 13), (10, 9), (12, 13), (13, 14)]:
        over(img, x, y, ramp[3] + (255,)); glow[(x, y)] = 120
    return img, mer_from(glow, metal=140, rough=95, gem_metal=20, gem_rough=80)


def eclipsite_block():
    img = Image.new('RGBA', (16, 16))
    glow = {}
    rng = random.Random(606)
    ramp = ECLIPSITE
    for y in range(16):
        for x in range(16):
            n = fbm(414, x, y, 16, (2, 4, 8), (0.5, 0.3, 0.2))
            # swirling iridescent ridges
            sw = math.sin((x * 0.55 + y * 0.9) + n * 6.0)
            base = 0.05 + n * 0.2
            col = ramp_at(ramp, base)
            if abs(sw) < 0.18:
                t = 1 - abs(sw) / 0.18
                col = ramp_at(ramp, 0.42 + 0.3 * t)
                glow[(x, y)] = int(60 + 120 * t)
            img.putpixel((x, y), col + (255,))
    # central eclipse emblem
    eclipse_motif(img, glow, 8, 8, rng, ramp, 3.2, 1.3)
    # frame
    px = img.load()
    for y in range(16):
        for x in range(16):
            if x in (0, 15) or y in (0, 15):
                px[x, y] = ramp_at(ramp, 0.08) + (255,)
            elif x in (1, 14) or y in (1, 14):
                c = px[x, y]
                f = 1.5 if (x == 1 or y == 1) else 0.55
                px[x, y] = tuple(min(255, int(v * f)) for v in c[:3]) + (255,)
    for (x, y) in [(3, 3), (12, 3), (3, 12), (12, 12), (5, 13), (13, 6)]:
        sparkle(img, glow, x, y, (159, 244, 255), 255)
    return img, mer_from(glow, metal=120, rough=60, gem_metal=130, gem_rough=50)


def build_all():
    jobs = {
        'azurite_ore': azurite_ore, 'pyrelite_ore': pyrelite_ore, 'eclipsite_ore': eclipsite_ore,
        'azurite_block': azurite_block, 'pyrelite_block': pyrelite_block, 'eclipsite_block': eclipsite_block,
    }
    for n, fn in jobs.items():
        img, mer = fn()
        write_block_texture(n, img, mer)
    return list(jobs)


if __name__ == '__main__':
    names = build_all()
    up_sheet([f'{RP}/textures/blocks/{n}.png' for n in names], PREVIEW + '/blocks_a.png', 12, 6)
