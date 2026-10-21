"""Box-based block geometry with baked rotations (no dependence on engine rotation conventions).
Coordinates are block-model space: x,z in [-8,8], y in [0,16]. Faces use world-aligned UVs on a 16x16 texture."""
from common import *

FACES = ('north', 'east', 'south', 'west', 'up', 'down')


class Box:
    def __init__(self, x0, y0, z0, x1, y1, z1, mat='*', faces=None, uvmap=None):
        self.b = [x0, y0, z0, x1, y1, z1]
        self.mat = mat                # material instance name (or dict face->name)
        self.faces = faces            # subset of faces to emit, None=all
        self.uvmap = uvmap or {}      # optional per-face (u,v,w,h) override

    def copy(self):
        return Box(*self.b, mat=self.mat, faces=self.faces, uvmap=dict(self.uvmap))

    @property
    def origin(self):
        return [self.b[0], self.b[1], self.b[2]]

    @property
    def size(self):
        return [self.b[3] - self.b[0], self.b[4] - self.b[1], self.b[5] - self.b[2]]


def rot_y(box, k):
    """rotate k quarter turns counter-clockwise seen from above: north -> west (x,z)->(z,-x)."""
    k %= 4
    x0, y0, z0, x1, y1, z1 = box.b
    nb = box.copy()
    for _ in range(k):
        x0, z0, x1, z1 = z0, -x1, z1, -x0
    nb.b = [x0, y0, z0, x1, y1, z1]
    return nb


def rot_x(box, k):
    """rotate k quarter turns about the x axis through the block centre (8 on y): up -> north for k=1."""
    k %= 4
    x0, y0, z0, x1, y1, z1 = box.b
    nb = box.copy()
    for _ in range(k):
        # centre-relative (dy,dz) -> (dz,-dy): up(+y) -> north(-z) -> down -> south
        ny0, ny1 = 8 + z0, 8 + z1
        nz0, nz1 = 8 - y1, 8 - y0
        y0, y1, z0, z1 = ny0, ny1, nz0, nz1
    nb.b = [x0, y0, z0, x1, y1, z1]
    return nb


def rot_z(box, k):
    """quarter turns about z axis: up -> east for k=1 (x,y) -> (y-8, 8-x)."""
    k %= 4
    x0, y0, z0, x1, y1, z1 = box.b
    nb = box.copy()
    for _ in range(k):
        nx0, nx1 = y0 - 8, y1 - 8
        ny0, ny1 = 8 - x1, 8 - x0
        x0, x1, y0, y1 = nx0, nx1, ny0, ny1
    nb.b = [x0, y0, z0, x1, y1, z1]
    return nb


def face_uv(b, face):
    x0, y0, z0, x1, y1, z1 = b
    sx, sy, sz = x1 - x0, y1 - y0, z1 - z0
    if face == 'north':
        return [8 - x1, 16 - y1], [sx, sy]
    if face == 'south':
        return [x0 + 8, 16 - y1], [sx, sy]
    if face == 'east':
        return [8 - z1, 16 - y1], [sz, sy]
    if face == 'west':
        return [z0 + 8, 16 - y1], [sz, sy]
    if face == 'up':
        return [x0 + 8, z0 + 8], [sx, sz]
    return [x0 + 8, 8 - z1], [sx, sz]


def clamp_uv(uv, size):
    return [max(0, min(16, uv[0])), max(0, min(16, uv[1]))], [max(0.01, min(16, size[0])), max(0.01, min(16, size[1]))]


def geometry(ident, boxes, bones=None):
    """boxes: list of Box or (bone_name, Box). Returns geometry file object."""
    by = {}
    for item in boxes:
        bn, bx = item if isinstance(item, tuple) else ('block', item)
        by.setdefault(bn, []).append(bx)
    bone_list = []
    for bn, bxs in by.items():
        cubes = []
        for bx in bxs:
            o, s = bx.origin, bx.size
            uv = {}
            for f in (bx.faces or FACES):
                if f in bx.uvmap:
                    u, sz = bx.uvmap[f][:2], bx.uvmap[f][2:]
                else:
                    u, sz = face_uv(bx.b, f)
                u, sz = clamp_uv(u, sz)
                mi = bx.mat[f] if isinstance(bx.mat, dict) else bx.mat
                uv[f] = {'uv': u, 'uv_size': sz, 'material_instance': mi}
            cubes.append({'origin': o, 'size': s, 'uv': uv})
        bone_list.append({'name': bn, 'pivot': [0, 0, 0], 'cubes': cubes})
    return {'format_version': '1.21.0', 'minecraft:geometry': [{
        'description': {'identifier': ident, 'texture_width': 16, 'texture_height': 16},
        'bones': bone_list}]}


def boxes_to_collision(boxes):
    out = []
    for bx in boxes:
        o, s = bx.origin, bx.size
        out.append({'origin': [round(o[0], 4), round(o[1], 4), round(o[2], 4)], 'size': [round(s[0], 4), round(s[1], 4), round(s[2], 4)]})
    return out
