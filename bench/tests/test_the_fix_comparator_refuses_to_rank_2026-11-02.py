#!/usr/bin/env python3
"""The fix comparator must REFUSE to rank far more often than it ranks.

HIS SPECIFICATION, 2026-10-17: the bound orchestrator's classifier must decide
*"which fixes are 'better' than others, which compose and which don't and which
meet our formal simplest sufficient fix, additive and composability standards"*,
and it is *"not 'model voting'... more akin to the simple classifier work already
done by Haiku"*.

WHAT THIS SUITE IS REALLY GUARDING. Not that the comparator ranks well -- that
it DOES NOT RANK when ranking is undecidable. A comparator that always returns an
ordering would be a rubric, and a rubric launders a judgement as a measurement.
That is the precise move the founder caught in 2026-05 when CC1 proposed
replacing the model-derived severity with a rubric, and it is the one near-miss
on the removal side of `additive-standard` in the whole project record.

So the assertions below are mostly NEGATIVE: given 2 sound candidates it must
return None; given a composition with no measurement it must refuse; given a
measurement with no stated direction it must refuse. Each of those is a place
where producing an answer would be worse than producing none.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
for _p in (REPO, REPO / "scripts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from bench.fix_comparator import (                 # noqa: E402
    BREACHES, MEASUREMENT_REQUIRED, SATISFIES, UNDECIDABLE,
    Candidate, additive_verdict, compare, composability_verdict, extent)


@pytest.fixture(scope="module")
def victim() -> str:
    """A REAL capability name from the committed snapshot, not an invented one.

    A test that deletes a made-up name would pass whatever the comparator reads,
    because the name would be absent from the snapshot either way -- so the
    assertion would hold for the wrong reason.
    """
    from bench.fix_comparator import _capability_names
    names = sorted(_capability_names())
    assert names, "no code-identifier capability names; regenerate the snapshot"
    # A name long enough that a word-boundary match cannot be accidental. The
    # first draft of this fixture took names[0] of the WHOLE snapshot, which is
    # 'a' -- an MC command -- and that single character is what exposed the
    # comparator's false-positive defect. Keeping a length floor here means the
    # fixture tests the comparator rather than the regex.
    long_enough = [n for n in names if len(n) >= 8]
    assert long_enough, f"no capability name of 8+ chars among {len(names)}"
    return long_enough[0]


def _fix(old: str, new: str, hint: str = "bench/x.py") -> str:
    """A proposed_fix in the runner's OWN marker format."""
    return f"<<<< SEARCH {hint}\n{old}\n==== REPLACE\n{new}\n>>>>\n"


# ---- the additive half, which is the only mechanically decidable one -----
def test_a_fix_that_deletes_a_capability_BREACHES(victim):
    c = Candidate("renames it away",
                  _fix(f"def {victim}(a):\n    return a",
                       "def totally_different_name(a):\n    return a"))
    v, why = additive_verdict(c)
    assert v == BREACHES, f"{v}: {why}"
    assert victim in why, "the refusal must NAME the capability it lost"
    assert "RETIRED" in why, "and must name the only route a removal is allowed"


def test_a_fix_that_keeps_it_SATISFIES(victim):
    c = Candidate("adds a guard",
                  _fix(f"def {victim}(a):\n    return a",
                       f"def {victim}(a):\n    if a is None:\n        return None\n    return a"))
    v, _why = additive_verdict(c)
    assert v == SATISFIES


def test_an_unparseable_fix_is_UNDECIDABLE_not_a_pass():
    v, why = additive_verdict(Candidate("prose only", "just make it faster"))
    assert v == UNDECIDABLE, (
        "an unparseable fix must not read as satisfying the standard; "
        "'I could not tell' and 'it is fine' are different answers")
    assert "no parseable edit" in why


def test_a_shorter_replacement_with_no_named_loss_is_UNDECIDABLE():
    """Shrinking is not by itself a breach, and must not be reported as one.

    `feedback_a_guard_can_accuse_correct_code_2026-10-28`: 9 of 36 failures in
    the 2026-10-28 baseline were guards accusing correct code, and fixing the
    subject to satisfy them would have made it worse.
    """
    v, why = additive_verdict(Candidate(
        "tightens", _fix("x = 1\ny = 2\nz = 3", "x = 1")))
    assert v == UNDECIDABLE and "shorter" in why


