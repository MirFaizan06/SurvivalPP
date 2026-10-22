"""Chapter III models: Ysolde, the Frost Cantor (boss) and the two frozen dead that follow her - the Rimewalker (zombie-like) and the Hoarbone
(skeleton-like).  Glow channel: eyes, crown crystals, pipe tips, the baton, rime in the cracks."""
import math
from common import *
from geo import Model, fbm3
import paint as P
from mob_hostiles import solid_glow, R

CANTOR_ID = 'geometry.ecr_frost_cantor'
RIME_ID = 'geometry.ecr_rimewalker'
HOAR_ID = 'geometry.ecr_hoarbone'

ICE = R('#12304e', '#2c6498', '#5aa6dc', '#9ed4f4', '#d8f2ff', '#f6fcff')
DEEP = R('#06101e', '#0c2040', '#143868', '#1e5090')
GOWN = R('#22384e', '#3c5878', '#5c7ea0', '#88a8c6', '#bcd4e8')
SKIN = R('#5e7288', '#8298ae', '#a8bccf', '#cbdae8')
HAIR = R('#3a4858', '#627488', '#92a4b8', '#c4d2e0')
SILVER = R('#4a5666', '#78869a', '#a8b6c8', '#d8e2ee')
GLOW = R('#1c78a8', '#5ac8f0', '#a8ecff', '#ffffff')
PIPE = R('#2a3a50', '#4a6486', '#7a98bc', '#b0cae4')


def cantor_materials():
    def gown(ctx):
        r, g, b, a, gl = P.make(GOWN, scale=0.5, base=0.62, amp=0.3, bevel=0.14, seed=401, streak=(1, 0.3))(ctx)
        n = fbm3(ctx.W, 402, 0.7, 2)
        if n > 0.78:                                                    # frost bloom on the silk
            c = ramp_at(ICE, 0.86)
            return (c[0], c[1], c[2], 255, 60)
        return (r, g, b, a, gl)

    def bodice(ctx):
        r, g, b, a, gl = P.make(ICE, scale=0.35, base=0.5, amp=0.34, bevel=0.2, seed=403)(ctx)
        n = fbm3(ctx.W, 404, 0.45, 2)
        if abs(n - 0.5) < 0.03:                                         # facet seams
            c = ramp_at(ICE, 0.97)
            return (c[0], c[1], c[2], 255, 40)
        return (r, g, b, a, gl)

    def sheet(ctx):                                                     # the music: glowing staff lines + notes on the train
        r, g, b, a, gl = P.make(GOWN, scale=0.5, base=0.7, amp=0.2, bevel=0.1, seed=405)(ctx)
        if ctx.face in ('north', 'south') and ctx.j % 3 == 1:
            c = ramp_at(GLOW, 0.7)
            return (c[0], c[1], c[2], 255, 200)
        return (r, g, b, a, gl)

    return {
        'gown': gown, 'bodice': bodice, 'sheet': sheet,
        'under': P.make(DEEP, scale=0.5, base=0.5, amp=0.4, bevel=0.12, seed=406, streak=(1, 0.3)),
        'ice': P.make(ICE, scale=0.4, base=0.62, amp=0.3, bevel=0.22, seed=407),
        'icicle': P.make(ICE, scale=0.4, base=0.72, amp=0.2, bevel=0.2, seed=408, glow_fn=lambda ctx, n, c: (c, 70)),
        'skin': P.make(SKIN, scale=0.5, base=0.6, amp=0.2, bevel=0.1, seed=409),
        'hair': P.make(HAIR, scale=0.5, base=0.6, amp=0.3, bevel=0.1, seed=410, streak=(1, 0.5)),
        'silver': P.make(SILVER, scale=0.5, base=0.55, amp=0.35, bevel=0.3, seed=411),
        'pipe': P.make(PIPE, scale=0.45, base=0.55, amp=0.35, bevel=0.25, seed=412, streak=(1, 0.5)),
        'mouth': P.make(DEEP, scale=0.5, base=0.3, amp=0.2, seed=413),
        'eye': solid_glow(GLOW, 0.6, 1.0, 255, 414, rim=False), 'gem': solid_glow(GLOW, 0.5, 1.0, 255, 415, rim=True),
        'tip': solid_glow(GLOW, 0.55, 1.0, 240, 416, rim=False), 'note': solid_glow(GLOW, 0.4, 0.9, 200, 417, rim=False),
    }


