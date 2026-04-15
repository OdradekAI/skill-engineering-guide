#!/usr/bin/env python3
"""
Version synchronization tool for bundle-plugins.

Reads .version-bump.json and bumps version numbers across all declared
files, detects drift, and audits for undeclared version strings.

Usage (via CLI):
    bundles-forge bump-version [project-root] <new-version>
    bundles-forge bump-version [project-root] --check
    bundles-forge bump-version [project-root] --audit

Exit codes: 0 = in sync, 1 = drift or undeclared files found
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(-[\w.]+)?$")


def _resolve_field_path(data, field):
    """Traverse a dotted field path like 'plugins.0.version' into nested JSON."""
    parts = field.split(".")
    current = data
    for part in parts:
        if part.isdigit():
            idx = int(part)
            if not isinstance(current, list) or idx >= len(current):
                return None
            current = current[idx]
        else:
            if not isinstance(current, dict) or part not in current:
                return None
            current = current[part]
    return current


def _set_field_path(data, field, value):
    """Set a value at a dotted field path like 'plugins.0.version'."""
    parts = field.split(".")
    current = data
    for part in parts[:-1]:
        if part.isdigit():
            current = current[int(part)]
        else:
            current = current[part]
    last = parts[-1]
    if last.isdigit():
        current[int(last)] = value
    else:
        current[last] = value


def load_config(repo_root):
    config_path = repo_root / ".version-bump.json"
    if not config_path.exists():
        print("error: .version-bump.json not found", file=sys.stderr)
        sys.exit(1)
    return json.loads(config_path.read_text(encoding="utf-8"))


def declared_files(config):
    return [(entry["path"], entry["field"]) for entry in config.get("files", [])]


def read_version(repo_root, path, field):
    fpath = repo_root / path
    if not fpath.exists():
        return None
    data = json.loads(fpath.read_text(encoding="utf-8"))
    return _resolve_field_path(data, field)


def write_version(repo_root, path, field, new_version):
    fpath = repo_root / path
    data = json.loads(fpath.read_text(encoding="utf-8"))
    _set_field_path(data, field, new_version)
    fpath.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                     encoding="utf-8")


def run_check(repo_root):
    """Check version drift. Returns structured results for programmatic use."""
    config = load_config(repo_root)
    entries = declared_files(config)

    versions = {}
    missing = []
    for path, field in entries:
        ver = read_version(repo_root, path, field)
        if ver is None:
            missing.append(path)
        else:
            versions[path] = ver

    unique = set(versions.values())
    has_drift = len(unique) > 1 or len(missing) > 0

    return {
        "versions": versions,
        "missing": missing,
        "unique_versions": sorted(unique),
        "has_drift": has_drift,
    }


def cmd_check(repo_root):
    result = run_check(repo_root)
    config = load_config(repo_root)

    print("Version check:\n")
    for path, field in declared_files(config):
        ver = result["versions"].get(path)
        label = f"{path} ({field})"
        if ver is None:
            print(f"  {label:<45}  MISSING")
        else:
            print(f"  {label:<45}  {ver}")

    print()
    if result["has_drift"]:
        if len(result["unique_versions"]) > 1:
            print("DRIFT DETECTED — versions are not in sync:")
            counts = Counter(result["versions"].values())
            for ver, count in counts.most_common():
                print(f"  {ver} ({count} files)")
        if result["missing"]:
            for m in result["missing"]:
                print(f"  MISSING: {m}")
    else:
        versions = list(result["versions"].values())
        if versions:
            print(f"All declared files are in sync at {versions[0]}")

    return result["has_drift"]


def cmd_audit(repo_root):
    result = run_check(repo_root)
    has_drift = result["has_drift"]

    if has_drift:
        n = len(result["unique_versions"])
        print(f"Version drift detected ({n} unique versions)")
    else:
        versions = list(result["versions"].values())
        if versions:
            print(f"Versions in sync at {versions[0]}")
    print()

    version_counts = Counter(result["versions"].values())

    if not version_counts:
        print("error: could not determine current version", file=sys.stderr)
        return True

    current_version = version_counts.most_common(1)[0][0]
    print(f"Audit: scanning repo for version string '{current_version}'...\n")

    config = load_config(repo_root)
    entries = declared_files(config)

    excludes = set(config.get("audit", {}).get("exclude", []))
    excludes.update({".git", "node_modules"})

    declared_paths = {path for path, _ in entries}

    found_undeclared = []
    for f in sorted(repo_root.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(repo_root)
        rel_str = str(rel).replace("\\", "/")

        skip = False
        for exc in excludes:
            if exc in rel.parts or rel_str == exc:
                skip = True
                break
        if skip:
            continue

        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except (OSError, PermissionError):
            continue

        if current_version not in content:
            continue

        if rel_str in declared_paths:
            continue

        for line_num, line in enumerate(content.splitlines(), 1):
            if current_version in line:
                found_undeclared.append(f"{rel_str}:{line_num}:{line.strip()}")

    if found_undeclared:
        print(f"UNDECLARED files containing '{current_version}':")
        for match in found_undeclared:
            print(f"  {match}")
        print()
        print("Review the above — add to .version-bump.json or audit.exclude as appropriate.")
        return True
    else:
        print("No undeclared files contain the version string. All clear.")
        return has_drift


def cmd_bump(repo_root, new_version, dry_run=False):
    if not SEMVER_RE.match(new_version):
        print(f"error: '{new_version}' doesn't look like a version (expected X.Y.Z or X.Y.Z-pre.N)",
              file=sys.stderr)
        sys.exit(1)

    config = load_config(repo_root)
    prefix = "[DRY RUN] " if dry_run else ""
    print(f"{prefix}Bumping all declared files to {new_version}...\n")

    for path, field in declared_files(config):
        fpath = repo_root / path
        if not fpath.exists():
            print(f"  SKIP (missing): {path}")
            continue
        old_ver = read_version(repo_root, path, field)
        if not dry_run:
            write_version(repo_root, path, field, new_version)
        label = f"{path} ({field})"
        print(f"  {label:<45}  {old_ver} -> {new_version}")

    print()
    if dry_run:
        print("Dry run complete — no files were modified.")
    else:
        print("Done. Running audit to check for missed files...\n")
        cmd_audit(repo_root)


def main():
    parser = argparse.ArgumentParser(
        description="Version synchronization tool for bundle-plugins.")
    parser.add_argument("project_root", nargs="?", default=".",
                        help="Bundle-plugin project root (default: current directory)")
    parser.add_argument("version", nargs="?", default=None,
                        help="New version (X.Y.Z or X.Y.Z-pre.N) for bump mode")
    parser.add_argument("--check", action="store_true",
                        help="Report current versions (detect drift)")
    parser.add_argument("--audit", action="store_true",
                        help="Check + scan repo for undeclared version strings")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview version bump without writing files")
    args = parser.parse_args()

    if SEMVER_RE.match(args.project_root) and args.version is None:
        args.version = args.project_root
        args.project_root = "."

    repo_root = Path(args.project_root).resolve()

    if args.check:
        has_drift = cmd_check(repo_root)
        sys.exit(1 if has_drift else 0)
    elif args.audit:
        has_issues = cmd_audit(repo_root)
        sys.exit(1 if has_issues else 0)
    elif args.version:
        cmd_bump(repo_root, args.version, dry_run=args.dry_run)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
