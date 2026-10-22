"""v1.6 places of Chapters III and IV: Verse Cairns (the four verses), the Frozen Cathedral (four chimes, the Cantor's Lectern, a hidden vault),
the Fen Hut (the first half of the riddle), the Drowned Chapel (three sconces, the Marsh Altar, a flooded passage to the second half) and the Wayfarer's Cairn."""
import math
from sbuild import *

STONE, MOSSY, CRACK = 'minecraft:stone_bricks', 'minecraft:mossy_stone_bricks', 'minecraft:cracked_stone_bricks'
ICE, BLUE, SNOW = 'minecraft:packed_ice', 'minecraft:blue_ice', 'minecraft:snow'
MUD, MUDB = 'minecraft:mud', 'minecraft:mud_bricks'


def lantern(b, x, y, z, soul=False, hanging=False):
    b.put(x, y, z, 'minecraft:soul_lantern' if soul else 'minecraft:lantern', hanging=hanging)


# ----------------------------------------------------------------------------- Verse Cairn (four variants, one verse each)
def verse_cairn(v):
    b = B(f'verse_cairn_{v}', 11, 11, 11, 3, 600 + v)
    c = 5
    b.disc(5.2, 0, [SNOW, SNOW, ICE, 'minecraft:stone'], 'minecraft:dirt', 2, 7)
    b.fill(c - 1, 1, c - 1, c + 1, 1, c + 1, STONE)                                         # plinth
    b.put(c, 1, c, 'minecraft:chiseled_stone_bricks')
    b.put(c, 2, c, 'ecr:verse_stone', **{'ecr:verse': v})
    for dx, dz in ((-3, -3), (3, -3), (-3, 3), (3, 3)):                                      # four rime-covered pillars
        for y in range(1, 4):
            b.put(c + dx, y, c + dz, ICE if y < 3 else BLUE)
        lantern(b, c + dx, 4, c + dz, soul=True)
    for dx in (-3, -2, -1, 0, 1, 2, 3):                                                      # a low ring wall with gaps
        for dz in (-4, 4):
            if abs(dx) != 1:
                b.put(c + dx, 1, c + dz, MOSSY if (dx + dz) % 3 else CRACK)
    b.put(c - 2, 1, c, 'ecr:lore_tablet', **{'ecr:text': [3, 0, 1, 9][v]})
    b.chest(c + 2, 1, c, 'ecr_verse_cairn', 'west')
    return b.save()


