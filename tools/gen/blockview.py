import os
"""Quick isometric preview of block geometry files (per-face UV) to sanity-check baked rotations."""
import json, math, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

FACE_QUADS = {
    'north': lambda x0, y0, z0, x1, y1, z1: [(x1, y1, z0), (x0, y1, z0), (x0, y0, z0), (x1, y0, z0)],
    'south': lambda x0, y0, z0, x1, y1, z1: [(x0, y1, z1), (x1, y1, z1), (x1, y0, z1), (x0, y0, z1)],
    'east': lambda x0, y0, z0, x1, y1, z1: [(x1, y1, z1), (x1, y1, z0), (x1, y0, z0), (x1, y0, z1)],
    'west': lambda x0, y0, z0, x1, y1, z1: [(x0, y1, z0), (x0, y1, z1), (x0, y0, z1), (x0, y0, z0)],
    'up': lambda x0, y0, z0, x1, y1, z1: [(x1, y1, z1), (x0, y1, z1), (x0, y1, z0), (x1, y1, z0)],
    'down': lambda x0, y0, z0, x1, y1, z1: [(x1, y0, z0), (x0, y0, z0), (x0, y0, z1), (x1, y0, z1)],
}
NORMALS = {'north': (0, 0, -1), 'south': (0, 0, 1), 'east': (1, 0, 0), 'west': (-1, 0, 0), 'up': (0, 1, 0), 'down': (0, -1, 0)}


def render_block(geo_path, mats, out, yaw=35, pitch=-28, scale=12, size=(260, 260), geo_obj=None, rgba=False):
    g = (geo_obj or json.load(open(geo_path)))['minecraft:geometry'][0]
    W, H = size
    img = np.zeros((H, W, 3), np.float32) + np.array((46, 46, 52), np.float32)
    zb = np.full((H, W), 1e9, np.float32)
    ya, pa = math.radians(yaw), math.radians(pitch)
    cy, sy = math.cos(ya), math.sin(ya)
    cp, sp = math.cos(pa), math.sin(pa)
    V = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]]) @ np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    cen = np.array([0, 8, 0.0])
    light = np.array([-0.4, 0.8, -0.5]); light /= np.linalg.norm(light)
    for bone in g['bones']:
        for c in bone['cubes']:
            o, s = c['origin'], c['size']
            x0, y0, z0, x1, y1, z1 = o[0], o[1], o[2], o[0] + s[0], o[1] + s[1], o[2] + s[2]
            for face, fuv in c['uv'].items():
                quad = np.array(FACE_QUADS[face](x0, y0, z0, x1, y1, z1), float)
                n = np.array(NORMALS[face], float)
                vn = V @ n
                if vn[2] > 0.001:
                    continue
                tex = mats.get(fuv['material_instance'], mats['*'])
                ta = np.array(tex)
                u0, v0 = fuv['uv']; uw, vh = fuv['uv_size']
                vp = (V @ (quad - cen).T).T
                sxy = np.stack([W / 2 + vp[:, 0] * scale, H * 0.6 - vp[:, 1] * scale], 1)
                uvs = np.array([(0, 0), (1, 0), (1, 1), (0, 1)], float)
                lam = 0.6 + 0.4 * max(0.0, float(np.dot(n, light)))
                for (a, b, c_) in ((0, 1, 2), (0, 2, 3)):
                    p0, p1, p2 = sxy[a], sxy[b], sxy[c_]
                    minx = int(max(0, math.floor(min(p0[0], p1[0], p2[0])))); maxx = int(min(W - 1, math.ceil(max(p0[0], p1[0], p2[0]))))
                    miny = int(max(0, math.floor(min(p0[1], p1[1], p2[1])))); maxy = int(min(H - 1, math.ceil(max(p0[1], p1[1], p2[1]))))
                    if maxx < minx or maxy < miny:
                        continue
                    xs, ys = np.meshgrid(np.arange(minx, maxx + 1) + 0.5, np.arange(miny, maxy + 1) + 0.5)
                    d = (p1[1] - p2[1]) * (p0[0] - p2[0]) + (p2[0] - p1[0]) * (p0[1] - p2[1])
                    if abs(d) < 1e-9:
                        continue
                    l1 = ((p1[1] - p2[1]) * (xs - p2[0]) + (p2[0] - p1[0]) * (ys - p2[1])) / d
                    l2 = ((p2[1] - p0[1]) * (xs - p2[0]) + (p0[0] - p2[0]) * (ys - p2[1])) / d
                    l3 = 1 - l1 - l2
                    m = (l1 >= -1e-4) & (l2 >= -1e-4) & (l3 >= -1e-4)
                    z = l1 * vp[a][2] + l2 * vp[b][2] + l3 * vp[c_][2]
                    ss = l1 * uvs[a][0] + l2 * uvs[b][0] + l3 * uvs[c_][0]
                    tt = l1 * uvs[a][1] + l2 * uvs[b][1] + l3 * uvs[c_][1]
                    tx = np.clip(((u0 + ss * uw) * ta.shape[1] / 16).astype(int), 0, ta.shape[1] - 1)
                    ty = np.clip(((v0 + tt * vh) * ta.shape[0] / 16).astype(int), 0, ta.shape[0] - 1)
                    col = ta[ty, tx]
                    ok = m & (z < zb[miny:maxy + 1, minx:maxx + 1]) & (col[..., 3] > 30)
                    sub = img[miny:maxy + 1, minx:maxx + 1]
                    zs = zb[miny:maxy + 1, minx:maxx + 1]
                    sub[ok] = np.minimum(255, col[..., :3].astype(np.float32)[ok] * lam * 1.15)
                    zs[ok] = z[ok]
    rgb = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    if rgba:
        a = Image.fromarray(((zb < 1e8) * 255).astype(np.uint8))
        rgb = rgb.convert('RGBA'); rgb.putalpha(a)
    if out:
        rgb.save(out)
    return rgb


def tex(name):
    return Image.open(f'{RP}/textures/blocks/{name}.png').convert('RGBA')


if __name__ == '__main__':
    base = tex('jacaranda_planks')
    jobs = [
        ('stasis_chamber', {'frame': tex('stasis_frame'), 'glass': tex('stasis_glass'), 'pearl': tex('stasis_pearl'), '*': tex('stasis_frame')}),
        ('sanctum_warden', {'stone': tex('sanctum_stone'), 'eye': tex('sanctum_eye'), 'top': tex('sanctum_top'), '*': tex('sanctum_stone')}),
        ('stasis_plate', {'top': tex('stasis_plate_top'), 'side': tex('stasis_plate_side'), '*': tex('stasis_plate_side')}),
        ('wood_stairs_bottom_north', {'*': base}),
        ('wood_stairs_top_east', {'*': base}),
        ('wood_fence', {'*': base}),
        ('wood_gate_closed_north', {'*': base}),
        ('wood_gate_open_north', {'*': base}),
        ('wood_trapdoor_bottom_open_north', {'*': base}),
        ('wood_door_open_r_north', {'*': base}),
        ('wood_button_north_off', {'*': base}),
        ('wood_button_down_off', {'*': base}),
    ]
    tiles = []
    for name, mats in jobs:
        p = f'{PREVIEW}/bv_{name}.png'
        render_block(f'{RP}/models/blocks/{name.replace("jacaranda_fence", "jacaranda_fence")}.geo.json', mats, p)
        tiles.append(Image.open(p))
    cols = 4
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new('RGB', (260 * cols, 260 * rows))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols) * 260, (i // cols) * 260))
    sheet.save(PREVIEW + '/blocks_geo.png')
