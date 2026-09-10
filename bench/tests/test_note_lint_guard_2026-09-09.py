"""The note linter must be reached by a commit, not only by a hand.

Task 7.2. Founder ruling 2026-09-04, verbatim: *"THE RULE ALREADY EXISTED as
Rule 27 of the note standard and the linter already caught it ... The failure was
never the absence of a rule or a checker; it was never running the checker.
Therefore: run `python3 scripts/note_vagueness_lint.py <file>` on every note and
every TTS file BEFORE delivering it, and treat a spelled-number finding as
blocking rather than advisory."*

WHAT WAS ACTUALLY WIRED BEFORE THIS. The linter's LOGIC is exercised by 3 test
files, which is not the same as running it over the notes. The only test that
lints real notes selects those declaring a v1.7 foot-line: measured 2026-09-09,
**29 of 379 files under `experimental_notes`, 7.65%, Wilson [5.4%, 10.8%],
Clopper-Pearson [5.2%, 10.8%]**. A new note that simply omitted the foot-line was
exempt by omission -- the checker existed, and the note never met it.

WHY STAGED FILES ONLY. Linting 379 archival notes on every commit would fire on
work written under earlier standards, which the standard preserves deliberately.
What a commit can fairly be held to is what that commit contains.

PROVEN LIVE, not asserted: staging a note containing a spelled number and
attempting a commit returns "REFUSED. 1 note finding(s) in the staged notes",
naming the token, and HEAD does not move. These tests reproduce that.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks" / "pre-commit"
LINT = REPO / "scripts" / "note_vagueness_lint.py"

CLEAN = ("# A clean note\n\nWritten 2026-09-09. It carries 29 findings and 3 "
         "scripts, all in digits.\n\nWritten under CDSFL note standard v1.7 "
         "(26 August 2026).\n")
DIRTY = ("# A note with a spelled number\n\nWritten 2026-09-09. It carries "
         "twenty-nine findings, which Rule 27 forbids.\n\nWritten under CDSFL "
         "note standard v1.7 (26 August 2026).\n")


def _hook_guard_files() -> list[str]:
    """Parse the hook's own `GUARDS=` block. See the note in `_repo`."""
    src = HOOK.read_text(encoding="utf-8")
    body = src[src.index("GUARDS=") + len("GUARDS="):]
    quote = body[0]
    assert quote in "\"'", "the GUARDS assignment in hooks/pre-commit is not quoted"
    names = [ln.strip() for ln in body[1:body.index(quote, 1)].splitlines() if ln.strip()]
    assert names, "the hook names no guard files at all"
    return names


def _repo(tmp_path):
    """A real git repository with the hook wired the way this one wires it."""
    work = tmp_path / "repo"
    (work / "experimental_notes").mkdir(parents=True)
    (work / "scripts").mkdir()
    (work / "hooks").mkdir()
    (work / "bench" / "tests").mkdir(parents=True)
    shutil.copy(LINT, work / "scripts" / "note_vagueness_lint.py")
    shutil.copy(HOOK, work / "hooks" / "pre-commit")
    os.chmod(work / "hooks" / "pre-commit", 0o755)
    # THE GUARD LIST IS READ OUT OF THE HOOK, NOT TYPED HERE. It was typed, as 4
    # names, and the hook has since grown to 6 -- task V1 added
    # `test_done_markers_carry_evidence_2026-09-10.py` and task M2 added
    # `test_task_list_markers_2026-09-09.py`. The hook then correctly refused
    # every commit in this fixture with "guard file(s) missing", and all 10 tests
    # in this file went red. The hook was right and the fixture was stale.
    #
    # This is the same defect as everything else found on 2026-09-10: a list
    # written down in 2 places, where one place moved. Reading it from the hook
    # means adding a 7th guard cannot silently break this file again.
    #
    # The other guards are STUBBED TO PASS so these tests isolate the note-lint
    # stage. Omitting them entirely would make the hook exit before reaching it.
    for g in _hook_guard_files():
        (work / "bench" / "tests" / g.split("/")[-1]).write_text(
            "def test_stub():\n    pass\n", encoding="utf-8")
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    for cmd in (["git", "init", "-q"], ["git", "config", "core.hooksPath", "hooks"],
                ["git", "add", "-A"],
                ["git", "commit", "-q", "--no-verify", "-m", "base"]):
        subprocess.run(cmd, cwd=work, check=True, env=env,
                       capture_output=True, text=True)
    return work, env


