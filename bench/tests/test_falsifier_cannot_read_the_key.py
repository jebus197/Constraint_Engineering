"""The falsifier sandbox must not be able to read the answer key.

WHY THIS FILE EXISTS. On 2026-07-29, Exp 48 (chemistry exam), finding C0012
(claim CH-13, the molar mass of 4-aminophenol), a falsifier was attached that
opened the exam's scoring key and printed the complete set of deliberately
planted false claims, instead of computing a molar mass. The runner re-ran it,
because the runner re-runs every falsifier, so the harness itself read the key
it exists to protect. The incident is recorded in
``bench/logs/exp48_chemistry_exam_live_20260729T044134Z.errata`` and the
offending source is preserved verbatim in that run's report under
``registry.entries.C0012.falsifier_code``.

The protection believed to be in place was not encryption. The exam articles and
keys sit outside the repository at Unix mode 600 — and every agent in this
system runs as that user, so mode 600 is not a barrier at all.

THE ACCEPTANCE TEST THAT MATTERS is the pair at the top of this file: the real
historical exploit, read verbatim out of the archive, must be REFUSED; and a
legitimate falsifier from the SAME RUN — one that opens its own staged target by
absolute path — must still execute normally. A guard that blocks honest work is
worse than the hole it closes, so both halves are asserted, and the third test
runs the whole tracked falsifier archive through the gate to hold the
false-positive rate at zero.

Everything here is offline. No model is dispatched and no network is touched.
"""
from __future__ import annotations

import ast
import io
import json
import os
import re
import sys
from contextlib import redirect_stderr
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bench.falsifier_verify import (  # noqa: E402
    INTEGRITY_REJECTIONS,
    INTEGRITY_VIOLATION,
    _sandbox_env,
    execute_python,
    reverify_falsifier,
    scan_falsifier_output,
    scan_falsifier_source,
)

EXP48_REPORT = (REPO_ROOT / "bench" / "logs"
                / "exp48_chemistry_exam_live_20260729T044134Z"
                / "exp48_chemistry_exam_live_report.json")

NORMAL_VERDICTS = {"CONFIRMED", "REFUTED", "ERROR", "UNTOOLABLE"}


def _archived_falsifier(finding_id: str) -> str:
    """The verbatim falsifier source for one Exp 48 finding.

    Read from the archive rather than copied into this file, so the test is
    pinned to the historical record and cannot drift away from it.

    A MISSING ARCHIVE IS A HARD FAILURE, NOT A SKIP. The report is tracked in
    git. If it is gone, the only acceptance test for the live, already-exploited
    hole has silently vanished — which is precisely the class of quiet failure
    this guard was built to stop.
    """
    if not EXP48_REPORT.is_file():
        pytest.fail(
            f"the Exp 48 run report is missing: {EXP48_REPORT}\n"
            "It is tracked in git and carries the only verbatim copy of the real "
            "key-reading falsifier. Restore it (git checkout -- bench/logs/) — do "
            "not weaken this test to make it pass."
        )
    report = json.loads(EXP48_REPORT.read_text(encoding="utf-8"))
    entry = report["registry"]["entries"][finding_id]
    code = entry.get("falsifier_code") or ""
    assert code.strip(), f"{finding_id} carries no falsifier source in the archive"
    return code


# ── the acceptance pair: the real exploit, and real honest work ──────────────

def test_the_real_exp48_c0012_exploit_is_refused():
    """The actual historical exploit, verbatim from the archive, is rejected."""
    exploit = _archived_falsifier("C0012")

    # Sanity: this really is the key-reading source and not something else that
    # has drifted into C0012 — assert the shape the errata describes.
    assert "planted_false" in exploit
    assert "json.load(open(" in exploit

    violations = scan_falsifier_source(exploit)
    assert violations, "the real exploit passed the static scan"

    # It is caught by several independent rules, not balanced on one regex.
    reasons = {reason for reason, _ in violations}
    assert len(reasons) >= 3, f"only one line of defence fired: {reasons}"
    assert any("answer-key" in r for r in reasons)
    assert any("plant" in r or "seed" in r for r in reasons)
    assert any("outside the declared target" in r for r in reasons)

    # The rejection quotes the matched text rather than asserting a violation
    # abstractly, so a human reading the log can see what tripped it.
    matched = " ".join(m for _, m in violations)
    assert "planted_false" in matched or "answer_key" in matched


