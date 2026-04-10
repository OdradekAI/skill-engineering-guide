---
description: "Scan a bundle-plugin for security risks only — runs Category 10 (Security) from the auditing skill without the full 10-category audit"
---

This command invokes the auditing skill in **security-only mode**. It runs only Category 9 (Security Scan) plus the `scan_security.py` script, skipping quality, structure, and documentation checks.

Use this when you want a quick security check without a full audit.

Invoke the `bundles-forge:auditing` skill with the context: **security-only scan requested via bundles-scan**.
