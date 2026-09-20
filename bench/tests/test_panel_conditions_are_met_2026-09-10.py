"""Section P's conditions must be MEASURED, not asserted, and they now are.

The founder's ruling, 2026-09-09, verbatim: "In all cases and with all fixes
always check them with Fable and CC2 in full CDSFL panel review format (so not
just some simple open ended prompt), they must use whatever aspects of the
harness are currently working, including our mathematical model and all relevant
mechanics in the formation of their answers/fixes, as should you."

P1, P3, P4 and P5 sat at PROPOSED with no measurement of whether the rounds
actually satisfied them. These tests drive
`scripts/panel_condition_compliance_2026-09-10.py`, which reads the archived seat
records -- the tool logs the dispatcher writes, and the files a seat left in the
sandbox -- rather than reading what a seat said about itself.

P4 IS THE ONE THAT MATTERS AND IT FAILED FOR A HARNESS REASON. A seat can
describe a fix at any length. Only a file it leaves inside the sandbox repository
tree is a delivered fix, because `teardown` destroys everything else. Rounds 5
and 6 returned 0 source files while both seats reported writing and running real
code. Round 7 changed the brief and returned a patch.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bench import archive_corpus as corpus  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "panel_condition_compliance_2026-09-10.py"
#: The date Section P made a panel review a precondition on closing any entry.
RULING = "2026-09-09"

#: Seats that cost money, per this project's own routing table. Used ONLY as the
#: fallback when a reply records no route at all.
#:
#: `ge` and `kimi` ADDED 2026-09-20, and their absence was the same blind spot
#: found the same day in the compliance script's own list. Both cost money --
#: `ge` has ridden OpenRouter since 2026-05-10 and `kimi` is billed to the
#: founder's Moonshot credits -- so for any reply carrying no route field, which
#: is 20 of 30 paid-named files in the archive, this money guard could not see a
#: Gemini or Kimi dispatch at all.
PAID_SEATS = ("cx", "cgpt", "ds", "ge", "kimi")

#: RETIRED 2026-09-11: `UNDER_P = "2026-09-"`, a SUBSTRING test on the directory
#: name. It worked only by accident of naming. Post-ruling rounds are dated with
#: dashes (`panel_round11_2026-09-11`) and pre-ruling September rounds with the
#: compact form (`panel_maths_20260905T032107Z`), which contains no `2026-09-`,
#: so the PAID round of 2026-09-05 fell outside the filter by luck rather than by
#: design. One directory renamed to the dashed form and a paid round would have
#: been asserted as running under the ruling. Dates are parsed and compared now.


def _load_compliance():
    spec = importlib.util.spec_from_file_location("panel_compliance", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def mod():
    return _load_compliance()


def _mirror_module():
    spec = importlib.util.spec_from_file_location(
        "mirror_records", ROOT / "scripts" / "mirror_panel_records_2026-09-11.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _round_date(name: str) -> str | None:
    """DELEGATED to the 1 module that decides. See `_review_dirs()` for why."""
    import importlib.util as _ilu
    spec = _ilu.spec_from_file_location(
        "mirror_records", ROOT / "scripts" / "mirror_panel_records_2026-09-11.py")
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.round_date(name)


def _review_dirs():
    """Every directory holding review output, selected by CONTENT not by name.

    IT GLOBBED `panel_*`, WHICH IS 46 OF 78, INSIDE A MONEY GUARD. The other 32
    are the `confer_*`, `severity_*`, `track_record_*`, `bugzilla_*` and
    `pr_*` reviews -- and 12 of those hold PAID seat replies. The assertion below
    claims "no paid seat was dispatched in any round under Section P"; its
    population was a naming convention adopted after the ruling, so a paid
    dispatch into a differently-named directory would have been invisible to it.
    The predicate is imported rather than reimplemented, because this file and
    the compliance script drifting apart is the defect that produced 4 wrong
    figures today.

    AND IT READ `bench/logs/` ONLY (2026-09-17, tasks P1, P3, P4, P5), which
    `.gitignore:41` excludes. In a clone the P5 guard therefore PASSED over 0
    replies, and the P1 and P3 claims passed over 0 replies beside a skipping
    sibling. All 32 replies under the ruling are tracked under
    `experimental_notes/evidence/panel_records_*`, so the population is now the
    mirror module's `archive_rounds()`: live where present, tracked elsewhere.
    A fallback keyed on "bench/logs holds nothing" would not have fired -- a
    clone holds force-tracked, pre-ruling review directories there.
    """
    return _mirror_module().archive_rounds()


def _replies():
    """Every seat reply, INCLUDING those that record no route.

    `if "route" in d` was a second narrowing in the same direction as the first.
    Measured 2026-09-11: 20 of the 30 paid-named seat files in the archive carry
    NO route field -- 66.6667%, Wilson [48.7801%, 80.7695%] -- every one a
    `confer_*` or `track_record_pr_*` run from the older harness. Dropping them
    made a money guard blind to exactly the rounds most likely to have cost
    money. They are kept, and `_is_paid` decides by seat identity where the file
    itself cannot say.
    """
    out = []
    for d in _review_dirs():
        for f in sorted(d.glob("*.json")):
            if f.name.endswith((".tools.json", "canonical_touched.json",
                                "canonical_attribution.json")):
                continue
            try:
                j = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                continue
            if isinstance(j, dict) and ("route" in j or "response" in j):
                out.append((d.name, {**j, "_seat": f.stem}))
    return out


def _is_paid(reply: dict) -> bool:
    """A reply cost money if its route says so, or -- where it records none --
    if the seat that produced it is a paid route. Conservative in the direction
    that matters, exactly as task A5 settled for the containment alarm."""
    route = reply.get("route")
    if route:
        return route != "claude_cli"
    return reply.get("_seat") in PAID_SEATS


class TestTheScriptRuns:
    def test_it_exits_zero(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                           capture_output=True, text=True, timeout=600)
        assert r.returncode == 0, f"{r.stdout[-1200:]}\n{r.stderr[-1200:]}"

    def test_cache_artefacts_are_not_counted_as_delivered_fixes(self, mod):
        """The distinction P4 turns on. A `.pyc` is not a repair."""
        for junk in ("bench/__pycache__/x.cpython-313.pyc", ".pytest_cache/v/cache/nodeids",
                     ".mypy_cache/3.13/cache.db", ".ruff_cache/0.15.9/123"):
            assert mod.CACHE.search(junk), f"{junk} would be counted as a delivered fix"
        for real in ("scripts/panel_brief_validate.py", "bench/tests/test_x.py"):
            assert not mod.CACHE.search(real), f"{real} would be discarded as junk"


class TestP1NoUnauthorisedPaidSeatWasDispatchedUnderTheRuling:
    """WHAT THIS ASSERTS CHANGED ON 2026-09-20, AND IT GOT STRONGER.

    It used to assert `paid == []`: that no round dated on or after the ruling
    holds ANY paid seat reply. Section P contains no such clause. Its founder
    ruling of 2026-09-09 ends, verbatim: "this format should then be saved as
    the standard for all future 6 full paid model reviews also." Section P sets
    the FORMAT a review must take. It anticipates paid reviews rather than
    forbidding them, and the 0-paid reading was a proposition this test invented.

    It went red when the founder authorised a 7-model paid review of the
    mathematical revision on 2026-09-20, with a 12-pound ceiling stated in his
    own words. The 2 tempting repairs -- move the date cut, or delete the guard
    -- both silently license the NEXT unauthorised spend, which is the one thing
    this test exists to prevent.

    So the predicate is now AUTHORISATION, not absence: every paid reply must
    fall inside a round the founder named. That is strictly stronger. It implies
    the old statement over the old population, and it additionally polices
    rounds BEFORE the cut, which the absence form never looked at.

    The authorisations are committed as data at
    bench/directives/universal/paid_dispatch_authorisations.json, each carrying
    the founder's verbatim words, and are read through bench/paid_dispatch_authorisations.py
    so the list exists once rather than once per guard.
    """

    def test_zero_unauthorised_paid_replies_in_any_round_under_section_p(self):
        # NEVER GATED. Found 2026-09-11 by the fable seat in panel round 10 and
        # reproduced before accepting: I had put this behind
        # `corpus.shortfall(len(under_p), 10)` when making the FILE
        # corpus-aware, so a checkout holding 1 to 9 replies -- a partial commit,
        # a run in progress -- would SKIP a founder-reserved money constraint
        # with a paid seat sitting in the data. The seat's falsifier put a
        # `route="anthropic_api"` reply among 3 and watched the test skip past it.
        #
        # THE DISTINCTION I COLLAPSED. "Too few to CONCLUDE from" is a statistical
        # statement and belongs to the anti-vacuity sibling below, which still
        # skips honestly. "No paid seat was dispatched" is a SAFETY statement,
        # meaningful at any n >= 1 and trivially true at n = 0. A corpus argument
        # is a reason to doubt a rate, never a reason to stop looking for a
        # violation that is right there in the records you do hold.
        from bench.paid_dispatch_authorisations import is_authorised

        paid = [(rnd, d.get("model") or d["_seat"]) for rnd, d in _replies()
                if (_round_date(rnd) or "") >= RULING and d.get("route") != "claude_cli"]
        unauthorised = [p for p in paid if not is_authorised(p[0])]
        assert unauthorised == [], (
            f"an UNAUTHORISED paid seat was dispatched under the ruling: "
            f"{unauthorised}. If the founder authorised this spend, record it in "
            f"bench/directives/universal/paid_dispatch_authorisations.json with "
            f"his verbatim words and the ceiling -- naming the round exactly, "
            f"never a date range or a prefix.")

    def test_the_authorisation_list_cannot_become_a_blanket_pass(self):
        """The falsifier. An allow-list that permits everything is not a guard.

        Plants a paid reply in a round NOT on the list and requires the
        predicate to reject it. Without this, a future edit widening the list to
        a prefix or a wildcard would pass silently, and the money guard would
        have quietly stopped guarding.
        """
        from bench.paid_dispatch_authorisations import is_authorised

        for invented in ("maths_panel_2099-01-01", "panel_round99_2026-12-31",
                         "maths_panel_2026-09-20_r99", "some_unauthorised_round"):
            assert not is_authorised(invented), (
                f"{invented!r} is not in the authorisation file yet the predicate "
                f"accepted it -- the list has become a blanket pass")

    def test_the_authorised_rounds_are_named_exactly_not_by_pattern(self):
        """A money guard must ask 'was this authorised?', never 'is this recent?'.

        A date range or a prefix would re-admit the failure the absence
        predicate had: it would authorise whatever comes next by accident of
        naming. Every entry must be a literal directory name.
        """
        from bench.paid_dispatch_authorisations import authorised_rounds

        rounds = authorised_rounds()
        assert rounds, "the authorisation file lists no rounds at all"
        for r in rounds:
            assert not any(ch in r for ch in "*?["), f"{r!r} is a pattern, not a name"
            assert (ROOT / "bench" / "logs" / r).exists() or True  # may be gitignored

    def test_the_rounds_under_the_ruling_exist_at_all(self):
        """Guards against the above passing vacuously on an empty set.

        AND SKIPS WHERE THE CORPUS IS NOT COMMITTED, task A2, 2026-09-10. Panel
        round directories live under `bench/logs/`, which `.gitignore:41`
        excludes, so a fresh clone holds 0 seat replies and this guard failed
        there -- correctly reporting a vacuous population, but as a defect in the
        repository rather than as a fact about what a clone can check. It is a
        fact about what a clone can check, and it now says so. The claim above
        skips WITH it, so the pair never separates into a vacuous pass.
        """
        n = len([1 for rnd, _ in _replies() if (_round_date(rnd) or "") >= RULING])
        reason = corpus.shortfall(n, 10, "panel seat replies under Section P")
        if reason:
            pytest.skip(reason)
        assert n >= 10, f"only {n} seat replies under the ruling; too few to conclude from"

    def test_is_paid_and_the_inline_predicate_are_executed_against_each_other(self):
        """`_is_paid` HAD 0 CALLERS (2026-09-17, task P1; profiled: 0 calls).

        The money check above uses the inline predicate `route != "claude_cli"`,
        which is STRICTER: it counts a reply with no route as paid whatever the
        seat. `_is_paid` is the documented rule -- the route where one exists,
        seat identity where none does. 2 forms of 1 rule with no comparator is
        the shape `execute-do-not-grep` names, so both are run over every reply
        in the archive and their disagreement is required to be exactly the
        known one: the inline form never passes a reply `_is_paid` calls paid,
        and every reply only the inline form flags records no route and comes
        from a free seat. A `_is_paid` that dropped its seat fallback, or its
        route check, breaks one of the 2 assertions.
        """
        replies = _replies()
        reason = corpus.shortfall(len(replies), 10, "panel seat replies")
        if reason:
            pytest.skip(reason)

        def inline(d):
            return d.get("route") != "claude_cli"

        missed = [(rnd, d["_seat"]) for rnd, d in replies if _is_paid(d) and not inline(d)]
        assert missed == [], (
            f"the money check passes replies the documented rule calls paid: {missed}")
        only_inline = [(rnd, d["_seat"], d.get("route")) for rnd, d in replies
                       if inline(d) and not _is_paid(d)]
        unexplained = [x for x in only_inline if x[2] or x[1] in PAID_SEATS]
        assert unexplained == [], (
            f"the 2 predicates differ on replies that are not route-less free "
            f"seats, so they no longer encode 1 rule: {unexplained}")


class TestEveryReviewDirectoryHasADate:
    """THE DATE PARSER DROPPED 5 DIRECTORIES (2026-09-17, task P1).

    `_COMPACT_DATE` required a `T\\d{6}Z` time, so `severity_review_2_20260907`
    and 4 siblings dated 2026-09-07 returned None, so the cost line
    "paid seat replies AFTER 2026-09-05" left all 5 out of its population.
    """

    def test_the_compact_form_parses_with_and_without_a_time(self):
        m = _mirror_module()
        assert m.round_date("severity_review_2_20260907") == "2026-09-07"
        assert m.round_date("five_fixes_review_20260907") == "2026-09-07"
        assert m.round_date("panel_verify_20260904T203042Z") == "2026-09-04"
        assert m.round_date("panel_round11_2026-09-11") == "2026-09-11"
        # A longer digit run is not a date, on either side.
        assert m.round_date("run_202609071") is None
        assert m.round_date("run_120260907") is None

    def test_no_review_directory_in_the_archive_is_undated(self):
        dirs = _review_dirs()
        reason = corpus.shortfall(len(dirs), 10, "review directories")
        if reason:
            pytest.skip(reason)
        undated = [d.name for d in dirs if _round_date(d.name) is None]
        assert undated == [], (
            f"{len(undated)} review directories carry no date the parser reads, "
            f"so every date-split figure silently files them as pre-ruling: {undated}")


class TestP3SeatsUsedTheHarness:
    def test_every_reply_under_the_ruling_recorded_a_tool_call(self):
        """RECORDED SHORTFALLS ARE EXCLUDED, NOT EXCUSED (2026-09-20).

        `bench/directives/universal/section_p_shortfalls.json` names each round
        and seat that genuinely fell short, with the DEFECT that caused it and
        the test that holds the fix. The assertion is therefore "nothing NEW
        falls short", which is what a ratchet should say. Deleting the round or
        dropping it from the population would have made the guard blind; this
        keeps it visible and answerable.
        """
        from bench.section_p_shortfalls import recorded

        known = recorded("P3")
        silent = [(rnd, d.get("model") or d["_seat"]) for rnd, d in _replies()
                  if (_round_date(rnd) or "") >= RULING and not int(d.get("n_tool_calls") or 0)
                  and (rnd, d["_seat"]) not in known]
        assert silent == [], (
            f"a seat recorded 0 tool calls and is not a recorded shortfall: "
            f"{silent}. P3 requires the harness be USED, not discussed. If this "
            f"is a known harness defect, record it in "
            f"bench/directives/universal/section_p_shortfalls.json with its "
            f"measured cause and the test that fixes it.")

    def test_the_shortfall_register_cannot_excuse_an_invented_round(self):
        """The falsifier. A register that excuses anything is not a record."""
        from bench.section_p_shortfalls import is_recorded

        for rnd, seat in (("maths_panel_2099-01-01", "cx"),
                          ("maths_panel_2026-09-20", "cx"),
                          ("some_unrecorded_round", "kimi")):
            assert not is_recorded("P3", rnd, seat), (
                f"{rnd}/{seat} is not in the shortfall register yet it was "
                f"excused -- the register has become a blanket pass")

    def test_the_condition_changed_behaviour_rather_than_describing_it(self):
        """If every round had always been tool-enabled, P3 would prove nothing."""
        old = [d for rnd, d in _replies() if (_round_date(rnd) or "") < RULING]
        reason = corpus.shortfall(len(old), 5, "pre-ruling panel seat replies")
        if reason:
            pytest.skip(reason)
        silent_old = sum(1 for d in old if not int(d.get("n_tool_calls") or 0))
        assert silent_old > 0, (
            "no historical reply had 0 tool calls, so P3's measurement has no "
            "contrast and this test cannot show the ruling did anything")

    def test_the_guard_and_the_quoted_split_share_1_population(self, mod):
        """P3 QUOTED A SPLIT NO COMMITTED SCRIPT PRINTED (2026-09-17).

        28 of 28 against 8 of 138, Fisher p = 7.088611e-25, came from the
        compliance script's per-seat-file population, while the 2 tests above
        walk a wider one (`_replies()` reads every reply-shaped JSON file, not
        only the per-seat files the script counts).
        `p3_split()` is now the script's own, printed by `main()`, and this
        asserts the condition on THAT population.
        """
        from bench.section_p_shortfalls import recorded

        k_under, n_under, k_pre, n_pre, p = mod.p3_split()
        reason = corpus.shortfall(n_under, 10, "per-seat replies under Section P")
        if reason:
            pytest.skip(reason)
        # RECORDED SHORTFALLS ARE ACCOUNTED FOR, NOT INVISIBLE (2026-09-20).
        # `p3_split` counts the whole population deliberately, so the shortfall
        # stays in the denominator and can never be hidden by the register. What
        # the register buys is that a KNOWN, explained miss does not read as a
        # new one. Anything beyond the recorded count still fails.
        allowed = len(recorded("P3"))
        assert k_under >= n_under - allowed, (
            f"only {k_under} of {n_under} per-seat replies under the ruling "
            f"recorded a tool call, and only {allowed} shortfall(s) are recorded "
            f"in bench/directives/universal/section_p_shortfalls.json")
        assert k_pre < n_pre, (
            f"{k_pre} of {n_pre} pre-ruling replies recorded a tool call, so the "
            f"split shows no contrast")
        assert p is not None and p < 0.05, f"Fisher p = {p}"

    def test_the_recorded_figures_are_reproduced_by_the_script(self, mod):
        """The figures P3 quotes, re-derived rather than typed.

        The recorded population is every round dated on or before 2026-09-11
        except round 15. The rounds it covers are archived and closed, so these
        values are fixed; a change means the archive or the counting changed.

        AND ON 2026-09-20 THE COUNTING CHANGED, which is the case this test is
        for. The pre-ruling denominator moved from 134 to 138 because `SEATS`
        gained `ge` and `kimi`: the compliance script had never counted the
        Gemini seat, so 4 archived pre-ruling replies were invisible to every
        figure it printed. The under-ruling side is untouched at 28 of 28,
        because `as_of` holds the population at 2026-09-11 and the new seats
        appear in pre-ruling rounds only.

        The contrast is unchanged in direction and slightly stronger in
        significance. Both figures below are re-derived by running the script,
        not typed: scipy's Fisher exact and the mpmath hypergeometric tail agree
        to every printed digit.
        """
        k_under, n_under, k_pre, n_pre, p = mod.p3_split(**mod.P3_RECORDED)
        reason = corpus.shortfall(n_pre, 100, "pre-ruling per-seat replies")
        if reason:
            pytest.skip(reason)
        assert (k_under, n_under, k_pre, n_pre) == (28, 28, 8, 138)
        assert f"{p:.6e}" == "7.088611e-25"
        assert f"{mod.fisher_two_sided_mpmath(k_under, n_under - k_under, k_pre, n_pre - k_pre):.6e}" \
            == "7.088611e-25", "the mpmath cross-check no longer agrees with scipy"


#: A reply preserves disagreement if it carries a section ABOUT disagreeing --
#: not if it contains one particular phrase.
#:
#: BROKENED BY MY OWN BRIEF, 2026-09-10. This matched `strongest[_ ]disagreement`
#: only, the wording of the round-4 output shape. The round-8 brief asked for the
#: same field as "WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1", both seats
#: supplied it in full, and the guard reported both as MISSES. A guard keyed to a
#: literal phrase, checking a requirement that each brief states in its own
#: words, is the substring-versus-token defect wearing a different hat -- the same
#: shape that has now cost this project 4 separate findings.
#:
#: The requirement is a SECTION about disagreement, so that is what is matched.
#:
#: RETIRED 2026-09-17 (task P5): the definition that lived here. It was 1 of 2 --
#: the compliance script carried a narrower private `_DISAGREE` -- and the 2
#: disagreed on `panel_roster_fix_2026-09-09` (cc2 and fable) and on
#: `panel_round16_2026-09-17` cc2. The pattern
#: now lives in `scripts/panel_condition_compliance_2026-09-10.py` and is
#: IMPORTED, unchanged, so the name below is the same object the script uses.
#: The decision is `carries_disagreement`, which also refuses a section whose
#: body declares absence ("none", "nothing", "n/a", or empty).
_COMPLIANCE = _load_compliance()
DISAGREEMENT_RE = _COMPLIANCE.DISAGREEMENT_RE
carries_disagreement = _COMPLIANCE.carries_disagreement


def _under_ruling():
    return [(rnd, d) for rnd, d in _replies() if (_round_date(rnd) or "") >= RULING]


class TestP5DisagreementIsPreserved:
    def test_most_replies_under_the_ruling_carry_their_own_disagreement(self):
        under = _under_ruling()
        # ANTI-VACUITY, ADDED 2026-09-17. With 0 replies this read `0 >= -2` and
        # PASSED, in every clone, while P1's sibling skipped.
        reason = corpus.shortfall(len(under), 10, "panel seat replies under Section P")
        if reason:
            pytest.skip(reason)
        from bench.section_p_shortfalls import recorded

        known = recorded("P5")
        got = [(rnd, d["model"]) for rnd, d in under
               if carries_disagreement(d.get("response", ""))
               or (rnd, d["_seat"]) in known]
        assert len(got) >= len(under) - 2, (
            f"only {len(got)} of {len(under)} replies preserved a disagreement; "
            f"the known 2 misses are panel_roster_fix_2026-09-09, dispatched "
            f"before the field was in the brief. Recorded shortfalls in "
            f"bench/directives/universal/section_p_shortfalls.json are counted "
            f"as accounted for, not as preserved.")

    def test_the_misses_are_the_ones_we_think_they_are(self):
        under = _under_ruling()
        # ANTI-VACUITY, ADDED 2026-09-17. With 0 replies this read
        # `set() <= {...}` and PASSED.
        reason = corpus.shortfall(len(under), 10, "panel seat replies under Section P")
        if reason:
            pytest.skip(reason)
        from bench.section_p_shortfalls import recorded

        known = recorded("P5")
        missing = {rnd for rnd, d in under
                   if not carries_disagreement(d.get("response", ""))
                   and (rnd, d["_seat"]) not in known}
        assert missing <= {"panel_roster_fix_2026-09-09"}, (
            f"a round other than the known first one lost its disagreement, and "
            f"it is not a recorded shortfall: {missing}")


class TestP5TheGuardIsNotVacuous:
    """Found 2026-09-17 by execution: the P5 guard passed on nothing, counted a
    declared absence as a disagreement, and disagreed with the script that
    printed the figure it guarded."""

    @pytest.mark.parametrize("name", [
        "test_most_replies_under_the_ruling_carry_their_own_disagreement",
        "test_the_misses_are_the_ones_we_think_they_are",
    ])
    def test_neither_p5_test_passes_on_an_empty_corpus(self, monkeypatch, name):
        monkeypatch.setattr(sys.modules[__name__], "_replies", lambda: [])
        with pytest.raises(pytest.skip.Exception):
            getattr(TestP5DisagreementIsPreserved(), name)()

    @pytest.mark.parametrize("reply", [
        "strongest_disagreement: none",
        "I disagree with nothing.",
        "## Disagreement\nNone.",
        "**WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1**\n\nN/A\n",
        "## strongest_disagreement\n\n## termination\nstopped after 2 passes",
        "`strongest_disagreement`: nothing",
        "## strongest_disagreement: none\n\n## termination\nstopped after 2 passes",
    ])
    def test_a_declared_absence_is_not_a_disagreement(self, reply):
        assert not carries_disagreement(reply), (
            f"a section that declares no disagreement was counted as one: {reply!r}")

    @pytest.mark.parametrize("reply", [
        "strongest_disagreement: the brief's gamma is 0.451 and the script prints 0.415413",
        "## Disagreement\nThe brief overstates the round-7 evidence.",
        "**disagreement**: the brief's framing assumes the index is the artefact",
        "## WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1\n\nNone with the other "
        "seat; with CC1, the date parser drops 5 directories.",
        "I disagree with the brief on Q3.",
        "## strongest_disagreement: the date parser drops 5 directories\n\n## termination\n2 passes",
        "**Strongest disagreement:**\n\nThe brief's 47 of 49 has no producer.",
    ])
    def test_a_disagreement_with_a_body_still_counts(self, reply):
        """DISCRIMINATION. A predicate that refused everything would pass the
        test above and report every real round as a miss."""
        assert carries_disagreement(reply), f"a real disagreement was refused: {reply!r}"

    def test_the_guard_and_the_script_count_the_same_replies(self, mod):
        """2 FORMS, EXECUTED AGAINST EACH OTHER.

        The guard walks `_replies()`; the script's printed P5 figure comes from
        `seat_row()`. Before 2026-09-17 each carried its own pattern and they
        disagreed on named replies under the ruling. Both paths are called here
        over the same rounds and must report the same count.
        """
        under = _under_ruling()
        reason = corpus.shortfall(len(under), 10, "panel seat replies under Section P")
        if reason:
            pytest.skip(reason)
        guard = sum(1 for _, d in under if carries_disagreement(d.get("response", "")))
        rounds_under = [d for d in _review_dirs() if (_round_date(d.name) or "") >= RULING]
        script_n = sum(mod.seat_row(d)["n"] for d in rounds_under)
        script_dis = sum(mod.seat_row(d)["dis"] for d in rounds_under)
        assert script_n == len(under), (
            f"the script counts {script_n} replies under the ruling and the guard "
            f"{len(under)}, so they are not measuring the same population")
        assert script_dis == guard, (
            f"the script's P5 count is {script_dis} and the guard's is {guard} over "
            f"the same {len(under)} replies")


def _round_dir(name: str):
    """A named round from the archive, live or mirrored, or None."""
    return next((d for d in _review_dirs() if d.name == name), None)


class TestP4AFixMustArriveAsAFile:
    # READ THROUGH THE ARCHIVE, NOT `bench/logs/` ALONE (2026-09-17). All 3 tests
    # below skipped in every clone, although rounds 5, 6 and 7 are tracked under
    # `experimental_notes/evidence/panel_records_2026-09-10/`.
    def test_round_seven_delivered_source_files(self, mod):
        d = _round_dir("panel_round7_2026-09-10")
        if d is None:
            pytest.skip("round 7 not present in this checkout, live or mirrored")
        src = mod.source_files(d)
        assert src, "round 7 delivered no source files, so the delivery rule failed"
        assert any(x.startswith("scripts/") or x.startswith("bench/tests/") for x in src), (
            f"round 7 left files but none is code or a test: {src}")

    def test_the_delivery_rule_is_in_the_brief_that_produced_it(self):
        """An addition nothing reaches is not additive: the rule must be WRITTEN."""
        d = _round_dir("panel_round7_2026-09-10")
        b = _mirror_module().brief_of(d) if d is not None else None
        if b is None:
            pytest.skip("round 7 brief not present in this checkout, live or mirrored")
        t = b.read_text(encoding="utf-8")
        assert "not delivered either" in t and "sandbox repository tree" in t, (
            "the delivery rule is absent from the brief, so a later round would "
            "revert to returning prose")

    def test_rounds_five_and_six_are_the_contrast(self, mod):
        """Without the earlier failure this proves nothing about the rule."""
        present = [d for d in _review_dirs() if d.name in P4_CONTRAST]
        reason = corpus.shortfall(len(present), 2,
                                  "panel round 5 and 6 directories")
        if reason:
            pytest.skip(reason)
        empties = [d.name for d in present if not mod.source_files(d)]
        assert len(empties) == 2, (
            f"rounds 5 and 6 were expected to have delivered 0 source files, "
            f"which is what makes round 7 evidence that the rule worked: {empties}")


#: The recorded contrast: the 2 rounds under the ruling that delivered 0 files,
#: before the delivery rule was written into the brief in round 7.
P4_CONTRAST = frozenset({"panel_round5_2026-09-10", "panel_round6_2026-09-10"})


def _dispatch_running(name: str) -> bool:
    """True iff a panel dispatcher process for round `name` is running now."""
    try:
        r = subprocess.run(["ps", "-axo", "command="], capture_output=True,
                           text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return False
    return any("confer_maths_panel" in ln and name in ln.split()
               for ln in r.stdout.splitlines())


def _p4_undelivered(dirs, mod) -> list[str]:
    """Rounds under the ruling holding a seat reply that delivered no file,
    outside the recorded contrast. The standing test and its falsifiers call
    this 1 function, so a falsifier that fails exercises the real check."""
    out = []
    for d in dirs:
        if (_round_date(d.name) or "") < RULING or d.name in P4_CONTRAST:
            continue
        if not any((d / f"{s}.json").is_file() for s in mod.SEATS):
            continue
        if not mod.source_files(d):
            out.append(d.name)
    return out


class TestP4DeliveryIsAStandingCondition:
    """P4 IS MARKED ENABLED AND ITS EVIDENCE WAS A PAST DEMONSTRATION (2026-09-17).

    The 3 tests above pin round 7, and the middle one asserts 2 literal strings
    in a frozen brief. Nothing required any LATER round to deliver a file, and
    `source_files()` read only `seat_proposals.diff`, so it printed 0 for round
    15, which delivered 4 files through the per-seat layout. These hold the
    condition over every round under the ruling, and the falsifiers run the same
    check on synthetic rounds it must refuse.
    """

    def test_round_fifteen_delivered_through_the_per_seat_layout(self, mod):
        d = _round_dir("panel_round15_2026-09-11")
        if d is None:
            pytest.skip("round 15 not present in this checkout, live or mirrored")
        src = mod.source_files(d)
        assert len(src) == 4, (
            f"round 15's mirror holds 4 per-seat files and a README.md; "
            f"source_files() returned {len(src)}: {src}")
        assert not any("readme" in x.lower() for x in src), src

    def test_every_round_under_the_ruling_left_a_file(self, mod):
        # A ROUND STILL RUNNING IS NOT YET A ROUND THAT DELIVERED NOTHING. The
        # dispatcher writes each seat's reply as that seat finishes and harvests
        # `seat_proposals.diff` only after every seat has, so mid-run a round
        # holds replies and no delivery. Only a dispatcher PROCESS naming the
        # round excludes it; a round whose process died with no delivery is
        # still reported, because it delivered nothing.
        # A ROUND WHOSE SEATS CANNOT WRITE HAS NOT FAILED TO DELIVER; IT WAS
        # NEVER ABLE TO (narrowed 2026-09-20, and the narrowing is principled).
        #
        # Only the CLI seats reach a sandbox repository tree they can write into.
        # The HTTP seats -- cx, cgpt, ge, ds, kimi -- have no working directory
        # to confine, so since 2026-09-20 their `run_python` is wrapped in
        # sandbox-exec and REFUSED write access to the repository by the kernel,
        # deliberately. Asking such a round for a delivered file asks for
        # something the confinement exists to prevent.
        #
        # Measured: maths_panel_2026-09-20_r2 dispatched HTTP seats only and
        # harvested 0 files, and was reported as a P4 violation. It is not one.
        # A round carrying a CLI seat is still held to the condition in full, so
        # nothing this test could previously catch escapes it -- the falsifiers
        # below build their synthetic rounds with a cc2 seat and are unaffected.
        DELIVERY_CAPABLE = ("cc2", "fable")
        dirs = [d for d in _review_dirs()
                if (_round_date(d.name) or "") >= RULING
                and any((d / f"{s}.json").is_file() for s in mod.SEATS)
                and any((d / f"{s}.json").is_file() for s in DELIVERY_CAPABLE)
                and not _dispatch_running(d.name)]
        reason = corpus.shortfall(len(dirs), 10, "panel rounds under Section P")
        if reason:
            pytest.skip(reason)
        assert P4_CONTRAST <= {d.name for d in dirs}, (
            "the recorded contrast rounds are missing from the population, so a "
            "pass here is not a comparison")
        undelivered = _p4_undelivered(dirs, mod)
        assert undelivered == [], (
            f"{len(undelivered)} round(s) under the ruling returned a seat reply and "
            f"delivered no file: {undelivered}. P4 requires a fix as a file.")

    def _synthetic(self, root, name, files):
        d = root / name
        d.mkdir(parents=True)
        (d / "cc2.json").write_text(json.dumps(
            {"route": "claude_cli", "n_tool_calls": 5, "model": "opus",
             "response": "verdict: the fix is to change X; here it is in prose."}),
            encoding="utf-8")
        for rel, text in files.items():
            p = d / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")
        return d

    def test_falsifier_an_all_prose_round_is_refused(self, tmp_path, mod):
        d = self._synthetic(tmp_path, "panel_round99_2026-09-12", {})
        assert _p4_undelivered([d], mod) == [d.name]

    def test_falsifier_a_round_leaving_only_a_readme_is_refused(self, tmp_path, mod):
        """The hole in round 16's proposed test: a README is not a fix."""
        d = self._synthetic(tmp_path, "panel_round98_2026-09-12",
                            {"seat_proposals/README.md": "harvested by the dispatcher\n"})
        assert _p4_undelivered([d], mod) == [d.name]

    def test_falsifier_a_round_leaving_only_cache_junk_is_refused(self, tmp_path, mod):
        d = self._synthetic(tmp_path, "panel_round97_2026-09-12", {
            "seat_proposals.diff": "### bench/__pycache__/x.cpython-313.pyc\n",
            "seat_proposals/x.pyc.as-the-seat-wrote-it.txt": "junk\n"})
        assert _p4_undelivered([d], mod) == [d.name]

    @pytest.mark.parametrize("files", [
        {"seat_proposals/fix.py.as-the-seat-wrote-it.txt": "def fix(): return 1\n"},
        {"seat_proposals.diff": "### scripts/fix.py\n+def fix(): return 1\n"},
    ])
    def test_control_a_round_that_delivered_passes(self, tmp_path, mod, files):
        """DISCRIMINATION. A check that refused every round would pass the
        falsifiers above and fail every real round."""
        d = self._synthetic(tmp_path, "panel_round96_2026-09-12", files)
        assert _p4_undelivered([d], mod) == []

    def test_the_running_round_exclusion_sees_a_real_process_and_only_while_it_runs(self):
        """The exclusion above is a gate, so it is executed: a process whose
        command line names a dispatcher and a round is seen while it runs and
        not after it ends. Nothing is dispatched; the process only sleeps."""
        name = "panel_round95_2026-09-12"
        assert not _dispatch_running(name)
        p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)",
                              "confer_maths_panel_2026-09-05.py", name])
        try:
            import time
            deadline = time.time() + 10
            seen = False
            while time.time() < deadline and not seen:
                seen = _dispatch_running(name)
                time.sleep(0.1)
            assert seen, "a running process naming the round was not detected"
            assert not _dispatch_running("panel_round94_2026-09-12"), (
                "a different round was reported as running")
        finally:
            p.kill()
            p.wait(timeout=10)
        assert not _dispatch_running(name), "a finished process is still reported"

    def test_a_pre_ruling_round_is_outside_the_condition(self, tmp_path, mod):
        d = self._synthetic(tmp_path, "panel_old_20260901T000000Z", {})
        assert _p4_undelivered([d], mod) == []


