#!/usr/bin/env python3
"""Pre-run credential preflight (2026-07-06).

Checks that every model-route credential the dispatch layer needs is present
in <repo>/.env or the environment. Prints PRESENT/ABSENT per key — NEVER the
value. Exits 1 if any REQUIRED key is missing, so launchers can gate on it.

Written after the 2026-06-09 .env overwrite incident (the model keys were
destroyed by a write to .env that replaced the file instead of appending).
Standing conventions this enforces/documents:
  * .env is append-only for agents — never rewrite the whole file;
  * every experiment launch should run this preflight first.
"""
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REQUIRED = {
    "OPENROUTER_API_KEY": "Codex + ChatGPT + Gemini panel routes (OpenRouter)",
    "DEEPSEEK_API_KEY": "DeepSeek direct route",
}
OPTIONAL = {
    "GEMINI_API_KEY": "legacy direct-Google fallback (panel uses OpenRouter since 2026-05-10)",
    "GOOGLE_API_KEY": "legacy direct-Google fallback (alternate name)",
    "SEMANTIC_SCHOLAR_API_KEY": "ouroboros literature route (fast tier)",
}

def _env_file_names(path: Path) -> set:
    names = set()
    if path.is_file():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                if val.strip():
                    names.add(key.strip())
    return names

def main() -> int:
    found = _env_file_names(REPO / ".env") | {k for k in list(REQUIRED) + list(OPTIONAL) if os.environ.get(k)}
    missing_required = []
    print(f"Credential preflight — {REPO / '.env'} + environment (values never shown)\n")
    for key, why in REQUIRED.items():
        ok = key in found
        print(f"  [{'PRESENT' if ok else 'ABSENT '}] {key}  (REQUIRED: {why})")
        if not ok:
            missing_required.append(key)
    for key, why in OPTIONAL.items():
        print(f"  [{'PRESENT' if key in found else 'absent '}] {key}  (optional: {why})")
    if missing_required:
        print(f"\nBLOCKED: {len(missing_required)} required key(s) missing: {', '.join(missing_required)}")
        print("Add them to <repo>/.env (append — do not rewrite the file), format per .env.example.")
        return 1
    print("\nOK: all required model-route credentials present.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
