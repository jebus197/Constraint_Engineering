#!/usr/bin/env python3
"""Falsifier for review finding C0003 against Listing A of SW-21-REF-04:

    "TokenBucket.allow mutates shared state (self.tokens, self.last) without a lock."

Loads the REAL Listing A from the staged review document by absolute path (never a
re-typed copy), execs it, and drives the real allow() path from two threads.

Prints FALSIFIED and raises AssertionError iff the race is genuinely reachable.
Exits 0 if the listing is guarded.
"""
import ast, glob, os, re, sys, threading, time

# ---------------------------------------------------------------- real source
override = os.environ.get("ZC_TARGET")
cands = [override] if override else sorted(
    glob.glob(os.path.expanduser("~/CDSFL_review_targets/current/*.md")))
if not cands or not cands[0] or not os.path.exists(cands[0]):
    sys.exit("ABORT: staged review target not found; cannot test the real code")
TARGET = os.path.abspath(cands[0])
src_doc = open(TARGET, encoding="utf-8").read()

m = re.search(r"Listing A\b.*?```python\n(.*?)```", src_doc, re.S)
if not m:
    sys.exit("ABORT: could not locate Listing A code block in %s" % TARGET)
listing_a = m.group(1)
if "class TokenBucket" not in listing_a or "def allow" not in listing_a:
    sys.exit("ABORT: extracted block is not TokenBucket")

ns = {"time": time, "threading": threading}
exec(compile(listing_a, TARGET + "::ListingA", "exec"), ns)     # the REAL code
TokenBucket = ns["TokenBucket"]

print("target    :", TARGET)
print("listing A : %d lines, head %r"
      % (len(listing_a.strip().splitlines()), listing_a.strip().splitlines()[0]))

# ------------------------------------------- structural precondition (AST, real source)
tree = ast.parse(listing_a)
has_with = any(isinstance(n, ast.With) for n in ast.walk(tree))
names = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
lockish = {a for a in names if "lock" in a.lower() or "mutex" in a.lower()}
print("AST       : With-stmts=%r  lock-ish attrs=%r" % (has_with, sorted(lockish)))
# Reported as evidence, NOT used as a gate: a lock that fails to cover allow would
# still satisfy this scan. The verdict comes from running the code.

# ------------------------------------------------------------- instrumentation
# A yield point placed on the READ of self.tokens made by `if self.tokens >= cost`.
# It changes no arithmetic and no control flow; it only forces the interleaving that
# ZC-26 names. A correctly locked implementation must survive it unharmed -- that is
# the negative control below, and it is what stops this test being a tautology.
_tl = threading.local()
GATE = threading.Barrier(2)
GATE_TIMEOUT = 1.0
gate_trips = []


def _switch_point():
    try:
        GATE.wait(timeout=GATE_TIMEOUT)
        gate_trips.append(True)
    except threading.BrokenBarrierError:
        gate_trips.append(False)      # serialized: the interleaving never happened


class Instrumented(TokenBucket):
    """Real allow(); only the read of self.tokens is observable."""

    def __init__(self, capacity, rate):
        self._tokens = 0.0
        super().__init__(capacity, rate)

    @property
    def tokens(self):
        n = getattr(_tl, "n", 0) + 1
        _tl.n = n
        v = self._tokens              # the LOAD itself
        if n == 2:                    # read #1 = refill expr, read #2 = the `>=` test
            _switch_point()           # preempt AFTER the load, BEFORE the compare
        return v

    @tokens.setter
    def tokens(self, v):
        self._tokens = v

    def allow(self, cost=1.0):
        _tl.n = 0
        return TokenBucket.allow(self, cost)   # <-- the REAL buggy path


class Locked(Instrumented):
    """Negative control: the fix C0003 asks for, under identical instrumentation."""

    def __init__(self, capacity, rate):
        self._lk = threading.RLock()
        super().__init__(capacity, rate)

    def allow(self, cost=1.0):
        with self._lk:
            return Instrumented.allow(self, cost)


CAP, RATE, COST = 1.0, 0.0, 1.0        # rate 0 => refill can contribute nothing


def race(cls):
    global GATE
    GATE = threading.Barrier(2)
    gate_trips.clear()
    b = cls(CAP, RATE)
    pre = b._tokens                                   # SNAPSHOT before mutation
    assert pre == CAP, "setup failed: bucket did not start full"
    out = {}
    def run(i):
        out[i] = b.allow(COST)
    ts = [threading.Thread(target=run, args=(i,)) for i in (0, 1)]
    for t in ts: t.start()
    for t in ts: t.join(5.0)
    assert not any(t.is_alive() for t in ts), "ABORT: threads hung; test inconclusive"
    return pre, [out.get(0), out.get(1)], b._tokens, any(gate_trips)


# -------------------------------------------------- sanity: uninstrumented, sequential
raw = TokenBucket(CAP, RATE)
seq = [raw.allow(COST), raw.allow(COST)]
print("\n-- sanity: raw listing, one thread --")
print("capacity %.1f rate %.1f -> allow,allow = %r  tokens=%r" % (CAP, RATE, seq, raw.tokens))
if seq != [True, False]:
    sys.exit("ABORT: limiter is not even correct single-threaded; C0003 is not what is being tested")

pre, res, post, tripped = race(Instrumented)
print("\n-- real listing, two concurrent callers --")
print("pre tokens         : %r" % (pre,))
print("interleaving forced: %r" % (tripped,))
print("allow() returns    : %r" % (res,))
print("post tokens        : %r" % (post,))

c_pre, c_res, c_post, c_tripped = race(Locked)
print("\n-- negative control (locked subclass, same instrumentation) --")
print("interleaving forced: %r  (False = the lock serialized the callers)" % (c_tripped,))
print("allow() returns    : %r   post tokens: %r" % (c_res, c_post))
if c_res.count(True) > 1 or c_post < 0:
    sys.exit("ABORT: falsifier fires on locked code -- test is a tautology")

admitted = res.count(True)
if admitted > 1 or post < 0:
    print("\nFALSIFIED: Listing A TokenBucket.allow races on self.tokens.")
    print("  over-admission: %d requests of cost %.1f admitted from a %.1f-token bucket"
          % (admitted, COST, CAP))
    print("  invariant     : tokens %.1f -> %.1f, violating 0 <= tokens <= capacity"
          % (pre, post))
    print("  control       : the identical run under a lock admitted %d and left %r"
          % (c_res.count(True), c_post))
    raise AssertionError(
        "TokenBucket.allow has no mutual exclusion: two callers interleaved between "
        "the `tokens >= cost` test and the `tokens -= cost` subtraction both returned "
        "True against a %.1f-token bucket and left tokens at %.1f (< 0)" % (CAP, post))

print("\nNOT FALSIFIED: two concurrent callers could not over-admit or drive tokens "
      "negative; allow() is effectively serialized.")
sys.exit(0)
