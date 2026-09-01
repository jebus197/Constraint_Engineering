"""ImmuneMemory EVALUATION: is what it learned worth switching on?

Companion to ``test_immune_memory_consumption.py``, which proves the
consumption *wiring* works. This suite asks the different question the founder
posed — what is actually in the recorded memory, how thin is the evidence, and
would enabling ``immune_memory_consume_rk0`` have moved anything — and pins
every number the answer rests on, so the answer goes red rather than stale.

WHY EACH ASSERTION IS HERE, NOT JUST WHAT IT CHECKS
---------------------------------------------------

1. PROVENANCE. ``bench/state/immune_memory.json`` carried counts and no
   statement of where they came from. They reproduce exactly by replaying the
   three run reports that wrote them (Exp 47, 48, 49) — which worked only
   because those reports survived on disk. The replay is asserted so the
   file's origin stays a checked fact rather than a remembered one.

2. THE EVIDENCE IS THIN AND THE THINNESS IS THE POINT. Two of seven flaw
   classes rest on a SINGLE observation, and one of those single observations
   is the only class whose prior pulls R_k(0) downward — i.e. the only class
   where memory could ever bind. A Beta-Binomial posterior on one observation
   is not knowledge, and the test says so in numbers.

3. THE COUNTERFACTUAL IS A BOUND, NOT A TALLY. Across every archived run with
   an S* decision on record — 1160 decisions, 19 runs — replaying under
   today's memory flips nothing. That could be luck. It is not: at ρ = 0.2 the
   largest S* the blended prior can produce for ANY π_mem is 4/19 ≈ 0.2105,
   and the weakest fix ever scored is 0.740. The margin is asserted, so the
   test goes red the moment either side moves — a genuinely weak fix landing
   in the archive, or ρ being raised — which are exactly the two conditions
   under which this evaluation's conclusion stops holding.

4. THE DRIFT DETECTOR HAS NEVER FIRED BECAUSE IT HAS NEVER RUN. ``update_drift``
   has no caller outside tests. Replayed over the three recorded runs it would
   not have fired either. And it cannot fire upward in any realistic horizon:
   the maximum positive residual is 1 − π_mem, so at π_mem = 0.97 the CUSUM
   needs 72 consecutive perfect-confirmation experiments to reach a threshold
   of 2.0, while the downward direction needs 3. The detector gets quieter
   precisely as the memory gets more committed — a self-sealing property, and
   the shape of failure this project exists to catch. The asymmetry is derived
   here rather than asserted from memory of it.

5. THE INTEGRITY GUARDS ADDED 2026-08-12 to ``bench/dm/_memory.py``: duplicate
   ingestion, corrupt counts on load, and a null source hash that used to read
   as a match.

A FINDING THIS SUITE DOES NOT ASSERT ON, because the fix belongs to whoever
holds ``reference_runner_v3.py``: ``_rejection_lines`` tests each entry of
``gate_details`` for ``is False``/``== 0``, but those entries are ``str`` (110
archived cases) or ``dict`` (9) — never a bare falsy scalar. The "name the
failed gate" branch is therefore dead, and all 119 archived rejections produce
one identical sentence, "hard gate returned 0". On the S*-threshold rejection
path that consumption would newly make reachable, that sentence is not merely
uninformative but false: the fix reached the threshold check precisely BECAUSE
every hard gate returned 1 (verified below over all 1160 admissible results).
The panel would be told a gate failed when the memory-derived threshold, not a
gate, declined the fix. Asserting the current wrong string here would turn a
correct repair into a red test, so this suite verifies only the stable premise
— that no archived admissible result has a falsy gate entry — and leaves the
message itself to the runner's owner.

Run with:
    cd ~/Developer_Projects/Constraint_Engineering
    python3 -m pytest bench/tests/test_immune_memory_evaluation.py -v
"""

from __future__ import annotations

import ast
import copy
import glob
import json
import logging
import math
import os
import sys

import pytest

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from bench.dm._memory import (  # noqa: E402
    ImmuneMemory,
    MemoryIntegrityError,
)
from bench.reference_runner_v3 import (  # noqa: E402
    RK0_PI_BASE,
    check_sk_threshold,
)

# The runner defaults every archived run used: `model_params` is populated
# nowhere in the repository, so these are the values that actually decided
# every S* on record. Asserted in `test_archive_used_the_runner_defaults`.
NU_B, NU_F, Q = 0.05, 0.20, 0.5
RHO = 0.2  # RunnerConfig.immune_memory_rho default

_STATE = os.path.join(_project_root, "bench", "state", "immune_memory.json")
_LOGS = os.path.join(_project_root, "bench", "logs")

# The three runs that wrote the memory on disk, in the order they ran.
_RECORDING_RUNS = [
    "exp47_divergence_locationkey_live",
    "exp48_chemistry_exam_live",
    "exp49_engineering_exam_live",
]
_CONFIRMED_STATUSES = {"CONFIRMED", "CLOSED"}  # runner _CONF, line ~9479
_REJECTED_STATUS = "REFUTED"


