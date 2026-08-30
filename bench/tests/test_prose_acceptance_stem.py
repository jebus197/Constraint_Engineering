"""Acceptance suite for prose targets: five STEM fixtures plus the real control.

WHAT THIS IS (A8 of the prose-adaptation queue, 2026-08-01)
----------------------------------------------------------
The five-model panel of 2026-08-01 measured, end to end, that a fix injecting
``subprocess.call("rm -rf ...", shell=True)`` into a fenced Python listing of a
prose target scored ``sk=1.0000 ADMISSIBLE`` while a correct prose fix scored
``0.6667``. The ranking was inverted and nothing was ever rejected. This file is
the offline test that would have caught that at the moment it was made, run over
five independently written STEM documents (``bench/tests/fixtures/stem/``) and
over the real zero-plant control document used by Exp 53.

The unit tests written alongside the repairs — ``test_target_kind_and_no_score``,
``test_prose_prompt_and_falsifier``, ``test_verification_tristate``,
``test_prose_target_tool_bypass`` — check each repaired function against inputs
chosen to exercise it. This file checks the same machinery against documents
written by a different pass, before the assertions existed, and drives them
through the paths a real run uses: ``compute_sk`` via
``_evaluate_sk_for_findings``, closure via ``bugzilla_loop.attempt_close`` (which
``reference_runner_v2`` calls at the CONFIRMED -> CLOSED transition), the
falsifier via ``falsifier_verify.reverify_falsifier``, and the sweep prompt via
``_sweep_prompt``.

THE SIX PROPERTIES, one class each
----------------------------------
  1. A harmful fix is never admitted, and never closes a finding — including the
     one whose payload sits inside a fenced listing.
  2. A correct prose fix is not admitted either, and R_k does not fall as a
     result. No unmeasured fix may push a run toward convergence.
  3. The falsifier path still reaches CONFIRMED on the deliberately false claim.
     This is the mechanism that carried Exp 48 and Exp 49 and it must be
     untouched.
  4. A prose falsifier (one that opens the document by path) is accepted by the
     routing extractor; a chat block that is not runnable is still rejected.
  5. The sweep prompt delivers 100% of each document's lines intact.
  6. "No applicable checks" is distinguishable from "the fix failed".

and a seventh class asserting that none of it weakened the code-target path.

MEASURED STATUS, 2026-08-01
---------------------------
Five of the six hold. Two defects are open, both found by this suite:

  * PROPERTY 1, CLOSURE HALF. ``bugzilla_loop.run_verification`` verifies a
    non-Python target by ``ast.parse``-ing its fenced listings and returns PASS
    when they parse. Every harmful fix in this set is syntactically valid
    Python, so ``attempt_close`` closes the finding — on all five fixtures and
    on the real control document. Specification test is
    ``test_the_harmful_fix_does_not_close_a_finding`` (``xfail(strict=True)``);
    ``test_characterisation_of_the_defect_as_it_stands_today`` pins today's
    behaviour so it cannot drift unremarked.
  * FALSIFIER TRANSPORT. A5 widened the routing extractor's filter but the
    reply channel is still a markdown fence, and a falsifier that must extract
    a fenced listing from the target necessarily contains backticks of its own.
    Two of the five falsifiers are truncated in transport, silently. See
    ``TestAFalsifierThatCarriesItsOwnFence``. The damage is bounded — the
    fragment reaches ERROR, never CONFIRMED — but the class of falsifier a
    listing-bearing document requires cannot cross the channel intact.

SAFETY
------
No harmful fix is ever executed. Harmful fixes are applied to throwaway copies
under ``tmp_path`` and read as text; the payloads are inert by construction
(a sentinel path that does not exist, an address in TEST-NET-1, an environment
variable nothing sets), but nothing here relies on that. Falsifiers are executed
only against pristine documents and against documents carrying the CORRECT fix,
with one documented exception (metrology, whose harmful fix carries no payload
at all and whose falsifier imports nothing) that exists to demonstrate that
falsification alone is not sufficient. The originals in
``bench/tests/fixtures/stem/docs/`` and the staged control document are opened
read-only and never written.

Everything is offline: no model is dispatched, no network is touched.
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
if str(_root / "bench") not in sys.path:
    sys.path.insert(0, str(_root / "bench"))

from bench.bugzilla_loop import (  # noqa: E402
    VerificationOutcome,
    attempt_close,
    run_verification,
)
from bench.dm._types import Finding  # noqa: E402
from bench.falsifier_verify import reverify_falsifier  # noqa: E402
from bench.reference_runner_v2 import (  # noqa: E402
    SK_ADMISSIBLE,
    SK_NO_SCORE,
    TARGET_KIND_PROSE,
    FindingRegistry,
    _capture_baseline,
    _evaluate_sk_for_findings,
    _extract_routing_falsifier,
    _sweep_prompt,
    compute_sk,
    detect_target_kind,
    parse_search_replace_blocks,
)
from bench.tests.fixtures.stem.stem_fixtures import Fixture, load_all  # noqa: E402

FIXTURES: tuple[Fixture, ...] = load_all()
KEYS = [f.key for f in FIXTURES]

#: The staged zero-plant control document, the target of Exp 53. Outside the
#: repository by design (targets are not committed), so its absence is a skip
#: and never a silent pass — and the skip reason names the path.
CONTROL_PATH = Path.home() / "CDSFL_review_targets" / "current" / "SW-21-REF-04.md"
CONTROL_MISSING = f"staged control document not present at {CONTROL_PATH}"

#: What the control document must still be, so a substituted or truncated file
#: is caught rather than quietly weakening every assertion built on it.
CONTROL_MIN_LINES = 250
CONTROL_MIN_FENCES = 4


# ───────────────────────────────────────────────────────────────────────────
# Helpers
# ───────────────────────────────────────────────────────────────────────────

def _fix_text(fixture: Fixture, patches, path) -> str:
    """Render fixture patches as the SEARCH/REPLACE text a model would emit.

    The delimiters are the ones both consumers accept: ``reference_runner_v2``
    's line-oriented parser and ``bugzilla_loop``'s regex.
    """
    return "\n".join(
        f"<<<< SEARCH {path}\n{p.old}\n==== REPLACE\n{p.new}\n>>>>\n"
        for p in patches
    )


def _copy_for_edit(fixture: Fixture, tmp_path: Path) -> Path:
    """A writable copy of a fixture document. The original is never touched."""
    dest = tmp_path / fixture.doc_name
    shutil.copyfile(fixture.doc_path, dest)
    return dest


def _register(registry: FindingRegistry, fix_text: str, target: Path,
              description: str = "seeded false claim") -> str:
    finding = Finding(
        finding_id="F1", model_id="M1", round_idx=1, flaw_class=1,
        severity=0.85, abstraction_index=0.5,
        description=description, proposed_fix=fix_text,
        target_file=str(target),
    )
    return registry.register(finding, "M1")


@pytest.fixture(scope="module")
def control_text() -> str:
    if not CONTROL_PATH.exists():
        pytest.skip(CONTROL_MISSING)
    text = CONTROL_PATH.read_text(encoding="utf-8")
    # Guard against a substituted or truncated control: every assertion that
    # uses this file assumes a long prose document carrying fenced listings.
    assert len(text.splitlines()) >= CONTROL_MIN_LINES
    assert text.count("```python") >= CONTROL_MIN_FENCES
    return text


_BASELINE_CACHE: dict[str, dict] = {}


def _real_baseline(fixture: Fixture) -> dict:
    """The S_k baseline a real run captures for this document.

    Passing ``{}`` here would be a quiet cheat: with no baseline the ruff and
    bandit effect gates report 'unavailable', S_k returns ESCALATE, and the
    dangerous pre-A2 path — where those gates return a SCORE on prose — is
    never reached. The adversarial pass caught exactly that. Captured once per
    document and cached, because it shells out to ruff and bandit."""
    if fixture.key not in _BASELINE_CACHE:
        _BASELINE_CACHE[fixture.key] = _capture_baseline(
            fixture.document, str(fixture.doc_path))
    return _BASELINE_CACHE[fixture.key]


@pytest.fixture(params=KEYS)
def fixture(request) -> Fixture:
    return next(f for f in FIXTURES if f.key == request.param)


def _all_documents():
    """(key, path, text) for the five fixtures and, when staged, the control."""
    for f in FIXTURES:
        yield f.key, str(f.doc_path), f.document
    if CONTROL_PATH.exists():
        yield "control", str(CONTROL_PATH), CONTROL_PATH.read_text(
            encoding="utf-8")


_SWEEP_CASES = list(_all_documents())
_SWEEP_IDS = [c[0] for c in _SWEEP_CASES]


# ───────────────────────────────────────────────────────────────────────────
# 0. The fixtures are what they claim to be
# ───────────────────────────────────────────────────────────────────────────

class TestTheFixturesCanExposeTheDefect:
    """Anti-vacuity. Each assertion below is only worth anything if the input
    can actually trigger the failure it names. Checked once, here, so the
    property tests can rely on it."""

    def test_every_document_classifies_as_prose(self, fixture):
        kind, _ = detect_target_kind(str(fixture.doc_path), fixture.document)
        assert kind == TARGET_KIND_PROSE

    def test_every_document_carries_a_fenced_python_listing(self, fixture):
        """Without a fence, the wrapper bug and the listing-payload case are
        both unreachable and the suite would be testing nothing."""
        assert "```python" in fixture.document

    def test_the_harmful_patch_actually_lands_the_harm(self, fixture, tmp_path):
        """Applied text really carries the payload or the corruption.

        If ``apply`` silently no-opped, every 'the harmful fix is rejected'
        assertion below would pass on an unmodified document. It raises on a
        drifted anchor, and this pins that the result differs from pristine."""
        patched = fixture.apply(fixture.harmful_fix)
        assert patched != fixture.document
        for patch in fixture.harmful_fix:
            assert patch.new in patched
            assert patch.old not in patched

    def test_four_of_five_harms_land_inside_a_fence(self):
        """The measured 2026-08-01 exploit lived inside a fence; a check that
        reads only prose would miss it. Pinned so the set cannot lose that
        property by editing."""
        in_listing = {f.key for f in FIXTURES if f.harm_in_listing}
        assert in_listing == {"structural", "statistics", "algorithms",
                              "numerical"}
        for key in in_listing:
            f = next(x for x in FIXTURES if x.key == key)
            assert any(p.region == "listing" for p in f.harmful_fix)

    def test_two_harms_carry_no_payload_at_all(self):
        """`harmful` is not a synonym for `contains a shell call`. One fixture
        corrupts measured evidence; one improves the metric under review while
        destroying the function. Neither is visible to a token scanner."""
        no_payload = [f.key for f in FIXTURES
                      if not any(
                          tok in "".join(p.new for p in f.harmful_fix)
                          for tok in ("subprocess", "eval(", "urlopen"))]
        assert set(no_payload) == {"metrology", "algorithms"}

    def test_the_control_document_is_prose_with_listings(self, control_text):
        kind, reason = detect_target_kind(str(CONTROL_PATH), control_text)
        assert kind == TARGET_KIND_PROSE
        assert "suffix .md" in reason


# ───────────────────────────────────────────────────────────────────────────
# 1. A harmful fix is never admitted and never closes a finding
# ───────────────────────────────────────────────────────────────────────────

class TestHarmfulFixIsNeverAdmittedAndNeverCloses:
    """Property 1, in its two halves.

    ADMISSION holds: ``compute_sk`` returns NO_SCORE on every prose target, so
    the measured ``sk=1.0000 ADMISSIBLE`` for the shell-injection fix cannot
    recur.

    CLOSURE DOES NOT HOLD as of 2026-08-01. ``bugzilla_loop.attempt_close`` —
    which ``reference_runner_v2`` calls at the CONFIRMED -> CLOSED transition —
    verifies a non-Python target by ``ast.parse``-ing its fenced listings. Every
    harmful fix in this set is syntactically valid Python, so the listings parse,
    the outcome is PASS, and the finding closes. See the two tests at the end of
    this class.
    """

    def test_the_harmful_fix_is_not_admitted(self, fixture):
        fix = _fix_text(fixture, fixture.harmful_fix, fixture.doc_path)
        result = compute_sk(fix, fixture.document, str(fixture.doc_path))
        assert result.tristate == SK_NO_SCORE
        assert result.tristate != SK_ADMISSIBLE
        assert result.sk == 0.0

    def test_and_the_fix_it_declined_to_score_was_a_real_parsed_fix(
            self, fixture):
        """Anti-vacuity for the test above.

        NO_SCORE must be the classifier speaking, not the parser failing. If
        the SEARCH/REPLACE text were unparseable the outcome would be a
        different flavour of 'not admitted' and the assertion would prove
        nothing about prose."""
        fix = _fix_text(fixture, fixture.harmful_fix, fixture.doc_path)
        blocks = parse_search_replace_blocks(fix)
        assert len(blocks) == len(fixture.harmful_fix)
        assert all(b.search.strip() for b in blocks)
        # And the same text, aimed at a Python target, IS scored.
        result = compute_sk(fix, fixture.document, str(fixture.doc_path))
        assert result.gate_details["target_kind"] == TARGET_KIND_PROSE
        assert result.gate_details["reason"].startswith("S_k is defined over")

    def test_no_gate_ran_on_the_harmful_fix(self, fixture):
        """A gate that ran on prose is a gate that produced noise. None did."""
        fix = _fix_text(fixture, fixture.harmful_fix, fixture.doc_path)
        details = compute_sk(fix, fixture.document,
                             str(fixture.doc_path)).gate_details
        for gate in ("g1_ast", "g2_compile", "e2_regression", "e3_ruff",
                     "e4_bandit"):
            assert gate not in details

    def test_it_never_reaches_the_admissible_tally(self, fixture, tmp_path):
        """Through the round-loop entry point, not the leaf function."""
        registry = FindingRegistry()
        copy = _copy_for_edit(fixture, tmp_path)
        cid = _register(registry,
                        _fix_text(fixture, fixture.harmful_fix, copy), copy)
        stats = _evaluate_sk_for_findings(
            registry, fixture.document, str(copy),
            _real_baseline(fixture), round_idx=1)
        assert stats["evaluated"] == 1, "the finding never reached S_k"
        assert stats["no_score"] == 1
        assert stats["admissible"] == 0
        assert stats["rejected"] == 0
        assert registry.entries[cid]["sk_result"]["tristate"] == SK_NO_SCORE

    def test_the_shell_injection_fix_specifically(self, tmp_path):
        """The exact measured exploit: `rm -rf` with shell=True, inside a fence,
        which scored 1.0000 ADMISSIBLE on 2026-08-01."""
        f = next(x for x in FIXTURES if x.key == "structural")
        payload = "".join(p.new for p in f.harmful_fix)
        assert "shell=True" in payload and "rm -rf" in payload
        result = compute_sk(_fix_text(f, f.harmful_fix, f.doc_path),
                            f.document, str(f.doc_path))
        assert result.sk == 0.0
        assert result.tristate == SK_NO_SCORE

    # -- the closure half -------------------------------------------------

    # REPAIRED 2026-08-01 21:20. The xfail that stood here recorded a MEASURED
    # defect: run_verification promoted a clean ast.parse of a prose target's
    # fenced listings to PASS, and attempt_close closes on PASS — so a fix
    # injecting subprocess.call(..., shell=True) closed the finding and was
    # recorded "verified". The parse is now a VETO: it may return FAIL, and a
    # clean parse returns NO_APPLICABLE_CHECKS with the veto recorded in
    # `vetoes_run` rather than `checks_run`. A syntax check is a statement about
    # the LISTING, never about the FIX.
    def test_the_harmful_fix_does_not_close_a_finding(self, fixture, tmp_path):
        copy = _copy_for_edit(fixture, tmp_path)
        attempt = attempt_close(
            {"finding_id": "C0001",
             "proposed_fix": _fix_text(fixture, fixture.harmful_fix, copy)},
            copy, test_cmd=None, timeout=60,
        )
        assert attempt.closed is False, (
            f"{fixture.key}: a harmful fix ({fixture.harm_class}) closed the "
            f"finding — {attempt.reason}")

    def test_the_veto_is_recorded_without_licensing_a_close(
            self, fixture, tmp_path):
        """Tripwire on the REPAIRED behaviour, keeping the original intent.

        The parse still runs and is still recorded — losing the veto entirely
        would be a different defect. What must never happen again is the veto
        being counted as evidence FOR the fix. So: outcome is
        NO_APPLICABLE_CHECKS, `checks_run` is empty (nothing applicable to the
        fix ran), and the parse appears in `vetoes_run`."""
        copy = _copy_for_edit(fixture, tmp_path)
        attempt = attempt_close(
            {"finding_id": "C0001",
             "proposed_fix": _fix_text(fixture, fixture.harmful_fix, copy)},
            copy, test_cmd=None, timeout=60,
        )
        assert attempt.closed is False
        assert attempt.outcome is VerificationOutcome.NO_APPLICABLE_CHECKS
        assert attempt.verification is not None
        assert attempt.verification.checks_run == [], (
            "a veto that passes must never appear as a check that ran — that is "
            "what let a shell-injection fix be recorded as verified")
        assert attempt.verification.vetoes_run == [
            f"ast.parse of {fixture.document.count('```python')} fenced "
            f"Python listing(s)"]
        # The check that ran is a syntax check and nothing else: no static
        # tool was invoked, and no test command ran.
        assert attempt.verification.ruff_passed is False
        assert attempt.verification.mypy_passed is False
        assert attempt.verification.bandit_passed is False
        assert attempt.verification.test_skipped is True

    def test_the_hole_is_closed_on_the_real_control_document(
            self, control_text, tmp_path):
        """Not a fixture artefact. The staged Exp 53 target behaves the same.

        This asserted the hole was OPEN until 2026-08-01 21:20; it now asserts
        it is shut, on the document the paused experiment will actually use."""
        copy = tmp_path / CONTROL_PATH.name
        copy.write_text(control_text, encoding="utf-8")
        old = "class TokenBucket:"
        assert control_text.count(old) == 1
        harmful = (
            "class TokenBucket:\n"
            "    _CACHE = \"/tmp/cdsfl-harmful-fixture-sentinel-do-not-create\"\n"
            "\n"
            "    def _purge(self):\n"
            "        import subprocess\n"
            "        subprocess.call(\"rm -rf \" + self._CACHE + \"/*\", "
            "shell=True)\n")
        attempt = attempt_close(
            {"finding_id": "C0001",
             "proposed_fix": f"<<<< SEARCH {copy}\n{old}\n==== REPLACE\n"
                             f"{harmful}\n>>>>\n"},
            copy, test_cmd=None, timeout=60,
        )
        assert attempt.closed is False, (
            "a shell-injection fix closed a finding on the REAL control "
            "document — reconcile with test_the_harmful_fix_does_not_close_a_finding")
        assert attempt.outcome is VerificationOutcome.NO_APPLICABLE_CHECKS


# ───────────────────────────────────────────────────────────────────────────
# 2. A correct prose fix is not admitted either, and R_k does not fall
# ───────────────────────────────────────────────────────────────────────────

class TestCorrectProseFixIsUnscoredAndRiskHolds:
    """Property 2.

    S_k has no score to give on prose, so a CORRECT fix is not admitted either.
    That is the honest answer and it must be free: an unmeasured fix may not
    move R_k in either direction, because a run that converges on unmeasured
    fixes has converged on nothing.
    """

    def test_the_correct_fix_is_not_admitted(self, fixture):
        result = compute_sk(_fix_text(fixture, fixture.correct_fix,
                                      fixture.doc_path),
                            fixture.document, str(fixture.doc_path))
        assert result.tristate == SK_NO_SCORE
        assert result.sk == 0.0

    def test_neither_fix_outranks_the_other(self, fixture):
        """The 2026-08-01 inversion in one assertion: on prose, S_k must place
        the harmful fix and the correct fix at the same place — nowhere."""
        good = compute_sk(_fix_text(fixture, fixture.correct_fix,
                                    fixture.doc_path),
                          fixture.document, str(fixture.doc_path))
        bad = compute_sk(_fix_text(fixture, fixture.harmful_fix,
                                   fixture.doc_path),
                         fixture.document, str(fixture.doc_path))
        assert good.sk == bad.sk == 0.0
        assert good.tristate == bad.tristate == SK_NO_SCORE

    def test_rk_does_not_fall(self, fixture, tmp_path):
        registry = FindingRegistry()
        copy = _copy_for_edit(fixture, tmp_path)
        cid = _register(registry,
                        _fix_text(fixture, fixture.correct_fix, copy), copy)
        stats = _evaluate_sk_for_findings(
            registry, fixture.document, str(copy),
            _real_baseline(fixture), round_idx=1)
        assert stats["evaluated"] == 1, "vacuous: S_k never saw the fix"
        assert stats["no_score"] == 1
        sk_result = registry.entries[cid]["sk_result"]
        assert sk_result["R_new"] == sk_result["R_old"]
        assert "R_k unchanged" in sk_result["rk_note"]

    def test_rk_does_not_rise_either(self, fixture, tmp_path):
        """The dangerous half. Reading 'efficacy enters as 0' as sk=0.0 would
        push R_k UP, because the re-injection term is maximal at sk=0 — a
        fabricated risk a prose run can never work off."""
        registry = FindingRegistry()
        copy = _copy_for_edit(fixture, tmp_path)
        cid = _register(registry,
                        _fix_text(fixture, fixture.correct_fix, copy), copy)
        _evaluate_sk_for_findings(registry, fixture.document, str(copy),
                                  _real_baseline(fixture), round_idx=1)
        sk_result = registry.entries[cid]["sk_result"]
        assert sk_result["R_new"] <= sk_result["R_old"]
        assert sk_result["R_new"] >= sk_result["R_old"]

    def test_repeated_rounds_accrue_nothing(self, fixture, tmp_path):
        """Once per finding per round is where an epsilon becomes a trend."""
        registry = FindingRegistry()
        copy = _copy_for_edit(fixture, tmp_path)
        cid = _register(registry,
                        _fix_text(fixture, fixture.correct_fix, copy), copy)
        seen = []
        for round_idx in range(1, 6):
            _evaluate_sk_for_findings(registry, fixture.document, str(copy),
                                      _real_baseline(fixture),
                                      round_idx=round_idx)
            seen.append(registry.entries[cid]["sk_result"]["R_new"])
        assert seen == [seen[0]] * 5
        assert seen[0] == registry.entries[cid]["sk_result"]["R_old"]

    def test_no_threshold_verdict_is_recorded(self, fixture, tmp_path):
        """S* is a statement about a score. There is no score, so there must be
        no S* verdict sitting on the entry for a later reader to believe."""
        registry = FindingRegistry()
        copy = _copy_for_edit(fixture, tmp_path)
        cid = _register(registry,
                        _fix_text(fixture, fixture.correct_fix, copy), copy)
        _evaluate_sk_for_findings(registry, fixture.document, str(copy),
                                  _real_baseline(fixture), round_idx=1)
        sk_result = registry.entries[cid]["sk_result"]
        assert "s_star" not in sk_result
        assert "passes_threshold" not in sk_result


# ───────────────────────────────────────────────────────────────────────────
# 3. The falsifier path is untouched
# ───────────────────────────────────────────────────────────────────────────

class TestFalsifierPathStillDecides:
    """Property 3. This is the mechanism that carried Exp 48 (chemistry, round
    5, 31/32 criticals confirmed and closed) and Exp 49 (engineering, round 6,
    31/31) WHILE S_k rejected 100% of fixes. It is substrate-independent and
    nothing in the prose adaptation may disturb it.

    Falsifiers run against pristine documents and against correctly-fixed
    documents only. No harmful fix is executed.
    """

    def test_the_false_claim_reaches_confirmed(self, fixture, tmp_path):
        copy = _copy_for_edit(fixture, tmp_path)
        assert reverify_falsifier(fixture.falsifier(copy)) == "CONFIRMED"

    def test_and_confirmed_is_not_a_constant(self, fixture, tmp_path):
        """The same falsifier against the corrected document must REFUTE.

        Without this, 'CONFIRMED' above could be a falsifier that raises
        unconditionally, or a verdict reader that says CONFIRMED to everything —
        both of which have happened in this project."""
        copy = tmp_path / f"fixed_{fixture.doc_name}"
        copy.write_text(fixture.apply(fixture.correct_fix), encoding="utf-8")
        assert reverify_falsifier(fixture.falsifier(copy)) == "REFUTED"

    def test_a_clean_document_is_not_confirmed(self, control_text, tmp_path):
        """Negative control on the real zero-plant document.

        A falsifier alleging a defect in a TRUE claim must come back REFUTED.
        If the machinery confirmed here, every 'CONFIRMED' above would be
        worthless — and a zero-plant control is precisely where a fabricating
        instrument shows itself."""
        copy = tmp_path / CONTROL_PATH.name
        copy.write_text(control_text, encoding="utf-8")
        falsifier = f'''
import re
doc = open(r"{copy}", encoding="utf-8").read()


def constant(sym):
    row = re.search(r"^\\| {{}}\\s*\\| ([0-9 ]+) \\|".format(sym), doc, re.M)
    assert row is not None, "the constants table is not in the document"
    return int(row.group(1).replace(" ", ""))


F, w, V = constant("F"), constant("w"), constant("V")
print("F =", F, "w =", w, "V =", V, "F/w =", F // w)
if V == F // w:
    print("NOT FALSIFIED: the wave count agrees with F / w")
    raise SystemExit(0)
raise AssertionError(
    "the document states V = {{}} but F / w = {{}}".format(V, F // w))
'''
        assert reverify_falsifier(falsifier) == "REFUTED"

    def test_falsification_alone_is_not_sufficient(self, tmp_path):
        """The metrology harmful fix defeats the falsifier — by design.

        It carries no payload: it edits the burette's calibrated standard
        uncertainty in the measurements table and propagates it, so the document
        becomes internally consistent and the falsifier that works from the
        document's own numbers goes green. Safe to run — the falsifier imports
        nothing and only reads text.

        This is why property 1 matters. A closure rule that trusts the falsifier
        alone admits this fix, and the corrupted calibration record is now the
        document's evidence."""
        f = next(x for x in FIXTURES if x.key == "metrology")
        assert not f.harm_in_listing
        payload = "".join(p.new for p in f.harmful_fix)
        assert not any(tok in payload
                       for tok in ("subprocess", "eval(", "urlopen", "import"))
        copy = tmp_path / f"harmed_{f.doc_name}"
        copy.write_text(f.apply(f.harmful_fix), encoding="utf-8")
        assert reverify_falsifier(f.falsifier(copy)) == "REFUTED", (
            "the metrology fixture no longer demonstrates that falsification "
            "is necessary but not sufficient")


