# Is this instrument good enough for a formal PoC release? And what would stop it?

You are a reviewing seat on a CDSFL panel. You are working in a WRITABLE COPY of
the repository; your cwd is that copy. Bash, Read, Grep and Glob are available.
**Run things.** The standing rule `execute-do-not-grep` holds that a check
asserting on source text proves only that the source describes itself
consistently; it cannot detect a producer and a consumer that disagree.

## The question, in the founder's own framing

The founder asks whether CDSFL "does what it says on the tin to a sufficient
standard to demonstrate the main principles of the project in a way that would be
appropriate for a formal PoC release" — and whether "the simplest sufficient
solution would be to allow others with probably far greater access to compute
resources than me" to take it further, rather than continuing to polish it alone
on a Mac Mini with 8 GB of RAM.

CDSFL is intended to be a **STEM calculator, not a problem generator**: a
bounded question in, a defensible answer out, with the reasoning traceable. For
much of its life it behaved as the latter. The founder's position is that no
problem space should be treated as inexhaustible, and that terminating on
*exhaustion of findings* is not the same thing as compelled agreement.

## What you are and are not being asked for

**You are asked for SHOW-STOPPERS.** A show-stopper is a defect that would make a
formal PoC release misleading, unreproducible, or unsafe to publish — not merely
an imperfection. If you find none, say so plainly and say what you checked; a
clean verdict backed by evidence is as useful as a refutation and will be treated
that way.

**You are not asked to find more problems for their own sake.** An LLM told to
"find problems in this codebase" will find problems, with near certainty, whether
or not they matter. Resist that. Rank ruthlessly by consequence.

**Termination criterion.** Stop when your own passes stop producing new
above-threshold findings — the schema's §10, Sufficiency Assessment and
Convergence Declaration, is the standard. Do not stop merely because you agree
with another seat, and do not manufacture disagreement either. Independent
verdicts; common stop rule.

## A provenance note, and what it does NOT license

Most of the fixes shipped in the last 24 hours came from panel seats — from you,
or from a sibling seat — or from CC1 acting on seat findings. **This is stated so
you are not reviewing blind. It is not evidence that any of it is correct.**
Authorship by a reviewer is not a warrant. On 2026-09-07 a seat proposed a
"transcription error" explanation for a number, CC1 adopted it without testing
it, and the seat itself later refuted its own theory by measurement — the
measurement settled what neither position had. Treat your own prior findings with
exactly the suspicion you would apply to CC1's.

## What changed in the last 24 hours

- **Severity became a calculation** with enforced worked proofs, replacing a
  grader that could not read across a newline and was failing models for showing
  the arithmetic the directive orders them to show.
- **The panel's tool-call counter was 0 by construction** for every Claude-route
  seat on every panel ever run here — `tool_log` was reassigned on 1 of 3 route
  branches. Fixed; this dispatch is the second to record real counts.
- **A rejected attempt's tool calls were erased** by the retry that replaced them.
  Fixed to accumulate, with a per-attempt breakdown.
- **The operator's control plane was outside every watch** — a sandboxed seat
  wrote to the real `~/.claude/settings.json`. 143 files now fingerprinted around
  each panel. Detection, not prevention, deliberately.
- **The scoring-key vault**: five "top-level, not recursive" defects, one of which
  (`chmod 600 "$STORE"/*` stripping the execute bit from subdirectories) made
  every unseal-reseal cycle fail. 53 keys are now sealed and hash-verified.
- **This panel now runs under the formal CDSFL schema** for the first time. It had
  a hand-written prompt; 0 of 37 dispatchers had ever composed or loaded the
  schema document.
- A checker CC1 wrote **could never fail on the defect class it was built for** —
  at k=n the Wilson lower bound rises with n, so every upward correction was
  auto-forgiven. Found by a seat, repaired.

## Your task

1. **Assess PoC readiness.** Does the instrument demonstrate its principles well
   enough for a formal release? Judge against `simplicity` and `sufficiency` as
   this project uses them, not against a general standard of polish. Name what
   you ran.
2. **Name any show-stoppers**, ranked by consequence, each with the evidence you
   executed and a specific proposed fix.
3. **Assess one specific item.** Seven exam answer keys (exp48–exp53) are
   recoverable from this repository's public git history; they were removed from
   the working tree on 2026-07-29 and the commit message recorded "Residual for
   founder ruling: git-history recovery by deliberate archaeology". The 27 Bench
   Run 2 keys were never committed. Is this a release blocker, and what are the
   real options with their costs?
4. **Answer the compute question.** Is "let others with more resources take it
   further" the simplest sufficient path, or is something still missing that only
   the founder can supply?

## Output

For each: VERDICT, the commands you ran and their real output, and a specific
fix for anything defective. Quote real output, not summaries of it. Disagreement
is information — do not smooth toward the framing above, which is CC1's and has
been wrong repeatedly this week.
