from common import *
import json,os,sys,re,glob
BASE=(SCHEMA_DIR + '/json_schemas/server/entity')
def vkey(v):
    return tuple(int(x) if x.isdigit() else 0 for x in re.split(r'[.]',v))
def find(name):
    fn='minecraft_'+name.replace('minecraft:','')+'.json'
    cands=[]
    for d in os.listdir(BASE):
        p=os.path.join(BASE,d,fn)
        if os.path.exists(p): cands.append((vkey(d) if d!='beta' else (9999,),d,p))
    cands.sort()
    return cands[-1] if cands else None
def short(o):
    if isinstance(o,dict):
        r={}
        for k,v in o.items():
            if k.startswith('x-') or k in ('$schema','$id','title','description') : 
                continue
            r[k]=short(v)
        return r
    if isinstance(o,list): return [short(x) for x in o]
    return o
def show(name):
    f=find(name)
    if not f: print('NO SCHEMA',name); return
    d=json.load(open(f[2],encoding='utf-8'))
    props=d.get('properties') or {}
    if not props and 'oneOf' in d:
        for alt in d['oneOf']:
            if 'properties' in alt: props=alt['properties']; break
    print(f'## {name} (v{f[1]}) type={d.get("type")}')
    for k,v in props.items():
        t=v.get('type') or ('ref:'+os.path.basename(v['$ref'])) if isinstance(v,dict) else ''
        extra=''
        if isinstance(v,dict):
            if 'default' in v: extra+=f' default={json.dumps(v["default"])[:40]}'
            if 'enum' in v: extra+=f' enum={v["enum"]}'
        print('  ',k,t,extra)
if __name__=='__main__':
    for n in sys.argv[1:]: show(n)
