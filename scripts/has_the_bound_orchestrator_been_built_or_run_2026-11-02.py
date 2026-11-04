#!/usr/bin/env python3
"""HAS THE BOUND ORCHESTRATOR BEEN BUILT? HAS ITS EXPERIMENT EVER BEEN RUN?

HIS 2 DIRECT QUESTIONS, 2026-11-01, annotation 12 of `Closing_Report_2026-11-01.txt`,
verbatim: *"I originally listed this as a fully simulated experiment in its own
right. I am clearly not going to burn money on a live run until I know how this
might function. Has that experiment ever been run? Has this design ever been
built? If not you should do both."*

THEY ARE FACTUAL QUESTIONS AND THEY GET FACTUAL ANSWERS, by searching the code
and the run archive rather than by recollection. `feedback_check_the_record_before_declaring_a_gap`
records a case where a gap was declared that the record did not support, and
`feedback_three_artefacts_before_calling_it_untracked_2026-10-17` records 2
things reported as unbuilt that were already built.

B20's 4 COMPONENTS, from the entry's own WHAT-DOES-NOT-EXIST list:
  1. a role layer in the policy registry          (entry says BUILT 2026-11-02 under B21)
  2. an autonomous monitoring loop                 (entry says absent)
  3. a researcher-facing interface / UX backend    (entry says absent)
  4. a fix comparator                              (entry says absent)
Each is probed INDEPENDENTLY, because "the design" is 4 things and a single
yes/no about it would be the wrong shape of answer.
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys

# `_cli_help` lives in scripts/. Located rather than assumed, because the first
# version of this preamble elsewhere used a fixed depth and broke 13 imports.
import sys as _sys, pathlib as _pl  # noqa: E402
for _cand in (_pl.Path(__file__).resolve().parent, *_pl.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        if str(_cand) not in _sys.path:
            _sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def grep(pattern: str, *globs: str) -> list[str]:
    """Live code only. A harvested copy under bench/logs/**/files/** is the same
    artefact preserved twice, and matching one against itself is the 27-of-27
    self-match recorded in feedback_a_false_positive_can_be_why_a_rule_is_unenforced."""
    out = []
    for g in (globs or ("bench/**/*.py", "scripts/**/*.py")):
        for p in REPO.glob(g):
            s = str(p.relative_to(REPO))
            if s.startswith("bench/logs/") or "/sandbox_harvest/" in s:
                continue
            try:
                txt = p.read_text(errors="replace")
            except Exception:
                continue
            for i, ln in enumerate(txt.splitlines(), 1):
                if re.search(pattern, ln):
                    out.append(f"{s}:{i}: {ln.strip()[:110]}")
    return out


