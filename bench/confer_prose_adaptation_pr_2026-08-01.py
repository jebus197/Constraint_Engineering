#!/usr/bin/env python3
"""Panel review (pr): adapting the CDSFL instrument from code targets to prose.

FOUNDER-COMMISSIONED, 2026-08-01. Two differences from a standard `pr`:
  * CC1 participates ACTIVELY with its own position, rather than only collating.
  * The panel is asked to CONVERGE on one recommendation. The standing `pr`
    definition preserves disagreement instead, because compelled convergence is
    a recorded failure mode (Divergence Study, 2026-06-03). Both are honoured
    here: round 2 asks for a convergent recommendation AND for any dissent to be
    stated separately, so an actionable answer is produced without the
    disagreement being smoothed away.

Cost discipline: two rounds, five models, no tools. The founder is funding this
from borrowed money and said so.
"""
from __future__ import annotations

import concurrent.futures
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

import os  # noqa: E402

# .env is sourced inside experiment_11_orchestrator's __main__ block, so importing
# the module does NOT populate the keys. Every confer script must do it itself.
# Format is `export KEY=value`; the prefix has to be stripped (a checker that
# ignored it once produced a false "keys absent" report, corrected 2026-07-08).
_ENV = REPO / ".env"
if _ENV.exists():
    for _line in _ENV.read_text().splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        if _line.startswith("export "):
            _line = _line[7:]
        _k, _, _v = _line.partition("=")
        os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

from experiment_11_orchestrator import (  # noqa: E402
    call_deepseek, call_openrouter, call_claude_cli,
)

CDSFL = (REPO / "bench" / "directives" / "universal"
         / "cdsfl_core_formal.md").read_text(encoding="utf-8")

LOGS = REPO / "bench" / "logs" / "pr_prose_adaptation_2026-08-01"
LOGS.mkdir(parents=True, exist_ok=True)

MODELS = [
    ("cc2",      "opus",                          "claude_cli"),
    ("codex",    "openai/gpt-5.5",                "openrouter"),
    ("gemini",   "google/gemini-3.1-pro-preview", "openrouter"),
    ("chatgpt",  "openai/gpt-5.5",                "openrouter"),
    ("deepseek", "deepseek-v4-pro",               "deepseek"),
]

# ── The evidence, stated without spin. Every figure below was reproduced. ────

