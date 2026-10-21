"""Material shaders for the mobs. Each returns (r, g, b, a, glow) for a texel context."""
import math
from common import *
from geo import fbm3, noise3, FACE_LIGHT


def _lit(ctx, c, k=1.0):
    f = FACE_LIGHT[ctx.face] * k
    return tuple(max(0, min(255, int(v * f))) for v in c)


def _bevel(ctx, c, strength=0.22, w=1):
    d, side = ctx.edge
    if d < w:
        if side in ('t', 'l'):
            return tuple(min(255, int(v * (1 + strength))) for v in c)
        return tuple(int(v * (1 - strength * 1.3)) for v in c)
    return c


def make(ramp, scale=0.35, base=0.35, amp=0.45, bevel=0.2, seed=1, streak=None, glow_fn=None, light=1.0, octaves=3, tint_fn=None):
    """Generic ramp-based shader. streak=(axis, freq) stretches noise along an axis (fur / wood grain)."""
    def fn(ctx):
        P = ctx.W
        if streak:
            ax, f = streak
            Q = [P[0], P[1], P[2]]
            Q[ax] *= f
            n = fbm3(Q, seed, scale, octaves)
        else:
            n = fbm3(P, seed + ctx.cube.params.get('seed', 0), scale, octaves)
        t = base + (n - 0.5) * amp * 2
        t = max(0.0, min(1.0, t))
        c = ramp_at(ramp, t)
        c = _bevel(ctx, c, bevel)
        c = _lit(ctx, c, light)
        g = 0
        a = 255
        if glow_fn:
            r = glow_fn(ctx, n, c)
            if r is not None:
                c, g = r
        if tint_fn:
            c = tint_fn(ctx, c)
        return (c[0], c[1], c[2], a, g)
    return fn


def solid_glow(ramp, lo=0.55, hi=0.95, glow=255, scale=0.5, pulse=True, seed=9):
    def fn(ctx):
        n = fbm3(ctx.W, seed, scale, 2)
        t = lo + (hi - lo) * n
        c = ramp_at(ramp, t)
        if ctx.cube.params.get('rim', True):
            d, side = ctx.edge
            if d < 1:
                c = tuple(int(v * 0.75) for v in c)
        return (c[0], c[1], c[2], 255, glow)
    return fn


def veined(base_fn, ramp_vein, thr=0.035, seed=33, scale=0.22, glow=220):
    """Overlay glowing noise-ridge cracks on top of a base shader."""
    def fn(ctx):
        r, g, b, a, gl = base_fn(ctx)
        n = fbm3(ctx.W, seed + ctx.cube.params.get('seed', 0), scale, 3)
        ridge = abs(n - 0.5)
        if ridge < thr:
            t = 1 - ridge / thr
            c = ramp_at(ramp_vein, 0.45 + 0.5 * t)
            return (c[0], c[1], c[2], 255, int(110 + (glow - 110) * t))
        if ridge < thr * 1.7:
            m = mix((r, g, b), ramp_at(ramp_vein, 0.3), 0.35)
            return (m[0], m[1], m[2], 255, 40)
        return (r, g, b, a, gl)
    return fn


def eyes(core, rim, glow=255):
    def fn(ctx):
        d, side = ctx.edge
        c = rim if d == 0 and min(ctx.w, ctx.h) > 2 else core
        return (c[0], c[1], c[2], 255, glow)
    return fn


def panelled(base_fn, line_ramp, step=4, depth=0.5):
    """Adds engraved panel lines every `step` texels in model space (armour plates)."""
    def fn(ctx):
        r, g, b, a, gl = base_fn(ctx)
        W = ctx.W
        u = (W[0] + 64) % step
        v = (W[1] + 64) % step
        if abs(ctx.cube.params.get('panel', 1)) and (u < 0.5 or v < 0.5) and ctx.cube.params.get('panel', 1):
            return (int(r * (1 - depth)), int(g * (1 - depth)), int(b * (1 - depth)), a, 0)
        return (r, g, b, a, gl)
    return fn
