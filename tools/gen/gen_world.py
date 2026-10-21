"""World generation: ore veins, geodes, Jacaranda trees, Pyre Spires, Eclipse Obelisks and Shrines."""
from common import *
import structures

FV = '1.21.130'
WOOD_NAMES = ['jacaranda', 'frostpine', 'amberwood', 'sunwood', 'mireweep']


def feature(name, kind, body, fv=None):
    wjson(f'{BP}/features/{name}.json', {'format_version': fv or FV, f'minecraft:{kind}': {'description': {'identifier': f'{NS}:{name}'}, **body}})


def rule(name, feature_name, pass_, biome, dist):
    wjson(f'{BP}/feature_rules/{name}.json', {'format_version': FV, 'minecraft:feature_rules': {
        'description': {'identifier': f'{NS}:{name}', 'places_feature': f'{NS}:{feature_name}'},
        'conditions': {'placement_pass': pass_, 'minecraft:biome_filter': biome},
        'distribution': dist}})


def tag(v):
    return {'test': 'has_biome_tag', 'operator': '==', 'value': v}


def chance(n, d):
    return {'numerator': n, 'denominator': d}


def rng(lo, hi):
    return {'distribution': 'uniform', 'extent': [lo, hi]}


def dist_underground(iterations, y0, y1, n=None, d=None):
    out = {'iterations': iterations, 'coordinate_eval_order': 'xzy', 'x': rng(0, 15), 'y': rng(y0, y1), 'z': rng(0, 15)}
    if n:
        out['scatter_chance'] = chance(n, d)
    return out


def dist_surface(iterations, n, d):
    return {'iterations': iterations, 'coordinate_eval_order': 'xzy', 'scatter_chance': chance(n, d),
            'x': rng(0, 15), 'z': rng(0, 15), 'y': 'q.heightmap(v.worldx, v.worldz)'}


GROW_ON = ['minecraft:dirt', 'minecraft:grass_block', 'minecraft:podzol', 'minecraft:coarse_dirt',
           'minecraft:dirt_with_roots', 'minecraft:moss_block', 'minecraft:mud']
REPLACE = ['minecraft:air', 'minecraft:short_grass', 'minecraft:tall_grass', 'minecraft:fern', 'minecraft:large_fern',
           'minecraft:sunflower', 'minecraft:lilac', 'minecraft:rose_bush', 'minecraft:peony', 'minecraft:snow_layer',
           'minecraft:oak_leaves', 'minecraft:birch_leaves', 'minecraft:spruce_leaves', 'minecraft:cherry_leaves', 'minecraft:acacia_leaves', 'minecraft:jungle_leaves'] + [f'{NS}:{w}_leaves' for w in WOOD_NAMES]
THROUGH = ['minecraft:dirt', 'minecraft:grass_block', 'minecraft:short_grass', 'minecraft:tall_grass', 'minecraft:fern', 'minecraft:large_fern',
           'minecraft:sunflower', 'minecraft:lilac', 'minecraft:rose_bush', 'minecraft:peony']
def LOGB(w):
    return {'name': f'{NS}:{w}_log', 'states': {'minecraft:block_face': 'up'}}


def LEAFB(w):
    return {'name': f'{NS}:{w}_leaves', 'states': {'ecr:persistent': 0}}


LOG = LOGB('jacaranda')
LEAF = LEAFB('jacaranda')


def tree_common():
    return {'base_block': ['minecraft:dirt'], 'may_grow_on': GROW_ON, 'may_replace': REPLACE, 'may_grow_through': THROUGH}


def ir(a, b):
    return {'range_min': a, 'range_max': b}


