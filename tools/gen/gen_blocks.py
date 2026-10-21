"""All custom blocks: ores, storage blocks, altar, stasis chamber/plate, and the Jacaranda wood set."""
import math
from common import *
from registry import *
from blockgeo import *

BV = '1.26.30'
NETHERITE_ONLY = 'ecr:needs_netherite_pickaxe'


def mi(tex, method='opaque', **kw):
    d = {'texture': tex, 'render_method': method}
    d.update(kw)
    return d


def write_block(name, desc, comps, perms=None, sound=None):
    obj = {'format_version': BV, 'minecraft:block': {'description': desc, 'components': comps}}
    if perms:
        obj['minecraft:block']['permutations'] = perms
    wjson(f'{BP}/blocks/{name}.json', obj)
    BLOCK_IDS.append(f'{NS}:{name}')
    if sound:
        BLOCK_SOUND[f'{NS}:{name}'] = sound


def geo_write(name, boxes):
    ident = f'geometry.ecr_{name}'
    wjson(f'{RP}/models/blocks/{name}.geo.json', geometry(ident, boxes))
    return ident


def cat(category, group=None):
    d = {'category': category}
    if group:
        d['group'] = group
    return d


def loot_simple(name, entries):
    pools = []
    for (item, lo, hi, chance) in entries:
        pool = {'rolls': 1, 'entries': [{'type': 'item', 'name': item, 'weight': 1,
                                          'functions': [{'function': 'set_count', 'count': {'min': lo, 'max': hi}}]}]}
        if chance < 1:
            pool['conditions'] = [{'condition': 'random_chance', 'chance': chance}]
        pools.append(pool)
    wjson(f'{BP}/loot_tables/blocks/{name}.json', {'pools': pools})
    return f'loot_tables/blocks/{name}.json'


# =============================================================== ores + storage blocks
ORES = {
    'azurite_ore': dict(name='Azurite Ore', secs=7.0, resist=9.0, light=3, color='#2f86f0', sound='deepslate', raw='raw_azurite', cnt=(1, 3)),
    'pyrelite_ore': dict(name='Pyrelite Ore', secs=9.0, resist=12.0, light=7, color='#d4440f', sound='netherrack', raw='raw_pyrelite', cnt=(1, 3)),
    'eclipsite_ore': dict(name='Eclipsite Ore', secs=12.0, resist=18.0, light=9, color='#6d27b8', sound='stone', raw='raw_eclipsite', cnt=(1, 2)),
}
STORAGE = {
    'azurite_block': dict(name='Block of Azurite', secs=6.0, resist=14.0, color='#2f86f0', sound='metal', light=2),
    'pyrelite_block': dict(name='Block of Pyrelite', secs=8.0, resist=18.0, color='#d4440f', sound='metal', light=6),
    'eclipsite_block': dict(name='Block of Eclipsite', secs=12.0, resist=30.0, color='#34136a', sound='metal', light=8),
}


def build_ores():
    for n, d in ORES.items():
        key = terrain(n)
        loot = loot_simple(n, [(f'{NS}:{d["raw"]}', d['cnt'][0], d['cnt'][1], 1.0)])
        comps = {
            'minecraft:geometry': 'minecraft:geometry.full_block',
            'minecraft:material_instances': {'*': mi(key)},
            'minecraft:tags': ['minecraft:is_pickaxe_item_destructible', NETHERITE_ONLY, 'stone', 'ecr:ore'],
            'minecraft:destructible_by_mining': {'seconds_to_destroy': d['secs']},
            'minecraft:destructible_by_explosion': {'explosion_resistance': d['resist']},
            'minecraft:light_emission': d['light'],
            'minecraft:map_color': d['color'],
            'minecraft:loot': loot,
            'minecraft:friction': 0.6,
        }
        write_block(n, {'identifier': f'{NS}:{n}', 'menu_category': cat('nature', 'minecraft:itemGroup.name.ore')}, comps, sound=d['sound'])
        lang_block(n, d['name'])
    for n, d in STORAGE.items():
        key = terrain(n)
        comps = {
            'minecraft:geometry': 'minecraft:geometry.full_block',
            'minecraft:material_instances': {'*': mi(key)},
            'minecraft:tags': ['minecraft:is_pickaxe_item_destructible', 'metal'],
            'minecraft:destructible_by_mining': {'seconds_to_destroy': d['secs']},
            'minecraft:destructible_by_explosion': {'explosion_resistance': d['resist']},
            'minecraft:light_emission': d['light'],
            'minecraft:map_color': d['color'],
        }
        write_block(n, {'identifier': f'{NS}:{n}', 'menu_category': cat('construction')}, comps, sound=d['sound'])
        lang_block(n, d['name'])


