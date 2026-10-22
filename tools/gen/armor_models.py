"""Bespoke 3D armour for every tier: one geometry + painted texture per piece (no more recoloured vanilla layers).
Bones use the player skeleton names (head, body, rightArm, leftArm, rightLeg, leftLeg) so the pieces attach to the wearer."""
import math
from common import *
from geo import Model, fbm3
import paint as P
from mob_hostiles import solid_glow, R

PIECES = ('helmet', 'chestplate', 'leggings', 'boots')
BOUNDS = (2.2, 2.4, (0, 1.0, 0))


def armor_id(mat, piece):
    return f'geometry.ecr_armor_{mat}_{piece}'


def shade(base, k):
    def fn(ctx):
        r, g, b, a, gl = base(ctx)
        return (min(255, int(r * k)), min(255, int(g * k)), min(255, int(b * k)), a, gl)
    return fn


# ============================================================================== shared base volumes
def base_volumes(m, piece, mat, infl_chest=0.55, infl_legs=0.3, infl_boots=0.45):
    B = m.bone
    if piece == 'helmet':
        B('head', None, (0, 24, 0))
        m.cube('head', (-4, 24, -4), (8, 8, 8), mat, inflate=infl_chest, params={'seed': 1})
    elif piece == 'chestplate':
        B('body', None, (0, 24, 0)); B('rightArm', None, (-5, 22, 0)); B('leftArm', None, (5, 22, 0))
        m.cube('body', (-4, 12, -2), (8, 12, 4), mat, inflate=infl_chest, params={'seed': 2})
        m.cube('rightArm', (-8, 12, -2), (4, 12, 4), mat, inflate=infl_chest * 0.8, params={'seed': 3})
        m.cube('leftArm', (4, 12, -2), (4, 12, 4), mat, inflate=infl_chest * 0.8, params={'seed': 4})
    elif piece == 'leggings':
        B('body', None, (0, 24, 0)); B('rightLeg', None, (-1.9, 12, 0)); B('leftLeg', None, (1.9, 12, 0))
        m.cube('body', (-4, 12, -2), (8, 5, 4), mat, inflate=infl_legs, params={'seed': 5})
        m.cube('rightLeg', (-3.9, 5, -2), (4, 7, 4), mat, inflate=infl_legs, params={'seed': 6})
        m.cube('leftLeg', (-0.1, 5, -2), (4, 7, 4), mat, inflate=infl_legs, params={'seed': 7})
    else:
        B('rightLeg', None, (-1.9, 12, 0)); B('leftLeg', None, (1.9, 12, 0))
        m.cube('rightLeg', (-3.9, 0, -2), (4, 5, 4), mat, inflate=infl_boots, params={'seed': 8})
        m.cube('leftLeg', (-0.1, 0, -2), (4, 5, 4), mat, inflate=infl_boots, params={'seed': 9})


# ============================================================================== AZURITE  (faceted crystal plate)
def azurite_materials():
    az = AZURITE
    steel = R('#2a3440', '#4a5a6c', '#7a8fa6', '#b4c6d8', '#eaf4ff')
    gem = R('#0a5a8a', '#12a0d8', '#5ae0ff', '#d0fbff')
    cloth = R('#0e2236', '#18405e', '#256688', '#3a8ab0')

    def facet(ctx):
        r, g, b, a, gl = P.make(az, scale=0.35, base=0.48, amp=0.3, bevel=0.2, seed=201)(ctx)
        n = fbm3(ctx.W, 202, 0.45, 2)
        if abs(n - 0.5) < 0.03:                                           # light facet seams
            c = ramp_at(az, 0.95)
            return (c[0], c[1], c[2], 255, 0)
        return (r, g, b, a, gl)
    return {'plate': facet, 'steel': P.make(steel, scale=0.5, base=0.55, amp=0.35, bevel=0.25, seed=203),
            'gem': solid_glow(gem, 0.45, 1.0, 255, 204, rim=True), 'cloth': P.make(cloth, scale=0.5, base=0.5, amp=0.4, bevel=0.1, seed=205, streak=(1, 0.4))}


