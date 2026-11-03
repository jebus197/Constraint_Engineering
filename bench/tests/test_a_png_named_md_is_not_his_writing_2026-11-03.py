"""An 11 MB PNG wearing a `.md` extension returned 780 annotations he never wrote.

THE DEFECT. `Google Search Discussion on severity- 2026-09-28_10-28.md` in his
responses folder is a PNG image: it opens `\x89PNG`, `IHDR`, `IDAT`. The reader's
allow list `TEXT_SUFFIXES = {.txt, .rtf, .md}` accepted it on its EXTENSION, the
Mac OS Roman decoder decoded all 11,076,291 bytes without error because that
codec maps every byte, and 780 of the resulting 249,610 lines began with `#`. So
the reader reported 780 rulings of his that do not exist -- 0.481779 of the whole
1,619-annotation corpus -- and 3 guards went red demanding verdict rows for them.

IT ALSO TOOK EVERY COMMIT WITH IT. `context_for` re-read and re-split that file
once per annotation, so the reader went from 3.576 s to 684.25 s and 2 guards
that shell out to it died on the 300 s timeout. The timeout MASKED the 780: at
HEAD the tests could not reach the assertion that would have reported them.

THE 4TH PATCH OF THE SAME SHAPE. `.DS_Store` was excluded by name, Word's `~$`
lock files by prefix, and a `.zip` that returned 65 lines of compressed binary
produced the extension allow list on 2026-10-20 -- recorded in the reader as
"AN EXCLUSION LIST CANNOT HOLD. The ALLOW list is decidable." An extension is a
claim a file makes about itself, so the allow list is decidable and still wrong.
`is_binary_file` reads the bytes.

WHY IT CANNOT LOSE A VERDICT OF HIS. Every discriminator on PROSE SHAPE tried on
this folder was measured and refuted in 2026-10-17, losing real verdicts
including "Verdict: y". This asks whether the file is TEXT AT ALL: 0 of his
legitimate .txt and .md files carry a NUL byte, and an A/B in one process shows
exactly 780 annotations removed, all 780 from the PNG, 0 from any other file,
with all 131 of his markers intact.
"""
from __future__ import annotations

import importlib.util
import pathlib
import time

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
READER = REPO / "scripts" / "read_founder_responses_2026-10-11.py"
PNG_NAMED_MD = "Google Search Discussion on severity- 2026-09-28_10-28.md"


def _load():
    spec = importlib.util.spec_from_file_location("rfr_png_guard", READER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def R():
    return _load()


class TestTheBytesDecideNotTheName:
    def test_the_predicate_exists_and_is_reached(self, R):
        """An addition nothing calls is not additive."""
        assert callable(R.is_binary_file)
        src = READER.read_text()
        assert "and not is_binary_file(path)" in src, (
            "is_binary_file must be WIRED INTO is_one_of_his_annotated_responses; "
            "a predicate no selector calls decides nothing")

    def test_a_png_is_binary_whatever_it_is_called(self, R, tmp_path):
        p = tmp_path / "looks_like_his_note.md"
        p.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 64 + b"# not a heading")
        assert R.is_binary_file(p)
        assert not R.is_one_of_his_annotated_responses(p)

    def test_a_pdf_named_md_is_caught_though_it_has_no_early_nul(self, R, tmp_path):
        """The reason the magic list is not redundant with the NUL test.

        2 of the binaries in his folder are PDFs with no NUL in the first 4 KiB,
        so a NUL-only test would miss a PDF saved as `.md` -- the same accident
        that produced the PNG.
        """
        p = tmp_path / "note.md"
        p.write_bytes(b"%PDF-1.7\n" + b"1 0 obj\n" * 200)
        assert b"\x00" not in p.read_bytes()[:4096], "this case must have NO nul"
        assert R.is_binary_file(p)

    def test_plain_text_of_his_is_not_binary(self, R, tmp_path):
        p = tmp_path / "Morning_Report_2026-11-03.txt"
        p.write_text("# I accept your recommendation. fr\n\nSome report prose.\n")
        assert not R.is_binary_file(p)
        assert R.is_one_of_his_annotated_responses(p)

    def test_an_unreadable_file_is_a_reported_gap_not_a_silent_skip(self, R, tmp_path):
        """`is_binary_file` returns False on an OSError on purpose: an unreadable
        file must reach `unreadable_but_annotated`, which is loud."""
        missing = tmp_path / "gone.txt"
        assert R.is_binary_file(missing) is False