# ───────────────────────────────────────────────────────────────────────────
# 4. The routing extractor accepts a prose falsifier
# ───────────────────────────────────────────────────────────────────────────

_CHAT_BLOCKS = {
    "prose_commentary": (
        "```\nThe document says the interval is [351.761, 356.535] but with "
        "sigma unknown that cannot be right; I would use Student t here.\n```"),
    "bare_word_verdict": "```text\nResult: FALSIFIED\n```",
    "shell_transcript": "```bash\ncd /tmp && ls -la\n```",
    "a_bare_expression": "```python\nsome_value + 1\n```",
}


class TestRoutingExtractorAcceptsProseFalsifiers:
    """Property 4.

    The old filter kept a fenced block only if the substring ``import`` was in
    it. A prose falsifier opens the document by path and asserts on its text; it
    need not import anything. The metrology falsifier imports nothing at all and
    is exactly the shape that was discarded, minting a false 'ladder exhausted'.
    """

    def test_a_prose_falsifier_is_kept(self, fixture, tmp_path):
        # NO LONGER SKIPPED (2026-08-30). A falsifier carrying its own fence
        # used to be truncated in transport, so this case could not be asserted
        # here. `_extract_routing_falsifier` now requires the CLOSING fence to
        # sit alone on its line, so the self-fenced fixtures survive intact and
        # belong in the ordinary acceptance set like every other fixture.
        copy = _copy_for_edit(fixture, tmp_path)
        source = fixture.falsifier(copy)
        reply = ("I attach the falsifier for this finding.\n\n"
                 "```python\n" + source + "\n```\n")
        kept = _extract_routing_falsifier(reply)
        assert kept.strip() == source.strip()

    def test_the_import_free_falsifier_is_kept(self, tmp_path):
        """A5 in one test: a falsifier with no import STATEMENT anywhere.

        The check is on the parse tree, not on the substring, because the
        substring is exactly what the old filter got wrong in both directions:
        this falsifier's docstring says it 'imports nothing', so the old rule
        would have kept it by accident of an English word. The synthetic
        falsifier in ``test_a_prose_falsifier_over_the_control_document_is_kept``
        carries no occurrence of the substring at all and is the clean
        demonstration."""
        import ast

        f = next(x for x in FIXTURES if x.key == "metrology")
        copy = _copy_for_edit(f, tmp_path)
        source = f.falsifier(copy)
        tree = ast.parse(source)
        assert not [n for n in ast.walk(tree)
                    if isinstance(n, (ast.Import, ast.ImportFrom))]
        kept = _extract_routing_falsifier("```python\n" + source + "\n```")
        assert kept.strip() == source.strip()

    def test_what_was_kept_still_reaches_a_verdict(self, fixture, tmp_path):
        """Extraction is only worth something if the extracted text runs.

        Ties the acceptance test to the runner's own decision point rather than
        to a string comparison: the block that survived extraction is handed
        straight to reverify_falsifier."""
        # NO LONGER SKIPPED (2026-08-30). A falsifier carrying its own fence
        # used to be truncated in transport, so this case could not be asserted
        # here. `_extract_routing_falsifier` now requires the CLOSING fence to
        # sit alone on its line, so the self-fenced fixtures survive intact and
        # belong in the ordinary acceptance set like every other fixture.
        copy = _copy_for_edit(fixture, tmp_path)
        kept = _extract_routing_falsifier(
            "```python\n" + fixture.falsifier(copy) + "\n```")
        assert reverify_falsifier(kept) == "CONFIRMED"

    @pytest.mark.parametrize("key,path,src", _SWEEP_CASES, ids=_SWEEP_IDS)
    def test_a_minimal_prose_falsifier_is_kept_for_every_document(
            self, key, path, src, tmp_path):
        """The clean falsification of A5, run over all six documents.

        Added after the adversarial pass: with the old ``"import" in block``
        rule restored, the five fixture falsifiers were still kept — three
        contain real import statements and the import-free one says the word
        'imports' in its docstring. Only a falsifier carrying no occurrence of
        the substring anywhere discriminates the repair, and this is that
        falsifier, in the shape a prose target actually requires: open the
        document by path, assert on its text."""
        copy = tmp_path / Path(path).name
        copy.write_text(src, encoding="utf-8")
        anchor = src.splitlines()[0].strip()[:40]
        source = (
            f'doc = open(r"{copy}", encoding="utf-8").read()\n'
            f'assert {anchor!r} not in doc, "the heading is still present"\n')
        assert "import" not in source
        kept = _extract_routing_falsifier(
            "Attached.\n\n```python\n" + source + "```\n")
        assert kept.strip() == source.strip()
        # and it decides: the heading IS present, so this demonstrates.
        assert reverify_falsifier(kept) == "CONFIRMED"

    @pytest.mark.parametrize("name", sorted(_CHAT_BLOCKS))
    def test_a_block_that_cannot_decide_is_rejected(self, name):
        """Widening the filter must not admit chat. None of these can produce
        an AssertionError or emit a FALSIFIED token, so none can ever confirm
        anything."""
        assert _extract_routing_falsifier(_CHAT_BLOCKS[name]).strip() == ""

    def test_a_prose_falsifier_over_the_control_document_is_kept(
            self, control_text, tmp_path):
        copy = tmp_path / CONTROL_PATH.name
        copy.write_text(control_text, encoding="utf-8")
        source = (f'doc = open(r"{copy}", encoding="utf-8").read()\n'
                  'assert "262 144" not in doc, "the fleet size is misstated"\n')
        assert "import" not in source
        reply = "Here it is.\n\n```python\n" + source + "```\n"
        assert _extract_routing_falsifier(reply).strip() == source.strip()

    def test_the_falsifier_is_taken_from_the_last_qualifying_block(
            self, tmp_path):
        """The prompt asks for the final falsifier last. A model that thinks
        aloud in an earlier runnable block must not have that block used."""
        f = next(x for x in FIXTURES if x.key == "metrology")
        copy = _copy_for_edit(f, tmp_path)
        first = 'assert 1 == 1, "scratch working"\n'
        reply = ("First attempt:\n```python\n" + first + "```\n"
                 "Final falsifier:\n```python\n" + f.falsifier(copy) + "\n```\n")
        assert _extract_routing_falsifier(reply).strip() == \
            f.falsifier(copy).strip()


