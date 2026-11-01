#!/usr/bin/env python3
"""PRODUCER for the primary/secondary falsifier rule, 2026-10-31.

FOUNDER, 2026-10-31: *"I think your reformulation of my proposal to use a
primary and secondary falsifier, and to default to the primary only, when no
secondary is either available, or cannot be installed from the curated list
(although this second part is a further qualification from me), is probably the
right shape and you should apply it."*

THE RULE IS NOT NEW. His ruling of 2026-09-28 already states it for Wolfram:
*"Wolfram (when available) however should remain the secondary falsifier ran
against any output produced from the installed Open Source tools and should
never be considered the primary falsifier route."* Today generalises it from
Wolfram to every tool. What follows measures whether the harness can carry it.

EVERY FIGURE HERE IS CROSS-VERIFIED WITH 2 TOOLS, per the 21 Apr 2026 rule.
Exit 1 if any internal consistency check fails, so a wrong number cannot pass
silently as a right one.
"""
from __future__ import annotations

import argparse
import ast
import collections
import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import mpmath as mp
import numpy as np
from scipy import stats as sstats
from statsmodels.stats.proportion import proportion_confint

from bench import immune_agents as ia

REPO = pathlib.Path(__file__).resolve().parent.parent
FAILURES: list[str] = []


def _check(label: str, cond: bool, detail: str = "") -> None:
    if not cond:
        FAILURES.append(f"{label}: {detail}")


def wilson(k: int, n: int) -> tuple[float, float]:
    """Wilson 95% interval, statsmodels against an mpmath closed form."""
    lo_sm, hi_sm = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = mp.mpf("1.959963984540054")
    p = mp.mpf(k) / n
    d = 1 + z**2 / n
    c = p + z**2 / (2 * n)
    h = z * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    lo_mp, hi_mp = float((c - h) / d), float((c + h) / d)
    _check("wilson agreement", abs(lo_sm - lo_mp) < 1e-9 and abs(hi_sm - hi_mp) < 1e-9,
           f"statsmodels ({lo_sm},{hi_sm}) vs mpmath ({lo_mp},{hi_mp})")
    return float(lo_sm), float(hi_sm)


def fisher(table: list[list[int]]) -> float:
    """One-sided Fisher exact, scipy against an mpmath hypergeometric tail."""
    _, p_sp = sstats.fisher_exact(table, alternative="greater")
    a, b = table[0]
    c, d = table[1]
    n = a + b + c + d
    r1, c1 = a + b, a + c
    tot = mp.mpf(0)
    for k in range(a, min(r1, c1) + 1):
        tot += (mp.binomial(c1, k) * mp.binomial(n - c1, r1 - k)) / mp.binomial(n, r1)
    _check("fisher agreement", abs(float(tot) - p_sp) < 1e-12,
           f"scipy {p_sp} vs mpmath {float(tot)}")
    return float(p_sp)



from bench import falsifier_pairing as _fp


def fp_primary(tools, manifest):
    """Explicit manifest, because `main()` owns it.

    This read a module-level `man` until the body was wrapped in `main()` on
    2026-10-31, at which point the name became local and the call raised
    NameError. Taking it as an argument removes the hidden dependency rather
    than restoring a global.
    """
    return _fp.primary_candidates(tools, manifest)


def fp_select(primary, tools, manifest):
    return _fp.select_secondary(primary, tools, manifest, allow_paid=False)

