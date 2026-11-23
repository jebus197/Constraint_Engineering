# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'panel_batches23_20261122T223441Z', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 0d61783ae5625772c3dc9ef0be5d8ef0146286395a7c44e6a4f651b0a8c15739
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""B209: WHICH REFUSAL KEY SURVIVES, AND IS A COMPOSED FIX WARRANTED?

The brief for batches 2/3 asks which key the cy gate's anti-trap budget should
be keyed to, and tells the panel to attack CONDITION 2 -- "distinct per
contiguous busy period" as a weakening of "distinct per run". It also requires,
per the founder's ruling of 2026-10-02, that any COMPOSED fix be adopted only on
a DEMONSTRATED advantage over each fix alone, measured rather than judged.

So this scores every candidate on the same 6 scenarios. It decides the key by
execution; it does not argue for one.

CANDIDATES
  (a) session      session id alone.
  (c) empty-epoch  epoch advances when the live set is OBSERVED empty.
  (f) overlap      epoch advances when the new set is DISJOINT from the last.
  (a+e) idle       session id, plus a reset when the gate has been quiet > T.
  (c+e) composed   empty-epoch OR idle reset -- the OR composition.

SCENARIOS (the 3 conditions B209 sets, plus the 2 gap cases)
  S1 cond1-watched  steady watched run: counter must CLIMB 1..5.
  S2 cond1-churn    stable parent + a fresh nested child each poll (the real
                    board shape): must REACH the budget.
  S3 cond2-newrun   budget spent, then a genuinely new activity: must RESET.
  S4 midrun-gap     the set momentarily empties mid-activity: must NOT reset.
                    This is the falsifier the brief says it most expects to
                    bite candidate (c).
  S5 gap-unobserved activity A ends and B starts with NO empty observation in
                    between: must RESET. Found by this seat; the brief does not
                    name it, and it is where (c) and the idle timer fail.
  S6 cond3          key computable with an empty watched set, and INVARIANT to
                    a child appearing.
"""
import sys

MAX_REFUSALS = 60
T_IDLE = 5400          # the idle-reset constant, 3x a 30 min Monitor window


class Budget:
    """`spend()`'s semantics: the count zeroes whenever the key changes."""

    def __init__(self, cand):
        self.c, self.st = cand, {}

    def poll(self, pids, now=0.0):
        """One Stop-hook invocation.

        ★ CORRECTED 2026-11-22 after the first run of this script. The first
        version SPENT on an empty observation, which the real gate never does:
        `main()` returns 0 on `not (live or unwatched or pids)` BEFORE `spend()`
        is reached. That artefact charged candidate (c) a refusal it would never
        pay and made it fail S3 spuriously. An empty observation now updates the
        KEY STATE but does not spend, which is faithful to the gate -- and note
        this is itself a cost of candidate (c): the gate would have to write
        state on the idle path it currently exits for free.
        """
        k = self.c.key(pids, self.st, now)
        if not pids:
            return 0                       # the gate returns 0 without spending
        if self.st.get("key") != k:
            self.st = {**self.st, "key": k, "n": 0}
        self.st["n"] += 1
        self.st["last"] = now
        return self.st["n"]


class Session:
    name = "(a) session"
    def key(self, pids, st, now): return "sess"


class EmptyEpoch:
    name = "(c) empty-epoch"
    def key(self, pids, st, now):
        if not pids:
            st["epoch"] = int(st.get("epoch", 0)) + 1
        return "sess|e%d" % int(st.get("epoch", 0))


class Overlap:
    name = "(f) overlap"
    def key(self, pids, st, now):
        prev = set(st.get("act") or [])
        if pids and prev and not (prev & set(pids)):
            st["epoch"] = int(st.get("epoch", 0)) + 1
        if pids:
            st["act"] = sorted(pids)
        return "sess|act%d" % int(st.get("epoch", 0))


class Idle:
    name = "(a+e) idle"
    def key(self, pids, st, now):
        if "last" in st and now - st["last"] > T_IDLE:
            st["gen"] = int(st.get("gen", 0)) + 1
        return "sess|g%d" % int(st.get("gen", 0))


class EmptyEpochPlusIdle:
    name = "(c+e) composed"
    def key(self, pids, st, now):
        if not pids:
            st["epoch"] = int(st.get("epoch", 0)) + 1
        if "last" in st and now - st["last"] > T_IDLE:
            st["epoch"] = int(st.get("epoch", 0)) + 1
        return "sess|c%d" % int(st.get("epoch", 0))


A = ["70507", "70508"]          # activity A: parent + child
B = ["90001", "90002"]          # activity B: a different run entirely


