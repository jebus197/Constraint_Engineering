#!/usr/bin/env python3
"""CDSFL Onboarding Script — interactive setup + dynamic info source.

Usage:
  python3 scripts/cdsfl_onboard.py              # Default overview + env checks
  python3 scripts/cdsfl_onboard.py --full       # Splice in the sv-written state block
  python3 scripts/cdsfl_onboard.py --dry-run    # Self-test only; exits 0 on success

`--full` exits non-zero if the state block could not be spliced. A `--full`
run that silently returns the default view is the defect this script carried
for 118 days; it must never come back.

Dual purpose. First, this script is a researcher's first contact with the
project: it checks environment, offers to install missing dependencies
with permission, and points to documentation. Second, it serves as a
live summary view of the project: canonical prose is read at runtime
from `resources/ONBOARDING.md` and `docs/REPRODUCING.md` rather than
hardcoded in this file. The `sv` and `qc` scripts verify that the
wiring remains intact.

Security. This script never uploads, transmits, or commits API keys,
private keys, or crypto wallet keys. The API-key section reads local
environment variables only to tell you which keys are present or
missing — key *values* are never printed, logged, or transmitted. If
a required key is missing, supply it yourself via `.env` or shell
export. Never commit `.env` or any file containing real key material
to git.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cdsfl_utils import latest_experiment, read_section, repo_root, source_env, test_count
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bench"))
import wolfram_standard as W  # noqa: E402


# ---------------------------------------------------------------------------
# Dependency definitions
# ---------------------------------------------------------------------------

# (import_name, pip_name, description)
CORE_PACKAGES = [
    ("anthropic", "anthropic", "Claude API client"),
    ("openai", "openai", "OpenAI/OpenRouter API client"),
    ("scipy", "scipy", "Scientific computing and statistics"),
    ("numpy", "numpy", "Numerical computing"),
    ("sympy", "sympy", "Symbolic mathematics and computer algebra"),
    ("pytest", "pytest", "Test framework"),
    ("google.genai", "google-genai", "Google Generative AI client"),
    ("statsmodels", "statsmodels", "Statistical modelling"),
    ("pydantic", "pydantic", "Data validation"),
    ("httpx", "httpx", "Async-capable HTTP client"),
    ("cryptography", "cryptography", "Cryptographic primitives"),
]

CODE_QUALITY_PACKAGES = [
    ("mypy", "mypy", "Static type checker"),
    ("ruff", "ruff", "Fast Python linter and formatter"),
    ("bandit", "bandit", "Security-focused linter"),
    ("coverage", "coverage", "Code coverage measurement"),
]

STEM_PACKAGES = [
    ("z3", "z3-solver", "Z3 SMT solver — formal verification (B Cell v2)"),
    ("uncertainties", "uncertainties", "Error propagation in calculations"),
    ("mpmath", "mpmath", "Arbitrary precision arithmetic"),
    # ADDED 2026-09-17 on the founder's ruling. `.claude/CLAUDE.md`'s Tool
    # Constraint Box names 21 imports; this script checked 7 of them, so a new
    # clone could pass onboarding and then fail the first dimensional or
    # chemical claim it met. The 4 stdlib entries (ast, difflib, dis, inspect)
    # need no check. These 10 are the remainder.
    ("pint", "pint", "Dimensional analysis and units — default for unit claims"),
    ("astropy", "astropy", "Physical constants, SI/CGS conversion"),
    ("pandas", "pandas", "Data frames and time-series aggregation"),
    ("networkx", "networkx", "Graph-theoretic claims — default for graph claims"),
    ("pulp", "PuLP", "Linear and integer programming"),
    ("crosshair", "crosshair-tool", "Symbolic execution via z3 — behavioural claims"),
    ("sklearn", "scikit-learn", "ML metric and model claims"),
    ("rdkit", "rdkit", "SMILES parsing — default for chemical structure claims"),
    ("Bio", "biopython", "Sequence validation — default for biological sequences"),
    ("matplotlib", "matplotlib", "Plotting"),
]

OPTIONAL_PACKAGES = [
    # RETIRED, kept visible rather than deleted: the key-authenticated Wolfram
    # Alpha API client was dropped on 2026-08-03 and NO key should be supplied
    # for it. Wolfram now reaches this project 2 ways, neither needing this
    # package: the local Engine through `wolframscript`, and the Wolfram
    # connector's tools inside the assistant's own session.
    ("wolframalpha", "wolframalpha", "RETIRED 2026-08-03 — do not install or key"),
    ("web3", "web3", "Ethereum/Web3 blockchain interaction"),
    ("PIL", "Pillow", "Image processing"),
]

# Panel roster of record: `.claude/CLAUDE.md` § Model Confer Dispatch, and the
# peer preflight `scripts/check_model_keys.py`. Corrected 2026-08-06 — the
# previous table still described the pre-2026-05-10 routing (Gemini on the
# direct Google API, required) and named DeepSeek Reasoner, a model DeepSeek no
# longer lists.
API_KEYS = {
    "OPENROUTER_API_KEY": (
        "Required",
        "Codex GPT-5.5, ChatGPT GPT-5.5 and Gemini 3.1 Pro Preview panel routes",
    ),
    "DEEPSEEK_API_KEY": (
        "Required",
        "DeepSeek V4 Pro (deepseek-v4-pro) via the DeepSeek direct API",
    ),
    "GEMINI_API_KEY": (
        "Optional",
        "Legacy direct-Google fallback — the panel has routed Gemini via "
        "OpenRouter since 2026-05-10",
    ),
    "GOOGLE_API_KEY": (
        "Optional",
        "Legacy direct-Google fallback under its alternate name",
    ),
    "OPENAI_API_KEY": ("Optional", "Direct OpenAI API access (not used by default runners)"),
    "GITHUB_TOKEN": ("Optional", "Push access to repository"),
}

# Credentialed routes are not the whole panel. Claude Opus (cc2) dispatches
# through the `claude` CLI on the Max subscription, and Wolfram now runs
# credential-free. Named here so a reader does not conclude those routes are
# broken merely because no key stands for them above.
UNCREDENTIALED_ROUTES = [
    "Claude Opus (cc2) — `claude` CLI piped mode on the Max subscription; no API key.",
    "Wolfram — local `wolframscript` on the Wolfram Engine, plus the hosted Wolfram "
    "connector authorised in the assistant's own session; no API key (the "
    "key-authenticated bridge was retired 2026-08-03, and the WolframCloud MCP "
    "entry was removed on 2026-09-10 because it had stopped connecting).",
]

SYSTEM_TOOLS = [
    ("git", "git", "Version control"),
    ("jq", "jq", "JSON processor"),
    ("gh", "gh", "GitHub CLI"),
]

MIN_PYTHON = (3, 13)

SV_START_MARKER = "<!-- SV:LATEST_EXP_START -->"
SV_END_MARKER = "<!-- SV:LATEST_EXP_END -->"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def print_header(text: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def ask(prompt: str, default: str = "n") -> bool:
    """Ask a yes/no question. Returns True for yes."""
    try:
        answer = input(f"  {prompt} [{'Y/n' if default == 'y' else 'y/N'}] ").strip().lower()
        if not answer:
            answer = default
        return answer in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        print()
        return False


def has_homebrew() -> bool:
    return shutil.which("brew") is not None


def install_homebrew() -> bool:
    """Install Homebrew with user permission."""
    print("  Homebrew is not installed. It is needed to install system tools")
    print("  and manage Python versions on macOS.")
    print()
    print("  Install command:")
    print('    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
    print()
    if ask("Install Homebrew now?"):
        result = subprocess.run(
            ["/bin/bash", "-c",
             '$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)'],
            check=False,
        )
        return result.returncode == 0
    return False


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_python() -> bool:
    """Check Python version and offer upgrade if needed."""
    v = sys.version_info
    ok = v >= MIN_PYTHON
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] Python {v.major}.{v.minor}.{v.micro}")

    if ok:
        return True

    print(f"         Requires Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+")
    print()

    # Check if 3.13 is available elsewhere on the system
    for candidate in ["python3.13", "python3.14"]:
        path = shutil.which(candidate)
        if path:
            print(f"  Found {candidate} at {path}")
            print(f"  Re-run this script with: {path} scripts/cdsfl_onboard.py")
            return False

    # Check /usr/local/bin
    for candidate in ["/usr/local/bin/python3.13", "/usr/local/bin/python3.14"]:
        if Path(candidate).exists():
            print(f"  Found Python at {candidate}")
            print(f"  Re-run this script with: {candidate} scripts/cdsfl_onboard.py")
            return False

    # Offer to install
    if platform.system() == "Darwin":
        if has_homebrew():
            print("  Python 3.13 can be installed via Homebrew:")
            print("    brew install python@3.13")
            if ask("Install Python 3.13 via Homebrew?"):
                subprocess.run(["brew", "install", "python@3.13"], check=False)
                print("  After installation, re-run: python3.13 scripts/cdsfl_onboard.py")
        else:
            print("  To install Python 3.13, you need Homebrew (or pyenv).")
            if install_homebrew():
                print("  Now install Python: brew install python@3.13")
                if ask("Install Python 3.13 now?"):
                    subprocess.run(["brew", "install", "python@3.13"], check=False)
    else:
        print("  Install Python 3.13+ via your system package manager or pyenv:")
        print("    pyenv install 3.13")

    return False


def check_packages(
    packages: list[tuple[str, str, str]],
    label: str,
) -> list[str]:
    """Check a group of packages. Returns list of missing pip names."""
    missing = []
    print(f"  {label}:")
    for module, pip_name, desc in packages:
        mod_check = module.split(".")[0]
        spec = importlib.util.find_spec(mod_check)
        status = "FOUND" if spec else "MISSING"
        print(f"    [{status}] {pip_name:20s} {desc}")
        if not spec:
            missing.append(pip_name)
    return missing


def check_system_tools() -> list[str]:
    """Check for system CLI tools."""
    missing = []
    print("  System tools:")
    for cmd, brew_name, desc in SYSTEM_TOOLS:
        path = shutil.which(cmd)
        status = "FOUND" if path else "MISSING"
        print(f"    [{status}] {cmd:20s} {desc}")
        if not path:
            missing.append(brew_name)
    return missing


def check_claude_code() -> bool:
    """Check if Claude Code CLI is available."""
    print("  Claude Code (CC2 dispatch):")

    # Check PATH
    claude_path = shutil.which("claude")
    if claude_path:
        print(f"    [FOUND] claude CLI at {claude_path}")
        return True

    # Check macOS app bundle
    app_support = Path.home() / "Library" / "Application Support" / "Claude"
    if app_support.exists():
        import glob as globmod
        patterns = [
            str(app_support / "claude-code" / "*" / "claude.app" / "Contents" / "MacOS" / "claude"),
            str(app_support / "claude-code-vm" / "*" / "claude"),
        ]
        for pattern in patterns:
            matches = sorted(globmod.glob(pattern), reverse=True)
            for match in matches:
                if os.path.isfile(match):
                    print(f"    [FOUND] claude CLI at {match}")
                    return True

    print("    [MISSING] Claude Code CLI")
    print("             Install Claude for Desktop from https://claude.ai/download")
    print("             A Max subscription is required for CC2 dispatch.")
    if ask("Open download page in browser?"):
        subprocess.run(["open", "https://claude.ai/download"], check=False)
    return False


def wolfram_kernel_path() -> str | None:
    """The Engine's kernel binary, if the app is installed."""
    for candidate in (
            "/Applications/Wolfram Engine.app/Contents/MacOS/WolframKernel",
            "/Applications/Wolfram.app/Contents/MacOS/WolframKernel",
            "/Applications/Mathematica.app/Contents/MacOS/WolframKernel"):
        if Path(candidate).is_file():
            return candidate
    return None


