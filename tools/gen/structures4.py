"""Adventure structures, part 2 - HARD: Highland Bastion (mountains), Sunken Crypt (underground), Pyre Bastion (Nether), Eclipse Vault (End)."""
import math
from sbuild import *

STONE_MIX = [SB, MSB, CSB, 'minecraft:andesite']


# ============================================================================== 7. HIGHLAND BASTION
def highland_bastion():
    b = B('highland_bastion', 33, 23, 33, 6, 107)
    c = 16
    b.fill(c - 15, -6, c - 15, c + 15, -1, c + 15, 'minecraft:stone')
    b.disc(16.5, 0, ['minecraft:stone', 'minecraft:gravel', 'minecraft:andesite', 'minecraft:grass_block', 'minecraft:cobblestone'], 'minecraft:stone', 2, 16)
    b.fillr(c - 13, 0, c - 13, c + 13, 0, c + 13, [COB, 'minecraft:gravel', SB, MCOB, 'minecraft:coarse_dirt'], [4, 2, 3, 2, 1])
    # curtain wall
    b.ring(c - 14, c - 14, c + 14, c + 14, 1, 8, STONE_MIX, [6, 3, 2, 2])
    for k in range(-14, 15):
        if k % 2 == 0:
            for (x, z) in ((c + k, c - 14), (c + k, c + 14), (c - 14, c + k), (c + 14, c + k)):
                b.put(x, 9, z, SB)
    b.crumble(c - 14, c - 14, c + 14, c + 14, 6, 9, 0.18)
    b.clear(c - 1, 1, c + 14, c + 1, 5, c + 14)                                  # gate
    for dx in (-1, 0, 1):
        b.put(c + dx, 6, c + 14, 'minecraft:iron_bars')
        b.put(c + dx, 7, c + 14, 'minecraft:iron_bars')
    # four towers
    spawns = {(-1, -1): 'ecr:revenant', (1, -1): 'ecr:revenant', (-1, 1): 'ecr:gravewalker', (1, 1): None}
    for (sx, sz), ent in spawns.items():
        x0 = c - 14 if sx < 0 else c + 8
        z0 = c - 14 if sz < 0 else c + 8
        b.room(x0, 0, z0, x0 + 6, 14, z0 + 6, STONE_MIX, [6, 3, 2, 2])
        b.fill(x0, 7, z0, x0 + 6, 7, z0 + 6, SB)                                # upper floor
        b.fill(x0, 14, z0, x0 + 6, 14, z0 + 6, SB)                              # roof platform
        b.clear(x0 + 1, 8, z0 + 1, x0 + 5, 13, z0 + 5)
        lx = x0 + 1 if sx < 0 else x0 + 5
        b.ladder(lx, 1, 14, z0 + 3, 'east' if sx < 0 else 'west')
        b.clear(lx, 7, z0 + 3, lx, 7, z0 + 3)
        b.clear(lx, 14, z0 + 3, lx, 14, z0 + 3)
        door_x = x0 + 6 if sx < 0 else x0
        b.clear(door_x, 1, z0 + 3, door_x, 2, z0 + 3)
        for (x, z) in ((x0, z0), (x0 + 6, z0), (x0, z0 + 6), (x0 + 6, z0 + 6)):
            b.put(x, 15, z, SB)
        for k in range(0, 7, 2):
            for (x, z) in ((x0 + k, z0), (x0 + k, z0 + 6), (x0, z0 + k), (x0 + 6, z0 + k)):
                b.put(x, 15, z, SB)
        if ent:
            b.spawner(x0 + 3, 1, z0 + 3, ent, 3, 6, 4, 220, 600)
            b.chest(x0 + 3, 8, z0 + 4, 'ecr_highland_bastion_tower', 'north')
        else:
            b.chest(x0 + 3, 15, z0 + 3, 'ecr_highland_bastion_tower', 'north')
        b.web(3, x0 + 1, 1, z0 + 1, x0 + 5, 6, z0 + 5)
    # central keep
    b.room(c - 6, 0, c - 6, c + 6, 12, c + 6, STONE_MIX, [6, 3, 2, 1])
    b.fill(c - 5, 0, c - 5, c + 5, 0, c + 5, 'minecraft:polished_andesite')
    b.fill(c - 5, 6, c - 5, c + 5, 6, c + 5, 'minecraft:spruce_planks')
    b.clear(c - 5, 7, c - 5, c + 5, 11, c + 5)
    for k in range(-6, 7, 2):
        for (x, z) in ((c + k, c - 6), (c + k, c + 6), (c - 6, c + k), (c + 6, c + k)):
            b.put(x, 13, z, SB) if 0 <= x < 33 and 0 <= z < 33 else None
    b.clear(c - 1, 1, c + 6, c + 1, 3, c + 6)                                    # keep entrance
    # vestibule with the trap plates
    b.ring(c - 2, c + 1, c + 2, c + 6, 1, 5, [SB, MSB])
    b.clear(c - 1, 1, c + 2, c + 1, 5, c + 5)
    b.clear(c, 1, c + 1, c, 3, c + 1)                                            # doorway to the hall
    b.tnt_trap(c, 1, c + 4, SB, full=True)
    b.tnt_trap(c, 1, c + 2, SB, full=False)
    # hall + loot
    b.chest(c - 3, 1, c - 5, 'ecr_highland_bastion', 'south'); b.chest(c + 3, 1, c - 5, 'ecr_highland_bastion', 'south')
    for x in (c - 5, c + 5):
        for y in (1, 2, 3):
            b.put(x, y, c - 2, 'minecraft:bookshelf')
    b.web(8, c - 5, 1, c - 5, c + 5, 5, c)
    # second floor: ladder from the hall corner, two more chests + a spawner
    b.ladder(c + 5, 1, 6, c - 4, 'west')
    b.clear(c + 5, 6, c - 4, c + 5, 6, c - 4)
    b.chest(c - 4, 7, c - 5, 'ecr_highland_bastion', 'south'); b.chest(c, 7, c - 5, 'ecr_highland_bastion', 'south')
    b.spawner(c - 4, 7, c + 3, 'ecr:revenant', 3, 6, 3, 200, 550)
    # lava vault below the hall
    b.room(c - 5, -5, c - 5, c + 5, 0, c + 1, [SB, 'minecraft:infested_stone_bricks', CSB], [5, 1, 2])
    b.fill(c - 4, -4, c - 4, c + 4, -4, c, SB)
    b.fill(c - 4, -3, c - 4, c + 4, -1, c, AIR)
    b.fill(c - 3, -4, c - 3, c + 3, -4, c - 1, 'minecraft:lava')                 # lava lake, safe path along the north row
    b.fill(c - 4, 0, c - 4, c - 4, 0, c - 4, AIR)
    b.ladder(c - 4, -3, 0, c - 4, 'east')
    b.tnt_trap(c + 2, -3, c - 4, SB, full=False)
    b.chest(c + 4, -3, c - 4, 'ecr_highland_bastion_vault', 'south')
    b.spawner(c + 4, -3, c, 'ecr:cave_weaver', 2, 4, 2, 260, 700)
    b.web(5, c - 4, -3, c - 4, c + 4, -1, c)
    # courtyard dressing
    for (x, z) in ((c - 9, c + 8), (c + 9, c + 8), (c - 10, c - 2), (c + 10, c - 2)):
        b.put(x, 1, z, 'minecraft:barrel', facing_direction=1, open_bit=False)
        b.put(x + 1, 1, z, 'minecraft:hay_block', pillar_axis='y', deprecated=0)
    b.put(c - 9, 1, c + 4, 'minecraft:campfire', extinguished=True, **{'minecraft:cardinal_direction': 'south'})
    return b.save()


