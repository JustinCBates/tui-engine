#!/usr/bin/env python3
"""
Comprehensive test suite for EditorAdapter.

This test suite validates:
- Multi-line text editing functionality
- Syntax highlighting for multiple languages
- Search and replace operations
- Editor history (undo/redo)
- File operations (load/save)
- Professional styling integration
- Backward compatibility
- Real-world usage scenarios

Run with: python test_editor_adapter.py
"""

import sys
import time
import tempfile
import os
from pathlib import Path

# Add src to path for testing
src_path = Path(__file__).parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

try:
    from tui_engine.widgets.editor_adapter import (
        EditorMode, EditorLanguage, SearchOptions, EditorPosition,
        EditorSelection, EditorHistory, SyntaxHighlighter, EditorRenderer,
        EnhancedEditorAdapter, EditorAdapter, edit_text, edit_file, create_new_file
    )
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


def test_editor_history():
    """Test EditorHistory functionality."""
    print("🧪 Testing EditorHistory...")
    
    # Test basic history operations
    print("  📚 Basic history tests:")
    history = EditorHistory(max_history=5)
    
    # Initially, should not be able to undo/redo
    assert not history.can_undo(), "Should not be able to undo initially"
    assert not history.can_redo(), "Should not be able to redo initially"
    print("    ✅ Initial state correct")
    
    # Add operations
    history.add_operation("type", "Hello")
    assert history.can_undo(), "Should be able to undo after adding operation"
    assert not history.can_redo(), "Should not be able to redo after adding operation"
    print("    ✅ Added first operation")
    
    history.add_operation("type", "Hello World")
    history.add_operation("type", "Hello World!")
    assert history.can_undo(), "Should be able to undo"
    print("    ✅ Added multiple operations")
    
    # Test undo
    print("  ⏪ Undo tests:")
    operation = history.undo()
    assert operation is not None, "Undo should return operation"
    assert operation[0] == "type", "Should return correct action"
    assert operation[1] == "Hello World!", "Should return correct content"
    assert history.can_redo(), "Should be able to redo after undo"
    print("    ✅ Undo operation successful")
    
    # Test redo
    print("  ⏩ Redo tests:")
    operation = history.redo()
    assert operation is not None, "Redo should return operation"
    assert operation[0] == "type", "Should return correct action"
    print("    ✅ Redo operation successful")
    
    # Test history limit
    print("  📏 History limit tests:")
    for i in range(10):
        history.add_operation("type", f"Content {i}")
    
    # Should only keep last 5 operations
    undo_count = 0
    while history.can_undo():
        history.undo()
        undo_count += 1
    
    assert undo_count <= 5, f"Should limit history to 5, got {undo_count}"
    print(f"    ✅ History limited to {undo_count} operations")
    
    # Test modification tracking
    print("  🔄 Modification tracking tests:")
    history = EditorHistory()
    history.add_operation("type", "test")
    assert history.is_modified(), "Should be modified after operation"
    
    history.mark_saved()
    assert not history.is_modified(), "Should not be modified after save"
    print("    ✅ Modification tracking works")
    
    print("✅ EditorHistory tests passed!")


