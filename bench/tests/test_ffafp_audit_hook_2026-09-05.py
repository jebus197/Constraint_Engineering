"""Guard for ~/.claude/hooks/ffafp_audit.py, the FFAFP trace detector. Written 2026-09-05.

WHAT IS BEING GUARDED, AND WHY IT NEEDS THIS SHAPE OF GUARD
===========================================================
The hook decides, from the tool-call record alone, whether the last work turn left the
traces FFAFP would have left. Almost every part of that decision is a pair of forms that
can disagree while each remains individually self-consistent:

  * a naive `>`-is-a-write detector and the filtered one that replaced it,
  * a pure-Python Wilson interval and the statsmodels and SciPy ones,
  * an order-blind "did a test run" check and the ordered "did a test run AFTER the edit",
  * a naive `type == "user"` turn splitter and the `origin.kind` one,
  * the hook's incremental scan and the `--survey` walk.

Under `execute-do-not-grep` (founder ruling, 2026-09-04) a test that asserted on the hook's
SOURCE TEXT could only prove the module describes itself consistently. So every test below
CALLS both forms and compares their outputs, and the ones that matter assert the two forms
DISAGREE on a case built for the purpose. A test that cannot distinguish the right answer
from the wrong one is not evidence -- this suite has already found 3 that passed with the
model replaced by the constant 42.

NO TEST HERE WRITES TO THE REAL STATE DIRECTORY. `FFAFP_AUDIT_STATE_DIR` redirects it into
tmp_path. On 2026-08-26 a test in this suite was found rewriting 3 canonical project files
on every run; that is the failure this precaution exists for, and `test_state_dir_override_
keeps_the_suite_out_of_the_real_state` checks the precaution itself works.
"""
from __future__ import annotations

import importlib.util
import json
import math
import os
import pathlib
import subprocess
import sys

import pytest

HOOK = pathlib.Path.home() / ".claude" / "hooks" / "ffafp_audit.py"
if not HOOK.is_file():
    pytest.skip(f"FFAFP trace-detector hook absent at {HOOK}; nothing to guard.",
                allow_module_level=True)

_spec = importlib.util.spec_from_file_location("ffafp_audit", HOOK)
fa = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fa)


# --------------------------------------------------------------------------------------
# Transcript fixtures, shaped like the real JSONL rather than like a convenient stub.
# --------------------------------------------------------------------------------------

def human(uuid: str, text: str = "go", ts: str = "2026-09-05T04:00:00.000Z") -> dict:
    return {"type": "user", "isSidechain": False, "origin": {"kind": "human"},
            "uuid": uuid, "timestamp": ts, "message": {"role": "user", "content": text}}


def assistant(*tools, uuid: str = "a-1") -> dict:
    blocks = [{"type": "tool_use", "id": f"toolu_{i}", "name": n, "input": inp}
              for i, (n, inp) in enumerate(tools)]
    return {"type": "assistant", "isSidechain": False, "uuid": uuid,
            "timestamp": "2026-09-05T04:00:01.000Z",
            "message": {"role": "assistant", "content": blocks}}


def tool_result(uuid: str = "r-1") -> dict:
    """A tool result. Note it also carries `type: "user"` -- that is the whole problem."""
    return {"type": "user", "isSidechain": False, "uuid": uuid,
            "timestamp": "2026-09-05T04:00:02.000Z",
            "message": {"role": "user",
                        "content": [{"type": "tool_result", "tool_use_id": "toolu_0",
                                     "content": "ok"}]}}


def write_transcript(path: pathlib.Path, entries) -> pathlib.Path:
    path.write_text("".join(json.dumps(e) + "\n" for e in entries))
    return path


def turn_of(*tools) -> dict:
    """Build a turn by CALLING the real accumulator, never by hand-assembling its dict."""
    t = fa.new_turn("turn-1", "2026-09-05T04:00:00.000Z")
    for name, inp in tools:
        fa.record_tool(t, name, inp)
    return t


