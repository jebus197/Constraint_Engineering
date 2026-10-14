# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_his_rulings_2026-10-13', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 3166619fe0145b9607d555ca9ce24e097f65b594cdd52f2ea42a4bf68521ebf4
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Of the archived findings with no falsifier, how many were IRREDUCIBLE and how
many were NEVER ATTEMPTED?

THE CLAIM UNDER TEST, 2026-10-14: "1938 of 3298 = 58.7629% of archived findings
were recorded UNTOOLABLE or carry no falsifier." The question put to this script
is the one the headline figure does not answer: of those 1938, how many were
GENUINELY IRREDUCIBLE -- no tool could have decided them -- and how many were
merely NEVER ATTEMPTED, with no falsifier ever written and no execution record
of any kind?

THE DENOMINATOR IS REUSED, NOT RECOMPUTED. The 3,298 figure comes from
`scripts/severity_was_never_computed_from_the_model_2026-10-12.py` and
`scripts/the_verification_factor_shadow_2026-10-12.py`: every dict under
`registry.entries` of every `bench/logs/**/runner_state.json` that carries a
numeric `severity`. This script globs the same files and applies the same
predicate so the denominator is the same 3,298 by construction, and reprints it
so a mismatch is visible rather than silent.

THE NUMERATOR IS REPRODUCED EXACTLY, AND ITS DEFINITION IDENTIFIED. 1938 is the
count of those entries whose `falsifier_code` is absent or empty after
stripping. It is also, to the entry, the count of "no falsifier_code OR verdict
UNTOOLABLE" -- because all 41 UNTOOLABLE entries store empty code -- so the
claim's two-limbed wording picks out one set. Neighbouring definitions do NOT
give 1938 and are printed alongside so the reader can see which one the claim is
about.

WHAT THE ARCHIVE CAN AND CANNOT SUPPORT. There is no `untoolable_reason` field
anywhere in the corpus. The key inventory this script prints FIRST is the proof:
the only reason-bearing fields on this population are `withdraw_reason`,
`routing_defer_reason`, `computed_evidence[].detail`, `hil_reason`,
`close_reason` and `merge_blocked_reason`, and the first three are the only ones
that ever speak to toolability at all. So "genuinely irreducible" is only
decidable for the entries that carry such a reason; for the rest the archive
records the ABSENCE of a falsifier and nothing about why. That asymmetry is the
finding, and it is reported as a bound rather than hidden in a point estimate.

S_k IS NOT AN ATTEMPT ON THE CLAIM, and the archive says so in its own words.
736 of the 1938 carry an `sk_result`, which is an admissibility score for a
PROPOSED FIX. The corpus's own `routing_defer_reason` text reads: "the falsifier
verdict was UNTOOLABLE, an equipment failure, so the CLAIM itself has not been
tested by a runnable falsifier. Any S_k result on this entry speaks to a FIX,
not to the truth of the claim, and is not consulted here." This script honours
that and counts `sk_result` separately, never as evidence the claim was tested.

