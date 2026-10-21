"""Models + painters for the four new animals: Meadow Deer, Highland Yak, Wild Boar, Pheasant."""
import math
from common import *
from geo import Model, fbm3
import paint as P

R = lambda *c: [hx(x) for x in c]


def _spots(base_fn, spot_ramp, thresh=0.74, scale=0.55, seed=3, ymin=17.0, belly=15.5, belly_ramp=None):
    """fur with light dapples on the back and a pale belly"""
    def fn(ctx):
        r, g, b, a, gl = base_fn(ctx)
        W = ctx.W
        if belly_ramp is not None and ctx.cube.params.get('belly') and W[1] < belly and ctx.face != 'up':
            n = fbm3(W, seed + 5, 0.5, 2)
            c = ramp_at(belly_ramp, 0.45 + 0.4 * n)
            return (c[0], c[1], c[2], 255, 0)
        if W[1] > ymin and ctx.face in ('up', 'east', 'west', 'north', 'south') and ctx.cube.params.get('spots', True):
            n = fbm3(W, seed, scale, 2)
            if n > thresh:
                c = ramp_at(spot_ramp, 0.55 + 0.4 * (n - thresh) * 4)
                return (c[0], c[1], c[2], 255, 0)
        return (r, g, b, a, gl)
    return fn


# ============================================================================== MEADOW DEER
DEER_ID = 'geometry.ecr_meadow_deer'


def deer_materials():
    fur = R('#2c1a0d', '#47291a', '#6a4326', '#8b5c33', '#ae7b45', '#c99a62')
    white = R('#9d9684', '#c4bda9', '#e3dcc9', '#f6f1e2')
    dark = R('#0a0807', '#15110e', '#241c16', '#352a21')
    antler = R('#3a2c1c', '#5e4a30', '#8c7550', '#b9a27a', '#e0cfa6')
    base = P.make(fur, scale=0.3, base=0.5, amp=0.42, bevel=0.1, seed=41, streak=(2, 0.35))
    return {
        'fur': _spots(base, white, 0.76, 0.6, 7, ymin=16.5, belly=16.0, belly_ramp=white),
        'fur_plain': base,
        'white': P.make(white, scale=0.5, base=0.6, amp=0.3, bevel=0.1, seed=42),
        'dark': P.make(dark, scale=0.5, base=0.5, amp=0.3, bevel=0.1, seed=43),
        'antler': P.make(antler, scale=0.5, base=0.5, amp=0.4, bevel=0.2, seed=44, streak=(1, 0.5)),
        'eye': P.eyes((12, 8, 6), (40, 26, 18), 0),
        'ear_in': P.make(R('#6a3a3a', '#a06a66', '#d29a94'), scale=0.6, base=0.5, amp=0.3, seed=45),
    }


