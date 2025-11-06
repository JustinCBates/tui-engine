#!/usr/bin/env python3
"""Demo script showcasing FilePathAdapter capabilities.

This script demonstrates the file browser integration, path validation,
extension filtering, and various file selection scenarios.
"""
import sys
import os
from pathlib import Path
import tempfile
import time

# Add the project src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from typing import List

# Import our file path components
from tui_engine.widgets.file_path_adapter import (
    FilePathAdapter,
    create_file_selector,
    create_directory_selector,
    create_config_file_selector,
    create_image_file_selector,
    create_source_file_selector,
    FileSystemNavigator
)


def demo_file_system_navigator():
    """Demonstrate the FileSystemNavigator capabilities."""
    print("🗂️  FileSystemNavigator Demo")
    print("=" * 50)
    
    # Use current project as demo base
    base_path = Path("./src/tui_engine")
    
    if not base_path.exists():
        print("  ⚠️  Demo requires ./src/tui_engine directory")
        return
    
    # Create navigator for Python files
    navigator = FileSystemNavigator(
        base_path=base_path,
        allowed_extensions={'.py'},
        show_hidden=False,
        files_only=False
    )
    
    print(f"📁 Navigating: {navigator.current_path}")
    print(f"📊 Path info: {navigator.get_current_path_info()}")
    
    # List current directory
    items = navigator.list_current_directory()
    print(f"\n📋 Directory contents ({len(items)} items):")
    
    for item in items[:10]:  # Show first 10 items
        icon = "📁" if item['is_dir'] else "📄"
        size_info = f"({item['size']} bytes)" if item['is_file'] and item['size'] > 0 else ""
        print(f"  {icon} {item['name']} {size_info}")
    
    if len(items) > 10:
        print(f"  ... and {len(items) - 10} more items")
    
    # Test path completions
    print(f"\n🔍 Path completions for '__':")
    completions = navigator.get_path_completions("__")
    for completion in completions[:5]:
        print(f"  • {completion}")
    
    # Test navigation to widgets subdirectory
    widgets_path = base_path / "widgets"
    if widgets_path.exists():
        print(f"\n🚀 Navigating to widgets directory...")
        success = navigator.navigate_to(widgets_path)
        if success:
            widget_items = navigator.list_current_directory()
            python_files = [item for item in widget_items if item['is_file'] and item['name'].endswith('.py')]
            print(f"  ✓ Found {len(python_files)} Python files in widgets:")
            for py_file in python_files[:5]:
                print(f"    🐍 {py_file['name']}")
    
    print("\n" + "=" * 50)


def demo_basic_file_selection():
    """Demo basic file selection functionality."""
    print("📂 Basic File Selection Demo")
    print("=" * 50)
    
    # Create a demo project structure
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create realistic project structure
        (temp_path / "src").mkdir()
        (temp_path / "tests").mkdir()
        (temp_path / "docs").mkdir()
        (temp_path / "config").mkdir()
        
        # Create files
        files_to_create = [
            ("README.md", "# Demo Project\nThis is a demo project."),
            ("requirements.txt", "requests\npytest\nclick"),
            ("setup.py", "from setuptools import setup, find_packages"),
            ("src/__init__.py", ""),
            ("src/main.py", "def main():\n    print('Hello, World!')"),
            ("src/utils.py", "def helper_function():\n    pass"),
            ("tests/test_main.py", "def test_main():\n    assert True"),
            ("tests/test_utils.py", "def test_helper():\n    assert True"),
            ("docs/api.md", "# API Documentation"),
            ("docs/tutorial.md", "# Tutorial"),
            ("config/settings.json", '{"debug": true, "port": 8000}'),
            ("config/logging.yaml", "version: 1\nroot:\n  level: INFO"),
        ]
        
        for file_path, content in files_to_create:
            full_path = temp_path / file_path
            full_path.write_text(content)
        
        print(f"📋 Created demo project in: {temp_path}")
        print(f"📊 Project structure:")
        
        # Show project structure
        for root, dirs, files in os.walk(temp_path):
            level = root.replace(str(temp_path), '').count(os.sep)
            indent = '  ' * level
            print(f"{indent}📁 {os.path.basename(root)}/")
            subindent = '  ' * (level + 1)
            for file in files:
                extension = Path(file).suffix
                icon = {"py": "🐍", ".md": "📖", ".json": "📋", ".yaml": "⚙️", ".txt": "📝"}.get(extension, "📄")
                print(f"{subindent}{icon} {file}")
        
        # Demo 1: General file selector
        print(f"\n🔍 Demo 1: General file browser")
        general_selector = FilePathAdapter(
            message="Select any file:",
            base_path=temp_path,
            style='professional_blue'
        )
        
        print(f"  Available files and directories:")
        items = general_selector.list_current_directory()
        for item in items:
            print(f"    {item['display_name']}")
        
        # Demo path completions
        print(f"\n  Path completions for 'src/':")
        completions = general_selector.get_path_completions("src/")
        for completion in completions:
            print(f"    • {completion}")
        
        # Demo 2: Python file selector
        print(f"\n🐍 Demo 2: Python file selector")
        python_selector = create_source_file_selector(
            message="Select Python file:",
            base_path=temp_path,
            language='python'
        )
        
        print(f"  Python file completions:")
        completions = python_selector.get_path_completions("")
        python_files = [comp for comp in completions if comp.endswith('.py')]
        for py_file in python_files:
            print(f"    🐍 {py_file}")
        
        # Demo validation
        python_selector.set_value("src/main.py")
        is_valid, msg = python_selector.validate_current_path()
        print(f"  Validation of 'src/main.py': {'✅ Valid' if is_valid else f'❌ {msg}'}")
        
        # Demo 3: Config file selector
        print(f"\n⚙️  Demo 3: Configuration file selector")
        config_selector = create_config_file_selector(
            message="Select config file:",
            base_path=temp_path
        )
        
        config_completions = config_selector.get_path_completions("config/")
        for completion in config_completions:
            print(f"    ⚙️ {completion}")
    
    print("\n" + "=" * 50)


