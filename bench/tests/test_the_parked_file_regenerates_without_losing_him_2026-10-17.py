"""The parked-file regenerator may not lose, bury or paraphrase anything of his.

Task B3, on his ruling of 2026-10-16: *"Build it and implement it."* Nothing
removed an item from `experimental_notes/PARKED_FOR_THE_FOUNDER.md` when its
entry closed, so settled business accumulated in front of the live items --
measured at 14 of 21 settled, 66.6667%, Wilson [45.3735%, 82.8052%], by
`scripts/has_he_already_ruled_on_the_parked_2026-10-13.py`.

FOUR DEFECTS WERE FOUND IN THE REGENERATOR ITSELF BEFORE IT EVER RAN, and each
one is pinned here, because every one of them would have damaged the file it was
written to repair:

1. IT CARRIED ITS OWN CLASSIFICATION and disagreed with the measurement on 5 of
   21 items IN BOTH DIRECTIONS. Two of those disagreements would have moved a
   LIVE item into the settled section -- the burial, performed by the cure.
2. IT PARAPHRASED HIM INSIDE DOUBLE QUOTATION MARKS, writing "rather than bother
   me with them now?" where he wrote "unless there is something that clearly
   warrants my immediate attention?". Double quotes are verbatim under his
   convention.
3. ITS POSTCONDITION COUNTED HEADINGS, so a render defect that truncated a body
   passed while losing the substance -- measured at 33.3029% of the file and the
   text of all 7 live items, by
   `scripts/would_the_count_only_postcondition_have_caught_it_2026-10-17.py`.
4. IT DROPPED 3 SENTENCES of the preamble's substance and hard-coded a
   breakdown that was wrong the moment an item moved.

Every assertion below EXECUTES the regenerator against a copy of the real file
rather than reading its source, because a test that reads source text only
proves the module describes itself consistently.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import shutil
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
GEN = REPO / "scripts" / "regenerate_the_parked_file_2026-10-17.py"
MEASURE = REPO / "scripts" / "has_he_already_ruled_on_the_parked_2026-10-13.py"
PARKED = REPO / "experimental_notes" / "PARKED_FOR_THE_FOUNDER.md"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def gen():
    return _load(GEN, "parked_regen_under_test")


def test_the_regenerator_and_the_measurement_cannot_disagree(gen):
    """The settled set is the measurement's closed set, item for item.

    NOT a count: a count cannot say WHICH items moved, and the first draft's
    error was a swap -- 2 items in and 2 out -- which a count of 14 would have
    reported as agreement. Compared as SETS of headings.
    """
    m = gen._measure()
    live, settled = gen.classify(m)
    closed, ruled, undecided, _ = m.classify_items(
        m.parked_items(), m.task_states(), m.annotation_text(m.annotations()))
    assert {h for h, _, _ in settled} == {h for h, _ in closed}
    assert {h for h, _, _ in live} == {h for h, _ in undecided} | {
        h for h, _ in ruled}
    # and no item is in both halves, which would duplicate his text
    assert not ({h for h, _, _ in settled} & {h for h, _, _ in live})


def test_an_item_he_has_ruled_on_stays_live(gen, monkeypatch):
    """A ruling GIVEN is not work DONE, so a ruled item may not be buried.

    He ruled "restart it" on the zero-plant control on the 7th of August and
    again on the 6th of September, and it was still outstanding 70 days later.
    The measurement treats `ruled` as settled because it asks "has he dealt with
    this?"; the regenerator must not, because it asks "may this leave his
    attention?". `ruled` is currently 0 of 21, so this property is INVISIBLE to
    the live data and is tested with injected data instead -- an empty category
    is exactly where a divergence hides.
    """
    m = gen._measure()
    real = m.parked_items()
    assert real, "no parked items; the fixture is void"
    victim = real[0][0]

    def fake(items, states, ann_text):
        return ([], [(victim, [("2026-08-07", "A1", "restart it")])],
                [(h, []) for h, _ in items if h != victim], [])

    monkeypatch.setattr(m, "classify_items", fake)
    live, settled = gen.classify(m)
    assert victim in {h for h, _, _ in live}
    assert victim not in {h for h, _, _ in settled}
    why = {h: w for h, _, w in live}[victim]
    assert "RULED BY HIM" in why and "2026-08-07" in why


def test_his_instruction_is_his_words_not_a_paraphrase(gen):
    """The quotation is the file's own, character for character.

    The first draft retyped it and changed its meaning. This compares the
    constant against the live file, so a future edit to either side that
    paraphrases him turns this red.
    """
    line = [l for l in PARKED.read_text(encoding="utf-8").splitlines()
            if "Opened 2026-09-10 on his instruction" in l]
    assert len(line) == 1, "the preamble's attribution line moved or doubled"
    quoted = re.search(r'\*"(.+)"\*', line[0]).group(1)
    assert gen.HIS_INSTRUCTION == quoted
    assert "clearly warrants my immediate attention" in gen.HIS_INSTRUCTION


def test_the_breakdown_is_derived_from_the_reasons(gen):
    """A moved item changes the sentence, because it is computed."""
    assert gen._breakdown([("h", "b", "the item's own heading says so")]) == \
        "1 by their own heading"
    with_task = gen._breakdown([("h", "b", "the item's own heading says so"),
                          ("i", "b", "task list: A8 is DONE")])
    assert "1 by their own heading" in with_task
    assert "1 naming task entries recorded DONE or WITHDRAWN" in with_task
    with_exec = gen._breakdown([("h", "b", "the item's own heading says so"),
                            ("i", "b", "task list: A8 is DONE"),
                            ("j", "b", "refuted by execution: x")])
    assert "1 refuted by execution" in with_exec
    # an unrecognised reason is COUNTED, not silently dropped
    assert "1 by another route" in gen._breakdown([("h", "b", "mystery")])
    assert gen._breakdown([]) == "none"


def _run_apply(tmp_path, gen_src=None, times=1):
    """Run the regenerator with --apply against a COPY of the real file."""
    sand = tmp_path / "repo"
    sand.mkdir()
    (sand / "scripts").mkdir()
    (sand / "experimental_notes").mkdir()
    # SYMLINK THE WHOLE SCRIPTS TREE rather than hand-picking imports. The first
    # version copied 2 files and the sandbox died on `_cli_help`, so the mutation
    # below never ran: the assertion went red on an ImportError instead of on the
    # defect, which proves nothing about the postcondition. Only the 2 files
    # under test are real copies, so a mutant can replace one.
    for src in (REPO / "scripts").iterdir():
        dst = sand / "scripts" / src.name
        if not dst.exists():
            dst.symlink_to(src)
    for p in (GEN, MEASURE):
        (sand / "scripts" / p.name).unlink(missing_ok=True)
        shutil.copy2(p, sand / "scripts" / p.name)
    if gen_src is not None:
        (sand / "scripts" / GEN.name).write_text(gen_src, encoding="utf-8")
    # EVERY note is symlinked and only the parked file is a real copy, so the
    # measurement reads the true master task list while the regenerator writes
    # to a sandbox. Hand-listing the notes it needs failed twice -- first on
    # `_cli_help`, then on the master task list -- and each failure turned the
    # mutation assertion red for the wrong reason.
    for src in (REPO / "experimental_notes").iterdir():
        dst = sand / "experimental_notes" / src.name
        if src.name != PARKED.name and not dst.exists():
            dst.symlink_to(src)
    shutil.copy2(PARKED, sand / "experimental_notes" / PARKED.name)
    for rel in ("bench", "resources", "docs", "hooks", "logs"):
        src = REPO / rel
        dst = sand / rel
        if src.exists() and not dst.exists():
            dst.symlink_to(src)
    runs = []
    for _ in range(times):
        runs.append(subprocess.run(
            [sys.executable, str(sand / "scripts" / GEN.name), "--apply"],
            capture_output=True, text=True, cwd=str(sand)))
    return (runs if times > 1 else runs[0]), \
        sand / "experimental_notes" / PARKED.name


def test_every_item_survives_a_real_apply(tmp_path):
    """Run it for real on a copy: nothing lost, every body verbatim."""
    before = PARKED.read_text(encoding="utf-8")
    r, out = _run_apply(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "items preserved, bodies verbatim" in r.stdout
    m = _load(MEASURE, "parked_measure_check")
    n_before = len(re.findall(r"^## ", before, flags=re.M))
    after_text = out.read_text(encoding="utf-8")
    assert len(re.findall(r"^## ", after_text, flags=re.M)) == n_before
    # HIS WORDS, not a count: every original body appears verbatim.
    #
    # ★ THE BODY MUST STOP AT THE SECTION DIVIDER. Corrected 2026-10-30. A
    # split on `^## ` runs to the NEXT `## `, so the last item of the live
    # section swallowed the `---` divider, the `# Settled` header and that
    # header's own ITEM COUNT. The assertion then failed whenever the settled
    # count changed, reporting "body lost" for an item that was present in
    # full -- a guard accusing correct content, and the same boundary defect
    # repaired in `end_of_entries` earlier the same day. Verified by diffing
    # the one failing body: the only difference was the swallowed header.
    for p in re.split(r"^## ", before, flags=re.M)[1:]:
        tail = "\n".join(p.splitlines()[1:])
        body = re.split(r"^(?:---\s*$|# )", tail, flags=re.M)[0].strip()
        if body:
            assert body in after_text, f"body lost: {p.splitlines()[0][:70]}"


def test_the_body_postcondition_goes_red_when_a_body_is_dropped(tmp_path):
    """MUTATION. Truncate a body in `render` and the run must REFUSE.

    This is the assertion that proves the postcondition is not decoration, and
    the claim is MEASURED rather than asserted. Reverting to the count-only
    postcondition and applying this same mutation,
    `scripts/would_the_count_only_postcondition_have_caught_it_2026-10-17.py`
    reports exit 0 and the words "all preserved" while losing the text of 7 of
    21 items, 10,929 of 32,817 characters, 33.3029%. THE 7 ARE EXACTLY THE LIVE
    ITEMS -- the ones still needing him -- because the mutation truncates the
    live loop's bodies. The replacement refuses with exit 2 and names all 7.
    """
    src = GEN.read_text(encoding="utf-8")
    mutant = src.replace("        out.append(body.rstrip())\n"
                         "        out.append(\"\")\n"
                         "    out += [\"---\", \"\",",
                         "        out.append(body.rstrip()[:5])\n"
                         "        out.append(\"\")\n"
                         "    out += [\"---\", \"\",")
    assert mutant != src, "the mutation did not apply; it proves nothing"
    r, _ = _run_apply(tmp_path, gen_src=mutant)
    assert r.returncode == 2, (
        "a truncated body was accepted:\n" + r.stdout + r.stderr)
    assert "BODIES ALTERED" in r.stdout


def test_the_regenerator_refuses_when_the_file_is_missing(tmp_path):
    """It must not CREATE the file from nothing; absence is a fault to report."""
    sand = tmp_path / "bare"
    (sand / "scripts").mkdir(parents=True)
    (sand / "experimental_notes").mkdir(parents=True)
    for src in (REPO / "scripts").iterdir():
        dst = sand / "scripts" / src.name
        if not dst.exists():
            dst.symlink_to(src)
    for p in (GEN, MEASURE):
        (sand / "scripts" / p.name).unlink(missing_ok=True)
        shutil.copy2(p, sand / "scripts" / p.name)
    r = subprocess.run([sys.executable, str(sand / "scripts" / GEN.name),
                        "--apply"], capture_output=True, text=True,
                       cwd=str(sand))
    assert r.returncode == 2
    assert "does not exist" in r.stdout

def test_regenerating_twice_changes_nothing_but_the_timestamp(tmp_path):
    """IDEMPOTENCE. The second run must not add to the first run's output.

    THIS IS THE ASSERTION THE FIRST VERSION LACKED, and the defect it would have
    shipped was found by executing --apply a second time rather than by reading
    the code. The parser gives the LAST LIVE ITEM a body that absorbs everything
    up to the next "## ", which includes the separator and the settled section's
    own heading. So run 2 re-emitted both: the file came back with 28 `*SETTLED:`
    lines for 14 items and 2 copies of the settled heading, and every further run
    would have added another. Run 1 looked perfect. Committing after one run
    would have shipped a file that grew on every regeneration.
    """
    runs, out = _run_apply(tmp_path, times=3)
    for n, r in enumerate(runs, 1):
        assert r.returncode == 0, f"run {n}:\n{r.stdout}{r.stderr}"
        assert "items preserved, bodies verbatim" in r.stdout, f"run {n}"
    text = out.read_text(encoding="utf-8")
    # THE STRUCTURE MUST NOT GROW. Counted, because the growth was silent.
    assert text.count("\n# Settled — kept for the record") == 1
    assert len(re.findall(r"^---\s*$", text, flags=re.M)) == 2
    settled_lines = len(re.findall(r"^\*SETTLED:", text, flags=re.M))
    n_settled = int(re.search(r"# Settled — kept for the record, not for his "
                              r"attention \((\d+)\)", text).group(1))
    assert settled_lines == n_settled, (
        f"{settled_lines} reason lines for {n_settled} settled items")
    assert len(re.findall(r"^## ", text, flags=re.M)) == \
        len(re.findall(r"^## ", PARKED.read_text(encoding="utf-8"), flags=re.M))


def test_a_previous_runs_own_lines_are_stripped_not_duplicated(tmp_path, gen):
    """`strip_own_output` removes this script's marks and nothing of his."""
    his = "He wrote this and it must survive. --- and a stray rule above."
    body = ("*SETTLED: task list: A8 is DONE.*\n" + his + "\n\n---\n\n"
            "# Settled — kept for the record, not for his attention (14)\n\n"
            "Each of these was parked and has since been settled. They are "
            "listed with the reason so the decision remains auditable.\n")
    got = gen.strip_own_output(body)
    assert his in got
    assert "*SETTLED:" not in got
    assert "# Settled — kept" not in got
    assert "Each of these was parked" not in got
    # IDEMPOTENT ITSELF: stripping twice is stripping once.
    assert gen.strip_own_output(got) == got
    # AND IT LEAVES A CLEAN BODY ALONE.
    clean = "Just his words, with a --- rule inside them.\nAnd a second line."
    assert gen.strip_own_output(clean) == clean