def deer():
    m = Model(DEER_ID, 128, 128, bounds=(2.2, 2.4, (0, 1.1, 0)))
    B = m.bone
    B('root', None, (0, 0, 0))
    B('body', 'root', (0, 17, 0))
    m.cube('body', (-4, 14, -8), (8, 8.5, 16), 'fur', params={'seed': 1, 'belly': True})
    m.cube('body', (-4.3, 14.4, -9), (8.6, 9, 7), 'fur', params={'seed': 2, 'belly': True})         # chest
    m.cube('body', (-4, 14.2, 5), (8, 8, 5), 'fur', params={'seed': 3, 'belly': True})              # rump
    m.cube('body', (-1.5, 17.5, 9.5), (3, 3.5, 1.5), 'white', params={'spots': False})   # white tail patch
    # tail
    B('tail', 'body', (0, 21, 10))
    m.cube('tail', (-1.2, 18.8, 10), (2.4, 4, 2), 'white', rot=(-24, 0, 0), pivot=(0, 21, 10), params={'spots': False})
    # neck + head
    B('neck', 'body', (0, 21, -8))
    m.cube('neck', (-2.2, 21, -10.5), (4.4, 6, 4.4), 'fur', rot=(24, 0, 0), pivot=(0, 21, -8.5), params={'spots': False})
    m.cube('neck', (-2.4, 14.6, -11), (4.8, 7, 3), 'white', rot=(24, 0, 0), pivot=(0, 21, -9), params={'spots': False})
    B('head', 'neck', (0, 27, -12))
    m.cube('head', (-2.5, 26.5, -17), (5, 5, 6), 'fur_plain', params={'seed': 11})
    m.cube('head', (-1.7, 26.5, -21), (3.4, 3.4, 4.4), 'fur_plain', params={'seed': 12})
    m.cube('head', (-1.8, 25.4, -21.2), (3.6, 1.4, 4.6), 'white')                      # pale muzzle underside
    m.cube('head', (-1.2, 27.6, -21.8), (2.4, 2.0, 1.0), 'dark')                         # nose
    for s in (-1, 1):
        m.cube('head', (s * 2.45 - 0.5, 29.4, -15.2), (1, 1, 0.8), 'eye', params={'rim': False})
        x0 = 2.2 if s > 0 else -4.2
        m.cube('head', (x0, 31, -13), (2, 4, 1.2), 'fur_plain', rot=(0, 0, -28 * s), pivot=(x0 + 1, 31, -12.4), params={'seed': 14 + s})
        m.cube('head', (x0 + 0.4, 31.4, -13.2), (1.2, 3, 0.6), 'ear_in', rot=(0, 0, -28 * s), pivot=(x0 + 1, 31, -12.4))
    # antlers (stag only: toggled with the ecr:stag property)
    for s, nm in ((1, 'antler_l'), (-1, 'antler_r')):
        B(nm, 'head', (s * 1.4, 31.5, -13.5))
        x = s * 1.4
        m.cube(nm, (x - 0.6, 31.5, -14), (1.2, 5, 1.2), 'antler', rot=(-6, 0, -12 * s), pivot=(x, 31.5, -13.4))
        m.cube(nm, (x + s * 1.4 - 0.5, 35.8, -14.6), (1, 4.5, 1), 'antler', rot=(-14, 0, -26 * s), pivot=(x + s * 1.4, 35.8, -14))
        m.cube(nm, (x + s * 3.0 - 0.5, 39, -15.6), (1, 3.4, 1), 'antler', rot=(-18, 0, -40 * s), pivot=(x + s * 3.0, 39, -15))
        m.cube(nm, (x + s * 0.4 - 0.4, 34.4, -15.8), (0.8, 3, 0.8), 'antler', rot=(-48, 0, -8 * s), pivot=(x + s * 0.4, 34.4, -14.8))
        m.cube(nm, (x + s * 2.0 - 0.4, 37.4, -16.4), (0.8, 2.6, 0.8), 'antler', rot=(-50, 0, -22 * s), pivot=(x + s * 2.0, 37.4, -15.6))
    # legs
    def leg(tag, x, z, back):
        up, lo = f'leg_{tag}', f'leg_{tag}_lower'
        B(up, 'body', (x, 16, z))
        m.cube(up, (x - 1.7, 8.5, z - 1.8), (3.4, 8.6, 3.6), 'fur', params={'seed': 20, 'spots': False})
        B(lo, up, (x, 8.5, z))
        m.cube(lo, (x - 1.2, 1.6, z - 1.2), (2.4, 7.2, 2.4), 'fur_plain', params={'seed': 21})
        m.cube(lo, (x - 1.4, 0, z - 1.6), (2.8, 1.8, 3.4), 'dark')
    leg('fl', 2.6, -6.3, False); leg('fr', -2.6, -6.3, False)
    leg('bl', 2.6, 7.2, True); leg('br', -2.6, 7.2, True)
    return m


# ============================================================================== HIGHLAND YAK
YAK_ID = 'geometry.ecr_highland_yak'