# ============================================================================== 8. SUNKEN CRYPT  (placed underground)
def sunken_crypt():
    b = B('sunken_crypt', 27, 12, 27, 0, 108)
    c = 13
    DS = ['minecraft:deepslate', 'minecraft:cobbled_deepslate', 'minecraft:deepslate_bricks', 'minecraft:tuff', 'minecraft:cracked_deepslate_bricks']
    W = [4, 3, 3, 1, 2]
    b.fillr(0, 0, 0, 26, 11, 26, DS, W)
    # main hall
    b.clear(c - 2, 2, 3, c + 2, 6, 24)
    b.fill(c - 2, 1, 3, c + 2, 1, 24, 'minecraft:polished_deepslate')
    for z in range(4, 24, 4):                                                    # pillars with soul lanterns
        for x in (c - 2, c + 2):
            b.fill(x, 2, z, x, 6, z, 'minecraft:deepslate_bricks')
        b.put(c - 1, 6, z, 'minecraft:soul_lantern', hanging=True)
        b.put(c + 1, 6, z, 'minecraft:soul_lantern', hanging=True)
    # entrance tunnel (gravel plug to the outside)
    b.clear(c, 2, 24, c, 4, 26)
    b.fill(c, 2, 25, c, 4, 26, 'minecraft:gravel')
    # side chambers
    chambers = [((-1, 7), 'ecr:cave_weaver'), ((1, 7), 'ecr:revenant'), ((-1, 19), None), ((1, 19), 'ecr:gravewalker')]
    for (sx, zc), ent in chambers:
        x0, x1 = (c - 11, c - 5) if sx < 0 else (c + 5, c + 11)
        b.clear(x0 + 1, 2, zc - 3, x1 - 1, 6, zc + 3)
        b.fill(x0 + 1, 1, zc - 3, x1 - 1, 1, zc + 3, 'minecraft:deepslate_tiles')
        arch_x = c - 3 if sx < 0 else c + 3
        b.clear(arch_x, 2, zc - 1, arch_x, 4, zc + 1)
        cx_ = (x0 + x1) // 2
        # sarcophagi + bones
        b.fill(cx_ - 1, 2, zc - 2, cx_ + 1, 2, zc - 2, 'minecraft:bone_block')
        b.slab(cx_, 3, zc - 2, 'minecraft:cobbled_deepslate')
        b.put(cx_ - 2, 2, zc + 2, 'minecraft:bone_block')
        if ent:
            b.spawner(cx_, 2, zc, ent, 3, 6, 3, 200, 560)
        far_x = (x0 + 1) if sx < 0 else (x1 - 1)
        b.chest(far_x, 2, zc, 'ecr_sunken_crypt', 'east' if sx < 0 else 'west')
        b.put(cx_, 6, zc, 'minecraft:soul_lantern', hanging=True)
        b.web(5, x0 + 1, 2, zc - 3, x1 - 1, 6, zc + 3)
    # silverfish-walled armoury (SW chamber): hidden extra chest
    b.fill(c - 11, 2, 18, c - 11, 3, 20, 'minecraft:infested_deepslate')
    b.fill(c - 12, 2, 18, c - 12, 3, 20, AIR)
    b.chest(c - 12, 2, 19, 'ecr_sunken_crypt_hidden', 'east')
    # treasure dais with a lava moat at the north end
    b.clear(c - 3, 2, 1, c + 3, 6, 3)
    b.fill(c - 3, 1, 1, c + 3, 1, 3, 'minecraft:lava')
    b.fill(c - 1, 1, 1, c + 1, 1, 2, 'minecraft:polished_deepslate')
    b.fill(c, 1, 3, c, 1, 3, 'minecraft:polished_deepslate')
    b.fill(c - 2, 1, 3, c - 2, 1, 3, 'minecraft:polished_deepslate'); b.fill(c + 2, 1, 3, c + 2, 1, 3, 'minecraft:polished_deepslate')
    b.chest(c, 2, 1, 'ecr_sunken_crypt_vault', 'south')
    b.fill(c - 1, 2, 2, c + 1, 2, 2, AIR)
    # trap plates in the hall
    b.tnt_trap(c, 2, 10, 'minecraft:polished_deepslate', full=True)
    b.tnt_trap(c, 2, 16, 'minecraft:polished_deepslate', full=True)
    b.tnt_trap(c, 2, 6, 'minecraft:polished_deepslate', full=False)
    b.web(14, c - 2, 2, 5, c + 2, 6, 23)
    for _ in range(10):
        x, z = c + b.rng.choice((-2, -1, 1, 2)), b.rng.randint(5, 22)
        if b.get(x, 2, z) == b.S.pid(AIR):
            b.put(x, 2, z, 'minecraft:bone_block')
    return b.save()


