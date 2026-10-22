"""Crop growth-stage sprites (16x16) in a muted, vanilla-like style: straight 1 px stems, small two-tone leaves, no heavy outline.
v1.6: redrawn - the first version used a saturated palette, a noisy checker shading and a black outline, and the blocks rendered
without face dimming, so the plants glowed against the farmland."""
from PIL import Image
from common import hx

LEAF = [hx(c) for c in ('#1f3a14', '#2f5a1c', '#43782a', '#5c9638')]          # dark .. light
OAT = [hx(c) for c in ('#5a4a1c', '#8a7430', '#b49c46', '#d6c068')]
RED = [hx(c) for c in ('#5a120f', '#8f1e18', '#c2322a', '#e0604a')]
CHILI = [hx(c) for c in ('#1c3a10', '#2e5c1a', '#3f7a22', '#58963a')]
GOLD = [hx(c) for c in ('#6a4a10', '#a8801c', '#d6aa32', '#f0cf60')]
HUSK = [hx(c) for c in ('#2a4a18', '#3e6a24', '#5a8c36', '#7ab04a')]
WHITE = [hx('#d8d4bc'), hx('#f2eed6'), hx('#fffbe8')]
STEM = hx('#2a4a1a')


class C:
    def __init__(self):
        self.im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))

    def p(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < 16 and 0 <= y < 16:
            self.im.putpixel((x, y), tuple(c) + (255,))

    def has(self, x, y):
        return 0 <= x < 16 and 0 <= y < 16 and self.im.getpixel((x, y))[3] > 0

    def vline(self, x, y0, y1, col):
        for y in range(min(y0, y1), max(y0, y1) + 1):
            self.p(x, y, col)

    def leaf(self, x, y, d, n, pal, droop=0.0, rise=0.35):
        """a leaf of n pixels leaving (x, y) in direction d (+1 right / -1 left): dark base, light tip, shaded underside"""
        for i in range(n):
            t = i / max(1, n - 1)
            cx = x + d * (i + 1)
            cy = y - rise * (i + 1) + droop * (i + 1) * (i + 1) * 0.18
            self.p(cx, cy, pal[1] if i == 0 else pal[2 if t < 0.7 else 3])
            if 0 < i < n - 1:
                self.p(cx, round(cy) + 1, pal[0])
        return

    def disc(self, cx, cy, pal, big=False):
        """berry / tomato: 2x2 or 3x3 with highlight top-left"""
        r = 3 if big else 2
        for dy in range(r):
            for dx in range(r):
                if big and dx in (0, 2) and dy in (0, 2):
                    continue
                self.p(cx + dx, cy + dy, pal[2])
        for dx in range(r):
            self.p(cx + dx, cy + r - 1, pal[1])
        self.p(cx + r - 1, cy + r - 1, pal[0] if big else pal[1])
        self.p(cx, cy + (0 if not big else 0), pal[3]) if not big else self.p(cx + 1, cy, pal[3])

    def shade(self):
        """one-pixel darker rim on the lower-right edge so sprites read against the farmland without a black outline"""
        src = self.im.copy()
        for y in range(16):
            for x in range(16):
                if src.getpixel((x, y))[3] == 0:
                    continue
                if (x + 1 < 16 and src.getpixel((x + 1, y))[3] == 0) and (y + 1 >= 16 or src.getpixel((x, y + 1))[3] == 0):
                    r, g, b, a = src.getpixel((x, y))
                    self.im.putpixel((x, y), (int(r * 0.78), int(g * 0.78), int(b * 0.78), a))
        return self.im


# ----------------------------------------------------------------------------------------------- tomato
def tomato(s):
    c = C()
    top = (11, 8, 5, 3)[s]                                     # y of the plant's top, stems grow from y=15
    c.vline(7, top, 15, STEM)
    c.vline(8, top + 2, 15, LEAF[0]) if s >= 2 else None
    if s == 0:
        c.leaf(7, 14, -1, 2, LEAF); c.leaf(7, 14, 1, 2, LEAF)
    else:
        for k, y in enumerate(range(15, top, -3)):
            d = -1 if k % 2 == 0 else 1
            c.leaf(7, y - 1, d, 3 if s >= 2 else 2, LEAF, droop=0.4)
            if s >= 2:
                c.leaf(8, y - 3, -d, 2, LEAF, droop=0.3)
        c.leaf(7, top + 1, -1, 2, LEAF); c.leaf(7, top + 1, 1, 2, LEAF)
    if s == 2:
        for (x, y) in ((4, 8), (11, 6)):
            c.p(x, y, GOLD[3]); c.p(x + 1, y, GOLD[3]); c.p(x, y + 1, GOLD[2])
    if s == 3:
        c.disc(3, 9, RED, big=True); c.disc(10, 7, RED, big=True); c.disc(10, 11, RED); c.disc(4, 5, RED)
        for (x, y) in ((4, 8), (11, 6), (11, 10), (5, 4)):
            c.p(x, y, LEAF[2])
    return c.shade()


# ----------------------------------------------------------------------------------------------- corn
def corn(s):
    c = C()
    top = (11, 7, 3, 1)[s]
    c.vline(7, top, 15, HUSK[1]); c.vline(8, top + 1, 15, HUSK[0])
    ys = list(range(14, top + 1, -3))
    for k, y in enumerate(ys):
        d = -1 if k % 2 == 0 else 1
        c.leaf(7 if d < 0 else 8, y, d, 4 if s >= 1 else 3, HUSK, droop=1.0, rise=0.6)
        if s >= 1:
            c.leaf(8 if d < 0 else 7, y - 1, -d, 3, HUSK, droop=1.2, rise=0.5)
    if s >= 2:                                               # tassel
        c.vline(7, top - 0, top + 1, TAN3) if False else None
        c.p(7, top, GOLD[2]); c.p(8, top, GOLD[2]); c.p(6, top + 1, GOLD[1]); c.p(9, top + 1, GOLD[1]); c.p(7, top - 1 if top > 0 else top, GOLD[3])
    if s == 3:                                               # cobs wrapped in husk, silks on top
        for (x, y) in ((4, 7), (10, 5)):
            for dy in range(3):
                c.p(x, y + dy, GOLD[2]); c.p(x + 1, y + dy, GOLD[3] if dy == 1 else GOLD[2])
            c.p(x, y + 3, HUSK[1]); c.p(x + 1, y + 3, HUSK[2])
            c.p(x, y - 1, GOLD[1]); c.p(x + 1, y - 1, hx('#a89060'))
    return c.shade()


TAN3 = hx('#c8a850')


# ----------------------------------------------------------------------------------------------- strawberry
def strawberry(s):
    c = C()
    n = (2, 3, 3, 4)[s]
    for k in range(n):
        x = 3 + k * 3 + (k % 2)
        y = 15 - (k % 2)
        c.vline(x, y - 2 - (s > 0), y, STEM)
        top = y - 2 - (s > 0)
        c.leaf(x, top + 1, -1, 3, LEAF, droop=0.8, rise=0.5); c.leaf(x, top + 1, 1, 3, LEAF, droop=0.8, rise=0.5)
        c.p(x, top, LEAF[3]); c.p(x, top - 1, LEAF[2])
    if s >= 2:
        for (x, y) in ((4, 9), (9, 8), (12, 10)):
            c.p(x, y, WHITE[2]); c.p(x - 1, y, WHITE[1]); c.p(x + 1, y, WHITE[1]); c.p(x, y - 1, WHITE[1]); c.p(x, y + 1, WHITE[0])
            c.p(x, y, GOLD[3])
    if s == 3:
        for (x, y) in ((2, 11), (7, 10), (11, 11), (5, 12)):
            c.disc(x, y, RED)
            c.p(x, y - 1, LEAF[2]); c.p(x + 1, y - 1, LEAF[3])
    return c.shade()


# ----------------------------------------------------------------------------------------------- chili
def chili(s):
    c = C()
    top = (11, 8, 5, 3)[s]
    c.vline(7, top, 15, CHILI[0]); c.vline(8, top + 2, 15, CHILI[0]) if s >= 1 else None
    for k, y in enumerate(range(14, top, -2)):
        d = -1 if k % 2 == 0 else 1
        c.leaf(7 if d < 0 else 8, y, d, 3 if s >= 1 else 2, CHILI, droop=0.5)
    if s == 0:
        c.leaf(7, 14, -1, 2, CHILI); c.leaf(8, 14, 1, 2, CHILI)
    if s >= 2:
        for (x, y) in ((4, 8), (10, 7), (11, 10)):
            col = CHILI if s == 2 else RED
            for k in range(4):
                c.p(x, y + k, col[2 if k < 3 else 1]);
            c.p(x + 1, y, col[3]); c.p(x + 1, y + 1, col[2]); c.p(x, y - 1, LEAF[1])
            c.p(x, y + 3, col[1] if s == 2 else RED[0])
    return c.shade()


# ----------------------------------------------------------------------------------------------- oats
def oats(s):
    c = C()
    h = (4, 8, 11, 13)[s]
    xs = (2, 4, 6, 8, 10, 12, 14) if s > 0 else (3, 6, 9, 12)
    for i, x in enumerate(xs):
        hh = h - (i % 3)
        col = LEAF if s < 3 else OAT
        for y in range(hh):
            c.p(x, 15 - y, col[1 if y % 3 else 2])
        if s >= 2:                                           # seed heads
            gcol = LEAF if s == 2 else OAT
            for k in range(3):
                c.p(x - 1 + (k % 2) * 2, 15 - hh - k + 1, gcol[3]); c.p(x, 15 - hh - k, gcol[3] if s == 2 else GOLD[3])
        elif s == 1 and i % 2 == 0:
            c.p(x + 1, 15 - hh + 1, LEAF[2])
    return c.shade()


STAGE_FN = {'tomato': tomato, 'corn': corn, 'strawberry': strawberry, 'chili': chili, 'oats': oats}


def wild(name):
    im = STAGE_FN[name](3)
    c = C()
    c.im = im
    for (x, y, k) in ((1, 15, 2), (3, 15, 1), (12, 15, 2), (14, 15, 1), (2, 14, 1), (13, 14, 2)):
        if not c.has(x, y):
            c.p(x, y, LEAF[k]); c.p(x, y - 1, LEAF[min(3, k + 1)])
    return c.im


if __name__ == '__main__':
    import sys
    sheet = Image.new('RGBA', (5 * 16 * 8, 5 * 16 * 8), (90, 70, 50, 255))
    for r, name in enumerate(STAGE_FN):
        for s in range(4):
            sheet.alpha_composite(STAGE_FN[name](s).resize((128, 128), Image.NEAREST), (s * 128, r * 128))
        sheet.alpha_composite(wild(name).resize((128, 128), Image.NEAREST), (4 * 128, r * 128))
    sheet.save(sys.argv[1] if len(sys.argv) > 1 else 'crops_preview.png')