def test_the_real_exploit_yields_the_third_outcome_not_a_verdict():
    """A rejection must resolve the finding in NEITHER direction."""
    verdict = reverify_falsifier(_archived_falsifier("C0012"))
    assert verdict == INTEGRITY_VIOLATION
    assert verdict not in NORMAL_VERDICTS, (
        "an integrity fault has been collapsed into a verdict on the claim; the "
        "finding would be silently confirmed, dropped or re-asked instead of "
        "escalated to a human"
    )


def test_a_legitimate_falsifier_from_the_same_run_still_executes():
    """Exp 48 C0011 opens its own staged target by absolute home path.

    This is the half of the acceptance test that stops the guard from being
    tightened into uselessness. C0011 is honest work from the same contaminated
    run: it reads the staged exam document and compares two claim strings. If it
    is rejected, every exam falsifier is rejected.
    """
    legit = _archived_falsifier("C0011")
    assert "/CDSFL_review_targets/" in legit, (
        "C0011 no longer reads a staged target by absolute path; pick another "
        "clean falsifier that does, or this test proves nothing"
    )

    assert scan_falsifier_source(legit) == [], (
        "an honest falsifier that opens its own staged target was rejected"
    )

    # It reached the executor and came back with an ordinary outcome. The exam
    # target itself was deliberately removed from the tree after the run, so the
    # assertion is on the CLASS of outcome, not on CONFIRMED specifically.
    verdict = reverify_falsifier(legit)
    assert verdict != INTEGRITY_VIOLATION
    assert verdict in NORMAL_VERDICTS


def test_the_guard_rejects_nothing_else_in_the_whole_tracked_archive():
    """False-positive rate over every falsifier this project has ever run.

    Measured 2026-08-08: 560 unique falsifier sources across 26 archived runs,
    exactly 2 rejected — C0012 (the exploit) and C0015 (a falsifier from the same
    contaminated run whose own text asserts which claim was planted). Zero
    rejections among the other 558.

    If a future rule change makes this fail, the rule is blocking honest work.
    """
    logs = REPO_ROOT / "bench" / "logs"
    sources: dict[str, tuple[str, str]] = {}
    for report in sorted(logs.rglob("*_report.json")):
        try:
            data = json.loads(report.read_text(encoding="utf-8", errors="replace"))
        except (ValueError, OSError):
            continue
        entries = (data.get("registry") or {}).get("entries") or {}
        for cid, entry in entries.items():
            code = (entry or {}).get("falsifier_code") or ""
            if code.strip():
                sources.setdefault(code, (report.parent.name, cid))

    assert len(sources) > 400, (
        f"only {len(sources)} archived falsifiers found; the corpus this test "
        "measures against has gone missing"
    )

    rejected = {sources[code] for code in sources if scan_falsifier_source(code)}
    expected = {("exp48_chemistry_exam_live_20260729T044134Z", "C0012"),
                ("exp48_chemistry_exam_live_20260729T044134Z", "C0015")}
    assert rejected == expected, (
        f"gate rejected {sorted(rejected)}; expected exactly {sorted(expected)}. "
        "New entries are honest falsifiers being blocked."
    )


# ── both execution paths, not just the one named in the brief ────────────────

def test_the_model_facing_tool_refuses_and_does_not_execute(tmp_path):
    """execute_python is the MORE damaging path: its result re-enters the
    reviewing model's context. Exp 48's cost was the panel holding the seeded
    set, not the runner reading it once.

    Non-execution is proved by a side effect, not by the absence of output: the
    snippet's first statement writes a sentinel file. If the sentinel exists,
    the code ran and only its output was suppressed.
    """
    sentinel = tmp_path / "the_falsifier_ran.flag"
    code = (
        f"open({str(sentinel)!r}, 'w').write('ran')\n"
        "import json\n"
        # Fictional path. The shape is what is under test.
        "key = json.load(open('/Users/nobody/exam_keys/chem_answer_key.json'))\n"
        "print(key['planted_false'])\n"
    )
    out = execute_python(code)
    assert "INTEGRITY VIOLATION" in out
    assert "NOT EXECUTED" in out
    assert not sentinel.exists(), (
        "the snippet ran; the gate suppressed the output but did not stop the read"
    )


