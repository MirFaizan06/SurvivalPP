"""v1.2 hostiles: Gravewalker, Revenant, Cave Weaver, Sporeling (+ Bone Shard / Web Bolt projectiles).
Geometry, glow overlays, animations, client + behaviour entities, loot and spawn rules."""
import math
from PIL import Image
from common import *
from registry import LANG
import mob_hostiles, anims2
from gen_mobs import (glow_overlay, client_entity, render_controllers, projectile_client, projectile_bp, eff,
                      target_players, spawn_rule)
from gen_animals import entry

MON = {
    'gravewalker': dict(title='Gravewalker', egg=('#2a4a38', '#cfc29b'), xp=7),
    'revenant': dict(title='Revenant', egg=('#a2b0b2', '#5ae6ff'), xp=10),
    'cave_weaver': dict(title='Cave Weaver', egg=('#241f44', '#e060ff'), xp=9),
    'sporeling': dict(title='Sporeling', egg=('#1ea080', '#d8f0b0'), xp=6),
}


# ----------------------------------------------------------------------------- projectile sprites
def sprite_shard():
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y in range(16):
        for x in range(16):
            d = abs(x - 7.5) / 3.2 + abs(y - 7.5) / 6.4
            if d <= 0.45:
                c = (240, 253, 255); a = 255
            elif d <= 1.0:
                t = (1 - d) / 0.55
                c = ramp_at(R_CYAN, 0.35 + 0.5 * t); a = 255
            elif d <= 1.35:
                c = ramp_at(R_CYAN, 0.3); a = 150
            else:
                continue
            im.putpixel((x, y), c + (a,))
    return im


def sprite_web():
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    cx = cy = 7.5
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - cx, y - cy)
            ang = math.atan2(y - cy, x - cx)
            spoke = abs(math.sin(ang * 4)) > 0.9
            ring = abs(d - 3.0) < 0.55 or abs(d - 5.6) < 0.55
            if d <= 1.6:
                c = (255, 255, 255); a = 255
            elif d <= 7.0 and (spoke or ring):
                c = (232, 228, 250); a = 235
            elif d <= 5.8 and d > 1.6:
                c = (190, 184, 225); a = 70
            else:
                continue
            im.putpixel((x, y), c + (a,))
    return im


R_CYAN = [hx(c) for c in ('#08485a', '#12a0c0', '#5ae6ff', '#d8fbff')]


# ----------------------------------------------------------------------------- behaviour entities
COMMON = {
    'minecraft:breathable': {'total_supply': 15, 'suffocate_time': 0},
    'minecraft:despawn': {'despawn_from_distance': {}},
    'minecraft:nameable': {},
    'minecraft:physics': {},
    'minecraft:pushable_by_entity': {},
    'minecraft:pushable_by_block': {},
    'minecraft:conditional_bandwidth_optimization': {},
    'minecraft:is_hidden_when_invisible': {},
    'minecraft:jump.static': {},
    'minecraft:movement.basic': {},
    'minecraft:behavior.float': {'priority': 0},
    'minecraft:behavior.look_at_player': {'priority': 8, 'look_distance': 10, 'probability': 0.02},
    'minecraft:behavior.random_look_around': {'priority': 9},
}


def base(family, hp, speed, box, xp, name, extra=None, spawn='monster'):
    comps = dict(COMMON)
    comps.update({
        'minecraft:type_family': {'family': family + ['ecr_mob', 'monster', 'mob']},
        'minecraft:health': {'value': hp, 'max': hp},
        'minecraft:movement': {'value': speed},
        'minecraft:collision_box': {'width': box[0], 'height': box[1]},
        'minecraft:follow_range': {'value': 32, 'max': 32},
        'minecraft:experience_reward': {'on_death': f'query.last_hit_by_player ? {xp} : 0'},
        'minecraft:loot': {'table': f'loot_tables/entities/{name}.json'},
        'minecraft:behavior.hurt_by_target': {'priority': 1},
        'minecraft:behavior.random_stroll': {'priority': 7, 'speed_multiplier': 0.9},
    })
    comps.update(target_players(2, 28, must_see=False))
    if extra:
        comps.update(extra)
    return comps


def entity(name, comps, groups=None, events=None, props=None):
    desc = {'identifier': f'{NS}:{name}', 'is_spawnable': True, 'is_summonable': True, 'spawn_category': 'monster'}
    if props:
        desc['properties'] = props
    e = {'description': desc, 'components': comps}
    if groups:
        e['component_groups'] = groups
    if events:
        e['events'] = events
    return {'format_version': '1.26.50', 'minecraft:entity': e}


