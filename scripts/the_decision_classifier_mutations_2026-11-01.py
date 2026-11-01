#!/usr/bin/env python3
"""FAILABLE CHECK: is every predicate in the decision classifier load-bearing?

WHY THIS IS OWED. `scripts/how_many_decisions_actually_need_him_2026-11-01.py`
decides what reaches the founder's decision queue, and its predicate was WRONG
ON ITS FIRST RUN in the dangerous direction -- it asked whether a free panel
was mentioned ANYWHERE in an entry body and so marked B21 as needing nothing,
hiding a live question from him. A predicate that has been corrected once and
never attacked is a hypothesis.

4 REVERSIONS, EACH THE DEFECT A PREDICATE EXISTS TO PREVENT:

  1. body-scoped FREE  -- the original bug: an entry is granted if a free panel
     appears anywhere in it. B21 must LEAVE the owed set when this is applied.
  2. no DEPENDS        -- the 4 entries that declare they await B61 stop being
     recognised as dependants, so the owed count must RISE.
  3. no STALE          -- an entry that retires its own asking sentence is read
     as still asking, so the owed count must RISE.
  4. no HIS_DEFERRAL   -- entries he deferred himself re-enter the queue.

A reversion that leaves the owed set UNCHANGED means the predicate decides
nothing, which is the addition-reaching-nothing failure this project has
confirmed 11 times.

IT MUTATES A COPY, NEVER THE SUBJECT. On 2026-11-01 a mutation harness of mine
restored its subject with `git checkout --`, the subject had been written
minutes earlier and was not yet in git, and restore therefore meant DELETE --
after printing that it had caught 8 of 8. Here the source bytes are read once,
each mutation is written to a fresh file in a temporary directory, and the
subject on disk is never opened for writing at all. A commit may be in flight
while this runs and cannot be disturbed by it.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys
import tempfile
import uuid

REPO = pathlib.Path(__file__).resolve().parents[1]
SUBJECT = REPO / "scripts" / "how_many_decisions_actually_need_him_2026-11-01.py"

#: (name, original fragment, replacement, direction) -- direction is what the
#: owed set must do: 'shrink', 'grow', or 'change'.
MUTATIONS = [
    ("body-scoped FREE (the original defect)",
     "        free = bool(FREE.search(sent))",
     "        free = bool(FREE.search(txt))",
     "shrink"),
    ("DEPENDS blinded",
     'DEPENDS = re.compile(\n    r"AWAITS THE SHARED SCOPE DECISION AT ([A-Z]\\d+)"\n    r"|awaits? the (?:shared )?(?:scope )?decision at ([A-Z]\\d+)"\n    r"|NOT A RULING OF ITS OWN", re.I)',
     'DEPENDS = re.compile(\n    r"THIS PHRASE OCCURS IN NO ENTRY ([A-Z]\\d+)"\n    r"|NOR DOES THIS ONE ([A-Z]\\d+)", re.I)',
     "constructed"),
    ("STALE blinded",
     'STALE = re.compile(r"SENTENCE ABOVE IS STALE|ALREADY CONTAINS ITS OWN REFUTATION"',
     'STALE = re.compile(r"THIS STRING OCCURS IN NO ENTRY|NOR DOES THIS ONE"',
     "grow"),
    ("HIS_DEFERRAL branch removed",
     '    if state == "DEFERRED" and ruled:\n        kind = "HIS_DEFERRAL"\n    elif dep:',
     '    if False:\n        kind = "HIS_DEFERRAL"\n    elif dep:',
     "grow"),
]


#: ★ THE CASE LIVE DATA DOES NOT SUPPLY. Blinding DEPENDS changed nothing on
#: the real list, because all 4 entries that declare they await B61 also carry
#: no asking sentence and fall to MINE either way. The branch exists for an
#: entry that BOTH asks and depends -- which is what a dependant becomes the
#: moment it restates its parent's question, and is the shape that would put 1
#: decision in front of him 5 times. Driving it with a constructed entry is the
#: difference between a guard that is tested and a guard that is described.
CONSTRUCTED = {
    "state": "OPEN",
    "ruled": None,
    "text": ("**NEEDS HIS RULING: whether the de-duplicator keeps the longer "
             "line or the earlier one.** AWAITS THE SHARED SCOPE DECISION AT "
             "B61, so it is not a ruling of its own."),
    "baseline_kind": "DEPENDENT",
    "mutant_kind": "OWED",
}


def _load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def owed_set(path: pathlib.Path, name: str) -> set[str]:
    mod = _load(path, name)
    return {r["ident"] for r in mod.classify() if r["kind"] == "OWED"}


def main() -> int:
    if not SUBJECT.is_file():
        print(f"REFUSED: the subject {SUBJECT} does not exist. A harness that "
              f"cannot find what it is attacking must not report a result.")
        return 2
    source = SUBJECT.read_bytes()
    before = SUBJECT.stat().st_mtime_ns

    baseline = owed_set(SUBJECT, "decisions_baseline")
    print("=" * 78)
    print("THE DECISION CLASSIFIER, ATTACKED")
    print("=" * 78)
    print(f"\nbaseline owed set: {sorted(baseline)}  (n = {len(baseline)})")
    assert baseline, "ANTI-VACUITY: a baseline with 0 owed entries would make " \
                     "every 'shrink' mutation pass for free"

    caught = 0
    failures: list[str] = []
    text = source.decode()
    # Same DEPTH as the subject, so `parents[1]` still resolves to the repo.
    # `.cdsfl_tmp/` is the repository's own scratch directory and is ignored by
    # git, so a commit in flight cannot sweep a mutant into itself.
    scratch = REPO / ".cdsfl_tmp"
    scratch.mkdir(exist_ok=True)
    written: list[pathlib.Path] = []
    try:
        for i, (label, old, new, direction) in enumerate(MUTATIONS):
            if old not in text:
                print(f"\n  [{i+1}] {label}\n      NOT APPLIED: anchor absent. The "
                      f"harness is stale against its subject, which is a FAILURE "
                      f"and not a pass.")
                continue
            p = scratch / f"mutant_{uuid.uuid4().hex[:8]}_{i}.py"
            written.append(p)
            p.write_bytes(text.replace(old, new, 1).encode())
            try:
                got = owed_set(p, f"decisions_mutant_{i}")
            except Exception as exc:                      # noqa: BLE001
                # ★ AN EXCEPTION IS NOT A CATCH, AND THE FIRST VERSION OF THIS
                # HARNESS COUNTED IT AS ONE. Mutants were written to a system
                # temporary directory, so `REPO = parents[1]` resolved outside
                # the repository, every mutant died with FileNotFoundError
                # before reading a single entry, and the harness printed
                # "caught 4 of 4" having tested NOTHING. That is the vacuous
                # instrument this project keeps meeting: a check that cannot
                # fail for the right reason. Mutants now live at the same depth
                # as the subject so the path resolves, and a raise counts
                # against the harness.
                print(f"\n  [{i+1}] {label}\n      HARNESS FAILURE: the mutant "
                      f"raised {type(exc).__name__}: {exc}. It did not reach the "
                      f"predicate, so this mutation tested nothing.")
                failures.append(f"{label}: {type(exc).__name__}")
                continue
            if direction == "constructed":
                base_mod = sys.modules["decisions_baseline"]
                mut_mod = sys.modules[f"decisions_mutant_{i}"]
                base_kind = base_mod.classify_text(
                    CONSTRUCTED["state"], CONSTRUCTED["ruled"],
                    CONSTRUCTED["text"])["kind"]
                mut_kind = mut_mod.classify_text(
                    CONSTRUCTED["state"], CONSTRUCTED["ruled"],
                    CONSTRUCTED["text"])["kind"]
                ok = (base_kind == CONSTRUCTED["baseline_kind"]
                      and mut_kind == CONSTRUCTED["mutant_kind"])
                print(f"\n  [{i+1}] {label}")
                print(f"      live owed set UNCHANGED at {sorted(got)}, so the "
                      f"real list does not exercise this branch")
                print(f"      constructed entry that asks AND depends: baseline "
                      f"{base_kind}, mutant {mut_kind}")
                print(f"      expected {CONSTRUCTED['baseline_kind']} then "
                      f"{CONSTRUCTED['mutant_kind']}: "
                      f"{'CAUGHT' if ok else 'SURVIVED'}")
                if ok:
                    caught += 1
                else:
                    print("      ★ SURVIVED means this predicate decides nothing.")
                continue
            if direction == "shrink":
                ok = got < baseline
            elif direction == "grow":
                ok = got > baseline
            else:
                ok = got != baseline
            print(f"\n  [{i+1}] {label}")
            print(f"      owed under mutation: {sorted(got)}  (n = {len(got)})")
            print(f"      expected to {direction}: {'CAUGHT' if ok else 'SURVIVED'}")
            if ok:
                caught += 1
            else:
                print("      ★ SURVIVED means this predicate decides nothing.")
            lost = sorted(baseline - got)
            gained = sorted(got - baseline)
            if lost:
                print(f"      entries that would STOP reaching him: {lost}")
            if gained:
                print(f"      entries that would START reaching him: {gained}")

    finally:
        for p in written:
            p.unlink(missing_ok=True)
        assert not [p for p in written if p.exists()], "a mutant survived cleanup"

    assert SUBJECT.read_bytes() == source, "the subject was modified"
    assert SUBJECT.stat().st_mtime_ns == before, "the subject's mtime moved"
    print(f"\nsubject byte-identical and untouched: {SUBJECT.name}")
    print(f"\ncaught {caught} of {len(MUTATIONS)}")
    if failures:
        print(f"HARNESS FAILURES ({len(failures)}), which are NOT catches:")
        for f in failures:
            print(f"    {f}")
    print("=" * 78)
    return 0 if caught == len(MUTATIONS) and not failures else 1


if __name__ == "__main__":
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
