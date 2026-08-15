#!/usr/bin/env python3
"""Falsifier for review finding C0003 against SW-21-REF-04:

    "TokenBucket.allow mutates shared state (self.tokens, self.last) without a lock."

C0003 is a DEFECT only if BOTH hold:
  (1) MECHANISM  - the unsynchronised read-test-write in the REAL Listing A is
                   genuinely reachable and really over-admits, and
  (2) DISCLOSURE - the reference does not already state that Listing A carries no
                   lock, OR it elsewhere claims thread-safety, OR it asserts the
                   token invariant without restricting it to single-threaded use.

Reporting a property the document itself asserts, with its scope stated, is a
false positive, not a defect. Both legs are measured against the real file.

FALSIFIED (AssertionError) iff (1) AND (2). Exit 0 otherwise.
"""
import ast, glob, os, re, sys, threading, time

# ------------------------------------------------------------ the REAL source
TARGET = os.path.abspath((os.environ.get("ZC_TARGET") or (sorted(
    glob.glob(os.path.expanduser("~/CDSFL_review_targets/current/*.md"))) or [""])[0]))
if not TARGET or not os.path.exists(TARGET):
    sys.exit("ABORT: review target not found; refusing to test a re-typed copy")
doc = open(TARGET, encoding="utf-8").read()

m = re.search(r"Listing A\b.*?```python\n(.*?)```", doc, re.S)
if not m:
    sys.exit("ABORT: Listing A code block not found in %s" % TARGET)
listing_a = m.group(1)
if "class TokenBucket" not in listing_a or "def allow" not in listing_a:
    sys.exit("ABORT: extracted block is not TokenBucket")
ns = {"time": time, "threading": threading}
exec(compile(listing_a, TARGET + "::ListingA", "exec"), ns)      # the REAL code
TokenBucket = ns["TokenBucket"]
print("target   :", TARGET)
print("listing A: %d lines" % len(listing_a.strip().splitlines()))

# --------------------------------------- structural precondition (AST on real source)
tree = ast.parse(listing_a)
allow = next(n for n in ast.walk(tree)
             if isinstance(n, ast.FunctionDef) and n.name == "allow")
guarded = any(isinstance(n, ast.With) for n in ast.walk(allow))
lockish = sorted({n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)
                  and re.search("lock|mutex|sem", n.attr, re.I)})
stores  = sorted({t.attr for n in ast.walk(allow) for t in
                  ([n.target] if isinstance(n, ast.AugAssign) else
                   getattr(n, "targets", []))
                  if isinstance(t, ast.Attribute)})
print("AST      : allow() with-blocks=%s  lock-ish attrs=%r  self-attrs stored=%r"
      % (guarded, lockish, stores))
# Evidence only, NOT a gate: a lock that exists but fails to cover allow would still
# clear a structural scan. The verdict below comes from running the real code.

# ------------------------------------------------- sanity: correct single-threaded
raw = TokenBucket(1.0, 0.0)
if [raw.allow(1.0), raw.allow(1.0)] != [True, False]:
    sys.exit("ABORT: limiter is wrong single-threaded; that is not what C0003 claims")

# ============================ LEG 1: mechanism, natural scheduling, no instrumentation
CAP, N, TRIALS = 8, 64, 250
sys.setswitchinterval(1e-9)
nat = None
for trial in range(TRIALS):
    b = TokenBucket(CAP, 0.0)
    pre = b.tokens                                  # SNAPSHOT before any mutation
    assert pre == float(CAP), "setup failed: bucket did not start full"
    res, lk, go = [], threading.Lock(), threading.Barrier(N)
    def worker():
        go.wait()
        r = b.allow(1.0)                            # <- the REAL buggy path
        with lk: res.append(r)
    ts = [threading.Thread(target=worker) for _ in range(N)]
    for t in ts: t.start()
    for t in ts: t.join(10)
    if any(t.is_alive() for t in ts):
        sys.exit("ABORT: threads hung; inconclusive")
    if res.count(True) > CAP or b.tokens < 0:
        nat = (trial, pre, res.count(True), b.tokens); break
sys.setswitchinterval(0.005)

# ---------------- LEG 1b: deterministic gate + locked negative control (anti-tautology)
_tl = threading.local(); GATE = threading.Barrier(2); trips = []
def _switch():
    try: GATE.wait(timeout=1.0); trips.append(True)
    except threading.BrokenBarrierError: trips.append(False)

class Probe(TokenBucket):
    """Real allow(); only the LOAD of self.tokens for the `>=` test is observable."""
    def __init__(s, c, r): s._t = 0.0; super().__init__(c, r)
    @property
    def tokens(s):
        n = getattr(_tl, "n", 0) + 1; _tl.n = n; v = s._t
        if n == 2: _switch()                        # after load, before compare
        return v
    @tokens.setter
    def tokens(s, v): s._t = v
    def allow(s, cost=1.0):
        _tl.n = 0; return TokenBucket.allow(s, cost)