def bp_gravewalker():
    comps = base(['gravewalker', 'undead'], 26, 0.23, (0.7, 1.95), MON['gravewalker']['xp'], 'gravewalker', {
        'minecraft:navigation.walk': {'is_amphibious': True, 'can_pass_doors': True, 'can_break_doors': True, 'avoid_water': False},
        'minecraft:attack': {'damage': 5, 'effect_name': 'weakness', 'effect_duration': 7},
        'minecraft:burns_in_daylight': {},
        'minecraft:knockback_resistance': {'value': 0.25},
        'minecraft:behavior.break_door': {'priority': 4},
        'minecraft:behavior.melee_attack': {'priority': 3, 'speed_multiplier': 1.1, 'track_target': True},
        'minecraft:behavior.mount_pathing': {'priority': 5, 'speed_multiplier': 1.15, 'target_dist': 0.0, 'track_target': True},
    })
    return entity('gravewalker', comps)


def bp_revenant():
    comps = base(['revenant', 'undead', 'skeleton'], 30, 0.27, (0.7, 2.0), MON['revenant']['xp'], 'revenant', {
        'minecraft:navigation.walk': {'is_amphibious': True, 'can_pass_doors': True, 'avoid_water': False},
        'minecraft:knockback_resistance': {'value': 0.2},
        'minecraft:behavior.avoid_mob_type': {'priority': 4, 'entity_types': [
            {'filters': {'test': 'is_family', 'subject': 'other', 'operator': '==', 'value': 'wolf'}, 'max_dist': 6, 'walk_speed_multiplier': 1.0, 'sprint_speed_multiplier': 1.2}]},
    })
    groups = {
        'ecr:melee_mode': {
            'minecraft:attack': {'damage': 6},
            'minecraft:behavior.melee_attack': {'priority': 3, 'speed_multiplier': 1.25, 'track_target': True}},
        'ecr:ranged_mode': {
            'minecraft:behavior.ranged_attack': {'priority': 3, 'attack_interval': {'min': 1.3, 'max': 2.2}, 'attack_range': {'min': 0.0, 'max': 24.0}, 'burst_shots': 2, 'burst_interval': 0.3, 'speed_multiplier': 1.0, 'target_in_sight_time': 0.4, 'in_range_movement_mode': 'hold_position'},
            'minecraft:shooter': {'def': 'ecr:bone_shard', 'power': 1.7}},
        'ecr:mode_switcher': {'minecraft:target_nearby_sensor': {
            'inside_range': 4.0, 'outside_range': 6.5, 'must_see': True,
            'on_inside_range': {'event': 'ecr:switch_to_melee', 'target': 'self'},
            'on_outside_range': {'event': 'ecr:switch_to_ranged', 'target': 'self'}}},
    }
    events = {
        'minecraft:entity_spawned': {'add': {'component_groups': ['ecr:mode_switcher', 'ecr:ranged_mode']}},
        'ecr:switch_to_melee': {'add': {'component_groups': ['ecr:melee_mode']}, 'remove': {'component_groups': ['ecr:ranged_mode']}},
        'ecr:switch_to_ranged': {'add': {'component_groups': ['ecr:ranged_mode']}, 'remove': {'component_groups': ['ecr:melee_mode']}},
    }
    return entity('revenant', comps, groups, events)


def bp_weaver():
    comps = base(['cave_weaver', 'arthropod'], 34, 0.3, (1.5, 0.95), MON['cave_weaver']['xp'], 'cave_weaver', {
        'minecraft:navigation.climb': {'can_path_over_water': True, 'can_break_doors': False},
        'minecraft:can_climb': {},
        'minecraft:block_movement_slowdown_immunity': {},
        'minecraft:knockback_resistance': {'value': 0.1},
        'minecraft:damage_sensor': {'triggers': [{'cause': 'fall', 'deals_damage': 'no'}]},
    })
    comps['minecraft:navigation.climb'] = {'can_path_over_water': True}
    comps['minecraft:movement.basic'] = {}
    groups = {
        'ecr:melee_mode': {
            'minecraft:attack': {'damage': 5, 'effect_name': 'poison', 'effect_duration': 8},
            'minecraft:behavior.leap_at_target': {'priority': 3, 'yd': 0.35, 'must_be_on_ground': True},
            'minecraft:behavior.melee_attack': {'priority': 4, 'speed_multiplier': 1.2, 'track_target': True}},
        'ecr:ranged_mode': {
            'minecraft:behavior.ranged_attack': {'priority': 3, 'attack_interval': {'min': 3.0, 'max': 5.0}, 'attack_range': {'min': 0.0, 'max': 16.0}, 'burst_shots': 1, 'speed_multiplier': 1.0, 'target_in_sight_time': 0.5, 'in_range_movement_mode': 'follow_target'},
            'minecraft:shooter': {'def': 'ecr:web_bolt', 'power': 1.3}},
        'ecr:mode_switcher': {'minecraft:target_nearby_sensor': {
            'inside_range': 4.5, 'outside_range': 7.0, 'must_see': True,
            'on_inside_range': {'event': 'ecr:switch_to_melee', 'target': 'self'},
            'on_outside_range': {'event': 'ecr:switch_to_ranged', 'target': 'self'}}},
    }
    events = {
        'minecraft:entity_spawned': {'add': {'component_groups': ['ecr:mode_switcher', 'ecr:melee_mode']}},
        'ecr:switch_to_melee': {'add': {'component_groups': ['ecr:melee_mode']}, 'remove': {'component_groups': ['ecr:ranged_mode']}},
        'ecr:switch_to_ranged': {'add': {'component_groups': ['ecr:ranged_mode']}, 'remove': {'component_groups': ['ecr:melee_mode']}},
    }
    return entity('cave_weaver', comps, groups, events)