def yak_materials():
    fur = R('#0d0a08', '#1a140f', '#2a2018', '#3c2f23', '#54402f', '#6d5440')
    pale = R('#3a2e24', '#574634', '#7a644a', '#a08764')
    horn = R('#2a2218', '#4d4030', '#7d6a4c', '#b09c74', '#dccfa6')
    dark = R('#050403', '#0d0a08', '#1a1511')
    base = P.make(fur, scale=0.28, base=0.45, amp=0.5, bevel=0.08, seed=51, streak=(1, 0.32), octaves=3)

    def shaggy(ctx):
        r, g, b, a, gl = base(ctx)
        # hair strands: darker vertical streak lines
        if int(ctx.W[0] * 1.3 + ctx.W[2] * 0.7) % 3 == 0 and ctx.face in ('north', 'south', 'east', 'west'):
            return (int(r * 0.72), int(g * 0.72), int(b * 0.72), a, gl)
        return (r, g, b, a, gl)
    return {
        'fur': shaggy, 'pale': P.make(pale, scale=0.35, base=0.5, amp=0.4, bevel=0.1, seed=52, streak=(1, 0.4)),
        'horn': P.make(horn, scale=0.4, base=0.5, amp=0.35, bevel=0.2, seed=53, streak=(1, 0.5)),
        'dark': P.make(dark, scale=0.5, base=0.5, amp=0.3, seed=54),
        'eye': P.eyes((20, 14, 8), (60, 40, 24), 0), 'nose': P.make(R('#1a1210', '#2e211b', '#4a362a'), scale=0.6, base=0.5, amp=0.3, seed=55),
    }


def yak():
    m = Model(YAK_ID, 128, 128, bounds=(3.0, 2.6, (0, 1.2, 0)))
    B = m.bone
    B('root', None, (0, 0, 0))
    B('body', 'root', (0, 17, 0))
    m.cube('body', (-6, 11, -9), (12, 12, 18), 'fur', params={'seed': 1})
    m.cube('body', (-5, 20, -6), (10, 5, 11), 'fur', params={'seed': 2})              # shoulder hump
    m.cube('body', (-6.4, 7, -8), (12.8, 6, 16), 'fur', params={'seed': 3})            # shaggy skirt
    for k in range(7):                                                                    # hanging hair panels
        z = -8 + k * 2.4
        m.cube('body', (-7.0, 3.5 + (k % 3) * 0.8, z), (1.2, 6, 2.2), 'fur', params={'seed': 10 + k})
        m.cube('body', (5.8, 3.5 + ((k + 1) % 3) * 0.8, z), (1.2, 6, 2.2), 'fur', params={'seed': 20 + k})
    B('tail', 'body', (0, 20, 9.5))
    m.cube('tail', (-1.4, 12, 9.5), (2.8, 9, 2.8), 'fur', rot=(-10, 0, 0), pivot=(0, 20, 9.5), params={'seed': 30})
    # head
    B('head', 'body', (0, 22, -10))
    m.cube('head', (-3.5, 15.5, -17), (7, 8, 8), 'fur', params={'seed': 31})
    m.cube('head', (-3, 14.5, -20), (6, 6, 4), 'pale', params={'seed': 32})            # muzzle
    m.cube('head', (-2.4, 14.4, -20.6), (4.8, 3, 1), 'nose')
    for s in (-1, 1):
        m.cube('head', (s * 3.45 - 0.5, 20.4, -17.2), (1, 1.2, 1), 'eye', params={'rim': False})
        x0 = 3.0 if s > 0 else -5.0
        m.cube('head', (x0, 21.5, -13.6), (2, 3, 1.6), 'fur', rot=(0, 0, -20 * s), pivot=(x0 + 1, 21.5, -13), params={'seed': 33 + s})
        # sweeping horns (4 segments curving out, forward and up)
        hx_ = s * 3.6
        m.cube('head', (hx_ - 1, 22, -15.5), (2, 2, 2), 'horn', params={'seed': 34})
        m.cube('head', (hx_ + s * 1.8 - 0.9, 22.6, -15.2), (1.8, 1.8, 2), 'horn', rot=(0, 0, -20 * s), pivot=(hx_ + s * 1.8, 23, -14.6))
        m.cube('head', (hx_ + s * 3.8 - 0.8, 23.8, -15.4), (1.6, 1.6, 2), 'horn', rot=(0, 0, -45 * s), pivot=(hx_ + s * 3.8, 24.2, -14.8))
        m.cube('head', (hx_ + s * 5.2 - 0.6, 26.4, -16.2), (1.2, 3.2, 1.4), 'horn', rot=(-20, 0, -30 * s), pivot=(hx_ + s * 5.2, 26.4, -15.5))
    # legs (short, thick)
    def leg(tag, x, z):
        up, lo = f'leg_{tag}', f'leg_{tag}_lower'
        B(up, 'body', (x, 12, z))
        m.cube(up, (x - 2.2, 6, z - 2.4), (4.4, 7, 4.8), 'fur', params={'seed': 40})
        B(lo, up, (x, 6, z))
        m.cube(lo, (x - 1.9, 1.4, z - 2), (3.8, 5.4, 4), 'pale', params={'seed': 41})
        m.cube(lo, (x - 2.2, 0, z - 2.4), (4.4, 1.6, 4.8), 'dark')
    leg('fl', 3.6, -6.2); leg('fr', -3.6, -6.2); leg('bl', 3.6, 6.5); leg('br', -3.6, 6.5)
    return m


