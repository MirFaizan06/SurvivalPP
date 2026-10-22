"""Chapter IV models: Morwen, the Mire Lantern (boss) and the fen's dead - the Mirewalker (zombie-like), the Lanternbone (skeleton-like) and the
Mire Wisp.  Glow channel: lanterns, eyes, wisps, fungus."""
import math
from common import *
from geo import Model, fbm3
import paint as P
from mob_hostiles import solid_glow, R

MORWEN_ID = 'geometry.ecr_mire_lantern'
MIREWALKER_ID = 'geometry.ecr_mirewalker'
LANTERNBONE_ID = 'geometry.ecr_lanternbone'
WISP_ID = 'geometry.ecr_mire_wisp'

MOSS = R('#0c1a0e', '#18331a', '#2a5a2a', '#468a38', '#78b458')
BARK = R('#140c06', '#2c1c0e', '#503418', '#7a5430', '#a07844')
SKIN = R('#56644a', '#76866a', '#98a888', '#bccaa6')
IRON = R('#14141a', '#2a2a32', '#4c4c56', '#7c7c88')
LAMP = R('#6a4e08', '#c89a1c', '#ffd85a', '#fff4b0', '#ffffff')
WISP = R('#2a7a2a', '#6ac850', '#b8f080', '#f0ffc8')
MUD = R('#14100a', '#2a2014', '#4a3a22', '#6e5a38')


def morwen_materials():
    def cloak(ctx):
        r, g, b, a, gl = P.make(MOSS, scale=0.35, base=0.45, amp=0.5, bevel=0.1, seed=501, streak=(1, 0.4))(ctx)
        n = fbm3(ctx.W, 502, 0.45, 3)
        if n > 0.72:                                                    # lichen
            c = ramp_at(MOSS, 0.85 + (n - 0.72))
            return (c[0], c[1], c[2], 255, 0)
        if n < 0.14:                                                    # wet mud at the hem
            c = ramp_at(MUD, 0.5)
            return (c[0], c[1], c[2], 255, 0)
        return (r, g, b, a, gl)

    return {
        'cloak': cloak, 'vine': P.make(MOSS, scale=0.4, base=0.55, amp=0.4, bevel=0.1, seed=503, streak=(1, 0.6)),
        'bark': P.make(BARK, scale=0.4, base=0.5, amp=0.5, bevel=0.2, seed=504, streak=(1, 0.6)),
        'skin': P.make(SKIN, scale=0.5, base=0.55, amp=0.3, bevel=0.1, seed=505),
        'iron': P.make(IRON, scale=0.5, base=0.5, amp=0.4, bevel=0.3, seed=506),
        'dark': P.make(R('#030604', '#090f0a', '#121a14'), scale=0.5, base=0.5, amp=0.3, seed=507),
        'lamp': solid_glow(LAMP, 0.55, 1.0, 255, 508, rim=False), 'eye': solid_glow(LAMP, 0.7, 1.0, 255, 509, rim=False),
        'wisp': solid_glow(WISP, 0.5, 1.0, 255, 510, rim=False),
        'fungus': solid_glow(WISP, 0.3, 0.7, 150, 511, rim=False),
        'chain': P.make(IRON, scale=0.5, base=0.6, amp=0.3, bevel=0.2, seed=512),
    }


