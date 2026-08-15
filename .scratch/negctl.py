# Negative control: feed the falsifier a FIXED topo_order and a mangled one.
import re, sys, runpy, io, contextlib
import falsify_C0004 as F

FIXED = '''
def topo_order(nodes, edges):
    indeg = {n: 0 for n in nodes}
    succ = {n: [] for n in nodes}
    for a, b in edges:
        succ[a].append(b)
        indeg[b] += 1
    queue = deque(n for n in nodes if indeg[n] == 0)
    order = []
    while queue:
        n = queue.popleft()
        order.append(n)
        for s in succ[n]:
            indeg[s] -= 1
            if indeg[s] == 0:
                queue.append(s)
    if len(order) != len(indeg):
        raise ValueError("cycle in stage graph")
    return order
'''

def run_with(src, label):
    F.load_listing_e = lambda p: (_exec(src), src)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = F.main()
        print(f"[{label}] exit={rc}")
    except AssertionError as e:
        print(f"[{label}] FALSIFIED fired")
    except SystemExit as e:
        print(f"[{label}] SystemExit: {e}")
    for line in buf.getvalue().splitlines():
        print("    " + line)

def _exec(src):
    from collections import deque
    ns = {"deque": deque}
    exec(src, ns)
    return ns["topo_order"]

run_with(FIXED, "FIXED (fails closed)")
