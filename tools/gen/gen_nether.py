"""v1.7 "Burning Deep" update: Road V (Varenna, the Cinder Bride) and Road VI (Corvane, the Ashen Groom) - bosses, the Forged Blade, projectiles,
puzzle blocks (pedestals, Bridal Anvil, toll bells, Grave Altar, ember tablets), key items, seals, boss weapons, particles and fogs.
Structures live in structures7.py, behaviour in tools/scripts/{varenna,corvane,puzzle2}.js."""
import math
from PIL import Image
from common import *
from registry import *
import mob_nether, anims2, anims4
import nether_art as art
from gen_mobs import glow_overlay, projectile_client, projectile_bp, eff, target_players, render_controllers, orb_texture
from gen_items import write_item, repairable
from gen_blocks import write_block, mi, cat
from gen_blossom import client
from gen_animals import entry
from gen_hostiles import COMMON

BOSSES = {
    'cinder_bride': dict(title='The Cinder Bride', hp=900, box=(1.3, 3.6), speed=0.24, xp=2000, egg=('#2a1818', '#ff8a24'), melee=11, reach=3.4,
                         family=['cinder_bride'], ranged='ecr:cinder_bolt', power=1.6, interval=(3.0, 4.4)),
    'ashen_groom': dict(title='The Ashen Groom', hp=1100, box=(1.5, 3.9), speed=0.31, xp=2000, egg=('#1c2c3c', '#5ac8ff'), melee=14, reach=3.8,
                        family=['ashen_groom', 'undead'], ranged='ecr:soul_lance', power=1.9, interval=(2.6, 3.8)),
}
LOOT = {
    'cinder_bride': [entry('ecr:vowbreaker', 1, 1, looting=0), entry('ecr:forge_seal', 1, 1, looting=0), entry('ecr:cinder_heart', 1, 2, looting=0),
                     entry('minecraft:netherite_scrap', 3, 5, looting=0), entry('minecraft:ancient_debris', 2, 4, looting=0), entry('minecraft:diamond', 6, 10, looting=0),
                     entry('minecraft:enchanted_golden_apple', 1, 2, looting=0), entry('minecraft:experience_bottle', 16, 24, looting=0), entry('minecraft:gilded_blackstone', 8, 16, looting=0)],
    'ashen_groom': [entry('ecr:grievance', 1, 1, looting=0), entry('ecr:vow_seal', 1, 1, looting=0), entry('ecr:soul_ember', 1, 2, looting=0),
                    entry('minecraft:netherite_scrap', 3, 5, looting=0), entry('minecraft:ancient_debris', 2, 4, looting=0), entry('minecraft:diamond', 6, 10, looting=0),
                    entry('minecraft:totem_of_undying', 1, 1, looting=0), entry('minecraft:enchanted_golden_apple', 1, 2, looting=0), entry('minecraft:experience_bottle', 16, 24, looting=0)],
}


