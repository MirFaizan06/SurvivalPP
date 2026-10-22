"""v1.7 places of the Burning Deep: the Forge of Vows (three offering pedestals), the Ashen Chapel (the Bridal Anvil), the Toll Tower (four bells
and their core) and the Hollow Hall (the Grave Altar)."""
import math
from sbuild import *

BS, PB, PBB, CPB = 'minecraft:blackstone', 'minecraft:polished_blackstone', 'minecraft:polished_blackstone_bricks', 'minecraft:cracked_polished_blackstone_bricks'
GILD, MAGMA, SOILD, NB = 'minecraft:gilded_blackstone', 'minecraft:magma', 'minecraft:soul_soil', 'minecraft:nether_brick'
SLANT = 'minecraft:soul_lantern'


def slantern(b, x, y, z, hanging=False):
    b.put(x, y, z, SLANT, hanging=hanging)


def floor_disc(b, r, mix, w, depth=3):
    b.disc(r, 0, mix, 'minecraft:netherrack', depth, 0)
    for x in range(b.sx):
        for z in range(b.sz):
            if ((x - b.cx) ** 2 + (z - b.cz) ** 2) ** 0.5 <= r - 0.5 and b.get(x, 0, z) is not None:
                b.put(x, 0, z, b.rng.choices(mix, w)[0])


# ----------------------------------------------------------------------------- Forge of Vows
def forge_of_vows():
    S = 29
    b = B('forge_of_vows', S, 26, S, 4, 900)
    c = 14
    mix, w = [BS, PBB, CPB, MAGMA, GILD, SOILD], [6, 5, 3, 2, 1, 1]
    floor_disc(b, 13.4, mix, w)
    b.clear(0, 1, 0, S - 1, 20, S - 1)
    # lava channels (the forge's flues)
    for z in range(2, S - 2):
        if abs(z - c) > 2:
            b.put(c - 8, 0, z, 'minecraft:lava'); b.put(c + 8, 0, z, 'minecraft:lava')
    # perimeter wall with a south gate
    b.ring(c - 12, c - 12, c + 12, c + 12, 1, 4, [PBB, BS, CPB], [6, 4, 3])
    b.crumble(c - 12, c - 12, c + 12, c + 12, 3, 4, 0.25)
    b.clear(c - 2, 1, c + 12, c + 2, 4, c + 12)
    for x in (c - 3, c + 3):
        for y in range(1, 7):
            b.put(x, y, c + 12, PBB if y % 3 else GILD)
        slantern(b, x, 7, c + 12)
    b.fill(c - 3, 7, c + 12, c + 3, 7, c + 12, PBB)
    # the great anvil: a monument at the north end
    b.fill(c - 3, 1, c - 10, c + 3, 2, c - 7, PBB)
    b.fill(c - 2, 3, c - 9, c + 2, 4, c - 8, BS)
    b.fill(c - 1, 5, c - 9, c + 1, 6, c - 8, BS)
    b.fill(c - 5, 7, c - 10, c + 5, 8, c - 7, PBB)
    b.fill(c - 4, 9, c - 9, c + 4, 9, c - 8, GILD)
    for x in range(c - 4, c + 5, 2):
        b.put(x, 10, c - 9, MAGMA)
    b.put(c, 3, c - 7, 'minecraft:lava')                                                 # a flame at the anvil's heart
    # three pedestals, in space: Flame - Tears - Gold (the vow was spoken Gold, Flame, Tears)
    for dx, kind in ((-6, 'flame'), (0, 'tears'), (6, 'gold')):
        b.fill(c + dx, 1, c + 3, c + dx, 1, c + 3, PB)
        b.put(c + dx, 2, c + 3, f'ecr:pedestal_{kind}', **{'ecr:offered': 0})
        slantern(b, c + dx - 1, 2, c + 4); slantern(b, c + dx + 1, 2, c + 4)
    # the three vows, carved in ember tablets before each pedestal's row
    for dx, t in ((-6, 0), (0, 1), (6, 2)):
        b.put(c + dx, 1, c + 6, 'ecr:ember_tablet', **{'ecr:text': t})
    b.put(c - 11, 1, c - 11, 'ecr:ember_tablet', **{'ecr:text': 3})
    b.put(c + 11, 1, c - 11, 'ecr:ember_tablet', **{'ecr:text': 4})
    # pillars, a broken canopy and hanging lanterns
    for sx in (-1, 1):
        for sz in (-1, 1):
            ox, oz = c + sx * 6, c + sz * 8
            for y in range(1, 9):
                b.put(ox, y, oz, PBB if y % 4 else GILD)
            slantern(b, ox, 9, oz)
    for x in range(c - 7, c + 8):
        for z in (c - 8, c + 8):
            if b.rng.random() < 0.6:
                b.put(x, 8, z, PBB)
    # loot, spawners, a trap
    b.chest(c - 10, 1, c + 2, 'ecr_forge_of_vows', 'east')
    b.chest(c + 10, 1, c + 2, 'ecr_forge_of_vows', 'west')
    b.spawner(c - 10, 1, c - 3, 'minecraft:blaze', 2, 4, 3, 220, 600)
    b.spawner(c + 10, 1, c - 3, 'minecraft:wither_skeleton', 2, 4, 3, 300, 700)
    b.tnt_trap(c, 0, c + 10, PB)
    return b.save()


