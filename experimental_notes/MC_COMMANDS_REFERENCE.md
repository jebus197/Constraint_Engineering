CDSFL METACOGNITIVE COMMAND REFERENCE

Canonical sources: docs/REPRODUCING.md section "Metacognitive Commands", the
global CLAUDE.md, and the enforcing hook at ~/.claude/hooks/mc_commands.py.
Where they disagree, the hook is what actually runs.

Commands are typed as plain text in the conversation and combine freely, for
example "a, f, sy, d, t". Every command in a sequence runs in full and in order.


THE ONE THAT IS MOST OFTEN MISREMEMBERED

f is FFAFP, not FFFAP, and the order matters.

  FIND     identify the issue, with evidence
  FOLLOW   trace the consequences BEFORE touching anything: what depends on
           this, what interfaces it crosses, what breaks downstream. Map the
           blast radius.
  ANALYSE  gather evidence with tools. The tool output IS the evidence.
  FIX      the simplest sufficient correction to the root cause AND the
           downstream consequences found in Follow.
  P-PASS   actively try to break the fix. A fix you have not tried to break is
           a hypothesis, not a fix.

Analyse comes BEFORE Fix. Reversing them means fixing on a hunch and then
gathering evidence to justify what you already did. Follow comes before Fix for
the same reason: Find without Follow produces shallow patches, and Fix without
Follow produces regressions.


CORE COMMANDS

y      yes, approved.
cy     continue, AND monitor any running experiment at roughly 60 second
       cadence. Pause on anything odd, apply the full FFAFP cycle to it, fix,
       resume. Always keep a terminal open showing the running output.
d      discuss before proceeding. Do not start implementing.
p      P-pass. Try to disprove the conclusion before presenting it. Iterative,
       not observational: identify, fix, falsify, repeat to diminishing returns.
a      analyse dispassionately. Evidence over agreement. If the record
       contradicts the founder's framing, say so with citations.
e      extrapolate beyond the immediate domain. What generalises, what the
       boundary conditions are, and what new falsifiable questions follow.
f      FFAFP, the five step cycle above. All five steps, every time.
sy     use the mathematical and STEM tools: SymPy, Wolfram, SciPy, NumPy, z3,
       uncertainties, mpmath. Prose reasoning does not satisfy this. Every
       computational claim needs at least two independent tools, and every
       proportion needs a confidence interval.
t      produce the artefact pair: a plain text file for text to speech in the
       project's Desktop folder, and a markdown mirror in experimental_notes.
c      confer with Codex through the command line interface and run mutual
       P-passes until convergence or diminishing returns.
sv     save state. Read the canonical documents sequentially, update ONBOARDING
       and RECOVERY, capture an Open Brain session summary, commit.
qc     quality control. Sweep related documentation for staleness before
       committing.
rc     recover state. Same as rs.
rs     restore state in full. Rebuild the working context from scratch using the
       operational tracker, RECOVERY, ONBOARDING, the memory index and any other
       critical state files. Supersedes the older rr.
re     external research: web search, arXiv, Semantic Scholar.
ext    external research, the same as re, shorter to type.
rt     read all recovery resources, then continue.
r      re-read the key context files.
x      override the rest period warnings for this session.
sth    synthesise. Consolidate the findings into one coherent statement.
rg     regain full context on a named topic. Re-read the anchoring memory files,
       canonical documents and experimental notes END TO END, with no summary
       and no truncation, then name what was consulted.
sq     sequential. Strictly one tool call at a time, no parallel batches, to
       avoid stressing the servers during long autonomous runs. Sub-agents
       inherit the same constraint.
ag     use agents to parallelise genuinely independent work.
pr     panel review. Dispatch the full model panel on a completed analysis or
       design question, under sy, sth, f, e, d and t. Run WITHOUT compelled
       convergence, so each model returns an independent verdict and its
       strongest falsification. Disagreement is preserved as information rather
       than smoothed into consensus. Mirror the result to a text to speech file.


CONFERRING WITH A SPECIFIC MODEL

These direct a confer on the current task with one named model. They combine,
so "cx ge cc2" confers with all three.

cc2    Claude Opus 4.7, through the command line in piped mode, on the Max
       subscription. Free. Never routed through OpenRouter.
cx     Codex GPT-5.5, through OpenRouter. Paid.
ge     Gemini 3.1 Pro Preview, through OpenRouter. Paid.
cgpt   ChatGPT GPT-5.5, through OpenRouter. Paid.
ds     DeepSeek V4 Pro, through the DeepSeek direct interface. Paid.

A note on panel composition that is easy to miss. The cx and cgpt seats both
resolve to the same underlying model on OpenRouter, so counting seat labels
counts one model twice. A three model panel of CC1, CC2 and Fable costs nothing,
because all three run on the Max subscription.


TWO STANDING CONSTRAINTS THAT APPLY WHETHER OR NOT THE LETTERS ARE TYPED

f applies to all substantive work. sy applies to anything computable. These are
hard constraints, issued 30 August 2026, and the hook injects both on every
turn regardless of what was typed.


THREE RULES ADDED 4 SEPTEMBER 2026

Numbers are always written as digits, never as words, in every context without
exception.

A measured rate, proportion or count may only be cited if the script that
produced it is committed alongside it. A number that exists only as prose is a
claim about evidence, not evidence.

A test that asserts on the source text of a module proves only that the module
describes itself consistently. Where both forms exist as live code, the test
must call them and compare outputs.
