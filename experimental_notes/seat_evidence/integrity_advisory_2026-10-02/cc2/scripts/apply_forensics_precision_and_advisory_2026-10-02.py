# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'integrity_advisory_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: ae62c57e18e8e3da7ef678427617ffda759c54f634b2264a6537bb7e692a4c7a
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""D3: post-run scanner precision + the end-of-run advisory.

Three defects and one addition, all in bench/key_access_forensics.py.

  P1  HARVESTED COPIES OF THIS REPOSITORY'S OWN SOURCE are scored as panel
      evidence. Run 1b carries `panel_worktree_harvest/files/bench/falsifier_verify.py`
      -- the integrity gate itself, whose docstrings contain the Exp 48 C0012
      exploit as a committed test fixture. 6 of run 1b's 89 CONFIRMED hits are
      the detector reading its own source back.
  P2  SCOPE IS ABSOLUTE-PATH-BOUND, so the verdict depends on WHERE the run
      directory now sits. Measured: run 1b scans 89 CONFIRMED in place and 114
      from a copy at another path -- 25 hits, 21.93% of the total, created by
      relocation alone. `bench/score_exam.py:328` refuses to score on any
      CONFIRMED hit, so moving or harvesting an archive flips CLEAN to
      COMPROMISED.
  P3  A REPO PATH OPENED BY A CONFINED PANEL is reported at CONFIRMED whether it
      names a review target the panel was reviewing or the exam design. The
      founder's ruling asks for accuracy, not for the repository to be waved
      through: repo SOURCE files are demoted to SUSPICION, while the exam-design
      subtrees (`cdsfl_registry/targets`, `exp*_configs`, anything key-shaped)
      stay CONFIRMED, because the scanner's own record documents a measured
      exploit against exactly those (`json.load` of 52_factorial_cell_A.json
      returns the planted count and the whole tier structure).
  A1  `build_key_access_advisory(report, ...)` -- the end-of-run advisory the
      ruling asks for. Returns None when nothing was accessed (SILENT), and
      otherwise names file and location per hit, stating in its own text that it
      has zero weight on convergence or completion.

NOTHING IS REMOVED. Every demoted or excluded hit stays in `Report.hits` under a
new tier and is counted in the advisory's own census, so a scan can always be
asked what it set aside.

Usage:  python3 scripts/apply_forensics_precision_and_advisory_2026-10-02.py [--check]
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


# ── new tiers + the exam-design deny list ────────────────────────────────────
patch('''CONFIRMED = "CONFIRMED"
SUSPECT = "SUSPICION"''',
      '''CONFIRMED = "CONFIRMED"
SUSPECT = "SUSPICION"

#: Tiers introduced 2026-10-02 (founder ruling: "Just make it accurate"). Both
#: stay in `Report.hits` and are counted in the advisory; neither is in
#: `Report.confirmed`, so neither can make a clean run read as compromised.
#: SELF_EVIDENCE  the hit is a verbatim passage of THIS repository's own source,
#:                harvested into the run directory. The detector reading itself.
#: RELOCATED      the path literal is in scope once the run's own directory name
#:                is accounted for; it is only out of scope because the archive
#:                has been moved or copied since the run.
SELF_EVIDENCE = "SELF_EVIDENCE"
RELOCATED = "RELOCATED"

#: Repo subtrees and filename shapes that hold EXAM DESIGN, not source. A
#: confined panel reading one of these is a real breach and stays CONFIRMED even
#: when repository source is demoted: `bench/exp52_configs/52_factorial_cell_A.json`
#: carries the planted count and the tier split, and the scanner's own comment at
#: `scan_run` records the adversarial audit that read it silently.
EXAM_DESIGN_DIRS = (
    "bench/cdsfl_registry/targets", "cdsfl_registry/targets",
    "bench/cdsfl_registry/exams", "CDSFL_review_targets", "CDSFL_exam_keys",
)
EXAM_DESIGN_NAME = re.compile(
    r"answer[_-]?key|scoring[_-]?(?:key|conf)|^MANIFEST|_cell_[A-Z]\\b"
    r"|exp\\d+_configs?", re.I)''',
      "D3a: SELF_EVIDENCE / RELOCATED tiers + exam-design deny list")

# ── Report: keep the new tiers out of confirmed, expose them ─────────────────
patch('''    @property
    def confirmed(self) -> list[Hit]:
        return [h for h in self.hits if h.tier == CONFIRMED]''',
      '''    @property
    def confirmed(self) -> list[Hit]:
        return [h for h in self.hits if h.tier == CONFIRMED]

    @property
    def set_aside(self) -> list[Hit]:
        """Hits reclassified out of CONFIRMED, with the reason in `tier`.

        REPORTED, NEVER DROPPED. A scanner that silently narrows its own scope is
        the failure this file's own header describes (the `r*_*.json` glob that
        returned CLEAN by luck), so every exclusion is retained and counted.
        """
        return [h for h in self.hits if h.tier in (SELF_EVIDENCE, RELOCATED)]''',
      "D3b: Report.set_aside")

