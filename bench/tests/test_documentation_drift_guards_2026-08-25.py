"""Three guards against the drift class that produced four separate defects.

FOUNDER INSTRUCTION 2026-08-25: "Check it and ensure there is no repeated drift."

THE CLASS. Every one of these was a copy or a pointer that nothing compared against
its source, so it aged silently and was found by accident rather than by a check:

  1. 2026-08-24  the RUNWAY declared the project frozen pending nine decisions that
                 had been ruled two days earlier.
  2. 2026-08-24  MEMORY.md line 31 quoted a test figure and attributed it to a file
                 that has never contained it.
  3. 2026-08-24  the RUNWAY's Desktop mirror was 127 lines behind its repo copy.
  4. 2026-08-25  the project instructions named note standard v1.4 while memory was
                 at v1.5 — two versions and four months adrift. Commit e49a021 on
                 13 August had already recorded a "STRUCTURAL FIX" for exactly this
                 and it recurred, because that fix corrected the instance and not
                 the class.

Number four is the argument for this file. A correction that is not a check is a
promise, and this project's own note standard exists because a restated promise had
already failed.

CLAIM WITHDRAWN 2026-08-26. This paragraph previously read: "Cross-document
supersession — a document asserting something a later ruling overturned — is not
mechanically detectable and is not attempted. Defect 1 above would still not be
caught." The founder asked "For sure?", and it was too strong.

GENERAL supersession is not detectable. Defect 1 is not general: it is a hold
assertion plus a NAMED file that already carries a rulings marker, and both halves
are machine-readable. `scripts/supersession_check.py` detects that pair and fires
on the real historical file (git c8f63ec~1) this paragraph said it could not.
Defect 1 IS now caught, by that script and by
test_supersession_check_commissioned_2026-08-26.py, not by this file.

The residual limit, stated narrowly this time: a hold that names no file, or that
paraphrases the decision list instead of pointing at it, is still invisible.
"""
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
HOME = pathlib.Path.home()
MEMORY = HOME / ".claude/projects/-Users-georgejackson-Developer-Projects/memory"


# ---------------------------------------------------------------------------
# GUARD 1 — the note standard version must agree across its two homes
# ---------------------------------------------------------------------------
def _latest_memory_standard_version():
    """Highest cdsfl_note_standard_vN.N.md present in the memory directory."""
    best = None
    for f in MEMORY.glob("cdsfl_note_standard_v*.md"):
        m = re.search(r"_v(\d+)\.(\d+)\.md$", f.name)
        if m:
            v = (int(m.group(1)), int(m.group(2)))
            best = v if best is None or v > best else best
    return best


@pytest.mark.skipif(not MEMORY.exists(),
                    reason="private memory directory is outside the repo and absent here")
def test_project_instructions_name_the_current_note_standard():
    """The project CLAUDE.md must name the newest standard that exists in memory.

    This is the check that commit e49a021 said it was making on 13 August and did
    not: it fixed the pointer and left nothing behind to compare them again.
    """
    latest = _latest_memory_standard_version()
    assert latest, "no cdsfl_note_standard_vN.N.md found in the memory directory"
    claude_md = (REPO / ".claude/CLAUDE.md").read_text(encoding="utf-8")
    named = re.findall(r"cdsfl_note_standard_v(\d+)\.(\d+)\.md", claude_md)
    assert named, ".claude/CLAUDE.md names no note-standard file at all"
    highest_named = max((int(a), int(b)) for a, b in named)
    assert highest_named == latest, (
        f"note-standard drift: memory holds v{latest[0]}.{latest[1]} but the project "
        f"instructions name v{highest_named[0]}.{highest_named[1]} as newest. "
        "This exact drift recurred once after being 'structurally fixed'."
    )


@pytest.mark.skipif(not MEMORY.exists(), reason="memory directory absent")
def test_foot_line_convention_names_the_current_standard():
    """The foot-line every compliant note must carry was itself three versions
    stale on 2026-08-25 — it still said v1.2 while v1.5 was current."""
    latest = _latest_memory_standard_version()
    claude_md = (REPO / ".claude/CLAUDE.md").read_text(encoding="utf-8")
    m = re.search(r"Written under CDSFL note standard v(\d+)\.(\d+)", claude_md)
    assert m, "the foot-line convention is not stated in .claude/CLAUDE.md"
    stated = (int(m.group(1)), int(m.group(2)))
    assert stated == latest, (
        f"foot-line convention names v{stated[0]}.{stated[1]} but the current "
        f"standard is v{latest[0]}.{latest[1]}"
    )


