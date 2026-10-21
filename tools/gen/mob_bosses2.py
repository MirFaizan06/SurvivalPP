"""Models for the three v1.2 overworld bosses: Hollow King, Mosswood Colossus, Silkqueen."""
import math
from common import *
from geo import Model, fbm3
import paint as P
from mob_hostiles import solid_glow, R


# ============================================================================== HOLLOW KING
KING_ID = 'geometry.ecr_hollow_king'


def king_materials():
    bone = R('#2c342c', '#566055', '#8f9a8a', '#c4cdbd', '#eef3e4')
    iron = R('#0c0f10', '#1b2224', '#2f3a3c', '#465456', '#6a7c7e')
    gold = R('#3a2808', '#6a4a10', '#a67a1c', '#d4a62c', '#f4d460')
    cloak = R('#08100c', '#10201a', '#1a3a2c', '#2a5842')
    wood = R('#150e08', '#2b1c10', '#4a3220', '#6a4a30')
    soul = R('#0f6a30', '#22c060', '#66f09a', '#d8ffe8')
    dark = R('#020403', '#070c09', '#101a14')

    def cloak_fn(ctx):
        r, g, b, a, gl = P.make(cloak, scale=0.4, base=0.5, amp=0.5, bevel=0.1, seed=91, streak=(1, 0.3))(ctx)
        if ctx.face in ('north', 'south', 'east', 'west') and ctx.h > 3 and ctx.j >= ctx.h - 1:
            c = ramp_at(gold, 0.55)
            return (c[0], c[1], c[2], 255, 0)
        return (r, g, b, a, gl)

    def armor_fn(ctx):
        r, g, b, a, gl = P.make(iron, scale=0.35, base=0.5, amp=0.5, bevel=0.22, seed=92)(ctx)
        n = fbm3(ctx.W, 93, 0.5, 2)
        if n > 0.72:                                                               # verdigris / rust blooms
            c = ramp_at(R('#1a3a30', '#2f6a55', '#58a88a'), 0.3 + n * 0.5)
            return (c[0], c[1], c[2], 255, 0)
        return (r, g, b, a, gl)

    return {
        'bone': P.make(bone, scale=0.45, base=0.55, amp=0.32, bevel=0.2, seed=94),
        'armor': armor_fn, 'gold': P.make(gold, scale=0.45, base=0.55, amp=0.4, bevel=0.2, seed=95),
        'cloak': cloak_fn, 'wood': P.make(wood, scale=0.5, base=0.5, amp=0.4, bevel=0.1, seed=96, streak=(1, 0.5)),
        'dark': P.make(dark, scale=0.5, base=0.5, amp=0.3, seed=97),
        'soul': solid_glow(soul, 0.5, 1.0, 255, 98, rim=False), 'soul_dim': solid_glow(soul, 0.25, 0.55, 150, 99, rim=False),
    }


