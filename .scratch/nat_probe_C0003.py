import glob,os,re,sys,threading,time
T=sorted(glob.glob(os.path.expanduser("~/CDSFL_review_targets/current/*.md")))[0]
doc=open(T,encoding="utf-8").read()
src=re.search(r"Listing A\b.*?```python\n(.*?)```",doc,re.S).group(1)
ns={"time":time};exec(compile(src,T+"::ListingA","exec"),ns);TB=ns["TokenBucket"]
sys.setswitchinterval(1e-9)
CAP=8; N=64
for trial in range(400):
    b=TB(CAP,0.0); pre=b.tokens; res=[]
    lk=threading.Lock(); go=threading.Barrier(N)
    def w():
        go.wait()
        r=b.allow(1.0)
        with lk: res.append(r)
    ts=[threading.Thread(target=w) for _ in range(N)]
    for t in ts:t.start()
    for t in ts:t.join(5)
    adm=res.count(True)
    if adm>CAP or b.tokens<0:
        print("NATURAL RACE trial=%d pre=%r admitted=%d cap=%r post=%r"%(trial,pre,adm,CAP,b.tokens));break
else:
    print("no natural over-admission in 400 trials")
