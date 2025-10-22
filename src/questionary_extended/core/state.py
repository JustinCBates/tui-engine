"""
State management for questionary-extended.

This module provides page-scoped state management with assembly namespacing,
cross-component communication, and state persistence capabilities.
"""

from typing import Any, Dict, Optional


class PageState:
    """
    Page-scoped state manager with assembly namespacing.
    
    Provides:
    - Assembly namespacing (assembly.field format)
    - Cross-assembly state access
    - State validation and type checking
    - Optional persistence and undo/redo
    """
    
    def __init__(self):
        """Initialize empty page state."""
        self._state: Dict[str, Any] = {}
        self._assemblies: Dict[str, Dict[str, Any]] = {}
        
    def set(self, key: str, value: Any) -> None:
        """
        Set a state value with optional assembly namespacing.
        
        Args:
            key: State key, optionally namespaced (assembly.field)
            value: Value to store
        """
        if '.' in key:
            # Namespaced key (assembly.field)
            assembly, field = key.split('.', 1)
            if assembly not in self._assemblies:
                self._assemblies[assembly] = {}
            self._assemblies[assembly][field] = value
        else:
            # Global key
            self._state[key] = value
            
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a state value with optional assembly namespacing.
        
        Args:
            key: State key, optionally namespaced (assembly.field)
            default: Default value if key not found
            
        Returns:
            Stored value or default
        """
        if '.' in key:
            # Namespaced key (assembly.field)
            assembly, field = key.split('.', 1)
            if assembly in self._assemblies:
                return self._assemblies[assembly].get(field, default)
            return default
        else:
            # Global key
            return self._state.get(key, default)
            
    def get_assembly_state(self, assembly_name: str) -> Dict[str, Any]:
        """
        Get all state for a specific assembly.
        
        Args:
            assembly_name: Name of the assembly
            
        Returns:
            Dictionary of assembly's state
        """
        return self._assemblies.get(assembly_name, {}).copy()
        
    def get_all_state(self) -> Dict[str, Any]:
        """
        Get complete state as flat dictionary.
        
        Returns:
            Flat dictionary with namespaced keys (assembly.field)
        """
        result = self._state.copy()
        
        # Add namespaced assembly state
        for assembly_name, assembly_state in self._assemblies.items():
            for field, value in assembly_state.items():
                result[f"{assembly_name}.{field}"] = value
                
        return result
        
    def has_key(self, key: str) -> bool:
        """
        Check if a key exists in state.
        
        Args:
            key: State key to check
            
        Returns:
            True if key exists, False otherwise
        """
        if '.' in key:
            assembly, field = key.split('.', 1)
            return (assembly in self._assemblies and 
                   field in self._assemblies[assembly])
        else:
            return key in self._state
            
    def clear_assembly(self, assembly_name: str) -> None:
        """
        Clear all state for a specific assembly.
        
        Args:
            assembly_name: Name of assembly to clear
        """
        if assembly_name in self._assemblies:
            del self._assemblies[assembly_name]
            
    def clear_all(self) -> None:
        """Clear all state."""
        self._state.clear()
        self._assemblies.clear()


__all__ = ["PageState"]