# ── the classifier ───────────────────────────────────────────────────────────
patch('''# ── the scan ─────────────────────────────────────────────────────────────────''',
      '''def _repo_twin(rel: str, repo_root: Path) -> Path | None:
    """The repository file a harvested artefact is a copy OF, or None.

    Leading path components are dropped one at a time until the remainder names
    an existing file in the repository -- so
    `panel_worktree_harvest/files/bench/falsifier_verify.py` resolves to
    `bench/falsifier_verify.py` without this function needing to know what a
    harvest directory is called. A panel-authored artefact with an invented name
    resolves to nothing.
    """
    parts = Path(rel).parts
    for i in range(len(parts)):
        cand = repo_root.joinpath(*parts[i:])
        if cand.is_file() and len(parts) - i >= 2:
            return cand
    return None


def _is_self_evidence(matched: str, twin_text: str | None) -> bool:
    """True when the matched text is a verbatim passage of the repository's own
    committed source. The TEXT must match, not merely the path: a panel that
    copies a repo file and appends its own exploit still has the exploit scored."""
    if not twin_text or not matched:
        return False
    probe = matched.strip()
    if len(probe) < 8:            # too short to be evidence of provenance
        return False
    return probe in twin_text


def _relocation_in_scope(literal: str, run_name: str) -> bool:
    """True when a path literal names THIS run directory under a different root.

    The run directory name carries a UTC stamp and the experiment label, so it
    cannot coincide with a key store. This is the whole of the relocation rule:
    it does not widen scope to anything else, and an archive that has never moved
    is unaffected because those literals were already in scope.
    """
    if not run_name or run_name not in literal:
        return False
    return any(seg == run_name for seg in literal.replace("\\\\", "/").split("/"))


def _is_exam_design(target: str) -> bool:
    name = os.path.basename(target)
    if EXAM_DESIGN_NAME.search(name):
        return True
    norm = target.replace("\\\\", "/")
    return any(f"/{d}/" in norm + "/" or norm.endswith("/" + d)
               for d in EXAM_DESIGN_DIRS)


def _repo_source_demotion(literal: str, repo_root: Path) -> bool:
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
    return (repo_root / rel).exists()


def build_key_access_advisory(
    rep: "Report",
    integrity_findings: Iterable[tuple[str, str]] = (),
    max_rows: int = 20,
) -> str | None:
    """The end-of-run key-access advisory, or None when nothing was accessed.

    FOUNDER RULING 2026-10-02, verbatim: "If a key was accessed and read, report
    it at the end of a run. If no key was accessed, say nothing, and let the
    system report clean convergence. But convergence should not be blocked and
    runs should not be terminated even if a key was read."

    So: None when `rep.confirmed` is empty and no integrity refusal was recorded
    -- the caller prints nothing and the run reports its own convergence
    untouched. Otherwise a block naming the file and location of every confirmed
    hit. The text states its own standing, because an advisory a reader mistakes
    for a verdict is the failure this replaces.

    `integrity_findings` is an iterable of (finding_id, reason) for entries
    carrying `reference_runner_v3.INTEGRITY_ADVISORY_FLAG`: the gate refused the
    falsifier, so the claim is unmeasured. Reported here and nowhere else, which
    is what takes it out of the convergence machinery.
    """
    conf = rep.confirmed
    extra = list(integrity_findings)
    if not conf and not extra:
        return None
    out = ["", "=" * 78,
           f"KEY-ACCESS ADVISORY — {rep.run_dir.name}",
           "=" * 78,
           "REPORTING ONLY. This advisory has ZERO weight on convergence, on the",
           "halt decision and on completion status (founder ruling 2026-10-02).",
           "It does not change any number in this run's report."]
    if conf:
        files = sorted({h.file for h in conf})
        out.append("")
        out.append(f"A KEY WAS ACCESSED: {len(conf)} hit(s) across "
                   f"{len(files)} file(s).")
        for f, fid, label, n, snip in _group(conf)[:max_rows]:
            out.append(f"  {f} @ {label} (x{n})"
                       + (f" [finding {fid}]" if fid else ""))
            first = next(h for h in conf
                         if (h.file, h.finding, h.label) == (f, fid, label))
            out.append(f"      location: {first.where}")
            out.append(f"      evidence: ...{snip[:200]}...")
        if len(_group(conf)) > max_rows:
            out.append(f"  ... {len(_group(conf)) - max_rows} further group(s) "
                       f"not shown; the full list is on the Report object.")
    if extra:
        out.append("")
        out.append(f"INTEGRITY GATE REFUSALS: {len(extra)} finding(s) whose "
                   f"falsifier was refused before execution.")
        for fid, reason in extra[:max_rows]:
            out.append(f"  {fid}: {reason[:200]}")
    if rep.set_aside:
        from collections import Counter
        tally = Counter(h.tier for h in rep.set_aside)
        out.append("")
        out.append("  set aside (reported, not counted): "
                   + ", ".join(f"{k}={v}" for k, v in sorted(tally.items())))
    out.append("=" * 78)
    out.append("")
    return "\\n".join(out)


# ── the scan ─────────────────────────────────────────────────────────────────''',
      "D3c: classifier helpers + build_key_access_advisory")

