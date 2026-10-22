"""Items (tools, armour, materials, specials), attachables and recipes."""
from common import *
from registry import *

IV = '1.21.100'

MATS = {
    'azurite': dict(title='Azurite', tier='diamond', tools=1850, armor_factor=35, dmg=(8, 10, 6, 6, 1), speed=10, ench=16,
                    prot=(4, 8, 6, 3), rarity='uncommon', fire=False, handle='minecraft:stick'),
    'pyrelite': dict(title='Pyrelite', tier='netherite', tools=3600, armor_factor=52, dmg=(11, 14, 8, 9, 1), speed=14, ench=20,
                     prot=(4, 10, 7, 4), rarity='rare', fire=True, handle='minecraft:blaze_rod'),
    'eclipsite': dict(title='Eclipsite', tier='netherite', tools=8124, armor_factor=148, dmg=(32, 40, 24, 28, 4), speed=36, ench=30,
                      prot=(12, 32, 24, 12), rarity='epic', fire=True, handle='minecraft:end_rod'),
    # v1.6 alloys: no ore, made from a vanilla metal plus the drops of the Frozen Choir / the Fen (see gen_seals.py)
    'rimesteel': dict(title='Rimesteel', tier='iron', tools=1100, armor_factor=22, dmg=(7, 9, 5, 5, 1), speed=7, ench=14,
                      prot=(2, 6, 5, 2), rarity='uncommon', fire=False, handle='minecraft:stick', ore=False),
    'glacite': dict(title='Glacite', tier='diamond', tools=2600, armor_factor=42, dmg=(9, 11, 7, 7, 1), speed=11, ench=18,
                    prot=(4, 9, 7, 4), rarity='rare', fire=False, handle='minecraft:stick', ore=False),
    'wispsteel': dict(title='Wispsteel', tier='netherite', tools=4800, armor_factor=66, dmg=(13, 16, 9, 10, 1), speed=15, ench=22,
                      prot=(5, 11, 8, 5), rarity='epic', fire=True, handle='minecraft:breeze_rod', ore=False),
}
TOOL_KINDS = [('sword', 0, 'sword', 'Sword'), ('pickaxe', 2, 'pickaxe', 'Pickaxe'), ('axe', 1, 'axe', 'Axe'), ('shovel', 3, 'shovel', 'Shovel'), ('hoe', 4, 'hoe', 'Hoe')]
ARMOR_KINDS = [('helmet', 'head', 'helmet', 11, 'Helmet', 0), ('chestplate', 'chest', 'chestplate', 16, 'Chestplate', 1),
               ('leggings', 'legs', 'leggings', 15, 'Leggings', 2), ('boots', 'feet', 'boots', 13, 'Boots', 3)]
DESTRUCTIBLE = {'pickaxe': 'minecraft:is_pickaxe_item_destructible', 'axe': 'minecraft:is_axe_item_destructible',
                'shovel': 'minecraft:is_shovel_item_destructible', 'hoe': 'minecraft:is_hoe_item_destructible'}
ENCH_SLOT = {'sword': 'sword', 'pickaxe': 'pickaxe', 'axe': 'axe', 'shovel': 'shovel', 'hoe': 'hoe',
             'head': 'armor_head', 'chest': 'armor_torso', 'legs': 'armor_legs', 'feet': 'armor_feet'}


def write_item(name, comps, category, group=None):
    desc = {'identifier': f'{NS}:{name}', 'menu_category': {'category': category}}
    if group:
        desc['menu_category']['group'] = group
    wjson(f'{BP}/items/{name}.json', {'format_version': IV, 'minecraft:item': {'description': desc, 'components': comps}})
    ITEM_IDS.append(f'{NS}:{name}')


def repairable(name, ingot):
    return {'repair_items': [
        {'items': [f'{NS}:{name}'], 'repair_amount': 'context.other->query.remaining_durability + 0.12 * query.max_durability'},
        {'items': [ingot], 'repair_amount': 'query.max_durability * 0.25'}]}


