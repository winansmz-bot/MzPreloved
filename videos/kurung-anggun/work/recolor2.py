import numpy as np
from PIL import Image, ImageFilter
from recolor import load, gold_sample
def fix(a, C, G, C2, S, brooch=(), cuffs=(), dil=7, skin=()):
    v=G-C; L=v@v
    H,W=a.shape[:2]; P=a.reshape(-1,3)
    t=((P-C)@v)/L; res=P-(C+np.outer(t,v)); dist=np.linalg.norm(res,axis=1)
    t=t.reshape(H,W); dist=dist.reshape(H,W); res=res.reshape(H,W,3)
    cloth=((dist<30)&(t<0.35)&(t>-0.6)).astype('uint8')*255
    near=np.array(Image.fromarray(cloth).filter(ImageFilter.MaxFilter(dil)))>0
    m=near&(dist<45)&(t>-0.6)&(t<1.3)
    for (x0,y0,x1,y1) in brooch:
        sub=np.zeros_like(m); sub[y0:y1,x0:x1]=True
        m|=sub&(dist<60)&(t>-0.6)&(t<1.6)
    for (x0,y0,x1,y1) in skin:
        m[y0:y1,x0:x1]&=(t[y0:y1,x0:x1]<0.4)
    tt=t.copy()
    for (x0,y0,x1,y1) in cuffs:
        sub=np.zeros_like(m); sub[y0:y1,x0:x1]=True
        w=np.array(Image.fromarray((sub*255).astype('uint8')).filter(ImageFilter.GaussianBlur(3)))/255.0
        w=w*m
        tt=tt*(1-w)+np.clip(tt,-0.6,0.15)*w
    out=C2+tt[...,None]*(S-C2)+res
    o=a.copy(); o[m]=out[m]
    return np.clip(o,0,255).astype('uint8')
red=load('1ce0c760-image.jpg'); navy=load('746d8e6c-image.jpg')
Cr=np.median(red[330:400,80:120].reshape(-1,3),0); Gr=gold_sample(red,Cr)
Cn=np.median(navy[330:400,80:120].reshape(-1,3),0); Gn=gold_sample(navy,Cn)
brooch=[(145,255,185,290),(435,255,475,290),(870,145,970,250)]
cuffs=[(40,440,82,470),(243,440,287,470),(403,365,442,408),(484,368,514,398),(686,438,724,470)]
skin=[(118,140,205,262),(390,140,478,262),(680,140,760,262),(30,468,95,535),(236,468,300,535),(418,378,520,432),(690,468,745,535),(120,775,205,800),(395,770,470,800),(660,770,740,800),(862,395,960,560),(985,470,1080,625),(985,420,1010,460)]
maroon=np.array([88,30,44.]); silver=np.array([226,224,230.])
Image.fromarray(fix(red,Cr,Gr,maroon,silver,brooch,cuffs,skin=skin)).save('sheet-maroon.png')
Image.fromarray(navy.astype('uint8')).save('sheet-navy.png')
b=fix(navy,Cn,Gn,np.array([22,22,22.]),Gn,(),(),skin=skin).astype(float)
lum=b.mean(2,keepdims=True); blue=(b[...,2]-b[...,0])
sel=(lum[...,0]<90)&(blue>8)
b[sel]=(lum*np.array([1.0,1.0,1.02]))[sel]
Image.fromarray(np.clip(b,0,255).astype('uint8')).save('sheet-black.png')