def hollow_king():
    m = Model(KING_ID, 256, 128, bounds=(3.0, 4.2, (0, 1.8, 0)))
    B = m.bone
    B('root', None, (0, 0, 0))
    B('body', 'root', (0, 24, 0))
    m.cube('body', (-6, 22, -2.8), (12, 4, 5.6), 'bone')                                       # pelvis
    m.cube('body', (-1.6, 26, -1.6), (3.2, 16, 3.2), 'bone')                                    # spine
    for k in range(6):
        w = 13 - abs(k - 1.5) * 1.2
        m.cube('body', (-w / 2, 40 - k * 2.6, -3.0), (w, 1.2, 6.2), 'bone')                      # ribs
    m.cube('body', (-7, 30.6, -4.6), (14, 11.4, 2.4), 'armor', params={'seed': 1})            # cuirass
    m.cube('body', (-7.6, 29.6, -4.9), (15.2, 1.4, 2.8), 'gold')
    m.cube('body', (-2, 33.6, -5.3), (4, 4.6, 0.8), 'soul')                                     # soul-core in the chest
    m.cube('body', (-5.6, 24, -4.2), (11.2, 6.4, 1.8), 'armor', params={'seed': 2})           # faulds
    m.cube('body', (-5, 18, -3.8), (10, 6, 1.2), 'cloak', params={'seed': 3})                  # tabard
    for s in (-1, 1):
        m.cube('body', (s * 9.6 - 3.6, 39.4, -4.4), (7.2, 3.6, 8.8), 'armor', rot=(0, 0, -12 * s), pivot=(s * 9.6, 41, 0), params={'seed': 4})   # pauldrons
        m.cube('body', (s * 9.6 - 3.0, 41.8, -4.0), (6, 1.4, 8), 'gold', rot=(0, 0, -12 * s), pivot=(s * 9.6, 41, 0))
        m.cube('body', (s * 11.6 - 0.9, 43.4, -0.9), (1.8, 6, 1.8), 'armor', rot=(0, 0, -22 * s), pivot=(s * 11.6, 43.4, 0))
        m.cube('body', (s * 6.0 - 0.9, 43.8, -0.9), (1.8, 5, 1.8), 'armor', rot=(0, 0, -10 * s), pivot=(s * 6, 43.8, 0))
    m.cube('body', (-9.6, 8, 3.6), (19.2, 36, 1.2), 'cloak', rot=(-3, 0, 0), pivot=(0, 44, 3.6), params={'seed': 5})    # royal cloak
    m.cube('body', (-9.9, 41.4, 3.2), (19.8, 2.6, 2), 'gold')
    for k in range(6):
        bn = f'rag{k}'
        x = -9 + k * 3.6
        B(bn, 'body', (x + 1.8, 10, 4.4))
        m.cube(bn, (x, 0 + (k % 2) * 2, 4.0), (3.4, 10 - (k % 2) * 2, 1.0), 'cloak', params={'seed': 8 + k})
    # head
    B('head', 'body', (0, 42, 0))
    m.cube('head', (-5, 42, -5), (10, 10, 10), 'bone', params={'seed': 11})
    m.cube('head', (-3.6, 41.0, -5.2), (7.2, 1.8, 1.4), 'bone')                                 # jaw
    for k in range(5):
        m.cube('head', (-3.4 + k * 1.5, 40.6, -5.5), (0.8, 1.6, 0.5), 'bone')
    m.cube('head', (-1, 44.6, -5.4), (2, 2.4, 0.6), 'dark')                                      # nose
    for s in (-1, 1):
        m.cube('head', (s * 2.5 - 1.6, 46.4, -5.3), (3.2, 2.8, 0.6), 'dark')
        m.cube('head', (s * 2.5 - 1.0, 46.8, -5.5), (2, 1.8, 0.6), 'soul', params={'rim': False})
    m.cube('head', (-5.7, 51.6, -5.7), (11.4, 2.6, 11.4), 'gold', params={'seed': 12})        # crown band
    for k in range(8):
        a = k / 8 * math.tau
        x, z = math.cos(a) * 5.0, math.sin(a) * 5.0
        h = 5.4 if k % 2 == 0 else 3.4
        m.cube('head', (x - 0.8, 54.2, z - 0.8), (1.6, h, 1.6), 'gold')
        m.cube('head', (x - 0.5, 54.2 + h, z - 0.5), (1, 1, 1), 'soul' if k % 2 == 0 else 'gold')
    m.cube('head', (-1.2, 52.2, -6.0), (2.4, 1.6, 0.6), 'soul', params={'rim': False})          # front jewel
    # arms
    def arm(s, tag):
        x = 10.4 * s
        up, lo = f'arm_{tag}', f'forearm_{tag}'
        B(up, 'body', (x, 40.4, 0))
        m.cube(up, (x - 1.6, 29.6, -1.6), (3.2, 11.4, 3.2), 'bone')
        m.cube(up, (x - 2.4, 31.4, -2.4), (4.8, 3.2, 4.8), 'armor', params={'seed': 20 + s})
        B(lo, up, (x, 30, 0))
        m.cube(lo, (x - 1.5, 19.4, -1.5), (3, 11, 3), 'bone')
        m.cube(lo, (x - 2.2, 20.4, -2.2), (4.4, 6.4, 4.4), 'armor', params={'seed': 22 + s})
        m.cube(lo, (x - 2.0, 25.8, -2.0), (4, 1.2, 4), 'gold')
        m.cube(lo, (x - 1.5, 16.8, -1.5), (3, 3.2, 3), 'bone')
        for k in (-1, 0, 1):
            m.cube(lo, (x + k * 1.1 - 0.4, 12.6, -1.3), (0.8, 4.6, 0.8), 'bone', rot=(-12, 0, 0), pivot=(x + k * 1.1, 17, -1))
        if tag == 'r':
            B('scepter', lo, (x, 17.5, -1))
            m.cube('scepter', (x - 0.9, -6, -2.0), (1.8, 44, 1.8), 'wood', params={'seed': 30})
            m.cube('scepter', (x - 1.4, 8, -2.5), (2.8, 1.2, 2.8), 'gold')
            m.cube('scepter', (x - 1.4, 17, -2.5), (2.8, 1.2, 2.8), 'gold')
            m.cube('scepter', (x - 2.2, 38, -3.3), (4.4, 4, 4.4), 'bone')                       # skull head
            m.cube('scepter', (x - 1.4, 40.4, -3.6), (0.9, 0.9, 0.5), 'dark'); m.cube('scepter', (x + 0.5, 40.4, -3.6), (0.9, 0.9, 0.5), 'dark')
            m.cube('scepter', (x - 1.8, 42.4, -2.9), (3.6, 4.0, 3.6), 'soul', params={'rim': False})     # soul orb
            for k in range(4):
                a = k / 4 * math.tau
                m.cube('scepter', (x + math.cos(a) * 2.6 - 0.5, 41.4, -1.1 + math.sin(a) * 2.6 - 0.5), (1, 5, 1), 'gold', rot=(0, 0, 0))
    arm(1, 'l'); arm(-1, 'r')
    # legs
    def leg(s, tag):
        x = 3.6 * s
        up, lo = f'leg_{tag}', f'shin_{tag}'
        B(up, 'body', (x, 23, 0))
        m.cube(up, (x - 1.8, 12, -1.8), (3.6, 11, 3.6), 'bone')
        m.cube(up, (x - 2.6, 13, -2.6), (5.2, 6, 5.2), 'armor', params={'seed': 40 + s})
        B(lo, up, (x, 12, 0))
        m.cube(lo, (x - 1.6, 2, -1.6), (3.2, 10, 3.2), 'bone')
        m.cube(lo, (x - 2.4, 1.6, -2.4), (4.8, 7, 4.8), 'armor', params={'seed': 42 + s})
        m.cube(lo, (x - 2.2, 8.4, -2.2), (4.4, 1.4, 4.4), 'gold')
        m.cube(lo, (x - 2.6, 0, -4.4), (5.2, 2.4, 8.2), 'armor', params={'seed': 44 + s})
    leg(1, 'l'); leg(-1, 'r')
    return m


