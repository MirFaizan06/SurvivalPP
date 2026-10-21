"""Tiny Blockbench-style toolchain: build Bedrock geometry from code, auto-UV (box UV), paint the
texture procedurally, export geometry JSON + TGA, and render previews with a software rasteriser."""
import math, random, json
import numpy as np
from PIL import Image
from common import *

FACES = ['north', 'east', 'south', 'west', 'up', 'down']


class Cube:
    def __init__(self, bone, origin, size, mat, inflate=0.0, rot=None, pivot=None, mirror=False, params=None, glow=0.0):
        self.bone = bone
        self.origin = tuple(float(v) for v in origin)
        self.size = tuple(float(v) for v in size)
        self.mat = mat
        self.inflate = inflate
        self.rot = rot
        self.pivot = pivot
        self.mirror = mirror
        self.params = params or {}
        self.glow = glow
        self.uv = None

    @property
    def isz(self):
        return tuple(max(1, int(math.ceil(v - 1e-6))) for v in self.size)

    def rect_size(self):
        sx, sy, sz = self.isz
        return 2 * (sx + sz), sy + sz

    def face_rects(self):
        """(x,y,w,h) of each face in texture space for box UV."""
        u, v = self.uv
        sx, sy, sz = self.isz
        return {
            'up': (u + sz, v, sx, sz),
            'down': (u + sz + sx, v, sx, sz),
            'east': (u, v + sz, sz, sy),
            'north': (u + sz, v + sz, sx, sy),
            'west': (u + sz + sx, v + sz, sz, sy),
            'south': (u + sz + sx + sz, v + sz, sx, sy),
        }


class Model:
    def __init__(self, ident, tw, th, bounds=(4, 4, (0, 1, 0))):
        self.ident = ident
        self.tw, self.th = tw, th
        self.bones = {}
        self.order = []
        self.cubes = []
        self.bounds = bounds

    def bone(self, name, parent=None, pivot=(0, 0, 0), rot=None):
        self.bones[name] = dict(name=name, parent=parent, pivot=tuple(float(p) for p in pivot), rot=rot)
        self.order.append(name)
        return name

    def cube(self, bone, origin, size, mat, **kw):
        c = Cube(bone, origin, size, mat, **kw)
        self.cubes.append(c)
        return c

    # ------------------------------------------------------------- UV packing
    def pack(self):
        items = sorted(self.cubes, key=lambda c: (-c.rect_size()[1], -c.rect_size()[0]))
        occ = np.zeros((self.th, self.tw), dtype=bool)
        for c in items:
            w, h = c.rect_size()
            placed = False
            for y in range(0, self.th - h + 1):
                row_free = True
                x = 0
                while x <= self.tw - w:
                    blk = occ[y:y + h, x:x + w]
                    if not blk.any():
                        occ[y:y + h, x:x + w] = True
                        c.uv = (x, y)
                        placed = True
                        break
                    # skip past the first blocking column
                    cols = np.where(blk.any(axis=0))[0]
                    x += int(cols[-1]) + 1
                if placed:
                    break
            if not placed:
                raise RuntimeError(f'texture {self.tw}x{self.th} too small for {self.ident} (cube {c.mat} {c.size})')
        used = occ.sum() / occ.size
        return used

    # ------------------------------------------------------------- export
    def export(self):
        bones = []
        by_bone = {}
        for c in self.cubes:
            by_bone.setdefault(c.bone, []).append(c)
        for name in self.order:
            b = self.bones[name]
            d = {'name': name}
            if b['parent']:
                d['parent'] = b['parent']
            d['pivot'] = list(b['pivot'])
            if b['rot']:
                d['rotation'] = list(b['rot'])
            cubes = []
            for c in by_bone.get(name, []):
                cd = {'origin': list(c.origin), 'size': list(c.size), 'uv': list(c.uv)}
                if c.inflate:
                    cd['inflate'] = c.inflate
                if c.rot:
                    cd['pivot'] = list(c.pivot or [c.origin[0] + c.size[0] / 2, c.origin[1] + c.size[1] / 2, c.origin[2] + c.size[2] / 2])
                    cd['rotation'] = list(c.rot)
                if c.mirror:
                    cd['mirror'] = True
                cubes.append(cd)
            if cubes:
                d['cubes'] = cubes
            bones.append(d)
        bw, bh, bo = self.bounds
        return {
            'format_version': '1.12.0',
            'minecraft:geometry': [{
                'description': {
                    'identifier': self.ident, 'texture_width': self.tw, 'texture_height': self.th,
                    'visible_bounds_width': bw, 'visible_bounds_height': bh, 'visible_bounds_offset': list(bo)},
                'bones': bones}]}

    # ------------------------------------------------------------- painting
    def paint(self, mats, seed=1):
        """mats: dict name -> callable(ctx) -> (r,g,b,a, glow) ; returns (base RGBA image, glow RGBA overlay)"""
        base = Image.new('RGBA', (self.tw, self.th), (0, 0, 0, 0))
        glow = Image.new('RGBA', (self.tw, self.th), (0, 0, 0, 0))
        bpx, gpx = base.load(), glow.load()
        for ci, c in enumerate(self.cubes):
            fn = mats[c.mat]
            sx, sy, sz = c.isz
            ox, oy, oz = c.origin
            fx, fy, fz = c.size
            rects = c.face_rects()
            for face, (x0, y0, w, h) in rects.items():
                for j in range(h):
                    for i in range(w):
                        # 3D position of the texel centre on the surface (cube-local, 0..size)
                        a = (i + 0.5) / w
                        b = (j + 0.5) / h
                        if face == 'north':
                            P = (fx * (1 - a), fy * (1 - b), 0.0)
                        elif face == 'south':
                            P = (fx * a, fy * (1 - b), fz)
                        elif face == 'east':
                            P = (fx, fy * (1 - b), fz * (1 - a))
                        elif face == 'west':
                            P = (0.0, fy * (1 - b), fz * a)
                        elif face == 'up':
                            P = (fx * (1 - a), fy, fz * (1 - b))
                        else:
                            P = (fx * (1 - a), 0.0, fz * b)
                        ctx = Ctx(c, face, i, j, w, h, P, (ox + P[0], oy + P[1], oz + P[2]), ci, seed)
                        r, g, bl, al, gl = fn(ctx)
                        px = x0 + i
                        py = y0 + j
                        if 0 <= px < self.tw and 0 <= py < self.th:
                            bpx[px, py] = (int(r), int(g), int(bl), int(al))
                            if gl > 0:
                                gpx[px, py] = (int(r), int(g), int(bl), int(min(255, gl)))
        return base, glow

    def pixel_density_check(self):
        return {c.mat: 0 for c in self.cubes}


