# Contributing to Odoo MCP Server

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/itbrasil-odoo/mcp-odoo.git
   cd mcp-odoo
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   pip install pre-commit black isort flake8 mypy pytest
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## Development Workflow

### Code Style

We use several tools to maintain code quality:

- **Black**: Code formatting (88 char line length)
- **isort**: Import sorting
- **flake8**: Linting (with E501, W503 ignored)
- **bandit**: Security scanning
- **mypy**: Type checking

All checks run automatically via pre-commit hooks before each commit.

### Running Checks Manually

```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Run individual tools
black .
isort .
flake8 app.py simple_server.py src/
bandit -r src/ -ll
mypy src/ --ignore-missing-imports
```

### Testing

```bash
# Validate syntax
python -m py_compile app.py simple_server.py src/odoo_mcp/*.py

# Test imports
python -c "import sys; sys.path.insert(0, 'src'); from odoo_mcp.server import mcp"

# Run pytest (when available)
pytest tests/ -v --cov=src/odoo_mcp
```

### Testing with Odoo

For integration testing with Odoo:

```bash
# Using Docker
docker run -d --name odoo17 -p 8069:8069 \
  -e HOST=localhost -e PORT=8069 \
  -e USER=odoo -e PASSWORD=odoo \
  odoo:17

# Configure environment
export ODOO_URL=http://localhost:8069
export ODOO_DB=odoo
export ODOO_USERNAME=admin
export ODOO_PASSWORD=admin

# Run server
python run_server.py
```

## Pull Request Process

1. **Create a feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**

   - Follow the code style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Run checks**

   ```bash
   pre-commit run --all-files
   ```

4. **Commit your changes**

   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

   Follow [Conventional Commits](https://www.conventionalcommits.org/):

   - `feat:` new feature
   - `fix:` bug fix
   - `docs:` documentation changes
   - `style:` formatting changes
   - `refactor:` code refactoring
   - `test:` test additions/changes
   - `chore:` maintenance tasks

5. **Push and create PR**

   ```bash
   git push origin feature/your-feature-name
   ```

   Then create a Pull Request on GitHub.

## CI/CD Pipeline

Our CI/CD pipeline includes:

### Pre-commit (`pre-commit.yml`)

- Runs all pre-commit hooks
- Executes on every push and PR

### CI (`ci.yml`)

- **Lint**: Black, isort, flake8, bandit
- **Type Check**: mypy type checking
- **Tests**: Python 3.10, 3.11, 3.12
- **Security**: Custom security checks
- **Build**: Package build and validation

### Odoo Integration (`odoo-integration.yml`)

- Tests with Odoo 16 and 17
- Uses official Odoo Docker images
- PostgreSQL service container
- Real integration tests

### Publish (`publish.yml`)

- Builds and publishes to PyPI
- Triggered on release

## Security

### Security Checks

Our pipeline includes several security checks:

1. **Hardcoded Secrets** (`scripts/check_secrets.py`)

   - Detects hardcoded API keys, passwords, tokens

2. **MCP Security** (`scripts/check_mcp_security.py`)

   - Validates MCP best practices
   - Checks for unsafe bindings, missing timeouts

3. **Import Safety** (`scripts/check_import_security.py`)
   - Detects dangerous imports and patterns

### Reporting Security Issues

Please report security vulnerabilities to the maintainers privately via GitHub Security Advisories.

## Code Review Guidelines

Reviewers should check:

- [ ] Code follows style guidelines (pre-commit passes)
- [ ] Tests pass (CI green)
- [ ] Documentation updated
- [ ] Security checks pass
- [ ] Commit messages follow conventions
- [ ] No breaking changes (or properly documented)

## Questions?

Feel free to open an issue for questions or discussions!
