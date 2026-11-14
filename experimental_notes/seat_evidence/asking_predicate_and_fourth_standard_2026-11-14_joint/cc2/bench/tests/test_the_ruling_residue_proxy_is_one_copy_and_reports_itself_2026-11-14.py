# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'asking_predicate_and_fourth_standard_2026-11-14_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 7a841231b81c01f4c12eb953883d35c4cdf1795051e26572ade205c739da595b
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The ruling-residue date proxy is ONE implementation and SAYS it is a guess.

WHAT THIS GUARDS, and each clause names the measurement behind it.

1. ONE IMPLEMENTATION. Before 2026-11-14 the rule "is there a date in the body
   later than the ruling" was written out twice: inline in
   `how_many_decisions_actually_need_him_2026-11-01.classify_text` with
   `_DATED_IN_BODY`, and again in
   `morning_report_build_2026-10-12.asks_newer_than_the_ruling` with `_DATED`.
   The 2 patterns were byte-identical in source and the call sites independent,
   and the second one gates `ruling_is_spent`, which decides the MORNING
   REPORT's decision list -- the document he reads. `ruling_is_spent`'s own
   docstring records that this project has already paid for exactly that shape.
   The fold was licensed by a committed measurement: the 2 implementations
   agreed on 10 of 10 ruled OPEN entries, 1.000000, Wilson 95% [0.722467,
   1.000000]. These tests assert the fold holds and the fork does not return.

2. THE FLAG IS A REPORT, NOT A VERDICT. `classify_text` gained
   `residue_undecidable`. `kind` must be unchanged by its presence, or the
   addition would have moved a figure he reads while claiming not to.

3. NON-VACUITY, on constructed text and not on live data alone. A guard whose
   only evidence is live data that happens to exercise it is indistinguishable
   from a guard that does nothing.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def clf():
    sys.path.insert(0, str(REPO / "scripts"))
    return _load("_clf_guard",
                 "scripts/how_many_decisions_actually_need_him_2026-11-01.py")


@pytest.fixture(scope="module")
def mrb():
    sys.path.insert(0, str(REPO / "scripts"))
    return _load("_mrb_guard", "scripts/morning_report_build_2026-10-12.py")


@pytest.fixture(scope="module")
def live(clf):
    import task_list_markers as tlm                          # type: ignore
    opens = [e for e in tlm.parse_entries(LIST)
             if (e.state or "").upper() == "OPEN"]
    bodies = clf.bodies()
    return opens, bodies


class TestOneImplementation:
    def test_the_rule_is_exposed_as_a_named_function(self, clf):
        assert callable(getattr(clf, "residue_proxy_fired", None)), (
            "`residue_proxy_fired` is the single implementation of the date "
            "proxy; without it every caller re-types the comparison")

    def test_the_generator_no_longer_retypes_the_comparison(self):
        """★ THE FORK CANNOT RETURN SILENTLY.

        `_DATED` itself is NOT asserted absent: `_dated_additions` and the
        deferral derivation still use it for a different question, and removing
        a live pattern on the strength of one caller changing would be the
        removal half of the additive standard with no measurement behind it.
        What is asserted is that `asks_newer_than_the_ruling` does not compare
        dates itself.
        """
        import ast
        path = REPO / "scripts" / "morning_report_build_2026-10-12.py"
        src = path.read_text()
        fn = next(n for n in ast.walk(ast.parse(src))
                  if isinstance(n, ast.FunctionDef)
                  and n.name == "asks_newer_than_the_ruling")
        #: ★ THE DOCSTRING IS EXCLUDED, AND THE FIRST VERSION OF THIS TEST WAS
        #: WRONG FOR NOT EXCLUDING IT. The repaired function's docstring QUOTES
        #: the code it replaced, so a text search over the whole function
        #: matched the quotation and failed on the repair itself -- a scar
        #: reading as a wound, the same shape `classify_text`'s own positional
        #: retirement comment records on B22. The body is taken from the AST
        #: with the docstring node dropped, so only EXECUTABLE source is read.
        stmts = fn.body[1:] if (fn.body and isinstance(fn.body[0], ast.Expr)
                                and isinstance(fn.body[0].value, ast.Constant)
                                and isinstance(fn.body[0].value.value, str)
                                ) else fn.body
        body = "\n".join(ast.unparse(s) for s in stmts)
        assert "residue_proxy_fired" in body, (
            "asks_newer_than_the_ruling must DELEGATE to the one "
            "implementation, not re-type the date rule")
        assert "_DATED.findall" not in body, (
            "asks_newer_than_the_ruling has re-forked the date rule; the "
            "morning report and the banner can now disagree without any test "
            "seeing it, which is the 2026-11-01 defect recorded in "
            "`ruling_is_spent`'s own docstring")

    def test_the_2_surfaces_still_agree_on_every_ruled_open_entry(self, clf,
                                                                  mrb, live):
        """The fold's committed measurement, RE-MEASURED rather than quoted."""
        opens, bodies = live
        ruled = [e for e in opens if e.ruled]
        assert ruled, "no ruled OPEN entry: this test would be vacuous"
        for e in ruled:
            b = bodies.get(e.ident, "")
            mine = (bool(clf.classify_text(e.state, e.ruled, b)["live_asks"])
                    and clf.residue_proxy_fired(e.ruled, b))
            theirs = mrb.asks_newer_than_the_ruling(e.ident, e.ruled)
            assert mine == theirs, (
                f"{e.ident}: the classifier says {mine} and the morning report "
                f"generator says {theirs}. One of them is wrong and a count "
                f"would have hidden the swap.")


