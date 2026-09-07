"""Sealing the scoring keys must never be able to destroy them.

WHAT THIS GUARDS. `bench/vault_keys.sh vault` tars the plaintext key store into an
AES-256 archive and then deletes the plaintext. The passphrase is deliberately not
stored on this machine, so if the archive is wrong the keys are gone -- 29 scoring
keys, 27 of them for exams that have never been run.

THE DEFECT FOUND 2026-09-07, before the founder was asked to run it. The script
carried `set -eu` and NOT `set -o pipefail`. A pipeline's exit status is its LAST
command's, so `tar ... | openssl ... -out "$VAULT"` returns 0 whenever openssl
succeeds EVEN IF TAR FAILED, `set -e` does not fire, and `rm -rf "$STORE"` runs
anyway. Proved by execution: under `set -eu` a failing first stage reaches the
delete step with exit 0; under `set -euo pipefail` it aborts first.

Two further paths were closed at the same time. Writing straight over an existing
archive would destroy any keys it held that the current store does not -- and the
passphrase needed to check first is, by design, unavailable here. And nothing
proved the archive could be opened before the plaintext was deleted, which is how
a backup turns out to be empty on the day it is needed.
"""
from __future__ import annotations

import os
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "bench" / "vault_keys.sh"
PASS = "correct-horse-battery-staple-2026"


def _conf(tmp_path: Path) -> dict:
    store = tmp_path / "keys"
    store.mkdir()
    for i in range(1, 6):
        (store / f"ft-{i:03d}_KEY.json").write_text(f'{{"answer": "secret-{i}"}}')
    vault = tmp_path / "keys.tar.gz.enc"
    conf = tmp_path / "scoring.env"
    conf.write_text(textwrap.dedent(f"""
        CDSFL_STORE="{store}"
        CDSFL_VAULT="{vault}"
        CDSFL_LEGACY_STORES=""
    """).strip() + "\n")
    return {"store": store, "vault": vault, "conf": conf}


def _codec_bin(tmp_path: Path, mode: str) -> Path:
    """A stand-in for `openssl enc` that needs no terminal.

    WHAT IS AND IS NOT UNDER TEST. openssl reads its passphrase from /dev/tty and
    never from stdin, which is the property worth keeping -- it is the entire
    basis of the claim that the passphrase is not on this machine, since no
    process, config file or environment variable can supply it. So the passphrase
    path is left exactly as it ships, and these tests exercise the logic that was
    ADDED on 2026-09-07: pipefail, preserving an existing archive, writing and
    checking the manifest, and refusing to delete the plaintext against a stub.
    AES-256 itself is openssl's to get right, not this script's.

    mode "passthrough": a working codec (store) and its inverse (retrieve).
    mode "stub": exits 0 having written 5 bytes, the failure the size floor exists
    to catch.
    """
    d = tmp_path / f"bin_{mode}"
    d.mkdir(exist_ok=True)
    if mode == "passthrough":
        body = (
            '#!/bin/bash\n'
            'out=""; dec=0; inp=""; prev=""\n'
            'for a in "$@"; do\n'
            '  [ "$prev" = "-out" ] && out="$a"\n'
            '  [ "$prev" = "-in" ] && inp="$a"\n'
            '  [ "$a" = "-d" ] && dec=1\n'
            '  prev="$a"\n'
            'done\n'
            'if [ "$dec" = "1" ]; then cat "$inp"; else cat > "$out"; fi\n'
            'exit 0\n')
    else:
        body = (
            '#!/bin/bash\n'
            'out=""; prev=""\n'
            'for a in "$@"; do [ "$prev" = "-out" ] && out="$a"; prev="$a"; done\n'
            'cat >/dev/null\n'
            '[ -n "$out" ] && printf "stub" > "$out"\n'
            'exit 0\n')
    (d / "openssl").write_text(body)
    (d / "openssl").chmod(0o755)
    return d


def _run(args, conf, tmp_path, mode="passthrough", expect_ok=True):
    env = dict(os.environ, CDSFL_SCORING_CONF=str(conf),
               PATH=f"{_codec_bin(tmp_path, mode)}:{os.environ['PATH']}")
    r = subprocess.run(["bash", str(SCRIPT), *args], capture_output=True,
                       text=True, env=env)
    if expect_ok:
        assert r.returncode == 0, f"{args} failed:\n{r.stdout}\n{r.stderr}"
    return r


