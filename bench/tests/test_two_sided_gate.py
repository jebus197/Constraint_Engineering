"""Two-sided convergence gate (founder ruling 2026-06-10). Convergence requires BOTH
sides of the same diminishing-returns coin: gamma_critical >= gamma_alt_threshold (the
decay curve has flattened) AND K consecutive zero-new-critical rounds (the strict
'insurance' endpoint). gamma is an ACTIVE convergence condition, NOT 'reported only'."""
import bench.reference_runner_v3 as rr


def test_both_sides_required():
    """Each arm must be able to block on its own, at whatever quiet run is set.

    THE SERIES ARE DERIVED FROM THE CONFIGURED QUIET RUN, 2026-10-17. They were
    literals built for a quiet run of 3 -- `[3, 1, 0, 0, 0]` -- and his ruling of
    2026-10-08 raised it to 7, so the "both sides met" case stopped meeting the
    count side and the test failed on the arm it was not testing. The claim here
    is that BOTH arms are active, which is a property of the gate rather than of
    the number 3.
    """
    cfg = rr.RunnerConfig()
    K = cfg.gamma_alt_consecutive_zero_crit
    full = [3, 1] + [0] * K            # the count side MET
    short = [3, 1] + [0] * (K - 1) + [1, 0]   # the count side NOT met
    r_idx = len(full) - 1

    # BOTH sides met -> converge
    conv, _ = rr._check_gamma_alt_convergence(r_idx, 0.5, full, cfg,
                                              gamma_critical=0.607)
    assert conv, f"gamma above threshold + {K} zeros must converge"

    # gamma below threshold (curve NOT flattened) -> gamma BLOCKS even when
    # the count side is satisfied
    conv2, r2 = rr._check_gamma_alt_convergence(r_idx, 0.5, full, cfg,
                                                gamma_critical=0.20)
    assert not conv2 and "gamma_critical" in r2, (
        "low gamma must block, which is what makes gamma an active condition "
        "rather than a report")

    # count NOT met -> blocks even with a high gamma
    conv3, _ = rr._check_gamma_alt_convergence(len(short) - 1, 0.5, short, cfg,
                                               gamma_critical=0.9)
    assert not conv3, (
        f"high gamma alone must not converge without {K} consecutive "
        f"zero-critical rounds")


def test_the_recorded_live_run_replays_under_both_quiet_runs():
    """The 9 June live run, replayed, and what the raised quiet run does to it.

    IT ASSERTED `first == 6`, WHICH WAS TRUE UNDER A QUIET RUN OF 3 and went red
    when his ruling of 2026-10-08 raised it to 7. The series is a RECORDED run,
    so lengthening it to make the test green would be falsifying the record. What
    changed is the gate, and the honest test records both readings.

    THE SERIES HAS 3 TRAILING ZEROS. Under a quiet run of 3 it converges at round
    6, which is the historical result and is reproduced here. Under 7 it does NOT
    converge within its 7 recorded rounds at all -- the run would have kept
    going. That is exactly the cost his ruling buys: the measured false-quiet rate
    at 3 consecutive quiet rounds was 0.126374 against a 0.05 target, and 7 is the
    smallest window with zero premature closes observed in the archive.
    """
    loc = [10, 1, 5, 1, 0, 0, 0]
    gcrit = [0.0, 0.0, 0.59, 0.58, 0.571, 0.584, 0.607]

    def first_converge(k):
        cfg = rr.RunnerConfig()
        cfg.gamma_alt_consecutive_zero_crit = k
        return next((r for r in range(len(loc))
                     if rr._check_gamma_alt_convergence(
                         r, 0.5, loc[:r + 1], cfg, gamma_critical=gcrit[r])[0]),
                    None)

    # 1. THE HISTORICAL READING, reproduced rather than taken on trust.
    assert first_converge(3) == 6, (
        "under the quiet run of 3 that was configured when this run was recorded, "
        "it converged at round 6; if that no longer reproduces, something other "
        "than the quiet run has changed")

    # 2. THE READING UNDER THE CONFIGURED QUIET RUN, derived from the series.
    cfg = rr.RunnerConfig()
    K = cfg.gamma_alt_consecutive_zero_crit
    first_zero = loc.index(0)
    needed = first_zero + K - 1
    got = first_converge(K)
    if needed < len(loc):
        assert got == needed, (
            f"with a quiet run of {K} and zeros from round {first_zero}, the gate "
            f"should fire at round {needed}; got {got}")
    else:
        assert got is None, (
            f"a quiet run of {K} needs {needed + 1} rounds and this recorded run "
            f"has {len(loc)}, so it must NOT converge; got round {got}")