def azurite(m, piece):
    base_volumes(m, piece, 'plate')
    C = m.cube
    if piece == 'helmet':
        for k, (x, h, rz, rx) in enumerate(((0, 6, 0, 0), (-2.2, 4.4, 20, -6), (2.2, 4.4, -20, -6), (-3.2, 3.2, 38, -12), (3.2, 3.2, -38, -12))):
            C('head', (x - 0.8, 32.2, -1.2 - k * 0.1), (1.6, h, 1.6), 'plate', rot=(rx, 0, rz), pivot=(x, 32.2, -0.4), params={'seed': 10 + k})
        for k, (x, rz) in enumerate(((-2.6, 24), (2.6, -24))):
            C('head', (x - 0.7, 32.0, 2.2), (1.4, 4.0, 1.4), 'plate', rot=(18, 0, rz), pivot=(x, 32, 2.8), params={'seed': 20 + k})
        for s in (-1, 1):
            C('head', (s * 4.55 - 0.4, 24.4, -2.4), (0.8, 4.6, 4.8), 'steel', params={'seed': 30})           # cheek guard
        C('head', (-4.5, 29.4, -4.7), (9, 1.0, 1.0), 'steel')                                              # brow band
        C('head', (-0.9, 29.8, -5.0), (1.8, 1.8, 0.8), 'gem')                                              # forehead gem
    elif piece == 'chestplate':
        C('body', (-4.2, 22.4, -2.5), (8.4, 1.6, 5.0), 'steel')                                            # collar
        for k in range(3):
            C('body', (-4.2, 13 + k * 3.2, -2.6), (8.4, 0.8, 0.7), 'steel')                                # banding
        C('body', (-1.6, 16.4, -3.1), (3.2, 4.2, 1.0), 'gem', rot=(0, 0, 0))                               # chest gem
        C('body', (-1.0, 17.0, -3.4), (2.0, 3.0, 0.5), 'steel')
        C('body', (-3.8, 12.2, 2.0), (7.6, 11.0, 1.0), 'plate', inflate=0.3, params={'seed': 40})          # back plate
        for s, bn in ((-1, 'rightArm'), (1, 'leftArm')):
            x = s * 6.0
            for k, (dx, h, rz) in enumerate(((0, 5.4, 12 * s), (-1.8 * s, 4.0, 30 * s), (1.8 * s, 4.2, -4 * s))):
                C(bn, (x + dx - 0.9, 22.6, -0.9), (1.8, h, 1.8), 'plate', rot=(0, 0, -rz), pivot=(x + dx, 22.6, 0), params={'seed': 50 + k})
            C(bn, (x - 2.6, 21.2, -2.6), (5.2, 1.0, 5.2), 'steel')                                         # shoulder ring
            C(bn, (x - 2.5, 12.2, -2.5), (5.0, 1.2, 5.0), 'steel')                                         # cuff
    elif piece == 'leggings':
        C('body', (-4.3, 15.6, -2.5), (8.6, 1.4, 5.0), 'steel')                                            # belt
        C('body', (-1.0, 15.6, -3.1), (2.0, 1.6, 0.8), 'gem')
        for s, bn in ((-1, 'rightLeg'), (1, 'leftLeg')):
            x = s * 1.9
            C(bn, (x - 1.0, 6.0, -3.0), (2.0, 3.4, 1.2), 'plate', rot=(24, 0, 0), pivot=(x, 7, -2.4), params={'seed': 60})   # knee crystal
            C(bn, (x - 2.4, 11.0, -2.4), (4.8, 1.0, 4.8), 'steel')
    else:
        for s, bn in ((-1, 'rightLeg'), (1, 'leftLeg')):
            x = s * 1.9
            C(bn, (x - 2.5, 0.6, -2.5), (5.0, 1.0, 5.0), 'steel')
            C(bn, (x + s * 2.2 - 0.5, 0.8, -0.8), (1.0, 4.0, 1.6), 'plate', rot=(0, 0, 14 * s), pivot=(x + s * 2.2, 1, 0), params={'seed': 70})   # side fin
            C(bn, (x - 1.2, 0.4, -3.2), (2.4, 1.6, 1.4), 'plate', params={'seed': 71})                     # toe cap


# ============================================================================== PYRELITE  (infernal horned plate)
def pyrelite_materials():
    py = PYRELITE
    obsidian = R('#0a0608', '#1a0e12', '#2e1a20', '#46282e', '#663a40')
    ember = R('#7a1d00', '#c8400c', '#ff8a24', '#ffd35e', '#fff2b0')
    horn = R('#2a1a14', '#4a3224', '#7a5a42', '#b0906a', '#e0c9a0')

    def molten(ctx):
        r, g, b, a, gl = P.make(py, scale=0.35, base=0.3, amp=0.32, bevel=0.2, seed=211)(ctx)
        n = fbm3(ctx.W, 212, 0.25, 3)
        if abs(n - 0.5) < 0.028:                                          # glowing cracks
            c = ramp_at(ember, 0.7 + 0.3 * fbm3(ctx.W, 213, 0.6, 2))
            return (c[0], c[1], c[2], 255, 0)
        return (r, g, b, a, gl)
    return {'plate': molten, 'obsidian': P.make(obsidian, scale=0.4, base=0.5, amp=0.5, bevel=0.2, seed=214),
            'ember': solid_glow(ember, 0.55, 1.0, 255, 215, rim=False), 'horn': P.make(horn, scale=0.5, base=0.5, amp=0.4, bevel=0.2, seed=216, streak=(1, 0.5))}


def pyrelite(m, piece):
    base_volumes(m, piece, 'plate')
    C = m.cube
    if piece == 'helmet':
        for s in (-1, 1):
            C('head', (s * 3.6 - 0.8, 31.6, -0.8), (1.6, 3.2, 1.6), 'horn', rot=(0, 0, -22 * s), pivot=(s * 3.6, 31.6, 0), params={'seed': 11})
            C('head', (s * 5.6 - 0.6, 34.2, -0.6), (1.2, 3.4, 1.2), 'horn', rot=(-8, 0, -48 * s), pivot=(s * 5.6, 34.2, 0), params={'seed': 12})
            C('head', (s * 7.6 - 0.4, 36.4, -1.0), (0.8, 2.8, 0.8), 'horn', rot=(-14, 0, -74 * s), pivot=(s * 7.6, 36.4, -0.4), params={'seed': 13})
            C('head', (s * 4.5 - 0.4, 24.4, -3.0), (0.8, 4.0, 5.0), 'obsidian')
        C('head', (-4.6, 27.2, -4.8), (9.2, 1.6, 1.0), 'obsidian')
        C('head', (-3.6, 27.5, -5.1), (7.2, 0.9, 0.6), 'ember')                                           # glowing visor slit
        C('head', (-1.2, 24.2, -4.8), (2.4, 2.4, 1.0), 'obsidian')                                        # mouth guard
        C('head', (-0.8, 32.6, -3.0), (1.6, 1.6, 6.0), 'obsidian')                                        # crest ridge
    elif piece == 'chestplate':
        C('body', (-4.2, 22.6, -2.5), (8.4, 1.4, 5.0), 'obsidian')
        C('body', (-1.5, 15.0, -2.9), (3.0, 6.0, 0.8), 'ember')                                            # furnace core
        C('body', (-2.0, 14.6, -2.7), (4.0, 6.8, 0.5), 'obsidian')
        for k in range(3):
            C('body', (-4.2, 13.2 + k * 3.0, -2.6), (2.0, 0.7, 0.6), 'obsidian'); C('body', (2.2, 13.2 + k * 3.0, -2.6), (2.0, 0.7, 0.6), 'obsidian')
        C('body', (-3.8, 12.2, 2.0), (7.6, 11.0, 1.0), 'plate', inflate=0.3, params={'seed': 41})
        for k in range(3):
            C('body', (-3.0 + k * 3.0 - 0.6, 18.0, 3.0), (1.2, 4.0, 0.6), 'ember')                         # back vents
        for s, bn in ((-1, 'rightArm'), (1, 'leftArm')):
            x = s * 6.0
            C(bn, (x - 3.0, 22.0, -3.0), (6.0, 2.2, 6.0), 'obsidian', rot=(0, 0, -8 * s), pivot=(x, 22, 0))
            for k, (dx, h, rz) in enumerate(((0, 6.0, 20 * s), (-2.0 * s, 4.4, 50 * s), (2.0 * s, 4.0, -4 * s))):
                C(bn, (x + dx - 0.8, 23.6, -0.8), (1.6, h, 1.6), 'horn', rot=(0, 0, -rz), pivot=(x + dx, 23.6, 0), params={'seed': 51 + k})
            C(bn, (x - 2.6, 12.2, -2.6), (5.2, 1.6, 5.2), 'obsidian')
    elif piece == 'leggings':
        C('body', (-4.3, 15.6, -2.5), (8.6, 1.4, 5.0), 'obsidian')
        C('body', (-1.2, 12.4, -2.8), (2.4, 3.6, 0.8), 'ember')
        for s, bn in ((-1, 'rightLeg'), (1, 'leftLeg')):
            x = s * 1.9
            C(bn, (x - 2.0, 7.0, -3.0), (4.0, 6.0, 0.9), 'plate', rot=(-14, 0, 0), pivot=(x, 13, -2.4), params={'seed': 61})   # flame tasset
            C(bn, (x - 0.8, 5.6, -3.4), (1.6, 3.0, 1.6), 'horn', rot=(30, 0, 0), pivot=(x, 8, -2.4), params={'seed': 62})        # knee spike
    else:
        for s, bn in ((-1, 'rightLeg'), (1, 'leftLeg')):
            x = s * 1.9
            C(bn, (x - 2.5, 0.0, -2.5), (5.0, 1.0, 5.4), 'obsidian')
            for k in (-1, 0, 1):
                C(bn, (x + k * 1.3 - 0.45, 0.0, -4.4), (0.9, 0.9, 2.6), 'horn', params={'seed': 71})        # claws
            C(bn, (x - 0.6, 1.0, 2.0), (1.2, 3.2, 1.4), 'horn', rot=(-25, 0, 0), pivot=(x, 1, 2.4), params={'seed': 72})        # heel spur
            C(bn, (x - 0.15, 3.4, -2.55), (0.3, 1.2, 0.6), 'ember')


