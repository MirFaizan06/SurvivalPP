"""Animations for the Burning Deep bosses: the Cinder Bride (hovering bride with a hammer), the Ashen Groom (swordsman), the Forged Blade."""
from anims3 import *


def bride(name='cinder_bride'):
    A = f'animation.ecr_{name}.'
    out = {}
    idle = {
        'float': {'position': R(0, f'2.0 + math.sin({T}*70)*1.2', 0)},
        'body': {'rotation': R(f'math.sin({T}*55)*1.4', f'math.sin({T}*30)*3', f'math.sin({T}*45)*1.4')},
        'head': {'rotation': R(f'math.sin({T}*65)*2', f'math.sin({T}*28)*7', f'math.sin({T}*40)*2')},
        'arm_r': {'rotation': R(f'-18 + math.sin({T}*80)*3', 0, f'math.sin({T}*60)*2')},
        'arm_l': {'rotation': R(f'-26 + math.sin({T}*80 + 90)*4', 0, f'math.sin({T}*60)*2')},
        'hammer': {'rotation': R(f'math.sin({T}*50)*3', 0, f'8 + math.sin({T}*40)*2')},
        'ring': {'rotation': R(0, 0, f'{T}*90')},
        'blades': {'rotation': R(0, f'{T}*60', 0)},
        'halo': {'rotation': R(0, 0, f'{T}*30')},
        'veil': sway('veil', 17, 7),
    }
    for i in range(6):
        idle[f'train{i}'] = {'rotation': R(f'math.sin({T}*{60 + i * 6} + {i * 40})*{3 + i * 0.8}', f'math.sin({T}*{40 + i * 5} + {i * 70})*{4 + i}')}
    for i in range(5):
        idle[f'hair{i}'] = sway(f'hair{i}', i * 50 + 11, 5)
    for tag in 'lr':
        idle[f'sleeve_{tag}'] = sway(f'sleeve_{tag}', 90 if tag == 'l' else 140, 6)
    out[A + 'idle'] = anim(idle)
    w = {'body': {'rotation': R(f'6*{SPD}', 0, 0)}, 'float': {'position': R(0, f'math.abs(math.sin({PH}*0.5))*0.8*{SPD}', 0)}}
    for i in range(6):
        w[f'train{i}'] = {'rotation': R(f'-{3 + i}*{SPD}', f'math.sin({PH}*0.5 + {i * 50})*{4 + i}*{SPD}')}
    out[A + 'walk'] = anim(w)
    out[A + 'look'] = look('head', None, 55, 28)
    out[A + 'attack'] = anim({
        'arm_r': {'rotation': R(f'-140 + math.sin(q.life_time*1300)*110', 0, 6)},
        'hammer': {'rotation': R(f'math.sin(q.life_time*1300)*20')},
        'body': {'rotation': R(f'math.sin(q.life_time*1300)*12', f'math.sin(q.life_time*1300)*-16')},
    })
    out[A + 'cast'] = anim({
        'arm_r': {'rotation': R(-170, 0, -14)}, 'arm_l': {'rotation': R(-150, 0, 22)},
        'ring': {'rotation': R(0, 0, f'{T}*420')}, 'blades': {'rotation': R(0, f'{T}*260', 0)}, 'halo': {'rotation': R(0, 0, f'{T}*140')},
        'head': {'rotation': R(-18)}, 'body': {'rotation': R(-7)},
        'float': {'position': R(0, f'6 + math.sin({T}*220)*1.5', 0)},
    })
    return out


def groom(name='ashen_groom'):
    A = f'animation.ecr_{name}.'
    out = {}
    idle = {
        'body': {'rotation': R(f'math.sin({T}*70)*1.6', f'math.sin({T}*34)*3', f'math.sin({T}*50)*1.2'), 'position': R(0, f'math.sin({T}*70)*0.3', 0)},
        'head': {'rotation': R(f'math.sin({T}*60)*2', f'math.sin({T}*30)*6', f'math.sin({T}*45)*2')},
        'arm_r': {'rotation': R(f'-30 + math.sin({T}*90)*3', 0, f'-4 + math.sin({T}*55)*2')},
        'arm_l': {'rotation': R(f'-14 + math.sin({T}*90 + 70)*3', 0, f'6 + math.sin({T}*55)*2')},
        'sword': {'rotation': R(f'math.sin({T}*60)*3', 0, f'math.sin({T}*45)*2')},
        'veil_l': sway('veil_l', 31, 9, 6),
        'orbit': {'rotation': R(0, f'{T}*80', 0)},
    }
    for i in range(6):
        idle[f'coat{i}'] = sway(f'coat{i}', i * 57 + 5, 5)
    out[A + 'idle'] = anim(idle)
    w = {
        'body': {'rotation': R(f'4*{SPD}', f'math.cos({PH})*4*{SPD}'), 'position': R(0, f'math.abs(math.cos({PH}))*0.8*{SPD}', 0)},
        'leg_l': {'rotation': R(f'math.cos({PH})*40*{SPD}')}, 'leg_r': {'rotation': R(f'math.cos({PH} + 180)*40*{SPD}')},
        'shin_l': {'rotation': R(f'math.max(0, math.sin({PH} + 180))*30*{SPD}')}, 'shin_r': {'rotation': R(f'math.max(0, math.sin({PH}))*30*{SPD}')},
        'arm_l': {'rotation': R(f'math.cos({PH} + 180)*10*{SPD}')},
    }
    for i in range(6):
        w[f'coat{i}'] = {'rotation': R(f'-14*{SPD}', 0, f'math.sin({PH}*2 + {i * 40})*5*{SPD}')}
    out[A + 'walk'] = anim(w)
    out[A + 'look'] = look('head', None, 60, 30)
    out[A + 'attack'] = anim({
        'arm_r': {'rotation': R(f'-110 + math.sin(q.life_time*1500)*95', 0, 6)},
        'body': {'rotation': R(f'math.sin(q.life_time*1500)*9', f'math.sin(q.life_time*1500)*-22')},
        'sword': {'rotation': R(f'math.sin(q.life_time*1500)*14')},
    })
    out[A + 'cast'] = anim({
        'arm_r': {'rotation': R(-165, 0, -12)}, 'arm_l': {'rotation': R(-120, 0, 24)},
        'head': {'rotation': R(-20)}, 'body': {'rotation': R(-8)},
        'orbit': {'rotation': R(0, f'{T}*300', 0)},
    })
    return out


def forged_blade(name='forged_blade'):
    A = f'animation.ecr_{name}.'
    out = {}
    out[A + 'idle'] = anim({'body': {'position': R(0, f'math.sin({T}*220)*1.2', 0), 'rotation': R(180, f'{T}*150', f'math.sin({T}*90)*8')}})
    out[A + 'charge'] = anim({'body': {'rotation': R(90, f'{T}*900', 0)}})
    return out
