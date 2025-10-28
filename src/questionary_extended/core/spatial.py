"""
Spatial awareness and buffer management for TUI elements.

This module provides the foundational data structures and interfaces for
spatial-aware rendering, where elements know their space requirements and
the page manages buffer positioning and updates.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Protocol, Tuple
from abc import ABC, abstractmethod


@dataclass
class SpaceRequirement:
    """Represents an element's space requirements and constraints."""
    
    min_lines: int          # Minimum lines needed to render (compressed)
    current_lines: int      # Current lines being used
    max_lines: int         # Maximum lines this element could ever need
    preferred_lines: int   # Ideal lines for optimal display
    
    def can_fit_in(self, available_lines: int) -> bool:
        """Check if this element can fit in the given space."""
        return self.min_lines <= available_lines
    
    def is_compressed(self) -> bool:
        """Check if element is currently using less than preferred space."""
        return self.current_lines < self.preferred_lines
    
    def can_expand(self) -> bool:
        """Check if element could use more space."""
        return self.current_lines < self.max_lines


@dataclass 
class ElementPosition:
    """Tracks an element's position and allocation in the terminal buffer."""
    
    element_id: str         # Unique identifier
    start_line: int         # 0-indexed starting line in terminal
    allocated_lines: int    # Lines currently allocated to this element
    last_rendered_lines: int # Lines used in last render (may be < allocated)
    
    @property
    def end_line(self) -> int:
        """Last line occupied by this element (exclusive)."""
        return self.start_line + self.allocated_lines
    
    def contains_line(self, line_number: int) -> bool:
        """Check if the given line is within this element's allocation."""
        return self.start_line <= line_number < self.end_line


@dataclass
class BufferDelta:
    """Represents changes to an element's buffer content."""
    
    line_updates: List[Tuple[int, str]]  # [(relative_line, new_content), ...]
    space_change: int                    # Change in lines needed (+/- from current)
    clear_lines: List[int]              # Relative lines to clear completely
    
    def has_space_change(self) -> bool:
        """Check if this delta requires space reallocation."""
        return self.space_change != 0
    
    def has_content_changes(self) -> bool:
        """Check if this delta has content updates."""
        return bool(self.line_updates or self.clear_lines)


class SpatiallyAware(Protocol):
    """Protocol for elements that can manage their own space requirements."""
    
    def calculate_space_requirements(self) -> SpaceRequirement:
        """Calculate current space requirements for this element."""
        ...
    
    def calculate_buffer_changes(self) -> BufferDelta:
        """Calculate what changes are needed within allocated space."""
        ...
    
    def can_compress_to(self, lines: int) -> bool:
        """Check if element can be compressed to fit in given lines."""
        ...
    
    def compress_to_lines(self, lines: int) -> None:
        """Compress element content to fit in specified lines."""
        ...


class BufferManager(ABC):
    """Abstract interface for terminal buffer management."""
    
    @abstractmethod
    def allocate_space(self, element_id: str, requirement: SpaceRequirement) -> ElementPosition:
        """Allocate space for an element and return its position."""
        pass
    
    @abstractmethod
    def reallocate_space(self, element_id: str, new_requirement: SpaceRequirement) -> ElementPosition:
        """Reallocate space for an element with new requirements."""
        pass
    
    @abstractmethod
    def apply_buffer_delta(self, position: ElementPosition, delta: BufferDelta) -> None:
        """Apply changes to the terminal buffer at the given position."""
        pass
    
    @abstractmethod
    def get_element_position(self, element_id: str) -> Optional[ElementPosition]:
        """Get current position information for an element."""
        pass
    
    @abstractmethod
    def remove_element(self, element_id: str) -> None:
        """Remove an element and reclaim its space."""
        pass


@dataclass
class LayoutCalculation:
    """Result of a layout calculation for all elements."""
    
    positions: Dict[str, ElementPosition]  # All element positions
    total_lines: int                      # Total lines needed
    conflicts: List[str]                  # Elements that couldn't fit
    
    def get_position(self, element_id: str) -> Optional[ElementPosition]:
        """Get position for a specific element."""
        return self.positions.get(element_id)
    
    def has_conflicts(self) -> bool:
        """Check if any elements couldn't be positioned."""
        return bool(self.conflicts)


class LayoutEngine:
    """Engine for calculating optimal layout of spatial elements."""
    
    def __init__(self, terminal_height: Optional[int] = None):
        self.terminal_height = terminal_height or 50  # Default reasonable height
    
    def calculate_layout(self, elements: Dict[str, SpatiallyAware]) -> LayoutCalculation:
        """Calculate optimal layout for all elements."""
        positions = {}
        current_line = 0
        conflicts = []
        
        for element_id, element in elements.items():
            space_req = element.calculate_space_requirements()
            
            # Check if element can fit
            remaining_space = self.terminal_height - current_line
            if space_req.min_lines > remaining_space:
                conflicts.append(element_id)
                continue
            
            # Allocate space (prefer current_lines, but compress if needed)
            allocated_lines = min(space_req.current_lines, remaining_space)
            if allocated_lines < space_req.min_lines:
                allocated_lines = space_req.min_lines
            
            positions[element_id] = ElementPosition(
                element_id=element_id,
                start_line=current_line,
                allocated_lines=allocated_lines,
                last_rendered_lines=allocated_lines
            )
            
            current_line += allocated_lines
        
        return LayoutCalculation(
            positions=positions,
            total_lines=current_line,
            conflicts=conflicts
        )
    
    def can_expand_element(self, element_id: str, additional_lines: int, 
                          current_layout: LayoutCalculation) -> bool:
        """Check if an element can be expanded by the given number of lines."""
        position = current_layout.get_position(element_id)
        if not position:
            return False
        
        # Check if expansion would exceed terminal height
        new_end = position.end_line + additional_lines
        return new_end <= self.terminal_height