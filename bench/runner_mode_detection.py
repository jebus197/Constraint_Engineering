#!/usr/bin/env python3
"""Detect whether a declared mode was actually OPERATING -- entry B28.

HIS RULING, 2026-10-07 and again 2026-10-11: "state should be detected rather than
declared. The panel used to decide whether a round was blind or joint by reading an
environment variable, so forgetting the variable silently downgraded the check. It
now decides from what the briefing document actually contains. The runners have
several places where a mode is declared by a flag that can be forgotten."

WHAT THIS IS NOT. It is not an override. For most of these modes the detected fact
must not replace the declaration mid-run: flipping `location_keyed_convergence`
would change the convergence measure itself, and a measurement that silently
redefines itself is worse than one that is wrong in a stated way. So the
conversion is DETECT AND RECONCILE -- derive from the run's own output whether the
mode was operating, compare it with what was declared, and make any disagreement
LOUD AND RECORDED. After this a forgotten flag is reported rather than absorbed,
which is exactly the failure he named.

WHICH MODES, AND WHY ONLY THESE. `scripts/which_runner_modes_are_declared_2026-10-18.py`
classifies all 28 boolean config fields. 23 are an operator's CHOICE -- whether to
spend dispatch on arbitration, whether the tagger runs -- and there is no fact in
the run that could contradict a choice, so converting one would invent a signal.
5 assert a FACT about the run. `resume` was judged a mode and then RECLASSIFIED by
falsification: a checkpoint existing does not establish that the operator wants to
continue it, and detecting that one would silently resume a previous run whenever
its checkpoint survived on disk -- a worse failure than the forgotten flag.

AN HONEST DETECTOR MUST BE ABLE TO SAY IT DOES NOT KNOW. When a mode is off, the
artefacts it would produce are absent, so absence cannot distinguish "off" from "on
but broken". Each detector therefore returns True, False or None, and None means
UNDECIDABLE rather than False. A detector that guessed would manufacture
disagreements, and a manufactured disagreement in a run report is worse than a
silence because it would be acted on.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Optional

AGREE = "AGREE"
DECLARED_NOT_OPERATING = "DECLARED_NOT_OPERATING"
OPERATING_NOT_DECLARED = "OPERATING_NOT_DECLARED"
UNDECIDABLE = "UNDECIDABLE"

#: A declared value this pattern matches is not a boolean at all but the
#: redactor's placeholder. Measured 2026-10-18 across the archive: 4 of 4 reports
#: carrying a declared config withhold `location_keyed_convergence`, because its
#: name contains "key". It is not a secret, and the effect is that this one mode
#: cannot be reconciled at all. Raised separately; here it must be DETECTED and
#: reported as UNDECIDABLE rather than read as falsy, which is what a plain
#: `bool(value)` would have done -- silently turning a withheld True into a False
#: and inventing a DECLARED_NOT_OPERATING disagreement in every report.
_WITHHELD = re.compile(r"withheld|redact", re.I)


def _truthy_or_none(value) -> Optional[bool]:
    """A declared flag as a tristate. A withheld or absent value is None."""
    if value is None:
        return None
    if isinstance(value, str):
        if _WITHHELD.search(value):
            return None
        low = value.strip().lower()
        if low in ("true", "1", "yes"):
            return True
        if low in ("false", "0", "no", ""):
            return False
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return None


def _nonempty_series(report: dict, key: str) -> Optional[bool]:
    v = report.get(key)
    if v is None:
        return None
    if isinstance(v, (list, tuple)):
        return len(v) > 0
    return bool(v)


def _gating_flag(report: dict, key: str) -> Optional[bool]:
    """★ CIRCULAR, SO IT RETURNS None. Measured 2026-10-18.

    `result["location_crit_series_is_gating"]` and its hierarchical twin are each
    written as `bool(getattr(cfg, <the flag>, False))` -- a direct COPY of the
    switch, under a name that reads like a statement about behaviour. Comparing
    such a key with the declaration compares the flag with itself, so it can never
    disagree, and a detector built on it would report AGREE forever while
    witnessing nothing.

    `gamma_gate_series` is no better: it is the hardcoded string literal
    "gamma_critical_history". When `location_keyed_convergence` is on, the
    location-keyed count OVERWRITES `novel_critical_history`, which the gate
    reads, so the gate's input is substituted while that field still names the
    same series. The substitution is exactly what a reader would need to see.

    The key is still accepted as an argument so the pairing is recorded and
    checked by the guard; it is simply not treated as evidence.
    """
    return None


def _models_declared(report: dict) -> Optional[bool]:
    """Did the OPERATOR declare the model set, or were defaults used?

    ★ THE OBVIOUS DETECTOR IS WRONG AND WAS CAUGHT BY TRYING IT. Reading the
    report's `models` list and calling a non-empty list "declared" manufactured a
    disagreement on leg 3 of the shakedown: it recorded 6 models while its argv
    carried no `--models`, because DEFAULTS produce a model list too. A non-empty
    list is therefore consistent with both answers and establishes neither.

    The sound signal is the launch itself. `models_were_declared` is set when
    `--models` is passed or when a config FILE carries a `models` key, so:
      * `--models` in the recorded argv            -> True
      * neither `--models` nor `--config` present  -> False, defaults were used
      * `--config` present                         -> None, because the file's
        contents are not in the report and a config file may declare models
        without any trace in argv.
    """
    argv = report.get("_declared_argv")
    if not isinstance(argv, (list, tuple)):
        return None
    tokens = [str(a) for a in argv]
    if "--models" in tokens:
        return True
    if "--config" in tokens:
        return None
    return False


def _severity_spec_operating(report: dict) -> Optional[bool]:
    """UNDECIDABLE from any archived report, and the reason is measured.

    The obvious artefact is `severity_admissibility`, and reading it produced a
    disagreement on free_run1: declared False, "operating" True. That was MY
    detector being wrong, not the run. `result["severity_admissibility"]` is
    written UNCONDITIONALLY at two sites, the comment above it saying it is
    "stamped into every report (0C.12)". An artefact that appears whether or not
    the mode is on cannot witness the mode operating.

    No gated artefact exists. The specification's distinguishing effect is that a
    disproved finding scores zero, so a sound detector would compare severity
    against falsifier verdicts -- which needs at least one refuted finding to be
    present, and 0 of 41 findings across legs 1 and 2 carried one. Until the
    runner records the effect, this returns None.
    """
    return None


def _sk_operating(report: dict) -> Optional[bool]:
    for key in ("sk_series", "sk_scores", "sk_score_prose_listings_result"):
        if key in report:
            return _nonempty_series(report, key)
    return None


#: Why a mode's artefact is not usable as evidence. SOUND means it is.
SOUND = "SOUND"
CIRCULAR = "CIRCULAR"          # the artefact is a copy of the flag
UNGATED = "UNGATED"            # the artefact appears whether the mode is on or not
ABSENT = "ABSENT"              # no artefact exists at all


@dataclass(frozen=True)
class Mode:
    name: str
    detect: Callable[[dict], Optional[bool]]
    basis: str
    #: The report key the detector reads, or None where none exists. Named so
    #: that the guard can check the runner actually GATES that key on this flag.
    artefact: Optional[str] = None
    soundness: str = SOUND


#: The 5 modes, each with the artefact its detection reads.
MODES: tuple[Mode, ...] = (
    Mode("models_were_declared", _models_declared,
         "the recorded argv: `--models` means declared, neither it nor `--config` "
         "means defaults were used, and `--config` alone is undecidable because "
         "the file's contents are not in the report",
         artefact="_declared_argv", soundness=SOUND),
    Mode("location_keyed_convergence",
         lambda r: _gating_flag(r, "location_crit_series_is_gating"),
         "no sound artefact: the candidate key is a copy of the flag, and "
         "`gamma_gate_series` is a hardcoded literal that cannot show the "
         "substitution this mode performs on the gate's input",
         artefact="location_crit_series_is_gating", soundness=CIRCULAR),
    Mode("hierarchical_novelty_convergence",
         lambda r: _gating_flag(r, "hierarchical_crit_series_is_gating"),
         "no sound artefact: the candidate key is a copy of the flag",
         artefact="hierarchical_crit_series_is_gating", soundness=CIRCULAR),
    Mode("severity_spec_enabled", _severity_spec_operating,
         "no sound artefact: `severity_admissibility` is stamped into every "
         "report whether or not the mode is on",
         artefact="severity_admissibility", soundness=UNGATED),
    Mode("sk_score_prose_listings", _sk_operating,
         "no artefact of any kind reaches the report",
         artefact=None, soundness=ABSENT),
)


def unsound_modes() -> list[Mode]:
    """The modes whose effect NO archived report can witness.

    This is the substance of what entry B28 found, and it is deliberately
    callable rather than written only in prose: 4 of the 5 modes cannot be
    reconciled at all until the runner records their EFFECT, and anyone adding a
    detector is told which kinds of artefact do not count.
    """
    return [m for m in MODES if m.soundness != SOUND]


@dataclass(frozen=True)
class Finding:
    mode: str
    declared: Optional[bool]
    operating: Optional[bool]
    verdict: str
    basis: str
    note: str = ""

    def as_dict(self) -> dict:
        return {"mode": self.mode, "declared": self.declared,
                "operating": self.operating, "verdict": self.verdict,
                "basis": self.basis, "note": self.note}


def reconcile(report: dict, declared_config: dict | None = None) -> list[Finding]:
    """Compare each mode's declaration against whether it was operating.

    Decides nothing about the run. Returns one Finding per mode, including the
    UNDECIDABLE ones, because a mode that could not be checked must appear in the
    record rather than be omitted -- an omission reads as agreement.
    """
    dc = declared_config
    if dc is None:
        dc = report.get("_declared_config")
    dc = dc if isinstance(dc, dict) else {}

    out: list[Finding] = []
    for mode in MODES:
        declared = _truthy_or_none(dc.get(mode.name))
        try:
            operating = mode.detect(report)
        except Exception as exc:                                   # noqa: BLE001
            out.append(Finding(mode.name, declared, None, UNDECIDABLE, mode.basis,
                               f"the detector raised {type(exc).__name__}: {exc}"))
            continue

        if declared is None and operating is None:
            note = ("neither the declaration nor the run's output could be read, so "
                    "nothing about this mode is established")
            verdict = UNDECIDABLE
        elif declared is None:
            note = ("the declared value could not be read -- it is absent or "
                    "withheld -- so agreement cannot be judged even though the run's "
                    "output could be read")
            verdict = UNDECIDABLE
        elif operating is None:
            note = ("the run's output does not answer whether this mode operated; "
                    "when a mode is off its artefacts are absent, and absence cannot "
                    "distinguish off from on-but-broken")
            verdict = UNDECIDABLE
        elif declared == operating:
            note = "the declaration and the run's own output agree"
            verdict = AGREE
        elif declared and not operating:
            note = ("DECLARED BUT NOT OPERATING: the run was told to use this mode "
                    "and its output shows the mode did not take effect. This is the "
                    "silent downgrade his ruling targets")
            verdict = DECLARED_NOT_OPERATING
        else:
            note = ("OPERATING BUT NOT DECLARED: the mode took effect without being "
                    "asked for, so the run did something the record does not explain")
            verdict = OPERATING_NOT_DECLARED
        out.append(Finding(mode.name, declared, operating, verdict, mode.basis, note))
    return out


def disagreements(findings: list[Finding]) -> list[Finding]:
    return [f for f in findings
            if f.verdict in (DECLARED_NOT_OPERATING, OPERATING_NOT_DECLARED)]


def as_report_field(findings: list[Finding]) -> dict:
    return {
        "modes": [f.as_dict() for f in findings],
        "disagreements": [f.mode for f in disagreements(findings)],
        "undecidable": [f.mode for f in findings if f.verdict == UNDECIDABLE],
    }


def summarise(findings: list[Finding]) -> list[str]:
    """Lines for the run log. Disagreements first, because they are the point."""
    lines = []
    for f in disagreements(findings):
        lines.append(f"★ MODE DISAGREEMENT {f.mode}: declared={f.declared} "
                     f"operating={f.operating} -- {f.note}")
    undec = [f.mode for f in findings if f.verdict == UNDECIDABLE]
    if undec:
        lines.append(f"  modes that could not be checked: {', '.join(undec)}")
    agreed = [f.mode for f in findings if f.verdict == AGREE]
    if agreed:
        lines.append(f"  modes where declaration and output agree: {', '.join(agreed)}")
    return lines