def cantor():
    m = Model(CANTOR_ID, 256, 256, bounds=(3.4, 3.8, (0, 1.6, 0)))
    B, C = m.bone, m.cube
    B('root', None, (0, 0, 0))
    B('float', 'root', (0, 0, 0))
    B('body', 'float', (0, 22, 0))
    # gown: four flaring silk layers over a deep-blue underskirt, icicle hem
    C('body', (-5.0, 16.4, -3.8), (10.0, 4.0, 7.6), 'gown', params={'seed': 2})
    for ring, (rad, ln, tilt, mat) in enumerate(((5.2, 15.0, 22, 'under'), (6.4, 16.0, 30, 'gown'))):          # flared skirt panels in two rings
        n = 12
        for k in range(n):
            a = (k + 0.5 * ring) / n * math.tau
            x, z = math.sin(a) * rad * 0.6, math.cos(a) * rad * 0.5
            C('body', (x - 2.0, 19.0 - ln, z - 0.5), (4.0, ln, 1.0), mat, rot=(tilt * math.cos(a), 0, -tilt * math.sin(a)), pivot=(x, 19.0, z), params={'seed': 100 + ring * 20 + k})
    C('body', (-4.2, 19.8, -3.2), (8.4, 2.6, 6.4), 'silver', params={'seed': 5})                 # waist band
    C('body', (-1.2, 20.0, -3.7), (2.4, 2.2, 0.8), 'gem')
    # bodice + ice collar
    C('body', (-3.6, 22.4, -2.6), (7.2, 7.6, 5.2), 'bodice', params={'seed': 6})
    C('body', (-5.2, 29.2, -3.0), (10.4, 1.8, 6.0), 'bodice', params={'seed': 7})                # shoulder line
    for k, (x, h, rz) in enumerate(((-4.6, 6.0, 38), (-2.4, 7.4, 16), (0, 8.6, 0), (2.4, 7.4, -16), (4.6, 6.0, -38))):
        C('body', (x - 0.9, 30.4, 1.6), (1.8, h, 1.0), 'icicle', rot=(-14, 0, rz), pivot=(x, 30.4, 2.0), params={'seed': 10 + k})     # radiating collar spikes
    for k in range(12):                                                                        # icicle hem
        a = k / 12 * math.tau
        x, z = math.sin(a) * 6.8, math.cos(a) * 5.4
        bn = f'hem{k}'
        B(bn, 'body', (x, 6, z))
        C(bn, (x - 0.9, -3.0 + (k % 3) * 1.4, z - 0.5), (1.8, 8.0 - (k % 3) * 1.4, 1.0), 'icicle', params={'seed': 20 + k})
    # long train with a sheet of glowing music
    B('train', 'body', (0, 18, 3.6))
    C('train', (-3.8, 2.0, 3.4), (7.6, 17.0, 0.7), 'sheet', rot=(-5, 0, 0), pivot=(0, 18, 3.6))
    for k, nx in enumerate((-2.2, 0.4, 2.0)):
        C('train', (nx - 0.4, 6.0 + k * 3.8, 3.9), (0.8, 0.8, 0.5), 'note')
    # head
    B('head', 'body', (0, 30, 0))
    C('head', (-3.2, 30, -3.2), (6.4, 7.0, 6.4), 'skin', params={'seed': 30})
    C('head', (-3.7, 35.2, -3.7), (7.4, 2.8, 7.4), 'hair', params={'seed': 31})
    C('head', (-3.7, 29.6, -3.8), (1.0, 6.6, 1.4), 'hair'); C('head', (2.7, 29.6, -3.8), (1.0, 6.6, 1.4), 'hair')
    C('head', (-3.7, 28.2, 2.8), (7.4, 8.0, 1.5), 'hair')
    for s in (-1, 1):
        C('head', (s * 1.55 - 0.7, 33.0, -3.35), (1.4, 0.9, 0.5), 'eye', params={'rim': False})   # closed-lid glow
    C('head', (-1.0, 30.6, -3.4), (2.0, 1.6, 0.5), 'mouth')                                    # mid-song
    for k, (x, h, rz, rx) in enumerate(((0, 8.4, 0, -4), (-1.8, 6.6, 18, -6), (1.8, 6.6, -18, -6), (-3.4, 4.6, 36, -8), (3.4, 4.6, -36, -8), (-0.9, 5.0, 8, -22), (0.9, 5.0, -8, -22))):
        C('head', (x - 0.6, 37.6, -0.6 + (k % 2) * 0.6), (1.2, h, 1.2), 'icicle', rot=(rx, 0, rz), pivot=(x, 37.6, 0), params={'seed': 40 + k})      # crown
    C('head', (-3.8, 36.4, -3.9), (7.6, 0.9, 7.8), 'silver')
    C('head', (-0.7, 36.5, -4.3), (1.4, 1.4, 0.6), 'gem')
    for k in range(5):                                                                         # long silver hair (sway)
        x = -3.0 + k * 1.5
        bn = f'hair{k}'
        B(bn, 'head', (x + 0.7, 30, 2.9))
        C(bn, (x, 12.0 + (k % 2) * 2.0, 3.1), (1.5, 18.0 - (k % 2) * 2.0, 1.2), 'hair', params={'seed': 50 + k})
    # arms
    B('arm_r', 'body', (-4.8, 28.4, 0))
    C('arm_r', (-6.0, 18.6, -1.2), (2.4, 10.0, 2.4), 'gown', params={'seed': 60})
    C('arm_r', (-5.9, 16.8, -1.1), (2.2, 2.2, 2.2), 'skin')
    C('arm_r', (-6.6, 26.4, -2.0), (3.6, 2.4, 4.0), 'bodice')                                  # pauldron
    B('baton', 'arm_r', (-4.8, 17.4, -1.6))
    C('baton', (-5.4, 16.0, -1.8), (1.0, 20.0, 1.0), 'ice', params={'seed': 61})                # conductor's baton
    C('baton', (-5.8, 34.4, -2.2), (1.8, 3.2, 1.8), 'tip')
    B('arm_l', 'body', (4.8, 28.4, 0))
    C('arm_l', (3.6, 18.6, -1.2), (2.4, 10.0, 2.4), 'gown', params={'seed': 62})
    C('arm_l', (3.7, 16.8, -1.1), (2.2, 2.2, 2.2), 'skin')
    C('arm_l', (3.0, 26.4, -2.0), (3.6, 2.4, 4.0), 'bodice')
    for s, tag in ((-1, 'r'), (1, 'l')):                                                       # flowing sleeve ribbons
        bn = f'sleeve_{tag}'
        B(bn, f'arm_{tag}', (s * 4.8, 27.5, 0))
        C(bn, (s * 4.8 + s * 1.0 - 0.6, 6.0, -2.8), (1.2, 18.0, 5.6), 'gown', params={'seed': 63 + s})
    # the organ: nine pipes of ice in a half-ring behind her, tips glowing
    B('pipes', 'float', (0, 18, 0))
    for k in range(7):
        a = math.radians(-78 + k * 26)
        x, z = math.sin(a) * 17.0, math.cos(a) * 17.0 + 4.0
        h = 26 + (3 - abs(k - 3)) * 3.0
        C('pipes', (x - 1.1, 4.0, z - 1.1), (2.2, h, 2.2), 'pipe', rot=(0, math.degrees(a), 0), pivot=(x, 4, z), params={'seed': 70 + k})
        C('pipes', (x - 0.9, 4.0 + h, z - 0.9), (1.8, 1.0, 1.8), 'tip', rot=(0, math.degrees(a), 0), pivot=(x, 4, z))
    # drifting snow-crystals (orbit)
    B('orbit', 'float', (0, 24, 0))
    for k in range(8):
        a = k / 8 * math.tau
        r_ = 11 + (k % 3) * 2.2
        C('orbit', (math.cos(a) * r_ - 0.8, 10 + (k * 3.3) % 26, math.sin(a) * r_ - 0.8), (1.6, 3.0, 1.6), 'icicle', rot=(0, math.degrees(a), 20 * math.sin(a)),
          pivot=(math.cos(a) * r_, 12, math.sin(a) * r_), params={'seed': 90 + k})
    return m