def build_overworld():
    feature('azurite_ore_feature', 'ore_feature', {
        'count': 6, 'discard_chance_on_air_exposure': 0.35,
        'replace_rules': [{'places_block': f'{NS}:azurite_ore', 'may_replace': ['minecraft:deepslate']}]})
    rule('azurite_ore_rule', 'azurite_ore_feature', 'underground_pass', tag('overworld'), dist_underground(3, -62, -8, 2, 3))
    feature('azurite_geode_feature', 'geode_feature', {
        'filler': 'minecraft:air', 'inner_layer': f'{NS}:azurite_block', 'alternate_inner_layer': f'{NS}:azurite_ore',
        'middle_layer': 'minecraft:calcite', 'outer_layer': 'minecraft:smooth_basalt',
        'min_outer_wall_distance': 4, 'max_outer_wall_distance': 7, 'min_distribution_points': 3, 'max_distribution_points': 5,
        'min_point_offset': 1, 'max_point_offset': 3, 'max_radius': 16, 'crack_point_offset': 2,
        'generate_crack_chance': 0.9, 'base_crack_size': 2.0, 'noise_multiplier': 0.025,
        'use_potential_placements_chance': 0.0, 'use_alternate_layer0_chance': 0.12, 'placements_require_layer0_alternate': False,
        'invalid_blocks_threshold': 1})
    rule('azurite_geode_rule', 'azurite_geode_feature', 'underground_pass', tag('overworld'), dist_underground(1, -54, 0, 1, 42))

    # --- Jacaranda trees (three silhouettes, weighted)
    cherry_branch = {'cherry_canopy': {'leaf_block': LEAF, 'height': ir(3, 4), 'radius': ir(3, 4),
                                       'wide_bottom_layer_hole_chance': chance(1, 4), 'corner_hole_chance': chance(2, 3),
                                       'hanging_leaves_chance': chance(1, 5), 'hanging_leaves_extension_chance': chance(1, 3)}}
    feature('jacaranda_weeping_tree_feature', 'tree_feature', {
        **tree_common(),
        'cherry_trunk': {'trunk_block': LOG, 'trunk_height': {'base': 5, 'intervals': [3]},
                         'branches': {'tree_type_weights': {'one_branch': 1, 'two_branches': 2, 'two_branches_and_trunk': 2},
                                      'branch_horizontal_length': ir(2, 4), 'branch_start_offset_from_top': ir(-4, -2),
                                      'branch_end_offset_from_top': ir(-1, 0), 'branch_canopy': cherry_branch}},
        'cherry_canopy': {'leaf_block': LEAF, 'height': ir(4, 5), 'radius': ir(4, 5),
                          'wide_bottom_layer_hole_chance': chance(1, 4), 'corner_hole_chance': chance(2, 3),
                          'hanging_leaves_chance': chance(1, 4), 'hanging_leaves_extension_chance': chance(1, 3)}})
    feature('jacaranda_round_tree_feature', 'tree_feature', {
        **tree_common(),
        'acacia_trunk': {'trunk_width': 1, 'trunk_height': {'base': 5, 'intervals': [3], 'min_height_for_canopy': 3},
                         'trunk_block': LOG,
                         'trunk_lean': {'allow_diagonal_growth': True, 'lean_height': ir(2, 3), 'lean_steps': ir(2, 4), 'lean_length': ir(1, 2)}},
        'random_spread_canopy': {'canopy_height': ir(2, 3), 'canopy_radius': ir(3, 4), 'leaf_placement_attempts': 70,
                                 'leaf_blocks': [[LEAF, 1]]}})
    feature('jacaranda_grand_tree_feature', 'tree_feature', {
        **tree_common(),
        'fancy_trunk': {'trunk_height': {'base': 9, 'variance': 6, 'scale': 0.8}, 'trunk_width': 1,
                        'branches': {'slope': 0.35, 'density': 1.0, 'min_altitude_factor': 0.55},
                        'trunk_block': LOG, 'width_scale': 1.0, 'foliage_altitude_factor': 0.6},
        'fancy_canopy': {'height': 4, 'radius': 5, 'leaf_block': LEAF}})
    feature('jacaranda_tree_feature', 'weighted_random_feature', {'features': [
        [f'{NS}:jacaranda_weeping_tree_feature', 5], [f'{NS}:jacaranda_round_tree_feature', 3], [f'{NS}:jacaranda_grand_tree_feature', 2]]})
    rule('jacaranda_plains_rule', 'jacaranda_tree_feature', 'surface_pass', tag('plains'), dist_surface(1, 1, 6))
    rule('jacaranda_forest_rule', 'jacaranda_tree_feature', 'surface_pass', tag('oak_forest'), dist_surface(1, 1, 3))
    rule('jacaranda_flower_forest_rule', 'jacaranda_tree_feature', 'surface_pass', tag('flower_forest'), dist_surface(2, 3, 4))
    rule('jacaranda_meadow_rule', 'jacaranda_tree_feature', 'surface_pass', tag('meadow'), dist_surface(1, 1, 4))


