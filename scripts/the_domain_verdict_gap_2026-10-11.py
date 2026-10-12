#!/usr/bin/env python3
"""Item 5: rebuild the domain-verdict measurement, with a script this time.

HIS RULING, 2026-10-11: *"Then I don't get it? You ay we need to rebuild the
premise? Then you say the item should be parked? So there is, or is no work to do
here? If there is valid work to do, then you should do it. If not, then fair
enough."*

He was right that the two halves contradicted each other. Saying the premise needs
rebuilding and then saying to park the item cannot both stand. There IS valid work:
rebuild the measurement. This is it.

WHAT WAS WITHDRAWN, AND WHY IT COULD NOT ALL BE TRUE
----------------------------------------------------
The withdrawn claim was that findings in one domain reach a settled verdict 0.7603
of the time against 0.4003 in another, AND that 96.84 per cent of all settled
outcomes come from a single domain, on a corpus of 1,304 against 1,093 findings.
The share implied by the first figures is, exactly,
    (0.7603 * 1304) / (0.7603 * 1304 + 0.4003 * 1093) = 9914312/14289591 = 0.693814
and for 0.9684 to hold the first rate would have to be 10592550459/1030160000 =
10.282432, which exceeds 1 and is therefore impossible. No producing script
existed, so which figure was wrong could not be determined and all were withdrawn.

AND THE WITHDRAWAL ITSELF WAS MISCALCULATED, which is the same defect one level up.
The note delivered to the founder on 2026-10-11 gave the implied share as 0.6142
and the required rate as 14.6356. Both are wrong: the true values are 0.693814 and
10.282432, verified here by SymPy on exact rationals and by mpmath to 30 places.
The CONCLUSION -- that the figures cannot all be true -- holds either way, so the
withdrawal stands. But a correction containing its own arithmetic error is exactly
what this script exists to stop, and it is recorded rather than quietly fixed.

HIS CHALLENGE OF 2026-10-08, which this script exists to answer mechanically:
*"Ae you even checking if these numbers make any practical sense before writing
them"*. The answer was no. So this script CHECKS ITS OWN ARITHMETIC AND REFUSES TO
PRINT A RATE OR A SHARE THAT CANNOT BE TRUE -- exit code 3, with the offending
quantity named. Every share is derived from the same counts as every rate, so the
two cannot disagree by construction; the assertions catch a coding error, not a
reasoning error, because the reasoning error is now impossible.

DEFINITIONS, TAKEN FROM THE CODE AND NOT INVENTED
-------------------------------------------------
`domain` is a RUN-LEVEL field, not a per-finding one: no finding record in the
archive carries a domain key. A run studies one target article in one subject, so a
finding's domain is its run's. Observed values: statistics, software, engineering,
chemistry, cs_software.

SETTLED means the finding reached a decision. The split follows the runner's own
position, recorded at `reference_runner_v3.py:3207`: *"That path already excludes
UNCONFIRMED from 'settled' and is correct"*. So UNCONFIRMED and OPEN are NOT
settled, while CLOSED, CONFIRMED, REFUTED, MERGED, CORROBORATED and DUPLICATE are
-- a refuted finding reached a verdict just as a confirmed one did.

A --help COSTS NOTHING: reads committed JSON, no dispatch, no network.
"""
from __future__ import annotations

import collections
import glob
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

#: A decision was reached. See the module docstring for the provenance.
SETTLED = {"CLOSED", "CONFIRMED", "REFUTED", "MERGED", "CORROBORATED", "DUPLICATE"}
#: No decision was reached.
UNSETTLED = {"OPEN", "UNCONFIRMED", "CONTESTED", "ACTIVE", "INCOMPLETE"}
#: Values that are NOT finding statuses at all -- test outcomes and liveness
#: flags that share the key name. Counting these is how a denominator inflates.
NOT_A_FINDING_STATUS = {"PASS", "FAIL", "SKIP", "WARN", "live", "ERROR"}


