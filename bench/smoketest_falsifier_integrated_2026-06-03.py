"""Integrated falsifier smoke test (2026-06-03).

Proves the INTEGRATED pieces work together against a REAL CDSFL function, using
the production code paths (not bespoke loops):

  * dispatch tool-calling  -> experiment_11_orchestrator.call_openrouter(tools=...)
  * falsifier extraction   -> runner_core.parse_findings (-> Finding.falsifier_code)
  * independent re-verify   -> falsifier_verify.reverify_falsifier (runner decides)

Target: bench.dm._similarity.jaccard_similarity — a pure, deterministic,
embedding-independent function with execution-established ground truth:
  - symmetric: s(f1, f2) == s(f2, f1)                 (HOLDS — verified)
  - self-similarity is NOT 1.0: s(f, f) == 0.86 < 1.0 (HOLDS — a real, checkable
    property: a reasonable reader expects a finding to be maximally similar to
    itself; this function does not deliver that).

Two cases:
  POSITIVE — claim "self-similarity is not 1.0" (TRUE). The model writes a
    falsifier importing the REAL module; an honest falsifier RAISES/prints
    FALSIFIED -> runner re-run = CONFIRMED, matching ground truth.
  NEGATIVE (anti-auto-confirm, MANDATORY) — claim "the function is order-
    dependent (asymmetric)" (FALSE). A correctly written falsifier RAISES only
    if asymmetry is genuinely found; since the function is symmetric it exits
    clean -> runner re-run = REFUTED. A CONFIRMED here would mean the runner
    rubber-stamped a false claim — reported loudly as FAILURE.

The runner re-run is the ONLY verdict. The model's prose claim is never trusted.
Smoke test only — gated/default-OFF integration; not wired into live experiments.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "bench"))

# Load .env (same minimal loader the other smoke tests use).
_env = REPO_ROOT / ".env"
if _env.exists():
    for ln in _env.read_text().splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        ln = ln[7:] if ln.startswith("export ") else ln
        if "=" in ln:
            k, _, v = ln.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip("'\""))

from experiment_11_orchestrator import (  # noqa: E402
    EXECUTE_PYTHON_TOOL,
    call_openrouter,
    default_tool_executor,
)
from runner_core import parse_findings  # noqa: E402
from falsifier_verify import reverify_falsifier  # noqa: E402

MODEL = "openai/gpt-5.5"

# Shared directive scaffold. The CRITICAL refinement is baked in: the falsifier
# MUST import the real module, and MUST be written so it RAISES (AssertionError)
# or prints FALSIFIED *only when the claimed defect is genuinely present*.
_DIRECTIVE_HEAD = """You are a CDSFL STEM/code falsification reviewer with an execute_python tool.
The full local STEM toolset is importable AND the repository is importable.

You are reviewing this SPECIFIC CLAIM about real repository code:

  CLAIM: %s
  TARGET: the function `jaccard_similarity` in module `bench.dm._similarity`.

Your job is to decide, mechanically, whether the CLAIM identifies a REAL defect.

You MUST:
1. Use execute_python to investigate. IMPORT THE REAL MODULE — write
   `from bench.dm._similarity import jaccard_similarity` and
   `from bench.dm._types import Finding`. Do NOT retype or redefine the function;
   test the actual code.
2. Write a FALSIFIER: a self-contained Python snippet that imports the REAL
   module and RAISES an AssertionError (or prints the token FALSIFIED) IF AND
   ONLY IF the claimed defect is genuinely present. If the claim is false, your
   falsifier must run to a clean exit (it must NOT raise and must NOT print
   FALSIFIED).
3. Actually RUN your falsifier with execute_python and read the result.

Report EXACTLY one block in this format:

FINDING_ID: F001
FINDING: <one-line description of the claim under test>
FALSIFIER:
```python
<the exact code you ran — importing the REAL module>
```
RAN_RESULT: <paste the tool's actual output>
VERDICT: CONFIRMED   (if running it demonstrated the defect is real)
or
VERDICT: REFUTED     (if running it showed the claim is false)

A Finding line + a runnable FALSIFIER block are mandatory in every case.
"""

POSITIVE_CLAIM = (
    "jaccard_similarity does NOT return 1.0 for a finding compared with itself "
    "(self-similarity is not maximal): for a non-empty description, "
    "jaccard_similarity(f, f) < 1.0."
)
NEGATIVE_CLAIM = (
    "jaccard_similarity is ORDER-DEPENDENT (asymmetric): there exist findings "
    "f1, f2 such that jaccard_similarity(f1, f2) != jaccard_similarity(f2, f1)."
)

# Ground truth, established earlier by direct execution on the real function:
POSITIVE_GROUND_TRUTH = "CONFIRMED"  # self-sim IS < 1.0 -> defect-claim is real
NEGATIVE_GROUND_TRUTH = "REFUTED"    # function IS symmetric -> claim is false

# Deterministic fallback falsifiers (used only if the model fails to attach a
# usable one). Both import the REAL module and follow the raise-iff-defect rule,
# so the anti-rubber-stamp assertion is never silently skipped.
FALLBACK_POSITIVE = """\
from bench.dm._types import Finding
from bench.dm._similarity import jaccard_similarity
f = Finding('a', 'm', 0, 2, 0.8, 0.5, 'memory leak in the cache eviction path')
s = jaccard_similarity(f, f)
# Defect-claim: self-similarity is not 1.0. Raise IFF that defect is real.
assert s < 1.0, f'self-similarity is {s}, not < 1.0 -> claim NOT demonstrated'
print(f'FALSIFIED: self-similarity is {s}, not 1.0')
"""
FALLBACK_NEGATIVE = """\
from bench.dm._types import Finding
from bench.dm._similarity import jaccard_similarity
a = Finding('a', 'm', 0, 2, 0.8, 0.5, 'buffer overflow in the json parser module')
b = Finding('b', 'm', 0, 2, 0.7, 0.5, 'json parser module has a buffer overflow')
# Defect-claim: function is order-dependent. Raise IFF asymmetry is real.
if jaccard_similarity(a, b) != jaccard_similarity(b, a):
    print('FALSIFIED: order-dependent')
    raise AssertionError('asymmetric')