def test_a_newly_parked_item_is_not_buried_in_the_settled_section(tmp_path,
                                                                  monkeypatch):
    """`blocker_triage.park` must insert AHEAD of the settled section.

    The end of this file used to be the live queue; since the regeneration
    landed it is the archive. A plain append therefore buries each newly parked
    item on arrival -- task B3's defect reproduced by a different route, in the
    one script that writes to the file besides the regenerator. Found by tracing
    what else writes here, and pinned by CALLING `park` rather than reading it.
    """
    triage = _load(REPO / "scripts" / "blocker_triage.py", "triage_under_test")
    sand = tmp_path / "PARKED.md"
    shutil.copy2(PARKED, sand)
    text = sand.read_text(encoding="utf-8")
    assert "# Settled — kept for the record" in text, (
        "the fixture is not a regenerated file; this test would be vacuous")
    monkeypatch.setattr(triage, "PARKED", sand)
    out = triage.park("A brand new question that needs him",
                      "Its detail.", stamp="2026-10-17T13:30:00+01:00")
    assert out == sand
    after = sand.read_text(encoding="utf-8")
    where_item = after.index("## A brand new question that needs him")
    where_settled = after.index("# Settled — kept for the record")
    assert where_item < where_settled, "a new item landed inside the archive"
    # AND THE ARCHIVE IS UNTOUCHED: every settled heading still follows it.
    assert after.count("# Settled — kept for the record") == 1
    assert after.count("## A brand new question that needs him") == 1
    # RE-PARKING THE SAME TITLE STILL ADDS NOTHING.
    assert triage.park("A brand new question that needs him", "Its detail.",
                       stamp="2026-10-17T13:31:00+01:00") is None
    assert sand.read_text(encoding="utf-8").count(
        "## A brand new question that needs him") == 1
