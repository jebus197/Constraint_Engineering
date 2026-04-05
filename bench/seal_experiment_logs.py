"""
Seal Experiment Logs — Cryptographic Signing and Merkle Bundling

Finds all experiment log directories under bench/logs/ matching known
experiment prefixes (exp30_endocrine_*, exp31_postfix_*), then creates
a tamper-evident VerificationChain per experiment containing all round
chat logs, checkpoints, completion signals, and reports.

Each experiment directory receives an experiment_chain.json file that
can be independently verified via verification_chain.py.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "bench"))

from bench.verification_chain import VerificationChain  # noqa: E402

LOGS_DIR = REPO_ROOT / "bench" / "logs"

# Experiment directory prefixes to seal.
EXPERIMENT_PREFIXES = ("exp30_endocrine_", "exp31_postfix_")

# Filename pattern for round log files.
# Handles both r{N}_{model}_{timestamp}.json and round{N}_{model}_{timestamp}.json.
# The timestamp is always the final _YYYYMMDDTHHMMSSZ segment, so we parse
# from the right to handle model labels that contain underscores.
ROUND_RE = re.compile(
    r"^(?:r|round)(\d+)_(.+)_(\d{8}T\d{6}Z)\.json$"
)


def _parse_round_filename(name: str) -> dict | None:
    """Extract round number, model label, and timestamp from a round filename.

    Returns a dict with keys 'round', 'model', 'timestamp', or None if
    the filename does not match the expected pattern.
    """
    m = ROUND_RE.match(name)
    if not m:
        return None
    return {
        "round": int(m.group(1)),
        "model": m.group(2),
        "timestamp": m.group(3),
    }


def _read_json_safe(path: Path) -> dict | None:
    """Read and parse a JSON file. Returns None on failure."""
    try:
        text = path.read_text(encoding="utf-8")
        return json.loads(text)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"  WARNING: skipping {path.name} — {exc}", file=sys.stderr)
        return None


def _sanitise_payload(obj):
    """Recursively convert floats to string representations.

    The VerificationChain's canonical_json rejects floats for
    cross-platform determinism. We convert them to fixed-precision
    strings so that large model response payloads can be sealed.
    """
    if isinstance(obj, float):
        return str(obj)
    if isinstance(obj, dict):
        return {k: _sanitise_payload(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitise_payload(v) for v in obj]
    return obj


def _discover_experiments() -> list[Path]:
    """Find experiment directories under the logs folder."""
    if not LOGS_DIR.is_dir():
        return []
    dirs = []
    for entry in sorted(LOGS_DIR.iterdir()):
        if entry.is_dir() and any(
            entry.name.startswith(p) for p in EXPERIMENT_PREFIXES
        ):
            dirs.append(entry)
    return dirs


def _seal_experiment(exp_dir: Path, dry_run: bool = False) -> dict | None:
    """Seal all logs in a single experiment directory.

    Returns a summary dict, or None if there was nothing to seal.
    """
    exp_name = exp_dir.name
    chain = VerificationChain()
    record_count = 0

    # 1. Collect and sort round files by round number, then model.
    round_files: list[tuple[int, str, str, Path]] = []
    for f in sorted(exp_dir.iterdir()):
        if not f.is_file() or f.suffix != ".json":
            continue
        info = _parse_round_filename(f.name)
        if info is not None:
            round_files.append(
                (info["round"], info["model"], info["timestamp"], f)
            )

    round_files.sort(key=lambda t: (t[0], t[1]))

    # 2. Append round log records.
    for rnd, model, ts, fpath in round_files:
        payload = _read_json_safe(fpath)
        if payload is None:
            continue
        payload = _sanitise_payload(payload)
        metadata = {
            "experiment": exp_name,
            "round": rnd,
            "model": model,
            "timestamp": ts,
            "source_file": fpath.name,
        }
        if dry_run:
            print(f"  [DRY RUN] Would seal round log: {fpath.name}")
        else:
            chain.append_record(
                artifact_type="model_chat_log",
                payload=payload,
                recorded_by="seal_experiment_logs",
                metadata=metadata,
                storage_mode="hash_only",
            )
        record_count += 1

    # 3. Append checkpoint, completion signal, and report files.
    special_files = {
        "checkpoint.json": "experiment_checkpoint",
        "completion_signal.json": "experiment_checkpoint",
    }
    for f in sorted(exp_dir.iterdir()):
        if not f.is_file() or f.suffix != ".json":
            continue
        fname = f.name
        if fname in special_files:
            artifact_type = special_files[fname]
        elif "report" in fname.lower():
            artifact_type = "experiment_report"
        else:
            continue

        payload = _read_json_safe(f)
        if payload is None:
            continue
        payload = _sanitise_payload(payload)
        metadata = {
            "experiment": exp_name,
            "source_file": fname,
        }
        if dry_run:
            print(f"  [DRY RUN] Would seal {artifact_type}: {fname}")
        else:
            chain.append_record(
                artifact_type=artifact_type,
                payload=payload,
                recorded_by="seal_experiment_logs",
                metadata=metadata,
                storage_mode="full_payload",
            )
        record_count += 1

    if record_count == 0:
        print(f"  No sealable files found in {exp_name}.", file=sys.stderr)
        return None

    if dry_run:
        return {
            "experiment": exp_name,
            "records": record_count,
            "merkle_root": "(dry run — not computed)",
        }

    # 4. Seal the epoch and save.
    epoch = chain.seal_epoch()
    out_path = exp_dir / "experiment_chain.json"
    chain.save_json(str(out_path))

    return {
        "experiment": exp_name,
        "records": record_count,
        "merkle_root": epoch["merkle_root"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Seal experiment chat logs into Merkle-backed verification chains."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be sealed without writing any files.",
    )
    args = parser.parse_args()

    experiments = _discover_experiments()
    if not experiments:
        print("No experiment directories found under bench/logs/.")
        return 1

    print(f"Found {len(experiments)} experiment(s) to seal.\n")

    summaries: list[dict] = []
    for exp_dir in experiments:
        print(f"Sealing {exp_dir.name} ...")
        summary = _seal_experiment(exp_dir, dry_run=args.dry_run)
        if summary is not None:
            summaries.append(summary)

    if not summaries:
        print("\nNo records were sealed.")
        return 1

    # Print summary table.
    print("\n" + "=" * 72)
    print(f"{'Experiment':<45} {'Records':>7}  Merkle Root (first 32)")
    print("-" * 72)
    for s in summaries:
        root_preview = s["merkle_root"][:32] if len(s["merkle_root"]) > 32 else s["merkle_root"]
        print(f"{s['experiment']:<45} {s['records']:>7}  {root_preview}")
    print("=" * 72)

    return 0


if __name__ == "__main__":
    sys.exit(main())
