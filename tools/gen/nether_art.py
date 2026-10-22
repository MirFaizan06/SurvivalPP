"""Sprites and block textures for Roads V and VI (the Burning Deep): key items, seals, consumables, pedestals, the Bridal Anvil, toll bells,
the Grave Altar, ember tablets and the projectiles of the two bosses."""
import math, random
from PIL import Image, ImageDraw
from common import *
from seals_art import spr, stone, glow_dot

H = hx
BLACKSTONE = [H(c) for c in ('#0c0a0e', '#1a161c', '#2c262e', '#443c46', '#62586a')]
BASALT = [H(c) for c in ('#0e0e12', '#1c1c22', '#303038', '#4a4a54', '#686874')]
EMBER_R = [H(c) for c in ('#7a1d00', '#c8400c', '#ff8a24', '#ffd35e', '#fff2b0')]
SOUL_R = [H(c) for c in ('#0a3a6a', '#1c78c8', '#5ac8ff', '#b8f0ff', '#ffffff')]
GOLD_R = [H(c) for c in ('#5a3a08', '#a8781a', '#d9a830', '#f7d466', '#fff0a8')]


# ------------------------------------------------------------------------------------------------ items
def cinder_ring():
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([2, 4, 13, 14], outline=GOLD_R[1] + (255,), width=2)
    d.ellipse([3, 5, 12, 13], outline=GOLD_R[3] + (255,), width=1)
    d.polygon([(6, 1), (9, 1), (10, 4), (5, 4)], fill=EMBER_R[2] + (255,), outline=EMBER_R[0] + (255,))
    im.putpixel((7, 2), EMBER_R[4] + (255,))
    return im


def ember_compass():
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([1, 1, 14, 14], fill=BLACKSTONE[1] + (255,), outline=GOLD_R[1] + (255,))
    d.ellipse([2, 2, 13, 13], outline=GOLD_R[3] + (255,))
    d.ellipse([3, 3, 12, 12], fill=BLACKSTONE[0] + (255,))
    d.polygon([(8, 3), (10, 8), (8, 9), (6, 8)], fill=EMBER_R[2] + (255,))
    d.polygon([(8, 13), (10, 8), (8, 9), (6, 8)], fill=BASALT[3] + (255,))
    im.putpixel((8, 8), EMBER_R[4] + (255,))
    for (x, y) in ((8, 2), (8, 13), (2, 8), (13, 8)):
        im.putpixel((x, y), GOLD_R[4] + (255,))
    return im


def grave_key():
    pal = {'k': H('#0a1a2e'), 'b': H('#1c78c8'), 'c': H('#5ac8ff'), 'w': H('#ffffff'), 's': H('#8a98ac'), 'S': H('#d8e2ee'), 'd': H('#4a5666')}
    return spr(['................', '....kkkk........', '...kcwwck.......', '..kcwbbwck......', '..kcwbbwck......', '...kcwwck.......', '....kkSk........', '.....kSsk.......',
                '......kSsk......', '.......kSsk.....', '........kSdk....', '.......kSsk.....', '........kSsdk...', '.........kkkk...', '................', '................'], pal)


def seal(kind):
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ramp = EMBER_R if kind == 'forge' else SOUL_R
    d.ellipse([1, 1, 14, 14], fill=ramp[0] + (255,))
    d.ellipse([2, 2, 13, 13], fill=ramp[1] + (255,))
    d.ellipse([3, 3, 12, 12], fill=ramp[3] + (255,))
    if kind == 'forge':                                                    # an anvil
        d.rectangle([4, 6, 11, 8], fill=BASALT[1] + (255,))
        d.rectangle([6, 8, 9, 10], fill=BASALT[1] + (255,))
        d.rectangle([5, 10, 10, 11], fill=BASALT[1] + (255,))
        d.polygon([(2, 6), (4, 6), (4, 7), (3, 8)], fill=BASALT[1] + (255,))
        im.putpixel((7, 6), EMBER_R[3] + (255,)); im.putpixel((8, 6), EMBER_R[3] + (255,))
    else:                                                                  # two interlocked rings
        d.ellipse([3, 5, 9, 11], outline=BASALT[1] + (255,))
        d.ellipse([6, 5, 12, 11], outline=BASALT[1] + (255,))
        im.putpixel((8, 4), ramp[4] + (255,))
    return im


