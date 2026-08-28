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
    r = detection_rate({"alpha": ["H1", "C1"]}, cs, models=["alpha"], seeded_ids=[c.id for c in cs])
    assert r == {"alpha": 0.5}, "calibration canaries must not inflate p_hat"


def test_p_hat_refuses_a_single_generator_held_out_set():
    cs = [_c("H1", "a", "b"), _c("H2", "c", "d")]        # both handwritten
    with pytest.raises(CanaryIntegrityError, match="single generator"):
        detection_rate({"alpha": ["H1"]}, cs, models=["alpha"], seeded_ids=[c.id for c in cs])


def test_p_hat_refuses_when_there_is_nothing_held_out():
    cs = [_c("C1", "a", "b", split=CALIBRATION)]
    with pytest.raises(CanaryIntegrityError, match="no held-out canaries"):
        detection_rate({"alpha": []}, cs, models=["alpha"], seeded_ids=[c.id for c in cs])


def test_p_hat_is_per_domain_when_asked():
    cs = [_c("D1", "a", "b", domain="dsp"), _c("D2", "c", "d", domain="dsp", gen="generated"),
          _c("B1", "e", "f", domain="bio"), _c("B2", "g", "h", domain="bio", gen="generated")]
    caught = {"alpha": ["D1", "D2", "B1"]}
    assert detection_rate(caught, cs, models=["alpha"], seeded_ids=[c.id for c in cs], domain="dsp") == {"alpha": 1.0}
    assert detection_rate(caught, cs, models=["alpha"], seeded_ids=[c.id for c in cs], domain="bio") == {"alpha": 0.5}


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


# --------------------------------------------------------------------------- #
# The in-repo guard, attacked rather than assumed                              #
# --------------------------------------------------------------------------- #
def _write_probe():
    from bench.canary_seeding import REPO_ROOT
    probe = REPO_ROOT / "_canary_guard_probe.json"
    probe.write_text(json.dumps({"canaries": []}), encoding="utf-8")
    return probe


def test_a_symlink_pointing_into_the_repo_is_refused(tmp_path):
    """The guard resolves before comparing, so a symlink cannot launder a path."""
    probe = _write_probe()
    try:
        link = tmp_path / "outside_looking.json"
        link.symlink_to(probe)
        with pytest.raises(CanaryIntegrityError, match="inside the repository"):
            load_catalogue(link)
    finally:
        probe.unlink()


def test_a_symlinked_directory_into_the_repo_is_refused(tmp_path):
    from bench.canary_seeding import REPO_ROOT
    probe = _write_probe()
    try:
        d = tmp_path / "innocent_dir"
        d.symlink_to(REPO_ROOT)
        with pytest.raises(CanaryIntegrityError, match="inside the repository"):
            load_catalogue(d / probe.name)
    finally:
        probe.unlink()


def test_dot_dot_traversal_back_into_the_repo_is_refused():
    """Built from OUTSIDE /private: on macOS /var is a symlink, so a traversal
    rooted in a /var temp dir lands in /private/Users and fails for the wrong
    reason -- it does not exist. That would have looked like the guard working."""
    import shutil, tempfile
    from bench.canary_seeding import REPO_ROOT
    probe = _write_probe()
    td = pathlib.Path(tempfile.mkdtemp(dir=str(pathlib.Path.home())))
    try:
        ups = [".."] * len(td.resolve().parts[1:])
        trav = td.joinpath(*ups).joinpath(*REPO_ROOT.parts[1:]) / probe.name
        assert trav.is_file(), "the traversal must actually reach the file, or this proves nothing"
        with pytest.raises(CanaryIntegrityError, match="inside the repository"):
            load_catalogue(trav)
    finally:
        shutil.rmtree(td, ignore_errors=True)
        probe.unlink()


def test_a_relative_path_resolved_against_the_repo_cwd_is_refused(monkeypatch):
    from bench.canary_seeding import REPO_ROOT
    probe = _write_probe()
    try:
        monkeypatch.chdir(REPO_ROOT)
        with pytest.raises(CanaryIntegrityError, match="inside the repository"):
            load_catalogue(probe.name)
    finally:
        probe.unlink()