BASH = "Bash"
EDIT_PY = ("Edit", {"file_path": "bench/immune_agents.py"})
READ_PY = ("Read", {"file_path": "bench/immune_agents.py"})
RUN_TESTS = (BASH, {"command": "python3 -m pytest bench/tests/test_x.py -q"})


# --------------------------------------------------------------------------------------
# 1. The arithmetic. Cross-verified against two independent implementations.
# --------------------------------------------------------------------------------------

def test_wilson_agrees_with_statsmodels_and_scipy_and_rejects_the_normal_approximation():
    """The hook carries its own Wilson interval so it needs no SciPy at hook time.

    A private re-implementation is only trustworthy if it is checked against the library
    ones, per the 2026-04-21 two-tool cross-verification rule. The last assertion is the
    discriminating half: the WRONG interval a hurried author reaches for -- the normal
    approximation -- is shown to differ by more than the tolerance, so this test would
    fail if `wilson` were quietly replaced by it.
    """
    sm = pytest.importorskip("statsmodels.stats.proportion")
    st = pytest.importorskip("scipy.stats")

    cases = [(37, 109), (27, 220), (24, 220), (68, 220), (1, 3), (0, 10), (10, 10)]
    for k, n in cases:
        _, lo, hi = fa.wilson(k, n)
        sm_lo, sm_hi = sm.proportion_confint(k, n, alpha=0.05, method="wilson")
        assert lo == pytest.approx(sm_lo, abs=1e-9), f"statsmodels disagrees at {k}/{n}"
        assert hi == pytest.approx(sm_hi, abs=1e-9), f"statsmodels disagrees at {k}/{n}"

        # Third tool: rebuild the interval from SciPy's own normal quantile.
        z = st.norm.ppf(0.975)
        p = k / n
        d = 1.0 + z * z / n
        centre = (p + z * z / (2 * n)) / d
        half = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
        assert lo == pytest.approx(max(0.0, centre - half), abs=1e-9)
        assert hi == pytest.approx(min(1.0, centre + half), abs=1e-9)

    # DISCRIMINATION, in two places, so this test can tell a correct Wilson interval from
    # the normal approximation an author in a hurry reaches for instead.
    z = 1.959963984540054

    # (a) On the headline figure the lower bounds differ by 0.0062, which is well outside
    #     any rounding: Wilson 25.7% against the approximation's 25.1%.
    k, n = 37, 109
    p = k / n
    naive_half = z * math.sqrt(p * (1 - p) / n)
    _, lo, hi = fa.wilson(k, n)
    assert abs(lo - (p - naive_half)) > 0.005

    # (b) And the reason the approximation is the wrong tool at all: at a zero count it
    #     collapses to zero width, claiming a proportion is known exactly from 10
    #     observations. Wilson keeps a real upper bound. A substituted implementation
    #     cannot pass both halves of this.
    _, zlo, zhi = fa.wilson(0, 10)
    assert (zlo, zhi) != (0.0, 0.0)
    assert zhi > 0.2
    naive_zero_width = 2 * z * math.sqrt(0.0 * 1.0 / 10)
    assert naive_zero_width == 0.0 and (zhi - zlo) > 0.2


def test_wilson_is_degenerate_only_where_it_should_be():
    assert fa.wilson(0, 0) == (0.0, 0.0, 0.0)
    _, lo, hi = fa.wilson(0, 20)
    assert lo == 0.0 and 0.0 < hi < 1.0            # a zero count still has an upper bound
    _, lo, hi = fa.wilson(20, 20)
    assert hi == 1.0 and 0.0 < lo < 1.0


# --------------------------------------------------------------------------------------
# 2. The mutation detector. Both live forms are CALLED and compared.
# --------------------------------------------------------------------------------------