EVIDENCE = r"""
THE SYSTEM. CDSFL runs a five-model panel over a TARGET ARTICLE for many rounds.
Findings are raised, demonstrated by runnable falsifiers, fixes proposed, and each
fix scored by an admission pipeline (S_k). A two-sided convergence gate closes the
run when the critical-discovery curve has flattened AND K consecutive rounds add no
new critical findings.

The instrument was built when every target was a PYTHON MODULE. The arc has since
moved to prose: markdown design references and exam documents that carry natural
language claims plus fenced Python listings. Nobody adapted the instrument for that
shift. On 2026-08-01 a single control experiment was halted twice, and SEVEN
distinct defects of one class were found in a day. All were reproduced by execution.

THE CLASS: a code-review mechanism silently misapplied to a prose target.

  1. _anchor_dir_for wrote a scratch .py beside the target for tool context. The
     markdown target is staged read-only in a directory that refuses new files.
     Died EPERM one second into the first launch. LOUD.
  2. run_verification (close-the-loop) ran ruff/mypy/bandit on the sandbox
     whatever its type. mypy parsed the prose as source ("Leading zeros in decimal
     integer") so EVERY close-the-loop attempt failed and no finding could close.
  3. The S_k HARD GATES ran ast.parse and py_compile on the WHOLE target. The
     document's prose is not parseable Python, so A = g1*g2 = 0 and EVERY fix was
     REJECTED: 38 findings rejected at S_k, 29 by the AST gate. This was the
     dominant cause of the halt. Findings could never resolve, exhausted the
     routing ladder, and were locked "irreducible".
  4. max_irreducible_queue defaulted to 2, justified in-code by "for code review,
     genuinely irreducible defects are rare". CC1 raised it to 8, then 30, to stop
     the alarm refusing convergence. BOTH RAISES WERE WRONG. The alarm's own text
     says a large queue "almost certainly signals a routing/dedup mechanical
     failure, NOT genuine irreducibility" — which is exactly what it was. CC1
     suppressed a correct alarm twice. Reverted to the default.
  5. _sweep_prompt wraps the target in a ```python fence labelled "TARGET MODULE".
     A markdown document contains its own fences, so the runner's fence is closed
     by the document's first one: on one real target only 44 of 270 lines (16 per
     cent) land inside the block, with 12 stray fence markers loose in the prompt.
  6. The B-Cell specialist router hands the target path to verifiers that run
     mypy, ruff, bandit, dis and crosshair on it with no target-type check.
  7. _extract_routing_falsifier keeps only fenced blocks containing the word
     "import" — a code-target heuristic (a falsifier against a repo module must
     import it). A falsifier for a prose claim opens the staged document by
     absolute path and asserts on its text. Such a falsifier is discarded as
     EMPTY, which mints a false "ladder exhausted" record and inflates the
     irreducible queue against a bound of 2.

THE WORST ONE, AND IT WAS CC1'S OWN REPAIR. Fixing (3) so A=1 exposed that the
EFFECT gates behind it are stuck at fake-pass on a prose target:
  * e3_ruff — ruff error-recovers over markdown and reports 2752 phantom
    diagnostics as the BASELINE (3753 / 3290 / 2713 on the three other queued
    targets). The delta therefore measures HOW MUCH ENGLISH WAS ADDED.
  * e4_bandit — cannot parse the file, returns an empty result set, and reports
    "0 HIGH / 0 MEDIUM" forever. It carries the HEAVIEST weight in the pipeline (2.0
    against ruff's 1.0).
  * e2_regression — permanently unavailable: prose targets are staged outside the
    repo, and no prose config defines test_cmd.
So E is floored at 0.667, A is now 1, and sk >= 0.667 > 0 -> ADMISSIBLE, always.
The "no evidence" valve (`if not effect_gates: ESCALATE`) never fires, because e3
and e4 always return a score.

MEASURED END TO END, against the real control document:
    fix injecting subprocess.call("rm -rf /var/helios/" + x, shell=True)
        into a fenced listing            -> sk=1.0000  A=1  E=1.0000  ADMISSIBLE
    correct added prose (+8 lines)       -> sk=0.6667  A=1  E=0.6667  ADMISSIBLE
The ranking is INVERTED and nothing is ever rejected. The exploit adds 0 new ruff
diagnostics (it is inside a fence ruff already cannot parse); the correct prose adds
32 and scores 0.0.

sk_enabled is TRUE in all eight queued prose configs, against a code default of
FALSE. sk_s_floor is 0.0 in all of them, and check_sk_threshold computes s_star =
-0.053 -> clamped to 0.0, so the "Valley of Bad Fixes" guard passes everything too.
Every admitted fix drives R_k DOWNWARD (0.500 -> 0.367 at sk=1.0) where an honest
sk=0 would drive it UP to 0.620. The run's risk trajectory is pushed toward
"converged" by fixes whose quality was never measured.

CC1 CONVERTED A LOUD FAILURE INTO A SILENT ONE. Before the hard-gate repair the
pipeline rejected everything and halted visibly. After it, the pipeline accepts
everything, including a shell injection at full marks. This is the second time in
one day CC1 made that same class of error: an earlier repair of (2) returned
"passed=True" with all tools skipped, and `attempt_close` closes a finding on
verify.passed — so it would have marked every finding verified with nothing checked.

WHAT IS NOT IN DOUBT. The mathematical model is not implicated. Diminishing returns,
the decay curve and the two-sided gate are substrate-independent and have never been
shown wrong; every failure in this project's history has been mechanical. The
question is not whether the model applies to prose. It is which MECHANISMS can carry
it there, and what must be replaced rather than patched.

THE FOUNDER'S PROPOSED DESIGN, to be evaluated on its merits:
  A classifier flags a finding as possibly-irreducible or prose-heavy. That flag is
  a SIGNAL, not a verdict: the item is fed to the panel via the end-of-run sweep.
  The five frontier models adjudicate. Only if they concur that it is genuinely
  irreducible does it go to human review. Either way it does not block convergence.

CC1's assessment of that design, offered as a position to attack, not a conclusion:
  Two thirds of it is already built — irreducible items are ALREADY excluded from
  the blocking condition (they are logged "excluded from the A4 blocker"); the only
  coupling left is a queue-SIZE alarm. The missing piece is that THE PANEL IS NEVER
  TOLD WHY ITS FIX WAS REJECTED: 50 rejections across four rounds, and no model was
  informed. A frontier model shown "ParseError: leading zeros in decimal integer
  literals" against a fix it wrote for a markdown document would not conclude "my fix
  was bad" — it would conclude "the harness is parsing prose as Python". That is a
  better mechanical-failure detector than a count crossing a threshold. So the
  founder's design plus surfaced rejection reasons may be strictly better than the
  alarm. But it must not become a route by which model opinion waves items past a
  gate: "hard to verify" and "safe to set aside" are different claims, and this
  project's standing rule is that findings are confirmed programmatically or by the
  human, never by model vote.

CONSTRAINTS THAT BIND ANY ANSWER.
  * Money is short and real. The founder is funding this from borrowed money. A
    proposal costing many paid runs to validate is not viable however elegant.
  * Four prose experiments are queued: two exams, a four-cell factorial capstone,
    then a larger bench run. Every undiscovered instance costs a multi-hour paid run
    that halts, or worse one that completes and reports a corrupted number.
  * bench/logs/ is archival and never edited.
  * A fix that turns "cannot verify" into "verified" is worse than the defect it
    replaces. That mistake has already been made twice today.
"""

