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
#   bench/vault_keys.sh verify            # prove the seal opens, restores nothing
#   bench/vault_keys.sh register          # what each key IS, no passphrase needed
#   bench/vault_keys.sh status
#   bench/vault_keys.sh run -- <command>   # unvault only for the duration
set -eu
# PIPEFAIL, added 2026-09-07. Without it the seal below had an unrecoverable
# data-loss path, PROVED by execution rather than reasoned about: a pipeline's
# status is its LAST command's, so `tar ... | openssl ... -out "$VAULT"` returns 0
# whenever openssl succeeds, EVEN IF TAR FAILED. `set -e` then does not fire, and
# `rm -rf "$STORE"` runs anyway -- deleting the only plaintext copy of 29 scoring
# keys while the archive holds whatever openssl managed to write. Measured:
# `set -eu` reaches the delete step with exit 0; `set -euo pipefail` aborts first.
set -o pipefail

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
  # FOLD EVERYTHING, AND PROVE IT ARRIVED BEFORE DELETING ANYTHING.
  #
  # THE DEFECT THIS REPLACES, found 2026-09-07 while preparing the founder's own
  # sealing commands. The previous form was:
  #     cp -p "$legacy"/*.json "$STORE"/ 2>/dev/null || true
  #     rm -rf "$legacy"
  # which copies TOP-LEVEL *.json only and then deletes the whole directory.
  # Measured against the real stray store: 31 files present, 1 matched the glob,
  # 30 would have been destroyed -- including all 27 BR2 answer keys, which live
  # in a `br2_keys/` SUBDIRECTORY, and a `_KEY.md` the glob cannot see. The
  # `2>/dev/null || true` meant a total copy failure was silent, and `rm -rf` ran
  # regardless. These keys have no other copy.
  # FED BY REDIRECTION (2026-09-07, panel fable). Unquoted expansion split a store
  # path containing a space into non-existent directories, so its keys were SILENTLY
  # NOT FOLDED at seal time -- left in plaintext while the operator believed they
  # were sealed. Latent today (no current store path has a space) and not latent in
  # principle: the canonical store lives under "Application Support". Same defect
  # class status() was repaired for on 2026-09-06.
  while IFS= read -r legacy; do
    [ -n "$legacy" ] || continue
    [ -d "$legacy" ] || continue
    mkdir -p "$STORE"
    # Recursive, so subdirectories and non-.json key material travel too.
    # COPYFILE_DISABLE stops macOS tar emitting AppleDouble `._` sidecars, which
    # would otherwise double the file count inside the sealed archive.
    ( cd "$legacy" && COPYFILE_DISABLE=1 tar -cf - . ) \
      | ( cd "$STORE" && COPYFILE_DISABLE=1 tar -xf - )
    # Every source file must now exist in the destination with the same bytes.
    _missing=0
    while IFS= read -r rel; do
      if [ ! -f "$STORE/$rel" ] || ! cmp -s "$legacy/$rel" "$STORE/$rel"; then
        echo "  NOT FOLDED: $rel" >&2
        _missing=$((_missing + 1))
      fi
    done <<EOF
$(cd "$legacy" && find . -type f | sed "s|^\./||")
EOF
    if [ "$_missing" -ne 0 ]; then
      echo "REFUSING TO REMOVE $legacy: $_missing file(s) did not fold." >&2
      echo "Nothing has been deleted. The keys are still at $legacy." >&2
      exit 1
    fi
    _n=$(cd "$legacy" && find . -type f | wc -l | tr -d " ")
    rm -rf "$legacy"
    echo "folded legacy store into the vault: $legacy ($_n file(s), all verified)"
  done <<EOF
