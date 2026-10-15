"""Task 2.2: the falsifier exp42 C0040 never got. REBASED 2026-10-15 — IT IS FIXED.

THE FINDING, verbatim, raised by ChatGPT at severity 0.88 and recorded
`UNCONFIRMED` / `UNTOOLABLE` with an empty `falsifier_code`:
"`_load_universal_directive()` silently replaces the full universal HARD
directive with a 2.5k-character 'minimal' rendering whenever the full universal
text exceeds the model's `max_directive_chars`".

CONFIRMED 2026-09-10, AND LARGER THAN THE FINDING STATED. Not "whenever" --
ALWAYS. The full directive is 27,803 characters and the largest
`max_directive_chars` in the roster was 12,000, so the reduced form was served
to 5 of 5 models. The docstring's promise of "Full text for large-context
models" described a branch that could not fire for any model that existed.

★ REPAIRED 2026-10-15 ON THE FOUNDER'S RULING, AND THIS FILE NOW ASSERTS THE
REPAIRED PROPERTY RATHER THAN THE DEFECT. The file previously closed with "NO
FIX IS APPLIED HERE, DELIBERATELY ... parked for him", on the ground that
changing which directive text a model receives invalidates replay of archived
runs. He ruled on 2026-10-15: *"Apply any outstanding fixes you have identified
first, including any as yet unbuilt/unapplied machinery, before you begin the
runs"*, and, on the replay cost, *"We cannot go back and change time, so the
confounds discovered in the last 24 hours can only be noted and added to the
record honestly."* That is the authorisation this file was waiting for.

HIS REASONING, VERBATIM, 2026-10-14, because it is what decided the SHAPE of the
fix rather than merely permitting one: *"as far as any caps have ever existed,
their intention was to never feed any model more work than they were
demonstrably able to handle, especially for weaker models like Deepseek, and we
built considerable machinery around this principle. There was never an intent as
far as I recall to applying this same reasoning to the core operational
directives themselves"*, and *"7000 or so words for a system prompt is hardly
excessive for any modern model? Why should we need to cut it at all?"*

SO THE 2 BOUNDS ARE NOW SEPARATE FIELDS. `max_directive_chars` keeps its value
and bounds WORK -- the domain checklist, the review target, the code extracts,
the adversarial brief. `spec_chars` bounds the SPECIFICATION and is `None` for
every model, which means "deliver it whole".

WHAT IS MEASURED, by `scripts/the_spec_is_not_work_2026-10-15.py`:
  * 5 of 5 models had a work cap below the 27,803-character specification,
    100.0000%, Wilson [56.5518%, 100.0000%], so the reduced form was
    unconditional.
  * That reduced form carried 0 of 22 HARD blocks by verbatim containment,
    0.0000%, Wilson [0.0000%, 14.8655%], Clopper-Pearson [0.0000%, 15.4373%],
    where the 22 are whatever `_block_is_hard()` -- the project's OWN HARD
    predicate -- accepts. It now carries 22 of 22, 100.0000%, Wilson [85.1345%,
    100.0000%], Clopper-Pearson [84.5627%, 100.0000%].
  * A FIRST-8-WORDS PROBE REPORTED 1 of 22 AND 13 of 22 AND BOTH FIGURES ARE
    WITHDRAWN. It space-joins the first 8 words across newlines, so it cannot
    match a multi-line block against text that keeps its newlines, and 9 of the
    22 HARD blocks are multi-line. The instrument was the defect. Every
    assertion below uses verbatim containment.

THE OPERATIONAL DIRECTIVE WAS AND REMAINS THE OTHER HALF OF THE SEVERITY. It is
appended in full at `reference_runner_v3.py`, exempt from the caps, and the
checks for that are retained unchanged -- reporting the substitution without it
would have been alarming and wrong.
"""
from __future__ import annotations

import inspect
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench.cdsfl_registry.composer import (  # noqa: E402
    DIRECTIVES_DIR,
    PHENOTYPE_TRANSFORMS,
    PhenotypeTransform,
    _block_is_hard,
    _load_universal_directive,
    _render_universal_minimal,
    _split_packet_directives,
)

#: The (run directory, canonical id) of every critical finding this file writes
#: the falsifier for. `scripts/missing_falsifiers_2026-09-10.py` derives ALREADY
#: WRITTEN and REMAINING from these declarations, and
#: `test_missing_falsifiers_all_covered_2026-09-17.py` requires their union to
#: equal the script's population. The run is part of the key because a
#: canonical id is only unique within a run.
COVERS = {
    ("exp42_composer_20260606T202037Z", "C0040"),
}

D = pathlib.Path(DIRECTIVES_DIR)
FULL = D / "universal" / "cdsfl_core_formal.md"
OPER = D / "universal" / "cdsfl_operational.md"