NAIVE_CORPUS = [
    # Real shapes lifted from the surveyed transcripts, one per family of false positive.
    "grep -rn 'foo' bench/ >/dev/null 2>&1",
    "python3 - <<'PY'\nif x >= 0.05 and n >127:\n    print(f'{v:>6s}')\nPY",
    "echo \"a > the b\" && awk '{if ($1 > 0) print}' f.txt",
    "cat > bench/dm/_memory.py <<'EOF'\nx = 1\nEOF",
    "sed -i '' 's/a/b/' bench/immune_agents.py",
    "python3 run.py > /tmp/exp45.log 2>&1",
    "printf '%s\\n' hi >> experimental_notes/LEDGER.md",
]


def naive_mutations(cmd: str):
    """The detector that was built first and REJECTED: every `>` is a file write.

    Kept here as live code so the comparison below is between two things that both run,
    not between one that runs and a comment describing the other.
    """
    return [m.group("target") for m in fa._REDIRECT.finditer(cmd)]


def test_filtered_and_naive_mutation_detectors_disagree_on_real_shapes():
    """The filters must CHANGE the answer, or they are decoration.

    Measured over the full corpus by `--survey`: 90.8% of naive matches are not writes.
    Here the same disagreement is reproduced on 7 hand-picked real shapes so the test is
    self-contained and can fail if a filter is removed.
    """
    naive_total = sum(len(naive_mutations(c)) for c in NAIVE_CORPUS)
    filtered = [fa.bash_mutations(c) for c in NAIVE_CORPUS]
    filtered_total = sum(len(f) for f in filtered)
    assert naive_total > filtered_total, (
        "the naive detector matched no more than the filtered one, so the filters are "
        f"doing nothing: naive={naive_total} filtered={filtered_total}")

    flat = [p for f in filtered for p in f]
    # The three genuine writes survive.
    assert "bench/dm/_memory.py" in flat
    assert "experimental_notes/LEDGER.md" in flat
    assert "<in-place>" in flat                    # the `sed -i`, whose path is not parseable
    # And the noise does not.
    for junk in ("/dev/null", ">=", "0.05", "the", "{v:>6s}"):
        assert junk not in flat, f"{junk!r} was mistaken for a file write"


def test_heredoc_exclusion_is_load_bearing():
    """A `>` inside a heredoc body is Python or awk source, not a redirect.

    Measured: 4165 of 8688 naive matches, 47.9%, were inside heredoc bodies. This asserts
    the exclusion by running the detector with and against the heredoc span logic.
    """
    cmd = "python3 - <<'PY'\nif a >= b or c >0.05:\n    pass\nPY\necho done > bench/out.py"
    spans = fa.heredoc_spans(cmd)
    assert spans, "the heredoc body was not located at all"
    assert fa.bash_mutations(cmd) == ["bench/out.py"]
    # DISCRIMINATION: without the exclusion the same command yields extra matches.
    assert len(naive_mutations(cmd)) > 1


def test_stem_and_test_scanning_deliberately_include_heredoc_bodies():
    """The opposite rule, and it must be the opposite: `import sympy` in a heredoc body IS
    the evidence of the ANALYSE step. Excluding bodies there would make the signal blind to
    the project's own dominant way of running Python."""
    cmd = "python3 - <<'PY'\nimport sympy as sp\nprint(sp.simplify('x+x'))\nPY"
    sig = fa.bash_signals(cmd)
    assert "sympy" in sig["stem"]
    assert sig["mutations"] == []                  # and it is still not a file write


def test_a_grep_for_a_stem_name_is_not_a_stem_invocation():
    """Searching for the word `sympy` is a search, not an analysis. Without this the
    ANALYSE signal would credit the act of looking for it."""
    assert fa.bash_signals("grep -rn \"sympy\" bench/ | head")["stem"] == []
    assert fa.bash_signals("python3 -c 'import sympy; print(1)'")["stem"] == ["sympy"]