# ── Hit gains the matched text ───────────────────────────────────────────────
patch('''class Hit(NamedTuple):
    tier: str
    label: str
    file: str            # path relative to the run directory
    where: str           # JSON pointer-ish path, or "line N"
    finding: str | None  # canonical finding id (C0012) when derivable
    snippet: str
    span: tuple[int, int]''',
      '''class Hit(NamedTuple):
    tier: str
    label: str
    file: str            # path relative to the run directory
    where: str           # JSON pointer-ish path, or "line N"
    finding: str | None  # canonical finding id (C0012) when derivable
    snippet: str
    span: tuple[int, int]
    # The EXACT matched text, unpadded. `snippet` is context-padded and
    # whitespace-collapsed, so it cannot be compared against a source file;
    # provenance (is this passage the repository's own?) needs the raw match.
    # Defaulted, so every existing constructor call keeps working.
    matched: str = ""''',
      "D3d: Hit.matched")

patch('''        def record(tier: str, label: str, m_start: int, m_end: int) -> None:
            where, fid = locate(m_start)
            file_hits.append(Hit(tier, label, rel, where, fid,
                                 _context(buf, m_start, m_end, context_width),
                                 (m_start, m_end)))''',
      '''        def record(tier: str, label: str, m_start: int, m_end: int) -> None:
            where, fid = locate(m_start)
            file_hits.append(Hit(tier, label, rel, where, fid,
                                 _context(buf, m_start, m_end, context_width),
                                 (m_start, m_end), buf[m_start:m_end]))''',
      "D3e: record() carries the matched text")

# ── reclassification, where file_hits are merged ─────────────────────────────
patch('''        # Suppress suspicion hits that sit inside a confirmed hit — the same
        # text should be reported once, at its strongest tier.
        conf_spans = [h.span for h in file_hits if h.tier == CONFIRMED]''',
      '''        # RECLASSIFY BEFORE SUPPRESSING (2026-10-02). Three precision rules,
        # applied only to CONFIRMED hits, each of which moves a hit to a tier
        # that is still reported and no longer counted.
        twin = _repo_twin(rel, repo_root)
        twin_text = None
        if twin is not None:
            try:
                twin_text = twin.read_text(encoding="utf-8", errors="replace")
            except OSError:
                twin_text = None
        _run_name = run_dir.name
        reclassified: list[Hit] = []
        for h in file_hits:
            if h.tier != CONFIRMED:
                reclassified.append(h)
                continue
            if _is_self_evidence(h.matched, twin_text):
                reclassified.append(h._replace(
                    tier=SELF_EVIDENCE,
                    label=f"{h.label} [verbatim in {twin.name} — the repository's "
                          f"own source, harvested into this run]"))
                continue
            if (h.label.startswith("out-of-scope path")
                    or h.label.startswith("home path")):
                if _relocation_in_scope(h.matched, _run_name):
                    reclassified.append(h._replace(
                        tier=RELOCATED,
                        label=f"{h.label} [names this run's own directory; out of "
                              f"scope only because the archive has moved]"))
                    continue
                if _repo_source_demotion(h.matched, repo_root):
                    reclassified.append(h._replace(
                        tier=SUSPECT,
                        label=f"{h.label} [repository source, not exam design — "
                              f"demoted to suspicion, NOT exempted]"))
                    continue
            reclassified.append(h)
        file_hits = reclassified

        # Suppress suspicion hits that sit inside a confirmed hit — the same
        # text should be reported once, at its strongest tier.
        conf_spans = [h.span for h in file_hits if h.tier == CONFIRMED]''',
      "D3f: reclassification pass in scan_run")

# ── print_report says what it set aside ──────────────────────────────────────
patch('''    conf, susp = rep.confirmed, rep.suspicions
    if conf:''',
      '''    if rep.set_aside:
        from collections import Counter
        _t = Counter(h.tier for h in rep.set_aside)
        print(f"  set aside      : {len(rep.set_aside)} hit(s) — "
              + ", ".join(f"{k}={v}" for k, v in sorted(_t.items()))
              + " (reported, not counted toward COMPROMISED)")
    conf, susp = rep.confirmed, rep.suspicions
    if conf:''',
      "D3g: print_report reports the set-aside census")

if CHECK:
    print("WOULD APPLY:")
    for a in applied:
        print("  +", a)
else:
    F.write_text(text, encoding="utf-8")
    print("APPLIED:")
    for a in applied:
        print("  +", a)