# ============================================================================== RIMEWALKER (zombie-like)
def rime_materials():
    skin = R('#26343f', '#3e5262', '#62788a', '#8ea6b6', '#bcd0dc')
    fur = R('#241c18', '#3c302a', '#5e5048', '#84746a')
    frost = R('#7aa8c8', '#a8cce4', '#d8eef8', '#ffffff')
    cloth = R('#1a2634', '#2c4056', '#46627c', '#6a88a4')
    glow = R('#2a90c0', '#6ad4ff', '#b8f0ff', '#ffffff')

    def coat(ctx):
        r, g, b, a, gl = P.make(fur, scale=0.35, base=0.5, amp=0.5, bevel=0.1, seed=421, streak=(1, 0.35))(ctx)
        n = fbm3(ctx.W, 422, 0.5, 3)
        if n > 0.66:                                                    # frost crust
            c = ramp_at(frost, 0.4 + 0.6 * (n - 0.66) * 3)
            return (c[0], c[1], c[2], 255, 0)
        return (r, g, b, a, gl)

    return {
        'skin': P.make(skin, scale=0.45, base=0.55, amp=0.4, bevel=0.1, seed=423), 'coat': coat,
        'cloth': P.make(cloth, scale=0.5, base=0.5, amp=0.4, bevel=0.12, seed=424, streak=(1, 0.4)),
        'ice': P.make(frost, scale=0.4, base=0.7, amp=0.25, bevel=0.2, seed=425, glow_fn=lambda ctx, n, c: (c, 40)),
        'dark': P.make(R('#04080c', '#0a1218', '#141f28'), scale=0.5, base=0.5, amp=0.3, seed=426),
        'eye': solid_glow(glow, 0.6, 1.0, 255, 427, rim=False),
    }