def test_pipefail_is_set_so_a_failed_tar_cannot_reach_the_delete():
    src = SCRIPT.read_text()
    assert "set -o pipefail" in src, (
        "without pipefail, a failed tar leaves the pipeline at exit 0 and the "
        "plaintext keys are deleted against a bad archive")


@pytest.mark.skipif(not SCRIPT.exists(), reason="vault script absent")
def test_seal_then_verify_round_trips_and_the_plaintext_is_gone(tmp_path):
    c = _conf(tmp_path)
    out = _run(["vault"], c["conf"], tmp_path).stdout
    assert "sealed:" in out
    assert not c["store"].exists(), "the plaintext store survived the seal"
    assert c["vault"].is_file() and c["vault"].stat().st_size > 1024
    assert Path(str(c["vault"]) + ".manifest").is_file(), "no manifest was written"

    v = _run(["verify"], c["conf"], tmp_path).stdout
    assert "opened: 5 file(s)" in v, v
    assert "every file matches its recorded hash" in v, v
    assert not c["store"].exists(), "verify restored plaintext it should not have"


@pytest.mark.skipif(not SCRIPT.exists(), reason="vault script absent")
def test_an_existing_archive_is_preserved_not_overwritten(tmp_path):
    """It may hold keys the current store does not, and the passphrase needed to
    check is deliberately not on this machine."""
    c = _conf(tmp_path)
    _run(["vault"], c["conf"], tmp_path)
    first = c["vault"].read_bytes()
    c["store"].mkdir()
    (c["store"] / "ft-999_KEY.json").write_text('{"answer": "later"}')
    out = _run(["vault"], c["conf"], tmp_path).stdout
    assert "existing archive preserved as:" in out, out
    prev = list(tmp_path.glob("keys.tar.gz.enc.prev-*"))
    assert len(prev) == 1, f"the earlier archive was not preserved: {prev}"
    assert prev[0].read_bytes() == first, "the preserved copy is not the original"


@pytest.mark.skipif(not SCRIPT.exists(), reason="vault script absent")
def test_a_stub_archive_refuses_to_delete_the_plaintext(tmp_path):
    """The size floor is the last line of defence: a write that produced a file
    but not an archive must not be treated as a successful seal."""
    c = _conf(tmp_path)
    r = _run(["vault"], c["conf"], tmp_path, mode="stub", expect_ok=False)
    assert r.returncode != 0, "a stub archive was accepted as a successful seal"
    assert "REFUSING TO DELETE THE PLAINTEXT" in r.stderr, r.stdout + r.stderr
    assert c["store"].is_dir(), "the plaintext keys were deleted anyway"
    assert len(list(c["store"].glob("*.json"))) == 5, "keys were lost"


def _legacy_conf(tmp_path: Path):
    """A store, a vault, and a legacy directory shaped like the real one:
    nested subdirectory, and key material that is not top-level .json."""
    store = tmp_path / "store"
    legacy = tmp_path / "legacy"
    (legacy / "br2_keys").mkdir(parents=True)
    (legacy / "control_GROUND_TRUTH.json").write_text('{"a": 1}')
    (legacy / "control_KEY.md").write_text("# the answers")
    for i in range(1, 28):
        (legacy / "br2_keys" / f"ft-{i:03d}_KEY.json").write_text(f'{{"k": {i}}}')
    vault = tmp_path / "v.dat"
    conf = tmp_path / "scoring.env"
    conf.write_text(
        f'CDSFL_STORE="{store}"\nCDSFL_VAULT="{vault}"\n'
        f'CDSFL_LEGACY_STORES="{legacy}"\n')
    return {"store": store, "legacy": legacy, "vault": vault, "conf": conf}


def test_the_fold_carries_subdirectories_and_non_json_key_material(tmp_path):
    """THE DEFECT THIS PINS. The fold copied top-level *.json only and then
    `rm -rf`'d the whole directory. Measured against the real stray store on
    2026-09-07: 31 files present, 1 matched the glob, 30 would have been
    destroyed -- including all 27 BR2 answer keys, which sit in a subdirectory.
    These keys have no other copy."""
    c = _legacy_conf(tmp_path)
    out = _run(["vault"], c["conf"], tmp_path).stdout
    assert "all verified" in out, out
    assert not c["legacy"].exists(), "the legacy store was left behind"

    # The archive is the passthrough codec's output, so it is a readable tar.
    import tarfile, io
    with tarfile.open(fileobj=io.BytesIO(c["vault"].read_bytes()), mode="r:gz") as t:
        names = [n.split("/", 1)[-1] for n in t.getnames() if not n.endswith("/")]
        # macOS tar emits AppleDouble `._` sidecars; they are not key files.
        names = [n for n in names if not Path(n).name.startswith("._")]
    assert "control_KEY.md" in names, "a non-.json key file was lost in the fold"
    assert sum(1 for n in names if n.startswith("br2_keys/")) == 27, (
        f"BR2 keys lost: only {[n for n in names if 'br2' in n]}")
    assert "control_GROUND_TRUTH.json" in names