def demo_advanced_file_operations():
    """Demo advanced file operations."""
    print("🔧 Advanced File Operations Demo")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create file browser with directory creation enabled
        file_browser = FilePathAdapter(
            message="Advanced file browser:",
            base_path=temp_path,
            create_dirs=True,
            style='dark_mode'
        )
        
        print(f"📁 Base directory: {temp_path}")
        
        # Test directory creation through navigator
        navigator = file_browser._enhanced_adapter.navigator if file_browser._enhanced_adapter else None
        if navigator:
            # Create some directories
            test_dirs = ["project1", "project2", "shared", "temp"]
            for dir_name in test_dirs:
                success = navigator.create_directory(dir_name)
                if success:
                    print(f"  ✅ Created directory: {dir_name}")
                else:
                    print(f"  ❌ Failed to create directory: {dir_name}")
            
            # Create some files
            test_files = [
                ("project1/main.py", "print('Project 1')"),
                ("project2/app.py", "print('Project 2')"),
                ("shared/utils.py", "def shared_function(): pass"),
                ("README.md", "# Projects Overview")
            ]
            
            for file_path, content in test_files:
                full_path = temp_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
                print(f"  📝 Created file: {file_path}")
            
            # Test navigation
            print(f"\n🧭 Navigation demo:")
            print(f"  Current: {navigator.get_current_path_info()['relative_path'] or '.'}")
            
            # Navigate to project1
            success = navigator.navigate_to(temp_path / "project1")
            if success:
                print(f"  ✅ Navigated to: project1/")
                items = navigator.list_current_directory()
                for item in items:
                    if not item['is_parent']:
                        print(f"    {item['display_name']}")
                
                # Navigate back up
                navigator.navigate_up()
                print(f"  ✅ Navigated back to: {navigator.get_current_path_info()['relative_path'] or '.'}")
            
            # Test file filtering
            print(f"\n🔍 File filtering demo:")
            
            # Python files only
            py_navigator = FileSystemNavigator(
                base_path=temp_path,
                allowed_extensions={'.py'},
                files_only=True
            )
            py_items = py_navigator.list_current_directory()
            py_files = [item for item in py_items if item['is_file']]
            print(f"  🐍 Python files found: {len(py_files)}")
            for py_file in py_files:
                print(f"    • {py_file['name']}")
            
            # Directories only
            dir_navigator = FileSystemNavigator(
                base_path=temp_path,
                dirs_only=True
            )
            dir_items = dir_navigator.list_current_directory()
            directories = [item for item in dir_items if item['is_dir'] and not item['is_parent']]
            print(f"  📁 Directories found: {len(directories)}")
            for directory in directories:
                print(f"    • {directory['name']}/")
    
    print("\n" + "=" * 50)


