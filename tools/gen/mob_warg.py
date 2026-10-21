"""Ashen Warg - a hulking obsidian-plated hellhound of the Nether."""
from common import *
from geo import Model
import paint as P

ID = 'geometry.ecr_ashen_warg'


def materials():
    fur = [hx(x) for x in ['#0b0909', '#181211', '#261c1a', '#392a26', '#4e3b34', '#6a5248']]
    plate = [hx(x) for x in ['#050303', '#100808', '#1d0f10', '#31191a', '#4a2624', '#6a3a33']]
    bone = [hx(x) for x in ['#5c5140', '#85795f', '#b0a488', '#d6caae', '#f0e8d0']]
    horn = [hx(x) for x in ['#140c0c', '#271715', '#3c2723', '#583a33', '#7a5448']]
    mouth = [hx(x) for x in ['#2e0707', '#5b0e0b', '#8f1b10', '#c8340f']]
    fur_fn = P.make(fur, scale=0.28, base=0.4, amp=0.5, bevel=0.12, seed=5, streak=(2, 0.35), octaves=3)
    plate_base = P.make(plate, scale=0.2, base=0.35, amp=0.4, bevel=0.35, seed=21)
    return {
        'fur': fur_fn,
        'fur_dark': P.make([c for c in fur[:4]], scale=0.3, base=0.45, amp=0.5, bevel=0.1, seed=6, streak=(2, 0.4)),
        'plate': P.veined(plate_base, PYRELITE, thr=0.03, seed=44, scale=0.17, glow=230),
        'plate_plain': plate_base,
        'bone': P.make(bone, scale=0.5, base=0.55, amp=0.3, bevel=0.2, seed=8),
        'horn': P.make(horn, scale=0.4, base=0.5, amp=0.4, bevel=0.2, seed=9, streak=(1, 0.5)),
        'mouth': P.make(mouth, scale=0.4, base=0.5, amp=0.35, bevel=0.1, seed=10),
        'lava': P.solid_glow(PYRELITE, 0.55, 0.98, 255, 0.45, seed=11),
        'ember': P.solid_glow(PYRELITE, 0.4, 0.8, 190, 0.6, seed=12),
        'eye': P.eyes(hx('#fff0a0'), hx('#ff8a1e')),
    }