def _memory_on_disk() -> ImmuneMemory:
    if not os.path.exists(_STATE):
        pytest.skip("no recorded immune memory on disk")
    return ImmuneMemory.load(_STATE)


def _report_for(run_prefix: str) -> dict:
    hits = sorted(glob.glob(os.path.join(_LOGS, run_prefix + "_*", "*_report.json")))
    if not hits:
        pytest.skip(f"archival log for {run_prefix} not present")
    with open(hits[0]) as fh:
        return json.load(fh)


def _flaw_counts_from(report: dict) -> dict:
    """Reproduce the runner's own tallying block (reference_runner_v3 ~9478)."""
    counts: dict = {}
    for entry in report["registry"]["entries"].values():
        cell = counts.setdefault(int(entry.get("flaw_class") or 0), [0, 0])
        if entry["status"] in _CONFIRMED_STATUSES:
            cell[0] += 1
        elif entry["status"] == _REJECTED_STATUS:
            cell[1] += 1
    return {k: (v[0], v[1]) for k, v in counts.items()}


_DECISIONS_CACHE: list | None = None


def _all_archived_decisions() -> list:
    """Every S* decision on record, as (run, cid, flaw_class, result).

    The per-round ``sk_pipeline.results`` block is the decision record; the
    final registry keeps only each finding's last evaluation.
    """
    global _DECISIONS_CACHE
    if _DECISIONS_CACHE is not None:
        return _DECISIONS_CACHE
    out = []
    for path in sorted(glob.glob(os.path.join(_LOGS, "exp*", "*_report.json"))):
        try:
            with open(path) as fh:
                report = json.load(fh)
        except (json.JSONDecodeError, OSError):
            continue
        rounds = report.get("rounds")
        if not isinstance(rounds, list):
            continue
        registry = (report.get("registry") or {}).get("entries") or {}
        run = os.path.basename(os.path.dirname(path))
        for rnd in rounds:
            if not isinstance(rnd, dict):
                continue
            pipeline = rnd.get("sk_pipeline")
            if not isinstance(pipeline, dict):
                continue
            for cid, res in (pipeline.get("results") or {}).items():
                if isinstance(res, dict) and "s_star" in res:
                    fc = int((registry.get(cid) or {}).get("flaw_class") or 0)
                    out.append((run, cid, fc, res))
    _DECISIONS_CACHE = out
    return out


# ─────────────────────────────────────────────────────────────────────────────
# 1. WHAT IS ACTUALLY IN THE MEMORY
# ─────────────────────────────────────────────────────────────────────────────

