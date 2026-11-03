# Agent contract standards: what the founder's two named standards turn out to be, and what this project already implements

3 November 2026, 06:50 GMT

## Summary

The founder asked about 2 standards by name, Meta-Agent Architectures and the Model-Agent Interface, and said a derived version had once been discussed for inclusion in the model core directives, adding that he did not know whether it had ever been done.

It was not done. There are **0 genuine references** to either name anywhere in the repository, the directive files, the documentation, the experimental notes, the resources, or his own annotated replies. The 3 apparent matches found by search are coincidental word adjacencies: "model/agent run", "every model and every agent", and "model agents work in isolation". So the derived standard never reached the core directives, which answers the question he said he could not answer himself.

Neither name exists as a published specification under those exact titles. The formal construction that does the work he is pointing at is **assume-guarantee contracts**, set out in arXiv 2608.14590, where each agent declares the inputs it assumes and the outputs it guarantees, so that a composition can be checked rather than hoped for. The adjacent industrial pattern is the thin orchestrator, in which a deterministic supervisor performs classification, gathering, reliability checks and delegation only, and holds no domain judgement of its own.

## What this project already implements, measured

Of the 5 elements of the practical pattern, **5 of 5** are already present.

1. A typed task schema. The ticket store's fields carry it: `kind`, `task_ref`, `subjects`, `anchor`.
2. Typed result statuses, 9 of them, with 2214 CLOSED, 456 MERGED, 336 UNCONFIRMED and 83 OPEN at the time of measurement.
3. A terminal state that cannot be asserted. `TicketStore.close()` refuses without a verification, so a closure records a result rather than a claim.
4. No model voting. Findings are confirmed programmatically or by the human in the loop.
5. Evidence attached to every marker.

A first run of this measurement reported 4 of 5 and was wrong. The predicate tested `by_status()` for truthiness, and that function returns an empty list by design, so a correctly implemented element read as absent. The error was in the instrument, not in the code it measured, which is the dominant failure shape of this session.

## What is genuinely missing

Only the **declaration**. The project behaves as though its components had assume-guarantee contracts without any component stating one, so a contract cannot be checked, composed or reverted.

Where such a declaration should live is the founder's decision, not a repair to be applied unasked.

## What was done with that finding the same morning

The actuator built on 3 November is the first component in the project to carry an explicit declaration, and it carries it as data rather than as prose: `ASSUMES` holds 4 assumptions and `GUARANTEES` holds 5, both as module-level dictionaries in `bench/tools/cy_actuator_2026-11-03.py`.

The declaration has 2 consumers, which is what keeps it from being decorative. The guard `bench/tests/test_the_actuator_holds_its_contract_2026-11-03.py` iterates `GUARANTEES` and fails if a guarantee is declared with no test class naming it, so the declaration cannot drift ahead of what is held. And `--contract` prints both dictionaries, which costs nothing and dispatches nothing.

The actuator is **a single component** and not a project-wide standard, so it must not be reported as a standard of the project. Whether the pattern should be generalised to the rest of the harness remains the founder's decision.

## The boundary of this finding

What is established is that the 2 names appear nowhere in the project's own record, and that the 5 practical elements are implemented. What is **not** established is that assume-guarantee contracts are the standard the founder had in mind. He has said the names are external references and that the record need not be searched further, so the identification rests on the formal literature matching the function he described, not on a recovered project document. If he recognises a different construction, this note's identification is the part that should be discarded, and the measurement of the 5 elements stands independently of it.

Equally, nothing here measures whether declaring contracts across the harness would catch a defect that the current arrangement misses. That is a composability claim in the founder's strong sense, it requires a committed measurement showing the composed arrangement beats either part alone, and no such measurement exists. The actuator is 1 instance, which is evidence that the declaration is cheap to write and nothing more.

Written under CDSFL note standard v1.9 (1 November 2026).
