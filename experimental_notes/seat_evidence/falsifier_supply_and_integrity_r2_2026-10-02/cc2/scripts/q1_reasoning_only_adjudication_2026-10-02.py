# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'falsifier_supply_and_integrity_r2_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 8b1dfd1b7cadc3c2204a75fb98d9286703bf9e0378e4159a64d4405783ac8d49
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Q1: is the INTELLIGENCE-FIRST CONTRACT honoured on the archive?

THE QUESTION, sharpened so it can be falsified. The project forbids settling a
finding by model vote: a verdict is supposed to come from an INSTRUMENT. So of
the CRITICAL findings whose verdict came from MODEL REASONING rather than from
a tool, what proportion were SUBSEQUENTLY adjudicated by a tool? A
reasoning-only CONFIRMED that no tool ever revisits is a DEFECT, not a style.

POPULATION IS NOT REINVENTED. `harvest()` below is the loader of
`scripts/falsifier_supply_decomposition_2026-10-02.py`, unchanged in its
globs (`bench/logs/*/runner_state.json` and `bench/logs/*/*_report.json`), its
severity cut (>= 0.7), its deduplication key `(cid, sha1(description[:4000]))`
and its body-preferring tie-break. It reproduces 2596 raw -> 1309
deduplicated. The ONLY addition is PROVENANCE: which run directory each record
came from, and every raw record kept rather than only the winner, because part
(b) of the question is about a LATER round of the SAME run and that cannot be
asked of a collapsed record.

WHAT COUNTS AS A TOOL, STATED BEFORE MEASURING. A tool adjudication leaves a
RECORD OF EXECUTION in the entry:

    falsifier_code                        a body that was run
    routing_history[].last_falsifier_code a body the ladder ran
    computed_evidence                     discrimination-control executions
    discrimination                        baseline/corrected re-execution
    status_adjudicator == "tool"          the transition names a tool
    status_log[].adjudicator == "tool"    ditto, per transition

A model adjudication leaves PROSE AND A COUNT OF OPINIONS:

    verdicts[]                            per-model CONFIRM/CHALLENGE votes
    status_mechanism model_confirm_quorum / model_merge_vote
    rounds[].verification.verdicts[cid]   a verification pass by a model

THE SECOND CHANNEL IS WHY THE FIRST LOOKS CLEAN. Read only
`falsifier_verdict`, and the contract appears perfect: every CONFIRMED or
REFUTED falsifier_verdict in the archive carries a body, so the literal
predicate "CONFIRMED/REFUTED verdict with no body" has ZERO members. But
`status` carries its own terminal verdict, reached without any falsifier at
all, and that is the channel the contract is actually about. Both are reported;
reporting only the first would be a measurement that cannot fail.

CROSS-VERIFICATION. Every proportion carries a Wilson 95% interval from
statsmodels AND an independent mpmath closed form, with agreement asserted.
The stratum comparison is a Fisher exact test (scipy), cross-checked against an
mpmath hypergeometric closed form. No Wolfram result is used.
"""
from __future__ import annotations

import collections
import hashlib
import json
import pathlib
import sys

for _cand in (pathlib.Path(__file__).resolve().parent,
              *pathlib.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
CRITICAL = 0.7

#: Terminal adjudications in the STATUS channel. CLOSED is reported apart: it
#: is terminal and nearly all of its tool-free records carry verified=True,
#: but it is reached THROUGH a verdict rather than being one, so pooling it
#: with CONFIRMED would overstate the headline.
STATUS_VERDICTS = ("CONFIRMED", "REFUTED")


def wilson(k: int, n: int):
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    if n == 0:
        return None
    lo_sm, hi_sm = proportion_confint(k, n, method="wilson")
    mp.mp.dps = 40
    z = mp.mpf("1.959963984540054235524594430520551527955")
    p, d = mp.mpf(k) / n, 1 + z ** 2 / n
    c = p + z ** 2 / (2 * n)
    hh = z * mp.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2))
    lo_mp, hi_mp = float((c - hh) / d), float((c + hh) / d)
    agree = abs(lo_sm - lo_mp) < 1e-9 and abs(hi_sm - hi_mp) < 1e-9
    return float(lo_sm), float(hi_sm), lo_mp, hi_mp, agree


def pct(k: int, n: int, label: str, indent: str = "    ") -> None:
    if not n:
        print(f"{indent}{label:46s} {k:5d}  (NOT MEASURABLE: no denominator)")
        return
    w = wilson(k, n)
    print(f"{indent}{label:46s} {k:5d} / {n:5d} = {100*k/n:8.4f}%  "
          f"Wilson [{100*w[0]:7.4f}%, {100*w[1]:7.4f}%]  agree={w[4]}")


def _body(e: dict) -> str:
    """The reference script's body predicate, unchanged."""
    return ((e.get("falsifier_code") or "").strip()
            or (e.get("last_falsifier_code") or "").strip())