def stale_kernels() -> list[str]:
    """Wolfram kernel processes already running, from `ps`.

    `.claude/CLAUDE.md` requires this check BEFORE a licence message is read as a
    licence fault: on 2026-08-02 a second kernel spawned against the single-kernel
    licence made every call report "not activated", which it was not."""
    try:
        r = subprocess.run(["ps", "-axo", "pid=,command="], capture_output=True,
                           text=True, timeout=10)
    except Exception:
        return []
    return [line.strip() for line in (r.stdout or "").splitlines()
            if "MacOS/wolfram" in line or "WolframKernel" in line]


def wolfram_state(timeout: int = 120) -> str:
    """Does Wolfram actually COMPUTE here? Returns a state, never a guess.

    ABSENT        — `wolframscript` is not installed.
    NO_KERNEL     — installed, but it cannot locate a kernel to run.
    BUSY          — a kernel answered "Connection closed by WolframKernel" twice:
                    another caller holds the single-kernel licence.
    STALE_KERNEL  — a licence message, while kernel processes are already running;
                    a leftover kernel is the likely cause, not the licence.
    NOT_ACTIVATED — a licence message with no other kernel running.
    OK            — it evaluated 1+1 and returned 2.

    WHY THIS REPLACED A PATH CHECK (2026-09-15). The previous version reported
    `[FOUND] wolframscript` whenever the command existed. On 2026-09-14 that was
    true all evening while every call failed: the licence had expired on
    2026-09-11 without auto-renewing, and separately `wolframscript` could not
    locate a kernel at all. Presence is not capability, and a check that cannot
    tell them apart reports success during a total outage.

    RETRIED, AND 2 STATES ADDED, 2026-09-17 (Question 11). The first version
    classed kernel contention and a timeout as NO_KERNEL after 1 call, and then
    offered to reconfigure the kernel path, which is the wrong repair for both.
    It now goes through `wolfram_standard.run_local`, which retries once after a
    result that is not evidence.
    """
    script = shutil.which("wolframscript")
    if not script:
        return "ABSENT"
    # `runner=subprocess.run` is looked up NOW, so a test that replaces it is obeyed.
    r = W.run_local("Print[1+1]", timeout=timeout, runner=subprocess.run, script=script)
    out = (r["stdout"] + r["stderr"]).strip()
    # THE ANSWER IS NOT THE LAST LINE, MEASURED 2026-09-17 22:50 BST. `Print`
    # writes 2 and then RETURNS Null, so the real binary prints "2\nNull" and
    # this check -- which required "2" to be the final line -- classified a
    # KERNEL THAT COMPUTED CORRECTLY as NO_KERNEL, and then offered to
    # reconfigure a kernel path that was already right: the exact wrong repair
    # this function's docstring says it was rewritten to stop making. The
    # fixtures never caught it because they replied "2", a shape the binary does
    # not produce -- a producer and a consumer that disagreed while each
    # described itself consistently (`execute-do-not-grep`).
    if r["evidence"] and "2" in [line.strip() for line in out.splitlines()]:
        return "OK"
    low = out.lower()
    if "connection closed by wolframkernel" in low:
        return "BUSY"
    if "not activated" in low or "license" in low or "licence" in low:
        return "STALE_KERNEL" if stale_kernels() else "NOT_ACTIVATED"
    return "NO_KERNEL"


