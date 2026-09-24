"""The real path, not the function in isolation: drive the acceptance suite's own
_evaluate_sk_for_findings helper with the A19 flag ON and read what happens to
R_k and to the admissible tally for the HARMFUL fix of each fixture.

Property 1 of bench/tests/test_prose_acceptance_stem.py: "A harmful fix is never
admitted, and never closes a finding."
Property 2: "an unmeasured fix may not move R_k in either direction."
"""
import sys, pathlib, tempfile, shutil
ROOT = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
sys.path.insert(0, str(ROOT))
import bench.tests.test_prose_acceptance_stem as T           # noqa: E402
from bench.reference_runner_v3 import _evaluate_sk_for_findings  # noqa: E402
from bench.tests.fixtures.stem.stem_fixtures import load_all     # noqa: E402

# WIRED 2026-09-24 (CC1). This file works at MODULE level, so there is no
# main() for a help flag to intercept. Answered here, before any work.
# `_cli_help` lives in scripts/. Locate it rather than assume a depth: the
# first version of this preamble inserted parents[1] (the repo ROOT) and so
# worked when the file was RUN (sys.path[0] is the script dir) and failed when
# it was IMPORTED, which is how 13 scripts stopped importing on 2026-09-24.
import sys as _sys, pathlib as _pl  # noqa: E402
for _cand in (_pl.Path(__file__).resolve().parent, *_pl.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        _sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402
# GUARDED 2026-09-24 (CC1). At MODULE level this read the HOST's argv:
# the operational-script probe imports via `python3 -c "..." <path>`, so
# sys.argv[1] was the script's own path and the guard refused it, exit 2.
# `__name__` is still "__main__" when the file is RUN, so `--help` answers
# exactly as before; on IMPORT it is skipped and argv is never inspected.
if __name__ == "__main__":
    answer_help(__doc__, __file__)
tmp = pathlib.Path(tempfile.mkdtemp())
print(f"{'fixture':<24} {'fix':<8} {'flag':<5} {'tristate':<12} {'sk':>7} {'R_old':>7} {'R_new':>7} {'admitted'}")
print("-" * 92)
for fx in load_all():
    bl = T._real_baseline(fx)
    for label, patches in (("harmful", fx.harmful_fix), ("correct", fx.correct_fix)):
        for flag in (False, True):
            d = tmp / f"{fx.key}-{label}-{flag}"
            d.mkdir(parents=True, exist_ok=True)
            copy = d / fx.doc_path.name
            shutil.copy(fx.doc_path, copy)
            reg = T.FindingRegistry()
            cid = T._register(reg, T._fix_text(fx, patches, copy), copy)
            stats = _evaluate_sk_for_findings(reg, fx.document, str(copy), bl,
                                              round_idx=1,
                                              score_prose_listings=flag)
            e = reg.entries[cid]
            r = e.get("sk_result") or {}
            print(f"{fx.doc_path.name:<24} {label:<8} {str(flag):<5} "
                  f"{r.get('tristate','-'):<12} {r.get('sk',0):>7.4f} "
                  f"{r.get('R_old',float('nan')):>7.4f} {r.get('R_new',float('nan')):>7.4f} "
                  f"{stats.get('admissible', stats.get('admitted','?'))}")
print("-" * 92)
print("stats keys:", sorted(stats.keys()))
shutil.rmtree(tmp, ignore_errors=True)
