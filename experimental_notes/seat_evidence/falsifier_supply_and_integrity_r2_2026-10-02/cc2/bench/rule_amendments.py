# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'falsifier_supply_and_integrity_r2_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: e77d451d0b31e008fb068c154f5472c5ad3e4bdb8bfdac73066d7dc7a3971bd3
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The committed RULE-AMENDMENTS REGISTER, and the predicate it reconstructs.

THE DEFECT THIS CLOSES (2026-10-02). `scripts/panel_brief_validate.py` accepts
an ARCHIVED declared figure only if it RE-EXECUTES as of the brief's own date,
via the producer's `--as-of`. That pins the DENOMINATOR -- the corpus as it
stood -- and it cannot absorb a NUMERATOR change caused by a RULE change. The
round-11 brief of 2026-09-11 declares `real-rejection rate : 2/640 = 0.3125%`;
the founder's ruling of 2026-10-02 narrowed `bench/falsifier_verify.py`'s
pre-execution key gate to ACCESS-ONLY, one archived falsifier left the
real-rejection set, and as-of 2026-09-11 the producer now prints 1/640. The
corpus is identical; the rule moved under the record.

Neither horn of that dilemma is taken. The brief is NOT edited -- editing it
falsifies the record of what the seats were given -- and archived briefs are
NOT exempted. Instead `--as-of` now pins the RULE SET as well as the corpus:
this module reads the register, finds every amendment dated AFTER the figure's
date, and reconstructs the superseded predicate from rule tuples that are STILL
COMMITTED in the amended module. Nothing is re-implemented, so a "historical"
scan cannot drift from the history it claims.

IT CANNOT BE USED TO LAUNDER AN EDIT, and that is the property worth most here.
A register that could say "this figure is different now" without saying WHAT it
was and WHAT it became would be a worse hole than the one it fills. So:

  * every affected figure must carry `superseded_value` AND `replacement_value`;
  * they must DIFFER (a record that changes nothing is not an amendment);
  * `verify_register` EXECUTES the producer under both rule sets and refuses the
    register if either recorded value is not what the code actually prints;
  * every failure here RAISES. A malformed register does not fall back to the
    current rule set quietly; it makes the producer exit non-zero, which makes
    `_historical_reproduction` return None, which REFUSES the brief. Fail closed.