QUESTION = r"""
THE QUESTION, in four parts. Answer all four.

1. DIAGNOSIS. Is this a set of stragglers to be patched, or is the instrument
   structurally unfit for prose targets in some identifiable region? Name the
   region precisely if so. Be specific about which mechanisms carry a valid signal
   on prose and which cannot in principle.

2. THE S_k EFFECT STAGE. It currently accepts a shell injection at full marks.
   Choose and justify ONE:
     (a) repair it — say concretely what a valid effect signal for a prose target
         would be, and how it is obtained without a test suite;
     (b) disable it for prose targets (sk_enabled false) and resolve findings by
         falsifier + panel + human instead;
     (c) something else you can defend.
   If you choose (b), say what is LOST and whether the convergence gate still has
   the evidence it needs. If (a), beware: a gate that cannot fail is worse than no
   gate, because it launders an unmeasured fix as a measured one.

3. THE FOUNDER'S DESIGN. Evaluate it. Does it survive the objection that today's
   thirteen "irreducible" items were irreducible because of a BUG, so a panel
   adjudicating them blind would have concurred and hidden the defect? Does
   surfacing the rejection reason to the panel change that? What would you add or
   remove?

4. THE DEFINITIVE WAY FORWARD. Give the smallest change set that makes the
   instrument sound for prose targets, ordered by what must happen before the next
   paid run. Distinguish MUST (before any run) from SHOULD (before the factorial)
   from LATER. Be concrete: files, mechanisms, switches. Prefer disabling a
   mechanism that cannot work over patching it into a shape that merely appears to.

Apply full CDSFL protocol. P-pass your own answer before giving it: state what
would falsify your recommendation, and what you would expect to observe if you are
wrong. Mark uncertainty honestly. Where you cannot verify a claim from what you have
been given, say so rather than assuming.
"""

ROUND1 = EVIDENCE + QUESTION


