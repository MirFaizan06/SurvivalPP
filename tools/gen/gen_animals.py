"""v1.2 animals: Meadow Deer, Highland Yak, Wild Boar, Pheasant.
Geometry + textures + animations + client entities + behaviour entities (breeding, babies, panic/defence) + loot + spawn rules."""
from common import *
from registry import LANG
import mob_animals, anims2
from gen_mobs import spawn_rule

FEED_DEER = ['minecraft:apple', 'ecr:oats', 'minecraft:wheat', 'ecr:strawberry']
FEED_YAK = ['minecraft:wheat', 'ecr:oats', 'minecraft:hay_block']
FEED_BOAR = ['minecraft:carrot', 'minecraft:potato', 'minecraft:beetroot', 'ecr:corn_cob']
FEED_PHEASANT = ['minecraft:wheat_seeds', 'minecraft:beetroot_seeds', 'ecr:corn_kernels', 'ecr:oat_seeds']

ANIMALS = {
    'meadow_deer': dict(title='Meadow Deer', hp=14, box=(0.9, 1.7), speed=0.3, feed=FEED_DEER, egg=('#8b5c33', '#f0e6cf'), xp=3, kind='quad', panic=1.6),
    'highland_yak': dict(title='Highland Yak', hp=30, box=(1.5, 1.7), speed=0.2, feed=FEED_YAK, egg=('#2a2018', '#b09c74'), xp=3, kind='quad', panic=1.2, milk=True, kb=0.4),
    'wild_boar': dict(title='Wild Boar', hp=18, box=(1.0, 1.0), speed=0.26, feed=FEED_BOAR, egg=('#38291d', '#e9dcc0'), xp=3, kind='quad', defend=5),
    'pheasant': dict(title='Pheasant', hp=5, box=(0.5, 0.75), speed=0.26, feed=FEED_PHEASANT, egg=('#bb7430', '#1fc088'), xp=2, kind='bird', panic=1.6),
}


# ----------------------------------------------------------------------------- client side
def client(name, a):
    anims = ['idle', 'walk', 'look'] + (['flap'] if a['kind'] == 'bird' else [])
    animate = ['idle', {'walk': 'q.modified_move_speed > 0.02'}, 'look']
    if a['kind'] == 'bird':
        animate.append({'flap': '!q.is_on_ground && !q.is_in_water'})
    return {'format_version': '1.10.0', 'minecraft:client_entity': {'description': {
        'identifier': f'{NS}:{name}',
        'materials': {'default': 'entity_alphatest'},
        'textures': {'default': f'textures/entity/{name}'},
        'geometry': {'default': f'geometry.ecr_{name}'},
        'animations': {k: f'animation.ecr_{name}.{k}' for k in anims},
        'scripts': {'animate': animate},
        'render_controllers': [f'controller.render.ecr_{name}'],
        'spawn_egg': {'base_color': a['egg'][0], 'overlay_color': a['egg'][1]}}}}


def render_controllers():
    rc = {}
    for n in ANIMALS:
        c = {'geometry': 'Geometry.default', 'materials': [{'*': 'Material.default'}], 'textures': ['Texture.default']}
        if n == 'meadow_deer':
            vis = "q.property('ecr:stag') == 1 && !q.is_baby"
            c['part_visibility'] = [{'antler_l': vis}, {'antler_r': vis}]
        rc[f'controller.render.ecr_{n}'] = c
    return {'format_version': '1.8.0', 'render_controllers': rc}


