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
import json
import os
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
    # THE BACKUP VAULT IS REDIRECTED INTO tmp_path. Without this the tests write
    # credential-shaped files into the founder's real ~/.config, which the first
    # version of the out-of-repo fix did on its very first run.
    vault = tmp_path / "vault"
    monkeypatch.setenv("CDSFL_ENV_BACKUP_DIR", str(vault))
    return m, env, vault


class TestOnlyTheTokenLineMoves:
    def test_every_other_line_is_byte_identical(self, mod, monkeypatch, capsys):
        m, env, vault = mod
        monkeypatch.setattr(m.getpass, "getpass", lambda *a, **k: NEW)
        before = env.read_text().splitlines()
        assert m.main(["--rotate"]) == 0
        after = env.read_text().splitlines()
        assert len(before) == len(after)
        differing = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
        assert len(differing) == 1, f"{len(differing)} lines changed, expected 1"
        assert "ZENODO_TOKEN" in after[differing[0]]

    def test_it_keeps_the_lines_own_shape(self, mod, monkeypatch):
        m, env, vault = mod
        monkeypatch.setattr(m.getpass, "getpass", lambda *a, **k: NEW)
        m.main(["--rotate"])
        line = [ln for ln in env.read_text().splitlines() if "ZENODO_TOKEN" in ln][0]
        assert line.startswith("  export ZENODO_TOKEN="), line
        assert line.endswith(NEW)

    def test_the_other_keys_survive_by_name_and_count(self, mod, monkeypatch):
        m, env, vault = mod
        monkeypatch.setattr(m.getpass, "getpass", lambda *a, **k: NEW)
        before = m.key_names(env.read_text())
        m.main(["--rotate"])
        assert m.key_names(env.read_text()) == before == [
            "DEEPSEEK_API_KEY", "GITHUB_TOKEN", "OPENAI_API_KEY", "ZENODO_TOKEN"]

    def test_a_backup_exists_before_anything_is_written(self, mod, monkeypatch):
        m, env, vault = mod
        monkeypatch.setattr(m.getpass, "getpass", lambda *a, **k: NEW)
        m.main(["--rotate"])
        backups = list(vault.glob("env.backup-*"))
        assert len(backups) == 1
        assert backups[0].read_text() == FAKE_ENV, "the backup is not the ORIGINAL"


class TestItNeverEchoesTheToken:
    def test_not_the_old_value_nor_the_new_one(self, mod, monkeypatch, capsys):
        m, env, vault = mod
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
        m, env, vault = mod
        before = env.read_text()
        assert m.main([]) == 0
        assert env.read_text() == before
        assert "Nothing was changed" in capsys.readouterr().out


class TestItCanRefuse:
    @pytest.mark.parametrize("bad", ["", "short", "has spaces in it", "tok-with-dashes!!"])
    def test_it_refuses_a_bad_token_and_writes_nothing(self, mod, monkeypatch, bad):
        m, env, vault = mod
        monkeypatch.setattr(m.getpass, "getpass", lambda *a, **k: bad)
        before = env.read_text()
        assert m.main(["--rotate"]) == 3
        assert env.read_text() == before, "a refused token still changed the file"
        # A backup taken before the prompt is EXPECTED and harmless: it is a copy
        # of the unchanged file. Requiring its absence was an artefact of the
        # ordering that destroyed a one-time token on 2026-09-19, so the property
        # held here is the one that matters -- .env did not move.
        for b in vault.glob("env.backup-*"):
            assert b.read_text() == before

    def test_a_disturbed_neighbour_restores_the_backup(self, mod, monkeypatch, capsys):
        """If the write ever corrupted another line, the file must come BACK."""
        m, env, vault = mod
        monkeypatch.setattr(m.getpass, "getpass", lambda *a, **k: NEW)
        # a rotate() that also mangles an unrelated line, to prove the guard fires
        monkeypatch.setattr(m, "rotate", lambda new, text: text.replace(
            "GITHUB_TOKEN=ghp-fake-github-1111111111", "GITHUB_TOKEN=CLOBBERED"))
        assert m.main(["--rotate"]) == 4
        assert env.read_text() == FAKE_ENV, "the backup was not restored"
        assert "backup has been restored" in capsys.readouterr().out

    def test_a_missing_token_line_is_not_invented(self, mod, monkeypatch):
        m, env, vault = mod
        env.write_text("OPENAI_API_KEY=sk-fake\n", encoding="utf-8")
        monkeypatch.setattr(m.getpass, "getpass", lambda *a, **k: NEW)
        with pytest.raises(SystemExit):
            m.main(["--rotate"])


class TestItIsOffline:
    def test_rotating_contacts_nothing(self, mod, monkeypatch):
        m, env, vault = mod
        monkeypatch.setattr(m.getpass, "getpass", lambda *a, **k: NEW)
        import socket
        def boom(*a, **k):
            raise AssertionError("the rotation tool opened a socket")
        monkeypatch.setattr(socket, "create_connection", boom)
        monkeypatch.setattr(socket, "getaddrinfo", boom)
        assert m.main(["--rotate"]) == 0


