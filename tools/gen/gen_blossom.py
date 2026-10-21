"""Chapter I of the story: The Veiled Blossom (Hanae) + her Blossom Vexes, Veiled Echoes and Petal Blades, the Blossom Altar block, the story items
(Wayfarer's Journal, Veiled Mirror, Blossom Seal), fog definitions and every texture/entity file they need."""
import math, random
from PIL import Image, ImageDraw
from common import *
from registry import *
import mob_hanae, anims2
import gen_bosses
from gen_mobs import glow_overlay, projectile_client, projectile_bp, eff
from gen_items import write_item, shapeless
from gen_blocks import write_block, mi, cat

BOSS = 'veiled_blossom'


# ----------------------------------------------------------------------------- client side
def client(ident, name, geo, anims, animate, egg=None, material='entity_alphatest', glow=True, textures=None, rc=None):
    d = {
        'identifier': ident,
        'materials': {'default': material, 'glow': 'entity_emissive_alpha'} if glow else {'default': material},
        'textures': textures or {'default': f'textures/entity/{name}', 'glow': f'textures/entity/{name}_glow'},
        'geometry': {'default': geo},
        'animations': {a: f'animation.ecr_{name}.{a}' for a in anims},
        'scripts': {'animate': animate},
        'render_controllers': rc or [f'controller.render.ecr_{name}'] + ([f'controller.render.ecr_{name}_glow'] if glow else []),
    }
    if egg:
        d['spawn_egg'] = {'base_color': egg[0], 'overlay_color': egg[1]}
    return {'format_version': '1.10.0', 'minecraft:client_entity': {'description': d}}


def render_controllers():
    skin = "Array.skin[q.property('ecr:phase') == 2 ? 1 : 0]"
    skin_glow = "Array.skin[q.property('ecr:phase') == 2 ? 1 : 0]"
    rc = {
        'controller.render.ecr_veiled_blossom': {
            'arrays': {'textures': {'Array.skin': ['Texture.default', 'Texture.corrupt']}},
            'geometry': 'Geometry.default', 'materials': [{'*': 'Material.default'}], 'textures': [skin]},
        'controller.render.ecr_veiled_blossom_glow': {
            'arrays': {'textures': {'Array.skin': ['Texture.glow', 'Texture.glow_corrupt']}},
            'geometry': 'Geometry.default', 'materials': [{'*': 'Material.glow'}], 'textures': [skin_glow]},
        'controller.render.ecr_blossom_echo': {'geometry': 'Geometry.default', 'materials': [{'*': 'Material.default'}], 'textures': ['Texture.default']},
        'controller.render.ecr_blossom_vex': {'geometry': 'Geometry.default', 'materials': [{'*': 'Material.default'}], 'textures': ['Texture.default']},
        'controller.render.ecr_blossom_vex_glow': {'geometry': 'Geometry.default', 'materials': [{'*': 'Material.glow'}], 'textures': ['Texture.glow']},
    }
    return {'format_version': '1.8.0', 'render_controllers': rc}


# ----------------------------------------------------------------------------- behaviour entities
def bp_vex():
    comps = {
        'minecraft:type_family': {'family': ['blossom_vex', 'ecr_minion', 'ecr_mob', 'monster', 'mob']},
        'minecraft:health': {'value': 6, 'max': 6},
        'minecraft:collision_box': {'width': 0.45, 'height': 0.85},
        'minecraft:movement': {'value': 1.0}, 'minecraft:movement.basic': {}, 'minecraft:jump.static': {},
        'minecraft:navigation.walk': {'can_path_over_water': True, 'using_door_annotation': True},
        'minecraft:physics': {'has_collision': False, 'has_gravity': False},
        'minecraft:attack': {'damage': 2, 'effect_name': 'slowness', 'effect_duration': 2},
        'minecraft:fire_immune': {}, 'minecraft:can_climb': {},
        'minecraft:follow_range': {'value': 40, 'max': 40},
        'minecraft:behavior.float': {'priority': 0},
        'minecraft:behavior.hurt_by_target': {'priority': 1},
        'minecraft:behavior.charge_attack': {'priority': 4},
        'minecraft:behavior.look_at_player': {'priority': 9, 'look_distance': 6},
        'minecraft:behavior.nearest_attackable_target': {'priority': 2, 'must_see': False, 'reselect_targets': True,
                                                         'entity_types': [{'filters': {'test': 'is_family', 'subject': 'other', 'operator': '==', 'value': 'player'}, 'max_dist': 40}]},
        'minecraft:nameable': {}, 'minecraft:despawn': {'despawn_from_distance': {}},
        'minecraft:pushable_by_entity': {}, 'minecraft:pushable_by_block': {}, 'minecraft:conditional_bandwidth_optimization': {},
        'minecraft:is_hidden_when_invisible': {},
        'minecraft:timer': {'time': [16, 20], 'looping': False, 'time_down_event': {'event': 'ecr:expire'}},
        'minecraft:experience_reward': {'on_death': 'query.last_hit_by_player ? 3 : 0'},
    }
    return {'format_version': '1.26.50', 'minecraft:entity': {
        'description': {'identifier': f'{NS}:blossom_vex', 'is_spawnable': False, 'is_summonable': True, 'spawn_category': 'monster'},
        'component_groups': {'ecr:despawn': {'minecraft:instant_despawn': {}}}, 'components': comps,
        'events': {'ecr:expire': {'add': {'component_groups': ['ecr:despawn']}}}}}