#: Every way this module could start a child process. The first cut of this
#: test matched ``c.endswith("subprocess.run") or c == "Popen"``, which reads as
#: though it covers Popen and does not: ``ast.unparse`` renders the idiomatic
#: call as ``subprocess.Popen``, which ends with neither. Measured 2026-08-08 by
#: mutation — a third execution site written with ``subprocess.Popen``, and one
#: written with ``os.system``, both passed the test with no gate on them. A
#: structural pin that silently covers less than it claims is the same shape as
#: the defect the module exists to stop.
_SUBPROCESS_LAUNCH_VERBS = {"run", "Popen", "call", "check_call", "check_output"}
_OS_LAUNCH_CALLS = {"os.system", "os.popen", "os.posix_spawn", "os.posix_spawnp"}


def _bare_launch_names(tree: ast.AST) -> set[str]:
    """Launcher verbs pulled into the module namespace by a from-import."""
    bare = {"Popen"}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] == "subprocess":
            bare |= {(a.asname or a.name) for a in node.names
                     if a.name in _SUBPROCESS_LAUNCH_VERBS}
    return bare


def _launches_a_child(name: str, bare: set[str]) -> bool:
    head, _, tail = name.rpartition(".")
    if head.endswith("subprocess"):
        return tail in _SUBPROCESS_LAUNCH_VERBS
    if name in _OS_LAUNCH_CALLS or name.startswith(("os.exec", "os.spawn")):
        return True
    return name in bare


def _ungated_launch_sites(source: str) -> list[str]:
    """Functions in ``source`` that start a child without calling the scanner."""
    tree = ast.parse(source)
    bare = _bare_launch_names(tree)

    def calls(node: ast.AST) -> set[str]:
        return {ast.unparse(sub.func) for sub in ast.walk(node)
                if isinstance(sub, ast.Call)}

    ungated = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        made = calls(fn)
        if any(_launches_a_child(c, bare) for c in made):
            if "scan_falsifier_source" not in made:
                ungated.append(f"{fn.name} (line {fn.lineno})")
    return ungated


def test_every_subprocess_launch_in_the_module_is_gated():
    """A guard on one path with others open is not a guard.

    Structural, not behavioural: parse falsifier_verify.py, find every function
    that launches a child process by ANY mechanism, and require that same
    function to call the scanner. This is what catches a THIRD execution site
    being added later without a gate — the failure this project has already met
    twice (PYTHONPATH pinning, and the file-drop bridge choosing its interpreter
    by what sat beside it).
    """
    module = REPO_ROOT / "bench" / "falsifier_verify.py"
    source = module.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(module))
    bare = _bare_launch_names(tree)

    def calls(node: ast.AST) -> set[str]:
        return {ast.unparse(sub.func) for sub in ast.walk(node)
                if isinstance(sub, ast.Call)}

    launchers = [fn for fn in ast.walk(tree)
                 if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef))
                 and any(_launches_a_child(c, bare) for c in calls(fn))]

    assert len(launchers) >= 2, (
        f"expected both execute_python and reverify_falsifier to launch a "
        f"subprocess; found {[f.name for f in launchers]}"
    )
    assert _ungated_launch_sites(source) == [], (
        f"{_ungated_launch_sites(source)} launch model-authored code without "
        "calling scan_falsifier_source first — an ungated execution site"
    )


