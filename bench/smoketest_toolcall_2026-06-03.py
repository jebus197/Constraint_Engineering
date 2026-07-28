"""Tool-access spike (2026-06-03): does each model route actually CALL tools and
use the result? Single `execute_python` tool with the full local STEM toolset
behind it. Prompt requires tool use (answer not memorisable at a glance), so a
correct answer is evidence of genuine tool use.

Routes tested:
  - OpenRouter openai/gpt-5.5  (cx / cgpt)   — OpenAI tools API
  - OpenRouter google/gemini-3.1-pro-preview — OpenAI tools API
  - DeepSeek   deepseek-v4-pro                — OpenAI-compatible tools API
  - CC2 (claude CLI)                          — native --allowedTools (Bash)

Smoke test only — NOT wired into the runner yet.
"""
from __future__ import annotations
import json, os, subprocess, sys, tempfile, time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
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

# The verification task: count primes below 100000. Correct answer = 9592.
# Not memorisable at a glance; a correct number is strong evidence of real
# execution. The model is told it MUST use the tool.
TASK = (
    "Using the execute_python tool, compute the exact number of prime numbers "
    "strictly below 100000. You MUST run code with the tool (e.g. via sympy) — "
    "do NOT answer from memory or estimate. After you have the tool's result, "
    "reply with ONLY the integer count and nothing else."
)
EXPECTED = "9592"

EXECUTE_TOOL = {
    "type": "function",
    "function": {
        "name": "execute_python",
        "description": (
            "Execute a Python 3 snippet and return its stdout/stderr. The full "
            "local STEM toolset is importable: sympy, numpy, scipy, statsmodels, "
            "mpmath, z3, sklearn, networkx, pandas, plus stdlib (ast, math, etc.). "
            "Print results you want to see."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python source to run."}
            },
            "required": ["code"],
        },
    },
}


def execute_python(code: str, timeout: int = 30) -> str:
    """Run a Python snippet, return combined stdout/stderr (truncated)."""
    f = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False)
    f.write(code); f.close()
    try:
        r = subprocess.run([sys.executable, f.name], capture_output=True,
                           text=True, timeout=timeout)
        out = (r.stdout or "") + (("\n[stderr]\n" + r.stderr) if r.stderr else "")
        return out.strip()[:4000] or "(no output)"
    except subprocess.TimeoutExpired:
        return f"[timeout after {timeout}s]"
    except Exception as e:  # noqa: BLE001
        return f"[error: {type(e).__name__}: {e}]"
    finally:
        try: os.unlink(f.name)
        except OSError: pass


def run_openai_toolcall(client, model_id: str, max_iters: int = 5) -> dict:
    """Run the OpenAI tool-call loop. Returns {tool_calls, final, ran_code, ok}."""
    messages = [
        {"role": "system", "content": "You are a careful STEM verifier. Use tools to check facts; never guess."},
        {"role": "user", "content": TASK},
    ]
    n_tool_calls = 0
    ran_code = False
    last_tool_out = ""
    final = ""
    for _ in range(max_iters):
        resp = client.chat.completions.create(
            model=model_id, messages=messages, tools=[EXECUTE_TOOL],
            tool_choice="auto", temperature=0.0, max_tokens=4096, timeout=180,
        )
        msg = resp.choices[0].message
        tcs = getattr(msg, "tool_calls", None) or []
        if tcs:
            n_tool_calls += len(tcs)
            messages.append({"role": "assistant", "content": msg.content or "",
                             "tool_calls": [tc.model_dump() for tc in tcs]})
            for tc in tcs:
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                code = args.get("code", "")
                out = execute_python(code) if code else "[no code provided]"
                if code: ran_code = True
                last_tool_out = out
                messages.append({"role": "tool", "tool_call_id": tc.id,
                                 "content": out[:4000]})
        else:
            final = (msg.content or "").strip()
            break
    ok = EXPECTED in final or EXPECTED in last_tool_out
    return {"tool_calls": n_tool_calls, "ran_code": ran_code,
            "final": final[:120], "tool_out": last_tool_out[:120], "ok": ok}


def test_openai_route(name: str, base_url: str, key_env: str, model_id: str) -> dict:
    import openai
    key = os.environ.get(key_env)
    if not key:
        return {"route": name, "error": f"{key_env} not set"}
    client = openai.OpenAI(base_url=base_url, api_key=key, timeout=200)
    t0 = time.time()
    try:
        r = run_openai_toolcall(client, model_id)
        r["route"] = name; r["elapsed_s"] = round(time.time()-t0, 1)
        return r
    except Exception as e:  # noqa: BLE001
        return {"route": name, "error": f"{type(e).__name__}: {e}",
                "elapsed_s": round(time.time()-t0, 1)}


def test_cc2_cli() -> dict:
    """CC2 via claude CLI: native tools (Bash). Allow it to run code."""
    t0 = time.time()
    cmd = ["claude", "-p", TASK + "\n\nYou have Bash/Read tools — use them to run Python.",
           "--allowedTools", "Bash", "--max-turns", "8"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
        out = (r.stdout or "").strip()
        return {"route": "cc2-cli", "final": out[-120:], "ok": EXPECTED in out,
                "elapsed_s": round(time.time()-t0, 1)}
    except Exception as e:  # noqa: BLE001
        return {"route": "cc2-cli", "error": f"{type(e).__name__}: {e}",
                "elapsed_s": round(time.time()-t0, 1)}


def main():
    print("=== tool-access spike (expected answer: 9592) ===\n")
    print("local execute_python self-check:",
          execute_python("from sympy import primerange; print(len(list(primerange(2,100000))))"))
    print()
    results = []
    results.append(test_openai_route("openrouter:gpt-5.5",
        "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY", "openai/gpt-5.5"))
    results.append(test_openai_route("openrouter:gemini-3.1-pro",
        "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY", "google/gemini-3.1-pro-preview"))
    results.append(test_openai_route("deepseek:v4-pro",
        "https://api.deepseek.com", "DEEPSEEK_API_KEY", "deepseek-v4-pro"))
    results.append(test_cc2_cli())
    print("\n=== RESULTS ===")
    for r in results:
        print(json.dumps(r, default=str))
    Path("/tmp/toolcall_spike_results.json").write_text(json.dumps(results, indent=2, default=str))
    print("\nsaved: /tmp/toolcall_spike_results.json")


if __name__ == "__main__":
    sys.exit(main())
