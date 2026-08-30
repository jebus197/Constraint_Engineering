# Re-adjudicating the 133 pairs with both defects repaired

The archived adjudication was computed with two defects that were only found on 2026-08-30:

1. **`_direction`'s `SAME` was the fall-through**, so an ERRORed falsifier leg did not merely contaminate a
   verdict — it **produced** one. 40 of 178 leg-bearing directions, touching 34 of 133 pairs.
2. **`_apply_fix_to_source` corrupted patches.** A raw substring match spliced replacements *inside* an
   indented line, leaving the original line alongside and the file unparseable. 12 of 313 fixes.

This re-run uses `bench.fix_efficacy.probe_pair`, which carries the corrected verdict rule and works through
the discrimination-control overlay, so **no reviewed target is written to at any point** — unlike the
original tool, which writes to the live file and restores in a `finally`.

## Result

| | old | re-checked |
|---|---|---|
| pairs | 133 | 90 resolvable, **43 not re-checkable** |
| `SAME` | 23 | **2** |
| `DIFFERENT` | 10 | 8 |
| everything else | 100 | 80 `INCONCLUSIVE_EQUIPMENT` |

**The 43 are not refuted — they are unchecked.** Their target is absent from the discrimination-control map,
mostly exp48 and exp49. Reporting them as refuted would be the same confident-direction error this project
keeps correcting.

## The 23 SAME, precisely

| outcome | n |
|---|---|
| confirmed `SAME` | **2** — exp44 C0001/C0003 and exp44 C0032/C0037 |
| refuted | **3** |
| could not be re-checked | **18** |

**So the honest statement is: of the 5 that could be re-checked, 2 confirm and 3 fail.** Not "the evidence
base is 2".

## The three refutations are the applier repair working, and they close a causal chain

All three involve exp44 **C0028**, and all three fail with *"no applicable fix"*.

C0028's proposed fix, run through the **pre-fix** applier, produces a file that **does not parse** —
`expected an indented block after function definition, line 513`. Under the repaired applier it is correctly
refused.

So the chain is:

> applier splices mid-line → patch corrupts the target → the corrupted file is judged → the falsifiers go
> quiet on wreckage → a **false `SAME`** is recorded → that `SAME` is the evidence the `MERGED` status
> requires → `MERGED` is **terminal, with no `REOPENED` exit** → findings deleted permanently.

**Two of the original 23 `SAME` verdicts rested on a corrupted patch.** Had the merge path been wired to the
old adjudicator before 2026-08-30, that is the route by which it would have destroyed findings.

## Bearing on the founder's ruling

The founder ruled *"Then wire it"* and *"Prefer CC2's solution"*, and CC2's blocker — that the adjudicator
could not run in flight — **is removed**: `probe_pair` works through the overlay and agrees with the
post-hoc tool 10 of 10 on cleanly-decided pairs.

What has changed is the **evidence**, not the ruling. The wiring is built and validated. Turning it on now
would act on 2 confirmed pairs with 43 unchecked and a terminal, unrecoverable status at the other end. That
is a decision for the founder awake, and the recommendation is to re-run the adjudication first with the
targets for exp48/exp49 resolved, so the 43 stop being unknown.


## Why the 43 cannot be re-checked, and what it would take — FOR THE FOUNDER

The 43 are **exp48 (27) and exp49 (16)**, and their targets are absent from every map because they are
absent from the working tree:

```
/Users/georgejackson/CDSFL_review_targets/exp48_chemistry.md    exists=False
/Users/georgejackson/CDSFL_review_targets/exp49_engineering.md  exists=False
```

**This is the security design working, not a defect.** Both were moved out of the repository on
`eecdb0f`, whose own message records why:

> *"Reviewing panels carry Bash/Read/Grep/Glob — a co-located, name-derivable key made every seeded claim
> discoverable by a single `ls` (precision 1.0, recall 1.0), defeating three rounds of prose/statistical
> hardening."*

**They are recoverable.** Verified by listing names only, with no content read:

```
git ls-tree -r --name-only eecdb0f | grep exp4[89]
  bench/cdsfl_registry/targets/exp48_chemistry.md
  bench/cdsfl_registry/targets/exp49_engineering.md
```

**★ Both `eecdb0f` and `ddd74bd` are reachable from `exp39-experimental` AND FROM NOTHING ELSE.** Confirmed
again tonight with `git branch -a --contains`. That branch must not be deleted before the encrypted bundle
is verified — the standing rule, re-verified rather than recited.

**CC1 has not extracted them, and this is deliberate.** These are seeded exam targets: materialising them
re-creates the exposure `eecdb0f` closed, and exp48 is separately the run excluded for the key read. The
standing rule permits an unencrypted study copy only *after* an experiment has run, which both have — so it
is permissible, but it is a decision at the security boundary and it belongs to the founder awake, not to
CC1 at one in the morning.

If the founder rules yes, the re-check needs no repository change: the targets can be extracted to a
throwaway root and `probe_pair` pointed at it with `repo_root=`, leaving the tracked tree untouched.
