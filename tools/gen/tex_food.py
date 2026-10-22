"""Procedural sprites: crops (4 growth stages + wild variants), seeds, produce, cooked foods, meats."""
import math, random
from PIL import Image
from common import *
from tex_items import swap_palette

R = lambda *c: [hx(x) for x in c]
GREEN = R('#14310e', '#235c1b', '#3b8a28', '#62b83a', '#92dc5c')
DGREEN = R('#0a1f08', '#143510', '#235a18', '#37801f', '#5aa83a')
RED = R('#4a0a0c', '#8f1519', '#d02a1e', '#ef5a3a', '#ffa08a')
GOLD = R('#5a3a08', '#a86d12', '#e0a41e', '#f7cf4a', '#fff0a0')
TAN = R('#6b4b1e', '#a2762f', '#cfa150', '#ead08a', '#fff0c4')
PINK = R('#6b1230', '#b02a55', '#e0517c', '#f78fae', '#ffd0dd')
ORANGE = R('#5a1a05', '#a8380c', '#e0641a', '#ff9a3c', '#ffd27a')


class Canvas:
    def __init__(self):
        self.im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))

    def px(self, x, y, c):
        if 0 <= x < 16 and 0 <= y < 16:
            self.im.putpixel((int(x), int(y)), tuple(c) + (255,))

    def get(self, x, y):
        return self.im.getpixel((x, y))

    def disc(self, cx, cy, r, ramp, light=(-0.6, -0.7), outline=True):
        pts = set()
        for y in range(16):
            for x in range(16):
                if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r * r:
                    pts.add((x, y))
        for (x, y) in pts:
            nx, ny = (x + 0.5 - cx) / r, (y + 0.5 - cy) / r
            t = 0.55 + 0.45 * -(nx * light[0] + ny * light[1]) / (abs(light[0]) + abs(light[1]) + 1e-6) * 0.9
            self.px(x, y, ramp_at(ramp, max(0.12, min(0.95, t))))
        if outline:
            for (x, y) in pts:
                if any((x + dx, y + dy) not in pts for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    self.px(x, y, ramp[0] if (x + y) % 2 else ramp[1])
        return pts

    def line(self, a, b, col, w=1):
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]), 1) * 2)
        for i in range(n + 1):
            x = a[0] + (b[0] - a[0]) * i / n
            y = a[1] + (b[1] - a[1]) * i / n
            for dx in range(w):
                self.px(round(x) + dx, round(y), col)

    def leaf(self, x, y, dx, dy, length, ramp):
        for i in range(length):
            t = i / max(1, length - 1)
            cx, cy = x + dx * i, y + dy * i - math.sin(t * math.pi) * 0.6
            self.px(round(cx), round(cy), ramp[3 if i % 2 == 0 else 2])
            if 0 < i < length - 1:
                self.px(round(cx), round(cy) + 1, ramp[1])
        self.px(round(x + dx * (length - 1)), round(y + dy * (length - 1)), ramp[4])

    def outline_dark(self, col=(0, 0, 0)):
        src = self.im.copy()
        for y in range(16):
            for x in range(16):
                if src.getpixel((x, y))[3] == 0:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < 16 and 0 <= ny < 16 and src.getpixel((nx, ny))[3] > 0:
                            self.im.putpixel((x, y), (18, 10, 8, 200))
                            break


def seeds_sprite(cols, seed, n=9):
    c = Canvas()
    rng = random.Random(seed)
    spots = [(5, 9), (8, 10), (10, 8), (6, 6), (9, 5), (4, 11), (11, 11), (7, 8), (8, 7)][:n]
    for (x, y) in spots:
        c.px(x, y, cols[1]); c.px(x + 1, y, cols[2]); c.px(x, y - 1, cols[3])
        c.px(x + 1, y + 1, cols[0])
    c.outline_dark()
    return c.im


# ------------------------------------------------------------------ produce items
def tomato():
    c = Canvas()
    c.disc(8, 9.2, 5.3, RED)
    for (x, y) in ((8, 4), (7, 4), (9, 4), (6, 5), (10, 5), (8, 5), (8, 3)):
        c.px(x, y, GREEN[3] if (x, y) != (8, 3) else GREEN[1])
    c.px(7, 5, GREEN[2]); c.px(9, 5, GREEN[2])
    c.px(6, 8, hx('#ffd0c0')); c.px(7, 7, hx('#ffb09a'))
    return c.im


