# Card Shuffling Navigation Demo

This demo showcases the **proper TUI engine architecture** with universal visibility system and central screen management through `Page.refresh()`.

## 🏗️ **TUI Engine Architecture**

### **Hierarchical Structure**
```
Page (Top-level container)
├── Card (Visual grouping) 
│   └── Assembly (Interactive component groups)
│       └── Component (questionary elements)
└── Assembly (Direct page assemblies - not in cards)
    └── Component (questionary elements)
```

### **Universal Visibility System**
- **All elements** (Page, Card, Assembly, Component) have `visible` property
- **Show/Hide methods**: `.show()` and `.hide()` on all elements
- **State-driven display**: Only visible elements are rendered
- **Central management**: `Page.refresh()` handles all screen updates

### **Key Features**
- **Mixed placement**: Assemblies can be in Cards OR directly on Page
- **Automatic screen management**: Page clears screen and reprints visible elements in order
- **Event-driven navigation**: Page Up/Down changes visibility state, triggers refresh
- **Consistent API**: All elements follow same visibility patterns

## 📁 **Demo Files**

### **`proper_card_demo.py`** ⭐ **RECOMMENDED**
The correct implementation using TUI engine architecture:
- **Proper structure**: Page → Cards → Assemblies → Components
- **Visibility management**: Uses `.show()/.hide()` methods
- **Central refresh**: `page.refresh()` handles all screen updates
- **State-driven navigation**: Page Up/Down changes Card visibility

### **`architecture_demo.py`**
Comprehensive architecture demonstration:
- **Mixed structure**: Shows Cards with Assemblies + Page-level Assemblies
- **Multiple views**: Navigate between different visibility configurations
- **Educational**: Shows how universal visibility system works

### **`test_refresh.py`**
Simple test demonstrating the refresh architecture:
- **Validation**: Tests visibility and refresh functionality
- **Step-by-step**: Shows elements being hidden/shown with refresh

### **Legacy Demos** (Pre-Architecture)
- **`pagekey_demo.py`**: Direct key capture without TUI engine
- **`card_shuffling_demo.py`**: Enhanced but bypasses architecture  
- **`simple_demo.py`**: Original prompt-based navigation

## 🚀 **Usage**

### **Proper Architecture Demo** (Recommended)
```bash
cd examples/card_shuffling_navigation
python3 proper_card_demo.py
```

**Controls:**
- **Page Up**: Previous card (changes visibility + refresh)
- **Page Down**: Next card (changes visibility + refresh)
- **1-5**: Jump directly to specific card
- **R**: Run current card (demo assembly structure)
- **A**: Show all cards (architecture overview)
- **Q**: Quit demo

### **Architecture Overview Demo**
```bash
python3 architecture_demo.py
```

**Features:**
- Navigate between 6 different visibility configurations
- See how mixed Page/Card/Assembly structure works
- Understand universal visibility system

### **Simple Refresh Test**
```bash
python3 test_refresh.py
```

**Output:** Shows step-by-step visibility changes with refresh

## 🏗️ **Architecture Implementation**

### **Page.refresh() Method**
```python
def refresh(self) -> None:
    """Clear screen and reprint all visible elements in order."""
    self.clear_screen()
    self._render_header()
    
    for component in self.components:
        self._render_component(component)
```

### **Universal Visibility**
```python
# All elements have these methods:
element.show()    # Make visible
element.hide()    # Make invisible
element.visible   # Boolean property

# Page renders only visible elements:
visible = getattr(component, 'visible', True)
if not visible:
    return  # Skip rendering
```

### **State-Driven Navigation**
```python
# Change visibility state
cards[current_index].show()
cards[other_indices].hide()

# Trigger centralized refresh
page.refresh()  # Automatic screen clear + reprint
```

## 🎯 **Design Benefits**

1. **Separation of Concerns**: Navigation logic separate from display logic
2. **Consistent Rendering**: All screen updates go through same path
3. **Universal Patterns**: Same visibility API for all element types
4. **Flexible Structure**: Assemblies can be in Cards or directly on Page
5. **Event-Driven**: Changes trigger automatic refresh, no manual screen management

## 🔧 **Architecture Elements**

### **Page Management**
- **Container**: Top-level organization
- **State**: Central state management with assembly namespacing  
- **Refresh**: Centralized screen clearing and reprinting
- **Navigation**: Visibility coordination

### **Card Organization**  
- **Visual grouping**: Related assemblies together
- **Styling**: Multiple visual styles (minimal, bordered, highlighted)
- **Visibility**: Can be shown/hidden as units

### **Assembly Logic**
- **Component groups**: Interactive element collections
- **Namespacing**: State isolation with `assembly.field` keys
- **Placement flexibility**: In Cards OR directly on Page

### **Component Interface**
- **Questionary compatibility**: Full backward compatibility
- **Enhanced features**: Conditional visibility, validation
- **Universal visibility**: Same show/hide API as containers

## 🚀 **Next Steps**

This architecture sets the foundation for:
- **Event system**: Real-time component interactions
- **State-driven updates**: Automatic visibility based on data
- **Complex wizards**: Multi-page workflows with proper navigation
- **Enhanced validation**: Cross-component validation with visual feedback

The universal visibility system and central refresh method provide the core infrastructure for sophisticated TUI applications while maintaining clean separation of concerns.