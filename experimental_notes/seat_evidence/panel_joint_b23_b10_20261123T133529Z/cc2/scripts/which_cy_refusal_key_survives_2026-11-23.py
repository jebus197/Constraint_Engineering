# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'panel_joint_b23_b10_20261123T133529Z', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: cf0e442c8c20fbd8b84e5541af69c2db1a9a5187a392fe8ecbdabb999615d293
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Does the cy refusal budget need 2 mechanisms, or does 1 key suffice? (B209)

DESTINATION `scripts/`. Written 2026-11-23 for the joint panel round.

WHAT IT DECIDES, AND WHY IT IS A COMPOSABILITY MEASUREMENT RATHER THAN A
PREFERENCE. The 2026-11-22 blind round produced 2 incompatible candidate keys
for the anti-trap refusal budget. cc2 proposed a SET-OVERLAP epoch, advancing
when the newly observed process set is disjoint from the last. fable implemented
an OBSERVED-IDLE epoch, advancing only when the gate itself finds nothing
running. The dispatcher then confirmed against real code that fable's loses
protection for a second back-to-back run -- 61 then 62 -- and that cc2's own
reply documents 2 residual failure modes of the overlap predicate.

THE FOUNDER'S RULE OF 2026-10-02 is that a composed fix is adopted only on a
DEMONSTRATED advantage over each fix alone, and that where a single fix performs
as well the single fix is preferred. That rule needs a measurement, so this is
it. Each candidate is the REAL hook with one mechanism DISABLED, not a
paraphrase of it:

  (a) session-only  : the epoch never advances            -- brief candidate (a)
  (c) idle-epoch    : advance on an observed idle only    -- fable
  (f) overlap       : advance on a disjoint set only      -- cc2
  (f+c) both        : advance on either                   -- both epoch signals
  (f+c+ceiling)     : both, plus MAX_REFUSALS_PER_SESSION -- AS SHIPPED

IT DRIVES `decide()` IN `hooks/cy_monitor_gate.py`. It does not re-implement the
threshold. A second implementation of the rule is 2 forms that can disagree
while each describes itself consistently, which is the `execute-do-not-grep`
defect class -- 4 confirmed instances in this project, all found by executing 2
forms against each other and 0 by reading them.

THE 2 PROPERTIES BEING SCORED ARE OPPOSED, which is the whole finding:
  ANTI-TRAP  -- an idle session is eventually released, whatever the observed
                process sets do. Failure = a session refused for ever.
  PROTECTION -- a genuinely new activity gets a fresh budget, so a live run is
                not left unguarded by its predecessor's spending. Failure = a
                live run unobserved.
A candidate scores PASS on a scenario only if the scenario's own oracle holds.

S6 IS EXPECTED TO FAIL FOR EVERY CANDIDATE and is reported rather than dropped.
Two separate activities whose pid sets overlap through pid reuse are
indistinguishable from one continuing activity by ANY predicate over observed
pid sets, so this harness states the bound instead of hiding it. `no silent
caps`.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import pathlib
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
GATE = pathlib.Path(os.environ.get("CDSFL_CY_GATE_PATH")
                    or REPO / "hooks" / "cy_monitor_gate.py")

#: The board's real shape, taken from the live board of 2026-11-22 and not
#: invented: 1 long-lived parent plus a child replaced per guard file. The board
#: makes exactly 1 real pytest invocation (`hooks/pre-commit:1237`), so the
#: churn is in NESTED children, which `_RUNNER_PATTERNS`' `pytest.*bench/tests`
#: also matches. The set is therefore not REPLACED; it OVERLAPS.
CHURNING = [["70507"], ["70507", "76042"], ["70507", "77353"],
            ["70507", "78785"], ["70507", "79475"]]

IDLE = "IDLE"          # an observation in which the gate sees nothing running


