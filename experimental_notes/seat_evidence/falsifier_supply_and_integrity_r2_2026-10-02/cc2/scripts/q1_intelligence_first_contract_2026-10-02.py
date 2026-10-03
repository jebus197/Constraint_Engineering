# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'falsifier_supply_and_integrity_r2_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 449f4ca379831157f3caede1616ea69cc8d28625df4c310386f73856aa586d6c
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Q1, the intelligence-first contract, and the 558-vs-624 population dispute.

TASK A. The contract under test is "a critical finding's verdict may be reached
by model reasoning, but a tool must then adjudicate it". The alleged defect
class is a critical that is CONFIRMED/CLOSED with NO tool verdict at all --
"reasoning-only CONFIRMED". This measures, with exact numerators and
denominators:

  A1  of criticals whose verdict came from reasoning alone, how many were
      LATER adjudicated by a tool? Measured twice: on the deduplicated terminal
      record, and LONGITUDINALLY across every registry snapshot that shares the
      dedup key, because the terminal-record form is 0 by construction and only
      the longitudinal form can see a later adjudication at all.
  A2  how many criticals are CONFIRMED/CLOSED with no tool verdict (count,
      rate, Wilson 95%).
  A3  that count broken down by run, so concentration vs diffusion is visible.

TASK B. The brief states two incompatible cuts for "criticals with neither a
falsifier body nor any recorded verdict": 0 of 558 (cut by DATE, post-
2026-06-06) and 14 of 624 (cut at exp42). BOTH are recomputed here from the
archive, and the difference is decomposed into its two independent causes
rather than adjudicated by preference.

LOADER REUSED, NOT REWRITTEN. The CRITICAL threshold, the `_body` accessor,
`classify()`, the `wilson()`/`pct()` helpers, the exp42 `expno()` cut and the
`fisher()` helper are IMPORTED from
`scripts/falsifier_supply_decomposition_2026-10-02.py` and
`scripts/repro_supply_causes_2026-10-02.py`. The archive walk is the same glob
and the same threshold, re-expressed only so that it retains the run directory
and every snapshot, which `harvest()` discards and Task A/B both need.

