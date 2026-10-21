"""Models + painters for the four v1.2 hostiles: Gravewalker, Revenant, Cave Weaver, Sporeling.
Every material returns (r, g, b, a, glow) - glow > 0 ends up in the emissive overlay."""
import math
from common import *
from geo import Model, fbm3
import paint as P

R = lambda *c: [hx(x) for x in c]


def solid_glow(ramp, lo=0.5, hi=0.95, glow=255, seed=9, rim=True):
    def fn(ctx):
        n = fbm3(ctx.W, seed, 0.5, 2)
        c = ramp_at(ramp, lo + (hi - lo) * n)
        if rim:
            d, side = ctx.edge
            if d < 1 and min(ctx.w, ctx.h) > 2:
                c = tuple(int(v * 0.7) for v in c)
        return (c[0], c[1], c[2], 255, glow)
    return fn


# ============================================================================== GRAVEWALKER
GRAVE_ID = 'geometry.ecr_gravewalker'


def gravewalker_materials():
    skin = R('#141f19', '#23382c', '#3a5a45', '#5c8063', '#8aa985')
    shroud = R('#1d1a14', '#3a3426', '#615841', '#8f8260', '#bdb084')
    bone = R('#5a5440', '#8f8868', '#c9c1a0', '#ece6cc')
    wrap = R('#2a2218', '#4d3e2a', '#7a6544', '#a88f60')
    moss = R('#0a2410', '#134a1c', '#1f7a2c', '#3ab048')
    dark = R('#050805', '#0c120d', '#161f18')
    glow = R('#0f5a2a', '#1fa85a', '#5af09a', '#c8ffe0')

    def shroud_fn(ctx):
        r, g, b, a, gl = P.make(shroud, scale=0.4, base=0.45, amp=0.5, bevel=0.1, seed=21, streak=(1, 0.35))(ctx)
        n = fbm3(ctx.W, 77, 0.3, 3)
        if n > 0.7:                                            # grave stains
            return (int(r * 0.45), int(g * 0.5), int(b * 0.45), a, 0)
        if n < 0.2 and ctx.W[1] < 16:                          # moss creeping up from the hem
            c = ramp_at(moss, 0.4 + n * 2)
            return (c[0], c[1], c[2], 255, 0)
        return (r, g, b, a, gl)

    return {
        'skin': P.make(skin, scale=0.45, base=0.5, amp=0.45, bevel=0.1, seed=22),
        'shroud': shroud_fn,
        'bone': P.make(bone, scale=0.5, base=0.55, amp=0.3, bevel=0.2, seed=23),
        'wrap': P.make(wrap, scale=0.5, base=0.5, amp=0.4, bevel=0.12, seed=24, streak=(1, 0.5)),
        'moss': P.make(moss, scale=0.55, base=0.5, amp=0.45, bevel=0.1, seed=25),
        'dark': P.make(dark, scale=0.5, base=0.5, amp=0.3, seed=26),
        'eye': solid_glow(glow, 0.6, 1.0, 255, 27),
        'rune': solid_glow(glow, 0.35, 0.7, 150, 28, rim=False),
    }