# ----------------------------------------------------------------------------- behaviour entities
def bp_boss(name, b):
    comps = dict(COMMON)
    comps.pop('minecraft:behavior.look_at_player')
    comps.pop('minecraft:behavior.random_look_around')
    comps.pop('minecraft:despawn')
    comps.update({
        'minecraft:type_family': {'family': b['family'] + ['ecr_mob', 'boss', 'monster', 'mob']},
        'minecraft:health': {'value': b['hp'], 'max': b['hp']},
        'minecraft:movement': {'value': b['speed']},
        'minecraft:collision_box': {'width': b['box'][0], 'height': b['box'][1]},
        'minecraft:follow_range': {'value': 56, 'max': 56},
        'minecraft:knockback_resistance': {'value': 1.0},
        'minecraft:fire_immune': {},
        'minecraft:boss': {'hud_range': 64, 'should_darken_sky': False, 'name': b['title']},
        'minecraft:damage_sensor': {'triggers': [{'cause': c, 'deals_damage': 'no'} for c in ('fall', 'drowning', 'suffocation', 'lava', 'fire', 'fire_tick')]},
        'minecraft:experience_reward': {'on_death': str(b['xp'])},
        'minecraft:loot': {'table': f'loot_tables/entities/{name}.json'},
        'minecraft:persistent': {},
        'minecraft:navigation.walk': {'can_pass_doors': True, 'avoid_water': False, 'is_amphibious': True, 'can_break_doors': False},
        'minecraft:behavior.hurt_by_target': {'priority': 1},
        'minecraft:behavior.random_stroll': {'priority': 7, 'speed_multiplier': 0.6},
        'minecraft:behavior.look_at_player': {'priority': 8, 'look_distance': 24, 'probability': 0.05},
        'minecraft:behavior.random_look_around': {'priority': 9},
    })
    comps.update(target_players(2, 56, must_see=False))
    melee = {'minecraft:attack': {'damage': b['melee']},
             'minecraft:behavior.melee_box_attack': {'priority': 3, 'speed_multiplier': 1.25, 'horizontal_reach': b['reach'], 'track_target': True, 'cooldown_time': 1.0}}
    groups = {
        'ecr:phase_2': {'minecraft:movement': {'value': round(b['speed'] * 1.12, 3)}},
        'ecr:phase_3': {'minecraft:movement': {'value': round(b['speed'] * 1.25, 3)}},
        'ecr:phase_4': {'minecraft:movement': {'value': round(b['speed'] * 1.4, 3)}},
        'ecr:melee_mode': melee,
        'ecr:ranged_mode': {
            'minecraft:behavior.ranged_attack': {'priority': 3, 'attack_interval': {'min': b['interval'][0], 'max': b['interval'][1]}, 'attack_range': {'min': 0.0, 'max': 28.0}, 'burst_shots': 3, 'burst_interval': 0.3,
                                                 'speed_multiplier': 1.0, 'target_in_sight_time': 0.4, 'in_range_movement_mode': 'follow_target'},
            'minecraft:shooter': {'def': b['ranged'], 'power': b['power']}},
        'ecr:mode_switcher': {'minecraft:target_nearby_sensor': {
            'inside_range': 4.5, 'outside_range': 7.5, 'must_see': False,
            'on_inside_range': {'event': 'ecr:switch_to_melee', 'target': 'self'}, 'on_outside_range': {'event': 'ecr:switch_to_ranged', 'target': 'self'}}},
    }
    events = {
        'minecraft:entity_spawned': {'set_property': {'ecr:phase': 0}, 'add': {'component_groups': ['ecr:mode_switcher', 'ecr:melee_mode']}},
        'ecr:enter_phase_2': {'add': {'component_groups': ['ecr:phase_2']}, 'set_property': {'ecr:phase': 1}},
        'ecr:enter_phase_3': {'add': {'component_groups': ['ecr:phase_3']}, 'remove': {'component_groups': ['ecr:phase_2']}, 'set_property': {'ecr:phase': 2}},
        'ecr:enter_phase_4': {'add': {'component_groups': ['ecr:phase_4']}, 'remove': {'component_groups': ['ecr:phase_3']}, 'set_property': {'ecr:phase': 3}},
        'ecr:cast_on': {'set_property': {'ecr:casting': True}}, 'ecr:cast_off': {'set_property': {'ecr:casting': False}},
        'ecr:switch_to_melee': {'add': {'component_groups': ['ecr:melee_mode']}, 'remove': {'component_groups': ['ecr:ranged_mode']}},
        'ecr:switch_to_ranged': {'add': {'component_groups': ['ecr:ranged_mode']}, 'remove': {'component_groups': ['ecr:melee_mode']}},
    }
    if name == 'ashen_groom':
        events.update({f'ecr:stance_{i}': {'set_property': {'ecr:stance': i}} for i in range(3)})
    props = {'ecr:phase': {'type': 'int', 'range': [0, 3], 'default': 0, 'client_sync': True},
             'ecr:casting': {'type': 'bool', 'default': False, 'client_sync': True}}
    if name == 'ashen_groom':
        props['ecr:stance'] = {'type': 'int', 'range': [0, 2], 'default': 0, 'client_sync': True}
    desc = {'identifier': f'{NS}:{name}', 'is_spawnable': True, 'is_summonable': True, 'spawn_category': 'monster', 'properties': props}
    return {'format_version': '1.26.50', 'minecraft:entity': {'description': desc, 'component_groups': groups, 'components': comps, 'events': events}}


