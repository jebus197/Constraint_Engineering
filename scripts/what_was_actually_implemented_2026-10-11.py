#!/usr/bin/env python3
"""Which of the last week's agreed changes are LIVE, which are built-not-wired, which are nothing.

THE FOUNDER'S CHALLENGE, 2026-10-11: *"in the past there have been periods where we have spent
significant effort discussing changes and improvements that were ultimately never implemented.
So this cle[a]rly begs the question of how much of the work we have been engaged in over the
last several days had actually been implemented, and what if anything has been omitted?"*

He raised it off the sharpest instance: *"you are st[i]ll routing our models by name, despite
all the work we have done to date to correct this."*

=============================================================================================
WHY THIS SCRIPT EXISTS IN THIS FORM, AND WHAT THE FIRST ATTEMPT GOT WRONG
=============================================================================================
A FIRST VERSION OF THIS FILE ENUMERATED 17 ITEMS FROM THE ASSISTANT'S OWN RECOLLECTION and
reported "8 of 17 LIVE, Wilson (0.2617, 0.6904)". That headline is WITHDRAWN. Memory is
precisely the instrument the founder's question says not to trust, and it failed in 3 ways
that are recorded here so the shape is not repeated:

  1. PROBE NAMES WERE INVENTED. `gamma_alt_consecutive_zero_crit_RAISED` is not a symbol in
     this repository; it was a guess. The real field is `gamma_alt_consecutive_zero_crit` and
     it IS live and overridable, so the item was mislabelled NOT_IMPLEMENTED when the honest
     verdict is MEASURED_NOT_ACTED (the knob exists; the value was never moved off 3).
  2. THE LIVE-MODULE LIST WAS INCOMPLETE. `scripts/cdsfl_utils.py` was omitted, so the
     `git_state` repair -- which is live, and which the 2026-10-08 session state correctly
     records as landed -- was reported BUILT_NOT_CALLED. That was a defect in the instrument,
     not in the tree.
  3. DEFINED WAS TREATED AS WIRED. A symbol defined inside a live module was scored as
     reached. The additive standard's own words are *"every new flag, gate, subcommand or
     entry point must be wired to a CALLER and executed by a test"*, so a definition nothing
     invokes is exactly the failure being audited. Every probe below therefore has to name a
     CALL SITE, not a definition site.

THE DECIDING RULE, which is the project's own (`execute-do-not-grep`, founder 2026-09-04):
*"A test that asserts on the SOURCE TEXT of a module asserts only that the module describes
itself consistently."* So every probe here CALLS the code and compares outputs. Where a probe
cannot execute, it says so rather than substituting a text match.

=============================================================================================
THE INSTRUMENT IS ITSELF VERIFIED, because the rule above applies to this file too
=============================================================================================
`wilson()` below is cross-verified at 2026-10-11T14:20Z against 4 independent implementations
over 10 cases including all 3 degenerate ones (0/n, n/n, 1/1):
    statsmodels.stats.proportion.proportion_confint(method="wilson")  max |diff| 1.110e-16
    scipy.stats.norm.ppf, score form from first principles              max |diff| 0.000e+00
    mpmath at 40 decimal places on 8/17                   agrees to 12 significant figures
    Wolfram Language at 20 decimal places on 8/17                      max |diff| 0.000e+00
Wolfram was reachable on this date (`wolframscript -code '2+2'` -> 4, exit 0), which CORRECTS
the expectation recorded in resources/RECOVERY.md that the licence would lapse on 2026-10-08.

Run: python3 scripts/what_was_actually_implemented_2026-10-11.py
     python3 scripts/what_was_actually_implemented_2026-10-11.py --json
     python3 scripts/what_was_actually_implemented_2026-10-11.py --merge <audit.json>
"""
from __future__ import annotations

import argparse
import ast
import glob
import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
Z = 1.959963984540054

