# HELIOS-3 Zone Controller — Configuration Rollout and Distribution Design Reference

**Document ID:** SW-21-REF-04
**Scope:** One service (the HELIOS-3 zone controller, its admission limiter, its distribution ring, its manifest index, its retry scheduler, its wave tracker and its accounting path) together with the reference implementations that define its behaviour: cost of the planning and distribution paths, capacity and constant cross-checks, invariants and boundary conditions, concurrency and interleaving, the rollout dependency graph, numerical behaviour, and API contracts.
**Status:** Internal technical reference. Assertions carry traceability tags (ZC-nn) so review is logged against individual statements rather than whole sections.

---

## 1. Purpose and structure of this reference

HELIOS-3 pushes configuration manifests to a fleet of agent nodes. A rollout is planned as a dependency graph of stages, admitted through a token-bucket limiter, addressed through a consistent-hash ring, indexed through fixed-size manifest blocks, retried under exponential backoff with jitter, and accounted for by an online mean-and-variance estimator in the metrics sidecar. The parts share one set of constants and one set of reference implementations, so they are described together.

### 1.1 Conventions

Every cost statement is a statement about the reference implementations printed in section 2 and about no other. Where a bound is asserted, the statement names whether it is a worst-case bound, an expectation over a stated distribution, or a figure realised on the data printed here; that distinction is part of the claim, not a wording preference. Byte prefixes are decimal (kB = 10^3 bytes, MB = 10^6, GB = 10^9) and binary prefixes are written out (MiB = 2^20 bytes). Every figure below is re-derivable from those constants, the listings of section 2 and the edge list of section 7.

Design inputs used throughout:

| Symbol | Value | Meaning |
|--------|-------|---------|
| F      | 262 144 | agent nodes in the managed fleet, that is 2^18 |
| w      | 4 096 | nodes addressed in one rollout wave, that is 2^12 |
| V      | 64 | waves in a full fleet rollout, F / w |
| M      | 24 | distribution members published on the hash ring |
| T      | 128 | virtual points published per member |
| L      | 64 | shards of the descriptor cache, that is 2^6 |
| C      | 1 024 | entry capacity of one descriptor-cache shard |
| P      | 8 192 | bytes in one manifest block |
| E      | 32 | bytes in one manifest entry, a 16-byte digest, an 8-byte offset and an 8-byte length |
| r      | 400 | configuration pushes per second, the sustained design load |
| z      | 12 kB | mean serialised manifest carried by one push |
| B_tok  | 240 | token-bucket capacity, in tokens |
| R_tok  | 60 | token-bucket refill rate, tokens per second |
| d_0    | 250 ms | base retry delay |
| d_max  | 32 000 ms | retry-delay ceiling |
| u      | 2^-53 | unit roundoff of the binary64 format |

---

## 2. Reference implementations

The listings below are the definitions the rest of this document reasons about, printed in full so every behavioural statement can be checked against the code. The section imports `bisect`, `hashlib`, `random`, `threading`, `time` and `collections.deque`.

Listing A, the admission limiter.

```python
class TokenBucket:
    def __init__(self, capacity, refill_per_sec):
        self.capacity = float(capacity)
        self.rate = float(refill_per_sec)
        self.tokens = float(capacity)
        self.last = time.monotonic()

    def allow(self, cost=1.0):
        now = time.monotonic()
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False
```

Listing B, the block search used by the manifest reader.

```python
def find_block(offsets, pos):
    lo, hi = 0, len(offsets) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if offsets[mid] <= pos:
            lo = mid
        else:
            hi = mid - 1
    return lo
```

Listing C, the retry schedule.

```python
def backoff_delay(attempt, base_ms=250, ceiling_ms=32000, rand=random.random):
    capped = min(ceiling_ms, base_ms * (2 ** attempt))
    return rand() * capped
```

Listing D, the distribution ring.

```python
def ring_hash(s):
    return int.from_bytes(hashlib.blake2b(s.encode(), digest_size=8).digest(), "big")


class HashRing:
    def __init__(self, members, vnodes):
        self.points = []
        for m in members:
            for j in range(vnodes):
                self.points.append((ring_hash(f"{m}#{j}"), m))
        self.points.sort()
        self.keys = [p[0] for p in self.points]

    def locate(self, key):
        idx = bisect.bisect_right(self.keys, ring_hash(key))
        return self.points[idx % len(self.points)][1]
```

