"""The naming check catches a coined machinery name and passes an introduced one.

WHY. Of 13 terms the founder examined from CC1's own reports, 8 were faults: 7
coined outright, 1 a collision with an existing project meaning. His complaint:
*"It can't be the case that I wake up to a tts report and struggle to know what
you are talking about!"* `note_vagueness_lint.py` passed every faulty term.

WHAT IS GUARDED. The check's DISCRIMINATION, executed rather than described -- it
must fire on a bare coined machinery name and stay silent on one the writer
introduces. Its measured limits are asserted too, because a check whose blind
spots are undocumented invites exactly the false confidence it exists to prevent.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "note_naming_check_2026-09-28.py"


def _load():
    spec = importlib.util.spec_from_file_location("naming_check", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["naming_check"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def nc():
    assert SCRIPT.is_file(), f"missing {SCRIPT}"
    return _load()


def test_candidates_require_a_machinery_head_noun(nc):
    """Adjacency is not a name. The first design matched any 2-4 words and
    returned 24 findings on one report, nearly all sentence fragments."""
    found = nc.candidates("The critics order ran first and the write returned nothing.")
    assert "critics order" in found
    assert "write returned" not in found, "a verb phrase is not a machinery name"


def test_ordinary_english_with_a_head_noun_is_not_a_name(nc):
    found = nc.candidates("The same gate fired again at the next stage.")
    assert "same gate" not in found
    assert "next stage" not in found


def test_an_introduced_name_is_passed_over(nc):
    """Coining a name is permitted; asserting one as already-shared is the fault."""
    text = "The absorb rule, which is the mechanism merging near-duplicates, fired."
    cands = nc.candidates(text)
    assert "absorb rule" in cands
    assert nc.introduced(text, "absorb rule", cands["absorb rule"]) is True


def test_a_bare_name_is_not_treated_as_introduced(nc):
    text = "The critics order determined which dimension ran first."
    cands = nc.candidates(text)
    assert "critics order" in cands
    assert nc.introduced(text, "critics order", cands["critics order"]) is False


def test_code_and_paths_are_not_scanned_for_names(nc):
    """A phrase inside backticks or a path is not prose making a claim."""
    stripped = nc._strip("Text `the widget gate` and bench/the_widget_gate.py here.")
    assert "widget gate" not in stripped.lower()


def test_repo_hits_excludes_the_note_being_checked(nc, tmp_path):
    """A note must not vouch for its own coinage.

    THE SENTINEL IS ASSEMBLED AT RUN TIME, AND THE FIRST VERSION WAS NOT. It wrote
    the absent phrase as a literal, which passed while the file was uncommitted and
    failed the moment it was committed, because `git grep` then found the phrase in
    THIS FILE and returned 1 where 0 was asserted.

    That is not an incidental slip: it is the retrospective blind spot documented in
    the script's own header, demonstrated by the test on itself. A phrase becomes
    invisible to a novelty check the instant anything in the repository contains it,
    including the check's own tests. Joining the parts here means the whole phrase
    exists nowhere on disk, so `git grep -F` cannot match it.
    """
    hits_all = nc.repo_hits("additive standard", exclude=None)
    assert hits_all > 0, (
        "expected a known project term to appear in the repo; -1 would mean no "
        "search backend answered at all, which the fallback exists to prevent")
    sentinel = " ".join(["zzqx" + "vvbb", "nonexistent" + "qqq", "gate" + "xyz"])
    missing = nc.repo_hits(sentinel, exclude=None)
    assert missing == 0, (
        f"{sentinel!r} was found in the repo; if a test now writes it as a "
        "literal, assemble it at run time instead"
    )


def test_a_verb_before_the_head_means_the_match_crossed_a_clause(nc):
    """Measured 2026-09-28: the head-noun pattern alone returned 6 findings on the
    28 September report, 5 of them clause fragments. The verb filter removed only
    false positives -- the 24 September report stayed at 3 findings including the
    confirmed fault `prose scoring flag`, and the fixture's `critics order` still
    fired."""
    assert "appendix retired that rule" not in nc.candidates(
        "The appendix retired that rule on 2026-09-21.")
    assert "decision precedes the branch" not in nc.candidates(
        "The decision precedes the branch in every case.")
    assert "dispatcher passes seats" not in nc.candidates(
        "The dispatcher passes seats their tool list.")
    # And the filter must not eat a real coinage whose modifier merely looks verb-like.
    assert "prose scoring flag" in nc.candidates("The prose scoring flag was unreachable.")


def test_the_documented_blind_spot_is_real_not_theoretical(nc):
    """A COLLISION is invisible: the term exists, so novelty is 0 and nothing fires.

    This is asserted so the limit cannot quietly stop being true and leave the
    docstring overstating what the check covers.
    """
    hits = nc.repo_hits("blocking gate", exclude=None)
    assert hits > 0, (
        "`blocking gate` no longer appears in the repo; the collision blind spot "
        "documented in the script's header needs re-measuring"
    )


# ---------------------------------------------------------------------------
# THE FALSE ZERO. A failing search backend was read as "the phrase is already
# known", so every phrase was DROPPED and --measure printed a rate it could not
# compute. Two fabrication modes were executed on 2026-09-28, in OPPOSITE
# directions, both exiting 0 with a Wilson interval printed round the fake rate.
#
# EVERY TEST BELOW RUNS THE REAL SCRIPT IN A REAL TREE. None asserts on source
# text and none hardcodes a constant the module owns: the sentinel phrase, the
# exit codes and the exclusion list are all READ OFF the module, because a probe
# that re-derives a value the code owns is the shape that shipped five defects
# the same day -- each one staying green through a mutation that broke the thing
# it appeared to guard.
# ---------------------------------------------------------------------------


def _tree(tmp_path: Path, notes: int = 4, with_git: bool = False,
          populated: bool = False) -> Path:
    """A tree the script can be pointed at: scripts/ + experimental_notes/.

    The notes are REAL notes from this repository, so the corpus is the thing
    the script is built for rather than a fixture that only resembles one.
    """
    import shutil
    import subprocess as sp
    root = tmp_path / ("git_tree" if with_git else "bare_tree")
    (root / "scripts").mkdir(parents=True)
    (root / "experimental_notes").mkdir(parents=True)
    shutil.copy2(SCRIPT, root / "scripts" / SCRIPT.name)
    src = sorted((ROOT / "experimental_notes").glob("*.md"))[:notes]
    assert src, "this repository has no notes corpus to build a fixture from"
    for p in src:
        shutil.copy2(p, root / "experimental_notes" / p.name)
    if populated:
        #: The sentinel must be findable, or the script refuses -- which is the
        #: behaviour a different test asserts. Read the phrase off the module so
        #: this fixture cannot drift from the guard it is feeding.
        (root / "SENTINEL_CARRIER.md").write_text(
            f"This tree carries the {_sentinel()} directive.\n", encoding="utf-8")
    if with_git:
        sp.run(["git", "init", "-q", "."], cwd=root, check=True,
               capture_output=True)
    return root


def _sentinel() -> str:
    """The sentinel phrase, EXTRACTED from the module rather than retyped."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("naming_check_probe", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.SENTINEL


