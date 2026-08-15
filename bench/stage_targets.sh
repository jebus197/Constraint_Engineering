#!/bin/bash
# Stage review targets OUTSIDE the repository, READ-ONLY, ONE PER DIRECTORY.
#
# Four properties this enforces, each learned from a confirmed failure:
#
#  1. A frozen target must actually be frozen. Panel models hold Bash for the
#     falsifier loop, and Bash writes by redirection, so removing Write/Edit is
#     not sufficient. Mode 444 makes mutation fail at the filesystem.
#     (Exp 47, 2026-07-29: the target was edited on disk and restored inside two
#     minutes, leaving no trace in git or the round files.)
#
#  2. The scoring key must not be reachable from where the panel stands. The
#     staged tree holds modules only — no key, no git history, no sibling
#     metadata. (Keys co-located with targets were findable by a single ls.)
#
#  3. One document per directory. A shared staging directory let a single ls
#     enumerate every exam in the series, including ones not yet sat: the
#     filenames announced the experiment numbers, the subject ladder, and the
#     existence of a series. The panel's working directory now contains exactly
#     the document under review.
#
#  4. THE DIRECTORY NAME IS STABLE ("current"); the FILE keeps the document's own
#     ID. Staging under the Document ID gave a different directory every leg, and
#     the Claude CLI evaluates workspace trust per directory — so CC2 died on the
#     first launch of the control with "this workspace has not been trusted", and
#     no amount of trusting could have kept up with a name that changes each time.
#     A fixed directory needs accepting once. Every property that matters is kept:
#     one document, nothing beside it, a neutral name inside and out.
#
#  5. ONE DOCUMENT STAGED AT A TIME. Per-directory staging stops `ls` inside the
#     panel's own directory, but every target shared one parent, so `ls ..`
#     enumerated the whole series and `cat ../*/*.md` read every sibling exam —
#     including papers not yet sat. That is exactly the mechanism the cross-target
#     count prior needs, and the mechanism a panel would use to compare the
#     zero-plant control against a seeded sibling. Staging now CLEARS the root
#     first, so the parent holds precisely the document under review.
#
#  5. Names carry no experiment metadata. Each document is staged under its own
#     internal Document ID (PR-14-REF-02, SW-21-REF-04, ...), read from the file
#     itself, so nothing in the path says "exp52", "factorial" or "control".
#     A control document whose filename names it as the control is not a control.
#
# Usage: bench/stage_targets.sh [module.md ...]   (default: all modules)
# Prints, per module, the test_article and panel_cwd values its config must carry.
set -eu

# Target location comes from the same off-repo config the keys use.
CONF="${CDSFL_SCORING_CONF:-$HOME/.config/cdsfl/scoring.env}"
[ -r "$CONF" ] || { echo "missing scoring config: $CONF" >&2; exit 1; }
# shellcheck source=/dev/null
. "$CONF"

# Targets live WITH the scoring keys, outside the repository. A target kept under
# version control leaks itself: repairing a seeded claim touches only seeded
# claims, so a diff returns the planted set at precision 1.000 — no key needed and
# nothing for a detector to see. The repo keeps hashes only (targets/MANIFEST.md).
SRC="${CDSFL_TARGETS:?scoring config did not define CDSFL_TARGETS}"
STAGE=~/CDSFL_review_targets

mkdir -p "$STAGE"
chmod u+w "$STAGE" 2>/dev/null || true

if [ "$#" -eq 0 ]; then
  echo "usage: $0 <module.md> [module.md ...]" >&2
  echo "  Refusing to stage every module at once: a shared parent lets one leg" >&2
  echo "  enumerate and read the whole exam series with 'ls ..'." >&2
  exit 2
fi

# Clear the root. Anything already staged is a sibling the current leg must not
# be able to see. Targets are regenerable from the repository, so nothing is lost.
if [ -d "$STAGE" ]; then
  find "$STAGE" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null \
    | while IFS= read -r -d "" old; do
        chmod -R u+w "$old" 2>/dev/null || true
        rm -rf "$old"
      done
fi

staged=0
for f in "$@"; do
  case "$f" in
    /*) : ;;
    *) f="$SRC/$f" ;;
  esac
  [ -e "$f" ] || { echo "  MISSING: $f" >&2; exit 1; }

  # The document names itself. No mapping table to drift out of step with the
  # modules, and no experiment number anywhere in the staged path.
  docid=$(grep -m1 -E '^\*\*Document ID:\*\*' "$f" \
          | sed -E 's/.*\*\*Document ID:\*\*[[:space:]]*//' | tr -d '[:space:]')
  if [ -z "$docid" ]; then
    echo "  NO DOCUMENT ID in $f — refusing to stage under its repo filename" >&2
    exit 1
  fi

  d="$STAGE/current"
  chmod u+w "$d" 2>/dev/null || true
  chmod u+w "$d/$docid.md" 2>/dev/null || true
  mkdir -p "$d"
  cp "$f" "$d/$docid.md"
  chmod 444 "$d/$docid.md"   # writes fail; they do not silently succeed
  chmod 555 "$d"             # and no new files may appear alongside it
  staged=$((staged + 1))
  echo "  $docid  <- $(basename "$f")"
  echo "      test_article: $d/$docid.md"
  echo "      panel_cwd   : $d"
done

echo "staged $staged module(s), read-only, one per directory under $STAGE"
