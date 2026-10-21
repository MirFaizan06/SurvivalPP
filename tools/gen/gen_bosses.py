"""v1.2 overworld bosses: Hollow King, Mosswood Colossus, Silkqueen (models, entities, loot, animations)."""
from common import *
from registry import LANG
import mob_bosses2, anims2
from gen_mobs import glow_overlay, render_controllers, target_players
from gen_animals import entry
from gen_hostiles import COMMON

BOSSES = {
    'hollow_king': dict(title='Hollow King', hp=450, box=(1.4, 3.6), speed=0.25, xp=900, egg=('#1a3a2c', '#f4d460'),
                        family=['hollow_king', 'undead'], melee=16, reach=2.6),
    'mosswood_colossus': dict(title='Mosswood Colossus', hp=650, box=(2.6, 5.4), speed=0.2, xp=900, egg=('#47301a', '#7ae070'),
                              family=['mosswood_colossus'], melee=26, reach=3.6),
    'silkqueen': dict(title='Silkqueen', hp=400, box=(3.4, 2.0), speed=0.31, xp=900, egg=('#1c1638', '#f2c744'),
                      family=['silkqueen', 'arthropod'], melee=10, reach=2.4),
}

LOOT = {
    'hollow_king': [entry('minecraft:totem_of_undying', 1, 1, looting=0), entry('ecr:hollow_crown', 1, 1, looting=0), entry('ecr:grave_dust', 8, 14, looting=0),
                    entry('ecr:hollow_bone', 6, 10, looting=0), entry('minecraft:diamond', 3, 6, looting=0), entry('minecraft:emerald', 8, 16, looting=0),
                    entry('minecraft:enchanted_golden_apple', 1, 1, looting=0, chance=0.35)],
    'mosswood_colossus': [entry('ecr:colossus_core', 1, 1, looting=0), entry('ecr:spore_cluster', 8, 14, looting=0), entry('minecraft:moss_block', 16, 24, looting=0),
                          entry('minecraft:diamond', 4, 8, looting=0), entry('minecraft:enchanted_golden_apple', 1, 1, looting=0),
                          entry('minecraft:netherite_scrap', 1, 2, looting=0, chance=0.5)],
    'silkqueen': [entry('ecr:queens_fang', 1, 1, looting=0), entry('ecr:silk_gland', 6, 10, looting=0), entry('minecraft:string', 16, 32, looting=0),
                  entry('minecraft:spider_eye', 6, 10, looting=0), entry('minecraft:diamond', 3, 6, looting=0), entry('minecraft:ender_pearl', 4, 8, looting=0),
                  entry('minecraft:enchanted_golden_apple', 1, 1, looting=0, chance=0.5)],
}