def bp_echo():
    comps = {
        'minecraft:type_family': {'family': ['blossom_echo', 'ecr_minion', 'ecr_mob', 'monster', 'mob']},
        'minecraft:health': {'value': 1, 'max': 1},
        'minecraft:collision_box': {'width': 0.9, 'height': 2.5},
        'minecraft:movement': {'value': 0.26}, 'minecraft:movement.basic': {}, 'minecraft:jump.static': {},
        'minecraft:navigation.walk': {'can_path_over_water': True, 'avoid_water': False, 'can_pass_doors': True},
        'minecraft:behavior.float': {'priority': 0},
        'minecraft:behavior.avoid_mob_type': {'priority': 2, 'entity_types': [{'filters': {'test': 'is_family', 'subject': 'other', 'operator': '==', 'value': 'player'}, 'max_dist': 6, 'walk_speed_multiplier': 1.0, 'sprint_speed_multiplier': 1.3}]},
        'minecraft:behavior.random_stroll': {'priority': 5, 'speed_multiplier': 0.9},
        'minecraft:behavior.look_at_player': {'priority': 7, 'look_distance': 12, 'probability': 0.05},
        'minecraft:nameable': {}, 'minecraft:physics': {}, 'minecraft:pushable_by_entity': {}, 'minecraft:pushable_by_block': {},
        'minecraft:conditional_bandwidth_optimization': {}, 'minecraft:is_hidden_when_invisible': {}, 'minecraft:fire_immune': {},
        'minecraft:timer': {'time': [28, 34], 'looping': False, 'time_down_event': {'event': 'ecr:expire'}},
    }
    return {'format_version': '1.26.50', 'minecraft:entity': {
        'description': {'identifier': f'{NS}:blossom_echo', 'is_spawnable': False, 'is_summonable': True, 'spawn_category': 'monster'},
        'component_groups': {'ecr:despawn': {'minecraft:instant_despawn': {}}}, 'components': comps,
        'events': {'ecr:expire': {'add': {'component_groups': ['ecr:despawn']}}}}}


# ----------------------------------------------------------------------------- sprites
def petal_sprite():
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y in range(16):
        for x in range(16):
            u, v = (x - 7.5) / 3.6, (y - 7.5) / 6.6
            d = u * u + v * v
            if d <= 1.0:
                t = 1 - d
                c = ramp_at(mob_hanae.PINK, 0.5 + 0.5 * t) if v < 0.2 else ramp_at(mob_hanae.PINK, 0.35 + 0.5 * t)
                a = 255
            elif d <= 1.7:
                c = ramp_at(mob_hanae.PINK, 0.3); a = 150
            else:
                continue
            im.putpixel((x, y), c + (a,))
    im.putpixel((7, 2), (255, 255, 255, 255)); im.putpixel((8, 3), (255, 255, 255, 255))
    return im


def spr(rows, pal):
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row[:16]):
            if ch in pal:
                im.putpixel((x, y), pal[ch] + (255,))
    return im


