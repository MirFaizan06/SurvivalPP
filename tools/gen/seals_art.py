"""Hand-built sprites and block textures for Chapters III and IV: shards and essence, seals, the Keeper's lantern, tuning fork,
projectiles, particle sprites, and the textures of the puzzle blocks (verse stones, chimes, sconces, altars, tablets)."""
import math, random
from PIL import Image, ImageDraw
from common import *


def spr(rows, pal):
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row[:16]):
            if ch in pal:
                im.putpixel((x, y), pal[ch] + (255,))
    return im


H = hx


# ------------------------------------------------------------------------------------------------ items
def glacial_shard():
    pal = {'k': H('#0a2a4a'), 'b': H('#1c70b0'), 'c': H('#40b4e8'), 'd': H('#8ee0ff'), 'w': H('#ffffff')}
    return spr(['................', '.......kk.......', '......kwwk......', '.....kwcdck.....', '....kwcddcbk....', '....kcdddcbk....', '...kcdddddcbk...', '...kcdddddcbk...',
                '...kbcdddcbbk...', '....kbcdcbbk....', '....kbbcbbk.....', '.....kbbbk......', '......kbk.......', '.......k........', '................', '................'], pal)


def rime_shard():
    pal = {'k': H('#1c2a3a'), 'b': H('#4a6a88'), 'c': H('#86a8c4'), 'd': H('#c2dcee'), 'w': H('#ffffff')}
    return spr(['................', '................', '.......kk.......', '......kcck......', '.....kcddck.....', '.....kdwdbk.....', '....kcdddbbk....', '....kcddbbk.....',
                '.....kcbbk......', '......kbk.......', '.......k........', '................', '................', '................', '................', '................'], pal)


def wisp_essence():
    pal = {'k': H('#1c4a1c'), 'g': H('#4aa83a'), 'h': H('#9ae070'), 'w': H('#f0ffc8')}
    return spr(['................', '......kkkk......', '....kkggggkk....', '...kgghhhhggk...', '..kghhwwwwhhgk..', '..kghwwwwwwhgk..', '..kghwwwwwwhgk..', '..kghhwwwwhhgk..',
                '...kgghhhhggk...', '....kkggggkk....', '.....kkggkk.....', '......kggk......', '.......kk.......', '................', '................', '................'], pal)


def tuning_fork():
    pal = {'k': H('#2a303a'), 's': H('#8a98ac'), 'S': H('#e2eaf4'), 'b': H('#5a6a80'), 'c': H('#8ee0ff')}
    return spr(['................', '...kk......kk...', '..kSSk....kSSk..', '..ksSk....kSsk..', '..ksSk....kSsk..', '..ksSk....kSsk..', '..ksSk....kSsk..', '..kssk....kssk..',
                '..kbsk....kskb..', '...kbsk..kskb...', '....kbskksbk....', '.....kbssbk.....', '......kSSk......', '......ksSk......', '......kckk......', '.......kk.......'], pal)


def seal(kind):
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if kind == 'choir':
        rim, mid, fill, mark = H('#0a2a4a'), H('#40b4e8'), H('#bfe6ff'), H('#ffffff')
    else:
        rim, mid, fill, mark = H('#3a2a08'), H('#d9a830'), H('#fff0a8'), H('#ffffff')
    d.ellipse([1, 1, 14, 14], fill=rim)
    d.ellipse([2, 2, 13, 13], fill=mid)
    d.ellipse([3, 3, 12, 12], fill=fill)
    if kind == 'choir':                                                     # snowflake
        for dx, dy in ((0, -4), (0, 4), (-4, 0), (4, 0), (-3, -3), (3, 3), (-3, 3), (3, -3)):
            im.putpixel((8 + dx // 2 if dx else 8, 8 + dy // 2 if dy else 8), mark + (255,)) if False else None
        for k in range(6):
            a = k / 6 * math.tau
            for r in (1, 2, 3, 4):
                x, y = 7.5 + math.cos(a) * r, 7.5 + math.sin(a) * r
                im.putpixel((int(round(x)), int(round(y))), mark + (255,)) if r < 4 else im.putpixel((int(round(x)), int(round(y))), H('#40b4e8') + (255,))
    else:                                                                   # lantern
        for y in range(4, 12):
            for x in range(6, 10):
                im.putpixel((x, y), H('#a8781a') + (255,)) if y in (4, 11) else im.putpixel((x, y), H('#ffe27a') + (255,))
        im.putpixel((7, 3), rim + (255,)); im.putpixel((8, 3), rim + (255,))
        for y in (7, 8):
            im.putpixel((7, y), mark + (255,)); im.putpixel((8, y), mark + (255,))
    for (x, y) in ((8, 0), (8, 15), (0, 8), (15, 8)):
        pass
    return im


def keepers_lantern():
    pal = {'k': H('#1c1812'), 'g': H('#a8781a'), 'y': H('#ffd85a'), 'Y': H('#fff4b0'), 'm': H('#9ae070')}
    return spr(['................', '.......kk.......', '......k..k......', '.....k....k.....', '....kkkkkkkk....', '...kgyyyyyygk...', '...kgyymmyygk...', '...kgymYYmygk...',
                '...kgymYYmygk...', '...kgyymmyygk...', '...kgyyyyyygk...', '....kkkkkkkk....', '.....kg..gk.....', '......kkkk......', '................', '................'], pal)


# ------------------------------------------------------------------------------------------------ projectiles
def note_sprite():
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    glow = [hx(c) for c in ('#0a2a4a', '#1c70b0', '#40b4e8', '#8ee0ff', '#ffffff')]
    cx = cy = 7.5
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - cx, y - cy)
            if d <= 7.0:
                a = int(max(0, 150 - d * 22))
                im.putpixel((x, y), glow[1] + (a,))
    d = ImageDraw.Draw(im)
    d.ellipse([3, 9, 7, 13], fill=glow[3] + (255,), outline=glow[0] + (255,))               # note head
    d.rectangle([7, 3, 8, 11], fill=glow[4] + (255,))                                       # stem
    d.polygon([(8, 3), (12, 5), (12, 8), (8, 6)], fill=glow[3] + (255,), outline=glow[2] + (255,))   # flag
    return im


def wisp_bolt_sprite():
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    pal = [hx(c) for c in ('#1c4a1c', '#4aa83a', '#9ae070', '#f0ffc8', '#ffffff')]
    cx = cy = 7.5
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - cx, y - cy)
            if d <= 2.0:
                c, a = pal[4], 255
            elif d <= 3.6:
                c, a = pal[3], 255
            elif d <= 5.2:
                c, a = pal[2], 230
            elif d <= 6.6:
                c, a = pal[1], 150
            else:
                continue
            im.putpixel((x, y), c + (a,))
    return im


