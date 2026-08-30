#!/usr/bin/env python3
"""Three-reviewer panel: CC1, CC2, Fable. Free on the Max plan, no metered cost.

SANDBOXED. Both reviewers reach the Claude CLI, which grants Bash, and BASH IS A
SUPERSET OF WRITE. On 2026-08-22 a model edited the working tree directly during a
dispatch and a blanket `git add -A` committed it. set_panel_cwd() confines each
dispatch to a throwaway worktree: reads and test runs work, writes cannot escape.
"""
from __future__ import annotations
import concurrent.futures, json, os, pathlib, shutil, subprocess, sys, tempfile, time

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "bench"))
_env = REPO / ".env"
if _env.is_file():
    for _l in _env.read_text().splitlines():
        _l = _l.strip()
        if not _l or _l.startswith("#") or "=" not in _l: continue
        if _l.startswith("export "): _l = _l[len("export "):].lstrip()
        _k, _, _v = _l.partition("=")
        os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

from experiment_11_orchestrator import call_claude_cli, set_panel_cwd  # noqa: E402

LOGS = REPO / "bench/logs/convergence_panel_2026-08-23"
PROMPT = (LOGS / "BRIEF.md").read_text(encoding="utf-8")

SYSTEM = (
    "You are reviewing CDSFL, a research framework that uses structured Popperian "
    "falsification and a multi-model panel to find defects in STEM artefacts. Biological "
    "component names are ANALOGY ONLY -- module names, not biology.\n\n"
    "Its founding principle is TOOLS DECIDE, NOT VOTES: a finding is confirmed when the "
    "runner independently re-executes a model-supplied falsifier, never by model "
    "agreement. Hold yourself to it -- run the command, then make the claim.\n\n"
    "Your working directory is a DISPOSABLE COPY of the repository. Read it and run "
    "tests in it freely; anything you write there is discarded. Only your report leaves "
    "this session.\n\n"
    "The founder has explicitly required a SINGLE converged answer to Q1 and has "
    "overridden this project's usual no-compelled-convergence rule for that question "
    "only. On Q2 and Q3 disagreement is preserved as information.\n\n"
    "Do not pad. Every word is read, so make every word carry weight."
)
MODELS = [("cc2", "opus"), ("fable", "fable")]


def run(tag, model_id):
    t0 = time.time()
    wt = pathlib.Path(tempfile.mkdtemp(prefix="cdsfl_panel_")) / "repo"
    try:
        rc = subprocess.run(["git", "worktree", "add", "--detach", str(wt), "HEAD"],
                            cwd=str(REPO), capture_output=True).returncode
        if rc != 0:
            raise RuntimeError("sandbox worktree could not be created")
        set_panel_cwd(str(wt))
        txt = call_claude_cli(model_id, SYSTEM, PROMPT, timeout=2400, max_retries=2) or ""
        ok = bool(txt.strip()) and "<invoke" not in txt and len(txt) > 800
        rec = {"reviewer": tag, "ok": ok, "chars": len(txt),
               "elapsed_s": round(time.time() - t0, 1), "response": txt}
        if not ok:
            rec["error"] = "empty, too short, or a tool-call block rather than a verdict"
    except Exception as e:  # noqa: BLE001
        rec = {"reviewer": tag, "ok": False, "error": f"{type(e).__name__}: {e}",
               "elapsed_s": round(time.time() - t0, 1), "response": ""}
    finally:
        set_panel_cwd(None)
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)],
                       cwd=str(REPO), capture_output=True)
        shutil.rmtree(wt.parent, ignore_errors=True)
    (LOGS / f"{tag}.json").write_text(json.dumps(rec, indent=2))
    print(f"  [{tag}] ok={rec['ok']} chars={rec.get('chars',0)} {rec['elapsed_s']}s"
          + (f"  ERR={rec.get('error')}" if not rec["ok"] else ""), flush=True)
    return rec


print(f"=== convergence panel: {len(MODELS)} reviewers, brief {len(PROMPT):,} chars ===")
print("    both are Max-plan and FREE. Sandboxed in throwaway worktrees.", flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    list(pool.map(lambda a: run(*a), MODELS))
print("  done", flush=True)
