#!/usr/bin/env python3
r"""B37: the nested suite was never unserialised, and the deadlock was the
protection being switched off.

HIS PROPOSAL, 2026-10-28, verbatim: *"Can this test not be run sequentially,
similar to your sq MC command? Why risk choking up my 8GB machine and making it
unusable, or risk the tests failing to complete, when the tests can be run
sequentially, to the same effect?"*

HIS CONCERN IS RIGHT AND HIS PROPOSED MECHANISM IS NOT THE ONE THAT APPLIES, and
the difference matters because serialising would have changed nothing.

3 HYPOTHESES WERE TESTED. 2 ARE REFUTED.

  1. REFUTED -- "the nested run is parallel and should be serialised".
     `hooks/pre-commit` line 357 runs `python3 -m pytest -q -p no:cacheprovider
     $GUARDS`. No `-n`, no xdist. `pytest.ini` carries no `addopts`, so the outer
     run is serial too. BOTH runs were already sequential. There is nothing to
     serialise.

  2. REFUTED -- "a fork inside a threaded process deadlocks on an inherited
     lock". This is a real failure class and `timeout_method = thread` does make
     every pytest process multi-threaded, so it was the strongest candidate. But
     Python 3.13 on macOS defaults to the `spawn` start method, nothing in the
     tree calls `set_start_method` or `get_context`, and a spawned child shares
     no inherited lock state. Ruled out.

  3. SUPPORTED -- "the per-test timeout is the protection, and that run had
     replaced it with a whole-run limit". B37's own record says the deadlocking
     run was made "WITH THE LIMIT RAISED TO 1800 SECONDS FOR THE WHOLE RUN".
     A whole-run limit does not reclaim an individual test, so the per-test
     backstop was absent exactly when the hang happened.

THE MEASUREMENT THAT DECIDED IT, and it refuted a 4th hypothesis of mine on the
way. I expected that a THREAD-method timeout could not reclaim a process blocked
in `os.waitpid`, since a thread cannot interrupt another thread's syscall. That
is wrong: pytest-timeout's thread method tears down the whole process. Measured
against a deliberately unbounded `subprocess.run(["sleep", "25"])` under a
3-second thread-method limit: the run completed in 4 seconds of wall clock, so
the protection reclaims a blocked child about 1 second over its limit.

WHAT THE ANSWER TO HIS RULING IS, THEREFORE. A test MAY legitimately run the
hook's full guard list, because the cost is bounded and known, PROVIDED the
per-test limit is never replaced by a whole-run limit. That is the one thing
that must not be done again, and it is now guarded rather than remembered.

THE RESIDUAL RISK, WHICH IS REAL BUT IS NOT THE MECHANISM. 13 of 22 subprocess
launches across the 3 nested-hook files carry no `timeout=`, 0.590909 Wilson
[0.387348, 0.767442], all 13 in
`bench/tests/test_precommit_restages_repairs_2026-09-11.py`. A hang in one of
those costs the whole per-test budget and fails the test rather than the single
call, so bounding them is defence in depth. It does not change the deadlock
story.
"""
from __future__ import annotations

import ast
import json
import pathlib
import subprocess
import sys
import tempfile
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
NESTED = (
    "bench/tests/test_precommit_guard_2026-09-09.py",
    "bench/tests/test_precommit_restages_repairs_2026-09-11.py",
    "bench/tests/test_precommit_gate_cost_2026-09-10.py",
)
RUNNERS = {"run", "check_call", "check_output", "Popen", "call"}


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    from scipy.stats import norm
    z = float(norm.ppf(0.975))
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return ((c - h) / d, (c + h) / d)


def nested_run_is_serial() -> dict:
    """Hypothesis 1. Read the hook's own invocation and pytest.ini's addopts."""
    hook = (REPO / "hooks" / "pre-commit").read_text(encoding="utf-8")
    line = next((l for l in hook.splitlines() if "-m pytest" in l), "")
    ini = (REPO / "pytest.ini").read_text(encoding="utf-8")
    return {
        "hook_pytest_invocation": line.strip(),
        "hook_uses_xdist": ("-n " in line) or ("xdist" in line),
        "ini_has_addopts": any(l.strip().startswith("addopts")
                               for l in ini.splitlines()),
        "verdict": "both runs are already serial"
                   if not (("-n " in line) or ("xdist" in line)) else "PARALLEL",
    }


def fork_deadlock_is_possible() -> dict:
    """Hypothesis 2. The start method decides it."""
    import multiprocessing as mp
    forced = []
    me = pathlib.Path(__file__).resolve()
    for p in REPO.rglob("*.py"):
        # EXCLUDE THIS FILE. The first version matched its own source, because a
        # scanner that searches for `set_start_method` contains that string, and
        # it reported itself as forcing a start method -- flipping the verdict
        # from "ruled out" to "POSSIBLE" on its own text. Same class as
        # `execute-do-not-grep`: a text scan is not evidence about behaviour,
        # and a text scan that includes itself is not even evidence about text.
        if p.resolve() == me:
            continue
        if "/logs/" in str(p) or "/.git/" in str(p):
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "set_start_method" in txt or "mp.get_context(" in txt:
            forced.append(str(p.relative_to(REPO)))
    method = mp.get_start_method(allow_none=True) or mp.get_start_method()
    return {"default_start_method": method,
            "files_forcing_a_start_method": forced,
            "verdict": "ruled out -- a spawned child inherits no lock state"
                       if method == "spawn" and not forced else "POSSIBLE"}


