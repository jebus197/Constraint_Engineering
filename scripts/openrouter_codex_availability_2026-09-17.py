#!/usr/bin/env python3
"""Is Codex a SEPARATE model on OpenRouter, or the same model the ChatGPT seat uses?

FOUNDER, 2026-09-17, after correcting a conflation of CC1's: *"There has never
been a paid Codex seat in any simulated run. This is a clear conflation ... The
ideal scenario would be to check if ChatGPT and Codex are available via
OpenRouter, and if Codex is available separately, which version best suits our
needs, given time, money and our requirements ... I would rather have as much
diversity in seat allocation as possible."*

THE CONFOUND THIS MEASURES. `.claude/CLAUDE.md` gives the `cx` (Codex) seat and
the `cgpt` (ChatGPT) seat the SAME identifier, `openai/gpt-5.5`. 2 seats on 1
model are 1 architecture wearing 2 labels, so the panel has 4 architectures and
reports 5. Whether that can be fixed by buying a different model is a question
about the catalogue, and the catalogue is a fact to be read, not guessed.

WHAT IT READS. `https://openrouter.ai/api/v1/models`, which is public, needs no
key, and costs nothing: it is a catalogue listing, not an inference call. NO
MODEL IS DISPATCHED BY THIS SCRIPT AT ANY FLAG, so it cannot spend money.

WHAT IT REPORTS, for every model whose id or name mentions codex, gpt-5, o3, o4
or chatgpt: the exact id, the context length, and the price per 1,000,000 prompt
and completion tokens as OpenRouter states it. Then it answers the founder's
question directly: does an id containing "codex" exist, and is the seat pair
currently pointed at 1 id?

Nothing is written unless `--json PATH` is given. `--offline PATH` reads a
previously saved catalogue instead of the network, so the measurement can be
re-run from the archived copy.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[1]
CATALOGUE = "https://openrouter.ai/api/v1/models"
INTERESTING = ("codex", "gpt-5", "chatgpt", "o3", "o4-", "gpt-4.1")
#: What the project's 2 OpenAI-routed seats are pointed at today.
SEAT_IDS = {"cx (Codex)": "openai/gpt-5.5", "cgpt (ChatGPT)": "openai/gpt-5.5"}


def fetch(offline: pathlib.Path | None = None) -> dict:
    if offline:
        return json.loads(offline.read_text(encoding="utf-8"))
    req = urllib.request.Request(CATALOGUE, headers={"User-Agent": "cdsfl-availability-probe"})
    with urllib.request.urlopen(req, timeout=60) as fh:      # noqa: S310 - fixed https URL
        return json.loads(fh.read().decode("utf-8"))


def per_million(price: str | None) -> float | None:
    try:
        return round(float(price) * 1_000_000, 4)
    except (TypeError, ValueError):
        return None


def rows(cat: dict) -> list[dict]:
    """Every row this question needs, INCLUDING tool support.

    TOOL SUPPORT WAS ADDED 2026-09-18 AFTER AN ADVERSARIAL CHECK CAUGHT ITS
    ABSENCE. The first version captured id, name, context and price only, and the
    assistant then wrote "every one supports tool calling and tool choice" into
    the action list from a shell command run once and thrown away. That is
    `measured-rate-travels-with-its-script` broken in the same document that
    condemned an older claim for breaking it: a figure whose producer does not
    produce it is a claim about evidence, not evidence. It matters here because
    the panel's OpenRouter route dispatches WITH tools, so a seat pointed at a
    model that cannot take them fails at the first call.
    """
    out = []
    for m in cat.get("data", []):
        blob = f"{m.get('id','')} {m.get('name','')}".lower()
        if not any(w in blob for w in INTERESTING):
            continue
        p = m.get("pricing") or {}
        supported = m.get("supported_parameters") or []
        arch = m.get("architecture") or {}
        out.append({
            "id": m.get("id"),
            "name": m.get("name"),
            "context": m.get("context_length"),
            "usd_per_1m_prompt": per_million(p.get("prompt")),
            "usd_per_1m_completion": per_million(p.get("completion")),
            "supports_tools": "tools" in supported,
            "supports_tool_choice": "tool_choice" in supported,
            "modality": arch.get("modality"),
        })
    return sorted(out, key=lambda r: r["id"] or "")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=pathlib.Path)
    ap.add_argument("--offline", type=pathlib.Path, help="read a saved catalogue instead")
    ap.add_argument("--all", action="store_true", help="print every matching row")
    a = ap.parse_args(argv)

    try:
        cat = fetch(a.offline)
    except Exception as exc:                                  # noqa: BLE001
        print(f"the catalogue could not be read ({type(exc).__name__}: {exc}). "
              "NOT EVIDENCE: nothing is concluded about availability.")
        return 2

    matched = rows(cat)
    codex = [r for r in matched if "codex" in (r["id"] or "").lower()]
    listed = {r["id"] for r in matched}
    seats_resolve_to = {k: (v if v in listed else f"{v} (NOT IN THE CATALOGUE)")
                        for k, v in SEAT_IDS.items()}

    for r in (matched if a.all else matched[:40]):
        print(f"{r['id']:<42} ctx {str(r['context']):>8}  "
              f"${r['usd_per_1m_prompt']}/1M in  ${r['usd_per_1m_completion']}/1M out  "
              f"tools={r['supports_tools']} tool_choice={r['supports_tool_choice']}")
    out = {
        "catalogue": CATALOGUE if not a.offline else str(a.offline),
        "models_listed_in_total": len(cat.get("data", [])),
        "matching_rows": len(matched),
        "codex_ids": codex,
        "a_separate_codex_model_exists": bool(codex),
        "every_codex_id_takes_tools": all(r["supports_tools"] and r["supports_tool_choice"]
                                          for r in codex) if codex else None,
        "seat_candidates_that_cannot_take_tools": [r["id"] for r in matched
                                                   if not r["supports_tools"]],
        "the_2_seats_point_at": SEAT_IDS,
        "seat_ids_found_in_the_catalogue": seats_resolve_to,
        "the_2_seats_share_1_id": len(set(SEAT_IDS.values())) == 1,
        "rows": matched,
    }
    print("\n" + json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=2))
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
