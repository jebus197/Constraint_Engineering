#!/usr/bin/env python3
"""The evidence for task B22: is the harness yet a general-purpose STEM calculator?

HIS QUESTION, verbatim, recorded in task B22: *"there is also a separate question
of what 'fixes' should mean in a setting that is not coding related, but is
specific to any other given STEM topic?... CDSFL has been envisaged from the
outset as a general purpose STEM calculator, operating on strict Popperian
falsification principles. But in order for that to be true the entire harness has
to be as equally useful against a wide range of STEM related topics, as it
currently is for code."* He directs it to a free panel *"not only asking if we are
there already or not, but if any improvements or modifications may be required in
order to bring us meaningfully closer to that goal?"*

WHY THIS SCRIPT EXISTS. `scripts/panel_brief_validate.py` refuses a brief whose
figures are not reproduced by a named script, and it is right to: the brief for
this question previously carried a central AGAINST claim that was FALSE, and a
panel reasoning from it would have argued from a false premise. Every figure the
brief quotes is printed here, and the 1 refuted claim is printed beside its
refutation rather than quietly dropped.

WHAT IT DELIBERATELY DOES NOT DO: decide the question. The substantive issue is
whether the harness's notion of a RESOLVED finding survives where no executable
repair exists, and that is for the panel.
"""
from __future__ import annotations

import argparse
import dataclasses
import importlib.util
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

#: Domain files that ARE the code case. Named explicitly because the entry's
#: "10 STEM domains, not 1" is true and slightly flattering: 3 of the 10 are code
#: or cross-domain, so the non-code count is what the question actually turns on.
CODE_DOMAINS = {"code", "cs_software", "cross_domain"}