def morwen():
    m = Model(MORWEN_ID, 256, 256, bounds=(3.0, 3.6, (0, 1.4, 0)))
    B, C = m.bone, m.cube
    B('root', None, (0, 0, 0))
    B('float', 'root', (0, 0, 0))
    B('body', 'float', (0, 20, 0))
    # hunched torso in a great moss cloak
    C('body', (-4.4, 20.0, -3.0), (8.8, 11.0, 6.0), 'cloak', rot=(8, 0, 0), pivot=(0, 20, 0), params={'seed': 1})
    C('body', (-5.6, 29.4, -3.6), (11.2, 3.0, 7.2), 'cloak', rot=(8, 0, 0), pivot=(0, 20, 0), params={'seed': 2})         # shoulder mantle
    C('body', (-5.0, 8.0, -4.0), (10.0, 13.0, 8.0), 'cloak', params={'seed': 3})
    C('body', (-6.0, 2.0, -4.8), (12.0, 7.0, 9.6), 'cloak', params={'seed': 4})
    for k in range(10):                                                                        # ragged hem strips
        a = k / 10 * math.tau
        x, z = math.sin(a) * 5.6, math.cos(a) * 4.4
        bn = f'hem{k}'
        B(bn, 'body', (x, 3, z))
        C(bn, (x - 1.3, -4.0 + (k % 3) * 1.6, z - 0.6), (2.6, 8.0 - (k % 3) * 1.6, 1.2), 'cloak', params={'seed': 10 + k})
    for k in range(6):                                                                         # hanging vines (sway)
        x = -5.0 + k * 2.0
        bn = f'vine{k}'
        B(bn, 'body', (x, 30, -2.4 + (k % 2) * 4.0))
        C(bn, (x - 0.5, 14.0 - (k % 3) * 3.0, -2.6 + (k % 2) * 4.0), (1.0, 16.0 + (k % 3) * 3.0, 1.0), 'vine', params={'seed': 30 + k})
    # head under a hood of moss, antlers of old branches
    B('head', 'body', (0, 31, -1.5))
    C('head', (-3.0, 31, -4.0), (6.0, 7.0, 6.0), 'skin', params={'seed': 40})
    C('head', (-4.0, 36.4, -5.0), (8.0, 3.6, 8.0), 'cloak', params={'seed': 41})
    C('head', (-4.0, 30.0, -5.0), (1.4, 7.4, 8.0), 'cloak'); C('head', (2.6, 30.0, -5.0), (1.4, 7.4, 8.0), 'cloak')
    C('head', (-4.0, 29.0, 1.6), (8.0, 9.0, 1.6), 'cloak', rot=(-8, 0, 0), pivot=(0, 36, 2))
    C('head', (-1.6, 31.4, -4.2), (3.2, 1.0, 0.5), 'dark')                                      # stitched mouth
    for k in range(3):
        C('head', (-1.2 + k * 1.0, 31.2, -4.35), (0.3, 1.4, 0.3), 'bark')
    for s in (-1, 1):
        C('head', (s * 1.6 - 1.0, 34.0, -4.05), (2.0, 1.6, 0.6), 'dark')
        C('head', (s * 1.6 - 0.6, 34.3, -4.35), (1.2, 1.0, 0.5), 'eye', params={'rim': False})
        for k, (dx, dy, h, rz) in enumerate(((0, 0, 7.0, 14), (1.2, 4.0, 5.0, 40), (0.4, 7.0, 4.4, -10))):                 # antler tines
            C('head', (s * (3.4 + dx) - 0.5, 38.0 + dy, -2.0), (1.0, h, 1.0), 'bark', rot=(0, 0, -rz * s), pivot=(s * (3.4 + dx), 38.0 + dy, -1.5), params={'seed': 50 + k})
    for k in range(4):                                                                         # fungus on the hood
        C('head', (-3.0 + k * 2.0, 39.5, -2.0 + (k % 2) * 3), (1.2, 1.0, 1.2), 'fungus', params={'rim': False})
    # arms
    B('arm_r', 'body', (-5.2, 28, -1.0))
    C('arm_r', (-6.0, 14.0, -1.8), (2.0, 15.0, 2.2), 'skin', params={'seed': 60})
    C('arm_r', (-6.6, 20.0, -2.4), (3.2, 7.0, 3.2), 'cloak', params={'seed': 61})
    C('arm_r', (-6.2, 12.4, -2.0), (2.4, 2.6, 2.4), 'skin')
    B('staff', 'arm_r', (-5.2, 14, -2.0))
    C('staff', (-5.8, -2.0, -2.6), (1.2, 62.0, 1.2), 'bark', params={'seed': 62})                   # a gnarled pole twice her height
    C('staff', (-6.6, 52.0, -2.8), (2.8, 1.0, 1.6), 'bark')
    for k in range(3):
        C('staff', (-6.4 - k * 0.5, 30.0 + k * 8.0, -2.4), (1.0, 5.0, 1.0), 'bark', rot=(0, 0, 40 + k * 10), pivot=(-5.2, 30 + k * 8, -2.0))
    B('lantern', 'staff', (-6.0, 52.0, -2.0))                                                  # the great lantern (swings)
    C('lantern', (-6.5, 50.0, -2.5), (1.0, 3.0, 1.0), 'chain')
    C('lantern', (-9.0, 40.0, -4.5), (6.0, 10.0, 6.0), 'lamp', params={'seed': 63})
    C('lantern', (-9.6, 39.2, -5.1), (7.2, 1.0, 7.2), 'iron'); C('lantern', (-9.6, 49.4, -5.1), (7.2, 1.0, 7.2), 'iron')
    for dx, dz in ((-9.6, -5.1), (-3.4, -5.1), (-9.6, 0.1), (-3.4, 0.1)):
        C('lantern', (dx, 39.2, dz), (0.9, 11.2, 0.9), 'iron')
    C('lantern', (-9.4, 50.4, -4.9), (6.8, 1.4, 6.8), 'iron', params={'seed': 64})
    B('arm_l', 'body', (5.2, 28, -1.0))
    C('arm_l', (4.0, 14.0, -1.8), (2.0, 15.0, 2.2), 'skin', params={'seed': 65})
    C('arm_l', (3.4, 20.0, -2.4), (3.2, 7.0, 3.2), 'cloak', params={'seed': 66})
    C('arm_l', (3.8, 12.4, -2.0), (2.4, 2.6, 2.4), 'skin')
    B('lamp_l', 'arm_l', (5.0, 13, -2.0))                                                      # small hand lantern
    C('lamp_l', (4.2, 6.0, -3.2), (1.6, 6.0, 1.6), 'lamp', params={'seed': 67})
    C('lamp_l', (3.8, 5.6, -3.6), (2.4, 0.8, 2.4), 'iron'); C('lamp_l', (3.8, 12.0, -3.6), (2.4, 0.8, 2.4), 'iron')
    # will-o-wisps circling her
    B('orbit', 'float', (0, 26, 0))
    for k in range(7):
        a = k / 7 * math.tau
        r_ = 11 + (k % 3) * 2.0
        C('orbit', (math.cos(a) * r_ - 1.0, 12 + (k * 3.9) % 26, math.sin(a) * r_ - 1.0), (2.0, 2.0, 2.0), 'wisp', params={'rim': False})
    return m


