from PIL import Image, ImageDraw, ImageFilter
import numpy as np
IMG='/tmp/claude-0/-home-claude/09a16d60-b7d3-584b-8a37-da9665017baa/scratchpad/build3/site/img/'
SETS={'cover-sushi':('#F0643C',['s2g-invitation','s2g-pourquoi','s2g-plateau']),
      'cover-hem8':('#F28A1E',['h8-menu-red','h8-music','h8-seagames']),
      'cover-koem':('#D23A4A',['ko-fruit-2','ko-pinkday','ko-fruit-1']),
      'cover-duckee':('#E0559A',['dk-ba-0','dk-menu-fr','dk-ba-7'])}
W,H=1600,1100
def hexrgb(h): return tuple(int(h[i:i+2],16) for i in (1,3,5))
def rounded(im,r):
    m=Image.new('L',im.size,0);ImageDraw.Draw(m).rounded_rectangle((0,0,im.width-1,im.height-1),r,fill=255);o=im.convert('RGBA');o.putalpha(m);return o
for name,(tint,(l,c,r)) in SETS.items():
    t=np.array(hexrgb(tint),float);base=np.array([13,12,10],float)
    yy,xx=np.mgrid[0:H,0:W];d=np.sqrt(((xx-W*.5)/W)**2+((yy-H*.45)/H)**2)
    k=np.clip(1-d*1.6,0,1)[...,None]
    bg=(base*(1-.55*k)+t*.55*k*0.75+base*0.0)
    bg=np.clip(base+(t-base)*(0.22+0.38*k),0,255).astype('uint8')
    canvas=Image.fromarray(bg,'RGB').convert('RGBA')
    ims=[Image.open(IMG+n+'.webp').convert('RGB') for n in (l,c,r)]
    ch=860; cim=ims[1].resize((round(ims[1].width*ch/ims[1].height),ch),Image.LANCZOS)
    sh=640
    side=[im.resize((round(im.width*sh/im.height),sh),Image.LANCZOS) for im in (ims[0],ims[2])]
    ov=90; total=side[0].width+cim.width+side[1].width-2*ov
    if total>W-80:
        s=(W-80+2*ov-cim.width)/(side[0].width+side[1].width)
        side=[im.resize((round(im.width*s),round(im.height*s)),Image.LANCZOS) for im in side]
        total=side[0].width+cim.width+side[1].width-2*ov
    x0=(W-total)//2; cy=H//2
    pos=[(x0,cy-side[0].height//2),(x0+side[0].width-ov,cy-ch//2),(x0+side[0].width-ov+cim.width-ov,cy-side[1].height//2)]
    order=[(side[0],pos[0]),(side[1],pos[2]),(cim,pos[1])]
    for im,(x,y) in order:
        rim=rounded(im,22)
        shadow=Image.new('RGBA',canvas.size,(0,0,0,0));sd=Image.new('RGBA',rim.size,(0,0,0,150));sd.putalpha(rim.split()[3].point(lambda v:v*0.6))
        shadow.paste(sd,(x+10,y+26),sd);shadow=shadow.filter(ImageFilter.GaussianBlur(26))
        canvas=Image.alpha_composite(canvas,shadow);canvas.paste(rim,(x,y),rim)
    canvas.convert('RGB').save(IMG+name+'.webp','WEBP',quality=82)
    print(name)
