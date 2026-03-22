#!/usr/bin/env python3
"""
Tutor-style sequential decomposition test for ft-004.

Each model maintains a PERSISTENT CONVERSATION — each step builds on the
model's own prior answers, exactly as a student accumulates understanding
at a blackboard. No step is presented to a fresh context.

CC (Opus 4.6) is the tutor/orchestrator/arbiter. Only Gemini and CX are
tested as students.

Usage:
    source .env && python3 bench/tutor_test.py
"""

import json
import os
import subprocess as sp
import sys
import time
from pathlib import Path

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
GEMINI_TIMEOUT = 300   # 5 min per step
CX_TIMEOUT = 900       # 15 min per step — CX at xhigh needs headroom


def err(msg):
    print(msg, file=sys.stderr, flush=True)


# ============================================================
# Model callers — persistent conversation variants
# ============================================================

class GeminiChat:
    """Multi-turn chat with Gemini via SDK. Context persists across turns."""

    def __init__(self):
        from google import genai
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.chat = self.client.chats.create(
            model="gemini-3.1-pro-preview",
            config=genai.types.GenerateContentConfig(
                max_output_tokens=32768,
                temperature=0.0,
            ),
        )

    def send(self, prompt: str, timeout: int = GEMINI_TIMEOUT) -> str:
        """Send a message in the ongoing conversation."""
        err(f"  [gemini] sending ({len(prompt)} chars) ...")
        t0 = time.monotonic()
        try:
            response = self.chat.send_message(prompt)
            elapsed = time.monotonic() - t0
            text = response.text or ""
            err(f"  [gemini] done ({elapsed:.1f}s, {len(text)} chars)")
            return text.strip()
        except Exception as e:
            raise RuntimeError(f"gemini failed: {e}")


class CodexChat:
    """Simulated multi-turn chat with Codex via codex exec.

    codex exec is stateless, so we accumulate the full conversation
    history and feed it back each time. The model sees all prior
    exchanges as context — equivalent to a persistent conversation.
    """

    def __init__(self):
        self.history = []  # list of (role, text) tuples

    def send(self, prompt: str, timeout: int = CX_TIMEOUT) -> str:
        """Send a message, including all prior conversation context."""
        self.history.append(("tutor", prompt))

        # Build the full conversation for CX to see
        if len(self.history) == 1:
            # First turn — just the prompt
            full_prompt = prompt
        else:
            parts = []
            parts.append(
                "This is a continuing mathematical tutorial. "
                "Your previous answers are shown below. "
                "Continue building on YOUR OWN prior work.\n"
            )
            for role, text in self.history[:-1]:
                label = "TUTOR" if role == "tutor" else "YOUR ANSWER"
                parts.append(f"--- {label} ---\n{text}\n")
            parts.append(f"--- TUTOR (current step) ---\n{prompt}\n")
            parts.append("Answer this step now, building on your prior work above.")
            full_prompt = "\n".join(parts)

        err(f"  [cx] sending ({len(full_prompt)} chars, "
            f"turn {len([h for h in self.history if h[0] == 'tutor'])}) ...")
        t0 = time.monotonic()

        import tempfile
        fd, out_path = tempfile.mkstemp(suffix=".txt", prefix="cx_")
        os.close(fd)
        try:
            result = sp.run(
                ["codex", "exec", "--output-last-message", out_path, full_prompt],
                capture_output=True, text=True, timeout=timeout
            )
            elapsed = time.monotonic() - t0
            text = Path(out_path).read_text().strip()
            if not text:
                raise RuntimeError(
                    f"codex exec returned empty output "
                    f"(exit {result.returncode}, "
                    f"stderr: {result.stderr[:200]})"
                )
            err(f"  [cx] done ({elapsed:.1f}s, {len(text)} chars)")
            self.history.append(("student", text))
            return text
        except sp.TimeoutExpired:
            raise RuntimeError(f"codex exec timed out after {timeout}s")
        finally:
            try:
                os.unlink(out_path)
            except OSError:
                pass


