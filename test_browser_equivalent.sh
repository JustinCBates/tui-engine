#!/bin/bash

# TUI-Engine Testing Script
# This script runs tests exactly like VS Code Test Browser should
# Usage: ./test_browser_equivalent.sh [test_pattern] [options]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/home/vpsuser/projects/tui-engine"
PYTHON_CMD="python3"
PYTEST_CMD="pytest"

# Ensure we're in the project directory
cd "$PROJECT_ROOT"

# Add local bin to PATH
export PATH="/home/vpsuser/.local/bin:$PATH"

echo -e "${BLUE}🔧 TUI-Engine Test Browser Equivalent${NC}"
echo "======================================="
echo "Project Root: $PROJECT_ROOT"
echo "Python: $(which $PYTHON_CMD)"
echo "Pytest: $(which $PYTEST_CMD)"
echo ""

# Function to run tests with specific configuration
run_tests() {
    local test_pattern="${1:-tests}"
    local extra_args="$2"
    
    echo -e "${YELLOW}📊 Running tests: $test_pattern${NC}"
    echo "Extra args: $extra_args"
    echo ""
    
    # This matches exactly what VS Code Test Browser would run
    $PYTHON_CMD -m $PYTEST_CMD \
        "$test_pattern" \
        --cov=src \
        --cov-report=term-missing \
        --cov-report=html:htmlcov \
        --cov-report=json:coverage.json \
        --cov-fail-under=85 \
        --tb=short \
        -v \
        $extra_args
}

# Function to run quick tests (no coverage)
run_quick_tests() {
    local test_pattern="${1:-tests}"
    
    echo -e "${YELLOW}⚡ Running quick tests: $test_pattern${NC}"
    echo ""
    
    $PYTHON_CMD -m $PYTEST_CMD \
        "$test_pattern" \
        -v \
        --tb=short
}

# Function to discover tests
discover_tests() {
    echo -e "${BLUE}🔍 Discovering tests...${NC}"
    echo ""
    
    $PYTHON_CMD -m $PYTEST_CMD \
        tests \
        --collect-only \
        -q
}

# Function to run specific test class or method
run_specific_test() {
    local test_spec="$1"
    
    echo -e "${YELLOW}🎯 Running specific test: $test_spec${NC}"
    echo ""
    
    $PYTHON_CMD -m $PYTEST_CMD \
        "$test_spec" \
        -v \
        --tb=short
}

# Function to show test results summary
show_test_summary() {
    echo ""
    echo -e "${GREEN}✅ Test Summary${NC}"
    echo "=================="
    
    if [ -f "coverage.json" ]; then
        echo "📊 Coverage report generated: coverage.json"
        echo "🌐 HTML coverage report: htmlcov/index.html"
        
        # Extract coverage percentage if available
        if command -v jq &> /dev/null; then
            coverage_percent=$(jq -r '.totals.percent_covered' coverage.json 2>/dev/null || echo "N/A")
            echo "📈 Coverage: ${coverage_percent}%"
        fi
    fi
    
    if [ -d "htmlcov" ]; then
        echo ""
        echo -e "${BLUE}To view HTML coverage report:${NC}"
        echo "  Open: file://$PROJECT_ROOT/htmlcov/index.html"
    fi
}

# Main script logic
case "${1:-all}" in
    "discover")
        discover_tests
        ;;
    "quick")
        run_quick_tests "${2:-tests}"
        ;;
    "specific")
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Please provide test specification${NC}"
            echo "Usage: $0 specific tests/test_file.py::TestClass::test_method"
            exit 1
        fi
        run_specific_test "$2"
        ;;
    "file")
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Please provide test file${NC}"
            echo "Usage: $0 file tests/test_validators.py"
            exit 1
        fi
        run_tests "$2"
        show_test_summary
        ;;
    "all")
        run_tests "tests"
        show_test_summary
        ;;
    *)
        # Treat as test pattern
        run_tests "$1" "$2"
        show_test_summary
        ;;
esac

echo ""
echo -e "${GREEN}🎉 Test execution completed!${NC}"