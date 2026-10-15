"""The specification is delivered whole, and the caps still bound the work.

FOUNDER'S RULING, 2026-10-14, which is what this file enforces: *"as far as any
caps have ever existed, their intention was to never feed any model more work
than they were demonstrably able to handle, especially for weaker models like
Deepseek, and we built considerable machinery around this principle. There was
never an intent as far as I recall to applying this same reasoning to the core
operational directives themselves."* And: *"7000 or so words for a system prompt
is hardly excessive for any modern model? Why should we need to cut it at all?"*

4 DEFECTS WERE FOUND BY DRAWING THAT LINE IN CODE, and each one has its own
class below. Producer for every figure quoted here:
`scripts/the_spec_is_not_work_2026-10-15.py`.

  1. `_load_universal_directive` chose the reduced form by the WORK cap, so 5 of
     5 models got it unconditionally (100.0000%, Wilson [56.5518%, 100.0000%]).
  2. The reduced form carried 0 of 22 HARD blocks by verbatim containment
     (0.0000%, Wilson [0.0000%, 14.8655%]), the 22 including the whole of
     "Falsifier Integrity -- Do Not Reach for the Answer".
  3. `resolve_layer_conflicts` resolved the specification AGAINST ITSELF: 40 of
     42 conflicts were SAME-PACKET (95.2381%, Wilson [84.2101%, 98.6842%]), and
     41 of the 42 deletions had a HARD loser by the resolver's own HARD
     predicate (an earlier reading of 11 is WITHDRAWN -- it tested the
     100-character truncated `loser_text`, which drops the packet class).
  4. The decomposition decision counted a payload it cannot split. 6 of 6
     simulated seats (100.0000%, Wilson [60.9666%, 100.0000%]) have an effective
     limit below the 74,177-character system prompt, so every simulated dispatch
     would have force-decomposed on the size of its own instructions -- while no
     paid seat would have.

EVERY TEST HERE EXECUTES THE CODE. None asserts on source text, because a test
that reads a module only establishes that the module describes itself
consistently (`execute-do-not-grep`, measured 2026-09-04).
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "bench"))

from bench.cdsfl_registry import composer as C  # noqa: E402

DIRECTIVES = pathlib.Path(C.DIRECTIVES_DIR)
CORE = DIRECTIVES / "universal" / "cdsfl_core_formal.md"
DOMAINS = sorted(
    p.name for p in DIRECTIVES.iterdir() if p.is_dir() and p.name != "universal"
)


@pytest.fixture(scope="module")
def core() -> str:
    return CORE.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def hard_blocks(core) -> list[str]:
    return [b for b in C._split_packet_directives(core) if C._block_is_hard(b)]


def _preliminary(packets, model="opus_4_6", domain="structural"):
    return C.ComposedDirectiveSet(
        packets=packets,
        rendered_text=C._render_directive_text(packets),
        policy={}, cid="guard", constraint_count=1, token_estimate=1,
        constraint_density=0.0,
        coherence_budget=C.MODEL_COHERENCE_BUDGETS.get(
            model, C.DEFAULT_COHERENCE_BUDGET),
        pruned_soft=[], manifest={"model": model, "domain": domain},
    )


def _three_layers(domain: str, model: str = "opus_4_6"):
    packets = [C._load_universal_directive(model)]
    dp = C._load_domain_directive(domain, variant=None)
    if dp is not None:
        packets.append(dp)
    packets.append(C._build_situation_packet(
        review_target="scripts/t.py", code_extracts="def f(x):\n    return x\n",
        verified_facts="", explicit_unknowns="",
        adversarial_brief="Find what is wrong, not what is right.",
        interaction_surface=""))
    return packets


class TestTheTwoBoundsAreDistinct:
    def test_the_fields_exist_and_default_as_ruled(self):
        t = C.PhenotypeTransform()
        assert t.spec_chars is None, (
            "the SPECIFICATION bound no longer defaults to 'deliver whole'")
        assert t.max_directive_chars == 8000, (
            "the WORK bound's default moved; the ruling did not license that")

    def test_the_work_bound_cannot_cut_the_specification(self, core):
        """EXECUTED: a model with a 10-character WORK cap still gets it whole."""
        probe = "spec_not_work_probe"
        try:
            C.PHENOTYPE_TRANSFORMS[probe] = C.PhenotypeTransform(
                max_directive_chars=10)
            assert C._load_universal_directive(probe).text == core
        finally:
            C.PHENOTYPE_TRANSFORMS.pop(probe, None)

    def test_the_specification_bound_does_cut_it(self, core):
        """The SPECIFICATION bound selects the reduced form.
        ★ `spec_chars` IS 20,000, DELIBERATELY: below the 27,803-character
        specification so the reduced form is SELECTED, and above the
        8,367-character faithful render so it FITS. A bound below 8,367 raises
        instead, which is correct and is covered by its own test.
        """
        probe = "spec_not_work_probe"
        try:
            C.PHENOTYPE_TRANSFORMS[probe] = C.PhenotypeTransform(
                max_directive_chars=99_999, spec_chars=20_000)
            got = C._load_universal_directive(probe).text
            assert got != core and len(got) < len(core)
            assert len(got) > 5_000, (
                f"the reduced form is only {len(got)} chars; it is supposed to "
                f"carry every HARD block")
        finally:
            C.PHENOTYPE_TRANSFORMS.pop(probe, None)

    def test_a_minimal_style_model_with_a_tiny_work_bound_does_not_raise(self):
        """★ A LATENT RAISE THE P-PASS FOUND. `_load_universal_directive` passed
        `max_directive_chars` to `_render_universal_minimal`, whose `max_chars`
        RAISES rather than truncating -- correctly, since a specification cut to
        fit is the defect being closed. But the faithful render is 8,367
        characters, so any model configured `format_style="minimal"` with a work
        bound below that would have raised. `deepseek_v3` was the only such
        model and moved to "concise", so no live config reached it; a latent
        raise on a reachable branch is a defect whether or not a current config
        hits it."""
        probe = "min_style_probe"
        try:
            C.PHENOTYPE_TRANSFORMS[probe] = C.PhenotypeTransform(
                max_directive_chars=4000, format_style="minimal")
            got = C._load_universal_directive(probe)
            assert len(got.text) > 4000, (
                "the reduced form now fits a 4000-character WORK bound, so this "
                "test no longer exercises the branch it was written for")
            C.PHENOTYPE_TRANSFORMS[probe] = C.PhenotypeTransform(
                max_directive_chars=99_999, format_style="minimal",
                spec_chars=100)
            with pytest.raises(ValueError):
                C._load_universal_directive(probe)
        finally:
            C.PHENOTYPE_TRANSFORMS.pop(probe, None)

    def test_deepseek_keeps_every_work_setting_it_had(self):
        """The weakest seat's work machinery is what the ruling PROTECTS. If
        this ever goes red the repair has been misread as cap-lifting."""
        t = C.PHENOTYPE_TRANSFORMS["deepseek_v3"]
        assert t.max_directive_chars == 4000
        assert t.strip_examples and t.strip_rationale
        assert t.simplify_language and t.compress_tables


class TestADomainThatMatchesNothingIsLoud:
    """★ FOUND 2026-10-15 while choosing the domain for the 2 free runs. The
    launcher's own resume command says `--domain statistics` and there is no
    `statistics` directory, so every such run composed NO domain layer while the
    manifest still recorded `"domain": "statistics"`.

    Measured by `scripts/a_domain_name_that_matches_nothing_2026-10-15.py` over
    every `"domain"` value in every shipped config, resolved through the live
    loader: **16 of 47 references resolve to nothing — 34.0426%, Wilson
    [22.1674%, 48.3291%], Clopper-Pearson [20.8641%, 49.3132%]** — and **6 of
    the 9 distinct names match nothing — 66.6667%, Wilson [35.4202%,
    87.9416%]**: `biology`, `cs_software`, `engineering`, `information_science`,
    `physics`, `statistics`.

    IT WARNS AND DOES NOT REFUSE. Refusing would break 16 of 47 shipped
    references at once, and whether those 6 names should acquire directories or
    be renamed is the founder's call.
    """

    def test_an_unmatched_domain_warns_and_returns_none(self):
        import warnings
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            got = C._load_domain_directive("statistics", None)
        assert got is None
        msgs = [str(w.message) for w in caught
                if "NO DOMAIN LAYER" in str(w.message)]
        assert msgs, "an unmatched domain is still silent"
        assert "statistics" in msgs[0] and "mathematics" in msgs[0], (
            f"the warning does not name the domain and the shipped list: {msgs[0]}")

    def test_a_matched_domain_is_silent(self):
        import warnings
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            got = C._load_domain_directive("mathematics", None)
        assert got is not None and len(got.text) > 1000
        assert not [w for w in caught if "NO DOMAIN LAYER" in str(w.message)], (
            "a domain that DOES resolve is warning, so the warning is noise")

    def test_the_free_runs_use_a_domain_that_resolves(self):
        """The launch script must not name a domain that composes nothing."""
        script = (ROOT / "scripts" / "local"
                  / "launch_free_runs_2026-10-15.sh").read_text(encoding="utf-8")
        import re
        named = re.findall(r"--domain\s+([A-Za-z_-]+)", script)
        assert named, "the launch script names no domain"
        for domain in set(named):
            assert C._load_domain_directive(domain, None) is not None, (
                f"the launch script passes --domain {domain}, which composes no "
                f"domain layer at all")


class TestTheReducedFormIsFaithful:
    def test_every_hard_block_verbatim(self, hard_blocks):
        mini = C._render_universal_minimal()
        missing = [b.splitlines()[0][:60] for b in hard_blocks if b not in mini]
        assert not missing, f"{len(missing)} of {len(hard_blocks)} absent: {missing}"

    def test_the_count_is_what_the_producer_measured(self, hard_blocks):
        assert len(hard_blocks) == 22, (
            f"the HARD set is now {len(hard_blocks)}, not the 22 every figure in "
            f"this file's docstring was measured over; remeasure before editing")

    def test_a_first_eight_words_probe_would_understate_it(self, hard_blocks):
        """THE INSTRUMENT THAT FAILED, PINNED SO IT CANNOT BE REINTRODUCED.
        It space-joins across newlines, so it cannot match a multi-line block.
        """
        mini = C._render_universal_minimal().lower()

        def probe(t: str) -> str:
            return " ".join(t.split()[:8]).strip("#*-| ").lower()

        by_probe = sum(1 for b in hard_blocks if probe(b) and probe(b) in mini)
        by_verbatim = sum(1 for b in hard_blocks if b in C._render_universal_minimal())
        assert by_verbatim == len(hard_blocks)
        assert by_probe < by_verbatim, (
            "the probe no longer understates, so the multi-line blocks it "
            "cannot see have gone -- recheck the specification")


class TestTheResolverNeverDeletesTheSpecification:
    def test_a_packet_never_resolves_against_itself(self):
        total = same_packet = 0
        for domain in DOMAINS:
            _r, conflicts = C.resolve_layer_conflicts(
                _preliminary(_three_layers(domain), domain=domain))
            for c in conflicts:
                total += 1
                if c.winner_layer == c.loser_layer and c.winner_packet == c.loser_packet:
                    same_packet += 1
        assert same_packet == 0, (
            f"{same_packet} of {total} conflicts are a packet against itself")

    def test_no_hard_directive_is_ever_deleted(self):
        deleted = []
        for domain in DOMAINS:
            for flag in (False, True):
                _r, conflicts = C.resolve_layer_conflicts(
                    _preliminary(_three_layers(domain), domain=domain),
                    delete_soft_loser=flag)
                for c in conflicts:
                    if c.deleted and C._block_is_hard(c.loser_text):
                        deleted.append((domain, flag, c.topic,
                                        c.loser_text.splitlines()[0][:50]))
        assert not deleted, f"HARD directives deleted: {deleted}"

    def test_every_packet_passes_through_byte_identical_by_default(self):
        """THE PROPERTY, AND THE FIRST VERSION OF THIS TEST ASKED THE WRONG
        QUESTION. It re-split each packet and checked block membership, but
        `_split_packet_directives` STRIPS every line, so a stripped block is
        not a substring of an indented original -- the test reported 701
        "losses" against text that was byte-identical. Byte equality is both
        simpler and strictly stronger, and it catches the structural reflow
        (blank lines, indentation) that block membership cannot see.
        """
        differing = []
        for domain in DOMAINS:
            packets = _three_layers(domain)
            before = [(p.layer, p.name, p.text) for p in packets]
            after, _c = C.resolve_layer_conflicts(
                _preliminary(packets, domain=domain))
            got = {(p.layer, p.name): p.text for p in after.packets}
            for layer, name, text in before:
                if got.get((layer, name)) != text:
                    delivered = got.get((layer, name))
                    differing.append((domain, layer, name, len(text),
                                      None if delivered is None else len(delivered)))
        assert not differing, (
            f"{len(differing)} packets were altered although nothing was "
            f"dropped: {differing[:5]}")

    def test_the_deleting_capability_is_retained_and_reachable(self):
        """Additive standard: the behaviour is RETIRED from the default path,
        not removed. If the flag stops changing anything, the capability has
        become an addition nothing reaches."""
        assert C.CONFLICT_DELETES_SOFT_LOSER is False
        changed_on = changed_off = 0
        for domain in DOMAINS:
            for flag in (True, False):
                packets = _three_layers(domain)
                before = {(p.layer, p.name): p.text for p in packets}
                after, _c = C.resolve_layer_conflicts(
                    _preliminary(packets, domain=domain), delete_soft_loser=flag)
                got = {(p.layer, p.name): p.text for p in after.packets}
                n = sum(1 for k, v in before.items() if got.get(k) != v)
                if flag:
                    changed_on += n
                else:
                    changed_off += n
        assert changed_off == 0, changed_off
        assert changed_on > 0, (
            "delete_soft_loser=True changes nothing, so the retained "
            "capability is inert")


class TestTheCapStillBoundsWork:
    def test_the_specification_survives_every_models_cap(self, core):
        for model in C.PHENOTYPE_TRANSFORMS:
            composed = C.compose(
                task_domain="structural", model=model,
                review_target="scripts/t.py", code_extracts="x = 1\n" * 500,
                adversarial_brief="b")
            assert core[:400] in composed.rendered_text, (
                f"{model} lost the head of the specification to the cap")
            assert "Falsifier Integrity" in composed.rendered_text, (
                f"{model} lost the falsifier-integrity section to the cap")

    def test_the_cap_still_cuts_work_for_the_weakest_seat(self):
        composed = C.compose(
            task_domain="structural", model="deepseek_v3",
            review_target="scripts/t.py", code_extracts="x = 1\n" * 500,
            adversarial_brief="b")
        record = composed.manifest["length_cap"]
        assert record["fired"] is True, (
            "the cap no longer fires for deepseek_v3 on a large work payload, "
            "which would mean the work bound had been lifted")
        assert record["work_cap"] == 4000
        assert record["spec_chars_exempt"] > 20_000
        assert all(p["layer"] != "universal" for p in record["packets_cut"]), (
            f"the cap cut the specification: {record['packets_cut']}")

    def test_the_manifest_records_both_bounds(self):
        composed = C.compose(task_domain="structural", model="opus_4_6",
                             review_target="t.py", code_extracts="x = 1\n")
        pt = composed.manifest["phenotype_transform"]
        assert "spec_chars" in pt and pt["spec_chars"] is None
        assert pt["max_directive_chars"] == 12000


class TestTheDecompositionDecisionCountsWorkItCanSplit:
    @pytest.fixture(scope="class")
    def rr(self):
        import reference_runner_v3
        return reference_runner_v3

    @pytest.fixture(scope="class")
    def mgr(self):
        class Cfg:
            pre_decompose_models = ()

        class Mgr:
            config = Cfg()

        return Mgr()

    def test_legacy_callers_are_unchanged(self, rr, mgr):
        from run_exp17_immune import _should_decompose
        for total in range(0, 200_001, 7_919):
            new = rr.should_decompose_v2("NOFP_GUARD", mgr, payload_chars=total)
            legacy = (True if total > rr.DECOMPOSE_HARD_FLOOR_CHARS
                      else _should_decompose("NOFP_GUARD", mgr, payload_chars=total))
            assert new == legacy, total

    def test_the_floor_now_judges_the_decomposable_payload(self, rr, mgr):
        """A seat with a large proven limit must NOT decompose a small work
        payload merely because its instructions are long."""
        spec, work = 74_177, 20_000
        assert rr.should_decompose_v2(
            "CC2", mgr, payload_chars=spec + work,
            decomposable_chars=work, fixed_chars=spec) is False
        assert rr.should_decompose_v2(
            "CC2", mgr, payload_chars=spec + 90_000,
            decomposable_chars=90_000, fixed_chars=spec) is True

    def test_decomposition_is_refused_when_it_cannot_help(self, rr, mgr):
        """Every simulated seat's effective limit is below the system prompt,
        so no chunk count brings a turn under it -- proved unsat in z3."""
        spec = 74_177
        for seat in ("CC2-SIM", "ChatGPT-SIM", "Codex-SIM",
                     "DeepSeek-SIM", "Fable-SIM", "Gemini-SIM"):
            assert rr._decomposition_is_futile(seat, mgr, spec) is True, seat
            assert rr.should_decompose_v2(
                seat, mgr, payload_chars=spec + 20_000,
                decomposable_chars=20_000, fixed_chars=spec) is False, seat

    def test_a_paid_seat_is_not_futile(self, rr, mgr):
        for seat in ("CC2", "ChatGPT", "Codex", "Gemini", "DeepSeek"):
            assert rr._decomposition_is_futile(seat, mgr, 74_177) is False, seat

    def test_an_explicit_override_is_honoured_over_the_futility_argument(self, rr):
        class Cfg:
            pre_decompose_models = ("CC2-SIM",)

        class Mgr:
            config = Cfg()

        assert rr.should_decompose_v2(
            "CC2-SIM", Mgr(), payload_chars=94_177,
            decomposable_chars=20_000, fixed_chars=74_177) is True

    def test_the_guard_reads_the_same_cache_as_the_decision(self, rr):
        from run_exp17_immune import _load_fingerprint_cache
        assert rr._load_fingerprint_cache is _load_fingerprint_cache, (
            "the futility guard and the decomposition decision would read "
            "different fingerprint caches and could disagree about a seat")
