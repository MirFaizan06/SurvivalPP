"""Animation JSON for the Ashen Warg, Voidweaver and Eclipse Sovereign (Molang driven, loop-safe)."""
from common import *

S = lambda e: e if isinstance(e, str) else e


def anim(loop=True, bones=None, length=None, override=False):
    d = {'loop': loop, 'bones': bones or {}}
    if length:
        d['animation_length'] = length
    if override:
        d['override_previous_animation'] = True
    return d


def R(x=0, y=0, z=0):
    return [x, y, z]


# ======================================================================== ASHEN WARG
def warg():
    A = 'animation.ecr_ashen_warg.'
    t = 'q.life_time'
    spd = 'math.clamp(q.modified_move_speed, 0, 1.3)'
    ph = 'q.modified_distance_moved * 38.17'
    out = {}
    out[A + 'idle'] = anim(True, {
        'body': {'rotation': R(f'math.sin({t}*120)*0.9'), 'position': R(0, f'math.sin({t}*120)*0.25', 0)},
        'neck': {'rotation': R(f'math.sin({t}*90)*2', f'math.sin({t}*45)*3')},
        'head': {'rotation': R(f'math.sin({t}*70)*1.5', f'math.sin({t}*33)*3')},
        'jaw': {'rotation': R(f'4 + math.sin({t}*150)*3')},
        'tail1': {'rotation': R(f'math.sin({t}*60)*3', f'math.sin({t}*70)*10')},
        'tail2': {'rotation': R(0, f'math.sin({t}*70 - 40)*14')},
        'tail3': {'rotation': R(0, f'math.sin({t}*70 - 80)*18')},
        'fl_upper': {'rotation': R(f'math.sin({t}*50)*1.5')},
        'fr_upper': {'rotation': R(f'-math.sin({t}*50)*1.5')},
    })
    # diagonal gait: fl & hr together, fr & hl together
    def leg(up_phase, lo_phase):
        return up_phase, lo_phase
    walk = {
        'body': {'rotation': R(f'math.cos({ph}*2)*2*{spd}', 0, f'math.cos({ph})*2.5*{spd}'),
                 'position': R(0, f'math.abs(math.cos({ph}))*1.1*{spd}', 0)},
        'neck': {'rotation': R(f'math.cos({ph}*2 + 60)*3*{spd}')},
        'tail1': {'rotation': R(f'-12*{spd}', f'math.cos({ph})*9*{spd}')},
        'tail2': {'rotation': R(0, f'math.cos({ph} - 40)*12*{spd}')},
        'tail3': {'rotation': R(0, f'math.cos({ph} - 80)*16*{spd}')},
        'fl_upper': {'rotation': R(f'math.cos({ph})*48*{spd}')},
        'fl_lower': {'rotation': R(f'(math.max(0, math.sin({ph})) * -34 + 10)*{spd}')},
        'fl_paw': {'rotation': R(f'math.max(0, math.sin({ph}))*18*{spd}')},
        'fr_upper': {'rotation': R(f'math.cos({ph} + 180)*48*{spd}')},
        'fr_lower': {'rotation': R(f'(math.max(0, math.sin({ph} + 180)) * -34 + 10)*{spd}')},
        'fr_paw': {'rotation': R(f'math.max(0, math.sin({ph} + 180))*18*{spd}')},
        'hl_thigh': {'rotation': R(f'math.cos({ph} + 180)*42*{spd}')},
        'hl_shin': {'rotation': R(f'(math.max(0, math.sin({ph} + 180)) * 30)*{spd}')},
        'hl_foot': {'rotation': R(f'(math.max(0, -math.sin({ph} + 180)) * 22 - 8)*{spd}')},
        'hr_thigh': {'rotation': R(f'math.cos({ph})*42*{spd}')},
        'hr_shin': {'rotation': R(f'(math.max(0, math.sin({ph})) * 30)*{spd}')},
        'hr_foot': {'rotation': R(f'(math.max(0, -math.sin({ph})) * 22 - 8)*{spd}')},
    }
    out[A + 'walk'] = anim(True, walk)
    out[A + 'look'] = anim(True, {
        'head': {'rotation': R('math.clamp(q.target_x_rotation, -35, 35)', 'math.clamp(q.target_y_rotation, -50, 50)')},
        'neck': {'rotation': R('math.clamp(q.target_x_rotation, -25, 25) * 0.3', 'math.clamp(q.target_y_rotation, -50, 50) * 0.3')},
    })
    a = 'math.sin(v.attack_time*180)'
    out[A + 'attack'] = anim(True, {
        'body': {'position': R(0, 0, f'-{a}*3.2'), 'rotation': R(f'{a}*6')},
        'neck': {'rotation': R(f'{a}*12')},
        'head': {'rotation': R(f'{a}*10')},
        'jaw': {'rotation': R(f'{a}*40')},
        'fl_upper': {'rotation': R(f'-{a}*55')},
        'fr_upper': {'rotation': R(f'-{a}*45')},
    })
    # when hunting: hackles up, ember mane flares (head lowered, tail raised)
    out[A + 'hunt'] = anim(True, {
        'neck': {'rotation': R(10)},
        'head': {'rotation': R(-6)},
        'jaw': {'rotation': R(f'10 + math.sin({t}*220)*6')},
        'tail1': {'rotation': R(-10)},
    })
    return out


