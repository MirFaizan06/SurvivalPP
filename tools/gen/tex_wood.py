"""Wood-set textures for all tree species, derived from vanilla patterns with rank-mapped palettes."""
import random
from PIL import Image
from common import *
from tex_items import swap_palette

R = lambda *c: [hx(x) for x in c]

WOODS = {
    'jacaranda': dict(
        title='Jacaranda', sound='cherry_wood', map='#a98fb0', leaf_map='#7f5ee8',
        bark=R('#1f181c', '#31282c', '#473a3f', '#5e4e54', '#78666c', '#94818a'),
        heart=R('#62486a', '#7d6285', '#987da0', '#b399b8', '#cdb8d1', '#e3d4e6'),
        plank=R('#5f4663', '#785c7d', '#917598', '#a98fb0', '#c0a9c6', '#d6c5d9'),
        leaf=R('#241857', '#3b2a8c', '#5a3fbf', '#7f5ee8', '#a98af8', '#d2b8ff', '#f4e4ff'),
        src=dict(bark='pale_oak_log_side.png', top='cherry_log_top.png', s_side='stripped_cherry_log_side.png', s_top='stripped_cherry_log_top.png',
                 planks='cherry_planks.png', leaves='cherry_leaves.tga', sapling='cherry_sapling.png', d_lo='cherry_door_bottom.png', d_up='cherry_door_top.png', trap='cherry_trapdoor.png'),
        speck=None),
    'frostpine': dict(
        title='Frostpine', sound='wood', map='#7aa0b8', leaf_map='#4aa59c',
        bark=R('#141b22', '#202d38', '#324658', '#486379', '#668299', '#88a4b8'),
        heart=R('#52667a', '#6e8499', '#8aa1b5', '#a6bccc', '#c5d6e2', '#e2eef6'),
        plank=R('#48607a', '#627c97', '#7f99b2', '#9db5c9', '#bccfdd', '#dbe8f1'),
        leaf=R('#0b2f36', '#12474d', '#1b6366', '#2d8481', '#58b0a6', '#9ddccf', '#e3fbf6'),
        src=dict(bark='log_spruce.png', top='log_spruce_top.png', s_side='stripped_spruce_log.png', s_top='stripped_spruce_log_top.png',
                 planks='planks_spruce.png', leaves='leaves_spruce.tga', sapling='sapling_spruce.png', d_lo='door_spruce_lower.png', d_up='door_spruce_upper.png', trap='spruce_trapdoor.png'),
        speck=('#eefcff', 0.13)),
    'amberwood': dict(
        title='Amberwood', sound='wood', map='#c47a3a', leaf_map='#ee7a2a',
        bark=R('#24120d', '#3a2016', '#573223', '#774833', '#996447', '#b58563'),
        heart=R('#7a3f1d', '#9a5528', '#b86f36', '#d28c4c', '#e8ab72', '#f6cd9f'),
        plank=R('#7e4220', '#9c5a2b', '#b9743a', '#d19053', '#e6b078', '#f6d2a4'),
        leaf=R('#4a0f08', '#7a1d0e', '#b2341a', '#dd5a22', '#f58a2e', '#ffb94a', '#ffe28a'),
        src=dict(bark='log_oak.png', top='log_oak_top.png', s_side='stripped_oak_log.png', s_top='stripped_oak_log_top.png',
                 planks='planks_acacia.png', leaves='leaves_oak.tga', sapling='sapling_oak.png', d_lo='door_birch_lower.png', d_up='door_birch_upper.png', trap='birch_trapdoor.png'),
        speck=('#ffd45a', 0.1)),
    'sunwood': dict(
        title='Sunwood', sound='wood', map='#dca832', leaf_map='#e8d83a',
        bark=R('#2e2210', '#483618', '#664b22', '#87632e', '#a98040', '#c9a05a'),
        heart=R('#8a5c10', '#a8761a', '#c79228', '#e0b03d', '#f0cd62', '#fbe595'),
        plank=R('#94650f', '#b5821a', '#d3a02a', '#eabc42', '#f6d66a', '#fdeea4'),
        leaf=R('#4f4a0b', '#7c7414', '#aaa01d', '#cfc52f', '#e9e24e', '#f6f284', '#fffbc2'),
        src=dict(bark='log_acacia.png', top='log_acacia_top.png', s_side='stripped_acacia_log.png', s_top='stripped_acacia_log_top.png',
                 planks='planks_birch.png', leaves='leaves_acacia.tga', sapling='sapling_acacia.png', d_lo='door_acacia_lower.png', d_up='door_acacia_upper.png', trap='acacia_trapdoor.png'),
        speck=('#fff7a8', 0.08)),
    'mireweep': dict(
        title='Mireweep', sound='wood', map='#78905a', leaf_map='#58a066',
        bark=R('#14160e', '#222517', '#363c25', '#4d5834', '#697849', '#889a62'),
        heart=R('#3f5232', '#576c43', '#718a57', '#8da771', '#aac48e', '#c9deb0'),
        plank=R('#3b4c2c', '#506439', '#677f4a', '#809b5f', '#9db97c', '#bdd49f'),
        leaf=R('#0e2a1a', '#173f27', '#245d38', '#38824d', '#5fae6a', '#98d68e', '#d4f5c0'),
        src=dict(bark='log_jungle.png', top='log_jungle_top.png', s_side='stripped_jungle_log.png', s_top='stripped_jungle_log_top.png',
                 planks='planks_jungle.png', leaves='leaves_jungle.tga', sapling='sapling_jungle.png', d_lo='door_jungle_lower.png', d_up='door_jungle_upper.png', trap='jungle_trapdoor.png'),
        speck=('#d9ffb8', 0.07)),
}


