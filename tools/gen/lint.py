"""Cross-reference lint for the generated packs."""
from common import *
import json, os, re, sys, subprocess, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
BP = (OUT + '/ECR_BP')
RP = (OUT + '/ECR_RP')
SCH = SCHEMA_DIR
problems = []


def bad(msg):
    problems.append(msg)
    print('  X', msg)


def jl(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def vanilla_names(fn):
    d = json.load(open(f'{SCH}/vanilladata_modules/{fn}'))
    names = set()
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ('name', 'id', 'block_name', 'item_name') and isinstance(v, str):
                    names.add(v if ':' in v else 'minecraft:' + v)
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)
    walk(d)
    return names


VB = vanilla_names('mojang-blocks.json')
VI = vanilla_names('mojang-items.json')
VBI = VB | VI

all_json = [p for p in glob.glob(f'{BP}/**/*.json', recursive=True) + glob.glob(f'{RP}/**/*.json', recursive=True)]
print('JSON files:', len(all_json))
for p in all_json:
    try:
        jl(p)
    except Exception as e:
        bad(f'parse {p}: {e}')

# ---------------------------------------------------------------- ids
my_blocks = {f'ecr:{os.path.basename(p)[:-5]}' for p in glob.glob(f'{BP}/blocks/*.json')}
my_items = {f'ecr:{os.path.basename(p)[:-5]}' for p in glob.glob(f'{BP}/items/*.json')}
my_entities = {f'ecr:{os.path.basename(p)[:-5]}' for p in glob.glob(f'{BP}/entities/*.json')}
my_particles = {f'ecr:{os.path.basename(p)[:-5]}' for p in glob.glob(f'{RP}/particles/*.json')}
my_fogs = {f'ecr:{os.path.basename(p)[:-5]}' for p in glob.glob(f'{RP}/fogs/*.json')}
mine = my_blocks | my_items | my_entities
print('blocks', len(my_blocks), 'items', len(my_items), 'entities', len(my_entities))


def check_ref(name, where, kind='bi'):
    if name.startswith('ecr:'):
        if name not in mine:
            bad(f'{where}: unknown ecr id {name}')
    elif name.startswith('minecraft:'):
        pool = VBI if kind == 'bi' else VB
        if name not in pool:
            bad(f'{where}: unknown vanilla id {name}')


# recipes
for p in glob.glob(f'{BP}/recipes/*.json'):
    j = jl(p)
    body = next(v for k, v in j.items() if k.startswith('minecraft:recipe'))
    names = []
    if 'key' in body:
        names += [v['item'] for v in body['key'].values()]
    if 'ingredients' in body:
        names += [v['item'] for v in body['ingredients']]
    if 'input' in body:
        names.append(body['input'])
    if 'output' in body:
        names.append(body['output'])
    if 'result' in body:
        names.append(body['result']['item'])
    for n in names:
        check_ref(n, os.path.basename(p))
    if 'pattern' in body:
        w = max(len(r) for r in body['pattern'])
        for r in body['pattern']:
            for ch in r:
                if ch != ' ' and ch not in body['key']:
                    bad(f'{os.path.basename(p)}: pattern char {ch} missing from key')

# loot
for p in glob.glob(f'{BP}/loot_tables/**/*.json', recursive=True):
    j = jl(p)
    for pool in j.get('pools', []):
        for e in pool.get('entries', []):
            if e.get('type') == 'item':
                check_ref(e['name'], os.path.relpath(p, BP))
        for c in pool.get('conditions', []):
            if c.get('condition') == 'match_tool':
                check_ref(c['item'], os.path.relpath(p, BP))
for p in glob.glob(f'{BP}/blocks/*.json'):
    j = jl(p)['minecraft:block']
    loot = j['components'].get('minecraft:loot')
    if loot and not os.path.exists(f'{BP}/{loot}'):
        bad(f'{os.path.basename(p)}: missing loot {loot}')