def _commit(work, env, name, body):
    (work / "experimental_notes" / name).write_text(body, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=work, check=True, env=env,
                   capture_output=True)
    return subprocess.run(["git", "commit", "-m", "probe"], cwd=work, env=env,
                          capture_output=True, text=True, timeout=180)


def test_the_hook_and_the_linter_both_exist():
    assert HOOK.is_file() and LINT.is_file()


def test_the_hook_names_the_linter():
    assert "note_vagueness_lint.py" in HOOK.read_text(encoding="utf-8"), (
        "the linter is not reached by the commit path, so it is run only by hand")


def test_untouched_prose_in_a_touched_file_is_not_held_against_the_commit(tmp_path):
    """THE SCOPING THAT MAKES THIS GUARD USABLE, and it was wrong first time.

    The first version linted whole staged FILES and refused its own first real
    commit with 388 findings -- every one pre-existing prose in archival notes
    that a 1-line spelled-number correction had merely touched. That contradicted
    the guard's own stated principle, "what a commit can fairly be held to is what
    that commit contains", which had been implemented as "what files it touches".

    Holding a commit to 400 lines written under an earlier standard because it
    corrected 1 number in them is how a guard teaches people to reach for
    --no-verify by reflex."""
    work, env = _repo(tmp_path)
    legacy = ("# An archival note\n\n"
              "There were twenty-nine of them, written under an earlier standard.\n")
    (work / "experimental_notes" / "old.md").write_text(legacy, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=work, check=True, env=env,
                   capture_output=True)
    subprocess.run(["git", "commit", "-q", "--no-verify", "-m", "legacy"],
                   cwd=work, check=True, env=env, capture_output=True)

    # Now touch it with a CLEAN addition. The legacy violation must not block.
    (work / "experimental_notes" / "old.md").write_text(
        legacy + "\nA later correction adds 29 clean findings.\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=work, check=True, env=env,
                   capture_output=True)
    r = subprocess.run(["git", "commit", "-m", "touch"], cwd=work, env=env,
                       capture_output=True, text=True, timeout=180)
    assert r.returncode == 0, (
        f"a clean addition to a file with legacy prose was refused:\n{r.stderr}")


def test_a_violating_ADDED_line_is_still_refused_in_such_a_file(tmp_path):
    """DISCRIMINATION for the same case: the narrowing must not disarm it."""
    work, env = _repo(tmp_path)
    legacy = "# An archival note\n\nThere were twenty-nine of them.\n"
    (work / "experimental_notes" / "old.md").write_text(legacy, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=work, check=True, env=env,
                   capture_output=True)
    subprocess.run(["git", "commit", "-q", "--no-verify", "-m", "legacy"],
                   cwd=work, check=True, env=env, capture_output=True)

    (work / "experimental_notes" / "old.md").write_text(
        legacy + "\nAnd the assistant then added forty seven more.\n",
        encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=work, check=True, env=env,
                   capture_output=True)
    r = subprocess.run(["git", "commit", "-m", "touch"], cwd=work, env=env,
                       capture_output=True, text=True, timeout=180)
    assert r.returncode != 0, "a spelled number ADDED to the file was let through"
    assert "forty seven" in r.stderr, r.stderr


def test_correcting_an_archival_note_always_passes(tmp_path):
    """THE PROPERTY THE 2026-09-09 REMEDIATION DEPENDS ON.

    207 spelled numbers were corrected across 67 archival notes that carry
    plenty of older prose the current standard would flag. A guard that refuses
    a commit for REDUCING the finding count would make the standard
    unenforceable: the only way to touch an old note would be to rewrite it
    entirely, which is the mechanical rewrite the standard forbids."""
    work, env = _repo(tmp_path)
    legacy = ("# An archival note\n\nThe system recorded twenty-nine of them "
              "and the mechanism agreed.\n")
    (work / "experimental_notes" / "old.md").write_text(legacy, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=work, check=True, env=env,
                   capture_output=True)
    subprocess.run(["git", "commit", "-q", "--no-verify", "-m", "legacy"],
                   cwd=work, check=True, env=env, capture_output=True)

    # Correct ONLY the number. The vague subjects stay, as they must.
    (work / "experimental_notes" / "old.md").write_text(
        legacy.replace("twenty-nine", "29"), encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=work, check=True, env=env,
                   capture_output=True)
    r = subprocess.run(["git", "commit", "-m", "correct the number"], cwd=work,
                       env=env, capture_output=True, text=True, timeout=180)
    assert r.returncode == 0, (
        f"correcting a number in an archival note was refused:\n{r.stderr}")