def wolfram_licence_warning(timeout: int = 60) -> str | None:
    """Read `$LicenseExpirationDate` and warn before it lapses.

    The Engine licence did not auto-renew on 2026-09-11 and was activated by hand
    on 2026-09-15, expiring 2026-10-08. When the kernel cannot say, the recorded
    date is used and the warning says so."""
    r = W.run_local("$LicenseExpirationDate", timeout=timeout, runner=subprocess.run,
                    script=shutil.which("wolframscript"))
    read = W.parse_licence_expiry(r["stdout"]) if r["evidence"] else None
    warning = W.licence_warning(read or W.RECORDED_LICENCE_EXPIRY)
    if warning and not read:
        warning += f" (date recorded on 2026-09-15; the kernel did not report one: {r['reason']})"
    return warning


def check_wolfram() -> str:
    """Report the Wolfram routes, and offer to repair the local one."""
    print("  Wolfram:")
    print("    [INFO] 2 routes, and they are not redundant. The local Engine")
    print("           runs Wolfram Language through `wolframscript` with no")
    print("           per-call limit. The Wolfram connector, authorised in the")
    print("           assistant's own session, adds natural-language queries and")
    print("           a cloud kernel.")
    print("    [POLICY] Wolfram is the SECOND falsifier, and it is never required.")
    print("           Founder ruling 2026-09-17: every model and every agent uses")
    print("           tools wherever possible, Wolfram included, but SymPy, z3,")
    print("           mpmath, SciPy, statsmodels and NumPy stay PRIMARY in every")
    print("           case. Nothing in this project depends on Wolfram, and the")
    print("           test suite passes on a machine that has never had it.")
    print("           Calls from seats and agents are queued through 1 kernel:")
    print("           bench/tools/wolfram_gate/serial, wired by wolfram_standard.")
    print("    [RETIRED] The key-authenticated Wolfram Local MCP Bridge was")
    print("              retired 2026-08-03. No key is needed and none should")
    print("              be supplied. Not a missing dependency.")

    state = wolfram_state()
    if state == "OK":
        print("    [OK] wolframscript evaluated 1+1 and returned 2.")
        warning = wolfram_licence_warning()
        if warning:
            print(f"    [RENEW] {warning}")
        return state

    if state == "BUSY":
        print("    [BUSY] the kernel is in use: 2 calls both got \"Connection closed")
        print("           by WolframKernel\". The Engine licence allows 1 kernel at a")
        print("           time. Close the other Wolfram session and re-run this script.")
        print("           Nothing needs reconfiguring.")
        return state

    if state == "STALE_KERNEL":
        print("    [STALE KERNEL] a licence message, but Wolfram kernel processes are")
        print("           already running, and a leftover kernel is the likely cause:")
        kernels = stale_kernels()
        for line in kernels[:5]:
            print(f"             {line[:100]}")
        if len(kernels) > 5:
            print(f"             ... and {len(kernels) - 5} more; `ps -axo pid,command | grep -i wolfram` lists all")
        print("           End those processes, then re-run this script. Do not")
        print("           re-activate on the strength of this message alone.")
        return state

    if state == "ABSENT":
        print("    [ABSENT] wolframscript is not installed. NOT A BLOCKER: the")
        print("             project runs without it and every result stays")
        print("             reproducible. Installing it adds a second falsifier,")
        print("             which is why it is recommended and made this easy.")
        if has_homebrew():
            print("      Command: brew install --cask wolfram-engine")
            if ask("Install the Wolfram Engine via Homebrew?", default="y"):
                subprocess.run(["brew", "install", "--cask", "wolfram-engine"],
                               check=False)
        else:
            print("      Homebrew is not available. Download the free Wolfram")
            print("      Engine for Developers, then re-run this script:")
            print("        https://www.wolfram.com/engine/")
        return state

    if state == "NO_KERNEL":
        print("    [NO KERNEL] wolframscript cannot locate a kernel to run.")
        kernel = wolfram_kernel_path()
        if kernel:
            print(f"      A kernel IS installed at: {kernel}")
            print("      Command: wolframscript -configure "
                  f'WOLFRAMSCRIPT_KERNELPATH="{kernel}"')
            if ask("Point wolframscript at that kernel?", default="y"):
                subprocess.run(["wolframscript", "-configure",
                                f"WOLFRAMSCRIPT_KERNELPATH={kernel}"], check=False)
                print(f"      Re-checked: {wolfram_state()}")
        else:
            print("      No Engine app found either. Install it first (above).")
        return state

    # CORRECTED 2026-09-17. This block used to say activation "needs your Wolfram
    # ID and password, so it cannot be automated from here". Measured that
    # evening with the licence file backed up first: `wolframscript -activate`
    # with stdin CLOSED returned exit 0 and "Wolfram Engine activated", prompting
    # for nothing, because it authenticates through the cloud credential already
    # stored under ~/Library/WolframEngine/ApplicationData/CloudObject.
    print("    [NOT ACTIVATED] a kernel runs but the licence is not valid.")
    print("      Activation needs no password here: it authenticates through the")
    print("      stored cloud credential. Run it, or let the agent do it:")
    print("        wolframscript -activate")
    print("        python3 scripts/wolfram_licence_renew_2026-09-17.py --run --force")
    print("      A LaunchAgent, com.cdsfl.wolfram-licence-renew, runs that script")
    print("      at login and twice a day, so a lapse repairs itself. The free")
    print("      Engine licence does NOT auto-renew on its own: it lapsed on")
    print("      2026-09-11 and was activated by hand on 2026-09-15.")
    return state


