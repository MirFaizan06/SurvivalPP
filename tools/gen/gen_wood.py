"""Full wood sets (log, stripped log, wood, stripped wood, planks, stairs, slab, double slab, fence, gate,
trapdoor, door, plate, button, leaves, sapling) for every tree species. Geometry is shared between species."""
from common import *
from registry import *
from blockgeo import *
from gen_blocks import write_block as _write_block, geo_write, mi, cat, loot_simple
from tex_wood import WOODS

WATER_BLOCK = {'detection_rules': [{'liquid_type': 'water', 'can_contain_liquid': True, 'on_liquid_touches': 'blocking'}]}
WATER_POP = {'detection_rules': [{'liquid_type': 'water', 'can_contain_liquid': False, 'on_liquid_touches': 'popped'}]}
FUEL = {'log': 15, 'wood': 15, 'planks': 15, 'stairs': 15, 'fence': 15, 'fence_gate': 15, 'trapdoor': 15, 'pressure_plate': 15, 'slab': 7.5, 'button': 5}


def wb(name, desc, comps, perms=None, sound=None):
    """write a wood block; wood blocks get a block-placer item (fuel, vanilla tags, 3D icon) instead of the auto item"""
    kind = None
    for suf in ('pressure_plate', 'fence_gate', 'stairs', 'slab', 'fence', 'trapdoor', 'button', 'planks', 'log', 'wood'):
        if name.endswith('_' + suf):
            kind = suf
            break
    if kind in ('stairs', 'slab', 'fence', 'trapdoor'):
        comps['minecraft:liquid_detection'] = WATER_BLOCK
    if kind in ('button', 'pressure_plate') or name.endswith('_sapling'):
        comps['minecraft:liquid_detection'] = WATER_POP
    if name.endswith('_door') or kind in ('fence_gate', 'trapdoor'):
        comps['minecraft:redstone_consumer'] = {'min_power': 0, 'propagates_power': False}
    mc = desc.get('menu_category', {})
    if kind in FUEL and mc.get('category') not in (None, 'none'):
        tags = []
        if kind == 'planks':
            tags = ['minecraft:planks']
        elif kind in ('log', 'wood'):
            tags = ['minecraft:logs', 'minecraft:logs_that_burn']
        elif kind == 'slab':
            tags = ['minecraft:wooden_slabs']
        WOOD_ITEMS.append(dict(name=name, kind=kind, category=mc['category'], group=mc.get('group'), fuel=FUEL[kind], tags=tags))
        desc = dict(desc)
        desc['menu_category'] = {'category': 'none'}
    _write_block(name, desc, comps, perms, sound=sound)

DIRS = ['north', 'west', 'south', 'east']
FLAM_WOOD = {'catch_chance_modifier': 5, 'destroy_chance_modifier': 20}
FLAM_LOG = {'catch_chance_modifier': 5, 'destroy_chance_modifier': 5}
DIRT = ['minecraft:grass_block', 'minecraft:dirt', 'minecraft:podzol', 'minecraft:coarse_dirt', 'minecraft:mud', 'minecraft:moss_block', 'minecraft:dirt_with_roots']


def wood_common(spec, secs=2.0, resist=3.0, flam=FLAM_WOOD, color=None):
    return {
        'minecraft:destructible_by_mining': {'seconds_to_destroy': secs},
        'minecraft:destructible_by_explosion': {'explosion_resistance': resist},
        'minecraft:flammable': flam,
        'minecraft:map_color': color or spec['map'],
    }


def rot_h(src, dst):
    from PIL import Image
    im = Image.open(f'{RP}/textures/blocks/{src}.png').convert('RGBA').rotate(90)
    save_png(im, f'{RP}/textures/blocks/{dst}.png')


# ------------------------------------------------------------------------------ shared geometry
def stair_boxes(half):
    if half == 'bottom':
        return [Box(-8, 0, -8, 8, 8, 8), Box(-8, 8, -8, 8, 16, 0)]
    return [Box(-8, 8, -8, 8, 16, 8), Box(-8, 0, -8, 8, 8, 0)]


def fence_parts():
    post = [Box(-2, 0, -2, 2, 16, 2)]
    base_arm = [Box(-1, 12, -8, 1, 15, -2), Box(-1, 6, -8, 1, 9, -2)]
    return post, {d: [rot_y(b, k) for b in base_arm] for k, d in enumerate(DIRS)}


