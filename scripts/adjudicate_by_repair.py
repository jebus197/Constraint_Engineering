#!/usr/bin/env python3
"""Decide "same defect or two?" by REPAIR, not by opinion.

WHY THIS EXISTS
---------------
The similarity function's accuracy was measured against labels from a
sentence-embedding model, which refused to call 133 of the 460 pairs. Those were
silently dropped, so every error rate computed from the rest is optimistic by an
unknown amount.

Two ways of closing that gap were proposed and both were wrong. Asking the
founder to adjudicate put a chemistry/engineering/programming judgement in front
of the one participant with no domain access, and it is not an HIL-irreducible
question. Asking a model panel to vote was worse: CDSFL is a tools-decide
harness, and `pr` runs under `sy` and `f` for exactly that reason. A panel
eyeballing pairs and voting is the free pass the whole project exists to refuse.

There is a tool that decides this, and the project already names it as its
ground-truth method: COUNTERFACTUAL REPAIR.

  Apply A's proposed fix to the target. Re-run BOTH falsifiers.
    - B's falsifier now passes too -> A's repair cured B -> SAME defect.
    - B's falsifier still fails     -> B survived A's repair -> DIFFERENT.

Run it in both directions and require the two to agree. No votes, no opinions,
no API spend. The runner already owns this decision everywhere else via
CONFIRM-only; this just applies it to a question it was never pointed at.

WHAT HAD TO BE FIXED FIRST
--------------------------
The first attempt decided ZERO pairs. `endocrine._apply_fix_to_source` could not
parse a single fix the runner produces, because the emitter and the parser
disagreed twice over the same block:

  emitter (runner_core.py:886):  `<<<< SEARCH <path>` / `==== REPLACE` / `>>>>`
  parser  (endocrine.py:589+):   required `====` EXACTLY, and the word REPLACE
                                 on the CLOSING line

Both conditions are false for every runner-emitted fix. The parser also gated on
`"SEARCH" in line`, rejecting the `<<<< OLD` form the same emitter produces when
there is no file hint. With those three corrected, 129 of 153 archived fixes on
the code targets apply, against 0 before.

HONEST BOUNDS
-------------
* A pair is decided only when BOTH falsifiers reproduce CONFIRMED on the
  unmodified target first. A falsifier that no longer fires is not evidence.
* Both directions must agree. Disagreement is reported as DISAGREE, not resolved
  by preferring one side.
* If a finding's own fix does not cure its own falsifier, the pair is
  INCONCLUSIVE — the fix is ineffective and can say nothing about the other.
* The target file is restored in a `finally`. It is checked byte-identical at
  the end and the script fails loudly if it is not.
* Exam targets (Exp 48/49) are markdown; a falsifier for a prose claim does not
  read the document, so repair cannot propagate. Those pairs are out of scope
  here and are reported as such rather than silently skipped.

Usage
-----
    python3 scripts/adjudicate_by_repair.py --dry-run
    python3 scripts/adjudicate_by_repair.py --run exp44
    python3 scripts/adjudicate_by_repair.py            # all code targets
"""
from __future__ import annotations

import argparse
import hashlib
import re
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from bench.endocrine import _apply_fix_to_source  # noqa: E402
from bench.falsifier_verify import reverify_falsifier  # noqa: E402

# Only runs whose target is Python and still on disk. The two exam runs are
# excluded by construction and reported separately.
TARGETS = {
    "exp44": ("exp44_evidence_locationkey_live", "bench/evidence.py"),
    "exp45": ("exp45_memory_statistics_live", "bench/dm/_memory.py"),
    "exp46": ("exp46_stage6_locationkey_live", "bench/dm/_shadow_stage6.py"),
    "exp47": ("exp47_divergence_locationkey_live", "bench/dm/_divergence.py"),
}
PAIRS = REPO / "experimental_notes" / "data" / "similarity_pairs_backfilled.json"
OUT = REPO / "experimental_notes" / "data" / "adjudication_by_repair.json"