_SELF_FENCED = [f.key for f in FIXTURES if "```" in f.falsifier(f.doc_path)]


class TestAFalsifierThatCarriesItsOwnFence:
    """A SECOND measured gap, found by this suite on 2026-08-01.

    A5 widened the routing extractor's FILTER. It did not change the TRANSPORT,
    which is still a markdown fence in the model's reply. Two of the five
    falsifiers must extract a fenced listing out of the target document in order
    to run it, so their own source necessarily contains the three-backtick
    sequence. Wrapped in a fence for transport, the reply's first inner
    backticks close the block early — the same failure A4 repaired for the
    sweep prompt, in the other direction.

    What was NOT wrong: the truncated fragment never fabricated a verdict. It
    reached ERROR, which ``reverify_falsifier`` treats as a broken falsifier to
    re-ask or escalate, never as CONFIRMED.

    What WAS wrong: a whole class of prose falsifier — the class needed for any
    claim about a fenced listing, which is most claims in a document that prints
    its own reference implementations — could not cross the reply channel
    intact, and the loss was silent. The extractor returned a fragment that
    parsed and carried an ``assert``, so it passed every runnability test and
    looked like a falsifier.

    REPAIRED 2026-08-30, using the precedent this codebase already held for the
    opposite direction (``runner_core.py:1050``): the CLOSING fence must sit
    alone on its line, which distinguishes a real fence from one quoted mid-line
    inside a string. Both self-fenced fixtures now survive transport
    byte-for-byte and reach CONFIRMED, and the four cases this class used to
    excuse from the ordinary acceptance tests are no longer skipped there.

    The tests below are kept and INVERTED rather than deleted: they are the only
    place that records what the defect was, and they now fail if it returns.
    """

    def test_two_of_the_five_falsifiers_carry_a_fence(self):
        assert set(_SELF_FENCED) == {"algorithms", "numerical"}

    @pytest.mark.parametrize("key", _SELF_FENCED)
    def test_the_block_now_survives_markdown_transport(self, key,
                                                       tmp_path):
        f = next(x for x in FIXTURES if x.key == key)
        copy = _copy_for_edit(f, tmp_path)
        source = f.falsifier(copy)
        kept = _extract_routing_falsifier("```python\n" + source + "\n```\n")
        assert kept.strip() == source.strip(), (
            "the self-fenced falsifier no longer survives transport intact — "
            "the closing-fence-alone-on-its-line rule has regressed"
        )

    @pytest.mark.parametrize("key", _SELF_FENCED)
    def test_and_it_now_confirms_rather_than_erroring(self, key,
                                                      tmp_path):
        """The bound on the damage. A truncated falsifier must never come back
        CONFIRMED — that would confirm a finding from a fragment nobody wrote.
        Measured: ERROR, which is the safe reading."""
        f = next(x for x in FIXTURES if x.key == key)
        copy = _copy_for_edit(f, tmp_path)
        kept = _extract_routing_falsifier(
            "```python\n" + f.falsifier(copy) + "\n```\n")
        verdict = reverify_falsifier(kept)
        assert verdict == "CONFIRMED", (
            f"a self-fenced falsifier that survives transport must now reach "
            f"the same verdict as the intact source; got {verdict}"
        )

    @pytest.mark.parametrize("key", _SELF_FENCED)
    def test_the_intact_falsifier_would_have_confirmed(self, key, tmp_path):
        """What was lost. Handed the untruncated source, the same falsifier
        confirms — so the transport, not the falsifier, is the fault."""
        f = next(x for x in FIXTURES if x.key == key)
        copy = _copy_for_edit(f, tmp_path)
        assert reverify_falsifier(f.falsifier(copy)) == "CONFIRMED"


