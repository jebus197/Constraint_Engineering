"""A write that leaves the scratch tree must not classify "transient".

PANEL SEAT B FINDING, 2026-09-28, against the literal-leading-prefix rule added
to `hooks/ffafp_audit.py:classify_path` on 2026-09-24. That rule decided
transience by where a path STARTS, and the start does not bind where the write
LANDS. Measured against the real module before the repair, every one of these
returned "transient" -- the one verdict that EXCUSES a write, removing it from
the mutation set entirely in all three consumers:

  /tmp/../<repo>/hooks/evil.py          a literal `..` segment
  /tmp/${V:-../../repo}/hooks/evil.py   a default-value expansion that is not an
                                        assignment, so `shell_assignments`
                                        cannot see it, yet the real shell
                                        honours it -- the landing point is
                                        deterministic for the writer and
                                        unknowable to the parser
  /tmp/$V/hooks/evil.py                 V knowable from neither the command nor
                                        the hook's inherited environment
  /tmp/$(echo ..)/repo/evil.py          `$(` and a backtick never matched the
                                        residual clause's `\\$\\{?\\w+` at all

A SECOND, INDEPENDENT ESCAPE is closed here too: a variable AT OR AFTER the
extension, `> bench/panel_sandbox.py$NOPE`. The 2026-09-24 clause required the
extension to be literal, and `os.path.splitext` returns `.py$nope`, so the
clause declined and the path fell to "unresolved", which every consumer also
excludes. An UNSET shell variable expands to the EMPTY STRING, so that write
landed exactly on `bench/panel_sandbox.py`.

WHERE THIS MODULE DEPARTS FROM THE SEAT'S OWN PATCH, AND WHY. The seat's repair
granted transience only when the remainder held no `..` at all, then fell
through to the extension rules. That over-accuses: `/tmp/a/../b.py` normalises
back INTO /tmp and is genuinely scratch. Executed 2026-09-28, the write lands on
/private/tmp/b.py. Three shapes were measured misclassified "code" by that
patch -- `/tmp/a/../b.py`, `/tmp/../tmp/x.py`, `/private/tmp/../tmp/x.py`. A
false accusation is not the harmless direction in this gate: it is what parked
the previous Stop hook within a day on 2026-09-11 and what produced this gate's
first real bounce on 2026-09-24. This module therefore re-tests the NORMALISED
path with the SAME predicate, which is exact for the literal case.

HOW THIS FILE AVOIDS THE DEFECT SHAPE THAT SHIPPED FIVE TIMES TODAY -- a test
that RE-DERIVES a value the code owns instead of EXTRACTING it. The scratch
locations are read out of `_transient_prefix.__code__.co_consts`, and the
extension classes out of `_CODE_EXT` and `_DOC_EXT`. Nothing below re-lists
`/tmp/` or `.py`. Add a sixth scratch location to the module and its escape is
covered here automatically; delete one and the extraction shrinks with it. Every
verdict is obtained by CALLING the module, and the two shell-semantics premises
the finding rests on are obtained by running a real shell.
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / "hooks" / "ffafp_audit.py"


@pytest.fixture(scope="module")
def fa():
    spec = importlib.util.spec_from_file_location("ffafp_audit_escape_2026_09_28", HOOK)
    m = importlib.util.module_from_spec(spec)
    sys.modules["ffafp_audit_escape_2026_09_28"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def scratch(fa):
    """The scratch locations THE MODULE ITSELF names, read from its own
    `SCRATCH_MARKERS`. Not a second list maintained alongside the first.

    An earlier draft of this fixture read the literals out of
    `_transient_prefix.__code__.co_consts`. Mutating the predicate to build the
    same strings by concatenation showed why that was wrong: CPython folds the
    concatenation, so the extraction kept working but returned the markers in a
    DIFFERENT ORDER, and the executed test below -- which took `scratch[0]` --
    then tried to write under a directory that does not exist on this machine
    and failed for a reason unrelated to the classifier. Reading a named module
    constant is the supported contract; reading bytecode was reverse engineering
    that happened to work.

    `SCRATCH_MARKERS` is the tuple the RULE itself iterates, not an alias over
    it. A draft in which it was an alias was mutated to drop 3 entries: the rule
    kept them, this guard lost them, and all 13 cases stayed green. One tuple
    read by both removes that possibility instead of asserting against it.
    """
    markers = [mk for mk, _anywhere in fa.SCRATCH_MARKERS]
    assert markers, (
        "SCRATCH_MARKERS is empty, so every case below would be vacuous"
    )
    for mk in markers:
        assert fa._transient_prefix(mk + "keep.log"), (
            f"{mk!r} is named in SCRATCH_MARKERS but _transient_prefix rejects "
            "it; the contract the guard reads and the rule the hook runs have "
            "diverged"
        )
    return markers


@pytest.fixture(scope="module")
def real_scratch(scratch):
    """A named scratch location that EXISTS here, for the executed shell tests.

    Chosen by asking the filesystem, not by assuming a position in the list: a
    marker like `/scratchpad/` is a mid-path marker with no real directory of
    its own, and taking it by index made an earlier draft fail in bash rather
    than in the classifier.
    """
    for mk in scratch:
        if os.path.isdir(mk) and os.access(mk, os.W_OK):
            return mk
    pytest.skip(f"none of {scratch} is a writable directory on this machine")


def _code_ext(fa):
    return sorted(fa._CODE_EXT)


def _doc_ext(fa):
    return sorted(fa._DOC_EXT)


# ── the escapes ──────────────────────────────────────────────────────────────

def test_a_literal_traversal_out_of_every_scratch_location_is_judged_by_extension(fa, scratch):
    """Leaving the tree forfeits the excuse; the kind is still knowable."""
    for mk in scratch:
        for ext in _code_ext(fa):
            p = mk + "../" * 6 + "Users/g/proj/hooks/evil" + ext
            assert fa.classify_path(p) == "code", (p, fa.classify_path(p))
        for ext in _doc_ext(fa):
            p = mk + "../" * 6 + "Users/g/proj/NOTES" + ext
            assert fa.classify_path(p) == "doc", (p, fa.classify_path(p))


def test_a_dynamic_remainder_under_a_scratch_head_is_unresolved_never_transient(fa, scratch):
    """An unquoted expansion's value may itself contain `/` and `..`, so no
    dynamic element after a scratch head can be shown harmless."""
    forms = ["$V", "${V:-../../repo}", "${V}", "$(echo ..)", "`cat d`"]
    for mk in scratch:
        for form in forms:
            p = mk + form + "/hooks/evil.py"
            assert fa.classify_path(p) == "unresolved", (p, fa.classify_path(p))


def test_a_variable_at_or_after_the_extension_no_longer_hides_a_write(fa):
    for ext in _code_ext(fa):
        assert fa.classify_path("bench/panel_sandbox" + ext + "$NOPE") == "code", ext
        assert fa.classify_path("bench/panel_sandbox" + ext + "${NOPE}") == "code", ext
    for ext in _doc_ext(fa):
        assert fa.classify_path("experimental_notes/NOTE" + ext + "$NOPE") == "doc", ext
    # Extensionless but under a literal directory: still a change worth noting.
    assert fa.classify_path("hooks/pre-commit$NOPE") == "other"
    # No literal directory at all -- the location is genuinely unknown.
    assert fa.classify_path("x.py$Z") == "unresolved"


# ── anti-vacuity: nothing legitimate is reclassified ─────────────────────────

def test_a_traversal_that_returns_into_the_same_scratch_tree_stays_transient(fa, scratch):
    """THE ASSERTION THAT DISCRIMINATES THIS FIX FROM THE SEAT'S.

    A `/../` string test cannot pass this: the path contains `..` yet normalises
    back inside the tree, and the write really does land there.
    """
    for mk in scratch:
        for tail in ("sub/../keep.py", "./keep.py", "a/b/../../keep.py", "sub//keep.py"):
            p = mk + tail
            assert fa.classify_path(p) == "transient", (p, fa.classify_path(p))


def test_plain_scratch_writes_keep_their_verdict(fa, scratch):
    for mk in scratch:
        assert fa.classify_path(mk + "run.log") == "transient"
        assert fa.classify_path(mk + "x/out.json") == "transient"
        assert fa.classify_path(mk + "deep/nested/stdout.txt") == "transient"


def test_the_2026_09_24_head_and_extension_rule_is_unchanged(fa):
    assert fa.classify_path("bench/targets/exp$n.py") == "code"
    assert fa.classify_path("bench/logs/run_$STAMP/BRIEF.md") == "doc"
    assert fa.classify_path("$WORK/x.py") == "unresolved"
    assert fa.classify_path("$NEVER_SET_ANYWHERE_XYZ/file.py") == "unresolved"


def test_the_2026_09_24_bounce_fix_is_unchanged(fa):
    """`classify_write` RESOLVES from the command first, so a scratchpad file
    named through `$SP` is still excused by evidence rather than by guess."""
    got = fa.classify_write("$SP/gate_in.json",
                            "SP=/tmp/claude/scratchpad; echo hi > $SP/gate_in.json")
    assert got == "transient", got
    got = fa.classify_write("$REPO/bench/reference_runner_v3.py",
                            "REPO=/Users/x/proj; echo hi > $REPO/bench/reference_runner_v3.py")
    assert got == "code", got


def test_resolution_beats_the_scratch_head_rule_end_to_end(fa):
    """Through `bash_mutations`, the shape of the 2026-09-24 first real bounce."""
    muts = fa.bash_mutations("SP=/tmp/claude/scratchpad; echo hi > $SP/gate_in.json")
    assert muts == ["/tmp/claude/scratchpad/gate_in.json"], muts
    assert fa.classify_path(muts[0]) == "transient"


def test_the_consumers_still_drop_scratch_and_still_count_an_escape(fa):
    """The verdict has to reach the signal accumulator, not just be returned."""
    turn = fa.new_turn() if hasattr(fa, "new_turn") else None
    if turn is None:  # accumulator built by a differently named factory
        pytest.skip("no turn factory exposed")
    fa.record_tool(turn, "Write", {"file_path": "/tmp/scratch/run.log"})
    assert turn["mutations"] == [], turn["mutations"]
    escape = "/tmp/../Users/g/proj/hooks/evil.py"
    fa.record_tool(turn, "Write", {"file_path": escape})
    assert turn["mutations"] == [escape], turn["mutations"]


# ── the two shell premises, executed rather than asserted ────────────────────

def test_the_traversal_write_really_lands_inside_the_target_tree(fa, tmp_path, real_scratch):
    """EXECUTED. If this ever fails the finding's premise is gone, not the fix."""
    (tmp_path / "repo" / "hooks").mkdir(parents=True)
    target = str(tmp_path / "repo")
    # /tmp is a symlink to private/tmp on macOS, so step up past the root -- the
    # kernel clamps `..` at / -- and re-enter by absolute path.
    written = real_scratch + "../" * 12 + target.lstrip("/") + "/hooks/evil.py"
    subprocess.run(["bash", "-c", "echo x > " + written], check=True)
    landed = tmp_path / "repo" / "hooks" / "evil.py"
    assert landed.is_file(), f"premise gone: {written} no longer lands in the tree"
    assert fa.classify_path(written) == "code", fa.classify_path(written)


