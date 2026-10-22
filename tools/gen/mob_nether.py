"""Roads V and VI models (the Burning Deep): Varenna, the Cinder Bride (boss), Corvane, the Ashen Groom (boss) and the Forged Blade.
Glow channel: embers, soul fire, eyes, seams, rings."""
import math
from common import *
from geo import Model, fbm3
import paint as P
from mob_hostiles import solid_glow, R

BRIDE_ID = 'geometry.ecr_cinder_bride'
GROOM_ID = 'geometry.ecr_ashen_groom'
BLADE_ID = 'geometry.ecr_forged_blade'

CHAR = R('#080404', '#160c0c', '#2a1818', '#44282a', '#663c3c')
EMBER = R('#7a1d00', '#c8400c', '#ff8a24', '#ffd35e', '#fff2b0')
LACE = R('#2a2624', '#524a46', '#837a72', '#b8aea4', '#e6ddd0')
ASH = R('#4a403e', '#6e625e', '#948782', '#b9aca6', '#d8ccc4')
IRON = R('#0a0a0e', '#1a1a22', '#32323e', '#52525e', '#7a7a88')
HAIR = R('#050202', '#120808', '#241010', '#3c1c18')
ROSE = R('#3a0608', '#7a0c10', '#b81c20', '#e84a3a')
SOUL = R('#0a3a6a', '#1c78c8', '#5ac8ff', '#b8f0ff', '#ffffff')
BONE = R('#2a2824', '#5a564c', '#908a78', '#c4bda4', '#ece6cc')
COAT = R('#06070a', '#10121a', '#1c202c', '#2c3242')
STEEL = R('#101216', '#262a32', '#444a56', '#6e7686', '#a0a8ba')
VEIL = R('#3a3836', '#68645e', '#9a948c', '#cdc6bc', '#f2ece2')


# ============================================================================== THE CINDER BRIDE
def bride_materials():
    def gown(ctx):
        r, g, b, a, gl = P.make(CHAR, scale=0.4, base=0.5, amp=0.5, bevel=0.14, seed=801, streak=(1, 0.3))(ctx)
        n = fbm3(ctx.W, 802, 0.3, 3)
        if abs(n - 0.5) < 0.022:                                          # glowing cracks in the burnt silk
            c = ramp_at(EMBER, 0.55 + 0.4 * fbm3(ctx.W, 803, 0.7, 2))
            return (c[0], c[1], c[2], 255, 200)
        if n > 0.8:                                                       # scraps of lace
            c = ramp_at(LACE, 0.55)
            return (c[0], c[1], c[2], 255, 0)
        return (r, g, b, a, gl)

    def plate(ctx):
        r, g, b, a, gl = P.make(IRON, scale=0.4, base=0.5, amp=0.4, bevel=0.25, seed=804)(ctx)
        n = fbm3(ctx.W, 805, 0.3, 3)
        if abs(n - 0.5) < 0.02:
            c = ramp_at(EMBER, 0.7)
            return (c[0], c[1], c[2], 255, 180)
        return (r, g, b, a, gl)

    return {
        'gown': gown, 'plate': plate,
        'lace': P.make(LACE, scale=0.5, base=0.55, amp=0.4, bevel=0.12, seed=806, streak=(1, 0.4)),
        'veil': P.make(VEIL, scale=0.5, base=0.6, amp=0.3, bevel=0.08, seed=807, streak=(1, 0.6)),
        'skin': P.make(ASH, scale=0.5, base=0.6, amp=0.25, bevel=0.1, seed=808),
        'hair': P.make(HAIR, scale=0.5, base=0.5, amp=0.4, bevel=0.1, seed=809, streak=(1, 0.5)),
        'iron': P.make(IRON, scale=0.45, base=0.5, amp=0.4, bevel=0.3, seed=810, streak=(1, 0.4)),
        'wood': P.make(R('#1c1008', '#38200e', '#5a3818', '#7c5028'), scale=0.4, base=0.5, amp=0.5, bevel=0.15, seed=811, streak=(1, 0.7)),
        'rose': P.make(ROSE, scale=0.6, base=0.55, amp=0.3, bevel=0.2, seed=812),
        'lip': P.make(R('#3a0a08', '#7a1810', '#b8301c'), scale=0.5, base=0.6, amp=0.2, seed=813),
        'ember': solid_glow(EMBER, 0.55, 1.0, 255, 814, rim=False), 'eye': solid_glow(EMBER, 0.8, 1.0, 255, 815, rim=False),
        'core': solid_glow(EMBER, 0.7, 1.0, 255, 816, rim=True), 'blade': P.make(STEEL, scale=0.5, base=0.6, amp=0.3, bevel=0.3, seed=817),
        'edge': solid_glow(EMBER, 0.45, 0.9, 220, 818, rim=False),
    }


