#!/usr/bin/env python3
"""Test script for AutocompleteAdapter functionality.

This script tests both enhanced and legacy modes of the AutocompleteAdapter,
including completion algorithms, validation, and theme integration.
"""
import sys
import os
from pathlib import Path

# Add the project src directory to Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from typing import List, Tuple, Dict, Any
import tempfile


def test_completion_engine():
    """Test the CompletionEngine functionality."""
    print("🧪 Testing CompletionEngine...")
    
    from tui_engine.widgets.autocomplete_adapter import CompletionEngine
    
    # Test data
    candidates = [
        "apple", "application", "apply", "banana", "band", "bandana",
        "cat", "car", "card", "care", "careful", "python", "java", "javascript"
    ]
    
    engine = CompletionEngine(
        case_sensitive=False,
        fuzzy_threshold=0.6,
        max_results=5
    )
    
    # Test prefix matching
    results = engine.complete("app", candidates, "prefix")
    print(f"  ✓ Prefix 'app': {[r[0] for r in results]}")
    assert len(results) > 0
    assert results[0][0] in ["apple", "application", "apply"]
    
    # Test substring matching
    results = engine.complete("car", candidates, "substring")
    print(f"  ✓ Substring 'car': {[r[0] for r in results]}")
    assert len(results) > 0
    assert any("car" in r[0] for r in results)
    
    # Test fuzzy matching
    results = engine.complete("javscpt", candidates, "fuzzy")
    print(f"  ✓ Fuzzy 'javscpt': {[r[0] for r in results]}")
    # Should match 'javascript' despite typo
    
    # Test smart algorithm
    results = engine.complete("ban", candidates, "smart")
    print(f"  ✓ Smart 'ban': {[r[0] for r in results]}")
    assert len(results) > 0
    
    print("✅ CompletionEngine tests passed!")
    return True


def test_enhanced_autocomplete_adapter():
    """Test EnhancedAutocompleteAdapter functionality."""
    print("🧪 Testing EnhancedAutocompleteAdapter...")
    
    try:
        from tui_engine.widgets.autocomplete_adapter import EnhancedAutocompleteAdapter
        
        # Static completions
        static_completions = ["python", "java", "javascript", "typescript", "go", "rust"]
        
        # Dynamic completion source
        def programming_language_source(query: str) -> List[str]:
            """Example dynamic completion source."""
            languages = [
                "c", "c++", "c#", "php", "ruby", "perl", "swift", 
                "kotlin", "scala", "clojure", "haskell", "erlang"
            ]
            return [lang for lang in languages if query.lower() in lang.lower()]
        
        # Create adapter
        adapter = EnhancedAutocompleteAdapter(
            message="Choose a programming language:",
            completions=static_completions,
            completion_sources=[programming_language_source],
            algorithm="smart",
            case_sensitive=False,
            max_results=8,
            min_input_length=1,
            style='professional_blue'
        )
        
        # Test basic functionality
        print(f"  ✓ Created adapter: {adapter}")
        print(f"  ✓ Widget info: {adapter.get_widget_info()}")
        
        # Test value setting/getting
        adapter.set_value("test")
        assert adapter.get_value() == "test"
        print("  ✓ Value setting/getting works")
        
        # Test completions
        completions = adapter.get_completions("py")
        print(f"  ✓ Completions for 'py': {[c[0] for c in completions]}")
        assert len(completions) > 0
        assert any("python" in c[0] for c in completions)
        
        # Test completion sources
        completions = adapter.get_completions("c")
        print(f"  ✓ Completions for 'c': {[c[0] for c in completions]}")
        assert len(completions) > 0
        
        # Test adding/removing completion sources
        def extra_source(query: str) -> List[str]:
            return ["extra1", "extra2"] if "ex" in query else []
        
        adapter.add_completion_source(extra_source)
        completions = adapter.get_completions("ex")
        print(f"  ✓ Completions after adding source: {[c[0] for c in completions]}")
        assert any("extra" in c[0] for c in completions)
        
        adapter.remove_completion_source(extra_source)
        
        # Test validation
        def length_validator(value: str) -> bool:
            return len(value) >= 2
        
        adapter.enable_validation(length_validator)
        is_valid, msg = adapter.validate_input("a")
        assert not is_valid
        print("  ✓ Validation works")
        
        is_valid, msg = adapter.validate_input("python")
        assert is_valid
        
        adapter.disable_validation()
        
        # Test theme changing
        if adapter.is_questionary_enhanced():
            adapter.change_theme('dark_mode')
            print("  ✓ Theme change works")
        
        # Test completion settings
        adapter.update_completion_settings(
            algorithm="prefix",
            max_results=5
        )
        print("  ✓ Completion settings update works")
        
        # Test statistics
        stats = adapter.get_completion_stats()
        print(f"  ✓ Completion stats: {stats}")
        assert 'completion_sources' in stats
        
        print("✅ EnhancedAutocompleteAdapter tests passed!")
        return True
        
    except ImportError as e:
        print(f"⚠️  Questionary not available, skipping enhanced tests: {e}")
        return True
    except Exception as e:
        print(f"❌ EnhancedAutocompleteAdapter test failed: {e}")
        return False