@pytest.fixture(scope="module")
def full_text():
    assert FULL.is_file(), "the full universal directive is missing entirely"
    return FULL.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def hard_blocks(full_text):
    blocks = [b for b in _split_packet_directives(full_text) if _block_is_hard(b)]
    assert len(blocks) >= 20, (
        f"only {len(blocks)} HARD blocks found by the project's own predicate; "
        f"the specification or the predicate has changed and the figures in this "
        f"file's docstring need remeasuring")
    return blocks


class TestEveryModelNowReceivesTheSpecificationWhole:
    """The repaired property. This is the half of the file that used to assert
    the defect, and every assertion here is the negation of what it said."""

    def test_every_model_receives_the_full_directive(self, full_text):
        for model in PHENOTYPE_TRANSFORMS:
            got = _load_universal_directive(model)
            assert got.text == full_text, (
                f"{model} does not receive the specification whole: "
                f"{len(got.text)} chars against {len(full_text)}")

    def test_the_work_cap_is_still_below_the_specification(self, full_text):
        """The repair did NOT raise the work caps, and must not be read as if
        it had. Every one of them is still smaller than the specification; what
        changed is that the specification no longer consults them."""
        biggest = max(t.max_directive_chars for t in PHENOTYPE_TRANSFORMS.values())
        assert len(full_text) > biggest, (
            f"a work cap ({biggest}) now exceeds the specification "
            f"({len(full_text)}), which would mean the caps were raised -- they "
            f"were not supposed to be")

    def test_no_model_sets_a_specification_bound(self):
        for model, transform in PHENOTYPE_TRANSFORMS.items():
            assert transform.spec_chars is None, (
                f"{model} carries spec_chars={transform.spec_chars}, so it is "
                f"back on the reduced form; that is a decision needing a "
                f"measurement, not a default")

    def test_the_specification_bound_is_what_the_loader_consults(self, full_text):
        """EXECUTED, not grepped: give a probe model a tiny `spec_chars` and the
        reduced form must appear; give it a tiny `max_directive_chars` and the
        full text must survive."""
        probe = "c0040_probe_model"
        try:
            PHENOTYPE_TRANSFORMS[probe] = PhenotypeTransform(
                max_directive_chars=10, spec_chars=None)
            assert _load_universal_directive(probe).text == full_text, (
                "a tiny WORK cap still cuts the specification")
            # 20,000: below the specification so the reduced form is
            # SELECTED, above the 8,367-character faithful render so it FITS.
            # A bound below 8,367 raises instead, which is correct -- a
            # specification cut to fit is the defect this repair closes.
            PHENOTYPE_TRANSFORMS[probe] = PhenotypeTransform(
                max_directive_chars=99_999, spec_chars=20_000)
            got = _load_universal_directive(probe).text
            assert got != full_text and len(got) < len(full_text), (
                "a SPECIFICATION bound does not select the reduced form")
        finally:
            PHENOTYPE_TRANSFORMS.pop(probe, None)

    def test_the_docstring_no_longer_over_promises(self):
        """THE FIRST VERSION OF THIS TEST COULD NOT TELL A QUOTATION FROM A
        PROMISE, and it failed on the repaired docstring for that reason alone.
        The repaired docstring QUOTES the old over-promise in order to record
        that it was false, which is the right thing for the record and exactly
        what a bare substring check misreads. Same class as the verdict reader
        that matched "NOT FALSIFIED" as though it contained "FALSIFIED".
        Double-quoted spans are therefore removed before the check.
        """
        doc = inspect.getdoc(_load_universal_directive) or ""
        unquoted = re.sub(r'"[^"]*"', " ", doc)
        assert "Full text for large-context models" not in unquoted, (
            "the docstring still promises a branch by capacity OUTSIDE a "
            "quotation; the decision is no longer about capacity at all")
        assert "Full text for large-context models" in doc, (
            "the docstring no longer records the promise it used to make, so a "
            "reader cannot see what changed")
        assert "spec_chars" in doc, (
            "the docstring does not name what the decision now turns on")


