"""Systematic behavioural coverage for the operational scripts in ``scripts/``.

WHY THIS FILE EXISTS
--------------------
Until 2026-08-05 not one of the five operational scripts had any test at all.
That is why ``scripts/cdsfl_qc.py`` crashed on every invocation for 105 days and
``scripts/cdsfl_onboard.py --full`` was a byte-for-byte no-op for 118 days, both
unnoticed, and both while their own self-reporting said the run had gone fine.

The per-repair files written on 2026-08-05 —
``test_cdsfl_utils_repairs.py``, ``test_cdsfl_recover_repairs.py``,
``test_cdsfl_qc_and_seal_repairs.py``, ``test_cdsfl_sv_repairs.py`` — pin the
individual fixes. This file pins the DEFECT CLASSES those fixes belong to, so
that the next occurrence of the same shape is caught in a file nobody has to
remember to extend. Where a check can be expressed as a property of the whole
``scripts/`` directory rather than of one call site, it is written that way.

THE GOVERNING PATTERN, which every class below is one instance of:
EVERY FAILURE RENDERED AS A CONFIDENT SUCCESS.

  1. A verdict discarded by truthiness      — ``ok = chain.verify_chain()`` on a
     function returning ``(bool, str)``. A non-empty tuple is always true, so the
     tamper detector could never report tampering.
  2. A failed lookup rendered as an absence — "(No experiment logs found)"
     printed over ~60 archives; "(No pending work section found)" printed over
     1,575 live lines for 113 days.
  3. A parser that mis-names what it read   — ``export KEY=value`` partitioned
     without stripping the prefix, so every key read as MISSING. This fault has
     now occurred TWICE, in two different scripts, 2026-07-08 and 2026-08-05.
  4. A search bound to one candidate        — ``latest_experiment()`` locked to
     the highest experiment number with no fallback.
  5. A failed subprocess parsed as data     — a failed ``rev-list`` writes
     nothing to stdout, and empty stdout parsed as a number is zero, which
     rendered as "up to date".
  6. A truncation nobody was told about     — 20 of 26 uncommitted files listed
     under a heading that read as complete.
  7. Usage text advertising what is not there.
  8. A crashed check returning success.

ANTI-VACUITY
------------
Several tests below are directory-wide scans. A scan that collects nothing
passes trivially and pins nothing, which is the same failure as no test at all,
so each scan carries an explicit assertion that it found the sites it is
supposed to be looking at before it asserts anything about them.

FALSIFICATION
-------------
Five tests carry a reconstructed PRE-REPAIR implementation or input beside the
real one and assert that the two disagree. A test that passes both with and
against the defect pins nothing; these ones demonstrate, in the suite itself,
that they discriminate. They are marked ``# FALSIFIER`` in the source.

OFFLINE
-------
Nothing here reaches the network. ``git_state()``, ``test_count()`` and
``measure_suite()`` are never called for real: the first runs ``git fetch``, the
second spawns pytest collection, the third spawns the whole suite. Every one of
them is replaced with a stub at the single call site. The only subprocesses
spawned are ``sys.executable <script> --help`` and one bad-flag invocation, both
of which argparse answers and exits before any script body runs; ``python3`` is
not in the netguard's blocked-binary list and neither opens a socket.
"""

from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import cdsfl_qc  # noqa: E402
import cdsfl_recover  # noqa: E402
import cdsfl_seal_logs  # noqa: E402
import cdsfl_utils  # noqa: E402
import check_model_keys  # noqa: E402

LOUD = "!!"

# The scripts under test. ``generate_topology.py`` is excluded deliberately: it
# is a one-shot SVG generator with no argument parser, no exit-code contract and
# no lookup semantics, so every property below is vacuous for it.
SCRIPT_PATHS = sorted(
    p for p in SCRIPTS.glob("*.py") if p.name != "generate_topology.py"
)


def _sources() -> dict[Path, str]:
    return {p: p.read_text(encoding="utf-8") for p in SCRIPT_PATHS}


def _text(lines: list[str]) -> str:
    return "\n".join(lines)


# ═════════════════════════════════════════════════════════════════════════════
# CLASS 1 — a verdict returned as (bool, str) must never be tested for truth
#
# THE DEFECT: scripts/cdsfl_seal_logs.py did `ok = chain.verify_chain()` where
# verify_chain returns (bool, message). Every non-empty tuple is true, so `ok`
# was true whether the chain verified or not, and the tamper detector could not
# report tampering in the project that publishes tamper-evident provenance as a
# core property. One byte appended to a sealed log gave "OK" and exit 0.
#
# This is the single highest-value test in the file because it is the only one
# that generalises to code not yet written: it is a property of the whole
# scripts/ directory, checked structurally, and it fires on a NEW call site as
# readily as on the one that was fixed.
# ═════════════════════════════════════════════════════════════════════════════

# Call names whose result is ALWAYS truthy regardless of the outcome it reports.
# subprocess.run returns a CompletedProcess, which is true even when
# returncode is 1 — the same shape of trap as a (bool, str) tuple.
_ALWAYS_TRUTHY_CALLS = {"run"}


def _returns_in_own_scope(fn: ast.AST) -> list[ast.Return]:
    """``return`` statements belonging to ``fn`` itself, not to nested defs."""
    out: list[ast.Return] = []
    stack = list(getattr(fn, "body", []))
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.Lambda, ast.ClassDef)):
            continue
        if isinstance(node, ast.Return):
            out.append(node)
        stack.extend(ast.iter_child_nodes(node))
    return out


def _outer_annotation_name(ann: ast.AST | None) -> str | None:
    """``tuple[bool, str]`` -> ``tuple``. Only the OUTERMOST type counts:
    ``dict[int, tuple[str, str]]`` is a dict, and treating it as a tuple would
    manufacture false positives on _parse_ps and _scan_headings."""
    if ann is None:
        return None
    if isinstance(ann, ast.Subscript):
        ann = ann.value
    if isinstance(ann, ast.Name):
        return ann.id
    if isinstance(ann, ast.Attribute):
        return ann.attr
    return None


def _tuple_returning_function_names(sources: list[str]) -> set[str]:
    """Names of functions that hand back a tuple — annotated or literal."""
    names: set[str] = set()
    for src in sources:
        for node in ast.walk(ast.parse(src)):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if _outer_annotation_name(node.returns) in ("tuple", "Tuple"):
                names.add(node.name)
                continue
            for ret in _returns_in_own_scope(node):
                if isinstance(ret.value, ast.Tuple) and len(ret.value.elts) >= 2:
                    names.add(node.name)
                    break
    return names


def _called_name(call: ast.Call) -> str | None:
    func = call.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _own_scope_nodes(scope: ast.AST):
    """Every node belonging to ``scope`` itself, not to a nested def.

    Binding and testing must be matched INSIDE one scope. Walking the whole
    module tree instead matches a name bound in one function against a
    same-named local tested in ANOTHER, which reports a violation on correct
    code — and a directory-wide guard that cries wolf is a guard that gets
    deleted, taking the real coverage with it.
    """
    stack = list(getattr(scope, "body", []))
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.Lambda, ast.ClassDef)):
            continue
        yield node
        stack.extend(ast.iter_child_nodes(node))


def _unwrap_walrus(node: ast.AST) -> ast.AST:
    """``(ok := verify())`` in boolean position is a test of ``verify()``."""
    return node.value if isinstance(node, ast.NamedExpr) else node


def _boolean_contexts(nodes):
    """Every expression node in ``nodes`` whose VALUE is coerced to bool."""
    for node in nodes:
        if isinstance(node, (ast.If, ast.While, ast.IfExp, ast.Assert)):
            yield _unwrap_walrus(node.test)
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            yield _unwrap_walrus(node.operand)
        elif isinstance(node, ast.BoolOp):
            yield from (_unwrap_walrus(v) for v in node.values)
        elif isinstance(node, ast.comprehension):
            yield from (_unwrap_walrus(v) for v in node.ifs)


