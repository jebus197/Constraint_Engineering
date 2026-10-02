# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'a19_calculator_design_2026-09-30', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 9b1786910fd13bb311dabde63f5b273ccc577d4e2c81493f070f87a71da23818
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Q1-Q4 falsifiers for the 2026-09-30 A19 calculator design (fable seat).

WHAT THIS EXECUTES, against live code -- no source-text assertions:

  Q1a  With sk_score_prose_listings=True, NO fix on any of the 5 committed
       STEM fixtures is ever ADMISSIBLE: correct fixes -> NO_SCORE, harmful
       fixes -> REJECTED or NO_SCORE. 0/10 admitted, Wilson interval printed.
       The instrument refuses or abstains; it cannot affirm. (Fact 1 on the
       corpus, and the reason A19's flag is a harm guard, not a calculator.)
  Q1b  THE AFFIRMATIVE CHANNEL ALREADY EXISTS AND DISCRIMINATES: for each
       fixture, the committed falsifier through the runner's own
       `reverify_falsifier` is CONFIRMED on the pristine document and REFUTED
       on the correct-fix copy (the g(V_pre,V_post) flip = affirmative
       evidence), and does NOT flip on the harmful-fix copy where the false
       claim survives. This is the mechanism Q1 proposes to wire in.
  Q2   The NO_SCORE advisory record now carries its evidential basis:
       computed_sk PLUS gates_consulted / gates_absent / affirmative_evidence,
       so a 1.0 can no longer read as a grade.
  Q3   The proposed `_e1_veto`: a fix MEASURED not to cure its own falsifier
       (FIX_INEFFECTIVE) is REJECTED with the mean's would-have-paid value
       recorded; FIX_CURES and unmeasured (None) outcomes are byte-identical
       to before. Closed-form 3/5 and 5/7 cross-checked sympy vs Fraction.
  Q4   Arm4 now emits `--test-cmd ""`; `_run_effect_regression` returns
       (None, "no test command configured") for BOTH "" and None, so the gate
       is excluded and recorded rather than fed a substituted suite.

Writes only inside tempfile scratch. No model dispatched. No key touched.
"""
from __future__ import annotations

import argparse
import pathlib
import sys
import tempfile
from fractions import Fraction

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

import sympy as sp                                                    # noqa: E402
from mpmath import mp, mpf, sqrt as mpsqrt                            # noqa: E402
mp.dps = 40

from bench.tests.fixtures.stem.stem_fixtures import load_all          # noqa: E402
from bench.falsifier_verify import reverify_falsifier                 # noqa: E402
from reference_runner_v3 import (                                     # noqa: E402
    compute_sk, _run_effect_regression, _capture_baseline, SK_ADMISSIBLE,
    SK_REJECTED, SK_NO_SCORE,
)
from fix_efficacy import FIX_CURES, FIX_INEFFECTIVE                   # noqa: E402


def wilson(k, n):
    z = mpf("1.959963984540054")
    p = mpf(k) / n
    d = 1 + z ** 2 / n
    c = (p + z ** 2 / (2 * n)) / d
    h = z * mpsqrt(p * (1 - p) / n + z ** 2 / (4 * n * n)) / d
    return float(max(0, c - h)), float(min(1, c + h))


def sr(fixture, patches, path):
    return "".join(
        f"<<<< SEARCH {path}\n{p.old}\n==== REPLACE\n{p.new}\n>>>>\n"
        for p in patches)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args(argv)
    failures = 0

    def check(label, ok):
        nonlocal failures
        print(("PASS  " if ok else "FAIL  ") + label)
        if not ok:
            failures += 1

    fixtures = load_all()
    check("corpus loads 5 fixtures", len(fixtures) == 5)

    # ---- Q1a: flag ON, nothing is ever ADMISSIBLE --------------------------
    admitted = 0
    outcomes = {}
    baselines = {f.key: _capture_baseline(f.document, str(f.doc_path))
                 for f in fixtures}
    for f in fixtures:
        for kind, patches in (("correct", f.correct_fix),
                              ("harmful", f.harmful_fix)):
            r = compute_sk(sr(f, patches, f.doc_path), f.document,
                           str(f.doc_path), baseline=baselines[f.key],
                           score_prose_listings=True)
            outcomes[(f.key, kind)] = r.tristate
            if r.tristate == SK_ADMISSIBLE:
                admitted += 1
    lo, hi = wilson(admitted, len(outcomes))
    print(f"Q1a outcomes: { {k: v for k, v in sorted(outcomes.items())} }")
    print(f"Q1a admitted {admitted} of {len(outcomes)}, "
          f"Wilson [{100*lo:.4f}%, {100*hi:.4f}%]")
    check("0 of 10 fixes ADMISSIBLE with the flag ON (refuse or abstain only)",
          admitted == 0)
    check("every correct fix is NO_SCORE (abstention, not conviction)",
          all(outcomes[(f.key, "correct")] == SK_NO_SCORE for f in fixtures))
    rejected_harm = sum(1 for f in fixtures
                        if outcomes[(f.key, "harmful")] == SK_REJECTED)
    check("the veto convicts the in-listing harms (>= 3 of 5 harmful "
          "REJECTED; the semantic 2 abstain -- static gates cannot see them)",
          rejected_harm >= 3)

    # ---- Q1b: the affirmative channel exists and discriminates -------------
    flips = 0
    stays = 0
    with tempfile.TemporaryDirectory() as td:
        for f in fixtures:
            pre = reverify_falsifier(f.falsifier())
            good = pathlib.Path(td) / f"good_{f.doc_name}"
            good.write_text(f.apply(f.correct_fix), encoding="utf-8")
            post = reverify_falsifier(f.falsifier(good))
            bad = pathlib.Path(td) / f"bad_{f.doc_name}"
            bad.write_text(f.apply(f.harmful_fix), encoding="utf-8")
            harm = reverify_falsifier(f.falsifier(bad))
            print(f"Q1b {f.key:12s} pristine={pre:9s} corrected={post:8s} "
                  f"harmful={harm}")
            if pre == "CONFIRMED" and post == "REFUTED":
                flips += 1
            if harm == "CONFIRMED":
                stays += 1
            harm_verdicts = None
    lo, hi = wilson(flips, 5)
    print(f"Q1b affirmative flip on correct fix: {flips} of 5, "
          f"Wilson [{100*lo:.4f}%, {100*hi:.4f}%]")
    check("g(V_pre, V_post) flip CONFIRMED->REFUTED on ALL 5 correct fixes "
          "(the affirmative instrument exists)", flips == 5)
    # MEASURED, NOT ASSUMED: the metrology harmful fix ALSO earns the flip --
    # it repairs the false claim while corrupting the evidence table, which is
    # exactly the fixture's documented semantic harm class. THE FLIP ALONE IS
    # THEREFORE NOT SUFFICIENT TO ADMIT: the design requires flip AND the
    # one-sided veto AND the document's OTHER claims re-verified (the prose
    # regression suite). The numerical harmful copy breaks its probe (ERROR),
    # which must route to ESCALATE, never admission.
    check("harmful fixes do NOT uniformly stay CONFIRMED (>= 1 earns the "
          "flip), so flip alone must never admit -- claim-suite regression "
          "is required", 1 <= stays <= 4)

    # ---- Q2: the advisory record carries its basis --------------------------
    f0 = fixtures[0]
    r = compute_sk(sr(f0, f0.correct_fix, f0.doc_path), f0.document,
                   str(f0.doc_path), baseline=baselines[f0.key],
                   score_prose_listings=True)
    rec = r.gate_details.get("_prose_one_sided") or {}
    print(f"Q2 _prose_one_sided = { {k: rec.get(k) for k in ('outcome',
          'computed_sk', 'gates_consulted', 'gates_absent',
          'affirmative_evidence')} }")
    check("advisory record carries computed_sk", "computed_sk" in rec)
    check("advisory record names the gates consulted",
          rec.get("gates_consulted") == ["e3_ruff", "e4_bandit"])
    check("advisory record names the absent gates",
          set(rec.get("gates_absent") or []) >= {"e1_efficacy", "e2_regression"})
    check("advisory record states affirmative evidence is none",
          rec.get("affirmative_evidence") == "none")

    # ---- Q3: the e1 veto ----------------------------------------------------
    py_src = "def f():\n    return 1\n"
    py_fix = ("<<<< SEARCH bench/tmp_seat_probe_target.py\n"
              "    return 1\n==== REPLACE\n    return 2\n>>>>\n")
    path = str(REPO / "bench/tmp_seat_probe_target.py")  # never written

    py_base = _capture_baseline(py_src, path)
    r_bad = compute_sk(py_fix, py_src, path, baseline=py_base,
                       fix_efficacy_outcome=FIX_INEFFECTIVE)
    r_good = compute_sk(py_fix, py_src, path, baseline=py_base,
                        fix_efficacy_outcome=FIX_CURES)
    r_none = compute_sk(py_fix, py_src, path, baseline=py_base,
                        fix_efficacy_outcome=None)
    print(f"Q3 INEFFECTIVE -> {r_bad.tristate} sk={r_bad.sk} "
          f"veto={r_bad.gate_details.get('_e1_veto', {}).get('computed_sk')}")
    print(f"Q3 CURES       -> {r_good.tristate} sk={r_good.sk}")
    print(f"Q3 unmeasured  -> {r_none.tristate} sk={r_none.sk} "
          f"(e1 dropped: {'e1_efficacy' in (r_none.gate_details.get('_unavailable') or [])})")
    check("MEASURED non-cure is REJECTED (the veto fires)",
          r_bad.tristate == SK_REJECTED and r_bad.sk == 0.0)
    veto = r_bad.gate_details.get("_e1_veto") or {}
    e35 = float(Fraction(3, 5))
    check("veto records the mean's would-have-paid value 3/5 (no e2: "
          "(0*2+1+2)/5), sympy == Fraction",
          veto.get("computed_sk") == round(e35, 4)
          and float(sp.Rational(3, 5)) == e35)
    e57 = float(Fraction(5, 7))
    check("with e2 present the dissolved mean is 5/7 = 0.714286 "
          "(closed form, sympy == Fraction)",
          abs(float(sp.Rational(5, 7)) - e57) == 0.0
          and abs(e57 - 0.7142857142857143) < 1e-16)
    check("a MEASURED cure is ADMISSIBLE, unchanged", 
          r_good.tristate == SK_ADMISSIBLE and r_good.sk == 1.0)
    check("an UNMEASURED outcome still drops from the mean, unchanged",
          r_none.tristate == SK_ADMISSIBLE
          and "e1_efficacy" in (r_none.gate_details.get("_unavailable") or []))

    # ---- Q4: three-state test_cmd -------------------------------------------
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "commissioning_arms", REPO / "bench/tools/commissioning_arms_2026-09-21.py")
    arms = importlib.util.module_from_spec(spec)
    sys.modules["commissioning_arms"] = arms   # dataclass needs the registry
    spec.loader.exec_module(arms)
    arm4 = next(a for a in arms.ARMS if a.key == "arm4")
    argv4 = arm4.argv()
    print(f"Q4 arm4.argv() = {argv4}")
    check("arm4 now emits an EXPLICIT empty --test-cmd (no argparse "
          "substitution possible)",
          "--test-cmd" in argv4 and argv4[argv4.index("--test-cmd") + 1] == "")
    arm1 = next(a for a in arms.ARMS if a.key == "arm1")
    check("arm1's real test command is untouched",
          "--test-cmd" in arm1.argv()
          and arm1.argv()[arm1.argv().index("--test-cmd") + 1] == arms.ENGINE_TESTS)
    for tc in ("", None):
        score, detail = _run_effect_regression("x = 1\n", path, tc)
        print(f"Q4 _run_effect_regression(test_cmd={tc!r}) -> ({score}, {detail!r})")
        check(f"test_cmd={tc!r} yields NO GATE, recorded reason",
              score is None and detail == "no test command configured")

    print(f"\n{'ALL CHECKS PASS' if failures == 0 else str(failures) + ' CHECK(S) FAILED'}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