def _run(root: Path, *args: str):
    import subprocess as sp
    return sp.run([sys.executable, "scripts/" + SCRIPT.name, *args],
                  cwd=root, capture_output=True, text=True, timeout=900)


def test_a_git_less_tree_no_longer_fabricates_a_zero_rate(nc, tmp_path):
    """MODE 1, EXECUTED. Every panel sandbox has `.git` severed by design, so
    `git grep` exits 128 and `repo_hits` returned -1; `check()` filtered on
    `hits != 0`, dropping every phrase. Before the fix a git-less copy of this
    repository printed `RULE A 0/5 = 0.0000%`, density 0.0000, exit 0.

    The fix must leave --measure either REPORTING (the fallback answered) or
    REFUSING (nothing could), and never printing a 0 rate at exit 0.
    """
    root = _tree(tmp_path, notes=4, with_git=False, populated=True)
    assert not (root / ".git").exists()
    r = _run(root, "--measure")
    assert r.returncode in (nc.EXIT_CLEAN, nc.EXIT_REFUSED), r.stderr
    if r.returncode == nc.EXIT_CLEAN:
        assert "search backend        grep" in r.stdout, r.stdout
        assert "0/4 = 0.0000%" not in r.stdout, (
            "a git-less tree still reported a zero firing rate:\n" + r.stdout)
    else:
        assert "REFUS" in r.stderr.upper(), r.stderr


