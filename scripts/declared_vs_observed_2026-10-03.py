#!/usr/bin/env python3
"""MEASUREMENT 10: does what the launcher DECLARED match what actually FIRED?

WHY IT HAD NO SCRIPT, which turned out to be upstream of the script. The
programme of study lists measurement 10 as having no committed producer. The
reason is that nothing recorded the declaration: `run_simulated_experiment.py`
wrote the runner's results and not one field of the config that produced them,
so "declared" lived only in that file's source and in whatever argv a human kept.
The comparison was unanswerable from the archive for every run ever made. The
launcher now writes `_declared_config` and `_declared_argv` into its report;
this script is the consumer.

WHAT IT CHECKS, each one an OBSERVABLE consequence rather than a restatement of
the flag -- a check that reads the declaration twice and calls the agreement a
measurement is the defect one level up:

  rounds_within_cap      rounds actually run vs `extension_cap`
  pattern_fired          `pattern` vs the pattern the report records running
  topology_fired         `topology` vs the topology the report records
  prose_scoring_fired    `sk_score_prose_listings` vs whether any prose listing
                         was actually scored in the registry
  fix_efficacy_fired     `fix_efficacy_mode` vs whether fix-efficacy records
                         exist on the entries
  blocking_fired         `discrimination_control_blocks` vs whether any
                         NO_DISCRIMINATION entry was actually demoted
  gate_threshold_fired   `gamma_alt_threshold` vs the threshold the convergence
                         decision was taken against

Every disagreement is reported with both sides. An UNOBSERVABLE check -- one
where the run produced no evidence either way -- is named as unobservable and
never counted as agreement, because that is how a vacuous checker passes.

Usage:
  python3 scripts/declared_vs_observed_2026-10-03.py --report bench/logs/<run>/<name>_report.json
  python3 scripts/declared_vs_observed_2026-10-03.py --all          # every report that carries a declaration
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

AGREE, DISAGREE, UNOBSERVABLE = "AGREE", "DISAGREE", "UNOBSERVABLE"


def _entries(rep: dict) -> dict:
    return (rep.get("registry") or {}).get("entries") or {}


def check(rep: dict) -> list[dict]:
    d = rep.get("_declared_config") or {}
    if not d:
        return [{"check": "declaration_present", "verdict": UNOBSERVABLE,
                 "declared": None, "observed": None,
                 "note": "this report carries no _declared_config, so nothing "
                         "about it can be compared; it predates the launcher "
                         "recording its own declaration"}]
    out = []

    def add(name, verdict, declared, observed, note=""):
        out.append({"check": name, "verdict": verdict, "declared": declared,
                    "observed": observed, "note": note})

    gh = rep.get("gamma_critical_history") or rep.get("gamma_history") or []
    cap = d.get("extension_cap")
    if cap is None or not gh:
        add("rounds_within_cap", UNOBSERVABLE, cap, len(gh) or None,
            "no rounds recorded, or no cap declared")
    else:
        add("rounds_within_cap", AGREE if len(gh) <= cap else DISAGREE,
            cap, len(gh),
            "" if len(gh) <= cap else "more rounds ran than the declared cap")

    for field, obs_key in (("pattern", "pattern"), ("topology", "topology")):
        dec = d.get(field)
        obs = rep.get(obs_key)
        if dec is None or obs is None:
            add(f"{field}_fired", UNOBSERVABLE, dec, obs,
                "the report does not state what it actually ran")
        else:
            add(f"{field}_fired", AGREE if dec == obs else DISAGREE, dec, obs)

    es = _entries(rep)
    dec = d.get("sk_score_prose_listings")
    scored = sum(1 for e in es.values()
                 if isinstance(e, dict) and e.get("sk_prose_scored"))
    if dec is None:
        add("prose_scoring_fired", UNOBSERVABLE, dec, scored)
    elif dec and not es:
        add("prose_scoring_fired", UNOBSERVABLE, dec, scored,
            "no findings, so prose scoring had nothing to act on")
    elif dec:
        add("prose_scoring_fired", AGREE if scored else UNOBSERVABLE, dec, scored,
            "" if scored else "declared on, but no entry records a prose score; "
                              "the run may have had no prose listing to score")
    else:
        add("prose_scoring_fired", DISAGREE if scored else AGREE, dec, scored,
            "declared off but prose scores exist" if scored else "")

    dec = d.get("fix_efficacy_mode")
    fe = sum(1 for e in es.values()
             if isinstance(e, dict) and (e.get("fix_efficacy")
                                         or e.get("fix_efficacy_outcome")))
    if dec is None:
        add("fix_efficacy_fired", UNOBSERVABLE, dec, fe)
    elif str(dec) in ("off", "none", ""):
        add("fix_efficacy_fired", DISAGREE if fe else AGREE, dec, fe,
            "declared off but efficacy records exist" if fe else "")
    else:
        add("fix_efficacy_fired", AGREE if fe else UNOBSERVABLE, dec, fe,
            "" if fe else "declared on, but no fix reached closure, so the "
                          "probe had nothing to run on")

    dec = d.get("discrimination_control_blocks")
    voided = [cid for cid, e in es.items()
              if isinstance(e, dict)
              and (e.get("falsifier_verdict") or "") == "NON_DISCRIMINATING"]
    demoted = [cid for cid in voided
               if es[cid].get("status") not in ("CONFIRMED", "CLOSED",
                                                "CORROBORATED")]
    if not voided:
        add("blocking_fired", UNOBSERVABLE, dec, 0,
            "no falsifier was voided, so the flag could not act either way")
    elif dec:
        add("blocking_fired", AGREE if len(demoted) == len(voided) else DISAGREE,
            dec, f"{len(demoted)} of {len(voided)} demoted",
            "" if len(demoted) == len(voided)
            else f"declared blocking, but these stayed terminal: "
                 f"{sorted(set(voided) - set(demoted))}")
    else:
        add("blocking_fired", AGREE if not demoted else DISAGREE,
            dec, f"{len(demoted)} of {len(voided)} demoted",
            "" if not demoted else f"declared NOT blocking, but these were "
                                   f"demoted anyway: {sorted(demoted)}")

    dec = d.get("gamma_alt_threshold")
    reason = (rep.get("convergence_reason") or "")
    if dec is None:
        add("gate_threshold_fired", UNOBSERVABLE, dec, None)
    elif not reason:
        add("gate_threshold_fired", UNOBSERVABLE, dec, None,
            "the run recorded no convergence reason to read a threshold from")
    else:
        add("gate_threshold_fired",
            AGREE if str(dec) in reason else UNOBSERVABLE, dec, reason[:160],
            "" if str(dec) in reason
            else "the reason text does not quote the declared threshold, so "
                 "this cannot be decided from it")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--report", help="a single *_report.json")
    ap.add_argument("--all", action="store_true",
                    help="every report under bench/logs")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if not a.report and not a.all:
        ap.error("pass --report or --all")

    targets = []
    if a.report:
        targets = [pathlib.Path(a.report)]
    else:
        targets = sorted((REPO / "bench" / "logs").rglob("*_report.json"))

    overall, rows = {AGREE: 0, DISAGREE: 0, UNOBSERVABLE: 0}, []
    carried = 0
    for t in targets:
        try:
            rep = json.loads(t.read_text(encoding="utf-8", errors="replace"))
        except (ValueError, OSError):
            continue
        res = check(rep)
        if rep.get("_declared_config"):
            carried += 1
        for r in res:
            overall[r["verdict"]] = overall.get(r["verdict"], 0) + 1
        rows.append({"report": str(t.relative_to(REPO)) if str(t).startswith(str(REPO)) else str(t),
                     "checks": res})

    if a.json:
        print(json.dumps({"reports": len(rows),
                          "reports_carrying_a_declaration": carried,
                          "totals": overall, "rows": rows}, indent=2))
        return 0

    print("DECLARED VS OBSERVED (measurement 10)")
    print(f"  reports read                  : {len(rows)}")
    print(f"  reports with a declaration    : {carried}")
    if not carried:
        print("  NOTHING CAN BE COMPARED YET: no archived report carries a")
        print("  declaration. The launcher records one from 2026-10-03; the")
        print("  3 study runs are the first that can answer this.")
    for row in rows:
        shown = [c for c in row["checks"] if c["verdict"] != UNOBSERVABLE]
        if not shown:
            continue
        print(f"\n  {row['report']}")
        for c in row["checks"]:
            mark = {AGREE: "ok ", DISAGREE: "NO ", UNOBSERVABLE: "-- "}[c["verdict"]]
            print(f"    {mark}{c['check']:22s} declared={c['declared']!r} "
                  f"observed={c['observed']!r}"
                  + (f"  :: {c['note']}" if c["note"] else ""))
    print(f"\n  totals: {overall[AGREE]} agree, {overall[DISAGREE]} DISAGREE, "
          f"{overall[UNOBSERVABLE]} unobservable "
          "(unobservable is NEVER counted as agreement)")
    return 1 if overall[DISAGREE] else 0


if __name__ == "__main__":
    raise SystemExit(main())