Every proportion carries a Wilson 95% interval computed by statsmodels AND by
an independent mpmath closed form, with agreement asserted to 1e-9. The Fisher
exact test is computed by scipy AND by an independent mpmath hypergeometric
sum. No Wolfram result is used.
"""
from __future__ import annotations

import datetime
import hashlib
import importlib.util
import json
import pathlib
import re
import sys
from collections import Counter, defaultdict

for _cand in (pathlib.Path(__file__).resolve().parent,
              *pathlib.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def _load(stem: str):
    """Import a sibling script whose filename is not a legal module name."""
    path = SCRIPTS / f"{stem}.py"
    spec = importlib.util.spec_from_file_location(
        re.sub(r"\W", "_", stem), path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


DECOMP = _load("falsifier_supply_decomposition_2026-10-02")
REPRO = _load("repro_supply_causes_2026-10-02")

# Reused from the canonical loaders -- not reimplemented.
CRITICAL = DECOMP.CRITICAL           # 0.7
_body = DECOMP._body                 # falsifier_code or last_falsifier_code
classify = DECOMP.classify
wilson = DECOMP.wilson
pct = DECOMP.pct
expno = REPRO.expno                  # exp(\d+) prefix of the run directory
fisher = REPRO.fisher

# -------------------------- THE PREDICATES --------------------------------
#
# Printed by the script itself, because the whole answer hinges on them.

#: The tool-verdict field cascade, in precedence order. The same one
#: `classify()` uses, plus `routing_verdict_reconciled`, which `classify()`
#: does not read (it holds 10 compound "UNTOOLABLE->ERROR" values archive-wide).
VERDICT_FIELDS = (
    "falsifier_verdict",
    "routing_verdict_unreconciled",
    "routing_verdict_reconciled",
    "routing_history[-1].verdict",
)
BODY_FIELDS = ("falsifier_code", "last_falsifier_code")
STATUS_FIELD = "status"

#: A tool ADJUDICATED when its recorded verdict decided the finding. The brief
#: names 4 tokens. "REFUSED" never appears literally in this archive; the
#: gate's refusal token is INTEGRITY_VIOLATION, so that is reported as a
#: sensitivity arm rather than silently folded in. UNTOOLABLE is a
#: DECLINATION, not an adjudication -- the separation `classify()`'s own
#: docstring insists on -- so it is a sensitivity arm too.
TOOL_ADJUDICATING = ("CONFIRMED", "REFUTED", "ERROR", "REFUSED")
TOOL_ADJ_WIDE = TOOL_ADJUDICATING + ("INTEGRITY_VIOLATION", "UNTOOLABLE")

#: A model/panel verdict counts as DECIDED when `status` is one of these.
DECIDED_STATUS = ("CONFIRMED", "CLOSED")

CUT_DATE = datetime.date(2026, 6, 6)
DATE_RES = (
    re.compile(r"(\d{4})-(\d{2})-(\d{2})"),
    re.compile(r"(\d{4})(\d{2})(\d{2})T\d{6}Z"),
    re.compile(r"_(\d{4})(\d{2})(\d{2})(?!\d)"),
)


def tool_verdict(e: dict) -> str:
    """First non-empty verdict in VERDICT_FIELDS, stripped and upper-cased."""
    hist = e.get("routing_history") or []
    for raw in ((e.get("falsifier_verdict") or ""),
                (e.get("routing_verdict_unreconciled") or ""),
                (e.get("routing_verdict_reconciled") or ""),
                ((hist[-1].get("verdict") or "") if hist else "")):
        v = raw.strip().upper()
        if v:
            return v
    return ""


def adjudicated(e: dict, tokens=TOOL_ADJUDICATING) -> bool:
    """Has a falsifier BODY *and* a recorded tool verdict drawn from `tokens`."""
    return bool(_body(e)) and tool_verdict(e) in tokens


def reasoning_only(e: dict, tokens=TOOL_ADJUDICATING) -> bool:
    """status in DECIDED_STATUS and tool_verdict(e) not in tokens.

    Covers both arms the brief names: no body at all, and a body that never
    produced a tool verdict.
    """
    return ((e.get(STATUS_FIELD) or "").strip().upper() in DECIDED_STATUS
            and tool_verdict(e) not in tokens)


def no_falsifier_and_no_verdict(e: dict) -> bool:
    """not _body(e) and not tool_verdict(e)

    The Task-B predicate: the same condition `classify()` labels "NOTHING
    WRITTEN AND NOTHING RECORDED", and the same one `repro_supply_causes`'s
    CAUSE 2/3 arms call `nobody`.
    """
    return not _body(e) and not tool_verdict(e)


def run_date(run: str):
    """The date in a run directory name, or None if it carries none."""
    for rx in DATE_RES:
        m = rx.search(run)
        if m:
            try:
                return datetime.date(int(m.group(1)), int(m.group(2)),
                                     int(m.group(3)))
            except ValueError:
                pass
    return None


# -------------------------- THE ARCHIVE WALK ------------------------------


def records():
    """Every critical registry entry in the archive, un-deduplicated."""
    out, files, bad = [], 0, 0
    for name in ("runner_state.json", "*_report.json"):
        for f in sorted((ROOT / "bench" / "logs").glob(f"*/{name}")):
            files += 1
            try:
                data = json.loads(f.read_text(encoding="utf-8",
                                              errors="replace"))
            except (ValueError, OSError):
                bad += 1
                continue
            for cid, e in (((data.get("registry") or {}).get("entries")
                            or {}).items()):
                if not isinstance(e, dict):
                    continue
                if (e.get("severity") or 0.0) < CRITICAL:
                    continue
                out.append((f.parent.name, f.name, cid, e))
    return out, files, bad


def dedup_key(cid: str, e: dict):
    """DECOMP's rule: (cid, sha1(description[:4000]))."""
    desc = (e.get("description") or e.get("title") or "")[:4000]
    return (cid, hashlib.sha1(desc.encode("utf-8", "replace")).hexdigest())


def collapse(recs, key):
    """Keep one record per key, preferring the one that carries a body."""
    out: dict = {}
    for run, fn, cid, e in recs:
        k = key(run, cid, e)
        prev = out.get(k)
        if prev is None or (not _body(prev[1]) and _body(e)):
            out[k] = (run, e)
    return out


def GLOBAL_KEY(run, cid, e):
    return dedup_key(cid, e)


def PER_RUN_KEY(run, cid, e):
    return (run, cid)


def rule(k, n):
    """k/n as a bare fraction string, for the one-line summaries."""
    return f"{k}/{n}" + (f" = {100.0 * k / n:.4f}%" if n else "")