def gate_boxes(open_):
    posts = [Box(-8, 5, -1, -6, 16, 1), Box(6, 5, -1, 8, 16, 1)]
    if not open_:
        bars = [Box(-6, 6, -0.5, 6, 9, 0.5), Box(-6, 12, -0.5, 6, 15, 0.5), Box(-2, 9, -0.5, 2, 12, 0.5), Box(-6, 9, -0.5, -4, 12, 0.5), Box(4, 9, -0.5, 6, 12, 0.5)]
    else:
        bars = [Box(-8, 6, -7, -6.5, 9, -1), Box(-8, 12, -7, -6.5, 15, -1), Box(-8, 9, -3.5, -6.5, 12, -1),
                Box(6.5, 6, -7, 8, 9, -1), Box(6.5, 12, -7, 8, 15, -1), Box(6.5, 9, -3.5, 8, 12, -1)]
    return posts + bars


def trapdoor_boxes(half, open_, k):
    if not open_:
        return [Box(-8, 0, -8, 8, 3, 8) if half == 'bottom' else Box(-8, 13, -8, 8, 16, 8)]
    return [rot_y(Box(-8, 0, 5, 8, 16, 8), k)]


def door_boxes(open_, hinge_right, k):
    if not open_:
        b = Box(-8, 0, 5, 8, 16, 8)
    else:
        b = Box(5, 0, -8, 8, 16, 8) if hinge_right else Box(-8, 0, -8, -5, 16, 8)
    return [rot_y(b, k)]


def write_shared_geometry():
    for half in ('bottom', 'top'):
        for k, d in enumerate(DIRS):
            geo_write(f'wood_stairs_{half}_{d}', [rot_y(b, k) for b in stair_boxes(half)])
    geo_write('wood_slab_bottom', [Box(-8, 0, -8, 8, 8, 8)])
    geo_write('wood_slab_top', [Box(-8, 8, -8, 8, 16, 8)])
    post, arms = fence_parts()
    boxes = [('post', b) for b in post]
    for d in DIRS:
        boxes += [(f'arm_{d}', b) for b in arms[d]]
    geo_write('wood_fence', boxes)
    for open_ in (False, True):
        for k, d in enumerate(DIRS):
            geo_write(f'wood_gate_{"open" if open_ else "closed"}_{d}', [rot_y(b, k) for b in gate_boxes(open_)])
    for half in ('bottom', 'top'):
        for open_ in (False, True):
            for k, d in enumerate(DIRS):
                if not open_ and k > 0:
                    continue
                if open_ and half == 'top':
                    continue
                geo_write(f'wood_trapdoor_{half}_{"open" if open_ else "closed"}' + (f'_{d}' if open_ else ''), trapdoor_boxes(half, open_, k))
    for open_ in (False, True):
        for hinge in (False, True):
            if not open_ and hinge:
                continue
            for k, d in enumerate(DIRS):
                geo_write(f'wood_door_{"open" if open_ else "closed"}{"_r" if hinge else ""}_{d}', door_boxes(open_, hinge, k))
    geo_write('wood_plate', [Box(-7, 0, -7, 7, 1, 7)])
    geo_write('wood_plate_pressed', [Box(-7, 0, -7, 7, 0.5, 7)])
    tf = {'up': lambda b: b, 'down': lambda b: rot_x(b, 2), 'north': lambda b: rot_x(b, 1), 'south': lambda b: rot_x(b, 3),
          'east': lambda b: rot_z(b, 1), 'west': lambda b: rot_z(b, 3)}
    for face, fn in tf.items():
        for pressed in (False, True):
            geo_write(f'wood_button_{face}_{"on" if pressed else "off"}', [fn(Box(-3, 0, -2, 3, 1 if pressed else 2, 2))])


