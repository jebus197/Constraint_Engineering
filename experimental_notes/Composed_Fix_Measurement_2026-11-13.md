# Measuring a composed fix rather than asserting it

**2026-11-13** · Constraint Engineering (CDSFL) · entry B169, the permission predicate reading a sentence that *describes* the founder's authority as one *claiming* it

## What this is about

`hooks/work_not_narrate.py` holds `_residue_is_his`, the predicate a Stop gate uses to tell 2 kinds of task-list entry apart: the merely unfinished, and the kind waiting on a decision only the founder can take. The file shares inode `518972710` with `~/.claude/hooks/work_not_narrate.py`, so the repository copy and the live gate are 1 file, and editing it is editing the gate that runs on every turn.

## The reported defect, and the repair that overshot

B169 recorded that the predicate matched a neighbouring entry's record of a standing rule, *that only he may reject a feature request*. That sentence describes an authority in general; it says nothing about the entry containing it.

A repair shipped the same morning by a different route from the one B169 proposed: suppress the match when the grammatical object is indefinite (`a`, `an`, `one`, `any`), on the reasoning that an indefinite object names a **class**. It is right about the reported case.

It is wrong about a sentence no test reached:

```
"only he may authorise a paid panel dispatch, and this entry needs one"
    object rule alone  ->  False   (no permission needed)
    correct answer     ->  True
```

The object is indefinite, so the rule suppressed; but the sentence names a class **and claims it for this entry**. The gate would have prodded the session into work requiring his authorisation.

The 2 error directions are not symmetrical:

| direction | effect | visible? |
|---|---|---|
| false positive | stalls work | yes — somebody waits |
| false negative | acts without him | **no** |

The repair had moved the guard into the quieter and more dangerous mode, and every existing polarity test passed with that defect present, because each case had either a definite object or no tie to the entry.

## The measurement

9 labelled sentences — 2 quoted from B169, the rest constructed to probe the boundary — scored against 6 candidate rules.

| rule | score | Wilson 95% |
|---|---|---|
| no suppressor | 4 of 9 | [0.188779, 0.733349] |
| object rule alone (live that morning) | 6 of 9 | [0.354202, 0.879416] |
| **subject rule** (B169's own proposal) | 8 of 9 | [0.565000, 0.980109] |
| both, naively composed | 7 of 9 | [0.452589, 0.936775] |
| **narrowed** object rule alone | 8 of 9 | [0.565000, 0.980109] |
| **narrowed object + subject (shipped)** | **9 of 9** | [0.700855, 1.000000] |

`composability-requires-a-measurement` — his standard of 2026-10-02 — permits composing only where the pair demonstrably beats either fix in isolation, and prefers the single fix otherwise. The shipped rule clears it at **9 against 8**. The *naive* composition does not, scoring below both parts, which is why the narrowing is load-bearing rather than decorative.

Each part earns its place on a different case:

- the **object rule** on the bare class statement,
- the **narrowing** on the 2 residues tied to *this entry*,
- B169's **subject rule** on an attributive frame with a *definite* object.

## An error of mine, corrected in the same pass

The first version of this repair was committed with a source comment quoting `6/7/6/8` over **8** cases and claiming dominance. An ablation then showed the subject rule changed the verdict on **0 of those 8 cases** and on **0 of 181 live entries** — so the narrowed object rule alone tied at 8, and his standard refuses a composition that merely ties.

The cause was a hole in the corpus, not a redundant rule. Every attributive case written also had an indefinite object, which the object rule already suppresses, so **no case reached the subject rule at all**. The missing case is the minimal pair of a case already present:

```
"only he may approve this change"                 -> True   (claims)
"his rule is that only he may approve this change" -> False  (reports)
```

Identical shape, definite object, differing only in the attributive frame, opposite labels. It was added **after** the ablation, and that is declared in the producer, because adding a case that rescues a pattern is the shape of a flattering measure.

## The honest limit

Both new parts are **inert on the live list**: 0 of 181 entries change verdict, and the 53 sentences where an `only he` co-occurs with an attributive frame are already suppressed by the object rule. Support is **n = 9 constructed cases, not 181 live ones** — carried on the principle that a regression guard must not need a live defect.

## Verification

- Guard: `bench/tests/test_a_movable_entry_is_not_one_that_merely_asks_nothing_2026-11-12.py`, class `TestTheNarrowingAndTheSubjectRule` — 4 tests, including B169's constructed case as the falsifier it asked for, and a check that **each part still changes at least 1 verdict** so neither can quietly become decorative. 25 of 25 green.
- Mutations: `scripts/the_residue_rule_mutations_2026-11-13.py` — **7 of 7 red**. Because the subject is the live gate, the harness reads the original bytes first, restores in a `finally`, and compares SHA-256 rather than assuming. It does **not** use `git checkout --`, which would have discarded the uncommitted repair instead of the mutation.
- Producer: `scripts/which_residue_rule_discriminates_2026-11-13.py` — computes the dominance test rather than asserting it, and names the parts the composition is made of rather than any variant that happens to tie.

## The refusal that stands

B169 noted that rewording the neighbouring entry so its evidence stopped tripping the predicate would be gaming the instrument, and declined it in writing. That entry's wording is untouched. The predicate is what changed.

---

Written under CDSFL note standard v1.9.