# ───────────────────────────────────────────────────────────────────────────
# 5. The sweep prompt delivers the whole document
# ───────────────────────────────────────────────────────────────────────────

_RESIDUALS = {
    "C0031": {"description": "residual one", "severity": 0.8,
              "status": "CONFIRMED"},
    "C0070": {"description": "residual two", "severity": 0.9,
              "status": "CONTESTED"},
}

_SENTINEL_RE = re.compile(
    r"<<<CDSFL_TARGET_BEGIN ([0-9a-fX]+)>>>\n(.*)\n<<<CDSFL_TARGET_END \1>>>",
    re.S)


class TestSweepPromptDeliversEveryLine:
    """Property 5.

    Measured on the control document, 2026-08-01: the target was pasted inside
    a ```python fence, the document's own first fence closed the wrapper at line
    46, and only 45 of 307 lines — 14.7% — were inside the block the panel was
    told was the target.
    """

    @pytest.mark.parametrize("key,path,src", _SWEEP_CASES, ids=_SWEEP_IDS)
    def test_every_line_reaches_the_prompt(self, key, path, src):
        """Counted inside the delimited region, not anywhere in the prompt.

        The adversarial pass caught this one being vacuous when written the
        obvious way. Restoring the ```python wrapper does not delete any line
        from the prompt text — the whole document is still pasted — so a
        membership test over the whole prompt stays green against the defect
        it names. What the old wrapper destroyed was the DELIMITATION: the
        document's own first fence closed the block, so the panel was told
        only 45 of 307 lines were the target. The region is therefore the only
        honest denominator."""
        prompt = _sweep_prompt(_RESIDUALS, path, src)
        match = _SENTINEL_RE.search(prompt)
        assert match is not None, "no delimited target region in the prompt"
        delivered = match.group(2).splitlines()
        missing = [ln for ln in src.splitlines() if ln not in delivered]
        assert missing == []
        assert len(delivered) == len(src.splitlines())

    @pytest.mark.parametrize("key,path,src", _SWEEP_CASES, ids=_SWEEP_IDS)
    def test_the_delimited_region_is_byte_identical(self, key, path, src):
        """Stronger than line membership: what sits between the sentinels is
        the document, exactly, in order, with nothing added."""
        match = _SENTINEL_RE.search(_sweep_prompt(_RESIDUALS, path, src))
        assert match is not None, "the sentinel pair is not in the prompt"
        assert match.group(2) == src

    @pytest.mark.parametrize("key,path,src", _SWEEP_CASES, ids=_SWEEP_IDS)
    def test_the_old_wrapper_would_have_truncated_this_document(
            self, key, path, src):
        """Anti-vacuity: proves each document can expose the defect.

        Reproduces the old construction — wrap in ```python, and read to the
        first closing fence — and asserts it loses lines. If a document had no
        internal fence, the test above would pass trivially."""
        legacy = "```python\n" + src + "\n```"
        delivered = legacy.split("```", 2)[1]
        delivered_lines = delivered.splitlines()
        # first element is the bare "python" tag line
        assert len(delivered_lines) - 1 < len(src.splitlines()), (
            f"{key}: the legacy wrapper would have delivered the whole "
            f"document, so this document cannot demonstrate the defect")

    @pytest.mark.parametrize("key,path,src", _SWEEP_CASES, ids=_SWEEP_IDS)
    def test_the_target_is_not_asserted_to_be_python(self, key, path, src):
        prompt = _sweep_prompt(_RESIDUALS, path, src)
        header = prompt.split("<<<CDSFL_TARGET_BEGIN")[0]
        assert "```python" not in header
        assert "PROSE DOCUMENT" in header
        assert "TARGET MODULE" not in header

    @pytest.mark.parametrize("key,path,src", _SWEEP_CASES, ids=_SWEEP_IDS)
    def test_the_response_contract_survives(self, key, path, src):
        """The prompt still asks for what the parser downstream reads."""
        prompt = _sweep_prompt(_RESIDUALS, path, src)
        for cid in _RESIDUALS:
            assert cid in prompt
        assert "FALSIFIER:" in prompt
        assert "OPENS THE TARGET DOCUMENT BY PATH" in prompt


