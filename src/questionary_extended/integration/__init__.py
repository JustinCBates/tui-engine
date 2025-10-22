"""
Integration layer for questionary-extended.

This module handles seamless integration with the original questionary library:
- Questionary Bridge: Compatibility layer ensuring existing code works unchanged
- Validators: Enhanced validation system with questionary compatibility
- Result Conversion: Format conversion between questionary and qe results
"""

from .questionary_bridge import QuestionaryBridge

__all__ = [
    "QuestionaryBridge",
]