# ============================================================================== MIREWALKER (zombie-like)
def mirewalker_materials():
    skin = R('#1e2a16', '#34452a', '#566a42', '#7e9462', '#a6bc86')
    mud = R('#100c06', '#241a0e', '#3e2e18', '#5c4626')
    moss = MOSS
    glow = R('#8a6a08', '#d9a820', '#ffe27a', '#ffffff')

    def hide(ctx):
        r, g, b, a, gl = P.make(skin, scale=0.4, base=0.5, amp=0.5, bevel=0.1, seed=521)(ctx)
        n = fbm3(ctx.W, 522, 0.45, 3)
        if n > 0.7:
            c = ramp_at(moss, 0.5 + (n - 0.7) * 2)
            return (c[0], c[1], c[2], 255, 0)
        if n < 0.2:
            c = ramp_at(mud, 0.5)
            return (c[0], c[1], c[2], 255, 0)
        return (r, g, b, a, gl)

    return {
        'hide': hide, 'mud': P.make(mud, scale=0.4, base=0.5, amp=0.5, bevel=0.1, seed=523), 'moss': P.make(moss, scale=0.5, base=0.55, amp=0.4, bevel=0.1, seed=524, streak=(1, 0.5)),
        'reed': P.make(R('#3a4a14', '#5c7424', '#8aa63a', '#b8cc60'), scale=0.5, base=0.55, amp=0.3, bevel=0.1, seed=525, streak=(1, 0.8)),
        'bone': P.make(R('#4a4a30', '#7a7a54', '#a8a878', '#d0d0a4'), scale=0.5, base=0.55, amp=0.3, bevel=0.2, seed=526),
        'dark': P.make(R('#030604', '#090f0a', '#121a14'), scale=0.5, base=0.5, amp=0.3, seed=527),
        'eye': solid_glow(glow, 0.65, 1.0, 255, 528, rim=False), 'fungus': solid_glow(WISP, 0.3, 0.8, 170, 529, rim=False),
    }


