"""v1.3 adventure structures: world-gen rules (rarity, biomes, placement) and tiered chest loot for the ten new structures."""
from common import *
import structures3, structures4
from gen_world import feature, rule, tag, anyof, dist_surface, dist_underground
from gen_world2 import item

N = NS


# ----------------------------------------------------------------------------- loot
def ench(name, weight, lo=None, hi=None, levels=(15, 30)):
    e = item(name, weight, lo, hi)
    e.setdefault('functions', []).append({'function': 'enchant_with_levels', 'levels': {'min': levels[0], 'max': levels[1]}, 'treasure': False})
    return e


def book(weight):
    e = item('minecraft:book', weight)
    e['functions'] = [{'function': 'enchant_randomly'}]
    return e


COMMON = [
    item('minecraft:bread', 14, 2, 6), item('minecraft:apple', 10, 1, 4), item('minecraft:coal', 14, 3, 9), item('minecraft:arrow', 14, 5, 16),
    item('minecraft:bone', 10, 2, 6), item('minecraft:string', 10, 2, 6), item('minecraft:leather', 8, 1, 4), item('minecraft:torch', 10, 4, 12),
    item('minecraft:gold_nugget', 8, 3, 9), item(f'{N}:oat_bread', 6, 1, 3), item(f'{N}:cooked_venison', 6, 1, 3), item(f'{N}:tomato_seeds', 4, 1, 3),
    item('minecraft:bone_meal', 8, 2, 6), item('minecraft:iron_nugget', 10, 3, 9),
]
T1 = COMMON + [item('minecraft:iron_ingot', 10, 1, 3), item('minecraft:gold_ingot', 4, 1, 2), item('minecraft:saddle', 2), item('minecraft:golden_apple', 1)]
T2 = COMMON + [item('minecraft:iron_ingot', 14, 2, 6), item('minecraft:gold_ingot', 10, 2, 5), item('minecraft:redstone', 10, 4, 10), item('minecraft:lapis_lazuli', 8, 3, 8),
               item('minecraft:emerald', 8, 1, 3), book(8), item('minecraft:golden_apple', 3), item('minecraft:name_tag', 4), item('minecraft:saddle', 4),
               item('minecraft:experience_bottle', 6, 1, 3), item(f'{N}:raw_azurite', 2, 1, 2)]
T3 = [item('minecraft:iron_ingot', 14, 3, 8), item('minecraft:gold_ingot', 12, 3, 7), item('minecraft:diamond', 10, 1, 3), item('minecraft:emerald', 12, 2, 6),
      book(14), item('minecraft:golden_apple', 6, 1, 2), item('minecraft:ender_pearl', 6, 1, 3), item('minecraft:experience_bottle', 10, 2, 6),
      ench('minecraft:iron_sword', 4), ench('minecraft:iron_pickaxe', 4), ench('minecraft:diamond_chestplate', 2, levels=(18, 32)), item('minecraft:name_tag', 4),
      item(f'{N}:raw_azurite', 5, 1, 4), item(f'{N}:azurite_ingot', 2, 1, 2), item('minecraft:saddle', 4), item(f'{N}:hunters_stew', 4, 1, 2), item('minecraft:obsidian', 6, 2, 6)]
T4 = [item('minecraft:diamond', 14, 2, 6), item('minecraft:emerald', 12, 3, 8), item('minecraft:gold_ingot', 12, 4, 10), book(16), book(10),
      item('minecraft:golden_apple', 8, 1, 3), item('minecraft:enchanted_golden_apple', 2), item('minecraft:netherite_scrap', 5, 1, 2), item('minecraft:ender_pearl', 6, 2, 4),
      ench('minecraft:diamond_sword', 5, levels=(22, 38)), ench('minecraft:diamond_pickaxe', 4, levels=(22, 38)), ench('minecraft:diamond_chestplate', 4, levels=(22, 38)),
      ench('minecraft:diamond_helmet', 3, levels=(22, 38)), ench('minecraft:bow', 4, levels=(20, 35)), item(f'{N}:azurite_ingot', 8, 1, 4), item(f'{N}:raw_pyrelite', 4, 1, 2),
      item('minecraft:experience_bottle', 10, 3, 8), item('minecraft:totem_of_undying', 1), item(f'{N}:hollow_bone', 6, 1, 3), item(f'{N}:silk_gland', 4, 1, 2)]
