"""v1.6 "Seals Update": Chapter III (the Frost Cantor, Ysolde) and Chapter IV (the Mire Lantern, Morwen).
Bosses, their minions, the Rimewalker / Hoarbone / Mirewalker / Lanternbone, the puzzle blocks, story items, materials, gear recipes, boss weapons,
particles, fogs and sprites.  Structures live in structures6.py, behaviour in tools/scripts/{cantor,morwen,puzzle,gear,mobs3}.js."""
import math
from PIL import Image
from common import *
from registry import *
import mob_frost, mob_mire, anims2, anims3
import gen_bosses, gen_hostiles
import seals_art as art
from gen_mobs import glow_overlay, projectile_client, projectile_bp, eff, target_players, spawn_rule, render_controllers
from gen_items import write_item, shaped, shapeless, repairable
from gen_blocks import write_block, mi, cat
from gen_blossom import client
from gen_animals import entry
from gen_hostiles import base as mob_base, entity as mob_entity, monster_rule

MOBS = {
    'rimewalker': dict(title='Rimewalker', egg=('#3e5262', '#6ad4ff'), xp=9),
    'hoarbone': dict(title='Hoarbone', egg=('#c4d2da', '#5ac8f0'), xp=11),
    'mirewalker': dict(title='Mirewalker', egg=('#34452a', '#ffe27a'), xp=9),
    'lanternbone': dict(title='Lanternbone', egg=('#9aa46c', '#ffd85a'), xp=11),
}
VERSES = ('dawn', 'zenith', 'dusk', 'midnight')
SCONCES = ('eye', 'star', 'moon')


# ----------------------------------------------------------------------------- creatures: behaviour entities
def bp_rimewalker():
    comps = mob_base(['rimewalker', 'undead'], 28, 0.23, (0.7, 1.95), MOBS['rimewalker']['xp'], 'rimewalker', {
        'minecraft:navigation.walk': {'is_amphibious': True, 'can_pass_doors': True, 'can_break_doors': True, 'avoid_water': False},
        'minecraft:attack': {'damage': 5, 'effect_name': 'slowness', 'effect_duration': 5},
        'minecraft:freezing_immune': {},
        'minecraft:knockback_resistance': {'value': 0.3},
        'minecraft:behavior.break_door': {'priority': 4},
        'minecraft:behavior.melee_attack': {'priority': 3, 'speed_multiplier': 1.1, 'track_target': True},
    })
    return mob_entity('rimewalker', comps)


def bp_hoarbone():
    comps = mob_base(['hoarbone', 'undead', 'skeleton'], 28, 0.27, (0.7, 2.0), MOBS['hoarbone']['xp'], 'hoarbone', {
        'minecraft:navigation.walk': {'is_amphibious': True, 'can_pass_doors': True, 'avoid_water': False},
        'minecraft:freezing_immune': {},
        'minecraft:knockback_resistance': {'value': 0.2},
        'minecraft:behavior.avoid_mob_type': {'priority': 4, 'entity_types': [
            {'filters': {'test': 'is_family', 'subject': 'other', 'operator': '==', 'value': 'wolf'}, 'max_dist': 6, 'walk_speed_multiplier': 1.0, 'sprint_speed_multiplier': 1.2}]},
    })
    groups = {
        'ecr:melee_mode': {'minecraft:attack': {'damage': 5, 'effect_name': 'slowness', 'effect_duration': 4},
                           'minecraft:behavior.melee_attack': {'priority': 3, 'speed_multiplier': 1.25, 'track_target': True}},
        'ecr:ranged_mode': {
            'minecraft:behavior.ranged_attack': {'priority': 3, 'attack_interval': {'min': 1.4, 'max': 2.4}, 'attack_range': {'min': 0.0, 'max': 24.0}, 'burst_shots': 1, 'speed_multiplier': 1.0, 'target_in_sight_time': 0.4, 'in_range_movement_mode': 'hold_position'},
            'minecraft:shooter': {'def': 'ecr:bone_shard', 'power': 1.7}},
        'ecr:mode_switcher': {'minecraft:target_nearby_sensor': {
            'inside_range': 4.0, 'outside_range': 6.5, 'must_see': True,
            'on_inside_range': {'event': 'ecr:switch_to_melee', 'target': 'self'}, 'on_outside_range': {'event': 'ecr:switch_to_ranged', 'target': 'self'}}},
    }
    events = {
        'minecraft:entity_spawned': {'add': {'component_groups': ['ecr:mode_switcher', 'ecr:ranged_mode']}},
        'ecr:switch_to_melee': {'add': {'component_groups': ['ecr:melee_mode']}, 'remove': {'component_groups': ['ecr:ranged_mode']}},
        'ecr:switch_to_ranged': {'add': {'component_groups': ['ecr:ranged_mode']}, 'remove': {'component_groups': ['ecr:melee_mode']}},
    }
    return mob_entity('hoarbone', comps, groups, events)


