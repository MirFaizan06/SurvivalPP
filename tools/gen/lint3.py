"""Lint part 3: structure palettes (block names + states) validated against Mojang's vanilla block data."""
import glob, json, os, sys
from common import *

problems = []


def bad(m):
    problems.append(m)
    print('  X', m)


vd = json.load(open(f'{BEDROCK_SAMPLES}/metadata/vanilladata_modules/mojang-blocks.json'))
blocks = {b['name']: [p['name'] for p in b['properties']] for b in vd['data_items']}
values = {p['name']: [v['value'] for v in p['values']] for p in vd['block_properties']}
my_blocks = {f'ecr:{os.path.basename(p)[:-5]}' for p in glob.glob(f'{BP}/blocks/*.json')}

n = 0
for p in sorted(glob.glob(f'{BUILD}/structure_palettes/*.json')):
    name = os.path.basename(p)[:-5]
    pal = json.load(open(p))
    n += 1
    for bname, states in pal:
        if bname.startswith('ecr:'):
            if bname not in my_blocks:
                bad(f'{name}: unknown ecr block {bname}')
            continue
        if bname not in blocks:
            bad(f'{name}: unknown vanilla block {bname}')
            continue
        for k, v in states.items():
            if k not in blocks[bname]:
                bad(f'{name}: {bname} has no state "{k}" (valid: {blocks[bname]})')
            elif k in values and v not in values[k]:
                bad(f'{name}: {bname} state {k}={v!r} not in {values[k][:8]}')
print(f'structures checked: {n}')
print(f'\nLINT3: {len(problems)} problem(s)')
sys.exit(1 if problems else 0)