def journal_sprite():
    pal = {'k': hx('#14061a'), 'p': hx('#3a1c4c'), 'P': hx('#582a6c'), 'q': hx('#241030'), 'g': hx('#d9a830'), 'G': hx('#fff0a8'), 'r': hx('#dc7aa4'), 'R': hx('#ffd2e4'), 'c': hx('#c8284a'), 'w': hx('#ecdccb')}
    return spr([
        '................', '..kkkkkkkkkkkk..', '.kqppPPPPPPPPpk.', '.kqpPPPPPPPPPpk.', '.kqpPgGGGGgPPpk.', '.kqpPgPrRPgPPpk.', '.kqpPgrRRrgPPpk.', '.kqpPgPrrPgPPpk.',
        '.kqpPgGGGGgPPpk.', '.kqpPPPPPPPPPpk.', '.kqppPPPPPPPppk.', '.kwwwwwwwwwwwwk.', '.kkkkkkkkkcckk..', '.........cc.....', '.........cc.....', '................'], pal)


def mirror_sprite():
    pal = {'k': hx('#3a1a28'), 'g': hx('#d9a830'), 'G': hx('#fff0a8'), 'r': hx('#dc7aa4'), 'R': hx('#ffd2e4'), 'b': hx('#bfe6ff'), 'B': hx('#eaf8ff'), 'm': hx('#8ab8d8'), 'w': hx('#ffffff')}
    return spr([
        '................', '.....kkkkkk.....', '...kkggGGggkk...', '..kgGbbBBbbGgk..', '.kgGbBBwBBbbGgk.', '.kgbBBwBbbmbbgk.', '.kgbBwBbbmmbbgk.', '.kgbBBbbmmmbbgk.',
        '.kgGbbbmmmbbGgk.', '..kgGbbmmbbGgk..', '...kkgGGGggkk...', '.....kgGgk......', '......kgGk......', '.......kgrk.....', '........krRk....', '.........kk.....'], pal)


def seal_sprite():
    pal = {'k': hx('#5a1a3a'), 'g': hx('#d9a830'), 'G': hx('#fff0a8'), 'a': hx('#a8466f'), 'b': hx('#dc7aa4'), 'c': hx('#f6a8c8'), 'd': hx('#ffe6f0'), 'e': hx('#c8284a')}
    return spr([
        '................', '.....kkkkkk.....', '...kkgGGGGgkk...', '..kgGbbbbbbGgk..', '.kgGbbbdcbbbGgk.', '.kgbbbdddcbbbgk.', '.kgbbdddddcbbgk.', '.kgbdddGGdddcbgk',
        '.kgbbdddddcbbgk.', '.kgbbbdddcbbbgk.', '..kgGbbcbbbGgk..', '...kkgGGGGgkk...', '.....kkeekk.....', '......eeee......', '......eeee......', '.......ee.......'], pal)


# ----------------------------------------------------------------------------- Blossom Altar block
def altar_textures():
    SK = mob_hanae.PINK
    for part in ('top', 'side', 'bottom'):
        img = Image.new('RGBA', (16, 16))
        px = img.load()
        rng = random.Random(7 + len(part))
        for y in range(16):
            for x in range(16):
                n = (math.sin(x * 0.9 + y * 0.4) + math.sin(y * 1.1 - x * 0.3)) * 0.12 + rng.random() * 0.12
                c = ramp_at(SK, 0.62 + n)
                if x in (0, 15) or y in (0, 15):
                    c = tuple(int(v * (1.15 if (x == 0 or y == 0) else 0.7)) for v in c)
                px[x, y] = tuple(min(255, v) for v in c) + (255,)
        if part == 'top':
            for k in range(5):                                      # carved five-petal flower
                a = k / 5 * math.tau - math.pi / 2
                cx, cy = 7.5 + math.cos(a) * 3.2, 7.5 + math.sin(a) * 3.2
                for y in range(16):
                    for x in range(16):
                        if math.hypot(x + 0.5 - cx - 0.5, y + 0.5 - cy - 0.5) < 2.4:
                            px[x, y] = ramp_at(SK, 0.92 - 0.1 * math.hypot(x - 7.5, y - 7.5) / 5) + (255,)
            for y in range(6, 10):
                for x in range(6, 10):
                    px[x, y] = ramp_at(mob_hanae.GOLD, 0.8) + (255,)
            for (x, y) in ((2, 2), (13, 2), (2, 13), (13, 13)):
                px[x, y] = ramp_at(mob_hanae.GOLD, 0.7) + (255,)
        if part == 'side':
            for x in range(16):
                for y in (4, 11):
                    px[x, y] = ramp_at(mob_hanae.GOLD, 0.45) + (255,)
                for y in range(5, 11):
                    c = px[x, y]
                    px[x, y] = tuple(int(v * 0.72) for v in c[:3]) + (255,)
            for cx in (3, 8, 13):
                for (dx, dy) in ((0, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)):
                    px[(cx + dx) % 16, 7 + dy] = ramp_at(SK, 0.95) + (255,)
        save_png(img, f'{RP}/textures/blocks/blossom_altar_{part}.png')


