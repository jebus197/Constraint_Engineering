"""Commissioned tests for canary seeding.

Every guard is fed BOTH a case it must accept and a case it must refuse. A guard
tested only on input it accepts is indistinguishable from no guard at all -- the
note-standard lint sat in the tree from v1.5 doing exactly that, passing forever
because nothing was ever run against it.
"""
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.canary_seeding import (            # noqa: E402
    CALIBRATION, HELD_OUT, Canary, CanaryIntegrityError,
    catches, detection_rate, load_catalogue, seed,
)

DOC = ("The sampling theorem requires f_s > 2*f_max for exact reconstruction.\n"
       "With N = 1024 points the bin spacing is 1.5625 Hz.\n"
       "The filter has unity gain in the passband.\n")


def _c(cid, find, replace, *, split=HELD_OUT, gen="handwritten", domain="dsp"):
    return Canary(id=cid, domain=domain, defect_class="reasoning", generator=gen,
                  split=split, find=find, replace=replace, summary=f"{cid} ground truth")


# --------------------------------------------------------------------------- #
# The catalogue must never live in the repository                              #
# --------------------------------------------------------------------------- #
def test_refuses_a_catalogue_inside_the_repository(tmp_path):
    inside = REPO / "bench" / "_canary_probe.json"
    inside.write_text(json.dumps({"canaries": []}), encoding="utf-8")
    try:
        with pytest.raises(CanaryIntegrityError, match="inside the repository"):
            load_catalogue(inside)
    finally:
        inside.unlink()


def test_accepts_a_catalogue_outside_the_repository(tmp_path):
    """The known-GOOD half. Without it the guard could be `raise` on every path."""
    out = tmp_path / "cat.json"
    out.write_text(json.dumps({"canaries": [
        {"id": "K1", "domain": "dsp", "defect_class": "reasoning", "generator": "handwritten",
         "split": HELD_OUT, "find": "a", "replace": "b", "summary": "s"}]}), encoding="utf-8")
    got = load_catalogue(out)
    assert [c.id for c in got] == ["K1"]


# --------------------------------------------------------------------------- #
# Seeding                                                                      #
# --------------------------------------------------------------------------- #
def test_seeds_and_reports_both_hashes():
    seeded, man = seed(DOC, [_c("K1", "f_s > 2*f_max", "f_s > f_max")])
    assert "f_s > f_max" in seeded and "2*f_max" not in seeded
    assert man["clean_sha256"] != man["seeded_sha256"]
    assert man["canaries"][0]["id"] == "K1"


def test_refuses_an_ambiguous_location():
    doc = "the gain is unity\nthe gain is unity\n"
    with pytest.raises(ValueError, match="occurs 2 times"):
        seed(doc, [_c("K1", "the gain is unity", "the gain is 2")])


def test_refuses_a_find_that_is_not_there():
    with pytest.raises(ValueError, match="not present"):
        seed(DOC, [_c("K1", "no such text", "x")])


def test_refuses_duplicate_ids():
    with pytest.raises(ValueError, match="duplicate canary id"):
        seed(DOC, [_c("K1", "unity gain", "zero gain"), _c("K1", "1024", "512")])


def test_seeding_nothing_is_not_a_measurement():
    with pytest.raises(ValueError, match="seeding nothing"):
        seed(DOC, [])


# --------------------------------------------------------------------------- #
# Blinding -- the seeded document must not announce itself                     #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("replacement,why", [
    ("f_s > f_max  # K1", "the canary id"),
    ("f_s > f_max  # handwritten", "the generator name"),
    ("f_s > f_max  # K1 ground truth", "the ground-truth summary"),
    ("f_s > f_max  # canary", "the word canary"),
    ("f_s > f_max  # seeded here", "the word seeded"),
])
def test_broken_blinding_is_refused(replacement, why):
    with pytest.raises(CanaryIntegrityError):
        seed(DOC, [_c("K1", "f_s > 2*f_max", replacement)])


def test_clean_blinding_is_accepted():
    """Known-GOOD: a plain mutation with no tell must pass."""
    seeded, _ = seed(DOC, [_c("K1", "f_s > 2*f_max", "f_s > f_max")])
    assert "K1" not in seeded


# --------------------------------------------------------------------------- #
# Scoring                                                                      #
# --------------------------------------------------------------------------- #
def test_no_verifier_scores_nothing_rather_than_guessing():
    """Absent evidence, the honest answer is that nothing is demonstrated."""
    assert catches([{"model": "m"}], [_c("K1", "a", "b")], verifier=None) == {}


def test_counterfactual_verifier_decides_the_catch():
    cs = [_c("K1", "f_s > 2*f_max", "f_s > f_max"),
          _c("K2", "1.5625 Hz", "15.625 Hz", gen="generated")]
    finds = [{"model": "alpha", "hits": {"K1"}}, {"model": "beta", "hits": set()}]
    got = catches(finds, cs, verifier=lambda f, c: c.id in f["hits"])
    assert got == {"alpha": ["K1"]}


def test_p_hat_is_held_out_only():
    cs = [_c("H1", "a", "b"), _c("H2", "c", "d", gen="generated"),
          _c("C1", "e", "f", split=CALIBRATION)]
    # alpha killed one held-out and the calibration one; only the held-out counts.
    r = detection_rate({"alpha": ["H1", "C1"]}, cs)
    assert r == {"alpha": 0.5}, "calibration canaries must not inflate p_hat"


def test_p_hat_refuses_a_single_generator_held_out_set():
    cs = [_c("H1", "a", "b"), _c("H2", "c", "d")]        # both handwritten
    with pytest.raises(CanaryIntegrityError, match="single generator"):
        detection_rate({"alpha": ["H1"]}, cs)


def test_p_hat_refuses_when_there_is_nothing_held_out():
    cs = [_c("C1", "a", "b", split=CALIBRATION)]
    with pytest.raises(CanaryIntegrityError, match="no held-out canaries"):
        detection_rate({"alpha": []}, cs)


def test_p_hat_is_per_domain_when_asked():
    cs = [_c("D1", "a", "b", domain="dsp"), _c("D2", "c", "d", domain="dsp", gen="generated"),
          _c("B1", "e", "f", domain="bio"), _c("B2", "g", "h", domain="bio", gen="generated")]
    caught = {"alpha": ["D1", "D2", "B1"]}
    assert detection_rate(caught, cs, domain="dsp") == {"alpha": 1.0}
    assert detection_rate(caught, cs, domain="bio") == {"alpha": 0.5}


# --------------------------------------------------------------------------- #
# Construction                                                                 #
# --------------------------------------------------------------------------- #
def test_a_canary_that_changes_nothing_is_rejected():
    with pytest.raises(ValueError, match="find == replace"):
        _c("K1", "same", "same")


def test_an_unknown_split_is_rejected():
    with pytest.raises(ValueError, match="split must be one of"):
        Canary(id="K1", domain="d", defect_class="c", generator="g",
               split="whatever", find="a", replace="b", summary="s")