# ============================================================================== WILD BOAR
BOAR_ID = 'geometry.ecr_wild_boar'


def boar_materials():
    fur = R('#14100d', '#241b14', '#38291d', '#503b29', '#6b5038', '#86684a')
    pink = R('#4a2a2a', '#7a4545', '#a86a68', '#d09a94')
    tusk = R('#7a6e58', '#b0a285', '#dcd0b0', '#f6eed2')
    dark = R('#060403', '#100c09', '#1c150f')
    base = P.make(fur, scale=0.3, base=0.45, amp=0.5, bevel=0.1, seed=61, streak=(2, 0.4))
    return {
        'fur': base, 'pink': P.make(pink, scale=0.6, base=0.5, amp=0.3, seed=62),
        'tusk': P.make(tusk, scale=0.5, base=0.6, amp=0.3, bevel=0.2, seed=63),
        'bristle': P.make(R('#050403', '#0d0a08', '#1a140f', '#2a2018'), scale=0.6, base=0.5, amp=0.4, seed=64),
        'dark': P.make(dark, scale=0.5, base=0.5, amp=0.3, seed=65), 'eye': P.eyes((200, 40, 20), (90, 10, 6), 120),
    }


def boar():
    m = Model(BOAR_ID, 128, 64, bounds=(2.2, 1.6, (0, 0.7, 0)))
    B = m.bone
    B('root', None, (0, 0, 0))
    B('body', 'root', (0, 11, 0))
    m.cube('body', (-4.5, 6.5, -6.5), (9, 9, 14), 'fur', params={'seed': 1})
    m.cube('body', (-5, 7.2, -8), (10, 9.5, 7), 'fur', params={'seed': 2})
    m.cube('body', (-4.2, 6.5, 5), (8.4, 8, 5), 'fur', params={'seed': 3})
    for k in range(7):                                                                  # bristle ridge
        z = -7 + k * 2.1
        m.cube('body', (-0.7, 15.2 + (0.3 if k < 3 else 0), z), (1.4, 3.2 - abs(k - 2) * 0.35, 1.6), 'bristle', rot=(-14, 0, 0), pivot=(0, 15.2, z + 0.8))
    B('tail', 'body', (0, 13, 10))
    m.cube('tail', (-0.7, 11, 10), (1.4, 4, 1.4), 'pink', rot=(-24, 0, 0), pivot=(0, 13, 10))
    m.cube('tail', (-0.7, 10.4, 11.6), (1.4, 1.4, 2), 'dark')
    B('head', 'body', (0, 12, -8))
    m.cube('head', (-3.8, 6, -14), (7.6, 7.2, 7), 'fur', params={'seed': 11})
    m.cube('head', (-2.4, 6, -19), (4.8, 4.2, 5.5), 'pink', params={'seed': 12})          # snout
    m.cube('head', (-2.6, 6.8, -20), (5.2, 3.2, 1), 'pink', params={'seed': 13})
    m.cube('head', (-1.9, 7.8, -20.6), (1.2, 1.2, 0.8), 'dark'); m.cube('head', (0.7, 7.8, -20.6), (1.2, 1.2, 0.8), 'dark')
    m.cube('head', (-3.6, 12.6, -10.5), (7.2, 2, 4), 'bristle')                          # mane
    for s in (-1, 1):
        m.cube('head', (s * 3.45 - 0.5, 10, -12.6), (1, 1, 1), 'eye', params={'rim': False})
        m.cube('head', (s * 2.7 - 0.5, 5.6, -18.8), (1, 3.4, 1.2), 'tusk', rot=(-14, 0, 8 * s), pivot=(s * 2.7, 6, -18.2))
        m.cube('head', (s * 3.0 - 0.45, 8.4, -18.4), (0.9, 1.6, 1), 'tusk')
        x0 = 2.4 if s > 0 else -4.4
        m.cube('head', (x0, 13, -11), (2, 3.2, 1.6), 'fur', rot=(0, 0, -22 * s), pivot=(x0 + 1, 13, -10.4), params={'seed': 14 + s})
    def leg(tag, x, z):
        up, lo = f'leg_{tag}', f'leg_{tag}_lower'
        B(up, 'body', (x, 8, z))
        m.cube(up, (x - 1.6, 3.5, z - 1.8), (3.2, 5.2, 3.6), 'fur', params={'seed': 20})
        B(lo, up, (x, 3.5, z))
        m.cube(lo, (x - 1.3, 0.8, z - 1.4), (2.6, 3, 2.8), 'fur', params={'seed': 21})
        m.cube(lo, (x - 1.4, 0, z - 1.6), (2.8, 1, 3.2), 'dark')
    leg('fl', 2.8, -4.8); leg('fr', -2.8, -4.8); leg('bl', 2.8, 7); leg('br', -2.8, 7)
    return m


