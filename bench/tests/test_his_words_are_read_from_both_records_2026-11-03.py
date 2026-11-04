"""His mid-turn words must be readable, and the union must never SHRINK.

WHY THIS FILE EXISTS. On 2026-11-03 an instrument written that same day to check
whether a compaction summary had INVENTED a question of his reported that the
term `v_bar` appears 0 times in 1,719 of his typed messages, and concluded the
summary made it up. He asked it directly at 2026-11-03T03:56:55, typed while a
turn was running. The harness stores such a message on an entry of type
`queue-operation` with the text in a TOP-LEVEL `content` key, no `message` dict
and no `promptSource`, so no instrument here could see it. 206 of his 1,421
distinct messages live only in that record: 0.144968, Wilson 95%
[0.127620, 0.164231].

THE PROPERTY THIS GUARD DEFENDS IS DIRECTIONAL, AND THAT IS DELIBERATE. A reader
that merely CHANGED its answer would be indistinguishable from one that broke,
so the assertion is that the union is a SUPERSET of what the old narrow scan
returns. Something can be added; nothing may be lost. The decisive case is named
rather than counted -- `test_his_v_bar_question_is_found` -- because a count
cannot say WHICH message went missing, and a swap of one for another leaves a
count unchanged.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
READER = REPO / "scripts" / "his_messages.py"
WRONGED = REPO / "scripts" / "a_compaction_summary_can_invent_his_question_2026-11-03.py"

#: The message whose absence from the corpus produced a false claim about him.
#: Named, with its timestamp, so the regression is specific.
V_BAR_TS = "2026-11-03T03:56:55"
V_BAR_OPENING = "What is v-bar? I have never heard of it before?"


@pytest.fixture(scope="module")
def hm():
    spec = importlib.util.spec_from_file_location("_hm", READER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def narrow_scan():
    """What the OLD predicate returned: `type: "user"` entries only.

    Written out here rather than imported, because the thing it models no longer
    exists in the reader. It is the baseline the union must dominate.
    """
    root = pathlib.Path.home() / ".claude/projects/-Users-georgejackson-Developer-Projects"
    if not root.is_dir():
        return None
    out = set()
    for p in sorted(root.glob("*.jsonl")):
        with p.open(errors="ignore") as fh:
            for raw in fh:
                if '"type":"user"' not in raw and '"type": "user"' not in raw:
                    continue
                try:
                    e = json.loads(raw)
                except Exception:                            # noqa: BLE001
                    continue
                if e.get("type") != "user" or e.get("toolUseResult") is not None:
                    continue
                if e.get("isMeta"):
                    continue
                msg = e.get("message") or {}
                c = msg.get("content")
                t = c if isinstance(c, str) else " ".join(
                    b.get("text", "") for b in (c or [])
                    if isinstance(b, dict) and b.get("type") == "text")
                if isinstance(t, str) and t.strip():
                    out.add(" ".join(t.split())[:300])
    return out


# --------------------------------------------------- THE DIRECTIONAL PROPERTY

@pytest.mark.skipif(not (pathlib.Path.home()
                         / ".claude/projects/-Users-georgejackson-Developer-Projects"
                         ).is_dir(), reason="transcripts absent on this machine")
def test_the_union_is_a_superset_of_the_narrow_scan(hm, narrow_scan):
    """THE ASSERTION THAT MATTERS. Nothing the old scan saw may be lost."""
    if narrow_scan is None:
        pytest.skip("transcripts absent")
    union = {" ".join(m.text.split())[:300] for m in hm.distinct()}
    # The narrow scan has no exclusions, so subtract the shapes the reader
    # names as not-his before comparing. Each is a NAMED reason, so this is not
    # a loophole: a message dropped for an unnamed reason still fails below.
    expected = {k for k in narrow_scan if not hm.why_not_his(k)}
    lost = sorted(expected - union)
    assert not lost, (
        f"{len(lost)} message(s) the old narrow scan returned are missing from "
        f"the union, so the reader LOST something instead of adding: "
        f"{[m[:80] for m in lost[:3]]}")


@pytest.mark.skipif(not (pathlib.Path.home()
                         / ".claude/projects/-Users-georgejackson-Developer-Projects"
                         ).is_dir(), reason="transcripts absent on this machine")
def test_the_union_is_strictly_larger_so_the_reader_is_not_vacuous(hm, narrow_scan):
    """ANTI-VACUITY. A union equal to the narrow scan would pass the superset
    test while reading nothing new, which is the whole point of the repair."""
    if narrow_scan is None:
        pytest.skip("transcripts absent")
    union = {" ".join(m.text.split())[:300] for m in hm.distinct()}
    gained = union - narrow_scan
    assert gained, (
        "the union returns nothing the narrow scan did not, so the queue record "
        "is not being read and this reader is decoration")
    assert len(gained) >= 100, (
        f"only {len(gained)} message(s) gained; 206 were measured on "
        f"2026-11-03. A large fall means the queue branch has narrowed.")


# ------------------------------------------- THE DECISIVE CASE, NAMED NOT COUNTED

@pytest.mark.skipif(not (pathlib.Path.home()
                         / ".claude/projects/-Users-georgejackson-Developer-Projects"
                         ).is_dir(), reason="transcripts absent on this machine")
def test_his_v_bar_question_is_found(hm):
    """The exact message whose absence produced a false claim about him."""
    hits = hm.mentions(re.compile(r"(?<![A-Za-z0-9])v[-_ ]?bars?\b", re.I))
    assert hits, (
        "his v-bar question is not being read. That message is why this reader "
        "exists: without it the project told him he had never asked something "
        "he asked at 03:56 on the 3rd of November.")
    assert any(h.ts.startswith(V_BAR_TS) for h in hits), (
        f"a v-bar message was found but not the one at {V_BAR_TS}: "
        f"{[h.ts for h in hits]}")
    one = next(h for h in hits if h.ts.startswith(V_BAR_TS))
    assert one.text.lstrip().startswith(V_BAR_OPENING), (
        f"the message at {V_BAR_TS} does not open as recorded: "
        f"{one.text[:90]!r}")
    assert one.record == "queued", (
        f"it is now coming from the {one.record!r} record. If the harness has "
        f"started writing mid-turn messages to the ordinary record, re-measure "
        f"the 206 before trusting any figure that rests on it.")


@pytest.mark.skipif(not (pathlib.Path.home()
                         / ".claude/projects/-Users-georgejackson-Developer-Projects"
                         ).is_dir(), reason="transcripts absent on this machine")
def test_the_producer_that_was_wrong_now_answers_correctly(hm):
    """EXECUTED, not read. The instrument whose verdict this repair inverted."""
    r = subprocess.run([sys.executable, str(WRONGED)], capture_output=True,
                       text=True, timeout=300, cwd=str(REPO))
    assert r.returncode == 0, f"it exited {r.returncode}\n{r.stderr[-700:]}"
    assert "HE DID WRITE IT" in r.stdout, (
        "the producer has gone back to reporting that the question was a "
        "summary artefact. It was his.")
    assert "of 1421" in r.stdout.replace(",", ""), (
        "the denominator is no longer the count of DISTINCT messages of his. A "
        "raw row count double-counts every mid-turn message and admits the task "
        "notifications the harness queues to itself, which inflates it in the "
        "flattering direction.")


# ------------------------------------------------------ THE READER'S OWN RULES

def test_only_enqueue_is_read_from_the_queue(hm):
    """`dequeue` and `remove` are the harness moving ONE message in and out.

    Reading all 3 operations would count him 3 times. Measured over the corpus:
    3,740 enqueue against 2,018 dequeue and 1,721 remove.
    """
    src = READER.read_text()
    assert 'operation") != "enqueue"' in src or 'operation") == "enqueue"' in src, (
        "the reader no longer restricts itself to the enqueue operation")


def test_every_exclusion_carries_a_named_reason(hm):
    """An exclusion without a name is one nobody can object to."""
    assert hm.NOT_HIS_WRITING, "the exclusion table is empty; this is vacuous"
    for reason, pred in hm.NOT_HIS_WRITING:
        assert isinstance(reason, str) and reason.strip(), (
            "an exclusion carries no reason")
        assert callable(pred), f"the {reason!r} exclusion is not callable"


def test_the_exclusions_actually_discriminate(hm):
    """EXECUTED both ways. A predicate that matched everything, or nothing,
    would pass a source-text check and destroy the corpus."""
    assert hm.why_not_his("<task-notification>\nsomething") == "task notification"
    assert hm.why_not_his("cy HEARTBEAT (mechanical)") == "cy heartbeat"
    assert hm.why_not_his("Stop hook feedback: [x]") == "stop hook echo"
    # And a real message of his must survive every one of them.
    assert hm.why_not_his(
        "What is v-bar? I have never heard of it before?") is None, (
        "an exclusion is eating his actual words")
    assert hm.why_not_his("rs first.") is None


def test_distinct_prefers_the_prompt_record(hm, tmp_path):
    """A message present in BOTH records must be returned once, from the
    canonical record, because the prompt copy carries the fields other
    instruments expect."""
    t = tmp_path / "x.jsonl"
    text = "a sentence of his that appears in both records"
    rows = [
        {"type": "queue-operation", "operation": "enqueue",
         "timestamp": "2026-11-03T10:00:00Z", "content": text},
        {"type": "user", "timestamp": "2026-11-03T10:00:01Z",
         "message": {"role": "user", "content": text}},
    ]
    t.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    got = hm.distinct(tmp_path)
    assert len(got) == 1, f"expected 1 distinct message, got {len(got)}"
    assert got[0].record == "prompt", (
        f"the {got[0].record!r} copy won; the prompt copy is canonical")


def test_a_queued_only_message_survives(hm, tmp_path):
    """The 206 case, in miniature and under control."""
    t = tmp_path / "x.jsonl"
    t.write_text(json.dumps(
        {"type": "queue-operation", "operation": "enqueue",
         "timestamp": "2026-11-03T03:56:55Z",
         "content": "What is v-bar? I have never heard of it before?"}) + "\n")
    got = hm.distinct(tmp_path)
    assert len(got) == 1 and got[0].record == "queued"
    assert hm.mentions("v-bar", tmp_path), "mentions() cannot see a queued-only message"


def test_the_bookkeeping_operations_are_not_counted(hm, tmp_path):
    """dequeue and remove carry the same text and must contribute nothing."""
    t = tmp_path / "x.jsonl"
    text = "one message, three bookkeeping rows"
    rows = [
        {"type": "queue-operation", "operation": "enqueue",
         "timestamp": "2026-11-03T10:00:00Z", "content": text},
        {"type": "queue-operation", "operation": "dequeue",
         "timestamp": "2026-11-03T10:00:01Z", "content": text},
        {"type": "queue-operation", "operation": "remove",
         "timestamp": "2026-11-03T10:00:02Z", "content": text},
    ]
    t.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    assert len(list(hm.iter_messages(tmp_path))) == 1, (
        "the bookkeeping operations are being counted, so he is tripled")


def test_help_answers_without_doing_the_work():
    """His standing rule: a `--help` must never cost money or minutes."""
    r = subprocess.run([sys.executable, str(READER), "--help"],
                       capture_output=True, text=True, timeout=60,
                       cwd=str(REPO))
    assert r.returncode == 0
    assert "usage:" in (r.stdout + r.stderr).lower()


def test_the_reader_is_reached_by_a_caller(hm):
    """ADDITIVE STANDARD. A reader nothing imports is an unwired addition, the
    shape this project has confirmed 11 times."""
    callers = [p for p in (REPO / "scripts").glob("*.py")
               if p.name != "his_messages.py"
               and "his_messages" in p.read_text(errors="ignore")]
    assert callers, (
        "no script imports his_messages.py, so the repair reaches nothing and "
        "is the addition-nothing-reaches half of the additive standard")