# ------------------------------------------------------------------------------ per-species blocks
def build_logs(w, spec):
    T = spec['title']
    for n in (f'{w}_log_side', f'stripped_{w}_log_side'):
        rot_h(n, n + '_h')
    sets = {
        f'{w}_log': (f'{w}_log_side', f'{w}_log_top', f'{T} Log'),
        f'stripped_{w}_log': (f'stripped_{w}_log_side', f'stripped_{w}_log_top', f'Stripped {T} Log'),
        f'{w}_wood': (f'{w}_log_side', f'{w}_log_side', f'{T} Wood'),
        f'stripped_{w}_wood': (f'stripped_{w}_log_side', f'stripped_{w}_log_side', f'Stripped {T} Wood'),
    }
    for n, (side, end, title) in sets.items():
        s, sh, e = terrain(side), terrain(side + '_h'), terrain(end)
        comps = {
            'minecraft:geometry': 'minecraft:geometry.full_block',
            'minecraft:material_instances': {'*': mi(s), 'up': mi(e), 'down': mi(e), 'side': mi(s)},
            'minecraft:tags': ['minecraft:is_axe_item_destructible', 'wood', 'log', f'{NS}:{w}_logs'],
            **wood_common(spec, 2.0, 2.0, FLAM_LOG),
        }
        xax = {'*': mi(sh), 'east': mi(e), 'west': mi(e), 'up': mi(sh), 'down': mi(sh), 'north': mi(sh), 'south': mi(sh)}
        zax = {'*': mi(sh), 'north': mi(e), 'south': mi(e), 'up': mi(s), 'down': mi(s), 'east': mi(sh), 'west': mi(sh)}
        perms = [
            {'condition': "q.block_state('minecraft:block_face') == 'east' || q.block_state('minecraft:block_face') == 'west'", 'components': {'minecraft:material_instances': xax}},
            {'condition': "q.block_state('minecraft:block_face') == 'north' || q.block_state('minecraft:block_face') == 'south'", 'components': {'minecraft:material_instances': zax}},
        ]
        desc = {'identifier': f'{NS}:{n}', 'menu_category': cat('nature', 'minecraft:itemGroup.name.log'),
                'traits': {'minecraft:placement_position': {'enabled_states': ['minecraft:block_face']}}}
        wb(n, desc, comps, perms, sound=spec['sound'])
        lang_block(n, title)


def build_planks(w, spec):
    T = spec['title']
    p = terrain(f'{w}_planks')
    comps = {
        'minecraft:geometry': 'minecraft:geometry.full_block',
        'minecraft:material_instances': {'*': mi(p)},
        'minecraft:tags': ['minecraft:is_axe_item_destructible', 'wood', f'{NS}:{w}_planks'],
        **wood_common(spec, 2.0, 3.0),
    }
    wb(f'{w}_planks', {'identifier': f'{NS}:{w}_planks', 'menu_category': cat('construction', 'minecraft:itemGroup.name.planks')}, comps, sound=spec['sound'])
    lang_block(f'{w}_planks', f'{T} Planks')
    comps2 = dict(comps)
    comps2['minecraft:loot'] = loot_simple(f'{w}_double_slab', [(f'{NS}:{w}_slab', 2, 2, 1.0)])
    wb(f'{w}_double_slab', {'identifier': f'{NS}:{w}_double_slab', 'menu_category': cat('none')}, comps2, sound=spec['sound'])
    lang_block(f'{w}_double_slab', f'{T} Double Slab')