def bp_blade():
    comps = {
        'minecraft:type_family': {'family': ['forged_blade', 'ecr_minion', 'ecr_mob', 'monster', 'mob']},
        'minecraft:health': {'value': 6, 'max': 6},
        'minecraft:collision_box': {'width': 0.5, 'height': 1.2},
        'minecraft:movement': {'value': 1.25}, 'minecraft:movement.basic': {}, 'minecraft:jump.static': {},
        'minecraft:navigation.walk': {'can_path_over_water': True, 'using_door_annotation': True},
        'minecraft:physics': {'has_collision': False, 'has_gravity': False},
        'minecraft:attack': {'damage': 7},
        'minecraft:fire_immune': {},
        'minecraft:follow_range': {'value': 40, 'max': 40},
        'minecraft:behavior.float': {'priority': 0},
        'minecraft:behavior.hurt_by_target': {'priority': 1},
        'minecraft:behavior.charge_attack': {'priority': 4},
        'minecraft:behavior.look_at_player': {'priority': 9, 'look_distance': 6},
        'minecraft:behavior.nearest_attackable_target': {'priority': 2, 'must_see': False, 'reselect_targets': True,
                                                         'entity_types': [{'filters': {'test': 'is_family', 'subject': 'other', 'operator': '==', 'value': 'player'}, 'max_dist': 40}]},
        'minecraft:nameable': {}, 'minecraft:despawn': {'despawn_from_distance': {}},
        'minecraft:pushable_by_entity': {}, 'minecraft:pushable_by_block': {}, 'minecraft:conditional_bandwidth_optimization': {},
        'minecraft:is_hidden_when_invisible': {},
        'minecraft:timer': {'time': [18, 22], 'looping': False, 'time_down_event': {'event': 'ecr:expire'}},
    }
    return {'format_version': '1.26.50', 'minecraft:entity': {
        'description': {'identifier': f'{NS}:forged_blade', 'is_spawnable': True, 'is_summonable': True, 'spawn_category': 'monster'},
        'component_groups': {'ecr:despawn': {'minecraft:instant_despawn': {}}}, 'components': comps,
        'events': {'ecr:expire': {'add': {'component_groups': ['ecr:despawn']}}}}}


# ----------------------------------------------------------------------------- fogs / particles
def fogs():
    def fog(name, start, end, colour, density, scatter, absorb):
        d = {'fog_start': start, 'fog_end': end, 'fog_color': colour, 'render_distance_type': 'render'}
        wjson(f'{RP}/fogs/{name}.json', {'format_version': '1.21.90', 'minecraft:fog_settings': {
            'description': {'identifier': f'{NS}:{name}'},
            'distance': {'air': d, 'weather': dict(d)},
            'volumetric': {
                'density': {'air': {'max_density': density, 'zero_density_height': 320.0, 'max_density_height': 320.0}},
                'media_coefficients': {'air': {'scattering': scatter, 'absorption': absorb}},
                'henyey_greenstein_g': {'air': {'henyey_greenstein_g': 0.4}}}}})
    fog('forge_haze', 0.10, 0.62, '#ff7a30', 0.12, [0.95, 0.45, 0.15], [0.02, 0.1, 0.2])
    fog('forge_inferno', 0.04, 0.46, '#e0400c', 0.2, [0.95, 0.3, 0.08], [0.04, 0.2, 0.3])
    fog('forge_cinders', 0.03, 0.34, '#5a0e08', 0.26, [0.8, 0.14, 0.06], [0.1, 0.3, 0.35])
    fog('forge_ashfall', 0.02, 0.26, '#241412', 0.3, [0.5, 0.2, 0.15], [0.2, 0.4, 0.4])
    fog('soul_mist', 0.10, 0.62, '#4ab0e8', 0.12, [0.2, 0.55, 0.95], [0.2, 0.08, 0.02])
    fog('soul_gale', 0.04, 0.44, '#2a78c8', 0.2, [0.1, 0.4, 0.95], [0.3, 0.12, 0.02])
    fog('soul_void', 0.03, 0.34, '#0e3a6a', 0.26, [0.08, 0.3, 0.9], [0.4, 0.2, 0.03])
    fog('soul_hollow', 0.02, 0.26, '#06182a', 0.3, [0.05, 0.2, 0.7], [0.5, 0.3, 0.05])