def bp_sporeling():
    comps = base(['sporeling', 'fungus'], 12, 0.2, (0.8, 1.1), MON['sporeling']['xp'], 'sporeling', {
        'minecraft:navigation.walk': {'can_pass_doors': True, 'avoid_water': False},
        'minecraft:attack': {'damage': 3, 'effect_name': 'nausea', 'effect_duration': 9},
        'minecraft:behavior.melee_attack': {'priority': 3, 'speed_multiplier': 1.15, 'track_target': True},
        'minecraft:target_nearby_sensor': {
            'inside_range': 3.2, 'outside_range': 4.5, 'must_see': False,
            'on_inside_range': {'event': 'ecr:puff_on', 'target': 'self'},
            'on_outside_range': {'event': 'ecr:puff_off', 'target': 'self'}},
    })
    comps['minecraft:follow_range'] = {'value': 20, 'max': 20}
    events = {
        'ecr:puff_on': {'set_property': {'ecr:puffing': True}},
        'ecr:puff_off': {'set_property': {'ecr:puffing': False}},
    }
    return entity('sporeling', comps, None, events, {'ecr:puffing': {'type': 'bool', 'default': False, 'client_sync': True}})


# ----------------------------------------------------------------------------- loot / spawn
LOOT = {
    'gravewalker': [entry('minecraft:rotten_flesh', 0, 2), entry('ecr:grave_dust', 0, 2), entry('ecr:hollow_bone', 0, 1, chance=0.3),
                    entry('minecraft:iron_ingot', 1, 1, looting=0, chance=0.03), entry('minecraft:potato', 1, 1, looting=0, chance=0.03)],
    'revenant': [entry('minecraft:bone', 0, 2), entry('ecr:hollow_bone', 0, 2), entry('minecraft:arrow', 0, 3), entry('ecr:grave_dust', 0, 1, chance=0.4),
                 entry('minecraft:bow', 1, 1, looting=0, chance=0.06)],
    'cave_weaver': [entry('minecraft:string', 1, 3), entry('minecraft:spider_eye', 0, 1, chance=0.5), entry('ecr:silk_gland', 0, 1, chance=0.45)],
    'sporeling': [entry('ecr:spore_cluster', 1, 2), entry('minecraft:brown_mushroom', 0, 2), entry('minecraft:red_mushroom', 0, 1, chance=0.5)],
}


def monster_rule(name, weight, herd, tags, surface=True, underground=True, bright=(0, 7), extra=None):
    cond = {}
    if surface:
        cond['minecraft:spawns_on_surface'] = {}
    if underground:
        cond['minecraft:spawns_underground'] = {}
    cond.update({
        'minecraft:brightness_filter': {'min': bright[0], 'max': bright[1], 'adjust_for_weather': True},
        'minecraft:difficulty_filter': {'min': 'easy', 'max': 'hard'},
        'minecraft:weight': {'default': weight},
        'minecraft:herd': {'min_size': herd[0], 'max_size': herd[1]},
        'minecraft:biome_filter': {'any_of': [{'test': 'has_biome_tag', 'operator': '==', 'value': t} for t in tags]}})
    if extra:
        cond.update(extra)
    return spawn_rule(f'{NS}:{name}', [cond], 'monster')


def spawns():
    wjson(f'{BP}/spawn_rules/gravewalker.json', monster_rule('gravewalker', 28, (1, 3), ['forest', 'plains', 'taiga', 'roofed', 'swamp', 'cherry_grove'], underground=False,
                                                             extra={'minecraft:spawns_on_block_filter': ['minecraft:grass_block', 'minecraft:dirt', 'minecraft:podzol', 'minecraft:coarse_dirt', 'minecraft:moss_block']}))
    wjson(f'{BP}/spawn_rules/revenant.json', monster_rule('revenant', 22, (1, 2), ['extreme_hills', 'mountains', 'taiga', 'caves', 'plains']))
    # Cave Weavers live underground everywhere, and creep up through the roots of cherry groves at night (the Chapter I quest needs them there)
    cw = monster_rule('cave_weaver', 30, (1, 2), ['monster'], surface=False)
    cw['minecraft:spawn_rules']['conditions'] += monster_rule('cave_weaver', 22, (1, 2), ['cherry_grove'], underground=False)['minecraft:spawn_rules']['conditions']
    wjson(f'{BP}/spawn_rules/cave_weaver.json', cw)
    wjson(f'{BP}/spawn_rules/sporeling.json', monster_rule('sporeling', 26, (2, 4), ['lush_caves', 'mangrove_swamp', 'swamp', 'roofed', 'mooshroom_island']))


