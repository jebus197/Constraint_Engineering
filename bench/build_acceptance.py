"""THE MECHANICAL ACCEPTANCE GATE for the build experiment.

WHY THIS IS THE WHOLE POINT
---------------------------
On 2026-08-22 the discrimination control measured that 131 of 263 archived
falsifiers keep firing after the very defect they accuse has been repaired. The
cause is that the falsifier gate accepts a falsifier IF IT FIRES -- a ONE-SIDED
test. `reverify_falsifier("print('FALSIFIED')")` returns CONFIRMED.

The founder asked the obvious question: how can a broken instrument be used to
repair itself? The answer is that this gate is TWO-SIDED, and the second side is
exactly the check that was missing:

    (1) the model's new test must FAIL at the parent commit
    (2) the same test must PASS with the model's patch applied
    (3) the FULL SUITE must stay green

A test that always fails cannot pass (2). A test that always passes cannot pass
(1). The fail-before/pass-after requirement IS the discrimination control, present
in the acceptance criterion at construction rather than bolted on two months
later. (3) is an independent constraint the model does not control.

NO MODEL VOTE AND NO CC1 ADJUDICATION APPEARS ANYWHERE IN THIS FILE. That is
deliberate and it is the reason this gate can be trusted where the other could
not.

THE HONEST RESIDUAL, stated here rather than discovered later: a patch can pass
all three checks and still be wrong because its test is too narrow. This gate
cannot see that. It CANNOT, however, produce the failure mode measured on
2026-08-22, and that is the claim being made -- no more.

PRE-REGISTERED TELL (fixed before the first dispatch): an acceptance rate near
100% means the checks are not binding and the run should be distrusted. Near 0%
means the models cannot do the task. A healthy result is a mix.

ISOLATION. Every candidate is evaluated in its own `git worktree`, never in the
working tree. A rejected patch cannot leave a trace, and two models working the
same file cannot collide.
"""
from __future__ import annotations

import dataclasses
import re
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent
SEARCH_REPLACE = re.compile(
    r"<<<<\s*SEARCH\s+(?P<path>[^\n]+)\n(?P<search>.*?)\n====\s*REPLACE[^\n]*\n"
    r"(?P<replace>.*?)\n>>>>", re.S)

# Every distinguishable outcome. Deliberately NOT collapsible to a boolean: this
# project's single most repeated lesson is that "it failed" and "it crashed"
# must never render identically.
ACCEPTED = "ACCEPTED"
REJ_NO_PATCH = "REJECTED_NO_PATCH"
REJ_NO_TEST = "REJECTED_NO_TEST"
REJ_PATCH_DID_NOT_APPLY = "REJECTED_PATCH_DID_NOT_APPLY"
REJ_TEST_PASSED_BEFORE = "REJECTED_TEST_PASSED_AT_PARENT"     # test proves nothing
REJ_TEST_FAILED_AFTER = "REJECTED_TEST_STILL_FAILS_WITH_PATCH"
REJ_SUITE_WENT_RED = "REJECTED_SUITE_WENT_RED"
ERR_HARNESS = "INDETERMINATE_HARNESS_ERROR"


@dataclasses.dataclass
class Verdict:
    outcome: str
    detail: str = ""
    test_at_parent: str = ""
    test_with_patch: str = ""
    suite_before: str = ""
    suite_after: str = ""
    files_touched: tuple = ()

    @property
    def accepted(self) -> bool:
        return self.outcome == ACCEPTED


def parse_patch(text: str) -> list:
    """Extract SEARCH/REPLACE blocks. Returns [(path, search, replace), ...]."""
    return [(m.group("path").strip(), m.group("search"), m.group("replace"))
            for m in SEARCH_REPLACE.finditer(text or "")]


def parse_test(text: str) -> tuple:
    """Extract the model's new test: a ```python fence tagged TEST_FILE: <path>."""
    m = re.search(r"TEST_FILE:\s*([^\n]+)\n+```(?:python)?\n(.*?)```", text or "", re.S)
    if not m:
        return "", ""
    return m.group(1).strip(), m.group(2)


def _run(cmd: list, cwd: Path, timeout: int = 900) -> tuple:
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                       timeout=timeout)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def failing_nodeids(out: str) -> frozenset:
    """The set of failing test node-ids in a pytest run."""
    return frozenset(re.findall(r"^FAILED\s+(\S+)", out or "", re.M))


_BASELINE: dict = {}


def suite_baseline(parent: str, suite_cmd: list, timeout: int) -> frozenset:
    """WHICH TESTS ALREADY FAIL AT THE PARENT, IN A WORKTREE.

    MEASURED 2026-08-22, and it is why this function exists: the first version of
    this gate assumed a green suite and rejected a VALID patch from Codex as
    REJECTED_SUITE_WENT_RED. In a bare worktree at the same commit, with NO patch
    applied, 1 test fails -- test_falsifier_cannot_read_the_key.py scans "the whole
    tracked archive" and bench/logs is gitignored, so a fresh worktree has no
    archive for it to scan.

    Every task in the run would have been falsely rejected, the experiment would
    have reported near-0% acceptance, and near-0% is this harness's own
    pre-registered tell for "the models cannot do the task". A harness artefact
    would have rendered as a confident verdict about six models' competence -- this
    project's house failure mode, committed by the instrument built to end it.

    So step 3 is now TWO-SIDED like steps 1 and 2: measure the parent, compare the
    patch. Green-at-parent was an assumption, and refusing assumptions is the whole
    design. Cached per parent: the baseline is identical for every candidate.
    """
    key = (parent, tuple(suite_cmd))
    if key in _BASELINE:
        return _BASELINE[key]
    wt = Path(tempfile.mkdtemp(prefix="cdsfl_base_")) / f"wt_{uuid.uuid4().hex[:8]}"
    try:
        rc, _ = _run(["git", "worktree", "add", "--detach", str(wt), parent], REPO)
        if rc != 0:
            _BASELINE[key] = frozenset()
            return _BASELINE[key]
        _, out = _run(suite_cmd, wt, timeout)
        _BASELINE[key] = failing_nodeids(out)
    except Exception:                              # noqa: BLE001
        _BASELINE[key] = frozenset()
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)],
                       cwd=str(REPO), capture_output=True)
        shutil.rmtree(wt.parent, ignore_errors=True)
    return _BASELINE[key]