# ============================================================================== ECLIPSITE  (void armour with shards + halo)
def eclipsite_materials():
    ec = ECLIPSITE
    void = R('#03010a', '#0a0420', '#14083a', '#201058', '#2f1c80')
    rune = R('#2a1070', '#6a3ad0', '#b07aff', '#e8d8ff')
    cyan = R('#0a5a6a', '#20b0c8', '#7af0ff', '#e8ffff')

    def voidplate(ctx):
        r, g, b, a, gl = P.make(void, scale=0.35, base=0.45, amp=0.5, bevel=0.22, seed=221)(ctx)
        n = fbm3(ctx.W, 222, 0.3, 3)
        if abs(n - 0.5) < 0.018:
            c = ramp_at(rune, 0.6 + 0.35 * fbm3(ctx.W, 223, 0.7, 2))
            return (c[0], c[1], c[2], 255, 0)
        return (r, g, b, a, gl)

    def shard(ctx):
        n = fbm3(ctx.W, 224, 0.4, 2)
        c = ramp_at(ec, min(1.0, 0.4 + 0.55 * n))
        d, side = ctx.edge
        if d < 1:
            c = tuple(int(v * 0.7) for v in c)
        return (c[0], c[1], c[2], 255, 0)
    return {'plate': voidplate, 'shard': shard, 'rune': solid_glow(rune, 0.5, 1.0, 255, 225, rim=False),
            'eye': solid_glow(cyan, 0.6, 1.0, 255, 226, rim=False), 'trim': P.make(ec, scale=0.45, base=0.55, amp=0.4, bevel=0.25, seed=227)}