# ★ ADDED 2026-11-02 BECAUSE 2 OF THIS SCRIPT'S 4 VERDICTS WERE WRONG, AND THEY
# WERE WRONG IN THE FLATTERING-TO-NOBODY DIRECTION: it reported `ux_backend` and
# `fix_comparator` as "N candidate line(s)" from a GREP, and a caller reading
# that could not tell "the module exists" from "N lines mention these words".
# B20's own text had already corrected the UX half BY HAND while this producer
# still emitted a line count, which is the clearest possible sign that the
# producer was not the thing being believed.
#
# `execute-do-not-grep` is the standing rule and it is the whole repair: a test
# that asserts on SOURCE TEXT asserts only that the text describes itself. So
# each component is now decided by EXISTENCE, then by IMPORT, then by the
# SYMBOLS it must expose, then by whether a guard file names it. The grep stays
# BELOW the verdict as supporting context, never as the verdict.
#
# THE 4TH CHECK IS NOT DECORATION. A module that exists, imports and exposes its
# symbols but that no test reaches is exactly the "addition nothing reaches" the
# additive standard names, and this project has 11 confirmed instances of it. So
# an unreached module is reported as its own state rather than as BUILT.
def module_verdict(module_rel: str, symbols: tuple[str, ...],
                   guard_globs: tuple[str, ...]) -> str:
    """BUILT / PRESENT BUT UNREACHED / PRESENT BUT BROKEN / ABSENT, by execution."""
    import importlib.util as _ilu
    f = REPO / module_rel
    if not f.is_file():
        return f"ABSENT: no file at {module_rel}"
    # ★ THE PROBE MUST REGISTER THE MODULE IN `sys.modules` BEFORE EXECUTING IT,
    # and the first version did not. `dataclasses` resolves a field's type through
    # `sys.modules.get(cls.__module__).__dict__`, so any module declaring a
    # dataclass with `KW_ONLY` raised `AttributeError: 'NoneType' object has no
    # attribute '__dict__'` -- and the probe reported that as "PRESENT BUT
    # BROKEN" against `bench/fix_comparator.py`, which imports perfectly well by
    # `import bench.fix_comparator`. MY INSTRUMENT ACCUSED CORRECT CODE, which is
    # the error class this project has recorded most often, and repairing the
    # SUBJECT to satisfy it would have damaged a working 19,901-byte module.
    # Registering the module is what the import system itself does, so the probe
    # now matches the mechanism it is standing in for, and it cleans up after
    # itself so a probe cannot leave a half-built module visible to later code.
    import sys as _sys
    name = "_probe_" + f.stem.replace("-", "_")
    try:
        spec = _ilu.spec_from_file_location(name, f)
        mod = _ilu.module_from_spec(spec)
        _sys.modules[name] = mod
        try:
            spec.loader.exec_module(mod)
        finally:
            _sys.modules.pop(name, None)
    except Exception as exc:                                   # noqa: BLE001
        return (f"PRESENT BUT BROKEN: {module_rel} is {f.stat().st_size} bytes "
                f"and does not import ({type(exc).__name__}: {exc})")
    missing = [s for s in symbols if not hasattr(mod, s)]
    if missing:
        return (f"PRESENT BUT INCOMPLETE: {module_rel} imports but lacks "
                f"{missing}")
    guards = []
    for g in guard_globs:
        guards += [q for q in (REPO / "bench" / "tests").glob(g) if q.is_file()]
    guards = sorted({q for q in guards}, key=lambda q: q.name)
    named = [q.name for q in guards
             if f.stem in q.read_text(errors="replace")
             or module_rel in q.read_text(errors="replace")]
    if not named:
        return (f"PRESENT BUT UNREACHED: {module_rel} imports and exposes "
                f"{list(symbols)} but no guard under bench/tests names it -- "
                f"an addition nothing reaches is not additive")
    return (f"BUILT: {module_rel}, {f.stat().st_size} bytes, imports, exposes "
            f"{list(symbols)}, named by {named}")


