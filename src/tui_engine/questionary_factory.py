"""
Dependency Injection system for questionary module.

This module provides a clean dependency injection interface for the questionary
library, replacing the complex import fallback system with standard Python
patterns. It supports both production use (default questionary import) and
testing use (injected mock factories).

Example usage:
    # Production code (uses default questionary)
    questionary_module = get_questionary()
    
    # Test code (inject mock)
    set_questionary_factory(lambda: mock_questionary)
    questionary_module = get_questionary()  # Returns mock
    clear_questionary_factory()  # Reset to default

This system provides:
- Clean separation of concerns
- Standard dependency injection patterns
- Performance optimization through caching
- Simple testing patterns
- Backward compatibility with existing code
"""

from typing import Optional, Callable, Any
import logging

# Type aliases for clarity and documentation
QuestionaryFactory = Callable[[], Any]
QuestionaryModule = Any

logger = logging.getLogger(__name__)


class QuestionaryProvider:
    """
    Central provider for questionary dependencies with dependency injection support.
    
    This class manages the questionary module resolution, supporting both default
    import behavior and custom factory injection for testing scenarios.
    
    The provider uses caching to avoid repeated factory calls and improve performance,
    especially important in test scenarios where mock setup can be expensive.
    """
    
    def __init__(self):
        """Initialize the provider with no custom factory (default behavior)."""
        self._factory: Optional[QuestionaryFactory] = None
        self._cached_questionary: Optional[QuestionaryModule] = None
    
    def set_factory(self, factory: QuestionaryFactory) -> None:
        """
        Set a custom questionary factory.
        
        This is primarily used for testing, where you want to inject a mock
        questionary module instead of using the real one.
        
        Args:
            factory: A callable that returns a questionary-like module
            
        Example:
            provider.set_factory(lambda: mock_questionary)
        """
        if not callable(factory):
            raise TypeError("Factory must be callable")
            
        self._factory = factory
        self._cached_questionary = None  # Clear cache when factory changes
        logger.debug("Custom questionary factory set")
    
    def get_questionary(self) -> QuestionaryModule:
        """
        Get the questionary module via factory or default import.
        
        If a custom factory has been set (via set_factory), it will be used.
        Otherwise, the default questionary module will be imported and returned.
        
        Results are cached to improve performance, especially in test scenarios
        where the same mock might be requested many times.
        
        Returns:
            The questionary module (real or injected mock)
            
        Raises:
            ImportError: If questionary cannot be imported and no factory is set
            Exception: If the custom factory raises an exception
        """
        if self._factory is not None:
            # Use custom factory (typically for testing)
            if self._cached_questionary is None:
                try:
                    self._cached_questionary = self._factory()
                    logger.debug("Questionary module created from custom factory")
                except Exception as e:
                    logger.error(f"Custom questionary factory failed: {e}")
                    raise
            return self._cached_questionary
        
        # Default behavior - import real questionary
        try:
            import questionary
            logger.debug("Using default questionary import")
            return questionary
        except ImportError as e:
            logger.error(f"Failed to import questionary: {e}")
            raise ImportError(
                "questionary library not available. Install with: pip install questionary"
            ) from e
    
    def clear_factory(self) -> None:
        """
        Reset to default questionary import behavior.
        
        This removes any custom factory and clears the cache, returning the
        provider to its default state where it will import the real questionary
        module.
        
        This is typically called in test cleanup to ensure tests don't interfere
        with each other.
        """
        self._factory = None
        self._cached_questionary = None
        logger.debug("Questionary factory cleared, reset to default")
    
    def is_factory_set(self) -> bool:
        """
        Check if a custom factory is currently set.
        
        Returns:
            True if a custom factory is active, False if using default import
        """
        return self._factory is not None


# Global provider instance - this is the single source of truth for questionary resolution
_provider = QuestionaryProvider()


# Public API functions - these are the main interface used by application code
def set_questionary_factory(factory: QuestionaryFactory) -> None:
    """
    Set a custom questionary factory for dependency injection.
    
    This is the main function used by tests to inject mock questionary modules.
    
    Args:
        factory: A callable that returns a questionary-like module
        
    Example:
        from unittest.mock import MagicMock
        mock_questionary = MagicMock()
        set_questionary_factory(lambda: mock_questionary)
    """
    _provider.set_factory(factory)


def get_questionary() -> QuestionaryModule:
    """
    Get the questionary module (injected or default).
    
    This is the main function used by application code to get the questionary
    module. It will return either the real questionary module or an injected
    mock, depending on the current configuration.
    
    Returns:
        The questionary module (real or mock)
        
    Example:
        questionary_module = get_questionary()
        text_prompt = questionary_module.text("What's your name?")
    """
    return _provider.get_questionary()


def clear_questionary_factory() -> None:
    """
    Reset to default questionary behavior.
    
    This removes any injected factory and returns to using the real questionary
    module. Typically used in test cleanup.
    
    Example:
        # In test cleanup
        clear_questionary_factory()
    """
    _provider.clear_factory()


def is_questionary_factory_set() -> bool:
    """
    Check if a custom questionary factory is currently active.
    
    Returns:
        True if using an injected factory, False if using default import
        
    This can be useful for debugging or conditional behavior in tests.
    """
    return _provider.is_factory_set()


# For advanced use cases, expose the provider class
__all__ = [
    'QuestionaryProvider',
    'QuestionaryFactory', 
    'QuestionaryModule',
    'set_questionary_factory',
    'get_questionary',
    'clear_questionary_factory',
    'is_questionary_factory_set'
]