def check_api_keys() -> None:
    """Check API key availability.

    Reads local environment variables to detect *presence* of named keys.
    Never prints, logs, or transmits key values. If a required key is
    missing, supply it yourself via `.env` or shell export; do not commit
    `.env` or any file containing real key material to git.
    """
    print("  SECURITY: This check reads local environment variables to")
    print("  report key presence only. Key values are never printed or")
    print("  transmitted. If a required key is missing, supply it via")
    print("  `.env` or shell export. Never commit `.env` or any file")
    print("  containing real key material to git.")
    print()
    source_env()
    for key, (level, desc) in API_KEYS.items():
        found = os.environ.get(key)
        status = "FOUND" if found else "MISSING"
        marker = "  " if found else ("!!" if level == "Required" else "  ")
        print(f"  {marker}[{status}] {key} ({level})")
        print(f"           {desc}")
    print()
    print("  Routes that need no key:")
    for route in UNCREDENTIALED_ROUTES:
        print(f"    - {route}")


# ---------------------------------------------------------------------------
# Installation
# ---------------------------------------------------------------------------

def install_packages(missing: list[str], label: str) -> None:
    """Offer to install missing packages."""
    if not missing:
        return

    print(f"  {len(missing)} {label} packages to install: {', '.join(missing)}")
    print(f"    Command: {sys.executable} -m pip install {' '.join(missing)}")
    print()

    if ask(f"Install {label} packages?", default="y"):
        subprocess.run(
            [sys.executable, "-m", "pip", "install", *missing],
            check=False,
        )
        print()


def install_system_tools(missing: list[str]) -> None:
    """Offer to install missing system tools via Homebrew."""
    if not missing:
        return

    if not has_homebrew():
        print(f"  {len(missing)} system tools missing but Homebrew not available.")
        print("  Install Homebrew first, then re-run this script.")
        return

    print(f"  {len(missing)} system tools to install: {', '.join(missing)}")
    print(f"    Command: brew install {' '.join(missing)}")
    print()

    if ask("Install system tools via Homebrew?"):
        subprocess.run(["brew", "install", *missing], check=False)
        print()


# ---------------------------------------------------------------------------
# Dynamic content readers
# ---------------------------------------------------------------------------