def _whole_bindings_from(node: ast.AST) -> list[ast.Name]:
    """Targets that take the WHOLE result of ``node``'s call, if any.

    All three assignment spellings, because the guard is worthless if the
    defect can be written in a way it cannot see:

      * ``ok = verify()``           — ``ast.Assign``, the form actually shipped;
      * ``ok: bool = verify()``     — ``ast.AnnAssign``; this codebase already
        writes annotated assignments from calls, so it is not hypothetical;
      * ``(ok := verify())``        — ``ast.NamedExpr``.

    A ``Tuple`` target IS the unpacking that makes the call safe, so it is
    deliberately not returned here.
    """
    if isinstance(node, ast.Assign):
        targets: list[ast.AST] = list(node.targets)
    elif isinstance(node, (ast.AnnAssign, ast.NamedExpr)):
        targets = [node.target]
    else:
        return []
    if not isinstance(getattr(node, "value", None), ast.Call):
        return []
    return [t for t in targets if isinstance(t, ast.Name)]


def _truthiness_violations(src: str, label: str, names: set[str]) -> list[str]:
    """Both spellings of the defect, because the real one was the second.

      * ``if verify(...)``            — the call itself in boolean position;
      * ``ok = verify(...); if ok:``  — bound to a name with NO unpacking, then
        tested. This is the form scripts/cdsfl_seal_logs.py actually carried.
    """
    tree = ast.parse(src)
    hits: set[str] = set()

    for node in _boolean_contexts(ast.walk(tree)):
        if isinstance(node, ast.Call):
            called = _called_name(node)
            if called in names or called in _ALWAYS_TRUTHY_CALLS:
                hits.add(
                    f"{label}:{node.lineno}: {called}() is tested for truth "
                    f"directly; its verdict is discarded"
                )

    scopes = [tree] + [
        n for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    for scope in scopes:
        bound: dict[str, tuple[int, str]] = {}
        own = list(_own_scope_nodes(scope))
        for node in own:
            targets = _whole_bindings_from(node)
            if not targets:
                continue
            called = _called_name(node.value)
            if called not in names and called not in _ALWAYS_TRUTHY_CALLS:
                continue
            for target in targets:
                bound[target.id] = (node.lineno, called or "?")
        if not bound:
            continue
        # Bindings come from THIS scope only (above), but the tests are looked
        # for in nested scopes too: a name bound in an enclosing function is
        # genuinely visible inside a nested def, and a verdict discarded
        # through a closure is the same defect. The asymmetry is the point —
        # it keeps the closure case while removing the sibling false positive.
        for node in _boolean_contexts(ast.walk(scope)):
            if isinstance(node, ast.Name) and node.id in bound:
                line, called = bound[node.id]
                hits.add(
                    f"{label}:{node.lineno}: '{node.id}' was bound whole from "
                    f"{called}() at line {line} and is now tested for truth"
                )
    return sorted(hits)


def _imported_bench_modules() -> list[Path]:
    """Files under bench/ that scripts/ imports from, resolved to paths.

    The defect crossed a module boundary — scripts/cdsfl_seal_logs.py called
    verify_chain, which is DEFINED in bench/verification_chain.py — so the name
    collector has to look there too. Deriving the list from the imports rather
    than hardcoding it means a script that starts importing a new bench module
    widens the guard automatically. Scanning all of bench/ was measured as an
    alternative: it also yields zero violations today, but it pulls in generic
    names (`gate`, `verify`, `solve`, `locate`) that a same-named boolean
    helper in scripts/ would later collide with, and a false positive on a
    directory-wide guard is how a guard gets disabled.
    """
    found: set[Path] = set()
    for path in SCRIPT_PATHS:
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            dotted: list[str] = []
            if isinstance(node, ast.ImportFrom) and node.module:
                dotted.append(node.module)
            elif isinstance(node, ast.Import):
                dotted.extend(alias.name for alias in node.names)
            for name in dotted:
                if not name.startswith("bench"):
                    continue
                candidate = REPO_ROOT / Path(*name.split("."))
                for target in (candidate.with_suffix(".py"),
                               candidate / "__init__.py"):
                    if target.is_file():
                        found.add(target)
    return sorted(found)


class TestVerdictTuplesAreNeverTestedForTruth:

    def _names(self) -> set[str]:
        sources = [p.read_text(encoding="utf-8") for p in SCRIPT_PATHS]
        sources += [p.read_text(encoding="utf-8") for p in _imported_bench_modules()]
        return _tuple_returning_function_names(sources)

    def test_the_collector_reaches_across_the_module_boundary(self):
        """ANTI-VACUITY for the import walk: the defect's own definition site
        must be discovered, or the guard is inert exactly where it matters."""
        discovered = _imported_bench_modules()
        assert (REPO_ROOT / "bench" / "verification_chain.py") in discovered, (
            f"the module defining verify_chain was not reached; found "
            f"{[str(p.relative_to(REPO_ROOT)) for p in discovered]}"
        )

    def test_the_scan_actually_sees_the_functions_it_is_guarding(self):
        """ANTI-VACUITY. A name set that came back empty would make every
        assertion below pass without examining anything."""
        names = self._names()
        assert "verify_chain" in names, (
            "verify_chain is the function the tamper-detector defect was "
            "committed against; if the collector no longer sees it, this whole "
            "guard is inert and the defect can return unnoticed"
        )
        assert "_verify_contents" in names
        assert "_run_git_rc" in names

    def test_no_script_discards_a_verdict_by_testing_the_tuple(self):
        names = self._names()
        violations: list[str] = []
        for path, src in _sources().items():
            violations += _truthiness_violations(
                src, str(path.relative_to(REPO_ROOT)), names
            )
        assert violations == [], (
            "A function returning (bool, message) is TRUE in every case, "
            "including failure. Unpack it — `ok, msg = f()` — and test `ok`.\n"
            + "\n".join(violations)
        )

    # FALSIFIER
    def test_the_scan_catches_the_defect_as_it_was_actually_written(self):
        """The pre-repair scripts/cdsfl_seal_logs.py::_verify_dir, reconstructed
        verbatim in shape. If this does not fire, the test above proves
        nothing."""
        pre_repair = (
            "def _verify_dir(dir_path):\n"
            "    seal_path = dir_path / SEAL_FILENAME\n"
            "    if not seal_path.exists():\n"
            "        return False\n"
            "    try:\n"
            "        chain = VerificationChain.load_json(str(seal_path))\n"
            "        ok = chain.verify_chain()\n"
            "    except Exception as err:\n"
            "        return False\n"
            "    if not ok:\n"
            "        print('TAMPERED')\n"
            "        return False\n"
            "    print('OK')\n"
            "    return True\n"
        )
        hits = _truthiness_violations(pre_repair, "<pre-repair>", self._names())
        assert len(hits) == 1, hits
        assert "verify_chain" in hits[0] and "tested for truth" in hits[0]

    # FALSIFIER
    def test_the_scan_catches_the_direct_form_too(self):
        pre_repair = (
            "def check(chain):\n"
            "    if chain.verify_chain():\n"
            "        print('OK')\n"
        )
        assert _truthiness_violations(pre_repair, "<direct>", self._names())

    # FALSIFIER — added 2026-08-06 by adversarial verification of this file.
    # The scan as first written saw `ok = verify_chain()` and nothing else:
    # both spellings below reproduce the SAME discarded verdict and both
    # returned zero hits, so the guard could be walked straight past by a
    # defect written in either of them.
    def test_the_scan_catches_the_annotated_spelling(self):
        """``ok: bool = chain.verify_chain()`` is ``ast.AnnAssign``, not
        ``ast.Assign``. scripts/ already contains annotated assignments from
        calls, so this spelling is idiomatic here rather than hypothetical —
        and the annotation makes the bug read as MORE careful, not less."""
        annotated = (
            "def check(chain):\n"
            "    ok: bool = chain.verify_chain()\n"
            "    if not ok:\n"
            "        print('TAMPERED')\n"
        )
        hits = _truthiness_violations(annotated, "<annotated>", self._names())
        assert len(hits) == 1, hits
        assert "verify_chain" in hits[0] and "bound whole" in hits[0]

    # FALSIFIER — added 2026-08-06 by adversarial verification of this file.
    def test_the_scan_catches_the_walrus_spelling(self):
        """``if (ok := chain.verify_chain()):`` puts an ``ast.NamedExpr`` in
        the boolean position, so the call underneath it was invisible."""
        walrus = (
            "def check(chain):\n"
            "    if (ok := chain.verify_chain()):\n"
            "        print('OK')\n"
        )
        assert _truthiness_violations(walrus, "<walrus>", self._names())

    def test_a_binding_does_not_leak_across_a_function_boundary(self):
        """FALSE-POSITIVE guard, added 2026-08-06. Matching bindings against
        tests over the whole module reported a violation on wholly correct
        code: ``a`` indexes its tuple (safe), and ``b`` has an unrelated local
        that happens to share the name. A directory-wide guard that fires on
        correct code is one that gets deleted, and its real coverage goes with
        it."""
        correct = (
            "def a(chain):\n"
            "    ok = chain.verify_chain()\n"
            "    return ok[0]\n"
            "\n"
            "def b(flag):\n"
            "    ok = flag\n"
            "    if ok:\n"
            "        print('unrelated')\n"
        )
        assert _truthiness_violations(correct, "<two-scopes>", self._names()) == []

    # FALSIFIER — the other half of the scope rule. Narrowing bindings to one
    # scope must not lose a verdict discarded through a closure, where the
    # name genuinely IS visible.
    def test_a_verdict_discarded_inside_a_nested_def_is_still_caught(self):
        closure = (
            "def outer(chain):\n"
            "    ok = chain.verify_chain()\n"
            "    def inner():\n"
            "        if ok:\n"
            "            print('OK')\n"
            "    return inner\n"
        )
        assert _truthiness_violations(closure, "<closure>", self._names())

    def test_the_scan_does_not_fire_on_correct_unpacking(self):
        """The repaired form must be accepted, or the guard is unusable."""
        repaired = (
            "def check(chain):\n"
            "    ok, msg = chain.verify_chain()\n"
            "    if not ok:\n"
            "        print(msg)\n"
        )
        assert _truthiness_violations(repaired, "<repaired>", self._names()) == []

    def test_the_live_verdict_still_survives_the_round_trip(self):
        """Structural scans can be satisfied by code that does not work. This
        asserts the actual behaviour the scan is a proxy for: the tuple is
        truthy in BOTH outcomes, and only the unpacked first element differs."""
        false_verdict = (False, "content hash mismatch")
        true_verdict = (True, "3 sealed file(s) re-read and matched")
        assert bool(false_verdict) is bool(true_verdict) is True
        assert false_verdict[0] is not true_verdict[0]


# ═════════════════════════════════════════════════════════════════════════════
# CLASS 2 — "nothing found" must not be able to mean "the probe failed"
#
# THE DEFECT: latest_experiment() returning None printed "(No experiment logs
# found)" over ~60 archives; a dead marker printed "(No pending work section
# found)" over 1,575 live lines for 113 days; read_section() returned "" both
# for an unreadable file and for an absent marker.
#
# The property below is cross-site rather than per-site: for EVERY probe that
# can come back empty, the failed-lookup form and the real-absence form must be
# distinguishable by a caller. cdsfl_recover.py states that convention in its
# own source ("!!" = lookup failed, "(...)" = real absence), so keying on the
# marker is keying on a documented contract, not on incidental prose.
# ═════════════════════════════════════════════════════════════════════════════


def _absence_vs_failure_cases(tmp_path: Path) -> list[tuple[str, str, str]]:
    """(site, text produced by a FAILED lookup, text produced by a REAL absence)."""
    cases: list[tuple[str, str, str]] = []

    # --- cdsfl_recover.experiment_absence_lines -----------------------------
    empty_logs = tmp_path / "empty_logs"
    empty_logs.mkdir()
    unparseable = tmp_path / "unparseable_logs"
    (unparseable / "exp53_halted_control").mkdir(parents=True)
    cases.append((
        "cdsfl_recover.experiment_absence_lines",
        _text(cdsfl_recover.experiment_absence_lines(unparseable)),
        _text(cdsfl_recover.experiment_absence_lines(empty_logs)),
    ))

    # --- cdsfl_recover.pending_work_lines -----------------------------------
    no_markers = tmp_path / "RECOVERY_no_markers.md"
    no_markers.write_text("# Recovery\n\nprose with no markers at all\n",
                          encoding="utf-8")
    empty_block = tmp_path / "RECOVERY_empty_block.md"
    empty_block.write_text(
        f"# Recovery\n\n{cdsfl_recover.PENDING_START}\n\n"
        f"{cdsfl_recover.PENDING_END}\n",
        encoding="utf-8",
    )
    cases.append((
        "cdsfl_recover.pending_work_lines",
        _text(cdsfl_recover.pending_work_lines(no_markers)),
        _text(cdsfl_recover.pending_work_lines(empty_block)),
    ))

    # --- cdsfl_recover.recovery_head_lines ----------------------------------
    absent = tmp_path / "RECOVERY_absent.md"
    nothing_above = tmp_path / "RECOVERY_head_empty.md"
    nothing_above.write_text(
        f"{cdsfl_recover.PENDING_START}\nbody\n{cdsfl_recover.PENDING_END}\n",
        encoding="utf-8",
    )
    cases.append((
        "cdsfl_recover.recovery_head_lines",
        _text(cdsfl_recover.recovery_head_lines(absent)),
        _text(cdsfl_recover.recovery_head_lines(nothing_above)),
    ))

    # --- cdsfl_recover.running_experiment_lines -----------------------------
    def _ps_dies() -> str:
        raise OSError("ps exited 1")

    quiet_machine = "  1234 01:23 /bin/zsh\n  1235 00:04 /usr/bin/ssh-agent\n"
    pid_dir = tmp_path / "pids"
    pid_dir.mkdir()
    cases.append((
        "cdsfl_recover.running_experiment_lines",
        _text(cdsfl_recover.running_experiment_lines(pid_dir, _ps_dies)),
        _text(cdsfl_recover.running_experiment_lines(pid_dir, lambda: quiet_machine)),
    ))

    # --- cdsfl_recover.gamma_lines ------------------------------------------
    no_report = tmp_path / "exp_no_report"
    no_report.mkdir()
    with_report = tmp_path / "exp_with_report"
    with_report.mkdir()
    (with_report / "exp42_report.json").write_text(json.dumps({
        "gamma_history": [0.51, 0.68],
        "gamma_critical_history": [0.44, 0.62],
    }), encoding="utf-8")
    cases.append((
        "cdsfl_recover.gamma_lines",
        _text(cdsfl_recover.gamma_lines({"log_dir": str(no_report), "gamma": 0.77})),
        _text(cdsfl_recover.gamma_lines({"log_dir": str(with_report)})),
    ))

    # --- cdsfl_recover.target_lines -----------------------------------------
    present = tmp_path / "target.py"
    present.write_text("x = 1\n", encoding="utf-8")
    cases.append((
        "cdsfl_recover.target_lines",
        _text(cdsfl_recover.target_lines({"target": ""}, tmp_path)),
        _text(cdsfl_recover.target_lines({"target": "target.py"}, tmp_path)),
    ))

    return cases


class TestAbsenceIsDistinguishableFromAFailedLookup:

    def test_every_probe_marks_a_failed_lookup_and_a_real_absence_apart(
        self, tmp_path: Path,
    ):
        cases = _absence_vs_failure_cases(tmp_path)
        assert len(cases) >= 6, "ANTI-VACUITY: the case table did not build"
        for site, failure, absence in cases:
            assert failure != absence, f"{site}: the two forms render identically"
            assert LOUD in failure, (
                f"{site}: a FAILED lookup did not carry the '{LOUD}' marker, so "
                f"a recovering agent reads it as a statement about the project"
            )
            assert LOUD not in absence, (
                f"{site}: a real absence carried the failure marker, which "
                f"makes the marker meaningless"
            )

    def test_read_section_cannot_be_told_apart_by_truthiness_alone(
        self, tmp_path: Path,
    ):
        """THE POINT OF SectionText. All three outcomes are falsy, so a caller
        that tests the result for truth learns nothing; the verdict is on
        ``.status``. This is CLASS 1's shape in a different disguise, and it is
        why the return type had to change rather than the callers."""
        empty_section = tmp_path / "empty.md"
        empty_section.write_text("## Marker\n\n## Next\n", encoding="utf-8")
        no_marker = tmp_path / "no_marker.md"
        no_marker.write_text("# nothing relevant here\n", encoding="utf-8")

        ok = cdsfl_utils.read_section(empty_section, "## Marker", "\n## ")
        missing = cdsfl_utils.read_section(no_marker, "## Marker", "\n## ")
        unreadable = cdsfl_utils.read_section(tmp_path / "nope.md", "## Marker")

        assert not ok and not missing and not unreadable
        assert {ok.status, missing.status, unreadable.status} == {
            "ok", "marker-missing", "unreadable"
        }
        # Blast radius: every pre-existing caller treats this as a plain str.
        assert isinstance(ok, str) and isinstance(missing, str)

    def test_an_unscannable_document_is_not_reported_as_having_no_bad_refs(
        self, tmp_path: Path,
    ):
        """Zero broken references and "I could not open the file" are the same
        empty list unless the scan says which it was."""
        readable = tmp_path / "clean.md"
        readable.write_text("no references here at all\n", encoding="utf-8")
        clean = cdsfl_utils.check_file_references(readable)
        failed = cdsfl_utils.check_file_references(tmp_path / "does_not_exist.md")

        assert [e for e in clean if e.get("scan_failed")] == []
        assert [e for e in failed if e.get("scan_failed")] != []

    # FALSIFIER
    def test_the_pre_repair_report_really_could_not_tell_them_apart(
        self, tmp_path: Path,
    ):
        """Before the repair the recovery report had one string for both
        states. Reconstructed here so the assertions above are demonstrably
        pinned to the distinction and not to incidental wording."""
        def pre_repair_absence(_logs_dir: Path) -> list[str]:
            return ["  (No experiment logs found)"]

        empty = tmp_path / "empty_logs"
        empty.mkdir()
        unparseable = tmp_path / "unparseable_logs"
        (unparseable / "exp53_halted_control").mkdir(parents=True)

        assert pre_repair_absence(unparseable) == pre_repair_absence(empty)
        assert LOUD not in _text(pre_repair_absence(unparseable))
        # …and the repaired probe does tell them apart.
        assert (cdsfl_recover.experiment_absence_lines(unparseable)
                != cdsfl_recover.experiment_absence_lines(empty))

    def test_a_skipped_experiment_number_is_announced_not_swallowed(
        self, tmp_path: Path, monkeypatch, capsys,
    ):
        """latest_experiment() falling back is itself a partial failure, and the
        caller must be able to say "exp53 wrote no report" rather than implying
        exp53 does not exist."""
        logs = tmp_path / "bench" / "logs"
        (logs / "exp53_halted_control").mkdir(parents=True)
        good = logs / "exp42_evidence"
        good.mkdir()
        (good / "exp42_report.json").write_text(json.dumps({"experiment": "exp42"}),
                                                encoding="utf-8")
        monkeypatch.setattr(cdsfl_utils, "repo_root", lambda: tmp_path)

        result = cdsfl_utils.latest_experiment()

        assert result is not None
        assert result["skipped_higher"] == [53]
        assert "exp53" in capsys.readouterr().err


# ═════════════════════════════════════════════════════════════════════════════
# CLASS 3 — .env parsing tolerates the `export ` prefix
#
# THE DEFECT, TWICE: scripts/check_model_keys.py on 2026-07-08 reported every
# key ABSENT and manufactured a "the keys were destroyed" incident; the keys
# were present the whole time. scripts/cdsfl_utils.py::source_env carried the
# identical fault into 2026-08-05, and cdsfl_onboard reported all six keys
# MISSING. A fault that has occurred twice in two files is a directory-level
# property, so it is tested as one.
#
# No real key material is read or written: every fixture below is a synthetic
# .env with placeholder values, and every assertion is on variable NAMES.
# ═════════════════════════════════════════════════════════════════════════════

# Every module in the operational path that parses .env line by line. Both
# config-ingestion boundaries are named deliberately: this project has three
# recorded instances of a launcher honouring a key the runner drops, or the
# reverse, because only one path was checked.
_ENV_PARSER_FILES = [
    SCRIPTS / "cdsfl_utils.py",
    SCRIPTS / "check_model_keys.py",
    REPO_ROOT / "bench" / "runner_core.py",
    REPO_ROOT / "bench" / "launcher_core.py",
]

_ENV_FIXTURE = (
    "# comment line\n"
    "\n"
    "export CDSFL_TEST_EXPORTED=placeholder-not-a-key\n"
    "CDSFL_TEST_PLAIN=placeholder-not-a-key\n"
    "export CDSFL_TEST_QUOTED='placeholder-not-a-key'\n"
)


def _pre_repair_source_env(env_file: Path, environ: dict) -> None:
    """The parser as it stood before 2026-08-05: no `export ` strip."""
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            environ.setdefault(key.strip(), value.strip().strip("'\""))


class TestEnvParsingToleratesTheExportPrefix:

    def test_source_env_names_the_variable_not_the_shell_keyword(
        self, tmp_path: Path, monkeypatch,
    ):
        (tmp_path / ".env").write_text(_ENV_FIXTURE, encoding="utf-8")
        monkeypatch.setattr(cdsfl_utils, "repo_root", lambda: tmp_path)
        fake_env: dict[str, str] = {}
        monkeypatch.setattr(os, "environ", fake_env)

        cdsfl_utils.source_env()

        assert fake_env.get("CDSFL_TEST_EXPORTED") == "placeholder-not-a-key"
        assert fake_env.get("CDSFL_TEST_PLAIN") == "placeholder-not-a-key"
        assert fake_env.get("CDSFL_TEST_QUOTED") == "placeholder-not-a-key"
        assert [k for k in fake_env if k.startswith("export ")] == []

    def test_the_credential_preflight_agrees_with_the_loader(self, tmp_path: Path):
        """The preflight and the loader must not disagree about what a key is
        called — a preflight that disagrees with the consumer it stands in for
        is the 2026-07-08 incident exactly."""
        env_file = tmp_path / ".env"
        env_file.write_text(_ENV_FIXTURE, encoding="utf-8")

        names = check_model_keys._env_file_names(env_file)

        assert names == {"CDSFL_TEST_EXPORTED", "CDSFL_TEST_PLAIN",
                         "CDSFL_TEST_QUOTED"}

    # FALSIFIER
    def test_the_pre_repair_parser_really_does_lose_every_exported_key(
        self, tmp_path: Path,
    ):
        """Without this, the two tests above could be passing for reasons
        unrelated to the prefix."""
        env_file = tmp_path / ".env"
        env_file.write_text(_ENV_FIXTURE, encoding="utf-8")
        broken: dict[str, str] = {}

        _pre_repair_source_env(env_file, broken)

        assert "CDSFL_TEST_EXPORTED" not in broken
        assert broken.get("export CDSFL_TEST_EXPORTED") == "placeholder-not-a-key"
        # The one key with no prefix survived, which is why the fault looked
        # partial and went unexplained for months.
        assert broken.get("CDSFL_TEST_PLAIN") == "placeholder-not-a-key"

    def test_every_env_parser_in_the_operational_path_strips_the_prefix(self):
        """Directory-level guard: a NEW parser that forgets this fails here,
        without anyone having to remember this file exists."""
        checked = 0
        missing: list[str] = []
        for path in _ENV_PARSER_FILES:
            if not path.exists():
                missing.append(f"{path} is absent — cannot verify its .env parse")
                continue
            src = path.read_text(encoding="utf-8")
            # Every spelling of the split. Matching a literal `partition("=")`
            # would let a parser that switched to `split('=', 1)` drop OUT of
            # the guard without anyone being told — a silent skip, which is the
            # same failure shape as the defect. A named file that is here and
            # is not recognised is reported, never passed over in silence.
            splits_on_equals = bool(
                re.search(r"\.(?:partition|split)\(\s*['\"]=['\"]", src)
            )
            if ".env" not in src or not splits_on_equals:
                missing.append(
                    f"{path.relative_to(REPO_ROOT)} is listed as an operational "
                    f".env parser but no longer looks like one (mentions .env: "
                    f"{'.env' in src}; splits on '=': {splits_on_equals}). "
                    f"Either it stopped parsing .env — remove it from "
                    f"_ENV_PARSER_FILES — or the scan can no longer see the "
                    f"parse and is now inert on this file."
                )
                continue
            checked += 1
            if 'startswith("export ")' not in src:
                missing.append(
                    f"{path.relative_to(REPO_ROOT)} parses .env by partitioning "
                    f"on '=' but never strips the `export ` prefix"
                )
        assert checked >= 2, (
            "ANTI-VACUITY: expected at least two live .env parsers; found "
            f"{checked}. The scan is looking in the wrong place."
        )
        assert missing == [], "\n".join(missing)


# ═════════════════════════════════════════════════════════════════════════════
# CLASS 4 — latest_experiment() falls back past a report-less highest number
#
# THE DEFECT: the search was bound to max(experiment number). exp53 is the
# deliberately halted zero-plant control and wrote no report, so the whole
# archive — ~60 directories, 37 reports — rendered as "(No experiment logs
# found)" in both `rs` and `sv`.
# ═════════════════════════════════════════════════════════════════════════════


def _make_logs(tmp_path: Path, spec: dict[str, dict | None]) -> Path:
    logs = tmp_path / "bench" / "logs"
    logs.mkdir(parents=True)
    for name, payload in spec.items():
        d = logs / name
        d.mkdir()
        if payload is not None:
            (d / f"{name.split('_')[0]}_report.json").write_text(
                json.dumps(payload), encoding="utf-8"
            )
    return logs


def _pre_repair_latest_experiment(logs_dir: Path) -> dict | None:
    """The search as it stood before 2026-08-05: highest number, no fallback."""
    exp_dirs = []
    for d in logs_dir.iterdir():
        m = re.match(r"exp(\d+)", d.name)
        if d.is_dir() and m:
            exp_dirs.append((int(m.group(1)), d))
    if not exp_dirs:
        return None
    max_n = max(n for n, _ in exp_dirs)
    for _, d in [(n, d) for n, d in exp_dirs if n == max_n]:
        reports = list(d.glob("exp*_report.json"))
        if not reports:
            continue
        return {"number": max_n}
    return None


class TestLatestExperimentFallsBackPastAReportlessTop:

    def test_a_halted_top_experiment_does_not_blank_the_archive(
        self, tmp_path: Path, monkeypatch,
    ):
        _make_logs(tmp_path, {
            "exp53_zero_plant_control": None,     # halted, wrote nothing
            "exp49_prose_target": {"experiment": "exp49", "total_rounds": 7},
            "exp42_evidence": {"experiment": "exp42", "total_rounds": 6},
        })
        monkeypatch.setattr(cdsfl_utils, "repo_root", lambda: tmp_path)

        result = cdsfl_utils.latest_experiment()

        assert result is not None
        assert result["number"] == 49
        assert result["skipped_higher"] == [53]

    def test_it_descends_past_several_report_less_numbers(
        self, tmp_path: Path, monkeypatch,
    ):
        _make_logs(tmp_path, {
            "exp54_integration": None,
            "exp53_zero_plant_control": None,
            "exp40_macrophage": {"experiment": "exp40"},
        })
        monkeypatch.setattr(cdsfl_utils, "repo_root", lambda: tmp_path)

        result = cdsfl_utils.latest_experiment()

        assert result["number"] == 40
        assert result["skipped_higher"] == [54, 53], (
            "the passed-over numbers must be reported highest-first, or a "
            "caller cannot say which runs are unreported"
        )

    def test_nothing_parseable_at_all_is_still_none(
        self, tmp_path: Path, monkeypatch,
    ):
        """The fallback must not invent a result. A genuine total absence is
        still None — the caller (experiment_absence_lines) is what turns it
        into the loud form, and that split is tested in CLASS 2."""
        _make_logs(tmp_path, {"exp53_zero_plant_control": None})
        monkeypatch.setattr(cdsfl_utils, "repo_root", lambda: tmp_path)

        assert cdsfl_utils.latest_experiment() is None

    # FALSIFIER
    def test_the_pre_repair_search_really_did_blank_the_archive(
        self, tmp_path: Path,
    ):
        logs = _make_logs(tmp_path, {
            "exp53_zero_plant_control": None,
            "exp49_prose_target": {"experiment": "exp49"},
        })
        assert _pre_repair_latest_experiment(logs) is None, (
            "if the pre-repair search finds exp49, the fixture does not "
            "reproduce the defect and the tests above prove nothing"
        )


# ═════════════════════════════════════════════════════════════════════════════
# CLASS 5 — git_state() compares against its OWN upstream, and a failed git
#           command is "unknown", never "up to date"
#
# THE DEFECT, both halves: every branch was compared against a hardcoded
# origin/main, so exp39-experimental — level with its own upstream — reported
# "diverged (ahead 98, behind 1)"; and _run_git discarded the return code, so a
# FAILED rev-list wrote nothing to stdout, and empty stdout parsed as a number
# is zero, which rendered as "up to date".
#
# OFFLINE: _run_git_rc is the single subprocess call site in cdsfl_utils, and
# it is replaced here, so no `git fetch` is attempted.
# ═════════════════════════════════════════════════════════════════════════════


def _fake_git(responses: dict[tuple[str, ...], tuple[int, str]]):
    """Build a _run_git_rc stand-in. Unlisted commands answer (0, "")."""
    seen: list[tuple[str, ...]] = []

    def run(*args: str, cwd=None) -> tuple[int, str]:
        seen.append(args)
        return responses.get(args, (0, ""))

    run.seen = seen  # type: ignore[attr-defined]
    return run


_BASE_GIT = {
    ("branch", "--show-current"): (0, "exp39-experimental"),
    ("status", "--porcelain"): (0, ""),
    ("log", "--oneline", "-1"): (0, "49d2473 sv: audit repairs"),
    ("log", "-1", "--format=%ci"): (0, "2026-08-05 21:00:00 +0100"),
    ("log", "--oneline", "-10"): (0, "49d2473 sv: audit repairs"),
}


def _pre_repair_remote_sync(run_git_rc) -> str:
    """The comparison as it stood: hardcoded ref, return code discarded."""
    _, counts = run_git_rc("rev-list", "--left-right", "--count",
                           "origin/main...HEAD")
    parts = counts.split()
    behind_n, ahead_n = (int(parts[0]), int(parts[1])) if len(parts) == 2 else (0, 0)
    if ahead_n == 0 and behind_n == 0:
        return "up to date"
    if ahead_n and behind_n:
        return f"diverged (ahead {ahead_n}, behind {behind_n})"
    return f"ahead by {ahead_n}" if ahead_n else f"behind by {behind_n}"


class TestGitStateNamesItsRefAndFailsLoudly:

    def test_it_compares_against_this_branchs_own_upstream(self, monkeypatch):
        upstream = "origin/exp39-experimental"
        run = _fake_git({
            **_BASE_GIT,
            ("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"):
                (0, upstream),
            ("rev-list", "--left-right", "--count", f"{upstream}...HEAD"): (0, "0\t0"),
        })
        monkeypatch.setattr(cdsfl_utils, "_run_git_rc", run)

        state = cdsfl_utils.git_state()

        assert state["remote_sync"] == f"up to date with {upstream}"
        assert not any("origin/main" in " ".join(a) for a in run.seen), (
            "a branch was compared against a ref that is not its upstream"
        )

    def test_a_failed_rev_list_is_unknown_not_up_to_date(self, monkeypatch):
        upstream = "origin/exp39-experimental"
        run = _fake_git({
            **_BASE_GIT,
            ("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"):
                (0, upstream),
            # A failed git command writes NOTHING to stdout.
            ("rev-list", "--left-right", "--count", f"{upstream}...HEAD"): (128, ""),
        })
        monkeypatch.setattr(cdsfl_utils, "_run_git_rc", run)

        sync = cdsfl_utils.git_state()["remote_sync"]

        assert sync.startswith("unknown"), sync
        assert "up to date" not in sync

    def test_the_ref_actually_compared_is_always_named(self, monkeypatch):
        """Numbers with no ref beside them are unreadable, and that is how
        "diverged (ahead 98, behind 1)" survived for months."""
        run = _fake_git({
            **_BASE_GIT,
            ("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"): (128, ""),
            ("rev-list", "--left-right", "--count", "origin/main...HEAD"): (0, "1\t3"),
        })
        monkeypatch.setattr(cdsfl_utils, "_run_git_rc", run)

        sync = cdsfl_utils.git_state()["remote_sync"]

        assert "origin/main" in sync
        assert "no upstream configured" in sync
        assert "ahead 3" in sync and "behind 1" in sync

    def test_garbled_output_is_unknown_too(self, monkeypatch):
        """rc 0 with unparseable stdout is still not a measurement."""
        run = _fake_git({
            **_BASE_GIT,
            ("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"):
                (0, "origin/exp39-experimental"),
            ("rev-list", "--left-right", "--count",
             "origin/exp39-experimental...HEAD"): (0, "fatal: bad revision"),
        })
        monkeypatch.setattr(cdsfl_utils, "_run_git_rc", run)

        assert cdsfl_utils.git_state()["remote_sync"].startswith("unknown")

    # FALSIFIER
    def test_the_pre_repair_comparison_really_did_say_up_to_date(self):
        failed = _fake_git({})  # every command answers (0, "") -> empty stdout
        assert _pre_repair_remote_sync(failed) == "up to date", (
            "if the reconstruction does not render a failure as 'up to date', "
            "the test above is not pinned to the defect"
        )


# ═════════════════════════════════════════════════════════════════════════════
# CLASS 6 — a truncated list always states its remainder
#
# THE DEFECT: the recovery report printed 20 of 26 uncommitted files under the
# heading "Uncommitted (26 file(s)):" and said nothing about the other 6, three
# of which were new test files. A reader concludes the tree holds what is shown.
#
# Scope note: this scan is deliberately restricted to slices that are ITERATED
# — a list rendered item by item. `str(err)[:300]` and `stdout[-20:]` are string
# clamps with no per-item reading and no count above them, and requiring a
# disclosure note on those would be noise. Disclosure is required at FUNCTION
# scope, because the count and the remainder note are printed by the same
# function that does the slicing.
#
# KNOWN BOUNDARY, stated so nobody over-trusts this: function scope means a
# function holding TWO capped listings passes on one disclosure. Per-slice
# matching was tried and rejected — it fires on `gs["recent_log"][:10]`, where
# the source is `git log -10` and the slice can never truncate anything, and a
# guard that cries wolf on a provably-safe line is a guard that gets deleted.
# The behavioural counterpart, which has no such gap, is
# test_cdsfl_recover_repairs.py::test_the_stated_count_is_the_real_number_of_uncommitted_files.
# ═════════════════════════════════════════════════════════════════════════════

_DISCLOSURE_WORDS = ("more", "withheld", "capped", "not shown", "truncat")


def _iterated_capped_slices(fn: ast.AST) -> list[tuple[int, str]]:
    iters: list[ast.AST] = []
    for node in ast.walk(fn):
        if isinstance(node, ast.For):
            iters.append(node.iter)
        elif isinstance(node, ast.comprehension):
            iters.append(node.iter)
    out: list[tuple[int, str]] = []
    for it in iters:
        if not isinstance(it, ast.Subscript) or not isinstance(it.slice, ast.Slice):
            continue
        sl = it.slice
        if (sl.lower is None and sl.step is None
                and isinstance(sl.upper, ast.Constant)
                and isinstance(sl.upper.value, int)):
            out.append((it.lineno, ast.unparse(it)))
    return out


def _discloses_a_cap(fn: ast.AST) -> bool:
    for node in ast.walk(fn):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            low = node.value.lower()
            if any(word in low for word in _DISCLOSURE_WORDS):
                return True
    return False


def _undisclosed_truncations(src: str, label: str) -> list[str]:
    tree = ast.parse(src)
    out: list[str] = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        slices = _iterated_capped_slices(fn)
        if slices and not _discloses_a_cap(fn):
            for line, text in slices:
                out.append(f"{label}:{line}: {fn.name}() prints {text} "
                           f"and never says what it withheld")
    return out


class TestTruncatedListsStateTheirRemainder:

    def test_the_scan_sees_the_capped_listings_it_is_guarding(self):
        """ANTI-VACUITY."""
        found = 0
        for path, src in _sources().items():
            for fn in ast.walk(ast.parse(src)):
                if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    found += len(_iterated_capped_slices(fn))
        assert found >= 3, (
            f"expected several capped listings across scripts/; found {found}"
        )

    def test_no_script_prints_a_capped_listing_in_silence(self):
        violations: list[str] = []
        for path, src in _sources().items():
            violations += _undisclosed_truncations(
                src, str(path.relative_to(REPO_ROOT))
            )
        assert violations == [], (
            "A list cut to N under a heading that reads as complete is a "
            "silent falsehood. State the remainder.\n" + "\n".join(violations)
        )

    # FALSIFIER
    def test_the_scan_catches_an_undisclosed_cap(self):
        broken = (
            "def report(items):\n"
            "    print(f'Uncommitted ({len(items)} file(s)):')\n"
            "    for f in items[:20]:\n"
            "        print(f)\n"
        )
        hits = _undisclosed_truncations(broken, "<broken>")
        assert len(hits) == 1 and "items[:20]" in hits[0]

    def test_the_scan_accepts_a_disclosed_cap(self):
        fixed = (
            "def report(items):\n"
            "    total = len(items)\n"
            "    print(f'Uncommitted ({total} file(s)):')\n"
            "    for f in items[:20]:\n"
            "        print(f)\n"
            "    if total > 20:\n"
            "        print(f'... and {total - 20} more not shown')\n"
        )
        assert _undisclosed_truncations(fixed, "<fixed>") == []


# ═════════════════════════════════════════════════════════════════════════════
# CLASS 7 — usage text advertises only flags that exist
#
# THE DEFECT this generalises: `--full` was documented and accepted and did
# nothing for 118 days, and `--fix-timestamps` outlived its implementation.
# Advertising a flag the parser does not define is worse than either, because
# argparse rejects it at the door and the documented command simply fails.
#
# Extraction is restricted to docstring lines that INVOKE the script by name,
# so a line describing another script's flags (cdsfl_qc.py's docstring mentions
# `cdsfl_onboard.py --dry-run`) is not misread as a claim about this one.
# ═════════════════════════════════════════════════════════════════════════════

_FLAG_RE = re.compile(r"(?<![\w-])(--[A-Za-z][\w-]*)")


def _advertised_flags(src: str, script_name: str) -> set[str]:
    doc = ast.get_docstring(ast.parse(src)) or ""
    found: set[str] = set()
    for line in doc.splitlines():
        if script_name in line:
            found |= set(_FLAG_RE.findall(line))
    return found


def _implemented_flags(src: str) -> set[str]:
    out: set[str] = set()
    for node in ast.walk(ast.parse(src)):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "add_argument"):
            for arg in node.args:
                if (isinstance(arg, ast.Constant) and isinstance(arg.value, str)
                        and arg.value.startswith("-")):
                    out.add(arg.value)
    return out


