# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'severity_spec_is_uncomputable_2026-11-04', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 940e238f941a2579b89c7868a75800fc4a2362e5e66485b32708e8d5c356b3a6
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The operational severity form preserves section 7.7's key property, and the
key-property producer counts each distinct registry exactly once.

Panel 2026-11-04 (severity_spec_is_uncomputable). Two executed checks:

1. KEY PROPERTY under the operational form Sev_op(f) = W(class) ·
   V(verification), i.e. `compute_sev_f` with `confidence` identically
   absent (the only state the archive has ever been in: 0 of 3,170 distinct
   entries carry the field): a REFUTED finding scores EXACTLY 0.0 for every
   class value and every confidence value a model could smuggle in,
   because V(REFUTED) = 0 annihilates the product.

2. PRODUCER SCOPE: `entries()` in
   scripts/severity_was_never_computed_from_the_model_2026-10-12.py must
   yield each distinct registry once. Before 2026-11-04 its recursive glob
   also counted sandbox_harvest copies of runner_state.json — the 5 REFUTED
   findings of commissioning_arm1_panel_20260929T214647Z each entered the
   42/37 key-property tally three times (deduplicated: 32/27, 84.3750%).
"""
import importlib.util
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench import reference_runner_v3 as rr  # noqa: E402

_PRODUCER = (REPO / "scripts" /
             "severity_was_never_computed_from_the_model_2026-10-12.py")


def _load_producer():
    spec = importlib.util.spec_from_file_location("sev_producer", _PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_refuted_scores_zero_for_every_class_and_confidence():
    for cls in (None, "", "HARD", "SOFT", "hard", "soft", "GARBAGE"):
        for conf in (None, 0.0, 0.3, 0.7, 1.0, 5.0, -1.0, "not-a-number"):
            for verdict in ("REFUTED", "refuted", " Refuted "):
                got = rr.compute_sev_f(cls, conf, verdict)
                assert got == 0.0, (
                    f"key property violated: compute_sev_f({cls!r}, {conf!r}, "
                    f"{verdict!r}) = {got!r}, expected 0.0")


def test_confirmed_and_unassessed_keep_nonzero_lattice():
    # The drop of `confidence` must not zero everything: the two
    # harness-owned factors still span the documented lattice.
    assert rr.compute_sev_f("HARD", None, "CONFIRMED") == 1.0
    assert rr.compute_sev_f("SOFT", None, "CONFIRMED") == 0.5
    assert rr.compute_sev_f("HARD", None, None) == 0.5
    assert rr.compute_sev_f("SOFT", None, "UNTOOLABLE") == 0.25


def test_producer_counts_each_distinct_registry_once(tmp_path):
    mod = _load_producer()
    state = {"registry": {"entries": {
        "C0001": {"severity": 0.9, "falsifier_verdict": "REFUTED"},
        "C0002": {"severity": 0.2, "falsifier_verdict": "CONFIRMED"},
    }}}
    other = {"registry": {"entries": {
        "C0001": {"severity": 0.1, "falsifier_verdict": "CONFIRMED"},
    }}}
    real = tmp_path / "run_a"; real.mkdir()
    copy = tmp_path / "harvest" / "files" / "bench" / "logs" / "run_a"
    copy.mkdir(parents=True)
    distinct = tmp_path / "run_b"; distinct.mkdir()
    (real / "runner_state.json").write_text(json.dumps(state))
    (copy / "runner_state.json").write_text(json.dumps(state))   # duplicate
    (distinct / "runner_state.json").write_text(json.dumps(other))
    mod.LOGS = tmp_path
    got = sorted((cid, e.get("severity")) for _fp, cid, e in mod.entries())
    assert got == [("C0001", 0.1), ("C0001", 0.9), ("C0002", 0.2)], (
        f"expected the duplicate registry to be skipped; got {got}")