T5 = [item('minecraft:diamond', 12, 4, 10), item('minecraft:netherite_scrap', 10, 1, 3), item('minecraft:netherite_ingot', 3, 1, 2), item('minecraft:enchanted_golden_apple', 6, 1, 2),
      book(14), book(12), item('minecraft:totem_of_undying', 4), ench('minecraft:diamond_sword', 4, levels=(28, 40)), ench('minecraft:netherite_pickaxe', 2, levels=(26, 40)),
      ench('minecraft:netherite_chestplate', 2, levels=(26, 40)), item(f'{N}:azurite_ingot', 10, 2, 6), item(f'{N}:pyrelite_ingot', 6, 1, 3), item(f'{N}:raw_eclipsite', 4, 1, 2),
      item(f'{N}:eclipsite_ingot', 1, 1, 1), item('minecraft:experience_bottle', 10, 4, 10), item('minecraft:ender_pearl', 6, 2, 5), item('minecraft:elytra', 1)]
NETHER = [item('minecraft:gold_ingot', 14, 3, 9), item('minecraft:netherite_scrap', 8, 1, 3), item('minecraft:ancient_debris', 6, 1, 2), item(f'{N}:raw_pyrelite', 10, 1, 4),
          item(f'{N}:pyrelite_ingot', 5, 1, 2), item('minecraft:blaze_rod', 8, 2, 5), item('minecraft:diamond', 8, 2, 5), item('minecraft:obsidian', 8, 3, 8),
          item('minecraft:magma_cream', 8, 2, 6), item('minecraft:golden_apple', 5, 1, 2), book(10), ench('minecraft:golden_sword', 4, levels=(20, 34)),
          ench('minecraft:diamond_pickaxe', 3, levels=(24, 38)), item('minecraft:totem_of_undying', 2), item(f'{N}:ember_fang', 8, 1, 3)]
END = [item('minecraft:ender_pearl', 14, 3, 8), item('minecraft:diamond', 10, 3, 8), item('minecraft:netherite_ingot', 5, 1, 2), item(f'{N}:void_essence', 12, 1, 4),
       item(f'{N}:raw_eclipsite', 8, 1, 3), item(f'{N}:eclipsite_ingot', 3, 1, 2), book(12), item('minecraft:enchanted_golden_apple', 5, 1, 2),
       item('minecraft:totem_of_undying', 4), item('minecraft:elytra', 2), item('minecraft:shulker_shell', 6, 1, 3), item('minecraft:end_rod', 8, 3, 10),
       ench('minecraft:netherite_sword', 2, levels=(28, 40)), item(f'{N}:eclipse_sigil', 1), item('minecraft:experience_bottle', 10, 4, 10)]

# table name -> (entries, rolls, rare relic or None)
TABLES = {
    'ecr_bandit_camp': (T1, (2, 3), None),
    'ecr_bandit_lookout': (T1, (4, 6), (f'{N}:grave_sigil', 0.03)),
    'ecr_sunken_well': (T1, (3, 5), None),
    'ecr_sunken_well_hidden': (T2, (4, 6), (f'{N}:silk_idol', 0.06)),
    'ecr_watch_keep_tower': (T2, (3, 5), None),
    'ecr_watch_keep_keep': (T2, (4, 7), (f'{N}:grave_sigil', 0.08)),
    'ecr_dune_vault_hall': (T2, (3, 5), None),
    'ecr_dune_vault': (T3, (4, 6), (f'{N}:silk_idol', 0.08)),
    'ecr_thorn_shrine': (T3, (4, 6), (f'{N}:verdant_heart', 0.1)),
    'ecr_frost_cairn': (T3, (4, 6), (f'{N}:grave_sigil', 0.08)),
    'ecr_highland_bastion_tower': (T3, (3, 5), None),
    'ecr_highland_bastion': (T4, (5, 8), (f'{N}:verdant_heart', 0.12)),
    'ecr_highland_bastion_vault': (T5, (6, 9), (f'{N}:silk_idol', 0.2)),
    'ecr_sunken_crypt': (T4, (5, 8), (f'{N}:grave_sigil', 0.15)),
    'ecr_sunken_crypt_hidden': (T4, (4, 6), (f'{N}:silk_idol', 0.15)),
    'ecr_sunken_crypt_vault': (T5, (6, 9), (f'{N}:grave_sigil', 0.25)),
    'ecr_pyre_bastion': (NETHER, (5, 8), None),
    'ecr_pyre_bastion_core': (NETHER + T5[:6], (7, 10), (f'{N}:eclipse_sigil', 0.1)),
    'ecr_eclipse_vault': (END, (5, 8), None),
    'ecr_eclipse_vault_core': (END + T5[:6], (8, 11), (f'{N}:eclipse_sigil', 0.3)),
}


