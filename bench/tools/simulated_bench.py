#!/usr/bin/env python3
"""A FULL simulated bench round: every repaired component, agents for the panel.

    PANEL LABELS ARE `SIM-A`..`SIM-E` AND MUST STAY THAT WAY. They are Claude
    subagents, not the named frontier models. Labelling them `Gemini`/`Codex`/etc
    on 2026-08-04 put two indistinguishable panels into the record — one real, one
    simulated — and results were reported as though vendors had produced them.
    That is a provenance failure, not a naming choice.

WHY THIS EXISTS, STATED HONESTLY
--------------------------------
Between 2026-08-01 and 04 the harness took a week of repairs — the routing
ladder's prompt, tri-state verification, S_k NO_SCORE on prose, the panel
briefing, the launch preflight, rejection reasons, sweep-on-halt, ruling 3's
computed evidence, the ouroboros query and reader, and a shadow novelty rule.
Two of those are proven end to end. The rest are UNIT-TESTED ONLY, and
unit-green-while-the-live-path-disagrees is this project's signature failure: the
2026-06-08 wiring bug, the launcher config-drop class six times over, and four
repairs to one function in a day.

An earlier version of this file registered findings and compared novelty rules,
and was described as a simulated bench. It was not. It never called the falsifier
gate, routing, run_verification, S_k, the rejection lines or either convergence
gate. This version calls all of them.

WHAT IT IS AND IS NOT
---------------------
IS:   the REAL pipeline functions, in the real order, on a real target, with the
      panel's output supplied by agents instead of paid models. It tests MECHANICS
      — does each stage receive what it expects, act correctly, and hand on.
IS NOT: an experiment. A simulated panel's findings differ in character from five
      frontier models under the full directive. Nothing here is an experimental
      result and none of it belongs in the paper.

TARGET: `bench/tests/fixtures/stem/docs/ALG-02-REF-01.md` — 149 lines, 7 claims,
ONE planted defect (AL-03), TWO executable fenced listings, which is the document
shape that halted the zero-plant control. Ground truth is exact, so the run scores
itself rather than being eyeballed.

    python3 bench/tools/simulated_bench.py --findings <agent_findings.json>
    python3 bench/tools/simulated_bench.py --scripted     # deterministic, no agents
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench/tests/fixtures/stem"))

STAGES: List[Dict[str, Any]] = []


def stage(name: str):
    """Every stage records what it did, so the report is evidence not narration."""
    def deco(fn):
        def wrapped(*a, **kw):
            rec = {"stage": name, "ok": False, "detail": "", "error": ""}
            try:
                rec["detail"] = fn(*a, **kw) or ""
                rec["ok"] = True
            except Exception as e:  # noqa: BLE001 — a broken stage is the finding
                rec["error"] = f"{type(e).__name__}: {e}"
                rec["trace"] = traceback.format_exc()[-800:]
            STAGES.append(rec)
            mark = "ok  " if rec["ok"] else "FAIL"
            print(f"  [{mark}] {name}: {rec['detail'] or rec['error']}", flush=True)
            return rec
        return wrapped
    return deco


def scripted_findings(fx, S) -> List[Dict[str, Any]]:
    """Deterministic stand-in when no agent findings are supplied. Deliberately
    includes: the real planted defect found twice in different words, a second
    genuinely different defect at the SAME listing (the novelty blind spot), a
    false positive on a TRUE claim, and one finding with NO falsifier (which must
    route rather than settle)."""
    return [
        dict(finding_id="F001", model_id="SIM-A", severity=0.85, round_idx=0,
             description=("VERDICT: CONFIRM. AL-03 overstates the comparison count: "
                          "`dedup` performs 2016 comparisons on 64 distinct inputs, "
                          "not the at-most-k the document claims. Listing A."),
             falsifier_code=fx.falsifier_template.replace(
                 S.DOC_PATH_TOKEN, str(S.DOC_DIR / fx.doc_name)),
             proposed_fix=""),
        dict(finding_id="F002", model_id="SIM-B", severity=0.82, round_idx=0,
             description=("AL-03: the linear-time claim for `dedup` fails. Membership "
                          "on a list is O(n), so Listing A is quadratic — 2016 "
                          "comparisons at n=64."),
             falsifier_code=fx.falsifier_template.replace(
                 S.DOC_PATH_TOKEN, str(S.DOC_DIR / fx.doc_name)),
             proposed_fix=""),
        dict(finding_id="F003", model_id="SIM-D", severity=0.88, round_idx=0,
             description=("Listing A's `dedup` conflates equal-but-distinct values: "
                          "`1`, `1.0` and `True` compare equal, so dedup([1, 1.0, True]) "
                          "returns a single element and silently drops two inputs."),
             falsifier_code="", proposed_fix=""),          # no falsifier -> must route
        dict(finding_id="F004", model_id="SIM-C", severity=0.75, round_idx=0,
             description="AL-01 appears unsupported: dedup preserves first-seen order.",
             falsifier_code="", proposed_fix=""),          # false positive
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--findings", type=str, default="")
    ap.add_argument("--scripted", action="store_true")
    args = ap.parse_args()

    import stem_fixtures as S
    from bench import reference_runner_v2 as R
    from bench.convergence_location import (
        hierarchical_novelty_series, novelty_rule_divergence)

    fx = S.ALGORITHMS
    doc = S.DOC_DIR / fx.doc_name
    text = doc.read_text(encoding="utf-8")
    planted = [c.tag for c in fx.claims if c.verdict != "TRUE"]

    print(f"\n  TARGET  {doc.name}  {len(text)} bytes, "
          f"{text.count('```')//2} listings, {len(fx.claims)} claims, "
          f"planted={planted}")

    cfg = R.RunnerConfig(
        test_article=str(doc), falsifier_gate_enabled=True, routing_enabled=True,
        sk_enabled=True, location_keyed_convergence=True,
        post_convergence_sweep_rounds=0, max_rounds=4, extension_cap=4,
    )

    # ── 1. target kind ────────────────────────────────────────────────────
    @stage("target_kind detection")
    def s_kind():
        k, why = R.resolve_target_kind(str(doc), text, declared=None)
        assert k == R.TARGET_KIND_PROSE, f"expected prose, got {k}"
        return f"{k} ({why})"
    s_kind()

    # ── 2. A9 launch preflight ────────────────────────────────────────────
    @stage("A9 launch preflight")
    def s_pre():
        r = R.preflight_target_machinery(cfg, str(doc), R.TARGET_KIND_PROSE)
        assert not r, f"refused: {r}"
        bad = R.preflight_target_machinery(
            R.RunnerConfig(test_article=str(doc), routing_enabled=False,
                           falsifier_gate_enabled=True),
            str(doc), R.TARGET_KIND_PROSE)
        assert bad, "preflight failed to refuse a prose run with routing off"
        return f"passes for this config; refuses routing-off ({len(bad)} reason)"
    s_pre()

    # ── 3. S_k must abstain on prose ──────────────────────────────────────
    @stage("S_k NO_SCORE on prose")
    def s_sk():
        res = R.compute_sk("<<<<<<< SEARCH\nfoo\n=======\nbar\n>>>>>>> REPLACE",
                           text, str(doc))
        assert res.tristate == R.SK_NO_SCORE, f"got {res.tristate}"
        return f"tristate={res.tristate}, sk={res.sk}"
    s_sk()

    # ── 4. tri-state verification: a clean parse may not close ────────────
    @stage("tri-state verification (veto, not pass)")
    def s_ver():
        import tempfile, shutil
        tmp = Path(tempfile.mkdtemp()) / doc.name
        shutil.copy(doc, tmp)
        from bench.bugzilla_loop import run_verification, VerificationOutcome
        v = run_verification(tmp, None, baseline_path=doc)
        assert v.outcome is not VerificationOutcome.PASS, "clean parse returned PASS"
        assert v.vetoes_run, "veto not recorded"
        return f"outcome={v.outcome.name}, vetoes_run={v.vetoes_run[0][:40]}"
    s_ver()

    # ── 5. registry + panel briefing ──────────────────────────────────────
    reg = R.FindingRegistry()
    reg.target_kind = R.TARGET_KIND_PROSE

    if args.findings:
        rows = json.loads(Path(args.findings).read_text())
        claimed = sum(1 for r in rows if r.get("_ran"))
        print(f"  PANEL   {len(rows)} findings from "
              f"{len({r['model_id'] for r in rows})} agents; "
              f"{claimed} claim their falsifier RAN")
    else:
        rows = scripted_findings(fx, S)

    @stage("panel briefing branches on target kind")
    def s_brief():
        for r in rows:
            reg.register(R.Finding(
                finding_id=r["finding_id"], model_id=r["model_id"],
                round_idx=r.get("round_idx", 0), flaw_class=r.get("flaw_class", 3),
                severity=r["severity"], abstraction_index=0.5,
                description=r["description"], proposed_fix=r.get("proposed_fix", ""),
                falsifier_code=r.get("falsifier_code", ""), target_file=str(doc),
            ), r["model_id"])
        b = reg.build_summary(1)
        assert "runs ruff + mypy + bandit" not in b, "prose run promised linters"
        assert "RUNNABLE FALSIFIER" in b, "prose briefing does not name the route"
        return f"{len(reg.entries)} findings registered; prose briefing correct"
    s_brief()

    # ── 6. falsifier gate — the real settlement path ──────────────────────
    @stage("falsifier gate (CONFIRM-only)")
    def s_gate():
        R.apply_falsifier_verdicts(reg, 0, cfg, str(REPO))
        v = {c: e.get("falsifier_verdict") for c, e in reg.entries.items()}
        esc = sum(1 for e in reg.entries.values() if e.get("escalated"))
        return f"verdicts={v}, escalated={esc}"
    s_gate()

    # ── 7. A10 rejection reasons reach the panel ──────────────────────────
    @stage("A10 rejection reasons rendered")
    def s_a10():
        lines = [l for e in reg.entries.values() for l in R._rejection_lines(e)]
        assert lines, "no rejection reasons rendered for any finding"
        b = reg.build_summary(1)
        assert any(t in b for t in ("FALSIFIER ERROR", "NO FALSIFIER",
                                    "FIX REJECTED", "NOT SCORED")), \
            "reasons exist on entries but do not reach the round prompt"
        return f"{len(lines)} line(s); e.g. {lines[0][:70]}"
    s_a10()

    # ── 8. novelty: both series + where they disagree ─────────────────────
    @stage("novelty series (location + hierarchical shadow)")
    def s_nov():
        from bench.convergence_location import target_symbols
        syms = target_symbols(text) or []
        loc = R._location_keyed_critical_series(reg, 1, syms)
        hier = hierarchical_novelty_series(reg.entries, 1, syms)
        div = novelty_rule_divergence(reg.entries, syms)
        return (f"symbols={len(syms)} location={loc} hierarchical={hier} "
                f"blind-spot candidates={div['n_split']}")
    s_nov()

    # ── 9. convergence gate ───────────────────────────────────────────────
    @stage("two-sided gate evaluation")
    def s_gate2():
        conv, why = R._check_gamma_alt_convergence(
            3, 0.9, [2, 0, 0, 0], cfg,
            unresolved_critical=reg.unverified_critical_count(),
            irreducible_queue=reg.irreducible_queue_count(), gamma_critical=1.0)
        return f"converged={conv} :: {why[:90]}"
    s_gate2()

    # ── 10. score against ground truth ────────────────────────────────────
    @stage("scored against fixture ground truth")
    def s_score():
        true_tags = [c.tag for c in fx.claims if c.verdict == "TRUE"]
        conf = [e for e in reg.entries.values()
                if e.get("falsifier_verdict") == "CONFIRMED"]
        hit = [e for e in conf if any(t in e["description"] for t in planted)]
        fp = [e for e in conf if any(t in e["description"] for t in true_tags)
              and not any(t in e["description"] for t in planted)]
        other = len(conf) - len(hit) - len(fp)
        return (f"registered={len(reg.entries)} CONFIRMED={len(conf)} | "
                f"planted defect DETECTED={bool(hit)} ({len(hit)} demonstration(s)) "
                f"| FALSE POSITIVES CONFIRMED={len(fp)} | unclassified={other}")
    s_score()

    @stage("residue: what reached the human, and why")
    def s_res():
        from collections import Counter
        unsettled = [e for e in reg.entries.values()
                     if e.get("falsifier_verdict") != "CONFIRMED"]
        why = Counter(e.get("falsifier_verdict") or "none" for e in unsettled)
        esc = sum(1 for e in reg.entries.values() if e.get("escalated"))
        return f"unsettled={len(unsettled)} {dict(why)}; escalated={esc}"
    s_res()

    # ── THE 2026-08-29/30 REPAIRS, EXERCISED HERE RATHER THAN TRUSTED ────────
    # Founder, 2026-08-30: "BR2 is not strictly just a test. It is the entire
    # machinery of the schema turned against a large number of meaningful
    # external targets for the first time. It is not a good place to find out
    # something we built doesn't work as intended." So every repair from that
    # window gets a stage here first.

    @stage("rho is CONTRIBUTORY, not a veto (founder ruling 2026-08-29)")
    def s_rho():
        from reference_runner_v2 import _check_gamma_alt_convergence
        kw = dict(cfg=cfg, novel_critical_history=[3, 0, 0, 0, 0, 0, 0],
                  unresolved_critical=0, contested=0)
        with_churn, why = _check_gamma_alt_convergence(6, 0.20, rho_churn=True, **kw)
        without, _ = _check_gamma_alt_convergence(6, 0.20, rho_churn=False, **kw)
        if with_churn != without:
            raise AssertionError("churn changed the verdict; it is still a veto")
        if "churn" not in why.lower():
            raise AssertionError("churn stopped being REPORTED as well as blocking")
        # and it must not be able to MANUFACTURE a convergence
        still, _ = _check_gamma_alt_convergence(
            6, 0.20, rho_churn=True, cfg=cfg,
            novel_critical_history=[3, 2, 1, 2, 1, 1, 2],
            unresolved_critical=0, contested=0)
        if still:
            raise AssertionError("a run still producing criticals converged")
        return (f"verdict identical with/without churn ({with_churn}); churn still named; "
                f"cannot manufacture a convergence")

    @stage("the fix applier refuses a patch that would break the target")
    def s_apply():
        from endocrine import _apply_fix_to_source
        src = 'def f():\n    """doc."""\n    x = 1\n'
        bad = ('<<<< SEARCH def f():\n"""doc."""\n    x = 1\n==== REPLACE\n'
               'def f():\n    """doc."""\n    x = 2\n>>>>')
        good = "<<<< SEARCH\n    x = 1\n==== REPLACE\n    x = 2\n>>>>"
        if _apply_fix_to_source(src, bad) is not None:
            raise AssertionError("a corrupting patch was applied and returned")
        if "x = 2" not in (_apply_fix_to_source(src, good) or ""):
            raise AssertionError("a sound patch was refused")
        return "corrupting patch refused; sound patch applied (12 of 313 archived fixes were corrupted this way)"

    @stage("the discrimination overlay leaks no git history")
    def s_overlay():
        import shutil as _sh, subprocess as _sp
        from reference_runner_v2 import _build_discrimination_overlay
        ov = _build_discrimination_overlay(REPO, "bench/evidence.py", "# MUTATED\n")
        try:
            if (ov / ".git").exists():
                raise AssertionError(".git is reachable from the overlay")
            r = _sp.run(["git", "-C", str(ov), "log", "--oneline", "-1"],
                        capture_output=True, text=True)
            if r.returncode == 0:
                raise AssertionError("git resolves a repository inside the overlay: "
                                     "the plant is recoverable at precision 1.0")
            leaf = ov / "bench" / "evidence.py"
            if leaf.is_symlink() or leaf.read_text() != "# MUTATED\n":
                raise AssertionError("the substituted leaf did not take")
        finally:
            _sh.rmtree(ov, ignore_errors=True)
        return "no .git; git log rc!=0; mirror intact; substituted leaf is a real file"

    @stage("fix-efficacy probe: runs, and is structurally unable to gate")
    def s_fe():
        import ast as _ast
        from fix_efficacy import probe as _probe, FIX_CURES, FIX_INEFFECTIVE
        src = (REPO / "bench" / "reference_runner_v2.py").read_text()
        tree = _ast.parse(src)
        for g in ("_evaluate_gate_conditions", "_check_gamma_alt_convergence"):
            fn = next(n for n in _ast.walk(tree)
                      if isinstance(n, _ast.FunctionDef) and n.name == g)
            if "fix_efficacy" in _ast.unparse(fn):
                raise AssertionError(f"{g} references the probe; it could gate")
        upd = next(n for n in _ast.walk(tree)
                   if isinstance(n, _ast.FunctionDef) and n.name == "_update_finding_statuses")
        if "fix_efficacy" not in _ast.unparse(upd):
            raise AssertionError("the probe is not actually wired into the status pass")
        return "wired into the status pass; absent from BOTH gate functions"

    @stage("EXTEND is READ (founder ruling, 21 Aug — it was read by nothing)")
    def s_extend():
        import ast as _a
        src = (REPO / "bench" / "reference_runner_v2.py").read_text()
        kinds = ("CONFIRM", "CHALLENGE", "EXTEND", "MERGE", "REOPEN")
        unread = [k for k in kinds if src.count(f'== "{k}"') == 0]
        if unread:
            raise AssertionError(f"verdict types offered to models and read by nothing: {unread}")
        t = _a.parse(src)
        upd = _a.unparse(next(n for n in _a.walk(t) if isinstance(n, _a.FunctionDef)
                              and n.name == "_update_finding_statuses")).replace('"', "'")
        if "v['verdict'] == 'EXTEND'" not in upd or "'extensions'" not in upd:
            raise AssertionError("extensions are not collected onto the parent")
        for g in ("_evaluate_gate_conditions", "_check_gamma_alt_convergence"):
            b = _a.unparse(next(n for n in _a.walk(t) if isinstance(n, _a.FunctionDef)
                                and n.name == g)).lower()
            if "extension" in b:
                raise AssertionError(f"{g} references extensions; they could gate")
        return ("all 5 verdict types consumed; extensions recorded on the parent and "
                "absent from both gates (209 archived EXTENDs were invisible)")

    for _s in (s_rho, s_apply, s_overlay, s_fe, s_extend):
        _s()

    if args.findings:
        @stage("agent claim vs runner verdict (honesty check)")
        def s_hon():
            byid = {r["finding_id"]: r for r in rows}
            bad = []
            for e in reg.entries.values():
                src = next((byid[a] for a in e.get("source_aliases", [])
                            if a in byid), None)
                if src and src.get("_ran") and e.get("falsifier_verdict") != "CONFIRMED":
                    bad.append((e.get("canonical_id"), e.get("falsifier_verdict")))
            return (f"{len(bad)} finding(s) the agent said RAN but the runner could "
                    f"not confirm: {bad[:5]}")
        s_hon()

    ok = sum(1 for s in STAGES if s["ok"])
    print(f"\n  STAGES: {ok}/{len(STAGES)} passed")
    for s in STAGES:
        if not s["ok"]:
            print(f"    FAILED {s['stage']}: {s['error']}")
    out = REPO / "bench/logs/simulated_bench_last.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(STAGES, indent=2))
    print(f"  detail -> {out}")
    return 0 if ok == len(STAGES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
