"""Lint part 4 ("bug sweep"): official schemas for entities + spawn rules, Molang names/balance, animation/geometry/texture cross-refs,
biome tags, loot ids, recipe uniqueness.  Run via `python tools/dev.py lint`."""
import glob, json, os, re, subprocess, sys
from common import *

problems, warns = [], []


def bad(m):
    problems.append(m)
    print('  X', m)


def warn(m):
    warns.append(m)
    print('  ~', m)


def jl(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


SM = f'{BEDROCK_SAMPLES}/metadata'
mq = jl(f'{SM}/molang_modules/mojang-molang-queries.json')
QUERIES = {q['name'].split('.', 1)[1] for q in mq['queries']}
MATHF = {m['name'].split('.', 1)[1] for m in mq['math_functions']} | {'pi'}
vd = jl(f'{SM}/vanilladata_modules/mojang-blocks.json')
VBLOCK = {b['name'] for b in vd['data_items']}
VITEM = {i['name'] for i in jl(f'{SM}/vanilladata_modules/mojang-items.json')['data_items']}
VBI = VBLOCK | VITEM
BIOME_TAGS = set()
for p in glob.glob(f'{BEDROCK_SAMPLES}/behavior_pack/biomes/*.biome.json'):
    m = re.search(r'"tags"\s*:\s*\[(.*?)\]', open(p, encoding='utf-8').read(), re.S)
    if m:
        BIOME_TAGS |= set(re.findall(r'"([a-z_0-9]+)"', m.group(1)))
MINE = {f'ecr:{os.path.basename(p)[:-5]}' for d in ('blocks', 'items', 'entities') for p in glob.glob(f'{BP}/{d}/*.json')}
VANILLA_MATERIALS = {'entity', 'entity_alphatest', 'entity_emissive_alpha', 'entity_alphatest_change_color', 'fireball', 'entity_nocull', 'entity_multitexture',
                     'armor', 'armor_enchanted', 'entity_beam', 'entity_static', 'entity_alphablend'}

# ------------------------------------------------------------------ official schemas (entities, spawn rules)
def schema(d, root, files):
    env = dict(os.environ)
    r = subprocess.run(['node', (ROOT / 'tools' / 'validate_schema.js').as_posix(), d, root] + files, capture_output=True, text=True, env=env)
    cur = ''
    for l in r.stdout.split('\n'):
        l = l.strip()
        if not l or l.startswith('checked'):
            if l:
                print(' ', l)
            continue
        if l.startswith('INVALID') or l.startswith('JSON PARSE'):
            cur = l
        elif 'passingSchemas' in l or '/filters' in l or '/minecraft:biome_filter' in l or 'entity_types must be object' in l:
            continue                    # the official filter schema is stricter than vanilla's own entities (cow, zombie...) - known false positives
        else:
            bad(f'schema {cur}: {l}')


schema(f'{SM}/json_schemas/server/entity/1.26.50', 'ActorDocument.json', glob.glob(f'{BP}/entities/*.json'))
schema(f'{SM}/json_schemas/server/spawn/1.21.50', 'Spawn Rules.json', glob.glob(f'{BP}/spawn_rules/*.json'))

# ------------------------------------------------------------------ Molang
def molang_check(expr, where):
    if expr.count('(') != expr.count(')'):
        bad(f'{where}: unbalanced parentheses in {expr!r}')
    for ns, name in re.findall(r'\b(query|q|math|variable|v|temp|t)\.([a-z_0-9]+)', expr):
        if ns in ('query', 'q') and name not in QUERIES:
            bad(f'{where}: unknown query.{name}')
        if ns == 'math' and name not in MATHF:
            bad(f'{where}: unknown math.{name}')


def walk_strings(o, fn, path=''):
    if isinstance(o, str):
        fn(o, path)
    elif isinstance(o, dict):
        for k, v in o.items():
            walk_strings(v, fn, f'{path}/{k}')
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk_strings(v, fn, f'{path}[{i}]')


anim_defs = {}                                  # animation id -> set(bones)
for p in glob.glob(f'{RP}/animations/*.json'):
    d = jl(p)
    for aid, a in d['animations'].items():
        anim_defs[aid] = set(a.get('bones', {}).keys())
        walk_strings(a, lambda s, path: molang_check(s, f'{os.path.basename(p)}:{aid}{path}'))

geo = {}
for p in glob.glob(f'{RP}/models/**/*.json', recursive=True):
    for g in jl(p).get('minecraft:geometry', []):
        geo[g['description']['identifier']] = {b['name'] for b in g['bones']}

rcs = {}
for p in glob.glob(f'{RP}/render_controllers/*.json'):
    for k, v in jl(p)['render_controllers'].items():
        rcs[k] = v
        walk_strings(v, lambda s, path: molang_check(s, f'{os.path.basename(p)}:{k}{path}'))

# BP entity properties
bp_props = {}
for p in glob.glob(f'{BP}/entities/*.json'):
    e = jl(p)['minecraft:entity']
    bp_props[e['description']['identifier']] = set(e['description'].get('properties', {}).keys())

used_anims = set()
for p in glob.glob(f'{RP}/entity/*.entity.json'):
    ce = jl(p)['minecraft:client_entity']['description']
    ident = ce['identifier']
    nm = os.path.basename(p)
    walk_strings(ce.get('scripts', {}), lambda s, path: molang_check(s, f'{nm}{path}'))
    if ident in MINE and ident not in bp_props:
        pass
    for gid in ce.get('geometry', {}).values():
        if gid not in geo and gid != 'geometry.fireball':
            bad(f'{nm}: geometry {gid} not found')
    for t in ce.get('textures', {}).values():
        if not any(os.path.exists(f'{RP}/{t}.{x}') for x in ('png', 'tga')):
            bad(f'{nm}: texture {t} missing')
    for m in ce.get('materials', {}).values():
        if m not in VANILLA_MATERIALS:
            warn(f'{nm}: material {m} not in the known list')
    for rc in ce.get('render_controllers', []):
        if rc not in rcs and not rc.startswith('controller.render.fireball'):
            bad(f'{nm}: render controller {rc} not defined')
    gbones = set().union(*[geo.get(g, set()) for g in ce.get('geometry', {}).values()]) if ce.get('geometry') else set()
    for short, aid in ce.get('animations', {}).items():
        if aid.startswith('animation.ecr_'):
            used_anims.add(aid)
            if aid not in anim_defs:
                bad(f'{nm}: animation {aid} not defined')
            else:
                for bone in anim_defs[aid] - gbones:
                    warn(f'{nm}: animation {aid} drives bone "{bone}" that the geometry does not have')
    # every q.property used must be declared on the behaviour entity
    for prop in re.findall(r"q(?:uery)?\.property\('([^']+)'\)", json.dumps(ce)):
        if prop not in bp_props.get(ident, set()):
            bad(f'{nm}: uses property {prop} that {ident} does not declare')
    # render-controller part_visibility bones exist
    for rc in ce.get('render_controllers', []):
        for pv in rcs.get(rc, {}).get('part_visibility', []):
            for bone in pv:
                if bone != '*' and bone not in gbones:
                    bad(f'{nm}: part_visibility bone {bone} not in geometry')
for aid in set(anim_defs) - used_anims:
    warn(f'animation {aid} is never used by a client entity')

# ------------------------------------------------------------------ UI json: every texture it names exists
for p_ in glob.glob(f'{RP}/ui/*.json'):
    walk_strings(jl(p_), lambda s, path: bad(f'{os.path.basename(p_)}: texture {s} missing') if s.startswith('textures/') and not os.path.exists(f'{RP}/{s}.png') else None)

# ------------------------------------------------------------------ biome tags in spawn rules and feature rules
def tags_in(o, out):
    if isinstance(o, dict):
        if o.get('test') == 'has_biome_tag' and isinstance(o.get('value'), str):
            out.add(o['value'])
        for v in o.values():
            tags_in(v, out)
    elif isinstance(o, list):
        for v in o:
            tags_in(v, out)


for p in glob.glob(f'{BP}/spawn_rules/*.json') + glob.glob(f'{BP}/feature_rules/*.json'):
    used = set()
    tags_in(jl(p), used)
    for t in used - BIOME_TAGS:
        bad(f'{os.path.basename(p)}: biome tag "{t}" is not used by any vanilla biome')
    if '/spawn_rules/' in p.replace('\\', '/'):
        d = jl(p)['minecraft:spawn_rules']
        ident = d['description']['identifier']
        if ident not in MINE:
            bad(f'{os.path.basename(p)}: spawn rule for unknown entity {ident}')
        for c in d['conditions']:
            sob = c.get('minecraft:spawns_on_block_filter', [])
            for b in ([sob] if isinstance(sob, str) else sob):
                if b not in VBLOCK and b not in MINE:
                    bad(f'{os.path.basename(p)}: spawn block {b} unknown')

# ------------------------------------------------------------------ loot tables + recipes
for p in glob.glob(f'{BP}/loot_tables/**/*.json', recursive=True):
    for pool in jl(p).get('pools', []):
        for e in pool.get('entries', []):
            n = e.get('name')
            if n and n not in VBI and n not in MINE:
                bad(f'{os.path.relpath(p, BP)}: unknown item {n}')

ids = {}
for p in glob.glob(f'{BP}/recipes/*.json'):
    j = jl(p)
    body = next(v for k, v in j.items() if k.startswith('minecraft:recipe'))
    i = body['description']['identifier']
    if i in ids:
        bad(f'duplicate recipe identifier {i}: {os.path.basename(p)} and {ids[i]}')
    ids[i] = os.path.basename(p)
    if i != f'ecr:{os.path.basename(p)[:-5]}':
        warn(f'recipe {os.path.basename(p)} has identifier {i}')

# every chest loot table referenced by a structure exists
pal_dir = f'{BUILD}/structure_palettes'
tables = {os.path.basename(p)[:-5] for p in glob.glob(f'{BP}/loot_tables/chests/*.json')}
for p in glob.glob(f'{BP}/structures/ecr/*.mcstructure'):
    raw = open(p, 'rb').read()
    for t in set(re.findall(rb'loot_tables/chests/([a-z_0-9]+)\.json', raw)):
        if t.decode() not in tables:
            bad(f'{os.path.basename(p)}: chest loot table {t.decode()} missing')

# ------------------------------------------------------------------ every vanilla id mentioned in a script must exist (block / item / entity / particle)
ENT = {e['name'] for e in jl(f'{SM}/vanilladata_modules/mojang-entities.json')['data_items']}
PART = set()
for p_ in glob.glob(f'{BEDROCK_SAMPLES}/resource_pack/particles/*.json'):
    PART |= set(re.findall(r'"identifier"\s*:\s*"(minecraft:[a-z_0-9]+)"', open(p_, encoding='utf-8').read()))
NOT_IDS = {'minecraft:cherry_grove', 'minecraft:block_face', 'minecraft:vertical_half', 'minecraft:equippable', 'minecraft:overworld', 'minecraft:nether', 'minecraft:the_end', 'minecraft:player', 'minecraft:free'}
known = VBI | ENT | PART | NOT_IDS
for p_ in glob.glob(f'{BP}/scripts/*.js'):
    src = open(p_, encoding='utf-8').read()
    for mid in sorted(set(re.findall(r"'(minecraft:[a-z_0-9]+)'", src))):
        if mid not in known:
            bad(f'{os.path.basename(p_)}: "{mid}" is not a known vanilla block/item/entity/particle id')

# ------------------------------------------------------------------ fogs pushed by scripts exist
fog_ids = {jl(p_)['minecraft:fog_settings']['description']['identifier'] for p_ in glob.glob(f'{RP}/fogs/*.json')}
src_b = open(f'{BP}/scripts/blossom.js', encoding='utf-8').read()
m_ = re.search(r'const FOGS = \[(.*?)\];', src_b, re.S)
for f in re.findall(r'\$\{NS\}:([a-z_]+)', m_.group(1)) if m_ else []:
    if f'ecr:{f}' not in fog_ids:
        bad(f'blossom.js pushes fog ecr:{f} but no such fog definition exists')

# ------------------------------------------------------------------ diag.js lists exactly the creatures the behaviour pack defines
m_ = re.search(r'CREATURES = \[(.*?)\];', open(f'{BP}/scripts/diag.js', encoding='utf-8').read(), re.S)
listed = set(re.findall(r"'([a-z_]+)'", m_.group(1))) if m_ else set()
defined = set()
for p_ in glob.glob(f'{BP}/entities/*.json'):
    e_ = jl(p_)['minecraft:entity']
    fam_ = e_['components'].get('minecraft:type_family', {}).get('family', [])
    if 'projectile' not in fam_ and 'ecr_projectile' not in fam_:
        defined.add(os.path.basename(p_)[:-5])
if listed != defined:
    bad(f'diag.js CREATURES out of sync: missing {sorted(defined - listed)} extra {sorted(listed - defined)}')

# ------------------------------------------------------------------ sounds: every definition points at a real file; scripts only play defined ids
sdefs = jl(f'{RP}/sounds/sound_definitions.json')['sound_definitions'] if os.path.exists(f'{RP}/sounds/sound_definitions.json') else {}
for k, v in sdefs.items():
    for snd in v['sounds']:
        if not os.path.exists(f"{RP}/{snd['name']}.ogg"):
            bad(f'sound {k}: file {snd["name"]}.ogg missing')
for p_ in glob.glob(f'{BP}/scripts/*.js'):
    for sid in set(re.findall(r"'(ecr\.music\.[a-z_]+)'", open(p_, encoding='utf-8').read())):
        if sid not in sdefs:
            bad(f'{os.path.basename(p_)}: plays undefined sound {sid}')

# ------------------------------------------------------------------ every mob has a spawn egg (projectiles excluded)
for p_ in glob.glob(f'{BP}/entities/*.json'):
    e_ = jl(p_)['minecraft:entity']
    fam = e_['components'].get('minecraft:type_family', {}).get('family', [])
    if 'projectile' in fam or 'ecr_projectile' in fam:
        continue
    n = os.path.basename(p_)[:-5]
    if not e_['description'].get('is_spawnable'):
        bad(f'mob ecr:{n} is not spawnable (no spawn egg)')
    ce_ = jl(f'{RP}/entity/{n}.entity.json')['minecraft:client_entity']['description']
    if 'spawn_egg' not in ce_:
        bad(f'mob ecr:{n} has no spawn_egg colours in its client entity')

# ------------------------------------------------------------------ every block / item / entity has a display name
lang = {}
for line in open(f'{RP}/texts/en_US.lang', encoding='utf-8').read().split('\n'):
    if '=' in line:
        k, v = line.split('=', 1)
        lang[k] = v
for p_ in glob.glob(f'{BP}/blocks/*.json'):
    n = os.path.basename(p_)[:-5]
    if f'tile.ecr:{n}.name' not in lang:
        bad(f'no display name for block ecr:{n}')
for p_ in glob.glob(f'{BP}/items/*.json'):
    n = os.path.basename(p_)[:-5]
    if f'item.ecr:{n}.name' not in lang and f'item.ecr:{n}' not in lang:
        bad(f'no display name for item ecr:{n}')
for p_ in glob.glob(f'{BP}/entities/*.json'):
    n = os.path.basename(p_)[:-5]
    if f'entity.ecr:{n}.name' not in lang:
        bad(f'no display name for entity ecr:{n}')
    d_ = jl(p_)['minecraft:entity']['description']
    if d_.get('is_spawnable') and f'item.spawn_egg.entity.ecr:{n}.name' not in lang:
        bad(f'no spawn egg name for ecr:{n}')

# boss-bar skins: bossbar.js SKINS must match gen_ui.SKINS (the glyph page is indexed by position), and every skin boss must be an entity
import gen_ui
js = open(f'{ROOT}/tools/scripts/bossbar.js', encoding='utf-8').read()
m_ = re.search(r"export const SKINS = \[([^\]]*)\]", js)
js_skins = re.findall(r"'([a-z_]+)'", m_.group(1)) if m_ else []
if js_skins != list(gen_ui.SKINS):
    bad(f'bossbar.js SKINS {js_skins} != gen_ui.SKINS {list(gen_ui.SKINS)}')
for sk in gen_ui.SKINS:
    if not os.path.exists(f'{BP}/entities/{sk}.json'):
        bad(f'boss-bar skin {sk} has no entity')
if not os.path.exists(f'{RP}/font/glyph_E4.png'):
    bad('missing RP font/glyph_E4.png (boss-bar glyph page)')

print(f'\nLINT4: {len(problems)} problem(s), {len(warns)} warning(s)')
sys.exit(1 if problems else 0)