# ------------------------------------------------------------------------------------------------ particle sprites
def glow_dot(col, size=16, hard=0.25):
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    c = (size - 1) / 2
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - c, y - c) / c
            if d <= 1:
                a = 1.0 if d < hard else max(0.0, 1 - (d - hard) / (1 - hard)) ** 1.6
                im.putpixel((x, y), tuple(col[:3]) + (int(255 * a),))
    return im


def snow_sprite():
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for k in range(6):
        a = k / 6 * math.tau
        for r in range(0, 6):
            x, y = 7.5 + math.cos(a) * r, 7.5 + math.sin(a) * r
            im.putpixel((int(round(x)), int(round(y))), (235, 248, 255, 255 if r < 5 else 160))
        for sg in (-1, 1):
            x, y = 7.5 + math.cos(a) * 3.5 + math.cos(a + sg * 1.0) * 1.6, 7.5 + math.sin(a) * 3.5 + math.sin(a + sg * 1.0) * 1.6
            im.putpixel((int(round(x)), int(round(y))), (200, 232, 255, 220))
    return im


def ring_sprite():
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if 5.0 <= d <= 7.4:
                a = 1 - abs(d - 6.2) / 1.2
                im.putpixel((x, y), (255, 255, 255, int(255 * max(0, a))))
    return im


# ------------------------------------------------------------------------------------------------ block textures
def stone(ramp, seed, lo=0.3, span=0.42):
    rng = random.Random(seed)
    g = [[rng.random() for _ in range(16)] for _ in range(16)]
    im = Image.new('RGBA', (16, 16))
    px = im.load()
    for y in range(16):
        for x in range(16):
            v = g[y][x] * 0.5 + g[(y + 1) % 16][x] * 0.2 + g[y][(x + 1) % 16] * 0.2 + g[(y + 1) % 16][(x + 1) % 16] * 0.1
            t = lo + span * v
            if x in (0, 15) or y in (0, 15):
                t *= 0.82 if (x == 15 or y == 15) else 1.1
            px[x, y] = ramp_at(ramp, min(1.0, t)) + (255,)
    return im


SLATE = [hx(c) for c in ('#10161c', '#1e2830', '#34424e', '#4e6070', '#6c8294')]
FROST_STONE = [hx(c) for c in ('#1a2a3a', '#2e4660', '#4c6e90', '#7ea4c4', '#bcd8ec')]
MOSS_STONE = [hx(c) for c in ('#0e1a12', '#1c3022', '#2e4a34', '#476a48', '#6a9264')]
BELL = [hx(c) for c in ('#3a2a10', '#7a5a1e', '#b8902c', '#e6c456', '#fff0a0')]


