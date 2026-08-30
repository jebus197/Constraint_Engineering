"""Simulated-run artefacts must never wear a bare vendor name.

WHAT THIS PINS
--------------
Founder ruling 2026-08-08 amends the earlier simulated-agent naming rule.
Simulated panel members are named ``CC2-SIM``, ``Codex-SIM``, ``Gemini-SIM``,
``DeepSeek-SIM``, ``ChatGPT-SIM``. The ``-SIM`` suffix carries useful role
information, and it may never be dropped — not in labels, finding IDs, report
fields, log directories, notes or commit messages.

The risk the suffix creates is a summariser dropping it, which reproduces the
2026-08-04 provenance failure: a five-agent simulated bench was labelled with the
real panel's names, results were reported as though vendors had produced them, and
the same 24 hours contained a REAL five-model panel under the same five names. Two
panels in the record that a reader could not tell apart. A result attributed to a
model that never produced it is, downstream, indistinguishable from a fabricated
one.

THE VENDOR LIST IS DERIVED, NOT HARDCODED
-----------------------------------------
Tokens come from the panel roster table in ``.claude/CLAUDE.md`` (the "Model Confer
Dispatch (combinable)" table). A panel rotation therefore cannot silently defeat
this check — swap Gemini for Mistral in the roster and Mistral becomes guarded on
the next run. ``test_rotation_cannot_defeat_the_check`` proves that property
against a synthetic roster.

Derivation rule, per roster row: guard the command alias upper-cased and the first
word of the Model column, keeping tokens of three or more characters. On the
2026-05-10 roster that yields CC2, CGPT, Claude, Codex, Gemini, ChatGPT, DeepSeek —
a superset of the five mandated bases. The two-letter aliases (``cx``, ``ge``,
``ds``) are dropped deliberately: they are worth little (a summariser writes
"Gemini", not "ge") and they collide with ordinary text.

TWO MEASURED DESIGN DECISIONS, BOTH OF WHICH REFUTE THE OBVIOUS IMPLEMENTATION
------------------------------------------------------------------------------
1. **"Content mentions the word simulated" is NOT a usable predicate.** Measured
   2026-08-08: 108 files under ``bench/logs/`` contain that word, and essentially
   all of them are REAL panel runs in which a model wrote prose like "(Simulated)
   The defect is present…". Those runs legitimately carry bare vendor names in
   their own filenames (``round7_deepseek_*.json``, ``r1_gemini_*.json``), so a
   substring predicate would turn this guard red across the entire real archive on
   its first run, and the repair would be an exclusion list — i.e. a dead guard.
   The predicate here requires a STRUCTURAL self-declaration instead: a name
   marker, a ``SIM-x`` panel label, a ``-SIM`` suffix, a ``simulated_bench``
   reference, or an explicit ``"simulated": true``-style key. Measured against the
   same archive: zero false selections. ``test_prose_mention_is_not_a_simulated_
   artefact`` pins that so nobody later "fixes" the predicate into over-matching.

2. **A bare vendor token in free prose is NOT a violation; a vendor token in a
   LABEL POSITION is.** ``bench/tools/simulated_bench.py`` contains bare
   ``Claude``, ``Codex`` and ``Gemini`` — inside the docstring that explains the
   2026-08-04 failure. A free-text scan would go red on the institutional memory
   of the very rule it enforces, and the "fix" would be to delete the explanation.
   So violations are only raised where an identity actually gets attached: path
   segments, JSON values under identity keys, Python string literals bound to
   identity keywords / dict keys / names (via AST, so comments and docstrings are
   structurally invisible), and identity-shaped key/value or label constructs in
   other text.

KNOWN BOUNDARY, STATED RATHER THAN HIDDEN
-----------------------------------------
A simulated artefact that carries no marker at all is indistinguishable from a real
run and will not be scanned. That residual is inherent: real runs are *supposed* to
carry bare vendor names. It is bounded by ``bench/tools/simulated_bench.py`` being
in scope unconditionally, and by any file under a name-marked directory being in
scope.

FAILURE IS LOUD, INCLUDING THE FAILURE TO CHECK
-----------------------------------------------
An unparseable roster is a hard FAIL, never a skip — a guard that cannot derive
what it protects is blind, and a blind guard that passes is this project's
signature defect. An empty artefact set skips, but warns as well, so it surfaces
rather than reading as a pass.
"""

from __future__ import annotations

import ast
import json
import re
import sys
import warnings
from pathlib import Path
from typing import Any, Iterable, List, NamedTuple, Sequence, Set, Tuple

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ROSTER_DOC = REPO_ROOT / ".claude" / "CLAUDE.md"
LOGS_DIR = REPO_ROOT / "bench" / "logs"
SIM_TOOL = REPO_ROOT / "bench" / "tools" / "simulated_bench.py"
DIRECTIVE_DOC = (REPO_ROOT / "bench" / "directives" / "universal"
                 / "cdsfl_core_formal.md")

REQUIRED_SUFFIX = "-SIM"

