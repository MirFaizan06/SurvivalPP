"""Hand-built 32x32 sword sprites (no recoloured vanilla): every tier has its own blade silhouette, guard, grip and glow."""
import math
from PIL import Image
from common import *

N = 32
HX, HY = 4.2, 27.8          # hilt end
TX, TY = 28.4, 3.8          # blade tip


def lerp(a, b, t):
    return a + (b - a) * t


def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def frame():
    dx, dy = TX - HX, TY - HY
    L = math.hypot(dx, dy)
    return L, (dx / L, dy / L), (-dy / L, dx / L)           # length, direction, normal (pointing up-left)


def draw(style):
    L, d, n = frame()
    img = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    px = img.load()
    cells = {}
    for y in range(N):
        for x in range(N):
            rx, ry = x + 0.5 - HX, y + 0.5 - HY
            t = (rx * d[0] + ry * d[1]) / L
            s = rx * n[0] + ry * n[1]
            res = style(t, s, x, y)
            if res:
                cells[(x, y)] = res
    for (x, y), c in cells.items():
        px[x, y] = c + (255,)
    # outline: darken a 1px border around the silhouette
    out = {}
    for (x, y), c in cells.items():
        for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + ox, y + oy)
            if q not in cells and 0 <= q[0] < N and 0 <= q[1] < N:
                out[q] = tuple(int(v * 0.22) for v in c)
    for (x, y), c in out.items():
        px[x, y] = c + (255,)
    return img


def ramp(r, t):
    return ramp_at(r, clamp(t))


# ------------------------------------------------------------------------------- AZURITE: crystalline longsword
def azurite(t, s, x, y):
    blade0 = 0.30
    if blade0 <= t <= 1.0:
        w = lerp(2.1, 1.7, clamp((t - blade0) / 0.55)) if t < 0.88 else lerp(1.7, 0.0, (t - 0.88) / 0.12)
        if abs(s) <= w:
            u = s / max(w, 0.01)                         # -1 (upper-left edge) .. 1
            facet = 0.5 + 0.28 * (-u) + 0.1 * math.sin(t * 38)
            if abs(u) < 0.2:
                facet = 0.28 + 0.1 * math.sin(t * 25)     # fuller
            if abs(s - 0.9) < 0.35 and 0.4 < t < 0.8:
                facet = 0.97                              # glint
            if int(t * 60) % 11 == 0 and abs(u) < 0.7:
                facet = min(1.0, facet + 0.22)            # facet seams
            return ramp(AZURITE, facet)
    if 0.235 <= t < 0.30 and abs(s) <= 4.4 - abs(t - 0.265) * 22:      # crystal cross-guard with swept tips
        k = 0.35 + 0.35 * (1 - abs(s) / 4.6)
        gem = abs(s) < 0.9
        return ramp([hx(c) for c in ('#2a3440', '#4a5a6c', '#7a8fa6', '#b4c6d8', '#eaf4ff')], 0.5 + 0.4 * k) if not gem else ramp(AZURITE, 0.95)
    if 0.07 <= t < 0.235 and abs(s) <= 0.95:                                 # wrapped grip
        wrap = (int(t * 70) % 2 == 0)
        return ramp([hx(c) for c in ('#0e2236', '#18405e', '#256688', '#3a8ab0')], 0.35 + (0.35 if wrap else 0.0) - 0.15 * s)
    if t < 0.07 and abs(s) <= 1.5 and t > -0.03:                             # pommel crystal
        return ramp(AZURITE, 0.8 - 0.25 * s)
    return None