The service constructs its ring as `HashRing([f"dist-{i:02d}" for i in range(M)], T)`, so the members are named dist-00 through dist-23 and every ring figure below is reproducible.

Listing E, the stage planner.

```python
def topo_order(nodes, edges):
    indeg = {n: 0 for n in nodes}
    succ = {n: [] for n in nodes}
    for a, b in edges:
        succ[a].append(b)
        indeg[b] += 1
    queue = deque(n for n in nodes if indeg[n] == 0)
    order = []
    while queue:
        n = queue.popleft()
        order.append(n)
        for s in succ[n]:
            indeg[s] -= 1
            if indeg[s] == 0:
                queue.append(s)
    return order
```

Listing F, the wave tracker.

```python
class WaveTracker:
    def __init__(self, wave_size):
        self.wave_size = wave_size
        self.done = 0
        self.lock = threading.Lock()
        self.ready = threading.Condition(self.lock)

    def record(self):
        with self.lock:
            self.done += 1
            if self.done == self.wave_size:
                self.ready.notify_all()

    def wait_for_wave(self):
        with self.ready:
            while self.done < self.wave_size:
                self.ready.wait()
            return self.done
```

Listing G, the online mean-and-variance estimator used by the metrics sidecar.

```python
def welford(xs):
    n = 0
    mean = 0.0
    m2 = 0.0
    for x in xs:
        n += 1
        delta = x - mean
        mean += delta / n
        delta2 = x - mean
        m2 += delta * delta2
    return n, mean, m2
```

---

## 3. Cost of the planning and distribution paths

**ZC-01.** The planner of Listing E initialises one in-degree counter per node, dequeues each node once, and decrements exactly one counter per edge. On the rollout graph of section 7, with n = 14 stages and m = 18 edges, an instrumented run performs 14 dequeues, 14 enqueues and 18 decrements, so the cost is Theta(n + m).

**ZC-02.** Listing B halves the residual span [lo, hi] on each pass, beginning at P / E - 1 = 255 on a full manifest block. Sweeping every position a block covers measures a worst case of ceil(log2 256) = 8 passes, and no position needs a ninth.

**ZC-03.** The ring of Listing D holds M x T = 3 072 sorted points, so the binary search inside locate performs at most 12 comparisons: 2^11 = 2 048 is less than 3 073 and 2^12 = 4 096 is not, so ceil(log2 (3 072 + 1)) = 12 and the interval cannot survive a thirteenth halving.

**ZC-04.** Adding a twenty-fifth member publishes a further T = 128 points on a ring that then carries 3 200, so the arriving member owns 128 / 3 200 = 1 / 25 of the ring and 4 per cent of the key space changes owner in expectation. Locating node-000000 through node-262143 against the twenty-four-member ring and again with dist-24 added moves 11 524 keys, that is 4.40 per cent, every one onto dist-24 and none between two members already present.

**ZC-05.** The unjittered delay of Listing C is min(d_max, d_0 x 2^attempt), which first reaches the ceiling at attempt index 7, since 250 x 2^7 = 32 000 and 250 x 2^6 = 16 000. Summed over attempt indices 0 through 7 the unjittered schedule is 250 x (2^8 - 1) = 63 750 ms, that is 63.75 s of accumulated wait before the eighth retry is issued.

**ZC-06.** The returned delay is a uniform draw on [0, capped), whose expectation is capped / 2, so by linearity the expected accumulated wait over the same eight attempts is 63.75 / 2 = 31.875 s. A Monte Carlo estimate over 200 000 schedules returns a mean within 0.1 s of that figure, a tolerance of about four standard errors at that sample size.

The costs above are worst-case except ZC-04 and ZC-06, which are expectations under the distributions stated with them.

---

## 4. Capacity, load and constant cross-checks

**ZC-07.** A full rollout covers V = F / w = 262 144 / 4 096 = 64 waves. At the design load of r = 400 pushes per second one wave of w = 4 096 nodes occupies 4 096 / 400 = 10.24 s and the full fleet 655.36 s, that is 10.92 minutes of push time exclusive of stage barriers.