class SVBlock(NamedTuple):
    """The sv-written state block, and — when absent — WHY it is absent.

    ``status`` is "ok" or one of the failure reasons below. An empty ``text``
    with no reason attached is exactly the shape of defect this type exists to
    prevent: a caller must never be able to mistake "could not find it" for
    "there is nothing to show".
    """

    text: str      # marker pair included; "" unless status == SV_OK
    status: str    # SV_OK | unreadable | no-markers | no-start | no-end
                   # | duplicate | inverted | empty
    detail: str


SV_OK = "ok"


def find_sv_block(root: Path) -> SVBlock:
    """Locate the SV:LATEST_EXP block ANYWHERE in resources/ONBOARDING.md.

    THE DEFECT THIS CLOSES (founder ruling, 2026-08-05: "take the search
    route"). This search used to run against the extracted
    '## What This Project Is' section only, while `cdsfl_sv.py` writes the
    marker pair into '## Current State'. `find()` returned -1, the guard
    silently fell through, and `--full` was a byte-for-byte no-op for 118
    days — 884 characters either way, with nothing to tell the reader that
    ~80,000 characters of project state had been dropped.

    Searching the whole file rather than moving what sv writes is deliberate:
    it survives any future reorganisation of ONBOARDING.md, and it moves no
    content out from under readers who know where to find it. Nothing here
    depends on section ordering, section names, or line numbers — only on the
    marker pair itself.
    """
    path = root / "resources" / "ONBOARDING.md"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return SVBlock("", "unreadable", f"{path}: {exc}")

    start = text.find(SV_START_MARKER)
    end = text.find(SV_END_MARKER)

    if start == -1 and end == -1:
        return SVBlock(
            "", "no-markers",
            f"neither {SV_START_MARKER} nor {SV_END_MARKER} appears in {path}",
        )
    if start == -1:
        return SVBlock("", "no-start", f"{SV_START_MARKER} is absent from {path}")
    if end == -1:
        return SVBlock("", "no-end", f"{SV_END_MARKER} is absent from {path}")

    # More than one pair: the search route has to CHOOSE, and choosing quietly
    # is how this script came to be audited. Two pairs means `--full` would
    # print the FIRST — potentially the stale one — and drop the rest without
    # a word, which is the same defect class as the 118-day no-op wearing a
    # different hat. `cdsfl_sv.py` never writes a second pair (it re-substitutes
    # in place), so this state can only arrive by hand-editing ONBOARDING.md,
    # which is exactly what is happening to that file. Refuse and say so.
    starts = text.count(SV_START_MARKER)
    ends = text.count(SV_END_MARKER)
    if starts > 1 or ends > 1:
        return SVBlock(
            "", "duplicate",
            f"{starts} {SV_START_MARKER} and {ends} {SV_END_MARKER} in {path} "
            f"— exactly one of each is expected; splicing would silently print "
            f"the first and drop the rest. Delete the surplus pair(s) or re-run "
            f"`python3 scripts/cdsfl_sv.py`.",
        )

    if end < start:
        return SVBlock(
            "", "inverted",
            f"{SV_END_MARKER} (offset {end}) precedes {SV_START_MARKER} "
            f"(offset {start}) in {path}",
        )

    inner = text[start + len(SV_START_MARKER):end]
    if not inner.strip():
        return SVBlock(
            "", "empty",
            f"the marker pair is present in {path} but there is nothing "
            f"between the markers",
        )

    block = text[start:end + len(SV_END_MARKER)]
    return SVBlock(
        block, SV_OK,
        f"{len(inner.strip())} chars between the markers, "
        f"at offsets {start}-{end + len(SV_END_MARKER)} of {len(text)}",
    )


def read_onboarding_what_is(root: Path) -> str:
    """Read the 'What This Project Is' section from resources/ONBOARDING.md.

    The SV:LATEST_EXP block is always stripped here, wherever it happens to
    fall. `--full` re-attaches it once, from `find_sv_block`, so the block is
    printed exactly once no matter which section ONBOARDING.md keeps it in.
    The old `strip_sv=False` path is gone: it promised the caller a block this
    function never had, which is how `--full` came to be a no-op.
    """
    path = root / "resources" / "ONBOARDING.md"
    content = read_section(path, "## What This Project Is", "\n## ")
    if not content:
        return ""
    start = content.find(SV_START_MARKER)
    end = content.find(SV_END_MARKER)
    if start != -1 and end > start:
        # Whole block inside this section: excise it.
        content = content[:start].rstrip() + "\n" + content[end + len(SV_END_MARKER):].lstrip()
    elif start != -1:
        # Block STARTS here and runs past the section boundary. Cut at the
        # marker: keeping the opening lines would both leak a fragment into
        # the default view and duplicate it under --full, which re-attaches
        # the whole block.
        content = content[:start]
    elif end != -1:
        # Mirror case — the block started in an earlier section and ends here.
        content = content[end + len(SV_END_MARKER):]
    return content.strip()


def build_project_summary(root: Path, full: bool = False) -> tuple[str, list[str]]:
    """Assemble the summary text. Returns (text, problems).

    `problems` is never discarded silently by any caller: `print_project_summary`
    prints each one on stdout AND stderr and refuses to report success, and
    `dry_run` fails on any of them. When `--full` cannot deliver the state
    block the caller gets the default text *and* a problem saying so — not the
    default text alone.
    """
    problems: list[str] = []

    what = read_onboarding_what_is(root)
    if not what:
        problems.append(
            "resources/ONBOARDING.md '## What This Project Is' read as EMPTY. "
            "Canonical project prose is sourced from that section; the summary "
            "shown is not it."
        )

    if not full:
        return what, problems

    block = find_sv_block(root)
    if block.status != SV_OK:
        problems.append(
            f"--full was requested but the SV:LATEST_EXP state block could NOT "
            f"be spliced ({block.status}: {block.detail}). What follows is the "
            f"DEFAULT view — nothing was added to it. That block is written by "
            f"`python3 scripts/cdsfl_sv.py`; repair the marker pair in "
            f"resources/ONBOARDING.md or re-run sv."
        )
        return what, problems

    return (f"{what}\n\n{block.text}" if what else block.text), problems


