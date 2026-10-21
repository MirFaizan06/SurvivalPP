"""Custom armour pipeline: geometry + texture + inventory icon + attachables for every tier, and the Veilbloom Regalia items (boss drop)."""
from common import *
from registry import *
import armor_models as A
import art_swords
from gen_items import write_item, repairable, ENCH_SLOT, ARMOR_KINDS, MATS, IV

GEOM = {'helmet': 'helmet', 'chestplate': 'chestplate', 'leggings': 'leggings', 'boots': 'boots'}
VARS = {'helmet': 'helmet_layer_visible', 'chestplate': 'chest_layer_visible', 'leggings': 'leg_layer_visible', 'boots': 'boot_layer_visible'}

SAKURA = {'tier': 'ecr_sakura', 'title': 'Veilbloom', 'prot': (3, 8, 6, 3), 'armor_factor': 37, 'ench': 25, 'rarity': 'epic'}
SAKURA_NAMES = {'helmet': 'Veilbloom Crown', 'chestplate': 'Veilbloom Haori', 'leggings': 'Veilbloom Hakama', 'boots': 'Veilbloom Geta'}


def attachable(mat, piece):
    name = f'{mat}_{piece}'
    tex = f'textures/models/armor/{name}'
    common_ = {'materials': {'default': 'armor', 'enchanted': 'armor_enchanted'},
               'textures': {'default': tex, 'enchanted': 'textures/misc/enchanted_actor_glint'},
               'geometry': {'default': A.armor_id(mat, piece)}, 'render_controllers': ['controller.render.armor']}
    wjson(f'{RP}/attachables/{name}.json', {'format_version': '1.8.0', 'minecraft:attachable': {'description': {
        'identifier': f'{NS}:{name}', **common_, 'scripts': {'parent_setup': f'variable.{VARS[piece]} = 0.0;'}}}})
    wjson(f'{RP}/attachables/{name}.player.json', {'format_version': '1.10.0', 'minecraft:attachable': {'description': {
        'identifier': f'{NS}:{name}.player', 'item': {f'{NS}:{name}': "query.owner_identifier == 'minecraft:player'"}, **common_,
        'scripts': {'parent_setup': f'variable.{VARS[piece]} = 0.0;', 'animate': ['offset']},
        'animations': {'offset': f'animation.armor.{GEOM[piece]}.offset'}}}})


def sakura_items():
    for kind, slot, grp, mult, title, i in ARMOR_KINDS:
        name = f'sakura_{kind}'
        comps = {
            'minecraft:icon': {'textures': {'default': itemtex(name)}}, 'minecraft:max_stack_size': 1,
            'minecraft:durability': {'max_durability': SAKURA['armor_factor'] * mult},
            'minecraft:wearable': {'slot': f'slot.armor.{slot}', 'protection': SAKURA['prot'][i]},
            'minecraft:enchantable': {'slot': ENCH_SLOT[slot], 'value': SAKURA['ench']},
            'minecraft:repairable': repairable(name, f'{NS}:sakura_shard'),
            'minecraft:tags': {'tags': ['minecraft:is_armor', 'minecraft:trimmable_armors', f'{NS}:sakura_gear']},
            'minecraft:rarity': {'value': SAKURA['rarity']}}
        write_item(name, comps, 'equipment', f'minecraft:itemGroup.name.{grp}')
        lang_item(name, SAKURA_NAMES[kind])
    comps = {'minecraft:icon': {'textures': {'default': itemtex('sakura_shard')}}, 'minecraft:max_stack_size': 64, 'minecraft:rarity': {'value': 'epic'}, 'minecraft:glint': True}
    write_item('sakura_shard', comps, 'items')
    lang_item('sakura_shard', 'Veilbloom Shard')


def build():
    for mat in A.DESIGNS:
        for piece in A.PIECES:
            m, base = A.build_model(mat, piece)
            name = f'{mat}_{piece}'
            wjson(f'{RP}/models/entity/armor_{name}.geo.json', m.export())
            save_png(base, f'{RP}/textures/models/armor/{name}.png')
            save_png(A.icon(m, base, piece), f'{RP}/textures/items/{name}.png')
            attachable(mat, piece)
    sakura_items()
    art_swords.build()
    # shard icon: a single glowing petal
    from PIL import Image, ImageDraw
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pal = {'k': hx('#5a1a3a'), 'a': hx('#a8466f'), 'b': hx('#dc7aa4'), 'c': hx('#f6a8c8'), 'd': hx('#ffe6f0'), 'g': hx('#f7d466')}
    rows = ['......kk........', '.....kcck.......', '....kcddck......', '...kcdddbbk.....', '..kcddbbbbak....', '..kcdbbbbaak....', '..kbbbbbaakk....', '...kbbbaakg.....',
            '....kbaakgg.....', '.....kkkgg......']
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in pal:
                im.putpixel((x + 1, y + 3), pal[ch] + (255,))
    save_png(im, f'{RP}/textures/items/sakura_shard.png')