def cinder_heart():
    pal = {'k': H('#2a0600'), 'r': H('#7a1d00'), 'o': H('#c8400c'), 'y': H('#ff8a24'), 'w': H('#ffd35e'), 'x': H('#fff2b0')}
    return spr(['................', '................', '...kkk....kkk...', '..kroork..kroor.', '.krooyork.krooyok', '.kroyywok.kroywok', '.kroywxok.krowxok', '.kroywwok.krowwok',
                '..kroyyork.kroyok', '...kroyyorkkroyk.', '....kroyyoyoyk...', '.....kroyyyok....', '......kroyok.....', '.......kook......', '........kk.......', '................'], pal)


def cinder_heart_fixed():
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([2, 3, 8, 9], fill=EMBER_R[1] + (255,)); d.ellipse([7, 3, 13, 9], fill=EMBER_R[1] + (255,))
    d.polygon([(2, 7), (13, 7), (8, 14)], fill=EMBER_R[1] + (255,))
    d.ellipse([4, 4, 7, 7], fill=EMBER_R[2] + (255,)); d.ellipse([8, 4, 11, 7], fill=EMBER_R[2] + (255,))
    d.polygon([(4, 7), (11, 7), (8, 11)], fill=EMBER_R[2] + (255,))
    d.ellipse([5, 4, 6, 5], fill=EMBER_R[4] + (255,))
    for (x, y) in ((3, 2), (12, 1), (8, 1)):
        im.putpixel((x, y), EMBER_R[3] + (255,))
    return im


def soul_ember():
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(4, 9), (11, 9), (10, 14), (5, 14)], fill=BASALT[2] + (255,), outline=BASALT[0] + (255,))
    d.rectangle([3, 8, 12, 9], fill=BASALT[3] + (255,))
    d.polygon([(8, 1), (11, 6), (10, 9), (6, 9), (5, 6)], fill=SOUL_R[1] + (255,))
    d.polygon([(8, 3), (10, 6), (9, 9), (7, 9), (6, 6)], fill=SOUL_R[2] + (255,))
    d.polygon([(8, 5), (9, 7), (8, 9), (7, 7)], fill=SOUL_R[4] + (255,))
    return im


# ------------------------------------------------------------------------------------------------ projectiles
def cinder_bolt():
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if d <= 2.0:
                c, a = EMBER_R[4], 255
            elif d <= 3.6:
                c, a = EMBER_R[3], 255
            elif d <= 5.2:
                c, a = EMBER_R[2], 230
            elif d <= 6.8:
                c, a = EMBER_R[1], 150
            else:
                continue
            im.putpixel((x, y), c + (a,))
    return im


def soul_lance():
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y in range(16):
        for x in range(16):
            d = abs(x - 7.5) / 2.6 + abs(y - 7.5) / 7.0
            if d <= 0.4:
                c, a = SOUL_R[4], 255
            elif d <= 0.9:
                c, a = SOUL_R[2], 255
            elif d <= 1.3:
                c, a = SOUL_R[1], 170
            else:
                continue
            im.putpixel((x, y), c + (a,))
    return im


# ------------------------------------------------------------------------------------------------ block textures
def pedestal_top(kind):
    im = stone(BLACKSTONE, 200 + len(kind), 0.3, 0.35)
    d = ImageDraw.Draw(im)
    d.rectangle([1, 1, 14, 14], outline=BLACKSTONE[4] + (255,))
    d.ellipse([3, 3, 12, 12], fill=BLACKSTONE[0] + (255,), outline=EMBER_R[1] + (255,))
    if kind == 'gold':                                                     # an ingot
        d.polygon([(5, 9), (7, 6), (11, 6), (10, 9)], fill=GOLD_R[3] + (255,), outline=GOLD_R[1] + (255,))
        d.rectangle([5, 9, 10, 10], fill=GOLD_R[2] + (255,))
    elif kind == 'flame':                                                  # a blaze rod
        d.line([(5, 11), (10, 5)], fill=EMBER_R[3] + (255,), width=2)
        d.point((10, 5), fill=EMBER_R[4] + (255,))
    else:                                                                  # a tear
        d.polygon([(7, 4), (10, 8), (8, 11), (6, 8)], fill=H('#c8e8f8') + (255,), outline=H('#7aa8c8') + (255,))
    return im


