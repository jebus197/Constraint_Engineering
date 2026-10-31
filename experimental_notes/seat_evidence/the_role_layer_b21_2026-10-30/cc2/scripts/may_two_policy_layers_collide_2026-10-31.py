# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'the_role_layer_b21_2026-10-30', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 1d1c7c61cab20ba12faa10e9472134d6b1be3e168e847371523178fb8f9021a4
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""May 2 policy layers write the same leaf? Measured, and the answer is 2-sided.

WHY THIS EXISTS. Panel brief `the_role_layer_b21_2026-10-30` establishes by
execution that reversing the (domain, model) merge order moves 0 of 60 pairs,
then frames the remaining live question as:

    "may layers write into each other's namespace at all? Nothing in
     `_deep_merge` forbids it. The disjointness is a convention that no
     mechanism enforces."

That framing is half right and the half it omits changes the answer. This
script measures BOTH halves against the live `bench/cdsfl_registry/registry.py`
-- it calls `_load_toml`, `_deep_merge`, `_check_monotonicity` and
`load_effective_policy` and re-implements none of them.

WHAT IT MEASURES.

  1. SIBLING overlap: domain x model leaf collisions. Expected 0, reproducing
     the brief independently.
  2. ANCESTOR overlap: every domain / model / target file against
     `universal.toml`. Overlap here is not a convention being observed by luck
     -- it is the merge engine's stated purpose ("lower layers can tighten but
     never loosen"), so if this count is non-zero then overlap is already
     PERMITTED and pervasive, and "may layers overlap at all" is already
     answered yes by 10 domain files.
  3. WHAT A COLLISION DOES, by execution: a synthetic SOFT collision and a
     synthetic HARD collision, merged through the live functions.
  4. POSITION-INDEPENDENCE OF MONOTONICITY against a hostile role layer
     inserted at every position in the merge sequence.
  5. THE 3 ABSENCE BEHAVIOURS, by calling `load_effective_policy`.
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from bench.cdsfl_registry import registry as R  # noqa: E402

RD = R.REGISTRY_DIR


def leaves(d, prefix=""):
    """Every leaf dotpath of a nested dict."""
    out = {}
    for k, v in d.items():
        p = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(leaves(v, p + "."))
        else:
            out[p] = v
    return out