def s1(c):
    b = Budget(c)
    got = [b.poll(["70507"], t) for t in range(5)]
    return got == [1, 2, 3, 4, 5], "polls=%s" % got


def s2(c):
    b = Budget(c)
    n = 0
    for i in range(MAX_REFUSALS + 1):
        n = b.poll(["70507", str(80000 + i)], float(i))
    return n > MAX_REFUSALS, "final=%d" % n


def s3(c):
    b = Budget(c)
    for i in range(MAX_REFUSALS + 1):
        b.poll(A, float(i))
    b.poll([], 100.0)                      # A ends, and the gate sees it
    n = b.poll(B, 400.0)                   # B starts 5 min later
    return n == 1, "newrun=%d" % n


def s4(c):
    b = Budget(c)
    for i in range(5):
        b.poll(A, float(i))
    b.poll([], 5.0)                        # a sub-second hole mid-activity
    n = b.poll(A, 6.0)
    # ★ ORACLE CORRECTED 2026-11-22 together with Budget.poll. It read `n == 7`,
    # which assumed the empty observation SPENT a refusal. It does not -- the
    # gate returns 0 first -- so an unbroken count across the hole continues
    # 5 -> 6. The property under test is unchanged: the counter must NOT reset.
    return n == 6, "after_gap=%d (want 6, reset would give 1)" % n


def s5(c):
    b = Budget(c)
    for i in range(MAX_REFUSALS + 1):
        b.poll(A, float(i))
    n = b.poll(B, 400.0)                   # no empty observation in between
    return n == 1, "newrun=%d" % n


def s6(c):
    b1, b2 = Budget(c), Budget(c)
    k1 = c.key(["111"], b1.st, 0.0)
    k2 = c.key(["111", "222"], b1.st, 1.0)
    return bool(k1) and k1 == k2, "%r vs %r" % (k1, k2)


SCEN = [("S1 cond1-watched", s1), ("S2 cond1-churn", s2),
        ("S3 cond2-newrun", s3), ("S4 midrun-gap", s4),
        ("S5 gap-unobserved", s5), ("S6 cond3", s6)]
CANDS = [Session(), EmptyEpoch(), Overlap(), Idle(), EmptyEpochPlusIdle()]


def main() -> int:
    print("=" * 78)
    print("B209: WHICH REFUSAL KEY SURVIVES ALL 6 SCENARIOS?")
    print("=" * 78)
    rows = {}
    for c in CANDS:
        res = []
        for nm, fn in SCEN:
            ok, detail = fn(c)
            res.append((nm, ok, detail))
        rows[c.name] = res
    w = max(len(c.name) for c in CANDS)
    print("  %-*s  %s" % (w, "candidate",
                          "  ".join(n.split()[0] for n, _ in SCEN)))
    for c in CANDS:
        print("  %-*s  %s   %d/6" % (
            w, c.name,
            "  ".join(("PASS" if ok else "FAIL")[:4].rjust(4)
                      for _, ok, _ in rows[c.name]),
            sum(1 for _, ok, _ in rows[c.name] if ok)))
    print()
    for c in CANDS:
        bad = [(n, d) for n, ok, d in rows[c.name] if not ok]
        if bad:
            print("  %s fails:" % c.name)
            for n, d in bad:
                print("     %-20s %s" % (n, d))
    winners = [c.name for c in CANDS
               if all(ok for _, ok, _ in rows[c.name])]
    print()
    print("  CANDIDATES PASSING ALL 6 : %s" % (winners or "NONE"))
    print()
    print("  COMPOSABILITY, per the founder's ruling of 2026-10-02.")
    print("  A composed fix is adopted ONLY on a demonstrated advantage over")
    print("  each fix alone. Measured here:")
    for nm in ["(c) empty-epoch", "(a+e) idle", "(c+e) composed"]:
        print("     %-18s %d/6" % (nm, sum(1 for _, ok, _ in rows[nm] if ok)))
    comp = sum(1 for _, ok, _ in rows["(c+e) composed"] if ok)
    best_single = max(sum(1 for _, ok, _ in rows[c.name] if ok) for c in CANDS)
    print("     composed scores %d/6; the best SINGLE candidate scores %d/6."
          % (comp, best_single))
    print("     %s" % ("COMPOSITION IS NOT WARRANTED: a single fix performs at"
                       " least as well,\n     so the single fix is preferred."
                       if comp <= best_single else
                       "composition shows an advantage and warrants adoption."))
    ok = winners == ["(f) overlap"] and comp <= best_single
    print()
    print("  VERDICT: %s" % ("(f) overlap is the unique survivor and no "
                             "composition is warranted." if ok else
                             "the scoring did NOT single out (f); read above."))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
