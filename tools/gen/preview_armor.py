"""python preview_armor.py  ->  <build>/preview/armor_all.png (3D renders of every piece on a posed mannequin-less view + icons)"""
import sys
from PIL import Image
from common import *
import armor_models as A
import geo

sheet = Image.new('RGB', (4 * 330, 4 * 330 + 0), (46, 46, 52))
icons = Image.new('RGBA', (16 * 36, 40), (60, 60, 70, 255))
n = 0
for r, mat in enumerate(A.DESIGNS):
    for c, piece in enumerate(A.PIECES):
        m, base = A.build_model(mat, piece)
        geo.GAIN = 1.3
        im = geo.render(m, base, None, yaw=30, pitch=-8, scale=A.SCALE[piece] * 0.8, size=(330, 330), center=A.CENTER[piece])
        sheet.paste(im, (c * 330, r * 330))
        icons.alpha_composite(A.icon(m, base, piece), (n * 36 + 2, 4)); n += 1
sheet.save(f'{PREVIEW}/armor_all.png')
icons.resize((icons.width * 3, icons.height * 3), Image.NEAREST).save(f'{PREVIEW}/armor_icons.png')
print('ok')