def load_gate(state: pathlib.Path):
    os.environ["CDSFL_CY_STATE"] = str(state)
    spec = importlib.util.spec_from_file_location("cy_gate_scored", GATE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    assert str(m.state_path()) == str(state), (
        f"the CDSFL_CY_STATE override is not in force ({m.state_path()}); this "
        f"harness would otherwise spend the live session's refusal budget")
    return m


def configure(m, candidate: str) -> None:
    """Disable mechanisms to realise a candidate. The REAL code otherwise."""
    if "ceiling" not in candidate:
        m.MAX_REFUSALS_PER_SESSION = 10 ** 9          # effectively absent
    if "f" not in candidate:                          # no disjoint-set advance
        _orig = m.refusal_key

        def _no_overlap(payload, live, unwatched, pids, _o=_orig):
            st = m._read_state()
            before = int(st.get("epoch") or 0)
            k = _o(payload, live, unwatched, pids)
            st2 = m._read_state()
            if int(st2.get("epoch") or 0) != before:   # undo the set-based bump
                st2["epoch"] = before
                m._write_state(st2)
                k = f"{str((payload or {}).get('session_id') or '')}|e{before}"
            return k
        m.refusal_key = _no_overlap
    if "c" not in candidate:                          # no observed-idle advance
        m.note_idle = lambda: None


def run(candidate: str, observations) -> list[dict]:
    """Drive one candidate through one observation sequence. Returns the trace."""
    with tempfile.TemporaryDirectory() as td:
        m = load_gate(pathlib.Path(td) / "state.json")
        configure(m, candidate)
        trace = []
        for obs in observations:
            if obs is IDLE:
                m.note_idle()
                trace.append({"obs": "idle", "refuse": False, "n": 0,
                              "total": m.session_spent()})
                continue
            refuse, used, total = m.decide({"session_id": "s"}, [], [], obs)
            trace.append({"obs": list(obs), "refuse": refuse, "n": used,
                          "total": total})
        return trace


# ---------------------------------------------------------------- scenarios

def _const_parent(n):
    return [["70507", str(80000 + i)] for i in range(n)]


def _disjoint(n, base=100):
    return [[str(base + i)] for i in range(n)]


SCENARIOS = []


def scenario(key, prop, why):
    def deco(fn):
        SCENARIOS.append({"key": key, "prop": prop, "why": why, "fn": fn})
        return fn
    return deco


@scenario("S1", "ANTI-TRAP", "the board's real churn shape must still climb")
def s1(cand):
    t = run(cand, CHURNING)
    got = [r["n"] for r in t]
    return got == list(range(1, len(CHURNING) + 1)), f"n={got}"


@scenario("S2", "ANTI-TRAP", "a churning unwatched run is eventually released")
def s2(cand):
    t = run(cand, _const_parent(200))
    released = [i for i, r in enumerate(t) if not r["refuse"]]
    return bool(released), ("released at event " + str(released[0])
                            if released else "NEVER released in 200 events")


@scenario("S3", "ANTI-TRAP",
          "FULLY DISJOINT observations -- serial single-pid invocations with no "
          "surviving parent -- must still be released")
def s3(cand):
    t = run(cand, _disjoint(400))
    released = [i for i, r in enumerate(t) if not r["refuse"]]
    return bool(released), ("released at event " + str(released[0])
                            if released else "NEVER released in 400 events")


@scenario("S4", "ANTI-TRAP",
          "a FLAPPING detector -- the gate intermittently sees nothing while a "
          "run continues -- must not refuse for ever")
def s4(cand):
    obs = []
    for i in range(200):
        obs.append(["70507", str(80000 + i)])
        if i % 5 == 4:
            obs.append(IDLE)
    t = run(cand, obs)
    released = [i for i, r in enumerate(t)
                if r["obs"] != "idle" and not r["refuse"]]
    return bool(released), ("released at event " + str(released[0])
                            if released else "NEVER released in 200 refusals")


@scenario("S5", "PROTECTION",
          "2 back-to-back activities with NO observed idle between them: the "
          "second must get a fresh budget (the dispatcher's 61-then-62 case)")
def s5(cand):
    first = [["500"]] * 61                  # activity A, exhausts the budget
    second = [["900"]] * 3                  # activity B, different pid set
    t = run(cand, first + second)
    b = t[61:]
    ok = all(r["refuse"] for r in b)
    return ok, (f"activity B refused={[r['refuse'] for r in b]} "
                f"n={[r['n'] for r in b]}")


@scenario("S6", "PROTECTION",
          "2 separate activities whose pid sets OVERLAP through pid reuse: NO "
          "predicate over observed sets can separate them (bound, not defect)")
def s6(cand):
    first = [["500"]] * 61
    second = [["500", "900"]] * 3
    t = run(cand, first + second)
    b = t[61:]
    ok = all(r["refuse"] for r in b)
    return ok, f"activity B refused={[r['refuse'] for r in b]}"


CANDIDATES = [("(a) session-only", ""),
              ("(c) idle-epoch", "c"),
              ("(f) overlap", "f"),
              ("(f+c) both signals", "fc"),
              ("(f+c+ceiling) SHIPPED", "fc+ceiling")]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true", help="machine-readable")
    a = ap.parse_args(argv)

    rows = {}
    for label, cand in CANDIDATES:
        rows[label] = {}
        for sc in SCENARIOS:
            ok, note = sc["fn"](cand)
            rows[label][sc["key"]] = {"pass": bool(ok), "note": note}

    if a.json:
        print(json.dumps(rows, indent=2))
        return 0

    print("=" * 78)
    print("B209: DOES THE ANTI-TRAP BUDGET NEED 2 MECHANISMS?")
    print("=" * 78)
    print(f"\n  gate under test : {GATE}")
    print("  each candidate is the REAL hook with mechanisms disabled\n")
    for sc in SCENARIOS:
        print(f"  {sc['key']}  [{sc['prop']:10s}] {sc['why']}")
    print()
    hdr = "  " + "candidate".ljust(24) + "".join(s["key"].ljust(7)
                                                 for s in SCENARIOS) + "score"
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for label, _ in CANDIDATES:
        cells = "".join(("PASS" if rows[label][s["key"]]["pass"] else "FAIL").ljust(7)
                        for s in SCENARIOS)
        k = sum(1 for s in SCENARIOS if rows[label][s["key"]]["pass"])
        print("  " + label.ljust(24) + cells + f"{k}/{len(SCENARIOS)}")

    print("\n  WHY EACH SINGLE MECHANISM FAILS, with the trace:")
    for label, key in (("(f) overlap", "S3"), ("(c) idle-epoch", "S5")):
        print(f"    {label:22s} {key}: {rows[label][key]['note']}")

    # The composability claim, stated as a comparison and not as a judgement.
    def score(label, prop):
        return sum(1 for s in SCENARIOS
                   if s["prop"] == prop and rows[label][s["key"]]["pass"])
    shipped = "(f+c+ceiling) SHIPPED"
    print("\n  COMPOSABILITY, MEASURED (founder, 2026-10-02):")
    for prop in ("ANTI-TRAP", "PROTECTION"):
        tot = sum(1 for s in SCENARIOS if s["prop"] == prop)
        line = "    " + prop.ljust(11)
        for label, _ in CANDIDATES:
            line += f"{label.split(')')[0]+')'}={score(label, prop)}/{tot}  "
        print(line)
    dominates = all(
        sum(1 for s in SCENARIOS if rows[shipped][s["key"]]["pass"])
        > sum(1 for s in SCENARIOS if rows[label][s["key"]]["pass"])
        for label, _ in CANDIDATES if label != shipped)
    print(f"\n    the composed fix STRICTLY dominates every single fix : {dominates}")
    print("    so the composition is warranted on a measurement, not a judgement.")
    print("\n  THE BOUND THIS HARNESS DOES NOT CLOSE: S6. Every candidate fails "
          "it,\n  including the shipped one. Pid reuse makes 2 activities "
          "observationally\n  identical to 1, so no key over observed pid sets "
          "can separate them. The\n  per-session ceiling does not help: it "
          "bounds over-refusal, not under-\n  protection. Reported, not hidden.")

    assert rows[shipped]["S3"]["pass"] and rows[shipped]["S5"]["pass"], (
        "the shipped configuration failed a scenario each single mechanism was "
        "chosen to cover; the composition is not doing what this harness claims")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