def species_trees():
    # ---------------------------------------------------------------- Frostpine (taiga / snowy biomes)
    w = 'frostpine'
    L, F = LOGB(w), LEAFB(w)
    feature('frostpine_spruce_tree_feature', 'tree_feature', {
        **tree_common(),
        'trunk': {'trunk_height': ir(7, 10), 'trunk_block': L},
        'spruce_canopy': {'lower_offset': ir(1, 2), 'upper_offset': ir(0, 1), 'max_radius': ir(2, 3), 'leaf_block': F}})
    feature('frostpine_tall_tree_feature', 'tree_feature', {
        **tree_common(),
        'trunk': {'trunk_height': ir(11, 15), 'trunk_block': L},
        'pine_canopy': {'canopy_height': ir(8, 10), 'base_radius': 3, 'leaf_block': F}})
    feature('frostpine_tree_feature', 'weighted_random_feature', {'features': [
        [f'{NS}:frostpine_spruce_tree_feature', 3], [f'{NS}:frostpine_tall_tree_feature', 2]]})
    rule('frostpine_taiga_rule', 'frostpine_tree_feature', 'surface_pass', tag('taiga'), dist_surface(2, 1, 2))
    rule('frostpine_ice_plains_rule', 'frostpine_tree_feature', 'surface_pass', tag('ice_plains'), dist_surface(1, 1, 6))
    rule('frostpine_grove_rule', 'frostpine_tree_feature', 'surface_pass', tag('grove'), dist_surface(2, 1, 3))
    rule('frostpine_slopes_rule', 'frostpine_tree_feature', 'surface_pass', tag('snowy_slopes'), dist_surface(1, 1, 6))

    # ---------------------------------------------------------------- Amberwood (autumn maple: birch / dark / oak forests)
    w = 'amberwood'
    L, F = LOGB(w), LEAFB(w)
    feature('amberwood_grand_tree_feature', 'tree_feature', {
        **tree_common(),
        'fancy_trunk': {'trunk_height': {'base': 8, 'variance': 5, 'scale': 0.8}, 'trunk_width': 1,
                        'branches': {'slope': 0.38, 'density': 1.0, 'min_altitude_factor': 0.5},
                        'trunk_block': L, 'width_scale': 1.1, 'foliage_altitude_factor': 0.6},
        'fancy_canopy': {'height': 4, 'radius': 5, 'leaf_block': F}})
    feature('amberwood_bushy_tree_feature', 'tree_feature', {
        **tree_common(),
        'trunk': {'trunk_height': ir(4, 6), 'trunk_block': L},
        'random_spread_canopy': {'canopy_height': ir(3, 4), 'canopy_radius': ir(2, 3), 'leaf_placement_attempts': 55, 'leaf_blocks': [[F, 1]]}})
    feature('amberwood_tree_feature', 'weighted_random_feature', {'features': [
        [f'{NS}:amberwood_grand_tree_feature', 2], [f'{NS}:amberwood_bushy_tree_feature', 3]]})
    rule('amberwood_birch_rule', 'amberwood_tree_feature', 'surface_pass', tag('birch'), dist_surface(1, 1, 2))
    rule('amberwood_roofed_rule', 'amberwood_tree_feature', 'surface_pass', tag('roofed'), dist_surface(2, 2, 3))
    rule('amberwood_oak_forest_rule', 'amberwood_tree_feature', 'surface_pass', tag('oak_forest'), dist_surface(1, 1, 4))

    # ---------------------------------------------------------------- Sunwood (golden acacia: savanna)
    w = 'sunwood'
    L, F = LOGB(w), LEAFB(w)
    lean = {'allow_diagonal_growth': True, 'lean_height': ir(2, 3), 'lean_steps': ir(2, 3), 'lean_length': ir(1, 2)}
    feature('sunwood_acacia_tree_feature', 'tree_feature', {
        **tree_common(),
        'acacia_trunk': {'trunk_width': 1, 'trunk_height': {'base': 5, 'intervals': [3], 'min_height_for_canopy': 3}, 'trunk_block': L, 'trunk_lean': lean},
        'acacia_canopy': {'canopy_size': 3, 'leaf_block': F, 'simplify_canopy': False}})
    feature('sunwood_umbrella_tree_feature', 'tree_feature', {
        **tree_common(),
        'acacia_trunk': {'trunk_width': 1, 'trunk_height': {'base': 6, 'intervals': [3], 'min_height_for_canopy': 4}, 'trunk_block': L, 'trunk_lean': lean},
        'random_spread_canopy': {'canopy_height': ir(1, 2), 'canopy_radius': ir(4, 5), 'leaf_placement_attempts': 80, 'leaf_blocks': [[F, 1]]}})
    feature('sunwood_tree_feature', 'weighted_random_feature', {'features': [
        [f'{NS}:sunwood_acacia_tree_feature', 3], [f'{NS}:sunwood_umbrella_tree_feature', 2]]})
    rule('sunwood_savanna_rule', 'sunwood_tree_feature', 'surface_pass', tag('savanna'), dist_surface(1, 1, 2))

    # ---------------------------------------------------------------- Mireweep (weeping willow: swamps / rivers)
    w = 'mireweep'
    L, F = LOGB(w), LEAFB(w)
    feature('mireweep_willow_tree_feature', 'tree_feature', {
        **tree_common(),
        'mangrove_trunk': {'trunk_width': 1, 'trunk_height': {'base': 5, 'height_rand_a': 2, 'height_rand_b': 3}, 'trunk_block': L,
                           'branches': {'branch_length': ir(1, 3), 'branch_steps': ir(1, 2), 'branch_chance': chance(1, 2)}},
        'mangrove_canopy': {'canopy_height': ir(3, 4), 'canopy_radius': ir(3, 4), 'leaf_placement_attempts': 75, 'leaf_blocks': [[F, 1]],
                            'hanging_block': F, 'hanging_block_placement_chance': chance(1, 3)}})
    feature('mireweep_drooping_tree_feature', 'tree_feature', {
        **tree_common(),
        'cherry_trunk': {'trunk_block': L, 'trunk_height': {'base': 5, 'intervals': [2]},
                         'branches': {'tree_type_weights': {'one_branch': 1, 'two_branches': 3, 'two_branches_and_trunk': 1},
                                      'branch_horizontal_length': ir(2, 3), 'branch_start_offset_from_top': ir(-3, -2), 'branch_end_offset_from_top': ir(-1, 0),
                                      'branch_canopy': {'cherry_canopy': {'leaf_block': F, 'height': ir(3, 4), 'radius': ir(3, 3),
                                                                           'wide_bottom_layer_hole_chance': chance(1, 3), 'corner_hole_chance': chance(2, 3),
                                                                           'hanging_leaves_chance': chance(2, 3), 'hanging_leaves_extension_chance': chance(2, 3)}}}},
        'cherry_canopy': {'leaf_block': F, 'height': ir(4, 5), 'radius': ir(4, 4),
                          'wide_bottom_layer_hole_chance': chance(1, 3), 'corner_hole_chance': chance(2, 3),
                          'hanging_leaves_chance': chance(2, 3), 'hanging_leaves_extension_chance': chance(2, 3)}})
    feature('mireweep_tree_feature', 'weighted_random_feature', {'features': [
        [f'{NS}:mireweep_willow_tree_feature', 3], [f'{NS}:mireweep_drooping_tree_feature', 2]]})
    rule('mireweep_swamp_rule', 'mireweep_tree_feature', 'surface_pass', tag('swamp'), dist_surface(2, 3, 4))
    rule('mireweep_mangrove_rule', 'mireweep_tree_feature', 'surface_pass', tag('mangrove_swamp'), dist_surface(1, 1, 3))
    rule('mireweep_river_rule', 'mireweep_tree_feature', 'surface_pass', tag('river'), dist_surface(1, 1, 6))



