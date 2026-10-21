import os
import sys, importlib, time
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import geo
from geo import render_views
geo.GAIN=2.2
name=sys.argv[1]
mod=importlib.import_module(name)
t=time.time()
m=mod.build()
print('used',m.pack())
base,glow=m.paint(mod.materials())
base.save(f'{PREVIEW}/{name}_tex.png')
render_views(m, base, f'{PREVIEW}/{name}_views.png', views=((35,18),(215,18),(90,8)), size=(760,760), scale=float(sys.argv[2]) if len(sys.argv)>2 else 6, center=(0, float(sys.argv[3]) if len(sys.argv)>3 else 16, 0))
print('ok',time.time()-t)
