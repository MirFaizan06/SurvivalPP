"""Voidweaver - a floating, robed End sorcerer wearing a cracked bone mask."""
import math
from common import *
from geo import Model, fbm3
import paint as P

ID = 'geometry.ecr_voidweaver'


def materials():
    robe = [hx(x) for x in ['#05020f', '#0b0524', '#140a3a', '#1f1257', '#2f1c80']]
    cloth2 = [hx(x) for x in ['#08041a', '#100833', '#1a0e4f', '#271770']]
    trim = [hx(x) for x in ['#3a2570', '#6a45b8', '#a07af0', '#d3b8ff', '#f4eaff']]
    mask = [hx(x) for x in ['#2c2644', '#575079', '#8f89b3', '#c9c4e2', '#f3f0ff']]
    skin = [hx(x) for x in ['#0a0714', '#161029', '#241a40', '#352960']]

    def robe_fn(ctx):
        base = P.make(robe, scale=0.45, base=0.45, amp=0.45, bevel=0.12, seed=3, streak=(1, 0.3))(ctx)
        W = ctx.W
        # woven vertical pinstripes + a trim band every 10 units
        stripe = int(W[0] * 1.0) % 3 == 0
        r, g, b, a, gl = base
        if stripe:
            r, g, b = int(r * 1.25), int(g * 1.25), int(b * 1.4)
        if ctx.cube.params.get('band') and (int(W[1]) % 10 in (0,)):
            c = ramp_at(trim, 0.55)
            return (c[0], c[1], c[2], 255, 70)
        return (min(255, r), min(255, g), min(255, b), a, gl)

    def tatter_fn(ctx):
        r, g, b, a, gl = P.make(cloth2, scale=0.5, base=0.5, amp=0.5, bevel=0.1, seed=4, streak=(1, 0.25))(ctx)
        # glowing hem line along the bottom 1 texel of each strip
        if ctx.face in ('north', 'south', 'east', 'west') and ctx.j >= ctx.h - 1:
            c = ramp_at(ECLIPSITE, 0.7)
            return (c[0], c[1], c[2], 255, 200)
        return (r, g, b, a, gl)

    def crystal_fn(ctx):
        n = fbm3(ctx.W, 12, 0.4, 2)
        t = 0.45 + 0.5 * n
        # facet shading by face
        t = t * {'up': 1.1, 'down': 0.7}.get(ctx.face, 0.95)
        c = ramp_at(ECLIPSITE, min(1, t))
        if ctx.cube.params.get('cyan') and n > 0.55:
            c = hx('#9ff4ff')
        d, side = ctx.edge
        if d < 1 and ctx.w > 2:
            c = tuple(int(v * 0.7) for v in c)
        return (c[0], c[1], c[2], 255, 235)

    def eye_fn(ctx):
        d, side = ctx.edge
        c = hx('#e9fdff') if d >= 1 or min(ctx.w, ctx.h) <= 2 else hx('#5ef2ff')
        return (c[0], c[1], c[2], 255, 255)

    def rune_fn(ctx):
        n = fbm3(ctx.W, 5, 0.9, 2)
        c = ramp_at(ECLIPSITE, 0.6 + 0.35 * n)
        return (c[0], c[1], c[2], 255, 255)

    return {
        'robe': robe_fn,
        'tatter': tatter_fn,
        'trim': P.make(trim, scale=0.5, base=0.5, amp=0.35, bevel=0.3, seed=7),
        'mask': P.make(mask, scale=0.55, base=0.6, amp=0.3, bevel=0.2, seed=8),
        'skin': P.make(skin, scale=0.5, base=0.5, amp=0.4, bevel=0.15, seed=9),
        'crystal': crystal_fn,
        'eye': eye_fn,
        'rune': rune_fn,
    }


