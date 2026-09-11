# CDSFL stage-0 re-staging helper.  POSIX sh.  Sourced by hooks/pre-commit.
#
# WHY THIS FILE EXISTS AT ALL, with the measurement rather than the intention.
#
# On 2026-09-11 task A2's DONE claim -- "a fresh clone is green" -- was re-checked
# by actually cloning HEAD and running the suite there.  It was not green:
#
#     3 failed, 6952 passed, 38 skipped, 1 xfailed in 1478.12s
#     FAILED bench/tests/test_citation_content_2026-09-10.py
#     FAILED bench/tests/test_experiment_run_ledger_2026-08-26.py
#     FAILED bench/tests/test_measurement_survey_is_safe_2026-09-11.py
#
# The same suite in the maintainer's working tree was 6988 passed, 0 failed.
#
# THE CAUSE.  A pre-commit hook sees the STAGED snapshot.  Stage 0's repairs --
# the run-ledger refresh and the citation-content repair -- write to the WORKING
# TREE and did not `git add` what they wrote.  So every commit shipped the
# UNREPAIRED content, the repair sat uncommitted, and the NEXT commit swept it
# in.  The repairs were permanently 1 commit behind.  A clone at HEAD was
# therefore broken while `git status` in the maintainer's tree said nothing at
# all, which is why 2 days of commits passed without anyone seeing it.
#
# Confirmed immediately after the previous commit, with the ledger's own figure
# agreeing between the generator and the working-tree file at 14904 while
# `git diff HEAD` still reported the ledger modified -- the repair had run, and
# had not reached the commit.
#
# WHY A SEPARATE FILE RATHER THAN 6 MORE LINES IN THE HOOK.  `execute-do-not-grep`:
# a test that reads the hook's text proves only that the hook describes itself
# consistently.  The logic lives here once, the hook SOURCES it, and
# bench/tests/test_precommit_restages_repairs_2026-09-11.py sources THE SAME FILE
# and runs it against a real git index.  There is 1 representation, and the test
# executes it.
#
# WHAT IS DELIBERATELY NOT DONE: `git add -A`.  Only the exact paths a repair
# REPORTS having changed are staged, so an unrelated work-in-progress edit is
# never swept into a commit.  Anything a repair does not name, this does not
# touch.

# Stage each path named on stdin, 1 per line.  Never fails the commit: a path
# that has vanished or that git refuses is reported and skipped, because stage 0
# is non-blocking by design and a convenience repair must not be able to stop
# work.  The MISSING-file check in the hook is what refuses; this is not.
cdsfl_restage_paths() {
    while IFS= read -r _p; do
        [ -n "$_p" ] || continue
        if [ ! -f "$_p" ]; then
            echo "pre-commit: repair named $_p, which is not a file; not staged" >&2
            continue
        fi
        if cdsfl_is_partially_staged "$_p"; then
            cdsfl_stage_repair_delta "$_p"
            _rc=$?
            if [ "$_rc" -eq 0 ]; then
                echo "pre-commit: staged only the repair's delta in $_p"
                echo "            (it was partially staged; your withheld hunks" \
                     "are untouched)"
            elif [ "$_rc" -eq 2 ]; then
                :   # nothing changed, so nothing to stage and nothing to say
            else
                echo "pre-commit: $_p is partially staged AND the repair collides" >&2
                echo "            with a hunk you left out. NOT staged: staging it" >&2
                echo "            would commit work you withheld. The repair is in" >&2
                echo "            your working tree and will lag 1 commit behind." >&2
                echo "            Stage it yourself, or: git commit --no-verify" >&2
            fi
            continue
        fi
        if git add -- "$_p"; then
            echo "pre-commit: re-staged $_p (stage-0 repair)"
        else
            echo "pre-commit: could not stage $_p; it will lag a commit behind" >&2
        fi
    done
}

# PARTIAL STAGING: the one case where re-staging costs something.
#
# `git add -- <path>` stages the WHOLE file. If the author had staged part of a
# file with `git add -p` and deliberately left the rest out, a repair to that
# file sweeps the rest into the commit. The master task list is repaired by the
# citation guard AND is edited constantly, so this is not hypothetical.
#
# WHY IT STILL STAGES. The alternative is the defect this file exists to fix:
# the commit ships the unrepaired content and a clone at HEAD is broken. Between
# "an extra hunk lands, visibly, with a line saying so" and "every clone is
# broken, silently, for 2 days", the first is the lesser cost -- but it is a
# cost, so it is announced rather than absorbed.
#
# Surgical staging -- splicing only the repaired line into the index blob -- was
# considered and rejected: it means building a tree object by hand inside a
# shell hook, and a subtle bug there writes a WRONG blob, which is worse than an
# extra hunk that the author can see in the diff.
cdsfl_is_partially_staged() {
    git diff --cached --quiet -- "$1" && return 1   # nothing staged for it
    git diff --quiet -- "$1" && return 1            # nothing unstaged for it
    return 0
}

