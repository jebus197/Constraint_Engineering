# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'severity_corrected_2026-11-06_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: d1defa2da38a602a4fc71f2baf8552db4e092a32834da3cc5fc2a4a857b62f7f
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""A dated producer's byte-copy at repo root is a hazard, not a feature.

EVIDENCE (joint round on `severity_corrected_2026-11-06`, 2026-11-10).
`the_computed_severity_is_three_valued_on_the_archive_2026-11-06.py` sat at
repo root, byte-identical -- sha256
917aa5d7d5c48fca9ff05cb5398abdfaad4c9635dd1d9fc291c4ce0eb92abea5 -- to the
archived blind-half copy at
bench/logs/severity_corrected_2026-11-06/sandbox_harvest/cc2/attempt-1/
files/scripts/the_computed_severity_is_three_valued_on_the_archive_2026-11-06.py,
and superseded by the folded-back scripts/ version that declares its frame.
The sandbox manifest records no root-level path for it: an accidental
deposit. Executed at root it resolved `REPO` one directory too high,
printed "NO ARCHIVE ... measurement not attempted" and EXITED 0 -- a
measurement-shaped no-op, the exact failure mode
`bench/tests/test_operational_scripts.py` documents for unreached scripts,
at a path that suite does not scan.

Removal satisfies the additive standard because the measurement is
committed here: the byte-identical archived copy (hash above) preserves
the original, and the named properties on which the scripts/ replacement
dominates are (1) its archive path resolves (root copy: NO ARCHIVE, exit
0) and (2) its frame is declared (root copy: undeclared, the defect of
the round). This test makes the property executable so the deposit
cannot silently recur at the next harvest fold-back.
"""
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]


def test_repo_root_carries_no_copy_of_a_scripts_producer():
    script_names = {p.name for p in (REPO / "scripts").glob("*.py")}
    stray = sorted(p.name for p in REPO.glob("*.py") if p.name in script_names)
    assert stray == [], (
        f"copies of scripts/ producers found at repo root: {stray}. "
        "scripts/ is the producer's real path; a root copy resolves its "
        "archive one level too high and exits 0 having measured nothing."
    )
