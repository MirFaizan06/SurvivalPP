"""Master build: regenerates every asset, writes manifests + scripts, lints and packages the .mcaddon."""
import os, shutil, sys, json, zipfile, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFilter
from common import *

BP_UUID = '62528153-2da9-4ae4-b4e0-08192cd90100'
BP_DATA = '9cfe2e62-8261-494f-ba10-d2d1bca78df5'
BP_SCRIPT = '113cfa18-9f77-4c66-a4b2-2dfe824f2422'
RP_UUID = 'd10f19cf-1a0e-4150-9b48-bab248978a46'
RP_RES = 'e2cf5c22-918d-47f0-8a86-1a2e7324d6fc'
_V = json.load(open(ROOT / 'tools' / 'version.json', encoding='utf-8'))
VERSION = _V['version']                      # bump in tools/version.json for every release (the game ignores same/lower versions)
ENGINE = [1, 26, 50]
TITLE = _V['title']
VSTR = '.'.join(str(x) for x in VERSION)
DESC = f'A story-driven Bedrock adventure by Tech Bytes Design.  v{VSTR}: the Seven Seals saga, bosses, adventure structures, new ores, stones, crops, animals, trees & stasis chambers.'
OUT_NAME = f"{_V['file_stem']}_v{VSTR}"


def _rm(func, path, exc):
    import stat, time
    os.chmod(path, stat.S_IWRITE)
    time.sleep(0.05)
    func(path)


def clean():
    for d in (BP, RP):
        if os.path.exists(d):
            shutil.rmtree(d, onexc=_rm) if sys.version_info >= (3, 12) else shutil.rmtree(d, onerror=_rm)
        os.makedirs(d)


def pack_icon():
    S = 256
    img = Image.new('RGB', (S, S), (8, 4, 18))
    px = img.load()
    rng = random.Random(7)
    for y in range(S):
        for x in range(S):
            d = math.hypot(x - 128, y - 118) / 180
            t = max(0, 1 - d)
            px[x, y] = (int(10 + 46 * t * t), int(5 + 14 * t * t), int(26 + 90 * t * t))
    for _ in range(90):
        x, y = rng.randrange(S), rng.randrange(S)
        b = rng.choice([90, 140, 200, 255])
        px[x, y] = (b, b, min(255, b + 30))
    d = ImageDraw.Draw(img)
    cx, cy, r = 128, 112, 46
    # corona rays
    for k in range(48):
        a = k / 48 * math.tau
        L = 78 + (k % 3) * 14 + (10 if k % 2 else 0)
        col = ramp_at(ECLIPSITE, 0.55 + 0.4 * (0.5 + 0.5 * math.cos(a - 3.9)))
        d.line([(cx + math.cos(a) * (r + 4), cy + math.sin(a) * (r + 4)), (cx + math.cos(a) * L, cy + math.sin(a) * L)], fill=col, width=2)
    glow = Image.new('RGB', (S, S), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for rr, c in ((r + 18, (90, 30, 140)), (r + 10, (170, 70, 210)), (r + 4, (255, 170, 240))):
        gd.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=c)
    glow = glow.filter(ImageFilter.GaussianBlur(9))
    img = Image.blend(img, Image.composite(glow, img, glow.convert('L').point(lambda v: 255 if v > 8 else 0)), 0.85)
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3], fill=(255, 200, 250))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(4, 2, 10))
    # gem trio
    for i, nm in enumerate(('azurite_ingot', 'pyrelite_ingot', 'eclipsite_ingot')):
        ic = Image.open(f'{RP}/textures/items/{nm}.png').convert('RGBA').resize((56, 56), Image.NEAREST)
        img.paste(ic, (32 + i * 66, 176), ic)
    # "S++" glyph block built from rects (no font dependency)
    def rect(x0, y0, x1, y1, col): d.rectangle([x0, y0, x1, y1], fill=col)
    gold = (255, 226, 150)
    shade = (90, 40, 130)
    for off, col in ((2, shade), (0, gold)):
        ox = 18 + off; oy = 14 + off
        for (a, b, c_, e) in ((0, 0, 20, 5), (0, 0, 5, 14), (0, 14, 20, 19), (15, 19, 20, 33), (0, 33, 20, 38)):
            rect(ox + a, oy + b, ox + c_, oy + e, col)
        for px0 in (26, 44):
            rect(ox + px0, oy + 12, ox + px0 + 14, oy + 17, col)
            rect(ox + px0 + 4, oy + 8, ox + px0 + 9, oy + 22, col)
    for p in (f'{BP}/pack_icon.png', f'{RP}/pack_icon.png'):
        ensure(p)
        img.save(p)


