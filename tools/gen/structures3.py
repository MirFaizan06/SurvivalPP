"""Adventure structures, part 1 - EASY and MEDIUM (surface).  Loot tables are named ecr_<structure>[_suffix] (see gen_world3)."""
import math
from sbuild import *


# ============================================================================== 1. BANDIT LOOKOUT  (easy - a stilt tower, two chests, no traps)
def bandit_lookout():
    b = B('bandit_lookout', 15, 19, 15, 3, 101)
    c = 7
    b.disc(6.6, 0, ['minecraft:grass_block', 'minecraft:grass_block', 'minecraft:coarse_dirt', 'minecraft:podzol'], 'minecraft:dirt', 2, 15)
    for dx in (-2, 2):                                                          # four stilts
        for dz in (-2, 2):
            for y in range(1, 9):
                b.log(c + dx, y, c + dz)
    for y in (3, 6):                                                            # cross braces
        for k in range(-2, 3):
            for (x, z) in ((c + k, c - 2), (c + k, c + 2), (c - 2, c + k), (c + 2, c + k)):
                if b.get(x, y, z) is None:
                    b.put(x, y, z, 'minecraft:oak_planks' if y == 3 else 'minecraft:spruce_planks')
    for y in range(1, 9):
        b.log(c, y, c)                                                          # ladder column
    b.ladder(c, 1, 9, c + 1, 'south')
    b.fill(c - 3, 8, c - 3, c + 3, 8, c + 3, 'minecraft:oak_planks')            # platform
    b.put(c, 8, c + 1, AIR)                                                       # hatch
    b.put(c, 8, c, 'minecraft:oak_planks')
    for k in range(-3, 4):                                                      # railing
        for (x, z) in ((c + k, c - 3), (c + k, c + 3), (c - 3, c + k), (c + 3, c + k)):
            if not (x == c and z == c + 3):
                b.put(x, 9, z, 'minecraft:oak_fence')
    for dx in (-3, 3):                                                          # roof posts + roof
        for dz in (-3, 3):
            for y in range(9, 13):
                b.put(c + dx, y, c + dz, 'minecraft:oak_fence' if y > 9 else 'minecraft:oak_log', **({'pillar_axis': 'y'} if y == 9 else {}))
    b.fill(c - 4, 13, c - 4, c + 4, 13, c + 4, 'minecraft:spruce_slab', **{'minecraft:vertical_half': 'bottom'})
    b.put(c, 12, c, 'minecraft:lantern', hanging=True)
    b.chest(c - 2, 9, c - 2, 'ecr_bandit_lookout', 'south')
    b.put(c + 2, 9, c - 2, 'minecraft:barrel', facing_direction=1, open_bit=False)
    b.put(c + 2, 9, c + 2, 'minecraft:hay_block', pillar_axis='y', deprecated=0)
    b.put(c - 2, 9, c + 2, 'minecraft:hay_block', pillar_axis='y', deprecated=0)
    # ground camp
    b.put(c + 4, 1, c - 3, 'minecraft:campfire', extinguished=False, **{'minecraft:cardinal_direction': 'south'})
    b.log(c + 3, 1, c - 3, axis='z'); b.log(c + 5, 1, c - 3, axis='z')
    b.chest(c - 4, 1, c + 3, 'ecr_bandit_camp', 'east')
    b.put(c - 4, 1, c + 4, 'minecraft:barrel', facing_direction=1, open_bit=False)
    b.put(c - 5, 1, c + 3, 'minecraft:hay_block', pillar_axis='x', deprecated=0)
    b.put(c + 4, 1, c + 4, 'minecraft:oak_fence'); b.put(c + 4, 2, c + 4, 'minecraft:oak_fence'); b.put(c + 4, 3, c + 4, 'minecraft:lantern', hanging=False)
    return b.save()


