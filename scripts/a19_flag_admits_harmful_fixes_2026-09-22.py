"""The real path, not the function in isolation: drive the acceptance suite's own
_evaluate_sk_for_findings helper with the A19 flag ON and read what happens to
R_k and to the admissible tally for the HARMFUL fix of each fixture.

Property 1 of bench/tests/test_prose_acceptance_stem.py: "A harmful fix is never
admitted, and never closes a finding."
Property 2: "an unmeasured fix may not move R_k in either direction."

★ THIS FILE'S NAME IS NOT SUPPORTED BY ITS OWN OUTPUT, and the name is kept only
because renaming it would break the citations that point here. Re-measured
2026-10-17 over all 5 fixtures, both fix kinds and both flag states -- 20 rows:

    harmful fix, flag OFF : 5 of 5 NO_SCORE    (passes through UNSCORED)
    harmful fix, flag ON  : 3 of 5 REJECTED, 2 of 5 NO_SCORE
    correct fix, flag OFF : 5 of 5 NO_SCORE
    correct fix, flag ON  : 5 of 5 NO_SCORE    (0 wrongly rejected)

So the flag does not ADMIT a harmful fix -- the `admitted` column is 0 on all 20
rows, which is Property 1 holding in BOTH states. What the flag changes is that
3 of the 5 harmful fixes become actively REJECTED instead of silently unscored.
The state that lets a harmful prose fix through without an opinion is the flag
being OFF, which is the opposite of what the filename says.

WHAT THE EVIDENCE DOES NOT SETTLE, and why the default is still the founder's
call. 0 of 5 correct fixes were wrongly rejected, and 0 of 5 bounds the
false-rejection rate only at [0.0000%, 43.4482%] on a 95% Wilson interval. A
default that decides which fixes reach a verdict should not be flipped on an
upper bound that wide, so the measurement is reported and the ruling is left
where task A19 already puts it.

THE `nan` IN THE R_old AND R_new COLUMNS IS EXPECTED, not a defect. Those keys
are absent from `sk_result` on a REJECTED outcome because Property 2 governs an
UNMEASURED fix, and a rejected fix has been measured. Reading them as a fault
was an error made and corrected on 2026-10-17.
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
