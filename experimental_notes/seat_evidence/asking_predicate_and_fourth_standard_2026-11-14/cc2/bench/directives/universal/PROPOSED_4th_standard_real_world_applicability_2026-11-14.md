<!-- PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'asking_predicate_and_fourth_standard_2026-11-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 8fc44911cdbe155f15a1527e29f83bf6168d7e91af1e22ee98a6978e6df8d5f5
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited. -->
<!--
★ WHY THIS PROPOSAL IS IN A FILE OF ITS OWN AND NOT IN `cdsfl_core_formal.md`,
WHICH IS WHERE THE BRIEF OF 2026-11-14 ASKED FOR IT.

It was written into `cdsfl_core_formal.md` first, and that was a MISTAKE caught
by execution in the same round. `composer._render_universal_minimal` carries
EVERY block of that file which `composer._block_is_hard()` accepts, VERBATIM,
into the minimal universal directive every seat receives. Measured 2026-11-14:
with the proposal in that file, `_block_is_hard()` accepted **2 of its blocks**
as HARD -- it reads MUST, NEVER, REQUIRED and "inadmissible" across the whole
file -- so an UNRATIFIED standard would have reached every seat as a binding
constraint. That is precisely the act the brief forbids: "Do not install a
changed predicate or a 4th standard as though it were settled."

`cdsfl_core_formal.md` has therefore been restored to its dispatched state,
sha256 9da304edb6c80a60, byte-exact and verified. The proposal lives here, in a
file no composer route reads, and it reaches the founder rather than the panel.

THE UNDERLYING DEFECT IS REPORTED RATHER THAN WORKED AROUND SILENTLY:
`cdsfl_core_formal.md` has NO notion of a block that is drafted but not in
force. Any future draft written there -- by a seat, or by the founder himself
sketching a standard -- becomes a HARD constraint on every seat the moment it
contains the word MUST. There is no marker, no gate and no test that
distinguishes a ratified directive from a draft. A fix would be a ratification
predicate in `_block_is_hard()` (reject a block inside a section flagged
unratified), and it is NOT taken here: it changes what reaches every seat, so
it is the founder's to rule, and this round's remit is the ruling-residue proxy.
-->

## PROPOSED 4th STANDARD — Real-World Applicability, under the HIL-Consequence Caveat

> **STATUS: PROPOSED, NOT ADOPTED. 2026-11-14.** This section is a drafted text
> placed where a 4th standard would have to live if the founder rules to adopt
> it. **It is not in force.** Nothing in this repository reads it, no gate
> enforces it, and no seat is bound by it. It is written here rather than in a
> report because a standard that is described in prose has not been delivered,
> and because this is the file by which the other 3 standards
> (`simplicity-default`, `additive-standard`,
> `composability-requires-a-measurement`) actually reach a seat. **Adoption is
> the founder's ruling and his alone.** His words that prompted it, verbatim:
> *"Another standard I am considering adopting is that of real world
> applicability, which should apply in circumstances where it involves a
> meaningful consequence for the HIL, which appears to be the case here? I would
> suggest that this is a standard we should adopt, with this 'HIL consequence'
> caveat."*

**Proposed text, 1 paragraph.**

> **real-world-applicability (HIL consequence).** Where a change alters a figure,
> a list, a name or a verdict that the human in the loop READS AND ACTS ON, the
> change is assessed on its consequence to that human and not only on its
> internal correctness. The caveat is what bounds it: the standard applies when,
> and only when, a wrong outcome would reach the HIL — meaning the defect can
> produce (i) a wrong quantity he reads, (ii) a live question that disappears
> from a list he relies on, (iii) work silently removed from a queue he believes
> is being worked, or (iv) a standard, gate or figure he is told is checked when
> nothing checks it. Where the standard applies, a proposed fix must name EVERY
> surface the changed value reaches, and for each surface state the DIRECTION in
> which an error there is invisible to him; a fix that leaves an invisible
> direction unnamed is inadmissible, and a fix that reduces error on one surface
> while silently increasing it on another is a regression regardless of its
> aggregate. Consequence to the HIL is reported on the surface's own terms — the
> figure, the list, the stalled entry — never as a bare number, because the
> project's declared `software` scale (CVSS v4.0 base score) presupposes an
> attacker and cannot score a defect that has none.

**Proposed decision procedure — the question a reviewer asks.**

```
APPLIES?   Does the changed value reach a surface the HIL reads and acts on?
           NO  -> this standard is silent; the other 3 decide.
           YES -> continue.

ENUMERATE  List EVERY consumer of the changed value, by file and line.
           An unenumerated consumer is an unmet condition, not an omission.

SIGN       For each consumer, state which error direction is INVISIBLE to him.
           Over-reporting is NOT a property of a predicate; it is a property of
           a predicate PAIRED WITH A CONSUMER, and one predicate may be read
           with opposite sign by 2 consumers.

INADMISSIBLE if any consumer is unenumerated, OR any invisible direction is
           unnamed, OR the fix increases the invisible-error count on any
           surface — even where it decreases the total.
```

**Proposed mechanism, and an honest statement of its limit.** A *partial*
mechanism exists and runs:
`scripts/which_surfaces_the_ruling_proxy_reaches_2026-11-14.py` enumerates the
consumers of one founder-facing predicate, states each consumer's invisible
direction, and scores every candidate repair on INVISIBLE-ERROR PAIRS — the
count of (entry, surface) pairs where a wrong verdict produces an outcome he
cannot detect. That count is computable, reproducible and decided the live
question it was built for. **There is NO general gate**, and this must be said
plainly rather than implied away: no test can decide for an arbitrary change
whether a value "reaches a surface the HIL reads and acts on", because that
predicate is about him and not about the code. So the standard is proposed for
adoption **with the per-case producer as its mechanism and with its generality
declared as a reported direction of travel**, which is how this project's
depth-before-breadth ratio is already held. Adopting it with NO mechanism at all
would make it the 12th confirmed instance of an addition that nothing reaches —
the failure mode `additive-standard` exists to catch — and that is the specific
reason the producer was built in the same round as the text.

**Proposed relation to the existing 3, including the case where they pull apart.**
It does not contradict `additive-standard` or
`composability-requires-a-measurement`. It appears to contradict
`simplicity-default`, and the concrete case is from the round that produced it:
the simplest sufficient repair to the ruling-residue proxy is to REPORT the
disagreement and change no verdict — 1 new predicate, 1 new dict key, no edit to
a work-gating hook. Measured, that repair leaves **5 invisible-error pairs**,
because the gate surface is untouched; only extending the same flag to the gate
reaches **0**. So the simplest sufficient fix is the one that leaves the human
exposed. **The resolution is that the conflict is apparent and not real:** the
contested word is *sufficient*. `simplicity-default` already requires a fix that
"actually discharges the requirement", and what this standard does is place the
HIL consequence INSIDE the requirement. Once it is there, the report-only repair
is not a simpler sufficient fix — it is an insufficient one, and simplicity
selects the extended fix unaided. The 4th standard is therefore better read as
fixing the SCOPE of simplicity's sufficiency test than as a 4th competing
criterion, and if adopted it should be adopted in that form.

---
