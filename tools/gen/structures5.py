"""Hanae's Shrine - a torii gate, a stone path, a cherry-wood pavilion over the Blossom Altar, a koi pond and ancient blossom trees (cherry groves only)."""
import math
from sbuild import *


def hanae_shrine():
    b = B('hanae_shrine', 25, 16, 25, 3, 301)
    c = 12
    CR, CRS = 'minecraft:crimson_planks', 'minecraft:stripped_crimson_stem'
    b.disc(11.6, 0, ['minecraft:grass_block', 'minecraft:grass_block', 'minecraft:grass_block', 'minecraft:podzol'], 'minecraft:dirt', 2, 13)
    # path + stepping stones
    for z in range(c + 3, c + 12):
        for x in (c - 1, c, c + 1):
            b.put(x, 0, z, 'minecraft:stone_bricks' if (x + z) % 3 else 'minecraft:polished_andesite')
    for z in range(c - 12 + 14, c + 3):
        pass
    # platform and dais
    b.fill(c - 5, 0, c - 5, c + 5, 0, c + 5, 'minecraft:polished_andesite')
    for k in range(-5, 6):
        for (x, z) in ((c + k, c - 5), (c + k, c + 5), (c - 5, c + k), (c + 5, c + k)):
            b.put(x, 0, z, 'minecraft:stone_bricks')
    b.fill(c - 1, 1, c - 1, c + 1, 1, c + 1, 'minecraft:stone_bricks')
    b.put(c, 2, c, 'ecr:blossom_altar')
    b.chest(c, 1, c - 4, 'ecr_hanae_shrine', 'south')
    # pavilion
    for dx in (-4, 4):
        for dz in (-4, 4):
            for y in range(1, 7):
                b.log(c + dx, y, c + dz, wood='cherry')
    for d in range(-4, 5):
        for (x, z) in ((c + d, c - 4), (c - 4, c + d), (c + 4, c + d)):
            if b.get(x, 1, z) is None:
                b.put(x, 1, z, 'minecraft:cherry_fence')
    b.clear(c, 1, c - 4, c, 1, c - 4)
    b.chest(c, 1, c - 4, 'ecr_hanae_shrine', 'south')
    b.fill(c - 5, 7, c - 5, c + 5, 7, c + 5, 'minecraft:cherry_planks')
    b.fill(c - 4, 8, c - 4, c + 4, 8, c + 4, 'minecraft:cherry_planks')
    b.fill(c - 3, 9, c - 3, c + 3, 9, c + 3, 'minecraft:cherry_planks')
    b.fill(c - 1, 10, c - 1, c + 1, 10, c + 1, 'minecraft:cherry_planks')
    for k in range(-5, 6):
        for (x, z) in ((c + k, c - 6), (c + k, c + 6), (c - 6, c + k), (c + 6, c + k)):
            if 0 <= x < 25 and 0 <= z < 25:
                b.slab(x, 7, z, 'minecraft:cherry', 'bottom') if abs(k) <= 5 and b.get(x, 7, z) is None else None
    for dx in (-2, 2):
        for dz in (-2, 2):
            b.put(c + dx, 6, c + dz, 'minecraft:lantern', hanging=True)
    # torii gate
    for dx in (-3, 3):
        for y in range(1, 7):
            b.put(c + dx, y, c + 9, CRS, pillar_axis='y')
    b.fill(c - 2, 5, c + 9, c + 2, 5, c + 9, CR)
    b.fill(c - 5, 7, c + 9, c + 5, 7, c + 9, CR)
    b.fill(c - 6, 8, c + 9, c + 6, 8, c + 9, CR)
    for dx in (-6, 6):
        b.put(c + dx, 9, c + 9, CR)
    # stone lanterns along the path
    for (x, z) in ((c - 3, c + 4), (c + 3, c + 4), (c - 3, c + 11), (c + 3, c + 11)):
        b.put(x, 1, z, 'minecraft:stone_bricks'); b.put(x, 2, z, 'minecraft:stone_bricks')
        b.put(x, 3, z, 'minecraft:lantern', hanging=False)
    # koi pond (east)
    px, pz = c + 8, c - 3
    for x in range(c + 4, 25):
        for z in range(c - 7, c + 1):
            d = math.hypot(x - px, z - pz)
            if d <= 3.3:
                b.put(x, 0, z, 'minecraft:water', liquid_depth=0)
                b.put(x, -1, z, 'minecraft:clay')
            elif d <= 4.3:
                b.put(x, 0, z, 'minecraft:stone_bricks' if b.rng.random() < 0.5 else 'minecraft:mossy_stone_bricks')
    # ancient blossom trees
    for (tx, tz) in ((c - 9, c - 6), (c - 8, c + 4), (c + 8, c + 8), (c + 3, c - 10)):
        for y in range(1, 6):
            b.log(tx, y, tz, wood='cherry')
        for dx in range(-3, 4):
            for dy in range(-1, 3):
                for dz in range(-3, 4):
                    if dx * dx + (dy * 1.5) ** 2 + dz * dz <= 10.5:
                        x, y, z = tx + dx, 6 + dy, tz + dz
                        if 0 <= x < 25 and 0 <= z < 25 and b.get(x, y, z) is None:
                            b.put(x, y, z, 'minecraft:cherry_leaves', persistent_bit=True, update_bit=False)
    # fallen petals
    for _ in range(90):
        x, z = c + b.rng.randint(-11, 11), c + b.rng.randint(-11, 11)
        if math.hypot(x - c, z - c) < 11 and b.get(x, 1, z) is None and b.get(x, 0, z) is not None and not (abs(x - c) <= 5 and abs(z - c) <= 5):
            b.put(x, 1, z, 'minecraft:pink_petals', growth=b.rng.randint(0, 3), **{'minecraft:cardinal_direction': b.rng.choice(['north', 'south', 'east', 'west'])})
    return b.save()


if __name__ == '__main__':
    print(hanae_shrine())
