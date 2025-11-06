#!/usr/bin/env python3
"""Demo script showcasing AutocompleteAdapter capabilities.

This script demonstrates the various features of the AutocompleteAdapter
including different completion algorithms, themes, and real-world usage scenarios.
"""
import sys
import os
from pathlib import Path

# Add the project src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from typing import List
import time

# Import our autocomplete components
from tui_engine.widgets.autocomplete_adapter import (
    AutocompleteAdapter,
    create_autocomplete,
    create_file_autocomplete,
    create_command_autocomplete,
    CompletionEngine
)


def demo_completion_engine():
    """Demonstrate the CompletionEngine capabilities."""
    print("🧪 CompletionEngine Algorithm Demo")
    print("=" * 50)
    
    # Test data representing programming languages and frameworks
    candidates = [
        "python", "javascript", "typescript", "java", "csharp", "golang",
        "rust", "swift", "kotlin", "scala", "ruby", "php", "perl",
        "react", "vue", "angular", "django", "flask", "fastapi",
        "spring", "express", "nextjs", "svelte", "laravel"
    ]
    
    engine = CompletionEngine(
        case_sensitive=False,
        fuzzy_threshold=0.6,
        max_results=5,
        prefer_prefix=True
    )
    
    test_queries = [
        ("py", "prefix"),
        ("script", "substring"), 
        ("reactjs", "fuzzy"),
        ("java", "smart"),
        ("ang", "smart")
    ]
    
    for query, algorithm in test_queries:
        print(f"\n🔍 Query: '{query}' using {algorithm} algorithm")
        results = engine.complete(query, candidates, algorithm)
        
        for i, (candidate, score) in enumerate(results, 1):
            print(f"  {i}. {candidate:<12} (score: {score:.3f})")
    
    print("\n" + "=" * 50)


def demo_programming_language_autocomplete():
    """Demo autocomplete for programming languages with dynamic sources."""
    print("💻 Programming Language Autocomplete Demo")
    print("=" * 50)
    
    # Static list of popular languages
    languages = [
        "python", "javascript", "typescript", "java", "c", "cpp", "csharp",
        "go", "rust", "swift", "kotlin", "scala", "ruby", "php", "perl"
    ]
    
    # Dynamic source for frameworks
    def framework_source(query: str) -> List[str]:
        frameworks = {
            "py": ["django", "flask", "fastapi", "pyramid", "tornado"],
            "js": ["react", "vue", "angular", "express", "nextjs", "svelte"],
            "java": ["spring", "spring-boot", "hibernate", "struts"],
            "go": ["gin", "echo", "fiber", "beego"],
            "rust": ["rocket", "actix-web", "warp", "tower"]
        }
        
        results = []
        for prefix, items in frameworks.items():
            if query.lower().startswith(prefix):
                results.extend(items)
        return results
    
    # Create autocomplete adapter
    adapter = create_autocomplete(
        message="Choose a programming language or framework:",
        completions=languages,
        style='professional_blue'
    )
    
    # Add the framework source
    adapter.add_completion_source(framework_source)
    
    print("📋 Available features:")
    print("  • Static completions for popular languages")
    print("  • Dynamic framework suggestions based on language prefixes")
    print("  • Intelligent ranking with smart algorithm")
    print("  • Professional blue theme styling")
    
    # Demo queries
    test_queries = ["py", "js", "java", "go", "rust", "script", "spring"]
    
    for query in test_queries:
        print(f"\n🔍 Completions for '{query}':")
        completions = adapter.get_completions(query)
        
        if completions:
            for i, (completion, score) in enumerate(completions[:5], 1):
                print(f"  {i}. {completion:<15} (score: {score:.3f})")
        else:
            print("  No completions found")
    
    # Show adapter stats
    stats = adapter.get_completion_stats()
    print(f"\n📊 Adapter Statistics:")
    print(f"  • Completion sources: {stats['completion_sources']}")
    print(f"  • Algorithm: {stats['algorithm']}")
    print(f"  • Max results: {stats['max_results']}")
    print(f"  • Cache enabled: {stats['cache_enabled']}")
    
    print("\n" + "=" * 50)


