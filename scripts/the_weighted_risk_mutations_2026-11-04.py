#!/usr/bin/env python3
"""Does `the_weighted_risk_is_not_a_probability_2026-11-04.py` actually detect?

A producer that cannot go red is a description, not a measurement. This
applies 7 mutations to the 3 files that producer reads and requires each one
to change its verdict. A mutation that leaves the output identical names a
blind spot, and the blind spot is reported rather than excused.

THE RESTORE IS FROM BYTES THIS SCRIPT READ, never from git. `git checkout --`
would discard any uncommitted work in the subject files, which on 2026-11-01
destroyed the very edit under test. Each file's original bytes are held in
memory, written back, and verified by sha256 before the next mutation.

ANCHORS ARE DERIVED FROM THE SUBJECT FILES, never hardcoded, so a mutation
cannot silently become a no-op when a file is edited above the anchor.
"""
from __future__ import annotations

import hashlib
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PRODUCER = REPO / "scripts/the_weighted_risk_is_not_a_probability_2026-11-04.py"
DIRECTIVE = REPO / "bench/directives/universal/cdsfl_operational.md"
APPENDIX = REPO / "docs/MATHEMATICAL_APPENDIX.md"
AUDIT = REPO / "experimental_notes/Mathematical_Model_Audit_2026-04-08.md"


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class _Rose:
    """An expectation that a counted quantity went UP, not that it equals N.

    `label` names the printed prefix; the integer after it is read from the
    baseline output and from the mutated output, and the mutation counts as
    detected only when the second exceeds the first.
    """

    def __init__(self, label: str) -> None:
        self.label = label

    def __repr__(self) -> str:
        return f"a rise in {self.label!r}"

    @staticmethod
    def _read(out: str, label: str) -> int | None:
        m = re.search(re.escape(label) + r"\s*(\d+)", out)
        return int(m.group(1)) if m else None

    def holds(self, base_out: str, mut_out: str) -> bool:
        a = self._read(base_out, self.label)
        b = self._read(mut_out, self.label)
        return a is not None and b is not None and b > a


def _run() -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(PRODUCER)],
                       capture_output=True, text=True, cwd=str(REPO))
    return r.returncode, r.stdout + r.stderr


# (file, find, replace, label, what the verdict must now show)
def _mutations(texts: dict[pathlib.Path, str]) -> list[tuple]:
    drv = texts[DIRECTIVE]
    app = texts[APPENDIX]
    aud = texts[AUDIT]

    # derive each anchor from the file, and refuse if it is not unique
    def one(text: str, needle: str, where: str) -> str:
        n = text.count(needle)
        assert n == 1, f"anchor {needle[:40]!r} appears {n} times in {where}"
        return needle

    return [
        (DIRECTIVE,
         one(drv, "R_n = Σ_k w_k · R_k(n)", "directive"),
         "R_n = AGGREGATE_OVER_CLASSES",
         "the R_n definition is renamed",
         "DEFINITION"),
        (DIRECTIVE,
         one(drv, "If R_k > 0.5", "directive"),
         "If R_k > 0.9",
         "the 0.5 gate threshold is moved",
         # NOT "0.5 GATE": that label is what the producer prints when it
         # FINDS the gate, so the mutation removes it. The observable is the
         # producer SAYING the gate went missing, which is the behaviour this
         # harness forced it to acquire.
         "the 0.5 gate was NOT found"),
        (DIRECTIVE,
         one(drv, "The w_k are NOT required to sum to 1.", "directive"),
         "The w_k are required to sum to 1.",
         "the scale note is INVERTED to claim normalisation",
         "requiring normalisation: 1"),
        (APPENDIX,
         one(app, "the per-class R_k reports residual risk, whose range",
             "appendix"),
         "R_n reports residual risk, whose range",
         "the appendix correction is REVERTED to the defect",
         "DEFECT PRESENT"),
        (APPENDIX,
         one(app, "> **L_n = Σ_k s_k · R_{n,k}**", "appendix"),
         "> **L_n = SOMETHING_ELSE**",
         "the appendix L_n definition is renamed",
         "NOT VERIFIABLE"),
        (AUDIT,
         one(aud, "| R_n ∈ [0, 1] for π ∈ [0,1), m ∈ [0,1] |",
             "audit"),
         "| R_n ∈ [0, 1] for π ∈ [0,1), m ∈ [0,1], w_k summing to 1 |",
         "the audit row is given the missing w_k quantifier",
         "quantifies over w_k: True"),
        (AUDIT,
         one(aud, "### Formal Proofs (z3 SMT solver)", "audit"),
         "### Formal Proofs (z3 SMT solver) -- see scripts/x.py",
         "the audit is given a producer reference",
         # RELATIVE, NOT ABSOLUTE. This read "names: 1" and went blind the
         # moment the audit's own scope correction cited a producer, which
         # moved the baseline from 0 to 1. An expectation pinned to an
         # absolute count measures the file's current contents, not the
         # producer's sensitivity.
         _Rose("Producer scripts the audit names:")),
    ]


def main() -> int:
    subjects = [DIRECTIVE, APPENDIX, AUDIT]
    originals = {p: p.read_bytes() for p in subjects}
    texts = {p: b.decode("utf-8") for p, b in originals.items()}

    base_rc, base_out = _run()
    print("=" * 76)
    print("BASELINE")
    print("=" * 76)
    print(f"  producer exit {base_rc}")
    if base_rc != 0:
        print("  REFUSING: the producer is not green before mutation, so a red "
              "result below would not be attributable to the mutation.")
        return 1

    muts = _mutations(texts)
    print(f"\n  {len(muts)} mutations, each restored from bytes held in memory\n")

    red = 0
    blind = []
    for i, (path, find, repl, label, expect) in enumerate(muts, 1):
        path.write_text(texts[path].replace(find, repl, 1), encoding="utf-8")
        rc, out = _run()
        changed = (out != base_out)
        # restore and PROVE the restore
        path.write_bytes(originals[path])
        assert _sha(path.read_bytes()) == _sha(originals[path]), (
            f"restore of {path} did not reproduce the original bytes")

        shows = (expect.holds(base_out, out) if isinstance(expect, _Rose)
                 else expect in out)
        ok = changed and shows
        red += ok
        if not ok:
            blind.append(label)
        print(f"  {i}. {'RED ' if ok else 'BLIND'}  {label}")
        print(f"       output changed: {changed}   verdict shows "
              f"{expect!r}: {shows}   exit {rc}")

    print()
    print("=" * 76)
    print(f"VERDICT: {red} of {len(muts)} mutations detected")
    print("=" * 76)
    for p in subjects:
        print(f"  {p.relative_to(REPO)} restored, sha256 "
              f"{_sha(p.read_bytes())[:16]}")
    if blind:
        print("\n  BLIND SPOTS, reported rather than excused:")
        for b in blind:
            print(f"    - {b}")
        return 1
    print("\n  no blind spots")
    return 0


if __name__ == "__main__":
    # A `--help` MUST NOT run the measurement. This script WRITES: it mutates 3
    # tracked files in place and restores them from bytes it read. Answering the
    # flag by doing the work would therefore edit the repository to print usage,
    # which is worse than the time it costs. Caught by
    # test_help_never_acts_2026-09-11.py on the full board, outside the gate.
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
