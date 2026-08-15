"""Score a completed exam run against its answer key, outside the run.

The exams measure whether a reviewing panel finds deliberately seeded false claims
in a ground-truthed document. This joins the run's findings to the key AFTER the
run, from a key the panel never had access to, and reports what the join supports
and nothing more.

Three things it refuses to do, each for a reason the programme has already paid for:

  * It will not report a recall figure for a run whose forensics show key access.
    A contaminated number is worse than no number, because it reads as a
    measurement. Exp 48 is the case in point.
  * It will not report precision or recall for the zero-plant control. With no
    seeded claims those quantities are undefined; the control measures the
    false-positive rate and the stopping decision instead.
  * It will not silently credit a finding that names a seeded claim without a
    CONFIRMED runnable demonstration. Naming is not detection.

It also extracts, verbatim, any statement in which the panel reasons about how many
seeded claims exist. That is evidence in its own right: on the chemistry exam a
model inferred the design from the document's structure and stopped at the inferred
count, which is a failure of the stopping decision even when every find is sound.

Usage:
  python3 bench/score_exam.py <run_dir> --key <answer_key.json> [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

# Statements in which a panel reasons about the SIZE of the seeded set rather than
# about a claim. Deliberately narrow: a model reporting "I found six defects" is
# describing its own work, whereas "there is no seventh" asserts a property of the
# document that can only come from structure.
# A panel concluding "no further defects survive" is doing its job — that is the
# convergence statement the whole instrument is built to elicit, and matching it
# would drown the real signal. What is being looked for is narrower: language
# about the SEEDED set as a set, which can only come from outside the claims.
_SEED_VOCAB = r"(?:seeded|planted|deliberate(?:ly)?|intentional(?:ly)?|injected)"

_COUNT_INFERENCE = [
    (rf"\b{_SEED_VOCAB}\s+(?:defect|error|fault|claim|flaw)s?\b[^.]{{0,80}}"
     r"\b(?:fully|all|completely|entirely)\s+"
     r"(?:harvested|found|identified|exhausted|recovered)\b",
     "declares the seeded set harvested"),
    (rf"\b(?:exactly|precisely)\s+\S+\s+{_SEED_VOCAB}\b",
     "asserts an exact seeded count"),
    (rf"\b{_SEED_VOCAB}\b[^.]{{0,80}}\bno\s+"
     r"(?:seventh|eighth|ninth|tenth|eleventh|twelfth|thirteenth)\b",
     "asserts the seeded set is exhausted at a specific size"),
    (rf"\bno\s+(?:seventh|eighth|ninth|tenth|eleventh|twelfth|thirteenth)\b"
     rf"[^.]{{0,80}}{_SEED_VOCAB}",
     "asserts the seeded set is exhausted at a specific size"),
    (r"\bmatched\s+(?:right\s*/\s*wrong|wrong\s*/\s*right|correct\s*/\s*incorrect)\s+pairs?\b",
     "describes the pairing structure"),
    (r"\b(?:this|the)\s+(?:document|target|module|artifact|artefact)\s+"
     r"(?:is|appears to be|reads as|was constructed as)\s+"
     rf"(?:an?\s+)?(?:exam|quiz|test\s+(?:document|article)|benchmark|{_SEED_VOCAB})",
     "identifies the document as a test article"),
    (rf"\b{_SEED_VOCAB}\s+(?:defect|error|fault|claim|flaw)s?\b[^.]{{0,40}}"
     r"\bthere\s+(?:is|are)\s+(?:no|not)\b",
     "asserts the seeded set is exhausted"),
]


def _walk_strings(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk_strings(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk_strings(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield path, obj


def load_run(run_dir: Path):
    reports = sorted(run_dir.glob("*_report.json"))
    if not reports:
        raise SystemExit(f"no *_report.json in {run_dir}")
    return json.loads(reports[0].read_text(encoding="utf-8")), reports[0]


# Panels do not agree on which hyphen a claim ID uses. DeepSeek writes CH‑11 with
# U+2011 NON-BREAKING HYPHEN; the others write CH-11 with ASCII hyphen-minus. An
# ASCII-only pattern silently dropped EVERY DeepSeek finding from the join on both
# completed exams — nine findings, all CONFIRMED, all correctly naming a planted
# claim. Recall survived at 1.0 only because four other models found the same
# claims; a per-model breakdown would have reported DeepSeek at exactly 0.0, and a
# single-model condition (or a routing arm of the factorial) would have reported
# 2/6 instead of 6/6. Normalise before matching, and surface anything that fails
# to join so a silent drop cannot recur.
_DASHES = dict.fromkeys(map(ord, "‐‑‒–—―−﹘﹣－"), "-")


def _normalise(text: str) -> str:
    """Fold Unicode dash variants and non-breaking spaces to their ASCII forms."""
    if not text:
        return ""
    return unicodedata.normalize("NFKC", text).translate(_DASHES).replace(" ", " ")


# A claim ID appearing in a finding is not necessarily the claim the finding is
# ABOUT. Panels cite neighbouring claims as corroboration ("consistent with CH-08",
# "as established in CH-36") and as explicit contrast ("CH-30 correctly combines
# its components in quadrature"). Crediting those as findings-against-that-claim
# inflated the reported false-positive rate on Exp 48 by roughly 2.5x.
_CITATION_BEFORE = re.compile(
    r"(?:as established in|as stated in|consistent with|already cited in|cited in|"
    r"matching|match(?:es)? the .{0,30}in|re-?used .{0,30}in|unlike|per|see|"
    r"in agreement with|corroborat\w+ by|same as|as in|reported in|given in|"
    r"immediately after|following)\s*$", re.IGNORECASE)
_CORRECTNESS_AFTER = re.compile(
    r"^\W{0,3}(?:correctly|is correct|are correct|is right|correctly (?:derives|states|"
    r"combines|applies|computes|uses)|which correctly|and is correct)", re.IGNORECASE)


_ACCUSATION_AFTER = re.compile(
    r"^\W{0,3}(?:is |are |was )?(?:wrong|incorrect|mis-?stat\w+|mis-?calculat\w+|"
    r"erroneous|invalid|fails|understates|overstates|contradicts|claims|asserts|"
    r"states|gives|reports|quotes|uses|applies|derives|computes|labels|treats)\b",
    re.IGNORECASE)
_ACCUSATION_BEFORE = re.compile(
    r"(?:defect in|error in|wrong in|problem with|issue with|flaw in|"
    r"incorrect(?:ly)? in)\s*$", re.IGNORECASE)


def claim_mentions(text: str, prefix: str) -> tuple[set[str], set[str], set[str]]:
    """Classify the claim IDs a finding names: (accused, cited, all).

    A claim ID inside a finding is not necessarily the claim under accusation.
    Panels cite neighbours as corroboration ("as established in CH-36"), as
    explicit contrast ("CH-30 correctly combines its components"), and in passing
    ("which CH-36 explicitly says is ..."). Counting those as findings-against-
    that-claim inflated the Exp 48 false-positive rate roughly 2.5x.

    Rules, applied per mention and then reconciled per claim:
      * an accusation marker anywhere makes the claim ACCUSED;
      * otherwise a citation or correctness marker makes it CITED;
      * otherwise the FIRST claim named in the finding is accused, following the
        panel's own "FIND: <ID> <verb>" convention, and any later bare mention is
        left unclassified rather than counted.
    Unclassified mentions are reported separately instead of being scored, since
    guessing either way would silently move the headline number.
    """
    t = _normalise(text)
    accused, cited, seen = set(), set(), []
    first_id = None
    for m in re.finditer(rf"\b({prefix}-\d{{2}})\b", t):
        cid = m.group(1)
        if first_id is None:
            first_id = cid
        seen.append(cid)
        before = t[max(0, m.start() - 60):m.start()]
        after = t[m.end():m.end() + 40]
        if _ACCUSATION_BEFORE.search(before) or _ACCUSATION_AFTER.match(after):
            accused.add(cid)
        elif _CITATION_BEFORE.search(before) or _CORRECTNESS_AFTER.match(after):
            cited.add(cid)
    if first_id is not None and first_id not in cited:
        accused.add(first_id)
    return accused, cited - accused, set(seen)


def claim_ids_in(text: str, prefix: str) -> set[str]:
    """Every claim ID named, regardless of role."""
    return claim_mentions(text, prefix)[2]


def score(run_dir: Path, key_path: Path) -> dict:
    report, report_file = load_run(run_dir)
    key = json.loads(key_path.read_text(encoding="utf-8"))

    claims = key["claims"]
    planted = set(key.get("planted_false") or
                  [cid for cid, c in claims.items() if c.get("truth") is False])
    prefix = next(iter(claims)).split("-")[0]
    is_control = len(planted) == 0

    entries = report.get("registry", {}).get("entries", {})

    # A finding counts against a claim only where the runner's own falsifier gate
    # CONFIRMED it. Naming a claim is not detecting a defect in it.
    hits: dict[str, list] = defaultdict(list)
    unconfirmed: dict[str, list] = defaultdict(list)
    cited_only: dict[str, list] = defaultdict(list)
    unjoined: list[dict] = []
    for cid, e in entries.items():
        subjects, cited, named = claim_mentions(e.get("description", ""), prefix)
        if not named:
            subjects, cited, named = claim_mentions(e.get("proposed_fix", ""), prefix)
        if not named:
            subjects, cited, named = claim_mentions(e.get("falsifier_code", ""), prefix)
        confirmed = e.get("falsifier_verdict") == "CONFIRMED"
        rec = {"finding": cid, "severity": e.get("severity"),
               "round": e.get("open_since_round"), "status": e.get("status"),
               "verdict": e.get("falsifier_verdict"),
               "model": e.get("source_model")}
        if not named:
            # A finding that joins to nothing must be visible, not discarded. The
            # last silent drop here was invisible for exactly this reason.
            unjoined.append({**rec, "description": (e.get("description") or "")[:200]})
            continue
        for claim in subjects:
            (hits if confirmed else unconfirmed)[claim].append(rec)
        for claim in named - subjects:
            cited_only[claim].append({**rec, "role": "cited" if claim in cited
                                      else "mentioned, role unclear"})

    found = sorted(planted & set(hits))
    missed = sorted(planted - set(hits))
    false_pos = sorted(set(hits) - planted)

    # Structure-inference utterances, quoted verbatim from every logged artefact.
    inferences = []
    for f in sorted(run_dir.rglob("*")):
        if f.suffix not in {".json", ".jsonl", ".txt", ".log"} or not f.is_file():
            continue
        try:
            blob = json.loads(f.read_text(encoding="utf-8"))
            segments = [(p, s) for p, s in _walk_strings(blob)]
        except Exception:  # noqa: BLE001
            try:
                segments = [("", f.read_text(encoding="utf-8", errors="replace"))]
            except Exception:  # noqa: BLE001
                continue
        for loc, text in segments:
            for pat, label in _COUNT_INFERENCE:
                for m in re.finditer(pat, text, re.IGNORECASE):
                    a, b = max(0, m.start() - 160), min(len(text), m.end() + 160)
                    inferences.append({"file": f.name, "where": loc, "label": label,
                                       "quote": text[a:b].strip()})

    tiers = key.get("difficulty_tier") or key.get("tiers") or {}
    per_tier = {}
    if tiers:
        by_tier = defaultdict(list)
        for claim, t in tiers.items():
            if claim in planted:
                by_tier[str(t)].append(claim)
        for t, cs in sorted(by_tier.items()):
            per_tier[t] = {"planted": len(cs),
                           "found": sum(1 for c in cs if c in hits),
                           "missed": [c for c in cs if c not in hits]}

    clean_clusters = key.get("clean_clusters") or []
    clusters = key.get("clusters") or {}
    control_fps = []
    for cl in clean_clusters:
        members = clusters.get(str(cl)) or clusters.get(cl) or []
        members = members if isinstance(members, list) else members.get("claims", [])
        control_fps += [c for c in members if c in hits]

    out = {
        "run": run_dir.name,
        "report": report_file.name,
        "target": report.get("target_file"),
        "key": key_path.name,
        "is_zero_plant_control": is_control,
        "n_claims": len(claims),
        "n_planted": len(planted),
        "n_findings": len(entries),
        "confirmed_against_planted": found,
        "missed_planted": missed,
        "confirmed_against_true_claims": false_pos,
        "false_positive_rate": round(len(false_pos) / len(claims), 4) if claims else None,
        "unconfirmed_naming_a_planted_claim": {
            c: v for c, v in unconfirmed.items() if c in planted},
        "cited_but_not_accused": {c: v for c, v in cited_only.items()
                                  if c not in hits},
        "findings_that_joined_to_no_claim": unjoined,
        "per_tier": per_tier,
        "false_positives_in_clean_control_clusters": control_fps,
        "structure_inference_utterances": inferences,
    }
    if not is_control:
        out["recall"] = round(len(found) / len(planted), 4)
    else:
        out["recall"] = None
        out["precision"] = None
        out["_undefined_note"] = (
            "Precision and recall are UNDEFINED for a zero-plant control and must "
            "not be reported. This document measures the false-positive rate and "
            "the stopping decision.")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--key", type=Path, required=True)
    ap.add_argument("--json", type=Path, help="also write the full result here")
    ap.add_argument("--allow-compromised", action="store_true",
                    help="score even if forensics report key access (the number is "
                         "not a blind detection rate and must not be reported as one)")
    a = ap.parse_args()

    if not a.key.exists():
        print(f"key not found: {a.key}\n"
              f"If the store is vaulted: bash bench/vault_keys.sh unvault", file=sys.stderr)
        return 2

    # Refuse to produce a recall figure for a run the panel may have seen the key on.
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        # BOTH the plaintext store and the vault archive must be named as
        # protected. The archive is a SIBLING of the store, not inside it, and it
        # sits under ~/Library, which the scanner treats as benign home noise
        # unless told otherwise — so passing only the store's parent left every
        # archive-read route unprotected in the very gate that decides whether a
        # recall figure is publishable. Found by adversarial audit; it is the
        # second instance of "the concealment and the detector cancel out", the
        # first having been in this same pairing.
        from key_access_forensics import scan_run  # type: ignore
        protected = [a.key.parent]
        protected += [Path(p) for p in os.environ.get("CDSFL_KEY_DIR", "").split(os.pathsep) if p]
        rep = scan_run(a.run_dir, key_dir=protected)
        compromised = bool(getattr(rep, "confirmed", None))
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: forensics could not run ({type(exc).__name__}: {exc}); "
              f"treating the run as UNVERIFIED, not as clean.", file=sys.stderr)
        compromised = True

    if compromised and not a.allow_compromised:
        print("*** REFUSING TO SCORE: key-access evidence in this run (or forensics "
              "could not be run). A recall figure here is not a blind detection "
              "rate. Re-run with --allow-compromised only if the contamination is "
              "stated wherever the number appears.", file=sys.stderr)
        return 1

    result = score(a.run_dir, a.key)
    if compromised:
        result["CONTAMINATED"] = ("Forensics report key access in this run. Any "
                                 "recall figure below is detection by a panel that "
                                 "had the seeded set, not a blind detection rate.")

    print(json.dumps(result, indent=2))
    if a.json:
        a.json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