class Ctx:
    __slots__ = ('cube', 'face', 'i', 'j', 'w', 'h', 'P', 'W', 'idx', 'seed')

    def __init__(self, cube, face, i, j, w, h, P, W, idx, seed):
        self.cube, self.face, self.i, self.j, self.w, self.h = cube, face, i, j, w, h
        self.P, self.W, self.idx, self.seed = P, W, idx, seed

    @property
    def edge(self):
        """distance (in texels) to the nearest face border, plus which border"""
        d = {'l': self.i, 'r': self.w - 1 - self.i, 't': self.j, 'b': self.h - 1 - self.j}
        k = min(d, key=d.get)
        return d[k], k


# ------------------------------------------------------------- 3D value noise
_perm = np.random.RandomState(1234).randint(0, 256, 512)
_vals = np.random.RandomState(4321).rand(256)


def _h(ix, iy, iz, s):
    return _vals[(_perm[(_perm[(_perm[(ix + s) & 255] + iy) & 255] + iz) & 255]) & 255]


def noise3(x, y, z, s=0):
    ix, iy, iz = math.floor(x), math.floor(y), math.floor(z)
    fx, fy, fz = x - ix, y - iy, z - iz
    fx, fy, fz = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy), fz * fz * (3 - 2 * fz)
    def L(a, b, t): return a + (b - a) * t
    c000 = _h(ix, iy, iz, s); c100 = _h(ix + 1, iy, iz, s)
    c010 = _h(ix, iy + 1, iz, s); c110 = _h(ix + 1, iy + 1, iz, s)
    c001 = _h(ix, iy, iz + 1, s); c101 = _h(ix + 1, iy, iz + 1, s)
    c011 = _h(ix, iy + 1, iz + 1, s); c111 = _h(ix + 1, iy + 1, iz + 1, s)
    return L(L(L(c000, c100, fx), L(c010, c110, fx), fy), L(L(c001, c101, fx), L(c011, c111, fx), fy), fz)


def fbm3(p, s=0, scale=0.25, oct=3):
    v, a, tot = 0.0, 1.0, 0.0
    f = scale
    for k in range(oct):
        v += noise3(p[0] * f, p[1] * f, p[2] * f, s + k * 17) * a
        tot += a; a *= 0.5; f *= 2.1
    return v / tot