def particles():
    def pfx(ident, tex, n, life, size, speed, accel, grad, shape='point', radius=0.3, drag=0.0):
        comps = {
            'minecraft:emitter_rate_instant': {'num_particles': n}, 'minecraft:emitter_lifetime_once': {'active_time': 0.5},
            'minecraft:particle_lifetime_expression': {'max_lifetime': life}, 'minecraft:particle_initial_speed': speed,
            'minecraft:particle_motion_dynamic': {'linear_acceleration': accel, 'linear_drag_coefficient': drag},
            'minecraft:particle_appearance_billboard': {'size': [size, size], 'facing_camera_mode': 'lookat_xyz',
                                                        'uv': {'texture_width': 16, 'texture_height': 16, 'uv': [0, 0], 'uv_size': [16, 16]}},
            'minecraft:particle_appearance_tinting': {'color': {'interpolant': 'variable.particle_age / variable.particle_lifetime', 'gradient': grad}},
        }
        if shape == 'sphere':
            comps['minecraft:emitter_shape_sphere'] = {'radius': radius, 'direction': 'outwards'}
        elif shape == 'disc':
            comps['minecraft:emitter_shape_disc'] = {'radius': radius, 'plane_normal': [0, 1, 0], 'direction': 'outwards'}
        else:
            comps['minecraft:emitter_shape_point'] = {'direction': ['Math.random(-1,1)', 'Math.random(0.2,1)', 'Math.random(-1,1)']}
        wjson(f'{RP}/particles/{ident}.json', {'format_version': '1.10.0', 'particle_effect': {
            'description': {'identifier': f'{NS}:{ident}', 'basic_render_parameters': {'material': 'particles_alpha', 'texture': f'textures/particle/{tex}'}}, 'components': comps}})
    pfx('ember_spark', 'ecr_wisp', 6, '1.1', '0.14', 'Math.random(0.6, 1.8)', [0, 1.2, 0], {'0.0': '#ffe8a0ff', '0.5': '#ff8a24cc', '1.0': '#00c8400c'}, 'sphere', 0.3, 0.4)
    pfx('soul_flame', 'ecr_mote', 5, '1.4', '0.2', '0.3', [0, 0.9, 0], {'0.0': '#e8faffff', '0.5': '#5ac8ffcc', '1.0': '#001c78c8'}, 'sphere', 0.3, 0.3)
    pfx('ash_drift', 'ecr_snow', 10, '2.6', '0.12', 'Math.random(0.3, 0.9)', [0, -0.15, 0], {'0.0': '#8a7e7aff', '0.8': '#4a403ed0', '1.0': '#004a403e'}, 'disc', 1.8, 0.8)
    pfx('forge_burst', 'ecr_ring', 40, '1.2', '0.5', 'Math.random(3.0, 6.0)', [0, 0.3, 0], {'0.0': '#fff2b0ff', '0.5': '#ff8a24aa', '1.0': '#00c8400c'}, 'sphere', 0.4, 2.4)
    pfx('soul_burst', 'ecr_ring', 40, '1.2', '0.5', 'Math.random(3.0, 6.0)', [0, 0.3, 0], {'0.0': '#ffffffff', '0.5': '#5ac8ffaa', '1.0': '#001c78c8'}, 'sphere', 0.4, 2.4)
    pfx('blade_trail', 'ecr_wisp', 2, '0.6', '0.2', '0.1', [0, 0, 0], {'0.0': '#ffd35eff', '1.0': '#00c8400c'}, 'sphere', 0.1, 0.0)


