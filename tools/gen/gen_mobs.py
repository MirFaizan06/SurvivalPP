"""Builds the three mobs + two projectiles: geometry, textures, client entities, render controllers,
behaviour entities, loot tables and spawn rules."""
import math, random
from PIL import Image
from common import *
import geo
import mob_warg, mob_voidweaver, mob_boss
import anims

NS_ = NS


def glow_overlay(glow_img):
    """glow_img has RGBA with alpha = glow strength; entity_emissive_alpha wants LOW alpha for strong glow."""
    out = Image.new('RGBA', glow_img.size, (0, 0, 0, 0))
    gp, op = glow_img.load(), out.load()
    for y in range(glow_img.height):
        for x in range(glow_img.width):
            r, g, b, a = gp[x, y]
            if a > 0:
                op[x, y] = (r, g, b, max(60, 255 - int(a * 0.62)))
    return out


def build_model(mod, name):
    m = mod.build()
    used = m.pack()
    base, glow = m.paint(mod.materials())
    save_tga(base, f'{RP}/textures/entity/{name}.tga')
    save_tga(glow_overlay(glow), f'{RP}/textures/entity/{name}_glow.tga')
    base.save(f'{PREVIEW}/{name}_final_tex.png')
    wjson(f'{RP}/models/entity/{name}.geo.json', m.export())
    return m


def client_entity(ident, name, geo_id, anim_names, animate, egg, scale=None, extra_scripts=None):
    anims_ = {a: f'animation.ecr_{name}.{a}' for a in anim_names}
    scripts = {'animate': animate}
    if scale:
        scripts['scale'] = scale
    if extra_scripts:
        scripts.update(extra_scripts)
    return {
        'format_version': '1.10.0',
        'minecraft:client_entity': {'description': {
            'identifier': ident,
            'materials': {'default': 'entity_alphatest', 'glow': 'entity_emissive_alpha'},
            'textures': {'default': f'textures/entity/{name}', 'glow': f'textures/entity/{name}_glow'},
            'geometry': {'default': geo_id},
            'animations': anims_,
            'scripts': scripts,
            'render_controllers': [f'controller.render.ecr_{name}', f'controller.render.ecr_{name}_glow'],
            'spawn_egg': {'base_color': egg[0], 'overlay_color': egg[1]},
        }}}


def render_controllers(names):
    rc = {}
    for n in names:
        rc[f'controller.render.ecr_{n}'] = {'geometry': 'Geometry.default', 'materials': [{'*': 'Material.default'}], 'textures': ['Texture.default']}
        rc[f'controller.render.ecr_{n}_glow'] = {'geometry': 'Geometry.default', 'materials': [{'*': 'Material.glow'}], 'textures': ['Texture.glow']}
    return {'format_version': '1.8.0', 'render_controllers': rc}


# --------------------------------------------------------------------------- projectiles
def orb_texture(kind):
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    cx = cy = 7.5
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - cx, y - cy)
            if kind == 'ember':
                if d <= 2.0:
                    c = (255, 246, 200)
                elif d <= 3.6:
                    c = ramp_at(PYRELITE, 0.8 + 0.2 * (1 - (d - 2) / 1.6))
                elif d <= 5.6:
                    c = ramp_at(PYRELITE, 0.45 + 0.25 * (1 - (d - 3.6) / 2.0))
                else:
                    continue
                a = 255 if d <= 5.0 else 190
            elif kind == 'void':
                if d <= 2.2:
                    c = (255, 255, 255)
                elif d <= 4.0:
                    c = ramp_at(ECLIPSITE, 0.62 + 0.38 * (1 - (d - 2.2) / 1.8))
                elif d <= 6.2:
                    c = ramp_at(ECLIPSITE, 0.34 + 0.2 * (1 - (d - 4) / 2.2))
                else:
                    continue
                a = 255 if d <= 5.4 else 180
            else:  # eclipse orb: black disc + corona
                if d <= 3.0:
                    c = (5, 2, 12); a = 255
                elif d <= 4.6:
                    ang = math.atan2(y - cy, x - cx)
                    t = 0.5 + 0.5 * math.cos(ang - 3.9)
                    c = ramp_at(ECLIPSITE, 0.55 + 0.4 * t); a = 255
                elif d <= 7.2:
                    ang = math.atan2(y - cy, x - cx)
                    if abs(math.sin(ang * 4)) > 0.78:
                        c = ramp_at(ECLIPSITE, 0.45); a = 170
                    else:
                        continue
                else:
                    continue
            im.putpixel((x, y), c + (a,))
    return im


