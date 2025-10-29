#!/usr/bin/env python
# noqa: E501
"""Check import safety and security."""

import re
import sys
from pathlib import Path

RISKY_IMPORTS = {
    "pickle": {
        "pattern": re.compile(
            r"^import\s+pickle|^from\s+pickle\s+import",
            re.MULTILINE,
        ),
        "reason": "pickle executes code. Use json/yaml.",
        "severity": "HIGH",
    },
    "marshal": {
        "pattern": re.compile(
            r"^import\s+marshal|^from\s+marshal\s+import",
            re.MULTILINE,
        ),
        "reason": "marshal executes code. Use json.",
        "severity": "HIGH",
    },
    "subprocess_shell": {
        # Match shell=True but exclude comments
        "pattern": re.compile(
            r"^(?!.*#.*shell).*subprocess\.(call|run|Popen).*shell\s*=\s*True",
            re.MULTILINE,
        ),
        "reason": "shell=True is dangerous.",
        "severity": "CRITICAL",
    },
    "os_system": {
        "pattern": re.compile(r"^(?!.*#).*os\.system\s*\(", re.MULTILINE),
        "reason": "os.system is unsafe. Use subprocess.",
        "severity": "HIGH",
    },
    "eval": {
        "pattern": re.compile(r"^(?!.*#).*\beval\s*\(", re.MULTILINE),
        "reason": "eval is dangerous. Never use with user input.",
        "severity": "CRITICAL",
    },
    "exec": {
        "pattern": re.compile(r"^(?!.*#).*\bexec\s*\(", re.MULTILINE),
        "reason": "exec is dangerous. Never use with user input.",
        "severity": "CRITICAL",
    },
}

SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__"}


def check_file(filepath: Path) -> list:
    """Check a file for risky imports."""
    issues = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return issues

    for risk_name, risk_config in RISKY_IMPORTS.items():
        for match in risk_config["pattern"].finditer(content):
            line_num = content[: match.start()].count("\n") + 1
            issues.append(
                {
                    "file": str(filepath),
                    "line": line_num,
                    "risk": risk_name,
                    "reason": risk_config["reason"],
                    "severity": risk_config["severity"],
                    "match": match.group(0),
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
        if filepath.suffix == ".py":
            issues = check_file(filepath)
            all_issues.extend(issues)

    critical = [i for i in all_issues if i["severity"] == "CRITICAL"]
    high = [i for i in all_issues if i["severity"] == "HIGH"]

    if critical:
        print("🚨 CRITICAL import security issues:", file=sys.stderr)
        for issue in critical:
            print(
                f"  {issue['file']}:{issue['line']} - " f"{issue['risk']}",
                file=sys.stderr,
            )
            print(f"    ❌ {issue['reason']}", file=sys.stderr)
        return 1

    if high:
        print("⚠️  HIGH severity import issues:", file=sys.stderr)
        for issue in high:
            print(
                f"  {issue['file']}:{issue['line']} - " f"{issue['risk']}",
                file=sys.stderr,
            )
            print(f"    ⚠️ {issue['reason']}", file=sys.stderr)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
