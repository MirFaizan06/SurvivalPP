"""Reusable Molang animation sets (quadruped, biped, bird, spider) for the v1.2 mobs."""
from common import *

T = 'q.life_time'
SPD = 'math.clamp(q.modified_move_speed, 0, 1.3)'
PH = 'q.modified_distance_moved * 38.17'


def R(x=0, y=0, z=0):
    return [x, y, z]


def anim(bones, loop=True):
    return {'loop': loop, 'bones': bones}


def look(head='head', neck=None, hy=50, hx=30):
    b = {head: {'rotation': R(f'math.clamp(q.target_x_rotation, -{hx}, {hx})', f'math.clamp(q.target_y_rotation, -{hy}, {hy})')}}
    if neck:
        b[neck] = {'rotation': R(f'math.clamp(q.target_x_rotation, -{hx}, {hx}) * 0.3', f'math.clamp(q.target_y_rotation, -{hy}, {hy}) * 0.3')}
    return anim(b)


def quad(name, amp=38, lower=30, bob=1.0, tail='tail', neck=None, extra_idle=None):
    A = f'animation.ecr_{name}.'
    out = {}
    idle = {
        'body': {'rotation': R(f'math.sin({T}*100)*0.8'), 'position': R(0, f'math.sin({T}*100)*0.2', 0)},
        'head': {'rotation': R(f'math.sin({T}*70)*2', f'math.sin({T}*40)*3')},
    }
    if tail:
        idle[tail] = {'rotation': R(0, f'math.sin({T}*140)*10', f'math.sin({T}*90)*4')}
    if neck:
        idle[neck] = {'rotation': R(f'math.sin({T}*60)*2')}
    if extra_idle:
        idle.update(extra_idle)
    out[A + 'idle'] = anim(idle)
    w = {
        'body': {'rotation': R(f'math.cos({PH}*2)*1.5*{SPD}', 0, f'math.cos({PH})*2*{SPD}'), 'position': R(0, f'math.abs(math.cos({PH}))*{bob}*{SPD}', 0)},
        'leg_fl': {'rotation': R(f'math.cos({PH})*{amp}*{SPD}')},
        'leg_fr': {'rotation': R(f'math.cos({PH} + 180)*{amp}*{SPD}')},
        'leg_bl': {'rotation': R(f'math.cos({PH} + 180)*{amp}*{SPD}')},
        'leg_br': {'rotation': R(f'math.cos({PH})*{amp}*{SPD}')},
        'leg_fl_lower': {'rotation': R(f'(math.max(0, math.sin({PH})) * -{lower})*{SPD}')},
        'leg_fr_lower': {'rotation': R(f'(math.max(0, math.sin({PH} + 180)) * -{lower})*{SPD}')},
        'leg_bl_lower': {'rotation': R(f'(math.max(0, math.sin({PH} + 180)) * {lower})*{SPD}')},
        'leg_br_lower': {'rotation': R(f'(math.max(0, math.sin({PH})) * {lower})*{SPD}')},
        'head': {'rotation': R(f'math.cos({PH}*2 + 40)*3*{SPD}')},
    }
    if tail:
        w[tail] = {'rotation': R(f'-8*{SPD}', f'math.cos({PH})*10*{SPD}')}
    out[A + 'walk'] = anim(w)
    out[A + 'look'] = look('head', neck)
    return out


def bird(name):
    A = f'animation.ecr_{name}.'
    out = {}
    out[A + 'idle'] = anim({
        'body': {'rotation': R(f'math.sin({T}*110)*1.5')},
        'neck': {'rotation': R(f'math.sin({T}*60)*3 + 4')},
        'head': {'rotation': R(f'math.sin({T}*130)*4', f'math.sin({T}*45)*8')},
        'tail': {'rotation': R(f'math.sin({T}*90)*3', f'math.sin({T}*70)*4')},
        'wing_l': {'rotation': R(0, 0, f'math.sin({T}*100)*2')},
        'wing_r': {'rotation': R(0, 0, f'-math.sin({T}*100)*2')},
    })
    out[A + 'walk'] = anim({
        'leg_l': {'rotation': R(f'math.cos({PH}*1.4)*50*{SPD}')},
        'leg_r': {'rotation': R(f'math.cos({PH}*1.4 + 180)*50*{SPD}')},
        'neck': {'rotation': R(f'(math.cos({PH}*2.8)*12 + 8)*{SPD}')},
        'body': {'rotation': R(f'(4 + math.cos({PH}*2.8)*3)*{SPD}'), 'position': R(0, f'math.abs(math.cos({PH}*1.4))*0.6*{SPD}', 0)},
        'tail': {'rotation': R(f'-10*{SPD}', f'math.cos({PH}*1.4)*8*{SPD}')},
    })
    out[A + 'look'] = look('head', 'neck', 70, 30)
    out[A + 'flap'] = anim({
        'wing_l': {'rotation': R(0, 0, f'-math.abs(math.sin({T}*1300))*70 - 15')},
        'wing_r': {'rotation': R(0, 0, f'math.abs(math.sin({T}*1300))*70 + 15')},
        'tail': {'rotation': R(-25)},
    })
    return out


