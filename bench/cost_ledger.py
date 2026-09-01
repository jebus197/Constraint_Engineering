"""What a run actually cost. GAP 2, 2026-08-23.

WHY THIS EXISTS. `bench/FINANCIAL_LEDGER.md` has sat in the repository since March
and NEITHER RUNNER WRITES TO IT. Measured 2026-08-23: zero references to it in
`reference_runner_v3.py` or in the build-experiment harness. So this project has no
record of what any experiment cost, and the founder is spending borrowed money.

The one figure that did exist was an estimate, and it was wrong by 18x -- the build
experiment was projected at about eight dollars and cost about forty-five cents. An
estimate that far out is not a budget, it is a guess with a currency symbol.

WHAT THIS RECORDS, AND WHAT IT REFUSES TO.
It records what is OBSERVABLE from this side: which route each dispatch used,
whether that route is metered, the prompt and response sizes, and the elapsed time.
From those it derives a token estimate and, where a price is supplied, a cost.

It does NOT invent a price. `PRICES` is empty by default and every derived figure is
labelled ESTIMATED. A ledger that quietly asserts a dollar figure it cannot verify
is worse than no ledger, because it would be believed. The provider's own invoice is
the only authority on what was actually charged; this is the usage record you check
it against.

Max-plan routes (the Claude CLI) are recorded with `metered=False` and contribute
zero to any cost total. They are still counted, because "how much did we use" and
"how much were we charged" are different questions.
"""
from __future__ import annotations

import json
import pathlib
import threading
import time
from typing import Any, Dict, List, Optional

REPO = pathlib.Path(__file__).resolve().parent.parent

# Routes that bill. The Claude CLI runs on the founder's Max subscription and does
# not. Anything unknown is treated as METERED, because assuming a route is free is
# the expensive direction to be wrong in.
UNMETERED_ROUTES = frozenset({"claude_cli"})

# Deliberately empty. See the module docstring: no price is asserted that has not
# been supplied. Populate at call time from a config the founder controls, or leave
# it empty and read the token counts.
PRICES: Dict[str, Dict[str, float]] = {}

_LOCK = threading.Lock()


class CostLedger:
    """Append-only usage record for one run."""

    def __init__(self, run_dir: pathlib.Path, prices: Optional[Dict] = None) -> None:
        self.path = pathlib.Path(run_dir) / "cost_ledger.json"
        self.prices = dict(prices or PRICES)
        self.rows: List[Dict[str, Any]] = []
        if self.path.is_file():                     # resume-safe
            try:
                self.rows = json.loads(self.path.read_text()).get("dispatches", [])
            except Exception:                        # noqa: BLE001 — a corrupt
                self.rows = []                       # ledger must not kill a run

    def record(self, *, model: str, route: str, prompt_chars: int,
               response_chars: int, elapsed_s: float, round_idx: Optional[int] = None,
               note: str = "") -> Dict[str, Any]:
        """One dispatch. Never raises: a ledger failure must not fail an experiment."""
        try:
            metered = route not in UNMETERED_ROUTES
            # 4 chars per token is the conventional rough figure and is LABELLED as
            # an estimate everywhere it surfaces. The provider counts differently.
            row = {
                "model": model, "route": route, "metered": metered,
                "round": round_idx,
                "prompt_chars": int(prompt_chars),
                "response_chars": int(response_chars),
                "est_input_tokens": int(prompt_chars) // 4,
                "est_output_tokens": int(response_chars) // 4,
                "elapsed_s": round(float(elapsed_s), 1),
                "ts": int(time.time()),
                "note": note,
            }
            price = self.prices.get(model) or self.prices.get(route)
            if metered and price:
                row["est_cost_usd"] = round(
                    row["est_input_tokens"] / 1e6 * price.get("in", 0.0)
                    + row["est_output_tokens"] / 1e6 * price.get("out", 0.0), 6)
                row["price_source"] = "supplied at call time"
            with _LOCK:
                self.rows.append(row)
                self._flush()
            return row
        except Exception as exc:                     # noqa: BLE001
            return {"error": f"{type(exc).__name__}: {exc}"}

    def totals(self) -> Dict[str, Any]:
        metered = [r for r in self.rows if r.get("metered")]
        free = [r for r in self.rows if not r.get("metered")]
        priced = [r for r in metered if "est_cost_usd" in r]
        out: Dict[str, Any] = {
            "dispatches": len(self.rows),
            "metered_dispatches": len(metered),
            "unmetered_dispatches": len(free),
            "est_input_tokens": sum(r.get("est_input_tokens", 0) for r in metered),
            "est_output_tokens": sum(r.get("est_output_tokens", 0) for r in metered),
            "wall_clock_s": round(sum(r.get("elapsed_s", 0.0) for r in self.rows), 1),
            "priced_dispatches": len(priced),
            "unpriced_dispatches": len(metered) - len(priced),
        }
        if priced:
            out["est_cost_usd"] = round(sum(r["est_cost_usd"] for r in priced), 4)
        out["caveat"] = (
            "ESTIMATED from character counts at 4 chars/token. The provider's "
            "invoice is the authority on what was charged; this is the usage "
            "record to check it against. Unpriced dispatches contribute ZERO to "
            "any cost figure and are counted separately so the gap is visible.")
        return out

    def _flush(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps({"totals": self.totals(), "dispatches": self.rows}, indent=1),
            encoding="utf-8")
