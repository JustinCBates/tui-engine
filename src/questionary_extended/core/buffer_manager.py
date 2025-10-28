"""
Terminal buffer management implementation.

Provides concrete implementation of buffer management with ANSI escape
sequences for smooth, flicker-free updates.
"""

import os
import sys
from typing import Dict, Optional, List
from .spatial import BufferManager, ElementPosition, SpaceRequirement, BufferDelta


class ANSIBufferManager(BufferManager):
    """
    ANSI-based terminal buffer manager.
    
    Handles direct terminal manipulation using ANSI escape sequences
    for precise cursor positioning and line management.
    """
    
    def __init__(self, terminal_height: Optional[int] = None):
        self._element_positions: Dict[str, ElementPosition] = {}
        self._terminal_height = terminal_height or self._detect_terminal_height()
        self._next_available_line = 0
        
    def _detect_terminal_height(self) -> int:
        """Detect terminal height or use reasonable default."""
        try:
            return os.get_terminal_size().lines
        except OSError:
            return 50  # Reasonable default
    
    def allocate_space(self, element_id: str, requirement: SpaceRequirement) -> ElementPosition:
        """Allocate space for an element and return its position."""
        if element_id in self._element_positions:
            raise ValueError(f"Element '{element_id}' already has allocated space")
        
        # Calculate available space
        available_lines = self._terminal_height - self._next_available_line
        
        # Determine allocation
        if requirement.current_lines <= available_lines:
            allocated_lines = requirement.current_lines
        elif requirement.min_lines <= available_lines:
            allocated_lines = requirement.min_lines
        else:
            raise ValueError(f"Element '{element_id}' requires {requirement.min_lines} lines but only {available_lines} available")
        
        # Create position
        position = ElementPosition(
            element_id=element_id,
            start_line=self._next_available_line,
            allocated_lines=allocated_lines,
            last_rendered_lines=0
        )
        
        # Update tracking
        self._element_positions[element_id] = position
        self._next_available_line += allocated_lines
        
        return position
    
    def reallocate_space(self, element_id: str, new_requirement: SpaceRequirement) -> ElementPosition:
        """Reallocate space for an element with new requirements."""
        current_position = self._element_positions.get(element_id)
        if not current_position:
            return self.allocate_space(element_id, new_requirement)
        
        space_change = new_requirement.current_lines - current_position.allocated_lines
        
        if space_change == 0:
            return current_position  # No change needed
        
        if space_change > 0:
            # Element needs more space - expand
            return self._expand_element(element_id, space_change)
        else:
            # Element needs less space - contract
            return self._contract_element(element_id, -space_change)
    
    def _expand_element(self, element_id: str, additional_lines: int) -> ElementPosition:
        """Expand an element's allocation."""
        position = self._element_positions[element_id]
        
        # Insert lines in terminal to make space
        insertion_point = position.end_line + 1  # 1-indexed for ANSI
        self._insert_terminal_lines(insertion_point, additional_lines)
        
        # Update position
        position.allocated_lines += additional_lines
        
        # Update all positions below this element
        self._shift_positions_below(position.start_line, additional_lines)
        self._next_available_line += additional_lines
        
        return position
    
    def _contract_element(self, element_id: str, lines_to_remove: int) -> ElementPosition:
        """Contract an element's allocation."""
        position = self._element_positions[element_id]
        
        # Remove lines from terminal
        deletion_point = position.end_line - lines_to_remove + 1  # 1-indexed
        self._delete_terminal_lines(deletion_point, lines_to_remove)
        
        # Update position
        position.allocated_lines -= lines_to_remove
        
        # Update all positions below this element
        self._shift_positions_below(position.start_line, -lines_to_remove)
        self._next_available_line -= lines_to_remove
        
        return position
    
    def apply_buffer_delta(self, position: ElementPosition, delta: BufferDelta) -> None:
        """Apply changes to the terminal buffer at the given position."""
        # Handle space changes first
        if delta.has_space_change():
            # This should have been handled by reallocate_space
            pass
        
        # Track what we've already rendered to avoid duplication
        if not hasattr(self, '_rendered_content'):
            self._rendered_content = {}
        
        element_key = f"{position.element_id}_{position.start_line}"
        
        # Use ANSI positioning to update or clear specific lines. This avoids
        # appending duplicate content to the terminal and ensures old content
        # is cleared when elements shrink.
        if not hasattr(self, '_rendered_content'):
            self._rendered_content = {}

        # Clear any requested lines first
        if delta.clear_lines:
            for rel_line in sorted(delta.clear_lines):
                abs_line = position.start_line + rel_line
                # Clear the specific terminal line
                print(f"\x1b[{abs_line + 1};1H\x1b[2K", end="")

        if delta.line_updates:
            # Sort by line number to update in order
            sorted_updates = sorted(delta.line_updates, key=lambda x: x[0])
            new_content = [content for _, content in sorted_updates]

            # Only write if content differs from last render
            if element_key not in self._rendered_content or self._rendered_content[element_key] != new_content:
                for rel_line, content in sorted_updates:
                    abs_line = position.start_line + rel_line
                    # Position cursor, clear the line, and write the new content
                    # Use normal print (with newline) to ensure the terminal
                    # cursor moves to the start of the following line after the write.
                    print(f"\x1b[{abs_line + 1};1H\x1b[2K{content}")
                # Remember what we rendered for this element
                self._rendered_content[element_key] = new_content

            # Update tracking
            max_line_used = max(rel_line for rel_line, _ in delta.line_updates) + 1
            position.last_rendered_lines = max_line_used
        # Ensure output is flushed so the terminal state is updated promptly
        try:
            sys.stdout.flush()
        except Exception:
            pass
    
    def _position_cursor_at_end(self) -> None:
        """Position cursor at the end of all rendered content."""
        if not self._element_positions:
            # No elements, just move to a safe position
            print("\x1b[1;1H", end="")  # Move to top-left
            sys.stdout.flush()
            return
            
        # Find the last line with content
        max_end_line = 0
        for pos in self._element_positions.values():
            if hasattr(pos, 'last_rendered_lines') and pos.last_rendered_lines > 0:
                content_end = pos.start_line + pos.last_rendered_lines
                max_end_line = max(max_end_line, content_end)
        
        # Safety check - ensure we don't go beyond terminal bounds
        if max_end_line > self._terminal_height - 2:
            max_end_line = self._terminal_height - 2
        
        # Move cursor to the line after all content
        target_line = max_end_line + 1
        if target_line > 0:
            print(f"\x1b[{target_line};1H", end="")
            sys.stdout.flush()
    
    def get_element_position(self, element_id: str) -> Optional[ElementPosition]:
        """Get current position information for an element."""
        return self._element_positions.get(element_id)
    
    def remove_element(self, element_id: str) -> None:
        """Remove an element and reclaim its space."""
        position = self._element_positions.get(element_id)
        if not position:
            return
        
        # Clear the element's content
        for line_offset in range(position.allocated_lines):
            terminal_line = position.start_line + line_offset + 1
            self._clear_terminal_line(terminal_line)
        
        # Remove the lines from terminal
        self._delete_terminal_lines(position.start_line + 1, position.allocated_lines)
        
        # Update positions of elements below
        self._shift_positions_below(position.start_line, -position.allocated_lines)
        self._next_available_line -= position.allocated_lines
        
        # Remove from tracking
        del self._element_positions[element_id]
    
    # ANSI Terminal Operations
    def _insert_terminal_lines(self, line_number: int, count: int) -> None:
        """Insert blank lines at specified position (1-indexed)."""
        print(f"\x1b[{line_number};1H", end="")  # Move to position
        print(f"\x1b[{count}L", end="")          # Insert lines
        sys.stdout.flush()
    
    def _delete_terminal_lines(self, line_number: int, count: int) -> None:
        """Delete lines at specified position (1-indexed)."""
        print(f"\x1b[{line_number};1H", end="")  # Move to position
        print(f"\x1b[{count}M", end="")          # Delete lines
        sys.stdout.flush()
    
    def _clear_terminal_line(self, line_number: int) -> None:
        """Clear a specific line (1-indexed)."""
        print(f"\x1b[{line_number};1H", end="")  # Move to line
        print(f"\x1b[2K", end="")                # Clear line
        sys.stdout.flush()
    
    def _update_terminal_line(self, line_number: int, content: str) -> None:
        """Update a specific line with new content (1-indexed)."""
        print(f"\x1b[{line_number};1H", end="")  # Move to line
        print(f"\x1b[2K{content}", end="")       # Clear and write
        sys.stdout.flush()
    
    def _shift_positions_below(self, start_line: int, offset: int) -> None:
        """Update positions of all elements below the given line."""
        for position in self._element_positions.values():
            if position.start_line > start_line:
                position.start_line += offset