def bp_mirewalker():
    comps = mob_base(['mirewalker', 'undead'], 32, 0.21, (0.8, 2.0), MOBS['mirewalker']['xp'], 'mirewalker', {
        'minecraft:navigation.walk': {'is_amphibious': True, 'can_pass_doors': True, 'can_break_doors': True, 'avoid_water': False},
        'minecraft:attack': {'damage': 5, 'effect_name': 'poison', 'effect_duration': 6},
        'minecraft:knockback_resistance': {'value': 0.3},
        'minecraft:behavior.break_door': {'priority': 4},
        'minecraft:behavior.melee_attack': {'priority': 3, 'speed_multiplier': 1.05, 'track_target': True},
    })
    return mob_entity('mirewalker', comps)


def bp_lanternbone():
    comps = mob_base(['lanternbone', 'undead', 'skeleton'], 26, 0.26, (0.7, 2.0), MOBS['lanternbone']['xp'], 'lanternbone', {
        'minecraft:navigation.walk': {'is_amphibious': True, 'can_pass_doors': True, 'avoid_water': False},
        'minecraft:knockback_resistance': {'value': 0.2},
    })
    groups = {
        'ecr:melee_mode': {'minecraft:attack': {'damage': 5},
                           'minecraft:behavior.melee_attack': {'priority': 3, 'speed_multiplier': 1.25, 'track_target': True}},
        'ecr:ranged_mode': {
            'minecraft:behavior.ranged_attack': {'priority': 3, 'attack_interval': {'min': 2.2, 'max': 3.4}, 'attack_range': {'min': 0.0, 'max': 22.0}, 'burst_shots': 1, 'speed_multiplier': 1.0, 'target_in_sight_time': 0.4, 'in_range_movement_mode': 'hold_position'},
            'minecraft:shooter': {'def': 'ecr:wisp_bolt', 'power': 1.3}},
        'ecr:mode_switcher': {'minecraft:target_nearby_sensor': {
            'inside_range': 4.0, 'outside_range': 6.5, 'must_see': True,
            'on_inside_range': {'event': 'ecr:switch_to_melee', 'target': 'self'}, 'on_outside_range': {'event': 'ecr:switch_to_ranged', 'target': 'self'}}},
    }
    events = {
        'minecraft:entity_spawned': {'add': {'component_groups': ['ecr:mode_switcher', 'ecr:ranged_mode']}},
        'ecr:switch_to_melee': {'add': {'component_groups': ['ecr:melee_mode']}, 'remove': {'component_groups': ['ecr:ranged_mode']}},
        'ecr:switch_to_ranged': {'add': {'component_groups': ['ecr:ranged_mode']}, 'remove': {'component_groups': ['ecr:melee_mode']}},
    }
    return mob_entity('lanternbone', comps, groups, events)


def bp_wisp():
    comps = {
        'minecraft:type_family': {'family': ['mire_wisp', 'ecr_minion', 'ecr_mob', 'monster', 'mob']},
        'minecraft:health': {'value': 4, 'max': 4},
        'minecraft:collision_box': {'width': 0.5, 'height': 0.7},
        'minecraft:movement': {'value': 0.9}, 'minecraft:movement.basic': {}, 'minecraft:jump.static': {},
        'minecraft:navigation.walk': {'can_path_over_water': True, 'using_door_annotation': True},
        'minecraft:physics': {'has_collision': False, 'has_gravity': False},
        'minecraft:attack': {'damage': 3, 'effect_name': 'blindness', 'effect_duration': 3},
        'minecraft:fire_immune': {},
        'minecraft:follow_range': {'value': 32, 'max': 32},
        'minecraft:behavior.float': {'priority': 0},
        'minecraft:behavior.hurt_by_target': {'priority': 1},
        'minecraft:behavior.charge_attack': {'priority': 4},
        'minecraft:behavior.random_stroll': {'priority': 7, 'speed_multiplier': 0.5},
        'minecraft:behavior.look_at_player': {'priority': 9, 'look_distance': 6},
        'minecraft:behavior.nearest_attackable_target': {'priority': 2, 'must_see': False, 'reselect_targets': True,
                                                         'entity_types': [{'filters': {'test': 'is_family', 'subject': 'other', 'operator': '==', 'value': 'player'}, 'max_dist': 24}]},
        'minecraft:nameable': {}, 'minecraft:despawn': {'despawn_from_distance': {}},
        'minecraft:pushable_by_entity': {}, 'minecraft:pushable_by_block': {}, 'minecraft:conditional_bandwidth_optimization': {},
        'minecraft:is_hidden_when_invisible': {},
        'minecraft:loot': {'table': 'loot_tables/entities/mire_wisp.json'},
        'minecraft:experience_reward': {'on_death': 'query.last_hit_by_player ? 4 : 0'},
    }
    return {'format_version': '1.26.50', 'minecraft:entity': {
        'description': {'identifier': f'{NS}:mire_wisp', 'is_spawnable': True, 'is_summonable': True, 'spawn_category': 'monster'}, 'components': comps}}