def anyof(*tags):
    return {'any_of': [tag(t) for t in tags]}


def stones_worldgen():
    """New natural stones spawn in blobs with normal stone, plus biome-flavoured boosts (caves, mountains, jungles...)."""
    from tex_stone import STONES
    for v, spec in STONES.items():
        g = spec['gen']
        feature(f'{v}_blob_feature', 'ore_feature', {
            'count': g['count'], 'discard_chance_on_air_exposure': 0.0,
            'replace_rules': [{'places_block': f'{NS}:{v}', 'may_replace': [f'minecraft:{r}' for r in g['rules']]}]})
        rule(f'{v}_rule', f'{v}_blob_feature', 'underground_pass', tag('overworld'),
             dist_underground(g['iters'], g['y'][0], g['y'][1], g['chance'][0], g['chance'][1]))
    # biome flavoured boosts
    rule('marlstone_dripstone_rule', 'marlstone_blob_feature', 'underground_pass', tag('dripstone_caves'), dist_underground(3, -32, 40))
    rule('slate_mountain_rule', 'slate_blob_feature', 'underground_pass', tag('mountains'), dist_underground(3, 40, 160))
    rule('verdite_lush_rule', 'verdite_blob_feature', 'underground_pass', anyof('lush_caves', 'jungle', 'swamp', 'mangrove_swamp'), dist_underground(3, -32, 48))
    rule('umbrastone_deep_rule', 'umbrastone_blob_feature', 'underground_pass', tag('deep_dark'), dist_underground(4, -64, 0))


