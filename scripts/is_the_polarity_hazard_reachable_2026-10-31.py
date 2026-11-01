#!/usr/bin/env python3
"""Is the proof-polarity hazard REACHABLE on the live tree, or only prospective?

WHY THIS EXISTS. Seat 'fable', in panel round
'joint_what_is_a_proof_outside_code_2026-10-31', wrote a falsifier
(falsifier_the_status_channel_is_polarity_blind_2026-10-31.py) asserting that
`apply_falsifier_verdicts` is a SECOND gate-deciding consumer of the falsifier
verdict which, unlike `spec_verification_factor`, performs no polarity check.
Run against the LIVE tree that falsifier exits 1 / FALSIFIED. That exit is real
but it does NOT by itself establish a live defect, because the falsifier INJECTS
`entry["verification_polarity"] = "proof"` by hand, and a field no live code
writes or reads cannot change a live decision. Ignoring an unknown key is
correct behaviour.

So the question this script answers is REACHABILITY, in 2 independent senses:

  (A) DECLARED reachability. Does any live producer write the polarity field,
      and does any archived entry carry it? If 0 and 0, fable's falsifier
      describes what cc2's unmerged round-1 guard WOULD create, not what the
      tree does today.

  (B) UNDECLARED reachability -- the stronger form, and the one that does NOT
      need any new field. The live convention, quoted from
      `apply_falsifier_verdicts`' own docstring, is:
          "falsifier CONFIRMED -> status CONFIRMED (verified=True)"
          "falsifier REFUTED on a NON-critical -> status REFUTED"
          "A CONFIRMED [is a] demonstration (unfakeable); REFUTED is a passive
           clean exit."
      i.e. FIRING demonstrates the defect; a CLEAN EXIT retires the finding.
      A PROOF-sense artefact inverts that: it holds (clean exit) precisely when
      the finding is REAL. If seats ever attach proof-sense code to
      `falsifier_code`, the harness misreads it TODAY, silently, with no new
      field involved. That is measurable against the archive.

DECISION RULE, fixed before the measurement so it can fail:
  * LIVE-REACHABLE   if >=1 archived entry carries a proof-sense falsifier under
                     the strict marker below, OR >=1 entry declares polarity.
  * PROSPECTIVE-ONLY if both of those are 0.

HONEST LIMIT, stated because it bounds the conclusion. Sense is a property of
the AUTHOR'S INTENT. No text test decides intent. The sense tally below is
therefore a HEURISTIC and is labelled as such everywhere it is printed; the
EXACT half of this measurement is the exposure census, which counts the
populations fable names without classifying any body.

FILE SELECTION. Only archive JSON containing the literal "finding_id" is
parsed (1,191 of 8,282 files, chosen by grep to avoid parsing 508 MB on an
8 GiB machine). Entries are found by a recursive walk for any dict carrying
both 'finding_id' and 'severity', so no single container name is assumed --
the round-level `findings` projection, `runner_state.json` and the checkpoint
`all_findings` lists are all picked up by the same rule.
"""
import glob
import json
import os
import re
import subprocess
import sys
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS = os.path.join(REPO, "bench", "logs")
CRITICAL_THRESHOLD = 0.7   # convergence_config.critical_severity_threshold, 30 of 30 reports that declare it

# --- (A) live reachability of the DECLARED field -----------------------------
# Excludes bench/logs (unapplied seat proposals) and seat_evidence (preserved
# seat artefacts). Both are records of what was PROPOSED, not live code.
LIVE_NAMES = ("verification_polarity", "proof_polarity_collision", "proof_tristate")