def build_equipment():
    for mat, d in MATS.items():
        ingot = f'{NS}:{mat}_ingot'
        for kind, idx, grp, title in TOOL_KINDS:
            name = f'{mat}_{kind}'
            tex = itemtex(name)
            comps = {
                'minecraft:icon': {'textures': {'default': tex}},
                'minecraft:max_stack_size': 1,
                'minecraft:hand_equipped': True,
                'minecraft:durability': {'max_durability': d['tools']},
                'minecraft:damage': {'value': d['dmg'][idx]},
                'minecraft:enchantable': {'slot': ENCH_SLOT[kind], 'value': d['ench']},
                'minecraft:repairable': repairable(name, ingot),
                'minecraft:tags': {'tags': [f'minecraft:is_{kind}', 'minecraft:is_tool', f'minecraft:{d["tier"]}_tier', f'{NS}:{mat}_gear']},
                'minecraft:rarity': {'value': d['rarity']},
            }
            if kind == 'sword':
                comps['minecraft:digger'] = {'use_efficiency': True, 'destroy_speeds': [{'block': 'minecraft:web', 'speed': 15}]}
                comps['minecraft:can_destroy_in_creative'] = False
            else:
                comps['minecraft:digger'] = {'use_efficiency': True, 'destroy_speeds': [
                    {'block': {'tags': f"query.any_tag('{DESTRUCTIBLE[kind]}')"}, 'speed': d['speed']}]}
            if d['fire']:
                comps['minecraft:fire_resistant'] = {'value': True}
            write_item(name, comps, 'equipment', f'minecraft:itemGroup.name.{grp}')
            lang_item(name, f'{d["title"]} {title}')
        for kind, slot, grp, mult, title, i in ARMOR_KINDS:
            name = f'{mat}_{kind}'
            tex = itemtex(name)
            comps = {
                'minecraft:icon': {'textures': {'default': tex}},
                'minecraft:max_stack_size': 1,
                'minecraft:durability': {'max_durability': d['armor_factor'] * mult},
                'minecraft:wearable': {'slot': f'slot.armor.{slot}', 'protection': d['prot'][i]},
                'minecraft:enchantable': {'slot': ENCH_SLOT[slot], 'value': d['ench']},
                'minecraft:repairable': repairable(name, ingot),
                'minecraft:tags': {'tags': ['minecraft:is_armor', 'minecraft:trimmable_armors', f'minecraft:{d["tier"]}_tier', f'{NS}:{mat}_gear']},
                'minecraft:rarity': {'value': d['rarity']},
            }
            if d['fire']:
                comps['minecraft:fire_resistant'] = {'value': True}
            write_item(name, comps, 'equipment', f'minecraft:itemGroup.name.{grp}')
            lang_item(name, f'{d["title"]} {title}')
            attachable(name, mat, kind)
        # materials
        for nm, title, extra in ((f'{mat}_ingot', f'{d["title"]} Ingot', {}), (f'raw_{mat}', f'Raw {d["title"]}', {}))[:2 if d.get('ore', True) else 1]:
            comps = {'minecraft:icon': {'textures': {'default': itemtex(nm)}}, 'minecraft:max_stack_size': 64,
                     'minecraft:rarity': {'value': d['rarity']}}
            if d['fire']:
                comps['minecraft:fire_resistant'] = {'value': True}
            write_item(nm, comps, 'items')
            lang_item(nm, title)