class TestWhatTheMemoryHolds:

    def test_disk_memory_reproduces_from_the_three_run_reports(self):
        """Provenance by replay. The file names its sources only as of
        2026-08-12; for everything written before that, this replay IS the
        provenance record."""
        replay = ImmuneMemory()
        for run in _RECORDING_RUNS:
            replay.record_experiment(run, _flaw_counts_from(_report_for(run)))

        disk = _memory_on_disk()
        assert disk._experiment_count == 3, (
            f"memory records {disk._experiment_count} experiments; this suite "
            f"describes the 3-run state written by {_RECORDING_RUNS}")
        assert set(replay._records) == set(disk._records), (
            f"flaw classes differ: replay {sorted(replay._records)} vs disk "
            f"{sorted(disk._records)}")
        for fc, rec in disk._records.items():
            ref = replay._records[fc]
            assert rec.confirmed == pytest.approx(ref.confirmed, abs=1e-9), fc
            assert rec.rejected == pytest.approx(ref.rejected, abs=1e-9), fc
            assert rec.experiments_seen == ref.experiments_seen, fc

    def test_the_evidence_base_is_thin_and_here_is_how_thin(self):
        """Raw (undecayed) observation counts per class, straight from the
        source reports. Five of seven classes rest on six observations or
        fewer; two rest on one."""
        raw: dict = {}
        for run in _RECORDING_RUNS:
            for fc, (conf, rej) in _flaw_counts_from(_report_for(run)).items():
                cell = raw.setdefault(fc, [0, 0])
                cell[0] += conf
                cell[1] += rej

        totals = {fc: c + r for fc, (c, r) in raw.items()}
        singletons = sorted(fc for fc, n in totals.items() if n <= 1)
        thin = sorted(fc for fc, n in totals.items() if n <= 6)

        assert singletons, (
            "no single-observation flaw class — the memory has grown past the "
            f"state this evaluation describes: {totals}")
        assert 8 in singletons, (
            f"flaw class 8 is no longer a singleton: {totals}. It was THE "
            f"class that mattered, being the only one whose prior pulls "
            f"R_k(0) downward; re-run the evaluation.")
        assert len(thin) >= len(totals) - 2, (
            f"most classes should still be thin; totals={totals}")

        # Classes 1 and 5 carry the bulk, and class 1 is also the parser's
        # DEFAULT for any finding that arrives without a FLAW_CLASS marker
        # (runner_core `_parse_flaw_class`, and the DeepSeek header adapter
        # which stamps flaw_class 1 explicitly). Its rate is therefore closer
        # to "the pipeline's overall confirmation rate" than to a property of
        # logic defects, and it must not be read as the latter.
        assert totals[1] >= 50 and totals[5] >= 50, totals

    def test_confirmation_rates_are_a_terminal_decision_ratio_not_a_flaw_rate(self):
        """π_mem = confirmed / (confirmed + REFUTED). Findings that end
        UNCONFIRMED, MERGED or DUPLICATE enter NEITHER count, so π_mem is
        'given a terminal confirm-or-refute, P(confirm)' — near 1 by
        construction in a CONFIRM-only pipeline — not 'P(a claimed flaw of
        this class is real)'. The gap is measured here so it cannot be
        glossed."""
        counted = excluded = 0
        for run in _RECORDING_RUNS:
            for entry in _report_for(run)["registry"]["entries"].values():
                if entry["status"] in _CONFIRMED_STATUSES or \
                        entry["status"] == _REJECTED_STATUS:
                    counted += 1
                else:
                    excluded += 1
        assert excluded > 0, (
            "no findings fall outside the confirm/refute tally — the caveat "
            "this test records would no longer apply")

        mem = _memory_on_disk()
        well_populated = [fc for fc, r in mem._records.items() if r.total >= 5]
        for fc in well_populated:
            assert mem.pi_mem(fc) > 0.9, (
                f"class {fc} π_mem={mem.pi_mem(fc):.4f} — the near-unanimous "
                f"rate this caveat explains no longer holds; re-derive it")

    def test_experiments_seen_counts_appearances_not_observations(self):
        """A flaw class present in a run but contributing (0, 0) — every one
        of its findings ended MERGED or UNCONFIRMED — still increments
        `experiments_seen`. So the field a reader would use to judge "how much
        evidence is this?" over-reports. Exp 48 did exactly that for class 3."""
        counts = _flaw_counts_from(_report_for("exp48_chemistry_exam_live"))
        empty = [fc for fc, (c, r) in counts.items() if c == 0 and r == 0]
        assert empty, f"expected a zero-contribution class in Exp 48: {counts}"

        mem = ImmuneMemory()
        mem.record_experiment("only", {3: (0, 0)})
        assert mem._records[3].experiments_seen == 1
        assert mem._records[3].total == 0.0
        assert mem.pi_mem(3) == pytest.approx(0.5), (
            "a zero-contribution appearance must leave π_mem uninformative")


# ─────────────────────────────────────────────────────────────────────────────
# 2. THE COUNTERFACTUAL — would consumption have moved anything?
# ─────────────────────────────────────────────────────────────────────────────