# ============================================================
# Tutor steps for ft-004
# ============================================================

STEPS = [
    ("step1", "Setting and understanding", """\
We are going to work through a mathematical construction together, \
one step at a time. I will set each step; you solve it. Do not jump \
ahead -- answer only what is asked.

Step 1 -- The setting:
We are working on the real interval [0, 1]. We need a function f: [0, 1] -> R \
that has two properties simultaneously:
(a) f is continuous at every point in [0, 1].
(b) f is differentiable at NO point in [0, 1].

What do these two properties mean together? Why is property (b) surprising \
given property (a)? Answer concisely."""),

    ("step2", "Construction parameters", """\
Good. Now we will use the Weierstrass function:
  f(x) = sum_{n=0}^{infinity} a^n cos(b^n pi x)

where the parameters must satisfy:
- 0 < a < 1
- b is a positive odd integer
- ab > 1 + 3*pi/2

Explain why EACH parameter condition is necessary:
(a) Why must 0 < a < 1?
(b) Why must b be odd?
(c) Why must ab > 1 + 3*pi/2?

Be precise. Do not attempt the proofs yet."""),

    ("step3", "Continuity proof", """\
Good. Now prove that f(x) = sum_{n=0}^{infinity} a^n cos(b^n pi x) \
is continuous on [0, 1], given 0 < a < 1.

Your proof must:
1. Show the series converges uniformly (not just pointwise).
2. Apply the theorem that a uniform limit of continuous functions is continuous.
3. Explicitly verify the hypotheses of any theorem you invoke.

Write the proof now. Be rigorous."""),

    ("step4a", "Construct sequence x_m", """\
Good. We now need to prove f is differentiable at NO point.

Take an arbitrary x in [0, 1]. We need a sequence x_m approaching x \
such that the difference quotient [f(x_m) - f(x)] / (x_m - x) diverges.

Your task for this step ONLY:
- Let k_m be the nearest integer to b^m * x, so b^m * x = k_m + e_m \
where -1/2 <= e_m < 1/2.
- Define x_m explicitly in terms of k_m and b^m.
- Choose the direction of approach so that |x_m - x| is controlled.
- Prove that x_m -> x as m -> infinity. State which condition on a, b \
you use for this.

Do not attempt any bounds on the difference quotient yet."""),

    ("step4b", "Bound the dominant term", """\
Good. Now use YOUR construction of x_m from the previous step.

Compute the difference quotient for the m-th term ONLY:
  [a^m cos(b^m pi x_m) - a^m cos(b^m pi x)] / (x_m - x)

Your task for this step ONLY:
- Substitute b^m * x_m and b^m * x using YOUR definitions of k_m, \
epsilon_m, e_m from step 4a.
- Use the fact that b is odd, so b^m is odd, so cos(odd integer * pi) = -1.
- Show the magnitude of this single-term quotient is at least C * (ab)^m.
- Find the explicit value of C.

Use the SAME variable names you defined in step 4a."""),

    ("step4c", "Bound head and tail", """\
Good. You showed the m-th term contributes magnitude at least C * (ab)^m.

Now bound the remaining terms. Use YOUR construction of x_m from step 4a \
and YOUR variable names throughout.

HEAD (indices n = 0, 1, ..., m-1):
- Apply the Mean Value Theorem to each cos term.
- Sum the resulting geometric series.
- Show the total head contribution is at most C' * (ab)^m. Find C'.

TAIL (indices n = m+1, m+2, ...):
- Use the fact that b is odd, so b^(n-m) is also odd for n > m.
- Show what sign each tail term's contribution has relative to the \
dominant term.
- Conclude whether the tail adds to or cancels the dominant term.

Important: do NOT switch variable names or construction method. \
Use exactly what you defined in steps 4a and 4b."""),

    ("step4d", "Combine and conclude", """\
Good. You have established:
- Dominant (n = m): magnitude >= C * (ab)^m  [your value of C from step 4b]
- Head (n < m): magnitude <= C' * (ab)^m  [your value of C' from step 4c]
- Tail (n > m): same sign as dominant  [from step 4c]

Now combine them to complete the proof:
1. Write the full difference quotient as dominant + tail - head.
2. Since tail reinforces dominant: |quotient| >= C*(ab)^m - C'*(ab)^m.
3. For divergence, need C > C'. Solve for the condition on ab.
4. Verify that you recover ab > 1 + 3*pi/2.
5. Since x was arbitrary, state the final conclusion.

Use YOUR values of C and C' from steps 4b and 4c."""),

    ("step5_verify", "Self-verification", """\
Now review your COMPLETE proof across all steps. You have the full \
construction in this conversation. Check for:

1. Consistency: did you use the same x_m construction throughout?
2. Are all bounds explicitly derived (no hand-waving)?
3. Are the conditions 0 < a < 1, b odd, ab > 1 + 3*pi/2 each used \
at least once, and only where needed?
4. Is there any gap between steps where an assumption is introduced \
without proof?
5. Are there any bounds that are looser than necessary?
6. Does the final conclusion follow logically from everything above?

List every issue you find. If the proof is complete and correct, \
state that explicitly with brief justification."""),
]


