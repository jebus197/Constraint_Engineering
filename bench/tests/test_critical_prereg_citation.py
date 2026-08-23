"""T09 — the live work queue and RECOVERY must CITE the frozen critical-severity
pre-registration, not just name the threshold.

`CRITICAL_SEVERITY_THRESHOLD = 0.7` is the operational proxy for a
consequence-based rubric that was pre-registered and FROZEN on 2026-05-18 at
``bench/exp40_baseline/CRITICAL_DEFINITION_PREREG_2026-05-18.md``. Before this
pin, the two live documents that carry the threshold as an open item named the
number and the ruling but never the pre-registration, so an agent reading either
one could move the float without knowing a frozen pre-registration governs it.

These tests assert the citation sits NEXT TO the critical-severity item (not
merely somewhere in a 220 KB file), that the cited file is on disk, that it is
marked frozen, and that the number it encodes still matches the runner's
constant. Offline: filesystem reads only.
"""

from __future__ import annotations

import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PREREG_REL = "bench/exp40_baseline/CRITICAL_DEFINITION_PREREG_2026-05-18.md"
PREREG = REPO / PREREG_REL
QUEUE = REPO / "experimental_notes" / "OUTSTANDING_QUEUE_to_BR2.md"
RECOVERY = REPO / "resources" / "RECOVERY.md"
RUNNER = REPO / "bench" / "reference_runner_v2.py"

WINDOW = 12  # lines either side of the critical-severity item


def _cites_near(doc: pathlib.Path, anchor: str) -> bool:
    """True if PREREG_REL appears within WINDOW lines of any `anchor` line."""
    lines = doc.read_text(encoding="utf-8").splitlines()
    hits = [i for i, ln in enumerate(lines) if anchor in ln]
    assert hits, f"{doc.name} no longer mentions {anchor!r}"
    for i in hits:
        block = "\n".join(lines[max(0, i - WINDOW): i + WINDOW + 1])
        if PREREG_REL in block:
            return True
    return False


class TestThePreRegistrationExistsAndGoverns:
    def test_file_is_on_disk(self):
        assert PREREG.is_file(), f"cited pre-registration missing: {PREREG_REL}"

    def test_it_is_frozen_and_encodes_the_threshold(self):
        text = PREREG.read_text(encoding="utf-8")
        assert "FROZEN" in text, "the cited file must be the frozen pre-registration"
        assert "CRITICAL_SEVERITY_THRESHOLD = 0.7" in text

    def test_the_runner_constant_still_matches_what_is_cited(self):
        # If the constant ever moves, the citation is a lie and this fails.
        assert "\nCRITICAL_SEVERITY_THRESHOLD = 0.7\n" in RUNNER.read_text(
            encoding="utf-8"
        )


@pytest.mark.parametrize(
    "doc, anchor",
    [
        (QUEUE, "critical-severity"),
        (RECOVERY, "critical-severity ceiling"),
    ],
    ids=["outstanding_queue", "recovery"],
)
class TestBothLiveDocumentsCiteIt:
    def test_path_is_cited_beside_the_open_item(self, doc, anchor):
        assert _cites_near(doc, anchor), (
            f"{doc.name}: the critical-severity item must cite {PREREG_REL} so the "
            "0.7 float cannot be moved without seeing the frozen pre-registration"
        )

    def test_citation_resolves_on_disk(self, doc, anchor):
        text = doc.read_text(encoding="utf-8")
        assert PREREG_REL in text
        assert (REPO / PREREG_REL).is_file()