# ======================================================================== VOIDWEAVER
def voidweaver():
    A = 'animation.ecr_voidweaver.'
    t = 'q.life_time'
    out = {}
    bones = {
        'float': {'position': R(0, f'2.4 + math.sin({t}*105)*1.6', 0)},
        'body': {'rotation': R(f'math.sin({t}*75)*1.2', f'math.sin({t}*40)*2.5', f'math.sin({t}*55)*1.5')},
        'head': {'rotation': R(f'math.sin({t}*62)*2', f'math.sin({t}*38)*3')},
        'crown': {'rotation': R(0, f'-{t}*55', 0), 'position': R(0, f'math.sin({t}*130)*0.9', 0)},
        'orbit': {'rotation': R(0, f'{t}*80', 0)},
        'arm_l': {'rotation': R(f'math.sin({t}*70)*3', 0, f'math.sin({t}*60)*2')},
        'arm_r': {'rotation': R(f'-math.sin({t}*70)*3', 0, f'-math.sin({t}*60)*2')},
        'forearm_l': {'rotation': R(f'-math.sin({t}*85)*4')},
        'forearm_r': {'rotation': R(f'math.sin({t}*85)*4')},
    }
    for k in range(8):
        bones[f'hem{k}'] = {'rotation': R(f'math.sin({t}*130 + {k*45})*8', 0, f'math.sin({t}*110 + {k*60})*6')}
    for k in range(5):
        bones[f'cape{k}'] = {'rotation': R(f'10 + math.sin({t}*100 + {k*55})*10', 0, f'math.sin({t}*80 + {k*70})*4')}
    out[A + 'idle'] = anim(True, bones)
    spd = 'math.clamp(q.modified_move_speed, 0, 1.3)'
    wb = {'body': {'rotation': R(f'{spd}*9')}, 'head': {'rotation': R(f'-{spd}*5')}}
    for k in range(8):
        wb[f'hem{k}'] = {'rotation': R(f'{spd}*(16 + {k%3}*4)')}
    for k in range(5):
        wb[f'cape{k}'] = {'rotation': R(f'{spd}*22')}
    out[A + 'walk'] = anim(True, wb)
    out[A + 'look'] = anim(True, {'head': {'rotation': R('math.clamp(q.target_x_rotation, -30, 30)', 'math.clamp(q.target_y_rotation, -60, 60)')}})
    # casting stance while hunting: arms lifted, shards spin faster, crown flares
    out[A + 'combat'] = anim(True, {
        'arm_l': {'rotation': R(-34, 0, f'-14 + math.sin({t}*200)*3')},
        'arm_r': {'rotation': R(-34, 0, f'14 - math.sin({t}*200)*3')},
        'forearm_l': {'rotation': R(-62)},
        'forearm_r': {'rotation': R(-62)},
        'orbit': {'rotation': R(0, f'{t}*210', 0)},
        'crown': {'position': R(0, 3, 0)},
        'head': {'rotation': R(-6)},
    })
    return out


