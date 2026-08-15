import re, sys, os, threading, time
sys.setswitchinterval(1e-6)
p=os.path.expanduser("~/CDSFL_review_targets/current/SW-21-REF-04.md")
src=open(p,encoding="utf-8").read()
code=re.search(r"Listing A\b.*?```python\n(.*?)```", src, re.S).group(1)
ns={"time":time}; exec(code, ns); TB=ns["TokenBucket"]
N=24
worst=0; trial_hit=None
for trial in range(400):
    b=TB(1.0,0.0)
    start=threading.Barrier(N)
    res=[]
    lk=threading.Lock()
    def run():
        start.wait()
        r=b.allow(1.0)
        with lk: res.append(r)
    ts=[threading.Thread(target=run) for _ in range(N)]
    for t in ts:t.start()
    for t in ts:t.join()
    a=res.count(True)
    worst=max(worst,a)
    if a>1:
        trial_hit=(trial,a,b.tokens); break
print("worst admitted:",worst,"hit:",trial_hit)
