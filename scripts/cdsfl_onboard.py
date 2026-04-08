#!/usr/bin/env python3
"""CDSFL Onboarding Script — interactive setup for external researchers.

Usage: python3 scripts/cdsfl_onboard.py

Checks environment, explains project structure, offers dependency
installation, and points to key documentation. Designed for a
researcher's first contact with the project.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cdsfl_utils import latest_experiment, repo_root, source_env, test_count


REQUIRED_PACKAGES = [
    ("anthropic", "anthropic"),
    ("openai", "openai"),
    ("scipy", "scipy"),
    ("numpy", "numpy"),
    ("pytest", "pytest"),
    ("sympy", "sympy"),
    ("google.genai", "google-genai"),
    ("statsmodels", "statsmodels"),
]

OPTIONAL_PACKAGES = [
    ("z3", "z3-solver"),
    ("uncertainties", "uncertainties"),
    ("wolframalpha", "wolframalpha"),
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


def print_header(text: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def check_python() -> bool:
    v = sys.version_info
    ok = v >= (3, 13)
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] Python {v.major}.{v.minor}.{v.micro}")
    if not ok:
        print(f"         Requires Python 3.13+. Current: {v.major}.{v.minor}")
        print(f"         Install via: brew install python@3.13 or pyenv install 3.13")
    return ok


def check_packages() -> list[str]:
    missing = []

    print("  Required:")
    for module, pip_name in REQUIRED_PACKAGES:
        spec = importlib.util.find_spec(module.split(".")[0])
        status = "FOUND" if spec else "MISSING"
        print(f"    [{status}] {pip_name}")
        if not spec:
            missing.append(pip_name)

    print("  Optional:")
    for module, pip_name in OPTIONAL_PACKAGES:
        spec = importlib.util.find_spec(module)
        status = "FOUND" if spec else "MISSING"
        print(f"    [{status}] {pip_name}")

    return missing


def check_api_keys() -> None:
    source_env()

    for key, (level, desc) in API_KEYS.items():
        found = os.environ.get(key)
        status = "FOUND" if found else "MISSING"
        marker = "  " if found else ("!!" if level == "Required" else "  ")
        print(f"  {marker}[{status}] {key} ({level})")
        print(f"           {desc}")


def print_project_summary() -> None:
    root = repo_root()

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

    # Live state
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
  |   |-- GLOSSARY.md                     Term definitions
  |   |-- ARCHITECTURE.md                 System components and data flow
  |   |-- REPRODUCING.md                  How to replicate experiments
  |   |-- CURRENT_STATE.md                Machine-generated state snapshot
  |   +-- MATHEMATICAL_APPENDIX.md        Mathematical framework
  |
  |-- resources/                 Recovery resources
  |   |-- ONBOARDING.md                   Full project context
  |   +-- RECOVERY.md                     Recovery protocol and pending work
  |
  |-- experimental_notes/        Analysis and results per experiment
  |-- scripts/                   Automation (this script lives here)
  +-- .claude/CLAUDE.md          CC1 command configuration"""

    print(structure)

    # Check which docs exist
    print("\n  Documentation status:")
    docs = [
        "docs/GLOSSARY.md",
        "docs/ARCHITECTURE.md",
        "docs/REPRODUCING.md",
        "docs/CURRENT_STATE.md",
        "docs/MATHEMATICAL_APPENDIX.md",
    ]
    for d in docs:
        exists = (root / d).exists()
        status = "exists" if exists else "NOT YET CREATED"
        print(f"    {'  ' if exists else '! '}{d}: {status}")


def offer_install(missing: list[str]) -> None:
    if not missing:
        print("  All required packages are installed.")
        return

    print(f"  {len(missing)} required packages missing: {', '.join(missing)}")
    print()
    cmd = f"pip install {' '.join(missing)}"
    print(f"  Install command: {cmd}")
    print()

    try:
        answer = input("  Install now? [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return

    if answer == "y":
        subprocess.run([sys.executable, "-m", "pip", "install", *missing])


def main() -> None:
    root = repo_root()

    print()
    print("  CDSFL Project Onboarding")
    print(f"  Repository: {root}")

    print_header("PROJECT SUMMARY")
    print_project_summary()

    print_header("ENVIRONMENT CHECK")

    print("  Python version:")
    check_python()
    print()

    print("  Packages:")
    missing = check_packages()
    print()

    print("  API keys:")
    check_api_keys()

    print_header("PROJECT STRUCTURE")
    print_structure()

    print_header("DEPENDENCY INSTALLATION")
    offer_install(missing)

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
    print("  Questions? See resources/ONBOARDING.md for full project history.")
    print()


if __name__ == "__main__":
    main()