def test_an_incomplete_fold_refuses_to_delete_the_source(tmp_path):
    """Verification before deletion is the point. If anything fails to arrive,
    the legacy directory must survive untouched."""
    c = _legacy_conf(tmp_path)
    # A read-protected file cannot be folded; the source must then be kept.
    victim = c["legacy"] / "br2_keys" / "ft-001_KEY.json"
    hostile = tmp_path / "bin_hostile"
    hostile.mkdir()
    (hostile / "tar").write_text(
        '#!/bin/bash\n'
        '# extract everything EXCEPT one file, simulating a partial fold\n'
        'if [ "$1" = "-cf" ]; then exec /usr/bin/tar "$@"; fi\n'
        'exec /usr/bin/tar --exclude "./br2_keys/ft-001_KEY.json" "$@"\n')
    (hostile / "tar").chmod(0o755)
    env = dict(os.environ, CDSFL_SCORING_CONF=str(c["conf"]),
               PATH=f"{hostile}:{_codec_bin(tmp_path, 'passthrough')}:{os.environ['PATH']}")
    r = subprocess.run(["bash", str(SCRIPT), "vault"], capture_output=True,
                       text=True, env=env)
    assert r.returncode != 0, "an incomplete fold was accepted"
    assert "REFUSING TO REMOVE" in r.stderr, r.stdout + r.stderr
    assert c["legacy"].is_dir(), "the source was deleted despite a failed fold"
    assert victim.is_file(), "the un-folded key was destroyed"


# ---------------------------------------------------------------------------
# THE UNSEAL-RESEAL CYCLE, added 2026-09-07 PM after it failed in the founder's
# hands. Everything above tests a single seal. Nothing tested the SECOND one,
# and that is where the store had been quietly made unreadable.
# ---------------------------------------------------------------------------


def _conf_nested(tmp_path: Path) -> dict:
    """A store shaped like the real one: files at top level AND in subdirectories.

    The real store holds `br2_keys/` (27 answer keys), `targets/` and
    `clearances/`. Every fixture above used a flat store, which is exactly why
    4 top-level-only defects survived in this file until they were hit in
    production: a flat store cannot distinguish "counts entries" from "counts
    files", nor "chmods files" from "chmods directories too".
    """
    c = _conf(tmp_path)
    sub = c["store"] / "br2_keys"
    sub.mkdir()
    for i in range(1, 4):
        (sub / f"ft-{i:03d}_KEY.json").write_text(f'{{"nested": "secret-{i}"}}')
    deeper = c["store"] / "targets"
    deeper.mkdir()
    (deeper / "exp52_factorial.md").write_text("# a target article\n")
    # 5 flat + 3 nested + 1 deeper = 9 files; 7 TOP-LEVEL entries (5 files, 2 dirs)
    c["n_files"] = 9
    c["n_toplevel"] = 7
    return c


def test_a_store_can_be_unsealed_and_resealed(tmp_path):
    """The defect that cost a 60-mile round trip.

    `unvault` ran `chmod 600 "$STORE"/*`, and that glob matches DIRECTORIES.
    Mode 600 on a directory removes its execute bit, so it cannot be traversed,
    so the next `vault`'s tar fails with "Cannot stat: Permission denied", the
    pipeline fails, pipefail aborts, and nothing is sealed. It would have
    recurred on every cycle, because unvault always restores those directories.
    """
    c = _conf_nested(tmp_path)
    _run(["vault"], c["conf"], tmp_path)
    assert not c["store"].exists(), "plaintext should be gone after sealing"

    _run(["unvault"], c["conf"], tmp_path)
    assert c["store"].is_dir()

    # Every directory restored must still be traversable by its owner.
    shut = [p for p in c["store"].rglob("*") if p.is_dir() and not (p.stat().st_mode & 0o100)]
    assert not shut, f"directories left without the owner execute bit: {shut}"

    # And the whole point: sealing again must work.
    out = _run(["vault"], c["conf"], tmp_path).stdout
    assert "sealed" in out, out
    assert not c["store"].exists(), "second seal did not remove the plaintext"


