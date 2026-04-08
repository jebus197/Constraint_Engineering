#!/usr/bin/env python3
"""
Bidirectional P-pass interactive smoke test.

Full CDSFL+HIL loop: CC and reviewer confer as equals, with SymPy
as arbiter on verifiable claims. Each step is a cycle, not a lecture.

1. CC presents step + SymPy verification of any claims
2. Reviewer responds with understanding + their own findings/challenges
3. CC P-passes reviewer's findings (SymPy verifies their claims)
4. CC feeds back: correct/incorrect with SymPy evidence
5. Reviewer P-passes CC's feedback — can disagree with evidence
6. Cycle until convergence on that step (max 3 exchanges per step)
7. Move to next step

SymPy is the tiebreaker. If both models disagree and SymPy resolves
it, SymPy wins. If SymPy can't resolve it, the disagreement is
recorded and deferred to human review.

Usage:
    source ../.env && python3 bench/interactive_smoke.py
"""

import json
import os
import subprocess as sp
import sys
import time
from pathlib import Path

# Load .env
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                if line.startswith("export "):
                    line = line[7:]
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())

if "ANTHROPIC_API_KEY" in os.environ:
    del os.environ["ANTHROPIC_API_KEY"]

MAX_EXCHANGES_PER_STEP = 3  # convergence cap per step


def err(msg):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", file=sys.stderr, flush=True)


def call_cc(prompt: str, timeout: int = 600) -> str:
    t0 = time.monotonic()
    result = sp.run(
        ["claude", "-p", "--model", "claude-opus-4-6", "--output-format", "text"],
        input=prompt, capture_output=True, text=True, timeout=timeout
    )
    elapsed = time.monotonic() - t0
    if result.returncode != 0:
        raise RuntimeError(f"claude failed (exit {result.returncode})")
    err(f"  [cc] done ({elapsed:.1f}s, {len(result.stdout)} chars)")
    return result.stdout.strip()


def verify_sympy(claim: str) -> dict:
    """Verify a mathematical claim via SymPy in subprocess sandbox."""
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
            ["python3", "-c", code],
            capture_output=True, text=True, timeout=10
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


# ============================================================
# Tutorial steps — each is a topic for bidirectional P-pass
# ============================================================

STEPS = [
    {
        "label": "Prior knowledge",
        "cc_opens": (
            "We are going to review a proof of the Erdos-Szekeres theorem "
            "together as equals. I will present each step. You will challenge "
            "anything you disagree with. If we disagree on a mathematical claim, "
            "SymPy will arbitrate.\n\n"
            "Before I show the proof: what do you know about this theorem? "
            "What are the standard proof techniques? What mistakes are common?"
        ),
        "sympy_claims": [],
    },
    {
        "label": "Labelling scheme",
        "cc_opens": (
            "Here is the labelling scheme. For each element a_k (k=1..n^2+1):\n"
            "  i_k = length of longest increasing subsequence ending at a_k\n"
            "  d_k = length of longest decreasing subsequence ending at a_k\n\n"
            "Claim: i_k >= 1 and d_k >= 1 for all k.\n"
            "Claim: each element considered alone forms subsequences of length 1.\n\n"
            "Do you agree? Challenge anything you find incomplete or wrong."
        ),
        "sympy_claims": ["Ge(1, 1)"],
    },
    {
        "label": "Injectivity of label pairs",
        "cc_opens": (
            "Key claim: no two elements share the same label pair (i_j, d_j) != (i_k, d_k) for j != k.\n\n"
            "Argument: take j < k. Elements are distinct, so a_j < a_k or a_j > a_k.\n"
            "  If a_j < a_k: any increasing subseq ending at a_j can be extended by a_k, "
            "so i_k >= i_j + 1, giving i_k > i_j.\n"
            "  If a_j > a_k: same for decreasing, d_k >= d_j + 1, giving d_k > d_j.\n"
            "Either way the pairs differ.\n\n"
            "P-pass this. Is the argument complete? Any hidden assumptions? "
            "Does it rely on anything unstated? Challenge or confirm."
        ),
        "sympy_claims": [],
    },
    {
        "label": "Pigeonhole contradiction",
        "cc_opens": (
            "If all i_k <= n and all d_k <= n, there are at most n*n = n^2 "
            "possible pairs. But we have n^2+1 elements with unique pairs. Contradiction.\n\n"
            "Therefore some i_k >= n+1 or some d_k >= n+1.\n\n"
            "Claim: n^2 + 1 > n^2 for all positive n.\n"
            "Claim: i_k >= n+1 means there EXISTS an increasing subsequence of length n+1 "
            "(not just that the label has that value).\n\n"
            "P-pass both claims. The second is where proofs often hand-wave. "
            "Is it justified? Does i_k >= n+1 constructively give us a subsequence?"
        ),
        "sympy_claims": ["Gt(n**2 + 1, n**2)"],
    },
    {
        "label": "Tightness construction",
        "cc_opens": (
            "Tightness for n=4. Consider 4x4 grid, rows read right to left:\n"
            "  4, 3, 2, 1, 8, 7, 6, 5, 12, 11, 10, 9, 16, 15, 14, 13\n\n"
            "16 = 4^2 elements.\n\n"
            "Claims:\n"
            "1. No increasing subsequence of length 5 exists.\n"
            "2. No decreasing subsequence of length 5 exists.\n"
            "3. A monotone subsequence of length exactly 4 exists.\n\n"
            "Verify or refute each. Don't take my word for it — check."
        ),
        "sympy_claims": ["Eq(4**2, 16)"],
    },
    {
        "label": "Final findings",
        "cc_opens": (
            "We have walked through the entire proof interactively. "
            "Now produce your final findings.\n\n"
            "For each finding, state:\n"
            "- The specific claim you are challenging or confirming\n"
            "- HARD (mathematical necessity) or SOFT (style/robustness)\n"
            "- Your confidence (0.0 to 1.0)\n"
            "- A verifiable mathematical expression if applicable\n"
            "- Whether you and I agreed or disagreed during the tutorial\n\n"
            "Be thorough. Include everything we discussed, including "
            "any points where you challenged me and were right."
        ),
        "sympy_claims": [],
    },
]