def attachable(name, mat, kind):
    layer = 2 if kind == 'leggings' else 1
    geom = {'helmet': 'helmet', 'chestplate': 'chestplate', 'leggings': 'leggings', 'boots': 'boots'}[kind]
    var = {'helmet': 'helmet_layer_visible', 'chestplate': 'chest_layer_visible', 'leggings': 'leg_layer_visible', 'boots': 'boot_layer_visible'}[kind]
    tex = f'textures/models/armor/{mat}_{layer}'
    common = {
        'materials': {'default': 'armor', 'enchanted': 'armor_enchanted'},
        'textures': {'default': tex, 'enchanted': 'textures/misc/enchanted_actor_glint'},
        'render_controllers': ['controller.render.armor'],
    }
    wjson(f'{RP}/attachables/{name}.json', {'format_version': '1.8.0', 'minecraft:attachable': {'description': {
        'identifier': f'{NS}:{name}', **common, 'geometry': {'default': f'geometry.humanoid.armor.{geom}'},
        'scripts': {'parent_setup': f'variable.{var} = 0.0;'}}}})
    wjson(f'{RP}/attachables/{name}.player.json', {'format_version': '1.10.0', 'minecraft:attachable': {'description': {
        'identifier': f'{NS}:{name}.player', 'item': {f'{NS}:{name}': "query.owner_identifier == 'minecraft:player'"}, **common,
        'geometry': {'default': f'geometry.player.armor.{geom}'},
        'scripts': {'parent_setup': f'variable.{var} = 0.0;', 'animate': ['offset']},
        'animations': {'offset': f'animation.armor.{geom}.offset'}}}})


def build_specials():
    sp = {
        'ember_fang': ('Ember Fang', {'minecraft:fuel': {'duration': 60}}, 'uncommon'),
        'void_essence': ('Void Essence', {}, 'rare'),
        'eclipse_core': ('Eclipse Core', {'minecraft:glint': True}, 'epic'),
        'eclipse_sigil': ('Eclipse Sigil', {'minecraft:glint': True, 'minecraft:max_stack_size': 1}, 'epic'),
    }
    for n, (title, extra, rar) in sp.items():
        comps = {'minecraft:icon': {'textures': {'default': itemtex(n)}}, 'minecraft:max_stack_size': 64, 'minecraft:rarity': {'value': rar}}
        comps.update(extra)
        write_item(n, comps, 'items')
        lang_item(n, title)
    comps = {'minecraft:icon': {'textures': {'default': itemtex('sanctum_pass')}}, 'minecraft:max_stack_size': 16, 'minecraft:rarity': {'value': 'rare'}, 'minecraft:glint': True}
    write_item('sanctum_pass', comps, 'items')
    lang_item('sanctum_pass', 'Sanctum Pass')
    # block-placer items with proper sprites (one sapling + one door per tree species)
    from tex_wood import WOODS
    for w, spec in WOODS.items():
        T = spec['title']
        for n, title, grp, cat_, texsrc in (
                (f'{w}_sapling', f'{T} Sapling', 'minecraft:itemGroup.name.sapling', 'nature', f'{w}_sapling_icon'),
                (f'{w}_door', f'{T} Door', 'minecraft:itemGroup.name.door', 'construction', f'{w}_door_icon')):
            comps = {'minecraft:icon': {'textures': {'default': itemtex(n, texsrc)}}, 'minecraft:max_stack_size': 64,
                     'minecraft:block_placer': {'block': f'{NS}:{n}', 'replace_block_item': True}}
            if n.endswith('_sapling'):
                comps['minecraft:fuel'] = {'duration': 5}
                comps['minecraft:compostable'] = {'composting_chance': 30}
            write_item(n, comps, cat_, grp)
            lang_item(n, title)
    # wood blocks as block-placer items: burnable, tagged for vanilla recipes, with 3D icons
    from registry import WOOD_ITEMS
    for it in WOOD_ITEMS:
        n = it['name']
        title = LANG.get(f'tile.{NS}:{n}.name', n)
        comps = {'minecraft:icon': {'textures': {'default': itemtex(n, f'{n}_icon')}}, 'minecraft:max_stack_size': 64,
                 'minecraft:block_placer': {'block': f'{NS}:{n}', 'replace_block_item': True},
                 'minecraft:fuel': {'duration': it['fuel']}}
        if it['tags']:
            comps['minecraft:tags'] = {'tags': it['tags']}
        write_item(n, comps, it['category'], it['group'])
        lang_item(n, title)
    # spawn eggs / entity names
    LANG['entity.ecr:ashen_warg.name'] = 'Ashen Warg'
    LANG['entity.ecr:voidweaver.name'] = 'Voidweaver'
    LANG['entity.ecr:eclipse_sovereign.name'] = 'Eclipse Sovereign'
    LANG['item.spawn_egg.entity.ecr:ashen_warg.name'] = 'Ashen Warg Spawn Egg'
    LANG['item.spawn_egg.entity.ecr:voidweaver.name'] = 'Voidweaver Spawn Egg'
    LANG['item.spawn_egg.entity.ecr:eclipse_sovereign.name'] = 'Eclipse Sovereign Spawn Egg'
    LANG['entity.ecr:void_bolt.name'] = 'Void Bolt'
    LANG['entity.ecr:eclipse_orb.name'] = 'Eclipse Orb'
    LANG['entity.ecr:ember_spit.name'] = 'Ember Spit'