def test_a_brand_new_note_is_held_to_the_whole_standard(tmp_path):
    """The ratchet must not become an amnesty for new work.

    A note with no version at HEAD has a baseline of 0, so every finding in it
    is an addition."""
    work, env = _repo(tmp_path)
    r = _commit(work, env, "brand_new.md",
                "# New\n\nThe system recorded twenty-nine findings.\n\n"
                "Written under CDSFL note standard v1.7 (26 August 2026).\n")
    assert r.returncode != 0, "a new note carrying violations was let through"


def test_a_violating_note_is_REFUSED(tmp_path):
    """THE PROPERTY, driven through a real `git commit`."""
    work, env = _repo(tmp_path)
    r = _commit(work, env, "bad.md", DIRTY)
    assert r.returncode != 0, (
        f"the commit succeeded with a spelled number staged:\n{r.stdout}\n{r.stderr}")
    assert "REFUSED" in r.stderr and "note finding" in r.stderr, r.stderr
    assert "twenty-nine" in r.stderr, (
        "the refusal must name the offending token, or it cannot be acted on")


def test_the_refused_commit_does_not_land(tmp_path):
    """A guard that prints a refusal and commits anyway is worse than none."""
    work, env = _repo(tmp_path)
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=work, env=env,
                            capture_output=True, text=True).stdout.strip()
    _commit(work, env, "bad.md", DIRTY)
    after = subprocess.run(["git", "rev-parse", "HEAD"], cwd=work, env=env,
                           capture_output=True, text=True).stdout.strip()
    assert before == after, "HEAD moved despite the refusal"


def test_a_clean_note_commits(tmp_path):
    """DISCRIMINATION. A guard that fires on everything is as useless as one
    that fires on nothing."""
    work, env = _repo(tmp_path)
    r = _commit(work, env, "good.md", CLEAN)
    assert r.returncode == 0, f"a clean note was refused:\n{r.stdout}\n{r.stderr}"
    # git routes a hook's stdout to its own stderr, so the confirmation can
    # arrive on either stream depending on the git version.
    assert "ratchet held" in (r.stdout + r.stderr), (r.stdout, r.stderr)


def test_a_commit_touching_no_note_is_unaffected(tmp_path):
    """The guard must not tax every commit in the repository."""
    work, env = _repo(tmp_path)
    (work / "scripts" / "unrelated.py").write_text("x = 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=work, check=True, env=env,
                   capture_output=True)
    r = subprocess.run(["git", "commit", "-m", "unrelated"], cwd=work, env=env,
                       capture_output=True, text=True, timeout=180)
    assert r.returncode == 0, r.stderr
    assert "ratchet" not in (r.stdout + r.stderr), (r.stdout, r.stderr)


def test_a_missing_linter_refuses_rather_than_passes(tmp_path):
    """FAILS CLOSED. "A guard that cannot fail is not a guard" is this project's
    own line, with 3 instances recorded in a single night."""
    work, env = _repo(tmp_path)
    (work / "scripts" / "note_vagueness_lint.py").unlink()
    r = _commit(work, env, "any.md", CLEAN)
    assert r.returncode != 0, "a missing linter let the commit through"
    assert "linter is missing" in r.stderr, r.stderr


def test_no_verify_remains_the_documented_escape(tmp_path):
    """Bypassing must stay possible and stay deliberate."""
    work, env = _repo(tmp_path)
    (work / "experimental_notes" / "bad.md").write_text(DIRTY, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=work, check=True, env=env,
                   capture_output=True)
    r = subprocess.run(["git", "commit", "--no-verify", "-m", "deliberate"],
                       cwd=work, env=env, capture_output=True, text=True, timeout=180)
    assert r.returncode == 0, r.stderr


# ── THE TWO BYPASSES A REVIEWER DEMONSTRATED, 2026-09-10 ────────────────────
#
# The guard shipped on 2026-09-09 and an adversarial review found 2 ways past
# it the same night. Both are reproduced here as tests, because both were
# invisible to the 12 that existed: one committed a single file and so never
# reached the mixed case, and none broke the linter.

