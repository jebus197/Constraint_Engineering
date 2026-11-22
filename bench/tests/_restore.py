"""Restore a mutated file COMPLETELY — its bytes and its modification time.

DRAFTED 2026-11-22; destination `bench/tests/_restore.py`. Promote it, have
`test_the_morning_report_is_generated_2026-10-12.py` DELEGATE to it, and only
then consider any other caller.

WHY A SHARED DECLARATION. Entry B201 found that a guard restored the bytes it
mutated and left the modification time moved, which made a sibling currency check
red on a record whose CONTENT had not changed. The repair was
`_detail_restored_completely()`, and it lives in exactly 1 file -- the one it
fixed. Measured 2026-11-22 by
`a_restore_that_moves_the_timestamp_2026-11-22.py`: of 84 guards that write a
path and restore it in a `finally`, **3 restore the timestamp and 81 do not**, and
**15 of those 81 mention no temporary directory at all**, so are likelier to be
writing a repository path. 2 of those 15 are confirmed writers, caught live
during a commit board on 2026-11-22.

THE SHAPE FOLLOWS `bench/claude_cli_resolution.py`, which collapsed 2 duplicated
implementations of one idea into 1 declaration both callers delegate to. Nothing
is taken away from a caller; 1 declaration replaces 1.

★ WHY THE BYTE ASSERTION IS NOT ENOUGH, which is the lesson this file exists to
encode. `test_the_markdown_companion_is_generated_2026-10-30.py` mutates a
repository path, restores it, and asserts
`DST.read_bytes() == original, "the control failed to restore"` -- it PROVES the
content came back, and calls `utime` 0 times. The check is real and its SCOPE is
the defect: a restore has 2 properties, and verifying the first is exactly what
stops anyone asking about the second. This helper restores both and says so.

★ A FILE THAT DID NOT EXIST BEFORE IS REMOVED, NOT LEFT BEHIND. Restoring
"the original" of a file the block created means deleting it. A helper that wrote
an empty file instead would leave a path that every later reader treats as real.
"""
from __future__ import annotations

import contextlib
import os
import pathlib
from typing import Iterator


@contextlib.contextmanager
def restored_completely(path: "os.PathLike[str] | str") -> Iterator[pathlib.Path]:
    """Restore `path`'s BYTES and its access/modification times on exit.

    Yields the path as a `pathlib.Path` so a caller can write through it.

    Restores on every exit, including an exception, which is the whole point of
    a context manager here rather than a `try/finally` written out 15 times.

    A path that did not exist on entry is REMOVED on exit rather than recreated
    empty, because an empty file is not the state that was found.
    """
    p = pathlib.Path(path)
    existed = p.exists()
    original: bytes | None = None
    times: tuple[float, float] | None = None

    if existed:
        original = p.read_bytes()
        st = p.stat()
        times = (st.st_atime, st.st_mtime)

    try:
        yield p
    finally:
        if not existed:
            # It was created inside the block. The state found was ABSENT.
            p.unlink(missing_ok=True)
        else:
            assert original is not None and times is not None
            # Write first, THEN stamp: writing moves the mtime, so stamping
            # before writing would be undone by the write itself. This ordering
            # is the only part of the helper that can silently not work.
            if p.read_bytes() != original:
                p.write_bytes(original)
            os.utime(p, times)


def is_restored(path: "os.PathLike[str] | str",
                original: bytes, times: tuple[float, float],
                mtime_tolerance: float = 1e-6) -> bool:
    """True when BOTH properties match. For a guard checking the helper itself.

    `mtime_tolerance` exists because a filesystem may not store the full float
    precision `os.utime` was given, and a guard asserting exact equality would
    fail for a reason unconnected to the restore. It is NOT a licence to accept
    a moved timestamp: the default is far below any real write's granularity.
    """
    p = pathlib.Path(path)
    if not p.exists():
        return False
    if p.read_bytes() != original:
        return False
    st = p.stat()
    return abs(st.st_mtime - times[1]) <= mtime_tolerance