def pedestal_side(lit):
    im = stone(BLACKSTONE, 210 + (1 if lit else 0), 0.25, 0.35)
    d = ImageDraw.Draw(im)
    for y in (3, 12):
        d.line([(1, y), (14, y)], fill=(BLACKSTONE[4] if not lit else EMBER_R[2]) + (255,))
    if lit:
        d.rectangle([6, 5, 9, 10], fill=EMBER_R[2] + (255,))
    return im


def anvil_top():
    im = stone(BASALT, 220, 0.3, 0.3)
    d = ImageDraw.Draw(im)
    d.rectangle([2, 2, 13, 13], fill=BASALT[1] + (255,), outline=EMBER_R[1] + (255,))
    d.rectangle([5, 5, 10, 10], outline=EMBER_R[2] + (255,))
    d.point((7, 7), fill=EMBER_R[4] + (255,)); d.point((8, 8), fill=EMBER_R[4] + (255,))
    return im


def anvil_side():
    im = stone(BASALT, 221, 0.25, 0.3)
    d = ImageDraw.Draw(im)
    d.rectangle([2, 3, 13, 6], fill=BASALT[1] + (255,), outline=BASALT[4] + (255,))
    d.rectangle([5, 7, 10, 10], fill=BASALT[1] + (255,))
    d.rectangle([3, 11, 12, 13], fill=BASALT[1] + (255,), outline=BASALT[4] + (255,))
    d.line([(3, 4), (12, 4)], fill=EMBER_R[2] + (255,))
    return im


def toll_core():
    im = stone(BASALT, 230, 0.25, 0.3)
    d = ImageDraw.Draw(im)
    d.ellipse([2, 2, 13, 13], fill=BLACKSTONE[0] + (255,), outline=SOUL_R[1] + (255,))
    d.ellipse([4, 4, 11, 11], outline=SOUL_R[2] + (255,))
    d.ellipse([6, 6, 9, 9], fill=SOUL_R[3] + (255,))
    d.point((7, 7), fill=SOUL_R[4] + (255,))
    return im


def toll_bell(n):
    pal = [(EMBER_R, 'ember'), (SOUL_R, 'soul'), ([H(c) for c in ('#3a3630', '#6a6458', '#a69e8a', '#d8d0b8', '#f6f0d8')], 'bone'), ([H(c) for c in ('#2a0a3a', '#5a1a7a', '#9a3ad0', '#c88af0', '#f0d8ff')], 'violet')][n]
    ramp = pal[0]
    im = stone(BASALT, 240 + n, 0.25, 0.3)
    d = ImageDraw.Draw(im)
    for i, w in enumerate([2, 4, 6, 6, 8, 8, 10, 10]):
        y = 3 + i
        x0 = 8 - w // 2
        for x in range(x0, x0 + w):
            im.putpixel((x, y), ramp_at(ramp, 0.4 + 0.45 * ((x - x0) / max(1, w - 1) < 0.5) + 0.05 * i) + (255,))
        im.putpixel((x0, y), ramp[0] + (255,))
    d.ellipse([6, 12, 9, 14], fill=ramp[3] + (255,))
    for k in range(n + 1):                                                 # notches count the bell
        im.putpixel((3 + k * 2, 14), ramp[4] + (255,))
    return im


def grave_altar_top():
    im = stone(BLACKSTONE, 250, 0.3, 0.3)
    d = ImageDraw.Draw(im)
    d.rectangle([1, 1, 14, 14], outline=SOUL_R[1] + (255,))
    d.ellipse([3, 6, 8, 11], outline=SOUL_R[3] + (255,))
    d.ellipse([7, 6, 12, 11], outline=SOUL_R[3] + (255,))
    d.point((8, 4), fill=SOUL_R[4] + (255,))
    return im


def ember_tablet(seed):
    im = stone(BLACKSTONE, 260 + seed, 0.3, 0.3)
    d = ImageDraw.Draw(im)
    d.rectangle([2, 2, 13, 13], outline=BLACKSTONE[3] + (255,))
    rng = random.Random(seed)
    for y in range(4, 12, 2):
        x = 4
        while x < 12:
            w = rng.randint(1, 3)
            d.line([(x, y), (min(12, x + w), y)], fill=(EMBER_R[2] if y % 4 == 0 else EMBER_R[1]) + (255,))
            x += w + 2
    return im