# The five bases the founder named on 2026-08-08. Asserted as a SUBSET of what the
# roster derivation produces — they are a floor on correctness, not the source.
MANDATED_BASES = {"CC2", "Codex", "Gemini", "DeepSeek", "ChatGPT"}


# ─────────────────────────── roster derivation ────────────────────────────────

class RosterParseError(AssertionError):
    """The roster could not be read. Never downgrade this to a skip."""


_TABLE_HEADER = re.compile(r"^\|\s*cmd\s*\|\s*model\s*\|", re.I)
_SEPARATOR_CELL = set("-: ")
_LEADING_WORD = re.compile(r"[A-Za-z][A-Za-z0-9]*")
_TOKEN_SHAPE = re.compile(r"^[A-Za-z][A-Za-z0-9]*$")
_MIN_TOKEN_LEN = 3
_MIN_ROSTER_ROWS = 3


def parse_panel_roster(text: str) -> List[Tuple[str, str]]:
    """Return [(cmd, model)] from the dispatch table. Empty means parse failure."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not _TABLE_HEADER.match(line.strip()):
            continue
        rows: List[Tuple[str, str]] = []
        for raw in lines[i + 1:]:
            stripped = raw.strip()
            if not stripped.startswith("|"):
                break
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) < 2:
                break
            if all(set(c) <= _SEPARATOR_CELL for c in cells if c):
                continue                                   # markdown rule row
            cmd = cells[0].strip("`").strip()
            model = cells[1].strip("`").strip()
            if cmd and model:
                rows.append((cmd, model))
        if rows:
            return rows
    return []


def roster_vendor_tokens(rows: Sequence[Tuple[str, str]]) -> Set[str]:
    """Guarded tokens: the alias upper-cased plus the Model column's first word."""
    tokens: Set[str] = set()
    for cmd, model in rows:
        candidates = {cmd.upper()}
        lead = _LEADING_WORD.match(model)
        if lead:
            candidates.add(lead.group(0))
        for tok in candidates:
            if len(tok) >= _MIN_TOKEN_LEN and _TOKEN_SHAPE.match(tok):
                tokens.add(tok)
    return tokens


def load_vendor_tokens() -> Set[str]:
    """Derive the guarded vendor list, failing loudly at every blind spot."""
    if not ROSTER_DOC.exists():
        raise RosterParseError(
            f"panel roster not found at {ROSTER_DOC}. This check derives the vendor "
            f"list from that file; without it the check is blind, so it fails rather "
            f"than passing vacuously."
        )
    rows = parse_panel_roster(ROSTER_DOC.read_text(encoding="utf-8", errors="replace"))
    if len(rows) < _MIN_ROSTER_ROWS:
        raise RosterParseError(
            f"parsed {len(rows)} roster row(s) from {ROSTER_DOC}, expected at least "
            f"{_MIN_ROSTER_ROWS}. The 'Model Confer Dispatch (combinable)' table has "
            f"probably changed shape. Fix parse_panel_roster — do NOT hardcode the "
            f"vendor list, or a panel rotation will silently defeat this guard. "
            f"Parsed: {rows}"
        )
    tokens = roster_vendor_tokens(rows)
    if len(tokens) < _MIN_TOKEN_LEN:
        raise RosterParseError(
            f"derived only {sorted(tokens)} from roster rows {rows}; too few to guard."
        )
    return tokens


# ─────────────────────── what counts as a simulated artefact ──────────────────

# A name marker: 'simulated'/'simulation' anywhere, or a bare 'sim' path segment.
# Deliberately does NOT match 'similarity' or 'simple'.
_NAME_MARK = re.compile(r"(?i)simulat|(?:^|[_\-./])sim(?=[_\-./]|$)")

# Cheap byte pre-filter: a superset of _CONTENT_MARK, so the archive is read once
# at ~2.3 s rather than decoded in full at ~13 s.
#
# The superset property is LOAD-BEARING and is pinned by
# ``test_prefilter_is_a_true_superset_of_the_content_mark``. It was false when
# first written: the token was b'"simulated"' (with the closing quote), but the
# last _CONTENT_MARK alternative matches `"run_type": "simulated` with NO closing
# quote, so an artefact declaring itself `{"run_type": "simulated_panel_v2", ...}`
# failed the pre-filter, was never selected, and never scanned — while this guard
# reported a confident pass. Same shape as the line-anchored text arm: a failure
# that renders as a success. Any new _CONTENT_MARK alternative must have a
# corresponding byte token here, or the pin goes red.
_CONTENT_PREFILTER = (b"SIM", b'"simulated', b'"is_simulated"', b"simulated_bench")

# A STRUCTURAL self-declaration. Prose that merely uses the word does not qualify.
_CONTENT_MARK = re.compile(
    r"\bSIM-[A-Z]\b"
    r"|[A-Za-z0-9]-SIM\b"
    r"|simulated_bench"
    r'|"(?:simulated|is_simulated)"\s*:\s*true'
    r'|"(?:mode|run_type|panel_kind|panel)"\s*:\s*"simulated'
)