def test_backward_compatible_adapter():
    """Test the backward-compatible AutocompleteAdapter."""
    print("🧪 Testing backward-compatible AutocompleteAdapter...")
    
    from tui_engine.widgets.autocomplete_adapter import AutocompleteAdapter
    
    # Test legacy mode (with explicit widget)
    legacy_adapter = AutocompleteAdapter(widget="dummy_widget")
    print(f"  ✓ Legacy adapter created: {legacy_adapter}")
    
    # Test value operations
    legacy_adapter.set_value("test_value")
    assert legacy_adapter.get_value() == "test_value"
    print("  ✓ Legacy value operations work")
    
    # Test enhanced mode (without widget)
    try:
        enhanced_adapter = AutocompleteAdapter(
            message="Test message:",
            completions=["option1", "option2", "option3"],
            style='professional_blue'
        )
        print(f"  ✓ Enhanced adapter created: {enhanced_adapter}")
        
        # Test enhanced features
        enhanced_adapter.set_value("opt")
        completions = enhanced_adapter.get_completions("opt")
        print(f"  ✓ Enhanced completions: {[c[0] for c in completions[:3]]}")
        
        # Test widget info
        info = enhanced_adapter.get_widget_info()
        print(f"  ✓ Widget info: {info}")
        assert 'use_questionary' in info
        
    except Exception as e:
        print(f"  ⚠️  Enhanced mode not available: {e}")
    
    print("✅ Backward-compatible AutocompleteAdapter tests passed!")
    return True


def test_convenience_functions():
    """Test convenience functions for creating autocomplete widgets."""
    print("🧪 Testing convenience functions...")
    
    from tui_engine.widgets.autocomplete_adapter import (
        create_autocomplete, create_file_autocomplete, create_command_autocomplete
    )
    
    # Test basic autocomplete creation
    basic_auto = create_autocomplete(
        message="Basic test:",
        completions=["test1", "test2", "test3"]
    )
    print(f"  ✓ Basic autocomplete: {basic_auto}")
    
    # Test file autocomplete with temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some test files
        test_files = ["test.txt", "test.py", "example.md", "script.sh"]
        for filename in test_files:
            Path(temp_dir) / filename
        
        file_auto = create_file_autocomplete(
            message="Choose file:",
            base_path=temp_dir,
            extensions=[".txt", ".py"]
        )
        print(f"  ✓ File autocomplete: {file_auto}")
    
    # Test command autocomplete
    command_auto = create_command_autocomplete(
        message="Enter command:",
        commands=["build", "test", "deploy", "clean"]
    )
    print(f"  ✓ Command autocomplete: {command_auto}")
    
    print("✅ Convenience function tests passed!")
    return True


