"""Key-blind panel draft-review of the Exp 49 engineering exam module.

The locked exam spec requires every draft to be panel-reviewed against the
selection criteria before use. Reviewers see the MODULE ONLY — never the
answer key — and are asked about wording quality, not truth values.
Dispatches are stateless API calls; no exam contamination is possible.
"""
from __future__ import annotations
import concurrent.futures
import json
import os
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "bench"))
from experiment_11_orchestrator import (  # noqa: E402
    call_claude_cli, call_deepseek, call_openrouter,
)

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

LOGS = REPO_ROOT / "bench" / "logs" / "confer_exp49_draft_review_2026-07-29"
LOGS.mkdir(parents=True, exist_ok=True)

SYSTEM = (REPO_ROOT / "bench" / "directives" / "universal"
          / "cdsfl_core_formal.md").read_text(encoding="utf-8")
MODULE = (REPO_ROOT / "bench" / "cdsfl_registry" / "targets"
          / "exp49_engineering.md").read_text(encoding="utf-8")

PROMPT = f"""KEY-BLIND DRAFT REVIEW (CDSFL locked-spec gate). The document below is a
candidate ground-truthed review target for an upcoming experiment. You are NOT
being asked to find its planted errors, and you have NOT been shown its answer
key. Review it against the selection criteria ONLY:

1. COHERENCE: does it read as a plausible, self-contained technical document
   (not an obvious quiz)?
2. FALSIFIABILITY: is every numbered claim mechanically checkable in principle
   (a tool could verify or refute it from the document's own content)?
3. AMBIGUITY: list any claim whose WORDING is ambiguous enough that two
   competent readers could disagree about what is being asserted (cite ids).
4. SELF-CONTAINMENT: does any claim depend on outside facts not stated in the
   document (beyond standard reference knowledge)?
5. VERDICT: ACCEPT / ACCEPT-WITH-EDITS (list the edits) / REJECT (why).

Do not attempt to grade individual claims true or false. Wording quality only.

DOCUMENT:
{MODULE}
"""

MODELS = [
    ("cc2",      "opus",                          "claude_cli"),
    ("cx",       "openai/gpt-5.5",                "openrouter"),
    ("gemini",   "google/gemini-3.1-pro-preview", "openrouter"),
    ("chatgpt",  "openai/gpt-5.5",                "openrouter"),
    ("deepseek", "deepseek-v4-pro",               "deepseek"),
]


def dispatch(name, model_id, route):
    t0 = time.time()
    try:
        if route == "claude_cli":
            resp = call_claude_cli(model_id, SYSTEM, PROMPT)
        elif route == "deepseek":
            resp = call_deepseek(model_id, SYSTEM, PROMPT)
        else:
            resp = call_openrouter(model_id, SYSTEM, PROMPT)
        ok = bool(resp and resp.strip())
        out = {"model": name, "ok": ok, "chars": len(resp or ""),
               "elapsed_s": round(time.time() - t0, 1), "response": resp or ""}
    except Exception as e:  # noqa: BLE001
        out = {"model": name, "ok": False, "error": f"{type(e).__name__}: {e}",
               "elapsed_s": round(time.time() - t0, 1), "response": ""}
    (LOGS / f"{name}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"  [{name}] ok={out['ok']} chars={out.get('chars', 0)} {out['elapsed_s']}s"
          + (f" ERR={out.get('error')}" if not out["ok"] else ""))
    return out


def main():
    print(f"=== Exp 49 engineering exam draft review (key-blind) — {len(MODELS)} models ===")
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        futs = {ex.submit(dispatch, n, m, r): n for n, m, r in MODELS}
        for f in concurrent.futures.as_completed(futs):
            res = f.result()
            results[res["model"]] = res
    (LOGS / "_all.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    ok = [n for n, r in results.items() if r["ok"]]
    print(f"\n=== {len(ok)}/{len(MODELS)} responded: {ok} ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