def build():
    m = Model(ID, 256, 128, bounds=(3.2, 2.6, (0, 1.2, 0)))
    B = m.bone
    B('root', None, (0, 0, 0))
    B('body', 'root', (0, 17, 0))
    # ------------------------------------------------------------- torso
    m.cube('body', (-5.5, 11, 3), (11, 12, 10), 'fur', params={'seed': 1})            # hips / rump
    m.cube('body', (-6.5, 11, -10), (13, 14, 12), 'fur', params={'seed': 2})           # chest / shoulders
    m.cube('body', (-5.5, 11, -1), (11, 11, 5), 'fur_dark', params={'seed': 3})          # waist
    m.cube('body', (-3.5, 9.5, -8), (7, 2, 14), 'fur_dark')                             # belly
    # spine ridge + obsidian back spikes (shoulder -> hip)
    m.cube('body', (-1.2, 25, -9.5), (2.4, 1.6, 11.5), 'plate_plain')
    m.cube('body', (-1.2, 23, 2), (2.4, 1.6, 11), 'plate_plain')
    for k in range(8):
        z = -8.5 + k * 2.9
        yb = 26.4 if z < 1.5 else 24.4
        h = 6.5 - k * 0.55
        m.cube('body', (-1.4 + k * 0.03, yb, z), (2.8 - k * 0.2, h, 1.8), 'plate', rot=(-20 - k * 1.5, 0, 0), pivot=(0, yb, z + 0.9), params={'seed': k})
    # shoulder pauldrons
    for s in (-1, 1):
        x0 = 6.2 if s > 0 else -10.2
        m.cube('body', (x0, 20.5, -9.5), (4, 4.5, 9), 'plate', rot=(0, 0, -16 * s), pivot=(x0 + 2, 25, -5), params={'seed': 5 + s})
        m.cube('body', (x0 + (0.6 if s > 0 else 0.4), 24.6, -8.5), (3, 2.6, 6), 'plate', rot=(0, 0, -30 * s), pivot=(x0 + 1.5, 25, -5), params={'seed': 7 + s})
        # glowing chest cracks
        m.cube('body', (s * 3.6 - 1.2, 15, -10.4), (2.4, 5, 1), 'lava', params={'rim': False})
    m.cube('body', (-2, 18.5, -10.6), (4, 3, 1), 'ember', params={'rim': False})

    # ------------------------------------------------------------- neck + head
    B('neck', 'body', (0, 23, -9), rot=(12, 0, 0))
    m.cube('neck', (-3.8, 18, -17), (7.6, 8, 9), 'fur', params={'seed': 8})
    m.cube('neck', (-1.2, 26, -15), (2.4, 1.6, 6), 'plate_plain')
    for k in range(3):   # ember mane spikes crowning the neck
        m.cube('neck', (-1.1, 27.4, -15 + k * 2.2), (2.2, 4.8 - k * 0.8, 1.6), 'ember', rot=(-24, 0, 0), pivot=(0, 27.4, -14.2 + k * 2.2), params={'rim': False})
    B('head', 'neck', (0, 22, -16), rot=(-12, 0, 0))
    m.cube('head', (-4.5, 17.5, -25), (9, 8, 9), 'fur', params={'seed': 11})                  # skull
    m.cube('head', (-3, 17.5, -32), (6, 5, 7), 'fur_dark', params={'seed': 12})               # snout
    m.cube('head', (-3.2, 22.4, -32.6), (6.4, 1.2, 6.2), 'plate_plain')                          # nose bridge plate
    m.cube('head', (-1.5, 20.6, -33), (3, 2, 1.5), 'plate_plain')                                # nose pad
    m.cube('head', (-5.2, 24, -24.5), (10.4, 2.5, 5), 'plate', params={'seed': 14})            # brow ridge
    m.cube('head', (-4.8, 26, -19), (9.6, 2, 6), 'plate', params={'seed': 15})                 # crest plate
    for s in (-1, 1):
        m.cube('head', (s * 2.6 - 1.2, 21.6, -25.4), (2.4, 1.6, 1), 'eye', params={'rim': False})
        x0 = 2.6 if s > 0 else -4.6
        m.cube('head', (x0, 26, -18), (2, 5, 2), 'fur', rot=(-8, 0, 12 * s), pivot=(x0 + 1, 26, -17), params={'seed': 20 + s})
        m.cube('head', (x0 + 0.4, 26.4, -18.4), (1.2, 3.6, 0.8), 'mouth', rot=(-8, 0, 12 * s), pivot=(x0 + 1, 26, -17))
        hx0 = 3.6 if s > 0 else -5.6
        m.cube('head', (hx0, 24.6, -22), (2, 4, 2), 'horn', rot=(0, 0, -18 * s), pivot=(hx0 + 1, 24.6, -21), params={'seed': 31 + s})
        m.cube('head', (hx0 + s * 2.9, 27.8, -21.5), (1.6, 4, 1.6), 'horn', rot=(-6, 0, -38 * s), pivot=(hx0 + s * 2.9 + 0.8, 27.8, -20.7))
        m.cube('head', (hx0 + s * 5.9, 30.6, -21.2), (1.2, 3.4, 1.2), 'ember', rot=(-14, 0, -58 * s), pivot=(hx0 + s * 5.9 + 0.6, 30.6, -20.6), params={'rim': False})
        m.cube('head', (s * 2.2 - 0.5, 15.2, -31.6), (1, 2.6, 1), 'bone', params={'seed': 40 + s})
        m.cube('head', (s * 2.9 - 0.5, 16.0, -28.6), (1, 1.8, 1), 'bone')
    B('jaw', 'head', (0, 18, -24.5))
    m.cube('jaw', (-2.6, 15.2, -31.5), (5.2, 2.4, 7), 'fur_dark', params={'seed': 50})
    m.cube('jaw', (-2.0, 17.4, -30.8), (4, 0.8, 5.8), 'mouth')
    m.cube('jaw', (-3.0, 14.4, -32.2), (6, 1.5, 2.5), 'plate_plain')
    for s in (-1, 1):
        m.cube('jaw', (s * 1.9 - 0.5, 17.8, -31.4), (1, 2.4, 1), 'bone')
        m.cube('jaw', (s * 2.3 - 0.5, 17.8, -28.4), (0.8, 1.4, 0.8), 'bone')

    # ------------------------------------------------------------- legs
    def foreleg(s, tag):
        x = 4.0 * s
        up, lo, pw = f'{tag}_upper', f'{tag}_lower', f'{tag}_paw'
        B(up, 'body', (x, 18, -5.5))
        m.cube(up, (x - 2.7, 9.5, -8.3), (5.4, 9.5, 5.6), 'fur', params={'seed': 60 + s})
        m.cube(up, (x - 2.9 + (0.4 * -s), 13.5, -8.6), (5.8, 3, 6.2), 'plate', params={'seed': 62 + s})   # elbow armour
        B(lo, up, (x, 10, -5.5), rot=(4, 0, 0))
        m.cube(lo, (x - 2.2, 2.5, -7.7), (4.4, 7.7, 4.4), 'fur_dark', params={'seed': 64 + s})
        B(pw, lo, (x, 2.5, -5.5))
        m.cube(pw, (x - 2.6, 0, -9.2), (5.2, 2.6, 7.2), 'fur', params={'seed': 66 + s})
        for k in (-1, 0, 1):
            m.cube(pw, (x + k * 1.7 - 0.5, 0, -10.8), (1, 1.2, 2.2), 'bone')

    def hindleg(s, tag):
        x = 4.2 * s
        th, sh, ft = f'{tag}_thigh', f'{tag}_shin', f'{tag}_foot'
        B(th, 'body', (x, 21, 8), rot=(-22, 0, 0))
        m.cube(th, (x - 3, 11.5, 4.6), (6, 10.5, 7), 'fur', params={'seed': 70 + s})
        m.cube(th, (x - 3.2 + (0.4 * -s), 15.5, 4.3), (6.4, 3.4, 7.6), 'plate', params={'seed': 72 + s})
        B(sh, th, (x, 12.5, 6.5), rot=(46, 0, 0))
        m.cube(sh, (x - 2.2, 5.5, 4.8), (4.4, 7.8, 4.4), 'fur_dark', params={'seed': 74 + s})
        B(ft, sh, (x, 6, 9), rot=(-30, 0, 0))
        m.cube(ft, (x - 1.9, 1.8, 7.4), (3.8, 4.8, 3.6), 'fur', params={'seed': 76 + s})
        m.cube(ft, (x - 2.6, 0, 3.6), (5.2, 2.2, 7.4), 'fur', params={'seed': 78 + s})
        for k in (-1, 0, 1):
            m.cube(ft, (x + k * 1.7 - 0.5, 0, 2.2), (1, 1.2, 2.2), 'bone')

    foreleg(1, 'fl'); foreleg(-1, 'fr')
    hindleg(1, 'hl'); hindleg(-1, 'hr')

    # ------------------------------------------------------------- tail
    B('tail1', 'body', (0, 21, 12.5), rot=(34, 0, 0))
    m.cube('tail1', (-2.4, 19, 12), (4.8, 4.8, 9), 'fur', params={'seed': 90})
    B('tail2', 'tail1', (0, 21, 21), rot=(-8, 0, 0))
    m.cube('tail2', (-1.8, 19.4, 20.5), (3.6, 3.6, 8), 'fur_dark', params={'seed': 91})
    B('tail3', 'tail2', (0, 21, 28.5), rot=(-18, 0, 0))
    m.cube('tail3', (-1.2, 19.8, 28), (2.4, 2.4, 5), 'plate_plain')
    m.cube('tail3', (-2.2, 18.6, 31), (4.4, 4.8, 6), 'lava', rot=(0, 0, 45), pivot=(0, 21, 34), params={'rim': False})
    m.cube('tail3', (-1.2, 19.8, 36), (2.4, 2.4, 3), 'ember', params={'rim': False})
    return m