def test_a_model_that_caught_nothing_scores_zero_rather_than_vanishing():
    """The silent-omission defect, found by attacking my own module.

    Deriving the result from the catch list alone dropped any reviewer that
    detected nothing -- the totally blind reviewer, which is the single result
    this instrument exists to surface.
    """
    cs = [_c("H1", "a", "b"), _c("H2", "c", "d", gen="generated")]
    r = detection_rate({"alpha": ["H1"]}, cs, models=["alpha", "beta"], seeded_ids=[c.id for c in cs])
    assert r == {"alpha": 0.5, "beta": 0.0}, "a reviewer that caught nothing went missing"


def test_p_hat_refuses_an_empty_roster():
    cs = [_c("H1", "a", "b"), _c("H2", "c", "d", gen="generated")]
    with pytest.raises(CanaryIntegrityError, match="no model roster"):
        detection_rate({"alpha": ["H1"]}, cs, models=[], seeded_ids=[c.id for c in cs])


# --------------------------------------------------------------------------- #
# Defects found by the independent build panel, 2026-08-28. Each is pinned      #
# with the attack the reviewer actually ran.                                    #
# --------------------------------------------------------------------------- #
def test_case_mangled_root_component_is_refused():
    """Path.resolve() does not case-normalise on macOS, and relative_to is a
    string comparison, so a path whose ROOT components differ in case resolved to
    "outside" and the catalogue was read.

    The two reviewers disagreed here and both were right about what they ran:
    mangling a component BELOW the root was already refused; mangling a component
    OF the root read the key. This pins the second.
    """
    from bench.canary_seeding import REPO_ROOT
    probe = _write_probe()
    try:
        variant = pathlib.Path(str(probe).replace("/Constraint_Engineering/",
                                                  "/CONSTRAINT_ENGINEERING/"))
        if not variant.exists():
            pytest.skip("filesystem is case-sensitive, so this attack does not apply")
        with pytest.raises(CanaryIntegrityError):
            load_catalogue(variant)
    finally:
        probe.unlink()


def test_a_hardlink_to_a_tracked_file_is_refused(tmp_path):
    """resolve() cannot see through a hardlink, so a link made outside a tracked
    tree reads the tracked bytes. Both reviewers demonstrated it."""
    import os
    probe = _write_probe()
    link = tmp_path / "innocent.json"
    try:
        os.link(probe, link)
        with pytest.raises(CanaryIntegrityError, match="hard link"):
            load_catalogue(link)
    finally:
        probe.unlink()


def test_the_guard_protects_any_worktree_not_just_this_modules_tree(tmp_path):
    """REPO_ROOT was parents[1] of THIS FILE, so a copy running in a throwaway
    worktree -- which is how panels are dispatched -- would read a catalogue in
    the canonical tracked tree. Containment is now decided by finding a .git."""
    from bench.canary_seeding import _in_a_git_worktree
    fake = tmp_path / "some_other_repo"
    (fake / ".git").mkdir(parents=True)
    (fake / "cat.json").write_text("{}", encoding="utf-8")
    assert _in_a_git_worktree(fake / "cat.json") == fake
    plain = tmp_path / "not_a_repo"
    plain.mkdir()
    assert _in_a_git_worktree(plain / "cat.json") is None


def test_an_id_in_both_splits_is_refused(tmp_path):
    """A calibration kill scored as held-out detection -- the exact Goodhart
    failure the split exists to prevent."""
    cat = tmp_path / "cat.json"
    cat.write_text(json.dumps({"canaries": [
        {"id": "X1", "domain": "d", "defect_class": "c", "generator": "g",
         "split": CALIBRATION, "find": "a", "replace": "b", "summary": "s"},
        {"id": "X1", "domain": "d", "defect_class": "c", "generator": "h",
         "split": HELD_OUT, "find": "c", "replace": "d", "summary": "s"}]}), encoding="utf-8")
    with pytest.raises(CanaryIntegrityError, match="duplicate canary id"):
        load_catalogue(cat)