def read_reproducing_mc(root: Path) -> str:
    """Read the Metacognitive Commands section from docs/REPRODUCING.md."""
    path = root / "docs" / "REPRODUCING.md"
    return read_section(path, "## Metacognitive Commands (MC)", "\n## ")


# ---------------------------------------------------------------------------
# Info display (driven from canonical documents at runtime)
# ---------------------------------------------------------------------------

def print_project_summary(root: Path, full: bool = False) -> bool:
    """Print the project summary, sourced from resources/ONBOARDING.md.

    Returns True only if the requested view was delivered in full. A False
    return must reach the exit code — a `--full` run that quietly prints the
    default view and exits 0 is the 118-day defect.
    """
    text, problems = build_project_summary(root, full=full)

    for problem in problems:
        print(f"  [ERROR] {problem}")
        print(f"cdsfl_onboard: {problem}", file=sys.stderr)
    if problems:
        print()

    if text:
        for line in text.split("\n"):
            print(f"  {line}" if line.strip() else "")
    else:
        print("  [WARNING] Could not read resources/ONBOARDING.md.")
        print("  Canonical project prose is sourced from that file; without")
        print("  it this summary is empty. Run `git pull` to sync.")
    print()

    exp = latest_experiment()
    if exp:
        print(f"  Latest experiment: {exp['name']} (#{exp['number']})")
        print(f"    Status: {exp['status']} | {exp['total_rounds']} rounds | "
              f"{exp['total_findings']} findings | gamma={exp['gamma']:.3f}")
        print(f"    Models: {', '.join(exp['models'])}")

    tests = test_count()
    if tests:
        print(f"  Test suite: {tests} tests")

    return not problems


def print_structure(root: Path) -> None:
    """Print a short structural map of top-level directories.

    The full architecture tree lives in `resources/ONBOARDING.md
    § Architecture Overview`. Printing only the top-level layout here
    avoids the staleness problems that hardcoded deep trees suffer.
    """
    print("  Top-level layout:\n")
    top_level = [
        ("PAPER.md", "Canonical technical statement (white paper)"),
        ("README.md", "Operational front door"),
        ("bench/", "Runner infrastructure, experiment code, tests"),
        ("docs/", "Architecture, glossary, reproducing, mathematical appendix"),
        ("resources/", "Onboarding, recovery, shortcuts, memory mirrors"),
        ("experimental_notes/", "Markdown analysis per experiment"),
        ("scripts/", "This script, sv, qc, recover (automation)"),
        (".claude/CLAUDE.md", "CC1 command configuration"),
    ]
    for path, desc in top_level:
        exists = (root / path).exists()
        marker = "[OK]     " if exists else "[MISSING]"
        print(f"    {marker} {path:22s} {desc}")
    print()
    print("  Full architecture map: resources/ONBOARDING.md § Architecture Overview")

    print("\n  Documentation presence:")
    docs = [
        "docs/GLOSSARY.md", "docs/ARCHITECTURE.md", "docs/REPRODUCING.md",
        "docs/CURRENT_STATE.md", "docs/MATHEMATICAL_APPENDIX.md",
        "resources/ONBOARDING.md", "resources/RECOVERY.md", "resources/SHORTCUTS.md",
    ]
    for d in docs:
        exists = (root / d).exists()
        status = "exists" if exists else "NOT YET CREATED"
        print(f"    {'  ' if exists else '! '}{d}: {status}")


def print_mc_commands(root: Path) -> None:
    """Print the Metacognitive Commands reference from docs/REPRODUCING.md."""
    mc = read_reproducing_mc(root)
    if mc:
        for line in mc.split("\n"):
            print(f"  {line}" if line.strip() else "")
    else:
        print("  [WARNING] Could not read MC section from docs/REPRODUCING.md.")
        print("  Canonical MC reference is sourced from that file.")


# ---------------------------------------------------------------------------
# Dry-run mode (used by sv / qc sanity checks)
# ---------------------------------------------------------------------------