class TestCounterfactual:

    def test_archive_used_the_runner_defaults(self):
        """Premise of every replay below: R_k(0) was the literal uniform prior
        in every archived decision, and `model_params` is written nowhere."""
        decisions = _all_archived_decisions()
        assert decisions, "no archived S* decisions found"
        for run, cid, _fc, res in decisions:
            assert res["R_old"] == RK0_PI_BASE, (
                f"{run}/{cid}: archived R_old {res['R_old']} — the archive was "
                f"not produced at the uniform prior")

    def test_replay_reproduces_every_archived_decision(self):
        """Guard on the harness itself before it is used to prove a negative."""
        for run, cid, _fc, res in _all_archived_decisions():
            passes, s_star = check_sk_threshold(
                res["sk"], nu_b=NU_B, nu_f=NU_F, q=Q, R=RK0_PI_BASE, s_floor=0.0)
            assert passes == res["passes_threshold"], f"{run}/{cid}"
            assert s_star == pytest.approx(res["s_star"], abs=1e-9), f"{run}/{cid}"

    def test_no_decision_flips_under_todays_memory(self):
        """The measurement the enable/don't-enable decision rests on: every
        archived S* decision, replayed against the strongest prior that
        exists — the memory as it stands now, which is what a future run would
        actually load."""
        mem = _memory_on_disk()
        flips = []
        for run, cid, fc, res in _all_archived_decisions():
            R = mem.blended_prior(fc, RK0_PI_BASE, RHO)
            passes, s_star = check_sk_threshold(
                res["sk"], nu_b=NU_B, nu_f=NU_F, q=Q, R=R, s_floor=0.0)
            if passes != res["passes_threshold"]:
                flips.append((run, cid, fc, res["sk"], res["s_star"], s_star))
        assert not flips, f"admissibility flipped under memory: {flips}"

    def test_the_first_recording_run_had_nothing_to_consume(self):
        """Exp 47 is the only recording run whose findings reached the S*
        decision at all, and it began with an EMPTY memory — where Jeffreys
        pseudocounts give π_mem = 0.5 for every class, so the blended prior is
        exactly π_base. Its counterfactual is identically zero, by
        construction rather than by luck."""
        empty = ImmuneMemory()
        for fc in (0, 1, 5, 8, 99):
            assert empty.blended_prior(fc, RK0_PI_BASE, RHO) == \
                pytest.approx(RK0_PI_BASE, abs=1e-12)

        for run in ("exp48_chemistry_exam_live", "exp49_engineering_exam_live"):
            reached = [d for d in _all_archived_decisions() if d[0].startswith(run)]
            assert not reached, (
                f"{run} now shows S* decisions ({len(reached)}); its findings "
                f"previously all failed fix-admission before the threshold, so "
                f"its counterfactual was empty for a second, independent reason")

    def test_the_margin_is_a_bound_not_a_coincidence(self):
        """S*(R) = (ν_b + ν_f − ν_b·ν_f − q·R) / (ν_f·(1 − ν_b)) is strictly
        decreasing in R, and R = (1−ρ)·0.5 + ρ·π_mem ≥ 0.5·(1−ρ). So at
        ρ = 0.2 the largest S* ANY memory can produce is 4/19 ≈ 0.2105,
        whatever it learns. Every fix ever scored beat that by a factor of
        three. SymPy and z3 agree on the bound (z3: S* ≥ 0.740 at ρ = 0.2 is
        unsat); this asserts it against the production decision function."""
        worst_R = (1.0 - RHO) * RK0_PI_BASE  # π_mem = 0, the strictest possible
        _, max_s_star = check_sk_threshold(
            0.0, nu_b=NU_B, nu_f=NU_F, q=Q, R=worst_R, s_floor=0.0)
        assert max_s_star == pytest.approx(4.0 / 19.0, abs=1e-4), max_s_star

        sks = [res["sk"] for _run, _cid, _fc, res in _all_archived_decisions()]
        assert len(sks) >= 1000, f"archive shrank to {len(sks)} decisions"
        assert min(sks) > max_s_star, (
            f"the weakest archived fix (S_k={min(sks)}) no longer clears the "
            f"strictest threshold ρ={RHO} can produce ({max_s_star:.4f}). "
            f"Consumption can now change an admissibility outcome — re-run the "
            f"evaluation before enabling it.")

    def test_rho_boundary_at_which_the_channel_opens(self):
        """Where the safety actually comes from, stated as a number. A flip
        needs S* > S_k, and sup_π_mem S*(ρ) = (25ρ − 1)/19, so the channel
        opens at ρ > (19·S_k_min + 1)/25 — 0.6024 against today's archive.
        `immune_memory_rho` is a free config float clamped only to [0, 1]:
        nothing in the code holds it below this line, so this test is the
        thing that would notice."""
        sk_min = min(res["sk"] for _r, _c, _f, res in _all_archived_decisions())
        rho_star = (19.0 * sk_min + 1.0) / 25.0
        assert rho_star == pytest.approx(0.6024, abs=5e-4), rho_star
        assert RHO < rho_star, (
            f"the configured default ρ={RHO} has reached the boundary "
            f"ρ*={rho_star:.4f} at which memory can decline a fix the uniform "
            f"prior admits")

        # Just above the boundary the flip is real, not theoretical.
        strict = (1.0 - 0.61) * RK0_PI_BASE  # ρ = 0.61, π_mem = 0
        passes_hi, s_hi = check_sk_threshold(
            sk_min, nu_b=NU_B, nu_f=NU_F, q=Q, R=strict, s_floor=0.0)
        passes_lo, _ = check_sk_threshold(
            sk_min, nu_b=NU_B, nu_f=NU_F, q=Q, R=RK0_PI_BASE, s_floor=0.0)
        assert passes_lo and not passes_hi, (
            f"at ρ=0.61 the weakest archived fix should be declined "
            f"(S*={s_hi:.4f} vs S_k={sk_min})")

    def test_only_flaw_class_8_can_bind_today_and_it_rests_on_one_observation(self):
        """The one live edge. Class 8's single REFUTED observation gives
        π_mem = 0.2625, R_k(0) = 0.4525 and a POSITIVE S* of 0.0724 — the only
        class whose prior creates a real threshold. No archived fix scores
        below it (min 0.740), so nothing flips; but this is a threshold
        derived from one observation, and it is the whole of the memory's
        current decision-relevant content."""
        mem = _memory_on_disk()
        binding = {}
        for fc in sorted(mem._records):
            R = mem.blended_prior(fc, RK0_PI_BASE, RHO)
            _, s_star = check_sk_threshold(
                0.5, nu_b=NU_B, nu_f=NU_F, q=Q, R=R, s_floor=0.0)
            if s_star > 0.0:
                binding[fc] = s_star
        assert list(binding) == [8], (
            f"classes producing a positive S* changed: {binding}")
        assert binding[8] == pytest.approx(0.0724, abs=5e-4), binding
        assert mem._records[8].total == pytest.approx(math.exp(-0.1), abs=1e-6), (
            "class 8 is no longer one decayed observation — the caveat above "
            "needs re-deriving")

    def test_the_sk_gate_has_never_bound_at_all(self):
        """Context for the whole question: at the uniform prior S* clamps to
        0.0 in every archived decision, and 92% of scores are exactly 1.0. The
        threshold consumption would feed has never rejected anything, so the
        upside of feeding it is bounded by 'a gate that has never fired might
        fire'."""
        decisions = _all_archived_decisions()
        assert all(res["s_star"] == 0.0 for _r, _c, _f, res in decisions)
        assert all(res["passes_threshold"] for _r, _c, _f, res in decisions)

    def test_no_admissible_result_has_a_falsy_gate_entry(self):
        """Premise of the `_rejection_lines` finding recorded in this module's
        docstring: a fix reaching the S* check has passed every gate, so a
        threshold rejection cannot honestly be reported as a gate failure."""
        falsy = []
        for run, cid, _fc, res in _all_archived_decisions():
            for key, val in (res.get("gate_details") or {}).items():
                if val is False or val == 0 or val == 0.0:
                    falsy.append((run, cid, key, val))
        assert not falsy, f"archived admissible results with a falsy gate: {falsy}"


