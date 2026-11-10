"""B21 step 5: the selectable model list, generated rather than hand-written.

HIS DESIGN INTENT, verbatim, 2026-10-17: "model selection should preferably be
a simple box, containing a scrollable list of models available from OpenRouter
and models available on a user's local machine ... with available models on a
user's local machine at the top of this list", with "role management, such as
'worker' ... 'classifier' ... and 'orchestrator'" individually selectable, plus
a recommended list and a note that untested models in a given role carry
unknown performance.

HIS ARGUMENT FOR IT, verbatim: "We clearly cannot make such claims, and then
say 'Oh, btw, that isn't really true. Here is a list of the only models you can
use.'"

THREE SOURCES, LOCAL FIRST AS HE SPECIFIED:
  1. LOCAL    -- models served by an Ollama-compatible daemon on this machine.
  2. REGISTRY -- bench/cdsfl_registry/models/*.toml, the ones this project has
                 policy for. These carry role evidence; everything else does not.
  3. REMOTE   -- OpenRouter's public model list.

THIS MODULE NEVER COSTS MONEY. Listing models is a free endpoint and the probe
is opt-in: `catalogue()` does not touch the network unless `include_remote=True`
is passed, and `--help` never does. That is the founder's standing rule after
15 of 17 runners were found to bill on `--help`.

UNTESTED IS SAID, NOT IMPLIED. Every entry carries `role_evidence`, which is
the roles this project has actually run that model in. An empty list means
unknown performance in every role, and the renderer says so in words.
"""
from __future__ import annotations

import json
import os
import pathlib
import urllib.error
import urllib.request

REPO = pathlib.Path(__file__).resolve().parent.parent
MODELS_DIR = REPO / "bench" / "cdsfl_registry" / "models"
ROLES_DIR = REPO / "bench" / "cdsfl_registry" / "roles"
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
LOCAL_ENDPOINTS = ("http://127.0.0.1:11434/api/tags",)   # Ollama-compatible


def registry_models() -> list[dict]:
    """Models this project holds policy for. Never empty on a healthy tree."""
    out = []
    if not MODELS_DIR.is_dir():
        return out
    for p in sorted(MODELS_DIR.glob("*.toml")):
        out.append({"id": p.stem, "source": "registry", "local": False,
                    "has_policy": True})
    return out


def known_roles() -> list[str]:
    if not ROLES_DIR.is_dir():
        return []
    return sorted(p.stem for p in ROLES_DIR.glob("*.toml"))


def local_models(timeout: float = 0.5) -> list[dict]:
    """Models served locally. Fails SILENTLY and fast -- absence is normal."""
    out = []
    for url in LOCAL_ENDPOINTS:
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                data = json.loads(r.read().decode())
        except Exception:                                          # noqa: BLE001
            continue
        for m in data.get("models", []):
            name = m.get("name") or m.get("model")
            if name:
                out.append({"id": name, "source": "local", "local": True,
                            "has_policy": False})
    return out


def remote_models(timeout: float = 5.0) -> list[dict]:
    """OpenRouter's public catalogue. A FREE endpoint; no key, no charge."""
    req = urllib.request.Request(
        OPENROUTER_MODELS_URL, headers={"User-Agent": "cdsfl-model-catalogue"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode())
    except (urllib.error.URLError, OSError, ValueError):
        return []
    return [{"id": m.get("id"), "source": "openrouter", "local": False,
             "has_policy": False}
            for m in data.get("data", []) if m.get("id")]


def role_evidence() -> dict[str, list[str]]:
    """Which roles this project has ACTUALLY run each model in.

    Read from the registry's own role configs rather than asserted, so a model
    with no recorded role returns an empty list and the renderer can say
    `unknown performance` instead of implying it is fine.
    """
    import tomllib
    ev: dict[str, list[str]] = {}
    for p in sorted(ROLES_DIR.glob("*.toml")) if ROLES_DIR.is_dir() else []:
        try:
            cfg = tomllib.loads(p.read_text(encoding="utf-8"))
        except Exception:                                          # noqa: BLE001
            continue
        for m in (cfg.get("role") or {}).get("observed_models", []) or []:
            ev.setdefault(str(m), []).append(p.stem)
    return ev


def catalogue(include_remote: bool = False, include_local: bool = True) -> list[dict]:
    """The selectable list, LOCAL FIRST, then registry, then remote.

    `include_remote` defaults to False so that no call path reaches the network
    by accident. Duplicates are merged on `id`, keeping the earliest (and so
    most local) source and OR-ing `has_policy`.
    """
    rows: list[dict] = []
    if include_local:
        rows += local_models()
    rows += registry_models()
    if include_remote:
        rows += remote_models()
    ev = role_evidence()
    seen: dict[str, dict] = {}
    for r in rows:
        k = r["id"]
        if k in seen:
            seen[k]["has_policy"] = seen[k]["has_policy"] or r["has_policy"]
            continue
        r = dict(r)
        r["role_evidence"] = sorted(ev.get(k, []))
        r["untested_note"] = ("" if r["role_evidence"] else
                              "no role evidence in this project: performance "
                              "in any role is unknown")
        seen[k] = r
    order = {"local": 0, "registry": 1, "openrouter": 2}
    return sorted(seen.values(), key=lambda r: (order[r["source"]], r["id"]))


def render(rows: list[dict]) -> str:
    lines = [f"{len(rows)} selectable model(s). Local first, as he specified.",
             f"roles available: {', '.join(known_roles()) or 'none'}", ""]
    for r in rows:
        tag = "LOCAL" if r["local"] else r["source"].upper()
        pol = "policy" if r["has_policy"] else "no policy"
        note = f"  -- {r['untested_note']}" if r["untested_note"] else \
               f"  -- run here as: {', '.join(r['role_evidence'])}"
        lines.append(f"  [{tag:10}] {r['id']:38} ({pol}){note}")
    return "\n".join(lines)


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--remote", action="store_true",
                    help="also list OpenRouter's public catalogue (free endpoint)")
    ap.add_argument("--no-local", action="store_true",
                    help="skip the local-daemon probe")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    rows = catalogue(include_remote=a.remote, include_local=not a.no_local)
    print(json.dumps(rows, indent=1) if a.json else render(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
