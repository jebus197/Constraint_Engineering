#!/usr/bin/env python3
"""Falsifier for the review finding against Listing A (TokenBucket.allow):

    "allow accepts negative cost. If cost < 0 then `self.tokens >= cost` is True
     and `self.tokens -= cost` INCREASES the token count, potentially exceeding
     self.capacity."

Loads the REAL Listing A from the staged review document by absolute path
(never a re-typed copy), execs it, drives the real allow() path, snapshots
self.tokens BEFORE each in-place mutating call.

Prints FALSIFIED and raises AssertionError iff the defect is genuinely present.
Exits 0 if the code is guarded.
"""
import glob, os, re, sys, time

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

ns = {"time": time}
exec(compile(listing_a, TARGET + "::ListingA", "exec"), ns)   # the REAL code
TokenBucket = ns["TokenBucket"]

print("target    :", TARGET)
print("listing A : %d lines, head %r"
      % (len(listing_a.strip().splitlines()), listing_a.strip().splitlines()[0]))

CAP, RATE, NEG = 10.0, 0.0, -100.0   # rate 0 => refill can contribute nothing


def probe(cls):
    """Drive the real path. Returns (invariant_breach, ratelimit_bypass, trace)."""
    t = {}
    # --- Part 1: invariant 0 <= tokens <= capacity -------------------------
    b = cls(CAP, RATE)
    if b.allow(4.0) is not True:
        sys.exit("ABORT: setup failed, legitimate unit request refused")
    pre = b.tokens                                   # SNAPSHOT before mutation
    if pre > CAP:
        sys.exit("ABORT: bucket already above capacity before the test")
    try:
        admitted, raised = b.allow(NEG), None
    except Exception as exc:                         # a guarded implementation
        admitted, raised = None, exc
    post = getattr(b, "tokens", None)
    t.update(pre=pre, post=post, admitted=admitted, raised=raised)
    breach = (raised is None and admitted is True
              and post > pre and post > CAP)

    # --- Part 2: consequence — rate-limit bypass on a drained bucket -------
    d = cls(CAP, RATE)
    d.allow(CAP)                                     # drain to exactly zero
    pre_d = d.tokens                                 # SNAPSHOT before mutation
    refused_before = d.allow(1.0) is False           # limiter working as designed
    try:
        d.allow(NEG); bypass_raised = None
    except Exception as exc:
        bypass_raised = exc
    admitted_after = d.allow(1.0) is True            # refilled without any refill
    t.update(pre_d=pre_d, refused_before=refused_before,
             bypass_raised=bypass_raised, admitted_after=admitted_after,
             post_d=getattr(d, "tokens", None))
    bypass = (bypass_raised is None and refused_before and admitted_after)
    return breach, bypass, t


breach, bypass, t = probe(TokenBucket)
print("\n-- part 1: invariant --")
print("capacity %.1f  rate %.1f" % (CAP, RATE))
print("pre  tokens        : %r" % (t["pre"],))
print("allow(%.1f)      -> %r%s" % (NEG, t["admitted"],
      "  (raised %s: %s)" % (type(t["raised"]).__name__, t["raised"])
      if t["raised"] else ""))
print("post tokens        : %r   (capacity %.1f)" % (t["post"], CAP))
print("\n-- part 2: consequence --")
print("drained tokens     : %r" % (t["pre_d"],))
print("allow(1.0) before  : refused=%r" % (t["refused_before"],))
print("allow(1.0) after   : admitted=%r  tokens=%r" % (t["admitted_after"], t["post_d"]))

# ------------------------------------------------- negative control (anti-tautology)
class Guarded(TokenBucket):
    def allow(self, cost=1.0):
        if cost < 0:
            raise ValueError("cost must be non-negative")
        return TokenBucket.allow(self, cost)

ctrl_breach, ctrl_bypass, _ = probe(Guarded)
print("\n-- negative control (guarded subclass) --")
print("breach=%r bypass=%r  (both must be False for the test to mean anything)"
      % (ctrl_breach, ctrl_bypass))
if ctrl_breach or ctrl_bypass:
    sys.exit("ABORT: falsifier fires on guarded code — test is a tautology")

if breach or bypass:
    print("\nFALSIFIED: Listing A TokenBucket.allow admits negative cost.")
    if breach:
        print("  invariant: tokens %.1f -> %.1f exceeds capacity %.1f by %.1f"
              % (t["pre"], t["post"], CAP, t["post"] - CAP))
    if bypass:
        print("  bypass   : a bucket drained to %.1f with refill rate %.1f/s "
              "refused a unit request, then admitted one immediately after a "
              "single allow(%.1f) — the rate limit is defeated without waiting."
              % (t["pre_d"], RATE, NEG))
    raise AssertionError(
        "TokenBucket.allow(cost<0): `tokens >= cost` passes and `tokens -= cost` "
        "raises the count (%.1f -> %.1f > capacity %.1f); invariant "
        "0 <= tokens <= capacity violated and the limiter is bypassable"
        % (t["pre"], t["post"], CAP))

print("\nNOT FALSIFIED: negative cost neither breached capacity nor bypassed the limit.")
sys.exit(0)