@pytest.mark.parametrize("gen", ["", "   "])
def test_an_empty_generator_name_is_refused(gen):
    """An empty generator counted as a second generator and defeated the guard."""
    with pytest.raises(ValueError, match="generator is empty"):
        _c("K1", "a", "b", gen=gen)


def test_generators_differing_only_in_case_or_padding_are_one_generator():
    cs = [_c("H1", "a", "b", gen="gpt"), _c("H2", "c", "d", gen="GPT ")]
    with pytest.raises(CanaryIntegrityError, match="single generator"):
        detection_rate({"alpha": ["H1"]}, cs, models=["alpha"], seeded_ids=["H1", "H2"])


def test_legitimate_prose_containing_seeded_or_mutant_is_not_refused():
    """Confirmed false refusal that would have bitten the biology corpus: a clean
    document saying "a seeded random number generator" was rejected outright."""
    doc = ("Results used a seeded random number generator.\n"
           "The mutant strain grew faster than the wild type.\n"
           "The filter has unity gain in the passband.\n")
    seeded, _ = seed(doc, [_c("K1", "unity gain", "zero gain")])
    assert "seeded random number generator" in seeded


def test_a_tell_the_edit_introduces_is_still_refused():
    """The known-GOOD half of the pair above: introducing the word must still fail."""
    doc = "Results used a seeded random number generator.\nThe filter has unity gain.\n"
    with pytest.raises(CanaryIntegrityError, match="announces the exercise"):
        seed(doc, [_c("K1", "unity gain", "zero gain, a seeded mutant")])


def test_plural_tells_are_caught():
    with pytest.raises(CanaryIntegrityError, match="announces the exercise"):
        seed(DOC, [_c("K1", "unity gain", "zero gain  # canaries")])


def test_unseeded_canaries_cannot_deflate_the_score():
    """An unseeded canary is unkillable by construction. Counting it in k lowers
    every model's rate by an amount nobody can see."""
    cs = [_c("H1", "a", "b"), _c("H2", "c", "d", gen="generated"),
          _c("H3", "e", "f", gen="generated")]
    r = detection_rate({"alpha": ["H1", "H2"]}, cs, models=["alpha"], seeded_ids=["H1", "H2"])
    assert r == {"alpha": 1.0}, "the panel caught everything actually seeded"


def test_scoring_with_no_seeded_ids_is_refused():
    cs = [_c("H1", "a", "b"), _c("H2", "c", "d", gen="generated")]
    with pytest.raises(CanaryIntegrityError, match="no seeded ids"):
        detection_rate({"alpha": ["H1"]}, cs, models=["alpha"], seeded_ids=[])


def test_a_catch_for_an_unknown_id_is_refused():
    """Silently intersecting these away would hide id drift upstream."""
    cs = [_c("H1", "a", "b"), _c("H2", "c", "d", gen="generated")]
    with pytest.raises(CanaryIntegrityError, match="in no catalogue"):
        detection_rate({"alpha": ["H1", "GHOST"]}, cs, models=["alpha"],
                       seeded_ids=["H1", "H2"])


def test_seeding_a_target_under_version_control_is_refused():
    """The seeded document IS an answer key: git diff returns the planted set at
    precision 1.000, no key required (MANIFEST.md, measured 2026-07-29)."""
    with pytest.raises(CanaryIntegrityError, match="git work tree"):
        seed(DOC, [_c("K1", "unity gain", "zero gain")],
             target_path=REPO / "bench" / "canary_seeding.py")


def test_seeding_a_target_outside_version_control_is_allowed(tmp_path):
    t = tmp_path / "target.md"
    t.write_text(DOC, encoding="utf-8")
    seeded, man = seed(DOC, [_c("K1", "unity gain", "zero gain")], target_path=t)
    assert "zero gain" in seeded and man["canaries"][0]["id"] == "K1"