def test_a_quoted_pytest_is_a_search_not_a_test_run():
    assert fa.bash_signals("grep -rn 'pytest' docs/")["test"] is False
    assert fa.bash_signals("python3 -m pytest bench/tests -q")["test"] is True


def test_path_classification_separates_code_doc_and_transient():
    assert fa.classify_path("bench/immune_agents.py") == "code"
    assert fa.classify_path("experimental_notes/NOTE.md") == "doc"
    assert fa.classify_path("/tmp/exp45.log") == "transient"
    assert fa.classify_path("bench/logs/exp55.pid") == "transient"
    assert fa.classify_path("bench/cdsfl_registry/targets/exp51_biology") == "other"


# --------------------------------------------------------------------------------------
# 3. Turn segmentation. The naive splitter is run alongside and shown to be wrong.
# --------------------------------------------------------------------------------------

def test_human_prompt_discriminator_rejects_tool_results_meta_and_compaction():
    """Measured in one live slice: 460 tool-result entries against 31 real prompts, all
    carrying `type: "user"`. A splitter keyed on the type alone would cut the session into
    hundreds of one-tool fragments and every FFAFP verdict built on it would be noise."""
    entries = [
        human("u-1"),
        tool_result("r-1"),
        {"type": "user", "isSidechain": False, "origin": {"kind": "task-notification"},
         "uuid": "n-1", "message": {"role": "user", "content": "done"}},
        {"type": "user", "isSidechain": False, "isCompactSummary": True, "uuid": "c-1",
         "message": {"role": "user", "content": "summary"}},
        {"type": "user", "isSidechain": False, "isMeta": True, "uuid": "m-1",
         "message": {"role": "user", "content": "meta"}},
        {"type": "user", "isSidechain": True, "origin": {"kind": "human"}, "uuid": "s-1",
         "message": {"role": "user", "content": "subagent"}},
    ]
    verdicts = [fa.is_human_prompt(e) for e in entries]
    assert verdicts == [True, False, False, False, False, False]
    # DISCRIMINATION: the obvious wrong splitter accepts all 6.
    naive = [e.get("type") == "user" for e in entries]
    assert sum(naive) == 6 and sum(verdicts) == 1


# --------------------------------------------------------------------------------------
# 4. The verdict itself. Each pair differs by exactly the trace under test.
# --------------------------------------------------------------------------------------

def test_code_edit_with_no_check_afterwards_is_flagged_ppass():
    v = fa.audit(turn_of(READ_PY, EDIT_PY))
    assert v["is_work"] is True and v["code"] is True
    assert "P-PASS" in v["missing"]


def test_the_same_turn_with_a_trailing_test_is_silent():
    """Differs from the previous test by ONE tool call. If the detector ignored the check,
    both would be flagged; if it flagged nothing, neither would be."""
    v = fa.audit(turn_of(READ_PY, EDIT_PY, RUN_TESTS))
    assert v["missing"] == [], f"unexpected flags: {v['missing']}"
    assert fa.render(v, []) == ""


def test_a_check_run_BEFORE_the_edit_does_not_count_as_a_ppass():
    """P-pass means trying to break the fix. A suite run before the edit cannot have
    tested it. This is the ordering assertion, and it is what separates this detector from
    a naive 'did a test appear anywhere in the turn' check."""
    t = turn_of(RUN_TESTS, READ_PY, EDIT_PY)
    v = fa.audit(t)
    assert "P-PASS" in v["missing"]
    # DISCRIMINATION: the order-blind form would pass this turn.
    order_blind = bool(t["failable_idx"])
    assert order_blind is True and v["verified_after"] is False
    # ANALYSE is still satisfied -- a test DID run, it just ran too early to be a P-pass.
    assert "ANALYSE" not in v["missing"]