class TestTheReducedFormIsFaithfulWhenItIsReached:
    """It is no longer the default path, but it is still reachable, and an
    addition nothing reaches is not additive either -- so it must be correct."""

    def test_every_hard_block_is_carried_verbatim(self, hard_blocks):
        mini = _render_universal_minimal()
        missing = [b.splitlines()[0][:70] for b in hard_blocks if b not in mini]
        assert not missing, (
            f"{len(missing)} of {len(hard_blocks)} HARD blocks are absent from "
            f"the reduced form: {missing}")

    def test_falsifier_integrity_reaches_the_reduced_form(self):
        """Named rather than left inside a count. This section instructs models
        not to cheat on the falsifiers every verdict in this project rests on,
        and it reached no model by any path before 2026-10-15."""
        mini = _render_universal_minimal().lower()
        assert "falsifier integrity" in mini, (
            "the reduced form has lost the falsifier-integrity section again")
        for phrase in ("do not read a scoring key",
                       "do not modify, delete, weaken or skip a test",
                       "do not terminate early"):
            assert phrase in mini, f"the reduced form has lost: {phrase!r}"

    def test_it_is_no_longer_only_key_equals_value_lines(self):
        mini = _render_universal_minimal()
        lines = [l for l in mini.splitlines() if l.strip()]
        kv = [l for l in lines if re.match(r"^[a-z][\w.]*=", l.strip())]
        assert len(kv) / len(lines) < 0.8, (
            f"{len(kv)} of {len(lines)} lines are still key=value; the reduced "
            f"form is still a flag dump")

    def test_an_over_tight_bound_raises_rather_than_truncating(self):
        """A specification cut to fit is the defect this repair closes, so a
        caller that cannot afford the HARD set learns it from an exception."""
        with pytest.raises(ValueError):
            _render_universal_minimal(max_chars=100)


class TestTheSeverityIsKeptHonest:
    """Retained unchanged from the 2026-09-10 version. Without these the
    finding reads as "models get 2.5k of flags", which was never true."""

    def test_the_operational_directive_is_appended_in_full(self):
        assert OPER.is_file()
        src = (ROOT / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        assert 'model_cdsfl += "\\n\\n" + _OPERATIONAL_DIRECTIVE_TEXT' in src, (
            "the operational directive is no longer appended, which would make "
            "C0040 far worse than recorded")

    def test_the_specification_is_now_a_real_share_of_the_prompt(self, full_text):
        """The inverse of the old assertion, and the point of the repair: the
        operational directive used to be more than 90% of what a model saw,
        because the specification had been reduced to a flag dump."""
        oper = OPER.read_text(encoding="utf-8")
        total = len(full_text) + len(oper)
        assert total > 40000, total
        share = len(full_text) / total
        assert 0.3 < share < 0.5, (
            f"the specification is {share:.4f} of the system prompt; the "
            f"measured figure on 2026-10-15 was 0.3748 and a large move means "
            f"a directive file changed size")


class TestWhatIsStillNotCoveredByTheOperationalDirectiveAlone:
    """The operational directive still covers only part of the specification.
    That no longer costs anything, because the specification itself now
    arrives -- but the measurement is retained so a future regression that
    returns to the reduced form is reported against a known baseline."""

    def test_at_most_a_bounded_number_of_sections_go_missing(self, full_text):
        """UPPER BOUND, never a point estimate. The heuristic is crude.

        First 3 words of 4+ characters per heading, all required to appear
        somewhere in the operational text. A section covered under different
        wording reports NOT FOUND, so this over-counts the loss by construction.
        """
        oper = OPER.read_text(encoding="utf-8").lower()
        heads = [h.strip() for h in re.findall(r"^#{1,3}\s+(.+)$", full_text, re.M)]
        assert len(heads) >= 10, f"only {len(heads)} headings found; recheck"
        missing = []
        for h in heads:
            words = [w for w in re.sub(r"[^a-z0-9 ]", " ", h.lower()).split()
                     if len(w) > 3][:3]
            if words and not all(w in oper for w in words):
                missing.append(h)
        assert missing, (
            "the operational directive now appears to cover every section, so "
            "the C0040 loss may be closed -- verify by reading before believing")
        # TWO TOOLS on the proportion, as this project requires.
        from statsmodels.stats.proportion import proportion_confint
        lo, hi = proportion_confint(len(heads) - len(missing), len(heads),
                                    method="wilson")
        lo_c, _hi_c = proportion_confint(len(heads) - len(missing), len(heads),
                                         method="beta")
        from scipy.stats import beta as sbeta
        cov = len(heads) - len(missing)
        slo = sbeta.ppf(0.025, cov, len(heads) - cov + 1) if cov else 0.0
        assert abs(slo - lo_c) < 1e-9, "statsmodels and scipy disagree"
        assert 0.0 < hi < 1.0, (lo, hi)

    def test_the_falsifier_integrity_section_reaches_a_model_now(self, full_text):
        """It still is NOT in the operational directive. It now arrives by the
        specification itself, which is the whole repair in one assertion."""
        oper = OPER.read_text(encoding="utf-8").lower()
        assert "falsifier integrity" in full_text.lower(), (
            "the section is gone from the specification; recheck the finding")
        assert "falsifier integrity" not in oper, (
            "the operational directive now carries falsifier integrity, so this "
            "half of the C0040 loss is closed by a different route -- update it")
        for model in PHENOTYPE_TRANSFORMS:
            delivered = _load_universal_directive(model).text.lower()
            assert "falsifier integrity" in delivered, (
                f"{model} is not told the falsifier-integrity section")