def mirewalker():
    m = Model(MIREWALKER_ID, 128, 128, bounds=(1.3, 2.3, (0, 1.1, 0)))
    B, C = m.bone, m.cube
    B('root', None, (0, 0, 0))
    B('body', 'root', (0, 12, 0))
    C('body', (-4.6, 11.0, -2.6), (9.2, 13.0, 5.2), 'hide', params={'seed': 1})                  # bloated torso
    C('body', (-5.0, 10.4, -3.0), (10.0, 5.0, 6.0), 'mud', params={'seed': 2})
    C('body', (-4.2, 20.0, 2.0), (8.4, 4.4, 2.0), 'moss', rot=(-10, 0, 0), pivot=(0, 22, 2), params={'seed': 3})   # moss hump on the back
    for k in range(5):                                                                         # trailing weed from the belt
        bn = f'strip{k}'
        B(bn, 'body', (-4 + k * 2 + 1, 11, -2.9))
        C(bn, (-4 + k * 2, 4.0 - (k % 2) * 1.2, -3.1), (1.8, 7.0 + (k % 2) * 1.2, 0.7), 'moss', params={'seed': 5 + k})
    for k, (x, y) in enumerate(((-3.0, 14.0), (2.6, 17.4))):                                   # glowing fungus growths
        C('body', (x - 0.9, y, -3.4), (1.8, 1.6, 1.0), 'fungus', params={'rim': False})
    B('head', 'body', (0, 24, 0))
    C('head', (-4, 24, -4), (8, 8, 8), 'hide', params={'seed': 12})
    C('head', (-4.4, 30.8, -4.4), (8.8, 2.4, 8.8), 'moss', params={'seed': 13})
    for k, (x, h) in enumerate(((-2.6, 7.0), (-0.6, 9.0), (1.8, 6.0), (3.2, 7.6))):          # reeds growing from the skull
        C('head', (x - 0.4, 32.0, -1.0 + (k % 2) * 2), (0.8, h, 0.8), 'reed', rot=(0, 0, (k - 1.5) * 6), pivot=(x, 32, 0), params={'seed': 14 + k})
    C('head', (-2.2, 24.6, -4.4), (4.4, 1.8, 0.6), 'dark')
    for k in range(4):
        C('head', (-1.8 + k * 1.0, 24.4, -4.6), (0.5, 0.9, 0.4), 'bone')
    for s in (-1, 1):
        C('head', (s * 1.9 - 1.3, 27.2, -4.25), (2.6, 2.0, 0.5), 'dark')
        C('head', (s * 1.9 - 0.8, 27.6, -4.45), (1.6, 1.0, 0.5), 'eye', params={'rim': False})
    # one long arm, one short and swollen
    for s, tag, ln in ((1, 'l', 13.0), (-1, 'r', 10.0)):
        x = 5.6 * s
        B(f'arm_{tag}', 'body', (x, 22, 0))
        C(f'arm_{tag}', (x - 2.0, 22 - ln, -2.0), (4.0, ln, 4.0), 'hide', params={'seed': 20 + s})
        C(f'arm_{tag}', (x - 2.3, 22 - ln, -2.3), (4.6, 3.0, 4.6), 'mud')
        C(f'arm_{tag}', (x - 2.4, 14.5, -2.4), (4.8, 5.0, 4.8), 'moss', params={'seed': 22 + s})
    for s, tag in ((1, 'l'), (-1, 'r')):
        x = 2.2 * s
        B(f'leg_{tag}', 'body', (x, 12, 0))
        C(f'leg_{tag}', (x - 2.2, 0, -2.2), (4.4, 12, 4.4), 'mud', params={'seed': 30 + s})
        C(f'leg_{tag}', (x - 2.5, 7.0, -2.5), (5.0, 3.0, 5.0), 'moss')
        C(f'leg_{tag}', (x - 2.5, 0, -3.2), (5.0, 2.0, 5.6), 'hide')
    return m


