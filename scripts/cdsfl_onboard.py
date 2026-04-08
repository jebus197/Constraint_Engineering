#!/usr/bin/env python3
"""CDSFL Onboarding Script — interactive setup for external researchers.

Usage: python3 scripts/cdsfl_onboard.py

Checks environment, explains project structure, installs dependencies
with user permission, and points to key documentation. Designed for a
researcher's first contact with the project.
"""

from __future__ import annotations

import importlib.util
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cdsfl_utils import latest_experiment, repo_root, source_env, test_count


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
    """Check API key availability."""
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
# Info display
# ---------------------------------------------------------------------------

def print_project_summary() -> None:
    print("  CDSFL (Constraint-Driven Synthesis and Falsification) is a protocol-level")
    print("  architecture for scientific cognition. It formalises Popperian falsification")
    print("  as a structured protocol that AI models follow when producing and reviewing")
    print("  technical output.")
    print()
    print("  The system operates a panel of 5 frontier models from 4 vendors under")
    print("  structured falsification rounds. An immune-inspired pipeline processes")
    print("  findings, a convergence gate detects epistemic saturation, and a")
    print("  verification chain provides cryptographic audit trails.")
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


def print_structure() -> None:
    root = repo_root()
    structure = """
  Constraint_Engineering/
  |
  |-- bench/                     Runner infrastructure
  |   |-- experiment_11_orchestrator.py   Model dispatch and API config
  |   |-- runner_core.py                  Shared runner infrastructure
  |   |-- insect_brain.py                 Central relay and checkpoints
  |   |-- immune_agents.py                Immune pipeline (6 cell types)
  |   |-- evidence.py                     Evidence layer
  |   |-- endocrine.py                    Endocrine layer (health monitoring)
  |   |-- cdsfl_registry/                 Policy engine and directive composition
  |   |-- directives/                     CDSFL system prompts
  |   |-- run_exp*.py                     Experiment-specific runners
  |   |-- logs/                           Experiment logs and reports
  |   +-- tests/                          Test suite
  |
  |-- docs/                      Documentation
  |   |-- GLOSSARY.md                     Term definitions (51 terms)
  |   |-- ARCHITECTURE.md                 System components and data flow
  |   |-- REPRODUCING.md                  How to replicate experiments
  |   |-- CURRENT_STATE.md                Machine-generated state snapshot
  |   +-- MATHEMATICAL_APPENDIX.md        Mathematical framework (1081 lines)
  |
  |-- resources/                 Recovery resources
  |   |-- ONBOARDING.md                   Full project context and history
  |   +-- RECOVERY.md                     Recovery protocol and pending work
  |
  |-- experimental_notes/        Analysis and results per experiment
  |-- scripts/                   Automation (this script, sv, qc, recover)
  +-- .claude/CLAUDE.md          CC1 command configuration"""

    print(structure)

    print("\n  Documentation status:")
    docs = [
        "docs/GLOSSARY.md", "docs/ARCHITECTURE.md", "docs/REPRODUCING.md",
        "docs/CURRENT_STATE.md", "docs/MATHEMATICAL_APPENDIX.md",
    ]
    for d in docs:
        exists = (root / d).exists()
        status = "exists" if exists else "NOT YET CREATED"
        print(f"    {'  ' if exists else '! '}{d}: {status}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    root = repo_root()

    print()
    print("  CDSFL Project Onboarding")
    print(f"  Repository: {root}")
    print(f"  Platform: {platform.system()} {platform.machine()}")

    # --- PROJECT SUMMARY ---
    print_header("PROJECT SUMMARY")
    print_project_summary()

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
    print_structure()

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
    print("  1. Read docs/GLOSSARY.md for term definitions")
    print("  2. Read docs/ARCHITECTURE.md for system overview")
    print("  3. Read docs/REPRODUCING.md for how to run experiments")
    print("  4. Run: python3 scripts/cdsfl_recover.py --full")
    print("     to see the current project state")
    print()
    print("  To run the test suite:")
    print("    python3 -m pytest bench/tests/ -v")
    print()
    print("  To replicate the latest experiment:")
    print("    See docs/REPRODUCING.md for step-by-step instructions")
    print()


if __name__ == "__main__":
    main()
