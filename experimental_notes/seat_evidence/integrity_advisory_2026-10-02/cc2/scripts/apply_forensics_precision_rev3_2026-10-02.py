# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'integrity_advisory_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 2cfecbc62c862d709d1f51becf19cb3daef2fda7a9025080421a2581b59c1e27
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""D3, revision 3: match the PATH, not the construct around it.

Revision 2 still fired on 0 of run 1b's 107 hits. Executed cause: `Hit.matched`
for an `OPEN_CALL` hit is the whole match -- `Path("/Users/.../bench/SPEC.md"` --
so splitting it on "/" yields a first segment of `Path("` and a last segment with
a trailing quote, and no tail ever equals a declared target. The path literal is
captured inside the match (`quoted` / `bare`) and has to be recovered before any
tail comparison. One helper, used by both rules.

This is the third revision of the same fix and every one of the first two looked
right when read. The tool is the only thing that distinguished them.

Usage:  python3 scripts/apply_forensics_precision_rev3_2026-10-02.py [--check]
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
CHECK = "--check" in sys.argv
F = REPO / "bench" / "key_access_forensics.py"
text = F.read_text(encoding="utf-8")
applied: list[str] = []


def patch(anchor: str, new: str, tag: str) -> None:
    global text
    if new in text:
        print(f"  = {tag} (already applied)")
        return
    n = text.count(anchor)
    if n != 1:
        raise SystemExit(f"ANCHOR NOT UNIQUE for {tag}: {n} occurrence(s)")
    text = text.replace(anchor, new, 1)
    applied.append(tag)


patch('''def _tail_candidates(literal: str) -> list[str]:''',
      '''#: The path inside a matched read/list construct. `Hit.matched` carries the whole
#: match (`Path("/Users/.../x.md"`), so the literal must be recovered before any
#: tail comparison; without this both tail rules match nothing at all.
_PATH_IN_MATCH = re.compile(
    r"(?:~/|\\$HOME/|\\$\\{HOME\\}/|/Users/|/home/|/Volumes/|/Library/)"
    r"[^\\s\\"'\\\\)\\],;\\x00]*")


def _path_from_match(matched: str) -> str:
    """The path literal inside a matched construct, or the match itself."""
    m = _PATH_IN_MATCH.search(matched or "")
    return m.group(0) if m else (matched or "")


def _tail_candidates(literal: str) -> list[str]:''',
      "rev3a: _path_from_match helper")

patch('''                if _relocation_in_scope(h.matched, _run_name, _declared_tails):''',
      '''                _lit = _path_from_match(h.matched)
                if _relocation_in_scope(_lit, _run_name, _declared_tails):''',
      "rev3b: relocation test reads the recovered literal")

patch('''                if _repo_source_demotion(h.matched, repo_root):''',
      '''                if _repo_source_demotion(_lit, repo_root):''',
      "rev3c: demotion test reads the recovered literal")

if CHECK:
    print("WOULD APPLY:")
    for a in applied:
        print("  +", a)
else:
    F.write_text(text, encoding="utf-8")
    print("APPLIED:")
    for a in applied:
        print("  +", a)
