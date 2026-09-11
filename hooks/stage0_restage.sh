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
        if git add -- "$_p"; then
            echo "pre-commit: re-staged $_p (stage-0 repair)"
        else
            echo "pre-commit: could not stage $_p; it will lag a commit behind" >&2
        fi
    done
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
    case "$GIT_INDEX_FILE" in
        "$_dir/index"|*/index|index) return 0 ;;
    esac
    echo "pre-commit: this is a pathspec commit (git commit -- <path>), so the" >&2
    echo "            stage-0 repairs below are staged into git's TEMPORARY" >&2
    echo "            index. They WILL land in this commit even though they are" >&2
    echo "            outside the pathspec, and 'git status' will read MM after." >&2
}
