"""Little-endian NBT writer + .mcstructure builder + procedural structure designs."""
import struct, math, random
from common import *

VER = 18168865


# ----------------------------------------------------------------------------- NBT (bedrock, little endian)
def _s(s):
    b = s.encode('utf-8')
    return struct.pack('<H', len(b)) + b


class T:
    pass


def tag_byte(v): return (1, struct.pack('<b', v))
def tag_int(v): return (3, struct.pack('<i', v))
def tag_string(v): return (8, _s(v))
def tag_float(v): return (5, struct.pack('<f', v))
def tag_long(v): return (4, struct.pack('<q', v))


def tag_list(items, elem_type):
    """items: payload bytes already encoded for elem_type"""
    return (9, struct.pack('<bi', elem_type, len(items)) + b''.join(items))


def tag_compound(d):
    out = b''
    for k, (tid, payload) in d.items():
        out += struct.pack('<b', tid) + _s(k) + payload
    out += b'\x00'
    return (10, out)


def write_nbt(root, path):
    tid, payload = root
    data = struct.pack('<b', tid) + _s('') + payload
    ensure(path)
    with open(path, 'wb') as f:
        f.write(data)


def _state(v):
    if isinstance(v, bool):
        return tag_byte(1 if v else 0)
    if isinstance(v, int):
        return tag_int(v)
    return tag_string(v)


class Structure:
    def __init__(self, sx, sy, sz):
        self.size = (sx, sy, sz)
        self.grid = {}
        self.palette = []
        self.pal_index = {}
        self.block_data = {}   # (x,y,z) -> nbt compound for block entities

    def pid(self, name, states=None):
        key = (name, tuple(sorted((states or {}).items())))
        if key not in self.pal_index:
            self.pal_index[key] = len(self.palette)
            self.palette.append((name, states or {}))
        return self.pal_index[key]

    def set(self, x, y, z, name, states=None):
        sx, sy, sz = self.size
        if 0 <= x < sx and 0 <= y < sy and 0 <= z < sz:
            self.grid[(x, y, z)] = self.pid(name, states)

    def get(self, x, y, z):
        return self.grid.get((x, y, z))

    def save(self, path):
        sx, sy, sz = self.size
        total = sx * sy * sz
        layer0 = [-1] * total
        for (x, y, z), i in self.grid.items():
            layer0[(x * sy + y) * sz + z] = i
        layer1 = [-1] * total
        pal = []
        for name, states in self.palette:
            pal.append(tag_compound({
                'name': tag_string(name),
                'states': tag_compound({k: _state(v) for k, v in states.items()}),
                'version': tag_int(VER)})[1])
        bpd = {}
        for (x, y, z), nbt in self.block_data.items():
            idx = (x * sy + y) * sz + z
            bpd[str(idx)] = tag_compound({'block_entity_data': nbt})
        root = tag_compound({
            'format_version': tag_int(1),
            'size': tag_list([struct.pack('<i', v) for v in self.size], 3),
            'structure': tag_compound({
                'block_indices': tag_list([
                    tag_list([struct.pack('<i', v) for v in layer0], 3)[1],
                    tag_list([struct.pack('<i', v) for v in layer1], 3)[1]], 9),
                'entities': tag_list([], 10),
                'palette': tag_compound({'default': tag_compound({
                    'block_palette': tag_list(pal, 10),
                    'block_position_data': tag_compound(bpd)})}),
            }),
            'structure_world_origin': tag_list([struct.pack('<i', 0)] * 3, 3),
        })
        write_nbt(root, path)
        # record the palette so lint can validate block names + states against Mojang's data
        import json, os
        pal_dir = f'{BUILD}/structure_palettes'
        ensure(f'{pal_dir}/x')
        with open(f'{pal_dir}/{os.path.splitext(os.path.basename(path))[0]}.json', 'w') as f:
            json.dump([[n, st] for n, st in self.palette], f)
        vox_dir = f'{BUILD}/structure_voxels'
        ensure(f'{vox_dir}/x')
        with open(f'{vox_dir}/{os.path.splitext(os.path.basename(path))[0]}.json', 'w') as f:
            json.dump({'size': self.size, 'palette': [n for n, st in self.palette],
                       'voxels': [[x, y, z, i] for (x, y, z), i in self.grid.items()]}, f)


# ----------------------------------------------------------------------------- designs
def circle_pts(r):
    R = int(math.ceil(r))
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if x * x + z * z <= r * r + 0.5:
                yield x, z


