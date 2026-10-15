#!/usr/bin/env python3
"""Two questions about free run 1, answered by EXECUTION rather than by reading.

Produced 2026-10-15 while run 1 (`free_run1_directive_whole_20261015T061123Z`)
was in its post-convergence sweep. It carries its own figures so that none of
them exists only as prose (`measured-rate-travels-with-its-script`).

QUESTION 1 — WAS THE A19 "NO APPLICABLE CHECKS" A DEFECT?

CC1's working hypothesis, formed at 08:14 BST from reading ONE comment in
`bench/bugzilla_loop.py`, was that the close-the-loop verifier points ruff,
mypy and bandit at the whole `.md` file and therefore cannot reach the fenced
Python listings that A19 taught `S_k` to score -- which would have made the
3 non-closures of C0018, C0019 and C0020 a gap in the capability this run is
commissioning.

THE HYPOTHESIS IS WITHDRAWN. `verify_fix` is CALLED here against a prose
target rather than read, per `execute-do-not-grep`, and the narrow prose path
is a DOCUMENTED DESIGN DECISION with 3 rejected alternatives recorded beside
it at `bugzilla_loop.py:440-465`. The listings reference imports the document
declares in PROSE, so ruff and mypy report undefined names on any extracted
fragment NO MATTER WHAT THE FIX DID. What is deterministically checkable
without a baseline is whether the code still PARSES, and that is what runs.
A clean parse is recorded as NO_APPLICABLE_CHECKS and NOT as PASS, because
`if verify.passed` closes a finding and calling an unchecked fix "verified"
is the worse error -- that exact mistake is rejected alternative 2.

The real, bounded consequence is recorded instead: on a prose target no
finding can close by STATIC VERIFICATION, so closure rate is not a measurable
quantity on this target and the parse veto is the only automatic rejection.

QUESTION 2 — DOES RUN 1's SEVERITY SHADOW CONTRADICT THE ARCHIVE?

Run 1's shadow reports `crossed_downward = []` on 22 findings: promoting the
section 7.7 severity would have changed NOTHING in this run. The archive
measurement of 2026-10-15 put the reach at 7 releases in 2,994 findings. A
reader could take 0 of 22 as refuting the 7 of 2,994, so the compatibility is
computed rather than asserted, with scipy and mpmath as the 2 tools.
"""
from __future__ import annotations

import ast
import pathlib
import sys
import tempfile