def altar_block():
    altar_textures()
    t_top, t_side, t_bot = terrain('blossom_altar_top'), terrain('blossom_altar_side'), terrain('blossom_altar_bottom')
    comps = {
        'minecraft:geometry': 'minecraft:geometry.full_block',
        'minecraft:material_instances': {'*': mi(t_side), 'up': mi(t_top), 'down': mi(t_bot), 'side': mi(t_side)},
        'minecraft:tags': ['minecraft:is_pickaxe_item_destructible', 'stone'],
        'minecraft:destructible_by_mining': {'seconds_to_destroy': 30.0},
        'minecraft:destructible_by_explosion': {'explosion_resistance': 1200.0},
        'minecraft:light_emission': 5, 'minecraft:map_color': '#f6a8c8',
        f'{NS}:blossom_altar': {},
    }
    write_block('blossom_altar', {'identifier': f'{NS}:blossom_altar', 'menu_category': cat('construction')}, comps, sound='stone')
    lang_block('blossom_altar', 'Blossom Altar')


# ----------------------------------------------------------------------------- items
def story_items():
    for name, title, fn, extra in (
            ('wayfarers_journal', "Wayfarer's Journal", journal_sprite, {'minecraft:rarity': {'value': 'rare'}}),
            ('veiled_mirror', 'Veiled Mirror', mirror_sprite, {'minecraft:rarity': {'value': 'rare'}, 'minecraft:glint': True}),
            ('blossom_seal', 'Seal of the Blossom', seal_sprite, {'minecraft:rarity': {'value': 'epic'}, 'minecraft:glint': True})):
        save_png(fn(), f'{RP}/textures/items/{name}.png')
        comps = {'minecraft:icon': {'textures': {'default': itemtex(name)}}, 'minecraft:max_stack_size': 1}
        comps.update(extra)
        write_item(name, comps, 'items')
        lang_item(name, title)
    # a lost journal can be rewritten (progress is stored on the player, not on the book)
    shapeless('wayfarers_journal', ['minecraft:book', 'minecraft:ink_sac', 'minecraft:pink_petals'], f'{NS}:wayfarers_journal')


# ----------------------------------------------------------------------------- fog
def fogs():
    def fog(name, start, end, colour):
        wjson(f'{RP}/fogs/{name}.json', {'format_version': '1.21.90', 'minecraft:fog_settings': {
            'description': {'identifier': f'{NS}:{name}'},
            'distance': {'air': {'fog_start': start, 'fog_end': end, 'fog_color': colour, 'render_distance_type': 'fixed'}}}})
    fog('blossom_veil', 4, 64, '#f3c4da')
    fog('blossom_storm', 1, 30, '#e88ab4')
    fog('eclipse_bloom', 0, 20, '#3a0818')


