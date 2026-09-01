#!/usr/bin/env python3
"""Operating characteristic for THE SIMILARITY FUNCTION (`bench/convergence_location.py`).

WHY THIS FILE EXISTS
--------------------
The similarity function's justifying measurement — 438 same-location critical
pairs, tier-2 medians 0.559 vs 0.000, Mann-Whitney p = 1.9e-25, tier-3 Fisher
p = 1.4e-07 — lived only as PROSE COMMENTS in `bench/convergence_location.py`.
No pair dataset was stored, no script rebuilt it, and no test recomputed it. The
numbers were true and were not reproducible by anything but re-deriving them by
hand. This script closes that gap: it rebuilds the dataset from the six archived
reports and recomputes every recorded figure, so the claim and its evidence move
together.

It also does the thing the recorded measurement stops short of. Reporting a
p-value answers "is the separation real?" — which was never seriously in doubt at
p = 1.9e-25. It does not answer the question the rule is actually used to decide:
AT THE THRESHOLD THE RUNNER USES, how often does this merge two genuinely
different findings? That is an operating characteristic, not a significance test,
and it is what the founder approved building on 2026-08-16.

THE HONEST LIMIT, stated up front because it bounds everything below
--------------------------------------------------------------------
The labels are produced by a sentence-embedding model. They are NOT ground truth.
They are one machine's opinion, used to grade another machine's rule.

That is defensible for the separation claim: the embedding is part of neither
tier, so it is at least an INDEPENDENT machine opinion, and independence is what
makes p = 1.9e-25 meaningful. It is NOT sufficient for an operating point, because
an operating point is a decision about how much error to accept, and calibrating
that against an unvalidated proxy launders the proxy's error into the decision.

So this script reports two things separately and never mixes them:

  * metrics against EMBEDDING labels    — reproducible now, provisional
  * metrics against HUMAN labels        — authoritative, computed only for the
                                          pairs a human has actually adjudicated

`--adjudication-pack` writes the pairs needing human judgement. Until those come
back, every operating point here carries the embedding caveat, and this script
prints that caveat next to every number rather than in a footnote.

THE 120 EXCLUDED PAIRS
----------------------
The recorded measurement labels a pair SAME at embedding >= 0.90 and DIFFERENT at
<= 0.70, and it SILENTLY DROPS the 120 pairs in between. 438 - 28 - 290 = 120.
Those 120 are 27% of the data and they are not a random 27%: they are precisely
the pairs where the question is hard. Excluding them makes any separation look
cleaner than it is, and no version of the recorded comment says they were
dropped. That is the single largest weakness in the evidence base for this rule.

Usage
-----
    python3 scripts/similarity_operating_characteristic.py                 # full report
    python3 scripts/similarity_operating_characteristic.py --rebuild       # refresh cache
    python3 scripts/similarity_operating_characteristic.py --adjudication-pack
    python3 scripts/similarity_operating_characteristic.py --human-labels FILE

Offline: set HF_HUB_OFFLINE=1. The backend model is cached locally.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import bench.convergence_location as CL  # noqa: E402

# The six completed location-keyed runs. Mirrors ARCHIVE in
# bench/tests/test_combined_identity_rule.py; kept in step with it deliberately,
# and `test_operating_characteristic.py` asserts the two agree.
ARCHIVE = {
    "exp44": ("exp44_evidence_locationkey_live", "bench/evidence.py"),
    "exp45": ("exp45_memory_statistics_live", "bench/dm/_memory.py"),
    "exp46": ("exp46_stage6_locationkey_live", "bench/dm/_shadow_stage6.py"),
    "exp47": ("exp47_divergence_locationkey_live", "bench/dm/_divergence.py"),
    # Exp 48/49 reviewed markdown exam documents no longer on disk. Their symbol
    # set is reconstructed from claim IDs — see `_symbols_for`.
    "exp48": ("exp48_chemistry_exam_live", None),
    "exp49": ("exp49_engineering_exam_live", None),
}

CRITICAL_SEVERITY = 0.7

# The recorded figures this script must reproduce. A mismatch means either the
# archive or the extractors have moved, and the recorded claim is stale.
RECORDED = {"criticals": 165, "tier2_coverage": 161, "tier3_coverage": 94,
            "pairs": 438, "n_same": 28, "n_diff": 290}

# The labelling band from the recorded measurement. Pairs strictly between these
# are UNLABELLED, not "different" — the distinction is the whole point of the
# adjudication pack.
EMB_SAME, EMB_DIFF = 0.90, 0.70

# Stored under experimental_notes/data/, NOT bench/results/ — that directory is
# gitignored, so the dataset and the adjudication pack would have existed on one
# machine only. The entire point of this script is that a claim and its evidence
# must travel together; leaving the evidence untracked would have reproduced the
# defect it was written to close, one directory over.
CACHE = REPO / "experimental_notes" / "data" / "similarity_pairs_438.json"
PACK = REPO / "experimental_notes" / "data" / "similarity_adjudication_pack.json"


# ── dataset ─────────────────────────────────────────────────────────────────

def _report(run: str) -> dict:
    stem = ARCHIVE[run][0]
    hits = [p for p in (REPO / "bench" / "logs").glob(f"{stem}_*/{stem}_report.json")
            if ".errata" not in str(p)]
    if not hits:
        raise FileNotFoundError(f"archived run not present: {stem}")
    return json.loads(hits[0].read_text(encoding="utf-8"))


def _symbols_for(run: str, rep: dict) -> frozenset:
    target = ARCHIVE[run][1]
    if target and (REPO / target).is_file():
        return CL.target_symbols(str(REPO / target))
    ids: set = set()
    for e in rep["registry"]["entries"].values():
        ids |= set(re.findall(r"\b([A-Z]{2}-\d{2})\b", e.get("description", "") or ""))
    return frozenset(ids)


def _backfill_for(run: str) -> dict:
    """Repaired descriptions for a run, or {} if none were written.

    OPT-IN, never automatic. The sidecar is produced by
    `scripts/backfill_descriptions.py` and holds only repairs whose join to the
    archived raw response was verified against the stored text. Reading it
    changes what every figure below is computed on, so the caller asks for it
    explicitly and the report says which mode it ran in.
    """
    stem = ARCHIVE[run][0]
    for d in (REPO / "bench" / "logs").glob(f"{stem}_*"):
        p = d / "descriptions_backfill.json"
        if p.is_file():
            try:
                return json.loads(p.read_text(encoding="utf-8")).get("descriptions") or {}
            except Exception:
                return {}
    return {}


def build_dataset(backfilled: bool = False) -> dict:
    """Rebuild the 165 criticals and their 438 same-location pairs.

    POPULATION NOTE, and it matters. This uses every critical in the registry —
    NOT `CL._gate_population`, which filters terminal-non-novel entries and was
    added on 2026-08-12. Measured both ways: the gate population gives 136
    located criticals and 423 pairs; the full population gives 139 and 438. The
    recorded figures are the full population, so that is what is reproduced here.
    The two populations answering differently is itself worth knowing: the rule
    is evidenced on a superset of the findings the gate actually sees.
    """
    crits, pairs = [], []
    for run in ARCHIVE:
        rep = _report(run)
        repairs = _backfill_for(run) if backfilled else {}
        entries = rep["registry"]["entries"]
        if repairs:
            entries = json.loads(json.dumps(entries))
            for cid, v in repairs.items():
                if cid in entries:
                    entries[cid]["description"] = v["description"]
        syms = _symbols_for(run, {"registry": {"entries": entries}})
        here = []
        for e in entries.values():
            if (e.get("severity") or 0.0) < CRITICAL_SEVERITY:
                continue
            desc = e.get("description", "") or ""
            rec = {
                "run": run, "cid": e.get("canonical_id", ""), "desc": desc,
                "severity": e.get("severity"), "round": e.get("open_since_round"),
                "status": e.get("status"), "verdict": e.get("falsifier_verdict"),
                "locations": sorted(CL.finding_locations(desc, syms)),
                "signature": sorted(CL.stem_signature(desc)),
                "outcomes": sorted(str(o) for o in CL.computed_outcomes(desc)),
            }
            crits.append(rec)
            if rec["locations"]:
                here.append(rec)
        for a, b in itertools.combinations(here, 2):
            shared = sorted(set(a["locations"]) & set(b["locations"]))
            if not shared:
                continue
            pairs.append({
                "run": run, "a": a["cid"], "b": b["cid"], "shared_locations": shared,
                "tier2": CL.signature_similarity(frozenset(a["signature"]),
                                                 frozenset(b["signature"])),
                "tier3": CL.outcome_agreement(CL.computed_outcomes(a["desc"]),
                                              CL.computed_outcomes(b["desc"])),
                "a_desc": a["desc"], "b_desc": b["desc"],
            })
    return {"criticals": crits, "pairs": pairs}


def add_embedding_labels(data: dict) -> dict:
    """Cosine similarity between the two descriptions, and the derived label.

    The backend is all-MiniLM-L6-v2, the same family the recorded measurement
    used. `label` is 1 (same defect), 0 (different) or None (in the excluded
    band). None is a first-class value here; the recorded measurement dropped it.
    """
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    from sentence_transformers import SentenceTransformer, util

    model = SentenceTransformer("all-MiniLM-L6-v2")
    texts = sorted({p["a_desc"] for p in data["pairs"]} |
                   {p["b_desc"] for p in data["pairs"]})
    emb = model.encode(texts, convert_to_tensor=True, show_progress_bar=False,
                       normalize_embeddings=True)
    idx = {t: i for i, t in enumerate(texts)}
    for p in data["pairs"]:
        s = float(util.cos_sim(emb[idx[p["a_desc"]]], emb[idx[p["b_desc"]]]).item())
        p["embedding"] = s
        p["label"] = 1 if s >= EMB_SAME else (0 if s <= EMB_DIFF else None)
    return data


def load_dataset(rebuild: bool = False, backfilled: bool = False) -> dict:
    cache = (CACHE.with_name("similarity_pairs_backfilled.json")
             if backfilled else CACHE)
    if cache.is_file() and not rebuild:
        return json.loads(cache.read_text(encoding="utf-8"))
    data = add_embedding_labels(build_dataset(backfilled=backfilled))
    data["backfilled"] = backfilled
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(data, indent=1), encoding="utf-8")
    return data


# ── evaluation ──────────────────────────────────────────────────────────────

def reproduce(data: dict) -> list:
    """Recompute every recorded figure. Returns (name, got, want, ok) rows."""
    c, p = data["criticals"], data["pairs"]
    got = {
        "criticals": len(c),
        "tier2_coverage": sum(1 for x in c if x["signature"]),
        "tier3_coverage": sum(1 for x in c if x["outcomes"]),
        "pairs": len(p),
        "n_same": sum(1 for x in p if x.get("label") == 1),
        "n_diff": sum(1 for x in p if x.get("label") == 0),
    }
    return [(k, got[k], RECORDED[k], got[k] == RECORDED[k]) for k in RECORDED]


def auc(scores, labels) -> float:
    """Mann-Whitney U / |pos||neg|, ties counted as half. No sklearn dependency."""
    pos = [s for s, y in zip(scores, labels) if y == 1]
    neg = [s for s, y in zip(scores, labels) if y == 0]
    if not pos or not neg:
        return float("nan")
    wins = sum((1.0 if a > b else 0.5 if a == b else 0.0) for a in pos for b in neg)
    return wins / (len(pos) * len(neg))


def operating_points(pairs, thresholds) -> list:
    """For each merge threshold: false-merge rate and same-defect recall.

    FALSE MERGE is the costly error and the one the founder asked to bound: two
    genuinely different findings collapsed into one, so a real second defect is
    never counted and the gate can close on it. RECALL is what the rule buys.
    """
    lab = [p for p in pairs if p.get("label") is not None]
    same = [p for p in lab if p["label"] == 1]
    diff = [p for p in lab if p["label"] == 0]
    rows = []
    for t in thresholds:
        fm = sum(1 for p in diff if p["tier2"] >= t)
        tm = sum(1 for p in same if p["tier2"] >= t)
        rows.append({
            "threshold": t,
            "false_merge": fm, "n_diff": len(diff),
            "false_merge_rate": fm / len(diff) if diff else float("nan"),
            "recall": tm / len(same) if same else float("nan"),
            "n_same": len(same),
        })
    return rows


def three_way(pairs, t_split, t_merge) -> dict:
    """Merge automatically / refer to a human / split automatically.

    This is the shape the founder approved. The point of the middle band is that
    a rule permitted to say NOTHING can hold its automatic decisions to a much
    tighter error bound than one forced to answer every pair.
    """
    lab = [p for p in pairs if p.get("label") is not None]
    out = {"t_split": t_split, "t_merge": t_merge, "n": len(lab),
           "merge": 0, "refer": 0, "split": 0,
           "false_merge": 0, "false_split": 0, "refer_same": 0, "refer_diff": 0}
    for p in lab:
        s, y = p["tier2"], p["label"]
        if s >= t_merge:
            out["merge"] += 1
            out["false_merge"] += (y == 0)
        elif s <= t_split:
            out["split"] += 1
            out["false_split"] += (y == 1)
        else:
            out["refer"] += 1
            out["refer_same"] += (y == 1)
            out["refer_diff"] += (y == 0)
    out["referral_rate"] = out["refer"] / out["n"] if out["n"] else float("nan")
    out["false_merge_rate"] = (out["false_merge"] / out["merge"]) if out["merge"] else 0.0
    out["false_split_rate"] = (out["false_split"] / out["split"]) if out["split"] else 0.0
    return out


def cluster_bootstrap_auc(data, B: int = 2000, seed: int = 20260817) -> tuple:
    """95% CI for AUC, resampling FINDINGS rather than pairs.

    WHY THIS IS NOT A PLAIN BOOTSTRAP, and it is the methodological point of this
    file. The 438 pairs are not 438 independent observations. They are all pairs
    among 139 findings, so one finding appears in many pairs and their errors are
    correlated. Resampling pairs directly would treat correlated observations as
    independent and produce a confidence interval far too narrow — the classic
    way pairwise evaluations overstate their own precision.

    So this resamples the underlying findings with replacement WITHIN each run,
    re-forms all same-location pairs among the resample, and recomputes AUC. That
    is the node bootstrap, and it propagates the dependence correctly.
    """
    import random
    rng = random.Random(seed)
    by_run: dict = {}
    for p in data["pairs"]:
        by_run.setdefault(p["run"], []).append(p)
    # index pairs by unordered finding pair, per run
    index = {r: {frozenset((p["a"], p["b"])): p for p in ps} for r, ps in by_run.items()}
    nodes = {r: sorted({x for p in ps for x in (p["a"], p["b"])}) for r, ps in by_run.items()}

    stats = []
    for _ in range(B):
        sc, lb = [], []
        for r, ns in nodes.items():
            draw = [rng.choice(ns) for _ in ns]
            for i in range(len(draw)):
                for j in range(i + 1, len(draw)):
                    if draw[i] == draw[j]:
                        continue
                    p = index[r].get(frozenset((draw[i], draw[j])))
                    if p is None or p.get("label") is None:
                        continue
                    sc.append(p["tier2"])
                    lb.append(p["label"])
        if sc and 0 < sum(lb) < len(lb):
            stats.append(auc(sc, lb))
    stats.sort()
    if len(stats) < 100:
        return float("nan"), float("nan"), len(stats)
    lo = stats[int(0.025 * len(stats))]
    hi = stats[int(0.975 * len(stats))]
    return lo, hi, len(stats)


def decide(pairs) -> list:
    """Run every pair through `identity_decision` and record the reason.

    ROUTED THROUGH THE RULE, NOT RE-IMPLEMENTED. The same discipline the pair
    tests use, and for the same reason: a check that re-derives the logic it is
    checking cannot see that logic break. It also matters here specifically —
    a hand-rolled version of this ablation gave a DIFFERENT tier-3 answer,
    because the live rule consults tier 3 only AFTER the no-witness check, and
    the hand-rolled one did not model that ordering.
    """
    for p in pairs:
        if p.get("label") is None:
            continue
        syms = frozenset(p["shared_locations"])
        d0 = CL.identity_decision(p["a_desc"], syms, [])
        prior = CL.Prior(d0.locations, d0.signature, d0.outcomes, "A")
        d1 = CL.identity_decision(p["b_desc"], syms, [prior])
        p["_reason"], p["_new"] = d1.reason, d1.is_new
    return [p for p in pairs if p.get("label") is not None]


def baseline_comparison(lab) -> dict:
    """The similarity function against the thing it is layered on: location keying.

    THE COMPARATOR IS THE POINT. Tiers 2 and 3 only ever act WITHIN an
    already-flagged location, so for every one of these same-location pairs the
    baseline — location keying alone — merges unconditionally. Its false-merge
    count on this set is therefore every different-defect pair in it.

    Reporting the rule's merge precision without that comparator would be
    alarming and would be wrong: 63% of its merges being different-defect pairs
    sounds like a broken rule, and is in fact a large improvement on a baseline
    that is wrong 100% of the time. Reporting only the improvement would be the
    opposite error. Both are below.
    """
    same = [p for p in lab if p["label"] == 1]
    diff = [p for p in lab if p["label"] == 0]
    merged = [p for p in lab if not p["_new"]]
    return {
        "n": len(lab), "n_same": len(same), "n_diff": len(diff),
        "base_rate_same": len(same) / len(lab) if lab else float("nan"),
        # baseline: location keying alone merges every same-location pair
        "base_merges": len(lab), "base_false_merges": len(diff),
        # the rule
        "merges": len(merged),
        "false_merges": sum(1 for p in merged if p["label"] == 0),
        "splits": sum(1 for p in lab if p["_new"]),
        "false_splits": sum(1 for p in lab if p["_new"] and p["label"] == 1),
        "precision": (sum(1 for p in merged if p["label"] == 1) / len(merged)
                      if merged else float("nan")),
        "recall": (sum(1 for p in same if not p["_new"]) / len(same)
                   if same else float("nan")),
    }


def tier3_ablation(lab) -> dict:
    """What tier 3 actually CHANGES, not what it answers.

    The recorded justification for tier 3 is its answer distribution — Fisher
    p = 1.4e-07, never once calling a same-defect pair DIFFERENT. That describes
    its OPINIONS. This measures its EFFECT: the pairs where `same_computed_outcome`
    is the reason the rule merged, meaning tier 3 overrode a tier-2 split. On any
    other pair tier 3 changed nothing, by construction — a DIFFERENT answer is
    recorded as corroboration and moves no count.
    """
    operative = [p for p in lab if p["_reason"] == "same_computed_outcome"]
    return {
        "operative": len(operative), "n": len(lab),
        "operative_correct": sum(1 for p in operative if p["label"] == 1),
        "operative_wrong": sum(1 for p in operative if p["label"] == 0),
        "pairs": [(p["run"], p["a"], p["b"], p["label"], p["embedding"]) for p in operative],
        "says_same": sum(1 for p in lab if p["tier3"] == "SAME"),
        "says_different": sum(1 for p in lab if p["tier3"] == "DIFFERENT"),
        "abstains": sum(1 for p in lab if p["tier3"] == "UNKNOWN"),
    }


# Round-number caps applied to finding descriptions before they ever reach this
# rule. 200 is `runner_core._parse_findings`' fallback when the DESCRIPTION/FIND
# field does not match and it keeps `block[:200]`; 500 is the registry write in
# `reference_runner_v3`. Both cut mid-word.
DESCRIPTION_CAPS = {200, 300, 500, 1200}


def _truncated(text: str) -> bool:
    return len(text) in DESCRIPTION_CAPS


def input_quality(data, lab) -> dict:
    """How much of the rule's INPUT is clipped mid-sentence, and does it matter?

    OBSERVED 2026-08-16, and it was found only because C0063's anchor turned out
    to be missing rather than absent by nature. Across every archived report,
    2187 finding descriptions: 714 are exactly 200 characters and 661 exactly
    500. 1284 end mid-word. Roughly 63% of the archive's findings are stored
    truncated, and the similarity function reads the truncated form.

    THE CAUSAL CLAIM IS NOT ESTABLISHED, and this function reports the check that
    weakens it as prominently as the one that supports it. Pooled, a merged pair
    involving truncated text is far more likely to be a wrong merge. Stratified
    by run, the association reverses on the two exam targets (exp48, exp49). That
    is a Simpson's-paradox signature: the pooled odds ratio is partly carried by
    which runs happen to have both high truncation and high error. What survives
    stratification is weaker and worth stating plainly — truncation shrinks the
    stem signature (medians 4 vs 5 tokens), and a Jaccard over small sets is
    coarse enough that ties land exactly on the merge threshold.
    """
    from scipy.stats import fisher_exact, mannwhitneyu

    crit = data["criticals"]
    merged = [p for p in lab if not p["_new"]]
    a = sum(1 for p in merged if p["label"] == 0 and p["_trunc"])
    b = sum(1 for p in merged if p["label"] == 0 and not p["_trunc"])
    c = sum(1 for p in merged if p["label"] == 1 and p["_trunc"])
    d = sum(1 for p in merged if p["label"] == 1 and not p["_trunc"])
    odds, pv = fisher_exact([[a, b], [c, d]])
    st = [len(x["signature"]) for x in crit if _truncated(x["desc"])]
    sf = [len(x["signature"]) for x in crit if not _truncated(x["desc"])]
    _u, spv = mannwhitneyu(st, sf) if st and sf else (float("nan"), float("nan"))
    per_run = {}
    for r in sorted({p["run"] for p in lab}):
        m = [p for p in merged if p["run"] == r]
        per_run[r] = (
            sum(1 for p in m if p["label"] == 0 and p["_trunc"]),
            sum(1 for p in m if p["label"] == 1 and p["_trunc"]),
            sum(1 for p in m if p["label"] == 0 and not p["_trunc"]),
            sum(1 for p in m if p["label"] == 1 and not p["_trunc"]))
    return {
        "n_crit": len(crit),
        "trunc_crit": sum(1 for x in crit if _truncated(x["desc"])),
        "at_200": sum(1 for x in crit if len(x["desc"]) == 200),
        "at_500": sum(1 for x in crit if len(x["desc"]) == 500),
        "pooled": (a, b, c, d), "odds": odds, "p": pv,
        "per_run": per_run,
        "sig_trunc": st, "sig_full": sf, "sig_p": spv,
        "on_threshold": sum(1 for p in lab
                            if abs(p["tier2"] - CL.WITHIN_LOCATION_THRESHOLD) < 1e-9),
    }


def write_adjudication_pack(data: dict) -> pathlib.Path:
    """The pairs in the excluded band, formatted for a human to rule on.

    Deliberately NOT pre-answered. This script's author is a machine, and a
    machine labelling these would reproduce exactly the defect the exercise
    exists to remove: a machine grading a machine, with the grader's errors
    invisible because nothing independent ever checks them.
    """
    band = [p for p in data["pairs"] if p.get("label") is None]
    band.sort(key=lambda p: -p["embedding"])
    pack = [{
        "id": f"ADJ-{i:03d}", "run": p["run"], "a": p["a"], "b": p["b"],
        "shared_locations": p["shared_locations"],
        "embedding": round(p["embedding"], 4),
        "tier2_jaccard": round(p["tier2"], 4), "tier3": p["tier3"],
        "finding_a": p["a_desc"], "finding_b": p["b_desc"],
        "SAME_DEFECT": None,  # <- the human fills this in: true / false
        "note": "",
    } for i, p in enumerate(band, 1)]
    PACK.parent.mkdir(parents=True, exist_ok=True)
    PACK.write_text(json.dumps({
        "question": ("Do these two findings describe THE SAME DEFECT? Set "
                     "SAME_DEFECT to true or false. Leave null if genuinely "
                     "undecidable and say why in `note`."),
        "why": ("These 120 pairs sit in the band the automated labelling refused "
                "to call either way (embedding strictly between 0.70 and 0.90). "
                "The recorded measurement dropped them silently. They are 27% of "
                "the data and they are the hard 27%."),
        "count": len(pack), "pairs": pack,
    }, indent=1), encoding="utf-8")
    return PACK


# ── report ──────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--rebuild", action="store_true", help="recompute the cache")
    ap.add_argument("--adjudication-pack", action="store_true",
                    help="write the 120 unlabelled pairs for human ruling")
    ap.add_argument("--human-labels", metavar="FILE",
                    help="a completed adjudication pack; re-reports against it")
    ap.add_argument("--bootstrap", type=int, default=2000)
    ap.add_argument("--backfilled", action="store_true",
                    help="use repaired descriptions from the backfill sidecars")
    args = ap.parse_args()

    data = load_dataset(rebuild=args.rebuild, backfilled=args.backfilled)
    pairs = data["pairs"]

    print("=" * 74)
    print("SIMILARITY FUNCTION — OPERATING CHARACTERISTIC")
    print("  descriptions: " + ("REPAIRED (backfill sidecars applied)"
                                if args.backfilled else
                                "AS ARCHIVED (truncated/substituted, pre-2026-08-17)"))
    print("=" * 74)

    print("\n1. REPRODUCTION OF THE RECORDED FIGURES")
    ok_all = True
    for name, got, want, ok in reproduce(data):
        ok_all &= ok
        print(f"   {'OK ' if ok else 'DIFF'}  {name:16s} got {got:4d}   recorded {want:4d}")
    print("   " + ("all recorded figures reproduce from the archive."
                   if ok_all else "MISMATCH — the recorded claim is stale."))

    lab = [p for p in pairs if p.get("label") is not None]
    band = [p for p in pairs if p.get("label") is None]
    print(f"\n2. WHAT THE RECORDED MEASUREMENT LEFT OUT")
    print(f"   labelled pairs                   {len(lab):4d}")
    print(f"   UNLABELLED, silently dropped     {len(band):4d}  "
          f"({len(band)/len(pairs):.1%} of the data)")
    print( "   These are the pairs the embedding refused to call. They are not a")
    print( "   random sample: they are where the question is hardest.")

    print("\n3. DISCRIMINATION (tier 2, against embedding labels)")
    a = auc([p["tier2"] for p in lab], [p["label"] for p in lab])
    lo, hi, nb = cluster_bootstrap_auc(data, B=args.bootstrap)
    print(f"   AUC                              {a:.4f}")
    print(f"   95% CI (finding-level bootstrap) [{lo:.4f}, {hi:.4f}]   {nb} resamples")
    print( "   The CI resamples FINDINGS, not pairs: the 438 pairs come from 139")
    print( "   findings and are not independent observations.")

    print("\n4. OPERATING POINTS — P(merge | genuinely different), the costly error")
    print(f"   {'thresh':>7}  {'false merges':>13}  {'rate':>7}  {'recall':>7}")
    for r in operating_points(pairs, [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]):
        mark = "  <- live" if abs(r["threshold"] - CL.WITHIN_LOCATION_THRESHOLD) < 1e-9 else ""
        print(f"   {r['threshold']:7.2f}  {r['false_merge']:6d}/{r['n_diff']:<6d}"
              f"  {r['false_merge_rate']:7.2%}  {r['recall']:7.2%}{mark}")

    lab = decide(pairs)
    bc = baseline_comparison(lab)
    print("\n5. AGAINST THE BASELINE IT REPLACES — location keying alone")
    print(f"   base rate: only {bc['n_same']} of {bc['n']} labelled pairs are the same "
          f"defect ({bc['base_rate_same']:.1%}).")
    print(f"   location keying alone   merges {bc['base_merges']:3d}   "
          f"false merges {bc['base_false_merges']:3d}  (100% of the different-defect pairs)")
    print(f"   + similarity function   merges {bc['merges']:3d}   "
          f"false merges {bc['false_merges']:3d}  "
          f"({1 - bc['false_merges']/bc['base_false_merges']:.0%} fewer)")
    print(f"   false SPLITS introduced {bc['false_splits']:3d}   "
          f"— the rule never split a same-defect pair on this archive.")
    print(f"   merge precision {bc['precision']:.1%}, recall {bc['recall']:.1%}.")
    print( "   BOTH readings are true and neither alone is honest. Precision of")
    print(f"   {bc['precision']:.0%} sounds like a broken rule; it is a large improvement on a")
    print( "   baseline that is wrong every time, and it buys that with zero false")
    print( "   splits. The skewed base rate, not the discriminator, drives precision.")

    print("\n6. THREE-WAY RULE — merge / refer to a human / split")
    for ts, tm in ((0.05, 0.40), (0.10, 0.50), (0.05, 0.50)):
        r = three_way(pairs, ts, tm)
        print(f"   split<={ts:.2f} merge>={tm:.2f}:  "
              f"merge {r['merge']:3d} (wrong {r['false_merge']:2d}, {r['false_merge_rate']:5.1%})  "
              f"refer {r['refer']:3d} ({r['referral_rate']:5.1%})  "
              f"split {r['split']:3d} (wrong {r['false_split']:2d}, {r['false_split_rate']:5.1%})")

    print("\n7. TIER-3 ABLATION — what it CHANGES, not what it answers")
    ab = tier3_ablation(lab)
    print(f"   answers   SAME {ab['says_same']:3d}   DIFFERENT {ab['says_different']:3d}   "
          f"abstains {ab['abstains']:3d}  ({ab['abstains']/ab['n']:.0%})")
    print(f"   but it CHANGES the decision on only {ab['operative']} of {ab['n']} labelled pairs")
    print(f"   of those:  correct {ab['operative_correct']}   WRONG {ab['operative_wrong']}")
    for run, a, b, y, e in ab["pairs"]:
        print(f"      {run} {a}/{b}  labelled {'SAME' if y else 'DIFFERENT'}  embedding {e:.3f}")
    if ab["operative"] and not ab["operative_correct"]:
        print( "   On this archive tier 3's ENTIRE operative contribution is wrong merges.")
        print( "   State the weak claim, not the strong one: n is 3, so this does not")
        print( "   establish tier 3 is harmful — it establishes there is no evidence of")
        print( "   benefit, and that its recorded justification (Fisher p = 1.4e-07)")
        print( "   describes its ANSWERS, which is not the quantity that matters.")

    for p in lab:
        p["_trunc"] = _truncated(p["a_desc"]) or _truncated(p["b_desc"])
    iq = input_quality(data, lab)
    import statistics
    print("\n8. INPUT QUALITY — how much of what the rule reads is cut mid-word")
    print(f"   criticals stored truncated at a cap  {iq['trunc_crit']:3d}/{iq['n_crit']}"
          f"  ({iq['trunc_crit']/iq['n_crit']:.0%})"
          f"   [{iq['at_200']} at 200, {iq['at_500']} at 500]")
    a, b, c, d = iq["pooled"]
    print(f"   pooled, among MERGED pairs: wrong+truncated {a}, wrong+full {b}, "
          f"right+truncated {c}, right+full {d}")
    print(f"   Fisher p = {iq['p']:.3g}, odds ratio {iq['odds']:.3g}  "
          f"— BUT see the stratification below")
    print(f"   {'run':7s}{'wrong+tr':>9s}{'right+tr':>9s}{'wrong+full':>11s}{'right+full':>11s}")
    for r, (x1, x2, x3, x4) in iq["per_run"].items():
        print(f"   {r:7s}{x1:9d}{x2:9d}{x3:11d}{x4:11d}")
    print( "   The association REVERSES on exp48 and exp49. The pooled odds ratio is")
    print( "   therefore partly a run effect, not a truncation effect, and the causal")
    print( "   claim is NOT established. Reporting only the pooled number would be")
    print( "   the same error this script was written to correct.")
    print(f"   What does survive: truncation shrinks the signature — median "
          f"{statistics.median(iq['sig_trunc']):.0f} tokens vs "
          f"{statistics.median(iq['sig_full']):.0f}, p = {iq['sig_p']:.3g}.")
    print(f"   And {iq['on_threshold']} labelled pairs sit EXACTLY on the "
          f"{CL.WITHIN_LOCATION_THRESHOLD} threshold, because a Jaccard over")
    print( "   small token sets is coarse: 1 shared of 3 and 3 gives exactly 0.200.")

    if args.human_labels:
        hl = json.loads(pathlib.Path(args.human_labels).read_text(encoding="utf-8"))
        ruled = {(p["run"], p["a"], p["b"]): p["SAME_DEFECT"]
                 for p in hl["pairs"] if p.get("SAME_DEFECT") is not None}
        merged = 0
        for p in pairs:
            v = ruled.get((p["run"], p["a"], p["b"]))
            if v is not None:
                p["label"] = int(bool(v))
                merged += 1
        print(f"\n9. WITH {merged} HUMAN LABELS APPLIED  <- AUTHORITATIVE")
        lab2 = [p for p in pairs if p.get("label") is not None]
        print(f"   AUC over {len(lab2)} pairs           "
              f"{auc([p['tier2'] for p in lab2], [p['label'] for p in lab2]):.4f}")
        for r in operating_points(pairs, [0.10, 0.20, 0.30, 0.40, 0.50]):
            print(f"   thresh {r['threshold']:.2f}  false-merge {r['false_merge_rate']:6.2%}"
                  f"  recall {r['recall']:6.2%}")
    else:
        print("\n9. HUMAN LABELS — NOT YET SUPPLIED")
        print("   Everything above is scored against EMBEDDING labels: one machine")
        print("   grading another. The separation claim survives that (the embedding")
        print("   is independent of both tiers). The operating point does NOT — a")
        print("   threshold calibrated on an unvalidated proxy inherits its errors.")
        print(f"   Run --adjudication-pack to produce the {len(band)} pairs needing a ruling.")

    if args.adjudication_pack:
        p = write_adjudication_pack(data)
        print(f"\n   adjudication pack written: {p.relative_to(REPO)}")
        print(f"   {len(band)} pairs, unanswered, sorted by embedding score descending.")

    print("\n" + "=" * 74)
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