# ----------------------------------------------------------------------------- recipes
def rid(n):
    return f'{NS}:{n}'


UNLOCK = {'context': 'AlwaysUnlocked'}


def shaped(name, pattern, key, result, count=1):
    wjson(f'{BP}/recipes/{name}.json', {'format_version': '1.20.10', 'minecraft:recipe_shaped': {
        'description': {'identifier': rid(name)}, 'tags': ['crafting_table'], 'pattern': pattern,
        'key': {k: {'item': v} for k, v in key.items()}, 'unlock': UNLOCK, 'result': {'item': result, 'count': count}}})


def shapeless(name, ingredients, result, count=1):
    # A single-ingredient shapeless recipe is NOT offered by the 2x2 inventory grid on every client, vanilla writes these as
    # 1x1 shaped recipes (log -> planks), so we do the same.
    if len(ingredients) == 1:
        shaped(name, ['#'], {'#': ingredients[0]}, result, count)
        return
    wjson(f'{BP}/recipes/{name}.json', {'format_version': '1.20.10', 'minecraft:recipe_shapeless': {
        'description': {'identifier': rid(name)}, 'tags': ['crafting_table'],
        'ingredients': [{'item': i} for i in ingredients], 'unlock': UNLOCK, 'result': {'item': result, 'count': count}}})


def furnace(name, inp, out, tags):
    wjson(f'{BP}/recipes/{name}.json', {'format_version': '1.20.10', 'minecraft:recipe_furnace': {
        'description': {'identifier': rid(name)}, 'tags': tags, 'input': inp, 'output': out}})


PATTERNS = {
    'sword': (['#', '#', '/'], True), 'pickaxe': (['###', ' / ', ' / '], True), 'axe': (['##', '#/', ' /'], True),
    'shovel': (['#', '/', '/'], True), 'hoe': (['##', ' /', ' /'], True),
    'helmet': (['###', '# #'], False), 'chestplate': (['# #', '###', '###'], False),
    'leggings': (['###', '# #', '# #'], False), 'boots': (['# #', '# #'], False),
}


