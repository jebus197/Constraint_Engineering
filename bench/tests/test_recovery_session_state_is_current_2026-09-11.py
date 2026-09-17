"""Task A23: RECOVERY.md's newest SESSION STATE must not fall behind the commits.

WHY THIS MATTERS MORE THAN TIDINESS. After a compaction the assistant reads
`resources/RECOVERY.md` as its picture of where the project is. On 2026-09-11 the
newest block was dated 2026-09-08 and named HEAD `beb39fb`, while HEAD was 3 days
and dozens of commits past it -- so the picture omitted the whole task-list
clearance arc, the fresh-clone work and 2 panel rounds. `rs` surfaced it.

AND "RUN SV" WOULD NOT HAVE FIXED IT. `scripts/cdsfl_sv.py --dry-run` reports
"Preserved manual content" for RECOVERY.md: it updates a timestamp and
DELIBERATELY does not regenerate the hand-written SESSION STATE block, flagging
the stamp so it says the body was preserved rather than implying freshness. The
entry that said "to be closed by the next sv" was wrong about the mechanism. The
block is written by hand, so a guard is the only thing that can notice it rotting.

WHAT THIS CHECKS, and what it deliberately does not. It checks that the newest
block names a commit reachable from HEAD and is not absurdly old. It does NOT
check the prose: no test can tell whether a recovery narrative is a good one, and
pretending otherwise would be a guard that fires on style.

AND THERE IS ONE DECIDABLE SLICE OF THE PROSE, added 2026-09-11 after this guard
stayed GREEN over a claim that had become FALSE. The block read *"A FRESH `git
clone` NOW RUNS THE FULL SUITE GREEN: 6658 passed ... EXIT 0"*. Cloning HEAD that
morning gave 3 failed, 6952 passed. The guard was right not to judge the
narrative -- but that sentence was not a narrative, it was a MEASUREMENT, and
this project already has a rule for those: `measured-rate-travels-with-its-script`
says a figure may be cited only if the script that produced it is committed
alongside. The 6658 named no producer, because nothing in the repository performed
a clone at all, which is exactly how it survived being false for a day.

So: a suite-shaped or clone-shaped figure in the newest block must name a script.
That is mechanically decidable, it would have caught this, and it still says
nothing about whether the prose is any good. WIDENED 2026-09-17 (panel round
17, task A23): a complete pytest command also counts as a producer, because the
full suite has no `scripts/*.py` producer and the rule was unsatisfiable by
honest prose about it; see `_NAMES_A_PYTEST_RUN` below. The check is still
syntactic: it asks that a producer be NAMED, not that the named one produced
the figure.
"""
from __future__ import annotations

import datetime
import pathlib
import re
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
RECOVERY = ROOT / "resources" / "RECOVERY.md"

#: How far behind HEAD the newest block may fall before it misleads a reader.
#: Generous on purpose: this is a rot detector, not a commit-by-commit ratchet.
MAX_COMMITS_BEHIND = 60


def _newest_block() -> tuple[str, str]:
    text = RECOVERY.read_text(encoding="utf-8")
    m = re.search(r"^## SESSION STATE — (.+?)\s*\(READ THIS FIRST\)\s*$",
                  text, re.M)
    assert m, "RECOVERY.md carries no SESSION STATE heading at all"
    start = m.end()
    nxt = re.search(r"^## SESSION STATE — ", text[start:], re.M)
    return m.group(1), text[start:start + (nxt.start() if nxt else len(text))]


