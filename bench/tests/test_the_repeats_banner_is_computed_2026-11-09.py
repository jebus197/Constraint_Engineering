"""The "are these repeats" banner must be COMPUTED at the live count.

WHY. Until 2026-11-09 `scripts/build_decisions_file_2026-11-07.py` held that
section as a literal template with only `n`, `date` and `sha` substituted, so
it printed the word "Neither" whatever the data said. Its bounds were measured
over 29 items on 2026-11-08 and never recomputed; at 12 items the printed
Wilson upper bound of 0.116970 should have been 0.242494, understated by
2.073133 times, and the Clopper-Pearson 0.119445 should have been 0.264648,
understated by 2.215654 times. It also named B20 and B71 as carrying rulings
when neither was among its own items.

THE FIRST REPAIR FIXED ONLY THE WRITTEN SURFACE and left the SPOKEN one, which
is the one he listens to, still printing the frozen bounds. So every test here
runs BOTH renders. A fix on 1 of 2 surfaces is the shape this project keeps
meeting.

THESE TESTS EXECUTE. They call the renderer and read its output, and compare it
against the summary function called separately -- a producer and a consumer
that disagree are each individually correct.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
FROZEN = ("0.116970", "0.119445")


@pytest.fixture(scope="module")
def bdf():
    spec = importlib.util.spec_from_file_location(
        "bdf_rep", REPO / "scripts" / "build_decisions_file_2026-11-07.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["bdf_rep"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def rendered(bdf):
    mrb, rows = bdf.collect()
    return {s: bdf.render(mrb, rows, spoken=s) for s in (True, False)}, rows


def _head(text: str) -> str:
    """Everything before the index, which is where the banner lives."""
    for mark in ("THE ", "## The "):
        i = text.find(mark + "")
    m = re.search(r"(?:^|\n)(?:## The \d+ at a glance|THE \d+ AT A GLANCE)", text)
    return text[:m.start()] if m else text


class TestTheFiguresAreLive:
    def test_the_summary_is_computed_from_the_rows(self, bdf, rendered):
        _, rows = rendered
        s = bdf.repeats_summary(rows)
        assert s["n"] == len(rows), "the banner's n is not the live row count"
        assert s["gap"] < 1e-9, f"the 2 interval routes disagree by {s['gap']}"

    @pytest.mark.parametrize("spoken", [True, False],
                             ids=["spoken", "written"])
    def test_the_rendered_bound_matches_the_computed_bound(
            self, bdf, rendered, spoken):
        texts, rows = rendered
        s = bdf.repeats_summary(rows)
        head = _head(texts[spoken])
        assert f"{s['w_hi']:.6f}" in head, (
            f"the {'spoken' if spoken else 'written'} banner does not carry the "
            f"Wilson upper bound computed at n={s['n']}")
        assert f"{s['cp_hi']:.6f}" in head, (
            "the Clopper-Pearson upper bound is not the computed one")

    @pytest.mark.parametrize("spoken", [True, False],
                             ids=["spoken", "written"])
    def test_a_frozen_bound_appears_only_as_a_named_correction(
            self, rendered, spoken):
        head = _head(rendered[0][spoken])
        for f in FROZEN:
            n = head.count(f)
            assert n <= 1, f"{f} appears {n} times; a stale bound came back"
            if n:
                i = head.find(f)
                near = head[max(0, i - 420):i + 120]
                assert ("should have read" in near or "understat" in near), (
                    f"{f} is printed as if it were current: ...{near[-180:]}")

    @pytest.mark.parametrize("spoken", [True, False],
                             ids=["spoken", "written"])
    def test_no_foreign_identifier_is_named(self, bdf, rendered, spoken):
        """★ ADDED AFTER A MUTATION SURVIVED. Replacing the computed names with
        the literal "B20, B21 and B71" left all 15 tests green, because B21 is
        genuinely present and nothing checked the others. Naming an entry this
        file does not carry is the exact defect measured on 2026-11-09."""
        texts, rows = rendered
        idents = {r["ident"] for r in rows}
        head = _head(texts[spoken])
        # The claim paragraph only -- the correction sentence below it names
        # B20 and B71 ON PURPOSE, as the figures it supersedes.
        start = head.lower().find("not repeats either")
        assert start >= 0, "the claim paragraph is gone"
        end = head.lower().find("every figure in this section", start)
        para = head[start:end if end > start else len(head)]
        foreign = sorted({m for m in re.findall(r"\b[A-Z]{1,2}\d{1,4}\b", para)
                          if m not in idents})
        assert not foreign, (
            f"the banner names entries this file does not carry: {foreign}. "
            f"Its own are {sorted(idents)}")

    @pytest.mark.parametrize("spoken", [True, False],
                             ids=["spoken", "written"])
    def test_the_named_entries_are_this_file_s_own(self, bdf, rendered, spoken):
        """★ RE-POINTED 2026-11-13. THIS GUARD WAS OUTGROWN, NOT BROKEN.

        It asserted that every entry the banner COMPUTES as carrying a ruling
        also appears in the rendered head BY ITS CODE -- `B77` literally in the
        text. On 2026-11-10 the banner was deliberately changed to render
        DECISION NUMBERS instead: "decision 4 below", "decisions 1 to 6 below".
        That change is his own descriptor rule applied to this surface -- he
        has no access to the ticket store and cannot look a bare code up -- so
        the renderer is right and this assertion was pinning the form the rule
        replaced.

        THE PROPERTY IS KEPT AND IS NOW STRONGER. What matters is that nothing
        the banner computes goes unrendered. That is asserted here against the
        NUMBER the reader can actually follow, and the count is compared too,
        so a renderer that silently dropped one would still fail.
        """
        texts, rows = rendered
        s = bdf.repeats_summary(rows)
        idents = {r["ident"] for r in rows}
        head = _head(texts[spoken])
        computed = s["ruled"] + s["responded"]
        for named in computed:
            assert named in idents, (
                f"{named} is named by the banner but is not one of this "
                f"file's own rows")
        # ★ CALL THE PRODUCER'S OWN RENDERER, do not re-derive its string
        # shapes. A first version of this assertion guessed at the forms --
        # "decision N below", "decisions N and M" -- and merged the ruled and
        # responded groups into one range, so it demanded "decisions 1 to 6
        # below" where the banner correctly prints "decisions 1 to 4 below"
        # and "decisions 5 and 6 below" as 2 separate groups. A test that
        # re-implements its subject tests its own copy.
        pos = {r["ident"]: i + 1 for i, r in enumerate(rows) if r.get("ident")}
        for group, label in ((s["ruled"], "ruled"), (s["responded"], "responded")):
            if not group:
                continue
            phrase = bdf._decision_numbers(group, pos)
            assert phrase != "none", (
                f"the banner counts {len(group)} entries as {label} and "
                f"renders them as 'none'")
            assert phrase in head, (
                f"the {label} group renders as {phrase!r}, which is not in "
                f"the head. A banner that counts an entry and then does not "
                f"point at it tells him a number he cannot act on.")
            # ...and nothing computed may be silently dropped by the renderer.
            missing = [i for i in group if i not in pos]
            assert not missing, (
                f"{missing} are counted as {label} but have no position, so "
                f"`_decision_numbers` drops them silently while the COUNT "
                f"still includes them")


class TestTheVerdictIsDerived:
    """The word after the question mark must follow the data, not a template."""

    def test_an_empty_set_does_not_say_neither(self, bdf):
        s = bdf.repeats_summary([])
        assert s["verdict"] != "Neither.", (
            "with 0 rows the banner still asserts 'Neither'")

    def test_rows_with_no_ruling_and_no_reply_are_all_new(self, bdf):
        rows = [{"ident": "Z1"}, {"ident": "Z2"}]
        assert bdf.repeats_summary(rows)["verdict"] == "All of them are new to you."

    def test_a_ruling_or_a_reply_gives_neither(self, bdf):
        assert bdf.repeats_summary(
            [{"ident": "Z1", "ruled": "2026-01-01"}])["verdict"] == "Neither."
        assert bdf.repeats_summary(
            [{"ident": "Z1", "responded": "2026-01-01"}])["verdict"] == "Neither."

    def test_the_bound_moves_with_n(self, bdf):
        a = bdf.repeats_summary([{"ident": f"Z{i}"} for i in range(12)])
        b = bdf.repeats_summary([{"ident": f"Z{i}"} for i in range(29)])
        assert a["w_hi"] > b["w_hi"], (
            "the interval does not widen as the sample shrinks, so it is not "
            "being computed at the live count")
        assert abs(a["w_hi"] - 0.242494) < 1e-5, a["w_hi"]
        assert abs(a["cp_hi"] - 0.264648) < 1e-5, a["cp_hi"]


class TestGrammarHeReadsAloud:
    """★ THESE 2 PINNED THE PRE-2026-11-10 LABEL FORM AND ARE RE-POINTED.

    They asserted the label rendered as "entry Z1" and "entries Z1, Z2" --
    bare codes. On 2026-11-10 the banner was deliberately changed to render
    DECISION NUMBERS, because he has no access to the ticket store and a bare
    code tells him nothing he can act on. The renderer is right; these
    assertions pinned the form his own rule replaced.

    THE PROPERTY THEY EXIST FOR IS THE VERB AGREEMENT, and that is kept
    exactly: 1 entry takes a singular verb, 2 take a plural. Only the label
    form moves, and it moves to what the producer actually emits.
    """

    def test_one_entry_takes_a_singular_verb(self, bdf):
        s = bdf.repeats_summary([{"ident": "Z1", "ruled": "2026-01-01"}])
        assert s["ruled_verb"] == "carries", (
            f"1 entry took the plural verb {s['ruled_verb']!r}")
        assert s["ruled_label"] == "decision 1 below", (
            f"the singular label is {s['ruled_label']!r}")

    def test_two_entries_take_a_plural_verb(self, bdf):
        s = bdf.repeats_summary([{"ident": "Z1", "ruled": "2026-01-01"},
                                 {"ident": "Z2", "ruled": "2026-01-02"}])
        assert s["ruled_verb"] == "carry", (
            f"2 entries took the singular verb {s['ruled_verb']!r}")
        assert s["ruled_label"] == "decisions 1 and 2 below", (
            f"the plural label is {s['ruled_label']!r}. 2 consecutive numbers "
            f"read better aloud as '1 and 2' than as a range, which is the "
            f"renderer's own stated rule.")

    @pytest.mark.parametrize("spoken", [True, False],
                             ids=["spoken", "written"])
    def test_no_number_verb_disagreement_in_the_render(self, rendered, spoken):
        head = _head(rendered[0][spoken])
        assert not re.search(r"\b1 carry\b", head), "'1 carry' is in the output"