# =============================================================== eclipse altar
def build_altar():
    t_top, t_side, t_bot = terrain('eclipse_altar_top'), terrain('eclipse_altar_side'), terrain('eclipse_altar_bottom')
    comps = {
        'minecraft:geometry': 'minecraft:geometry.full_block',
        'minecraft:material_instances': {'*': mi(t_side), 'up': mi(t_top), 'down': mi(t_bot), 'side': mi(t_side)},
        'minecraft:tags': ['minecraft:is_pickaxe_item_destructible', 'stone'],
        'minecraft:destructible_by_mining': {'seconds_to_destroy': 30.0},
        'minecraft:destructible_by_explosion': {'explosion_resistance': 1200.0},
        'minecraft:light_emission': 6,
        'minecraft:map_color': '#1c1033',
        f'{NS}:altar': {},
    }
    write_block('eclipse_altar', {'identifier': f'{NS}:eclipse_altar', 'menu_category': cat('construction')}, comps, sound='stone')
    lang_block('eclipse_altar', 'Eclipse Altar')


# =============================================================== stasis chamber + plate
def chamber_boxes(loaded):
    F, G, P = 'frame', 'glass', 'pearl'
    boxes = []
    boxes.append(('frame', Box(-8, 0, -8, 8, 2, 8, F)))                       # base plate
    boxes.append(('frame', Box(-8, 14, -8, 8, 16, 8, F)))                     # cap
    for sx in (-8, 6):
        for sz in (-8, 6):
            boxes.append(('frame', Box(sx, 2, sz, sx + 2, 14, sz + 2, F)))    # corner posts
    boxes.append(('frame', Box(-6, 2, -6, 6, 3, 6, F)))                       # inner plinth
    boxes.append(('glass', Box(-6, 3, -6, 6, 14, 6, G)))                      # glass body
    # glass panes on the four sides, slightly proud
    for k in range(4):
        boxes.append(('glass', rot_y(Box(-6, 3, -7.2, 6, 14, -6.2, G), k)))
    # pearl cluster inside
    pb = [Box(-2.5, 6, -2.5, 2.5, 11, 2.5, P), Box(-1.5, 5, -1.5, 1.5, 12, 1.5, P), Box(-3.5, 7, -1.5, 3.5, 10, 1.5, P), Box(-1.5, 7, -3.5, 1.5, 10, 3.5, P)]
    for b in pb:
        boxes.append(('pearl', b))
    return boxes


def build_stasis():
    fr, gl, pe = terrain('stasis_frame'), terrain('stasis_glass'), terrain('stasis_pearl')
    ident = geo_write('stasis_chamber', chamber_boxes(True))
    inst = {'frame': mi(fr, 'blend'), 'glass': mi(gl, 'blend'), 'pearl': mi(pe, 'blend', face_dimming=False), '*': mi(fr, 'blend')}
    comps = {
        'minecraft:geometry': {'identifier': ident, 'bone_visibility': {'frame': 1, 'glass': 1, 'pearl': 0}},
        'minecraft:material_instances': inst,
        'minecraft:tags': ['minecraft:is_pickaxe_item_destructible', 'metal', 'ecr:stasis'],
        'minecraft:destructible_by_mining': {'seconds_to_destroy': 3.5},
        'minecraft:destructible_by_explosion': {'explosion_resistance': 20.0},
        'minecraft:light_dampening': 0,
        'minecraft:light_emission': 0,
        'minecraft:map_color': '#453a63',
        'minecraft:loot': loot_simple('stasis_chamber', [(f'{NS}:stasis_chamber', 1, 1, 1.0)]),
        f'{NS}:stasis_chamber': {},
    }
    perms = [{'condition': "q.block_state('ecr:loaded') == 1", 'components': {
        'minecraft:geometry': {'identifier': ident, 'bone_visibility': {'frame': 1, 'glass': 1, 'pearl': 1}},
        'minecraft:light_emission': 9}}]
    desc = {'identifier': f'{NS}:stasis_chamber', 'menu_category': cat('items'), 'states': {'ecr:loaded': [0, 1]}}
    write_block('stasis_chamber', desc, comps, perms, sound='glass')
    lang_block('stasis_chamber', 'Stasis Chamber')

    # ---- plate
    top, side = terrain('stasis_plate_top'), terrain('stasis_plate_side')
    up = [Box(-7, 0, -7, 7, 2, 7, {'up': 'top', 'down': 'side', 'north': 'side', 'south': 'side', 'east': 'side', 'west': 'side'}, uvmap={'up': (1, 1, 14, 14)})]
    dn = [Box(-7, 0, -7, 7, 1, 7, {'up': 'top', 'down': 'side', 'north': 'side', 'south': 'side', 'east': 'side', 'west': 'side'}, uvmap={'up': (1, 1, 14, 14)})]
    g_up = geo_write('stasis_plate', up)
    g_dn = geo_write('stasis_plate_pressed', dn)
    inst = {'top': mi(top), 'side': mi(side), '*': mi(side)}
    comps = {
        'minecraft:geometry': g_up,
        'minecraft:material_instances': inst,
        'minecraft:collision_box': False,
        'minecraft:selection_box': {'origin': [-7, 0, -7], 'size': [14, 2, 14]},
        'minecraft:tags': ['minecraft:is_pickaxe_item_destructible', 'stone', 'ecr:stasis'],
        'minecraft:destructible_by_mining': {'seconds_to_destroy': 1.5},
        'minecraft:destructible_by_explosion': {'explosion_resistance': 6.0},
        'minecraft:light_dampening': 0,
        'minecraft:light_emission': 3,
        'minecraft:map_color': '#150a2b',
        'minecraft:loot': loot_simple('stasis_plate', [(f'{NS}:stasis_plate', 1, 1, 1.0)]),
        f'{NS}:stasis_plate': {},
    }
    perms = [{'condition': "q.block_state('ecr:powered') == 1", 'components': {
        'minecraft:geometry': g_dn,
        'minecraft:light_emission': 12,
        'minecraft:redstone_producer': {'power': 15, 'strongly_powered_face': 'down'}}}]
    desc = {'identifier': f'{NS}:stasis_plate', 'menu_category': cat('construction', 'minecraft:itemGroup.name.pressurePlate'), 'states': {'ecr:powered': [0, 1]}}
    write_block('stasis_plate', desc, comps, perms, sound='stone')
    lang_block('stasis_plate', 'Stasis Trigger Plate')


