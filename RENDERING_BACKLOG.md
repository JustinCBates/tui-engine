# TUI Engine Rendering System Backlog

## Executive Summary

The TUI Engine has a sophisticated but problematic delta calculation and incremental rendering system. While the architectural foundation is solid, several critical issues prevent reliable operation with dynamic content. This backlog prioritizes fixes and improvements to create a robust, efficient rendering system.

## Critical Issues Identified

### 1. **Incremental Refresh System Failures**
- **Issue**: Incremental refresh creates spacing issues and duplicate content
- **Root Cause**: Complex cursor positioning breaks with dynamic content changes
- **Impact**: Animation demos and interactive tests show blank spaces and duplicated elements
- **Current Workaround**: Manual screen clearing bypasses the system entirely

### 2. **Naive Delta Calculation**
- **Issue**: Current delta system uses "clear all, render all" approach
- **Root Cause**: No intelligent line-by-line diffing
- **Impact**: No performance benefit from delta system
- **Evidence**: `calculate_delta()` always clears entire previous render

### 3. **Positioning System Brittleness**
- **Issue**: Absolute terminal positioning fails when content size changes
- **Root Cause**: No position recalculation when elements show/hide
- **Impact**: Card visibility changes break subsequent element positioning
- **Evidence**: Cards showing/hiding causes layout corruption

### 4. **Status Component Replacement Issues**
- **Issue**: Order dependency between visibility changes and status updates
- **Root Cause**: `text_status()` affects rendering before visibility changes applied
- **Impact**: Tests require specific operation order to work correctly
- **Evidence**: Had to reorder hide/show operations before status calls

## Backlog Items

### HIGH PRIORITY

#### P1-001: Fix Incremental Refresh Spacing Issues
**Story**: As a developer, I want incremental refresh to work reliably with dynamic content so that animations don't have spacing issues.

**Acceptance Criteria**:
- [ ] Incremental refresh handles card show/hide without spacing issues
- [ ] No duplicate content during transitions
- [ ] Page header remains consistent during updates
- [ ] Animation demos work with incremental refresh enabled

**Technical Details**:
- Review `_move_cursor_up()` and `_clear_line()` logic
- Fix line count tracking with dynamic content
- Add robust position validation
- Test with card visibility changes

**Estimated Effort**: 5 story points

#### P1-002: Intelligent Delta Calculation
**Story**: As a developer, I want the delta system to efficiently calculate actual line differences so that only changed content is re-rendered.

**Acceptance Criteria**:
- [ ] Line-by-line comparison to identify actual changes
- [ ] Only update lines that actually changed
- [ ] Handle content size changes gracefully
- [ ] Maintain performance benefits over full refresh

**Technical Implementation**:
```python
def calculate_delta(self) -> RenderDelta:
    current = self.get_render_lines()
    previous = self._last_rendered_lines
    
    # Find actual differences
    lines_to_update = []
    for i, (old, new) in enumerate(zip(previous, current)):
        if old != new:
            lines_to_update.append((i, new))
    
    # Handle size changes
    if len(current) > len(previous):
        lines_to_add = current[len(previous):]
    elif len(current) < len(previous):
        lines_to_clear = len(previous) - len(current)
        
    return RenderDelta(
        lines_to_clear=lines_to_clear,
        lines_to_add=lines_to_add,
        lines_to_update=lines_to_update
    )
```

**Estimated Effort**: 8 story points

#### P1-003: Robust Position Management
**Story**: As a developer, I want element positioning to be recalculated when content changes so that layout remains correct.

**Acceptance Criteria**:
- [ ] Position tracking survives element size changes
- [ ] Container hierarchy maintains correct child positions
- [ ] Graceful fallback to full refresh when positioning becomes complex
- [ ] Performance monitoring for position recalculation overhead

**Technical Details**:
- Implement virtual layout manager
- Track element positions in screen buffer
- Detect when incremental update is more expensive than full refresh
- Add position validation and debugging

**Estimated Effort**: 13 story points

### MEDIUM PRIORITY

#### P2-001: Status Component Order Independence
**Story**: As a developer, I want status updates to work regardless of when visibility changes occur so that I don't need to worry about operation order.

**Acceptance Criteria**:
- [ ] Status updates work before or after visibility changes
- [ ] No duplicate rendering when combining operations
- [ ] Consistent behavior across all test scenarios

**Technical Details**:
- Decouple status replacement from immediate rendering
- Batch visibility and status changes
- Apply changes in optimal order automatically