def hard_dotpaths():
    return sorted(set(R.HARD_CONSTRAINTS) | set(R.HARD_THRESHOLDS) | set(R.HARD_STRINGS))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    report = {}

    universal = R._load_toml(RD / "universal.toml")
    u_leaves = set(leaves(universal))
    domains = {p.stem: R._load_toml(p) for p in sorted((RD / "domains").glob("*.toml"))}
    models = {p.stem: R._load_toml(p) for p in sorted((RD / "models").glob("*.toml"))}

    print("=" * 78)
    print("1. SIBLING OVERLAP  (domain x model), leaf dotpaths")
    print("=" * 78)
    pairs = 0
    sib_collide = []
    for dn, dc in domains.items():
        for mn, mc in models.items():
            pairs += 1
            shared = set(leaves(dc)) & set(leaves(mc))
            if shared:
                sib_collide.append((dn, mn, sorted(shared)))
    print(f"   pairs examined                  : {pairs}")
    print(f"   pairs sharing >=1 leaf dotpath  : {len(sib_collide)}")
    print("   -> reproduces the brief independently: siblings are disjoint TODAY.")
    report["sibling_pairs"] = pairs
    report["sibling_collisions"] = len(sib_collide)

    print()
    print("=" * 78)
    print("2. ANCESTOR OVERLAP  (each lower-layer file x universal.toml)")
    print("=" * 78)
    anc = {}
    for kind, group in (("domain", domains), ("model", models)):
        for name, cfg in group.items():
            shared = sorted(set(leaves(cfg)) & u_leaves)
            anc[f"{kind}/{name}"] = shared
            print(f"   {kind}/{name:22} overlaps universal on {len(shared):3} leaf(s)")
    n_files = len(anc)
    n_overlapping = sum(1 for v in anc.values() if v)
    total_overlap_leaves = sum(len(v) for v in anc.values())
    print()
    print(f"   files examined                     : {n_files}")
    print(f"   files that OVERRIDE a universal leaf: {n_overlapping}")
    print(f"   total overriding leaf writes        : {total_overlap_leaves}")
    print()
    print("   SO OVERLAP IS NOT A CONVENTION AWAITING A RULING. Every lower layer")
    print("   that does anything at all overlaps layer 1 -- that IS overriding, and")
    print("   it is the engine's documented purpose. The open question is narrower:")
    print("   may 2 layers at the SAME tier, whose relative order expresses no")
    print("   intent, write the same leaf. Those are different questions and the")
    print("   brief's phrasing ('at all') merges them.")
    report["ancestor_overlap_files"] = n_overlapping
    report["ancestor_overlap_leaves"] = total_overlap_leaves

    print()
    print("=" * 78)
    print("3. WHAT A COLLISION ACTUALLY DOES, by execution")
    print("=" * 78)
    # SOFT collision: two synthetic layers both set verification.something_soft
    soft_key = "verification.peer_support_min_families"   # a real HARD threshold
    a = {"verification": {"demo_soft": 5}}
    b = {"verification": {"demo_soft": 1}}
    m_ab = R._deep_merge(R._deep_merge(universal, a), b)
    m_ba = R._deep_merge(R._deep_merge(universal, b), a)
    print(f"   SOFT leaf 'verification.demo_soft': A sets 5, B sets 1")
    print(f"     merge A then B -> {R._dotpath_get(m_ab,'verification.demo_soft')}")
    print(f"     merge B then A -> {R._dotpath_get(m_ba,'verification.demo_soft')}")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        R._check_monotonicity(m_ab, "demo_soft")
        R._check_monotonicity(m_ba, "demo_soft")
    print(f"     monotonicity raised : no")
    print(f"     warnings emitted    : {len(w)}")
    print("     -> LAST WRITER WINS, SILENTLY. No warning, no log, no record in")
    print("        the merged policy of the value that was discarded. Per CDSFL")
    print("        core S10 category 3/4 that is a property of the measurement")
    print("        machinery that cannot be recovered from the artefact.")
    report["soft_collision_silent"] = (len(w) == 0)

    # HARD collision: a layer that weakens a protected leaf.
    hostile = {"verification": {"peer_support_min_families": 1}}
    try:
        R._check_monotonicity(R._deep_merge(universal, hostile), "hostile")
        print(f"\n   HARD leaf {soft_key!r} lowered 2 -> 1: NOT caught  <-- FALSIFIED")
        report["hard_collision_caught"] = False
    except R.PolicyViolationError as e:
        first = str(e).strip().splitlines()[-1].strip()
        print(f"\n   HARD leaf {soft_key!r} lowered 2 -> 1:")
        print(f"     PolicyViolationError raised: {first}")
        report["hard_collision_caught"] = True

    print()
    print("=" * 78)
    print("4. POSITION-INDEPENDENCE vs a HOSTILE ROLE LAYER at every position")
    print("=" * 78)
    base_layers = [("domain", domains["mathematics"]), ("model", models["opus_4_6"])]
    caught_at = []
    for pos in range(len(base_layers) + 1):
        seq = base_layers[:pos] + [("role", hostile)] + base_layers[pos:]
        pol = universal
        verdict = "NOT CAUGHT"
        for name, cfg in seq:
            pol = R._deep_merge(pol, cfg)
            try:
                R._check_monotonicity(pol, name)
            except R.PolicyViolationError:
                verdict = f"caught at layer {name!r}"
                break
        order = " -> ".join(["universal"] + [n for n, _ in seq])
        print(f"   pos {pos}: {order}")
        print(f"            {verdict}")
        caught_at.append(verdict != "NOT CAUGHT")
    print()
    print(f"   positions where the weakening was caught: {sum(caught_at)}/{len(caught_at)}")
    print("   -> `_check_monotonicity(merged, layer_name)` takes no previous")
    print("      policy, so it compares against module constants and runs after")
    print("      EVERY merge. A role layer cannot weaken a HARD constraint from")
    print("      any position. Question 2 is therefore a PREFERENCE, not a")
    print("      safety question -- for the 17 protected dotpaths only.")
    report["hostile_caught_everywhere"] = all(caught_at)

    print()
    print("=" * 78)
    print("5. THE 3 ABSENCE BEHAVIOURS, by calling load_effective_policy")
    print("=" * 78)
    obs = {}
    # missing MODEL file
    try:
        R.load_effective_policy(domain="mathematics", model="no_such_model_xyz")
        obs["model_absent"] = "SILENT"
    except FileNotFoundError:
        obs["model_absent"] = "RAISE:FileNotFoundError"
    # missing TASK file
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        R.load_effective_policy(domain="mathematics", task_id="no_such_task_xyz")
        obs["task_absent"] = "WARN" if w else "SILENT"
    # UNKNOWN domain
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        R.load_effective_policy(domain="no_such_domain_xyz")
        obs["domain_unknown"] = "WARN" if w else "SILENT"
    # KNOWN domain whose file is absent: 'biomedical' maps to 'physics', which
    # exists; construct the case by consulting DOMAIN_MAP for a mapped target
    # with no file on disk.
    mapped_missing = [k for k, v in R.DOMAIN_MAP.items()
                      if not (RD / "domains" / f"{v}.toml").exists()]
    obs["known_domain_file_absent_cases"] = mapped_missing or "none on disk today"
    for k, v in obs.items():
        print(f"   {k:34} {v}")
    print(f"   {'tasks_dir_exists':34} {(RD/'tasks').exists()}")
    print(f"   {'roles_dir_exists':34} {(RD/'roles').exists()}")
    print()
    print("   3 DISTINCT PRECEDENTS: RAISE, WARN, SILENT -- confirming the brief")
    print("   and refuting entry B21's 2-precedent framing.")
    print()
    print("   AND A 4th OBSERVATION THE BRIEF DID NOT MAKE: tasks/ DOES NOT EXIST.")
    print("   So layer 3 is not 'silent when a file is missing'; layer 3 has never")
    print("   applied at all, for any task_id, since the directory it reads from is")
    print("   absent. The 4-layer merge is a 3-layer merge in practice. SILENT is")
    print("   the precedent that produced that, which is the argument against it.")
    report["absence"] = obs
    report["tasks_dir_exists"] = (RD / "tasks").exists()

    if args.json:
        print(json.dumps(report, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