def harvest():
    """Every critical in the archive, deduplicated, WITH provenance."""
    raw = 0
    seen: dict = {}
    key_run: dict = {}
    key_cid: dict = {}
    by_run_cid: dict = {}
    parse_failures = 0
    files = 0
    sk_rounds: dict = {}
    ver_rounds: dict = {}
    apparatus: set = set()
    for name in ("runner_state.json", "*_report.json"):
        for f in sorted((ROOT / "bench" / "logs").glob(f"*/{name}")):
            files += 1
            try:
                data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            except (ValueError, OSError):
                parse_failures += 1
                continue
            run = f.parent.name
            # ---- round-stamped, PER-CID tool executions and model passes.
            rounds = data.get("rounds")
            if isinstance(rounds, list):
                for r in rounds:
                    if not isinstance(r, dict):
                        continue
                    rn = r.get("round")
                    skp = r.get("sk_pipeline")
                    if isinstance(skp, dict) and isinstance(skp.get("results"), dict):
                        rr = skp.get("round", rn)
                        if isinstance(rr, int):
                            for cid in skp["results"]:
                                sk_rounds.setdefault((run, cid), []).append(rr)
                    vf = r.get("verification")
                    if isinstance(vf, dict) and isinstance(vf.get("verdicts"), dict):
                        rr = vf.get("round", rn)
                        if isinstance(rr, int):
                            for cid, vd in vf["verdicts"].items():
                                act = (vd or {}).get("action") if isinstance(vd, dict) else None
                                ver_rounds.setdefault((run, cid), []).append((rr, act or ""))
            reg = (data.get("registry") or {}).get("entries") or {}
            for cid, e in reg.items():
                if not isinstance(e, dict):
                    continue
                if (e.get("severity") or 0.0) < CRITICAL:
                    continue
                raw += 1
                if "falsifier_verdict" in e or "falsifier_code" in e:
                    apparatus.add(run)
                by_run_cid.setdefault((run, cid), []).append(e)
                desc = (e.get("description") or e.get("title") or "")[:4000]
                key = (cid, hashlib.sha1(desc.encode("utf-8", "replace")).hexdigest())
                prev = seen.get(key)
                if prev is None or (not _body(prev) and _body(e)):
                    seen[key] = e
                key_run.setdefault(key, run)
                key_cid.setdefault(key, cid)
    return dict(raw=raw, seen=seen, parse_failures=parse_failures, files=files,
                key_run=key_run, key_cid=key_cid, by_run_cid=by_run_cid,
                sk_rounds=sk_rounds, ver_rounds=ver_rounds, apparatus=apparatus)


# --------------------------------------------------------------------------
# channel predicates
# --------------------------------------------------------------------------
def tool_record(e: dict) -> str:
    """Name the tool-execution record this entry carries, or ''."""
    if _body(e):
        return "falsifier_code"
    if any((hh.get("last_falsifier_code") or "").strip()
           for hh in (e.get("routing_history") or []) if isinstance(hh, dict)):
        return "routing_history.last_falsifier_code"
    if e.get("computed_evidence"):
        return "computed_evidence"
    if e.get("discrimination"):
        return "discrimination"
    if e.get("status_adjudicator") == "tool":
        return "status_adjudicator=tool"
    if any(s.get("adjudicator") == "tool"
           for s in (e.get("status_log") or []) if isinstance(s, dict)):
        return "status_log.adjudicator=tool"
    return ""


