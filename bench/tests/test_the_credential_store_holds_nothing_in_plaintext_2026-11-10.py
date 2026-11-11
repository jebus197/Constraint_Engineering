#!/usr/bin/env python3
"""The credential store keeps nothing readable, and refuses what it must refuse.

★ WHAT THIS GUARDS. `bench/credential_store.py`, built 2026-11-10 on his
requirement that the advanced settings surface hold vendor API keys and vendor
logins *"encrypted (not stored as plain text, which would clearly be a bad
practice to begin with)"* and readable *"only ... by the user/researcher entering
the correct password"*. Entry B142, the settings surface; `fr:e8951f2ed269`, the
credential store.

WHY EVERY TEST HERE EXECUTES THE MODULE. A guard that asserted on the source
text of a cryptographic module would assert only that the module describes
itself consistently -- it could not tell an authenticated envelope from an
unauthenticated one, because both are described correctly in their own comments.
That is `execute-do-not-grep`, and this project has found 4 defects by running 2
forms against each other and 0 by reading. So each property below is
established by WRITING a store, ATTACKING it, and observing the refusal.

EVERY TEST USES A TEMPORARY PATH. None of them can read, write or even stat the
researcher's real store at `~/.cdsfl/credentials.enc`; `test_the_default_path_is_
outside_the_repository` is the only one that looks at the default, and it only
looks at the path, never the file.

THE 3 ADVERSARIAL CASES ARE THE POINT. A round-trip test passes against a store
that writes plaintext with a decorative header. What distinguishes real
encryption is that a WRONG passphrase fails, a FLIPPED ciphertext byte fails, and
a DOWNGRADED key-derivation function fails -- the last being the attack an
unauthenticated envelope would permit, where a thief holding the file swaps
Argon2id for a cheap hash and then attacks the passphrase at that lower cost.
"""
from __future__ import annotations

import base64
import importlib.util
import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "bench" / "credential_store.py"
BACKEND = ROOT / "bench" / "ux_backend_2026-10-20.py"

PASSPHRASE = "a-sufficiently-long-test-passphrase"
#: Marker strings chosen so a plaintext leak is unmistakable in a file dump.
SECRET_KEY = "sk-GUARD-PLAINTEXT-CANARY-0001"
SECRET_TOKEN = "rt-GUARD-PLAINTEXT-CANARY-0002"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def cs():
    assert MODULE.is_file(), f"{MODULE} is missing"
    return _load(MODULE, "_cs_guard")


@pytest.fixture()
def store(cs, tmp_path):
    """A fresh store holding 2 credentials, 1 of each accepted kind."""
    path = tmp_path / "credentials.enc"
    cs.init_store(PASSPHRASE, path)
    cs.add_credential("openrouter", cs.KIND_API_KEY, SECRET_KEY, PASSPHRASE,
                      vendor="OpenRouter", path=path)
    cs.add_credential("anthropic-cli", cs.KIND_REFRESH_TOKEN, SECRET_TOKEN,
                      PASSPHRASE, vendor="Anthropic", path=path)
    return path


class TestItRoundTrips:
    def test_a_stored_value_comes_back_exactly(self, cs, store):
        assert cs.get_credential("openrouter", PASSPHRASE, store) == SECRET_KEY
        assert cs.get_credential("anthropic-cli", PASSPHRASE, store) == SECRET_TOKEN

    def test_a_missing_name_is_a_clean_refusal(self, cs, store):
        with pytest.raises(cs.CredentialStoreError):
            cs.get_credential("never-stored", PASSPHRASE, store)

    def test_delete_removes_it_and_reports_whether_it_was_there(self, cs, store):
        assert cs.delete_credential("openrouter", PASSPHRASE, store) is True
        assert cs.delete_credential("openrouter", PASSPHRASE, store) is False
        with pytest.raises(cs.CredentialStoreError):
            cs.get_credential("openrouter", PASSPHRASE, store)

    def test_an_existing_name_is_not_overwritten_silently(self, cs, store):
        with pytest.raises(cs.CredentialStoreError):
            cs.add_credential("openrouter", cs.KIND_API_KEY, "different",
                              PASSPHRASE, path=store)
        assert cs.get_credential("openrouter", PASSPHRASE, store) == SECRET_KEY
        cs.add_credential("openrouter", cs.KIND_API_KEY, "different",
                          PASSPHRASE, path=store, replace=True)
        assert cs.get_credential("openrouter", PASSPHRASE, store) == "different"