for p in glob.glob(f'{BP}/entities/*.json'):
    j = jl(p)['minecraft:entity']
    loot = j['components'].get('minecraft:loot')
    if loot and not os.path.exists(f"{BP}/{loot['table']}"):
        bad(f'{os.path.basename(p)}: missing loot {loot["table"]}')

# features
def walk_strings(o, cb):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ('places_block', 'name', 'filler', 'inner_layer', 'alternate_inner_layer', 'middle_layer', 'outer_layer', 'block', 'ground_block') and isinstance(v, str):
                cb(v)
            walk_strings(v, cb)
    elif isinstance(o, list):
        for x in o:
            if isinstance(x, str) and x.startswith(('minecraft:', 'ecr:')):
                cb(x)
            walk_strings(x, cb)


feat_ids = {f'ecr:{os.path.basename(p)[:-5]}' for p in glob.glob(f'{BP}/features/*.json')}
for p in glob.glob(f'{BP}/features/*.json'):
    walk_strings(jl(p), lambda n, p=p: check_ref(n, os.path.basename(p), 'b') if (':' in n and n not in feat_ids) else None)
for p in glob.glob(f'{BP}/feature_rules/*.json'):
    pf = jl(p)['minecraft:feature_rules']['description']['places_feature']
    if pf not in feat_ids:
        bad(f'{os.path.basename(p)}: unknown feature {pf}')
for p in glob.glob(f'{BP}/features/*.json'):
    j = jl(p)
    for k, v in j.items():
        if k.startswith('minecraft:'):
            for key in ('places_feature', 'feature_to_snap', 'feature_to_place'):
                if key in v and v[key] not in feat_ids and not v[key].startswith('minecraft:'):
                    bad(f'{os.path.basename(p)}: unknown feature ref {v[key]}')
            for f in v.get('features', []):
                ref = f[0] if isinstance(f, list) else f
                if ref not in feat_ids:
                    bad(f'{os.path.basename(p)}: unknown feature ref {ref}')
            if 'structure_name' in v:
                n = v['structure_name'].split(':')[1]
                if not os.path.exists(f'{BP}/structures/ecr/{n}.mcstructure'):
                    bad(f'{os.path.basename(p)}: missing structure {n}')

# structures: palette block names
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import struct
def read_nbt(path):
    b = open(path, 'rb').read(); pos = [0]
    def rd(fmt):
        n = struct.calcsize(fmt); v = struct.unpack_from(fmt, b, pos[0]); pos[0] += n; return v[0]
    def rstr():
        n = rd('<H'); s = b[pos[0]:pos[0] + n].decode(); pos[0] += n; return s
    def payload(t):
        if t == 1: return rd('<b')
        if t == 2: return rd('<h')
        if t == 3: return rd('<i')
        if t == 4: return rd('<q')
        if t == 5: return rd('<f')
        if t == 8: return rstr()
        if t == 9:
            et = rd('<b'); n = rd('<i'); return [payload(et) for _ in range(n)]
        if t == 10:
            d = {}
            while True:
                tt = rd('<b')
                if tt == 0: break
                k = rstr()
                d[k] = payload(tt)
            return d
        raise Exception(t)
    t = rd('<b'); rstr(); return payload(t)
for p in glob.glob(f'{BP}/structures/ecr/*.mcstructure'):
    d = read_nbt(p)
    for ent in d['structure']['palette']['default']['block_palette']:
        check_ref(ent['name'], os.path.basename(p), 'b')

# ---------------------------------------------------------------- blocks: components + textures
comp_props = set(jl(f'{SCH}/json_schemas/server/block/1.26.20/Components.json')['properties'].keys())
terrain = jl(f'{RP}/textures/terrain_texture.json')['texture_data']
itemtex = jl(f'{RP}/textures/item_texture.json')['texture_data']
for k, v in terrain.items():
    if not os.path.exists(f"{RP}/{v['textures']}.png"):
        bad(f'terrain {k}: missing {v["textures"]}.png')
for k, v in itemtex.items():
    if not os.path.exists(f"{RP}/{v['textures']}.png"):
        bad(f'item tex {k}: missing {v["textures"]}.png')