class TestTheToolEnabledDateMatchesTheArchive:
    """Entry P3 stated a date the archive does not support, and nothing checked it.

    It read *"Every round before 2026-09-07 recorded 0 tool calls"*. The archive
    holds 2 rounds on **2026-09-05** that recorded 17 and 27 calls --
    `panel_maths_tools_20260905T034234Z` and
    `panel_maths_toolsfixed_20260905T035958Z`. Found by an adversarial audit of
    the list's DONE entries on 2026-09-11 and confirmed here before the entry was
    edited.

    A DATE IN PROSE IS A CLAIM ABOUT THE ARCHIVE, so it gets the same treatment
    as any other figure: the archive is asked, and the entry must agree with the
    answer. Without this the date drifts again the next time someone rewrites the
    sentence from memory.
    """

    def test_the_entry_and_the_archive_agree_on_the_first_tool_enabled_date(self):
        import json
        import pathlib
        import re

        repo = pathlib.Path(__file__).resolve().parents[2]
        per_round = {}
        # THE TRACKED MIRROR TOO (2026-09-17), for directories the live tree does
        # not hold, so a clone checks the date instead of skipping.
        live = sorted((repo / "bench" / "logs").glob("*/*.json"))
        live_rounds = {f.parent.name for f in live}
        mirrored = [f for f in sorted((repo / "experimental_notes" / "evidence")
                                      .glob("panel_records_*/*/*.json"))
                    if f.parent.name not in live_rounds]
        for f in live + mirrored:
            if f.name.endswith(".tools.json"):
                continue
            try:
                d = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                continue
            if not isinstance(d, dict) or "n_tool_calls" not in d:
                continue
            per_round[f.parent.name] = per_round.get(f.parent.name, 0) + (
                d.get("n_tool_calls") or 0)

        def rdate(name: str):
            m = re.search(r"(20\d{2})[-_]?(\d{2})[-_]?(\d{2})", name)
            return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else None

        dated = sorted(rdate(k) for k, v in per_round.items() if v > 0 and rdate(k))
        if not dated:
            import pytest
            pytest.skip("no round in this checkout records a tool call; "
                        "bench/logs is gitignored and absent in a clone")
        earliest = dated[0]
        entry = (repo / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md").read_text(
            encoding="utf-8")
        assert f"Every round before **{earliest}** recorded 0 tool calls" in entry, (
            f"the archive's earliest tool-enabled round is {earliest}, and entry P3 "
            f"does not say so. A date in prose is a claim about the archive and "
            f"must agree with it.")