def test_an_empty_git_index_is_refused_not_reported(nc, tmp_path):
    """MODE 2, EXECUTED, AND THE OPPOSITE DIRECTION. `git init` with nothing
    added makes `git grep` exit 1 -- not an error -- so every count is a
    legitimate-looking 0, every phrase becomes a finding, and before the fix the
    same corpus printed `RULE A 5/5 = 100.0000%`, density 5.8000, exit 0.

    THIS IS WHY THE SENTINEL IS `<= 0` AND NOT `< 0`: -1 never occurs here, so a
    test for a failed backend cannot see this mode at all.
    """
    root = _tree(tmp_path, notes=4, with_git=True, populated=True)
    assert (root / ".git").is_dir()
    r = _run(root, "--measure")
    assert r.returncode == nc.EXIT_REFUSED, (
        f"expected refusal, got {r.returncode}\nSTDOUT:\n{r.stdout}\n"
        f"STDERR:\n{r.stderr}")
    assert "100.0000%" not in r.stdout, r.stdout
    assert _sentinel() in r.stderr, r.stderr


def _tree_with_both_backends_dead(tmp_path: Path, tag: str) -> tuple[Path, Path]:
    """A tree where BOTH backends genuinely fail, and the stubs are real files.

    THE FIRST VERSION OF THE TEST BELOW WAS VACUOUS AND THE MUTATION PROVED IT.
    It set PATH to an empty directory to kill `git`, but the fallback names
    `/usr/bin/grep` by ABSOLUTE PATH, so the fallback always answered, the
    refusal path was never reached, and its assertion sat behind
    `if "REFUSED" in r.stderr` -- which never fired. Deleting the `except
    Unsearchable` clause left all 19 tests green. Killing `git` alone cannot
    reach the refusal; the absolute path in the source has to be redirected too.
    """
    bin_dir = tmp_path / f"deadbin_{tag}"
    bin_dir.mkdir()
    (bin_dir / "git").write_text("#!/bin/sh\nexit 128\n", encoding="utf-8")
    (bin_dir / "git").chmod(0o755)
    dead_grep = tmp_path / f"deadgrep_{tag}.sh"
    dead_grep.write_text("#!/bin/sh\nexit 2\n", encoding="utf-8")
    dead_grep.chmod(0o755)

    root = _tree(tmp_path / f"root_{tag}", notes=2, with_git=False, populated=True)
    target = root / "scripts" / SCRIPT.name
    src = target.read_text(encoding="utf-8")
    assert '"/usr/bin/grep"' in src, "the fallback no longer names /usr/bin/grep"
    target.write_text(src.replace('"/usr/bin/grep"', f'"{dead_grep}"'),
                      encoding="utf-8")
    return root, bin_dir


def test_refusal_has_its_own_exit_code_distinct_from_findings(nc, tmp_path):
    """A REFUSAL MUST NOT ARRIVE AS "1 FINDING". An uncaught exception leaves
    Python at exit 1, which is this tool's code for FINDINGS -- so raising
    without catching would have swapped one silent failure for another. BOTH
    seat proposals for this fix let the exception propagate, and neither noticed.

    Driven all the way through `main()` as a subprocess, because the exit code
    is the thing a caller reads and it exists nowhere inside the process.
    """
    assert nc.EXIT_REFUSED != nc.EXIT_FINDINGS
    root, bin_dir = _tree_with_both_backends_dead(tmp_path, "report")
    note = root / "experimental_notes" / "probe.md"
    note.write_text("The zzqxvvbb frobnication gate fired twice.\n",
                    encoding="utf-8")

    import os
    import subprocess as sp
    env = dict(os.environ)
    env["PATH"] = f"{bin_dir}:/usr/bin:/bin"
    r = sp.run([sys.executable, "scripts/" + SCRIPT.name,
                "experimental_notes/probe.md"],
               cwd=root, capture_output=True, text=True, timeout=300, env=env)
    assert r.returncode == nc.EXIT_REFUSED, (
        f"a tree no backend can search exited {r.returncode}, and "
        f"{nc.EXIT_FINDINGS} would be indistinguishable from findings\n"
        f"STDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}")
    assert "REFUSED" in r.stderr, r.stderr
    assert "NAMES NOTHING" not in r.stdout, r.stdout


