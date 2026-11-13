import os,sys
from PIL import Image,ImageDraw
fs=sorted(os.listdir('raw'))
fs=[f for f in fs if not f.endswith(('.avif',))]
n=int(sys.argv[1]);per=24
chunk=fs[n*per:(n+1)*per]
W=200;cols=6
rows=(len(chunk)+cols-1)//cols
sh=Image.new('RGB',(cols*W,rows*(W+16)),'#888')
d=ImageDraw.Draw(sh)
for i,f in enumerate(chunk):
    try:
        im=Image.open('raw/'+f).convert('RGBA');bg=Image.new('RGBA',im.size,(200,200,200,255));bg.alpha_composite(im);im=bg.convert('RGB');im.thumbnail((W-4,W-4))
        sh.paste(im,((i%cols)*W+2,(i//cols)*(W+16)))
    except Exception as e: pass
    d.text(((i%cols)*W+2,(i//cols)*(W+16)+W),f[7:15]+' '+str(i+n*per),fill='white')
sh.save(f'sheet{n}.png')
print(len(fs),[ (i+n*per,f[7:15]) for i,f in enumerate(chunk)])