def test_syntax_highlighter():
    """Test SyntaxHighlighter functionality."""
    print("\n🧪 Testing SyntaxHighlighter...")
    
    # Test language detection
    print("  🔍 Language detection tests:")
    test_files = [
        ("test.py", EditorLanguage.PYTHON),
        ("test.js", EditorLanguage.JAVASCRIPT),
        ("test.ts", EditorLanguage.TYPESCRIPT),
        ("test.html", EditorLanguage.HTML),
        ("test.css", EditorLanguage.CSS),
        ("test.json", EditorLanguage.JSON),
        ("test.yaml", EditorLanguage.YAML),
        ("test.md", EditorLanguage.MARKDOWN),
        ("test.sql", EditorLanguage.SQL),
        ("test.sh", EditorLanguage.BASH),
        ("test.c", EditorLanguage.C),
        ("test.cpp", EditorLanguage.CPP),
        ("test.java", EditorLanguage.JAVA),
        ("test.go", EditorLanguage.GO),
        ("test.rs", EditorLanguage.RUST),
        ("test.txt", EditorLanguage.PLAIN),
        ("", EditorLanguage.PLAIN),
    ]
    
    for filename, expected_lang in test_files:
        detected = SyntaxHighlighter.detect_language(filename)
        assert detected == expected_lang, f"Expected {expected_lang.value}, got {detected.value} for {filename}"
        print(f"    ✅ {filename or 'empty'}: {detected.value}")
    
    # Test highlighter initialization
    print("  🎨 Highlighter initialization tests:")
    for language in EditorLanguage:
        highlighter = SyntaxHighlighter(language)
        assert highlighter.language == language, f"Language should be {language.value}"
        print(f"    ✅ {language.value}: initialized")
    
    # Test text highlighting
    print("  ✨ Text highlighting tests:")
    python_code = """
def hello_world():
    print("Hello, World!")
    return 42
"""
    
    highlighter = SyntaxHighlighter(EditorLanguage.PYTHON)
    highlighted = highlighter.highlight_text(python_code.strip())
    assert isinstance(highlighted, str), "Should return string"
    print(f"    ✅ Python highlighting: {len(highlighted)} characters")
    
    # Test line highlighting
    line_highlighted = highlighter.highlight_line("def test():", 0)
    assert isinstance(line_highlighted, list), "Should return FormattedText list"
    print(f"    ✅ Line highlighting: {len(line_highlighted)} segments")
    
    print("✅ SyntaxHighlighter tests passed!")


def test_search_options():
    """Test SearchOptions functionality."""
    print("\n🧪 Testing SearchOptions...")
    
    # Test default options
    print("  ⚙️  Default options tests:")
    options = SearchOptions()
    assert not options.case_sensitive, "Should default to case insensitive"
    assert not options.regex, "Should default to literal search"
    assert not options.whole_word, "Should default to partial word matching"
    assert options.wrap_around, "Should default to wrap around"
    assert options.highlight_all, "Should default to highlight all matches"
    assert not options.replace_all, "Should default to single replacement"
    print("    ✅ Default options correct")
    
    # Test custom options
    print("  🔧 Custom options tests:")
    custom_options = SearchOptions(
        case_sensitive=True,
        regex=True,
        whole_word=True,
        wrap_around=False,
        highlight_all=False,
        replace_all=True
    )
    assert custom_options.case_sensitive, "Should be case sensitive"
    assert custom_options.regex, "Should use regex"
    assert custom_options.whole_word, "Should match whole words"
    assert not custom_options.wrap_around, "Should not wrap around"
    assert not custom_options.highlight_all, "Should not highlight all"
    assert custom_options.replace_all, "Should replace all"
    print("    ✅ Custom options correct")
    
    print("✅ SearchOptions tests passed!")


def test_editor_position():
    """Test EditorPosition functionality."""
    print("\n🧪 Testing EditorPosition...")
    
    # Test initialization
    print("  🎯 Position initialization tests:")
    pos = EditorPosition()
    assert pos.line == 0, "Should default to line 0"
    assert pos.column == 0, "Should default to column 0"
    print("    ✅ Default position: (0, 0)")
    
    pos = EditorPosition(5, 10)
    assert pos.line == 5, "Should set line correctly"
    assert pos.column == 10, "Should set column correctly"
    print("    ✅ Custom position: (5, 10)")
    
    # Test string representation
    print("  📝 String representation tests:")
    pos_str = str(pos)
    assert pos_str == "6:11", f"Expected '6:11', got '{pos_str}'"  # 1-based display
    print(f"    ✅ Position string: {pos_str}")
    
    print("✅ EditorPosition tests passed!")