def gravewalker():
    m = Model(GRAVE_ID, 128, 128, bounds=(1.2, 2.4, (0, 1.1, 0)))
    B = m.bone
    B('root', None, (0, 0, 0))
    B('body', 'root', (0, 12, 0))
    m.cube('body', (-4, 12, -2), (8, 12, 4), 'skin', params={'seed': 1})
    for k in range(4):                                                                        # exposed ribs
        m.cube('body', (-3.2, 15 + k * 2.1, -2.3), (6.4, 0.9, 0.5), 'bone')
    m.cube('body', (-1.2, 16, -2.4), (2.4, 5, 0.3), 'rune')                                  # faint grave-light in the chest
    m.cube('body', (-4.7, 8.5, -2.7), (9.4, 8, 5.4), 'shroud', rot=(4, 0, 0), pivot=(0, 16, 0), params={'seed': 2})
    m.cube('body', (-4.5, 4, 2.0), (9, 20, 0.9), 'shroud', rot=(-3, 0, 0), pivot=(0, 24, 2), params={'seed': 3})     # burial shroud down the back
    m.cube('body', (-5.4, 22.6, -3.0), (10.8, 2.6, 6), 'shroud', params={'seed': 4})                                  # shoulder mantle
    m.cube('body', (-5.9, 23.6, -2.4), (4.4, 1.6, 4.8), 'moss'); m.cube('body', (1.8, 23.8, -2.2), (3.6, 1.4, 4.2), 'moss')
    for k in range(5):                                                                        # tattered hem strips
        x = -4 + k * 2
        bn = f'strip{k}'
        B(bn, 'body', (x + 1, 10, -2.9))
        m.cube(bn, (x + 0.1, 3.6 - (k % 2) * 1.2, -3.3), (1.8, 7 + (k % 2) * 1.2, 0.7), 'shroud', params={'seed': 5 + k})
    # head
    B('head', 'body', (0, 24, 0))
    m.cube('head', (-4, 24, -4), (8, 8, 8), 'skin', params={'seed': 11})
    m.cube('head', (-4.7, 30.4, -4.9), (9.4, 3.2, 9.8), 'shroud', params={'seed': 12})                                # hood crown
    m.cube('head', (-4.7, 23.6, -4.9), (1.8, 7, 9.8), 'shroud', params={'seed': 13}); m.cube('head', (2.9, 23.6, -4.9), (1.8, 7, 9.8), 'shroud', params={'seed': 14})
    m.cube('head', (-3.6, 22.4, 3.4), (7.2, 10, 1.8), 'shroud', rot=(-10, 0, 0), pivot=(0, 30, 4), params={'seed': 15})   # hood back drape
    m.cube('head', (-3.2, 24.6, -4.4), (6.4, 1.8, 0.6), 'bone')                                                       # jaw bone
    for k in range(4):
        m.cube('head', (-2.6 + k * 1.6, 24.4, -4.7), (0.7, 1.2, 0.4), 'bone')
    m.cube('head', (-0.8, 26.2, -4.3), (1.6, 1.8, 0.5), 'dark')                                                        # nose hole
    for s in (-1, 1):
        m.cube('head', (s * 1.9 - 0.9, 28.0, -4.3), (1.8, 1.4, 0.6), 'eye', params={'rim': False})
    m.cube('head', (-4.4, 31.7, -2.0), (3.6, 1.4, 4.4), 'moss'); m.cube('head', (1.6, 31.9, 0.4), (2.8, 1.2, 3), 'moss')
    # arms (long and reaching)
    def arm(s, tag):
        x = 5.8 * s
        up, lo = f'arm_{tag}', f'forearm_{tag}'
        B(up, 'body', (x, 22, 0))
        m.cube(up, (x - 1.8, 13.5, -1.8), (3.6, 9.4, 3.6), 'skin', params={'seed': 30 + s})
        m.cube(up, (x - 2.1, 15.5, -2.1), (4.2, 5.4, 4.2), 'shroud', params={'seed': 32 + s})
        B(lo, up, (x, 14, 0))
        m.cube(lo, (x - 1.5, 5.4, -1.5), (3, 9, 3), 'skin', params={'seed': 34 + s})
        m.cube(lo, (x - 1.8, 7.6, -1.8), (3.6, 1.6, 3.6), 'wrap'); m.cube(lo, (x - 1.8, 10.8, -1.8), (3.6, 1.6, 3.6), 'wrap')
        m.cube(lo, (x - 1.4, 2.2, -1.4), (2.8, 3.4, 2.8), 'bone')
        for k in (-1, 0, 1):
            m.cube(lo, (x + k * 0.9 - 0.3, -0.6, -1.0), (0.6, 3.2, 0.6), 'bone', rot=(-10, 0, 0), pivot=(x + k * 0.9, 2.6, -0.7))
    arm(1, 'l'); arm(-1, 'r')
    # legs
    def leg(s, tag):
        x = 2.0 * s
        B(f'leg_{tag}', 'body', (x, 12, 0))
        m.cube(f'leg_{tag}', (x - 2, 0, -2), (4, 12, 4), 'wrap', params={'seed': 40 + s})
        m.cube(f'leg_{tag}', (x - 2.2, 6.4, -2.2), (4.4, 1.6, 4.4), 'shroud')
        m.cube(f'leg_{tag}', (x - 2.2, 0, -3), (4.4, 1.4, 5.2), 'dark')
    leg(1, 'l'); leg(-1, 'r')
    return m