def wood_extras(w, P):
    """Everything vanilla wood can be crafted into, with explicit recipes for our planks/logs (like Mojang does for mangrove)."""
    n = lambda x: f'{NS}:{x}'
    slab = n(f'{w}_slab')
    shaped(f'{w}_crafting_table', ['##', '##'], {'#': P}, 'minecraft:crafting_table')
    shaped(f'{w}_chest', ['###', '# #', '###'], {'#': P}, 'minecraft:chest')
    shaped(f'{w}_barrel', ['#S#', '# #', '#S#'], {'#': P, 'S': slab}, 'minecraft:barrel')
    shaped(f'{w}_bowl', ['# #', ' # '], {'#': P}, 'minecraft:bowl', 4)
    shaped(f'{w}_bookshelf', ['###', 'BBB', '###'], {'#': P, 'B': 'minecraft:book'}, 'minecraft:bookshelf')
    shaped(f'{w}_wooden_pickaxe', ['###', ' / ', ' / '], {'#': P, '/': 'minecraft:stick'}, 'minecraft:wooden_pickaxe')
    shaped(f'{w}_wooden_axe', ['##', '#/', ' /'], {'#': P, '/': 'minecraft:stick'}, 'minecraft:wooden_axe')
    shaped(f'{w}_wooden_shovel', ['#', '/', '/'], {'#': P, '/': 'minecraft:stick'}, 'minecraft:wooden_shovel')
    shaped(f'{w}_wooden_hoe', ['##', ' /', ' /'], {'#': P, '/': 'minecraft:stick'}, 'minecraft:wooden_hoe')
    shaped(f'{w}_wooden_sword', ['#', '#', '/'], {'#': P, '/': 'minecraft:stick'}, 'minecraft:wooden_sword')
    shaped(f'{w}_jukebox', ['###', '#D#', '###'], {'#': P, 'D': 'minecraft:diamond'}, 'minecraft:jukebox')
    shaped(f'{w}_note_block', ['###', '#R#', '###'], {'#': P, 'R': 'minecraft:redstone'}, 'minecraft:noteblock')
    shaped(f'{w}_composter', ['# #', '# #', '###'], {'#': slab}, 'minecraft:composter')
    shaped(f'{w}_lectern', ['SSS', ' B ', ' S '], {'S': slab, 'B': 'minecraft:bookshelf'}, 'minecraft:lectern')
    shaped(f'{w}_grindstone', ['/S/', '# #'], {'/': 'minecraft:stick', 'S': 'minecraft:normal_stone_slab', '#': P}, 'minecraft:grindstone')
    shaped(f'{w}_loom', ['SS', '##'], {'S': 'minecraft:string', '#': P}, 'minecraft:loom')
    shaped(f'{w}_cartography_table', ['PP', '##', '##'], {'P': 'minecraft:paper', '#': P}, 'minecraft:cartography_table')
    shaped(f'{w}_fletching_table', ['FF', '##', '##'], {'F': 'minecraft:flint', '#': P}, 'minecraft:fletching_table')
    shaped(f'{w}_smithing_table', ['II', '##', '##'], {'I': 'minecraft:iron_ingot', '#': P}, 'minecraft:smithing_table')
    shaped(f'{w}_tripwire_hook', ['I', '/', '#'], {'I': 'minecraft:iron_ingot', '/': 'minecraft:stick', '#': P}, 'minecraft:tripwire_hook', 2)
    for log in (f'{w}_log', f'{w}_wood', f'stripped_{w}_log', f'stripped_{w}_wood'):
        furnace(f'{w}_charcoal_from_{log}', n(log), 'minecraft:charcoal', ['furnace'])
        for fuel in ('coal', 'charcoal'):
            if log in (f'{w}_log', f'stripped_{w}_log'):
                shaped(f'{w}_campfire_{fuel}_{log}', [' / ', '/C/', 'LLL'], {'/': 'minecraft:stick', 'C': f'minecraft:{fuel}', 'L': n(log)}, 'minecraft:campfire')