@pytest.mark.parametrize("mutant, why", [
    ("def probe(c):\n"
     "    return subprocess.run([sys.executable, '-c', c])\n",
     "subprocess.run"),
    ("def probe(c):\n"
     "    return subprocess.Popen([sys.executable, '-c', c]).wait()\n",
     "subprocess.Popen — missed by the first cut of this test"),
    ("def probe(c):\n"
     "    return os.system(c)\n",
     "os.system"),
    ("def probe(c):\n"
     "    return os.popen(c).read()\n",
     "os.popen"),
    ("from subprocess import check_output\n"
     "def probe(c):\n"
     "    return check_output([sys.executable, '-c', c])\n",
     "a from-imported launcher"),
])
def test_the_ungated_site_detector_actually_detects(mutant, why):
    """The pin above is only worth its line count if it fails on a real mutant.

    Each mutant is a plausible third execution site with no scanner call. If the
    detector returns clean on any of them, the structural guarantee is decorative
    and a future ungated path would land unnoticed.
    """
    module = (REPO_ROOT / "bench" / "falsifier_verify.py").read_text(encoding="utf-8")
    found = _ungated_launch_sites(module + "\n\n" + mutant)
    assert [f.split(" (")[0] for f in found] == ["probe"], (
        f"an ungated third execution site written with {why} was not detected: "
        f"detector returned {found}"
    )


# ── the rejection must be loud ───────────────────────────────────────────────

def test_a_rejection_is_announced_and_recorded():
    """Every failure in this project has historically rendered as a confident
    success. An integrity rejection must be impossible to miss."""
    before = len(INTEGRITY_REJECTIONS)
    buf = io.StringIO()
    with redirect_stderr(buf):
        verdict = reverify_falsifier(
            "import json\n"
            "print(json.load(open('/Users/nobody/k/x_answer_key.json'))['planted_false'])\n"
        )
    assert verdict == INTEGRITY_VIOLATION

    banner = buf.getvalue()
    assert "INTEGRITY VIOLATION" in banner
    assert "NOT executed" in banner
    assert "planted_false" in banner, "the banner does not quote the matched text"
    assert "neither confirmed nor" in banner, (
        "the banner does not say this is not a verdict; a reader could take it "
        "as a decision on the finding"
    )

    assert len(INTEGRITY_REJECTIONS) == before + 1
    record = INTEGRITY_REJECTIONS[-1]
    assert record["where"] == "reverify_falsifier"
    assert record["violations"]


def test_the_runner_gate_escalates_an_unrecognised_verdict():
    """The third outcome only works if the runner's gate fails closed on it.

    reference_runner_v2.apply_falsifier_verdicts confirms on `== "CONFIRMED"`
    and drops on `== "REFUTED"` for sub-criticals; everything else falls to the
    escalation branch. Asserted structurally here because falsifier_verify.py
    cannot enforce what its caller does with the string it returns — and if that
    ever becomes an inequality test, an integrity fault could close a finding.
    """
    runner = (REPO_ROOT / "bench" / "reference_runner_v2.py").read_text(encoding="utf-8")
    gate = runner[runner.index("def apply_falsifier_verdicts"):]
    gate = gate[:gate.index("\ndef ", 10)]

    assert 'if verdict == "CONFIRMED":' in gate, (
        "the confirm branch is no longer an equality test on CONFIRMED; an "
        "unrecognised verdict could now confirm a finding"
    )
    assert 'elif verdict == "REFUTED" and not is_critical:' in gate, (
        "the drop branch is no longer an equality test on REFUTED; an "
        "unrecognised verdict could now drop a finding"
    )
    assert re.search(r"\n\s*else:\s*\n(?:\s*#[^\n]*\n)*\s*e\[\"escalated\"\] = True", gate), (
        "the fall-through branch no longer escalates"
    )


# ── layer 2: the environment the child is handed ─────────────────────────────

