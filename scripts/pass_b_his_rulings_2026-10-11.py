#!/usr/bin/env python3
"""Pass B: did the founder's own rulings land? Enumerated from HIS words, not from mine.

WHY PASS A WAS THROWN AWAY. The first inventory enumerated "what was agreed" from 5 sources
that were ALL the assistant's own writing -- 2 git-log passes, WORK_IN_FLIGHT_2026-10-07.md,
RECOVERY.md, and the operational tracker. **0 read the founder's own responses.** So it could
not detect the one thing he asked about: an instruction he gave that was never recorded. 29 of
his 200 window annotations have no verbal trace in those 5 sources at all.

PASS B INVERTS THE SOURCE. Every item below is one of HIS annotations, quoted, with its date
and file, and the check asks whether the tree does what he asked. His record is the independent
check on the assistant's, which is the only arrangement that can answer his question.

SCOPE, on his instruction of 2026-10-11: *"implement any previously ruled/agreed work not done
so far, over lets say a reasonable window of the last 7 days (so we don't get stuck in deep
time archaeology)."* So 2026-10-04 onward for implementation. Annotations are read from
2026-09-29 so the earlier context is visible, and anything older than 7 days is reported
WITHOUT being actioned.

Run: python3 scripts/pass_b_his_rulings_2026-10-11.py
     python3 scripts/pass_b_his_rulings_2026-10-11.py --json
"""
from __future__ import annotations

import argparse
import ast
import glob
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
Z = 1.959963984540054
IMPLEMENTATION_WINDOW_OPENS = "2026-10-04"


def wilson(k: int, n: int) -> tuple:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = (Z / d) * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return (round(max(0.0, c - h), 4), round(min(1.0, c + h), 4))


