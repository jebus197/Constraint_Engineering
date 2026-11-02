#!/usr/bin/env python3
"""Which seats would the demotion rule have demoted? A SHADOW report: nothing demoted.

WHY THIS WAS BLOCKED AND WHAT UNBLOCKED IT. Entry B56 records the demotion rule's
operating point at 1 wrong demotion in 50, on his ruling of 2026-10-30, and that
the rule is wired to nothing. The half that did not wait on him was a shadow
report naming which seats the rule WOULD have demoted. I declined to start it
unattended for 1 stated reason: it needs a definition of *a seat being right in a
round*, and a proxy chosen without measuring its alternatives is this project's
single most recorded error class.

HE THEN SUPPLIED THE PRIMARY CANDIDATE HIMSELF, in annotation 13 of
`Closing_Report_2026-11-01.txt`, verbatim: *"So if this work still needs done,
then you should do it. But I am not clear what you are asking of me? Being
'right' would be I presume when an issue is marked by the harness registry as
closed?"*

★ SO HIS PROXY IS THE PRIMARY AND IT IS MEASURED AGAINST 3 ALTERNATIVES RATHER
THAN SIMPLY ADOPTED. Adopting a proxy because the founder suggested it would be
the same error as adopting one because it was convenient -- the rule is that
alternatives get measured, not that the author gets to pick.

★ AND THE COMPARISON IS ON ORDERING, NOT ON RATE, WHICH IS THE POINT. A demotion
rule acts on a seat's RANK against its peers, so what matters is whether the 4
definitions order the seats the SAME way. If they agree, the choice of proxy is
not load-bearing and his can be adopted without further argument. If they
disagree, the choice decides who gets demoted and that is his to settle, not
mine. Kendall's tau is computed on scipy and again from first principles, per
the 2-tool rule.

NOTHING IS DEMOTED. There is no live demotion mechanism to connect to -- B56
records that finding -- so this reports and does not act.
"""
from __future__ import annotations
import collections, itertools, json, math, pathlib, sys