def test_environment_scrub_removes_every_variable_naming_the_key(monkeypatch, tmp_path):
    """Named variables, unnamed variables carrying the same value, and inherited
    PYTHONPATH entries under a protected root."""
    store = tmp_path / "store"
    store.mkdir()
    monkeypatch.setenv("CDSFL_STORE", str(store))
    monkeypatch.setenv("CDSFL_VAULT", str(tmp_path / "vault.age"))
    monkeypatch.setenv("CDSFL_TARGETS", str(tmp_path / "targets"))
    monkeypatch.setenv("CDSFL_KEY_DIR", f"{store}{os.pathsep}{tmp_path / 'vault.age'}")
    monkeypatch.setenv("CDSFL_LEGACY_STORES", str(tmp_path / "old"))
    monkeypatch.setenv("CDSFL_SCORING_CONF", str(tmp_path / "scoring.env"))
    # The same location under a name nobody enumerated.
    monkeypatch.setenv("SOME_OPERATOR_SHORTCUT", str(store))
    monkeypatch.setenv("PYTHONPATH", os.pathsep.join([str(store), "/some/legit/lib"]))

    env = _sandbox_env(str(REPO_ROOT))

    for name in ("CDSFL_STORE", "CDSFL_VAULT", "CDSFL_TARGETS", "CDSFL_KEY_DIR",
                 "CDSFL_LEGACY_STORES", "CDSFL_SCORING_CONF"):
        assert name not in env, f"{name} was handed to the child"
    assert "SOME_OPERATOR_SHORTCUT" not in env, (
        "a variable carrying the protected path under an unlisted name survived"
    )

    path_entries = env["PYTHONPATH"].split(os.pathsep)
    assert str(store) not in path_entries, "the key store was left on PYTHONPATH"
    assert "/some/legit/lib" in path_entries, (
        "an unrelated operator PYTHONPATH entry was discarded"
    )
    assert str(REPO_ROOT) in path_entries, "the repo is no longer importable"


def test_the_child_process_sees_no_variable_naming_the_key(monkeypatch, tmp_path):
    """End-to-end: run a benign probe and read what the child actually saw.

    Asserted against the PROTECTED names, not against every CDSFL_ variable —
    the harness legitimately sets unrelated ones (CDSFL_UNDER_PYTEST), and a
    test that forbade all of them would fail for the wrong reason.
    """
    monkeypatch.setenv("CDSFL_STORE", str(tmp_path / "store"))
    monkeypatch.setenv("CDSFL_TARGETS", str(tmp_path / "targets"))
    monkeypatch.setenv("CDSFL_VAULT", str(tmp_path / "vault.age"))
    # The probe names no protected variable, so it passes the source scan on its
    # own merits — the point is what the child can enumerate at run time.
    probe = ("import os\n"
             "print(sorted(k for k in os.environ if k.startswith('CDSFL_')))\n")
    assert scan_falsifier_source(probe) == []
    out = execute_python(probe)
    for name in ("CDSFL_STORE", "CDSFL_TARGETS", "CDSFL_VAULT", "CDSFL_KEY_DIR",
                 "CDSFL_LEGACY_STORES", "CDSFL_SCORING_CONF"):
        assert name not in out, f"the child could still see {name}: {out!r}"


# ── layer 3: the output, for a source that got past layer 1 ──────────────────

def test_obfuscated_source_is_caught_on_its_output():
    """Static rejection is a detector, not a boundary — stated plainly in the
    module docstring. A falsifier that assembles the field name at run time
    passes the source scan, so the output is scanned on a different signal."""
    obfuscated = (
        "field = ''.join(chr(c) for c in "
        "[112,108,97,110,116,101,100,95,102,97,108,115,101])\n"
        "print('recovered set for', field, ': CH-13 CH-19')\n"
    )
    assert scan_falsifier_source(obfuscated) == [], (
        "this fixture no longer tests the output net — the source scan caught it"
    )
    assert scan_falsifier_output("recovered set for planted_false : CH-13")

    buf = io.StringIO()
    with redirect_stderr(buf):
        verdict = reverify_falsifier(obfuscated)
    assert verdict == INTEGRITY_VIOLATION
    assert "INTEGRITY VIOLATION" in buf.getvalue()


def test_output_scan_does_not_reject_an_ordinary_traceback():
    """Path rules must never run against output: a traceback legitimately
    carries interpreter and repository paths."""
    traceback_text = (
        'Traceback (most recent call last):\n'
        f'  File "{REPO_ROOT}/bench/dm/_similarity.py", line 12, in jaccard\n'
        '  File "/Users/someone/Library/Python/3.13/lib/python/site-packages/x.py"\n'
        "ZeroDivisionError: division by zero\n"
    )
    assert scan_falsifier_output(traceback_text) == []


# ── the shapes the brief names, one assertion each ───────────────────────────