def manifests():
    bp = {
        'format_version': 2,
        'header': {'name': TITLE + ' [BP]', 'description': DESC, 'uuid': BP_UUID, 'version': VERSION, 'min_engine_version': ENGINE},
        'modules': [
            {'type': 'data', 'description': 'Eclipsed Realms data', 'uuid': BP_DATA, 'version': VERSION},
            {'type': 'script', 'language': 'javascript', 'description': 'Eclipsed Realms scripts', 'uuid': BP_SCRIPT, 'version': VERSION, 'entry': 'scripts/main.js'}],
        'dependencies': [{'uuid': RP_UUID, 'version': VERSION}, {'module_name': '@minecraft/server', 'version': '2.6.0'}, {'module_name': '@minecraft/server-ui', 'version': '2.0.0'}],
        'metadata': {'authors': ['Tech Bytes Design'], 'license': 'All rights reserved - Tech Bytes Design', 'url': ''},
    }
    rp = {
        'format_version': 2,
        'header': {'name': TITLE + ' [RP]', 'description': DESC, 'uuid': RP_UUID, 'version': VERSION, 'min_engine_version': ENGINE},
        'modules': [{'type': 'resources', 'description': 'Eclipsed Realms resources', 'uuid': RP_RES, 'version': VERSION}],
        'metadata': {'authors': ['Tech Bytes Design'], 'license': 'All rights reserved - Tech Bytes Design', 'url': ''},
    }
    wjson(f'{BP}/manifest.json', bp)
    wjson(f'{RP}/manifest.json', rp)


def copy_scripts():
    src = SCRIPTS_SRC
    dst = f'{BP}/scripts'
    os.makedirs(dst, exist_ok=True)
    for f in os.listdir(src):
        if f.endswith('.js'):
            shutil.copy(os.path.join(src, f), os.path.join(dst, f))


def generate():
    clean()
    import shutil
    shutil.rmtree(f'{BUILD}/structure_palettes', ignore_errors=True)
    import tex_blocks, tex_wood, tex_special, tex_items
    tex_blocks.build_all(); tex_wood.build(); tex_special.build(); tex_special.build_sanctum()
    tex_items.build_materials(); tex_items.build_special()
    tex_wood.build_icons()
    import tex_stone
    tex_stone.build()
    import tex_food
    tex_food.build()
    import tex_items2
    tex_items2.build()
    import gen_blocks, gen_items, gen_mobs, gen_world, registry
    gen_blocks.build_all()
    import blockicons
    blockicons.build()
    gen_items.build_all()
    import gen_crops
    gen_crops.build_all()
    import gen_items2
    gen_items2.build_all()
    import gen_armor2
    gen_armor2.build()
    gen_mobs.build()
    import gen_animals
    gen_animals.build()
    import gen_hostiles
    gen_hostiles.build()
    import gen_bosses
    gen_bosses.build()
    import gen_blossom
    gen_blossom.build()
    import gen_seals
    gen_seals.build()
    import gen_ui
    gen_ui.build()
    import gen_music
    gen_music.build()
    gen_world.build_all()
    import gen_world2
    gen_world2.build_all()
    import gen_world3
    gen_world3.build_all()
    registry.write_registries()
    copy_scripts()
    manifests()
    import icon
    icon.build()


def package():
    out_dir = DIST
    os.makedirs(out_dir, exist_ok=True)
    path = f'{out_dir}/{OUT_NAME}.mcaddon'
    if os.path.exists(path):
        os.remove(path)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for root_dir, label in ((BP, 'EclipsedRealms_BP'), (RP, 'EclipsedRealms_RP')):
            for dp, dn, fn in os.walk(root_dir):
                for f in fn:
                    full = os.path.join(dp, f)
                    rel = os.path.relpath(full, root_dir).replace('\\', '/')
                    z.write(full, f'{label}/{rel}')
    return path


if __name__ == '__main__':
    generate()
    if '--no-package' not in sys.argv:
        print(package())
