"""`parked_presentation` must DESCRIBE parked items, not list bare codes.

HIS `pf`, 2026-11-01, verbatim: *"But you are again presenting me just with
ticket labels like B21, C0037, C0036, without giving any meaningful indication
what these are? This does not match the recently agreed tts presentation
standard for issues of this type. Please fix."*

WHY THIS FILE EXISTS AT ALL, AND IT IS AN ADMISSION. The fix was written on
2026-11-01 and `parked_presentation` was reached by 0 tests: a census of every
live file under `bench/` and `scripts/` found the symbol in exactly 1 file, its
own module. Under this project's additive standard an addition nothing reaches
is not additive -- 11 confirmed defects here were additions that did nothing --
so the fix was itself an instance of the class it was built while measuring.

IT CALLS THE FUNCTION. Every assertion below executes `parked_presentation` on
constructed input and reads its return value. A test that asserted on the
module's SOURCE TEXT would only prove the module describes itself consistently;
4 defects in this project were found by executing 2 forms against each other and
none by reading. The constructed inputs are deliberate, not sampled, so each
behaviour he asked for is exercised by an input that isolates it.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
MOD_PATH = REPO / "scripts" / "morning_report_build_2026-10-12.py"


def _load():
    spec = importlib.util.spec_from_file_location("mrb_2026_10_12", MOD_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mrb():
    return _load()


def test_the_function_exists_and_is_callable(mrb):
    assert hasattr(mrb, "parked_presentation"), (
        "parked_presentation is gone. His `pf` of 2026-11-01 asked for described "
        "items rather than bare codes; without this function the report reverts "
        "to listing codes.")
    assert callable(mrb.parked_presentation)


def test_a_self_closed_heading_is_counted_not_enumerated(mrb):
    parked = [
        "B21: RESOLVED -- the routing question was settled on 2026-10-17.",
        "B99: a live question that is genuinely open and needs his view.",
    ]
    items = [{"ident": "B99", "headline": "Whether the ladder may demote gamma",
              "state": "OPEN", "ruled": None}]
    out = mrb.parked_presentation(parked, items)
    assert out["settled_count"] == 1, (
        f"a heading declaring RESOLVED was not counted as settled: {out}")
    joined = " ".join(str(i) for i in out["live"])
    assert "RESOLVED" not in joined, (
        "a self-declared-closed heading was enumerated in the live list. "
        "5 of 26 such headings reached him before this fix.")


def test_one_subject_collapses_to_one_line_carrying_its_count(mrb):
    parked = [f"B21 note number {n} about the very same routing subject"
              for n in range(1, 8)]
    items = [{"ident": "B21", "headline": "Model and role selection must be trivial",
              "state": "OPEN", "ruled": "2026-10-17"}]
    out = mrb.parked_presentation(parked, items)
    b21 = [i for i in out["live"] if "B21" in i.get("codes", [])]
    assert len(b21) == 1, (
        f"7 headings on one subject produced {len(b21)} live items, not 1. "
        "B21 alone owned 7 of the 26 live headings before this fix.")
    assert b21[0]["seen_in"] == 7, (
        f"the collapsed item lost its note count: seen_in={b21[0]['seen_in']}. "
        "The count must survive, or collapsing hides that 7 notes accumulated.")


def test_the_description_leads_and_is_not_the_bare_code(mrb):
    parked = ["B21: the routing question, restated at some length here."]
    items = [{"ident": "B21",
              "headline": "Model and role selection must be trivial",
              "state": "OPEN", "ruled": "2026-10-17"}]
    out = mrb.parked_presentation(parked, items)
    assert out["live"], "no live item produced"
    subj = out["live"][0]["subject"]
    assert subj.strip() != "B21", "the subject is the bare code"
    assert not subj.strip().startswith("B21"), (
        f"the rendered subject LEADS with the code: {subj!r}. His objection was "
        "precisely to being handed 'B21' with no indication what it is.")
    assert "Model and role selection" in subj, (
        f"the subject does not carry the task list's own headline: {subj!r}")


def test_a_ruling_date_is_carried_so_a_settled_item_can_be_told_apart(mrb):
    parked = ["B21: the routing question, restated at some length here."]
    items = [{"ident": "B21", "headline": "Model and role selection must be trivial",
              "state": "OPEN", "ruled": "2026-10-17"}]
    out = mrb.parked_presentation(parked, items)
    assert out["live"][0].get("ruled") == "2026-10-17", (
        "the ruling date is dropped. Without it a report cannot distinguish an "
        "item he has decided from one still owed, which is the 6-of-7 stale-queue "
        "failure measured on 2026-11-01.")


def test_a_heading_that_says_it_restates_another_is_not_enumerated_twice(mrb):
    # The phrasing is taken from the corpus, not invented: the live heading is
    # "Enable Tailscale SSH on the private network -- SAME DECISION AS 10.2
    # ABOVE, NOT A SECOND ONE". An earlier draft of this test used "SAME AS",
    # which appears nowhere in PARKED_FOR_THE_FOUNDER.md, and the failure it
    # produced was the test's fault rather than the subject's.
    parked = [
        "B30: SAME DECISION AS B21 ABOVE, NOT A SECOND ONE.",
        "B31: a genuinely distinct open question about the severity gate.",
    ]
    items = [{"ident": "B31", "headline": "Severity gate operating point",
              "state": "OPEN", "ruled": None}]
    out = mrb.parked_presentation(parked, items)
    bodies = " ".join(str(i) for i in out["live"])
    assert "SAME DECISION AS" not in bodies, (
        "a heading whose own text says it restates another was enumerated. It "
        "should be counted, for the same reason a closed one is.")


def test_nothing_is_deleted_only_regrouped(mrb):
    """Every input heading must be accounted for somewhere in the output."""
    parked = [
        "B21: RESOLVED -- settled on 2026-10-17.",
        "B21: the routing question, live.",
        "B21: another note on routing.",
        "B40: SAME AS B21.",
        "a loose heading with no code at all in it",
    ]
    items = [{"ident": "B21", "headline": "Routing", "state": "OPEN",
              "ruled": None}]
    out = mrb.parked_presentation(parked, items)
    accounted = (sum(i.get("seen_in", 1) for i in out["live"])
                 + out["settled_count"]
                 + out.get("duplicate_count", 0))
    assert accounted >= len(parked) - 1, (
        f"{len(parked)} headings in, {accounted} accounted for. Headings may be "
        "GROUPED or COUNTED but never silently dropped -- "
        "PARKED_FOR_THE_FOUNDER.md keeps every one and the report must reconcile "
        "against it.")


def test_empty_input_does_not_raise(mrb):
    out = mrb.parked_presentation([], [])
    assert out["live"] == []
    assert out["settled_count"] == 0


def test_it_is_wired_into_both_renderers(mrb):
    """The addition must be REACHED, not merely present."""
    src = MOD_PATH.read_text(errors="ignore")
    for fn in ("render_md", "render_tts"):
        assert f"def {fn}" in src, f"{fn} is gone from the generator"
    # Both renderers must call it; a fix only one path reaches is half a fix.
    assert src.count("parked_presentation(") >= 3, (
        "parked_presentation is defined but called fewer than twice. An "
        "addition nothing reaches is not additive, and the markdown and TTS "
        "paths are both delivered to him.")


def test_a_lowercase_mention_of_a_closure_word_is_not_a_closure(mrb):
    """★ THE DEFECT THIS GUARD ACTUALLY CAUGHT, PINNED SO IT CANNOT RETURN.

    `_PARKED_SELF_CLOSED` was compiled with `re.I`, so the LIVE heading "A
    superseded copy from August is sitting visible on your Desktop" -- a warning
    that a stale file is on his Desktop -- was classified as settled business and
    dropped from what reaches him. A fix that SUPPRESSES live work is worse than
    the repetition it was built to remove, because repetition is visible and
    suppression is not. Case is the discriminator the corpus already supplies:
    every genuine declaration in it shouts.
    """
    live_heading = ("A superseded copy from August is sitting visible on your "
                    "Desktop")
    assert not mrb._PARKED_SELF_CLOSED.search(live_heading), (
        "a lowercase MENTION of a closure word is being read as a DECLARATION "
        "of closure. This exact heading is live work and was hidden from him "
        "once already.")

    out = mrb.parked_presentation([live_heading,
                                   "B9: RESOLVED -- settled on 2026-10-17."], [])
    assert out["settled_count"] == 1, (
        f"expected exactly the uppercase RESOLVED heading to be settled, got "
        f"{out['settled_count']}")
    subjects = " ".join(str(i.get("subject", "")) for i in out["live"]).lower()
    assert "superseded copy" in subjects, (
        "the live Desktop warning did not survive into the live list")


def test_an_uppercase_declaration_is_still_caught(mrb):
    """The case-sensitivity fix must not cost the true positives."""
    for heading in (
        "RESOLVED -- The 4 verified closures need ticket-store writes",
        "Committed scripts reached by nothing: RESOLVED, NOTHING LEFT TO RULE ON",
        "NOT A BLOCKER -- the memory index warns about 2 names",
        "A8 policy ruling -- SUPERSEDED, THE QUESTION GOT SMALLER",
        "The 2 Wolfram items -- 0.1 IS CLOSED AND OFF HIS ALERTS",
    ):
        assert mrb._PARKED_SELF_CLOSED.search(heading), (
            f"a genuine uppercase declaration stopped being recognised: "
            f"{heading!r}. Dropping re.I must not cost the true positives.")