# ----------------------------------------------------------------------------- behaviour entity
def bp(name, a):
    ident = f'{NS}:{name}'
    w, h = a['box']
    feed = a['feed']
    adult = {
        'minecraft:experience_reward': {'on_bred': 'Math.Random(1,7)', 'on_death': f'query.last_hit_by_player ? Math.Random(1,{a["xp"]}) : 0'},
        'minecraft:loot': {'table': f'loot_tables/entities/{name}.json'},
        'minecraft:leashable_to': {'unleash_on_removal': False},
        'minecraft:breedable': {'require_tame': False, 'breeds_with': {ident: {}}, 'breed_items': feed},
        'minecraft:behavior.breed': {'priority': 3, 'speed_multiplier': 1.0},
    }
    baby = {
        'minecraft:is_baby': {},
        'minecraft:scale': {'value': 0.5},
        'minecraft:ageable': {'duration': 1200, 'feed_items': feed, 'grow_up': {'event': 'minecraft:ageable_grow_up', 'target': 'self'}},
        'minecraft:behavior.follow_parent': {'priority': 5, 'speed_multiplier': 1.1},
    }
    comps = {
        'minecraft:type_family': {'family': [name, 'ecr_animal', 'animal', 'mob']},
        'minecraft:breathable': {'total_supply': 15, 'suffocate_time': 0},
        'minecraft:collision_box': {'width': w, 'height': h},
        'minecraft:nameable': {},
        'minecraft:health': {'value': a['hp'], 'max': a['hp']},
        'minecraft:hurt_on_condition': {'damage_conditions': [{
            'filters': {'test': 'in_lava', 'subject': 'self', 'operator': '==', 'value': True}, 'cause': 'lava', 'damage_per_tick': 4}]},
        'minecraft:movement': {'value': a['speed']},
        'minecraft:navigation.walk': {'can_path_over_water': True, 'avoid_water': True, 'avoid_damage_blocks': True},
        'minecraft:movement.basic': {},
        'minecraft:jump.static': {},
        'minecraft:can_climb': {},
        'minecraft:despawn': {'despawn_from_distance': {}},
        'minecraft:leashable': {},
        'minecraft:balloonable': {},
        'minecraft:physics': {},
        'minecraft:pushable_by_entity': {},
        'minecraft:pushable_by_block': {},
        'minecraft:conditional_bandwidth_optimization': {},
        'minecraft:is_hidden_when_invisible': {},
        'minecraft:spawn_egg_interaction': {},
        'minecraft:offspring': {'offspring_pairs': {ident: ident}},
        'minecraft:behavior.float': {'priority': 0},
        'minecraft:behavior.tempt': {'priority': 4, 'speed_multiplier': 1.2, 'items': feed},
        'minecraft:behavior.random_stroll': {'priority': 6, 'speed_multiplier': 0.8},
        'minecraft:behavior.look_at_player': {'priority': 7, 'look_distance': 6.0, 'probability': 0.02},
        'minecraft:behavior.random_look_around': {'priority': 9},
    }
    if a.get('kb'):
        comps['minecraft:knockback_resistance'] = {'value': a['kb']}
    if a.get('panic'):
        comps['minecraft:behavior.panic'] = {'priority': 1, 'speed_multiplier': a['panic']}
    if a['kind'] == 'bird':
        comps['minecraft:damage_sensor'] = {'triggers': {'cause': 'fall', 'deals_damage': 'no'}}
        comps['minecraft:game_event_movement_tracking'] = {'emit_flap': True}
        comps['minecraft:navigation.walk']['using_door_annotation'] = True
    groups = {}
    props = {}
    events = {}
    if a.get('defend'):
        # neutral until hurt: the whole sounder joins in
        adult['minecraft:attack'] = {'damage': a['defend']}
        adult['minecraft:behavior.hurt_by_target'] = {'priority': 1, 'alert_same_type': True}
        adult['minecraft:behavior.melee_attack'] = {'priority': 2, 'speed_multiplier': 1.35, 'track_target': True, 'reach_multiplier': 1.2}
        baby['minecraft:behavior.panic'] = {'priority': 1, 'speed_multiplier': 1.4}
        comps['minecraft:knockback_resistance'] = {'value': 0.2}
    if a.get('milk'):
        adult['minecraft:interact'] = {'interactions': [{
            'on_interact': {'filters': {'all_of': [
                {'test': 'is_family', 'subject': 'other', 'value': 'player'},
                {'test': 'has_equipment', 'domain': 'hand', 'subject': 'other', 'value': 'bucket:0'}]}},
            'use_item': True, 'swing': True, 'transform_to_item': 'bucket:1', 'play_sounds': 'milk', 'interact_text': 'action.interact.milk'}]}
    if a['kind'] == 'bird':
        # moulting: pheasants drop a feather now and then
        adult['minecraft:spawn_entity'] = {'entities': [{'min_wait_time': 400, 'max_wait_time': 900, 'spawn_sound': 'plop', 'spawn_item': 'feather',
                                                         'filters': {'test': 'rider_count', 'subject': 'self', 'operator': '==', 'value': 0}}]}
    spawn_events = {'minecraft:spawn_adult': {'add': {'component_groups': [f'ecr:{name}_adult']}}}
    spawn_seq = [{'randomize': [{'weight': 92, 'trigger': 'minecraft:spawn_adult'}, {'weight': 8, 'add': {'component_groups': [f'ecr:{name}_baby']}}]}]
    born = {'add': {'component_groups': [f'ecr:{name}_baby']}}
    if name == 'meadow_deer':
        props['ecr:stag'] = {'type': 'bool', 'default': False, 'client_sync': True}
        events['ecr:roll_stag'] = {'randomize': [{'weight': 1, 'set_property': {'ecr:stag': True}}, {'weight': 1, 'set_property': {'ecr:stag': False}}]}
        born['trigger'] = 'ecr:roll_stag'
        spawn_seq.append({'trigger': 'ecr:roll_stag'})
    groups[f'ecr:{name}_baby'] = baby
    groups[f'ecr:{name}_adult'] = adult
    events.update({
        'minecraft:entity_spawned': {'sequence': spawn_seq},
        'minecraft:entity_born': born,
        'minecraft:ageable_grow_up': {'remove': {'component_groups': [f'ecr:{name}_baby']}, 'add': {'component_groups': [f'ecr:{name}_adult']}},
        'minecraft:entity_transformed': {'remove': {}, 'add': {'component_groups': [f'ecr:{name}_adult']}},
    })
    events.update(spawn_events)
    desc = {'identifier': ident, 'spawn_category': 'creature', 'is_spawnable': True, 'is_summonable': True}
    if props:
        desc['properties'] = props
    return {'format_version': '1.26.50', 'minecraft:entity': {'description': desc, 'component_groups': groups, 'components': comps, 'events': events}}