# ---- the refusals, which are the point -----------------------------------
def test_two_sound_candidates_are_NOT_RANKED(victim):
    a = Candidate("guard", _fix(f"def {victim}(a):\n    return a",
                                f"def {victim}(a):\n    assert a\n    return a"))
    b = Candidate("default", _fix(f"def {victim}(a):\n    return a",
                                  f"def {victim}(a=None):\n    return a"))
    r = compare([a, b])
    assert r["recommended"] is None, (
        f"it ranked {r['recommended']!r} with nothing to rank on. A comparator "
        f"that always produces an ordering is a rubric.")
    assert "NOT RANKABLE" in r["reason"]
    assert r["n_surviving"] == 2 and r["n_breaching"] == 0


def test_elimination_is_allowed_and_is_LABELLED_as_elimination(victim):
    good = Candidate("keeps", _fix(f"def {victim}(a):\n    return a",
                                   f"def {victim}(a):\n    return a or 0"))
    bad = Candidate("deletes", _fix(f"def {victim}(a):\n    return a",
                                    "def gone(a):\n    return a"))
    r = compare([good, bad])
    assert r["recommended"] == "keeps"
    assert "ELIMINATION" in r["reason"], (
        "a decision by elimination must say so; it is not a judgement of "
        "quality and must not read as one")


def test_simplest_sufficient_is_never_scored(victim):
    c = Candidate("x", _fix("a = 1", "a = 2"))
    r = compare([c])
    row = r["candidates"][0]
    assert row["simplest_sufficient"] == UNDECIDABLE
    assert "root cause" in row["simplest_sufficient_reason"]
    # the extent is reported as INPUT, so it must be present and numeric
    e = row["extent"]
    for k in ("old_chars", "new_chars", "old_lines", "new_lines", "net_lines"):
        assert isinstance(e[k], int), f"{k} must be reported as an input"


# ---- the false-positive family, ALL 3 FOUND BY THE MUTATION TEST ---------
def test_ordinary_english_in_a_diff_is_NOT_a_capability_loss():
    """THE DEFECT OF 2026-11-02, and it was UNGUARDED until the mutations said so.

    `capabilities()` has an `mc_commands` bucket whose names are chat tokens:
    24 of its 27 entries are under 3 characters, including `a`, `c`, `d`, `e`,
    `f`, `p`, `r`, `t`, `x` and `y`. With that bucket included, matching
    `\ba\b` against a diff fires on almost any English prose, so every fix
    whose removed text contained the word "a" was reported as DELETING A
    CAPABILITY. Re-adding the bucket left this suite GREEN, which is how a
    false-positive generator survives a guard.
    """
    c = Candidate("prose-heavy", _fix(
        "# a comment that mentions a thing and f and p and x and y\nvalue = 1",
        "# a comment that mentions a thing and f and p and x and y\nvalue = 2"))
    v, why = additive_verdict(c)
    assert v != BREACHES, (
        f"ordinary English words were read as capability names: {why}")


def test_a_single_character_name_can_never_be_a_capability_here():
    """The length floor, pinned. Dropping it left the suite green."""
    from bench.fix_comparator import _capability_names
    names = _capability_names()
    short = sorted(n for n in names if len(n) < 3)
    assert short == [], (
        f"names under 3 characters are in the match set: {short}. A word-"
        f"boundary match on these fires on prose, which is the 2026-11-02 "
        f"false positive.")
    assert "mc_commands" not in __import__(
        "bench.fix_comparator", fromlist=["x"]).CODE_IDENTIFIER_BUCKETS, (
        "the MC command bucket must stay excluded: its names are tokens the "
        "founder types, not symbols a source edit can delete, and their "
        "removal half is already guarded by test_additive_standard")


def test_the_identifier_floor_is_a_RATCHET_and_is_exercised(monkeypatch):
    """The length floor has 0 effect today, so it must be exercised to exist.

    Measured 2026-11-02: all 3 included buckets carry 0 names under 3
    characters, so dropping the floor changes nothing and the mutation that
    dropped it left this suite green. That is a ratchet against a FUTURE short
    name in a code bucket, and `additive-standard` requires a ratchet to be
    reached by a test rather than merely present. So a short name is planted in
    a code bucket and the floor must still exclude it.
    """
    import bench.fix_comparator as FC
    import capability_snapshot as cs
    real = cs.capabilities()
    planted = dict(real)
    planted["runner_config_fields"] = list(real.get("runner_config_fields") or []) + ["a", "xy"]
    monkeypatch.setattr(cs, "capabilities", lambda: planted)
    names = FC._capability_names()
    assert "a" not in names and "xy" not in names, (
        "the floor let a 1- and 2-character name into the match set; a word-"
        "boundary match on those fires on ordinary prose")
    # and the control: a long planted name MUST get through, or the floor is
    # simply rejecting everything and the assertion above is vacuous
    planted["runner_config_fields"] = list(real.get("runner_config_fields") or []) + ["a_long_planted_name"]
    assert "a_long_planted_name" in FC._capability_names(), (
        "the floor rejected a valid identifier; it is excluding too much")


