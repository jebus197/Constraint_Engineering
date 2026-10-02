# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'rho_repair_review_2026-09-29', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 6d38ee66183251242b3a080359de740d4ebf561c063526a267ae7e0efdd22ebb
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER: option 3's discount rule can erase a defect from novelty entirely.

CLAIM UNDER TEST. `_corroborated_discounts` discounts PAIRWISE and never checks
that the canonical it discounts AGAINST is itself still counted. Where the
discount graph holds a cycle or a chain whose root is separately discounted,
every member is discounted and the defect contributes ZERO novelty -- the
`cdsfl_a_model_can_delete_a_finding_by_repeating_itself` failure the function's
own docstring says it refuses, arriving through MUTUAL rather than SELF
reference.

FAILS (AssertionError / prints FALSIFIED) IFF THE DEFECT IS PRESENT.
Exits cleanly once `_release_annihilated_components` conserves one survivor
per component.

It imports the REAL `bench.reference_runner_v3`; nothing is retyped. It reads
only that module and `bench/logs/**/runner_state.json`, writes nothing, and
touches no scoring key, answer file or planted-defect manifest.

Takes no arguments. Exit 0 = claim REFUTED (code is sound); exit 1 = CONFIRMED.
"""
from __future__ import annotations
import argparse, collections, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _mk(R, fid, model, rnd, sev):
    return R.Finding(finding_id=fid, model_id=model, round_idx=rnd,
                     flaw_class="logic", severity=sev, abstraction_index=0.5,
                     description="d", proposed_fix="f", target_file="t.py")


class _Reg:
    def __init__(self, entries): self.entries = entries


def _same_defect_groups(entries):
    """Transitive same-defect groups, read from the `occasions` overlap record.

    Built from the OCCASIONS and not from the returned discount dict, on
    purpose. A repair that releases a survivor removes an edge from the discount
    graph and can split it, so recomputing components from the post-repair dict
    measures a graph the pairwise rule never produced. The occasion graph is the
    population the count is a statement about, and it does not move when the
    repair acts.
    """
    parent = {}
    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for tgt_id, tgt in entries.items():
        if not isinstance(tgt, dict):
            continue
        for occ in tgt.get("occasions") or []:
            if not isinstance(occ, dict) or occ.get("via") != "codiscovery":
                continue
            dup_id = occ.get("from_canonical")
            if (not dup_id or dup_id == tgt_id or dup_id not in entries
                    or not isinstance(entries[dup_id], dict)):
                continue
            if (tgt.get("open_since_round") is None
                    or entries[dup_id].get("open_since_round") is None):
                continue
            ra, rb = find(dup_id), find(tgt_id)
            if ra != rb:
                parent[ra] = rb
    comps = collections.defaultdict(set)
    for x in list(parent):
        comps[find(x)].add(x)
    return list(comps.values())


def _reconstruct(entries, alias_map):
    """The codiscovery occasion the post-repair runner writes, replayed onto an
    archived registry recorded before the write existed. Mirrors
    `scripts/option3_replay_2026-09-29.py::reconstruct`."""
    for cid, e in entries.items():
        if not isinstance(e, dict):
            continue
        for cd in e.get("codiscovery") or []:
            model, fid = cd.get("model") or "", cd.get("finding_id") or ""
            e.setdefault("occasions", []).append({
                "model": model, "round": e.get("open_since_round", 0),
                "alias": fid,
                "from_canonical": alias_map.get(f"{model}:{fid}", cid),
                "via": "codiscovery", "similarity": cd.get("similarity", 0.0)})


def main() -> int:
    argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        epilog="Takes no arguments. Exit 0 REFUTED, 1 CONFIRMED.").parse_args()

    import bench.reference_runner_v3 as R
    TERM = R._NON_NOVEL_TERMINAL_STATUSES
    failures = []

    # ── 1. CONSTRUCTED: two models corroborating each other in one round ─────
    reg = R.FindingRegistry()
    a = reg.register(_mk(R, "FA", "A", 0, 0.9), "A")
    b = reg.register(_mk(R, "FB", "B", 0, 0.9), "B")
    reg.record_codiscovery(a, "B", "FB", 0.9, round_idx=0)   # occasion on A -> B
    reg.record_codiscovery(b, "A", "FA", 0.9, round_idx=0)   # occasion on B -> A
    settled, _ = R._settled_novelty_series(reg, 0)
    corr, _ = R._corroborated_novelty_series(reg, 0)
    print(f"[1] mutual codiscovery, 1 defect, 2 canonicals: "
          f"settled={settled} corroborated={corr}")
    if settled[0] > 0 and corr[0] == 0:
        failures.append("FALSIFIED[1]: a real defect raised by 2 models in the "
                        "same round contributes 0 novelty — both sightings "
                        "discounted against each other.")

    # ── 2. CONSTRUCTED: live entry discounted against a TERMINAL target ──────
    reg2 = R.FindingRegistry()
    a2 = reg2.register(_mk(R, "FA", "A", 0, 0.9), "A")
    b2 = reg2.register(_mk(R, "FB", "B", 1, 0.9), "B")
    reg2.record_codiscovery(a2, "B", "FB", 0.9, round_idx=1)
    reg2.resolve(a2, "REFUTED", 1)
    settled2, _ = R._settled_novelty_series(reg2, 1)
    corr2, _ = R._corroborated_novelty_series(reg2, 1)
    print(f"[2] live entry discounted against a REFUTED target: "
          f"settled={settled2} corroborated={corr2}")
    if settled2[1] > 0 and corr2[1] == 0:
        failures.append("FALSIFIED[2]: an OPEN finding is discounted against a "
                        "REFUTED canonical that is itself uncounted — the "
                        "defect disappears from the novelty series.")

    # ── 3. ARCHIVE: conservation over every recorded registry ────────────────
    n_comp = n_bad = 0
    bad = []
    for fp in sorted((ROOT / "bench" / "logs").glob("**/runner_state.json")):
        try:
            st = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
        except Exception:                                    # noqa: BLE001
            continue
        rg = st.get("registry") or {}
        ents = rg.get("entries")
        if not isinstance(ents, dict) or not ents:
            continue
        ents = json.loads(json.dumps(ents))
        _reconstruct(ents, rg.get("alias_map") or {})
        disc = R._corroborated_discounts(_Reg(ents))
        for members in _same_defect_groups(ents):
            n_comp += 1
            countable = [m for m in members
                         if isinstance(ents.get(m), dict)
                         and ents[m].get("open_since_round") is not None
                         and ents[m].get("status") not in TERM]
            if countable and all(m in disc for m in countable):
                n_bad += 1
                bad.append((fp.parent.name, len(members)))
    print(f"[3] archive: {n_comp} same-defect groups (from the occasion "
          f"record), {n_bad} with every countable member discounted")
    for name, sz in bad:
        print(f"      annihilated component, size {sz}, in {name}")
    if n_bad:
        failures.append(f"FALSIFIED[3]: {n_bad} of {n_comp} same-defect groups "
                        f"in the recorded archive lose every member.")

    if failures:
        for f in failures:
            print(f)
        raise AssertionError(f"{len(failures)} of 3 checks demonstrate the defect")
    print("REFUTED: every same-defect group retains exactly one counted "
          "survivor; no defect is erased from the novelty series.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