# ============================================================================== 9. PYRE BASTION  (Nether)
def pyre_bastion():
    b = B('pyre_bastion', 29, 18, 29, 5, 109)
    c = 14
    BS, PBB, CPB = 'minecraft:blackstone', 'minecraft:polished_blackstone_bricks', 'minecraft:cracked_polished_blackstone_bricks'
    NB = 'minecraft:nether_brick'
    b.fill(c - 13, -5, c - 13, c + 13, -1, c + 13, BS)
    b.fillr(c - 13, 0, c - 13, c + 13, 0, c + 13, [BS, PBB, CPB, 'minecraft:magma', 'minecraft:soul_soil'], [6, 4, 2, 1, 1])
    b.clear(c - 13, 1, c - 13, c + 13, 12, c + 13)
    # lava moat (2 wide) with a south bridge
    for ring_r in (11, 12):
        for k in range(-ring_r, ring_r + 1):
            for (x, z) in ((c + k, c - ring_r), (c + k, c + ring_r), (c - ring_r, c + k), (c + ring_r, c + k)):
                b.put(x, 0, z, 'minecraft:lava')
    for z in range(c + 10, c + 14):
        for x in range(c - 1, c + 2):
            b.put(x, 0, z, NB)
    # inner wall
    b.ring(c - 9, c - 9, c + 9, c + 9, 1, 5, [PBB, BS, CPB, 'minecraft:gilded_blackstone'], [6, 4, 2, 1])
    b.crumble(c - 9, c - 9, c + 9, c + 9, 3, 5, 0.2)
    b.clear(c - 1, 1, c + 9, c + 1, 4, c + 9)
    # corner obelisks
    for sx in (-1, 1):
        for sz in (-1, 1):
            ox, oz = c + sx * 9, c + sz * 9
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    for y in range(1, 11):
                        if abs(dx) + abs(dz) <= 1 or y < 6:
                            b.put(ox + dx, y, oz + dz, PBB if y % 4 else 'minecraft:gilded_blackstone')
            b.put(ox, 11, oz, 'minecraft:magma'); b.put(ox, 12, oz, 'minecraft:glowstone')
    # keep
    b.room(c - 5, 0, c - 5, c + 5, 8, c + 5, [PBB, BS, CPB], [6, 4, 2])
    b.clear(c - 1, 1, c + 5, c + 1, 3, c + 5)
    b.fill(c - 4, 0, c - 4, c + 4, 0, c + 4, 'minecraft:polished_blackstone')
    for dx in range(-4, 5):                                                       # lava ring around a central island
        for dz in range(-4, 5):
            d = max(abs(dx), abs(dz))
            if d in (3, 4) and not (dx == 0 and dz > 0):
                b.put(c + dx, 0, c + dz, 'minecraft:lava')
    for z in range(c + 3, c + 5):                                                 # bridge tiles
        b.put(c, 0, z, NB)
    b.chest(c, 1, c - 1, 'ecr_pyre_bastion_core', 'south')
    b.put(c, 1, c, 'minecraft:gilded_blackstone')
    b.chest(c - 3, 1, c - 4, 'ecr_pyre_bastion', 'south'); b.chest(c + 3, 1, c - 4, 'ecr_pyre_bastion', 'south')
    b.spawner(c - 4, 1, c + 1, 'ecr:ashen_warg', 2, 4, 3, 220, 600)
    b.spawner(c + 4, 1, c + 1, 'ecr:ashen_warg', 2, 4, 3, 220, 600)
    b.spawner(c, 1, c - 4, 'minecraft:wither_skeleton', 2, 4, 3, 300, 800)
    # trap plates on the approach to the keep
    b.tnt_trap(c, 1, c + 7, 'minecraft:polished_blackstone', full=True)
    for _ in range(14):
        x, z = c + b.rng.randint(-8, 8), c + b.rng.randint(-8, 8)
        if b.get(x, 1, z) is None and b.get(x, 0, z) is not None and abs(x - c) > 5:
            b.put(x, 1, z, b.rng.choice(['minecraft:magma', 'minecraft:soul_sand', 'minecraft:blackstone']))
    return b.save()