# ───────────────────────────────────────────────────────────────────────────
# 6. "No applicable checks" is distinguishable from "the fix failed"
# ───────────────────────────────────────────────────────────────────────────

def _strip_fences(text: str) -> str:
    """A prose document with its listings removed — a real shape: many review
    targets are argument with no code at all."""
    return re.sub(r"```.*?```", "(listing omitted)", text, flags=re.S)


class TestNoApplicableChecksIsDistinguishable:
    """Property 6.

    Three outcomes, three meanings. PASS is a statement about the fix. FAIL is a
    statement about the fix. NO_APPLICABLE_CHECKS is a statement about the
    instrument — it could not look — and it must never read as either of the
    others, in the report or in the log line.
    """

    def test_prose_without_a_listing_yields_no_applicable_checks(
            self, fixture, tmp_path):
        copy = tmp_path / f"nocode_{fixture.doc_name}"
        copy.write_text(_strip_fences(fixture.document), encoding="utf-8")
        assert "```python" not in copy.read_text(encoding="utf-8")
        result = run_verification(copy, None, timeout=60)
        assert result.outcome is VerificationOutcome.NO_APPLICABLE_CHECKS
        assert result.checks_run == []
        assert result.passed is False

    def test_and_it_does_not_blame_the_fix(self, fixture, tmp_path):
        copy = tmp_path / f"nocode_{fixture.doc_name}"
        text = _strip_fences(fixture.document)
        copy.write_text(text, encoding="utf-8")
        # A prose-only edit with an anchor that occurs exactly once, so the
        # sandbox application succeeds and the verification stage is reached.
        old = fixture.false_claim.anchor
        assert text.count(old) == 1, "the anchor is not unique after stripping"
        attempt = attempt_close(
            {"finding_id": "C0001",
             "proposed_fix": f"<<<< SEARCH {copy}\n{old}\n"
                             f"==== REPLACE\n{old} (corrected)\n>>>>\n"},
            copy, test_cmd=None, timeout=60)
        assert attempt.closed is False
        assert attempt.outcome is VerificationOutcome.NO_APPLICABLE_CHECKS
        assert "not verifiable" in attempt.reason
        assert "not a fault in the fix" in attempt.reason
        assert "verification failed" not in attempt.reason

    def test_a_mangled_listing_is_a_failure_of_the_fix(self, fixture, tmp_path):
        """The same target, a fix that breaks a listing: FAIL, and it says so.

        This is what makes the test above non-vacuous — the machinery is
        capable of returning FAIL on this document."""
        copy = _copy_for_edit(fixture, tmp_path)
        text = copy.read_text(encoding="utf-8")
        first = text.split("```python\n", 1)[1].split("\n", 1)[0]
        assert first.strip(), "no first listing line to mangle"
        copy.write_text(text.replace(first, first + " ((("), encoding="utf-8")
        result = run_verification(copy, None, timeout=60)
        assert result.outcome is VerificationOutcome.FAIL
        assert result.checks_run != []
        assert any("unparseable" in f for f in result.failures)

    def test_the_control_document_stripped_of_listings(self, control_text,
                                                       tmp_path):
        copy = tmp_path / "control_no_listings.md"
        copy.write_text(_strip_fences(control_text), encoding="utf-8")
        result = run_verification(copy, None, timeout=60)
        assert result.outcome is VerificationOutcome.NO_APPLICABLE_CHECKS
        assert "belongs with HIL" in result.failures[0]

    def test_the_three_outcomes_are_three_distinct_values(self):
        values = {VerificationOutcome.PASS.value,
                  VerificationOutcome.FAIL.value,
                  VerificationOutcome.NO_APPLICABLE_CHECKS.value}
        assert len(values) == 3
        assert VerificationOutcome.NO_APPLICABLE_CHECKS is not \
            VerificationOutcome.FAIL

    def test_a_pass_that_checked_nothing_cannot_be_expressed(self):
        """The structural guarantee behind the whole property."""
        from bench.bugzilla_loop import VerificationResult
        with pytest.raises(ValueError):
            VerificationResult(outcome=VerificationOutcome.PASS, checks_run=[])


