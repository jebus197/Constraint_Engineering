#!/usr/bin/env python3
"""Task 6.4: how far do the archive/source checkers disagree with each other?

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

Five checkers each decided independently whether a repository-relative path is
archived run output or production source. This records what each one excluded
BEFORE the shared predicate landed, and the pairwise agreement between them, so
the justification for `bench/repo_paths.py` is reproducible rather than asserted.

The pre-fix exclusion sets are frozen here deliberately: after the fix every site
calls one predicate, so re-deriving them from source would return the same answer
for all 5 and the disagreement being fixed would become invisible.
"""
import itertools
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

#: What each site excluded on 2026-09-09, before `bench/repo_paths.py`.
BEFORE = {
    "scripts/drift_scan_scope_2026-09-08.py:47": ("bench/logs/",),
    "bench/tests/test_derived_docs_match_their_generators_2026-09-01.py:135": ("bench/logs/",),
    "bench/tests/test_line_citations_resolve_2026-09-01.py:73": ("bench/logs/", "bench/results/"),
    "bench/tests/test_python_floor_2026-09-07.py:74": (".git/", "bench/logs/"),
    "bench/tests/test_archive_is_not_written_by_tests.py:103": ("bench/logs",),
    # THE 2 SITES THE FIRST PASS MISSED, wired 2026-09-10 after an adversarial
    # review found task 6.4 had closed 5 of the 6 instances it named. Both are
    # sibling SCANNERS that walk bench/ for .py files, and both used a bare
    # substring on a path: "/logs/" and an os.sep-padded "logs". Neither matches
    # `bench/logs_quarantine`, whose segment is "logs_quarantine", and neither
    # matches `bench/results` at all -- exactly the 2 roots this predicate was
    # built to stop 5 checkers disagreeing about.
    "bench/tests/test_panel_sandbox_2026-09-07.py:244": ("/logs/",),
    "bench/tests/test_immune_memory_evaluation.py:452": ("logs",),
}


def main() -> int:
    roots = sorted({r for v in BEFORE.values() for r in v} | {"bench/logs_quarantine/"})
    print("what each checker excluded, before the shared predicate:\n")
    head = f"{'site':56s} " + " ".join(f"{r:24s}" for r in roots)
    print(head)
    for site, ex in BEFORE.items():
        row = " ".join(f"{('YES' if r in ex else 'no'):24s}" for r in roots)
        print(f"{site.split('/')[-1][:56]:56s} {row}")

    pairs = list(itertools.combinations(BEFORE.values(), 2))
    agree = sum(1 for a, b in pairs if set(a) == set(b))
    n = len(pairs)
    print(f"\npairs of checkers agreeing exactly: {agree} of {n}")

    from statsmodels.stats.proportion import proportion_confint
    lo_w, hi_w = proportion_confint(agree, n, method="wilson")
    lo_c, hi_c = proportion_confint(agree, n, method="beta")
    from scipy.stats import beta as sb
    lo_s = 0.0 if agree == 0 else sb.ppf(0.025, agree, n - agree + 1)
    hi_s = 1.0 if agree == n else sb.ppf(0.975, agree + 1, n - agree)
    print(f"Wilson 95%          : [{lo_w*100:.1f}%, {hi_w*100:.1f}%]  (statsmodels)")
    print(f"Clopper-Pearson 95% : [{lo_c*100:.1f}%, {hi_c*100:.1f}%]  (statsmodels)")
    print(f"Clopper-Pearson 95% : [{lo_s*100:.1f}%, {hi_s*100:.1f}%]  (scipy cross-check)")
    print(f"tools agree to 1e-9 : {abs(lo_s-lo_c) < 1e-9 and abs(hi_s-hi_c) < 1e-9}")

    quarantine = REPO / "bench" / "logs_quarantine"
    results = REPO / "bench" / "results"
    print(f"\nbench/logs_quarantine exists on disk : {quarantine.is_dir()}")
    print(f"bench/results exists on disk         : {results.is_dir()}")
    excl_q = sum(1 for ex in BEFORE.values() if "bench/logs_quarantine/" in ex)
    excl_r = sum(1 for ex in BEFORE.values() if "bench/results/" in ex)
    print(f"checkers excluding logs_quarantine   : {excl_q} of {len(BEFORE)}")
    print(f"checkers excluding bench/results     : {excl_r} of {len(BEFORE)}")

    print("\nAND THE REASON DELIMITING MATTERS, from this repository:")
    print("  'bench/logs_quarantine/x.py'.startswith('bench/logs')  ->",
          "bench/logs_quarantine/x.py".startswith("bench/logs"))
    print("  'bench/logs_quarantine/x.py'.startswith('bench/logs/') ->",
          "bench/logs_quarantine/x.py".startswith("bench/logs/"))
    print("  neither is a decision anyone made; component comparison removes the choice.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
