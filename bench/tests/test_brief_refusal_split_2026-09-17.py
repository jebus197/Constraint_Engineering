"""`brief_archive_refusal_rate_2026-09-10.py --split DATE` prints what task 5.2 needs.

PANEL ROUND 16, 2026-09-17. Task 5.2 quoted "49 of 49" briefs refused before the
format ruling and "0 of 7" after, and no committed script printed either. The
committed producer printed 1 aggregate, and its default mode also re-executes
declared figures, which drift after dispatch, so the aggregate mixes 2 causes.
`--split` reports the SHAPE checks alone on each side of a date.

bench/logs/ is gitignored, so the real archive is absent from any clone. These
tests run a copy of the script against a synthetic archive in tmp_path, whose
answer is known by construction: 2 malformed briefs dated before the cut (1 ISO,
1 compact), 2 conforming briefs dated on and after it, and 1 undated malformed
brief that must fall in neither group.
"""
from __future__ import annotations

import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "brief_archive_refusal_rate_2026-09-10.py"
VALIDATOR = REPO / "scripts" / "panel_brief_validate.py"

CONFORMING = (
    "# Brief 2026-09-17\n\n"
    "Review `scripts/thing.py`. Each seat must run it and execute the tests.\n"
    "Use gamma, the depletion exponent, to say whether findings are drying up, "
    "and report any rate with its interval and the script that produced it.\n"
    "The artefact is small, so the review should be short, but every claim must "
    "rest on command output rather than on reading the source.\n"
    "Propose a fix, and an executed falsifier with its output.\n"
    # The delivery rule became the validator's 8th check on 2026-09-17 (task P4),
    # so a fixture brief that omits it is no longer a VALID brief.
    "Write each fix into the sandbox repository tree at its real path, so it is delivered as a file rather than left in prose.\n"
    "State what would refute your answer.\n"
    "## Output\n\n- verdict\n- fix\n- falsifier_result\n\n"
    "Stop at diminishing returns.\n")
MALFORMED = "Please review the code and tell me what you think.\n"


def _archive(tmp_path: Path) -> Path:
    (tmp_path / "scripts").mkdir()
    shutil.copy(SCRIPT, tmp_path / "scripts" / SCRIPT.name)
    shutil.copy(VALIDATOR, tmp_path / "scripts" / VALIDATOR.name)
    logs = tmp_path / "bench" / "logs"
    for rel, text in (("panel_round1_2026-09-01/BRIEF.md", MALFORMED),
                      ("baseline_confer_20260331/BRIEF.md", MALFORMED),
                      ("panel_round5_2026-09-09/BRIEF.md", CONFORMING),
                      ("panel_round9_2026-09-10/BRIEF.md", CONFORMING),
                      ("scratch_review/BRIEF.md", MALFORMED)):
        (logs / rel).parent.mkdir(parents=True)
        (logs / rel).write_text(text, encoding="utf-8")
    return tmp_path


def _wilson(k: int, n: int) -> tuple[float, float]:
    z = 1.959963984540054
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, c - h), min(1.0, c + h)


def _run(tree: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(tree / "scripts" / SCRIPT.name), *args],
                          cwd=tree, capture_output=True, text=True, timeout=300)


def test_the_split_reports_each_side_of_the_ruling(tmp_path):
    tree = _archive(tmp_path)
    r = _run(tree, "--split", "2026-09-09")
    assert r.returncode == 0, r.stderr
    out = r.stdout
    assert "declared figures NOT re-executed" in out, out
    assert "archived briefs: 5" in out, out
    m = re.search(r"dated before 2026-09-09\s*: refused 2 of 2 = 100\.0000%, "
                  r"failing (\d+) to (\d+) check\(s\)", out)
    assert m, out
    import importlib.util
    spec = importlib.util.spec_from_file_location("validator_direct", VALIDATOR)
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    expected = len(v.validate(MALFORMED))
    assert expected >= 1 and not v.validate(CONFORMING), "the fixture briefs are mis-built"
    assert (int(m.group(1)), int(m.group(2))) == (expected, expected), (m.groups(), expected)
    assert re.search(r"dated on or after 2026-09-09\s*: refused 0 of 2 = 0\.0000%\n", out), out
    assert re.search(r"undated, in neither group\s*: 1 \['scratch_review/BRIEF\.md'\]", out), out


def test_the_printed_intervals_match_an_independent_closed_form(tmp_path):
    tree = _archive(tmp_path)
    out = _run(tree, "--split", "2026-09-09").stdout
    got = [tuple(float(x) / 100 for x in pair)
           for pair in re.findall(r"Wilson 95%\s*: \[([\d.]+)%, ([\d.]+)%\]", out)]
    assert len(got) == 2, out
    for (lo, hi), (k, n) in zip(got, ((2, 2), (0, 2))):
        wl, wh = _wilson(k, n)
        assert abs(lo - wl) < 1e-6 and abs(hi - wh) < 1e-6, ((lo, hi), (wl, wh))


def test_the_split_does_not_run_declared_figures(tmp_path):
    """A brief declaring a figure whose script is absent is refused by the default
    mode and must NOT be refused by the shape-only split."""
    tree = _archive(tmp_path)
    brief = tree / "bench" / "logs" / "panel_round9_2026-09-10" / "BRIEF.md"
    brief.write_text(CONFORMING + "\n<!-- figure: a count | scripts/absent.py | 7 -->\n",
                     encoding="utf-8")
    split = _run(tree, "--split", "2026-09-09").stdout
    assert re.search(r"dated on or after 2026-09-09\s*: refused 0 of 2", split), split
    default = _run(tree)
    assert "REFUSED by the committed validator: 4" in default.stdout, default.stdout


def test_a_date_is_read_from_either_spelling():
    import importlib.util
    spec = importlib.util.spec_from_file_location("refusal_rate", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    assert m.brief_date("panel_round16_2026-09-17/BRIEF.md") == "2026-09-17"
    assert m.brief_date("baseline_confer_run10_20260403/BRIEF.md") == "2026-04-03"
    assert m.brief_date("exp_20261399/BRIEF.md") is None, "an invalid month was accepted"
    assert m.brief_date("notes/BRIEF.md") is None


def test_help_and_a_bad_date(tmp_path):
    tree = _archive(tmp_path)
    h = _run(tree, "--help")
    assert h.returncode == 0 and h.stdout.startswith("usage:"), h
    assert "archived briefs" not in h.stdout
    bad = _run(tree, "--split", "2026-13-01")
    assert bad.returncode == 2 and "YYYY-MM-DD" in bad.stderr, bad