def bp(name, b):
    comps = dict(COMMON)
    comps.pop('minecraft:behavior.look_at_player')
    comps.pop('minecraft:behavior.random_look_around')
    comps.update({
        'minecraft:type_family': {'family': b['family'] + ['ecr_mob', 'boss', 'monster', 'mob']},
        'minecraft:health': {'value': b['hp'], 'max': b['hp']},
        'minecraft:movement': {'value': b['speed']},
        'minecraft:collision_box': {'width': b['box'][0], 'height': b['box'][1]},
        'minecraft:follow_range': {'value': 56, 'max': 56},
        'minecraft:knockback_resistance': {'value': 1.0},
        'minecraft:boss': {'hud_range': 64, 'should_darken_sky': False, 'name': b['title']},
        'minecraft:damage_sensor': {'triggers': [{'cause': c, 'deals_damage': 'no'} for c in ('fall', 'drowning', 'suffocation')]},
        'minecraft:experience_reward': {'on_death': str(b['xp'])},
        'minecraft:loot': {'table': f'loot_tables/entities/{name}.json'},
        'minecraft:persistent': {},
        'minecraft:behavior.hurt_by_target': {'priority': 1},
        'minecraft:behavior.random_stroll': {'priority': 7, 'speed_multiplier': 0.6},
        'minecraft:behavior.look_at_player': {'priority': 8, 'look_distance': 24, 'probability': 0.05},
        'minecraft:behavior.random_look_around': {'priority': 9},
    })
    comps.pop('minecraft:despawn')
    comps.update(target_players(2, 56, must_see=False))
    groups = {'ecr:phase_2': {'minecraft:movement': {'value': round(b['speed'] * 1.18, 3)}},
              'ecr:phase_3': {'minecraft:movement': {'value': round(b['speed'] * 1.38, 3)}}}
    events = {
        'minecraft:entity_spawned': {'set_property': {'ecr:phase': 0}},
        'ecr:enter_phase_2': {'add': {'component_groups': ['ecr:phase_2']}, 'set_property': {'ecr:phase': 1}},
        'ecr:enter_phase_3': {'add': {'component_groups': ['ecr:phase_3']}, 'remove': {'component_groups': ['ecr:phase_2']}, 'set_property': {'ecr:phase': 2}},
        'ecr:cast_on': {'set_property': {'ecr:casting': True}},
        'ecr:cast_off': {'set_property': {'ecr:casting': False}},
    }
    melee = {'minecraft:attack': {'damage': b['melee']},
             'minecraft:behavior.melee_box_attack': {'priority': 3, 'speed_multiplier': 1.2, 'horizontal_reach': b['reach'], 'track_target': True, 'cooldown_time': 1.2}}
    if name == 'hollow_king':
        comps['minecraft:navigation.walk'] = {'is_amphibious': True, 'can_pass_doors': True, 'can_break_doors': True, 'avoid_water': False}
        groups['ecr:melee_mode'] = melee
        groups['ecr:ranged_mode'] = {
            'minecraft:behavior.ranged_attack': {'priority': 3, 'attack_interval': {'min': 2.2, 'max': 3.6}, 'attack_range': {'min': 0.0, 'max': 28.0}, 'burst_shots': 3, 'burst_interval': 0.3, 'speed_multiplier': 1.0, 'target_in_sight_time': 0.4, 'in_range_movement_mode': 'follow_target'},
            'minecraft:shooter': {'def': 'ecr:bone_shard', 'power': 1.9}}
    elif name == 'mosswood_colossus':
        comps['minecraft:navigation.walk'] = {'can_pass_doors': False, 'can_break_doors': True, 'avoid_water': False, 'is_amphibious': True}
        groups['ecr:melee_mode'] = melee
        groups['ecr:ranged_mode'] = {}
    else:
        comps['minecraft:navigation.climb'] = {'can_path_over_water': True}
        comps['minecraft:can_climb'] = {}
        comps['minecraft:block_movement_slowdown_immunity'] = {}
        groups['ecr:melee_mode'] = {
            'minecraft:attack': {'damage': b['melee'], 'effect_name': 'poison', 'effect_duration': 10},
            'minecraft:behavior.leap_at_target': {'priority': 3, 'yd': 0.4, 'must_be_on_ground': True},
            'minecraft:behavior.melee_attack': {'priority': 4, 'speed_multiplier': 1.25, 'track_target': True, 'reach_multiplier': 1.6}}
        groups['ecr:ranged_mode'] = {
            'minecraft:behavior.ranged_attack': {'priority': 3, 'attack_interval': {'min': 2.6, 'max': 4.2}, 'attack_range': {'min': 0.0, 'max': 24.0}, 'burst_shots': 2, 'burst_interval': 0.5, 'speed_multiplier': 1.0, 'target_in_sight_time': 0.4, 'in_range_movement_mode': 'follow_target'},
            'minecraft:shooter': {'def': 'ecr:web_bolt', 'power': 1.5}}
    inside, outside = (4.0, 7.0) if name != 'mosswood_colossus' else (4.5, 6.0)
    groups['ecr:mode_switcher'] = {'minecraft:target_nearby_sensor': {
        'inside_range': inside, 'outside_range': outside, 'must_see': False,
        'on_inside_range': {'event': 'ecr:switch_to_melee', 'target': 'self'},
        'on_outside_range': {'event': 'ecr:switch_to_ranged', 'target': 'self'}}}
    events['minecraft:entity_spawned']['add'] = {'component_groups': ['ecr:mode_switcher', 'ecr:melee_mode']}
    events['ecr:switch_to_melee'] = {'add': {'component_groups': ['ecr:melee_mode']}, 'remove': {'component_groups': ['ecr:ranged_mode']}}
    events['ecr:switch_to_ranged'] = {'add': {'component_groups': ['ecr:ranged_mode']}, 'remove': {'component_groups': ['ecr:melee_mode']}}
    if name == 'mosswood_colossus':
        # the Colossus never goes ranged: it keeps closing in (its ranged mode is an empty group)
        events['ecr:switch_to_ranged'] = {'add': {'component_groups': ['ecr:melee_mode']}}
    desc = {'identifier': f'{NS}:{name}', 'is_spawnable': True, 'is_summonable': True, 'spawn_category': 'monster',
            'properties': {'ecr:phase': {'type': 'int', 'range': [0, 2], 'default': 0, 'client_sync': True},
                           'ecr:casting': {'type': 'bool', 'default': False, 'client_sync': True}}}
    return {'format_version': '1.26.50', 'minecraft:entity': {'description': desc, 'component_groups': groups, 'components': comps, 'events': events}}


