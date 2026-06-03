"""Falsifier-carrying smoke test (2026-06-03): can a model, given the execute
tool + the reframed directive, (1) find a real defect, (2) attach a RUNNABLE
falsifier that demonstrates it, (3) have run it itself to confirm — and can the
RUNNER independently re-run that falsifier to decide the verdict (no vote)?

Controlled target with a KNOWN bug (clamp returns lo instead of hi when x>hi),
so ground truth is known. Tests the core of the "tools decide" fix end-to-end:
model uses tool -> attaches falsifier -> runner re-runs -> verdict.

Smoke test only — NOT wired into the runner yet.
"""
from __future__ import annotations
import json, os, re, subprocess, sys, tempfile, time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
_env = REPO_ROOT / ".env"
if _env.exists():
    for ln in _env.read_text().splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"): continue
        ln = ln[7:] if ln.startswith("export ") else ln
        if "=" in ln:
            k, _, v = ln.partition("="); os.environ.setdefault(k.strip(), v.strip().strip("'\""))

# Controlled target: clamp() has a real bug — returns lo instead of hi when x>hi.
TARGET = '''
def clamp(x, lo, hi):
    """Clamp x to the range [lo, hi]."""
    if x < lo:
        return lo
    if x > hi:
        return lo   # intended: return hi
    return x
'''

DIRECTIVE = """You are a STEM/code falsification reviewer under CDSFL. The OBJECTIVE
is to find MATERIAL defects in the target below and PROVE each one mechanically —
not to enumerate style nits, and not to argue in prose.

For EACH material defect you find, you MUST:
1. Write a FALSIFIER: a self-contained Python snippet that, when run, RAISES an
   AssertionError (or prints FALSIFIED) if and only if the defect is real. It must
   include the target code and exercise the specific defect.
2. Actually RUN your falsifier using the execute_python tool, and read the result.
   A claim with no run falsifier is inadmissible.
3. Report it in EXACTLY this format (one block per defect):

FINDING: <one-line description>
FALSIFIER:
```python
<the exact code you ran>
```
RAN_RESULT: <paste the tool's actual output>
VERDICT: CONFIRMED   (if running it demonstrated the defect)

If you find no material defect, reply exactly: NO_MATERIAL_DEFECT.

TARGET:
```python
%s
```
""" % TARGET

EXECUTE_TOOL = {
    "type": "function",
    "function": {
        "name": "execute_python",
        "description": "Run Python 3; full STEM toolset importable (sympy, numpy, z3, etc.). Print what you want to see.",
        "parameters": {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]},
    },
}


def execute_python(code: str, timeout: int = 20) -> str:
    f = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False); f.write(code); f.close()
    try:
        r = subprocess.run([sys.executable, f.name], capture_output=True, text=True, timeout=timeout)
        out = (r.stdout or "")
        if r.returncode != 0:
            out += f"\n[exit {r.returncode}]\n" + (r.stderr or "")[-1500:]
        return out.strip()[:3000] or "(no output)"
    except subprocess.TimeoutExpired:
        return f"[timeout {timeout}s]"
    finally:
        try: os.unlink(f.name)
        except OSError: pass


def runner_reverify(falsifier_code: str) -> str:
    """The RUNNER independently re-runs the model's falsifier. Verdict by result:
    nonzero exit / AssertionError / 'FALSIFIED' => CONFIRMED (defect real);
    clean exit => REFUTED (falsifier did not demonstrate a defect)."""
    f = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False); f.write(falsifier_code); f.close()
    try:
        r = subprocess.run([sys.executable, f.name], capture_output=True, text=True, timeout=20)
        demonstrated = (r.returncode != 0) or ("FALSIFIED" in (r.stdout or "")) \
                       or ("AssertionError" in (r.stderr or ""))
        return "CONFIRMED" if demonstrated else "REFUTED"
    except subprocess.TimeoutExpired:
        return "ERROR_TIMEOUT"
    finally:
        try: os.unlink(f.name)
        except OSError: pass


def run_model(model_id: str, base_url: str, key_env: str, max_iters: int = 6) -> dict:
    import openai
    key = os.environ.get(key_env)
    if not key: return {"model": model_id, "error": f"{key_env} not set"}
    client = openai.OpenAI(base_url=base_url, api_key=key, timeout=200)
    messages = [{"role": "system", "content": "Careful CDSFL falsification reviewer. Prove defects by running code; never just assert in prose."},
                {"role": "user", "content": DIRECTIVE}]
    n_calls = 0; t0 = time.time()
    final = ""
    for _ in range(max_iters):
        resp = client.chat.completions.create(model=model_id, messages=messages, tools=[EXECUTE_TOOL],
                                              tool_choice="auto", temperature=0.0, max_tokens=4096, timeout=180)
        msg = resp.choices[0].message
        tcs = getattr(msg, "tool_calls", None) or []
        if tcs:
            n_calls += len(tcs)
            messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": [tc.model_dump() for tc in tcs]})
            for tc in tcs:
                try: args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError: args = {}
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": execute_python(args.get("code", ""))[:3000]})
        else:
            final = (msg.content or "").strip(); break
    # Extract the model's falsifier code block
    m = re.search(r"FALSIFIER:\s*```(?:python)?\s*(.*?)```", final, re.S)
    falsifier = m.group(1).strip() if m else ""
    model_verdict = "CONFIRMED" if "VERDICT: CONFIRMED" in final.upper() else \
                    ("NO_DEFECT" if "NO_MATERIAL_DEFECT" in final.upper() else "?")
    runner_verdict = runner_reverify(falsifier) if falsifier else "NO_FALSIFIER"
    return {"model": model_id, "tool_calls": n_calls, "elapsed_s": round(time.time()-t0,1),
            "has_falsifier": bool(falsifier), "model_verdict": model_verdict,
            "runner_verdict": runner_verdict,
            "AGREE_and_CORRECT": runner_verdict == "CONFIRMED" and model_verdict == "CONFIRMED",
            "falsifier_excerpt": falsifier[:160]}


def main():
    print("=== falsifier-carrying smoke test (target has a REAL clamp bug) ===\n")
    results = []
    for label, mid, base, key in [
        ("gpt-5.5", "openai/gpt-5.5", "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
        ("deepseek", "deepseek-v4-pro", "https://api.deepseek.com", "DEEPSEEK_API_KEY"),
    ]:
        try:
            r = run_model(mid, base, key); r["label"] = label
        except Exception as e:  # noqa: BLE001
            r = {"label": label, "model": mid, "error": f"{type(e).__name__}: {e}"}
        results.append(r); print(json.dumps(r, default=str))
    Path("/tmp/falsifier_spike_results.json").write_text(json.dumps(results, indent=2, default=str))
    print("\nKEY: AGREE_and_CORRECT=true means the model attached a falsifier whose")
    print("INDEPENDENT runner re-run confirmed the real defect — tools decided, no vote.")


if __name__ == "__main__":
    sys.exit(main())
