#!/usr/bin/env python3
"""Answer `--help` without doing the work first.

MEASURED 2026-09-11, and the measurement is the reason this exists.

`scripts/measurement_scripts_only_2026-09-11.py --run` executes every script it
classes as a measurement with `--help` first, and reports how many "did not
answer --help cleanly". It decided that on the EXIT CODE alone. A script with no
argument parser does not answer `--help` at all: it ignores the flag, runs its
entire measurement, and exits 0 -- which the survey read as a clean answer.

Requiring a `usage:` line instead of an exit code, over the 53 scripts the
survey classes as measurements:

    answered --help with a usage line : 23
    exited 0 but printed NO usage line: 30
    not answering: 30/53 = 56.6038%
      Wilson 95%          : [43.2654%, 69.0496%]  (statsmodels)
      Clopper-Pearson 95% : [42.2826%, 70.1608%]  (statsmodels/beta, and scipy
                                                   agrees to 1.1e-16)

Producing script: scripts/help_is_answered_2026-09-11.py.

WHY IT SURFACED AS A CLONE-ONLY FAILURE. In the maintainer's tree all 30 exited
0, because ignoring the flag and succeeding is indistinguishable from answering
it. In a fresh clone 2 of them failed -- `build_experiment_report.py` crashed on
an archived log that `.gitignore` excludes, and `check_model_keys.py` exited 1
because there is no .env -- and those 2 failures were 2 of the 3 that made task
A2's "a fresh clone is green" untrue. The other 28 were the same defect, silent.

WHY IT MATTERS BEYOND TIDINESS. The founder's own ruling on this class, after 15
of 17 runners billed a live dispatch on any unrecognised argument: a `--help`
must never cost money. None of these 30 spend money, but several run the full
measurement they exist to produce -- minutes of work, and in 1 case a git walk
over the whole history -- in answer to a request to be told what they do.

THE CONTRACT. `answer_help` is a no-op unless `-h` or `--help` is present in
argv, so a script's behaviour with any other arguments, including none, is
unchanged by construction. None of the 30 read `sys.argv` or use `argparse` at
all, verified before the flag was claimed, so nothing can be consuming `-h` as
data.
"""
from __future__ import annotations

import pathlib
import sys
import textwrap

HELP_FLAGS = ("-h", "--help")


def usage_line_present(blob: str) -> bool:
    """Did this output ANSWER a help request?

    The single definition, imported by both `help_is_answered_2026-09-11.py` and
    the survey in `measurement_scripts_only_2026-09-11.py`. Two copies of this
    predicate would be 2 representations of 1 truth with no comparator, which is
    the shape `execute-do-not-grep` names -- and the survey already carried the
    weaker EXIT-CODE version of it, which is how 30 scripts passed while
    ignoring the flag.

    `argparse` prints a line beginning `usage:`; so does `answer_help` above. A
    script that never parses the flag prints no such line.
    """
    return any(ln.lstrip().lower().startswith("usage:")
               for ln in (blob or "").splitlines())


def answer_help(doc: str | None, path: str | None = None,
                argv: list[str] | None = None,
                takes_no_arguments: bool = True) -> None:
    """Answer `-h`/`--help`, and refuse anything else, for a script with no parser.

    Returns without doing anything when argv is EMPTY, which is what makes this
    safe to place at the top of a script that parses nothing: a plain run
    reaches exactly the code it reached before.

    AND AN UNRECOGNISED ARGUMENT EXITS 2 RATHER THAN BEING IGNORED.
    `bench/tests/test_operational_scripts.py` already holds this rule, in these
    words: "a script that accepts `--fix-timestamps` and does nothing with it is
    the 118-day no-op again". Its check is a TEXT scan for `sys.argv`, so a
    script that reads argv only through THIS helper reads as argv-free and
    inherits a pass it has not earned -- a scanner resolving 1 form of a thing
    and reporting a false zero for the other, which is the shape this session
    has now met 10 times. The rule is therefore enforced here, in the code both
    forms go through, and the text scan is taught to see this call as well.

    `takes_no_arguments=False` disables the refusal for a caller that parses its
    own positionals afterwards. No caller needs it today; it exists so adding one
    does not require weakening the default.
    """
    args = sys.argv[1:] if argv is None else argv
    name = pathlib.Path(path or sys.argv[0]).name
    if any(a in HELP_FLAGS for a in args):
        print(f"usage: {name} [-h]")
        print()
        body = textwrap.dedent(doc or "").strip()
        print(body if body else "(this script carries no description)")
        print()
        print("This script takes no arguments; run it with none to do its work.")
        raise SystemExit(0)
    if takes_no_arguments and args:
        print(f"usage: {name} [-h]", file=sys.stderr)
        print(f"{name}: unrecognised argument(s): {' '.join(args)}",
              file=sys.stderr)
        print("This script takes no arguments. Refusing rather than ignoring "
              "them.", file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    # 1st call: real argv. An unrecognised argument exits 2; `--help` prints and
    # exits 0; no arguments returns.
    answer_help(__doc__, __file__)
    # Then, having established there were no arguments, print the usage anyway --
    # a library run directly should say what it is, not sit silent, so it does
    # not become a member of the set it exists to empty.
    answer_help(__doc__, __file__, argv=["--help"])