# ============================================================================== PHEASANT
PHEASANT_ID = 'geometry.ecr_pheasant'


def pheasant_materials():
    bronze = R('#3a1a08', '#63300f', '#8f4c1a', '#bb7430', '#dba24f', '#f0c877')
    green = R('#04231a', '#0a4a34', '#118a5e', '#1fc088', '#6af0c0')
    red = R('#4a0606', '#9a1212', '#d62020', '#ff5a4a')
    white = R('#a39b88', '#cdc5b0', '#ebe5d0', '#fbf8ea')
    tail = R('#3a2410', '#6a4420', '#a06a32', '#d09a52')
    base = P.make(bronze, scale=0.5, base=0.5, amp=0.42, bevel=0.08, seed=71)

    def barred(ctx):
        r, g, b, a, gl = base(ctx)
        if int(ctx.W[2] * 1.2 + 40) % 4 == 0:
            return (int(r * 0.7), int(g * 0.7), int(b * 0.7), a, gl)
        return (r, g, b, a, gl)

    def tailfn(ctx):
        c = ramp_at(tail, 0.5 + 0.4 * fbm3(ctx.W, 73, 0.6, 2))
        if int(ctx.W[2] * 1.1 + 40) % 3 == 0:
            c = tuple(int(v * 0.6) for v in c)
        if ctx.j >= ctx.h - 1:
            c = (230, 215, 190)
        return (c[0], c[1], c[2], 255, 0)
    return {
        'body': barred, 'green': P.make(green, scale=0.6, base=0.55, amp=0.35, bevel=0.1, seed=72),
        'red': P.make(red, scale=0.6, base=0.5, amp=0.3, seed=74), 'white': P.make(white, scale=0.5, base=0.6, amp=0.2, seed=75),
        'tail': tailfn, 'beak': P.make(R('#6a5a20', '#a89030', '#d8c050'), scale=0.6, base=0.5, amp=0.2, seed=76),
        'leg': P.make(R('#3a2a1a', '#5c4630', '#7e6244'), scale=0.6, base=0.5, amp=0.2, seed=77),
        'eye': P.eyes((255, 220, 60), (20, 12, 6), 0),
    }


