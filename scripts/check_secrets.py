#!/usr/bin/env python
# noqa: E501
"""Check for hardcoded secrets and credentials."""

import re
import sys
from pathlib import Path

SECRET_PATTERNS = {
    "api_key": re.compile(
        r"(?i)(api[_-]?key|apikey)\s*=\s*['\"]([^'\"]+)['\"]",
        re.MULTILINE,
    ),
    "password": re.compile(
        r"(?i)(password|passwd|pwd)\s*=\s*['\"]([^'\"]+)['\"]",
        re.MULTILINE,
    ),
    "token": re.compile(
        r"(?i)(token|auth_token|access_token)\s*=\s*['\"]([^'\"]+)['\"]",
        re.MULTILINE,
    ),
    "secret": re.compile(
        r"(?i)(secret|secret_key)\s*=\s*['\"]([^'\"]+)['\"]",
        re.MULTILINE,
    ),
    "oauth": re.compile(
        r"(?i)(oauth|client_secret)\s*=\s*['\"]([^'\"]+)['\"]",
        re.MULTILINE,
    ),
    "aws_key": re.compile(
        r"(AKIA[0-9A-Z]{16}|(?:aws_)?(?:access_key_id|" r"secret_access_key)\s*=)",
        re.MULTILINE,
    ),
    "github_token": re.compile(
        r"(ghp_[a-zA-Z0-9]{36}|github_token\s*=)",
        re.MULTILINE,
    ),
}

SKIP_DIRS = {".git", ".venv", ".env", "node_modules", "__pycache__"}
SKIP_FILES = {".pre-commit-config.yaml", "check_secrets.py", ".env.example"}


def check_file(filepath: Path) -> list:
    """Check a file for hardcoded secrets."""
    issues = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return issues

    for pattern_name, pattern in SECRET_PATTERNS.items():
        for match in pattern.finditer(content):
            line_num = content[: match.start()].count("\n") + 1
            issues.append(
                {
                    "file": str(filepath),
                    "line": line_num,
                    "type": pattern_name,
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
    for file_arg in argv:
        filepath = Path(file_arg)
        if filepath.is_dir() or any(
            skip_dir in filepath.parts for skip_dir in SKIP_DIRS
        ):
            continue
        if filepath.name in SKIP_FILES:
            continue
        if filepath.suffix == ".py":
            issues = check_file(filepath)
            all_issues.extend(issues)

    if all_issues:
        print("❌ Hardcoded secrets detected:", file=sys.stderr)
        for issue in all_issues:
            print(
                f"  {issue['file']}:{issue['line']} - "
                f"{issue['type']}: {issue['match']}",
                file=sys.stderr,
            )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
