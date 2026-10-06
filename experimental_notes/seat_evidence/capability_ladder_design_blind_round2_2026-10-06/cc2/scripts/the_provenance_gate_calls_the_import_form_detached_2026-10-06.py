# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'capability_ladder_design_blind_cc2_2026-10-06', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: e8edcc0853e5a1c564e9253f88a766e60bfcfe765d6064761a0a75e92a8c7db6
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
r"""`falsifier_style` calls the directive-mandated import form "detached".

THE DEFECT. `scripts/competence_provenance.py::falsifier_style` decides whether a
falsifier READ its target by one regex:

    open\s*\(|read_text|\.read\s*\(|linecache|getlines

A falsifier that reaches its target the way the CDSFL falsifier-integrity directive
REQUIRES -- "Import the REAL target module (e.g. `from bench.dm._convergence import
...`)" -- calls none of those names. It is therefore classified `detached`, the same
label given to a falsifier that opens nothing and restates the document from memory.

WHY IT IS ABOVE THRESHOLD. `competence_provenance.py` is not a report. Its own
docstring, and `bench/routing.py` lines 58-60, make it the gate that must run before
the capability ladder is re-derived: it "exits 2 and prints UNSAFE TO RANK ON when a
model's confirmations rest on falsifiers that never read the target". The founder has
ruled (2026-10-06) that the ladder must become a measured statistic. Implemented on
top of this classifier, the measured ladder would rank models by whether they reach
the target with `open()` rather than with `import` -- the inverse of the directive --
and, because the misclassified population is the majority, the gate refuses nearly
every corpus as UNSAFE TO RANK ON, so the measured ladder cannot be derived at all.

MEASURED over the 59 archived `bench/logs/*/runner_state.json` corpora: see the
MEASUREMENT block printed by this script. Headline: 630 of 1078 non-empty falsifiers
import a repository module yet are classified `detached`; only 130 are truly
detached. Wilson 95% intervals and a statsmodels cross-check are printed per figure.

THIS SCRIPT IS BOTH the runnable falsifier and the measurement. It imports the REAL
`scripts/competence_provenance.py` -- it does not retype `falsifier_style` -- and it
reads only the repository's own archived run state. It reads no scoring key, no
answer file and no planted-defect manifest.

Run:  python3 scripts/the_provenance_gate_calls_the_import_form_detached_2026-10-06.py
      python3 scripts/the_provenance_gate_calls_the_import_form_detached_2026-10-06.py --falsifier-only
"""
from __future__ import annotations

import argparse
import collections
import glob
import importlib.util
import json
import math
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

# Exactly the form the falsifier-integrity directive names as REQUIRED.
DIRECTIVE_MANDATED_FORM = (
    "from bench.dm._convergence import gamma_critical\n"
    "assert gamma_critical is not None\n"
)

# A repository-module import, any of the real top-level packages.
IMPORTS_REPO_MODULE = re.compile(
    r"^\s*(?:from|import)\s+(?:bench|scripts|explorer|hooks|resources)\b", re.M)


def _load_real_gate():
    """Import the REAL scripts/competence_provenance.py. No reimplementation."""
    path = REPO / "scripts" / "competence_provenance.py"
    spec = importlib.util.spec_from_file_location("competence_provenance", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# -----------------------------------------------------------------------------
# FALSIFIER
# -----------------------------------------------------------------------------

def falsifier() -> None:
    """Fails iff `falsifier_style` labels the import form "detached".

    Exits cleanly (no raise, no FALSIFIED) if the classifier is repaired to
    recognise a repository-module import as reaching its target.
    """
    gate = _load_real_gate()
    verdict = gate.falsifier_style(DIRECTIVE_MANDATED_FORM)
    if verdict == "detached":
        print("FALSIFIED")
        raise AssertionError(
            "falsifier_style() returned 'detached' for the falsifier form the "
            "CDSFL falsifier-integrity directive mandates verbatim:\n"
            f"{DIRECTIVE_MANDATED_FORM!r}\n"
            "A falsifier that imports the real target module is the canonical "
            "admissible form, yet it is scored identically to one that opens "
            "nothing. This is the classifier that gates ladder re-derivation."
        )
    print(f"defect absent: falsifier_style returned {verdict!r} for the import form")


# -----------------------------------------------------------------------------
# MEASUREMENT
# -----------------------------------------------------------------------------

def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple:
    """Wilson score interval, closed form. Cross-checked against statsmodels."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def _wilson_crosscheck(k: int, n: int) -> str:
    try:
        from statsmodels.stats.proportion import proportion_confint
        lo2, hi2 = proportion_confint(k, n, alpha=0.05, method="wilson")
    except Exception as exc:  # pragma: no cover - tool absent
        return f"statsmodels unavailable ({exc})"
    lo1, hi1 = wilson(k, n)
    ok = abs(lo1 - lo2) < 1e-12 and abs(hi1 - hi2) < 1e-12
    return (f"closed form [{lo1:.6f}, {hi1:.6f}] | statsmodels "
            f"[{lo2:.6f}, {hi2:.6f}] | agree={ok}")


def measure(logs_glob: str) -> dict:
    gate = _load_real_gate()
    c = collections.Counter()
    for p in sorted(glob.glob(logs_glob)):
        try:
            j = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        for _fid, e in ((j.get("registry") or {}).get("entries") or {}).items():
            code = e.get("falsifier_code")
            if code is None:
                continue
            if not str(code).strip():
                c["empty"] += 1
                continue
            c["nonempty"] += 1
            style = gate.falsifier_style(code)          # the REAL classifier
            imports = bool(IMPORTS_REPO_MODULE.search(code))
            if style == "reads":
                c["classified_reads"] += 1
            if imports:
                c["imports_repo_module"] += 1
            if style == "detached" and imports:
                c["misclassified"] += 1
            if style == "detached" and not imports:
                c["truly_detached"] += 1
    return dict(c)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--falsifier-only", action="store_true")
    ap.add_argument("--logs",
                    default=str(REPO / "bench" / "logs" / "*" / "runner_state.json"))
    args = ap.parse_args(argv)

    print("=" * 78)
    print("FALSIFIER - falsifier_style() on the directive-mandated import form")
    print("=" * 78)
    try:
        falsifier()
        failed = False
    except AssertionError as exc:
        print(f"AssertionError: {exc}")
        failed = True
    if args.falsifier_only:
        return 1 if failed else 0

    print()
    print("=" * 78)
    print("MEASUREMENT - archived falsifier corpus, classified by the REAL gate")
    print("=" * 78)
    c = measure(args.logs)
    n = c.get("nonempty", 0)
    for key in ("empty", "nonempty", "classified_reads", "imports_repo_module",
                "misclassified", "truly_detached"):
        k = c.get(key, 0)
        if key in ("empty", "nonempty"):
            print(f"  {key:24s} {k:5d}")
            continue
        lo, hi = wilson(k, n)
        print(f"  {key:24s} {k:5d}/{n} = {k / n:.4%}  Wilson95 [{lo:.4%}, {hi:.4%}]")
        print(f"  {'':24s} {_wilson_crosscheck(k, n)}")
    print()
    print("  INTERPRETATION: `misclassified` counts falsifiers that reach the real")
    print("  target by import -- the form the directive mandates -- and are scored")
    print("  by the ladder-derivation gate as if they had read nothing.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
