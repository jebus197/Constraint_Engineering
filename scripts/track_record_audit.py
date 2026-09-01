#!/usr/bin/env python3
"""Can the archive show that its own verdicts were tool-decided, and not voted?

WHY THIS EXISTS
---------------
On 2026-08-21 an assistant (CC1) told the founder that "the founding principle is
currently unauditable on its own record", repeating a reviewer's claim without
checking it against the archive. This script is that check. It was written on
2026-08-22 and it refutes the claim for every run from exp42 onward.

Every figure it prints is derived from `bench/logs/*/*_report.json` alone. It
dispatches nothing, writes nothing, and costs nothing. Run it again whenever the
archive grows.

    python3 scripts/track_record_audit.py

THE MEASUREMENTS
----------------
M3  how much of the archive carries a recorded falsifier verdict, split by era
M5  does the recorded status track the recorded tool verdict
M6  when tool and model majority DISAGREE, which one prevails
M7  falsifiers that did not run but wrote a terminal status anyway

M6 is the load-bearing one. Its known weaknesses are printed with it rather than
left for a reader to find: the disagreements cluster in one run, the mapping from
a vote label to an intended status is a construction, and the ambiguous case is
counted AGAINST the tool, not excluded.
"""
from __future__ import annotations
import collections, json, pathlib, re, sys

REPO = pathlib.Path(__file__).resolve().parent.parent
MODERN_FROM = 42          # the falsifier gate entered the code 2026-06-03 (4fba6cc)
TERMINAL = {"CLOSED", "CONFIRMED", "MERGED", "REFUTED", "REJECTED"}
TOOL_VERDICTS = {"CONFIRMED", "REFUTED", "REJECTED", "INCONCLUSIVE", "ERROR",
                 "NOT_APPLICABLE", "UNCERTAIN", "UNTOOLABLE", "NON_DISCRIMINATING"}
# What each side would have the terminal status be. The TOOL rows are the runner's
# documented behaviour (apply_falsifier_verdicts docstring); the VOTE rows are a
# reading of the vote labels and are therefore a CONSTRUCTION, flagged as such.
TOOL_WANTS = {"CONFIRMED": {"CLOSED", "CONFIRMED"}, "REFUTED": {"REFUTED"},
              "ERROR": {"UNCONFIRMED", "OPEN"}, "UNTOOLABLE": {"UNCONFIRMED", "OPEN"}}
VOTE_WANTS = {"CONFIRM": {"CLOSED", "CONFIRMED"}, "EXTEND": {"CLOSED", "CONFIRMED"},
              "REFUTE": {"REFUTED"}, "REFUTED": {"REFUTED"}, "MERGE": {"MERGED"},
              "REOPEN": {"OPEN", "UNCONFIRMED"}, "CHALLENGE": {"OPEN", "UNCONFIRMED"}}


_SKIPPED: set = set()


def entries():
    """Yield (run_name, era, canonical_id, entry) for every archived registry entry."""
    for rp in sorted(p for p in (REPO / "bench/logs").glob("*/*_report.json")
                     if ".errata" not in str(p)):
        nm = rp.parent.name
        if nm.endswith("_latest"):
            # A byte-equivalent duplicate of a timestamped directory. Counting it
            # inflated an earlier draft to 2,247 entries / 27.5% backed; the true
            # figures are 2,030 / 31.5%. CC2 caught it, 2026-08-22.
            _SKIPPED.add(nm)
            continue
        m = re.match(r"exp(\d+)", nm)
        if not m:
            continue
        era = "MODERN" if int(m.group(1)) >= MODERN_FROM else "LEGACY"
        try:
            d = json.loads(rp.read_text(encoding="utf-8", errors="replace"))
        except Exception:                 # noqa: BLE001 — a corrupt report is not fatal
            continue
        for cid, e in ((d.get("registry") or {}).get("entries") or {}).items():
            yield nm, era, cid, e


