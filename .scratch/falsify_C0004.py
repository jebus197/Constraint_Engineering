#!/usr/bin/env python3
"""Falsifier for review finding C0004 against Listing E (`topo_order`)."""

import copy, re, sys
from collections import deque

TARGET = "/Users/georgejackson/CDSFL_review_targets/current/SW-21-REF-04.md"


def load_listing_e(path):
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    blocks = re.findall(r"```python\n(.*?)```", text, re.DOTALL)
    hits = [b for b in blocks if re.search(r"^def topo_order\(", b, re.M)]
    if len(hits) != 1:
        sys.exit(f"PRECONDITION FAILED: found {len(hits)} topo_order listings, expected 1")
    src = hits[0]
    ns = {"deque": deque}
    exec(compile(src, path + "::ListingE", "exec"), ns)
    return ns["topo_order"], src


def main():
    topo_order, src = load_listing_e(TARGET)
    for probe in ("indeg[b] += 1", "queue.popleft()", "return order"):
        if probe not in src:
            sys.exit(f"PRECONDITION FAILED: reviewed line absent from disk: {probe!r}")

    nodes = [f"S{i}" for i in range(1, 15)]
    edges = [
        ("S1","S2"),("S1","S3"),("S2","S4"),("S3","S4"),("S3","S5"),
        ("S4","S6"),("S5","S6"),("S5","S7"),("S6","S8"),("S7","S8"),
        ("S8","S9"),("S8","S10"),("S9","S11"),("S10","S11"),
        ("S11","S12"),("S12","S13"),("S12","S14"),("S13","S14"),
    ]
    assert len(edges) == 18, "edge list transcription error"

    try:
        clean = topo_order(list(nodes), list(edges))
    except Exception as exc:
        sys.exit(f"INCONCLUSIVE: acyclic control raised {type(exc).__name__}: {exc}")
    if len(clean) != len(nodes):
        sys.exit(f"INCONCLUSIVE: acyclic control already truncated ({len(clean)}/14)")
    print(f"control (acyclic): {len(clean)}/14 stages ordered, no exception")

    cyc_nodes = list(nodes)
    cyc_edges = edges + [("S14", "S3")]

    nodes_before = copy.deepcopy(cyc_nodes)
    edges_before = copy.deepcopy(cyc_edges)

    try:
        order = topo_order(cyc_nodes, cyc_edges)
    except Exception as exc:
        print(f"CLEAN: cyclic input raised {type(exc).__name__}: {exc}")
        print("Defect absent - topo_order fails closed on a cycle.")
        return 0

    if not (isinstance(order, list) and set(order) <= set(cyc_nodes)):
        sys.exit("INCONCLUSIVE: return shape changed (not a list of stage names); "
                 f"got {type(order).__name__}={order!r} - re-review the new contract.")

    inputs_untouched = (cyc_nodes == nodes_before and cyc_edges == edges_before)
    print(f"cyclic probe: returned {type(order).__name__} of length {len(order)} "
          f"for {len(cyc_nodes)} stages -> {order}")
    print(f"caller inputs unmutated after call: {inputs_untouched}")

    if len(order) >= len(cyc_nodes):
        print("Defect absent - no truncation observed on cyclic input.")
        return 0

    dropped = [n for n in cyc_nodes if n not in order]
    deployed = [s for s in order]
    print(f"simulated rollout deployed {len(deployed)} stages, skipped {len(dropped)}: {dropped}")

    raise AssertionError(
        "FALSIFIED (C0004 CONFIRMED): topo_order returned a truncated rollout order of "
        f"{len(order)} for a {len(cyc_nodes)}-stage cyclic plan, raising nothing and leaving "
        f"the caller's inputs untouched{' (verified)' if inputs_untouched else ''}. The short "
        f"list is the only channel, so a caller that does not length-check silently skips "
        f"{len(dropped)} stages ({', '.join(dropped)}) and reports success. Fails open, not closed."
    )


if __name__ == "__main__":
    sys.exit(main())
