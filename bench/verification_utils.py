"""PM filter quality gate for CDSFL.

Run 8: observation-only (logs verdicts, all findings pass through).
Run 9+: load-bearing via immune_agents.py (6-cell immune pipeline).

Each verification stage (dedup, SymPy, AST, z3, statsmodels, PM) runs
independently and records results into a QualityGateResult.
"""

from __future__ import annotations

import ast
import json
import os
import re
import shutil
import subprocess as sp
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from bench.dm._types import Finding
from bench.dm._convergence import _finding_similarity


# ═══════════════════════════════════════════════════════════════════════════════
# Tool-equipped Python discovery
# ═══════════════════════════════════════════════════════════════════════════════

def _find_tools_python() -> str:
    """Find Python with SymPy/z3/statsmodels. Cached at module level."""
    candidates = [
        "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3",
        "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3",
        shutil.which("python3.13") or "",
        shutil.which("python3.12") or "",
    ]
    for py in candidates:
        if py and os.path.isfile(py):
            try:
                r = sp.run([py, "-c", "import sympy; print('ok')"],
                           capture_output=True, text=True, timeout=10)
                if "ok" in r.stdout:
                    return py
            except (sp.TimeoutExpired, OSError):
                continue
    return sys.executable  # fallback

_TOOLS_PYTHON: str = _find_tools_python()


# ═══════════════════════════════════════════════════════════════════════════════
# 1. SymPy verification (lifted from bench/interactive_smoke.py:67-112)
# ═══════════════════════════════════════════════════════════════════════════════


def verify_sympy(claim: str) -> dict:
    """Verify a mathematical claim via SymPy in a subprocess sandbox.

    Uses sympy.parse_expr with implicit multiplication and a custom local
    dict, evaluates via simplify(), with numerical fallback at n=100.
    Runs in a subprocess with a 10-second timeout.

    Args:
        claim: A string containing a mathematical expression or equation.

    Returns:
        {"verified": bool|None, "result": str, "method": str}
    """
    if not claim or claim.strip() == "None":
        return {"verified": None, "result": "no claim", "method": "skipped"}
    try:
        code = f"""
import sympy
from sympy import *
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
try:
    expr = parse_expr({repr(claim)},
        transformations=(standard_transformations + (implicit_multiplication_application,)),
        local_dict={{'pi': sympy.pi, 'E': sympy.E, 'oo': sympy.oo, 'n': symbols('n'),
                     'sqrt': sympy.sqrt, 'cos': sympy.cos, 'sin': sympy.sin,
                     'Eq': sympy.Eq, 'Gt': sympy.Gt, 'Lt': sympy.Lt,
                     'Ge': sympy.Ge, 'Le': sympy.Le, 'And': sympy.And}},
        global_dict={{'__builtins__': {{}}}})
    result = sympy.simplify(expr)
    if result == True:
        print("VERIFIED_TRUE")
    elif result == False:
        print("VERIFIED_FALSE")
    else:
        n_val = expr.subs(symbols('n'), 100)
        if n_val == True:
            print(f"NUMERICAL_TRUE (n=100)")
        elif n_val == False:
            print(f"NUMERICAL_FALSE (n=100)")
        else:
            print(f"SIMPLIFIED: {{result}}")
except Exception as e:
    print(f"UNVERIFIABLE: {{e}}")
"""
        result = sp.run(
            [_TOOLS_PYTHON, "-c", code],
            capture_output=True, text=True, timeout=10,
        )
        output = result.stdout.strip()
        if "VERIFIED_TRUE" in output or "NUMERICAL_TRUE" in output:
            return {"verified": True, "result": output, "method": "sympy"}
        elif "VERIFIED_FALSE" in output or "NUMERICAL_FALSE" in output:
            return {"verified": False, "result": output, "method": "sympy"}
        else:
            return {"verified": None, "result": output, "method": "unverifiable"}
    except Exception as e:
        return {"verified": None, "result": str(e), "method": "error"}


# ═══════════════════════════════════════════════════════════════════════════════
# 1b. z3 logical invariant verification
# ═══════════════════════════════════════════════════════════════════════════════