def projectile_client(ident, name, scale):
    return {'format_version': '1.10.0', 'minecraft:client_entity': {'description': {
        'identifier': ident,
        'materials': {'default': 'fireball'},
        'textures': {'default': f'textures/entity/{name}'},
        'geometry': {'default': 'geometry.fireball'},
        'animations': {'face_player': 'animation.actor.billboard'},
        'scripts': {'scale': scale, 'animate': ['face_player']},
        'render_controllers': ['controller.render.fireball']}}}


def projectile_bp(ident, power, dmg, effects, particle, gravity=0.0, fire=False):
    comps = {
        'minecraft:type_family': {'family': ['projectile', 'ecr_projectile']},
        'minecraft:collision_box': {'width': 0.35, 'height': 0.35},
        'minecraft:conditional_bandwidth_optimization': {'default_values': {'max_dropped_ticks': 7, 'max_optimized_distance': 80.0, 'use_motion_prediction_hints': True}},
        'minecraft:dimension_bound': {},
        'minecraft:physics': {},
        'minecraft:projectile': {
            'anchor': 'middle', 'gravity': gravity, 'inertia': 1.0, 'liquid_inertia': 1.0,
            'power': power, 'uncertainty_base': 3.0, 'uncertainty_multiplier': 0.0,
            'offset': [0, 0.5, 0], 'isolated_physics': False, 'reflect_on_hurt': True,
            'on_hit': {
                'impact_damage': {'damage': {'min': dmg[0], 'max': dmg[1]}, 'knockback': True, 'apply_knockback_to_blocking_targets': True},
                'particle_on_hit': {'particle_type': particle, 'num_particles': 14, 'on_entity_hit': True, 'on_other_hit': True},
                'remove_on_hit': {}}},
        'minecraft:pushable_by_entity': {},
        'minecraft:pushable_by_block': {},
    }
    on_hit = comps['minecraft:projectile']['on_hit']
    if effects:
        on_hit['mob_effect'] = {'effects': effects}
    if fire:
        on_hit['catch_fire'] = {'fire_affected_by_griefing': False}
        on_hit['impact_damage']['catch_fire'] = True
    return {'format_version': '1.26.50', 'minecraft:entity': {
        'description': {'identifier': ident, 'is_summonable': False, 'is_spawnable': False}, 'components': comps, 'events': None}}


def eff(name, amp, easy, normal, hard):
    return {'effect': name, 'amplifier': amp, 'durationeasy': easy, 'durationnormal': normal, 'durationhard': hard}


# --------------------------------------------------------------------------- common bits
def target_players(priority, dist, must_see=True):
    return {'minecraft:behavior.nearest_attackable_target': {
        'priority': priority, 'must_see': must_see, 'reselect_targets': True,
        'entity_types': [{'filters': {'test': 'is_family', 'subject': 'other', 'operator': '==', 'value': 'player'}, 'max_dist': dist}]}}


def loot(entries):
    pools = []
    for (item, lo, hi, chance, looting) in entries:
        fns = [{'function': 'set_count', 'count': {'min': lo, 'max': hi}}]
        if looting:
            fns.append({'function': 'looting_enchant', 'count': {'min': 0, 'max': looting}})
        pool = {'rolls': 1, 'entries': [{'type': 'item', 'name': item, 'weight': 1, 'functions': fns}]}
        conds = []
        if chance < 1:
            conds.append({'condition': 'random_chance', 'chance': chance})
        if conds:
            pool['conditions'] = conds
        pools.append(pool)
    return {'pools': pools}


def spawn_rule(ident, conds, pop='monster'):
    return {'format_version': '1.8.0', 'minecraft:spawn_rules': {'description': {'identifier': ident, 'population_control': pop}, 'conditions': conds}}