def eclipsite(m, piece):
    base_volumes(m, piece, 'plate')
    C = m.cube
    if piece == 'helmet':
        for k in range(8):                                                                         # floating halo
            a = k / 8 * math.tau
            C('head', (math.cos(a) * 5.4 - 0.9, 34.6, math.sin(a) * 5.4 - 0.9), (1.8, 0.7, 1.8), 'rune', rot=(0, -math.degrees(a), 0), pivot=(math.cos(a) * 5.4, 34.6, math.sin(a) * 5.4))
        for k, (h, rx, y) in enumerate(((7.0, 28, 30.0), (5.6, 40, 31.0), (4.2, 52, 32.0))):         # back-swept crest
            C('head', (-0.8, y, 2.0 + k * 1.2), (1.6, h, 1.4), 'trim', rot=(rx, 0, 0), pivot=(0, y, 2.4 + k), params={'seed': 11 + k})
        for s in (-1, 1):
            C('head', (s * 4.6 - 0.4, 24.0, -3.4), (0.8, 6.0, 6.0), 'plate')
            C('head', (s * 2.0 - 1.0, 28.0, -4.9), (2.0, 0.8, 0.7), 'eye')
            C('head', (s * 5.2 - 0.6, 28.6, 1.4), (1.2, 4.4, 1.2), 'shard', rot=(14, 0, -28 * s), pivot=(s * 5.2, 28.6, 1.4), params={'seed': 21})
        C('head', (-4.6, 29.2, -4.8), (9.2, 1.2, 1.0), 'trim')
    elif piece == 'chestplate':
        C('body', (-4.2, 22.6, -2.5), (8.4, 1.6, 5.0), 'trim')
        C('body', (-1.4, 16.0, -3.0), (2.8, 4.6, 0.9), 'rune')
        C('body', (-0.5, 12.8, -2.9), (1.0, 8.6, 0.6), 'rune')
        for k in range(2):
            C('body', (-4.2, 13.6 + k * 4.4, -2.6), (8.4, 0.7, 0.6), 'trim')
        C('body', (-4.2, 0.0, 2.2), (8.4, 22.0, 0.8), 'plate', params={'seed': 41})                # long flowing back plate
        C('body', (-1.0, 12.0, 3.0), (2.0, 11.0, 0.6), 'rune')
        for s, bn in ((-1, 'rightArm'), (1, 'leftArm')):
            x = s * 6.0
            for k, (dx, h, rz, dy) in enumerate(((0, 7.0, 10 * s, 0), (-2.4 * s, 5.0, 36 * s, 0.6), (2.4 * s, 4.6, -18 * s, 0.2))):
                C(bn, (x + dx - 0.9, 23.0 + dy, -0.9), (1.8, h, 1.8), 'shard', rot=(0, 0, -rz), pivot=(x + dx, 23.0, 0), params={'seed': 51 + k})
            C(bn, (x - 2.8, 21.6, -2.8), (5.6, 1.2, 5.6), 'trim')
            C(bn, (x - 2.5, 12.2, -2.5), (5.0, 1.0, 5.0), 'trim')
    elif piece == 'leggings':
        C('body', (-4.3, 15.6, -2.5), (8.6, 1.4, 5.0), 'trim')
        C('body', (-1.0, 15.6, -3.1), (2.0, 1.4, 0.7), 'rune')
        for s, bn in ((-1, 'rightLeg'), (1, 'leftLeg')):
            x = s * 1.9
            C(bn, (x - 1.8, 3.0, -2.9), (3.6, 10.0, 0.8), 'plate', rot=(-6, 0, 0), pivot=(x, 13, -2.4), params={'seed': 61})  # long tasset
            C(bn, (x - 0.6, 7.0, -3.3), (1.2, 4.0, 0.5), 'rune')
            C(bn, (x - 0.9, 5.4, -3.6), (1.8, 2.6, 1.6), 'shard', rot=(26, 0, 0), pivot=(x, 8, -2.4), params={'seed': 62})
    else:
        for s, bn in ((-1, 'rightLeg'), (1, 'leftLeg')):
            x = s * 1.9
            C(bn, (x - 2.5, 0.0, -2.5), (5.0, 0.9, 5.0), 'trim')
            for k, (dz, rx, h) in enumerate(((1.6, -18, 5.0), (2.8, -32, 4.0), (0.4, -6, 4.4))):
                C(bn, (x + s * 2.7 - 0.3, 1.0, dz - 0.7), (0.6, h, 1.4), 'shard', rot=(rx, 0, 18 * s), pivot=(x + s * 2.7, 1.5, dz), params={'seed': 70 + k})   # winged fins
            C(bn, (x - 0.5, 3.4, -2.6), (1.0, 1.0, 0.5), 'rune')


# ============================================================================== SAKURA  (the Veiled Blossom's regalia)
SAKURA = [hx(c) for c in ('#6a2448', '#a8466f', '#dc7aa4', '#f6a8c8', '#ffd2e4', '#fff0f6')]


def sakura_materials():
    cream = R('#a89080', '#d2baa6', '#ecdccb', '#fff6ec')
    gold = R('#6a4a0a', '#a8781a', '#d9a830', '#f7d466', '#fff0a8')
    obi = R('#3a0e22', '#6a1a3e', '#a02a5e', '#d04a84')
    ink = R('#14061a', '#26102e', '#3c1c48', '#58306a')
    glow = R('#a0406a', '#f070a8', '#ffb0d0', '#ffffff')

    def kimono(ctx):
        r, g, b, a, gl = P.make(SAKURA, scale=0.5, base=0.62, amp=0.3, bevel=0.15, seed=231, streak=(1, 0.35))(ctx)
        n = fbm3(ctx.W, 232, 0.9, 2)
        if n > 0.74:                                                       # scattered petal prints
            c = ramp_at(cream, 0.8)
            return (c[0], c[1], c[2], 255, 0)
        return (r, g, b, a, gl)
    return {'plate': kimono, 'petal': P.make(SAKURA, scale=0.6, base=0.7, amp=0.25, bevel=0.2, seed=233),
            'cream': P.make(cream, scale=0.5, base=0.6, amp=0.25, bevel=0.15, seed=234), 'gold': P.make(gold, scale=0.5, base=0.55, amp=0.4, bevel=0.3, seed=235),
            'obi': P.make(obi, scale=0.45, base=0.5, amp=0.4, bevel=0.15, seed=236, streak=(1, 0.5)), 'ink': P.make(ink, scale=0.5, base=0.5, amp=0.3, seed=237),
            'gem': solid_glow(glow, 0.5, 1.0, 255, 238, rim=True)}


