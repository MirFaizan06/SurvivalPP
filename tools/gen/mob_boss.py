"""The Eclipse Sovereign - towering void-armoured colossus crowned with a living eclipse."""
import math
from common import *
from geo import Model, fbm3
import paint as P

ID = 'geometry.ecr_eclipse_sovereign'


def materials():
    armor = [hx(x) for x in ['#05030a', '#0d0716', '#170d28', '#251640', '#37225f', '#4d3384']]
    trim = [hx(x) for x in ['#3b2468', '#6b44b5', '#a276ee', '#d5b6ff', '#f8eeff']]
    cloth = [hx(x) for x in ['#04020a', '#090414', '#120826', '#1d0e3c']]
    horn = [hx(x) for x in ['#1a1430', '#352c58', '#5f5490', '#9a8fcf', '#d6ceff']]
    skin = [hx(x) for x in ['#07040f', '#120a23', '#1e1237', '#2d1c52']]
    armor_base = P.make(armor, scale=0.2, base=0.42, amp=0.4, bevel=0.35, seed=31)

    def armor_fn(ctx):
        r, g, b, a, gl = armor_base(ctx)
        W = ctx.W
        # engraved plating lines + sparse glowing rune dashes
        if ctx.cube.params.get('panel', 1):
            if (int(W[0] + 100) % 6 == 0) or (int(W[1] + 100) % 7 == 0):
                return (int(r * 0.55), int(g * 0.55), int(b * 0.6), a, 0)
        if ctx.cube.params.get('runes') and (int(W[0] + 100) % 6 == 3) and (int(W[1] + 100) % 5 in (1, 2)):
            c = ramp_at(ECLIPSITE, 0.78)
            return (c[0], c[1], c[2], 255, 230)
        return (r, g, b, a, gl)

    def cloth_fn(ctx):
        r, g, b, a, gl = P.make(cloth, scale=0.45, base=0.5, amp=0.5, bevel=0.08, seed=33, streak=(1, 0.2))(ctx)
        if ctx.face in ('north', 'south', 'east', 'west') and (ctx.j >= ctx.h - 2 or ctx.i == 0 or ctx.i == ctx.w - 1) and ctx.cube.params.get('edge', 1):
            c = ramp_at(ECLIPSITE, 0.62)
            return (c[0], c[1], c[2], 255, 170)
        return (r, g, b, a, gl)

    def glow_gradient(ctx):
        n = fbm3(ctx.W, 51, 0.35, 2)
        t = 0.5 + 0.45 * n
        c = ramp_at(ECLIPSITE, min(1, t))
        if ctx.cube.params.get('white'):
            c = mix(c, (255, 255, 255), 0.55)
        d, side = ctx.edge
        if d < 1 and ctx.w > 2 and ctx.cube.params.get('rim', True):
            c = tuple(int(v * 0.72) for v in c)
        return (c[0], c[1], c[2], 255, 255)

    def core_fn(ctx):
        # a black eclipse disc with a bright corona on the chest plate (square face texture)
        cx, cy = (ctx.w - 1) / 2, (ctx.h - 1) / 2
        d = math.hypot((ctx.i - cx) / max(1, ctx.w / 2), (ctx.j - cy) / max(1, ctx.h / 2))
        ang = math.atan2(ctx.j - cy, ctx.i - cx)
        if ctx.face not in ('north',):
            c = ramp_at(armor, 0.3)
            return (c[0], c[1], c[2], 255, 0)
        if d < 0.55:
            return (4, 2, 10, 255, 0)
        if d < 0.82:
            t = 0.5 + 0.5 * math.cos(ang - 3.9)
            c = ramp_at(ECLIPSITE, 0.55 + 0.45 * t)
            return (c[0], c[1], c[2], 255, 255)
        if d < 1.05:
            ray = abs(math.sin(ang * 6))
            if ray > 0.7:
                c = ramp_at(ECLIPSITE, 0.45)
                return (c[0], c[1], c[2], 255, 190)
        c = ramp_at(armor, 0.2)
        return (c[0], c[1], c[2], 255, 0)

    def eye_fn(ctx):
        c = hx('#f4ffff')
        d, side = ctx.edge
        if d == 0:
            c = hx('#6ff3ff')
        return (c[0], c[1], c[2], 255, 255)

    return {
        'armor': armor_fn,
        'trim': P.make(trim, scale=0.4, base=0.5, amp=0.35, bevel=0.3, seed=36),
        'cloth': cloth_fn,
        'horn': P.make(horn, scale=0.35, base=0.5, amp=0.4, bevel=0.25, seed=37, streak=(1, 0.4)),
        'skin': P.make(skin, scale=0.4, base=0.5, amp=0.4, bevel=0.15, seed=38),
        'glow': glow_gradient,
        'core': core_fn,
        'eye': eye_fn,
    }