# --------------------------------------------------------------------------- the entities
def bp_warg():
    comps = {
        'minecraft:type_family': {'family': ['ashen_warg', 'ecr_mob', 'monster', 'mob', 'nether']},
        'minecraft:health': {'value': 70, 'max': 70},
        'minecraft:collision_box': {'width': 1.5, 'height': 1.6},
        'minecraft:movement': {'value': 0.34},
        'minecraft:movement.basic': {},
        'minecraft:navigation.walk': {'avoid_damage_blocks': False, 'avoid_water': False, 'can_pass_doors': False, 'can_break_doors': False, 'can_path_over_lava': True, 'can_walk': True, 'is_amphibious': False},
        'minecraft:jump.static': {},
        'minecraft:attack': {'damage': 9},
        'minecraft:knockback_resistance': {'value': 0.6},
        'minecraft:follow_range': {'value': 40, 'max': 40},
        'minecraft:fire_immune': {},
        'minecraft:behavior.float': {'priority': 0},
        'minecraft:behavior.hurt_by_target': {'priority': 1},
        'minecraft:behavior.random_stroll': {'priority': 6, 'speed_multiplier': 0.8},
        'minecraft:behavior.look_at_player': {'priority': 7, 'look_distance': 10, 'probability': 0.02},
        'minecraft:behavior.random_look_around': {'priority': 8},
        'minecraft:experience_reward': {'on_death': 'query.last_hit_by_player ? 22 : 0'},
        'minecraft:loot': {'table': 'loot_tables/entities/ashen_warg.json'},
        'minecraft:despawn': {'despawn_from_distance': {}},
        'minecraft:nameable': {},
        'minecraft:physics': {},
        'minecraft:pushable_by_entity': {},
        'minecraft:pushable_by_block': {},
        'minecraft:conditional_bandwidth_optimization': {},
        'minecraft:is_hidden_when_invisible': {},
    }
    comps.update(target_players(2, 36))
    groups = {
        'ecr:melee_mode': {
            'minecraft:behavior.leap_at_target': {'priority': 3, 'yd': 0.45, 'must_be_on_ground': True},
            'minecraft:behavior.melee_attack': {'priority': 2, 'speed_multiplier': 1.25, 'track_target': True, 'reach_multiplier': 2.0, 'cooldown_time': 1.0}},
        'ecr:ranged_mode': {
            'minecraft:behavior.ranged_attack': {'priority': 3, 'attack_interval': {'min': 2.5, 'max': 4.5}, 'attack_range': {'min': 0.0, 'max': 22.0}, 'burst_shots': 2, 'burst_interval': 0.4, 'speed_multiplier': 1.1, 'target_in_sight_time': 0.4, 'in_range_movement_mode': 'follow_target'},
            'minecraft:shooter': {'def': 'ecr:ember_spit', 'power': 1.5}},
        'ecr:mode_switcher': {
            'minecraft:target_nearby_sensor': {
                'inside_range': 6.0, 'outside_range': 9.0, 'must_see': True,
                'on_inside_range': {'event': 'ecr:switch_to_melee', 'target': 'self'},
                'on_outside_range': {'event': 'ecr:switch_to_ranged', 'target': 'self'}}},
    }
    events = {
        'minecraft:entity_spawned': {'add': {'component_groups': ['ecr:mode_switcher', 'ecr:melee_mode']}},
        'ecr:switch_to_melee': {'add': {'component_groups': ['ecr:melee_mode']}, 'remove': {'component_groups': ['ecr:ranged_mode']}},
        'ecr:switch_to_ranged': {'add': {'component_groups': ['ecr:ranged_mode']}, 'remove': {'component_groups': ['ecr:melee_mode']}},
    }
    return {'format_version': '1.26.50', 'minecraft:entity': {
        'description': {'identifier': 'ecr:ashen_warg', 'is_spawnable': True, 'is_summonable': True, 'spawn_category': 'monster'},
        'component_groups': groups, 'components': comps, 'events': events}}