# ----------------------------------------------------------------------------- items
def items():
    def mk(name, title, im, stack=1, rarity='epic', glint=True, extra=None):
        save_png(im, f'{RP}/textures/items/{name}.png')
        comps = {'minecraft:icon': {'textures': {'default': itemtex(name)}}, 'minecraft:max_stack_size': stack, 'minecraft:rarity': {'value': rarity}}
        if glint:
            comps['minecraft:glint'] = True
        if extra:
            comps.update(extra)
        write_item(name, comps, 'items')
        lang_item(name, title)
    mk('cinder_ring', 'Cinder Ring', art.cinder_ring(), rarity='rare')
    mk('ember_compass', 'Ember Compass', art.ember_compass(), rarity='rare')
    mk('grave_key', 'Grave Key', art.grave_key(), rarity='rare')
    mk('forge_seal', 'Seal of the Forge', art.seal('forge'))
    mk('vow_seal', 'Seal of the Vow', art.seal('vow'))
    food = lambda n, s: {'minecraft:food': {'nutrition': n, 'saturation_modifier': s, 'can_always_eat': True}, 'minecraft:use_animation': {'value': 'eat'},
                         'minecraft:use_modifiers': {'use_duration': 1.6, 'movement_modifier': 0.5}}
    mk('cinder_heart', 'Cinder Heart', art.cinder_heart_fixed(), stack=8, extra=food(4, 0.8))
    mk('soul_ember', 'Soul Ember', art.soul_ember(), stack=8, extra=food(4, 0.8))
    for name, title, dmg, dur, repair in (('vowbreaker', 'Vowbreaker', 15, 4200, f'{NS}:cinder_heart'), ('grievance', 'Grievance', 14, 4200, f'{NS}:soul_ember')):
        comps = {
            'minecraft:icon': {'textures': {'default': itemtex(name)}}, 'minecraft:max_stack_size': 1, 'minecraft:hand_equipped': True,
            'minecraft:durability': {'max_durability': dur}, 'minecraft:damage': {'value': dmg},
            'minecraft:enchantable': {'slot': 'sword', 'value': 24},
            'minecraft:repairable': repairable(name, repair),
            'minecraft:tags': {'tags': ['minecraft:is_sword', 'minecraft:is_tool', 'minecraft:netherite_tier', f'{NS}:{name}']},
            'minecraft:rarity': {'value': 'epic'}, 'minecraft:glint': True, 'minecraft:fire_resistant': {'value': True},
            'minecraft:digger': {'use_efficiency': True, 'destroy_speeds': [{'block': 'minecraft:web', 'speed': 15}]},
            'minecraft:can_destroy_in_creative': False,
        }
        write_item(name, comps, 'equipment', 'minecraft:itemGroup.name.sword')
        lang_item(name, title)


