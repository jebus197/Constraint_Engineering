# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'falsifier_supply_and_integrity_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 81e8763e1519f0d89c917d4ec077fbb13251dfe1aff1af58a2eb4c7d722f1f0f
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Is the founder's intelligence-first contract honoured? (Q1, Q2, and Cause 2)

HIS DESIGN INTENT, verbatim: "a hand-rolled falsifier could be acceptable as a
form of 'scratchpad' reasoning method for the models, so long as that reasoning
was either invariably confirmed, or refuted with tools, and providing our
machinery instructs the models to keep trying like this until their solutions
are subsequently confirmed by tools."

That makes hand-rolling a PROCESS question, not a supply question: the 86.3727%
hand-rolled rate measured by `falsifier_supply_decomposition_2026-10-02.py` is
not itself a defect. The defect would be a critical that reached an ACCEPTED
terminal status on a model's say-so with no tool ever adjudicating it. The
runner already records the distinction, per entry, in `status_adjudicator`
("tool" / "model" / "panel") beside `status_mechanism`, so the contract is
DECIDABLE from the archive rather than inferable.

THREE MEASUREMENTS, one population:

  Q1  Of criticals ADJUDICATED BY MODEL REASONING, what share were
      subsequently adjudicated by a tool? And -- the sharper form, because
      the project forbids confirmation by model vote -- how many reached an
      accepted terminal status with NO tool verdict anywhere on the entry?

  Q2  The same split restricted to PROSE runs, where the briefing itself says
      ruff/mypy/bandit/pytest "have no purchase". If the tool-adjudication rate
      collapses there, the "keep trying until tool-confirmed" loop is not
      reachable on the stratum that starves most.

  C2  The zero-plant control stratum under BOTH definitions of "no falsifier",
      on identical rows. The adversarial pass claimed 19 of 46 with the pre-fix
      body-only definition; `repro_supply_causes` measures 0 of 46 with the
      verdict-first definition. Printing both on the same rows is what decides
      whether the control stratum was a real inflation or an artefact of the
      conflation `classify()` corrected the same day.

Populations are declared, not assumed, and both candidate cuts are printed
side by side (post-exp42 vs post-2026-06-06) because the brief's own two
figures -- 0 of 558 and 14 of 624 -- disagree and the disagreement is a
population choice, not a measurement error.

Every proportion carries a Wilson interval from statsmodels against an
independent mpmath closed form; every 2x2 carries a Fisher exact from scipy
against an independent mpmath hypergeometric sum. Disagreement is printed.
No Wolfram result is used here.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from collections import Counter

for _cand in (pathlib.Path(__file__).resolve().parent,
              *pathlib.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
CRIT = 0.7

# A verdict only a TOOL can write. `reverify_falsifier` is the only producer of
# these strings in the repository; a model proposes a finding, never a verdict.
TOOL_VERDICTS = {"CONFIRMED", "REFUTED", "ERROR", "TIMEOUT",
                 "INTEGRITY_VIOLATION", "REFUSED"}
# Terminal statuses that mean the project ACCEPTED the finding as real.
ACCEPTED = {"CLOSED", "CONFIRMED", "CORROBORATED"}
# Dates, for the second candidate population cut.
DATE_RE = re.compile(r"(20\d{6})T")


def wilson(k: int, n: int):
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    if not n:
        return 0.0, 0.0, 0.0, 0.0, True
    lo, hi = proportion_confint(k, n, method="wilson")
    mp.mp.dps = 40
    z = mp.mpf("1.959963984540054235524594430520551527955")
    p, d = mp.mpf(k) / n, 1 + z ** 2 / n
    c = p + z ** 2 / (2 * n)
    h = z * mp.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2))
    mlo, mhi = float((c - h) / d), float((c + h) / d)
    return float(lo), float(hi), mlo, mhi, abs(lo - mlo) < 1e-9 and abs(hi - mhi) < 1e-9


def pct(label: str, k: int, n: int) -> None:
    lo, hi, mlo, mhi, agree = wilson(k, n)
    if not n:
        print(f"    {label:52s} {k:4d} / {n:4d}  (empty stratum: no interval)")
        return
    print(f"    {label:52s} {k:4d} / {n:4d} = {100*k/n:8.4f}%  "
          f"Wilson [{100*lo:7.4f}%, {100*hi:7.4f}%]  agree={agree}")