# ----------------------------------------------------------------------------- Ashen Chapel
def ashen_chapel():
    S = 31
    b = B('ashen_chapel', S, 28, S, 5, 910)
    c = 15
    mix, w = [BS, PBB, CPB, SOILD, MAGMA], [6, 5, 3, 2, 1]
    floor_disc(b, 14.6, mix, w, 4)
    b.clear(0, 1, 0, S - 1, 22, S - 1)
    # nave: 13 wide, 23 long (north = apse)
    for y in range(1, 11):
        for z in range(4, 27):
            for x in (c - 6, c + 6):
                b.put(x, y, z, b.rng.choices([PBB, CPB, BS, GILD], [8, 4, 3, 1])[0])
        for x in range(c - 6, c + 7):
            b.put(x, y, 26, b.rng.choices([PBB, CPB, BS], [8, 4, 3])[0])
            b.put(x, y, 4, b.rng.choices([PBB, CPB, BS], [8, 4, 3])[0])
    b.crumble(c - 6, 4, c + 6, 26, 6, 10, 0.25)
    b.clear(c - 1, 1, 26, c + 1, 5, 26)                                                  # south doorway
    for y in range(6, 10):                                                               # tall windows
        for z in (8, 12, 16, 20):
            for x in (c - 6, c + 6):
                b.put(x, y, z, 'minecraft:glass_pane')
    for x in range(c - 6, c + 7):                                                        # ribbed roof, half collapsed
        for z in range(5, 26):
            if (z % 4 == 0 or abs(x - c) == 6) and b.rng.random() < 0.7:
                b.put(x, 11, z, PBB)
    for z in range(5, 26, 4):                                                            # arches
        for k, y in enumerate((8, 9, 10)):
            for x in (c - 6 + k, c + 6 - k):
                if b.rng.random() < 0.8:
                    b.put(x, y, z, PBB)
    # aisle: black carpet runner with a white bride's path
    for z in range(5, 26):
        for x in (c - 1, c, c + 1):
            b.put(x, 1, z, 'minecraft:black_carpet')
        b.put(c, 1, z, 'minecraft:white_carpet')
    # burnt pews
    for z in range(10, 24, 3):
        for side in (-1, 1):
            for dx in range(2, 5):
                if b.rng.random() < 0.8:
                    b.slab(c + side * dx, 1, z, 'minecraft:nether_brick', 'bottom')
    # the apse: a dais and the Bridal Anvil
    for x in range(c - 4, c + 5):
        for z in range(5, 10):
            b.put(x, 1, z, PB)
    b.fill(c - 2, 2, 6, c + 2, 2, 8, PBB)
    b.put(c, 3, 7, 'ecr:bridal_anvil')
    for dx in (-2, 2):
        for y in range(3, 9):
            b.put(c + dx, y, 6, PBB if y % 3 else GILD)
        slantern(b, c + dx, 9, 6)
    b.put(c - 4, 2, 6, 'ecr:ember_tablet', **{'ecr:text': 5})
    b.put(c + 4, 2, 6, 'ecr:ember_tablet', **{'ecr:text': 4})
    # side crypt below the nave, found by following the cracked floor tiles
    b.fill(c - 4, -4, 12, c + 4, -1, 20, PBB)
    b.clear(c - 3, -3, 13, c + 3, -1, 19)
    b.put(c - 5, 0, 22, PBB)
    b.ladder(c + 3, -3, 0, 13, 'south')
    b.put(c + 3, 0, 13, CPB)                                                             # the cap that hides the shaft
    b.chest(c, -3, 18, 'ecr_ashen_chapel_crypt', 'north')
    b.chest(c - 3, -3, 14, 'ecr_ashen_chapel_crypt', 'east')
    slantern(b, c, -2, 16)
    # loot, spawners, traps
    b.chest(c - 5, 1, 12, 'ecr_ashen_chapel', 'east')
    b.chest(c + 5, 1, 18, 'ecr_ashen_chapel', 'west')
    b.spawner(c - 5, 1, 21, 'minecraft:blaze', 2, 4, 3, 220, 600)
    b.spawner(c + 5, 1, 9, 'minecraft:wither_skeleton', 2, 4, 3, 300, 700)
    b.tnt_trap(c, 1, 14, PB)
    return b.save()