class TestNothingIsReadableOnDisk:
    def test_no_secret_appears_anywhere_in_the_file(self, store):
        raw = store.read_bytes()
        assert SECRET_KEY.encode() not in raw
        assert SECRET_TOKEN.encode() not in raw
        #: And not base64-encoded either, which a lazy "encoding" would leave.
        assert base64.b64encode(SECRET_KEY.encode()) not in raw

    def test_no_secret_appears_in_the_backup_either(self, store):
        """The backup is a SECOND copy, so it is a second place to leak."""
        backup = store.with_suffix(store.suffix + ".bak")
        assert backup.is_file(), "no backup was kept, so a bad write has no fallback"
        raw = backup.read_bytes()
        assert SECRET_KEY.encode() not in raw
        assert SECRET_TOKEN.encode() not in raw

    def test_the_file_is_readable_by_its_owner_only(self, store):
        assert stat.S_IMODE(store.stat().st_mode) == 0o600
        assert stat.S_IMODE(store.parent.stat().st_mode) == 0o700

    def test_listing_returns_metadata_and_never_a_value(self, cs, store):
        rows = cs.list_credentials(PASSPHRASE, store)
        assert len(rows) == 2
        for row in rows:
            assert "value" not in row
            blob = json.dumps(row)
            assert SECRET_KEY not in blob and SECRET_TOKEN not in blob
            assert row["fingerprint"] and len(row["fingerprint"]) == 12

    def test_verify_proves_it_opens_without_revealing_contents(self, cs, store):
        out = cs.verify_store(PASSPHRASE, store)
        assert out["opens"] is True and out["entries"] == 2
        blob = json.dumps(out)
        assert SECRET_KEY not in blob and SECRET_TOKEN not in blob

    def test_the_fingerprint_does_not_reverse_and_does_discriminate(self, cs):
        a, b = cs.fingerprint(SECRET_KEY), cs.fingerprint(SECRET_TOKEN)
        assert a != b, "2 different secrets must not share a fingerprint"
        assert cs.fingerprint(SECRET_KEY) == a, "it must be stable"
        assert SECRET_KEY not in a and len(a) == 12