def test_an_unset_variable_expands_empty_so_the_write_lands_on_the_prefix(fa, tmp_path):
    """EXECUTED. The premise under the trailing-variable half of the fix."""
    r = subprocess.run(["bash", "-c", "echo INJECTED > victim.py$NOPE_VAR_2026_09_28"],
                       cwd=tmp_path, capture_output=True)
    assert r.returncode == 0, r.stderr
    assert (tmp_path / "victim.py").is_file(), "unset variable did not expand empty"
    assert fa.classify_path("bench/victim.py$NOPE_VAR_2026_09_28") == "code"


def test_a_non_escaping_traversal_really_lands_back_in_the_scratch_tree(fa, tmp_path):
    """EXECUTED. The premise under the anti-vacuity assertion above: this is why
    accusing `/tmp/a/../b.py` would be a FALSE accusation."""
    sub = tmp_path / "a"
    sub.mkdir()
    written = str(sub) + "/../b.py"
    subprocess.run(["bash", "-c", "echo x > " + written], check=True)
    assert (tmp_path / "b.py").is_file(), written
    assert os.path.realpath(written) == os.path.realpath(str(tmp_path / "b.py"))


# ── where the seat's two attempts disagreed with each other ──────────────────

def test_a_variable_in_a_scratch_basename_is_unresolved_not_transient(fa, scratch):
    """THE SEAT CONTRADICTED ITSELF HERE and this module follows the sound half.

    Its attempt-1 test asserted `/tmp/out_$N.log` -> "transient"; its attempt-2
    patch returns "unresolved" for the same path. "unresolved" is the sound
    verdict: `$N` may expand to `../../etc/pwned`, so the landing point is not
    knowable. The choice is free of downstream cost because all three consumers
    exclude "transient" and "unresolved" alike, so no write changes status --
    only the honesty of the label does.
    """
    for mk in scratch:
        assert fa.classify_path(mk + "out_$N.log") == "unresolved"


