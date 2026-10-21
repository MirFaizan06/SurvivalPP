"""v1.2 structures: Forgotten Graveyard, Verdant Shrine, Silk Nest, Hunter's Camp, Mossy Boulder."""
import math, random
from common import *
from structures import Structure, tag_compound, tag_string, tag_byte, tag_int, tag_list, circle_pts

STRUCT_DIR = f'{BP}/structures/ecr'


def chest(S, pos, table, facing=2):
    S.set(*pos, 'minecraft:chest', {'facing_direction': facing})
    S.block_data[pos] = tag_compound({
        'id': tag_string('Chest'), 'isMovable': tag_byte(1), 'LootTable': tag_string(f'loot_tables/chests/{table}.json'),
        'LootTableSeed': tag_int(0), 'x': tag_int(pos[0]), 'y': tag_int(pos[1]), 'z': tag_int(pos[2]),
        'Items': tag_list([], 10)})


def root(S, x, z, base, depth, block='minecraft:dirt'):
    for k in range(1, depth + 1):
        if base - k >= 0:
            S.set(x, base - k, z, block)


# ============================================================================== FORGOTTEN GRAVEYARD  (ground layer = base)
def graveyard(path, seed=11):
    rng = random.Random(seed)
    R, base = 8, 5
    S = Structure(2 * R + 1, base + 10, 2 * R + 1)
    c = R
    for x in range(2 * R + 1):
        for z in range(2 * R + 1):
            d = math.hypot(x - c, z - c)
            if d > 8.4:
                continue
            S.set(x, base, z, 'minecraft:podzol' if rng.random() < 0.35 else ('minecraft:coarse_dirt' if rng.random() < 0.2 else 'minecraft:grass_block'))
            root(S, x, z, base, 2 + (1 if d < 5 else 0))
            for y in range(1, 5):
                S.set(x, base + y, z, 'minecraft:air')
    # iron-fence boundary with lantern posts
    for a in range(0, 360, 6):
        x = c + int(round(math.cos(math.radians(a)) * 7.6))
        z = c + int(round(math.sin(math.radians(a)) * 7.6))
        S.set(x, base + 1, z, 'minecraft:iron_bars')
    for a in range(0, 360, 90):
        x = c + int(round(math.cos(math.radians(a + 45)) * 7.4))
        z = c + int(round(math.sin(math.radians(a + 45)) * 7.4))
        for y in range(1, 4):
            S.set(x, base + y, z, 'ecr:polished_slate')
        S.set(x, base + 4, z, 'minecraft:soul_lantern')
    for gx in (c - 1, c, c + 1):                                               # gate gap on the south side
        for gz in (c + 7, c + 8):
            S.set(gx, base + 1, gz, 'minecraft:air')
    # mausoleum (north side)
    mx, mz = c, c - 4
    for x in range(mx - 3, mx + 4):
        for z in range(mz - 2, mz + 3):
            S.set(x, base, z, 'ecr:polished_slate')
            for y in range(1, 5):
                edge = x in (mx - 3, mx + 3) or z in (mz - 2, mz + 2)
                S.set(x, base + y, z, ('ecr:slate' if (x + y + z) % 5 else 'minecraft:mossy_cobblestone') if edge else 'minecraft:air')
            S.set(x, base + 5, z, 'ecr:polished_slate')
    for x in range(mx - 2, mx + 3):
        S.set(x, base + 6, mz, 'ecr:slate')
    S.set(mx, base + 1, mz + 2, 'minecraft:air'); S.set(mx, base + 2, mz + 2, 'minecraft:air')      # doorway facing the yard
    S.set(mx, base + 3, mz + 2, 'ecr:polished_slate')
    chest(S, (mx, base + 1, mz - 1), 'ecr_graveyard', 3)
    S.set(mx - 2, base + 1, mz - 1, 'minecraft:bone_block'); S.set(mx + 2, base + 1, mz - 1, 'minecraft:bone_block')
    S.set(mx, base + 1, mz, 'minecraft:soul_lantern')
    for x in (mx - 2, mx + 2):
        S.set(x, base + 3, mz - 1, 'minecraft:web')
    # summoning plinth for the Hollow King in the yard
    px, pz = c, c + 2
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            S.set(px + dx, base, pz + dz, 'minecraft:stone_bricks' if (dx + dz) % 2 else 'ecr:polished_slate')
    S.set(px, base + 1, pz, 'minecraft:bone_block')
    for (dx, dz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        S.set(px + dx, base + 1, pz + dz, 'minecraft:soul_torch', {'torch_facing_direction': 'top'})
    # graves
    spots = [(-5, -1), (-5, 2), (-5, 5), (5, -1), (5, 2), (5, 5), (-2, 6), (2, 6), (-3, 0), (3, 0)]
    rng.shuffle(spots)
    for (gx, gz) in spots[:8]:
        x, z = c + gx, c + gz
        if math.hypot(gx, gz) > 7:
            continue
        for k in range(3):
            S.set(x, base, z + k, 'minecraft:coarse_dirt')
        S.set(x, base + 1, z, rng.choice(['ecr:slate', 'ecr:marlstone', 'minecraft:mossy_cobblestone']))
        S.set(x, base + 2, z, 'ecr:polished_slate')
    # dead trees / brush
    for (tx, tz, h) in ((-6, -5, 5), (6, -6, 4), (-6, 6, 4)):
        for y in range(1, h):
            S.set(c + tx, base + y, c + tz, 'minecraft:stripped_oak_log' if y > 1 else 'minecraft:oak_log')
        S.set(c + tx + 1, base + h - 1, c + tz, 'minecraft:oak_fence'); S.set(c + tx, base + h - 2, c + tz - 1, 'minecraft:oak_fence')
    for _ in range(14):
        x, z = c + rng.randint(-6, 6), c + rng.randint(-6, 6)
        if math.hypot(x - c, z - c) < 7 and S.get(x, base + 1, z) is None:
            S.set(x, base + 1, z, rng.choice(['minecraft:dead_bush', 'minecraft:web', 'minecraft:brown_mushroom', 'minecraft:fern']))
    S.save(path)
    return S.size, base


# ============================================================================== VERDANT SHRINE
def verdant_shrine(path, seed=12):
    rng = random.Random(seed)
    R, base = 6, 4
    S = Structure(2 * R + 1, base + 9, 2 * R + 1)
    c = R
    for dx, dz in circle_pts(6.3):
        d = math.hypot(dx, dz)
        x, z = c + dx, c + dz
        S.set(x, base, z, 'minecraft:moss_block' if d < 5.2 else 'minecraft:mossy_cobblestone')
        root(S, x, z, base, 2 + (1 if d < 4 else 0), 'minecraft:moss_block' if d < 5 else 'minecraft:dirt')
        for y in range(1, 8):
            S.set(x, base + y, z, 'minecraft:air')
        if d < 5.2 and d > 1.6 and rng.random() < 0.55:
            S.set(x, base + 1, z, 'minecraft:moss_carpet')
    S.set(c, base, c, 'minecraft:moss_block')
    S.set(c, base + 1, c, 'minecraft:moss_block')                                   # ritual block for the Colossus
    for k in range(8):
        a = k / 8 * math.tau + 0.4
        px, pz = c + int(round(math.cos(a) * 5)), c + int(round(math.sin(a) * 5))
        h = 4 + (k % 3)
        for y in range(1, h):
            S.set(px, base + y, pz, 'minecraft:mossy_cobblestone' if y % 2 else 'ecr:verdite' if (k % 2) else 'minecraft:moss_block')
        S.set(px, base + h, pz, 'minecraft:moss_block')
        S.set(px, base + h + 1, pz, rng.choice(['minecraft:azalea', 'minecraft:flowering_azalea', 'minecraft:oak_sapling']))
        S.set(px, base + 1, pz, 'minecraft:mossy_cobblestone')
    for (dx, dz) in ((2, 0), (-2, 0), (0, 2), (0, -2), (2, 2), (-2, -2)):
        S.set(c + dx, base + 1, c + dz, rng.choice(['minecraft:moss_carpet', 'minecraft:brown_mushroom', 'minecraft:red_mushroom', 'ecr:wild_strawberry', 'ecr:wild_oats']))
    chest(S, (c + 3, base + 1, c), 'ecr_verdant_shrine', 4)
    S.save(path)
    return S.size, base


# ============================================================================== SILK NEST (underground chamber, no ground level)
def silk_nest(path, seed=13):
    rng = random.Random(seed)
    R, H = 6, 9
    S = Structure(2 * R + 1, H, 2 * R + 1)
    c = R
    for x in range(2 * R + 1):
        for z in range(2 * R + 1):
            for y in range(H):
                d = math.sqrt((x - c) ** 2 + ((y - 3.2) * 1.5) ** 2 + (z - c) ** 2)
                if d <= 5.6:
                    S.set(x, y, z, 'minecraft:air')
                elif d <= 6.8:
                    S.set(x, y, z, 'minecraft:stone' if rng.random() < 0.6 else rng.choice(['ecr:slate', 'ecr:umbrastone', 'minecraft:deepslate']))
    for x in range(2 * R + 1):                                                           # silk-lined floor
        for z in range(2 * R + 1):
            if math.hypot(x - c, z - c) <= 5.6:
                S.set(x, 0, z, 'minecraft:black_wool' if rng.random() < 0.25 else 'minecraft:white_wool' if rng.random() < 0.35 else 'ecr:polished_umbrastone')
    for _ in range(60):                                                                   # cobwebs everywhere
        x, y, z = c + rng.randint(-5, 5), rng.randint(1, 6), c + rng.randint(-5, 5)
        if S.get(x, y, z) is not None and math.sqrt((x - c) ** 2 + ((y - 3.2) * 1.5) ** 2 + (z - c) ** 2) <= 5.4:
            S.set(x, y, z, 'minecraft:web')
    for (dx, dz) in ((3, 2), (-3, 3), (2, -3), (-2, -3), (4, -1)):                    # egg sacs
        S.set(c + dx, 1, c + dz, 'minecraft:slime')
        S.set(c + dx, 2, c + dz, 'minecraft:web')
    # silk idol altar: ritual cobweb on a plinth
    S.set(c, 1, c, 'ecr:polished_umbrastone')
    S.set(c, 2, c, 'minecraft:web')
    chest(S, (c + 1, 1, c + 3), 'ecr_silk_nest', 2)
    S.save(path)
    return S.size


# ============================================================================== HUNTER'S CAMP
def hunters_camp(path, seed=14):
    rng = random.Random(seed)
    R, base = 5, 4
    S = Structure(2 * R + 1, base + 6, 2 * R + 1)
    c = R
    for dx, dz in circle_pts(5.2):
        x, z = c + dx, c + dz
        S.set(x, base, z, 'minecraft:coarse_dirt' if rng.random() < 0.5 else 'minecraft:grass_block')
        root(S, x, z, base, 2)
        for y in range(1, 6):
            S.set(x, base + y, z, 'minecraft:air')
    S.set(c, base + 1, c, 'minecraft:campfire', {'extinguished': False})
    for (dx, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        S.set(c + dx, base + 1, c + dz, 'minecraft:spruce_log', {'pillar_axis': 'x' if dx else 'z'})
    # A-frame tent (west)
    tx, tz = c - 4, c
    for z in range(tz - 2, tz + 3):
        S.set(tx, base + 3, z, 'minecraft:spruce_planks')
        S.set(tx - 1, base + 2, z, 'minecraft:brown_wool' if z % 2 else 'minecraft:white_wool'); S.set(tx + 1, base + 2, z, 'minecraft:brown_wool' if z % 2 else 'minecraft:white_wool')
        S.set(tx - 2, base + 1, z, 'minecraft:brown_wool'); S.set(tx + 2, base + 1, z, 'minecraft:brown_wool')
        S.set(tx, base + 1, z, 'minecraft:air')
    chest(S, (tx, base + 1, tz - 1), 'ecr_hunters_camp', 3)
    S.set(tx, base + 1, tz + 1, 'minecraft:barrel', {'facing_direction': 1})
    # drying rack with hanging "meat" (cooked venison stand-ins: hay + fences)
    rx, rz = c + 3, c - 2
    for z in range(rz, rz + 3):
        S.set(rx, base + 1, z, 'minecraft:oak_fence'); S.set(rx, base + 2, z, 'minecraft:oak_fence')
    S.set(rx, base + 3, rz, 'minecraft:oak_slab'); S.set(rx, base + 3, rz + 1, 'minecraft:oak_slab'); S.set(rx, base + 3, rz + 2, 'minecraft:oak_slab')
    S.set(rx + 1, base + 1, rz + 1, 'minecraft:hay_block')
    S.set(c + 2, base + 1, c + 3, 'minecraft:fletching_table')
    for _ in range(6):
        x, z = c + rng.randint(-4, 4), c + rng.randint(-4, 4)
        if S.get(x, base + 1, z) is None and math.hypot(x - c, z - c) < 5:
            S.set(x, base + 1, z, rng.choice(['minecraft:fern', 'minecraft:short_grass', 'minecraft:sweet_berry_bush']))
    S.save(path)
    return S.size, base


# ============================================================================== MOSSY BOULDER
def boulder(path, seed=15):
    rng = random.Random(seed)
    R, base = 4, 3
    S = Structure(2 * R + 1, base + 6, 2 * R + 1)
    c = R
    cx, cy, cz = c + rng.uniform(-0.4, 0.4), base + 1.6, c + rng.uniform(-0.4, 0.4)
    for x in range(2 * R + 1):
        for z in range(2 * R + 1):
            for y in range(base - 1, base + 6):
                d = math.sqrt((x - cx) ** 2 + ((y - cy) * 1.25) ** 2 + (z - cz) ** 2) + rng.uniform(-0.35, 0.35)
                if d <= 3.1:
                    r = rng.random()
                    top = y > base + 1
                    S.set(x, y, z, 'minecraft:mossy_cobblestone' if r < 0.38 else 'minecraft:moss_block' if (top and r < 0.55) else rng.choice(['minecraft:stone', 'ecr:slate', 'ecr:marlstone']) if r < 0.85 else 'minecraft:cobblestone')
    for x in range(2 * R + 1):
        for z in range(2 * R + 1):
            if math.hypot(x - c, z - c) <= 4.2 and S.get(x, base, z) is None:
                S.set(x, base, z, 'minecraft:grass_block'); root(S, x, z, base, 2)
    S.save(path)
    return S.size, base


def build_all():
    out = {}
    out['graveyard'] = graveyard(f'{STRUCT_DIR}/forgotten_graveyard.mcstructure')
    out['verdant_shrine'] = verdant_shrine(f'{STRUCT_DIR}/verdant_shrine.mcstructure')
    out['silk_nest'] = silk_nest(f'{STRUCT_DIR}/silk_nest.mcstructure')
    out['hunters_camp'] = hunters_camp(f'{STRUCT_DIR}/hunters_camp.mcstructure')
    out['boulder'] = boulder(f'{STRUCT_DIR}/mossy_boulder.mcstructure')
    return out


if __name__ == '__main__':
    print(build_all())
