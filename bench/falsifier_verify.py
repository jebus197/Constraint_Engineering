"""Falsifier sandbox + independent re-verification ("tools decide", 3 June 2026).

This module is the runner-side truth-decider for the "tools decide, not votes"
fix. A model, during review, attaches a FALSIFIER per critical finding: a
self-contained Python snippet that RAISES (AssertionError) or prints FALSIFIED
if and only if the claimed defect is real. The falsifier must IMPORT THE REAL
target module (e.g. ``from bench.dm._similarity import jaccard_similarity``) so
it exercises actual repository code, not a model-retyped copy.

The RUNNER then re-runs that falsifier independently via :func:`reverify_falsifier`.
The runner's result is the verdict — never the model's prose claim. The smoke
tests (bench/smoketest_falsifier_2026-06-03.py) proved a model can attach a
correct falsifier while making zero tool calls of its own, so the independent
re-run is the only trustworthy decision point.

Sandbox guarantees (HARD constraints):
  - 30 s wall-clock timeout per run.
  - Runs in a fresh temporary cwd (NamedTemporaryFile dir), never the repo.
  - Repo importable via PYTHONPATH=<repo_root> so falsifiers can import targets.
  - Read/import only: the snippet file lives in the OS temp dir and the cwd is
    a throwaway temp dir, so a falsifier cannot delete or modify repo files by
    relative path. (A maliciously absolute-pathed write is out of scope — the
    falsifier source is model-authored review code, re-run for its exit status.)

This module imports nothing from the runner or orchestrator, so it stays a leaf
dependency the runner can call without import cycles.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_TIMEOUT = 30  # seconds; HARD per-run wall-clock cap


def _sandbox_env(repo_root: str) -> dict:
    """Build a subprocess env with the repo importable via PYTHONPATH.

    Prepends repo_root to any existing PYTHONPATH so a falsifier's
    ``from bench.dm... import ...`` resolves against the real tree while the
    rest of the parent environment (PATH for the interpreter, etc.) is kept.
    """
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")
    # 2026-06-07 harness hardening: put BOTH the repo root and bench/ on
    # PYTHONPATH so a falsifier resolves `from bench.cdsfl_registry.X import`
    # AND `from cdsfl_registry.X import`. Models frequently write a relative
    # `sys.path.insert(0,'bench')` that breaks in the throwaway temp CWD; this
    # makes that hack redundant rather than fatal. reverify runs only under the
    # falsifier gate, so non-gate experiments are unaffected.
    parts = [repo_root, os.path.join(repo_root, "bench")]
    if existing:
        parts.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(parts)
    return env


def execute_python(
    code: str,
    repo_root: str | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> str:
    """Run a Python snippet in the sandbox and return combined stdout/stderr.

    Used both as the model-facing ``execute_python`` tool executor (during the
    tool-call loop) and as the primitive under :func:`reverify_falsifier`. The
    snippet runs with the repo on PYTHONPATH and a temporary working directory.
    Output is truncated to keep tool transcripts bounded.

    Returns the captured text; on timeout/launch failure returns a bracketed
    diagnostic string rather than raising, so the tool loop can feed the result
    back to the model.
    """
    root = repo_root or str(REPO_ROOT)
    env = _sandbox_env(root)
    # Temp dir for cwd (throwaway) and a temp file for the snippet, both outside
    # the repo so relative-path writes from the snippet cannot touch the tree.
    with tempfile.TemporaryDirectory(prefix="cdsfl_falsifier_") as tmp_cwd:
        fh = tempfile.NamedTemporaryFile(
            "w", suffix=".py", dir=tmp_cwd, delete=False, encoding="utf-8"
        )
        try:
            fh.write(code)
            fh.close()
            r = subprocess.run(
                [sys.executable, fh.name],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tmp_cwd,
                env=env,
            )
            out = r.stdout or ""
            if r.returncode != 0:
                out += f"\n[exit {r.returncode}]\n" + (r.stderr or "")[-2000:]
            return out.strip()[:4000] or "(no output)"
        except subprocess.TimeoutExpired:
            return f"[timeout after {timeout}s]"
        except Exception as exc:  # noqa: BLE001
            return f"[error: {type(exc).__name__}: {exc}]"
        # TemporaryDirectory cleans up the snippet file with the dir.


def reverify_falsifier(
    falsifier_code: str,
    repo_root: str | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> str:
    """Independently re-run a model-attached falsifier and decide the verdict.

    The runner — NOT the model — owns this decision. Verdict semantics:

      * "CONFIRMED"   — the re-run GENUINELY demonstrated the defect: the
                        falsifier raised an AssertionError or printed the literal
                        token ``FALSIFIED``. Only the falsifier's designed failure
                        mechanism counts — NOT an arbitrary nonzero exit.
      * "REFUTED"     — the falsifier ran to a clean exit (returncode 0, no
                        AssertionError, no FALSIFIED). It did NOT demonstrate a
                        defect, so a claim attached to it is not rubber-stamped.
      * "UNTOOLABLE"  — no falsifier code was supplied (empty/whitespace). There
                        is nothing to re-run, so the claim is unverifiable here.
      * "ERROR"       — the falsifier could not be trusted to decide: a timeout,
                        a harness/launch failure, OR a nonzero exit that is NOT a
                        genuine demonstration (a BROKEN falsifier — bad import,
                        typo, raw uncaught exception). Treated as not-demonstrated;
                        never an auto-CONFIRM. The runner re-asks or escalates.

    The asymmetry is deliberate. CONFIRMED requires the falsifier's designed
    demonstration (AssertionError / FALSIFIED). A clean exit with no demonstration
    is REFUTED. Everything else — timeout, harness error, or a broken falsifier
    that crashes for an unrelated reason — is ERROR, never CONFIRMED. (Without
    this, a model shipping a buggy falsifier — a bad import or typo — would have
    its finding silently auto-confirmed; caught in review 3 June 2026.)
    """
    if not falsifier_code or not falsifier_code.strip():
        return "UNTOOLABLE"

    root = repo_root or str(REPO_ROOT)
    env = _sandbox_env(root)
    with tempfile.TemporaryDirectory(prefix="cdsfl_reverify_") as tmp_cwd:
        fh = tempfile.NamedTemporaryFile(
            "w", suffix=".py", dir=tmp_cwd, delete=False, encoding="utf-8"
        )
        try:
            fh.write(falsifier_code)
            fh.close()
            r = subprocess.run(
                [sys.executable, fh.name],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tmp_cwd,
                env=env,
            )
        except subprocess.TimeoutExpired:
            return "ERROR"
        except Exception:  # noqa: BLE001
            return "ERROR"

    stdout = r.stdout or ""
    stderr = r.stderr or ""
    # CONFIRMED requires a GENUINE demonstration via the falsifier's designed
    # failure mechanism — an AssertionError or an explicit FALSIFIED token. A
    # nonzero exit for any OTHER reason (ImportError, NameError, SyntaxError, a
    # raw uncaught exception) means the falsifier is BROKEN, not that the defect
    # is real, and must NEVER auto-confirm; return ERROR so the runner can
    # re-ask the model or escalate.
    # Exp 44 post-run fix (2026-07-27, C0025/C0034/C0009): the old substring
    # test ("FALSIFIED" in stdout) matched "NOT FALSIFIED" — an honest negative
    # report — and stamped it CONFIRMED, letting a demonstrated-ABSENT defect
    # close as real (C0025, sev 0.90). Likewise a setup-guard AssertionError
    # ("test setup failed: ...") is instrument breakage, not a demonstration
    # (C0009). Verdict reading is now negation- and setup-aware:
    #   1. An explicit negative report wins: NOT FALSIFIED -> REFUTED.
    #   2. A setup/guard AssertionError -> ERROR (broken instrument, re-ask).
    #   3. CONFIRMED requires the FALSIFIED token NOT preceded by NOT, or a
    #      genuine (non-setup) AssertionError.
    import re as _re
    if _re.search(r"\bNOT[\s_-]?FALSIFIED\b", stdout, _re.IGNORECASE):
        return "REFUTED"
    _assert_err = "AssertionError" in stderr
    if _assert_err and _re.search(r"AssertionError[^\n]*\b(setup|precondition|guard)\b",
                                  stderr, _re.IGNORECASE):
        return "ERROR"
    if _re.search(r"(?<![A-Z_])FALSIFIED\b", stdout) or _assert_err:
        return "CONFIRMED"
    if r.returncode == 0:
        return "REFUTED"
    return "ERROR"


if __name__ == "__main__":
    # Tiny self-check against the real similarity module (read-only).
    _real_confirm = (
        "from bench.dm._types import Finding\n"
        "from bench.dm._similarity import jaccard_similarity\n"
        "f = Finding('a','m',0,2,0.8,0.5,'memory leak in cache eviction path')\n"
        "assert jaccard_similarity(f, f) < 1.0, 'self-sim should be < 1.0 (real defect)'\n"
        "print('FALSIFIED: self-similarity is not 1.0')\n"
    )
    _false_claim = (
        "from bench.dm._types import Finding\n"
        "from bench.dm._similarity import jaccard_similarity\n"
        "a = Finding('a','m',0,2,0.8,0.5,'buffer overflow in json parser')\n"
        "b = Finding('b','m',0,2,0.7,0.5,'json parser buffer overflow')\n"
        "# FALSE claim under test: the function is order-dependent (asymmetric).\n"
        "# A correctly written falsifier RAISES only if asymmetry is actually\n"
        "# found. The function is symmetric, so the probe finds nothing ->\n"
        "# clean exit -> REFUTED (the runner does NOT rubber-stamp the claim).\n"
        "if jaccard_similarity(a, b) != jaccard_similarity(b, a):\n"
        "    print('FALSIFIED: asymmetric')\n"
        "    raise AssertionError('order-dependent')\n"
        "print('symmetric: claim not demonstrated')\n"
    )
    print("real-defect  reverify:", reverify_falsifier(_real_confirm), "(expect CONFIRMED)")
    print("false-claim  reverify:", reverify_falsifier(_false_claim), "(expect REFUTED)")
    print("empty        reverify:", reverify_falsifier(""), "(expect UNTOOLABLE)")