def collect_material_textures(obj, out):
    if isinstance(obj, dict):
        mi = obj.get('minecraft:material_instances')
        if isinstance(mi, dict):
            for v in mi.values():
                out.append(v if isinstance(v, str) else v.get('texture'))
        for v in obj.values():
            collect_material_textures(v, out)
    elif isinstance(obj, list):
        for v in obj:
            collect_material_textures(v, out)

geo_ids = {}
for p in glob.glob(f'{RP}/models/**/*.json', recursive=True):
    for g in jl(p).get('minecraft:geometry', []):
        geo_ids[g['description']['identifier']] = {b['name'] for b in g['bones']}
for p in glob.glob(f'{BP}/blocks/*.json'):
    j = jl(p)['minecraft:block']
    comps = []
    def gather(o):
        if isinstance(o, dict):
            comps.extend(o.keys())
        return o
    for k in j['components']:
        if k.startswith('minecraft:') and k not in comp_props:
            bad(f'{os.path.basename(p)}: unknown block component {k}')
    for pm in j.get('permutations', []):
        for k in pm['components']:
            if k.startswith('minecraft:') and k not in comp_props:
                bad(f'{os.path.basename(p)}: unknown permutation component {k}')
    texs = []
    collect_material_textures(j, texs)
    for t in texs:
        if t not in terrain:
            bad(f'{os.path.basename(p)}: unknown terrain texture {t}')
    # geometry references
    def geos(o):
        out = []
        if isinstance(o, dict):
            g = o.get('minecraft:geometry')
            if isinstance(g, str): out.append(g)
            elif isinstance(g, dict): out.append(g['identifier'])
            for v in o.values(): out += geos(v)
        elif isinstance(o, list):
            for v in o: out += geos(v)
        return out
    for g in geos(j):
        if not g.startswith('minecraft:') and g not in geo_ids:
            bad(f'{os.path.basename(p)}: unknown geometry {g}')
    # sound
bl = jl(f'{RP}/blocks.json')
for b in my_blocks:
    if b not in bl:
        bad(f'blocks.json missing {b}')

# items: icons
for p in glob.glob(f'{BP}/items/*.json'):
    j = jl(p)['minecraft:item']
    ic = j['components'].get('minecraft:icon')
    if ic:
        t = ic['textures']['default']
        if t not in itemtex:
            bad(f'{os.path.basename(p)}: unknown icon {t}')

# lang
lang = dict(l.split('=', 1) for l in open(f'{RP}/texts/en_US.lang', encoding='utf-8').read().split('\n') if '=' in l)
for b in my_blocks:
    if f'tile.{b}.name' not in lang:
        bad(f'lang missing tile.{b}.name')
for i in my_items:
    if f'item.{i}' not in lang:
        bad(f'lang missing item.{i}')
for e in ('ashen_warg', 'voidweaver', 'eclipse_sovereign'):
    if f'entity.ecr:{e}.name' not in lang:
        bad(f'lang missing entity {e}')

# ---------------------------------------------------------------- entities
anim_ids = {}
for p in glob.glob(f'{RP}/animations/*.json'):
    for k, v in jl(p)['animations'].items():
        anim_ids[k] = set(v.get('bones', {}).keys())
rc_ids = set()
for p in glob.glob(f'{RP}/render_controllers/*.json'):
    rc_ids |= set(jl(p)['render_controllers'].keys())
for p in glob.glob(f'{RP}/entity/*.entity.json'):
    d = jl(p)['minecraft:client_entity']['description']
    ident = d['identifier']
    for g in d['geometry'].values():
        if g not in geo_ids and not g.startswith('geometry.fireball'):
            bad(f'{ident}: geometry {g} missing')
    for t in d['textures'].values():
        if not (os.path.exists(f'{RP}/{t}.png') or os.path.exists(f'{RP}/{t}.tga')):
            bad(f'{ident}: texture {t} missing')
    for rc in d['render_controllers']:
        if rc not in rc_ids and not rc.startswith('controller.render.fireball'):
            bad(f'{ident}: render controller {rc} missing')
    geom_bones = set()
    for g in d['geometry'].values():
        geom_bones |= geo_ids.get(g, set())
    for short, full in d['animations'].items():
        if full.startswith('animation.ecr'):
            if full not in anim_ids:
                bad(f'{ident}: animation {full} missing')
            else:
                for bn in anim_ids[full]:
                    if bn not in geom_bones:
                        bad(f'{ident}: animation {full} drives unknown bone {bn}')
    for a in d.get('scripts', {}).get('animate', []):
        nm = a if isinstance(a, str) else list(a.keys())[0]
        if nm not in d['animations']:
            bad(f'{ident}: animate refers to unknown {nm}')