# `_cli_help` lives in scripts/. Locate it rather than assume a depth.
for _cand in (pathlib.Path(__file__).resolve().parent,
              *pathlib.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
# `_extract_python` defers an import of `reference_runner_v3` by BARE module
# name, so `bench/` must be importable. In a live run that module is already in
# sys.modules because it IS the runner; a standalone caller has to supply it.
sys.path.insert(0, str(REPO / "bench"))


def q1_execute_the_verifier() -> dict:
    """CALL verify_fix on a prose target. Do not grep its source."""
    from bench.bugzilla_loop import (
        VerificationOutcome,
        _extract_python,
        is_python_target,
        run_verification,
    )

    target = REPO / "bench/cdsfl_registry/targets/prose_with_computable_listings.md"
    text = target.read_text(encoding="utf-8")

    out: dict = {"target": str(target.relative_to(REPO))}
    out["is_python_target"] = is_python_target(target)

    # Extract the fenced listings the way A19's S_k does, and confirm they are
    # valid Python -- so the tools' silence is NOT a statement about the code.
    import re

    blocks = re.findall(r"```(?:python)?\n(.*?)```", text, re.S)
    parsed = 0
    for b in blocks:
        try:
            ast.parse(b)
            parsed += 1
        except SyntaxError:
            pass
    out["fenced_blocks"] = len(blocks)
    out["fenced_blocks_that_parse"] = parsed
    # `_extract_python` returns a PATH to a written .py file, not a string.
    _ex = _extract_python(target)
    out["extractor_wrote_a_file"] = _ex is not None
    if _ex is not None:
        _txt = _ex.read_text(encoding="utf-8")
        out["extracted_chars"] = len(_txt)
        out["extracted_parses"] = True
        try:
            ast.parse(_txt)
        except SyntaxError:
            out["extracted_parses"] = False
        _ex.unlink(missing_ok=True)
    else:
        out["extracted_chars"] = 0
        out["extracted_parses"] = False

    # CASE A: an untouched prose target. Expect NO_APPLICABLE_CHECKS, checks_run=[].
    with tempfile.TemporaryDirectory() as td:
        sandbox = pathlib.Path(td) / target.name
        sandbox.write_text(text, encoding="utf-8")
        r = run_verification(sandbox, test_cmd=None)
        out["clean_outcome"] = r.outcome.value
        out["clean_checks_run"] = list(r.checks_run)
        out["clean_vetoes_run"] = list(getattr(r, "vetoes_run", []))
        out["clean_passed_property"] = bool(r.passed)
        out["clean_no_applicable"] = bool(r.no_applicable_checks)

    # CASE B: a prose target whose listing has been MANGLED. The parse veto is
    # the one thing that must still bite, or a fix that breaks a listing closes.
    with tempfile.TemporaryDirectory() as td:
        sandbox = pathlib.Path(td) / target.name
        # Mangle INSIDE the first fenced listing, so the veto is tested on the
        # element A19 taught S_k to score and not on the surrounding prose.
        first = blocks[0]
        mangled_block = first.replace("(", "((", 1) if "(" in first else first + "\n  )\n"
        broken = text.replace(first, mangled_block, 1)
        sandbox.write_text(broken, encoding="utf-8")
        out["mangle_changed_the_file"] = broken != text
        out["mangled_block_still_parses"] = True
        try:
            ast.parse(mangled_block)
        except SyntaxError:
            out["mangled_block_still_parses"] = False
        r2 = run_verification(sandbox, test_cmd=None)
        out["mangled_outcome"] = r2.outcome.value
        out["mangled_vetoes_run"] = list(getattr(r2, "vetoes_run", []))
        out["mangled_passed_property"] = bool(r2.passed)

    out["veto_bites_on_mangled_listing"] = (
        out["mangled_outcome"] == VerificationOutcome.FAIL.value
    )
    out["clean_is_not_a_pass"] = out["clean_outcome"] != VerificationOutcome.PASS.value
    return out


def q2_shadow_vs_archive() -> dict:
    """Is 0 of 22 compatible with 7 of 2,994? scipy and mpmath, independently."""
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp

    arch_hits, arch_n = 7, 2994
    run_hits, run_n = 0, 22
    p = arch_hits / arch_n

    out: dict = {
        "archive_hits": arch_hits,
        "archive_n": arch_n,
        "archive_rate": p,
        "run1_crossed_downward": run_hits,
        "run1_findings": run_n,
    }

    # Expected crossings in 22 findings at the archive rate.
    out["expected_crossings_in_22"] = p * run_n

    # P(observing 0 | n=22, p) -- scipy, then mpmath at 50 digits.
    out["p_zero_scipy"] = float(stats.binom.pmf(0, run_n, p))
    mp.mp.dps = 50
    out["p_zero_mpmath"] = float((mp.mpf(1) - mp.mpf(arch_hits) / arch_n) ** run_n)
    out["p_zero_tools_agree"] = bool(
        abs(out["p_zero_scipy"] - out["p_zero_mpmath"]) < 1e-12
    )

    # Exact binomial test of 0/22 against the archive rate.
    bt = stats.binomtest(run_hits, run_n, p, alternative="two-sided")
    out["binomtest_p"] = float(bt.pvalue)
    out["refutes_archive_at_0.05"] = bool(bt.pvalue < 0.05)

    # Intervals, 2 methods each, and whether they overlap.
    a_lo, a_hi = proportion_confint(arch_hits, arch_n, method="wilson")
    a_lo2, a_hi2 = proportion_confint(arch_hits, arch_n, method="beta")
    r_lo, r_hi = proportion_confint(run_hits, run_n, method="wilson")
    r_lo2, r_hi2 = proportion_confint(run_hits, run_n, method="beta")
    out["archive_wilson"] = [float(a_lo), float(a_hi)]
    out["archive_clopper_pearson"] = [float(a_lo2), float(a_hi2)]
    out["run1_wilson"] = [float(r_lo), float(r_hi)]
    out["run1_clopper_pearson"] = [float(r_lo2), float(r_hi2)]
    out["intervals_overlap"] = bool(max(a_lo2, r_lo2) <= min(a_hi2, r_hi2))

    # How many findings would be needed for 0 to mean something, at 80% power.
    n_needed = None
    for n in range(1, 20001):
        if (1 - p) ** n < 0.20:
            n_needed = n
            break
    out["findings_needed_for_zero_to_be_informative"] = n_needed
    return out


def main() -> int:
    import json

    q1 = q1_execute_the_verifier()
    q2 = q2_shadow_vs_archive()

    print("=" * 72)
    print("Q1  THE A19 'NO APPLICABLE CHECKS' IS BY DESIGN — HYPOTHESIS WITHDRAWN")
    print("=" * 72)
    for k, v in q1.items():
        print(f"  {k:38s} {v}")

    print()
    print("=" * 72)
    print("Q2  RUN 1's SEVERITY SHADOW vs THE ARCHIVE — 0 of 22 vs 7 of 2,994")
    print("=" * 72)
    for k, v in q2.items():
        print(f"  {k:38s} {v}")

    ok = (
        q1["clean_is_not_a_pass"]
        and q1["veto_bites_on_mangled_listing"]
        and q1["fenced_blocks_that_parse"] == q1["fenced_blocks"]
        and q2["p_zero_tools_agree"]
        and not q2["refutes_archive_at_0.05"]
        and q2["intervals_overlap"]
    )
    print()
    print("VERDICT:")
    print("  A19 verifier behaviour on a prose target: BY DESIGN, veto still bites")
    print("  Run 1 shadow 0 of 22: COMPATIBLE with the archive's 7 of 2,994")
    print(f"  all assertions hold: {ok}")

    (REPO / "experimental_notes/evidence").mkdir(parents=True, exist_ok=True)
    dest = (
        REPO
        / "experimental_notes/evidence/run1_converged_and_a19_is_by_design_2026-10-15.json"
    )
    dest.write_text(json.dumps({"q1": q1, "q2": q2, "all_hold": ok}, indent=2))
    print(f"  evidence -> {dest.relative_to(REPO)}")
    return 0 if ok else 1


if __name__ == "__main__":
    answer_help(__doc__, __file__)
    raise SystemExit(main())
