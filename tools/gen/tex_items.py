"""Item + armor textures for Azurite / Pyrelite / Eclipsite.
Tool/armor sprites are rank-mapped palette swaps of the vanilla diamond sprites (the same
technique used by every 'mc+' style pack) with extra bespoke glints per material."""
import math, random
from PIL import Image
from common import *

HANDLE_STICK = [hx(x) for x in ['#28200b', '#493615', '#684e1e', '#89672b', '#a8823a']]
HANDLE_BLAZE = [hx(x) for x in ['#6b2d00', '#a84a05', '#e07c10', '#ffb62a', '#ffe27a']]
HANDLE_ENDROD = [hx(x) for x in ['#2d2447', '#4f4380', '#8a7bd0', '#cbbcff', '#f6f0ff']]
HANDLE_BREEZE = [hx(x) for x in ['#1a3a2e', '#2c6a50', '#4aa078', '#8ee0b0', '#d8ffe8']]

MATS = {
    'azurite':  dict(ramp=AZURITE,  handle=HANDLE_STICK,  sparkle=hx('#e8fbff'), stick='stick', curve=0.9),
    'pyrelite': dict(ramp=PYRELITE, handle=HANDLE_BLAZE,  sparkle=hx('#fff2b0'), stick='blaze_rod', curve=1.75),
    'eclipsite': dict(ramp=ECLIPSITE, handle=HANDLE_ENDROD, sparkle=hx('#9ff4ff'), stick='end_rod', curve=1.35),
    'rimesteel': dict(ramp=RIMESTEEL, handle=HANDLE_STICK, sparkle=hx('#ffffff'), stick='stick', curve=1.1, raw=False),
    'glacite': dict(ramp=GLACITE, handle=HANDLE_STICK, sparkle=hx('#ffffff'), stick='stick', curve=0.85, raw=False),
    'wispsteel': dict(ramp=WISPSTEEL, handle=HANDLE_BREEZE, sparkle=hx('#fff6b0'), stick='breeze_rod', curve=1.3, raw=False),
}


def swap_palette(img, ramp, handle_ramp=None, lo=0.06, hi=1.0, split_handle=True, curve=1.0):
    img = img.copy()
    px = img.load()
    cols = {}
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            cols.setdefault((r, g, b), []).append((x, y))
    head, handle = [], []
    for c in cols:
        (handle if (split_handle and c[0] > c[2] + 6) else head).append(c)

    def assign(group, rmp, lo_, hi_):
        group = sorted(group, key=lum)
        n = len(group)
        for i, c in enumerate(group):
            u = (i / (n - 1) if n > 1 else 1.0)
            if rmp is ramp:
                u = u ** curve
            t = lo_ + (hi_ - lo_) * u
            new = ramp_at(rmp, t)
            for (x, y) in cols[c]:
                a = px[x, y][3]
                px[x, y] = new + (a,)

    assign(head, ramp, lo, hi)
    if handle:
        assign(handle, handle_ramp or HANDLE_STICK, 0.0, 1.0)
    return img


def add_sparkles(img, pts, col):
    for (x, y) in pts:
        if 0 <= x < img.width and 0 <= y < img.height and img.getpixel((x, y))[3] > 0:
            img.putpixel((x, y), col + (255,))


def brightest(img, n=2):
    best = []
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = img.getpixel((x, y))
            if a:
                best.append((lum((r, g, b)), x, y))
    best.sort(reverse=True)
    return [(x, y) for _, x, y in best[:n]]


def mer_items(img, mat):
    """Emissive map for items (used by Vibrant Visuals / ray tracing)."""
    mer = Image.new('RGB', img.size, (0, 0, 200))
    px = img.load(); mp = mer.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if not a:
                continue
            l = lum((r, g, b))
            if mat == 'azurite':
                mp[x, y] = (90, int(max(0, l - 0.75) * 255), 60)
            elif mat == 'pyrelite':
                glow = 0
                if r > 200 and g > 100:
                    glow = int(min(255, (l - 0.4) * 400))
                mp[x, y] = (30, max(0, glow), 90)
            else:
                glow = int(max(0, l - 0.55) * 450) if (r > 150 or b > 150) else 0
                mp[x, y] = (120, min(255, glow), 55)
    return mer


TOOLS = ['sword', 'pickaxe', 'axe', 'shovel', 'hoe']
ARMOR = ['helmet', 'chestplate', 'leggings', 'boots']


