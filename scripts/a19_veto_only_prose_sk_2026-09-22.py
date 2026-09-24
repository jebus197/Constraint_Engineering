"""FALSIFIER: with `score_prose_listings=True`, S_k must never ADMIT on a
prose target -- it may convict (REJECTED) or abstain (NO_SCORE), and R_k must
hold on every unadmitted fix.

Run on the tree of 2026-09-22 BEFORE the veto-only repair, this raises
AssertionError on the first fixture: all 5 harmful and all 5 correct fixes
scored ADMISSIBLE (sk 0.5333..1.0000) and moved R_k 0.5000 -> as low as
0.3667, refuting the acceptance suite's Property 1 (5/5) and Property 2
(10/10). On the repaired tree it exits cleanly. Companion producer of the
original measurement: scripts/a19_flag_admits_harmful_fixes_2026-09-22.py
(which drives the same path but only prints).

EXTENDED 2026-09-24 (panel): section 2 constructs a population BEYOND the 5
archived fixtures -- .md/.txt/.rst targets, listing-bearing and listing-free,
clean and harmful fixes, both flag states -- and asserts the same 3 properties
over all of it: never ADMISSIBLE on a non-Python target, R_k held on every
unadmitted fix, and the finding left OPEN. This is the adjudicated branch
removal's dominance check run over inputs its 10-row producer never saw.

Repo-relative on purpose: no operator-specific ROOT, no Wolfram, no network.
"""
import contextlib
import io
import os
import pathlib
import shutil
import sys
import tempfile

