#!/usr/bin/env python3
"""Did the UNRESOLVED section elicit the id-addressed falsifier form in run 1?

THE MEASUREMENT THIS SERVES. `in_round_clearance` is 1 of the programme's
outstanding measurements. Its 2 halves are (a) does in-round falsifier
re-attachment clear A4 blockers while the gate can still see it, and (b) does
the UNRESOLVED section elicit the id-addressed form AT ALL. The recorded
baseline for (b) is **0 of 3473 archived round replies, Wilson [0.0000%,
0.1105%]**, and the reason is documented in the runner itself: the panel was
TOLD not to supply one. UNCONFIRMED findings -- the only status
`unverified_critical_count` treats as an A4 blocker -- used to be rendered under
a header reading "SETTLED ... confirmed, closed, or merged. Do not CHALLENGE or
re-describe them", measured at 175 of 175 attributed blockers, 100.0000%,
Wilson [97.8520%, 100.0000%]. `build_summary` was changed to render them under
UNRESOLVED and ask for the form explicitly.

THE PREDICATE IS THE LIVE ONE, NOT AN INVENTED REGEX. The pattern is lifted
from `record_in_round_falsifier_reattachments` in `bench/reference_runner_v3.py`
by reading that function's own source, so a drift between this script and the
runner is impossible to introduce silently:

    FALSIFIER:\\s*(C\\d{4})\\s*```(?:python)?\\s*\\n(.*?)```

ONE-SIDEDNESS, stated because it decides how a zero may be read. A zero here is
NOT evidence that the elicitation does not work. The form can only be supplied
if there was an UNCONFIRMED critical rendered under UNRESOLVED for a seat to
address. A run that produced no A4 blockers gave the mechanism nothing to fire
on, and that is a property of the run, not of the mechanism. So this script
reports the OPPORTUNITY COUNT alongside the hit count, and refuses to turn a
zero into a verdict when the opportunity count is also zero.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
RUN1 = REPO / ("bench/logs/free_run1_directive_whole_20261015T061123Z"
               "_20261015T061124Z")
RUNNER = REPO / "bench/reference_runner_v3.py"

BASELINE_HITS, BASELINE_N = 0, 3473


def live_pattern() -> str:
    """Read the regex out of the runner's own source. Fail loudly if absent."""
    src = RUNNER.read_text(encoding="utf-8")
    m = re.search(r'r"(FALSIFIER:\\s\*\(C\\d\{4\}\).*?)"', src)
    if not m:
        raise SystemExit("the runner's FALSIFIER pattern could not be located; "
                         "refusing to substitute an invented one")
    return m.group(1)


