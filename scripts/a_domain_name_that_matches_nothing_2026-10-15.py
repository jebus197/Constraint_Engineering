#!/usr/bin/env python3
"""How often does a configured domain name silently contribute NO domain directive?

FOUND 2026-10-15 while choosing the domain for the 2 free runs. The launcher's
own resume command uses `--domain statistics`, and there is no `statistics`
directory under `bench/directives/`, so `_load_domain_directive` returns `None`
and the composition carries NO DOMAIN LAYER AT ALL. Nothing says so.

WHY IT MATTERS IN THE FOUNDER'S OWN TERMS, 2026-10-14: *"The whole point of
measuring what our models can do and then giving them exactly the kind of work
they are best suited to, is that no resource and no model's capabilities are
wasted."* A run naming a domain that matches nothing wastes the entire domain
layer, and a reader of the manifest cannot tell that from a run whose domain
simply had little to say -- the manifest records `"domain": "statistics"` either
way.

WHAT IS COUNTED: every `"domain"` value in every shipped `bench/exp*_configs/*.json`,
resolved through the LIVE `_load_domain_directive` rather than by comparing
strings, because the resolver globs for `*.txt` inside the directory and a
directory that exists but is empty also returns `None`.
"""
from __future__ import annotations

import collections
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scipy.stats import beta as scipy_beta                       # noqa: E402
from statsmodels.stats.proportion import proportion_confint       # noqa: E402

from bench.cdsfl_registry import composer as C                    # noqa: E402


def interval(k: int, n: int) -> str:
    if n == 0:
        return "n=0"
    lo_w, hi_w = proportion_confint(k, n, alpha=0.05, method="wilson")
    lo_cp = 0.0 if k == 0 else float(scipy_beta.ppf(0.025, k, n - k + 1))
    hi_cp = 1.0 if k == n else float(scipy_beta.ppf(0.975, k + 1, n - k))
    return (f"{100.0 * k / n:.4f}%  Wilson [{100*lo_w:.4f}%, {100*hi_w:.4f}%]"
            f"  Clopper-Pearson [{100*lo_cp:.4f}%, {100*hi_cp:.4f}%]")


def _domains_in_configs():
    """Every `domain` value any shipped config names, with its file."""
    out = []
    for path in sorted(REPO.glob("bench/exp*_configs/*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                if isinstance(node.get("domain"), str):
                    out.append((path.name, node["domain"]))
                stack.extend(node.values())
            elif isinstance(node, list):
                stack.extend(node)
    return out


def main() -> int:
    shipped = sorted(
        p.name for p in (REPO / "bench" / "directives").iterdir()
        if p.is_dir() and p.name != "universal"
    )
    print("=" * 78)
    print("A DOMAIN NAME THAT MATCHES NOTHING CONTRIBUTES NOTHING, SILENTLY")
    print("=" * 78)
    print(f"shipped domain directories ({len(shipped)}): {', '.join(shipped)}")
    print()

    rows = _domains_in_configs()
    counts = collections.Counter(d for _f, d in rows)
    print(f"{'domain named by a config':<24}{'uses':>6}  resolves?  chars")
    resolved = unresolved = 0
    for name, n in counts.most_common():
        packet = C._load_domain_directive(name, variant=None)
        ok = packet is not None
        resolved += n if ok else 0
        unresolved += 0 if ok else n
        print(f"  {name:<22}{n:>6}  {'YES' if ok else 'NO ':>8}   "
              f"{len(packet.text) if ok else 0}")
    total = resolved + unresolved
    print()
    print(f"config domain references that resolve to a directive: {resolved} of {total}")
    print(f"  {interval(resolved, total)}")
    print(f"config domain references that silently resolve to NOTHING: {unresolved} of {total}")
    print(f"  {interval(unresolved, total)}")
    distinct_bad = [d for d in counts if C._load_domain_directive(d, None) is None]
    print(f"\ndistinct names that match nothing: {len(distinct_bad)} of {len(counts)}"
          f" — {interval(len(distinct_bad), len(counts))}")
    print(f"  {', '.join(sorted(distinct_bad))}")

    print()
    print("THE RUN COMMAND IN THE TRACKER USES `--domain statistics`:")
    for name in ("statistics", "mathematics"):
        packet = C._load_domain_directive(name, variant=None)
        print(f"  {name:<14} -> "
              + (f"{len(packet.text)} chars, {packet.name}" if packet
                 else "None — NO DOMAIN LAYER IS COMPOSED"))
    print()
    print("=" * 78)
    print("NOTHING IS CHANGED BY THIS SCRIPT. It reads the live composer and reports.")
    print("=" * 78)
    return 0


def _answer_help_without_measuring(doc: str) -> None:
    """A `--help` MUST NEVER COST ANYTHING, and that is a founder-standing rule:
    15 of 17 runners once billed a live dispatch on any unrecognised argument.
    This script's measurement is free, but the rule is about the SHAPE: a flag
    that silently runs the whole measurement is indistinguishable from a flag
    that silently spends. Guarded by
    `bench/tests/test_help_is_answered_2026-09-11.py`.
    """
    import argparse
    ap = argparse.ArgumentParser(
        prog=pathlib.Path(__file__).name,
        description=(doc or "").strip().splitlines()[0] if doc else None,
        epilog="Takes no arguments: run it with none to produce the measurement.",
    )
    ap.parse_args()


if __name__ == "__main__":
    _answer_help_without_measuring(__doc__)
    raise SystemExit(main())
