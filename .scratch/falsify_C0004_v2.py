#!/usr/bin/env python3
"""Falsifier for review finding C0004 -- Listing E (`topo_order`) of SW-21-REF-04.

Claim under test: on cyclic input the planner returns a TRUNCATED rollout order,
raising nothing, so the caller silently deploys a partial plan (fails open).

FALSIFIED is printed / AssertionError raised iff, on a graph that genuinely holds
a cycle, topo_order returns normally with fewer entries than nodes and emits no
exception and no warning -- i.e. the short list is the only channel.
Any other outcome exits clean.
"""

import copy, hashlib, json, os, re, sys, warnings
from collections import deque

REPO = "/Users/georgejackson/Developer_Projects/Constraint_Engineering"
MANIFEST = os.path.join(REPO, "bench/cdsfl_registry/targets/MANIFEST.md")
DOC_ID = "SW-21-REF-04"
TARGET = os.environ.get("CDSFL_TARGET",
                        "/Users/georgejackson/CDSFL_review_targets/current/SW-21-REF-04.md")


def bail(msg):
    print(msg)
    sys.exit(0)


def provenance(path):
    """Tie the bytes on disk to the manifest hash for DOC_ID (real-source proof)."""
    blob = re.search(r"```json\n(.*?)```", open(MANIFEST).read(), re.DOTALL)
    if not blob:
        bail("INCONCLUSIVE: manifest JSON block not found")
    entries = {v["document_id"]: v for v in json.loads(blob.group(1)).values()}
    if DOC_ID not in entries:
        bail(f"INCONCLUSIVE: {DOC_ID} absent from manifest")
    raw = open(path, "rb").read()
    got = hashlib.sha256(raw).hexdigest()
    want = entries[DOC_ID]["sha256"]
    state = "matches manifest" if got == want else f"REVISED since manifest ({want[:12]}...)"
    print(f"provenance: {DOC_ID} sha256 {got[:12]}... {state}, {len(raw)} bytes")
    return raw.decode()


def load_listing_e(text, path):
    hits = [b for b in re.findall(r"```python\n(.*?)```", text, re.DOTALL)
            if re.search(r"^def topo_order\(", b, re.M)]
    if len(hits) != 1:
        bail(f"INCONCLUSIVE: found {len(hits)} topo_order listings, expected 1")
    src = hits[0]
    for probe in ("indeg[b] += 1", "queue.popleft()", "indeg[s] -= 1"):
        if probe not in src:
            bail(f"INCONCLUSIVE: reviewed line absent from disk: {probe!r}")
    ns = {"deque": deque}
    exec(compile(src, path + "::ListingE", "exec"), ns)
    return ns["topo_order"], src


NODES = [f"S{i}" for i in range(1, 15)]
EDGES = [("S1","S2"),("S1","S3"),("S2","S4"),("S3","S4"),("S3","S5"),
         ("S4","S6"),("S5","S6"),("S5","S7"),("S6","S8"),("S7","S8"),
         ("S8","S9"),("S8","S10"),("S9","S11"),("S10","S11"),
         ("S11","S12"),("S12","S13"),("S12","S14"),("S13","S14")]
BACK_EDGE = ("S14", "S3")          # closes S3 -> ... -> S14 -> S3


def has_cycle(nodes, edges):
    """Independent DFS cycle oracle -- does NOT reuse the code under test."""
    succ = {n: [] for n in nodes}
    for a, b in edges:
        succ[a].append(b)
    WHITE, GREY, BLACK = 0, 1, 2
    colour = {n: WHITE for n in nodes}

    def visit(u):
        colour[u] = GREY
        for v in succ[u]:
            if colour[v] == GREY or (colour[v] == WHITE and visit(v)):
                return True
        colour[u] = BLACK
        return False

    return any(colour[n] == WHITE and visit(n) for n in nodes)


def main():
    topo_order, _ = load_listing_e(provenance(TARGET), TARGET)

    # --- control: the acyclic rollout graph must order all 14 stages ---
    if has_cycle(NODES, EDGES):
        bail("INCONCLUSIVE: control graph is not acyclic -- transcription error")
    try:
        clean = topo_order(list(NODES), list(EDGES))
    except Exception as exc:
        bail(f"INCONCLUSIVE: acyclic control raised {type(exc).__name__}: {exc}")
    if len(clean) != len(NODES):
        bail(f"INCONCLUSIVE: acyclic control already truncated ({len(clean)}/{len(NODES)})")
    print(f"control (acyclic): {len(clean)}/{len(NODES)} stages ordered, no exception")

    # --- probe: same graph plus one back edge ---
    nodes, edges = list(NODES), EDGES + [BACK_EDGE]
    if not has_cycle(nodes, edges):
        bail("INCONCLUSIVE: probe graph has no cycle -- oracle disagrees, precondition unmet")

    nodes_before, edges_before = copy.deepcopy(nodes), copy.deepcopy(edges)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            order = topo_order(nodes, edges)
        except Exception as exc:
            print(f"CLEAN: cyclic input raised {type(exc).__name__}: {exc}")
            return 0

    if not (isinstance(order, list) and set(order) <= set(nodes)):
        bail("INCONCLUSIVE: return shape changed (not a list of stage names); "
             f"got {type(order).__name__}={order!r} -- re-review the contract")
    if len(order) >= len(nodes):
        bail(f"CLEAN: no truncation on cyclic input ({len(order)}/{len(nodes)})")

    unmutated = (nodes == nodes_before and edges == edges_before)
    dropped = [n for n in nodes if n not in order]
    print(f"cyclic probe: returned list of length {len(order)} for {len(nodes)} stages -> {order}")
    print(f"warnings emitted: {len(caught)}; caller inputs unmutated: {unmutated}")
    print(f"simulated rollout deployed {len(order)}, silently skipped {len(dropped)}: {dropped}")

    if caught or not unmutated:
        bail("CLEAN: an out-of-band signal (warning or mutated input) reaches the caller")

    raise AssertionError(
        f"FALSIFIED (C0004 CONFIRMED): topo_order returned a {len(order)}-stage rollout order "
        f"for a {len(nodes)}-stage plan whose graph provably holds a cycle, raising nothing, "
        f"warning nothing, and leaving the caller's nodes/edges untouched. The short list is "
        f"the only channel, so a caller that does not length-check deploys {order} and skips "
        f"{len(dropped)} stages ({', '.join(dropped)}) while reporting success. Fails open."
    )


if __name__ == "__main__":
    sys.exit(main())
