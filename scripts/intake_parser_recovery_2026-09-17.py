#!/usr/bin/env python3
"""Task 9.3: how much of what the intake parser SAW did it RECOVER, over the archive?

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

WHY THIS EXISTS. Task 9.3 and the docstring of
`bench/tests/test_intake_parser_is_studied_2026-09-10.py` quoted point figures --
132 of 411 raw labels, 132 of 138 (or 140) fenced labels, 271 unfenced, 6
recovered only by the tolerant companion, over 119 replies -- that no committed
script produced. They also disagreed with each other: 411 less 271 is 140, not
138. A re-scan with the shipped telemetry reproduced none of them. This script is
the producer: only its printed output may be quoted.

WHAT IT MEASURES. `runner_core.falsifier_intake_telemetry`, the function the
runner itself calls, applied to the `response` of every archived reply matching
`bench/logs/exp*/r*_*.json` that contains `FALSIFIER:`. It reports replies
examined, raw labels, labels with a fence within 3 lines, blocks recovered, and
blocks recovered only by the tolerant companion, with both recovery rates and
their Wilson intervals from 2 implementations.

THE POPULATION IS DECLARED, because it moves. Files are taken in reverse lexical
order of path, the order the 2026-09-10 test uses. By default every matching file is
read; `--stop-at-fenced N` reproduces that test's rule of stopping once N fenced
labels are seen. `bench/logs` is ignored by `.gitignore` and only part of it is
committed, so a maintainer's tree can hold replies a fresh clone does not: the
script prints how many of the files it read are tracked, and a sha256 of the
file list, so 2 runs can be compared, and `--tracked-only` restricts the
population to what a clone has. Tracked symlinked directories are followed by the
glob and counted once (see `population`).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
GLOB = "bench/logs/exp*/r*_*.json"


def tracked_files(repo: pathlib.Path = REPO) -> set[str] | None:
    """Repo-relative paths git tracks under bench/logs, or None when git cannot say."""
    try:
        r = subprocess.run(["git", "ls-files", "bench/logs"], cwd=repo,
                           capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    return set(r.stdout.split())


def population(repo: pathlib.Path = REPO, tracked_only: bool = False,
               tracked: set[str] | None = None) -> tuple[list[pathlib.Path], int]:
    """Every distinct reply file the glob matches, and how many aliases were skipped.

    Order is reverse lexical order of the matched path, the order the 2026-09-10
    test uses and calls "newest first"; it is only roughly chronological
    (`experiment_18/` sorts ahead of every `exp5*` directory).

    SYMLINKED DIRECTORIES ARE COUNTED ONCE. `bench/logs` holds tracked symlinks
    such as `exp36_evidence_latest -> exp36_evidence_20260407T004931Z`, and the
    glob follows them, so the same reply is matched under 2 names. Each file is
    kept at its first match and returned as its resolved path, which is also the
    path git tracks.
    """
    repo = repo.resolve()
    seen: set[pathlib.Path] = set()
    files: list[pathlib.Path] = []
    aliases = 0
    for f in sorted(repo.glob(GLOB), key=lambda p: str(p), reverse=True):
        real = f.resolve()
        if real in seen:
            aliases += 1
            continue
        seen.add(real)
        files.append(real)
    if tracked_only:
        if tracked is None:
            raise RuntimeError("git ls-files failed; cannot restrict to tracked files")
        files = [f for f in files if str(f.relative_to(repo)) in tracked]
    return files, aliases


def scan(files, stop_at_fenced: int | None = None) -> dict:
    """Sum the runner's own intake telemetry over the replies that carry a label."""
    root = REPO / "bench"
    for p in (str(root), str(REPO)):
        if p not in sys.path:
            sys.path.insert(0, p)
    from runner_core import falsifier_intake_telemetry as telem

    out = {"files_read": 0, "replies_examined": 0, "labels_seen": 0,
           "labels_with_a_fence_within_3_lines": 0, "blocks_recovered": 0,
           "recovered_only_by_the_companion": 0, "unreadable": 0}
    for f in files:
        out["files_read"] += 1
        try:
            r = json.loads(pathlib.Path(f).read_text(encoding="utf-8")).get("response", "")
        except (ValueError, OSError, AttributeError):
            out["unreadable"] += 1
            continue
        if not isinstance(r, str) or "FALSIFIER:" not in r:
            continue
        t = telem(r)
        out["replies_examined"] += 1
        for k in ("labels_seen", "labels_with_a_fence_within_3_lines",
                  "blocks_recovered", "recovered_only_by_the_companion"):
            out[k] += t[k]
        if stop_at_fenced and out["labels_with_a_fence_within_3_lines"] >= stop_at_fenced:
            break
    out["labels_without_a_fence"] = (out["labels_seen"]
                                     - out["labels_with_a_fence_within_3_lines"])
    return out


