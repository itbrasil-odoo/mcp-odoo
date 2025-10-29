# Security Best Practices

This document outlines the security measures implemented in the Odoo MCP Server following the [Model Context Protocol Security Best Practices](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices).

## 🔒 Security Measures Implemented

### 1. Authentication & Authorization

- **No Token Passthrough**: The MCP server validates that tokens are issued specifically for it, not passing through upstream tokens
- **Session Security**: Sessions use secure, non-deterministic UUIDs
- **User Binding**: Sessions are bound to user-specific information from authenticated tokens

### 2. Network Security

- **Configurable Binding**: Server binding defaults to `127.0.0.1` (localhost only) and is configurable via `HOST` environment variable
- **SSL/TLS Verification**: SSL verification is enabled by default; disabling it triggers security warnings
- **Request Timeouts**: All HTTP requests include timeouts to prevent hanging connections

### 3. Input Validation & Sanitization

- **No eval/exec**: Code does not use `eval()` or `exec()` with user input
- **No shell=True**: Subprocess calls avoid `shell=True` to prevent command injection
- **Schema Validation**: Input validation using Pydantic models

### 4. Code Security

- **No Hardcoded Secrets**: All credentials come from environment variables or config files
- **Import Safety**: No use of `pickle`, `marshal`, or other unsafe serialization
- **Security Scanning**: Pre-commit hooks include bandit, secret detection, and custom MCP security checks

### 5. Development vs Production

- **Development Warnings**: Features like SSL bypass show explicit warnings
- **Environment Separation**: Configuration separated by environment (dev/staging/prod)
- **Secure Defaults**: All security features enabled by default

## 🛡️ Pre-commit Security Checks

The following automated checks run on every commit:

1. **Bandit** - Python security linter
2. **Secret Detection** - Detects hardcoded credentials
3. **MCP Security** - Custom checks for MCP-specific vulnerabilities:
   - Token passthrough detection
   - Unsafe command execution patterns
   - Hardcoded localhost URLs
4. **Import Safety** - Validates no dangerous imports (pickle, eval, exec, etc.)

## 📋 Security Checklist

Before deploying to production:

- [ ] Environment variables configured (no hardcoded credentials)
- [ ] SSL verification enabled (`ODOO_VERIFY_SSL=true`)
- [ ] Server binding restricted (`HOST=127.0.0.1` or VPN IP)
- [ ] Authentication enabled on MCP client
- [ ] All pre-commit hooks passing
- [ ] No secrets in git history
- [ ] Dependencies updated to latest secure versions

## 🚨 Reporting Security Issues

If you discover a security vulnerability, please email the maintainers directly instead of opening a public issue.

## 📚 References

- [MCP Security Best Practices](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices)
- [MCP Best Practices Guide](https://modelcontextprotocol.info/docs/best-practices/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

## 🔄 Security Updates

This document is updated as new security measures are implemented. Last updated: 2025-10-29