def build_leaves_sapling(w, spec):
    T = spec['title']
    lf = terrain(f'{w}_leaves')
    comps = {
        'minecraft:geometry': {'identifier': 'minecraft:geometry.full_block', 'culling_layer': 'minecraft:culling_layer.leaves'},
        'minecraft:material_instances': {'*': mi(lf, 'alpha_test_single_sided')},
        'minecraft:tags': ['minecraft:is_hoe_item_destructible', 'minecraft:is_shears_item_destructible', 'leaves', f'{NS}:{w}_leaves'],
        'minecraft:light_dampening': 1,
        'minecraft:destructible_by_mining': {'seconds_to_destroy': 0.2},
        'minecraft:destructible_by_explosion': {'explosion_resistance': 0.2},
        'minecraft:flammable': {'catch_chance_modifier': 30, 'destroy_chance_modifier': 60},
        'minecraft:map_color': spec['leaf_map'],
        'minecraft:loot': f'loot_tables/blocks/{w}_leaves.json',
        f'{NS}:leaves': {},
    }
    wjson(f'{BP}/loot_tables/blocks/{w}_leaves.json', {'pools': [
        {'rolls': 1, 'conditions': [{'condition': 'match_tool', 'item': 'minecraft:shears'}],
         'entries': [{'type': 'item', 'name': f'{NS}:{w}_leaves', 'weight': 1}]},
        {'rolls': 1, 'conditions': [{'condition': 'random_chance', 'chance': 0.06}],
         'entries': [{'type': 'item', 'name': f'{NS}:{w}_sapling', 'weight': 1}]},
        {'rolls': 1, 'conditions': [{'condition': 'random_chance', 'chance': 0.03}],
         'entries': [{'type': 'item', 'name': 'minecraft:stick', 'weight': 1, 'functions': [{'function': 'set_count', 'count': {'min': 1, 'max': 2}}]}]}]})
    desc = {'identifier': f'{NS}:{w}_leaves', 'menu_category': cat('nature', 'minecraft:itemGroup.name.leaves'), 'states': {'ecr:persistent': [0, 1]}}
    wb(f'{w}_leaves', desc, comps, sound='grass')
    lang_block(f'{w}_leaves', f'{T} Leaves')

    sp = terrain(f'{w}_sapling')
    comps = {
        'minecraft:geometry': 'minecraft:geometry.cross',
        'minecraft:material_instances': {'*': mi(sp, 'alpha_test', face_dimming=False)},
        'minecraft:collision_box': False,
        'minecraft:selection_box': {'origin': [-6, 0, -6], 'size': [12, 12, 12]},
        'minecraft:light_dampening': 0,
        'minecraft:destructible_by_mining': {'seconds_to_destroy': 0.0},
        'minecraft:destructible_by_explosion': {'explosion_resistance': 0.0},
        'minecraft:flammable': {'catch_chance_modifier': 60, 'destroy_chance_modifier': 100},
        'minecraft:map_color': spec['leaf_map'],
        'minecraft:loot': loot_simple(f'{w}_sapling', [(f'{NS}:{w}_sapling', 1, 1, 1.0)]),
        'minecraft:placement_filter': {'conditions': [{'allowed_faces': ['up'], 'block_filter': DIRT}]},
        f'{NS}:sapling': {},
    }
    wb(f'{w}_sapling', {'identifier': f'{NS}:{w}_sapling', 'menu_category': cat('none')}, comps, sound='grass')
    lang_block(f'{w}_sapling', f'{T} Sapling')


def build_stairs_slabs(w, spec):
    T = spec['title']
    inst = {'*': mi(terrain(f'{w}_planks'))}
    perms = []
    for half in ('bottom', 'top'):
        for k, d in enumerate(DIRS):
            boxes = [rot_y(b, k) for b in stair_boxes(half)]
            perms.append({'condition': f"q.block_state('minecraft:cardinal_direction') == '{d}' && q.block_state('minecraft:vertical_half') == '{half}'",
                          'components': {'minecraft:geometry': f'geometry.ecr_wood_stairs_{half}_{d}', 'minecraft:collision_box': boxes_to_collision(boxes)}})
    comps = {
        'minecraft:geometry': 'geometry.ecr_wood_stairs_bottom_north',
        'minecraft:material_instances': inst,
        'minecraft:collision_box': boxes_to_collision(stair_boxes('bottom')),
        'minecraft:tags': ['minecraft:is_axe_item_destructible', 'wood'],
        'minecraft:support': {'shape': 'stair'},
        **wood_common(spec, 2.0, 3.0),
    }
    desc = {'identifier': f'{NS}:{w}_stairs', 'menu_category': cat('construction', 'minecraft:itemGroup.name.stairs'),
            'traits': {'minecraft:placement_direction': {'enabled_states': ['minecraft:cardinal_direction']},
                       'minecraft:placement_position': {'enabled_states': ['minecraft:vertical_half']}}}
    wb(f'{w}_stairs', desc, comps, perms, sound=spec['sound'])
    lang_block(f'{w}_stairs', f'{T} Stairs')

    bot, top = [Box(-8, 0, -8, 8, 8, 8)], [Box(-8, 8, -8, 8, 16, 8)]
    comps = {
        'minecraft:geometry': 'geometry.ecr_wood_slab_bottom',
        'minecraft:material_instances': inst,
        'minecraft:collision_box': boxes_to_collision(bot)[0],
        'minecraft:selection_box': boxes_to_collision(bot)[0],
        'minecraft:tags': ['minecraft:is_axe_item_destructible', 'wood'],
        **wood_common(spec, 2.0, 3.0),
    }
    perms = [{'condition': "q.block_state('minecraft:vertical_half') == 'top'", 'components': {
        'minecraft:geometry': 'geometry.ecr_wood_slab_top', 'minecraft:collision_box': boxes_to_collision(top)[0], 'minecraft:selection_box': boxes_to_collision(top)[0]}}]
    desc = {'identifier': f'{NS}:{w}_slab', 'menu_category': cat('construction', 'minecraft:itemGroup.name.slab'),
            'traits': {'minecraft:placement_position': {'enabled_states': ['minecraft:vertical_half']}}}
    wb(f'{w}_slab', desc, comps, perms, sound=spec['sound'])
    lang_block(f'{w}_slab', f'{T} Slab')


