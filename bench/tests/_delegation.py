"""Follow a thin wrapper to the function it delegates to, for source-text guards.

WHY THIS EXISTS, MEASURED 2026-10-11
------------------------------------
On 2026-10-07, commit `46617574` split `_dispatch_single_model` into a 12-line
wrapper decorated with `@_records_seat_completion` delegating to a 77-line
`_dispatch_single_model_inner`. The behaviour moved; nothing was lost. But THREE
guards assert on the named function's unparsed source, so all three went red and
stayed red for 4 days:

  * test_sim_seam_covers_every_dispatch_2026-08-30 :: the_known_dispatchers_all_use_the_primitive
  * test_the_corrected_copy_ask_is_wired_2026-08-30 :: the_dispatch_path_reads_it
  * test_the_corrected_copy_ask_is_wired_2026-08-30 :: the_ask_without_the_gate_is_announced

Verified at 3 revisions by AST: at `46617574^` the function was 78 lines and held
`_ASK_CORRECTED_COPY`; at `46617574` it is 12 lines and holds neither that nor a
call to `dispatch_to_model`, while `_inner` holds `_ASK_CORRECTED_COPY`, the
"NO ask" announcement and the `dispatch_to_model` call. So the SYSTEM is sound and
the INSTRUMENTS were blind -- the `execute-do-not-grep` failure class for the 4th
time in this project.

THE FIX IS NOT TO LOOSEN THE ASSERTION. A guard that passes on an empty wrapper
would be vacuous. `delegated_source` returns the wrapper's source CONCATENATED
with its delegate's, so the assertion still requires the marker to exist
somewhere on the real dispatch path, and still fails if it is deleted from both.
Held by `test_the_delegation_resolver_is_not_vacuous_2026-10-11.py`.
"""
from __future__ import annotations

import ast
from typing import Iterable

#: Suffixes a wrapper's delegate conventionally carries in this repository.
_DELEGATE_SUFFIXES = ("_inner", "_impl", "_body")


def _named(tree: ast.AST, name: str):
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name:
            return n
    return None


def delegate_names(tree: ast.AST, name: str) -> list[str]:
    """Names `name` delegates to: a called function whose name extends its own."""
    fn = _named(tree, name)
    if fn is None:
        return []
    out = []
    for c in ast.walk(fn):
        if isinstance(c, ast.Call) and isinstance(c.func, ast.Name):
            cand = c.func.id
            if cand != name and cand.startswith(name) and cand.endswith(_DELEGATE_SUFFIXES):
                out.append(cand)
    return sorted(set(out))


def delegated_source(tree: ast.AST, name: str) -> str:
    """`name`'s unparsed source plus that of every function it delegates to.

    Transitive, so a wrapper delegating to a wrapper still resolves. Returns ""
    when `name` is absent, which keeps a renamed function a LOUD failure rather
    than a silent pass.
    """
    fn = _named(tree, name)
    if fn is None:
        return ""
    parts, seen, queue = [ast.unparse(fn)], {name}, list(delegate_names(tree, name))
    while queue:
        d = queue.pop(0)
        if d in seen:
            continue
        seen.add(d)
        sub = _named(tree, d)
        if sub is not None:
            parts.append(ast.unparse(sub))
            queue.extend(delegate_names(tree, d))
    return "\n".join(parts)


def callers_of(tree: ast.AST, callee: str, *, follow_delegation: bool = True) -> set[str]:
    """Every function whose own body, or its delegate's, calls `callee`.

    A wrapper is reported under the WRAPPER's name, because that is the name the
    rest of the runner refers to and the name a guard's expected-set records.

    BARE-NAME CALLS ONLY, AND THAT IS A TRAP WORTH NAMING. The match is
    `isinstance(c.func, ast.Name)`, so `obj.callee()` -- a METHOD call -- is
    NOT found. A guard that asks this whether a method is wired gets an empty
    set and reads it as "nothing calls it", which is a false negative of
    exactly the shape this module exists to prevent. It happened on 2026-10-12
    to the first version of
    bench/tests/test_the_severity_specification_shadow_2026-10-12.py, whose
    subject is a `FindingRegistry` method. Measured at the same time: all 3
    other call sites in the suite target module-level functions, so no existing
    guard is vacuous because of this. For a method, walk for `ast.Attribute`
    with the matching `.attr` instead.
    """
    direct: set[str] = set()
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for c in ast.walk(fn):
            if isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == callee:
                direct.add(fn.name)
    if not follow_delegation:
        return direct
    out = set(direct)
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if any(d in direct for d in delegate_names(tree, fn.name)):
                out.add(fn.name)
    return out