**Estimated Effort**: 5 story points

#### P2-002: Animation Framework
**Story**: As a developer, I want a proper animation framework so that I don't need manual screen clearing for smooth transitions.

**Acceptance Criteria**:
- [ ] Built-in animation support with frame management
- [ ] Configurable frame rate and timing
- [ ] Automatic header preservation during animations
- [ ] Support for different animation types (fade, slide, etc.)

**Technical Details**:
- Create `AnimationManager` class
- Integrate with delta system for efficient updates
- Provide high-level animation API
- Support both automatic and manual frame control

**Estimated Effort**: 8 story points

#### P2-003: Rendering Performance Monitoring
**Story**: As a developer, I want to monitor rendering performance so that I can identify bottlenecks and validate optimizations.

**Acceptance Criteria**:
- [ ] Track rendering times for delta vs full refresh
- [ ] Monitor line-level update counts
- [ ] Provide debugging output for rendering decisions
- [ ] Performance regression testing

**Technical Details**:
- Add timing instrumentation to render methods
- Create performance analysis tools
- Implement configurable debug output
- Add benchmark suite for rendering scenarios

**Estimated Effort**: 5 story points

### LOW PRIORITY

#### P3-001: Advanced Delta Features
**Story**: As a developer, I want advanced delta features like partial line updates so that rendering is even more efficient.

**Acceptance Criteria**:
- [ ] Partial line updates for small changes
- [ ] Color and style change detection
- [ ] Optimize common patterns (status updates, progress bars)

**Estimated Effort**: 8 story points

#### P3-002: Layout Optimization
**Story**: As a developer, I want optimized layout algorithms so that complex UIs render efficiently.

**Acceptance Criteria**:
- [ ] Intelligent layout caching
- [ ] Minimize layout recalculations
- [ ] Support for layout constraints and flexbox-like behavior

**Estimated Effort**: 13 story points

## Technical Debt

### TD-001: Remove Manual Screen Clearing Workarounds
**Description**: Once incremental refresh is fixed, remove manual `os.system('clear')` calls from demos.

**Files to Update**:
- `card_shuffling_test.py` - Remove manual clearing in animation demo
- `card_shuffling_test.py` - Remove manual clearing in quick test
- Consider removing `clear_content_area()` helper function

**Estimated Effort**: 2 story points

### TD-002: Unify Rendering Interfaces
**Description**: Consolidate different rendering approaches into consistent interface.

**Current Issues**:
- Mix of `refresh()`, `render_delta()`, and manual rendering
- Inconsistent header management
- Multiple ways to achieve same result

**Estimated Effort**: 5 story points

## Testing Requirements

### Test Coverage Needed
- [ ] Unit tests for delta calculation with various content changes
- [ ] Integration tests for incremental refresh scenarios
- [ ] Performance tests comparing delta vs full refresh
- [ ] Regression tests for card visibility edge cases
- [ ] Animation smoothness validation tests

### Test Scenarios
1. **Dynamic Content Changes**: Cards showing/hiding in various combinations
2. **Status Updates**: Status replacement during content changes
3. **Performance Boundaries**: When to fallback to full refresh
4. **Edge Cases**: Empty content, very long content, rapid changes
5. **Animation Stress**: Rapid successive frame updates

## Success Metrics

1. **Reliability**: 0 rendering artifacts in demo suite
2. **Performance**: 50% reduction in screen updates for typical scenarios
3. **Developer Experience**: No operation order dependencies
4. **Maintainability**: Unified rendering approach across codebase

## Implementation Priority

**Sprint 1**: P1-001 (Incremental Refresh) + P2-001 (Status Order)
**Sprint 2**: P1-002 (Delta Calculation) + TD-001 (Remove Workarounds)
**Sprint 3**: P1-003 (Position Management) + P2-003 (Performance Monitoring)
**Sprint 4**: P2-002 (Animation Framework) + TD-002 (Unify Interfaces)

## Risk Assessment

**High Risk**: P1-003 (Position Management) - Complex architectural changes
**Medium Risk**: P1-002 (Delta Calculation) - Performance implications
**Low Risk**: P2-001 (Status Order) - Isolated behavioral changes

## Notes

- Current manual clearing approach works well for demos but doesn't scale
- Delta system architecture is sound, implementation needs refinement
- Consider progressive enhancement: start with reliability, then optimize
- Animation framework could become foundation for future UI components