def demo_configuration_autocomplete():
    """Demo autocomplete for configuration keys."""
    print("⚙️  Configuration Key Autocomplete Demo")
    print("=" * 50)
    
    # Comprehensive configuration keys
    config_keys = [
        # Database settings
        "database.host", "database.port", "database.name", "database.user",
        "database.password", "database.ssl", "database.timeout",
        
        # Server settings
        "server.host", "server.port", "server.ssl.enabled", "server.ssl.cert",
        "server.ssl.key", "server.max_connections", "server.timeout",
        
        # Cache settings
        "cache.redis.host", "cache.redis.port", "cache.redis.db",
        "cache.memcached.servers", "cache.default_timeout",
        
        # Logging settings
        "logging.level", "logging.file", "logging.format", "logging.rotation",
        "logging.max_size", "logging.backup_count",
        
        # Security settings
        "security.secret_key", "security.algorithm", "security.token_expiry",
        "security.password_min_length", "security.max_login_attempts"
    ]
    
    # Create configuration autocomplete
    config_adapter = create_autocomplete(
        message="Enter configuration key:",
        completions=config_keys,
        algorithm="substring",  # Good for hierarchical keys
        style='dark_mode'
    )
    
    print("📋 Configuration categories available:")
    categories = set(key.split('.')[0] for key in config_keys)
    for category in sorted(categories):
        count = len([k for k in config_keys if k.startswith(category + '.')])
        print(f"  • {category:<10} ({count} settings)")
    
    # Demo different types of queries
    test_queries = [
        ("host", "Find all host-related settings"),
        ("database", "Database configuration"),
        ("ssl", "SSL/Security settings"),
        ("log", "Logging configuration"),
        ("port", "Port settings"),
        ("timeout", "Timeout configurations")
    ]
    
    for query, description in test_queries:
        print(f"\n🔍 {description} ('{query}'):")
        completions = config_adapter.get_completions(query)
        
        for i, (completion, score) in enumerate(completions[:4], 1):
            print(f"  {i}. {completion:<25} (score: {score:.3f})")
    
    print("\n" + "=" * 50)


def demo_api_endpoint_autocomplete():
    """Demo autocomplete for API endpoints."""
    print("🌐 API Endpoint Autocomplete Demo")
    print("=" * 50)
    
    def api_endpoint_source(query: str) -> List[str]:
        """Dynamic API endpoint source."""
        endpoints = [
            # User endpoints
            "/api/v1/users", "/api/v1/users/{id}", "/api/v1/users/{id}/profile",
            "/api/v1/users/{id}/posts", "/api/v1/users/{id}/followers",
            
            # Post endpoints
            "/api/v1/posts", "/api/v1/posts/{id}", "/api/v1/posts/{id}/comments",
            "/api/v1/posts/{id}/likes", "/api/v1/posts/search",
            
            # Authentication endpoints
            "/api/v1/auth/login", "/api/v1/auth/logout", "/api/v1/auth/refresh",
            "/api/v1/auth/register", "/api/v1/auth/reset-password",
            
            # Admin endpoints
            "/api/v1/admin/users", "/api/v1/admin/users/{id}/ban",
            "/api/v1/admin/posts/moderate", "/api/v1/admin/settings",
            
            # Health and metrics
            "/api/v1/health", "/api/v1/metrics", "/api/v1/status"
        ]
        
        # Return endpoints that contain the query
        return [ep for ep in endpoints if query.lower() in ep.lower()]
    
    # Create API endpoint autocomplete
    api_adapter = AutocompleteAdapter(
        message="Enter API endpoint:",
        completion_sources=[api_endpoint_source],
        algorithm="substring",
        min_input_length=2,
        style='high_contrast'
    )
    
    print("📋 API endpoint categories:")
    print("  • User management (/api/v1/users/*)")
    print("  • Post operations (/api/v1/posts/*)")
    print("  • Authentication (/api/v1/auth/*)")
    print("  • Administration (/api/v1/admin/*)")
    print("  • System health (/api/v1/health, /api/v1/metrics)")
    
    # Demo queries for different use cases
    test_queries = [
        ("user", "User-related endpoints"),
        ("post", "Post-related endpoints"),
        ("auth", "Authentication endpoints"),
        ("admin", "Admin endpoints"),
        ("{id}", "Endpoints with path parameters"),
        ("v1", "All v1 API endpoints")
    ]
    
    for query, description in test_queries:
        print(f"\n🔍 {description} ('{query}'):")
        completions = api_adapter.get_completions(query)
        
        for i, (completion, score) in enumerate(completions[:4], 1):
            print(f"  {i}. {completion:<30} (score: {score:.3f})")
    
    print("\n" + "=" * 50)


