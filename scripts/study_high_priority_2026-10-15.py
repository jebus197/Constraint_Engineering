#!/usr/bin/env python3
"""Add the 2026-10-15 high-priority items to the programme of study.

Founder's instruction, 2026-10-15: *"Make sure you mark these items as high
priority considerations in the accompanying/outstanding program of study"*
(PROGRAMME, per his own spelling ruling of 2026-10-05: programme for a study).
"""
import json, pathlib, subprocess, sys

REPO = pathlib.Path(__file__).resolve().parents[1]
P = REPO / "experimental_notes" / "STUDY_IN_FLIGHT.json"


def _now() -> str:
    """The clock is CAPTURED, never typed (`read-the-clock`), and capturing it is
    an ACTION -- so it happens inside a function and not at import."""
    return subprocess.run(["date", "-Iseconds"],
                          capture_output=True, text=True).stdout.strip()


def _entries(NOW: str):
    """The measurements and defects to add, as pure data. Takes the stamp so
    nothing here reads a clock or touches the tree."""

    NEW_MEASUREMENTS = [
    {
        "id": "directive_delivery",
        "priority": "HIGH",
        "added": NOW,
        "what": ("Does delivering the project's own specification WHOLE change what the "
                 "panel detects and how it converges? Before 2026-10-15 every model "
                 "received a 2,503-character reduced form of the 27,803-character core "
                 "specification, carrying 0 of its 22 HARD blocks verbatim. It now "
                 "receives all 27,803 characters."),
        "founder_ruling": ("APPLY THE FIX THEN MEASURE IT (2026-10-15). His reasoning, "
                           "2026-10-14: \"7000 or so words for a system prompt is hardly "
                           "excessive for any modern model? Why should we need to cut it at "
                           "all?\" and \"as far as any caps have ever existed, their "
                           "intention was to never feed any model more work than they were "
                           "demonstrably able to handle ... There was never an intent as far "
                           "as I recall to applying this same reasoning to the core "
                           "operational directives themselves.\""),
        "this_is_the_caps_question_he_asked_to_have_measured": True,
        "baseline": {
            "spec_chars_delivered_before": 2503,
            "spec_chars_delivered_after": 27803,
            "hard_blocks_carried_before": "0 of 22, 0.0000%, Wilson [0.0000%, 14.8655%]",
            "hard_blocks_carried_after": "22 of 22, 100.0000%, Wilson [85.1345%, 100.0000%]",
            "system_prompt_chars_before": 48877,
            "system_prompt_chars_after": 74177,
            "producer": "scripts/the_spec_is_not_work_2026-10-15.py",
        },
        "what_it_can_and_cannot_say": (
            "2 free runs compare 2 runs, so they cannot establish a rate. They CAN show "
            "whether findings per round, rounds to convergence, HIL referrals and the "
            "irreducible queue move, and whether any seat degrades on the longer prompt."),
        "result": None,
        "headline": None,
    },
    {
        "id": "severity_promotion",
        "priority": "HIGH",
        "added": NOW,
        "what": ("Promote the severity specification shadow from record-only to DECIDING, "
                 "and measure whether it distorts convergence. This is the 2nd free run's "
                 "subject, deliberately separated from the directive repair so each is "
                 "attributable."),
        "founder_ruling": ("DO NOT RUN A SHADOW IN A SIMULATION (2026-10-15). His words, "
                           "2026-10-14: \"why run them in shadow in a simulated run, when "
                           "the purpose of a simulated run is to test how they will behave "
                           "in a real experiment and to fix any deficiencies/issues you "
                           "encounter so that we don't run into those same issues in a paid "
                           "run, and risk pointlessly burning money we don't have?\""),
        "why_it_needed_a_build_not_a_flag": (
            "Measured 2026-10-15: of the 10 mechanisms listed in the programme revision, 6 "
            "are LIVE, 1 is a record by design, 1 is a measurement, and 2 are genuine "
            "record-only shadows -- 2 of 10, 20.0000%, Wilson [5.6682%, 50.9838%]. NEITHER "
            "of the 2 had a flag that makes it gate, so promoting them is a build. And "
            "their own promotion criterion asks for non-distortion evidence \"from a run\", "
            "which a shadow can never supply because a shadow never decides. That circle "
            "is what his question exposed."),
        "result": None,
        "headline": None,
    },
    {
        "id": "coherence_budget_recalibration",
        "priority": "HIGH",
        "added": NOW,
        "what": ("Re-derive MODEL_COHERENCE_BUDGETS from the 2 free runs' logs via "
                 "`update_coherence_budgets_from_experiments`. The budgets are STALE BY "
                 "CONSTRUCTION after the directive repair and the coherence pruner's "
                 "ablation arm is inert until they are re-derived."),
        "founder_ruling": "not yet put to him; the measurement is the precondition",
        "why": ("`constraint_density = constraint_count / (len(rendered) // 4)` has the "
                "rendered length in its DENOMINATOR while `constraint_count` is derived "
                "from the merged TOML policy and does NOT grow with the specification. "
                "Delivering the specification whole multiplies the rendered length by about "
                "5.7, so density fell below every budget. Measured 2026-10-15: 0 of 50 real "
                "compositions over budget, 0.0000%, Wilson [0.0000%, 7.1348%], "
                "Clopper-Pearson [0.0000%, 7.1122%]; max density 0.002835 against a "
                "smallest budget of 0.010, 3.5277 times below it."),
        "the_named_loss": ("The lean-versus-full comparison the 2026-07-18 pruning review "
                           "gates every cut on CANNOT BE RUN until this is closed. The "
                           "mechanism's REACHABILITY is still pinned by "
                           "bench/tests/test_composer_pruning_ablation_switch_2026-10-13.py "
                           "with a budget supplied explicitly."),
        "explicitly_not_done": ("The budgets were NOT hand-retuned. A hand-set cap with no "
                                "measurement behind it is precisely what the founder "
                                "objected to on 2026-10-13 and 2026-10-14."),
        "producer": "scripts/the_spec_is_not_work_2026-10-15.py",
        "result": None,
        "headline": None,
    },
]

    NEW_DEFECTS = [
    {
        "id": "concise-style-deduplicates-the-code-under-review",
        "priority": "HIGH",
        "at": NOW,
        "severity": "the situation packet's code extracts are collapsed for 4 of 5 models",
        "status": "FOUND 2026-10-15, NOT FIXED — recorded honestly per his instruction",
        "what": ("`_apply_phenotype_transform` with `format_style=\"concise\"` runs the "
                 "semantic-duplicate dedup over the SITUATION packet, which carries the "
                 "review target, the code extracts and the adversarial brief. Measured "
                 "2026-10-15 on a 1,492-character situation packet holding 20 repeated "
                 "function definitions: opus_4_6 (style \"full\") receives 1,491 "
                 "characters; chatgpt_5_4, codex_5_3, deepseek_v3 and gemini_3_1_pro (all "
                 "\"concise\") receive 339 -- the repeats collapsed to 1 and every line "
                 "stripped of indentation. 4 of 5 models, 80.0000%, Wilson [37.5535%, "
                 "96.3776%]."),
        "why_it_is_bounded": ("The code under review ALSO reaches the model through the "
                              "user prompt, which `_build_prompt` builds from `full_code`, "
                              "so a model is not reviewing nothing. The situation packet is "
                              "supplementary context. The harm is that 2 genuinely "
                              "different functions with similar token sets can be collapsed "
                              "into 1, and indentation -- which is syntax in Python -- is "
                              "destroyed."),
        "why_not_fixed_tonight": ("Dedup-over-code is a design change to the phenotype "
                                  "layer, it is not in the causal path of either free run's "
                                  "hypothesis, and 3 large changes in one night with no "
                                  "measurement between them is how a confound becomes "
                                  "unattributable."),
        "pre_existing": ("Not introduced by the 2026-10-15 repair. `format_style=\"concise\"` "
                         "predates it for chatgpt_5_4, codex_5_3 and gemini_3_1_pro."),
        "needs": "a founder ruling: should the phenotype layer dedup the code under review at all?",
    },
    {
        "id": "proven-floor-used-as-a-ceiling-in-the-decomposition-decision",
        "priority": "HIGH",
        "at": NOW,
        "severity": "a seat's observed capacity can never rise",
        "status": "FOUND 2026-10-15, NOT FIXED — a futility guard was added instead",
        "what": ("`_should_decompose` step 2 reads `max_successful_prompt_chars` and "
                 "returns `payload_chars > observed * 0.9`. Its own docstring calls that "
                 "figure a PROVEN FLOOR -- \"The model has PROVEN it can handle at least "
                 "that much input\" -- and the code uses it as a CEILING. A seat that has "
                 "only ever been sent 72,934 characters can never be sent more, so the "
                 "observed maximum never rises: a ratchet that cannot climb, structurally "
                 "the same defect as the routing ladder's."),
        "what_it_cost_tonight": ("With the specification delivered whole the system prompt "
                                 "is 74,177 characters, and 6 of 6 simulated seats "
                                 "(100.0000%, Wilson [60.9666%, 100.0000%], "
                                 "Clopper-Pearson [54.0742%, 100.0000%]) have an effective "
                                 "limit below that: CC2-SIM 72,465, ChatGPT-SIM 65,640, "
                                 "Codex-SIM 70,922, DeepSeek-SIM 72,465, Fable-SIM 69,775, "
                                 "Gemini-SIM 67,510. Every simulated dispatch would have "
                                 "force-decomposed on the size of its own instructions. NO "
                                 "PAID SEAT WOULD HAVE -- CC2 sits at 418,685 and DeepSeek "
                                 "at 99,068 -- so this is a confound that fires only in "
                                 "simulation, which is the exact hazard he named."),
        "what_was_done_instead": ("A futility guard: when the NON-DECOMPOSABLE part of the "
                                  "payload already exceeds the effective limit, "
                                  "decomposition is dominated on per-request bytes, total "
                                  "bytes and request count, so the monolithic dispatch is "
                                  "sent and the transport is allowed to speak. Proof: SymPy "
                                  "`S*n > 0`, z3 `unsat` on all 3 negations, mpmath on the "
                                  "concrete case. An explicit `pre_decompose_models` "
                                  "override is honoured over the futility argument."),
        "needs": ("a founder ruling: should the observed maximum be allowed to rise, and by "
                  "what rule? Changing it alters routing for PAID seats."),
    },
    {
        "id": "cross-layer-soft-deletion-on-a-spurious-topic-match",
        "priority": "HIGH",
        "at": NOW,
        "severity": "an engineering requirement a model is then never told",
        "status": ("RETIRED FROM THE DEFAULT PATH 2026-10-15 and retained behind "
                   "`CONFLICT_DELETES_SOFT_LOSER`, the same treatment the directive pruner "
                   "got on his 2026-10-13 ruling"),
        "what": ("`_directive_topic_and_stance` assigns topic `table` to any text "
                 "containing the word \"table\" or a pipe-delimited row, so the core "
                 "specification's FORMALISATION TABLE was recorded as conflicting with "
                 "`product_automotive`'s \"Material specification per OEM standard (VW TL, "
                 "BMW GS, GM GMW, Ford WSS-M)\" and deleted it. The 2 texts are about "
                 "different things."),
        "measured": ("With the specification delivered whole, over 10 domains: 42 conflicts "
                     "before the repair, of which 40 were the specification against ITSELF "
                     "(95.2381%, Wilson [84.2101%, 98.6842%]), 0 same-layer and 2 "
                     "cross-layer; 41 of the 42 deletions had a HARD loser by the resolver's own HARD predicate, 40 of them blocks of the specification itself (an earlier reading of 11 is WITHDRAWN: it tested a 100-character truncated field that carries no packet class). After: 2 conflicts "
                     "recorded, 0 HARD deletions, 0 blocks lost."),
        "what_is_given_up": ("A model may now receive 2 directives a cruder reading calls "
                             "contradictory. Whether that costs anything is what the free "
                             "runs answer."),
        "needs": "measurement in the free runs, then his ruling on whether to re-enable deletion",
    },
]

    return NEW_MEASUREMENTS, NEW_DEFECTS


