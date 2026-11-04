# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_severity_spec_is_uncomputable_2026-11-04', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: efbb87765e445fcb7f0950b6748b0fe5ce96639143afe48fa81f6fef1841c470
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The critical partition's key property (appendix 7.7), on all THREE readers.

2026-11-04 joint severity round. `spec_critical_severity` annihilates the
asserted severity iff this harness's own falsifier verdict is REFUTED, and is
read by `_settled_novelty_series`, `_corroborated_novelty_series` and
`_location_keyed_critical_series` (the third GATES whenever
`location_keyed_convergence` is set -- 16 configs -- and was named by neither
round-1 seat). Every test EXECUTES the real readers; none asserts source text.

Measured basis (scripts/both_severity_substitutions_one_archive_one_gate_2026-11-04.py,
67 distinct archived registries, real gate): this form flips 0 archived
convergence verdicts; `asserted * V` flips 11 (all manufactured, vacuous
branch); `W(class) * V` flips 26 (the same 11 plus 15 blocked).
"""
import copy
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest  # noqa: E402

import bench.reference_runner_v3 as rr  # noqa: E402

SYMS = ["wilson_interval"]


def _reg(entries):
    r = rr.FindingRegistry()
    r.entries = entries
    return r


def _entry(**kw):
    e = {"canonical_id": "C0001", "severity": 0.9, "status": "OPEN",
         "falsifier_verdict": None, "open_since_round": 1,
         "description": "`wilson_interval` mis-centres the numerator"}
    e.update(kw)
    return e


def _crit_counts(reg):
    _, a = rr._settled_novelty_series(reg, 3)
    _, b = rr._corroborated_novelty_series(reg, 3)
    c = rr._location_keyed_critical_series(reg, 3, SYMS)
    return sum(a), sum(b), sum(c)


# [A] KEY PROPERTY: a disproved finding is not a critical discovery.
def test_refuted_is_not_a_critical_discovery_in_any_reader():
    reg = _reg({"C0001": _entry(falsifier_verdict="REFUTED")})
    assert _crit_counts(reg) == (0, 0, 0)


def test_refuted_still_counts_as_a_finding_in_all_s():
    reg = _reg({"C0001": _entry(falsifier_verdict="REFUTED")})
    all_s, _ = rr._settled_novelty_series(reg, 3)
    assert sum(all_s) == 1


@pytest.mark.parametrize("asserted", [0.0, 0.3, 0.7, 0.9, 1.0])
def test_annihilation_is_independent_of_the_asserted_float(asserted):
    e = _entry(severity=asserted, falsifier_verdict="REFUTED")
    assert rr.spec_critical_severity(e) == 0.0


# [B] The A4-relevant population must NOT be de-escalated (V(None)=0.5 is the
# measured manufactured-convergence mechanism and is deliberately NOT applied).
def test_unresolved_critical_stays_critical_in_every_reader():
    reg = _reg({"C0001": _entry(falsifier_verdict=None)})
    assert _crit_counts(reg) == (1, 1, 1)


def test_confirmed_critical_stays_critical_in_every_reader():
    reg = _reg({"C0001": _entry(falsifier_verdict="CONFIRMED")})
    assert _crit_counts(reg) == (1, 1, 1)


def test_confirmed_subcritical_is_not_promoted():
    # W(class)*V would score this 1.0 and block convergence on it; the
    # restricted form leaves the asserted 0.3 alone.
    e = _entry(severity=0.3, falsifier_verdict="CONFIRMED")
    assert rr.spec_critical_severity(e) == 0.3
    reg = _reg({"C0001": e})
    assert _crit_counts(reg) == (0, 0, 0)


# [C] Verdict reversal self-heals: the function reads the LIVE field.
def test_refuted_to_confirmed_reversal_restores_the_count():
    e = _entry(falsifier_verdict="REFUTED")
    reg = _reg({"C0001": e})
    assert _crit_counts(reg) == (0, 0, 0)
    e["falsifier_verdict"] = "CONFIRMED"
    assert _crit_counts(reg) == (1, 1, 1)


# [D] A refuted claim must not INOCULATE its location: a later genuine critical
# at the same location still counts as new in the location-keyed series.
def test_refuted_entry_does_not_inoculate_its_location():
    reg = _reg({
        "C0001": _entry(falsifier_verdict="REFUTED", open_since_round=0),
        "C0002": _entry(canonical_id="C0002", falsifier_verdict="CONFIRMED",
                        open_since_round=2),
    })
    series = rr._location_keyed_critical_series(reg, 3, SYMS)
    assert series == [0, 0, 1, 0]


# [E] The defect is DEMONSTRABLE: with the raw read restored, every reader
# counts the disproved finding -- the falsifier fails iff the defect is present.
def test_raw_read_restores_the_defect(monkeypatch):
    monkeypatch.setattr(rr, "spec_critical_severity",
                        lambda e: float(e.get("severity") or 0.0))
    reg = _reg({"C0001": _entry(falsifier_verdict="REFUTED")})
    assert _crit_counts(reg) == (1, 1, 1)


# [F] REPLAY INVARIANCE: the repair changes 0 archived convergence verdicts.
def _distinct_states():
    repo = Path(__file__).resolve().parents[2]
    seen = set()
    for f in sorted(repo.glob("bench/logs/**/runner_state.json")):
        h = hashlib.sha256(f.read_bytes()).hexdigest()
        if h in seen:
            continue
        seen.add(h)
        yield f, json.loads(f.read_text())


def _gate(reg, max_round, cfg):
    all_s, crit_s = rr._settled_novelty_series(reg, max_round)
    ok, _ = rr._check_gamma_alt_convergence(
        round_idx=max_round, gamma=rr._estimate_gamma(all_s),
        novel_critical_history=crit_s, cfg=cfg,
        gamma_critical=rr._estimate_gamma(crit_s),
        total_findings=sum(all_s))
    return ok


def test_no_archived_convergence_verdict_is_restated(monkeypatch):
    cfg = rr.RunnerConfig()
    replayed = moved = 0
    for f, state in _distinct_states():
        entries = (state.get("registry") or {}).get("entries") or {}
        if not entries:
            continue
        nch = state.get("novel_critical_history") or []
        max_round = (len(nch) - 1 if nch else
                     max((e.get("open_since_round") or 0)
                         for e in entries.values()))
        reg = _reg(copy.deepcopy(entries))
        with monkeypatch.context() as m:
            m.setattr(rr, "spec_critical_severity",
                      lambda e: float(e.get("severity") or 0.0))
            before = _gate(reg, max_round, cfg)
        after = _gate(reg, max_round, cfg)
        replayed += 1
        if before != after:
            moved += 1
    assert replayed >= 60   # the archive is present and deduplicated
    assert moved == 0, f"{moved} of {replayed} archived gate verdicts moved"
