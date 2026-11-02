#!/usr/bin/env python3
"""Does the orchestrator status producer's execution check actually DISCRIMINATE?

WHY THIS EXISTS. On 2026-11-02 `scripts/has_the_bound_orchestrator_been_built_or_run_2026-11-02.py`
reported 2 of its 4 components by GREP, as "N candidate line(s)", and both
verdicts were wrong: `bench/ux_backend_2026-10-20.py` and
`bench/fix_comparator.py` both exist, import and are named by guards. The repair
replaced the grep with an execution check. A repair not tried against its own
failure mode is a hypothesis, so this harness applies mutations and requires each
to be CAUGHT.

THE CONTROL THAT MAKES IT MEAN SOMETHING. For each mutation it also records what
the OLD grep predicate would have said. A mutation the execution check catches
and the grep does not is direct evidence that the repair added discrimination
rather than words.

IT RESTORES WHAT IT FOUND. Every mutation is applied by renaming a file aside and
renaming it back in a `finally`, and the harness verifies the restoration before
exiting. `git checkout --` is NOT used: the project's own record holds a case
where it ate the subject of the work.
"""
from __future__ import annotations

import importlib.util
import io
import contextlib
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PRODUCER = REPO / "scripts" / "has_the_bound_orchestrator_been_built_or_run_2026-11-02.py"

#: The grep the repair REPLACED, kept here as the control. If this still matches
#: after a mutation, the old predicate could not have noticed it.
OLD_GREPS = {
    "ux_backend": re.compile(
        r"ux_backend|UX_BACKEND|def .*researcher|researcher_interface|"
        r"add_model|register_model|api_key|API_KEY"),
    "fix_comparator": re.compile(
        r"compar(e|ator).*fix|fix.*compar(e|ator)|which_fix|"
        r"simplest_sufficient|composab"),
}

MUTATIONS = [
    ("ux_backend", "bench/ux_backend_2026-10-20.py",
     "the researcher-facing UX backend is removed"),
    ("fix_comparator", "bench/fix_comparator.py",
     "the fix comparator is removed"),
]


def _producer_verdicts() -> dict:
    spec = importlib.util.spec_from_file_location("_osp", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_osp"] = mod
    try:
        spec.loader.exec_module(mod)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            mod.main()
        out = buf.getvalue()
    finally:
        sys.modules.pop("_osp", None)
    v = {}
    for line in out.splitlines():
        m = re.match(r"\s{2}(\w+)\s+: (.+)$", line)
        if m:
            v[m.group(1)] = m.group(2).strip()
    return v


def _old_grep_would_match(key: str) -> int:
    """Lines the retired grep still matches across the live tree."""
    pat = OLD_GREPS[key]
    n = 0
    for sub in ("bench", "scripts", "hooks"):
        for f in (REPO / sub).rglob("*.py"):
            if "logs" in f.parts:
                continue
            try:
                for ln in f.read_text(errors="replace").splitlines():
                    if pat.search(ln):
                        n += 1
            except Exception:                                  # noqa: BLE001
                continue
    return n


def main() -> int:
    print("=" * 74)
    print("DOES THE EXECUTION CHECK DISCRIMINATE WHERE THE GREP DID NOT?")
    print("=" * 74)
    base = _producer_verdicts()
    print("  BASELINE, unmutated:")
    for k, v in base.items():
        print(f"    {k:18s} {v[:88]}")

    caught = 0
    rows = []
    for key, rel, what in MUTATIONS:
        f = REPO / rel
        aside = f.with_suffix(f.suffix + ".mutation_aside")
        if not f.is_file():
            rows.append((what, "SKIPPED", "the file is already absent", 0))
            continue
        grep_before = _old_grep_would_match(key)
        f.rename(aside)
        try:
            v = _producer_verdicts().get(key, "(verdict missing)")
            grep_after = _old_grep_would_match(key)
            red = v.startswith("ABSENT")
            caught += red
            rows.append((what, "CAUGHT" if red else "MISSED", v[:70],
                         grep_after))
        finally:
            aside.rename(f)
            assert f.is_file(), f"RESTORE FAILED for {rel} -- fix before trusting this run"
        print(f"\n  MUTATION: {what}")
        print(f"    execution check says : {rows[-1][2]}")
        print(f"    verdict              : {rows[-1][1]}")
        print(f"    the RETIRED grep matched {grep_before} line(s) before and "
              f"{rows[-1][3]} after")
        if rows[-1][3] >= grep_before - 2 and rows[-1][1] == "CAUGHT":
            print(f"    -> THE CONTROL HOLDS: the grep barely moved while the")
            print(f"       execution check flipped to ABSENT, so the repair added")
            print(f"       discrimination and not wording.")

    print()
    print("  every mutated file was restored:",
          all((REPO / rel).is_file() for _, rel, _ in MUTATIONS))
    tested = [r for r in rows if r[1] != "SKIPPED"]
    print(f"  {caught} of {len(tested)} mutation(s) red")
    return 0 if tested and caught == len(tested) else 1


if __name__ == "__main__":
    raise SystemExit(main())