def main() -> int:
    rows = list(entries())
    if not rows:
        print("  no archived reports found — nothing to audit"); return 1

    # ---- M3: coverage, by era -------------------------------------------------
    cov = collections.defaultdict(collections.Counter)
    st_cov = collections.defaultdict(collections.Counter)
    runs = collections.defaultdict(set)
    for nm, era, _cid, e in rows:
        st = (e.get("status") or "").upper()
        fv = (e.get("falsifier_verdict") or "").strip().upper()
        backed = fv in TOOL_VERDICTS and fv not in ("UNTOOLABLE", "NON_DISCRIMINATING")
        runs[era].add(nm)
        cov[era]["entries"] += 1
        cov[era]["fcode"] += bool((e.get("falsifier_code") or "").strip())
        if st in TERMINAL:
            cov[era]["terminal"] += 1
            cov[era]["backed"] += backed
            st_cov[(era, st)]["n"] += 1
            st_cov[(era, st)]["b"] += backed

    print("M3  COVERAGE — how much of the archive can show what decided it\n")
    for era in ("MODERN", "LEGACY"):
        c = cov[era]
        if not c: continue
        lab = (f"{era} (exp{MODERN_FROM}+, from 2026-06)" if era == "MODERN"
               else f"{era} (to exp{MODERN_FROM-1}, to 2026-05)")
        print(f"  {lab}  —  {len(runs[era])} runs")
        print(f"    entries {c['entries']:>5}    carrying falsifier code {c['fcode']:>5}"
              f" ({c['fcode']/max(c['entries'],1)*100:.1f}%)")
        print(f"    terminal {c['terminal']:>4}    backed by a recorded tool verdict"
              f" {c['backed']:>5} ({c['backed']/max(c['terminal'],1)*100:.1f}%)")
        for (ee, st), v in sorted(st_cov.items(), key=lambda kv: -kv[1]["n"]):
            if ee != era: continue
            print(f"      {st:<12}{v['n']:>5}{v['b']:>7}{v['b']/v['n']*100:>7.1f}%")
        print()

    # ---- M5: does status track the tool verdict? ------------------------------
    table = collections.Counter()
    for _nm, era, _cid, e in rows:
        if era != "MODERN": continue
        fv = (e.get("falsifier_verdict") or "").strip().upper()
        if fv: table[(fv, (e.get("status") or "").upper())] += 1
    fvs = sorted({a for a, _ in table}); sts = sorted({b for _, b in table})
    print("M5  MODERN ARC — tool verdict (rows) x recorded status (columns)\n")
    print(f"  {'tool verdict':<20}" + "".join(f"{s:>13}" for s in sts) + f"{'total':>8}")
    for a in fvs:
        print(f"  {a:<20}" + "".join(f"{table[(a,s)]:>13}" for s in sts)
              + f"{sum(table[(a,s)] for s in sts):>8}")
    cc = sum(table[("CONFIRMED", s)] for s in ("CLOSED", "CONFIRMED"))
    ct = sum(table[("CONFIRMED", s)] for s in sts)
    rr, rt = table[("REFUTED", "REFUTED")], sum(table[("REFUTED", s)] for s in sts)
    print(f"\n  tool CONFIRMED -> CLOSED or CONFIRMED : {cc}/{ct} ({cc/max(ct,1)*100:.1f}%)")
    print(f"  tool REFUTED   -> REFUTED             : {rr}/{rt} ({rr/max(rt,1)*100:.1f}%)\n")

    # ---- M6: who wins when they disagree? -------------------------------------
    res = collections.Counter(); detail = []; cells = collections.Counter()
    for nm, era, cid, e in rows:
        if era != "MODERN": continue
        fv = (e.get("falsifier_verdict") or "").strip().upper()
        vs = [(v.get("verdict") or "").upper()
              for v in (e.get("verdicts") or []) if isinstance(v, dict)]
        cells[(bool(fv), bool(vs))] += 1
        st = (e.get("status") or "").upper()
        if fv not in TOOL_WANTS or not vs: continue
        maj = collections.Counter(vs).most_common(1)[0][0]
        if maj not in VOTE_WANTS: continue
        tw, vw = TOOL_WANTS[fv], VOTE_WANTS[maj]
        if tw == vw:
            res["agree"] += 1; continue
        res["disagree"] += 1
        who = ("TOOL" if st in tw and st not in vw else
               "VOTE" if st in vw and st not in tw else "neither")
        res[who] += 1
        detail.append((nm[:34], cid, fv, maj, st, who))

    d = max(res["disagree"], 1)
    print("M6  MODERN ARC — when the tool verdict and the model majority DISAGREE\n")
    print(f"    entries carrying both        {res['agree']+res['disagree']:>5}")
    print(f"    they agree                   {res['agree']:>5}")
    print(f"    they disagree                {res['disagree']:>5}")
    print(f"      the TOOL prevails          {res['TOOL']:>5}  ({res['TOOL']/d*100:.1f}%)")
    print(f"      the model MAJORITY prevails{res['VOTE']:>5}  ({res['VOTE']/d*100:.1f}%)")
    print(f"      neither                    {res['neither']:>5}")
    print("\n    THERE IS NO P-VALUE HERE, AND THERE MUST NOT BE (CC2, 2026-08-22).")
    print("    apply_falsifier_verdicts overwrites the status from the tool verdict")
    print("    UNCONDITIONALLY whenever the gate is on. With the gate on, 'the tool")
    print("    prevails' is DETERMINISTIC. A sign test against a vote-decided null")
    print("    tests a hypothesis the source code already assigns probability zero.")
    print("    An earlier draft reported p = 2.98e-08 and it was arithmetic on a")
    print("    foregone conclusion. What this table legitimately establishes is a")
    print("    REGRESSION CHECK: the gate was enabled and nothing bypassed it across")
    print("    every run. That is worth having -- six model-vote paths to MERGED were")
    print("    found in this codebase on 2026-08-19 -- but it is a bug check, not a")
    print("    significance test.")
    # A strict partition: a case is counted once. Tool-failure first, because when
    # the tool did not run there is no truth verdict for a vote to contradict.
    failed = [r for r in detail if r[2] in ("ERROR", "UNTOOLABLE")]
    rest   = [r for r in detail if r not in failed]
    house  = [r for r in rest if r[3] in ("MERGE", "REOPEN", "EXTEND")]
    truth  = [r for r in rest if r not in house]
    assert len(failed) + len(house) + len(truth) == len(detail)
    print("\n    DECOMPOSITION (CC2, 2026-08-22) -- these are not 26 equivalent contests:")
    print(f"      {len(failed):>3}  the tool FAILED (ERROR/UNTOOLABLE) and the runner withheld.")
    print( "           Supports: model agreement is not SUFFICIENT. Sound, and it is the")
    print( "           assumption-free restatement below.")
    print(f"      {len(house):>3}  MERGE / REOPEN / EXTEND majorities against a CONFIRMED tool.")
    print( "           MERGE means 'duplicate of C00xx' -- a HOUSEKEEPING vote, not a truth")
    print( "           vote. Counting these as 'the model wanted a different truth' is a")
    print( "           construction and is NOT defensible. They are excluded.")
    print(f"      {len(truth):>3}  a model majority making a TRUTH claim against a tool truth verdict.")
    for r in truth:
        print(f"           {r[0]}  {r[1]}  tool={r[2]} majority={r[3]} -> {r[4]}")
    print( "      So 'the tool overrules the panel ON TRUTH' rests on the last line alone.")
    print( "      'Votes are not sufficient' rests on the first and holds.")
    print("\n    KNOWN WEAKNESSES OF THIS MEASUREMENT, stated here so no reader has to find them:")
    byrun = collections.Counter(r[0] for r in detail)
    if byrun:
        top, n = byrun.most_common(1)[0]
        print(f"      * the disagreements CLUSTER: {n} of {res['disagree']} come from "
              f"{top}. Entries are not independent.")
    print("      * VOTE_WANTS is a reading of vote labels, not a recorded intent.")
    print("      * this covers only entries carrying BOTH a tool verdict and votes:")
    for (hasfv, hasv), n in sorted(cells.items(), key=lambda kv: -kv[1]):
        print(f"          tool {'YES' if hasfv else 'no '} | votes "
              f"{'YES' if hasv else 'no '}   {n:>5}")
    print("      * it cannot speak to entries with NO tool verdict; those are M3's residual.")
    print("      * status-vs-verdict is not causation. What makes it more than correlation")
    print("        is the ORDER IN THE CODE: reference_runner_v3 calls")
    print("        _update_finding_statuses (votes) and THEN apply_falsifier_verdicts,")
    print("        whose docstring reads 'Called AFTER _update_finding_statuses so the")
    print("        falsifier verdict wins'. The vote writes first and is overridden.\n")
    if detail:
        print(f"  {'run':<36}{'id':<8}{'tool':<12}{'majority':<11}{'status':<13}{'winner'}")
        for r in sorted(detail, key=lambda r: (r[5], r[0])):
            print(f"  {r[0]:<36}{r[1]:<8}{r[2]:<12}{r[3]:<11}{r[4]:<13}{r[5]}")

    # ---- M7: falsifiers that did not run but wrote a terminal status ----------
    bad, denom = [], 0
    for nm, era, cid, e in rows:
        if era != "MODERN": continue
        fv = (e.get("falsifier_verdict") or "").strip().upper()
        st = (e.get("status") or "").upper()
        if fv in {"ERROR", "UNTOOLABLE"}:
            denom += 1
            if st in {"CLOSED", "CONFIRMED", "REFUTED", "MERGED"}:
                bad.append((nm[:38], cid, fv, st, e.get("severity"), e.get("verified")))
    print(f"\nM7  falsifiers that did NOT run but wrote a TERMINAL status: "
          f"{len(bad)} of {denom}\n")
    print(f"  {'run':<40}{'id':<8}{'tool':<12}{'status':<11}{'sev':<7}{'verified'}")
    for r in bad:
        print(f"  {r[0]:<40}{r[1]:<8}{r[2]:<12}{r[3]:<11}{str(r[4]):<7}{r[5]}")
    print("\n  A `verified=True` case has an independent fix-verification behind it and is")
    print("  defensible. A `verified=False` case wrote a terminal verdict the falsifier")
    print("  cannot support. NOTE (CC2, 2026-08-22): all four carry escalated=True, so a")
    print("  human saw them at the moment they were mislabelled. The status is still")
    print("  wrong; 'killed on no evidence' overstates it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