def run_bidirectional_review(model_name: str, send_fn):
    """Full bidirectional P-pass dialogue."""
    err(f"\n{'='*60}")
    err(f"  BIDIRECTIONAL P-PASS: {model_name}")
    err(f"{'='*60}")

    results = {"model": model_name, "steps": [], "total_time": 0}
    t_total = time.monotonic()

    for i, step in enumerate(STEPS):
        err(f"\n  === Step {i+1}: {step['label']} ===")
        step_data = {
            "step": i+1, "label": step["label"],
            "exchanges": [], "converged": False,
            "sympy_results": [],
        }

        # SymPy pre-verification of CC's claims
        for claim in step.get("sympy_claims", []):
            sv = verify_sympy(claim)
            step_data["sympy_results"].append(sv)
            err(f"  [sympy] {claim} -> {sv['result'][:60]}")

        # Exchange 1: CC opens, reviewer responds
        cc_message = step["cc_opens"]
        if step_data["sympy_results"]:
            cc_message += "\n\n[SymPy verification of my claims: " + "; ".join(
                f"{c} = {sv['result'][:40]}"
                for c, sv in zip(step["sympy_claims"], step_data["sympy_results"])
            ) + "]"

        err(f"  [exchange 1] CC presents ({len(cc_message)} chars)")
        try:
            reviewer_response = send_fn(cc_message)
            err(f"  [exchange 1] Reviewer responds ({len(reviewer_response)} chars)")
        except Exception as e:
            err(f"  [exchange 1] Reviewer FAILED: {e}")
            step_data["exchanges"].append({"error": str(e)})
            results["steps"].append(step_data)
            continue

        step_data["exchanges"].append({
            "cc": cc_message[:500],
            "reviewer": reviewer_response[:500],
        })

        # Exchanges 2-N: CC P-passes reviewer, reviewer P-passes CC
        prev_reviewer = reviewer_response
        for ex_num in range(2, MAX_EXCHANGES_PER_STEP + 1):
            # CC P-passes reviewer's response
            ppass_prompt = (
                f"The reviewer responded to your presentation of '{step['label']}':\n\n"
                f"{prev_reviewer[:3000]}\n\n"
                "P-pass their response:\n"
                "1. Are their observations correct?\n"
                "2. Did they find anything you missed?\n"
                "3. Are any of their claims wrong? If so, state a verifiable expression.\n"
                "4. Do you AGREE (converged) or DISAGREE (need another exchange)?\n\n"
                "If they raised a mathematical claim, state it in SymPy-parseable form "
                "so we can verify. Reply with CONVERGED if you agree on all points, "
                "or DISAGREE: [reason] if not."
            )

            try:
                cc_ppass = call_cc(ppass_prompt)
                err(f"  [exchange {ex_num}] CC P-passes ({len(cc_ppass)} chars)")
            except Exception as e:
                err(f"  [exchange {ex_num}] CC P-pass FAILED: {e}")
                break

            # Extract any SymPy claims from CC's P-pass
            # Look for patterns like "verify: expression" or expressions in backticks
            import re
            claims_in_ppass = re.findall(r'verify:\s*`?([^`\n]+)`?', cc_ppass, re.I)
            for claim in claims_in_ppass[:3]:  # max 3 claims per exchange
                sv = verify_sympy(claim.strip())
                step_data["sympy_results"].append(sv)
                err(f"  [sympy] {claim.strip()[:40]} -> {sv['result'][:60]}")

            # Check convergence
            if "CONVERGED" in cc_ppass.upper():
                err(f"  [exchange {ex_num}] CC says CONVERGED")
                step_data["converged"] = True
                step_data["exchanges"].append({
                    "cc_ppass": cc_ppass[:500],
                    "converged_by": "cc",
                })
                break

            # Reviewer P-passes CC's feedback
            reviewer_ppass_prompt = (
                f"The tutor evaluated your response:\n\n"
                f"{cc_ppass[:3000]}\n\n"
            )
            if claims_in_ppass:
                sympy_feedback = "; ".join(
                    f"{c.strip()[:30]} = {verify_sympy(c.strip())['result'][:30]}"
                    for c in claims_in_ppass[:3]
                )
                reviewer_ppass_prompt += f"[SymPy arbitration: {sympy_feedback}]\n\n"

            reviewer_ppass_prompt += (
                "P-pass their evaluation:\n"
                "1. Do you accept their corrections?\n"
                "2. Do you maintain any of your challenges? If so, provide evidence.\n"
                "3. Do you have NEW findings based on this exchange?\n"
                "Reply with CONVERGED if you agree on all points, or state your "
                "remaining disagreements with evidence."
            )

            try:
                reviewer_ppass = send_fn(reviewer_ppass_prompt)
                err(f"  [exchange {ex_num}] Reviewer P-passes ({len(reviewer_ppass)} chars)")
            except Exception as e:
                err(f"  [exchange {ex_num}] Reviewer P-pass FAILED: {e}")
                break

            step_data["exchanges"].append({
                "cc_ppass": cc_ppass[:500],
                "reviewer_ppass": reviewer_ppass[:500],
                "sympy_claims": [s['result'][:60] for s in step_data["sympy_results"][-3:]],
            })

            if "CONVERGED" in reviewer_ppass.upper():
                err(f"  [exchange {ex_num}] Reviewer says CONVERGED")
                step_data["converged"] = True
                break

            prev_reviewer = reviewer_ppass

        if not step_data["converged"]:
            err(f"  [step {i+1}] Did not converge in {MAX_EXCHANGES_PER_STEP} exchanges — recording disagreement")

        results["steps"].append(step_data)

    elapsed = time.monotonic() - t_total
    results["total_time"] = round(elapsed, 1)
    err(f"\n  {model_name} COMPLETE: {elapsed:.1f}s, "
        f"{sum(1 for s in results['steps'] if s.get('converged'))}/6 steps converged")
    return results


