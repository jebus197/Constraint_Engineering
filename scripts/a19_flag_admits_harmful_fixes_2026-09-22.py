"""The real path, not the function in isolation: drive the acceptance suite's own
_evaluate_sk_for_findings helper with the A19 flag ON and read what happens to
R_k and to the admissible tally for the HARMFUL fix of each fixture.

Property 1 of bench/tests/test_prose_acceptance_stem.py: "A harmful fix is never
admitted, and never closes a finding."
Property 2: "an unmeasured fix may not move R_k in either direction."
"""
import os
import pathlib
import shutil
import sys
import tempfile

# `_cli_help` lives in scripts/. Locate it rather than assume a depth: the
# first version of this preamble inserted parents[1] (the repo ROOT) and so
# worked when the file was RUN (sys.path[0] is the script dir) and failed when
# it was IMPORTED, which is how 13 scripts stopped importing on 2026-09-24.
for _cand in (pathlib.Path(__file__).resolve().parent,
              *pathlib.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

# REPO-RELATIVE, 2026-09-24 (panel). This file carried an ABSOLUTE path to the
# maintainer's checkout, so run from any other tree -- including the very
# sandbox reviewing a change to compute_sk -- it silently measured the LIVE
# repository instead of the tree under test, and on any other machine it
# crashed. Its own sibling (a19_veto_only_prose_sk) states the rule this file
# broke: "Repo-relative on purpose: no operator-specific ROOT."
ROOT = pathlib.Path(os.environ.get("CE_ROOT",
                                   pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(ROOT))

import bench.tests.test_prose_acceptance_stem as T                # noqa: E402
from bench.reference_runner_v3 import _evaluate_sk_for_findings   # noqa: E402
from bench.tests.fixtures.stem.stem_fixtures import load_all      # noqa: E402


def main() -> None:
    # MOVED INTO main(), 2026-09-24 (panel). This work ran at MODULE level, so
    # any tool that merely imported the file built fixture trees and spawned
    # ruff and bandit -- RED on test_no_tracked_script_writes_at_import. Two
    # mechanical wrap attempts broke on the mid-file guard; this is the proper
    # form: imports stay importable, work runs only when the file is run.
    tmp = pathlib.Path(tempfile.mkdtemp())
    stats = {}
    print(f"{'fixture':<24} {'fix':<8} {'flag':<5} {'tristate':<12} "
          f"{'sk':>7} {'R_old':>7} {'R_new':>7} {'admitted'}")
    print("-" * 92)
    try:
        for fx in load_all():
            bl = T._real_baseline(fx)
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
                        reg, fx.document, str(copy), bl,
                        round_idx=1, score_prose_listings=flag)
                    e = reg.entries[cid]
                    r = e.get("sk_result") or {}
                    print(f"{fx.doc_path.name:<24} {label:<8} {str(flag):<5} "
                          f"{r.get('tristate','-'):<12} {r.get('sk',0):>7.4f} "
                          f"{r.get('R_old',float('nan')):>7.4f} "
                          f"{r.get('R_new',float('nan')):>7.4f} "
                          f"{stats.get('admissible', stats.get('admitted','?'))}")
        print("-" * 92)
        print("stats keys:", sorted(stats.keys()))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    answer_help(__doc__, __file__)
    main()