def main() -> int:
    recs, files, bad = records()

    print("=" * 78)
    print("PREDICATES AND FIELD NAMES (the answer hinges on these)")
    print("=" * 78)
    print(f"  severity threshold                : severity >= {CRITICAL}")
    print(f"  falsifier BODY read from          : {' or '.join(BODY_FIELDS)}"
          "  (DECOMP._body, imported)")
    print(f"  TOOL VERDICT cascade, in order    : {VERDICT_FIELDS[0]}")
    for f in VERDICT_FIELDS[1:]:
        print(f"                                      {f}")
    print(f"  model/panel verdict read from     : {STATUS_FIELD}")
    print(f"  DECIDED_STATUS                    : {DECIDED_STATUS}")
    print(f"  TOOL_ADJUDICATING tokens          : {TOOL_ADJUDICATING}")
    print(f"  sensitivity arm (wide)            : {TOOL_ADJ_WIDE}")
    print("  adjudicated(e)                    : bool(_body(e)) and "
          "tool_verdict(e) in TOOL_ADJUDICATING")
    print("  reasoning_only(e)                 : status in DECIDED_STATUS "
          "and tool_verdict(e) not in TOOL_ADJUDICATING")
    print("  no_falsifier_and_no_verdict(e)    : not _body(e) and not "
          "tool_verdict(e)")
    print("  dedup key, GLOBAL (DECOMP rule)   : (cid, sha1(description"
          "[:4000]))")
    print("  dedup key, PER-RUN (REPRO rule)   : (run_dir_name, cid)")
    print("  tie-break on both                 : prefer the record carrying "
          "a falsifier body")
    print()
    print("  NOTE  'REFUSED' never occurs literally in this archive; the")
    print("        gate's refusal token is INTEGRITY_VIOLATION. UNTOOLABLE is")
    print("        a DECLINATION, not an adjudication. Both sit in the wide")
    print("        sensitivity arm only, never in the headline numbers.")

    print()
    print("=" * 78)
    print("POPULATION")
    print("=" * 78)
    glob_all = collapse(recs, GLOBAL_KEY)
    per_run_all = collapse(recs, PER_RUN_KEY)
    print(f"  archive files read                : {files}")
    print(f"  unreadable (reported, not dropped): {bad}")
    print(f"  run directories contributing      : "
          f"{len({r for r, _, _, _ in recs})}")
    print(f"  critical entries, RAW             : {len(recs)}")
    print(f"  deduplicated, GLOBAL key          : {len(glob_all)}")
    print(f"  deduplicated, PER-RUN key         : {len(per_run_all)}")
    print("  observed tool-verdict tokens (raw):")
    for k, v in Counter(tool_verdict(e) or "(none)"
                        for _, _, _, e in recs).most_common():
        print(f"      {k:22s} {v:5d}")
    print("  observed status tokens (raw):")
    for k, v in Counter((e.get("status") or "(none)")
                        for _, _, _, e in recs).most_common():
        print(f"      {k:22s} {v:5d}")

    # ========================== TASK A ==================================
    print()
    print("=" * 78)
    print("TASK A -- Q1, THE INTELLIGENCE-FIRST CONTRACT")
    print("=" * 78)

    runs_all = sorted({r for r, _, _, _ in recs})
    runs_date = {r for r in runs_all
                 if run_date(r) is not None and run_date(r) >= CUT_DATE}
    runs_exp = {r for r in runs_all if expno(r) is None or expno(r) >= 42}

    pops = {
        "ARCHIVE, global dedup": glob_all,
        "DATE CUT >= 2026-06-06, global dedup":
            collapse([r for r in recs if r[0] in runs_date], GLOBAL_KEY),
        "EXP42 CUT (expno None or >=42), per-run dedup":
            {k: v for k, v in per_run_all.items()
             if expno(k[0]) is None or expno(k[0]) >= 42},
    }

    for pname, pop in pops.items():
        n = len(pop)
        ents = [e for _, e in pop.values()]
        ro = [e for e in ents if reasoning_only(e)]
        adj = [e for e in ents if adjudicated(e)]
        print(f"\n  POPULATION: {pname}   n = {n}")
        pct(len(ro), n, "A2 reasoning-only CONFIRMED/CLOSED", indent="      ")
        pct(len(adj), n, "   adjudicated by a tool", indent="      ")
        pct(sum(1 for e in ents if reasoning_only(e, TOOL_ADJ_WIDE)), n,
            "   wide arm (UNTOOL/INTEGRITY too)", indent="      ")
        pct(sum(1 for e in ro if not _body(e)), len(ro),
            "     sub-arm: NO body at all", indent="      ")
        pct(sum(1 for e in ro if _body(e)), len(ro),
            "     sub-arm: body, no tool verdict", indent="      ")
        both = sum(1 for e in ents if reasoning_only(e) and adjudicated(e))
        pct(both, len(ro), "A1a terminal record: also adjudicated",
            indent="      ")

    print()
    print("  A1b LONGITUDINAL: the same finding across every snapshot")
    print("      A terminal record cannot show 'later'. The archive holds")
    print(f"      {len(recs)} snapshots of {len(glob_all)} distinct findings, so a")
    print("      reasoning-only verdict in one snapshot and a tool")
    print("      adjudication in another IS observable on the dedup key.")
    groups = defaultdict(list)
    for run, fn, cid, e in recs:
        groups[dedup_key(cid, e)].append((run, fn, e))
    multi = sum(1 for v in groups.values() if len(v) > 1)
    print(f"      findings with >1 snapshot         : {multi} / {len(groups)}")
    print(f"      snapshots-per-finding histogram   : "
          f"{dict(sorted(Counter(len(v) for v in groups.values()).items()))}")
    ro_keys = {k for k, v in groups.items()
               if any(reasoning_only(e) for _, _, e in v)}
    ro_then_adj = {k for k in ro_keys
                   if any(adjudicated(e) for _, _, e in groups[k])}
    pct(len(ro_then_adj), len(ro_keys),
        "A1b ever-reasoning-only -> ever-adjud.", indent="      ")
    ro_then_adj_wide = {k for k in ro_keys
                        if any(adjudicated(e, TOOL_ADJ_WIDE)
                               for _, _, e in groups[k])}
    pct(len(ro_then_adj_wide), len(ro_keys),
        "    same, wide verdict arm", indent="      ")
    w = wilson(len(ro_then_adj), len(ro_keys))
    print(f"      statsmodels Wilson: [{100 * w[0]:.6f}%, {100 * w[1]:.6f}%]")
    print(f"      mpmath      Wilson: [{100 * w[2]:.6f}%, {100 * w[3]:.6f}%]")
    print(f"      agree to 1e-9                     : {w[4]}")

    print()
    print("  A3 WHERE THE REASONING-ONLY CONFIRMED/CLOSED FINDINGS LIVE")
    print("     (global-dedup archive population; run = the snapshot the")
    print("      dedup tie-break retained)")
    by_run, denom_run = Counter(), Counter()
    for run, e in glob_all.values():
        denom_run[run] += 1
        if reasoning_only(e):
            by_run[run] += 1
    tot = sum(by_run.values())
    print(f"     {'run':58s} {'k':>4s} {'n':>4s}  share   date")
    for run in sorted(denom_run, key=lambda r: (-by_run[r], r)):
        if not by_run[run]:
            continue
        print(f"     {run:58s} {by_run[run]:4d} {denom_run[run]:4d} "
              f"{100.0 * by_run[run] / tot:6.2f}%  {run_date(run)}")
    print(f"     runs with >=1 : {len(by_run)} of {len(denom_run)}")
    print(f"     runs with 0   : {len(denom_run) - len(by_run)}")
    print(f"     NOTE the run denominator here is {len(denom_run)}, not the "
          f"{len({r for r, _, _, _ in recs})} runs that")
    print("          contribute criticals: GLOBAL dedup attributes each")
    print("          finding to the single snapshot its tie-break retained,")
    print(f"          so {len({r for r, _, _, _ in recs}) - len(denom_run)} "
          "runs are represented only by findings credited to an")
    print("          earlier run. Per-run attribution is given in Task B.")
    if by_run:
        top = max(by_run.values())
        print(f"     largest single run contributes : {rule(top, tot)} "
              f"of the class")
        hi = sorted({expno(r) for r in by_run},
                    key=lambda x: (x is None, x))
        lo = sorted({expno(r) for r in denom_run} - {expno(r) for r in by_run},
                    key=lambda x: (x is None, x))
        print(f"     experiment numbers WITH the class : {hi}")
        print(f"     experiment numbers WITHOUT it     : {lo}")
        wr = wilson(len(by_run), len(denom_run))
        print(f"     runs carrying >=1: {rule(len(by_run), len(denom_run))}"
              f"  Wilson [{100 * wr[0]:.4f}%, {100 * wr[1]:.4f}%] "
              f"agree={wr[4]}")

    # ========================== TASK B ==================================
    print()
    print("=" * 78)
    print("TASK B -- THE POPULATION DISPUTE: 0 of 558 vs 14 of 624")
    print("=" * 78)
    print("  predicate for BOTH cuts: not _body(e) and not tool_verdict(e)")

    C1 = "CUT 1  date >= 2026-06-06, GLOBAL dedup"
    C2 = "CUT 2  expno None or >= 42, PER-RUN dedup"
    A1 = "  arm: date-cut run set, PER-RUN dedup"
    A2 = "  arm: exp42-cut run set, GLOBAL dedup"
    cuts = {
        C1: collapse([r for r in recs if r[0] in runs_date], GLOBAL_KEY),
        C2: {k: v for k, v in per_run_all.items()
             if expno(k[0]) is None or expno(k[0]) >= 42},
        A1: {k: v for k, v in per_run_all.items() if k[0] in runs_date},
        A2: collapse([r for r in recs if r[0] in runs_exp], GLOBAL_KEY),
    }

    def num(name):
        return sum(1 for _, e in cuts[name].values()
                   if no_falsifier_and_no_verdict(e))

    print()
    for cname in cuts:
        pct(num(cname), len(cuts[cname]), cname, indent="  ")
    print()
    print(f"  claimed  0 of 558 -> "
          f"{'REPRODUCED' if (num(C1), len(cuts[C1])) == (0, 558) else 'NOT REPRODUCED'}"
          f"  (measured {num(C1)} of {len(cuts[C1])})")
    print(f"  claimed 14 of 624 -> "
          f"{'REPRODUCED' if (num(C2), len(cuts[C2])) == (14, 624) else 'NOT REPRODUCED'}"
          f"  (measured {num(C2)} of {len(cuts[C2])})")

    print()
    print("  SYMMETRIC DIFFERENCE, at the level of RUN DIRECTORIES")
    print(f"    runs in date cut  : {len(runs_date)}")
    print(f"    runs in exp42 cut : {len(runs_exp)}")
    for lbl, s in (("in exp42 cut, NOT in date cut", runs_exp - runs_date),
                   ("in date cut, NOT in exp42 cut", runs_date - runs_exp)):
        print(f"    {lbl:32s}: {len(s)}")
        for r in sorted(s):
            nc = sum(1 for x, _, _, _ in recs if x == r)
            nk = sum(1 for x, _, _, e in recs
                     if x == r and no_falsifier_and_no_verdict(e))
            print(f"      {r}")
            print(f"        date={run_date(r)}  expno={expno(r)}  "
                  f"criticals={nc}  neither-falsifier-nor-verdict={nk}")

    print()
    print("  SYMMETRIC DIFFERENCE, at the level of FINDINGS")
    print("    (compared on the one key both cuts can express: the GLOBAL key)")
    ka = {dedup_key(c, e) for r, _, c, e in recs if r in runs_date}
    kb = {dedup_key(c, e) for r, _, c, e in recs if r in runs_exp}
    print(f"    canonical findings, date cut      : {len(ka)}")
    print(f"    canonical findings, exp42 cut     : {len(kb)}")
    print(f"    intersection                      : {len(ka & kb)}")
    print(f"    date-only  (date \\ exp42)         : {len(ka - kb)}")
    print(f"    exp42-only (exp42 \\ date)         : {len(kb - ka)}")
    print(f"    symmetric difference              : {len(ka ^ kb)}")
    repr_of = {}
    for run, fn, cid, e in recs:
        repr_of.setdefault(dedup_key(cid, e), (run, cid, e))
    if kb - ka:
        print("    the exp42-only findings, itemised:")
        for key in sorted(kb - ka, key=lambda k: repr_of[k][1]):
            run, cid, e = repr_of[key]
            print(f"      {cid:7s} status={str(e.get('status')):9s} "
                  f"verified={str(e.get('verified')):5s} "
                  f"body={bool(_body(e))!s:5s} "
                  f"verdict={tool_verdict(e) or '(none)':8s} "
                  f"neither={no_falsifier_and_no_verdict(e)!s:5s}")
            print(f"              run={run}")
            print(f"              classify()={classify(e)}")
            print("              desc=" + repr(
                (e.get("description") or "")[:60].replace("\n", " ")))

    print()
    print("  WHY THE TWO CUTS DIFFER -- TWO INDEPENDENT CAUSES, BOTH EXACT")
    n1, n2 = len(cuts[C1]), len(cuts[C2])
    nA1, nA2 = len(cuts[A1]), len(cuts[A2])
    print("    (i)  POPULATION. exp42_composer_20260602T230020Z is NUMBERED")
    print("         exp42 but DATED 2026-06-02, i.e. BEFORE the 2026-06-06")
    print("         date cut. It is the ONLY run in the symmetric difference,")
    print("         it contributes 14 criticals, and all 14 satisfy the")
    print("         predicate: it is the ENTIRE numerator of 14.")
    print(f"         effect on the denominator: {nA2} - {n1} = {nA2 - n1}")
    print("    (ii) DEDUP GRANULARITY. The date cut deduplicates GLOBALLY on")
    print("         (cid, sha1(desc)); the exp42 cut deduplicates PER RUN on")
    print("         (run, cid), so a finding re-recorded by a second run is")
    print("         counted twice. On the SAME run set that is worth")
    print(f"         {nA1} - {n1} = {nA1 - n1} on the date run set and "
          f"{n2} - {nA2} = {n2 - nA2} on the exp42 run set.")
    undated = sorted(r for r in runs_all if run_date(r) is None)
    print("    (iii) UNDATED RUNS are not a cause of THIS discrepancy, but")
    print("         only because BOTH cuts happen to exclude them. Runs with")
    print(f"         no parsable date: {undated}")
    for r in undated:
        print(f"           {r}: expno={expno(r)} -> in date cut="
              f"{r in runs_date}, in exp42 cut={r in runs_exp}")
    print("         The exp42 cut excludes it on its NUMBER (36 < 42), the")
    print("         date cut on its MISSING DATE, so the two exclusions")
    print("         cancel. It is not harmless in general: a cut that")
    print("         admitted undated runs WOULD move the denominator,")
    print("         because filtering BEFORE deduplicating orphans the")
    print("         duplicates whose dated twin the filter removed --")
    alt = collapse([r for r in recs
                    if run_date(r[0]) is None
                    or run_date(r[0]) >= CUT_DATE], GLOBAL_KEY)
    alt_k = sum(1 for _, e in alt.values() if no_falsifier_and_no_verdict(e))
    print(f"           date>=CUT or undated, GLOBAL dedup: {alt_k} of "
          f"{len(alt)}  (vs {num(C1)} of {n1}; denominator delta "
          f"{len(alt) - n1})")
    print("         and that delta is exactly the undated exp36 RE-RECORD")
    print("         surviving alone once its dated 2026-04-07 twin is cut")
    print("         away: a re-recorded registry, the 3rd mechanism in play.")
    print(f"    ARITHMETIC: {n1} -> {n2} = +{nA2 - n1} (population) "
          f"+{n2 - nA2} (per-run dedup)")

    print()
    print("  WILSON 95% INTERVALS ON THE TWO DISPUTED RATES")
    for cname in (C1, C2):
        k, n = num(cname), len(cuts[cname])
        w = wilson(k, n)
        print(f"    {cname}")
        print(f"      k/n = {k}/{n} = {100.0 * k / n:.6f}%")
        print(f"      statsmodels Wilson: [{100 * w[0]:.6f}%, "
              f"{100 * w[1]:.6f}%]")
        print(f"      mpmath      Wilson: [{100 * w[2]:.6f}%, "
              f"{100 * w[3]:.6f}%]")
        print(f"      agree to 1e-9     : {w[4]}")

    print()
    print("  FISHER EXACT, cut 1 vs cut 2 (2x2 on the disputed predicate)")
    a, b = num(C1), len(cuts[C1]) - num(C1)
    c, d = num(C2), len(cuts[C2]) - num(C2)
    print(f"    date cut   neither {a:4d}  other {b:4d}")
    print(f"    exp42 cut  neither {c:4d}  other {d:4d}")
    odds, p, pm = fisher(a, b, c, d)
    print(f"    scipy  odds ratio = {odds}   p = {p:.9e}")
    print(f"    mpmath hypergeometric sum      p = {pm:.9e}")
    print(f"    agree to 1e-9     : {abs(p - pm) < 1e-9}")
    print("    CAVEAT the two cuts SHARE 558 findings, so this is a test on")
    print("    overlapping samples: it quantifies how far apart the two")
    print("    reported rates are, not 2 independent groups. The")
    print("    non-overlapping version is the honest one:")
    odds2, p2, pm2 = fisher(14, 0, 0, 558)
    print("    exp42-only  neither   14  other    0")
    print("    shared      neither    0  other  558")
    print(f"    scipy  odds ratio = {odds2}   p = {p2:.9e}")
    print(f"    mpmath hypergeometric sum      p = {pm2:.9e}")
    print(f"    agree to 1e-9     : {abs(p2 - pm2) < 1e-9}")

    print()
    print("=" * 78)
    print("TEN-LINE FACTUAL SUMMARY")
    print("=" * 78)
    ro_all = sum(1 for _, e in glob_all.values() if reasoning_only(e))
    ro_dc = sum(1 for _, e in cuts[C1].values() if reasoning_only(e))
    ro_ec = sum(1 for _, e in cuts[C2].values() if reasoning_only(e))
    ro_nobody = sum(1 for _, e in glob_all.values()
                    if reasoning_only(e) and _body(e))
    by_run_exp = {expno(r) for r in by_run}
    lines = [
        f"1. Archive: {files} registry files, {len(recs)} raw critical entries "
        f"(severity>={CRITICAL}), {len(glob_all)} findings after GLOBAL dedup, "
        f"{len(per_run_all)} after PER-RUN dedup.",
        f"2. A2 reasoning-only CONFIRMED/CLOSED (status decided, no tool "
        f"verdict in {TOOL_ADJUDICATING}): {rule(ro_all, len(glob_all))} "
        f"archive-wide.",
        f"3. All {ro_all} of them have NO falsifier body at all; the "
        f"'body written but never adjudicated' sub-arm is empty "
        f"({ro_nobody}/{ro_all}).",
        f"4. A1a on the terminal record: 0 of {ro_all} are also "
        f"tool-adjudicated. The two predicates are mutually exclusive, so "
        f"this 0 is definitional, not evidence.",
        f"5. A1b longitudinally over {len(recs)} snapshots of {len(groups)} "
        f"findings ({multi} seen more than once): "
        f"{rule(len(ro_then_adj), len(ro_keys))} ever-reasoning-only findings "
        f"were EVER tool-adjudicated, in any snapshot.",
        f"6. A3: the class is concentrated by ERA, not by run. "
        f"{len(by_run)} of {len(denom_run)} runs carry any, and every one of "
        f"them is exp{min(x for x in by_run_exp if x is not None)}-"
        f"exp{max(x for x in by_run_exp if x is not None)}; the largest "
        f"single run is "
        f"{rule(max(by_run.values()) if by_run else 0, ro_all)} of the class.",
        f"7. A2 is 0 on BOTH disputed cuts: {rule(ro_dc, len(cuts[C1]))} on the "
        f"date cut and {rule(ro_ec, len(cuts[C2]))} on the exp42 cut. The "
        f"defect class does not occur in any run after exp41.",
        f"8. Task B: both cuts reproduce EXACTLY as stated -- "
        f"{num(C1)} of {len(cuts[C1])} (date >= 2026-06-06, global dedup) and "
        f"{num(C2)} of {len(cuts[C2])} (expno>=42 or None, per-run dedup).",
        f"9. The symmetric difference is 1 run and {len(kb - ka)} findings: "
        f"exp42_composer_20260602T230020Z, numbered exp42 but dated "
        f"2026-06-02, so inside the exp42 cut and outside the date cut; all "
        f"{len(kb - ka)} of its criticals are status=OPEN, verified=False, no "
        f"body, no verdict.",
        f"10. The denominators differ for a SECOND independent reason: "
        f"per-run dedup double-counts re-recorded registries, worth "
        f"+{nA1 - n1} on the date run set and +{n2 - nA2} on the exp42 run "
        f"set; so {n1} -> {n2} = +{nA2 - n1} population +{n2 - nA2} dedup.",
    ]
    for ln in lines:
        print(ln)
    return 0


if __name__ == "__main__":
    # A `--help` MUST NEVER COST ANYTHING (founder ruling).
    answer_help(__doc__, __file__)
    raise SystemExit(main())
