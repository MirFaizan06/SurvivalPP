import sys
from PIL import Image, ImageDraw
def sheet(paths, out, scale=8, cols=6, bg=(64,64,64,255)):
    ims=[]
    for p in paths:
        im=Image.open(p).convert('RGBA')
        ims.append((p,im))
    cw=max(i.width for _,i in ims)*scale+8
    ch=max(i.height for _,i in ims)*scale+8
    rows=(len(ims)+cols-1)//cols
    S=Image.new('RGBA',(cw*cols,ch*rows),bg)
    for k,(p,im) in enumerate(ims):
        r,c=divmod(k,cols)
        big=im.resize((im.width*scale,im.height*scale),Image.NEAREST)
        S.alpha_composite(big,(c*cw+4,r*ch+4))
    S.convert('RGB').save(out)
if __name__=='__main__':
    out=sys.argv[1]; scale=int(sys.argv[2]); cols=int(sys.argv[3]); sheet(sys.argv[4:],out,scale,cols)
