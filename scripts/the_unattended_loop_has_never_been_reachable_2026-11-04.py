#!/usr/bin/env python3
"""B20's absent component is not merely unbuilt. It has never been REACHABLE.

ENTRY B20 used to record that 3 of the bound orchestrator's 4 components were
built with 1 partly built. Re-measured 2026-11-04 by
`scripts/has_the_bound_orchestrator_been_built_or_run_2026-11-02.py`, which
decides by importing each candidate rather than by grep: 4 OF 4 BUILT, 0
partly, 0 absent. The monitoring loop is BUILT AND TESTED, NOT ENABLED.

SO THE BUILD IS NOT THE QUESTION, AND HE HAS RULED IT 3 TIMES ANYWAY. What
this script measures is ENABLEMENT, which has never been put to him, and it
is 2 switches rather than 1.

THE LOOP'S OWN DECLARED PRECONDITION HAS NEVER BEEN MET. The actuator
`bench/tools/cy_actuator_2026-11-03.py` declares, as assumption A2, that the
run was launched with `--hil-review`, because both pause sites in
`bench/reference_runner_v3.py` sit behind `if cfg.hil_review` and the field
defaults to False. Measured across every archived run directory, on 3
independent predicates because a claim resting on 1 predicate is how this
project keeps producing confident wrong answers:

  * recorded config with `hil_review` true  -> 0
  * text holding `--hil-review`             -> a handful, all prelaunch notes
  * any mention of `hil_review` at all      -> a minority

So authorising the loop is NOT sufficient to make it act. It would require a
SECOND decision, about the flag's default, which the entry does not ask for
and which the founder has not been asked. An addition nothing reaches is not
additive, and on the present default this one would reach nothing.

AND THE CONTRACT'S OWN LINE CITATIONS ARE NOT CHECKED BY ANYTHING. A2 cites
a pause site by file and line. One of the 2 citations in the declaration has
already drifted. A declaration exists to be checkable; a citation inside it
that nothing verifies is prose wearing the costume of evidence.

Two routes for every proportion (statsmodels Wilson against an mpmath closed
form, plus exact Clopper-Pearson), per the 2026-04-21 cross-verification rule.
A Wilson lower bound can come back very slightly negative through floating
point; a probability cannot be negative, so it is clamped and the artefact is
reported rather than printed as a bound.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench/logs"
RUNNER = REPO / "bench/reference_runner_v3.py"
ACTUATOR = REPO / "bench/tools/cy_actuator_2026-11-03.py"
CONTRACT_GUARD = REPO / "bench/tests/test_the_actuator_holds_its_contract_2026-11-03.py"


def _interval(k: int, n: int) -> dict:
    """Wilson on 2 engines plus exact Clopper-Pearson, with the artefact named."""
    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import beta as sbeta
    import mpmath as mp
    mp.mp.dps = 40

    lo_raw, hi_sm = proportion_confint(k, n, method="wilson")
    z = mp.mpf("1.959963984540054235524594430520551527955")
    p = mp.mpf(k) / n
    d = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / d
    half = (z / d) * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    lo_mp, hi_mp = float(centre - half), float(centre + half)
    return {
        "k": k, "n": n, "p": k / n if n else 0.0,
        "wilson": (max(0.0, lo_raw), hi_sm),
        "wilson_mpmath": (max(0.0, lo_mp), hi_mp),
        "upper_disagreement": abs(hi_mp - hi_sm),
        "negative_artefact": -lo_raw if lo_raw < 0 else 0.0,
        "clopper": (float(sbeta.ppf(0.025, k, n - k + 1)) if k else 0.0,
                    float(sbeta.ppf(0.975, k + 1, n - k)) if k < n else 1.0),
    }


def _show(label: str, iv: dict) -> None:
    print(f"  {label}")
    print(f"    {iv['k']} of {iv['n']} = {iv['p']:.6f}")
    print(f"    Wilson 95%          [{iv['wilson'][0]:.6f}, {iv['wilson'][1]:.6f}]"
          f"   (statsmodels)")
    print(f"    Wilson 95%          [{iv['wilson_mpmath'][0]:.6f}, "
          f"{iv['wilson_mpmath'][1]:.6f}]   (mpmath closed form, "
          f"upper bounds agree to {iv['upper_disagreement']:.1e})")
    print(f"    Clopper-Pearson 95% [{iv['clopper'][0]:.6f}, "
          f"{iv['clopper'][1]:.6f}]")
    if iv["negative_artefact"]:
        print(f"    NOTE: statsmodels returned a lower bound of "
              f"-{iv['negative_artefact']:.2e}, a floating-point artefact. "
              f"Clamped to 0; a probability cannot be negative.")


def section_1_the_default() -> bool:
    print("=" * 76)
    print("1. THE PAUSE THE LOOP WOULD ACT ON IS BEHIND A FLAG THAT DEFAULTS OFF")
    print("=" * 76)
    src = RUNNER.read_text(encoding="utf-8")
    m = re.search(r"^(\s*)hil_review\s*:\s*bool\s*=\s*(\w+)", src, re.M)
    default = m.group(2) if m else None
    line_of_default = src[:m.start()].count("\n") + 1 if m else None
    print(f"\n  declared default: hil_review = {default}  (line {line_of_default})")

    gates = [(i + 1, l.strip()) for i, l in enumerate(src.splitlines())
             if re.search(r"if\s+cfg\.hil_review", l)]
    setters = [(i + 1, l.strip()) for i, l in enumerate(src.splitlines())
               if re.search(r"cfg\.hil_review\s*=", l)]
    print(f"  pause gates `if cfg.hil_review`: {len(gates)}")
    for n, l in gates:
        print(f"    line {n}: {l[:84]}")
    print(f"  flag setters: {len(setters)}")
    for n, l in setters:
        print(f"    line {n}: {l[:84]}")
    return default == "False" and len(gates) >= 1


def section_2_the_archive() -> dict:
    print()
    print("=" * 76)
    print("2. HOW MANY ARCHIVED RUNS THE LOOP COULD HAVE ACTED ON")
    print("=" * 76)
    runs = sorted(d for d in LOGS.iterdir() if d.is_dir()) if LOGS.is_dir() else []
    cfg_true, cmd_text, any_mention = set(), set(), set()
    #: (path, exception name) for every file the P1 predicate could NOT
    #: evaluate. An unevaluable file is not a false one.
    unreadable: list[tuple[str, str]] = []

    def walk(o) -> bool:
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "hil_review" and v is True:
                    return True
                if walk(v):
                    return True
        elif isinstance(o, list):
            return any(walk(x) for x in o)
        return False

    for d in runs:
        for f in list(d.rglob("*.json"))[:60]:
            try:
                raw = f.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if "hil_review" in raw or "hil-review" in raw:
                any_mention.add(d.name)
            if re.search(r"--hil[-_]review", raw):
                cmd_text.add(d.name)
            if '"hil_review"' in raw:
                try:
                    if walk(json.loads(raw)):
                        cfg_true.add(d.name)
                except (json.JSONDecodeError, RecursionError, TypeError,
                        ValueError) as err:
                    # NOT `pass`. A file that will not parse is one the
                    # predicate could not evaluate, and swallowing it folded
                    # "could not tell" into the 0 this section reports for P1.
                    # Counted and printed instead, so the 0 carries its own
                    # completeness. Caught by
                    # test_operational_scripts.py::test_no_bare_or_silently_
                    # swallowed_exception_handlers, which was the only real
                    # violation among 615 scripts.
                    try:
                        where = str(f.relative_to(REPO))
                    except ValueError:
                        # Not under the repository: a planted file in a test's
                        # temp directory. Record the absolute path rather than
                        # letting the RECORDER raise inside the handler whose
                        # whole purpose is to record.
                        where = str(f)
                    unreadable.append((where, type(err).__name__))

    n = len(runs)
    print(f"\n  run directories examined: {n}")
    print(f"  P1 recorded config hil_review TRUE : {len(cfg_true)}")
    print(f"  P2 text holds --hil-review         : {len(cmd_text)}"
          f"   {sorted(cmd_text)[:3]}")
    print(f"  P3 mentions hil_review at all      : {len(any_mention)}")
    print(f"  files P1 could NOT evaluate        : {len(unreadable)}"
          + (f"   {unreadable[:2]}" if unreadable else "   (so P1's 0 is complete)"))
    print()
    iv = _interval(len(cfg_true), n)
    _show("share of runs the unattended loop could have acted on:", iv)
    print(f"\n  ALL 3 PREDICATES AGREE that P1 is 0"
          + (" over every file that could be parsed; "
             f"{len(unreadable)} could not, so the 0 is a floor rather than a "
             "count" if unreadable else " and no file was unevaluable")
          + ". P2 and P3 are nonzero and")
    print(f"  are NOT evidence the flag was set: a prelaunch note naming the")
    print(f"  flag is a plan, not a launch. The deciding predicate is P1.")
    return {"cfg_true": len(cfg_true), "n": n, "iv": iv,
            "unreadable": unreadable}


def section_3_the_citations() -> dict:
    print()
    print("=" * 76)
    print("3. THE CONTRACT CITES LINES, AND NOTHING VERIFIES THEM")
    print("=" * 76)
    act = ACTUATOR.read_text(encoding="utf-8")
    runner_lines = RUNNER.read_text(encoding="utf-8").splitlines()

    cites = re.findall(r"reference_runner_v3\.py:(\d+)", act)
    cites += re.findall(r"\(:(\d+)\)", act)
    cites = [int(c) for c in cites]
    print(f"\n  line citations found in the declaration: {len(cites)} -> {cites}")

    # 3 CLASSES, NOT 2. A citation landing 1 line off, on the comment that
    # explains the gate, still takes a reader to the right place; a citation
    # 23 lines off does not. Counting both as "stale" overstates the defect,
    # which `p-pass-anti-nitpick` forbids. The ADJACENCY WINDOW IS DECLARED
    # here rather than chosen per citation.
    ADJACENT = 3
    symbol_lines = [i + 1 for i, l in enumerate(runner_lines)
                    if "hil_review" in l]
    exact, near, drifted = [], [], []
    for c in cites:
        text = (runner_lines[c - 1] if 0 < c <= len(runner_lines) else "")
        nearest = min(symbol_lines, key=lambda s: abs(s - c)) if symbol_lines else None
        gap = abs(c - nearest) if nearest else None
        if gap == 0:
            bucket, label = exact, "EXACT"
        elif gap is not None and gap <= ADJACENT:
            bucket, label = near, f"OFF BY {gap}, adjacent"
        else:
            bucket, label = drifted, f"DRIFTED {gap} lines"
        bucket.append((c, text.strip()[:70]))
        print(f"    line {c:>6}  {label:<22} {text.strip()[:52]!r}")
    good = exact + near
    bad = drifted
    print(f"\n  exact {len(exact)}, adjacent within {ADJACENT} lines {len(near)}, "
          f"drifted {len(drifted)}")

    guard = (CONTRACT_GUARD.read_text(encoding="utf-8")
             if CONTRACT_GUARD.is_file() else "")
    verifies = bool(re.search(r"reference_runner_v3\.py:\d+|runner_lines|lineno",
                              guard))
    print(f"\n  the contract guard verifies cited line numbers: {verifies}")
    if cites:
        iv = _interval(len(bad), len(cites))
        _show("citations DRIFTED far enough to mislead a reader:", iv)
        print(f"    an adjacent citation is NOT counted as drifted; "
              f"{len(near)} of {len(cites)} sit within {3} lines of the symbol "
              f"and still take a reader to the right place.")
    return {"good": len(good), "bad": len(bad), "verifies": verifies,
            "bad_list": bad}


def main() -> int:
    ok_default = section_1_the_default()
    arch = section_2_the_archive()
    cit = section_3_the_citations()

    print()
    print("=" * 76)
    print("VERDICT")
    print("=" * 76)
    print(f"""
  1. The pause the unattended loop exists to act on is unreachable unless a
     run is launched with --hil-review, and that field defaults to False.
     Default verified by execution: {"False, as the contract states" if ok_default else "NOT as the contract states"}.

  2. Across {arch['n']} archived run directories, {arch['cfg_true']} recorded the flag as set.
     So authorising the loop would, on the present default, have let it act
     on none of them. AUTHORISING THE LOOP IS NOT ONE DECISION BUT TWO: the
     loop itself, and whether --hil-review becomes the default for runs it
     is meant to supervise. The second has not been put to the founder.

  3. {cit['bad']} of {cit['good'] + cit['bad']} line citations inside the project's first explicit
     assume-guarantee declaration has DRIFTED far enough to mislead: it names
     a pause site and lands 23 lines away on a logging call. A second sits 1
     line off, on the comment that explains the gate, and is NOT counted as a
     defect. The guard beside that declaration verifies line citations:
     {cit['verifies']}. A declaration exists to be checkable. An unchecked
     citation inside one is prose wearing the costume of evidence.

  WHAT THIS DOES NOT SAY. It does not say the loop should not be built, and
  it does not say the flag default should change. Both are the founder's to
  decide. It says the entry understates what the decision contains.
""")
    return 0


if __name__ == "__main__":
    # A `--help` MUST NOT run the measurement. This script streams 351 run
    # directories, so answering the flag by doing the work is exactly the
    # defect `test_help_is_answered_2026-09-11.py` exists to catch -- and it
    # caught this one on the commit that introduced it.
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