def sakura(m, piece):
    base_volumes(m, piece, 'plate', infl_chest=0.5)
    C = m.cube
    if piece == 'helmet':
        for k, rz in enumerate((-62, -31, 0, 31, 62)):                                              # kanzashi fan of petals
            C('head', (-1.4, 32.6, 1.4), (2.8, 4.6, 0.5), 'petal', rot=(-14, 0, rz), pivot=(0, 32.2, 1.6), params={'seed': 10 + k})
        for s in (-1, 1):
            C('head', (s * 4.2 - 1.2, 29.2, 0.4), (2.4, 2.4, 2.4), 'ink', params={'seed': 20})         # hair buns
            C('head', (s * 4.2 - 0.6, 30.4, 0.6), (1.2, 1.2, 1.2), 'gold')
            C('head', (s * 4.5 - 0.2, 23.0, -3.4), (0.4, 3.6, 0.4), 'ink')                              # side locks
            C('head', (s * 2.0 - 0.2, 24.0, -4.9), (0.4, 5.0, 0.4), 'gold')                             # hanging bead strands
            C('head', (s * 2.0 - 0.45, 23.4, -4.95), (0.9, 0.9, 0.9), 'gem')
        C('head', (-4.6, 31.4, -4.7), (9.2, 1.2, 9.4), 'gold')                                       # circlet
        C('head', (-1.0, 30.8, -5.1), (2.0, 2.2, 0.8), 'gem')
        C('head', (-4.2, 22.0, 3.2), (8.4, 9.0, 1.0), 'ink', params={'seed': 21})                    # long hair behind
    elif piece == 'chestplate':
        C('body', (-4.2, 22.4, -2.6), (8.4, 1.8, 5.2), 'cream')                                      # layered collar
        C('body', (-1.2, 20.6, -2.9), (2.4, 2.4, 0.6), 'cream', rot=(0, 0, 45))
        C('body', (-4.4, 14.0, -2.7), (8.8, 3.4, 5.4), 'obi', params={'seed': 40})                    # obi sash
        C('body', (-1.2, 14.4, -3.3), (2.4, 2.6, 0.8), 'gold')
        C('body', (-3.0, 15.0, 2.6), (3.0, 3.0, 1.2), 'obi', rot=(0, 0, 32), pivot=(-1.5, 16.5, 3.0))   # obi bow loops
        C('body', (0.0, 15.0, 2.6), (3.0, 3.0, 1.2), 'obi', rot=(0, 0, -32), pivot=(1.5, 16.5, 3.0))
        C('body', (-1.0, 8.0, 3.0), (2.0, 8.0, 0.6), 'obi', rot=(6, 0, 0), pivot=(0, 15, 3.0))           # sash tails
        C('body', (-3.8, 12.2, 2.0), (7.6, 11.0, 1.0), 'plate', inflate=0.2, params={'seed': 41})
        for s, bn in ((-1, 'rightArm'), (1, 'leftArm')):
            x = s * 6.0
            C(bn, (x - 2.6, 21.0, -2.6), (5.2, 2.0, 5.2), 'petal', params={'seed': 50})              # petal pauldron
            C(bn, (x - 2.0, 22.4, -2.0), (4.0, 1.2, 4.0), 'petal', params={'seed': 51})
            C(bn, (x + s * 2.4 - 0.4, 2.0, -3.0), (0.8, 12.0, 6.0), 'plate', rot=(0, 0, -4 * s), pivot=(x + s * 2.4, 14, 0), params={'seed': 52})   # furisode sleeve
            C(bn, (x + s * 2.4 - 0.45, 1.6, -3.2), (0.9, 0.8, 6.4), 'gold')
    elif piece == 'leggings':
        C('body', (-4.3, 15.4, -2.5), (8.6, 1.6, 5.0), 'obi')
        for s, bn in ((-1, 'rightLeg'), (1, 'leftLeg')):
            x = s * 1.9
            C(bn, (x - 2.2, 3.0, -3.0), (4.4, 10.0, 0.8), 'plate', rot=(-5, 0, 0), pivot=(x, 13, -2.4), params={'seed': 61})   # hakama front pleat
            C(bn, (x + s * 2.0 - 0.4, 3.4, -2.2), (0.8, 9.0, 4.4), 'plate', rot=(0, 0, -6 * s), pivot=(x + s * 2.0, 13, 0), params={'seed': 62})
            C(bn, (x - 2.2, 2.6, 2.2), (4.4, 10.0, 0.8), 'plate', rot=(5, 0, 0), pivot=(x, 13, 2.4), params={'seed': 63})
            C(bn, (x - 2.3, 2.4, -3.1), (4.6, 0.7, 1.0), 'gold')
    else:
        for s, bn in ((-1, 'rightLeg'), (1, 'leftLeg')):
            x = s * 1.9
            C(bn, (x - 2.4, 0.0, -2.8), (4.8, 1.2, 5.6), 'gold')                                    # raised geta sole
            for k, (dz, rz) in enumerate(((-1.0, 24), (0.8, 0), (2.6, -24))):
                C(bn, (x + s * 2.7 - 0.2, 1.4, dz - 0.9), (0.4, 3.2, 1.8), 'petal', rot=(0, 0, rz * s), pivot=(x + s * 2.7, 1.4, dz), params={'seed': 70 + k})   # ankle petals
            C(bn, (x - 0.6, 3.6, -2.8), (1.2, 1.2, 0.8), 'gem')
            C(bn, (x - 2.3, 4.2, -2.4), (4.6, 0.8, 4.8), 'cream')



# ============================================================================== RIMESTEEL  (iron replica: riveted nordic plate, fur, frost)
RIMESTEEL = [hx(c) for c in ('#0e1622', '#26384c', '#4a6a88', '#86a8c4', '#c2dcee', '#f0f8ff', '#ffffff')]


def rimesteel_materials():
    fur = R('#22201c', '#3e382e', '#625848', '#8a7e68')
    ice = R('#3c6a90', '#6aa0c8', '#a8d0ec', '#e2f4ff')
    leather = R('#1a120c', '#32231a', '#523a28', '#76563c')

    def plate(ctx):
        r, g, b, a, gl = P.make(RIMESTEEL, scale=0.4, base=0.5, amp=0.3, bevel=0.22, seed=251, streak=(1, 0.35))(ctx)
        n = fbm3(ctx.W, 252, 0.5, 3)
        if n > 0.78:                                                       # frost creeping over the steel
            c = ramp_at(ice, 0.55 + (n - 0.78) * 2)
            return (c[0], c[1], c[2], 255, 0)
        return (r, g, b, a, gl)
    return {'plate': plate, 'steel': P.make(RIMESTEEL, scale=0.5, base=0.62, amp=0.3, bevel=0.3, seed=253),
            'fur': P.make(fur, scale=0.4, base=0.5, amp=0.5, bevel=0.1, seed=254, streak=(1, 0.4)),
            'leather': P.make(leather, scale=0.5, base=0.5, amp=0.4, bevel=0.15, seed=255, streak=(1, 0.6)),
            'ice': P.make(ice, scale=0.4, base=0.7, amp=0.25, bevel=0.2, seed=256, glow_fn=lambda ctx, n, c: (c, 40)),
            'rivet': P.make(R('#4a5260', '#8a96a8', '#c4ccd8', '#ffffff'), scale=0.5, base=0.7, amp=0.2, bevel=0.4, seed=257)}