class TestTheAdversarialCases:
    """A round-trip passes against plaintext with a header. These do not."""

    def test_a_wrong_passphrase_does_not_open_it(self, cs, store):
        with pytest.raises(cs.WrongPassphrase):
            cs.get_credential("openrouter", PASSPHRASE + "x", store)

    def test_a_flipped_ciphertext_byte_is_detected(self, cs, store, tmp_path):
        blob = json.loads(store.read_text())
        raw = bytearray(base64.b64decode(blob["ciphertext"]))
        raw[7] ^= 0x01
        blob["ciphertext"] = base64.b64encode(bytes(raw)).decode("ascii")
        bad = tmp_path / "flipped.enc"
        bad.write_text(json.dumps(blob))
        with pytest.raises(cs.WrongPassphrase):
            cs.get_credential("openrouter", PASSPHRASE, bad)

    def test_a_downgraded_key_derivation_function_is_detected(self, cs, store, tmp_path):
        """THE ATTACK AN UNAUTHENTICATED ENVELOPE WOULD PERMIT.

        A thief holding the file rewrites the recorded KDF to something cheap
        and then attacks the passphrase at that reduced cost. Binding the
        envelope in as additional authenticated data is what stops it, so this
        test is the one that distinguishes a bound envelope from a loose one.
        """
        blob = json.loads(store.read_text())
        blob["envelope"]["kdf"] = {"name": "scrypt", "n": 1024, "r": 8, "p": 1}
        bad = tmp_path / "downgraded.enc"
        bad.write_text(json.dumps(blob))
        with pytest.raises(cs.WrongPassphrase):
            cs.get_credential("openrouter", PASSPHRASE, bad)

    def test_an_envelope_field_that_does_not_feed_the_key_is_still_detected(
            self, cs, store, tmp_path):
        """★ THIS IS THE TEST THAT ACTUALLY PINS THE AUTHENTICATED ENVELOPE,
        ADDED 2026-11-10 AFTER THE MUTATION HARNESS SHOWED THE OTHERS DID NOT.

        `test_a_downgraded_key_derivation_function_is_detected` and
        `test_a_swapped_salt_is_detected` both pass even with the envelope
        binding REMOVED FROM BOTH SIDES, because editing the KDF or the salt
        changes the DERIVED KEY, so the decryption fails for that reason alone.
        They are good tests of the key derivation and no test at all of the
        binding. The harness reported it as an ESCAPE and that is the finding.

        `cipher` is the field that isolates the property: it is recorded in the
        envelope, it is NOT an input to the key derivation, and nothing else
        reads it. So editing it can only be caught by the envelope being bound
        in as additional authenticated data. With the binding present this must
        fail; with it removed, this is the only test that moves.
        """
        blob = json.loads(store.read_text())
        assert blob["envelope"]["cipher"] == "AES-256-GCM", (
            "this test depends on `cipher` being a recorded envelope field that "
            "does not feed the key derivation; the envelope has changed shape")
        blob["envelope"]["cipher"] = "AES-128-GCM"
        bad = tmp_path / "relabelled.enc"
        bad.write_text(json.dumps(blob))
        with pytest.raises(cs.WrongPassphrase):
            cs.get_credential("openrouter", PASSPHRASE, bad)

    def test_a_swapped_salt_is_detected(self, cs, store, tmp_path):
        blob = json.loads(store.read_text())
        blob["envelope"]["salt"] = base64.b64encode(b"\x00" * 16).decode("ascii")
        bad = tmp_path / "resalted.enc"
        bad.write_text(json.dumps(blob))
        with pytest.raises(cs.WrongPassphrase):
            cs.get_credential("openrouter", PASSPHRASE, bad)

    def test_a_fresh_nonce_is_drawn_on_every_write(self, cs, store):
        """Reusing a nonce under one key is the single catastrophic mistake
        available with this cipher, so the nonce must never be carried over."""
        seen = {json.loads(store.read_text())["envelope"]["nonce"]}
        for i in range(4):
            cs.add_credential(f"extra-{i}", cs.KIND_API_KEY, f"v{i}",
                              PASSPHRASE, path=store)
            seen.add(json.loads(store.read_text())["envelope"]["nonce"])
        assert len(seen) == 5, f"a nonce repeated across writes: {len(seen)} of 5 distinct"

    def test_an_unknown_kdf_name_is_refused_rather_than_guessed(self, cs, store, tmp_path):
        blob = json.loads(store.read_text())
        blob["envelope"]["kdf"] = {"name": "rot13"}
        bad = tmp_path / "unknown.enc"
        bad.write_text(json.dumps(blob))
        with pytest.raises(cs.CredentialStoreError):
            cs.get_credential("openrouter", PASSPHRASE, bad)

    def test_a_future_version_is_refused_rather_than_misread(self, cs, store, tmp_path):
        """★ TIGHTENED 2026-11-10 AFTER IT PASSED FOR THE WRONG REASON.

        This asserted only that SOME `CredentialStoreError` was raised. Removing
        the version check entirely left it GREEN, because bumping the version
        also changes the authenticated envelope, so the AEAD rejected the file
        and raised `WrongPassphrase` -- itself a `CredentialStoreError`. The test
        was therefore measuring the cipher, not the version check, and the
        mutation harness caught it as an ESCAPE.

        It now pins the version check specifically: the refusal must name the
        version and must NOT be the authentication failure, which proves the
        check fires BEFORE any decryption is attempted. That ordering is the
        property worth having -- a reader should refuse a format it does not
        understand rather than try to decrypt it and report a confusing error.
        """
        blob = json.loads(store.read_text())
        blob["envelope"]["version"] = cs.STORE_VERSION + 1
        bad = tmp_path / "future.enc"
        bad.write_text(json.dumps(blob))
        with pytest.raises(cs.CredentialStoreError) as exc:
            cs.get_credential("openrouter", PASSPHRASE, bad)
        assert not isinstance(exc.value, cs.WrongPassphrase), (
            "the version was refused by the CIPHER, not by the version check, so "
            "this test would stay green with the version check deleted")
        assert str(cs.STORE_VERSION) in str(exc.value), (
            "the refusal must say which version it reads")


