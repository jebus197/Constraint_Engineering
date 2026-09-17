"""Every code path that pays a model seat either checks its brief or is on record as not.

TASK 5.2 CLAIMED A UNIVERSAL. It said the brief format is the standard for every
future paid review because "the dispatcher every paid review would use is the same
one the free rounds use". Panel round 16 (2026-09-17) checked the set rather than
the member: `bench/confer_maths_panel_2026-09-05.py` refuses a non-conforming
brief before any seat is reached, and 47 `bench/confer_*.py` files call a paid
transport, of which 1 references `panel_brief_validate`. 3 others read a
`BRIEF.md` off disk and send it to paid seats with no format check.

THE CHECK IS NOT PUT IN THE TRANSPORT, deliberately. `call_openrouter` and
`call_deepseek` in `bench/experiment_11_orchestrator.py` also carry ordinary
experiment prompts through `dispatch()`, so validating there would refuse
experiment runs.

WHAT THIS HOLDS. The population is COMPUTED, by parsing every tracked `.py` under
bench/ and scripts/ (tests and logs excluded) for a call to `call_openrouter`,
`call_deepseek` or `call_openrouter_with_tools`. Each member must either
(a) import `validate` and `check_declared_figures` from `panel_brief_validate` and
reach both from its entry point in a statement before the first statement that
reaches a paid transport, or (b) appear in
`bench/directives/universal/unvalidated_paid_dispatchers.json` with a reason. The
registry records which members read a `BRIEF.md`, so the 3 brief readers stand as
named, open exemptions rather than disappearing into a count. A new paid
dispatcher with neither goes red; a registered file that no longer needs its entry
goes red until the entry is removed.

WHAT IT CANNOT SEE, stated. It is static, because running a paid dispatcher to
test it spends money. "Before" is statement order in the entry point, following
calls and function references within the same file only. It does not check that
the text validated is the text sent. And "reads a BRIEF.md" means a string
constant naming `BRIEF.md`; a dispatcher reading a brief under another name is
counted as building its prompt in code.
"""
from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "bench" / "directives" / "universal" / "unvalidated_paid_dispatchers.json"
PANEL = "bench/confer_maths_panel_2026-09-05.py"
BRIEF_READERS_FOUND_2026_09_17 = (
    "bench/confer_enforcement_prose_pr_2026-08-19.py",
    "bench/confer_stage1_audit_pr_2026-08-18.py",
    "bench/confer_track_record_pr_2026-08-22.py",
)
TRANSPORTS = frozenset({"call_openrouter", "call_deepseek", "call_openrouter_with_tools"})
VALIDATORS = frozenset({"validate", "check_declared_figures"})


def _called(node: ast.AST) -> "str | None":
    f = node.func if isinstance(node, ast.Call) else None
    return None if f is None else (getattr(f, "id", None) or getattr(f, "attr", None))


