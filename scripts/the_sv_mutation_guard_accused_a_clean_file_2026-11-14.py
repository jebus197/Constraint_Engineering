#!/usr/bin/env python3
"""The sv tree-mutation guard accused a file that never invokes sv.

★ WHAT HAPPENED. The full suite of 2026-11-14 failed
`test_tests_do_not_mutate_the_working_tree_2026-08-26.py::
test_no_test_runs_sv_against_the_real_repo_without_dry_run` on
`test_the_co_author_trailer_is_not_doubled_2026-11-14.py`, the guard written
that same night for B193, the entry on sv appending a co-author trailer the
message already carries. The accusation is FALSE and the guard's own printed
remedy -- pass --dry-run -- would have put a meaningless flag string into a file
with no sv CLI call to pass it to.

★ WHY THE OLD PREDICATE COULD NOT BE RIGHT. It was 3 regexes ANDed over the
WHOLE FILE: `sv.main()|cdsfl_sv.py"` anywhere, `cwd=REPO` anywhere, and no
`--dry-run` anywhere. In the accused file the first matched a `read_text()` of
the sv SOURCE for an AST parse, and the second matched an unrelated read-only
`git log -1 --format=%B 4a802768` 25 lines away. A substring is not a call, and
a file-wide conjunction cannot tell 2 unrelated lines from 1 call site.

★ AND THE FIRST REPLACEMENT WAS WRONG IN THE OTHER DIRECTION, which is the
finding worth keeping. It assumed an in-process `sv.main()` writes relative to
the PROCESS CWD, and so flagged all 3 in-process call sites in the corpus. sv
does not: it writes under `repo_root()`, and all 3 monkeypatch `sv.repo_root` to
a tmp directory. Replacing 1 false positive with 3 was 1 reading away.

Reads only. Writes nothing. Runs no pytest.
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
GUARD = (REPO / "bench" / "tests"
         / "test_tests_do_not_mutate_the_working_tree_2026-08-26.py")
ACCUSED = (REPO / "bench" / "tests"
           / "test_the_co_author_trailer_is_not_doubled_2026-11-14.py")

#: The predicate as it stood before 2026-11-14, kept so the comparison is an
#: EXECUTION of both forms rather than a claim about one of them.
OLD_SV = re.compile(r"sv\.main\(\)|cdsfl_sv\.py['\"]")
OLD_DRY = re.compile(r"--dry-run")
OLD_CWD = re.compile(r"cwd\s*=\s*(REPO|REPO_ROOT|str\(REPO\)|str\(REPO_ROOT\))\b")


def _guard_module():
    """Import the guard file as a module to call its LIVE predicate.

    `execute-do-not-grep`: the new predicate is read out of the file that runs
    it, never re-implemented here, so this script cannot agree with a copy of
    itself.
    """
    spec = importlib.util.spec_from_file_location("svmut", GUARD)
    m = importlib.util.module_from_spec(spec)
    sys.modules["svmut"] = m
    spec.loader.exec_module(m)
    return m


def old_offends(src: str) -> bool:
    return (bool(OLD_SV.search(src)) and bool(OLD_CWD.search(src))
            and not OLD_DRY.search(src))


def _wilson_statsmodels(k: int, n: int):
    from statsmodels.stats.proportion import proportion_confint
    return tuple(proportion_confint(k, n, alpha=0.05, method="wilson"))


def _wilson_mpmath(k: int, n: int):
    """Hand-rolled, so the interval is not 1 library agreeing with itself."""
    import mpmath as mp
    mp.mp.dps = 40
    if n == 0:
        return (mp.mpf(0), mp.mpf(0))
    z = mp.sqrt(2) * mp.erfinv(mp.mpf("0.95"))
    p = mp.mpf(k) / n
    d = 1 + z**2 / n
    c = p + z**2 / (2 * n)
    h = z * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return (max(mp.mpf(0), (c - h) / d), min(mp.mpf(1), (c + h) / d))


def _cp_statsmodels(k: int, n: int):
    from statsmodels.stats.proportion import proportion_confint
    return tuple(proportion_confint(k, n, alpha=0.05, method="beta"))


def _cp_exact_tails(k: int, n: int):
    """Clopper-Pearson from the EXACT binomial tails, by bisection.

    mpmath's `findroot` does not converge at these parameters and `betainc`
    failed to converge too, both measured on 2026-11-14; bisection on a
    monotone tail cannot fail to.
    """
    import mpmath as mp
    mp.mp.dps = 40
    a = mp.mpf("0.025")

    def upper_tail(p):            # P(X >= k) at p, increasing in p
        return mp.fsum([mp.binomial(n, i) * p**i * (1 - p)**(n - i)
                        for i in range(k, n + 1)])

    def lower_tail(p):            # P(X <= k) at p, decreasing in p
        return mp.fsum([mp.binomial(n, i) * p**i * (1 - p)**(n - i)
                        for i in range(0, k + 1)])

    def bisect(f, target, lo, hi):
        for _ in range(300):
            mid = (lo + hi) / 2
            if (f(mid) - target) * (f(lo) - target) <= 0:
                hi = mid
            else:
                lo = mid
        return (lo + hi) / 2

    lo = mp.mpf(0) if k == 0 else bisect(upper_tail, a, mp.mpf(0), mp.mpf(1))
    hi = mp.mpf(1) if k == n else bisect(lower_tail, a, mp.mpf(0), mp.mpf(1))
    return (lo, hi)


def _report_proportion(label: str, k: int, n: int) -> None:
    ws = _wilson_statsmodels(k, n)
    wm = _wilson_mpmath(k, n)
    cs = _cp_statsmodels(k, n)
    ce = _cp_exact_tails(k, n)
    agree_w = max(abs(float(wm[0]) - ws[0]), abs(float(wm[1]) - ws[1]))
    agree_c = max(abs(float(ce[0]) - cs[0]), abs(float(ce[1]) - cs[1]))
    print(f"  {label}: {k} of {n} = {k / n if n else 0.0:.6f}")
    print(f"      Wilson          [{ws[0]:.6f}, {ws[1]:.6f}]  "
          f"(statsmodels; hand-rolled mpmath agrees to {agree_w:.3e})")
    print(f"      Clopper-Pearson [{cs[0]:.6f}, {cs[1]:.6f}]  "
          f"(beta quantile; exact binomial tails agree to {agree_c:.3e})")


#: The 7 cases the guard must decide, each from something actually observed.
#: `True` means the predicate SHOULD flag it.
FIXTURES = [
    ("the historical defect of 2026-08-26",
     "import cdsfl_sv as sv\ndef t():\n"
     "    subprocess.run([sys.executable, '-c', \"sys.argv = ['cdsfl_sv.py']; "
     "sys.exit(sv.main())\"], cwd=REPO)\n", True),
    ("the accepted fix for it",
     "import cdsfl_sv as sv\ndef t():\n"
     "    subprocess.run([sys.executable, '-c', \"sys.argv = ['cdsfl_sv.py', "
     "'--dry-run']; sys.exit(sv.main())\"], cwd=REPO)\n", False),
    ("a run with a tmp cwd",
     "import cdsfl_sv as sv\ndef t():\n    subprocess.run([x], cwd=tmp_path)\n",
     False),
    ("in-process sv.main(), nothing redirected",
     "import cdsfl_sv as sv\ndef t():\n    sv.main()\n", True),
    ("in-process sv.main() with --dry-run patched into argv",
     "import cdsfl_sv as sv\ndef t():\n"
     "    monkeypatch.setattr(sys, 'argv', ['sv', '--dry-run'])\n    sv.main()\n",
     False),
    ("in-process sv.main() with repo_root redirected to tmp",
     "import cdsfl_sv as sv\ndef t():\n"
     "    monkeypatch.setattr(sv, 'repo_root', lambda: tmp_path)\n    sv.main()\n",
     False),
    ("the 2026-11-14 shape: import, AST read of the sv source, unrelated git log",
     'import cdsfl_sv as sv\ndef t():\n'
     '    subprocess.run(["git", "log", "-1", "--format=%B", "4a802768"], cwd=REPO)\n'
     'def u():\n'
     '    tree = ast.parse((REPO / "scripts" / "cdsfl_sv.py").read_text())\n',
     False),
]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true",
                    help="emit the figures as JSON instead of prose")
    a = ap.parse_args([] if argv is None else argv)

    m = _guard_module()
    files = sorted((REPO / "bench" / "tests").glob("test_*.py"))
    old_flagged, new_flagged, invocation_files = [], [], []
    for p in files:
        src = p.read_text(encoding="utf-8", errors="replace")
        if old_offends(src):
            old_flagged.append(p.name)
        if m.sv_offender_call_sites(src):
            new_flagged.append(p.name)
        if m.sv_invocation_call_sites(src):
            invocation_files.append(p.name)

    inproc = []
    for p in files:
        src = p.read_text(encoding="utf-8", errors="replace")
        for line, call, is_inproc in m.sv_invocation_call_sites(src):
            if is_inproc:
                inproc.append((p.name, line))

    wrong = [(lbl, want, bool(m.sv_offender_call_sites(src)))
             for lbl, src, want in FIXTURES
             if bool(m.sv_offender_call_sites(src)) != want]

    if a.json:
        import json
        print(json.dumps({
            "files": len(files),
            "old_flagged": old_flagged,
            "new_flagged": new_flagged,
            "files_containing_an_invocation": len(invocation_files),
            "in_process_call_sites": inproc,
            "fixtures": len(FIXTURES),
            "fixtures_decided_wrongly": wrong,
        }, indent=2))
        return 0 if not wrong else 1

    print(f"  test files scanned: {len(files)}")
    print(f"  files containing an sv INVOCATION (any kind): "
          f"{len(invocation_files)}")
    print(f"  in-process `sv.main()` call sites: {len(inproc)} -> "
          f"{', '.join(f'{n}:{ln}' for n, ln in inproc)}")
    print()
    _report_proportion("OLD file-wide conjunction flagged",
                       len(old_flagged), len(files))
    for n in old_flagged:
        print(f"      {n}  <- FALSE POSITIVE: no sv CLI call in the file at all")
    print()
    _report_proportion("NEW call-scoped AST predicate flags",
                       len(new_flagged), len(files))
    print()
    print(f"  fixtures decided correctly: {len(FIXTURES) - len(wrong)} "
          f"of {len(FIXTURES)}")
    for lbl, want, got in wrong:
        print(f"      WRONG: {lbl} -- wanted {want}, got {got}")
    if wrong:
        print("  REFUSED: the predicate decides a commissioning case wrongly.")
        return 1
    print("  Both directions hold: the historical defect is still caught and "
          "the clean file is not.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
