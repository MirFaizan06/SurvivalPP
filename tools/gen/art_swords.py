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



RIMESTEEL_R = [hx(c) for c in ('#0e1622', '#26384c', '#4a6a88', '#86a8c4', '#c2dcee', '#f0f8ff', '#ffffff')]
GLACITE_R = [hx(c) for c in ('#06182e', '#0f3a6a', '#1c70b0', '#40b4e8', '#8ee0ff', '#d4f6ff', '#ffffff')]
WISPSTEEL_R = [hx(c) for c in ('#06140e', '#0f3a26', '#1c7a4a', '#3cc070', '#a8f08a', '#ffe27a', '#fffbd0')]
FUR = [hx(c) for c in ('#22201c', '#3e382e', '#625848', '#8a7e68')]
LEATHER = [hx(c) for c in ('#1a120c', '#32231a', '#523a28', '#76563c')]
GOLD_R = [hx(c) for c in ('#6a4a0a', '#a8781a', '#d9a830', '#f7d466', '#fff0a8')]
BARK = [hx(c) for c in ('#140c06', '#2c1c0e', '#503418', '#7a5430')]
SILVER_R = [hx(c) for c in ('#4a5666', '#78869a', '#a8b6c8', '#d8e2ee', '#ffffff')]


# ------------------------------------------------------------------------------- RIMESTEEL: nordic broadsword with a fur-wrapped grip
def rimesteel(t, s, x, y):
    blade0 = 0.30
    if blade0 <= t <= 1.0:
        w = 2.2 if t < 0.86 else lerp(2.2, 0.0, (t - 0.86) / 0.14)
        if abs(s) <= w:
            u = s / max(w, 0.01)
            f = 0.5 + 0.28 * (-u) + 0.06 * math.sin(t * 30)
            if abs(u) < 0.22:
                f = 0.3 + 0.06 * math.sin(t * 22)                      # fuller
            if abs(u) > 0.8:
                f = 0.9                                                 # honed edge
            if (x * 7 + y * 13) % 11 == 0 and abs(u) > 0.45:
                f = 0.97                                                # frost speckles
            return ramp(RIMESTEEL_R, f)
    if 0.22 <= t < 0.30 and abs(s) <= 3.6 - abs(t - 0.26) * 20:       # swept guard
        return ramp(SILVER_R, 0.5 + 0.35 * (1 - abs(s) / 4.0))
    if 0.07 <= t < 0.22 and abs(s) <= 1.0:                           # fur-wrapped grip
        return ramp(FUR, 0.35 + (0.4 if int(t * 60) % 2 == 0 else 0.0) - 0.1 * s)
    if t < 0.07 and abs(s) <= 1.6 and t > -0.03:
        return ramp(RIMESTEEL_R, 0.8 - 0.25 * s)
    return None


# ------------------------------------------------------------------------------- GLACITE: crystal-cut ice broadsword with a snowflake guard
def glacite(t, s, x, y):
    blade0 = 0.32
    if blade0 <= t <= 1.0:
        spike = 0.9 * (1 if int(t * 26) % 3 == 0 else 0) if t < 0.9 else 0.0
        w = lerp(2.4, 1.8, clamp((t - blade0) / 0.55)) if t < 0.88 else lerp(1.8, 0.0, (t - 0.88) / 0.12)
        if -w - spike <= s <= w:
            if s < -w:
                return ramp(GLACITE_R, 0.82)                            # crystal spurs on the spine
            u = s / max(w, 0.01)
            f = 0.55 + 0.25 * (-u) + 0.08 * math.sin(t * 40)
            if abs(u) < 0.2:
                f = 0.3
            if int(t * 54) % 9 == 0 and abs(u) < 0.8:
                f = min(1.0, f + 0.3)
            if abs(s - 0.8) < 0.35 and 0.45 < t < 0.8:
                f = 1.0
            return ramp(GLACITE_R, f)
    gx, gy = HX + (TX - HX) * 0.27, HY + (TY - HY) * 0.27
    dist = math.hypot(x + 0.5 - gx, y + 0.5 - gy)
    ang = math.atan2(y + 0.5 - gy, x + 0.5 - gx)
    if dist <= 4.2 and t < 0.32:
        if dist < 1.3:
            return ramp(GLACITE_R, 1.0)
        if abs(math.sin(ang * 3)) > 0.93 or abs(dist - 3.4) < 0.5 and False:
            return ramp(SILVER_R, 0.9)                                  # six arms of the snowflake
    if 0.07 <= t < 0.22 and abs(s) <= 0.95:
        return ramp([hx(c) for c in ('#0c2040', '#143868', '#1e5090', '#2c70b8')], 0.35 + (0.35 if int(t * 66) % 2 == 0 else 0.0) - 0.1 * s)
    if t < 0.07 and abs(s) <= 1.5 and t > -0.03:
        return ramp(GLACITE_R, 0.8 - 0.25 * s)
    return None