# ----------------------------------------------------------------------------- loot
def entry(item, lo, hi, smelt=False, looting=1, chance=1.0):
    fns = [{'function': 'set_count', 'count': {'min': lo, 'max': hi}}]
    if smelt:
        fns.append({'function': 'furnace_smelt', 'conditions': [{'condition': 'entity_properties', 'entity': 'this', 'properties': {'on_fire': True}}]})
    if looting:
        fns.append({'function': 'looting_enchant', 'count': {'min': 0, 'max': looting}})
    pool = {'rolls': 1, 'entries': [{'type': 'item', 'name': item, 'weight': 1, 'functions': fns}]}
    if chance < 1:
        pool['conditions'] = [{'condition': 'random_chance', 'chance': chance}]
    return pool


LOOT = {
    'meadow_deer': [entry('ecr:raw_venison', 1, 3, True), entry('minecraft:leather', 0, 2)],
    'highland_yak': [entry('ecr:raw_yak_meat', 2, 4, True), entry('minecraft:leather', 1, 3)],
    'wild_boar': [entry('minecraft:porkchop', 1, 3, True), entry('ecr:boar_tusk', 0, 2, looting=1), entry('minecraft:leather', 0, 1, chance=0.5)],
    'pheasant': [entry('ecr:raw_pheasant', 1, 1, True), entry('minecraft:feather', 0, 2)],
}

SPAWN = {
    'meadow_deer': dict(blocks=['minecraft:grass_block', 'minecraft:podzol'], weight=8, herd=(2, 4), tags=['forest', 'meadow', 'taiga', 'cherry_grove']),
    'highland_yak': dict(blocks=['minecraft:grass_block', 'minecraft:snow', 'minecraft:stone', 'minecraft:gravel'], weight=7, herd=(2, 3), tags=['extreme_hills', 'mountains']),
    'wild_boar': dict(blocks=['minecraft:grass_block', 'minecraft:podzol', 'minecraft:coarse_dirt'], weight=7, herd=(2, 4), tags=['forest', 'taiga', 'jungle']),
    'pheasant': dict(blocks=['minecraft:grass_block'], weight=9, herd=(1, 3), tags=['plains', 'forest', 'meadow', 'savanna']),
}


def spawn(name):
    s = SPAWN[name]
    return spawn_rule(f'{NS}:{name}', [{
        'minecraft:spawns_on_surface': {}, 'minecraft:spawns_on_block_filter': s['blocks'],
        'minecraft:brightness_filter': {'min': 7, 'max': 15, 'adjust_for_weather': False},
        'minecraft:weight': {'default': s['weight']}, 'minecraft:herd': {'min_size': s['herd'][0], 'max_size': s['herd'][1]},
        'minecraft:biome_filter': {'any_of': [{'test': 'has_biome_tag', 'operator': '==', 'value': t} for t in s['tags']]}}], 'animal')


# ----------------------------------------------------------------------------- build
def build():
    quad_anims = {}
    for name, a in ANIMALS.items():
        builder, mats, gid = mob_animals.MODELS[name]
        m = builder()
        m.pack()
        base, _ = m.paint(mats())
        save_png(base, f'{RP}/textures/entity/{name}.png')
        base.save(f'{PREVIEW}/{name}_final_tex.png')
        wjson(f'{RP}/models/entity/{name}.geo.json', m.export())
        wjson(f'{RP}/entity/{name}.entity.json', client(name, a))
        wjson(f'{BP}/entities/{name}.json', bp(name, a))
        wjson(f'{BP}/loot_tables/entities/{name}.json', {'pools': LOOT[name]})
        wjson(f'{BP}/spawn_rules/{name}.json', spawn(name))
        anims = anims2.bird(name) if a['kind'] == 'bird' else anims2.quad(
            name, amp=(30 if name == 'highland_yak' else 40), lower=(16 if name == 'highland_yak' else 32),
            bob=(0.5 if name == 'highland_yak' else 1.0), neck=('neck' if name == 'meadow_deer' else None))
        anims2.write(name, anims)
        LANG[f'entity.{NS}:{name}.name'] = a['title']
        LANG[f'item.spawn_egg.entity.{NS}:{name}.name'] = f'{a["title"]} Spawn Egg'
    wjson(f'{RP}/render_controllers/ecr_animals.render_controllers.json', render_controllers())


if __name__ == '__main__':
    build()
    print('animals ok')
