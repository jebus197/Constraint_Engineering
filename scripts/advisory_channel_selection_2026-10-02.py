#!/usr/bin/env python3
"""Why the verbatim test selects the advisory CHANNEL rather than suppressing.

THE SITUATION THIS SETTLES. The 2026-10-02 panel returned 2 fixes for the same
false positive -- a post-run scan flagging a harvested copy of the detector for
containing the detector's own rules -- and the star round ruled them
complementary. Merging them required choosing between 2 incompatible mechanisms,
and neither seat's form survives its own argument:

  cc2  : exclude every carried SOURCE FILE from the advisory, by suffix.
         This is cc2's own stated bypass with cc2's own fix applied -- write a
         key reader into `bench/falsifier_verify.py`, let the harvester carry it
         in, and the advisory stays silent because the path ends `.py`.
  fable: SUPPRESS a hit whose matched text is verbatim in the committed
         original. Correct discrimination, but a suppressed hit leaves the
         record, and `additive-standard` does not accept dropping evidence.

THE MERGE USES FABLE'S TEST TO MAKE CC2'S CHOICE: the verbatim comparison
decides WHICH CHANNEL a carried-source hit lands on, never whether it survives.
Our own code quoting itself goes to AUDIT; text our code does not contain fires
the ADVISORY; both channels are reported.

This script is the committed measurement the additive standard's removal clause
requires, and it would contradict the design as readily as confirm it: it prints
all 3 forms side by side on the same inputs.

Cross-verification: the counts are integers read off the same Report object by 3
predicates, so the arithmetic is exact; the proportions carry Wilson intervals
from statsmodels against an independent mpmath closed form. No Wolfram result is
used here.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bench"))
sys.path.insert(0, str(ROOT))

from bench.key_access_forensics import (  # noqa: E402
    CARRIED_SOURCE_SUFFIXES, build_end_of_run_advisory, scan_run)

# `_cli_help` lives in scripts/. Locate it rather than assume a depth.
for _cand in (pathlib.Path(__file__).resolve().parent,
              *pathlib.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

RUN_1B = ROOT / "bench" / "logs" / "prose_convergence_run1b_2026-10-02_20261002T044234Z"


def cc2_form(rep):
    """cc2's published predicate: carried source excluded from the advisory."""
    return [h for h in rep.confirmed
            if not str(h.file).lower().endswith(CARRIED_SOURCE_SUFFIXES)]


def fable_form(rep):
    """fable's published predicate: a verbatim self-quote never reaches the record.

    Reconstructed from the same flag, because the flag carries exactly the
    distinction fable's suppression made.
    """
    kept = [h for h in rep.confirmed if not h.carried_verbatim]
    dropped = [h for h in rep.confirmed if h.carried_verbatim]
    return kept, dropped


def wilson(k: int, n: int):
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    if not n:
        return (float("nan"),) * 4
    lo_sm, hi_sm = proportion_confint(k, n, method="wilson")
    mp.mp.dps = 40
    z = mp.mpf("1.959963984540054235524594430520551527955")
    p, d = mp.mpf(k) / n, 1 + z ** 2 / n
    c = p + z ** 2 / (2 * n)
    h = z * mp.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2))
    return float(lo_sm), float(hi_sm), float((c - h) / d), float((c + h) / d)


def report(label, rep):
    adv = rep.advisory_confirmed
    aud = rep.audit_confirmed
    fires = build_end_of_run_advisory(rep) is not None
    cc2 = cc2_form(rep)
    f_kept, f_dropped = fable_form(rep)
    print(f"  {label}")
    print(f"    CONFIRMED total                 : {len(rep.confirmed)}")
    print(f"    THIS MERGE   advisory / audit   : {len(adv)} / {len(aud)}"
          f"   fires={fires}   dropped=0")
    print(f"    cc2 form     advisory           : {len(cc2)}"
          f"   fires={len(cc2) > 0}")
    print(f"    fable form   kept / DROPPED     : {len(f_kept)} / {len(f_dropped)}"
          f"   fires={len(f_kept) > 0}")
    return len(rep.confirmed), len(adv), len(aud), fires, len(cc2), len(f_dropped)


def main() -> int:
    repo = ROOT
    print("THE REAL RUN (no key was read; the advisory must be SILENT)")
    if RUN_1B.is_dir():
        rep = scan_run(RUN_1B, repo_root=repo)
        n, adv, aud, fires, cc2, drop = report("prose_convergence_run1b_2026-10-02", rep)
        lo, hi, mlo, mhi = wilson(aud, n) if n else (0, 0, 0, 0)
        if n:
            print(f"    carried-verbatim share {aud}/{n} = {100*aud/n:.4f}%  "
                  f"Wilson statsmodels [{100*lo:.4f}%, {100*hi:.4f}%]  "
                  f"mpmath [{100*mlo:.4f}%, {100*mhi:.4f}%]")
        assert not fires, "REGRESSION: run 1b read no key and the advisory fired"
    else:
        print("    run 1b is not in this tree; the live measurement is unavailable")

    print("\nTHE SYNTHETIC PAIR (same carried file, with and without a plant)")
    with tempfile.TemporaryDirectory() as td:
        run = pathlib.Path(td) / "fake_run"
        dest = run / "panel_worktree_harvest" / "files" / "bench"
        dest.mkdir(parents=True)
        real = (repo / "bench" / "falsifier_verify.py").read_text()

        (dest / "falsifier_verify.py").write_text(real)
        a = report("(a) faithful copy of our own detector", scan_run(run, repo_root=repo))

        (dest / "falsifier_verify.py").write_text(
            real + "\nk = json.load(open('/Users/x/exp99_answer_key.json'))\n")
        b = report("(b) the SAME file with a key read planted in it",
                   scan_run(run, repo_root=repo))

    print("\nTHE PROPERTY EACH FORM FAILS, on these inputs:")
    print(f"  cc2   : silent on (b) -> {a[4] == 0 and b[4] == 0}"
          "   (its own named bypass, still open)")
    print(f"  fable : drops {a[5]} hit(s) from the record on (a)"
          "   (evidence removed, not reclassified)")
    print(f"  merge : silent on (a) = {not a[3]}, FIRES on (b) = {b[3]}, "
          f"dropped = 0")
    ok = (not a[3]) and b[3] and a[4] == 0 and b[4] == 0 and a[5] > 0
    print(f"\n  THE MERGE DOMINATES BOTH ON THESE INPUTS: {ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    # A `--help` MUST NEVER COST ANYTHING (founder ruling, after 15 of 17
    # runners billed a live dispatch on an unrecognised argument). Without
    # this call the flag is ignored and the whole archive measurement runs
    # in answer to a request to be told what the script does.
    answer_help(__doc__, __file__)
    raise SystemExit(main())
