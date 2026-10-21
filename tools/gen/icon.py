"""Pack thumbnail: key art of the Veiled Blossom under a blossom-pink eclipse, rendered from the real model (no text, reads at 256px)."""
import math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from common import *
import geo
import mob_hanae

W = 1024


def hanae_shot(scale, yaw, pitch, cy=22, gain=1.05):
    m = mob_hanae.hanae()
    m.pack()
    base, glow = m.paint(mob_hanae.hanae_materials(False))
    geo.GAIN = gain
    return geo.render(m, base, None, yaw=yaw, pitch=pitch, scale=scale, size=(W, W), center=(0, cy, 0), rgba=True, ycen=0.56)


def bloom(img, thresh=238, radius=14, strength=0.32):
    a = np.array(img.convert('RGB')).astype(np.float32)
    mx = a.max(axis=2)
    mask = mx > thresh
    glow = np.zeros_like(a)
    glow[mask] = a[mask]
    g = Image.fromarray(glow.astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius))
    g2 = Image.fromarray(glow.astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius * 2.8))
    out = a + np.array(g).astype(np.float32) * strength + np.array(g2).astype(np.float32) * strength * 0.7
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def background(rng):
    yy, xx = np.mgrid[0:W, 0:W].astype(np.float32)
    px = np.zeros((W, W, 3), np.float32)
    t = yy / W
    top, mid, low = np.array([8, 4, 28]), np.array([66, 22, 78]), np.array([150, 62, 118])
    k = np.clip(t * 1.25, 0, 1)[..., None]
    px[:] = np.where(k < 0.55, top + (mid - top) * (k / 0.55), mid + (low - mid) * ((k - 0.55) / 0.45))
    cx, cy = W * 0.5, W * 0.33
    d = np.hypot(xx - cx, yy - cy)
    corona = np.exp(-((d - 190) / 120.0) ** 2)
    px += corona[..., None] * np.array([150, 50, 120])
    ring = np.exp(-((d - 160) / 6.0) ** 2)
    px += ring[..., None] * np.array([255, 190, 225])
    ang = np.arctan2(yy - cy, xx - cx)
    rays = (np.abs(np.sin(ang * 12)) ** 20) * np.exp(-np.clip(d - 165, 0, None) / 190.0) * (d > 162)
    px += rays[..., None] * np.array([230, 120, 190]) * 0.32
    px[d < 158] = np.array([6, 2, 14])                                       # the eclipse disc
    img = Image.fromarray(np.clip(px, 0, 255).astype(np.uint8))
    d_ = ImageDraw.Draw(img)
    for _ in range(140):                                                      # stars in the upper sky
        x, y = rng.randint(0, W), rng.randint(0, int(W * 0.35))
        if math.hypot(x - cx, y - cy) > 215:
            c = rng.randint(150, 255)
            d_.point((x, y), fill=(c, c, 255))
    return img


def torii(img):
    layer = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    col = (70, 14, 40, 235)
    x0, x1, base, top = 150, 874, 640, 470
    for px_ in (330, 694):
        d.rectangle([px_ - 17, top, px_ + 17, base], fill=col)
    d.polygon([(x0, top - 8), (x1, top - 8), (x1 - 34, top + 22), (x0 + 34, top + 22)], fill=col)
    d.rectangle([x0 + 70, top + 52, x1 - 70, top + 78], fill=col)
    layer = layer.filter(ImageFilter.GaussianBlur(2.2))
    img.alpha_composite(layer)


def petal_poly(cx, cy, size, ang):
    pts = []
    for k in range(12):
        t = k / 11 * math.tau
        r = size * (0.55 + 0.45 * abs(math.sin(t / 2)))
        pts.append((cx + math.cos(t + ang) * r * 0.62, cy + math.sin(t + ang) * r))
    return pts


def blossom_branch(img, rng, side):
    layer = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    pts = []
    for k in range(9):
        t = k / 8
        x = (20 + 400 * t) if side < 0 else (W - 20 - 400 * t)
        y = 40 + 150 * math.sin(t * 2.0) - 20 * t
        pts.append((x, y))
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i + 1]], fill=(28, 14, 22, 255), width=int(26 - i * 2.4))
    for (x, y) in pts:
        for _ in range(7):
            bx, by = x + rng.uniform(-70, 70), y + rng.uniform(-60, 70)
            for k in range(5):
                a = k / 5 * math.tau
                d.polygon(petal_poly(bx + math.cos(a) * 12, by + math.sin(a) * 12, 17, a + 1.57), fill=(rng.choice([(236, 150, 190), (248, 190, 215), (222, 120, 172)]) + (235,)))
            d.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=(255, 214, 110, 255))
    layer = layer.filter(ImageFilter.GaussianBlur(1.1))
    img.alpha_composite(layer)


def petals(img, rng, count, blur, size_rng, alpha):
    layer = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(count):
        x, y = rng.uniform(0, W), rng.uniform(0, W)
        s = rng.uniform(*size_rng)
        d.polygon(petal_poly(x, y, s, rng.uniform(0, math.tau)), fill=(rng.choice([(255, 190, 215), (255, 225, 238), (240, 150, 195)]) + (alpha,)))
    if blur:
        layer = layer.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(layer)


def compose():
    rng = random.Random(2026)
    img = background(rng).convert('RGBA')
    torii(img)
    # misty ground
    mist = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    md = ImageDraw.Draw(mist)
    for k in range(40):
        y = int(W * 0.66 + k * 9)
        md.ellipse([-200, y, W + 200, y + 90], fill=(240, 170, 210, 3 + k // 9))
    img.alpha_composite(mist.filter(ImageFilter.GaussianBlur(26)))
    # reflections: two translucent echoes either side
    for sx, yaw in ((-300, 38), (300, -38)):
        echo = hanae_shot(9.0, yaw, -4)
        r, g, b, a = echo.split()
        echo = Image.merge('RGBA', (r.point(lambda v: int(v * 0.8 + 40)), g.point(lambda v: int(v * 0.85 + 40)), b.point(lambda v: min(255, int(v * 0.9 + 80))), a.point(lambda v: int(v * 0.34))))
        img.alpha_composite(echo, (sx, 120))
    petals(img, rng, 26, 9, (30, 54), 150)
    hero = hanae_shot(15.5, 24, -6)
    shadow = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    img.alpha_composite(hero, (0, -6))
    blossom_branch(img, rng, -1)
    blossom_branch(img, rng, 1)
    petals(img, rng, 80, 0, (6, 15), 215)
    petals(img, rng, 10, 5, (44, 74), 120)
    out = bloom(img)
    # vignette
    yy, xx = np.mgrid[0:W, 0:W].astype(np.float32)
    v = 1 - 0.55 * (np.hypot(xx - W / 2, yy - W / 2) / (W * 0.72)) ** 2.4
    arr = np.array(out).astype(np.float32) * np.clip(v, 0.25, 1)[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def build():
    img = compose()
    img.save(PREVIEW + '/icon_1024.png')
    out = img.resize((512, 512), Image.LANCZOS)
    for p in (f'{BP}/pack_icon.png', f'{RP}/pack_icon.png'):
        ensure(p)
        out.save(p)
    img.resize((256, 256), Image.LANCZOS).save(PREVIEW + '/icon_256.png')
    return out


if __name__ == '__main__':
    build()
    print('icon ok')