def wilson_closed_form(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """The Wilson score interval, written out, as the 2nd implementation."""
    if n == 0:
        return (math.nan, math.nan)
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = (z / (1 + z * z / n)) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, centre - half), min(1.0, centre + half))


def rates(s: dict) -> dict:
    """Both recovery rates, each with Wilson intervals from 2 implementations."""
    from statsmodels.stats.proportion import proportion_confint
    out = {}
    for name, denom in (("over_fenced_labels", s["labels_with_a_fence_within_3_lines"]),
                        ("over_raw_labels", s["labels_seen"])):
        if not denom:
            out[name] = None
            continue
        k = min(s["blocks_recovered"], denom)
        lo, hi = proportion_confint(k, denom, method="wilson")
        lo2, hi2 = wilson_closed_form(k, denom)
        out[name] = {"k": k, "n": denom, "rate": k / denom,
                     "wilson": (lo, hi), "wilson_closed_form": (lo2, hi2),
                     "agree_to": max(abs(lo - lo2), abs(hi - hi2))}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stop-at-fenced", type=int, default=0,
                    help="stop once this many fenced labels are seen (0 = read all)")
    ap.add_argument("--tracked-only", action="store_true",
                    help="read only files git tracks, as a fresh clone would")
    a = ap.parse_args(argv)

    tracked = tracked_files()
    files, aliases = population(tracked_only=a.tracked_only, tracked=tracked)
    s = scan(files, stop_at_fenced=a.stop_at_fenced or None)
    read = files[:s["files_read"]]
    rel = [str(f.relative_to(REPO.resolve())) for f in read]
    digest = hashlib.sha256("\n".join(sorted(rel)).encode("utf-8")).hexdigest()

    print(f"population: {GLOB}, reverse lexical order of path"
          f"{', tracked files only' if a.tracked_only else ''}")
    print(f"  distinct files matched  : {len(files)}")
    print(f"  symlink aliases skipped : {aliases}")
    print(f"  files read              : {s['files_read']}"
          f"{f' (stopped at {a.stop_at_fenced} fenced labels)' if a.stop_at_fenced else ''}")
    if tracked is None:
        print("  tracked by git          : unknown (git ls-files failed)")
    else:
        n_tr = sum(1 for r in rel if r in tracked)
        print(f"  tracked by git          : {n_tr} of {len(rel)} read")
    print(f"  sha256 of sorted list   : {digest}")
    print(f"  unreadable              : {s['unreadable']}")
    print()
    print(f"replies carrying FALSIFIER: {s['replies_examined']}")
    print(f"  raw labels              : {s['labels_seen']}")
    print(f"  labels with a fence     : {s['labels_with_a_fence_within_3_lines']}")
    print(f"  labels without a fence  : {s['labels_without_a_fence']}")
    print(f"  blocks recovered        : {s['blocks_recovered']}")
    print(f"  recovered ONLY by the tolerant companion: "
          f"{s['recovered_only_by_the_companion']}")
    for name, r in rates(s).items():
        if r is None:
            print(f"\nrecovery {name}: no denominator")
            continue
        print(f"\nrecovery {name}: {r['k']} of {r['n']} = {r['rate']:.4%}")
        print(f"  Wilson 95% : [{r['wilson'][0]:.4%}, {r['wilson'][1]:.4%}] (statsmodels)")
        print(f"  Wilson 95% : [{r['wilson_closed_form'][0]:.4%}, "
              f"{r['wilson_closed_form'][1]:.4%}] (closed form, agrees to "
              f"{r['agree_to']:.1e})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