def demo_file_path_autocomplete():
    """Demo file path autocomplete."""
    print("📁 File Path Autocomplete Demo")
    print("=" * 50)
    
    # Create file autocomplete for the current project
    file_adapter = create_file_autocomplete(
        message="Choose a file:",
        base_path="./src",
        extensions=[".py", ".md", ".txt", ".json"]
    )
    
    print("📋 File path autocomplete features:")
    print("  • Searches in ./src directory")
    print("  • Filters by extensions: .py, .md, .txt, .json")
    print("  • Uses prefix matching algorithm")
    print("  • Provides relative path completions")
    
    # Demo with some common patterns
    test_queries = ["tui", "widget", "adapt", "__init__", "test"]
    
    for query in test_queries:
        print(f"\n🔍 Files matching '{query}':")
        completions = file_adapter.get_completions(query)
        
        for i, (completion, score) in enumerate(completions[:4], 1):
            print(f"  {i}. {completion:<25} (score: {score:.3f})")
    
    print("\n" + "=" * 50)


def demo_command_autocomplete():
    """Demo command autocomplete."""
    print("⚡ Command Autocomplete Demo")
    print("=" * 50)
    
    # Custom project commands
    project_commands = [
        "build", "test", "lint", "format", "deploy", "clean",
        "install", "upgrade", "start", "stop", "restart",
        "migrate", "backup", "restore", "logs", "status"
    ]
    
    command_adapter = create_command_autocomplete(
        message="Enter command:",
        commands=project_commands
    )
    
    print("📋 Available command types:")
    print("  • Project commands (build, test, deploy, etc.)")
    print("  • System commands (ls, cd, git, python, etc.)")
    print("  • Smart prefix matching with fallback to fuzzy")
    
    # Demo various command patterns
    test_queries = ["te", "build", "git", "py", "doc", "star"]
    
    for query in test_queries:
        print(f"\n🔍 Commands matching '{query}':")
        completions = command_adapter.get_completions(query)
        
        for i, (completion, score) in enumerate(completions[:5], 1):
            print(f"  {i}. {completion:<15} (score: {score:.3f})")
    
    print("\n" + "=" * 50)


def demo_validation_features():
    """Demo validation features."""
    print("✅ Validation Features Demo")
    print("=" * 50)
    
    # Create adapter with validation
    adapter = create_autocomplete(
        message="Enter a valid email:",
        completions=["user@example.com", "admin@company.org", "test@domain.net"],
        style='minimal'
    )
    
    # Email validation function
    def email_validator(email: str) -> str:
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, email):
            return ""  # Valid
        return "Please enter a valid email address"
    
    adapter.enable_validation(email_validator)
    
    print("📋 Email validation demo:")
    print("  • Uses regex pattern for email validation")
    print("  • Provides helpful error messages")
    print("  • Can be enabled/disabled dynamically")
    
    # Test various inputs
    test_inputs = [
        "user@example.com",
        "invalid-email",
        "test@domain",
        "admin@company.org",
        "not_an_email"
    ]
    
    for test_input in test_inputs:
        is_valid, message = adapter.validate_input(test_input)
        status = "✅ Valid" if is_valid else f"❌ Invalid: {message}"
        print(f"  '{test_input}' -> {status}")
    
    print("\n" + "=" * 50)


