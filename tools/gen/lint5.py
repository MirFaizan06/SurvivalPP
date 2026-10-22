"""Lint part 5 ("content-log regressions"): every class of error that Minecraft's own Content Log has reported against this pack, checked offline.
 - entity component members that are not in the official schema (e.g. hurt_by_target.alert_same_type stopped five mobs from loading)
 - interact.play_sounds must be an array, no item data suffixes ("bucket:1") in transform_to_item / has_equipment
 - blocks: Molang conditions without `%`, redstone_producer in permutations needs a base component; the multi_block trait needs minecraft:movable; block_placer / blocks.json refs exist
 - features: structure_template_feature needs `constraints`, cherry canopy heights >= 4, scatter_chance numerator < denominator
 - recipes: every shaped / shapeless recipe needs `unlock`; every recipe result item exists
Run via `python tools/dev.py lint`."""
import glob, json, os, re, sys
from common import *

problems = []


def bad(m):
    problems.append(m)
    print('  X', m)


def jl(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


SCHEMA_ROOT = f'{BEDROCK_SAMPLES}/metadata/json_schemas/server/entity'
VERSIONS = sorted([d for d in os.listdir(SCHEMA_ROOT) if re.match(r'^\d+\.\d+\.\d+$', d)], key=lambda v: tuple(map(int, v.split('.'))), reverse=True)
_cache = {}


def component_props(comp):
    """member names the newest official schema defines for an entity component, or None when there is no schema file"""
    if comp in _cache:
        return _cache[comp]
    props = None
    fn = comp.replace(':', '_') + '.json'
    for v in VERSIONS:
        p = f'{SCHEMA_ROOT}/{v}/{fn}'
        if os.path.exists(p):
            d = jl(p)
            props = set(d.get('properties', {}).keys()) if isinstance(d.get('properties'), dict) else None
            break
    _cache[comp] = props
    return props


def walk_entity_components(ent, ident):
    e = ent['minecraft:entity']
    blocks = [('components', e.get('components', {}))] + [(f'component_groups.{g}', c) for g, c in e.get('component_groups', {}).items()]
    for where, comps in blocks:
        for name, body in comps.items():
            if not name.startswith('minecraft:') or not isinstance(body, dict):
                continue
            props = component_props(name)
            if props:
                for k in body:
                    if k not in props:
                        bad(f'{ident}: {where}: {name}.{k} is not a member of the official schema')
            if name == 'minecraft:interact':
                for it in body.get('interactions', []):
                    ps = it.get('play_sounds')
                    if ps is not None and not isinstance(ps, list):
                        bad(f'{ident}: {where}: interact.play_sounds must be an array')
                    tt = it.get('transform_to_item')
                    if isinstance(tt, str) and re.search(r':\d+$', tt):
                        bad(f'{ident}: {where}: transform_to_item "{tt}" uses an item data suffix - use a real item id')
            s = json.dumps(body)
            for m in re.finditer(r'"value": "([a-z_:]+:\d+)"', s):
                bad(f'{ident}: {where}: {name}: item value "{m.group(1)}" uses a data suffix')


for p in glob.glob(f'{BP}/entities/*.json'):
    walk_entity_components(jl(p), os.path.basename(p))

# ------------------------------------------------------------------------------------------------ blocks
ALL_BLOCKS = {f'ecr:{os.path.basename(p)[:-5]}' for p in glob.glob(f'{BP}/blocks/*.json')}
for p in glob.glob(f'{BP}/blocks/*.json'):
    b = jl(p)['minecraft:block']
    name = os.path.basename(p)
    base = set(b.get('components', {}))
    for perm in b.get('permutations', []):
        for c in perm.get('components', {}):
            if c == 'minecraft:redstone_producer' and c not in base:
                bad(f'{name}: redstone_producer in a permutation but not in the base components (format >= 1.26.20)')
    for perm in b.get('permutations', []):
        if '%' in perm.get('condition', ''):
            bad(f'{name}: Molang has no % operator - use math.mod() ({perm["condition"]})')
    traits = b['description'].get('traits', {})
    if 'minecraft:multi_block' in traits and 'minecraft:movable' not in base:
        bad(f'{name}: trait minecraft:multi_block needs the component minecraft:movable')
bl = jl(f'{RP}/blocks.json')
for k in bl:
    if k.startswith('ecr:') and k not in ALL_BLOCKS:
        bad(f'blocks.json: {k} does not exist')
for p in glob.glob(f'{BP}/items/*.json'):
    it = jl(p)['minecraft:item']['components']
    ref = it.get('minecraft:block_placer', {}).get('block')
    if ref and ref.startswith('ecr:') and ref not in ALL_BLOCKS:
        bad(f'{os.path.basename(p)}: block_placer references missing block {ref}')

# ------------------------------------------------------------------------------------------------ features
for p in glob.glob(f'{BP}/features/*.json'):
    d = jl(p)
    name = os.path.basename(p)
    kind = [k for k in d if k.startswith('minecraft:') and k.endswith('_feature')]
    if 'minecraft:structure_template_feature' in d and 'constraints' not in d['minecraft:structure_template_feature']:
        bad(f'{name}: structure_template_feature has no `constraints`')
    s = json.dumps(d)
    for m in re.finditer(r'"cherry_canopy": \{[^{}]*?"height": \{"range_min": (\d+)', s):
        if int(m.group(1)) < 4:
            bad(f'{name}: cherry_canopy height range_min {m.group(1)} < 4')


def scan_chance(o, where):
    if isinstance(o, dict):
        if 'scatter_chance' in o and isinstance(o['scatter_chance'], dict):
            c = o['scatter_chance']
            if c.get('numerator', 0) >= c.get('denominator', 1):
                bad(f'{where}: scatter_chance numerator must be below the denominator ({c})')
        for v in o.values():
            scan_chance(v, where)
    elif isinstance(o, list):
        for v in o:
            scan_chance(v, where)


for p in glob.glob(f'{BP}/feature_rules/*.json'):
    scan_chance(jl(p), os.path.basename(p))

# ------------------------------------------------------------------------------------------------ recipes
ITEMS = {f'ecr:{os.path.basename(p)[:-5]}' for p in glob.glob(f'{BP}/items/*.json')} | ALL_BLOCKS
for p in glob.glob(f'{BP}/recipes/*.json'):
    d = jl(p)
    name = os.path.basename(p)
    for kind in ('minecraft:recipe_shaped', 'minecraft:recipe_shapeless'):
        if kind in d:
            r = d[kind]
            if 'unlock' not in r:
                bad(f'{name}: 1.20+ recipes require unlock data')
            res = r.get('result')
            res = res[0] if isinstance(res, list) else res
            item = res.get('item') if isinstance(res, dict) else None
            if item and item.startswith('ecr:') and item not in ITEMS:
                bad(f'{name}: result {item} does not exist')

print(f'\nLINT5: {len(problems)} problem(s)')
sys.exit(1 if problems else 0)
