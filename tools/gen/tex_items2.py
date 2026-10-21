"""v1.2 drop / relic item sprites (hand-drawn 16x16 ASCII + a few procedural ones)."""
import math
from PIL import Image
from common import *
from tex_items import ascii_sprite, save_item

H = hx


def sprite_boar_tusk():
    pal = {'k': H('#2b2418'), 'b': H('#f1e8cc'), 'w': H('#fffbe8'), 'g': H('#cdbf9c'), 's': H('#9b8d6c'), 'd': H('#5a4a30')}
    return ascii_sprite([
        '.............kk.',
        '............kbwk',
        '...........kbbgk',
        '..........kbbgsk',
        '.........kbbgsk.',
        '........kbbgsk..',
        '.......kbbgsk...',
        '......kbbgsk....',
        '.....kbbgsk.....',
        '....kbbgsk......',
        '....kbgsk.......',
        '....kdsk........',
        '....kdk.........',
        '.....k..........',
    ], pal)


def sprite_hollow_bone():
    pal = {'k': H('#1c1a14'), 'b': H('#e6dfc6'), 'w': H('#fbf7e4'), 'g': H('#b8b094'), 'h': H('#2a2620'), 's': H('#8d866c')}
    return ascii_sprite([
        '..............kk',
        '.............kbbk',
        '...........kbwbk',
        '...........kbbgk.',
        '..........kbbgk..',
        '.........kbgsk...',
        '........kbgsk....',
        '.......kbgsk.....',
        '......kbgsk......',
        '.....kbgsk.......',
        '....kbgsk.......',
        'kbbkbgsk.........',
        'kbhhbkk..........',
        'kbwhbk...........',
        '.kbbk............',
        '..kk.............',
    ], pal)


def sprite_grave_dust():
    pal = {'k': H('#1a2018'), 'd': H('#3a463a'), 'g': H('#5f7160'), 'G': H('#8ea08c'), 'w': H('#d6e6d0')}
    return ascii_sprite([
        '.......kk.......',
        '......kggk......',
        '.....kgGGgk.....',
        '....kgGwGGgk....',
        '...kgGGGGwGgk...',
        '..kgGGgGGGGGgk..',
        '.kgGgGGGgGGgGgk.',
        '.kdgGGgGGGgGGdk.',
        '..kddgggGgggdk..',
        '...kkddddddkk...',
    ], pal)


def sprite_silk_gland():
    pal = {'k': H('#2a2236'), 'w': H('#f3f0ff'), 'g': H('#cfc6e8'), 'p': H('#a58de0'), 's': H('#8878b8')}
    return ascii_sprite([
        '......s..s......',
        '.......kk.......',
        '......kwwk......',
        '.....kwwgwk.....',
        '....kwwwgwwk....',
        '...kwwwwgwwwk...',
        '...kwwpwwgwwk...',
        '...kwwwwwgwwk...',
        '...kwwwwwgwpk...',
        '....kwwwwgwk....',
        '....kgwwwgsk....',
        '.....kggwsk.....',
        '......kkkk......',
    ], pal)


def sprite_spore_cluster():
    pal = {'k': H('#0b2a1c'), 'g': H('#2f9a5a'), 'G': H('#5fd77e'), 'l': H('#c8ffb0'), 'd': H('#1c5a3a')}
    return ascii_sprite([
        '.....kk.........',
        '....kgGk..kk....',
        '...kgGlGkkGgk...',
        '...kgGGGkgGlGk..',
        '....kkgkkgGGGk..',
        '...kk.kd.kkgk...',
        '..kgGk.d.kgGlk..',
        '.kgGlGkdkgGGGk..',
        '.kgGGGk.kkgGk...',
        '..kkgkk..kk.....',
        '.....d..........',
    ], pal)


def sprite_queens_fang():
    pal = {'w': H('#f1ecff'), 'g': H('#b9a8e6'), 'p': H('#7ee05a'), 'k': H('#1d1830'), 's': H('#8878b8')}
    return ascii_sprite([
        '...kkkk.........',
        '..kwwwwk........',
        '..kwwwgwk.......',
        '...kwwwgwk......',
        '....kwwgwk......',
        '.....kwgsk......',
        '.....kwwgk......',
        '......kwgk......',
        '......kwgk......',
        '.......kgk......',
        '.......kpk......',
        '.......kpk......',
        '........k.......',
    ], pal)


def sprite_silk_idol():
    pal = {'k': H('#2d2a3a'), 'w': H('#e8e4f4'), 'g': H('#b0a8cc'), 'r': H('#e03048'), 's': H('#7a7396')}
    return ascii_sprite([
        '..k..........k..',
        '..kk..kkkk..kk..',
        '...kk.kwwk.kk...',
        '.k..kkkwwkkk..k.',
        '.kkkkwwwwgwkkkk.',
        '...kkwrwwrwkk...',
        '.kkkkwwwwgwkkkk.',
        '.k..kkkwgkkk..k.',
        '...kk..kgk..kk..',
        '..kk..kkskk..kk.',
        '..k..........k..',
    ], pal)


