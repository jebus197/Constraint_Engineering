"""Running the tests must not write into bench/logs/.

`bench/logs/` is archival: it is the record of what the panel actually did, it
is never edited, and corrections are filed as sidecars beside it rather than
applied to it. That rule was being broken by the test suite itself.

`bench/immune_agents.py` attaches a FileHandler to `bench/logs/immune_pipeline.log`
at import time. Every pytest run imports it, so every pytest run appended
synthetic pipeline output — `TestModel_F001`, toy targets, fixture findings —
into the same file that records real experiment history. 332 such lines had
accumulated, continuously since 2026-05-15. A reader of the archive cannot
separate fixture noise from run history without inspecting model names line by
line, and nothing in the file announces that any of it is synthetic.

Found 2026-07-31 when `git status` showed the archive dirty after a test run
that was supposed to have touched nothing. The existing pollution is left in
place: those lines sit interleaved with genuine records from the halted control
run, and rewriting an archive to tidy it is the thing the rule forbids.
"""
from __future__ import annotations

import os
import subprocess
import sys
import ast
from pathlib import Path
from bench.repo_paths import line_mentions_archive_path

_root = Path(__file__).resolve().parents[2]
ARCHIVE = _root / "bench" / "logs"
PIPELINE_LOG = ARCHIVE / "immune_pipeline.log"


class TestTheArchiveStaysClean:
    def test_the_shadow_logger_does_not_target_the_archive_under_pytest(self):
        """The handler this process actually attached."""
        import logging

        import bench.immune_agents  # noqa: F401 — import is the point

        log = logging.getLogger("immune.pipeline")
        targets = [Path(h.baseFilename).resolve()
                   for h in log.handlers if hasattr(h, "baseFilename")]
        assert targets, "the shadow logger attached no file handler at all"
        inside = [t for t in targets if ARCHIVE.resolve() in t.parents]
        assert not inside, (
            f"a test run is writing into the archive: {inside}")

    def test_a_real_pipeline_import_leaves_the_archive_byte_identical(self):
        """End to end, in a fresh interpreter, exercising the logger for real.

        Byte length rather than mtime: a handler that opens the file in append
        mode touches mtime without writing, and that is harmless.
        """
        if not PIPELINE_LOG.exists():
            import pytest
            pytest.skip("no archive to protect on this machine")
        before = PIPELINE_LOG.stat().st_size

        script = (
            "import sys, logging\n"
            "sys.modules.setdefault('pytest', sys.modules['sys'])\n"  # pose as pytest
            "sys.path.insert(0, %r)\n"
            "import bench.immune_agents\n"
            "logging.getLogger('immune.pipeline').info('SYNTHETIC TEST LINE')\n"
            "logging.shutdown()\n" % str(_root)
        )
        subprocess.run([sys.executable, "-c", script], check=True,
                       capture_output=True, timeout=120,
                       env={**os.environ, "CDSFL_SHADOW_LOG_DIR": ""})

        assert PIPELINE_LOG.stat().st_size == before, (
            "a test-shaped process grew the archive — the redirect is not working")

    def test_the_override_still_lets_a_real_run_write_where_it_should(self):
        """The redirect must not break the logging a real experiment relies on."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            script = (
                "import sys, logging\n"
                "sys.modules.setdefault('pytest', sys.modules['sys'])\n"
                "sys.path.insert(0, %r)\n"
                "import bench.immune_agents\n"
                "logging.getLogger('immune.pipeline').info('DELIBERATE LINE')\n"
                "logging.shutdown()\n" % str(_root)
            )
            subprocess.run([sys.executable, "-c", script], check=True,
                           capture_output=True, timeout=120,
                           env={**os.environ, "CDSFL_SHADOW_LOG_DIR": tmp})
            written = list(Path(tmp).glob("immune_pipeline.log"))
            assert written, "the explicit override wrote nothing"
            assert "DELIBERATE LINE" in written[0].read_text(encoding="utf-8")


class TestNoTestWritesAnywhereInTheArchive:
    """Broader than the one log — nothing under bench/logs/ is a test's to write."""

    #: Calls that create, modify or remove something at a path.
    WRITERS = ("write_text", "write_bytes", "open", "mkdir", "unlink", "rmtree",
               "touch", "rename", "replace", "copy", "copytree")

    def test_no_test_file_names_a_path_inside_the_archive_for_writing(self):
        """PARSED, not scanned, and the reason is a false positive it produced.

        This was a substring test over each source line: if the line mentioned
        `bench/logs` and contained a writer's name anywhere, it was an offender.
        That cannot tell the write TARGET from the write CONTENT. Widening the
        archive definition to the shared `ARCHIVE_ROOTS` in task 6.4 made the
        difference visible immediately: `(git_repo / ".gitignore").write_text(
        "bench/results/\\n")` writes a .gitignore whose TEXT names an archive
        root, and the line-scan called it a write into the archive.

        So the receiver is parsed instead. `x.write_text(y)` is an offence when
        `x` names an archive path; what `y` contains is not this test's business.
        The archive definition itself still comes from `bench/repo_paths.py`, so
        there remains exactly 1 place that decides what an archive is."""
        offenders = []
        for path in sorted((_root / "bench" / "tests").glob("test_*.py")):
            if path.name == Path(__file__).name:
                continue
            text = path.read_text(encoding="utf-8")
            try:
                tree = ast.parse(text)
            except SyntaxError:  # pragma: no cover - a broken test file is its own alarm
                continue
            for node in ast.walk(tree):
                if not (isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Attribute)
                        and node.func.attr in self.WRITERS):
                    continue
                receiver = ast.get_source_segment(text, node.func.value) or ""
                if not line_mentions_archive_path(receiver):
                    continue
                line = text.splitlines()[node.lineno - 1].strip()
                offenders.append(f"{path.name}:{node.lineno}: {line[:90]}")
        assert not offenders, (
            "tests must read the archive, never write to it:\n  "
            + "\n  ".join(offenders))
