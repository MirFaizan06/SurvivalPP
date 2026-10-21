"""Global registries filled while generating (terrain/item textures, lang strings, creative groups)."""
from common import *

TERRAIN = {}     # key -> texture path
ITEMTEX = {}
LANG = {}        # key -> value (resource pack en_US.lang)
BLOCK_SOUND = {}  # block id -> sound set for blocks.json
BLOCK_IDS = []
ITEM_IDS = []
WOOD_ITEMS = []   # block-placer items for wood blocks (fuel / tags / 3D icons)


def terrain(key, path=None):
    TERRAIN[f'ecr_{key}'] = f'textures/blocks/{path or key}'
    return f'ecr_{key}'


def itemtex(key, path=None):
    ITEMTEX[f'ecr_{key}'] = f'textures/items/{path or key}'
    return f'ecr_{key}'


def lang_block(ident, name):
    LANG[f'tile.{NS}:{ident}.name'] = name


def lang_item(ident, name):
    LANG[f'item.{NS}:{ident}'] = name
    LANG[f'item.{NS}:{ident}.name'] = name


def write_registries():
    wjson(f'{RP}/textures/terrain_texture.json', {
        'resource_pack_name': 'ecr', 'texture_name': 'atlas.terrain', 'padding': 8, 'num_mip_levels': 4,
        'texture_data': {k: {'textures': v} for k, v in sorted(TERRAIN.items())}})
    wjson(f'{RP}/textures/item_texture.json', {
        'resource_pack_name': 'ecr', 'texture_name': 'atlas.items',
        'texture_data': {k: {'textures': v} for k, v in sorted(ITEMTEX.items())}})
    bl = {'format_version': [1, 1, 0]}
    for b, s in BLOCK_SOUND.items():
        bl[b] = {'sound': s}
    wjson(f'{RP}/blocks.json', bl)
    lines = [f'{k}={v}' for k, v in LANG.items()]
    wtext(f'{RP}/texts/en_US.lang', '\n'.join(lines) + '\n')
    wjson(f'{RP}/texts/languages.json', ['en_US'])
    # behaviour pack lang (some clients read names from here)
    wtext(f'{BP}/texts/en_US.lang', '\n'.join(lines) + '\n')
    wjson(f'{BP}/texts/languages.json', ['en_US'])