# ============================================================================== 2. SUNKEN WELL  (easy - dry well, cellar, silverfish niche)
def sunken_well():
    b = B('sunken_well', 13, 20, 13, 12, 102)
    c = 6
    b.fill(0, -11, 0, 12, -1, 12, 'minecraft:stone')                            # solid footprint so no cave opens the cellar
    b.fillr(0, -11, 0, 12, -1, 12, ['minecraft:stone', 'minecraft:stone', 'minecraft:andesite', 'minecraft:cobblestone'])
    b.disc(6.2, 0, ['minecraft:grass_block', 'minecraft:grass_block', 'minecraft:coarse_dirt'], 'minecraft:dirt', 1, 6)
    # cellar
    b.room(c - 4, -10, c - 4, c + 4, -4, c + 4, [SB, MSB, CSB], [6, 3, 2])
    b.fill(c - 3, -10, c - 3, c + 3, -10, c + 3, SB)
    # shaft
    b.fill(c - 1, -3, c - 1, c + 1, 0, c + 1, AIR)
    b.fill(c - 1, -4, c - 1, c + 1, -4, c + 1, AIR)
    b.ring(c - 2, c - 2, c + 2, c + 2, -3, 2, [COB, MCOB, COB])
    b.fill(c - 1, 1, c - 1, c + 1, 2, c + 1, AIR)
    b.ladder(c, -9, 0, c - 1, 'south')
    for k in (-2, 2):                                                           # roof frame
        for j in (-2, 2):
            b.put(c + k, 3, c + j, 'minecraft:oak_fence'); b.put(c + k, 4, c + j, 'minecraft:oak_fence')
    b.fill(c - 3, 5, c - 3, c + 3, 5, c + 3, 'minecraft:oak_slab', **{'minecraft:vertical_half': 'bottom'})
    b.clear(c - 1, 5, c - 1, c + 1, 5, c + 1)
    b.put(c, 4, c, 'minecraft:oak_fence'); b.put(c, 5, c, 'minecraft:oak_slab', **{'minecraft:vertical_half': 'bottom'})
    b.put(c, 4, c, AIR)
    # cellar furniture
    b.chest(c - 3, -9, c - 3, 'ecr_sunken_well', 'south')
    b.chest(c + 3, -9, c + 3, 'ecr_sunken_well', 'north')
    for (x, z) in ((c - 3, c + 3), (c + 3, c - 3)):
        b.put(x, -9, z, 'minecraft:barrel', facing_direction=1, open_bit=False)
    b.put(c - 3, -5, c, 'minecraft:soul_lantern', hanging=True)
    b.put(c + 3, -5, c, 'minecraft:soul_lantern', hanging=True)
    b.web(8, c - 3, -9, c - 3, c + 3, -5, c + 3)
    # secret niche behind silverfish bricks (east wall): the hidden chest is the better one
    b.fill(c + 4, -9, c - 1, c + 4, -8, c + 1, 'minecraft:infested_stone_bricks')
    b.fill(c + 5, -9, c - 1, c + 5, -8, c + 1, AIR)
    b.fill(c + 5, -10, c - 1, c + 5, -10, c + 1, SB)
    b.fill(c + 5, -7, c - 1, c + 5, -7, c + 1, SB)
    b.fill(c + 6, -10, c - 1, c + 6, -7, c + 1, SB)
    b.chest(c + 5, -9, c, 'ecr_sunken_well_hidden', 'west')
    return b.save()


