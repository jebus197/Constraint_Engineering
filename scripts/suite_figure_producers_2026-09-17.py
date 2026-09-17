#!/usr/bin/env python3
"""Which producer form actually backs the suite figures in `resources/RECOVERY.md`.

READ-ONLY. Writes nothing, spawns nothing. `classify()` in
`scripts/measurement_scripts_only_2026-09-11.py` should call this a MEASUREMENT.

WHY THIS EXISTS. Task A23 shipped
`bench/tests/test_recovery_session_state_is_current_2026-09-11.py`, whose rule
`TestASuiteFigureNamesItsProducer` is `measured-rate-travels-with-its-script`
applied to the one document a post-compaction reader trusts most. The rule is
right. Its PATTERN was not: it recognised a producer only in the form
`scripts/<name>.py`, and a full-suite figure has no such producer -- the thing
that produces "7,493 passed" is a pytest invocation.

That is not a hypothesis about what people might write. This file's own history
already writes it the honest way: the SESSION STATE blocks of 2026-09-08 and
2026-09-06 both name `python3 -m pytest bench/tests -q --netguard-strict` beside
their figure. Under the shipped pattern those honest paragraphs are OFFENDERS,
and the only ways to go green are to cite a script that did not produce the
number, or to stop reporting the suite. Both are worse than the defect.

So this is a measurement, not a preference: it counts how many suite-figure
paragraphs in the whole file are backed by each form. The broadening in the
guard is admitted only because this count says the pytest-command form is the
one the record actually uses.

Run:  python3 scripts/suite_figure_producers_2026-09-17.py
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RECOVERY = REPO / "resources" / "RECOVERY.md"

#: Copied in shape from the guard under test, thousands separators included.
SUITE_FIGURE = re.compile(r"\b\d{1,3}(?:,\d{3})*\s+(?:passed|failed)\b")
#: The form the shipped guard accepts.
NAMES_A_SCRIPT = re.compile(r"scripts/[\w./-]+\.py")
#: A COMPLETE, re-runnable pytest invocation: the interpreter, `-m pytest`, and
#: at least one further argument (a target or a flag). A bare mention of the
#: word "pytest" does NOT match, which is what keeps this from being a hole.
NAMES_A_PYTEST_RUN = re.compile(r"python3?\s+-m\s+pytest\s+(?:-\S+|\S*/\S*|\S+\.py)")


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def paragraphs_with_figures(text: str) -> list:
    return [p for p in re.split(r"\n\s*\n", text) if SUITE_FIGURE.search(p)]


def survey(path: Path = RECOVERY) -> dict:
    text = path.read_text(encoding="utf-8")
    paras = paragraphs_with_figures(text)
    script = [p for p in paras if NAMES_A_SCRIPT.search(p)]
    pytest_run = [p for p in paras if NAMES_A_PYTEST_RUN.search(p)]
    either = [p for p in paras
              if NAMES_A_SCRIPT.search(p) or NAMES_A_PYTEST_RUN.search(p)]
    neither = [p for p in paras
               if not (NAMES_A_SCRIPT.search(p) or NAMES_A_PYTEST_RUN.search(p))]
    return {
        "paragraphs_with_a_suite_figure": len(paras),
        "backed_by_a_scripts_py": len(script),
        "backed_by_a_pytest_command": len(pytest_run),
        "backed_by_either": len(either),
        "backed_by_neither": len(neither),
        "unbacked_previews": [p.strip()[:110] for p in neither],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    s = survey()
    if a.json:
        print(json.dumps(s, indent=2))
        return 0
    n = s["paragraphs_with_a_suite_figure"]
    for key in ("backed_by_a_scripts_py", "backed_by_a_pytest_command",
                "backed_by_either", "backed_by_neither"):
        k = s[key]
        lo, hi = wilson(k, n)
        print(f"{key}: {k} of {n} = {100.0 * k / n if n else 0:.4f}%, "
              f"Wilson [{100 * lo:.4f}%, {100 * hi:.4f}%]")
    for prev in s["unbacked_previews"]:
        print(f"  UNBACKED: {prev}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
