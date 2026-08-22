#!/usr/bin/env python3
"""THE INSTRUMENT INVENTORY. Every component that emits a number or a verdict.

WHY THIS EXISTS
---------------
Every defect found in the week of 2026-08-15 to 2026-08-22 was found by a
measurement nobody had ever run: the similarity function's flagging rate, the
merge paths' decision source, the R_k reader's parse coverage, the detection
channel's inputs, the falsifier gate's dependence on its target. Each component
had been built, switched on, and used to produce results without anyone checking
that it did what it said.

That is not an endless problem. It is a FINITE backlog nobody had enumerated.
This file is the enumeration. It converts "we keep finding defects" into a
burndown with a visible end.

COMMISSIONED means: a test exists that exercises this component with a KNOWN-GOOD
and a KNOWN-BAD input and asserts it answers differently. That is the falsification
principle applied to the instrument rather than to the artefact. The gate's own
failure is the canonical case -- `reverify_falsifier("print('FALSIFIED')")` returns
CONFIRMED, and no test had ever fed it a known-bad falsifier.

THE DETECTION HERE IS HEURISTIC AND SAYS SO. A test is scored as a commissioning
candidate when it names the component AND carries both a positive and a negative
assertion. That is a first pass, not a verdict. Founder ruling 2026-08-22: the
panel confirms or refutes each row with tools in the build experiment. Rows are
therefore marked with CC1's confidence, and the panel's verdict column is empty
until they fill it.

    python3 scripts/instrument_inventory.py [--md]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
TESTS = REPO / "bench/tests"

# (id, human name, symbol or module to grep, file, what it emits, config flag or "")
INSTRUMENTS = [
    ("I01", "Duane/Crow-AMSAA gamma estimator", "_estimate_gamma", "bench/reference_runner_v2.py", "number", ""),
    ("I02", "Two-sided gamma gate", "_check_gamma_gate", "bench/reference_runner_v2.py", "verdict", ""),
    ("I03", "Churn detector (rho)", "_compute_rho", "bench/reference_runner_v2.py", "number", ""),
    ("I04", "State-convergence check", "_check_state_convergence", "bench/reference_runner_v2.py", "verdict", ""),
    ("I05", "Gamma-alt convergence", "_check_gamma_alt_convergence", "bench/reference_runner_v2.py", "verdict", ""),
    ("I06", "Hardened convergence", "_check_hardened_convergence", "bench/reference_runner_v2.py", "verdict", "hardened_gate_enabled"),
    ("I07", "Stall convergence", "_check_stall_convergence", "bench/reference_runner_v2.py", "verdict", ""),
    ("I08", "Budget extension", "_check_budget_extension", "bench/reference_runner_v2.py", "verdict", ""),
    ("I09", "Attention metrics", "_compute_attention_metrics", "bench/reference_runner_v2.py", "numbers", ""),
    ("I10", "S_k fix efficacy", "compute_sk", "bench/reference_runner_v2.py", "number", "sk_enabled"),
    ("I11", "S_k admissibility threshold", "check_sk_threshold", "bench/reference_runner_v2.py", "verdict", "sk_enabled"),
    ("I12", "R_k three-phase model", "compute_rk", "bench/reference_runner_v2.py", "number", ""),
    ("I13", "R_k eta channel", "compute_rk_with_eta_channel", "bench/reference_runner_v2.py", "number", ""),
    ("I14", "THE FALSIFIER GATE", "apply_falsifier_verdicts", "bench/reference_runner_v2.py", "verdict", "falsifier_gate_enabled"),
    ("I15", "Verdict reader", "reverify_falsifier", "bench/falsifier_verify.py", "verdict", ""),
    ("I16", "Discrimination control", "run_discrimination_control", "bench/reference_runner_v2.py", "verdict", "(presence-gated)"),
    ("I17", "Routing/escalation ladder", "_apply_routing", "bench/reference_runner_v2.py", "routing decision", "routing_enabled"),
    ("I18", "Status transitions", "_update_finding_statuses", "bench/reference_runner_v2.py", "status", ""),
    ("I19", "Similarity function (3 tiers)", "signature_similarity", "bench/dm/_similarity.py", "number+verdict", ""),
    ("I20", "Outcome agreement (tier 3)", "outcome_agreement", "bench/dm/_similarity.py", "verdict", ""),
    ("I21", "Location keying", "location_only_series", "bench/convergence_location.py", "series", ""),
    ("I22", "Divergence measure", "_divergence", "bench/dm/_divergence.py", "number", ""),
    ("I23", "Diversity measure", "_diversity", "bench/dm/_diversity.py", "number", ""),
    ("I24", "Fix complexity (nu), shadow", "_fix_complexity", "bench/dm/_fix_complexity.py", "number", "(shadow)"),
    ("I25", "Immune memory prior", "_memory", "bench/dm/_memory.py", "number", ""),
    ("I26", "Load balancer  [SHELVED 2026-08-22]", "_load_balancer", "bench/dm/_load_balancer.py", "allocation", "(shelved)"),
    ("I27", "Shadow stage-6", "_shadow_stage6", "bench/dm/_shadow_stage6.py", "number", "(shadow)"),
    ("I28", "Near-duplicate feedback into the prompt", "_feedback", "bench/dm/_feedback.py", "prompt text", ""),
    ("I29", "Claim-type classifier", "_classify_claim_v2", "bench/immune_agents.py", "class", ""),
    ("I30", "Immune removal decision", "immune", "bench/immune_agents.py", "verdict", ""),
    ("I31", "Health monitor", "health", "bench/immune_agents.py", "alarm", ""),
    ("I32", "Finding parser / description extractor", "parse_findings", "bench/runner_core.py", "structured findings", ""),
    ("I33", "Survived-falsification ledger", "SurvivedFalsificationLedger", "bench/evidence.py", "positive record", "(NOT WIRED)"),
    ("I34", "Null-perturbation control", "null_perturbation", "scripts/null_perturbation_control.py", "verdict", "(offline script)"),
]

# DIRECT MEASUREMENTS. These are not heuristics: each was established by running
# the component against a known-bad input and recording what it did. Where one
# exists it OVERRIDES the heuristic, because a heuristic that disagrees with a
# measurement is wrong by definition.
MEASURED = {
    "I14": (False, "MEASURED 2026-08-22: reverify_falsifier(\"print('FALSIFIED')\") "
                   "returns CONFIRMED, and so does \"assert False, 'FALSIFIED'\". The "
                   "gate has never required a falsifier to depend on its target. NOT "
                   "COMMISSIONED, and the heuristic scored it as commissioned."),
    "I16": (True,  "MEASURED 2026-08-22: run against 372 archived falsifiers with a "
                   "tripwire, a baseline requirement and a determinism check; it "
                   "separated 132 discriminating from 131 non-discriminating."),
    "I34": (True,  "MEASURED 2026-08-21: 397 findings, 360 fired, 0 moved on either "
                   "an irrelevant comment or an unaccused function rename."),
    "I33": (False, "MEASURED 2026-08-22: has a full test suite but is NOT READ BY THE "
                   "RUNNER. A tested component that nothing calls is not commissioned; "
                   "it is shelved."),
    "I26": (False, "SHELVED by founder ruling 2026-08-22. Never ran outside its own "
                   "tests; reports an impossible allocation as a success."),
}

POS = re.compile(r"assert[^\n]*(==|is True|is not None|in |> ?0|>= ?)", re.I)
NEG = re.compile(r"assert[^\n]*(!=|is False|is None|not in |pytest\.raises|== ?0|not )", re.I)


def _grep_tests(symbol: str) -> list:
    """Test files naming this symbol."""
    out = subprocess.run(["grep", "-rl", symbol, str(TESTS)],
                         capture_output=True, text=True).stdout.split()
    return [pathlib.Path(p) for p in out if p.endswith(".py")]


def _commissioning_candidate(files: list, symbol: str) -> tuple:
    """Does any naming test carry BOTH a positive and a negative assertion?

    Heuristic and labelled as such. A test that only ever asserts the happy path
    cannot detect the failure mode this project keeps shipping, which is a
    component that answers the same way regardless of input.
    """
    for f in files:
        try:
            txt = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if symbol not in txt:
            continue
        if POS.search(txt) and NEG.search(txt):
            return True, f.name
    return False, ""


def _flag_in_live_configs(flag: str) -> str:
    if not flag or flag.startswith("("):
        return flag or "-"
    ALIASES = {"routing_enabled": ("routing_enabled", "take_up_slack_enabled")}
    keys = ALIASES.get(flag, (flag,))
    on = off = 0
    for cfg in sorted(REPO.glob("bench/exp4[2-9]_configs/*.json")) + \
            sorted(REPO.glob("bench/exp5*_configs/*.json")):
        try:
            d = json.loads(cfg.read_text())
        except Exception:            # noqa: BLE001
            continue
        v = next((d[k] for k in keys if k in d), None)
        if v is True:
            on += 1
        elif v is None:
            off += 1
    return f"on in {on}/{on+off}" if (on + off) else "-"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--md", action="store_true", help="emit a markdown table")
    args = ap.parse_args()

    rows = []
    for iid, name, sym, path, emits, flag in INSTRUMENTS:
        exists = (REPO / path).is_file()
        files = _grep_tests(sym) if exists else []
        comm, which = _commissioning_candidate(files, sym)
        heuristic = comm
        if iid in MEASURED:
            comm, which = MEASURED[iid]
            which = "MEASURED: " + which
        rows.append({"id": iid, "name": name, "symbol": sym, "file": path,
                     "emits": emits, "flag": flag, "file_exists": exists,
                     "naming_tests": len(files),
                     "commissioning_candidate": comm, "evidence": which,
                     "heuristic_said": heuristic,
                     "measured": iid in MEASURED,
                     "panel_verdict": ""})

    n = len(rows)
    c = sum(1 for r in rows if r["commissioning_candidate"])
    if args.md:
        print("| id | instrument | emits | live flag | tests naming it | commissioning candidate | panel |")
        print("|---|---|---|---|---|---|---|")
        for r in rows:
            print(f"| {r['id']} | {r['name']} | {r['emits']} | "
                  f"{_flag_in_live_configs(r['flag'])} | {r['naming_tests']} | "
                  f"{'YES — ' + r['evidence'] if r['commissioning_candidate'] else '**NO**'} | |")
        print(f"\n**{c} of {n} instruments have a commissioning candidate. "
              f"{n - c} do not.**")
    else:
        print(f"  {'id':<5}{'instrument':<42}{'emits':<17}{'flag':<16}"
              f"{'tests':>6}{'  commissioned?':<18}")
        for r in rows:
            mark = "yes" if r["commissioning_candidate"] else "NO"
            print(f"  {r['id']:<5}{r['name'][:41]:<42}{r['emits']:<17}"
                  f"{_flag_in_live_configs(r['flag']):<16}{r['naming_tests']:>6}"
                  f"  {mark:<16}{r['evidence']}")
        print(f"\n  {c} of {n} have a commissioning candidate; {n-c} do not.")
        meas = [r for r in rows if r["measured"]]
        wrong = [r for r in meas if r["heuristic_said"] != r["commissioning_candidate"]]
        print(f"\n  CALIBRATION OF THE HEURISTIC AGAINST DIRECT MEASUREMENT:")
        print(f"    {len(meas)} rows have been measured directly; the heuristic")
        print(f"    disagreed with the measurement on {len(wrong)} of them"
              + (f" ({', '.join(r['id'] for r in wrong)})." if wrong else "."))
        over = [r for r in wrong if r["heuristic_said"] and not r["commissioning_candidate"]]
        under = [r for r in wrong if r["commissioning_candidate"] and not r["heuristic_said"]]
        if over:
            print(f"    {len(over)} disagreement(s) in the CONFIDENT direction "
                  f"({', '.join(r['id'] for r in over)}): the heuristic said commissioned")
            print(f"    where measurement says it is not. That is this project's house")
            print(f"    failure mode, so the {c} 'yes' rows below are UNVERIFIED, not")
            print(f"    reassurance.")
        if under:
            print(f"    {len(under)} disagreement(s) in the CAUTIOUS direction "
                  f"({', '.join(r['id'] for r in under)}): commissioned by measurement")
            print(f"    with no test naming it. Harmless here, but it means the heuristic")
            print(f"    misses offline instruments entirely.")
        print("\n  HEURISTIC, NOT A VERDICT. 'Commissioning candidate' means a test names")
        print("  the component and carries both a positive and a negative assertion. The")
        print("  panel confirms or refutes each row with tools (founder ruling 2026-08-22).")
    (REPO / "experimental_notes/data/instrument_inventory.json").write_text(
        json.dumps({"n": n, "commissioning_candidates": c, "rows": rows}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
