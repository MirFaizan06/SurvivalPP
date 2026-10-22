"""Boss music: copies the OGG tracks from tools/assets/music into the resource pack and registers them as sound definitions
(played by tools/scripts/music.js).  See tools/assets/music/CREDITS.md for sources and licences (all CC0)."""
import os, shutil
from common import *

TRACKS = {'veiled_blossom': 0.85, 'eclipse_sovereign': 0.85, 'frost_cantor': 0.85, 'mire_lantern': 0.85,
          'cinder_bride': 0.9, 'ashen_groom': 0.9}
SRC = ROOT / 'tools' / 'assets' / 'music'


def build():
    defs = {}
    for name, vol in TRACKS.items():
        dst = f'{RP}/sounds/music/{name}.ogg'
        ensure(dst)
        shutil.copyfile(SRC / f'{name}.ogg', dst)
        defs[f'ecr.music.{name}'] = {'category': 'music',
                                     'sounds': [{'name': f'sounds/music/{name}', 'stream': True, 'volume': vol, 'load_on_low_memory': False}]}
    wjson(f'{RP}/sounds/sound_definitions.json', {'format_version': '1.14.0', 'sound_definitions': defs})