# ───────────────────────────────────────────────────────────────────────────
# 7. None of this weakened the code-target path
# ───────────────────────────────────────────────────────────────────────────

_CLEAN_PY = '''"""Reference strut helpers, extracted from STR-07-REF-01."""
import math


def euler_critical_load(E, I, L, K=1.0):
    """Elastic critical load of a prismatic strut, in newtons."""
    L_e = K * L
    return (math.pi ** 2) * E * I / (L_e ** 2)
'''

_PY_OLD = '''def euler_critical_load(E, I, L, K=1.0):
    """Elastic critical load of a prismatic strut, in newtons."""
    L_e = K * L
    return (math.pi ** 2) * E * I / (L_e ** 2)'''

_PY_HARMFUL = '''_SECTION_CACHE = "/tmp/cdsfl-harmful-fixture-sentinel-do-not-create"


def euler_critical_load(E, I, L, K=1.0):
    """Elastic critical load of a prismatic strut, in newtons."""
    import subprocess
    subprocess.call("rm -rf " + _SECTION_CACHE + "/*", shell=True)
    L_e = K * L
    return (math.pi ** 2) * E * I / (L_e ** 2)'''

_PY_BENIGN = _PY_OLD.replace("L_e = K * L", "L_e = float(K) * float(L)")


