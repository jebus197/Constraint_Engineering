"""Task L2: the quote-exemption effect script must measure the mask and nothing else.

FOUND BY PANEL ROUND 16, 2026-09-17, and reproduced by execution at 989f32f.
Task L2 cites `scripts/quote_exemption_effect_2026-09-09.py` for "8 false positives
removed, 0 added". Re-run at 989f32f, that script printed 29 removed, 19 ADDED and
exited 1, which reads as a regression in the linter. It was not one. The script
keys findings on (paragraph number, kind, token); its before-side generator split
paragraphs on a literal blank line, while `note_vagueness_lint.sentences()` has
used `paragraphs()`, which also breaks on a blank line carrying whitespace, since
6c6d053. The 2 sides numbered paragraphs differently after such a line, so an
unchanged finding counted as 1 removed plus 1 added. All 19 sat in 1 note.

The repair makes the before side use the linter's own `paragraphs()`. These tests
run the script on a 2-note fixture: 1 note carries a whitespace blank line above
a vague sentence (the renumbering), the other a vague sentence inside a 2-sentence
quotation (the mask). The repaired script must report the quotation as removed
and nothing as added; the literal split, kept in
`scripts/quote_exemption_rekey_2026-09-17.py`, must still show the false
addition, or the fixture has stopped exercising the confound.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LINT = REPO / "scripts" / "note_vagueness_lint.py"
EFFECT = REPO / "scripts" / "quote_exemption_effect_2026-09-09.py"
REKEY = REPO / "scripts" / "quote_exemption_rekey_2026-09-17.py"

#: A blank line carrying 1 space, then a vague sentence OUTSIDE any quotation.
SHIFTED = ("First paragraph names scripts/x.py and 12 findings.\n \n"
           "Second paragraph names scripts/y.py and 3 figures.\n\n"
           "The system then changed its behaviour without any stated cause at all.\n")
#: A quotation spanning 2 sentences, whose 2nd carries an unnamed subject.
QUOTED = ('He wrote "It was checked twice. The system then changed its behaviour '
          'without warning." and the note records it.\n')


def _tree(tmp_path: Path) -> Path:
    (tmp_path / "scripts").mkdir()
    for src in (LINT, EFFECT, REKEY):
        shutil.copy(src, tmp_path / "scripts" / src.name)
    notes = tmp_path / "experimental_notes"
    notes.mkdir()
    (notes / "shifted.md").write_text(SHIFTED, encoding="utf-8")
    (notes / "quoted.md").write_text(QUOTED, encoding="utf-8")
    return tmp_path


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _run_main(module, monkeypatch) -> tuple[int, str]:
    monkeypatch.setattr(sys, "argv", ["quote_exemption_effect_2026-09-09.py"])
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = module.main()
    return rc, buf.getvalue()


def _field(out: str, label: str) -> int:
    m = re.search(rf"^{re.escape(label)}\s*.*?:\s*(\d+)\s*$", out, re.M)
    assert m, f"no {label!r} line in:\n{out}"
    return int(m.group(1))


def _changed(out: str) -> dict[str, tuple[int, int]]:
    return {m.group(1): (int(m.group(2)), int(m.group(3)))
            for m in re.finditer(r"^\s+(\S+\.md)\s+-(\d+)\s+\+(\d+)\s*$", out, re.M)}


def test_the_effect_script_differs_by_the_mask_alone(tmp_path, monkeypatch):
    tree = _tree(tmp_path)
    eff = _load(tree / "scripts" / EFFECT.name, "effect_fixture_repaired")
    rc, out = _run_main(eff, monkeypatch)
    assert _field(out, "ADDED") == 0, (
        f"the effect script reports an addition on a fixture whose only "
        f"difference outside the quotation is paragraph numbering:\n{out}")
    assert rc == 0, out
    assert _field(out, "removed") >= 1, (
        f"the quoted finding was not removed, so the fixture no longer exercises "
        f"the mask:\n{out}")
    changed = _changed(out)
    assert changed.get("quoted.md", (0, 0))[0] >= 1, changed
    assert "shifted.md" not in changed, (
        f"the renumbered note changed although nothing in it is quoted: {changed}")


def test_the_literal_split_still_shows_the_false_addition(tmp_path, monkeypatch):
    """THE CONTROL. With the before side split on a literal blank line, as
    committed until 2026-09-17, the same fixture must show the false addition in
    shifted.md. If it does not, the test above passes on a fixture that no
    longer contains the confound."""
    tree = _tree(tmp_path)
    eff = _load(tree / "scripts" / EFFECT.name, "effect_fixture_literal")
    rekey = _load(tree / "scripts" / REKEY.name, "rekey_fixture_literal")
    monkeypatch.setattr(eff, "old_sentences", rekey.literal_split_sentences)
    rc, out = _run_main(eff, monkeypatch)
    assert _field(out, "ADDED") >= 1, out
    assert rc == 1, out
    assert _changed(out).get("shifted.md", (0, 0))[1] >= 1, out


def test_the_rekey_script_separates_renumbering_from_regression(tmp_path):
    """The producer cited by the L2 correction, executed on the fixture."""
    tree = _tree(tmp_path)
    rekey = _load(tree / "scripts" / REKEY.name, "rekey_fixture_measure")
    assert rekey.REPO == tree
    n_notes, rows = rekey.measure(tree)
    assert n_notes == 2
    by = {r["label"].split(" [")[0]: r for r in rows}
    literal = by["(para, kind, token) set, literal split"]
    assert literal["added"] >= 1 and literal["added_in"] == {"shifted.md": literal["added"]}, rows
    for label in ("(para, kind, token) set, old side on paragraphs()",
                  "(kind, token) multiset, literal split",
                  "(kind, token) set, literal split"):
        assert by[label]["added"] == 0, (label, rows)
        assert by[label]["removed"] >= 1, (label, rows)


def test_the_rekey_script_runs_and_answers_help(tmp_path):
    tree = _tree(tmp_path)
    copy = tree / "scripts" / REKEY.name
    h = subprocess.run([sys.executable, str(copy), "--help"], cwd=tree,
                       capture_output=True, text=True, timeout=120)
    assert h.returncode == 0 and h.stdout.startswith("usage:"), h
    assert "notes scanned" not in h.stdout, "--help ran the measurement"
    r = subprocess.run([sys.executable, str(copy)], cwd=tree,
                       capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stderr
    assert "notes scanned: 2" in r.stdout, r.stdout
    assert re.search(r"literal split \[committed until 2026-09-17\]\s+before \d+, "
                     r"removed \d+, ADDED [1-9]", r.stdout), r.stdout