WILD_BIOMES = {
    'tomato': [('plains', 1, 5), ('jungle', 1, 6)],
    'corn': [('savanna', 1, 4), ('plains', 1, 10)],
    'strawberry': [('oak_forest', 1, 4), ('birch', 1, 4), ('taiga', 1, 4), ('meadow', 1, 3), ('cherry_grove', 1, 3)],
    'chili': [('mesa', 1, 3), ('desert', 1, 8), ('savanna', 1, 8)],
    'oats': [('plains', 1, 6), ('meadow', 1, 4), ('taiga', 1, 10), ('extreme_hills', 1, 6)],
}


def crops_worldgen():
    """Wild crop patches so players can find seeds in the world."""
    for c, spots in WILD_BIOMES.items():
        feature(f'wild_{c}_feature', 'single_block_feature', {
            'places_block': [{'block': f'{NS}:wild_{c}', 'weight': 1}],
            'enforce_placement_rules': True, 'enforce_survivability_rules': True,
            'may_replace': ['minecraft:air', 'minecraft:short_grass']})
        feature(f'wild_{c}_patch_feature', 'scatter_feature', {
            'places_feature': f'{NS}:wild_{c}_feature', 'project_input_to_floor': True,
            'distribution': {'iterations': 6, 'coordinate_eval_order': 'xzy',
                             'x': {'distribution': 'uniform', 'extent': [-3, 3]}, 'y': 0, 'z': {'distribution': 'uniform', 'extent': [-3, 3]}}})
        for biome, n, d in spots:
            rule(f'wild_{c}_{biome}_rule', f'wild_{c}_patch_feature', 'surface_pass', tag(biome), dist_surface(1, n, d))


def build_nether():
    feature('pyrelite_ore_feature', 'ore_feature', {
        'count': 5, 'discard_chance_on_air_exposure': 0.25,
        'replace_rules': [{'places_block': f'{NS}:pyrelite_ore', 'may_replace': ['minecraft:netherrack', 'minecraft:basalt', 'minecraft:blackstone']}]})
    rule('pyrelite_ore_rule', 'pyrelite_ore_feature', 'underground_pass', tag('nether'), dist_underground(2, 6, 90, 1, 2))
    feature('pyrelite_geode_feature', 'geode_feature', {
        'filler': 'minecraft:lava', 'inner_layer': f'{NS}:pyrelite_block', 'alternate_inner_layer': f'{NS}:pyrelite_ore',
        'middle_layer': 'minecraft:basalt', 'outer_layer': 'minecraft:blackstone',
        'min_outer_wall_distance': 4, 'max_outer_wall_distance': 7, 'min_distribution_points': 3, 'max_distribution_points': 5,
        'min_point_offset': 1, 'max_point_offset': 3, 'max_radius': 14, 'crack_point_offset': 2,
        'generate_crack_chance': 0.6, 'base_crack_size': 1.5, 'noise_multiplier': 0.03,
        'use_potential_placements_chance': 0.0, 'use_alternate_layer0_chance': 0.2, 'placements_require_layer0_alternate': False,
        'invalid_blocks_threshold': 4})
    rule('pyrelite_geode_rule', 'pyrelite_geode_feature', 'underground_pass', tag('nether'), dist_underground(1, 20, 100, 1, 30))
    feature('pyre_spire_feature', 'structure_template_feature', {
        'structure_name': f'{NS}:pyre_spire', 'adjustment_radius': 4, 'facing_direction': 'random', 'rotate_around_center': True,
        'constraints': {'grounded': {}}})
    feature('pyre_spire_floor_feature', 'snap_to_surface_feature', {
        'feature_to_snap': f'{NS}:pyre_spire_feature', 'search_range': 14, 'surface': 'floor'}, fv='1.26.50')
    rule('pyre_spire_rule', 'pyre_spire_floor_feature', 'surface_pass', tag('nether'), dist_underground(1, 34, 96, 1, 5))


