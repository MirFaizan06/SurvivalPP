"""Extra checks: entity/item component names against official lists, Molang balance, image sanity."""
from common import *
import json, glob, re, os, sys
from PIL import Image
BP = (OUT + '/ECR_BP')
RP = (OUT + '/ECR_RP')
SCH = (SCHEMA_DIR + '/json_schemas/server')
bad = []

ent_comps = set(json.load(open(f'{SCH}/entity/1.26.50/Entity component definitions.json'))['properties'].keys())
item_comps = set(json.load(open(f'{SCH}/item/1.26.30/Item Components.json'))['properties'].keys())
# components that exist but are not in the (older) definitions file
ent_extra = {'minecraft:boss', 'minecraft:behavior.ranged_attack', 'minecraft:projectile', 'minecraft:collision_box', 'minecraft:freezing_immune'}

for p in glob.glob(f'{BP}/entities/*.json'):
    e = json.load(open(p))['minecraft:entity']
    comps = set(e['components'].keys())
    for g in e.get('component_groups', {}).values():
        comps |= set(g.keys())
    for c in comps:
        if c not in ent_comps and c not in ent_extra:
            bad.append(f'{os.path.basename(p)}: component not in official list: {c}')
    for ev, body in (e.get('events') or {}).items():
        for g in (body.get('add', {}) or {}).get('component_groups', []) + (body.get('remove', {}) or {}).get('component_groups', []):
            if g not in e.get('component_groups', {}):
                bad.append(f'{os.path.basename(p)}: event {ev} uses unknown group {g}')
    # shooter projectile defs exist
    for g in [e['components']] + list(e.get('component_groups', {}).values()):
        sh = g.get('minecraft:shooter')
        if sh and not os.path.exists(f"{BP}/entities/{sh['def'].split(':')[1]}.json"):
            bad.append(f'{os.path.basename(p)}: shooter def {sh["def"]} missing')

for p in glob.glob(f'{BP}/items/*.json'):
    it = json.load(open(p))['minecraft:item']
    for c in it['components']:
        if c not in item_comps:
            bad.append(f'{os.path.basename(p)}: item component not in official list: {c}')

def balanced(s):
    d = 0
    for ch in s:
        if ch == '(': d += 1
        if ch == ')': d -= 1
        if d < 0: return False
    return d == 0

def walk(o, where):
    if isinstance(o, dict):
        for v in o.values(): walk(v, where)
    elif isinstance(o, list):
        for v in o: walk(v, where)
    elif isinstance(o, str):
        if not balanced(o):
            bad.append(f'{where}: unbalanced parens: {o[:80]}')
        if o.count("'") % 2:
            bad.append(f'{where}: odd quotes: {o[:80]}')

for p in glob.glob(f'{RP}/animations/*.json') + glob.glob(f'{RP}/entity/*.json') + glob.glob(f'{BP}/blocks/*.json'):
    walk(json.load(open(p)), os.path.basename(p))

for p in glob.glob(f'{RP}/textures/entity/*.tga'):
    im = Image.open(p)
    if im.mode != 'RGBA':
        bad.append(f'{p}: mode {im.mode}')
for p in glob.glob(f'{RP}/textures/**/*.png', recursive=True):
    if os.sep + 'ui' + os.sep in p or '/ui/' in p:
        continue                      # UI images are drawn stretched, not atlased: any size is fine
    im = Image.open(p)
    w, h = im.size
    if (w & (w - 1)) or (h & (h - 1)):
        bad.append(f'{p}: non power-of-two {im.size}')

print('LINT2:', len(bad), 'problem(s)')
for b in bad:
    print('  X', b)