# ======================================================================== ECLIPSE SOVEREIGN
def boss():
    A = 'animation.ecr_eclipse_sovereign.'
    t = 'q.life_time'
    ph = "q.property('ecr:phase')"
    out = {}
    bones = {
        'float': {'position': R(0, f'3 + math.sin({t}*75)*2.4', 0)},
        'body': {'rotation': R(f'math.sin({t}*60)*1.2', f'math.sin({t}*30)*2', 0)},
        'head': {'rotation': R(f'math.sin({t}*52)*1.5', f'math.sin({t}*26)*2')},
        'halo': {'rotation': R(0, 0, f'{t}*(18 + 26*{ph})')},
        'orbit': {'rotation': R(0, f'{t}*(55 + 35*{ph})', 0)},
        'arm_l': {'rotation': R(f'math.sin({t}*60)*2', 0, f'math.sin({t}*50)*1.5')},
        'arm_r': {'rotation': R(f'-math.sin({t}*60)*2', 0, f'-math.sin({t}*50)*1.5')},
        'forearm_l': {'rotation': R(f'-math.sin({t}*70)*3')},
        'forearm_r': {'rotation': R(f'math.sin({t}*70)*3')},
    }
    for i, n in enumerate(['tail1', 'tail2', 'tail3', 'tail4']):
        bones[n] = {'rotation': R(f'math.sin({t}*75 - {i*35})*{3 + i*2}', f'math.sin({t}*50 - {i*30})*{2 + i}', f'math.sin({t}*60 - {i*40})*{4 + i*3}')}
    for k in range(7):
        bones[f'cape{k}'] = {'rotation': R(f'7 + math.sin({t}*90 + {k*50})*7', 0, f'math.sin({t}*70 + {k*60})*3')}
    out[A + 'idle'] = anim(True, bones)
    spd = 'math.clamp(q.modified_move_speed, 0, 1.3)'
    ph2 = 'q.modified_distance_moved * 22'
    wb = {
        'body': {'rotation': R(f'{spd}*7')},
        'head': {'rotation': R(f'-{spd}*4')},
        'tail1': {'rotation': R(f'-{spd}*10')},
        'arm_l': {'rotation': R(f'math.cos({ph2})*10*{spd}')},
        'arm_r': {'rotation': R(f'-math.cos({ph2})*10*{spd}')},
    }
    for k in range(7):
        wb[f'cape{k}'] = {'rotation': R(f'{spd}*14')}
    out[A + 'walk'] = anim(True, wb)
    out[A + 'look'] = anim(True, {'head': {'rotation': R('math.clamp(q.target_x_rotation, -25, 25)', 'math.clamp(q.target_y_rotation, -55, 55)')}})
    a = 'math.sin(v.attack_time*180)'
    out[A + 'slam'] = anim(True, {
        'body': {'rotation': R(f'{a}*16')},
        'head': {'rotation': R(f'{a}*10')},
        'arm_l': {'rotation': R(f'-{a}*115', 0, f'-{a}*6')},
        'arm_r': {'rotation': R(f'-{a}*115', 0, f'{a}*6')},
        'forearm_l': {'rotation': R(f'-{a}*20')},
        'forearm_r': {'rotation': R(f'-{a}*20')},
    })
    out[A + 'combat'] = anim(True, {
        'halo': {'rotation': R(0, 0, f'{t}*40')},
        'arm_l': {'rotation': R(-8, 0, -6)},
        'arm_r': {'rotation': R(-8, 0, 6)},
        'forearm_l': {'rotation': R(-28)},
        'forearm_r': {'rotation': R(-28)},
        'head': {'rotation': R(-4)},
    })
    # summoning / casting pose (property driven, used in phase 2+)
    out[A + 'cast'] = anim(True, {
        'arm_l': {'rotation': R(-22, 0, f'-68 + math.sin({t}*260)*4')},
        'arm_r': {'rotation': R(-22, 0, f'68 - math.sin({t}*260)*4')},
        'forearm_l': {'rotation': R(-38)},
        'forearm_r': {'rotation': R(-38)},
        'body': {'rotation': R(-6)},
        'head': {'rotation': R(-12)},
        'halo': {'rotation': R(0, 0, f'{t}*260')},
        'float': {'position': R(0, f'9 + math.sin({t}*200)*1.4', 0)},
    })
    return out


def write_all():
    for fn, nm in ((warg, 'ashen_warg'), (voidweaver, 'voidweaver'), (boss, 'eclipse_sovereign')):
        wjson(f'{RP}/animations/{nm}.animation.json', {'format_version': '1.8.0', 'animations': fn()})


if __name__ == '__main__':
    write_all()
    print('anims ok')
