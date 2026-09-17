#!/usr/bin/env python3
"""How many archived panel briefs would the committed validator refuse, and why?

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

Task 5.1's entry cites "all 49 archived briefs would be refused, failing 1 to 7
checks, mean 2.4" and names no script. An adversarial review on 2026-09-10 could
not reproduce the spread from the committed validator, so this reproduces it -- or
corrects it -- from the artefacts.

THE COUNT COMES OFF THE VALIDATOR'S OWN REFUSAL LINE, which states the number of
failed checks explicitly. A first attempt counted occurrences of the words
"missing" and "fail" in the output and returned 1.00 for every brief, because the
header contains "fails" exactly once regardless of how many checks failed. That
was the ruler, not the briefs, and it is why this script parses the stated number
instead of inferring one.

PER-CHECK BREAKDOWN, ADDED 2026-09-17 (task P4). Entry P4 said the founder's
point "is still true of 47 of 49 briefs" and no script printed 47. The committed
validator's "requires a fix" and "requires the fix to be TESTED" checks, run over
the 49 briefs dated before the 2026-09-09 ruling, give a different figure, and
`per_check()` now prints it, split at the ruling, for every shape check including
the delivery check added the same day. These are the validator's lexical shape
checks, a looser test than a reader's judgement of whether a brief truly
required a tested fix, so the 2 figures do not measure the same thing.

THE ARCHIVE IS READ LIVE OR MIRRORED (2026-09-17). This read `bench/logs/`
only, which `.gitignore:41` excludes, so in a clone it printed "no BRIEF.md
found" and exited 1. Briefs now come from the mirror module's
`archive_rounds()`, with `BRIEF.md.txt` read where the live `BRIEF.md` is absent.
"""
import pathlib
import re
import statistics
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
VALIDATOR = REPO / "scripts" / "panel_brief_validate.py"
COUNT = re.compile(r"fails (\d+) required check\(s\)")
RULING = "2026-09-09"


def _load(name, path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def briefs() -> list[tuple[str, pathlib.Path]]:
    """(round name, brief path) for every archived round that holds a brief."""
    mir = _load("mirror_records", REPO / "scripts" / "mirror_panel_records_2026-09-11.py")
    out = []
    for d in mir.archive_rounds():
        b = mir.brief_of(d)
        if b is not None:
            out.append((d.name, b))
    return out


def per_check(items, ruling: str = RULING) -> dict:
    """Shape-check outcomes, split at `ruling`, by calling `validate()` in-process.

    `items` is [(round name, brief text)]. Returns {"pre": {...}, "post": {...}},
    each holding n, refused, per-label meet counts under "meets", and
    "fix_and_tested", the briefs meeting both "requires a fix" and "requires the
    fix to be TESTED". Undated rounds count as pre-ruling, as everywhere else.
    Declared figures are NOT re-executed here; this is the shape half only.
    """
    pbv = _load("pbv_breakdown", VALIDATOR)
    mir = _load("mirror_records", REPO / "scripts" / "mirror_panel_records_2026-09-11.py")
    labels = [label for label, _, _ in pbv.CHECKS]
    out = {}
    for side in ("pre", "post"):
        out[side] = {"n": 0, "refused": 0, "fix_and_tested": 0,
                     "meets": {label: 0 for label in labels}}
    for name, text in items:
        side = "post" if (mir.round_date(name) or "") >= ruling else "pre"
        problems = pbv.validate(text)
        failed = {label for label in labels
                  if any(p.startswith(label + ":") for p in problems)}
        s = out[side]
        s["n"] += 1
        s["refused"] += bool(problems)
        for label in labels:
            s["meets"][label] += label not in failed
        s["fix_and_tested"] += not ({"requires a fix, not only a finding",
                                     "requires the fix to be TESTED"} & failed)
    return out


def main() -> int:
    items = briefs()
    if not items:
        print("no BRIEF.md found", file=sys.stderr)
        return 1
    refused, passed, per_brief = [], [], {}
    for name, b in items:
        r = subprocess.run([sys.executable, str(VALIDATOR), str(b)],
                           capture_output=True, text=True)
        out = r.stdout + r.stderr
        m = COUNT.search(out)
        if m:
            n = int(m.group(1))
            refused.append(n)
            per_brief[name] = n
        else:
            passed.append(name)

    n_total = len(items)
    print(f"archived briefs                 : {n_total}")
    print(f"REFUSED by the committed validator: {len(refused)}")
    print(f"accepted                        : {len(passed)}  {passed}")
    if refused:
        print(f"failed checks per refused brief : min {min(refused)}, "
              f"max {max(refused)}, mean {statistics.mean(refused):.2f}, "
              f"median {statistics.median(refused)}")
        import collections
        for k, v in sorted(collections.Counter(refused).items()):
            print(f"   {v:3d} brief(s) fail {k} check(s)")

    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import beta as sb
    k, n = len(refused), n_total
    lo, hi = proportion_confint(k, n, method="wilson")
    lo2 = 0.0 if k == 0 else sb.ppf(0.025, k, n - k + 1)
    hi2 = 1.0 if k == n else sb.ppf(0.975, k + 1, n - k)
    print(f"\nrefusal rate: {k}/{n} = {k/n:.4f}")
    print(f"  Wilson 95%          [{lo*100:.1f}%, {hi*100:.1f}%]   (statsmodels)")
    print(f"  Clopper-Pearson 95% [{lo2*100:.1f}%, {hi2*100:.1f}%]   (scipy)")

    import numpy as np, mpmath as mp
    mp.mp.dps = 20
    if refused:
        print(f"  mean cross-check: numpy {np.mean(refused):.6f} | "
              f"mpmath {mp.nstr(mp.fsum([mp.mpf(x) for x in refused])/len(refused), 8)}")

    texts = [(name, b.read_text(encoding="utf-8", errors="replace")) for name, b in items]
    split = per_check(texts)
    print(f"\nSHAPE CHECKS, PER CHECK, split at the ruling {RULING} "
          f"(validate() in-process; declared figures not re-executed):")
    for side, title in (("pre", "before the ruling (undated included)"),
                        ("post", "on or after the ruling")):
        s = split[side]
        print(f"  {title}: {s['n']} briefs, {s['refused']} fail at least 1 shape check")
        for label, met in s["meets"].items():
            print(f"      meets {label!r}: {met} of {s['n']}")
        print(f"      meets BOTH 'requires a fix' and 'TESTED': {s['fix_and_tested']} of "
              f"{s['n']}; lacking 1 or both: {s['n'] - s['fix_and_tested']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