def save_item(name, img, mat=None):
    save_png(img, f'{RP}/textures/items/{name}.png')
    if mat:
        save_png(mer_items(img, mat), f'{RP}/textures/items/{name}_mer.png')
        wjson(f'{RP}/textures/items/{name}.texture_set.json',
              {"format_version": "1.21.30",
               "minecraft:texture_set": {"color": name, "metalness_emissive_roughness": name + "_mer"}})


def build_materials():
    names = []
    for mat, d in MATS.items():
        ramp, handle = d['ramp'], d['handle']
        # tools & armour (diamond sprites)
        for t in TOOLS + ARMOR:
            src = load(f'items/diamond_{t}.png')
            img = swap_palette(src, ramp, handle, curve=d['curve'])
            if mat == 'pyrelite':
                add_sparkles(img, brightest(img, 1), hx('#fff6c2'))
            elif mat == 'eclipsite':
                bs = brightest(img, 3)
                add_sparkles(img, bs[:1], hx('#9ff4ff'))
                add_sparkles(img, bs[1:2], hx('#ff9cf0'))
            else:
                add_sparkles(img, brightest(img, 1), hx('#ffffff'))
            save_item(f'{mat}_{t}', img, mat); names.append(f'{mat}_{t}')
        # ingot: netherite ingot silhouette
        ing = swap_palette(load('items/netherite_ingot.png'), ramp, None, lo=0.1, hi=1.0, split_handle=False, curve=d['curve'])
        if mat != 'azurite':
            add_sparkles(ing, brightest(ing, 1), d['sparkle'])
        save_item(f'{mat}_ingot', ing, mat); names.append(f'{mat}_ingot')
        # raw chunk: raw iron silhouette (only the ore metals have one)
        if d.get('raw', True):
            raw = swap_palette(load('items/raw_iron.png'), ramp, None, lo=0.05, hi=0.92, split_handle=False, curve=d['curve'])
            add_sparkles(raw, brightest(raw, 2), d['sparkle'])
            save_item(f'raw_{mat}', raw, mat); names.append(f'raw_{mat}')
        # nugget-like shard used for the T-tier shards (from iron nugget)
    return names


# ------------------------------------------------------------ ASCII hand drawn sprites
def ascii_sprite(rows, pal):
    h = len(rows); w = max(len(r) for r in rows)
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    ox, oy = (16 - w) // 2, (16 - h) // 2
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != '.' and ch in pal:
                im.putpixel((ox + x, oy + y), pal[ch] + (255,))
    return im


def sprite_ember_fang():
    pal = {'k': hx('#1a0805'), 'd': hx('#3b0c08'), 'r': hx('#7d1a0a'), 'o': hx('#d4440f'), 'y': hx('#ff8a24'), 'w': hx('#ffd35e'), 'b': hx('#e9dcc8'), 'g': hx('#b6a58c'), 's': hx('#7a6c58')}
    rows = [
        '......kkkk......',
        '.....kbbbgk.....',
        '.....kbwbgk.....',
        '....kbbbbggk....',
        '....kbbbbgsk....',
        '....kbbbgsk.....',
        '....kybbgsk.....',
        '.....kybgsk.....',
        '.....kooggk.....',
        '.....koogk......',
        '......kosk......',
        '......kok.......',
        '.......kk.......',
    ]
    return ascii_sprite(rows, pal)


def sprite_void_essence():
    pal = {'k': hx('#05020c'), 'd': hx('#150a2b'), 'p': hx('#34136a'), 'm': hx('#6d27b8'), 'f': hx('#c046dc'), 'l': hx('#ff9cf0'), 'c': hx('#9ff4ff'), 'g': hx('#8a8aa8')}
    rows = [
        '.....gggggg.....',
        '....gdddddddg...',
        '...gdppmmmppdg..',
        '..gdpmmfffmmpdg.',
        '..gdmffllfffmdg.',
        '..gdmflcclffmdg.',
        '..gdmflccllfmdg.',
        '..gdpmffllfmpdg.',
        '...gdpmmfmmpdg..',
        '....gddppppdg...',
        '.....ggddddg....',
        '......gggggg....',
    ]
    return ascii_sprite(rows, pal)