def build():
    m = Model(ID, 256, 256, bounds=(7, 8, (0, 3.4, 0)))
    B = m.bone
    B('root', None, (0, 0, 0))
    B('float', 'root', (0, 0, 0))
    B('body', 'float', (0, 46, 0))
    # ---------------------------------------------------------------- torso
    m.cube('body', (-7, 40, -4.5), (14, 8, 9), 'armor', params={'seed': 1, 'runes': 1})                 # waist
    m.cube('body', (-12, 48, -6.5), (24, 17, 13), 'armor', params={'seed': 2})                           # chest
    m.cube('body', (-13, 63, -7), (26, 4, 14), 'trim')                                                    # upper chest rim
    m.cube('body', (-8, 66.5, -5.5), (16, 5, 11), 'armor', params={'seed': 3})                           # gorget
    m.cube('body', (-4.4, 51.5, -7.7), (8.8, 8.8, 1.6), 'core')                                          # eclipse core
    m.cube('body', (-5.2, 50.7, -7.3), (10.4, 10.4, 0.9), 'trim', rot=(0, 0, 45), pivot=(0, 55.9, -7))
    m.cube('body', (-11, 47, -7), (22, 1.6, 1), 'trim')
    m.cube('body', (-12.6, 56, 6.2), (25.2, 8, 3), 'armor', params={'seed': 4, 'runes': 1})             # back plate
    # pauldrons (two layered plates + spikes)
    for s in (-1, 1):
        x = s * 17
        m.cube('body', (x - 7, 62, -7.5), (14, 5, 15), 'armor', rot=(0, 0, -10 * s), pivot=(x, 66, 0), params={'seed': 5 + s})
        m.cube('body', (x - 6, 66, -6.5), (12, 4, 13), 'armor', rot=(0, 0, -14 * s), pivot=(x, 66, 0), params={'seed': 7 + s})
        m.cube('body', (x - 5.4, 69.6, -5.5), (10.8, 1.6, 11), 'trim', rot=(0, 0, -16 * s), pivot=(x, 66, 0))
        for k in range(3):
            m.cube('body', (x + s * (2 + k * 3.2) - 1.4, 70.4 + k * 1.4, -1.5), (2.8, 11 - k * 2.5, 3), 'glow', rot=(0, 0, -22 * s - k * 6 * s), pivot=(x + s * (2 + k * 3.2), 70, 0), params={'rim': True})
    # ---------------------------------------------------------------- tasset skirt
    for k in range(5):
        x = -10 + k * 5
        m.cube('body', (x - 2.3, 30, -6.2 + abs(k - 2) * 0.9), (4.6, 12, 1.6), 'armor', rot=(-4, 0, 0), pivot=(x, 41, -5), params={'seed': 10 + k})
        m.cube('body', (x - 1.6, 29, -6.4 + abs(k - 2) * 0.9), (3.2, 1.6, 1.2), 'glow', params={'rim': False})
    # ---------------------------------------------------------------- void tail (floating lower body)
    B('tail1', 'body', (0, 40, 0))
    m.cube('tail1', (-9, 30, -6), (18, 10.5, 12), 'cloth', params={'edge': 0})
    m.cube('tail1', (-9.4, 38.5, -6.4), (18.8, 1.4, 12.8), 'trim')
    B('tail2', 'tail1', (0, 30, 0))
    m.cube('tail2', (-6.5, 21, -4.5), (13, 9.5, 9), 'cloth', params={'edge': 0})
    B('tail3', 'tail2', (0, 21, 0))
    m.cube('tail3', (-4.2, 13, -3), (8.4, 8.5, 6), 'cloth', params={'edge': 0})
    B('tail4', 'tail3', (0, 13, 0))
    m.cube('tail4', (-2.2, 6, -1.6), (4.4, 7.5, 3.2), 'cloth', params={'edge': 0})
    m.cube('tail4', (-0.9, 1.5, -0.9), (1.8, 4.8, 1.8), 'glow')
    for k in range(6):   # glowing seams that spiral down the tail
        y = 38 - k * 5.4
        w = 9 - k * 1.2
        m.cube('tail1' if k < 2 else ('tail2' if k < 4 else 'tail3'), (-w - 0.2, y, -w * 0.66 - 0.5), (2 * w + 0.4, 0.9, 0.8), 'glow', params={'rim': False})
    # ---------------------------------------------------------------- cape tatters
    for k in range(7):
        x = -15 + k * 5
        bn = f'cape{k}'
        B(bn, 'body', (x, 68, 7.8))
        h = 40 + (k % 3) * 6 - abs(k - 3) * 2
        m.cube(bn, (x - 2.2, 68 - h, 7.2), (4.4, h, 1.2), 'cloth')
    # ---------------------------------------------------------------- head
    B('head', 'body', (0, 72, 0))
    m.cube('head', (-6.5, 71, -6.5), (13, 12, 13), 'armor', params={'seed': 20})                         # helm
    m.cube('head', (-7, 70.4, -7), (14, 2, 14), 'trim')                                                    # brow band
    m.cube('head', (-6, 75.6, -7.1), (12, 3.2, 1.2), 'armor', params={'panel': 0})                        # visor
    for s in (-1, 1):
        m.cube('head', (s * 3.2 - 1.8, 76.2, -7.5), (3.6, 1.6, 0.8), 'eye')
        m.cube('head', (s * 5.6 - 1, 70, -7.2), (2, 6, 1.2), 'trim')                                       # cheek guards
    m.cube('head', (-3, 71, -7.4), (6, 5, 1.2), 'armor', params={'panel': 0})
    m.cube('head', (-1, 83, -4), (2, 7, 15), 'armor', rot=(-10, 0, 0), pivot=(0, 83, 3), params={'seed': 24})  # crest fin
    m.cube('head', (-0.6, 83.8, -3.6), (1.2, 5.6, 14), 'glow', rot=(-10, 0, 0), pivot=(0, 83, 3), params={'rim': False})
    for s in (-1, 1):   # great curved horns
        m.cube('head', (s * 6.2 - 2, 77, -3), (4, 6, 4), 'horn', rot=(0, 0, -20 * s), pivot=(s * 6.2, 77, -1))
        m.cube('head', (s * 9.8 - 1.7, 81, -2.7), (3.4, 8, 3.4), 'horn', rot=(0, 0, -36 * s), pivot=(s * 9.8, 81, -1))
        m.cube('head', (s * 14.6 - 1.3, 87, -2.3), (2.6, 8, 2.6), 'horn', rot=(0, 0, -50 * s), pivot=(s * 14.6, 87, -1))
        m.cube('head', (s * 19.6 - 0.9, 93, -1.9), (1.8, 6, 1.8), 'glow', rot=(0, 0, -62 * s), pivot=(s * 19.6, 93, -1), params={'white': 1})
    # ---------------------------------------------------------------- the eclipse halo
    B('halo', 'head', (0, 84, 13))
    N = 14
    for k in range(N):
        a = k / N * math.tau
        x, y = math.cos(a) * 19, math.sin(a) * 19
        m.cube('halo', (x - 3.4, 84 + y - 1.6, 11.5), (6.8, 3.2, 3), 'glow', rot=(0, 0, math.degrees(a) + 90), pivot=(x, 84 + y, 13), params={'white': k % 2})
    for k in range(18):  # corona rays on the inner side
        a = k / 18 * math.tau
        x, y = math.cos(a) * 12.5, math.sin(a) * 12.5
        L = 5 if k % 2 == 0 else 3
        m.cube('halo', (x - 0.7, 84 + y - L / 2, 12.2), (1.4, L, 1.2), 'glow', rot=(0, 0, math.degrees(a) + 90), pivot=(x, 84 + y, 13), params={'white': 1, 'rim': False})
    m.cube('halo', (-8, 76, 12.4), (16, 16, 1.6), 'skin', params={'seed': 30})
    m.cube('halo', (-8, 76, 12.2), (16, 16, 1.6), 'skin', rot=(0, 0, 45), pivot=(0, 84, 13), params={'seed': 31})
    # ---------------------------------------------------------------- arms
    def arm(s, tag):
        x = s * 17.5
        up, lo, hd = f'arm_{tag}', f'forearm_{tag}', f'hand_{tag}'
        B(up, 'body', (x, 63, 0), rot=(0, 0, 6 * s))
        m.cube(up, (x - 4.5, 48, -4.5), (9, 15, 9), 'armor', params={'seed': 40 + s, 'runes': 1})
        m.cube(up, (x - 5.2, 47, -5.2), (10.4, 2.2, 10.4), 'trim')
        B(lo, up, (x, 48, 0), rot=(-18, 0, -4 * s))
        m.cube(lo, (x - 5, 31, -5), (10, 17, 10), 'armor', params={'seed': 42 + s})
        m.cube(lo, (x - 5.6, 30, -5.6), (11.2, 2.4, 11.2), 'trim')
        m.cube(lo, (x - 1, 40, -5.9), (2, 6, 1), 'glow', params={'rim': False})
        # bracer spikes
        m.cube(lo, (x + s * 5 - 1, 40, -1.5), (2, 9, 3), 'armor', rot=(0, 0, -25 * s), pivot=(x + s * 5, 40, 0), params={'panel': 0})
        B(hd, lo, (x, 31, 0))
        m.cube(hd, (x - 4.4, 23, -4.5), (8.8, 8, 9), 'skin', params={'seed': 44 + s})
        for k in range(4):
            fx = x - 3.3 + k * 2.2
            m.cube(hd, (fx - 0.9, 11, -4.2 + (k % 2) * 0.6), (1.8, 12.4, 1.8), 'skin', rot=(-10, 0, 0), pivot=(fx, 23, -3.5), params={'seed': 50 + k})
            m.cube(hd, (fx - 0.8, 5.2, -4.6 + (k % 2) * 0.6), (1.6, 7, 1.6), 'glow', rot=(-10, 0, 0), pivot=(fx, 23, -3.5), params={'white': 1, 'rim': False})
    arm(1, 'l'); arm(-1, 'r')
    # ---------------------------------------------------------------- orbiting void blades
    B('orbit', 'body', (0, 56, 0))
    for k in range(4):
        a = k / 4 * math.tau + math.pi / 4
        x, z = math.sin(a) * 36, math.cos(a) * 36
        m.cube('orbit', (x - 2, 40, z - 1), (4, 24, 2), 'glow', rot=(-8 * math.cos(a), 0, 8 * math.sin(a)), pivot=(x, 52, z), params={'white': 1})
        m.cube('orbit', (x - 4.5, 63, z - 1.6), (9, 2, 3.2), 'trim')
        m.cube('orbit', (x - 1.2, 65, z - 1.2), (2.4, 7, 2.4), 'horn')
        m.cube('orbit', (x - 1.6, 38, z - 0.8), (3.2, 2.4, 1.6), 'glow', params={'rim': False})
    return m