def test_deleting_a_RETIRED_name_is_NOT_a_breach(victim, monkeypatch):
    """A retired capability may be removed; that is what RETIRED is for.

    ★ THIS MUST BE EXERCISED SYNTHETICALLY, AND THE REASON IS A MEASUREMENT.
    The live RETIRED set holds 3 names -- `ext`, `rc`, `rr` -- and 0 of the 3
    are in the live capability set, while 2 of the 3 are under 3 characters and
    so are filtered out before the exemption is ever consulted. So the
    `n not in retired` clause is UNREACHABLE on today's data: dropping it
    entirely left this suite green, which is the `additive-standard` symmetric
    failure -- an addition nothing reaches is not an addition.

    Retiring the clause would be wrong, because it is correct and will bite the
    moment a retired name IS a code identifier. So it is made REACHABLE here
    instead, by retiring a name that IS in the live set, which is exactly the
    situation the clause exists for.
    """
    import bench.fix_comparator as FC
    monkeypatch.setattr(FC, "_retired_names", lambda: {victim})
    c = Candidate("removes a retired capability",
                  _fix(f"def {victim}(a):\n    return a",
                       "def replacement(a):\n    return a"))
    v, why = additive_verdict(c)
    assert v != BREACHES, (
        f"a RETIRED capability must be removable without breaching: {why}")
    # and the control: WITHOUT the retirement the same edit must breach, or
    # this test would pass for the wrong reason
    monkeypatch.setattr(FC, "_retired_names", lambda: set())
    v2, _ = additive_verdict(c)
    assert v2 == BREACHES, (
        "un-retired, the identical edit must breach; otherwise the exemption "
        "is not what made the difference")


# ---- composability, where his definition does the work -------------------
def test_a_composition_with_no_measurement_is_REFUSED():
    v, why = composability_verdict(Candidate("a", ""), Candidate("b", ""))
    assert v == MEASUREMENT_REQUIRED
    assert "dominating BOTH parts" in why


@pytest.mark.parametrize("missing", ["property", "composed", "a_alone",
                                     "b_alone", "direction"])
def test_a_partial_measurement_is_REFUSED(missing):
    m = {"property": "p", "composed": 2, "a_alone": 1, "b_alone": 1,
         "direction": "higher_is_better"}
    m.pop(missing)
    v, why = composability_verdict(
        Candidate("a", ""), Candidate("b", ""),
        Candidate("c", "", measurement=m))
    assert v == MEASUREMENT_REQUIRED and missing in why


def test_the_direction_defect_found_by_exercising_it_stays_closed():
    """THE LIVE DEFECT OF 2026-11-02, pinned.

    The first version tested `composed > a and composed > b` unconditionally.
    Given wall clock -- composed 0.029 s against parts at 0.019 s and 0.010 s --
    it returned SATISFIES and so recommended the SLOWEST option. It was found by
    running the function on a real measurement, not by reading it.
    """
    slower = {"property": "stop-hook wall clock (s)", "composed": 0.029,
              "a_alone": 0.019, "b_alone": 0.010,
              "direction": "lower_is_better"}
    v, why = composability_verdict(Candidate("a", ""), Candidate("b", ""),
                                   Candidate("c", "", measurement=slower))
    assert v == BREACHES, (
        "a composition that is SLOWER than both parts must not be recommended "
        "on a lower-is-better property")
    assert "single fix is PREFERRED" in why


def test_a_dominating_composition_is_allowed_in_both_directions():
    lower = {"property": "seconds", "composed": 0.009, "a_alone": 0.019,
             "b_alone": 0.010, "direction": "lower_is_better"}
    higher = {"property": "speed-up", "composed": 519.0, "a_alone": 316.3,
              "b_alone": 1.0, "direction": "higher_is_better"}
    for m in (lower, higher):
        v, _ = composability_verdict(Candidate("a", ""), Candidate("b", ""),
                                     Candidate("c", "", measurement=m))
        assert v == SATISFIES, f"should dominate: {m}"


def test_an_unrecognised_direction_is_REFUSED():
    v, why = composability_verdict(
        Candidate("a", ""), Candidate("b", ""),
        Candidate("c", "", measurement={
            "property": "p", "composed": 1, "a_alone": 0, "b_alone": 0,
            "direction": "bigger"}))
    assert v == MEASUREMENT_REQUIRED and "bigger" in why


