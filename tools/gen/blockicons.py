"""3D inventory icons for wood-block items, rendered from the real block geometry + textures."""
import json
from PIL import Image
from common import *
import registry
from blockgeo import Box, geometry
from blockview import render_block
from tex_wood import WOODS


def tex(name):
    return Image.open(f'{RP}/textures/blocks/{name}.png').convert('RGBA')


def wood_of(name):
    for w in WOODS:
        if f'{w}_' in name or name.endswith(w):
            return w
    raise KeyError(name)


def cube_geo(faces):
    return geometry('icon', [Box(-8, 0, -8, 8, 16, 8, faces)])


def fit(img, box=30):
    bb = img.getbbox()
    img = img.crop(bb)
    s = min(box / img.width, box / img.height)
    img = img.resize((max(1, round(img.width * s)), max(1, round(img.height * s))), Image.LANCZOS)
    out = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    out.paste(img, ((32 - img.width) // 2, (32 - img.height) // 2 + 1), img)
    return out


def icon_for(it):
    n, kind = it['name'], it['kind']
    w = wood_of(n)
    stripped = n.startswith('stripped_')
    planks = tex(f'{w}_planks')
    geo_dir = f'{RP}/models/blocks'
    if kind == 'planks':
        return render_block(None, {'*': planks}, None, geo_obj=cube_geo({f: '*' for f in ('north', 'east', 'south', 'west', 'up', 'down')}), size=(256, 256), scale=8, rgba=True)
    if kind in ('log', 'wood'):
        side = tex(f'stripped_{w}_log_side' if stripped else f'{w}_log_side')
        end = tex(f'stripped_{w}_log_top' if stripped else f'{w}_log_top') if kind == 'log' else side
        faces = {'north': 'side', 'east': 'side', 'south': 'side', 'west': 'side', 'up': 'end', 'down': 'end'}
        return render_block(None, {'side': side, 'end': end, '*': side}, None, geo_obj=cube_geo(faces), size=(256, 256), scale=8, rgba=True)
    gmap = {'stairs': 'wood_stairs_bottom_north', 'slab': 'wood_slab_bottom', 'fence_gate': 'wood_gate_closed_north',
            'trapdoor': 'wood_trapdoor_bottom_closed', 'pressure_plate': 'wood_plate', 'button': 'wood_button_up_off'}
    if kind == 'fence':
        g = json.load(open(f'{geo_dir}/wood_fence.geo.json'))
        g['minecraft:geometry'][0]['bones'] = [b for b in g['minecraft:geometry'][0]['bones'] if b['name'] in ('post', 'arm_east', 'arm_west')]
        return render_block(None, {'*': planks}, None, geo_obj=g, size=(256, 256), scale=8, rgba=True)
    g = json.load(open(f'{geo_dir}/{gmap[kind]}.geo.json'))
    sc = {'pressure_plate': 8, 'button': 8}.get(kind, 8)
    return render_block(None, {'*': tex(f'{w}_trapdoor') if kind == 'trapdoor' else planks}, None, geo_obj=g, size=(256, 256), scale=sc, rgba=True)


def build():
    # the registry is filled by gen_wood, so make sure the wood blocks exist first
    for it in registry.WOOD_ITEMS:
        img = fit(icon_for(it))
        save_png(img, f'{RP}/textures/items/{it["name"]}_icon.png')


if __name__ == '__main__':
    import gen_blocks
    gen_blocks.build_all()
    build()
    sel = [f'{RP}/textures/items/{it["name"]}_icon.png' for it in registry.WOOD_ITEMS if it['name'].startswith(('jacaranda', 'stripped_jacaranda', 'amberwood'))]
    up_sheet(sel, PREVIEW + '/wood_icons.png', 6, 7)