print('symmetric: claim not demonstrated')
"""


def run_case(name: str, claim: str, ground_truth: str, fallback: str) -> dict:
    """Run one case through the production integration path; return a result row."""
    directive = _DIRECTIVE_HEAD % claim
    print(f"\n--- {name} CASE ---")
    print(f"claim: {claim}")
    used_fallback = False
    try:
        # Production dispatch route with the GATED tool path enabled.
        response = call_openrouter(
            model_id=MODEL,
            system_prompt=(
                "Careful CDSFL falsification reviewer. Prove or disprove the "
                "claim by running code against the REAL module; never assert in "
                "prose alone."
            ),
            user_prompt=directive,
            max_tokens=4096,
            timeout=180,
            max_retries=2,
            tools=[EXECUTE_PYTHON_TOOL],
            tool_executor=default_tool_executor,
            max_tool_iters=6,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"[dispatch error: {type(exc).__name__}: {exc}]")
        return {"case": name, "error": f"{type(exc).__name__}: {exc}"}

    # Production extraction: parse_findings populates Finding.falsifier_code.
    findings = parse_findings("cx", 1, response)
    falsifier = findings[0].falsifier_code if findings else ""
    model_attached = bool(falsifier)
    imports_real = "bench.dm._similarity" in falsifier
    # Model's prose verdict (informational only — never the decider).
    up = response.upper()
    model_verdict = (
        "CONFIRMED" if "VERDICT: CONFIRMED" in up
        else "REFUTED" if "VERDICT: REFUTED" in up
        else "?"
    )

    if not model_attached or not imports_real:
        # Fall back so the anti-rubber-stamp check is deterministic; report it.
        used_fallback = True
        falsifier = fallback

    # THE VERDICT: independent runner re-run. Never the model's claim.
    runner_verdict = reverify_falsifier(falsifier, str(REPO_ROOT))
    matches = runner_verdict == ground_truth

    print(f"model attached falsifier? {model_attached} "
          f"(imports real module: {imports_real})")
    print(f"model prose verdict:      {model_verdict} (informational only)")
    print(f"used fallback falsifier?  {used_fallback}")
    print(f"runner reverify verdict:  {runner_verdict}")
    print(f"ground truth:             {ground_truth}")
    print(f"MATCHES ground truth?     {matches}")
    return {
        "case": name,
        "model_attached_falsifier": model_attached,
        "imports_real_module": imports_real,
        "used_fallback": used_fallback,
        "model_prose_verdict": model_verdict,
        "runner_verdict": runner_verdict,
        "ground_truth": ground_truth,
        "matches_ground_truth": matches,
    }


def main() -> int:
    print("=== integrated falsifier smoke test "
          "(target: real jaccard_similarity) ===")
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("OPENROUTER_API_KEY not set — cannot run the model dispatch. "
              "Reporting honestly and aborting (no faked results).")
        return 2

    rows = []
    rows.append(run_case("POSITIVE", POSITIVE_CLAIM,
                         POSITIVE_GROUND_TRUTH, FALLBACK_POSITIVE))
    rows.append(run_case("NEGATIVE", NEGATIVE_CLAIM,
                         NEGATIVE_GROUND_TRUTH, FALLBACK_NEGATIVE))

    print("\n=== SUMMARY ===")
    ok = True
    neg_row = None
    for r in rows:
        if r.get("error"):
            print(f"{r['case']}: ERROR {r['error']}")
            ok = False
            continue
        print(f"{r['case']}: runner={r['runner_verdict']} "
              f"gt={r['ground_truth']} match={r['matches_ground_truth']} "
              f"(model_attached={r['model_attached_falsifier']}, "
              f"fallback={r['used_fallback']})")
        if not r["matches_ground_truth"]:
            ok = False
        if r["case"] == "NEGATIVE":
            neg_row = r

    # Anti-auto-confirm hard gate: a false claim must NEVER reverify CONFIRMED.
    if neg_row and not neg_row.get("error"):
        if neg_row["runner_verdict"] == "CONFIRMED":
            print("\n*** FAILURE: NEGATIVE (false) claim reverified CONFIRMED — "
                  "the runner RUBBER-STAMPED a false claim. ***")
            ok = False
        elif neg_row["runner_verdict"] == "REFUTED":
            print("\nNEGATIVE case REFUTED as required — no auto-confirm. "
                  "The runner did NOT rubber-stamp the false claim.")
        else:
            print(f"\nNEGATIVE case verdict {neg_row['runner_verdict']} "
                  "(not REFUTED) — investigate; not a clean anti-confirm pass.")
            ok = False

    print(f"\nOVERALL: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
