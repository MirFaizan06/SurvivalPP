"""v1.2 world generation: Forgotten Graveyards, Verdant Shrines, Silk Nests, Hunter's Camps, Mossy Boulders + their chest loot."""
from common import *
import structures2
from gen_world import feature, rule, tag, anyof, dist_surface, dist_underground


def item(name, weight, lo=None, hi=None):
    e = {'type': 'item', 'name': name, 'weight': weight}
    if lo is not None:
        e['functions'] = [{'function': 'set_count', 'count': {'min': lo, 'max': hi if hi is not None else lo}}]
    return e


def chest_loot(name, entries, rolls=(3, 6), rare=None):
    pools = [{'rolls': {'min': rolls[0], 'max': rolls[1]}, 'entries': entries}]
    if rare:
        pools.append({'rolls': 1, 'conditions': [{'condition': 'random_chance', 'chance': rare[1]}], 'entries': [item(rare[0], 1)]})
    wjson(f'{BP}/loot_tables/chests/{name}.json', {'pools': pools})


def loot():
    chest_loot('ecr_graveyard', [
        item('minecraft:bone', 24, 2, 8), item('minecraft:rotten_flesh', 14, 2, 6), item(f'{NS}:grave_dust', 16, 1, 4), item(f'{NS}:hollow_bone', 12, 1, 3),
        item('minecraft:iron_ingot', 10, 1, 3), item('minecraft:gold_ingot', 8, 1, 3), item('minecraft:emerald', 6, 1, 3), item('minecraft:name_tag', 6),
        item('minecraft:golden_apple', 3), item('minecraft:soul_lantern', 6, 1, 2), item('minecraft:book', 8, 1, 2), item('minecraft:saddle', 4)],
        rare=(f'{NS}:grave_sigil', 0.12))
    chest_loot('ecr_verdant_shrine', [
        item(f'{NS}:spore_cluster', 16, 1, 4), item('minecraft:moss_block', 14, 2, 8), item('minecraft:glow_berries', 10, 2, 6), item('minecraft:bone_meal', 16, 3, 10),
        item(f'{NS}:strawberry_seeds', 8, 1, 3), item(f'{NS}:oat_seeds', 8, 1, 3), item(f'{NS}:tomato_seeds', 8, 1, 3), item('minecraft:flowering_azalea', 6, 1, 2),
        item('minecraft:emerald', 6, 1, 3), item('minecraft:golden_apple', 3), item('minecraft:experience_bottle', 8, 1, 4)],
        rare=(f'{NS}:verdant_heart', 0.12))
    chest_loot('ecr_silk_nest', [
        item('minecraft:string', 26, 3, 10), item(f'{NS}:silk_gland', 12, 1, 3), item('minecraft:spider_eye', 14, 1, 4), item('minecraft:web', 10, 1, 3),
        item('minecraft:diamond', 5, 1, 2), item('minecraft:iron_ingot', 10, 1, 4), item('minecraft:ender_pearl', 6, 1, 2), item('minecraft:experience_bottle', 8, 1, 3)],
        rare=(f'{NS}:silk_idol', 0.12))
    chest_loot('ecr_hunters_camp', [
        item(f'{NS}:raw_venison', 14, 1, 4), item(f'{NS}:cooked_venison', 10, 1, 3), item(f'{NS}:raw_yak_meat', 8, 1, 3), item(f'{NS}:cooked_pheasant', 8, 1, 3),
        item('minecraft:leather', 12, 1, 4), item('minecraft:arrow', 16, 4, 16), item('minecraft:feather', 12, 2, 8), item('minecraft:bow', 4),
        item(f'{NS}:hunters_stew', 5), item(f'{NS}:oat_bread', 8, 1, 4), item(f'{NS}:corn_kernels', 6, 1, 3), item(f'{NS}:boar_tusk', 6, 1, 2), item('minecraft:string', 8, 1, 4)],
        rolls=(3, 5))


def structure(name, struct, base, forest, n, d, adj=5, steep=4):
    feature(f'{name}_feature', 'structure_template_feature', {
        'structure_name': f'{NS}:{struct}', 'adjustment_radius': adj, 'facing_direction': 'random', 'rotate_around_center': True,
        'ground_level': base, 'constraints': {'leveled': {'max_steepness': steep}, 'unburied': {}}}, fv='1.26.30')
    rule(f'{name}_rule', f'{name}_feature', 'surface_pass', anyof(*forest), dist_surface(1, n, d))


def build_all():
    sizes = structures2.build_all()
    structure('forgotten_graveyard', 'forgotten_graveyard', sizes['graveyard'][1], ['forest', 'plains', 'taiga', 'swamp'], 1, 170, steep=5)
    structure('verdant_shrine', 'verdant_shrine', sizes['verdant_shrine'][1], ['forest', 'taiga', 'jungle', 'meadow'], 1, 190, adj=4)
    structure('hunters_camp', 'hunters_camp', sizes['hunters_camp'][1], ['forest', 'taiga', 'plains', 'meadow'], 1, 100, adj=4, steep=3)
    structure('mossy_boulder', 'mossy_boulder', sizes['boulder'][1], ['forest', 'taiga', 'extreme_hills', 'mountains'], 1, 14, adj=3, steep=3)
    # silk nests: sealed pockets hidden in solid rock, found by mining or by their stray webs
    feature('silk_nest_feature', 'structure_template_feature', {
        'structure_name': f'{NS}:silk_nest', 'adjustment_radius': 3, 'facing_direction': 'random', 'rotate_around_center': True, 'constraints': {}})
    rule('silk_nest_rule', 'silk_nest_feature', 'underground_pass', tag('overworld'), dist_underground(1, 5, 38, 1, 70))
    loot()


if __name__ == '__main__':
    build_all()
    print('world2 ok')
