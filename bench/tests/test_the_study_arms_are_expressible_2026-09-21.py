"""Every arm of the commissioning study must be expressible on the command line.

WHAT WAS WRONG. `bench/tools/run_simulated_experiment.py` took its panel as
`VENDORS[:args.models]` -- a COUNT, resolved as a PREFIX of a fixed vendor list
whose order is CC2, DeepSeek, ChatGPT, Gemini, Codex, Fable.

Arm 3 of `experimental_notes/Programme_of_Study_Full_Scope_2026-09-21.md` is a
SEAT CONTRAST between Codex-SIM and ChatGPT-SIM, which sit at positions 4 and 2.
No value of `--models` selects that pair, so the arm could not be launched at
all. It was not a flag left off; it was an arm with no way to ask for it, and
that is the kind of gap a commissioning study exists to find BEFORE the money
is spent rather than after.

WHY EXECUTION AND NOT INSPECTION. `resolve_seats` is CALLED here with the exact
strings the study's command lines use, and the returned labels are compared to
what each arm specifies. Asserting on the source text of the argument parser
would prove only that the parser describes itself consistently, which is the
defect class `execute-do-not-grep` names and which this project has now found 4
separate times by running 2 forms against each other.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
RUNNER = REPO / "bench" / "tools" / "run_simulated_experiment.py"


def _module():
    spec = importlib.util.spec_from_file_location("run_simulated_experiment", RUNNER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_arm_3_the_seat_contrast_is_expressible():
    """The arm that could not be asked for before this change."""
    m = _module()
    assert m.resolve_seats("Codex,ChatGPT", 6) == ["Codex-SIM", "ChatGPT-SIM"]


def test_arm_3_is_unreachable_through_the_count_alone():
    """The defect itself, pinned: no --models value yields that pair.

    Without this, a later change could drop `--seats` and the suite would stay
    green while arm 3 quietly became unlaunchable again.
    """
    m = _module()
    contrast = {"Codex-SIM", "ChatGPT-SIM"}
    for count in range(1, len(m.VENDORS) + 1):
        assert set(m.resolve_seats(None, count)) != contrast, (
            f"--models {count} now yields the contrast pair; if the VENDORS order "
            "changed, this test's premise needs rewriting rather than deleting"
        )


def test_arm_2_the_single_seat_is_expressible():
    m = _module()
    assert m.resolve_seats("CC2", 6) == ["CC2-SIM"]


def test_arm_1_the_five_seat_panel_is_unchanged():
    """The default path must not move, or every existing config changes meaning."""
    m = _module()
    assert m.resolve_seats(None, 5) == list(m.VENDORS[:5])
    assert m.resolve_seats(None, 6) == list(m.VENDORS)


def test_the_suffix_is_carried_at_source_either_way():
    """Founder ruling 2026-08-08: the `-SIM` suffix is not applied downstream."""
    m = _module()
    bare = m.resolve_seats("Codex,ChatGPT", 6)
    suffixed = m.resolve_seats("Codex-SIM,ChatGPT-SIM", 6)
    assert bare == suffixed == ["Codex-SIM", "ChatGPT-SIM"]
    assert all(s.endswith("-SIM") for s in bare)


def test_order_is_preserved_because_seat_zero_is_the_manager():
    """Sorting would silently hand `player_manager` to a different seat."""
    m = _module()
    assert m.resolve_seats("Codex,ChatGPT", 6)[0] == "Codex-SIM"
    assert m.resolve_seats("ChatGPT,Codex", 6)[0] == "ChatGPT-SIM"


@pytest.mark.parametrize(
    "bad,why",
    [
        ("Codex,Codex", "a repeated seat would desynchronise the 2 panel lists"),
        ("Claude", "an unknown seat must not silently become a smaller panel"),
        (",,", "an empty selection must not silently become the default panel"),
    ],
)
def test_bad_selections_are_refused_before_any_dispatch(bad, why):
    m = _module()
    with pytest.raises(m.SeatSelectionError):
        m.resolve_seats(bad, 6)


def test_an_out_of_range_count_is_refused():
    m = _module()
    for bad in (0, -1, len(_module().VENDORS) + 1):
        with pytest.raises(m.SeatSelectionError):
            m.resolve_seats(None, bad)


def test_no_simulated_seat_carries_a_real_vendor_name_unsuffixed():
    """Provenance: a simulated agent is never labelled as a real model.

    `feedback_no_fake_model_labels` -- and the labels are what reach finding IDs,
    the log directory and the report, so an unsuffixed one contaminates the record.
    """
    m = _module()
    for seat in m.resolve_seats(None, len(m.VENDORS)):
        assert seat.endswith("-SIM"), seat


# ---------------------------------------------------------------------------
# The rest of the arm configuration, parsed rather than read.
#
# `CDSFL_Programme_of_Study_2026-09-17.txt` specifies the arms run "with routing,
# the falsifier gate and the admissibility gate on, and the hardened gate, merge
# arbitration and immune memory off", and the same document records that the run
# it describes "has no launcher". Every item in that sentence was reachable
# except merge arbitration, which was a bare `True` in the config literal.
# ---------------------------------------------------------------------------


def test_merge_arbitration_can_be_turned_off():
    """The pre-registered arm design needs it off; it had no switch at all."""
    m = _module()
    args = m.build_parser().parse_args(["--no-merge-arbitration"])
    assert args.no_merge_arbitration is True


def test_merge_arbitration_defaults_to_on():
    """Default unchanged: disabling a shipped capability needs a measurement."""
    m = _module()
    assert m.build_parser().parse_args([]).no_merge_arbitration is False


def test_the_domain_is_selectable_and_defaults_to_statistics():
    """It was a bare literal, so every target was briefed as a statistics task."""
    m = _module()
    assert m.build_parser().parse_args([]).domain == "statistics"
    assert m.build_parser().parse_args(["--domain", "software"]).domain == "software"


def test_the_prose_arm_target_is_accepted_by_the_parser():
    """Arm 4 commissions A19 and needs a markdown target carrying fenced Python."""
    m = _module()
    args = m.build_parser().parse_args(
        ["--target", "bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md"])
    assert args.target.endswith(".md")
    assert (REPO / args.target).is_file(), (
        "the prose arm's candidate target named in the 17 September programme "
        "is missing; arm 4 cannot commission A19 without one"
    )


def test_a_full_arm_command_line_parses_end_to_end():
    """Arm 3 as it will actually be launched, parsed in one go."""
    m = _module()
    args = m.build_parser().parse_args([
        "--seats", "Codex,ChatGPT", "--rounds", "8",
        "--target", "bench/dm/_memory.py", "--no-merge-arbitration",
        "--domain", "software", "--name", "commissioning_arm3",
    ])
    assert m.resolve_seats(args.seats, args.models) == ["Codex-SIM", "ChatGPT-SIM"]
    assert args.rounds == 8 and args.no_merge_arbitration is True
