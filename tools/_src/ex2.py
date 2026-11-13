import re,sys,html,glob,json,urllib.parse
out={}
for f in glob.glob('*.html'):
    if f=='s.html':continue
    t=open(f,encoding='utf8').read()
    b=re.search(r'<body.*',t,re.S).group(0)
    b=re.sub(r'<script.*?</script>|<style.*?</style>','',b,flags=re.S)
    s=re.sub(r'<(br|/p|/h\d|/div|/li|/span)[^>]*>','\n',b)
    s=html.unescape(re.sub('<.*?>','',s))
    lines=[l.strip().strip('​').strip() for l in s.split('\n')]
    lines=[l for l in lines if l]
    open('txt_'+f[:-5]+'.txt','w',encoding='utf8').write("\n".join(lines))
    imgs=[]
    bi=[]
    for m in re.findall(r'wixstatic\.com/media/([^/"\s\\]+)',b):
        if m not in bi: bi.append(m)
    out[f]=bi
json.dump(out,open('imgs.json','w'),indent=1)
for k,v in out.items(): print(k,len(v),v[:30])
