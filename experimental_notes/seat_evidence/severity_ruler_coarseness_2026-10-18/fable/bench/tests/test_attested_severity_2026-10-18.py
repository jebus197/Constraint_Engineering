# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'severity_ruler_coarseness_2026-10-18', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: b738a53c0c4338b056e57b28fff9dbbab5f568a4489fba4fa75e9840ca4b8eb0
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The severity ruler's de-coarsening: pooled attestations, executed falsifier.

Panel task C4 (founder question of 2026-10-04): the asserted severity wobbles
~0.14 between repeat assessments against a ~0.09 decision half-band, so the
0.7 cut decides criticality partly at random. Section 7.7's V corrects with
the falsifier verdict but leaves the asserted number's own noise untouched in
the unresolved (V=0.5) population. The registry already holds k independent
assessments of each co-discovered defect; `attested_severity` pools them by
median and `stamp_attested_severity` records the result BESIDE the asserted
number, default off, moving no gate (the stamp_sev_f precedent).

WHAT THIS FILE WOULD PRINT IF THE FIX WERE WRONG: pytest FAILED lines with
AssertionError naming the broken property -- identity at k=1, median at k>=2,
self-reference admitted, severity mutated, flag-off mutation, or the leg3
archive numbers (C0001 star median 0.875; C0011 star crossing 0.78 -> 0.64;
settled-series gamma_critical unchanged at 1.000 under the pooled ruler).
It prints `passed` now.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
for _p in (str(REPO), str(REPO / "bench")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from bench.reference_runner_v3 import (  # noqa: E402
    RunnerConfig,
    attested_severity,
    stamp_attested_severity,
    _settled_novelty_series,
    _estimate_gamma,
)

LEG3 = (REPO / "bench" / "logs"
        / "leg3_final_shakedown_20261015T220118Z" / "runner_state.json")


class _FakeReg:
    def __init__(self, entries):
        self.entries = entries


def _entry(cid, sev, occs=()):
    return {"canonical_id": cid, "severity": sev,
            "occasions": [{"via": "codiscovery", "from_canonical": d}
                          for d in occs]}


def _cfg(**kw):
    # RunnerConfig requires positional identity fields in some revisions;
    # construct defensively via defaults only.
    try:
        return RunnerConfig(**kw)
    except TypeError:
        cfg = RunnerConfig.__new__(RunnerConfig)
        for k, v in kw.items():
            setattr(cfg, k, v)
        return cfg


def test_k1_is_byte_identical_to_the_asserted_number():
    e = _entry("C0001", 0.73)
    med, n, spread = attested_severity(e, {"C0001": e})
    assert (med, n, spread) == (0.73, 1, 0.0)


def test_median_over_the_direct_star_odd_and_even():
    ents = {
        "C0001": _entry("C0001", 0.9, ["C0002", "C0003"]),
        "C0002": _entry("C0002", 0.5),
        "C0003": _entry("C0003", 0.8),
    }
    med, n, _ = attested_severity(ents["C0001"], ents)
    assert n == 3 and med == 0.8  # median of [0.5, 0.8, 0.9]
    ents["C0001"]["occasions"].append(
        {"via": "codiscovery", "from_canonical": "C0004"})
    ents["C0004"] = _entry("C0004", 0.6)
    med, n, _ = attested_severity(ents["C0001"], ents)
    assert n == 4 and med == pytest.approx(0.7)  # (0.6 + 0.8) / 2 on [.5,.6,.8,.9]


def test_self_reference_absent_members_and_non_codiscovery_are_refused():
    e = _entry("C0001", 0.9, ["C0001", "C9999"])
    e["occasions"].append({"via": "register", "from_canonical": "C0002"})
    ents = {"C0001": e, "C0002": _entry("C0002", 0.1)}
    med, n, spread = attested_severity(e, ents)
    assert (med, n, spread) == (0.9, 1, 0.0)


def test_duplicate_occasions_counted_once():
    e = _entry("C0001", 0.9, ["C0002", "C0002"])
    ents = {"C0001": e, "C0002": _entry("C0002", 0.5)}
    med, n, _ = attested_severity(e, ents)
    assert n == 2 and med == pytest.approx(0.7)


def test_default_off_is_a_no_op_and_mutates_nothing():
    ents = {"C0001": _entry("C0001", 0.9, ["C0002"]),
            "C0002": _entry("C0002", 0.5)}
    before = json.dumps(ents, sort_keys=True)
    assert stamp_attested_severity(_FakeReg(ents), _cfg(), 3) == 0
    assert json.dumps(ents, sort_keys=True) == before


def test_flag_on_stamps_beside_and_never_touches_severity():
    ents = {"C0001": _entry("C0001", 0.9, ["C0002"]),
            "C0002": _entry("C0002", 0.5)}
    n = stamp_attested_severity(
        _FakeReg(ents), _cfg(severity_attestation_enabled=True), 3)
    assert n == 2
    rec = ents["C0001"]["severity_attested"]
    assert rec["value"] == pytest.approx(0.7) and rec["n"] == 2
    assert rec["informative_only"] is True and rec["round"] == 3
    assert ents["C0001"]["severity"] == 0.9  # asserted number untouched
    assert ents["C0002"]["severity"] == 0.5


@pytest.mark.skipif(not LEG3.exists(), reason="leg3 archive not present")
def test_leg3_archive_star_medians_and_gamma_invariance():
    ents = json.load(open(LEG3))["registry"]["entries"]
    # C0001 was sighted by 6 seats: [0.9, 0.9, 0.85, 0.9, 0.85, 0.78].
    med, n, spread = attested_severity(ents["C0001"], ents)
    assert n == 6 and med == pytest.approx(0.875) and spread == pytest.approx(0.12)
    # The de-coarsening is CAPABLE of firing: C0011 (asserted 0.78, critical
    # alone) pools with its co-sighting C0017 (0.5) to 0.64, below the cut.
    med, n, _ = attested_severity(ents["C0011"], ents)
    assert n == 2 and med == pytest.approx(0.64)
    # And the convergence instrument does not move on this archive: the
    # settled-series gamma_critical is 1.000 under both rulers.
    max_round = 4
    _, crit_asserted = _settled_novelty_series(_FakeReg(ents), max_round)
    pooled = {cid: dict(e, severity=attested_severity(e, ents)[0])
              for cid, e in ents.items()}
    _, crit_pooled = _settled_novelty_series(_FakeReg(pooled), max_round)
    assert _estimate_gamma(crit_asserted, 3) == pytest.approx(1.0)
    assert _estimate_gamma(crit_pooled, 3) == pytest.approx(1.0)
    assert crit_asserted[1:] == crit_pooled[1:] == [0, 0, 0, 0]
