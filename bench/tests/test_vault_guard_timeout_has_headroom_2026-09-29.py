"""The exam-run vault guard's timeout, pinned to the scan's MEASURED cost.

THE DEFECT THIS EXISTS TO PREVENT RECURRING, and it is a constant that drifted out
from under the thing it guards.

`reference_runner_v3.run_experiment` refuses to start an exam run unless
`bench/vault_keys.sh status` reports `VAULTED`. That check ran with a bare
`timeout=120`, set on 2026-09-01 (ce08914) when the scan cost about 2.15 s --
55.8x headroom. On 2026-09-08 (2230744) the stray scan deliberately became an
UNBOUNDED walk of `$HOME`, because a depth ceiling had made it blind to the
repository itself, which is where the Exp 48 leak came from. The change was right
and `vault_keys.sh` records its own cost measurement for it: 2.15 s to about 10 s.

NOTHING CONNECTED THE TWO FILES. The margin fell from 55.8x to 12x and nobody
looked again. On 2026-09-29 the simulated shakedown refused to start TWICE, with
the keys correctly vaulted throughout, because inside a live run the scan competes
with the launcher copying ~20,800 files and 2 of 3 attempts exceeded 120 s. A
`sitecustomize` probe -- which modified nothing in the repository -- timed the
guard's own subprocess in a live run at 30.77 s, about 2.3x the idle mean.

SO THIS FILE IS THE MISSING CONNECTION. It EXECUTES the scan, times it, and fails
if `VAULT_STATUS_TIMEOUT_S` has stopped leaving real margin. A future change that
makes the scan more expensive -- which may well be the right thing to do again --
now breaks a test instead of silently eating the guard's headroom.

WHAT IT DELIBERATELY DOES NOT DO. It does not assert the scan is FAST. Cost is the
price of the scan not being blind, and narrowing it is the failure it was rewritten
to end. It asserts only that the cap and the cost have not drifted apart.

It also never echoes the scan's output: on a machine with stray key material that
output names paths, and a test log is not the place for them.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "bench" / "vault_keys.sh"

#: The margin required between the cap and the scan's measured idle cost. Chosen
#: from the in-run observation rather than by feel: the scan ran about 2.3x its
#: idle mean inside a live run, and 2 of 3 in-run attempts exceeded a cap that
#: left 9.1x idle headroom. 20x idle therefore keeps real room above the worst
#: in-run figure actually seen, while still failing if the scan's cost doubles.
REQUIRED_IDLE_HEADROOM = 20.0

#: The worst in-run duration measured, 2026-09-29, by the sitecustomize probe.
OBSERVED_IN_RUN_S = 30.77


@pytest.fixture(scope="module")
def timeout_const():
    sys.path.insert(0, str(REPO))
    from bench.reference_runner_v3 import VAULT_STATUS_TIMEOUT_S
    return VAULT_STATUS_TIMEOUT_S


@pytest.fixture(scope="module")
def measured_idle_seconds():
    """Execute the real scan. Skips rather than fails where it cannot run."""
    if not SCRIPT.is_file():
        pytest.skip("vault_keys.sh absent")
    conf = Path(os.environ.get("CDSFL_SCORING_CONF",
                               Path.home() / ".config" / "cdsfl" / "scoring.env"))
    if not conf.is_file():
        pytest.skip("no scoring config on this machine; the scan cannot be timed here")
    best = None
    for _ in range(2):
        t0 = time.time()
        try:
            subprocess.run(["bash", str(SCRIPT), "status"],
                           capture_output=True, text=True, timeout=900)
        except subprocess.TimeoutExpired:
            pytest.fail(
                "vault_keys.sh status did not finish in 900s. That is far beyond "
                "any measured cost and is a real fault in the scan, not a margin "
                "problem -- do not 'fix' it by raising VAULT_STATUS_TIMEOUT_S.")
        dt = time.time() - t0
        best = dt if best is None else min(best, dt)
    return best


class TestTheCapAndTheCostHaveNotDriftedApart:

    def test_the_guard_uses_the_named_constant_not_a_literal(self):
        """A literal here is how the drift happened; it must stay named."""
        src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        assert "timeout=VAULT_STATUS_TIMEOUT_S" in src
        assert 'subprocess.run(["bash", str(_vault), "status"],\n' in src
        # the old bare literal must not come back on this call
        assert '"status"],\n                                     capture_output=True, text=True, timeout=120)' not in src

    def test_the_cap_leaves_real_margin_over_the_measured_cost(
            self, timeout_const, measured_idle_seconds):
        headroom = timeout_const / measured_idle_seconds
        assert headroom >= REQUIRED_IDLE_HEADROOM, (
            f"vault_keys.sh status now costs {measured_idle_seconds:.1f}s and "
            f"VAULT_STATUS_TIMEOUT_S is {timeout_const}s -- only {headroom:.1f}x "
            f"headroom, below the required {REQUIRED_IDLE_HEADROOM}x. The scan got "
            f"more expensive. Raise the constant deliberately and record the new "
            f"measurement beside it; do NOT narrow the scan to fit the cap.")

    def test_the_cap_clears_the_worst_in_run_duration_ever_measured(self, timeout_const):
        assert timeout_const >= OBSERVED_IN_RUN_S * 5, (
            f"the cap {timeout_const}s leaves under 5x the worst in-run duration "
            f"measured ({OBSERVED_IN_RUN_S}s). In-run cost runs well above idle "
            f"because the launcher copies ~20,800 files at the same moment.")

    def test_the_old_cap_would_now_fail_this_check(self, measured_idle_seconds):
        """ANTI-VACUITY: the check must reject the value that actually broke."""
        assert 120 / measured_idle_seconds < REQUIRED_IDLE_HEADROOM, (
            "the scan has become cheap enough that the original 120s cap would "
            "pass; this guard can no longer detect the drift it was written for")


class TestTheControlItselfIsUnchanged:
    """Raising a timeout must not have loosened what the guard actually requires."""

    def test_it_still_demands_VAULTED_and_still_fails_closed(self):
        src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        assert '_out.lstrip().startswith("VAULTED")' in src, (
            "the guard no longer requires the scan to report VAULTED")
        assert "REFUSING TO START: a plaintext scoring key is on disk" in src

    def test_a_timeout_still_refuses_rather_than_proceeding(self):
        src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        i = src.find("cannot verify the scoring keys are vaulted")
        assert i != -1
        window = src[max(0, i - 400):i]
        assert "raise RuntimeError(" in window, (
            "a failed vault check must still RAISE; failing open here would "
            "reinstate the exposure the guard exists to prevent")

    def test_no_bypass_was_introduced(self):
        src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        for bypass in ("SKIP_VAULT", "CDSFL_SKIP_VAULT", "VAULT_BYPASS", "IGNORE_VAULT"):
            assert bypass not in src, f"a bypass named {bypass} appeared"
