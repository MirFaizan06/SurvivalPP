"""Animation sets for the Chapter III / IV creatures: the Frost Cantor, Morwen (Mire Lantern) and the Mire Wisp."""
from anims2 import *


def sway(b, ph, amp=6, slow=0):
    return {'rotation': R(f'math.sin({T}*{70 + ph % 40 - slow} + {ph})*{amp}', 0, f'math.sin({T}*{55 + ph % 30 - slow} + {ph * 2})*{amp * 0.6}')}


def cantor(name='frost_cantor'):
    """conducting: the baton arm keeps a slow 3/4 beat, the gown and hair drift, the organ pipes breathe and the snow-crystals orbit"""
    A = f'animation.ecr_{name}.'
    out = {}
    idle = {
        'float': {'position': R(0, f'1.8 + math.sin({T}*75)*1.3', 0)},
        'body': {'rotation': R(f'math.sin({T}*55)*1.6', f'math.sin({T}*30)*3', f'math.sin({T}*45)*1.5')},
        'head': {'rotation': R(f'-6 + math.sin({T}*65)*2', f'math.sin({T}*28)*6', f'math.sin({T}*40)*2')},
        'arm_r': {'rotation': R(f'-62 + math.sin({T}*210)*22', 0, f'-14 + math.sin({T}*105)*8')},
        'baton': {'rotation': R(f'math.sin({T}*210 + 40)*14', 0, f'math.sin({T}*105)*6')},
        'arm_l': {'rotation': R(f'-30 + math.sin({T}*105 + 90)*10', 0, f'16 + math.sin({T}*70)*5')},
        'orbit': {'rotation': R(0, f'{T}*45', 0)},
        'pipes': {'rotation': R(0, f'math.sin({T}*20)*3', 0)},
        'train': {'rotation': R(f'math.sin({T}*60)*3')},
    }
    for i in range(12):
        idle[f'hem{i}'] = sway(f'hem{i}', i * 30, 6)
    for i in range(5):
        idle[f'hair{i}'] = sway(f'hair{i}', i * 50 + 11, 5)
    for tag in 'lr':
        idle[f'sleeve_{tag}'] = sway(f'sleeve_{tag}', 90 if tag == 'l' else 140, 7)
    out[A + 'idle'] = anim(idle)
    w = {'body': {'rotation': R(f'7*{SPD}', 0, 0)}, 'float': {'position': R(0, f'math.abs(math.sin({PH}*0.5))*0.8*{SPD}', 0)}, 'head': {'rotation': R(f'-4*{SPD}')}}
    for i in range(12):
        w[f'hem{i}'] = {'rotation': R(f'-16*{SPD}', 0, f'math.sin({PH}*0.5 + {i * 30})*4*{SPD}')}
    for i in range(5):
        w[f'hair{i}'] = {'rotation': R(f'-14*{SPD}')}
    out[A + 'walk'] = anim(w)
    out[A + 'look'] = look('head', None, 55, 28)
    out[A + 'attack'] = anim({
        'arm_r': {'rotation': R(f'-110 + math.sin(q.life_time*1400)*70', 0, -10)},
        'baton': {'rotation': R(f'math.sin(q.life_time*1400)*30')},
        'body': {'rotation': R(f'math.sin(q.life_time*1400)*8', f'math.sin(q.life_time*1400)*-16')},
    })
    out[A + 'cast'] = anim({
        'arm_r': {'rotation': R(-150, 0, -24)}, 'arm_l': {'rotation': R(-150, 0, 24)},
        'baton': {'rotation': R(f'math.sin({T}*600)*12', 0, f'math.sin({T}*400)*10')},
        'orbit': {'rotation': R(0, f'{T}*260', 0)},
        'pipes': {'rotation': R(0, f'math.sin({T}*300)*5', 0), 'scale': R(1, f'1.06 + math.sin({T}*600)*0.05', 1)},
        'head': {'rotation': R(-22)}, 'body': {'rotation': R(-7)},
        'float': {'position': R(0, f'6 + math.sin({T}*220)*1.5', 0)},
    })
    return out


