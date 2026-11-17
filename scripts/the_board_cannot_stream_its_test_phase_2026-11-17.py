#!/usr/bin/env python3
"""Why the commit board's test phase is silent, and why the obvious repair disables the gate.

B202. Reproduces every figure quoted in that entry. Nothing here touches the
repository: each arm runs in a fresh temporary directory against generated
test trees, so the measurement cannot be contaminated by, or contaminate,
the real guard set.

THE POINT OF THE SCRIPT IS THE EXIT CODE, NOT THE TIMING. `OUT=$(cmd | tee ...)`
reports the status of the LAST pipeline element, so a red board becomes a green
one. That is measured here against a deliberately failing tree rather than
argued from the shell's documentation.

A FIRST VERSION OF THIS MEASUREMENT WAS WRONG AND IS KEPT AS A NAMED ARM.
Probing with 3 tests showed every arm producing output only at the end, which
reads as "streaming is impossible". 3 tests emit 3 bytes of progress and a pipe
buffer is 4-8 KiB, so no repair could have looked alive at that size: the
probe's VOLUME manufactured the result. `tiny_probe_is_uninformative()` keeps
that arm so the trap is visible rather than quietly fixed.
"""
from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys
import tempfile
import time

import numpy as np
from scipy import stats as sps

MANY = 12000          # enough progress bytes to exceed a pipe buffer
SPREAD_EVERY = 3000   # sleeps, so "during the run" is observable at all
REPEATS = 5


def _tree(d: pathlib.Path, n: int, fail_at: int | None) -> pathlib.Path:
    f = d / "test_generated.py"
    body = [
        "import pytest, time",
        f'@pytest.mark.parametrize("i", range({n}))',
        "def test_many(i):",
        f"    if i % {SPREAD_EVERY} == 0: time.sleep(0.8)",
    ]
    if fail_at is not None:
        body.append(f'    assert i != {fail_at}, "deliberate failure"')
    f.write_text("\n".join(body) + "\n", encoding="utf-8")
    return f


ARMS = {
    # name: shell body. $T is the generated test file.
    "A_current":   'OUT=$(python3 -m pytest -q -p no:cacheprovider "$T" 2>&1); CODE=$?',
    "B_tee":       'OUT=$(python3 -m pytest -q -p no:cacheprovider "$T" 2>&1 | tee /dev/stderr); CODE=$?',
    "C_tee_unbuf": 'OUT=$(PYTHONUNBUFFERED=1 python3 -m pytest -q -p no:cacheprovider "$T" 2>&1 | tee /dev/stderr); CODE=$?',
    "E_tmpfile": (
        'LOG=$(mktemp); tail -f "$LOG" 2>/dev/null & TAILPID=$!; '
        'python3 -m pytest -q -p no:cacheprovider "$T" > "$LOG" 2>&1; CODE=$?; '
        'kill "$TAILPID" 2>/dev/null; wait "$TAILPID" 2>/dev/null; '
        'OUT=$(cat "$LOG"); rm -f "$LOG"'
    ),
}


def run_arm(arm: str, n: int, fail_at: int | None) -> dict:
    """Run one arm. Returns first-output latency, exit code and captured size."""
    d = pathlib.Path(tempfile.mkdtemp(prefix="cdsfl_stream_"))
    try:
        t = _tree(d, n, fail_at)
        script = d / "arm.sh"
        script.write_text(
            "#!/bin/sh\nT=\"$1\"\n" + ARMS[arm] +
            '\nprintf "\\n@@ CODE=%s BYTES=%s FAILED=%s\\n" "$CODE" "${#OUT}" '
            '"$(printf \'%s\' "$OUT" | grep -c failed)"\n',
            encoding="utf-8")
        start = time.time()
        p = subprocess.Popen(["/bin/sh", str(script), str(t)], cwd=d,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, bufsize=1)
        first = None
        code = bytes_ = failed = None
        lines = 0
        for line in p.stdout:
            el = time.time() - start
            if line.startswith("@@ "):
                for tok in line[3:].split():
                    k, _, v = tok.partition("=")
                    if k == "CODE":
                        code = int(v)
                    elif k == "BYTES":
                        bytes_ = int(v)
                    elif k == "FAILED":
                        failed = int(v)
                continue
            lines += 1
            if line.strip() and first is None:
                first = el
        p.wait()
        return {"arm": arm, "first": first, "lines": lines, "code": code,
                "bytes": bytes_, "failed": failed, "total": time.time() - start}
    finally:
        shutil.rmtree(d, ignore_errors=True)


def tiny_probe_is_uninformative() -> dict:
    """The retired arm: 3 tests cannot fill a pipe buffer, so every arm looks dead."""
    out = {a: run_arm(a, 3, None) for a in ("A_current", "B_tee")}
    both_late = all(
        r["first"] is None or r["first"] >= r["total"] * 0.75 for r in out.values())
    return {"arms": out, "every_arm_looks_dead": both_late}


