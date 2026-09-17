# Panel review: an unratified rule withdrawn, a control commissioned, and a figure corrected

**Single-shot.** No follow-up round. Do not reply with a holding note. If you run
out of time, report what you established and label the rest unchecked.

**Suite baseline so you need not run it:** `python3 -m pytest bench/tests -q`
gives **4,780 passed, 0 failed** at commit `295c72c`, about 6 minutes.

Everything below is committed. `git log --oneline -3` to orient.

**Standing context you should know:** an earlier review in this series (you, on
2026-09-01) refuted a claim of mine by pointing out I had counted a
violation-gated key while its unconditional sibling sat one line below. That
correction was right and is now in the code. Please be at least that hard here.

---

## 1. A rule was withdrawn because it was never a rule

`severity_demotion_notice()` in `bench/reference_runner_v3.py` used to emit
`barred_when_simulated: [... "convergence verdicts as evidence" ...]`.

Provenance, and this is the part to check: the runway raised it as
**"Panel-converged, both reviewers | HIGH — needs a standing ruling"**
(commit `b8a2a05`). Commit `bb8d54b`, the same day, then opens
**"STANDING RULING (0C.12), panel-converged 2026-09-01"**. No HIL approval
happened in between. The founder, asked about it, said he could not remember
approving it — and the record says he did not.

The founder has now ruled: *"remove that clause that prevents you from reporting
when that is the case. It seems to serve no purpose other than to confuse you and
me."*

**Verify or refute:**
- Is the provenance chain as described? Check `b8a2a05` and `bb8d54b` yourself.
- Is what survives correctly scoped? The notice now says magnitudes are
  uncalibrated and do not transfer, and that readiness reporting is PERMITTED.
  Is there anything in that wording which still smuggles in a bar?
- **Is this a case of a model vote becoming a rule?** If you think the promotion
  was legitimate, say so and say why.

## 2. The age control took three attempts to commission

`bench/tests/test_latent_control_audit_2026-09-01.py`.

- v1 asserted "something is currently TOO_NEW". It went red when the canary run
  moved the baseline — a test meant to prove the control works, failing because
  the control worked.
- v2 asserted the invariant (`TOO_NEW iff first_committed > newest`). A mutation
  test refuted it: setting `too_new = False` outright left all nine green,
  because the invariant is vacuous when nothing is new. Same shape as the S_k
  skip-guard failure this project already had.
- v3 gives `audit()` an injectable baseline (`--as-of`). Pinned to 07:19:13 on
  2026-09-01, the three keys committed later that day must quarantine.

**Verify or refute:** run the mutations yourself. Does v3 actually have teeth, or
have I just moved the vacuity somewhere new? Try to find a mutation of the age
control that v3 still passes.

## 3. Seat identity is now keyed on (model_id, api)

The founder recalled the Codex and ChatGPT seats once being differentiated. They
were, and it was route-based: Codex via `codex exec` carrying OpenAI's own hidden
agent prompt, ChatGPT bare via OpenRouter with CDSFL as system message.

Measured: pre-lapse 78 paired rounds, 356 vs 479 findings, sign test
**p = 0.00515**; post-lapse 205 paired rounds, 270 vs 251, **p = 0.378**. It
lapsed 2026-04-02 in `556e0af`.

**Verify or refute:** reproduce those two sign tests. Is the pairing sound — are
"paired rounds" really paired, same round same target? Is a sign test the right
instrument here, or does the count data want something else? And is
`f"{model_id}@{api}"` the right identity key, or does it now over-separate
(e.g. a primary/secondary failover changing `api` mid-run and splitting one seat
into two voices)?

## 4. A figure I published was wrong

0C.22 published **21/103 = 20.4%**. The denominator double-counted: each run's
registry appears in both its report and its `runner_state.json`, and one run
directory is a symlink to another. Deduplicated over 46 run directories:
**11/47 = 23.4%, Wilson [13.6%, 37.2%]**.

**Verify or refute:** reproduce both numbers. Is 46 the right population? Are
there other duplication paths I have not found (resumed runs, partial writes,
per-round snapshots)?

## 5. The vacuity prediction was refuted by its own run

Runway 0C.28 asserted a simulated run *cannot* converge non-vacuously "by
construction", because the critical arm needs severity >= 0.70 and simulated
severity clusters near 0.46.

The canary run converged at round 3, `gamma_critical=1.000 >= 0.3`, zero
occurrences of VACUOUS, **12 of 22 findings at severity >= 0.70** (54.5%, Wilson
[34.7%, 73.1%]). The explanation offered: the prediction held the target
constant, and seeding genuinely severe defects makes the panel rate them
severely.

**Verify or refute:** is that explanation right? Or did something else change
between the two runs that better accounts for it — the blinding change, the
history severing, the seat-identity change, or the target simply being different?
This matters: if severity moved for a reason other than the plants, the
detection result below is confounded.

---

## The questions that matter more than the verifications

**Q1. Two of five seeded defects were missed by all six seats.** They are
`compute_source_hash` losing its `sorted()` (order-dependent hash), and
`provenance_complete` using `>=` instead of `==` (excess ids read as complete).
Both are in the `calibration` split, so neither affects the reported `p_hat` —
which flatters the headline.

Is that miss the models' fault, the harness author's fault, or unavoidable given
the kill criterion (a falsifier that fires on the seeded text and stays quiet on
the clean one)? **Try to write a killing falsifier for each yourself.** You know
the ground truth, so if you cannot, no blind reviewer could.

**Q2. Is this runner fit to take into a real experiment?** No real run has ever
used a v3.x runner — 0 of 20 archived real reports carry one. What would you
check before spending real money that has not been checked?

**Q3. What did I get wrong in this batch that nobody has caught yet?** You found
the `target_hashes` sibling last time. Find the equivalent here.