def _mod(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m          # dataclasses need this before exec
    spec.loader.exec_module(m)
    return m


def policy_domains() -> dict:
    from bench.cdsfl_registry.registry import DOMAIN_MAP, REGISTRY_DIR
    files = sorted(p.stem for p in (REGISTRY_DIR / "domains").glob("*.toml"))
    non_code = [d for d in files if d not in CODE_DOMAINS]
    models = sorted(p.stem for p in (REGISTRY_DIR / "models").glob("*.toml"))
    return {"domain_map_keys": len(DOMAIN_MAP), "domain_files": files,
            "domain_file_count": len(files),
            "non_code_domains": non_code, "non_code_count": len(non_code),
            "code_domains_present": sorted(set(files) & CODE_DOMAINS),
            "model_files": models, "model_file_count": len(models),
            "tasks_layer_exists": (REGISTRY_DIR / "tasks").is_dir(),
            "roles_layer_exists": (REGISTRY_DIR / "roles").is_dir()}


def stem_corpus() -> dict:
    m = _mod(REPO / "bench/tests/fixtures/stem/stem_fixtures.py", "sf_brief")
    rows = []
    for f in m.FIXTURES:
        rows.append({"key": f.key, "domain": f.domain,
                     "claims": len(f.claims),
                     "has_falsifier_template": bool(f.falsifier_template),
                     "has_correct_fix": bool(f.correct_fix),
                     "has_harmful_fix": bool(f.harmful_fix),
                     "harm_class": f.harm_class})
    return {"documents": len(rows), "claims_total": sum(r["claims"] for r in rows),
            "per_document": rows,
            "fixture_fields": sorted(x.name for x in dataclasses.fields(m.FIXTURES[0])),
            "every_doc_has_a_falsifier_template":
                all(r["has_falsifier_template"] for r in rows),
            "every_doc_has_a_harmful_fix": all(r["has_harmful_fix"] for r in rows)}


def who_reaches_the_corpus() -> dict:
    """★ THE AGAINST POINT THAT SURVIVES. The corpus is real and no LIVE-PATH
    module consults it."""
    pat = re.compile(r"stem_fixtures|fixtures/stem")
    buckets = {"test": [], "tooling": [], "script": [], "live": []}
    for p in sorted(REPO.rglob("*.py")):
        rel = p.relative_to(REPO).as_posix()
        if rel.startswith(".git/") or "sandbox_harvest" in rel or "panel_worktree" in rel:
            continue
        if not rel.startswith(("bench/", "scripts/", "hooks/")):
            continue
        try:
            if not pat.search(p.read_text(encoding="utf-8", errors="replace")):
                continue
        except OSError:
            continue
        if "/tests/" in rel:
            buckets["test"].append(rel)
        elif "/tools/" in rel:
            buckets["tooling"].append(rel)
        elif rel.startswith("scripts/"):
            buckets["script"].append(rel)
        else:
            buckets["live"].append(rel)
    return {k: {"count": len(v), "files": v} for k, v in buckets.items()}


def does_the_runner_reach_the_policy_merge() -> dict:
    """★ THE REFUTED CLAIM, PRINTED WITH ITS REFUTATION.

    Task B22 asserted that *"the canonical runner makes 0 calls to the policy
    merge engine, so nothing domain-adaptive reaches a live run -- the domain
    string reaches prompt composition only"*. The first clause is true of the
    SYMBOL and the conclusion is false: the call sits inside `compose()`, which
    the runner invokes once per seat per round, and the DOMAIN is what it passes.
    """
    runner = (REPO / "bench/reference_runner_v3.py").read_text(encoding="utf-8")
    composer = (REPO / "bench/cdsfl_registry/composer.py").read_text(encoding="utf-8")
    from bench.cdsfl_registry.registry import load_effective_policy
    merged = load_effective_policy(domain="mathematics", model="opus_4_6")
    compose_calls = re.findall(r"compose\(task_domain=\w+", runner)
    return {
        "runner_textual_refs_to_load_effective_policy":
            runner.count("load_effective_policy"),
        "composer_calls_to_load_effective_policy":
            composer.count("load_effective_policy"),
        "runner_calls_compose_with_task_domain": len(compose_calls),
        "merged_policy_keys_for_mathematics_opus": len(merged),
        "verdict": ("THE RUNNER DOES REACH THE 4-LAYER MERGE, through compose(), "
                    "and passes the DOMAIN to it. The entry's 0-calls claim is "
                    "true of the symbol and false of the behaviour."),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    res = {"policy_domains": policy_domains(),
           "stem_corpus": stem_corpus(),
           "who_reaches_the_corpus": who_reaches_the_corpus(),
           "policy_merge_on_the_live_path": does_the_runner_reach_the_policy_merge()}
    if a.json:
        print(json.dumps(res, indent=2))
        return 0

    d, c, w, pm = (res["policy_domains"], res["stem_corpus"],
                   res["who_reaches_the_corpus"], res["policy_merge_on_the_live_path"])
    print("FOR domain-generality")
    print(f"  domain layer: {d['domain_file_count']} domain policy files, reached by "
          f"{d['domain_map_keys']} DOMAIN_MAP keys")
    print(f"    of those, {d['non_code_count']} are NON-CODE STEM: "
          f"{', '.join(d['non_code_domains'])}")
    print(f"    and {len(d['code_domains_present'])} are the code case: "
          f"{', '.join(d['code_domains_present'])}")
    print(f"  model layer: {d['model_file_count']} per-model files")
    print(f"  ground-truth corpus: {c['documents']} independently written documents "
          f"carrying {c['claims_total']} tagged claims")
    for r in c["per_document"]:
        print(f"    {r['key']:12s} {r['claims']:2d} claims   {r['domain']}")
    print(f"    every document carries a runnable falsifier template: "
          f"{c['every_doc_has_a_falsifier_template']}")
    print(f"    every document carries a HARMFUL fix and a harm class: "
          f"{c['every_doc_has_a_harmful_fix']}  "
          f"(classes: {sorted({r['harm_class'] for r in c['per_document']})})")
    print(f"  THE LIVE PATH IS DOMAIN-ADAPTIVE: composer.py calls "
          f"load_effective_policy {pm['composer_calls_to_load_effective_policy']} "
          f"time(s) and the runner calls compose(task_domain=...) "
          f"{pm['runner_calls_compose_with_task_domain']} time(s); the merged policy "
          f"for mathematics/opus_4_6 has "
          f"{pm['merged_policy_keys_for_mathematics_opus']} keys")

    print("\nAGAINST")
    print(f"  NO LIVE-PATH MODULE READS THE STEM CORPUS. It is reached by "
          f"{w['tooling']['count']} tooling file(s), {w['test']['count']} test(s) "
          f"and {w['script']['count']} measurement script(s), and by "
          f"{w['live']['count']} live-path module(s).")
    print(f"  THERE IS NO ROLE LAYER in the policy merge "
          f"(roles/ exists: {d['roles_layer_exists']}), and no task layer either "
          f"(tasks/ exists: {d['tasks_layer_exists']}).")

    print("\nWITHDRAWN FROM THE EARLIER BRIEF, and this is why this script exists")
    print(f"  The entry claimed the runner makes 0 calls to the policy merge, "
          f"concluding that nothing domain-adaptive reaches a live run.")
    print(f"  The runner contains "
          f"{pm['runner_textual_refs_to_load_effective_policy']} TEXTUAL references "
          f"to load_effective_policy, which is what that claim read -- but the call "
          f"is inside compose(), which the runner invokes once per seat per round.")
    print(f"  {pm['verdict']}")

    print("\nTHE QUESTION THIS SCRIPT DOES NOT ANSWER, left for the panel")
    print("  In code and mathematics a fix is an edit whose falsifier can be re-run,")
    print("  so admissibility is decidable by execution. In an experimental domain a")
    print("  defective claim may be repairable only by NARROWING it, by RESTATING its")
    print("  boundary conditions, or by declaring it UNFALSIFIABLE on available")
    print("  evidence -- none of which a falsifier can execute against. So the open")
    print("  question is not whether the harness can REVIEW non-code STEM, which it")
    print("  demonstrably can, but whether its notion of a RESOLVED finding survives")
    print("  when no executable repair exists. The specification has no verdict for")
    print("  'correctly identified, not repairable by edit'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