# ----------------------------------------------------------------------------- puzzle blocks
def blocks():
    base = {'minecraft:geometry': 'minecraft:geometry.full_block', 'minecraft:tags': ['minecraft:is_pickaxe_item_destructible', 'stone'],
            'minecraft:destructible_by_mining': {'seconds_to_destroy': 40.0}, 'minecraft:destructible_by_explosion': {'explosion_resistance': 1200.0}}
    # three offering pedestals: gold, flame, tears
    for kind, title in (('gold', 'Pedestal of Gold'), ('flame', 'Pedestal of Flame'), ('tears', 'Pedestal of Tears')):
        top, side, sidel = terrain(f'pedestal_{kind}_top'), terrain('pedestal_side'), terrain('pedestal_side_lit')
        save_png(art.pedestal_top(kind), f'{RP}/textures/blocks/pedestal_{kind}_top.png')
        save_png(art.pedestal_side(False), f'{RP}/textures/blocks/pedestal_side.png')
        save_png(art.pedestal_side(True), f'{RP}/textures/blocks/pedestal_side_lit.png')
        comps = dict(base)
        comps.update({'minecraft:material_instances': {'*': mi(side), 'up': mi(top), 'side': mi(side)}, 'minecraft:map_color': '#2c262e', f'{NS}:pedestal': {}})
        perms = [{'condition': "q.block_state('ecr:offered') == 1", 'components': {'minecraft:material_instances': {'*': mi(sidel), 'up': mi(top), 'side': mi(sidel)}, 'minecraft:light_emission': 10}}]
        write_block(f'pedestal_{kind}', {'identifier': f'{NS}:pedestal_{kind}', 'menu_category': cat('construction'), 'states': {'ecr:offered': [0, 1]}}, comps, perms, sound='stone')
        lang_block(f'pedestal_{kind}', title)
    # the Bridal Anvil
    t_top, t_side = terrain('bridal_anvil_top'), terrain('bridal_anvil_side')
    save_png(art.anvil_top(), f'{RP}/textures/blocks/bridal_anvil_top.png')
    save_png(art.anvil_side(), f'{RP}/textures/blocks/bridal_anvil_side.png')
    comps = dict(base)
    comps.update({'minecraft:material_instances': {'*': mi(t_side), 'up': mi(t_top), 'side': mi(t_side)}, 'minecraft:light_emission': 8, 'minecraft:map_color': '#303038', f'{NS}:bridal_anvil': {}})
    write_block('bridal_anvil', {'identifier': f'{NS}:bridal_anvil', 'menu_category': cat('construction')}, comps, sound='anvil')
    lang_block('bridal_anvil', 'Bridal Anvil')
    # the toll tower: a core and four bells
    t = terrain('toll_core')
    save_png(art.toll_core(), f'{RP}/textures/blocks/toll_core.png')
    comps = dict(base)
    comps.update({'minecraft:material_instances': {'*': mi(t)}, 'minecraft:light_emission': 9, 'minecraft:map_color': '#1c78c8', f'{NS}:toll_core': {}})
    write_block('toll_core', {'identifier': f'{NS}:toll_core', 'menu_category': cat('construction')}, comps, sound='stone')
    lang_block('toll_core', 'Toll Core')
    for n, title in enumerate(('Ember Bell', 'Soul Bell', 'Bone Bell', 'Violet Bell')):
        tb = terrain(f'toll_bell_{n}')
        save_png(art.toll_bell(n), f'{RP}/textures/blocks/toll_bell_{n}.png')
        comps = dict(base)
        comps.update({'minecraft:material_instances': {'*': mi(tb)}, 'minecraft:light_emission': 6, 'minecraft:map_color': '#a69e8a', f'{NS}:toll_bell': {}})
        write_block(f'toll_bell_{n}', {'identifier': f'{NS}:toll_bell_{n}', 'menu_category': cat('construction')}, comps, sound='bell')
        lang_block(f'toll_bell_{n}', title)
    # the Grave Altar
    gt, gs = terrain('grave_altar_top'), terrain('grave_altar_side')
    save_png(art.grave_altar_top(), f'{RP}/textures/blocks/grave_altar_top.png')
    save_png(art.stone(art.BLACKSTONE, 251, 0.3, 0.35), f'{RP}/textures/blocks/grave_altar_side.png')
    comps = dict(base)
    comps.update({'minecraft:material_instances': {'*': mi(gs), 'up': mi(gt), 'side': mi(gs)}, 'minecraft:light_emission': 7, 'minecraft:map_color': '#1c78c8', f'{NS}:grave_altar': {}})
    write_block('grave_altar', {'identifier': f'{NS}:grave_altar', 'menu_category': cat('construction')}, comps, sound='stone')
    lang_block('grave_altar', 'Grave Altar')
    # ember tablets (12 texts, 4 textures)
    tex = [terrain(f'ember_tablet_{i}') for i in range(4)]
    for i in range(4):
        save_png(art.ember_tablet(i), f'{RP}/textures/blocks/ember_tablet_{i}.png')
    comps = dict(base)
    comps.update({'minecraft:material_instances': {'*': mi(tex[0])}, 'minecraft:destructible_by_mining': {'seconds_to_destroy': 8.0}, 'minecraft:light_emission': 3, 'minecraft:map_color': '#2c262e', f'{NS}:ember_tablet': {}})
    perms = [{'condition': f"math.mod(q.block_state('ecr:text'), 4) == {i}", 'components': {'minecraft:material_instances': {'*': mi(tex[i])}}} for i in (1, 2, 3)]
    write_block('ember_tablet', {'identifier': f'{NS}:ember_tablet', 'menu_category': cat('construction'), 'states': {'ecr:text': list(range(12))}}, comps, perms, sound='stone')
    lang_block('ember_tablet', 'Ember Tablet')