# ----------------------------------------------------------------------------- Frozen Cathedral
def frozen_cathedral():
    S = 33
    b = B('frozen_cathedral', S, 34, S, 4, 650)
    c = 16
    b.disc(16.4, 0, [SNOW, SNOW, ICE, 'minecraft:stone'], 'minecraft:stone', 3, 12)
    b.fill(5, 0, 5, 27, 0, 27, 'minecraft:smooth_stone')                                       # nave floor
    for x in range(5, 28):
        for z in range(5, 28):
            if (x + z) % 7 == 0:
                b.put(x, 0, z, 'minecraft:polished_andesite')
    for z in range(6, 28):                                                                      # blue carpet down the aisle
        for x in (c - 1, c, c + 1):
            b.put(x, 1, z, 'minecraft:light_blue_carpet')
    # walls: 5..27, height 1..10, mixed stone / ice
    for y in range(1, 11):
        for x in range(5, 28):
            for z in (5, 27):
                b.put(x, y, z, b.rng.choices([STONE, MOSSY, CRACK, ICE, BLUE], [10, 2, 3, 3, 1])[0])
        for z in range(6, 27):
            for x in (5, 27):
                b.put(x, y, z, b.rng.choices([STONE, MOSSY, CRACK, ICE, BLUE], [10, 2, 3, 3, 1])[0])
    for y in range(4, 8):                                                                       # tall pointed windows
        for wx in (9, 13, 19, 23):
            for z in (5, 27):
                if z == 27 and wx in (13, 19):
                    continue
                b.put(wx, y, z, 'minecraft:glass_pane')
        for wz in (10, 14, 18, 22):
            for x in (5, 27):
                b.put(x, y, wz, 'minecraft:glass_pane')
    b.clear(c - 1, 1, 27, c + 1, 5, 27)                                                         # the south door and its arch
    b.put(c - 2, 6, 27, BLUE); b.put(c + 2, 6, 27, BLUE)
    for y in range(1, 6):
        b.put(c - 2, y, 27, BLUE); b.put(c + 2, y, 27, BLUE)
    b.fill(c - 1, 6, 27, c + 1, 6, 27, BLUE)
    lantern(b, c - 1, 5, 26, soul=True, hanging=True); lantern(b, c + 1, 5, 26, soul=True, hanging=True)
    # corner buttresses
    for (x, z) in ((5, 5), (27, 5), (5, 27), (27, 27)):
        for y in range(1, 13):
            b.put(x, y, z, ICE if y % 4 else BLUE)
    # roof: stepped vault of packed ice
    for k, y in enumerate(range(11, 17)):
        lo, hi = 5 + k * 2, 27 - k * 2
        if lo > hi:
            break
        for x in range(lo, hi + 1):
            for z in range(lo, hi + 1):
                if x in (lo, hi) or z in (lo, hi):
                    b.put(x, y, z, ICE if (x + z) % 3 else BLUE)
        if k == 0:
            for x in range(6, 27):
                for z in range(6, 27):
                    b.put(x, 11, z, ICE if (x + z) % 5 else BLUE)
    for x in range(11, 22):
        for z in range(11, 22):
            b.put(x, 16, z, BLUE)
    # central spire
    for y in range(12, 27):
        for dx, dz in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            b.put(c + dx, y, c + dz, STONE if y % 5 else BLUE)
    for y in range(17, 27):
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                if abs(dx) + abs(dz) == 1 or (dx == 0 and dz == 0):
                    b.put(c + dx, y, c + dz, ICE)
    b.put(c, 27, c, 'minecraft:sea_lantern')
    b.put(c, 28, c, BLUE)
    # two bell towers flank the entrance, each ending in an icy spire
    for tx in (4, 28):
        for y in range(1, 19):
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    if abs(dx) == 2 or abs(dz) == 2:
                        b.put(tx + dx, y, 28 + dz - 1, b.rng.choices([STONE, MOSSY, ICE, BLUE], [8, 2, 3, 1])[0])
                    elif y == 1:
                        b.put(tx + dx, y, 28 + dz - 1, 'minecraft:smooth_stone')
        for k in range(5):
            r = 2 - k // 2
            for dx in range(-r, r + 1):
                for dz in range(-r, r + 1):
                    b.put(tx + dx, 19 + k, 27 + dz, BLUE if k % 2 else ICE)
        b.put(tx, 24, 27, 'minecraft:sea_lantern')
        for y in range(8, 12):                                                                   # belfry openings
            b.put(tx, y, 25, 'minecraft:iron_bars'); b.put(tx, y, 29, 'minecraft:iron_bars')
    # the organ: nine pillars of calcite and ice along the north wall (the pipes that breathe the song)
    for i, x in enumerate(range(8, 25, 2)):
        h = 4 + (i if i < 5 else 8 - i) * 1
        for y in range(1, h + 4):
            b.put(x, y, 7, 'minecraft:calcite' if y < h + 3 else BLUE)
        b.put(x, h + 4, 7, 'minecraft:sea_lantern') if i % 4 == 0 else None
    b.fill(8, 1, 6, 24, 1, 6, 'minecraft:quartz_block')
    # dais with the lectern, four chimes around it - the order in space is NOT the order of the sun's road
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            b.put(c + dx, 1, c + dz, 'minecraft:quartz_block')
    b.put(c, 2, c, 'ecr:choir_lectern')
    for dx, dz, name in ((-7, -5, 'zenith'), (7, -5, 'midnight'), (-7, 5, 'dawn'), (7, 5, 'dusk')):
        b.fill(c + dx, 1, c + dz, c + dx, 1, c + dz, 'minecraft:quartz_block')
        b.put(c + dx, 2, c + dz, f'ecr:chime_{name}')
        lantern(b, c + dx, 3, c + dz, soul=True)
    for k in (-1, 1):                                                                           # pews
        for z in range(18, 26, 2):
            for x in range(c + k * 3, c + k * 7, k):
                b.put(x, 1, z, 'minecraft:spruce_slab', **{'minecraft:vertical_half': 'bottom'})
    # lore + loot
    b.put(c - 3, 2, 8, 'ecr:lore_tablet', **{'ecr:text': 9})
    b.put(c + 3, 2, 8, 'ecr:lore_tablet', **{'ecr:text': 3})
    b.chest(7, 1, 12, 'ecr_frozen_cathedral', 'east')
    b.chest(25, 1, 20, 'ecr_frozen_cathedral', 'west')
    b.spawner(7, 1, 22, f'{NS}:hoarbone', count=2, nearby=5, rng_=4, lo=300, hi=800)
    b.spawner(25, 1, 10, f'{NS}:rimewalker', count=2, nearby=5, rng_=4, lo=300, hi=800)
    b.tnt_trap(c, 0, 22, 'minecraft:smooth_stone')                                              # the aisle is mined
    # hidden vault below the NW corner: a cracked tile over a ladder shaft
    b.fill(6, -3, 6, 9, -1, 9, STONE)
    b.clear(7, -3, 7, 8, -1, 8)
    b.put(6, 0, 6, STONE)
    b.ladder(7, -3, 0, 7, 'south')
    b.put(7, 0, 8, 'minecraft:smooth_stone')
    b.put(7, 0, 7, CRACK)                                                                       # the cap that hides the shaft
    b.chest(8, -3, 8, 'ecr_frozen_cathedral_vault', 'north')
    lantern(b, 8, -2, 7, soul=True)
    return b.save()