# ============================================================================== MOSSWOOD COLOSSUS
COL_ID = 'geometry.ecr_mosswood_colossus'


def colossus_materials():
    bark = R('#150d07', '#2a1a0d', '#47301a', '#664726', '#86623a')
    stone = R('#1a201a', '#2f3a2e', '#4a5a47', '#6a7d64', '#8ca084')
    moss = R('#0a2a10', '#14501c', '#1f8030', '#38b848', '#7ae070')
    leaf = R('#0a3a14', '#17702a', '#26a83e', '#5ae060', '#a8ff90')
    core = R('#2a6a08', '#6ad020', '#b8f850', '#f2ffc0')
    dark = R('#040804', '#0a140a', '#142014')

    def bark_fn(ctx):
        r, g, b, a, gl = P.make(bark, scale=0.35, base=0.5, amp=0.55, bevel=0.14, seed=101, streak=(1, 0.28), octaves=3)(ctx)
        n = fbm3(ctx.W, 102, 0.28, 3)
        if n > 0.66 and ctx.face != 'down':
            c = ramp_at(moss, 0.3 + (n - 0.66) * 3.2)
            return (c[0], c[1], c[2], 255, 0)
        return (r, g, b, a, gl)

    def stone_fn(ctx):
        r, g, b, a, gl = P.make(stone, scale=0.35, base=0.5, amp=0.5, bevel=0.2, seed=103)(ctx)
        n = fbm3(ctx.W, 104, 0.3, 3)
        if n > 0.6 and ctx.face != 'down':
            c = ramp_at(moss, 0.25 + (n - 0.6) * 3.0)
            return (c[0], c[1], c[2], 255, 0)
        return (r, g, b, a, gl)

    return {
        'bark': bark_fn, 'stone': stone_fn, 'moss': P.make(moss, scale=0.5, base=0.5, amp=0.45, bevel=0.12, seed=105),
        'leaf': P.make(leaf, scale=0.7, base=0.5, amp=0.5, bevel=0.15, seed=106), 'dark': P.make(dark, scale=0.5, base=0.5, amp=0.3, seed=107),
        'core': solid_glow(core, 0.4, 1.0, 255, 108, rim=False), 'eye': solid_glow(core, 0.7, 1.0, 255, 109, rim=False),
        'vine': P.make(leaf, scale=0.8, base=0.4, amp=0.4, bevel=0.1, seed=110, streak=(1, 0.4)),
    }