def bp_voidweaver():
    comps = {
        'minecraft:type_family': {'family': ['voidweaver', 'ecr_mob', 'monster', 'mob', 'enderling']},
        'minecraft:health': {'value': 52, 'max': 52},
        'minecraft:collision_box': {'width': 0.9, 'height': 2.7},
        'minecraft:movement': {'value': 0.27},
        'minecraft:movement.basic': {},
        'minecraft:navigation.walk': {'avoid_damage_blocks': True, 'avoid_water': True, 'can_pass_doors': True},
        'minecraft:jump.static': {},
        'minecraft:attack': {'damage': 5},
        'minecraft:follow_range': {'value': 40, 'max': 40},
        'minecraft:fire_immune': {},
        'minecraft:behavior.float': {'priority': 0},
        'minecraft:behavior.hurt_by_target': {'priority': 1},
        'minecraft:behavior.ranged_attack': {'priority': 2, 'attack_interval': {'min': 1.4, 'max': 2.6}, 'attack_range': {'min': 0.0, 'max': 20.0}, 'burst_shots': 1, 'speed_multiplier': 1.0, 'target_in_sight_time': 0.5, 'in_range_movement_mode': 'hold_position'},
        'minecraft:shooter': {'def': 'ecr:void_bolt', 'power': 1.5},
        'minecraft:behavior.avoid_mob_type': {'priority': 3, 'entity_types': [{'filters': {'test': 'is_family', 'subject': 'other', 'operator': '==', 'value': 'player'}, 'max_dist': 5.0, 'walk_speed_multiplier': 1.0, 'sprint_speed_multiplier': 1.25}]},
        'minecraft:behavior.random_stroll': {'priority': 6, 'speed_multiplier': 0.7},
        'minecraft:behavior.look_at_player': {'priority': 7, 'look_distance': 12, 'probability': 0.02},
        'minecraft:behavior.random_look_around': {'priority': 8},
        'minecraft:teleport': {'random_teleports': True, 'min_random_teleport_time': 6, 'max_random_teleport_time': 22, 'random_teleport_cube': [16, 10, 16], 'target_distance': 24, 'target_teleport_chance': 0.02, 'teleports_on_projectile_hit': True},
        'minecraft:experience_reward': {'on_death': 'query.last_hit_by_player ? 26 : 0'},
        'minecraft:loot': {'table': 'loot_tables/entities/voidweaver.json'},
        'minecraft:despawn': {'despawn_from_distance': {}},
        'minecraft:nameable': {},
        'minecraft:physics': {},
        'minecraft:pushable_by_entity': {},
        'minecraft:pushable_by_block': {},
        'minecraft:conditional_bandwidth_optimization': {},
        'minecraft:is_hidden_when_invisible': {},
    }
    comps.update(target_players(2, 36))
    return {'format_version': '1.26.50', 'minecraft:entity': {
        'description': {'identifier': 'ecr:voidweaver', 'is_spawnable': True, 'is_summonable': True, 'spawn_category': 'monster'},
        'components': comps, 'events': None}}


