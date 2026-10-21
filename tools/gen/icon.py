import os
"""Pack thumbnail: cinematic key art rendered from the real mob models."""
import math, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
from common import *
import geo
import mob_boss, mob_warg, mob_voidweaver

W = 1024   # design resolution, exported at 256 and 512


def model(mod):
    m = mod.build()
    m.pack()
    base, _ = m.paint(mod.materials())
    return m, base


def shot(m, tex, yaw, pitch, scale, cy, ycen=0.6, gain=2.1):
    geo.GAIN = gain
    return geo.render(m, tex, None, yaw=yaw, pitch=pitch, scale=scale, size=(W, W), center=(0, cy, 0), rgba=True, ycen=ycen)


def bloom(img, thresh=215, radius=18, strength=1.1):
    a = np.array(img.convert('RGB')).astype(np.float32)
    mx = a.max(axis=2)
    sat = mx - a.min(axis=2)
    mask = ((mx > thresh) & (sat > 40)) | (mx > 245)
    glow = np.zeros_like(a)
    glow[mask] = a[mask]
    g = Image.fromarray(glow.astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius))
    g2 = Image.fromarray(glow.astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius * 2.6))
    out = np.array(img.convert('RGB')).astype(np.float32)
    out += np.array(g).astype(np.float32) * strength + np.array(g2).astype(np.float32) * strength * 0.8
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def background():
    img = Image.new('RGB', (W, W))
    px = np.zeros((W, W, 3), np.float32)
    yy, xx = np.mgrid[0:W, 0:W].astype(np.float32)
    # night-sky gradient with violet horizon glow
    t = yy / W
    px[..., 0] = 6 + 26 * (t ** 2.2)
    px[..., 1] = 3 + 8 * (t ** 2.2)
    px[..., 2] = 16 + 58 * (t ** 1.8)
    # eclipse behind the boss
    cx, cy = W * 0.5, W * 0.30
    d = np.hypot(xx - cx, yy - cy)
    corona = np.exp(-((d - 190) / 110.0) ** 2)
    px[..., 0] += 150 * corona; px[..., 1] += 40 * corona; px[..., 2] += 190 * corona
    ring = np.exp(-((d - 168) / 7.0) ** 2)
    px[..., 0] += 255 * ring; px[..., 1] += 190 * ring; px[..., 2] += 255 * ring
    disc = d < 166
    px[disc] = px[disc] * 0.0 + np.array([3, 1, 8])
    # radial rays
    ang = np.arctan2(yy - cy, xx - cx)
    rays = (np.abs(np.sin(ang * 14)) ** 18) * np.exp(-np.clip(d - 170, 0, None) / 160.0) * (d > 168)
    px[..., 0] += 110 * rays; px[..., 1] += 50 * rays; px[..., 2] += 160 * rays
    img = Image.fromarray(np.clip(px, 0, 255).astype(np.uint8))
    # stars + drifting embers
    d_ = ImageDraw.Draw(img)
    rng = random.Random(11)
    for _ in range(260):
        x, y = rng.randrange(W), rng.randrange(int(W * 0.8))
        b = rng.choice([110, 160, 220, 255])
        r = rng.choice([1, 1, 1, 2])
        col = (b, b, min(255, b + 30))
        d_.ellipse([x - r, y - r, x + r, y + r], fill=col)
    # floor fog
    fog = Image.new('RGB', (W, W), (0, 0, 0))
    fd = ImageDraw.Draw(fog)
    fd.ellipse([-200, W * 0.78, W + 200, W * 1.25], fill=(70, 30, 120))
    fog = fog.filter(ImageFilter.GaussianBlur(60))
    img = ImageChops.add(img, fog)
    return img


def text_outline(draw, xy, txt, font, fill, outline, width, anchor='mm'):
    x, y = xy
    for dx in range(-width, width + 1):
        for dy in range(-width, width + 1):
            if dx * dx + dy * dy <= width * width:
                draw.text((x + dx, y + dy), txt, font=font, fill=outline, anchor=anchor)
    draw.text(xy, txt, font=font, fill=fill, anchor=anchor)


def gradient_text(img, xy, txt, font, top, bottom, outline, width, glow=(190, 70, 230)):
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    text_outline(ld, xy, txt, font, (255, 255, 255, 255), outline + (255,), width)
    mask = Image.new('L', img.size, 0)
    ImageDraw.Draw(mask).text(xy, txt, font=font, fill=255, anchor='mm')
    grad = Image.new('RGBA', img.size, (0, 0, 0, 0))
    gp = grad.load()
    bb = mask.getbbox()
    for y in range(bb[1], bb[3] + 1):
        t = (y - bb[1]) / max(1, bb[3] - bb[1])
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)) + (255,)
        for x in range(bb[0], bb[2] + 1):
            gp[x, y] = c
    # glow behind
    gl = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(gl).text(xy, txt, font=font, fill=glow + (255,), anchor='mm')
    gl = gl.filter(ImageFilter.GaussianBlur(14))
    base = img.convert('RGBA')
    base.alpha_composite(gl)
    base.alpha_composite(layer)
    fillmask = grad.copy()
    fillmask.putalpha(ImageChops.multiply(grad.getchannel('A'), mask))
    base.alpha_composite(fillmask)
    return base