# ---- and it must consult no model ----------------------------------------
def test_it_consults_no_model_which_is_the_standing_correction():
    """`Findings confirmed programmatically or by HIL -- no model voting`.

    A comparator that asked a model which fix was better would breach that in
    the one place it matters most, so no dispatch route may appear in it.
    """
    src = (REPO / "bench" / "fix_comparator.py").read_text()
    for forbidden in ("openrouter", "OPENROUTER", "claude -p", "anthropic",
                      "chat.completions", "deepseek"):
        assert forbidden not in src, (
            f"the comparator references {forbidden!r}; it must be deterministic")

def test_the_refusal_MESSAGE_names_every_key_the_check_REQUIRES():
    """THE DEFECT OF 2026-11-03, PINNED, and it is a 2-declarations fault.

    The refusal message listed 4 keys -- property, composed, a_alone, b_alone --
    while the check enforced 5. A caller that supplied exactly what the message
    asked for was refused for `direction`, which the message never named. Found
    by CALLING the function with those 4 keys, not by reading it.

    This asserts the message against the SET, so a future key added to the set
    and not to the message fails here instead of being discovered by a caller.
    """
    from bench.fix_comparator import _COMPOSED_MEASUREMENT_KEYS
    _v, why = composability_verdict(Candidate("a", ""), Candidate("b", ""))
    missing = [k for k in _COMPOSED_MEASUREMENT_KEYS if k not in why]
    assert not missing, (
        f"the refusal message omits required key(s) {missing}, so a caller "
        f"obeying it is refused for something it was never told about")
    assert len(_COMPOSED_MEASUREMENT_KEYS) >= 5, (
        "the key set shrank; if that is deliberate the direction defect of "
        "2026-11-02 must be re-checked, because `direction` is what closed it")


def test_a_measurement_with_exactly_the_LISTED_keys_is_ACCEPTED_or_names_why():
    """ANTI-VACUITY for the test above. If the message named the keys but the
    check wanted something else entirely, the assertion above would still pass.
    So: supply every key the message names, and require the verdict NOT to be a
    refusal for a missing key.
    """
    m = {"property": "p", "composed": 0, "a_alone": 3, "b_alone": 5,
         "direction": "lower_is_better"}
    v, why = composability_verdict(
        Candidate("a", ""), Candidate("b", ""), Candidate("c", "", measurement=m))
    assert "omits" not in why, (
        f"a measurement carrying every declared key was still refused as "
        f"partial: {why}")
    assert v != MEASUREMENT_REQUIRED or "omits" not in why

# ---- extent, which no test called directly until 2026-11-03 ---------------
def test_extent_reports_a_net_zero_AND_says_whether_it_PARSED():
    """`net_lines == 0` means 2 different things, and only another field tells
    them apart.

    FOUND 2026-11-03 by calling `extent` directly. It was imported by this file
    and never exercised here -- `compare()` reached it, so it was not dead code,
    but its own contract had no direct test. A fix text that does not parse and a
    fix that is genuinely net-neutral BOTH report `net_lines == 0`. A consumer
    reading that field alone would conflate "no net change" with "I could not
    read your fix", which is the shape of asking what a 0 is a 0 OF.

    Nothing is currently at risk, because `compare()` emits the whole dict. This
    pins the 2 fields that disambiguate it, so a future change that drops either
    one fails here rather than in a consumer.
    """
    unparseable = Candidate("raw code, no markers", "        x = 1\n        y = 2\n")
    neutral = Candidate(
        "parses, net-neutral",
        "<<<< SEARCH f.py\n        x = 1\n==== REPLACE\n        x = 2\n>>>>")
    a, b = extent(unparseable), extent(neutral)

    assert a["net_lines"] == b["net_lines"] == 0, (
        "the premise of this test is that both cases report a net of 0; if that "
        "changed, the ambiguity is gone and this test should be retired")
    assert a["parses"] is False and b["parses"] is True, (
        "`parses` is the field that disambiguates a net-zero; it must keep "
        "distinguishing an unreadable fix from a net-neutral one")
    assert a["diff_hunks"] == 0 and b["diff_hunks"] >= 1, (
        "`diff_hunks` is the SECOND disambiguator and is not redundant: a "
        "consumer that reads hunks rather than `parses` must also be able to "
        "tell the 2 apart")
    assert b["file_hint"] == "f.py", (
        "a parsed fix must carry its file hint, which is what makes the extent "
        "attributable to a target at all")