def bride():
    m = Model(BRIDE_ID, 256, 256, bounds=(3.6, 3.8, (0, 1.6, 0)))
    B, C = m.bone, m.cube
    B('root', None, (0, 0, 0))
    B('float', 'root', (0, 0, 0))
    B('body', 'float', (0, 22, 0))
    # skirt: a burnt bell of flared panels with ember hems, three rings
    C('body', (-5.4, 16.0, -4.0), (10.8, 4.0, 8.0), 'gown', params={'seed': 1})
    for ring, (rad, ln, tilt, mat) in enumerate(((5.0, 15.0, 16, 'gown'), (6.2, 16.5, 25, 'lace'), (7.2, 17.0, 33, 'gown'))):
        n = 14
        for k in range(n):
            a = (k + 0.5 * ring) / n * math.tau
            x, z = math.sin(a) * rad * 0.62, math.cos(a) * rad * 0.52
            C('body', (x - 2.1, 19.0 - ln, z - 0.5), (4.2, ln, 1.0), mat, rot=(tilt * math.cos(a), 0, -tilt * math.sin(a)), pivot=(x, 19.0, z), params={'seed': 100 + ring * 20 + k})
            C('body', (x - 2.1, 19.0 - ln - 0.6, z - 0.6), (4.2, 1.0, 1.2), 'ember', rot=(tilt * math.cos(a), 0, -tilt * math.sin(a)), pivot=(x, 19.0, z))
    # bodice: a corset of blackened plate seamed with ember
    C('body', (-3.8, 19.8, -2.8), (7.6, 3.4, 5.6), 'plate', params={'seed': 2})
    C('body', (-3.6, 22.8, -2.6), (7.2, 7.4, 5.2), 'plate', params={'seed': 3})
    for k in range(3):
        C('body', (-2.6 + k * 2.6 - 0.3, 23.0, -2.85), (0.6, 7.0, 0.4), 'ember')
    C('body', (-5.4, 29.2, -3.2), (10.8, 2.2, 6.4), 'plate', params={'seed': 4})
    for s in (-1, 1):
        C('body', (s * 5.4 - 2.2, 28.6, -2.8), (4.4, 1.4, 5.6), 'plate', rot=(0, 0, -12 * s), pivot=(s * 5.4, 30, 0), params={'seed': 5})
        C('body', (s * 5.8 - 0.5, 30.4, -0.5), (1.0, 4.0, 1.0), 'iron', rot=(0, 0, -26 * s), pivot=(s * 5.8, 30.4, 0))
    C('body', (-1.2, 19.9, -3.1), (2.4, 2.4, 0.8), 'core')                                       # the ring-clasp at the waist
    # a long train of burnt silk dragging behind (six chained segments)
    B('train0', 'body', (0, 16, 3.4))
    for k in range(6):
        bn = f'train{k}'
        if k:
            B(bn, f'train{k - 1}', (0, 14 - k * 2.4, 3.4 + k * 5.4))
        C(bn, (-(4.2 + k * 0.5), 12.0 - k * 2.4, 3.2 + k * 5.4), (8.4 + k * 1.0, 1.0, 5.6), 'gown' if k % 2 == 0 else 'lace', params={'seed': 40 + k})
        C(bn, (-(4.2 + k * 0.5), 11.6 - k * 2.4, 3.2 + k * 5.4), (8.4 + k * 1.0, 0.7, 5.6), 'ember') if k % 2 == 1 else None
    # head: ash-pale face behind a black veil, ember eyes, a crown of candle-flame spikes
    B('head', 'body', (0, 31, 0))
    C('head', (-3.2, 30.6, -3.2), (6.4, 7.0, 6.4), 'skin', params={'seed': 20})
    C('head', (-3.5, 33.6, -3.6), (7.0, 4.4, 7.0), 'veil', params={'seed': 21})
    C('head', (-3.7, 35.8, -3.7), (7.4, 2.6, 7.4), 'hair', params={'seed': 22})
    C('head', (-3.8, 29.0, 2.8), (7.6, 9.0, 1.6), 'hair')
    for s in (-1, 1):
        C('head', (s * 1.6 - 0.9, 33.4, -3.45), (1.8, 0.9, 0.5), 'eye', params={'rim': False})
        C('head', (s * 3.6 - 0.6, 29.0, -2.0), (1.2, 8.0, 4.0), 'hair')
    C('head', (-1.0, 31.2, -3.4), (2.0, 0.8, 0.4), 'lip')
    for k, (x, h, rz) in enumerate(((0, 8.0, 0), (-2.0, 6.6, 16), (2.0, 6.6, -16), (-3.6, 5.0, 32), (3.6, 5.0, -32), (-1.0, 5.4, 8), (1.0, 5.4, -8))):
        C('head', (x - 0.7, 38.0, -0.7 + (k % 2) * 0.6), (1.4, h, 1.4), 'iron', rot=(-4, 0, rz), pivot=(x, 38, 0), params={'seed': 30 + k})
        C('head', (x - 0.5 - h * 0.0, 38.0 + h * 0.92, -0.5), (1.0, 1.6, 1.0), 'ember', rot=(-4, 0, rz), pivot=(x, 38, 0))
    C('head', (-3.8, 37.4, -3.9), (7.6, 0.9, 7.8), 'iron')
    for k in range(5):                                                                          # long burnt hair with ember tips (sway)
        x = -3.0 + k * 1.5
        bn = f'hair{k}'
        B(bn, 'head', (x + 0.7, 30, 3.0))
        C(bn, (x, 12.0 + (k % 2) * 2.0, 3.2), (1.5, 18.0 - (k % 2) * 2.0, 1.2), 'hair', params={'seed': 50 + k})
        C(bn, (x, 11.4 + (k % 2) * 2.0, 3.2), (1.5, 1.2, 1.2), 'ember')
    B('veil', 'head', (0, 36, 3.4))
    C('veil', (-3.8, 14.0, 3.7), (7.6, 22.0, 0.5), 'veil', params={'seed': 60})
    C('veil', (-3.8, 13.4, 3.65), (7.6, 0.8, 0.6), 'ember')
    # the halo: a ring of embers burning behind her head
    B('halo', 'head', (0, 33, 3.0))
    for k in range(16):
        a = k / 16 * math.tau
        C('halo', (math.cos(a) * 9.0 - 0.9, 33 + math.sin(a) * 9.0 - 0.9, 3.4), (1.8, 1.8, 0.8), 'ember', params={'rim': False})
    # arms: the right carries the forge-hammer, the left holds the ring and a bouquet of burnt roses
    B('arm_r', 'body', (-4.8, 28.4, 0))
    C('arm_r', (-6.0, 18.4, -1.2), (2.4, 10.4, 2.4), 'gown', params={'seed': 70})
    C('arm_r', (-5.9, 16.6, -1.1), (2.2, 2.2, 2.2), 'skin')
    B('hammer', 'arm_r', (-4.8, 17.2, -1.6))
    C('hammer', (-5.5, 4.0, -2.2), (1.4, 28.0, 1.4), 'wood', params={'seed': 71})
    C('hammer', (-9.0, 30.0, -4.6), (8.0, 6.0, 6.0), 'iron', params={'seed': 72})
    C('hammer', (-9.4, 30.4, -4.2), (8.8, 5.2, 5.2), 'plate', params={'seed': 73})
    C('hammer', (-6.9, 31.0, -4.9), (3.2, 4.0, 0.7), 'core')
    C('hammer', (-6.9, 31.0, 0.0), (3.2, 4.0, 0.7), 'core')
    B('arm_l', 'body', (4.8, 28.4, 0))
    C('arm_l', (3.6, 18.4, -1.2), (2.4, 10.4, 2.4), 'gown', params={'seed': 74})
    C('arm_l', (3.7, 16.6, -1.1), (2.2, 2.2, 2.2), 'skin')
    B('ring', 'arm_l', (4.8, 16.5, -2.0))
    for k in range(12):
        a = k / 12 * math.tau
        C('ring', (4.8 + math.cos(a) * 4.0 - 0.6, 16.5 + math.sin(a) * 4.0 - 0.6, -3.2), (1.2, 1.2, 1.2), 'ember', params={'rim': False})
    for k, (dx, dy, dz) in enumerate(((0, 0, 0), (1.4, 0.8, 0.4), (-1.2, 1.0, -0.4), (0.4, 1.8, 0.8), (-0.4, -0.8, 0.9))):          # bouquet of burnt roses
        C('ring', (3.0 + dx - 0.9, 13.0 + dy, -2.0 + dz - 0.9), (1.8, 1.8, 1.8), 'rose' if k % 2 == 0 else 'ember', params={'seed': 80 + k, 'rim': False} if k % 2 else {'seed': 80 + k})
    for s, tag in ((-1, 'r'), (1, 'l')):
        bn = f'sleeve_{tag}'
        B(bn, f'arm_{tag}', (s * 4.8, 27.5, 0))
        C(bn, (s * 4.8 + s * 1.0 - 0.6, 7.0, -2.8), (1.2, 18.0, 5.6), 'lace', params={'seed': 90 + s})
    # eight forged swords circling her
    B('blades', 'float', (0, 24, 0))
    for k in range(8):
        a = k / 8 * math.tau
        r_ = 13.0 + (k % 2) * 2.0
        y = 8 + (k * 3.7) % 22
        C('blades', (math.cos(a) * r_ - 0.5, y, math.sin(a) * r_ - 0.4), (1.0, 14.0, 0.8), 'blade', rot=(0, math.degrees(a) + 90, 16 * math.sin(a)), pivot=(math.cos(a) * r_, y + 7, math.sin(a) * r_), params={'seed': 100 + k})
        C('blades', (math.cos(a) * r_ - 0.3, y + 0.5, math.sin(a) * r_ - 0.2), (0.6, 12.0, 0.4), 'edge', rot=(0, math.degrees(a) + 90, 16 * math.sin(a)), pivot=(math.cos(a) * r_, y + 7, math.sin(a) * r_))
        C('blades', (math.cos(a) * r_ - 2.0, y - 1.6, math.sin(a) * r_ - 0.5), (4.0, 1.0, 1.0), 'iron', rot=(0, math.degrees(a) + 90, 16 * math.sin(a)), pivot=(math.cos(a) * r_, y + 7, math.sin(a) * r_))
    return m


