#!/usr/bin/env python3
"""Which of the 245 commits' changes are SIMULATION-ONLY and must not reach main.

HIS QUESTION, 2026-10-16: *"give me your view if it is safe to move everything we
have learned from our simulated experiments to our main branch, and then to
switch back to using the main branch from there? Care must be taken to ensure
that work that is only applicable to our simulated experiments, doesn't get
carried over to main, so that our live/real experiments can work as expected.
You should probably survey and enumerate everything to ensure this can happen,
although I suspect the vast majority of the lessons we have learned are indeed
applicable to main?"*

WHY A SCRIPT. 1,242 paths differ. Deciding by recollection which of them are
simulation scaffolding is exactly the operation this project has recorded going
wrong, and `measured-rate-travels-with-its-script` requires the producer to be
committed beside any figure quoted from it.

THE CLASSIFICATION, AND WHAT IT DELIBERATELY REFUSES TO DO. A path is called
SIMULATION-ONLY only on EVIDENCE IN ITS OWN NAME OR CONTENT -- the stand-in
dispatch shim, the simulated launcher, a `-SIM` fingerprint, a simulated run's
log directory. Everything else is reported as MAIN-APPLICABLE or as NEEDS
READING. A topic word is not enough: "sim" appears inside "similarity" and
"simple", so a bare substring test would sweep in unrelated files, which is the
shape of defect recorded in `feedback_check_the_whole_set`. It therefore
UNDER-reports the simulation surface and lists the residue for reading rather
than guessing either way.

THE RISK THAT MATTERS MOST IS NOT A FILE, IT IS STATE. A simulated run writes
fingerprints and immune memory. If a simulated run's numbers reach main, the
LIVE runner will route and gate on evidence no paid model produced. B7 was the
repair for exactly that, so this script checks the real seats' fingerprints
against main rather than assuming the repair held.

It reads only. Nothing is merged, moved or deleted by this script.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from _cli_help import answer_help                                  # noqa: E402

BASE = "origin/main"

#: Paths that exist to run a SIMULATED experiment and nothing else.
SIM_ONLY_EXACT = (
    "bench/tools/sim_dispatch_shim.py",
    "bench/tools/run_simulated_experiment.py",
)
#: Directory prefixes whose contents are a simulated run's own output.
SIM_ONLY_PREFIX = ("bench/logs/",)
#: A simulated seat's fingerprint. The REAL seats' files are checked separately.
SIM_FINGERPRINT = re.compile(r"^bench/fingerprints/.*-SIM\.json$")
#: The real paid seats. A simulated run must never move these.
REAL_FINGERPRINT = re.compile(r"^bench/fingerprints/(CC2|ChatGPT|Codex|Gemini"
                              r"|DeepSeek|Fable)\.json$")
#: Live state a simulated run writes.
SHARED_STATE = ("bench/state/immune_memory.json",)


def sh(*args: str) -> str:
    return subprocess.run(args, capture_output=True, text=True).stdout


def changed() -> list[str]:
    out = sh("git", "diff", "--name-only", f"{BASE}...HEAD")
    return [l.strip() for l in out.splitlines() if l.strip()]


def interval(k: int, n: int) -> str:
    if n == 0:
        return "n=0"
    from statsmodels.stats.proportion import proportion_confint
    lo_w, hi_w = proportion_confint(k, n, alpha=0.05, method="wilson")
    lo_c, hi_c = proportion_confint(k, n, alpha=0.05, method="beta")
    import scipy.stats as st
    z = st.norm.ppf(0.975)
    p, d = k / n, 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    assert max(abs(lo_w - (c - h)), abs(hi_w - (c + h))) < 1e-9, "routes disagree"
    return (f"{100 * k / n:.4f}%  Wilson [{100 * lo_w:.4f}%, {100 * hi_w:.4f}%]"
            f"  Clopper-Pearson [{100 * lo_c:.4f}%, {100 * hi_c:.4f}%]")


def classify(paths: list[str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {
        "SIM-ONLY ENTRY POINTS": [],
        "SIM RUN ARTEFACTS": [],
        "SIM SEAT FINGERPRINTS": [],
        "REAL SEAT FINGERPRINTS — MUST NOT HAVE MOVED": [],
        "SHARED LIVE STATE — READ THE DIFF": [],
        "MAIN-APPLICABLE": [],
    }
    for p in paths:
        if p in SIM_ONLY_EXACT:
            out["SIM-ONLY ENTRY POINTS"].append(p)
        elif any(p.startswith(x) for x in SIM_ONLY_PREFIX):
            out["SIM RUN ARTEFACTS"].append(p)
        elif SIM_FINGERPRINT.match(p):
            out["SIM SEAT FINGERPRINTS"].append(p)
        elif REAL_FINGERPRINT.match(p):
            out["REAL SEAT FINGERPRINTS — MUST NOT HAVE MOVED"].append(p)
        elif p in SHARED_STATE:
            out["SHARED LIVE STATE — READ THE DIFF"].append(p)
        else:
            out["MAIN-APPLICABLE"].append(p)
    return out


def main() -> int:
    ahead = sh("git", "rev-list", "--count", f"{BASE}..HEAD").strip()
    behind = sh("git", "rev-list", "--count", f"HEAD..{BASE}").strip()
    paths = changed()
    print("=" * 78)
    print("1. THE DIVERGENCE")
    print("=" * 78)
    print(f"  commits this branch has that main lacks : {ahead}")
    print(f"  commits main has that this branch lacks : {behind}"
          f"   -> a MERGE, not a fast-forward" if behind != "0" else "")
    print(f"  paths differing                          : {len(paths)}")

    buckets = classify(paths)
    print()
    print("=" * 78)
    print("2. THE CLASSIFICATION")
    print("=" * 78)
    for name, items in buckets.items():
        print(f"  {name}: {len(items)}")
    sim = sum(len(buckets[k]) for k in
              ("SIM-ONLY ENTRY POINTS", "SIM RUN ARTEFACTS",
               "SIM SEAT FINGERPRINTS"))
    print()
    print(f"  SIMULATION SURFACE: {sim} of {len(paths)} paths")
    print(f"    {interval(sim, len(paths))}")
    print(f"  MAIN-APPLICABLE:    {len(buckets['MAIN-APPLICABLE'])} of {len(paths)}")
    print(f"    {interval(len(buckets['MAIN-APPLICABLE']), len(paths))}")

    print()
    print("  THE SIM-ONLY ENTRY POINTS, in full:")
    for p in buckets["SIM-ONLY ENTRY POINTS"]:
        print(f"    {p}")

    print()
    print("=" * 78)
    print("3. THE RISK THAT IS NOT A FILE: DID A SIMULATED RUN MOVE REAL STATE?")
    print("=" * 78)
    real = buckets["REAL SEAT FINGERPRINTS — MUST NOT HAVE MOVED"]
    if not real:
        print("  0 real-seat fingerprints differ from main. B7's repair held.")
    else:
        print(f"  *** {len(real)} REAL-SEAT FINGERPRINT(S) DIFFER FROM MAIN ***")
        for p in real:
            diff = sh("git", "diff", "--numstat", f"{BASE}...HEAD", "--", p).strip()
            print(f"    {p}   numstat: {diff}")
        print("  A simulated run must never move a paid seat's recorded capacity.")
    for p in buckets["SHARED LIVE STATE — READ THE DIFF"]:
        print(f"  shared state differs: {p}")
        print("    This is immune persistence working as designed -- the memory")
        print("    LEARNS from runs -- but the numbers now in it were produced by")
        print("    SIMULATED seats, so carrying it to main means the live runner")
        print("    inherits priors no paid model produced. HIS DECISION.")
    return 0


if __name__ == "__main__":
    answer_help(__doc__, __file__)
    raise SystemExit(main())