def main() -> int:
    NOW = _now()
    NEW_MEASUREMENTS, NEW_DEFECTS = _entries(NOW)
    d = json.loads(P.read_text(encoding="utf-8"))
    existing_m = {m["id"] for m in d["measurements"]}
    existing_d = {x.get("id") for x in d["open_defects"]}
    added_m = [m for m in NEW_MEASUREMENTS if m["id"] not in existing_m]
    added_d = [x for x in NEW_DEFECTS if x["id"] not in existing_d]
    d["measurements"].extend(added_m)
    d["open_defects"].extend(added_d)

    d["high_priority_2026_10_15"] = {
        "added": NOW,
        "founder_instruction": ("\"Apply any outstanding fixes you have identified first, "
                                "including any as yet unbuilt/unapplied machinery, before you "
                                "begin the runs. Make sure you mark these items as high "
                                "priority considerations in the accompanying/outstanding "
                                "program of study\" — 2026-10-15"),
        "measurements": [m["id"] for m in NEW_MEASUREMENTS],
        "defects": [x["id"] for x in NEW_DEFECTS],
        "runs": {
            "run_1": "directive_delivery — the specification delivered whole, severity shadow UNCHANGED",
            "run_2": "severity_promotion — the severity specification promoted to deciding",
            "why_2_and_not_1": ("Promoting the severity specification alters what counts as "
                                "critical, which alters convergence. Running it alongside the "
                                "directive repair makes neither attributable, which is the same "
                                "error the programme already rejects for per-fix attribution. "
                                "2 free runs cost nothing."),
        },
        "replay_cost_accepted_by_him": ("\"We cannot go back and change time, so the confounds "
                                         "discovered in the last 24 hours can only be noted and "
                                         "added to the record honestly.\" Delivering the "
                                         "specification whole changes every dispatch and "
                                         "invalidates replay against the 81 archived runs. That "
                                         "is the cost C0040 was parked for and he has now paid "
                                         "it knowingly."),
    }

    d["run_conditions"]["protocol"] = (
        "full cy: scripts/cy_watchdog_2026-10-02.py polls at 60 s and speaks only on an "
        "event; a Monitor arming turns each line into a wake-up; a tail terminal runs on the "
        "founder's own machine via scripts/local/open_run_tail.sh"
    )

    P.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    json.loads(P.read_text(encoding="utf-8"))
    print(f"added {len(added_m)} measurement(s): {[m['id'] for m in added_m]}")
    print(f"added {len(added_d)} defect(s): {[x['id'] for x in added_d]}")
    print(f"measurements now {len(d['measurements'])}, open_defects now {len(d['open_defects'])}")
    print(f"stamped {NOW}")
    return 0


def _answer_help_without_acting(doc: str) -> None:
    """★ THIS SCRIPT WRITES, SO `--help` MUST NOT RUN IT. Guarded by
    `bench/tests/test_help_never_acts_2026-09-11.py`, which found 2 real defects
    in the first version of this file: it ignored `--help` and did its ordinary
    work, and it WROTE AT IMPORT -- its body was top level, so any tool that
    merely inspected it rewrote `STUDY_IN_FLIGHT.json`. Both are now closed by
    construction: every write is inside `main()`, and `main()` runs only under
    the name guard below.
    """
    import argparse
    ap = argparse.ArgumentParser(
        prog=pathlib.Path(__file__).name,
        description=(doc or "").strip().splitlines()[0] if doc else None,
        epilog=("Takes no arguments. It is IDEMPOTENT: an id already present in "
                "STUDY_IN_FLIGHT.json is not added twice, so re-running it is "
                "safe and is how the programme's state and the record of why it "
                "changed are kept from drifting apart."),
    )
    ap.parse_args()


if __name__ == "__main__":
    _answer_help_without_acting(__doc__)
    raise SystemExit(main())