# `_cli_help` lives in scripts/. Locate it rather than assume a depth.
for _cand in (pathlib.Path(__file__).resolve().parent,
              *pathlib.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

ROOT = pathlib.Path(os.environ.get("CE_ROOT",
                                   pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(ROOT))

import bench.tests.test_prose_acceptance_stem as T                 # noqa: E402
from bench.reference_runner_v3 import (                            # noqa: E402
    SK_ADMISSIBLE, SK_NO_SCORE, SK_REJECTED, TARGET_KIND_PYTHON,
    _capture_baseline, _evaluate_sk_for_findings, apply_sk_to_rk,
    compute_sk, resolve_target_kind,
)
from bench.tests.fixtures.stem.stem_fixtures import load_all       # noqa: E402

_LISTING_BODY = (
    "import math\n"
    "\n"
    "\n"
    "def area(radius: float) -> float:\n"
    "    return math.pi * radius * radius\n"
)
_ANCHOR = "    return math.pi * radius * radius"

_DOC_WITH_LISTING = (
    "# Design note\n\nThe area helper under review:\n\n"
    "```python\n" + _LISTING_BODY + "```\n\nClosing prose.\n"
)
_DOC_PURE_PROSE = "# Design note\n\nNo code here at all, only argument.\n"

#: (label, replacement) pairs applied at the anchor line. "clean" leaves the
#: static sweep spotless -- the case where the SURVIVING branch and the REMOVED
#: branch could differ if the survivor paid out; "high" plants a bandit HIGH,
#: where the survivor convicts and the removed branch would only have
#: abstained; "delete_fence" removes the listing wholesale (g0).
_FIXES = (
    ("clean", _ANCHOR + "\n\n\ndef circumference(radius: float) -> float:\n"
              "    return 2.0 * math.pi * radius"),
    ("high", _ANCHOR + "\nimport subprocess\n"
             "subprocess.call(\"rm -rf /\", shell=True)"),
)


def _sr(path, old, new):
    return f"<<<< SEARCH {path}\n{old}\n==== REPLACE\n{new}\n>>>>\n"


def constructed_population(check) -> None:
    """Section 2: the never-admit rule over targets the fixtures never covered."""
    tmp = pathlib.Path(tempfile.mkdtemp())
    rows = 0
    try:
        for suffix in (".md", ".txt", ".rst"):
            doc = _DOC_WITH_LISTING
            path = tmp / f"note{suffix}"
            path.write_text(doc)
            kind, _why = resolve_target_kind(str(path), doc)
            check(kind != TARGET_KIND_PYTHON,
                  f"POPULATION {suffix}: constructed prose target resolved as "
                  f"Python; the population is not testing the prose path")
            baseline = _capture_baseline(doc, str(path))
            for label, replacement in _FIXES:
                for flag in (False, True):
                    with contextlib.redirect_stdout(io.StringIO()):
                        res = compute_sk(_sr(path, _ANCHOR, replacement), doc,
                                         str(path), baseline=baseline,
                                         score_prose_listings=flag)
                    rows += 1
                    check(res.tristate != SK_ADMISSIBLE,
                          f"POPULATION {suffix}/{label}/flag={flag}: ADMITTED "
                          f"on a non-Python target (sk={res.sk})")
                    if res.tristate == SK_NO_SCORE:
                        r_new, _ = apply_sk_to_rk(0.5, res.tristate)
                        check(r_new == 0.5,
                              f"POPULATION {suffix}/{label}: NO_SCORE moved R_k")
                    print(f"  population {suffix:<5} {label:<12} flag={flag!s:<5} "
                          f"-> {res.tristate}")
            # A fix that deletes the fence entirely: g0 must reject, not admit.
            with contextlib.redirect_stdout(io.StringIO()):
                res = compute_sk(
                    _sr(path, "```python\n" + _LISTING_BODY + "```", "gone"),
                    doc, str(path), baseline=baseline, score_prose_listings=True)
            rows += 1
            check(res.tristate == SK_REJECTED,
                  f"POPULATION {suffix}/delete_fence: expected REJECTED, "
                  f"got {res.tristate}")
            print(f"  population {suffix:<5} delete_fence flag=True  -> {res.tristate}")

        # Pure prose, no listing: the flag must change nothing.
        pure = tmp / "pure.md"
        pure.write_text(_DOC_PURE_PROSE)
        for flag in (False, True):
            with contextlib.redirect_stdout(io.StringIO()):
                res = compute_sk(_sr(pure, "only argument.", "only evidence."),
                                 _DOC_PURE_PROSE, str(pure),
                                 baseline=_capture_baseline(_DOC_PURE_PROSE, str(pure)),
                                 score_prose_listings=flag)
            rows += 1
            check(res.tristate == SK_NO_SCORE,
                  f"POPULATION pure-prose/flag={flag}: expected NO_SCORE, "
                  f"got {res.tristate}")

        # Through the round-loop entry point: a REJECTED conviction and a
        # NO_SCORE abstention must both leave the finding OPEN and R_k unmoved.
        for label, replacement in _FIXES:
            d = tmp / f"e2e-{label}"
            d.mkdir(exist_ok=True)
            copy = d / "note.md"
            copy.write_text(_DOC_WITH_LISTING)
            reg = T.FindingRegistry()
            cid = T._register(reg, _sr(copy, _ANCHOR, replacement), copy)
            with contextlib.redirect_stdout(io.StringIO()):
                stats = _evaluate_sk_for_findings(
                    reg, _DOC_WITH_LISTING, str(copy),
                    _capture_baseline(_DOC_WITH_LISTING, str(copy)),
                    round_idx=1, score_prose_listings=True)
            e = reg.entries[cid]
            r = e.get("sk_result") or {}
            rows += 1
            check(stats["admissible"] == 0,
                  f"POPULATION e2e/{label}: admissible tally moved")
            check(e["status"] in ("OPEN", "CONFIRMED", "CONTESTED"),
                  f"POPULATION e2e/{label}: finding closed by an unadmitted fix "
                  f"(status={e['status']})")
            r_old, r_new = r.get("R_old"), r.get("R_new")
            check(r_new is None or r_new == r_old,
                  f"POPULATION e2e/{label}: R_k moved {r_old} -> {r_new} "
                  f"on tristate {r.get('tristate')}")
            print(f"  population e2e   {label:<12} -> {r.get('tristate')} "
                  f"(status {e['status']}, R held)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"  population rows: {rows}")


def main() -> None:
    # MOVED INTO main(), 2026-09-24 (panel): this work ran at module level, so
    # importing the file built trees and spawned ruff and bandit.
    failures = []

    def check(cond, msg):
        if not cond:
            failures.append(msg)

    tmp = pathlib.Path(tempfile.mkdtemp())
    try:
        for fx in load_all():
            baseline = T._real_baseline(fx)
            for label, patches in (("harmful", fx.harmful_fix),
                                   ("correct", fx.correct_fix)):
                for flag in (False, True):
                    d = tmp / f"{fx.key}-{label}-{flag}"
                    d.mkdir(parents=True, exist_ok=True)
                    copy = d / fx.doc_path.name
                    shutil.copy(fx.doc_path, copy)
                    reg = T.FindingRegistry()
                    cid = T._register(reg, T._fix_text(fx, patches, copy), copy)
                    stats = _evaluate_sk_for_findings(
                        reg, fx.document, str(copy), baseline,
                        round_idx=1, score_prose_listings=flag)
                    r = reg.entries[cid].get("sk_result") or {}
                    tri = r.get("tristate")
                    r_old, r_new = r.get("R_old"), r.get("R_new")
                    print(f"{fx.key:<12} {label:<8} flag={flag!s:<5} "
                          f"{tri:<12} R {r_old} -> {r_new}")
                    if tri == SK_ADMISSIBLE or stats["admissible"] != 0:
                        check(False, f"{fx.key}/{label}/flag={flag}: ADMITTED ({tri})")
                    if r_old is not None and r_new is not None and r_new != r_old:
                        check(False, f"{fx.key}/{label}/flag={flag}: R_k moved "
                                     f"{r_old} -> {r_new} on an unadmitted fix")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("-" * 72)
    constructed_population(check)

    if failures:
        print("FALSIFIED")
        raise AssertionError(
            "S_k admitted or moved risk on a prose target:\n  "
            + "\n  ".join(failures))
    print("OK: 20 archived evaluations + constructed population "
          "(3 suffixes x 5 rows + 2 pure-prose + 2 e2e), 0 admissions, "
          "R_k held in every case.")


if __name__ == "__main__":
    answer_help(__doc__, __file__)
    main()