# ─────────────────────────────────────────────────────────────────────────────
# 3. THE DRIFT DETECTOR
# ─────────────────────────────────────────────────────────────────────────────

class TestDriftDetector:

    def test_update_drift_has_no_production_caller(self):
        """Structural, not by inspection. 'It never fired' and 'it never ran'
        are different claims and only the second is true."""
        callers = []
        for path in glob.glob(os.path.join(_project_root, "bench", "**", "*.py"),
                              recursive=True):
            rel = os.path.relpath(path, _project_root)
            if os.sep + "tests" + os.sep in os.sep + rel or "__pycache__" in rel:
                continue
            try:
                with open(path, encoding="utf-8") as fh:
                    tree = ast.parse(fh.read())
            except (SyntaxError, UnicodeDecodeError, OSError):
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and \
                        isinstance(node.func, ast.Attribute) and \
                        node.func.attr in ("update_drift", "is_drifting"):
                    callers.append(f"{rel}:{node.lineno}")
        assert not callers, (
            f"update_drift/is_drifting now has a production caller: {callers}. "
            f"The detector is live — its calibration (see the asymmetry test "
            f"below) must be settled before it is trusted.")

    def test_replaying_the_recorded_runs_never_fires_it(self):
        """Fed the observed per-class confirmation rate of each recording run,
        against the memory as it stood before that run."""
        mem = ImmuneMemory()  # drift_threshold default 2.0
        peak_pos, trough_neg, fired = 0.0, 0.0, []
        for run in _RECORDING_RUNS:
            counts = _flaw_counts_from(_report_for(run))
            for fc, (conf, rej) in sorted(counts.items()):
                total = conf + rej
                if total == 0:
                    continue
                if mem.update_drift(fc, conf / total):
                    fired.append((run, fc))
                state = mem._drift[fc]
                peak_pos = max(peak_pos, state.cusum_pos)
                trough_neg = min(trough_neg, state.cusum_neg)
            mem.record_experiment(run, counts)
        assert not fired, f"drift would have fired at {fired}"
        assert peak_pos < 1.0 and trough_neg > -1.0, (
            f"CUSUM excursions grew (peak +{peak_pos:.3f}, {trough_neg:.3f}) — "
            f"they were +0.560/−0.500 against a threshold of 2.0")

    def test_the_detector_is_one_directional_at_the_learned_rates(self):
        """The residual is observed_rate − π_mem, so the largest UPWARD step
        possible is 1 − π_mem. At the rates this memory has learned that caps
        the upward step near zero: the better the memory thinks a class is
        doing, the less able it becomes to notice it doing even better —
        including the case where reality has moved and memory is simply
        stale. Downward, three all-refuted experiments suffice."""
        mem = _memory_on_disk()
        threshold = mem.drift_threshold
        for fc, rec in sorted(mem._records.items()):
            pi = mem.pi_mem(fc)
            up_step, down_step = 1.0 - pi, pi
            n_up = math.inf if up_step <= 0 else math.ceil(threshold / up_step)
            n_down = math.inf if down_step <= 0 else math.ceil(threshold / down_step)
            if pi > 0.9:
                assert n_up >= 20, (
                    f"class {fc}: π_mem={pi:.4f} should need >=20 consecutive "
                    f"perfect-confirmation experiments to flag, got {n_up}")
                assert n_down <= 3, f"class {fc}: downward needs {n_down}"

        # And the asymmetry is intrinsic, not an artefact of these counts.
        for pi in (0.90, 0.95, 0.99):
            assert math.ceil(2.0 / (1.0 - pi)) > math.ceil(2.0 / pi)