def bp_boss():
    comps = {
        'minecraft:type_family': {'family': ['eclipse_sovereign', 'ecr_mob', 'monster', 'mob', 'boss']},
        'minecraft:health': {'value': 1600, 'max': 1600},
        'minecraft:collision_box': {'width': 2.8, 'height': 6.2},
        'minecraft:movement': {'value': 0.28},
        'minecraft:movement.basic': {},
        'minecraft:navigation.walk': {'avoid_damage_blocks': False, 'avoid_water': False, 'can_pass_doors': False, 'can_break_doors': True, 'can_walk': True},
        'minecraft:jump.static': {},
        'minecraft:knockback_resistance': {'value': 1.0},
        'minecraft:follow_range': {'value': 64, 'max': 64},
        'minecraft:fire_immune': {},
        'minecraft:freezing_immune': {},
        'minecraft:boss': {'hud_range': 64, 'should_darken_sky': True, 'name': 'Eclipse Sovereign'},
        'minecraft:damage_sensor': {'triggers': [
            {'cause': 'fall', 'deals_damage': 'no'}, {'cause': 'drowning', 'deals_damage': 'no'}, {'cause': 'suffocation', 'deals_damage': 'no'},
            {'cause': 'lava', 'deals_damage': 'no'}, {'cause': 'fire', 'deals_damage': 'no'}, {'cause': 'fire_tick', 'deals_damage': 'no'}]},
        'minecraft:behavior.float': {'priority': 0},
        'minecraft:behavior.hurt_by_target': {'priority': 1},
        'minecraft:behavior.random_stroll': {'priority': 7, 'speed_multiplier': 0.6},
        'minecraft:behavior.look_at_player': {'priority': 8, 'look_distance': 24, 'probability': 0.05},
        'minecraft:behavior.random_look_around': {'priority': 9},
        'minecraft:experience_reward': {'on_death': '1500'},
        'minecraft:loot': {'table': 'loot_tables/entities/eclipse_sovereign.json'},
        'minecraft:persistent': {},
        'minecraft:nameable': {},
        'minecraft:physics': {},
        'minecraft:pushable_by_block': {},
        'minecraft:conditional_bandwidth_optimization': {},
        'minecraft:is_hidden_when_invisible': {},
    }
    comps.update(target_players(2, 64, must_see=False))
    groups = {
        'ecr:melee_mode': {
            'minecraft:attack': {'damage': 26},
            'minecraft:behavior.melee_box_attack': {'priority': 3, 'speed_multiplier': 1.2, 'horizontal_reach': 2.2, 'track_target': True, 'cooldown_time': 1.4}},
        'ecr:ranged_mode': {
            'minecraft:behavior.ranged_attack': {'priority': 3, 'attack_interval': {'min': 2.5, 'max': 4.5}, 'attack_range': {'min': 0.0, 'max': 48.0}, 'burst_shots': 3, 'burst_interval': 0.35, 'speed_multiplier': 1.0, 'target_in_sight_time': 0.4, 'in_range_movement_mode': 'follow_target'},
            'minecraft:shooter': {'def': 'ecr:eclipse_orb', 'power': 1.6}},
        'ecr:mode_switcher': {
            'minecraft:target_nearby_sensor': {
                'inside_range': 6.0, 'outside_range': 8.0, 'must_see': False,
                'on_inside_range': {'event': 'ecr:switch_to_melee', 'target': 'self'},
                'on_outside_range': {'event': 'ecr:switch_to_ranged', 'target': 'self'}}},
        'ecr:phase_2': {'minecraft:movement': {'value': 0.33}},
        'ecr:phase_3': {'minecraft:movement': {'value': 0.4}},
    }
    events = {
        'minecraft:entity_spawned': {'add': {'component_groups': ['ecr:mode_switcher']}, 'set_property': {'ecr:phase': 0}},
        'ecr:switch_to_melee': {'add': {'component_groups': ['ecr:melee_mode']}, 'remove': {'component_groups': ['ecr:ranged_mode']}},
        'ecr:switch_to_ranged': {'add': {'component_groups': ['ecr:ranged_mode']}, 'remove': {'component_groups': ['ecr:melee_mode']}},
        'ecr:enter_phase_2': {'add': {'component_groups': ['ecr:phase_2']}, 'set_property': {'ecr:phase': 1}},
        'ecr:enter_phase_3': {'add': {'component_groups': ['ecr:phase_3']}, 'remove': {'component_groups': ['ecr:phase_2']}, 'set_property': {'ecr:phase': 2}},
        'ecr:cast_on': {'set_property': {'ecr:casting': True}},
        'ecr:cast_off': {'set_property': {'ecr:casting': False}},
    }
    return {'format_version': '1.26.50', 'minecraft:entity': {
        'description': {
            'identifier': 'ecr:eclipse_sovereign', 'is_spawnable': True, 'is_summonable': True, 'spawn_category': 'monster',
            'properties': {
                'ecr:phase': {'type': 'int', 'range': [0, 2], 'default': 0, 'client_sync': True},
                'ecr:casting': {'type': 'bool', 'default': False, 'client_sync': True}}},
        'component_groups': groups, 'components': comps, 'events': events}}