def name_marks_simulated(relative_path: str) -> bool:
    return bool(_NAME_MARK.search(relative_path))


#: Fields in a REVIEW record that hold a reviewer's own words or commands.
#: A `-SIM` string inside one of these is the reviewer TALKING ABOUT simulated
#: labels, not an artefact declaring itself simulated.
_QUOTATION_KEYS = ("response", "input_preview", "command", "prompt", "text",
                   "brief", "evidence", "detail", "description", "stdout")


def _strip_quoted_prose(data: bytes) -> bytes:
    """Blank out reviewer-authored free text before looking for a self-declaration.

    THE FALSE POSITIVE, 2026-08-30. `bench/logs/panel_*/cc2.tools.json` is the
    tool log of the REAL CC2 reviewing this repository. It was selected as a
    "simulated artefact" because CC2 had grepped for `CC2-SIM`, so the string
    `-SIM` appeared inside a shell command in its own log -- and the guard then
    flagged the FILENAME `cc2.tools.json` as a bare vendor name.

    That is this file's own stated principle applied one level up: a vendor
    token in free prose is not a violation, and by the same logic a SIM token in
    free prose is not a self-declaration. A real panel that DISCUSSES simulated
    labels must not be reclassified as a simulated run, or every future review
    brief on this subject turns the guard red and the "repair" is an exclusion
    list -- i.e. a dead guard, which is the outcome this file exists to prevent.

    Structural declarations are untouched: `"models": ["CC2-SIM"]`,
    `"model_id": "Gemini-SIM"`, `"simulated": true`, `simulated_bench` and any
    SIM token in a path or an identity key all still select.
    """
    text = data.decode("utf-8", errors="replace")
    for key in _QUOTATION_KEYS:
        # Blank the VALUE of a quotation-bearing JSON key, leaving structure.
        text = re.sub(
            r'("' + key + r'"\s*:\s*")((?:[^"\\]|\\.)*)(")',
            lambda m: m.group(1) + " " * len(m.group(2)) + m.group(3),
            text,
        )
    return text.encode("utf-8", errors="replace")


def content_marks_simulated(data: bytes) -> bool:
    if not any(tok in data for tok in _CONTENT_PREFILTER):
        return False
    structural = _strip_quoted_prose(data)
    return bool(_CONTENT_MARK.search(structural.decode("utf-8", errors="replace")))


# ────────────────────────── identity (label) positions ────────────────────────

_IDENTITY_EXACT = {
    "by", "author", "label", "reviewer", "speaker", "source", "attributedto",
    "producedby", "runby", "cell", "member", "members", "roster", "reportedby",
    # The 2026-08-08 ruling names "finding IDs" verbatim alongside labels and
    # report fields. `finding_id` normalises to `findingid`; without this entry
    # {"finding_id": "GEMINI-003"} passed the guard untouched.
    "findingid",
}


def is_identity_key(key: Any) -> bool:
    """True for keys under which a panel member's identity is recorded."""
    normalised = re.sub(r"[^a-z0-9]", "", str(key).lower())
    if any(word in normalised for word in ("model", "agent", "panel")):
        return True
    return normalised in _IDENTITY_EXACT


def bare_vendor_hits(value: str, tokens: Iterable[str]) -> List[str]:
    """Vendor tokens present in ``value`` WITHOUT the mandatory -SIM suffix.

    Suffix matching is case-insensitive so a lowercase directory (``gemini-sim``)
    is accepted; the suffix must still be present and must still be exactly SIM
    (``DeepSeek-SIMULATED`` does not satisfy it).
    """
    hits: List[str] = []
    for token in sorted(tokens):
        pattern = rf"(?<![A-Za-z0-9]){re.escape(token)}(?![A-Za-z0-9])"
        for match in re.finditer(pattern, value, re.I):
            if re.match(r"(?i)-SIM(?![A-Za-z0-9])", value[match.end():]):
                continue                                   # correctly suffixed
            hits.append(token)
            break
    return hits


class Violation(NamedTuple):
    artefact: str
    location: str
    value: str
    token: str

    def render(self) -> str:
        return (f"  {self.artefact}\n      at {self.location}\n"
                f"      value {self.value!r} carries bare vendor name "
                f"{self.token!r} — must be {self.token}{REQUIRED_SUFFIX}")