# ─────────────────────────────────────────────────────────────────────────────
# 4. INTEGRITY GUARDS ADDED 2026-08-12
# ─────────────────────────────────────────────────────────────────────────────

class TestIntegrityGuards:

    def test_reingesting_an_experiment_is_refused_and_leaves_counts_intact(self):
        """The runner's cycle is load → record → save against one shared file,
        so a resumed or re-run experiment used to add its whole registry a
        second time with no error and no report field."""
        mem = ImmuneMemory()
        mem.record_experiment("exp47", {1: (41, 2)})
        before = copy.deepcopy(mem._records[1].to_dict())

        with pytest.raises(MemoryIntegrityError, match="already recorded"):
            mem.record_experiment("exp47", {1: (41, 2)})

        assert mem._records[1].to_dict() == before, (
            "a refused ingestion must not have partially applied — decay is "
            "applied before the new counts, so a late refusal would silently "
            "shrink every existing record")
        assert mem._experiment_count == 1
        assert mem.experiment_ids == ("exp47",)

    def test_the_double_count_this_prevents_is_not_a_rounding_error(self):
        """Quantified, so the guard is not mistaken for tidiness: re-ingesting
        Exp 47 moves class 1's π_mem materially and nothing downstream could
        tell."""
        base = ImmuneMemory()
        base.record_experiment("exp47", {1: (41, 2)})
        doubled = ImmuneMemory()
        doubled.record_experiment("exp47", {1: (41, 2)})
        doubled.record_experiment("exp47", {1: (41, 2)}, allow_reingest=True)
        assert doubled.pi_mem(1) > base.pi_mem(1)
        assert doubled._records[1].confirmed > 1.8 * base._records[1].confirmed

    def test_reingest_is_available_when_it_is_meant(self):
        mem = ImmuneMemory()
        mem.record_experiment("replicate", {1: (5, 1)})
        mem.record_experiment("replicate", {1: (5, 1)}, allow_reingest=True)
        assert mem._experiment_count == 2
        assert mem.experiment_ids == ("replicate", "replicate")

    def test_provenance_survives_save_and_load(self, tmp_path):
        path = str(tmp_path / "mem.json")
        mem = ImmuneMemory()
        mem.record_experiment("expA", {1: (3, 1)})
        mem.record_experiment("expB", {2: (1, 1)})
        mem.save(path)

        reloaded = ImmuneMemory.load(path)
        assert reloaded.experiment_ids == ("expA", "expB")
        with pytest.raises(MemoryIntegrityError, match="already recorded"):
            reloaded.record_experiment("expA", {1: (3, 1)})

        with open(path) as fh:
            assert json.load(fh)["experiment_ids"] == ["expA", "expB"]

    def test_a_legacy_memory_cannot_recognise_its_own_sources(self, tmp_path,
                                                              caplog):
        """THE DUPLICATE GUARD IS PROSPECTIVE ONLY, and until 2026-08-12 that
        was silent (found by adversarial verification of the guard above).

        A memory written before the ledger existed carries `experiment_count`
        and NO `experiment_ids`, so it recognises none of its own sources and
        re-ingesting any of them is accepted with no error — the exact defect
        the guard exists to close, still open on every pre-ledger file. The
        guard is not wrong; it is inert here, and an inert guard that says
        nothing is a guard reporting a success it has not achieved. `load` now
        announces the state and `provenance_complete` makes it answerable.
        """
        path = str(tmp_path / "legacy.json")
        with open(path, "w") as fh:
            json.dump({
                "version": 1, "experiment_count": 3, "decay_rate": 0.1,
                "drift_threshold": 2.0, "source_hash": None,
                # No "experiment_ids" — the shape of every memory written
                # before the ledger, including the live one.
                "records": {"1": {"flaw_class": 1, "confirmed": 56.9,
                                  "rejected": 1.64, "experiments_seen": 3}},
            }, fh)

        with caplog.at_level(logging.WARNING, logger="cdsfl.memory"):
            mem = ImmuneMemory.load(path)
        assert not mem.provenance_complete
        assert mem.experiment_ids == () and mem._experiment_count == 3
        assert any("duplicate-ingestion guard CANNOT" in r.getMessage()
                   for r in caplog.records), (
            "a memory that cannot police its own re-ingestion must say so on "
            f"load; captured: {[r.getMessage() for r in caplog.records]}")

        # And the exposure itself, quantified rather than asserted in prose.
        before = mem._records[1].confirmed
        mem.record_experiment("exp47_divergence_locationkey_live", {1: (41, 2)})
        assert mem._records[1].confirmed > 1.5 * before, (
            "the legacy re-ingestion no longer doubles the count — if the file "
            "format changed, re-derive this exposure")

    def test_a_memory_written_since_the_ledger_knows_its_own_sources(self, tmp_path):
        path = str(tmp_path / "modern.json")
        mem = ImmuneMemory()
        mem.record_experiment("expA", {1: (3, 1)})
        mem.record_experiment("expB", {1: (2, 0)})
        mem.save(path)
        assert ImmuneMemory.load(path).provenance_complete

    def test_the_live_memory_predates_the_ledger_and_that_is_now_visible(self):
        """Stated as a fact about the real file, not an abstraction. A red here
        means the gap was CLOSED (experiment_ids backfilled) — update this test
        and delete the exposure note in `provenance_complete`."""
        mem = _memory_on_disk()
        assert not mem.provenance_complete, (
            f"the live memory now names its sources ({mem.experiment_ids}); "
            f"the duplicate guard has become effective for them")

    def test_an_unnamed_experiment_is_refused(self):
        mem = ImmuneMemory()
        for bad in ("", "   ", None):
            with pytest.raises(MemoryIntegrityError, match="non-empty exp_id"):
                mem.record_experiment(bad, {1: (1, 0)})

    def test_corrupt_counts_are_refused_at_both_entry_points(self, tmp_path):
        """π_mem outside [0, 1] — and so a blended prior outside [0, 1],
        contradicting this class's own documented bound — is reachable from a
        negative count. Both the ingest path and the file are checked, because
        a hand-edited or truncated JSON is the entry point no API guard sees."""
        mem = ImmuneMemory()
        for bad in (-1, float("nan"), float("inf"), "seven"):
            with pytest.raises(MemoryIntegrityError):
                mem.record_experiment(f"bad-{bad}", {1: (bad, 0)})
            with pytest.raises(MemoryIntegrityError):
                mem.record_experiment(f"bad-r-{bad}", {1: (0, bad)})

        path = str(tmp_path / "corrupt.json")
        with open(path, "w") as fh:
            json.dump({
                "version": 1, "experiment_count": 1, "decay_rate": 0.1,
                "drift_threshold": 2.0, "source_hash": None,
                "records": {"1": {"flaw_class": 1, "confirmed": -10.0,
                                  "rejected": 0.0, "experiments_seen": 1}},
            }, fh)
        with pytest.raises(MemoryIntegrityError):
            ImmuneMemory.load(path)

    def test_decay_must_actually_decay(self):
        """Exp 45 finding C0031, CONFIRMED 2026-07-27 and still live when
        measured on 2026-08-12. A negative `decay_rate` makes
        `math.exp(-decay_rate) > 1`, so the step named "decay" MULTIPLIES every
        existing count on each run: memory climbing toward certainty on no new
        evidence, with nothing downstream able to distinguish it from learning.
        Reachable through the persisted file, whose `decay_rate` `load` adopts
        verbatim — so both doors are checked."""
        for bad in (-0.5, float("nan"), float("inf")):
            with pytest.raises(MemoryIntegrityError):
                ImmuneMemory(decay_rate=bad)

        assert issubclass(MemoryIntegrityError, ValueError), (
            "the archived C0031 falsifier guards with `except (ValueError, "
            "TypeError): return`; raising outside that family makes a correct "
            "repair register as a broken falsifier")

        good = ImmuneMemory(decay_rate=0.1)
        good.record_experiment("seed", {7: (10, 4)})
        before = good._records[7].confirmed
        good.record_experiment("decay_only", {})
        assert good._records[7].confirmed < before, "decay must reduce counts"

    def test_a_negative_decay_rate_in_the_file_is_refused(self, tmp_path):
        path = str(tmp_path / "amplifying.json")
        with open(path, "w") as fh:
            json.dump({"version": 1, "experiment_count": 0, "decay_rate": -0.5,
                       "drift_threshold": 2.0, "source_hash": None,
                       "records": {}}, fh)
        with pytest.raises(MemoryIntegrityError, match="decay_rate"):
            ImmuneMemory.load(path)

    def test_the_live_memory_file_still_loads(self):
        """The guards must refuse corruption without refusing reality."""
        mem = _memory_on_disk()
        assert mem._experiment_count == 3
        assert mem.decay_rate == pytest.approx(0.1)
        assert sorted(mem._records) == [1, 2, 3, 4, 5, 6, 8]

    def test_the_bound_this_class_documents_now_actually_holds(self):
        """`blended_prior` promises [0, 1]. With the guards in place that is
        true for every state reachable through the API — including the counts
        that used to break it."""
        mem = ImmuneMemory()
        mem.record_experiment("ok", {1: (1000, 0), 2: (0, 1000), 3: (0, 0)})
        for fc in (1, 2, 3, 99):
            for rho in (0.0, 0.2, 0.5, 1.0):
                for base in (0.0, 0.5, 1.0):
                    pi = mem.blended_prior(fc, base, rho)
                    assert 0.0 <= pi <= 1.0, (fc, rho, base, pi)

    def test_an_ungrounded_hash_no_longer_reads_as_a_match(self, tmp_path):
        """The invalidation guard required BOTH hashes truthy, so a file with
        `source_hash: null` — which is what every memory written to date
        carries — passed silently. A caller arming the guard would have got a
        clean load and no warning on exactly the file it exists to catch."""
        path = str(tmp_path / "ungrounded.json")
        mem = ImmuneMemory()  # source_hash defaults to None
        mem.record_experiment("exp1", {1: (8, 2)})
        mem.save(path)
        with open(path) as fh:
            assert json.load(fh)["source_hash"] is None

        assert ImmuneMemory.load(path).pi_mem(1) == pytest.approx(mem.pi_mem(1))
        invalidated = ImmuneMemory.load(path, expected_hash="deadbeef")
        assert invalidated.pi_mem(1) == pytest.approx(0.5), (
            "an ungrounded memory must not satisfy a hash expectation")

    def test_the_memory_on_disk_is_ungrounded_and_that_is_now_visible(self):
        """Stated as a fact about the live file, not an abstraction: nothing
        computes a source hash, so the real memory carries none."""
        with open(_STATE) as fh:
            assert json.load(fh).get("source_hash") is None, (
                "the memory is now hash-grounded — the invalidation path is "
                "live and its behaviour on a code change needs measuring")