# ============================================================
# Model callers
# ============================================================

class DeepSeekChat:
    def __init__(self):
        from openai import OpenAI
        self.client = OpenAI(
            api_key=os.environ.get("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        self.history = [{"role": "system", "content":
            "You are a mathematical reviewer in a bidirectional P-pass dialogue. "
            "Challenge claims you disagree with. Provide evidence. State CONVERGED "
            "when you agree on all points. Do not be deferential — if you think "
            "the tutor is wrong, say so with evidence."}]

    def send(self, prompt: str) -> str:
        self.history.append({"role": "user", "content": prompt})
        response = self.client.chat.completions.create(
            model="deepseek-chat", messages=self.history,
            max_tokens=4096, temperature=0.0,
        )
        if not response.choices:
            raise RuntimeError("API returned no choices (possible upstream 500)")
        text = response.choices[0].message.content.strip()
        self.history.append({"role": "assistant", "content": text})
        return text


class CXChat:
    def __init__(self):
        self.history = []

    def send(self, prompt: str) -> str:
        self.history.append(("tutor", prompt))
        parts = [
            "You are in a bidirectional P-pass dialogue. Challenge claims you "
            "disagree with. Provide evidence. State CONVERGED when you agree. "
            "Do not be deferential.\n"
        ]
        # Keep last 3 exchanges full, summarise earlier
        full_start = max(0, len(self.history) - 6)
        for role, text in self.history[full_start:]:
            label = "TUTOR/CC" if role == "tutor" else "YOUR RESPONSE"
            parts.append(f"--- {label} ---\n{text[:2000]}\n")
        parts.append("Respond now.")
        full = "\n".join(parts)

        import tempfile
        fd, out = tempfile.mkstemp(suffix=".txt", prefix="cx_")
        os.close(fd)
        try:
            result = sp.run(
                ["codex", "exec", "--output-last-message", out, "-"],
                input=full,
                capture_output=True, text=True, timeout=300
            )
            text = Path(out).read_text().strip()
            if not text:
                text = result.stdout.strip()
            if not text:
                raise RuntimeError("codex exec returned empty")
            self.history.append(("reviewer", text))
            return text
        finally:
            Path(out).unlink(missing_ok=True)