def _read_or_none(path: Path) -> str | None:
    """File text, or None if it cannot be read. Never raises."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def dry_run(root: Path) -> int:
    """Self-test the canonical-document wiring. Exit 0 only if every check passed.

    WHAT CHANGED AND WHY (2026-08-06). This self-test printed a bare "OK" over
    a `--full` mode that had been a byte-for-byte no-op since the day it was
    written. It could not have caught that, because it only checked that the
    markers existed *somewhere in the file* and that the reader returned a
    non-empty string — never that `--full` produced anything different from
    the default. A self-test that cannot fail on the defect it exists to catch
    is not a test.

    So the last check here asserts the OBSERVABLE PROPERTY: `--full` output
    differs from the default, strictly contains it, and the difference is a
    non-empty marker-delimited block. And every check now prints its name and
    its result, because a bare "OK" is not auditable.

    Consumers (`scripts/cdsfl_sv.py` step 7, `scripts/cdsfl_qc.py`
    `check_onboard_script`) gate on the return code and read stderr, so the
    expanded stdout is safe; failing lines are still mirrored to stderr.
    """
    checks: list[tuple[str, bool, str]] = []

    def record(name: str, ok: bool, detail: str) -> None:
        checks.append((name, bool(ok), detail))

    onboarding = root / "resources" / "ONBOARDING.md"
    reproducing = root / "docs" / "REPRODUCING.md"

    onboarding_text = _read_or_none(onboarding)
    record(
        "ONBOARDING.md readable",
        onboarding_text is not None,
        f"{onboarding}"
        + (f" ({len(onboarding_text)} chars)" if onboarding_text is not None
           else " — missing or unreadable"),
    )

    record(
        'ONBOARDING.md has "## What This Project Is"',
        onboarding_text is not None and "## What This Project Is" in onboarding_text,
        "section heading present" if onboarding_text is not None
        and "## What This Project Is" in onboarding_text
        else "section heading ABSENT — the default summary has no source",
    )

    block = find_sv_block(root)
    record(
        "SV:LATEST_EXP marker pair locatable anywhere in ONBOARDING.md",
        block.status == SV_OK,
        f"{block.status}: {block.detail}",
    )

    reproducing_text = _read_or_none(reproducing)
    record(
        "REPRODUCING.md readable",
        reproducing_text is not None,
        f"{reproducing}"
        + (f" ({len(reproducing_text)} chars)" if reproducing_text is not None
           else " — missing or unreadable"),
    )

    mc_heading = "## Metacognitive Commands (MC)"
    record(
        f'REPRODUCING.md has "{mc_heading}"',
        reproducing_text is not None and mc_heading in reproducing_text,
        "section heading present" if reproducing_text is not None
        and mc_heading in reproducing_text
        else "section heading ABSENT — the MC table has no source",
    )

    what = read_onboarding_what_is(root)
    record(
        "read_onboarding_what_is returns content",
        bool(what),
        f"{len(what)} chars" if what else "EMPTY — the dynamic summary would be blank",
    )

    mc = read_reproducing_mc(root)
    record(
        "read_reproducing_mc returns content",
        bool(mc),
        f"{len(mc)} chars" if mc else "EMPTY — the dynamic MC table would be blank",
    )

    # THE CHECK THAT WOULD HAVE CAUGHT THE 118-DAY NO-OP.
    # Not "the code path ran" — the observable difference between the two views.
    default_text, default_problems = build_project_summary(root, full=False)
    full_text, full_problems = build_project_summary(root, full=True)
    delta = full_text[len(default_text):] if full_text.startswith(default_text) else ""
    spliced = delta.replace(SV_START_MARKER, "").replace(SV_END_MARKER, "").strip()
    splice_ok = (
        not default_problems
        and not full_problems
        and bool(default_text)
        and full_text != default_text
        and default_text in full_text
        and SV_START_MARKER in delta
        and SV_END_MARKER in delta
        and bool(spliced)
    )
    if splice_ok:
        splice_detail = (
            f"--full is {len(full_text)} chars vs default {len(default_text)}; "
            f"it contains the default view and adds a {len(spliced)}-char "
            f"marker-delimited block"
        )
    else:
        reasons = list(default_problems) + list(full_problems)
        if not reasons:
            reasons.append(
                f"--full produced {len(full_text)} chars against a default of "
                f"{len(default_text)}; spliced block {len(spliced)} chars, "
                f"start marker in delta={SV_START_MARKER in delta}, "
                f"end marker in delta={SV_END_MARKER in delta}, "
                f"default contained in full={default_text in full_text}"
            )
        splice_detail = " | ".join(reasons)
    record("--full differs from, and contains, the default view", splice_ok, splice_detail)

    failed = [c for c in checks if not c[1]]

    print(f"cdsfl_onboard --dry-run: {len(checks)} checks against {root}")
    for name, ok, detail in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name} — {detail}")

    if failed:
        print(
            f"cdsfl_onboard --dry-run: FAIL "
            f"({len(failed)} of {len(checks)} checks failed)",
            file=sys.stderr,
        )
        for name, _, detail in failed:
            print(f"  {name}: {detail}", file=sys.stderr)
        print(f"cdsfl_onboard --dry-run: FAIL ({len(failed)} of {len(checks)} failed)")
        return 1

    print(f"cdsfl_onboard --dry-run: OK ({len(checks)} of {len(checks)} checks passed)")
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="CDSFL onboarding + dynamic info source.",
        epilog=(
            "Key values are never printed or transmitted. Supply missing "
            "keys via `.env` or shell export; never commit `.env`."
        ),
    )
    ap.add_argument(
        "--full",
        action="store_true",
        help=(
            "Splice the SV:LATEST_EXP state block into the project summary, "
            "from wherever the marker pair sits in ONBOARDING.md. Exits 1 if "
            "the block could not be spliced."
        ),
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Self-test only; no prompts, no installs. Exit 0 on success.",
    )
    return ap.parse_args()


def wire_git_hooks(root: Path) -> bool:
    """Point git at the repository's versioned hooks/ directory.

    WHY THIS IS HERE RATHER THAN IN A README. `core.hooksPath` is per-clone local
    configuration: it is not carried by the repository, so a fresh clone has NO
    pre-commit guard until someone runs 1 command. A guard that depends on
    remembering to install it has the same reliability as the discipline it
    replaces, which is the failure this whole mechanism exists to end.

    Measured 2026-09-09 before this was wired: `git config --get core.hooksPath`
    was unset, `.git/hooks` held 14 files and every one was a `.sample`, and
    commit 57d5a0e had reached HEAD that morning with the full suite red.

    Setting it is safe and was checked rather than assumed: of the files in
    `hooks/`, git executes only those bearing a git-hook name, so the Claude Code
    hooks stored alongside (mc_commands.py and the rest) are ignored by git, and
    nothing in `.git/hooks` was active to lose.
    """
    hooks_dir = root / "hooks"
    if not hooks_dir.is_dir():
        print("  [WARN] hooks/ is missing; git hooks not wired")
        return False
    current = subprocess.run(["git", "config", "--get", "core.hooksPath"],
                             cwd=root, capture_output=True, text=True).stdout.strip()
    if current == "hooks":
        print("  [OK] core.hooksPath already points at hooks/")
    else:
        subprocess.run(["git", "config", "core.hooksPath", "hooks"], cwd=root, check=False)
        print(f"  [SET] core.hooksPath: {current or '(unset)'} -> hooks")
    pre = hooks_dir / "pre-commit"
    if not pre.is_file():
        print("  [WARN] hooks/pre-commit is missing; commits are unguarded")
        return False
    if not os.access(pre, os.X_OK):
        pre.chmod(0o755)
        print("  [SET] hooks/pre-commit made executable (git ignores it otherwise)")
    else:
        print("  [OK] hooks/pre-commit present and executable")
    _stamp_onboarded(root)
    return True


def _stamp_onboarded(root: Path) -> None:
    """Record IN THIS CLONE'S LOCAL CONFIG that onboarding has run.

    WHY A SECOND MARKER WHEN `core.hooksPath` IS ALREADY ONE. It is not one, and
    the difference decides whether a red test means "not set up yet" or "the guard
    was removed". `core.hooksPath` unset is ambiguous between those, and they have
    opposite remedies: run onboarding, or find out who turned the guard off.

    THE DISCRIMINATOR THIS REPLACES WAS UNREACHABLE, measured 2026-09-10 in a
    fresh clone at /tmp/ce_fresh. `test_the_live_repository_is_actually_wired`
    decided "this looks like a fresh clone" from `git config --get user.email`
    being empty -- but `--get` falls back to GLOBAL config, and `git clone`
    inherits the machine's global identity. In the fresh clone the command
    returned `jebus.2504@gmail.com`, so the skip branch could not fire on any
    machine with a git identity, which is every machine that can clone and
    commit. The addition was there and nothing reached it.

    `cdsfl.onboarded` is written with `--local`, so it lives in `.git/config`,
    is never cloned, and survives someone unsetting `core.hooksPath` -- which is
    precisely the case that must stay RED rather than becoming a skip.
    """
    stamp = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    subprocess.run(["git", "config", "--local", "cdsfl.onboarded", stamp],
                   cwd=root, check=False, capture_output=True)
    print(f"  [SET] cdsfl.onboarded = {stamp}")


def main() -> int:
    args = parse_args()
    root = repo_root()

    if args.dry_run:
        return dry_run(root)

    print()
    print("  CDSFL Project Onboarding")
    print(f"  Repository: {root}")
    print(f"  Platform: {platform.system()} {platform.machine()}")

    # --- PROJECT SUMMARY ---
    print_header("PROJECT SUMMARY")
    summary_ok = print_project_summary(root, full=args.full)

    # --- PYTHON VERSION ---
    print_header("PYTHON VERSION")
    python_ok = check_python()

    # --- PACKAGES ---
    print_header("PYTHON PACKAGES")
    all_missing: list[str] = []

    missing_core = check_packages(CORE_PACKAGES, "Core (required)")
    all_missing.extend(missing_core)
    print()

    missing_quality = check_packages(CODE_QUALITY_PACKAGES, "Code quality")
    all_missing.extend(missing_quality)
    print()

    missing_stem = check_packages(STEM_PACKAGES, "STEM / verification")
    all_missing.extend(missing_stem)
    print()

    check_packages(OPTIONAL_PACKAGES, "Optional")

    # --- GIT HOOKS ---
    print_header("GIT HOOKS")
    wire_git_hooks(root)
    print()

    # --- SYSTEM TOOLS ---
    print_header("SYSTEM TOOLS")
    missing_sys = check_system_tools()
    print()
    check_claude_code()
    print()
    check_wolfram()

    # --- API KEYS ---
    print_header("API KEYS")
    check_api_keys()

    # --- PROJECT STRUCTURE ---
    print_header("PROJECT STRUCTURE")
    print_structure(root)

    # --- INSTALLATION ---
    print_header("INSTALLATION")

    if all_missing:
        print(f"  Total missing Python packages: {len(all_missing)}")
        print()
        if missing_core:
            install_packages(missing_core, "core")
        if missing_quality:
            install_packages(missing_quality, "code quality")
        if missing_stem:
            install_packages(missing_stem, "STEM/verification")
    else:
        print("  All required Python packages are installed.")

    if missing_sys:
        print()
        install_system_tools(missing_sys)

    # --- GETTING STARTED ---
    print_header("GETTING STARTED")
    print("  1. Read resources/ONBOARDING.md for full project context")
    print("  2. Read docs/GLOSSARY.md for term definitions")
    print("  3. Read docs/ARCHITECTURE.md for system components and data flow")
    print("  4. Read docs/REPRODUCING.md for how to run experiments")
    print("  5. Run: python3 scripts/cdsfl_recover.py --full")
    print("     to see the current project state")
    print()
    print("  To run the test suite:")
    print("    python3 -m pytest bench/tests/ -v")
    print()
    print("  To view the full ONBOARDING summary via this script:")
    print("    python3 scripts/cdsfl_onboard.py --full")
    print()
    print("  To replicate the latest experiment:")
    print("    See docs/REPRODUCING.md for step-by-step instructions")

    # --- METACOGNITIVE COMMANDS ---
    print_header("METACOGNITIVE COMMANDS (MC)")
    print_mc_commands(root)
    print()
    print("  Canonical source: docs/REPRODUCING.md § Metacognitive Commands")
    print("  Model config:     .claude/CLAUDE.md")
    print()

    if not summary_ok:
        # Repeated here because the error scrolled off the top hundreds of
        # lines ago, and carried into the exit code because a run that could
        # not deliver what was asked for must not report success.
        print("  [ERROR] The PROJECT SUMMARY above was INCOMPLETE — see the")
        print("          error printed under that heading. Exiting 1.")
        print()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