class TestTheRefusalThatIsPolicy:
    def test_a_vendor_account_password_is_refused(self, cs, store):
        with pytest.raises(cs.CredentialStoreError) as exc:
            cs.add_credential("vendor-login", "account_password",
                              "irrelevant", PASSPHRASE, path=store)
        message = str(exc.value)
        assert cs.KIND_REFRESH_TOKEN in message, (
            "the refusal must name the alternative, or it is an obstacle rather "
            "than an answer")
        assert "second factor" in message

    @pytest.mark.parametrize("spelling", ["password", "login", "vendor_password",
                                          "account_login", "login_password"])
    def test_every_spelling_of_it_is_refused(self, cs, store, spelling):
        """A researcher will not guess the exact token, so each near spelling
        must reach the SAME explanation rather than a generic unknown-kind."""
        with pytest.raises(cs.CredentialStoreError) as exc:
            cs.add_credential("x", spelling, "irrelevant", PASSPHRASE, path=store)
        assert cs.KIND_REFRESH_TOKEN in str(exc.value)

    def test_an_empty_value_is_refused(self, cs, store):
        with pytest.raises(cs.CredentialStoreError):
            cs.add_credential("empty", cs.KIND_API_KEY, "", PASSPHRASE, path=store)

    def test_a_short_passphrase_is_refused_at_creation(self, cs, tmp_path):
        with pytest.raises(cs.CredentialStoreError):
            cs.init_store("short", tmp_path / "s.enc")
        assert not (tmp_path / "s.enc").exists(), (
            "a refused creation must leave no file behind")

    def test_creating_over_an_existing_store_is_refused(self, cs, store):
        with pytest.raises(cs.CredentialStoreError):
            cs.init_store(PASSPHRASE, store)
        assert cs.get_credential("openrouter", PASSPHRASE, store) == SECRET_KEY


class TestRekeying:
    def test_the_new_passphrase_opens_it_and_the_old_does_not(self, cs, store):
        new = "a-different-long-test-passphrase"
        cs.change_passphrase(PASSPHRASE, new, store)
        assert cs.get_credential("openrouter", new, store) == SECRET_KEY
        with pytest.raises(cs.WrongPassphrase):
            cs.get_credential("openrouter", PASSPHRASE, store)

    def test_rekeying_draws_new_key_material(self, cs, store):
        before = json.loads(store.read_text())["envelope"]
        cs.change_passphrase(PASSPHRASE, "a-different-long-test-passphrase", store)
        after = json.loads(store.read_text())["envelope"]
        assert before["salt"] != after["salt"]
        assert before["nonce"] != after["nonce"]

    def test_a_short_new_passphrase_is_refused_and_changes_nothing(self, cs, store):
        with pytest.raises(cs.CredentialStoreError):
            cs.change_passphrase(PASSPHRASE, "short", store)
        assert cs.get_credential("openrouter", PASSPHRASE, store) == SECRET_KEY