def rimesteel(m, piece):
    base_volumes(m, piece, 'plate', infl_chest=0.45)
    C = m.cube
    if piece == 'helmet':
        C('head', (-4.6, 29.4, -4.7), (9.2, 1.4, 9.4), 'steel')                                              # brow band
        C('head', (-0.7, 24.6, -4.9), (1.4, 5.6, 0.9), 'steel')                                             # nasal guard
        for s in (-1, 1):
            C('head', (s * 4.5 - 0.4, 24.0, -3.0), (0.8, 5.4, 5.6), 'steel')                                 # cheek plates
            C('head', (s * 3.8 - 0.9, 31.4, -1.0), (1.8, 3.6, 1.8), 'ice', rot=(0, 0, -26 * s), pivot=(s * 3.8, 31.4, 0), params={'seed': 11})   # ice horns
            C('head', (s * 2.4 - 0.4, 30.2, -4.9), (0.8, 0.8, 0.4), 'rivet')
        C('head', (-4.7, 23.6, 3.0), (9.4, 4.2, 1.8), 'fur', params={'seed': 12})                            # fur neck mantle
        C('head', (-0.8, 31.2, -3.0), (1.6, 1.8, 6.0), 'fur', params={'seed': 13})                           # fur crest
    elif piece == 'chestplate':
        C('body', (-5.0, 22.2, -3.0), (10.0, 2.4, 6.0), 'fur', params={'seed': 20})                          # fur collar
        C('body', (-4.2, 15.4, -2.6), (8.4, 1.4, 5.2), 'leather')                                            # belt
        C('body', (-1.0, 15.2, -2.9), (2.0, 1.8, 0.6), 'steel')
        for k in range(3):
            C('body', (-3.4 + k * 3.4, 19.0, -2.55), (0.9, 0.9, 0.4), 'rivet')
        C('body', (-0.5, 16.8, -2.6), (1.0, 5.6, 0.4), 'steel')                                              # central ridge
        C('body', (-3.8, 12.2, 2.0), (7.6, 11.0, 1.0), 'plate', inflate=0.25, params={'seed': 21})
        for s, bn in ((-1, 'rightArm'), (1, 'leftArm')):
            x = s * 6.0
            C(bn, (x - 2.8, 21.2, -2.8), (5.6, 1.6, 5.6), 'steel')                                           # pauldron
            C(bn, (x - 2.6, 22.6, -2.6), (5.2, 1.0, 5.2), 'fur', params={'seed': 22})
            C(bn, (x - 0.8, 23.4, -0.8), (1.6, 3.2, 1.6), 'ice', rot=(0, 0, -18 * s), pivot=(x, 23.4, 0), params={'seed': 23})
            C(bn, (x - 2.5, 12.2, -2.5), (5.0, 2.0, 5.0), 'fur', params={'seed': 24})                        # fur cuff
    elif piece == 'leggings':
        C('body', (-4.3, 15.6, -2.5), (8.6, 1.4, 5.0), 'leather')
        for s, bn in ((-1, 'rightLeg'), (1, 'leftLeg')):
            x = s * 1.9
            C(bn, (x - 1.9, 6.0, -2.9), (3.8, 6.4, 0.8), 'plate', rot=(-6, 0, 0), pivot=(x, 13, -2.4), params={'seed': 30})   # tasset
            C(bn, (x - 1.1, 5.2, -3.3), (2.2, 2.2, 1.2), 'steel')                                            # knee
            C(bn, (x - 2.2, 4.4, -2.2), (4.4, 1.4, 4.4), 'fur', params={'seed': 31})
    else:
        for s, bn in ((-1, 'rightLeg'), (1, 'leftLeg')):
            x = s * 1.9
            C(bn, (x - 2.5, 0.0, -2.5), (5.0, 1.0, 5.4), 'steel')
            C(bn, (x - 2.4, 3.4, -2.4), (4.8, 1.8, 4.8), 'fur', params={'seed': 40})                         # fur cuffs
            C(bn, (x - 1.0, 0.6, -3.4), (2.0, 1.6, 1.2), 'plate')
            C(bn, (x + s * 2.5 - 0.3, 1.0, -0.5), (0.6, 3.0, 1.2), 'ice', rot=(0, 0, 14 * s), pivot=(x + s * 2.5, 1, 0), params={'seed': 41})


# ============================================================================== GLACITE  (diamond replica: cut ice crystal with snowflake emblem)
GLACITE = [hx(c) for c in ('#06182e', '#0f3a6a', '#1c70b0', '#40b4e8', '#8ee0ff', '#d4f6ff', '#ffffff')]


def glacite_materials():
    silver = R('#3a4a5c', '#6a809a', '#a0b6cc', '#dae6f2', '#ffffff')
    deep = R('#06101e', '#0c2040', '#143868', '#1e5090')

    def crystal(ctx):
        r, g, b, a, gl = P.make(GLACITE, scale=0.32, base=0.5, amp=0.3, bevel=0.24, seed=261)(ctx)
        n = fbm3(ctx.W, 262, 0.4, 2)
        if abs(n - 0.5) < 0.03:
            c = ramp_at(GLACITE, 0.96)
            return (c[0], c[1], c[2], 255, 30)
        return (r, g, b, a, gl)

    def flake(ctx):
        c = ramp_at(GLACITE, 0.97)
        return (c[0], c[1], c[2], 255, 230)
    return {'plate': crystal, 'silver': P.make(silver, scale=0.5, base=0.6, amp=0.3, bevel=0.3, seed=263), 'deep': P.make(deep, scale=0.5, base=0.5, amp=0.4, bevel=0.15, seed=264),
            'shard': P.make(GLACITE, scale=0.4, base=0.72, amp=0.2, bevel=0.22, seed=265, glow_fn=lambda ctx, n, c: (c, 80)), 'flake': flake}


