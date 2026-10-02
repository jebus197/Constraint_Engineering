# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'integrity_advisory_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 82d97efbb4fb1f87dd5113597c5de8cc14dc5db2c03a5b6c36baa2731c907930
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Revision 5: two defects in MY OWN D1/D3 implementation, both found by
committed oracles rather than by reading.

  V1  `open('scoring_key.json')` and `open('MANIFEST.md').read()` stopped being
      refused. `bench/tests/test_falsifier_cannot_read_the_key.py` pins both, and
      it is right: those are ACCESSES, not vocabulary. The brief's
      access/vocabulary split is not a clean partition over the shipped rule
      list -- `scoring[_-]?key` and `MANIFEST` are vocabulary in prose and access
      inside a read construct. A read-construct rule restores both without
      restoring the prose refusal.

  V2  My EXAM_DESIGN_DIRS named `CDSFL_review_targets` and `CDSFL_exam_keys` in
      `bench/key_access_forensics.py`, breaking that file's first load-bearing
      property -- "It names no protected path" -- which
      `test_key_access_forensics.py::test_scanner_source_names_no_protected_path`
      exists to enforce. The names are removed. Nothing is lost: an exam-key path
      is already matched by the generic `answer[_-]key` rule, and a staged target
      directory arrives at run time through `discover_target_dirs`.

Usage:  python3 scripts/apply_key_access_rev5_repairs_2026-10-02.py [--check]
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
CHECK = "--check" in sys.argv
applied: list[str] = []


def patch(rel: str, anchor: str, new: str, tag: str) -> None:
    p = REPO / rel
    text = p.read_text(encoding="utf-8")
    if new in text:
        print(f"  = {tag} (already applied)")
        return
    if text.count(anchor) != 1:
        raise SystemExit(f"ANCHOR NOT UNIQUE for {tag}: {text.count(anchor)}")
    if not CHECK:
        p.write_text(text.replace(anchor, new, 1), encoding="utf-8")
    applied.append(tag)


patch("bench/falsifier_verify.py",
      '''    (re.compile(r"CDSFL_(?:STORE|VAULT|TARGETS|KEY_DIR|LEGACY_STORES|SCORING_CONF)"),
     "a protected environment variable by name"),
)''',
      '''    (re.compile(r"CDSFL_(?:STORE|VAULT|TARGETS|KEY_DIR|LEGACY_STORES|SCORING_CONF)"),
     "a protected environment variable by name"),
    # A KEY ARTEFACT OPENED BY NAME. `scoring_key` and `MANIFEST` are vocabulary
    # in prose and ACCESS inside a read construct, so the access/vocabulary split
    # does not fall cleanly along the shipped rule list. Restored here as an
    # access rule, which keeps `open('scoring_key.json')` and
    # `open('MANIFEST.md').read()` refused -- both pinned by
    # bench/tests/test_falsifier_cannot_read_the_key.py -- while leaving a
    # sentence that merely mentions a scoring key alone.
    (re.compile(
        r"(?:open|read_text|read_bytes|readlines|json\\.load|load|loads|Path"
        r"|cat|head|tail|less|more|grep|rg|jq|tarfile\\.open|gzip\\.open)"
        rf"\\s*\\(\\s*{_Q}?[\\w./~$-]*"
        r"(?:scoring[_\\- ]?(?:key|conf)|MANIFEST|answer[_\\- ]?key"
        r"|planted[_\\- ]?false)[\\w.-]*", re.I),
     "a key artefact opened by name"),
)''', "rev5a: key artefact opened by name is an ACCESS rule")

patch("bench/key_access_forensics.py",
      '''EXAM_DESIGN_DIRS = (
    "bench/cdsfl_registry/targets", "cdsfl_registry/targets",
    "bench/cdsfl_registry/exams", "CDSFL_review_targets", "CDSFL_exam_keys",
)''',
      '''#: REPOSITORY-RELATIVE ONLY. This file names no protected path -- property 1 of
#: its own header, enforced by
#: test_key_access_forensics.py::test_scanner_source_names_no_protected_path.
#: An operator-side key or staged-target directory must NOT be listed here: the
#: generic `answer[_-]key` rule already matches the former, and the latter
#: arrives at run time through `discover_target_dirs` / `--target-dir`.
EXAM_DESIGN_DIRS = (
    "bench/cdsfl_registry/targets", "cdsfl_registry/targets",
    "bench/cdsfl_registry/exams",
)''', "rev5b: forensics names no protected path")

patch("scripts/guard_false_positive_blind_spot_2026-10-02.py",
      '''    tracked = subprocess.run(["git", "ls-files"], cwd=REPO,''',
      '''    # FAILS LOUD, NOT OPEN (2026-10-02, panel). This enumerator had no
    # return-code check, so in any tree that is not a git checkout -- a harvested
    # sandbox, an exported tarball, a clone with no .git -- `git ls-files`
    # returned nothing and section 4 printed "0 across 0 files". A census that
    # reports zero because its enumerator died is indistinguishable from a census
    # that found nothing, and the guard written to protect this very exclusion
    # (test_the_census_excludes_the_documents_written_about_the_token) then
    # compares 0 < 0 and cannot see the difference either.
    _probe = subprocess.run(["git", "ls-files"], cwd=REPO,
                            capture_output=True, text=True)
    if _probe.returncode != 0 or not _probe.stdout.strip():
        raise SystemExit(
            "REFUSING TO REPORT A CENSUS: `git ls-files` returned "
            f"{_probe.returncode} with {len(_probe.stdout.strip())} bytes in "
            f"{REPO}. The population of section 4 is DEFINED as the tracked "
            "files, so with no tracked file list every figure below it would "
            "read 0 and look like a measurement. Run this in a git checkout.")
    tracked = subprocess.run(["git", "ls-files"], cwd=REPO,''',
      "rev5c: the census producer refuses to report a vacuous population")

print("WOULD APPLY:" if CHECK else "APPLIED:")
for a in applied:
    print("  +", a)
