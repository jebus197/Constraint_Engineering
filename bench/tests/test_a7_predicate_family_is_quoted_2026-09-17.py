"""Task A7: the entry must quote the predicate FAMILY, not a withdrawn identification.

THE DEFECT. The producer, scripts/escalation_paths_2026-09-11.py, withdrew the
sentence "almost certainly the one that was meant" after panel round 12 swept 7
candidate predicates: {20, 22, 32} all reproduce the entry's single anchor
(exp55_v3_control = 8), so one family figure cannot identify a predicate. The
A7 entry body in the task list kept the withdrawn identification.

THE TRUTH SIDE IS EXECUTED. The family is recomputed here by calling the real
producer's escalated_without_a_falsifier() at the runner-read threshold, at the
next float above it (the strict form), and with no severity filter at all --
and the entry body must quote exactly that family and must not carry the
withdrawn phrase.
"""
from __future__ import annotations

import importlib.util
import math
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
LIST = ROOT / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
SCRIPT = ROOT / "scripts" / "escalation_paths_2026-09-11.py"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("esc_a7", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["esc_a7"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def family(mod):
    thr = mod.critical_threshold()
    at = len(mod.escalated_without_a_falsifier(thr))
    strict = len(mod.escalated_without_a_falsifier(math.nextafter(thr, 2.0)))
    unfiltered = len(mod.escalated_without_a_falsifier(float("-inf")))
    return sorted({strict, at, unfiltered})


@pytest.fixture(scope="module")
def a7_body():
    sys.path.insert(0, str(ROOT / "scripts"))
    from task_list_markers import parse_entries
    entries = parse_entries(LIST)
    lines = LIST.read_text(encoding="utf-8").splitlines()
    idx = {e.ident: e.line_no for e in entries}
    later = sorted(n for n in idx.values() if n > idx["A7"])
    return "\n".join(lines[idx["A7"] - 1:(later[0] - 1 if later else len(lines))])


class TestTheFamilyIsRealAndQuoted:
    def test_the_family_still_has_three_members(self, family):
        """ANTI-VACUITY. If the archive changed and the candidates collapsed to
        one figure, the family quote would be stale in the other direction."""
        assert len(family) == 3, family
        assert family[1] == 22, family

    def test_the_entry_quotes_the_family(self, a7_body, family):
        quoted = "{" + ", ".join(str(n) for n in family) + "}"
        assert quoted in a7_body, (
            f"A7 does not quote the predicate family {quoted} that its own "
            f"producer computes; the count 22 is being presented as identified "
            f"when it is one of {family}")

    def test_the_withdrawn_identification_is_gone(self, a7_body):
        """The ASSERTING form must be gone. Quoting the phrase in order to
        withdraw it is legitimate and is not flagged; asserting it is."""
        assert "so it is almost certainly what was meant" not in a7_body, (
            "the producer withdrew 'almost certainly the one that was meant' "
            "(panel round 12: one family figure cannot identify a predicate); "
            "the entry still asserts it")
        if "almost certainly" in a7_body:
            at = a7_body.index("almost certainly")
            assert "withdrawn" in a7_body[max(0, at - 200):at + 200], (
                "the phrase appears without withdrawal context")