_cache: dict = {}

# Where the off-repo exam papers live, and every path an exp48/49 falsifier is
# known to open. The papers are TARGETS, not answer keys — the key vault stays
# sealed and untouched — but they are deliberately kept out of the repository, so
# they are staged only for the duration of a run and removed in a `finally`.
AWAY = pathlib.Path.home() / "Library" / "Application Support" / "cdsfl-targets.away"
EXAMS = {
    "exp48": ("exp48_chemistry_exam_live", "exp48_chemistry.md"),
    "exp49": ("exp49_engineering_exam_live", "exp49_engineering.md"),
}


def _exam_paths(doc: str) -> list:
    return [REPO / doc,
            REPO / "bench" / "cdsfl_registry" / "targets" / doc,
            pathlib.Path.home() / "CDSFL_review_targets" / doc]


def _versions(target_rel: str) -> list:
    """Every stored version of a target, newest first, ACROSS ALL REFS.

    `--all` is load-bearing. Searching only the current branch found five
    versions of bench/evidence.py and led to the conclusion that a finding's
    run-time state no longer existed; the branch `exp39-experimental` holds 107
    commits main does not, because the milestone merge squashed them.
    """
    import subprocess
    out = subprocess.run(["git", "log", "--all", "--format=%h", "--", target_rel],
                         capture_output=True, text=True, cwd=str(REPO)).stdout
    vers = []
    for sha in out.strip().splitlines():
        txt = subprocess.run(["git", "show", f"{sha}:{target_rel}"],
                             capture_output=True, text=True, cwd=str(REPO)).stdout
        if txt:
            vers.append((sha, txt))
    return vers


def _md_normalise(text: str) -> str:
    """Strip markdown emphasis and collapse whitespace.

    WHY. On the prose targets the models' SEARCH blocks matched almost nothing —
    2 of 33 for exp48, 7 of 32 for exp49, and identically across EVERY stored
    version of both papers. That looked like paraphrase, which would have made
    the fixes unusable and the pairs undecidable.

    It was not paraphrase. Median similarity between a SEARCH block and its true
    paragraph is 0.99, and the whole difference is markdown emphasis: the paper
    says `**EN-06.**`, the model quotes `EN-06.`. Models strip formatting when
    they quote. Normalising both sides takes the locatable share from 14% to 80%
    with no fuzzy threshold to tune and no risk of matching the wrong passage on
    a similarity score.
    """
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", text or "")
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", t)
    t = re.sub(r"`([^`]*)`", r"\1", t)
    return re.sub(r"\s+", " ", t).strip()


def _apply_prose_fix(doc: str, proposed_fix: str) -> str | None:
    """Apply a SEARCH/REPLACE fix to a PROSE target, matching on normalised form.

    Paragraph-scoped deliberately: the claim being repaired is one paragraph, and
    replacing a whole paragraph cannot corrupt a neighbouring claim the way an
    offset-based splice could.

    PRECEDENCE, and ambiguity is refused rather than guessed:
      1. A UNIQUE exact match wins. Several exact matches -> None.
      2. Otherwise a UNIQUE match on normalised form. Several -> None.
      3. No match -> None.
    Rule 1 outranks rule 2 on purpose: if the model's quote appears verbatim
    exactly once, that is a stronger signal than a formatting-insensitive match
    elsewhere, even when both exist. Every None leaves the pair undecided, which
    is the correct failure direction — a wrongly-placed repair would produce a
    confident and false SAME/DIFFERENT verdict.
    """
    m = re.search(r"^<{4,}[^\n]*\n(.*?)\n^={4,}[^\n]*$\n(.*?)(?:\n^>{4,}|\Z)",
                  proposed_fix or "", re.M | re.S)
    if not m:
        return None
    search, replace = m.group(1).strip(), m.group(2).strip()
    if not search or not replace:
        return None
    if search in doc:
        # Ambiguity is refused on this path too. An earlier draft returned
        # `doc.replace(search, replace, 1)` here, which silently patched the FIRST
        # of several identical passages while the docstring claimed ambiguity was
        # refused. The unit test below caught the docstring, not the code.
        if doc.count(search) != 1:
            return None
        return doc.replace(search, replace, 1)
    want = _md_normalise(search)
    if not want:
        return None
    paras = re.split(r"(\n\s*\n)", doc)
    hits = [i for i, p in enumerate(paras)
            if i % 2 == 0 and want and want in _md_normalise(p)]
    if len(hits) != 1:
        return None                      # absent, or ambiguous — refuse to guess
    paras[hits[0]] = replace
    return "".join(paras)