def _dispatch(name: str, model_id: str, route: str, prompt: str, tag: str) -> dict:
    t0 = time.time()
    try:
        if route == "claude_cli":
            resp = call_claude_cli(model_id, CDSFL, prompt)
        elif route == "deepseek":
            resp = call_deepseek(model_id, CDSFL, prompt)
        else:
            resp = call_openrouter(model_id, CDSFL, prompt)
        ok = bool(resp and resp.strip())
        out = {"model": name, "round": tag, "ok": ok, "chars": len(resp or ""),
               "elapsed_s": round(time.time() - t0, 1), "response": resp or ""}
    except Exception as e:  # noqa: BLE001 — a dead route must not kill the panel
        out = {"model": name, "round": tag, "ok": False,
               "error": f"{type(e).__name__}: {e}",
               "elapsed_s": round(time.time() - t0, 1), "response": ""}
    (LOGS / f"{tag}_{name}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"  [{tag}][{name}] ok={out['ok']} chars={out.get('chars', 0)} "
          f"{out['elapsed_s']}s" + (f" ERR={out.get('error')}" if not out["ok"] else ""))
    return out


def run_round(prompt: str, tag: str) -> dict:
    results: dict = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        futs = {ex.submit(_dispatch, n, m, r, prompt, tag): n for n, m, r in MODELS}
        for f in concurrent.futures.as_completed(futs):
            res = f.result()
            results[res["model"]] = res
    (LOGS / f"_{tag}_all.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


def main() -> int:
    print(f"=== PANEL REVIEW: prose adaptation — {len(MODELS)} models, 2 rounds ===")
    print(f"    logs: {LOGS}")

    print("\n--- ROUND 1: independent positions ---")
    r1 = run_round(ROUND1, "r1")
    ok1 = [n for n, r in r1.items() if r["ok"]]
    print(f"  {len(ok1)}/{len(MODELS)} responded: {ok1}")
    if len(ok1) < 3:
        print("  ABORT: fewer than three positions; not a panel. No round 2 dispatched.")
        return 2

    # Round 2 shows every model the others' positions and asks for convergence,
    # with dissent recorded rather than smoothed away.
    others = "\n\n".join(
        f"===== POSITION FROM {n.upper()} =====\n{r1[n]['response'][:14000]}"
        for n in ok1)
    round2 = (
        EVIDENCE
        + "\n\nROUND 1 PRODUCED THE FOLLOWING INDEPENDENT POSITIONS.\n\n"
        + others
        + r"""

ROUND 2. Read every position above, including any that contradicts your own.

The founder requires ONE definitive recommendation, not a survey. Converge if the
evidence supports convergence — and say so plainly if it does not, because a forced
consensus that hides a real disagreement is worse than an honest split. This project
has recorded compelled convergence as a failure mode.

Produce:
  1. WHERE YOU CHANGED YOUR MIND, and which argument moved you. If nothing moved
     you, say that and say why the counter-arguments fail.
  2. THE CONVERGENT RECOMMENDATION — the smallest change set that makes the
     instrument sound for prose targets, ordered MUST / SHOULD / LATER, with files
     and switches named. Where the panel agrees, state it as agreed.
  3. RESIDUAL DISAGREEMENT, stated separately and without softening. Name who
     disagrees and on what. Do not manufacture consensus to satisfy the request.
  4. THE STRONGEST OBJECTION to the recommendation you just gave, and why you
     nonetheless hold it.
  5. COST. The founder is funding this from borrowed money. Estimate what your
     recommendation costs in paid runs before the next experiment can start, and
     say what could be cut if the answer is too expensive.
""")
    print("\n--- ROUND 2: cross-examination and convergence ---")
    r2 = run_round(round2, "r2")
    ok2 = [n for n, r in r2.items() if r["ok"]]
    print(f"  {len(ok2)}/{len(MODELS)} responded: {ok2}")

    (LOGS / "_summary.json").write_text(json.dumps(
        {"round1": {n: {"ok": r["ok"], "chars": r.get("chars", 0)} for n, r in r1.items()},
         "round2": {n: {"ok": r["ok"], "chars": r.get("chars", 0)} for n, r in r2.items()}},
        indent=2), encoding="utf-8")
    print(f"\n=== complete. r1={len(ok1)}/5  r2={len(ok2)}/5 ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
