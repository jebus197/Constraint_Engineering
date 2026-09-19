#!/usr/bin/env python3
"""The rotation tool changes 1 line and nothing else, and never echoes the token.

TASK Z1, the writing half. `scripts/zenodo_token_check.py` (2026-09-10) reports
the state; this covers the tool that CHANGES it.

WHY IT MATTERS THAT ONLY 1 LINE MOVES: `.env` holds 10 credentials across 10
assignments with 6 comment lines between them. The note delivered on 2026-09-10
asked the founder to hand-edit that file, which risks the other 9 to save
nothing. Every test here runs against a FAKE env file under tmp_path; the real
one is never opened.

THE NEGATIVE CONTROLS ARE THE POINT. A rotation tool that always reports success
measures nothing, so `test_it_refuses_a_short_token` and
`test_a_disturbed_neighbour_restores_the_backup` both require it to REFUSE.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "zenodo_rotate.py"

FAKE_ENV = """# credentials, do not commit
OPENAI_API_KEY=sk-fake-openai-0000000000
  export ZENODO_TOKEN=oldoldoldoldoldoldoldoldold123
GITHUB_TOKEN=ghp-fake-github-1111111111

# a trailing comment
DEEPSEEK_API_KEY=fake-deepseek-2222222222
"""
NEW = "brandnewtoken9999999999999999999999"


@pytest.fixture
def mod(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("zrot", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    env = tmp_path / ".env"
    env.write_text(FAKE_ENV, encoding="utf-8")
    monkeypatch.setattr(m, "ENV", env)
    return m, env


class TestOnlyTheTokenLineMoves:
    def test_every_other_line_is_byte_identical(self, mod, monkeypatch, capsys):
        m, env = mod
        monkeypatch.setattr(m.getpass, "getpass", lambda *a, **k: NEW)
        before = env.read_text().splitlines()
        assert m.main(["--rotate"]) == 0
        after = env.read_text().splitlines()
        assert len(before) == len(after)
        differing = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
        assert len(differing) == 1, f"{len(differing)} lines changed, expected 1"
        assert "ZENODO_TOKEN" in after[differing[0]]

    def test_it_keeps_the_lines_own_shape(self, mod, monkeypatch):
        m, env = mod
        monkeypatch.setattr(m.getpass, "getpass", lambda *a, **k: NEW)
        m.main(["--rotate"])
        line = [ln for ln in env.read_text().splitlines() if "ZENODO_TOKEN" in ln][0]
        assert line.startswith("  export ZENODO_TOKEN="), line
        assert line.endswith(NEW)

    def test_the_other_keys_survive_by_name_and_count(self, mod, monkeypatch):
        m, env = mod
        monkeypatch.setattr(m.getpass, "getpass", lambda *a, **k: NEW)
        before = m.key_names(env.read_text())
        m.main(["--rotate"])
        assert m.key_names(env.read_text()) == before == [
            "DEEPSEEK_API_KEY", "GITHUB_TOKEN", "OPENAI_API_KEY", "ZENODO_TOKEN"]

    def test_a_backup_exists_before_anything_is_written(self, mod, monkeypatch):
        m, env = mod
        monkeypatch.setattr(m.getpass, "getpass", lambda *a, **k: NEW)
        m.main(["--rotate"])
        backups = list(env.parent.glob(".env.backup-*"))
        assert len(backups) == 1
        assert backups[0].read_text() == FAKE_ENV, "the backup is not the ORIGINAL"


class TestItNeverEchoesTheToken:
    def test_not_the_old_value_nor_the_new_one(self, mod, monkeypatch, capsys):
        m, env = mod
        monkeypatch.setattr(m.getpass, "getpass", lambda *a, **k: NEW)
        m.main(["--rotate"])
        out = capsys.readouterr().out
        assert NEW not in out, "the tool printed the NEW token"
        assert "oldoldoldoldoldoldoldoldold123" not in out, "it printed the OLD token"
        # `shape()` is the only thing allowed to touch the value, and it must
        # surface at most the first 4 characters -- never the token itself.
        assert m.shape(NEW).count(NEW) == 0
        assert NEW[:4] in m.shape(NEW) and NEW[4:] not in m.shape(NEW)

    def test_read_only_mode_changes_nothing(self, mod, capsys):
        m, env = mod
        before = env.read_text()
        assert m.main([]) == 0
        assert env.read_text() == before
        assert "Nothing was changed" in capsys.readouterr().out


class TestItCanRefuse:
    @pytest.mark.parametrize("bad", ["", "short", "has spaces in it", "tok-with-dashes!!"])
    def test_it_refuses_a_bad_token_and_writes_nothing(self, mod, monkeypatch, bad):
        m, env = mod
        monkeypatch.setattr(m.getpass, "getpass", lambda *a, **k: bad)
        before = env.read_text()
        assert m.main(["--rotate"]) == 3
        assert env.read_text() == before
        assert list(env.parent.glob(".env.backup-*")) == [], "it backed up before refusing"

    def test_a_disturbed_neighbour_restores_the_backup(self, mod, monkeypatch, capsys):
        """If the write ever corrupted another line, the file must come BACK."""
        m, env = mod
        monkeypatch.setattr(m.getpass, "getpass", lambda *a, **k: NEW)
        # a rotate() that also mangles an unrelated line, to prove the guard fires
        monkeypatch.setattr(m, "rotate", lambda new, text: text.replace(
            "GITHUB_TOKEN=ghp-fake-github-1111111111", "GITHUB_TOKEN=CLOBBERED"))
        assert m.main(["--rotate"]) == 4
        assert env.read_text() == FAKE_ENV, "the backup was not restored"
        assert "backup has been restored" in capsys.readouterr().out

    def test_a_missing_token_line_is_not_invented(self, mod, monkeypatch):
        m, env = mod
        env.write_text("OPENAI_API_KEY=sk-fake\n", encoding="utf-8")
        monkeypatch.setattr(m.getpass, "getpass", lambda *a, **k: NEW)
        with pytest.raises(SystemExit):
            m.main(["--rotate"])


class TestItIsOffline:
    def test_rotating_contacts_nothing(self, mod, monkeypatch):
        m, env = mod
        monkeypatch.setattr(m.getpass, "getpass", lambda *a, **k: NEW)
        import socket
        def boom(*a, **k):
            raise AssertionError("the rotation tool opened a socket")
        monkeypatch.setattr(socket, "create_connection", boom)
        monkeypatch.setattr(socket, "getaddrinfo", boom)
        assert m.main(["--rotate"]) == 0