# ----------------------------------------------------------------------------- build
def build():
    specs = {
        'gravewalker': (['idle', 'walk', 'look', 'aggro', 'attack'],
                        ['idle', {'walk': 'q.modified_move_speed > 0.02'}, 'look', {'aggro': 'q.has_target'}, {'attack': 'q.is_delayed_attacking'}]),
        'revenant': (['idle', 'walk', 'look', 'aggro', 'attack'],
                     ['idle', {'walk': 'q.modified_move_speed > 0.02'}, 'look', {'aggro': 'q.has_target'}, {'attack': 'q.is_delayed_attacking'}]),
        'cave_weaver': (['idle', 'walk', 'look', 'rear'],
                        ['idle', {'walk': 'q.modified_move_speed > 0.02'}, 'look', {'rear': 'q.has_target && q.is_delayed_attacking'}]),
        'sporeling': (['idle', 'walk', 'look', 'puff'],
                      ['idle', {'walk': 'q.modified_move_speed > 0.02'}, 'look', {'puff': "q.property('ecr:puffing')"}]),
    }
    anim_sets = {
        'gravewalker': anims2.biped('gravewalker', arm=-72, sway=[f'strip{i}' for i in range(5)], leg='leg', shamble=1.4, cast=False),
        'revenant': anims2.biped('revenant', arm=-80, sway=[f'rag{i}' for i in range(5)], leg='leg', shin='shin', legamp=42, bow=True, cast=False),
        'cave_weaver': anims2.spider('cave_weaver'),
        'sporeling': anims2.spores('sporeling'),
    }
    for name, a in MON.items():
        builder, mats, gid = mob_hostiles.MODELS[name]
        m = builder()
        m.pack()
        base_img, glow = m.paint(mats())
        save_tga(base_img, f'{RP}/textures/entity/{name}.tga')
        save_tga(glow_overlay(glow), f'{RP}/textures/entity/{name}_glow.tga')
        base_img.save(f'{PREVIEW}/{name}_final_tex.png')
        wjson(f'{RP}/models/entity/{name}.geo.json', m.export())
        names, animate = specs[name]
        wjson(f'{RP}/entity/{name}.entity.json', client_entity(f'{NS}:{name}', name, gid, names, animate, a['egg'], scale='1.0'))
        anims2.write(name, anim_sets[name])
        LANG[f'entity.{NS}:{name}.name'] = a['title']
        LANG[f'item.spawn_egg.entity.{NS}:{name}.name'] = f'{a["title"]} Spawn Egg'
        wjson(f'{BP}/loot_tables/entities/{name}.json', {'pools': LOOT[name]})
    wjson(f'{RP}/render_controllers/ecr_hostiles.render_controllers.json', render_controllers(list(MON)))
    wjson(f'{BP}/entities/gravewalker.json', bp_gravewalker())
    wjson(f'{BP}/entities/revenant.json', bp_revenant())
    wjson(f'{BP}/entities/cave_weaver.json', bp_weaver())
    wjson(f'{BP}/entities/sporeling.json', bp_sporeling())
    spawns()
    # projectiles
    save_png(sprite_shard(), f'{RP}/textures/entity/bone_shard.png')
    save_png(sprite_web(), f'{RP}/textures/entity/web_bolt.png')
    wjson(f'{RP}/entity/bone_shard.entity.json', projectile_client(f'{NS}:bone_shard', 'bone_shard', '1.2'))
    wjson(f'{RP}/entity/web_bolt.entity.json', projectile_client(f'{NS}:web_bolt', 'web_bolt', '1.5'))
    wjson(f'{BP}/entities/bone_shard.json', projectile_bp(f'{NS}:bone_shard', 1.7, (4, 6), [eff('slowness', 0, 60, 100, 140)], 'witchspell', gravity=0.03))
    wjson(f'{BP}/entities/web_bolt.json', projectile_bp(f'{NS}:web_bolt', 1.3, (1, 2), [eff('slowness', 2, 80, 120, 160)], 'snowballpoof', gravity=0.04))
    LANG[f'entity.{NS}:bone_shard.name'] = 'Bone Shard'
    LANG[f'entity.{NS}:web_bolt.name'] = 'Web Bolt'


if __name__ == '__main__':
    build()
    print('hostiles ok')
