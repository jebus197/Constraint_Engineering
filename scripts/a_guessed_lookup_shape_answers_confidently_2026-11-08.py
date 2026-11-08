#!/usr/bin/env python3
"""A guessed lookup shape returns a confident wrong answer, 5 times in 1 night.

WHY THIS EXISTS. On 2026-11-07 into 2026-11-08 this session asked 4 different
data structures for something using a key whose SHAPE it had assumed rather than
checked. Every one returned cleanly -- an empty string, an empty list, a zero --
and every one of those is indistinguishable from a real measurement. 2 of the 4
would have reached the founder as false statements, and 1 would have blocked his
morning report entirely.

THE POINT IS NOT THE COUNT, IT IS THAT BOTH FORMS ARE EXECUTABLE. Each case
below runs the WRONG call and the RIGHT call against the live structure and
prints both answers, so the error is demonstrated rather than recalled. That is
`execute-do-not-grep` applied to lookups: a producer and a consumer that
disagree about a key cannot be caught by reading either one, because each is
internally consistent.

WHAT MAKES THIS CLASS DANGEROUS. A wrong PATH raises. A wrong lookup SHAPE does
not: dict.get returns None, a missing store id returns "", a filtered list comes
back empty. The failure is silent and it is always in the reassuring direction --
"nothing found" reads as "nothing wrong".

NO RATE IS REPORTED. The denominator would be "lookups performed in a session",
which nothing counts, and inventing one is the defect this project recorded as a
figure with no producer. 5 named cases, each reproducible.

Exit 0 iff every case still reproduces BOTH answers.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
if not (REPO / "scripts").is_dir():
    REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")


def _load(name: str, rel: str):
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def case_store_key_vs_identifier():
    """`ticket_id` wants a BARE identifier; the item's own key carries a prefix."""
    m = _load("lk_mrb", "scripts/morning_report_build_2026-10-12.py")
    wrong, right = m.ticket_id("task:B20"), m.ticket_id("B20")
    return ("a store key where an identifier belongs",
            f'ticket_id("task:B20") -> {wrong!r}',
            f'ticket_id("B20")      -> {right!r}',
            bool(right) and not wrong,
            "measured 48 of 48 items as carrying no ticket id; a refusal built "
            "on it would have refused every item and withheld his report")


def case_nested_vs_flat():
    """The authored detail is keyed FLAT as `task:C0001`, not nested under `task`."""
    d = json.loads((REPO / "experimental_notes" / "data"
                    / "morning_report_decisions.json").read_text(encoding="utf-8"))
    wrong = (d.get("task") or {}).get("C0001")
    right = d.get("task:C0001")
    return ("a nested lookup on a flat mapping",
            "d['task']['C0001']  -> None (and 'task' is not even a key)",
            f"d['task:C0001']     -> a dict of {len(right)} fields"
            if right else "d['task:C0001'] -> MISSING",
            wrong is None and bool(right),
            "produced the claim that the entry has no authored detail at all, "
            "and from it a claim that his report mis-classifies it; both false")


def case_blocking_vs_cli():
    """Rule 30 is reachable only through its own function, not through `blocking`."""
    m = _load("lk_lint", "scripts/note_vagueness_lint.py")
    sample = next((p for p in sorted(
        (REPO / "experimental_notes").glob("*.md"))
        if m.undefined_project_terms(p)), None)
    if sample is None:
        return ("the blocking subset where the gate counts the total",
                "no note carries a Rule 30 finding", "", False,
                "the corpus no longer exercises this case")
    wrong = len([f for f in m.blocking(sample)
                 if f[1] == "undefined-project-term"])
    right = len(m.undefined_project_terms(sample))
    return ("the blocking subset where the gate counts the TOTAL",
            f"blocking({sample.name}) Rule-30 findings -> {wrong}",
            f"undefined_project_terms(...)             -> {right}",
            wrong == 0 and right > 0,
            "every note was cleared all night with the call that cannot see "
            "the rule, and 2 commits were refused on exactly it")


