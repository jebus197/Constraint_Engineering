#!/bin/bash
# Keep the scoring keys off the filesystem, in readable form, while a panel runs.
#
# WHY. Confining the panel's working directory (panel_cwd) stops discovery by
# proximity and stops a repository grep, but it does not stop two things a model
# with Bash can still do: read an absolute path it has guessed or been told, and
# search the home directory (`find ~ -name '*answer_key*'`, `grep -r planted_false ~`).
# On 2026-07-29 a routed model in Exp 48 did exactly the first of those, using an
# absolute path that a config note inside the repository had disclosed.
#
# WHAT. The key store is held as a single AES-256 encrypted archive whose
# PASSPHRASE IS NEVER ON THIS MACHINE. The operator supplies it to seal, and again
# to open for scoring. Between those two moments the seeded sets are unreadable to
# anything running here — including code the harness itself executes with the
# operator's own credentials, which is the route panel confinement and file
# permissions cannot cover.
#
# This replaced a plain compressed archive (founder ruling, 2026-07-29). That was
# obfuscation: it defeated a filename or content search but not a reader who knew
# where to look, and the location was recoverable. The passphrase is the thing that
# actually binds, precisely because it is the one part of the system that is not
# stored anywhere a process can reach.
#
# The literature calls the risk evaluation-mechanic exploitation rather than
# cheating, and the standard mitigations are grading held out of the agent's
# workspace and no task-adjacent metadata beside its inputs. This is that, done
# simply.
#
# Usage:
#   bench/vault_keys.sh vault              # before a run
#   bench/vault_keys.sh unvault            # for scoring
#   bench/vault_keys.sh status
#   bench/vault_keys.sh run -- <command>   # unvault only for the duration
set -eu

# Location is read from a file OUTSIDE the repository. Naming the key store in a
# tracked file is what leaked it during Exp 48: the note recording where the keys
# had moved to was committed inside the tree the panel could read. One indirection
# is defence in depth, not a boundary — the boundary is panel confinement plus
# detection of any climb out of the staged directory.
CONF="${CDSFL_SCORING_CONF:-$HOME/.config/cdsfl/scoring.env}"
[ -r "$CONF" ] || { echo "missing scoring config: $CONF" >&2; exit 1; }
# shellcheck source=/dev/null
. "$CONF"
: "${CDSFL_STORE:?scoring config did not define CDSFL_STORE}"
: "${CDSFL_VAULT:?scoring config did not define CDSFL_VAULT}"
STORE="$CDSFL_STORE"
VAULT="$CDSFL_VAULT"

vault() {
  # Fold any legacy store into the canonical one first, so a single archive
  # holds everything and no copy is left behind outside the vault system.
  for legacy in $CDSFL_LEGACY_STORES; do
    [ -d "$legacy" ] || continue
    mkdir -p "$STORE"
    cp -p "$legacy"/*.json "$STORE"/ 2>/dev/null || true
    rm -rf "$legacy"
    echo "folded legacy store into the vault: $legacy"
  done
  if [ ! -d "$STORE" ]; then
    echo "already vaulted (no plaintext store)"; return 0
  fi
  if [ -z "$(ls -A "$STORE" 2>/dev/null)" ]; then
    rmdir "$STORE"; echo "already vaulted (empty store removed)"; return 0
  fi
  echo "Sealing the scoring keys. The passphrase is NOT stored anywhere on this"
  echo "machine — you will be asked for it again to score, and it cannot be"
  echo "recovered if lost. Keep it in your password manager."
  tar -czf - -C "$(dirname "$STORE")" "$(basename "$STORE")" \
    | openssl enc -aes-256-cbc -pbkdf2 -iter 600000 -salt -out "$VAULT"
  chmod 600 "$VAULT"
  rm -rf "$STORE"
  echo "sealed: the keys are on disk only as ciphertext, and the passphrase is not."
}

unvault() {
  if [ -d "$STORE" ]; then echo "already unvaulted"; return 0; fi
  [ -f "$VAULT" ] || { echo "NO VAULT at $VAULT" >&2; exit 1; }
  openssl enc -d -aes-256-cbc -pbkdf2 -iter 600000 -in "$VAULT" \
    | tar -xzf - -C "$(dirname "$STORE")" \
    || { echo "could not open the archive — wrong passphrase, or it is damaged" >&2
         rm -rf "$STORE" 2>/dev/null || true; exit 1; }
  chmod 700 "$STORE"; chmod 600 "$STORE"/* 2>/dev/null || true
  echo "unvaulted to $STORE ($(ls -1 "$STORE" | wc -l | tr -d ' ') keys)"
}

status() {
  rc=0
  # Every location that has EVER held a plaintext key, not just the current one.
  # Model-authored code runs inside this harness with the operator's own
  # credentials — the falsifier re-verification path and the execute_python tool
  # both do — so an absolute-path read reaches any plaintext key that exists,
  # whatever the panel's working directory is. The only control that actually
  # binds is that no plaintext key is on disk at all. Adversarial audit,
  # 2026-07-29: a legacy key directory survived outside the vault system and was
  # named in a commit message, and every planted set was recovered from it.
  # NEWLINE-separated, never word-split: the canonical store path contains a
  # space ("Application Support"). An unquoted loop over it silently checked two
  # non-existent directories and reported the store clean — the same
  # space-truncation class of bug the forensics scanner was just fixed for.
  check_one() {
    [ -d "$1" ] && [ -n "$(ls -A "$1" 2>/dev/null)" ] || return 0
    echo "UNVAULTED — $(ls -1 "$1" 2>/dev/null | wc -l | tr -d ' ') key(s) in plaintext at: $1"
    rc=1
  }
  check_one "$CDSFL_STORE"
  printf '%s\n' $CDSFL_LEGACY_STORES | while IFS= read -r loc; do
    [ -n "$loc" ] && check_one "$loc"
  done
  for loc in $CDSFL_LEGACY_STORES; do
    if [ -d "$loc" ] && [ -n "$(ls -A "$loc" 2>/dev/null)" ]; then rc=1; fi
  done
  # A copy somewhere nobody recorded is the case this is really guarding against.
  known=$(printf '%s\n' "$CDSFL_STORE" $CDSFL_LEGACY_STORES | sed 's/[].[^$*\\/]/\\&/g' | paste -sd'|' -)
  stray=$(find "$HOME" -maxdepth 4 -name '*answer_key*.json' 2>/dev/null \
          | grep -v "Developer_Projects" \
          | grep -Ev "^(${known})/" || true)
  if [ -n "$stray" ]; then
    echo "UNVAULTED — stray plaintext key file(s) outside every known store:"
    echo "$stray" | sed 's/^/    /'
    rc=1
  fi
  if [ "$rc" = "0" ]; then
    echo "VAULTED — no plaintext key file on disk in any known or scanned location."
  else
    echo "  A panel run must not start in this state."
  fi
  if [ -f "$CDSFL_VAULT" ]; then
    echo "  sealed archive present ($(wc -c <"$CDSFL_VAULT" | tr -d ' ') bytes, AES-256, passphrase not on this machine)"
  else
    echo "  NO ARCHIVE"
  fi
  return 0
}

case "${1:-status}" in
  vault)   vault ;;
  unvault) unvault ;;
  status)  status ;;
  run)
    shift
    [ "${1:-}" = "--" ] && shift
    [ "$#" -gt 0 ] || { echo "usage: $0 run -- <command>" >&2; exit 2; }
    unvault
    trap vault EXIT INT TERM
    "$@"
    ;;
  *) echo "usage: $0 {vault|unvault|status|run -- <command>}" >&2; exit 2 ;;
esac
