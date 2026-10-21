"""python preview_models.py <module> <key> [scale] [centerY]  ->  build/preview/<key>_views.png"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
from common import *
import geo
from geo import render_views

mod = importlib.import_module(sys.argv[1])
key = sys.argv[2]
scale = float(sys.argv[3]) if len(sys.argv) > 3 else 8
cy = float(sys.argv[4]) if len(sys.argv) > 4 else 12
builder, mats, gid = mod.MODELS[key]
m = builder()
print('texture used', round(m.pack(), 2))
base, glow = m.paint(mats())
base.save(f'{PREVIEW}/{key}_tex.png')
geo.GAIN = 2.0
render_views(m, base, f'{PREVIEW}/{key}_views.png', views=((35, -14), (215, -14), (90, -8)), size=(760, 760), scale=scale, center=(0, cy, 0))
print('ok')