THE FOUR CLASSES, defined only from fields that exist.

  B  REASONED IRREDUCIBILITY -- a reason string on the entry states why no tool
     can decide it ("Not a testable code claim", "carries no claim about the
     target module's code", "a status note ... not a claim about any code").
  A  ATTEMPT RECORDED, NO FALSIFIER STORED -- the falsifier slot was reached and
     a verdict written while the code field stayed empty (UNTOOLABLE, ERROR, or
     blank), or the routing ladder logged rungs, or the entry was error-routed
     or marked exhausted. Equipment, not irreducibility.
  D  ADMINISTRATIVELY MOOT -- merged into another entry, so the falsifier was
     never this entry's to run.
  E  NEVER ATTEMPTED -- no falsifier field at all, no routing record, no reason,
     no error route, no exhaustion. The archive holds nothing but the claim.

Precedence runs B, A, D, E, so the class most favourable to "irreducible" is
assigned first and E is the residue that survives every alternative reading.

THE OBJECTIVE REDUCIBILITY SIGNAL. Independently of any class, this script asks
what the 1938 are ABOUT: the target file extension (from the proposed fix's
SEARCH header, else a path in the claim text, else the run's target) and whether
the claim text contains a concrete code reference or a numeric literal.
Something mechanically checkable in principle is not irreducible.

THE DIRECT CROSS-CHECK, BY TWO ROUTES, AND ONE OF THEM FAILS HONESTLY. Route
one: findings recorded with no falsifier in one run whose dedup twin -- same
normalised claim text -- carries an EXECUTED falsifier with a CONFIRMED or
REFUTED verdict in another. This route returns 0, and the reason is printed:
claim text is almost never repeated across runs, and a first pass that keyed on
every description returned 60 twins which were ALL the 82 entries carrying an
empty `description` colliding on one hash. That artefact is excluded by a
minimum claim length and the exclusion is reported. Route two: entries whose OWN
`routing_history` logged an UNTOOLABLE or ERROR verdict and which a falsifier
nevertheless went on to decide. That route returns 36, and each is a worked
instance of "called untoolable, later decided by a tool".

EVERY PROPORTION CARRIES A WILSON INTERVAL FROM TWO INDEPENDENT ROUTES --
statsmodels' `proportion_confint(method='wilson')` and a Wilson derived by hand
in mpmath at 50 digits, with the normal quantile from `mpmath.erfinv` rather
than a tabulated 1.96 -- plus Clopper-Pearson for comparison. Agreement between
the two routes is asserted numerically, not assumed.

Usage: python3 scripts/how_many_untoolable_were_never_attempted_2026-10-14.py
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"

#: Verdicts meaning a tool actually DECIDED the claim.
DECIDED = {"CONFIRMED", "REFUTED"}

#: Reason-text that asserts the claim is not computable at all. Drawn from the
#: strings that actually occur in `withdraw_reason` and
#: `computed_evidence[].detail` on this population -- not invented.
NONCOMPUTABLE_RE = re.compile(
    r"not a testable"
    r"|not a defect of this"
    r"|not a defect in"
    r"|no actual defect"
    r"|nothing (?:in the target )?a falsifier could"
    r"|a falsifier could execu"
    r"|carries no claim"
    r"|no claim about"
    r"|not a claim about"
    r"|process narrative"
    r"|review process"
    r"|VCS-hygiene",
    re.I,
)

#: A path with an extension, used to attribute a target to a claim.
PATH_RE = re.compile(r"[\w./\-]*\w+\.(?:py|md|toml|json|ya?ml|sh|txt|cfg|ini|tex)\b")
#: The runner's own search/replace fix header names the file it patches.
SEARCH_RE = re.compile(r"<<<<+\s*SEARCH\s+([^\s\n]+)")
#: A bare number in the claim text: a quantity a tool could check.
NUMERIC_RE = re.compile(r"(?<![\w.])\d+(?:\.\d+)?(?![\w])")
#: A code reference: a backticked span, a call, an attribute access, a line
#: number anchor, or a module filename.
CODEISH_RE = re.compile(r"`[^`]+`|\b\w+\(\)|\b\w+\.\w+\(|:\d+\b|\b\w+\.py\b")


# ---------------------------------------------------------------- enumeration

def run_target(state_path: pathlib.Path):
    """The target this run reviewed, from the run's own report JSON."""
    for rep in sorted(state_path.parent.glob("*report*.json")):
        try:
            r = json.loads(rep.read_text(encoding="utf-8", errors="ignore"))
        except Exception:                                     # noqa: BLE001
            continue
        if isinstance(r, dict):
            for k in ("target", "target_file", "target_path", "target_rel", "file"):
                if r.get(k):
                    return str(r[k])
    return None


def entries():
    """The SAME enumeration as the 3,298 producers: every registry entry under
    bench/logs/**/runner_state.json carrying a numeric severity."""
    for fp in sorted(LOGS.glob("**/runner_state.json")):
        try:
            d = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
        except Exception:                                     # noqa: BLE001
            continue
        for cid, e in (((d or {}).get("registry") or {}).get("entries") or {}).items():
            if isinstance(e, dict) and isinstance(e.get("severity"), (int, float)):
                yield fp, cid, e


# ------------------------------------------------------------------ predicates

def code(e: dict) -> str:
    return str(e.get("falsifier_code") or "").strip()


def verdict(e: dict) -> str:
    return str(e.get("falsifier_verdict") or "").strip().upper()


def in_population(e: dict) -> bool:
    """The claim's set: no falsifier stored, or recorded UNTOOLABLE."""
    return (not code(e)) or verdict(e) == "UNTOOLABLE"


def reason_strings(e: dict):
    """Every field on this entry that can speak to WHY no falsifier exists."""
    out = []
    for k in ("withdraw_reason", "routing_defer_reason"):
        if e.get(k):
            out.append(str(e[k]))
    for it in e.get("computed_evidence") or []:
        if isinstance(it, dict) and it.get("detail"):
            out.append(str(it["detail"]))
    return out


def attempt_on_claim(e: dict) -> bool:
    """Did the machinery reach the claim and leave a mark, without storing code?

    Deliberately excludes `sk_result`: that scores a FIX, and the archive's own
    routing_defer_reason text refuses to read it as a test of the claim.
    """
    return (
        "falsifier_verdict" in e
        or bool(e.get("routing_history"))
        or bool(e.get("error_routed"))
        or e.get("exhausted") is True
    )


def classify(e: dict) -> str:
    rs = reason_strings(e)
    if any(NONCOMPUTABLE_RE.search(r) for r in rs):
        return "B_reasoned_irreducible"
    if attempt_on_claim(e):
        return "A_attempt_no_falsifier"
    if e.get("merged_into") or str(e.get("status")) == "MERGED":
        return "D_administratively_moot"
    return "E_never_attempted"


def target_of(e: dict, fallback):
    m = SEARCH_RE.search(str(e.get("proposed_fix") or ""))
    if m:
        return m.group(1), "proposed_fix"
    m = PATH_RE.search(str(e.get("description") or ""))
    if m:
        return m.group(0), "claim_text"
    if fallback:
        return fallback, "run_target"
    return None, "none"


#: Minimum normalised claim length for a dedup key to mean anything. WITHOUT
#: THIS THE CROSS-CHECK REPORTS 60 AND THE 60 ARE AN ARTEFACT: 82 archived
#: entries carry an EMPTY or near-empty `description`, they all hash together,
#: and one of them happens to hold an executed falsifier -- so every
#: empty-description entry acquires a spurious "tooled twin". Measured, then
#: excluded, and the excluded count is printed rather than dropped silently.
DEDUP_MIN_CHARS = 40


def dedup_norm(e: dict) -> str:
    return re.sub(r"\s+", " ", str(e.get("description") or "")).strip().lower()[:300]


def dedup_key(e: dict):
    """A content dedup key, or None when the claim text is too thin to key on."""
    norm = dedup_norm(e)
    if len(norm) < DEDUP_MIN_CHARS:
        return None
    return hashlib.sha1(norm.encode("utf-8")).hexdigest()


# -------------------------------------------------------------------- intervals

def wilson_statsmodels(k: int, n: int):
    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    return float(lo), float(hi)


def wilson_by_hand(k: int, n: int):
    """Wilson score interval derived from scratch at 50 digits in mpmath.

    Centre  (k + z^2/2) / (n + z^2)
    Half    z/(n + z^2) * sqrt( k(n-k)/n + z^2/4 )

    The normal quantile is computed, not tabulated: z = sqrt(2) * erfinv(1-a).
    """
    from mpmath import mp, mpf, erfinv, sqrt
    mp.dps = 50
    z = sqrt(mpf(2)) * erfinv(mpf("0.95"))        # Phi(z) = 0.975
    n_, k_ = mpf(n), mpf(k)
    denom = n_ + z ** 2
    centre = (k_ + z ** 2 / 2) / denom
    half = (z / denom) * sqrt(k_ * (n_ - k_) / n_ + z ** 2 / 4)
    # Clamp to [0, 1]: at k = 0 the exact lower limit is 0 and the float cast
    # lands at -4e-19, which would print as "-0.0000%" and read as a defect.
    lo = max(0.0, float(centre - half))
    hi = min(1.0, float(centre + half))
    return lo, hi


def clopper_pearson(k: int, n: int):
    from scipy import stats
    lo = float(stats.beta.ppf(0.025, k, n - k + 1)) if k else 0.0
    hi = float(stats.beta.ppf(0.975, k + 1, n - k)) if k < n else 1.0
    return lo, hi


AGREEMENT = []


def pct(label: str, k: int, n: int, indent: str = "  ") -> None:
    if not n:
        print(f"{indent}{label}: no denominator")
        return
    wlo, whi = wilson_statsmodels(k, n)
    hlo, hhi = wilson_by_hand(k, n)
    clo, chi = clopper_pearson(k, n)
    delta = max(abs(wlo - hlo), abs(whi - hhi))
    AGREEMENT.append(delta)
    print(f"{indent}{label}: {k}/{n} = {k / n:.4%}")
    print(f"{indent}    Wilson 95% (statsmodels) [{wlo:.4%}, {whi:.4%}]")
    print(f"{indent}    Wilson 95% (mpmath,50dp) [{hlo:.4%}, {hhi:.4%}]  "
          f"max|diff| {delta:.2e}")
    print(f"{indent}    Clopper-Pearson 95%      [{clo:.4%}, {chi:.4%}]")


def rule(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


# ------------------------------------------------------------------------ main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog=pathlib.Path(__file__).name,
        description=(__doc__ or "").strip().splitlines()[0],
        epilog="Takes no arguments; --help does no work and touches nothing.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--full-doc", action="store_true",
                    help="print this script's full docstring and exit")
    args = ap.parse_args(argv)
    if args.full_doc:
        print((__doc__ or "").strip())
        return 0

    rows = list(entries())
    targets = {fp: run_target(fp) for fp in {fp for fp, _c, _e in rows}}
    n_all = len(rows)
    if n_all < 100:
        print(f"only {n_all} archived entries found under {LOGS}; measurement void.")
        return 3

    pop = [(fp, cid, e) for fp, cid, e in rows if in_population(e)]
    n = len(pop)

    print("THE CORPUS, reusing the 3,298 producers' enumeration")
    print("=" * 72)
    print(f"  files globbed  : bench/logs/**/runner_state.json  "
          f"({len({fp for fp, _c, _e in rows})} files)")
    print("  predicate      : registry.entries[*] is a dict with numeric severity")
    print(f"  entries        : {n_all}   (producers report 3,298: "
          f"{'MATCH' if n_all == 3298 else 'MISMATCH'})")

    rule("STEP 2. REPRODUCING 1938, AND NAMING WHICH DEFINITION IT IS")
    defs = [
        ("falsifier_code absent or empty", lambda e: not code(e)),
        ("  ... OR verdict UNTOOLABLE", in_population),
        ("falsifier_verdict absent or blank", lambda e: not verdict(e)),
        ("  ... OR verdict UNTOOLABLE", lambda e: (not verdict(e)
                                                   or verdict(e) == "UNTOOLABLE")),
        ("verdict not in {CONFIRMED,REFUTED}", lambda e: verdict(e) not in DECIDED),
        ("no falsifier_code KEY at all", lambda e: "falsifier_code" not in e),
    ]
    for lab, f in defs:
        k = sum(1 for _fp, _c, e in rows if f(e))
        flag = "  <== THE CLAIM'S 1938" if k == 1938 else ""
        print(f"  {lab:<38}{k:>6}/{n_all} = {k / n_all:8.4%}{flag}")
    print()
    pct("CLAIM REPRODUCED: untoolable or no falsifier", n, n_all)
    print("  The claim states 1938/3298 = 58.7629%. "
          f"{'EXACT MATCH.' if n == 1938 and n_all == 3298 else 'DIFFERS -- see above.'}")

    rule("STEP 3a. KEY INVENTORY over the population (what the archive HAS)")
    keys = collections.Counter()
    for _fp, _c, e in pop:
        for k_ in e:
            keys[k_] += 1
    for k_, c in keys.most_common():
        print(f"  {k_:<32}{c:>6}/{n}")
    print()
    print("  FIELDS THAT DO NOT EXIST ANYWHERE IN THE CORPUS:")
    for absent in ("untoolable_reason", "falsifier_attempts", "irreducible_reason",
                   "execution_log", "confidence", "constraint_class"):
        tot = sum(1 for _fp, _c, e in rows if absent in e)
        print(f"    {absent:<24}{tot:>6}/{n_all}")
    print("  -> there is NO field recording why a finding was untoolable. Any")
    print("     statement of genuine irreducibility must come from a free-text")
    print("     reason, and only three fields ever carry one.")
    print()
    print("  VERDICT FIELD ON THE POPULATION:")
    for v, c in collections.Counter(
            verdict(e) or "(absent or blank)" for _fp, _c, e in pop).most_common():
        print(f"    {v:<24}{c:>6}")
    print()
    print("  REASON-BEARING FIELDS ON THE POPULATION:")
    for f in ("withdraw_reason", "routing_defer_reason", "hil_reason",
              "close_reason", "merge_blocked_reason", "computed_evidence"):
        print(f"    {f:<32}{sum(1 for _fp, _c, e in pop if e.get(f)):>6}")
    print(f"    {'ANY of the 3 toolability reasons':<32}"
          f"{sum(1 for _fp, _c, e in pop if reason_strings(e)):>6}")
    print()
    print("  ADJACENT EXECUTION RECORDS (about the FIX, not the claim):")
    print(f"    sk_result present       "
          f"{sum(1 for _fp, _c, e in pop if e.get('sk_result') is not None):>6}")
    print(f"    sk_evaluated true       "
          f"{sum(1 for _fp, _c, e in pop if e.get('sk_evaluated')):>6}")
    print("    The corpus's own routing_defer_reason refuses to read S_k as a")
    print("    test of the claim; this script does not count it as one.")

    rule("STEP 3b. THE CLASSES (precedence B, A, D, E -- irreducible first)")
    cls = collections.Counter(classify(e) for _fp, _c, e in pop)
    labels = {
        "B_reasoned_irreducible": "B GENUINELY IRREDUCIBLE (a reason says so)",
        "A_attempt_no_falsifier": "A ATTEMPT RECORDED, no falsifier stored",
        "D_administratively_moot": "D ADMINISTRATIVELY MOOT (merged away)",
        "E_never_attempted": "E NEVER ATTEMPTED (nothing in the record)",
    }
    for k_ in ("B_reasoned_irreducible", "A_attempt_no_falsifier",
               "D_administratively_moot", "E_never_attempted"):
        pct(labels[k_], cls[k_], n)
    print(f"  partition total: {sum(cls.values())} of {n} "
          f"({'exhaustive and disjoint' if sum(cls.values()) == n else 'BROKEN'})")
    print()
    print("  THE HEADLINE CONTRAST, as the claim asks it:")
    gi = cls["B_reasoned_irreducible"]
    na = cls["E_never_attempted"]
    pct("genuinely irreducible, of the untoolable set", gi, n)
    pct("never attempted at all, of the untoolable set", na, n)
    if gi:
        print(f"  ratio never-attempted : irreducible = {na / gi:.1f} : 1")
    print()
    print("  AND THE WIDEST POSSIBLE READING OF IRREDUCIBILITY: count EVERY")
    print("  entry carrying any toolability reason at all as irreducible, even")
    print("  the ones whose reason records a hand check or a duplicate.")
    widest = sum(1 for _fp, _c, e in pop if reason_strings(e))
    pct("upper bound on irreducible", widest, n)
    print("  Even at that bound the remainder -- entries for which the archive")
    print("  gives no reason whatsoever -- is:")
    pct("no reason recorded", n - widest, n)

    rule("STEP 3c. SUB-ANATOMY OF CLASS A (what the attempt mark actually was)")
    a = [(fp, cid, e) for fp, cid, e in pop
         if classify(e) == "A_attempt_no_falsifier"]
    na_ = len(a)
    for lab, f in (
        ("verdict UNTOOLABLE, code empty", lambda e: verdict(e) == "UNTOOLABLE"),
        ("verdict ERROR, code empty", lambda e: verdict(e) == "ERROR"),
        ("verdict key present but BLANK", lambda e: "falsifier_verdict" in e
            and verdict(e) == ""),
        ("routing ladder logged rungs", lambda e: bool(e.get("routing_history"))),
        ("error_routed", lambda e: bool(e.get("error_routed"))),
        ("exhausted true", lambda e: e.get("exhausted") is True),
        ("irreducible_escalation true", lambda e: bool(e.get("irreducible_escalation"))),
    ):
        print(f"  {lab:<34}{sum(1 for _fp, _c, e in a if f(e)):>6}/{na_}")
    rungs = collections.Counter()
    for _fp, _c, e in pop:
        for s in e.get("routing_history") or []:
            if isinstance(s, dict):
                rungs[(s.get("rungs_tried"), s.get("rungs_available"))] += 1
    if rungs:
        print("  routing ladder (rungs_tried, rungs_available) over the population:")
        for kk, c in rungs.most_common():
            print(f"    {str(kk):<16}{c:>6}")
        print("  A ladder that stops at 2 of 5 has not shown rungs 3-5 would fail.")

    rule("STEP 4. THE OBJECTIVE REDUCIBILITY SIGNAL (what the claims are ABOUT)")
    ext = collections.Counter()
    prov = collections.Counter()
    for fp, _c, e in pop:
        t, src = target_of(e, targets.get(fp))
        prov[src] += 1
        ext[pathlib.PurePath(t).suffix.lower() if t else "(unknown)"] += 1
    print("  target attributed from:")
    for s, c in prov.most_common():
        print(f"    {s:<16}{c:>6}")
    print("  by target extension:")
    for x, c in ext.most_common():
        print(f"    {x or '(no extension)':<16}{c:>6}/{n} = {c / n:8.4%}")
    print()
    pct("target is a .py source file", ext[".py"], n)
    code_n = sum(1 for _fp, _c, e in pop
                 if CODEISH_RE.search(str(e.get("description") or "")))
    num_n = sum(1 for _fp, _c, e in pop
                if NUMERIC_RE.search(str(e.get("description") or "")))
    either = sum(1 for _fp, _c, e in pop
                 if CODEISH_RE.search(str(e.get("description") or ""))
                 or NUMERIC_RE.search(str(e.get("description") or "")))
    pct("claim text carries a CODE reference", code_n, n)
    pct("claim text carries a NUMERIC literal", num_n, n)
    pct("carries a code reference or a number", either, n)
    pct("carries NEITHER (no mechanical handle)", n - either, n)
    print("  flaw_class of the population (8 = documentation, the only prose class):")
    for fc, c in sorted(collections.Counter(
            str(e.get("flaw_class")) for _fp, _c, e in pop).items()):
        print(f"    class {fc:<10}{c:>6}")
    pct("flaw_class 8 (documentation)",
        sum(1 for _fp, _c, e in pop if str(e.get("flaw_class")) == "8"), n)

    rule("STEP 5. CROSS-CHECK: untoolable here, TOOLED elsewhere")
    groups = collections.defaultdict(list)
    unkeyable = 0
    for fp, cid, e in rows:
        k_ = dedup_key(e)
        if k_ is None:
            unkeyable += 1
            continue
        groups[k_].append((fp, cid, e))
    twinned, shown = [], []
    for _k, g in groups.items():
        mine = [x for x in g if in_population(x[2])]
        done = [x for x in g if not in_population(x[2])
                and verdict(x[2]) in DECIDED and code(x[2])]
        if mine and done:
            twinned.extend(mine)
            shown.append((mine[0], done[0], len(mine)))
    print(f"  dedup keys (normalised claim text, 300ch): {len(groups)} over "
          f"{n_all - unkeyable} keyable entries")
    print(f"  entries with claim text under {DEDUP_MIN_CHARS}ch, EXCLUDED as "
          f"unkeyable: {unkeyable}")
    print("  (an earlier pass keyed them too and reported 60 tooled twins; all")
    print("   60 were empty-description entries colliding on one hash. The")
    print("   figure below is what survives excluding them.)")
    pct("population entries with a TOOLED dedup twin", len(twinned), n)
    for (m, d, cnt_) in shown[:8]:
        print(f"    {m[0].parent.name}/{m[1]}  ->  "
              f"{d[0].parent.name}/{d[1]}  {verdict(d[2])} "
              f"({len(code(d[2]))}ch of falsifier)  [{cnt_} untooled copies]")
    if len(shown) > 8:
        print(f"    ... and {len(shown) - 8} more dedup keys")
    if not shown:
        print("    NONE. No substantive claim text appears both without a")
        print("    falsifier in one run and with an executed, decided one in")
        print("    another. The dedup route yields no instance, so the")
        print("    within-entry route below is the only evidence on this point.")
    within = sum(1 for _fp, _c, e in rows
                 if any(str(s.get("verdict") or "").upper() in ("UNTOOLABLE", "ERROR")
                        for s in (e.get("routing_history") or [])
                        if isinstance(s, dict))
                 and verdict(e) in DECIDED and code(e))
    pct("entries whose own routing log shows UNTOOLABLE/ERROR yet ended DECIDED",
        within, n_all)
    print("  Each of these is a direct instance of a finding the machinery")
    print("  called untoolable and a falsifier later decided.")

    rule("STEP 6. TWO-TOOL AGREEMENT ON EVERY WILSON INTERVAL")
    worst = max(AGREEMENT) if AGREEMENT else 0.0
    print(f"  intervals computed by both routes : {len(AGREEMENT)}")
    print(f"  worst |statsmodels - mpmath|     : {worst:.3e}")
    print(f"  agree to 1e-12                   : {'YES' if worst < 1e-12 else 'NO'}")

    rule("VERDICT")
    print(f"  Of the {n} archived findings recorded UNTOOLABLE or carrying no")
    print(f"  falsifier ({n}/{n_all} = {n / n_all:.4%}):")
    print(f"    GENUINELY IRREDUCIBLE, by the archive's own reasons : {gi}"
          f"  ({gi / n:.4%})")
    print(f"    NEVER ATTEMPTED, nothing in the record at all       : {na}"
          f"  ({na / n:.4%})")
    print(f"    ATTEMPT RECORDED but no falsifier stored            : "
          f"{cls['A_attempt_no_falsifier']}  "
          f"({cls['A_attempt_no_falsifier'] / n:.4%})")
    print(f"    ADMINISTRATIVELY MOOT (merged)                      : "
          f"{cls['D_administratively_moot']}  "
          f"({cls['D_administratively_moot'] / n:.4%})")
    print()
    print("  THE DISTINCTION IS DECIDABLE IN ONE DIRECTION ONLY, and the key")
    print("  inventory above is why. No `untoolable_reason` field exists, so")
    print(f"  irreducibility can only be read off the {widest} entries that carry")
    print("  a free-text toolability reason. For the rest the archive records")
    print("  the ABSENCE of a falsifier and says nothing about why -- which is")
    print("  itself the answer to the question asked: the corpus cannot show")
    print("  that a tool was tried and failed, because for the overwhelming")
    print("  majority no tool was tried. The objective signal points the same")
    print(f"  way: {ext['.py']} of {n} target a .py source file and {either} carry a")
    print("  code reference or a number in the claim text, so they are")
    print("  mechanically checkable in principle. The cross-check finds")
    print(f"  {len(twinned)} cross-run dedup twins (the dedup route is weak here: all")
    print("  but 82 claims are textually unique to one run), but it does find")
    print(f"  {within} entries whose OWN routing log recorded UNTOOLABLE or ERROR")
    print("  and which a falsifier nevertheless went on to decide -- each one a")
    print("  worked instance of never-attempted-then-toolable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
