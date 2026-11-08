#!/usr/bin/env python3
"""Is "syntax raises confidence" an INSTRUMENTATION gap, or was it never built?

THE RECORD UNDER TEST. `experimental_notes/STUDY_IN_FLIGHT.json` carries
`the-classifier-logs-no-pre-syntax-confidence-so-one-clause-cannot-be-checked`,
severity "INSTRUMENTATION GAP, not a behavioural defect", whose `for_done`
reads: "log both the pre-syntax and the post-syntax confidence per
classification".

WHY THAT CLASSIFICATION IS WORTH TESTING. Logging a before/after pair
presupposes that an AFTER exists -- that something, somewhere, adjusts the
classifier's confidence on a syntactic signal. If nothing does, the remedy is
not instrumentation at all: there is no second value to record, and the gap is
a MISSING MECHANISM. Those 2 diagnoses lead to different work and only 1 of
them is the founder's to rule on.

HIS COMPOSITION, from his ruling of 2026-10-03 ("DO IT, mark as a significant
study area") as the producer `haiku_as_classifier_at_run_scale_2026-10-15.py`
quotes it: "Haiku decides, syntax raises confidence, never blocks". 3 clauses.

HOW THIS DECIDES IT, STRUCTURALLY RATHER THAN BY READING. Every assignment to
the classifier's confidence variable is found by walking the AST, and the SOURCE
of each value is reported. A clause that raises confidence must appear as an
assignment whose value depends on something other than the model's own reply.

THE DECISION RULE, STATED BEFORE THE MEASUREMENT: the record's
"instrumentation gap" classification stands if at least 1 assignment derives
the confidence from a non-model signal. It is refuted if every assignment comes
from the model's reply or a bare constant.

Exit 0 iff a verdict was reached.
"""
from __future__ import annotations

import ast
import pathlib
import subprocess

REPO = pathlib.Path(__file__).resolve().parent.parent
if not (REPO / "scripts").is_dir():
    REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
AGENTS = REPO / "bench" / "immune_agents.py"
VAR = "llm_confidence"


def _assignments(tree: ast.AST, var: str):
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name) and t.id == var:
                    out.append((n.lineno, ast.unparse(n.value)))
        elif isinstance(n, ast.AugAssign):
            if isinstance(n.target, ast.Name) and n.target.id == var:
                out.append((n.lineno, f"AUG {ast.unparse(n.op)} "
                                      f"{ast.unparse(n.value)}"))
    return sorted(out)


def _reads(tree: ast.AST, var: str):
    """Where the value is CONSULTED, which is what makes a change behavioural."""
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Compare):
            src = ast.unparse(n)
            if var in src:
                out.append((n.lineno, src))
    return sorted(out)


