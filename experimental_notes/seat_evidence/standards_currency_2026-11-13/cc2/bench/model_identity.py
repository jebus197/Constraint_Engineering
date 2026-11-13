# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'standards_currency_2026-11-13', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 5776d5441ba93c5c65f7ee0477a1113b86c62c7f9dd9e512f8b840b20879239f
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Which model actually answered, and can the installed client reach the intended one.

WHAT THIS CLOSES. `bench/seat_aliveness_2026-10-06.py` asks whether a route
answers. It never asks WHICH model answered, and `bench/seat_readiness.py` asks
only whether a seat is configured. So the two checks that stand between a
dispatch and a run are both blind to model identity. Measured on 2026-11-13: the
panel dispatch's 2 free Max-subscription seats (`cc2`, `fable`) pin NO version at
all -- they name an alias that resolves to whatever the installed CLI serves --
and `claude-fable-5-2` requires CLI 2.1.290 against 2.1.220 installed, a gap of
70 patch releases. Neither fact is reportable by anything in the repository today.

THE RULE THIS MODULE OBEYS, AND IT IS THE PROJECT'S OWN. Tools decide, not votes.
A model's SELF-REPORTED identity is a model vote: models routinely misstate their
own version, and a probe that parses "I am Fable 5.2" out of a reply has
substituted an assertion for a measurement. So identity here is read ONLY from
the TRANSPORT's own envelope -- the `modelUsage` map that
`claude --output-format json` returns -- which is written by the client, not by
the model. Verified live on 2026-11-13: alias `opus` resolved to `claude-opus-5`
in the envelope's `modelUsage` keys.

DERIVED, NOT TYPED. Nothing here stores a model name. `resolved_from_envelope`
reads whatever the transport reported, and `cli_version_gate` compares two
version strings it is given. A new release needs no edit to this file, which is
the whole point: a typed identity goes stale, a read one does not.

WHAT THIS DELIBERATELY DOES NOT DO. It does not rewrite a route, a pin, or a
catalogue entry. A mismatch is REPORTED, never repaired -- the human rules on it.
Auto-correcting a route would be a model editing a dispatch constraint with no
human in the loop, which is the defect this round was convened to examine, not a
fix for it.
"""

from __future__ import annotations

import re
from typing import Any

__all__ = [
    "resolved_from_envelope",
    "parse_required_cli",
    "cli_version_gate",
    "identity_verdict",
    "IDENTITY_STATES",
]

#: Every value `identity_verdict()["how"]` can take. A caller that branches on
#: identity must handle all 4; an unrecognised state is how a blind check gets
#: reported as a green one.
IDENTITY_STATES = ("match", "mismatch", "unreachable", "unknown")

#: The upstream refusal names its own minimum client version. This matches the
#: version TRIPLE out of such a message; it is deliberately not a model-name
#: pattern, because model names are exactly what must not be typed here.
_REQUIRED_CLI_RE = re.compile(
    r"(?:requires|minimum|at least|upgrade to)\D{0,40}?(\d+\.\d+\.\d+)",
    re.IGNORECASE,
)


def resolved_from_envelope(envelope: Any) -> list[str]:
    """The model ids the TRANSPORT says served the call, busiest first.

    Reads `modelUsage`, which the client writes. Returns [] when the envelope
    carries no such key -- an empty list means "the transport did not say", which
    a caller must not read as "the intended model answered".
    """
    if not isinstance(envelope, dict):
        return []
    usage = envelope.get("modelUsage")
    if not isinstance(usage, dict):
        return []

    def _out(k: str) -> int:
        v = usage.get(k)
        return v.get("outputTokens", 0) if isinstance(v, dict) else 0

    return sorted((k for k in usage if isinstance(k, str)), key=lambda k: -_out(k))


def parse_required_cli(text: str | None) -> str | None:
    """The minimum client version an upstream refusal names, or None.

    The gap is only computable because the refusal states its own requirement.
    Where it does not, this returns None and the verdict is `unknown` rather than
    a guessed number.
    """
    if not isinstance(text, str):
        return None
    m = _REQUIRED_CLI_RE.search(text)
    return m.group(1) if m else None


def _triple(v: str | None) -> tuple[int, int, int] | None:
    if not isinstance(v, str):
        return None
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", v)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None


def cli_version_gate(required: str | None, installed: str | None) -> dict[str, Any]:
    """Can `installed` reach a model that `required` demands?

    `patch_gap` is reported ONLY when the two versions share a major and a minor,
    because a patch count across a minor boundary is not a distance -- it is two
    numbers subtracted. Across a minor or major boundary `patch_gap` is None and
    `reachable` still answers.
    """
    req, ins = _triple(required), _triple(installed)
    if req is None or ins is None:
        return {"reachable": None, "patch_gap": None, "required": required,
                "installed": installed,
                "why": "a version was missing or unparseable, so no gate applies"}
    reachable = ins >= req
    gap = (req[2] - ins[2]) if (req[:2] == ins[:2] and not reachable) else None
    return {"reachable": reachable, "patch_gap": gap, "required": required,
            "installed": installed,
            "why": (f"installed {installed} "
                    f"{'satisfies' if reachable else 'is below'} "
                    f"required {required}")}


def identity_verdict(intended: str | None,
                     envelope: Any = None,
                     installed_cli: str | None = None,
                     refusal_text: str | None = None) -> dict[str, Any]:
    """What answered, whether it is what was asked for, and whether it is reachable.

    NEVER RAISES. A probe that threw on a malformed envelope would turn a
    reporting check into a dispatch blocker, and this check's whole contract is
    that it reports and the human rules.

    `how` is one of IDENTITY_STATES:
      match       the transport named a model consistent with `intended`
      mismatch    the transport named a model NOT consistent with `intended`
      unreachable the installed client is below the version the model requires
      unknown     the transport did not say, so nothing is claimed
    """
    resolved = resolved_from_envelope(envelope)
    required = parse_required_cli(refusal_text)
    gate = cli_version_gate(required, installed_cli)

    if gate["reachable"] is False:
        return {"how": "unreachable", "intended": intended, "resolved": resolved,
                "gate": gate,
                "why": (f"intended {intended!r} requires client {required} and "
                        f"{installed_cli} is installed; the seat cannot reach it")}
    if not resolved:
        return {"how": "unknown", "intended": intended, "resolved": [],
                "gate": gate,
                "why": ("the transport returned no modelUsage, so WHICH model "
                        "answered was not measured; self-report is not accepted")}
    if not isinstance(intended, str) or not intended.strip():
        return {"how": "unknown", "intended": intended, "resolved": resolved,
                "gate": gate,
                "why": ("no intended model was given, so a resolved id cannot be "
                        "compared against one")}

    # An ALIAS is a request for whatever the client serves, so it cannot mismatch
    # on version -- only on FAMILY. A VERSION-BEARING intent must appear in the
    # resolved id. Both tests are substring tests on the transport's own string;
    # no model-name table is consulted or stored.
    want = intended.strip().lower()
    got = [r.lower() for r in resolved]
    tail = want.split("/")[-1]
    family = re.split(r"[-_]", tail)[0]
    hit = any(want in g for g in got) or any(family and family in g for g in got)
    return {"how": "match" if hit else "mismatch", "intended": intended,
            "resolved": resolved, "gate": gate,
            "why": f"transport reported {resolved!r} for intended {intended!r}"}