def case_pipeline_exit_code():
    """A pipeline's status is its LAST stage's, so `| tail` hides a failure."""
    with tempfile.TemporaryDirectory() as td:
        script = pathlib.Path(td) / "boom.py"
        script.write_text("import sys; sys.exit(1)\n", encoding="utf-8")
        piped = subprocess.run(
            f"{sys.executable} {script} | tail -1", shell=True,
            capture_output=True, text=True).returncode
        direct = subprocess.run([sys.executable, str(script)],
                                capture_output=True, text=True).returncode
    return ("a pipeline's exit code read as the command's",
            f"`cmd | tail -1` -> exit {piped}",
            f"`cmd`           -> exit {direct}",
            piped == 0 and direct == 1,
            "a guard run reporting 1 failed of 1,534 was called green, hiding "
            "a DONE marker that had lost its support")


def case_zsh_does_not_word_split():
    """`cmd $FILES` is 44 arguments in bash and 1 in zsh, which is this shell."""
    import shutil
    zsh = shutil.which("zsh")
    if not zsh:
        return ("an unquoted list passed to a command", "no zsh on this machine",
                "", False, "the case cannot be reproduced here")
    script = ("FILES='a b c'; "
              "printf 'args=%s\\n' \"$#\" >/dev/null; "
              "set -- $FILES; printf '%s' \"$#\"")
    unsplit = subprocess.run([zsh, "-c", script], capture_output=True,
                             text=True).stdout.strip()
    split = subprocess.run(["/bin/bash", "-c", script], capture_output=True,
                           text=True).stdout.strip()
    return ("an unquoted list passed to a command",
            f"zsh  `set -- $FILES` -> {unsplit} argument(s)",
            f"bash `set -- $FILES` -> {split} argument(s)",
            unsplit == "1" and split == "3",
            "44 test files went to pytest as 1 argument; it reported 'no tests "
            "ran' and exited 4, and the turn reported the guards as running")


CASES = [case_store_key_vs_identifier, case_nested_vs_flat,
         case_blocking_vs_cli, case_pipeline_exit_code,
         case_zsh_does_not_word_split]


def main() -> int:
    # ★ `--help` MUST NOT DO THE WORK. Added 2026-11-08: 8 scripts of this
    # date wrote files while answering `--help`, which
    # `bench/tests/test_help_never_acts_2026-09-11.py` forbids and which
    # `feedback_help_must_never_cost_money` records as 15 of 17 runners
    # billing for a help request. A parser is used rather than
    # `_cli_help.answer_help` because an unrecognised argument then exits 2
    # instead of being ignored, and because it cannot be made unreachable
    # under `python3 -m`, which is how 5 of 9 earlier repairs failed.
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    print("=" * 78)
    print("A GUESSED LOOKUP SHAPE ANSWERS CONFIDENTLY, AND IN THE REASSURING")
    print("DIRECTION. 5 CASES FROM 1 NIGHT, EACH RUN BOTH WAYS.")
    print("=" * 78)
    ok = 0
    for fn in CASES:
        label, wrong, right, reproduced, cost = fn()
        print(f"\n  {label}")
        print(f"      WRONG : {wrong}")
        print(f"      RIGHT : {right}")
        print(f"      reproduces today: {reproduced}")
        print(f"      what it cost    : {cost}")
        ok += bool(reproduced)
    print("\n" + "=" * 78)
    print(f"  cases still reproducing both answers: {ok} of {len(CASES)}")
    print("  NO RATE IS REPORTED. The denominator would be 'lookups performed")
    print("    in a session', which nothing counts; inventing one is the defect")
    print("    this project recorded as a figure with no producer.")
    print("  THE COMMON SHAPE: a wrong PATH raises, a wrong SHAPE returns")
    print("    empty. Empty is indistinguishable from a measurement, and it")
    print("    always reads as 'nothing wrong'.")
    print("  THE CHECK THAT WOULD HAVE CAUGHT ALL 5: before trusting a lookup,")
    print("    run it on an input whose answer is already known. Every case")
    print("    above is 2 lines of code away from being obvious.")
    print("=" * 78)
    return 0 if ok == len(CASES) else 1


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
