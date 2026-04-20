# logs/chat/ — Curated Chat Record

Curated chat and conversation artefacts that belong in the project's
preserved record. Populated deliberately, not automatically.

## What belongs here

- Edited panel discussions worth preserving as evidence.
- Redacted transcripts that have been through privacy review.
- Published exchanges (e.g. accompanying a blog post or paper).

## What does not belong here

- Raw Claude Code session transcripts (JSONL files under
  `~/.claude/projects/…`). These contain private user context,
  strategy discussions, and tool outputs that may reference material
  outside the project; they must not enter the public repository.
- Unredacted chat exports that have not been through privacy review.

## Sealing

Each directory under `chat/` receives a `sealed_chain.json` Merkle seal
when `python3 scripts/cdsfl_seal_logs.py` is run from the repo root.
Verification is automatic under `scripts/cdsfl_qc.py`.