def _validates_before_paying(tree: ast.Module) -> bool:
    aliases = {a.asname or a.name: a.name
               for n in ast.walk(tree)
               if isinstance(n, ast.ImportFrom) and n.module == "panel_brief_validate"
               for a in n.names}
    if not VALIDATORS <= set(aliases.values()):
        return False
    funcs = {n.name: n for n in ast.walk(tree)
             if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}

    memo: dict[str, tuple[frozenset, bool]] = {}

    def reach(node: ast.AST, stack: frozenset = frozenset()) -> tuple[frozenset, bool]:
        validators, pays = set(), False
        for n in ast.walk(node):
            name = _called(n)
            if name in TRANSPORTS:
                pays = True
            if name in aliases and aliases[name] in VALIDATORS:
                validators.add(aliases[name])
            ref = n.id if isinstance(n, ast.Name) else None
            if ref in funcs and ref not in stack and funcs[ref] is not node:
                if ref not in memo:
                    memo[ref] = reach(funcs[ref], stack | {ref})
                v, p = memo[ref]
                validators |= v
                pays = pays or p
        return frozenset(validators), pays

    if "main" in funcs:
        entry = funcs["main"].body
    else:
        entry = [s for s in tree.body
                 if not isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    seen: set = set()
    for stmt in entry:
        v, p = reach(stmt)
        if p:
            return VALIDATORS <= seen
        seen |= v
    return False


def facts(src: str) -> "dict | None":
    """None if the source calls no paid transport; else what the guard needs."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    if not any(_called(n) in TRANSPORTS for n in ast.walk(tree)):
        return None
    return {
        "reads_brief": any(isinstance(n, ast.Constant) and isinstance(n.value, str)
                           and "BRIEF.md" in n.value for n in ast.walk(tree)),
        "validates": _validates_before_paying(tree),
    }


def tracked_python() -> list[str]:
    """Tracked files, plus untracked ones git does not ignore, so a new dispatcher
    is seen before it is committed rather than after."""
    r = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard",
                        "--", "bench", "scripts"], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        pytest.skip("the population is computed from git's file list; this is not a "
                    "git checkout, and an empty population would pass anything")
    return sorted({f for f in r.stdout.split()
                   if f.endswith(".py") and not f.startswith(("bench/tests/", "bench/logs/"))
                   and (ROOT / f).is_file()})


def population(root: Path, files: list[str]) -> dict[str, dict]:
    out = {}
    for f in files:
        got = facts((root / f).read_text(encoding="utf-8", errors="replace"))
        if got is not None:
            out[f] = got
    return out


def unregistered(pop: dict[str, dict], registry: dict[str, dict]) -> list[str]:
    return sorted(f for f, v in pop.items() if not v["validates"] and f not in registry)


def _registry() -> dict[str, dict]:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))["entries"]


@pytest.fixture(scope="module")
def live():
    return population(ROOT, tracked_python())


class TestThePopulationIsComputed:
    def test_it_is_not_vacuous(self, live):
        assert PANEL in live, f"{PANEL} is no longer seen calling a paid transport"
        assert len(live) >= 40, f"only {len(live)} paid dispatchers found"

    def test_the_panel_dispatcher_validates_before_it_pays(self, live):
        """POSITIVE CONTROL on the 1 real validating dispatcher. If the static rule
        stopped recognising it, every check below would be reading a broken rule."""
        assert live[PANEL]["validates"], (
            f"{PANEL} no longer reaches validate and check_declared_figures before "
            f"its first paid call")
        assert live[PANEL]["reads_brief"]


class TestEveryPaidRouteIsAccountedFor:
    def test_every_paid_dispatcher_validates_or_is_registered(self, live):
        missing = unregistered(live, _registry())
        assert not missing, (
            f"{len(missing)} file(s) call a paid transport, do not check a brief "
            f"before paying, and are not in {REGISTRY.relative_to(ROOT)}: {missing}. "
            f"Validate the prompt with panel_brief_validate before the first paid "
            f"call, or register the file with the reason it does not.")

    def test_the_registry_has_no_slack(self, live):
        reg = _registry()
        stale = sorted(f for f in reg if f not in live or live[f]["validates"])
        assert not stale, (
            f"{stale} are registered as unvalidated paid dispatchers and no longer "
            f"are (gone, no longer paying, or now validating); remove them")
        unexplained = sorted(f for f, v in reg.items() if not str(v.get("reason", "")).strip())
        assert not unexplained, f"registered with no reason: {unexplained}"

    def test_brief_readers_are_recorded_as_brief_readers(self, live):
        """A file that reads a BRIEF.md and pays unchecked is the case the format
        ruling is about; it may not sit in the registry under a generic reason."""
        reg = _registry()
        computed = sorted(f for f, v in live.items() if v["reads_brief"] and not v["validates"])
        recorded = sorted(f for f, v in reg.items() if v.get("reads_brief"))
        assert computed == recorded, (computed, recorded)

    def test_the_3_found_on_2026_09_17_validate_or_stand_as_open_exemptions(self, live):
        reg = _registry()
        for f in BRIEF_READERS_FOUND_2026_09_17:
            assert f in live, f"{f} is gone or no longer pays; update this test deliberately"
            assert live[f]["validates"] or reg.get(f, {}).get("reads_brief"), f


class TestTheRuleDiscriminates:
    """CONTROLS on synthetic dispatchers, so the rule is shown to flag what it
    exists to flag and to pass what it exists to pass."""

    HEAD = ("from pathlib import Path\n"
            "from experiment_11_orchestrator import call_openrouter\n"
            "PROMPT = (Path('logs') / 'BRIEF.md').read_text()\n")
    PAY = "def dispatch():\n    return call_openrouter('m', 'sys', PROMPT)\n"
    CHECK = ("def check():\n"
             "    from panel_brief_validate import validate, check_declared_figures\n"
             "    if validate(PROMPT) + check_declared_figures(PROMPT):\n"
             "        raise SystemExit(2)\n")

    def _flag(self, tmp_path, src):
        (tmp_path / "bench").mkdir(exist_ok=True)
        (tmp_path / "bench" / "confer_x.py").write_text(src, encoding="utf-8")
        pop = population(tmp_path, ["bench/confer_x.py"])
        return pop["bench/confer_x.py"], unregistered(pop, {})

    def test_a_brief_reader_that_pays_unchecked_is_flagged(self, tmp_path):
        f, missing = self._flag(tmp_path, self.HEAD + self.PAY
                                + "def main():\n    dispatch()\n")
        assert f == {"reads_brief": True, "validates": False}
        assert missing == ["bench/confer_x.py"]

    def test_the_same_file_checking_first_is_not_flagged(self, tmp_path):
        f, missing = self._flag(tmp_path, self.HEAD + self.PAY + self.CHECK
                                + "def main():\n    check()\n    dispatch()\n")
        assert f["validates"] and missing == []

    def test_checking_after_paying_is_flagged(self, tmp_path):
        f, missing = self._flag(tmp_path, self.HEAD + self.PAY + self.CHECK
                                + "def main():\n    dispatch()\n    check()\n")
        assert not f["validates"] and missing == ["bench/confer_x.py"]

    def test_the_shape_check_alone_is_not_enough(self, tmp_path):
        half = self.CHECK.replace(", check_declared_figures", "").replace(
            " + check_declared_figures(PROMPT)", "")
        f, missing = self._flag(tmp_path, self.HEAD + self.PAY + half
                                + "def main():\n    check()\n    dispatch()\n")
        assert not f["validates"] and missing == ["bench/confer_x.py"]

    def test_a_paying_reference_through_a_pool_counts_as_paying(self, tmp_path):
        """`pool.submit(dispatch, ...)` passes the function without calling it,
        which is how the real panel dispatcher pays."""
        f, missing = self._flag(tmp_path, self.HEAD + self.PAY
                                + "def main(pool):\n    pool.submit(dispatch)\n")
        assert missing == ["bench/confer_x.py"]
        f2, missing2 = self._flag(tmp_path, self.HEAD + self.PAY + self.CHECK
                                  + "def main(pool):\n    check()\n    pool.submit(dispatch)\n")
        assert f2["validates"] and missing2 == []

    def test_a_file_that_pays_nothing_is_outside_the_population(self, tmp_path):
        (tmp_path / "bench").mkdir()
        (tmp_path / "bench" / "free.py").write_text(
            "from experiment_11_orchestrator import call_claude_cli\n"
            "call_claude_cli('opus', None, open('BRIEF.md').read())\n", encoding="utf-8")
        assert population(tmp_path, ["bench/free.py"]) == {}
