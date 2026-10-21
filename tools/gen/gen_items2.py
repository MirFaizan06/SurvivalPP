"""v1.2 items: mob drops, boss summon relics, boss trophies (crown / fang / heartwood core) + recipes + crown attachable."""
from common import *
from registry import *
from gen_items import write_item, shaped, shapeless, repairable, ENCH_SLOT
import math
import geo
import paint as P

CROWN_ID = 'geometry.ecr_hollow_crown'

# name: (title, stack, rarity, extra components, creative group)
DROPS = {
    'boar_tusk': ('Boar Tusk', 64, 'common', {}, None),
    'grave_dust': ('Grave Dust', 64, 'common', {}, None),
    'hollow_bone': ('Hollow Bone', 64, 'common', {}, None),
    'silk_gland': ('Silk Gland', 64, 'uncommon', {}, None),
    'spore_cluster': ('Spore Cluster', 64, 'common', {'minecraft:compostable': {'composting_chance': 85}}, None),
}
RELICS = {
    'grave_sigil': ('Grave Sigil', 16, 'rare', {'minecraft:glint': True}),
    'verdant_heart': ('Verdant Heart', 16, 'rare', {'minecraft:glint': True}),
    'silk_idol': ('Silk Idol', 16, 'rare', {'minecraft:glint': True}),
    'colossus_core': ('Heartwood Core', 16, 'epic', {'minecraft:glint': True}),
}


def crown_model():
    m = geo.Model(CROWN_ID, 64, 64, bounds=(1.0, 1.0, (0, 1.5, 0)))
    m.bone('head', None, (0, 24, 0))
    m.cube('head', (-4.6, 31.4, -4.6), (9.2, 2.2, 9.2), 'gold')
    m.cube('head', (-4.85, 31.0, -4.85), (9.7, 0.7, 9.7), 'trim')
    for i in range(8):
        ang = i * math.pi / 4
        x, z = math.cos(ang) * 3.9, math.sin(ang) * 3.9
        h = 3.2 if i % 2 == 0 else 2.0
        m.cube('head', (x - 0.8, 33.6, z - 0.8), (1.6, h, 1.6), 'gold')
        m.cube('head', (x - 0.45, 33.6 + h, z - 0.45), (0.9, 0.9, 0.9), 'gem' if i % 2 == 0 else 'bone')
    m.cube('head', (-0.9, 32.0, -4.95), (1.8, 1.4, 0.4), 'gem')
    return m


def crown_materials():
    gold = [hx(c) for c in ('#4a300a', '#7a5612', '#b98a1f', '#d9a830', '#f2c84c', '#ffe48a')]
    trim = [hx(c) for c in ('#1a1208', '#33260f', '#5a4218', '#7a5c26')]
    gem = [hx(c) for c in ('#0a4a2c', '#1f8a5a', '#4cf0a0', '#b6ffd8')]
    bone = [hx(c) for c in ('#8d866c', '#b8b094', '#e6dfc6', '#fbf7e4')]
    return {'gold': P.make(gold, scale=0.5, base=0.55, amp=0.4, bevel=0.15, seed=81),
            'trim': P.make(trim, scale=0.5, base=0.5, amp=0.3, bevel=0.1, seed=82),
            'gem': P.make(gem, scale=0.6, base=0.6, amp=0.35, bevel=0.2, seed=83),
            'bone': P.make(bone, scale=0.5, base=0.6, amp=0.3, bevel=0.2, seed=84)}


def build_crown_attachable():
    m = crown_model()
    m.pack()
    base, _ = m.paint(crown_materials())
    save_png(base, f'{RP}/textures/models/hollow_crown.png')
    wjson(f'{RP}/models/entity/hollow_crown.geo.json', m.export())
    common_ = {
        'materials': {'default': 'armor', 'enchanted': 'armor_enchanted'},
        'textures': {'default': 'textures/models/hollow_crown', 'enchanted': 'textures/misc/enchanted_actor_glint'},
        'geometry': {'default': CROWN_ID},
        'render_controllers': ['controller.render.armor'],
    }
    wjson(f'{RP}/attachables/hollow_crown.json', {'format_version': '1.8.0', 'minecraft:attachable': {'description': {
        'identifier': f'{NS}:hollow_crown', **common_}}})
    wjson(f'{RP}/attachables/hollow_crown.player.json', {'format_version': '1.10.0', 'minecraft:attachable': {'description': {
        'identifier': f'{NS}:hollow_crown.player', 'item': {f'{NS}:hollow_crown': "query.owner_identifier == 'minecraft:player'"}, **common_}}})