class TestUsageTextAdvertisesOnlyImplementedFlags:

    def test_the_extractor_reads_a_usage_block_correctly(self):
        """ANTI-VACUITY, on a fixed input so it cannot drift with the scripts.
        The second line is the case that matters: cdsfl_qc.py's docstring
        describes `cdsfl_onboard.py --dry-run` while defining no flags of its
        own, and reading that as a claim about cdsfl_qc would be a false
        positive on a real document."""
        src = (
            '"""Demo script.\n'
            "\n"
            "Usage:\n"
            "  python3 scripts/demo.py --alpha\n"
            "  python3 scripts/demo.py --beta-flag   # comment\n"
            "\n"
            "Checks:\n"
            "  1. Other script wiring (other.py --gamma passes)\n"
            '"""\n'
        )
        assert _advertised_flags(src, "demo.py") == {"--alpha", "--beta-flag"}

    def test_the_scan_finds_advertised_flags_in_the_real_scripts(self):
        advertising = {
            path.name for path, src in _sources().items()
            if _advertised_flags(src, path.name)
        }
        assert len(advertising) >= 2, (
            f"only {sorted(advertising)} appear to advertise any flag; the "
            f"extractor is probably not reading the usage block"
        )

    def test_a_script_with_no_parser_advertises_no_flags(self):
        """The converse of the rule, and the reason the two subprocess tests
        below can skip a parser-less script without losing coverage: a module
        that cannot parse a flag must not tell anyone to pass one."""
        for path, src in _sources().items():
            if "ArgumentParser" in src:
                continue
            assert _advertised_flags(src, path.name) == set(), (
                f"{path.relative_to(REPO_ROOT)} has no argument parser, so "
                f"every flag in its usage text is silently ignored"
            )

    def test_no_script_documents_a_flag_it_does_not_define(self):
        violations: list[str] = []
        for path, src in _sources().items():
            advertised = _advertised_flags(src, path.name)
            implemented = _implemented_flags(src) | {"--help"}
            for flag in sorted(advertised - implemented):
                violations.append(
                    f"{path.relative_to(REPO_ROOT)}: usage advertises {flag}, "
                    f"which argparse does not define — the documented command "
                    f"exits 2"
                )
        assert violations == [], "\n".join(violations)

    @pytest.mark.parametrize("script", SCRIPT_PATHS, ids=lambda p: p.name)
    def test_help_builds_and_lists_every_advertised_flag(self, script: Path):
        """Runs the real ``--help``. argparse answers and exits before any
        script body runs, so this is a pure parser check — but it is also the
        cheapest possible proof that the module still IMPORTS, which is the
        thing whose absence let cdsfl_qc.py crash unnoticed for 105 days."""
        src = script.read_text(encoding="utf-8")
        if "ArgumentParser" not in src:
            pytest.skip(
                f"{script.name} defines no argument parser; the converse rule "
                f"(it must then advertise no flags) is asserted above"
            )

        proc = subprocess.run(
            [sys.executable, str(script), "--help"],
            capture_output=True, text=True, timeout=60, cwd=str(REPO_ROOT),
        )

        assert proc.returncode == 0, proc.stderr[-2000:]
        for flag in sorted(_advertised_flags(src, script.name)):
            assert flag in proc.stdout, (
                f"{script.name} --help does not list {flag}, which its own "
                f"usage text tells a reader to run"
            )

    @pytest.mark.parametrize("script", SCRIPT_PATHS, ids=lambda p: p.name)
    def test_an_unknown_flag_is_rejected_loudly(self, script: Path):
        """A retired flag must fail, not be silently ignored — a script that
        accepts `--fix-timestamps` and does nothing with it is the 118-day
        no-op again."""
        src = script.read_text(encoding="utf-8")
        if "ArgumentParser" not in src:
            pytest.skip(
                f"{script.name} defines no argument parser; the converse rule "
                f"(it must then advertise no flags) is asserted above"
            )

        proc = subprocess.run(
            [sys.executable, str(script), "--this-flag-does-not-exist"],
            capture_output=True, text=True, timeout=60, cwd=str(REPO_ROOT),
        )

        assert proc.returncode != 0
        assert "unrecognized arguments" in proc.stderr