class TestSecretsNeverReachTheCommandLine:
    def test_no_subcommand_accepts_a_secret_as_an_option(self, cs):
        """`ps` shows another process's argv on this platform, so a secret
        passed as a flag is readable by anything running for as long as the
        process lives. No option may take one."""
        parser = cs.build_parser()
        forbidden = ("password", "passphrase", "secret", "value", "token", "key")
        found = []
        for action in parser._actions:                       # noqa: SLF001
            for opt in action.option_strings:
                bare = opt.lstrip("-").replace("-", "_").lower()
                if bare in ("api_key",):                     # a KIND, not a value
                    continue
                if any(word == bare or bare.endswith("_" + word)
                       for word in forbidden):
                    found.append(opt)
        for sub in parser._subparsers._group_actions:        # noqa: SLF001
            for name, sp in getattr(sub, "choices", {}).items():
                for action in sp._actions:                   # noqa: SLF001
                    for opt in action.option_strings:
                        bare = opt.lstrip("-").replace("-", "_").lower()
                        if any(word == bare or bare.endswith("_" + word)
                               for word in forbidden):
                            found.append(f"{name} {opt}")
        assert not found, f"these options would put a secret in argv: {found}"

    def test_help_touches_no_store_and_costs_nothing(self, tmp_path):
        """`--help` must never read, write or create anything."""
        env = dict(os.environ)
        env["CDSFL_CREDENTIAL_STORE"] = str(tmp_path / "must-not-appear.enc")
        env.pop("CDSFL_CREDENTIAL_PASSPHRASE", None)
        done = subprocess.run([sys.executable, str(MODULE), "--help"],
                              capture_output=True, text=True, timeout=120, env=env)
        assert done.returncode == 0, done.stderr
        assert "usage" in done.stdout.lower()
        assert not (tmp_path / "must-not-appear.enc").exists()
        assert list(tmp_path.iterdir()) == []


class TestThePassphraseIsHeldAsideInAFreeWindow:
    """★ FOUND BY TRACING DEPENDENTS, 2026-11-11, not by a failure.

    `bench/tests/conftest.py` strips credential-shaped environment variables for
    the duration of a free-network test, on the measured argument that spending
    money requires a CREDENTIAL and not a hostname, so a host deny-list is a
    losing race. Its suffix list catches `_API_KEY`, `_TOKEN`, `_SECRET`,
    `_ACCESS_KEY` and `_SECRET_KEY`.

    `CDSFL_CREDENTIAL_PASSPHRASE` ends in `_PASSPHRASE` and matched NONE of
    them. On its own a passphrase bills nobody -- but it opens a store whose
    entire purpose is to hold vendor API keys, so leaving it in the environment
    reinstates the exact route the hold-list exists to close, one indirection
    further out. It is now named explicitly, and these tests pin that, because a
    line added to a list with nothing asserting it is the addition-nothing-
    reaches defect in its quietest form.
    """

    @pytest.fixture()
    def conftest_mod(self):
        return _load(ROOT / "bench" / "tests" / "conftest.py", "_cred_conftest")

    def test_the_passphrase_variable_is_on_the_hold_list(self, cs, conftest_mod):
        """Named from the STORE module, so a rename cannot silently unlist it."""
        assert cs.PASSPHRASE_ENV in conftest_mod._CREDENTIAL_NAMES, (
            f"{cs.PASSPHRASE_ENV} is not held aside during a free-network "
            f"window, so a test in that window could unlock the credential "
            f"store and reach a billable key")

    def test_the_suffix_list_alone_would_not_catch_it(self, cs, conftest_mod):
        """ANTI-VACUITY. If a suffix ever covers it, the explicit entry becomes
        redundant and this test says so rather than passing quietly."""
        assert not cs.PASSPHRASE_ENV.endswith(conftest_mod._CREDENTIAL_SUFFIXES), (
            "a suffix now covers the passphrase variable, so the explicit "
            "hold-list entry is redundant -- check which before removing either")

    def test_holding_removes_it_and_restoring_returns_it_intact(self, cs,
                                                                conftest_mod,
                                                                monkeypatch):
        monkeypatch.setenv(cs.PASSPHRASE_ENV, "a-probe-passphrase-value")
        conftest_mod._hold_credentials()
        try:
            assert cs.PASSPHRASE_ENV not in os.environ, (
                "the passphrase survived the hold")
        finally:
            conftest_mod._restore_credentials()
        assert os.environ.get(cs.PASSPHRASE_ENV) == "a-probe-passphrase-value", (
            "the passphrase was not restored, or was restored altered")

    def test_the_store_cannot_be_opened_from_the_environment_while_held(
            self, cs, conftest_mod, tmp_path, monkeypatch):
        """THE PROPERTY, END TO END: with the variable held, a caller that
        relies on the environment for its passphrase gets nothing."""
        path = tmp_path / "credentials.enc"
        cs.init_store(PASSPHRASE, path)
        cs.add_credential("openrouter", cs.KIND_API_KEY, SECRET_KEY, PASSPHRASE,
                          path=path)
        monkeypatch.setenv(cs.PASSPHRASE_ENV, PASSPHRASE)
        assert cs.read_passphrase() == PASSPHRASE, "the probe itself is broken"
        conftest_mod._hold_credentials()
        try:
            assert cs.PASSPHRASE_ENV not in os.environ
        finally:
            conftest_mod._restore_credentials()


