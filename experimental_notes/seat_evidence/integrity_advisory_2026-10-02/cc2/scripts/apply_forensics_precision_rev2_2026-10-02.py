# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'integrity_advisory_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: c57beb29a8ab81ecbff4d50c28c901229304e984d08fe6bddac3a05c1c28684e
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""D3, revision 2: the measured mechanism, not the assumed one.

Revision 1 excluded harvested copies of this repository's own source (7 of run
1b's hits) and tried to recognise a relocated archive by the run directory's own
name. EXECUTED against run 1b, that second rule fired on 0 hits, and the reason
is a sharper defect than the one it was aimed at:

  ALL 107 remaining CONFIRMED hits are repo-rooted paths from the checkout the
  run was made in, and the single most frequent literal is the run's OWN
  DECLARED TARGET: `Path("<foreign repo>/bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md")`.

`discover_target_dirs` passes `target_file` through `_norm_path`, which resolves
a RELATIVE value against the scanner's cwd. Run 1b's report records
`target_file = "bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md"` -- relative -- so the
allowlist gained `<cwd>/bench` and the real target directory never entered it.
Every read of the document the panel was convened to review was therefore
reported as out-of-scope access, at tier CONFIRMED, on a run where no key exists.

That also explains the 89-vs-114 gap between scanning run 1b in place and from a
copy: `_in_scope`'s truncation clause (`a.startswith(target)`) admits any
ANCESTOR of an allowlisted root, so with the original run path on the allowlist
25 bare-ancestor literals (`<repo>`, `<repo>/bench`) passed, and without it they
did not. The verdict moved with the archive's location, not with its contents.

So this revision matches by REPO-RELATIVE TAIL instead of absolute prefix:
  * a literal whose tail is a DECLARED target (or a context file) is in scope,
    from any checkout -> tier RELOCATED, reported, not counted;
  * a literal whose tail names anything else that exists in this repository is
    repository SOURCE -> demoted to SUSPICION, reported, not counted;
  * exam design is excluded from both, by `_is_exam_design`, so
    `cdsfl_registry/targets/...` and `exp52_configs/...` keep tier CONFIRMED.

Usage:  python3 scripts/apply_forensics_precision_rev2_2026-10-02.py [--check]
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


patch('''def _relocation_in_scope(literal: str, run_name: str) -> bool:
    """True when a path literal names THIS run directory under a different root.

    The run directory name carries a UTC stamp and the experiment label, so it
    cannot coincide with a key store. This is the whole of the relocation rule:
    it does not widen scope to anything else, and an archive that has never moved
    is unaffected because those literals were already in scope.
    """
    if not run_name or run_name not in literal:
        return False
    return any(seg == run_name for seg in literal.replace("\\\\", "/").split("/"))''',
      '''def declared_target_tails(run_dir: Path) -> list[str]:
    """Repo-relative paths the panel was DECLARED to read, as written.

    Same runner-authored sources as `discover_target_dirs` and the same trust
    rule, but the value is kept AS A TAIL rather than resolved against the
    scanner's cwd. A report that records `target_file` relative -- which run 1b
    does -- is then still matchable from any checkout.
    """
    tails: set[str] = set()
    for probe in sorted(run_dir.rglob("*.json")):
        if probe.name not in RUNNER_AUTHORED and not probe.name.endswith("_report.json"):
            continue
        try:
            obj = json.loads(probe.read_text(encoding="utf-8", errors="replace"))
        except Exception:  # noqa: BLE001
            continue
        if not isinstance(obj, dict):
            continue
        vals: list[str] = []
        for key in ("target_file", "staged_copy", "target_path"):
            v = obj.get(key)
            if isinstance(v, str) and v:
                vals.append(v)
        cf = obj.get("context_files")
        if isinstance(cf, list):
            vals += [c for c in cf if isinstance(c, str) and c]
        for v in vals:
            p = v.replace("\\\\", "/").lstrip("/")
            if p:
                tails.add(p)
    return sorted(tails)


def _tail_candidates(literal: str) -> list[str]:
    """Every proper suffix of a path literal, longest first."""
    parts = [p for p in literal.replace("\\\\", "/").split("/") if p and p != "."]
    return ["/".join(parts[i:]) for i in range(len(parts))]


def _relocation_in_scope(literal: str, run_name: str,
                         declared_tails: Iterable[str] = ()) -> bool:
    """True when a path literal names, from SOME checkout, something this run was
    declared to read -- its own directory, its target, or a context file.

    MATCHED BY TAIL, NOT BY ABSOLUTE PREFIX, which is the whole repair: a run
    directory and a declared target are the two things whose absolute location
    changes when an archive is copied, and both are identified here by the part
    that does not change. Nothing else is widened.
    """
    segs = [s for s in literal.replace("\\\\", "/").split("/") if s]
    if run_name and any(seg == run_name for seg in segs):
        return True
    tails = set(declared_tails)
    if not tails:
        return False
    for cand in _tail_candidates(literal):
        for t in tails:
            if cand == t or cand.startswith(t.rstrip("/") + "/"):
                return True
    return False''',
      "rev2a: declared_target_tails + tail-matched relocation")