# ------------------------------------------------------------------------------- WISPSTEEL: dark fen-iron blade, antler guard, lantern pommel
def wispsteel(t, s, x, y):
    blade0 = 0.32
    bend = 1.8 * ((t - blade0) / 0.68) ** 2 if t > blade0 else 0.0
    sb = s + bend
    if blade0 <= t <= 1.0:
        w = 1.9 if t < 0.9 else lerp(1.9, 0.0, (t - 0.9) / 0.1)
        if abs(sb) <= w:
            u = sb / max(w, 0.01)
            if abs(u) > 0.7:
                return ramp(WISPSTEEL_R, 0.55 + 0.4 * (abs(u) - 0.7) / 0.3)       # glowing foxfire edge
            if abs(u) < 0.12 and int(t * 40) % 3 == 0:
                return ramp(WISPSTEEL_R, 0.95)
            return ramp([hx(c) for c in ('#0a0e0c', '#161e1a', '#26322c', '#3c4a42', '#586a60')], 0.3 + 0.25 * (-u) + (0.1 if int(t * 36) % 7 == 0 else 0))
    if 0.2 <= t < 0.32:                                                       # antler guard
        ax = abs(s)
        if ax <= 4.4 - abs(t - 0.26) * 14 and (ax > 1.0 or t < 0.27):
            return ramp(BARK, 0.4 + 0.4 * (1 - ax / 4.6))
        if 1.2 < ax <= 2.2 and 0.27 <= t < 0.36:
            return ramp(BARK, 0.7)                                            # tines
    if 0.07 <= t < 0.2 and abs(s) <= 0.9:
        return ramp(GOLD_R, 0.4 + (0.3 if int(t * 66) % 2 == 0 else 0.0) - 0.1 * s)
    lx, ly = HX - 0.2, HY + 0.5
    if t < 0.07 and abs(s) <= 1.9 and t > -0.06:                              # lantern pommel
        return ramp(WISPSTEEL_R, 0.9) if abs(s) < 1.1 else ramp(GOLD_R, 0.6)
    return None


# ------------------------------------------------------------------------------- FROSTSONG: the Frost Cantor's conductor-sword
def frostsong(t, s, x, y):
    blade0 = 0.36
    if blade0 <= t <= 1.0:
        w = 1.25 if t < 0.93 else lerp(1.25, 0.0, (t - 0.93) / 0.07)
        wave = 0.9 * math.sin(t * 36)
        if abs(s) <= w:
            u = s / max(w, 0.01)
            if abs(s - wave) < 0.55 and t > 0.4:
                return ramp(GLACITE_R, 0.98)                            # the glowing melody line along the blade
            f = 0.62 + 0.25 * (-u)
            if abs(u) > 0.75:
                f = 0.92
            return ramp(GLACITE_R, f * 0.92)
    gx, gy = HX + (TX - HX) * 0.30, HY + (TY - HY) * 0.30
    dx_, dy_ = x + 0.5 - gx, y + 0.5 - gy
    dist = math.hypot(dx_, dy_)
    if 3.1 <= dist <= 4.1 and t < 0.38:                                    # treble-clef ring guard
        return ramp(SILVER_R, 0.55 + 0.4 * (0.5 + 0.5 * math.cos(math.atan2(dy_, dx_) - 3.9)))
    if dist <= 1.4:
        return ramp(GLACITE_R, 1.0)
    if 0.06 <= t < 0.26 and abs(s) <= 0.9:
        return ramp([hx(c) for c in ('#3a4a5c', '#6a809a', '#a0b6cc', '#dae6f2')], 0.35 + (0.35 if int(t * 66) % 2 == 0 else 0.0) - 0.1 * s)
    if t < 0.06 and abs(s) <= 1.5 and t > -0.04:
        return ramp(SILVER_R, 0.85 - 0.3 * s)
    return None