def sprite_hollow_crown():
    pal = {'k': H('#2a1a05'), 'b': H('#d9a830'), 'w': H('#ffe48a'), 'd': H('#7a5612'), 'G': H('#4cf0a0'), 'g': H('#1f8a5a'), 'r': H('#a01818')}
    return ascii_sprite([
        '..k...k.kk...k..',
        '.kbk.kbkkbk.kbk.',
        '.kbbkkbbbbkkbbk.',
        '.kbwbbbbbbbbwbk.',
        '.kbbbGbbrbbGbbk.',
        '.kbbbgbbbbbgbbk.',
        '.kbbbbbbbbbbbbk.',
        '.kddddddddddddk.',
        '..kkkkkkkkkkkk..',
    ], pal)


def _canvas():
    return Image.new('RGBA', (16, 16), (0, 0, 0, 0))


def sprite_verdant_heart():
    """moss-green heart with veins, leaves on top and a glowing core"""
    im = _canvas()
    px = im.load()
    ramp = [H(c) for c in ('#0e2a12', '#1d5a22', '#2f8f36', '#56c453', '#9af07a', '#d8ffb0')]
    for y in range(16):
        for x in range(16):
            u, v = (x - 7.5) / 6.4, (8.2 - y) / 6.0
            g = (u * u + v * v - 1) ** 3 - u * u * v ** 3
            f = 1.0 + g * 1.4
            if g <= 0:
                t = 0.35 + 0.5 * (1 - f) + 0.18 * (-u * 0.6 + v * 0.4)
                t += 0.12 * math.sin(x * 1.7 + y * 0.9)
                c = ramp[max(0, min(5, int(t * 5.99)))]
                if f > 0.78:
                    c = tuple(int(q * 0.55) for q in c)
                px[x, y] = c + (255,)
    for (x, y) in ((6, 6), (7, 6), (7, 7), (8, 7), (8, 8), (7, 9), (7, 10)):
        px[x, y] = ramp[5] + (255,)
    for (x, y) in ((9, 2), (10, 1), (11, 1), (10, 2), (11, 2), (12, 2), (5, 2), (4, 1), (3, 1), (4, 2), (5, 3)):
        px[x, y] = ramp[3] + (255,)
    px[10, 1] = ramp[4] + (255,); px[4, 1] = ramp[4] + (255,)
    return im


def sprite_colossus_core():
    """a cross-section of ancient heartwood: tree rings around a glowing green seed"""
    im = _canvas()
    px = im.load()
    wood = [H(c) for c in ('#2a1a0c', '#4a2f17', '#6b4a27', '#8d6638', '#b08a52')]
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if d > 7.4:
                continue
            if d > 6.4:
                px[x, y] = H('#1c1108') + (255,)
            elif d < 2.2:
                px[x, y] = (H('#e8ffc8') if d < 1.1 else H('#6af07a')) + (255,)
            elif d < 3.2:
                px[x, y] = H('#2f8f36') + (255,)
            else:
                ring = 0.5 + 0.5 * math.sin(d * 2.9)
                t = int(ring * 3.2 + (0.7 if (x + y) % 5 == 0 else 0))
                px[x, y] = wood[max(0, min(4, 1 + t))] + (255,)
    for (x, y) in ((11, 3), (12, 4), (3, 12), (4, 12)):
        px[x, y] = H('#4cd35a') + (255,)       # moss
    return im


def sprite_grave_sigil():
    """round bone-grey ritual disc with a skull sigil and a sickly green ring"""
    im = _canvas()
    px = im.load()
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if d > 7.3:
                continue
            if d > 6.3:
                c = H('#14180f')
            elif d > 5.2:
                c = H('#3fbf6a') if (x + y) % 2 == 0 else H('#2a8a4a')
            else:
                t = 0.5 + 0.18 * math.sin(x * 1.3 + y * 0.8) - 0.06 * (d / 5)
                v = int(120 + 120 * t)
                c = (v, min(255, v + 4), max(0, v - 18))
            px[x, y] = c + (255,)
    dark = H('#181410') + (255,)
    for (x, y) in ((6, 5), (7, 5), (9, 5), (10, 5), (6, 6), (9, 6), (10, 6), (7, 6),
                   (7, 8), (8, 8), (6, 9), (7, 9), (8, 9), (9, 9), (6, 10), (8, 10), (9, 10)):
        px[x, y] = dark
    px[8, 5] = H('#ece6ce') + (255,); px[8, 6] = H('#ece6ce') + (255,)
    return im


SPRITES = {
    'boar_tusk': sprite_boar_tusk, 'hollow_bone': sprite_hollow_bone, 'grave_dust': sprite_grave_dust,
    'silk_gland': sprite_silk_gland, 'spore_cluster': sprite_spore_cluster, 'queens_fang': sprite_queens_fang,
    'silk_idol': sprite_silk_idol, 'hollow_crown': sprite_hollow_crown, 'verdant_heart': sprite_verdant_heart,
    'colossus_core': sprite_colossus_core, 'grave_sigil': sprite_grave_sigil,
}


def build():
    for n, fn in SPRITES.items():
        save_item(n, fn())
    return list(SPRITES)


if __name__ == '__main__':
    names = build()
    up_sheet([f'{RP}/textures/items/{n}.png' for n in names], PREVIEW + '/items_v12.png', 6, 12)