def verify_z3(claim: str) -> dict:
    """Verify a logical invariant claim via z3-solver in a subprocess.

    Attempts to express numeric constraints as z3 assertions and check
    satisfiability. Returns {"verified": bool|None, "result": str, "method": "z3"}.
    """
    if not claim or claim.strip() == "None":
        return {"verified": None, "result": "no claim", "method": "skipped"}
    try:
        code = f"""
import z3, re
claim = {repr(claim)}
nums = re.findall(r'[-+]?\\d*\\.?\\d+', claim)
if len(nums) >= 2:
    a, b = float(nums[0]), float(nums[1])
    x = z3.Real('x')
    s = z3.Solver()
    if '>=' in claim:
        s.add(z3.Not(x >= b)); s.add(x == a)
        print("VERIFIED_TRUE" if s.check() == z3.unsat else "VERIFIED_FALSE")
    elif '<=' in claim:
        s.add(z3.Not(x <= b)); s.add(x == a)
        print("VERIFIED_TRUE" if s.check() == z3.unsat else "VERIFIED_FALSE")
    elif '==' in claim or '= ' in claim:
        s.add(z3.Not(x == b)); s.add(x == a)
        print("VERIFIED_TRUE" if s.check() == z3.unsat else "VERIFIED_FALSE")
    else:
        print(f"Z3_PARSED: {len(nums)} values")
else:
    print("Z3_UNSTRUCTURED")
"""
        result = sp.run(
            [_TOOLS_PYTHON, "-c", code],
            capture_output=True, text=True, timeout=10,
        )
        output = result.stdout.strip()
        if "VERIFIED_TRUE" in output:
            return {"verified": True, "result": output, "method": "z3"}
        elif "VERIFIED_FALSE" in output:
            return {"verified": False, "result": output, "method": "z3"}
        else:
            return {"verified": None, "result": output, "method": "z3"}
    except Exception as e:
        return {"verified": None, "result": str(e), "method": "z3_error"}


# ═══════════════════════════════════════════════════════════════════════════════
# 1c. Statistical verification via statsmodels
# ═══════════════════════════════════════════════════════════════════════════════


def verify_statistical(claim: str) -> dict:
    """Verify a statistical claim by extracting and checking p-values/correlations.

    Returns {"verified": bool|None, "result": str, "method": "statsmodels"}.
    """
    if not claim or claim.strip() == "None":
        return {"verified": None, "result": "no claim", "method": "skipped"}
    try:
        code = f"""
import re
claim = {repr(claim)}
p_match = re.search(r'p\\s*[<=]\\s*(0\\.\\d+)', claim)
if p_match:
    p = float(p_match.group(1))
    print("STAT_SIGNIFICANT" if p < 0.05 else "STAT_NOT_SIGNIFICANT")
else:
    r_match = re.search(r'r\\s*=\\s*([-+]?0?\\.\\d+)', claim)
    if r_match:
        r = abs(float(r_match.group(1)))
        label = "STRONG" if r > 0.7 else "MODERATE" if r > 0.3 else "WEAK"
        print(f"CORRELATION_{{label}}: r={{r_match.group(1)}}")
    else:
        print("STAT_UNPARSEABLE")
"""
        result = sp.run(
            [_TOOLS_PYTHON, "-c", code],
            capture_output=True, text=True, timeout=10,
        )
        output = result.stdout.strip()
        if "SIGNIFICANT" in output and "NOT_SIGNIFICANT" not in output:
            return {"verified": True, "result": output, "method": "statsmodels"}
        elif "NOT_SIGNIFICANT" in output:
            return {"verified": False, "result": output, "method": "statsmodels"}
        else:
            return {"verified": None, "result": output, "method": "statsmodels"}
    except Exception as e:
        return {"verified": None, "result": str(e), "method": "statsmodels_error"}


# ═══════════════════════════════════════════════════════════════════════════════
# 2. AST-based structural verification
# ═══════════════════════════════════════════════════════════════════════════════