def corn_cob():
    c = Canvas()
    for y in range(2, 13):
        w = 4 if 3 <= y <= 11 else 3
        for x in range(8 - w // 2, 8 + (w + 1) // 2):
            t = 0.5 + 0.35 * (1 if (x + y) % 2 == 0 else -0.4) + (0.1 if x < 8 else -0.15)
            c.px(x, y, ramp_at(GOLD, t))
    for y in range(2, 13, 2):
        for x in (6, 7, 8, 9):
            c.px(x, y, ramp_at(GOLD, 0.25))
    for (x, y, k) in ((6, 10, 3), (9, 10, 3), (5, 12, 3), (10, 12, 3), (7, 13, 2), (8, 13, 2)):
        c.px(x, y, GREEN[k]); c.px(x, y + 1, GREEN[1])
    for y in range(9, 15):
        c.px(8, y, GREEN[3]); c.px(7, y, GREEN[2])
    c.outline_dark()
    return c.im


def strawberry():
    c = Canvas()
    widths = [3, 5, 6, 6, 6, 5, 3, 1]
    for i, w in enumerate(widths):
        y = 5 + i
        for x in range(8 - w // 2 - (w % 2 == 0 and 0), 8 - w // 2 + w):
            t = 0.6 + 0.3 * (0.4 - (x - 7) * 0.1) - 0.1 * i / 8
            c.px(x, y, ramp_at(RED, min(0.92, max(0.2, t))))
    for (x, y) in ((6, 7), (9, 7), (7, 9), (10, 9), (6, 11), (8, 8), (8, 11)):
        c.px(x, y, GOLD[3])
    for (x, y, k) in ((8, 4, 3), (7, 4, 2), (9, 4, 2), (6, 5, 3), (10, 5, 3), (8, 5, 3), (5, 4, 2), (11, 4, 2), (8, 3, 1)):
        c.px(x, y, GREEN[k])
    c.px(6, 6, hx('#ffc0b0'))
    c.outline_dark()
    return c.im


def chili():
    c = Canvas()
    path = [(10, 4), (10, 5), (9, 6), (9, 7), (8, 8), (8, 9), (7, 10), (6, 11), (5, 12), (4, 13)]
    for i, (x, y) in enumerate(path):
        w = 3 if i < 6 else (2 if i < 9 else 1)
        for dx in range(w):
            t = 0.35 + 0.5 * (1 - dx / max(1, w - 1) if w > 1 else 0.5)
            c.px(x - 1 + dx, y, ramp_at(RED, min(0.9, t + 0.1 * (i % 2))))
    c.px(9, 5, hx('#ffb09a')); c.px(9, 6, hx('#ff8f78'))
    for (x, y, k) in ((10, 3, 2), (11, 3, 3), (9, 3, 3), (10, 2, 1), (11, 2, 2)):
        c.px(x, y, GREEN[k])
    c.outline_dark()
    return c.im


def oats():
    c = Canvas()
    for (x0, x1) in ((3, 4), (6, 7), (8, 9), (11, 12)):
        for y in range(14, 6, -1):
            t = (14 - y) / 7
            x = round(x0 + (x1 - x0) * 0 + (x1 - x0) * t * 0.5 + ((x0 - 7.5) * 0.0))
            c.px(x, y, TAN[1] if y % 2 else TAN[2])
        hx_, hy = x0 + (x1 - x0) // 2, 7
        for k in range(5):
            y = hy - k
            c.px(hx_ - 1 + (k % 2) * 2, y, GOLD[3]); c.px(hx_, y, GOLD[2] if k % 2 else GOLD[4])
    for x in range(4, 12):
        c.px(x, 12, TAN[0]); c.px(x, 13, TAN[1])            # twine tie
    c.px(7, 12, RED[2]); c.px(8, 12, RED[2])
    c.outline_dark()
    return c.im


def roasted_corn():
    img = corn_cob()
    px = img.load()
    for y in range(16):
        for x in range(16):
            r, g, b, a = px[x, y]
            if a and r > 160 and g > 130:
                f = 0.62 + 0.14 * ((x * 7 + y * 3) % 3) / 2
                px[x, y] = (int(r * f), int(g * f * 0.85), int(b * 0.4), a)
    for (x, y) in ((6, 4), (9, 7), (7, 10), (8, 3)):
        px[x, y] = hx('#3a1e08') + (255,)
    return img


# ------------------------------------------------------------------ crop stages
def stem(c, x, h, col=GREEN, dark=True):
    for i in range(h):
        c.px(x, 15 - i, col[2] if i % 2 else col[3])
        if dark and x + 1 < 16:
            c.px(x + 1, 15 - i, col[1])


def tomato_stage(s):
    c = Canvas()
    h = (4, 7, 10, 12)[s]
    stem(c, 7, h)
    for i in range(0, h - 1, 3):
        d = -1 if (i // 3) % 2 == 0 else 1
        c.leaf(7 + (d > 0), 14 - i, d, -0.5, 3 + (1 if s > 1 else 0), GREEN)
    if s == 0:
        c.leaf(7, 13, -1, -1, 2, GREEN); c.leaf(8, 13, 1, -1, 2, GREEN)
    if s >= 2:
        c.leaf(7, 5 + (3 - s), -1, 0.2, 3, GREEN); c.leaf(8, 5 + (3 - s), 1, 0.2, 3, GREEN)
    if s == 2:
        for (x, y) in ((5, 9), (10, 8), (9, 11)):
            c.px(x, y, GREEN[3]); c.px(x + 1, y, GREEN[2]); c.px(x, y + 1, GREEN[2]); c.px(x + 1, y + 1, GREEN[1])
    if s == 3:
        for (x, y) in ((4, 9), (10, 8), (9, 12), (5, 12), (11, 11)):
            c.disc(x + 1, y + 1, 1.9, RED, outline=False)
            c.px(x + 1, y - 0, GREEN[3])
    c.outline_dark()
    return c.im


def corn_stage(s):
    c = Canvas()
    h = (4, 8, 12, 15)[s]
    stem(c, 7, h, GREEN)
    stem(c, 8, h - 1, DGREEN, dark=False)
    for i in range(1, h, 3):
        d = -1 if (i // 3) % 2 == 0 else 1
        c.leaf(7 + (d > 0), 14 - i, d, -0.7, 4 if s > 0 else 3, GREEN)
        c.leaf(7 + (d > 0), 14 - i - 1, -d, -0.4, 3, DGREEN)
    if s >= 2:
        c.line((8, 3), (8, 1), GOLD[3]); c.px(7, 2, GOLD[2]); c.px(9, 2, GOLD[2])
    if s == 3:
        for (x, y) in ((5, 8), (10, 6)):
            for k in range(3):
                c.px(x, y + k, GOLD[3 - (k % 2)]); c.px(x + 1, y + k, GOLD[2])
            c.px(x, y + 3, GREEN[3]); c.px(x + 1, y + 3, GREEN[2])
    c.outline_dark()
    return c.im


def strawberry_stage(s):
    c = Canvas()
    n = (2, 3, 4, 5)[s]
    for k in range(n):
        x = 3 + k * 2 + (k % 2)
        y = 14 - (k % 2) * 2
        c.leaf(x, y, 1, -0.6, 3, GREEN); c.leaf(x, y, -1, -0.6, 3, GREEN)
        c.leaf(x, y - 1, 0, -1, 3, DGREEN)
    if s >= 2:
        for (x, y) in ((4, 9), (9, 7), (11, 10), (7, 5)):
            c.px(x, y, hx('#ffffff')); c.px(x - 1, y, hx('#f4f0d8')); c.px(x + 1, y, hx('#f4f0d8')); c.px(x, y - 1, hx('#f4f0d8')); c.px(x, y + 1, GOLD[3])
    if s == 3:
        for (x, y) in ((4, 10), (9, 9), (11, 11), (6, 12), (7, 7)):
            c.disc(x + 0.5, y + 0.5, 1.7, RED, outline=False); c.px(x, y - 1, GREEN[3])
            c.px(x, y, hx('#ffd0c0'))
    c.outline_dark()
    return c.im


def chili_stage(s):
    c = Canvas()
    h = (4, 7, 10, 12)[s]
    stem(c, 7, h, DGREEN)
    for i in range(0, h, 2):
        d = -1 if (i // 2) % 2 == 0 else 1
        c.leaf(7 + (d > 0), 14 - i, d, -0.4, 3, GREEN)
    if s == 0:
        c.leaf(7, 13, -1, -1, 2, GREEN); c.leaf(8, 13, 1, -1, 2, GREEN)
    if s >= 2:
        for (x, y) in ((4, 8), (10, 7), (9, 10)):
            col = GREEN if s == 2 else RED
            for k in range(3):
                c.px(x, y + k, col[3 if s == 2 else 2 + (k % 2)]); c.px(x + 1, y + k, col[2 if s == 2 else 1])
            c.px(x, y + 3, col[1] if s == 2 else RED[0])
    c.outline_dark()
    return c.im


def oats_stage(s):
    c = Canvas()
    h = (4, 8, 11, 13)[s]
    for x0 in (3, 5, 7, 9, 11):
        hh = h - ((x0 // 2) % 2)
        for y in range(hh):
            c.px(x0, 15 - y, (GREEN[3] if s < 2 else (TAN[3] if s == 3 else GREEN[4])) if y % 2 else (GREEN[2] if s < 3 else TAN[2]))
        if s >= 2:
            col = GREEN if s == 2 else GOLD
            for k in range(3 if s == 2 else 4):
                c.px(x0 - 1 + (k % 2) * 2, 15 - hh - k + 1, col[3]); c.px(x0, 15 - hh - k, col[4] if s == 3 else col[3])
    c.outline_dark()
    return c.im


import tex_crops                                   # v1.6: redrawn muted sprites (the functions above are the old ones, kept for reference)
STAGE_FN = tex_crops.STAGE_FN


def wild(name):
    return tex_crops.wild(name)


# ------------------------------------------------------------------ recolours of vanilla sprites
def recolor(src, ramp, lo=0.05, hi=1.0, curve=1.0):
    return swap_palette(load('items/' + src), ramp, None, lo, hi, False, curve)


MEAT_RAW_VENISON = R('#2a0608', '#5b0f14', '#8c1d22', '#b9393c', '#e0766f')
MEAT_COOKED_VENISON = R('#241107', '#4a2410', '#7a3d1b', '#a8602d', '#d4934f')
MEAT_RAW_YAK = R('#2a070a', '#5a1018', '#852024', '#aa3434', '#d06a62')
MEAT_COOKED_YAK = R('#1f1006', '#41210e', '#6c3818', '#965527', '#c78544')
PHEASANT_RAW = R('#5a3a30', '#8f6554', '#c28d78', '#e3b8a0', '#f7dccd')
PHEASANT_COOKED = R('#4a2a10', '#7d4a1e', '#b06f2f', '#d9a04e', '#f2cf88')
SOUP_TOMATO = R('#3b0b0b', '#7f1412', '#c42a1e', '#ec5a3a', '#ffa890')
SOUP_PORRIDGE = R('#4a3a20', '#8a6c3a', '#c29d5c', '#e4cc92', '#fff0cc')
SOUP_CHILI = R('#3a0f05', '#7a2208', '#bf4410', '#ef7a22', '#ffbb66')
SOUP_HUNTER = R('#2a1a0c', '#4f3118', '#7d5129', '#aa7a43', '#d8b077')


WOOD = R('#2a180a', '#4a2e14', '#6e4a22', '#94672f', '#b98a4a')


def bowl_food(ramp, bits=None, steam=True, seed=1):
    c = Canvas()
    rng = random.Random(seed)
    # wooden bowl body
    for y in range(9, 14):
        w = 12 - (y - 9) * 1
        x0 = 8 - w // 2
        for x in range(x0, x0 + w):
            c.px(x, y, ramp_at(WOOD, 0.35 + 0.1 * (y - 9) - (0.1 if x > 8 else 0)))
    for x in range(4, 12):
        c.px(x, 14, WOOD[0])
    # rim + contents
    for y in range(6, 10):
        w = 12 + (1 if y in (7, 8) else 0) - abs(y - 8)
        x0 = 8 - w // 2
        for x in range(x0, x0 + w):
            edge = x in (x0, x0 + w - 1) or y in (6, 9)
            if edge:
                c.px(x, y, ramp_at(WOOD, 0.75 if y < 8 else 0.45))
            else:
                c.px(x, y, ramp_at(ramp, 0.5 + 0.3 * rng.random() * (1 if y < 8 else 0.4)))
    for (x, y) in (bits or []):
        c.px(x, y, ramp_at(ramp, 0.95))
    c.outline_dark()
    if steam:
        for (x, y) in ((6, 4), (7, 3), (9, 4), (10, 3), (8, 2)):
            c.px(x, y, (235, 235, 240))
    return c.im


def build_items():
    out = {}
    out['tomato'] = tomato(); out['corn_cob'] = corn_cob(); out['strawberry'] = strawberry()
    out['chili_pepper'] = chili(); out['oats'] = swap_palette(load('items/wheat.png'), R('#5a4a1e', '#948039', '#c9b45a', '#e8d98c', '#fff8c8'), None, 0.0, 1.0, False); out['roasted_corn'] = roasted_corn()
    out['tomato_seeds'] = seeds_sprite(R('#6b5a2a', '#c9b45a', '#efe08a', '#fff6c0'), 1)
    out['corn_kernels'] = seeds_sprite(R('#8a5a08', '#d9a21c', '#f7cf4a', '#fff0a0'), 2, 8)
    out['strawberry_seeds'] = seeds_sprite(R('#3a1a10', '#7a3a22', '#b86a3a', '#e8a070'), 3)
    out['chili_seeds'] = seeds_sprite(R('#7a6a4a', '#cfc08a', '#f2e8b8', '#ffffff'), 4)
    out['oat_seeds'] = seeds_sprite(R('#6b4b1e', '#a2762f', '#cfa150', '#ead08a'), 5, 7)
    out['raw_venison'] = recolor('beef_raw.png', MEAT_RAW_VENISON)
    out['cooked_venison'] = recolor('beef_cooked.png', MEAT_COOKED_VENISON)
    out['raw_yak_meat'] = recolor('porkchop_raw.png', MEAT_RAW_YAK)
    out['cooked_yak_meat'] = recolor('porkchop_cooked.png', MEAT_COOKED_YAK)
    out['raw_pheasant'] = recolor('chicken_raw.png', PHEASANT_RAW)
    out['cooked_pheasant'] = recolor('chicken_cooked.png', PHEASANT_COOKED)
    out['tomato_soup'] = bowl_food(SOUP_TOMATO, [(6, 7), (9, 7), (8, 8)], seed=1)
    out['porridge'] = bowl_food(SOUP_PORRIDGE, [(7, 7), (10, 7), (8, 8), (6, 8)], steam=True, seed=2)
    out['chili_stew'] = bowl_food(SOUP_CHILI, [(6, 7), (9, 8), (10, 7), (8, 7)], seed=3)
    out['hunters_stew'] = bowl_food(SOUP_HUNTER, [(6, 7), (7, 8), (9, 7), (10, 8), (8, 7)], seed=4)
    out['oat_bread'] = swap_palette(load('items/bread.png'), R('#6b4b1e', '#a2762f', '#cfa150', '#ead08a', '#fff0c4'), None, 0.05, 1.0, False)
    out['berry_pie'] = swap_palette(load('items/pumpkin_pie.png'), R('#4a0a1a', '#8f1535', '#d0304e', '#ef6a7a', '#ffc8c8'), None, 0.05, 1.0, False)
    for n, im in out.items():
        save_png(im, f'{RP}/textures/items/{n}.png')
    return list(out)


def build_stages():
    names = []
    for crop, fn in STAGE_FN.items():
        for s in range(4):
            n = f'{crop}_stage{s}'
            save_png(fn(s), f'{RP}/textures/blocks/{n}.png'); names.append(n)
        n = f'wild_{crop}'
        save_png(wild(crop), f'{RP}/textures/blocks/{n}.png'); names.append(n)
    return names


def build():
    return build_items(), build_stages()


if __name__ == '__main__':
    items, stages = build()
    up_sheet([f'{RP}/textures/items/{n}.png' for n in items], PREVIEW + '/food_items.png', 8, 8)
    up_sheet([f'{RP}/textures/blocks/{n}.png' for n in stages], PREVIEW + '/crop_stages.png', 8, 5)