class TestTheImmutableFlag:
    """THE DEFECT THAT BROKE THE FIRST LIVE ATTEMPT, 2026-09-19 19:51 BST.

    `.env` carries the macOS `uchg` flag. `shutil.copy2` copies that flag to the
    backup, and `os.chmod` on an immutable file raises EPERM, so the tool died
    AFTER the founder had pasted a token Zenodo shows exactly once. Both halves
    are fixed and both are held here: the flag is handled, and nothing that can
    fail is allowed to run after the prompt.
    """

    @pytest.fixture
    def locked(self, mod):
        import stat as st
        m, env, vault = mod
        os.chflags(env, st.UF_IMMUTABLE)
        yield m, env, vault
        os.chflags(env, 0)
        for b in vault.glob("env.backup-*"):
            os.chflags(b, 0)

    def test_it_rotates_a_locked_file_and_re_locks_it(self, locked, monkeypatch):
        import stat as st
        m, env, vault = locked
        monkeypatch.setattr(m.getpass, "getpass", lambda *a, **k: NEW)
        assert m.main(["--rotate"]) == 0
        assert env.read_text().count(NEW) == 1
        assert env.stat().st_flags & st.UF_IMMUTABLE, "the lock was not put back on"

    def test_the_backup_is_not_left_immutable(self, locked, monkeypatch):
        import stat as st
        m, env, vault = locked
        monkeypatch.setattr(m.getpass, "getpass", lambda *a, **k: NEW)
        m.main(["--rotate"])
        backup = list(vault.glob("env.backup-*"))[0]
        assert not backup.stat().st_flags & st.UF_IMMUTABLE, "copy2 inherited uchg"
        assert backup.stat().st_mode & 0o777 == 0o600

    def test_a_failed_preparation_never_asks_for_the_token(self, mod, monkeypatch):
        """The token-burning bug, stated as a property: if preparation fails,
        getpass is NOT called, so a one-time secret cannot be destroyed."""
        m, env, vault = mod
        asked = []
        monkeypatch.setattr(m.getpass, "getpass",
                            lambda *a, **k: asked.append(1) or NEW)
        monkeypatch.setattr(m, "preflight",
                            lambda e: (_ for _ in ()).throw(PermissionError("nope")))
        assert m.main(["--rotate"]) == 5
        assert asked == [], "it asked for the token before proving it could write"
        assert env.read_text() == FAKE_ENV


class TestTheCheckerDoesNotLieAboutWhyItFailed:
    """THE FALSE NEGATIVE OF 2026-09-19 19:57 BST.

    The live check reported "could not reach zenodo.org: JSONDecodeError" on a
    run where Zenodo answered HTTP 200 and the freshly rotated token was valid.
    Cause: `r.read(2000)` truncated a 3,718-byte response, so a complete JSON
    array arrived cut in half. The instrument truncated its own evidence and
    reported the truncation as an outage.

    3 outcomes must stay distinguishable, because they call for 3 different
    actions: rejected (make a new token), unreachable (wait), unparseable (the
    token is fine, the reader is not).
    """

    @pytest.fixture
    def checker(self, tmp_path, monkeypatch):
        spec = importlib.util.spec_from_file_location(
            "zcheck", ROOT / "scripts" / "zenodo_token_check.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        env = tmp_path / ".env"
        env.write_text("ZENODO_TOKEN=" + "a" * 60 + "\n", encoding="utf-8")
        monkeypatch.setattr(m, "ENV", env)
        # `main()` parses sys.argv itself, so the flag is supplied that way.
        monkeypatch.setattr(sys, "argv", ["zenodo_token_check.py", "--live"])
        return m

    def _serve(self, monkeypatch, body: bytes, status: int = 200):
        import urllib.request

        class _R:
            def __init__(self): self.status = status
            def read(self, n=None): return body[:n] if n else body
            def __enter__(self): return self
            def __exit__(self, *a): return False

        monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **k: _R())

    def test_a_response_over_2000_bytes_is_not_called_an_outage(self, checker,
                                                                monkeypatch, capsys):
        """The exact regression: a big, VALID payload."""
        big = json.dumps([{"id": i, "metadata": {"title": "x" * 80}}
                          for i in range(40)]).encode()
        assert len(big) > 2000
        self._serve(monkeypatch, big)
        rc = checker.main()
        out = capsys.readouterr().out
        assert "could not reach" not in out, "a 200 with valid JSON was called an outage"
        assert "the token WORKS" in out and "40 deposition" in out
        assert rc == 0

    def test_an_unparseable_200_is_not_reported_as_unreachable(self, checker,
                                                               monkeypatch, capsys):
        self._serve(monkeypatch, b"<html>bot check</html>")
        rc = checker.main()
        out = capsys.readouterr().out
        assert "could not reach" not in out
        assert "ACCEPTED" in out and "did not" in out
        assert rc == 4

    def test_a_401_is_still_reported_as_rejected(self, checker, monkeypatch, capsys):
        import urllib.error, urllib.request
        def boom(*a, **k):
            raise urllib.error.HTTPError("u", 401, "Unauthorized", {}, None)
        monkeypatch.setattr(urllib.request, "urlopen", boom)
        assert checker.main() == 1
        assert "REJECTED" in capsys.readouterr().out

    def test_a_real_transport_failure_is_still_an_outage(self, checker, monkeypatch,
                                                         capsys):
        import urllib.error, urllib.request
        def boom(*a, **k):
            raise urllib.error.URLError("connection refused")
        monkeypatch.setattr(urllib.request, "urlopen", boom)
        assert checker.main() == 3
        assert "could not reach" in capsys.readouterr().out