def thread_timeout_reclaims_a_blocked_child() -> dict:
    """Hypothesis 4, mine, and it is REFUTED. Executed, not reasoned about."""
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d)
        (p / "test_blocked.py").write_text(
            "import subprocess\n\n\n"
            "def test_unbounded_child():\n"
            "    subprocess.run(['sleep', '25'])\n", encoding="utf-8")
        (p / "pytest.ini").write_text(
            "[pytest]\ntimeout = 3\ntimeout_method = thread\n", encoding="utf-8")
        t0 = time.time()
        r = subprocess.run([sys.executable, "-m", "pytest", "test_blocked.py",
                            "-q", "-p", "no:cacheprovider"],
                           cwd=p, capture_output=True, text=True, timeout=120)
        elapsed = time.time() - t0
    return {"limit_s": 3, "child_sleep_s": 25,
            "wall_clock_s": round(elapsed, 1),
            "reclaimed": elapsed < 20,
            "overshoot_s": round(elapsed - 3, 1),
            "timed_out_marker_present": "Timeout" in (r.stdout + r.stderr),
            "verdict": "the thread method DOES reclaim a blocked child; my "
                       "hypothesis that it could not is refuted"
                       if elapsed < 20 else "it does NOT reclaim"}


def unbounded_launches() -> dict:
    """The residual risk, counted by AST rather than by line proximity.

    A first attempt counted with `grep -A3` and got 3 of 16 for one file where
    the AST says 13 of 16. Line proximity is the wrong instrument for a question
    about call boundaries.
    """
    total = 0
    bare: list[dict] = []
    for rel in NESTED:
        tree = ast.parse((REPO / rel).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            if getattr(fn, "attr", None) in RUNNERS and \
                    getattr(getattr(fn, "value", None), "id", None) == "subprocess":
                total += 1
                if "timeout" not in {k.arg for k in node.keywords if k.arg}:
                    bare.append({"file": rel, "line": node.lineno})
    lo, hi = wilson(len(bare), total)
    return {"launches": total, "unbounded": len(bare),
            "rate": len(bare) / total if total else 0.0,
            "wilson95": [lo, hi], "sites": bare}


def per_test_limit_is_present() -> dict:
    """The one thing that must not be switched off again."""
    ini = (REPO / "pytest.ini").read_text(encoding="utf-8")
    timeout = None
    method = None
    for line in ini.splitlines():
        s = line.strip()
        if s.startswith("timeout ") or s.startswith("timeout="):
            timeout = s.split("=", 1)[-1].strip()
        if s.startswith("timeout_method"):
            method = s.split("=", 1)[-1].strip()
    marks = {}
    for rel in NESTED:
        txt = (REPO / rel).read_text(encoding="utf-8")
        marks[rel] = [l.strip() for l in txt.splitlines()
                      if "mark.timeout" in l]
    return {"per_test_timeout": timeout, "timeout_method": method,
            "explicit_marks": marks,
            "verdict": "present" if timeout else "ABSENT -- the deadlock "
                                                "configuration"}


def main() -> int:
    # A REAL PARSER, INSIDE main(), AND THE PLACEMENT IS THE POINT.
    # A module-level `answer_help` call satisfies the writes-answer-help ratchet
    # in test_help_never_acts and BREAKS the import probe in
    # test_operational_scripts, which imports every parser-less script in a
    # subprocess with a stray argv: `answer_help` refuses the unrecognised
    # argument and the module exits 2 during import. Measured 2026-10-28, after
    # my own first fix did exactly that to 3 scripts. `answers_help` accepts "an
    # ArgumentParser constructed anywhere", so a parser HERE satisfies both:
    # `--help` is answered without running the scan, and an import reaches no
    # argv at all because main() is not called at import time.
    import argparse
    argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0]).parse_args()
    print("== B37, and his proposal measured against 3 hypotheses ==\n")
    out = {}

    print("-- hypothesis 1: the nested run is parallel and needs serialising")
    out["serial"] = nested_run_is_serial()
    for k, v in out["serial"].items():
        print(f"   {k}: {v}")

    print("\n-- hypothesis 2: a fork inside a threaded process deadlocks")
    out["fork"] = fork_deadlock_is_possible()
    for k, v in out["fork"].items():
        print(f"   {k}: {v}")

    print("\n-- hypothesis 4 (mine): a thread-method timeout cannot reclaim a "
          "blocked child")
    out["reclaim"] = thread_timeout_reclaims_a_blocked_child()
    for k, v in out["reclaim"].items():
        print(f"   {k}: {v}")

    print("\n-- the protection that must never be switched off")
    out["limit"] = per_test_limit_is_present()
    for k, v in out["limit"].items():
        print(f"   {k}: {v}")

    print("\n-- residual risk: unbounded subprocess launches (AST-counted)")
    out["unbounded"] = unbounded_launches()
    u = out["unbounded"]
    print(f"   {u['unbounded']} of {u['launches']} launches carry no timeout = "
          f"{u['rate']:.6f}  Wilson [{u['wilson95'][0]:.6f}, "
          f"{u['wilson95'][1]:.6f}]")
    for s in u["sites"]:
        print(f"      {s['file']}:{s['line']}")

    dest = REPO / "experimental_notes" / "data" / \
        "nested_suite_bounded_2026-10-28.json"
    dest.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