# ============================================================================== REVENANT
REV_ID = 'geometry.ecr_revenant'


def revenant_materials():
    bone = R('#3a4448', '#6a767a', '#a2b0b2', '#d4e0e0', '#f2fbfb')
    rust = R('#150a06', '#2c170e', '#4a2a18', '#6e4426', '#946236')
    cloak = R('#0a1014', '#131e26', '#1f3140', '#2e475c')
    wood = R('#1a110a', '#33200f', '#5a3a1c', '#80562b')
    dark = R('#020405', '#070b0d', '#10181b')
    cyan = R('#08485a', '#12a0c0', '#5ae6ff', '#d8fbff')

    def cloak_fn(ctx):
        r, g, b, a, gl = P.make(cloak, scale=0.45, base=0.5, amp=0.5, bevel=0.1, seed=51, streak=(1, 0.3))(ctx)
        if ctx.face in ('north', 'south', 'east', 'west') and ctx.j >= ctx.h - 1 and ctx.h > 3:
            c = ramp_at(cyan, 0.5)                                                      # frost-lit hem
            return (c[0], c[1], c[2], 255, 150)
        return (r, g, b, a, gl)

    return {
        'bone': P.make(bone, scale=0.5, base=0.55, amp=0.32, bevel=0.2, seed=52),
        'rust': P.make(rust, scale=0.4, base=0.5, amp=0.55, bevel=0.2, seed=53),
        'cloak': cloak_fn, 'wood': P.make(wood, scale=0.5, base=0.5, amp=0.4, bevel=0.1, seed=54, streak=(1, 0.5)),
        'dark': P.make(dark, scale=0.5, base=0.5, amp=0.3, seed=55),
        'eye': solid_glow(cyan, 0.65, 1.0, 255, 56, rim=False),
        'string': solid_glow(cyan, 0.5, 0.9, 200, 57, rim=False),
        'spine': solid_glow(cyan, 0.3, 0.6, 130, 58, rim=False),
    }


