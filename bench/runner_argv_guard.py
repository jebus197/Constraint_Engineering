"""Refuse to start a PAID experiment because of a typo or a `--help`.

WHY THIS EXISTS. On 2026-08-07 a cold-start drill — an agent given only this
repository's documentation and told to behave like an outside researcher — ran
``python3 bench/run_exp36_evidence.py --help``. That is the safest, most
conventional thing anyone does to an unfamiliar command-line script. On these
runners it was the thing that spent money: fifteen of the seventeen
``run_exp*.py`` scripts hand-parse ``sys.argv``, silently ignore anything they
do not recognise, and fall through to ``mode = "run"``, whose first action is a
live preflight dispatch to five paid models. The drill did it twice before
working out what was happening.

``docs/REPRODUCING.md`` pointed researchers at five of those scripts and said
"Most runners accept CLI flags", which was false and expensive.

This is the project's governing failure mode — a failure rendering as a
confident success — pointed in the most costly direction available: silence
where a refusal belonged, on the machine of someone who has not agreed to be
billed. The founder funds this project from borrowed money, and a stranger
reproducing it has agreed to even less.

WHAT IT DOES, and deliberately no more. Called as the first statement of
``main()``, before any credential is sourced or any model is contacted:

  * ``-h`` / ``--help`` / ``help``  -> print usage, exit 0.
  * any token the caller does not recognise -> print usage, exit 2.
  * anything else -> return, and the runner proceeds exactly as before.

It changes NOTHING about a valid invocation. It is a gate on the way in, not a
new argument parser: replacing fifteen hand-rolled parsers with ``argparse``
would alter the behaviour of historical experiment runners, and their recorded
results depend on that behaviour. The narrow fix is the correct one.
"""

from __future__ import annotations

import sys
from typing import Iterable, Optional, Sequence

_HELP = {"-h", "--help", "help", "-help", "--usage"}


def guard_argv(
    known: Iterable[str],
    usage: str,
    argv: Optional[Sequence[str]] = None,
    *,
    exit_fn=sys.exit,
    out=None,
) -> None:
    """Exit before any paid work if the arguments are help or unrecognised.

    ``known`` is the set of tokens this runner actually understands — its own
    flags and positional modes. Values that follow a flag (``--pattern star``)
    are NOT checked: a runner that accepts ``--pattern`` decides for itself
    whether ``star`` is valid, and it already does so, loudly, further down.

    ``exit_fn`` and ``out`` exist so the behaviour can be tested without
    terminating the test process.
    """
    argv = list(sys.argv[1:] if argv is None else argv)
    stream = out if out is not None else sys.stderr
    known = set(known)

    if any(a in _HELP for a in argv):
        print(usage, file=stream)
        exit_fn(0)
        return

    # Only tokens that LOOK like options are policed. A bare word is either a
    # positional mode the runner knows, or a value belonging to the flag before
    # it — and guessing which would make this guard reject valid invocations,
    # which is a worse failure than the one it fixes.
    unknown = [a for a in argv if a.startswith("-") and a not in known]
    if unknown:
        print(
            f"Unrecognised argument(s): {' '.join(unknown)}\n\n"
            f"{usage}\n\n"
            f"REFUSING TO START. This runner dispatches to paid models as soon "
            f"as it begins, so it stops on an argument it does not understand "
            f"rather than ignoring it and running anyway.",
            file=stream,
        )
        exit_fn(2)
        return
