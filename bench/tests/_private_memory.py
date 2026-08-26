"""Readability probe for the private memory directory, which lives outside the repo.

WHY THIS EXISTS. Measured 2026-08-26 01:45 BST, mid-session: this process lost
read access to ~/.claude/projects/.../memory while the session was running. Edits
to files in that directory had succeeded roughly forty minutes earlier. The
access change is environmental, not a project event.

WHAT THAT BROKE, AND IT IS THE HOUSE FAILURE MODE. Four tests guarded themselves
with `if not MEMORY.exists(): skip` or `if not PRIVATE_MEMORY.is_dir(): skip`.
Under this permission state:

    exists()      -> True          (so the skip does NOT fire)
    is_dir()      -> True          (so the skip does NOT fire)
    iterdir()     -> PermissionError
    read_text()   -> PermissionError
    glob(...)     -> []            <-- returns EMPTY, does not raise

The glob case is the dangerous one. `_latest_memory_standard_version()` globbed
for cdsfl_note_standard_v*.md, got an empty list, returned None, and the test
failed with "no cdsfl_note_standard_vN.N.md found in the memory directory" --
asserting the files are ABSENT when they are merely UNREADABLE. A failed
measurement rendered as a finding, inside the drift guard written to catch
exactly that class.

THE RULE. Existence is not readability. Probe by attempting the read that the
test actually needs, and treat a denial as a measurement that did not happen:
SKIP with a message saying so, never FAIL (which reads as drift) and never
silently pass (which reads as health).
"""
from __future__ import annotations

import pathlib

MEMORY_DIR = (pathlib.Path.home()
              / ".claude/projects/-Users-georgejackson-Developer-Projects/memory")


def probe(directory: pathlib.Path = MEMORY_DIR) -> tuple[bool, str]:
    """(readable, reason). Attempts the read rather than asking about it.

    `readable` is True only when the directory can actually be enumerated AND at
    least one entry can be opened, because enumeration alone has been observed to
    succeed on this machine while per-file reads were denied.
    """
    if not directory.exists():
        return False, f"{directory} does not exist on this machine"
    if not directory.is_dir():
        return False, f"{directory} exists but is not a directory"
    try:
        entries = [p for p in directory.iterdir()]
    except (PermissionError, OSError) as exc:
        return False, (f"{directory.name} cannot be enumerated: "
                       f"{type(exc).__name__}. The comparison did not happen; "
                       "this is NOT evidence of drift.")
    files = [p for p in entries if p.is_file()]
    if not files:
        return False, f"{directory.name} enumerated but contains no files"
    try:
        files[0].read_bytes()
    except (PermissionError, OSError) as exc:
        return False, (f"{directory.name} lists {len(files)} files but they "
                       f"cannot be read: {type(exc).__name__}. The comparison "
                       "did not happen; this is NOT evidence of drift.")
    return True, f"{len(files)} files readable"


def files(directory: pathlib.Path = MEMORY_DIR) -> list[pathlib.Path]:
    """Every readable file. Raises if the directory cannot be enumerated, so a
    caller cannot mistake a denial for an empty directory."""
    return [p for p in directory.iterdir() if p.is_file()]