# ------------------------------------------------------------------------------- PYRELITE: molten serrated falchion
def pyrelite(t, s, x, y):
    blade0 = 0.30
    bend = 2.6 * ((t - blade0) / 0.7) ** 2 if t > blade0 else 0.0            # curved blade
    sb = s + bend
    if blade0 <= t <= 1.0:
        w = lerp(2.0, 2.6, clamp((t - blade0) / 0.4)) if t < 0.5 else lerp(2.6, 0.0, ((t - 0.5) / 0.5) ** 0.8)
        # serrated back edge (upper-left)
        tooth = 0.9 * (1 if int(t * 34) % 2 == 0 else 0)
        if -w - tooth <= sb <= w:
            if sb < -w:                                      # teeth
                return ramp(PYRELITE, 0.3)
            u = sb / max(w, 0.01)
            if abs(u) < 0.2:                                  # glowing molten core
                return ramp([hx(c) for c in ('#7a1d00', '#c8400c', '#ff8a24', '#ffd35e', '#fff2b0')], 0.62 + 0.38 * (0.5 + 0.5 * math.sin(t * 22)))
            edge = 0.5 + 0.3 * u
            col = ramp([hx(c) for c in ('#0a0608', '#1a0e12', '#2e1a20', '#46282e', '#663a40')], 0.3 + 0.4 * (-u) + (0.1 if int(t * 40) % 7 == 0 else 0))
            if u > 0.72:                                      # hot cutting edge
                col = ramp([hx(c) for c in ('#7a1d00', '#c8400c', '#ff8a24', '#ffd35e', '#fff2b0')], 0.45 + 0.4 * (u - 0.72) / 0.28)
            return col
    if 0.22 <= t < 0.30 and abs(s) <= 3.6 - abs(t - 0.26) * 18:      # flame-shaped guard
        return ramp([hx(c) for c in ('#0a0608', '#1a0e12', '#2e1a20', '#46282e')], 0.55 - 0.12 * abs(s) / 3 + 0.1) if abs(s) > 1.0 else ramp(PYRELITE, 0.85)
    if 0.06 <= t < 0.22 and abs(s) <= 0.95:
        return ramp([hx(c) for c in ('#2a0e08', '#5a1c10', '#8a2e18', '#b84a28')], 0.3 + (0.35 if int(t * 64) % 2 == 0 else 0.0) - 0.1 * s)
    if t < 0.06 and abs(s) <= 1.6 and t > -0.04:
        return ramp(PYRELITE, 0.88 - 0.3 * s)
    return None


# ------------------------------------------------------------------------------- ECLIPSITE: slim void blade with a corona guard
def eclipsite(t, s, x, y):
    blade0 = 0.34
    bend = 1.2 * ((t - blade0) / 0.66) ** 2 if t > blade0 else 0.0
    sb = s + bend
    if blade0 <= t <= 1.0:
        w = 1.3 if t < 0.9 else lerp(1.3, 0.0, (t - 0.9) / 0.1)
        if abs(sb) <= w:
            u = sb / max(w, 0.01)
            dark = ramp([hx(c) for c in ('#03010a', '#0a0420', '#14083a', '#201058', '#2f1c80')], 0.3 + 0.25 * (-u))
            if abs(u) > 0.62:                                  # glowing violet edge
                return ramp(ECLIPSITE, 0.55 + 0.4 * (abs(u) - 0.62) / 0.38)
            if abs(u) < 0.14 and int(t * 44) % 3 == 0:        # cyan sparks down the spine
                return hx('#9ff4ff')
            return dark
    ringc = 0.27
    rx, ry = x + 0.5 - (HX + (TX - HX) * ringc), y + 0.5 - (HY + (TY - HY) * ringc)
    dist = math.hypot(rx, ry)
    if 3.3 <= dist <= 4.3 and not (0.3 <= t):                      # the corona ring around the hilt
        ang = math.atan2(ry, rx)
        return ramp(ECLIPSITE, 0.55 + 0.4 * (0.5 + 0.5 * math.cos(ang - 3.9)))
    if dist <= 1.5:
        return hx('#9ff4ff') if dist < 0.9 else ramp(ECLIPSITE, 0.9)
    if 0.07 <= t < 0.24 and abs(s) <= 0.9:
        return ramp([hx(c) for c in ('#08041a', '#100833', '#1a0e4f', '#271770')], 0.3 + (0.3 if int(t * 66) % 2 == 0 else 0.0) - 0.1 * s)
    if t < 0.07 and abs(s) <= 1.4 and t > -0.04:
        return ramp(ECLIPSITE, 0.85 - 0.3 * s)
    return None


SWORDS = {'azurite': azurite, 'pyrelite': pyrelite, 'eclipsite': eclipsite}


def build():
    for mat, st in SWORDS.items():
        save_png(draw(st), f'{RP}/textures/items/{mat}_sword.png')


if __name__ == '__main__':
    ims = [draw(st).resize((256, 256), Image.NEAREST) for st in SWORDS.values()]
    sheet = Image.new('RGBA', (256 * 3, 256), (60, 60, 70, 255))
    for i, im in enumerate(ims):
        sheet.alpha_composite(im, (i * 256, 0))
    sheet.save(f'{PREVIEW}/swords.png')
    print('ok')
