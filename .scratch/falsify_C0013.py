#!/usr/bin/env python3
"""Falsifier for review finding C0013 against SW-21-REF-04, Listing A:

    "TokenBucket.allow mutates shared admission state without synchronization."

The target is a REVIEW ARTICLE, not a service. A finding is a genuine defect of the
article only if the hazard is BOTH (i) really reachable in the printed listing AND
(ii) not already correctly disclosed and scoped by the article's own statements.
An article that states the hazard itself has no defect to report; re-filing it is a
false positive, however true the sentence is of the code.

So this fires iff  reachable AND NOT (disclosed AND correctly-scoped).
Reachability is RUN, never inferred from a lock scan (see m4_sham_lock).
"""
import ast, glob, os, re, sys, threading, time

# ------------------------------------------------------------------ real source
override = os.environ.get("ZC_TARGET")
cands = [override] if override else sorted(
    glob.glob(os.path.expanduser("~/CDSFL_review_targets/current/*.md")))
if not cands or not cands[0] or not os.path.exists(cands[0]):
    sys.exit("ABORT: staged review target not found; cannot test the real code")
TARGET = os.path.abspath(cands[0])
doc = open(TARGET, encoding="utf-8").read()

m = re.search(r"Listing A\b.*?```python\n(.*?)```", doc, re.S)
if not m:
    sys.exit("ABORT: could not locate Listing A code block in %s" % TARGET)
listing_a = m.group(1)
if "class TokenBucket" not in listing_a or "def allow" not in listing_a:
    sys.exit("ABORT: extracted block is not TokenBucket")

ns = {"time": time, "threading": threading}
exec(compile(listing_a, TARGET + "::ListingA", "exec"), ns)          # the REAL code
TokenBucket = ns["TokenBucket"]

print("target     :", TARGET)
tree = ast.parse(listing_a)
lockish = sorted({n.attr for n in ast.walk(tree)
                  if isinstance(n, ast.Attribute) and "lock" in n.attr.lower()})
print("AST        : With-stmts=%r lock-ish attrs=%r  (evidence only, NOT a gate)"
      % (any(isinstance(n, ast.With) for n in ast.walk(tree)), lockish))

# ============================ PART 1 — is the race really reachable? (RUN it) ===
_tl = threading.local()
GATE = threading.Barrier(2)
trips = []

def _switch_point():
    try:
        GATE.wait(timeout=1.0); trips.append(True)
    except threading.BrokenBarrierError:
        trips.append(False)                 # serialized: interleaving never happened

class Instrumented(TokenBucket):
    """Real allow(); only the LOAD of self.tokens is observable. No arithmetic or
    control flow is altered -- a properly locked allow survives this untouched,
    which is what the negative control below proves."""
    def __init__(self, capacity, rate):
        self._tokens = 0.0
        super().__init__(capacity, rate)
    @property
    def tokens(self):
        n = getattr(_tl, "n", 0) + 1; _tl.n = n
        v = self._tokens                     # the LOAD itself
        if n == 2:                           # read#1 = refill expr, read#2 = the >= test
            _switch_point()                  # preempt AFTER load, BEFORE compare
        return v
    @tokens.setter
    def tokens(self, v):
        self._tokens = v
    def allow(self, cost=1.0):
        _tl.n = 0
        return TokenBucket.allow(self, cost)          # <-- the REAL path

class Locked(Instrumented):
    """Negative control: the fix C0013 asks for, same instrumentation."""
    def __init__(self, capacity, rate):
        self._lk = threading.RLock(); super().__init__(capacity, rate)
    def allow(self, cost=1.0):
        with self._lk:
            return Instrumented.allow(self, cost)

CAP, RATE, COST = 1.0, 0.0, 1.0            # rate 0 => refill can contribute nothing

