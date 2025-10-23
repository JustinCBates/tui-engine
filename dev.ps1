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