class Locked(Probe):                                 # the fix C0003 asks for
    def __init__(s, c, r): s._lk = threading.RLock(); super().__init__(c, r)
    def allow(s, cost=1.0):
        with s._lk: return Probe.allow(s, cost)

def duel(cls):
    global GATE
    GATE = threading.Barrier(2); trips.clear()
    b = cls(1.0, 0.0); pre = b._t                    # SNAPSHOT before mutation
    out = {}
    ts = [threading.Thread(target=lambda i=i: out.__setitem__(i, b.allow(1.0)))
          for i in (0, 1)]
    for t in ts: t.start()
    for t in ts: t.join(5)
    if any(t.is_alive() for t in ts): sys.exit("ABORT: threads hung; inconclusive")
    return pre, [out.get(0), out.get(1)], b._t, any(trips)

g_pre, g_res, g_post, g_trip = duel(Probe)
c_pre, c_res, c_post, c_trip = duel(Locked)
if c_res.count(True) > 1 or c_post < 0:
    sys.exit("ABORT: falsifier fires on LOCKED code -- it is a tautology, not a test")

mechanism = bool(nat) or g_res.count(True) > 1 or g_post < 0
print("\n-- leg 1: mechanism --")
print("natural (no instrumentation): %s"
      % ("over-admitted %d of a %d-token bucket on trial %d, tokens %r -> %r"
         % (nat[2], CAP, nat[0], nat[1], nat[3]) if nat
         else "no over-admission in %d x %d-thread trials" % (TRIALS, N)))
print("forced interleave           : tripped=%r returns=%r tokens %r -> %r"
      % (g_trip, g_res, g_pre, g_post))
print("locked control (same probe) : tripped=%r returns=%r tokens %r -> %r"
      % (c_trip, c_res, c_pre, c_post))
print("mechanism real              : %r" % mechanism)

# =========================== LEG 2: does the reference already state this?
stmts = dict(re.findall(r"\*\*(ZC-\d+)\.\*\*\s*(.*?)(?=\n\n|\Z)", doc, re.S))
about_a = {k: v for k, v in stmts.items()
           if re.search(r"Listing A|TokenBucket|token bucket", v, re.I)}
disclosed = {k for k, v in about_a.items()
             if re.search(r"carries no lock|no lock|not thread[- ]safe|"
                          r"is therefore not thread", v, re.I)}
claims_safe = {k for k, v in about_a.items()
               if re.search(r"(?<!not )(?<!never )thread[- ]safe|"
                            r"safe (?:for|under) (?:any |multiple |concurrent)", v, re.I)
               and k not in disclosed}
inv = {k for k, v in about_a.items()
       if re.search(r"0 <= tokens <= capacity|invariant", v, re.I)}
unscoped_inv = {k for k in inv
                if not re.search(r"single[- ]threaded|one caller|serial",
                                 about_a[k], re.I)}
print("\n-- leg 2: disclosure in the real document --")
print("statements about Listing A  : %s" % sorted(about_a))
print("disclose the missing lock   : %s" % sorted(disclosed))
print("claim thread-safety         : %s" % sorted(claims_safe))
print("invariant stmts unscoped    : %s" % sorted(unscoped_inv))
undisclosed = (not disclosed) or bool(claims_safe) or bool(unscoped_inv)
print("document defective          : %r" % undisclosed)

# ------------------------------------------------------------------- verdict
if mechanism and undisclosed:
    print("\nFALSIFIED: unsynchronised mutation in TokenBucket.allow is reachable AND "
          "the reference does not scope it.")
    raise AssertionError(
        "C0003 confirmed: allow() read-modify-writes self.tokens/self.last with no "
        "mutual exclusion; concurrent callers over-admitted (%s) and the document "
        "discloses=%s claims-safe=%s unscoped-invariants=%s"
        % (nat[2] if nat else g_res, sorted(disclosed), sorted(claims_safe),
           sorted(unscoped_inv)))

print("\nNOT FALSIFIED: C0003 is not a defect of this reference.")
print("  mechanism       : %s" % ("reachable and reproduced" if mechanism else
      "NOT reachable -- concurrent callers could not over-admit; allow() is serialized"))
if not mechanism:
    sys.exit(0)
print("  but disclosed by: %s -- the document asserts the missing lock itself,"
      % sorted(disclosed))
print("  claims no thread-safety anywhere, and scopes its token invariant (%s) to "
      "single-threaded use. Restating a stated, correctly-scoped property is a "
      "false positive." % sorted(inv))
sys.exit(0)
