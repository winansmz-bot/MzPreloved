import numpy as np
from PIL import Image
import sys
U='/root/.claude/uploads/3fb0b22c-2fca-56f3-9b69-2e6021efc4dc/'
def load(f): return np.array(Image.open(U+f).convert('RGB')).astype(float)
def gold_sample(a, cloth):
    # bright, saturated warm pixels in detail panel D
    d=a[660:805,870:1110].reshape(-1,3)
    lum=d.mean(1); r,g,b=d.T
    m=(r>g)&(g>b+25)&(lum>np.percentile(lum,90))
    return np.median(d[m],0)
def remap(a, C, G, C2, S, maxres=45, cuff_boxes=()):
    v=G-C; L=(v@v)
    P=a.reshape(-1,3)
    t=((P-C)@v)/L
    proj=C+np.outer(t,v)
    res=P-proj
    dist=np.linalg.norm(res,axis=1)
    m=(dist<maxres)&(t>-0.6)&(t<1.6)
    t2=t.copy()
    out=C2+np.outer(t2,S-C2)+res
    o=P.copy(); o[m]=out[m]
    o=o.reshape(a.shape)
    return np.clip(o,0,255), m.reshape(a.shape[:2]), t.reshape(a.shape[:2]), res.reshape(a.shape)
if __name__=='__main__':
    red=load('1ce0c760-image.jpg'); navy=load('746d8e6c-image.jpg')
    Cr=np.median(red[330:400,80:120].reshape(-1,3),0); Gr=gold_sample(red,Cr)
    Cn=np.median(navy[330:400,80:120].reshape(-1,3),0); Gn=gold_sample(navy,Cn)
    print('red cloth',Cr,'gold',Gr,'navy cloth',Cn,'gold',Gn)
    maroon=np.array([88,30,44.]); silver=np.array([226,224,230.])
    o,m,_,_=remap(red,Cr,Gr,maroon,silver)
    Image.fromarray(o.astype('uint8')).save('sheet-maroon.png')
    black=np.array([24,23,26.])
    o2,_,_,_=remap(navy,Cn,Gn,black,Gn)
    Image.fromarray(o2.astype('uint8')).save('sheet-black.png')