# ----------------------------------------------------------------------------- build
def recolor_glow(glow_tga, mode):
    """the Groom's glow overlay is soul-blue; stance 0 = ember (orange), 1 = soul (blue, as painted), 2 = hollow (white-grey)"""
    im = glow_tga.convert('RGBA')
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if not a:
                continue
            if mode == 0:
                px[x, y] = (min(255, int(b * 1.0)), min(255, int(g * 0.62)), int(r * 0.3), a)
            elif mode == 2:
                l = int((r + g + b) / 3 * 0.9 + 40)
                px[x, y] = (min(255, l), min(255, l), min(255, l), a)
    return im


def render_controllers_nether():
    skin = "Array.glow[q.property('ecr:stance')]"
    rc = {
        'controller.render.ecr_cinder_bride': {'geometry': 'Geometry.default', 'materials': [{'*': 'Material.default'}], 'textures': ['Texture.default']},
        'controller.render.ecr_cinder_bride_glow': {'geometry': 'Geometry.default', 'materials': [{'*': 'Material.glow'}], 'textures': ['Texture.glow']},
        'controller.render.ecr_ashen_groom': {'geometry': 'Geometry.default', 'materials': [{'*': 'Material.default'}], 'textures': ['Texture.default']},
        'controller.render.ecr_ashen_groom_glow': {'arrays': {'textures': {'Array.glow': ['Texture.glow_ember', 'Texture.glow', 'Texture.glow_hollow']}},
                                                   'geometry': 'Geometry.default', 'materials': [{'*': 'Material.glow'}], 'textures': [skin]},
        'controller.render.ecr_forged_blade': {'geometry': 'Geometry.default', 'materials': [{'*': 'Material.default'}], 'textures': ['Texture.default']},
        'controller.render.ecr_forged_blade_glow': {'geometry': 'Geometry.default', 'materials': [{'*': 'Material.glow'}], 'textures': ['Texture.glow']},
    }
    return {'format_version': '1.8.0', 'render_controllers': rc}


