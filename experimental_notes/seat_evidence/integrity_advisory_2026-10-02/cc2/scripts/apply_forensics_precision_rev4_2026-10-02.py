# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'integrity_advisory_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: cd886dda015e4da2c539cfd36a91e57f9cbed25dc9372fb545392b63f04c02cc
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""D3, revision 4: recognise the FOREIGN CHECKOUT ROOT, using the predicate this
repository already owns.

After rev3, run 1b retains 25 CONFIRMED hits and every one is a literal that ends
AT the foreign checkout root or at a top-level directory inside it --
`Path("<repo>")`, `sys.path.insert(0, "<repo>/bench")`. Tail matching cannot see
those: the only tail with a separator is `Constraint_Engineering/bench`, which
does not exist inside this checkout, and a bare `bench` is deliberately rejected
as naming nothing reliably.

`bench/repo_paths.foreign_repo_roots` is the committed predicate for exactly this
and it is narrow by construction -- "ONLY an absolute path ending at a directory
named like this project, identified from the git remote rather than from the
folder name". Executed here in a non-git sandbox it returns
['/Users/georgejackson/Developer_Projects/Constraint_Engineering'] for run 1b's
literals, so it works where it is needed.

The remainder under that root is then a repo-relative path and gets the SAME
exam-design test as every other demotion: `cdsfl_registry/targets/...` and
`exp*_configs/...` stay CONFIRMED. A failure to import leaves the hit at
CONFIRMED, which is the fail-safe direction.

Usage:  python3 scripts/apply_forensics_precision_rev4_2026-10-02.py [--check]
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
CHECK = "--check" in sys.argv
F = REPO / "bench" / "key_access_forensics.py"
text = F.read_text(encoding="utf-8")
applied: list[str] = []

ANCHOR = '''    if _is_exam_design(_norm_path(literal)):
        return False
    for cand in _tail_candidates(literal):
        if cand.count("/") < 1:        # a bare basename names nothing reliably
            continue
        if _is_exam_design(cand):
            return False
        if (repo_root / cand).exists():
            return True
    return False'''

NEW = '''    if _is_exam_design(_norm_path(literal)):
        return False
    for cand in _tail_candidates(literal):
        if cand.count("/") < 1:        # a bare basename names nothing reliably
            continue
        if _is_exam_design(cand):
            return False
        if (repo_root / cand).exists():
            return True
    # THE LITERAL MAY END AT THE CHECKOUT ROOT ITSELF, or at a top-level
    # directory inside it, and no tail of such a path exists in THIS tree. Use
    # the repository's own narrow predicate for "an absolute path ending at a
    # directory named like this project". An import failure leaves the hit at
    # CONFIRMED, which is the fail-safe direction.
    try:
        from bench.repo_paths import foreign_repo_roots
    except ImportError:                                   # pragma: no cover
        try:
            from repo_paths import foreign_repo_roots     # type: ignore
        except ImportError:
            return False
    try:
        roots = foreign_repo_roots(literal, repo_root)
    except Exception:                                     # noqa: BLE001
        return False
    norm = literal.replace("\\\\", "/")
    for root in list(roots) + [str(repo_root)]:
        root = str(root).rstrip("/")
        if not root or not (norm == root or norm.startswith(root + "/")):
            continue
        rel = norm[len(root):].lstrip("/")
        if rel and _is_exam_design(rel):
            return False
        if not rel or (repo_root / rel).exists():
            return True
    return False'''

if NEW in text:
    print("  = rev4 (already applied)")
elif text.count(ANCHOR) != 1:
    raise SystemExit(f"ANCHOR NOT UNIQUE: {text.count(ANCHOR)}")
else:
    text = text.replace(ANCHOR, NEW, 1)
    applied.append("rev4: foreign-checkout-root demotion via bench.repo_paths")
    if not CHECK:
        F.write_text(text, encoding="utf-8")

print("WOULD APPLY:" if CHECK else "APPLIED:")
for a in applied:
    print("  +", a)
