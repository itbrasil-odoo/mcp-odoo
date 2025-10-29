# Pre-commit Hooks Configuration for MCP Server

This repository uses **pre-commit hooks** to enforce code quality, security, and formatting standards based on **Model Context Protocol (MCP) Security Best Practices**.

## Quick Start

### 1. Install pre-commit
```bash
pip install pre-commit
```

### 2. Install hooks
```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

### 3. Run hooks manually (optional)
```bash
# Run on staged files
pre-commit run

# Run on all files
pre-commit run --all-files
```

## Configured Hooks

### Code Formatting & Linting
- **Black**: Automatic Python code formatting (line length: 88 chars)
- **isort**: Automatic import organization (Black compatible)
- **autoflake**: Remove unused imports and variables

### Security Scanning
- **Bandit**: Detect common security issues in Python code
- **detect-private-key**: Prevent accidental private key commits

### File Validation
- **check-yaml**: Validate YAML syntax
- **check-json**: Validate JSON syntax
- **check-toml**: Validate TOML syntax
- **end-of-file-fixer**: Ensure files end with newline
- **trailing-whitespace**: Remove trailing whitespace
- **check-merge-conflict**: Detect unresolved merge conflicts

### Custom MCP Security Checks

Three custom scripts validate MCP-specific security requirements:

#### 1. Check for Hardcoded Secrets
- **Script**: `scripts/check_secrets.py`
- **Detects**: API keys, tokens, passwords, AWS keys, GitHub tokens, database URLs
- **Reference**: [MCP Security - Never expose tokens](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices)

#### 2. Check MCP Security Best Practices
- **Script**: `scripts/check_mcp_security.py`
- **Detects**:
  - Token passthrough vulnerabilities
  - Unsafe command execution (subprocess shell=True)
  - Hardcoded localhost/IP addresses
- **Reference**: [MCP Best Practices - Defense in Depth](https://modelcontextprotocol.info/docs/best-practices/)

#### 3. Check Import Safety
- **Script**: `scripts/check_import_security.py`
- **Detects**:
  - Dangerous imports: `pickle`, `marshal` (code execution risk)
  - Unsafe functions: `eval()`, `exec()` (arbitrary code execution)
  - Shell execution patterns: `subprocess.Popen(..., shell=True)`, `os.system()`

## Configuration Files

### `.pre-commit-config.yaml`
Main configuration file defining all hooks and their settings.

### `.bandit.yaml`
Bandit security scanner configuration:
- Test selection and exclusions
- Skip rules for low-risk patterns

### `.secrets.baseline`
Baseline file for `detect-secrets`:
- Initializes secret detection rules
- Supports: AWS keys, GitHub tokens, JWTs, and more

### `scripts/` Directory
Custom security check implementations:
- `check_secrets.py` - Detects hardcoded credentials
- `check_mcp_security.py` - Validates MCP security patterns
- `check_import_security.py` - Ensures safe imports

## Workflow

### Before committing:
1. **Hooks run automatically** (via `.git/hooks/pre-commit`)
2. **Files are auto-fixed** (Black, isort, autoflake)
3. **If errors occur**, commit is blocked
4. **Review changes and commit again**

### Example:
```bash
$ git commit -m "feat: add new endpoint"

# Pre-commit hooks execute...
# Black reformats code ✅
# isort reorganizes imports ✅
# Bandit finds unsafe pattern ❌ BLOCKED

$ git add . && git commit -m "feat: add new endpoint"  # Retry after fix
```

## Security - What Gets Blocked

### CRITICAL (Blocks commit)
- `eval()`, `exec()` in code
- `subprocess(..., shell=True)`
- Private keys in files
- Hardcoded secrets/credentials

### HIGH (Blocks commit)
- Unsafe imports: `pickle`, `marshal`
- `os.system()` calls
- Suspected token passthrough patterns

### MEDIUM (Warning only)
- Hardcoded localhost addresses
- Dynamic imports with variables

## Bypass (Use with caution)

```bash
# Skip all pre-commit checks (NOT RECOMMENDED)
git commit --no-verify -m "message"

# Skip specific hook
SKIP=bandit git commit -m "message"
```

## MCP Security Best Practices Applied

### Defense in Depth
Multi-layer security validation:
- Network: No hardcoded endpoints
- Code: No unsafe imports/execution
- Credentials: No secrets in code
- Format: Consistent, auditable code

### Local MCP Server Compromise Prevention
- Detects unsafe subprocess calls
- Identifies command injection vectors
- Prevents dangerous code patterns

### Token Passthrough Prevention
- Detects suspicious token handling
- Ensures tokens are validated, not passed through

### Scope Minimization
- Removes unused imports automatically
- Uses only necessary/safe imports

## Troubleshooting

### Hook not running
```bash
pre-commit install  # Reinstall
```

### Stale cache
```bash
pre-commit clean  # Clear cache
```

### Update hooks
```bash
pre-commit autoupdate
```

### Suppress specific checks
Use `noqa` comments for false positives:
```python
# Skip Bandit check S307
parsed = ast.literal_eval(data)  # noqa: S307

# Skip trailing whitespace
value = something  # noqa
```

## References

- [MCP Security Best Practices](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices)
- [MCP Implementation Guide](https://modelcontextprotocol.info/docs/best-practices/)
- [pre-commit Documentation](https://pre-commit.com)
- [Black Code Formatter](https://github.com/psf/black)
- [Bandit Security Scanner](https://bandit.readthedocs.io)
- [detect-secrets](https://github.com/Yelp/detect-secrets)

---

**Status**: ✅ Production Ready
**Last Updated**: 2025-10-29
