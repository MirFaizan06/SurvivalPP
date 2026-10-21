"""Textures for the four new natural stone families (derived from vanilla stone patterns, rank-mapped)."""
import random
from PIL import Image
from common import *
from tex_items import swap_palette

R = lambda *c: [hx(x) for x in c]

STONES = {
    'marlstone': dict(
        title='Marlstone', sound='stone', secs=1.5, resist=6.0, map='#c4baa0',
        ramp=R('#8a8068', '#a89e84', '#c4baa0', '#dcd2b8', '#efe6cf'),
        src=dict(base='stone_diorite.png', polished='stone_diorite_smooth.png', bricks='stonebrick.png'),
        gen=dict(rules=['stone'], count=44, y=(-12, 110), iters=2, chance=(2, 3))),
    'slate': dict(
        title='Slate', sound='stone', secs=2.0, resist=6.0, map='#516a7c',
        ramp=R('#1b2630', '#2a3945', '#3b4f5f', '#4f6a7d', '#6d8aa0'),
        src=dict(base='stone.png', polished='stone_andesite_smooth.png', bricks='stonebrick.png'),
        gen=dict(rules=['stone', 'tuff'], count=40, y=(-16, 96), iters=2, chance=(1, 1))),
    'verdite': dict(
        title='Verdite', sound='stone', secs=2.0, resist=6.0, map='#2f8a58',
        ramp=R('#0a2418', '#123c27', '#1c5c3a', '#2b7f52', '#4fae78'),
        src=dict(base='tuff.png', polished='polished_tuff.png', bricks='tuff_bricks.png'),
        gen=dict(rules=['stone', 'tuff', 'deepslate'], count=34, y=(-32, 64), iters=1, chance=(1, 2))),
    'umbrastone': dict(
        title='Umbrastone', sound='deepslate', secs=3.0, resist=9.0, map='#3a2751',
        ramp=R('#0b0710', '#150e1e', '#22162f', '#35224b', '#4f3573'),
        src=dict(base='deepslate/deepslate.png', polished='deepslate/polished_deepslate.png', bricks='deepslate/deepslate_bricks.png'),
        gen=dict(rules=['deepslate', 'stone'], count=36, y=(-64, 8), iters=2, chance=(1, 1))),
}


def strata(img, ramp, seed, step=4, amp=0.16):
    """horizontal sedimentary bands"""
    px = img.load()
    rng = random.Random(seed)
    for y in range(16):
        f = 1 + amp * (1 if (y // 2) % 2 == 0 else -1) * (0.6 + 0.4 * rng.random())
        if y % step == 0:
            f *= 0.86
        for x in range(16):
            r, g, b, a = px[x, y]
            px[x, y] = (min(255, int(r * f)), min(255, int(g * f)), min(255, int(b * f)), a)


def fossils(img, ramp, seed):
    rng = random.Random(seed)
    dark = ramp[0] + (255,)
    mid = ramp[1] + (255,)
    px = img.load()
    for (cx, cy) in ((4, 5), (11, 11)):
        for (dx, dy) in ((0, 0), (1, 0), (2, 1), (2, 2), (1, 3), (0, 3), (-1, 2), (-1, 1), (0, 1)):
            x, y = cx + dx, cy + dy
            if 0 <= x < 16 and 0 <= y < 16:
                px[x, y] = dark
        if 0 <= cx + 1 < 16 and 0 <= cy + 2 < 16:
            px[cx + 1, cy + 2] = mid


def veins(img, light, seed, glow=None):
    rng = random.Random(seed)
    px = img.load()
    mer = Image.new('RGB', (16, 16), (0, 0, 200)) if glow else None
    for _ in range(3):
        x, y = rng.randrange(16), rng.randrange(16)
        for k in range(rng.randrange(4, 8)):
            px[x % 16, y % 16] = light + (255,)
            if mer:
                mer.putpixel((x % 16, y % 16), (40, glow, 90))
            x += rng.choice([-1, 0, 1, 1]); y += rng.choice([0, 1, 1])
    return mer


def build_one(name, d):
    ramp, s = d['ramp'], d['src']
    base = swap_palette(load('blocks/' + s['base']), ramp, None, 0.0, 1.0, False)
    mer = None
    if name == 'marlstone':
        fossils(base, ramp, 7)
    elif name == 'slate':
        strata(base, ramp, 3)
    elif name == 'verdite':
        veins(base, ramp[4], 5)
        px = base.load()
        for (x, y) in ((3, 12), (12, 4), (8, 8)):
            px[x, y] = hx('#e8c25a') + (255,)
    elif name == 'umbrastone':
        mer = veins(base, ramp[4], 9, glow=90)
    polished = swap_palette(load('blocks/' + s['polished']), ramp, None, 0.18, 0.95, False)
    bricks = swap_palette(load('blocks/' + s['bricks']), ramp, None, 0.05, 0.95, False)
    outs = {name: base, f'polished_{name}': polished, f'{name}_bricks': bricks}
    for n, im in outs.items():
        save_png(im, f'{RP}/textures/blocks/{n}.png')
    if mer is not None:
        save_png(mer, f'{RP}/textures/blocks/{name}_mer.png')
        wjson(f'{RP}/textures/blocks/{name}.texture_set.json',
              {'format_version': '1.21.30', 'minecraft:texture_set': {'color': name, 'metalness_emissive_roughness': name + '_mer'}})
    return list(outs)


def build():
    names = []
    for n, d in STONES.items():
        names += build_one(n, d)
    return names


if __name__ == '__main__':
    names = build()
    up_sheet([f'{RP}/textures/blocks/{n}.png' for n in names], PREVIEW + '/stones.png', 10, 6)
