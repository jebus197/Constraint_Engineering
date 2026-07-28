#!/usr/bin/env python3
"""CDSFL Onboarding Script — interactive setup + dynamic info source.

Usage:
  python3 scripts/cdsfl_onboard.py              # Default overview + env checks
  python3 scripts/cdsfl_onboard.py --full       # Include full ONBOARDING.md content
  python3 scripts/cdsfl_onboard.py --dry-run    # Self-test only; exits 0 on success

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
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cdsfl_utils import latest_experiment, read_section, repo_root, source_env, test_count


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
]

OPTIONAL_PACKAGES = [
    ("wolframalpha", "wolframalpha", "Wolfram Alpha API client"),
    ("web3", "web3", "Ethereum/Web3 blockchain interaction"),
    ("PIL", "Pillow", "Image processing"),
]

API_KEYS = {
    "OPENROUTER_API_KEY": ("Required", "Model dispatch for Codex and ChatGPT via OpenRouter"),
    "GEMINI_API_KEY": ("Required", "Gemini 3.1 Pro dispatch via Google GenAI API"),
    "DEEPSEEK_API_KEY": ("Required", "DeepSeek Reasoner dispatch via DeepSeek API"),
    "GOOGLE_API_KEY": ("Optional", "Alternative to GEMINI_API_KEY for Google API access"),
    "OPENAI_API_KEY": ("Optional", "Direct OpenAI API access (not used by default runners)"),
    "WOLFRAM_API_KEY": ("Optional", "Wolfram Alpha for mathematical verification"),
    "GITHUB_TOKEN": ("Optional", "Push access to repository"),
}

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


def check_wolfram_mcp() -> bool:
    """Check for Wolfram MCP Bridge."""
    print("  Wolfram MCP Bridge:")
    wolfram_app = Path("/Applications/WolframLocalMCPBridge.app")
    if wolfram_app.exists():
        print("    [FOUND] Wolfram Local MCP Bridge")
        return True
    print("    [MISSING] Wolfram Local MCP Bridge")
    print("             Optional — provides Wolfram computational engine via MCP")
    print("             Download from https://www.wolfram.com/")
    return False


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

def read_onboarding_what_is(root: Path, strip_sv: bool = True) -> str:
    """Read the 'What This Project Is' section from resources/ONBOARDING.md.

    If strip_sv is True (default), removes the SV:LATEST_EXP content block
    so the default overview stays short. --full includes it.
    """
    path = root / "resources" / "ONBOARDING.md"
    content = read_section(path, "## What This Project Is", "\n## ")
    if not content:
        return ""
    if strip_sv:
        start = content.find(SV_START_MARKER)
        end = content.find(SV_END_MARKER)
        if start != -1 and end != -1:
            content = content[:start].rstrip() + "\n" + content[end + len(SV_END_MARKER):].lstrip()
    return content.strip()


def read_reproducing_mc(root: Path) -> str:
    """Read the Metacognitive Commands section from docs/REPRODUCING.md."""
    path = root / "docs" / "REPRODUCING.md"
    return read_section(path, "## Metacognitive Commands (MC)", "\n## ")


# ---------------------------------------------------------------------------
# Info display (driven from canonical documents at runtime)
# ---------------------------------------------------------------------------

def print_project_summary(root: Path, full: bool = False) -> None:
    """Print the project summary, sourced from resources/ONBOARDING.md.

    Default mode strips the SV:LATEST_EXP block. `full=True` includes it.
    """
    what = read_onboarding_what_is(root, strip_sv=not full)
    if what:
        for line in what.split("\n"):
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

def dry_run(root: Path) -> int:
    """Verify canonical documents exist and expected markers are present.

    Exit 0 on success. Produces minimal output so it can be embedded in
    the sv post-commit sanity step and the qc staleness sweep.
    """
    errors: list[str] = []

    onboarding = root / "resources" / "ONBOARDING.md"
    reproducing = root / "docs" / "REPRODUCING.md"

    if not onboarding.exists():
        errors.append(f"MISSING: {onboarding}")
    else:
        text = onboarding.read_text(encoding="utf-8")
        if SV_START_MARKER not in text:
            errors.append(f"MISSING MARKER in ONBOARDING.md: {SV_START_MARKER}")
        if SV_END_MARKER not in text:
            errors.append(f"MISSING MARKER in ONBOARDING.md: {SV_END_MARKER}")
        if "## What This Project Is" not in text:
            errors.append("MISSING SECTION in ONBOARDING.md: ## What This Project Is")

    if not reproducing.exists():
        errors.append(f"MISSING: {reproducing}")
    else:
        text = reproducing.read_text(encoding="utf-8")
        if "## Metacognitive Commands (MC)" not in text:
            errors.append("MISSING SECTION in REPRODUCING.md: ## Metacognitive Commands (MC)")

    if not read_onboarding_what_is(root):
        errors.append("read_onboarding_what_is returned empty — dynamic summary would be blank")

    if not read_reproducing_mc(root):
        errors.append("read_reproducing_mc returned empty — dynamic MC table would be blank")

    if errors:
        print("cdsfl_onboard --dry-run: FAIL", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        return 1

    print("cdsfl_onboard --dry-run: OK")
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
        help="Include the SV:LATEST_EXP block in the project summary (full ONBOARDING state).",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Self-test only; no prompts, no installs. Exit 0 on success.",
    )
    return ap.parse_args()


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
    print_project_summary(root, full=args.full)

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

    # --- SYSTEM TOOLS ---
    print_header("SYSTEM TOOLS")
    missing_sys = check_system_tools()
    print()
    check_claude_code()
    print()
    check_wolfram_mcp()

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
    return 0


if __name__ == "__main__":
    sys.exit(main())