${CDSFL_LEGACY_STORES:-}
EOF
  if [ ! -d "$STORE" ]; then
    echo "already vaulted (no plaintext store)"; return 0
  fi
  if [ -z "$(ls -A "$STORE" 2>/dev/null)" ]; then
    rmdir "$STORE"; echo "already vaulted (empty store removed)"; return 0
  fi
  echo "Sealing the scoring keys. The passphrase is NOT stored anywhere on this"
  echo "machine — you will be asked for it again to score, and it cannot be"
  echo "recovered if lost. Keep it in your password manager."

  # NEVER OVERWRITE AN EXISTING ARCHIVE. A vault already on disk may hold keys
  # that are not in the current plaintext store; writing straight over it would
  # destroy them with no way back, and the passphrase that opens it is by design
  # not available here to check first. Moved aside, never deleted.
  if [ -f "$VAULT" ]; then
    _prev="$VAULT.prev-$(date -u +%Y%m%dT%H%M%SZ)"
    mv "$VAULT" "$_prev"
    echo "existing archive preserved as: $_prev"
  fi

  # A manifest of NAMES AND HASHES ONLY -- no key content -- so the seal can be
  # verified later, and so a truncated archive is detectable without the
  # passphrase. Filenames are not the secret; the answers inside them are.
  # RECURSIVE, corrected 2026-09-07 (panel, cc2, proved in a sandbox store shaped
  # like the real one). Both lines were TOP-LEVEL ONLY: `ls -1` counts br2_keys/ as
  # ONE key, and `shasum -a 256 *` errors "Is a directory" on it -- an error that
  # 2>/dev/null swallowed and `|| true` cleared. So the manifest omitted 27 of the
  # 31 keys, `verify`'s MANIFEST MISMATCH check compared against that truncated
  # manifest and passed, and `register`'s post-seal branch -- the whole reason the
  # register exists -- described only what the manifest listed. The register's own
  # stated purpose, "a register that omits what is about to be sealed is the
  # failure it exists to prevent", was realised.
  _count=$( cd "$STORE" && find . -type f | wc -l | tr -d " " )
  ( cd "$STORE" && find . -type f -print0 | sort -z | xargs -0 shasum -a 256 ) \
    > "$VAULT.manifest"
  chmod 600 "$VAULT.manifest"

  tar -czf - -C "$(dirname "$STORE")" "$(basename "$STORE")" \
    | openssl enc -aes-256-cbc -pbkdf2 -iter 600000 -salt -out "$VAULT"
  chmod 600 "$VAULT"

  # ONLY NOW may the plaintext go, and only against evidence the archive exists
  # and is not a stub. pipefail above catches a failed tar; this catches a write
  # that produced a file but not an archive.
  _size=$(wc -c <"$VAULT" | tr -d " ")
  if [ ! -s "$VAULT" ] || [ "$_size" -lt 1024 ]; then
    echo "REFUSING TO DELETE THE PLAINTEXT: the archive is $_size bytes, which is" >&2
    echo "too small to hold $_count keys. The store is untouched at $STORE." >&2
    exit 1
  fi
  # THE REGISTER IS WRITTEN BY SEALING, NOT BY REMEMBERING (2026-09-07, panel).
  # fable: seal time is the unique enforcement point -- the only moment a human is
  # guaranteed present while the content is still readable. cc2: do NOT refuse on an
  # unclassified key, because that makes the safe action require a code edit and
  # leaves the plaintext on disk until someone edits a case statement, which is the
  # shape of guard people work around. Both are satisfied by writing the register
  # automatically and making UNCLASSIFIED loud on stderr rather than fatal.
  # `[ test ] && echo` returns 1 when the test is FALSE, and under `set -e` with
  # pipefail that aborted the whole seal -- caught by the round-trip test, which is
  # what it is for. An if/fi cannot return non-zero on the common path.
  _unclassified=0
  while IFS= read -r _f; do
    if [ "$(describe "$(basename "$_f")")" = "UNCLASSIFIED -- describe it here before sealing" ]; then
      _unclassified=$((_unclassified + 1))
    fi
  done <<EOF