# ─────────────────────────────────────────────────────────────────────────────
# 5. P-PASS — the advisory-only claim, attacked
# ─────────────────────────────────────────────────────────────────────────────

class TestAdvisoryOnlyUnderAttack:

    def test_memory_never_reaches_a_finding_status(self):
        """The safety claim at its strongest point: no code path writes a
        finding's status from anything the memory produced. Checked
        structurally — `ImmuneMemory` is imported at exactly the two runner
        sites (record, consume) and neither assigns to `["status"]`."""
        runner = os.path.join(_project_root, "bench", "reference_runner_v3.py")
        with open(runner, encoding="utf-8") as fh:
            tree = ast.parse(fh.read())

        importers = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and \
                    (node.module or "").endswith("_memory"):
                importers.append(node)
        assert len(importers) == 2, (
            f"ImmuneMemory is imported at {len(importers)} sites; the two "
            f"known ones are the recording and consumption blocks")

        enclosing = []
        for imp in importers:
            best = None
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and \
                        node.lineno <= imp.lineno <= (node.end_lineno or 0):
                    if best is None or node.lineno > best.lineno:
                        best = node
            enclosing.append(best.name if best else "<module>")
        assert sorted(enclosing) == ["_build_rk0_prior", "run_experiment"], enclosing

    def test_but_memory_can_change_a_pipeline_outcome_and_here_is_the_case(self):
        """The attack that succeeds, stated honestly. Memory cannot set a
        verdict, but it CAN decline a fix the uniform prior admits — today,
        at the shipped ρ, for flaw class 8. No such fix exists in the archive
        (weakest is 0.740 against a 0.0724 threshold), so the exposure is
        latent rather than realised. It is not zero, and 'advisory-only' is a
        property of the current ρ and the current counts, not of the design."""
        mem = _memory_on_disk()
        R_mem = mem.blended_prior(8, RK0_PI_BASE, RHO)
        weak_sk = 0.05  # below class 8's threshold, above zero

        admits, s_uniform = check_sk_threshold(
            weak_sk, nu_b=NU_B, nu_f=NU_F, q=Q, R=RK0_PI_BASE, s_floor=0.0)
        declines, s_memory = check_sk_threshold(
            weak_sk, nu_b=NU_B, nu_f=NU_F, q=Q, R=R_mem, s_floor=0.0)

        assert admits and not declines, (
            f"the constructed override no longer holds: uniform S*={s_uniform}, "
            f"memory S*={s_memory} at R={R_mem:.4f}")
        assert s_uniform == 0.0 and s_memory > 0.0

        # And the outcome is not inert: a REJECTED tristate is rendered into
        # the panel's next prompt by `_rejection_lines`, so the memory reaches
        # the finding stream indirectly, via what the panel is told.
        from bench.reference_runner_v3 import _rejection_lines, SK_REJECTED
        lines = _rejection_lines({"sk_result": {"tristate": SK_REJECTED,
                                                "gate_details": {}}})
        assert lines and "REJECTED" in lines[0], lines

    def test_rho_zero_closes_the_channel_completely(self):
        """The escape hatch, verified against the live counts rather than
        assumed: ρ = 0 collapses the blended prior to π_base for every class,
        including class 8."""
        mem = _memory_on_disk()
        for fc in sorted(mem._records) + [99]:
            assert mem.blended_prior(fc, RK0_PI_BASE, 0.0) == \
                pytest.approx(RK0_PI_BASE, abs=1e-12)