def biped(name, arm=-70, sway=(), leg='leg', shin=None, arm_lo='forearm', shamble=1.0, legamp=38, bob=0.5, bow=False):
    """humanoid: arms held forward, legs swing, hem/rag bones sway"""
    A = f'animation.ecr_{name}.'
    out = {}
    idle = {
        'body': {'rotation': R(f'math.sin({T}*90)*1.2*{shamble}', 0, f'math.sin({T}*60)*1.0')},
        'head': {'rotation': R(f'math.sin({T}*70)*2', f'math.sin({T}*40)*4', f'math.sin({T}*50)*{2*shamble}')},
        'arm_l': {'rotation': R(f'{arm} + math.sin({T}*110)*3', f'{-4 if not bow else 14}', 0)},
        'arm_r': {'rotation': R(f'{arm} + math.sin({T}*110 + 90)*3', f'{4 if not bow else -6}', 0)},
    }
    for sname in sway:
        idle[sname] = {'rotation': R(f'math.sin({T}*120 + {sum(map(ord, sname)) * 37 % 360})*5', 0, f'math.sin({T}*80 + {sum(map(ord, sname)) * 37 % 360})*3')}
    out[A + 'idle'] = anim(idle)
    w = {
        'body': {'rotation': R(f'{3*shamble}*{SPD}', f'math.cos({PH})*4*{SPD}'), 'position': R(0, f'math.abs(math.cos({PH}))*{bob}*{SPD}', 0)},
        f'{leg}_l': {'rotation': R(f'math.cos({PH})*{legamp}*{SPD}')},
        f'{leg}_r': {'rotation': R(f'math.cos({PH} + 180)*{legamp}*{SPD}')},
        'arm_l': {'rotation': R(f'math.cos({PH} + 180)*8*{SPD}', 0, f'math.cos({PH})*3*{SPD}')},
        'arm_r': {'rotation': R(f'math.cos({PH})*8*{SPD}', 0, f'-math.cos({PH})*3*{SPD}')},
    }
    if shin:
        w[f'{shin}_l'] = {'rotation': R(f'math.max(0, math.sin({PH} + 180))*28*{SPD}')}
        w[f'{shin}_r'] = {'rotation': R(f'math.max(0, math.sin({PH}))*28*{SPD}')}
    for sname in sway:
        w[sname] = {'rotation': R(f'-12*{SPD} + math.cos({PH}*2 + {sum(map(ord, sname)) * 37 % 360})*7*{SPD}')}
    out[A + 'walk'] = anim(w)
    out[A + 'look'] = look('head', None, 60, 35)
    # aggro: arms snap up and claw
    out[A + 'aggro'] = anim({
        'arm_l': {'rotation': R(f'-18 + math.sin({T}*900)*10', 0, 0)},
        'arm_r': {'rotation': R(f'-18 + math.sin({T}*900 + 180)*10', 0, 0)} if not bow else {'rotation': R(-88, 4, 0)},
        'head': {'rotation': R(10)},
    })
    out[A + 'cast'] = anim({
        'arm_l': {'rotation': R(f'-150 + math.sin({T}*400)*6', 0, 14)},
        'arm_r': {'rotation': R(f'-150 + math.sin({T}*400 + 90)*6', 0, -14)},
        'head': {'rotation': R(-18)},
        'body': {'rotation': R(-6)},
    })
    out[A + 'attack'] = anim({
        'arm_l': {'rotation': R(f'-70 + math.sin(q.life_time*1500)*55')},
        'arm_r': {'rotation': R(f'-70 + math.sin(q.life_time*1500 + 90)*55')},
        'body': {'rotation': R(f'math.sin(q.life_time*1500)*9')},
    })
    return out