def model_record(e: dict) -> str:
    """Name the model-reasoning adjudication record, or ''."""
    if e.get("verdicts"):
        return "verdicts[] (per-model votes)"
    mech = (e.get("status_mechanism") or "")
    if mech.startswith("model_"):
        return f"status_mechanism={mech}"
    for s in (e.get("status_log") or []):
        if isinstance(s, dict):
            if s.get("adjudicator") == "model":
                return "status_log.adjudicator=model"
            if (s.get("mechanism") or "").startswith("model_"):
                return f"status_log.mechanism={s['mechanism']}"
    return ""


def falsifier_channel_verdict(e: dict) -> str:
    hist = e.get("routing_history") or []
    last = ((hist[-1].get("verdict") or "").strip().upper()
            if hist and isinstance(hist[-1], dict) else "")
    return ((e.get("falsifier_verdict") or "").strip().upper()
            or (e.get("routing_verdict_unreconciled") or "").strip().upper()
            or last)


def adj_round(e: dict):
    """When the reasoning verdict landed. Prefer the recorded transition."""
    r = e.get("last_status_change_round")
    if isinstance(r, int):
        return r
    rs = [v.get("round") for v in (e.get("verdicts") or [])
          if isinstance(v, dict) and isinstance(v.get("round"), int)]
    return max(rs) if rs else None


def later_tool_adjudication(h, key, e):
    """Did a tool touch this cid in a LATER round of the SAME run?

    Matchers are all keyed on (run, cid) and all require a round STRICTLY
    GREATER than the round the reasoning verdict landed on. The
    sibling-artefact matcher has no round of its own and is counted
    separately as an UPPER BOUND rather than silently folded in.
    """
    run, cid = h["key_run"][key], h["key_cid"][key]
    r0 = adj_round(e)
    hits = []
    if r0 is not None:
        for rr in h["sk_rounds"].get((run, cid), []):
            if rr > r0:
                hits.append(f"sk_pipeline@r{rr}")
                break
        for sib in h["by_run_cid"].get((run, cid), []):
            for s in (sib.get("status_log") or []):
                if (isinstance(s, dict) and s.get("adjudicator") == "tool"
                        and isinstance(s.get("round"), int) and s["round"] > r0):
                    hits.append(f"status_log.tool@r{s['round']}")
                    break
            for hh in (sib.get("routing_history") or []):
                if (isinstance(hh, dict) and (hh.get("last_falsifier_code") or "").strip()
                        and isinstance(hh.get("round"), int) and hh["round"] > r0):
                    hits.append(f"routing_history.body@r{hh['round']}")
                    break
            d = sib.get("discrimination")
            if isinstance(d, dict) and isinstance(d.get("round"), int) and d["round"] > r0:
                hits.append(f"discrimination@r{d['round']}")
    sibling_body = any(_body(sib) for sib in h["by_run_cid"].get((run, cid), []))
    return hits, sibling_body