def bp_decoy():
    """a mirage of Morwen: one hit and it bursts (the script punishes whoever struck it)"""
    comps = {
        'minecraft:type_family': {'family': ['mire_decoy', 'ecr_minion', 'ecr_mob', 'monster', 'mob']},
        'minecraft:health': {'value': 1, 'max': 1},
        'minecraft:collision_box': {'width': 0.9, 'height': 2.6},
        'minecraft:physics': {}, 'minecraft:fire_immune': {},
        'minecraft:behavior.look_at_player': {'priority': 7, 'look_distance': 20, 'probability': 0.2},
        'minecraft:nameable': {}, 'minecraft:pushable_by_entity': {}, 'minecraft:pushable_by_block': {},
        'minecraft:conditional_bandwidth_optimization': {}, 'minecraft:is_hidden_when_invisible': {},
        'minecraft:timer': {'time': [24, 28], 'looping': False, 'time_down_event': {'event': 'ecr:expire'}},
    }
    return {'format_version': '1.26.50', 'minecraft:entity': {
        'description': {'identifier': f'{NS}:mire_decoy', 'is_spawnable': True, 'is_summonable': True, 'spawn_category': 'monster'},
        'component_groups': {'ecr:despawn': {'minecraft:instant_despawn': {}}}, 'components': comps,
        'events': {'ecr:expire': {'add': {'component_groups': ['ecr:despawn']}}}}}


LOOT = {
    'rimewalker': [entry('minecraft:rotten_flesh', 0, 2), entry('ecr:rime_shard', 0, 2, chance=0.55), entry('ecr:glacial_shard', 1, 1, looting=1, chance=0.05),
                   entry('minecraft:iron_nugget', 1, 3, looting=0, chance=0.12)],
    'hoarbone': [entry('minecraft:bone', 0, 2), entry('minecraft:arrow', 0, 3), entry('ecr:rime_shard', 0, 1, chance=0.5), entry('ecr:glacial_shard', 1, 1, looting=1, chance=0.07)],
    'mirewalker': [entry('minecraft:rotten_flesh', 0, 2), entry('minecraft:moss_block', 0, 1, chance=0.3), entry('ecr:wisp_essence', 1, 1, looting=1, chance=0.12),
                   entry('minecraft:slime_ball', 0, 1, chance=0.2)],
    'lanternbone': [entry('minecraft:bone', 0, 2), entry('minecraft:arrow', 0, 3), entry('ecr:wisp_essence', 1, 1, looting=1, chance=0.35), entry('minecraft:glow_berries', 0, 2, chance=0.4)],
    'mire_wisp': [entry('ecr:wisp_essence', 1, 2, looting=1, chance=0.85), entry('minecraft:glowstone_dust', 0, 1, chance=0.4)],
}


def spawns():
    wjson(f'{BP}/spawn_rules/rimewalker.json', monster_rule('rimewalker', 26, (1, 3), ['frozen', 'ice_plains'], underground=False))
    wjson(f'{BP}/spawn_rules/hoarbone.json', monster_rule('hoarbone', 20, (1, 2), ['frozen', 'mountains']))
    wjson(f'{BP}/spawn_rules/mirewalker.json', monster_rule('mirewalker', 28, (1, 3), ['swamp', 'mangrove_swamp'], underground=False))
    wjson(f'{BP}/spawn_rules/lanternbone.json', monster_rule('lanternbone', 18, (1, 2), ['swamp', 'mangrove_swamp'], underground=False))
    wjson(f'{BP}/spawn_rules/mire_wisp.json', monster_rule('mire_wisp', 10, (1, 2), ['swamp', 'mangrove_swamp'], underground=False, bright=(0, 5)))


# ----------------------------------------------------------------------------- fogs, particles
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
    fog('cantor_whiteout', 0.10, 0.62, '#dcefff', 0.14, [0.8, 0.9, 1.0], [0.02, 0.01, 0.0])
    fog('cantor_blizzard', 0.03, 0.40, '#bcd8f0', 0.2, [0.7, 0.85, 1.0], [0.05, 0.03, 0.0])
    fog('cantor_requiem', 0.02, 0.34, '#3a5a8a', 0.24, [0.3, 0.5, 0.95], [0.2, 0.12, 0.02])
    fog('fen_mist', 0.12, 0.7, '#a8c078', 0.12, [0.6, 0.85, 0.4], [0.04, 0.0, 0.08])
    fog('fen_dark', 0.04, 0.44, '#243418', 0.2, [0.4, 0.7, 0.3], [0.1, 0.04, 0.12])
    fog('fen_hollow', 0.02, 0.32, '#0a1408', 0.26, [0.3, 0.6, 0.2], [0.2, 0.1, 0.2])