def demo_validation_and_security():
    """Demo validation and security features."""
    print("🔒 Validation & Security Demo")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test structure with restricted area
        (temp_path / "public").mkdir()
        (temp_path / "restricted").mkdir()
        (temp_path / "uploads").mkdir()
        
        # Create files
        (temp_path / "public" / "welcome.txt").write_text("Welcome to public area")
        (temp_path / "public" / "data.json").write_text('{"public": true}')
        (temp_path / "restricted" / "secrets.txt").write_text("Top secret information")
        (temp_path / "uploads" / "document.pdf").write_text("PDF content")
        
        print(f"🏗️  Created test structure:")
        print(f"  📁 public/ (allowed)")
        print(f"  📁 restricted/ (blocked by security)")
        print(f"  📁 uploads/ (specific file types only)")
        
        # Demo 1: Basic path validation
        print(f"\n🔍 Demo 1: Basic path validation")
        
        file_selector = FilePathAdapter(
            message="Select file:",
            base_path=temp_path / "public",  # Restrict to public only
            files_only=True
        )
        
        # Test valid file
        file_selector.set_value("welcome.txt")
        is_valid, msg = file_selector.validate_current_path()
        print(f"  'welcome.txt': {'✅ Valid' if is_valid else f'❌ {msg}'}")
        
        # Test non-existent file
        file_selector.set_value("missing.txt")
        is_valid, msg = file_selector.validate_current_path()
        print(f"  'missing.txt': {'✅ Valid' if is_valid else f'❌ {msg}'}")
        
        # Demo 2: Extension validation
        print(f"\n📄 Demo 2: Extension validation")
        
        json_selector = FilePathAdapter(
            message="Select JSON file:",
            base_path=temp_path / "public",
            allowed_extensions=['.json'],
            files_only=True
        )
        
        json_selector.set_value("data.json")
        is_valid, msg = json_selector.validate_current_path()
        print(f"  'data.json': {'✅ Valid' if is_valid else f'❌ {msg}'}")
        
        json_selector.set_value("welcome.txt")
        is_valid, msg = json_selector.validate_current_path()
        print(f"  'welcome.txt': {'✅ Valid' if is_valid else f'❌ {msg}'}")
        
        # Demo 3: Custom validation
        print(f"\n⚡ Demo 3: Custom validation")
        
        def size_validator(path: str) -> str:
            """Validate file size."""
            try:
                full_path = temp_path / "public" / path
                if full_path.exists() and full_path.is_file():
                    size = full_path.stat().st_size
                    if size > 100:
                        return f"File too large: {size} bytes (max 100)"
                return ""
            except Exception as e:
                return f"Cannot validate file: {e}"
        
        size_selector = FilePathAdapter(
            message="Select small file:",
            base_path=temp_path / "public",
            files_only=True
        )
        size_selector.enable_validation(size_validator)
        
        size_selector.set_value("welcome.txt")
        is_valid, msg = size_selector.validate_current_path()
        print(f"  'welcome.txt': {'✅ Valid' if is_valid else f'❌ {msg}'}")
        
        # Demo 4: Security boundaries
        print(f"\n🛡️  Demo 4: Security boundaries")
        
        # Navigator restricted to public directory
        public_navigator = FileSystemNavigator(base_path=temp_path / "public")
        
        # Try to navigate outside (should fail)
        success = public_navigator.navigate_to(temp_path / "restricted")
        print(f"  Navigate to restricted/: {'❌ Blocked' if not success else '⚠️ Allowed'}")
        
        # Try to navigate to parent (should fail)
        success = public_navigator.navigate_to(temp_path)
        print(f"  Navigate to parent: {'❌ Blocked' if not success else '⚠️ Allowed'}")
        
        # Validate path outside base
        is_valid, msg = public_navigator.validate_path(temp_path / "restricted" / "secrets.txt")
        print(f"  Access restricted file: {'❌ Blocked' if not is_valid else '⚠️ Allowed'}")
        print(f"    Reason: {msg}")
    
    print("\n" + "=" * 50)