def _verdict(code: str, state_key: str, timeout: int = 20) -> str:
    """Re-run a falsifier. Cached on (target state, falsifier) — the same
    falsifier against the same file content cannot give a different answer, and
    a pair set re-runs the same falsifier many times."""
    if not (code or "").strip():
        return "NO_FALSIFIER"
    key = (state_key, hashlib.sha256(code.encode("utf-8", "replace")).hexdigest())
    if key not in _cache:
        try:
            _cache[key] = reverify_falsifier(code, repo_root=str(REPO), timeout=timeout)
        except Exception as exc:                      # noqa: BLE001 - reported, not swallowed
            _cache[key] = f"ERROR:{type(exc).__name__}"
    return _cache[key]


def _direction(fixer: dict, other: dict, target: pathlib.Path,
               orig: str, orig_key: str) -> tuple[str, str]:
    """Apply `fixer`'s fix; report what happens to both falsifiers."""
    patched = _apply_fix_to_source(orig, fixer.get("proposed_fix") or "")
    if not patched or patched == orig:
        return "NO_APPLICABLE_FIX", ""
    state = hashlib.sha256(patched.encode()).hexdigest()[:16]
    try:
        target.write_text(patched, encoding="utf-8")
        v_self = _verdict(fixer.get("falsifier_code") or "", state)
        v_other = _verdict(other.get("falsifier_code") or "", state)
    finally:
        target.write_text(orig, encoding="utf-8")
    d = f"self={v_self} other={v_other}"
    if v_self == "CONFIRMED":
        # The fix does not cure its own falsifier. A real observation about the
        # FIX, and it holds whatever `other` did.
        return "FIX_INEFFECTIVE", d
    # SAME used to be the fall-through, so an ERRORed leg did not merely
    # contaminate a verdict -- it PRODUCED one. Panel-flagged 2026-08-28 for the
    # 12 contaminated SAME rows; following it into this function found 40 of 178
    # leg-bearing directions affected across 34 of 133 pairs, because the
    # fall-through reaches DIFFERENT too. A verdict now requires legs that can
    # carry it: an equipment failure is reported as equipment failure.
    if v_self != "REFUTED" or v_other not in ("REFUTED", "CONFIRMED"):
        return "INCONCLUSIVE_EQUIPMENT", d
    if v_other == "CONFIRMED":
        return "DIFFERENT", d
    return "SAME", d