REACHED BY A CALLER, as the additive standard's symmetric half requires:
`scripts/archived_falsifier_rejections_2026-09-10.py` consults it on every
`--as-of` run, and `scripts/panel_brief_validate.py` reaches it through that
producer when it re-executes an archived figure. Executed by
`bench/tests/test_rule_amendments_register_2026-10-02.py`.
"""
from __future__ import annotations

import datetime
import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
REGISTER = REPO / "bench" / "rule_amendments.json"

SCHEMA = "cdsfl.rule_amendments/1"

_DATE = re.compile(r"^20\d\d-\d\d-\d\d$")

#: Fields every affected-figure record must carry, non-empty. `superseded_value`
#: and `replacement_value` are both REQUIRED: the register exists to record what
#: a rule change did to a number, and a record that names only one of the two
#: values is the laundering shape this guard refuses.
_FIGURE_FIELDS = ("label", "producer", "brief", "as_of",
                  "superseded_value", "replacement_value")


class RegisterError(RuntimeError):
    """The register is unusable. Raised, never swallowed: a brief whose
    historical figure depends on an unloadable register must be REFUSED, not
    accepted under whatever rules happen to be in force today."""


def _date(value: str, what: str) -> datetime.date:
    if not isinstance(value, str) or not _DATE.match(value):
        raise RegisterError(f"{what}: {value!r} is not a YYYY-MM-DD date")
    try:
        return datetime.date.fromisoformat(value)
    except ValueError as exc:
        raise RegisterError(f"{what}: {value!r} is not a real date ({exc})")


def load_register(path: pathlib.Path | str = REGISTER) -> tuple[dict, ...]:
    """Every amendment, validated. Raises RegisterError on anything malformed.

    Validation is deliberately strict and deliberately NOT advisory. A register
    is an acceptance oracle for archived figures; a half-filled record in it
    would let an amendment move a number with no account of the move.
    """
    path = pathlib.Path(path)
    if not path.is_file():
        raise RegisterError(f"the rule-amendments register is missing: {path}")
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise RegisterError(f"{path} does not parse as JSON: {exc}")
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        raise RegisterError(
            f"{path}: schema is {doc.get('schema') if isinstance(doc, dict) else doc!r}, "
            f"expected {SCHEMA!r}")
    amendments = doc.get("amendments")
    if not isinstance(amendments, list) or not amendments:
        raise RegisterError(
            f"{path}: 'amendments' is empty or missing. An EMPTY register is "
            f"not a valid state once a rule has been amended -- it is the "
            f"bypass this file exists to prevent. Remove the file to assert "
            f"that no rule has ever been amended")
    seen: set[str] = set()
    out: list[dict] = []
    for i, a in enumerate(amendments):
        where = f"{path}: amendment {i}"
        if not isinstance(a, dict):
            raise RegisterError(f"{where} is not an object")
        aid = a.get("id")
        if not isinstance(aid, str) or not aid.strip():
            raise RegisterError(f"{where}: 'id' is missing or empty")
        if aid in seen:
            raise RegisterError(f"{path}: amendment id {aid!r} appears twice")
        seen.add(aid)
        where = f"{path}: amendment {aid}"
        a_date = _date(a.get("date"), f"{where} 'date'")
        if not str(a.get("rule_changed") or "").strip():
            raise RegisterError(
                f"{where}: 'rule_changed' is missing. An amendment with no "
                f"statement of what changed is a bare permission slip")
        pred = a.get("old_predicate")
        if not isinstance(pred, dict):
            raise RegisterError(f"{where}: 'old_predicate' is missing")
        for field in ("module", "callable"):
            if not str(pred.get(field) or "").strip():
                raise RegisterError(
                    f"{where}: 'old_predicate.{field}' is missing -- the OLD "
                    f"predicate must be IDENTIFIED, or it cannot be rebuilt")
        tuples = pred.get("restored_rule_tuples")
        if (not isinstance(tuples, list) or not tuples
                or not all(isinstance(t, str) and t.strip() for t in tuples)):
            raise RegisterError(
                f"{where}: 'old_predicate.restored_rule_tuples' must name at "
                f"least 1 rule tuple still committed in "
                f"{pred.get('module')!r}; the superseded predicate is rebuilt "
                f"from the real code, never re-implemented here")
        figures = a.get("affected_figures")
        if not isinstance(figures, list) or not figures:
            raise RegisterError(
                f"{where}: 'affected_figures' is empty. An amendment that "
                f"affects no declared figure does not belong in this register")
        for j, f in enumerate(figures):
            fwhere = f"{where} figure {j}"
            if not isinstance(f, dict):
                raise RegisterError(f"{fwhere} is not an object")
            for field in _FIGURE_FIELDS:
                if not str(f.get(field) or "").strip():
                    raise RegisterError(
                        f"{fwhere}: {field!r} is missing or empty. BOTH the "
                        f"superseded value and the replacement value are "
                        f"required: a register that records a rule change "
                        f"without recording what it did to the number is a "
                        f"way to launder an edit, which is exactly what this "
                        f"register must not become")
            f_date = _date(f.get("as_of"), f"{fwhere} 'as_of'")
            if f_date >= a_date:
                raise RegisterError(
                    f"{fwhere}: as_of {f['as_of']} is not BEFORE the "
                    f"amendment date {a['date']}. A figure measured on or "
                    f"after the amendment was produced under the new rule and "
                    f"needs no historical reconstruction")
            if f["superseded_value"].strip() == f["replacement_value"].strip():
                raise RegisterError(
                    f"{fwhere}: superseded_value and replacement_value are "
                    f"identical ({f['superseded_value']!r}). Then the rule "
                    f"change did not move this figure and listing it here "
                    f"would buy old-rule treatment for a figure that never "
                    f"needed it")
        out.append(a)
    return tuple(out)


def amendments_after(as_of: str,
                     path: pathlib.Path | str = REGISTER) -> tuple[dict, ...]:
    """Amendments enacted strictly AFTER `as_of`, i.e. not yet in force then.

    Missing register means no rule has ever been amended, which is a legitimate
    state (a fresh clone of a project that has never amended one). A register
    that EXISTS and is malformed is not.
    """
    if not pathlib.Path(path).is_file():
        return ()
    cut = _date(as_of, "as-of")
    return tuple(a for a in load_register(path)
                 if datetime.date.fromisoformat(a["date"]) > cut)


def restored_rules(as_of: str, path: pathlib.Path | str = REGISTER):
    """The rule tuples that were in force at `as_of` and have since been cut.

    Read from the amended module BY NAME. If a named tuple has been deleted the
    register is stale and this RAISES -- a superseded predicate that can no
    longer be rebuilt must stop the re-execution, not be silently skipped.
    """
    import importlib
    rules: list[tuple] = []
    for a in amendments_after(as_of, path):
        pred = a["old_predicate"]
        try:
            mod = importlib.import_module(pred["module"])
        except ImportError as exc:
            raise RegisterError(
                f"amendment {a['id']}: cannot import {pred['module']!r}: {exc}")
        if not hasattr(mod, pred["callable"]):
            raise RegisterError(
                f"amendment {a['id']}: {pred['module']}.{pred['callable']} no "
                f"longer exists, so the amended predicate cannot be identified")
        for name in pred["restored_rule_tuples"]:
            got = getattr(mod, name, None)
            if not got:
                raise RegisterError(
                    f"amendment {a['id']}: {pred['module']}.{name} is gone or "
                    f"empty, so the SUPERSEDED predicate can no longer be "
                    f"rebuilt and no figure dated before {a['date']} can be "
                    f"re-executed under it")
            rules.extend(tuple(got))
    return tuple(rules)


def rule_set_note(as_of: str, path: pathlib.Path | str = REGISTER) -> str:
    """One loud line naming the rule set `--as-of` just pinned."""
    after = amendments_after(as_of, path)
    if not after:
        return (f"rule set            : current (no amendment in the register "
                f"post-dates {as_of})")
    ids = ", ".join(a["id"] for a in after)
    n = len(restored_rules(as_of, path))
    return (f"rule set            : AS OF {as_of} -- {n} superseded rule(s) "
            f"restored by amendment(s) {ids}")


def scan_source_as_of(code: str, as_of: str,
                      path: pathlib.Path | str = REGISTER):
    """`scan_falsifier_source` as it behaved on `as_of`.

    STRICTLY ADDITIVE over the live gate: the current scanner runs unchanged and
    the superseded rule tuples are applied on top. So the historical predicate
    is always at least as strict as today's, which is the direction a narrowing
    amendment went, and the live gate is not touched by this module at all.
    """
    from bench.falsifier_verify import scan_falsifier_source
    violations = list(scan_falsifier_source(code))
    if not code:
        return violations
    for pattern, reason in restored_rules(as_of, path):
        m = pattern.search(code)
        if m and (reason, m.group(0)[:200]) not in violations:
            violations.append((reason, m.group(0)[:200]))
    return violations


_RATE = re.compile(r"^\s*(real-rejection rate : .+?)\s*$", re.M)


def _producer_figure(producer: pathlib.Path, as_of: str, rules: str) -> str:
    r = subprocess.run(
        [sys.executable, str(producer), "--as-of", as_of, "--rules", rules],
        cwd=REPO, capture_output=True, text=True, timeout=1800)
    if r.returncode != 0:
        raise RegisterError(
            f"{producer.name} --as-of {as_of} --rules {rules} exited "
            f"{r.returncode}:\n{(r.stdout + r.stderr)[-800:]}")
    m = _RATE.search(r.stdout)
    if not m:
        raise RegisterError(
            f"{producer.name} --as-of {as_of} --rules {rules} printed no "
            f"'real-rejection rate :' line")
    return m.group(1)


def verify_register(path: pathlib.Path | str = REGISTER) -> list[str]:
    """EXECUTE every record. Empty list means the register tells the truth.

    This is the anti-laundering check, and it is a measurement rather than a
    schema assertion. For each affected figure the producer is run twice over
    the SAME corpus: under the restored rule set, which must print the
    SUPERSEDED value, and under the current rule set, which must print the
    RECORDED REPLACEMENT value. So an amendment cannot claim a supersession
    that did not happen, and cannot record a replacement figure that the code
    does not produce.
    """
    problems: list[str] = []
    for a in load_register(path):
        for f in a["affected_figures"]:
            producer = (REPO / f["producer"]).resolve()
            if not producer.is_file():
                problems.append(
                    f"{a['id']}: producer {f['producer']} does not exist, so "
                    f"the figure cannot be re-executed under either rule set")
                continue
            old = _producer_figure(producer, f["as_of"], "as-of")
            new = _producer_figure(producer, f["as_of"], "current")
            if f["superseded_value"].strip() not in old:
                problems.append(
                    f"{a['id']}: the register says the superseded value was "
                    f"{f['superseded_value']!r}, but under the restored rule "
                    f"set the producer prints {old!r}")
            if f["replacement_value"].strip() not in new:
                problems.append(
                    f"{a['id']}: the register says the amendment replaced it "
                    f"with {f['replacement_value']!r}, but under the CURRENT "
                    f"rule set the producer prints {new!r}. An amendment may "
                    f"not record a replacement figure the code does not "
                    f"produce")
            if old.strip() == new.strip():
                problems.append(
                    f"{a['id']}: the restored and current rule sets print the "
                    f"same figure ({old!r}), so this record claims a "
                    f"supersession that did not occur")
    return problems


def main() -> int:
    try:
        amendments = load_register()
    except RegisterError as exc:
        print(f"rule-amendments: UNUSABLE — {exc}", file=sys.stderr)
        return 2
    for a in amendments:
        print(f"{a['id']}  {a['date']}")
        print(f"  rule changed      : {a['rule_changed']}")
        pred = a["old_predicate"]
        print(f"  old predicate     : {pred['module']}.{pred['callable']} "
              f"+ {', '.join(pred['restored_rule_tuples'])}")
        for f in a["affected_figures"]:
            print(f"  figure            : {f['label']} ({f['producer']}, "
                  f"as of {f['as_of']})")
            print(f"    superseded      : {f['superseded_value']}")
            print(f"    replaced by     : {f['replacement_value']}")
    problems = verify_register()
    for p in problems:
        print(f"rule-amendments: FAILS — {p}", file=sys.stderr)
    print(f"\nrule-amendments: {len(amendments)} amendment(s), "
          f"{'VERIFIED by execution' if not problems else 'REFUSED'}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