def place(comp, im, cx, bottom, height):
    """scale a transparent render so its visible height == height, centre it on cx and rest it on `bottom`"""
    bb = im.getbbox()
    c = im.crop(bb)
    sc = height / c.height
    c = c.resize((max(1, int(c.width * sc)), height), Image.LANCZOS)
    x, y = int(cx - c.width / 2), int(bottom - c.height)
    a = c.getchannel('A').filter(ImageFilter.GaussianBlur(24))
    glow = Image.new('RGBA', c.size, (120, 50, 200, 0))
    glow.putalpha(a.point(lambda v: int(v * 0.45)))
    comp.alpha_composite(glow, (max(0, x), max(0, y)))
    comp.alpha_composite(c, (x, y))


def gem(comp, name, x, y, s, tint):
    ic = Image.open(f'{RP}/textures/items/{name}.png').convert('RGBA').resize((16 * s, 16 * s), Image.NEAREST)
    pad = 60
    layer = Image.new('RGBA', (ic.width + pad * 2, ic.height + pad * 2), (0, 0, 0, 0))
    layer.alpha_composite(ic, (pad, pad))
    halo = layer.getchannel('A').filter(ImageFilter.GaussianBlur(26))
    g = Image.new('RGBA', layer.size, tint + (0,))
    g.putalpha(halo.point(lambda v: int(v * 0.9)))
    comp.alpha_composite(g, (x - pad, y - pad))
    comp.alpha_composite(layer, (x - pad, y - pad))


def compose():
    bg = background().convert('RGBA')
    boss, bt = model(mob_boss)
    warg, wt = model(mob_warg)
    voidw, vt = model(mob_voidweaver)
    shot_boss = shot(boss, bt, yaw=12, pitch=-6, scale=7.0, cy=56, ycen=0.52, gain=1.55)
    shot_warg = shot(warg, wt, yaw=-42, pitch=-10, scale=9.0, cy=14, ycen=0.60, gain=2.3)
    shot_void = shot(voidw, vt, yaw=28, pitch=-8, scale=8.0, cy=24, ycen=0.60, gain=2.0)

    comp = bg.copy()
    place(comp, shot_boss, W * 0.5, 800, 640)
    place(comp, shot_warg, W * 0.20, 770, 300)
    place(comp, shot_void, W * 0.81, 790, 400)
    comp = bloom(comp.convert('RGB'), thresh=238, radius=10, strength=0.55).convert('RGBA')

    gem(comp, 'azurite_ingot', 70, 300, 7, (40, 120, 255))
    gem(comp, 'pyrelite_ingot', 850, 250, 7, (255, 110, 30))
    gem(comp, 'eclipsite_ingot', 905, 480, 6, (200, 70, 240))

    band = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    bp = band.load()
    for y in range(int(W * 0.70), W):
        t = max(0.0, (y - W * 0.70) / (W * 0.30))
        a = int(238 * min(1, t * 1.3) ** 1.2)
        for x in range(W):
            bp[x, y] = (4, 2, 12, a)
    comp.alpha_composite(band)

    f_title = ImageFont.truetype('C:/Windows/Fonts/impact.ttf', 176)
    f_sub = ImageFont.truetype('C:/Windows/Fonts/bahnschrift.ttf', 64)
    f_tag = ImageFont.truetype('C:/Windows/Fonts/bahnschrift.ttf', 42)
    comp = gradient_text(comp, (W // 2, 812), 'SURVIVAL++', f_title, (255, 244, 190), (255, 150, 60), (30, 8, 50), 9)
    d = ImageDraw.Draw(comp)
    sub = 'ECLIPSED REALMS'
    total = sum(d.textlength(c, font=f_sub) + 14 for c in sub) - 14
    x = (W - total) / 2
    for c in sub:
        for dx in (-3, 3):
            for dy in (-3, 3):
                d.text((x + dx, 918 + dy), c, font=f_sub, fill=(20, 5, 40), anchor='lm')
        d.text((x, 918), c, font=f_sub, fill=(216, 170, 255), anchor='lm')
        x += d.textlength(c, font=f_sub) + 14
    d.text((W // 2, 978), 'END++  \u2022  NETHER++  \u2022  VANILLA++', font=f_tag, fill=(150, 235, 255), anchor='mm')
    d.text((W // 2, 1008), 'by Tech Bytes Design', font=ImageFont.truetype('C:/Windows/Fonts/bahnschrift.ttf', 24), fill=(190, 175, 220), anchor='mm')
    return comp.convert('RGB')


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
