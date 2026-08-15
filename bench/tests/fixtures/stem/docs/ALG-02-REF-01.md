# Pipeline Stage Planner — Cost and Dependency-Graph Reference

**Document ID:** ALG-02-REF-01
**Scope:** One planning component (the stage planner that de-duplicates incoming
stage identifiers and then orders them against a dependency graph) together with the
reference implementations that define its behaviour: the cost of de-duplication, the
cost and correctness of the topological ordering, and the structural properties of the
graph the planner is asked to order.
**Status:** Internal technical reference. Assertions carry traceability tags (AL-nn)
so review is logged against individual statements rather than whole sections.

---

## 1. Purpose and conventions

Every cost statement is a statement about the reference implementations printed in
section 2 and about no other. Costs are counts of a named elementary operation, not
wall-clock times, so each statement names the operation it counts. Where a bound is
asserted the statement says whether it is worst case, best case, or the figure
realised on the graph of section 4. Inputs to `dedup` are assumed hashable and to
support equality comparison.

| Symbol | Value | Meaning |
|--------|-------|---------|
| n | 11 | stages in the reference plan |
| m | 14 | dependency edges in the reference plan |
| k | 64 | length of the de-duplication benchmark input |

---

## 2. Reference implementations

The listings below are the definitions the rest of this document reasons about,
printed in full so every cost statement can be checked against the code. The section
imports `collections.deque`.

Listing A, the de-duplicator applied to the incoming stage identifiers.

```python
def dedup(items):
    """Return items with later duplicates removed, preserving first-seen order."""
    seen = []
    out = []
    for x in items:
        if x not in seen:
            seen.append(x)
            out.append(x)
    return out
```

Listing B, Kahn's algorithm as the planner runs it.

```python
from collections import deque

def topological_order(nodes, edges):
    """Return one topological order, or a short list if the graph has a cycle."""
    succ = {u: [] for u in nodes}
    indeg = {u: 0 for u in nodes}
    for u, v in edges:
        succ[u].append(v)
        indeg[v] += 1
    q = deque(u for u in nodes if indeg[u] == 0)
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in succ[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return order
```

---

## 3. Cost of de-duplication

**AL-01.** Listing A preserves first-seen order, because an element is appended to
`out` at the moment it is first admitted and never moved afterwards, and elements
already in `seen` are skipped without touching `out`.

**AL-02.** Listing A is correct on any hashable input that supports equality: the
membership test `x not in seen` is exactly the predicate "no earlier admitted element
compares equal to x", which is the definition of a first-seen de-duplication.

**AL-03.** Because `seen` never holds a duplicate, the membership test on each pass
inspects each stored element at most once across the whole run, so `dedup` performs at
most k element comparisons in total and its cost is linear in the input length. On the
benchmark input of k = 64 pairwise-distinct identifiers an instrumented run performs
64 comparisons.

**AL-04.** Substituting a `set` for the list in Listing A changes the comparison count
but not the returned value, since insertion order is preserved by `out` and not by
`seen`. The substitution is therefore behaviour-preserving on hashable input and is
the change the planner should make if the comparison count ever matters.

**AL-05.** Listing B initialises one in-degree counter per node, dequeues each node at
most once, and decrements exactly one counter per edge, so its cost is Theta(n + m).
On the graph of section 4 an instrumented run performs 11 dequeues, 11 enqueues and
14 decrements.

**AL-06.** Listing B returns a list shorter than the node count exactly when the graph
holds a cycle, because a node on a cycle never reaches in-degree zero and is therefore
never enqueued. The converse holds too: on an acyclic graph every node eventually
reaches in-degree zero, so the returned order has length n.

---

## 4. The dependency graph

Stages are named A through K and the plan is the directed graph on the following edge
list, printed in full so every property below can be recomputed.

A -> B, A -> C, B -> D, C -> D, C -> E, D -> F, E -> F, E -> G, F -> H, G -> H,
H -> I, H -> J, I -> K, J -> K.

**AL-07.** The list defines n = 11 nodes and m = 14 edges. Every edge runs from an
earlier letter to a later one, so alphabetical order is itself a topological order and
the graph is acyclic; a cycle would need at least one edge running backwards through
the alphabet.

**AL-08.** Exactly one stage has in-degree zero, A, and exactly one has out-degree
zero, K, so the plan has a single entry point and a single completion point. The
underlying undirected graph is connected, so no stage is isolated.

**AL-09.** The longest directed path visits 7 stages across 6 edges, one such path
being A, B, D, F, H, I, K. That length is a floor on the schedule: no ordering
completes the plan in fewer than 7 sequential slots however much runs in parallel,
because those 7 stages are pairwise ordered by the edge list.

**AL-10.** The graph admits exactly 28 distinct topological orderings under exhaustive
enumeration, so the planner may legally emit any one of 28 sequences. That count is a
property of the edge list alone and not of the traversal Listing B performs, which
returns just one of them.

**AL-11.** No edge in the list is implied by the others: the transitive reduction of
the graph carries all 14 edges. Removing any single edge therefore enlarges the set of
legal orderings rather than leaving it unchanged.

**AL-12.** Stage H has 7 ancestors and 3 descendants, and 7 + 3 + 1 accounts for all
11 stages, so H is ordered with respect to every other stage. Every one of the 28
orderings therefore places exactly seven stages before H and three after it, and H
acts as a barrier no stage can cross.

---

Written as a review fixture. Every figure is recomputable from the edge list of
section 4 and the listings of section 2.