def demo_convenience_functions():
    """Demo convenience functions for specific file types."""
    print("🎯 Convenience Functions Demo")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create files of different types
        file_types = {
            "source_files": [
                ("main.py", "Python source"),
                ("app.js", "JavaScript source"),
                ("style.css", "CSS source"),
                ("index.html", "HTML source")
            ],
            "config_files": [
                ("config.json", '{"app": "demo"}'),
                ("settings.yaml", "app:\n  name: demo"),
                ("database.ini", "[database]\nhost=localhost")
            ],
            "images": [
                ("logo.png", "PNG image data"),
                ("banner.jpg", "JPEG image data"),
                ("icon.svg", "SVG image data")
            ],
            "documents": [
                ("README.md", "# Documentation"),
                ("guide.txt", "User guide"),
                ("manual.pdf", "PDF manual")
            ]
        }
        
        # Create directory structure
        for category, files in file_types.items():
            category_dir = temp_path / category
            category_dir.mkdir()
            for filename, content in files:
                (category_dir / filename).write_text(content)
        
        print(f"📋 Created file type demo structure:")
        for category in file_types:
            file_count = len(file_types[category])
            print(f"  📁 {category}/ ({file_count} files)")
        
        # Demo convenience functions
        convenience_demos = [
            ("🐍 Source file selector (Python)", lambda: create_source_file_selector(
                base_path=temp_path / "source_files",
                language='python'
            )),
            ("📜 Source file selector (JavaScript)", lambda: create_source_file_selector(
                base_path=temp_path / "source_files",
                language='javascript'
            )),
            ("⚙️ Config file selector", lambda: create_config_file_selector(
                base_path=temp_path / "config_files"
            )),
            ("🖼️ Image file selector", lambda: create_image_file_selector(
                base_path=temp_path / "images"
            )),
            ("📁 Directory selector", lambda: create_directory_selector(
                base_path=temp_path
            ))
        ]
        
        for demo_name, selector_func in convenience_demos:
            print(f"\n{demo_name}:")
            try:
                selector = selector_func()
                
                # Show what files this selector finds
                completions = selector.get_path_completions("")
                if completions:
                    print(f"  Found {len(completions)} matching items:")
                    for completion in completions[:5]:
                        print(f"    • {completion}")
                    if len(completions) > 5:
                        print(f"    ... and {len(completions) - 5} more")
                else:
                    print("  No matching files found")
                
                # Show widget configuration
                info = selector.get_widget_info()
                if info.get('allowed_extensions'):
                    extensions = ", ".join(info['allowed_extensions'])
                    print(f"  Allowed extensions: {extensions}")
                
                if info.get('files_only'):
                    print("  Mode: Files only")
                elif info.get('dirs_only'):
                    print("  Mode: Directories only")
                
            except Exception as e:
                print(f"  ❌ Error creating selector: {e}")
    
    print("\n" + "=" * 50)


def demo_performance_features():
    """Demo performance and caching features."""
    print("⚡ Performance & Caching Demo")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a large directory structure for performance testing
        print(f"🏗️  Creating large directory structure...")
        
        # Create multiple subdirectories with many files
        for i in range(5):
            subdir = temp_path / f"dir_{i:02d}"
            subdir.mkdir()
            
            # Create many files in each subdirectory
            for j in range(20):
                filename = f"file_{j:03d}.txt"
                (subdir / filename).write_text(f"Content for {filename}")
        
        # Create mixed file types
        extensions = ['.py', '.js', '.json', '.md', '.txt', '.log']
        for i, ext in enumerate(extensions):
            for j in range(10):
                filename = f"test_{j:02d}{ext}"
                (temp_path / filename).write_text(f"Test file {filename}")
        
        total_files = sum(len(list(d.iterdir())) for d in temp_path.iterdir() if d.is_dir())
        total_files += len([f for f in temp_path.iterdir() if f.is_file()])
        print(f"  ✅ Created {total_files} files and directories")
        
        # Demo 1: Directory listing performance
        print(f"\n📋 Demo 1: Directory listing performance")
        
        navigator = FileSystemNavigator(base_path=temp_path)
        
        start_time = time.time()
        items = navigator.list_current_directory()
        end_time = time.time()
        
        duration = (end_time - start_time) * 1000
        print(f"  Listed {len(items)} items in {duration:.1f}ms")
        
        # Show breakdown by type
        files = [item for item in items if item['is_file']]
        dirs = [item for item in items if item['is_dir'] and not item['is_parent']]
        print(f"  📄 Files: {len(files)}")
        print(f"  📁 Directories: {len(dirs)}")
        
        # Demo 2: Path completion performance
        print(f"\n🔍 Demo 2: Path completion performance")
        
        completion_tests = ["test", "file", "dir", "py", "js"]
        
        for query in completion_tests:
            start_time = time.time()
            completions = navigator.get_path_completions(query)
            end_time = time.time()
            
            duration = (end_time - start_time) * 1000
            print(f"  Query '{query}': {len(completions)} results in {duration:.1f}ms")
        
        # Demo 3: Filtered navigation performance
        print(f"\n🐍 Demo 3: Filtered navigation performance")
        
        # Test with different file type filters
        filter_tests = [
            ("Python files", {'.py'}),
            ("JavaScript files", {'.js'}),
            ("Config files", {'.json', '.yaml', '.ini'}),
            ("Text files", {'.txt', '.md'}),
        ]
        
        for filter_name, extensions in filter_tests:
            start_time = time.time()
            
            filtered_navigator = FileSystemNavigator(
                base_path=temp_path,
                allowed_extensions=extensions,
                files_only=True
            )
            
            filtered_items = filtered_navigator.list_current_directory()
            end_time = time.time()
            
            duration = (end_time - start_time) * 1000
            file_count = len([item for item in filtered_items if item['is_file']])
            print(f"  {filter_name}: {file_count} files in {duration:.1f}ms")
        
        # Demo 4: Memory efficiency
        print(f"\n💾 Demo 4: Memory efficiency")
        
        # Test with large directory
        large_navigator = FileSystemNavigator(base_path=temp_path)
        
        # Navigate to a subdirectory
        subdir = temp_path / "dir_00"
        success = large_navigator.navigate_to(subdir)
        if success:
            subdir_items = large_navigator.list_current_directory()
            print(f"  Subdirectory items: {len(subdir_items)}")
            
            # Test path info retrieval
            path_info = large_navigator.get_current_path_info()
            print(f"  Current path info retrieved: {len(path_info)} fields")
            
            # Navigate back
            large_navigator.navigate_up()
            print(f"  ✅ Navigation completed efficiently")
    
    print("\n" + "=" * 50)