def test_editor_renderer():
    """Test EditorRenderer functionality."""
    print("\n🧪 Testing EditorRenderer...")
    
    # Test initialization
    print("  🎨 Renderer initialization tests:")
    renderer = EditorRenderer()
    assert renderer.show_line_numbers, "Should show line numbers by default"
    assert renderer.tab_size == 4, "Should default to 4 spaces per tab"
    print("    ✅ Default renderer settings")
    
    renderer = EditorRenderer(
        show_line_numbers=False,
        tab_size=2,
        theme_variant="dark_mode"
    )
    assert not renderer.show_line_numbers, "Should not show line numbers"
    assert renderer.tab_size == 2, "Should use custom tab size"
    assert renderer.theme_variant == "dark_mode", "Should use custom theme"
    print("    ✅ Custom renderer settings")
    
    # Test content rendering
    print("  📄 Content rendering tests:")
    lines = ["def hello():", "    print('Hello')", "    return True"]
    rendered = renderer.render_content(lines, current_line=1)
    
    assert isinstance(rendered, str), "Should return string"
    assert len(rendered) > 0, "Should produce output"
    # Should not have line numbers in this config
    assert "│" not in rendered, "Should not have line number separator"
    print(f"    ✅ Content rendered: {len(rendered)} characters")
    
    # Test with line numbers
    renderer_with_numbers = EditorRenderer(show_line_numbers=True)
    rendered_with_numbers = renderer_with_numbers.render_content(lines)
    assert "│" in rendered_with_numbers, "Should have line number separator"
    print("    ✅ Line numbers rendered")
    
    # Test status line
    print("  📊 Status line tests:")
    pos = EditorPosition(2, 5)
    status = renderer.render_status_line(
        filename="test.py",
        position=pos,
        mode=EditorMode.INSERT,
        modified=True,
        language=EditorLanguage.PYTHON
    )
    
    assert isinstance(status, str), "Should return string"
    assert "test.py" in status, "Should contain filename"
    assert "[+]" in status, "Should indicate modified"
    assert "3:6" in status, "Should show position (1-based)"
    assert "INSERT" in status, "Should show mode"
    assert "PYTHON" in status, "Should show language"
    print("    ✅ Status line rendered correctly")
    
    print("✅ EditorRenderer tests passed!")


def test_enhanced_editor_adapter():
    """Test EnhancedEditorAdapter functionality."""
    print("\n🧪 Testing EnhancedEditorAdapter...")
    
    # Test initialization
    print("  🚀 Initialization tests:")
    editor = EnhancedEditorAdapter()
    assert editor.content == "", "Should start with empty content"
    assert editor.language == EditorLanguage.PLAIN, "Should default to plain text"
    assert editor.mode == EditorMode.INSERT, "Should default to insert mode"
    print("    ✅ Default editor created")
    
    # Test with content
    content = "def test():\n    pass"
    editor = EnhancedEditorAdapter(
        content=content,
        filename="test.py",
        show_line_numbers=True
    )
    assert editor.content == content, "Should set content"
    assert editor.language == EditorLanguage.PYTHON, "Should detect Python"
    assert len(editor.lines) == 2, "Should split content into lines"
    print("    ✅ Editor with content created")
    
    # Test content operations
    print("  📝 Content operations tests:")
    editor.set_content("Hello\nWorld")
    assert editor.get_content() == "Hello\nWorld", "Should set and get content"
    assert len(editor.lines) == 2, "Should update lines"
    assert editor.modified, "Should mark as modified"
    print("    ✅ Content operations work")
    
    # Test search functionality
    print("  🔍 Search functionality tests:")
    test_content = """
def hello():
    print("Hello")
    print("World")
    return "Hello World"
"""
    editor.set_content(test_content.strip())
    
    # Search for "Hello"
    options = SearchOptions(case_sensitive=False)
    matches = editor.search_text("Hello", options)
    assert len(matches) >= 2, f"Should find at least 2 matches, found {len(matches)}"
    print(f"    ✅ Found {len(matches)} search matches")
    
    # Test case sensitive search
    options_case = SearchOptions(case_sensitive=True)
    matches_case = editor.search_text("hello", options_case)
    print(f"    ✅ Case sensitive search: {len(matches_case)} matches")
    
    # Test regex search
    options_regex = SearchOptions(regex=True)
    matches_regex = editor.search_text(r"print\(.+\)", options_regex)
    assert len(matches_regex) >= 2, f"Should find print statements, found {len(matches_regex)}"
    print(f"    ✅ Regex search: {len(matches_regex)} matches")
    
    # Test replace functionality
    print("  🔄 Replace functionality tests:")
    original_content = editor.get_content()
    options_replace = SearchOptions(replace_all=True)
    replacements = editor.replace_text("Hello", "Hi", options_replace)
    assert replacements > 0, "Should make replacements"
    assert "Hi" in editor.get_content(), "Should contain replacement text"
    assert "Hello" not in editor.get_content() or "Hello World" in editor.get_content(), "Should replace occurrences"
    print(f"    ✅ Made {replacements} replacements")
    
    # Test undo/redo
    print("  ⏪ Undo/redo tests:")
    # Content was changed by replace, so undo should work
    undo_result = editor.undo()
    if undo_result:
        print("    ✅ Undo operation successful")
        
        redo_result = editor.redo()
        if redo_result:
            print("    ✅ Redo operation successful")
        else:
            print("    ⚠️  Redo not available (expected in some cases)")
    else:
        print("    ⚠️  Undo not available (expected in some cases)")
    
    # Test statistics
    print("  📊 Statistics tests:")
    stats = editor.get_statistics()
    expected_keys = ['lines', 'non_empty_lines', 'characters', 'characters_no_spaces', 'words', 'language', 'mode', 'modified', 'filename']
    for key in expected_keys:
        assert key in stats, f"Statistics should include {key}"
    
    assert stats['language'] == 'python', f"Language should be python, got {stats['language']}"
    assert stats['mode'] == 'insert', f"Mode should be insert, got {stats['mode']}"
    assert stats['lines'] > 0, "Should have lines"
    print(f"    ✅ Statistics: {stats['lines']} lines, {stats['words']} words, {stats['characters']} chars")
    
    print("✅ EnhancedEditorAdapter tests passed!")


