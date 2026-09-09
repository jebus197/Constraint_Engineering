"""One path-delimited predicate for "is this archived run output, or source?"

TASK 6.4. Founder ruling, verbatim: *"So the sweep (and its original context,
which I shouldn't need to repeat), should be run again if you do this? If so,
do it."*

WHY ONE PREDICATE. Five checkers each decided this question for themselves and
they did not agree. Measured 2026-09-09 by `scripts/archive_root_agreement_2026-09-09.py`:
**1 of 10 pairs agree exactly**, Wilson [1.8%, 40.4%], Clopper-Pearson
[0.3%, 44.5%]. Only 1 of 5 excluded `bench/results/`; **0 of 5 excluded
`bench/logs_quarantine/`**, which exists on disk and holds quarantined run
output; and 1 of 5 tested a bare SUBSTRING (`"bench/logs" not in line`) rather
than a path prefix. So the same file could be production source to 1 checker and
archive to the next, which is the class this project catalogues as "a bounded
traversal standing in for a complete one" -- here, five different bounds.

WHY DELIMITED, with the example sitting in this repository. `bench/logs_quarantine`
starts with the string `bench/logs`, so a bare `startswith("bench/logs")` matches
it by accident while `startswith("bench/logs/")` misses it entirely. Neither is a
decision anyone made. This module compares PATH COMPONENTS, so `logs` can never
be confused with `logs_quarantine` in either direction, and adding a root to
`ARCHIVE_ROOTS` is the only way to change what counts.

WHAT THIS IS NOT. It does not decide whether a file is committed, generated, or
ignored -- only whether its location marks it as the OUTPUT of a run rather than
part of the instrument. `.gitignore` and the tracked-file checks answer the other
questions and are not duplicated here.
"""

from __future__ import annotations

import os
import re
from pathlib import PurePosixPath
from typing import Iterable, Union

#: Repository-relative roots whose contents are the output of runs, not source.
#: Adding one here changes every caller at once, which is the point.
ARCHIVE_ROOTS: tuple[str, ...] = (
    "bench/logs",
    "bench/logs_quarantine",
    "bench/results",
)

PathLike = Union[str, "os.PathLike[str]"]


def _parts(path: PathLike) -> tuple[str, ...]:
    """Repo-relative path as POSIX components, tolerant of Windows separators."""
    text = str(path).replace("\\", "/").strip()
    if text.startswith("./"):
        text = text[2:]
    return PurePosixPath(text).parts


def is_archived_run_output(path: PathLike, roots: Iterable[str] = ARCHIVE_ROOTS) -> bool:
    """True when a repo-relative path lies inside an archive root.

    A root itself counts, so `bench/logs` is archive and so is
    `bench/logs/run/x.json`. `bench/logs_quarantine` is a DIFFERENT root and is
    matched only because it is named in `ARCHIVE_ROOTS`, never by accident of
    sharing a prefix with `bench/logs`.
    """
    parts = _parts(path)
    for root in roots:
        rp = _parts(root)
        if rp and parts[:len(rp)] == rp:
            return True
    return False


def is_production_source(path: PathLike, roots: Iterable[str] = ARCHIVE_ROOTS) -> bool:
    """The complement, named positively because most callers ask it that way."""
    return not is_archived_run_output(path, roots)


#: A quoted string literal, as it appears in source text.
_QUOTED = re.compile(r"""['"]([^'"\n]{1,300})['"]""")
#: A bare path-ish token, for mentions that are not inside quotes.
_TOKEN = re.compile(r"[A-Za-z0-9_./\\-]{4,}")


def line_mentions_archive_path(line: str, roots: Iterable[str] = ARCHIVE_ROOTS) -> bool:
    """True when a SOURCE LINE names a path inside an archive root.

    DISTINCT FROM `is_archived_run_output`, which classifies a path, and the
    distinction is not academic: the first attempt at task 6.4 wired a
    text-scanning checker to the PATH predicate by stripping the line's quotes
    and passing the whole line. Every line then failed the check, every offender
    was skipped, and the test went green while detecting nothing. Executed to
    confirm it: `fp = REPO / "bench/logs/run" / name` classified as not-archive,
    where the substring test it replaced caught it.

    So this scans the line for path-shaped fragments -- quoted literals first,
    then bare tokens containing a separator -- and asks the path predicate about
    each. `ARCHIVE_ROOTS` stays the single place that decides what an archive is.
    """
    for m in _QUOTED.finditer(line):
        if is_archived_run_output(m.group(1), roots):
            return True
    for token in _TOKEN.findall(line):
        if ("/" in token or "\\" in token) and is_archived_run_output(token, roots):
            return True
    return False