# ============================================================================== LANTERNBONE (skeleton-like)
def lanternbone_materials():
    bone = R('#3a4028', '#6a7448', '#9aa46c', '#c8d09c', '#eef2c8')
    rag = MOSS
    glow = LAMP

    def bone_fn(ctx):
        r, g, b, a, gl = P.make(bone, scale=0.5, base=0.55, amp=0.3, bevel=0.2, seed=541)(ctx)
        n = fbm3(ctx.W, 542, 0.5, 2)
        if n > 0.72:
            c = ramp_at(MOSS, 0.6)
            return (c[0], c[1], c[2], 255, 0)
        return (r, g, b, a, gl)

    return {
        'bone': bone_fn, 'rag': P.make(rag, scale=0.4, base=0.5, amp=0.5, bevel=0.1, seed=543, streak=(1, 0.4)),
        'bark': P.make(BARK, scale=0.4, base=0.5, amp=0.5, bevel=0.2, seed=544, streak=(1, 0.6)),
        'iron': P.make(IRON, scale=0.5, base=0.5, amp=0.4, bevel=0.3, seed=545),
        'dark': P.make(R('#030604', '#090f0a', '#121a14'), scale=0.5, base=0.5, amp=0.3, seed=546),
        'eye': solid_glow(glow, 0.65, 1.0, 255, 547, rim=False), 'lamp': solid_glow(glow, 0.55, 1.0, 255, 548, rim=False),
    }


def lanternbone():
    m = Model(LANTERNBONE_ID, 128, 128, bounds=(1.2, 2.6, (0, 1.2, 0)))
    B, C = m.bone, m.cube
    B('root', None, (0, 0, 0))
    B('body', 'root', (0, 12, 0))
    C('body', (-0.9, 12, -0.9), (1.8, 12, 1.8), 'bone')
    for k in range(5):
        w = 7.4 - abs(k - 1.6) * 0.9
        C('body', (-w / 2, 22 - k * 2.2, -2.0), (w, 0.9, 4), 'bone')
    C('body', (-3.4, 10.8, -1.6), (6.8, 2.2, 3.2), 'bone')
    C('body', (-5.4, 20.6, -3.0), (10.8, 4.0, 6.0), 'rag', params={'seed': 2})                    # moss shawl
    C('body', (-5.0, 5.0, 2.4), (10.0, 19.0, 0.9), 'rag', rot=(-4, 0, 0), pivot=(0, 24, 2.4), params={'seed': 3})
    for k in range(5):
        bn = f'rag{k}'
        B(bn, 'body', (-5 + k * 2.5 + 1.25, 12, 3.0))
        C(bn, (-5 + k * 2.5, 0.5 + (k % 2) * 1.5, 2.5), (2.4, 11.5 - (k % 2) * 1.5, 0.8), 'rag', params={'seed': 6 + k})
    B('head', 'body', (0, 24, 0))
    C('head', (-4, 24, -4), (8, 8, 8), 'bone', params={'seed': 11})
    C('head', (-4.5, 29.8, -4.5), (9, 2.6, 9), 'rag', params={'seed': 12})
    C('head', (-0.8, 25.6, -4.4), (1.6, 1.8, 0.5), 'dark')
    C('head', (-2.8, 24.2, -4.3), (5.6, 1.4, 0.6), 'bone')
    for k in range(5):
        C('head', (-2.6 + k * 1.1, 23.9, -4.5), (0.6, 1.0, 0.4), 'bone')
    for s in (-1, 1):
        C('head', (s * 2.0 - 1.2, 27.4, -4.2), (2.4, 2.2, 0.6), 'dark')
        C('head', (s * 2.0 - 0.7, 27.9, -4.45), (1.4, 1.2, 0.5), 'eye', params={'rim': False})
        for k, (dy, h, rz) in enumerate(((0, 6.4, 18), (3.6, 4.4, 48))):                       # branch antlers
            C('head', (s * 3.8 - 0.5, 30.4 + dy, -0.5), (1.0, h, 1.0), 'bark', rot=(0, 0, -rz * s), pivot=(s * 3.8, 30.4 + dy, 0), params={'seed': 14 + k})
    for s, tag in ((1, 'l'), (-1, 'r')):
        x = 5.4 * s
        B(f'arm_{tag}', 'body', (x, 22, 0))
        C(f'arm_{tag}', (x - 1, 12.8, -1), (2, 10, 2), 'bone')
        B(f'forearm_{tag}', f'arm_{tag}', (x, 13, 0))
        C(f'forearm_{tag}', (x - 1, 3.6, -1), (2, 10, 2), 'bone')
        C(f'forearm_{tag}', (x - 1.2, 1.2, -1.2), (2.4, 2.6, 2.4), 'bone')
        if tag == 'r':
            B('staff', f'forearm_{tag}', (x, 3, -2))
            C('staff', (x - 0.6, -10.0, -3.2), (1.2, 30.0, 1.2), 'bark', params={'seed': 20})   # hooked pole
            C('staff', (x - 3.6, 18.0, -3.2), (4.2, 1.2, 1.2), 'bark')
            B('lantern', 'staff', (x - 3.2, 18, -2.6))
            C('lantern', (x - 3.2, 14.0, -3.2), (3.0, 4.2, 3.0), 'lamp', params={'seed': 21})
            C('lantern', (x - 3.4, 18.0, -3.4), (3.4, 0.8, 3.4), 'iron'); C('lantern', (x - 3.4, 13.4, -3.4), (3.4, 0.8, 3.4), 'iron')
    for s, tag in ((1, 'l'), (-1, 'r')):
        x = 2.0 * s
        B(f'leg_{tag}', 'body', (x, 12, 0))
        C(f'leg_{tag}', (x - 1, 6, -1), (2, 6, 2), 'bone')
        B(f'shin_{tag}', f'leg_{tag}', (x, 6, 0))
        C(f'shin_{tag}', (x - 1, 0, -1), (2, 6, 2), 'bone')
        C(f'shin_{tag}', (x - 1.4, 0, -2.2), (2.8, 1.2, 4.0), 'rag')
    return m