patch('''def _repo_source_demotion(literal: str, repo_root: Path) -> bool:
    """True when a path literal names ordinary repository SOURCE.

    Demotion, not exemption: the hit survives at SUSPICION. Exam design and
    anything key-shaped are excluded, so the documented
    `json.load(52_factorial_cell_A.json)` exploit keeps its CONFIRMED tier.
    """
    target = _norm_path(literal)
    if _is_exam_design(target):
        return False
    try:
        rel = Path(target).resolve().relative_to(repo_root.resolve())
    except (ValueError, OSError):
        return False
    if _is_exam_design(str(rel)):
        return False
    return (repo_root / rel).exists()''',
      '''def _repo_source_demotion(literal: str, repo_root: Path) -> bool:
    """True when a path literal names ordinary repository SOURCE, from ANY checkout.

    Demotion, not exemption: the hit survives at SUSPICION and is counted in the
    advisory's set-aside census. Exam design and anything key-shaped are excluded
    FIRST, so the documented `json.load(52_factorial_cell_A.json)` exploit and any
    read under `cdsfl_registry/targets` keep tier CONFIRMED.

    The absolute-prefix test it replaces could only recognise THIS checkout, so
    it was blind to every archived run -- which is every run a reader scans.
    """
    if _is_exam_design(_norm_path(literal)):
        return False
    for cand in _tail_candidates(literal):
        if cand.count("/") < 1:        # a bare basename names nothing reliably
            continue
        if _is_exam_design(cand):
            return False
        if (repo_root / cand).exists():
            return True
    return False''',
      "rev2b: repo-source demotion matched by tail")

patch('''                if _relocation_in_scope(h.matched, _run_name):''',
      '''                if _relocation_in_scope(h.matched, _run_name, _declared_tails):''',
      "rev2c: pass declared tails to the relocation test")

patch('''        _run_name = run_dir.name''',
      '''        _run_name = run_dir.name
        _declared_tails = _tails''',
      "rev2d: bind declared tails in the per-file loop")

patch('''    rep.target_dirs = sorted({*discover_target_dirs(run_dir),
                              *(_norm_path(d) for d in extra_target_dirs)})''',
      '''    rep.target_dirs = sorted({*discover_target_dirs(run_dir),
                              *(_norm_path(d) for d in extra_target_dirs)})
    # Repo-relative tails the panel was declared to read. Computed once per run.
    _tails = declared_target_tails(run_dir)''',
      "rev2e: compute declared tails once per run")

if CHECK:
    print("WOULD APPLY:")
    for a in applied:
        print("  +", a)
else:
    F.write_text(text, encoding="utf-8")
    print("APPLIED:")
    for a in applied:
        print("  +", a)