def pyre_spire(path, seed=1):
    rng = random.Random(seed)
    H, R = 22, 4
    S = Structure(2 * R + 1, H + 3, 2 * R + 1)
    c = R
    # tapering cone with obsidian-like crust and molten veins
    for y in range(H):
        r = 3.9 * (1 - y / H) ** 0.85 + 0.4
        if y == 0:
            r = 4.2
        for dx, dz in circle_pts(r):
            d = math.hypot(dx, dz)
            roll = rng.random()
            edge = d > r - 1.0
            if roll < 0.06:
                S.set(c + dx, y, c + dz, 'ecr:pyrelite_ore')
            elif roll < 0.10 and not edge:
                S.set(c + dx, y, c + dz, 'minecraft:magma')
            elif roll < 0.16:
                S.set(c + dx, y, c + dz, 'minecraft:basalt', {'pillar_axis': 'y'})
            elif roll < 0.20 and y > 2:
                S.set(c + dx, y, c + dz, 'ecr:pyrelite_block')
            else:
                S.set(c + dx, y, c + dz, 'minecraft:blackstone')
    # glowing lava core line
    for y in range(2, H - 1):
        S.set(c, y, c, 'minecraft:lava') if y % 5 else S.set(c, y, c, 'minecraft:glowstone')
    # crown
    S.set(c, H, c, 'ecr:pyrelite_block')
    S.set(c, H + 1, c, 'minecraft:glowstone')
    S.set(c, H + 2, c, 'minecraft:magma')
    for (dx, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        S.set(c + dx, H - 1, c + dz, 'ecr:pyrelite_ore')
    # little satellite fangs at the base
    for (dx, dz, h) in ((4, 0, 3), (-4, 1, 4), (1, 4, 3), (-1, -4, 5), (3, 3, 2), (-3, -3, 3)):
        for y in range(h):
            S.set(c + dx, y, c + dz, 'minecraft:blackstone' if y < h - 1 else 'ecr:pyrelite_ore')
    S.save(path)
    return S.size


def eclipse_obelisk(path, seed=2):
    rng = random.Random(seed)
    H = 17
    S = Structure(7, H + 4, 7)
    c = 3
    OBS, CRY = 'minecraft:obsidian', 'minecraft:crying_obsidian'
    # stepped plinth
    for x in range(7):
        for z in range(7):
            S.set(x, 0, z, 'minecraft:end_bricks' if (x + z) % 2 else OBS)
    for x in range(1, 6):
        for z in range(1, 6):
            S.set(x, 1, z, OBS)
    for x in range(2, 5):
        for z in range(2, 5):
            S.set(x, 2, z, CRY if (x, z) != (3, 3) else 'ecr:eclipse_altar')
    # tapering shaft with carved glyph bands
    for y in range(3, H):
        half = 1 if y < H - 5 else 0
        for dx in range(-half, half + 1):
            for dz in range(-half, half + 1):
                if y % 4 == 0 and half == 1 and (abs(dx) + abs(dz)) == 1:
                    S.set(c + dx, y, c + dz, 'ecr:eclipse_altar')
                elif y % 6 == 5 and rng.random() < 0.35:
                    S.set(c + dx, y, c + dz, CRY)
                else:
                    S.set(c + dx, y, c + dz, OBS)
    # eclipsite crown + end rod antenna
    S.set(c, H, c, 'ecr:eclipsite_block')
    S.set(c, H + 1, c, 'ecr:eclipsite_block')
    for (dx, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        S.set(c + dx, H, c + dz, CRY)
    S.set(c, H + 2, c, 'minecraft:end_rod', {'facing_direction': 1})
    S.set(c, H + 3, c, 'minecraft:end_rod', {'facing_direction': 1})
    # four buttress fangs
    for (dx, dz) in ((2, 0), (-2, 0), (0, 2), (0, -2)):
        for y in range(1, 5):
            S.set(c + dx, y, c + dz, OBS)
        S.set(c + dx, 5, c + dz, CRY)
    S.save(path)
    return S.size


def eclipse_shrine(path, seed=3):
    rng = random.Random(seed)
    R = 9
    base = 5                         # ground level index (platform layer)
    S = Structure(2 * R + 1, base + 9, 2 * R + 1)
    c = R
    OBS, CRY, BR = 'minecraft:obsidian', 'minecraft:crying_obsidian', 'minecraft:end_bricks'
    for dx, dz in circle_pts(8.4):
        d = math.hypot(dx, dz)
        if d > 7.2:
            blk = BR
        elif d > 4.6:
            blk = OBS if (int(d * 2) % 2 == 0) else BR
        elif d > 2.4:
            blk = CRY if rng.random() < 0.18 else OBS
        else:
            blk = OBS
        S.set(c + dx, base, c + dz, blk)
        # root the platform into the terrain
        depth = 1 + int(max(0, (8.4 - d)) * 0.5)
        for k in range(1, min(depth, base) + 1):
            S.set(c + dx, base - k, c + dz, OBS if d < 6 else BR)
    # glowing eclipsite ring
    for k in range(24):
        a = k / 24 * math.tau
        S.set(c + int(round(math.cos(a) * 3.6)), base, c + int(round(math.sin(a) * 3.6)), 'ecr:eclipsite_block')
    # central altar
    S.set(c, base + 1, c, 'ecr:eclipse_altar')
    # four pillars
    for (sx, sz) in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        px, pz = c + 6 * sx, c + 6 * sz
        for y in range(1, 7):
            S.set(px, base + y, pz, OBS if y < 6 else CRY)
        S.set(px, base + 7, pz, 'minecraft:end_rod', {'facing_direction': 1})
        for (dx, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            S.set(px + dx, base + 1, pz + dz, BR)
    # entrance steps + loot chest behind the altar
    chest = (c, base + 1, c + 4)
    S.set(*chest, 'minecraft:chest', {'minecraft:cardinal_direction': 'north'})
    S.block_data[chest] = tag_compound({
        'id': tag_string('Chest'), 'isMovable': tag_byte(1), 'LootTable': tag_string('loot_tables/chests/ecr_eclipse_shrine.json'),
        'LootTableSeed': tag_int(0), 'x': tag_int(chest[0]), 'y': tag_int(chest[1]), 'z': tag_int(chest[2]),
        'Items': tag_list([], 10)})
    S.save(path)
    return S.size, base


def build_all():
    out = {}
    out['pyre_spire'] = pyre_spire(f'{BP}/structures/ecr/pyre_spire.mcstructure')
    out['eclipse_obelisk'] = eclipse_obelisk(f'{BP}/structures/ecr/eclipse_obelisk.mcstructure')
    out['eclipse_shrine'] = eclipse_shrine(f'{BP}/structures/ecr/eclipse_shrine.mcstructure')
    return out


if __name__ == '__main__':
    print(build_all())