class TestTheFlagIsAReportNotAVerdict:
    def test_every_open_entry_carries_the_key(self, clf, live):
        opens, bodies = live
        for e in opens:
            d = clf.classify_text(e.state, e.ruled, bodies.get(e.ident, ""))
            assert "residue_undecidable" in d, f"{e.ident} lacks the key"
            assert isinstance(d["residue_undecidable"], bool)

    def test_the_flag_fires_exactly_where_the_proxy_decides(self, clf, live):
        """True iff a live ask, a recorded ruling, and the proxy firing.

        That conjunction is precisely the `classify_text` branch in which
        `_later` chooses between OWED and GRANTED; anywhere else the verdict
        does not depend on the proxy at all.
        """
        opens, bodies = live
        for e in opens:
            b = bodies.get(e.ident, "")
            d = clf.classify_text(e.state, e.ruled, b)
            expect = (bool(d["live_asks"]) and bool(e.ruled)
                      and clf.residue_proxy_fired(e.ruled, b))
            assert d["residue_undecidable"] is expect, e.ident

    def test_the_flag_never_changes_the_kind(self, clf):
        """★ NON-VACUITY AND VERDICT-NEUTRALITY IN ONE CONSTRUCTED PAIR.

        Two bodies identical but for a dated progress note that asks nothing.
        The note must flip the FLAG and the KIND together in the direction the
        classifier already had -- OWED with a later date, GRANTED without --
        and the flag must not be able to fire where there is no ruling.
        """
        ask = "**NEEDS HIS RULING:** should the gate name this entry?"
        with_note = ask + "\n\n2026-11-20 built the producer, all green."
        a = clf.classify_text("OPEN", "2026-11-08", ask)
        b = clf.classify_text("OPEN", "2026-11-08", with_note)
        assert a["kind"] == "GRANTED" and a["residue_undecidable"] is False
        assert b["kind"] == "OWED" and b["residue_undecidable"] is True, (
            "the constructed case does not exercise the flag; the live-data "
            "assertions above would then be the only evidence it works")
        c = clf.classify_text("OPEN", None, with_note)
        assert c["residue_undecidable"] is False, (
            "with no recorded ruling there is no residue to be undecided "
            "about, and the proxy is not consulted")

    def test_the_banner_figure_is_unchanged_by_the_addition(self, clf, live):
        """The count he reads must be the OWED count and nothing else."""
        import task_list_markers as tlm                      # type: ignore
        opens, bodies = live
        owed = sum(1 for e in opens
                   if clf.classify_text(e.state, e.ruled,
                                        bodies.get(e.ident, ""))["kind"]
                   == "OWED")
        line = tlm.summarise()
        assert f"{owed} of {len(opens)} open await YOU" in line, (
            f"the banner reads {line!r} and the OWED count is {owed}; the "
            f"addition has moved a figure he reads")
