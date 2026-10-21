"""The Veiled Blossom (Hanae) - a floating shrine maiden in layered kimono with a wagasa parasol, a folding fan, orbiting petals and paper charms;
plus her Blossom Vex (a tiny masked petal spirit).  Glow channel: eyes, jewel, charm glyphs, petal edges."""
import math
from common import *
from geo import Model, fbm3
import paint as P
from mob_hostiles import solid_glow, R

HANAE_ID = 'geometry.ecr_veiled_blossom'
VEX_ID = 'geometry.ecr_blossom_vex'

PINK = R('#6a2448', '#a8466f', '#dc7aa4', '#f6a8c8', '#ffd2e4', '#fff0f6')
PLUM = R('#12061a', '#241030', '#3a1c4c', '#582a6c')
SKIN = R('#c8a898', '#e6c8b8', '#f6e2d4', '#fff2ea')
HAIR = R('#05020a', '#100618', '#201028', '#34183c')
GOLD = R('#6a4a0a', '#a8781a', '#d9a830', '#f7d466', '#fff0a8')
MASK = R('#b8b0b8', '#dcd6dc', '#f6f2f6', '#ffffff')
RED = R('#4a0a18', '#8a1428', '#c8284a', '#f0607a')
WOOD = R('#2a1c10', '#4a3420', '#6c4e30', '#8e6c44')
CREAM = R('#a89080', '#d2baa6', '#ecdccb', '#fff6ec')
GLOW = R('#a0406a', '#f070a8', '#ffb0d0', '#ffffff')


def hanae_materials(corrupt=False):
    pink = PINK if not corrupt else R('#1a0610', '#4a0a24', '#8a1440', '#c8285a', '#ff6a8a', '#ffd0dc')
    plum = PLUM if not corrupt else R('#06010a', '#10041a', '#1c0828', '#2c1038')
    red = RED if not corrupt else R('#2a0004', '#5a0010', '#a00020', '#ff2a4a')
    glowc = GLOW if not corrupt else R('#600010', '#d01040', '#ff6080', '#ffe0e8')

    def kimono(ctx):
        r, g, b, a, gl = P.make(pink, scale=0.5, base=0.6, amp=0.28, bevel=0.14, seed=301, streak=(1, 0.3))(ctx)
        n = fbm3(ctx.W, 302, 0.8, 2)
        if n > 0.76:
            c = ramp_at(CREAM, 0.85)
            return (c[0], c[1], c[2], 255, 0)
        return (r, g, b, a, gl)

    def under(ctx):
        r, g, b, a, gl = P.make(plum, scale=0.5, base=0.5, amp=0.4, bevel=0.12, seed=303, streak=(1, 0.3))(ctx)
        W = ctx.W
        if int(W[1]) % 6 == 0 and ctx.face in ('north', 'south', 'east', 'west'):      # embroidered bands
            c = ramp_at(GOLD, 0.55)
            return (c[0], c[1], c[2], 255, 0)
        n = fbm3(W, 304, 0.7, 2)
        if n > 0.78:
            c = ramp_at(pink, 0.7)
            return (c[0], c[1], c[2], 255, 40)
        return (r, g, b, a, gl)

    def canopy(ctx):
        r, g, b, a, gl = P.make(red, scale=0.5, base=0.55, amp=0.3, bevel=0.14, seed=305)(ctx)
        d = int(ctx.W[0] * 0.9 + ctx.W[2] * 0.9)
        if d % 9 == 0 or (d % 9 == 1 and ctx.face == 'up'):                           # cream ribs
            c = ramp_at(CREAM, 0.7)
            return (c[0], c[1], c[2], 255, 0)
        n = fbm3(ctx.W, 306, 0.9, 2)
        if n > 0.8:
            c = ramp_at(pink, 0.9)
            return (c[0], c[1], c[2], 255, 90)
        return (r, g, b, a, gl)

    def ofuda(ctx):
        r, g, b, a, gl = P.make(CREAM, scale=0.5, base=0.6, amp=0.2, bevel=0.1, seed=307)(ctx)
        if ctx.face in ('north', 'south') and 1 <= ctx.i <= ctx.w - 2 and 1 <= ctx.j <= ctx.h - 2 and (ctx.i + ctx.j * 3) % 4 == 0:
            c = ramp_at(glowc, 0.8)
            return (c[0], c[1], c[2], 255, 230)                                      # glowing seal glyph
        return (r, g, b, a, gl)

    return {
        'kimono': kimono, 'under': under, 'canopy': canopy, 'ofuda': ofuda,
        'skin': P.make(SKIN, scale=0.5, base=0.6, amp=0.2, bevel=0.1, seed=308), 'hair': P.make(HAIR, scale=0.5, base=0.5, amp=0.4, bevel=0.1, seed=309, streak=(1, 0.5)),
        'gold': P.make(GOLD, scale=0.5, base=0.55, amp=0.35, bevel=0.3, seed=310), 'mask': P.make(MASK, scale=0.6, base=0.65, amp=0.15, bevel=0.15, seed=311),
        'mark': P.make(red, scale=0.6, base=0.6, amp=0.2, seed=312), 'obi': P.make(red, scale=0.45, base=0.5, amp=0.4, bevel=0.15, seed=313, streak=(1, 0.5)),
        'wood': P.make(WOOD, scale=0.5, base=0.5, amp=0.4, bevel=0.1, seed=314, streak=(1, 0.5)),
        'petal': P.make(pink, scale=0.6, base=0.72, amp=0.2, bevel=0.2, seed=315, glow_fn=lambda ctx, n, c: (c, 70)),
        'eye': solid_glow(glowc, 0.6, 1.0, 255, 316, rim=False), 'gem': solid_glow(glowc, 0.5, 1.0, 255, 317, rim=True),
    }