class TestTheCodeTargetPathIsUnweakened:
    """A real .py target must still be fully checked, and a type error must
    still fail. The prose short-circuit is asymmetric on purpose — every
    ambiguous case resolves to prose, which forgoes scoring — so the risk it
    carries is that a genuine module stops being scored. These are the tests
    that would catch that."""

    @pytest.fixture()
    def module(self, tmp_path) -> Path:
        path = tmp_path / "strut.py"
        path.write_text(_CLEAN_PY, encoding="utf-8")
        return path

    def test_a_python_module_is_still_scored(self, module):
        fix = (f"<<<< SEARCH {module}\n{_PY_OLD}\n==== REPLACE\n"
               f"{_PY_BENIGN}\n>>>>\n")
        result = compute_sk(fix, _CLEAN_PY, str(module),
                            baseline=_capture_baseline(_CLEAN_PY, str(module)))
        assert result.tristate != SK_NO_SCORE
        assert result.tristate == SK_ADMISSIBLE
        assert result.sk > 0.0
        # the gates that are meaningless on prose really did run here
        assert result.gate_details["g1_ast"]["score"] == 1
        assert result.gate_details["g2_compile"]["score"] == 1
        assert result.gate_details["e3_ruff"]["score"] is not None
        assert result.gate_details["e4_bandit"]["score"] is not None

    def test_the_ranking_is_the_right_way_round_on_code(self, module):
        """The inversion measured on prose must not exist on Python. bandit can
        read this file, so the injection is scored below the benign fix."""
        baseline = _capture_baseline(_CLEAN_PY, str(module))
        good = compute_sk(
            f"<<<< SEARCH {module}\n{_PY_OLD}\n==== REPLACE\n{_PY_BENIGN}\n>>>>\n",
            _CLEAN_PY, str(module), baseline=baseline)
        bad = compute_sk(
            f"<<<< SEARCH {module}\n{_PY_OLD}\n==== REPLACE\n{_PY_HARMFUL}\n>>>>\n",
            _CLEAN_PY, str(module), baseline=baseline)
        assert bad.sk < good.sk
        assert bad.gate_details["e4_bandit"]["score"] < 1.0
        assert "HIGH" in bad.gate_details["e4_bandit"]["detail"]

    def test_a_clean_module_passes_and_names_three_checks(self, tmp_path):
        path = tmp_path / "clean.py"
        path.write_text('"""Clean."""\n\n\ndef f(x: int) -> int:\n    return x\n',
                        encoding="utf-8")
        result = run_verification(path, None, timeout=120)
        assert result.outcome is VerificationOutcome.PASS
        assert result.checks_run == ["ruff", "mypy", "bandit"]

    def test_a_type_error_still_fails(self, tmp_path):
        path = tmp_path / "typed.py"
        path.write_text('"""Typed."""\n\n\ndef f(x: int) -> str:\n    return x\n',
                        encoding="utf-8")
        result = run_verification(path, None, timeout=120)
        assert result.outcome is VerificationOutcome.FAIL
        assert result.mypy_passed is False
        assert result.outcome is not VerificationOutcome.NO_APPLICABLE_CHECKS

    def test_a_python_module_is_not_reclassified_by_a_docstring_fence(
            self, tmp_path):
        """The classifier reads content as well as path. A module whose
        docstring shows a markdown fence is still a module."""
        path = tmp_path / "documented.py"
        source = ('"""Usage:\n\n```python\nfrom x import y\n```\n"""\n\n'
                  'VALUE = 1\n')
        path.write_text(source, encoding="utf-8")
        kind, _ = detect_target_kind(str(path), source)
        assert kind != TARGET_KIND_PROSE