def revenant():
    m = Model(REV_ID, 128, 128, bounds=(1.2, 2.6, (0, 1.2, 0)))
    B = m.bone
    B('root', None, (0, 0, 0))
    B('body', 'root', (0, 12, 0))
    m.cube('body', (-0.9, 12, -0.9), (1.8, 12, 1.8), 'bone')                                        # spine
    m.cube('body', (-0.5, 13.5, -1.3), (1, 9, 0.5), 'spine')                                        # glowing marrow line
    for k in range(5):
        w = 7.4 - abs(k - 1.6) * 0.9
        m.cube('body', (-w / 2, 22 - k * 2.2, -2.0), (w, 0.9, 4), 'bone')                            # ribs
    m.cube('body', (-3.4, 10.8, -1.6), (6.8, 2.2, 3.2), 'bone')                                      # pelvis
    for s in (-1, 1):
        m.cube('body', (s * 5.4 - 2.1, 22.2, -2.6), (4.2, 2.6, 5.2), 'rust', rot=(0, 0, -10 * s), pivot=(s * 5.4, 24, 0), params={'seed': 2})   # pauldrons
        m.cube('body', (s * 5.8 - 0.7, 24.6, -0.7), (1.4, 2.6, 1.4), 'rust', rot=(0, 0, -20 * s), pivot=(s * 5.8, 24.6, 0))               # spikes
    m.cube('body', (-5.6, 3, 2.4), (11.2, 21, 0.9), 'cloak', rot=(-4, 0, 0), pivot=(0, 24, 2.4), params={'seed': 3})       # cloak
    for k in range(5):
        bn = f'rag{k}'
        x = -5 + k * 2.5
        B(bn, 'body', (x + 1.25, 12, 3.0))
        m.cube(bn, (x, 0.5 + (k % 2) * 1.5, 2.5), (2.4, 11.5 - (k % 2) * 1.5, 0.8), 'cloak', params={'seed': 6 + k})
    m.cube('body', (-4.2, 11.0, -2.4), (8.4, 1.2, 4.8), 'rust')                                      # belt
    # head
    B('head', 'body', (0, 24, 0))
    m.cube('head', (-4, 24, -4), (8, 8, 8), 'bone', params={'seed': 11})
    m.cube('head', (-4.5, 29.6, -4.5), (9, 3.6, 9), 'rust', params={'seed': 12})                      # helm dome
    m.cube('head', (-4.5, 27.4, 3.2), (9, 5, 1.4), 'rust', params={'seed': 13})                        # helm neck guard
    m.cube('head', (-0.7, 25, -4.9), (1.4, 5.6, 0.9), 'rust')                                            # nasal guard
    for s in (-1, 1):
        m.cube('head', (s * 2.0 - 1.2, 27.4, -4.2), (2.4, 2.2, 0.6), 'dark')                           # sockets
        m.cube('head', (s * 2.0 - 0.7, 27.9, -4.45), (1.4, 1.2, 0.5), 'eye', params={'rim': False})
        m.cube('head', (s * 4.4 - 0.5, 28.6, -1.0), (1, 4.2, 1.2), 'rust', rot=(0, 0, -16 * s), pivot=(s * 4.4, 28.6, -0.4))   # horns on the helm
    m.cube('head', (-2.8, 24.2, -4.3), (5.6, 1.6, 0.6), 'bone')
    for k in range(5):
        m.cube('head', (-2.6 + k * 1.1, 23.9, -4.5), (0.6, 1.0, 0.4), 'bone')
    # arms
    def arm(s, tag):
        x = 5.4 * s
        up, lo = f'arm_{tag}', f'forearm_{tag}'
        B(up, 'body', (x, 22, 0))
        m.cube(up, (x - 1, 12.8, -1), (2, 10, 2), 'bone')
        B(lo, up, (x, 13, 0))
        m.cube(lo, (x - 1, 3.6, -1), (2, 10, 2), 'bone')
        m.cube(lo, (x - 1.5, 3.4, -1.5), (3, 1.5, 3), 'rust')                                            # bracer
        m.cube(lo, (x - 1.2, 1.2, -1.2), (2.4, 2.6, 2.4), 'bone')
        if tag == 'r':
            B('bow', lo, (x, 4, -2))
            m.cube('bow', (x - 0.7, 0.4, -3.4), (1.4, 3.6, 1.4), 'wood')                                  # grip
            m.cube('bow', (x - 0.6, 3.8, -3.9), (1.2, 7, 1.2), 'wood', rot=(18, 0, 0), pivot=(x, 4, -3.4))
            m.cube('bow', (x - 0.6, -7.0, -3.9), (1.2, 7, 1.2), 'wood', rot=(-18, 0, 0), pivot=(x, 0.4, -3.4))
            m.cube('bow', (x - 0.2, -7.6, -1.0), (0.4, 17.6, 0.4), 'string')
    arm(1, 'l'); arm(-1, 'r')
    def leg(s, tag):
        x = 2.0 * s
        up, lo = f'leg_{tag}', f'shin_{tag}'
        B(up, 'body', (x, 12, 0))
        m.cube(up, (x - 1, 6, -1), (2, 6, 2), 'bone')
        B(lo, up, (x, 6, 0))
        m.cube(lo, (x - 1, 0.8, -1), (2, 5.2, 2), 'bone')
        m.cube(lo, (x - 1.4, 5.0, -1.4), (2.8, 1.6, 2.8), 'bone')                                       # knee
        m.cube(lo, (x - 1.6, 0, -2.6), (3.2, 1.2, 4.4), 'rust')                                          # boot
    leg(1, 'l'); leg(-1, 'r')
    return m