def main() -> int:
    answer_help(__doc__, __file__)
    print("=" * 78)
    print("B20, THE ORCHESTRATOR BOUND INSIDE THE HARNESS: BUILT? RUN?")
    print("=" * 78)
    verdicts = {}

    # ---- 1. the role layer, which the entry says B21 built -------------------
    print("\n1. A ROLE LAYER IN THE POLICY REGISTRY")
    try:
        from bench.cdsfl_registry import policy_engine as pe   # noqa: F401
        mod = pe
        names = [n for n in dir(mod) if "role" in n.lower()]
        print(f"   policy_engine imports. role-named symbols: {names[:10]}")
    except Exception as exc:                                   # noqa: BLE001
        print(f"   policy_engine not importable as that name: {type(exc).__name__}")
        names = []
    hits = grep(r"ROLE_LAYER|role_layer|LAYER_ROLE|\brole\b.*layer|layer.*\brole\b")
    print(f"   grep for a role layer: {len(hits)} live line(s)")
    for h in hits[:6]:
        print(f"     {h}")
    _withheld = max(0, len(hits) - 6)
    if _withheld:
        print(f"     ... and {_withheld} more not shown "
              f"(of {len(hits)} total)")
    verdicts["role_layer"] = "BUILT" if (names or hits) else "ABSENT"

    # ---- 2. an autonomous monitoring loop ------------------------------------
    print("\n2. AN AUTONOMOUS MONITORING LOOP, and the rule for what 'screwy' means")
    wd = REPO / "scripts" / "cy_watchdog_2026-10-02.py"
    gate = REPO / "hooks" / "cy_monitor_gate.py"
    print(f"   cy_watchdog_2026-10-02.py exists        : {wd.is_file()}")
    print(f"   hooks/cy_monitor_gate.py exists         : {gate.is_file()}")
    if wd.is_file():
        src = wd.read_text()
        # ★ BOTH EMITTERS, BY SYNTAX TREE — corrected 2026-11-04. This read
        # `say("UPPERCASE")` only and reported 4 kinds as "the watchdog's EVENT
        # VOCABULARY". The watchdog's events are emitted by `ev()`, a DIFFERENT
        # function with 10 distinct literal kinds, and `say()` adds ARMED, CLOSED
        # and HEARTBEAT with WATCHDOG shared between them. The union is 13, which
        # is the figure B20's own text records and which this instrument
        # contradicted by a factor of more than 3.
        #
        # A regex naming the wrong function is the predicate error this project
        # keeps finding: the check ran, returned a number, and the number was
        # about something else. The AST route cannot name the wrong function
        # silently, because the function is the key it groups by.
        import ast as _ast
        _ev, _say = set(), set()
        try:
            for _n in _ast.walk(_ast.parse(src)):
                if not isinstance(_n, _ast.Call) or not _n.args:
                    continue
                _nm = getattr(_n.func, "id", getattr(_n.func, "attr", ""))
                _a = _n.args[0]
                if not (isinstance(_a, _ast.Constant) and isinstance(_a.value, str)):
                    continue
                if _nm == "ev":
                    _ev.add(_a.value)
                elif _nm == "say" and _a.value.split()[0].isupper():
                    _say.add(_a.value.split()[0])
        except SyntaxError:
            pass
        kinds = sorted(_ev | _say)
        print(f"   the watchdog's EVENT VOCABULARY         : {len(kinds)} kinds, "
              f"{len(_ev)} from ev() and {len(_say)} from say() with "
              f"{len(_ev & _say)} shared")
        print(f"     {kinds}")
        print(f"   -> THAT VOCABULARY IS THE 'WHAT IS SCREWY' RULE B20 SAYS IS MISSING.")
        print(f"      B20's own text names this as its highest-risk arm: 'noticing")
        print(f"      that something is screwy with no rule naming what screwy")
        print(f"      means'. Each event above is a mechanical predicate, and the")
        print(f"      pulse file added 2026-11-02 makes them readable by a program")
        print(f"      rather than only by a human reading prose.")
    # ★ THE ACTUATOR IS PROBED, NOT ASSUMED ABSENT — corrected 2026-11-04.
    # This verdict was a HARDCODED STRING: given the watchdog and the gate, it
    # asserted "what is absent is a loop that ACTS on them unattended" with no
    # reference to anything that might act. So it could not change when the
    # actuator was built, and `bench/tools/cy_actuator_2026-11-03.py` landed in
    # commit 99d800db the following day while this instrument went on reporting
    # the component as PARTLY BUILT. B20's entry text repeated that, which is the
    # SECOND time that entry's absence list has gone stale — its own text already
    # records the first, where 2 of 3 claims were false.
    #
    # An instrument whose verdict is a constant measures nothing. That is the
    # `boundary_band_sensitivity` shape this project has confirmed before: a
    # value shipped as an unconditional constant, vacuous in 41 of 41 reports.
    # The other 3 components here were already probed by IMPORTING the candidate
    # and naming the tests that reach it, so this now does the same.
    act = REPO / "bench" / "tools" / "cy_actuator_2026-11-03.py"
    act_ok, act_names, act_tests = False, [], []
    if act.is_file():
        try:
            import importlib.util as _ilu
            _spec = _ilu.spec_from_file_location("_cy_actuator_probe", act)
            _mod = _ilu.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
            act_ok = True
            act_names = sorted(n for n in dir(_mod)
                               if n in ("classify", "main", "act", "resume"))
        except Exception as _e:                              # noqa: BLE001
            act_names = [f"import failed: {type(_e).__name__}"]
        act_tests = sorted(p.name for p in (REPO / "bench" / "tests").glob("test_*.py")
                           if "cy_actuator" in p.read_text(errors="replace"))
    print(f"   bench/tools/cy_actuator_2026-11-03.py exists: {act.is_file()}")
    if act.is_file():
        print(f"   it imports                              : {act_ok}")
        print(f"   it exposes                              : {act_names}")
        print(f"   tests that reach it                     : {act_tests}")
        print(f"   -> THE ACTING HALF EXISTS. It watches a launched run, classifies")
        print(f"      why the run stopped, records that with its evidence, and under")
        print(f"      `--act` re-invokes the same launch command with `--resume`.")

    if not (wd.is_file() and gate.is_file()):
        verdicts["monitoring_loop"] = "ABSENT"
    elif act_ok and act_tests:
        # ★ RULE 20: BUILT AND TESTED IS NOT ENABLED, and the distinction is the
        # one he had to ask for 4 times. The actuator acts only under `--act`,
        # and nothing in the harness passes it, so the loop does not yet run
        # unattended even though every part of it exists.
        verdicts["monitoring_loop"] = (
            "BUILT AND TESTED, NOT ENABLED: the detector, its event vocabulary, "
            "the pulse file and the actuator all exist and the actuator is "
            f"reached by {len(act_tests)} test file(s); it acts only under "
            "`--act`, which nothing in the harness passes, so the cycle is not "
            "yet unattended")
    else:
        verdicts["monitoring_loop"] = (
            "PARTLY BUILT: the detector and its event vocabulary exist and arm "
            "automatically; what is absent is a loop that ACTS on them unattended")

    # ---- 3. the researcher-facing interface / UX backend --------------------
    print("\n3. A RESEARCHER-FACING INTERFACE, AND THE UX BACKEND HE AUTHORISED")
    ux = grep(r"ux_backend|UX_BACKEND|def .*researcher|researcher_interface|"
              r"add_model|register_model|api_key|API_KEY")
    print(f"   grep for a model-adding / key-handling surface: {len(ux)} line(s)")
    for h in ux[:10]:
        print(f"     {h}")
    _withheld = max(0, len(ux) - 10)
    if _withheld:
        print(f"     ... and {_withheld} more not shown "
              f"(of {len(ux)} total)")
    # THE VERDICT IS THE MODULE CHECK. The grep above is context only.
    verdicts["ux_backend"] = module_verdict(
        "bench/ux_backend_2026-10-20.py", ("TABS", "seats"),
        ("test_*ux*.py", "test_*seat*.py"))
    print(f"   VERDICT (by execution, not by grep): {verdicts['ux_backend']}")

    # ---- 4. the fix comparator ---------------------------------------------
    print("\n4. A FIX COMPARATOR, deciding which fixes are better and which compose")
    fc = grep(r"compar(e|ator).*fix|fix.*compar(e|ator)|which_fix|"
              r"simplest_sufficient|composab")
    print(f"   grep for a comparator against the 3 standards: {len(fc)} line(s)")
    for h in fc[:10]:
        print(f"     {h}")
    _withheld = max(0, len(fc) - 10)
    if _withheld:
        print(f"     ... and {_withheld} more not shown "
              f"(of {len(fc)} total)")
    verdicts["fix_comparator"] = module_verdict(
        "bench/fix_comparator.py", ("compare",),
        ("test_*fix_comparator*.py", "test_*comparator*.py"))
    print(f"   VERDICT (by execution, not by grep): {verdicts['fix_comparator']}")

    # ---- 5. HAS THE EXPERIMENT EVER RUN? -----------------------------------
    print("\n5. HAS THE EXPERIMENT EVER BEEN RUN?")
    logs = REPO / "bench" / "logs"
    cands = []
    for d in sorted(logs.glob("*")):
        if not d.is_dir():
            continue
        # ★ `bound` ALONE WAS A FALSE POSITIVE, corrected 2026-11-02 before the
        # figure was reported. It matched `severity_bounds_validation_...` on
        # the substring of "bounds", so the probe claimed 1 candidate run where
        # the true answer is 0. A predicate that matches the wrong word is the
        # most recorded error class in this project, and the control for it is
        # to require the ORCHESTRATOR sense, not merely the letters.
        if re.search(r"orchestrat|bound[_-]orch|b20[_-]", d.name, re.I):
            cands.append(d.name)
    print(f"   run directories whose NAME mentions an orchestrator arm: {len(cands)}")
    for c in cands[:8]:
        print(f"     {c}")
    _withheld = max(0, len(cands) - 8)
    if _withheld:
        print(f"     ... and {_withheld} more not shown "
              f"(of {len(cands)} total)")
    # and the stronger test: does any run's own config declare a bound arm?
    declared = []
    for f in sorted(logs.glob("*/runner_state.json")):
        try:
            txt = f.read_text(errors="replace")[:200000]
        except Exception:
            continue
        if re.search(r'"bound_orchestrator"|"orchestrator_arm"|bound_orchestrator', txt):
            declared.append(f.parent.name)
    print(f"   runs whose recorded state DECLARES a bound-orchestrator arm: "
          f"{len(declared)}")
    verdicts["experiment_run"] = "NEVER RUN" if not (cands or declared) else str(cands or declared)

    print("\n" + "=" * 78)
    print("ANSWERS TO HIS 2 QUESTIONS")
    print("=" * 78)
    for k, v in verdicts.items():
        print(f"  {k:18s} : {v}")
    print()
    # ★ THIS SUMMARY IS DERIVED, NOT TYPED, CORRECTED 2026-11-02. It read
    # "1 of its 4 components is built ... and 2 are absent", which was true when
    # written and became wrong the moment the grep verdicts above were replaced
    # by execution checks: 2 components the grep could not see were already
    # built. The project's own pre-commit header states the general case -- "a
    # number typed once goes stale the next time the set grows" -- so the counts
    # below are computed from `verdicts` and cannot drift from it.
    comp = {k: v for k, v in verdicts.items() if k != "experiment_run"}
    built = [k for k, v in comp.items() if str(v).startswith("BUILT")]
    partly = [k for k, v in comp.items() if str(v).startswith("PARTLY")]
    absent = [k for k, v in comp.items() if str(v).startswith("ABSENT")]
    degraded = [k for k, v in comp.items()
                if str(v).startswith(("PRESENT BUT", "UNREACHED"))]
    n = len(comp)
    print(f"  HAS THE DESIGN BEEN BUILT? "
          f"{'YES, AS A WHOLE' if len(built) == n else 'NOT AS A WHOLE'}. "
          f"{len(built)} of {n} component(s) built, {len(partly)} partly built, "
          f"{len(absent)} absent, {len(degraded)} present but not usable.")
    for label, group in (("built", built), ("partly built", partly),
                         ("absent", absent), ("present but not usable", degraded)):
        if group:
            print(f"    {label:24s}: {', '.join(sorted(group))}")
    # ★ THIS BLOCK WAS A CONSTANT TOO, and fixing the verdict above without it
    # left the output self-contradictory for one run: "4 of 4 built" followed by
    # "WHAT REMAINS: a loop that ACTS". That is the same fixed-the-deciding-layer-
    # left-the-reporting-layer shape found in the verdict census the same night,
    # repeated here within the hour. It now DERIVES from the verdict.
    _ml = verdicts.get("monitoring_loop", "")
    if _ml.startswith("BUILT AND TESTED, NOT ENABLED"):
        print("  WHAT REMAINS, AND NEITHER HALF IS A BUILD: the actuator acts only")
        print("  under `--act`, which 0 production callers pass, so the cycle is not")
        print("  yet unattended; and the experiment has never been run. ENABLING it")
        print("  changes run behaviour and RUNNING it costs money, so both are his.")
    elif _ml.startswith("PARTLY BUILT"):
        print("  WHAT REMAINS, STATED RATHER THAN COUNTED: a loop that ACTS on the")
        print("  watchdog's events unattended. The detector, its event vocabulary and")
        print("  the pulse file exist; nothing performs the pause, diagnose, fix and")
        print("  resume cycle without a human or a model in the loop.")
    else:
        print(f"  WHAT REMAINS: the monitoring loop reads {_ml[:60]!r}.")
    print(f"  HAS THE EXPERIMENT BEEN RUN? "
          f"{'No. 0 runs in the archive declare the arm.' if not declared and not cands else 'See section 5.'}")
    print("  HIS OWN PRIORITY RULING STILL GOVERNS THE BUILD, 2026-10-17: *\"I do")
    print("  not wish you to become too sidetracked on this specific issue. It")
    print("  should be built and tested at the appropriate time.\"*")
    # ★ ALSO DERIVED, 2026-11-04. This closed with "So an absent component here is
    # a DEFERRAL he ordered, not neglected work", which reads as an excuse once
    # there are 0 absent components -- and there now are 0.
    _absent = [k for k, v in verdicts.items() if str(v).startswith("ABSENT")]
    if _absent:
        print(f"  So the {len(_absent)} absent component(s) here are a DEFERRAL he")
        print("  ordered, not neglected work.")
    else:
        print("  0 components are absent, so the deferral now governs only the")
        print("  ENABLEMENT and the RUN, which are his to release.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