def test_follow_is_graded_none_generic_and_targeted():
    none_ = fa.audit(turn_of(EDIT_PY, RUN_TESTS))
    generic = fa.audit(turn_of(("Read", {"file_path": "docs/REPRODUCING.md"}), EDIT_PY, RUN_TESTS))
    targeted = fa.audit(turn_of(READ_PY, EDIT_PY, RUN_TESTS))
    assert none_["follow"] == "none" and "FOLLOW" in none_["missing"]
    assert generic["follow"] == "generic" and "FOLLOW" not in generic["missing"]
    assert targeted["follow"] == "targeted" and "FOLLOW" not in targeted["missing"]
    # The three are genuinely distinguished, not collapsed to one value.
    assert len({none_["follow"], generic["follow"], targeted["follow"]}) == 3


def test_a_grep_for_the_symbol_before_the_edit_counts_as_follow():
    t = turn_of((BASH, {"command": "grep -rn 'immune_agents' bench/ | head -20"}), EDIT_PY, RUN_TESTS)
    assert fa.audit(t)["follow"] == "targeted"


def test_a_read_in_an_earlier_turn_still_credits_follow():
    """FFAFP is a cycle over a task, not over a turn. Mapping the blast radius on one turn
    and editing on the next is correct practice; flagging it would be a false positive, and
    false positives are what get a hook switched off."""
    t = turn_of(EDIT_PY, RUN_TESTS)
    assert fa.audit(t, prior_reads=set())["follow"] == "none"
    assert fa.audit(t, prior_reads={"bench/immune_agents.py"})["follow"] == "targeted"


def test_a_documentation_only_turn_owes_no_test():
    v = fa.audit(turn_of(("Read", {"file_path": "experimental_notes/N.md"}),
                         ("Write", {"file_path": "experimental_notes/N.md"})))
    assert v["is_work"] is True and v["doc_only"] is True and v["code"] is False
    assert v["missing"] == []


def test_writing_only_to_tmp_is_not_a_work_turn():
    v = fa.audit(turn_of((BASH, {"command": "python3 run.py > /tmp/exp.log 2>&1"})))
    assert v["is_work"] is False and v["missing"] == []


def test_render_is_silent_on_a_clean_verdict_and_names_every_flag_otherwise():
    clean = fa.audit(turn_of(READ_PY, EDIT_PY, RUN_TESTS))
    dirty = fa.audit(turn_of(EDIT_PY))
    assert fa.render(clean, []) == ""
    msg = fa.render(dirty, [])
    assert msg and all(code in msg for code in dirty["missing"])
    assert "bench/immune_agents.py" in msg
    assert "MISSING TRACES" in msg, "the notice must not claim it proves rigour"


# --------------------------------------------------------------------------------------
# 5. End to end. The hook is EXECUTED as the harness would execute it.
# --------------------------------------------------------------------------------------

def run_hook(tmp_path: pathlib.Path, transcript: pathlib.Path, session: str = "sess-1",
             extra_env=None):
    payload = {"session_id": session, "transcript_path": str(transcript),
               "hook_event_name": "UserPromptSubmit", "prompt": "continue"}
    env = dict(os.environ)
    env["FFAFP_AUDIT_STATE_DIR"] = str(tmp_path / "state")
    env.update(extra_env or {})
    return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload),
                          capture_output=True, text=True, env=env, timeout=120)


