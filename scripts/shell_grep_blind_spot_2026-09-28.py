#!/usr/bin/env python3
"""How many matching files does the SESSION'S `grep` never show the assistant?

FOUND 2026-09-28 by a subagent auditing something else, and it matters far beyond
that audit: `grep` in this session is a SHELL FUNCTION installed by Claude Code's
own shell snapshot, wrapping ugrep with `--ignore-files`. It therefore honours
`.gitignore` and silently skips `bench/logs/**` (353 MB, 5,840 files) and every
other ignored path. Nothing in the output says a file was skipped.

WHY IT IS NOT COSMETIC. This project's evidence lives under `bench/logs/`. A grep
that cannot see the archive will report "0 occurrences" of a term that occurs
hundreds of times there, and "0 occurrences" is exactly the shape of claim this
project treats as a finding.

THE FIRST ATTEMPT AT THIS MEASUREMENT WAS VACUOUS, and that is recorded here
rather than quietly fixed. It invoked the comparison through `zsh -ic`, a fresh
shell that never sources the snapshot, so `grep` there was already /usr/bin/grep:
it compared the real grep against itself and returned a reassuring 0 of 541
missed. A measurement whose control and treatment are the same thing measures
nothing. Both commands below therefore run in ONE shell, the same one the
assistant uses.
"""
from __future__ import annotations

import subprocess
import sys

PATTERNS = ["agenttools", "WolframCloud", "mcp-remote", "sandbox_harvest",
            "PANEL_ONLY", "wolframscript", "falsifier", "gamma_critical"]


def counts(pattern: str) -> tuple[int, int]:
    """(files the session's grep finds, files /usr/bin/grep finds)."""
    script = (
        f'grep -rl {pattern!r} . 2>/dev/null | wc -l; '
        f'/usr/bin/grep -rl {pattern!r} . 2>/dev/null | wc -l'
    )
    r = subprocess.run(["zsh", "-c", f"source ~/.claude/shell-snapshots/"
                        f"$(ls -t ~/.claude/shell-snapshots/ | head -1) 2>/dev/null; {script}"],
                       capture_output=True, text=True)
    lines = [l.strip() for l in r.stdout.split() if l.strip().isdigit()]
    if len(lines) != 2:
        return (-1, -1)
    return int(lines[0]), int(lines[1])


def rows() -> list[tuple[str, int, int]]:
    """(pattern, files the session's grep finds, files /usr/bin/grep finds)."""
    return [(p, *counts(p)) for p in PATTERNS]


def is_vacuous(measured: list[tuple[str, int, int]]) -> bool:
    """Did the wrapper fail to load, making this a comparison with itself?

    THE FAILURE THIS GUARDS IS ONE THAT ALREADY HAPPENED. The first attempt at
    this measurement ran through `zsh -ic`, which never sources the snapshot, so
    `grep` there WAS /usr/bin/grep. It returned 0 of 541 missed and read as
    reassurance. If the snapshot ever moves, is renamed, or stops defining the
    function, this script would repeat that exact lie -- silently, and in the
    reassuring direction, which is the worst direction for a lie to run.

    A loaded wrapper differs from /usr/bin/grep on at least 1 pattern, because
    every pattern here occurs inside the gitignored archive. Equality everywhere
    therefore means the control and the treatment are the same program.
    """
    usable = [(s, r) for _, s, r in measured if s >= 0 and r > 0]
    if not usable:
        return True
    return all(s == r for s, r in usable)


def main() -> int:
    shell_tot = real_tot = 0
    measured = rows()
    print(f"{'pattern':<18}{'session grep':>14}{'/usr/bin/grep':>15}{'unseen':>8}")
    for name, s, r in measured:
        if s < 0:
            print(f"{name:<18}{'probe failed':>14}")
            continue
        shell_tot += s
        real_tot += r
        print(f"{name:<18}{s:>14}{r:>15}{r-s:>8}")

    #: REFUSE RATHER THAN REASSURE. See `is_vacuous`.
    if is_vacuous(measured):
        print()
        print("VACUOUS: the session's grep matched /usr/bin/grep on every pattern.",
              file=sys.stderr)
        print("  The shell wrapper was NOT loaded, so this compared the real grep",
              file=sys.stderr)
        print("  with itself and measured nothing. Do not read 0% as reassurance.",
              file=sys.stderr)
        return 3

    missed = real_tot - shell_tot
    if real_tot == 0:
        print("no matches at all; nothing measured")
        return 2

    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    mp.mp.dps = 40
    w = proportion_confint(missed, real_tot, method="wilson")
    cp = proportion_confint(missed, real_tot, method="beta")
    n, k, z = mp.mpf(real_tot), mp.mpf(missed), mp.mpf('1.959963984540054')
    ph = k / n
    d = 1 + z**2 / n
    c = (ph + z**2 / (2 * n)) / d
    hw = z * mp.sqrt(ph * (1 - ph) / n + z**2 / (4 * n**2)) / d

    print()
    print(f"FILES THE SESSION'S grep NEVER SHOWS: {missed}/{real_tot} = "
          f"{100.0*missed/real_tot:.4f}%")
    print(f"  Wilson 95%          [{100*w[0]:.4f}%, {100*w[1]:.4f}%]")
    print(f"  Clopper-Pearson 95% [{100*cp[0]:.4f}%, {100*cp[1]:.4f}%]")
    print(f"  mpmath@40dps Wilson [{mp.nstr(100*(c-hw), 6)}%, {mp.nstr(100*(c+hw), 6)}%]"
          f"   |agreement| {mp.nstr(abs((c-hw) - mp.mpf(str(w[0]))), 3)}")
    print()
    print("  Use /usr/bin/grep for any search whose ANSWER MIGHT BE ZERO.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
