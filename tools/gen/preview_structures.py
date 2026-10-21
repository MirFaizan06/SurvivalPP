"""python preview_structures.py [name ...]  ->  <build>/preview/struct_<name>.png  (isometric full view + cutaway view, chests/spawners/TNT highlighted)"""
import json, os, sys, glob
from PIL import Image, ImageDraw
from common import *

KEY = [  # substring -> colour (first match wins)
    ('chest', (255, 215, 0)), ('mob_spawner', (0, 240, 255)), ('tnt', (255, 40, 40)), ('pressure_plate', (255, 255, 255)),
    ('lava', (255, 120, 20)), ('water', (40, 90, 220)), ('powder_snow', (230, 240, 255)), ('web', (230, 230, 230)), ('infested', (200, 90, 200)),
    ('wither_rose', (30, 30, 30)), ('pointed_dripstone', (150, 120, 90)), ('eclipsite', (170, 90, 255)), ('altar', (210, 60, 255)),
    ('obsidian', (50, 30, 80)), ('end_', (230, 230, 160)), ('purpur', (170, 110, 170)), ('sandstone', (225, 205, 140)), ('sand', (230, 215, 150)),
    ('terracotta', (200, 120, 70)), ('snow', (245, 248, 255)), ('ice', (150, 200, 245)), ('blackstone', (45, 40, 50)), ('nether_brick', (80, 30, 35)),
    ('magma', (200, 80, 20)), ('soul', (90, 70, 55)), ('deepslate', (70, 72, 80)), ('tuff', (100, 100, 90)), ('moss', (80, 130, 50)), ('vine', (50, 110, 40)),
    ('grass', (95, 150, 60)), ('dirt', (120, 85, 55)), ('podzol', (90, 65, 40)), ('gravel', (130, 125, 120)), ('mossy', (95, 125, 85)),
    ('stone', (125, 125, 125)), ('cobble', (115, 115, 115)), ('andesite', (135, 135, 140)), ('log', (110, 80, 45)), ('planks', (170, 130, 80)),
    ('fence', (150, 110, 70)), ('slab', (170, 130, 80)), ('ladder', (160, 120, 70)), ('bookshelf', (150, 110, 70)), ('hay', (220, 190, 60)),
    ('barrel', (140, 100, 60)), ('lantern', (255, 200, 120)), ('campfire', (255, 150, 60)), ('bone', (235, 230, 210)), ('iron_bars', (160, 160, 165)),
    ('glowstone', (255, 220, 120)), ('bricks', (130, 125, 120)), ('torch', (255, 200, 100)), ('end_rod', (255, 255, 255)), ('stray', (200, 200, 255)),
]


def colour(name):
    n = name.replace('minecraft:', '').replace('ecr:', '')
    for k, c in KEY:
        if k in n:
            return c
    return (150, 150, 150)


def render(data, cut, scale=11, axis=2):
    vox = [(x, y, z, data['palette'][i]) for x, y, z, i in data['voxels'] if data['palette'][i] != 'minecraft:air']
    if cut is not None:
        vox = [v for v in vox if v[axis] <= cut]
    vox.sort(key=lambda v: (v[0] + v[2], v[1]))
    sx, sy, sz = data['size']
    W = int((sx + sz) * scale + 40)
    H = int((sx + sz) * scale * 0.5 + sy * scale * 1.0 + 60)
    im = Image.new('RGB', (W, H), (40, 42, 52))
    d = ImageDraw.Draw(im)
    ox, oy = sz * scale + 20, sy * scale + 30
    for x, y, z, n in vox:
        c = colour(n)
        px = ox + (x - z) * scale
        py = oy + (x + z) * scale * 0.5 - y * scale
        top = tuple(min(255, int(v * 1.15)) for v in c); left = tuple(int(v * 0.65) for v in c); right = tuple(int(v * 0.82) for v in c)
        s = scale
        d.polygon([(px, py - s), (px + s, py - s * 0.5), (px, py), (px - s, py - s * 0.5)], fill=top)
        d.polygon([(px - s, py - s * 0.5), (px, py), (px, py + s), (px - s, py + s * 0.5)], fill=left)
        d.polygon([(px + s, py - s * 0.5), (px, py), (px, py + s), (px + s, py + s * 0.5)], fill=right)
    return im


def main():
    names = sys.argv[1:] or [os.path.basename(p)[:-5] for p in glob.glob(f'{BUILD}/structure_voxels/*.json')]
    for n in names:
        data = json.load(open(f'{BUILD}/structure_voxels/{n}.json'))
        a = render(data, None)
        axis = 0 if os.environ.get('CUTX') else 2
        b = render(data, data['size'][axis] // 2, axis=axis)
        out = Image.new('RGB', (a.width + b.width, max(a.height, b.height)), (40, 42, 52))
        out.paste(a, (0, 0)); out.paste(b, (a.width, 0))
        out.save(f'{PREVIEW}/struct_{n}.png')
        print(n, out.size)


if __name__ == '__main__':
    main()
