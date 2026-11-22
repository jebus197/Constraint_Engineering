#!/usr/bin/env python3
"""Does the standing-goal guard actually bite? Reverse each defence and look.

A guard that cannot go red proves nothing. This script reverses, one at a time,
each property `bench/tests/test_the_standing_goal_survives_compaction_2026-11-22.py`
claims to hold, and reports whether the suite notices.

RESTORATION IS THE DANGEROUS PART, AND IT IS WHY THIS IS A SCRIPT AND NOT A
SEQUENCE OF EDITS. `hooks/task_list_pulse.py` is HARD LINKED to the live hook at
~/.claude/hooks/task_list_pulse.py, so every mutation here breaks the real hook
for as long as it is applied. The original bytes are captured first, restored in
a finally block, and verified by hash at the end. An earlier harness in this
project restored with `git checkout --` and destroyed uncommitted work; this one
restores exactly what it found, which for a hard link also means writing in
place rather than renaming a replacement over it.
"""
import hashlib
import pathlib
import subprocess
import sys

# `_cli_help` lives in scripts/. Located rather than assumed at a fixed depth,
# so the import works when this file is IMPORTED as well as when it is RUN.
for _cand in (pathlib.Path(__file__).resolve().parent,
              *pathlib.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402


REPO = pathlib.Path(__file__).resolve().parents[1]
HOOK = REPO / "hooks" / "task_list_pulse.py"
GOAL = REPO / "experimental_notes" / "THE_STANDING_GOAL.md"
TEST = REPO / "bench" / "tests" / "test_the_standing_goal_survives_compaction_2026-11-22.py"


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write_in_place(p, text):
    """Truncate and rewrite, so a hard link to the live hook is preserved."""
    with open(p, "w") as fh:
        fh.write(text)


def run_suite():
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(TEST)],
        cwd=REPO, capture_output=True, text=True, timeout=600,
    )
    return proc.returncode, proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""


# Each mutation is (name, target, transform). The transform receives the ORIGINAL
# text and returns the mutated text, so no anchor is typed twice.
MUTATIONS = [
    ("hook never injects the goal at all",
     HOOK,
     lambda t: t.replace('ctx += "".join("\\n[goal] " + ln',
                         'ctx += "".join("" + ln' if False else '_unused = "".join("\\n[goal] " + ln'),
     False),

    ("goal text becomes a hardcoded constant, ignoring the file",
     HOOK,
     lambda t: t.replace('    f = repo / "experimental_notes" / "THE_STANDING_GOAL.md"',
                         '    return "A FROZEN STRING"\n'
                         '    f = repo / "experimental_notes" / "THE_STANDING_GOAL.md"'),
     False),

    ("fail-safe removed: a missing file now raises instead of returning ''",
     HOOK,
     lambda t: t.replace("    except Exception:                      "
                         "# noqa: BLE001 -- see MUST ALWAYS EXIT 0\n        return \"\"",
                         "    except Exception:                      "
                         "# noqa: BLE001 -- see MUST ALWAYS EXIT 0\n        raise"),
     False),

    # EQUIVALENT MUTANT, PROVEN BELOW, NOT A GUARD GAP. str.find returns the
    # FIRST index of each marker and neither marker is a prefix of the other,
    # so end never equals begin; and when end < begin the slice
    # text[begin+len(BEGIN):end] has start > stop, which Python evaluates to "".
    # The guarded and unguarded forms therefore agree on EVERY input. The clause
    # is kept because it states the intent and would matter to any future reader
    # that does not use slicing -- but no test can distinguish it, and reporting
    # it as a miss would be reporting a property of Python as a defect.
    ("marker-order check dropped, so inverted markers slice backwards",
     HOOK,
     lambda t: t.replace("if begin < 0 or end < 0 or end <= begin:",
                         "if begin < 0 or end < 0:"),
     True),

    ("only the first line of the goal is injected",
     HOOK,
     lambda t: t.replace('for ln in goal.splitlines() if ln.strip()',
                         'for ln in goal.splitlines()[:1] if ln.strip()'),
     False),

    ("continuation lines lose their label",
     HOOK,
     lambda t: t.replace('ctx += "".join("\\n[goal] " + ln for ln',
                         'ctx += "\\n[goal] " + goal  # unlabelled continuations\n'
                         '        _skip = "".join("" + ln for ln'),
     False),

    ("a reserved category is dropped from the injected block",
     GOAL,
     lambda t: t.replace("computationally irreducible, safety, legal/ethical, or a "
                         "fundamental change in",
                         "safety or a fundamental change in", 1),
     False),
]



def prove_equivalence():
    """Show mutation 4 cannot be detected, rather than asserting it."""
    import itertools
    import random
    B, E = "<!-- INJECT-BEGIN -->", "<!-- INJECT-END -->"

    def guarded(t):
        b, e = t.find(B), t.find(E)
        return "" if (b < 0 or e < 0 or e <= b) else t[b + len(B):e].strip()

    def mutated(t):
        b, e = t.find(B), t.find(E)
        return "" if (b < 0 or e < 0) else t[b + len(B):e].strip()

    random.seed(20261122)
    pieces = ["", "x", "PAY", B, E, "\n", "zz"]
    n = diff = 0
    for k in range(5):
        for combo in itertools.product(pieces, repeat=k):
            t = "".join(combo)
            n += 1
            diff += guarded(t) != mutated(t)
    for _ in range(20000):
        t = "".join(random.choice(pieces) for _ in range(random.randint(0, 9)))
        n += 1
        diff += guarded(t) != mutated(t)
    return n, diff


def main():
    originals = {p: p.read_text() for p in (HOOK, GOAL)}
    hashes = {p: digest(p) for p in originals}

    base_rc, base_tail = run_suite()
    print(f"BASELINE (unmutated): rc={base_rc}  {base_tail}")
    if base_rc != 0:
        print("REFUSING TO MUTATE: the suite is not green to begin with.")
        return 2

    red = 0
    try:
        for i, (name, target, transform, equivalent) in enumerate(MUTATIONS, 1):
            before = originals[target]
            after = transform(before)
            if after == before:
                print(f"  {i}. SKIPPED (anchor not found) — {name}")
                continue
            write_in_place(target, after)
            try:
                rc, tail = run_suite()
            finally:
                write_in_place(target, before)
            if equivalent:
                verdict = ("EQUIVALENT (expected green)" if rc == 0
                           else "RED — EQUIVALENCE CLAIM IS WRONG")
            else:
                verdict = "RED" if rc != 0 else "GREEN — THE GUARD MISSED IT"
                red += rc != 0
            print(f"  {i}. {verdict:28s} {name}")
            print(f"      {tail}")
    finally:
        for p, text in originals.items():
            write_in_place(p, text)
        for p, h in hashes.items():
            got = digest(p)
            state = "restored" if got == h else "!! NOT RESTORED !!"
            print(f"  {state}: {p.relative_to(REPO)}")
            if got != h:
                return 3

    total = sum(1 for _, t, f, eq in MUTATIONS
                if not eq and f(originals[t]) != originals[t])
    n, diff = prove_equivalence()
    print(f"\nEQUIVALENCE PROOF for mutation 4: {n:,} inputs tested, "
          f"{diff} on which the guarded and unguarded forms differ.")
    print(f"{red} of {total} NON-EQUIVALENT mutations turned the guard red.")
    return 0 if (red == total and diff == 0) else 1


if __name__ == "__main__":
    answer_help(__doc__, __file__)
    sys.exit(main())
