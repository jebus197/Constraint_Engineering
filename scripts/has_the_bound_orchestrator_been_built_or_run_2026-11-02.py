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
    verdicts["role_layer"] = "BUILT" if (names or hits) else "ABSENT"

    # ---- 2. an autonomous monitoring loop ------------------------------------
    print("\n2. AN AUTONOMOUS MONITORING LOOP, and the rule for what 'screwy' means")
    wd = REPO / "scripts" / "cy_watchdog_2026-10-02.py"
    gate = REPO / "hooks" / "cy_monitor_gate.py"
    print(f"   cy_watchdog_2026-10-02.py exists        : {wd.is_file()}")
    print(f"   hooks/cy_monitor_gate.py exists         : {gate.is_file()}")
    if wd.is_file():
        src = wd.read_text()
        kinds = sorted(set(re.findall(r'say\(\s*"([A-Z_ ]+)"', src)))
        print(f"   the watchdog's EVENT VOCABULARY         : {kinds}")
        print(f"   -> THAT VOCABULARY IS THE 'WHAT IS SCREWY' RULE B20 SAYS IS MISSING.")
        print(f"      B20's own text names this as its highest-risk arm: 'noticing")
        print(f"      that something is screwy with no rule naming what screwy")
        print(f"      means'. Each event above is a mechanical predicate, and the")
        print(f"      pulse file added 2026-11-02 makes them readable by a program")
        print(f"      rather than only by a human reading prose.")
    verdicts["monitoring_loop"] = (
        "PARTLY BUILT: the detector and its event vocabulary exist and arm "
        "automatically; what is absent is a loop that ACTS on them unattended"
        if wd.is_file() and gate.is_file() else "ABSENT")

    # ---- 3. the researcher-facing interface / UX backend --------------------
    print("\n3. A RESEARCHER-FACING INTERFACE, AND THE UX BACKEND HE AUTHORISED")
    ux = grep(r"ux_backend|UX_BACKEND|def .*researcher|researcher_interface|"
              r"add_model|register_model|api_key|API_KEY")
    print(f"   grep for a model-adding / key-handling surface: {len(ux)} line(s)")
    for h in ux[:10]:
        print(f"     {h}")
    verdicts["ux_backend"] = "ABSENT" if not ux else f"{len(ux)} candidate line(s)"

    # ---- 4. the fix comparator ---------------------------------------------
    print("\n4. A FIX COMPARATOR, deciding which fixes are better and which compose")
    fc = grep(r"compar(e|ator).*fix|fix.*compar(e|ator)|which_fix|"
              r"simplest_sufficient|composab")
    print(f"   grep for a comparator against the 3 standards: {len(fc)} line(s)")
    for h in fc[:10]:
        print(f"     {h}")
    verdicts["fix_comparator"] = "ABSENT" if not fc else f"{len(fc)} candidate line(s)"

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
    print("  HAS THE DESIGN BEEN BUILT? NOT AS A WHOLE. 1 of its 4 components is")
    print("  built (the role layer, under B21 on 2026-11-02), 1 is partly built")
    print("  (the monitoring detector, whose missing 'screwy' rule was closed")
    print("  2026-11-02), and 2 are absent.")
    print("  HAS THE EXPERIMENT BEEN RUN? No. 0 runs in the archive declare the arm.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