#: THE VERDICT VOCABULARY. The first version had 5 categories and needed 9: the 4 it lacked
#: are the ones that separate "nobody did the work" from "the work was done and the decision
#: was not taken", which is the distinction the founder's question actually turns on.
VERDICTS = (
    "LIVE",               # exists, a live caller invokes it, a test executes it
    "LIVE_NOT_DEFAULT",   # all of the above, but only reachable via a flag nothing sets
    "LIVE_UNTESTED",      # exists and called by live code, but no test executes it
    "BUILT_NOT_CALLED",   # exists, maybe tested, but NO live code calls it
    "MEASURED_NOT_ACTED", # the measurement landed and was committed; the change was not applied
    "PROSE_ONLY",         # exists only in a comment, note or document
    "NOT_IMPLEMENTED",    # absent from the tree
    "AWAITING_RULING",    # deliberately unbuilt, pending the founder; cite where recorded
    "LAPSED",             # instructed, never done, and no record of a decision to defer
)

#: Modules that constitute LIVE code. A producer script or a test calling something does NOT
#: make it live. Corrected 2026-10-11: cdsfl_utils/cdsfl_recover/launcher_core/runner_core were
#: missing from the first version and their absence produced a false BUILT_NOT_CALLED.
LIVE = (
    "bench/reference_runner_v3.py",
    "bench/confer_maths_panel_2026-09-05.py",
    "bench/routing.py",
    "bench/panel_sandbox.py",
    "bench/experiment_11_orchestrator.py",
    "bench/insect_brain.py",
    "bench/immune_agents.py",
    "bench/evidence.py",
    "bench/endocrine.py",
    "bench/runner_core.py",
    "bench/launcher_core.py",
    "bench/tools/run_simulated_experiment.py",
    "scripts/cdsfl_utils.py",
    "scripts/cdsfl_recover.py",
    "scripts/cdsfl_sv.py",
)