def pheasant():
    m = Model(PHEASANT_ID, 64, 64, bounds=(1.2, 1.4, (0, 0.5, 0)))
    B = m.bone
    B('root', None, (0, 0, 0))
    B('body', 'root', (0, 7, 0))
    m.cube('body', (-2.5, 5, -4), (5, 5, 8), 'body', params={'seed': 1})
    m.cube('body', (-2.9, 5.5, -4.5), (5.8, 4.2, 3), 'body', params={'seed': 2})
    m.cube('body', (-2, 4.4, -3), (4, 1, 6), 'white')
    B('neck', 'body', (0, 9, -4))
    m.cube('neck', (-1.2, 8.4, -5.6), (2.4, 4.2, 2.4), 'green', params={'seed': 3})
    m.cube('neck', (-1.4, 8.8, -5.8), (2.8, 0.8, 2.8), 'white')                          # white collar
    B('head', 'neck', (0, 12, -4.8))
    m.cube('head', (-1.5, 11.5, -7.2), (3, 3, 3), 'green', params={'seed': 4})
    m.cube('head', (-0.8, 11.6, -9), (1.6, 1.2, 2), 'beak')
    m.cube('head', (-1.6, 11.8, -7.4), (3.2, 1.6, 1.4), 'red')                            # red face patch
    for s in (-1, 1):
        m.cube('head', (s * 1.55 - 0.3, 13, -6.2), (0.6, 0.6, 0.6), 'eye', params={'rim': False})
    m.cube('head', (-0.4, 14.4, -6), (0.8, 1.6, 1.2), 'green', rot=(-20, 0, 0), pivot=(0, 14.4, -5.4))
    B('tail', 'body', (0, 8, 4))
    for k in range(5):
        a = (k - 2) * 9
        m.cube('tail', (-0.7, 6.6, 3.5), (1.4, 1.2, 9 - abs(k - 2)), 'tail', rot=(-6 + abs(k - 2) * 2, a, 0), pivot=(0, 7.2, 3.8))
    for s, nm in ((1, 'wing_l'), (-1, 'wing_r')):
        B(nm, 'body', (s * 2.7, 9, -1))
        m.cube(nm, (s * 2.7 - (0 if s > 0 else 0.9), 5.2, -2.6), (0.9, 3.8, 6), 'body', params={'seed': 6 + s})
        m.cube(nm, (s * 2.7 - (0 if s > 0 else 0.9), 4.8, 0.4), (0.9, 2.4, 3.6), 'tail')
    for s, nm in ((1, 'leg_l'), (-1, 'leg_r')):
        B(nm, 'body', (s * 1.2, 5, 0))
        m.cube(nm, (s * 1.2 - 0.4, 0.4, -0.4), (0.8, 4.8, 0.8), 'leg')
        m.cube(nm, (s * 1.2 - 1, 0, -1.8), (2, 0.6, 2.6), 'leg')
    return m


MODELS = {
    'meadow_deer': (deer, deer_materials, DEER_ID),
    'highland_yak': (yak, yak_materials, YAK_ID),
    'wild_boar': (boar, boar_materials, BOAR_ID),
    'pheasant': (pheasant, pheasant_materials, PHEASANT_ID),
}