def client(name, b, anim_map, animate):
    return {'format_version': '1.10.0', 'minecraft:client_entity': {'description': {
        'identifier': f'{NS}:{name}',
        'materials': {'default': 'entity_alphatest', 'glow': 'entity_emissive_alpha'},
        'textures': {'default': f'textures/entity/{name}', 'glow': f'textures/entity/{name}_glow'},
        'geometry': {'default': f'geometry.ecr_{name}'},
        'animations': {k: f'animation.ecr_{name}.{v}' for k, v in anim_map.items()},
        'scripts': {'animate': animate},
        'render_controllers': [f'controller.render.ecr_{name}', f'controller.render.ecr_{name}_glow'],
        'spawn_egg': {'base_color': b['egg'][0], 'overlay_color': b['egg'][1]}}}}


def build():
    biped_walk = "q.modified_move_speed > 0.02"
    notcast = "!q.property('ecr:casting')"
    specs = {
        'hollow_king': (anims2.biped('hollow_king', arm=-10, sway=[f'rag{i}' for i in range(6)], leg='leg', shin='shin', legamp=30, shamble=0.5, bob=0.6),
                        {'idle': 'idle', 'walk': 'walk', 'look': 'look', 'aggro': 'aggro', 'attack': 'attack', 'cast': 'cast'},
                        ['idle', {'walk': biped_walk}, 'look', {'aggro': f'q.has_target && {notcast}'}, {'attack': f'q.is_delayed_attacking && {notcast}'}, {'cast': "q.property('ecr:casting')"}]),
        'mosswood_colossus': (anims2.biped('mosswood_colossus', arm=-6, sway=[f'vine{i}' for i in range(8)], leg='leg', shin='shin', legamp=24, shamble=0.4, bob=1.4),
                              {'idle': 'idle', 'walk': 'walk', 'look': 'look', 'aggro': 'aggro', 'attack': 'attack', 'cast': 'cast'},
                              ['idle', {'walk': biped_walk}, 'look', {'aggro': f'q.has_target && {notcast}'}, {'attack': f'q.is_delayed_attacking && {notcast}'}, {'cast': "q.property('ecr:casting')"}]),
        'silkqueen': (anims2.spider('silkqueen', amp=20, lift=14),
                      {'idle': 'idle', 'walk': 'walk', 'look': 'look', 'rear': 'rear'},
                      ['idle', {'walk': biped_walk}, 'look', {'rear': "q.has_target && q.is_delayed_attacking || q.property('ecr:casting')"}]),
    }
    for name, b in BOSSES.items():
        builder, mats, gid = mob_bosses2.MODELS[name]
        m = builder()
        m.pack()
        base, glow = m.paint(mats())
        save_tga(base, f'{RP}/textures/entity/{name}.tga')
        save_tga(glow_overlay(glow), f'{RP}/textures/entity/{name}_glow.tga')
        base.save(f'{PREVIEW}/{name}_final_tex.png')
        wjson(f'{RP}/models/entity/{name}.geo.json', m.export())
        anims, amap, animate = specs[name]
        anims2.write(name, anims)
        wjson(f'{RP}/entity/{name}.entity.json', client(name, b, amap, animate))
        wjson(f'{BP}/entities/{name}.json', bp(name, b))
        wjson(f'{BP}/loot_tables/entities/{name}.json', {'pools': LOOT[name]})
        LANG[f'entity.{NS}:{name}.name'] = b['title']
        LANG[f'item.spawn_egg.entity.{NS}:{name}.name'] = f'{b["title"]} Spawn Egg'
    wjson(f'{RP}/render_controllers/ecr_bosses2.render_controllers.json', render_controllers(list(BOSSES)))


if __name__ == '__main__':
    build()
    print('bosses ok')
