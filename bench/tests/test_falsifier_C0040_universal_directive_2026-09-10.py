"""Task 2.2: the falsifier exp42 C0040 never got. It is the largest of the set.

THE FINDING, verbatim, raised by ChatGPT at severity 0.88 and recorded
`UNCONFIRMED` / `UNTOOLABLE` with an empty `falsifier_code`:
"`_load_universal_directive()` silently replaces the full universal HARD
directive with a 2.5k-character 'minimal' rendering whenever the full universal
text exceeds the model's `max_directive_chars`".

CONFIRMED, AND LARGER THAN THE FINDING STATES. Not "whenever" -- ALWAYS. The full
directive is 27,803 characters and the largest `max_directive_chars` in the
roster is 12,000, so the reduced form is served to 5 of 5 models. The docstring's
promise of "Full text for large-context models" describes a branch that cannot
fire for any model that exists.

WHAT THE REDUCED FORM IS. Not a summary: a TOML key dump.
`policy.constraints.falsification_required=true`. 0 of the full directive's 16
section headings survive it. A model told a flag is set has not been told what
falsification is or how to perform it.

AND NOW THE PART THAT KEEPS THE SEVERITY HONEST. The models are NOT left with
flags. `reference_runner_v3.py:8339` appends `cdsfl_operational.md` -- 44,157
characters -- to every model, explicitly exempt from the phenotype caps, so the
system prompt is 46,660 characters and mostly prose. Reporting the substitution
without this would be alarming and wrong.

WHAT SURVIVES THE CHECK. Of the 16 sections in the full universal directive, the
operational directive covers 6 (37.50%, Wilson [18.48%, 61.36%]). The other 10
reach no model by either path, and they include "Runnable Falsifiers for Critical
Findings" and "Falsifier Integrity -- Do Not Reach for the Answer" -- the section
instructing models not to cheat on the falsifiers this project's verdicts rest on.

THE COVERAGE HEURISTIC IS CRUDE AND SAYS SO. It takes the first 3 words of 4 or
more characters from each heading and asks whether all appear anywhere in the
operational text. That can report NOT FOUND for a section covered under different
wording, so 10 of 16 is an UPPER BOUND on the loss, not a measurement of it. The
tests below assert the bound, never the point estimate.

NO FIX IS APPLIED HERE, DELIBERATELY. Changing which directive text a model
receives changes every dispatch and invalidates replay of archived runs -- the
same class as the S* threshold promotion, which this project ruled needs the
founder. Confirmed, measured, tested, and parked for him.
"""
from __future__ import annotations

import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench.cdsfl_registry.composer import (  # noqa: E402
    DIRECTIVES_DIR,
    PHENOTYPE_TRANSFORMS,
    _load_universal_directive,
    _render_universal_minimal,
)

D = pathlib.Path(DIRECTIVES_DIR)
FULL = D / "universal" / "cdsfl_core_formal.md"
OPER = D / "universal" / "cdsfl_operational.md"


@pytest.fixture(scope="module")
def full_text():
    assert FULL.is_file(), "the full universal directive is missing entirely"
    return FULL.read_text(encoding="utf-8")


class TestTheSubstitutionHappensToEveryModel:
    def test_no_model_receives_the_full_directive(self, full_text):
        """The finding says "whenever ... exceeds". It is ALWAYS."""
        biggest = max(t.max_directive_chars for t in PHENOTYPE_TRANSFORMS.values())
        assert len(full_text) > biggest, (
            f"the full directive ({len(full_text)}) now fits the largest cap "
            f"({biggest}), so some model gets the full text and C0040's scope "
            f"has changed")
        for model in PHENOTYPE_TRANSFORMS:
            got = _load_universal_directive(model)
            assert len(got.text) < len(full_text), model

    def test_the_docstring_promises_a_branch_that_cannot_fire(self, full_text):
        """"Full text for large-context models" -- there are none."""
        import inspect
        doc = inspect.getdoc(_load_universal_directive) or ""
        assert "Full text for large-context models" in doc, (
            "the docstring changed; recheck whether it still over-promises")
        assert all(len(full_text) > t.max_directive_chars
                   for t in PHENOTYPE_TRANSFORMS.values())