# ----------------------------------------------------------------------------- Toll Tower
def toll_tower():
    S = 15
    b = B('toll_tower', S, 42, S, 4, 920)
    c = 7
    floor_disc(b, 6.8, [SOILD, 'minecraft:soul_sand', BS, PBB], [4, 4, 2, 2], 3)
    b.clear(0, 1, 0, S - 1, 33, S - 1)
    # the shaft: 9x9 walls, 22 high
    for y in range(1, 23):
        for k in range(-4, 5):
            for (x, z) in ((c + k, c - 4), (c + k, c + 4), (c - 4, c + k), (c + 4, c + k)):
                b.put(x, y, z, b.rng.choices([PBB, CPB, BS, GILD], [8, 4, 3, 1])[0] if y % 6 else GILD)
    b.clear(c - 1, 1, c + 4, c + 1, 3, c + 4)                                            # door
    for y in range(1, 22):
        b.put(c - 3, y, c - 3, 'minecraft:ladder', facing_direction=3)                      # a ladder up the north-west corner (faces south)
    for y in (6, 12, 18):                                                                  # landings
        for x in range(c - 3, c + 4):
            for z in range(c - 3, c + 4):
                if not (x == c - 3 and z == c - 3):
                    b.put(x, y, z, PBB) if (x + z) % 2 == 0 or abs(x - c) == 3 or abs(z - c) == 3 else None
    for y in (5, 11, 17):
        slantern(b, c + 3, y, c + 3)
    # belfry: open on four sides, y 23..29
    for y in range(23, 31):
        for (x, z) in ((c - 4, c - 4), (c + 4, c - 4), (c - 4, c + 4), (c + 4, c + 4)):
            b.put(x, y, z, PBB if y % 3 else GILD)
    b.fill(c - 4, 22, c - 4, c + 4, 22, c + 4, PBB)
    b.fill(c - 4, 31, c - 4, c + 4, 31, c + 4, PBB)
    for k in range(4):
        b.fill(c - 3 + k, 32 + k // 2, c - 3 + k, c + 3 - k, 32 + k // 2, c + 3 - k, PBB)
    b.put(c, 35, c, GILD)
    b.put(c, 36, c, SLANT, hanging=False)
    # the core and its four bells (one per cardinal side, on the belfry rim)
    b.put(c, 23, c, 'ecr:toll_core')
    b.put(c, 26, c, SLANT, hanging=True)
    for (dx, dz, n) in ((0, -3, 0), (3, 0, 1), (0, 3, 2), (-3, 0, 3)):
        b.put(c + dx, 23, c + dz, PB)
        b.put(c + dx, 24, c + dz, f'ecr:toll_bell_{n}')
    b.put(c - 1, 23, c, 'ecr:ember_tablet', **{'ecr:text': 6})
    # base room loot + spawner + trap
    b.chest(c + 2, 1, c - 2, 'ecr_toll_tower', 'south')
    b.spawner(c - 2, 1, c + 2, 'minecraft:wither_skeleton', 2, 4, 3, 300, 700)
    b.tnt_trap(c, 0, c + 1, PB)
    return b.save()


# ----------------------------------------------------------------------------- Hollow Hall
def hollow_hall():
    S = 35
    b = B('hollow_hall', S, 28, S, 4, 930)
    c = 17
    floor_disc(b, 16.8, [SOILD, 'minecraft:soul_sand', BS, PBB, CPB], [4, 4, 2, 3, 2], 3)
    b.clear(0, 1, 0, S - 1, 22, S - 1)
    # long hall: 15 wide x 29 long, walls of polished blackstone with basalt buttresses
    for y in range(1, 11):
        for z in range(3, 33):
            for x in (c - 7, c + 7):
                b.put(x, y, z, b.rng.choices([PBB, CPB, BS], [7, 4, 3])[0])
        for x in range(c - 7, c + 8):
            b.put(x, y, 32, b.rng.choices([PBB, CPB, BS], [7, 4, 3])[0])
            b.put(x, y, 3, b.rng.choices([PBB, CPB, BS], [7, 4, 3])[0])
    b.crumble(c - 7, 3, c + 7, 32, 5, 10, 0.3)
    b.clear(c - 1, 1, 32, c + 1, 5, 32)
    for z in range(6, 31, 5):                                                            # buttresses
        for side in (-1, 1):
            for y in range(1, 11):
                b.put(c + side * 8, y, z, 'minecraft:polished_basalt', pillar_axis='y')
            slantern(b, c + side * 6, 4, z)
    for z in range(4, 32, 4):                                                            # roof beams (mostly fallen)
        for x in range(c - 7, c + 8):
            if b.rng.random() < 0.45:
                b.put(x, 11, z, PBB)
    # the bride's aisle: black runner, white bridal path, empty pews
    for z in range(4, 32):
        for x in (c - 1, c, c + 1):
            b.put(x, 1, z, 'minecraft:black_carpet')
        b.put(c, 1, z, 'minecraft:white_carpet')
    for z in range(12, 31, 3):
        for side in (-1, 1):
            for dx in range(2, 6):
                if b.rng.random() < 0.85:
                    b.slab(c + side * dx, 1, z, 'minecraft:nether_brick', 'bottom')
    # the groom's dais at the far end: a ring of soul lanterns, the Grave Altar in the middle
    for x in range(c - 5, c + 6):
        for z in range(4, 12):
            if (x - c) ** 2 + (z - 8) ** 2 <= 30:
                b.put(x, 1, z, PB)
    b.fill(c - 1, 2, 7, c + 1, 2, 9, PBB)
    b.put(c, 3, 8, 'ecr:grave_altar')
    for k in range(10):
        a = k / 10 * math.tau
        x, z = int(round(c + math.cos(a) * 4.4)), int(round(8 + math.sin(a) * 4.4))
        b.put(x, 2, z, PBB); slantern(b, x, 3, z)
    b.put(c - 3, 2, 12, 'ecr:ember_tablet', **{'ecr:text': 7})
    b.put(c + 3, 2, 12, 'ecr:ember_tablet', **{'ecr:text': 8})
    b.put(c - 6, 1, 20, 'ecr:ember_tablet', **{'ecr:text': 9})
    b.put(c + 6, 1, 24, 'ecr:ember_tablet', **{'ecr:text': 10})
    b.put(c, 1, 29, 'ecr:ember_tablet', **{'ecr:text': 11})
    # loot, spawners, traps
    b.chest(c - 6, 1, 6, 'ecr_hollow_hall', 'east')
    b.chest(c + 6, 1, 6, 'ecr_hollow_hall', 'west')
    b.chest(c - 6, 1, 28, 'ecr_hollow_hall', 'east')
    b.spawner(c - 5, 1, 16, 'minecraft:wither_skeleton', 2, 4, 3, 300, 700)
    b.spawner(c + 5, 1, 22, 'minecraft:wither_skeleton', 2, 4, 3, 300, 700)
    b.tnt_trap(c, 0, 20, PB)
    return b.save()


def build_all():
    return {'forge_of_vows': forge_of_vows(), 'ashen_chapel': ashen_chapel(), 'toll_tower': toll_tower(), 'hollow_hall': hollow_hall()}


if __name__ == '__main__':
    print(build_all())