def build_end():
    feature('eclipsite_ore_feature', 'ore_feature', {
        'count': 5, 'discard_chance_on_air_exposure': 0.2,
        'replace_rules': [{'places_block': f'{NS}:eclipsite_ore', 'may_replace': ['minecraft:end_stone']}]})
    rule('eclipsite_ore_rule', 'eclipsite_ore_feature', 'underground_pass', tag('the_end'), dist_underground(3, 20, 80, 1, 2))
    feature('eclipse_obelisk_feature', 'structure_template_feature', {
        'structure_name': f'{NS}:eclipse_obelisk', 'adjustment_radius': 3, 'facing_direction': 'random', 'rotate_around_center': True,
        'constraints': {'grounded': {}, 'unburied': {}}})
    rule('eclipse_obelisk_rule', 'eclipse_obelisk_feature', 'surface_pass', tag('the_end'), dist_surface(1, 1, 10))
    feature('eclipse_shrine_feature', 'structure_template_feature', {
        'structure_name': f'{NS}:eclipse_shrine', 'adjustment_radius': 6, 'facing_direction': 'random', 'rotate_around_center': True,
        'ground_level': 5, 'constraints': {'leveled': {'max_steepness': 4}, 'unburied': {}}}, fv='1.26.30')
    rule('eclipse_shrine_rule', 'eclipse_shrine_feature', 'surface_pass', tag('the_end'), dist_surface(1, 1, 90))
    # shrine loot
    wjson(f'{BP}/loot_tables/chests/ecr_eclipse_shrine.json', {'pools': [
        {'rolls': {'min': 3, 'max': 5}, 'entries': [
            {'type': 'item', 'name': 'minecraft:ender_pearl', 'weight': 20, 'functions': [{'function': 'set_count', 'count': {'min': 2, 'max': 6}}]},
            {'type': 'item', 'name': 'minecraft:diamond', 'weight': 12, 'functions': [{'function': 'set_count', 'count': {'min': 1, 'max': 4}}]},
            {'type': 'item', 'name': f'{NS}:void_essence', 'weight': 10, 'functions': [{'function': 'set_count', 'count': {'min': 1, 'max': 3}}]},
            {'type': 'item', 'name': f'{NS}:raw_eclipsite', 'weight': 6, 'functions': [{'function': 'set_count', 'count': {'min': 1, 'max': 2}}]},
            {'type': 'item', 'name': 'minecraft:obsidian', 'weight': 14, 'functions': [{'function': 'set_count', 'count': {'min': 2, 'max': 8}}]},
            {'type': 'item', 'name': 'minecraft:golden_apple', 'weight': 6},
            {'type': 'item', 'name': 'minecraft:experience_bottle', 'weight': 10, 'functions': [{'function': 'set_count', 'count': {'min': 2, 'max': 6}}]},
            {'type': 'item', 'name': 'minecraft:netherite_scrap', 'weight': 4}]},
        {'rolls': 1, 'conditions': [{'condition': 'random_chance', 'chance': 0.2}], 'entries': [{'type': 'item', 'name': f'{NS}:eclipsite_ingot', 'weight': 1}]}]})


def build_all():
    structures.build_all()
    build_overworld()
    species_trees()
    stones_worldgen()
    crops_worldgen()
    build_nether()
    build_end()


if __name__ == '__main__':
    build_all()
    print('world ok')