# ============================================================================== 3. RUINED WATCH KEEP  (medium - TNT floor plate + a spawner guarding the chests)
def watch_keep():
    b = B('watch_keep', 21, 16, 21, 4, 103)
    c = 10
    b.disc(10.4, 0, ['minecraft:grass_block', 'minecraft:coarse_dirt', 'minecraft:grass_block', 'minecraft:podzol'], 'minecraft:dirt', 2, 12)
    b.fill(c - 8, 0, c - 8, c + 8, 0, c + 8, SB)                                 # courtyard floor
    b.fillr(c - 8, 0, c - 8, c + 8, 0, c + 8, [SB, MSB, CSB, 'minecraft:gravel', 'minecraft:coarse_dirt'], [4, 3, 2, 1, 1])
    b.ring(c - 8, c - 8, c + 8, c + 8, 1, 5, [SB, MSB, CSB], [5, 3, 2])
    for x in range(c - 8, c + 9, 2):                                              # battlements
        for z in (c - 8, c + 8):
            b.put(x, 6, z, SB)
    for z in range(c - 8, c + 9, 2):
        for x in (c - 8, c + 8):
            b.put(x, 6, z, SB)
    b.clear(c - 1, 1, c + 8, c + 1, 3, c + 8)                                     # gate
    for dx in (-2, 2):
        b.put(c + dx, 4, c + 8, 'minecraft:iron_bars')
    # corner towers (5x5 shell, 3x3 interior, ladder up)
    towers = [(c - 8, c - 8), (c + 8, c - 8), (c - 8, c + 8), (c + 8, c + 8)]
    for k, (tx, tz) in enumerate(towers):
        x0, z0 = tx - (0 if tx < c else 4), tz - (0 if tz < c else 4)
        b.room(x0, 0, z0, x0 + 4, 9, z0 + 4, [SB, MSB, CSB], [5, 3, 2])
        b.fill(x0, 9, z0, x0 + 4, 9, z0 + 4, SB)
        b.clear(x0 + 1, 8, z0 + 1, x0 + 3, 9, z0 + 3)
        for (x, z) in ((x0, z0), (x0 + 4, z0), (x0, z0 + 4), (x0 + 4, z0 + 4)):
            b.put(x, 10, z, SB)
    # north-west tower: spawner room with the "tower" chest
    x0, z0 = c - 8, c - 8
    b.spawner(x0 + 2, 1, z0 + 2, 'ecr:gravewalker', 3, 5, 3, 250, 700)
    b.chest(x0 + 1, 1, z0 + 2, 'ecr_watch_keep_tower', 'east')
    b.clear(x0 + 2, 1, z0 + 4, x0 + 2, 2, z0 + 4)                                 # doorway on the courtyard side
    # keep
    b.room(c - 4, 0, c - 4, c + 4, 6, c + 4, [SB, MSB, CSB], [6, 3, 1])
    b.fill(c - 3, 0, c - 3, c + 3, 0, c + 3, SB)
    b.clear(c, 1, c + 4, c, 2, c + 4)                                             # entrance
    b.fill(c - 4, 6, c - 4, c + 4, 6, c + 4, SB)
    b.crumble(c - 4, c - 4, c + 4, c + 4, 6, 6, 0.35)
    b.tnt_trap(c, 1, c + 2, SB, full=False)                                       # trap in the entrance hall
    b.put(c - 1, 1, c + 2, 'minecraft:cracked_stone_bricks')
    b.chest(c, 1, c - 3, 'ecr_watch_keep_keep', 'south')
    b.chest(c + 3, 1, c - 2, 'ecr_watch_keep_keep', 'west')
    b.put(c - 3, 1, c - 3, 'minecraft:bookshelf'); b.put(c - 3, 2, c - 3, 'minecraft:bookshelf')
    b.put(c - 3, 1, c + 1, 'minecraft:bookshelf')
    b.web(10, c - 3, 1, c - 3, c + 3, 5, c + 3)
    # courtyard dressing
    b.put(c - 6, 1, c + 5, 'minecraft:campfire', extinguished=True, **{'minecraft:cardinal_direction': 'south'})
    b.put(c + 6, 1, c + 5, 'minecraft:barrel', facing_direction=1, open_bit=False)
    b.put(c + 6, 1, c + 4, 'minecraft:hay_block', pillar_axis='y', deprecated=0)
    b.crumble(c - 8, c - 8, c + 8, c + 8, 4, 6, 0.4)
    return b.save()