def glacite(m, piece):
    base_volumes(m, piece, 'plate', infl_chest=0.6)
    C = m.cube
    if piece == 'helmet':
        for k, (x, h, rz, rx) in enumerate(((0, 8, 0, -4), (-2.0, 6.4, 16, -4), (2.0, 6.4, -16, -4), (-3.6, 4.6, 34, -6), (3.6, 4.6, -34, -6))):
            C('head', (x - 0.9, 32.0, -1.4), (1.8, h, 1.8), 'shard', rot=(rx, 0, rz), pivot=(x, 32, -0.5), params={'seed': 10 + k})
        for s in (-1, 1):
            C('head', (s * 4.6 - 0.4, 24.0, -3.4), (0.8, 5.0, 6.0), 'silver')
            C('head', (s * 5.2 - 0.6, 28.0, 1.0), (1.2, 5.0, 1.2), 'shard', rot=(10, 0, -30 * s), pivot=(s * 5.2, 28, 1), params={'seed': 20})
        C('head', (-4.7, 27.4, -4.8), (9.4, 2.0, 1.0), 'silver')                                             # visor rim
        C('head', (-3.8, 27.8, -5.0), (7.6, 1.0, 0.6), 'deep')
        C('head', (-0.8, 29.6, -5.1), (1.6, 1.6, 0.6), 'flake')
    elif piece == 'chestplate':
        C('body', (-4.3, 22.4, -2.6), (8.6, 1.8, 5.2), 'silver')
        for k, (dx, dy) in enumerate(((0, 0), (-2.2, -2.4), (2.2, -2.4), (0, -4.6))):                         # snowflake emblem
            C('body', (dx - 0.8, 17.6 + dy, -3.2), (1.6, 1.6, 0.8), 'flake')
        C('body', (-0.5, 12.8, -2.9), (1.0, 4.0, 0.5), 'flake')
        C('body', (-3.8, 12.2, 2.0), (7.6, 11.0, 1.0), 'plate', inflate=0.3, params={'seed': 40})
        for k in range(3):
            C('body', (-3.0 + k * 2.6, 14.0, 3.0), (1.4, 8.0 - k * 1.0, 1.4), 'shard', rot=(10, 0, 0), pivot=(-2.3 + k * 2.6, 22, 3), params={'seed': 41 + k})
        for s, bn in ((-1, 'rightArm'), (1, 'leftArm')):
            x = s * 6.0
            for k, (dx, h, rz) in enumerate(((0, 7.0, 10 * s), (-2.2 * s, 5.2, 34 * s), (2.2 * s, 5.0, -14 * s))):
                C(bn, (x + dx - 1.0, 22.6, -1.0), (2.0, h, 2.0), 'shard', rot=(0, 0, -rz), pivot=(x + dx, 22.6, 0), params={'seed': 50 + k})
            C(bn, (x - 2.8, 21.2, -2.8), (5.6, 1.2, 5.6), 'silver')
            C(bn, (x - 2.5, 12.2, -2.5), (5.0, 1.2, 5.0), 'silver')
    elif piece == 'leggings':
        C('body', (-4.3, 15.6, -2.5), (8.6, 1.4, 5.0), 'silver')
        C('body', (-1.0, 15.7, -3.1), (2.0, 1.4, 0.7), 'flake')
        for s, bn in ((-1, 'rightLeg'), (1, 'leftLeg')):
            x = s * 1.9
            C(bn, (x - 1.2, 5.4, -3.4), (2.4, 3.6, 1.6), 'shard', rot=(26, 0, 0), pivot=(x, 7, -2.4), params={'seed': 60})
            C(bn, (x - 1.9, 7.0, -2.9), (3.8, 5.0, 0.8), 'plate', rot=(-8, 0, 0), pivot=(x, 13, -2.4), params={'seed': 61})
            C(bn, (x - 2.4, 11.0, -2.4), (4.8, 1.0, 4.8), 'silver')
    else:
        for s, bn in ((-1, 'rightLeg'), (1, 'leftLeg')):
            x = s * 1.9
            C(bn, (x - 2.5, 0.4, -2.5), (5.0, 1.0, 5.0), 'silver')
            for k, (dz, rx, h) in enumerate(((1.4, -16, 4.8), (2.8, -30, 3.8))):
                C(bn, (x + s * 2.6 - 0.4, 1.0, dz - 0.8), (0.8, h, 1.6), 'shard', rot=(rx, 0, 16 * s), pivot=(x + s * 2.6, 1.5, dz), params={'seed': 70 + k})
            C(bn, (x - 1.2, 0.4, -3.4), (2.4, 2.0, 1.6), 'plate', rot=(-10, 0, 0), pivot=(x, 1, -2.5), params={'seed': 72})


# ============================================================================== WISPSTEEL  (netherite replica: dark fen-iron, lantern light, antler crest)
WISPSTEEL = [hx(c) for c in ('#06140e', '#0f3a26', '#1c7a4a', '#3cc070', '#a8f08a', '#ffe27a', '#fffbd0')]


def wispsteel_materials():
    iron = R('#0a0e0c', '#161e1a', '#26322c', '#3c4a42', '#586a60')
    gold = R('#6a4a0a', '#a8781a', '#d9a830', '#f7d466', '#fff0a8')
    moss = R('#0c1a0e', '#18331a', '#2a5a2a', '#468a38')
    bark = R('#140c06', '#2c1c0e', '#503418', '#7a5430')

    def dark_plate(ctx):
        r, g, b, a, gl = P.make(iron, scale=0.35, base=0.5, amp=0.4, bevel=0.22, seed=271)(ctx)
        n = fbm3(ctx.W, 272, 0.3, 3)
        if abs(n - 0.5) < 0.026:                                           # green foxfire in the seams
            c = ramp_at(WISPSTEEL, 0.62 + 0.3 * fbm3(ctx.W, 273, 0.7, 2))
            return (c[0], c[1], c[2], 255, 0)
        if n > 0.8:
            c = ramp_at(moss, 0.55)
            return (c[0], c[1], c[2], 255, 0)
        return (r, g, b, a, gl)
    return {'plate': dark_plate, 'gold': P.make(gold, scale=0.5, base=0.55, amp=0.4, bevel=0.3, seed=274),
            'moss': P.make(moss, scale=0.4, base=0.5, amp=0.5, bevel=0.1, seed=275, streak=(1, 0.5)), 'bark': P.make(bark, scale=0.4, base=0.5, amp=0.5, bevel=0.2, seed=276, streak=(1, 0.6)),
            'lamp': solid_glow(WISPSTEEL, 0.7, 1.0, 255, 277, rim=False), 'wisp': solid_glow(WISPSTEEL, 0.4, 0.8, 220, 278, rim=False)}