# ----------------------------------------------------------------------------- Fen Hut
def fen_hut():
    b = B('fen_hut', 13, 14, 13, 4, 700)
    c = 6
    b.disc(6.2, 0, [MUD, MUD, 'minecraft:moss_block', 'minecraft:grass_block'], MUD, 3, 8)
    for dx, dz in ((-3, -3), (3, -3), (-3, 3), (3, 3), (0, -3), (0, 3)):                            # stilts
        for y in range(-2, 2):
            b.log(c + dx, y, c + dz, wood='mangrove')
    b.fill(c - 3, 2, c - 3, c + 3, 2, c + 3, 'minecraft:mangrove_planks')
    for y in range(3, 6):                                                                       # walls
        for d in range(-3, 4):
            for (x, z) in ((c + d, c - 3), (c + d, c + 3), (c - 3, c + d), (c + 3, c + d)):
                if b.get(x, y, z) is None:
                    b.put(x, y, z, 'minecraft:mangrove_planks')
    b.clear(c - 1, 3, c + 3, c, 4, c + 3)                                                       # door
    for y in (4,):
        for (x, z) in ((c - 3, c), (c + 3, c), (c, c - 3)):
            b.put(x, y, z, 'minecraft:glass_pane')
    for k in range(4):                                                                          # roof
        for x in range(c - 4 + k, c + 5 - k):
            for z in range(c - 4 + k, c + 5 - k):
                if x in (c - 4 + k, c + 4 - k) or z in (c - 4 + k, c + 4 - k):
                    b.put(x, 6 + k, z, 'minecraft:mangrove_planks')
    b.put(c, 9, c, 'minecraft:mangrove_planks')
    lantern(b, c, 5, c + 1, hanging=True)
    b.put(c + 2, 3, c - 2, 'ecr:lore_tablet', **{'ecr:text': 4})                              # the first half of the riddle
    b.put(c - 2, 3, c - 2, 'ecr:lore_tablet', **{'ecr:text': 6})
    b.chest(c - 2, 3, c + 2, 'ecr_fen_hut', 'east')
    for y in range(-1, 3):                                                                      # a ladder up the south side
        b.put(c + 1, y, c + 4, 'minecraft:ladder', facing_direction=2)
    return b.save()