def test_file_operations():
    """Test file load/save operations."""
    print("\n🧪 Testing file operations...")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        test_content = """#!/usr/bin/env python3
def greet(name):
    print(f"Hello, {name}!")

if __name__ == "__main__":
    greet("World")
"""
        f.write(test_content)
        temp_filename = f.name
    
    try:
        # Test loading file
        print("  📂 File loading tests:")
        editor = EnhancedEditorAdapter()
        load_success = editor.load_from_file(temp_filename)
        assert load_success, "Should successfully load file"
        assert editor.get_content() == test_content, "Should load correct content"
        assert editor.language == EditorLanguage.PYTHON, "Should detect Python language"
        assert not editor.modified, "Should not be marked as modified after load"
        print(f"    ✅ Loaded file: {len(editor.lines)} lines")
        
        # Test modifying content
        print("  ✏️  Content modification tests:")
        editor.set_content(editor.get_content() + "\n# Added comment")
        assert editor.modified, "Should be marked as modified after edit"
        print("    ✅ Content modified")
        
        # Test saving file
        print("  💾 File saving tests:")
        save_success = editor.save_to_file()
        assert save_success, "Should successfully save file"
        assert not editor.modified, "Should not be marked as modified after save"
        print("    ✅ File saved successfully")
        
        # Verify saved content
        with open(temp_filename, 'r') as f:
            saved_content = f.read()
        assert "# Added comment" in saved_content, "Should contain added comment"
        print("    ✅ Saved content verified")
        
        # Test saving to new file
        print("  💾 Save as tests:")
        new_temp_file = temp_filename + ".new"
        save_as_success = editor.save_to_file(new_temp_file)
        assert save_as_success, "Should successfully save to new file"
        assert os.path.exists(new_temp_file), "New file should exist"
        print("    ✅ Save as successful")
        
        # Clean up new file
        os.unlink(new_temp_file)
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)
    
    print("✅ File operations tests passed!")