def test_measure_also_refuses_through_main_when_both_backends_die(nc, tmp_path):
    """The same catch point, reached from --measure rather than from a note, so
    no mode can route an Unsearchable to the findings exit code."""
    root, bin_dir = _tree_with_both_backends_dead(tmp_path, "measure")
    import os
    import subprocess as sp
    env = dict(os.environ)
    env["PATH"] = f"{bin_dir}:/usr/bin:/bin"
    r = sp.run([sys.executable, "scripts/" + SCRIPT.name, "--measure"],
               cwd=root, capture_output=True, text=True, timeout=300, env=env)
    assert r.returncode == nc.EXIT_REFUSED, (r.returncode, r.stdout, r.stderr)
    assert "Wilson" not in r.stdout, r.stdout


def test_check_refuses_when_no_backend_can_answer(nc, tmp_path):
    """check() must RAISE on -1, not drop the phrase. Guarded through the public
    function rather than through the internal cache, so the contract under test
    is the one `check()` actually consumes."""
    note = tmp_path / "note.md"
    note.write_text("The zzqxvvbb frobnication gate fired.\n", encoding="utf-8")
    seen: list[str] = []

    def dead(phrase, exclude=None):
        seen.append(phrase)
        return -1

    original = nc.repo_hits
    nc.repo_hits = dead
    try:
        with pytest.raises(nc.Unsearchable):
            nc.check(note)
    finally:
        nc.repo_hits = original
    assert seen, "check() never consulted the backend at all"


def test_unsearchable_is_a_runtime_error_so_old_callers_still_catch_it(nc):
    assert issubclass(nc.Unsearchable, RuntimeError)


def test_the_fallback_answers_where_git_cannot(nc, tmp_path):
    """THE ADDITIVE HALF, EXECUTED. Refusing alone would leave the tool unable
    to run in the very place the defect was found. In a git-less tree the
    fallback must return a real count for a phrase that is present and 0 for one
    that is absent -- the operating-characteristic pair, not one half of it.
    """
    root = _tree(tmp_path, notes=3, with_git=False, populated=True)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "naming_check_fallback", root / "scripts" / SCRIPT.name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.ROOT == root, mod.ROOT

    present, backend = mod.repo_hits_detail(mod.SENTINEL, exclude=None)
    assert backend == "grep", f"expected the fallback, got {backend!r}"
    assert present > 0, f"{mod.SENTINEL!r} not found by the fallback"

    #: ASSEMBLED AT RUN TIME. A literal here would be written into the tree by
    #: this very file and stop being absent -- the retrospective blind spot the
    #: script documents, demonstrated once already by an earlier version of the
    #: test above.
    absent = " ".join(["zzqx" + "vvbb", "frobnication" + "qqq", "gate" + "xyz"])
    missing, backend2 = mod.repo_hits_detail(absent, exclude=None)
    assert backend2 == "grep"
    assert missing == 0, f"{absent!r} was found in a 4-file tree: {missing}"


