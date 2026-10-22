"""Crops (4 growth stages, farmland rules, bone meal, right-click harvest), wild crops, seeds, produce, cooked foods, recipes."""
from common import *
from registry import *
from gen_blocks import write_block, mi, cat, loot_simple
from gen_items import write_item, shaped, shapeless, furnace
from gen_wood import WATER_POP

CROPS = {
    # crop:      (plant title, seed item,        produce item,    seed title,         produce title, nutrition, sat, growth chance, bush height)
    'tomato':     ('Tomato Plant', 'tomato_seeds', 'tomato', 'Tomato Seeds', 'Tomato', 3, 0.4, 0.22, 14),
    'corn':       ('Corn Plant', 'corn_kernels', 'corn_cob', 'Corn Kernels', 'Corn Cob', 2, 0.3, 0.18, 16),
    'strawberry': ('Strawberry Bush', 'strawberry_seeds', 'strawberry', 'Strawberry Seeds', 'Strawberry', 2, 0.3, 0.20, 10),
    'chili':      ('Chili Plant', 'chili_seeds', 'chili_pepper', 'Chili Seeds', 'Chili Pepper', 1, 0.2, 0.20, 13),
    'oats':       ('Oat Grass', 'oat_seeds', 'oats', 'Oat Seeds', 'Oats', 0, 0.0, 0.28, 14),
}
GROW_DATA = {c: v[7] for c, v in CROPS.items()}

FOODS = {
    # item: (title, nutrition, saturation, stack, converts_to, animation)
    'roasted_corn': ('Roasted Corn', 6, 0.7, 64, None, 'eat'),
    'oat_bread': ('Oat Bread', 6, 0.6, 64, None, 'eat'),
    'berry_pie': ('Strawberry Pie', 8, 0.5, 64, None, 'eat'),
    'tomato_soup': ('Tomato Soup', 7, 0.6, 1, 'minecraft:bowl', 'eat'),
    'porridge': ('Oat Porridge', 6, 0.7, 1, 'minecraft:bowl', 'eat'),
    'chili_stew': ('Chili Stew', 10, 0.8, 1, 'minecraft:bowl', 'eat'),
    'hunters_stew': ('Hunter\'s Stew', 12, 0.9, 1, 'minecraft:bowl', 'eat'),
    'raw_venison': ('Raw Venison', 3, 0.3, 64, None, 'eat'),
    'cooked_venison': ('Cooked Venison', 8, 0.8, 64, None, 'eat'),
    'raw_yak_meat': ('Raw Yak Meat', 3, 0.3, 64, None, 'eat'),
    'cooked_yak_meat': ('Cooked Yak Meat', 9, 0.8, 64, None, 'eat'),
    'raw_pheasant': ('Raw Pheasant', 2, 0.3, 64, None, 'eat'),
    'cooked_pheasant': ('Cooked Pheasant', 6, 0.7, 64, None, 'eat'),
}

FARMLAND = ['minecraft:farmland']
WILD_SOIL = ['minecraft:grass_block', 'minecraft:dirt', 'minecraft:podzol', 'minecraft:coarse_dirt', 'minecraft:moss_block']


def food_components(nutrition, sat, stack=64, converts=None, anim='eat', always=False, compost=None, seconds=1.6):
    f = {'nutrition': nutrition, 'saturation_modifier': sat}
    if converts:
        f['using_converts_to'] = converts
    if always:
        f['can_always_eat'] = True
    comps = {'minecraft:max_stack_size': stack, 'minecraft:food': f, 'minecraft:use_animation': {'value': anim},
             'minecraft:use_modifiers': {'use_duration': seconds, 'movement_modifier': 0.35},
             'minecraft:tags': {'tags': ['minecraft:is_food']}}
    if compost:
        comps['minecraft:compostable'] = {'composting_chance': compost}
    return comps


def build_crop_blocks():
    for c, (ptitle, seed, produce, stitle, pr_title, nutr, sat, chance, h) in CROPS.items():
        stages = [terrain(f'{c}_stage{s}', f'{c}_stage{s}') for s in range(4)]
        loot = loot_simple(f'{c}_crop', [(f'{NS}:{seed}', 1, 1, 1.0)])
        comps = {
            'minecraft:geometry': 'minecraft:geometry.cross',
            'minecraft:material_instances': {'*': mi(stages[0], 'alpha_test', face_dimming=True)},
            'minecraft:collision_box': False,
            'minecraft:selection_box': {'origin': [-6, 0, -6], 'size': [12, h, 12]},
            'minecraft:light_dampening': 0,
            'minecraft:destructible_by_mining': {'seconds_to_destroy': 0.0},
            'minecraft:destructible_by_explosion': {'explosion_resistance': 0.0},
            'minecraft:flammable': {'catch_chance_modifier': 60, 'destroy_chance_modifier': 100},
            'minecraft:loot': loot,
            'minecraft:map_color': '#5aa83a',
            'minecraft:placement_filter': {'conditions': [{'allowed_faces': ['up'], 'block_filter': FARMLAND}]},
            'minecraft:liquid_detection': WATER_POP,
            'minecraft:tags': ['ecr:crop'],
            f'{NS}:crop': {},
        }
        perms = [{'condition': f"q.block_state('ecr:growth') == {s}", 'components': {
            'minecraft:material_instances': {'*': mi(stages[s], 'alpha_test', face_dimming=True)}}} for s in (1, 2, 3)]
        desc = {'identifier': f'{NS}:{c}_crop', 'menu_category': cat('none'), 'states': {'ecr:growth': [0, 1, 2, 3]}}
        write_block(f'{c}_crop', desc, comps, perms, sound='grass')
        lang_block(f'{c}_crop', ptitle)

        # wild plant: always mature, found in the world
        wt = terrain(f'wild_{c}', f'wild_{c}')
        wloot = {'pools': [
            {'rolls': 1, 'entries': [{'type': 'item', 'name': f'{NS}:{seed}', 'weight': 1, 'functions': [{'function': 'set_count', 'count': {'min': 1, 'max': 2}}]}]},
            {'rolls': 1, 'conditions': [{'condition': 'random_chance', 'chance': 0.6}],
             'entries': [{'type': 'item', 'name': f'{NS}:{produce}', 'weight': 1}]}]}
        wjson(f'{BP}/loot_tables/blocks/wild_{c}.json', wloot)
        wcomps = dict(comps)
        wcomps.pop(f'{NS}:crop', None)
        wcomps['minecraft:material_instances'] = {'*': mi(wt, 'alpha_test', face_dimming=True)}
        wcomps['minecraft:loot'] = f'loot_tables/blocks/wild_{c}.json'
        wcomps['minecraft:placement_filter'] = {'conditions': [{'allowed_faces': ['up'], 'block_filter': WILD_SOIL}]}
        wcomps['minecraft:tags'] = ['ecr:wild_crop']
        write_block(f'wild_{c}', {'identifier': f'{NS}:wild_{c}', 'menu_category': cat('nature', 'minecraft:itemGroup.name.flower')}, wcomps, sound='grass')
        lang_block(f'wild_{c}', f'Wild {ptitle.split()[0]}')