def _const_strings(node: ast.AST) -> List[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return [e.value for e in node.elts
                if isinstance(e, ast.Constant) and isinstance(e.value, str)]
    return []


def scan_path(relative_path: str, tokens: Iterable[str]) -> List[Violation]:
    out: List[Violation] = []
    for segment in Path(relative_path).parts:
        for token in bare_vendor_hits(segment, tokens):
            out.append(Violation(relative_path, "path segment", segment, token))
    return out


def scan_json(obj: Any, tokens: Iterable[str], artefact: str,
              trail: str = "$") -> List[Violation]:
    out: List[Violation] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            here = f"{trail}.{key}"
            if is_identity_key(key):
                items = value if isinstance(value, list) else [value]
                for item in items:
                    if isinstance(item, str):
                        for token in bare_vendor_hits(item, tokens):
                            out.append(Violation(artefact, here, item, token))
            out.extend(scan_json(value, tokens, artefact, here))
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            out.extend(scan_json(item, tokens, artefact, f"{trail}[{index}]"))
    return out


def scan_python(text: str, tokens: Iterable[str], artefact: str) -> List[Violation]:
    """AST only — comments and docstrings are structurally out of reach."""
    out: List[Violation] = []
    tree = ast.parse(text)
    for node in ast.walk(tree):
        found: List[Tuple[str, str, int]] = []
        if isinstance(node, ast.keyword) and node.arg and is_identity_key(node.arg):
            for s in _const_strings(node.value):
                found.append((f"keyword {node.arg}=", s, getattr(node.value, "lineno", 0)))
        elif isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if (isinstance(key, ast.Constant) and isinstance(key.value, str)
                        and is_identity_key(key.value)):
                    for s in _const_strings(value):
                        found.append((f"dict key {key.value!r}", s,
                                      getattr(value, "lineno", 0)))
        elif isinstance(node, ast.Assign):
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if any(is_identity_key(n) for n in names):
                for s in _const_strings(node.value):
                    found.append((f"assignment to {names}", s, node.lineno))
        for where, value, lineno in found:
            for token in bare_vendor_hits(value, tokens):
                out.append(Violation(artefact, f"line {lineno} {where}", value, token))
    return out


# NOT line-anchored, deliberately. An earlier version anchored the key to the start
# of a line and was refuted by its own fixture: `{"model_id": "Gemini", "trunc` — a
# truncated JSON artefact falling back to the text arm — matched nothing at all and
# the guard reported a confident pass over unchecked content. The same hole covered
# every log-shaped line (`... INFO panel=Gemini dispatched`). Keys carry no spaces,
# which keeps ordinary prose ("the model is: X") from being read as an attribution.
_TEXT_KV = re.compile(
    r"""(?<![A-Za-z0-9_])["'`]?(?P<key>[A-Za-z][A-Za-z0-9_.\-]{0,30}?)["'`]?"""
    r"""[ \t]*[:=][ \t]*["'`]?(?P<val>[A-Za-z][A-Za-z0-9_.\-]*)"""
)
# Closing pipe is a LOOKAHEAD, not consumed. Consuming it made the scan
# non-overlapping, so only alternate cells were ever examined: in
# `| F001 | Gemini | 0.85 |` the first match ate the pipe that opens the Gemini
# cell, and the vendor name in column 2 — the commonest real shape for a findings
# table — was invisible. Zero hits, reported as a pass.
_TEXT_CELL = re.compile(r"\|[ \t]*(?P<val>[A-Za-z][A-Za-z0-9_.\-]*)[ \t]*(?=\|)")
_TEXT_BOLD = re.compile(r"\*\*(?P<val>[A-Za-z][A-Za-z0-9_.\-]*)\*\*[ \t]*[:\-—]")


def scan_text(text: str, tokens: Iterable[str], artefact: str) -> List[Violation]:
    """Label-shaped constructs in prose artefacts: key/value, table cell, bold label."""
    out: List[Violation] = []
    for match in _TEXT_KV.finditer(text):
        if not is_identity_key(match.group("key")):
            continue
        value = match.group("val")
        for token in bare_vendor_hits(value, tokens):
            out.append(Violation(artefact, f"{match.group('key').strip()}: label",
                                 value, token))
    for regex, what in ((_TEXT_CELL, "table cell"), (_TEXT_BOLD, "bold label")):
        for match in regex.finditer(text):
            value = match.group("val")
            for token in bare_vendor_hits(value, tokens):
                out.append(Violation(artefact, what, value, token))
    return out


def scan_artefact(path: Path, relative_path: str, data: bytes,
                  tokens: Iterable[str]) -> List[Violation]:
    out = scan_path(relative_path, tokens)
    text = data.decode("utf-8", errors="replace")
    suffix = path.suffix.lower()
    if suffix == ".json":
        try:
            out.extend(scan_json(json.loads(text), tokens, relative_path))
        except (json.JSONDecodeError, RecursionError):
            out.extend(scan_text(text, tokens, relative_path))
    elif suffix == ".py":
        try:
            out.extend(scan_python(text, tokens, relative_path))
        except SyntaxError:
            out.extend(scan_text(text, tokens, relative_path))
    elif suffix == ".jsonl":
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.extend(scan_json(json.loads(line), tokens, relative_path))
            except json.JSONDecodeError:
                out.extend(scan_text(line, tokens, relative_path))
    else:
        out.extend(scan_text(text, tokens, relative_path))
    return out


# ───────────────────── artefact discovery (one pass, cached) ──────────────────

class Survey(NamedTuple):
    simulated: List[Tuple[Path, str, bytes]]
    prose_only_mentions: List[str]      # say "simulated" but are NOT selected
    unreadable: List[str]
    sim_tool_present: bool


_SURVEY: Survey | None = None


def survey_artefacts() -> Survey:
    global _SURVEY
    if _SURVEY is not None:
        return _SURVEY

    simulated: List[Tuple[Path, str, bytes]] = []
    prose_only: List[str] = []
    unreadable: List[str] = []

    def ingest(path: Path) -> None:
        relative = str(path.relative_to(REPO_ROOT))
        try:
            data = path.read_bytes()
        except OSError as exc:
            unreadable.append(f"{relative}: {type(exc).__name__}: {exc}")
            return
        if name_marks_simulated(relative) or content_marks_simulated(data):
            simulated.append((path, relative, data))
        elif b"imulated" in data:
            prose_only.append(relative)

    if LOGS_DIR.exists():
        for path in sorted(LOGS_DIR.rglob("*")):
            if path.is_file():
                ingest(path)

    sim_tool_present = SIM_TOOL.is_file()
    if sim_tool_present and all(p != SIM_TOOL for p, _, _ in simulated):
        ingest(SIM_TOOL)

    _SURVEY = Survey(simulated, prose_only, unreadable, sim_tool_present)
    return _SURVEY


# ───────────────────────────────── the tests ──────────────────────────────────

class TestRosterDerivation:
    """The vendor list must come from the roster, and must fail loudly if it can't."""

    def test_roster_yields_the_mandated_panel(self):
        rows = parse_panel_roster(ROSTER_DOC.read_text(encoding="utf-8"))
        assert len(rows) >= _MIN_ROSTER_ROWS, f"roster parse degraded: {rows}"
        tokens = roster_vendor_tokens(rows)
        missing = MANDATED_BASES - tokens
        assert not missing, (
            f"the roster derivation lost mandated panel base(s) {sorted(missing)}. "
            f"Derived {sorted(tokens)} from {rows}. Every base named in the "
            f"2026-08-08 ruling must be guarded."
        )

    def test_rotation_cannot_defeat_the_check(self, tmp_path):
        """Swap a panel member in the roster; the new vendor becomes guarded."""
        rotated = tmp_path / "CLAUDE.md"
        rotated.write_text(
            "### Model Confer Dispatch (combinable)\n\n"
            "| Cmd | Model | Route | Identifier |\n"
            "|-----|-------|-------|---|\n"
            "| `cc2` | Claude Opus 4.7 | CLI piped mode | `opus` |\n"
            "| `mi` | Mistral Large 3 | OpenRouter API | `mistralai/large-3` |\n"
            "| `ds` | DeepSeek V4 Pro | DeepSeek direct API | `deepseek-v4-pro` |\n",
            encoding="utf-8")
        tokens = roster_vendor_tokens(parse_panel_roster(rotated.read_text()))
        assert "Mistral" in tokens, (
            f"a rotated-in vendor was not picked up: {sorted(tokens)}. The vendor "
            f"list must be derived from the roster, never hardcoded."
        )
        assert "Gemini" not in tokens, "a rotated-out vendor leaked in from a hardcode"

    def test_unparseable_roster_fails_rather_than_passing_blind(self, tmp_path,
                                                               monkeypatch):
        empty = tmp_path / "CLAUDE.md"
        empty.write_text("# no dispatch table here\n", encoding="utf-8")
        monkeypatch.setattr(sys.modules[__name__], "ROSTER_DOC", empty)
        with pytest.raises(RosterParseError):
            load_vendor_tokens()

    def test_missing_roster_fails_rather_than_passing_blind(self, tmp_path,
                                                            monkeypatch):
        monkeypatch.setattr(sys.modules[__name__], "ROSTER_DOC",
                            tmp_path / "absent" / "CLAUDE.md")
        with pytest.raises(RosterParseError):
            load_vendor_tokens()


class TestDetectorGoesRedAndGreen:
    """P-pass: a planted bare name must go red; the suffixed form must pass."""

    TOKENS = {"CC2", "Codex", "Gemini", "DeepSeek", "ChatGPT", "Claude"}

    def test_json_identity_value_bare_name_is_red(self):
        payload = {"findings": [{"finding_id": "F001", "model_id": "Gemini",
                                 "severity": 0.85}]}
        hits = scan_json(payload, self.TOKENS, "fixture.json")
        assert [h.token for h in hits] == ["Gemini"], f"expected one hit, got {hits}"

    def test_json_identity_value_with_suffix_is_green(self):
        payload = {"findings": [{"finding_id": "F001", "model_id": "Gemini-SIM",
                                 "severity": 0.85}]}
        assert scan_json(payload, self.TOKENS, "fixture.json") == []

    def test_json_identity_list_bare_name_is_red(self):
        payload = {"panel_members": ["CC2-SIM", "Codex-SIM", "DeepSeek"]}
        assert [h.token for h in scan_json(payload, self.TOKENS, "f.json")] \
            == ["DeepSeek"]

    def test_python_identity_keyword_bare_name_is_red(self):
        source = 'row = dict(finding_id="F001", model_id="Codex", severity=0.8)\n'
        assert [h.token for h in scan_python(source, self.TOKENS, "f.py")] == ["Codex"]

    def test_python_identity_keyword_with_suffix_is_green(self):
        source = 'row = dict(finding_id="F001", model_id="Codex-SIM", severity=0.8)\n'
        assert scan_python(source, self.TOKENS, "f.py") == []

    def test_python_identity_assignment_and_list_are_red(self):
        source = 'PANEL_MODELS = ["CC2-SIM", "Gemini", "Codex-SIM"]\n'
        assert [h.token for h in scan_python(source, self.TOKENS, "f.py")] == ["Gemini"]

    def test_path_segment_bare_name_is_red(self):
        hits = scan_path("bench/logs/simulated_run_x/gemini/round_00.json", self.TOKENS)
        assert [h.token for h in hits] == ["Gemini"]

    def test_path_segment_with_suffix_is_green_including_lowercase(self):
        assert scan_path("bench/logs/simulated_run_x/gemini-sim/round_00.json",
                         self.TOKENS) == []

    def test_suffix_must_be_exactly_sim(self):
        """`DeepSeek-SIMULATED` does not satisfy the mandatory suffix."""
        assert bare_vendor_hits("DeepSeek-SIMULATED", self.TOKENS) == ["DeepSeek"]
        assert bare_vendor_hits("DeepSeek-SIM", self.TOKENS) == []

    def test_prose_and_docstrings_are_not_violations(self):
        """Pins bench/tools/simulated_bench.py, whose docstring names the vendors.

        A free-text scan would go red on the text explaining the 2026-08-04
        provenance failure, and the 'fix' would be deleting that explanation.
        """
        source = (
            '"""Labelling these `Gemini`/`Codex` on 2026-08-04 was a provenance\n'
            'failure. They are Claude subagents, not the named frontier models."""\n'
            '# Never label a simulated agent DeepSeek or ChatGPT.\n'
            'row = dict(model_id="SIM-A")\n'
        )
        assert scan_python(source, self.TOKENS, "f.py") == []

    def test_jsonl_artefacts_are_scanned_line_by_line(self, tmp_path):
        """The .jsonl arm must actually run, not sit as untested code."""
        art = tmp_path / "simulated_rounds.jsonl"
        art.write_text('{"model_id": "CC2-SIM"}\n{"model_id": "ChatGPT"}\n',
                       encoding="utf-8")
        hits = scan_artefact(art, "simulated_rounds.jsonl", art.read_bytes(),
                             self.TOKENS)
        assert [h.token for h in hits] == ["ChatGPT"], hits

    def test_malformed_json_falls_back_to_text_rather_than_scanning_nothing(
            self, tmp_path):
        """A truncated artefact must still be checked — silence here is the defect."""
        art = tmp_path / "simulated_truncated.json"
        art.write_text('{"model_id": "Gemini", "trunc', encoding="utf-8")
        hits = scan_artefact(art, "simulated_truncated.json", art.read_bytes(),
                             self.TOKENS)
        assert [h.token for h in hits] == ["Gemini"], (
            f"a malformed simulated artefact was scanned into silence: {hits}")

    def test_prefilter_is_a_true_superset_of_the_content_mark(self):
        """The cheap byte pre-filter must never veto something _CONTENT_MARK matches.

        If it does, the artefact is not merely mis-scanned — it is never selected,
        so nothing scans it and this guard reports a confident pass over content it
        never read. Every alternative of _CONTENT_MARK gets a case here.
        """
        corpus = [
            b'{"model_id": "SIM-A"}',
            b'{"model_id": "Gemini-SIM"}',
            b'produced by simulated_bench.py',
            b'{"simulated": true}',
            b'{"is_simulated": true}',
            b'{"mode": "simulated"}',
            b'{"run_type": "simulated_panel_v2", "model_id": "Gemini"}',
            b'{"panel": "simulated run 3", "model_id": "Codex"}',
            b'{"panel_kind": "simulated-exp48", "model_id": "DeepSeek"}',
        ]
        for blob in corpus:
            marked = bool(_CONTENT_MARK.search(blob.decode("utf-8", errors="replace")))
            assert marked, f"fixture no longer exercises _CONTENT_MARK: {blob!r}"
            assert content_marks_simulated(blob), (
                f"pre-filter vetoed an artefact that _CONTENT_MARK matches: {blob!r}. "
                f"It would never be selected and never scanned, and this guard would "
                f"go green over unread content. Add a byte token to _CONTENT_PREFILTER."
            )

    def test_markdown_table_cell_in_any_column_is_red(self):
        """Not just column 1 — the regex must overlap on the shared pipe.

        A findings table puts the identity in column 2 or 3. The original pattern
        consumed the closing pipe, so `| F001 | Gemini | 0.85 |` produced no hit.
        """
        row = "| Finding | Model | Severity |\n| F001 | Gemini | 0.85 |\n"
        assert [h.token for h in scan_text(row, self.TOKENS, "simulated_note.md")] \
            == ["Gemini"], "a vendor name in a non-leading table cell was missed"
        ok = "| F001 | Gemini-SIM | 0.85 |\n"
        assert scan_text(ok, self.TOKENS, "simulated_note.md") == []

    def test_finding_id_carrying_a_bare_vendor_name_is_red(self):
        """The 2026-08-08 ruling names finding IDs explicitly."""
        payload = {"findings": [{"finding_id": "GEMINI-003", "severity": 0.9}]}
        assert [h.token for h in scan_json(payload, self.TOKENS, "f.json")] == ["Gemini"]
        good = {"findings": [{"finding_id": "GEMINI-SIM-003", "severity": 0.9}]}
        assert scan_json(good, self.TOKENS, "f.json") == []

    def test_end_to_end_fixture_files_go_red_then_green(self, tmp_path):
        """Whole-artefact P-pass over real files on disk, both directions."""
        bad = tmp_path / "simulated_panel.json"
        bad.write_text(json.dumps({"run": "sim", "panel": ["Gemini", "CC2-SIM"]}),
                       encoding="utf-8")
        violations = scan_artefact(bad, "simulated_panel.json", bad.read_bytes(),
                                   self.TOKENS)
        assert [v.token for v in violations] == ["Gemini"], violations

        good = tmp_path / "simulated_panel_ok.json"
        good.write_text(json.dumps({"run": "sim", "panel": ["Gemini-SIM", "CC2-SIM"]}),
                        encoding="utf-8")
        assert scan_artefact(good, "simulated_panel_ok.json", good.read_bytes(),
                             self.TOKENS) == []


class TestSimulatedPredicate:
    """The predicate must select self-declared simulated artefacts and nothing else."""

    def test_name_marker_selects(self):
        assert name_marks_simulated("bench/logs/simulated_bench_last.json")
        assert name_marks_simulated("bench/logs/sim/round_00.json")

    def test_name_marker_does_not_over_match(self):
        assert not name_marks_simulated("bench/dm/_similarity.py")
        assert not name_marks_simulated("bench/logs/simple_run.log")

    def test_structural_content_markers_select(self):
        assert content_marks_simulated(b'{"model_id": "SIM-A"}')
        assert content_marks_simulated(b'{"model_id": "Gemini-SIM"}')
        assert content_marks_simulated(b'produced by simulated_bench.py')

    def test_prose_mention_is_not_a_simulated_artefact(self):
        """The measured refutation of the obvious predicate — do not relax this.

        Real panel runs contain prose like '(Simulated) The defect is present'.
        Selecting on that substring would flag the whole real archive, whose
        filenames legitimately carry bare vendor names.
        """
        real_prose = (b'{"description": "**Attempt**: (Simulated) The defect is '
                      b'present because the second call returns True."}')
        assert not content_marks_simulated(real_prose)

        survey = survey_artefacts()
        if survey.prose_only_mentions:
            sample = survey.prose_only_mentions[:3]
            assert all(not name_marks_simulated(p) for p in sample), sample


class TestLiveArtefacts:
    """The actual guard, over the repository's real simulated artefacts."""

    def test_no_bare_vendor_name_in_any_simulated_artefact(self):
        tokens = load_vendor_tokens()
        survey = survey_artefacts()

        assert not survey.unreadable, (
            "in-scope artefacts could not be read, so this guard did not actually "
            "check them:\n  " + "\n  ".join(survey.unreadable)
        )

        if not survey.simulated:
            reason = (
                f"no simulated artefacts found. Searched {LOGS_DIR} recursively for a "
                f"name marker (simulated/simulation/a bare 'sim' segment) or a "
                f"structural content marker (SIM-x label, -SIM suffix, "
                f"simulated_bench reference, \"simulated\": true), plus "
                f"{SIM_TOOL} (present={survey.sim_tool_present}). Guarded vendor "
                f"tokens derived from the roster: {sorted(tokens)}. This check is "
                f"NOT passing — it found nothing to check."
            )
            warnings.warn(reason, stacklevel=2)
            pytest.skip(reason)

        violations: List[Violation] = []
        for path, relative, data in survey.simulated:
            violations.extend(scan_artefact(path, relative, data, tokens))

        assert not violations, (
            f"{len(violations)} bare vendor name(s) in simulated artefacts. Every "
            f"simulated panel member must carry the mandatory {REQUIRED_SUFFIX} "
            f"suffix (founder ruling 2026-08-08): CC2-SIM, Codex-SIM, Gemini-SIM, "
            f"DeepSeek-SIM, ChatGPT-SIM. A bare vendor name here is a provenance "
            f"failure — it makes a simulated result indistinguishable from a real "
            f"one.\n" + "\n".join(v.render() for v in violations)
        )

    def test_integrity_directive_section_is_present(self):
        """This file is named ..._and_integrity_directive.py; nothing pinned it.

        The falsifier-integrity section was added to the universal directive on
        2026-08-08 and is loaded as the panel's system prompt. It carried no test,
        so a later edit could delete it and every suite would stay green — the
        section would simply stop reaching the panel, silently. Anchors below are
        the load-bearing behaviours, not the prose around them.
        """
        assert DIRECTIVE_DOC.is_file(), (
            f"the universal directive is missing at {DIRECTIVE_DOC}; it is loaded as "
            f"the panel system prompt by launcher_core and the orchestrator."
        )
        text = DIRECTIVE_DOC.read_text(encoding="utf-8")

        assert "## Falsifier Integrity" in text, (
            "the falsifier-integrity section has been removed from the universal "
            "directive. It is what tells the panel a verdict must derive from the "
            "artefact under review alone."
        )
        required = {
            "artefact-alone rule": "artefact under review alone",
            "admissibility predicate": "admissible(f)",
            "no key/answer-file read": "scoring key",
            "no weakening a test": "weaken",
            "no uncomputed verdict": "did not compute",
            "no early termination": "terminate early",
            "the archived instance": "C0012",
        }
        missing = sorted(name for name, anchor in required.items()
                         if anchor not in text)
        assert not missing, (
            f"the falsifier-integrity section lost its load-bearing content: "
            f"{missing}. Restore it or update this pin deliberately — do not delete "
            f"the pin to make the suite green."
        )
        assert text.count("```") % 2 == 0, (
            "unbalanced code fences in the universal directive; the panel would "
            "receive a mangled system prompt."
        )

    def test_the_named_simulation_tool_is_in_scope(self):
        """If the tool is renamed away, say so — do not quietly lose the coverage."""
        survey = survey_artefacts()
        if not survey.sim_tool_present:
            warnings.warn(
                f"{SIM_TOOL} is absent, so the Python arm of this guard scans "
                f"nothing named in the brief. If it moved, update SIM_TOOL.",
                stacklevel=2)
            pytest.skip(f"{SIM_TOOL} not present")
        assert any(p == SIM_TOOL for p, _, _ in survey.simulated), (
            f"{SIM_TOOL} exists but was not picked up as a simulated artefact; "
            f"the discovery pass has a hole."
        )


class TestAReviewerQuotingSimLabelsIsNotASimulatedArtefact:
    """The selector must not turn a REAL panel review into a simulated run.

    THE FALSE POSITIVE, 2026-08-30. `bench/logs/panel_*/cc2.tools.json` is the
    real CC2's tool log. CC2 had grepped for `CC2-SIM` while reviewing the
    naming repair, so `-SIM` appeared inside a shell command in its own log; the
    selector matched it anywhere in bytes, classified a real artefact as
    simulated, and then flagged the filename `cc2.tools.json` as a bare vendor
    name. Left unfixed, every future review brief on this subject turns the
    guard red, and the obvious "repair" is an exclusion list -- a dead guard,
    which is precisely what this file exists to prevent.

    Both directions are pinned, because a selector that stops selecting is a
    worse failure than one that over-selects.
    """

    STRUCTURAL = [
        ('a models list',        b'{"models": ["CC2-SIM", "Gemini-SIM"]}'),
        ('a model_id',           b'{"model_id": "Gemini-SIM", "x": 1}'),
        ('an explicit flag',     b'{"simulated": true}'),
        ('a SIM-x panel label',  b'{"label": "SIM-A"}'),
        ('a bench reference',    b'{"src": "simulated_bench"}'),
        ('quoted AND structural',
         b'{"response": "about CC2-SIM", "models": ["CC2-SIM"]}'),
    ]
    QUOTED_ONLY = [
        ('a reviewer command',   b'{"input_preview": "grep -rn CC2-SIM bench/"}'),
        ('reviewer prose',       b'{"response": "I checked CC2-SIM and Fable-SIM."}'),
    ]

    @pytest.mark.parametrize("why,data", STRUCTURAL, ids=[c[0] for c in STRUCTURAL])
    def test_a_structural_declaration_still_selects(self, why, data):
        assert content_marks_simulated(data), (
            f"{why} no longer selects — the guard has been weakened and a "
            f"simulated artefact can now carry bare vendor names unnoticed"
        )

    @pytest.mark.parametrize("why,data", QUOTED_ONLY, ids=[c[0] for c in QUOTED_ONLY])
    def test_a_reviewer_merely_quoting_a_sim_label_does_not_select(self, why, data):
        assert not content_marks_simulated(data), (
            f"{why} selects, so a real review that discusses simulated labels "
            f"is misclassified as a simulated run"
        )

    def test_the_real_run_artefacts_are_still_selected(self):
        """The strongest check available: the actual artefact that carried the
        123 bare vendor names must still be caught."""
        for rel in ("bench/logs_quarantine/sim45_memory_20260830T153011Z/"
                    "sim45_memory_report.json",
                    "bench/logs/sim45_memory_20260830T161215Z/"
                    "sim45_memory_report.json"):
            f = REPO_ROOT / rel
            if f.is_file():
                assert content_marks_simulated(f.read_bytes()), rel
