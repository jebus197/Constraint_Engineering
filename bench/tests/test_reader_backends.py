"""Librarian backend routing: the right model, and K3 available but not default.

Two founder directives, 2026-07-31.

1. "DeepSeek-chat is hot trash. Make sure it's fixed/changed to deepseek-v4-pro
   going forward." The ouroboros librarian's DeepSeek route hardcoded
   `deepseek-chat` at its dispatch site — a different and weaker model than the
   `deepseek-v4-pro` the panel actually runs. Nobody had evaluated the librarian
   on `deepseek-chat`; the bake-off measured `deepseek-v4-pro`. Two further
   dispatch sites carried the same string.

2. "Wire K3 with an optional shadow switch for now until we can confirm it is
   fully working." Kimi K3 measured 0.887 on the 71-candidate relevance
   benchmark against Haiku's 0.873, and recovered 24 of 25 genuinely relevant
   papers against Haiku's 21 — but McNemar exact gives p=1.0, so the difference
   is not established. It is provisioned, never the default, and selecting it is
   a deliberate act.

The routing must degrade, never raise: an unreachable backend falls through to
the deterministic extractive brief, so a broken K3 cannot take a run down.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from bench.ouroboros_cell import OuroborosCell  # noqa: E402


class TestDeepSeekModelIsThePanelsModel:
    def test_the_default_is_v4_pro(self):
        assert OuroborosCell.DEEPSEEK_READER_MODEL == "deepseek-v4-pro"

    def test_no_dispatch_site_still_names_deepseek_chat(self):
        """The string must not reappear at any call site, in any module.

        Comments naming it as the superseded value are fine and are excluded —
        the point is that nothing DISPATCHES to it.
        """
        offenders = []
        for path in sorted((_root / "bench").glob("*.py")):
            for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith("#") or "deepseek-chat" not in line:
                    continue
                code = line.split("#", 1)[0]
                if "deepseek-chat" in code:
                    offenders.append(f"{path.name}:{i}: {stripped[:80]}")
        assert not offenders, (
            "a dispatch site still routes to deepseek-chat:\n  " + "\n  ".join(offenders))


class TestKimiIsWiredButNotDefault:
    def test_kimi_is_not_the_default(self):
        """Not established as better. Provisioned, not promoted."""
        assert OuroborosCell(shadow=True).reader_backend == "haiku"

    def test_kimi_is_selectable(self):
        assert OuroborosCell(shadow=True, reader_backend="kimi").reader_backend == "kimi"

    def test_the_kimi_model_id_is_the_openrouter_route(self):
        assert OuroborosCell.KIMI_READER_MODEL == "moonshotai/kimi-k3"

    @pytest.mark.parametrize("backend", ["haiku", "deepseek", "kimi", "none"])
    def test_every_documented_backend_is_accepted(self, backend):
        assert OuroborosCell(shadow=True, reader_backend=backend).reader_backend == backend


class TestAnUnreachableBackendDegradesRatherThanRaising:
    """The whole point of the extractive fallback. A librarian that cannot be
    reached must produce a real, deterministic brief — not an exception that
    kills a paid round.

    These tests ATTEMPT an outbound call on purpose: the netguard denying it is
    precisely the "unreachable backend" the test needs, so the attempt is the
    experimental condition rather than an accident. Hence `allow_outbound`.

    Without that marker these three tests turn `--netguard-strict` red, because
    strict mode escalates any attempt to an error. That happened — this file was
    written before the guard existed and put three errors into the first strict
    run after it landed. The marker is the guard's own purpose-built exemption;
    the calls are still denied and nothing reaches the wire.
    """

    PAPER = {"title": "Numerically stable streaming variance",
             "abstract": "We present a Welford-class update that avoids "
                         "catastrophic cancellation in the sum of squares."}
    TARGET = "streaming variance suffers catastrophic cancellation"

    @pytest.mark.allow_outbound
    @pytest.mark.parametrize("backend", ["kimi", "deepseek", "haiku"])
    def test_a_dead_backend_still_returns_a_brief(self, backend, monkeypatch):
        cell = OuroborosCell(shadow=True, reader_backend=backend,
                             reader_model="definitely-not-a-real-model-id")
        out = cell._cheap_reader_read(self.TARGET, self.PAPER, "")
        assert out["relevance"] in ("HIGH", "MEDIUM", "LOW", "NONE")
        assert isinstance(out["brief"], str)
        assert "error" in out, "a degraded read must say why it degraded"

    def test_backend_none_is_deterministic_and_needs_no_network(self):
        cell = OuroborosCell(shadow=True, reader_backend="none")
        a = cell._cheap_reader_read(self.TARGET, self.PAPER, "")
        b = cell._cheap_reader_read(self.TARGET, self.PAPER, "")
        assert a["relevance"] == b["relevance"] and a["brief"] == b["brief"]
        assert a["reader_model"] == "extractive_fallback"