# ============================================================================== MIRE WISP
def wisp_materials():
    return {
        'core': solid_glow(WISP, 0.7, 1.0, 255, 561, rim=False), 'halo': solid_glow(WISP, 0.4, 0.8, 200, 562, rim=False),
        'tail': solid_glow(WISP, 0.3, 0.6, 140, 563, rim=False), 'eye': solid_glow(LAMP, 0.7, 1.0, 255, 564, rim=False),
    }


def wisp():
    m = Model(WISP_ID, 64, 64, bounds=(1.0, 1.2, (0, 0.5, 0)))
    B, C = m.bone, m.cube
    DY = 6.0
    B('root', None, (0, 0, 0))
    B('body', 'root', (0, 8 + DY, 0))
    m.cube('body', (-2.5, 5.5 + DY, -2.5), (5.0, 5.0, 5.0), 'core')
    for k in range(4):
        a = k / 4 * math.tau + 0.4
        m.cube('body', (math.cos(a) * 3.6 - 1.0, 6.5 + DY, math.sin(a) * 3.6 - 1.0), (2.0, 2.0, 2.0), 'halo')
    m.cube('body', (-2.9, 6.8 + DY, -2.65), (1.6, 1.2, 0.3), 'eye'); m.cube('body', (1.3, 6.8 + DY, -2.65), (1.6, 1.2, 0.3), 'eye')
    for k in range(3):
        bn = f'tail{k}'
        B(bn, 'body' if k == 0 else f'tail{k - 1}', (0, 5.5 - k * 2.6 + DY, 0.5))
        m.cube(bn, (-1.2 + k * 0.2, 3.0 - k * 2.6 + DY, -0.7), (2.4 - k * 0.6, 2.8, 1.4), 'tail')
    return m


MODELS = {
    'mire_lantern': (morwen, morwen_materials, MORWEN_ID),
    'mirewalker': (mirewalker, mirewalker_materials, MIREWALKER_ID),
    'lanternbone': (lanternbone, lanternbone_materials, LANTERNBONE_ID),
    'mire_wisp': (wisp, wisp_materials, WISP_ID),
}
