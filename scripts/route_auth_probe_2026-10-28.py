#!/usr/bin/env python3
r"""Probe the routes a dispatch will ACTUALLY use, before the work starts.

HIS INSTRUCTION, 2026-10-28, verbatim: *"We should make a policy that Claude CLI
and all other model logins (when running in multi-vendor paid mode), should be
checked first before beginning any substantial body of work. If not a loud alert
should be issued to do so. Then I won't come back and find a large body of work I
thought I had authorised hadn't been done because of a simple failed re-auth."*

WHAT IT COST TO LEARN: on 2026-10-28 the CLI's OAuth session had expired before he
authorised a night's work. The panel review and the simulated run were both
blocked, and so were 30 of the 36 open work-remaining items, which are reviews he
had asked for. The aliveness probe in the panel dispatcher caught it, but only at
DISPATCH -- after a 19,888-character brief had been written.

HIS FOLLOW-UP QUESTION, AND IT IS THE DESIGN: *"But how does this solve needing to
run a similar probe during free reviews and simulated runs? The probe would need
to still function and to discern between the two conditions I think."*

HE IS RIGHT, AND THE ANSWER IS NOT A MODE FLAG. A mode flag is a second
description of a fact the roster already carries, and 2 descriptions of 1 rule
drift apart -- the defect class this project has measured more often than any
other. So this probes THE ROUTES THE ROSTER NAMES, nothing more:

  * a free panel and a simulated run both dispatch through `claude -p`, so the
    local CLI probe covers them, and that is the case that actually bit;
  * a paid dispatch names at least 1 seat whose route is not `claude_cli`, and
    only then does an outbound probe fire.

So "free" and "paid" are not conditions the probe has to tell apart. They are
different route sets, and the route set is read from the roster the dispatch is
about to use. There is no flag to set wrongly.

HIS RULING ON THE OUTBOUND PROBES, 2026-10-28: *"Run the probe when a paid
dispatch has been authorised, as you suggest."* So an outbound probe fires only
for a route the roster names, never speculatively.

PROBE, DO NOT PARSE -- AND THIS IS THE HALF WITH A MEASURED PRECEDENT. The
tempting cheap check is to look for a credential in `.env`. Measured 2026-10-28,
a line-initial parse of that file sees 2 of its 9 declarations and would report 7
PRESENT keys as missing: 0.777778, Wilson [0.452589, 0.936775],
Clopper-Pearson [0.399906, 0.971855] agreeing across statsmodels, scipy and an
independent mpmath bisection to 0.000e+00. The cause is the `export ` prefix, and
that is EXACTLY the bug that produced a false "keys absent" alarm on 2026-07-08,
recorded in ONBOARDING as "a parser bug, not a missing credential". So presence is
never inferred from a file: a route is asked whether it answers.

EVERY PROBE IS FREE. `claude auth status` is local and makes no network call.
OpenRouter's key endpoint and DeepSeek's balance endpoint return account metadata
and run no inference, so neither consumes tokens or credit. That is this project's
standing rule that a capability check must never cost money.

A FAILED PROBE IS NOT A SILENT FAILURE. The exit code is non-zero and the reason
names the route, the remedy and who can apply it -- `claude login` is interactive
and only the founder can run it.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import urllib.error
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[1]

#: Free metadata endpoints. Neither runs inference, so neither costs anything.
#: Keyed by the vendor a route belongs to, not by the seat name, because several
#: seats share one vendor and one probe answers for all of them.
VENDOR_PROBES = {
    "openrouter": ("https://openrouter.ai/api/v1/key", "OPENROUTER_API_KEY",
                   "Bearer"),
    "deepseek": ("https://api.deepseek.com/user/balance", "DEEPSEEK_API_KEY",
                 "Bearer"),
}

#: Which vendor a dispatcher route belongs to. `claude_cli` is local and has no
#: vendor endpoint; it is probed with the CLI's own status command.
ROUTE_VENDOR = {
    "openrouter": "openrouter",
    "deepseek": "deepseek",
    "claude_cli": None,
}


def env_from_dotenv() -> dict:
    """Read `.env` the way the runners do, honouring `export `.

    NOT used to decide whether a credential is valid -- only to supply the value
    a probe will present. The 2026-07-08 precedent is why this exists as a
    separate, clearly-labelled step rather than as the check itself.
    """
    out = {}
    p = REPO / ".env"
    if not p.is_file():
        return out
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("export "):
            s = s[len("export "):].strip()
        if "=" not in s:
            continue
        k, v = s.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def probe_claude_cli(timeout: int = 30) -> dict:
    """Local, free, no network. The route every free seat and every simulated
    run uses, and the one that failed on 2026-10-28."""
    try:
        r = subprocess.run(["claude", "auth", "status"], capture_output=True,
                           text=True, timeout=timeout)
    except FileNotFoundError:
        return {"route": "claude_cli", "ok": False,
                "why": "the `claude` CLI is not on PATH",
                "remedy": "install Claude Code, or correct PATH"}
    except subprocess.TimeoutExpired:
        return {"route": "claude_cli", "ok": False,
                "why": f"`claude auth status` did not answer in {timeout}s",
                "remedy": "retry; if it persists the CLI is wedged"}
    text = (r.stdout or "") + (r.stderr or "")
    try:
        data = json.loads(r.stdout)
    except (ValueError, TypeError):
        data = {}
    logged_in = bool(data.get("loggedIn"))
    if logged_in:
        return {"route": "claude_cli", "ok": True,
                "method": data.get("authMethod"), "why": "logged in"}
    why = "the CLI reports loggedIn false"
    if "OAuth session expired" in text:
        why = "the OAuth session expired and could not be refreshed"
    return {"route": "claude_cli", "ok": False, "why": why,
            "remedy": "run `claude login` -- it is interactive and opens a "
                      "browser, so only the founder can do it"}


def probe_vendor(vendor: str, env: dict, timeout: int = 20) -> dict:
    """An outbound call to a FREE metadata endpoint. Fires only for a vendor the
    roster actually names, per his ruling of 2026-10-28."""
    url, var, scheme = VENDOR_PROBES[vendor]
    key = os.environ.get(var) or env.get(var)
    if not key:
        return {"route": vendor, "ok": False,
                "why": f"{var} is set neither in the environment nor in .env",
                "remedy": f"add {var} to .env in `export {var}=...` form"}
    req = urllib.request.Request(url, headers={
        "Authorization": f"{scheme} {key}",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = resp.getcode()
            body = resp.read(2048).decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        return {"route": vendor, "ok": False,
                "why": f"the {vendor} metadata endpoint returned HTTP {e.code}",
                "remedy": f"the {var} in .env is rejected; replace it"}
    except Exception as e:                                     # noqa: BLE001
        return {"route": vendor, "ok": False,
                "why": f"could not reach {vendor}: {type(e).__name__}: {e}",
                "remedy": "check connectivity; this is not a credential fault"}
    #: NEVER echo the body. It carries account metadata and, on some vendors, a
    #: truncated key. Only the status and a shape check reach the caller.
    return {"route": vendor, "ok": code == 200, "http": code,
            "why": "the endpoint accepted the credential" if code == 200
                   else f"unexpected HTTP {code}",
            "metadata_bytes": len(body)}


def routes_for(seats: list) -> list:
    """The route set a roster implies, deduplicated and ordered.

    `seats` is a list of (name, model, route) tuples, exactly the shape
    `bench/confer_maths_panel_2026-09-05.py` holds in MODELS, so this reads the
    roster the dispatch will use rather than a second copy of it.
    """
    seen, out = set(), []
    for s in seats:
        route = s[2] if isinstance(s, (list, tuple)) and len(s) >= 3 else str(s)
        if route not in seen:
            seen.add(route)
            out.append(route)
    return out


def probe_routes(seats: list, allow_outbound: bool = True) -> dict:
    """Probe exactly the routes the roster names. The whole design, in 1 call."""
    env = env_from_dotenv()
    results, skipped = [], []
    for route in routes_for(seats):
        vendor = ROUTE_VENDOR.get(route, route)
        if vendor is None:
            results.append(probe_claude_cli())
        elif vendor in VENDOR_PROBES:
            if allow_outbound:
                results.append(probe_vendor(vendor, env))
            else:
                skipped.append(route)
        else:
            results.append({"route": route, "ok": False,
                            "why": f"no probe is defined for route {route!r}",
                            "remedy": "add one to VENDOR_PROBES, or correct the "
                                      "roster"})
    bad = [r for r in results if not r.get("ok")]
    return {"probed": results, "skipped_outbound": skipped,
            "all_ok": not bad, "failures": bad}


def _free_roster() -> list:
    """The 2 free seats, as the panel dispatcher defines them."""
    return [("cc2", "opus", "claude_cli"), ("fable", "fable", "claude_cli")]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Probe the model routes a dispatch will use, before it runs.")
    ap.add_argument("--routes", default="claude_cli",
                    help="comma-separated routes to probe (default: claude_cli, "
                         "which is what every free panel and simulated run uses)")
    ap.add_argument("--no-outbound", action="store_true",
                    help="skip vendor endpoints even if the route set names them")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    seats = [("seat", "model", r.strip()) for r in a.routes.split(",") if r.strip()]
    res = probe_routes(seats, allow_outbound=not a.no_outbound)
    if a.json:
        print(json.dumps(res, indent=2))
    else:
        print("== route authentication probe ==")
        for r in res["probed"]:
            mark = "OK  " if r.get("ok") else "FAIL"
            print(f"   {mark} {r['route']}: {r['why']}")
            if not r.get("ok") and r.get("remedy"):
                print(f"        remedy: {r['remedy']}")
        for s in res["skipped_outbound"]:
            print(f"   SKIP {s}: outbound probe suppressed by --no-outbound")
        if res["all_ok"]:
            print("   every route the roster names is authenticated.")
        else:
            print(f"\n   *** {len(res['failures'])} ROUTE(S) NOT AUTHENTICATED. "
                  f"Work dispatched through them will not run. ***")
    return 0 if res["all_ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
