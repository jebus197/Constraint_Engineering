# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'panel_joint_b23_b10_20261123T133529Z', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 233487873a627df760bb10274496e705be71d118265db95b72ff40d7ebec07c6
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""B209 joint round: does a 2-SIDED reset beat the overlap key? Measured.

DESTINATION `scripts/`. Written 2026-11-23 at the joint round on batches 2/3.

THE QUESTION THE BRIEF ASKS. The commit board's convergence gate is 2-sided --
it requires BOTH a flattened curve AND K consecutive zero-new rounds -- and the
brief asks whether the cy gate's anti-trap counter needs the same 2-sided shape
rather than 1 key. The founder's composability ruling of 2026-10-02 makes that
a MEASUREMENT: compose only on a demonstrated advantage over each fix alone.

THE 2 RESET SIGNALS ERR IN OPPOSITE DIRECTIONS, which is why the analogy to the
convergence gate was expected to fail: there, both conditions guard the SAME
failure (premature convergence), so conjunction tightens it. Here, resetting
too EAGERLY re-opens B209 (the counter never reaches 60; a session can be
trapped) and resetting too RARELY carries an exhausted budget into a live run
(a stop is allowed while a run is unobserved). A conjunction imports the
too-rare side; a disjunction imports the too-eager side. This script checks
that prediction by execution rather than keeping it as prose.

CANDIDATES
  (c)   empty-epoch  reset when the live set is OBSERVED empty (the implemented
                     `note_idle` repair of the prior round).
  (f)   overlap      reset when the new set is DISJOINT from the last (cc2's
                     proposal, adopted with the state-preserving `spend()`).
  (f|c) disjunction  reset on EITHER signal.
  (f&c) conjunction  reset only when an emptiness was observed since the last
                     spend AND the new set is disjoint -- the 2-sided shape.

SCENARIOS. S1-S6 are seat cc2's, reproduced from
`experimental_notes/seat_evidence/panel_batches23_20261122T223441Z/cc2/scripts/
which_cy_refusal_key_survives_2026-11-22.py` (sha 0d61783ae5625772) so the
baseline is the table the brief already reproduced. R1 and R2 are the 2
residual modes cc2 NAMED in the adopted key's own docstring, promoted to
scenarios so the composition question is scored on the full known set:
  R1 wholesale-replacement  the set is replaced with NO overlap MID-activity:
                            must NOT reset (else B209 returns in a slower form).
  R2 pid-reuse              a new activity REUSES a pid of the exhausted one,
                            with no empty observation: must reset.

WHICH FAILURES ARE DEMONSTRATED AND WHICH ARE CONSTRUCTED, because a tie on
count is broken by consequence and reality, not by arithmetic (severity is
ORDINAL; a count of scenario passes is reported, never summed consequences):
  S5 is CONFIRMED against the competing implemented hook by the dispatcher
     (exhausts at 61, opens at 62: a live run unprotected).
  S2 is the measured board shape of 2026-11-22.
  S4 requires a Stop landing inside a sub-second process gap; R1 a process
     shape never observed on the measured board; R2 kernel pid reuse matching
     `_RUNNER_PATTERNS` between 2 consecutive polls. None of the 3 has been
     observed on this machine.
