# 🚀 GitHub Actions CI/CD Documentation

## 📋 Workflow Overview

Our GitHub Actions setup provides comprehensive automation for:
- **Continuous Integration (CI)**: Testing, linting, security checks
- **Continuous Deployment (CD)**: Publishing to PyPI
- **Maintenance**: Dependency updates, security monitoring
- **Performance**: Benchmarking and performance regression detection

## 🔄 Workflows

### 1. CI/CD Pipeline (`ci.yml`)
**Triggers:** Push to `main`, `develop`, `feature/*` branches and PRs

**Jobs:**
- **Test Matrix**: Python 3.8-3.12 on Ubuntu, Windows, macOS
- **Linting**: `ruff check`, `black --check`, `mypy`  
- **Security**: `bandit` and `safety` security audits
- **Build**: Package building and validation with `twine`
- **Coverage**: Code coverage reporting to Codecov

**Artifacts:**
- Test results and coverage reports
- Security audit reports
- Built packages (wheel and source distribution)

### 2. PyPI Publishing (`publish.yml`)
**Triggers:** 
- Automatic on GitHub releases
- Manual dispatch with environment selection (testpypi/pypi)

**Features:**
- ✅ Test PyPI deployment for validation
- ✅ Production PyPI deployment on releases
- ✅ Trusted publishing (no API keys needed)
- ✅ Package checksums and release assets
- ✅ Automated release note generation

### 3. Security & Dependencies (`security.yml`)
**Triggers:**
- Weekly automated runs (Mondays 9 AM UTC)
- Manual dispatch
- Pull request dependency review

**Features:**
- 📊 `pip-audit`, `safety`, and `bandit` security scans
- 🔄 Automated dependency update PRs
- 🚨 Automatic security issue creation on vulnerabilities
- 📋 Dependency review on PRs

### 4. Performance Testing (`performance.yml`)
**Triggers:**
- Push to main branches
- Weekly performance monitoring
- Pull request performance regression checks

**Features:**
- ⚡ Import speed benchmarking
- 💾 Memory profiling with `memory-profiler`
- 📊 Performance regression detection
- 🎯 Automated performance reports

## 🏗️ Workflow Dependencies

### Required Secrets
```yaml
# For PyPI publishing
PYPI_API_TOKEN         # Production PyPI token
TEST_PYPI_API_TOKEN    # Test PyPI token

# For code coverage
CODECOV_TOKEN          # Codecov upload token
```

### Repository Settings
```yaml
# Branch protection rules
- Require status checks: CI/CD Pipeline
- Require up-to-date branches
- Require signed commits (recommended)

# Environments
- testpypi: Test PyPI deployment
- pypi: Production PyPI deployment  
```

## 📊 Status Badges

Add these to your README.md:

```markdown
[![CI/CD Pipeline](https://github.com/yourusername/questionary-extended/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/questionary-extended/actions/workflows/ci.yml)
[![Publish to PyPI](https://github.com/yourusername/questionary-extended/actions/workflows/publish.yml/badge.svg)](https://github.com/yourusername/questionary-extended/actions/workflows/publish.yml)
[![Security Audit](https://github.com/yourusername/questionary-extended/actions/workflows/security.yml/badge.svg)](https://github.com/yourusername/questionary-extended/actions/workflows/security.yml)
[![Performance](https://github.com/yourusername/questionary-extended/actions/workflows/performance.yml/badge.svg)](https://github.com/yourusername/questionary-extended/actions/workflows/performance.yml)
[![codecov](https://codecov.io/gh/yourusername/questionary-extended/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/questionary-extended)
```

## 🚀 Deployment Process

### Development Flow
1. **Feature Development**: Work on `feature/*` branches
2. **Pull Request**: CI runs full test suite + security checks
3. **Code Review**: Manual review + automated checks
4. **Merge**: Merge to `develop` branch
5. **Release Preparation**: Merge `develop` → `main`
6. **Release**: Create GitHub release → Automatic PyPI deployment

### Publishing to PyPI
```bash
# Test deployment (manual)
gh workflow run publish.yml -f environment=testpypi

# Production deployment (automatic on release)
gh release create v0.1.0 --title "v0.1.0" --notes "Release notes"
```

## 🔧 Local Development Setup

### Install Development Dependencies
```bash
# Install with all development dependencies
pip install -e ".[dev]"

# Or install specific dependency groups
pip install -e ".[test,quality,security]"
```

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### Manual Quality Checks
```bash
# Run the same checks as CI
ruff check src/ tests/
black --check src/ tests/
mypy src/
pytest --cov=questionary_extended
bandit -r src/
safety check
```

## 📈 Monitoring & Maintenance

### Weekly Automated Tasks
- Dependency vulnerability scanning
- Dependency update PR creation  
- Performance benchmark collection
- Security audit reporting

### Manual Maintenance
- Review and merge dependency update PRs
- Address security vulnerabilities
- Monitor performance trends
- Update documentation

## 🛡️ Security Best Practices

### Implemented Security Measures
- ✅ Automated dependency vulnerability scanning
- ✅ Code security analysis with Bandit
- ✅ Dependency review on PRs
- ✅ Trusted PyPI publishing (no stored tokens)
- ✅ Minimal permissions for workflows
- ✅ Signed releases with checksums

### Security Response
1. **Automated Detection**: Security workflows create issues for vulnerabilities
2. **Assessment**: Evaluate severity and impact
3. **Patching**: Apply fixes via dependency updates or code changes
4. **Testing**: Verify fixes don't break functionality  
5. **Release**: Deploy security updates promptly

## 🎯 Performance Monitoring

### Tracked Metrics
- **Import Speed**: Cold import and specific import timing
- **Memory Usage**: Memory profiling of core functions
- **Benchmark Results**: Performance test execution times
- **Regression Detection**: Comparison with baseline performance

### Performance Goals
- Import time: < 50ms cold import
- Memory usage: < 10MB for typical operations
- Test suite: < 2 minutes full execution
- Package size: < 1MB wheel size

## 📝 Troubleshooting

### Common Issues
1. **Failed Tests**: Check Python version compatibility matrix
2. **Security Alerts**: Review dependency updates and security patches
3. **Publishing Failures**: Verify version increments and package metadata
4. **Performance Regressions**: Check for inefficient code changes

### Debug Commands
```bash
# Check workflow status
gh workflow list
gh run list --workflow=ci.yml

# Download artifacts
gh run download <run-id>

# View logs
gh run view <run-id> --log
```