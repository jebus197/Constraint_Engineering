# Sealing the scoring keys: the commands, and 3 defects found while preparing them

**2026-09-07, 01:15 BST. Constraint Engineering (CDSFL).**

Nothing has been sealed. Sealing requires a passphrase that is deliberately unavailable to anything running on this machine, so it is the operator's action. What follows is the procedure, and an account of why the previously recorded procedure would not have worked.

## The 3 defects, all found by running the tooling rather than trusting it

**1. The seal covered a directory that does not exist.** `vault_keys.sh` seals `$CDSFL_STORE`, which is `~/Library/Application Support/cdsfl-scoring`. That path is absent. The 31 key files live in `~/Developer_Projects/CDSFL_experiment_keys/`, which the vault system did not know about — its own status output called them *"stray plaintext key file(s) outside every known store"*. Run in that state, `vault` prints `already vaulted (no plaintext store)` and seals nothing.

**2. The obvious repair would have destroyed 27 answer keys.** Telling the tool about that directory makes it a legacy store, which `vault` folds in. The fold was:

```bash
cp -p "$legacy"/*.json "$STORE"/ 2>/dev/null || true
rm -rf "$legacy"
```

Top-level `*.json` only, then delete the directory. Measured against the real store: **31 files present, 1 matched the glob, 30 would have been destroyed** — including all 27 Bench Run 2 answer keys, which sit in a `br2_keys/` subdirectory, and `control_two_distinct_defects_KEY.md`, which the glob cannot see. `2>/dev/null || true` meant a total copy failure was silent and `rm -rf` ran regardless. These keys have no other copy.

**3. A failed archive step could not stop the delete.** The script set `set -eu` and not `set -o pipefail`. A pipeline's status is its last command's, so `tar -czf - ... | openssl enc ... -out "$VAULT"` returns 0 whenever `openssl` succeeds **even if `tar` failed**, `set -e` does not fire, and `rm -rf "$STORE"` runs against a bad archive. Proved by execution: under `set -eu` a failing first stage reaches the delete step with exit 0; under `set -euo pipefail` it aborts first.

A fourth, smaller error was corrected at the same time: `check_one` counted top-level entries with `ls -1 | wc -l`, so a store holding 29 keys reported **"4 key(s)"** — 3 files plus `br2_keys/` counted once, its 27 answer keys invisible. An operator reading that would materially misjudge the exposure being warned about.

## What is fixed, in `bench/vault_keys.sh`

- `set -o pipefail`, so a failed archive step stops the script before any delete.
- The fold copies the whole tree (`tar` piped, `COPYFILE_DISABLE=1`) and then compares **every** source file against its copy with `cmp`. One missing or differing file and it refuses to remove the source, naming what did not fold.
- An existing archive is never overwritten. It is moved to `$VAULT.prev-<UTC timestamp>`, because it may hold keys the current store does not and the passphrase needed to check is by design not available here.
- A manifest of **names and SHA-256 hashes only** — no key content — is written beside the archive.
- The plaintext is deleted only after the ciphertext is confirmed present and above a size floor. A stub archive refuses and leaves the keys in place.
- A new `verify` subcommand opens the archive, counts the files, checks them against the manifest, and **restores nothing**.

Covered by `bench/tests/test_vault_seal_is_safe_2026-09-07.py` — 6 tests, including one that simulates a partial fold and asserts the source survives, and one that feeds a stub archive and asserts the plaintext is kept.

The passphrase path is untouched: `openssl` reads it from `/dev/tty` and never from stdin, a config file or an environment variable, which is the entire basis of the claim that it is not on this machine. The tests therefore exercise the added logic with a stand-in codec and leave AES-256 to `openssl`.

## The procedure

Run from the repository root. Each step prompts at the terminal.

**Step 1 — optional, recommended.** An archive of 174,112 bytes already exists from an earlier session. If its passphrase is to hand, open it first so everything ends in one archive rather than two. If the passphrase is lost, skip this: the old archive is preserved untouched with a timestamp and there will simply be 2 archives.

```bash
bash bench/vault_keys.sh unvault
```

**Step 2 — see what is about to be sealed.** Expect `UNVAULTED — 31 key file(s) in plaintext`.

```bash
bash bench/vault_keys.sh status
```

**Step 3 — seal.** Asks for the passphrase twice, to set and to confirm.

```bash
bash bench/vault_keys.sh vault
```

**Step 4 — prove it opens.** Same passphrase; restores nothing.

```bash
bash bench/vault_keys.sh verify
```

**Step 5 — confirm.** Expect `VAULTED — no plaintext key file on disk in any known or scanned location.`

```bash
bash bench/vault_keys.sh status
```

## Afterwards

Scoring does not need the keys open for long. `run` unseals only for the duration of one command and re-seals on exit, including on failure or interrupt:

```bash
bash bench/vault_keys.sh run -- <scoring command>
```

The previous scoring config is backed up at `~/.config/cdsfl/scoring.env.bak-20260907`. `CDSFL_LEGACY_STORES` is **newline-separated**, not space-separated: the script reads it with `while IFS= read -r loc` and builds its stray-scan regex with `printf '%s\n'`, and space separation cannot work anyway because a store path may contain a space — the canonical one is under `Application Support`.
