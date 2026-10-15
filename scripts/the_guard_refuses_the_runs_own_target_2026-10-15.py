#!/usr/bin/env python3
"""The confinement guard refuses the falsifier's own review target. Measured.

OBSERVED 2026-10-15 08:44 BST on free run 2, then confirmed on free run 1's
completed log: 18 refusals per run reading

    bench/logs/<run>/working/prose_with_computable_listings.md

which is the run's OWN WORKING COPY of the document the falsifier was asked to
review. Each refusal routes its finding to a human carrying the text "This is
NOT a verdict: the finding is neither confirmed nor refuted."

NEITHER COMPONENT IS WRONG ON ITS OWN. THE SEAM IS.

  * `bench/falsifier_verify.py` defines `_is_evidence(path)`, which returns True
    for any path carrying a `bench` segment immediately followed by `logs`, and
    `_denied(path)` refuses an evidence path EVEN INSIDE AN ALLOWED ROOT. That
    is deliberate and correct: a falsifier reading this project's run evidence
    could read prior verdicts instead of demonstrating a defect. Both free seats
    found that hole independently on 2026-10-12 and it was closed the same day
    by commit `e8ee2e18`, whose message reads "his ruling 2: the fix EXISTS and
    is built. A falsifier can no longer read our evidence."
  * `bench/reference_runner_v3.py:11688` stages the review target at
    `work_dir = logs_dir / "working"`, which has been its location since commit
    `ce08914c` on 2026-09-01.
  * `falsifier_verify._allow_roots` already names a designated, ALLOWED staging
    location for exactly this purpose: `STAGED_TARGET_ROOT`, which is
    `~/CDSFL_review_targets`, described in its own docstring as where "an exam
    falsifier opens the one document it is given".

So the runner stages the target inside the one tree the guard refuses, while an
allowed staging root sits unused. The guard is right, the staging location is
wrong, and each is individually defensible, which is why reading either file
alone cannot find this.

IT IS A REGRESSION WITH A DATE, AND THE EVIDENCE IS THE REFUSED PATHS THEMSELVES
RATHER THAN THE COMMIT DATES. `study_run1b_2026-10-03`, which predates the
evidence rule, carries 81 refusals and NONE of them is a target: they are Python
interpreter paths -- `site-packages` listings and `<string>`/`<stdin>` import
probes. Free runs 1 and 2, which postdate it, carry 18 each and EVERY ONE is the
working target. The failure mode changed shape between those dates.

WHAT IT DOES NOT DO, STATED BECAUSE OVERSTATING IT WOULD BE EASY. It did not
stop run 1 converging, and it did not leave a critical unresolved: run 1 closed
at 0 unresolved criticals and its post-convergence settle closed 3
CONFIRMED-and-verified findings. The convergence gate counts UNCONFIRMED
criticals, and a refusal is not a disconfirmation. The cost is to VERIFICATION
DEPTH -- how many findings carry an executed demonstration rather than a human
referral -- not to the gate.

NOT FIXED HERE. Run 2 was in flight and carries the identical defect, 18 and 18,
so the matched pair the 2 runs exist to form is intact and attributable. Fixing
the staging location mid-pair would have made neither run comparable to the
other. Recorded for after run 2.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench/logs"
REFUSAL = "outside the declared target roots"
MATCHED = re.compile(r"matched:\s*'([^']*)'")


def classify(path: str) -> str:
    p = path.replace("\\", "/")
    # strip the leading verb ("open ", "os.listdir ")
    if " " in p:
        p = p.split(" ", 1)[1]
    parts = [q for q in p.split("/") if q]
    for i, seg in enumerate(parts):
        if seg == "bench" and i + 1 < len(parts) and parts[i + 1] == "logs":
            if "working" in parts:
                return "THE RUN'S OWN WORKING TARGET"
            return "project evidence (not the target)"
    if "site-packages" in parts or "lib-dynload" in parts:
        return "python interpreter / site-packages"
    if any(q in ("<string>", "<stdin>") for q in parts):
        return "python import probe"
    if parts[:1] == ["Users"] or p.startswith("~"):
        return "home-rooted"
    return "other"


def scan(run_dir: pathlib.Path) -> dict:
    log = run_dir / "console.log"
    if not log.exists():
        return {}
    text = log.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    kinds: dict[str, int] = {}
    total = 0
    for i, ln in enumerate(lines):
        if REFUSAL not in ln:
            continue
        total += 1
        m = None
        for j in range(i + 1, min(i + 4, len(lines))):
            m = MATCHED.search(lines[j])
            if m:
                break
        kind = classify(m.group(1)) if m else "unparsed"
        kinds[kind] = kinds.get(kind, 0) + 1
    return {"refusals": total, "by_kind": kinds}


def main() -> int:
    from statsmodels.stats.proportion import proportion_confint
    from scipy import stats as sstats

    runs = [
        ("study_run1b_2026-10-03_20261003T100439Z", "BEFORE the 2026-10-12 evidence rule"),
        ("free_run1_directive_whole_20261015T061123Z_20261015T061124Z", "AFTER"),
        ("free_run2_severity_spec_20261015T073418Z_20261015T073418Z", "AFTER (in flight at scan time)"),
    ]
    out = {}
    print("=" * 78)
    print("1. WHAT WAS REFUSED, BY KIND, BEFORE AND AFTER")
    print("=" * 78)
    for name, era in runs:
        d = LOGS / name
        r = scan(d)
        if not r:
            print(f"  {name}: no console.log")
            continue
        out[name] = {"era": era, **r}
        print(f"\n  {name}")
        print(f"    era: {era}")
        print(f"    refusals: {r['refusals']}")
        for k, v in sorted(r["by_kind"].items(), key=lambda kv: -kv[1]):
            print(f"      {v:>4}  {k}")

    print()
    print("=" * 78)
    print("2. THE PROPORTION THAT IS THE RUN'S OWN TARGET")
    print("=" * 78)
    KEY = "THE RUN'S OWN WORKING TARGET"
    rows = []
    for name, era in runs:
        r = out.get(name)
        if not r or not r["refusals"]:
            continue
        k = r["by_kind"].get(KEY, 0)
        n = r["refusals"]
        lo, hi = proportion_confint(k, n, method="wilson")
        lob, hib = proportion_confint(k, n, method="beta")
        rows.append((name, k, n, lo, hi, lob, hib))
        print(f"  {name[:46]:<46} {k:>3} of {n:<3} "
              f"Wilson [{lo*100:7.4f}%, {hi*100:8.4f}%]")
        print(f"  {'':<46} {'':>3}    {'':<3} "
              f"CP     [{lob*100:7.4f}%, {hib*100:8.4f}%]")

    if len(rows) >= 2:
        before = rows[0]
        after = rows[1]
        table = [[after[1], after[2] - after[1]], [before[1], before[2] - before[1]]]
        ft = sstats.fisher_exact(table)
        print()
        print(f"  Fisher exact, after vs before: p = {ft[1]:.6e}  "
              f"odds ratio = {ft[0] if ft[0] != float('inf') else 'inf'}")
        try:
            chi = sstats.chi2_contingency(table, correction=True)[1]
            print(f"  chi-square with Yates cross-check: p = {chi:.6e}")
        except ValueError as e:
            print(f"  chi-square cross-check: undefined ({e})")

    print()
    print("=" * 78)
    print("3. THE SEAM, STATED AS 2 FACTS AND 1 UNUSED ROOT")
    print("=" * 78)
    fv = (REPO / "bench/falsifier_verify.py").read_text(encoding="utf-8")
    rr = (REPO / "bench/reference_runner_v3.py").read_text(encoding="utf-8")
    staged = re.search(r'STAGED_TARGET_ROOT\s*=\s*(.+)', fv)
    workdir = re.search(r'work_dir\s*=\s*logs_dir\s*/\s*"working"', rr)
    evidence = 'seg == "bench" and i + 1 < len(parts) and parts[i + 1] == "logs"' in fv
    denied_before_allow = fv.index("def _denied") < fv.index("def _allow_roots") or True
    print(f"  guard refuses any bench/logs path as evidence : {evidence}")
    print(f"  runner stages the target at logs_dir/working   : {bool(workdir)}")
    print(f"  an ALLOWED staged root exists and is unused    : "
          f"{staged.group(1).strip() if staged else 'NOT FOUND'}")
    print(f"  the staged root appears in the runner          : "
          f"{'CDSFL_review_targets' in rr}")

    verdict = bool(evidence) and bool(workdir) and ("CDSFL_review_targets" not in rr)
    print()
    print("=" * 78)
    print("VERDICT")
    print("=" * 78)
    print(f"  the seam is real: {verdict}")
    print("  the guard is correct; the staging location is inside what it guards;")
    print("  and the designated allowed staging root is never used by the runner.")
    print()
    print("  BOUND: this did NOT stop run 1 converging and left 0 unresolved")
    print("  criticals. The gate counts UNCONFIRMED criticals and a refusal is not")
    print("  a disconfirmation. The cost is verification DEPTH, not convergence.")

    out["seam"] = {
        "guard_refuses_bench_logs_as_evidence": bool(evidence),
        "runner_stages_at_logs_dir_working": bool(workdir),
        "staged_target_root": staged.group(1).strip() if staged else None,
        "runner_uses_the_staged_root": "CDSFL_review_targets" in rr,
        "evidence_rule_commit": "e8ee2e18 (2026-10-12)",
        "staging_location_commit": "ce08914c (2026-09-01)",
        "verdict": verdict,
    }
    dest = REPO / "experimental_notes/evidence/guard_refuses_own_target_2026-10-15.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(f"  evidence -> {dest.relative_to(REPO)}")
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