def test_the_marker_set_still_covers_the_temp_dir_this_machine_reports(fa):
    """The one drift a data-driven guard cannot see is a DELETION from the set it
    reads, so anchor the set to a location obtained from the operating system.

    `tempfile.gettempdir()` honours TMPDIR, which on macOS is the per-session
    /var/folders/... directory and on Linux is normally /tmp. Either way it is
    where this project's own runs put their logs, so it must classify transient.
    """
    import tempfile
    td = tempfile.gettempdir().lower().rstrip("/") + "/"
    assert fa._transient_prefix(td + "run.log"), (
        f"the OS reports {td} as the temp dir but SCRATCH_MARKERS no longer "
        "covers it; a marker was deleted from the set"
    )
    assert fa.classify_path(td + "exp55.py") == "transient", td


# ── the live-corpus measurement, pinned as executing assertions ───────────────

#: THE REAL WRITES WHOSE VERDICT THIS REPAIR CHANGES, taken from the live
#: transcript corpus rather than invented: 6 transcripts, 270.8 MB, 8,261
#: mutation targets, walked on 2026-09-28 through `scan`'s own `on_tool` hook.
#: 13 of the 8,261 change verdict and no write moves the other way. Re-derive the
#: class totals any time with the committed
#: `scripts/ffafp_unresolved_evasion_2026-09-24.py`, which reads the repository
#: copy of this hook: transient 1381 -> 1372, unresolved 56 -> 60, other 523 ->
#: 527, code 4079 -> 4080.
#:
#: Rates, Wilson 95%, agreed by SymPy solving the interval symbolically and by
#: statsmodels.proportion_confint independently:
#:   9 of the 1381 previously-excused writes were not soundly excusable
#:     -- 0.65%, [0.34%, 1.23%]
#:   4 of the 56 previously-undecidable writes are now counted as work
#:     -- 7.14%, [2.81%, 16.98%]
#:   5 of all 8261 mutation targets newly ENTER the mutation set
#:     -- 0.061%, [0.026%, 0.142%]
#:
#: HONEST PROVENANCE OF THE ONE `code` CASE. The single transient -> code entry,
#: `/tmp/../repo/hooks/evil.py`, is the probe typed while confirming this fault
#: on 2026-09-28, which the live corpus then recorded. So the traversal escape
#: has NO observed historical exploitation in this corpus: it was a latent hole,
#: not an exploited one. The 4 recoveries below are different -- they are
#: ordinary repository writes, made in earnest, that the audit could not see.
CORPUS_VERDICT_CHANGES = (
    # (path, verdict before 2026-09-28, verdict after)
    ("/tmp/../repo/hooks/evil.py", "transient", "code"),
    ("bench/cdsfl_registry/targets/.cleared_exp$n", "unresolved", "other"),
    ("bench/tests/$b", "unresolved", "other"),
    ("bench/$F", "unresolved", "other"),
    ("bench/tools/wolfram_gate/deny/$name", "unresolved", "other"),
    ("/tmp/supersede_test/R_$c.md", "transient", "unresolved"),
    ("/tmp/tl_$c.md", "transient", "unresolved"),
    ("/private/tmp/claude-501/-Users-georgejackson-Developer-Projects/"
     "6142171c-97c7-4e77-9a9a-8d36d795bb89/scratchpad/$f.txt", "transient", "unresolved"),
    ("/private/tmp/claude-501/-Users-georgejackson-Developer-Projects/"
     "a07b3790-0a2a-4978-aedb-bd842c0493d3/scratchpad/tr_$2.jsonl", "transient", "unresolved"),
    ("/private/tmp/claude-501/-Users-georgejackson-Developer-Projects/"
     "a07b3790-0a2a-4978-aedb-bd842c0493d3/scratchpad/headcopy/$f", "transient", "unresolved"),
    ("/private/tmp/claude-501/-Users-georgejackson-Developer-Projects/"
     "a07b3790-0a2a-4978-aedb-bd842c0493d3/scratchpad/ruff_head/$b", "transient", "unresolved"),
)


def test_every_real_corpus_write_this_repair_moves_lands_where_it_was_measured(fa):
    """Real data, not a synthetic shape. These paths were written by real turns."""
    for path, before, after in CORPUS_VERDICT_CHANGES:
        got = fa.classify_path(path)
        assert got == after, (path, "expected", after, "got", got, "was", before)
        assert got != before, (path, "verdict did not move at all")


def test_the_four_recoveries_reach_the_mutation_set_end_to_end(fa):
    """A verdict is worth nothing until a consumer acts on it.

    The 4 writes that moved unresolved -> other are the repair's real recoveries:
    ordinary repository writes the audit previously dropped in silence. This
    drives `record_tool`, the consumer, rather than re-asserting the classifier.
    """
    recoveries = [p for p, b, a in CORPUS_VERDICT_CHANGES
                  if b == "unresolved" and a == "other"]
    assert len(recoveries) == 4, recoveries
    turn = fa.new_turn()
    for p in recoveries:
        fa.record_tool(turn, "Write", {"file_path": p})
    assert turn["mutations"] == recoveries, turn["mutations"]
    assert turn["first_mut"] == 0 and turn["last_mut"] == len(recoveries) - 1