def build():
    m = Model(ID, 256, 128, bounds=(2.6, 3.4, (0, 1.4, 0)))
    B = m.bone
    B('root', None, (0, 0, 0))
    B('float', 'root', (0, 0, 0))
    B('body', 'float', (0, 24, 0))
    # robe skirt, stacked and flaring (floating a few units above the ground)
    m.cube('body', (-4.5, 26, -3), (9, 7, 6), 'robe', params={'seed': 1})
    m.cube('body', (-5.5, 19, -3.5), (11, 7, 7), 'robe', params={'seed': 2, 'band': 1})
    m.cube('body', (-6.5, 12, -4), (13, 7, 8), 'robe', params={'seed': 3})
    m.cube('body', (-7.5, 6, -4.5), (15, 6, 9), 'robe', params={'seed': 4, 'band': 1})
    m.cube('body', (-7.9, 5.4, -4.9), (15.8, 1.2, 9.8), 'trim')
    m.cube('body', (-5.2, 30.6, -3.6), (10.4, 1.2, 7.2), 'trim')                              # sash
    m.cube('body', (-1.2, 12, -4.6), (2.4, 19, 0.8), 'trim')                                  # front stole
    m.cube('body', (-1.6, 17, -5.4), (3.2, 3.2, 0.8), 'rune')                                  # glowing sigil
    # chest + shoulders
    m.cube('body', (-5, 32, -3.2), (10, 7, 6.4), 'robe', params={'seed': 5})
    m.cube('body', (-7.5, 37, -3.8), (15, 2.6, 7.6), 'trim')                                  # mantle
    for s in (-1, 1):
        m.cube('body', (s * 7.8 - 2, 36.2, -3), (4, 3.6, 6), 'trim', rot=(0, 0, -14 * s), pivot=(s * 7.8, 38, 0))
        m.cube('body', (s * 9.4 - 0.8, 39.5, -1), (1.6, 6, 2), 'crystal', rot=(0, 0, -28 * s), pivot=(s * 9.4, 39.5, 0), params={'cyan': 1})
    # ------------------------------------------------------------ hem tatters (each its own bone so they sway)
    for k in range(8):
        a = k / 8 * math.tau
        x, z = math.sin(a) * 7.4, math.cos(a) * 4.4
        bn = f'hem{k}'
        B(bn, 'body', (x, 6, z))
        m.cube(bn, (x - 1.2, 0.2, z - 0.6), (2.4, 6, 1.2), 'tatter')
    # back cape tatters
    for k in range(5):
        x = -6 + k * 3
        bn = f'cape{k}'
        B(bn, 'body', (x, 38, 4.2))
        h = 24 + (k % 3) * 5
        m.cube(bn, (x - 1.4, 38 - h, 4), (2.8, h, 0.8), 'tatter')
    # ------------------------------------------------------------ head
    B('head', 'body', (0, 39.5, 0))
    m.cube('head', (-4.4, 39, -4.4), (8.8, 9, 8.8), 'robe', params={'seed': 11})            # hood
    m.cube('head', (-3.6, 47.4, -1.4), (7.2, 2.4, 6), 'robe', rot=(-18, 0, 0), pivot=(0, 47.4, 1.6), params={'seed': 12})   # hood peak
    m.cube('head', (-3, 36.8, 2.4), (6, 10, 3.6), 'robe', rot=(-14, 0, 0), pivot=(0, 40, 3), params={'seed': 13})            # hood back drape
    m.cube('head', (-3.6, 39.6, -5.6), (7.2, 7.6, 1.4), 'mask')                                # bone mask
    m.cube('head', (-3.8, 45.4, -6), (7.6, 1.2, 1.2), 'trim')
    m.cube('head', (-0.5, 40, -6.3), (1, 4, 0.8), 'trim')
    for s in (-1, 1):
        m.cube('head', (s * 1.9 - 1.3, 43, -6.4), (2.6, 1.4, 0.7), 'eye')
        m.cube('head', (s * 1.4 - 0.4, 40.4, -6.3), (0.8, 2.2, 0.7), 'rune')                  # cracked tears
        m.cube('head', (s * 3.5 - 0.9, 44.8, -5.2), (1.8, 6, 1.8), 'mask', rot=(0, 0, -22 * s), pivot=(s * 3.5, 44.8, -4.3))  # mask horn
        m.cube('head', (s * 5.2 - 0.7, 49.2, -5.0), (1.4, 4, 1.4), 'mask', rot=(0, 0, -40 * s), pivot=(s * 5.2, 49.2, -4.3))
    # floating crown shards
    B('crown', 'head', (0, 54, 0))
    for k in range(5):
        a = k / 5 * math.tau
        x, z = math.sin(a) * 5.6, math.cos(a) * 5.6
        h = 6 + (k % 2) * 2
        m.cube('crown', (x - 0.9, 52 + (k % 2), z - 0.9), (1.8, h, 1.8), 'crystal', rot=(0, 0, 0), params={'cyan': 1 if k % 2 else 0})
    # ------------------------------------------------------------ arms
    def arm(s, tag):
        x = 8.2 * s
        up, lo, hd = f'arm_{tag}', f'forearm_{tag}', f'hand_{tag}'
        B(up, 'body', (x, 37, 0), rot=(0, 0, 8 * s))
        m.cube(up, (x - 2.2, 29, -2.2), (4.4, 9, 4.4), 'robe', params={'seed': 20 + s})
        m.cube(up, (x - 2.8, 28.2, -2.8), (5.6, 1.4, 5.6), 'trim')
        B(lo, up, (x, 29, 0), rot=(-26, 0, -6 * s))
        m.cube(lo, (x - 2.6, 20, -2.6), (5.2, 9.6, 5.2), 'robe', params={'seed': 22 + s, 'band': 1})    # flared sleeve
        m.cube(lo, (x - 3, 19.4, -3), (6, 1.2, 6), 'trim')
        B(hd, lo, (x, 20, 0))
        m.cube(hd, (x - 1.6, 16.2, -1.8), (3.2, 4, 3.6), 'skin', params={'seed': 24 + s})
        for k in (-1, 0, 1):
            m.cube(hd, (x + k * 1.2 - 0.4, 11.4, -1.2 + abs(k) * 0.2), (0.8, 5.2, 0.8), 'skin', rot=(-8, 0, 0), pivot=(x + k * 1.2, 16.4, -1))
            m.cube(hd, (x + k * 1.2 - 0.45, 10.6, -1.3 + abs(k) * 0.2), (0.9, 1.4, 0.9), 'eye')
    arm(1, 'l'); arm(-1, 'r')
    # ------------------------------------------------------------ orbiting eclipse shards
    B('orbit', 'body', (0, 28, 0))
    for k in range(4):
        a = k / 4 * math.tau
        x, z = math.sin(a) * 14, math.cos(a) * 14
        m.cube('orbit', (x - 1.2, 22 + (k % 2) * 4, z - 1.2), (2.4, 8, 2.4), 'crystal', rot=(18 * math.cos(a), 0, 18 * math.sin(a)), pivot=(x, 26, z), params={'cyan': k % 2})
    return m