def fisher(a, b, c, d):
    from scipy.stats import fisher_exact
    import mpmath as mp
    odds, p = fisher_exact([[a, b], [c, d]])
    mp.mp.dps = 50
    n = a + b + c + d
    if not n:
        return odds, p, p
    r1, c1 = a + b, a + c

    def pr(x):
        return (mp.binomial(c1, x) * mp.binomial(n - c1, r1 - x)) / mp.binomial(n, r1)
    obs, tot = pr(a), mp.mpf(0)
    for x in range(max(0, r1 - (n - c1)), min(r1, c1) + 1):
        q = pr(x)
        if q <= obs * (1 + mp.mpf("1e-30")):
            tot += q
    return odds, p, float(tot)


def entries():
    """Deduplicated criticals, keyed (run, cid). Identical rule to
    `repro_supply_causes_2026-10-02.py` so the two are comparable row for row."""
    rows: dict[tuple[str, str], tuple] = {}
    for name in ("runner_state.json", "*_report.json"):
        for f in sorted((ROOT / "bench" / "logs").glob(f"*/{name}")):
            try:
                data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            except Exception:  # noqa: BLE001
                continue
            cfg = data.get("config") or {}
            tgt = str(cfg.get("target_file") or data.get("target_file") or "")
            for cid, e in ((data.get("registry") or {}).get("entries") or {}).items():
                if not isinstance(e, dict) or (e.get("severity") or 0) < CRIT:
                    continue
                key = (f.parent.name, cid)
                body = ((e.get("falsifier_code") or "").strip()
                        or (e.get("last_falsifier_code") or "").strip())
                prev = rows.get(key)
                if prev is None or (not prev[2] and body):
                    rows[key] = (f.parent.name, tgt, body, e)
    return rows


def expno(r: str):
    m = re.match(r"exp(\d+)", r)
    return int(m.group(1)) if m else None


def rundate(r: str):
    m = DATE_RE.search(r)
    return m.group(1) if m else None


def tool_verdict(e) -> str:
    """The strongest TOOL-written verdict anywhere on the entry.

    Reads the ladder-side residual too. `_apply_routing` writes
    `falsifier_verdict` back only on `result.resolved`, so a ladder run that
    did not confirm leaves its real verdict only in `routing_history[-1]` and
    `routing_verdict_unreconciled` -- which is exactly the feedback-channel
    defect listed as Cause 3. An entry adjudicated there HAS been toolled, and
    counting it as untoolled would reproduce the defect inside the measurement.
    """
    for v in ((e.get("falsifier_verdict") or ""),
              (e.get("routing_verdict_unreconciled") or ""),
              *[(h.get("verdict") or "") for h in reversed(e.get("routing_history") or [])
                if isinstance(h, dict)]):
        s = v.strip().upper()
        if s in TOOL_VERDICTS:
            return s
    return ""


def adjudicator(e) -> str:
    a = (e.get("status_adjudicator") or "").strip().lower()
    return a or "unrecorded"


def is_prose(run: str, tgt: str) -> bool:
    return tgt.lower().endswith((".md", ".txt", ".rst")) or "prose" in run.lower()