**ZC-08.** With P = 8 192 bytes to a manifest block and E = 32 bytes to an entry, a full block holds P / E = 256 entries. One entry per fleet node fills F / 256 = 1 024 blocks, occupying 1 024 x 8 192 = 8 388 608 bytes, exactly 8 MiB, with no partial block at the tail because F is an exact multiple of 256.

**ZC-09.** At r = 400 pushes per second carrying z = 12 kB apiece the distribution bandwidth is 4.8 MB/s, that is 38.4 Mbit/s. Over a 24-hour window the same rate moves 400 x 12 000 x 86 400 = 414 720 000 000 bytes, that is 414.72 GB or 386.24 GiB.

**ZC-10.** The descriptor cache has room for L x C = 64 x 1 024 = 65 536 entries with every shard full. The shard index is the low bits of the key hash, and because L = 2^6 the mask is 63; a key population whose hashes share a residue modulo 64 lands entirely in one shard, whose capacity is C = 1 024 rather than the nominal 65 536.

**ZC-11.** Each ring member publishes T = 128 of the M x T = 3 072 points, so its expected share of the key space is 128 / 3 072 = 1 / 24 = 4.17 per cent. Summing the arc each member owns gives a mean share of 4.167 per cent with a relative standard deviation near 9 per cent, close to the 1 / sqrt(T) = 8.8 per cent spread expected of T independent arcs.

**ZC-12.** Under single-threaded use, over any window of t seconds the limiter of Listing A admits at most B_tok + R_tok x t unit-cost requests whatever the arrival pattern, that being the whole token supply available in the window; at t = 10 s the ceiling is 840. In the fluid model a demand of 300 per second drains the full bucket after B_tok / (300 - R_tok) = 240 / 240 = 1.0 s, after which the admitted rate settles at R_tok = 60 per second.

**ZC-13.** Manifest entries are keyed by a 16-byte digest, that is 128 bits. Across the F = 2^18 entries of one fleet manifest the birthday approximation F^2 / (2 x 2^128) evaluates to 2^-93, or 1.01 x 10^-28, and the closed form 1 - exp(-F (F - 1) / (2 x 2^128)) agrees to three figures in exact arithmetic.

---

## 5. Invariants, preconditions and postconditions

**ZC-14.** Under single-threaded use with non-negative costs Listing A maintains the invariant 0 <= tokens <= capacity across every call. The refill is clamped by min against the capacity and the subtraction is guarded by the test tokens >= cost, so neither can push the count outside that interval. A randomised sweep of 120 000 calls with mixed costs and gaps records no violation.

**ZC-15.** Listing B carries the precondition that offsets is non-empty, sorted non-decreasing, and that offsets[0] <= pos. Its postcondition is that the returned index lies in [0, len(offsets) - 1], that offsets[index] <= pos, and that index is the largest such position. A sweep over every position spanned by a full 256-entry block returns indices covering 0 through 255 with no violation.

**ZC-16.** While every intermediate stays finite, Listing G maintains the invariant m2 >= 0 after every update, because delta is the deviation of the new value from the previous mean and delta2 its deviation from the updated mean; the update moves the mean towards the new value, so the two deviations carry the same sign and their product is non-negative. Two thousand randomised streams produce no negative intermediate.

**ZC-17.** The postcondition of locate rests on a non-empty ring and a bounded index: bisect.bisect_right(self.keys, h) returns a value in [0, len(points)], and len(points) exactly when h reaches or exceeds every published point. The subsequent idx % len(self.points) maps that case back to 0, so the subscript is always in range; the modulo closes the ring rather than guarding it, and removing it would raise IndexError on keys hashing past the last point.

**ZC-18.** In Listing E each edge is visited once, from the successor list of its tail, so exactly m = 18 decrements occur and no counter is decremented more often than its node has incoming edges. The loop invariant that no in-degree counter becomes negative therefore holds, and an instrumented run confirms zero negative intermediates and all fourteen residual counters at zero on exit.

**ZC-19.** The planner carries the postcondition that it returns a list shorter than the node count exactly when the graph holds a cycle, because a node on a cycle never reaches in-degree zero and is never enqueued. On the printed graph the order has length 14, equal to the node count; adding the back edge S14 -> S3 shortens it to 2 and stalls twelve stages.

**ZC-20.** The postcondition of Listing C is a value in the half-open interval [0, min(d_max, d_0 x 2^attempt)), so every delay is non-negative and none reaches d_max = 32 000 ms. The unjittered cap is non-decreasing in the attempt index and constant from index 7 onward; the sampled delays are not ordered, since each is drawn uniformly below its own cap. Sampling 48 000 delays across attempt indices 0 through 15 places every draw inside that interval.