# ============================================================================== THE ASHEN GROOM
def groom_materials():
    def bone(ctx):
        r, g, b, a, gl = P.make(BONE, scale=0.5, base=0.5, amp=0.4, bevel=0.2, seed=831)(ctx)
        n = fbm3(ctx.W, 832, 0.4, 2)
        if n > 0.78:                                                    # soot
            return (int(r * 0.45), int(g * 0.45), int(b * 0.45), a, 0)
        return (r, g, b, a, gl)

    def coat(ctx):
        r, g, b, a, gl = P.make(COAT, scale=0.4, base=0.5, amp=0.5, bevel=0.12, seed=833, streak=(1, 0.3))(ctx)
        n = fbm3(ctx.W, 834, 0.35, 3)
        if n > 0.76:                                                    # frost-blue mildew of the grave
            c = ramp_at(SOUL, 0.18 + (n - 0.76))
            return (c[0], c[1], c[2], 255, 0)
        return (r, g, b, a, gl)

    def plate(ctx):
        r, g, b, a, gl = P.make(STEEL, scale=0.4, base=0.4, amp=0.4, bevel=0.28, seed=835)(ctx)
        n = fbm3(ctx.W, 836, 0.28, 3)
        if abs(n - 0.5) < 0.02:
            c = ramp_at(SOUL, 0.7)
            return (c[0], c[1], c[2], 255, 170)
        return (r, g, b, a, gl)

    return {
        'bone': bone, 'coat': coat, 'plate': plate,
        'trim': P.make(R('#1c2a3a', '#3a566e', '#6a90ae', '#a8cce4'), scale=0.5, base=0.6, amp=0.3, bevel=0.3, seed=837),
        'veil': P.make(VEIL, scale=0.5, base=0.6, amp=0.3, bevel=0.08, seed=838, streak=(1, 0.6)),
        'steel': P.make(STEEL, scale=0.5, base=0.6, amp=0.3, bevel=0.3, seed=839, streak=(1, 0.3)),
        'dark': P.make(R('#020304', '#06080a', '#0e1216'), scale=0.5, base=0.5, amp=0.3, seed=840),
        'rose': P.make(ROSE, scale=0.6, base=0.55, amp=0.3, bevel=0.2, seed=841),
        'soul': solid_glow(SOUL, 0.55, 1.0, 255, 842, rim=False), 'eye': solid_glow(SOUL, 0.8, 1.0, 255, 843, rim=False),
        'rune': solid_glow(SOUL, 0.4, 0.8, 220, 844, rim=False), 'core': solid_glow(SOUL, 0.7, 1.0, 255, 845, rim=True),
    }


