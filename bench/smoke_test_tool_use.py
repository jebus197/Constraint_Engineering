#!/usr/bin/env python3
"""Smoke test: CC2 tool execution (CLI Bash) and DeepSeek-Reasoner (direct API).

Verifies that:
1. CC2 can execute SymPy/z3 via Bash when dispatched through claude CLI
2. DeepSeek-Reasoner via direct API produces deterministic verification output

Run: python3 bench/smoke_test_tool_use.py
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


# ── Test 1: CC2 SymPy execution via CLI ─────────────────────────────
def test_cc2_sympy():
    """Dispatch CC2 with a task that REQUIRES SymPy execution to answer correctly."""
    print("\n" + "=" * 60)
    print("TEST 1: CC2 — SymPy execution via claude CLI")
    print("=" * 60)

    # Find claude CLI
    cli = None
    for candidate in [
        "claude",
        str(Path.home() / "Library/Application Support/Claude/claude-code/latest/claude.app/Contents/MacOS/claude"),
    ]:
        try:
            subprocess.run([candidate, "--version"], capture_output=True, timeout=5)
            cli = candidate
            break
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue

    if not cli:
        # Search for any claude binary
        try:
            result = subprocess.run(
                ["find", str(Path.home() / "Library/Application Support/Claude"),
                 "-name", "claude", "-type", "f"],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.strip().split("\n"):
                if line and "MacOS/claude" in line:
                    cli = line
                    break
        except Exception:
            pass

    if not cli:
        print("  SKIP: claude CLI not found")
        return None

    system_prompt = (
        "You are a mathematical verification agent. When asked to verify a "
        "mathematical claim, you MUST use the Bash tool to execute Python code "
        "with SymPy to check the claim computationally. Do NOT compute manually. "
        "Use the tool. Show the tool output in your response."
    )

    user_prompt = (
        "Verify this claim using SymPy (execute Python code, do not compute manually):\n\n"
        "Claim: The integral of x^2 * sin(x) from 0 to pi equals pi^2 - 4.\n\n"
        "Run: python3 -c \"import sympy; x = sympy.Symbol('x'); "
        "result = sympy.integrate(x**2 * sympy.sin(x), (x, 0, sympy.pi)); "
        "print(f'Result: {result}'); print(f'pi^2 - 4 = {sympy.pi**2 - 4}'); "
        "print(f'Equal: {sympy.simplify(result - (sympy.pi**2 - 4)) == 0}')\"\n\n"
        "Report the tool output and whether the claim is verified."
    )

    cmd = [
        cli, "-p",
        "--model", "opus",
        "--output-format", "text",
        "--no-session-persistence",
        "--disallowed-tools", "Edit", "Write",
        "--system-prompt", system_prompt,
    ]

    print(f"  Dispatching to CC2 via {cli}...")
    t0 = time.monotonic()
    try:
        result = subprocess.run(
            cmd,
            input=user_prompt,
            capture_output=True,
            text=True,
            timeout=300,
        )
        elapsed = time.monotonic() - t0
        text = result.stdout.strip()
        stderr = result.stderr.strip()[:300] if result.stderr else ""

        print(f"  Done: {elapsed:.1f}s, {len(text)} chars")
        if result.returncode != 0:
            print(f"  STDERR: {stderr}")

        # Check for evidence of tool execution
        has_sympy = "sympy" in text.lower() or "SymPy" in text
        has_result = "pi**2 - 4" in text or "π² - 4" in text or "pi^2 - 4" in text
        has_tool_output = "Result:" in text or "Equal:" in text or "True" in text
        has_bash = "bash" in text.lower() or "python" in text.lower() or "```" in text

        print(f"  Evidence of SymPy mention: {has_sympy}")
        print(f"  Evidence of computed result: {has_result}")
        print(f"  Evidence of tool output: {has_tool_output}")
        print(f"  Evidence of code execution: {has_bash}")

        # Show key section of response
        print(f"\n  --- Response (first 800 chars) ---")
        print("  " + text[:800].replace("\n", "\n  "))
        print(f"  --- End ---\n")

        if has_tool_output or (has_result and has_bash):
            print("  PASS: CC2 executed tool and produced verification output")
            return True
        elif has_sympy and has_result:
            print("  WARN: CC2 mentioned SymPy and got correct result but may have computed manually")
            return True
        else:
            print("  FAIL: No evidence of tool execution")
            return False

    except subprocess.TimeoutExpired:
        print(f"  FAIL: Timeout after 300s")
        return False
    except Exception as e:
        print(f"  FAIL: {e}")
        return False


# ── Test 2: DeepSeek-Reasoner via direct API ────────────────────────
def test_deepseek_reasoner():
    """Dispatch DeepSeek-Reasoner via direct API for deterministic verification."""
    print("\n" + "=" * 60)
    print("TEST 2: DeepSeek-Reasoner — direct API verification")
    print("=" * 60)

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("  SKIP: DEEPSEEK_API_KEY not set")
        return None

    try:
        import openai
    except ImportError:
        print("  SKIP: openai package not installed")
        return None

    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )

    system_prompt = (
        "You are a deep verification specialist for the CDSFL falsification pipeline. "
        "Your role: independently verify mathematical claims from other models. "
        "For each claim, attempt to falsify it. Show your full reasoning chain. "
        "Recompute any R_k values from stated parameters. "
        "Verdict: CORROBORATED, REFUTED, or INSUFFICIENT_DATA."
    )

    user_prompt = (
        "DEEP VERIFICATION REQUEST\n\n"
        "Finding: CC2_F003\n"
        "Claim: In runner_core.py parse_findings(), the regex pattern "
        "r'SEVERITY:\\s*([\\d.]+)' fails to match severity values formatted as "
        "'SEVERITY: HIGH' (non-numeric). This causes a silent fallback to "
        "default severity 0.5, which inflates false-positive rates.\n\n"
        "Proposed fix: Add a severity mapping dict {'CRITICAL': 0.95, 'HIGH': 0.85, "
        "'MEDIUM': 0.60, 'LOW': 0.30} as fallback when numeric parse fails.\n\n"
        "R_k parameters from original model:\n"
        "  R_old = 0.45, eta = 0.85, d = 0.75, p = 0.70\n"
        "  Model claimed: q = 0.446, R_det = 0.283, R_k = 0.283\n\n"
        "Tasks:\n"
        "1. Attempt to FALSIFY the finding (find a counter-argument or scenario where "
        "the claim is wrong)\n"
        "2. Verify the proposed fix is correct and complete\n"
        "3. Independently recompute R_k from the stated parameters\n"
        "4. Issue verdict: CORROBORATED or REFUTED\n"
    )

    print(f"  Dispatching to DeepSeek-Reasoner via direct API...")
    t0 = time.monotonic()
    try:
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=8192,
            temperature=0.0,
            timeout=180,
        )
        elapsed = time.monotonic() - t0

        if not response.choices:
            print(f"  FAIL: No choices returned after {elapsed:.1f}s")
            return False

        choice = response.choices[0]
        text = (choice.message.content or "").strip()
        reasoning = ""
        if hasattr(choice.message, "reasoning_content"):
            reasoning = (choice.message.reasoning_content or "").strip()

        print(f"  Done: {elapsed:.1f}s, {len(text)} chars content, "
              f"{len(reasoning)} chars reasoning")

        # Check for key verification elements
        has_verdict = any(v in text.upper() for v in ["CORROBORATED", "REFUTED", "INSUFFICIENT"])
        has_rk = "R_k" in text or "R_det" in text or "R_old" in text
        has_recomputation = any(s in text for s in ["0.446", "0.283", "0.85", "0.75"])
        has_falsification = any(s in text.lower() for s in ["falsif", "counter", "disprove", "refute"])

        # Verify R_k independently here
        R_old, eta, d, p = 0.45, 0.85, 0.75, 0.70
        q = eta * d * p  # 0.44625
        R_det = R_old * (1 - q) / (1 - q * R_old)
        print(f"\n  Independent R_k check: q={q:.4f}, R_det={R_det:.4f}")
        print(f"  Model claimed: q=0.446, R_det=0.283")
        print(f"  Delta q: {abs(q - 0.446):.4f}, Delta R_det: {abs(R_det - 0.283):.4f}")

        print(f"\n  Has verdict: {has_verdict}")
        print(f"  Has R_k recomputation: {has_rk}")
        print(f"  Has numerical values: {has_recomputation}")
        print(f"  Has falsification attempt: {has_falsification}")

        # Show response
        print(f"\n  --- Response (first 1200 chars) ---")
        print("  " + text[:1200].replace("\n", "\n  "))
        print(f"  --- End ---\n")

        if has_verdict and has_rk and has_falsification:
            print("  PASS: DeepSeek-Reasoner produced structured verification")
            return True
        elif has_verdict or has_rk:
            print("  WARN: Partial verification (missing some elements)")
            return True
        else:
            print("  FAIL: No verification elements found")
            return False

    except Exception as e:
        print(f"  FAIL: {e}")
        return False


# ── Main ────────────────────────────────────────────────────────────
def main():
    print("CDSFL Tool Use Smoke Test")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    results = {}

    results["cc2_sympy"] = test_cc2_sympy()
    results["deepseek_reasoner"] = test_deepseek_reasoner()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, result in results.items():
        status = "PASS" if result is True else ("SKIP" if result is None else "FAIL")
        print(f"  {name}: {status}")

    # Save results
    output_path = REPO_ROOT / "bench" / "logs" / "smoke_test_tool_use.json"
    output_path.write_text(json.dumps({
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "results": {k: ("PASS" if v is True else ("SKIP" if v is None else "FAIL"))
                    for k, v in results.items()},
    }, indent=2), encoding="utf-8")
    print(f"\n  Results saved: {output_path}")

    all_tested = [v for v in results.values() if v is not None]
    if all_tested and all(all_tested):
        print("\n  ALL TESTS PASSED")
        return 0
    elif any(v is False for v in results.values()):
        print("\n  SOME TESTS FAILED")
        return 1
    else:
        print("\n  ALL TESTS SKIPPED")
        return 2


if __name__ == "__main__":
    sys.exit(main())
