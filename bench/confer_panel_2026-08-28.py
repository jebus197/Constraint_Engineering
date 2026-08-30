#!/usr/bin/env python3
"""Three-reviewer panel: CC1, CC2, Fable. Free on the Max plan, no metered cost.

Generic over the brief, so the two dispatches approved on 2026-08-27 ("Do them
both") share one dispatcher instead of two near-copies. Pass the log directory;
it must contain BRIEF.md.

SANDBOXED, and the reason is not hypothetical. Both reviewers reach the Claude
CLI, which grants Bash, and BASH IS A SUPERSET OF WRITE. On 2026-08-22 a model
edited the working tree during a dispatch and a blanket `git add -A` committed
it. Each reviewer is confined to a throwaway git worktree: reads and test runs
work, writes cannot escape, and the worktree is removed in a `finally`.

CC1 does not vote. It curates, collates, and tests the output with tools.
"""
from __future__ import annotations
import concurrent.futures, json, os, pathlib, shutil, subprocess, sys, tempfile, time

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "bench"))
_env = REPO / ".env"
if _env.is_file():
    for _l in _env.read_text().splitlines():
        _l = _l.strip()
        if not _l or _l.startswith("#") or "=" not in _l:
            continue
        if _l.startswith("export "):
            _l = _l[len("export "):].lstrip()
        _k, _, _v = _l.partition("=")
        os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

from experiment_11_orchestrator import call_claude_cli, set_panel_cwd, set_tool_log_sink  # noqa: E402

if len(sys.argv) < 2:
    print("usage: confer_panel_2026-08-28.py <log-dir-name> [--dry-run]", file=sys.stderr)
    raise SystemExit(2)
LOGS = REPO / "bench" / "logs" / sys.argv[1]
DRY = "--dry-run" in sys.argv
BRIEF = LOGS / "BRIEF.md"
if not BRIEF.is_file():
    print(f"no BRIEF.md in {LOGS}", file=sys.stderr)
    raise SystemExit(2)
PROMPT = BRIEF.read_text(encoding="utf-8")

SYSTEM = (
    "You are reviewing CDSFL, a research framework that uses structured Popperian "
    "falsification and a multi-model panel to find defects in STEM artefacts. Biological "
    "component names are ANALOGY ONLY -- module names, not biology.\n\n"
    "Its founding principle is TOOLS DECIDE, NOT VOTES: a finding is confirmed when the "
    "runner independently re-executes a model-supplied falsifier, never by model "
    "agreement. Hold yourself to it -- run the command, then make the claim. A claim you "
    "did not check is worth less than an admission that you could not check it.\n\n"
    "Your working directory is a DISPOSABLE COPY of the repository. Read it, run tests in "
    "it, and break things in it freely; anything you write there is discarded. Only your "
    "report leaves this session.\n\n"
    "Disagreement between reviewers is preserved as information, not smoothed into "
    "consensus. Where you differ from what the brief asserts, say so and show why.\n\n"
    "Do not pad. The founder is dyslexic and reads every word."
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
        # Evidence that the reviewer actually RAN things, not just wrote.
        set_tool_log_sink(str(LOGS / f"{tag}.tools.json"))
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
        set_tool_log_sink(None)
        # EXTRACT THE REVIEWER'S WORK BEFORE TEARING THE SANDBOX DOWN.
        #
        # Founder, 2026-08-30: "why are you throwing sandbox repairs away? Sure
        # sandboxes should be deleted after we are done with them and after you
        # have extracted fixes, not before!"
        #
        # He is right and the cost was real. On the 2026-08-30 repair-loop panel,
        # fable wrote three changes to canary_seeding.py plus 7 tests, and cc2
        # wrote four edits to reference_runner_v2.py plus 8 tests and two further
        # fixes. Every line was deleted here before anyone read it, and the
        # reviews had to be re-implemented from their prose descriptions.
        #
        # A reviewer is dispatched WITHOUT Write/Edit, but Bash can write, and
        # both reviewers used it. The diff is the most valuable thing a review
        # produces and it was the one thing being discarded.
        try:
            diff = subprocess.run(["git", "diff", "HEAD"], cwd=str(wt),
                                  capture_output=True, text=True, timeout=60)
            untracked = subprocess.run(["git", "ls-files", "--others",
                                        "--exclude-standard"], cwd=str(wt),
                                       capture_output=True, text=True, timeout=60)
            patch = LOGS / f"{tag}.patch"
            body = diff.stdout or ""
            for rel in (untracked.stdout or "").split():
                f = pathlib.Path(wt) / rel
                try:
                    if f.is_file() and f.stat().st_size < 400_000:
                        body += (f"\n=== NEW FILE: {rel} ===\n"
                                 + f.read_text(encoding="utf-8", errors="replace"))
                except OSError:
                    pass
            if body.strip():
                patch.write_text(body, encoding="utf-8")
                print(f"  [{tag}] extracted {len(body):,} chars of work -> {patch.name}",
                      flush=True)
            else:
                print(f"  [{tag}] no file changes to extract", flush=True)
        except Exception as _e:                              # noqa: BLE001
            print(f"  [{tag}] EXTRACTION FAILED, sandbox kept at {wt}: {_e}", flush=True)
            return rec          # do NOT destroy work we could not extract
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)],
                       cwd=str(REPO), capture_output=True)
        shutil.rmtree(wt.parent, ignore_errors=True)
    (LOGS / f"{tag}.json").write_text(json.dumps(rec, indent=2), encoding="utf-8")
    print(f"  [{tag}] ok={rec['ok']} chars={rec.get('chars', 0)} {rec['elapsed_s']}s"
          + (f"  ERR={rec.get('error')}" if not rec["ok"] else ""), flush=True)
    return rec


print(f"=== panel: {LOGS.name} — {len(MODELS)} reviewers, brief {len(PROMPT):,} chars ===",
      flush=True)
print("    cc2 and fable are Max-plan and FREE. Sandboxed in throwaway worktrees.",
      flush=True)
if DRY:
    print("    DRY RUN — nothing dispatched.", flush=True)
    raise SystemExit(0)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    list(pool.map(lambda a: run(*a), MODELS))
print("  done", flush=True)