def test_a_mixed_commit_cannot_smuggle_a_new_violation(tmp_path):
    """BYPASS 1, REPRODUCED. A ratchet on a SUM is not a ratchet.

    The first version summed every staged note and compared totals. A commit
    that cleaned 3 spelled numbers out of an archival note AND added a new note
    containing "twenty-nine" nets -2, so the total fell and the commit landed
    with exit 0. The guard printed the new violation by name on its way past.
    Judged per file, the new note goes 0 -> 1 and the commit is refused."""
    work, env = _repo(tmp_path)
    legacy = ("# An archival note\n\nThere were twenty-nine of them, and "
              "forty seven others, and fifty five more.\n")
    (work / "experimental_notes" / "old.md").write_text(legacy, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=work, check=True, env=env,
                   capture_output=True)
    subprocess.run(["git", "commit", "-q", "--no-verify", "-m", "legacy"],
                   cwd=work, check=True, env=env, capture_output=True)
    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=work, env=env,
                            capture_output=True, text=True).stdout.strip()

    # Clean the old note AND add a new one carrying a fresh violation.
    (work / "experimental_notes" / "old.md").write_text(
        legacy.replace("twenty-nine", "29").replace("forty seven", "47")
              .replace("fifty five", "55"), encoding="utf-8")
    (work / "experimental_notes" / "brand_new.md").write_text(
        "# New\n\nThe run recorded twenty-nine findings.\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=work, check=True, env=env,
                   capture_output=True)
    r = subprocess.run(["git", "commit", "-m", "mixed"], cwd=work, env=env,
                       capture_output=True, text=True, timeout=180)

    assert r.returncode != 0, (
        f"a net-downward commit smuggled a new violation through:\n"
        f"{r.stdout}\n{r.stderr}")
    assert "brand_new.md" in r.stderr, r.stderr
    after = subprocess.run(["git", "rev-parse", "HEAD"], cwd=work, env=env,
                           capture_output=True, text=True).stdout.strip()
    assert before == after, "HEAD moved despite the refusal"


def test_the_cleaning_half_of_that_commit_still_passes_on_its_own(tmp_path):
    """DISCRIMINATION for bypass 1. Correcting an archival note must still be
    possible — the narrowing must not become a bar."""
    work, env = _repo(tmp_path)
    legacy = "# An archival note\n\nThere were twenty-nine of them.\n"
    (work / "experimental_notes" / "old.md").write_text(legacy, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=work, check=True, env=env,
                   capture_output=True)
    subprocess.run(["git", "commit", "-q", "--no-verify", "-m", "legacy"],
                   cwd=work, check=True, env=env, capture_output=True)
    (work / "experimental_notes" / "old.md").write_text(
        legacy.replace("twenty-nine", "29"), encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=work, check=True, env=env,
                   capture_output=True)
    r = subprocess.run(["git", "commit", "-m", "clean"], cwd=work, env=env,
                       capture_output=True, text=True, timeout=180)
    assert r.returncode == 0, r.stderr


def test_a_linter_that_errors_refuses_rather_than_scoring_zero(tmp_path):
    """BYPASS 2, REPRODUCED. The guard failed OPEN when its checker broke.

    `LINT_CODE=$?` sat after an if/else, so it read the if/else's status — always
    0 — and the "linter could not run" refusal was unreachable. A linter that
    errors still prints "0 finding(s)" on its way out, so the count read 0 and
    the commit passed. That is failing open inside a guard whose own header
    says it fails closed."""
    work, env = _repo(tmp_path)
    # A linter that always errors, while still printing a plausible count.
    (work / "scripts" / "note_vagueness_lint.py").write_text(
        "import sys\nprint('  0 finding(s). Reported, not enforced')\n"
        "sys.exit(3)\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=work, check=True, env=env,
                   capture_output=True)
    subprocess.run(["git", "commit", "-q", "--no-verify", "-m", "break linter"],
                   cwd=work, check=True, env=env, capture_output=True)

    r = _commit(work, env, "any.md", CLEAN)
    assert r.returncode != 0, (
        f"a broken linter scored 0 findings and the commit passed:\n{r.stderr}")
    assert "exited non-zero" in r.stderr, r.stderr