def rimewalker():
    m = Model(RIME_ID, 128, 128, bounds=(1.2, 2.4, (0, 1.1, 0)))
    B, C = m.bone, m.cube
    B('root', None, (0, 0, 0))
    B('body', 'root', (0, 12, 0))
    C('body', (-4, 12, -2), (8, 12, 4), 'skin', params={'seed': 1})
    C('body', (-4.6, 11.4, -2.6), (9.2, 11.6, 5.2), 'coat', params={'seed': 2})                  # fur-lined coat, frosted
    C('body', (-5.4, 21.6, -3.2), (10.8, 3.2, 6.4), 'coat', params={'seed': 3})                  # collar
    C('body', (-4.6, 10.6, -2.8), (9.2, 1.2, 5.6), 'cloth')
    for k in range(3):                                                                         # icicles on the shoulder
        C('body', (-6.0 + k * 0.4, 23.6, -0.8 + k * 0.3), (1.2, 3.8 - k * 0.6, 1.2), 'ice', rot=(0, 0, 20 + k * 12), pivot=(-5.4, 23.6, 0), params={'seed': 4 + k})
    C('body', (3.4, 23.6, -0.6), (1.4, 5.0, 1.4), 'ice', rot=(0, 0, -16), pivot=(4.0, 23.6, 0), params={'seed': 8})
    for k in range(5):                                                                         # tattered coat tails
        bn = f'strip{k}'
        B(bn, 'body', (-4 + k * 2 + 1, 11, -2.9))
        C(bn, (-4 + k * 2, 5.4 - (k % 2) * 1.2, -3.2), (1.8, 6.4 + (k % 2) * 1.2, 0.7), 'coat', params={'seed': 9 + k})
    B('head', 'body', (0, 24, 0))
    C('head', (-4, 24, -4), (8, 8, 8), 'skin', params={'seed': 14})
    C('head', (-4.6, 29.4, -4.6), (9.2, 3.4, 9.2), 'coat', params={'seed': 15})                  # fur hood
    C('head', (-4.6, 24.0, -4.6), (1.4, 6.6, 9.2), 'coat'); C('head', (3.2, 24.0, -4.6), (1.4, 6.6, 9.2), 'coat')
    C('head', (-4.0, 23.0, 3.4), (8.0, 9.0, 1.6), 'coat', rot=(-8, 0, 0), pivot=(0, 30, 4))
    C('head', (-1.8, 24.8, -4.4), (3.6, 1.4, 0.6), 'dark')                                      # slack mouth
    for s in (-1, 1):
        C('head', (s * 1.9 - 1.3, 27.2, -4.25), (2.6, 2.0, 0.5), 'dark')
        C('head', (s * 1.9 - 0.8, 27.6, -4.45), (1.6, 1.0, 0.5), 'eye', params={'rim': False})
    C('head', (-0.5, 31.8, -4.0), (1.0, 4.4, 1.0), 'ice', rot=(-12, 0, 0), pivot=(0, 32, -4))  # horn of ice through the hood
    for s, tag in ((1, 'l'), (-1, 'r')):
        x = 5.4 * s
        B(f'arm_{tag}', 'body', (x, 22, 0))
        C(f'arm_{tag}', (x - 1.8, 11.0, -1.8), (3.6, 11.0, 3.6), 'skin', params={'seed': 20 + s})
        C(f'arm_{tag}', (x - 2.1, 14.4, -2.1), (4.2, 7.0, 4.2), 'coat', params={'seed': 22 + s})
        C(f'arm_{tag}', (x - 1.6, 11.0, -1.6), (3.2, 1.6, 3.2), 'ice')
    for s, tag in ((1, 'l'), (-1, 'r')):
        x = 2.0 * s
        B(f'leg_{tag}', 'body', (x, 12, 0))
        C(f'leg_{tag}', (x - 2, 0, -2), (4, 12, 4), 'cloth', params={'seed': 30 + s})
        C(f'leg_{tag}', (x - 2.3, 5.0, -2.3), (4.6, 4.4, 4.6), 'coat', params={'seed': 32 + s})
        C(f'leg_{tag}', (x - 2.3, 0, -3.0), (4.6, 2.0, 5.2), 'coat')
    return m


