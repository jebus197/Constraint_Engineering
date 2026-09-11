# Two jobs. Supply FIXES, not findings.

Disposable COPY of the repo. ONE-SHOT dispatch — see your system prompt. Write your
findings as you go; a partial answer with evidence beats a holding note.

Do NOT run the full suite (8+ minutes). Targeted tests only.

---

## JOB 1 — fix the five items blocking an honest PoC release

A previous round concluded: the CLAIMS survive the known defects, but the EVIDENCE
PACKAGING is not release-ready. Verified since: `passes_threshold` and `R_new` have
zero production readers, so the S* defect cannot have manufactured a convergence;
and round-0 escalation fails by HALTING, which is the safe direction.

The five items, with what was measured:

1. **Unpushed work.** 15 commits on `main` are not on `origin`. A stranger cannot
   fetch the current state at all.
2. **No declared Python floor.** No `setup.py`, `pyproject.toml`, `setup.cfg` or
   `requirements.txt`. Codex already hit exactly this: 3 of 524 modules fail to
   parse on 3.11.2, and 14 test files import one of them, so collection cannot
   start. The repo runs on 3.13.3 only, by accident.
3. **6 of 245 test files reach into `$HOME` with no skip guard** (2.4%, Wilson
   [1.1%, 5.2%]) — `_private_memory.py`, `test_acceptance_gate_repairs_2026-08-23.py`,
   `test_falsifier_cannot_read_the_key.py`, `test_key_access_forensics.py`,
   `test_sv_rulings.py` and one more. They fail on a clean checkout regardless of
   any defect in the method.
4. **The convergence count does not survive deduplication.** "25 archived runs"
   was asserted; deduplicating report files by content hash gives **24 distinct
   events, 9 simulated, 15 live**. `exp36_evidence_latest` is byte-identical to
   `exp36_evidence_20260407T004931Z`. Decide the defensible number and where it
   should be stated so it cannot drift again.
5. **Two different denominators for one quantity sit in the runner.** Line 10602
   says `s_star` reads 0.0 in "3181 of 3181"; lines 10775/10781 say "3816". Today's
   measurement: 3181 of 3181. The tracker and a morning report also carry 3816.

**For each: supply the fix.** Patches, not descriptions. Say what you ran. If an
item needs no fix, say so in one line. Item 4 and 5 are about numbers that a
stranger falsifies by counting — treat them as seriously as a code defect.

---

## JOB 2 — can the FFAFP protocol be mechanically enforced?

The founder's diagnosis, and I think it is correct: CC1 performs FIND and P-PASS
well and performs **FOLLOW** and **ANALYSE** thinly, so the P-pass keeps catching
what FOLLOW should have caught. Live instances from the last 24 hours:

* called `sk_break_even(R, q, nu_b, nu_f)` against a signature of
  `(nu_b, nu_f, q, R)` — never checked the signature; the fix was inert and read
  as done;
* wrote a deferral in `_apply_routing` without tracing that the flag also feeds
  the alarm — it silenced 3 of 6 archived alarms;
* wrote a guard reading `sk_result` without checking a structural guard forbids
  exactly that;
* wrote a test asserting on source text between parens — comments satisfied it.

**The finding that matters:** `~/.claude/hooks/ffafp_audit.py` EXISTS — 38,421
bytes, executable, dated 2026-09-05 — and is **NOT WIRED** in
`~/.claude/settings.json`, where `prompt_clock`, `mc_commands` and
`compaction_watch` all are. The FFAFP enforcement hook is itself an addition
connected to nothing.

**Answer these:**

(a) Read that hook. What does it actually check? Does it enforce FOLLOW, or only
    observe? Would wiring it have caught any of the four instances above?

(b) If it would not, what WOULD? Be concrete and mechanical. The obvious candidate:
    an edit to a target must be preceded, in the same turn, by evidence that the
    target's callers and dependents were enumerated. Is that enforceable from a
    tool-call stream? What is the false-positive cost?

(c) Judge it against the project's own **simplest sufficient** standard: before
    building a mechanism, state what goes wrong without it and check whether a
    cheaper existing property already prevents that. Is there already something
    that would do this job?

**Supply the fix**, including the settings.json wiring if you conclude it should be
wired. Say plainly if you think it should NOT be.