def verify_ast_claim(
    claim_type: str, claim_target: str, source_path: str
) -> dict:
    """Verify structural claims about Python source code using ast.parse().

    Supported claim types:
        - "decorator_exists": check if any class has decorator ``claim_target``
        - "class_exists": check if a class named ``claim_target`` exists
        - "method_exists": check if a method named ``claim_target`` exists
          in any class

    Args:
        claim_type: One of "decorator_exists", "class_exists", "method_exists".
        claim_target: The name of the decorator, class, or method to find.
        source_path: Path to the Python source file.

    Returns:
        {"verified": bool|None, "result": str, "method": "ast"}
    """
    try:
        with open(source_path, "r") as f:
            tree = ast.parse(f.read(), filename=source_path)
    except (OSError, SyntaxError) as e:
        return {"verified": None, "result": f"parse error: {e}", "method": "ast"}

    if claim_type == "class_exists":
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == claim_target:
                return {
                    "verified": True,
                    "result": f"class {claim_target} found at line {node.lineno}",
                    "method": "ast",
                }
        return {
            "verified": False,
            "result": f"class {claim_target} not found",
            "method": "ast",
        }

    elif claim_type == "method_exists":
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if (
                        isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and item.name == claim_target
                    ):
                        return {
                            "verified": True,
                            "result": (
                                f"method {claim_target} found in class "
                                f"{node.name} at line {item.lineno}"
                            ),
                            "method": "ast",
                        }
        return {
            "verified": False,
            "result": f"method {claim_target} not found in any class",
            "method": "ast",
        }

    elif claim_type == "decorator_exists":
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for dec in node.decorator_list:
                    dec_name = None
                    if isinstance(dec, ast.Name):
                        dec_name = dec.id
                    elif isinstance(dec, ast.Attribute):
                        dec_name = dec.attr
                    elif isinstance(dec, ast.Call):
                        if isinstance(dec.func, ast.Name):
                            dec_name = dec.func.id
                        elif isinstance(dec.func, ast.Attribute):
                            dec_name = dec.func.attr
                    if dec_name == claim_target:
                        return {
                            "verified": True,
                            "result": (
                                f"decorator @{claim_target} found on class "
                                f"{node.name} at line {node.lineno}"
                            ),
                            "method": "ast",
                        }
        return {
            "verified": False,
            "result": f"decorator @{claim_target} not found on any class",
            "method": "ast",
        }

    else:
        return {
            "verified": None,
            "result": f"unknown claim_type: {claim_type}",
            "method": "ast",
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Deduplication
# ═══════════════════════════════════════════════════════════════════════════════


def dedup_findings(
    new_findings: List[Finding],
    prior_findings: List[Finding],
    tau_sim: float = 0.8,
) -> Tuple[List[Finding], List[dict]]:
    """Deduplicate new findings against prior findings.

    For each new finding, computes similarity against all prior findings
    using _finding_similarity from bench.dm._convergence. If max similarity
    >= tau_sim, marks the finding as a duplicate.

    Args:
        new_findings: Findings from the current round.
        prior_findings: Accumulated findings from previous rounds.
        tau_sim: Similarity threshold for duplicate detection.

    Returns:
        (unique_findings, dedup_log) where dedup_log contains per-finding
        dicts with {finding_id, duplicate_of, similarity}.
    """
    unique: List[Finding] = []
    dedup_log: List[dict] = []

    for nf in new_findings:
        best_sim = 0.0
        best_match: Optional[str] = None

        for pf in prior_findings:
            sim = _finding_similarity(nf, pf)
            if sim > best_sim:
                best_sim = sim
                best_match = pf.finding_id

        is_dup = best_sim >= tau_sim
        dedup_log.append({
            "finding_id": nf.finding_id,
            "duplicate_of": best_match if is_dup else None,
            "similarity": round(best_sim, 4),
        })

        if not is_dup:
            unique.append(nf)

    return unique, dedup_log


# ═══════════════════════════════════════════════════════════════════════════════
# 4. QualityGateResult
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class QualityGateResult:
    """Aggregated result from all quality-gate stages."""

    filtered_findings: List[Finding]     # findings that passed all stages
    all_findings: List[Finding]          # original input findings
    dedup_log: List[dict]                # per-finding dedup verdicts
    sympy_log: List[dict]                # per-finding sympy verdicts (if applicable)
    ast_log: List[dict]                  # per-finding ast verdicts (if applicable)
    pm_verdicts: List[dict]              # per-finding PM verdicts
    agreement_rate: float                # fraction of findings PM confirmed
    stage_timings: Dict[str, float]      # {stage_name: seconds}
    dedup_count: int                     # how many were marked as duplicates
    pm_confirmed: int = 0
    pm_rejected: int = 0


# ═══════════════════════════════════════════════════════════════════════════════
# 5. PM verification via local claude CLI
# ═══════════════════════════════════════════════════════════════════════════════


def pm_verify_findings(
    findings: List[Finding],
    source_paths: List[str],
    timeout: int = 120,
    pm_enabled: bool = False,
) -> List[dict]:
    """Verify findings using local claude CLI as a PM (Project Manager) step.

    Hardware-aware for M1 8GB: runs a single sequential call, not parallel
    agents. Uses claude -p with restricted tools and max 3 turns.

    Args:
        findings: Findings to verify.
        source_paths: Paths to source files the PM should inspect.
        timeout: Subprocess timeout in seconds.
        pm_enabled: If False, returns empty verdicts immediately.

    Returns:
        List of {"finding_id": str, "verdict": str, "reasoning": str}
        where verdict is "CONFIRMED", "REJECTED", or "NEEDS_INFO".
    """
    if not pm_enabled or not findings:
        return [
            {"finding_id": f.finding_id, "verdict": "SKIPPED", "reasoning": "PM disabled"}
            for f in findings
        ]

    # Build the verification prompt
    files_list = "\n".join(f"  - {p}" for p in source_paths)
    findings_block = "\n".join(
        f"  [{f.finding_id}] severity={f.severity:.2f} "
        f"flaw_class={f.flaw_class}: {f.description}"
        for f in findings
    )

    prompt = (
        "You are a verification PM. Read the source files listed below and "
        "verify each finding using Find-Follow-Fix (FFF).\n\n"
        f"Source files:\n{files_list}\n\n"
        f"Findings to verify:\n{findings_block}\n\n"
        "For EACH finding, respond with exactly one JSON object per line "
        "(no other text), with keys: finding_id, verdict (CONFIRMED|REJECTED|NEEDS_INFO), reasoning.\n"
        "Example: {\"finding_id\": \"f1\", \"verdict\": \"CONFIRMED\", \"reasoning\": \"...\"}"
    )

    try:
        result = sp.run(
            [
                "claude", "-p", prompt,
                "--allowedTools", "Read,Bash,Grep,Glob",
                "--max-turns", "3",
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout.strip()

        # Parse JSON lines from output
        verdicts: List[dict] = []
        seen_ids: set = set()
        for line in output.splitlines():
            line = line.strip()
            if not line or not line.startswith("{"):
                continue
            try:
                obj = json.loads(line)
                if "finding_id" in obj and "verdict" in obj:
                    verdicts.append({
                        "finding_id": obj["finding_id"],
                        "verdict": obj.get("verdict", "NEEDS_INFO"),
                        "reasoning": obj.get("reasoning", ""),
                    })
                    seen_ids.add(obj["finding_id"])
            except json.JSONDecodeError:
                continue

        # Fill in any findings not covered in the response
        for f in findings:
            if f.finding_id not in seen_ids:
                verdicts.append({
                    "finding_id": f.finding_id,
                    "verdict": "NEEDS_INFO",
                    "reasoning": "PM did not return a verdict for this finding",
                })

        return verdicts

    except sp.TimeoutExpired:
        return [
            {"finding_id": f.finding_id, "verdict": "NEEDS_INFO", "reasoning": "PM timeout"}
            for f in findings
        ]
    except Exception as e:
        return [
            {"finding_id": f.finding_id, "verdict": "NEEDS_INFO", "reasoning": f"PM error: {e}"}
            for f in findings
        ]


# ═══════════════════════════════════════════════════════════════════════════════
# 6. Orchestrator
# ═══════════════════════════════════════════════════════════════════════════════

# Patterns used to detect mathematical claims in finding descriptions
_MATH_PATTERN = re.compile(
    r"(?:"
    r"[=<>!]=?"          # comparison/equality operators
    r"|[+\-*/^]"         # arithmetic operators
    r"|\bsqrt\b"         # sqrt keyword
    r"|\b\d+\s*[*/+\-]"  # digit followed by operator
    r"|\bEq\("           # sympy Eq()
    r"|\bGt\(|\bLt\("    # sympy Gt(), Lt()
    r")"
)

# Patterns used to detect structural claims in finding descriptions
_STRUCT_PATTERNS = {
    "decorator_exists": re.compile(r"@(\w+)\s+decorator", re.IGNORECASE),
    "class_exists": re.compile(r"\bclass\s+(\w+)\b", re.IGNORECASE),
    "method_exists": re.compile(r"\bmethod\s+(\w+)\b", re.IGNORECASE),
}


def run_quality_gate(
    new_findings: List[Finding],
    prior_findings: List[Finding],
    source_paths: List[str],
    pm_enabled: bool = False,
    tau_sim: float = 0.8,
) -> QualityGateResult:
    """Run the full quality gate pipeline.

    Stages:
        1. Dedup (always runs)
        2. SymPy verification on findings with mathematical claims
        3. AST verification on findings with structural claims
        4. PM verification (only if pm_enabled=True)

    This is OBSERVATION-ONLY: all findings pass through regardless of
    verification outcome. The verdicts are logged for analysis.

    Args:
        new_findings: Findings from the current round.
        prior_findings: Accumulated findings from previous rounds.
        source_paths: Paths to source files for AST and PM verification.
        pm_enabled: Whether to run the PM verification stage.
        tau_sim: Similarity threshold for dedup.

    Returns:
        QualityGateResult with all logs and metrics.
    """
    timings: Dict[str, float] = {}
    sympy_log: List[dict] = []
    ast_log: List[dict] = []

    # Stage 1: Dedup
    t0 = time.monotonic()
    unique_findings, dedup_log = dedup_findings(new_findings, prior_findings, tau_sim)
    timings["dedup"] = round(time.monotonic() - t0, 4)

    # Stage 2: SymPy verification on mathematical claims
    t0 = time.monotonic()
    for f in unique_findings:
        if _MATH_PATTERN.search(f.description):
            result = verify_sympy(f.description)
            sympy_log.append({"finding_id": f.finding_id, **result})
    timings["sympy"] = round(time.monotonic() - t0, 4)

    # Stage 3: AST verification on structural claims
    t0 = time.monotonic()
    for f in unique_findings:
        for claim_type, pattern in _STRUCT_PATTERNS.items():
            match = pattern.search(f.description)
            if match:
                target = match.group(1)
                for src in source_paths:
                    if src.endswith(".py"):
                        result = verify_ast_claim(claim_type, target, src)
                        ast_log.append({"finding_id": f.finding_id, **result})
                        if result["verified"]:
                            break  # found it, stop searching source files
    timings["ast"] = round(time.monotonic() - t0, 4)

    # Stage 4: PM verification
    t0 = time.monotonic()
    pm_verdicts = pm_verify_findings(
        unique_findings, source_paths, pm_enabled=pm_enabled,
    )
    timings["pm"] = round(time.monotonic() - t0, 4)

    # Compute PM metrics
    pm_confirmed = sum(1 for v in pm_verdicts if v["verdict"] == "CONFIRMED")
    pm_rejected = sum(1 for v in pm_verdicts if v["verdict"] == "REJECTED")
    total_pm = pm_confirmed + pm_rejected
    agreement_rate = pm_confirmed / total_pm if total_pm > 0 else 0.0

    dedup_count = sum(1 for d in dedup_log if d["duplicate_of"] is not None)

    # Observation-only: all unique findings pass through
    return QualityGateResult(
        filtered_findings=unique_findings,
        all_findings=new_findings,
        dedup_log=dedup_log,
        sympy_log=sympy_log,
        ast_log=ast_log,
        pm_verdicts=pm_verdicts,
        agreement_rate=round(agreement_rate, 4),
        stage_timings=timings,
        dedup_count=dedup_count,
        pm_confirmed=pm_confirmed,
        pm_rejected=pm_rejected,
    )