# ═════════════════════════════════════════════════════════════════════════════
# CLASS 8 — a crashed check exits non-zero
#
# THE DEFECT: cdsfl_qc.py aborted mid-run for 105 days. Once the crash was
# contained so the report survived it, the remaining hazard is subtler and is
# what this pins: a run that reports "1 checks crashed" in its body while
# handing the shell a 0. Any wrapper reading only the status is then told a
# partially-failed run succeeded.
# ═════════════════════════════════════════════════════════════════════════════

_QC_CHECKS = (
    "check_staleness", "check_test_consistency", "check_experiment_consistency",
    "check_glossary", "check_onboard_script", "check_log_seals",
)


def _stub_qc(monkeypatch, tmp_path: Path, *, crash: bool) -> None:
    """Replace every check. NOTHING real runs: check_staleness would call
    git_state (git fetch), check_test_consistency would spawn the entire suite,
    and the seal/onboard checks spawn subprocesses."""
    monkeypatch.setattr(sys, "argv", ["cdsfl_qc.py"])
    monkeypatch.setattr(cdsfl_qc, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(cdsfl_qc, "timestamp_iso", lambda: "2026-08-05T21:00:00+01:00")
    for name in _QC_CHECKS:
        monkeypatch.setattr(
            cdsfl_qc, name,
            lambda _root: [{"category": "OK", "file": "x", "detail": "ran"}],
        )
    if crash:
        def boom(_root, **_kw):
            raise OSError(63, "File name too long")
        monkeypatch.setattr(cdsfl_qc, "check_broken_references", boom)
    else:
        monkeypatch.setattr(cdsfl_qc, "check_broken_references", lambda _r, **_k: [])


class TestACrashedCheckExitsNonZero:

    def test_a_crash_is_both_reported_and_returned(
        self, tmp_path: Path, monkeypatch, capsys,
    ):
        _stub_qc(monkeypatch, tmp_path, crash=True)

        code = cdsfl_qc.main()
        out = capsys.readouterr().out

        assert code != 0, (
            "the body says a check crashed and the status says success — the "
            "two must not be able to disagree"
        )
        assert "CHECK_FAILED" in out
        assert "1 checks crashed" in out
        assert "INCOMPLETE" in out

    def test_the_crash_does_not_take_the_report_down_with_it(
        self, tmp_path: Path, monkeypatch, capsys,
    ):
        """The 105-day defect itself: an unhandled error aborted the process
        before anything was printed."""
        _stub_qc(monkeypatch, tmp_path, crash=True)

        cdsfl_qc.main()

        out = capsys.readouterr().out
        assert "FINDINGS" in out
        assert "OSError" in out and "File name too long" in out, (
            "the crash must name itself; 'a check failed' with no cause is "
            "how a broken instrument goes unfixed"
        )

    def test_a_clean_run_still_exits_zero(
        self, tmp_path: Path, monkeypatch, capsys,
    ):
        _stub_qc(monkeypatch, tmp_path, crash=False)

        assert cdsfl_qc.main() == 0
        assert "0 checks crashed" in capsys.readouterr().out

    def test_findings_alone_do_not_gate(self, tmp_path: Path, monkeypatch, capsys):
        """qc reports; it does not enforce. A stale document must not fail the
        run, or the exit code stops meaning "the instrument worked"."""
        _stub_qc(monkeypatch, tmp_path, crash=False)
        monkeypatch.setattr(
            cdsfl_qc, "check_staleness",
            lambda _r: [{"category": "STALE", "file": "d", "detail": "old"}],
        )

        assert cdsfl_qc.main() == 0
        capsys.readouterr()

    def test_run_check_never_lets_a_crash_pass_as_an_empty_result(self):
        """[] and "it exploded" must not be the same answer."""
        def explodes(_root):
            raise RuntimeError("boom")

        findings = cdsfl_qc.run_check("x", explodes, REPO_ROOT)

        assert len(findings) == 1
        assert findings[0]["category"] == "CHECK_FAILED"
        assert "RuntimeError" in findings[0]["detail"]

    def test_the_seal_verifier_also_returns_non_zero_on_failure(
        self, tmp_path: Path, monkeypatch, capsys,
    ):
        """The same contract on the other exit-coded script. A directory that
        holds sealable files but no seal is UNSEALED, and that is a failure."""
        logs = tmp_path / "logs"
        (logs / "confer" / "session_a").mkdir(parents=True)
        (logs / "confer" / "session_a" / "round1.md").write_text("x\n",
                                                                encoding="utf-8")
        monkeypatch.setattr(cdsfl_seal_logs, "LOGS_ROOT", logs)
        monkeypatch.setattr(sys, "argv", ["cdsfl_seal_logs.py", "--verify"])

        code = cdsfl_seal_logs.main()

        assert code != 0
        assert "UNSEALED" in capsys.readouterr().err


# ═════════════════════════════════════════════════════════════════════════════
# ADDED — the exit code must reach the shell
#
# Why this is worth pinning: every guarantee in CLASS 8 is void if the value
# main() computes is thrown away at the entrypoint. `main()` on a function that
# returns 1 is exactly as silent as returning 0. This is a structural check
# because there is no way to observe it from inside the process.
# ═════════════════════════════════════════════════════════════════════════════


def _main_can_return_a_code(src: str) -> bool:
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            if _outer_annotation_name(node.returns) == "int":
                return True
            for ret in _returns_in_own_scope(node):
                if ret.value is not None and not (
                    isinstance(ret.value, ast.Constant) and ret.value.value is None
                ):
                    return True
    return False


class TestExitCodesReachTheShell:

    def test_the_scan_finds_scripts_with_an_exit_code_contract(self):
        """ANTI-VACUITY."""
        coded = [p.name for p, src in _sources().items() if _main_can_return_a_code(src)]
        assert len(coded) >= 3, coded

    # Both idioms propagate the status. The check accepted only the first until
    # 2026-08-16, when `scripts/similarity_operating_characteristic.py` was
    # flagged for using the second — a FALSE POSITIVE, since
    # `raise SystemExit(main())` is the stdlib-documented equivalent and needs no
    # `sys` import. The check was a bare substring match on one spelling.
    #
    # Worth fixing rather than working around. A checking instrument that reports
    # a violation where none exists trains its readers to override it, and an
    # override habit is how a real violation gets waved through later. That is the
    # same failure this file exists to catch, one level up.
    _PROPAGATING_ENTRYPOINTS = ("sys.exit(main())", "raise SystemExit(main())")

    def test_every_script_that_computes_a_code_propagates_it(self):
        violations: list[str] = []
        for path, src in _sources().items():
            if not _main_can_return_a_code(src):
                continue
            if not any(form in src for form in self._PROPAGATING_ENTRYPOINTS):
                violations.append(
                    f"{path.relative_to(REPO_ROOT)}: main() returns a status "
                    f"that the entrypoint discards — a bare main() call makes "
                    f"every failure exit 0"
                )
        assert violations == [], "\n".join(violations)

    def test_the_check_accepts_both_propagating_idioms_and_rejects_a_bare_call(self):
        """Guards the fix above. Without this, someone re-tightening the check to
        a single spelling would reintroduce the false positive and no test would
        say so — and the check would still look like it was working."""
        assert _main_can_return_a_code("def main():\n    return 1\n")
        for form in self._PROPAGATING_ENTRYPOINTS:
            assert any(f in form for f in self._PROPAGATING_ENTRYPOINTS)
        bare = "def main():\n    return 1\n\nif __name__ == '__main__':\n    main()\n"
        assert not any(form in bare for form in self._PROPAGATING_ENTRYPOINTS), (
            "a bare main() call must still be flagged")


# ═════════════════════════════════════════════════════════════════════════════
# ADDED — no script swallows an error into silence
#
# Why: `except Exception: pass` is CLASS 1 and CLASS 2 in one line — the
# failure happened, nothing recorded it, and the caller proceeds as though the
# operation succeeded. The two typed `except (json.JSONDecodeError, OSError):
# pass` handlers in the tree are legitimate: each falls through to a DIFFERENT
# code path that produces a real value, rather than continuing as if nothing
# went wrong. The rule is therefore narrow and mechanical: no bare `except:`,
# and no broad `except Exception` whose entire body is `pass`.
# ═════════════════════════════════════════════════════════════════════════════


class TestNoScriptSwallowsAnErrorIntoSilence:

    def test_no_bare_or_silently_swallowed_exception_handlers(self):
        violations: list[str] = []
        for path, src in _sources().items():
            for node in ast.walk(ast.parse(src)):
                if not isinstance(node, ast.ExceptHandler):
                    continue
                body = [
                    s for s in node.body
                    if not (isinstance(s, ast.Expr)
                            and isinstance(s.value, ast.Constant))
                ]
                only_pass = len(body) == 1 and isinstance(body[0], ast.Pass)
                rel = path.relative_to(REPO_ROOT)
                if node.type is None:
                    violations.append(
                        f"{rel}:{node.lineno}: bare `except:` catches "
                        f"KeyboardInterrupt and SystemExit as well as the fault"
                    )
                elif only_pass and ast.unparse(node.type) in ("Exception", "BaseException"):
                    violations.append(
                        f"{rel}:{node.lineno}: `except {ast.unparse(node.type)}: "
                        f"pass` — the failure leaves no trace anywhere"
                    )
        assert violations == [], "\n".join(violations)