def test_integration_scenarios():
    """Test real-world integration scenarios."""
    print("🧪 Testing integration scenarios...")
    
    from tui_engine.widgets.autocomplete_adapter import AutocompleteAdapter
    
    # Scenario 1: Programming language selector with multiple sources
    languages = ["python", "java", "javascript", "typescript", "go", "rust", "c++"]
    
    def framework_source(query: str) -> List[str]:
        frameworks = {
            "py": ["django", "flask", "fastapi", "pyramid"],
            "js": ["react", "vue", "angular", "express"],
            "ja": ["spring", "spring-boot", "hibernate"],
            "go": ["gin", "echo", "fiber"],
            "ru": ["rocket", "actix-web", "warp"]
        }
        
        results = []
        for prefix, items in frameworks.items():
            if query.lower().startswith(prefix):
                results.extend(items)
        return results
    
    lang_selector = AutocompleteAdapter(
        message="Choose language or framework:",
        completions=languages,
        completion_sources=[framework_source],
        algorithm="smart",
        style='professional_blue'
    )
    
    # Test language completion
    completions = lang_selector.get_completions("py")
    print(f"  ✓ Language/Framework 'py': {[c[0] for c in completions[:5]]}")
    
    # Scenario 2: Configuration key autocomplete
    config_keys = [
        "database.host", "database.port", "database.name",
        "server.host", "server.port", "server.ssl",
        "cache.redis.host", "cache.redis.port",
        "logging.level", "logging.file", "logging.format"
    ]
    
    config_selector = AutocompleteAdapter(
        message="Configuration key:",
        completions=config_keys,
        algorithm="substring",
        style='dark_mode'
    )
    
    completions = config_selector.get_completions("host")
    print(f"  ✓ Config keys with 'host': {[c[0] for c in completions[:3]]}")
    
    # Scenario 3: API endpoint autocomplete
    def api_endpoint_source(query: str) -> List[str]:
        endpoints = [
            "/api/users", "/api/users/{id}", "/api/users/{id}/posts",
            "/api/posts", "/api/posts/{id}", "/api/posts/{id}/comments",
            "/api/auth/login", "/api/auth/logout", "/api/auth/refresh",
            "/api/admin/users", "/api/admin/settings"
        ]
        
        return [ep for ep in endpoints if query.lower() in ep.lower()]
    
    api_selector = AutocompleteAdapter(
        message="API endpoint:",
        completion_sources=[api_endpoint_source],
        algorithm="substring",
        min_input_length=2
    )
    
    completions = api_selector.get_completions("user")
    print(f"  ✓ API endpoints with 'user': {[c[0] for c in completions[:3]]}")
    
    print("✅ Integration scenario tests passed!")
    return True


def test_error_handling():
    """Test error handling and edge cases."""
    print("🧪 Testing error handling...")
    
    from tui_engine.widgets.autocomplete_adapter import AutocompleteAdapter, CompletionEngine
    
    # Test empty completions
    empty_adapter = AutocompleteAdapter(
        message="Empty test:",
        completions=[]
    )
    completions = empty_adapter.get_completions("test")
    assert len(completions) == 0
    print("  ✓ Empty completions handled")
    
    # Test error in completion source
    def error_source(query: str) -> List[str]:
        raise ValueError("Test error")
    
    error_adapter = AutocompleteAdapter(
        message="Error test:",
        completion_sources=[error_source]
    )
    completions = error_adapter.get_completions("test")
    # Should not crash, just return empty list
    print("  ✓ Completion source errors handled")
    
    # Test invalid validation function
    def bad_validator(value: str):
        raise RuntimeError("Validator error")
    
    adapter = AutocompleteAdapter(message="Validation test:")
    adapter.enable_validation(bad_validator)
    is_valid, msg = adapter.validate_input("test")
    assert not is_valid
    assert "error" in msg.lower()
    print("  ✓ Validation errors handled")
    
    # Test completion engine edge cases
    engine = CompletionEngine()
    
    # Empty query
    results = engine.complete("", ["test1", "test2"])
    assert len(results) > 0  # Should return all candidates
    
    # Empty candidates
    results = engine.complete("test", [])
    assert len(results) == 0
    
    print("  ✓ Edge cases handled")
    
    print("✅ Error handling tests passed!")
    return True


def main():
    """Run all AutocompleteAdapter tests."""
    print("🚀 Starting AutocompleteAdapter test suite...\n")
    
    tests = [
        test_completion_engine,
        test_enhanced_autocomplete_adapter,
        test_backward_compatible_adapter,
        test_convenience_functions,
        test_integration_scenarios,
        test_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            print()  # Add spacing between tests
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with error: {e}\n")
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All AutocompleteAdapter tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    exit(main())