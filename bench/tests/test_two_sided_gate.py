"""Two-sided convergence gate (founder ruling 2026-06-10). Convergence requires BOTH
sides of the same diminishing-returns coin: gamma_critical >= gamma_alt_threshold (the
decay curve has flattened) AND K consecutive zero-new-critical rounds (the strict
'insurance' endpoint). gamma is an ACTIVE convergence condition, NOT 'reported only'."""
import bench.reference_runner_v2 as rr


def test_both_sides_required():
    cfg = rr.RunnerConfig()  # gamma_alt_threshold=0.30, window=3
    z3 = [3, 1, 0, 0, 0]     # three consecutive zeros
    # BOTH sides met -> converge
    conv, _ = rr._check_gamma_alt_convergence(4, 0.5, z3, cfg, gamma_critical=0.607)
    assert conv, "gamma above threshold + 3 zeros must converge"
    # gamma below threshold (curve NOT flattened) -> gamma BLOCKS even with 3 zeros
    conv2, r2 = rr._check_gamma_alt_convergence(4, 0.5, z3, cfg, gamma_critical=0.20)
    assert not conv2 and "gamma_critical" in r2, "low gamma must block (gamma is active)"
    # count NOT met (no 3 zeros) -> blocks even with high gamma
    conv3, _ = rr._check_gamma_alt_convergence(4, 0.5, [3, 1, 1, 0, 0], cfg, gamma_critical=0.9)
    assert not conv3, "high gamma alone must not converge without the 3-zero count"


def test_recorded_live_run_converges_at_round_6():
    """The 9 June live run, replayed through the two-sided gate, converges at round 6 —
    identical to the count-only result, confirming the two sides naturally agree."""
    cfg = rr.RunnerConfig()
    loc = [10, 1, 5, 1, 0, 0, 0]
    gcrit = [0.0, 0.0, 0.59, 0.58, 0.571, 0.584, 0.607]
    first = next((r for r in range(7) if rr._check_gamma_alt_convergence(
        r, 0.5, loc[:r + 1], cfg, gamma_critical=gcrit[r])[0]), None)
    assert first == 6