# ============================================================================== CAVE WEAVER
WEAVER_ID = 'geometry.ecr_cave_weaver'


def weaver_materials():
    shell = R('#0a0912', '#15122a', '#241f44', '#38306a', '#52488f')
    band = R('#4a4570', '#6a6598', '#8f89bc', '#b3add8')
    hair = R('#05040a', '#0d0a1a', '#1a1530')
    silk = R('#3a3560', '#56518a', '#7a74ae')
    fang = R('#4a3d3a', '#8e7e74', '#d8c9b8', '#f6efe0')
    eye = R('#4a0a6a', '#a020e0', '#e060ff', '#ffd0ff')
    venom = R('#1a5a10', '#3ab020', '#7aee50', '#d0ffb0')

    def abdomen(ctx):
        r, g, b, a, gl = P.make(shell, scale=0.4, base=0.5, amp=0.5, bevel=0.1, seed=61, streak=(1, 0.4))(ctx)
        W = ctx.W
        if int(W[2] * 0.8 + 100) % 6 == 0:                              # pale bands across the abdomen
            c = ramp_at(band, 0.4 + 0.4 * fbm3(W, 62, 0.5, 2))
            return (c[0], c[1], c[2], 255, 0)
        return (r, g, b, a, gl)

    def leg_fn(ctx):
        r, g, b, a, gl = P.make(shell, scale=0.5, base=0.5, amp=0.45, bevel=0.1, seed=63)(ctx)
        if int(ctx.W[0] * 0.7 + ctx.W[2] * 0.7 + 200) % 7 == 0:
            c = ramp_at(band, 0.5)
            return (c[0], c[1], c[2], 255, 0)
        return (r, g, b, a, gl)

    return {
        'abdomen': abdomen, 'thorax': P.make(shell, scale=0.4, base=0.45, amp=0.45, bevel=0.12, seed=64),
        'leg': leg_fn, 'hair': P.make(hair, scale=0.7, base=0.5, amp=0.4, seed=65),
        'silk': P.make(silk, scale=0.6, base=0.6, amp=0.25, bevel=0.15, seed=66),
        'fang': P.make(fang, scale=0.5, base=0.6, amp=0.3, bevel=0.2, seed=67),
        'eye': solid_glow(eye, 0.5, 1.0, 255, 68, rim=False),
        'venom': solid_glow(venom, 0.4, 0.9, 200, 69, rim=False),
    }


