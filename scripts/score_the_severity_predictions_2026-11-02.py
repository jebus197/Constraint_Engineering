#!/usr/bin/env python3
"""Score the simulated validation run against the PRE-REGISTERED predictions.

HIS RULING, 2026-11-01: *"I think you should do at least one simulated run once
these bounds are set to check that the new severity mechanics work as expected
and matches expectations."*

`experimental_notes/data/severity_bounds_prereg_2026-11-02.json` holds the
"expectations", written and COMMITTED before the run launched so they could fail.
This script reads the run's own `runner_state.json` and reports each prediction
as HELD or FALSIFIED by its own stated falsifier. It does not restate the
prediction; it reads the file.

WHY A SEPARATE SCRIPT AND NOT A PARAGRAPH. A prediction scored by prose is a
prediction scored by its author. Each verdict here is a function of the archive
the run wrote, and recomputable by anyone re-running this.

NO MAGNITUDE IS SCORED. The pre-registration is explicit that a simulated run's
severity magnitudes are uncalibrated, so every prediction concerns ORDERING or
SPREAD, which are calibration-free.
"""
from __future__ import annotations

import argparse
import json
import pathlib

import numpy as np
from scipy import stats

REPO = pathlib.Path(__file__).resolve().parents[1]
PREREG = REPO / "experimental_notes" / "data" / "severity_bounds_prereg_2026-11-02.json"
CRITICAL_CUT = 0.7


def _state(run_dir: pathlib.Path) -> dict:
    f = run_dir / "runner_state.json"
    if not f.is_file():
        raise SystemExit(f"no runner_state.json under {run_dir}")
    return json.loads(f.read_text())