# ------------------------------------------------------------------------------- MIRELIGHT SCYTHE: the Mire Lantern's lantern-scythe
def mirelight(t, s, x, y):
    px_, py_ = x + 0.5, y + 0.5
    if -0.03 <= t <= 0.97 and abs(s) <= 0.62:                                 # long gnarled pole
        return ramp(BARK, 0.35 + 0.35 * (0.5 + 0.5 * math.sin(t * 50)) - 0.1 * s)
    cx, cy = 21.0, 17.0                                                       # crescent blade: an arc of a big circle that leaves the pole top
    dx, dy = px_ - cx, py_ - cy
    dist = math.hypot(dx, dy)
    ang = math.degrees(math.atan2(dy, dx)) % 360
    if 196 <= ang <= 292:
        k = (ang - 196) / 96.0                                                # 0 at the tip, 1 at the pole
        thick = 0.6 + 2.6 * (k ** 0.8)
        if 10.4 - thick <= dist <= 10.4:
            edge = (10.4 - dist) / max(thick, 0.01)                           # 0 = outer cutting edge
            if edge < 0.3:
                return ramp(WISPSTEEL_R, 0.97 if k > 0.15 else 0.8)
            return ramp([hx(c) for c in ('#0a0e0c', '#161e1a', '#26322c', '#3c4a42', '#586a60')], 0.3 + 0.3 * k + 0.1 * (1 - edge))
    if 292 < ang <= 304 and 8.4 <= dist <= 11.4:                              # collar that binds the blade to the pole
        return ramp(GOLD_R, 0.6)
    lx, ly = 16.5, 20.0                                                       # hanging lantern
    if 15 <= px_ <= 19 and 18 <= py_ <= 23:
        if px_ in (15.5, 18.5) or py_ in (18.5, 22.5):
            return ramp(GOLD_R, 0.45)
        return ramp(WISPSTEEL_R, 1.0)
    if abs(px_ - 17.0) < 0.6 and 16.4 <= py_ < 18:
        return ramp(GOLD_R, 0.35)
    if t < 0.05 and abs(s) <= 1.0:
        return ramp(GOLD_R, 0.55)
    return None


L_SCALE = 0.0   # set below once frame() is known

L_SCALE = frame()[0]
SWORDS = {'azurite': azurite, 'pyrelite': pyrelite, 'eclipsite': eclipsite, 'rimesteel': rimesteel, 'glacite': glacite, 'wispsteel': wispsteel,
          'frostsong': frostsong, 'mirelight_scythe': mirelight}


BOSS_WEAPONS = ('frostsong', 'mirelight_scythe')


def build():
    for mat, st in SWORDS.items():
        save_png(draw(st), f'{RP}/textures/items/{mat if mat in BOSS_WEAPONS else mat + "_sword"}.png')


if __name__ == '__main__':
    ims = [draw(st).resize((256, 256), Image.NEAREST) for st in SWORDS.values()]
    sheet = Image.new('RGBA', (256 * len(ims), 256), (60, 60, 70, 255))
    for i, im in enumerate(ims):
        sheet.alpha_composite(im, (i * 256, 0))
    sheet.save(f'{PREVIEW}/swords.png')
    print('ok')