# =============================================================== Sanctum Warden (zone protection block)
def build_sanctum():
    st, eye, top = terrain('sanctum_stone'), terrain('sanctum_eye'), terrain('sanctum_top')
    full = (0, 0, 16, 16)
    boxes = [
        ('block', Box(-8, 0, -8, 8, 3, 8, 'stone')),
        ('block', Box(-5, 3, -5, 5, 13, 5, {'north': 'eye', 'south': 'eye', 'east': 'eye', 'west': 'eye', 'up': 'stone', 'down': 'stone'},
                      uvmap={'north': full, 'south': full, 'east': full, 'west': full})),
        ('block', Box(-7, 13, -7, 7, 16, 7, {'up': 'top', 'down': 'stone', 'north': 'stone', 'south': 'stone', 'east': 'stone', 'west': 'stone'},
                      uvmap={'up': (1, 1, 14, 14)})),
    ]
    for sx in (-8, 6):
        for sz in (-8, 6):
            boxes.append(('block', Box(sx, 3, sz, sx + 2, 11, sz + 2, 'stone')))
            boxes.append(('block', Box(sx + 0.25, 11, sz + 0.25, sx + 1.75, 12.5, sz + 1.75, 'eye', uvmap={f: (6, 6, 4, 4) for f in FACES})))
    g = geo_write('sanctum_warden', boxes)
    comps = {
        'minecraft:geometry': g,
        'minecraft:material_instances': {'stone': mi(st), 'eye': mi(eye), 'top': mi(top), '*': mi(st)},
        'minecraft:tags': ['minecraft:is_pickaxe_item_destructible', 'stone', 'ecr:sanctum'],
        'minecraft:destructible_by_mining': {'seconds_to_destroy': 40.0},
        'minecraft:destructible_by_explosion': {'explosion_resistance': 3600000.0},
        'minecraft:light_emission': 7,
        'minecraft:map_color': '#127aa6',
        'minecraft:loot': loot_simple('sanctum_warden', [(f'{NS}:sanctum_warden', 1, 1, 1.0)]),
        f'{NS}:sanctum': {},
    }
    write_block('sanctum_warden', {'identifier': f'{NS}:sanctum_warden', 'menu_category': cat('items')}, comps, sound='stone')
    lang_block('sanctum_warden', 'Sanctum Warden')


def build_all():
    build_ores()
    build_altar()
    build_stasis()
    build_sanctum()
    import gen_wood
    gen_wood.build_all()
    import gen_stone
    gen_stone.build_all()


if __name__ == '__main__':
    build_all()
    print(len(BLOCK_IDS), 'blocks')