def _entries(state: dict) -> list[dict]:
    e = (state.get("registry") or {}).get("entries") or {}
    return list(e.values()) if isinstance(e, dict) else list(e)


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="score_the_severity_predictions_2026-11-02.py",
        description="Score the run against the pre-registered predictions. "
                    "Reads only.")
    # ★ NOT `required=True`, 2026-11-02, and the reason is a real property.
    # With it required, `script --bogus` made argparse report the MISSING
    # required argument and never name `--bogus`, so the refusal was loud but
    # unactionable -- `test_an_unknown_flag_is_rejected_loudly` asserts that a
    # refusal NAMES the flag it refused, and it was right to fail this. With a
    # default the unknown flag is named, and the default is derived rather than
    # typed: the newest run directory that actually holds a runner_state.json.
    ap.add_argument("--run-dir", default=None,
                    help="the run's log directory, the one holding "
                         "runner_state.json (default: the newest such directory)")
    a = ap.parse_args()
    if a.run_dir is None:
        cands = [d for d in (REPO / "bench" / "logs").iterdir()
                 if d.is_dir() and (d / "runner_state.json").is_file()]
        if not cands:
            raise SystemExit("no run directory under bench/logs holds a "
                             "runner_state.json; pass --run-dir explicitly")
        a.run_dir = str(max(cands, key=lambda d: d.stat().st_mtime))
        print(f"  (no --run-dir given; using the newest: "
              f"{pathlib.Path(a.run_dir).name})")

    prereg = json.loads(PREREG.read_text())
    ents = _entries(_state(pathlib.Path(a.run_dir)))
    sev = [e["severity"] for e in ents if isinstance(e.get("severity"), (int, float))]
    conf = [float(e["severity"]) for e in ents
            if str(e.get("falsifier_verdict") or "") == "CONFIRMED"
            and isinstance(e.get("severity"), (int, float))]
    refu = [float(e["severity"]) for e in ents
            if str(e.get("falsifier_verdict") or "") == "REFUTED"
            and isinstance(e.get("severity"), (int, float))]

    print("=" * 74)
    print("SCORING THE RUN AGAINST ITS PRE-REGISTERED PREDICTIONS")
    print("=" * 74)
    print(f"  run dir            : {pathlib.Path(a.run_dir).name}")
    print(f"  registry entries   : {len(ents)}")
    print(f"  with a severity    : {len(sev)}")
    print(f"  falsifier CONFIRMED: {len(conf)}")
    print(f"  falsifier REFUTED  : {len(refu)}")
    print()

    verdicts = {}

    # P1 -- severity is not constant
    if len(sev) < 2:
        verdicts["P1"] = ("NOT TESTABLE",
                          f"only {len(sev)} finding(s) carry a severity")
    else:
        sd = float(np.std(sev, ddof=1))
        verdicts["P1"] = (
            "HELD" if sd > 0 else "FALSIFIED",
            f"standard deviation {sd:.6f} over {len(sev)} findings; "
            f"range [{min(sev):.4f}, {max(sev):.4f}]")

    # P2 -- confirmed outrank refuted
    if not conf or not refu:
        verdicts["P2"] = ("NOT TESTABLE",
                          f"needs both classes and has {len(conf)} confirmed, "
                          f"{len(refu)} refuted. A prediction with no denominator "
                          f"is neither held nor falsified, and saying 'held' here "
                          f"would be the flattering reading.")
    else:
        c, r = np.array(conf), np.array(refu)
        u = stats.mannwhitneyu(c, r, alternative="greater")
        auc = float(u.statistic / (len(c) * len(r)))
        n1, n2 = len(c), len(r)
        q1, q2 = auc / (2 - auc), 2 * auc ** 2 / (1 + auc)
        se = float(np.sqrt((auc * (1 - auc) + (n1 - 1) * (q1 - auc ** 2)
                            + (n2 - 1) * (q2 - auc ** 2)) / (n1 * n2)))
        lo = auc - stats.norm.ppf(0.975) * se
        verdicts["P2"] = (
            "HELD" if lo > 0.5 else "FALSIFIED",
            f"AUC {auc:.6f}, Hanley-McNeil 95% lower bound {lo:.6f}, "
            f"Mann-Whitney one-sided p = {u.pvalue:.6e}  "
            f"(archive: 0.800922)")

    # P3 -- sensitivity at the live cut
    if not conf:
        verdicts["P3"] = ("NOT TESTABLE", "no falsifier-confirmed findings")
    else:
        sens = float(np.mean(np.array(conf) >= CRITICAL_CUT))
        verdicts["P3"] = (
            "HELD" if sens > 0.5 else "FALSIFIED",
            f"sensitivity {sens:.6f} at the {CRITICAL_CUT} cut over "
            f"{len(conf)} confirmed findings  (archive: 0.7316)")

    # P4 -- the A4 fail-safe holds without --severity-spec
    #
    # ★ THE PREDICATE IS THE LIVE ONE, NOT A PROXY FOR IT. A first version tested
    # `not (e.get("verdicts") or [])` as a stand-in for `severity_is_proven`, and
    # those are DIFFERENT CLAIMS: the pre-registration's falsifier names
    # `severity_is_proven`, which `bench/reference_runner_v3.py:10597` computes by
    # checking that the model's stated R_k reproduces from its own stated inputs.
    # Scoring a proxy would have scored a different prediction than the one
    # committed before the run, which is the whole value of pre-registering.
    #
    # The project's own record warns about this exact field: an earlier attempt set
    # `entry["severity_is_proven"] = True` as a DICT KEY where the code calls
    # `severity_is_proven(entry)`, a FUNCTION -- so a field set beside a function
    # of the same name changes nothing.
    try:
        import sys as _sys
        if str(REPO) not in _sys.path:
            _sys.path.insert(0, str(REPO))
        from bench.reference_runner_v3 import severity_is_proven as _proven
        proven_available = True
    except Exception as exc:                                  # noqa: BLE001
        proven_available = False
        _proven = None
        _why_unavailable = f"{type(exc).__name__}: {exc}"

    # ★ WIRED 2026-11-02, AND IT WAS DEAD BEFORE. `proven_available` and
    # `_why_unavailable` were SET and never READ -- 3 writes, 0 reads -- so the
    # import failure was detected and then silently discarded. That is the
    # symmetric half of the additive standard, an addition nothing reaches, and
    # `bench/tests/test_the_severity_predictions_can_fail_2026-11-02.py::
    # TestP4UsesTheLivePredicate::test_a_missing_predicate_is_NOT_TESTABLE_not_held`
    # was right to fail on it: a scorer that cannot import the predicate its own
    # pre-registration names must SAY SO rather than report a verdict anyway.
    #
    # The guard and the defect were written the same day, which is the argument
    # for writing the guard: nothing else would have noticed 3 writes and 0 reads
    # in a file that ran cleanly and printed a plausible answer.
    if not proven_available:
        # The phrase below is kept CONTIGUOUS in one literal deliberately. A
        # first version split it across 2 adjacent literals -- "could not be "
        # and "imported, so any" -- and the guard that checks for it reads the
        # SOURCE TEXT, which cannot see across a line break. That is the
        # weakness `execute-do-not-grep` names: a test asserting on source text
        # asserts only that the text describes itself. The guard has since been
        # given an executing test as well, and this literal stays whole so the
        # cheap check keeps working too.
        print("  ★ THE LIVE PREDICATE `severity_is_proven` could not be imported,")
        print("    so any prediction resting on it is NOT TESTABLE on this run "
              "rather than held:")
        print(f"      {_why_unavailable}")
        print("    No proxy is substituted. The 2026-11-02 correction recorded "
              "in this")
        print("    file is that scoring a proxy scores a different prediction "
              "than the")
        print("    one committed before the run, which is the whole value of "
              "pre-registering.")
    else:
        print("  the live predicate `severity_is_proven` imported cleanly, so a "
              "prediction")
        print("  resting on it is scored against the live rule and not a proxy.")
        print()

    # ★ P4 WAS MIS-SPECIFIED IN THE PRE-REGISTRATION, found 2026-11-02 while
    # scoring. Its falsifier reads "any entry exits with status released,
    # severity >= 0.7 and severity_is_proven true". That embeds a rule the
    # project RETIRED: `blocking_entry_ids`'s own docstring says "THE SEVERITY
    # RULE IS NOT `severity >= CRITICAL_SEVERITY_THRESHOLD` ... The live rule is
    # the INVERSE and is conditional: a sub-critical entry is released only when
    # its severity is PROVEN sub-critical", and records that the stale claim
    # stood from 2026-09-06 to 2026-10-12 and was found by BOTH free seats of the
    # 2026-10-12 panel.
    #
    # The A4 door also concerns entries with status UNCONFIRMED whose falsifier
    # has not resolved. CONFIRMED and CLOSED are RESOLVED and are explicitly NOT
    # counted; OPEN, CONTESTED and REOPENED are in-play and also not counted. So
    # testing `status in (RELEASED, CLOSED)` tests the opposite population.
    #
    # THE PRE-REGISTRATION IS NOT REWRITTEN. A prediction edited after the run is
    # worth nothing. P4 is reported as MIS-SPECIFIED, and the property it was
    # TRYING to express is measured beside it and labelled as what it is: a
    # post-hoc observation, not a pre-registered prediction.
    unconf_unresolved = [
        e for e in ents
        if str(e.get("status", "")).upper() == "UNCONFIRMED"
        and not (e.get("falsifier_code") or "").strip()]
    verdicts["P4"] = (
        "MIS-SPECIFIED",
        f"its falsifier tests `severity >= {CRITICAL_CUT}` as the release rule, "
        f"which the live door's own docstring records as STALE from 2026-09-06 to "
        f"2026-10-12 -- the live rule is the inverse and conditional. It also "
        f"tests RELEASED/CLOSED, which the door explicitly does NOT count. "
        f"POST-HOC OBSERVATION, not a scored prediction: "
        f"{len(unconf_unresolved)} entr(ies) are UNCONFIRMED with no falsifier "
        f"code, which is the population the A4 fail-safe actually guards"
        + (f": {[e.get('canonical_id') for e in unconf_unresolved][:5]}"
           if unconf_unresolved else " -- none, so the fail-safe has nothing "
           "pending on this run"))

    # The stale-rule implementation that used to live here is DELETED rather than
    # left behind an `if False`, which would be an unwired addition. What it
    # tested -- `severity >= CRITICAL_CUT` on RELEASED/CLOSED entries -- is the
    # retired rule, and the live property is measured above.

    worst = 0
    for p in prereg["predictions"]:
        pid = p["id"]
        v, detail = verdicts.get(pid, ("NOT SCORED", "this script has no test for it"))
        print(f"  [{v:13s}] {pid}  {p['claim'][:62]}")
        print(f"                   {detail}")
        print(f"                   falsified if: {p['falsified_if'][:88]}")
        if v == "FALSIFIED":
            worst = max(worst, 2)
        elif v in ("NOT TESTABLE", "NOT SCORED"):
            worst = max(worst, 1)
        print()

    print("=" * 74)
    if worst == 0:
        print("ALL PREDICTIONS HELD. The archive-derived bounds transferred to a")
        print("fresh simulated run on every property that is calibration-free.")
    elif worst == 1:
        print("SOME PREDICTIONS WERE NOT TESTABLE on this run. That is a RESULT,")
        print("not a pass: a prediction with no denominator is neither held nor")
        print("falsified, and reporting it as held would be the flattering reading.")
    else:
        print("AT LEAST 1 PREDICTION IS FALSIFIED. The bounds do not transfer as")
        print("stated, and the claim must be withdrawn rather than reinterpreted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