class GeminiChat:
    def __init__(self):
        from google import genai
        key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.client = genai.Client(api_key=key)
        self.chat = self.client.chats.create(
            model="gemini-3.1-pro-preview",
            config=genai.types.GenerateContentConfig(
                max_output_tokens=4096, temperature=0.0),
        )

    def send(self, prompt: str) -> str:
        response = self.chat.send_message(prompt)
        return (response.text or "").strip()


class ChatGPTChat:
    def __init__(self):
        self.history = []

    def send(self, prompt: str) -> str:
        self.history.append(("user", prompt))
        # chatgpt CLI doesn't support multi-turn natively,
        # so accumulate context like CX
        parts = [
            "You are in a bidirectional P-pass dialogue. Challenge claims you "
            "disagree with. State CONVERGED when you agree.\n"
        ]
        full_start = max(0, len(self.history) - 6)
        for role, text in self.history[full_start:]:
            label = "TUTOR/CC" if role == "user" else "YOUR RESPONSE"
            parts.append(f"--- {label} ---\n{text[:2000]}\n")
        parts.append("Respond now.")
        full = "\n".join(parts)

        result = sp.run(
            ["chatgpt", "-q", "--model", "gpt-5.4"],
            input=full, capture_output=True, text=True, timeout=120
        )
        text = result.stdout.strip()
        if not text:
            raise RuntimeError(f"chatgpt empty (exit {result.returncode})")
        self.history.append(("assistant", text))
        return text


def main():
    err("BIDIRECTIONAL P-PASS SMOKE TEST")
    err("ft-001 × CDSFL+HIL × 4 reviewers × interactive dialogue")
    err(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    all_results = {"task": "ft-001", "protocol": "bidirectional_ppass", "models": {}}

    models = [
        ("DeepSeek V3.2", lambda: DeepSeekChat()),
        ("Codex 5.3", lambda: CXChat()),
        ("Gemini 3.1 Pro", lambda: GeminiChat()),
        ("ChatGPT 5.4", lambda: ChatGPTChat()),
    ]

    for name, make_chat in models:
        try:
            chat = make_chat()
            result = run_bidirectional_review(name, chat.send)
            all_results["models"][name] = result
        except Exception as e:
            err(f"  {name} FATAL: {e}")
            all_results["models"][name] = {"fatal_error": str(e)}

    # Save
    out_dir = Path(__file__).parent / "results" / "interactive_smoke"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"bidirectional_ppass_{ts}.json"
    out_path.write_text(json.dumps(all_results, indent=2) + "\n")
    err(f"\nResults saved to: {out_path}")

    # Summary
    err(f"\n{'='*60}")
    err(f"  SUMMARY")
    err(f"{'='*60}")
    for name, r in all_results["models"].items():
        if "fatal_error" in r:
            err(f"  {name}: FATAL — {r['fatal_error'][:80]}")
        else:
            steps = r.get("steps", [])
            converged = sum(1 for s in steps if s.get("converged"))
            total_exchanges = sum(len(s.get("exchanges", [])) for s in steps)
            sympy_checks = sum(len(s.get("sympy_results", [])) for s in steps)
            err(f"  {name}: {converged}/6 converged, {total_exchanges} exchanges, "
                f"{sympy_checks} SymPy checks, {r.get('total_time', '?')}s")


if __name__ == "__main__":
    main()