def build_items():
    for c, (ptitle, seed, produce, stitle, pr_title, nutr, sat, chance, h) in CROPS.items():
        # seeds
        comps = {'minecraft:icon': {'textures': {'default': itemtex(seed)}}, 'minecraft:max_stack_size': 64,
                 'minecraft:block_placer': {'block': f'{NS}:{c}_crop', 'use_on': FARMLAND},
                 'minecraft:compostable': {'composting_chance': 30}}
        write_item(seed, comps, 'nature', 'minecraft:itemGroup.name.seed')
        lang_item(seed, stitle)
        # produce
        comps = {'minecraft:icon': {'textures': {'default': itemtex(produce)}}}
        if nutr:
            comps.update(food_components(nutr, sat, always=(c == 'chili'), compost=65))
        else:
            comps.update({'minecraft:max_stack_size': 64, 'minecraft:compostable': {'composting_chance': 65}})
        write_item(produce, comps, 'items', 'minecraft:itemGroup.name.crop')
        lang_item(produce, pr_title)
    for n, (title, nutr, sat, stack, conv, anim) in FOODS.items():
        group = 'minecraft:itemGroup.name.rawFood' if n.startswith('raw_') else 'minecraft:itemGroup.name.cookedFood'
        comps = {'minecraft:icon': {'textures': {'default': itemtex(n)}}}
        comps.update(food_components(nutr, sat, stack, conv, anim, compost=(85 if n in ('oat_bread', 'berry_pie') else None), seconds=(2.4 if stack == 1 else 1.6)))
        write_item(n, comps, 'items', group)
        lang_item(n, title)


def build_recipes():
    B = 'minecraft:bowl'
    n = lambda x: f'{NS}:{x}'
    shapeless('tomato_soup', [n('tomato'), n('tomato'), B], n('tomato_soup'))
    shaped('oat_bread', ['###'], {'#': n('oats')}, n('oat_bread'))
    shapeless('porridge', [n('oats'), n('oats'), 'minecraft:sugar', B], n('porridge'))
    shapeless('berry_pie', [n('strawberry'), n('strawberry'), n('strawberry'), 'minecraft:sugar', 'minecraft:egg'], n('berry_pie'))
    shapeless('chili_stew_venison', [n('chili_pepper'), n('cooked_venison'), B], n('chili_stew'))
    shapeless('chili_stew_beef', [n('chili_pepper'), 'minecraft:cooked_beef', B], n('chili_stew'))
    shapeless('hunters_stew_venison', [n('cooked_venison'), n('tomato'), 'minecraft:potato', B], n('hunters_stew'))
    shapeless('hunters_stew_yak', [n('cooked_yak_meat'), n('tomato'), 'minecraft:potato', B], n('hunters_stew'))
    cook = ['furnace', 'smoker', 'campfire', 'soul_campfire']
    furnace('roasted_corn', n('corn_cob'), n('roasted_corn'), cook)
    furnace('cooked_venison', n('raw_venison'), n('cooked_venison'), cook)
    furnace('cooked_yak_meat', n('raw_yak_meat'), n('cooked_yak_meat'), cook)
    furnace('cooked_pheasant', n('raw_pheasant'), n('cooked_pheasant'), cook)
    # seeds from produce (so you never get stuck without seeds)
    shapeless('tomato_seeds_from_tomato', [n('tomato')], n('tomato_seeds'), 2)
    shapeless('corn_kernels_from_cob', [n('corn_cob')], n('corn_kernels'), 3)
    shapeless('strawberry_seeds_from_berry', [n('strawberry')], n('strawberry_seeds'), 2)
    shapeless('chili_seeds_from_pepper', [n('chili_pepper')], n('chili_seeds'), 2)
    shapeless('oat_seeds_from_oats', [n('oats')], n('oat_seeds'), 2)
    # bone-meal-like fertiliser is vanilla compost; hay for oats
    shaped('hay_from_oats', ['###', '###', '###'], {'#': n('oats')}, 'minecraft:hay_block')


def build_all():
    build_crop_blocks()
    build_items()
    build_recipes()