import sys as _sys, pathlib as _pl  # noqa: E402
for _cand in (_pl.Path(__file__).resolve().parent, *_pl.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        if str(_cand) not in _sys.path:
            _sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"

#: His operating point, read from its owner rather than retyped.
def _chosen_target() -> float:
    p = REPO / "scripts" / "can_we_do_better_than_one_in_twenty_2026-10-30.py"
    for ln in p.read_text().splitlines():
        if ln.strip().startswith("CHOSEN_TARGET"):
            return float(ln.split("=")[1].split("#")[0].strip())
    raise SystemExit("CHOSEN_TARGET is not in its owning script; refusing to guess")


#: The 4 candidate definitions of "the seat was right about this finding".
DEFS = {
    "his_closed": lambda e: str(e.get("status", "")).upper() == "CLOSED",
    "resolved_favourably": lambda e: str(e.get("status", "")).upper()
        in ("CLOSED", "CONFIRMED", "CORROBORATED"),
    "tool_confirmed": lambda e: str(e.get("falsifier_verdict", "")).upper()
        == "CONFIRMED",
    "not_withdrawn": lambda e: str(e.get("status", "")).upper()
        not in ("REFUTED", "MERGED", "DUPLICATE"),
}


def wilson(k: int, n: int):
    if n == 0:
        return (float("nan"),) * 3
    p = k / n; z = 1.959963984540054
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def kendall_tau_manual(a: list[float], b: list[float]) -> float:
    """Tau-b from first principles, so scipy is corroborated and not trusted."""
    n = len(a)
    conc = disc = ta = tb = 0
    for i, j in itertools.combinations(range(n), 2):
        da, db = a[i] - a[j], b[i] - b[j]
        if da == 0 and db == 0:
            ta += 1; tb += 1
        elif da == 0:
            ta += 1
        elif db == 0:
            tb += 1
        elif da * db > 0:
            conc += 1
        else:
            disc += 1
    n0 = n * (n - 1) / 2
    den = math.sqrt((n0 - ta) * (n0 - tb))
    return (conc - disc) / den if den else float("nan")


def main() -> int:
    answer_help(__doc__, __file__)
    target = _chosen_target()
    per_seat = {k: collections.Counter() for k in DEFS}
    totals = collections.Counter()
    for f in sorted(LOGS.glob("*/runner_state.json")):
        try:
            j = json.loads(f.read_text(errors="ignore"))
        except Exception:                                    # noqa: BLE001
            continue
        ents = (j.get("registry") or {}).get("entries") or {}
        ents = list(ents.values()) if isinstance(ents, dict) else list(ents)
        for e in ents:
            seat = str(e.get("source_model") or "").strip()
            if not seat:
                continue
            totals[seat] += 1
            for name, fn in DEFS.items():
                if fn(e):
                    per_seat[name][seat] += 1

    print("=" * 78)
    print("SHADOW DEMOTION REPORT — NOTHING IS DEMOTED")
    print("=" * 78)
    print(f"  his operating point, read from its owning script: {target}")
    print(f"  seats with findings: {len(totals)}   findings: {sum(totals.values())}")

    seats = [s for s, n in totals.most_common() if n >= 20]
    print(f"  seats with at least 20 findings, which is the comparable set: "
          f"{len(seats)}")
    if len(seats) < 3:
        print("  FEWER THAN 3 COMPARABLE SEATS. An ordering comparison needs at")
        print("  least 3 to be meaningful, so NOTHING IS CONCLUDED.")
        return 1

    print(f"\n  RATE UNDER EACH DEFINITION, per seat")
    hdr = f"  {'seat':22s} {'n':>5s}"
    for name in DEFS:
        hdr += f" {name[:17]:>18s}"
    print(hdr)
    rates: dict[str, list[float]] = {k: [] for k in DEFS}
    for s in seats:
        row = f"  {s[:22]:22s} {totals[s]:5d}"
        for name in DEFS:
            p, lo, hi = wilson(per_seat[name][s], totals[s])
            rates[name].append(p)
            row += f" {p:18.6f}"
        print(row)

    print(f"\n  DOES THE CHOICE OF DEFINITION CHANGE THE ORDERING?")
    from scipy import stats as _s
    worst = 1.0
    for a, b in itertools.combinations(DEFS, 2):
        t_sp = _s.kendalltau(rates[a], rates[b]).statistic
        t_man = kendall_tau_manual(rates[a], rates[b])
        agree = abs(t_sp - t_man) < 1e-9
        worst = min(worst, t_sp if t_sp == t_sp else 1.0)
        print(f"    {a[:20]:22s} vs {b[:20]:22s} tau = {t_sp:+.6f}"
              f"   (manual {t_man:+.6f}, agree {agree})")

    print(f"\n  ORDERING UNDER EACH DEFINITION, worst first (the demotion end)")
    for name in DEFS:
        order = [s for _, s in sorted(zip(rates[name], seats))]
        print(f"    {name:22s} {order}")

    print("\n" + "=" * 78)
    if worst >= 0.9:
        print(f"THE 4 DEFINITIONS AGREE ON ORDERING (worst pairwise tau "
              f"{worst:+.6f}).")
        print("So the choice of proxy is NOT load-bearing at this sample, and his")
        print("-- a finding marked CLOSED by the registry -- can be adopted on the")
        print("evidence rather than on his authority. The alternatives were")
        print("measured, which is what the rule asked for.")
    else:
        print(f"THE DEFINITIONS DISAGREE ON ORDERING (worst pairwise tau "
              f"{worst:+.6f}).")
        print("So the choice of proxy DECIDES WHO WOULD BE DEMOTED. That is his to")
        print("settle and not mine, and adopting his suggestion without saying so")
        print("would hide a decision inside a measurement.")
    # ─────────────────────────────────────────────────────────────────────
    # ★ THE CONFOUND, WHICH IS LARGER THAN THE QUESTION THIS SCRIPT WAS WRITTEN
    # TO ANSWER AND WAS VISIBLE IN ITS OWN FIRST OUTPUT.
    #
    # Every SIMULATED seat scores higher than every REAL seat on all 4
    # definitions. So a demotion rule run across the mixed set would demote
    # every paid seat and keep every stand-in -- not because the paid seats are
    # worse, but because the 2 populations are not comparable. The "right rate"
    # is dominated by RUN TYPE, and any ordering taken across both is measuring
    # that rather than capability.
    print("\n" + "=" * 78)
    print("★ THE CONFOUND: REAL SEATS AGAINST SIMULATED STAND-INS")
    print("=" * 78)
    real = [s for s in seats if not s.endswith("-SIM")]
    sim = [s for s in seats if s.endswith("-SIM")]
    idx = {s: i for i, s in enumerate(seats)}
    for name in DEFS:
        rr = [rates[name][idx[s]] for s in real]
        rs = [rates[name][idx[s]] for s in sim]
        if not rr or not rs:
            continue
        from scipy import stats as _st
        u = _st.mannwhitneyu(rs, rr, alternative="greater")
        print(f"  {name:22s} real max {max(rr):.6f} | sim min {min(rs):.6f}"
              f"   separated: {min(rs) > max(rr)}"
              f"   Mann-Whitney p = {u.pvalue:.6e}")
    print(f"\n  real seats: {real}")
    print(f"  simulated  : {sim}")
    print("\n  SO THE ORDERING ABOVE MUST NOT BE READ AS A CAPABILITY RANKING.")
    print("  A demotion rule applied to it would demote the paid panel entire.")

    print("\n  AND WITHIN EACH POPULATION, DOES THE PROXY CHOICE STILL MATTER?")
    for label, grp in (("real", real), ("simulated", sim)):
        if len(grp) < 3:
            print(f"    {label}: only {len(grp)} seat(s); an ordering comparison")
            print(f"      needs 3, so NOTHING IS CONCLUDED for this group.")
            continue
        w = 1.0
        for a, b in itertools.combinations(DEFS, 2):
            ra = [rates[a][idx[s]] for s in grp]
            rb = [rates[b][idx[s]] for s in grp]
            t = kendall_tau_manual(ra, rb)
            if t == t:
                w = min(w, t)
        print(f"    {label:10s} {len(grp)} seats, worst pairwise tau {w:+.6f}"
              f"   -> proxy choice {'MATTERS' if w < 0.9 else 'does not matter'}")

    print("\nAND NOTHING IS DEMOTED EITHER WAY: B56 records that no live demotion")
    print("mechanism exists to connect this to. This reports; it does not act.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