class FallbackBufferManager(BufferManager):
    """
    Fallback buffer manager for environments with limited ANSI support.
    
    Uses simple line-by-line printing without cursor manipulation.
    """
    
    def __init__(self):
        self._element_positions: Dict[str, ElementPosition] = {}
        self._next_available_line = 0
    
    def allocate_space(self, element_id: str, requirement: SpaceRequirement) -> ElementPosition:
        """Allocate space by tracking line positions."""
        position = ElementPosition(
            element_id=element_id,
            start_line=self._next_available_line,
            allocated_lines=requirement.current_lines,
            last_rendered_lines=0
        )
        
        self._element_positions[element_id] = position
        self._next_available_line += requirement.current_lines
        
        return position
    
    def reallocate_space(self, element_id: str, new_requirement: SpaceRequirement) -> ElementPosition:
        """In fallback mode, just print the changes linearly."""
        return self.allocate_space(element_id, new_requirement)
    
    def apply_buffer_delta(self, position: ElementPosition, delta: BufferDelta) -> None:
        """Apply changes by printing them sequentially."""
        for relative_line, content in delta.line_updates:
            print(content)
    
    def get_element_position(self, element_id: str) -> Optional[ElementPosition]:
        """Get position information."""
        return self._element_positions.get(element_id)
    
    def remove_element(self, element_id: str) -> None:
        """Remove element from tracking."""
        if element_id in self._element_positions:
            del self._element_positions[element_id]