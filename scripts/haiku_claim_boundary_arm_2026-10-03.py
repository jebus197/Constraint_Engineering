#!/usr/bin/env python3
"""The MODEL ARM: can a cheap classifier draw the decidable-claim boundary?

THE FOUNDER'S QUESTION, verbatim, 2026-09-30: "we previously did measure our
classifier agent (Haiku) and in general found it to be very reliable? Would
composing both approaches present any meaningful improvement over any single
one?"

WHY THIS ARM CANNOT BE SKIPPED. `scripts/claim_classifier_labelled_set_2026-10-01.py`
measured 2 arms on the same 15 documents and the composition scores 15 of 15 --
but its claim arm locates claims by ANCHORS taken from the corpus's own claim
lists, i.e. the answer key, and returns False on any document the corpus does
not describe. That 15 of 15 is a lookup's score. Composing a syntax gate with a
lookup cannot answer whether a cheap MODEL finds claims in an unseen document.

WHAT IS AT STAKE IN THE STATUS QUO, measured by that script and re-checked here:
the syntax arm scores 5 of 10 on sensitivity, which a binomial test cannot
distinguish from a coin (p = 1.000000), and 0 of 5 on the prose variants
(p = 0.0625). It is not an unreliable claim detector; it is a FENCE-SYNTAX
detector being read as one, and the prose documents lack fences by construction.

THE LABELS ARE NEVER SHOWN TO THE MODEL. The documents and the key live in
separate files by construction, and this script asserts that no label content
reaches a prompt before any dispatch happens. A leak here would reproduce the
exact defect the lookup arm already has.

A FAILED DISPATCH IS NOT A WRONG ANSWER. Every non-answer is counted and
reported separately, never folded into the error count -- a silent zero in the
denominator is a defect class this project has shipped before.

COST: 15 dispatches through the claude CLI on the founder's Max subscription,
serialised. That is subscription model time, not API spend.

Cross-verification: every proportion carries a Wilson interval from statsmodels
and an independent mpmath closed form; every comparison between arms is a
McNemar exact test from scipy cross-checked against an mpmath binomial sum.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import re
import shutil
import subprocess
import sys

for _cand in (pathlib.Path(__file__).resolve().parent,
              *pathlib.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
SET_SCRIPT = ROOT / "scripts" / "claim_classifier_labelled_set_2026-10-01.py"

QUESTION = (
    "Does this document contain at least 1 claim that computation could "
    "settle? A claim computation could settle is one a program, a calculation, "
    "a unit check or a test could decide as true or false. Preferences, "
    "aesthetics, intentions and descriptions of process are not such claims.\n\n"
    "Answer on the FIRST line with exactly YES or NO. If YES, name the claim on "
    "the second line.\n\nDOCUMENT:\n")


def _load_set_module():
    spec = importlib.util.spec_from_file_location("clset", SET_SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["clset"] = m
    spec.loader.exec_module(m)
    return m


def wilson(k: int, n: int):
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    if n == 0:
        return None
    lo, hi = proportion_confint(k, n, method="wilson")
    mp.mp.dps = 40
    z = mp.mpf("1.959963984540054235524594430520551527955")
    p, d = mp.mpf(k) / n, 1 + z ** 2 / n
    c = p + z ** 2 / (2 * n)
    h = z * mp.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2))
    return lo, hi, float((c - h) / d), float((c + h) / d)


def show(label: str, k: int, n: int) -> None:
    w = wilson(k, n)
    if w is None:
        print(f"    {label:14s} {k}/{n} — no denominator")
        return
    agree = abs(w[0] - w[2]) < 1e-12 and abs(w[1] - w[3]) < 1e-12
    print(f"    {label:14s} {k}/{n} = {100*k/n:8.4f}%  "
          f"Wilson [{100*w[0]:7.4f}%, {100*w[1]:7.4f}%]  agree={agree}")


def mcnemar(b: int, c: int):
    """Exact McNemar on the discordant pairs, scipy against an mpmath sum."""
    from scipy.stats import binomtest
    import mpmath as mp
    n = b + c
    if n == 0:
        return 1.0, 1.0
    p_scipy = binomtest(b, n, 0.5).pvalue
    mp.mp.dps = 40
    obs = mp.binomial(n, b) * mp.mpf("0.5") ** n
    tot = mp.mpf(0)
    for k in range(n + 1):
        pk = mp.binomial(n, k) * mp.mpf("0.5") ** n
        if pk <= obs * (1 + mp.mpf("1e-30")):
            tot += pk
    return float(p_scipy), float(tot)


def dispatch(cli: str, doc_text: str, model: str, timeout: int) -> tuple[str, str]:
    """Return (verdict, raw). verdict is 'YES', 'NO' or 'NO-ANSWER'."""
    prompt = QUESTION + doc_text
    try:
        r = subprocess.run(
            [cli, "-p", prompt, "--model", model,
             "--output-format", "text", "--max-turns", "1"],
            capture_output=True, text=True, timeout=timeout)
    except subprocess.SubprocessError as exc:
        return "NO-ANSWER", f"{type(exc).__name__}: {exc}"
    raw = (r.stdout or "").strip()
    if r.returncode != 0 and not raw:
        return "NO-ANSWER", f"exit {r.returncode}: {(r.stderr or '')[:200]}"
    first = next((ln.strip() for ln in raw.splitlines() if ln.strip()), "")
    if re.match(r"^\**\s*YES\b", first, re.I):
        return "YES", raw
    if re.match(r"^\**\s*NO\b", first, re.I):
        return "NO", raw
    if re.search(r"\bYES\b", raw[:200], re.I):
        return "YES", raw
    if re.search(r"\bNO\b", raw[:200], re.I):
        return "NO", raw
    return "NO-ANSWER", raw


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--set-dir", required=True,
                    help="directory written by claim_classifier_labelled_set --emit-model-set")
    ap.add_argument("--model", default="haiku", help="claude CLI model alias")
    ap.add_argument("--timeout", type=int, default=90)
    ap.add_argument("--out", help="write the raw replies and scores here as JSON")
    ap.add_argument("--from-results", metavar="FILE",
                    help="re-score saved replies instead of dispatching again; "
                         "the model answers are data, so a scoring repair must "
                         "not cost a second round of model time")
    a = ap.parse_args(argv)

    setdir = pathlib.Path(a.set_dir)
    raw_labels = json.loads((setdir / "LABELS_WITHHELD.json").read_text())
    # THE LABEL IS A FIELD, NOT THE TRUTHINESS OF THE RECORD. The first version
    # of this script read `bool(labels[name])` and every entry is a non-empty
    # dict, so all 15 documents scored as POSITIVE and the 5 negatives vanished:
    # specificity had no denominator and the model's 3 correct refusals were
    # counted as misses. Caught by the anti-vacuity assertion below, which did
    # not exist when the arm first ran.
    labels = {k: bool(v["has_decidable_claim"]) if isinstance(v, dict) else bool(v)
              for k, v in raw_labels.items()}
    assert len(set(labels.values())) == 2, (
        f"the label set has only one class ({set(labels.values())}); "
        f"specificity or sensitivity would have no denominator and the arm "
        f"would score a constant answer as perfect")
    docs = {p.stem: p.read_text(encoding="utf-8")
            for p in sorted((setdir / "documents").glob("*.md"))}
    assert set(docs) == set(labels), (
        f"documents and labels disagree: {sorted(set(docs) ^ set(labels))}")

    # THE LEAK CHECK, BEFORE ANY DISPATCH. No label value may appear in a prompt.
    key_blob = json.dumps(raw_labels)
    for name, text in docs.items():
        assert key_blob not in (QUESTION + text), "the key reached a prompt"
    assert "LABELS_WITHHELD" not in QUESTION
    print(f"LEAK CHECK PASSED: {len(docs)} prompts carry no label content.\n")

    if a.from_results:
        saved = json.loads(pathlib.Path(a.from_results).read_text())
        rows = [{"doc": r["doc"], "truth": labels[r["doc"]],
                 "model": r["model"], "raw": r.get("raw", "")}
                for r in saved["rows"]]
        print(f"RE-SCORED from {a.from_results}: {len(rows)} saved replies, "
              f"0 new dispatches.\n")
        for r in rows:
            mark = "?" if r["model"] == "NO-ANSWER" else (
                "ok" if (r["model"] == "YES") == r["truth"] else "MISS")
            print(f"  {r['doc']:22s} truth={'YES' if r['truth'] else 'NO ':3s} "
                  f"model={r['model']:10s} {mark}")
        return _score_and_report(rows, docs, a)

    cli = shutil.which("claude")
    if not cli:
        print("claude CLI not found on PATH; the model arm cannot run.",
              file=sys.stderr)
        return 2

    rows = []
    for i, (name, text) in enumerate(sorted(docs.items()), 1):
        verdict, raw = dispatch(cli, text, a.model, a.timeout)
        truth = labels[name]
        rows.append({"doc": name, "truth": truth, "model": verdict,
                     "raw": raw[:1200]})
        mark = "?" if verdict == "NO-ANSWER" else (
            "ok" if (verdict == "YES") == truth else "MISS")
        print(f"  [{i:2d}/{len(docs)}] {name:22s} truth={'YES' if truth else 'NO ':3s} "
              f"model={verdict:10s} {mark}")

    return _score_and_report(rows, docs, a)


def _score_and_report(rows, docs, a) -> int:
    answered = [r for r in rows if r["model"] != "NO-ANSWER"]
    noans = len(rows) - len(answered)
    print(f"\nDISPATCHES: {len(rows)}; answered {len(answered)}; "
          f"NO-ANSWER {noans} (counted separately, never as errors)")
    if not answered:
        print("no answers; nothing can be scored.")
        return 1

    def sc(pred):
        tp = sum(1 for r in answered if r["truth"] and pred(r))
        fn = sum(1 for r in answered if r["truth"] and not pred(r))
        fp = sum(1 for r in answered if not r["truth"] and pred(r))
        tn = sum(1 for r in answered if not r["truth"] and not pred(r))
        return tp, fn, fp, tn

    clset = _load_set_module()
    syn = {}
    for name, text in docs.items():
        syn[name] = bool(clset._syntax_arm(text, name))

    arms = {
        "MODEL (haiku)": lambda r: r["model"] == "YES",
        "SYNTAX (status quo)": lambda r: syn[r["doc"]],
        "COMPOSED or": lambda r: r["model"] == "YES" or syn[r["doc"]],
        "COMPOSED and": lambda r: r["model"] == "YES" and syn[r["doc"]],
    }
    results = {}
    for label, pred in arms.items():
        tp, fn, fp, tn = sc(pred)
        n = tp + fn + fp + tn
        print(f"\n{label}")
        show("accuracy", tp + tn, n)
        show("sensitivity", tp, tp + fn)
        show("specificity", tn, tn + fp)
        print(f"    tp={tp} fn={fn} fp={fp} tn={tn}")
        results[label] = {"tp": tp, "fn": fn, "fp": fp, "tn": tn,
                          "correct": tp + tn, "n": n}

    print("\nTHE COMPOSABILITY STANDARD, APPLIED (founder, 2026-10-02):")
    print("  compose ONLY where the composition demonstrably beats EACH arm")
    print("  alone; where a single arm performs as well, prefer the single arm.")
    model_c = results["MODEL (haiku)"]["correct"]
    syn_c = results["SYNTAX (status quo)"]["correct"]
    best_single = max(model_c, syn_c)
    for comp in ("COMPOSED or", "COMPOSED and"):
        cc = results[comp]["correct"]
        b = sum(1 for r in answered
                if arms[comp](r) == r["truth"] and not (
                    (model_c >= syn_c and arms["MODEL (haiku)"](r) == r["truth"])
                    if model_c >= syn_c else
                    (arms["SYNTAX (status quo)"](r) == r["truth"])))
        c_ = sum(1 for r in answered
                 if arms[comp](r) != r["truth"] and (
                    (arms["MODEL (haiku)"](r) == r["truth"]) if model_c >= syn_c
                    else (arms["SYNTAX (status quo)"](r) == r["truth"])))
        p_s, p_m = mcnemar(b, c_)
        verdict = ("JUSTIFIED" if cc > best_single and p_s < 0.05
                   else "NOT JUSTIFIED")
        print(f"  {comp:14s} correct {cc}/{results[comp]['n']} vs best single "
              f"{best_single}: discordant {b}/{c_}, McNemar scipy p = {p_s:.6f}, "
              f"mpmath p = {p_m:.6f} -> {verdict}")

    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(
            {"rows": rows, "results": results, "no_answer": noans,
             "model": a.model}, indent=2))
        print(f"\nwrote {a.out}")
    return 0


if __name__ == "__main__":
    # This script HAS its own parser, so the helper answers --help and then
    # stands aside rather than refusing the script's own flags; see
    # scripts/_cli_help.py, `takes_no_arguments`.
    answer_help(__doc__, __file__, takes_no_arguments=False)
    raise SystemExit(main())