def morwen(name='mire_lantern'):
    """a hunched hag leaning on her great lantern pole: the lantern sways like a pendulum, vines and hem strips drift, wisps circle"""
    A = f'animation.ecr_{name}.'
    out = {}
    idle = {
        'float': {'position': R(0, f'1.4 + math.sin({T}*70)*1.0', 0)},
        'body': {'rotation': R(f'6 + math.sin({T}*50)*1.4', f'math.sin({T}*28)*3', f'math.sin({T}*42)*1.8')},
        'head': {'rotation': R(f'14 + math.sin({T}*60)*3', f'math.sin({T}*26)*8', f'math.sin({T}*38)*3')},
        'arm_r': {'rotation': R(f'-8 + math.sin({T}*70)*3', 0, f'math.sin({T}*55)*2')},
        'arm_l': {'rotation': R(f'-26 + math.sin({T}*90 + 60)*6', 0, f'8 + math.sin({T}*60)*3')},
        'lantern': {'rotation': R(f'math.sin({T}*95)*9', 0, f'math.sin({T}*72 + 40)*14')},
        'lamp_l': {'rotation': R(f'math.sin({T}*130)*10', 0, f'math.sin({T}*100)*12')},
        'orbit': {'rotation': R(0, f'-{T}*38', 0)},
    }
    for i in range(10):
        idle[f'hem{i}'] = sway(f'hem{i}', i * 36, 6, 8)
    for i in range(6):
        idle[f'vine{i}'] = sway(f'vine{i}', i * 55 + 20, 8, 12)
    out[A + 'idle'] = anim(idle)
    w = {'body': {'rotation': R(f'(10 + 4*math.sin({PH}))*{SPD}', 0, f'math.cos({PH})*3*{SPD}')}, 'float': {'position': R(0, f'math.abs(math.sin({PH}*0.5))*0.7*{SPD}', 0)},
         'lantern': {'rotation': R(f'-14*{SPD}', 0, f'math.cos({PH})*10*{SPD}')}}
    for i in range(10):
        w[f'hem{i}'] = {'rotation': R(f'-14*{SPD}', 0, f'math.sin({PH}*0.5 + {i * 36})*4*{SPD}')}
    for i in range(6):
        w[f'vine{i}'] = {'rotation': R(f'-12*{SPD}')}
    out[A + 'walk'] = anim(w)
    out[A + 'look'] = look('head', None, 55, 28)
    out[A + 'attack'] = anim({
        'arm_r': {'rotation': R(f'-90 + math.sin(q.life_time*1300)*60', 0, 10)},
        'lantern': {'rotation': R(f'math.sin(q.life_time*1300)*40')},
        'body': {'rotation': R(f'math.sin(q.life_time*1300)*10', f'math.sin(q.life_time*1300)*-12')},
    })
    out[A + 'cast'] = anim({
        'arm_r': {'rotation': R(-125, 0, -10)}, 'arm_l': {'rotation': R(-140, 0, 18)},
        'lantern': {'rotation': R(f'math.sin({T}*500)*8', 0, f'math.sin({T}*420)*12'), 'scale': R(f'1 + math.sin({T}*900)*0.12', f'1 + math.sin({T}*900)*0.12', f'1 + math.sin({T}*900)*0.12')},
        'orbit': {'rotation': R(0, f'-{T}*220', 0)},
        'head': {'rotation': R(-16)}, 'body': {'rotation': R(-2)},
        'float': {'position': R(0, f'5 + math.sin({T}*200)*1.5', 0)},
    })
    return out


def wisp(name='mire_wisp'):
    A = f'animation.ecr_{name}.'
    out = {}
    out[A + 'idle'] = anim({
        'body': {'position': R(0, f'math.sin({T}*200)*1.0', 0), 'rotation': R(f'math.sin({T}*90)*6', f'{T}*120', f'math.sin({T}*70)*6')},
        'tail0': {'rotation': R(f'math.sin({T}*220)*14', f'math.sin({T}*140)*10')},
        'tail1': {'rotation': R(f'math.sin({T}*220 + 60)*16', f'math.sin({T}*140 + 60)*12')},
        'tail2': {'rotation': R(f'math.sin({T}*220 + 120)*18', f'math.sin({T}*140 + 120)*14')},
    })
    out[A + 'charge'] = anim({
        'body': {'rotation': R(34, f'{T}*700'), 'scale': R(f'1 + math.sin({T}*1800)*0.12')},
        'tail0': {'rotation': R(-30)}, 'tail1': {'rotation': R(-26)}, 'tail2': {'rotation': R(-22)},
    })
    return out
