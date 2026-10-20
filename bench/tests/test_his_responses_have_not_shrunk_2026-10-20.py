"""His annotations may grow. They may not disappear.

THE LOSS THIS GUARDS AGAINST, measured 2026-10-19/20. 12 of his annotations on
`TASK_LIST_48_Hours_And_Rulings_2026-10-17.txt` ceased to exist, 3 of them
rulings still owed to him. The loss was invisible for 2 days and surfaced only
because 4 unrelated guards refused a commit. Nothing was watching his folder.

WHY THE ANNOTATION COUNT AND NOT A HASH. Word rewrites these files on every save
-- 29 of 94 are already CR-only, which no modern editor writes -- so a hash
changes constantly and a hash-based guard would cry wolf until it was ignored.
A drop in the number of his annotations is a loss of his words whatever else
moved, and it is the only signal here with no benign cause.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
PROD = ROOT / "scripts" / "his_responses_manifest_2026-10-20.py"
MANIFEST = ROOT / "experimental_notes" / "data" / "his_responses_manifest.json"


def _mod():
    spec = importlib.util.spec_from_file_location("_hrm", PROD)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_hrm"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def m():
    return _mod()


def test_the_manifest_exists_and_is_not_empty():
    """ANTI-VACUITY. With no manifest every comparison below is trivially clean,
    and the guard would pass loudest the day the baseline was deleted."""
    assert MANIFEST.is_file(), (
        f"{MANIFEST.relative_to(ROOT)} is missing. Take a baseline with:\n"
        f"  python3 scripts/his_responses_manifest_2026-10-20.py --write")
    files = json.loads(MANIFEST.read_text(encoding="utf-8"))["files"]
    assert len(files) >= 50, f"only {len(files)} file(s) in the manifest"
    assert sum(f["annotations"] for f in files.values()) >= 500


def test_no_file_has_lost_an_annotation(m):
    """THE RULE. A file may gain annotations; he writes them constantly. A file
    that LOSES one has lost his words, and that is never benign."""
    try:
        cur = m.shape()
    except Exception as exc:                                    # noqa: BLE001
        pytest.skip(f"his Responses folder is not readable here: {exc}")
    bad = m.losses(m.load(), cur)
    assert not bad, (
        "his annotations have been lost since the manifest was taken:\n  "
        + "\n  ".join(bad)
        + "\n\nDO NOT refresh the manifest to make this pass. Recover the text "
          "first -- Word's File > Browse Version History is the route, and the "
          "verdict record in experimental_notes/data/annotation_verdicts_*.json "
          "may hold a copy. Refresh only once the loss is accounted for.")


def test_no_file_in_the_manifest_has_vanished(m):
    try:
        cur = m.shape()
    except Exception as exc:                                    # noqa: BLE001
        pytest.skip(f"his Responses folder is not readable here: {exc}")
    gone = sorted(set(m.load()) - set(cur))
    assert not gone, f"{len(gone)} annotated file(s) have vanished: {gone}"


def test_the_detector_actually_detects(m):
    """EXECUTED, not asserted. A guard whose comparator is broken passes forever.
    This feeds `losses()` a constructed previous-state and requires it to object."""
    prev = {"X.txt": {"annotations": 9, "bytes": 1, "sha256": "", "lines": 1,
                      "encoding": "legacy", "cr_only": True}}
    cur = {"X.txt": {"annotations": 4, "bytes": 1, "sha256": "", "lines": 1,
                     "encoding": "legacy", "cr_only": True}}
    found = m.losses(prev, cur)
    assert len(found) == 1 and "9 to 4" in found[0], found

    assert len(m.losses(prev, {})) == 1, "a vanished file was not reported"
    grew = {"X.txt": {**cur["X.txt"], "annotations": 20}}
    assert m.losses(prev, grew) == [], (
        "growth was reported as a loss; he adds annotations constantly and a "
        "guard that fires on growth will be ignored within a week")
    assert m.losses(prev, prev) == [], "an unchanged folder was reported as lost"


def test_the_word_signature_is_recorded_rather_than_inferred(m):
    """The CR-only field is what names Word as the agent. If it stopped being
    recorded, the next loss would have no cause attached to it."""
    try:
        cur = m.shape()
    except Exception as exc:                                    # noqa: BLE001
        pytest.skip(f"his Responses folder is not readable here: {exc}")
    assert cur, "no annotated files found at all"
    assert all("cr_only" in f for f in cur.values())
    cr = sum(1 for f in cur.values() if f["cr_only"])
    assert cr >= 1, (
        "0 files are CR-only. That would mean Word has stopped rewriting them, "
        "which is good news worth confirming rather than a test to delete.")