---

## 6. Concurrency, atomicity and interleaving

**ZC-21.** The statement self.done += 1 in Listing F is a read-modify-write and is not atomic: disassembly shows LOAD_ATTR, BINARY_OP and STORE_ATTR as separate instructions, so two threads executing it without mutual exclusion could interleave between load and store and lose an increment. It is safe here only because every execution lies inside the with block holding the lock.

**ZC-22.** Under concurrent use the Condition in Listing F is constructed over the lock the class already holds, so self.ready and self.lock guard the same primitive and the two with blocks exclude one another rather than only themselves. Identity comparison on a constructed instance confirms the condition's underlying lock is the same object as self.lock, so record excludes wait_for_wave.

**ZC-23.** A concurrent waiter re-tests its predicate in a while loop rather than an if, so a wake arriving before the count is reached returns the thread to wait, not to the caller. The predicate is monotone, done being only ever incremented, so once satisfied it stays satisfied and a late waiter arriving after the wave completed returns without blocking.

**ZC-24.** notify_all rather than notify is required because several threads may wait concurrently on the same wave. The condition is signalled once, on the increment that reaches wave_size, so under notify one waiter would be released and the rest would block indefinitely. A four-waiter demonstration on a three-node wave releases all four.

**ZC-25.** With any number of concurrent callers, no method in Listing F takes a second lock while a first is held: an abstract-syntax scan reports a maximum with-nesting depth of one in both methods, and the two with statements name self.lock and self.ready, the same primitive. A hold-and-wait cycle requires some thread to own one lock and request another, and no such path exists; wait releases the underlying lock while blocked, so a waiter cannot shut out a recorder.




---

## 7. The rollout dependency graph

Stages are named S1 through S14 and the plan is the directed graph on the following edge list, printed in full so every property below can be recomputed.

S1 -> S2, S1 -> S3, S2 -> S4, S3 -> S4, S3 -> S5, S4 -> S6, S5 -> S6, S5 -> S7, S6 -> S8, S7 -> S8, S8 -> S9, S8 -> S10, S9 -> S11, S10 -> S11, S11 -> S12, S12 -> S13, S12 -> S14, S13 -> S14.

**ZC-27.** The list defines n = 14 nodes and m = 18 edges, and every edge runs from a lower-numbered stage to a higher-numbered one. Stage index is therefore itself a topological order, and no cycle can exist, since a cycle needs an edge running from a higher index to a lower one.

**ZC-28.** Exactly one stage has in-degree zero, S1, and one has out-degree zero, S14, so the plan has a single entry point and a single completion point. The underlying undirected graph is connected, so no stage is isolated.

**ZC-29.** The longest directed path is S1, S2, S4, S6, S8, S9, S11, S12, S13, S14, visiting 10 stages across 9 edges. That critical-path length of 10 is a floor: no schedule completes the rollout in fewer than 10 sequential slots however many stages run in parallel, since those 10 are pairwise ordered by the edge list.

**ZC-30.** The graph admits exactly 28 distinct topological orderings under exhaustive depth-first enumeration, so the scheduler may choose among 28 legal stage sequences. The count is a property of the edge list alone, not of the traversal Listing E performs, which returns just one of them.

**ZC-31.** The edge S12 -> S14 is implied by the path S12 -> S13 -> S14, so it constrains nothing the remaining edges do not. The transitive reduction therefore carries 17 edges rather than 18, and that is the only edge it removes; the set of legal orderings is identical with and without it.

**ZC-32.** S8 has 7 ancestors and 6 descendants, and 7 + 6 + 1 accounts for all 14 stages, so S8 is ordered with respect to every other stage. Every one of the 28 topological orderings therefore places exactly seven stages before S8 and six after it, and S8 acts as a barrier no stage can cross.

**ZC-33.** The largest set of mutually unordered stages has size 2 — for instance S9 and S10, which have no directed path between them in either direction. The plan therefore never offers more than two stages that may run at once, and a scheduler holding more than two stage-workers cannot use the surplus here.

---

## 8. Numerical behaviour of the accounting path

