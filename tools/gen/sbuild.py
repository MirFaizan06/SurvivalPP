"""Structure builder DSL: ground-relative coordinates (y=0 is the top ground layer), strict bounds, helpers for chests, spawners,
trap mechanisms, stairs/slabs, ruin weathering.  Also records every palette entry so lint can validate block names + states."""
import json, os, random, struct
from common import *
from structures import Structure, tag_compound, tag_string, tag_byte, tag_int, tag_list, tag_float

STRUCT_DIR = f'{BP}/structures/ecr'
PALETTE_DIR = f'{BUILD}/structure_palettes'

SB, MSB, CSB = 'minecraft:stone_bricks', 'minecraft:mossy_stone_bricks', 'minecraft:cracked_stone_bricks'
COB, MCOB = 'minecraft:cobblestone', 'minecraft:mossy_cobblestone'
AIR = 'minecraft:air'
DIRS = {'east': 0, 'west': 1, 'south': 2, 'north': 3}


def tag_short(v):
    return (2, struct.pack('<h', v))


class B:
    def __init__(self, name, sx, sy, sz, base, seed=1):
        self.name, self.base, self.sx, self.sy, self.sz = name, base, sx, sy, sz
        self.S = Structure(sx, sy, sz)
        self.rng = random.Random(seed)
        self.cx, self.cz = sx // 2, sz // 2

    # ----------------------------------------------------------------- primitives
    def put(self, x, y, z, name, **st):
        ay = self.base + y
        if not (0 <= x < self.sx and 0 <= ay < self.sy and 0 <= z < self.sz):
            raise ValueError(f'{self.name}: ({x},{y},{z}) outside {self.sx}x{self.sy}x{self.sz} (base {self.base})')
        self.S.set(x, ay, z, name, st or None)

    def get(self, x, y, z):
        return self.S.get(x, self.base + y, z)

    def fill(self, x0, y0, z0, x1, y1, z1, name, **st):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.put(x, y, z, name, **st)

    def fillr(self, x0, y0, z0, x1, y1, z1, names, weights=None):
        """random fill (weathered bricks etc.)"""
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.put(x, y, z, self.rng.choices(names, weights)[0])

    def clear(self, x0, y0, z0, x1, y1, z1):
        self.fill(x0, y0, z0, x1, y1, z1, AIR)

    def ring(self, x0, z0, x1, z1, y0, y1, names, weights=None):
        """vertical walls on the perimeter of a rectangle"""
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                for z in (z0, z1):
                    self.put(x, y, z, self.rng.choices(names, weights)[0])
            for z in range(z0 + 1, z1):
                for x in (x0, x1):
                    self.put(x, y, z, self.rng.choices(names, weights)[0])

    def room(self, x0, y0, z0, x1, y1, z1, names, weights=None):
        """solid shell (floor, ceiling, walls) with an air interior"""
        self.fillr(x0, y0, z0, x1, y1, z1, names, weights)
        self.clear(x0 + 1, y0 + 1, z0 + 1, x1 - 1, y1 - 1, z1 - 1)

    def disc(self, r, y, top, under, depth=2, clear_h=0, cx=None, cz=None):
        """natural ground disc rooted into the terrain (top block may be a list of choices)"""
        cx = self.cx if cx is None else cx
        cz = self.cz if cz is None else cz
        for x in range(self.sx):
            for z in range(self.sz):
                d = ((x - cx) ** 2 + (z - cz) ** 2) ** 0.5
                if d > r:
                    continue
                self.put(x, y, z, self.rng.choice(top) if isinstance(top, list) else top)
                for k in range(1, depth + 1 + (1 if d < r - 2 else 0)):
                    self.put(x, y - k, z, under)
                for k in range(1, min(clear_h, self.sy - 1 - self.base - y) + 1):
                    self.put(x, y + k, z, AIR)

    def crumble(self, x0, z0, x1, z1, y0, y1, chance):
        """knock random blocks out of wall rings (ruins)"""
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                for z in range(z0, z1 + 1):
                    if self.get(x, y, z) is not None and self.rng.random() < chance:
                        self.put(x, y, z, AIR)

    # ----------------------------------------------------------------- furnishing
    def stairs(self, x, y, z, mat, facing, upside=False):
        self.put(x, y, z, f'{mat}_stairs', weirdo_direction=DIRS[facing], upside_down_bit=upside)

    def slab(self, x, y, z, mat, half='bottom'):
        self.put(x, y, z, f'{mat}_slab', **{'minecraft:vertical_half': half})

    def log(self, x, y, z, wood='oak', axis='y'):
        self.put(x, y, z, f'minecraft:{wood}_log', pillar_axis=axis)

    def ladder(self, x, y0, y1, z, facing):
        for y in range(y0, y1 + 1):
            self.put(x, y, z, 'minecraft:ladder', facing_direction={'north': 2, 'south': 3, 'west': 4, 'east': 5}[facing])

    def chest(self, x, y, z, table, facing='south'):
        pos = (x, self.base + y, z)
        self.put(x, y, z, 'minecraft:chest', **{'minecraft:cardinal_direction': facing})
        self.S.block_data[pos] = tag_compound({
            'id': tag_string('Chest'), 'isMovable': tag_byte(1), 'LootTable': tag_string(f'loot_tables/chests/{table}.json'),
            'LootTableSeed': tag_int(0), 'x': tag_int(pos[0]), 'y': tag_int(pos[1]), 'z': tag_int(pos[2]), 'Items': tag_list([], 10)})

    def spawner(self, x, y, z, entity, count=3, nearby=6, rng_=4, lo=200, hi=600, player_range=16):
        pos = (x, self.base + y, z)
        self.put(x, y, z, 'minecraft:mob_spawner')
        self.S.block_data[pos] = tag_compound({
            'id': tag_string('MobSpawner'), 'isMovable': tag_byte(1), 'EntityIdentifier': tag_string(entity),
            'Delay': tag_short(20), 'MinSpawnDelay': tag_short(lo), 'MaxSpawnDelay': tag_short(hi), 'SpawnCount': tag_short(count),
            'MaxNearbyEntities': tag_short(nearby), 'RequiredPlayerRange': tag_short(player_range), 'SpawnRange': tag_short(rng_),
            'DisplayEntityHeight': tag_float(0.9), 'DisplayEntityScale': tag_float(1.0), 'DisplayEntityWidth': tag_float(0.8),
            'x': tag_int(pos[0]), 'y': tag_int(pos[1]), 'z': tag_int(pos[2])})

    def tnt_trap(self, x, y, z, floor=SB, full=False):
        """pressure plate at (x,y,z) on a floor block, TNT two layers below (a pressure plate strongly powers the block it sits on,
        which activates the TNT touching it - the desert-temple mechanism). `full` = 3x3 TNT, otherwise a plus."""
        self.put(x, y - 1, z, floor)
        self.put(x, y, z, 'minecraft:stone_pressure_plate', redstone_signal=0)
        cells = [(dx, dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1)] if full else [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dz in cells:
            self.put(x + dx, y - 2, z + dz, 'minecraft:tnt')
            if dx or dz:
                self.put(x + dx, y - 1, z + dz, floor)
        for dx in (-2, -1, 0, 1, 2):
            for dz in (-2, -1, 0, 1, 2):
                if self.get(x + dx, y - 2, z + dz) is None:
                    self.put(x + dx, y - 2, z + dz, floor)

    def web(self, n, x0, y0, z0, x1, y1, z1):
        placed = 0
        for _ in range(n * 6):
            x, y, z = self.rng.randint(x0, x1), self.rng.randint(y0, y1), self.rng.randint(z0, z1)
            if self.get(x, y, z) == self.S.pid(AIR):
                self.put(x, y, z, 'minecraft:web')
                placed += 1
                if placed >= n:
                    break

    # ----------------------------------------------------------------- output
    def save(self):
        path = f'{STRUCT_DIR}/{self.name}.mcstructure'
        self.S.save(path)
        ensure(f'{PALETTE_DIR}/{self.name}.json')
        with open(f'{PALETTE_DIR}/{self.name}.json', 'w') as f:
            json.dump([[n, s] for n, s in self.S.palette], f)
        return (self.sx, self.sy, self.sz), self.base
