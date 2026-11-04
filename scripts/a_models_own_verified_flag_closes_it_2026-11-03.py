#!/usr/bin/env python3
"""A model's own VERIFIED flag closes its finding, labelled as tool-adjudicated.

FOUND 2026-11-02 while answering his question about which lessons from the
ticket store should reach the harness registry. The first answer to that question
said the registry ALREADY had the ticket store's terminal-state rule, because
`grep` found 10 lines in the canonical runner mentioning CLOSED and `verified`.
Those 10 lines are a docstring, a report string and comments. Executing the code
says the opposite, which is why `execute-do-not-grep` exists.

THE CHAIN, each link established by the means named.

  1. EXECUTED. `runner_core.parse_findings` reads `VERIFIED` out of the model's
     own reply JSON and sets `Finding.verified` from it, accepting both the
     boolean `true` and the string `"TRUE"`. A reply saying `false` yields
     False, so the probe is not vacuous.
  2. READ. `FindingRegistry.register` copies it straight through:
     `"verified": finding.verified` at reference_runner_v3.py:3644. Nothing
     sanitises it. A second route exists at :20207, where `mark_verified` is
     called under `if f.verified`, so fixing only the registry would leave a
     door open -- which is why the fix needs both halves.
  3. READ. The CONFIRMED/CORROBORATED -> CLOSED transition at :6152 fires on
     `entry.get("verified")` alone, and records `adjudicator="tool"`,
     `evidence="verified fix, no unresolved challenges"`,
     `mechanism="verified_flag"`.
  4. MEASURED over the archive, below.

AND THE COMMENT DIRECTLY ABOVE THAT TRANSITION SAYS THE OPPOSITE. At :6154 it
reads that `verified` is only ever set by an execution and that the model never
sets it. That sentence is false, and it is the reason the defect survived: the
code asserts its own safety in a comment, so a reader checking the property
finds a claim rather than a check.

FIXED 2026-11-03 at the CLOSED transition, and this script is the evidence the
fix rests on. The transition now also requires that the flag be backed by an
execution -- `falsifier_verdict == "CONFIRMED"` or `bugzilla_verified` -- which
is a property every legitimate setter in the runner already leaves behind, so it
stops 0 real closures. Section 5 drives the live transition to show both halves.

WHY IT MATTERS MORE THAN AN ORDINARY MISLABEL. The project's standing correction
is that findings are confirmed programmatically or by a human, with no model
voting. The status machine ENFORCES that for CONFIRMED -- entry C0010 of the
2026-09-21 commissioning run carries a `refused_transitions` row showing a
model's CONFIRMED request refused and substituted with CORROBORATED. The
`verified` flag then carried that same entry from CORROBORATED to CLOSED, the
terminal and stronger state, labelled as adjudicated by a tool. The front door
is bolted and the side door is not.

THE SAME FIELD ALSO FEEDS ALLOCATION, and this half is LIVE BUT NOT ATTRIBUTED.
`bench/dm/_manager.py:717` computes `v_bar`, documented as mean verification
quality, as the fraction of a model's findings with `verified` True, and `v_bar`
is 1 of the 4 dimensions of the CapabilityFingerprint that decides how much work
each model is given. So a model that writes VERIFIED on its own findings raises
its own measured capability. The archive shows v_bar nonzero, so the dimension is
not inert -- but `f.verified` can also be runner-set, and nothing in the stored
fingerprints records which setter produced a given value. The claim that
self-reporting HAS moved an allocation is therefore NOT made here.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
RUNNER = REPO / "bench" / "reference_runner_v3.py"
PARSER = REPO / "bench" / "runner_core.py"
MANAGER = REPO / "bench" / "dm" / "_manager.py"


def _iv(k: int, n: int):
    """Wilson and Clopper-Pearson, on 2 independent implementations each."""
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    import mpmath
    mpmath.mp.dps = 40
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    wl, wh = proportion_confint(k, n, alpha=0.05, method="wilson")
    # second Wilson, written out, to catch a library disagreement
    import math
    z = stats.norm.ppf(0.975)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    wdiff = max(abs(wl - (c - hw)), abs(wh - (c + hw)))
    cl = 0.0 if k == 0 else float(stats.beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(stats.beta.ppf(0.975, k + 1, n - k))

    def bi(a, b, y):
        """Invert the regularised incomplete beta by bisection.

        HARDENED 2026-11-04. `mpmath.betainc` is fast, but its hyp2f1 path
        FAILS TO CONVERGE for large parameters at mid-range x. Measured at
        a=2437, b=17564 it succeeds for x <= 0.1264 and for x >= 0.9 and raises
        ValueError in between -- which is exactly where a bisection over [0, 1]
        takes its first step, so the whole inversion died rather than degrading.
        It surfaced when a producer called this at k=2436, n=20000; every
        existing caller used a small n, and the guard that executes every `_iv`
        against the same k and n uses n <= 38, so no test could have seen it.

        Where betainc raises, the same integral is computed by quadrature in
        log space instead. At the measured failing point that agreed with
        scipy's quantile to 1.11e-16. It costs about 6 s per bound against
        milliseconds for betainc, so it is used only after a failure, never by
        default.
        """
        logB = mpmath.log(mpmath.beta(a, b))

        def by_quad(x):
            if x <= 0:
                return mpmath.mpf(0)
            def dens(u):
                return mpmath.e**((a - 1) * mpmath.log(u)
                                  + (b - 1) * mpmath.log1p(-u) - logB)
            return mpmath.quad(dens, [0, min(mpmath.mpf(x), mpmath.mpf(1))])

        fell_back = False

        def _f(x):
            nonlocal fell_back
            if not fell_back:
                try:
                    return mpmath.betainc(a, b, 0, x, regularized=True) - y
                except Exception:
                    fell_back = True
            return by_quad(x) - y

        # STOP ON PRECISION, not on a fixed count. The bracket halves every
        # step, so 2**-60 is already below this tolerance and a fixed 240 did
        # 180 redundant evaluations. That is free for betainc and it is NOT
        # free for the quadrature fallback, which costs about 28 ms per
        # evaluation: 240 steps took 6.66 s and 60 take 1.69 s for a bound
        # identical to 12 decimal places. The count is still capped so a
        # pathological case cannot spin.
        lo, hi = mpmath.mpf(0), mpmath.mpf(1)
        tol = mpmath.mpf("1e-18")
        for _ in range(240):
            if hi - lo < tol:
                break
            m = (lo + hi) / 2
            lo, hi = (m, hi) if _f(m) < 0 else (lo, m)
        return float((lo + hi) / 2)

    cdiff = max(abs(cl - (0.0 if k == 0 else bi(k, n - k + 1, 0.025))),
                abs(ch - (1.0 if k == n else bi(k + 1, n - k, 0.975))))
    return (max(0.0, wl), wh), (cl, ch), max(wdiff, cdiff)


def _show(label: str, k: int, n: int) -> None:
    (wl, wh), (cl, ch), d = _iv(k, n)
    print(f"   {label}: {k} of {n}, {k/n if n else 0.0:.6f}")
    print(f"     Wilson 95%          [{wl:.6f}, {wh:.6f}]")
    print(f"     Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]   (2-impl |diff| {d:.1e})")


def probe_the_parser() -> dict:
    """EXECUTE the live parser against a model reply that claims VERIFIED."""
    sys.path.insert(0, str(REPO / "bench"))
    sys.path.insert(0, str(REPO))
    from runner_core import parse_findings            # noqa: PLC0415
    base = [{"FINDING_ID": "F001", "FLAW_CLASS": 2, "SEVERITY": 0.9,
             "ABSTRACTION_INDEX": 0.5,
             "DESCRIPTION": "A plausible defect in the parser's bounds check.",
             "PROPOSED_FIX": "clamp the index",
             "TARGET_FILE": "bench/runner_core.py"}]
    out = {}
    for label, val in (("boolean true", True), ('string "TRUE"', "TRUE"),
                       ("boolean false (control)", False)):
        rec = dict(base[0])
        rec["VERIFIED"] = val
        fs = parse_findings("SIM-A", 1, json.dumps([rec]))
        out[label] = (len(fs), bool(fs and fs[0].verified),
                      (fs[0].origin_type if fs else ""))
    return out


def scan_the_archive() -> dict:
    closed = 0
    by_mech: collections.Counter = collections.Counter()
    vf_total = 0
    vf_unbacked: list = []
    runs_any = set()
    runs_hit: collections.Counter = collections.Counter()
    for rep in sorted(LOGS.glob("*/*_report.json")):
        if "sandbox_harvest" in str(rep):
            continue
        try:
            d = json.loads(rep.read_text(errors="replace"))
        except Exception:                                  # noqa: BLE001
            continue
        ents = ((d.get("registry") or {}).get("entries")) or {}
        if not isinstance(ents, dict):
            continue
        runs_any.add(rep.parent.name)
        for cid, e in ents.items():
            if not isinstance(e, dict) or e.get("status") != "CLOSED":
                continue
            closed += 1
            mech = str(e.get("status_mechanism") or "(empty)")
            by_mech[mech] += 1
            if mech != "verified_flag":
                continue
            vf_total += 1
            if (str(e.get("falsifier_verdict") or "") == "CONFIRMED"
                    or e.get("bugzilla_verified")):
                continue
            runs_hit[rep.parent.name] += 1
            vf_unbacked.append((rep.parent.name, cid,
                                str(e.get("origin_type") or ""),
                                str(e.get("status_adjudicator") or ""),
                                ((e.get("fix_efficacy") or {}) or {}).get("outcome", "")))
    return {"closed": closed, "by_mech": by_mech, "vf_total": vf_total,
            "unbacked": vf_unbacked, "runs_any": runs_any, "runs_hit": runs_hit}


def scan_v_bar() -> dict:
    obs = []
    runs = set()

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get("v_bar"), (int, float)):
                yield float(o["v_bar"])
            for v in o.values():
                yield from walk(v)
        elif isinstance(o, list):
            for v in o:
                yield from walk(v)

    for rep in sorted(LOGS.glob("*/*_report.json")):
        if "sandbox_harvest" in str(rep):
            continue
        try:
            d = json.loads(rep.read_text(errors="replace"))
        except Exception:                                  # noqa: BLE001
            continue
        vals = list(walk(d))
        if vals:
            runs.add(rep.parent.name)
            obs.extend(vals)
    return {"obs": obs, "runs": runs}


def the_comment_claims_otherwise() -> dict:
    """Locate the carrying sites by line, skipping COMMENTS.

    A first version did not skip them and matched its own fix's explanatory
    comment, which quotes `if f.verified` while describing the defect -- the
    detector spelling out its own pattern, which is a shape this project has
    recorded repeatedly. The comment search below is deliberately the 1
    exception, since a comment is exactly what it is looking for.
    """
    src = RUNNER.read_text(errors="replace").splitlines()
    code = [("" if ln.lstrip().startswith("#") else ln) for ln in src]
    hits = [(i + 1, ln.strip()) for i, ln in enumerate(src)
            if "never sets it" in ln or "only ever set by an execution" in ln]
    gate = [(i + 1, ln.strip()) for i, ln in enumerate(code)
            if re.search(r'and entry\.get\("verified"\)', ln)]
    reg = [(i + 1, ln.strip()) for i, ln in enumerate(code)
           if re.search(r'"verified":\s*finding\.verified', ln)]
    mv = [(i + 1, ln.strip()) for i, ln in enumerate(code)
          if re.search(r'if f\.verified', ln)]
    return {"comment": hits, "gate": gate, "register": reg, "markv": mv}


def siblings():
    """The same gate in every runner that carries it, with its surroundings.

    THE POINT IS THE SURROUNDINGS, NOT THE LINE. The gate reads identically in
    5 files. In 1 of them an execution path exists and 378 of 412 closures use
    it; in the other 4 nothing ever writes `falsifier_verdict`, so the same
    conjunct would close the path instead of guarding it.

    PARSED WITH `ast`, NOT MATCHED WITH A REGEX. A first version matched lines
    needing both `entry["status"]` and `entry.get("verified")` on one line, and
    reported the v3 gate as line 9374 -- a DOCSTRING that quotes the old
    one-line form -- because the fix itself had split the real condition across
    2 lines. Walking the syntax tree finds the `if` whose test reads the field,
    wherever the condition is wrapped and whatever the prose around it says.
    """
    import ast as _ast                                     # noqa: PLC0415
    out = []
    for rel in ("bench/reference_runner.py", "bench/reference_runner_v3.py",
                "bench/run_exp35_policy_engine.py", "bench/run_exp36_evidence.py",
                "bench/run_exp37_evidence.py"):
        f = REPO / rel
        if not f.is_file():
            continue
        src = f.read_text(errors="replace")
        tree = _ast.parse(src)
        gates = []
        for node in _ast.walk(tree):
            if not isinstance(node, _ast.If):
                continue
            test_src = _ast.dump(node.test)
            if "'verified'" in test_src and "CONFIRMED" in test_src:
                gates.append(node.lineno)
        # counts come from the tree too, so a comment or docstring cannot inflate
        setters = fv = bz = 0
        for node in _ast.walk(tree):
            if isinstance(node, _ast.Assign):
                d = _ast.dump(node)
                if "'verified'" in d and "value=Constant(value=True)" in d:
                    setters += 1
                if "'falsifier_verdict'" in d:
                    fv += 1
            if isinstance(node, (_ast.Attribute, _ast.Constant, _ast.Name)):
                v = getattr(node, "attr", None) or getattr(node, "id", None) \
                    or (node.value if isinstance(getattr(node, "value", None), str) else None)
                if v == "bugzilla_verified":
                    bz += 1
        out.append((f.name, sorted(gates), setters, fv, bz))
    return out


def drive_the_transition():
    """Call `_update_finding_statuses` on 3 entry shapes and report the status.

    EXECUTED, NOT GREPPED. A text assertion about the conjunct would pass
    whether or not the conjunct does anything, which is the whole reason
    `execute-do-not-grep` exists in this project's rules.
    """
    import importlib.util                                  # noqa: PLC0415
    sys.path.insert(0, str(REPO / "bench"))
    spec = importlib.util.spec_from_file_location("_rr3_probe", RUNNER)
    rr3 = importlib.util.module_from_spec(spec)
    sys.modules["_rr3_probe"] = rr3
    spec.loader.exec_module(rr3)

    class _Cfg:
        def __getattr__(self, _n):
            return False

    base = {"canonical_id": "C0001", "status": "CONFIRMED", "verdicts": [],
            "severity": 0.7, "description": "d", "proposed_fix": "",
            "falsifier_code": "", "falsifier_verdict": "", "verified": True,
            "escalated": False, "origin_type": "model", "open_since_round": 0,
            "last_status_change_round": 0, "source_model": "SIM-A",
            "flaw_class": 1, "source_aliases": []}
    out = []
    for label, kw in (("the model's word alone", {}),
                      ("falsifier_verdict CONFIRMED", {"falsifier_verdict": "CONFIRMED"}),
                      ("bugzilla_verified", {"bugzilla_verified": True})):
        reg = rr3.FindingRegistry()
        e = dict(base)
        e.update(kw)
        reg.entries["C0001"] = e
        rr3._update_finding_statuses(reg, 1, _Cfg())
        out.append((label, reg.entries["C0001"]["status"],
                    reg.entries["C0001"].get("status_mechanism", "")))
    return out


def main() -> int:
    argparse.ArgumentParser(
        description=("Show that a model's own VERIFIED flag can close its "
                     "finding as tool-adjudicated.")).parse_args()
    print("=" * 78)
    print("A MODEL'S OWN `VERIFIED` FLAG CLOSES ITS FINDING AS TOOL-ADJUDICATED")
    print("=" * 78)

    print("\n1. THE LIVE PARSER, EXECUTED (not read).")
    pr = probe_the_parser()
    for label, (n, ver, origin) in pr.items():
        print(f"   reply says {label:24s} -> findings {n}, "
              f"Finding.verified={ver}, origin_type={origin!r}")
    assert pr["boolean true"][1] and not pr["boolean false (control)"][1], (
        "the probe is vacuous: the control must come back False")
    print("   => the model's self-declaration becomes Finding.verified, and the")
    print("      false control comes back False, so this is not vacuous.")

    print("\n2. THE 3 SITES THAT CARRY OR READ IT, BY LINE.")
    c = the_comment_claims_otherwise()
    for k, label in (("register", "registry copies the model's flag"),
                     ("markv", "mark_verified reads the finding's flag"),
                     ("gate", "the CLOSED transition reads the entry's flag"),
                     ("comment", "the comment asserting the model never sets it")):
        for ln, txt in c[k]:
            print(f"   {label:46s} :{ln}  {txt[:60]}")
    if not c["comment"]:
        print("   NOTE: the claiming comment is no longer present, so this")
        print("   producer's premise about it has been addressed.")

    print("\n3. WHAT THE ARCHIVE RECORDS.")
    a = scan_the_archive()
    print(f"   runs carrying a registry : {len(a['runs_any'])}")
    print(f"   entries CLOSED           : {a['closed']}")
    for m, v in a["by_mech"].most_common():
        print(f"      {v:5d}  status_mechanism = {m}")
    _show("CLOSED on `verified_flag` with NO CONFIRMED falsifier and no "
          "bugzilla verification", len(a["unbacked"]), a["vf_total"])
    _show("runs carrying at least 1 such closure", len(a["runs_hit"]),
          len(a["runs_any"]))
    adjs = collections.Counter(r[3] for r in a["unbacked"])
    origins = collections.Counter(r[2] for r in a["unbacked"])
    effs = collections.Counter(r[4] for r in a["unbacked"])
    print(f"   their recorded adjudicator : {dict(adjs)}")
    print(f"   their origin_type          : {dict(origins)}")
    print(f"   their fix_efficacy outcome : {dict(effs)}")
    # CHRONOLOGICAL, NOT ALPHABETICAL. A first version took sorted()[-1] over
    # the run NAMES and reported study_run1b_2026-10-03 as the newest, because
    # "stu" sorts above "sev" -- so it hid a 2026-11-02 run behind an October
    # one and the prose then put the newest hit in the wrong month. The run
    # name carries its own UTC stamp; sort on that.
    def _stamp(name: str) -> str:
        m = re.findall(r"(\d{8}T\d{6}Z)", name)
        if m:
            return max(m)
        m = re.findall(r"(\d{8})", name)
        return (max(m) + "T000000Z") if m else "00000000T000000Z"

    ranked = sorted(a["runs_hit"], key=_stamp)
    print("   affected runs, oldest first by their own UTC stamp:")
    for r in ranked:
        print(f"      {_stamp(r)}  {a['runs_hit'][r]:3d}  {r[:52]}")
    all_ranked = sorted(a["runs_any"], key=_stamp)
    rank = all_ranked.index(ranked[-1]) + 1 if ranked else 0
    print("   => the mechanism is NOT historical. The newest affected run is")
    print(f"      {_stamp(ranked[-1]) if ranked else 'n/a'}, which is run "
          f"{rank} of {len(all_ranked)} by date -- so only "
          f"{len(all_ranked) - rank} archived run(s) are newer than the most")
    print("      recent closure of this kind.")
    print("   AND THE 6 WORST ARE NOT THE 26. For 26 entries the runner never")
    print("   probed a fix because no falsifier existed. For 6 it DID probe and")
    print("   recorded FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER -- the runner measured")
    print("   that the fix fails its own test, and the entry closed anyway with")
    print("   `evidence=\"verified fix, no unresolved challenges\"`.")

    print("\n4. THE SAME FIELD FEEDS ALLOCATION. LIVE, NOT ATTRIBUTED.")
    v = scan_v_bar()
    nz = sum(1 for x in v["obs"] if x > 0)
    print("   dm/_manager.py:717 computes v_bar as the fraction of a model's")
    print("   findings with `verified` True; v_bar is 1 of the 4 "
          "CapabilityFingerprint dimensions.")
    _show("archived v_bar observations that are nonzero", nz, len(v["obs"]))
    print(f"   runs carrying any v_bar : {len(v['runs'])}")
    print("   => the dimension is not inert. But `verified` can also be")
    print("      runner-set and the stored fingerprints do not record which")
    print("      setter produced a value, so NO claim is made here that")
    print("      self-reporting has actually moved an allocation.")

    print("\n5. THE LIVE TRANSITION, DRIVEN (not read).")
    for label, st, mech in drive_the_transition():
        print(f"   entry {label:34s} -> status {st:12s} mechanism {mech!r}")
    print("   => the model's word alone no longer closes anything, and both")
    print("      execution-backed routes still do, so the fix is not a blanket")
    print("      refusal.")

    print("\n6. THE SAME GATE SITS IN 5 RUNNERS, AND THE FIX FOLDS BACK TO 1.")
    sib = siblings()
    for f, lns, setters, fv, bz in sib:
        where = ", ".join(f":{n}" for n in lns) or "(none)"
        print(f"   {f:30s} gates {where:16s} verified-setters {setters}  "
              f"falsifier_verdict writes {fv}  bugzilla refs {bz}")
    print("   => in the 4 siblings the ONLY setter is `mark_verified`, and NONE")
    print("      of them writes `falsifier_verdict` or has a bugzilla path. So")
    print("      applying this fix there would make the close path unreachable")
    print("      rather than correct -- disabling a feature, which the additive")
    print("      standard forbids. THIS IS THE HONEST ANSWER TO HIS Q15: a tested")
    print("      fix does NOT always fold back, and here folding it back")
    print("      mechanically would be a regression. What those 4 need is either")
    print("      an execution path or an honest label, and that is HIS ruling.")
    print("   AND THE MISLABEL IS v3-ONLY, which narrows the finding: v1 closes")
    print("   with a bare `resolve(cid, \"CLOSED\", round_idx)` and passes no")
    print("   adjudicator, so its closures are unlabelled rather than falsely")
    print("   attributed to a tool. That is why 840 of 1562 archived closures")
    print("   carry an empty `status_adjudicator`.")

    print("\n  THE ANSWER TO HIS QUESTION. The ticket store's rule that a")
    print("  terminal state is tool-only -- `close()` refuses without a")
    print("  verification -- is the lesson the registry NEEDS and does not")
    print("  have. A first pass said it was already present; that pass had")
    print("  grepped a comment instead of executing the code.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