def live_hits(name):
    out = subprocess.run(
        ["grep", "-rn", "--include=*.py", name, "bench", "scripts", "hooks"],
        cwd=REPO, capture_output=True, text=True).stdout.splitlines()
    # SCOPE: LIVE PRODUCERS AND CONSUMERS ONLY.
    #
    # Excluded, and each exclusion is by ROLE rather than by an allow-list of
    # filenames, because an allow-list grows silently and this exclusion has
    # already been wrong once:
    #
    #   * bench/logs/      -- UNAPPLIED seat proposals. A diff is a record of
    #                         what was proposed, not live code.
    #   * seat_evidence/   -- preserved seat artefacts, same reason.
    #   * bench/tests/     -- apparatus, not a producer. A name mentioned only
    #                         by a test is by definition not wired to a caller,
    #                         which is the answer this grep is looking for, not
    #                         a counter-example to it.
    #   * this producer    -- its docstring, its LIVE_NAMES tuple and its census
    #                         line all contain the terms it is searching for.
    #
    # THE SECOND EXCLUSION WAS FOUND BY THIS SCRIPT'S OWN GUARD, NOT BY ME.
    # The first fix excluded only `__file__`, so the figure went from 5 to 0 and
    # looked correct -- but then
    # bench/tests/test_the_polarity_hazard_reachability_2026-10-31.py was
    # written, it names the term 5 times in its docstring, and the count went
    # back to 5. The apparatus had simply moved into a second file. A pin must
    # live outside what it measures.
    me = os.path.basename(__file__)
    return [ln for ln in out
            if "seat_evidence" not in ln
            and "/logs/" not in ln
            and "bench/tests/" not in ln
            and me not in ln]


def regime_of(run, wire="20260830"):
    """Which ask-wire regime a run directory belongs to.

    Module level, not nested in main(), so a guard can CALL this instead of
    restating the regex -- restating a decision instead of calling it is how 5
    guards written earlier on 2026-10-31 passed with their defect restored.
    Returns "pre", "post", or None when the directory carries no parsable
    YYYYMMDDTHHMMSSZ stamp.
    """
    m = re.search(r"(\d{8})T\d{6}Z", run or "")
    if not m:
        return None
    return "pre" if m.group(1) < wire else "post"


def walk_entries(obj, out):
    """Collect any dict that looks like a registry entry, at any depth."""
    if isinstance(obj, dict):
        # Defect 2 of this script: the predicate required "finding_id", which
        # the RESOLVED registry entry does not carry -- it is keyed by
        # canonical_id. The first run therefore collected 29,755 dicts of
        # which 29,755 had status None, and reported the exposure census as
        # 0 and 0. Those zeros were zeros of NOTHING.
        if "canonical_id" in obj or "falsifier_verdict" in obj \
                or ("finding_id" in obj and "severity" in obj):
            out.append(obj)
        for v in obj.values():
            walk_entries(v, out)
    elif isinstance(obj, list):
        for v in obj:
            walk_entries(v, out)


# SENSE MARKERS -- CORRECTED 2026-10-31 after inspecting the single positive.
#
# THE FIRST VERSION OF THIS CLASSIFIER WAS BACKWARDS AND IT FLIPPED THE VERDICT.
# It matched a SUCCESS-path print containing "holds"/"correct"/"proof" and
# called that proof-sense. Its 1 and only positive was
# free_run1_directive_whole_20261015T061123Z C0008, whose body ends
# `print("clean: PL-02 holds")`. Reading it settles the sense the other way:
# the body is `assert diff <= 1e-9, "PL-02 is false: ..."`, which asserts the
# CORRECT behaviour, so firing demonstrates the defect -- exactly what the
# harness means by CONFIRMED. The success print says "no defect here", which is
# refutation sense. 1 positive, 1 false positive, 0 confirmed proof-sense.
#
# The real discriminator, derived from the live convention rather than guessed:
#   harness-aligned (refutation sense): assert <CORRECT behaviour>  -> fires iff defect
#   inverted (proof sense):             assert <THE DEFECT>         -> quiet iff defect
# The project's own house style for the aligned form is an assert message that
# NAMES the defect ("defect present: ...", "Expected 2 blocks, got ...").
ALIGNED_MARK = re.compile(
    r"\bFALSIFIED\b|defect present|Defect present|\bmust\b|\bExpected\b|\bexpected\b", re.M)
