#!/usr/bin/env python3
"""Run all Python test suites and report summary.

Cross-platform replacement for run-all.sh.

Usage:
    python tests/run_all.py
"""

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TEST_FILES = ["test_scripts.py", "test_integration.py", "test_graph_fixtures.py", "test_unit.py", "test_skill_quality.py", "test_workflow_chains.py"]
SEPARATOR = "\u2501" * 48


def main():
    total_pass = 0
    total_fail = 0

    for test_file in TEST_FILES:
        test_path = SCRIPT_DIR / test_file
        if not test_path.exists():
            print(f"\n[WARN] {test_file} not found — skipping")
            continue

        print(f"\n{SEPARATOR}")
        print(f"Running: {test_file}")
        print(f"{SEPARATOR}\n")

        result = subprocess.run(
            [sys.executable, str(test_path), "-v"],
        )
        if result.returncode == 0:
            total_pass += 1
        else:
            total_fail += 1

    print(f"\n{SEPARATOR}")
    print(f"Overall: {total_pass} test suites passed, {total_fail} failed")
    print(SEPARATOR)

    sys.exit(total_fail)


if __name__ == "__main__":
    main()
