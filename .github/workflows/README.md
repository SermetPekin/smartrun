# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automated testing, building, and publishing of smartrun.

## Workflows Overview

### 1. `test.yml` - Main Test Suite
**Triggers:** Push to main, Pull Requests
**Purpose:** Run comprehensive tests across multiple Python versions and operating systems

**What it does:**
- Tests on Python 3.10, 3.11, 3.12, 3.13
- Tests on Ubuntu, macOS, and Windows
- Uses UV for fast dependency installation with caching
- Runs all test suites:
  - General pytest tests
  - Timeout parameter tests
  - Notebook timeout tests
  - HTML parameter tests
  - CLI integration tests
- Runs example scripts to verify functionality
- Uploads test artifacts (on Ubuntu + Python 3.11)

**Key features:**
- Matrix testing across OS and Python versions
- UV caching for faster runs
- Comprehensive test coverage

---

### 2. `build.yml` - Build and Publish to PyPI
**Triggers:** Git tags matching `v*` (e.g., v1.0.0)
**Purpose:** Build and publish releases to PyPI

**What it does:**
1. **Build job:**
   - Uses UV to build the package
   - Creates wheel and sdist distributions
   - Uploads distributions as artifacts

2. **Test-build job:**
   - Downloads built distributions
   - Installs from wheel
   - Verifies installation and version

3. **Publish-to-pypi job:**
   - Downloads verified distributions
   - Publishes to PyPI using trusted publishing (no API token needed)

**Key features:**
- UV-based building (faster than pip)
- Artifact storage and reuse between jobs
- Test built package before publishing
- Trusted publishing (OIDC) - no manual API token management
- Only runs on version tags

---

### 3. `lint.yml` - Code Quality Checks
**Triggers:** Push to main, Pull Requests
**Purpose:** Enforce code quality standards

**What it does:**
- Runs flake8 for syntax errors and code quality
- Checks formatting with black (optional)
- Type checking with mypy (optional)
- Uses UV for dependency management

**Key features:**
- Fast with UV caching
- Strict checks for critical errors
- Optional checks for formatting/types

---

### 4. `smoke-test.yml` - PyPI Installation Tests
**Triggers:** Push to main, Pull Requests, Manual
**Purpose:** Verify published package works correctly

**What it does:**
- Tests on Python 3.10, 3.11, 3.12
- Installs latest smartrun from PyPI (not from source)
- Runs smoke tests:
  - Basic script execution
  - Package installation
  - Adding packages
  - Notebook execution
  - HTML generation from notebooks
  - Timeout parameter functionality

**Key features:**
- Tests actual PyPI package
- Verifies all major features work
- Can be triggered manually
- Uses UV for faster installation

---

## UV Benefits

All workflows use [UV](https://github.com/astral-sh/uv) instead of pip:

### Speed Improvements:
- **10-100x faster** than pip for dependency resolution
- **Parallel downloads** of packages
- **Efficient caching** between workflow runs
- **Faster builds** with `uv build`

### GitHub Actions Integration:
```yaml
- name: Set up uv
  uses: astral-sh/setup-uv@v5
  with:
    enable-cache: true
    cache-dependency-glob: "pyproject.toml"
```

### Common UV Commands Used:
```bash
uv sync --all-extras --dev    # Install all dependencies
uv run pytest -v               # Run tests in virtual environment
uv build                       # Build package distributions
uv pip install --system pkg    # System-wide installation
```

---

## Workflow Triggers Summary

| Workflow | Push to main | Pull Request | Git Tag | Manual |
|----------|-------------|--------------|---------|--------|
| test.yml | Yes | Yes | No | No |
| build.yml | No | No | Yes (v*) | No |
| lint.yml | Yes | Yes | No | No |
| smoke-test.yml | Yes | Yes | No | Yes |

---

## Setting Up Trusted Publishing (for build.yml)

To use trusted publishing (no API token needed):

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new publisher:
   - **PyPI Project Name:** smartrun
   - **Owner:** your-github-username
   - **Repository:** smartrun
   - **Workflow:** build.yml
   - **Environment:** pypi

3. Create environment in GitHub:
   - Go to Settings → Environments → New environment
   - Name: `pypi`
   - Add protection rules if desired

---

## Local Testing

You can test the workflows locally using [act](https://github.com/nektos/act):

```bash
# Install act
brew install act  # macOS
# or download from https://github.com/nektos/act/releases

# Run tests workflow
act push -W .github/workflows/test.yml

# Run lint workflow
act push -W .github/workflows/lint.yml
```

---

## Migration from Old Workflows

### Deprecated Workflows:
- `python-package.yml` → Replaced by `test.yml`
- `pak.yml` → Replaced by `test.yml`
- `pub.yml` → Replaced by `build.yml`
- `pypi.yml` → Replaced by `smoke-test.yml`

You can safely delete the old workflow files after verifying the new ones work correctly.

---

## Performance Comparison

**Old workflow (pip):**
- Install dependencies: ~2-3 minutes
- Run tests: ~1-2 minutes
- **Total: ~4-5 minutes**

**New workflow (UV):**
- Install dependencies: ~10-20 seconds (with cache: ~5 seconds)
- Run tests: ~1-2 minutes
- **Total: ~1.5-2.5 minutes**

**Speed improvement: 2-3x faster**

---

## Troubleshooting

### Cache Issues
If UV cache causes problems, you can disable it:
```yaml
- name: Set up uv
  uses: astral-sh/setup-uv@v5
  with:
    enable-cache: false
```

### Dependency Resolution Errors
If UV fails to resolve dependencies, check `pyproject.toml` for:
- Conflicting version constraints
- Missing dependencies
- Incorrect extras definitions

### Build Failures
If `uv build` fails:
- Ensure `pyproject.toml` has correct build-system configuration
- Check that all files are included in the package
- Verify version numbers are valid

---

## Future Improvements

Potential enhancements:
- Add coverage reporting with codecov
- Add security scanning (e.g., bandit, safety)
- Add documentation building and publishing
- Add benchmarking workflow
- Add release notes generation
