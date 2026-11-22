#!/usr/bin/env python3
"""The note pre-flight must judge the population the GATE judges, from the INDEX.

WHY THIS EXISTS. `scripts/note_ratchet_preflight_2026-11-01.py` has one job:
say, in seconds, whether the commit gate's note ratchet will refuse. Measured
2026-11-22, it disagreed with that gate in BOTH directions at once.

FALSE POSITIVE. `changed_notes()` selects any changed path ending `.md` or
`.txt` anywhere in the repository. The gate selects staged paths under
`experimental_notes/`, suffix `.md`, excluding `seat_evidence/`. So the
pre-flight exited 1 on `resources/RECOVERY.md` going 81 -> 83, a file the gate
never lints. The hook's own comment names that exact hazard: a guard that fires
on the ordinary case teaches people to reach for `--no-verify` by reflex.

FALSE NEGATIVE, which is the expensive half, and it had 2 independent causes.
The pre-flight scored the WORKING TREE while the gate scores the INDEX, and it
printed a NEW file's count without ever refusing on it while the gate holds a
new note to a baseline of 0. Both fired on 2026-11-22: the batch-1 full record
scored 0 in the tree and 3 in the index, and `BRIEF.md.txt` printed 33 findings
beside an exit code of 0.

A THIRD CAUSE WAS INTRODUCED BY THE REPAIR ITSELF AND IS PINNED BELOW.
`git show :path` reads the staged blob, so the revision prefix for the index is
the EMPTY string -- passing ":" builds `git show ::path`, which fails, and a
fail-closed reader then calls every staged note unreadable. The first run of
the repair did exactly that.

WHAT IS PINNED, AND IT IS PINNED BY EXECUTION. A test that reads the hook's
source and the script's source asserts only that 2 files describe themselves
consistently. These tests RUN the hook's own shell pipeline and RUN
`gate_population()` against the same constructed repository and compare the
outputs, so a producer and a consumer that drift apart go red.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
TOOL = REPO / "scripts" / "note_ratchet_preflight_2026-11-01.py"
HOOK = REPO / "hooks" / "pre-commit"


@pytest.fixture(scope="module")
def mod():
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location("preflight_pop", TOOL)
    m = importlib.util.module_from_spec(spec)
    sys.modules["preflight_pop"] = m
    spec.loader.exec_module(m)
    return m


def _hook_patterns() -> tuple[str, str]:
    """Lift the gate's OWN grep patterns out of `hooks/pre-commit`.

    Taken from the hook at test time rather than copied here, so that changing
    the hook changes what this test compares against instead of silently
    leaving a stale duplicate behind.
    """
    src = HOOK.read_text()
    m = re.search(
        r"STAGED_NOTES=\$\(git diff --cached --name-only --diff-filter=ACM\s*\\\s*"
        r"\|\s*grep -E '([^']+)'\s*\\\s*"
        r"\|\s*grep -v '([^']+)'",
        src,
    )
    assert m, "the hook's STAGED_NOTES selector could not be located"
    return m.group(1), m.group(2)


STAMP = "Written under CDSFL note standard v1.9 (1 November 2026).\n"


def _note(body: str) -> str:
    """A note body that is CLEAN under the linter's PATH-SENSITIVE rules.

    A file whose logical path sits under `experimental_notes/` must name the
    standard that produced it, so a bare probe scores 1 finding before it has
    said anything. Without this, every fixture here would be dirty for a
    reason none of these tests is about -- which is how the first run of this
    file failed 2 of 9 on its own scaffolding rather than on the subject.
    """
    return body.rstrip("\n") + "\n\n" + STAMP


def _git(repo: pathlib.Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=repo, capture_output=True,
                       text=True, check=True)
    return r.stdout


def _build_repo(tmp_path: pathlib.Path) -> pathlib.Path:
    """A repository holding every case the 2 selectors could disagree on."""
    repo = tmp_path / "r"
    (repo / "experimental_notes" / "seat_evidence").mkdir(parents=True)
    (repo / "experimental_notes" / "evidence" / "deep").mkdir(parents=True)
    (repo / "resources").mkdir()
    (repo / "docs").mkdir()
    _git(repo.parent, "init", "-q", str(repo))
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")

    seed = {
        "experimental_notes/a.md": _note("alpha"),
        "experimental_notes/seat_evidence/s.md": _note("seat"),
        "experimental_notes/evidence/deep/d.md": _note("deep"),
        "experimental_notes/b.txt": _note("companion"),
        "experimental_notes/c.md.txt": _note("suffix trap"),
        "resources/RECOVERY.md": "recovery\n",
        "docs/x.md": "doc\n",
        "root.md": "root\n",
        "code.py": "x = 1\n",
    }
    for rel, body in seed.items():
        (repo / rel).write_text(body)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "seed")

    # Now make a mixed working state: some staged, some only in the tree,
    # some untracked. The 2 selectors must still agree on what is STAGED.
    for rel in ("experimental_notes/a.md", "experimental_notes/b.txt",
                "experimental_notes/seat_evidence/s.md",
                "experimental_notes/evidence/deep/d.md",
                "resources/RECOVERY.md", "docs/x.md", "root.md"):
        body = (repo / rel).read_text().replace(STAMP, "").rstrip("\n")
        stamped = rel.startswith("experimental_notes/")
        (repo / rel).write_text(
            _note(body + "\nchanged") if stamped else body + "\nchanged\n")
    _git(repo, "add", "experimental_notes/a.md", "experimental_notes/b.txt",
         "experimental_notes/seat_evidence/s.md",
         "experimental_notes/evidence/deep/d.md",
         "resources/RECOVERY.md", "docs/x.md")
    # root.md changed in the tree ONLY -- never staged.
    (repo / "experimental_notes" / "new_note.md").write_text(_note("brand new"))
    _git(repo, "add", "experimental_notes/new_note.md")
    (repo / "experimental_notes" / "untracked.md").write_text(_note("untracked"))
    return repo


class TestTheTwoSelectorsAgree:
    def test_gate_population_equals_the_hooks_own_pipeline(self, mod, tmp_path,
                                                           monkeypatch):
        repo = _build_repo(tmp_path)
        inc, exc = _hook_patterns()
        shell = (
            "git diff --cached --name-only --diff-filter=ACM "
            f"| grep -E '{inc}' "
            f"| grep -v '{exc}' || true"
        )
        hook_says = sorted(
            x for x in subprocess.run(shell, shell=True, cwd=repo,
                                      capture_output=True, text=True
                                      ).stdout.splitlines() if x.strip()
        )
        monkeypatch.setattr(mod, "REPO", repo)
        tool_says = mod.gate_population()
        assert tool_says == hook_says, (
            f"the pre-flight and the gate disagree on what is judged:\n"
            f"  hook: {hook_says}\n  tool: {tool_says}")
        # The comparison is only worth anything if it is non-empty and if the
        # traps are genuinely present to be got wrong.
        assert hook_says, "the constructed repository staged nothing to compare"

    def test_the_traps_are_actually_excluded(self, mod, tmp_path, monkeypatch):
        """ANTI-VACUITY: each excluded case must be absent for a REASON."""
        repo = _build_repo(tmp_path)
        monkeypatch.setattr(mod, "REPO", repo)
        got = mod.gate_population()
        assert "experimental_notes/a.md" in got
        assert "experimental_notes/evidence/deep/d.md" in got, "nested .md is in"
        assert "experimental_notes/new_note.md" in got, "a new staged note is in"
        assert "experimental_notes/seat_evidence/s.md" not in got, "seat evidence"
        assert "experimental_notes/b.txt" not in got, "a .txt companion"
        assert "experimental_notes/c.md.txt" not in got, "the .md.txt suffix trap"
        assert "resources/RECOVERY.md" not in got, "outside experimental_notes"
        assert "docs/x.md" not in got, "outside experimental_notes"
        assert "root.md" not in got, "tree-only, never staged"
        assert "experimental_notes/untracked.md" not in got, "untracked"


class TestItReadsTheIndexNotTheTree:
    def test_empty_rev_reads_the_staged_blob(self, mod, tmp_path, monkeypatch):
        """The double-colon defect: `:` as rev builds `git show ::path`."""
        repo = _build_repo(tmp_path)
        monkeypatch.setattr(mod, "REPO", repo)
        f = "experimental_notes/a.md"
        staged = subprocess.run(["git", "show", f":{f}"], cwd=repo,
                                capture_output=True, text=True)
        assert staged.returncode == 0 and "changed" in staged.stdout
        # The module must be able to score that blob at all.
        assert mod._score_rev("", f) is not None, (
            "the index could not be read; a ':' prefix builds `git show ::path`")
        assert mod._score_rev(":", f) is None, (
            "':' must NOT work -- if it does, this test no longer pins the bug")

    def test_a_tree_fix_that_is_not_staged_still_refuses(self, mod, tmp_path,
                                                         monkeypatch):
        """Today's live defect: tree clean, index dirty, gate refuses.

        THE WORDING IS LOAD-BEARING. Measured 2026-11-22, the linter does NOT
        flag "It took twenty-nine tries." while it does flag "The run produced
        twenty-nine findings." -- so the first wording would have made this
        test pass for the wrong reason, with an index that was never dirty.
        """
        repo = _build_repo(tmp_path)
        monkeypatch.setattr(mod, "REPO", repo)
        f = "experimental_notes/offender.md"
        (repo / f).write_text(_note("The run produced twenty-nine findings."))
        _git(repo, "add", f)
        # Fix the TREE only. A tree-based reader now sees nothing wrong.
        (repo / f).write_text(_note("The run produced 29 findings."))
        assert mod._findings(repo / f, logical=f) == 0, "tree reads clean"
        assert mod._score_rev("", f) > 0, "the index still carries the finding"
        _rows, worse, divergent, _unread = mod.gate_verdict()
        assert any(w[0] == f for w in worse), (
            "a note fixed only in the tree must still refuse")
        assert any(d[0] == f for d in divergent), (
            "the tree/index divergence must be reported by name")


class TestANewNoteIsHeldToTheStandard:
    def test_a_new_staged_note_with_a_finding_refuses(self, mod, tmp_path,
                                                      monkeypatch):
        repo = _build_repo(tmp_path)
        monkeypatch.setattr(mod, "REPO", repo)
        f = "experimental_notes/fresh.md"
        (repo / f).write_text(_note("There were twenty-nine of them."))
        _git(repo, "add", f)
        _rows, worse, _div, _unread = mod.gate_verdict()
        hit = [w for w in worse if w[0] == f]
        assert hit, "a NEW note carrying a finding must refuse"
        assert hit[0][1] == 0, "its baseline must be 0, not absent"
        assert hit[0][3] is True, "it must be reported AS new"

    def test_a_clean_new_staged_note_does_not_refuse(self, mod, tmp_path,
                                                     monkeypatch):
        repo = _build_repo(tmp_path)
        monkeypatch.setattr(mod, "REPO", repo)
        _rows, worse, _div, _unread = mod.gate_verdict()
        assert not any(w[0] == "experimental_notes/new_note.md" for w in worse)


class TestTheAdvisoryHalfNeverDecides:
    def test_a_filthy_txt_companion_does_not_refuse(self, mod, tmp_path,
                                                    monkeypatch):
        repo = _build_repo(tmp_path)
        monkeypatch.setattr(mod, "REPO", repo)
        f = "experimental_notes/loud.txt"
        (repo / f).write_text(_note("There were twenty-nine, then thirty-one more."))
        _git(repo, "add", f)
        assert mod._findings(repo / f, logical=f) > 0, "the probe must be dirty"
        _rows, worse, _div, _unread = mod.gate_verdict()
        assert not any(w[0] == f for w in worse), (
            "a .txt companion must never set the exit code")

    def test_a_worsened_resources_doc_does_not_refuse(self, mod, tmp_path,
                                                      monkeypatch):
        repo = _build_repo(tmp_path)
        monkeypatch.setattr(mod, "REPO", repo)
        f = "resources/RECOVERY.md"
        (repo / f).write_text(_note("Now there are twenty-nine findings."))
        _git(repo, "add", f)
        _rows, worse, _div, _unread = mod.gate_verdict()
        assert not any(w[0] == f for w in worse), (
            "the gate does not lint resources/; the pre-flight must not either")


class TestTheWideScanSurvives:
    def test_changed_notes_still_sees_what_the_gate_ignores(self, mod, tmp_path,
                                                            monkeypatch):
        """ADDITIVE: the wide scan is demoted, never removed."""
        repo = _build_repo(tmp_path)
        monkeypatch.setattr(mod, "REPO", repo)
        wide = mod.changed_notes()
        assert "experimental_notes/b.txt" in wide
        assert "resources/RECOVERY.md" in wide
        assert "root.md" in wide, "tree-only changes stay visible"
        gate = set(mod.gate_population())
        assert set(wide) - gate, "the advisory half must still have content"