def race(cls):
    global GATE
    GATE = threading.Barrier(2); trips.clear()
    b = cls(CAP, RATE)
    pre = b._tokens                                    # SNAPSHOT before mutation
    assert pre == CAP, "setup failed: bucket did not start full"
    out = {}
    ts = [threading.Thread(target=lambda i=i: out.__setitem__(i, b.allow(COST)))
          for i in (0, 1)]
    for t in ts: t.start()
    for t in ts: t.join(5.0)
    assert not any(t.is_alive() for t in ts), "ABORT: threads hung; inconclusive"
    return pre, [out.get(0), out.get(1)], b._tokens, any(trips)

raw = TokenBucket(CAP, RATE)
seq = [raw.allow(COST), raw.allow(COST)]
print("\n-- sanity, single thread --  allow,allow = %r  tokens=%r" % (seq, raw.tokens))
if seq != [True, False]:
    sys.exit("ABORT: limiter is wrong even single-threaded; that is not what C0013 claims")

pre, res, post, tripped = race(Instrumented)
c_pre, c_res, c_post, c_tripped = race(Locked)
print("-- two concurrent callers, real listing --")
print("   pre=%r  interleaving forced=%r  returns=%r  post=%r" % (pre, tripped, res, post))
print("-- negative control (locked), same instrumentation --")
print("   interleaving forced=%r  returns=%r  post=%r" % (c_tripped, c_res, c_post))
if c_res.count(True) > 1 or c_post < 0:
    sys.exit("ABORT: falsifier fires on locked code -- it is a tautology")

reachable = res.count(True) > 1 or post < 0
print("\nPART 1 reachable  : %r  (%d of 2 unit-cost requests admitted from a %.1f-token "
      "bucket; tokens %.1f -> %.1f)" % (reachable, res.count(True), CAP, pre, post))

# ================== PART 2 — does the article already disclose and scope it? ===
stmts = re.findall(r"\*\*(ZC-\d+)\.\*\*(.*?)(?=\n\*\*ZC-|\n---|\Z)", doc, re.S)
tail  = [("<prose>", p) for p in re.findall(r"\n((?:[^\n*][^\n]*)?ZC-\d+ is quantified[^\n]*)", doc)]
about_a = [(t, b) for t, b in stmts + tail
           if re.search(r"Listing A\b|TokenBucket", b)]

CONC = r"concurrent|concurrency|interleav|thread-safe|two threads|race"
SINGLE = r"single-threaded"

disclosed = [t for t, b in about_a
             if re.search(r"not thread-safe|carries no lock|no lock\b", b, re.I)
             and re.search(CONC, b, re.I)]
# an invariant claim is mis-scoped if it asserts 0<=tokens<=capacity under concurrency
misscoped = [t for t, b in about_a
             if re.search(r"invariant", b, re.I)
             and re.search(r"tokens\s*<=\s*capacity", b)
             and re.search(CONC, b, re.I) and not re.search(SINGLE, b, re.I)]

print("PART 2 statements about Listing A : %r" % ([t for t, _ in about_a],))
print("       hazard disclosed by        : %r" % (disclosed,))
print("       invariant mis-scoped in    : %r" % (misscoped,))

# ============================================================== verdict =========
defect = reachable and (not disclosed or misscoped)
if defect:
    why = ("the article never states it" if not disclosed
           else "the article contradicts itself at %s, which claims the invariant "
                "holds under concurrency" % ",".join(misscoped))
    print("\nFALSIFIED: C0013 is a genuine defect of this article.")
    print("  reachable : %d admits from a %.1f-token bucket, tokens left at %.1f" %
          (res.count(True), CAP, post))
    print("  undisclosed: %s" % why)
    raise AssertionError(
        "TokenBucket.allow has no mutual exclusion -- two callers interleaved between "
        "the `tokens >= cost` test and the `tokens -= cost` subtraction both returned "
        "True against a %.1f-token bucket, leaving tokens at %.1f -- and %s"
        % (CAP, post, why))

if not reachable:
    print("\nNOT FALSIFIED: allow() is effectively serialized; C0013's premise is false "
          "of this listing.")
else:
    print("\nNOT FALSIFIED: the race is real, but the article already discloses it at %s "
          "and scopes its invariant claim to single-threaded use, so C0013 reports "
          "nothing the article got wrong -- it is a false positive."
          % ",".join(disclosed))
sys.exit(0)