def particles():
    def pfx(ident, tex, n, life, size, speed, accel, grad, shape='point', radius=0.3, drag=0.0, material='particles_alpha', rot=False):
        comps = {
            'minecraft:emitter_rate_instant': {'num_particles': n},
            'minecraft:emitter_lifetime_once': {'active_time': 0.5},
            'minecraft:particle_lifetime_expression': {'max_lifetime': life},
            'minecraft:particle_initial_speed': speed,
            'minecraft:particle_motion_dynamic': {'linear_acceleration': accel, 'linear_drag_coefficient': drag},
            'minecraft:particle_appearance_billboard': {
                'size': [size, size], 'facing_camera_mode': 'lookat_xyz',
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
            'description': {'identifier': f'{NS}:{ident}', 'basic_render_parameters': {'material': material, 'texture': f'textures/particle/{tex}'}}, 'components': comps}})
    pfx('frost_note', 'ecr_note', 1, '1.6', '0.28', '0.3', [0, 0.5, 0], {'0.0': '#ffffffff', '0.7': '#c8ecffff', '1.0': '#00bfe6ff'})
    pfx('snow_swirl', 'ecr_snow', 10, '2.2', '0.18', 'Math.random(0.4, 1.2)', [0, -0.25, 0], {'0.0': '#ffffffff', '0.8': '#e0f2ffd0', '1.0': '#00e0f2ff'}, 'disc', 1.6, 0.8)
    pfx('wisp_glow', 'ecr_wisp', 3, '1.3', '0.32', '0.25', [0, 0.45, 0], {'0.0': '#ccf0c8ff', '0.5': '#9ae070cc', '1.0': '#009ae070'}, 'sphere', 0.25, 0.6)
    pfx('lantern_mote', 'ecr_mote', 4, '1.8', '0.14', '0.2', [0, 0.35, 0], {'0.0': '#fffbd0ff', '0.6': '#ffd85acc', '1.0': '#00ffd85a'}, 'sphere', 0.4, 0.5)
    pfx('intro_burst', 'ecr_ring', 36, '1.4', '0.6', 'Math.random(2.5, 5.5)', [0, 0.2, 0], {'0.0': '#ffffffff', '0.5': '#ffffffaa', '1.0': '#00ffffff'}, 'sphere', 0.4, 2.4)
    pfx('rime_burst', 'ecr_snow', 22, '1.0', '0.22', 'Math.random(1.5, 3.5)', [0, -1.2, 0], {'0.0': '#ffffffff', '1.0': '#00bfe6ff'}, 'sphere', 0.3, 0.9)
    pfx('wisp_burst', 'ecr_wisp', 22, '1.0', '0.36', 'Math.random(1.2, 3.2)', [0, 0.3, 0], {'0.0': '#f0ffc8ff', '1.0': '#009ae070'}, 'sphere', 0.3, 1.1)
    save_png(art.glow_dot((255, 255, 255)), f'{RP}/textures/particle/ecr_wisp.png')
    save_png(art.glow_dot((255, 244, 200), hard=0.5), f'{RP}/textures/particle/ecr_mote.png')
    save_png(art.note_sprite(), f'{RP}/textures/particle/ecr_note.png')
    save_png(art.snow_sprite(), f'{RP}/textures/particle/ecr_snow.png')
    save_png(art.ring_sprite(), f'{RP}/textures/particle/ecr_ring.png')


