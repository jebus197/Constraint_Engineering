#!/usr/bin/env python3
"""Falsifier for the finding against Listing A (TokenBucket.allow):

    "allow accepts negative cost. If cost < 0 then `self.tokens >= cost` is True
     and `self.tokens -= cost` INCREASES the token count, potentially exceeding
     self.capacity."

Loads the REAL Listing A out of the staged review document by absolute path
(never a re-typed copy), execs it, drives the real allow() path, and snapshots
self.tokens BEFORE the in-place mutating call.

FALSIFIED + AssertionError iff the defect is genuinely present; exit 0 otherwise.
"""
import glob, os, re, sys, time

override = os.environ.get("ZC_TARGET")
cands = [override] if override else sorted(
    glob.glob(os.path.expanduser("~/CDSFL_review_targets/current/*.md")))
if not cands:
    sys.exit("ABORT: staged review target not found; cannot test the real code")
TARGET = os.path.abspath(cands[0])
src_doc = open(TARGET, encoding="utf-8").read()

m = re.search(r"Listing A\b.*?```python\n(.*?)```", src_doc, re.S)
if not m:
    sys.exit("ABORT: could not locate Listing A code block in %s" % TARGET)
listing_a = m.group(1)
if "class TokenBucket" not in listing_a or "def allow" not in listing_a:
    sys.exit("ABORT: extracted block is not TokenBucket")

ns = {"time": time}
exec(compile(listing_a, TARGET + "::ListingA", "exec"), ns)   # the REAL code
TokenBucket = ns["TokenBucket"]

print("target      :", TARGET)
print("listing A   : %d lines, first line %r"
      % (len(listing_a.strip().splitlines()), listing_a.strip().splitlines()[0]))

# precondition: partly drained bucket, refill rate 0 so any rise in the token
# count can only have come from the subtraction, not from refill.
CAP, RATE = 10.0, 0.0
tb = TokenBucket(CAP, RATE)
assert tb.allow(4.0) is True, "setup: legitimate request should be admitted"

pre_tokens = tb.tokens          # SNAPSHOT before the in-place mutating call
assert pre_tokens <= CAP, "setup: bucket already above capacity before the test"

NEG = -100.0
try:
    admitted, raised = tb.allow(NEG), None
except Exception as exc:                       # a guarded implementation
    admitted, raised = None, exc
post_tokens = getattr(tb, "tokens", None)

print("capacity    : %.1f   rate: %.1f" % (CAP, RATE))
print("pre  tokens : %r" % (pre_tokens,))
print("allow(%.1f) -> %r%s" % (NEG, admitted,
      "  (raised %s: %s)" % (type(raised).__name__, raised) if raised else ""))
print("post tokens : %r" % (post_tokens,))

probe = TokenBucket(CAP, RATE); probe.allow(4.0)     # characterising probe only
try:
    probe.allow(NEG); probe_next = (probe.allow(1.0), probe.tokens)
except Exception:
    probe_next = ("n/a", "n/a")
print("next call after inflation: allow(1.0)=%r, tokens=%r" % probe_next)

defect = (
    raised is None                 # negative cost accepted, not rejected
    and admitted is True           # `tokens >= cost` passed
    and post_tokens > pre_tokens   # `tokens -= cost` INCREASED the count
    and post_tokens > CAP          # and pushed it past capacity
)

if defect:
    print("\nFALSIFIED: allow(%.1f) returned True and raised the token count "
          "%.1f -> %.1f, breaching capacity %.1f by %.1f."
          % (NEG, pre_tokens, post_tokens, CAP, post_tokens - CAP))
    raise AssertionError(
        "Listing A TokenBucket.allow admits negative cost: tokens %.1f -> %.1f "
        "exceeds capacity %.1f (0 <= tokens <= capacity violated)"
        % (pre_tokens, post_tokens, CAP))

print("\nNOT FALSIFIED: negative cost did not inflate the bucket past capacity.")
sys.exit(0)
