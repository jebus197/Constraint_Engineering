"""Task 2.2: the falsifier exp42 C0002 never got, and the fix it names.

THE FINDING, verbatim from `bench/logs/exp42_composer_confirm_20260606T184941Z`,
C0002, raised by CC2 at severity 0.7: "`compose()` (line ~660) mutates the
caller's `situation` DirectivePacket in-place via `situation.text =
_apply_phenotype_transform(situation.text, transform)`. The docstring claims the
function is 'Pure'."

RECORDED `UNCONFIRMED`, `falsifier_verdict: UNTOOLABLE`, `falsifier_code: ''`.
Nothing was untoolable about it. It is a claim that calling a function changes an
object the caller still holds, which is 3 lines to check.

IT WAS TRUE, AND IT WAS STILL TRUE AT HEAD ON 2026-09-10 -- 96 days later.
`compose()` wrote through to the caller's `situation` and to each domain packet.

WHAT WAS NOT TRUE, and it matters for the severity: nothing live was corrupted.
`build_interaction_pattern` constructs a NEW DirectivePacket from the preset
tuple rather than returning the preset, and `_load_domain_directive` reads from
disk per call, so no shared object was reachable. The defect was a false
docstring plus a trap armed for the first caller to reuse a packet -- at which
point the phenotype transform would compound on every pass. That distinction is
asserted below rather than left to prose.
"""
from __future__ import annotations

import copy
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench.cdsfl_registry.composer import (  # noqa: E402
    PHENOTYPE_TRANSFORMS,
    _apply_phenotype_transform,
    build_interaction_pattern,
    compose,
)

DOMAIN = "software"
MODEL = "opus_4_6"


def _a_transforming_model() -> str:
    """A model whose phenotype transform actually changes text.

    Picked by EXECUTION, not by name. If the chosen model's transform were the
    identity, the purity test would pass whether or not compose mutated
    anything -- the vacuity this project found in 8 of its own mutation tests.
    """
    probe = build_interaction_pattern("meta_structured").text
    for name, tr in PHENOTYPE_TRANSFORMS.items():
        if _apply_phenotype_transform(probe, tr) != probe:
            return name
    pytest.skip("no phenotype transform changes text; the test would be vacuous")


class TestTheCallersPacketIsLeftAlone:
    def test_compose_does_not_mutate_the_situation_it_was_given(self):
        """THE FALSIFIER. Fails if and only if C0002's defect is present."""
        model = _a_transforming_model()
        situation = build_interaction_pattern("meta_structured")
        before = copy.deepcopy(situation)
        compose(task_domain=DOMAIN, model=model, situation=situation)
        assert situation.text == before.text, (
            "compose() rewrote the caller's situation packet in place; its "
            "docstring promises 'Pure: no side effects, no state mutation'")
        assert situation == before, "compose() changed some other field"

    def test_composing_twice_with_one_packet_gives_the_same_result(self):
        """The compounding this defect arms.

        Under the defect the second call transforms already-transformed text, so
        the 2 results differ. This is the consequence a caller would actually
        meet, as opposed to the docstring being wrong in the abstract.
        """
        model = _a_transforming_model()
        situation = build_interaction_pattern("meta_structured")
        first = compose(task_domain=DOMAIN, model=model, situation=situation)
        second = compose(task_domain=DOMAIN, model=model, situation=situation)
        # `rendered_text`, read from the dataclass, not `.text` guessed from
        # the packet's field name.
        assert first.rendered_text == second.rendered_text, (
            "composing twice from one packet gives different text, so the "
            "transform is compounding on a mutated input")


class TestTheFalsifierCanActuallyFail:
    """Without this, the tests above pass for a function that does nothing."""

    def test_the_transform_really_does_change_the_text(self):
        model = _a_transforming_model()
        probe = build_interaction_pattern("meta_structured").text
        assert _apply_phenotype_transform(probe, PHENOTYPE_TRANSFORMS[model]) != probe, (
            "the chosen transform is the identity, so a mutation would be "
            "invisible and the purity assertions above prove nothing")

    def test_the_pre_fix_expression_would_have_been_caught(self):
        """The revert, performed on a copy so the module is untouched.

        The pre-fix code was `situation.text = _apply_phenotype_transform(...)`.
        Doing exactly that to a packet and comparing against a deep copy must
        FAIL the equality the test above asserts -- which is what shows that
        assertion has teeth.
        """
        model = _a_transforming_model()
        situation = build_interaction_pattern("meta_structured")
        before = copy.deepcopy(situation)
        situation.text = _apply_phenotype_transform(
            situation.text, PHENOTYPE_TRANSFORMS[model])
        assert situation.text != before.text, (
            "the pre-fix expression leaves the packet unchanged, so this "
            "control does not reproduce the defect")


class TestTheSeverityClaimIsNotOverstated:
    """The finding is real; the disaster it implies is not, and both are said."""

    def test_the_preset_itself_was_never_reachable(self):
        """`build_interaction_pattern` returns a NEW packet, not the preset.

        If it handed back a shared object, the pre-fix mutation would have
        corrupted every later dispatch in the process. It does not, which is why
        this is a latent trap rather than a live corruption.
        """
        a = build_interaction_pattern("meta_structured")
        b = build_interaction_pattern("meta_structured")
        assert a is not b, "two calls returned the same object"
        a.text = "clobbered"
        assert build_interaction_pattern("meta_structured").text != "clobbered", (
            "mutating one packet changed what the next call returns, so the "
            "preset IS shared and this defect was live, not latent")
