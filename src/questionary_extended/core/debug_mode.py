"""
Debug mode configuration for TUI Engine.

Provides centralized debug mode management for enhanced development visibility.
"""

import os
import sys
from typing import Optional


class DebugMode:
    """Centralized debug mode management."""
    
    _debug_enabled: Optional[bool] = None
    
    @classmethod
    def is_enabled(cls) -> bool:
        """Check if debug mode is enabled."""
        if cls._debug_enabled is None:
            # Check environment variable or command line
            cls._debug_enabled = (
                os.environ.get('TUI_DEBUG', '').lower() in ('1', 'true', 'yes') or
                '--debug' in sys.argv
            )
        return cls._debug_enabled
    
    @classmethod
    def enable(cls) -> None:
        """Enable debug mode."""
        cls._debug_enabled = True
    
    @classmethod
    def disable(cls) -> None:
        """Disable debug mode."""
        cls._debug_enabled = False
    
    @classmethod
    def reset(cls) -> None:
        """Reset debug mode to auto-detect."""
        cls._debug_enabled = None


def is_debug_mode() -> bool:
    """Check if debug mode is enabled (convenience function)."""
    return DebugMode.is_enabled()


def debug_prefix(element_type: str) -> str:
    """Get debug prefix for element type."""
    if not is_debug_mode():
        return ""
    
    prefixes = {
        'page': '📄 [PAGE] ',
        'card': '🎴 [CARD] ',
        'assembly': '🏗️ [ASSEMBLY] ',
        'component': '🔧 [COMPONENT] '
    }
    
    return prefixes.get(element_type.lower(), f'🔍 [{element_type.upper()}] ')