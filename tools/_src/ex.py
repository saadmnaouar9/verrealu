import re,sys,html,json
t=open(sys.argv[1],encoding='utf8').read()
b=re.search(r'<body.*',t,re.S).group(0)
b=re.sub(r'<script.*?</script>|<style.*?</style>','',b,flags=re.S)
print("TITLE",re.search(r'<title>(.*?)</title>',t,re.S).group(1))
print("DESC",re.findall(r'name="description" content="(.*?)"',t))
print("LINKS");
for h,txt in sorted(set((h,re.sub('<.*?>','',x).strip()[:40]) for h,x in re.findall(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>',b,re.S))):print(" ",h,'|',txt)
print("TEXT")
s=re.sub(r'<(br|/p|/h\d|/div|/li|/span)[^>]*>','\n',b)
s=html.unescape(re.sub('<.*?>','',s))
print("\n".join(l.strip() for l in s.split('\n') if l.strip()))