def loot():
    for name, (entries, rolls, rare) in TABLES.items():
        pools = [{'rolls': {'min': rolls[0], 'max': rolls[1]}, 'entries': entries}]
        if rare:
            pools.append({'rolls': 1, 'conditions': [{'condition': 'random_chance', 'chance': rare[1]}], 'entries': [item(rare[0], 1)]})
        wjson(f'{BP}/loot_tables/chests/{name}.json', {'pools': pools})


# ----------------------------------------------------------------------------- placement
def structure(name, struct, base, biome, n, d, adj=6, steep=4, pass_='surface_pass', dist=None, constraints=None):
    feature(f'{name}_feature', 'structure_template_feature', {
        'structure_name': f'{NS}:{struct}', 'adjustment_radius': adj, 'facing_direction': 'random', 'rotate_around_center': True,
        'ground_level': base, 'constraints': constraints or {'leveled': {'max_steepness': steep}, 'unburied': {}}}, fv='1.26.30')
    rule(f'{name}_rule', f'{name}_feature', pass_, biome, dist or dist_surface(1, n, d))


def build_all():
    s = {}
    s.update(structures3.build_all())
    s.update(structures4.build_all())
    base = lambda k: s[k][1]
    # --- Overworld (rarity is per 16x16 chunk: 1/N; bigger = rarer). Easy ones are common, hard ones rare like mansions/outposts.
    structure('bandit_lookout', 'bandit_lookout', base('bandit_lookout'), anyof('plains', 'savanna', 'forest', 'meadow', 'taiga'), 1, 140, adj=5)
    structure('sunken_well', 'sunken_well', base('sunken_well'), anyof('plains', 'savanna', 'desert', 'forest', 'taiga', 'meadow'), 1, 150, adj=5, steep=3)
    structure('watch_keep', 'watch_keep', base('watch_keep'), anyof('plains', 'forest', 'taiga', 'swamp', 'savanna'), 1, 230, adj=8, steep=4)
    structure('dune_vault', 'dune_vault', base('dune_vault'), anyof('desert', 'mesa'), 1, 220, adj=8, steep=5)
    structure('thorn_shrine', 'thorn_shrine', base('thorn_shrine'), anyof('jungle', 'swamp', 'mangrove_swamp'), 1, 210, adj=8, steep=5)
    structure('frost_cairn', 'frost_cairn', base('frost_cairn'), anyof('frozen', 'ice', 'cold'), 1, 200, adj=7, steep=4)
    structure('highland_bastion', 'highland_bastion', base('highland_bastion'), anyof('extreme_hills', 'mountains'), 1, 380, adj=12, steep=7)
    # sunken crypts are buried: placed in the underground pass anywhere in the overworld, deep enough not to breach daylight
    feature('sunken_crypt_feature', 'structure_template_feature', {
        'structure_name': f'{NS}:sunken_crypt', 'adjustment_radius': 4, 'facing_direction': 'random', 'rotate_around_center': True})
    rule('sunken_crypt_rule', 'sunken_crypt_feature', 'underground_pass', tag('overworld'), dist_underground(1, -48, 20, 1, 420))
    # --- Nether: same snap-to-floor scheme the Pyre Spires use
    feature('pyre_bastion_feature', 'structure_template_feature', {
        'structure_name': f'{NS}:pyre_bastion', 'adjustment_radius': 8, 'facing_direction': 'random', 'rotate_around_center': True,
        'ground_level': base('pyre_bastion'), 'constraints': {'grounded': {}}}, fv='1.26.30')
    feature('pyre_bastion_floor_feature', 'snap_to_surface_feature', {
        'feature_to_snap': f'{NS}:pyre_bastion_feature', 'search_range': 20, 'surface': 'floor'}, fv='1.26.50')
    rule('pyre_bastion_rule', 'pyre_bastion_floor_feature', 'surface_pass', tag('nether'), dist_underground(1, 34, 90, 1, 70))
    # --- End
    structure('eclipse_vault', 'eclipse_vault', base('eclipse_vault'), tag('the_end'), 1, 130, adj=8, steep=6)
    loot()
    return s


if __name__ == '__main__':
    print(build_all())
