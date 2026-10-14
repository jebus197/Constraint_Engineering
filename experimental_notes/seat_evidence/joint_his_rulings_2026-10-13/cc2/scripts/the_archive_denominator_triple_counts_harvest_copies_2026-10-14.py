# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_his_rulings_2026-10-13', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 53e0a7ff52c48146bbb1047a0148be06beaedf5a0fda5165c248727afb641044
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""J3 side-finding, 2026-10-14: the archive denominator counts harvest copies.

The 3,298-entry corpus that the briefs, the severity measurements and the J3
question all rest on comes from
`scripts/severity_was_never_computed_from_the_model_2026-10-12.py`, whose
generator globs `bench/logs/**/runner_state.json` with no exclusion. That glob
picks up HARVESTED SEAT SANDBOXES stored under bench/logs -- copies of other
runs' registries saved beside the runs themselves.

Measured here: 304 of the 3,298 entries are such copies, they reduce to 152
distinct (canonical_id, description) keys -- so each is counted twice inside the
harvest set alone -- and 152 of 152 are also present in the clean archive. The
corpus therefore counts 152 findings three times.

Consequence, stated as the figure it moves: the no-falsifier share is
1938/3298 = 58.7629% as published, and 1886/2994 = 62.9927% with the copies
excluded. Both intervals are reported. The published figure is not wrong about
the files it read; it is wrong about how many findings exist.

NOTHING IS CHANGED BY THIS SCRIPT. The canonical producer is left exactly as it
is: its figure is quoted across several documents, and restating it is the
founder's call, not a seat's. This script measures the contamination so the
decision has a number.

Run: python3 scripts/the_archive_denominator_triple_counts_harvest_copies_2026-10-14.py
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CANON = REPO / "scripts" / "severity_was_never_computed_from_the_model_2026-10-12.py"
COPY_MARKERS = ("sandbox_harvest", "seat_evidence")


def wilson_two_tools(k: int, n: int):
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    mp.mp.dps = 50
    sm = proportion_confint(k, n, 0.05, "wilson")
    z = mp.sqrt(2) * mp.erfinv(mp.mpf("0.95"))
    n_ = mp.mpf(n); p = mp.mpf(k) / n_
    d = 1 + z ** 2 / n_
    c = (p + z ** 2 / (2 * n_)) / d
    h = (z * mp.sqrt(p * (1 - p) / n_ + z ** 2 / (4 * n_ ** 2))) / d
    return (float(sm[0]), float(sm[1])), (float(c - h), float(c + h))


def main() -> int:
    argparse.ArgumentParser(
        description=("J3: measure how many archive entries are harvested-sandbox "
                     "copies, and what excluding them does to the rate.")).parse_args()

    spec = importlib.util.spec_from_file_location("canon", CANON)
    canon = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(canon)

    rows = [(fp, cid, e) for fp, cid, e in canon.entries()
            if isinstance(e.get("severity"), (int, float))]
    def is_copy(fp) -> bool:
        return any(mk in str(fp) for mk in COPY_MARKERS)

    harvest = [r for r in rows if is_copy(r[0])]
    clean = [r for r in rows if not is_copy(r[0])]

    def key(e):
        return (e.get("canonical_id"), (e.get("description") or "")[:120])

    hk = {key(e) for _, _, e in harvest}
    ck = {key(e) for _, _, e in clean}

    print("=" * 78)
    print("J3 SIDE-FINDING -- THE ARCHIVE DENOMINATOR")
    print("=" * 78)
    print("canonical generator  : %s" % CANON.relative_to(REPO))
    print("entries with numeric severity, as published : %d" % len(rows))
    print("  inside harvested-sandbox copies           : %d" % len(harvest))
    print("  distinct keys among those copies          : %d" % len(hk))
    print("    => counted %.1fx within the copies alone"
          % (len(harvest) / max(len(hk), 1)))
    print("  copies also present in the clean archive  : %d of %d"
          % (len(hk & ck), len(hk)))
    print("  clean entries                             : %d" % len(clean))

    def nofals(seq):
        return [r for r in seq if not (r[2].get("falsifier_code") or "").strip()]

    k_all, n_all = len(nofals(rows)), len(rows)
    k_cl, n_cl = len(nofals(clean)), len(clean)
    print("\nthe no-falsifier / UNTOOLABLE share, both denominators:")
    for lbl, k, n in (("as published (copies INCLUDED)", k_all, n_all),
                      ("copies EXCLUDED", k_cl, n_cl)):
        sm, mpv = wilson_two_tools(k, n)
        print("  %-32s %4d/%4d = %8.4f%%  Wilson95 [%7.4f%%, %7.4f%%]"
              % (lbl, k, n, 100 * k / n, 100 * sm[0], 100 * sm[1]))
        print("  %-32s %18s mpmath   [%7.4f%%, %7.4f%%] agree=%s"
              % ("", "", 100 * mpv[0], 100 * mpv[1],
                 abs(sm[0] - mpv[0]) < 1e-12 and abs(sm[1] - mpv[1]) < 1e-12))
    print("\nBoth figures are real. The published one reproduces exactly and is")
    print("the right answer about the FILES; the excluded one is the right")
    print("answer about the FINDINGS. The direction matters: excluding copies")
    print("makes the no-falsifier problem LARGER, not smaller.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