def verse_stone(verse):
    """a frost-rimed standing stone with a glowing rune: rising sun / high sun / setting sun / moon"""
    im = stone(FROST_STONE, 70 + verse, 0.25, 0.5)
    d = ImageDraw.Draw(im)
    rune = hx('#bff0ff')
    glow = hx('#6ad4ff')
    if verse == 0:
        d.arc([4, 6, 11, 13], 180, 360, fill=rune)
        d.line([(3, 11), (12, 11)], fill=glow)
        d.point((7, 4), fill=glow); d.point((3, 7), fill=glow); d.point((12, 7), fill=glow)
    elif verse == 1:
        d.ellipse([5, 4, 10, 9], outline=rune)
        d.point((7, 6), fill=rune)
        for p in ((7, 2), (7, 11), (2, 6), (12, 6), (3, 3), (11, 3), (3, 9), (11, 9)):
            d.point(p, fill=glow)
    elif verse == 2:
        d.arc([4, 6, 11, 13], 180, 360, fill=rune)
        d.line([(3, 11), (12, 11)], fill=glow)
        d.line([(5, 4), (6, 5)], fill=glow); d.line([(10, 4), (9, 5)], fill=glow)
    else:
        d.ellipse([4, 3, 11, 10], fill=rune)
        d.ellipse([6, 2, 13, 9], fill=FROST_STONE[1] + (255,))                      # carve the crescent
        for p in ((3, 12), (11, 12), (8, 13), (13, 4)):
            d.point(p, fill=glow)
    return im


def bell_plate(gem_ramp, seed):
    im = stone(SLATE, seed, 0.28, 0.35)
    d = ImageDraw.Draw(im)
    for (x, y) in ((1, 1), (14, 1), (1, 14), (14, 14)):
        d.point((x, y), fill=BELL[3] + (255,))
    widths = [2, 4, 6, 6, 8, 8, 10, 10]
    for i, w in enumerate(widths):
        y = 3 + i
        x0 = 8 - w // 2
        for x in range(x0, x0 + w):
            t = 0.35 + 0.5 * ((x - x0) / max(1, w - 1) < 0.5) + 0.1 * (i / 8)
            im.putpixel((x, y), ramp_at(BELL, min(1.0, t)) + (255,))
        im.putpixel((x0, y), BELL[0] + (255,)); im.putpixel((x0 + w - 1, y), BELL[1] + (255,))
    for x in range(3, 13):
        im.putpixel((x, 11), BELL[1] + (255,))
    d.ellipse([6, 12, 9, 14], fill=ramp_at(gem_ramp, 0.8) + (255,), outline=gem_ramp[0] + (255,))
    d.ellipse([7, 5, 9, 7], fill=ramp_at(gem_ramp, 0.9) + (255,))                    # the gem in the bell
    im.putpixel((7, 5), (255, 255, 255, 255))
    return im


def sconce(symbol, lit):
    im = stone(MOSS_STONE, 90 + len(symbol) + (5 if lit else 0), 0.25, 0.4)
    d = ImageDraw.Draw(im)
    d.rectangle([3, 3, 12, 12], fill=hx('#06100a') + (255,), outline=hx('#1c3022') + (255,))
    on = lit
    c1 = hx('#ffe27a') if on else hx('#3a4a3a')
    c2 = hx('#fffbd0') if on else hx('#2a382a')
    if symbol == 'eye':
        d.line([(4, 8), (7, 5), (8, 5), (11, 8)], fill=c1)
        d.line([(4, 8), (7, 11), (8, 11), (11, 8)], fill=c1)
        d.rectangle([7, 7, 8, 9], fill=c2)
    elif symbol == 'star':
        pts = [(8 + math.cos(-math.pi / 2 + k * 2 * math.pi / 5) * 4.2, 8 + math.sin(-math.pi / 2 + k * 2 * math.pi / 5) * 4.2) for k in range(5)]
        order = [0, 2, 4, 1, 3, 0]
        for a, b in zip(order, order[1:]):
            d.line([pts[a], pts[b]], fill=c1)
        d.point((8, 8), fill=c2)
    else:
        d.ellipse([5, 4, 11, 10], fill=c1)
        d.ellipse([7, 3, 13, 9], fill=hx('#06100a') + (255,))
        d.point((6, 7), fill=c2)
        d.point((10, 12), fill=c1); d.point((4, 11), fill=c1)
    if on:
        for (x, y) in ((2, 2), (13, 2), (2, 13), (13, 13)):
            d.point((x, y), fill=hx('#ffe27a') + (255,))
    return im


def altar_top(ramp, mark, seed):
    im = stone(ramp, seed, 0.4, 0.4)
    d = ImageDraw.Draw(im)
    d.rectangle([1, 1, 14, 14], outline=ramp[1] + (255,))
    mark(d)
    return im


def tablet(seed):
    im = stone(SLATE, seed, 0.3, 0.3)
    d = ImageDraw.Draw(im)
    d.rectangle([2, 2, 13, 13], outline=SLATE[1] + (255,))
    rng = random.Random(seed)
    for y in range(4, 12, 2):
        x = 4
        while x < 12:
            w = rng.randint(1, 3)
            d.line([(x, y), (min(12, x + w), y)], fill=hx('#7ac8e8') + (255,) if y % 4 == 0 else hx('#5aa0c0') + (255,))
            x += w + 2
    return im