# ============================================================
# Runner
# ============================================================

def run_tutor_test(model_name: str, chat) -> dict:
    """Run the tutor decomposition with a persistent conversation."""
    err(f"\n{'='*60}")
    err(f"  TUTOR TEST: ft-004 with {model_name}")
    err(f"{'='*60}")

    results = {}
    t_total = time.monotonic()

    for key, label, prompt in STEPS:
        err(f"\n  --- {label} ---")
        try:
            r = chat.send(prompt)
            results[key] = r
            err(f"  {label} complete.")
        except Exception as e:
            err(f"  {label} FAILED: {e}")
            results[f"{key}_error"] = str(e)
            results["total_time"] = round(time.monotonic() - t_total, 1)
            return results

    elapsed = time.monotonic() - t_total
    results["total_time"] = round(elapsed, 1)
    err(f"\n  {model_name} COMPLETE: {elapsed:.1f}s total")
    return results


def main():
    err("TUTOR-STYLE DECOMPOSITION TEST v2: ft-004")
    err("Persistent conversations — each model accumulates context")
    err(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    all_results = {}

    # CC is tutor/orchestrator/arbiter — not a student.
    models = [
        ("Gemini 3.1 Pro", lambda: GeminiChat()),
        ("Codex 5.3 (CX)", lambda: CodexChat()),
    ]

    for name, make_chat in models:
        try:
            chat = make_chat()
            all_results[name] = run_tutor_test(name, chat)
        except Exception as e:
            err(f"  {name} FATAL: {e}")
            all_results[name] = {"fatal_error": str(e)}

    # Save results
    out_dir = Path("bench/results/tutor_test")
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"ft-004_tutor_v2_{timestamp}.json"
    out_path.write_text(json.dumps(all_results, indent=2) + "\n")
    err(f"\nResults saved to: {out_path}")

    # Also save as latest for easy access
    latest = out_dir / "ft-004_tutor_v2_latest.json"
    latest.write_text(json.dumps(all_results, indent=2) + "\n")

    # Print summary
    err(f"\n{'='*60}")
    err(f"  SUMMARY")
    err(f"{'='*60}")
    all_keys = [k for k, _, _ in STEPS]
    for name, r in all_results.items():
        total = r.get("total_time", "?")
        steps_ok = sum(1 for k in all_keys if k in r)
        steps_fail = sum(1 for k in r if k.endswith("_error"))
        err(f"  {name}: {steps_ok}/{len(all_keys)} steps complete, "
            f"{steps_fail} failures, {total}s")


if __name__ == "__main__":
    main()