class TestTheNewestBlockIsCurrent:
    def test_it_names_a_commit_reachable_from_head(self):
        _when, body = _newest_block()
        shas = re.findall(r"`([0-9a-f]{7,40})`", body)
        assert shas, "the newest SESSION STATE names no commit at all"
        # THE PROBE MUST BE ABLE TO ANSWER, OR SAY SO. Added 2026-09-17 by panel
        # review of task A23. `git merge-base --is-ancestor` exits 0 ancestor,
        # 1 not-an-ancestor and 128 when it cannot answer at all -- and "not a
        # git repository" is 128. Reading `returncode == 0` alone collapses 1
        # and 128 into "not reachable", so OUTSIDE A CHECKOUT this test
        # FABRICATED the failure "the block describes a tree that is not this
        # one". That is exactly the defect panel round 12 found in
        # `overstated_entries_2026-09-11.py`, which fabricated a 100% failure
        # rate from exit 128 -- and it was live here, in any `.git`-less copy
        # (a `git archive` export, a ZIP) and in every panel sandbox, because
        # `panel_sandbox.build()` deletes `.git`. A `git clone` keeps `.git`
        # and was never affected.
        #
        # The sibling test below ALREADY skips for this reason (":88"). One
        # test in a class skipping where its twin fabricates is the whole bug.
        #
        # SCOPED DELIBERATELY so this is not a hole: the skip is keyed on git
        # having no repository AT ALL, not on the 128 exit. A block naming a
        # sha that does not exist inside a real checkout still exits 128 and
        # still FAILS, which is the case worth catching.
        if subprocess.run(["git", "rev-parse", "--git-dir"], cwd=ROOT,
                          capture_output=True).returncode != 0:
            pytest.skip("not a git checkout, so reachability is undefined here "
                        "rather than false; run this in a checkout")
        reachable = []
        for sha in shas[:4]:
            r = subprocess.run(["git", "merge-base", "--is-ancestor", sha, "HEAD"],
                               cwd=ROOT, capture_output=True)
            reachable.append(r.returncode == 0)
        assert any(reachable), (
            f"none of the commits the newest SESSION STATE names ({shas[:4]}) is "
            f"an ancestor of HEAD; the block describes a tree that is not this "
            f"one")

    def test_it_is_not_far_behind_head(self):
        _when, body = _newest_block()
        shas = re.findall(r"`([0-9a-f]{7,40})`", body)
        best = None
        for sha in shas[:4]:
            r = subprocess.run(["git", "rev-list", "--count", f"{sha}..HEAD"],
                               cwd=ROOT, capture_output=True, text=True)
            if r.returncode == 0 and r.stdout.strip().isdigit():
                n = int(r.stdout.strip())
                best = n if best is None else min(best, n)
        if best is None:
            pytest.skip("no commit in the newest block resolves in this clone")
        assert best <= MAX_COMMITS_BEHIND, (
            f"the newest SESSION STATE is {best} commits behind HEAD. After a "
            f"compaction this file IS the project's picture of itself; write a "
            f"new block rather than raising this number. Note that "
            f"`scripts/cdsfl_sv.py` deliberately PRESERVES this block and will "
            f"not write it for you.")

    def test_its_date_is_not_absurdly_old(self):
        when, _body = _newest_block()
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})", when)
        assert m, f"the heading date is unparseable: {when!r}"
        d = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        age = (datetime.date.today() - d).days
        assert age <= 21, (
            f"the newest SESSION STATE is {age} days old. This is the file a "
            f"post-compaction reader trusts most.")


class TestTheCheckIsNotVacuous:
    def test_there_is_more_than_one_block(self):
        """The file is a RECORD: older blocks are kept deliberately. If there
        were only one, 'newest' would be measuring nothing."""
        n = len(re.findall(r"^## SESSION STATE — ", RECOVERY.read_text(), re.M))
        assert n >= 3, f"only {n} SESSION STATE block(s); the history is gone"

    def test_the_newest_block_is_the_first_one(self):
        """Newest-first is the file's own convention and the reason the heading
        says READ THIS FIRST. If it ever became oldest-first, every assertion
        above would silently be about the wrong block."""
        text = RECOVERY.read_text(encoding="utf-8")
        dates = re.findall(r"^## SESSION STATE — (\d{4}-\d{2}-\d{2})", text, re.M)
        assert dates == sorted(dates, reverse=True), (
            f"SESSION STATE blocks are no longer newest-first: {dates[:5]}")


#: A figure that reports a test run: "6658 passed", "3 failed", "0 failed".
#: A suite figure. THOUSANDS SEPARATORS INCLUDED, because "7,237 passed"
#: matched as "237 passed" under the previous pattern -- the count was
#: unaffected, since this is only ever used to ask HOW MANY figures a block
#: quotes, but a matcher that reads 7,237 as 237 is one consumer away from
#: reporting the wrong number, and that is the defect class this session
#: found 16 times.
_SUITE_FIGURE = re.compile(r"\b\d{1,3}(?:,\d{3})*\s+(?:passed|failed)\b")

#: Anything that looks like it names a committed producer.
_NAMES_A_SCRIPT = re.compile(r"scripts/[\w./-]+\.py")