def main() -> int:
    from statsmodels.stats.proportion import proportion_confint
    from scipy import stats as sstats

    pat_src = live_pattern()
    # `pat_src` is already the REGEX SOURCE as it appears in the runner, so its
    # backslashes are literal characters. Passing it through unicode_escape was
    # wrong: it tried to resolve \s and \d as PYTHON escapes and warned.
    pat = re.compile(pat_src, re.S)
    print(f"  pattern lifted from the runner: {pat_src}")

    if not RUN1.exists():
        print(f"run 1 directory absent: {RUN1}", file=sys.stderr)
        return 2

    # --- seat replies, per round --------------------------------------------
    replies = sorted(RUN1.glob("r*_*.json"))
    hits, n_replies = 0, 0
    per_round: dict[str, dict] = {}
    hit_detail = []
    for p in replies:
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        body = ""
        for k in ("response", "raw", "text", "reply", "content"):
            v = d.get(k)
            if isinstance(v, str) and v:
                body = v
                break
        if not body:
            body = json.dumps(d)
        n_replies += 1
        rnd = p.name.split("_", 1)[0]
        per_round.setdefault(rnd, {"replies": 0, "hits": 0})
        per_round[rnd]["replies"] += 1
        found = pat.findall(body)
        if found:
            hits += 1
            per_round[rnd]["hits"] += 1
            hit_detail.append({"file": p.name, "ids": [f[0] for f in found]})

    print()
    print("=" * 74)
    print("1. DID ANY SEAT REPLY CARRY THE ID-ADDRESSED FORM?")
    print("=" * 74)
    print(f"  seat reply files read : {n_replies}")
    for rnd in sorted(per_round):
        r = per_round[rnd]
        print(f"    {rnd:<5} replies={r['replies']:<3} with the form={r['hits']}")
    print(f"  replies carrying the form: {hits} of {n_replies}")
    if hit_detail:
        for h in hit_detail:
            print(f"    {h['file']}: {h['ids']}")

    # --- the OPPORTUNITY count, which decides whether a zero means anything --
    print()
    print("=" * 74)
    print("2. WAS THERE ANY OPPORTUNITY? (unconfirmed criticals to address)")
    print("=" * 74)
    opp = 0
    opp_detail = []
    rep = sorted(RUN1.glob("*_report.json"))
    state = RUN1 / "runner_state.json"
    for src in rep + ([state] if state.exists() else []):
        try:
            d = json.loads(src.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        txt = json.dumps(d)
        for key in ("unverified_critical_count", "unresolved_critical",
                    "irreducible_queue", "unverified_critical"):
            for m in re.finditer(rf'"{key}":\s*(\d+)', txt):
                v = int(m.group(1))
                opp_detail.append((src.name, key, v))
                opp = max(opp, v)
    for s, k, v in opp_detail[:14]:
        print(f"    {s:<52} {k} = {v}")
    print(f"  maximum unconfirmed-critical count seen: {opp}")

    # --- the two proportions ------------------------------------------------
    print()
    print("=" * 74)
    print("3. RUN 1 AGAINST THE ARCHIVED BASELINE")
    print("=" * 74)
    b_lo, b_hi = proportion_confint(BASELINE_HITS, BASELINE_N, method="wilson")
    r_lo, r_hi = proportion_confint(hits, max(n_replies, 1), method="wilson")
    b_lob, b_hib = proportion_confint(BASELINE_HITS, BASELINE_N, method="beta")
    r_lob, r_hib = proportion_confint(hits, max(n_replies, 1), method="beta")
    print(f"  archive  : {BASELINE_HITS} of {BASELINE_N}  "
          f"Wilson [{b_lo*100:.4f}%, {b_hi*100:.4f}%]  "
          f"CP [{b_lob*100:.4f}%, {b_hib*100:.4f}%]")
    print(f"  run 1    : {hits} of {n_replies}  "
          f"Wilson [{r_lo*100:.4f}%, {r_hi*100:.4f}%]  "
          f"CP [{r_lob*100:.4f}%, {r_hib*100:.4f}%]")
    if n_replies:
        ft = sstats.fisher_exact([[hits, n_replies - hits],
                                  [BASELINE_HITS, BASELINE_N - BASELINE_HITS]])
        print(f"  Fisher exact p (run 1 vs archive): {ft[1]:.4f}")
        chi = None
        try:
            chi = sstats.chi2_contingency(
                [[hits, n_replies - hits],
                 [BASELINE_HITS, BASELINE_N - BASELINE_HITS]])[1]
        except ValueError:
            pass
        print(f"  chi-square cross-check p         : "
              f"{'n/a (a zero margin makes it undefined)' if chi is None else f'{chi:.4f}'}")

    print()
    print("=" * 74)
    print("VERDICT")
    print("=" * 74)
    if opp == 0:
        print("  NO READING AVAILABLE. The maximum unconfirmed-critical count in")
        print("  run 1 is 0, so no finding was ever rendered under UNRESOLVED for a")
        print("  seat to address. A zero hit count is therefore a property of THIS")
        print("  RUN -- it converged with 0 unresolved criticals -- and says nothing")
        print("  about whether the elicitation works. The measurement needs a run")
        print("  that actually carries an A4 blocker into a round.")
        verdict = "NO_OPPORTUNITY"
    elif hits > 0:
        print(f"  ELICITED. {hits} of {n_replies} replies carried the form against a")
        print(f"  baseline of 0 of {BASELINE_N}. The mechanism fires.")
        verdict = "ELICITED"
    else:
        print(f"  NOT ELICITED DESPITE OPPORTUNITY. {opp} unconfirmed critical(s)")
        print(f"  were available and 0 of {n_replies} replies carried the form.")
        print("  This is a real negative and belongs in the record as one.")
        verdict = "NOT_ELICITED_DESPITE_OPPORTUNITY"
    print(f"  verdict: {verdict}")

    out = {
        "pattern_from_runner": pat_src,
        "seat_replies_read": n_replies,
        "replies_with_the_form": hits,
        "per_round": per_round,
        "hit_detail": hit_detail,
        "max_unconfirmed_critical_seen": opp,
        "opportunity_detail": [list(x) for x in opp_detail],
        "archive_baseline": [BASELINE_HITS, BASELINE_N],
        "archive_wilson": [b_lo, b_hi],
        "run1_wilson": [r_lo, r_hi],
        "verdict": verdict,
        "one_sidedness": ("a zero is not evidence against the mechanism unless the "
                          "opportunity count is above zero"),
    }
    dest = REPO / "experimental_notes/evidence/unresolved_elicitation_run1_2026-10-15.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(f"  evidence -> {dest.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
