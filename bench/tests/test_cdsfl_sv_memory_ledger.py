"""Regression test for moving MEMORY_EXCLUSIONS recounting into ``sv``."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import cdsfl_sv as sv  # noqa: E402


def _stated(text: str, label: str) -> int:
    row = re.search(rf"\|[^|\n]*{re.escape(label)}[^|\n]*\|\s*\**(\d+)\**\s*\|", text)
    assert row, f"no accounting row for {label!r}"
    return int(row.group(1))


def test_sv_recounts_memory_exclusions_ledger(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "repo"
    ledger = root / "resources" / "MEMORY_EXCLUSIONS.md"
    ledger.parent.mkdir(parents=True)
    ledger.write_text(
        """# resources/MEMORY_EXCLUSIONS.md — What Was Withheld From the Public Mirror

## Accounting (counted 2026-08-08 07:40 BST)

The source index lives privately at
`~/.claude/projects/-Users-georgejackson-Developer-Projects/memory/MEMORY.md`.
Every figure below was counted from that directory on the date in this
heading, not carried forward from a previous version of this file.
The directory holds **3 files**, of which one is `MEMORY.md` itself
(the index), leaving **2 individual memory files**. They partition as:

| bucket | count |
|---|---|
| Mirrored (in summarised form) in `MEMORY.md` | 0 |
| Named as excluded, with a reason, below | 1 |
| Session handoffs, declared in `MEMORY.md` as retained privately and deliberately not mirrored | 0 |
| **Unclassified — neither mirrored nor previously declared** | **1** |
| total | 2 |

## Excluded Entries

- **`alpha_excluded.md`** — excluded for the test.

## Unclassified — awaiting review

- `beta_unclassified.md`

## Verification
""",
        encoding="utf-8",
    )

    mem_dir = tmp_path / "memory"
    mem_dir.mkdir()
    for name in (
        "MEMORY.md",
        "alpha_excluded.md",
        "beta_unclassified.md",
        "gamma_mirrored.md",
        "handoff_session.md",
    ):
        (mem_dir / name).write_text(f"{name}\n", encoding="utf-8")

    monkeypatch.setattr(sv, "_MEMORY_DIR", mem_dir)
    monkeypatch.setattr(sv, "repo_root", lambda: root)
    monkeypatch.setattr(
        sv,
        "git_state",
        lambda: {
            "branch": "main",
            "clean": True,
            "uncommitted": [],
            "last_hash": "deadbee",
            "last_message": "seed",
            "last_date": "2026-08-22",
            "recent_log": ["deadbee seed"],
            "remote_sync": "up to date",
        },
    )
    monkeypatch.setattr(sv, "test_count", lambda: 0)
    monkeypatch.setattr(sv, "latest_experiment", lambda: None)
    monkeypatch.setattr(sv, "generate_current_state", lambda *a, **k: "state\n")
    monkeypatch.setattr(sv, "update_timestamp", lambda *a, **k: False)
    monkeypatch.setattr(sv, "update_onboarding_experiment", lambda *a, **k: False)
    monkeypatch.setattr(sv, "update_recovery_pending", lambda *a, **k: False)
    monkeypatch.setattr(sys, "argv", ["cdsfl_sv.py"])

    sv.main()

    text = ledger.read_text(encoding="utf-8")
    assert "The directory holds **5 files**" in text
    assert "leaving **4 individual memory files**" in text
    assert _stated(text, "Mirrored") == 1
    assert _stated(text, "Named as excluded") == 1
    assert _stated(text, "Session handoffs") == 1
    assert _stated(text, "Unclassified") == 1
    assert _stated(text, "total") == 4
