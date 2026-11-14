<!-- PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'asking_predicate_and_fourth_standard_2026-11-14_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 4548de28dad53e9ff40f65f7340189e75a0c498a672405c57310711524736a01
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited. -->
# PROPOSED 4th FORMAL STANDARD — NOT IN FORCE — AWAITS THE FOUNDER'S RULING

**Why this file is here and not in `bench/directives/universal/cdsfl_core_formal.md`.**
Verified by execution against the real `bench/cdsfl_registry/composer.py` on
2026-11-14: `_render_universal_minimal` carries **every** block of
`cdsfl_core_formal.md` that `_block_is_hard()` accepts **verbatim** into every
seat's prompt, and `_block_is_hard()` is a keyword test over
`_HARD_BLOCK_MARKERS = (" HARD ", " MUST ", " NEVER ", " REQUIRED ",
" NON-NEGOTIABLE ", " FORBIDDEN ", " DO NOT ", " ALWAYS ")`. A draft of the
paragraph below was split into 2 blocks; **1 was accepted as HARD, and it was
the directive — the `PROPOSED — NOT IN FORCE` header split into a separate
block that `_block_is_hard()` rejected.** So writing an unratified standard into
that file installs it as a binding HARD constraint on all six seats **with its
own not-in-force warning silently stripped off**. The live file currently yields
26 such blocks. This is reported as a defect in `composer.py` — that file has no
notion of a block drafted but not in force — and is NOT worked around by
rewording the draft to dodge the keywords, because the next author would not
know to.

---

## The paragraph, to paste

> **hil-consequence (a scope-correction to `simplest-sufficient`, not a competing
> criterion).** Where a change alters a figure, a list, a name, a queue or a
> verdict that the human in the loop READS AND ACTS ON, the cost to that human
> is part of what `simplest-sufficient` means by *sufficient*, and a fix that
> leaves that cost in place has not discharged the requirement however small it
> is. Simplicity is therefore never outranked: a fix more elaborate than its
> root cause requires is still refused, because an addition nothing reaches is
> not additive either. Where the standard applies, a proposed fix MUST enumerate
> EVERY consumer of the changed value by file and line, and for each consumer
> name the error direction that is INVISIBLE to him there — an unenumerated
> consumer is an unmet condition, not an omission, and the direction is a
> property of the value PAIRED WITH THE CONSUMER, never of the value alone,
> because the same verdict can be dismissible noise on one surface and silent
> removal on another. Consequence is ORDINAL and the ordering is: silent
> omission of something he must act on ≻ visible over-report ≻ cosmetic cost,
> critical at silent omission. It is SELECTED across surfaces by maximum and
> never summed, averaged or interpolated, and it is reported as a (value,
> scale-name) pair on the surface's own terms — the figure, the list, the
> stalled entry — never as a bare number. Where the consequence belongs to an
> APPLICATION domain rather than to this project, the application's ordering and
> critical level are INHERITED and named, not replaced by a number of this
> project's own; the declared `software` scale (CVSS v4.0 base score) cannot be
> used here, because CVSS v4.0 requires an Attack Vector in {N, A, L, P}, all of
> which presuppose an adversary, and a wrong decision count has none.
> A fix is inadmissible if it leaves any invisible direction unnamed, if it moves
> any error toward silent omission, or if it raises invisible error on any
> surface — regardless of its aggregate across surfaces, since an aggregate is a
> sum and a sum is inadmissible on an ordinal scale. Every application of this
> standard MUST ship a named runnable invariant for the direction it claims is
> safe, or state plainly that none can be written; the general question "which
> surface does the HIL read" is a judgement about him and not about the code, and
> is not mechanisable. Where the change touches no surface he reads, this
> standard is silent.

---

## Why this wording and not either blind seat's

The 2 blind replies agreed to adopt-with-changes and proposed **2 different
things**, not one thing twice. Seat `cc2` proposed a **scope-correction** to
`simplest-sufficient` with a per-surface ENUMERATE / SIGN procedure. Seat
`fable` proposed a **4th standard with an ordinal ladder** that OUTRANKS
simplicity on conflict, plus a mandatory runnable invariant. The structural
claims are incompatible: one says the standards cannot conflict by construction,
the other says one wins when they do.

Encoded as 3 decision functions over 8 constructed cases and executed —
`scripts/does_the_composed_hil_standard_beat_either_half_2026-11-14.py` — over
the 7 cases that touch a surface he reads:

| text | decides | Wilson 95% |
|---|---|---|
| SCOPE (`cc2`) | 6 of 7 = 0.857143 | [0.486464, 0.974321] |
| ORDER (`fable`) | 5 of 7 = 0.714286 | [0.358934, 0.917781] |
| COMPOSED (above) | **7 of 7 = 1.000000** | [0.645670, 1.000000] |

The composed text decides a **strict superset** of both halves, which is the
demonstrated advantage the founder's composability wording requires rather than
the weak "they do not conflict" sense it excludes. The one case only the
composition reaches is a figure feeding a decision whose consequence scale
belongs to an application domain; both halves are silent there, and the formal
directive's own ordinality section already rules that such a domain INHERITS the
application's ordering and must say so.

**And one clause of `fable`'s proposal is carried deliberately INVERTED.** Its
"HIL outranks simplicity where they conflict" ADMITS a HIL-safe fix far more
elaborate than its root cause — measured in the table above, where SCOPE and the
composition both REFUSE it. That is this project's single most-recorded defect
class: over its own record since 2026-08-01, **11** confirmed defects were
additions nothing reached and **0** were removals of something needed. So the
ladder is carried and the ranking clause is not; `cc2`'s structural point that
HIL cost belongs INSIDE sufficiency is what makes the ladder safe to carry.

## The procedure, for the standard to be operational

```
APPLIES?      Does the changed value reach a surface the HIL reads and acts on?
              No -> the standard is silent.
ENUMERATE     EVERY consumer, by file and line. Verify each line still reads as
              claimed; an enumeration that is not re-checked against the tree is
              prose. Measured 2026-11-14: a grep-derived enumeration of this
              round's own proxy returned 3 consumers and the verified count was
              5, because the same rule was implemented twice and the second copy
              gated the morning report.
SIGN          For each consumer, the error direction INVISIBLE to him there.
RANK          The worst rank moved toward, by SELECTION (max), on the ordering
              silent omission > visible over-report > cosmetic.
INADMISSIBLE  if any consumer unenumerated, any invisible direction unnamed, any
              movement toward silent omission, invisible error raised on ANY
              surface, the fix larger than its root cause, or no runnable
              invariant shipped.
```

## What would refute the standard

A change that reaches a founder-facing surface and that the procedure cannot
classify at ENUMERATE or SIGN — or one it classifies and still selects a fix
leaving more invisible error than an alternative. A single such case makes the
standard decorative, and it should then be WITHDRAWN rather than patched. The
decidability table above is the instrument: add the case to `CASES` and re-run.