def demo_theme_showcase():
    """Demo different themes."""
    print("🎨 Theme Showcase Demo")
    print("=" * 50)
    
    themes = ['professional_blue', 'dark_mode', 'high_contrast', 'classic_terminal', 'minimal']
    
    base_adapter = create_autocomplete(
        message="Choose a theme:",
        completions=themes,
        style='professional_blue'
    )
    
    print("📋 Available themes:")
    for i, theme in enumerate(themes, 1):
        print(f"  {i}. {theme}")
    
    print("\n🎨 Theme switching demonstration:")
    for theme in themes:
        print(f"\n  Switching to '{theme}' theme...")
        base_adapter.change_theme(theme)
        info = base_adapter.get_widget_info()
        print(f"    Current theme: {info['theme']}")
        print(f"    Questionary enhanced: {info['use_questionary']}")
    
    print("\n" + "=" * 50)


def demo_performance_features():
    """Demo performance and caching features."""
    print("🚀 Performance & Caching Demo")
    print("=" * 50)
    
    # Create a large dataset for performance testing
    large_dataset = [f"item_{i:04d}" for i in range(1000)]
    
    # Simulate expensive computation source
    def expensive_source(query: str) -> List[str]:
        """Simulate an expensive completion source."""
        print(f"    Computing expensive completions for '{query}'...")
        time.sleep(0.1)  # Simulate network/database delay
        return [item for item in large_dataset if query in item][:20]
    
    # Create adapter with caching
    adapter = AutocompleteAdapter(
        message="Search large dataset:",
        completion_sources=[expensive_source],
        cache_completions=True,
        cache_size=64,
        max_results=10
    )
    
    print("📋 Performance features:")
    print("  • LRU cache for completion results")
    print("  • Configurable cache size")
    print("  • Expensive computation simulation")
    print("  • Large dataset (1000 items)")
    
    # Test caching by repeating queries
    test_queries = ["001", "050", "100", "001", "050"]  # Repeat some queries
    
    print(f"\n⏱️  Testing with {len(large_dataset)} items:")
    
    for query in test_queries:
        start_time = time.time()
        completions = adapter.get_completions(query)
        end_time = time.time()
        
        duration = (end_time - start_time) * 1000  # Convert to milliseconds
        print(f"  Query '{query}': {len(completions)} results in {duration:.1f}ms")
    
    # Show cache statistics
    stats = adapter.get_completion_stats()
    print(f"\n📊 Cache performance:")
    if stats['cache_info']:
        cache_info = stats['cache_info']
        print(f"  • Hits: {cache_info.hits}")
        print(f"  • Misses: {cache_info.misses}")
        print(f"  • Cache size: {cache_info.currsize}/{cache_info.maxsize}")
        hit_rate = cache_info.hits / (cache_info.hits + cache_info.misses) * 100 if (cache_info.hits + cache_info.misses) > 0 else 0
        print(f"  • Hit rate: {hit_rate:.1f}%")
    
    print("\n" + "=" * 50)


def main():
    """Run all AutocompleteAdapter demos."""
    print("🚀 AutocompleteAdapter Feature Demonstration")
    print("=" * 70)
    print("This demo showcases the advanced autocomplete capabilities")
    print("including intelligent completion, themes, validation, and performance.")
    print("=" * 70)
    print()
    
    demos = [
        demo_completion_engine,
        demo_programming_language_autocomplete,
        demo_configuration_autocomplete,
        demo_api_endpoint_autocomplete,
        demo_file_path_autocomplete,
        demo_command_autocomplete,
        demo_validation_features,
        demo_theme_showcase,
        demo_performance_features
    ]
    
    for i, demo_func in enumerate(demos, 1):
        try:
            demo_func()
            if i < len(demos):
                print()
        except Exception as e:
            print(f"❌ Demo {demo_func.__name__} failed: {e}")
            print()
    
    print("🎉 AutocompleteAdapter demonstration complete!")
    print("This adapter provides professional autocomplete functionality")
    print("with intelligent completion algorithms, theming, validation,")
    print("and performance optimizations for modern TUI applications.")


if __name__ == "__main__":
    main()