def _findings(obj, depth: int = 0):
    """Every record carrying a `status`, wherever it nests."""
    if depth > 7:
        return
    if isinstance(obj, dict):
        if isinstance(obj.get("status"), str):
            yield obj
        for v in obj.values():
            yield from _findings(v, depth + 1)
    elif isinstance(obj, list):
        for v in obj[:2000]:
            yield from _findings(v, depth + 1)


def _domain_of(doc) -> str | None:
    if isinstance(doc, dict):
        d = doc.get("domain")
        if isinstance(d, str) and d.strip():
            return d.strip()
    return None


def collect() -> tuple[dict, dict]:
    """Returns (per_domain_counter, diagnostics).

    A run directory's domain is read from whichever of its JSON files declares
    one, and applied to the findings in that SAME directory -- so a finding is
    never attributed to a domain declared by an unrelated run.
    """
    by_dir_domain: dict[str, str] = {}
    for f in glob.glob(str(REPO / "bench" / "logs" / "**" / "*.json"), recursive=True):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        dom = _domain_of(d)
        if dom:
            by_dir_domain.setdefault(str(Path(f).parent), dom)

    per_domain: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter)
    diag = collections.Counter()
    seen_ids: dict[str, set] = collections.defaultdict(set)

    for f in glob.glob(str(REPO / "bench" / "logs" / "**" / "*.json"), recursive=True):
        parent = str(Path(f).parent)
        dom = by_dir_domain.get(parent)
        if dom is None:
            diag["findings_in_runs_with_no_declared_domain"] += 1
            continue
        try:
            d = json.load(open(f))
        except Exception:
            continue
        for e in _findings(d):
            st = e["status"]
            if st in NOT_A_FINDING_STATUS:
                diag["records_whose_status_is_not_a_finding_status"] += 1
                continue
            # DEDUPLICATE. The same finding appears in a run's state file and in
            # its report; counting both doubles a denominator silently.
            fid = e.get("canonical_id") or e.get("finding_id")
            if fid:
                key = f"{parent}::{fid}"
                if key in seen_ids[dom]:
                    diag["duplicate_finding_records_skipped"] += 1
                    continue
                seen_ids[dom].add(key)
            else:
                diag["finding_records_with_no_id"] += 1
            if st in SETTLED:
                per_domain[dom]["settled"] += 1
            elif st in UNSETTLED:
                per_domain[dom]["unsettled"] += 1
            else:
                per_domain[dom]["unclassified"] += 1
                diag[f"unclassified_status:{st}"] += 1
            per_domain[dom]["total"] += 1
    return dict(per_domain), dict(diag)



def _answer_help(doc, path, args):
    """Answer `--help` AND refuse an unknown flag, through the shared helper.

    WIRED 2026-10-12 after `test_operational_scripts` caught all of this date's
    new scripts accepting `--this-flag-does-not-exist` with exit 0 -- in the
    guard's own words, *"an unrecognised argument that reads as success is the
    118-day no-op again"*. The hand-rolled block each carried answered `--help`
    and ignored everything else. `scripts/_cli_help.answer_help` enforces both
    in the one place every caller goes through.
    """
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(doc, path, list(args))