# ============================================================================== HOARBONE (skeleton-like archer)
def hoar_materials():
    bone = R('#5a6a74', '#8ea0aa', '#c4d2da', '#e6f0f4', '#fbffff')
    frost = R('#7aa8c8', '#a8cce4', '#d8eef8', '#ffffff')
    fur = R('#222c36', '#3a4856', '#5c6e7e', '#8296a6')
    wood = R('#1c1a24', '#34303f', '#544e68', '#7a7298')
    glow = R('#1c78a8', '#5ac8f0', '#a8ecff', '#ffffff')

    def bone_fn(ctx):
        r, g, b, a, gl = P.make(bone, scale=0.5, base=0.6, amp=0.3, bevel=0.2, seed=431)(ctx)
        n = fbm3(ctx.W, 432, 0.55, 2)
        if n > 0.74:
            c = ramp_at(frost, 0.7 + (n - 0.74))
            return (c[0], c[1], c[2], 255, 20)
        return (r, g, b, a, gl)

    return {
        'bone': bone_fn, 'fur': P.make(fur, scale=0.4, base=0.5, amp=0.5, bevel=0.1, seed=433, streak=(1, 0.4)),
        'ice': P.make(frost, scale=0.4, base=0.72, amp=0.2, bevel=0.2, seed=434, glow_fn=lambda ctx, n, c: (c, 60)),
        'wood': P.make(wood, scale=0.5, base=0.5, amp=0.4, bevel=0.1, seed=435, streak=(1, 0.5)),
        'dark': P.make(R('#03060a', '#080e14', '#10181f'), scale=0.5, base=0.5, amp=0.3, seed=436),
        'eye': solid_glow(glow, 0.65, 1.0, 255, 437, rim=False), 'string': solid_glow(glow, 0.5, 0.9, 200, 438, rim=False),
    }