# ----------------------------------------------------------------------------- Drowned Chapel
def drowned_chapel():
    S = 29
    b = B('drowned_chapel', S, 20, S, 6, 750)
    c = 14
    b.disc(14.2, 0, [MUD, MUD, 'minecraft:moss_block', 'minecraft:grass_block', 'minecraft:water'], MUD, 4, 6)
    for x in range(6, 23):                                                                      # nave floor
        for z in range(5, 25):
            b.put(x, 0, z, MUDB if (x + z) % 5 else 'minecraft:mossy_stone_bricks')
    for y in range(1, 8):                                                                       # walls, slowly eaten by the fen
        for x in range(6, 23):
            for z in (5, 24):
                b.put(x, y, z, b.rng.choices([MOSSY, STONE, CRACK, MUDB], [10, 3, 3, 4])[0])
        for z in range(6, 24):
            for x in (6, 22):
                b.put(x, y, z, b.rng.choices([MOSSY, STONE, CRACK, MUDB], [10, 3, 3, 4])[0])
    b.crumble(6, 5, 22, 24, 5, 7, 0.22)
    b.clear(c - 1, 1, 24, c + 1, 4, 24)                                                         # south door
    for y in range(1, 6):
        b.put(c - 2, y, 24, MOSSY); b.put(c + 2, y, 24, MOSSY)
    b.fill(c - 2, 5, 24, c + 2, 5, 24, MOSSY)
    for y in range(3, 6):
        for z in (9, 13, 17, 21):
            for x in (6, 22):
                b.put(x, y, z, 'minecraft:glass_pane')
    # three sconces on the north wall: the order in space (moon, eye, star) is not the order to light them (eye, star, moon)
    for dx, name in ((-4, 'moon'), (0, 'eye'), (4, 'star')):
        b.put(c + dx, 3, 6, f'ecr:sconce_{name}', **{'ecr:lit': 0})
        b.put(c + dx, 2, 6, STONE)
        b.put(c + dx, 1, 6, STONE)
    # altar dais
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            b.put(c + dx, 1, 9 + dz, STONE)
    b.put(c, 2, 9, 'ecr:marsh_altar')
    lantern(b, c - 2, 2, 7, hanging=False); lantern(b, c + 2, 2, 7, hanging=False)
    # the flooded pool in the SW corner leads to a hidden chamber
    for x in range(8, 13):
        for z in range(18, 23):
            for y in range(-3, 1):
                b.put(x, y, z, 'minecraft:water', liquid_depth=0)
    for x in range(7, 14):
        for z in range(17, 24):
            for y in (-4,):
                b.put(x, y, z, STONE)
    for y in range(-3, 1):                                                                       # pool walls
        for x in range(7, 14):
            for z in (17, 23):
                if b.get(x, y, z) is None:
                    b.put(x, y, z, MOSSY)
        for z in range(17, 24):
            for x in (7, 13):
                if b.get(x, y, z) is None:
                    b.put(x, y, z, MOSSY)
    for x in range(1, 8):                                                                        # the drowned tunnel going west at the bottom of the pool
        for y in (-3, -2):
            b.put(x, y, 20, 'minecraft:water', liquid_depth=0)
        for y in (-4, -1):
            for z in (19, 20, 21):
                b.put(x, y, z, STONE)
        for z in (19, 21):
            for y in (-3, -2):
                b.put(x, y, z, STONE)
    for x in range(0, 6):                                                                        # the flooded chamber: shell, water below, an air pocket above
        for z in range(17, 24):
            for y in range(-4, 1):
                shell = x in (0, 5) or z in (17, 23) or y in (-4, 0)
                b.put(x, y, z, MOSSY if shell else ('minecraft:water' if y <= -2 else AIR), **({'liquid_depth': 0} if (not shell and y <= -2) else {}))
    for y in (-3, -2):                                                                           # the tunnel meets the chamber
        b.put(5, y, 20, 'minecraft:water', liquid_depth=0)
    b.put(1, -3, 20, 'ecr:lore_tablet', **{'ecr:text': 5})                                       # the second half of the riddle, underwater
    b.chest(2, -3, 18, 'ecr_drowned_chapel_vault', 'east')
    b.put(1, -3, 22, 'ecr:lore_tablet', **{'ecr:text': 10})
    lantern(b, 3, -1, 22)                                                                        # a lantern in the air pocket
    # loot, spawners, tablets, vines
    b.chest(8, 1, 10, 'ecr_drowned_chapel', 'east')
    b.chest(20, 1, 12, 'ecr_drowned_chapel', 'west')
    b.spawner(8, 1, 14, f'{NS}:lanternbone', count=2, nearby=5, rng_=4, lo=300, hi=800)
    b.spawner(20, 1, 20, f'{NS}:mire_wisp', count=2, nearby=6, rng_=4, lo=200, hi=600)
    b.put(c + 4, 1, 12, 'ecr:lore_tablet', **{'ecr:text': 10})
    b.put(c - 4, 1, 12, 'ecr:lore_tablet', **{'ecr:text': 6})
    return b.save()


# ----------------------------------------------------------------------------- Wayfarer's Cairn
def wayfarer_cairn():
    b = B('wayfarer_cairn', 9, 8, 9, 2, 800)
    c = 4
    b.disc(4.2, 0, ['minecraft:grass_block', 'minecraft:grass_block', 'minecraft:coarse_dirt'], 'minecraft:dirt', 1, 5)
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            b.put(c + dx, 1, c + dz, 'minecraft:cobblestone' if (dx + dz) % 2 else 'minecraft:mossy_cobblestone')
    for dx in range(-1, 2):
        b.put(c + dx, 2, c, 'minecraft:mossy_cobblestone')
    b.put(c, 3, c, 'minecraft:cobblestone')
    b.put(c, 4, c, 'minecraft:lantern', hanging=False)
    b.put(c - 2, 1, c, 'ecr:lore_tablet', **{'ecr:text': 0})
    b.put(c + 2, 1, c, 'ecr:lore_tablet', **{'ecr:text': 1})
    b.put(c, 1, c + 2, 'ecr:lore_tablet', **{'ecr:text': 8})
    b.chest(c, 1, c - 2, 'ecr_wayfarer_cairn', 'south')
    return b.save()


def build_all():
    out = {}
    for v in range(4):
        out[f'verse_cairn_{v}'] = verse_cairn(v)
    out['frozen_cathedral'] = frozen_cathedral()
    out['fen_hut'] = fen_hut()
    out['drowned_chapel'] = drowned_chapel()
    out['wayfarer_cairn'] = wayfarer_cairn()
    return out


if __name__ == '__main__':
    print(build_all())
