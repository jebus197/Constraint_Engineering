"""Every seat is described, and no 2 seats are described as the same model.

WHAT THIS ENCODES. His ruling of 2026-09-20 made `cx` a DISTINCT model from
`cgpt`; the project's own record of it states that before the ruling both pointed
at `openai/gpt-5.5`, "so the panel had 4 architectures and reported 5". The live
DISPATCH honours that ruling. `MODEL_ROSTER` did not: it described both `Codex`
and `ChatGPT` as "GPT-5.5 (OpenAI)", reproducing in prose exactly the confusion
the ruling removed, and `describe_model` reaches a report line.

AND `Fable` WAS ABSENT from the table, so `describe_model` returned the bare
label. The miss was already ANNOUNCED by `resolve_or_alarm` and simply never
filled -- detection without repair -- and a simulated Fable seat was reported as
"SIMULATED stand-in for Fable", which tells a reader nothing about which model
stood in.

★ THIS GUARDS THE PROPERTIES, NOT THE STRINGS. It does not assert that Codex is
described as any particular text, because the panel rotates and a pinned literal
would go stale the next time it does -- the failure mode recorded in
`feedback_a_guard_can_accuse_correct_code_2026-10-28`, where 9 of 36 baseline
failures were guards pinning a value rather than a property. What it asserts is
that every seat is described, that no 2 seats share a description, and that the
description does not contradict the live dispatch.

★ IT TAKES NO POSITION ON THE PHENOTYPE KEYS, which is the founder's decision.
4 of 6 keys name a superseded version, measured by
`scripts/how_many_seats_are_keyed_to_a_stale_version_2026-11-02.py`, and a key
indexes a fingerprint that a future run reads back as a prior. Asserting anything
about them here would pre-empt that decision and would redden the board under
either answer.
"""
from __future__ import annotations

import collections
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench import runner_core as rc                            # noqa: E402
from bench.reference_runner_v3 import (                        # noqa: E402
    MODEL_ROSTER, describe_model)


class TestEverySeatIsDescribed:

    def test_no_seat_in_model_specs_is_missing_from_the_roster(self):
        """A missing entry makes a seat describe itself in a report."""
        missing = sorted(set(rc.MODEL_SPECS) - set(MODEL_ROSTER))
        assert not missing, (
            f"{missing} are dispatchable seats with no roster description, so "
            f"describe_model returns the bare label and a report says only the "
            f"seat's own name")

    @pytest.mark.parametrize("label", sorted(rc.MODEL_SPECS))
    def test_describe_model_says_more_than_the_label(self, label):
        got = describe_model(label)
        assert got != label, (
            f"describe_model({label!r}) returned the label itself, which is the "
            f"silent-default shape resolve_or_alarm exists to announce")
        assert len(got) > len(label), got

    def test_a_simulated_label_names_the_model_it_stands_in_for(self):
        """The provenance rule: a simulated seat must say what it stood in for.

        The standing directive forbids labelling a simulated agent with a real
        model's name, and the other half of that is that a simulated stand-in
        must say WHICH model it replaced, or the record is unattributable.
        """
        got = describe_model("Fable-SIM")
        assert "SIMULATED" in got
        assert "no paid dispatch occurred" in got
        assert got != "SIMULATED stand-in for Fable -- no paid dispatch occurred", (
            "the stand-in names only the bare label, so the report does not say "
            "which model was simulated")


class TestNoTwoSeatsShareADescription:
    """The property his 2026-09-20 ruling is about."""

    def test_descriptions_are_distinct_across_seats(self):
        counts = collections.Counter(MODEL_ROSTER.values())
        shared = {d: n for d, n in counts.items() if n > 1}
        if shared:
            who = {d: sorted(k for k, v in MODEL_ROSTER.items() if v == d)
                   for d in shared}
            pytest.fail(
                f"2 or more seats are described as the same model: {who}. That is "
                f"the state his ruling of 2026-09-20 corrected -- the panel then "
                f"had 4 architectures and reported 5. If 2 seats genuinely run "
                f"the same model, the roster should say so explicitly rather than "
                f"by collision.")

    def test_the_description_does_not_contradict_the_live_dispatch(self):
        """Codex dispatches on a codex model, so its description must not deny it.

        Checked against the dispatch site rather than against a remembered
        string, so a future route change moves both together.
        """
        orch = (REPO / "bench" / "experiment_11_orchestrator.py").read_text()
        assert "openai/gpt-5.3-codex" in orch, (
            "the orchestrator no longer dispatches a codex model; this test's "
            "anchor is gone and the roster description should be re-checked "
            "against whatever it now sends")
        desc = MODEL_ROSTER.get("Codex", "")
        assert "codex" in desc.lower(), (
            f"Codex is described as {desc!r}, which does not name a codex model "
            f"while the live dispatch sends openai/gpt-5.3-codex. Before the "
            f"2026-09-20 ruling this seat and ChatGPT both ran gpt-5.5; the "
            f"description must not reproduce that.")


class TestItDoesNotPreEmptHisDecision:
    """The phenotype keys are his; this file must stay silent on them."""

    def test_this_file_asserts_nothing_about_a_phenotype_key(self):
        """Enforced on this file's own source, so a later edit cannot drift.

        The identifier is assembled from parts rather than written out, because a
        literal would put the pattern into the very text being searched -- the
        self-matching trap hit twice on 2026-11-02.
        """
        body = pathlib.Path(__file__).read_text().split('"""', 2)[-1]
        needle = "COMPOSER_" + "MODEL_" + "MAP"
        assert needle not in body, (
            "this file reaches for the phenotype key map; renaming those keys is "
            "the founder's decision and a guard here would pre-empt it")
