"""EXECUTE the shipped absorption decision -- do not grep it.

Extracts the live decision block from bench/reference_runner_v3.py verbatim,
compiles it, and calls it. Then calls (a) the falsifier-difference rule and
(b) the REJECTED signature-similarity-only rule on the same archived pairs.
"""
import glob, itertools, json, re, sys, textwrap, types
from pathlib import Path

REPO = Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "bench"))
from bench.convergence_location import signature_similarity, stem_signature

SRC = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")

# --- extract the SHIPPED block verbatim, by anchors, not line numbers --------
start = SRC.index("                _absorb = True\n                _sim = 1.0\n")
end_anchor = SRC.index("                if _absorb:\n", start)
BLOCK = SRC[start:end_anchor]
print("EXTRACTED SHIPPED BLOCK: %d chars, %d lines"
      % (len(BLOCK), BLOCK.count("\n")))

THRESHOLD = None
m = re.search(r"^_UNLOCATED_MERGE_THRESHOLD\s*=\s*([0-9.]+)", SRC, re.M)
THRESHOLD = float(m.group(1))
print("SHIPPED _UNLOCATED_MERGE_THRESHOLD =", THRESHOLD)

FN_SRC = ("def _shipped_absorb(f, registry, existing, _UNLOCATED_MERGE_THRESHOLD, _log):\n"
          + textwrap.indent(textwrap.dedent(BLOCK), "    ")
          + "    return _absorb, _sim\n")
ns = {}
exec(compile(FN_SRC, "<shipped-absorb-block>", "exec"), ns)
shipped_absorb = ns["_shipped_absorb"]

class _F:                      # stands in for the runner's Finding object
    def __init__(self, d):
        self.model_id = "M"; self.finding_id = "F1"
        self.description = d.get("description") or ""
        self.falsifier_code = d.get("falsifier_code") or ""
class _Reg:
    def __init__(self, prev): self.entries = {"C0001": prev}

def call_shipped(new, prev):
    return shipped_absorb(_F(new), _Reg(prev), "C0001", THRESHOLD, lambda *a: None)

# --- the two comparison rules ------------------------------------------------
def falsifier_rule(new, prev):
    """Different falsifier => different defect => NOT absorbed."""
    a = (new.get("falsifier_code") or "").strip()
    b = (prev.get("falsifier_code") or "").strip()
    if a and b and a != b:
        return False
    na, nb = stem_signature(new.get("description") or ""), stem_signature(prev.get("description") or "")
    if na and nb and signature_similarity(na, nb) < THRESHOLD:
        return False
    return True

def rejected_signature_rule(new, prev):
    """THE REJECTED SIMPLIFICATION: textual signature similarity alone."""
    na, nb = stem_signature(new.get("description") or ""), stem_signature(prev.get("description") or "")
    if na and nb and signature_similarity(na, nb) < THRESHOLD:
        return False
    return True

# --- build the archived pair set --------------------------------------------
FN_RE = re.compile(r"`([A-Za-z_][A-Za-z0-9_]*)\s*\(\)?`|\b([a-z_][a-z0-9_]{3,})\(\)")
def fn_names(text):
    out = set()
    for a, b in FN_RE.findall(text or ""):
        out.add(a or b)
    return out

ents = []
for p in sorted(glob.glob(str(REPO / "bench/logs/**/*_report.json"), recursive=True)):
    try: d = json.load(open(p))
    except Exception: continue
    reg = d.get("registry")
    if not isinstance(reg, dict): continue
    for e in (reg.get("entries") or {}).values():
        if (e.get("falsifier_code") or "").strip() and (e.get("description") or "").strip():
            ents.append({"description": e["description"],
                         "falsifier_code": e["falsifier_code"],
                         "fns": fn_names(e["description"]),
                         "src": p})
print("ARCHIVED ENTRIES with both description and falsifier_code:", len(ents))

pairs = [(a, b) for a, b in itertools.combinations(ents, 2)
         if a["fns"] & b["fns"] and a["falsifier_code"].strip() != b["falsifier_code"].strip()]
print("SAME-FUNCTION, DIFFERENT-FALSIFIER PAIRS:", len(pairs))

# --- run all three rules on every pair ---------------------------------------
dis_ship_vs_fals = 0
dis_ship_vs_rejected = 0
rejected_would_absorb = 0
errors = 0
for a, b in pairs:
    try:
        s, _sim = call_shipped(a, b)
    except Exception as exc:
        errors += 1; continue
    fr = falsifier_rule(a, b)
    rr = rejected_signature_rule(a, b)
    if s != fr: dis_ship_vs_fals += 1
    if s != rr: dis_ship_vs_rejected += 1
    if rr: rejected_would_absorb += 1

n = len(pairs) - errors
print()
print("=== EXECUTED RESULTS over %d pairs (errors=%d) ===" % (n, errors))
print("shipped vs falsifier-difference rule  : %d disagreements" % dis_ship_vs_fals)
print("shipped vs REJECTED signature-only    : %d disagreements" % dis_ship_vs_rejected)
print("rejected rule would ABSORB (delete)   : %d of %d = %.4f"
      % (rejected_would_absorb, n, rejected_would_absorb / n if n else 0))
try:
    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(rejected_would_absorb, n, method="wilson")
    print("Wilson 95%% CI for the rejected rule's deletion rate: [%.4f, %.4f]" % (lo, hi))
except Exception as e:
    import math
    p = rejected_would_absorb / n; z = 1.959963984540054
    d = 1 + z*z/n; c = (p + z*z/(2*n))/d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    print("Wilson 95%% CI (hand-computed): [%.4f, %.4f]" % (c-h, c+h))