**ZC-34.** Under round-to-nearest a binary64 value carries a relative representation error of at most u = 2^-53 = 1.1102 x 10^-16. One tenth does not fall on the grid: the stored double is 0.100 000 000 000 000 005 551 115 123 125 782 7..., which exceeds one tenth by 5.5511 x 10^-18. As a fraction of the value that excess is 5.5511 x 10^-17, exactly 2^-54, so it sits at half the representation bound.

**ZC-35.** The textbook one-pass variance, formed as (sum of squares - (sum)^2 / n) / (n - 1), loses the whole result to cancellation on values that are large and close together. On the readings 100 000 000, 100 000 001 and 100 000 002 the exact sample variance is 1, and the textbook expression in binary64 returns exactly 0.

**ZC-36.** Listing G on the same three readings returns m2 = 2.0 and therefore a sample variance of m2 / (n - 1) = 1.0, matching the exact rational result. The estimator never forms the sum of squares, so the cancellation of ZC-35 has nothing to act on; a two-pass computation in the same format also returns 1.0.

**ZC-37.** Accumulating 0.1 ten times by repeated addition in binary64 yields 0.999 999 999 999 999 9, not 1.0, and the shortfall is exactly 1.1102 x 10^-16, one unit roundoff. The value returned is the largest double below 1.0, the spacing of the binary64 grid immediately below 1 being exactly u.

**ZC-38.** A cumulative push counter held as a binary32 float stops advancing at 2^24 = 16 777 216, because beyond that magnitude the spacing of the format exceeds one and an increment of one rounds back to the stored value. At r = 400 per second that is reached after 41 943.04 s, or 11.65 hours, inside the 24-hour reporting window, so the sidecar holds this counter in a wider format.

**ZC-39.** Byte totals are held as Python integers rather than doubles for the same reason at the other end of the range: the spacing of the binary64 grid at 10^17 is 16, so adding one to that magnitude leaves it unchanged. The daily total of 414 720 000 000 bytes from ZC-09 is exact as an integer at any magnitude the accounting path reaches.

---

## 9. API contracts and structural properties

**ZC-40.** TokenBucket defines exactly two methods, __init__ and allow, and no method named consume, acquire or take is defined on the class. A call site invoking one of those names raises AttributeError at the call site instead of admitting a request unnoticed.

**ZC-41.** TokenBucket.allow takes self and cost, with cost defaulting to 1.0 and no variadic parameter. Its arity is therefore one or two positional arguments and no other, so a signature mismatch at a call site is reported at the call boundary; it contains exactly two return statements, one True and one False, so the result is always a bool.

**ZC-42.** find_block reads only its two parameters, its three local names and the builtin len. It declares nothing global or non-local, performs no attribute or subscript assignment, and calls no function but len, so its result is fixed by its arguments and the offsets list is left unmodified.

**ZC-43.** WaveTracker.record contains no return statement and therefore returns None on every path, while wait_for_wave has a single-exit return of self.done. Because the loop exits only when the predicate fails, the value returned is at least wave_size, so it serves as a completion count but does not identify which call closed the wave.

**ZC-44.** Every name imported at the head of section 2 is used by at least one listing: time by A, random by C, bisect and hashlib by D, deque by E, threading by F. A lint pass over the section reports no unused import and a static type-check pass no issue.

---

## 10. Application notes

Sections 3 to 9 draw on three inputs and no others: the constants of section 1, the reference implementations of section 2, and the edge list of section 7. Every figure here is derived from those three and re-derivable by the same route — take the input, take the listing, evaluate.

The sections are coupled through those inputs rather than through one another, so a revision to any of them propagates into several at once. The fleet size F enters the ring-relocation measurement of section 3 and the wave arithmetic, manifest sizing and digest-collision estimate of section 4. The ring constants M and T enter the search cost of section 3 and the ownership share of section 4. The token-bucket constants enter the admission ceiling of section 4 and the invariant of section 5. The edge list fixes every property in section 7 and the instrumented counts in ZC-01.

Every statement names its own basis. Whatever a result depends on — the input class it is quantified over, the distribution it is averaged across, the listing it is asserted of, the execution model it assumes, or the numeric format it is evaluated in — is stated with the result, in every section alike.

The traceability tags ZC-nn attach to individual statements rather than to sections, so a note recorded against this reference attaches to the statement it concerns.

---

**End of reference SW-21-REF-04.**
