"""Commissioning tests for two repairs made on 2026-08-30.

A. THE OVERLAY LEAKED THE REAL `.git`.
   `_build_discrimination_overlay` symlink-mirrors the repo root, and `.git` was
   mirrored with everything else. Measured before the fix: `git -C <overlay> log`
   and `git -C <overlay> diff` both ran and returned real repository history.
   For any overlay whose leaf differs from the tracked file -- which is EVERY
   discrimination-control and fix-efficacy overlay, and would be every canary
   overlay -- that hands back the mutation at precision 1.000 with no key. It is
   the leak `canary_seeding.seed` refuses a tracked target to prevent, arriving
   through a path that guard cannot see. It also made every overlay LOOK like a
   git work tree, so `seed()` refused the one place seeding is legitimate.

B. THE FIX-EFFICACY PROBE WAS BUILT AND NEVER CALLED.
   `bench/fix_efficacy.py` (commit 775518d, 14 passing tests) answers the one
   question the live loop never asks: does a fix cure the defect its OWN
   falsifier demonstrates? `reference_runner_v3` contained zero references to it.
   These tests commission the wiring and pin the property that makes the wiring
   safe: it is CONTRIBUTORY. It renders a line and records a reading. It must
   never be able to change a status or block convergence.
"""
import pathlib
import shutil
import subprocess
import sys
import textwrap

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

import reference_runner_v3 as rr                                   # noqa: E402
from bench.canary_seeding import (                                 # noqa: E402
    Canary, HELD_OUT, CanaryIntegrityError, seed,
)
from bench.fix_efficacy import (                                   # noqa: E402
    FEEDBACK_LINE, FIX_CURES, FIX_INEFFECTIVE, NOT_INTERCEPTED,
)

TARGET_REL = "bench/toy_target.py"


