"""Shared helpers for the Eclipsed Realms++ generators."""
import json, math, os, random, hashlib
from PIL import Image
import numpy as np

import os, sys
from pathlib import Path
ROOT = Path(os.environ.get('SPP_ROOT') or Path(__file__).resolve().parents[2])
BEDROCK_SAMPLES = Path(os.environ.get('BEDROCK_SAMPLES') or ROOT / '.ref' / 'bedrock-samples')
NPM_DIR = Path(os.environ.get('SPP_NPM') or ROOT / '.ref' / 'npm')
REF = (BEDROCK_SAMPLES / 'resource_pack' / 'textures').as_posix()
BUILD = Path(os.environ.get('SPP_BUILD') or ROOT / 'build')   # set SPP_BUILD to a non-synced folder if the repo lives in OneDrive/Dropbox
OUT = (BUILD / 'out').as_posix()
PREVIEW = (BUILD / 'preview').as_posix()
DIST = (ROOT / 'releases').as_posix()
SCRIPTS_SRC = (ROOT / 'tools' / 'scripts').as_posix()
SCHEMA_DIR = (BEDROCK_SAMPLES / 'metadata').as_posix()
GEN_DIR = Path(__file__).resolve().parent.as_posix()
BP = OUT + '/ECR_BP'
RP = OUT + '/ECR_RP'
for _d in (PREVIEW, DIST, OUT):
    os.makedirs(_d, exist_ok=True)
NS = 'ecr'

# ---------------------------------------------------------------- colours
def hx(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))

def lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(len(a)))

def ramp_at(ramp, t):
    """ramp: list of rgb tuples, t in [0,1] -> interpolated rgb ints"""
    t = max(0.0, min(1.0, t))
    f = t * (len(ramp) - 1)
    i = int(math.floor(f))
    if i >= len(ramp) - 1:
        return tuple(int(round(c)) for c in ramp[-1])
    c = lerp(ramp[i], ramp[i + 1], f - i)
    return tuple(int(round(v)) for v in c)

def lum(c):
    return (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) / 255.0

# The three materials ---------------------------------------------------------
AZURITE = [hx(x) for x in ['#071433', '#0e2a6b', '#1b4fb8', '#2f86f0', '#6cc3ff', '#c9efff', '#ffffff']]
PYRELITE = [hx(x) for x in ['#140505', '#3b0c08', '#7d1a0a', '#d4440f', '#ff8a24', '#ffd35e', '#fff6c2']]
ECLIPSITE = [hx(x) for x in ['#05020c', '#150a2b', '#34136a', '#6d27b8', '#c046dc', '#ff9cf0', '#9ff4ff']]
RIMESTEEL = [hx(x) for x in ['#0e1622', '#26384c', '#4a6a88', '#86a8c4', '#c2dcee', '#f0f8ff', '#ffffff']]
GLACITE = [hx(x) for x in ['#06182e', '#0f3a6a', '#1c70b0', '#40b4e8', '#8ee0ff', '#d4f6ff', '#ffffff']]
WISPSTEEL = [hx(x) for x in ['#06140e', '#0f3a26', '#1c7a4a', '#3cc070', '#a8f08a', '#ffe27a', '#fffbd0']]

# ---------------------------------------------------------------- IO helpers
def ensure(path):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)

def wjson(path, obj):
    ensure(path)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write('\n')

def wtext(path, text):
    ensure(path)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)

def save_png(im, path):
    ensure(path)
    im.save(path, 'PNG')

def save_tga(im, path):
    ensure(path)
    im.convert('RGBA').save(path, 'TGA', compression=None)

def load(rel):
    return Image.open(REF + '/' + rel).convert('RGBA')

# ---------------------------------------------------------------- noise
class Noise:
    """Seeded, optionally tileable value noise on a small grid."""
    def __init__(self, seed, size=16, cells=4):
        r = np.random.RandomState(seed)
        self.cells = cells
        self.size = size
        self.g = r.rand(cells, cells)

    def at(self, x, y):
        c = self.cells
        fx = (x / self.size) * c
        fy = (y / self.size) * c
        x0, y0 = int(math.floor(fx)), int(math.floor(fy))
        tx, ty = fx - x0, fy - y0
        tx = tx * tx * (3 - 2 * tx)
        ty = ty * ty * (3 - 2 * ty)
        g = self.g
        a = g[y0 % c, x0 % c]; b = g[y0 % c, (x0 + 1) % c]
        d = g[(y0 + 1) % c, x0 % c]; e = g[(y0 + 1) % c, (x0 + 1) % c]
        return (a * (1 - tx) + b * tx) * (1 - ty) + (d * (1 - tx) + e * tx) * ty

def fbm(seed, x, y, size=16, octaves=(2, 4, 8), weights=(0.5, 0.3, 0.2)):
    v = 0
    for k, (o, w) in enumerate(zip(octaves, weights)):
        n = Noise(seed * 31 + k * 7, size, o)
        v += n.at(x, y) * w
    return v

def tint(c, f):
    return tuple(max(0, min(255, int(round(v * f)))) for v in c[:3])

def mix(c1, c2, t):
    return tuple(int(round(c1[i] + (c2[i] - c1[i]) * t)) for i in range(3))

def over(img, x, y, rgba):
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), tuple(rgba) if len(rgba) == 4 else tuple(rgba) + (255,))

def up_sheet(paths, out, scale=8, cols=6):
    import subprocess, sys
    subprocess.run([sys.executable, GEN_DIR + '/sheet.py', out, str(scale), str(cols)] + list(paths), check=True)