def hanae():
    m = Model(HANAE_ID, 256, 256, bounds=(3.2, 3.6, (0, 1.6, 0)))
    B = m.bone
    C = m.cube
    B('root', None, (0, 0, 0))
    B('float', 'root', (0, 0, 0))
    B('body', 'float', (0, 20, 0))
    # robes: three flaring skirt layers, obi, torso, collar
    C('body', (-6.2, 6, -4.8), (12.4, 4.6, 9.6), 'under', params={'seed': 1})
    C('body', (-5.4, 10.6, -4.2), (10.8, 4.6, 8.4), 'kimono', params={'seed': 2})
    C('body', (-4.6, 15.2, -3.6), (9.2, 4.6, 7.2), 'under', params={'seed': 3})
    C('body', (-4.5, 19.6, -3.0), (9.0, 3.4, 6.0), 'obi', params={'seed': 4})
    C('body', (-1.4, 19.9, -3.5), (2.8, 2.8, 0.8), 'gold')                                    # obi clasp
    C('body', (-3.7, 23.0, -2.4), (7.4, 7.2, 4.8), 'kimono', params={'seed': 5})
    C('body', (-5.0, 29.2, -2.8), (10.0, 2.0, 5.6), 'kimono', params={'seed': 6})            # haori shoulder piece
    C('body', (-1.0, 23.6, -2.8), (2.0, 5.4, 0.6), 'under', rot=(0, 0, 18), pivot=(0, 29, -2.7))     # crossed collar
    C('body', (-1.0, 23.6, -2.8), (2.0, 5.4, 0.6), 'under', rot=(0, 0, -18), pivot=(0, 29, -2.7))
    C('body', (-3.0, 28.2, -2.9), (6.0, 1.0, 0.6), 'gold')
    # obi bow on the back
    B('bow', 'body', (0, 21, 3.2))
    C('bow', (-4.4, 19.4, 3.0), (3.6, 3.6, 1.6), 'obi', rot=(0, 0, 28), pivot=(-2.4, 21, 3.4))
    C('bow', (0.8, 19.4, 3.0), (3.6, 3.6, 1.6), 'obi', rot=(0, 0, -28), pivot=(2.4, 21, 3.4))
    C('bow', (-0.9, 20.0, 3.2), (1.8, 2.6, 1.4), 'gold')
    for s in (-1, 1):
        C('bow', (s * 1.4 - 0.7, 9.0, 3.4), (1.4, 11.0, 0.6), 'obi', rot=(8, 0, 6 * s), pivot=(s * 1.4, 20, 3.6))   # sash tails
    # hem trim petals + sway strips
    for k in range(10):
        a = k / 10 * math.tau
        x, z = math.sin(a) * 6.2, math.cos(a) * 4.6
        bn = f'hem{k}'
        B(bn, 'body', (x, 6, z))
        C(bn, (x - 1.2, 2.6, z - 0.5), (2.4, 3.6, 1.0), 'petal', params={'seed': 10 + k})
    # head
    B('head', 'body', (0, 31, 0))
    C('head', (-3, 31, -3), (6, 6.4, 6), 'skin', params={'seed': 20})
    C('head', (-3.5, 35.6, -3.5), (7, 2.6, 7), 'hair', params={'seed': 21})
    C('head', (-3.5, 31.5, -3.6), (0.9, 5.6, 1.2), 'hair'); C('head', (2.6, 31.5, -3.6), (0.9, 5.6, 1.2), 'hair')
    C('head', (-3.5, 31.0, 2.6), (7, 7.0, 1.4), 'hair')
    C('head', (-3.5, 34.2, -3.8), (3.2, 2.0, 0.9), 'hair', rot=(0, 0, 12), pivot=(-0.5, 36.2, -3.4))    # parted bangs
    C('head', (0.3, 34.2, -3.8), (3.2, 2.0, 0.9), 'hair', rot=(0, 0, -12), pivot=(0.5, 36.2, -3.4))
    for s in (-1, 1):
        C('head', (s * 3.6 - 1.3, 35.4, -0.6), (2.6, 2.6, 2.6), 'hair', params={'seed': 22})        # buns
        C('head', (s * 3.6 - 0.6, 36.9, -0.2), (1.2, 1.2, 1.2), 'gold')
        C('head', (s * 1.6 - 0.6, 33.5, -3.15), (1.2, 0.8, 0.5), 'eye', params={'rim': False})      # glowing eyes
        C('head', (s * 3.3 - 0.2, 26.0, -3.5), (0.4, 5.0, 0.4), 'gold')                              # hanging bead strands
        C('head', (s * 3.3 - 0.5, 25.0, -3.55), (1.0, 1.0, 1.0), 'petal')
    C('head', (-3.1, 31.0, -3.5), (6.2, 3.0, 0.6), 'mask', params={'seed': 23})                     # veil mask over the lower face
    C('head', (-0.4, 31.6, -3.65), (0.8, 2.2, 0.4), 'mark')
    for s in (-1, 1):
        C('head', (s * 1.9 - 0.3, 32.0, -3.65), (0.6, 1.8, 0.4), 'mark', rot=(0, 0, 10 * s), pivot=(s * 1.9, 33, -3.6))
    C('head', (-0.6, 34.6, -3.75), (1.2, 1.2, 0.5), 'gem')                                          # forehead jewel
    for k in range(7):                                                                              # blossom crown
        a = (k - 3) / 3 * 1.1
        C('head', (math.sin(a) * 3.8 - 1.0, 37.6 + math.cos(a) * 0.5, math.cos(a) * 1.0 - 2.6), (2.0, 1.2, 2.0), 'petal', rot=(0, 0, -math.degrees(a)), pivot=(math.sin(a) * 3.8, 38, math.cos(a) * 1.0 - 1.6), params={'seed': 30 + k})
    for k, rz in enumerate((-50, -25, 0, 25, 50)):                                                  # kanzashi fan
        C('head', (-0.5, 37.0, 2.6), (1.0, 5.4, 0.4), 'gold', rot=(-10, 0, rz), pivot=(0, 36.8, 2.8))
    for k in range(5):                                                                              # long hair strips (sway)
        x = -3 + k * 1.5
        bn = f'hair{k}'
        B(bn, 'head', (x + 0.7, 31, 2.8))
        C(bn, (x, 14.0 + (k % 2) * 1.5, 3.0), (1.5, 17.0 - (k % 2) * 1.5, 1.2), 'hair', params={'seed': 40 + k})
    B('veil', 'head', (0, 31, -3.4))
    C('veil', (-2.8, 22.0, -3.7), (5.6, 8.4, 0.3), 'mask')                                          # trailing veil strip
    C('veil', (-2.8, 22.0, -3.75), (5.6, 0.8, 0.3), 'mark')
    # arms with long furisode sleeves
    for s, tag in ((-1, 'r'), (1, 'l')):
        x = s * 4.6
        arm, sl = f'arm_{tag}', f'sleeve_{tag}'
        B(arm, 'body', (x, 29, 0))
        C(arm, (x - 1.0, 19.0, -1.2), (2.0, 10.0, 2.4), 'kimono', params={'seed': 50 + s})
        C(arm, (x - 0.9, 17.2, -1.0), (1.8, 2.0, 2.0), 'skin')
        B(sl, arm, (x, 28.5, 0))
        C(sl, (x + s * 1.0 - 0.7, 8.0, -3.2), (1.4, 18.0, 6.4), 'kimono', params={'seed': 52 + s})
        C(sl, (x + s * 1.0 - 0.8, 8.0, -3.3), (1.6, 1.6, 6.6), 'gold')
        C(sl, (x + s * 1.0 - 0.8, 24.6, -3.3), (1.6, 1.0, 6.6), 'obi')
    # wagasa parasol in the right hand, tilted out over her shoulder so the face stays visible
    B('parasol', 'arm_r', (-4.6, 18.4, -0.5), rot=(0, 0, 38))
    C('parasol', (-5.1, 18.0, -1.0), (1.0, 24.0, 1.0), 'wood', params={'seed': 60})
    for k in range(5):
        hw = 9.5 - k * 1.9
        C('parasol', (-4.6 - hw, 33.0 + k * 1.2, -hw), (2 * hw, 1.3, 2 * hw), 'canopy', params={'seed': 61 + k})
    C('parasol', (-5.4, 39.4, -0.8), (1.6, 2.6, 1.6), 'gold')
    for k in range(8):                                                                              # dangling canopy tassels
        a_ = k / 8 * math.tau
        C('parasol', (-4.6 + math.cos(a_) * 11.0 - 0.4, 29.4, math.sin(a_) * 11.0 - 0.4), (0.8, 4.2, 0.8), 'petal')
    # folding fan in the left hand
    B('fan', 'arm_l', (4.6, 18.4, -1.0))
    for k, rz in enumerate((-60, -30, 0, 30, 60)):
        C('fan', (4.2, 18.6, -1.4), (1.2, 9.0, 0.5), 'gold' if k % 2 else 'petal', rot=(0, 0, rz), pivot=(4.8, 18.6, -1.2))
    # orbiting petals and paper charms
    B('orbit', 'float', (0, 22, 0))
    for k in range(10):
        a = k / 10 * math.tau
        r_ = 14 + (k % 3) * 2.4
        C('orbit', (math.cos(a) * r_ - 1.0, 10 + (k * 2.7) % 24, math.sin(a) * r_ - 1.3), (2.0, 0.4, 2.6), 'petal', rot=(20 * math.sin(a), math.degrees(a), 20 * math.cos(a)),
          pivot=(math.cos(a) * r_, 12, math.sin(a) * r_), params={'seed': 70 + k})
    B('charms', 'float', (0, 20, 0))
    for k in range(5):
        a = k / 5 * math.tau
        C('charms', (math.cos(a) * 9.5 - 0.9, 14 + (k % 2) * 4, math.sin(a) * 9.5 - 0.15), (1.8, 5.2, 0.3), 'ofuda', rot=(0, -math.degrees(a) + 90, 0),
          pivot=(math.cos(a) * 9.5, 16, math.sin(a) * 9.5), params={'seed': 90 + k})
    return m