GAIN = 1.0
FACE_LIGHT = {'up': 1.12, 'north': 1.0, 'south': 0.9, 'east': 0.84, 'west': 0.96, 'down': 0.7}


# ------------------------------------------------------------- software renderer
def rotm(rx, ry, rz):
    """Bedrock convention (as used by Blockbench): x and y negated, applied z*y*x."""
    rx, ry, rz = -math.radians(rx), -math.radians(ry), math.radians(rz)
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def bone_matrices(model, pose=None):
    """world transform (R, t) for each bone: p_world = R @ (p - pivot) + pivot + T, chained to parents."""
    pose = pose or {}
    mats = {}
    def get(name):
        if name in mats:
            return mats[name]
        b = model.bones[name]
        rot = list(b['rot'] or [0, 0, 0])
        tr = [0.0, 0.0, 0.0]
        p = pose.get(name)
        if p:
            rot = [rot[i] + p.get('rot', [0, 0, 0])[i] for i in range(3)]
            tr = list(p.get('pos', [0, 0, 0]))
        R = rotm(*rot)
        piv = np.array(b['pivot'], float)
        # local: x -> R(x - piv) + piv + tr
        A = R
        t = piv - R @ piv + np.array(tr, float)
        if b['parent']:
            PA, Pt = get(b['parent'])
            A2 = PA @ A
            t2 = PA @ t + Pt
            mats[name] = (A2, t2)
        else:
            mats[name] = (A, t)
        return mats[name]
    for n in model.order:
        get(n)
    return mats


def cube_faces(c):
    """corner quads for each face in cube-local model space with (s,t) texture coords 0..1 (matching paint())."""
    inf = c.inflate
    x0, y0, z0 = c.origin[0] - inf, c.origin[1] - inf, c.origin[2] - inf
    x1, y1, z1 = c.origin[0] + c.size[0] + inf, c.origin[1] + c.size[1] + inf, c.origin[2] + c.size[2] + inf
    # each face: list of 4 vertices ordered (a,b)=(0,0),(1,0),(1,1),(0,1)  where a=i/w, b=j/h
    return {
        'north': [(x1, y1, z0), (x0, y1, z0), (x0, y0, z0), (x1, y0, z0)],
        'south': [(x0, y1, z1), (x1, y1, z1), (x1, y0, z1), (x0, y0, z1)],
        'east': [(x1, y1, z1), (x1, y1, z0), (x1, y0, z0), (x1, y0, z1)],
        'west': [(x0, y1, z0), (x0, y1, z1), (x0, y0, z1), (x0, y0, z0)],
        'up': [(x1, y1, z1), (x0, y1, z1), (x0, y1, z0), (x1, y1, z0)],
        'down': [(x1, y0, z0), (x0, y0, z0), (x0, y0, z1), (x1, y0, z1)],
    }