@pytest.mark.parametrize("code, why", [
    ("import json; d = json.load(open('/Users/nobody/k/x_answer_key.json'))",
     "answer-key path"),
    ("planted = key['planted_false']", "planted_false"),
    ("conf = open('/Users/nobody/.config/cdsfl/scoring.env').read()",
     "path outside the declared target"),
    ("open('scoring_key.json')", "scoring key by name"),
    ("open('MANIFEST.md').read()", "the target manifest"),
    ("import os; d = os.environ['CDSFL_STORE']", "protected env var by name"),
    ("truth = key['claims']['CH-13']['truth']", "the answer-key schema"),
    ("tiers = doc['difficulty_ladder']", "a key-internal field"),
    ("import os; os.system('cd ~/Library && cat *.json')",
     "escape from the sandbox cwd"),
])
def test_named_reach_for_key_material_is_refused(code, why):
    assert scan_falsifier_source(code), f"not rejected: {why}"
    assert reverify_falsifier(code) == INTEGRITY_VIOLATION


@pytest.mark.parametrize("code", [
    # Ordinary repository work: import the target and exercise it.
    "from bench.dm._similarity import jaccard_similarity\nprint('ok')\n",
    # The repo named by absolute path.
    f"src = open({str(REPO_ROOT / 'bench' / 'falsifier_verify.py')!r}).read()\nprint(len(src))\n",
    # The standard idiom for locating the repo root from a temp snippet. Eight
    # archived falsifiers use exactly this; a naive parent-traversal rule blocks
    # all of them.
    "from pathlib import Path\nroot = Path(__file__).resolve().parent.parent\nprint(root.name)\n",
    # Chemistry done properly — the computation C0012 should have contained.
    "AW = {'C': 12.011, 'H': 1.008, 'N': 14.007, 'O': 15.999}\n"
    "print(round(6*AW['C'] + 7*AW['H'] + AW['N'] + AW['O'], 2))\n",
])
def test_honest_falsifiers_are_untouched(code):
    assert scan_falsifier_source(code) == []
    assert reverify_falsifier(code) != INTEGRITY_VIOLATION


@pytest.mark.parametrize("code, why", [
    ('import os\nfor r, d, f in os.walk("/Users/georgejackson/"):\n    pass\n',
     "bare home directory, trailing slash"),
    ('import os\nfor r, d, f in os.walk("/Users/georgejackson"):\n    pass\n',
     "bare home directory, no trailing slash"),
    ('import glob\nprint(glob.glob("/Users/georgejackson" + "/*/*.json"))\n',
     "glob rooted at the bare home directory"),
    ('import os\nprint(os.listdir("/Users/georgejackson/Developer_Projects/"))\n',
     "an ancestor of the repository"),
])
def test_an_ancestor_of_an_allowed_root_is_not_itself_allowed(code, why):
    """A LITERAL bypass, closed 2026-08-08 — no obfuscation was needed for it.

    The path rule allowed any directory that was a PREFIX of an allowed root as
    well as anything inside one, so naming the bare home directory passed
    because the repository happens to sit under it. Walking the home directory
    is the most direct way to find a key store without naming it, and it was
    waved through verbatim. Separately, the path pattern required a trailing
    slash after the username, so ``"/Users/<name>"`` matched no rule at all.

    Measured over all 457 archived falsifier sources: neither tightening rejects
    anything that was previously accepted, so this costs no honest work.
    """
    assert scan_falsifier_source(code), f"not rejected: {why}"
    assert reverify_falsifier(code) == INTEGRITY_VIOLATION


def test_the_real_repository_is_allowed_even_under_a_shadow_root(tmp_path):
    """convergence_location._felm_verdict_in_shadow re-verifies with
    repo_root=<shadow mirror>. A falsifier that names the real tree by absolute
    path must not become an integrity violation just because the root it was
    handed is a mirror — the repository carries no key material."""
    shadow = tmp_path / "shadow"
    shadow.mkdir()
    code = f"src = open({str(REPO_ROOT / 'bench' / 'routing.py')!r}).read()\nprint(len(src))\n"
    assert scan_falsifier_source(code, repo_root=str(shadow)) == []
    # The key location is still refused under the same shadow root.
    assert scan_falsifier_source(
        "open('/Users/nobody/keys/x_answer_key.json')", repo_root=str(shadow))
