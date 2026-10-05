# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'fingerprint_ladder_review_2026-10-05', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: d871de4d3866672e0fdeff052d93f20e4c07fc4eb19ae596656d1e42f09fa0c6
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The ladder rungs routing actually TRIES must span more than one model.

WHY THIS EXISTS (panel review, 2026-10-05, by execution). `bench/routing.py`
tries only the first ``routing_max_rungs`` rungs (RunnerConfig default 2), and
`rank_falsifier_writers` puts {Codex-SIM, CC2-SIM, ChatGPT-SIM} at the top for
every source seat. With all three mapped to ``opus`` in
``sim_dispatch_shim.DEFAULT_LADDER``, the EXERCISED prefix was (opus, opus) for
6 of 6 source seats: the seat map presented 2 distinct models across the 5
rungs, and the capability CLIMB -- one model taking over from a DIFFERENT model,
the one thing the ladder exists to rehearse -- still never ran. That is the same
class as the 2026-08-30 finding in `rank_falsifier_writers`' own comment, where
routing ran but exercised the unknown-model fallback instead of the ladder.

``Codex-SIM`` now maps to ``fable``, which makes the exercised prefix mixed for
5 of 6 source seats. 5 of 6 is the maximum reachable with 2 model ids while
``CC2-SIM`` stays pinned to ``opus`` (roster: cc2 runs opus): a Codex-sourced
finding's prefix is (CC2-SIM, ChatGPT-SIM), and mixing it would force
ChatGPT-SIM onto ``fable``, which breaks the CC2-sourced prefix instead.

Producer: `scripts/the_provenance_gate_reads_text_not_behaviour_2026-10-05.py`
section 4.
"""
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.routing import rank_falsifier_writers  # noqa: E402
from bench.tools.sim_dispatch_shim import DEFAULT_LADDER  # noqa: E402


def _default_max_rungs() -> int:
    """RunnerConfig.routing_max_rungs' default, read from the dataclass field so
    this test follows the runner rather than restating a literal 2."""
    import dataclasses
    from bench.reference_runner_v3 import RunnerConfig
    for f in dataclasses.fields(RunnerConfig):
        if f.name == "routing_max_rungs":
            return int(f.default)
    raise AssertionError("RunnerConfig no longer has routing_max_rungs")


def _mixed_prefixes(ladder: dict) -> dict:
    """source seat -> whether the exercised rung prefix spans >1 model."""
    k = _default_max_rungs()
    seats = list(ladder)
    out = {}
    for src in seats:
        prefix = rank_falsifier_writers(seats, exclude=(src,))[:k]
        out[src] = len({ladder[r] for r in prefix}) > 1
    return out


class TestTheExercisedPrefixIsMixed:
    def test_most_source_seats_get_a_genuine_climb(self):
        mixed = _mixed_prefixes(DEFAULT_LADDER)
        n = sum(mixed.values())
        assert n >= 5, (
            f"only {n} of {len(mixed)} source seats get a mixed exercised rung "
            f"prefix ({mixed}); the capability climb between two DIFFERENT "
            f"models is unrehearsed again, which is the pre-2026-08-30 state "
            f"with a different cause")

    def test_the_generic_prefix_is_mixed(self):
        """The most common case: a finding from any seat outside the top rungs.
        Its prefix is (Codex-SIM, CC2-SIM) and must span 2 models."""
        k = _default_max_rungs()
        prefix = rank_falsifier_writers(list(DEFAULT_LADDER),
                                        exclude=("DeepSeek-SIM",))[:k]
        models = {DEFAULT_LADDER[r] for r in prefix}
        assert len(models) > 1, (
            f"prefix {prefix} resolves to {models}: uniform -- routing climbs "
            f"between two identical models")

    def test_the_probe_detects_the_defect_it_was_written_for(self):
        """ANTI-VACUITY. On the pre-2026-10-05 map (Codex-SIM -> opus), the
        probe must report 0 of 6 mixed, which is the measured defect state."""
        old = dict(DEFAULT_LADDER, **{"Codex-SIM": "opus"})
        mixed = _mixed_prefixes(old)
        assert sum(mixed.values()) == 0, (
            "the probe no longer sees the all-opus prefix as uniform, so the "
            "passing tests above vouch for nothing")

    def test_only_rostered_model_ids_are_used(self):
        """Same rule as the ladder's own test: no invented model id."""
        assert set(DEFAULT_LADDER.values()) <= {"opus", "fable"}