# ============================================================================== 4. DUNE VAULT  (medium - desert pyramid: fall-in shaft + TNT plate chamber)
def dune_vault():
    b = B('dune_vault', 23, 19, 23, 8, 104)
    c = 11
    SS, CS, CH = 'minecraft:sandstone', 'minecraft:cut_sandstone', 'minecraft:chiseled_sandstone'
    b.fill(0, -8, 0, 22, -1, 22, SS)
    b.disc(11.3, 0, ['minecraft:sand', 'minecraft:sand', 'minecraft:sandstone'], SS, 2, 12)
    for L in range(10):                                                           # stepped pyramid
        hw = 10 - L
        b.fill(c - hw, L + 1, c - hw, c + hw, L + 1, c + hw, SS)
    for L in range(0, 10, 3):                                                     # decorative bands
        hw = 10 - L
        for k in range(-hw, hw + 1):
            for (x, z) in ((c + k, c - hw), (c + k, c + hw), (c - hw, c + k), (c + hw, c + k)):
                b.put(x, L + 1, z, 'minecraft:orange_terracotta' if (k % 2 == 0) else 'minecraft:blue_terracotta')
    # entrance corridor (south) and upper hall
    b.clear(c, 1, c + 6, c, 2, c + 10)
    b.fill(c - 4, 1, c - 4, c + 4, 4, c + 4, AIR)
    b.fill(c - 4, 0, c - 4, c + 4, 0, c + 4, CS)
    for (x, z) in ((c - 3, c - 3), (c + 3, c - 3), (c - 3, c + 3), (c + 3, c + 3)):
        for y in range(1, 5):
            b.put(x, y, z, CH if y % 2 else CS)
    b.spawner(c - 3, 1, c, 'minecraft:husk', 2, 4, 3, 300, 800)
    b.chest(c + 3, 1, c - 1, 'ecr_dune_vault_hall', 'west')
    b.web(6, c - 4, 1, c - 4, c + 4, 4, c + 4)
    # fall-in shaft (offset 1 from the plate) down to the trap chamber
    b.fill(c + 1, -1, c, c + 1, 0, c, AIR)
    b.fill(c + 1, -5, c, c + 1, -2, c, AIR)
    # chamber
    b.room(c - 5, -8, c - 5, c + 5, -1, c + 5, [SS, CS], [3, 2])
    b.fill(c - 4, -7, c - 4, c + 4, -7, c + 4, CS)
    b.clear(c + 1, -1, c, c + 1, 0, c)
    b.tnt_trap(c, -6, c, SS, full=True)
    b.fill(c + 1, -6, c, c + 1, -2, c, AIR)
    b.put(c + 1, -7, c, CS)
    b.chest(c, -6, c - 4, 'ecr_dune_vault', 'south'); b.chest(c, -6, c + 4, 'ecr_dune_vault', 'north')
    b.chest(c - 4, -6, c, 'ecr_dune_vault', 'east'); b.chest(c + 4, -6, c, 'ecr_dune_vault', 'west')
    for (x, z) in ((c - 4, c - 4), (c + 4, c - 4), (c - 4, c + 4), (c + 4, c + 4)):
        b.put(x, -6, z, CH); b.put(x, -5, z, CH)
    return b.save()


# ============================================================================== 5. THORN SHRINE  (medium - jungle ruin: spiked pit, wither roses, silverfish)
def thorn_shrine():
    b = B('thorn_shrine', 19, 14, 19, 5, 105)
    c = 9
    b.disc(9.0, 0, ['minecraft:grass_block', 'minecraft:moss_block', 'minecraft:mossy_cobblestone', 'minecraft:podzol'], 'minecraft:dirt', 2, 9)
    b.fillr(c - 7, 0, c - 7, c + 7, 0, c + 7, [MSB, MSB, SB, MCOB, 'minecraft:moss_block'], [4, 3, 2, 2, 1])
    b.ring(c - 7, c - 7, c + 7, c + 7, 1, 4, [MSB, MCOB, SB, MSB], [4, 3, 1, 2])
    b.crumble(c - 7, c - 7, c + 7, c + 7, 3, 4, 0.45)
    b.clear(c - 1, 1, c + 7, c + 1, 3, c + 7)                                     # gate
    # sanctum
    b.room(c - 3, 0, c - 6, c + 3, 6, c - 1, [MSB, SB, 'minecraft:chiseled_stone_bricks'], [6, 2, 1])
    b.fill(c - 2, 0, c - 5, c + 2, 0, c - 2, 'minecraft:mossy_cobblestone')
    b.clear(c, 1, c - 1, c, 2, c - 1)                                             # doorway into the sanctum
    b.chest(c - 2, 1, c - 5, 'ecr_thorn_shrine', 'south')
    b.chest(c + 2, 1, c - 5, 'ecr_thorn_shrine', 'south')
    b.fill(c - 1, 1, c - 6, c + 1, 2, c - 6, 'minecraft:infested_stone_bricks')     # silverfish wall behind the chests
    b.spawner(c, 1, c - 3, 'minecraft:cave_spider', 3, 6, 3, 200, 500)
    # spike pit across the approach corridor, one bridge tile in the middle
    for z in range(c + 2, c + 5):
        for x in range(c - 1, c + 2):
            b.fill(x, -4, z, x, 0, z, AIR)
            b.put(x, -5, z, MSB)
            b.put(x, -4, z, 'minecraft:pointed_dripstone', hanging=False, dripstone_thickness='tip')
    for z in range(c + 2, c + 5):
        b.put(c, 0, z, MSB)
        b.put(c, 1, z, 'minecraft:wither_rose')
    b.put(c - 2, 0, c + 3, MSB); b.put(c + 2, 0, c + 3, MSB)
    for _ in range(18):                                                           # vines hanging on the inner wall faces
        x = b.rng.randint(c - 6, c + 6)
        z = b.rng.choice((c - 7, c + 7))
        iz = z + (1 if z == c - 7 else -1)
        if b.get(x, 2, z) is not None and b.get(x, 2, iz) is None:
            b.put(x, 2, iz, 'minecraft:vine', vine_direction_bits=4 if z == c - 7 else 1)
    for _ in range(14):
        x, z = b.rng.randint(c - 6, c + 6), b.rng.randint(c + 1, c + 6)
        if b.get(x, 1, z) is None and b.get(x, 0, z) is not None and abs(x - c) > 1:
            b.put(x, 1, z, b.rng.choice(['minecraft:fern', 'minecraft:short_grass', 'minecraft:wither_rose', 'minecraft:moss_carpet']))
    b.web(6, c - 3, 1, c - 5, c + 3, 5, c - 2)
    return b.save()