# ----------------------------------------------------------------------------- items
def items():
    def mk(name, title, im, extra=None, stack=64, rarity=None, glint=False):
        save_png(im, f'{RP}/textures/items/{name}.png')
        comps = {'minecraft:icon': {'textures': {'default': itemtex(name)}}, 'minecraft:max_stack_size': stack}
        if rarity:
            comps['minecraft:rarity'] = {'value': rarity}
        if glint:
            comps['minecraft:glint'] = True
        if extra:
            comps.update(extra)
        write_item(name, comps, 'items')
        lang_item(name, title)
    mk('glacial_shard', 'Glacial Shard', art.glacial_shard(), rarity='rare')
    mk('rime_shard', 'Rime Shard', art.rime_shard(), rarity='uncommon')
    mk('wisp_essence', 'Wisp Essence', art.wisp_essence(), rarity='rare', extra={'minecraft:fuel': {'duration': 30}})
    mk('tuning_fork', "Cantor's Tuning Fork", art.tuning_fork(), stack=1, rarity='rare', glint=True)
    mk('choir_seal', 'Seal of the Choir', art.seal('choir'), stack=1, rarity='epic', glint=True)
    mk('lantern_seal', 'Seal of the Lantern', art.seal('lantern'), stack=1, rarity='epic', glint=True)
    mk('keepers_lantern', "Keeper's Lantern", art.keepers_lantern(), stack=1, rarity='epic', glint=True)
    # boss weapons (sprites come from art_swords)
    for name, title, dmg, dur, repair, extra in (
            ('frostsong', 'Frostsong', 11, 3400, f'{NS}:glacial_shard', {}),
            ('mirelight_scythe', 'Mirelight Scythe', 12, 3600, f'{NS}:wisp_essence', {})):
        comps = {
            'minecraft:icon': {'textures': {'default': itemtex(name)}}, 'minecraft:max_stack_size': 1, 'minecraft:hand_equipped': True,
            'minecraft:durability': {'max_durability': dur}, 'minecraft:damage': {'value': dmg},
            'minecraft:enchantable': {'slot': 'sword', 'value': 22},
            'minecraft:repairable': repairable(name, repair),
            'minecraft:tags': {'tags': ['minecraft:is_sword', 'minecraft:is_tool', 'minecraft:diamond_tier', f'{NS}:{name}']},
            'minecraft:rarity': {'value': 'epic'}, 'minecraft:glint': True,
            'minecraft:digger': {'use_efficiency': True, 'destroy_speeds': [{'block': 'minecraft:web', 'speed': 15}]},
            'minecraft:can_destroy_in_creative': False,
        }
        write_item(name, comps, 'equipment', 'minecraft:itemGroup.name.sword')
        lang_item(name, title)
    LANG[f'item.{NS}:frostsong.lore'] = 'Right-click: Resonance'
    # ingredients -> alloys, lantern, tuning fork
    shapeless('rimesteel_ingot', ['minecraft:iron_ingot', f'{NS}:rime_shard', f'{NS}:rime_shard'], f'{NS}:rimesteel_ingot')
    shapeless('glacite_ingot', ['minecraft:diamond', f'{NS}:glacial_shard', f'{NS}:glacial_shard'], f'{NS}:glacite_ingot')
    shapeless('wispsteel_ingot', ['minecraft:gold_ingot', 'minecraft:netherite_scrap', f'{NS}:wisp_essence', f'{NS}:wisp_essence'], f'{NS}:wispsteel_ingot')
    shaped('tuning_fork', ['I I', 'IAI', ' / '], {'I': 'minecraft:iron_ingot', 'A': 'minecraft:amethyst_shard', '/': 'minecraft:stick'}, f'{NS}:tuning_fork')
    shapeless('keepers_lantern', ['minecraft:lantern'] + [f'{NS}:wisp_essence'] * 4, f'{NS}:keepers_lantern')