def _summarise_pytest(out: str) -> str:
    m = re.search(r"(\d+ (?:passed|failed)[^\n]*)", out or "")
    return m.group(1) if m else (out or "")[-200:].replace("\n", " ")


def evaluate(response: str, *, parent: str = "HEAD",
             suite_cmd: Optional[list] = None,
             suite_timeout: int = 1200) -> Verdict:
    """Apply a model's patch in an isolated worktree and judge it mechanically."""
    patches = parse_patch(response)
    if not patches:
        return Verdict(REJ_NO_PATCH, "no <<<< SEARCH / ==== REPLACE / >>>> block found")
    test_path, test_src = parse_test(response)
    if not test_path or not test_src.strip():
        return Verdict(REJ_NO_TEST,
                       "no test supplied; a patch without a test that fails at the "
                       "parent cannot be accepted, because nothing then demonstrates "
                       "the defect was real")

    # NOT -x: the gate needs the FULL failing set on both sides to compare them.
    suite_cmd = suite_cmd or ["python3", "-m", "pytest", "bench/tests/", "-q",
                              "--netguard-strict", "-p", "no:randomly"]
    baseline = suite_baseline(parent, suite_cmd, suite_timeout)
    wt = Path(tempfile.mkdtemp(prefix="cdsfl_build_")) / f"wt_{uuid.uuid4().hex[:8]}"
    try:
        rc, out = _run(["git", "worktree", "add", "--detach", str(wt), parent], REPO)
        if rc != 0:
            return Verdict(ERR_HARNESS, f"worktree add failed: {out[-300:]}")

        # ---- (1) the test must FAIL at the parent ---------------------------
        tp = wt / test_path
        tp.parent.mkdir(parents=True, exist_ok=True)
        tp.write_text(test_src, encoding="utf-8")
        rc_before, out_before = _run(
            ["python3", "-m", "pytest", test_path, "-q", "--netguard-strict"], wt, 600)
        if rc_before == 0:
            return Verdict(REJ_TEST_PASSED_BEFORE,
                           "the test passes at the parent commit, so it does not "
                           "demonstrate the defect it claims to fix",
                           test_at_parent=_summarise_pytest(out_before))

        # ---- apply the patch ------------------------------------------------
        touched = []
        for rel, search, replace in patches:
            f = wt / rel
            if not f.is_file():
                return Verdict(REJ_PATCH_DID_NOT_APPLY, f"target not present: {rel}",
                               test_at_parent=_summarise_pytest(out_before))
            src = f.read_text(encoding="utf-8", errors="replace")
            if search not in src:
                return Verdict(REJ_PATCH_DID_NOT_APPLY,
                               f"SEARCH block does not match {rel}",
                               test_at_parent=_summarise_pytest(out_before))
            f.write_text(src.replace(search, replace, 1), encoding="utf-8")
            touched.append(rel)

        # ---- (2) the same test must now PASS --------------------------------
        rc_after, out_after = _run(
            ["python3", "-m", "pytest", test_path, "-q", "--netguard-strict"], wt, 600)
        if rc_after != 0:
            return Verdict(REJ_TEST_FAILED_AFTER,
                           "the patch does not make the model's own test pass",
                           test_at_parent=_summarise_pytest(out_before),
                           test_with_patch=_summarise_pytest(out_after),
                           files_touched=tuple(touched))

        # ---- (3) the full suite must stay green -----------------------------
        rc_suite, out_suite = _run(suite_cmd, wt, suite_timeout)
        new_failures = failing_nodeids(out_suite) - baseline
        if new_failures:
            return Verdict(REJ_SUITE_WENT_RED,
                           "the patch makes its own test pass but breaks "
                           f"{len(new_failures)} test(s) that pass at the parent: "
                           + ", ".join(sorted(new_failures)[:4]),
                           test_at_parent=_summarise_pytest(out_before),
                           test_with_patch=_summarise_pytest(out_after),
                           suite_after=_summarise_pytest(out_suite),
                           files_touched=tuple(touched))

        return Verdict(ACCEPTED,
                       "test fails at parent, passes with the patch, and adds no "
                       "suite failure the parent does not already have",
                       test_at_parent=_summarise_pytest(out_before),
                       test_with_patch=_summarise_pytest(out_after),
                       suite_after=_summarise_pytest(out_suite),
                       files_touched=tuple(touched))
    except subprocess.TimeoutExpired as exc:
        return Verdict(ERR_HARNESS, f"timeout: {exc}")
    except Exception as exc:                        # noqa: BLE001 — reported, not swallowed
        return Verdict(ERR_HARNESS, f"{type(exc).__name__}: {exc}")
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)],
                       cwd=str(REPO), capture_output=True)
        shutil.rmtree(wt.parent, ignore_errors=True)