def colossus():
    m = Model(COL_ID, 256, 256, bounds=(5.0, 6.4, (0, 2.6, 0)))
    B = m.bone
    B('root', None, (0, 0, 0))
    B('body', 'root', (0, 40, 0))
    m.cube('body', (-12, 36, -8), (24, 16, 16), 'bark', params={'seed': 1})                      # hips / lower trunk
    m.cube('body', (-15, 48, -9.5), (30, 22, 19), 'bark', params={'seed': 2})                    # chest trunk
    m.cube('body', (-13, 66, -7.5), (26, 5, 15), 'stone', params={'seed': 3})                    # shoulder yoke
    m.cube('body', (-4.5, 52, -10.3), (9, 12, 1.4), 'core')                                      # glowing heart in a cleft
    m.cube('body', (-6, 51, -10.0), (12, 14, 0.8), 'dark')
    m.cube('body', (-15.6, 56, -4), (1.4, 10, 8), 'stone', params={'seed': 4}); m.cube('body', (14.2, 56, -4), (1.4, 10, 8), 'stone', params={'seed': 5})
    m.cube('body', (-13, 47.4, -10.2), (26, 3, 20.4), 'moss', params={'seed': 6})                # moss belt
    m.cube('body', (-10, 70.4, -6), (20, 3.2, 12), 'moss', params={'seed': 7})
    for k in range(5):                                                                              # saplings growing from the back
        x = -10 + k * 5
        m.cube('body', (x - 0.9, 70, 2.2 + (k % 2) * 3), (1.8, 8 + (k % 3) * 2, 1.8), 'bark', rot=(-10 + k * 4, 0, 0), pivot=(x, 70, 3))
        m.cube('body', (x - 3, 77 + (k % 3) * 2, 0.4 + (k % 2) * 3), (6, 5, 6), 'leaf', params={'seed': 20 + k})
    for k in range(8):                                                                              # hanging vines (sway)
        bn = f'vine{k}'
        x = -12.5 + k * 3.6
        B(bn, 'body', (x + 1.2, 50, -9.8))
        m.cube(bn, (x, 40 - (k % 3) * 3, -10.4), (2.4, 10 + (k % 3) * 3, 0.8), 'vine', params={'seed': 30 + k})
    # head
    B('head', 'body', (0, 70, 0))
    m.cube('head', (-6, 70, -6), (12, 11, 11), 'bark', params={'seed': 40})
    m.cube('head', (-5.4, 72, -7), (10.8, 8, 1.6), 'stone', params={'seed': 41})              # bark mask
    for s in (-1, 1):
        m.cube('head', (s * 2.8 - 1.4, 75.8, -7.4), (2.8, 2, 0.8), 'eye', params={'rim': False})
        m.cube('head', (s * 4.2 - 0.9, 80, -1), (1.8, 9, 1.8), 'bark', rot=(0, 0, -18 * s), pivot=(s * 4.2, 80, 0), params={'seed': 42})                 # branch antlers
        m.cube('head', (s * 7.6 - 0.7, 87.2, -1), (1.4, 6, 1.4), 'bark', rot=(0, 0, -42 * s), pivot=(s * 7.6, 87.2, 0), params={'seed': 43})
        m.cube('head', (s * 9.6 - 3, 90, -3), (6, 4, 6), 'leaf', params={'seed': 44})
    m.cube('head', (-3, 70.4, -7.2), (6, 2.2, 1), 'dark')
    m.cube('head', (-6.6, 80, -6.6), (13.2, 2.4, 13.2), 'moss', params={'seed': 45})
    # arms
    def arm(s, tag):
        x = 19 * s
        up, lo = f'arm_{tag}', f'forearm_{tag}'
        B(up, 'body', (x, 66, 0))
        m.cube(up, (x - 5, 46, -5), (10, 22, 10), 'bark', params={'seed': 50 + s})
        m.cube(up, (x - 6, 60, -6), (12, 5, 12), 'stone', params={'seed': 52 + s})
        B(lo, up, (x, 46, 0))
        m.cube(lo, (x - 6, 24, -6), (12, 22, 12), 'bark', params={'seed': 54 + s})
        m.cube(lo, (x - 7.4, 12, -7.4), (14.8, 13, 14.8), 'stone', params={'seed': 56 + s})   # boulder fist
        m.cube(lo, (x - 8, 20, -8), (16, 3, 16), 'moss')
        for k in (-1, 0, 1):
            m.cube(lo, (x + k * 4.2 - 1.6, 8, -8.6), (3.2, 5, 3.2), 'stone')
    arm(1, 'l'); arm(-1, 'r')
    # legs
    def leg(s, tag):
        x = 8 * s
        up, lo = f'leg_{tag}', f'shin_{tag}'
        B(up, 'body', (x, 38, 0))
        m.cube(up, (x - 6, 18, -6), (12, 20, 12), 'bark', params={'seed': 60 + s})
        m.cube(up, (x - 6.6, 30, -6.6), (13.2, 3.6, 13.2), 'moss')
        B(lo, up, (x, 18, 0))
        m.cube(lo, (x - 5.4, 4, -5.4), (10.8, 14, 10.8), 'bark', params={'seed': 62 + s})
        m.cube(lo, (x - 7, 0, -9), (14, 5, 17), 'stone', params={'seed': 64 + s})
    leg(1, 'l'); leg(-1, 'r')
    return m


