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
from pathlib import Path

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

    def test_no_test_file_names_a_path_inside_the_archive_for_writing(self):
        offenders = []
        for path in sorted((_root / "bench" / "tests").glob("test_*.py")):
            if path.name == Path(__file__).name:
                continue
            text = path.read_text(encoding="utf-8")
            for i, line in enumerate(text.splitlines(), 1):
                if "bench/logs" not in line and 'logs"' not in line:
                    continue
                if any(w in line for w in ("write_text(", "write_bytes(", "open(",
                                           "mkdir(", "unlink(", "rmtree(")):
                    offenders.append(f"{path.name}:{i}: {line.strip()[:90]}")
        assert not offenders, (
            "tests must read the archive, never write to it:\n  "
            + "\n  ".join(offenders))