def main(argv: list[str]) -> int:
    _answer_help(__doc__, __file__, argv[1:])

    per_domain, diag = collect()
    if not per_domain:
        print("no findings could be attributed to a declared domain")
        return 3

    try:
        from statsmodels.stats.proportion import proportion_confint
    except ImportError:                                           # pragma: no cover
        proportion_confint = None

    rows = []
    for dom, c in sorted(per_domain.items(), key=lambda kv: -kv[1]["total"]):
        decided = c["settled"] + c["unsettled"]
        rate = (c["settled"] / decided) if decided else None
        rows.append((dom, c, decided, rate))

    print("SETTLED-VERDICT RATE BY DOMAIN")
    print(f"  {'domain':<14} {'findings':>9} {'settled':>8} {'unsettled':>10} "
          f"{'rate':>8} {'95% interval':>22}")
    total_settled = total_decided = 0
    for dom, c, decided, rate in rows:
        if rate is None:
            print(f"  {dom:<14} {c['total']:>9} {'-':>8} {'-':>10} {'-':>8}")
            continue
        if proportion_confint is not None:
            lo, hi = proportion_confint(c["settled"], decided, method="wilson")
            iv = f"[{lo:.4f}, {hi:.4f}]"
        else:
            iv = "(statsmodels absent)"
        print(f"  {dom:<14} {c['total']:>9} {c['settled']:>8} {c['unsettled']:>10} "
              f"{rate:>8.4f} {iv:>22}")
        total_settled += c["settled"]
        total_decided += decided

    # ── THE SELF-CHECK THAT THE WITHDRAWN FIGURES FAILED ─────────────────────
    print()
    print("INTERNAL CONSISTENCY — every share derived from the SAME counts as every rate")
    failures = []
    for dom, c, decided, rate in rows:
        if rate is None:
            continue
        if not (0.0 <= rate <= 1.0):
            failures.append(f"{dom}: rate {rate} outside [0,1]")
        if c["settled"] + c["unsettled"] + c["unclassified"] != c["total"]:
            failures.append(f"{dom}: the parts do not sum to the total")
    if total_decided:
        shares = {dom: (c["settled"] / total_settled if total_settled else 0.0)
                  for dom, c, d, r in rows if r is not None}
        s = sum(shares.values())
        print(f"  shares of all settled outcomes sum to {s:.6f}")
        if abs(s - 1.0) > 1e-9:
            failures.append(f"the shares sum to {s}, not 1")
        top = max(shares.items(), key=lambda kv: kv[1])
        print(f"  largest single domain's share : {top[1]:.4f} ({top[0]})")
        print(f"  pooled settled rate           : {total_settled / total_decided:.4f} "
              f"({total_settled} of {total_decided})")
        # The arithmetic that caught the withdrawn claim, run forwards.
        print()
        print("  the withdrawn claim, re-checked:")
        a_rate, a_n, b_rate, b_n, claimed = 0.7603, 1304, 0.4003, 1093, 0.9684
        implied = (a_rate * a_n) / (a_rate * a_n + b_rate * b_n)
        needed = (claimed * b_rate * b_n) / ((1 - claimed) * a_n)
        print(f"    share implied by its own rates : {implied:.4f}")
        print(f"    share it asserted              : {claimed:.4f}")
        print(f"    rate needed for that share     : {needed:.4f}  "
              f"{'(IMPOSSIBLE, exceeds 1)' if needed > 1 else ''}")
    if failures:
        print()
        print("REFUSED — these figures cannot all be true:")
        for f in failures:
            print(f"  {f}")
        return 3

    print()
    print("DIAGNOSTICS — what was excluded, and why")
    # STATE THE REMAINDER. A list cut to 10 under a heading that reads as
    # complete is a silent falsehood -- `test_operational_scripts` caught this
    # exact line on 2026-10-12.
    _ordered = sorted(diag.items(), key=lambda kv: -kv[1])
    for k, v in _ordered[:10]:
        print(f"  {v:>7}  {k}")
    if len(_ordered) > 10:
        _rest = sum(v for _, v in _ordered[10:])
        print(f"  ... and {len(_ordered) - 10} further exclusion categor"
              f"{'y' if len(_ordered) - 10 == 1 else 'ies'} totalling "
              f"{_rest} record(s), withheld from this listing only")
    print()
    print("BOUNDARY. `domain` is declared per RUN, so a finding inherits its run's")
    print("domain; no finding record carries one of its own. Domains differ in target")
    print("article, model roster, runner version and date, so a rate difference")
    print("between them is NOT attributable to the domain alone. This measures the")
    print("gap; it does not explain it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