# ============================================================================== SILKQUEEN
QUEEN_ID = 'geometry.ecr_silkqueen'


def queen_materials():
    shell = R('#07060d', '#100d22', '#1c1638', '#2c2358', '#42387f')
    pale = R('#6a6490', '#9a94c0', '#cdc8e6', '#f0eeff')
    gold = R('#4a3408', '#8a620f', '#c8921c', '#f2c744')
    hair = R('#030206', '#0a0814', '#14102a')
    fang = R('#4a3d3a', '#8e7e74', '#d8c9b8', '#f6efe0')
    eye = R('#4a0a6a', '#a020e0', '#e060ff', '#ffe0ff')
    venom = R('#1a5a10', '#3ab020', '#7aee50', '#d0ffb0')
    silk = R('#8f88b0', '#c4bfe0', '#eeebfb')

    def abdomen(ctx):
        r, g, b, a, gl = P.make(shell, scale=0.4, base=0.5, amp=0.5, bevel=0.1, seed=121, streak=(1, 0.4))(ctx)
        W = ctx.W
        if ctx.face == 'up':                                                  # an hourglass-ish queen's mark on the back
            u = (W[0]) / 14.0; v = (W[2] - 18) / 14.0
            if abs(u) < 0.22 + 0.5 * abs(v) ** 1.2 and abs(v) < 0.8 and (abs(u) < 0.18 or abs(v) > 0.2):
                c = ramp_at(gold, 0.4 + 0.5 * fbm3(W, 122, 0.5, 2))
                return (c[0], c[1], c[2], 255, 0)
        if int(W[2] * 0.6 + 200) % 8 == 0:
            c = ramp_at(pale, 0.35 + 0.3 * fbm3(W, 123, 0.5, 2))
            return (c[0], c[1], c[2], 255, 0)
        return (r, g, b, a, gl)

    def leg_fn(ctx):
        r, g, b, a, gl = P.make(shell, scale=0.5, base=0.5, amp=0.45, bevel=0.1, seed=124)(ctx)
        if int(ctx.W[0] * 0.5 + ctx.W[2] * 0.5 + 300) % 9 == 0:
            c = ramp_at(gold, 0.5)
            return (c[0], c[1], c[2], 255, 0)
        return (r, g, b, a, gl)

    return {
        'abdomen': abdomen, 'thorax': P.make(shell, scale=0.4, base=0.45, amp=0.45, bevel=0.12, seed=125), 'leg': leg_fn,
        'hair': P.make(hair, scale=0.7, base=0.5, amp=0.4, seed=126), 'pale': P.make(pale, scale=0.5, base=0.45, amp=0.3, bevel=0.15, seed=127),
        'gold': P.make(gold, scale=0.45, base=0.55, amp=0.4, bevel=0.2, seed=128),
        'fang': P.make(fang, scale=0.5, base=0.6, amp=0.3, bevel=0.2, seed=129), 'eye': solid_glow(eye, 0.5, 1.0, 255, 130, rim=False),
        'venom': solid_glow(venom, 0.4, 0.9, 200, 131, rim=False), 'silk': P.make(silk, scale=0.6, base=0.55, amp=0.25, bevel=0.15, seed=132),
    }