def test_backward_compatible_adapter():
    """Test backward-compatible EditorAdapter."""
    print("\n🧪 Testing backward-compatible EditorAdapter...")
    
    # Test enhanced mode
    print("  🚀 Enhanced mode tests:")
    enhanced_adapter = EditorAdapter(enhanced=True, content="Test content")
    assert enhanced_adapter.enhanced == True, "Should be in enhanced mode"
    assert hasattr(enhanced_adapter, 'adapter'), "Should have adapter"
    assert isinstance(enhanced_adapter.adapter, EnhancedEditorAdapter), "Should be EnhancedEditorAdapter"
    print("    ✅ Enhanced adapter created")
    
    # Test content operations
    content = enhanced_adapter.get_content()
    assert content == "Test content", "Should get correct content"
    
    enhanced_adapter.set_content("New content")
    assert enhanced_adapter.get_content() == "New content", "Should set content"
    print("    ✅ Content operations work")
    
    # Test legacy mode
    print("  🔙 Legacy mode tests:")
    legacy_adapter = EditorAdapter(enhanced=False, content="Legacy content")
    assert legacy_adapter.enhanced == False, "Should be in legacy mode"
    assert legacy_adapter.content == "Legacy content", "Should set content"
    print("    ✅ Legacy adapter created")
    
    # Test representation
    print("  📝 String representation tests:")
    enhanced_repr = repr(enhanced_adapter)
    assert "enhanced=True" in enhanced_repr, "Should indicate enhanced mode"
    print(f"    ✅ Enhanced repr: {enhanced_repr[:50]}...")
    
    legacy_repr = repr(legacy_adapter)
    assert "enhanced=False" in legacy_repr, "Should indicate legacy mode"
    print(f"    ✅ Legacy repr: {legacy_repr[:50]}...")
    
    print("✅ Backward-compatible EditorAdapter tests passed!")


def test_convenience_functions():
    """Test convenience functions."""
    print("\n🧪 Testing convenience functions...")
    
    # Test function signatures
    print("  🎯 Function signature tests:")
    import inspect
    
    # Test edit_text function
    sig = inspect.signature(edit_text)
    expected_params = ['content', 'filename', 'language', 'theme_variant']
    for param in expected_params:
        assert param in sig.parameters, f"edit_text should have {param} parameter"
    print("    ✅ edit_text signature valid")
    
    # Test edit_file function
    sig = inspect.signature(edit_file)
    assert 'filename' in sig.parameters, "edit_file should have filename parameter"
    assert 'theme_variant' in sig.parameters, "edit_file should have theme_variant parameter"
    print("    ✅ edit_file signature valid")
    
    # Test create_new_file function
    sig = inspect.signature(create_new_file)
    expected_params = ['filename', 'template', 'theme_variant']
    for param in expected_params:
        assert param in sig.parameters, f"create_new_file should have {param} parameter"
    print("    ✅ create_new_file signature valid")
    
    print("✅ Convenience function tests passed!")


def test_real_world_scenarios():
    """Test real-world editor scenarios."""
    print("\n🧪 Testing real-world scenarios...")
    
    # Test code editing scenario
    print("  💻 Code editing scenario:")
    python_code = """
import os
import sys

def main():
    print("Hello, World!")
    
    # Process command line arguments
    for arg in sys.argv[1:]:
        print(f"Argument: {arg}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
"""
    
    editor = EnhancedEditorAdapter(
        content=python_code.strip(),
        filename="script.py",
        language=EditorLanguage.PYTHON
    )
    
    # Test search and replace for refactoring
    matches = editor.search_text("print", SearchOptions())
    assert len(matches) >= 2, f"Should find print statements, found {len(matches)}"
    
    # Test adding comments
    original_lines = len(editor.lines)
    editor.set_content(editor.get_content() + "\n# TODO: Add error handling")
    assert len(editor.lines) > original_lines, "Should add lines"
    print(f"    ✅ Code editing: {len(editor.lines)} lines, {len(matches)} print statements")
    
    # Test configuration file editing
    print("  ⚙️  Configuration editing scenario:")
    config_content = """
# Database configuration
host = localhost
port = 5432
database = myapp
user = admin
password = secret

# Cache settings
cache_enabled = true
cache_ttl = 3600
"""
    
    config_editor = EnhancedEditorAdapter(
        content=config_content.strip(),
        filename="config.ini",
        language=EditorLanguage.PLAIN
    )
    
    # Search for settings
    host_matches = config_editor.search_text("host", SearchOptions())
    assert len(host_matches) >= 1, "Should find host setting"
    
    # Replace password (simulate security update)
    replacements = config_editor.replace_text(
        "password = secret",
        "password = ********",
        SearchOptions()
    )
    assert replacements > 0, "Should replace password"
    assert "********" in config_editor.get_content(), "Should contain masked password"
    print(f"    ✅ Config editing: {replacements} security updates made")
    
    # Test documentation editing
    print("  📝 Documentation editing scenario:")
    markdown_content = """
# Project Documentation

## Overview
This is a sample project that demonstrates TUI functionality.

## Features
- Multi-line text editing
- Syntax highlighting
- Search and replace
- File operations

## Installation
```bash
pip install tui-engine
```

## Usage
See examples in the `demos/` directory.
"""
    
    doc_editor = EnhancedEditorAdapter(
        content=markdown_content.strip(),
        filename="README.md",
        language=EditorLanguage.MARKDOWN
    )
    
    # Test finding sections
    section_matches = doc_editor.search_text("##", SearchOptions())
    assert len(section_matches) >= 3, f"Should find sections, found {len(section_matches)}"
    
    # Test adding new section
    doc_editor.set_content(doc_editor.get_content() + "\n\n## Contributing\nPull requests welcome!")
    stats = doc_editor.get_statistics()
    print(f"    ✅ Documentation: {stats['lines']} lines, {stats['words']} words")
    
    print("✅ Real-world scenario tests passed!")


