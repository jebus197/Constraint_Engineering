"""The false-quiet window is 7 in every config whose experiment has not yet run.

HIS RULING, 2026-10-08, verbatim: *"Verdict. Fix it and check your fix with the
free panel."* It answered a panel finding that even at full roster there is a
**0.1159** chance of 3 consecutive quiet rounds arising without the problem space
being exhausted, and that *"The only levers identified are a longer required
quiet run, or more seats"*.

THE MEASUREMENT IS COMMITTED at
`bench/the_false_quiet_rate_is_not_the_gates_rate_2026-10-08.py`: the
premature-window rate falls **0.1264 -> 0.0784 -> 0.0458 -> 0.0263 -> 0.0000** as
the required quiet run goes 3 -> 4 -> 5 -> 6 -> 7. So 7 is the value at which the
rate reaches zero, and that is why 7 was chosen rather than a round number.

THE DEFAULT WAS REPAIRED AND EVERY CALLER OVERRODE IT.
`RunnerConfig.gamma_alt_consecutive_zero_crit` derives from
`REQUIRED_QUIET_RUN`, which was 7 when this file was written and **is 3 today**
-- restored by his ruling of 2026-10-27 after the measurement behind 7 was shown
to rest on a condition that never fires. The paragraphs below are kept in the
tense of 2026-10-17 because they record why 7 was chosen at the time; the live
assertion in `test_the_default_derives_from_the_measurement` is the current
value, and it reads 3. On 2026-10-17 **32 of 47 shipped configs set the
value to 3 explicitly**, so the repair was inert for every experiment that
matters -- the shape the additive standard calls an addition nothing reaches.

WHY ONLY 12 OF THE 32 WERE RAISED, and this is the boundary that matters. A
config is also the RECORD of how an experiment was run. Of the 32, **20 belong
to experiments with archived runs in `bench/logs/`** and are left exactly as they
are: editing them would misrepresent how exp40 through exp49, exp53 and exp55
were actually conducted, which is falsifying evidence rather than fixing a
default. The other **12 have no archived run** -- exp50 physics, exp51 biology,
exp52's 5 factorial cells and exp56's 3 arms -- and every one of them carries
`max_rounds` of 8 or 16, so a quiet run of 7 is reachable.

FEASIBILITY WAS CHECKED BEFORE THE CHANGE, not after: **31 of 33 configs setting
the knob have `max_rounds` >= 7 -- 93.9394%, Wilson [80.3938%, 98.3219%],
Clopper-Pearson [79.7736%, 99.2574%]**. The 2 that do not are
`42_composer_confirm.json` at 2 rounds and `55_v3_control.json` at 6, both
already-run and both therefore untouched anyway.

THE COST IS REAL AND IS STATED RATHER THAN BURIED. A quiet run of 7 needs at
least 7 settled rounds, so a converging run takes 8 rounds where it used to take
4. The 3 shakedown legs converged at rounds 3, 4 and 4. On a PAID run that is
roughly double the dispatches, and it is the price of taking the premature-window
rate from 0.1264 to 0.0000.
"""
from __future__ import annotations

import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
CONFIG_ROOT = REPO / "bench"
LOGS = REPO / "bench" / "logs"
KNOB = "gamma_alt_consecutive_zero_crit"

#: Deliberate instrumentation, not a quiet-run setting: 999 disables the arm.
INSTRUMENTATION_VALUES = {999}