def build():
    notcast = "!q.property('ecr:casting')"
    anim_sets = {'cinder_bride': anims4.bride, 'ashen_groom': anims4.groom}
    for name, b in BOSSES.items():
        builder, mats, gid = mob_nether.MODELS[name]
        m = builder(); m.pack()
        base_img, glow = m.paint(mats())
        glow_img = glow_overlay(glow)
        save_tga(base_img, f'{RP}/textures/entity/{name}.tga')
        save_tga(glow_img, f'{RP}/textures/entity/{name}_glow.tga')
        base_img.save(f'{PREVIEW}/{name}_final_tex.png')
        wjson(f'{RP}/models/entity/{name}.geo.json', m.export())
        anims2.write(name, anim_sets[name](name))
        animate = ['idle', {'walk': 'q.modified_move_speed > 0.02'}, 'look', {'attack': f'q.is_delayed_attacking && {notcast}'}, {'cast': "q.property('ecr:casting')"}]
        textures = None
        rc = None
        if name == 'ashen_groom':
            for mode, suffix in ((0, 'glow_ember'), (2, 'glow_hollow')):
                save_tga(recolor_glow(glow_img, mode), f'{RP}/textures/entity/{name}_{suffix}.tga')
            textures = {'default': f'textures/entity/{name}', 'glow': f'textures/entity/{name}_glow', 'glow_ember': f'textures/entity/{name}_glow_ember', 'glow_hollow': f'textures/entity/{name}_glow_hollow'}
        wjson(f'{RP}/entity/{name}.entity.json', client(f'{NS}:{name}', name, gid, ['idle', 'walk', 'look', 'attack', 'cast'], animate, egg=b['egg'], textures=textures))
        wjson(f'{BP}/entities/{name}.json', bp_boss(name, b))
        wjson(f'{BP}/loot_tables/entities/{name}.json', {'pools': LOOT[name]})
        LANG[f'entity.{NS}:{name}.name'] = b['title']
        LANG[f'item.spawn_egg.entity.{NS}:{name}.name'] = f'{b["title"]} Spawn Egg'
    # the Forged Blade
    builder, mats, gid = mob_nether.MODELS['forged_blade']
    m = builder(); m.pack()
    base_img, glow = m.paint(mats())
    save_tga(base_img, f'{RP}/textures/entity/forged_blade.tga'); save_tga(glow_overlay(glow), f'{RP}/textures/entity/forged_blade_glow.tga')
    wjson(f'{RP}/models/entity/forged_blade.geo.json', m.export())
    anims2.write('forged_blade', anims4.forged_blade())
    wjson(f'{RP}/entity/forged_blade.entity.json', client(f'{NS}:forged_blade', 'forged_blade', gid, ['idle', 'charge'], ['idle', {'charge': 'q.has_target'}], egg=('#52525e', '#ff8a24')))
    wjson(f'{BP}/entities/forged_blade.json', bp_blade())
    LANG[f'entity.{NS}:forged_blade.name'] = 'Forged Blade'
    LANG[f'item.spawn_egg.entity.{NS}:forged_blade.name'] = 'Forged Blade Spawn Egg'
    wjson(f'{RP}/render_controllers/ecr_nether.render_controllers.json', render_controllers_nether())
    # projectiles
    save_png(art.cinder_bolt(), f'{RP}/textures/entity/cinder_bolt.png')
    save_png(art.soul_lance(), f'{RP}/textures/entity/soul_lance.png')
    wjson(f'{RP}/entity/cinder_bolt.entity.json', projectile_client(f'{NS}:cinder_bolt', 'cinder_bolt', '1.6'))
    wjson(f'{RP}/entity/soul_lance.entity.json', projectile_client(f'{NS}:soul_lance', 'soul_lance', '1.6'))
    wjson(f'{BP}/entities/cinder_bolt.json', projectile_bp(f'{NS}:cinder_bolt', 1.6, (6, 9), [], 'lava', gravity=0.0, fire=True))
    wjson(f'{BP}/entities/soul_lance.json', projectile_bp(f'{NS}:soul_lance', 1.9, (6, 9), [eff('wither', 0, 60, 80, 100)], 'witchspell', gravity=0.0))
    LANG[f'entity.{NS}:cinder_bolt.name'] = 'Cinder Bolt'
    LANG[f'entity.{NS}:soul_lance.name'] = 'Soul Lance'
    fogs()
    particles()
    items()
    blocks()


if __name__ == '__main__':
    build()
    print('nether ok')
