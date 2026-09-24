#!/usr/bin/env python3
"""FALSIFIER: e2_regression's absence is recorded ONLY when a test command
exists.  Imports the REAL target module; does not retype it.

Defect present  -> AssertionError / prints FALSIFIED
Defect absent   -> exits cleanly.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import bench.reference_runner_v3 as rr3   # THE REAL TARGET MODULE

import inspect

# WIRED 2026-09-22 (CC1). Delivered by a panel seat without it, so `--help`
# ran the whole measurement. A help flag must ANSWER, never ACT.
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
src = inspect.getsource(rr3.compute_sk)
# strip comments first -- a comment MENTIONING the old guard is not the guard
code = "\n".join(l for l in src.splitlines()
                 if not l.lstrip().startswith("#"))
i = code.index('effect_gates.append(("e2_regression"')
branch = code[i:i+400]

# 1. STRUCTURAL: the guard must not be conditional on test_cmd
if "elif test_cmd" in branch:
    print("FALSIFIED: e2 unavailability is recorded only when test_cmd is set; "
          "an unconfigured test command drops the gate with no record.")
    raise AssertionError("e2 unavailability guard is conditional on test_cmd")

# 2. BEHAVIOURAL: no test_cmd -> e2 absent -> must appear in _unavailable
target = pathlib.Path(__file__).resolve().parents[1] / "bench" / "reference_runner_v3.py"
source = target.read_text()
fix = (f"<<<< SEARCH {target}\n"
       "RK0_PI_BASE: float = 0.5\n"
       "====\n"
       "RK0_PI_BASE: float = 0.5  # calibration anchor\n"
       ">>>> REPLACE\n")
res = rr3.compute_sk(fix, source, str(target), baseline=None, test_cmd=None)
assert res.blocks_applied == 1, f"probe did not apply: {res.gate_details}"
unavail = (res.gate_details or {}).get("_unavailable")
e2 = (res.gate_details or {}).get("e2_regression", {})
print(f"tristate={res.tristate} sk={res.sk} e2_score={e2.get('score')!r} "
      f"e2_detail={e2.get('detail')!r} _unavailable={unavail!r}")
if e2.get("score") is None and (unavail is None or "e2_regression" not in unavail):
    print("FALSIFIED: e2 was dropped from E with no entry in _unavailable.")
    raise AssertionError("e2 dropped without record")

# 3. THE FIX MUST CHANGE NO VERDICT: unavailable_gates never enters E.
body = inspect.getsource(rr3.compute_sk)
uses = [l.strip() for l in body.splitlines() if "unavailable_gates" in l
        and not l.lstrip().startswith("#")]
bad = [l for l in uses
       if not (l.startswith("unavailable_gates") or ".append(" in l
               or l.startswith('details["_unavailable"]')
               or l.startswith("if unavailable_gates"))]
print("every use of unavailable_gates in compute_sk:")
for l in uses: print("     ", l)
assert not bad, f"unavailable_gates reaches a computation: {bad}"
e_line = [l for l in body.splitlines() if "E = sum((w / W)" in l][0]
assert "unavailable_gates" not in e_line, "unavailable_gates enters the E expression"
print("OK: e2 unavailability is recorded; and unavailable_gates never enters E, "
      "so the record is additive and changes no verdict.")