def test_restored_files_are_600_and_directories_are_700(tmp_path):
    """Tightening permissions must not make the store unusable.

    The fix must not overshoot in the other direction either: files stay 600 and
    nothing is granted to group or other.
    """
    c = _conf_nested(tmp_path)
    _run(["vault"], c["conf"], tmp_path)
    _run(["unvault"], c["conf"], tmp_path)
    for p in c["store"].rglob("*"):
        mode = p.stat().st_mode & 0o777
        if p.is_dir():
            assert mode == 0o700, f"{p} is {oct(mode)}, want 0o700"
        else:
            assert mode == 0o600, f"{p} is {oct(mode)}, want 0o600"


def test_verify_counts_files_recursively_not_top_level_entries(tmp_path):
    """`verify` reported "opened: 18 file(s)" seconds after "sealed: 53 keys".

    The hash check was always complete -- `shasum -c` walks the manifest, which
    is recursive -- so only the printed count was wrong. But a verification step
    whose own output looks like a 65% data loss stops the operator dead, which
    is what it did.
    """
    c = _conf_nested(tmp_path)
    _run(["vault"], c["conf"], tmp_path)
    out = _run(["verify"], c["conf"], tmp_path).stdout
    assert f"opened: {c['n_files']} file(s)" in out, (
        f"expected the recursive count {c['n_files']}; got:\n{out}\n"
        f"(the top-level entry count would be {c['n_toplevel']})"
    )
    assert "VERIFIED" in out, out


def test_every_name_shape_in_the_real_store_is_described(tmp_path):
    """The register must not contain UNCLASSIFIED entries.

    The first register ever generated reported "17 key(s) UNCLASSIFIED" -- and
    they were the answer keys for every exam already run, their target articles,
    and the sequencer's clearance files. The register exists precisely so the
    operator can see what is sealed without the passphrase; one that cannot name
    the completed exams has failed at its only job.

    Hermetic: builds a store carrying one of every name shape the real store
    holds, rather than asserting against the operator's own machine.
    """
    c = _conf(tmp_path)
    for name in [
        "exp48_chemistry_answer_key.json", "exp49_engineering_answer_key.json",
        "exp50_physics_answer_key.json", "exp51_biology_answer_key.json",
        "exp52_factorial_answer_key.json", "exp53_control_zero_answer_key.json",
        "exp53_zone_controller_answer_key.json",
        "control_two_distinct_defects_KEY.md",
        "control_two_distinct_defects_GROUND_TRUTH.json",
        "canary_catalogue_memory_2026-09-01.json",
        "manifest_cdsfl_sim.qvlxpaZDnD.json", "README.md",
    ]:
        (c["store"] / name).write_text("x")
    (c["store"] / "targets").mkdir()
    (c["store"] / "targets" / "exp52_factorial.md").write_text("# target\n")
    (c["store"] / "clearances").mkdir()
    (c["store"] / "clearances" / ".cleared_exp48.detail").write_text("cleared\n")

    r = _run(["register"], c["conf"], tmp_path)
    reg = Path(str(c["vault"]) + ".register")
    assert reg.is_file(), r.stdout + r.stderr
    text = reg.read_text()
    bad = [ln for ln in text.splitlines() if "UNCLASSIFIED" in ln]
    assert not bad, (
        "these name shapes have no describe() case -- add one before sealing:\n  "
        + "\n  ".join(bad)
    )
    # and the register must actually describe things, not just be empty
    assert "Bench Run 2 answer key" in text or "answer key" in text, text[:400]


# ---------------------------------------------------------------------------
# THE STRAY SCAN COULD NOT SEE THE REPOSITORY'S OWN KEY DIRECTORY.
# Found 2026-09-08 by a defect sweep, verified independently. `find "$HOME"
# -maxdepth 5` cannot reach a FILE inside bench/cdsfl_registry/targets/, which
# is depth 6 -- and that is exactly where the Exp 48 leak came from. The gate
# `bench/arc_sequencer.sh:50` launches a whole experiment arc on this scan's
# verdict, so a key restored to that directory produced a false all-clear.
# ---------------------------------------------------------------------------


