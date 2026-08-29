"""Does a finding's proposed fix actually cure the defect its OWN falsifier demonstrates?

WHY THIS EXISTS
===============
Founder question, 2026-08-29: *"is there genuinely nothing that can be utilised to
detect when a fix is genuinely 'inadmissible', and when such a condition is
detected, feed it back to the model/s and require them to build a better fix? We
should already have much of this machinery. Why isn't it being used?"*

The founder is right that the machinery exists. What runs today is:

  * `bugzilla_loop.attempt_close` applies a proposed fix to a SANDBOX COPY and
    verifies it -- live, in flight, called from `_update_finding_statuses`.
  * but `run_verification` runs ruff, mypy, bandit and the experiment's GENERIC
    `test_cmd`. It asks "did this fix break anything". It never asks "does this
    fix cure the defect THIS finding claims".

That second question is the `FIX_INEFFECTIVE` condition, and **16 of the 48
undecided similarity pairs are exactly it**. It is invisible to the live loop.

THE OBSTACLE, AND WHY THE OBVIOUS FIX FAILS
===========================================
A sandbox copy at a different path does not work. Measured on exp44: **57 of 70
falsifiers reach their target by IMPORTING the module**, not by reading a path.
Those imports resolve to the ORIGINAL module, so the fix is invisible and every
probe would report "ineffective" -- wrong, and wrong in the confident direction.

`scripts/adjudicate_by_repair.py` sidesteps this by writing the patched text to
the LIVE target and restoring in a `finally`. That is fine for an offline batch
on a checkout and unacceptable in flight: the runner hashes the target every
round and raises TARGET INTEGRITY WARNING on change, and a kill between write and
restore corrupts the article under review.

WHAT THIS MODULE DOES INSTEAD: REUSE, NOT INVENTION
===================================================
The discrimination control already solved this exact problem on 2026-08-22 and
the solution was never reused. `_build_discrimination_overlay` builds a throwaway
repo root, symlink-mirrored, identical to the real one except for ONE file, so
imports resolve through it and the real tree is never touched. `_retarget_falsifier`
handles the minority that use absolute paths.

Critically, the control does not TRUST the overlay -- it MEASURES that the
overlay is load-bearing, with a tripwire, and yields a distinct INDETERMINATE
outcome rather than a verdict when it is not. This module inherits that property
verbatim, because the failure it protects against is the one measured above: a
falsifier that never reads the target would otherwise mint a false verdict
against a sound fix.

WHAT IT DELIBERATELY DOES NOT DO
================================
It decides nothing. It cannot close, open, merge or refute a finding. It returns
a reading. Whether that reading should feed the model-facing feedback channel, and
whether it should ever gate anything, is a founder ruling and is not taken here.
"""
from __future__ import annotations

import dataclasses
import pathlib
import shutil
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

#: Outcomes. Deliberately NOT collapsible to a boolean -- "the fix did not cure
#: it" and "the instrument could not look" must never be the same value, which
#: is the distinction the whole project keeps having to relearn.
FIX_CURES = "FIX_CURES_ITS_OWN_FALSIFIER"
FIX_INEFFECTIVE = "FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER"
NOT_INTERCEPTED = "INDETERMINATE_NOT_INTERCEPTED"   # falsifier never read the target
NO_BASELINE = "INDETERMINATE_NO_BASELINE"           # falsifier does not reproduce
NO_FIX = "INDETERMINATE_NO_APPLICABLE_FIX"          # fix did not apply
INDETERMINATE = "INDETERMINATE_OTHER"


@dataclasses.dataclass(frozen=True)
class FixEfficacyResult:
    outcome: str
    detail: str = ""

    @property
    def is_a_verdict(self) -> bool:
        """Only two outcomes are verdicts. Everything else is equipment."""
        return self.outcome in (FIX_CURES, FIX_INEFFECTIVE)


def _overlay_verdict(target_rel: str, content: str, falsifier_code: str,
                     repo_root: pathlib.Path, timeout: int) -> tuple[str, int]:
    """Run `falsifier_code` against an overlay whose target holds `content`.

    Returns (verdict, path_substitutions). The second value is how many absolute
    repo paths `_retarget_falsifier` rewrote, and it is load-bearing: see
    `_is_intercepted`.
    """
    from reference_runner_v2 import _build_discrimination_overlay, _retarget_falsifier
    from falsifier_verify import reverify_falsifier

    overlay = _build_discrimination_overlay(repo_root, target_rel, content)
    try:
        code, n = _retarget_falsifier(falsifier_code, repo_root, overlay)
        return reverify_falsifier(code, repo_root=str(overlay), timeout=timeout), n
    finally:
        shutil.rmtree(overlay, ignore_errors=True)