# ----------------------------------------------------------------------------- build
def build():
    builder, mats, gid = mob_hanae.MODELS[BOSS]
    m = builder(); m.pack()
    base, glow = m.paint(mats(False))
    base_c, glow_c = m.paint(mats(True))
    save_tga(base, f'{RP}/textures/entity/{BOSS}.tga'); save_tga(glow_overlay(glow), f'{RP}/textures/entity/{BOSS}_glow.tga')
    save_tga(base_c, f'{RP}/textures/entity/{BOSS}_corrupt.tga'); save_tga(glow_overlay(glow_c), f'{RP}/textures/entity/{BOSS}_glow_corrupt.tga')
    # echo: the same model as a translucent, cooler ghost
    ghost = base.copy()
    gp = ghost.load()
    for y in range(ghost.height):
        for x in range(ghost.width):
            r, g, b, a = gp[x, y]
            if a:
                gp[x, y] = (int(r * 0.8 + 40), int(g * 0.85 + 30), min(255, int(b * 0.9 + 70)), 120)
    save_png(ghost, f'{RP}/textures/entity/blossom_echo.png')
    wjson(f'{RP}/models/entity/{BOSS}.geo.json', m.export())
    anims2.write(BOSS, anims2.hanae(BOSS))
    notcast = "!q.property('ecr:casting')"
    wjson(f'{RP}/entity/{BOSS}.entity.json', client(
        f'{NS}:{BOSS}', BOSS, gid, ['idle', 'walk', 'look', 'attack', 'cast'],
        ['idle', {'walk': 'q.modified_move_speed > 0.02'}, 'look', {'attack': f'q.is_delayed_attacking && {notcast}'}, {'cast': "q.property('ecr:casting')"}],
        egg=gen_bosses.BOSSES[BOSS]['egg'],
        textures={'default': f'textures/entity/{BOSS}', 'corrupt': f'textures/entity/{BOSS}_corrupt', 'glow': f'textures/entity/{BOSS}_glow', 'glow_corrupt': f'textures/entity/{BOSS}_glow_corrupt'},
        rc=['controller.render.ecr_veiled_blossom', 'controller.render.ecr_veiled_blossom_glow']))
    # echo (shares the model + animations, plays idle/walk/look only)
    anims2.write('blossom_echo', {k.replace('veiled_blossom', 'blossom_echo'): v for k, v in anims2.hanae(BOSS).items() if not k.endswith(('attack', 'cast'))})
    wjson(f'{RP}/entity/blossom_echo.entity.json', client(
        f'{NS}:blossom_echo', 'blossom_echo', gid, ['idle', 'walk', 'look'], ['idle', {'walk': 'q.modified_move_speed > 0.02'}, 'look'],
        material='entity_alphablend', glow=False, textures={'default': 'textures/entity/blossom_echo'}))
    # vex
    vb, vm, vgid = mob_hanae.MODELS['blossom_vex']
    v = vb(); v.pack()
    vbase, vglow = v.paint(vm())
    save_tga(vbase, f'{RP}/textures/entity/blossom_vex.tga'); save_tga(glow_overlay(vglow), f'{RP}/textures/entity/blossom_vex_glow.tga')
    wjson(f'{RP}/models/entity/blossom_vex.geo.json', v.export())
    anims2.write('blossom_vex', anims2.blossom_vex())
    wjson(f'{RP}/entity/blossom_vex.entity.json', client(
        f'{NS}:blossom_vex', 'blossom_vex', vgid, ['idle', 'charge', 'look'], ['idle', {'charge': 'q.has_target'}, 'look']))
    wjson(f'{RP}/render_controllers/ecr_blossom.render_controllers.json', render_controllers())
    # behaviour
    wjson(f'{BP}/entities/{BOSS}.json', gen_bosses.bp(BOSS, gen_bosses.BOSSES[BOSS]))
    wjson(f'{BP}/entities/blossom_vex.json', bp_vex())
    wjson(f'{BP}/entities/blossom_echo.json', bp_echo())
    wjson(f'{BP}/loot_tables/entities/{BOSS}.json', {'pools': gen_bosses.LOOT[BOSS]})
    # projectile
    save_png(petal_sprite(), f'{RP}/textures/entity/petal_blade.png')
    wjson(f'{RP}/entity/petal_blade.entity.json', projectile_client(f'{NS}:petal_blade', 'petal_blade', '1.5'))
    wjson(f'{BP}/entities/petal_blade.json', projectile_bp(f'{NS}:petal_blade', 1.5, (2, 3), [eff('slowness', 0, 40, 60, 80)], 'witchspell', gravity=0.0))
    for ident, title in (('veiled_blossom', 'The Veiled Blossom'), ('blossom_vex', 'Blossom Vex'), ('blossom_echo', 'Veiled Echo'), ('petal_blade', 'Petal Blade')):
        LANG[f'entity.{NS}:{ident}.name'] = title
    LANG[f'item.spawn_egg.entity.{NS}:{BOSS}.name'] = 'The Veiled Blossom Spawn Egg'
    altar_block()
    story_items()
    fogs()


if __name__ == '__main__':
    build()
    print('blossom ok')