def build():
    m_w = build_model(mob_warg, 'ashen_warg')
    m_v = build_model(mob_voidweaver, 'voidweaver')
    m_b = build_model(mob_boss, 'eclipse_sovereign')
    anims.write_all()

    wjson(f'{RP}/entity/ashen_warg.entity.json', client_entity(
        'ecr:ashen_warg', 'ashen_warg', mob_warg.ID, ['idle', 'walk', 'look', 'attack', 'hunt'],
        ['idle', {'walk': 'q.modified_move_speed > 0.02'}, 'look', 'attack', {'hunt': 'q.has_target'}], ('#1c1210', '#ff8a1e'), scale='1.0'))
    wjson(f'{RP}/entity/voidweaver.entity.json', client_entity(
        'ecr:voidweaver', 'voidweaver', mob_voidweaver.ID, ['idle', 'walk', 'look', 'combat'],
        ['idle', {'walk': 'q.modified_move_speed > 0.02'}, 'look', {'combat': 'q.has_target'}], ('#150a33', '#c046dc'), scale='1.0'))
    wjson(f'{RP}/entity/eclipse_sovereign.entity.json', client_entity(
        'ecr:eclipse_sovereign', 'eclipse_sovereign', mob_boss.ID, ['idle', 'walk', 'look', 'slam', 'combat', 'cast'],
        ['idle', {'walk': 'q.modified_move_speed > 0.02'}, 'look', 'slam', {'combat': 'q.has_target && !q.property(\'ecr:casting\')'}, {'cast': 'q.property(\'ecr:casting\')'}],
        ('#05020c', '#ff9cf0'), scale='1.0'))
    wjson(f'{RP}/render_controllers/ecr_mobs.render_controllers.json', render_controllers(['ashen_warg', 'voidweaver', 'eclipse_sovereign']))

    # projectiles
    save_png(orb_texture('void'), f'{RP}/textures/entity/void_bolt.png')
    save_png(orb_texture('eclipse'), f'{RP}/textures/entity/eclipse_orb.png')
    save_png(orb_texture('ember'), f'{RP}/textures/entity/ember_spit.png')
    wjson(f'{RP}/entity/ember_spit.entity.json', projectile_client('ecr:ember_spit', 'ember_spit', '1.5'))
    wjson(f'{BP}/entities/ember_spit.json', projectile_bp('ecr:ember_spit', 1.4, (5, 7), [], 'lava', fire=True))
    wjson(f'{RP}/entity/void_bolt.entity.json', projectile_client('ecr:void_bolt', 'void_bolt', '1.4'))
    wjson(f'{RP}/entity/eclipse_orb.entity.json', projectile_client('ecr:eclipse_orb', 'eclipse_orb', '2.6'))
    wjson(f'{BP}/entities/void_bolt.json', projectile_bp('ecr:void_bolt', 1.5, (6, 8), [eff('slowness', 1, 80, 100, 140), eff('blindness', 0, 0, 40, 80)], 'witchspell'))
    wjson(f'{BP}/entities/eclipse_orb.json', projectile_bp('ecr:eclipse_orb', 1.35, (14, 18), [eff('wither', 1, 100, 160, 240), eff('weakness', 1, 100, 140, 200)], 'largeexplode'))

    wjson(f'{BP}/entities/ashen_warg.json', bp_warg())
    wjson(f'{BP}/entities/voidweaver.json', bp_voidweaver())
    wjson(f'{BP}/entities/eclipse_sovereign.json', bp_boss())

    # loot
    wjson(f'{BP}/loot_tables/entities/ashen_warg.json', loot([('ecr:ember_fang', 1, 2, 1.0, 1), ('ecr:raw_pyrelite', 1, 1, 0.12, 1), ('minecraft:blaze_powder', 0, 2, 0.5, 1)]))
    wjson(f'{BP}/loot_tables/entities/voidweaver.json', loot([('ecr:void_essence', 1, 2, 1.0, 1), ('minecraft:ender_pearl', 0, 1, 0.5, 1), ('ecr:raw_eclipsite', 1, 1, 0.1, 1)]))
    wjson(f'{BP}/loot_tables/entities/eclipse_sovereign.json', loot([
        ('ecr:eclipse_core', 1, 1, 1.0, 0), ('ecr:raw_eclipsite', 8, 14, 1.0, 0), ('ecr:void_essence', 5, 9, 1.0, 0),
        ('minecraft:netherite_ingot', 1, 3, 1.0, 0), ('minecraft:diamond', 6, 12, 1.0, 0), ('minecraft:elytra', 1, 1, 0.25, 0)]))

    # spawns
    wjson(f'{BP}/spawn_rules/ashen_warg.json', spawn_rule('ecr:ashen_warg', [
        {'minecraft:spawns_underground': {}, 'minecraft:difficulty_filter': {'min': 'easy', 'max': 'hard'},
         'minecraft:weight': {'default': 5}, 'minecraft:herd': {'min_size': 1, 'max_size': 3},
         'minecraft:biome_filter': {'test': 'has_biome_tag', 'operator': '==', 'value': 'nether'}}]))
    wjson(f'{BP}/spawn_rules/voidweaver.json', spawn_rule('ecr:voidweaver', [
        {'minecraft:spawns_on_surface': {}, 'minecraft:difficulty_filter': {'min': 'easy', 'max': 'hard'},
         'minecraft:weight': {'default': 4}, 'minecraft:herd': {'min_size': 1, 'max_size': 1},
         'minecraft:spawns_on_block_filter': ['minecraft:end_stone'],
         'minecraft:biome_filter': {'test': 'has_biome_tag', 'operator': '==', 'value': 'the_end'}}]))
    return {'warg': m_w, 'void': m_v, 'boss': m_b}


if __name__ == '__main__':
    build()
    print('mobs ok')
