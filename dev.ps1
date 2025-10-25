<#
Developer helper script for Windows PowerShell.

Usage:
  .\dev.ps1 -Action test
  .\dev.ps1 -Action coverage
  .\dev.ps1 -Action run-example
  .\dev.ps1 -Action setup-hooks

This script centralizes common development commands in a PowerShell-safe
form so contributors can copy/paste robust commands instead of ad-hoc
shell snippets that may be platform-specific.
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('test','coverage','run-example','setup-hooks')]
    [string]$Action
)

# Ensure gh (GitHub CLI) is available in this PowerShell session by adding
# common install locations to the PATH if necessary. This is session-only
# and non-destructive.
function Ensure-GhOnPath {
    if (Get-Command gh -ErrorAction SilentlyContinue) { return }

    $candidates = @(
        "$env:LOCALAPPDATA\Programs\GitHub CLI",
        "$env:ProgramFiles\GitHub CLI",
        "$env:ProgramFiles(x86)\GitHub CLI"
    )

    foreach ($dir in $candidates) {
        if ($null -ne $dir -and (Test-Path (Join-Path $dir 'gh.exe'))) {
            Write-Host "Adding GitHub CLI to PATH from: $dir" -ForegroundColor Green
            $env:PATH = $dir + ';' + $env:PATH
            return
        }
    }

    Write-Host "GitHub CLI ('gh') not found in common locations; ensure it's installed or on PATH." -ForegroundColor Yellow
}

# call early so following commands can use gh if needed
Ensure-GhOnPath

function Run-Tests {
    Write-Host "Running pytest (unit tests)..." -ForegroundColor Cyan
    python -m pytest --maxfail=1 --disable-warnings -q
}

# Run a moderate subset of tests that focus on questionary/prompts/components/cli
function Run-ModerateTests {
    Write-Host "Running moderate questionary-related pytest subset..." -ForegroundColor Cyan
    # Use a pytest -k expression that is PowerShell-safe (single quotes)
    python -m pytest -q tests/unit -k 'questionary or prompts or component or cli'
}
function Run-Coverage {
    Write-Host "Running pytest with coverage..." -ForegroundColor Cyan
    python -m pytest --cov=src --cov-report=term-missing --cov-report=html
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Coverage HTML available at ./htmlcov/index.html" -ForegroundColor Green
    }
}

function Run-Example {
    Write-Host "Running basic example (examples/basic_usage.py)" -ForegroundColor Cyan
    python .\examples\basic_usage.py
}

function Setup-Hooks {
    Write-Host "Installing pre-commit hooks (requires Python & pip)" -ForegroundColor Cyan
    # Try user install first; if it fails, try a system/user-agnostic install.
    & python -m pip install --user pre-commit
    if ($LASTEXITCODE -ne 0) {
        Write-Host "User install failed, attempting fallback install..." -ForegroundColor Yellow
        & python -m pip install pre-commit
    }

    if (Get-Command pre-commit -ErrorAction SilentlyContinue) {
        pre-commit install
        Write-Host "pre-commit installed." -ForegroundColor Green
    } else {
        Write-Host "pre-commit not found on PATH; please ensure your Python user scripts dir is on PATH." -ForegroundColor Yellow
    }
}

switch ($Action) {
    'test' { Run-Tests }
    'coverage' { Run-Coverage }
    'run-example' { Run-Example }
    'setup-hooks' { Setup-Hooks }
}
# TUI-Engine Development PowerShell Script
# Provides convenient commands for maintaining A+ testing standards on Windows

param(
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "🏆 TUI-Engine A+ Testing PowerShell Helper" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Coverage Commands:" -ForegroundColor Cyan
    Write-Host "  .\dev.ps1 coverage          - Run tests with coverage (A+ gate: 85%+)"
    Write-Host "  .\dev.ps1 coverage-report   - Generate detailed coverage report"
    Write-Host "  .\dev.ps1 coverage-track    - Track coverage history"
    Write-Host "  .\dev.ps1 coverage-html     - Generate HTML coverage report"
    Write-Host ""
    Write-Host "🧪 Testing Commands:" -ForegroundColor Yellow
    Write-Host "  .\dev.ps1 test              - Run all tests"
    Write-Host "  .\dev.ps1 test-fast         - Run tests with fail-fast"
    Write-Host ""
    Write-Host "🔧 Development Commands:" -ForegroundColor Magenta
    Write-Host "  .\dev.ps1 install           - Install package in development mode"
    Write-Host "  .\dev.ps1 dev-install       - Install with all development dependencies"
    Write-Host "  .\dev.ps1 lint              - Run linting (ruff)"
    Write-Host "  .\dev.ps1 format            - Format code (black + isort)"
    Write-Host "  .\dev.ps1 type-check        - Run type checking (mypy)"
    Write-Host ""
    Write-Host "⚙️ Setup Commands:" -ForegroundColor Blue
    Write-Host "  .\dev.ps1 setup-hooks       - Install pre-commit hooks"
    Write-Host "  .\dev.ps1 validate-aplus    - Validate A+ grade requirements"
    Write-Host "  .\dev.ps1 clean             - Clean build artifacts"
}