# ============================================================================== 10. ECLIPSE VAULT  (The End)
def eclipse_vault():
    b = B('eclipse_vault', 25, 17, 25, 6, 110)
    c = 12
    OBS, CRY, EB = 'minecraft:obsidian', 'minecraft:crying_obsidian', 'minecraft:end_bricks'
    b.fill(c - 12, -6, c - 12, c + 12, -1, c + 12, 'minecraft:end_stone')
    b.disc(12.2, 0, [EB, 'minecraft:end_stone', EB, 'minecraft:purpur_block'], 'minecraft:end_stone', 2, 10)
    for k in range(8):                                                            # pillar ring
        a = k / 8 * math.tau
        px, pz = c + int(round(math.cos(a) * 10)), c + int(round(math.sin(a) * 10))
        for y in range(1, 8):
            b.put(px, y, pz, OBS if y < 7 else CRY)
        b.put(px, 8, pz, 'minecraft:end_rod', facing_direction=1)
    # vault chamber
    b.room(c - 7, -6, c - 7, c + 7, 0, c + 7, [OBS, EB, CRY], [6, 4, 1])
    b.fill(c - 6, -5, c - 6, c + 6, -5, c + 6, 'minecraft:purpur_block')
    for ring in range(8):
        a = ring / 8 * math.tau
        b.put(c + int(round(math.cos(a) * 3)), -5, c + int(round(math.sin(a) * 3)), 'ecr:eclipsite_block')
    b.fill(c - 1, -5, c - 1, c + 1, -5, c + 1, OBS)
    b.put(c, -4, c, 'ecr:eclipse_altar')
    # entrance hut + ladder shaft
    b.room(c - 2, 0, c + 7, c + 2, 4, c + 11, [OBS, EB], [3, 2])
    b.clear(c - 1, 1, c + 8, c + 1, 3, c + 10)
    b.fill(c, -4, c + 9, c, 0, c + 9, AIR)
    for y in range(-4, 1):
        for (x, z) in ((c - 1, c + 9), (c + 1, c + 9), (c, c + 10)):
            b.put(x, y, z, EB)
    b.fill(c, 1, c + 10, c, 3, c + 10, EB)
    b.ladder(c, -4, 3, c + 9, 'north')
    b.clear(c, -4, c + 8, c, -3, c + 8)                                           # tunnel north into the vault
    b.clear(c, -4, c + 7, c, -3, c + 7)
    b.clear(c, 0, c + 9, c, 0, c + 9)
    # contents
    b.chest(c - 5, -4, c, 'ecr_eclipse_vault', 'east'); b.chest(c + 5, -4, c, 'ecr_eclipse_vault', 'west')
    b.chest(c, -4, c - 5, 'ecr_eclipse_vault_core', 'south')
    b.put(c - 1, -4, c - 5, CRY); b.put(c + 1, -4, c - 5, CRY)
    b.spawner(c - 5, -4, c - 5, 'ecr:voidweaver', 2, 4, 3, 260, 700)
    b.spawner(c + 5, -4, c - 5, 'ecr:voidweaver', 2, 4, 3, 260, 700)
    b.spawner(c, -4, c + 5, 'minecraft:endermite', 3, 6, 3, 200, 500)
    b.tnt_trap(c, -4, c + 3, 'minecraft:purpur_block', full=True)
    b.tnt_trap(c - 3, -4, c, 'minecraft:purpur_block', full=False)
    b.tnt_trap(c + 3, -4, c, 'minecraft:purpur_block', full=False)
    return b.save()


def build_all():
    out = {}
    for fn in (highland_bastion, sunken_crypt, pyre_bastion, eclipse_vault):
        out[fn.__name__] = fn()
    return out


if __name__ == '__main__':
    print(build_all())