# ---------------------------------------------------------------------------
# GUARD 2 — a declared Desktop mirror must match its canonical repo copy
# ---------------------------------------------------------------------------
# Documents that declare a Desktop mirror in their own text. The repo copy is
# canonical by founder ruling of 2026-08-06; the Desktop copy is a convenience.
DECLARED_MIRRORS = [
    ("experimental_notes/CDSFL_Agent_Operational_Plan.md",
     HOME / "Desktop/CDSFL_Agent_Operational_Plan.md"),
    ("experimental_notes/RUNWAY_to_BR2_2026-08-18.md",
     HOME / "Desktop/CDSFL_RUNWAY.md"),
]


@pytest.mark.parametrize("repo_rel,desktop", DECLARED_MIRRORS,
                         ids=[p.split("/")[-1] for p, _ in DECLARED_MIRRORS])
def test_declared_desktop_mirror_matches_its_canonical_copy(repo_rel, desktop):
    """Found 2026-08-24: the RUNWAY's mirror was 326 lines against the repo's 453,
    so the Desktop copy was missing everything from roughly 22 August onward —
    including the discrimination control result."""
    canonical = REPO / repo_rel
    assert canonical.is_file(), f"canonical copy missing: {repo_rel}"
    if not desktop.is_file():
        pytest.skip(f"Desktop mirror absent on this machine: {desktop.name}")
    a = canonical.read_text(encoding="utf-8", errors="replace")
    try:
        b = desktop.read_text(encoding="utf-8", errors="replace")
    except (PermissionError, OSError) as exc:
        # CONTENT DENIED, METADATA AVAILABLE. Measured 2026-08-25: this machine's
        # sandbox denies read() on ~/Desktop (6 of 6 attempts) while stat() and
        # write() both succeed. A first version of this branch SKIPPED, which was
        # honest but weak — and skipping is how a guard quietly stops guarding.
        #
        # Size is a real comparison, not a proxy for one, and it would have caught
        # the drift this guard exists for: the RUNWAY mirror was 326 lines against
        # the repo's 453 on 2026-08-24. Equal size is weaker than equal bytes, and
        # the message says so rather than claiming parity.
        try:
            desk_size = desktop.stat().st_size
        except (PermissionError, OSError):
            pytest.skip(f"{desktop.name} is inaccessible to read AND stat: "
                        f"{type(exc).__name__}. The comparison did not happen; this "
                        "is not evidence of drift.")
        repo_size = len(a.encode("utf-8"))
        if desk_size != repo_size:
            pytest.fail(
                f"mirror SIZE MISMATCH: {repo_rel} is {repo_size} bytes, "
                f"{desktop.name} is {desk_size}. Content could not be compared "
                f"(read denied) but the sizes differ, so they are NOT in sync. "
                f"The repo copy is canonical (founder ruling 2026-08-06)."
            )
        pytest.skip(f"{desktop.name}: content unreadable, but sizes MATCH at "
                    f"{repo_size} bytes — consistent with parity, weaker than proof.")
    if a != b:
        la, lb = len(a.splitlines()), len(b.splitlines())
        pytest.fail(
            f"mirror drift: {repo_rel} has {la} lines, {desktop.name} has {lb}. "
            f"The repo copy is canonical (founder ruling 2026-08-06); re-sync the "
            f"Desktop copy from it, never the reverse."
        )


# ---------------------------------------------------------------------------
# GUARD 3 — the memory ledger must be derived, not typed
# ---------------------------------------------------------------------------
@pytest.mark.skipif(not MEMORY.exists(), reason="memory directory absent")
def test_memory_ledger_total_matches_the_directory():
    """Duplicates the existing accounting assertion deliberately.

    The remedy recorded on 2026-08-17 — derive this number inside the save routine
    rather than typing it — has needed the same manual correction SEVEN consecutive
    times, twice in a single session on 2026-08-24. This test does not fix that; it
    is a second, independent place the discrepancy surfaces, so that a green suite
    cannot coexist with a wrong ledger if the other test is ever moved or skipped.
    """
    ledger = (REPO / "resources/MEMORY_EXCLUSIONS.md").read_text(encoding="utf-8")
    m = re.search(r"\|\s*total\s*\|\s*(\d+)\s*\|", ledger)
    assert m, "MEMORY_EXCLUSIONS.md states no total"
    stated = int(m.group(1))
    on_disk = len([p for p in MEMORY.iterdir() if p.is_file() and p.name != "MEMORY.md"])
    assert stated == on_disk, (
        f"memory ledger drift: {on_disk} individual files on disk, ledger says "
        f"{stated}. Seven consecutive manual corrections say this wants deriving "
        "inside sv rather than typing."
    )
