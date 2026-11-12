#!/usr/bin/env python3
"""The dispatcher stamps every brief it sends, and the SEATS get the stamped text.

★ B125's FIRST HALF, AND WHY IT IS TESTED HERE RATHER THAN ASSERTED. His
accepted recommendation is that a brief QUOTES THE STATE of every file it
references, so a seat's reading is attributable to the bytes it actually read.
The stamping function has existed since 2026-11-06 and, measured 2026-11-12,
reached **0 of 17** archived joint briefs
-- Wilson 95% [0.000000, 0.184318]. Each of those briefs named at least 1
artefact, so the stamper had something to resolve every time. An addition
reaching nothing is forbidden by the additive standard on its own,
independently of B125.

★ THE SENTENCE ABOVE WAS REFLOWED ON 2026-11-12 AND THE REASON IS A GUARD, NOT
STYLE. It originally ran both counts together on 1 line and put the interval on
the next, like this:

<!-- verbatim-begin: the defective sentence, quoted as evidence. The span is
     exempted so that quoting the fault does not REPRODUCE it -- a scar must not
     read as a wound, which is how the first attempt at this paragraph refused a
     second board. -->
    reached **0 of 17** archived joint briefs while **17 of 17** named an
    artefact -- Wilson 95% [0.000000, 0.184318].
<!-- verbatim-end -->

The interval belongs to the FIRST count. `scripts/wilson_interval_consistency.py` pairs an interval with a
count on the same line or the line before, so it took the NEARER one and
correctly reported the pair as contradictory: Wilson for 17 of 17 is
[0.815682, 1.000000], verified on statsmodels, NumPy and mpmath agreeing to
1.110e-16. The figures were right and the SENTENCE put them where a reader --
and a checker -- would mis-attribute them. It refused a commit board of
2248.44 s.

★ THE TEST THAT MATTERS IS THE RETURN VALUE, NOT THE FILE. `PROMPT` -- the text
the seats actually receive -- is bound from the brief by `resolve_brief` long
before the stamp runs. A fix that wrote the stamped file without rebinding PROMPT
would put the stamp on disk and send the seats the UNSTAMPED text: a cosmetic fix
wearing a real one's name. That was the first version of this repair, caught by
tracing where PROMPT is consumed (the seat-dispatch calls) rather than by reading
the diff.

★ IDEMPOTENCE IS BY GUARD, NOT BY THE STAMPER. Measured 2026-11-12: calling
`insert_stamp` twice adds the digest table twice. The heading check in
`stamp_brief_at_dispatch` is therefore load-bearing, and
`test_a_second_pass_does_not_double_the_table` is what holds it.

Costs nothing: writes only into pytest's own temporary directory, dispatches to
no model, runs no pytest of its own.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PANEL = REPO / "bench" / "confer_maths_panel_2026-09-05.py"
STAMPER = REPO / "scripts" / "stamp_the_brief_artefacts_2026-11-06.py"
HEADING = "ARTEFACT STAMPS AT DISPATCH"
#: A brief that names real repository files, so the stamper has something to
#: resolve. Chosen as paths that exist and are stable.
NAMED = ("bench/cdsfl_registry/domain_manifest.toml",
         "bench/cdsfl_registry/domain_vocabulary.py")


@pytest.fixture(scope="module")
def panel():
    assert PANEL.is_file()
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    spec = importlib.util.spec_from_file_location("panel_stamp_guard", PANEL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _brief(tmp_path: pathlib.Path, extra: str = "") -> pathlib.Path:
    b = tmp_path / "BRIEF.md"
    b.write_text(
        "# A BRIEF FOR THE GUARD\n\n"
        "This brief names files so the stamper has something to resolve.\n\n"
        f"See `{NAMED[0]}` and `{NAMED[1]}` for the vocabulary.\n\n"
        "## 0. WHAT IS BEING ASKED\n\nNothing; this is a fixture.\n" + extra,
        encoding="utf-8")
    return b


class TestTheStamperItselfIsReachable:
    def test_the_stamper_exists_and_exposes_what_the_dispatcher_calls(self):
        assert STAMPER.is_file(), f"the stamper is missing: {STAMPER}"
        spec = importlib.util.spec_from_file_location("bs_guard", STAMPER)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        for name in ("insert_stamp", "named_artefacts"):
            assert callable(getattr(m, name, None)), f"{name} is not callable"


class TestTheDispatcherStampsAndReturnsWhatTheSeatsGet:
    def test_it_stamps_a_brief_that_names_files(self, panel, tmp_path):
        b = _brief(tmp_path)
        before = b.read_text(encoding="utf-8")
        assert HEADING not in before
        out = panel.stamp_brief_at_dispatch(b, before)
        assert HEADING in b.read_text(encoding="utf-8"), "the file was not stamped"
        assert HEADING in out, (
            "the RETURN VALUE carries no stamp, so the seats would receive the "
            "unstamped text even though the file on disk is stamped")

    def test_the_returned_text_matches_the_file_on_disk(self, panel, tmp_path):
        """If these diverge, the archive records bytes nobody was sent."""
        b = _brief(tmp_path)
        out = panel.stamp_brief_at_dispatch(b, b.read_text(encoding="utf-8"))
        assert out == b.read_text(encoding="utf-8")

    def test_a_second_pass_does_not_double_the_table(self, panel, tmp_path):
        """The stamper is NOT idempotent; the heading guard is what makes this so."""
        b = _brief(tmp_path)
        first = panel.stamp_brief_at_dispatch(b, b.read_text(encoding="utf-8"))
        second = panel.stamp_brief_at_dispatch(b, first)
        assert second == first, "a second pass changed the brief"
        assert first.count(HEADING) == 1, (
            f"the heading appears {first.count(HEADING)} times after 1 pass")
        assert second.count(HEADING) == 1, (
            "a second pass added the digest table again; the heading guard in "
            "stamp_brief_at_dispatch is not holding")

    def test_the_stamp_records_a_digest_for_each_named_file(self, panel, tmp_path):
        b = _brief(tmp_path)
        out = panel.stamp_brief_at_dispatch(b, b.read_text(encoding="utf-8"))
        for path in NAMED:
            assert path in out, f"{path} is named in the brief but not stamped"


class TestItNeverBlocksADispatch:
    def test_a_missing_brief_returns_the_prompt_unchanged(self, panel, tmp_path):
        out = panel.stamp_brief_at_dispatch(tmp_path / "absent.md", "ORIGINAL")
        assert out == "ORIGINAL"

    def test_a_brief_naming_nothing_is_returned_unchanged(self, panel, tmp_path):
        b = tmp_path / "BRIEF.md"
        b.write_text("# no file paths at all here\n\nprose only.\n", encoding="utf-8")
        out = panel.stamp_brief_at_dispatch(b, b.read_text(encoding="utf-8"))
        assert HEADING not in out
        assert out == b.read_text(encoding="utf-8")

    def test_a_broken_stamper_does_not_raise_into_the_dispatch(
            self, panel, tmp_path, monkeypatch):
        """A guard that refuses on its own malfunction is the shape this project
        keeps having to withdraw, so a stamper failure must warn and continue."""
        monkeypatch.setattr(panel, "_REPO", tmp_path / "nowhere")
        b = _brief(tmp_path)
        body = b.read_text(encoding="utf-8")
        out = panel.stamp_brief_at_dispatch(b, body)
        assert isinstance(out, str) and out, "it returned nothing usable"


class TestTheOrderingInvariant:
    def test_the_stamp_is_called_before_the_topology_record(self):
        """The topology hashes the brief. Stamping afterwards would record a
        digest for a file that is not the one the seats were sent."""
        src = PANEL.read_text(encoding="utf-8")
        i_stamp = src.index("PROMPT = stamp_brief_at_dispatch(")
        i_topo = src.index("    _write_topology_record()", i_stamp - 4000)
        assert i_stamp < i_topo, (
            "the stamp runs after the topology record, so the recorded digest "
            "will not match the dispatched brief")

    def test_PROMPT_is_assignable_in_main(self):
        """Without the global declaration this is a silent local, and the seats
        keep the unstamped text while the file on disk looks right."""
        src = PANEL.read_text(encoding="utf-8")
        assert "global MODELS, PROMPT" in src, (
            "PROMPT is not declared global in main, so the rebind is a local "
            "and the seats receive the unstamped brief")