def main() -> int:
    rows = entries()

    print("POPULATION -- BOTH CANDIDATE CUTS, because the brief's own two "
          "figures disagree")
    post42 = {k: v for k, v in rows.items()
              if expno(k[0]) is None or expno(k[0]) >= 42}
    postjun = {k: v for k, v in rows.items()
               if (rundate(k[0]) or "99999999") > "20260606"}
    print(f"  all deduplicated criticals (severity >= {CRIT})     : {len(rows)}")
    print(f"  cut A: post-exp42 (feature cut, by experiment id)   : {len(post42)}")
    print(f"  cut B: post-2026-06-06 (date cut, undated dropped)  : {len(postjun)}")
    print(f"  rows in A but not B                                 : "
          f"{len(set(post42) - set(postjun))}")
    print(f"  rows in B but not A                                 : "
          f"{len(set(postjun) - set(post42))}")
    print("  THE DATE CUT SILENTLY DROPS EVERY UNDATED RUN DIRECTORY, which is")
    print("  where the panel_* and prose_* runs live. Cut A is the right")
    print("  population for a question about the FEATURE; cut B answers a")
    print("  question about a calendar and loses the newest runs to do it.")

    for cut_name, pop in (("A  post-exp42", post42), ("B  post-2026-06-06", postjun)):
        neither = [k for k, (r, t, b, e) in pop.items()
                   if not b and not tool_verdict(e)]
        print(f"\n  cut {cut_name}: criticals with NEITHER a falsifier nor a verdict")
        pct("neither body nor verdict", len(neither), len(pop))

    pop = post42
    print("\nQ1  THE INTELLIGENCE-FIRST CONTRACT")
    print("  recorded adjudicator over the whole population:")
    for a, n in Counter(adjudicator(e) for (_, _, _, e) in pop.values()).most_common():
        pct(f"status_adjudicator = {a}", n, len(pop))

    reasoned = {k: v for k, v in pop.items() if adjudicator(v[3]) != "tool"}
    toolled = [k for k, v in reasoned.items() if tool_verdict(v[3])]
    print("\n  OF THOSE ADJUDICATED BY MODEL REASONING, subsequently toolled:")
    pct("model-reasoned criticals, in population", len(reasoned), len(pop))
    pct("  ... of which a TOOL later returned a verdict", len(toolled), len(reasoned))

    print("\n  THE FORBIDDEN CASE -- accepted on reasoning, never toolled:")
    forbidden = [k for k, v in pop.items()
                 if (v[3].get("status") or "").strip().upper() in ACCEPTED
                 and adjudicator(v[3]) != "tool" and not tool_verdict(v[3])]
    accepted = [k for k, v in pop.items()
                if (v[3].get("status") or "").strip().upper() in ACCEPTED]
    pct("accepted terminal status", len(accepted), len(pop))
    pct("  ... accepted with NO tool verdict and no tool adjudicator",
        len(forbidden), len(accepted))
    if forbidden:
        print("    offenders (run, cid, status, adjudicator, mechanism):")
        for k in sorted(forbidden)[:12]:
            e = pop[k][3]
            print(f"      {k[0][:44]:46s} {k[1]:7s} "
                  f"{e.get('status'):12s} {adjudicator(e):10s} "
                  f"{(e.get('status_mechanism') or '-')}")
        if len(forbidden) > 12:
            print(f"      ... and {len(forbidden)-12} more")

    print("\nQ2  THE PROSE STRATUM, where the general instruments have no purchase")
    pr = {k: v for k, v in pop.items() if is_prose(k[0], v[1])}
    co = {k: v for k, v in pop.items() if not is_prose(k[0], v[1])}
    print(f"  prose-run criticals {len(pr)}   code-run criticals {len(co)}")
    for lbl, s in (("prose", pr), ("code ", co)):
        pct(f"{lbl}: a TOOL returned a verdict", 
            sum(1 for v in s.values() if tool_verdict(v[3])), len(s))
        pct(f"{lbl}: accepted with NO tool verdict",
            sum(1 for v in s.values()
                if (v[3].get("status") or "").upper() in ACCEPTED
                and not tool_verdict(v[3])), len(s))
    a = sum(1 for v in pr.values() if not tool_verdict(v[3]))
    b = len(pr) - a
    c = sum(1 for v in co.values() if not tool_verdict(v[3]))
    d = len(co) - c
    if (a + b) and (c + d):
        o, p, pm = fisher(a, b, c, d)
        print(f"  prose vs code, NO tool verdict: Fisher OR = {o:.4f}  "
              f"scipy p = {p:.6e}  mpmath p = {pm:.6e}  agree={abs(p-pm) < 1e-9}")

    print("\nC2  THE CONTROL STRATUM UNDER BOTH DEFINITIONS, on identical rows")
    runs_ctrl = sorted({k[0] for k in pop if "control" in k[0].lower()
                        or "zero" in k[0].lower()})
    print(f"  run directories counted as controls ({len(runs_ctrl)}): {runs_ctrl}")
    for defn, f in (("PRE-FIX  body only  (the claim's definition)",
                     lambda b, e: not b),
                    ("POST-FIX verdict first (classify() as corrected)",
                     lambda b, e: not b and not tool_verdict(e))):
        a = b_ = c = d = 0
        for k, (r, t, body, e) in pop.items():
            ctrl = ("control" in r.lower() or "zero" in r.lower())
            nb = f(body, e)
            if ctrl:
                a, b_ = a + nb, b_ + (not nb)
            else:
                c, d = c + nb, d + (not nb)
        print(f"  {defn}")
        print(f"    control  no-falsifier {a:4d}  other {b_:4d}")
        print(f"    live     no-falsifier {c:4d}  other {d:4d}")
        if (a + b_) and (c + d):
            o, p, pm = fisher(a, b_, c, d)
            print(f"    Fisher OR = {o:.4f}  scipy p = {p:.6e}  "
                  f"mpmath p = {pm:.6e}  agree={abs(p-pm) < 1e-9}")
    return 0


if __name__ == "__main__":
    answer_help(__doc__, __file__)
    raise SystemExit(main())
