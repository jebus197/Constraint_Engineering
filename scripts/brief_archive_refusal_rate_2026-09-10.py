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

`--split YYYY-MM-DD` (panel round 16, 2026-09-17) answers a different question:
how many briefs dated BEFORE the format ruling fail its SHAPE checks, against how
many dated on or after it. It calls `validate()` alone. The default mode also
re-executes every declared figure, and a figure that was right at dispatch can
drift afterwards as the corpus it counts grows, so the default aggregate mixes 2
causes and is not this split. A brief's date is the first YYYY-MM-DD, or else
the first valid compact YYYYMMDD, in its path under bench/logs/; a brief with
neither is reported as undated and counted in neither group.
"""
import argparse
import datetime
import math
import pathlib
import re
import statistics
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
VALIDATOR = REPO / "scripts" / "panel_brief_validate.py"
COUNT = re.compile(r"fails (\d+) required check\(s\)")
RULING = "2026-09-09"

_ISO = re.compile(r"(20\d\d)-(\d\d)-(\d\d)")
_COMPACT = re.compile(r"(?<!\d)(20\d\d)(\d\d)(\d\d)(?!\d)")


def brief_date(rel: str) -> "str | None":
    """The date a brief's directory carries, as YYYY-MM-DD, or None."""
    for rx in (_ISO, _COMPACT):
        for m in rx.finditer(rel):
            try:
                return datetime.date(*map(int, m.groups())).isoformat()
            except ValueError:
                continue
    return None


def _wilson(k: int, n: int) -> "tuple[float, float]":
    z = 1.959963984540054
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centre - half), min(1.0, centre + half)


def _clopper_pearson(k: int, n: int) -> "tuple[float, float]":
    def at_most(q, j):
        return math.fsum(math.comb(n, i) * q ** i * (1 - q) ** (n - i) for i in range(j + 1))

    def root(f):
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if f(mid) > 0 else (lo, mid)
        return (lo + hi) / 2

    return (0.0 if k == 0 else root(lambda q: 0.025 - (1 - at_most(q, k - 1))),
            1.0 if k == n else root(lambda q: at_most(q, k) - 0.025))


def split(cut: str) -> int:
    import importlib.util
    spec = importlib.util.spec_from_file_location("panel_brief_validate_split", VALIDATOR)
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    logs = REPO / "bench" / "logs"
    briefs = sorted(logs.rglob("BRIEF.md"))
    if not briefs:
        print("no BRIEF.md found", file=sys.stderr)
        return 1
    groups = {f"dated before {cut}": [], f"dated on or after {cut}": []}
    undated = []
    for b in briefs:
        rel = str(b.relative_to(logs))
        d = brief_date(rel)
        failed = len(v.validate(b.read_text(encoding="utf-8", errors="replace")))
        if d is None:
            undated.append(rel)
        else:
            groups[f"dated before {cut}" if d < cut else f"dated on or after {cut}"].append(failed)
    from statsmodels.stats.proportion import proportion_confint
    print(f"split at {cut}: shape checks only (validate()), declared figures NOT re-executed")
    print(f"archived briefs: {len(briefs)}")
    for label, fails in groups.items():
        n = len(fails)
        k = sum(1 for f in fails if f)
        if not n:
            print(f"  {label:28s}: 0 briefs")
            continue
        refused = [f for f in fails if f]
        span = f", failing {min(refused)} to {max(refused)} check(s)" if refused else ""
        print(f"  {label:28s}: refused {k} of {n} = {k / n:.4%}{span}")
        wl, wh = proportion_confint(k, n, method="wilson")
        cl, ch = proportion_confint(k, n, method="beta")
        wl2, wh2 = _wilson(k, n)
        cl2, ch2 = _clopper_pearson(k, n)
        print(f"      Wilson 95%          : [{wl:.4%}, {wh:.4%}]  (statsmodels; closed "
              f"form agrees to {max(abs(wl - wl2), abs(wh - wh2)):.1e})")
        print(f"      Clopper-Pearson 95% : [{cl:.4%}, {ch:.4%}]  (statsmodels; math.comb "
              f"bisection agrees to {max(abs(cl - cl2), abs(ch - ch2)):.1e})")
    print(f"  undated, in neither group   : {len(undated)} {undated}")
    return 0


def _load(name, path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _mirror():
    """The mirror module, or None where it is absent.

    ADDED 2026-09-17: `briefs()` and `per_check()` load it to read the tracked
    mirror as well as the live `bench/logs/`, and a tree that holds this script
    without it -- a test fixture, an extracted copy -- must still run rather
    than raise."""
    path = REPO / "scripts" / "mirror_panel_records_2026-09-11.py"
    return _load("mirror_records", path) if path.is_file() else None


def briefs() -> list[tuple[str, pathlib.Path]]:
    """(round name, brief path) for every archived round that holds a brief."""
    mir = _mirror()
    if mir is None:
        return [(b.parent.name, b) for b in sorted((REPO / "bench" / "logs").rglob("BRIEF.md"))]
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
    mir = _mirror()
    labels = [label for label, _, _ in pbv.CHECKS]
    out = {}
    for side in ("pre", "post"):
        out[side] = {"n": 0, "refused": 0, "fix_and_tested": 0,
                     "meets": {label: 0 for label in labels}}
    for name, text in items:
        dated = (mir.round_date(name) if mir is not None else brief_date(name)) or ""
        side = "post" if dated >= ruling else "pre"
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
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--split", metavar="YYYY-MM-DD",
                    help="report shape-check refusals before and on/after this date")
    a = ap.parse_args()
    if a.split is not None:
        try:
            cut = datetime.date.fromisoformat(a.split).isoformat()
        except ValueError:
            ap.error(f"--split takes a date as YYYY-MM-DD, not {a.split!r}")
        return split(cut)
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
    per = per_check(texts)
    print(f"\nSHAPE CHECKS, PER CHECK, split at the ruling {RULING} "
          f"(validate() in-process; declared figures not re-executed):")
    for side, title in (("pre", "before the ruling (undated included)"),
                        ("post", "on or after the ruling")):
        s = per[side]
        print(f"  {title}: {s['n']} briefs, {s['refused']} fail at least 1 shape check")
        for label, met in s["meets"].items():
            print(f"      meets {label!r}: {met} of {s['n']}")
        print(f"      meets BOTH 'requires a fix' and 'TESTED': {s['fix_and_tested']} of "
              f"{s['n']}; lacking 1 or both: {s['n'] - s['fix_and_tested']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