def main(argv: list[str] | None = None) -> int:
    import argparse                                        # noqa: PLC0415
    ap = argparse.ArgumentParser(description=__doc__.strip().split("\n")[0])
    ap.add_argument("--quick", action="store_true",
                    help="run the DECISIVE arm only (the exit code), so a guard "
                         "can execute this producer without paying for 38 pytest "
                         "trees. The full run is what the entry's figures come "
                         "from; --quick checks the producer still works.")
    a = ap.parse_args([] if argv is None else argv)

    print(__doc__.strip().split("\n")[0])
    print()

    if a.quick:
        print("== --quick: the decisive arm only ==")
        red = run_arm("A_current", 3, 1)["code"]
        green = run_arm("A_current", 3, None)["code"]
        tee_red = run_arm("B_tee", 3, 1)["code"]
        print(f"   current form: failing tree -> {red}, passing tree -> {green}")
        print(f"   tee form:     failing tree -> {tee_red}")
        ok = red != 0 and green == 0 and tee_red == 0
        print(f"   the pipeline loses the exit code: {tee_red == 0}")
        print(f"   quick check passed: {ok}")
        return 0 if ok else 1

    print("== the retired small probe, kept so the trap stays visible ==")
    tiny = tiny_probe_is_uninformative()
    for a, r in tiny["arms"].items():
        f = "never" if r["first"] is None else f"{r['first']:.2f}s"
        print(f"   {a:12s} first output {f:>7s} of a {r['total']:.2f}s run")
    print(f"   every arm looks dead at 3 tests: {tiny['every_arm_looks_dead']}")
    print("   -> a 3-byte progress stream cannot fill a 4-8 KiB pipe buffer,")
    print("      so this size refutes nothing. Measure at volume.")
    print()

    print(f"== liveness and capture at {MANY} tests ==")
    live = {}
    for a in ARMS:
        r = run_arm(a, MANY, None)
        live[a] = r
        f = "never" if r["first"] is None else f"{r['first']:.2f}s"
        print(f"   {a:12s} first {f:>7s}  lines {r['lines']:4d}  "
              f"code {r['code']}  captured {r['bytes']} bytes")
    sizes = {r["bytes"] for r in live.values()}
    print(f"   captured size identical across arms: {len(sizes) == 1} {sorted(sizes)}")
    print("   -> the hook post-processes OUT (pre-commit:1044-1097) to name the")
    print("      FAILED test, so a repair MUST keep OUT byte-exact.")
    print()

    print("== THE DECISIVE ARM: does the exit code survive? ==")
    print("   a failing tree. A correct gate must see a non-zero code.")
    verdicts = {}
    for a in ARMS:
        codes = []
        for _ in range(3):
            codes.append(run_arm(a, MANY, MANY // 2 + 1500)["code"])
        pass_codes = [run_arm(a, MANY, None)["code"] for _ in range(3)]
        verdicts[a] = {"failing": codes, "passing": pass_codes}
        ok = all(c != 0 for c in codes) and all(c == 0 for c in pass_codes)
        print(f"   {a:12s} failing->{codes}  passing->{pass_codes}  "
              f"distinguishes: {'YES' if ok else 'NO  <-- GATE BROKEN'}")
    print()

    print("== composability: is tee+unbuffered better than tee alone? ==")
    b = np.array([run_arm("B_tee", MANY, None)["first"] for _ in range(REPEATS)])
    c = np.array([run_arm("C_tee_unbuf", MANY, None)["first"] for _ in range(REPEATS)])
    u, pu = sps.mannwhitneyu(b, c, alternative="two-sided")
    tt, pt = sps.ttest_ind(b, c, equal_var=False)
    diff = c.mean() - b.mean()
    se = float(np.sqrt(b.var(ddof=1) / len(b) + c.var(ddof=1) / len(c)))
    print(f"   B tee alone       n={len(b)} mean {b.mean():.4f}s median {np.median(b):.4f}s")
    print(f"   C tee+unbuffered  n={len(c)} mean {c.mean():.4f}s median {np.median(c):.4f}s")
    print(f"   Mann-Whitney U={u:.1f} p={pu:.6f}   Welch t={tt:.4f} p={pt:.6f}")
    print(f"   mean difference C-B {diff:+.4f}s, 95% approx CI "
          f"[{diff - 1.96 * se:+.4f}, {diff + 1.96 * se:+.4f}]")
    shown_better = bool(pu < 0.05 and diff < 0)
    print(f"   composed form SHOWN better than the single fix: "
          f"{'YES' if shown_better else 'NO'}")
    print("   -> composability-requires-a-measurement: where a single fix performs")
    print("      as well, the single fix is PREFERRED. n is small, so this is")
    print("      'no difference demonstrated', not 'proven equal'.")
    print()

    e = verdicts["E_tmpfile"]
    e_ok = all(x != 0 for x in e["failing"]) and all(x == 0 for x in e["passing"])
    b_broken = any(x == 0 for x in verdicts["B_tee"]["failing"])
    a_silent = live["A_current"]["first"] is None
    print("== VERDICT ==")
    print(f"   current form silent through the test phase : {a_silent}")
    print(f"   tee form reports a RED board as green      : {b_broken}")
    print(f"   temp-file form keeps code AND streams      : {e_ok}")
    ok = a_silent and b_broken and e_ok
    print(f"   all 3 established: {ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
