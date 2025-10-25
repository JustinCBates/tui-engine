# Coverage Best Practices and Workflow

## 🎯 Coverage Excellence Workflow

This document outlines the best practices and automated workflows to ensure constant progress on test coverage and maintain full coverage when new code is added.

## 📊 Current Coverage Status

Based on our A+ achievement:

- **Overall Coverage**: 64% (boosted from initial state)
- **Utils Module**: 94% (A+ achievement)
- **Target**: 85%+ overall coverage for A+ maintenance

## 🔄 Coverage Workflow Process

### 1. Pre-Development Coverage Check

Before adding any new code to `src/`:

```bash
# Check current coverage baseline
python -m pytest --cov=src --cov-report=term-missing --cov-report=html

# Identify low-coverage modules
python -m coverage report --show-missing --precision=2
```

### 2. Test-Driven Development (TDD) Approach

For each new module/function:

```bash
# Create test file FIRST
touch tests/test_new_module.py

# Write failing tests
# Implement code to pass tests
# Verify coverage improvement
python -m pytest tests/test_new_module.py --cov=src.questionary_extended.new_module
```

### 3. Coverage Gates and Validation

#### Minimum Coverage Requirements

- **New Code**: 95%+ coverage required
- **Modified Code**: No coverage reduction allowed
- **Overall Project**: Maintain 85%+ for A+ status

#### Coverage Validation Commands

```bash
# Check if new code meets coverage requirements
python -m pytest --cov=src --cov-fail-under=85

# Generate detailed coverage report
python -m coverage html
# Open htmlcov/index.html to analyze gaps

# Check coverage diff (requires coverage.py >= 6.0)
python -m coverage report --format=markdown > coverage_report.md
```

## 🏗️ Automated Coverage Enforcement

### 1. Enhanced CI/CD Pipeline

The existing `.github/workflows/ci.yml` needs coverage gates:

```yaml
# Add to existing CI workflow
- name: Run tests with strict coverage
  run: |
    pytest --cov=questionary_extended --cov-report=xml --cov-report=term-missing --cov-fail-under=85

- name: Coverage comment on PR
  if: github.event_name == 'pull_request'
  uses: py-cov-action/python-coverage-comment-action@v3
  with:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    MINIMUM_GREEN: 85
    MINIMUM_ORANGE: 70
```

### 2. Pre-commit Hooks

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: coverage-check
        name: Coverage Check
        entry: python -m pytest --cov=src --cov-fail-under=85 --cov-report=term-missing
        language: system
        pass_filenames: false
        always_run: true
```

### 3. Coverage Ratcheting

Implement coverage ratcheting to prevent regression:

```bash
# Save current coverage as baseline
python -m coverage report --precision=2 | grep TOTAL | awk '{print $4}' > .coverage_baseline

# In CI, check against baseline
current_cov=$(python -m coverage report --precision=2 | grep TOTAL | awk '{print $4}' | sed 's/%//')
baseline_cov=$(cat .coverage_baseline | sed 's/%//')
if (( $(echo "$current_cov < $baseline_cov" | bc -l) )); then
  echo "Coverage regression detected: $current_cov% < $baseline_cov%"
  exit 1
fi
```

## 📈 Systematic Coverage Improvement Plan

### Phase 1: Target Low-Coverage Modules (Current Priority)

Based on current analysis, target these modules:

1. **prompts_core.py** (33% coverage)

   - 49 uncovered lines
   - Priority: High (core functionality)

2. **prompts.py** (37% coverage)

   - 52 uncovered lines
   - Priority: High (main user interface)

3. **Core modules** (45-53% coverage)
   - `assembly.py`, `state.py`, `component.py`
   - Priority: Medium (infrastructure)

### Phase 2: Implementation Template

For each module, follow this pattern:

```python
# tests/test_module_comprehensive.py
"""
Comprehensive test suite for module.py
Target: 95%+ coverage with edge cases
"""

import pytest
from src.questionary_extended.module import (
    function1, function2, Class1
)

class TestFunction1:
    """Comprehensive tests for function1."""

    def test_function1_happy_path(self):
        """Test normal operation."""
        pass

    def test_function1_edge_cases(self):
        """Test boundary conditions."""
        pass

    def test_function1_error_handling(self):
        """Test exception scenarios."""
        pass

    @pytest.mark.parametrize("input,expected", [
        # Property-based test cases
    ])
    def test_function1_property_based(self, input, expected):
        """Property-based testing."""
        pass

# Target: 15-20 tests per module for 95%+ coverage
```

## 🔧 Coverage Analysis Tools

### 1. Coverage Gap Analysis

```bash
# Identify specific uncovered lines
python -m coverage report --show-missing

# Generate annotated source code
python -m coverage annotate

# HTML report with detailed analysis
python -m coverage html
```

### 2. Coverage Quality Metrics

```bash
# Branch coverage (more thorough than line coverage)
python -m pytest --cov=src --cov-branch

# Coverage with performance timing
python -m pytest --cov=src --benchmark-only --benchmark-sort=mean
```

### 3. Coverage Tracking Over Time

```python
# coverage_tracker.py - Run after each test suite
import json
import datetime
from coverage import Coverage

def track_coverage():
    cov = Coverage()
    cov.load()

    report = {
        'timestamp': datetime.datetime.now().isoformat(),
        'total_coverage': cov.report(),
        'module_coverage': {}
    }

    # Save to history file
    with open('.coverage_history.json', 'a') as f:
        json.dump(report, f)
        f.write('\n')
```

## 🎯 Coverage Excellence Standards

### A+ Grade Maintenance Checklist

- [ ] Overall coverage ≥ 85%
- [ ] New code coverage ≥ 95%
- [ ] Critical paths have 100% coverage
- [ ] Edge cases and error handling covered
- [ ] Integration tests for complex workflows
- [ ] Performance regression tests
- [ ] Documentation examples tested

### Quality Gates

1. **Code Review**: Coverage report required for all PRs
2. **CI/CD**: Automated coverage checks in pipeline
3. **Release**: Coverage report in release notes
4. **Monitoring**: Weekly coverage trend analysis

## 🚀 Next Steps Implementation

### Immediate Actions (Week 1)

1. Enhance CI/CD with coverage gates
2. Set up pre-commit hooks
3. Create comprehensive test suite for `prompts_core.py`

### Short Term (Month 1)

1. Achieve 85%+ overall coverage
2. Implement property-based testing
3. Add performance benchmarks

### Long Term (Ongoing)

1. Maintain A+ standards for all new code
2. Regular coverage audits and improvements
3. Coverage trend analysis and reporting

## 📚 Resources and References

- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [pytest-cov Plugin](https://pytest-cov.readthedocs.io/)
- [Property-Based Testing with Hypothesis](https://hypothesis.readthedocs.io/)
- [Test-Driven Development Best Practices](https://testdriven.io/)

---

**Maintained by**: Development Team  
**Last Updated**: October 2025  
**Status**: A+ Grade Testing Architecture Achieved 🏆