def build_fence(w, spec):
    p = terrain(f'{w}_planks')
    conn = {'north': 'minecraft:connection_north', 'south': 'minecraft:connection_south', 'east': 'minecraft:connection_east', 'west': 'minecraft:connection_west'}
    vis = {'post': 1}
    for d in DIRS:
        vis[f'arm_{d}'] = f"q.block_state('{conn[d]}')"
    coll_post = {'origin': [-2, 0, -2], 'size': [4, 24, 4]}
    arm_coll = {'north': {'origin': [-1, 0, -8], 'size': [2, 24, 6]}, 'south': {'origin': [-1, 0, 2], 'size': [2, 24, 6]},
                'east': {'origin': [2, 0, -1], 'size': [6, 24, 2]}, 'west': {'origin': [-8, 0, -1], 'size': [6, 24, 2]}}
    perms = []
    for mask in range(16):
        cond, cols = [], [coll_post]
        for i, d in enumerate(['north', 'east', 'south', 'west']):
            on = bool(mask & (1 << i))
            cond.append(f"{'' if on else '!'}q.block_state('{conn[d]}')")
            if on:
                cols.append(arm_coll[d])
        perms.append({'condition': ' && '.join(cond), 'components': {'minecraft:collision_box': cols}})
    comps = {
        'minecraft:geometry': {'identifier': 'geometry.ecr_wood_fence', 'bone_visibility': vis},
        'minecraft:material_instances': {'*': mi(p)},
        'minecraft:collision_box': coll_post,
        'minecraft:selection_box': {'origin': [-2, 0, -2], 'size': [4, 16, 4]},
        'minecraft:tags': ['minecraft:is_axe_item_destructible', 'wood', 'fence'],
        'minecraft:support': {'shape': 'fence'},
        **wood_common(spec, 2.0, 3.0),
    }
    desc = {'identifier': f'{NS}:{w}_fence', 'menu_category': cat('construction', 'minecraft:itemGroup.name.fence'),
            'traits': {'minecraft:connection': {'enabled_states': ['minecraft:cardinal_connections']}}}
    wb(f'{w}_fence', desc, comps, perms, sound=spec['sound'])
    lang_block(f'{w}_fence', f'{spec["title"]} Fence')


def build_gate(w, spec):
    p = terrain(f'{w}_planks')
    perms = []
    for open_ in (False, True):
        for k, d in enumerate(DIRS):
            coll = False if open_ else boxes_to_collision([rot_y(Box(-8, 0, -2, 8, 24, 2), k)])[0]
            perms.append({'condition': f"q.block_state('minecraft:cardinal_direction') == '{d}' && q.block_state('ecr:open') == {1 if open_ else 0}",
                          'components': {'minecraft:geometry': f'geometry.ecr_wood_gate_{"open" if open_ else "closed"}_{d}', 'minecraft:collision_box': coll,
                                         'minecraft:selection_box': boxes_to_collision([rot_y(Box(-8, 5, -2, 8, 16, 2), k)])[0]}})
    comps = {
        'minecraft:geometry': 'geometry.ecr_wood_gate_closed_north',
        'minecraft:material_instances': {'*': mi(p)},
        'minecraft:collision_box': {'origin': [-8, 0, -2], 'size': [16, 24, 4]},
        'minecraft:tags': ['minecraft:is_axe_item_destructible', 'wood', 'fence_gate'],
        'minecraft:connection_rule': {'accepts_connections_from': 'none'},
        f'{NS}:openable': {},
        **wood_common(spec, 2.0, 3.0),
    }
    desc = {'identifier': f'{NS}:{w}_fence_gate', 'menu_category': cat('construction', 'minecraft:itemGroup.name.fenceGate'),
            'states': {'ecr:open': [0, 1]}, 'traits': {'minecraft:placement_direction': {'enabled_states': ['minecraft:cardinal_direction']}}}
    wb(f'{w}_fence_gate', desc, comps, perms, sound=spec['sound'])
    lang_block(f'{w}_fence_gate', f'{spec["title"]} Fence Gate')