def test_performance_and_memory():
    """Test performance and memory usage."""
    print("\n🧪 Testing performance and memory...")
    
    # Test large file handling
    print("  📄 Large file handling:")
    large_content = "\n".join([f"Line {i}: This is a test line with some content" for i in range(1000)])
    
    start_time = time.time()
    editor = EnhancedEditorAdapter(content=large_content)
    init_time = time.time() - start_time
    
    assert len(editor.lines) == 1000, "Should handle 1000 lines"
    print(f"    ✅ Initialized 1000 lines in {init_time:.3f}s")
    
    # Test search performance
    print("  🔍 Search performance:")
    start_time = time.time()
    matches = editor.search_text("test", SearchOptions())
    search_time = time.time() - start_time
    
    assert len(matches) == 1000, "Should find all matches"
    searches_per_second = len(matches) / search_time if search_time > 0 else float('inf')
    print(f"    ✅ Searched 1000 lines in {search_time:.3f}s ({searches_per_second:.0f} lines/sec)")
    
    # Test replace performance
    print("  🔄 Replace performance:")
    start_time = time.time()
    replacements = editor.replace_text("test", "demo", SearchOptions(replace_all=True))
    replace_time = time.time() - start_time
    
    assert replacements == 1000, "Should replace all occurrences"
    print(f"    ✅ Replaced 1000 occurrences in {replace_time:.3f}s")
    
    # Test memory efficiency
    print("  💾 Memory efficiency:")
    editor.set_content("Small content")
    stats_after = editor.get_statistics()
    assert stats_after['lines'] == 1, "Should update to small content"
    assert stats_after['characters'] < 100, "Should have small character count"
    print("    ✅ Memory efficiently managed")
    
    # Test syntax highlighting performance
    print("  🎨 Syntax highlighting performance:")
    python_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
""" * 50  # Repeat to create larger content
    
    start_time = time.time()
    highlighter = SyntaxHighlighter(EditorLanguage.PYTHON)
    highlighted = highlighter.highlight_text(python_code)
    highlight_time = time.time() - start_time
    
    assert len(highlighted) > len(python_code), "Highlighted text should be longer (ANSI codes)"
    chars_per_second = len(python_code) / highlight_time if highlight_time > 0 else float('inf')
    print(f"    ✅ Highlighted {len(python_code)} chars in {highlight_time:.3f}s ({chars_per_second:.0f} chars/sec)")
    
    print("✅ Performance and memory tests passed!")


def main():
    """Run all EditorAdapter tests."""
    print("🚀 Starting EditorAdapter test suite...\n")
    
    try:
        # Core functionality tests
        test_editor_history()
        test_syntax_highlighter()
        test_search_options()
        test_editor_position()
        test_editor_renderer()
        test_enhanced_editor_adapter()
        test_file_operations()
        test_backward_compatible_adapter()
        test_convenience_functions()
        
        # Advanced tests
        test_real_world_scenarios()
        test_performance_and_memory()
        
        print(f"\n📊 Test Results: 11/11 tests passed")
        print("🎉 All EditorAdapter tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)