def test_hook_end_to_end_reports_a_missing_ppass(tmp_path):
    tp = write_transcript(tmp_path / "t.jsonl", [
        human("u-1"),
        assistant(READ_PY, EDIT_PY),
        tool_result(),
    ])
    r = run_hook(tmp_path, tp)
    assert r.returncode == 0
    out = json.loads(r.stdout)
    ctx = out["hookSpecificOutput"]["additionalContext"]
    assert "P-PASS" in ctx and "bench/immune_agents.py" in ctx
    assert out["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"


def test_hook_end_to_end_is_silent_when_the_traces_are_there(tmp_path):
    """Same transcript plus the trailing suite run. Silence here is the discriminating
    result: a hook that always spoke would fail this, and one that never spoke would fail
    the previous test."""
    tp = write_transcript(tmp_path / "t.jsonl", [
        human("u-1"),
        assistant(READ_PY, EDIT_PY, RUN_TESTS),
        tool_result(),
    ])
    r = run_hook(tmp_path, tp)
    assert r.returncode == 0
    assert r.stdout.strip() == "", f"expected silence, got: {r.stdout[:300]}"


def test_hook_never_blocks_and_never_emits_a_decision(tmp_path):
    """REPORT, DO NOT BLOCK. A false block on correct work costs more than a missed
    reminder, and a blocking hook gets switched off within a day."""
    tp = write_transcript(tmp_path / "t.jsonl", [human("u-1"), assistant(EDIT_PY)])
    r = run_hook(tmp_path, tp)
    assert r.returncode == 0
    payload = json.loads(r.stdout)
    assert "decision" not in payload
    assert "decision" not in payload.get("hookSpecificOutput", {})
    assert payload.get("continue", True) is not False


@pytest.mark.parametrize("stdin_text", ["", "not json at all", "{}", '{"session_id": null}'])
def test_hook_exits_zero_on_garbage_input(tmp_path, stdin_text):
    env = dict(os.environ)
    env["FFAFP_AUDIT_STATE_DIR"] = str(tmp_path / "state")
    r = subprocess.run([sys.executable, str(HOOK)], input=stdin_text,
                       capture_output=True, text=True, env=env, timeout=120)
    assert r.returncode == 0, f"a hook that fails a prompt is worse than a missed notice: {r.stderr[:300]}"


def test_visible_flag_controls_suppression_only(tmp_path):
    tp = write_transcript(tmp_path / "t.jsonl", [human("u-1"), assistant(EDIT_PY)])
    quiet = json.loads(run_hook(tmp_path, tp, session="q").stdout)
    loud = json.loads(run_hook(tmp_path, tp, session="l",
                               extra_env={"FFAFP_AUDIT_VISIBLE": "1"}).stdout)
    assert quiet["suppressOutput"] is True
    assert loud["suppressOutput"] is False
    assert (quiet["hookSpecificOutput"]["additionalContext"]
            == loud["hookSpecificOutput"]["additionalContext"])


def test_second_run_reads_only_the_new_bytes_and_does_not_repeat_a_verdict(tmp_path):
    """The 45 MB transcript is why the offset exists. This proves both halves: the stored
    offset advances to end-of-file, and a turn already reported is not reported again."""
    tp = write_transcript(tmp_path / "t.jsonl", [human("u-1"), assistant(EDIT_PY)])
    first = run_hook(tmp_path, tp)
    assert "P-PASS" in first.stdout

    state_file = tmp_path / "state" / "sess-1"
    off1 = json.loads(state_file.read_text())["offset"]
    assert off1 == tp.stat().st_size, "the first pass did not reach end of file"

    with tp.open("a") as fh:
        fh.write(json.dumps(human("u-2", "next")) + "\n")
        fh.write(json.dumps(assistant(("Read", {"file_path": "docs/X.md"}))) + "\n")

    second = run_hook(tmp_path, tp)
    off2 = json.loads(state_file.read_text())["offset"]
    assert off2 > off1
    assert off2 == tp.stat().st_size
    assert second.stdout.strip() == "", "the same turn was reported twice"


def test_state_dir_override_keeps_the_suite_out_of_the_real_state(tmp_path):
    """The precaution the whole file depends on. If this fails, every other test here has
    been writing into ~/.claude/.ffafp_audit -- the 2026-08-26 defect, repeated."""
    session = "pytest-guard-session-2026-09-05"
    real = pathlib.Path.home() / ".claude" / ".ffafp_audit" / session
    assert not real.exists(), "stale artefact from an earlier run; the override was broken"
    tp = write_transcript(tmp_path / "t.jsonl", [human("u-1"), assistant(EDIT_PY)])
    run_hook(tmp_path, tp, session=session)
    assert (tmp_path / "state" / session).is_file(), "state was not written where told"
    assert not real.exists(), "the hook wrote into the real state directory"


# --------------------------------------------------------------------------------------
# 6. The survey, which is the script that reproduces the docstring's figures.
# --------------------------------------------------------------------------------------

def test_survey_and_the_hook_walk_the_same_loop(tmp_path):
    """A regression guard against re-duplicating the transcript walk.

    `survey()` originally had its own copy of the loop the hook uses. Two live forms of the
    same logic can agree with themselves and disagree with each other -- 4 defects in this
    project were found exactly that way. They were collapsed into one loop; this asserts a
    future author has not split them again, by driving each path over one transcript and
    comparing the work-turn counts they produce.
    """
    tp = write_transcript(tmp_path / "t.jsonl", [
        human("u-1"), assistant(READ_PY, EDIT_PY),
        human("u-2"), assistant(("Read", {"file_path": "docs/X.md"})),
        human("u-3"), assistant(("Write", {"file_path": "experimental_notes/N.md"})),
    ])
    st = fa.survey([str(tp)])

    verdicts = []
    state = {"offset": 0, "open": None, "seq": 0, "reads": {}}
    with tp.open() as fh:
        fa.scan(fh, state, on_close=verdicts.append)
    if state.get("open"):
        verdicts.append(fa.audit(state["open"], fa.prior_read_paths(state)))

    assert st["turns"] == len(verdicts) == 3
    assert st["work"] == sum(1 for v in verdicts if v["is_work"]) == 2
    assert st["code"] == 1 and st["doc_only"] == 1


def test_survey_signals_are_not_vacuous_on_the_real_corpus():
    """Reproduces the figures quoted in the hook's docstring, per
    `measured-rate-travels-with-its-script`.

    A signal that fires on every work turn, or on none, measures nothing while looking like
    a measurement. This project shipped `boundary_band_sensitivity` as an unconditional
    constant, vacuous in 41 of 41 archived reports, guarded by a test that read source text
    instead of calling the function. So the vacuity check is asserted, not merely printed.
    """
    root = pathlib.Path.home() / ".claude" / "projects" / "-Users-georgejackson-Developer-Projects"
    transcripts = sorted(str(p) for p in root.glob("*.jsonl")) if root.is_dir() else []
    if not transcripts:
        pytest.skip("no local transcripts on this machine; the rates cannot be recomputed here")

    st = fa.survey(transcripts)
    assert st["turns"] > 0 and st["work"] > 0 and st["code"] > 0

    for key, denom_key in (("follow_targeted", "work"), ("stem", "work"), ("test", "work"),
                           ("miss_ppass", "code")):
        denom = st[denom_key]
        assert 0 < st[key] < denom, (
            f"signal {key} is VACUOUS: {st[key]} of {denom}. A constant is not a detector.")

    # The naive redirect detector must still be visibly worse, on the real corpus and not
    # only on the 7 hand-picked shapes above.
    assert st["kept_redirects"] < st["naive_redirects"] / 2


def test_the_survey_and_the_detector_agree_on_every_redirect(tmp_path):
    """The unified `redirect_verdict`, checked by running both of its callers.

    Before this predicate existed the rule was written out twice and the copies disagreed:
    `--survey` rejected /dev/null and `bash_mutations` kept it. Both forms are executed
    here over the same commands and their counts compared, so a future re-divergence fails
    rather than hides.
    """
    cmds = NAIVE_CORPUS + [
        "python3 -m pytest bench/tests -q > /dev/null 2>&1",
        "cat > /dev/null <<'EOF'\nx\nEOF",
        "python3 - <<'PY'\nprint(1 > 0)\nPY\necho hi > bench/a.py",
    ]
    entries = [human("u-0")]
    for i, c in enumerate(cmds):
        entries.append(human(f"u-{i + 1}"))
        entries.append(assistant((BASH, {"command": c}), uuid=f"a-{i}"))
    tp = write_transcript(tmp_path / "t.jsonl", entries)

    st = fa.survey([str(tp)])
    direct = sum(len(fa.bash_mutations(c)) for c in cmds)
    inplace = sum(1 for c in cmds if "<in-place>" in fa.bash_mutations(c))
    # `kept_redirects` counts redirects only; `bash_mutations` also emits the sed -i marker.
    assert st["kept_redirects"] == direct - inplace
    assert st["rej_devnull"] > 0 and st["rej_heredoc"] > 0 and st["rej_shape"] > 0
    for c in cmds:
        assert "/dev/null" not in fa.bash_mutations(c)


def test_an_empty_redirect_target_is_a_quote_artefact_not_a_discard():
    """A number reported under the wrong label is not a measurement.

    `git commit -m "... <noreply@anthropic.com>"` contains a `>` whose apparent redirect
    target is a lone quote character. Measured 2026-09-05: 215 such matches in the surveyed
    corpus. An earlier draft counted every one of them in the `/dev/null` bucket -- the
    write/not-write verdict was right, so nothing downstream misbehaved and nothing failed,
    but `--survey` reported the wrong REASON to the founder. That is the defect class logged
    on 2026-08-30, a verdict counted with a label the code never emits.
    """
    commit = ('git commit -m "fix\\n\\nCo-Authored-By: Claude Opus 5 '
              '<noreply@anthropic.com>" && git log --oneline -2')
    bodies = fa.heredoc_spans(commit)
    verdicts = [fa.redirect_verdict(m.group("target"), m.start(), bodies)
                for m in fa._REDIRECT.finditer(commit)]
    assert verdicts, "no redirect-shaped match in a commit command that contains one"
    assert "devnull" not in verdicts, "a quote artefact was reported as a /dev/null discard"
    assert set(verdicts) == {"shape"}
    assert fa.bash_mutations(commit) == []

    # DISCRIMINATION: a real discard still lands in the /dev/null bucket, so the fix did
    # not simply empty that bucket.
    real = "grep -rn foo bench/ >/dev/null 2>&1"
    assert "devnull" in [fa.redirect_verdict(m.group("target"), m.start(), fa.heredoc_spans(real))
                         for m in fa._REDIRECT.finditer(real)]


def test_read_paths_are_deduplicated_and_capped_without_changing_a_verdict():
    """The state file is rewritten on every prompt, so an unbounded list in it is a leak.

    Measured 2026-09-05: the largest turn in the surveyed corpus serialised to 135443 bytes,
    with 1109 read_path entries of which most were duplicates. Deduplication is safe by
    construction -- FOLLOW is decided by a membership test -- and this asserts that safety by
    grading the SAME turn before and after the duplicates are collapsed.
    """
    t = fa.new_turn("t", "2026-09-05T00:00:00Z")
    for _ in range(50):
        fa.record_tool(t, "Bash", {"command": "grep -rn x bench/immune_agents.py"})
    fa.record_tool(t, "Edit", {"file_path": "bench/immune_agents.py"})
    assert len(t["read_paths"]) < 50, "duplicate read paths were not collapsed"
    assert "bench/immune_agents.py" in t["read_paths"]
    assert fa.audit(t)["follow"] == "targeted", "dedup changed the FOLLOW verdict"

    big = fa.new_turn("b", "2026-09-05T00:00:00Z")
    for i in range(fa.SEARCH_CAP + 200):
        fa.record_tool(big, "Read", {"file_path": f"bench/mod_{i}.py"})
    assert len(big["searches"]) == fa.SEARCH_CAP
    assert len(big["read_paths"]) <= fa.READ_PATH_CAP
    # DISCRIMINATION: the caps bind only above the observed maximum of 242 searches, so a
    # normal turn is untouched by them.
    assert fa.SEARCH_CAP > 242 and fa.READ_PATH_CAP > 242
