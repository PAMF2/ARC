# CI/CD Quick Reference Card

## Files Created

```
banking/
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions pipeline
├── .gitignore                        # Git ignore patterns
├── .coveragerc                       # Coverage configuration
├── pytest.ini                        # Pytest configuration
├── SECURITY.md                       # Security policy
├── CI_CD_SETUP_COMPLETE.md          # Full documentation
├── CICD_FILES_SUMMARY.md            # Detailed summary
├── CICD_QUICK_REFERENCE.md          # This file
└── validate_ci_setup.py             # Validation script
```

## Quick Commands

### Validation
```bash
python validate_ci_setup.py          # Validate CI/CD setup
```

### Formatting
```bash
black .                               # Format all Python files
isort .                               # Sort imports
```

### Linting
```bash
flake8 .                              # Lint code
mypy . --ignore-missing-imports       # Type check
```

### Security
```bash
bandit -r . -ll                       # Security scan
safety check                          # Dependency check
```

### Testing
```bash
pytest                                # Run all tests
pytest -m unit                        # Unit tests only
pytest -m integration                 # Integration tests
pytest -m "not slow"                  # Skip slow tests
pytest --cov=. --cov-report=html      # With coverage
```

### CI/CD Check (Run before push)
```bash
black . && isort . && flake8 . && pytest -m "unit and not slow"
```

## Test Markers

```bash
-m unit              # Fast unit tests
-m integration       # Integration tests
-m api               # API tests
-m blockchain        # Blockchain tests
-m ai                # AI/ML tests
-m security          # Security tests
-m circle            # Circle API
-m arc               # Anthropic ARC
-m gemini            # Google Gemini
-m baas              # Banking-as-a-Service
-m smoke             # Quick smoke tests
-m "not slow"        # Skip slow tests
```

## GitHub Setup

### 1. Initialize (if needed)
```bash
git init
git add .
git commit -m "feat: Add CI/CD and security configuration"
```

### 2. Add Remote
```bash
git remote add origin https://github.com/USER/REPO.git
git branch -M main
git push -u origin main
```

### 3. Add Secrets
Settings > Secrets > Actions > New repository secret:
- `ANTHROPIC_API_KEY`
- `CIRCLE_API_KEY`
- `GOOGLE_API_KEY`
- `OPENAI_API_KEY`

### 4. Branch Protection
Settings > Branches > Add rule:
- Branch: `main`
- ✅ Require status checks
- ✅ Require PR reviews

## CI/CD Pipeline

```
┌─────────────────┐
│   Push/PR       │
└────────┬────────┘
         │
    ┌────▼─────┐
    │   Lint   │  Black, isort, Flake8, mypy
    └────┬─────┘
         │
    ┌────▼─────┐
    │ Security │  Bandit, Safety
    └────┬─────┘
         │
    ┌────▼─────┐
    │   Test   │  pytest (3.10, 3.11, 3.13)
    └────┬─────┘
         │
    ┌────▼─────┐
    │Integration│ (main branch only)
    └────┬─────┘
         │
    ┌────▼─────┐
    │  Build   │  Import checks
    └────┬─────┘
         │
    ┌────▼─────┐
    │  Notify  │  Status summary
    └──────────┘
```

## Coverage Reports

After `pytest --cov=. --cov-report=html`:
- **Terminal**: Immediate feedback
- **HTML**: Open `htmlcov/index.html`
- **XML**: `coverage.xml` (for CI)
- **JSON**: `coverage.json` (programmatic)

## Pre-Commit Checklist

- [ ] `black .` (format)
- [ ] `isort .` (imports)
- [ ] `flake8 .` (lint)
- [ ] `pytest -m "unit and not slow"` (tests)
- [ ] No `.env` or secrets committed
- [ ] Update docs if needed

## Pre-PR Checklist

- [ ] All pre-commit checks pass
- [ ] `pytest --cov=.` (full tests)
- [ ] Coverage > 80%
- [ ] `bandit -r . -ll` (security)
- [ ] No critical security issues
- [ ] PR description complete
- [ ] Tests added for new features

## Common Issues

### Lint Fails
```bash
black .
isort .
```

### Tests Fail
```bash
pytest -v --lf  # Re-run last failed
pytest -v -k test_name  # Run specific test
```

### Coverage Low
```bash
pytest --cov=. --cov-report=term-missing  # See missing lines
# Add tests for uncovered code
```

### Security Issues
```bash
bandit -r . -ll  # Review issues
# Fix critical/high severity
```

## File Descriptions

| File | Purpose |
|------|---------|
| `ci.yml` | GitHub Actions pipeline |
| `.gitignore` | Git ignore patterns |
| `.coveragerc` | Coverage config |
| `pytest.ini` | Test config |
| `SECURITY.md` | Security policy |
| `validate_ci_setup.py` | Validation tool |

## Key Features

- ✅ Multi-Python version testing (3.10, 3.11, 3.13)
- ✅ Code formatting (Black, isort)
- ✅ Code quality (Flake8, mypy)
- ✅ Security scanning (Bandit, Safety)
- ✅ Test coverage reporting
- ✅ Integration tests
- ✅ 20+ test markers
- ✅ Comprehensive .gitignore
- ✅ Professional security policy

## Support

- Full docs: `CI_CD_SETUP_COMPLETE.md`
- Detailed summary: `CICD_FILES_SUMMARY.md`
- This reference: `CICD_QUICK_REFERENCE.md`

## Status

✅ **Complete** - All files created and validated
⏭️ **Next**: Push to GitHub and configure secrets

---
**Last Updated**: January 19, 2026
