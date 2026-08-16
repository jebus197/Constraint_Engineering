"""The similarity function's justifying measurement must stay reproducible.

WHY THIS EXISTS. Until 2026-08-16 the numbers that justify the similarity
function — 438 same-location critical pairs, tier-2 medians 0.559 against 0.000,
Mann-Whitney p = 1.9e-25, tier-3 coverage 94 of 165 — existed ONLY as prose
comments in `bench/convergence_location.py`. Nothing stored the pair dataset,
nothing recomputed it, and no test would have noticed if a change to the
extractors had silently invalidated every one of them.

That is the same failure class this project keeps finding in its own instruments:
a claim and its evidence stored in different places, so the claim outlives the
evidence without anything reporting a problem. These tests bind them together.

They are deliberately CHEAP — no embedding model, no bootstrap. They check that
the dataset still rebuilds to the recorded shape from the archive. The expensive
parts (labels, AUC, operating points) live in the script and are run by hand.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

_SPEC = importlib.util.spec_from_file_location(
    "similarity_operating_characteristic",
    REPO / "scripts" / "similarity_operating_characteristic.py")
OC = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(OC)

from bench.tests.test_combined_identity_rule import ARCHIVE as RULE_ARCHIVE  # noqa: E402


def _archive_present() -> bool:
    try:
        for run in OC.ARCHIVE:
            OC._report(run)
    except FileNotFoundError:
        return False
    return True


pytestmark = pytest.mark.skipif(
    not _archive_present(), reason="archived runs not present on this machine")


@pytest.fixture(scope="module")
def data():
    """Rebuilt from the archive, NOT read from the cached JSON.

    Reading the cache would make these tests pass forever regardless of what the
    extractors do, which is precisely the failure being guarded against.
    """
    return OC.build_dataset()


def test_the_two_archive_tables_name_the_same_runs_and_targets():
    """`scripts/similarity_operating_characteristic.py` and
    `test_combined_identity_rule.py` each carry an ARCHIVE table. Two tables that
    must agree and are not checked against each other are a divergence waiting to
    happen — and a divergence here would mean the script and the rule's own tests
    were measuring different populations while both looked healthy."""
    assert set(OC.ARCHIVE) == set(RULE_ARCHIVE)
    for run in OC.ARCHIVE:
        stem_s, target_s = OC.ARCHIVE[run]
        stem_r, target_r, _conv = RULE_ARCHIVE[run]
        assert stem_s == stem_r, f"{run}: log stem differs between the two tables"
        assert target_s == target_r, f"{run}: target differs between the two tables"


# Figures derivable from the archive alone. The remaining two — n_same, n_diff —
# are counts of EMBEDDING LABELS and cannot be recomputed without loading the
# sentence-transformer, so they are checked separately against the cached dataset
# and skipped when it is absent. Keeping the split explicit matters: a test that
# quietly needed a 90 MB model download would be disabled by the first person who
# ran the suite offline, and would then guard nothing while still looking green.
STRUCTURAL = ["criticals", "tier2_coverage", "tier3_coverage", "pairs"]
LABEL_DEPENDENT = ["n_same", "n_diff"]


@pytest.mark.parametrize("field", STRUCTURAL)
def test_each_recorded_figure_still_reproduces(data, field):
    """The figures written into `bench/convergence_location.py`'s comment block.

    A failure here does not necessarily mean the code is wrong — it means the
    COMMENT is now describing a measurement that no longer holds, and one of the
    two must move. Treat stale documentation as a defect of equal standing.
    """
    got = {n: g for n, g, _w, _ok in OC.reproduce(data)}
    assert got[field] == OC.RECORDED[field], (
        f"{field}: archive now gives {got[field]}, comment records "
        f"{OC.RECORDED[field]}. Re-run "
        f"`python3 scripts/similarity_operating_characteristic.py --rebuild` "
        f"and update the comment block in bench/convergence_location.py.")


@pytest.mark.parametrize("field", LABEL_DEPENDENT)
def test_the_label_counts_still_match_the_cached_dataset(field):
    import json
    if not OC.CACHE.is_file():
        pytest.skip("no cached dataset; run the script with --rebuild")
    cached = json.loads(OC.CACHE.read_text(encoding="utf-8"))
    got = {n: g for n, g, _w, _ok in OC.reproduce(cached)}
    assert got[field] == OC.RECORDED[field], (
        f"{field}: cached dataset gives {got[field]}, comment records "
        f"{OC.RECORDED[field]}.")


def test_the_pair_count_is_the_full_population_not_the_gate_population(data):
    """Guards a subtlety that cost real time to establish.

    `CL._gate_population` filters terminal-non-novel entries and was added on
    2026-08-12, AFTER the 438 figure was recorded. Rebuilding through it gives
    136 located criticals and 423 pairs, not 139 and 438. Anyone re-deriving this
    dataset will reach for the gate population because it is the more principled
    choice, get 423, and conclude the recorded figure was wrong. It is not — it
    is a different population, and this test says so where they will look.
    """
    assert len(data["pairs"]) == 438
    located = [c for c in data["criticals"] if c["locations"]]
    assert len(located) == 139
    assert len(data["criticals"]) == 165


def test_every_pair_shares_at_least_one_location(data):
    """The defining property. Without it these are not same-location pairs and
    tiers 2 and 3 are being measured outside the regime they are bounded to."""
    for p in data["pairs"]:
        assert p["shared_locations"], f"{p['run']} {p['a']}/{p['b']} shares no location"


def test_tier2_similarity_is_symmetric_on_the_archive(data):
    """An asymmetric similarity would make the rule's answer depend on arrival
    order — two runs over the same findings could then converge differently."""
    import bench.convergence_location as CL
    for p in data["pairs"][:200]:
        a = CL.stem_signature(p["a_desc"])
        b = CL.stem_signature(p["b_desc"])
        assert CL.signature_similarity(a, b) == CL.signature_similarity(b, a)