$( cd "$STORE" 2>/dev/null && find . -type f 2>/dev/null | sed "s|^\./||" )
EOF
  rm -rf "$STORE"
  echo "sealed: $_count keys, $_size bytes of ciphertext, passphrase not on this machine."
  register
  if [ "${_unclassified:-0}" -gt 0 ]; then
    echo "  $_unclassified key(s) UNCLASSIFIED in the register -- name them in describe() before the next run" >&2
  fi
  echo "VERIFY IT NOW, before you rely on it:  $0 verify"
}

describe() {
  # WHAT EACH KEY RESOURCE IS, readable WITHOUT the passphrase.
  #
  # FOUNDER, 2026-09-07: "Make sure you maintain a record next to these of what all
  # our sealed answer key resources are, both for already completed runs and
  # upcoming tasks/experiments on the runway. Humans sometimes forget passwords.
  # The last thing we need is for you to forget what you have called a thing!"
  #
  # The existing 174112-byte archive is exactly that failure already realised: it
  # was sealed BEFORE the manifest feature existed, so nothing on disk records what
  # is inside it, and the answer keys for the 2 completed exam runs are nowhere
  # loose on the filesystem. Their location is currently unknowable without opening
  # it. That is why `unvault` is no longer optional in the sealing procedure.
  #
  # Names, purposes and hashes only. No answer content ever leaves the archive.
  case "$1" in
    ft-*_KEY.json)                 echo "Bench Run 2 answer key, exam ${1%%_KEY.json}, not yet run" ;;
    control_two_distinct_defects_KEY.md)      echo "Exp 55 control, planted-defect key (prose)" ;;
    control_two_distinct_defects_GROUND_TRUTH.json) echo "Exp 55 control, ground truth" ;;
    canary_catalogue_*.json)       echo "Canary catalogue for a simulated run target" ;;
    manifest_cdsfl_sim.*.json)     echo "Seed manifest, one sandboxed simulated run" ;;
    README.md)                     echo "not a key -- store documentation" ;;
    *)                             echo "UNCLASSIFIED -- describe it here before sealing" ;;
  esac
}