function Invoke-Coverage {
    Write-Host "🎯 Running tests with A+ coverage standard (85%+)..." -ForegroundColor Green
    python -m pytest --cov=src --cov-report=term-missing --cov-fail-under=85
}

function Invoke-CoverageReport {
    Write-Host "📊 Generating comprehensive coverage report..." -ForegroundColor Green
    python scripts/coverage_tracker.py --report
}

function Invoke-CoverageTrack {
    Write-Host "📈 Tracking coverage history..." -ForegroundColor Green
    python scripts/coverage_tracker.py --track
}

function Invoke-CoverageHtml {
    Write-Host "🌐 Generating HTML coverage report..." -ForegroundColor Green
    python -m pytest --cov=src --cov-report=html
    Write-Host "Report available at: htmlcov/index.html" -ForegroundColor Yellow
}

function Invoke-Test {
    Write-Host "🧪 Running all tests..." -ForegroundColor Green
    python -m pytest
}

function Invoke-TestFast {
    Write-Host "⚡ Running tests with fail-fast..." -ForegroundColor Green
    python -m pytest -x
}

# PowerShell-friendly wrapper for the moderate questionary-focused test subset
function Invoke-ModerateTests {
    Write-Host "🧪 Running moderate questionary-related tests..." -ForegroundColor Green
    python -m pytest -q tests/unit -k 'questionary or prompts or component or cli'
}

function Invoke-Install {
    Write-Host "📦 Installing package in development mode..." -ForegroundColor Green
    pip install -e .
}

function Invoke-DevInstall {
    Write-Host "🛠️ Installing with development dependencies..." -ForegroundColor Green
    pip install -e ".[dev,test]"
}

function Invoke-Lint {
    Write-Host "🔍 Running linting checks..." -ForegroundColor Green
    ruff check src/ tests/ scripts/
}

function Invoke-Format {
    Write-Host "✨ Formatting code..." -ForegroundColor Green
    black src/ tests/ scripts/
    isort src/ tests/ scripts/
}

function Invoke-TypeCheck {
    Write-Host "🔤 Running type checks..." -ForegroundColor Green
    mypy src/
}

function Invoke-SetupHooks {
    Write-Host "🪝 Installing pre-commit hooks..." -ForegroundColor Green
    pre-commit install
    Write-Host "✅ Pre-commit hooks installed" -ForegroundColor Green
}

function Invoke-ValidateAPlus {
    Write-Host "🏆 Validating A+ Grade Requirements..." -ForegroundColor Green
    
    Write-Host "1. Coverage standard (85% minimum)..." -ForegroundColor Yellow
    $coverage = python -m pytest --cov=src --cov-fail-under=85 -q
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Coverage check failed" -ForegroundColor Red
        return
    }
    
    Write-Host "2. All tests passing..." -ForegroundColor Yellow
    python -m pytest -q
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Tests failing" -ForegroundColor Red
        return
    }
    
    Write-Host "3. Code quality checks..." -ForegroundColor Yellow
    ruff check src/ tests/ --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Linting issues found" -ForegroundColor Red
        return
    }
    
    Write-Host "4. Type safety..." -ForegroundColor Yellow
    mypy src/ --no-error-summary
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Type check issues found" -ForegroundColor Red
        return
    }
    
    Write-Host ""
    Write-Host "🎉 A+ Grade requirements validated!" -ForegroundColor Green
}

function Invoke-Clean {
    Write-Host "🧹 Cleaning build artifacts..." -ForegroundColor Green
    
    $cleanPaths = @(
        "build", "dist", "*.egg-info", "htmlcov", 
        ".coverage", ".coverage.*", ".pytest_cache", ".mypy_cache"
    )
    
    foreach ($path in $cleanPaths) {
        if (Test-Path $path) {
            Remove-Item -Path $path -Recurse -Force
        }
    }
    
    # Clean __pycache__ directories
    Get-ChildItem -Path . -Name "__pycache__" -Recurse | Remove-Item -Recurse -Force
    Get-ChildItem -Path . -Name "*.pyc" -Recurse | Remove-Item -Force
    
    Write-Host "✅ Cleanup complete" -ForegroundColor Green
}

# Main command dispatcher
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "coverage" { Invoke-Coverage }
    "coverage-report" { Invoke-CoverageReport }
    "coverage-track" { Invoke-CoverageTrack }
    "coverage-html" { Invoke-CoverageHtml }
    "test" { Invoke-Test }
    "test-fast" { Invoke-TestFast }
    "test-moderate" { Invoke-ModerateTests }
    "moderate-test" { Invoke-ModerateTests }
    "install" { Invoke-Install }
    "dev-install" { Invoke-DevInstall }
    "lint" { Invoke-Lint }
    "format" { Invoke-Format }
    "type-check" { Invoke-TypeCheck }
    "setup-hooks" { Invoke-SetupHooks }
    "validate-aplus" { Invoke-ValidateAPlus }
    "clean" { Invoke-Clean }
    default {
        Write-Host "❌ Unknown command: $Command" -ForegroundColor Red
        Write-Host "Use '.\dev.ps1 help' to see available commands" -ForegroundColor Yellow
    }
}