#!/usr/bin/env python3
"""Do falsifiers READ their targets, or is the discrimination control's method at fault?

THE QUESTION, raised by the live run of 2026-11-02. Of 15 discrimination-control
outcomes, 0 were determinate. 11 said: *"this falsifier behaves identically when
the target file is replaced wholesale, so the control cannot reach the target it
reads and cannot test whether it discriminates. Nothing is concluded."*

TWO READINGS, AND THE CONTROL CORRECTLY REFUSED TO CHOOSE:
  (a) the falsifier's verdict is INDEPENDENT of the file it claims to verify --
      the most consequential defect class this project could have; or
  (b) the control cannot instrument the read, an apparatus limitation that says
      nothing about the falsifier.

THIS SCRIPT SETTLES IT, and the answer is (b). The method is 3 cases run on a
COPY in a temp directory, never the live tree:

  1. the target UNCHANGED
  2. the target with the DEFECT REPAIRED -- preconditions intact, ANSWER changed
  3. the target replaced WHOLESALE -- the control's own intervention

MEASURED 2026-11-02 on C0001 of severity_bounds_validation_20261102T004713Z:
  unchanged         -> FALSIFIED
  defect repaired   -> NOT FALSIFIED
  wholesale swap    -> ERROR, KeyError: 'round_dispersion'

So the verdict MOVES CLEANLY when the answer changes: the falsifier reads and
discriminates, and (a) is REFUTED. A wholesale swap destroys the falsifier's
PRECONDITIONS -- the fenced python block it execs -- so it CRASHES instead of
returning a different verdict, and a crash is indistinguishable from "did not
falsify" to the control. The control is testing discrimination with an
intervention that breaks the instrument rather than changing the answer.

AND A FIRST VERSION OF THIS TEST NEARLY GOT THE RIGHT ANSWER FROM BROKEN
EVIDENCE. Its case 2 reported ERROR, which I almost read as "the verdict moved".
It was my own edit's artefact: a fallback regex `/\\s*n\\b` hit `sum(values) / n`,
the MEAN line, before the variance line, so it broke the mean instead of
repairing the defect. The repair must be surgical and is asserted to apply
exactly once.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import statistics
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
TARGET = REPO / "bench" / "cdsfl_registry" / "targets" / "prose_with_computable_listings.md"

#: The defect C0001 names, and its repair. Both asserted to match exactly once,
#: because a loose edit is how the first attempt broke the mean.
DEFECT = "    return sum((v - mean) ** 2 for v in values) / n"
REPAIR = "    return sum((v - mean) ** 2 for v in values) / (n - 1)"

FAILURES: list[str] = []


def _verdict(workdir: pathlib.Path, target_text: str, code: str) -> tuple[str, int, str]:
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / TARGET.name).write_text(target_text)
    (workdir / "f.py").write_text(code)
    r = subprocess.run([sys.executable, "f.py"], cwd=workdir,
                       capture_output=True, text=True, timeout=120)
    out = (r.stdout or "").strip()
    if "FALSIFIED" in out:
        v = "FALSIFIED"
    elif r.returncode != 0:
        v = "ERROR"
    else:
        v = "NOT FALSIFIED"
    tail = (r.stderr or "").strip().splitlines()
    return v, r.returncode, (tail[-1] if tail else "")


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="does_a_falsifier_read_its_target_2026-11-02.py",
        description="Settle whether a falsifier reads its target, by changing the "
                    "ANSWER rather than swapping the file. Runs in a temp copy; "
                    "the live tree is never written.")
    ap.add_argument("--run-dir", default=str(
        REPO / "bench" / "logs"
        / "severity_bounds_validation_20261102T004713Z_20261102T004713Z"),
        help="a run directory holding runner_state.json")
    ap.add_argument("--entry", default="C0001",
                    help="the canonical id whose falsifier_code is tested")
    a = ap.parse_args()

    st = pathlib.Path(a.run_dir) / "runner_state.json"
    if not st.is_file():
        raise SystemExit(f"no runner_state.json under {a.run_dir}")
    s = json.loads(st.read_text())
    ents = (s.get("registry") or {}).get("entries") or {}
    items = list(ents.values()) if isinstance(ents, dict) else list(ents)
    hit = [e for e in items if e.get("canonical_id") == a.entry]
    if not hit:
        raise SystemExit(f"{a.entry} is not in {a.run_dir}")
    e = hit[0]
    code = (e.get("falsifier_code") or "").strip()
    if not code:
        raise SystemExit(f"{a.entry} carries no falsifier_code, so nothing to run")

    orig = TARGET.read_text()
    print("=" * 72)
    print("DOES A FALSIFIER READ ITS TARGET?")
    print("=" * 72)
    print(f"  entry        : {a.entry}   recorded verdict: {e.get('falsifier_verdict')}")
    print(f"  target       : {TARGET.name}, {len(orig)} chars")
    print(f"  falsifier    : {len(code)} chars")

    # the defect itself, shown rather than described
    blocks = re.findall(r"```python\n(.*?)```", orig, re.S)
    ns: dict = {}
    # ★ THE FAILURE LEAVES A TRACE, 2026-11-02. This was `except Exception: pass`
    # and `TestNoScriptSwallowsAnErrorIntoSilence` was right to refuse it -- on
    # the same night a memory file was written arguing that a swallowed
    # exception is not a record of a failure but a failure that looks like data.
    # A block that will not execute is EXPECTED here, because the target's
    # listings are prose fragments, so the handler stays; what changes is that
    # it SAYS which block failed and why.
    skipped: list[str] = []
    for i, b in enumerate(blocks):
        try:
            exec(b, ns)                                    # noqa: S102
        except Exception as _bx:                           # noqa: BLE001
            skipped.append(f"block {i}: {type(_bx).__name__}: {_bx}")
    if skipped:
        print(f"  {len(skipped)} of {len(blocks)} listing(s) did not execute, "
              f"which is expected for a prose target:")
        for s in skipped:
            print(f"      {s[:110]}")
    vals = [1.0, 2.0, 3.0, 4.0, 5.0]
    if "round_dispersion" in ns:
        got = ns["round_dispersion"](vals)
        print(f"\n  round_dispersion({vals}) = {got}")
        print(f"    sample variance (what its docstring promises) = "
              f"{statistics.variance(vals)}")
        print(f"    population variance (what it returns)         = "
              f"{statistics.pvariance(vals)}")
        if abs(got - statistics.pvariance(vals)) > 1e-12:
            FAILURES.append("the target no longer carries the C0001 defect, so the "
                            "unchanged case cannot produce FALSIFIED and this test "
                            "proves nothing")

    if orig.count(DEFECT) != 1:
        FAILURES.append(f"the defect line matches {orig.count(DEFECT)} times, not 1; "
                        f"a loose edit is how the first attempt broke the mean")
        repaired = orig
    else:
        repaired = orig.replace(DEFECT, REPAIR, 1)

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="cdsfl_read_test_"))
    try:
        print("\n  the 3 cases, each on a COPY:")
        v1, rc1, e1 = _verdict(tmp / "1_unchanged", orig, code)
        print(f"    unchanged        -> {v1:14s} rc={rc1} {e1[:48]}")
        v2, rc2, e2 = _verdict(tmp / "2_answer_changed", repaired, code)
        print(f"    answer changed   -> {v2:14s} rc={rc2} {e2[:48]}")
        v3, rc3, e3 = _verdict(tmp / "3_wholesale_swap",
                               "# a different document\n\nnothing here.\n", code)
        print(f"    wholesale swap   -> {v3:14s} rc={rc3} {e3[:48]}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        assert not tmp.exists(), "the temp directory was not removed"

    print()
    print("=" * 72)
    if v1 == "FALSIFIED" and v2 == "NOT FALSIFIED":
        print("  THE FALSIFIER READS AND DISCRIMINATES. Its verdict moves cleanly")
        print("  when the ANSWER changes, so the reading that falsifiers ignore")
        print("  their targets is REFUTED.")
    else:
        FAILURES.append(f"the verdict did NOT move cleanly: unchanged={v1}, "
                        f"answer changed={v2}. Either the repair missed or the "
                        f"falsifier really does not discriminate -- re-measure "
                        f"before relying on either reading")
    if v3 == "ERROR":
        print("  AND THE CONTROL'S METHOD IS THE FAULT. A wholesale swap destroys")
        print("  the falsifier's preconditions, so it CRASHES rather than returning")
        print("  a different verdict -- and a crash is indistinguishable from")
        print("  'did not falsify' to the control.")
    else:
        FAILURES.append(f"a wholesale swap gave {v3}, not ERROR, so it no longer "
                        f"demonstrates why the control's method fails")

    print()
    print(f"FAILURES: {len(FAILURES)}")
    for f in FAILURES:
        print("  -", f)
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
