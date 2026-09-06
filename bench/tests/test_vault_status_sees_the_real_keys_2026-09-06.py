"""The vault status check reported VAULTED with 29 plaintext answer keys on disk.

WHY THIS MATTERS MORE THAN A WRONG STATUS LINE. bench/arc_sequencer.sh:50 gates a
whole experiment arc on it:

    if ! bash bench/vault_keys.sh status | grep -q '^VAULTED'; then halt ...

So a false all-clear does not merely misinform; it lets an arc start with the
answer keys readable. The script's own header states the control it is supposed to
enforce: "The only control that actually binds is that no plaintext key is on disk
at all." Its scan could not see the directory where they were.

IT WAS BLIND TWICE OVER, measured 2026-09-06:
  1. It matched only '*answer_key*.json'. The BR2 keys are 'ft-NNN_KEY.json' and
     the exp55 pair are '*_KEY.md' / '*GROUND_TRUTH.json' -- 0 of 29 real keys
     matched the pattern, even with the path exclusion removed.
  2. It excluded "Developer_Projects", which is where they live. The corrected
     patterns match 0 files inside the repository, so that exclusion was
     suppressing only true positives.

These tests are hermetic: they build a throwaway HOME and scoring config, so they
assert on the SCRIPT'S BEHAVIOUR rather than on the machine's current state. A
test that passed only because this machine happens to hold keys would go green the
moment the keys were sealed, which is exactly backwards.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "bench" / "vault_keys.sh"


def _sandbox(tmp_path: Path, key_names: list[str]) -> dict:
    """A throwaway HOME containing `key_names` at the depth the real keys sit at."""
    home = tmp_path / "home"
    keydir = home / "Developer_Projects" / "CDSFL_experiment_keys" / "br2_keys"
    keydir.mkdir(parents=True)
    for name in key_names:
        (keydir / name).write_text('{"ground_truth_notes": "sentinel"}')
    conf_dir = home / ".config" / "cdsfl"
    conf_dir.mkdir(parents=True)
    store = home / "Library" / "Application Support" / "cdsfl-scoring"
    vault = home / "Library" / "Application Support" / "cdsfl-scoring.tar.gz.enc"
    vault.parent.mkdir(parents=True, exist_ok=True)
    vault.write_bytes(b"ciphertext-placeholder")
    (conf_dir / "scoring.env").write_text(
        f'CDSFL_STORE="{store}"\n'
        f'CDSFL_VAULT="{vault}"\n'
        f'CDSFL_LEGACY_STORES="{home}/legacy"\n'
        f'CDSFL_TARGETS="{home}/targets"\n')
    env = dict(os.environ)
    env["HOME"] = str(home)
    env["CDSFL_SCORING_CONF"] = str(conf_dir / "scoring.env")
    return env


def _status(env) -> str:
    r = subprocess.run(["bash", str(SCRIPT), "status"],
                       capture_output=True, text=True, env=env, cwd=str(REPO))
    return r.stdout + r.stderr


def test_a_br2_style_key_is_detected(tmp_path):
    """ft-NNN_KEY.json is the real BR2 naming. The old pattern missed it entirely."""
    env = _sandbox(tmp_path, ["ft-001_KEY.json"])
    out = _status(env)
    assert "UNVAULTED" in out, f"a plaintext BR2 key was not detected:\n{out}"
    assert "ft-001_KEY.json" in out, "the offending file must be named, not just counted"


def test_markdown_and_ground_truth_keys_are_detected(tmp_path):
    env = _sandbox(tmp_path, ["control_KEY.md", "control_GROUND_TRUTH.json"])
    out = _status(env)
    assert "UNVAULTED" in out
    assert "control_KEY.md" in out
    assert "control_GROUND_TRUTH.json" in out


def test_a_clean_home_reports_vaulted(tmp_path):
    """The check must not simply always fail -- that would be as useless."""
    env = _sandbox(tmp_path, [])
    out = _status(env)
    assert "VAULTED" in out and "UNVAULTED" not in out, out


def test_all_27_br2_keys_are_reported_not_just_the_first(tmp_path):
    names = [f"ft-{i:03d}_KEY.json" for i in range(1, 28)]
    env = _sandbox(tmp_path, names)
    out = _status(env)
    missing = [n for n in names if n not in out]
    assert not missing, f"{len(missing)} of 27 keys went unreported: {missing[:5]}"


def test_the_old_pattern_would_have_missed_these(tmp_path):
    """NON-VACUITY. Reproduce the pre-fix scan and prove it finds nothing, so this
    suite cannot pass against the defect it was written for."""
    env = _sandbox(tmp_path, [f"ft-{i:03d}_KEY.json" for i in range(1, 28)])
    home = env["HOME"]
    old = subprocess.run(
        ["bash", "-c",
         f"find '{home}' -maxdepth 4 -name '*answer_key*.json' 2>/dev/null "
         f"| grep -v 'Developer_Projects' || true"],
        capture_output=True, text=True)
    assert old.stdout.strip() == "", (
        "the pre-fix scan found something, so it was not blind and this fix is "
        f"unnecessary: {old.stdout}")
    assert "UNVAULTED" in _status(env), "the corrected scan must find what the old one could not"


def test_an_empty_legacy_store_list_does_not_kill_the_script(tmp_path):
    """Regression: under `set -e` an empty CDSFL_LEGACY_STORES made the final
    `read` return non-zero and the script exited 1 printing NOTHING."""
    env = _sandbox(tmp_path, [])
    conf = Path(env["CDSFL_SCORING_CONF"])
    conf.write_text(conf.read_text().replace(
        [l for l in conf.read_text().splitlines() if l.startswith("CDSFL_LEGACY_STORES")][0],
        'CDSFL_LEGACY_STORES=""'))
    out = _status(env)
    assert out.strip(), "status produced NO output at all -- cannot tell clean from crashed"
    assert "VAULTED" in out


def test_the_arc_sequencer_still_gates_on_this_line(tmp_path):
    """If the gate stops consuming status, these tests stop protecting anything."""
    seq = (REPO / "bench" / "arc_sequencer.sh").read_text()
    assert "vault_keys.sh status" in seq
    assert "grep -q '^VAULTED'" in seq, (
        "arc_sequencer no longer gates on the VAULTED line; re-point this test")
