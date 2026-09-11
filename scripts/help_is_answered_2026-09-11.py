#!/usr/bin/env python3
"""How many measurement scripts ANSWER `--help` rather than ignore it?

`measured-rate-travels-with-its-script`: this file produces the figures quoted
in `scripts/_cli_help.py` and in task A2, so they are reproducible rather than
asserted.

THE DISTINCTION THIS MAKES AND THE OLDER SURVEY DID NOT.
`scripts/measurement_scripts_only_2026-09-11.py --run` already runs every
measurement script with `--help` and counts how many "did not answer --help
cleanly". It decided that on the EXIT CODE. A script with no argument parser
ignores the flag, runs its whole measurement, and exits 0, which the exit-code
test cannot distinguish from an answer. That is the same false-zero shape as a
scanner that resolves 1 form of a thing and reports 0 for the other.

THE TEST USED HERE. `argparse` prints a line starting `usage:` for `--help`, and
so does `scripts/_cli_help.py`. A script that never parses the flag prints no
such line. The check is therefore: exit 0 AND a line beginning `usage:`.

WHAT IT CANNOT SEE, stated rather than hidden. A script could print a `usage:`
line and still do its work; nothing here would notice. The check is necessary,
not sufficient, and it is the half that is mechanically decidable.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SURVEY = REPO / "scripts" / "measurement_scripts_only_2026-09-11.py"


def _classifier():
    """The SAME classifier the survey uses, imported rather than reimplemented.

    Two copies of "which scripts are measurements" would be 2 representations of
    1 truth with no comparator, which is the shape `execute-do-not-grep` names.
    """
    spec = importlib.util.spec_from_file_location("survey", SURVEY)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.classify


def measurement_scripts() -> list[pathlib.Path]:
    classify = _classifier()
    return [p for p in sorted((REPO / "scripts").glob("*.py"))
            if classify(p)[0] == "MEASUREMENT"]


def answers_help(path: pathlib.Path, timeout: int = 180) -> tuple[bool, str]:
    """Run one script with --help. Returns (answered, why-not)."""
    try:
        r = subprocess.run([sys.executable, str(path), "--help"], cwd=REPO,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.SubprocessError as exc:
        return False, type(exc).__name__
    if r.returncode != 0:
        return False, f"exit {r.returncode}"
    from _cli_help import usage_line_present
    if usage_line_present((r.stdout or "") + (r.stderr or "")):
        return True, ""
    return False, "exit 0 but no usage line -- the flag was ignored"


def main() -> int:
    from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
    answer_help(__doc__, __file__)

    scripts = measurement_scripts()
    answered, not_answered = [], []
    for p in scripts:
        ok, why = answers_help(p)
        (answered if ok else not_answered).append((p.name, why))

    n, k = len(scripts), len(not_answered)
    print(f"MEASUREMENT scripts (classifier shared with the survey): {n}")
    print(f"  answered --help with a usage line : {len(answered)}")
    print(f"  did NOT answer                    : {k}")
    for name, why in not_answered:
        print(f"      {name}: {why}")

    if n:
        from statsmodels.stats.proportion import proportion_confint
        lo, hi = proportion_confint(k, n, method="wilson")
        lo_c, hi_c = proportion_confint(k, n, method="beta")
        import scipy.stats as st
        lo_s = st.beta.ppf(0.025, k, n - k + 1) if k else 0.0
        hi_s = st.beta.ppf(0.975, k + 1, n - k) if k < n else 1.0
        print(f"\nnot answering --help: {k}/{n} = {k / n:.4%}")
        print(f"  Wilson 95%          : [{lo:.4%}, {hi:.4%}]  (statsmodels)")
        print(f"  Clopper-Pearson 95% : [{lo_c:.4%}, {hi_c:.4%}]  (statsmodels/beta)")
        print(f"  Clopper-Pearson 95% : [{lo_s:.4%}, {hi_s:.4%}]  (scipy, agrees "
              f"to {max(abs(lo_s - lo_c), abs(hi_s - hi_c)):.1e})")
    return 1 if k else 0


if __name__ == "__main__":
    raise SystemExit(main())