class TestWhereItLives:
    def test_the_default_path_is_outside_the_repository(self, cs):
        """A credential store inside a git working tree is 1 careless
        `git add -A` from being committed. Path only; the file is never read."""
        default = cs.DEFAULT_STORE_PATH.resolve()
        assert ROOT.resolve() not in default.parents, (
            f"{default} is inside the repository at {ROOT}")

    def test_the_environment_override_is_honoured(self, cs, tmp_path, monkeypatch):
        target = tmp_path / "elsewhere.enc"
        monkeypatch.setenv("CDSFL_CREDENTIAL_STORE", str(target))
        assert cs.store_path() == target

    def test_a_missing_store_is_a_clean_refusal_naming_the_remedy(self, cs, tmp_path):
        with pytest.raises(cs.CredentialStoreError) as exc:
            cs.get_credential("anything", PASSPHRASE, tmp_path / "absent.enc")
        assert "init" in str(exc.value)


class TestTheBackendViewIsReachableAndLeaksNothing:
    """★ THE STORE MUST HAVE A CALLER. `additive-standard`'s symmetric form:
    an addition nothing reaches is not additive either."""

    @pytest.fixture(scope="class")
    def ux(self):
        return _load(BACKEND, "_ux_cred_guard")

    def test_the_settings_view_calls_the_store(self, ux, tmp_path, monkeypatch):
        monkeypatch.setenv("CDSFL_CREDENTIAL_STORE", str(tmp_path / "none.enc"))
        view = ux.credentials()
        assert view["available"] is True, view
        assert view["exists"] is False and view["locked"] is True

    def test_the_view_reports_policy_read_from_the_module(self, ux, cs, tmp_path,
                                                          monkeypatch):
        """Restated policy drifts. The view must read the module's own lists."""
        monkeypatch.setenv("CDSFL_CREDENTIAL_STORE", str(tmp_path / "none.enc"))
        view = ux.credentials()
        assert view["accepts"] == list(cs.ALLOWED_KINDS)
        assert view["refuses"] == list(cs.KIND_REFUSED)
        assert view["min_passphrase_chars"] == cs.MIN_PASSPHRASE_CHARS

    def test_the_unlocked_view_returns_metadata_and_no_value(self, ux, cs, tmp_path,
                                                             monkeypatch):
        path = tmp_path / "credentials.enc"
        cs.init_store(PASSPHRASE, path)
        cs.add_credential("openrouter", cs.KIND_API_KEY, SECRET_KEY, PASSPHRASE,
                          path=path)
        monkeypatch.setenv("CDSFL_CREDENTIAL_STORE", str(path))
        view = ux.credentials(PASSPHRASE)
        assert view["locked"] is False and view["entry_count"] == 1
        assert SECRET_KEY not in json.dumps(view)

    def test_a_wrong_passphrase_leaves_the_view_locked(self, ux, cs, tmp_path,
                                                       monkeypatch):
        path = tmp_path / "credentials.enc"
        cs.init_store(PASSPHRASE, path)
        monkeypatch.setenv("CDSFL_CREDENTIAL_STORE", str(path))
        view = ux.credentials("wrong-but-long-enough")
        assert view["locked"] is True and view["entries"] == []
        assert "why" in view