def speckle(img, color, p, seed):
    rng = random.Random(seed)
    px = img.load()
    c = hx(color) + (255,)
    for y in range(img.height):
        for x in range(img.width):
            if px[x, y][3] > 0 and rng.random() < p:
                px[x, y] = c


def build_one(w):
    d = WOODS[w]
    s = d['src']
    B = lambda n: load('blocks/' + n)
    out = {}
    out[f'{w}_log_side'] = swap_palette(B(s['bark']), d['bark'], None, 0.0, 1.0, False)
    top = swap_palette(B(s['top']), d['heart'], None, 0.05, 1.0, False)
    for i in range(16):
        for (x, y) in ((i, 0), (i, 15), (0, i), (15, i)):
            top.putpixel((x, y), ramp_at(d['bark'], 0.35 + 0.1 * ((x + y) % 3) / 3) + (255,))
    out[f'{w}_log_top'] = top
    out[f'stripped_{w}_log_side'] = swap_palette(B(s['s_side']), d['heart'], None, 0.1, 0.95, False)
    out[f'stripped_{w}_log_top'] = swap_palette(B(s['s_top']), d['heart'], None, 0.1, 1.0, False)
    out[f'{w}_planks'] = swap_palette(B(s['planks']), d['plank'], None, 0.05, 1.0, False)
    leaves = swap_palette(B(s['leaves']), d['leaf'], None, 0.0, 1.0, False)
    if d['speck']:
        speckle(leaves, d['speck'][0], d['speck'][1], sum(map(ord, w)))
    out[f'{w}_leaves'] = leaves
    out[f'{w}_sapling'] = swap_palette(B(s['sapling']), d['leaf'], d['bark'], 0.0, 1.0, True)
    out[f'{w}_door_lower'] = swap_palette(B(s['d_lo']), d['plank'], None, 0.05, 1.0, False)
    out[f'{w}_door_upper'] = swap_palette(B(s['d_up']), d['plank'], None, 0.05, 1.0, False)
    out[f'{w}_trapdoor'] = swap_palette(B(s['trap']), d['plank'], None, 0.05, 1.0, False)
    for n, im in out.items():
        save_png(im, f'{RP}/textures/blocks/{n}.png')
    # item sprites
    save_png(out[f'{w}_sapling'], f'{RP}/textures/items/{w}_sapling_icon.png')
    lo, up = out[f'{w}_door_lower'], out[f'{w}_door_upper']
    icon = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    icon.paste(up.resize((10, 7), Image.NEAREST), (3, 1))
    icon.paste(lo.resize((10, 7), Image.NEAREST), (3, 8))
    px = icon.load()
    dark = ramp_at(d['bark'], 0.1) + (255,)
    for y in range(16):
        for x in range(2, 14):
            if not (3 <= x < 13 and 1 <= y < 15) and any(3 <= x + dx < 13 and 1 <= y + dy < 15 for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                px[x, y] = dark
    for (x, y) in ((10, 8), (10, 7)):
        px[x, y] = ramp_at(d['heart'], 0.95) + (255,)
    save_png(icon, f'{RP}/textures/items/{w}_door_icon.png')
    return list(out)


def build():
    names = []
    for w in WOODS:
        names += build_one(w)
    return names


def build_icons():
    pass   # icons are produced together with the textures in build_one


if __name__ == '__main__':
    names = build()
    sel = [f'{RP}/textures/blocks/{w}_{k}.png' for w in WOODS for k in ('log_side', 'log_top', 'planks', 'leaves', 'sapling', 'door_lower', 'trapdoor')]
    up_sheet(sel, PREVIEW + '/wood_all.png', 6, 7)