#: A COMPLETE, re-runnable pytest invocation -- interpreter, `-m pytest`, and at
#: least one further argument. Added 2026-09-17 by panel review of task A23.
#:
#: WHY, and it is a measurement rather than a preference. The rule below is
#: right: a suite figure a reader cannot re-run can go false without anything
#: noticing. Its PATTERN was wrong, because it accepted only `scripts/<name>.py`
#: and THE FULL SUITE HAS NO SUCH PRODUCER -- what produces "7,493 passed" is a
#: pytest invocation. The guard was therefore UNSATISFIABLE by honest prose
#: about the suite, and the only ways to green were to cite a script that did
#: not produce the number, or to stop reporting the suite. Both are worse than
#: the defect this rule exists to catch, and the first is a fabricated citation.
#:
#: It was not hypothetical. This guard was RED at HEAD on 2026-09-17: the newest
#: SESSION STATE block reported the suite green at `a2999f1` and named no
#: producer at all, so task A23's own DONE marker stood on a failing test.
#: `scripts/suite_figure_producers_2026-09-17.py` counts the forms actually used
#: across the whole file -- 4 of 20 suite-figure paragraphs are backed by a
#: pytest command against 3 by a `scripts/*.py` -- so the command form is the
#: one the record already uses, including in the blocks of 2026-09-08 and
#: 2026-09-06 that the shipped pattern would call offenders.
#:
#: THIS IS A WIDENING AND NOT A LOOSENING, and the boundary is kept sharp: a
#: bare mention of the word "pytest" does NOT match, and neither does running
#: prose -- the token after `pytest` must LOOK like a target or a flag (a path,
#: a `.py`, or a `-`). The first attempt used `\S+` and the negative control
#: below caught it inside the hour: "We ran python3 -m pytest and it passed"
#: satisfied it. The controls that pin the boundary live in
#: bench/tests/test_suite_figure_producer_forms_2026-09-17.py.
_NAMES_A_PYTEST_RUN = re.compile(r"python3?\s+-m\s+pytest\s+(?:-\S+|\S*/\S*|\S+\.py)")

#: Either accepted form. The rule is "the figure travels with something a reader
#: can re-run", never "the figure travels with a file under scripts/".
_NAMES_A_PRODUCER = re.compile(
    _NAMES_A_SCRIPT.pattern + "|" + _NAMES_A_PYTEST_RUN.pattern)


def _newest_block_text() -> str:
    """The newest SESSION STATE block's body, up to the next one."""
    text = RECOVERY.read_text(encoding="utf-8")
    heads = [m.start() for m in
             re.finditer(r"^## SESSION STATE — ", text, re.M)]
    assert heads, "no SESSION STATE block at all"
    start = heads[0]
    end = heads[1] if len(heads) > 1 else len(text)
    return text[start:end]


class TestASuiteFigureNamesItsProducer:
    """`measured-rate-travels-with-its-script`, applied to the 1 document a
    post-compaction reader trusts most."""

    def test_the_block_carries_suite_figures_at_all(self):
        """ANTI-VACUITY. A block with no figures would pass the next test
        without the rule ever being exercised."""
        figures = _SUITE_FIGURE.findall(_newest_block_text())
        assert len(figures) >= 2, (
            f"the newest SESSION STATE block carries {len(figures)} suite "
            f"figure(s); if it has genuinely stopped quoting any, delete this "
            f"pair of tests deliberately rather than letting them pass on "
            f"nothing")

    def test_every_paragraph_with_a_suite_figure_names_a_script(self):
        """The paragraph is the unit, not the sentence: a figure and its
        producer are routinely a sentence apart, and demanding them in one
        sentence would fire on correct prose."""
        block = _newest_block_text()
        offenders = []
        for para in re.split(r"\n\s*\n", block):
            if not _SUITE_FIGURE.search(para):
                continue
            if not _NAMES_A_PRODUCER.search(para):
                offenders.append(_SUITE_FIGURE.search(para).group(0)
                                 + " -- " + para.strip()[:110])
        assert not offenders, (
            "a suite figure in the newest SESSION STATE block names no "
            "producer (a scripts/*.py or a complete pytest command), so a "
            "reader cannot re-run it and it can go "
            "false without anything noticing -- which is what happened to "
            "\"6658 passed ... EXIT 0\" on 2026-09-11:\n  "
            + "\n  ".join(offenders))
