#!/usr/bin/env python3
"""
Coverage tracking and analysis tool for maintaining A+ testing standards.

This script provides utilities for tracking coverage over time, identifying
coverage gaps, and ensuring new code meets coverage requirements.
"""

import json
import datetime
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


def get_current_coverage() -> Dict:
    """Get current coverage statistics."""
    try:
        # Run coverage report and capture output
        result = subprocess.run(
            ["python", "-m", "coverage", "report", "--format=json"],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error getting coverage: {e}")
        return {}


def analyze_coverage_gaps(coverage_data: Dict) -> List[Dict]:
    """Analyze coverage gaps and identify priority areas."""
    files = coverage_data.get("files", {})
    gaps = []
    
    for file_path, file_data in files.items():
        if not file_path.startswith("src/questionary_extended"):
            continue
            
        coverage_percent = file_data["summary"]["percent_covered"]
        missing_lines = file_data["summary"]["missing_lines"]
        
        if coverage_percent < 85:  # A+ standard
            gaps.append({
                "file": file_path,
                "coverage": coverage_percent,
                "missing_lines": missing_lines,
                "priority": "high" if coverage_percent < 50 else "medium"
            })
    
    # Sort by priority and coverage percentage
    gaps.sort(key=lambda x: (x["priority"] == "medium", x["coverage"]))
    return gaps


def track_coverage_history():
    """Track coverage over time."""
    coverage_data = get_current_coverage()
    if not coverage_data:
        return
    
    history_file = Path(".coverage_history.json")
    
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "total_coverage": coverage_data["totals"]["percent_covered"],
        "files_count": len([f for f in coverage_data["files"] 
                           if f.startswith("src/questionary_extended")]),
        "commit_hash": get_git_hash(),
        "branch": get_git_branch()
    }
    
    # Load existing history
    history = []
    if history_file.exists():
        with open(history_file) as f:
            history = [json.loads(line) for line in f if line.strip()]
    
    # Add new entry
    history.append(entry)
    
    # Keep only last 50 entries
    history = history[-50:]
    
    # Save updated history
    with open(history_file, 'w') as f:
        for entry in history:
            f.write(json.dumps(entry) + '\n')
    
    print(f"✅ Coverage tracked: {entry['total_coverage']:.1f}%")


def get_git_hash() -> Optional[str]:
    """Get current git commit hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def get_git_branch() -> Optional[str]:
    """Get current git branch."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def check_new_code_coverage(files: List[str]) -> bool:
    """Check coverage for specific files (new/modified code)."""
    if not files:
        return True
    
    # Filter for Python files in src
    src_files = [f for f in files if f.startswith("src/") and f.endswith(".py")]
    if not src_files:
        return True
    
    print(f"Checking coverage for {len(src_files)} modified files...")
    
    coverage_data = get_current_coverage()
    if not coverage_data:
        return False
    
    files_data = coverage_data.get("files", {})
    failed_files = []
    
    for file_path in src_files:
        if file_path in files_data:
            coverage = files_data[file_path]["summary"]["percent_covered"]
            if coverage < 95:  # New code standard
                failed_files.append((file_path, coverage))
    
    if failed_files:
        print("❌ New code coverage requirements not met:")
        for file_path, coverage in failed_files:
            print(f"  {file_path}: {coverage:.1f}% (required: 95%+)")
        return False
    else:
        print("✅ All modified files meet coverage requirements")
        return True


def generate_coverage_report():
    """Generate a comprehensive coverage report."""
    coverage_data = get_current_coverage()
    if not coverage_data:
        return
    
    total_coverage = coverage_data["totals"]["percent_covered"]
    
    print("🏆 TUI-Engine Coverage Report")
    print("=" * 50)
    print(f"Overall Coverage: {total_coverage:.2f}%")
    
    # A+ Grade Status
    grade = "A+" if total_coverage >= 85 else "A" if total_coverage >= 75 else "B+"
    status_emoji = "🏆" if grade == "A+" else "🥇" if grade == "A" else "🥈"
    print(f"Grade Status: {status_emoji} {grade} Grade")
    
    # Coverage gaps analysis
    gaps = analyze_coverage_gaps(coverage_data)
    if gaps:
        print(f"\n📊 Coverage Improvement Opportunities ({len(gaps)} files):")
        for gap in gaps[:5]:  # Top 5
            print(f"  {gap['priority'].upper()}: {gap['file']} - {gap['coverage']:.1f}%")
        
        if len(gaps) > 5:
            print(f"  ... and {len(gaps) - 5} more files")
    else:
        print("\n🎯 All files meet A+ coverage standards!")
    
    # Recommendations
    print(f"\n📈 Recommendations:")
    if total_coverage < 85:
        print(f"  • Target {85 - total_coverage:.1f}% improvement for A+ grade")
        print(f"  • Focus on high-priority gaps first")
    else:
        print(f"  • Maintain A+ standards for new code (95%+ coverage)")
        print(f"  • Consider property-based testing for edge cases")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Coverage tracking and analysis")
    parser.add_argument("--track", action="store_true", help="Track coverage history")
    parser.add_argument("--report", action="store_true", help="Generate coverage report")
    parser.add_argument("--check-new", nargs="*", help="Check coverage for new files")
    parser.add_argument("--analyze", action="store_true", help="Analyze coverage gaps")
    
    args = parser.parse_args()
    
    if args.track:
        track_coverage_history()
    elif args.report:
        generate_coverage_report()
    elif args.check_new is not None:
        success = check_new_code_coverage(args.check_new)
        sys.exit(0 if success else 1)
    elif args.analyze:
        coverage_data = get_current_coverage()
        gaps = analyze_coverage_gaps(coverage_data)
        print(json.dumps(gaps, indent=2))
    else:
        generate_coverage_report()


if __name__ == "__main__":
    main()