def build_recipes():
    for mat, d in MATS.items():
        ing = f'{NS}:{mat}_ingot'
        for kind, (pat, handle) in PATTERNS.items():
            key = {'#': ing}
            if handle:
                key['/'] = d['handle']
            shaped(f'{mat}_{kind}', pat, key, f'{NS}:{mat}_{kind}')
        if not d.get('ore', True):
            continue
        shaped(f'{mat}_block', ['###', '###', '###'], {'#': ing}, f'{NS}:{mat}_block')
        shapeless(f'{mat}_ingot_from_block', [f'{NS}:{mat}_block'], ing, 9)
        furnace(f'{mat}_ingot_from_raw', f'{NS}:raw_{mat}', ing, ['furnace'])
        furnace(f'{mat}_ingot_from_raw_blasting', f'{NS}:raw_{mat}', ing, ['blast_furnace'])
        furnace(f'{mat}_ingot_from_ore', f'{NS}:{mat}_ore', ing, ['furnace'])
        furnace(f'{mat}_ingot_from_ore_blasting', f'{NS}:{mat}_ore', ing, ['blast_furnace'])
    # specials
    shaped('eclipse_sigil', ['VPV', 'PNP', 'VPV'], {'V': f'{NS}:void_essence', 'P': f'{NS}:pyrelite_ingot', 'N': 'minecraft:nether_star'}, f'{NS}:eclipse_sigil')
    shaped('eclipse_altar', ['OEO', 'ECE', 'OOO'], {'O': 'minecraft:obsidian', 'E': f'{NS}:eclipsite_ingot', 'C': 'minecraft:crying_obsidian'}, f'{NS}:eclipse_altar')
    shaped('stasis_chamber', ['IGI', 'GEG', 'IGI'], {'I': 'minecraft:iron_ingot', 'G': 'minecraft:glass', 'E': 'minecraft:ender_eye'}, f'{NS}:stasis_chamber')
    shapeless('stasis_plate', ['minecraft:ender_eye', 'minecraft:stone_pressure_plate', 'minecraft:redstone'], f'{NS}:stasis_plate')
    # deliberately brutal: needs the Eclipse Sovereign's Eclipse Core, a Totem of Undying, netherite and eclipsite
    shaped('sanctum_warden', ['NEN', 'OCO', 'RTR'], {'N': 'minecraft:netherite_ingot', 'E': f'{NS}:eclipsite_ingot', 'O': 'minecraft:obsidian',
                                                    'C': f'{NS}:eclipse_core', 'R': f'{NS}:pyrelite_ingot', 'T': 'minecraft:totem_of_undying'}, f'{NS}:sanctum_warden')
    shapeless('sanctum_pass', ['minecraft:paper', f'{NS}:azurite_ingot', 'minecraft:ender_pearl'], f'{NS}:sanctum_pass')
    # wood sets
    from tex_wood import WOODS
    for w in WOODS:
        P = f'{NS}:{w}_planks'
        for log in (f'{w}_log', f'{w}_wood', f'stripped_{w}_log', f'stripped_{w}_wood'):
            shapeless(f'{w}_planks_from_{log}', [f'{NS}:{log}'], P, 4)
        shaped(f'{w}_wood', ['##', '##'], {'#': f'{NS}:{w}_log'}, f'{NS}:{w}_wood', 3)
        shaped(f'stripped_{w}_wood', ['##', '##'], {'#': f'{NS}:stripped_{w}_log'}, f'{NS}:stripped_{w}_wood', 3)
        shaped(f'{w}_stick', ['#', '#'], {'#': P}, 'minecraft:stick', 4)
        shaped(f'{w}_slab', ['###'], {'#': P}, f'{NS}:{w}_slab', 6)
        shaped(f'{w}_stairs', ['#  ', '## ', '###'], {'#': P}, f'{NS}:{w}_stairs', 4)
        shaped(f'{w}_fence', ['#/#', '#/#'], {'#': P, '/': 'minecraft:stick'}, f'{NS}:{w}_fence', 3)
        shaped(f'{w}_fence_gate', ['/#/', '/#/'], {'#': P, '/': 'minecraft:stick'}, f'{NS}:{w}_fence_gate')
        shaped(f'{w}_door', ['##', '##', '##'], {'#': P}, f'{NS}:{w}_door', 3)
        shaped(f'{w}_trapdoor', ['###', '###'], {'#': P}, f'{NS}:{w}_trapdoor', 2)
        shaped(f'{w}_pressure_plate', ['##'], {'#': P}, f'{NS}:{w}_pressure_plate')
        shapeless(f'{w}_button', [P], f'{NS}:{w}_button')
        wood_extras(w, P)


def build_all():
    build_equipment()
    build_specials()
    build_recipes()
    import gen_stone
    gen_stone.build_recipes()


if __name__ == '__main__':
    build_all()
    print(len(ITEM_IDS), 'items')
