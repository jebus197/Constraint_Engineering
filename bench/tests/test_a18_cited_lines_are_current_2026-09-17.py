"""Task A18's cited read-sites must match where the reads ARE, by execution.

THE DEFECT THIS PINS. The A18 completion paragraph cites the three read sites by
line number -- `bench/reference_runner_v3.py:<N>` for `merge_arbitration_enabled`,
`immune_memory_enabled` and `api_access`. The runner then grew past 15,600 lines
and all three citations drifted (12638 -> 12902, 14984 -> 15253, 9423 -> 9438).
The A3 citation guard could not catch them: its anchor must be a def or a class,
and a config FIELD name is neither, so these citations are UNCHECKABLE to it and
drift silently -- the exact defect A3 describes, through the gap A3 declares.

THE TRUTH SIDE IS EXECUTED, NOT RETYPED. The real resolver,
`scripts/config_fields_are_read_2026-09-11.py::readers_of`, is called for each
field and the entry's cited line must be one of the lines the resolver actually
finds in `bench/reference_runner_v3.py` today.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
LIST = ROOT / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
RESOLVER = ROOT / "scripts" / "config_fields_are_read_2026-09-11.py"

FIELDS = ("merge_arbitration_enabled", "immune_memory_enabled", "api_access")


@pytest.fixture(scope="module")
def resolver():
    spec = importlib.util.spec_from_file_location("cfgread_a18", RESOLVER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["cfgread_a18"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def a18_body():
    """The A18 entry region: its heading line to the next entry heading."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from task_list_markers import parse_entries
    entries = parse_entries(LIST)
    lines = LIST.read_text(encoding="utf-8").splitlines()
    idx = {e.ident: e.line_no for e in entries}
    start = idx["A18"] - 1
    later = sorted(n for n in idx.values() if n > idx["A18"])
    end = later[0] - 1 if later else len(lines)
    return "\n".join(lines[start:end])


def cited_line_for(body: str, field: str) -> int:
    """The runner line cited WITHIN 120 chars of naming the field.

    The window matters: every field is also named in the A18 heading, far from
    any citation, and anchoring on the FIRST mention paired one field with its
    neighbour's line -- the same nearest-anchor care A3's guard takes."""
    for m in re.finditer(re.escape(f"`{field}`"), body):
        c = re.search(r"bench/reference_runner_v3\.py:(\d+)", body[m.end():m.end() + 120])
        if c:
            return int(c.group(1))
    raise AssertionError(f"A18 no longer cites a runner line beside {field}")


class TestA18CitesTheProducerRatherThanALineThatDrifts:
    """REPLACED 2026-09-17, in intake of panel round 17, and the seat's version is
    recorded above.

    fable delivered this file to hold A18's 3 cited runner lines current. The
    intake refused it: 1 operator commit during that very round moved all 3
    pins, and 2 more commits the same evening moved them again (12638 -> 12911
    -> 13064 for merge_arbitration_enabled). A test that pins a line number in
    prose asks the prose to track every edit to a 15,000-line file, which is
    the drift it is trying to catch rather than a guard against it.

    A18's entry now cites the PRODUCER, `readers_of()` in
    scripts/config_fields_are_read_2026-09-11.py, which prints the line as it
    stands. This class holds the property that survives: the producer still
    finds a runner read for each field, and the entry carries no line number
    that could be stale."""

    @pytest.mark.parametrize("field", FIELDS)
    def test_the_producer_still_finds_a_runner_read(self, resolver, field):
        readers = [r for r in resolver.readers_of(field) if "reference_runner_v3.py" in r]
        assert readers, f"{field} has no reader in the runner; A18's claim has changed"

    def test_the_entry_cites_no_runner_line_at_all(self, a18_body):
        """WHOLE BODY, not a window round the field name (corrected during this
        intake): a first version searched 400 characters either side of the first
        mention, which is in the HEADING, so putting a stale `:12638` back into
        the paragraph left all 10 tests green. The property is simply that this
        entry names no runner line, because every one of them drifted 3 times on
        2026-09-17."""
        stale = re.findall(r"reference_runner_v3\.py:(\d+)", a18_body)
        assert not stale, (
            f"A18 cites runner line(s) {stale}; they drifted 3 times on 2026-09-17 alone. "
            f"Cite readers_of() in scripts/config_fields_are_read_2026-09-11.py instead, "
            f"which prints the line as it stands.")

    def test_the_entry_names_the_producer(self, a18_body):
        assert "config_fields_are_read_2026-09-11.py" in a18_body