def spider(name, legs=8, amp=22, lift=16):
    A = f'animation.ecr_{name}.'
    out = {}
    idle = {'body': {'position': R(0, f'math.sin({T}*100)*0.25', 0)},
            'head': {'rotation': R(f'math.sin({T}*60)*2', f'math.sin({T}*35)*5')}}
    for i in range(legs):
        s = 1 if i % 2 == 0 else -1
        idle[f'leg{i}'] = {'rotation': R(0, f'math.sin({T}*80 + {i*45})*2', f'math.sin({T}*70 + {i*60})*1.5*{s}')}
    out[A + 'idle'] = anim(idle)
    walk = {'body': {'position': R(0, f'math.abs(math.cos({PH}*1.2))*0.4*{SPD}', 0)}}
    for i in range(legs):
        s = 1 if i % 2 == 0 else -1
        ph = i * 90 + (180 if (i // 2) % 2 else 0) + (0 if s > 0 else 90)
        walk[f'leg{i}'] = {'rotation': R(0, f'math.cos({PH}*1.2 + {ph})*{amp}*{SPD}', f'math.max(0, math.sin({PH}*1.2 + {ph}))*{lift}*{s}*{SPD}')}
    out[A + 'walk'] = anim(walk)
    out[A + 'look'] = look('head', None, 40, 20)
    # rear up and rock when it has a target (web-shooting pose)
    out[A + 'rear'] = anim({
        'body': {'rotation': R(f'-10 + math.sin({T}*400)*2')},
        'head': {'rotation': R(8)},
        'leg0': {'rotation': R(0, f'-10', f'-25')}, 'leg1': {'rotation': R(0, '10', '25')},
    })
    return out


def spores(name):
    """sporeling: waddling toadstool"""
    A = f'animation.ecr_{name}.'
    out = {}
    out[A + 'idle'] = anim({
        'head': {'rotation': R(f'math.sin({T}*80)*2', f'math.sin({T}*35)*6', f'math.sin({T}*55)*4')},
        'body': {'position': R(0, f'math.abs(math.sin({T}*90))*0.3', 0)},
        'arm_l': {'rotation': R(f'math.sin({T}*100)*5', 0, f'-6 + math.sin({T}*70)*3')},
        'arm_r': {'rotation': R(f'math.sin({T}*100 + 90)*5', 0, f'6 - math.sin({T}*70)*3')},
    })
    out[A + 'walk'] = anim({
        'leg_l': {'rotation': R(f'math.cos({PH}*1.5)*45*{SPD}')},
        'leg_r': {'rotation': R(f'math.cos({PH}*1.5 + 180)*45*{SPD}')},
        'arm_l': {'rotation': R(f'math.cos({PH}*1.5 + 180)*40*{SPD}')},
        'arm_r': {'rotation': R(f'math.cos({PH}*1.5)*40*{SPD}')},
        'body': {'rotation': R(0, 0, f'math.cos({PH}*1.5)*6*{SPD}'), 'position': R(0, f'math.abs(math.cos({PH}*1.5))*0.9*{SPD}', 0)},
        'head': {'rotation': R(0, 0, f'math.cos({PH}*1.5 + 90)*8*{SPD}')},
    })
    out[A + 'look'] = look('head', None, 45, 20)
    out[A + 'puff'] = anim({
        'head': {'rotation': R(f'math.sin({T}*1100)*6', 0, f'math.sin({T}*1700)*8'), 'scale': R(f'1 + math.sin({T}*1400)*0.06', f'1 - math.sin({T}*1400)*0.06', f'1 + math.sin({T}*1400)*0.06')},
        'arm_l': {'rotation': R(-30, 0, f'-40 + math.sin({T}*900)*10')},
        'arm_r': {'rotation': R(-30, 0, f'40 - math.sin({T}*900)*10')},
    })
    return out


def write(name, anims):
    wjson(f'{RP}/animations/{name}.animation.json', {'format_version': '1.8.0', 'animations': anims})