def adjudicate(run: str, stem: str, target_rel: str, band: list) -> list:
    target = REPO / target_rel
    if not target.is_file():
        return []
    dirs = [d for d in (REPO / "bench" / "logs").glob(f"{stem}_*") if d.is_dir()]
    if not dirs:
        return []
    reports = [p for p in dirs[0].glob("*_report.json") if ".errata" not in str(p)]
    if not reports:
        return []
    ents = json.loads(reports[0].read_text(encoding="utf-8"))["registry"]["entries"]

    orig = target.read_text(encoding="utf-8")
    orig_key = hashlib.sha256(orig.encode()).hexdigest()[:16]
    versions = _versions(target_rel)
    rows = []
    try:
        for p in [x for x in band if x["run"] == run]:
            A, B = ents.get(p["a"]), ents.get(p["b"])
            if not (A and B):
                continue
            # Precondition: both falsifiers must reproduce on the pristine file.
            va = _verdict(A.get("falsifier_code") or "", orig_key)
            vb = _verdict(B.get("falsifier_code") or "", orig_key)
            base, base_key, base_sha = orig, orig_key, "HEAD"
            if va != "CONFIRMED" or vb != "CONFIRMED":
                # VERSION SEARCH. A falsifier that does not fire against today's
                # file has usually had its defect repaired since, not been wrong.
                # Walk the stored versions for one where BOTH reproduce, and
                # adjudicate there — that is the state the finding was raised
                # against. 20 of 21 such findings reproduce somewhere.
                found = None
                for sha, txt in versions:
                    k = hashlib.sha256(txt.encode()).hexdigest()[:16]
                    try:
                        target.write_text(txt, encoding="utf-8")
                        if (_verdict(A.get("falsifier_code") or "", k) == "CONFIRMED"
                                and _verdict(B.get("falsifier_code") or "", k) == "CONFIRMED"):
                            found = (sha, txt, k)
                            break
                    finally:
                        target.write_text(orig, encoding="utf-8")
                if not found:
                    rows.append({"run": run, "a": p["a"], "b": p["b"],
                                 "verdict": "NO_BASELINE", "detail": f"{va}/{vb} (no version reproduces both)"})
                    continue
                base_sha, base, base_key = found[0], found[1], found[2]
            fwd, d1 = _direction(A, B, target, base, base_key)
            rev, d2 = _direction(B, A, target, base, base_key)
            if fwd == rev and fwd in ("SAME", "DIFFERENT"):
                verdict = fwd
            elif "SAME" in (fwd, rev) and "DIFFERENT" in (fwd, rev):
                verdict = "DISAGREE"
            elif fwd in ("SAME", "DIFFERENT"):
                verdict = fwd + "_ONE_WAY"
            elif rev in ("SAME", "DIFFERENT"):
                verdict = rev + "_ONE_WAY"
            else:
                verdict = "UNDECIDABLE"
            rows.append({"run": run, "a": p["a"], "b": p["b"], "verdict": verdict,
                         "forward": fwd, "reverse": rev, "baseline": base_sha,
                         "detail": f"{d1} | {d2}"})
    finally:
        target.write_text(orig, encoding="utf-8")
    if target.read_text(encoding="utf-8") != orig:
        raise SystemExit(f"FATAL: {target} was not restored")
    return rows