def build_trapdoor(w, spec):
    t = terrain(f'{w}_trapdoor')
    perms = []
    for half in ('bottom', 'top'):
        for open_ in (False, True):
            for k, d in enumerate(DIRS):
                if not open_ and k > 0:
                    continue
                if open_ and half == 'top':
                    continue
                boxes = trapdoor_boxes(half, open_, k)
                name = f'wood_trapdoor_{half}_{"open" if open_ else "closed"}' + (f'_{d}' if open_ else '')
                cond = (f"q.block_state('minecraft:cardinal_direction') == '{d}' && q.block_state('ecr:open') == 1" if open_
                        else f"q.block_state('minecraft:vertical_half') == '{half}' && q.block_state('ecr:open') == 0")
                perms.append({'condition': cond, 'components': {'minecraft:geometry': f'geometry.ecr_{name}', 'minecraft:collision_box': boxes_to_collision(boxes)[0],
                                                                'minecraft:selection_box': boxes_to_collision(boxes)[0]}})
    comps = {
        'minecraft:geometry': 'geometry.ecr_wood_trapdoor_bottom_closed',
        'minecraft:material_instances': {'*': mi(t, 'alpha_test_single_sided')},
        'minecraft:collision_box': {'origin': [-8, 0, -8], 'size': [16, 3, 16]},
        'minecraft:selection_box': {'origin': [-8, 0, -8], 'size': [16, 3, 16]},
        'minecraft:tags': ['minecraft:is_axe_item_destructible', 'wood', 'trapdoor'],
        'minecraft:light_dampening': 0,
        f'{NS}:openable': {},
        **wood_common(spec, 3.0, 3.0),
    }
    desc = {'identifier': f'{NS}:{w}_trapdoor', 'menu_category': cat('construction', 'minecraft:itemGroup.name.trapdoor'),
            'states': {'ecr:open': [0, 1]},
            'traits': {'minecraft:placement_direction': {'enabled_states': ['minecraft:cardinal_direction']},
                       'minecraft:placement_position': {'enabled_states': ['minecraft:vertical_half']}}}
    wb(f'{w}_trapdoor', desc, comps, perms, sound=spec['sound'])
    lang_block(f'{w}_trapdoor', f'{spec["title"]} Trapdoor')


def build_door(w, spec):
    lo, up = terrain(f'{w}_door_lower'), terrain(f'{w}_door_upper')
    perms = []
    for part in (0, 1):
        for open_ in (False, True):
            for hinge in (False, True):
                if not open_ and hinge:
                    continue
                for k, d in enumerate(DIRS):
                    boxes = door_boxes(open_, hinge, k)
                    name = f'wood_door_{"open" if open_ else "closed"}{"_r" if hinge else ""}_{d}'
                    cond = f"q.block_state('minecraft:multi_block_part') == {part} && q.block_state('minecraft:cardinal_direction') == '{d}' && q.block_state('ecr:open') == {1 if open_ else 0}"
                    if open_:
                        cond += f" && q.block_state('ecr:hinge_right') == {1 if hinge else 0}"
                    perms.append({'condition': cond, 'components': {
                        'minecraft:geometry': f'geometry.ecr_{name}', 'minecraft:collision_box': boxes_to_collision(boxes)[0],
                        'minecraft:selection_box': boxes_to_collision(boxes)[0],
                        'minecraft:material_instances': {'*': mi(lo if part == 0 else up, 'alpha_test_single_sided')}}})
    comps = {
        'minecraft:geometry': 'geometry.ecr_wood_door_closed_north',
        'minecraft:material_instances': {'*': mi(lo, 'alpha_test_single_sided')},
        'minecraft:collision_box': {'origin': [-8, 0, 5], 'size': [16, 16, 3]},
        'minecraft:tags': ['minecraft:is_axe_item_destructible', 'wood', 'door'],
        'minecraft:light_dampening': 0,
        'minecraft:loot': loot_simple(f'{w}_door', [(f'{NS}:{w}_door', 1, 1, 1.0)]),
        f'{NS}:openable': {},
        **wood_common(spec, 3.0, 3.0),
    }
    desc = {'identifier': f'{NS}:{w}_door', 'menu_category': cat('none'),
            'states': {'ecr:open': [0, 1], 'ecr:hinge_right': [0, 1]},
            'traits': {'minecraft:placement_direction': {'enabled_states': ['minecraft:cardinal_direction']},
                       'minecraft:multi_block': {'enabled_states': ['minecraft:multi_block_part'], 'parts': 2, 'direction': 'up'}}}
    wb(f'{w}_door', desc, comps, perms, sound=spec['sound'])
    lang_block(f'{w}_door', f'{spec["title"]} Door')