# ----------------------------------------------------------------------------- puzzle blocks
def blocks():
    # Verse Stones: four verses of the Cantor's song, one rune each
    textures = [terrain(f'verse_stone_{i}') for i in range(4)]
    for i in range(4):
        save_png(art.verse_stone(i), f'{RP}/textures/blocks/verse_stone_{i}.png')
    comps = {
        'minecraft:geometry': 'minecraft:geometry.full_block',
        'minecraft:material_instances': {'*': mi(textures[0])},
        'minecraft:tags': ['minecraft:is_pickaxe_item_destructible', 'stone'],
        'minecraft:destructible_by_mining': {'seconds_to_destroy': 8.0},
        'minecraft:destructible_by_explosion': {'explosion_resistance': 600.0},
        'minecraft:light_emission': 4, 'minecraft:map_color': '#7ea4c4',
        f'{NS}:verse_stone': {},
    }
    perms = [{'condition': f"q.block_state('ecr:verse') == {i}", 'components': {'minecraft:material_instances': {'*': mi(textures[i])}}} for i in (1, 2, 3)]
    write_block('verse_stone', {'identifier': f'{NS}:verse_stone', 'menu_category': cat('construction'), 'states': {'ecr:verse': [0, 1, 2, 3]}}, comps, perms, sound='stone')
    lang_block('verse_stone', 'Verse Stone')

    # Chimes of the sun's road
    gems = {'dawn': R_('#7a4a08', '#d9a830', '#ffd85a', '#fff4b0'), 'zenith': R_('#4a6a88', '#9ed4f4', '#d8f2ff', '#ffffff'),
            'dusk': R_('#5a1a48', '#a84a88', '#e0709a', '#ffb0c8'), 'midnight': R_('#0c1a4a', '#2a40a8', '#5a78e8', '#a8c0ff')}
    names = {'dawn': 'Chime of Dawn', 'zenith': 'Chime of Zenith', 'dusk': 'Chime of Dusk', 'midnight': 'Chime of Midnight'}
    for k, v in enumerate(VERSES):
        t = terrain(f'chime_{v}')
        save_png(art.bell_plate(gems[v], 110 + k), f'{RP}/textures/blocks/chime_{v}.png')
        comps = {
            'minecraft:geometry': 'minecraft:geometry.full_block', 'minecraft:material_instances': {'*': mi(t)},
            'minecraft:tags': ['minecraft:is_pickaxe_item_destructible', 'stone'],
            'minecraft:destructible_by_mining': {'seconds_to_destroy': 30.0}, 'minecraft:destructible_by_explosion': {'explosion_resistance': 1200.0},
            'minecraft:light_emission': 6, 'minecraft:map_color': '#e6c456', f'{NS}:chime': {},
        }
        write_block(f'chime_{v}', {'identifier': f'{NS}:chime_{v}', 'menu_category': cat('construction')}, comps, sound='stone')
        lang_block(f'chime_{v}', names[v])

    # Sconces of the drowned chapel (lit by the Keeper's Lantern)
    snames = {'eye': 'Sconce of the Eye', 'star': 'Sconce of the Star', 'moon': 'Sconce of the Moon'}
    for sym in SCONCES:
        off, on = terrain(f'sconce_{sym}'), terrain(f'sconce_{sym}_lit')
        save_png(art.sconce(sym, False), f'{RP}/textures/blocks/sconce_{sym}.png')
        save_png(art.sconce(sym, True), f'{RP}/textures/blocks/sconce_{sym}_lit.png')
        comps = {
            'minecraft:geometry': 'minecraft:geometry.full_block', 'minecraft:material_instances': {'*': mi(off)},
            'minecraft:tags': ['minecraft:is_pickaxe_item_destructible', 'stone'],
            'minecraft:destructible_by_mining': {'seconds_to_destroy': 30.0}, 'minecraft:destructible_by_explosion': {'explosion_resistance': 1200.0},
            'minecraft:map_color': '#476a48', f'{NS}:sconce': {},
        }
        perms = [{'condition': "q.block_state('ecr:lit') == 1", 'components': {'minecraft:material_instances': {'*': mi(on)}, 'minecraft:light_emission': 13}}]
        write_block(f'sconce_{sym}', {'identifier': f'{NS}:sconce_{sym}', 'menu_category': cat('construction'), 'states': {'ecr:lit': [0, 1]}}, comps, perms, sound='stone')
        lang_block(f'sconce_{sym}', snames[sym])

    # altars
    def mark_choir(d):
        for k in range(6):
            a = k / 6 * math.tau
            d.line([(7.5, 7.5), (7.5 + math.cos(a) * 5.5, 7.5 + math.sin(a) * 5.5)], fill=hx('#bff0ff') + (255,))
        d.ellipse([6, 6, 9, 9], fill=hx('#6ad4ff') + (255,))

    def mark_lantern(d):
        d.rectangle([5, 4, 10, 11], outline=hx('#c8b060') + (255,))
        d.rectangle([6, 5, 9, 10], fill=hx('#ffe27a') + (255,))
        d.rectangle([7, 2, 8, 3], fill=hx('#c8b060') + (255,))
    for name, title, ramp, mark, seed, comp in (
            ('choir_lectern', "Cantor's Lectern", art.FROST_STONE, mark_choir, 130, 'choir_lectern'),
            ('marsh_altar', 'Marsh Altar', art.MOSS_STONE, mark_lantern, 140, 'marsh_altar')):
        t_top, t_side = terrain(f'{name}_top'), terrain(f'{name}_side')
        save_png(art.altar_top(ramp, mark, seed), f'{RP}/textures/blocks/{name}_top.png')
        save_png(art.stone(ramp, seed + 1, 0.3, 0.4), f'{RP}/textures/blocks/{name}_side.png')
        comps = {
            'minecraft:geometry': 'minecraft:geometry.full_block',
            'minecraft:material_instances': {'*': mi(t_side), 'up': mi(t_top), 'down': mi(t_side), 'side': mi(t_side)},
            'minecraft:tags': ['minecraft:is_pickaxe_item_destructible', 'stone'],
            'minecraft:destructible_by_mining': {'seconds_to_destroy': 30.0}, 'minecraft:destructible_by_explosion': {'explosion_resistance': 1200.0},
            'minecraft:light_emission': 5, 'minecraft:map_color': '#7ea4c4' if 'choir' in name else '#476a48', f'{NS}:{comp}': {},
        }
        write_block(name, {'identifier': f'{NS}:{name}', 'menu_category': cat('construction')}, comps, sound='stone')
        lang_block(name, title)

    # lore tablets
    tex = [terrain(f'lore_tablet_{i}') for i in range(4)]
    for i in range(4):
        save_png(art.tablet(150 + i), f'{RP}/textures/blocks/lore_tablet_{i}.png')
    comps = {
        'minecraft:geometry': 'minecraft:geometry.full_block', 'minecraft:material_instances': {'*': mi(tex[0])},
        'minecraft:tags': ['minecraft:is_pickaxe_item_destructible', 'stone'],
        'minecraft:destructible_by_mining': {'seconds_to_destroy': 6.0}, 'minecraft:destructible_by_explosion': {'explosion_resistance': 300.0},
        'minecraft:light_emission': 2, 'minecraft:map_color': '#4e6070', f'{NS}:lore_tablet': {},
    }
    perms = [{'condition': f"math.mod(q.block_state('ecr:text'), 4) == {i}", 'components': {'minecraft:material_instances': {'*': mi(tex[i])}}} for i in (1, 2, 3)]
    write_block('lore_tablet', {'identifier': f'{NS}:lore_tablet', 'menu_category': cat('construction'), 'states': {'ecr:text': list(range(12))}}, comps, perms, sound='stone')
    lang_block('lore_tablet', 'Lore Tablet')