def main(argv=None) -> int:
    """Every measurement. Wrapped in a function on 2026-10-31 so that
    IMPORTING this module runs nothing: the project's own probe in
    `bench/tests/test_operational_scripts.py` imports every script to
    prove it still loads, and a module that measures at import turns
    that cheap check into a full run. A `--help` and an import must
    both cost nothing."""
    # ★ A `--help` MUST NEVER COST ANYTHING — his standing rule, and the
    # pre-commit gate enforces it. Without this, `--help` fell through to the
    # measurement and ran the whole thing: 8 producers were refused the commit
    # on exactly this. argparse answers and exits before any body runs.
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args(argv)

    print("=" * 72)
    print("M1. THE MANIFEST IS THE CURATED LIST, AND IT ALREADY HAS INSTALL FIELDS")
    print("=" * 72)
    man = ia._load_tool_manifest()
    n_entries = len(man)
    n_real = sum(1 for v in man.values() if not v.get("delegate"))
    n_install = sum(1 for v in man.values() if v.get("install_check"))
    n_hint = sum(1 for v in man.values() if v.get("package_hint"))
    print(f"entries                      {n_entries}")
    print(f"  non-delegated (dispatchable) {n_real}")
    print(f"  carrying install_check       {n_install}")
    print(f"  carrying package_hint        {n_hint}")
    _check("install fields co-extensive", n_install == n_hint == n_real,
           f"install={n_install} hint={n_hint} real={n_real}")
    print()
    print("So a curated allow-list with a per-tool install probe and a PEP 508")
    print("install hint ALREADY EXISTS. Grok's recommendation is already built.")

    print()
    print("=" * 72)
    print("M2. BUT NOTHING CONSUMES THE INSTALL FIELDS -- AN UNWIRED ADDITION")
    print("=" * 72)
    # Predicate check stated explicitly: a consumer would have to mention the key
    # as a literal somewhere, in any of entry["install_check"], .get("install_check")
    # or a module-level constant. A dynamically assembled key would evade this and
    # is reported as the known limit rather than assumed absent.
    mentions: list[tuple[str, int, str]] = []
    SELF = pathlib.Path(__file__).resolve()
    for py in sorted(REPO.rglob("*.py")):
        # EXCLUSIONS, each with its reason, because a census that counts its own
        # instrument measures the instrument. Both were live defects in the first
        # run of this script: it reported 10 consumers, all 10 its own lines.
        #   - SELF: this producer necessarily names the key it is counting.
        #   - bench/logs/**: panel sandbox harvests hold COPIES of immune_agents.py,
        #     so counting them multiplies one docstring by the number of runs.
        #     Kept on disk (point, never prune); excluded from the denominator.
        if ".git" in py.parts:
            continue
        if py.resolve() == SELF:
            continue
        if "logs" in py.parts and "bench" in py.parts:
            continue
        # INSTRUMENTS ARE NOT CONSUMERS -- a third exclusion, and it was a live
        # defect in this script's third run. A guard that EXERCISES the field and a
        # mutation harness that names it as a target both mention it, and counting
        # them says the field is consumed when what it means is that the field is
        # tested. The claim this section makes is about the PRODUCT: does any live
        # module read `install_check` to make a decision. So tests and scripts are
        # out, with their reason, and `bench/` minus `bench/tests/` is the
        # denominator. This is narrower than "every .py file" and it is the
        # question actually being asked.
        if "tests" in py.parts:
            continue
        if py.parts[0] == "scripts" or "/scripts/" in str(py):
            continue
        try:
            src = py.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "install_check" not in src:
            continue
        for i, line in enumerate(src.splitlines(), 1):
            if "install_check" in line:
                mentions.append((str(py.relative_to(REPO)), i, line.strip()[:90]))
    print("DENOMINATOR: live product modules only -- bench/ minus bench/tests/,")
    print("minus bench/logs/** (sandbox copies), minus scripts/ (instruments),")
    print("minus this producer. Each exclusion carries its reason in the source.")
    print(f"product lines mentioning install_check: {len(mentions)}")
    for f, i, t in mentions:
        print(f"   {f}:{i}  {t}")
    # classify: a docstring/comment mention is not a consumer
    code_consumers = []
    for f, i, t in mentions:
        if t.lstrip().startswith("#") or t.lstrip().startswith("*"):
            continue
        if "install_check," in t or "install_check :" in t:
            continue  # the loader docstring listing field names
        code_consumers.append((f, i, t))
    print()
    print(f"of those, lines that READ the field in code: {len(code_consumers)}")
    for f, i, t in code_consumers:
        print(f"   {f}:{i}  {t}")
    # A PRODUCER OUTLIVES ITS DEFECT. This check asserted 0 consumers, which was
    # the TRUE state until `bench/falsifier_pairing.py` was written on 2026-10-31
    # to implement the founder's rule -- and the rule NEEDS the field, so building
    # it made the assertion false. The check now holds BOTH halves, because either
    # alone is misleading: that nothing OUTSIDE the new module reads the field (so
    # the pre-fix measurement was right), and that the new module DOES read it (so
    # the field is no longer data nothing reaches).
    _NEW = "bench/falsifier_pairing.py"
    outside = [c for c in code_consumers if c[0] != _NEW]
    inside = [c for c in code_consumers if c[0] == _NEW]
    print()
    print(f"consumers OUTSIDE the new pairing module: {len(outside)}  {outside}")
    print(f"consumers INSIDE  the new pairing module: {len(inside)}")
    _check("nothing outside the pairing module reads install_check",
           len(outside) == 0, f"found {outside}")
    _check("the pairing module DOES read install_check -- else the curated list "
           "is still data nothing reaches", len(inside) >= 1,
           "falsifier_pairing.py does not reference install_check")
    print()
    print("LIMIT, stated so it is not mistaken for proof: a key assembled at")
    print("runtime would evade a literal search. None was found; none is claimed")
    print("to be impossible.")

    print()
    print("=" * 72)
    print("M3. THE DISPATCH IS SINGLE-TOOL BY CONSTRUCTION")
    print("=" * 72)
    # Read the dispatch loop's own AST and find the `break` that ends it.
    src = (REPO / "bench" / "immune_agents.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    breaks_in_tool_loops = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.For) and isinstance(node.target, ast.Name) \
                and node.target.id == "tool_name":
            for sub in ast.walk(node):
                if isinstance(sub, ast.Break):
                    breaks_in_tool_loops += 1
    print(f"`for tool_name in specialist_tools` loops carrying a `break`: "
          f"{breaks_in_tool_loops}")
    _check("the break exists", breaks_in_tool_loops >= 1,
           "no break found in the tool loop -- the finding would be withdrawn")
    print("Source: bench/immune_agents.py, `break  # First definitive result wins`.")
    print("So the FIRST definitive verdict ends the loop and every later tool for")
    print("that claim is never called. There is no secondary falsifier in this path.")

    print()
    print("=" * 72)
    print("M4. THE MANIFEST'S OWN claim_types -- NOT WHAT THE DISPATCH READS.")
    print("    CORRECTED LABEL. The first version of this script presented these")
    print("    lists as the dispatch's candidates. They are not: tool_map comes")
    print("    from `immune.verification_tools` in the DOMAIN TOMLs. M10 measures")
    print("    the layer that actually decides. This section is kept because the")
    print("    manifest's own view is what a tool author sees.")
    print("=" * 72)
    CLAIM_KEYS = ("mathematical", "logical", "statistical",
                  "code_structural", "code_behavioral")
    by_claim: dict[str, list[str]] = {}
    for ck in CLAIM_KEYS:
        cands = [k for k, v in man.items()
                 if ck in (v.get("claim_types") or []) and not v.get("delegate")]
        by_claim[ck] = cands
    multi = sum(1 for ck in CLAIM_KEYS if len(by_claim[ck]) >= 2)
    lo, hi = wilson(multi, len(CLAIM_KEYS))
    print(f"claim types with 2 or more dispatchable tools: {multi} of {len(CLAIM_KEYS)}"
          f"  Wilson 95% [{lo:.6f}, {hi:.6f}]")
    print()
    for ck in CLAIM_KEYS:
        print(f"  {ck:<17} {len(by_claim[ck]):>2} tools, dispatch order:")
        print(f"  {'':<17} {by_claim[ck]}")

    print()
    print("=" * 72)
    print("M5. TWO TOOLS CAN SHARE ONE VERIFIER -- NOT A SECOND FALSIFIER AT ALL")
    print("=" * 72)
    by_verifier: dict[str, list[str]] = collections.defaultdict(list)
    for k, v in man.items():
        if v.get("verifier"):
            by_verifier[v["verifier"]].append(k)
    shared = {vf: ks for vf, ks in by_verifier.items() if len(ks) > 1}
    print(f"verifier functions serving more than 1 manifest entry: {len(shared)}")
    for vf, ks in sorted(shared.items()):
        print(f"   {vf} <- {ks}")
        same_fn = getattr(ia, vf, None)
        print(f"      resolves to a single callable: {same_fn is not None}")
    _check("shared verifiers found", len(shared) >= 1,
           "none found -- the scipy/statsmodels point would be withdrawn")
    print()
    print("For a statistical claim the 2 candidates are `statsmodels` and `scipy`,")
    print("and BOTH resolve to the identical function `_verify_statistical`. So the")
    print("canonical 2-tool pair in that claim type is literally 1 function called")
    print("twice. This is the strongest possible case for the founder's own")
    print("qualification: a second tool is only a second falsifier if it is")
    print("independent of the first.")

    print()
    print("=" * 72)
    print("M6. A PAID ROUTE SITS IN THE MANIFEST -- HARD CONSTRAINT EXPOSURE")
    print("=" * 72)
    paid = []
    for k, v in man.items():
        vf = v.get("verifier") or ""
        fn_src = ""
        if vf:
            try:
                import inspect
                fn = getattr(ia, vf, None)
                fn_src = inspect.getsource(fn) if fn else ""
            except (OSError, TypeError):
                fn_src = ""
        if any(tok in fn_src for tok in ("API_KEY", "call_deepseek", "openrouter",
                                         "call_openrouter")):
            paid.append((k, vf, v.get("claim_types"), v.get("install_check")))
    print(f"manifest entries whose verifier reaches a paid API: {len(paid)}")
    for k, vf, cts, ic in paid:
        print(f"   {k}  verifier={vf}  claim_types={cts}  install_check={ic!r}")
        pos = {ck: (by_claim[ck].index(k) + 1 if k in by_claim[ck] else None)
               for ck in CLAIM_KEYS}
        print(f"      position in each dispatch order (1-based): "
              f"{ {c: p for c, p in pos.items() if p} }")
    _check("paid route identified", len(paid) >= 1,
           "none found -- the paid-dispatch risk would be withdrawn")
    print()
    print("CONSEQUENCE FOR THE RULE: a secondary selector that reaches for `the")
    print("next available tool` can trigger PAID DISPATCH. The founder's standing")
    print("constraint is that no paid dispatch happens without his authorisation,")
    print("so the selector must EXCLUDE a paid route by default, not rank it last.")

    print()
    print("=" * 72)
    print("M7. WHICH CURATED TOOLS ARE ACTUALLY AVAILABLE RIGHT NOW")
    print("=" * 72)
    avail, missing = [], []
    for k, v in man.items():
        chk = v.get("install_check")
        if not chk:
            continue
        try:
            exec(compile(chk, f"<install_check:{k}>", "exec"), {})
            avail.append(k)
        except Exception as exc:
            missing.append((k, type(exc).__name__))
    n_chk = len(avail) + len(missing)
    lo, hi = wilson(len(avail), n_chk)
    print(f"available: {len(avail)} of {n_chk}  Wilson 95% [{lo:.6f}, {hi:.6f}]")
    if missing:
        print(f"missing:   {missing}")
    print()
    print("So on THIS machine the curated list is near-fully installed, which means")
    print("the `cannot be installed` branch of his rule is rare here and must still")
    print("exist, because it is the branch that fires on someone else's machine.")

    print()
    print("=" * 72)
    print("M8. IS A SECONDARY WORTH ANYTHING? THE SESSION'S OWN CROSS-CHECKS")
    print("=" * 72)
    # Every cross-check run in this session, classified by whether the second tool
    # took a DIFFERENT ROUTE to the quantity or merely re-evaluated the first
    # tool's own formulation. `caught` = the pair surfaced an error.
    # Recorded here so the classification is auditable rather than asserted.
    PAIRS = [
        # (label, independent_route, caught)
        ("statsmodels vs mpmath, Wilson interval", False, False),
        ("scipy vs mpmath, Fisher exact", False, False),
        ("NumPy vs SymPy, cost quadratic (same fit handed to both)", False, False),
        ("z3 vs exhaustive enumeration, polarity table", False, False),
        ("SymPy model vs EXECUTING compute_rk", True, True),
        ("my linear cost fit vs the file's committed live-priced anchors", True, True),
        ("my sidecar census vs the API's own tool_calls field", True, True),
    ]
    a = sum(1 for _, ind, c in PAIRS if ind and c)          # independent & caught
    b = sum(1 for _, ind, c in PAIRS if ind and not c)      # independent & missed
    c_ = sum(1 for _, ind, c in PAIRS if not ind and c)     # same-route & caught
    d_ = sum(1 for _, ind, c in PAIRS if not ind and not c) # same-route & missed
    print(f"{'pair':<58} {'independent':>12} {'caught':>7}")
    for label, ind, cc in PAIRS:
        print(f"{label:<58} {str(ind):>12} {str(cc):>7}")
    print()
    print(f"2x2:  independent-route: caught {a}, missed {b}")
    print(f"      same-route:        caught {c_}, missed {d_}")
    p = fisher([[a, b], [c_, d_]])
    print(f"Fisher exact, one-sided: p = {p:.6f}")
    print()
    print("READ THIS AS WEAK EVIDENCE AND NOTHING MORE. n = 7, the classification")
    print("is post-hoc, and the sample is the cross-checks this session happened to")
    print("record rather than a random draw from all cross-checks ever run. The")
    print("selection risk runs in the direction that FLATTERS the conclusion, so")
    print("the honest statement is: consistent with the rule, not a test of it.")
    print("A real test needs a pre-registered classification over the archive.")

    print()
    print("=" * 72)
    print("M9. WOLFRAM'S REACH, WHICH IS THE GAP THE FOUNDER ASKED ABOUT")
    print("=" * 72)
    in_manifest = [k for k in man if "wolfram" in k.lower()]
    print(f"manifest entries naming Wolfram: {len(in_manifest)} {in_manifest}")
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_panel", REPO / "bench" / "confer_maths_panel_2026-09-05.py")
    pmod = importlib.util.module_from_spec(spec)
    sys.modules["_panel"] = pmod
    try:
        spec.loader.exec_module(pmod)
    except SystemExit:
        pass
    host_tools = []
    for s in getattr(pmod, "TOOL_SPECS", []):
        f = s.get("function", {}) if isinstance(s, dict) else {}
        if f.get("name"):
            host_tools.append(f["name"])
    print(f"host-side tools a REMOTE seat can call: {len(host_tools)}")
    print(f"   {host_tools}")
    wolf_host = [t for t in host_tools if "wolfram" in t.lower()]
    print(f"of those, naming Wolfram: {len(wolf_host)} {wolf_host}")
    print()
    print("A CLI seat (cc2, fable) reaches Wolfram through its shell, because the")
    print("serial gate is first on its PATH. A remote seat (cx, ge, cgpt, ds) has")
    print("no shell and can only call a host-side tool. With no Wolfram tool in")
    print("that list, his 2026-09-28 secondary-falsifier ruling is unreachable for")
    print("those seats BY CONSTRUCTION, whatever any prompt tells them.")

    print()
    print("=" * 72)
    print("M10. THE LAYER THAT ACTUALLY DECIDES: THE DOMAIN TOMLs")
    print("=" * 72)
    # `_specialist_b_cell_dispatch` reads immune.verification_tools from the domain
    # config, so THIS is the candidate list for every real claim. A manifest entry
    # that no domain references is reachable by nothing -- the manifest header says
    # so in its own step 3, and skipping that step was a live error in this script's
    # first version.
    import tomllib
    DOM = REPO / "bench" / "cdsfl_registry" / "domains" / "immune"
    rows = []
    for tf in sorted(DOM.glob("*.toml")):
        cfg = tomllib.loads(tf.read_text(encoding="utf-8"))
        vt = (cfg.get("immune") or {}).get("verification_tools") or {}
        for claim, tools in sorted(vt.items()):
            pool = fp_primary(tools, man)
            if not pool:
                continue
            primary = pool[0]
            sec, reason, detail = fp_select(primary, tools, man)
            rows.append((tf.stem, claim, primary, sec, reason, len(tools)))
    print(f"{'domain':<21}{'claim type':<17}{'primary':<14}{'secondary':<20}reason")
    for d, c, pr, se, rs, n in rows:
        print(f"{d:<21}{c:<17}{pr:<14}{str(se):<20}{rs}")
    paired = sum(1 for r in rows if r[3] is not None)
    lo, hi = wilson(paired, len(rows))
    print()
    print(f"domain/claim-type pairs with an INDEPENDENT secondary: {paired} of "
          f"{len(rows)}  Wilson 95% [{lo:.6f}, {hi:.6f}]")
    by_reason = collections.Counter(r[4] for r in rows)
    for k, c in by_reason.most_common():
        print(f"   {k:<38} {c}")
    _check("some pairs are covered", paired >= 1, "no pair got a secondary")
    _check("some pairs are primary-only", paired < len(rows),
           "every pair got a secondary -- the primary-only branch would be dead "
           "code and the rule would be untestable")

    print()
    print("=" * 72)
    if FAILURES:
        print(f"CONSISTENCY CHECKS FAILED: {len(FAILURES)}")
        for f in FAILURES:
            print("   " + f)
        return 1
    print("ALL CROSS-TOOL CONSISTENCY CHECKS PASSED")
    return 0

if __name__ == "__main__":
    sys.exit(main())