def adjudicate_exam(run: str, stem: str, doc: str, band: list) -> list:
    """Exam runs (Exp 48/49). Same method, different plumbing.

    An earlier note in this file said exam pairs were out of scope because "a
    falsifier for a prose claim does not read the document". That was an
    assumption and it was wrong: 25 of exp49's 33 falsifiers open the target by
    path and recompute from its own inputs, so repair propagates exactly as it
    does for code. The real obstacle was mundane — the papers are held off-repo,
    so the path the falsifier opens does not exist.

    The papers are TARGETS, not answer keys. The key vault is untouched and stays
    sealed. They are copied in for the duration of the run and removed in a
    `finally`; nothing is committed.
    """
    src = AWAY / doc
    if not src.is_file():
        return []
    dirs = [d for d in (REPO / "bench" / "logs").glob(f"{stem}_*") if d.is_dir()]
    if not dirs:
        return []
    reports = [x for x in dirs[0].glob("*_report.json") if ".errata" not in str(x)]
    if not reports:
        return []
    ents = json.loads(reports[0].read_text(encoding="utf-8"))["registry"]["entries"]
    orig = src.read_text(encoding="utf-8")
    orig_key = hashlib.sha256(orig.encode()).hexdigest()[:16]

    staged = []
    rows = []
    try:
        for path in _exam_paths(doc):
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(orig, encoding="utf-8")
                staged.append(path)
            except OSError:
                pass                      # read-only location; the others suffice
        if not staged:
            return []
        primary = staged[0]

        def write_all(text: str) -> None:
            for q in staged:
                try:
                    q.write_text(text, encoding="utf-8")
                except OSError:
                    pass

        def direction(fixer, other):
            patched = (_apply_fix_to_source(orig, fixer.get("proposed_fix") or "")
                       or _apply_prose_fix(orig, fixer.get("proposed_fix") or ""))
            if not patched or patched == orig:
                return "NO_APPLICABLE_FIX", ""
            k = hashlib.sha256(patched.encode()).hexdigest()[:16]
            try:
                write_all(patched)
                vs = _verdict(fixer.get("falsifier_code") or "", k)
                vo = _verdict(other.get("falsifier_code") or "", k)
            finally:
                write_all(orig)
            if vs == "CONFIRMED":
                return "FIX_INEFFECTIVE", f"self={vs} other={vo}"
            if vo == "CONFIRMED":
                return "DIFFERENT", f"self={vs} other={vo}"
            return "SAME", f"self={vs} other={vo}"

        for p in [x for x in band if x["run"] == run]:
            A, B = ents.get(p["a"]), ents.get(p["b"])
            if not (A and B):
                continue
            va = _verdict(A.get("falsifier_code") or "", orig_key)
            vb = _verdict(B.get("falsifier_code") or "", orig_key)
            if va != "CONFIRMED" or vb != "CONFIRMED":
                rows.append({"run": run, "a": p["a"], "b": p["b"],
                             "verdict": "NO_BASELINE", "detail": f"{va}/{vb}"})
                continue
            fwd, d1 = direction(A, B)
            rev, d2 = direction(B, A)
            if fwd == rev and fwd in ("SAME", "DIFFERENT"):
                verdict = fwd
            elif "SAME" in (fwd, rev) and "DIFFERENT" in (fwd, rev):
                verdict = "DISAGREE"
            elif fwd in ("SAME", "DIFFERENT"):
                verdict = fwd + "_ONE_WAY"
            elif rev in ("SAME", "DIFFERENT"):
                verdict = rev + "_ONE_WAY"
            else:
                verdict = "UNDECIDABLE"
            rows.append({"run": run, "a": p["a"], "b": p["b"], "verdict": verdict,
                         "forward": fwd, "reverse": rev, "detail": f"{d1} | {d2}"})
    finally:
        for q in staged:
            try:
                q.unlink()
            except OSError:
                pass
    left = [q for q in staged if q.exists()]
    if left:
        raise SystemExit(f"FATAL: staged exam target not removed: {left}")
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", help="limit to one run, e.g. exp44")
    ap.add_argument("--dry-run", action="store_true", help="report scope, execute nothing")
    args = ap.parse_args()

    data = json.loads(PAIRS.read_text(encoding="utf-8"))
    band = [p for p in data["pairs"] if p.get("label") is None]
    in_scope = [p for p in band if p["run"] in TARGETS]
    exam = [p for p in band if p["run"] not in TARGETS]
    print(f"  unadjudicated pairs      : {len(band)}")
    print(f"  code targets (in scope)  : {len(in_scope)}")
    print(f"  exam targets (staged from the off-repo store): {len(exam)}")
    if args.dry_run:
        return 0

    rows = []
    for run, (stem, tgt) in TARGETS.items():
        if args.run and run != args.run:
            continue
        r = adjudicate(run, stem, tgt, in_scope)
        rows += r
        print(f"    {run}: {len(r)} pairs processed")
    for run, (stem, doc) in EXAMS.items():
        if args.run and run != args.run:
            continue
        r = adjudicate_exam(run, stem, doc, exam)
        rows += r
        print(f"    {run}: {len(r)} exam pairs processed")

    counts: dict = {}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    print("\n  VERDICTS (by repair, not by opinion):")
    for k, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"    {k:22s} {n}")
    decided = sum(n for k, n in counts.items() if k in ("SAME", "DIFFERENT"))
    print(f"\n  decided both directions agreeing: {decided}/{len(rows)}")
    OUT.write_text(json.dumps({"rows": rows, "counts": counts}, indent=1), encoding="utf-8")
    print(f"  written: {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