# SNAPSHOT BEFORE ANY REPAIR WRITES. Called once from hooks/pre-commit, ahead of
# the repair blocks. Normally copies nothing: 2 git calls and an empty set.
#
# Only PARTIALLY STAGED paths are copied, because those are the only ones where
# `git add` would take something the author withheld. Everything else keeps the
# plain `git add` path, unchanged.
CDSFL_SNAP=""
cdsfl_snapshot_partially_staged() {
    # `-z`, AND THE READS ARE LINE-WISE. Two defects were fixed here in
    # succession, both in code written to be careful.
    #
    # 1. The first version intersected the lists with `comm -12 - <(...)`.
    #    Process substitution is a bashism; this file is sourced by a
    #    `#!/bin/sh` hook and `sh -n` accepted it only because /bin/sh is bash
    #    in POSIX mode here. Under dash it is a syntax error, so the hook would
    #    fail to parse and every commit on a Debian-like system would be refused
    #    by the guard meant to protect it.
    #
    # 2. Its POSIX replacement used `for _b in $_both`, which WORD-SPLITS. A
    #    path containing a space became several words, matched nothing, and was
    #    never snapshotted -- so the delta path could not run and the file took
    #    the collision branch, printing "the repair collides with a hunk you
    #    left out" when nothing had collided. Measured on
    #    `A Note With Spaces.md`: index unchanged, repair not staged. It fails
    #    SAFE -- nothing is swept and nothing is corrupted -- but the repair
    #    lags a commit behind and the message is false.
    #
    # `--name-only -z` also stops git quoting unusual paths as `"caf\303\251.md"`,
    # which the unquoted form would have mangled. A path containing a NEWLINE is
    # still not handled; git can express one and this cannot, and saying so is
    # better than implying coverage.
    _both=$(git diff --cached --name-only -z 2>/dev/null | tr '\0' '\n')
    [ -n "$_both" ] || return 0
    _unstaged=$(git diff --name-only -z 2>/dev/null | tr '\0' '\n')
    [ -n "$_unstaged" ] || return 0
    _paths=$(
        printf '%s\n' "$_both" | while IFS= read -r _b; do
            [ -n "$_b" ] || continue
            printf '%s\n' "$_unstaged" | while IFS= read -r _u; do
                [ "$_b" = "$_u" ] && printf '%s\n' "$_b"
            done
        done
    )
    [ -n "$_paths" ] || return 0
    CDSFL_SNAP=$(mktemp -d "${TMPDIR:-/tmp}/cdsfl_stage0_snap.XXXXXX") || { CDSFL_SNAP=""; return 0; }
    printf '%s\n' "$_paths" | while IFS= read -r _p; do
        [ -n "$_p" ] && [ -f "$_p" ] || continue
        mkdir -p "$CDSFL_SNAP/$(dirname "$_p")"
        cp "$_p" "$CDSFL_SNAP/$_p"
    done
}

cdsfl_snapshot_cleanup() {
    [ -n "${CDSFL_SNAP:-}" ] && [ -d "$CDSFL_SNAP" ] && rm -rf "$CDSFL_SNAP"
    CDSFL_SNAP=""
}

# STAGE ONLY THE REPAIR'S DELTA into a partially staged file.
#
# `git add -- <path>` stages the WHOLE file, so a file the author staged with
# `git add -p` loses its withheld hunks to the next commit the moment a repair
# touches it. Both panel seats found this on 2026-09-11 and each built a fix;
# they disagreed on the mechanism, and the disagreement was settled by
# measurement rather than by argument. Repair at a varying distance from the
# author's unstaged hunk, 8-line file, real index:
#
#     gap  3-way `git merge-file`   zero-context `git apply --cached`
#      0   CONFLICT                 FAILED            (same line -- no answer)
#      1   CONFLICT                 OK, WIP excluded
#      2   OK                       OK
#      3   OK                       OK
#
# Zero-context apply succeeds everywhere merge-file does AND at gap 1, which is
# the common geometry: a citation repair 1 line from an edit in progress. That
# is a committed measurement showing one mechanism dominates on a named
# property, which is what choosing between them requires.
#
# At gap 0 BOTH refuse, correctly: the repair and the withheld hunk touch the
# same line and there is no right answer without asking. The caller then
# reports a lag rather than staging, because a visible 1-commit lag is better
# than an irreversible commit of content nobody reviewed.
#
# RETURN CODES, and the 3rd was added after a P-pass on this very function.
#   0  the repair's delta was staged
#   1  the delta could not be applied -- the caller REPORTS a collision
#   2  there was no delta: the repair reported a path it did not change
#
# There were 2 codes at first, and an empty patch returned 1. So a repair that
# reported a path without changing it made the hook print "the repair collides
# with a hunk you left out", which is false on every count -- nothing collided
# and nothing needed staging. A guard that cries wolf on the ordinary case is
# the same decay path as one that cannot fire.
cdsfl_stage_repair_delta() {
    _p=$1
    [ -n "${CDSFL_SNAP:-}" ] || return 1
    _before="$CDSFL_SNAP/$_p"
    [ -f "$_before" ] || return 1
    _patch="$CDSFL_SNAP/.delta.patch"
    # `git diff --no-index` exits 1 when the files differ, which is the ordinary
    # case here, so its status says nothing about success.
    git diff --no-index -U0 -- "$_before" "$_p" 2>/dev/null | awk -v p="$_p" '
        /^diff --git / { print "diff --git a/" p " b/" p; next }
        /^--- /        { print "--- a/" p; next }
        /^\+\+\+ /      { print "+++ b/" p; next }
        { print }
    ' > "$_patch"
    [ -s "$_patch" ] || return 2
    git apply --cached --unidiff-zero "$_patch" 2>/dev/null
}