def weaver():
    m = Model(WEAVER_ID, 128, 64, bounds=(2.4, 1.2, (0, 0.5, 0)))
    B = m.bone
    B('root', None, (0, 0, 0))
    B('body', 'root', (0, 8, 0))
    m.cube('body', (-4, 4, -5), (8, 7, 8), 'thorax', params={'seed': 1})                                 # cephalothorax
    m.cube('body', (-5.5, 3.2, 2), (11, 10, 11), 'abdomen', params={'seed': 2})                            # big banded abdomen
    m.cube('body', (-4.2, 12.4, 3.4), (8.4, 1.4, 8), 'silk', rot=(-6, 0, 0), pivot=(0, 12.4, 6), params={'seed': 3})   # silk saddle
    m.cube('body', (-1.8, 4.4, 12.4), (3.6, 3.2, 2), 'silk')                                                # spinneret
    m.cube('body', (-1.2, 5.0, 14.2), (2.4, 1.8, 1.4), 'venom')
    for k in range(9):                                                                                       # bristles along the back
        m.cube('body', (-3.6 + (k % 3) * 3.6, 11.0 + (k % 2) * 0.6, -3 + (k // 3) * 3.6), (0.7, 2.4, 0.7), 'hair', rot=(-14 + (k % 3) * 14, 0, 0), pivot=(-3.2 + (k % 3) * 3.6, 11.0, -2.6 + (k // 3) * 3.6))
    B('head', 'body', (0, 8, -5))
    m.cube('head', (-3, 4.4, -9.4), (6, 5.4, 4.6), 'thorax', params={'seed': 11})
    for k, (ex, ey, es) in enumerate(((-1.7, 8.2, 1.1), (1.7, 8.2, 1.1), (-2.8, 7.2, 0.8), (2.8, 7.2, 0.8), (-0.8, 9.0, 0.7), (0.8, 9.0, 0.7))):
        m.cube('head', (ex - es / 2, ey - es / 2, -9.8), (es, es, 0.6), 'eye', params={'rim': False})
    for s in (-1, 1):
        m.cube('head', (s * 1.4 - 0.5, 3.2, -10.4), (1, 3.4, 1.2), 'fang', rot=(-10, 0, 8 * s), pivot=(s * 1.4, 6, -9.6))
        m.cube('head', (s * 2.9 - 0.6, 4.6, -11.0), (1.2, 2.2, 1.6), 'thorax')                              # chelicerae
        m.cube('head', (s * 1.4 - 0.2, 2.6, -10.6), (0.4, 1.0, 0.4), 'venom')
    # eight legs
    for i in range(8):
        s = 1 if i % 2 == 0 else -1
        row = i // 2
        z = -3.4 + row * 2.8
        up, lo = f'leg{i}', f'leg{i}_lower'
        yaw = (-34 + row * 22) * s
        B(up, 'body', (s * 3.6, 8.4, z), rot=(0, yaw, 0))
        m.cube(up, (s * 3.6 + (0 if s > 0 else -7.6), 7.4, z - 0.9), (7.6, 1.8, 1.8), 'leg', rot=(0, 0, 28 * s), pivot=(s * 3.6, 8.4, z), params={'seed': i})
        B(lo, up, (s * 3.6 + s * 6.6, 12.0, z))
        m.cube(lo, (s * 3.6 + s * 6.6 + (0 if s > 0 else -1.6), 0, z - 0.8), (1.6, 12.4, 1.6), 'leg', rot=(0, 0, 8 * s), pivot=(s * 3.6 + s * 6.6, 12.0, z), params={'seed': 10 + i})
        m.cube(lo, (s * 3.6 + s * 7.2 - 0.6, -0.4, z - 0.6), (1.2, 1.0, 1.2), 'hair')
    return m


# ============================================================================== SPORELING
SPORE_ID = 'geometry.ecr_sporeling'


def sporeling_materials():
    cap = R('#0a3a30', '#106a58', '#1ea080', '#3ad0a0', '#8af0c8')
    spot = R('#d8f0b0', '#eefad0', '#fbffe8')
    gill = R('#c8b890', '#e2d4b0', '#f4ead0')
    stem = R('#8a7a5a', '#b4a47c', '#d8cba4', '#f0e6c4')
    dirt = R('#1a120a', '#2e2014', '#4a3320')
    glow = R('#2a6a08', '#6ad020', '#b8f850', '#f0ffc0')
    dark = R('#040806', '#0a120d', '#141d17')

    def cap_fn(ctx):
        r, g, b, a, gl = P.make(cap, scale=0.4, base=0.5, amp=0.5, bevel=0.1, seed=71)(ctx)
        n = fbm3(ctx.W, 72, 0.55, 2)
        if n > 0.68 and ctx.face != 'down':
            c = ramp_at(spot, 0.4 + (n - 0.68) * 3)
            return (c[0], c[1], c[2], 255, 90)                                   # softly glowing spots
        return (r, g, b, a, gl)

    return {
        'cap': cap_fn, 'gill': P.make(gill, scale=0.8, base=0.5, amp=0.3, bevel=0.1, seed=73, streak=(0, 0.9)),
        'stem': P.make(stem, scale=0.5, base=0.5, amp=0.4, bevel=0.15, seed=74, streak=(1, 0.5)),
        'dirt': P.make(dirt, scale=0.5, base=0.5, amp=0.5, bevel=0.1, seed=75),
        'eye': solid_glow(glow, 0.55, 1.0, 255, 76, rim=False), 'dark': P.make(dark, scale=0.5, base=0.5, amp=0.3, seed=77),
        'spore': solid_glow(glow, 0.3, 0.75, 170, 78, rim=False),
    }


def sporeling():
    m = Model(SPORE_ID, 64, 64, bounds=(1.0, 1.4, (0, 0.6, 0)))
    B = m.bone
    B('root', None, (0, 0, 0))
    B('body', 'root', (0, 5, 0))
    m.cube('body', (-2.6, 5, -1.8), (5.2, 6, 3.6), 'stem', params={'seed': 1})
    m.cube('body', (-2.9, 5.8, -2.1), (5.8, 1.6, 4.2), 'dirt')                                          # dirt-stained belt
    m.cube('body', (-1.2, 8.0, -2.0), (2.4, 2.2, 0.4), 'spore')                                         # glowing pustule
    B('head', 'body', (0, 11, 0))
    m.cube('head', (-3, 11, -3), (6, 4.6, 6), 'stem', params={'seed': 2})
    m.cube('head', (-6.4, 14.2, -6.4), (12.8, 1.4, 12.8), 'gill')                                       # gills (underside of the cap)
    m.cube('head', (-6.0, 15.2, -6.0), (12, 3.2, 12), 'cap', params={'seed': 3})                         # cap
    m.cube('head', (-4.6, 18.2, -4.6), (9.2, 1.8, 9.2), 'cap', params={'seed': 4})
    m.cube('head', (-2.4, 19.8, -2.4), (4.8, 1.2, 4.8), 'cap', params={'seed': 5})
    for s in (-1, 1):
        m.cube('head', (s * 1.5 - 0.9, 12.0, -3.2), (1.8, 1.8, 0.5), 'eye', params={'rim': False})
    m.cube('head', (-1.2, 11.1, -3.2), (2.4, 0.7, 0.4), 'dark')
    def arm(s, tag):
        x = 3.2 * s
        B(f'arm_{tag}', 'body', (x, 10, 0))
        m.cube(f'arm_{tag}', (x - 0.9, 3.4, -0.9), (1.8, 7, 1.8), 'stem', params={'seed': 6 + s})
        m.cube(f'arm_{tag}', (x - 1.3, 2.4, -1.3), (2.6, 1.8, 2.6), 'cap')
    arm(1, 'l'); arm(-1, 'r')
    def leg(s, tag):
        x = 1.3 * s
        B(f'leg_{tag}', 'body', (x, 5, 0))
        m.cube(f'leg_{tag}', (x - 1.1, 0.8, -1.1), (2.2, 4.2, 2.2), 'stem', params={'seed': 9 + s})
        m.cube(f'leg_{tag}', (x - 1.5, 0, -1.9), (3, 1.2, 3.4), 'dirt')
    leg(1, 'l'); leg(-1, 'r')
    return m


MODELS = {
    'gravewalker': (gravewalker, gravewalker_materials, GRAVE_ID),
    'revenant': (revenant, revenant_materials, REV_ID),
    'cave_weaver': (weaver, weaver_materials, WEAVER_ID),
    'sporeling': (sporeling, sporeling_materials, SPORE_ID),
}