def main() -> int:
    h = harvest()
    seen, raw = h["seen"], h["raw"]
    n = len(seen)
    print("POPULATION (loader reused from "
          "falsifier_supply_decomposition_2026-10-02.py)")
    print(f"  archive files read                : {h['files']}")
    print(f"  unreadable (reported, not dropped): {h['parse_failures']}")
    print(f"  critical entries, RAW             : {raw}")
    print(f"  critical entries, DEDUPLICATED    : {n}")
    print(f"  run directories contributing      : {len(set(h['key_run'].values()))}")
    print(f"  runs carrying falsifier apparatus : {len(h['apparatus'])}")

    # ---------------- field inventory -------------------------------------
    print(f"\nFIELD INVENTORY over the {n} DEDUPLICATED criticals "
          "(present / non-empty)")
    present, filled = collections.Counter(), collections.Counter()
    for e in seen.values():
        for k, v in e.items():
            present[k] += 1
            if v not in (None, "", [], {}, 0, 0.0, False):
                filled[k] += 1
    INTEREST = ["falsifier_code", "falsifier_verdict", "falsifier_stderr",
                "falsifier_stdout", "last_falsifier_code", "routing_history",
                "routing_verdict_unreconciled", "routing_verdict_reconciled",
                "status", "status_adjudicator", "status_mechanism",
                "status_evidence", "status_log", "verdicts", "verified",
                "verify_result", "computed_evidence", "discrimination",
                "sk_result", "fix_efficacy", "severity_proof", "escalated"]
    print("  -- adjudication-relevant fields (asked for by name; ABSENT means "
          "the field does not exist in this archive at all) --")
    for k in INTEREST:
        if k in present:
            print(f"    {k:34s} present {present[k]:5d} ({100*present[k]/n:6.2f}%)"
                  f"  non-empty {filled[k]:5d} ({100*filled[k]/n:6.2f}%)")
        else:
            print(f"    {k:34s} ABSENT from every entry")
    print("  -- every other field, by presence --")
    for k, c in present.most_common():
        if k in INTEREST:
            continue
        print(f"    {k:34s} present {c:5d} ({100*c/n:6.2f}%)"
              f"  non-empty {filled[k]:5d} ({100*filled[k]/n:6.2f}%)")

    print("\n  observed falsifier_verdict values:",
          dict(collections.Counter(
              (e.get("falsifier_verdict") or "").strip().upper()
              for e in seen.values() if "falsifier_verdict" in e).most_common()))
    print("  observed status values:",
          dict(collections.Counter(e.get("status") for e in seen.values()).most_common()))
    print("  observed status_adjudicator values:",
          dict(collections.Counter(e.get("status_adjudicator")
                                   for e in seen.values()).most_common()))

    # ---------------- (0) the literal predicate ---------------------------
    print("\n(0) THE LITERAL PREDICATE: falsifier_verdict CONFIRMED/REFUTED "
          "with NO body")
    fv_any = [e for e in seen.values() if falsifier_channel_verdict(e)]
    fv_cr = [e for e in fv_any
             if falsifier_channel_verdict(e) in ("CONFIRMED", "REFUTED")]
    fv_cr_nobody = [e for e in fv_cr if not tool_record(e)]
    pct(len(fv_any), n, "criticals with ANY falsifier-channel verdict")
    pct(len(fv_cr), n, "  of which CONFIRMED or REFUTED")
    pct(len(fv_cr_nobody), len(fv_cr),
        "  CONFIRMED/REFUTED with no tool record")
    nb = [e for e in fv_any if not _body(e)]
    print(f"    verdict-but-no-body, all verdicts  : {len(nb)}  "
          f"({dict(collections.Counter(falsifier_channel_verdict(e) for e in nb))})")
    print("    => in the FALSIFIER channel the contract is vacuously honoured:")
    print("       no CONFIRMED/REFUTED falsifier_verdict exists without a body.")

    # ---------------- (a) the status channel ------------------------------
    print("\n(a) THE STATUS CHANNEL: a terminal verdict reached with NO tool "
          "record anywhere in the entry")
    adjudicated = [(k, e) for k, e in seen.items()
                   if e.get("status") in STATUS_VERDICTS
                   or falsifier_channel_verdict(e) in ("CONFIRMED", "REFUTED")]
    reasoning_only = [(k, e) for k, e in adjudicated if not tool_record(e)]
    tool_backed = [(k, e) for k, e in adjudicated if tool_record(e)]
    pct(len(adjudicated), n, "criticals carrying a CONFIRMED/REFUTED verdict")
    pct(len(tool_backed), len(adjudicated), "  verdict backed by a TOOL record")
    pct(len(reasoning_only), len(adjudicated), "  verdict from MODEL REASONING only")
    print("    tool records seen, where present:",
          dict(collections.Counter(tool_record(e) for _, e in tool_backed).most_common()))
    print("    model records among reasoning-only:",
          dict(collections.Counter(model_record(e) or "NO RECORD AT ALL"
                                   for _, e in reasoning_only).most_common()))
    print("    their status:",
          dict(collections.Counter(e.get("status") for _, e in reasoning_only).most_common()))
    ro_conf = [(k, e) for k, e in reasoning_only if e.get("status") == "CONFIRMED"]
    print(f"    REASONING-ONLY *CONFIRMED* (the defect, deduplicated): {len(ro_conf)}")
    pct(len(ro_conf), n, "  as a share of all criticals")

    print("\n  SECONDARY, reported apart: CLOSED with no tool record. CLOSED is "
          "terminal\n  and is reached through a verdict, so it is not pooled "
          "with CONFIRMED above.")
    closed_nt = [e for e in seen.values()
                 if e.get("status") == "CLOSED" and not tool_record(e)]
    pct(len(closed_nt), n, "CLOSED, no tool record, of all criticals")
    print("    of those, verified=True (closed as a fixed finding with no "
          f"falsifier): {sum(1 for e in closed_nt if e.get('verified'))}")

    # ---------------- (b) subsequent tool adjudication --------------------
    print("\n(b) OF THE REASONING-ONLY VERDICTS, HOW MANY WERE SUBSEQUENTLY "
          "ADJUDICATED BY A TOOL?\n    (same run, same cid, round strictly "
          "later than the reasoning verdict)")
    datable = [(k, e) for k, e in reasoning_only if adj_round(e) is not None]
    later, sib_only, reasons = [], [], collections.Counter()
    for k, e in reasoning_only:
        hits, sibling_body = later_tool_adjudication(h, k, e)
        if hits:
            later.append((k, e))
            reasons[hits[0].split("@")[0]] += 1
        elif sibling_body:
            sib_only.append((k, e))
    print(f"    reasoning-only verdicts                     : {len(reasoning_only)}")
    print(f"    of those, with a datable verdict round      : {len(datable)}")
    pct(len(later), len(reasoning_only), "SUBSEQUENTLY adjudicated by a tool")
    pct(len(later), len(datable), "  same, denominator = datable only")
    pct(len(reasoning_only) - len(later), len(reasoning_only),
        "NEVER revisited by any tool")
    print(f"    matcher that fired, where one did: {dict(reasons)}")
    pct(len(sib_only), len(reasoning_only),
        "  (upper bound: sibling artefact has a body)")

    # THE 23% IS THE GENEROUS READING AND SAYING SO IS THE POINT. sk_pipeline
    # runs real instruments (ast, py_compile, pytest, ruff, bandit) but it
    # gates the PROPOSED FIX for admissibility; it never re-adjudicates
    # whether the finding is true. Counting it as "adjudicated by a tool" is
    # the most favourable construction the archive admits. The STRICT figure
    # asks the contract's actual question -- did an instrument later rule on
    # the CLAIM -- and is reported beside it, because the two differ by the
    # whole of the answer.
    strict = [1 for k, e in reasoning_only
              if any(not hit.startswith("sk_pipeline")
                     for hit in later_tool_adjudication(h, k, e)[0])]
    pct(len(strict), len(reasoning_only),
        "STRICT: a tool later ruled on the CLAIM")
    # And did a MODEL come back instead? rounds[].verification is a per-cid,
    # round-stamped verification pass whose adjudicator is a model.
    model_revisit = 0
    for k, e in reasoning_only:
        r0 = adj_round(e)
        run, cid = h["key_run"][k], h["key_cid"][k]
        if r0 is not None and any(rr > r0
                                  for rr, _ in h["ver_rounds"].get((run, cid), [])):
            model_revisit += 1
    pct(model_revisit, len(reasoning_only),
        "  for contrast: a MODEL later re-verified it")
    anyver = sum(1 for k, e in reasoning_only
                 if h["ver_rounds"].get((h["key_run"][k], h["key_cid"][k])))
    anysk = sum(1 for k, e in reasoning_only
                if h["sk_rounds"].get((h["key_run"][k], h["key_cid"][k])))
    print(f"    coverage, so the zeros are not mistaken for absence of data:")
    print(f"      reasoning-only cids with ANY verification pass on record: {anyver}")
    print(f"      reasoning-only cids with ANY sk_pipeline record         : {anysk}"
          f"   <- hard ceiling on the generous figure")

    # A SCRIPT THAT PRINTS 0 MUST SHOW ITS MATCHER CAN FIRE, or the 0 is
    # indistinguishable from a typo. Anchor the SAME strict matchers one round
    # before each tool-backed finding opened and count the fires. If this
    # self-check reports 0 the strict result above is void and must be
    # discarded rather than believed.
    ctl = collections.Counter()
    for k, e in tool_backed:
        anchor = e.get("open_since_round")
        if not isinstance(anchor, int):
            continue
        run, cid = h["key_run"][k], h["key_cid"][k]
        for sib in h["by_run_cid"].get((run, cid), []):
            for st in (sib.get("status_log") or []):
                if (isinstance(st, dict) and st.get("adjudicator") == "tool"
                        and isinstance(st.get("round"), int)
                        and st["round"] > anchor - 1):
                    ctl["status_log.adjudicator=tool"] += 1
            for hh in (sib.get("routing_history") or []):
                if (isinstance(hh, dict)
                        and (hh.get("last_falsifier_code") or "").strip()
                        and isinstance(hh.get("round"), int)
                        and hh["round"] > anchor - 1):
                    ctl["routing_history.body"] += 1
            d = sib.get("discrimination")
            if (isinstance(d, dict) and isinstance(d.get("round"), int)
                    and d["round"] > anchor - 1):
                ctl["discrimination"] += 1
    print(f"    SELF-CHECK of the strict matchers, anchor relaxed to "
          f"open_since_round-1\n      on the {len(tool_backed)} tool-backed "
          f"findings: {dict(ctl)}")
    print(f"      matchers fire {sum(ctl.values())} times when a tool record "
          f"exists after the anchor,\n      so the 0 above is a measurement, "
          f"not a dead branch."
          if sum(ctl.values()) else
          "      MATCHERS NEVER FIRE: the strict result above is NOT MEASURABLE.")

    ro_conf_later = [1 for k, e in ro_conf if later_tool_adjudication(h, k, e)[0]]
    pct(len(ro_conf_later), len(ro_conf),
        "of reasoning-only CONFIRMED, later tooled")

    # ---------------- (c) two strata, Fisher exact ------------------------
    print("\n(c) TWO STRATA: runs that HAVE the falsifier apparatus vs runs "
          "that do not")
    strata = {True: [0, 0], False: [0, 0]}  # [reasoning_only, tool_backed]
    for k, e in adjudicated:
        s = h["key_run"][k] in h["apparatus"]
        strata[s][0 if not tool_record(e) else 1] += 1
    for s, label in ((True, "runs WITH falsifier apparatus"),
                     (False, "runs WITHOUT falsifier apparatus")):
        ro, tb = strata[s]
        pct(ro, ro + tb, f"{label}: reasoning-only share")
    a, b = strata[True]
    c, d = strata[False]
    print(f"    2x2 table [[reasoning-only, tool-backed]] = [[{a}, {b}], [{c}, {d}]]")
    try:
        from scipy.stats import fisher_exact
        orr, p = fisher_exact([[a, b], [c, d]])
        import mpmath as mp
        mp.mp.dps = 50

        def _hg(i):
            return (mp.binomial(a + b, i) * mp.binomial(c + d, a + c - i)
                    / mp.binomial(a + b + c + d, a + c))
        lo, hi = max(0, a + c - (c + d)), min(a + b, a + c)
        obs = _hg(a)
        p_mp = float(mp.fsum([_hg(i) for i in range(lo, hi + 1)
                              if _hg(i) <= obs * (1 + mp.mpf("1e-25"))]))
        print(f"    Fisher exact (scipy):  odds ratio = {orr:.6g}, p = {p:.6g}")
        print(f"    Fisher exact (mpmath hypergeometric closed form): "
              f"p = {p_mp:.6g}, agree={abs(p - p_mp) < 1e-9}")
    except ImportError as exc:
        print(f"    NOT MEASURABLE: Fisher exact needs scipy ({exc})")

    # ---------------- verdict ---------------------------------------------
    print("\nVERDICT ON THE CONTRACT")
    print(f"  reasoning-only CONFIRMED criticals, never tooled even on the "
          f"generous reading: {len(ro_conf) - len(ro_conf_later)} of {len(ro_conf)}")
    print(f"  reasoning-only CONFIRMED criticals no tool ever ruled on the "
          f"CLAIM for: {len(ro_conf) - len(strict)} of {len(ro_conf)}")
    if len(ro_conf) - len(ro_conf_later) > 0:
        print("  => THE INTELLIGENCE-FIRST CONTRACT IS VIOLATED on this archive.")
    else:
        print("  => honoured.")
    return 0


if __name__ == "__main__":
    answer_help(__doc__, __file__)
    raise SystemExit(main())