def sprite_eclipse_core():
    pal = {'k': hx('#05020c'), 'd': hx('#0f0620'), 'p': hx('#34136a'), 'm': hx('#6d27b8'), 'f': hx('#c046dc'), 'l': hx('#ff9cf0'), 'c': hx('#9ff4ff'), 'w': hx('#ffffff')}
    rows = [
        '.......c........',
        '...f...l...f....',
        '....mc.m.cm.....',
        '.....kkkkk......',
        '..fl.kdddkk.lf..',
        '.c.mkdddddkkm.c.',
        'wlmmkdddddkkmmlw',
        '.c.mkdddddkkm.c.',
        '..fl.kdddkk.lf..',
        '.....kkkkk......',
        '....mc.m.cm.....',
        '...f...l...f....',
        '.......c........',
    ]
    im = ascii_sprite(rows, pal)
    # corona ring (circle) around centre
    cx, cy = 8, 8
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - cx + 0.0, y - cy)
            if 3.6 <= d <= 4.6 and im.getpixel((x, y))[3] == 0:
                ang = math.atan2(y - cy, x - cx)
                t = 0.5 + 0.5 * math.cos(ang - 3.9)
                im.putpixel((x, y), ramp_at(ECLIPSITE, 0.55 + 0.4 * t) + (255,))
    return im


def sprite_eclipse_sigil():
    pal = {'k': hx('#0b0614'), 'd': hx('#1c1033'), 'p': hx('#34136a'), 'm': hx('#6d27b8'), 'f': hx('#c046dc'), 'l': hx('#ff9cf0'), 'c': hx('#9ff4ff'), 's': hx('#6b6486'), 'S': hx('#a39cc2')}
    rows = [
        '....SSSSSSSS....',
        '..SSsddddddsSS..',
        '.SsdddmffmdddsS.',
        '.SdddmllllmdddS.',
        'SsddmlffffmlddsS'.replace('lffffml', 'llccllm')[:16],
        'SdmlfccccccflmdS',
        'SdmlfcckkccflmdS',
        'SdmlfcckkccflmdS',
        'SdmlfccccccflmdS',
        'SsddmlffffmlddsS',
        '.SdddmllllmdddS.',
        '.SsdddmffmdddsS.',
        '..SSsddddddsSS..',
        '....SSSSSSSS....',
    ]
    rows = [r.ljust(16, '.')[:16] for r in rows]
    return ascii_sprite(rows, pal)


def sprite_jacaranda_sapling():
    pal = {'k': hx('#3a2a26'), 'b': hx('#5a463f'), 'v': hx('#4a8a3a'), 'V': hx('#6fb04e'), 'p': hx('#7f5fd0'), 'P': hx('#a98af0'), 'L': hx('#d3baff'), 'W': hx('#f6e6ff')}
    rows = [
        '................',
        '....PLP.........',
        '...PLWLP..pP....',
        '..pPLWPLp.PLp...',
        '..PLPpLPPpLWP...',
        '...pPLpPpPLPp...',
        '....pPPbpPp.....',
        '.....pbbbp......',
        '......kbk.......',
        '......kbk..v....',
        '.....vkbk.vV....',
        '....vVvkbvVv....',
        '.....vVkbV......',
        '......vkb.......',
        '......kbk.......',
        '.....kkbkk......',
    ]
    return ascii_sprite(rows, pal)


def build_special():
    out = {}
    out['ember_fang'] = sprite_ember_fang()
    out['void_essence'] = sprite_void_essence()
    out['eclipse_core'] = sprite_eclipse_core()
    out['eclipse_sigil'] = sprite_eclipse_sigil()
    for n, im in out.items():
        save_item(n, im)
    return list(out)


# ------------------------------------------------------------ worn armour layers
def build_armor_layers():
    for mat, d in MATS.items():
        for layer in (1, 2):
            src = load(f'models/armor/diamond_{layer}.png')
            img = swap_palette(src, d['ramp'], None, lo=0.06, hi=1.0, split_handle=False, curve=d['curve'])
            # glints on the brightest couple of pixels per layer
            add_sparkles(img, brightest(img, 4), d['sparkle'])
            save_png(img, f'{RP}/textures/models/armor/{mat}_{layer}.png')


if __name__ == '__main__':
    names = build_materials() + build_special()
    build_armor_layers()
    up_sheet([f'{RP}/textures/items/{n}.png' for n in names], PREVIEW + '/items_a.png', 8, 12)
    up_sheet([f'{RP}/textures/models/armor/{m}_{l}.png' for m in MATS for l in (1, 2)], PREVIEW + '/armor_a.png', 6, 6)