# `scripts/experiment_run_ledger.py --refresh` prints, on success and only then:
#     "  refreshed experimental_notes/EXPERIMENT_RUN_LEDGER.md"
# Its decline path prints "  ledger NOT refreshed: ..." and names no path, so it
# cannot match.  The 2-space prefix is part of the format, not decoration.
cdsfl_restage_from_ledger_output() {
    sed -n 's/^  refreshed \(.*\)$/\1/p' | cdsfl_restage_paths
}

# `scripts/citation_content_guard_2026-09-10.py --fix` prints 1 line per repair:
#     "  experimental_notes/Note.md: 11354 -> 11456  (`symbol`)"
# The pattern is anchored on that exact shape -- 2 spaces, a path, a colon, a
# space, a line number, an arrow -- rather than on "contains ->", so the guard's
# REPORT mode cannot feed it.  Its report lines either carry 4 leading spaces
# ("    note.md:11 names `x`, which spans ...") or carry no arrow at all
# ("  23/127 = 18.1102%  Wilson [...]"), and neither matches.  `\(.*\)` rather
# than `\([^ :]*\)` so a path containing a space still resolves.
cdsfl_restage_from_citation_output() {
    sed -n 's/^  \(.*\): [0-9][0-9]* -> [0-9].*$/\1/p' | cdsfl_restage_paths
}

# A PATHSPEC COMMIT (`git commit -- some/path`) builds a TEMPORARY index, and
# git sets GIT_INDEX_FILE to it for the hook's lifetime.  Measured 2026-09-11 in
# a scratch repository: the hook's `git add` DOES reach that commit, so the
# repair still lands -- but a file the author deliberately excluded from the
# pathspec is committed with it, and the real index is left reporting `MM`
# afterwards.  That is surprising enough to be worth saying out loud.  It is a
# notice, never a refusal: the alternative is the defect this file exists to fix.
cdsfl_warn_if_partial_commit() {
    [ -n "${GIT_INDEX_FILE:-}" ] || return 0
    # NOT `git rev-parse --git-path index`.  That command RETURNS $GIT_INDEX_FILE
    # verbatim when the variable is set, so the comparison below would be the
    # variable against itself and the notice could never fire -- a check that
    # cannot fail, which is the shape this project keeps catching.  The first
    # version of this function had exactly that bug and the test caught it:
    # sh -x showed _real resolving to the fake lock path that had just been
    # exported.  `--absolute-git-dir` does not consult GIT_INDEX_FILE.
    _dir=$(git rev-parse --absolute-git-dir 2>/dev/null) || return 0
    # `index.lock` IS THE REAL INDEX. Both panel seats found this independently
    # on 2026-09-11 and it was reproduced here from a live hook, git 2.50.1:
    #
    #     git commit           .git/index                     real index
    #     git commit --amend   .git/index                     real index
    #     git commit -a        <gitdir>/index.lock            real index
    #     git commit -- <path> <gitdir>/next-index-<pid>.lock  TEMPORARY
    #
    # Without the `index.lock` escape, EVERY `git commit -am` in this repository
    # was told "this is a pathspec commit" and that files outside the pathspec
    # would land -- both false, on the commonest commit command there is. The
    # first version of this function could never fire; this one fired when it
    # must not. A notice that is wrong on the ordinary case stops being read,
    # which is a guard that cannot fail in mirror image.
    #
    # The discriminator is the basename: git names the final index `index`, its
    # lock `index.lock`, and a genuinely temporary index `next-index-<pid>`.
    case "$GIT_INDEX_FILE" in
        "$_dir/index"|*/index|index) return 0 ;;
        "$_dir/index.lock"|*/index.lock|index.lock) return 0 ;;
    esac
    echo "pre-commit: this is a pathspec commit (git commit -- <path>), so the" >&2
    echo "            stage-0 repairs below are staged into git's TEMPORARY" >&2
    echo "            index. They WILL land in this commit even though they are" >&2
    echo "            outside the pathspec, and 'git status' will read MM after." >&2
}