def probe(finding: dict, target_rel: str, *,
          repo_root: pathlib.Path | None = None,
          timeout: int = 20) -> FixEfficacyResult:
    """Three passes, in the order that makes a wrong answer impossible to reach.

    1. TRIPWIRE  -- the target is replaced by a file that raises on import. If
       the falsifier does not trip it, the falsifier never reads the target, so
       nothing this probe measures afterwards would mean anything. NOT_INTERCEPTED.
    2. BASELINE  -- the ORIGINAL target, through the same apparatus. The
       falsifier must still demonstrate the defect. If it does not, the probe has
       no starting point to improve on. NO_BASELINE.
    3. PATCHED   -- the fix applied. Still demonstrating means the fix does not
       cure it; quiet means it does.

    The order matters: 1 and 2 are the two ways a sound fix could be falsely
    condemned, and both are checked BEFORE any verdict can be produced.
    """
    from reference_runner_v2 import DISC_TRIPWIRE_BODY, DISC_TRIPWIRE_TOKEN
    from endocrine import _apply_fix_to_source

    root = repo_root or REPO_ROOT
    code = (finding.get("falsifier_code") or "").strip()
    fix = finding.get("proposed_fix") or ""
    if not code:
        return FixEfficacyResult(INDETERMINATE, "no falsifier attached")
    original = (root / target_rel).read_text(encoding="utf-8")

    # 1 -- is the overlay load-bearing for THIS falsifier?
    #
    # There are TWO ways a falsifier reaches its target and they need DIFFERENT
    # interception evidence. This was found by this module's own test, which
    # failed on the first version: the tripwire is an `import` that raises, so a
    # falsifier that READS THE FILE AS TEXT sees only the raising source, finds
    # nothing it is looking for, and exits clean. The first version read that as
    # "never reads the target" and would have refused a verdict on every
    # path-reading falsifier in the corpus.
    #
    #   import-based  -> the tripwire fires, and its token appears in the verdict
    #   path-based    -> `_retarget_falsifier` rewrote at least one absolute path
    #
    # Either is sufficient. Neither present means the falsifier reaches its
    # target by no route this apparatus controls, and no verdict is available.
    tw, tw_subs = _overlay_verdict(target_rel, DISC_TRIPWIRE_BODY, code, root, timeout)
    intercepted_by_import = DISC_TRIPWIRE_TOKEN in tw or tw == "ERROR"
    if not (intercepted_by_import or tw_subs > 0):
        return FixEfficacyResult(
            NOT_INTERCEPTED,
            f"falsifier returned {tw} against a target that only raises, and no "
            f"absolute path was rewritten, so it reaches its target by no route "
            f"this apparatus controls; no verdict is available")

    # 2 -- does the falsifier still reproduce, through this same apparatus?
    base, _ = _overlay_verdict(target_rel, original, code, root, timeout)
    if base != "CONFIRMED":
        return FixEfficacyResult(
            NO_BASELINE,
            f"falsifier returned {base} on the UNMODIFIED target, so it does not "
            f"demonstrate the defect it accuses; there is nothing for a fix to cure")

    # 3 -- apply the fix and ask again.
    patched = _apply_fix_to_source(original, fix)
    if not patched or patched == original:
        return FixEfficacyResult(NO_FIX, "the proposed fix did not apply to the target")
    after, _ = _overlay_verdict(target_rel, patched, code, root, timeout)
    if after == "CONFIRMED":
        return FixEfficacyResult(
            FIX_INEFFECTIVE,
            "the fix applies cleanly and the finding's own falsifier still "
            "demonstrates the defect afterwards")
    if after == "REFUTED":
        return FixEfficacyResult(
            FIX_CURES, "the finding's own falsifier goes quiet once the fix is applied")
    return FixEfficacyResult(INDETERMINATE, f"falsifier returned {after} on the patched target")


#: The model-facing line, for the feedback channel that already exists in
#: `build_feedback_sections`. NOT wired here -- wiring is a founder ruling.
FEEDBACK_LINE = (
    "YOUR FIX DOES NOT CURE YOUR OWN FALSIFIER. It was applied to a disposable "
    "copy of the target and your own test was re-run against it; the test still "
    "demonstrates the defect. Either the fix is incomplete, or the test does not "
    "test what the finding claims. Send a fix that makes your own test go quiet, "
    "or a test that actually exercises the defect you are describing."
)
