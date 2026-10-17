"""Counting helpers whose NAME states the unit, and which exclude themselves.

TASK C2. HIS QUESTION, 2026-10-02, verbatim: *"Then can similar errors be
prevented in the futre [future]? If not they might lead to unhelpful and
erroneous descisions [decisions]."* -- asked of 7 withdrawn statements.

THE 7 FELL INTO 3 SHAPES, and this module exists because each shape is a
counting mistake rather than a reasoning one:

  1. DOUBLE MATCHING. *"the producing script matched every run log under 2
     patterns at once"*, so each log was counted twice.
  2. LINES REPORTED AS OCCURRENCES. *"counted lines containing a match and
     reported them as occurrences, which is the same unit error caught once
     already the same day"*.
  3. SELF-INCLUSION. a census that *"included the 3 documents written about the
     term it was counting"*.

THE SAME 3 SHAPES RECURRED ON 2026-10-17, which is the evidence that a rule was
not enough. A detector read its OWN SOURCE as live code and reported 5 defects,
every one a line of its own docstring (shape 3). Another read its own
explanatory comment as the code it was checking (shape 3 again). A substring
scan reported 190 hits for "promot" -- the project's own shadow PROMOTION -- 64
for "division", mostly arithmetic, and 25 for "fixture", which is pytest (shape
2, a token counted as a concept). All were caught before they reached him, and
all were caught by accident rather than by a mechanism.

WHAT THIS MODULE DOES, AND WHAT IT DELIBERATELY DOES NOT. It cannot stop a
producer choosing the wrong population; nothing can. It makes the 3 shapes above
HARD TO WRITE:

  * the unit is in the FUNCTION NAME, so `occurrences` and `lines_containing`
    cannot be confused where they are called, and a reader of that line sees
    the unit without opening the definition;
  * `count_over` excludes the CALLING FILE by default, so a producer cannot
    appear in its own total without saying so;
  * `overlapping_patterns` reports patterns that match the same item, so an
    item counted twice is visible before any figure is published.

It is not a style preference. Every function returns a figure a brief may quote,
and the cost of getting one wrong is a withdrawn claim.
"""
from __future__ import annotations

import inspect
import pathlib
import re
from typing import Iterable, Pattern, Sequence

__all__ = [
    "occurrences",
    "lines_containing",
    "count_over",
    "overlapping_patterns",
]


def _compiled(pattern: "str | Pattern[str]", flags: int = 0) -> "Pattern[str]":
    return pattern if hasattr(pattern, "finditer") else re.compile(pattern, flags)


def occurrences(pattern: "str | Pattern[str]", text: str, flags: int = 0) -> int:
    """How many TIMES the pattern matches. 3 on a line holding it 3 times.

    Named for its unit because the error it prevents is a unit error: a figure
    reported as occurrences when it was lines is wrong by however many times a
    line repeats the term, and that is unbounded.
    """
    return sum(1 for _ in _compiled(pattern, flags).finditer(str(text)))


def lines_containing(pattern: "str | Pattern[str]", text: str,
                     flags: int = 0) -> int:
    """How many LINES hold at least one match. 1 on a line holding it 3 times.

    The other half of the pair, named so a call site cannot mean the first by
    accident.
    """
    rx = _compiled(pattern, flags)
    return sum(1 for line in str(text).split("\n") if rx.search(line))


def count_over(paths: Iterable["str | pathlib.Path"],
               pattern: "str | Pattern[str]",
               *,
               unit: str,
               exclude_self: bool = True,
               exclude: Sequence[str] = (),
               flags: int = 0) -> dict:
    """Count across files, EXCLUDING the calling file unless told otherwise.

    `unit` is KEYWORD-ONLY AND HAS NO DEFAULT. It must be "occurrences" or
    "lines", so the figure carries its unit out of the function and into
    whatever quotes it. Written first with a default of "occurrences", which
    made the docstring's claim that it was required FALSE -- the same shape as
    every other defect here: a description and a behaviour that disagree.

    SELF-EXCLUSION IS THE DEFAULT because shape 3 is the one that keeps
    recurring: a producer counting a term will mention that term, and a detector
    scanning for a pattern will contain that pattern in its own docstring. The
    excluded paths are RETURNED, not silently dropped, so a reader can see what
    was left out and object to it.

    Returns {"total", "unit", "files", "per_file", "excluded"}.
    """
    if unit not in ("occurrences", "lines"):
        raise ValueError(
            f"unit must be 'occurrences' or 'lines', not {unit!r}; a count "
            f"whose unit is not stated is the error this module exists to stop")
    counter = occurrences if unit == "occurrences" else lines_containing
    caller = ""
    if exclude_self:
        frame = inspect.stack()[1]
        caller = str(pathlib.Path(frame.filename).resolve())
    skip = {str(pathlib.Path(p).resolve()) for p in exclude}
    if caller:
        skip.add(caller)
    per_file: dict[str, int] = {}
    excluded: list[str] = []
    for raw in paths:
        path = pathlib.Path(raw)
        resolved = str(path.resolve())
        if resolved in skip:
            excluded.append(str(path))
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        n = counter(pattern, text, flags)
        if n:
            per_file[str(path)] = n
    return {
        "total": sum(per_file.values()),
        "unit": unit,
        "files": len(per_file),
        "per_file": per_file,
        "excluded": excluded,
    }


def overlapping_patterns(patterns: Sequence["str | Pattern[str]"],
                         items: Iterable[str],
                         flags: int = 0) -> dict:
    """Which items match MORE THAN ONE pattern, so a double count is visible.

    Shape 1 of the 3: *"the producing script matched every run log under 2
    patterns at once"*. A producer summing per-pattern counts over the same
    population double-counts exactly these items, and the error is invisible in
    the total.

    Returns {"double_matched", "by_item", "distinct_matched", "sum_of_counts"},
    where a `sum_of_counts` larger than `distinct_matched` is itself the
    evidence of double counting.
    """
    rxs = [_compiled(p, flags) for p in patterns]
    by_item: dict[str, list[int]] = {}
    for item in items:
        hits = [i for i, rx in enumerate(rxs) if rx.search(str(item))]
        if hits:
            by_item[str(item)] = hits
    double = {k: v for k, v in by_item.items() if len(v) > 1}
    return {
        "double_matched": len(double),
        "by_item": double,
        "distinct_matched": len(by_item),
        "sum_of_counts": sum(len(v) for v in by_item.values()),
    }