def test_a_failing_grep_that_printed_matches_is_kept_as_a_lower_bound(nc, tmp_path):
    """Measured 2026-09-28: a concurrent write elsewhere in the repository made
    one plain grep exit 2 AFTER printing a correct match, and the same phrase
    exited 0 on retry. Discarding that output would refuse on a tree that is
    merely busy, so a non-empty result from a failing grep is kept.

    Driven through the real subprocess boundary with a stub `git` and a stub
    `grep`, so the rule under test is the one the code runs.
    """
    import subprocess as sp
    bin_dir = tmp_path / "stub_bin"
    bin_dir.mkdir()
    (bin_dir / "git").write_text("#!/bin/sh\nexit 128\n", encoding="utf-8")
    (bin_dir / "git").chmod(0o755)

    root = _tree(tmp_path, notes=2, with_git=False, populated=True)
    stub_grep = tmp_path / "grep_partial.sh"
    stub_grep.write_text("#!/bin/sh\necho './some/file.md'\nexit 2\n",
                         encoding="utf-8")
    stub_grep.chmod(0o755)

    src = (root / "scripts" / SCRIPT.name).read_text(encoding="utf-8")
    assert '"/usr/bin/grep"' in src, "the fallback no longer names /usr/bin/grep"
    patched = src.replace('"/usr/bin/grep"', f'"{stub_grep}"')
    (root / "scripts" / SCRIPT.name).write_text(patched, encoding="utf-8")

    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "naming_check_partial", root / "scripts" / SCRIPT.name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    env = dict(**{"PATH": f"{bin_dir}:/usr/bin:/bin"})
    import os
    old_path = os.environ["PATH"]
    os.environ["PATH"] = env["PATH"]
    try:
        hits, backend = mod.repo_hits_detail("anything at all", exclude=None)
    finally:
        os.environ["PATH"] = old_path
    assert backend == "grep", backend
    assert hits == 1, (
        f"a grep that printed 1 match and exited 2 gave {hits}; its output is a "
        "lower bound, not a failure")
    del sp