def groom():
    m = Model(GROOM_ID, 256, 256, bounds=(2.4, 4.0, (0, 1.8, 0)))
    B, C = m.bone, m.cube
    B('root', None, (0, 0, 0))
    B('body', 'root', (0, 18, 0))
    # ribcage and spine, with the soul-fire heart
    C('body', (-1.2, 18, -1.2), (2.4, 16, 2.4), 'bone')
    for k in range(6):
        w = 11.0 - abs(k - 2.0) * 1.2
        C('body', (-w / 2, 33.0 - k * 2.6, -2.8), (w, 1.1, 5.6), 'bone')
    C('body', (-4.8, 14.6, -2.2), (9.6, 3.2, 4.4), 'bone')                                       # pelvis
    C('body', (-2.2, 24.0, -3.2), (4.4, 6.0, 3.2), 'core')                                       # the soul-fire heart
    C('body', (-3.0, 23.4, -3.6), (6.0, 0.8, 2.0), 'rune')
    # tailcoat: front lapels, waistcoat, back tails (sway)
    C('body', (-5.8, 22.6, -3.6), (3.6, 12.0, 0.9), 'coat', rot=(0, 0, 4), pivot=(-4, 34, -3.6), params={'seed': 2})
    C('body', (2.2, 22.6, -3.6), (3.6, 12.0, 0.9), 'coat', rot=(0, 0, -4), pivot=(4, 34, -3.6), params={'seed': 3})
    C('body', (-5.6, 33.4, -3.6), (11.2, 2.2, 7.2), 'coat', params={'seed': 4})
    for k in range(6):
        bn = f'coat{k}'
        x = -5.4 + k * 2.2
        B(bn, 'body', (x + 1.1, 16, 3.0))
        C(bn, (x, 0.0 + (k % 2) * 2.0, 2.6), (2.2, 17.0 - (k % 2) * 2.0, 1.0), 'coat', params={'seed': 10 + k})
        C(bn, (x, 0.0 + (k % 2) * 2.0, 2.5), (2.2, 0.8, 1.1), 'trim')
    C('body', (-1.0, 26.0, -3.9), (0.8, 6.0, 0.4), 'trim')                                       # waistcoat buttons
    C('body', (3.2, 31.6, -4.2), (2.0, 2.0, 1.0), 'rose', params={'seed': 5})                    # boutonniere
    # pauldrons
    for s in (-1, 1):
        C('body', (s * 7.4 - 3.4, 32.2, -3.6), (6.8, 3.0, 7.2), 'plate', rot=(0, 0, -14 * s), pivot=(s * 7.4, 34, 0), params={'seed': 6})
        C('body', (s * 8.2 - 0.9, 34.4, -0.9), (1.8, 5.6, 1.8), 'plate', rot=(0, 0, -22 * s), pivot=(s * 8.2, 34.4, 0), params={'seed': 7})
        C('body', (s * 8.2 - 0.5, 38.4, -0.5), (1.0, 2.2, 1.0), 'soul', rot=(0, 0, -22 * s), pivot=(s * 8.2, 34.4, 0), params={'rim': False})
    # head: skull under a battered top hat with a soul flame
    B('head', 'body', (0, 35, 0))
    C('head', (-4.4, 35, -4.4), (8.8, 9.0, 8.8), 'bone', params={'seed': 20})
    C('head', (-4.6, 34.4, -4.6), (9.2, 1.4, 9.2), 'bone')
    for k in range(5):
        C('head', (-3.0 + k * 1.5, 34.4, -4.9), (0.8, 1.4, 0.5), 'bone')                       # teeth
    C('head', (-0.9, 38.2, -4.7), (1.8, 2.0, 0.6), 'dark')
    for s in (-1, 1):
        C('head', (s * 2.2 - 1.4, 40.0, -4.6), (2.8, 2.4, 0.6), 'dark')
        C('head', (s * 2.2 - 0.8, 40.4, -4.9), (1.6, 1.4, 0.6), 'eye', params={'rim': False})
    C('head', (-6.4, 43.6, -6.4), (12.8, 1.0, 12.8), 'coat', params={'seed': 21})                 # the hat's brim
    C('head', (-4.6, 44.4, -4.6), (9.2, 10.0, 9.2), 'coat', params={'seed': 22})
    C('head', (-4.8, 44.6, -4.8), (9.6, 1.8, 9.6), 'trim')
    for k, (dx, h) in enumerate(((0, 6.0), (-1.6, 4.0), (1.6, 3.6))):                            # soul fire licking the hat
        C('head', (dx - 0.8, 54.4, -0.8), (1.6, h, 1.6), 'soul', params={'rim': False})
    # arms: right carries the greatsword, left is wrapped in the Bride's veil
    for s, tag in ((1, 'l'), (-1, 'r')):
        x = 8.0 * s
        up, lo = f'arm_{tag}', f'forearm_{tag}'
        B(up, 'body', (x, 33, 0))
        C(up, (x - 1.4, 20.4, -1.4), (2.8, 13.0, 2.8), 'bone')
        C(up, (x - 2.4, 22.6, -2.4), (4.8, 8.0, 4.8), 'plate', params={'seed': 30 + s})
        B(lo, up, (x, 20, 0))
        C(lo, (x - 1.4, 8.0, -1.4), (2.8, 12.4, 2.8), 'bone')
        C(lo, (x - 2.2, 10.0, -2.2), (4.4, 6.0, 4.4), 'plate', params={'seed': 32 + s})
        C(lo, (x - 1.2, 5.4, -1.2), (2.4, 3.2, 2.4), 'bone')
    B('sword', 'forearm_r', (-8.0, 7, -2))
    C('sword', (-8.8, 4.0, -3.4), (1.6, 6.0, 1.6), 'dark')                                       # grip
    C('sword', (-12.4, 9.6, -4.0), (8.8, 1.4, 2.8), 'steel')                                     # guard
    for k in range(10):
        a = k / 10 * math.tau
        C('sword', (-8.0 + math.cos(a) * 2.6 - 0.4, 10.3 + math.sin(a) * 2.6 - 0.4, -4.4), (0.8, 0.8, 0.8), 'soul', params={'rim': False})   # ring on the guard
    C('sword', (-9.2, 11.0, -3.6), (2.4, 38.0, 1.2), 'steel', params={'seed': 40})               # the greatsword blade
    C('sword', (-8.8, 14.0, -3.8), (1.6, 30.0, 0.5), 'rune')
    C('sword', (-9.2, 49.0, -3.6), (2.4, 3.6, 1.2), 'steel')
    B('veil_l', 'forearm_l', (8.0, 18, 0))
    C('veil_l', (6.4, -2.0, -2.8), (3.0, 20.0, 5.6), 'veil', params={'seed': 50})                # her veil, trailing from his arm
    C('veil_l', (6.4, -2.6, -2.8), (3.0, 0.8, 5.6), 'rune')
    C('veil_l', (6.8, 7.0, -2.4), (2.4, 2.4, 0.6), 'core')                                       # the ring on his finger
    # legs
    for s, tag in ((1, 'l'), (-1, 'r')):
        x = 3.2 * s
        B(f'leg_{tag}', 'body', (x, 17, 0))
        C(f'leg_{tag}', (x - 1.4, 8.0, -1.4), (2.8, 10.0, 2.8), 'bone')
        C(f'leg_{tag}', (x - 2.2, 10.0, -2.2), (4.4, 6.0, 4.4), 'plate', params={'seed': 60 + s})
        B(f'shin_{tag}', f'leg_{tag}', (x, 8, 0))
        C(f'shin_{tag}', (x - 1.4, 0.0, -1.4), (2.8, 8.4, 2.8), 'bone')
        C(f'shin_{tag}', (x - 2.2, 1.0, -2.2), (4.4, 6.0, 4.4), 'plate', params={'seed': 62 + s})
        C(f'shin_{tag}', (x - 2.4, 0.0, -3.6), (4.8, 1.8, 6.0), 'dark')
    # soul wisps circling him
    B('orbit', 'body', (0, 30, 0))
    for k in range(8):
        a = k / 8 * math.tau
        r_ = 12 + (k % 3) * 2.0
        C('orbit', (math.cos(a) * r_ - 1.1, 12 + (k * 4.6) % 34, math.sin(a) * r_ - 1.1), (2.2, 2.2, 2.2), 'soul', params={'rim': False})
    return m