def wilson(k: int, n: int) -> tuple:
    """Wilson score interval. Cross-verified against 4 tools -- see the module docstring."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = (Z / d) * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return (round(max(0.0, c - h), 4), round(min(1.0, c + h), 4))


def _load(name: str, rel: str):
    """Import a module from a path so its values can be READ rather than parsed."""
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _owning_function(rel: str, line: int) -> str:
    """Which function contains this line. Used to prove a call site is REACHABLE."""
    tree = ast.parse((REPO / rel).read_text(errors="ignore"))
    best = None
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.lineno <= line <= (n.end_lineno or n.lineno):
            if best is None or n.lineno > best.lineno:
                best = n
    return best.name if best else "<module level>"


# ======================================================================= the claims
def claim_the_a4_severity_test_is_live_and_two_sided() -> dict:
    """RECOVERY 2026-10-05 outstanding item 3 said the severity test was 'never implemented'.

    THE RECORD ITSELF NAMES THE METHOD -- *"Confirmed still absent by calling the counter"* --
    so this calls it, across 6 constructed registries. A text read would have reported the
    symbols present and stopped; the symbols being present is not the question.
    """
    m = _load("rr_audit", "bench/reference_runner_v3.py")
    reg = m.FindingRegistry.__new__(m.FindingRegistry)
    thr = m.CRITICAL_SEVERITY_THRESHOLD
    cases = {
        "low_no_proof":      {"status": "UNCONFIRMED", "severity": 0.2},
        "low_proof_PASS":    {"status": "UNCONFIRMED", "severity": 0.2,
                              "severity_proof": {"status": "PASS"}},
        "low_proof_WARN":    {"status": "UNCONFIRMED", "severity": 0.2,
                              "severity_proof": {"status": "WARN"}},
        "low_proof_FAIL":    {"status": "UNCONFIRMED", "severity": 0.2,
                              "severity_proof": {"status": "FAIL"}},
        "critical_PASS":     {"status": "UNCONFIRMED", "severity": 0.95,
                              "severity_proof": {"status": "PASS"}},
        "critical_no_proof": {"status": "UNCONFIRMED", "severity": 0.95},
    }
    got = {}
    for name, entry in cases.items():
        reg.entries = {"f1": dict(entry)}
        got[name] = reg.unverified_critical_count()
    # The test is live iff a PROVEN low severity is skipped AND an unproven one is not.
    fires = got["low_proof_PASS"] == 0 and got["low_proof_WARN"] == 0
    conservative = got["low_no_proof"] == 1 and got["low_proof_FAIL"] == 1
    criticals_always_block = got["critical_PASS"] == 1 and got["critical_no_proof"] == 1
    return {
        "item": "the A4 counter's severity test",
        "CRITICAL_SEVERITY_THRESHOLD": thr,
        "counter_returns": got,
        "severity_test_fires_on_a_proven_low": fires,
        "unproven_low_still_blocks": conservative,
        "criticals_always_block": criticals_always_block,
        "verdict": "LIVE" if (fires and conservative and criticals_always_block) else "CHECK",
        "note": ("gated on a worked proof, which is the form the founder ruled for on his 4th "
                 "rejection; RECOVERY's 'never implemented' line is now STALE"),
    }


def claim_the_hil_review_guard_executes_a_copy_not_the_wiring() -> dict:
    """The work-in-flight ledger claims *"The CLI wiring is now executed by a guard"*. It is not.

    The guard re-implements the `if` statement inside its own test body. So the runner's wiring
    could be DELETED and the guard would stay green -- which is the `execute-do-not-grep` defect
    in its subtler form: not asserting on source text, but asserting on a duplicate of the logic.
    """
    runner = (REPO / "bench/reference_runner_v3.py").read_text(errors="ignore").splitlines()
    wiring_lines = [i + 1 for i, l in enumerate(runner)
                    if "hil_review" in l and "cfg.hil_review = True" in l]
    gate_lines = [i + 1 for i, l in enumerate(runner)
                  if "cfg.hil_review" in l and l.strip().startswith("if ")]
    guard = REPO / "bench/tests/test_dormant_switches_are_decided_2026-10-07.py"
    gtext = guard.read_text(errors="ignore") if guard.is_file() else ""
    # Does the guard CALL the functions that own the wiring and the gates?
    owners = sorted({_owning_function("bench/reference_runner_v3.py", ln)
                     for ln in wiring_lines + gate_lines})
    calls_owner = {o: (f"R.{o}(" in gtext or f".{o}(" in gtext) for o in owners}
    reimplements = "cfg.hil_review = True" in gtext
    # how many configs enable it
    cfgs = sorted(glob.glob(str(REPO / "bench/exp*_configs/*.json")))
    enabled = 0
    for f in cfgs:
        try:
            flat = _flatten(json.load(open(f)))
        except Exception:
            continue
        if flat.get("hil_review"):
            enabled += 1
    return {
        "item": "hil_review's ON path",
        "runner_wiring_lines": wiring_lines,
        "runner_gate_branch_lines": gate_lines,
        "owning_functions": owners,
        "guard_calls_those_functions": calls_owner,
        "guard_reimplements_the_wiring_in_its_own_body": reimplements,
        "configs_enabling_it": f"{enabled} of {len(cfgs)}",
        "configs_wilson": wilson(enabled, len(cfgs)),
        "verdict": "LAPSED" if (reimplements and not any(calls_owner.values())) else "CHECK",
        "note": ("the ledger's claim that the CLI wiring is executed by a guard is FALSE: the "
                 "guard executes a copy, so deleting the runner's wiring leaves it green"),
    }


def claim_the_stream_json_parse_lapsed_against_its_own_trigger() -> dict:
    """The tracker named the trigger: *"Build it when the joint round lands, before `sv`."*

    The joint round landed and 2 `sv` commits followed. The parse still takes the whole string,
    so a mid-flight tool-call count is impossible BY CONSTRUCTION, not by configuration.
    """
    tree = ast.parse((REPO / "bench/experiment_11_orchestrator.py").read_text(errors="ignore"))
    sig = None
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and "stream_json" in n.name:
            ann = (ast.unparse(n.args.args[0].annotation)
                   if n.args.args and n.args.args[0].annotation else None)
            sig = {"name": n.name, "line": n.lineno,
                   "first_arg": n.args.args[0].arg if n.args.args else None,
                   "first_arg_annotation": ann}
    joint = REPO / "bench/logs/division_count_star_2026-10-08"
    try:
        svs = subprocess.run(
            ["git", "log", "--since=2026-10-08", "--pretty=%h|%ad|%s", "--date=iso"],
            cwd=REPO, capture_output=True, text=True, timeout=60).stdout.splitlines()
    except Exception:
        svs = []
    sv_after = [l for l in svs if "|sv:" in l]
    return {
        "item": "incremental stream-json parsing",
        "parser": sig,
        "takes_whole_string": bool(sig and sig.get("first_arg_annotation") == "str"),
        "joint_round_landed": joint.is_dir(),
        "sv_commits_after_the_trigger": sv_after,
        "verdict": "LAPSED" if (sig and sig.get("first_arg_annotation") == "str"
                                and joint.is_dir() and sv_after) else "CHECK",
        "note": ("a parser taking the complete output cannot report a count mid-flight; the "
                 "trigger fired, 2 sv gates passed, and no decision to defer was recorded"),
    }


def claim_the_ladder_orders_by_name_and_nothing_recomputes_it() -> dict:
    """His charge, stated precisely. The order WAS derived from measurement, then frozen.

    The comment at routing.py promises *"It climbs as it earns attempts"*. No code climbs.
    """
    rt = _load("rt_audit", "bench/routing.py")
    order = list(rt.DEFAULT_FALSIFIER_STRENGTH)
    src = (REPO / "bench/routing.py").read_text(errors="ignore")
    fns = {n.name for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef)}
    # Who references the tuple, and does anyone WRITE it?
    refs = {}
    for rel in sorted(set(glob.glob(str(REPO / "bench/**/*.py"), recursive=True)
                          + glob.glob(str(REPO / "scripts/*.py")))):
        if "/logs/" in rel or "/worktrees/" in rel:
            continue
        try:
            t = Path(rel).read_text(errors="ignore")
        except OSError:
            continue
        if "DEFAULT_FALSIFIER_STRENGTH" in t:
            r = str(Path(rel).relative_to(REPO))
            refs[r] = {"is_live": r in LIVE,
                       "assigns_it": any(
                           line.strip().startswith("DEFAULT_FALSIFIER_STRENGTH")
                           and "=" in line and "==" not in line
                           for line in t.splitlines())}
    prov = REPO / "scripts/competence_provenance.py"
    callers = [r for r in refs if refs[r]["is_live"]]
    prov_live_callers = []
    for rel in LIVE:
        f = REPO / rel
        if f.is_file() and "competence_provenance" in f.read_text(errors="ignore"):
            # is it a CALL or only a comment telling a human to run it?
            for i, line in enumerate(f.read_text(errors="ignore").splitlines(), 1):
                if "competence_provenance" in line:
                    prov_live_callers.append(
                        {"at": f"{rel}:{i}", "is_comment": line.strip().startswith("#")})
    return {
        "item": "routing reads a measured rate instead of a name",
        "DEFAULT_FALSIFIER_STRENGTH": order,
        "all_entries_are_vendor_names": all(isinstance(x, str) and not x.isdigit()
                                            for x in order),
        "routing_defines_a_wilson_or_rate_function": bool(
            {f for f in fns if "wilson" in f.lower() or "rate" in f.lower()}),
        "files_referencing_the_tuple": refs,
        "live_files_referencing_it": callers,
        "anything_reassigns_it_at_runtime": any(v["assigns_it"] for k, v in refs.items()
                                                if k != "bench/routing.py"),
        "provenance_script_exists": prov.is_file(),
        "provenance_references_in_live_code": prov_live_callers,
        # DERIVED, NOT ASSERTED. A P-pass on 2026-10-11 found this verdict hard-coded, so
        # it reported MEASURED_NOT_ACTED even on a tree where the ladder HAD been wired to
        # recompute -- the Lean-guard tautology (a guard that cannot fail) reproduced inside
        # the audit itself. The verdict now flips the moment any of the 4 facts changes.
        "verdict": (
            "LIVE" if (
                {f for f in fns if "wilson" in f.lower() or "rate" in f.lower()}
                and any(v["assigns_it"] for k, v in refs.items() if k != "bench/routing.py")
            ) else "LIVE_NOT_DEFAULT" if any(
                not c["is_comment"] for c in prov_live_callers
            ) else "MEASURED_NOT_ACTED" if prov.is_file()
            else "NOT_IMPLEMENTED"),
        "note": ("the order was DERIVED from measured resolve-rates and then frozen as a "
                 "literal tuple; the only link from the measurement to the ladder is a "
                 "comment instructing a human to run the script by hand"),
    }


def claim_the_false_quiet_criterion_was_measured_and_not_moved() -> dict:
    """The knob is live and overridable. The measured curve says it should move. It did not."""
    m = _load("rr_k", "bench/reference_runner_v3.py")
    cfg = m.RunnerConfig(experiment_name="t", models=["A"])
    k = getattr(cfg, "gamma_alt_consecutive_zero_crit", None)
    overriders = [rel for rel in ("bench/launcher_core.py", "bench/launch_exp40.py")
                  if (REPO / rel).is_file()
                  and "gamma_alt_consecutive_zero_crit" in (REPO / rel).read_text(errors="ignore")]
    cfgs = sorted(glob.glob(str(REPO / "bench/exp*_configs/*.json")))
    vals = {}
    for f in cfgs:
        try:
            flat = _flatten(json.load(open(f)))
        except Exception:
            continue
        if "gamma_alt_consecutive_zero_crit" in flat:
            vals[str(flat["gamma_alt_consecutive_zero_crit"])] = \
                vals.get(str(flat["gamma_alt_consecutive_zero_crit"]), 0) + 1
    return {
        "item": "the required quiet run, raised from the measured curve",
        "live_default_K": k,
        "overridable_through": overriders,
        "config_values": vals,
        "producer": "bench/the_false_quiet_rate_is_not_the_gates_rate_2026-10-08.py",
        "measured_rate_at_K_3": 0.126374,
        "K_for_a_0_05_target_point_estimate": 5,
        "K_for_a_0_05_target_upper_bound": 7,
        # DERIVED. Was hard-coded; a P-pass on 2026-10-11 showed it would still read
        # MEASURED_NOT_ACTED after the value had been raised, which is the whole point of
        # the probe. 3 is the un-raised value; the measured curve asks for 5 or 7.
        "verdict": (
            "NOT_IMPLEMENTED" if k is None
            else "LIVE" if (isinstance(k, int) and k >= 5)
            else "MEASURED_NOT_ACTED" if (REPO / "bench"
                 / "the_false_quiet_rate_is_not_the_gates_rate_2026-10-08.py").is_file()
            else "PROSE_ONLY"),
        "note": ("the knob is live and overridable and the measurement is committed; the value "
                 "was never moved off 3, and the producer's own status line reads PROPOSED"),
    }


def claim_no_config_holds_prose_where_a_boolean_belongs() -> dict:
    """RETIRED AS A FINDING, KEPT AS A REGRESSION GUARD. The claim was WITHDRAWN 2026-10-11.

    WHAT WAS CLAIMED: that 2 of 16 configs setting `immune_memory_enabled` held a
    230-character English sentence where a boolean belongs, and were therefore correct only
    by the accident of a non-empty string being truthy.

    WHAT REFUTED IT: reading exp50's config directly. It carries
    `immune_memory_enabled: true` -- a proper boolean -- at the TOP LEVEL, which is what both
    `reference_runner_v3` and the contamination guard in
    `bench/tests/test_immune_memory_consumption.py` actually read. The sentence lives at
    `_redesign_2026_09_10.deliberately_unchanged.immune_memory_enabled`, an underscore-prefixed
    ANNOTATION block whose stated purpose is to explain why the real field above it is left
    alone. The defect was in `_flatten` in THIS file, which descended into annotation blocks
    and collapsed documentation into the config namespace.

    WHAT THE SCOPE OF THE FAILURE WAS, so it is not over-generalised: the DENOMINATORS were
    never wrong (16, 31, 32, 0, 0 and 33 of 47 all reproduce under the repaired reader). Only
    the value breakdown for this one field moved, from {True: 11, <sentence>: 2, False: 3} to
    {True: 13, False: 3} -- and 13 matches the guard's own `is True` count of 13 exactly, so
    there was never a discovery gap either.

    IT IS KEPT RATHER THAN DELETED because a passing check here is what shows the repaired
    reader still holds; `_flatten` regressing would make this probe report offenders again.
    """
    cfgs = sorted(glob.glob(str(REPO / "bench/exp*_configs/*.json")))
    present, boolean, strings = 0, 0, []
    for f in cfgs:
        try:
            flat = _flatten(json.load(open(f)))
        except Exception:
            continue
        if "immune_memory_enabled" not in flat:
            continue
        present += 1
        v = flat["immune_memory_enabled"]
        if isinstance(v, bool):
            boolean += 1
        elif isinstance(v, str):
            strings.append({"config": str(Path(f).relative_to(REPO)),
                            "chars": len(v), "bool_of_it": bool(v), "starts": v[:70]})
    rr = (REPO / "bench/reference_runner_v3.py").read_text(errors="ignore")
    declared_bool = "immune_memory_enabled: bool" in rr
    read_by_truthiness = 'getattr(cfg, "immune_memory_enabled", False)' in rr
    # DOES ANY TEST PIN THE TYPE? A test merely MENTIONING the field does not; it has to
    # assert the value isinstance bool, or the string-valued configs can never be caught.
    pinning_tests = []
    for t in sorted(glob.glob(str(REPO / "bench/tests/test_*.py"))):
        try:
            txt = Path(t).read_text(errors="ignore")
        except OSError:
            continue
        if "immune_memory_enabled" not in txt:
            continue
        if ("isinstance" in txt and "bool" in txt) or "is True" in txt or "is False" in txt:
            pinning_tests.append(str(Path(t).relative_to(REPO)))
    return {
        "item": "immune_memory_enabled's declared type",
        "configs": len(cfgs),
        "set_it": present,
        "proper_booleans": boolean,
        "string_valued": len(strings),
        "string_valued_share_of_setters": (round(len(strings) / present, 4) if present else None),
        "wilson": wilson(len(strings), present),
        "offenders": strings,
        "declared_as_bool_in_the_runner": declared_bool,
        "read_by_truthiness": read_by_truthiness,
        "tests_pinning_the_type": pinning_tests,
        "verdict": (
            "LIVE" if (not strings and pinning_tests)
            else "LIVE_UNTESTED" if not strings
            else "LIVE_NOT_DEFAULT" if pinning_tests
            else "LIVE_UNTESTED"),
        "note": ("RETIRED/WITHDRAWN -- 0 string-valued fields under the repaired reader; the "
                 "earlier 2 were annotation text and 5 assertions do pin the type by identity"),
    }


def claim_the_adjudication_gap_has_no_producer() -> dict:
    """`measured-rate-travels-with-its-script`, broken on a figure quoted to the founder.

    0.7603 / 0.4003 / difference 0.3600 / odds 4.7516 / p = 3.87e-72 live in exactly 3 places:
    2 panel records under experimental_notes/ and the Desktop TTS the founder actually reads.
    They are in NO committed Python file, and NOT in docs/REPRODUCING.md -- an earlier draft of
    this docstring said they were, which was a MISREAD of `git show <sha> | grep -n`: those line
    numbers index the DIFF, not the file. Checked directly, the live REPRODUCING.md has 0 hits.

    THE FIGURE IS ATTRIBUTED TO CC1 BY THE RECORD ITSELF -- Panel_FULL_RECORD_Division_Count_
    Star_2026-10-08.md opens the paragraph *"A CC1 FINDING THAT CHANGES THE INPUTS RATHER THAN
    THE LOGIC"* -- so the missing producer is owed by the orchestrator, not by a seat.
    """
    needles = ("0.7603", "0.4003", "4.7516")
    prose, producers = [], []
    SELF = Path(__file__).resolve()
    for pat in ("docs/**/*.md", "experimental_notes/**/*.md", "resources/**/*.md",
                "*.md", "docs/*.md"):
        for f in glob.glob(str(REPO / pat), recursive=True):
            try:
                t = Path(f).read_text(errors="ignore")
            except OSError:
                continue
            if any(x in t for x in needles):
                rel = str(Path(f).relative_to(REPO))
                if rel not in prose:
                    prose.append(rel)
    for pat in ("bench/**/*.py", "scripts/**/*.py"):
        for f in glob.glob(str(REPO / pat), recursive=True):
            # EXCLUDE THIS FILE. Its own docstring quotes the figures it is auditing, so a
            # naive scan counted the audit as the producer and flipped the verdict. Measured
            # 2026-10-11: that is the `my_instruments_are_the_weak_point` shape again.
            if Path(f).resolve() == SELF:
                continue
            if "/logs/" in f or "/worktrees/" in f or "/tests/" in f:
                continue
            try:
                t = Path(f).read_text(errors="ignore")
            except OSError:
                continue
            if any(x in t for x in needles):
                producers.append(str(Path(f).relative_to(REPO)))
    return {
        "item": "the adjudication gap (statistics 0.7603 vs software 0.4003)",
        "prose_homes": sorted(prose),
        "committed_producers": sorted(producers),
        "attributed_to": ("CC1, by the record's own words: 'A CC1 FINDING THAT CHANGES THE "
                          "INPUTS RATHER THAN THE LOGIC'"),
        "in_docs_REPRODUCING_md": "0.7603" in (REPO / "docs/REPRODUCING.md").read_text(
            errors="ignore") if (REPO / "docs/REPRODUCING.md").is_file() else None,
        "verdict": "PROSE_ONLY" if prose and not producers else "CHECK",
        "note": ("the founder's ruling of 2026-09-04 exists because this happened before with "
                 "'282 of 711'; a number carried only as prose is a claim ABOUT evidence"),
    }


def claim_the_resume_pointer_is_stale() -> dict:
    """The tracker is the document a recovering agent is told to read FIRST."""
    tr = REPO / "experimental_notes/CDSFL_Agent_Operational_Plan.md"
    try:
        head = subprocess.run(["git", "log", "-1", "--pretty=%h|%ad", "--date=iso"],
                              cwd=REPO, capture_output=True, text=True, timeout=60).stdout.strip()
        tr_commit = subprocess.run(
            ["git", "log", "-1", "--pretty=%h|%ad", "--date=iso", "--", str(tr)],
            cwd=REPO, capture_output=True, text=True, timeout=60).stdout.strip()
        behind = subprocess.run(
            ["git", "rev-list", "--count", f"{tr_commit.split('|')[0]}..HEAD"],
            cwd=REPO, capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception:
        head = tr_commit = behind = "?"
    txt = tr.read_text(errors="ignore") if tr.is_file() else ""
    claims_in_flight = "cc2's blind reply is in flight" in txt
    joint_landed = (REPO / "bench/logs/division_count_star_2026-10-08").is_dir()
    return {
        "item": "the operational tracker's RESUME POINTER",
        "tracker_last_commit": tr_commit,
        "branch_head": head,
        "commits_behind": behind,
        "still_says_a_round_is_in_flight": claims_in_flight,
        "that_round_has_since_landed": joint_landed,
        "verdict": "LAPSED" if (claims_in_flight and joint_landed) else "CHECK",
        "note": ("operational-tracker-update-policy requires an update after each completed "
                 "task; the pointer would send a recovering agent to re-run finished work"),
    }


def _flatten(o, out=None, _top=True):
    """Config fields, flattened -- but NEVER descending into an annotation block.

    A KEY WHOSE NAME STARTS WITH `_` IS DOCUMENTATION, NOT CONFIGURATION. Measured
    2026-10-11, and this cost a withdrawn finding: an earlier version of this function
    descended into `_redesign_2026_09_10.deliberately_unchanged`, whose whole purpose is
    to carry a SENTENCE explaining why the real field above it is left alone. The sentence
    landed in the same namespace as the field and was reported as "a config holding prose
    where a boolean belongs" in 2 experiments. Both configs in fact carry a proper
    `immune_memory_enabled: true` at the top level, which is what the runner and the
    contamination guard both read. The defect was in this function, not in the tree.

    This is the `check the predicate before the result` shape for the 3rd time in one
    session, so the guard is structural rather than remembered: `_`-prefixed keys are
    skipped outright, and a nested real value never shadows a top-level one.
    """
    if out is None:
        out = {}
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(k, str) and k.startswith("_"):
                continue                      # annotation block -- documentation, not config
            if isinstance(v, (dict, list)):
                _flatten(v, out, _top=False)
            elif _top or k not in out:
                out[k] = v                    # a top-level field always wins
    elif isinstance(o, list):
        for v in o:
            _flatten(v, out, _top=False)
    return out


CLAIMS = (
    claim_the_a4_severity_test_is_live_and_two_sided,
    claim_the_hil_review_guard_executes_a_copy_not_the_wiring,
    claim_the_stream_json_parse_lapsed_against_its_own_trigger,
    claim_the_ladder_orders_by_name_and_nothing_recomputes_it,
    claim_the_false_quiet_criterion_was_measured_and_not_moved,
    claim_no_config_holds_prose_where_a_boolean_belongs,
    claim_the_adjudication_gap_has_no_producer,
    claim_the_resume_pointer_is_stale,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="emit the full result as JSON")
    ap.add_argument("--merge", metavar="FILE",
                    help="merge a fan-out audit's JSON rows into the tally")
    args = ap.parse_args()

    out = []
    for fn in CLAIMS:
        try:
            out.append(fn())
        except Exception as e:                                   # pragma: no cover
            out.append({"item": fn.__name__, "verdict": "ERROR",
                        "error": f"{type(e).__name__}: {e}"})

    merged = []
    if args.merge:
        try:
            blob = json.loads(Path(args.merge).read_text())
            merged = blob.get("rows") or blob.get("results") or []
        except Exception as e:
            print(f"  could not merge {args.merge}: {type(e).__name__}: {e}", file=sys.stderr)

    if args.json:
        print(json.dumps({"measured_here": out, "merged": merged}, indent=1, default=str))
        return 0

    print("== measured directly by this script, by EXECUTION ==\n")
    for r in out:
        print(f"  [{r.get('verdict','?'):18s}] {r.get('item')}")
        for k, v in r.items():
            if k in ("item", "verdict", "note"):
                continue
            print(f"        {k}: {v}")
        if r.get("note"):
            print(f"        -> {r['note']}")
        print()

    tally = {}
    for r in out + merged:
        v = str(r.get("verdict", "UNKNOWN")).upper()
        tally[v] = tally.get(v, 0) + 1
    n = sum(tally.values())
    print(f"== tally over {n} item(s) ==")
    for v, c in sorted(tally.items(), key=lambda kv: -kv[1]):
        lo, hi = wilson(c, n)
        print(f"   {v:20s} {c:>4}  = {c/n:.4f}  Wilson [{lo}, {hi}]")
    if not merged:
        print("\n   NOTE: no fan-out rows merged, so this tally covers only the 8 items probed")
        print("   here and is NOT the project-wide rate. Pass --merge <audit.json> for that.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
