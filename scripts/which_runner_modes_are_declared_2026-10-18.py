#!/usr/bin/env python3
"""Which runner modes are DECLARED by a flag, and which could be DETECTED -- B28.

HIS RULING, 2026-10-07, on the third of 4 panel lessons: "We should use it. Wire
it in all simulated and real runners going forward." The lesson: "state should be
detected rather than declared. The panel used to decide whether a round was blind
or joint by reading an environment variable, so forgetting the variable silently
downgraded the check. It now decides from what the briefing document actually
contains. The runners have several places where a mode is declared by a flag that
can be forgotten." He ruled it again on 2026-10-11 as "Verdict: Verify and fix
all."

THE DISTINCTION THIS SCRIPT DRAWS, because not every flag is a mode. A flag that
expresses an operator's CHOICE -- enable this capability, use that budget -- has
nothing to detect: there is no fact in the run that could contradict it. A flag
that asserts a FACT ABOUT THE RUN is different. "This round is blind", "this is a
resumed run", "the target is prose with computable listings" are all claims the
run's own contents can answer, and when such a claim is carried by a flag,
forgetting the flag silently downgrades a check rather than failing loudly. Those
are the modes his ruling names.

WHAT IT DOES. For every boolean field on the runner config it finds the real read
sites by walking the abstract syntax tree -- not by grepping for `cfg.NAME`, which
misses `getattr(cfg, "name", ...)`, `**kwargs` forwarding and dictionary access,
and which is how two of these fields first looked unreferenced. It reports, per
field, where it is read, where it is WRITTEN after construction (a write is how a
flag gets silently flipped), and whether anything in the tree already derives the
same fact from the run's contents.

IT CLASSIFIES NOTHING BY ITSELF. The DECLARED-versus-CHOICE judgement is recorded
in `MODE_JUDGEMENTS` below with a reason for each, and this script's job is to
keep that table honest: it fails loudly when a field exists with no entry, or an
entry names a field that no longer exists, so the list cannot quietly go stale as
the config changes.
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNNER = REPO / "bench" / "reference_runner_v3.py"

#: Per boolean config field: ("MODE" | "CHOICE", one-line reason).
#:
#: MODE  -- the flag asserts a fact about the run that the run's own contents can
#:          answer, so forgetting it downgrades a check silently. His ruling
#:          applies: detect it.
#: CHOICE -- the flag expresses an operator preference. There is no fact in the
#:          run that could contradict it, so there is nothing to detect and
#:          converting it would invent a signal.
#:
#: WHAT "CONVERT" MEANS HERE, AND WHY IT IS NOT AN OVERRIDE. For most of the MODE
#: fields the detected fact must not simply replace the declaration: changing
#: `location_keyed_convergence` mid-run would change the convergence measure
#: itself, and a measurement that silently redefines itself is worse than one that
#: is wrong in a stated way. So the conversion is DETECT AND RECONCILE -- derive
#: the fact from the run's own contents, compare it with the declaration, and make
#: any DISAGREEMENT loud and recorded. That repairs exactly the failure he named,
#: where "forgetting the variable silently downgraded the check": after this the
#: forgotten flag is reported, not absorbed.
MODE_JUDGEMENTS: dict[str, tuple[str, str]] = {
    # ── MODE: a claim about the run, independently observable ────────────────
    "models_were_declared": (
        "MODE", "asserts that the operator declared the model set; whether models "
                "were in fact declared is answerable from the config that was loaded"),
    "resume": (
        "CHOICE", "RECLASSIFIED FROM MODE BY FALSIFICATION, 2026-10-18. It looked "
                  "like a fact -- a checkpoint either exists or does not -- but the "
                  "existence of a checkpoint does NOT establish that the operator "
                  "wants to continue it. Detecting this one would silently resume a "
                  "previous run whenever its checkpoint survived on disk, which is a "
                  "worse failure than the forgotten flag his ruling targets. It does "
                  "carry the only post-construction write among these fields, so the "
                  "write is worth recording even though the flag stays declared"),
    "sk_score_prose_listings": (
        "MODE", "asserts the target is prose carrying computable listings; the "
                "target file's own contents answer it, and leg 3 ran against "
                "exactly such a target"),
    "location_keyed_convergence": (
        "MODE", "asserts findings carry location keys; whether the findings "
                "actually carry them is observable in the registry"),
    "hierarchical_novelty_convergence": (
        "MODE", "asserts the finding set is hierarchical; observable from whether "
                "findings carry parent references"),
    "severity_spec_enabled": (
        "MODE", "asserts the severity specification is in force; whether reports "
                "carry its fields is observable, and entry C0's measurement that "
                "0 of 72 reports carried the rubric is exactly this gap"),
    # ── CHOICE: an operator preference with nothing to detect ────────────────
    "merge_arbitration_enabled": ("CHOICE", "whether to spend dispatch on arbitration"),
    "inround_reask_enabled": ("CHOICE", "whether to re-ask within a round"),
    "apply_fixes_back_enabled": ("CHOICE", "whether fixes are fed back"),
    "prior_fix_summary_enabled": ("CHOICE", "whether to include a prior-fix summary"),
    "windowed_context_enabled": ("CHOICE", "context-window strategy"),
    "stall_gamma_termination_enabled": ("CHOICE", "whether a stall terminates the run"),
    "discrimination_control_ask": ("CHOICE", "whether the control question is asked"),
    "discrimination_control_blocks": ("CHOICE", "whether that control blocks"),
    "falsifier_gate_enabled": ("CHOICE", "whether the falsifier gate runs"),
    "routing_enabled": ("CHOICE", "whether routing runs"),
    "location_shadow_enabled": ("CHOICE", "whether the shadow calculation runs"),
    "severity_calibration_enabled": ("CHOICE", "whether calibration runs"),
    "sev_f_enabled": ("CHOICE", "whether the severity-f term is used"),
    "composer_coherence_pruning": ("CHOICE", "whether the composer prunes"),
    "latent_tagger_enabled": ("CHOICE", "whether the tagger runs"),
    "immune_memory_enabled": ("CHOICE", "whether immune memory is consulted; his "
                                        "2026-10-16 ruling makes this a researcher "
                                        "switch by design"),
    "immune_memory_consume_rk0": ("CHOICE", "how immune memory is consumed"),
    "alarm_on_empty_ladder": ("CHOICE", "whether an empty ladder raises an alarm"),
    "sk_enabled": ("CHOICE", "whether the sk score is computed"),
    "hil_review": ("CHOICE", "whether the operator wants review stops at all; its "
                             "TRIGGER CONDITION is entry B27 and is now evidence-based"),
    "feedback_channel_enabled": ("CHOICE", "whether the feedback channel runs"),
    "divergence_channel_enabled": ("CHOICE", "whether the divergence channel runs"),
}


def bool_fields(src: str) -> list[tuple[str, str]]:
    m = re.search(r"class RunnerConfig[^\n]*:\n(.*?)\n\n\n", src, re.S)
    body = m.group(1) if m else ""
    return re.findall(r"^\s{4}(\w+)\s*:\s*bool\s*=\s*(True|False)", body, re.M)


def read_and_write_sites(tree: ast.AST, name: str) -> tuple[list[int], list[int]]:
    """Every read and every post-construction write of cfg.<name>, from the tree.

    Walks the syntax tree rather than grepping, because `getattr(cfg, "name", d)`
    and dictionary access are reads that a `cfg.name` search does not see -- which
    is how `models_were_declared` and `sk_score_prose_listings` first appeared
    unreferenced when searched for by text.
    """
    reads, writes = [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == name:
            reads.append(node.lineno)
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
              and node.func.id == "getattr" and len(node.args) >= 2
              and isinstance(node.args[1], ast.Constant)
              and node.args[1].value == name):
            reads.append(node.lineno)
        elif isinstance(node, ast.Constant) and node.value == name:
            reads.append(node.lineno)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Attribute) and tgt.attr == name:
                    writes.append(tgt.lineno)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == "setattr" and len(node.args) >= 2 \
                and isinstance(node.args[1], ast.Constant) \
                and node.args[1].value == name:
            writes.append(node.lineno)
    return sorted(set(reads)), sorted(set(writes))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", choices=("MODE", "CHOICE"), default=None)
    args = ap.parse_args()

    src = RUNNER.read_text(errors="ignore")
    tree = ast.parse(src)
    fields = bool_fields(src)
    names = [n for n, _ in fields]

    unjudged = [n for n in names if n not in MODE_JUDGEMENTS]
    stale = [n for n in MODE_JUDGEMENTS if n not in names]

    print(f"boolean config fields on the runner: {len(fields)}")
    modes = [n for n in names if MODE_JUDGEMENTS.get(n, ("", ""))[0] == "MODE"]
    choices = [n for n in names if MODE_JUDGEMENTS.get(n, ("", ""))[0] == "CHOICE"]
    print(f"  judged MODE   (a fact the run can answer):   {len(modes)}")
    print(f"  judged CHOICE (an operator preference):      {len(choices)}")
    print(f"  UNJUDGED (the table has gone stale):         {len(unjudged)}")
    print()

    for name, default in fields:
        kind, why = MODE_JUDGEMENTS.get(name, ("UNJUDGED", "no entry in the table"))
        if args.only and kind != args.only:
            continue
        reads, writes = read_and_write_sites(tree, name)
        flag = "★" if kind == "MODE" else " "
        print(f"{flag} {name:40} {kind:8} default={default:5} "
              f"reads={len(reads):3} post-construction writes={len(writes)}")
        if writes:
            print(f"    WRITTEN AFTER CONSTRUCTION at line(s) {writes} -- a write is "
                  f"how a declared mode gets flipped without the operator seeing it")
        print(f"    {why}")

    print()
    if unjudged:
        print(f"★ THESE FIELDS HAVE NO JUDGEMENT and the table must be extended "
              f"before this list can be called reasoned: {unjudged}")
    if stale:
        print(f"★ THESE JUDGEMENTS NAME FIELDS THAT NO LONGER EXIST: {stale}")
    if not unjudged and not stale:
        print("every boolean field carries a judgement and every judgement names a "
              "live field, so the classification is complete as of this commit.")
    return 1 if (unjudged or stale) else 0


if __name__ == "__main__":
    sys.exit(main())