# ============================================================================== FORGED BLADE (a floating sword)
def blade_materials():
    return {
        'steel': P.make(STEEL, scale=0.5, base=0.6, amp=0.3, bevel=0.3, seed=861, streak=(1, 0.3)), 'iron': P.make(IRON, scale=0.5, base=0.5, amp=0.4, bevel=0.3, seed=862),
        'edge': solid_glow(EMBER, 0.5, 1.0, 255, 863, rim=False), 'core': solid_glow(EMBER, 0.7, 1.0, 255, 864, rim=False),
    }


def blade():
    m = Model(BLADE_ID, 64, 64, bounds=(1.0, 2.0, (0, 0.8, 0)))
    B, C = m.bone, m.cube
    B('root', None, (0, 0, 0))
    B('body', 'root', (0, 14, 0))
    C('body', (-1.1, 14.0, -0.5), (2.2, 15.0, 1.0), 'steel', params={'seed': 1})
    C('body', (-0.5, 15.0, -0.7), (1.0, 13.0, 0.5), 'edge')
    C('body', (-0.5, 29.0, -0.5), (1.0, 2.0, 1.0), 'steel')
    C('body', (-3.0, 12.6, -0.7), (6.0, 1.4, 1.4), 'iron')
    C('body', (-0.7, 8.0, -0.7), (1.4, 4.6, 1.4), 'iron')
    C('body', (-1.1, 6.6, -1.1), (2.2, 1.6, 2.2), 'core', params={'rim': False})
    return m


MODELS = {
    'cinder_bride': (bride, bride_materials, BRIDE_ID),
    'ashen_groom': (groom, groom_materials, GROOM_ID),
    'forged_blade': (blade, blade_materials, BLADE_ID),
}