def _overlay(tmp_path, content="X = 1\n"):
    (tmp_path / "bench").mkdir(parents=True, exist_ok=True)
    (tmp_path / TARGET_REL).write_text("X = 0\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    return rr._build_discrimination_overlay(tmp_path, TARGET_REL, content)


# ── A. the overlay must not carry .git ──────────────────────────────────────
def test_overlay_does_not_mirror_dot_git(tmp_path):
    ov = _overlay(tmp_path)
    try:
        assert not (ov / ".git").exists(), (
            "the overlay carries .git, so `git show HEAD:<target>` returns the "
            "pristine text and `git diff` returns the planted mutation")
        r = subprocess.run(["git", "-C", str(ov), "log", "--oneline", "-1"],
                           capture_output=True, text=True)
        assert r.returncode != 0, "git still resolves a repository from the overlay"
    finally:
        shutil.rmtree(ov, ignore_errors=True)


def test_overlay_is_still_a_usable_mirror(tmp_path):
    """The fix must not break what the overlay is FOR. Everything else is still
    linked, the leaf is a real file holding the substituted content, and the
    real tree is untouched."""
    ov = _overlay(tmp_path, content="X = 99\n")
    try:
        assert (ov / TARGET_REL).read_text() == "X = 99\n"
        assert not (ov / TARGET_REL).is_symlink()
        assert (tmp_path / TARGET_REL).read_text() == "X = 0\n"
    finally:
        shutil.rmtree(ov, ignore_errors=True)


def test_a_canary_can_now_be_seeded_on_an_overlay_but_not_on_the_tree(tmp_path):
    """The two halves of the same rule. Seeding the tracked article is refused
    (its history is the answer key); seeding the overlay is allowed, and after
    the fix the overlay no longer inherits that history."""
    can = Canary(id="K1", domain="code", defect_class="sign", generator="genA",
                 split=HELD_OUT, find="X = 0", replace="X = -1", summary="sign flip")
    ov = _overlay(tmp_path, content="X = 0\n")
    try:
        try:
            seed("X = 0\n", [can], target_path=tmp_path / TARGET_REL)
            raise AssertionError("seeding the tracked article was NOT refused")
        except CanaryIntegrityError:
            pass
        out, manifest = seed((ov / TARGET_REL).read_text(), [can],
                             target_path=ov / TARGET_REL)
        assert out == "X = -1\n"
        assert [c["id"] for c in manifest["canaries"]] == ["K1"]
    finally:
        shutil.rmtree(ov, ignore_errors=True)


# ── B. the fix-efficacy wiring ──────────────────────────────────────────────
def test_the_runner_actually_reaches_the_probe():
    """The whole defect was that it did not. If this wiring disappears again the
    probe is dead code with passing tests, which is how it spent its first day.

    REWRITTEN 2026-09-01 on integration. As drafted, this asserted module-level
    aliases `rr.FE_FIX_INEFFECTIVE` and `rr.FE_FEEDBACK_LINE`, which belonged to
    the reviewer's own draft of the wiring. The implementation that was adopted
    instead consults `fix_efficacy_decision()` and imports the probe lazily at
    the call site, so neither alias exists and neither ever did in this tree.

    The assertion is therefore restated against the property rather than the
    reviewer's chosen names: the runner must reach the probe, and the model must
    be told, in those words, that its fix does not cure its own falsifier. That
    the sentence reaches the model is separately pinned by
    `test_an_ineffective_fix_reaches_the_model` below, which passes.
    """
    body = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
    assert "fix_efficacy_decision(" in body, "the decision helper is not consulted"
    assert "from fix_efficacy import probe" in body, "the probe is never imported"
    assert FIX_INEFFECTIVE in body, (
        "the runner does not name the ineffective-fix outcome the probe returns")
    assert "DOES NOT CURE YOUR OWN FALSIFIER" in FEEDBACK_LINE
    assert isinstance(rr.FIX_EFFICACY_PER_ROUND_LIMIT, int)
    assert rr.FIX_EFFICACY_PER_ROUND_LIMIT > 0


def test_an_ineffective_fix_reaches_the_model():
    lines = rr._rejection_lines({"fix_efficacy": {"outcome": FIX_INEFFECTIVE,
                                                  "detail": "", "round": 3}})
    assert any("DOES NOT CURE YOUR OWN FALSIFIER" in ln for ln in lines)


def test_an_effective_fix_says_nothing():
    """A model told nothing is a model with no reason to rewrite a sound fix."""
    assert rr._rejection_lines({"fix_efficacy": {"outcome": FIX_CURES,
                                                 "detail": "", "round": 3}}) == []


def test_the_instrument_failing_to_look_is_never_reported_as_a_bad_fix():
    """NOT_INTERCEPTED means the falsifier never reads the target, so the probe
    measured nothing. Telling the model its fix is bad on that basis is the
    'cannot verify becomes verified' inversion, pointed the other way."""
    for outcome in (NOT_INTERCEPTED, "INDETERMINATE_NO_BASELINE",
                    "INDETERMINATE_NO_APPLICABLE_FIX", "INDETERMINATE_OTHER",
                    "INDETERMINATE_PROBE_ERROR"):
        assert rr._rejection_lines({"fix_efficacy": {"outcome": outcome,
                                                     "detail": "x", "round": 1}}) == [], outcome


def test_the_probe_is_contributory_and_cannot_gate_anything():
    """Founder ruling 2026-08-29, applied to rho in commit aff3ab7 and inherited
    here: an instrument that measures the exhaustion of a search must not be
    able to refuse the convergence it is measuring. The probe's key must appear
    in no gate. Read from source, so the test survives refactoring of the gates."""
    import inspect
    for fn in (rr._evaluate_gate_conditions, rr._check_gamma_alt_convergence):
        src = inspect.getsource(fn)
        assert "fix_efficacy" not in src, (
            f"{fn.__name__} reads the fix-efficacy result; it is contributory, "
            f"never a veto")