def test_an_empty_result_from_a_failing_grep_stays_unknowable(nc, tmp_path):
    """The other half of the same rule, and the half that protects the fix:
    "found nothing" and "died before looking" are the same empty string, so an
    empty result from a failing grep must be -1 rather than 0."""
    bin_dir = tmp_path / "stub_bin2"
    bin_dir.mkdir()
    (bin_dir / "git").write_text("#!/bin/sh\nexit 128\n", encoding="utf-8")
    (bin_dir / "git").chmod(0o755)

    root = _tree(tmp_path, notes=2, with_git=False, populated=True)
    stub_grep = tmp_path / "grep_dead.sh"
    stub_grep.write_text("#!/bin/sh\nexit 2\n", encoding="utf-8")
    stub_grep.chmod(0o755)
    src = (root / "scripts" / SCRIPT.name).read_text(encoding="utf-8")
    patched = src.replace('"/usr/bin/grep"', f'"{stub_grep}"')
    (root / "scripts" / SCRIPT.name).write_text(patched, encoding="utf-8")

    import importlib.util
    import os
    spec = importlib.util.spec_from_file_location(
        "naming_check_dead", root / "scripts" / SCRIPT.name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    old_path = os.environ["PATH"]
    os.environ["PATH"] = f"{bin_dir}:/usr/bin:/bin"
    try:
        hits, backend = mod.repo_hits_detail("anything at all", exclude=None)
    finally:
        os.environ["PATH"] = old_path
    assert (hits, backend) == (-1, "none"), (hits, backend)

    note = root / "experimental_notes" / "probe.md"
    note.write_text("The zzqxvvbb frobnication gate fired.\n", encoding="utf-8")
    os.environ["PATH"] = f"{bin_dir}:/usr/bin:/bin"
    try:
        mod._search_files.cache_clear()
        with pytest.raises(mod.Unsearchable):
            mod.check(note)
    finally:
        os.environ["PATH"] = old_path


def test_the_backend_label_comes_from_the_call_that_chose_it(nc):
    """ONE DECIDER, EXECUTED. If anything re-derived "is git available?" instead
    of reading the answer off the call that used it, producer and consumer could
    disagree while each looked individually correct -- the shape behind five
    defects on 2026-09-28. repo_hits() must agree with repo_hits_detail() on the
    same phrase, count and all."""
    nc._search_files.cache_clear()
    count, backend = nc.repo_hits_detail(nc.SENTINEL, exclude=None)
    assert backend in ("git", "grep"), backend
    assert count == nc.repo_hits(nc.SENTINEL, exclude=None)
    assert (count < 0) == (backend == "none")


def test_compare_backends_executes_both_and_reports_a_ci(nc):
    """THE RATE TRAVELS WITH ITS SCRIPT. The docstring claims the fallback
    substitutes safely for the decision check() makes; that claim is only worth
    the committed measurement behind it, so the mode that produces it must run.
    Small limit here for suite cost -- the full figure is in the docstring with
    the command that reproduces it."""
    rc = nc.compare_backends(limit=4)
    assert rc == nc.EXIT_CLEAN, rc


def test_measure_refuses_rather_than_printing_a_rate_it_cannot_compute(nc, tmp_path):
    """The refusal path of --measure, reached through main() so the exit code the
    caller sees is the one asserted."""
    root = _tree(tmp_path, notes=3, with_git=True, populated=False)
    r = _run(root, "--measure")
    assert r.returncode == nc.EXIT_REFUSED, (r.returncode, r.stdout, r.stderr)
    assert "Wilson" not in r.stdout, r.stdout


def test_the_fallback_can_see_the_notes_corpus_it_is_asked_about(nc):
    """A NARROWING EXCLUSION MUST NOT PASS UNNOTICED, and one did.

    Adding `experimental_notes` to `_EXCLUDE_DIRS` hides the entire notes corpus
    from the fallback -- every phrase whose only home is a note then reads as
    novel -- and all 20 earlier tests stayed green, because the fallback was only
    reachable by first breaking git. It is now its own function, so this test
    executes it where git works.

    THE DISCRIMINATING PHRASE IS FOUND AT RUN TIME, NOT WRITTEN DOWN. A literal
    would go stale the moment that phrase appeared elsewhere in the tree, and
    hardcoding a value the repository owns is the defect shape this whole file is
    about. So: ask git where each candidate lives, keep the ones that live ONLY
    under experimental_notes, and require the fallback to find them too.
    """
    notes = sorted((ROOT / "experimental_notes").glob("*.md"))
    assert notes, "no notes corpus to test against"

    discriminating: list[tuple[str, tuple[str, ...]]] = []
    for note in notes[:30]:
        if len(discriminating) >= 3:
            break
        text = note.read_text(encoding="utf-8", errors="replace")
        for phrase in sorted(nc.candidates(text)):
            where = nc._git_grep(phrase)
            if where is None:
                pytest.skip("git could not answer, so there is nothing to compare")
            if where and all(f.startswith("experimental_notes/") for f in where):
                discriminating.append((phrase, where))
                break

    assert discriminating, (
        "found no phrase living only under experimental_notes, so this test "
        "cannot discriminate; widen the scan before trusting it")

    for phrase, where in discriminating:
        found = nc._plain_grep(phrase)
        assert found is not None, f"the fallback could not answer {phrase!r}"
        assert found, (
            f"{phrase!r} is in {len(where)} note(s) ({where[0]}) and the fallback "
            "found it in none -- an exclusion is hiding the notes corpus")


def test_both_backends_are_reachable_and_agree_on_a_saturating_term(nc):
    """Executed side by side on the SAME phrase, in a tree where both work. The
    counts differ by design -- git asks about tracked content, the fallback about
    the working tree minus the caches -- but the zero-or-not answer, which is the
    only thing `check()` reads, must not."""
    git_files = nc._git_grep(nc.SENTINEL)
    if git_files is None:
        pytest.skip("git could not answer in this tree")
    plain_files = nc._plain_grep(nc.SENTINEL)
    assert plain_files is not None, "the fallback could not answer at all"
    assert (len(git_files) == 0) == (len(plain_files) == 0), (
        f"backends disagree on whether {nc.SENTINEL!r} exists: "
        f"git {len(git_files)}, fallback {len(plain_files)}")
    assert len(git_files) > 0 and len(plain_files) > 0