def R_(*c):
    return [hx(x) for x in c]


# ----------------------------------------------------------------------------- build
def build():
    # ---- bosses
    for name, mod, anim_fn, anims_, animate, glowkey in (
            ('frost_cantor', mob_frost, anims3.cantor, ['idle', 'walk', 'look', 'attack', 'cast'],
             ['idle', {'walk': 'q.modified_move_speed > 0.02'}, 'look', {'attack': "q.is_delayed_attacking && !q.property('ecr:casting')"}, {'cast': "q.property('ecr:casting')"}], None),
            ('mire_lantern', mob_mire, anims3.morwen, ['idle', 'walk', 'look', 'attack', 'cast'],
             ['idle', {'walk': 'q.modified_move_speed > 0.02'}, 'look', {'attack': "q.is_delayed_attacking && !q.property('ecr:casting')"}, {'cast': "q.property('ecr:casting')"}], None)):
        builder, mats, gid = mod.MODELS[name]
        m = builder(); m.pack()
        base_img, glow = m.paint(mats())
        save_tga(base_img, f'{RP}/textures/entity/{name}.tga'); save_tga(glow_overlay(glow), f'{RP}/textures/entity/{name}_glow.tga')
        base_img.save(f'{PREVIEW}/{name}_final_tex.png')
        wjson(f'{RP}/models/entity/{name}.geo.json', m.export())
        anims2.write(name, anim_fn(name))
        b = gen_bosses.BOSSES[name]
        wjson(f'{RP}/entity/{name}.entity.json', client(f'{NS}:{name}', name, gid, anims_, animate, egg=b['egg']))
        wjson(f'{BP}/entities/{name}.json', gen_bosses.bp(name, b))
        wjson(f'{BP}/loot_tables/entities/{name}.json', {'pools': gen_bosses.LOOT[name]})
        LANG[f'entity.{NS}:{name}.name'] = b['title']
        LANG[f'item.spawn_egg.entity.{NS}:{name}.name'] = f'{b["title"]} Spawn Egg'
    # ---- the dead of the Choir and the Fen
    specs = {
        'rimewalker': (mob_frost, anims2.biped('rimewalker', arm=-72, sway=[f'strip{i}' for i in range(5)], leg='leg', shamble=1.3, cast=False),
                       ['idle', 'walk', 'look', 'aggro', 'attack'], ['idle', {'walk': 'q.modified_move_speed > 0.02'}, 'look', {'aggro': 'q.has_target'}, {'attack': 'q.is_delayed_attacking'}]),
        'hoarbone': (mob_frost, anims2.biped('hoarbone', arm=-80, sway=[f'rag{i}' for i in range(5)], leg='leg', shin='shin', legamp=42, bow=True, cast=False),
                     ['idle', 'walk', 'look', 'aggro', 'attack'], ['idle', {'walk': 'q.modified_move_speed > 0.02'}, 'look', {'aggro': 'q.has_target'}, {'attack': 'q.is_delayed_attacking'}]),
        'mirewalker': (mob_mire, anims2.biped('mirewalker', arm=-68, sway=[f'strip{i}' for i in range(5)], leg='leg', shamble=1.6, cast=False),
                       ['idle', 'walk', 'look', 'aggro', 'attack'], ['idle', {'walk': 'q.modified_move_speed > 0.02'}, 'look', {'aggro': 'q.has_target'}, {'attack': 'q.is_delayed_attacking'}]),
        'lanternbone': (mob_mire, anims2.biped('lanternbone', arm=-10, sway=[f'rag{i}' for i in range(5)], leg='leg', shin='shin', legamp=40, cast=False),
                        ['idle', 'walk', 'look', 'aggro', 'attack'], ['idle', {'walk': 'q.modified_move_speed > 0.02'}, 'look', {'aggro': 'q.has_target'}, {'attack': 'q.is_delayed_attacking'}]),
    }
    for name, (mod, anim_set, anims_, animate) in specs.items():
        builder, mats, gid = mod.MODELS[name]
        m = builder(); m.pack()
        base_img, glow = m.paint(mats())
        save_tga(base_img, f'{RP}/textures/entity/{name}.tga'); save_tga(glow_overlay(glow), f'{RP}/textures/entity/{name}_glow.tga')
        wjson(f'{RP}/models/entity/{name}.geo.json', m.export())
        anims2.write(name, anim_set)
        from gen_mobs import client_entity
        wjson(f'{RP}/entity/{name}.entity.json', client_entity(f'{NS}:{name}', name, gid, anims_, animate, MOBS[name]['egg'], scale='1.0'))
        LANG[f'entity.{NS}:{name}.name'] = MOBS[name]['title']
        LANG[f'item.spawn_egg.entity.{NS}:{name}.name'] = f'{MOBS[name]["title"]} Spawn Egg'
        wjson(f'{BP}/loot_tables/entities/{name}.json', {'pools': LOOT[name]})
    wjson(f'{BP}/entities/rimewalker.json', bp_rimewalker())
    wjson(f'{BP}/entities/hoarbone.json', bp_hoarbone())
    wjson(f'{BP}/entities/mirewalker.json', bp_mirewalker())
    wjson(f'{BP}/entities/lanternbone.json', bp_lanternbone())
    # ---- wisp + decoy
    builder, mats, gid = mob_mire.MODELS['mire_wisp']
    m = builder(); m.pack()
    base_img, glow = m.paint(mats())
    save_tga(base_img, f'{RP}/textures/entity/mire_wisp.tga'); save_tga(glow_overlay(glow), f'{RP}/textures/entity/mire_wisp_glow.tga')
    wjson(f'{RP}/models/entity/mire_wisp.geo.json', m.export())
    anims2.write('mire_wisp', anims3.wisp())
    wjson(f'{RP}/entity/mire_wisp.entity.json', client(f'{NS}:mire_wisp', 'mire_wisp', gid, ['idle', 'charge'], ['idle', {'charge': 'q.has_target'}], egg=('#9ae070', '#ffe27a')))
    wjson(f'{BP}/entities/mire_wisp.json', bp_wisp())
    wjson(f'{BP}/loot_tables/entities/mire_wisp.json', {'pools': LOOT['mire_wisp']})
    LANG[f'entity.{NS}:mire_wisp.name'] = 'Mire Wisp'
    LANG[f'item.spawn_egg.entity.{NS}:mire_wisp.name'] = 'Mire Wisp Spawn Egg'
    # decoy: Morwen's model, translucent
    mb, mm, mgid = mob_mire.MODELS['mire_lantern']
    mm_ = mb(); mm_.pack()
    dimg, _ = mm_.paint(mm())
    ghost = dimg.copy(); gp = ghost.load()
    for y in range(ghost.height):
        for x in range(ghost.width):
            r, g, b, a = gp[x, y]
            if a:
                gp[x, y] = (int(r * 0.8 + 30), int(g * 0.9 + 40), int(b * 0.7 + 20), 130)
    save_png(ghost, f'{RP}/textures/entity/mire_decoy.png')
    anims2.write('mire_decoy', {k.replace('mire_lantern', 'mire_decoy'): v for k, v in anims3.morwen().items() if k.endswith(('idle', 'look'))})
    wjson(f'{RP}/entity/mire_decoy.entity.json', client(f'{NS}:mire_decoy', 'mire_decoy', mgid, ['idle', 'look'], ['idle', 'look'], egg=('#476a48', '#ffe27a'),
                                                         material='entity_alphablend', glow=False, textures={'default': 'textures/entity/mire_decoy'}))
    wjson(f'{BP}/entities/mire_decoy.json', bp_decoy())
    LANG[f'entity.{NS}:mire_decoy.name'] = 'Lantern Mirage'
    LANG[f'item.spawn_egg.entity.{NS}:mire_decoy.name'] = 'Lantern Mirage Spawn Egg'
    # ---- render controllers (default + glow) for everything above
    names = ['frost_cantor', 'mire_lantern', 'rimewalker', 'hoarbone', 'mirewalker', 'lanternbone', 'mire_wisp']
    rc = render_controllers(names)
    rc['render_controllers']['controller.render.ecr_mire_decoy'] = {'geometry': 'Geometry.default', 'materials': [{'*': 'Material.default'}], 'textures': ['Texture.default']}
    wjson(f'{RP}/render_controllers/ecr_seals.render_controllers.json', rc)
    # ---- projectiles
    save_png(art.note_sprite(), f'{RP}/textures/entity/frost_note.png')
    save_png(art.wisp_bolt_sprite(), f'{RP}/textures/entity/wisp_bolt.png')
    wjson(f'{RP}/entity/frost_note.entity.json', projectile_client(f'{NS}:frost_note', 'frost_note', '1.4'))
    wjson(f'{RP}/entity/wisp_bolt.entity.json', projectile_client(f'{NS}:wisp_bolt', 'wisp_bolt', '1.4'))
    wjson(f'{BP}/entities/frost_note.json', projectile_bp(f'{NS}:frost_note', 1.5, (3, 5), [eff('slowness', 1, 60, 80, 100)], 'snowballpoof', gravity=0.0))
    wjson(f'{BP}/entities/wisp_bolt.json', projectile_bp(f'{NS}:wisp_bolt', 1.3, (3, 4), [eff('poison', 0, 40, 60, 80)], 'witchspell', gravity=0.0))
    LANG[f'entity.{NS}:frost_note.name'] = 'Frozen Note'
    LANG[f'entity.{NS}:wisp_bolt.name'] = 'Wisp Bolt'
    spawns()
    fogs()
    particles()
    items()
    blocks()


if __name__ == '__main__':
    build()
    print('seals ok')