def silkqueen():
    k = 2.3
    m = Model(QUEEN_ID, 256, 128, bounds=(6.0, 3.0, (0, 1.2, 0)))
    B = m.bone
    o = lambda *c: tuple(v * k for v in c)

    def cube(bone, org, size, mat, **kw):
        if 'pivot' in kw and kw['pivot'] is not None:
            kw['pivot'] = o(*kw['pivot'])
        m.cube(bone, o(*org), o(*size), mat, **kw)

    B('root', None, (0, 0, 0))
    B('body', 'root', o(0, 8, 0))
    cube('body', (-4, 4, -5), (8, 7, 8), 'thorax', params={'seed': 1})
    cube('body', (-5.5, 3.2, 2), (11, 10, 11), 'abdomen', params={'seed': 2})
    cube('body', (-1.8, 4.4, 12.4), (3.6, 3.2, 2), 'silk')
    cube('body', (-1.2, 5.0, 14.2), (2.4, 1.8, 1.4), 'venom')
    for s in (-1, 1):
        cube('body', (s * 3.2 - 0.8, 11.0, -2.2), (1.6, 3.4, 1.6), 'gold', rot=(-12, 0, 8 * s), pivot=(s * 3.2, 11, -1.6))     # queen's spines
    for i in range(5):
        cube('body', (-0.9, 12.6 + (0 if i in (0, 4) else 0.6), -3.4 + i * 1.8), (1.8, 2.6 + (2 - abs(i - 2)) * 0.8, 1.2), 'gold', rot=(-8, 0, 0), pivot=(0, 13, -3.0 + i * 1.8))   # crest
    for kk in range(10):
        cube('body', (-4.8 + (kk % 5) * 2.4, 12.6, 3.6 + (kk // 5) * 4.4), (0.8, 2.6, 0.8), 'hair', rot=(-12, 0, 0), pivot=(-4.4 + (kk % 5) * 2.4, 12.6, 4 + (kk // 5) * 4.4))
    B('head', 'body', o(0, 8, -5))
    cube('head', (-3, 4.4, -9.4), (6, 5.4, 4.6), 'thorax', params={'seed': 11})
    for (ex, ey, es) in ((-1.7, 8.2, 1.2), (1.7, 8.2, 1.2), (-2.8, 7.2, 0.9), (2.8, 7.2, 0.9), (-0.8, 9.0, 0.8), (0.8, 9.0, 0.8), (-2.2, 9.1, 0.6), (2.2, 9.1, 0.6)):
        cube('head', (ex - es / 2, ey - es / 2, -9.8), (es, es, 0.6), 'eye', params={'rim': False})
    for s in (-1, 1):
        cube('head', (s * 1.4 - 0.6, 2.8, -10.6), (1.2, 4, 1.4), 'fang', rot=(-10, 0, 8 * s), pivot=(s * 1.4, 6, -9.6))
        cube('head', (s * 2.9 - 0.7, 4.4, -11.2), (1.4, 2.4, 1.8), 'thorax')
        cube('head', (s * 1.4 - 0.25, 2.2, -10.8), (0.5, 1.2, 0.5), 'venom')
    for i in range(8):
        s = 1 if i % 2 == 0 else -1
        row = i // 2
        z = -3.4 + row * 2.8
        up, lo = f'leg{i}', f'leg{i}_lower'
        yaw = (-34 + row * 22) * s
        B(up, 'body', o(s * 3.6, 8.4, z), rot=(0, yaw, 0))
        cube(up, (s * 3.6 + (0 if s > 0 else -7.6), 7.4, z - 0.9), (7.6, 1.8, 1.8), 'leg', rot=(0, 0, 28 * s), pivot=(s * 3.6, 8.4, z), params={'seed': i})
        B(lo, up, o(s * 3.6 + s * 6.6, 12.0, z))
        cube(lo, (s * 3.6 + s * 6.6 + (0 if s > 0 else -1.6), 0, z - 0.8), (1.6, 12.4, 1.6), 'leg', rot=(0, 0, 8 * s), pivot=(s * 3.6 + s * 6.6, 12.0, z), params={'seed': 10 + i})
        cube(lo, (s * 3.6 + s * 7.2 - 0.6, -0.4, z - 0.6), (1.2, 1.0, 1.2), 'hair')
    return m


MODELS = {
    'hollow_king': (hollow_king, king_materials, KING_ID),
    'mosswood_colossus': (colossus, colossus_materials, COL_ID),
    'silkqueen': (silkqueen, queen_materials, QUEEN_ID),
}