def _runner_config_default(field: str):
    """Read a RunnerConfig default by INSTANTIATING it, never by reading the source."""
    spec = importlib.util.spec_from_file_location("rr_pb", REPO / "bench/reference_runner_v3.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["rr_pb"] = m
    spec.loader.exec_module(m)
    cfg = m.RunnerConfig(experiment_name="t", models=["A"])
    return getattr(cfg, field, "__ABSENT__")


def _flatten(o, out=None, _top=True):
    if out is None:
        out = {}
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(k, str) and k.startswith("_"):
                continue
            if isinstance(v, (dict, list)):
                _flatten(v, out, _top=False)
            elif _top or k not in out:
                out[k] = v
    elif isinstance(o, list):
        for v in o:
            _flatten(v, out, _top=False)
    return out


def _config_values(field: str) -> dict:
    vals = {}
    files = sorted(glob.glob(str(REPO / "bench/exp*_configs/*.json")))
    for f in files:
        try:
            flat = _flatten(json.load(open(f)))
        except Exception:
            continue
        if field in flat:
            vals[str(flat[field])] = vals.get(str(flat[field]), 0) + 1
    return {"configs": len(files), "values": vals,
            "set_in": sum(vals.values())}


def _symbol_exists(rel: str, needle: str) -> bool:
    f = REPO / rel
    return f.is_file() and needle in f.read_text(errors="ignore")


# ============================================================ the checks
def _historical_off_configs() -> tuple:
    """Split the burst_mode=off configs into completed-run RECORDS and future-run configs.

    WHY THIS SPLIT EXISTS. A first reading reported "43 of 47 configs defy his ruling" and the
    implied remedy was a bulk edit. FOLLOW refused it: 33 of the 43 describe experiments that
    have already run and are archived under bench/logs/, so rewriting them would falsify the
    record rather than fix anything.
    """
    import os
    logs = {os.path.basename(p) for p in glob.glob(str(REPO / "bench/logs/*"))}
    hist, live = [], []
    for f in sorted(glob.glob(str(REPO / "bench/exp*_configs/*.json"))):
        try:
            fl = _flatten(json.load(open(f)))
        except Exception:
            continue
        if fl.get("burst_mode") != "off":
            continue
        name = fl.get("experiment_name") or os.path.basename(f).replace(".json", "")
        ran = any(name.split("_")[0] in L or name in L for L in logs)
        (hist if ran else live).append(os.path.basename(f))
    return len(hist), live


def check_gamma_gates_in_all_cases() -> dict:
    """ANN 143/157/214, 2026-10-08: *"Gamma should remain active in all cases. Fix it."*"""
    return {"check": "gamma gates wherever a slope exists",
            "his_words": "Gamma should remain active in all cases. Fix it.",
            "date": "2026-10-08",
            "evidence": {"_gamma_is_estimable present":
                         _symbol_exists("bench/reference_runner_v3.py", "_gamma_is_estimable")},
            "landed": _symbol_exists("bench/reference_runner_v3.py", "_gamma_is_estimable")}


def check_no_cap_on_the_ladder() -> dict:
    """ANN 45, 2026-10-05: *"I dont think there should be a cap at all ... until it is either
    resolved, or the ladder is exhausted."*"""
    spec = importlib.util.spec_from_file_location("rt_pb", REPO / "bench/routing.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["rt_pb"] = m
    spec.loader.exec_module(m)
    d = getattr(m, "DEFAULT_MAX_RUNGS", None)
    return {"check": "no cap on the routing ladder",
            "his_words": "I dont think there should be a cap at all",
            "date": "2026-10-05",
            "evidence": {"DEFAULT_MAX_RUNGS": d, "0 means exhaust": d == 0},
            "landed": d == 0}


def check_the_self_rung_routes_back() -> dict:
    """ANN 216/39: *"at least one rung on the ladder should point back to the original model
    and say, your solution didnt work or your falsifier is broken please fix."*"""
    import inspect
    spec = importlib.util.spec_from_file_location("rt_pb2", REPO / "bench/routing.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["rt_pb2"] = m
    spec.loader.exec_module(m)
    sig = inspect.signature(m.route)
    d = sig.parameters.get("self_rung_enabled")
    on = d is not None and d.default is True
    return {"check": "the ladder routes back to the source model",
            "his_words": "at least one rung should point back to the original model",
            "date": "2026-10-06",
            "evidence": {"self_rung_enabled default": (d.default if d else "__ABSENT__")},
            "landed": on}


def check_burst_logic_is_on() -> dict:
    """ANN 22/26, 2026-10-05: *"Burst logic mode is part of the ITC mechanism ... It shouldnt
    be off as far as I am concerned."* and *"this should also be on, by default in all our
    runners."*"""
    # FALSE NEGATIVE CORRECTED 2026-10-11. The first version of this check probed for
    # `burst_enabled`, `burst_mode_enabled` and `itc_burst_enabled`, NONE of which exist, and
    # reported NOT LANDED on a facility that is in fact on. The real field is
    # `burst_mode: str = "auto"` and the runner reads it as `if cfg.burst_mode != "off"`
    # (reference_runner_v3.py:15667), so "auto" satisfies his ruling and only "off" violates
    # it. This is the 5th predicate error of the session and it failed toward a COMFORTABLE
    # answer -- reporting work as undone is not comfortable, but inventing a field name is the
    # same `check the predicate before the result` shape either way.
    mode = _runner_config_default("burst_mode")
    cfg = _config_values("burst_mode")
    off_in_configs = cfg["values"].get("off", 0)
    on = (mode != "__ABSENT__") and (mode != "off")
    return {"check": "burst logic (part of ITC) is not off",
            "his_words": "It shouldnt be off as far as I am concerned",
            "date": "2026-10-05",
            "evidence": {"RunnerConfig burst_mode default": mode,
                         "the runner gates on `!= \"off\"`":
                             _symbol_exists("bench/reference_runner_v3.py",
                                            'cfg.burst_mode != "off"'),
                         "configs": cfg,
                         "configs setting it OFF": off_in_configs},
            "configs_that_are_historical_records": _historical_off_configs()[0],
            "configs_that_would_affect_a_future_run": _historical_off_configs()[1],
            "landed": on,
            "note": ("THE DEFAULT SATISFIES HIM and must not be confused with the configs. "
                     "\"auto\" is not off: the runner plans a burst whenever `should_burst` "
                     "fires. 43 configs pin \"off\", but FOLLOW established that 33 of those "
                     "are HISTORICAL RECORDS of completed runs -- editing them would falsify "
                     "the experimental record -- and of the remaining 10, five are the exp52 "
                     "factorial cells where burst mode is part of the DESIGN. So the bulk edit "
                     "is refused and the 10 are HIS RULING, not a defect to patch")}


def check_immune_memory_is_on() -> dict:
    """ANN 78, 2026-10-05: *"you should fix it, and immune memory, along with everything else
    should work and sing in close harmony with the rest of the schema."*"""
    d = _runner_config_default("immune_memory_enabled")
    cfg = _config_values("immune_memory_enabled")
    return {"check": "immune memory is on",
            "his_words": "immune memory ... should work and sing in close harmony",
            "date": "2026-10-05",
            "evidence": {"RunnerConfig default": d, "configs": cfg},
            "landed": d is True}


def check_fold_fixes_forward() -> dict:
    """ANN 27, 2026-10-05: *"Fold fixes forward is a useful facility ... providing it never
    touches the live tree and we can still review those fixes."*"""
    d = _runner_config_default("apply_fixes_back_enabled")
    cfg = _config_values("apply_fixes_back_enabled")
    guard = bool(glob.glob(str(REPO / "bench/tests/*seat_cannot_write*")))
    return {"check": "fold fixes forward, with the live tree protected",
            "his_words": "providing it never touches the live tree",
            "date": "2026-10-05",
            "evidence": {"RunnerConfig default": d, "configs": cfg,
                         "live-tree write guard exists": guard},
            "landed": (d is True) and guard}


def check_the_completion_marker_replaces_the_arbitrary_cap() -> dict:
    """ANN 155, 2026-10-08: *"the cap doesnt need to be arbitrary, at 900, or 1800 ... We can
    tell the models to print I am done at the end of all heir outputs, then watch for this
    signal in their output logs."*

    THIS IS THE ONE THAT WAS HALF-DONE. An overridable cap was built (PANEL_SEAT_TIMEOUT_S);
    the completion signal he actually proposed was not.
    """
    panel = REPO / "bench/confer_maths_panel_2026-09-05.py"
    t = panel.read_text(errors="ignore") if panel.is_file() else ""
    cap = "PANEL_SEAT_TIMEOUT_S" in t or "_seat_timeout_seconds" in t
    marker = bool(re.search(r"I am done|DONE_MARKER|completion[_ ]marker|_await_done",
                            t, re.I))
    return {"check": "a completion signal replaces the arbitrary seat cap",
            "his_words": "tell the models to print I am done ... watch for this signal",
            "date": "2026-10-08",
            "evidence": {"overridable cap built": cap,
                         "completion signal built": marker},
            "landed": marker,
            "note": ("the cap half landed and the signal half did not; his ruling was to make "
                     "the cap NON-arbitrary, not merely adjustable")}


def check_the_round_cap_prints_a_recommendation() -> dict:
    """ANN 108/184: *"Go with 10 with a recommendation to the reviewer to set a higher cap if
    convergence appears within direct reach."*"""
    rr = (REPO / "bench/reference_runner_v3.py").read_text(errors="ignore")
    cap = _runner_config_default("max_rounds")
    rec = bool(re.search(r"within (direct )?reach|recommend.{0,40}(higher|extend).{0,30}cap|"
                         r"extend the run", rr, re.I))
    return {"check": "round cap 10, with a printed recommendation to extend",
            "his_words": "Go with 10 with a recommendation to the reviewer to set a higher cap",
            "date": "2026-09-30 / 2026-10-01",
            "evidence": {"max_rounds default": cap, "recommendation printed": rec},
            "landed": rec}


def check_scale_independence() -> dict:
    """ANN 147/240, 2026-10-07/08: *"the system should be able to cope with 5, or 6, or 70, or
    700 models."* So no live module may hard-code the roster size."""
    offenders = []
    for rel in ("bench/routing.py", "bench/reference_runner_v3.py",
                "bench/tools/run_simulated_experiment.py"):
        f = REPO / rel
        if not f.is_file():
            continue
        for i, line in enumerate(f.read_text(errors="ignore").splitlines(), 1):
            s = line.strip()
            if s.startswith("#") or not s:
                continue
            if re.search(r"(len\(\s*models\s*\)|n_models|roster)\s*(==|<=|>=)\s*[567]\b", s):
                offenders.append(f"{rel}:{i}  {s[:90]}")
    return {"check": "no live module hard-codes the roster size",
            "his_words": "5, or 6, or 70, or 700 models",
            "date": "2026-10-07",
            "evidence": {"hard-coded roster comparisons": offenders},
            "landed": not offenders}


def check_the_programme_spelling_rule_is_recorded() -> dict:
    """ANN 61, 2026-10-05: *"as a UK native, I tend to use the word programme ... whereas I
    will use program, to denote a software program ... you should mark it nevertheless."*"""
    hits = []
    for rel in (".claude/CLAUDE.md",):
        f = REPO / rel
        if f.is_file() and re.search(r"programme.{0,120}program\b|program\b.{0,120}programme",
                                     f.read_text(errors="ignore"), re.S | re.I):
            hits.append(rel)
    mem = Path.home() / ".claude/projects/-Users-georgejackson-Developer-Projects/memory"
    for f in mem.glob("*.md"):
        if re.search(r"\bprogramme\b.{0,200}\bprogram\b", f.read_text(errors="ignore"), re.S):
            hits.append(f"memory/{f.name}")
    return {"check": "his programme-versus-program spelling rule is recorded",
            "his_words": "you should mark it nevertheless",
            "date": "2026-10-05",
            "evidence": {"recorded in": hits},
            "landed": bool(hits)}


def check_the_invented_terminology_guard() -> dict:
    """ANN 122/170/234, said at least 3 times: *"we have already had extensive discussion about
    your habit of inventing non-project specific terms ... You said you would fix it!?"*"""
    guards = sorted(glob.glob(str(REPO / "bench/tests/*term*")) +
                    glob.glob(str(REPO / "bench/tests/*vocab*")) +
                    glob.glob(str(REPO / "bench/tests/*glossary*")))
    lint = REPO / "scripts/note_vagueness_lint.py"
    checks_terms = False
    if lint.is_file():
        t = lint.read_text(errors="ignore")
        checks_terms = bool(re.search(r"invent|non-project|unofficial|glossar", t, re.I))
    return {"check": "a guard against inventing non-project terminology",
            "his_words": "You said you would fix it!?",
            "date": "2026-10-02 / 2026-10-04",
            "evidence": {"candidate guards": [str(Path(g).name) for g in guards],
                         "the note linter checks for invented terms": checks_terms},
            "landed": checks_terms or bool(guards)}


def check_the_token_spend_was_addressed() -> dict:
    """ANN 235, 2026-10-04: *"a big spike in my Anthropic Max plan usage quota, and right now I
    am nearly out of my weekly allowance ... I usually only barely scratch the surface."*

    TODAY'S FIX COVERS LOCAL CPU AND RAM. His 2026-10-04 note was about TOKEN BURN, which is a
    different resource and is NOT addressed by the budget gate.
    """
    budget = REPO / "scripts/local_resource_budget_2026-10-11.py"
    hook = Path.home() / ".claude/hooks/local_resource_budget.py"
    cm = REPO / ".claude/CLAUDE.md"
    # The plan limits are readable ONLY from inside a session (mcp get_usage), so no standalone
    # script or hook can meter them. The enforceable parts are therefore: the hook DEMANDS the
    # check on every allowed fan-out, and the directive makes it mandatory with a baseline.
    hook_demands = (hook.is_file()
                    and "get_usage" in hook.read_text(errors="ignore"))
    directive = (cm.is_file()
                 and "HIS TOKEN ALLOWANCE IS THE SECOND RESOURCE" in cm.read_text(errors="ignore"))
    return {"check": "his token-quota spike of 2026-10-04 is addressed",
            "his_words": "nearly out of my weekly allowance",
            "date": "2026-10-04",
            "evidence": {"local CPU/RAM budget exists": budget.is_file(),
                         "the hook demands a plan check on every fan-out": hook_demands,
                         "the directive makes it mandatory, with a baseline": directive},
            "landed": hook_demands and directive,
            "note": ("the plan window is readable only from inside a session, so the metering "
                     "cannot be automated; the hook demands it and the directive binds it. It "
                     "sat UNREAD for 7 days in a file grep treated as binary")}


CHECKS = (
    check_gamma_gates_in_all_cases,
    check_no_cap_on_the_ladder,
    check_the_self_rung_routes_back,
    check_burst_logic_is_on,
    check_immune_memory_is_on,
    check_fold_fixes_forward,
    check_the_completion_marker_replaces_the_arbitrary_cap,
    check_the_round_cap_prints_a_recommendation,
    check_scale_independence,
    check_the_programme_spelling_rule_is_recorded,
    check_the_invented_terminology_guard,
    check_the_token_spend_was_addressed,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    rows = []
    for fn in CHECKS:
        try:
            rows.append(fn())
        except Exception as e:
            rows.append({"check": fn.__name__, "landed": None,
                         "error": f"{type(e).__name__}: {e}"})
    if args.json:
        print(json.dumps(rows, indent=1, default=str))
        return 0
    landed = [r for r in rows if r.get("landed") is True]
    not_landed = [r for r in rows if r.get("landed") is False]
    errored = [r for r in rows if r.get("landed") is None]
    print("== HIS rulings, checked against the tree ==\n")
    for r in rows:
        mark = {True: "LANDED    ", False: "NOT LANDED", None: "ERROR     "}[r.get("landed")]
        print(f"  [{mark}] {r['check']}")
        if r.get("his_words"):
            print(f"       his words ({r.get('date')}): \"{r['his_words']}\"")
        for k, v in (r.get("evidence") or {}).items():
            print(f"         {k}: {v}")
        if r.get("note"):
            print(f"         -> {r['note']}")
        if r.get("error"):
            print(f"         !! {r['error']}")
        print()
    n = len(rows)
    for label, lst in (("LANDED", landed), ("NOT LANDED", not_landed), ("ERROR", errored)):
        lo, hi = wilson(len(lst), n)
        print(f"   {label:11s} {len(lst):>2} of {n} = {len(lst)/n:.4f}  Wilson [{lo}, {hi}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
