# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'severity_is_ordinal_2026-11-11', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: a3bd71a1a7a2959b0fadebe9f459e0bf5fbc9bd1b7cf5cff4371964ebfd79967
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Five executable tests on the claim that severity is an ORDINAL quantity.

Round `severity_is_ordinal_2026-11-11`, seat `fable`. Every test imports the
REAL repository module under test; none retypes a formula. Each test prints
CONFIRMS-BRIEF or REFUTES-BRIEF, and the script raises AssertionError at the end
if any claimed defect is demonstrated, so the polarity is: FAILS IFF THE DEFECT
IS PRESENT.

  A. `compute_sev_f` on the brief's four worked examples (sec 3.6).
  B. The z3 / SymPy result the brief states in sec 3.5.
  C. The permissible-statistic table in sec 3.7 (Stevens 1946).
  D. The identification of `v_bar` as mean severity in the brief's P10.
  E. The sec 8 question: can the sums at bench/dm/_convergence.py:267 and :303
     be replaced by an order statistic without changing what the gate decides
     on an archived registry?

Run:  python3 scripts/is_severity_ordinal_the_five_tests_2026-11-11.py
"""
from __future__ import annotations

import glob
import hashlib
import importlib.util
import json
import math
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

DEFECTS: list = []


def _hdr(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


# ---------------------------------------------------------------- A ----------
def test_a_compute_sev_f():
    _hdr("A. compute_sev_f on the brief's four worked examples (sec 3.6)")
    spec = importlib.util.spec_from_file_location(
        "rr3", os.path.join(REPO, "bench", "reference_runner_v3.py"))
    m = importlib.util.module_from_spec(spec)
    sys.modules["rr3"] = m
    spec.loader.exec_module(m)

    print("  _SEVERITY_SPEC                = %s" % (m._SEVERITY_SPEC,))
    print("  CRITICAL_SEVERITY_THRESHOLD   = %s" % (m.CRITICAL_SEVERITY_THRESHOLD,))
    assert m._SEVERITY_SPEC == {"on": False}, "sec 8 expected the switch OFF"

    cases = [
        ("Physics   Isp used without g0", "HARD", 0.90, "CONFIRMED"),
        ("Chemistry limiting reagent",    "HARD", 0.90, "CONFIRMED"),
        ("Biology   ORF off-by-one",      "HARD", 0.90, "CONFIRMED"),
        ("Maths     reversed inequality", "HARD", 0.90, "CONFIRMED"),
    ]
    vals = []
    for name, cls, conf, verdict in cases:
        s = m.compute_sev_f(cls, conf, verdict)
        vals.append(s)
        print("  %-32s -> %s" % (name, s))
    distinct = sorted(set(vals))
    print("  distinct values across four domains: %s" % (distinct,))
    assert distinct == [0.9], "sec 3.6 claims 0.9 for all four"

    rng = sorted({m.compute_sev_f(c, 0.9, v)
                  for c in ("HARD", "SOFT")
                  for v in ("CONFIRMED", "REFUTED", None)})
    print("  attainable RANGE at confidence 0.9: %s  (cardinality %d)"
          % (rng, len(rng)))
    print("  CONFIRMS-BRIEF: one distinct severity across four unrelated consequences.")
    DEFECTS.append("A: compute_sev_f returns one value (0.9) for four materially "
                   "different consequences")
    if len(rng) != 6:
        print("  NOTE the brief says 'the formula's entire range is 6 cells'; the "
              "RANGE has cardinality %d, the DOMAIN has 6 cells. Imprecision, "
              "not a defect." % len(rng))
    return m


# ---------------------------------------------------------------- B ----------
def test_b_sec_35():
    _hdr("B. The z3 / SymPy claim in brief sec 3.5")
    import z3
    import sympy as sp

    s = [z3.Real("s%d" % i) for i in range(4)]
    w = [z3.Real("w%d" % i) for i in range(4)]
    c = [z3.Real("c%d" % i) for i in range(4)]
    v = [z3.Real("v%d" % i) for i in range(4)]
    half = z3.RealVal("1/2")

    S = z3.Solver()
    for i in range(4):
        S.add(z3.Or(w[i] == half, w[i] == 1))
        S.add(c[i] >= 0, c[i] <= 1)
        S.add(z3.Or(v[i] == 0, v[i] == half, v[i] == 1))
        S.add(s[i] == w[i] * c[i] * v[i])
    S.add(z3.Distinct(*s))
    r_free = S.check()
    print("  4 distinct Sev, W in {1/2,1}, confidence and V FREE  -> %s" % r_free)
    if r_free == z3.sat:
        mdl = S.model()
        print("    witness: %s" % ([mdl.eval(x) for x in s],))

    c0, v0 = z3.Real("c0"), z3.Real("v0")
    S2 = z3.Solver()
    S2.add(c0 >= 0, c0 <= 1, z3.Or(v0 == 0, v0 == half, v0 == 1))
    for i in range(4):
        S2.add(z3.Or(w[i] == half, w[i] == 1))
        S2.add(s[i] == w[i] * c0 * v0)
    S2.add(z3.Distinct(*s))
    r_cond = S2.check()
    print("  4 distinct Sev, confidence and V HELD EQUAL          -> %s" % r_cond)

    S3 = z3.Solver()
    S3.add(c0 >= 0, c0 <= 1, z3.Or(v0 == 0, v0 == half, v0 == 1))
    for i in range(2):
        S3.add(z3.Or(w[i] == half, w[i] == 1))
        S3.add(s[i] == w[i] * c0 * v0)
    S3.add(z3.Distinct(s[0], s[1]))
    print("  2 distinct Sev, confidence and V HELD EQUAL          -> %s" % S3.check())

    W, C, V = sp.symbols("W C V", nonnegative=True)
    d = sp.diff(W * C * V, W)
    print("  SymPy  d(Sev)/dW = %s;  at V=0 it is %s, NOT > 0"
          % (d, d.subs({C: sp.Rational(9, 10), V: 0})))
    print("  counterexample to 'distinct severities <=> distinct weights':")
    print("    (<=) W=1 and W=1/2 at V=0 both give Sev = 0")
    print("    (=>) W=1 fixed, confidence 0.9 vs 0.8 at V=1 give 9/10 and 4/5")

    if r_free == z3.sat and r_cond == z3.unsat:
        print("  REFUTES-BRIEF: sec 3.5 says the 4-distinct query is unsat with "
              "confidence and verification FREE. It is SAT. The result holds only "
              "under the conditioning 'confidence and V held equal'.")
        DEFECTS.append("B: brief sec 3.5's z3 claim is false as stated (sat, not "
                       "unsat, with c and v free); and d(Sev)/dW = C*V is >= 0, not "
                       "> 0, so 'distinct severities <=> distinct weights' fails in "
                       "both directions")


# ---------------------------------------------------------------- C ----------
def test_c_sec_37():
    _hdr("C. The permissible-statistic table in brief sec 3.7 (Stevens 1946)")
    import sympy as sp

    t = sp.symbols("t", positive=True)
    maps = {"t**2": t ** 2, "sqrt(t)": sp.sqrt(t), "exp(t)": sp.exp(t),
            "log(1+t)": sp.log(1 + t), "2t": 2 * t, "t": t}

    def phi(name, x):
        return sp.simplify(maps[name].subs(t, x))

    def conventional_median(xs):
        xs = sorted(xs)
        n = len(xs)
        return xs[n // 2] if n % 2 else sp.Rational(1, 2) * (xs[n // 2 - 1] + xs[n // 2])

    def lower_median(xs):
        xs = sorted(xs)
        return xs[(len(xs) - 1) // 2]

    even = [sp.Integer(k) for k in (1, 2, 3, 4)]

    bad_conv = [nm for nm in maps
                if sp.simplify(phi(nm, conventional_median(even))
                               - conventional_median([phi(nm, x) for x in even])) != 0]
    bad_low = [nm for nm in maps
               if sp.simplify(phi(nm, lower_median(even))
                              - lower_median([phi(nm, x) for x in even])) != 0]
    print("  CONVENTIONAL median, even n=4 on levels 1,2,3,4:")
    print("    non-commuting relabellings: %s" % (bad_conv,))
    print("    exact counterexample under phi(t)=t^2: phi(median)=%s  median(phi)=%s"
          % (phi("t**2", conventional_median(even)),
             conventional_median([phi("t**2", x) for x in even])))
    print("  LOWER median (a genuine order statistic), same data:")
    print("    non-commuting relabellings: %s" % (bad_low,))

    cut = sp.Integer(3)
    bad_fixed, bad_transported = [], []
    for nm in maps:
        a = sum(1 for x in even if x >= cut)
        if sum(1 for x in even if phi(nm, x) >= cut) != a:
            bad_fixed.append(nm)
        if sum(1 for x in even if phi(nm, x) >= phi(nm, cut)) != a:
            bad_transported.append(nm)
    print("  count >= cut, cut TRANSPORTED by phi : non-commuting %s" % (bad_transported,))
    print("  count >= cut, cut HELD FIXED         : non-commuting %s" % (bad_fixed,))

    if bad_conv:
        print("  REFUTES-BRIEF (row 1): sec 3.7 lists `median` as admissible without "
              "qualification. The CONVENTIONAL sample median averages the two middle "
              "values at even n and fails on 4 of the brief's own 6 relabellings -- "
              "the same signature it assigns to SUM and MEAN.")
        DEFECTS.append("C1: brief sec 3.7 classes the conventional median as "
                       "ordinal-admissible; it is not, at even sample size")
    if bad_fixed:
        print("  REFUTES-BRIEF (row 2): `count >= cut` is admissible only when the "
              "CUT is transported by the same relabelling. The harness freezes the "
              "cut (CRITICAL_SEVERITY_THRESHOLD = 0.7), under which 5 of 6 "
              "relabellings change the count.")
        DEFECTS.append("C2: the frozen critical cut 0.7 is not order-invariant; an "
                       "ORDER alone does not determine a cut, so P4 as stated is "
                       "incomplete")
    assert not bad_low, "a selected order statistic must be invariant"


# ---------------------------------------------------------------- D ----------
def test_d_v_bar():
    _hdr("D. The brief's P10 identification of `v_bar` as MEAN SEVERITY")
    mgr = open(os.path.join(REPO, "bench", "dm", "_manager.py"),
               encoding="utf-8").read().splitlines()
    f19 = open(os.path.join(REPO, "bench", "run_exp19_fff.py"),
               encoding="utf-8").read().splitlines()
    typ = open(os.path.join(REPO, "bench", "dm", "_types.py"),
               encoding="utf-8").read().splitlines()

    def show(label, lines, n):
        print("  %s:%d: %s" % (label, n, lines[n - 1].strip()))
        return lines[n - 1]

    show("bench/dm/_manager.py", mgr, 644)
    v_line = show("bench/dm/_manager.py", mgr, 718)
    show("bench/dm/_manager.py", mgr, 645)
    a_line = show("bench/dm/_manager.py", mgr, 722)
    show("bench/dm/_types.py", typ, 331)
    show("bench/run_exp19_fff.py", f19, 327)
    f19_line = show("bench/run_exp19_fff.py", f19, 339)

    mgr_v_is_proportion = ("verified" in v_line and "severity" not in v_line)
    mgr_a_is_mean_sev = ("severity" in a_line)
    f19_v_is_mean_sev = ("severity" in f19_line)

    print("  _manager.py v_bar is a VERIFIED-FRACTION, no severity in it : %s"
          % mgr_v_is_proportion)
    print("  _manager.py MEAN SEVERITY is carried by axis `A`, not v_bar : %s"
          % mgr_a_is_mean_sev)
    print("  run_exp19_fff.py v_bar IS mean severity                     : %s"
          % f19_v_is_mean_sev)

    if mgr_v_is_proportion and mgr_a_is_mean_sev and f19_v_is_mean_sev:
        print("  REFUTES-BRIEF: P10 says `v_bar` is the mean severity computed in 4 "
              "places. In bench/dm/_manager.py the name `v_bar` carries the "
              "proportion of findings with verified=True -- a ratio-scale quantity "
              "for which the mean IS admissible -- and the mean severity is the "
              "SEPARATE fingerprint axis `A`. The ordinal objection lands on `A` "
              "(_manager.py:722) and on run_exp19_fff.py:339, not on `v_bar`.")
        print("  AND a real defect P10 did not state: the identifier `v_bar` has TWO "
              "incompatible definitions across modules -- mean severity in "
              "run_exp19_fff.py:327, proportion verified in bench/dm/_manager.py:644 "
              "-- while bench/dm/_types.py:331 documents it as 'Mean verification "
              "quality', matching neither word for word.")
        DEFECTS.append("D: `v_bar` names two different quantities in two modules "
                       "(mean severity in run_exp19_fff.py:327; proportion verified "
                       "in bench/dm/_manager.py:644). P10's premise is wrong; the "
                       "underlying collision is real and sharper.")


# ---------------------------------------------------------------- E ----------
def test_e_kappa_set(limit_runs=60, max_entries=400):
    _hdr("E. sec 8: can the sums at _convergence.py:267 and :303 be replaced by "
         "an order statistic without changing what the gate decides?")
    from bench.dm._convergence import ConvergenceDetector
    from bench.dm._types import DynamicManagementConfig, Finding

    def build(entries):
        rounds = {}
        for cid, e in entries.items():
            try:
                sev = float(e.get("severity") or 0.0)
            except (TypeError, ValueError):
                continue
            occ = e.get("occasions") or []
            rnd = 0
            if occ and isinstance(occ[0], dict):
                try:
                    rnd = int(occ[0].get("round") or 0)
                except (TypeError, ValueError):
                    rnd = 0
            desc = str(e.get("description") or "")[:600]
            rounds.setdefault(rnd, []).append(Finding(
                finding_id=str(cid), model_id=str(e.get("source_model") or "m"),
                round_idx=rnd,
                flaw_class=abs(hash(str(e.get("flaw_class") or 0))) % 8,
                severity=max(0.0, min(1.0, sev)), abstraction_index=0.5,
                description=desc))
        return rounds

    def relabel(rounds, f):
        out = {}
        for r, fs in rounds.items():
            out[r] = [Finding(
                finding_id=x.finding_id, model_id=x.model_id, round_idx=x.round_idx,
                flaw_class=x.flaw_class, severity=f(x.severity),
                abstraction_index=x.abstraction_index, description=x.description)
                for x in fs]
        return out

    def detector(rounds):
        cfg = DynamicManagementConfig()
        cd = ConvergenceDetector(cfg)
        for r in sorted(rounds):
            cd.add_round_findings(r, rounds[r])
        return cd, cfg

    def rank_kappa(cd, r, cut):
        """Order-statistic replacement for kappa_set ONLY. COUNT novel classes
        at or above the cut against COUNT cumulative classes at or above it.
        The only severity operation anywhere in it is a comparison."""
        novel = cd._novel_classes(r)
        cum = cd.get_cumulative_classes(r)
        n = sum(1 for ec in novel if ec.aggregated_severity >= cut)
        d = sum(1 for ec in cum if ec.aggregated_severity >= cut)
        return 1.0 if d == 0 else 1.0 - (n / d)

    def converged_rank(cd, cfg, r, cut):
        """converged() with ONLY kappa_set swapped. kappa_rate, kappa_adopt,
        the min, the severity veto and min_rounds are the production ones.

        ! THE FIRST VERSION OF THIS TEST WAS UNFAIR AND IS RECORDED RATHER THAN
        QUIETLY FIXED. It compared `rank_kappa >= tau_kappa` against the WHOLE
        of converged(), which also mins in kappa_rate and kappa_adopt. That
        reported 13 disagreements out of 18 -- all of them the two metrics the
        replacement had silently dropped, none of them severity. The faithful
        substitution below reports 0."""
        if r < cfg.min_rounds_for_convergence:
            return False
        if any(ec.aggregated_severity >= cut for ec in cd._novel_classes(r)):
            return False
        k = min(rank_kappa(cd, r, cut),
                max(0.0, cd.kappa_rate(r)), cd.kappa_adopt(r))
        return k >= cfg.tau_kappa

    PHIS = {
        "square": lambda x: x * x,
        "sqrt":   lambda x: math.sqrt(x),
        "expm1":  lambda x: (math.exp(x) - 1.0) / (math.e - 1.0),
        "log1p":  lambda x: math.log1p(x) / math.log(2.0),
    }

    files = sorted(glob.glob(os.path.join(REPO, "bench", "logs", "**",
                                          "runner_state.json"), recursive=True))
    print("  archived runner_state.json files found: %d" % len(files))

    seen, examined = set(), 0
    sum_flip = rank_flip = cases = 0
    agree_identity = disagree_identity = kset_binds = 0
    detail = []

    for fp in files:
        if examined >= limit_runs:
            break
        try:
            raw = open(fp, encoding="utf-8").read()
        except OSError:
            continue
        dg = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        if dg in seen:
            continue
        seen.add(dg)
        try:
            entries = (json.loads(raw).get("registry") or {}).get("entries") or {}
        except json.JSONDecodeError:
            continue
        if not entries or len(entries) > max_entries:
            continue
        base = build(entries)
        if len(base) < 2:
            continue
        rmax = max(base)
        try:
            cd0, cfg = detector(base)
            cut = cfg.eta_veto
            base_conv = cd0.converged(rmax)
            base_rank_conv = converged_rank(cd0, cfg, rmax, cut)
            _ks, _kr, _ka = (cd0.kappa_set(rmax),
                             max(0.0, cd0.kappa_rate(rmax)), cd0.kappa_adopt(rmax))
        except Exception as exc:
            detail.append("    skipped %s: %s"
                          % (os.path.basename(os.path.dirname(fp)), exc))
            continue
        examined += 1
        if _ks <= min(_kr, _ka) + 1e-12:
            kset_binds += 1
        if base_conv == base_rank_conv:
            agree_identity += 1
        else:
            disagree_identity += 1

        for nm, f in PHIS.items():
            cases += 1
            cdp, cfgp = detector(relabel(base, f))
            if cdp.converged(rmax) != base_conv:
                sum_flip += 1
            if converged_rank(cdp, cfgp, rmax, f(cut)) != base_rank_conv:
                rank_flip += 1

    print("  distinct archived registries exercised : %d" % examined)
    print("  kappa_set is the BINDING term of the min in : %d" % kset_binds)
    print("  (registry, relabelling) cases          : %d" % cases)
    print("  converged() flips under a strictly increasing relabelling")
    print("    with the SUM at :267/:303 in place   : %d" % sum_flip)
    print("    with the order-statistic replacement : %d" % rank_flip)
    print("  on the UNRELABELLED data the two gates agree on %d registries and "
          "disagree on %d" % (agree_identity, disagree_identity))
    for d in detail[:5]:
        print(d)

    if examined == 0:
        print("  INCONCLUSIVE: no usable archived registry. Not a result.")
        return

    print()
    print("  ANSWER TO sec 8's QUESTION, as measured:")
    if disagree_identity == 0:
        print("    On these %d archived registries the order-statistic replacement "
              "decides EXACTLY what the sum decides. The swap is "
              "behaviour-preserving ON THIS ARCHIVE." % examined)
    else:
        print("    The swap CHANGES the decision on %d of %d archived registries. "
              "It is NOT a free substitution, and under the additive standard it "
              "may not be made on judgement alone."
              % (disagree_identity, examined))
        DEFECTS.append("E: the order-statistic replacement changes converged() on "
                       "%d/%d archived registries"
                       % (disagree_identity, examined))
    if sum_flip > rank_flip:
        print("    And the sum is the NON-INVARIANT half: %d flips against %d for "
              "the replacement." % (sum_flip, rank_flip))
        DEFECTS.append("E2: kappa_set's converged() verdict moves under a strictly "
                       "increasing relabelling in %d/%d cases; the order-statistic "
                       "form moves in %d" % (sum_flip, cases, rank_flip))
    elif sum_flip == 0:
        print("    NOTE: the sum did NOT flip on this archive either (%d flips). "
              "The non-invariance is real in principle (test C) but is NOT "
              "EXERCISED by these registries. Reporting the null, not hiding it."
              % sum_flip)


# ---------------------------------------------------------------- F ----------
def test_f_constraint_class_is_unreachable():
    """The B84/B87 `constraint_class` writer cannot be reached by any model.

    brief sec 3.1 says `constraint_class` has 1 reader and 0 writers.
    docs/MATHEMATICAL_APPENDIX.md (sec 7.7, corrected 2026-11-11) says a writer
    NOW exists and "that half is now closed". Both are wrong in the way that
    matters: a writer exists at bench/reference_runner_v3.py:3620, and NOTHING
    CAN REACH IT, because bench/cdsfl_finding_schema.json -- the envelope every
    model must emit -- carries no such property, and no code path anywhere
    assigns `constraint_class=` on a Finding.
    """
    import ast
    _hdr("F. Is the B84 `constraint_class` writer REACHABLE?")

    schema = json.load(open(os.path.join(REPO, "bench", "cdsfl_finding_schema.json"),
                            encoding="utf-8"))
    props = (((schema.get("properties") or {}).get("findings") or {})
             .get("items") or {}).get("properties") or {}
    print("  schema finding-item properties: %s" % sorted(props))
    in_schema = "constraint_class" in props
    print("  `constraint_class` accepted by the envelope schema : %s" % in_schema)

    # Does ANY code path assign constraint_class= when constructing a Finding?
    assigners = []
    for root, _dirs, fns in os.walk(os.path.join(REPO, "bench")):
        if "logs" in root.split(os.sep) or "tests" in root.split(os.sep):
            continue
        for fn in fns:
            if not fn.endswith(".py"):
                continue
            fp = os.path.join(root, fn)
            try:
                tree = ast.parse(open(fp, encoding="utf-8").read())
            except (SyntaxError, UnicodeDecodeError, OSError):
                continue
            for node in ast.walk(tree):
                # Finding(..., constraint_class=X)
                if isinstance(node, ast.Call):
                    fname = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
                    if fname == "Finding":
                        for kw in node.keywords:
                            if kw.arg == "constraint_class":
                                assigners.append("%s:%d Finding(constraint_class=...)"
                                                 % (os.path.relpath(fp, REPO), node.lineno))
                # f.constraint_class = X  /  d["constraint_class"] = X
                if isinstance(node, ast.Assign):
                    for tgt in node.targets:
                        if isinstance(tgt, ast.Attribute) and tgt.attr == "constraint_class":
                            assigners.append("%s:%d attribute assignment"
                                             % (os.path.relpath(fp, REPO), node.lineno))
                        if (isinstance(tgt, ast.Subscript)
                                and isinstance(getattr(tgt, "slice", None), ast.Constant)
                                and tgt.slice.value == "constraint_class"):
                            assigners.append("%s:%d subscript assignment"
                                             % (os.path.relpath(fp, REPO), node.lineno))
    print("  code paths that SET a Finding's constraint_class: %d" % len(assigners))
    for a in assigners:
        print("    %s" % a)

    rr = open(os.path.join(REPO, "bench", "reference_runner_v3.py"),
              encoding="utf-8").read().splitlines()
    print("  the WRITER, bench/reference_runner_v3.py:3620:")
    print("    %s" % rr[3619].strip())
    writer_reads_default = 'getattr(finding, "constraint_class", "")' in rr[3619]
    print("  writer sources the value from the Finding attribute : %s"
          % writer_reads_default)

    if (not in_schema) and (not assigners) and writer_reads_default:
        print("  FALSIFIED: the envelope schema cannot carry `constraint_class`, no "
              "code path assigns it, so the Finding attribute is ALWAYS its default "
              "\"\" and the writer at :3620 always writes the empty string. "
              "compute_sev_f then defaults W to HARD=1.0 for EVERY finding, exactly "
              "as before the writer was added.")
        print("  This is an ADDITION NOTHING REACHES -- the defect class this "
              "project has measured 11 times since 2026-08-01 -- added 2026-11-11 "
              "(bench/dm/_types.py:436). And docs/MATHEMATICAL_APPENDIX.md sec 7.7 "
              "now tells a reader the half is CLOSED when it is not.")
        DEFECTS.append("F [CRITICAL]: the B84 `constraint_class` writer at "
                       "bench/reference_runner_v3.py:3620 is unreachable -- absent "
                       "from bench/cdsfl_finding_schema.json and assigned by 0 code "
                       "paths -- so W is still HARD=1.0 for every finding and "
                       "section 7.7 is still uncomputable. The appendix states the "
                       "opposite.")
    else:
        print("  NOT DEMONSTRATED: a producer exists. sec 7.7's W input is "
              "collectable.")


def main():
    test_a_compute_sev_f()
    test_b_sec_35()
    test_c_sec_37()
    test_d_v_bar()
    test_e_kappa_set()
    test_f_constraint_class_is_unreachable()

    _hdr("SUMMARY")
    if DEFECTS:
        print("FALSIFIED")
        for i, d in enumerate(DEFECTS, 1):
            print("  %d. %s" % (i, d))
        raise AssertionError("%d claimed defect(s) demonstrated" % len(DEFECTS))
    print("No claimed defect demonstrated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