def build_plate_button(w, spec):
    T = spec['title']
    p = terrain(f'{w}_planks')
    comps = {
        'minecraft:geometry': 'geometry.ecr_wood_plate',
        'minecraft:material_instances': {'*': mi(p)},
        'minecraft:collision_box': False,
        'minecraft:selection_box': {'origin': [-7, 0, -7], 'size': [14, 1, 14]},
        'minecraft:tags': ['minecraft:is_axe_item_destructible', 'wood', 'pressure_plate'],
        'minecraft:light_dampening': 0,
        f'{NS}:plate': {},
        **wood_common(spec, 0.5, 0.5),
    }
    perms = [{'condition': "q.block_state('ecr:pressed') == 1", 'components': {
        'minecraft:geometry': 'geometry.ecr_wood_plate_pressed', 'minecraft:selection_box': {'origin': [-7, 0, -7], 'size': [14, 0.5, 14]},
        'minecraft:redstone_producer': {'power': 15, 'strongly_powered_face': 'down'}}}]
    desc = {'identifier': f'{NS}:{w}_pressure_plate', 'menu_category': cat('construction', 'minecraft:itemGroup.name.pressurePlate'), 'states': {'ecr:pressed': [0, 1]}}
    wb(f'{w}_pressure_plate', desc, comps, perms, sound=spec['sound'])
    lang_block(f'{w}_pressure_plate', f'{T} Pressure Plate')

    from blockgeo import rot_x as rx, rot_z as rz
    sel = {'up': lambda b: b, 'down': lambda b: rx(b, 2), 'north': lambda b: rx(b, 1), 'south': lambda b: rx(b, 3), 'east': lambda b: rz(b, 1), 'west': lambda b: rz(b, 3)}
    perms = []
    for face, fn in sel.items():
        for pressed in (False, True):
            b = fn(Box(-3, 0, -2, 3, 1 if pressed else 2, 2))
            comp = {'minecraft:geometry': f'geometry.ecr_wood_button_{face}_{"on" if pressed else "off"}', 'minecraft:selection_box': boxes_to_collision([b])[0]}
            if pressed:
                comp['minecraft:redstone_producer'] = {'power': 15}
            perms.append({'condition': f"q.block_state('minecraft:block_face') == '{face}' && q.block_state('ecr:pressed') == {1 if pressed else 0}", 'components': comp})
    comps = {
        'minecraft:geometry': 'geometry.ecr_wood_button_up_off',
        'minecraft:material_instances': {'*': mi(p)},
        'minecraft:collision_box': False,
        'minecraft:selection_box': {'origin': [-3, 0, -2], 'size': [6, 2, 4]},
        'minecraft:tags': ['minecraft:is_axe_item_destructible', 'wood', 'button'],
        'minecraft:light_dampening': 0,
        f'{NS}:button': {},
        **wood_common(spec, 0.5, 0.5),
    }
    desc = {'identifier': f'{NS}:{w}_button', 'menu_category': cat('construction', 'minecraft:itemGroup.name.buttons'),
            'states': {'ecr:pressed': [0, 1]}, 'traits': {'minecraft:placement_position': {'enabled_states': ['minecraft:block_face']}}}
    wb(f'{w}_button', desc, comps, perms, sound=spec['sound'])
    lang_block(f'{w}_button', f'{T} Button')


def build_all():
    write_shared_geometry()
    for w, spec in WOODS.items():
        build_logs(w, spec)
        build_planks(w, spec)
        build_leaves_sapling(w, spec)
        build_stairs_slabs(w, spec)
        build_fence(w, spec)
        build_gate(w, spec)
        build_trapdoor(w, spec)
        build_door(w, spec)
        build_plate_button(w, spec)