def wispsteel(m, piece):
    base_volumes(m, piece, 'plate')
    C = m.cube
    if piece == 'helmet':
        for s in (-1, 1):
            for k, (dy, h, rz) in enumerate(((0, 7.0, 16), (4.0, 5.0, 46))):                                   # antler crest
                C('head', (s * 3.4 - 0.6, 31.6 + dy, -0.6), (1.2, h, 1.2), 'bark', rot=(0, 0, -rz * s), pivot=(s * 3.4, 31.6 + dy, 0), params={'seed': 10 + k})
            C('head', (s * 4.55 - 0.4, 24.0, -3.2), (0.8, 5.0, 5.6), 'plate')
            C('head', (s * 2.1 - 1.0, 27.6, -4.9), (2.0, 0.9, 0.5), 'lamp')                                    # glowing eye slits
        C('head', (-4.6, 29.2, -4.8), (9.2, 1.2, 1.0), 'gold')
        C('head', (-1.0, 24.4, -4.9), (2.0, 2.4, 0.9), 'plate')
        C('head', (-1.0, 33.4, -4.0), (2.0, 2.0, 2.0), 'wisp', params={'rim': False})                           # a wisp above the brow
        C('head', (-4.7, 29.8, 2.6), (9.4, 4.0, 1.8), 'moss', params={'seed': 12})                              # moss hood-back
    elif piece == 'chestplate':
        C('body', (-4.3, 22.5, -2.6), (8.6, 1.6, 5.2), 'gold')
        C('body', (-1.6, 15.4, -3.1), (3.2, 5.0, 1.2), 'lamp')                                                  # lantern in the chest
        for dx in (-1.7, 1.1):
            C('body', (dx, 15.2, -3.4), (0.6, 5.4, 0.6), 'gold')
        C('body', (-2.0, 14.6, -3.3), (4.0, 0.8, 0.8), 'gold'); C('body', (-2.0, 20.2, -3.3), (4.0, 0.8, 0.8), 'gold')
        C('body', (-3.8, 12.2, 2.0), (7.6, 11.0, 1.0), 'plate', inflate=0.3, params={'seed': 41})
        C('body', (-4.6, 4.0, 2.8), (9.2, 17.0, 0.8), 'moss', rot=(-4, 0, 0), pivot=(0, 22, 2.8), params={'seed': 42})   # moss cloak
        for s, bn in ((-1, 'rightArm'), (1, 'leftArm')):
            x = s * 6.0
            C(bn, (x - 2.8, 21.4, -2.8), (5.6, 1.4, 5.6), 'plate')
            C(bn, (x - 1.0, 22.8, -1.0), (2.0, 2.0, 2.0), 'wisp', params={'rim': False})
            C(bn, (x - 2.5, 12.2, -2.5), (5.0, 1.2, 5.0), 'gold')
    elif piece == 'leggings':
        C('body', (-4.3, 15.6, -2.5), (8.6, 1.4, 5.0), 'gold')
        C('body', (-3.5, 12.0, -3.4), (1.0, 4.0, 0.8), 'gold'); C('body', (2.5, 12.0, -3.4), (1.0, 4.0, 0.8), 'gold')       # hanging chains
        C('body', (-4.0, 9.6, -3.9), (2.0, 3.0, 2.0), 'lamp'); C('body', (2.0, 9.6, -3.9), (2.0, 3.0, 2.0), 'lamp')         # belt lanterns
        for s, bn in ((-1, 'rightLeg'), (1, 'leftLeg')):
            x = s * 1.9
            C(bn, (x - 1.9, 6.0, -2.9), (3.8, 6.0, 0.8), 'plate', rot=(-8, 0, 0), pivot=(x, 13, -2.4), params={'seed': 61})
            C(bn, (x - 0.8, 5.4, -3.4), (1.6, 2.4, 1.2), 'gold')
    else:
        for s, bn in ((-1, 'rightLeg'), (1, 'leftLeg')):
            x = s * 1.9
            C(bn, (x - 2.5, 0.0, -2.5), (5.0, 1.0, 5.4), 'gold')
            C(bn, (x - 2.4, 3.2, -2.4), (4.8, 2.0, 4.8), 'moss', params={'seed': 71})
            C(bn, (x - 1.0, 0.8, -3.4), (2.0, 1.6, 1.2), 'plate')
            C(bn, (x + s * 2.6 - 0.8, 1.6, -0.8), (1.6, 1.6, 1.6), 'wisp', params={'rim': False})


DESIGNS = {
    'azurite': (azurite, azurite_materials), 'pyrelite': (pyrelite, pyrelite_materials),
    'eclipsite': (eclipsite, eclipsite_materials), 'sakura': (sakura, sakura_materials),
    'rimesteel': (rimesteel, rimesteel_materials), 'glacite': (glacite, glacite_materials), 'wispsteel': (wispsteel, wispsteel_materials),
}
CENTER = {'helmet': (0, 30, 0), 'chestplate': (0, 18, 0), 'leggings': (0, 9, 0), 'boots': (0, 3, 0)}
SCALE = {'helmet': 17, 'chestplate': 11, 'leggings': 12, 'boots': 20}


def build_model(mat, piece):
    m = Model(armor_id(mat, piece), 128, 128, bounds=BOUNDS)
    DESIGNS[mat][0](m, piece)
    m.pack()
    base, glow = m.paint(DESIGNS[mat][1]())
    return m, base


def icon(m, tex, piece):
    """3D render of the piece, tight-cropped and resized to a 32x32 inventory icon"""
    from geo import render
    import geo
    geo.GAIN = 1.25
    im = render(m, tex, None, yaw=28, pitch=-6, scale=SCALE[piece] * 3, size=(900, 900), center=CENTER[piece], rgba=True, ycen=0.5)
    bbox = im.getbbox()
    im = im.crop(bbox)
    side = max(im.size)
    sq = Image.new('RGBA', (side + 8, side + 8), (0, 0, 0, 0))
    sq.paste(im, ((side + 8 - im.width) // 2, (side + 8 - im.height) // 2))
    return sq.resize((32, 32), Image.LANCZOS)


from PIL import Image
