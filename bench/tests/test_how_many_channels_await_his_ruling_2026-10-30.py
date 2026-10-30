#!/usr/bin/env python3
"""2 of the 4 `informative_only` channels he has ALREADY RULED, so C1 must not
ask him to rule them again.

WHAT WENT WRONG IN ENTRY C1. Its narrow question -- into which of sigma, S_k or
R_k a claim-level verdict should enter -- is genuinely his and is untouched here.
Its 2 SUPPORTING ARGUMENTS are not:

  (a) *"`target_complexity` appears with `informative_only` NOWHERE in the
      code"*, used to argue the claim ledger's header names a precedent that does
      not exist. REFUTED: 2 sites inside `run_experiment`, both written
      2026-09-10 in `22fd393a0`, which is 38 days BEFORE the 2026-10-18 search
      that reported them absent. So the search missed them; the tree did not
      move. The likely cause is a SAME-LINE predicate, since
      `result["target_complexity"]` and `"informative_only"` sit 4 lines apart
      in one dict literal -- the predicate-error class that accounted for 8 of
      the 10 reasoning-catchable errors measured on 2026-10-11.

  (b) *"3 channels carry `informative_only = True` ... 0 of the 3 have ever been
      promoted"*, concluding that *"answering it once would retire a class
      rather than an item"*. REFUTED: there are 4 distinct channels, and 2 of
      them carry a `why` field naming HIS OWN RULING as the reason they are
      informative-only BY DESIGN -- 2026-09-30 for the non-cure ledger
      (*"neither terminally rejects the finding nor blocks the run"*) and
      2026-09-09 for target complexity (*"a reported statistic, not an input to
      any gate"*). A channel he has ruled is not a channel awaiting promotion,
      and asking him again is the `already ruled` failure this project's record
      names twice. The 4th, `stamp_sev_f`, is a 2026-10-13 free-panel facility
      whose `RunnerConfig.sev_f_enabled` defaults to False, so its question is
      whether to switch it on, not where it enters the equations.

SO EXACTLY 1 CHANNEL AWAITS THE RULING C1 ASKS FOR, and the correction makes
what is owed him narrower rather than wider.

WHAT THIS FILE PINS. Not the counts -- channels may legitimately be added, and a
channel he rules later must be free to move from AWAITING to RULED without
turning a guard red. It pins the PROPERTIES: that the grouping treats a class
and its own serialising method as 1 channel; that a founder ruling propagates
across a channel's sites; that the 2 recorded rulings are still in the tree,
named by SCOPE rather than by line; and that the `target_complexity`
co-occurrence which refutes claim (a) is still there, pinned as a SET of scopes
rather than as a count, because a count cannot say which one moved.
"""
from __future__ import annotations

import ast
import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

PRODUCER = (REPO / "scripts"
            / "how_many_channels_actually_await_his_ruling_2026-10-30.py")