def hoarbone():
    m = Model(HOAR_ID, 128, 128, bounds=(1.2, 2.6, (0, 1.2, 0)))
    B, C = m.bone, m.cube
    B('root', None, (0, 0, 0))
    B('body', 'root', (0, 12, 0))
    C('body', (-0.9, 12, -0.9), (1.8, 12, 1.8), 'bone')                                           # spine
    for k in range(5):
        w = 7.4 - abs(k - 1.6) * 0.9
        C('body', (-w / 2, 22 - k * 2.2, -2.0), (w, 0.9, 4), 'bone')                              # ribs
    C('body', (-3.4, 10.8, -1.6), (6.8, 2.2, 3.2), 'bone')
    for k, (x, rz) in enumerate(((-3.6, 24), (3.6, -24), (-1.6, 8), (1.6, -8))):                  # ice growing out of the spine
        C('body', (x - 0.6, 20.0 + k * 0.8, 1.8), (1.2, 5.0 - k * 0.6, 1.2), 'ice', rot=(14, 0, rz), pivot=(x, 20, 2), params={'seed': 2 + k})
    C('body', (-5.8, 22.4, -2.8), (11.6, 2.8, 5.6), 'fur', params={'seed': 7})                    # fur mantle over the shoulders
    C('body', (-5.6, 3.0, 2.4), (11.2, 20.0, 0.9), 'fur', rot=(-4, 0, 0), pivot=(0, 24, 2.4), params={'seed': 8})
    for k in range(5):
        bn = f'rag{k}'
        B(bn, 'body', (-5 + k * 2.5 + 1.25, 12, 3.0))
        C(bn, (-5 + k * 2.5, 0.5 + (k % 2) * 1.5, 2.5), (2.4, 11.5 - (k % 2) * 1.5, 0.8), 'fur', params={'seed': 9 + k})
    B('head', 'body', (0, 24, 0))
    C('head', (-4, 24, -4), (8, 8, 8), 'bone', params={'seed': 14})
    C('head', (-4.6, 29.6, -4.6), (9.2, 3.4, 9.2), 'fur', params={'seed': 15})                    # hood
    C('head', (-4.6, 24.6, 3.0), (9.2, 8.0, 1.6), 'fur', rot=(-8, 0, 0), pivot=(0, 30, 4))
    C('head', (-0.8, 25.6, -4.4), (1.6, 1.8, 0.5), 'dark')
    C('head', (-2.8, 24.2, -4.3), (5.6, 1.4, 0.6), 'bone')
    for k in range(5):
        C('head', (-2.6 + k * 1.1, 23.9, -4.5), (0.6, 1.0, 0.4), 'bone')
    for s in (-1, 1):
        C('head', (s * 2.0 - 1.2, 27.4, -4.2), (2.4, 2.2, 0.6), 'dark')
        C('head', (s * 2.0 - 0.7, 27.9, -4.45), (1.4, 1.2, 0.5), 'eye', params={'rim': False})
        C('head', (s * 4.6 - 0.5, 30.4, -1.0), (1.0, 5.6, 1.0), 'ice', rot=(0, 0, -22 * s), pivot=(s * 4.6, 30.4, -0.4), params={'seed': 16})    # antlers of ice
    for s, tag in ((1, 'l'), (-1, 'r')):
        x = 5.4 * s
        B(f'arm_{tag}', 'body', (x, 22, 0))
        C(f'arm_{tag}', (x - 1, 12.8, -1), (2, 10, 2), 'bone')
        B(f'forearm_{tag}', f'arm_{tag}', (x, 13, 0))
        C(f'forearm_{tag}', (x - 1, 3.6, -1), (2, 10, 2), 'bone')
        C(f'forearm_{tag}', (x - 1.5, 3.4, -1.5), (3, 1.5, 3), 'ice')
        C(f'forearm_{tag}', (x - 1.2, 1.2, -1.2), (2.4, 2.6, 2.4), 'bone')
        if tag == 'r':                                                                          # frozen longbow
            B('bow', f'forearm_{tag}', (x, 4, -2))
            C('bow', (x - 0.7, 0.4, -3.4), (1.4, 3.6, 1.4), 'wood')
            C('bow', (x - 0.6, 3.8, -3.9), (1.2, 7, 1.2), 'ice', rot=(18, 0, 0), pivot=(x, 4, -3.4), params={'seed': 20})
            C('bow', (x - 0.6, -7.0, -3.9), (1.2, 7, 1.2), 'ice', rot=(-18, 0, 0), pivot=(x, 0.4, -3.4), params={'seed': 21})
            C('bow', (x - 0.2, -7.6, -1.0), (0.4, 17.6, 0.4), 'string')
    for s, tag in ((1, 'l'), (-1, 'r')):
        x = 2.0 * s
        B(f'leg_{tag}', 'body', (x, 12, 0))
        C(f'leg_{tag}', (x - 1, 6, -1), (2, 6, 2), 'bone')
        B(f'shin_{tag}', f'leg_{tag}', (x, 6, 0))
        C(f'shin_{tag}', (x - 1, 0, -1), (2, 6, 2), 'bone')
        C(f'shin_{tag}', (x - 1.6, 0, -2.4), (3.2, 1.4, 4.4), 'fur')
    return m


MODELS = {
    'frost_cantor': (cantor, cantor_materials, CANTOR_ID),
    'rimewalker': (rimewalker, rime_materials, RIME_ID),
    'hoarbone': (hoarbone, hoar_materials, HOAR_ID),
}