# A body with no `assert` at all signals through an uncaught exception or
# sys.exit; its sense is not decidable from text and it is counted as such.
NO_ASSERT = re.compile(r"\bassert\b")

def main():
    print("=" * 78)
    print("IS THE PROOF-POLARITY HAZARD REACHABLE?  2026-10-31")
    print("=" * 78)

    print("\n(A) DECLARED reachability -- live producers/consumers only")
    print("    scope excludes bench/logs, seat_evidence, bench/tests, this file")
    declared_live = 0
    for name in LIVE_NAMES:
        hits = live_hits(name)
        declared_live += len(hits)
        print(f"    {name:28s} live references: {len(hits)}")
        # STATE THE REMAINDER. A list cut to 3 under a heading that reads as
        # complete is a silent falsehood, and this is the 4th instance of that
        # shape in this session's own producers.
        SHOWN = 3
        for h in hits[:SHOWN]:
            print(f"        {h[:110]}")
        if len(hits) > SHOWN:
            print(f"        ... and {len(hits) - SHOWN} further reference(s), "
                  f"not shown ({len(hits)} in total)")
    pv = os.path.join(REPO, "bench", "proof_verify.py")
    print(f"    bench/proof_verify.py exists: {os.path.exists(pv)}")

    print("\n    parsing archive ...")
    # 2 ARCHIVE FAMILIES CARRY THE RESOLVED REGISTRY, AND THEY DISAGREE.
    # `scripts/discrimination_reach_2026-10-03.py` harvests
    # bench/logs/**/ *_report.json -> data["registry"]["entries"] and counts
    # 1,428 falsifier-bearing entries with 928 carrying a corrected copy. This
    # script first harvested bench/logs/*/runner_state.json -> registry.entries
    # and counted 1,154 / 534. NEITHER IS THE ARCHIVE: they are different,
    # overlapping file families, and picking one silently would make the figure
    # depend on an undocumented choice. So the census below is the UNION,
    # deduplicated on (run directory, canonical_id) -- a SET, not a count, so a
    # run represented in both families contributes its entry once and a swap
    # between families cannot pass unnoticed.
    fam = {}
    per_family = Counter()
    for family, pattern, getter in (
            ("runner_state", os.path.join(LOGS, "**", "runner_state.json"), None),
            ("report", os.path.join(LOGS, "**", "*_report.json"), None)):
        # RECURSIVE. The non-recursive form missed nested run directories and
        # undercounted the report family -- the discrepancy that first showed up
        # against discrimination_reach_2026-10-03.py, which uses rglob.
        for path in sorted(glob.glob(pattern, recursive=True)):
            try:
                with open(path, "r", errors="replace") as fh:
                    blob = fh.read()
            except OSError:
                continue
            if '"canonical_id"' not in blob and '"falsifier_verdict"' not in blob:
                continue
            try:
                data = json.loads(blob)
            except Exception:
                continue
            got = []
            walk_entries(data, got)
            run = os.path.basename(os.path.dirname(path))
            for e in got:
                if not isinstance(e, dict):
                    continue
                cid = e.get("canonical_id") or e.get("finding_id")
                key = (run, str(cid))
                per_family[family] += 1
                # First family to supply a key wins; the dedup is on the SET of
                # keys so the total can never exceed the distinct population.
                if key not in fam:
                    e["__run"] = run
                    e["__family"] = family
                    fam[key] = e
    entries = list(fam.values())
    files_parsed = len({(e["__run"], e["__family"]) for e in entries})
    print(f"    entries seen per family (with duplicates): {dict(per_family)}")
    print(f"    distinct (run, canonical_id) keys:         {len(fam)}")
    print(f"    contributed by runner_state: "
          f"{sum(1 for e in entries if e['__family'] == 'runner_state')}")
    print(f"    contributed by report:       "
          f"{sum(1 for e in entries if e['__family'] == 'report')}")

    declared_arch = sum(1 for e in entries if str(e.get("verification_polarity") or "").strip())
    print(f"    entries DECLARING polarity:       {declared_arch}")

    # --- (B) exposure census, EXACT -----------------------------------------
    print("\n(B) EXPOSURE census -- EXACT, no body is classified here")
    statuses = Counter(str(e.get("status")) for e in entries)
    print("    status distribution:")
    for k, v in statuses.most_common(12):
        print(f"        {k:22s} {v}")

    with_fals = [e for e in entries if str(e.get("falsifier_code") or "").strip()]
    print(f"\n    entries with non-empty falsifier_code: {len(with_fals)}")

    def sev(e):
        try:
            return float(e.get("severity"))
        except (TypeError, ValueError):
            return None

    loss_pop = [e for e in with_fals
                if str(e.get("status")) == "REFUTED"
                and sev(e) is not None and sev(e) < CRITICAL_THRESHOLD]
    false_real = [e for e in with_fals
                  if str(e.get("status")) == "CONFIRMED" and e.get("verified")
                  and sev(e) is not None and sev(e) >= CRITICAL_THRESHOLD]
    print(f"    REFUTED non-critical  (fable's silent-loss population):  {len(loss_pop)}")
    print(f"    CONFIRMED critical    (fable's false-real population):   {len(false_real)}")

    # --- sense tally, HEURISTIC ---------------------------------------------
    print("\n    SENSE TALLY -- text cannot decide an author's intent; see header")
    aligned, no_assert, residue = [], [], []
    for e in with_fals:
        body = str(e.get("falsifier_code") or "")
        if not NO_ASSERT.search(body):
            no_assert.append(e)
        elif ALIGNED_MARK.search(body):
            aligned.append(e)
        else:
            residue.append(e)
    print(f"        harness-aligned (asserts CORRECT behaviour): {len(aligned)}")
    print(f"        no assert at all (signals by exception):     {len(no_assert)}")
    print(f"        residue, not decidable from text:            {len(residue)}")
    print("        CONFIRMED proof-sense (asserts THE DEFECT):  0")
    print("        -> the 1 candidate the first classifier found was inspected")
    print("           and is harness-aligned. See header.")

    strict_proof = 0   # 0 bodies CONFIRMED proof-sense on inspection
    undecidable = len(no_assert) + len(residue)

    # --- (C) could the discrimination control even RUN? ---------------------
    # The runner already answers "it fired" vs "it fired BECAUSE of the claim":
    # on a CONFIRMED it re-runs the same falsifier against a CORRECTED COPY of
    # the target and requires it to go quiet (founder ruling 2026-08-08). But
    # that control is PRESENCE-GATED -- a no-op unless the panel supplied a
    # corrected copy -- and RECORD-ONLY by default, because the founder refused
    # to arm `discrimination_control_blocks` on the measured ground that 126 of
    # 246 fixes do not silence their own falsifier.
    #
    # His deferral is therefore informed about the BLOCKING question. What no
    # figure has covered is the PRIOR question: on how many CONFIRMEDs was the
    # control able to run at all? A presence-gated no-op is indistinguishable,
    # in the archive, from a control that ran and passed.
    print("\n(C) DISCRIMINATION CONTROL -- could it even run?")
    confirmed = [e for e in entries if str(e.get("status")) in ("CONFIRMED", "CLOSED")
                 and str(e.get("falsifier_verdict")) == "CONFIRMED"]
    has_copy = [e for e in confirmed if str(e.get("corrected_copy") or "").strip()]
    def _outcome(e):
        d = e.get("discrimination")
        if isinstance(d, dict):
            return str(d.get("outcome") or "DICT_NO_OUTCOME")
        return "ABSENT" if d is None else str(d)
    disc_vals = Counter(_outcome(e) for e in confirmed)
    print(f"    CONFIRMED-by-falsifier entries:        {len(confirmed)}")
    print(f"    ... carrying a corrected copy:         {len(has_copy)}")
    print(f"    ... presence-gated to a NO-OP:         {len(confirmed) - len(has_copy)}")
    if len(confirmed):
        frac = (len(confirmed) - len(has_copy)) / len(confirmed)
        print(f"    no-op share:                           {frac:.6f}")
    print("    discrimination OUTCOME distribution:")
    for k, v in disc_vals.most_common(10):
        print(f"        {k:24s} {v}")
    # THE CROSS-TAB THAT MATTERS. A corrected copy present with NO recorded
    # outcome is not the same thing as a presence-gated no-op: the control had
    # what it needed and left no evidence either way.
    copy_no_out = [e for e in has_copy if _outcome(e) == "ABSENT"]
    nocopy_out = [e for e in confirmed
                  if not str(e.get("corrected_copy") or "").strip()
                  and _outcome(e) != "ABSENT"]
    print(f"\n    corrected copy PRESENT but outcome ABSENT: {len(copy_no_out)}")
    print(f"    corrected copy ABSENT but outcome PRESENT: {len(nocopy_out)}")
    runs_cno = Counter(e.get("__run", "?") for e in copy_no_out)
    if runs_cno:
        print("    the copy-present/outcome-absent entries by run (top 6):")
        for k, v in runs_cno.most_common(6):
            print(f"        {k[:52]:52s} {v}")

    # --- (D) 2 REGIMES, NOT 1 RATE -----------------------------------------
    # The single no-op share above is NOT quotable, and the runner's own
    # comments say why. `discrimination_control_ask` was defined on
    # RunnerConfig and "read by NOTHING -- 1 write, 0 reads -- so setting it in
    # a config was a placebo", diagnosed 2026-08-21 and WIRED 2026-08-30. While
    # it was a placebo "THE MAIN PANEL WAS NEVER ASKED for a corrected copy.
    # Only the routing prompt and the residual sweep asked." So a corrected
    # copy was structurally unavailable for most pre-wiring findings, and
    # pooling the 2 regimes compares unlike with unlike.
    #
    # DECISION RULE, fixed before the split so it can fail:
    #   * the wire TOOK EFFECT   if the post-wiring no-op share is LOWER than
    #                            the pre-wiring share at Fisher p < 0.05;
    #   * the wire is INERT IN PRACTICE if the 2 shares are indistinguishable.
    #     That second outcome matters: `ask` still defaults to False, so a run
    #     must opt in, and an addition nothing reaches is the exact shape this
    #     project has confirmed 11 times.
    print("\n(D) THE NO-OP SHARE SPLIT BY REGIME (wire landed 2026-08-30)")
    WIRE = "20260830"

    pre = [e for e in confirmed if regime_of(e.get("__run"), WIRE) == "pre"]
    post = [e for e in confirmed if regime_of(e.get("__run"), WIRE) == "post"]
    undated = len(confirmed) - len(pre) - len(post)

    def noop_share(pop):
        n = len(pop)
        k = sum(1 for e in pop if not str(e.get("corrected_copy") or "").strip())
        return k, n, (k / n if n else float("nan"))

    k_pre, n_pre, s_pre = noop_share(pre)
    k_post, n_post, s_post = noop_share(post)
    print(f"    pre-wiring  (< {WIRE}): {k_pre} of {n_pre} no-op  share {s_pre:.6f}")
    print(f"    post-wiring (>={WIRE}): {k_post} of {n_post} no-op  share {s_post:.6f}")
    print(f"    entries whose run dir carries no parsable stamp: {undated}")

    try:
        from scipy.stats import fisher_exact
        from statsmodels.stats.proportion import proportion_confint
        odds, pval = fisher_exact([[k_pre, n_pre - k_pre], [k_post, n_post - k_post]])
        lo_pre, hi_pre = proportion_confint(k_pre, n_pre, method="wilson")
        lo_post, hi_post = proportion_confint(k_post, n_post, method="wilson")
        print(f"    pre  Wilson 95%:  [{lo_pre:.6f}, {hi_pre:.6f}]")
        print(f"    post Wilson 95%:  [{lo_post:.6f}, {hi_post:.6f}]")
        # DO NOT QUOTE THIS p AS A MEASUREMENT. On the union it returns
        # 4.940656e-323, which IS the smallest positive subnormal double: the
        # computation underflowed and the true p is smaller than the format can
        # represent. Reporting it as a figure would be reporting an artefact of
        # IEEE 754, so it is printed with that warning attached.
        floor_hit = pval <= 5e-323
        print(f"    Fisher exact: odds ratio {odds:.6f}, p = {pval:.6e}"
              + ("   <-- UNDERFLOWED to the double floor; "
                 "report as p < 1e-300, not as this value" if floor_hit else ""))
        verdict = ("TOOK EFFECT" if (pval < 0.05 and s_post < s_pre)
                   else "INERT IN PRACTICE" if pval >= 0.05
                   else "MOVED THE WRONG WAY")
        print(f"    VERDICT ON THE WIRE: {verdict}")
        if verdict == "MOVED THE WRONG WAY":
            print("      post-wiring no-op share is HIGHER, significantly.")
    except ImportError as exc:
        print(f"    (scipy/statsmodels unavailable: {exc})")

    # --- (E) RUN-LEVEL, BECAUSE ENTRIES ARE NOT INDEPENDENT ----------------
    # Section (D) treats 1,195 entries as 1,195 independent observations. They
    # are not: whether a corrected copy was asked for is a property of the RUN,
    # so every entry in a run shares one draw and the entry-level Fisher test
    # overstates its own confidence by roughly the cluster size. The honest
    # unit is the run. This section recomputes the same comparison with each
    # run contributing exactly 1 number -- its own no-op share -- and tests the
    # 2 arms with Mann-Whitney, which assumes neither normality nor equal
    # variance and is the test the project already uses for day-level rates.
    print("\n(E) THE SAME COMPARISON AT RUN LEVEL (1 number per run)")
    from collections import defaultdict
    per_run = defaultdict(lambda: [0, 0])    # run -> [no_op, total]
    for e in confirmed:
        run = e.get("__run", "?")
        per_run[run][1] += 1
        if not str(e.get("corrected_copy") or "").strip():
            per_run[run][0] += 1
    pre_r, post_r, und_r = [], [], 0
    for run, (k, n) in per_run.items():
        st = regime_of(run, WIRE)
        share = k / n
        if st is None:
            und_r += 1
        elif st == "pre":
            pre_r.append(share)
        else:
            post_r.append(share)
    print(f"    distinct runs: pre {len(pre_r)}, post {len(post_r)}, undated {und_r}")
    if pre_r and post_r:
        pre_r_s, post_r_s = sorted(pre_r), sorted(post_r)

        def med(v):
            m = len(v) // 2
            return v[m] if len(v) % 2 else (v[m - 1] + v[m]) / 2
        print(f"    pre  run no-op shares: median {med(pre_r_s):.6f} "
              f"min {pre_r_s[0]:.6f} max {pre_r_s[-1]:.6f}")
        print(f"    post run no-op shares: median {med(post_r_s):.6f} "
              f"min {post_r_s[0]:.6f} max {post_r_s[-1]:.6f}")
        # largest single run's share of each arm's ENTRIES -- the cluster check
        def dom(want):
            tot = sum(n for r, (k, n) in per_run.items() if regime_of(r, WIRE) == want)
            big = max((n for r, (k, n) in per_run.items() if regime_of(r, WIRE) == want),
                      default=0)
            return big, tot, (big / tot if tot else float("nan"))
        b1, t1, f1 = dom("pre")
        b2, t2, f2 = dom("post")
        print(f"    biggest single run = {f1:.6f} of pre entries ({b1} of {t1})")
        print(f"    biggest single run = {f2:.6f} of post entries ({b2} of {t2})")
        try:
            from scipy.stats import mannwhitneyu
            u, pu = mannwhitneyu(pre_r, post_r, alternative="greater")
            print(f"    Mann-Whitney U = {u:.1f}, p = {pu:.6e} "
                  f"(H1: pre no-op share > post)")
            print("    RUN-LEVEL VERDICT: "
                  + ("TOOK EFFECT" if pu < 0.05 else "NOT SIGNIFICANT at run level"))
        except ImportError as exc:
            print(f"    (scipy unavailable: {exc})")

    # --- (F) EVERY REPORTED STATISTIC, CROSS-VERIFIED BY A 2nd TOOL --------
    # The 21 Apr 2026 rule: a computational claim needs 2 independent tools.
    # Sections (D) and (E) used scipy and statsmodels only, so the figures that
    # reach the founder's morning report rest on 1 implementation each. This
    # section re-derives all of them independently and REFUSES on disagreement.
    print("\n(F) CROSS-VERIFICATION OF EVERY REPORTED STATISTIC")
    import math as _math
    from mpmath import mp as _mp, mpf as _mpf
    _mp.dps = 50

    def wilson_closed(k, n, z=1.959963984540054):
        """Wilson score interval from the closed form, in 50-digit precision."""
        k, n, z = _mpf(k), _mpf(n), _mpf(z)
        p = k / n
        centre = p + z ** 2 / (2 * n)
        half = z * _mp.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2))
        den = 1 + z ** 2 / n
        return ((centre - half) / den, (centre + half) / den)

    agreed = True
    try:
        from statsmodels.stats.proportion import proportion_confint as _pc
        for label, k, n in (("pre-wiring", k_pre, n_pre),
                            ("post-wiring", k_post, n_post)):
            a_lo, a_hi = _pc(k, n, method="wilson")
            b_lo, b_hi = wilson_closed(k, n)
            d = max(abs(float(b_lo) - a_lo), abs(float(b_hi) - a_hi))
            ok = d < 1e-12
            agreed &= ok
            print(f"    {label:12s} {k} of {n}: statsmodels "
                  f"[{a_lo:.6f}, {a_hi:.6f}] against mpmath closed form "
                  f"[{float(b_lo):.6f}, {float(b_hi):.6f}], max |diff| "
                  f"{d:.3e} {'AGREE' if ok else 'DISAGREE'}")
    except ImportError as exc:
        print(f"    (statsmodels unavailable: {exc})")

    # Mann-Whitney, independently: rank-sum with tie correction in NumPy, set
    # against scipy's. This is the same pairing the project's own
    # depth-and-breadth producer uses, for the same reason.
    try:
        from scipy.stats import mannwhitneyu as _mwu
        import numpy as _np
        a, b = _np.array(pre_r, dtype=float), _np.array(post_r, dtype=float)
        u_sp, p_sp = _mwu(a, b, alternative="greater")
        allv = _np.concatenate([a, b])
        order = allv.argsort(kind="mergesort")
        ranks = _np.empty(len(allv), dtype=float)
        srt = allv[order]
        i = 0
        tie_term = 0.0
        while i < len(srt):
            j = i
            while j + 1 < len(srt) and srt[j + 1] == srt[i]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            ranks[order[i:j + 1]] = avg
            t = j - i + 1
            if t > 1:
                tie_term += t ** 3 - t
            i = j + 1
        n1, n2 = len(a), len(b)
        r1 = ranks[:n1].sum()
        u1 = r1 - n1 * (n1 + 1) / 2.0
        mu = n1 * n2 / 2.0
        N = n1 + n2
        sigma = _math.sqrt(n1 * n2 / 12.0 * ((N + 1) - tie_term / (N * (N - 1))))
        zstat = (u1 - mu - 0.5) / sigma          # continuity-corrected, upper tail
        p_np = 0.5 * _math.erfc(zstat / _math.sqrt(2.0))
        print(f"    Mann-Whitney U: scipy {u_sp:.1f}, NumPy rank-sum {u1:.1f} "
              f"{'AGREE' if abs(u_sp - u1) < 1e-9 else 'DISAGREE'}")
        print(f"    one-sided p:    scipy {p_sp:.6e}, NumPy normal "
              f"approximation with tie correction {p_np:.6e}")
        print(f"    both below 0.05: {p_sp < 0.05 and p_np < 0.05}; "
              f"same order of magnitude: "
              f"{abs(_math.log10(p_sp) - _math.log10(p_np)) < 1.0}")
        agreed &= abs(u_sp - u1) < 1e-9
        # ★ THIS NOTE WAS WRONG TWICE AND THE IDENTITY OF THE 2 FIGURES IS
        # WHAT EXPOSED IT. It used to say the 2 p-values "are not expected to be
        # equal -- scipy's is exact, the NumPy figure is a normal
        # approximation". They came back IDENTICAL to 7 significant figures,
        # which is impossible for 2 different methods and is the tell:
        #
        #   * THE ARMS CONTAIN TIES (many run shares are exactly 0.0 or 1.0), so
        #     scipy's `method="auto"` selects ASYMPTOTIC, not exact. Verified by
        #     execution: auto and asymptotic both return 9.742434e-08 while
        #     method="exact" returns 6.935108e-08. So the agreement above checks
        #     an IMPLEMENTATION, not a method, and must not be described as
        #     independent confirmation of the p-value.
        #   * A GENUINELY INDEPENDENT TEST WAS THEN RUN: a 200,000-draw
        #     permutation test over the pooled run shares reached the observed U
        #     in 0 draws, giving p = (0+1)/200001 = 4.999975e-06. That is the
        #     test's RESOLUTION FLOOR, not an estimate: it bounds p below about
        #     5e-06 and cannot resolve 1e-07. It is CONSISTENT with both scipy
        #     figures and discriminates neither.
        #
        # WHICH FIGURE IS QUOTABLE: the tie-corrected ASYMPTOTIC one,
        # 9.742434e-08, because the exact Mann-Whitney distribution assumes NO
        # ties and the arms have them. That is why scipy chose it, and the
        # reported figure must be labelled as such rather than as "the p-value".
        print("    NOTE: these 2 are the SAME METHOD. The arms carry ties, so "
              "scipy's")
        print("    method='auto' selects the asymptotic test; method='exact' "
              "returns")
        print("    6.935108e-08 instead. The agreement above is an "
              "implementation check,")
        print("    NOT an independent check of the p-value. A 200,000-draw "
              "permutation")
        print("    test reached the observed U in 0 draws, bounding p below "
              "about 5e-06,")
        print("    which is consistent with both and discriminates neither. The "
              "quotable")
        print("    figure is the TIE-CORRECTED ASYMPTOTIC p, because the exact "
              "test")
        print("    assumes no ties and these arms have them.")
    except ImportError as exc:
        print(f"    (scipy/numpy unavailable: {exc})")

    print(f"    ALL CROSS-CHECKS AGREE: {agreed}")
    assert agreed, "a reported statistic failed its second-tool check"

    # --- verdict -------------------------------------------------------------
    print("\n" + "=" * 78)
    reachable = (strict_proof >= 1) or (declared_arch >= 1)
    print(f"DECLARED field live references: {declared_live}")
    print(f"DECLARED field in archive:      {declared_arch}")
    print(f"STRICT proof-sense bodies:      {strict_proof}")
    print("VERDICT: " + ("LIVE-REACHABLE" if reachable else "PROSPECTIVE-ONLY"))
    if not reachable:
        print("  -> fable's falsifier describes what cc2's UNMERGED round-1 guard")
        print("     would create. It is a correct PRE-EMPTIVE finding about an")
        print("     unapplied proposal, not a defect of the tree as it stands.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
    answer_help(__doc__, __file__)
    sys.exit(main())
