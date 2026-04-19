"""Shared CLI utilities for bundle-plugin scripts."""

import argparse
import sys
from pathlib import Path


class BundlesForgeError(Exception):
    """User-facing error raised by submodules (invalid input, missing files).

    Caught by run_main() which prints the message to stderr and exits.
    """
    def __init__(self, message, code=1):
        self.message = message
        self.code = code
        super().__init__(message)


def run_main(fn):
    """Top-level wrapper: catches BundlesForgeError, prints to stderr, exits."""
    try:
        fn()
    except BundlesForgeError as e:
        print(f"error: {e.message}", file=sys.stderr)
        sys.exit(e.code)


def make_parser(description):
    """Create a standard argparse parser with target-dir and --json options."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("target_dir", nargs="?", default=".",
                        help="Bundle-plugin root (default: current directory)")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON instead of markdown")
    return parser


def resolve_target(path_str):
    """Resolve target directory and verify it contains a skills/ directory."""
    root = Path(path_str).resolve()
    if not (root / "skills").is_dir():
        raise BundlesForgeError(f"{root} has no skills/ directory")
    return root


def exit_by_severity(summary):
    """Exit with code 2 (critical), 1 (warnings), or 0 (clean)."""
    sys.exit(2 if summary.get("critical", 0) else
             1 if summary.get("warning", 0) else 0)