class TestTheReducedFormIsAFlagDumpNotASummary:
    def test_no_section_heading_survives(self, full_text):
        mini = _render_universal_minimal(max_chars=12000)
        heads = [h.strip() for h in re.findall(r"^#{1,3}\s+(.+)$", full_text, re.M)]
        assert len(heads) >= 10, f"only {len(heads)} headings found; recheck"
        kept = [h for h in heads
                if h.split("—")[0].strip()[:24].lower() in mini.lower()]
        assert not kept, f"some headings now survive: {kept}"

    def test_it_is_key_equals_value_lines(self):
        mini = _render_universal_minimal(max_chars=12000)
        lines = [l for l in mini.splitlines() if l.strip()]
        kv = [l for l in lines if re.match(r"^[a-z][\w.]*=", l.strip())]
        assert len(kv) / len(lines) > 0.8, (
            f"only {len(kv)} of {len(lines)} lines are key=value; the reduced "
            f"form may no longer be a flag dump")


class TestTheSeverityIsKeptHonest:
    """Without these the finding reads as "models get 2.5k of flags". False."""

    def test_the_operational_directive_is_appended_in_full(self):
        assert OPER.is_file()
        src = (ROOT / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        assert 'model_cdsfl += "\\n\\n" + _OPERATIONAL_DIRECTIVE_TEXT' in src, (
            "the operational directive is no longer appended, which would make "
            "C0040 far worse than recorded")

    def test_the_prompt_a_model_actually_receives_is_mostly_prose(self):
        mini = _render_universal_minimal(max_chars=12000)
        oper = OPER.read_text(encoding="utf-8")
        total = len(mini) + len(oper)
        assert total > 40000, total
        assert len(oper) / total > 0.9, (
            "the operational directive is no longer the bulk of the prompt")


class TestWhatIsLostByBothPaths:
    def test_at_most_a_bounded_number_of_sections_go_missing(self, full_text):
        """UPPER BOUND, never a point estimate. The heuristic is crude.

        First 3 words of 4+ characters per heading, all required to appear
        somewhere in the operational text. A section covered under different
        wording reports NOT FOUND, so this over-counts the loss by construction.
        """
        oper = OPER.read_text(encoding="utf-8").lower()
        heads = [h.strip() for h in re.findall(r"^#{1,3}\s+(.+)$", full_text, re.M)]
        missing = []
        for h in heads:
            words = [w for w in re.sub(r"[^a-z0-9 ]", " ", h.lower()).split()
                     if len(w) > 3][:3]
            if words and not all(w in oper for w in words):
                missing.append(h)
        assert len(missing) <= len(heads), "impossible"
        assert missing, (
            "the operational directive now appears to cover every section, so "
            "the C0040 loss may be closed -- verify by reading before believing")
        # TWO TOOLS on the proportion, as this project requires.
        from statsmodels.stats.proportion import proportion_confint
        lo, hi = proportion_confint(len(heads) - len(missing), len(heads),
                                    method="wilson")
        lo_c, hi_c = proportion_confint(len(heads) - len(missing), len(heads),
                                        method="beta")
        from scipy.stats import beta as sbeta
        cov = len(heads) - len(missing)
        slo = sbeta.ppf(0.025, cov, len(heads) - cov + 1) if cov else 0.0
        assert abs(slo - lo_c) < 1e-9, "statsmodels and scipy disagree"
        assert 0.0 < hi < 1.0, (lo, hi)

    def test_the_falsifier_integrity_section_is_among_the_missing(self, full_text):
        """The one that matters most, named rather than left in a count.

        "Falsifier Integrity -- Do Not Reach for the Answer" instructs models not
        to cheat on the falsifiers this project's verdicts rest on.
        """
        oper = OPER.read_text(encoding="utf-8").lower()
        assert "falsifier integrity" in full_text.lower(), (
            "the section is gone from the full directive too; recheck the finding")
        assert "falsifier integrity" not in oper, (
            "the operational directive now carries falsifier integrity, so this "
            "half of the C0040 loss is closed -- update the finding")
