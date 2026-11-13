import re,html,sys
BS=chr(92)
def imgs(f):
    t=open(f,encoding='utf8').read()
    b=re.search(r'<body.*',t,re.S).group(0)
    res=[]
    for m in re.finditer(r'data-image-info="([^"]+)"',b):
        d=html.unescape(m.group(1))
        u=re.search(r'"uri":"([^"]+)"',d)
        w=re.search(r'"width":(\d+),"height":(\d+)',d)
        alt=re.search(r'"alt":"([^"]*)"',d)
        res.append((u.group(1) if u else '?', w.group(0) if w else '', alt.group(1) if alt else ''))
    return res
if __name__=='__main__':
    for r in imgs(sys.argv[1]): print(r)