def _find(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            got = _find(v, key)
            if got is not None:
                return got
    elif isinstance(obj, list):
        for v in obj:
            got = _find(v, key)
            if got is not None:
                return got
    return None


def _configs():
    for p in sorted(CONFIG_ROOT.glob("exp*_configs/*.json")):
        try:
            yield p, json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue


def _has_archived_run(cfg) -> bool:
    name = _find(cfg, "experiment_name") or _find(cfg, "name")
    if not name:
        return False
    return any(d.is_dir() and d.name.startswith(str(name))
               for d in LOGS.iterdir())


@pytest.fixture(scope="module")
def runner():
    import bench.reference_runner_v3 as mod
    return mod


def test_the_default_derives_from_the_measurement(runner):
    """The dataclass default must BE `REQUIRED_QUIET_RUN`, not a copy of it."""
    import dataclasses
    declared = {f.name: f.default
                for f in dataclasses.fields(runner.RunnerConfig)}
    # REVERTED TO 3 ON HIS RULING OF 2026-10-27. This assertion read `== 7`
    # from 2026-10-17 until then, on the premise that 7 is where the measured
    # premature-window rate reaches 0.0000.
    #
    # THE PREMISE DID NOT SURVIVE. That 0.0000 is NON-OCCURRENCE: 7 consecutive
    # quiet rounds occur 0 times across 63 reports and 409 usable rounds, so the
    # rate went to zero because its condition never fires, not because the
    # setting is safe. Both free-panel seats returned REVERT_TO_3 independently
    # on 2026-10-25. Producers:
    # `bench/what_should_the_quiet_run_be_2026-10-25.py` and
    # `bench/can_any_signal_see_a_premature_close_2026-10-27.py`.
    #
    # THE FILENAME IS NOW HISTORICAL and is deliberately not changed: it records
    # when the value WAS seven, and renaming it would erase that from the tree.
    assert runner.REQUIRED_QUIET_RUN == 3, (
        "3 is the value his ruling of 2026-10-27 restored, after the measurement "
        "behind 7 was shown to rest on a condition that never fires; a different "
        "value needs its own measurement AND his ruling")
    assert declared[KNOB] == runner.REQUIRED_QUIET_RUN


def test_no_unrun_config_converges_sooner_than_the_measurement_allows(runner):
    """THE RATCHET. An experiment still to run may not keep the old window."""
    offenders = []
    for path, cfg in _configs():
        value = _find(cfg, KNOB)
        if value is None or value in INSTRUMENTATION_VALUES:
            continue
        if _has_archived_run(cfg):
            continue
        if value < runner.REQUIRED_QUIET_RUN:
            offenders.append((path.relative_to(CONFIG_ROOT), value))
    assert not offenders, (
        f"these configs have no archived run and would converge on a window "
        f"shorter than the measured {runner.REQUIRED_QUIET_RUN}, so his "
        f"2026-10-08 ruling would be inert for them:\n"
        + "\n".join(f"    {p}: {v}" for p, v in offenders))


def test_an_already_run_config_is_left_as_the_record():
    """ANTI-OVERREACH. The archived configs must still read 3.

    This is the other half of the ratchet and it fails if a later sweep
    'tidies' them: a config is the record of how an experiment was conducted,
    and rewriting exp42's window would misrepresent a run that has happened.
    """
    kept = []
    for path, cfg in _configs():
        value = _find(cfg, KNOB)
        if value is None or value in INSTRUMENTATION_VALUES:
            continue
        if _has_archived_run(cfg):
            kept.append((path.relative_to(CONFIG_ROOT), value))
    assert kept, "no archived config found; this test has gone blind"
    rewritten = [(p, v) for p, v in kept if v != 3]
    assert not rewritten, (
        "these configs record experiments that have already run, and their "
        "convergence window has been changed, which misrepresents how those "
        "runs were conducted:\n"
        + "\n".join(f"    {p}: {v}" for p, v in rewritten))


def test_every_unrun_config_can_actually_reach_the_window():
    """A window of 7 inside a 6-round budget can never be satisfied.

    Checked BEFORE the change was applied rather than after, and asserted here
    so a future config added with a short round budget and a long window is
    refused rather than left to exhaust its rounds every run.

    SCOPED TO UNRUN CONFIGS, because the first version of this assertion went
    red on an ARCHIVED one and that was a genuine historical finding rather than
    something to fix: `exp42_configs/42_composer_confirm.json` sets a window of
    3 inside `max_rounds` of 2, so the alternative
    convergence route that counts consecutive settled rounds could never have
    been satisfied in that run and the run must have terminated by another route. It is
    left alone, like every other archived config, and recorded here instead --
    the next test asserts that it stays recorded rather than tidied.
    """
    bad = []
    for path, cfg in _configs():
        value = _find(cfg, KNOB)
        if value is None or value in INSTRUMENTATION_VALUES:
            continue
        if _has_archived_run(cfg):
            continue
        rounds = _find(cfg, "max_rounds")
        if rounds is not None and value > rounds:
            bad.append((path.relative_to(CONFIG_ROOT), value, rounds))
    assert not bad, (
        "these configs require more settled rounds than they are allowed to "
        "run, so they can never converge:\n"
        + "\n".join(f"    {p}: window {v} > max_rounds {r}"
                    for p, v, r in bad))


def test_the_unsatisfiable_archived_window_is_still_on_the_record():
    """The exp42 case must not be quietly tidied away.

    ANTI-VACUITY FOR THE ONE ABOVE. If someone 'fixes'
    `42_composer_confirm.json` by widening its round budget or shrinking its
    window, the historical fact that its settled-round convergence route was unsatisfiable
    disappears, and the exemption in the previous test starts protecting
    nothing. Asserted on the archived file so the record stays legible.
    """
    p = CONFIG_ROOT / "exp42_configs" / "42_composer_confirm.json"
    if not p.is_file():
        pytest.skip("the archived config is gone; nothing left to protect")
    cfg = json.loads(p.read_text(encoding="utf-8"))
    window, rounds = _find(cfg, KNOB), _find(cfg, "max_rounds")
    assert (window, rounds) == (3, 2), (
        f"this archived config recorded an unsatisfiable settled-round window "
        f"(3 settled rounds required inside a 2-round budget) and now reads "
        f"({window}, {rounds}). If it was changed deliberately, the historical "
        f"finding needs recording somewhere that survives.")