register() {
  # Build the register from whichever source is authoritative right now:
  # the plaintext store if it exists, otherwise the archive's manifest.
  out="$VAULT.register"
  {
    echo "CDSFL sealed-key register"
    echo "Generated $(date -u +%Y-%m-%dT%H:%M:%SZ). Names and purposes only -- no answers."
    echo
    # EVERY location the seal will cover, not just $STORE. The first version read
    # $STORE alone and described NOTHING, because all 36 plaintext files live in
    # LEGACY stores that `vault` folds in at seal time. A register that omits what
    # is about to be sealed is the failure it exists to prevent.
    _any=0
    # FED BY REDIRECTION, NOT BY UNQUOTED EXPANSION (2026-09-07, panel fable).
    # The first version split ${CDSFL_LEGACY_STORES} on whitespace, so a store whose
    # path contains a space was SILENTLY omitted from the register -- and the
    # canonical store path contains one ("Application Support"). This is the exact
    # word-splitting defect status() was repaired for on 2026-09-06, reintroduced
    # the next day in the function beside it. status() established the pattern; this
    # now uses it.
    while IFS= read -r _loc; do
      [ -n "$_loc" ] || continue
      [ -d "$_loc" ] && [ -n "$(ls -A "$_loc" 2>/dev/null)" ] || continue
      _any=1
      echo "SOURCE: plaintext, not yet sealed -- $_loc"
      ( cd "$_loc" && find . -type f | sed "s|^\./||" | sort ) | while IFS= read -r rel; do
        printf '  %-46s %s\n' "$rel" "$(describe "$(basename "$rel")")"
      done
      echo
    done <<EOF
$STORE
${CDSFL_LEGACY_STORES:-}
EOF
    if [ "$_any" = "1" ]; then
      :
    elif [ -f "$VAULT.manifest" ]; then
      echo "SOURCE: the manifest beside the sealed archive"
      echo
      while IFS= read -r line; do
        f=${line#*  }
        printf '  %-46s %s\n' "$f" "$(describe "$(basename "$f")")"
      done < "$VAULT.manifest"
    else
      echo "NEITHER a plaintext store NOR a manifest exists."
      echo "The archive at $VAULT cannot be described without its passphrase."
      echo "Run 'unvault', then 'register', then 'vault' to give it one."
    fi
    echo
    [ -f "$VAULT" ] && echo "Archive: $VAULT ($(wc -c <"$VAULT" | tr -d ' ') bytes, AES-256)"
  } > "$out"
  chmod 600 "$out"
  cp "$out" "$HOME/Desktop/CDSFL_sealed_key_register.txt" 2>/dev/null \
    && echo "register written: $out" \
    && echo "  and mirrored to ~/Desktop/CDSFL_sealed_key_register.txt" \
    || echo "register written: $out (Desktop mirror failed)"
}

verify() {
  # Prove the archive OPENS and holds what was sealed, without ever putting the
  # plaintext back where a model could reach it. Sealing an archive nobody has
  # opened is how a backup turns out to be empty on the day it is needed.
  [ -f "$VAULT" ] || { echo "NO VAULT at $VAULT" >&2; exit 1; }
  _tmp=$(mktemp -d)
  trap 'rm -rf "$_tmp"' EXIT INT TERM
  echo "Enter the passphrase to verify the seal. Nothing is restored to $STORE."
  openssl enc -d -aes-256-cbc -pbkdf2 -iter 600000 -in "$VAULT" \
    | tar -xzf - -C "$_tmp" \
    || { echo "COULD NOT OPEN THE ARCHIVE — wrong passphrase, or it is damaged." >&2
         exit 1; }
  _inner="$_tmp/$(basename "$STORE")"
  _n=$(ls -1 "$_inner" 2>/dev/null | wc -l | tr -d " ")
  echo "opened: $_n file(s)"
  if [ -f "$VAULT.manifest" ]; then
    if ( cd "$_inner" && shasum -a 256 -c "$VAULT.manifest" >/dev/null 2>&1 ); then
      echo "manifest: every file matches its recorded hash"
    else
      echo "MANIFEST MISMATCH — the archive does not hold what was sealed." >&2
      exit 1
    fi
  else
    echo "no manifest beside the archive (sealed before 2026-09-07); count only"
  fi
  echo "VERIFIED. The keys are recoverable with this passphrase."
}

unvault() {
  if [ -d "$STORE" ]; then echo "already unvaulted"; return 0; fi
  [ -f "$VAULT" ] || { echo "NO VAULT at $VAULT" >&2; exit 1; }
  openssl enc -d -aes-256-cbc -pbkdf2 -iter 600000 -in "$VAULT" \
    | tar -xzf - -C "$(dirname "$STORE")" \
    || { echo "could not open the archive — wrong passphrase, or it is damaged" >&2
         rm -rf "$STORE" 2>/dev/null || true; exit 1; }
  chmod 700 "$STORE"; chmod 600 "$STORE"/* 2>/dev/null || true
  # RECURSIVE (2026-09-07). Third instance of the same top-level-only count: this
  # would report "4 keys" after restoring 31, because br2_keys/ counts as one entry.
  echo "unvaulted to $STORE ($(find "$STORE" -type f | wc -l | tr -d ' ') key file(s))"
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
    # COUNTED RECURSIVELY, corrected 2026-09-07. `ls -1 | wc -l` counts top-level
    # ENTRIES, so the store holding 29 keys reported "4" -- 3 files plus the
    # `br2_keys` directory counted once, with its 27 answer keys invisible. An
    # operator reading "4 keys in plaintext" would materially misjudge the
    # exposure he is being warned about.
    echo "UNVAULTED — $(find "$1" -type f 2>/dev/null | wc -l | tr -d ' ') key file(s) in plaintext at: $1"
    rc=1
  }
  check_one "$CDSFL_STORE"
  # `|| true`, and the emptiness guard, added 2026-09-06. Under `set -e` an empty
  # CDSFL_LEGACY_STORES made the final `read` return non-zero and killed the whole
  # script SILENTLY -- no output, exit 1. It failed safe, because
  # arc_sequencer.sh greps for '^VAULTED' and an empty string does not match, but a
  # status command that prints nothing at all is its own hazard: the operator
  # cannot tell "clean" from "crashed".
  # REDIRECTION, NOT A PIPE (panel, 2026-09-06, cc2 + fable). CDSFL_LEGACY_STORES
  # was read 3 ways here, 2 of them word-splitting on unquoted expansion. A legacy
  # store whose path CONTAINS A SPACE was therefore split into 2 non-existent
  # directories, both of which "passed", and the check printed VAULTED with a
  # plaintext key sitting in it -- the exact false all-clear this scan was rewritten
  # to end, reintroduced by the very loop added to work around the first bug.
  #
  # The first bug was that a PIPED `while` runs in a subshell, so `rc=1` set inside
  # it cannot escape. That is why a second, word-splitting `for` loop existed at all.
  # Feeding by redirection keeps the loop in the current shell, so rc survives and
  # the second loop is deleted rather than patched. 10 lines to 5.
  while IFS= read -r loc; do
    [ -n "$loc" ] && check_one "$loc"
  done <<EOF
${CDSFL_LEGACY_STORES:-}
EOF
  # A copy somewhere nobody recorded is the case this is really guarding against.
  # Quoted, and the class widened: an unescaped +?(){}| in a store path would
  # otherwise corrupt the regex that excludes known stores from the stray scan.
  known=$(printf '%s\n' "$CDSFL_STORE" "${CDSFL_LEGACY_STORES:-}" | sed 's/[].[^$*\\\/+?(){}|]/\\&/g' | paste -sd'|' -)
  # PATTERNS AND SCOPE, CORRECTED 2026-09-06 — the previous form reported VAULTED
  # while 29 plaintext answer keys sat on disk, and bench/arc_sequencer.sh:50 gates
  # a whole experiment arc on that line. It was blind twice over:
  #   1. It matched only '*answer_key*.json'. The BR2 keys are named
  #      'ft-NNN_KEY.json' and the exp55 pair are '*_KEY.md' / '*GROUND_TRUTH.json',
  #      so the pattern matched 0 of 29 real keys.
  #   2. It excluded "Developer_Projects" outright — the directory the keys are in.
  #      Measured before removing it: the corrected patterns match 0 files inside
  #      the repository, so the exclusion suppressed only true positives.
  # Depth 5, not 4, because the BR2 keys sit one level deeper (br2_keys/).
  #   3. EXTENDED 2026-09-07. It matched 0 of the 5 files in ~/CDSFL_keys: 2 canary
  #      catalogues and 3 seed manifests, every one of which NAMES the planted
  #      defects. So the scan could print VAULTED with answer-key-class material in
  #      plaintext at mode 644 -- and a simulated run writes one more on every
  #      canary pass. 'manifest_cdsfl_*' rather than 'manifest_*' because the scan
  #      walks $HOME to depth 5 and a bare 'manifest_*.json' would sweep in
  #      unrelated project files.
  stray=$(find "$HOME" -maxdepth 5 \
            \( -name '*answer_key*.json' -o -name '*_KEY.json' \
               -o -name '*_KEY.md' -o -name '*GROUND_TRUTH.json' \
               -o -name '*planted*.json' \
               -o -name '*canary*.json' -o -name 'manifest_cdsfl_*.json' \) 2>/dev/null \
          | grep -v '/\.git/' \
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
  verify)  verify ;;
  register) register ;;
  run)
    shift
    [ "${1:-}" = "--" ] && shift
    [ "$#" -gt 0 ] || { echo "usage: $0 run -- <command>" >&2; exit 2; }
    unvault
    trap vault EXIT INT TERM
    "$@"
    ;;
  *) echo "usage: $0 {vault|unvault|verify|register|status|run -- <command>}" >&2; exit 2 ;;
esac