def _is_clean(stdout: str) -> bool:
    """True only if the scan reported a clean state.

    `"VAULTED" in stdout` is NOT a clean check: "UNVAULTED" CONTAINS "VAULTED",
    so the naive form passes in both directions and can never fail. Written that
    way here on 2026-09-08 and caught the same hour by mutating the scan pattern
    and watching the test stay green -- the assertion could not see the defect
    it existed to catch.
    """
    return "UNVAULTED" not in stdout and "VAULTED" in stdout


def _status_with_home(tmp_path, home, conf):
    env = dict(os.environ, HOME=str(home), CDSFL_SCORING_CONF=str(conf),
               PATH=f"{_codec_bin(tmp_path, 'passthrough')}:{os.environ['PATH']}")
    return subprocess.run(["bash", str(SCRIPT), "status"], capture_output=True,
                          text=True, env=env)


def _mock_home(tmp_path):
    """A home whose repo sits where the real one does: 2 levels down."""
    home = tmp_path / "home"
    (home / "Developer_Projects" / "Constraint_Engineering" / "bench"
          / "cdsfl_registry" / "targets").mkdir(parents=True)
    store = home / "Library" / "Application Support" / "cdsfl-scoring"
    store.mkdir(parents=True)
    vault = home / "Library" / "Application Support" / ".cdsfl-store.dat"
    conf = tmp_path / "scoring.env"
    conf.write_text(textwrap.dedent(f"""
        CDSFL_STORE="{store}"
        CDSFL_VAULT="{vault}"
        CDSFL_LEGACY_STORES=""
    """).strip() + "\n")
    return home, store, vault, conf


def test_a_key_at_repository_depth_is_seen_by_the_stray_scan(tmp_path):
    """Depth 6 is where the real answer keys were tracked. The scan must reach it."""
    home, store, vault, conf = _mock_home(tmp_path)
    # sealed state: no plaintext store, an archive present
    store.rmdir()
    vault.write_bytes(b"x" * 5000)

    clean = _status_with_home(tmp_path, home, conf)
    assert _is_clean(clean.stdout), f"baseline should be clean:\n{clean.stdout}{clean.stderr}"

    deep = (home / "Developer_Projects" / "Constraint_Engineering" / "bench"
                 / "cdsfl_registry" / "targets" / "exp50_physics_answer_key.json")
    deep.write_text('{"planted_false": ["PH-07"]}')

    dirty = _status_with_home(tmp_path, home, conf)
    assert "UNVAULTED" in dirty.stdout, (
        "a real answer key sitting at repository depth was NOT detected. That is "
        "the false all-clear that would let bench/arc_sequencer.sh launch an "
        f"entire arc against live plaintext keys.\n{dirty.stdout}{dirty.stderr}")
    assert "exp50_physics_answer_key.json" in dirty.stdout, dirty.stdout


def test_run_logs_named_canary_do_not_block_the_arc(tmp_path):
    """The pattern must not match run OUTPUT on its directory name.

    Removing the depth ceiling surfaced 6 files matching '*canary*.json', all of
    them sim45 run reports and status vocabularies carrying no answer material
    (measured: 0 canary_id / defect_id / planted_location / seeded_defects).
    Left broad, the gate would block every arc on ordinary logs.
    """
    home, store, vault, conf = _mock_home(tmp_path)
    store.rmdir()
    vault.write_bytes(b"x" * 5000)
    logs = (home / "Developer_Projects" / "Constraint_Engineering" / "bench"
                 / "logs" / "sim45_canary_20260901T145630Z")
    logs.mkdir(parents=True)
    (logs / "sim45_canary_20260901T145630Z_report.json").write_text('{"rounds": 4}')
    (logs / "sim45_canary_20260901T145630Z_status_vocabulary.json").write_text('{"v": 1}')

    r = _status_with_home(tmp_path, home, conf)
    assert _is_clean(r.stdout), (
        "run logs whose directory is named *canary* were treated as key material, "
        f"which would block the arc gate permanently:\n{r.stdout}{r.stderr}")

    # ...but a real catalogue in the same place MUST still be caught
    (logs / "canary_catalogue_memory_2026-09-01.json").write_text('{"canary_id": "K1"}')
    r2 = _status_with_home(tmp_path, home, conf)
    assert "UNVAULTED" in r2.stdout, (
        "narrowing the pattern lost a real canary catalogue -- that is the "
        f"blind spot the narrowing must not create:\n{r2.stdout}{r2.stderr}")