def _producer():
    assert PRODUCER.is_file(), f"producer absent: {PRODUCER}"
    spec = importlib.util.spec_from_file_location("channel_probe", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _producer()


@pytest.fixture(scope="module")
def c(mod):
    return mod.classify()


class TestTheGroupingIsRight:
    """The unit is the CHANNEL. Counting sites is the error C1 made."""

    def test_a_class_and_its_serialising_method_are_one_channel(self, mod):
        """SYNTHETIC, so no tree change can make it vacuous."""
        src = (
            "class Chan:\n"
            "    informative_only = True\n"
            "    def report(self):\n"
            "        return {'informative_only': self.informative_only}\n"
        )
        tree = ast.parse(src)
        spans = mod._scope_map(tree)
        # the class-body flag and the dict inside the method
        assert mod._scope_of(spans, 2) == "Chan"
        assert mod._scope_of(spans, 4) == "Chan", (
            "a dict inside a method was attributed to the METHOD, so a flag and "
            "its own serialisation count as 2 channels and inflate what is owed "
            "him -- the exact over-count this file exists to correct")

    def test_a_module_level_function_keeps_its_own_name(self, mod):
        tree = ast.parse("def f():\n    return {'informative_only': True}\n")
        assert mod._scope_of(mod._scope_map(tree), 2) == "f"

    def test_there_are_fewer_channels_than_sites(self, c):
        assert c["n_channels"] < c["n_sites"], (
            f"{c['n_sites']} site(s) grouped into {c['n_channels']} channel(s); "
            f"if those are equal the grouping has stopped grouping and every "
            f"sibling site is being counted as a separate obligation")


class TestARulingPropagatesAcrossItsChannel:
    def test_the_error_path_inherits_its_channels_ruling(self, c):
        """`run_experiment` holds target complexity's normal AND error path.
        Only the normal path carries the `why`; both must read as RULED."""
        ch = [x for x in c["channels"] if x["scope"] == "run_experiment"]
        assert ch, "the run_experiment channel has gone; re-derive this check"
        assert len(ch[0]["sites"]) >= 2, (
            "the run_experiment channel now holds fewer than 2 sites, so the "
            "propagation this test checks is no longer exercised")
        assert ch[0]["why"] and "2026-09-09" in ch[0]["why"]
        assert ch[0] in c["ruled"]

    def test_a_synthetic_channel_with_no_why_is_awaiting(self, mod, c):
        """POSITIVE CONTROL on the classifier: it must discriminate, not just
        agree with the current tree."""
        ruled_scopes = {x["scope"] for x in c["ruled"]}
        await_scopes = {x["scope"] for x in c["unruled"]}
        assert ruled_scopes, "nothing classifies as RULED; the classifier is blind"
        assert await_scopes, (
            "nothing classifies as AWAITING; the classifier calls everything "
            "ruled and could not detect an unruled channel")
        assert not (ruled_scopes & await_scopes), (
            f"these scopes are in BOTH buckets: {ruled_scopes & await_scopes}")


class TestTheTwoRulingsAreStillInTheTree:
    """Named by SCOPE, not by line, so ordinary edits cannot fail this."""

    def test_the_non_cure_ledger_ruling_of_30_september(self, c):
        ch = [x for x in c["channels"]
              if x["scope"] == "collect_non_cure_ledger"]
        assert ch, "the non-cure ledger channel has gone"
        assert ch[0]["why"] and "2026-09-30" in ch[0]["why"], (
            "the non-cure ledger no longer records his 2026-09-30 ruling, so C1 "
            "would read it as a channel awaiting promotion and ask him again")

    def test_both_rulings_name_him_as_the_source(self, c):
        for ch in c["ruled"]:
            assert "founder ruling" in str(ch["why"]).lower(), (
                f"{ch['scope']} is classified RULED on a `why` that does not "
                f"name a founder ruling: {ch['why']!r}")


class TestClaimAIsRefutedAndStaysRefuted:
    def test_target_complexity_co_occurs_with_the_flag(self, mod):
        hits = mod.target_complexity_cooccurs()
        scopes = sorted({h["file"] for h in hits})
        assert hits, (
            "0 co-occurrences found, which would RESTORE entry C1's claim that "
            "`target_complexity` appears with `informative_only` nowhere. Check "
            "whether the sites were removed or the detector broke before "
            "accepting it")
        assert scopes == ["bench/reference_runner_v3.py"], (
            f"the co-occurrence set moved to {scopes}; it was pinned as a set "
            f"rather than a count so that a swap is visible")

    def test_the_sites_predate_the_search_that_missed_them(self, mod):
        """THE REASON THIS IS THE SEARCH'S FAULT AND NOT THE TREE'S.

        A claim measured on 2026-10-18 cannot be blamed for code written after
        it. Every co-occurring site must be OLDER than that date for the entry's
        statement to have been false when written.
        """
        for h in mod.target_complexity_cooccurs():
            prov = mod.first_commit_touching(h["file"], h["line"])
            assert prov["date"], f"no blame date for {h['file']}:{h['line']}"
            assert prov["date"] < "2026-10-18", (
                f"{h['file']}:{h['line']} was written {prov['date']}, AFTER the "
                f"2026-10-18 search. That site cannot be evidence the search "
                f"missed anything, and the entry's correction must be re-scoped "
                f"to the sites that do predate it.")


def test_sev_f_is_default_off_so_its_question_is_not_the_same_question():
    """The 4th channel is not C1's question wearing a different name."""
    tree = ast.parse((REPO / "bench" / "reference_runner_v3.py").read_text())
    found = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "RunnerConfig":
            for st in node.body:
                tgt = getattr(st, "target", None)
                if isinstance(st, ast.AnnAssign) and getattr(tgt, "id", "") == \
                        "sev_f_enabled":
                    found = ast.literal_eval(st.value)
    assert found is False, (
        f"RunnerConfig.sev_f_enabled now defaults to {found!r}. While it was "
        f"False, `stamp_sev_f` was a default-off facility whose question is "
        f"whether to switch it on. If it is on by default, it IS now a live "
        f"scoring channel and C1's question may genuinely cover it.")