class TestTheLiveFolder:
    @pytest.mark.skipif(not (pathlib.Path(
        "/Users/georgejackson/Developer_Projects/Responses") / PNG_NAMED_MD).is_file(),
        reason="his folder does not hold that file on this machine")
    def test_the_actual_offender_is_excluded(self, R):
        p = R.RESPONSES / PNG_NAMED_MD
        assert p.open("rb").read(4).startswith(b"\x89PNG"), "premise: it is a PNG"
        assert R.is_binary_file(p)
        assert not R.is_one_of_his_annotated_responses(p)

    def test_the_exclusion_is_reported_by_name(self, R):
        """A silent skip is the defect this reader exists to prevent."""
        rows = R.binaries_wearing_a_text_extension()
        names = {r["file"] for r in rows}
        if (R.RESPONSES / PNG_NAMED_MD).is_file():
            assert PNG_NAMED_MD in names
            row = next(r for r in rows if r["file"] == PNG_NAMED_MD)
            assert row["signature"].startswith("89504e47")
            assert row["bytes"] > 1_000_000

    def test_no_annotation_is_attributed_to_the_png(self, R):
        anns = R.annotations(None, None)
        assert [a for a in anns if a.get("file") == PNG_NAMED_MD] == []

    def test_removing_the_check_restores_exactly_780_and_nothing_else(self, R):
        """THE DIRECTION THAT MATTERS: the check must remove the PNG's lines and
        NOT ONE WORD OF HIS. Executed as an A/B, not reasoned about."""
        off = _load()
        off.is_binary_file = lambda p, probe=4096: False
        before = off.annotations(None, None)
        after = R.annotations(None, None)

        def key(a):
            return (str(a.get("file")), a.get("line_index"))

        lost = {key(a) for a in before} - {key(a) for a in after}
        assert lost, "premise: the check removes something, or this proves nothing"
        from_other = {k for k in lost if k[0] != PNG_NAMED_MD}
        assert from_other == set(), (
            f"the check drops his real writing from {sorted({k[0] for k in from_other})}")
        assert {key(a) for a in after} - {key(a) for a in before} == set()


