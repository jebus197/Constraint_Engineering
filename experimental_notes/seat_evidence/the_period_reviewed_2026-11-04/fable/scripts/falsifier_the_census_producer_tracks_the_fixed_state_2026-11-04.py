# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'the_period_reviewed_2026-11-04', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: a5a68b9a2ec2005c0884bc96c8c265a40032dc3aa3c7a703852f380d3ffc7cbc
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER for the 2026-11-04 repair of
`scripts/the_census_counts_what_the_reader_excludes_2026-11-04.py`.

CLAIM UNDER TEST: the producer now (1) exits 0 on the repaired tree, where the
census quotes only his annotations and names the residue; and (2) still goes
red if the B108 fix reverts -- i.e. if `claim_a_naive_grep_is_blind_to_some_of_them`
again folds the residue into `annotations_total` or stops naming it.

FAILS (raises AssertionError / prints FALSIFIED) iff either half is false.
"""
import importlib.util
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PRODUCER = REPO / "scripts" / "the_census_counts_what_the_reader_excludes_2026-11-04.py"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main() -> int:
    # Half 1: the producer passes on the repaired tree.
    r = subprocess.run([sys.executable, str(PRODUCER)],
                       capture_output=True, text=True, timeout=600)
    if r.returncode != 0 or "All structural checks held: True" not in r.stdout:
        print("FALSIFIED: producer does not pass on the repaired tree "
              f"(exit {r.returncode})")
        print(r.stdout[-600:])
        return 1
    print(f"half 1: producer exit 0, verdict line: "
          f"{[l for l in r.stdout.splitlines() if l.startswith('VERDICT')][0]}")

    # Half 2: a reverted census (pre-fix shape) must turn step_2 red.
    producer = load(PRODUCER, "_census_producer")
    m = producer._reader()
    real = m.claim_a_naive_grep_is_blind_to_some_of_them

    class Reverted:
        """Proxy over the real reader module simulating the PRE-FIX census:
        the residue folded into `annotations_total` and not reported."""
        def __getattr__(self, k):
            return getattr(m, k)
        def claim_a_naive_grep_is_blind_to_some_of_them(self):
            c = dict(real())
            c["annotations_total"] = (c["annotations_total"]
                                      + c["annotations_excluded_as_not_his"])
            c["annotations_excluded_as_not_his"] = 0
            return c

    s2 = producer.step_2_the_decomposition(Reverted())
    red = not (s2["quotes_only_his"] and s2["residue_named"])
    assert red, "FALSIFIED: step_2 stayed green on a reverted census"
    print(f"half 2: reverted census -> quotes_only_his={s2['quotes_only_his']}, "
          f"residue_named={s2['residue_named']} (red as required)")
    print("NOT FALSIFIED: both halves hold.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