def render(model, tex, out, yaw=35, pitch=20, scale=6, size=(640, 640), pose=None, bg=(46, 46, 52), glow=None, center=None, shade=True, rgba=False, ycen=0.62, unlit=False):
    W, H = size
    img = np.zeros((H, W, 3), np.float32) + np.array(bg, np.float32)
    zb = np.full((H, W), 1e9, np.float32)
    texa = np.array(tex.convert('RGBA'))
    mats = bone_matrices(model, pose)
    ya, pa = math.radians(yaw), math.radians(pitch)
    # camera rotation: world -> view (yaw about Y, pitch about X); model front is -Z, camera looks at it from -Z side by default
    cy, sy_ = math.cos(ya), math.sin(ya)
    cp, sp = math.cos(pa), math.sin(pa)
    Ry = np.array([[cy, 0, sy_], [0, 1, 0], [-sy_, 0, cy]])
    Rp = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]])
    V = Rp @ Ry
    cen = np.array(center if center is not None else [0, model.bounds[1] * 8, 0], float)
    light = np.array([-0.4, 0.8, -0.5]); light /= np.linalg.norm(light)
    tris = []
    for c in model.cubes:
        A, t = mats[c.bone]
        cr = np.eye(3); ct = np.zeros(3)
        if c.rot:
            piv = np.array(c.pivot or [c.origin[0] + c.size[0] / 2, c.origin[1] + c.size[1] / 2, c.origin[2] + c.size[2] / 2], float)
            Rc = rotm(*c.rot)
            cr = Rc; ct = piv - Rc @ piv
        rects = c.face_rects()
        for face, quad in cube_faces(c).items():
            pts = []
            for q in quad:
                p = cr @ np.array(q) + ct
                p = A @ p + t
                pts.append(p)
            pts = np.array(pts)
            n = np.cross(pts[1] - pts[0], pts[3] - pts[0])
            nl = np.linalg.norm(n)
            if nl < 1e-9:
                continue
            n = n / nl
            # outward check against cube centre
            cc = A @ (cr @ (np.array(c.origin) + np.array(c.size) / 2) + ct) + t
            if np.dot(n, pts.mean(0) - cc) < 0:
                n = -n
            vn = V @ n
            if vn[2] > 0.0:   # facing away (camera looks along +z in view space after flip below)
                pass
            vp = (V @ (pts - cen).T).T
            tris.append((vp, n, rects[face], face, vn))
    # depth: camera at -z looking +z in view space; smaller z = nearer
    for vp, n, (rx, ry, rw, rh), face, vn in tris:
        if vn[2] > 0.001:     # back-facing in view space (normal pointing away from camera at -z)
            continue
        sxy = np.stack([W / 2 + vp[:, 0] * scale, H * ycen - vp[:, 1] * scale], 1)
        uv = np.array([(0, 0), (1, 0), (1, 1), (0, 1)], float)
        lam = 0.55 + 0.45 * max(0.0, float(np.dot(n, light))) if (shade and not unlit) else 1.0
        for (a, b, c_) in ((0, 1, 2), (0, 2, 3)):
            p0, p1, p2 = sxy[a], sxy[b], sxy[c_]
            minx = int(max(0, math.floor(min(p0[0], p1[0], p2[0])))); maxx = int(min(W - 1, math.ceil(max(p0[0], p1[0], p2[0]))))
            miny = int(max(0, math.floor(min(p0[1], p1[1], p2[1])))); maxy = int(min(H - 1, math.ceil(max(p0[1], p1[1], p2[1]))))
            if maxx < minx or maxy < miny:
                continue
            xs, ys = np.meshgrid(np.arange(minx, maxx + 1) + 0.5, np.arange(miny, maxy + 1) + 0.5)
            d = (p1[1] - p2[1]) * (p0[0] - p2[0]) + (p2[0] - p1[0]) * (p0[1] - p2[1])
            if abs(d) < 1e-9:
                continue
            l1 = ((p1[1] - p2[1]) * (xs - p2[0]) + (p2[0] - p1[0]) * (ys - p2[1])) / d
            l2 = ((p2[1] - p0[1]) * (xs - p2[0]) + (p0[0] - p2[0]) * (ys - p2[1])) / d
            l3 = 1 - l1 - l2
            m = (l1 >= -1e-4) & (l2 >= -1e-4) & (l3 >= -1e-4)
            if not m.any():
                continue
            z = l1 * vp[a][2] + l2 * vp[b][2] + l3 * vp[c_][2]
            ss = l1 * uv[a][0] + l2 * uv[b][0] + l3 * uv[c_][0]
            tt = l1 * uv[a][1] + l2 * uv[b][1] + l3 * uv[c_][1]
            tx = np.clip((rx + ss * rw).astype(int), 0, texa.shape[1] - 1)
            ty = np.clip((ry + tt * rh).astype(int), 0, texa.shape[0] - 1)
            col = texa[ty, tx]
            ok = m & (z < zb[miny:maxy + 1, minx:maxx + 1]) & (col[..., 3] > 40)
            if not ok.any():
                continue
            sub = img[miny:maxy + 1, minx:maxx + 1]
            zsub = zb[miny:maxy + 1, minx:maxx + 1]
            rgb = np.minimum(255, col[..., :3].astype(np.float32) * lam * GAIN)
            sub[ok] = rgb[ok]
            zsub[ok] = z[ok]
    out_img = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    if rgba:
        out_img = out_img.convert('RGBA')
        out_img.putalpha(Image.fromarray(((zb < 1e8) * 255).astype(np.uint8)))
    if out:
        out_img.save(out)
    return out_img


def render_views(model, tex, out, views=((35, 18), (215, 18), (90, 10), (0, 4)), scale=6, size=(520, 560), pose=None, center=None):
    import tempfile, os
    ims = []
    for k, (yaw, pitch) in enumerate(views):
        p = out + f'.v{k}.png'
        render(model, tex, p, yaw=yaw, pitch=pitch, scale=scale, size=size, pose=pose, center=center)
        ims.append(Image.open(p))
    W = sum(i.width for i in ims)
    sheet = Image.new('RGB', (W, ims[0].height))
    x = 0
    for i in ims:
        sheet.paste(i, (x, 0)); x += i.width
    sheet.save(out)
    for k in range(len(views)):
        os.remove(out + f'.v{k}.png')
