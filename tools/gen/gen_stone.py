"""New natural stone families: base, polished, bricks + stairs / slabs / double slabs, with recipes."""
from common import *
from registry import *
from blockgeo import *
from gen_blocks import write_block, mi, cat, loot_simple
from gen_wood import stair_boxes, DIRS, WATER_BLOCK
from tex_stone import STONES

GROUP_STONE = 'minecraft:itemGroup.name.stone'
GROUP_BRICK = 'minecraft:itemGroup.name.stoneBrick'


def common(spec, secs=None, resist=None):
    return {
        'minecraft:tags': ['minecraft:is_pickaxe_item_destructible', 'stone'],
        'minecraft:destructible_by_mining': {'seconds_to_destroy': secs or spec['secs']},
        'minecraft:destructible_by_explosion': {'explosion_resistance': resist or spec['resist']},
        'minecraft:map_color': spec['map'],
    }


def cube(name, tex, title, spec, category, group):
    comps = {'minecraft:geometry': 'minecraft:geometry.full_block', 'minecraft:material_instances': {'*': mi(terrain(tex))}, **common(spec)}
    write_block(name, {'identifier': f'{NS}:{name}', 'menu_category': cat(category, group)}, comps, sound=spec['sound'])
    lang_block(name, title)


def shapes(base, tex, title, spec):
    inst = {'*': mi(terrain(tex))}
    perms = []
    for half in ('bottom', 'top'):
        for k, d in enumerate(DIRS):
            boxes = [rot_y(b, k) for b in stair_boxes(half)]
            perms.append({'condition': f"q.block_state('minecraft:cardinal_direction') == '{d}' && q.block_state('minecraft:vertical_half') == '{half}'",
                          'components': {'minecraft:geometry': f'geometry.ecr_wood_stairs_{half}_{d}', 'minecraft:collision_box': boxes_to_collision(boxes)}})
    comps = {'minecraft:geometry': 'geometry.ecr_wood_stairs_bottom_north', 'minecraft:material_instances': inst,
             'minecraft:collision_box': boxes_to_collision(stair_boxes('bottom')), 'minecraft:support': {'shape': 'stair'},
             'minecraft:liquid_detection': WATER_BLOCK, **common(spec)}
    desc = {'identifier': f'{NS}:{base}_stairs', 'menu_category': cat('construction', 'minecraft:itemGroup.name.stairs'),
            'traits': {'minecraft:placement_direction': {'enabled_states': ['minecraft:cardinal_direction']},
                       'minecraft:placement_position': {'enabled_states': ['minecraft:vertical_half']}}}
    write_block(f'{base}_stairs', desc, comps, perms, sound=spec['sound'])
    lang_block(f'{base}_stairs', f'{title} Stairs')

    bot, top = [Box(-8, 0, -8, 8, 8, 8)], [Box(-8, 8, -8, 8, 16, 8)]
    comps = {'minecraft:geometry': 'geometry.ecr_wood_slab_bottom', 'minecraft:material_instances': inst,
             'minecraft:collision_box': boxes_to_collision(bot)[0], 'minecraft:selection_box': boxes_to_collision(bot)[0],
             'minecraft:liquid_detection': WATER_BLOCK, **common(spec)}
    perms = [{'condition': "q.block_state('minecraft:vertical_half') == 'top'", 'components': {
        'minecraft:geometry': 'geometry.ecr_wood_slab_top', 'minecraft:collision_box': boxes_to_collision(top)[0], 'minecraft:selection_box': boxes_to_collision(top)[0]}}]
    desc = {'identifier': f'{NS}:{base}_slab', 'menu_category': cat('construction', 'minecraft:itemGroup.name.slab'),
            'traits': {'minecraft:placement_position': {'enabled_states': ['minecraft:vertical_half']}}}
    write_block(f'{base}_slab', desc, comps, perms, sound=spec['sound'])
    lang_block(f'{base}_slab', f'{title} Slab')

    comps = {'minecraft:geometry': 'minecraft:geometry.full_block', 'minecraft:material_instances': inst,
             'minecraft:loot': loot_simple(f'{base}_double_slab', [(f'{NS}:{base}_slab', 2, 2, 1.0)]), **common(spec)}
    write_block(f'{base}_double_slab', {'identifier': f'{NS}:{base}_double_slab', 'menu_category': cat('none')}, comps, sound=spec['sound'])
    lang_block(f'{base}_double_slab', f'{title} Double Slab')


def build_blocks():
    for v, spec in STONES.items():
        T = spec['title']
        cube(v, v, T, spec, 'nature', GROUP_STONE)
        cube(f'polished_{v}', f'polished_{v}', f'Polished {T}', spec, 'construction', GROUP_STONE)
        cube(f'{v}_bricks', f'{v}_bricks', f'{T} Bricks', spec, 'construction', GROUP_BRICK)
        shapes(f'polished_{v}', f'polished_{v}', f'Polished {T}', spec)
        shapes(f'{v}_bricks', f'{v}_bricks', f'{T} Brick', spec)


def build_recipes():
    from gen_items import shaped, shapeless
    for v in STONES:
        P, B = f'{NS}:polished_{v}', f'{NS}:{v}_bricks'
        shaped(f'polished_{v}', ['##', '##'], {'#': f'{NS}:{v}'}, P, 4)
        shaped(f'{v}_bricks', ['##', '##'], {'#': P}, B, 4)
        for base, item in ((f'polished_{v}', P), (f'{v}_bricks', B)):
            shaped(f'{base}_stairs', ['#  ', '## ', '###'], {'#': item}, f'{NS}:{base}_stairs', 4)
            shaped(f'{base}_slab', ['###'], {'#': item}, f'{NS}:{base}_slab', 6)
        # stonecutter shortcuts
        for out, cnt, src in ((f'{NS}:polished_{v}', 1, f'{NS}:{v}'), (B, 1, f'{NS}:{v}'), (B, 1, P),
                              (f'{NS}:polished_{v}_stairs', 1, f'{NS}:{v}'), (f'{NS}:polished_{v}_slab', 2, f'{NS}:{v}'),
                              (f'{NS}:{v}_bricks_stairs', 1, f'{NS}:{v}'), (f'{NS}:{v}_bricks_slab', 2, f'{NS}:{v}')):
            name = f"cut_{out.split(':')[1]}_from_{src.split(':')[1]}"
            wjson(f'{BP}/recipes/{name}.json', {'format_version': '1.20.10', 'minecraft:recipe_shapeless': {
                'description': {'identifier': f'{NS}:{name}'}, 'tags': ['stonecutter'], 'ingredients': [{'item': src}], 'unlock': {'context': 'AlwaysUnlocked'}, 'result': {'item': out, 'count': cnt}}})


def build_all():
    build_blocks()