"""
import sys

MAX_REFUSALS = 60


class Budget:
    """`spend()`'s semantics, state-preserving as adopted: the count zeroes
    whenever the key changes; everything else in the dict survives."""

    def __init__(self, cand):
        self.c, self.st = cand, {}

    def poll(self, pids, now=0.0):
        if not pids:
            self.c.saw_empty(self.st)
            return 0                   # the gate returns 0 without spending
        k = self.c.key(pids, self.st, now)
        if self.st.get("key") != k:
            self.st["key"] = k
            self.st["n"] = 0
        self.st["n"] = self.st.get("n", 0) + 1
        return self.st["n"]


class EmptyEpoch:
    name = "(c) empty-epoch"
    def saw_empty(self, st): st["idle_seen"] = True
    def key(self, pids, st, now):
        if st.pop("idle_seen", False):
            st["epoch"] = int(st.get("epoch", 0)) + 1
        return "sess|e%d" % int(st.get("epoch", 0))


class Overlap:
    name = "(f) overlap"
    def saw_empty(self, st): pass
    def key(self, pids, st, now):
        prev = set(st.get("act") or [])
        if prev and not (prev & set(pids)):
            st["epoch"] = int(st.get("epoch", 0)) + 1
        st["act"] = sorted(pids)
        return "sess|act%d" % int(st.get("epoch", 0))


class Disjunction:
    name = "(f|c) either"
    def saw_empty(self, st): st["idle_seen"] = True
    def key(self, pids, st, now):
        prev = set(st.get("act") or [])
        if st.pop("idle_seen", False) or (prev and not (prev & set(pids))):
            st["epoch"] = int(st.get("epoch", 0)) + 1
        st["act"] = sorted(pids)
        return "sess|o%d" % int(st.get("epoch", 0))


class Conjunction:
    name = "(f&c) 2-sided"
    #: ★ CORRECTED AGAINST MY OWN INTEREST before first citation: the first
    #: version never stored `act`, so its disjointness arm was VACUOUS and it
    #: failed S3 spuriously (and could never advance at all). The correction is
    #: recorded here rather than quietly made, matching cc2's own practice in
    #: the harness this extends.
    def saw_empty(self, st): st["idle_seen"] = True
    def key(self, pids, st, now):
        prev = set(st.get("act") or [])
        if st.get("idle_seen") and prev and not (prev & set(pids)):
            st["epoch"] = int(st.get("epoch", 0)) + 1
            st["idle_seen"] = False
        st["act"] = sorted(pids)
        return "sess|b%d" % int(st.get("epoch", 0))


A = ["70507", "70508"]
B = ["90001", "90002"]


def s1(c):
    b = Budget(c)
    got = [b.poll(["70507"], t) for t in range(5)]
    return got == [1, 2, 3, 4, 5], "polls=%s" % got

def s2(c):
    b = Budget(c); n = 0
    for i in range(MAX_REFUSALS + 1):
        n = b.poll(["70507", str(80000 + i)], float(i))
    return n > MAX_REFUSALS, "final=%d" % n

def s3(c):
    b = Budget(c)
    for i in range(MAX_REFUSALS + 1):
        b.poll(A, float(i))
    b.poll([], 100.0)
    n = b.poll(B, 400.0)
    return n == 1, "newrun=%d" % n

def s4(c):
    b = Budget(c)
    for i in range(5):
        b.poll(A, float(i))
    b.poll([], 5.0)
    n = b.poll(A, 6.0)
    return n == 6, "after_gap=%d (want 6, reset gives 1)" % n

def s5(c):
    b = Budget(c)
    for i in range(MAX_REFUSALS + 1):
        b.poll(A, float(i))
    n = b.poll(B, 400.0)
    return n == 1, "newrun=%d" % n

def s6(c):
    b = Budget(c)
    k1 = c.key(["111"], b.st, 0.0)
    k2 = c.key(["111", "222"], b.st, 1.0)
    return bool(k1) and k1 == k2, "%r vs %r" % (k1, k2)

def r1(c):
    b = Budget(c)
    got = [b.poll(["1", "2"], 0.0), b.poll(["1", "3"], 1.0),
           b.poll(["7", "8"], 2.0)]           # full replacement, SAME activity
    return got == [1, 2, 3], "polls=%s" % got

def r2(c):
    b = Budget(c)
    for i in range(MAX_REFUSALS + 1):
        b.poll(["100", str(200 + i)], float(i))
    n = b.poll(["100", "999"], 400.0)          # "100" reused by a NEW run
    return n == 1, "newrun=%d" % n


SCEN = [("S1", s1), ("S2", s2), ("S3", s3), ("S4", s4), ("S5", s5),
        ("S6", s6), ("R1", r1), ("R2", r2)]
DEMONSTRATED = {"S2", "S5"}          # observed/confirmed on this machine
CANDS = [EmptyEpoch(), Overlap(), Disjunction(), Conjunction()]


def main() -> int:
    print("=" * 74)
    print("DOES A 2-SIDED RESET BEAT THE OVERLAP KEY? (scored, not judged)")
    print("=" * 74)
    rows = {}
    for c in CANDS:
        rows[c.name] = [(nm, *fn(c)) for nm, fn in SCEN]
    w = max(len(c.name) for c in CANDS)
    print("  %-*s  %s" % (w, "candidate", "    ".join(n for n, _ in SCEN)))
    for c in CANDS:
        print("  %-*s  %s   %d/8" % (w, c.name,
              "  ".join(("PASS" if ok else "FAIL") for _, ok, _ in rows[c.name]),
              sum(ok for _, ok, _ in rows[c.name])))
    print()
    for c in CANDS:
        bad = [(n, d) for n, ok, d in rows[c.name] if not ok]
        if bad:
            demo = [n for n, _ in bad if n in DEMONSTRATED]
            print("  %s fails: %s%s" % (
                c.name, ", ".join("%s (%s)" % t for t in bad),
                "   <- includes a DEMONSTRATED scenario: %s" % demo if demo
                else "   (all constructed, none observed on this machine)"))
    f_fail = {n for n, ok, _ in rows["(f) overlap"] if not ok}
    and_fail = {n for n, ok, _ in rows["(f&c) 2-sided"] if not ok}
    or_fail = {n for n, ok, _ in rows["(f|c) either"] if not ok}
    print()
    print("  VERDICT, per the founder's composability ruling of 2026-10-02:")
    dominated = (and_fail & DEMONSTRATED or or_fail & DEMONSTRATED) and not (f_fail & DEMONSTRATED)
    if dominated:
        print("    NEITHER composition dominates the overlap key alone. Every")
        print("    composed candidate fails at least 1 DEMONSTRATED scenario or")
        print("    scores no better; the single fix is preferred. The 2 reset")
        print("    signals err in opposite directions, so the convergence gate's")
        print("    2-sided analogy does not transfer.")
        return 0
    print("    A composition shows an advantage; re-read the table.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