def demo_theme_integration():
    """Demo theme integration with file browsers."""
    print("🎨 Theme Integration Demo")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create sample files
        (temp_path / "document.txt").write_text("Sample document")
        (temp_path / "config.json").write_text('{"theme": "demo"}')
        (temp_path / "script.py").write_text("print('Hello')")
        
        themes = ['professional_blue', 'dark_mode', 'high_contrast', 'classic_terminal', 'minimal']
        
        print(f"📋 Available themes: {', '.join(themes)}")
        
        # Create file selector with each theme
        for theme in themes:
            print(f"\n🎨 Theme: {theme}")
            
            file_selector = FilePathAdapter(
                message=f"File browser with {theme} theme:",
                base_path=temp_path,
                style=theme
            )
            
            # Show theme info
            info = file_selector.get_widget_info()
            print(f"  Current theme: {info['theme']}")
            print(f"  Questionary enhanced: {info['use_questionary']}")
            
            # List files with theme
            items = file_selector.list_current_directory()
            print(f"  Files displayed:")
            for item in items:
                if item['is_file']:
                    print(f"    {item['display_name']}")
            
            # Test theme switching
            if file_selector.is_questionary_enhanced():
                # Switch to next theme
                next_theme_idx = (themes.index(theme) + 1) % len(themes)
                next_theme = themes[next_theme_idx]
                
                file_selector.change_theme(next_theme)
                updated_info = file_selector.get_widget_info()
                print(f"  ✅ Switched to: {updated_info['theme']}")
            else:
                print(f"  ⚠️  Theme switching requires Questionary")
    
    print("\n" + "=" * 50)


def main():
    """Run all FilePathAdapter demos."""
    print("🚀 FilePathAdapter Feature Demonstration")
    print("=" * 70)
    print("This demo showcases the advanced file path selection capabilities")
    print("including file browser integration, validation, and security features.")
    print("=" * 70)
    print()
    
    demos = [
        demo_file_system_navigator,
        demo_basic_file_selection,
        demo_advanced_file_operations,
        demo_validation_and_security,
        demo_convenience_functions,
        demo_performance_features,
        demo_theme_integration
    ]
    
    for i, demo_func in enumerate(demos, 1):
        try:
            demo_func()
            if i < len(demos):
                print()
        except Exception as e:
            print(f"❌ Demo {demo_func.__name__} failed: {e}")
            print()
    
    print("🎉 FilePathAdapter demonstration complete!")
    print("This adapter provides professional file browser functionality")
    print("with security, validation, filtering, and performance optimizations")
    print("for modern terminal-based file selection interfaces.")


if __name__ == "__main__":
    main()