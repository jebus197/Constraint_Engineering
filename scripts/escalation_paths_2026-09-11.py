#!/usr/bin/env python3
"""Task A7: every archived critical escalated with no falsifier, by WHICH path.

THE ENTRY SAID 25, ACROSS 9 RUNS, WITH `exp53_control_zero_live` ACCOUNTING FOR
10. Neither figure reproduces, and finding that out took longer than fixing it.

  No predicate I could construct returns 25. The closest is severity >=
  CRITICAL_SEVERITY_THRESHOLD (0.7, read from the runner, not typed) AND
  `hil_escalated` AND no `falsifier_code`, which returns 22 -- and that predicate
  reproduces the entry's OTHER family figure exactly, `exp55_v3_control` = 8.

  "ALMOST CERTAINLY THE ONE THAT WAS MEANT" WAS TOO STRONG AND IS WITHDRAWN.
  Found 2026-09-11 by the fable seat in panel round 12, which swept 7 candidate
  predicates: dropping the severity filter ALSO reproduces exp55_v3_control = 8,
  with a total of 32; a strict `> 0.7` also gives 8, with 20. So {20, 22, 32}
  all pass the single anchor, the entry's unreproduced 25 sits inside that
  range, and ONE family figure cannot identify a predicate. The number 22 is
  quoted with its family from here on.

  WHAT SURVIVES THE WIDENING, and it is the half that mattered: ANONYMOUS is 0
  under EVERY candidate, including the widest set of 32 (12 merge deadlock, 11
  irreducible, 9 stale contested). The conclusion was never at risk; the
  identification was overstated.

  `exp53_control_zero_live` CONTRIBUTES 0 AND CANNOT CONTRIBUTE ANY. Its 2 runs
  hold no `*_report.json` at all: their findings live in `checkpoint.json` under
  `all_findings`, as a list of per-round LISTS, in a DIFFERENT SCHEMA that has
  `falsification_present` where the registry has `falsifier_code` and no
  escalation flag set anywhere. Run 1 holds exactly 10 criticals at >= 0.7, which
  is where the entry's "10" comes from -- they are criticals, they are not
  escalations, and no escalated-with-no-falsifier count can include them.

THE ACTIONABLE HALF, AND IT IS NOT WHAT THE ENTRY EXPECTED. The entry assumed a
gate "let a critical escalate with no runnable check". There is no such hole.
Every one of the 22 is escalated by a NAMED, deliberate mechanism that records
its reason:

    11  irreducible_escalation   the routing ladder ran out (2026-08-01 design)
     8  merge deadlock           a MERGE stalemate for N rounds
     3  stale contested          an unresolved challenge aged past its threshold

WHAT IS ACTUALLY MISSING IS THE INSTRUMENT. `irreducible_queue_count` counts only
the FIRST of those 3 -- correctly, because its docstring scopes it to the ladder
running out -- so an auditor keying on that one flag sees 11 of 22 as
unaccounted. That is what produced "no falsifier" as though it were "no reason".
This script names the path for every one of them, so ANONYMOUS is a set that can
be checked and is presently empty.

THE BACKLOG'S DISPOSITION IS THE FOUNDER'S. Archived runs cannot be retro-fixed.
What this supplies is the decision's factual basis, not the decision.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"


def critical_threshold() -> float:
    """Read from the runner. A threshold typed here is a second rule."""
    src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
    m = re.search(r"^CRITICAL_SEVERITY_THRESHOLD\s*=\s*([\d.]+)", src, re.M)
    assert m, "the runner no longer defines CRITICAL_SEVERITY_THRESHOLD"
    return float(m.group(1))


#: Each named escalation path, and the field or reason-text that identifies it.
#: Order matters only for reporting; an entry may legitimately carry more than 1.
PATHS = (
    ("irreducible_escalation",
     lambda e: bool(e.get("irreducible_escalation")),
     "the routing ladder ran out without any model writing a runnable test"),
    ("merge deadlock",
     lambda e: "MERGE deadlock" in (e.get("hil_reason") or ""),
     "a MERGE stalemate persisted past max_defer rounds"),
    ("stale contested",
     lambda e: "Unresolved challenge" in (e.get("hil_reason") or ""),
     "a challenge went unresolved past its round threshold"),
    ("mechanical fault",
     lambda e: bool(e.get("mechanical_fault")),
     "the falsifier fired against a CORRECTED copy"),
    ("discrimination indeterminate",
     lambda e: bool(e.get("discrimination_indeterminate")),
     "the discrimination control could not decide"),
    ("routing deferred",
     lambda e: bool(e.get("routing_deferred")),
     "routing deferred the item to a later round"),
    # FOUND BY THE COVERAGE CHECK BELOW, not by reading the archive. This path
    # has never fired on a critical with no falsifier, so no census would have
    # shown it; the runner has 6 sites that escalate and the first version of
    # this table recognised 5.
    ("contested too long",
     lambda e: "Contested for" in (e.get("hil_reason") or ""),
     "a finding stayed CONTESTED past its round threshold"),
)

#: The marker each site in the runner must leave behind, so the table above can
#: recognise what the site produced.
_SITE_MARKERS = ("irreducible_escalation", "mechanical_fault",
                 "discrimination_indeterminate", "routing_deferred",
                 "MERGE deadlock", "Unresolved challenge", "Contested for")


def uncovered_escalation_sites() -> list[tuple[int, str]]:
    """Runner sites that set `hil_escalated` and leave nothing recognisable.

    TWO REPRESENTATIONS WITH A COMPARATOR, which is the only form this project
    accepts. The table above says what an escalation can look like; the runner
    says what one actually is. Without this check the table could drift behind a
    newly added path and every item from it would be reported ANONYMOUS -- loud,
    which is the right direction, but only after a run produces one.

    IT FOUND A GAP ON ITS FIRST EXECUTION: `escalate_stale_contested` has 2
    escalating branches, not 1, and the CONTESTED branch was unrecognised.
    """
    import re as _re

    src = (REPO / "bench" / "reference_runner_v3.py").read_text(
        encoding="utf-8").splitlines()
    out = []
    for i, line in enumerate(src):
        if not _re.search(r'\["hil_escalated"\]\s*=\s*True', line):
            continue
        window = "\n".join(src[max(0, i - 12):i + 14])
        if not any(m in window for m in _SITE_MARKERS):
            out.append((i + 1, line.strip()[:80]))
    return out


def registry_entries():
    """Every registry entry in the archive, deduplicated per run by id."""
    for run in sorted(LOGS.iterdir()):
        if not run.is_dir():
            continue
        seen = {}
        for f in sorted(run.glob("*_report.json")):
            try:
                d = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            except (ValueError, OSError):
                continue
            for cid, e in ((d.get("registry") or {}).get("entries") or {}).items():
                if isinstance(e, dict):
                    seen.setdefault(cid, e)
        for cid, e in seen.items():
            yield run.name, cid, e


def escalated_without_a_falsifier(thr: float):
    out = []
    for run, cid, e in registry_entries():
        try:
            sev = float(e.get("severity"))
        except (TypeError, ValueError):
            continue
        if sev < thr or not e.get("hil_escalated"):
            continue
        if (e.get("falsifier_code") or "").strip():
            continue
        named = [n for n, pred, _why in PATHS if pred(e)]
        out.append((run, cid, sev, named, (e.get("hil_reason") or "")[:90]))
    return out


def main() -> int:
    thr = critical_threshold()
    rows = escalated_without_a_falsifier(thr)
    print(f"critical severity threshold, read from the runner: {thr}")
    print(f"archived criticals escalated to a human with NO falsifier: {len(rows)}")

    by_path = {}
    for _r, _c, _s, named, _why in rows:
        key = " + ".join(named) if named else "ANONYMOUS"
        by_path[key] = by_path.get(key, 0) + 1
    print("\nby named escalation path:")
    for k, v in sorted(by_path.items(), key=lambda kv: -kv[1]):
        print(f"  {v:3d}  {k}")

    anon = [r for r in rows if not r[3]]
    print(f"\nANONYMOUS -- escalated, no falsifier, no named path: {len(anon)}")
    for run, cid, sev, _n, why in anon:
        print(f"    {run}  {cid}  sev={sev}  reason={why!r}")
    if not anon:
        print("    none. Every escalation records the mechanism that made it.")

    if rows:
        from statsmodels.stats.proportion import proportion_confint
        from scipy.stats import beta as sbeta
        k, n = len(anon), len(rows)
        lo, hi = proportion_confint(k, n, method="wilson")
        lo_c, hi_c = proportion_confint(k, n, method="beta")
        hi_s = 1.0 if k == n else sbeta.ppf(0.975, k + 1, n - k)
        print(f"\nanonymous rate: {k}/{n} = {k / n:.4%}")
        print(f"  Wilson 95%          : [{lo:.4%}, {hi:.4%}]  (statsmodels)")
        print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_c:.4%}]  (statsmodels/beta)")
        print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_s:.4%}]  (scipy, agrees "
              f"to {abs(hi_s - hi_c):.1e})")

    gaps = uncovered_escalation_sites()
    print(f"\nrunner sites that escalate and leave nothing recognisable: {len(gaps)}")
    for ln, text in gaps:
        print(f"    reference_runner_v3.py:{ln}  {text}")
    if not gaps:
        print("    none. Every escalation site leaves a marker this table reads.")

    print("\nTHE PREDICATE IS UNDERDETERMINED BY ITS ANCHOR. Dropping the "
          "severity filter also\nreproduces exp55_v3_control = 8, with a total "
          "of 32; a strict `> 0.7` gives 20. One\nfamily figure cannot identify "
          "a predicate, so 22 is quoted with its family {20, 22, 32}.\nANONYMOUS "
          "is 0 under every candidate, which is the half that carries the "
          "finding.")

    print("\nTHE ENTRY'S 25 DOES NOT REPRODUCE and its exp53 attribution cannot: "
          "that run\nkeeps findings in checkpoint.json under `all_findings`, in a "
          "schema with no\nescalation flag at all. See this script's docstring.")
    print("THE BACKLOG'S DISPOSITION IS THE FOUNDER'S. Archived runs cannot be "
          "retro-fixed;\nthis supplies the decision's factual basis, not the "
          "decision.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