# ============================================================================== 6. FROST CAIRN  (medium - snow fort: powder-snow pit + stray spawner)
def frost_cairn():
    b = B('frost_cairn', 17, 19, 17, 7, 106)
    c = 8
    b.disc(8.0, 0, ['minecraft:snow', 'minecraft:snow', 'minecraft:grass_block'], 'minecraft:dirt', 2, 9)
    b.room(c - 6, 0, c - 6, c + 6, 6, c + 6, ['minecraft:stone_bricks', 'minecraft:packed_ice', 'minecraft:snow', 'minecraft:cracked_stone_bricks'], [4, 2, 3, 1])
    b.fill(c - 5, 0, c - 5, c + 5, 0, c + 5, 'minecraft:packed_ice')
    for L in range(5):                                                            # snow-capped dome roof
        hw = 6 - L
        b.fill(c - hw, 7 + L, c - hw, c + hw, 7 + L, c + hw, 'minecraft:snow')
    b.fill(c - 5, 6, c - 5, c + 5, 6, c + 5, 'minecraft:stone_bricks')
    b.clear(c - 4, 6, c - 4, c + 4, 6, c + 4)
    b.clear(c - 1, 1, c + 6, c + 1, 3, c + 6)                                     # entrance
    # central powder-snow pit with a stone path along the edge
    b.fill(c - 2, -5, c - 2, c + 2, 0, c + 2, 'minecraft:powder_snow')
    b.fill(c - 2, -6, c - 2, c + 2, -6, c + 2, 'minecraft:blue_ice')
    b.ring(c - 3, c - 3, c + 3, c + 3, -6, 0, ['minecraft:stone_bricks', 'minecraft:cracked_stone_bricks'], [4, 1])
    # alcoves: chests on the far side, stray spawner in a niche
    b.chest(c - 4, 1, c - 4, 'ecr_frost_cairn', 'south')
    b.chest(c + 4, 1, c - 4, 'ecr_frost_cairn', 'south')
    b.put(c, 1, c - 5, 'minecraft:packed_ice'); b.put(c, 2, c - 5, 'minecraft:packed_ice')
    b.spawner(c, 1, c - 4, 'minecraft:stray', 3, 5, 3, 250, 700)
    b.put(c + 4, 1, c + 4, 'minecraft:campfire', extinguished=True, **{'minecraft:cardinal_direction': 'north'})
    b.web(5, c - 5, 1, c - 5, c + 5, 5, c + 5)
    for (x, z) in ((c - 5, c + 5), (c + 5, c + 5)):
        for y in range(1, 4):
            b.put(x, y, z, 'minecraft:packed_ice')
    return b.save()


def build_all():
    out = {}
    for fn in (bandit_lookout, sunken_well, watch_keep, dune_vault, thorn_shrine, frost_cairn):
        out[fn.__name__] = fn()
    return out


if __name__ == '__main__':
    print(build_all())