# ============================================================================== BLOSSOM VEX
def vex_materials():
    return {
        'mask': P.make(MASK, scale=0.6, base=0.65, amp=0.15, bevel=0.2, seed=330), 'mark': P.make(RED, scale=0.6, base=0.6, amp=0.2, seed=331),
        'petal': P.make(PINK, scale=0.6, base=0.72, amp=0.2, bevel=0.2, seed=332, glow_fn=lambda ctx, n, c: (c, 90)),
        'robe': P.make(PINK, scale=0.5, base=0.5, amp=0.3, bevel=0.12, seed=333), 'gold': P.make(GOLD, scale=0.5, base=0.55, amp=0.35, bevel=0.3, seed=334),
        'eye': solid_glow(GLOW, 0.6, 1.0, 255, 335, rim=False), 'hair': P.make(HAIR, scale=0.5, base=0.5, amp=0.4, seed=336),
    }


def vex():
    m = Model(VEX_ID, 64, 64, bounds=(1.2, 1.4, (0, 0.5, 0)))
    B = m.bone
    DY = 7.0

    def C(bone, origin, size, mat, **kw):
        kw_ = dict(kw)
        if kw_.get('pivot'):
            kw_['pivot'] = (kw_['pivot'][0], kw_['pivot'][1] + DY, kw_['pivot'][2])
        return m.cube(bone, (origin[0], origin[1] + DY, origin[2]), size, mat, **kw_)
    B('root', None, (0, 0, 0))
    B('body', 'root', (0, 8 + DY, 0))
    C('body', (-2.4, 5, -2.4), (4.8, 5.4, 4.8), 'robe', params={'seed': 1})                          # small petal-robed body
    C('body', (-3.0, 3.2, -3.0), (6.0, 2.2, 6.0), 'petal', params={'seed': 2})
    B('head', 'body', (0, 10.4 + DY, 0))
    C('head', (-3, 10.4, -3), (6, 5.6, 6), 'mask', params={'seed': 3})                              # round white mask head
    C('head', (-3.5, 14.6, -3.5), (7, 2.0, 7), 'hair')
    C('head', (-0.4, 14.0, -3.15), (0.8, 2.2, 0.4), 'mark')
    for s in (-1, 1):
        C('head', (s * 1.5 - 0.7, 12.4, -3.1), (1.4, 0.8, 0.4), 'eye', params={'rim': False})
        C('head', (s * 2.1 - 0.3, 10.6, -3.15), (0.6, 1.6, 0.4), 'mark', rot=(0, 0, 14 * s), pivot=(s * 2.1, 11.4, -3.1))
        C('head', (s * 2.6 - 1.0, 15.2, -1.0), (2.0, 2.0, 2.0), 'petal', params={'seed': 4})          # petal ears
    for s, tag in ((-1, 'l'), (1, 'r')):
        B(f'wing_{tag}', 'body', (s * 2.4, 9 + DY, 1.4))
        for k, (rz, ln) in enumerate(((20, 7.0), (-5, 6.0), (-30, 5.0))):
            C(f'wing_{tag}', (s * 2.4 + (0 if s > 0 else -ln), 8.4 - k * 1.0, 1.0), (ln, 0.5, 3.0), 'petal', rot=(0, 0, rz * s), pivot=(s * 2.4, 9, 1.4), params={'seed': 5 + k})
    for k in range(3):                                                                              # trailing ribbon tail (sways)
        bn = f'tail{k}'
        B(bn, 'body' if k == 0 else f'tail{k - 1}', (0, 5 - k * 3.2 + DY, 2.0 + k * 0.4))
        C(bn, (-0.9, 2.0 - k * 3.2, 1.6 + k * 0.4), (1.8, 3.4, 0.8), 'petal' if k % 2 == 0 else 'gold', params={'seed': 8 + k})
    return m


MODELS = {'veiled_blossom': (hanae, hanae_materials, HANAE_ID), 'blossom_vex': (vex, vex_materials, VEX_ID)}