class TestTheDecodeIsCachedAndStillCorrect:
    def test_lines_of_equals_a_fresh_split(self, R, tmp_path):
        p = tmp_path / "a.txt"
        p.write_text("one\ntwo\nthree\n")
        assert list(R.lines_of(p)) == R.read_any(p).splitlines()

    def test_a_file_edited_between_reads_is_re_read(self, R, tmp_path):
        """The one way a cache is WRONG rather than merely stale."""
        p = tmp_path / "b.txt"
        p.write_text("one\ntwo\n")
        first = R.lines_of(p)
        time.sleep(0.01)
        p.write_text("ONE\ntwo\n")               # SAME byte length
        assert len(p.read_text()) == 8, "premise: the edit preserves the size"
        assert R.lines_of(p) != first, (
            "a same-size edit must still invalidate: the key carries mtime_ns")

    def test_the_cache_returns_a_tuple_so_a_caller_cannot_corrupt_it(self, R, tmp_path):
        p = tmp_path / "c.txt"
        p.write_text("x\ny\n")
        assert isinstance(R.lines_of(p), tuple)

    def test_the_escape_hatch_the_docstring_promises_exists(self, R):
        assert callable(R.read_any.cache_clear)
        assert callable(R.lines_of.cache_clear)
        R.read_any.cache_clear()
        R.lines_of.cache_clear()

    def test_context_for_does_not_resplit_the_file_once_per_annotation(
            self, R, tmp_path, monkeypatch):
        """A REGRESSION GUARD THAT DOES NOT NEED A LIVE DEFECT TO BITE, AND THAT
        EXERCISES THE DECIDING LAYER.

        2 earlier attempts at this guard were BLIND, both for reasons worth
        recording. The wall-clock test below went vacuous the moment the PNG was
        excluded: with no 11 MB file left in his folder, reverting the fix made
        it 0.0x slower and all 14 tests stayed green. The second attempt timed
        `lines_of` against `read_any(...).splitlines()` directly, which is true
        of the 2 helpers whatever `context_for` calls -- it tested the property
        instead of the call site.

        So this one calls `context_for` itself, over its own large file, with
        `RESPONSES` pointed at a temporary folder. 684.25 s of the pre-fix
        reader was `splitlines()` on 1 file, 780 times.
        """
        n = 240
        lines = []
        for i in range(150_000):
            lines.append(f"# his annotation {i} goes here. fr" if i % 250 == 0
                         else f"line {i} of a long generated report")
        big = tmp_path / "His_Long_Report_2026-11-03.txt"
        big.write_text("\n".join(lines) + "\n")
        monkeypatch.setattr(R, "RESPONSES", tmp_path)
        anns = [{"file": big.name, "line_index": i * 250} for i in range(n)]

        R.lines_of.cache_clear()
        R.read_any.cache_clear()
        t0 = time.perf_counter()
        got = [R.context_for(a, before=6) for a in anns]
        el = time.perf_counter() - t0

        assert all(got), "premise: context_for must actually return lines here"
        per = el / n
        # ★ THE BOUND IS CALIBRATED, NOT GUESSED. A first bound of 10 ms sat
        # ABOVE BOTH routes and the mutation stayed green -- the 3rd blind
        # predicate on this one surface, which is where the project's rule says
        # to stop and measure. Measured on 2026-11-03 over this exact file at
        # 150,000 lines: 0.0310 ms per annotation cached against 4.8563 ms
        # uncached, a separation of 157x. 0.80 ms sits 26x above the cached cost
        # and 6x below the uncached one, so it catches the regression without
        # flaking on a loaded machine. (60,000 lines gives 0.0196 vs 1.8428,
        # 94x; 250,000 gives 0.0457 vs 8.3891, 184x.)
        assert per < 0.00080, (
            f"context_for cost {per*1000:.4f} ms per annotation over a "
            f"{big.stat().st_size/1e6:.1f} MB file ({el:.2f} s for {n}). The "
            f"cached route measures 0.0310 ms and the per-annotation re-split "
            f"4.8563 ms, so anything above 0.80 ms is the 684.25 s regression "
            f"that killed every commit")

    def test_the_reader_is_fast_enough_for_a_guard_to_shell_out_to_it(self, R):
        """The regression that blocked every commit was WALL CLOCK, so the guard
        against it has to be wall clock. 60 s is 8.8x the measured 6.80 s and
        0.2x the 300 s timeout that killed it, so it is loose enough not to
        flake and tight enough to catch a return to quadratic re-reading."""
        import subprocess
        import sys
        t0 = time.perf_counter()
        r = subprocess.run([sys.executable, str(READER), "--since", "2026-10-30",
                            "--json"], capture_output=True, text=True,
                           cwd=str(REPO), timeout=180)
        el = time.perf_counter() - t0
        assert r.returncode == 0, r.stderr[-800:]
        assert el < 60.0, (
            f"the reader took {el:.1f} s; it was 684.25 s before the decode and "
            f"split were cached, which killed 2 guards on a 300 s timeout")
