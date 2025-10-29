#!/usr/bin/env python
# noqa: E501
"""Check MCP-specific security best practices."""

import re
import sys
from pathlib import Path

SECURITY_CHECKS = {
    "token_passthrough": {
        "patterns": [
            re.compile(
                r"(bearer|access)_token\s*=\s*(request|client)\.",
                re.IGNORECASE,
            ),
            re.compile(
                r"client\..*token.*=.*upstream_token",
                re.IGNORECASE,
            ),
        ],
        "message": "Potential token passthrough vulnerability.",
        "severity": "HIGH",
    },
    "unsafe_subprocess": {
        "patterns": [
            re.compile(r"shell\s*=\s*True"),
            re.compile(r"^[^#]*os\.system\s*\("),
            re.compile(r"^[^#]*\beval\s*\("),
            re.compile(r"^[^#]*\bexec\s*\("),
        ],
        "message": "Unsafe command execution pattern detected.",
        "severity": "CRITICAL",
    },
    "hardcoded_localhost": {
        "patterns": [
            re.compile(r"http://localhost:[0-9]+", re.IGNORECASE),
            re.compile(r"127\.0\.0\.1:[0-9]+"),
        ],
        "message": "Hardcoded localhost. Use environment variables.",
        "severity": "MEDIUM",
    },
}

SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__"}


def check_file(filepath: Path) -> list:
    """Check a file for MCP security issues."""
    issues = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return issues

    for check_name, check_config in SECURITY_CHECKS.items():
        for pattern in check_config["patterns"]:
            for match in pattern.finditer(content):
                line_num = content[: match.start()].count("\n") + 1
                issues.append(
                    {
                        "file": str(filepath),
                        "line": line_num,
                        "check": check_name,
                        "message": check_config["message"],
                        "severity": check_config["severity"],
                        "match": match.group(0)[:50],
                    }
                )
    return issues


def main(argv=None):
    """Main entry point."""
    argv = argv or sys.argv[1:]
    if not argv:
        return 0

    all_issues = []
    skip_files = {__file__, "check_mcp_security.py"}
    for file_arg in argv:
        filepath = Path(file_arg)
        if filepath.is_dir() or any(
            skip_dir in filepath.parts for skip_dir in SKIP_DIRS
        ):
            continue
        if filepath.name in skip_files:
            continue
        if filepath.suffix == ".py":
            issues = check_file(filepath)
            all_issues.extend(issues)

    critical = [i for i in all_issues if i["severity"] == "CRITICAL"]
    high = [i for i in all_issues if i["severity"] == "HIGH"]

    if critical:
        print("🚨 CRITICAL security issues:", file=sys.stderr)
        for issue in critical:
            print(
                f"  {issue['file']}:{issue['line']} - " f"{issue['message']}",
                file=sys.stderr,
            )
        return 1

    if high:
        print("⚠️  HIGH severity issues:", file=sys.stderr)
        for issue in high:
            print(
                f"  {issue['file']}:{issue['line']} - " f"{issue['message']}",
                file=sys.stderr,
            )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
