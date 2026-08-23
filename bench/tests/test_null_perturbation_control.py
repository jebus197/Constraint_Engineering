from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "scripts" / "null_perturbation_control.py"


def _load_script():
    spec = importlib.util.spec_from_file_location("null_perturbation_control_under_test", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _items(n: int) -> list[dict[str, str]]:
    return [
        {
            "run": f"exp{i}",
            "cid": f"C{i}",
            "target": "target.py",
            "severity": "LOW",
            "status": "OPEN",
        }
        for i in range(n)
    ]


def _patch_fast_control(monkeypatch: pytest.MonkeyPatch, module, n: int) -> None:
    monkeypatch.setattr(module, "eligible", lambda: _items(n))
    monkeypatch.setattr(
        module,
        "run_one",
        lambda item: ("CONFIRMED", "CONFIRMED", "CONFIRMED", "unrelated"),
    )


def test_dry_run_computes_but_does_not_touch_the_committed_record(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _load_script()
    _patch_fast_control(monkeypatch, module, 12)

    committed_record = REPO_ROOT / "experimental_notes" / "data" / "null_perturbation_control.json"
    before = committed_record.read_bytes()

    monkeypatch.setattr(
        sys,
        "argv",
        ["null_perturbation_control.py", "--limit", "12", "--dry-run"],
    )
    assert module.main() == 0

    after = committed_record.read_bytes()
    assert after == before
    assert "dry-run: not writing" in capsys.readouterr().out


def test_limited_run_refuses_to_replace_larger_existing_record_unless_forced(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _load_script()
    _patch_fast_control(monkeypatch, module, 12)

    out = tmp_path / "null_perturbation_control.json"
    original = {"rows": [{"old": i} for i in range(397)]}
    out.write_text(json.dumps(original, indent=2), encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        ["null_perturbation_control.py", "--limit", "12", "--out", str(out)],
    )
    assert module.main() == 2

    assert json.loads(out.read_text(encoding="utf-8")) == original
    err = capsys.readouterr().err
    assert "refusing to overwrite" in err
    assert "397 rows" in err
    assert "12 rows" in err

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "null_perturbation_control.py",
            "--limit",
            "12",
            "--out",
            str(out),
            "--force",
        ],
    )
    assert module.main() == 0
    replaced = json.loads(out.read_text(encoding="utf-8"))
    assert len(replaced["rows"]) == 12