# attachables
for p in glob.glob(f'{RP}/attachables/*.json'):
    d = jl(p)['minecraft:attachable']['description']
    for t in d['textures'].values():
        if t.startswith('textures/models/armor') and not os.path.exists(f'{RP}/{t}.png'):
            bad(f'{os.path.basename(p)}: missing {t}')

# non-id ecr: strings the scripts use (dynamic property keys, scriptevent ids, block states, entity events/properties, tags)
SCRIPT_WORDS = ('bossbar', 'bossbar_off', 'cinematic', 'cinematic_off', 'verse', 'lit', 'text', 'puzzle', 'gear', 'intro', 'c3', 'c4', 'puzzle_v1', 'cantor_state', 'expire', 'despawn', 'melee_mode', 'ranged_mode', 'mode_switcher', 'switch_to_melee', 'switch_to_ranged', 'verse_stone', 'lore_tablet', 'sconce', 'sconce_', 'chime', 'choir_lectern', 'marsh_altar')

# scripts: ids referenced
for p in glob.glob(f'{BP}/scripts/*.js'):
    s = open(p, encoding='utf-8').read()
    for m in re.finditer(r"`\$\{NS\}:([a-z_0-9]+)`|'ecr:([a-z_0-9]+)'", s):
        n = 'ecr:' + (m.group(1) or m.group(2))
        if n not in mine and n not in my_particles and n not in my_fogs and n not in ('ecr:needs_netherite_pickaxe',):
            # custom block components / states / props are legitimate non-ids
            if n.split(':')[1] in ('altar', 'stasis_chamber', 'stasis_plate', 'openable', 'plate', 'button', 'leaves', 'sapling', 'loaded', 'powered', 'open', 'pressed', 'persistent', 'phase', 'casting', 'link', 'db_v1', 'cast_on', 'cast_off', 'enter_phase_2', 'enter_phase_3', 'hinge_right', 'growth', 'sanctum_idx', 'diag', 'blossom_veil', 'blossom_storm', 'eclipse_bloom', 'story', 'journal_given', 'puffing', 'stag', 'roll_stag', 'relic', 'crop', 'wild_crop', 'pass_zone', 'sanctum_v1', 'wplates_v1', 'deathmsg_suppressed', 'sanctum', 'needs_netherite_pickaxe', *SCRIPT_WORDS):
                continue
            bad(f'{os.path.basename(p)}: unknown id {n}')

# block schema + item schema validation
for what, d, root, files in (('blocks', f'{SCH}/json_schemas/server/block/1.26.20', 'Blocks.json', glob.glob(f'{BP}/blocks/*.json')),
                             ('items', f'{SCH}/json_schemas/server/item/1.26.30', 'ItemDocument.json', glob.glob(f'{BP}/items/*.json'))):
    env = dict(os.environ, IGNORE_STATES='1')
    r = subprocess.run(['node', (ROOT / 'tools' / 'validate_schema.js').as_posix(), d, root] + files, capture_output=True, text=True, env=env)
    lines = [l for l in r.stdout.split('\n') if l.strip()]
    for l in lines:
        if 'checked' in l:
            print(' ', what, l)
        elif 'destroy_speeds' in l or 'passingSchemas' in l:
            continue
        elif l.startswith('INVALID'):
            cur = l
        else:
            bad(f'{what} schema {cur}: {l.strip()}')

print(f'\nLINT: {len(problems)} problem(s)')
sys.exit(1 if problems else 0)