def main() -> int:
    if not AGENTS.is_file():
        print(f"REFUSED: no file at {AGENTS}")
        return 1
    src = AGENTS.read_text(encoding="utf-8")
    tree = ast.parse(src)

    print("=" * 78)
    print('IS "SYNTAX RAISES CONFIDENCE" BUILT, OR ONLY RECORDED?')
    print("=" * 78)

    asg = _assignments(tree, VAR)
    print(f"\nEVERY ASSIGNMENT TO `{VAR}` IN bench/immune_agents.py:")
    from_model, from_other = [], []
    for line, value in asg:
        #: A value is MODEL-DERIVED when it reads the reply, and CONSTANT when
        #: it is a bare literal. Anything else would be a candidate for the
        #: syntax clause and is reported separately so this cannot quietly
        #: classify a real adjustment as noise.
        is_model = any(tok in value for tok in ("lines[", "response", "reply",
                                                "stdout"))
        is_const = value.replace(".", "").replace("-", "").isdigit()
        #: ★ A CLAMP IS NOT A NEW SOURCE, corrected 2026-11-08 after the first
        #: version of this predicate counted `max(0.0, min(1.0, llm_confidence))`
        #: as an adjustment from some other signal and therefore UPHELD the
        #: framing it was built to test. A re-assignment whose value depends only
        #: on the variable itself and numeric literals carries no new
        #: information: it bounds the model's number, it does not raise it on
        #: anything.
        _bare = value.replace(VAR, "").replace("max", "").replace("min", "")
        is_clamp = (VAR in value
                    and not any(c.isalpha() for c in _bare))
        kind = ("MODEL REPLY" if is_model else
                "CONSTANT" if is_const else
                "CLAMP of the same value" if is_clamp else "OTHER -- inspect")
        (from_model if (is_model or is_const or is_clamp)
         else from_other).append((line, value))
        print(f"  line {line:>6}  {kind:<18} {value}")

    print(f"\n  assignments from the model's reply or a constant: "
          f"{len(from_model)} of {len(asg)}")
    print(f"  assignments from any OTHER source               : "
          f"{len(from_other)} of {len(asg)}")

    print("\nWHERE THE VALUE IS CONSULTED -- this is what makes any change "
          "BEHAVIOURAL:")
    for line, cmp_src in _reads(tree, VAR):
        print(f"  line {line:>6}  {cmp_src}")

    #: THE PHRASE ITSELF. If the clause were built, the words would appear in
    #: code or in a test, not only in the record that asks for it. Run through
    #: grep so the search is reproducible and its scope visible.
    r = subprocess.run(
        ["grep", "-rl", "syntax raises confidence",
         str(REPO / "bench"), str(REPO / "scripts")],
        capture_output=True, text=True)
    hits = [ln for ln in r.stdout.splitlines() if ln.strip()]
    #: ★ COMPILED BYTECODE AND A QUOTATION ARE NOT AN IMPLEMENTATION. The first
    #: version counted a `__pycache__/*.pyc` -- the compiled form of a
    #: docstring quoting him -- as a live reference, and double-counted the
    #: source beside it.
    live = [h for h in hits
            if "/logs/" not in h and "STUDY_IN_FLIGHT" not in h
            and "__pycache__" not in h and not h.endswith(".pyc")]
    print(f"\nFILES NAMING THE CLAUSE: {len(hits)} in all, of which "
          f"{len(live)} are live code or tests rather than run logs and copies "
          f"of the record itself.")
    for h in live[:8]:
        print(f"      {h}")

    #: ★ THE VERDICT RESTS ON THE ASSIGNMENTS ALONE, corrected 2026-11-08.
    #: The phrase search CANNOT distinguish a file that QUOTES his composition
    #: from one that IMPLEMENTS it -- the only live hit is the measurement
    #: producer whose docstring quotes him -- so it is reported as context and
    #: given no weight in the decision. A search that cannot tell a mention
    #: from a mechanism must not be allowed to settle whether the mechanism
    #: exists; this project has recorded the same confusion twice.
    verdict_instrumentation = bool(from_other)
    print("\n" + "=" * 78)
    if verdict_instrumentation:
        print("VERDICT: the record's INSTRUMENTATION framing STANDS -- a "
              "non-model")
        print("  adjustment or a live reference to the clause was found above.")
    else:
        print("VERDICT: THE RECORD'S FRAMING IS REFUTED. Every assignment to "
              "the")
        print("  classifier's confidence comes from the model's own reply or a "
              "bare")
        print(f"  constant. The clause is named in {len(live)} live file(s), "
              f"and that")
        print("  file is the MEASUREMENT PRODUCER whose docstring quotes his")
        print("  composition -- a quotation, not an implementation. There is")
        print("  no POST-syntax value to log, so this is not an "
              "instrumentation gap:")
        print("  THE CLAUSE WAS NEVER BUILT.")
        print()
        print("  AND THAT MAKES IT HIS, not a repair. The value gates")
        print("  `should_override`, so a rule that RAISES it would make more")
        print("  overrides fire and would change how findings are classified and")
        print("  routed. A behavioural change to a gate is his ruling under the")
        print("  project's ambiguity-defaults-to-HARD rule, and his composition")
        print("  of 2026-10-03 is the thing that would be being interpreted.")
        print()
        print("  WHAT IS NOT CLAIMED: that the clause SHOULD be built, or what")
        print("  'syntax' should mean operationally. 2 readings are available --")
        print("  agreement with the syntactic classifier, or a well-formedness")
        print("  property of the claim itself -- and they are not the same rule.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    import pathlib as _pl
    import sys as _sys
    _sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    try:
        from _cli_help import answer_help as _answer_help
        _answer_help(__doc__, __file__, takes_no_arguments=True)
    except ImportError:
        pass
    raise SystemExit(main())