def build_items():
    for n, (title, stack, rar, extra, grp) in DROPS.items():
        comps = {'minecraft:icon': {'textures': {'default': itemtex(n)}}, 'minecraft:max_stack_size': stack, 'minecraft:rarity': {'value': rar}}
        comps.update(extra)
        write_item(n, comps, 'items')
        lang_item(n, title)
    for n, (title, stack, rar, extra) in RELICS.items():
        comps = {'minecraft:icon': {'textures': {'default': itemtex(n)}}, 'minecraft:max_stack_size': stack, 'minecraft:rarity': {'value': rar}}
        comps.update(extra)
        write_item(n, comps, 'items')
        lang_item(n, title)
    # Silkqueen's Fang: a venom dagger-sword
    n = 'queens_fang'
    comps = {
        'minecraft:icon': {'textures': {'default': itemtex(n)}}, 'minecraft:max_stack_size': 1, 'minecraft:hand_equipped': True,
        'minecraft:durability': {'max_durability': 1400}, 'minecraft:damage': {'value': 9},
        'minecraft:enchantable': {'slot': ENCH_SLOT['sword'], 'value': 18},
        'minecraft:repairable': repairable(n, f'{NS}:silk_gland'),
        'minecraft:digger': {'use_efficiency': True, 'destroy_speeds': [{'block': 'minecraft:web', 'speed': 15}]},
        'minecraft:can_destroy_in_creative': False,
        'minecraft:tags': {'tags': ['minecraft:is_sword', 'minecraft:is_tool']},
        'minecraft:rarity': {'value': 'epic'}}
    write_item(n, comps, 'equipment', 'minecraft:itemGroup.name.sword')
    lang_item(n, "Silkqueen's Fang")
    # Hollow Crown: wearable helmet-slot relic
    n = 'hollow_crown'
    comps = {
        'minecraft:icon': {'textures': {'default': itemtex(n)}}, 'minecraft:max_stack_size': 1,
        'minecraft:durability': {'max_durability': 480},
        'minecraft:wearable': {'slot': 'slot.armor.head', 'protection': 3},
        'minecraft:enchantable': {'slot': ENCH_SLOT['head'], 'value': 15},
        'minecraft:repairable': repairable(n, f'{NS}:hollow_bone'),
        'minecraft:tags': {'tags': ['minecraft:is_armor', f'{NS}:relic']},
        'minecraft:rarity': {'value': 'epic'}}
    write_item(n, comps, 'equipment', 'minecraft:itemGroup.name.helmet')
    lang_item(n, 'Hollow Crown')
    build_crown_attachable()


def build_recipes():
    n = lambda x: f'{NS}:{x}'
    shapeless('boar_tusk_to_bone_meal', [n('boar_tusk')], 'minecraft:bone_meal', 3)
    shapeless('grave_dust_to_bone_meal', [n('grave_dust')], 'minecraft:bone_meal', 1)
    shapeless('hollow_bone_to_bone_meal', [n('hollow_bone')], 'minecraft:bone_meal', 4)
    shapeless('spore_cluster_to_bone_meal', [n('spore_cluster')], 'minecraft:bone_meal', 2)
    shapeless('silk_gland_to_string', [n('silk_gland')], 'minecraft:string', 4)
    shaped('grave_sigil', ['BDB', 'DGD', 'BDB'], {'B': n('hollow_bone'), 'D': n('grave_dust'), 'G': 'minecraft:gold_block'}, n('grave_sigil'))
    shaped('verdant_heart', ['SMS', 'MEM', 'SMS'], {'S': n('spore_cluster'), 'M': 'minecraft:moss_block', 'E': 'minecraft:emerald_block'}, n('verdant_heart'))
    shaped('silk_idol', ['GWG', 'WDW', 'GWG'], {'G': n('silk_gland'), 'W': 'minecraft:web', 'D': 'minecraft:diamond'}, n('silk_idol'))


def build_all():
    build_items()
    build_recipes()
