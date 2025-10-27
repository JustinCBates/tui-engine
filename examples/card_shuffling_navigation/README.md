# Card Shuffling Navigation Demo

This demo showcases a single page with 5 cards where only one is visible at a time.

## Features

- 🎴 **Card Navigation**: Navigate between 5 different cards
- ⌨️ **Keyboard Controls**: Use Page Up/Down or numeric keys 1-5
- 📝 **Descriptive Content**: Each card has explanatory text
- 🔢 **Integer Inputs**: Simple integer prompts in each card's assembly
- 🎯 **Visual Feedback**: Clear indication of current card

## How to Run

```bash
cd examples/card_shuffling_navigation
python card_shuffling_demo.py
```

## Navigation Controls

- **N** - Next card (equivalent to Page Down)
- **P** - Previous card (equivalent to Page Up) 
- **1-5** - Jump directly to specific card
- **R** - Run/execute current card's assembly
- **Q** - Quit the demo

## Card Themes

1. 🏠 **Personal Information** - Basic personal details
2. 💼 **Professional Details** - Work experience information  
3. 🎓 **Education Level** - Educational background
4. 🌟 **Preferences** - Personal preferences and ratings
5. 🎯 **Goals & Targets** - Objectives and targets

## Architecture

This demo demonstrates:
- Single `Page` with multiple `Card` components
- Each card contains an `Assembly` with integer input
- Card visibility management (show/hide)
- Navigation state management
- User input handling and validation

The demo uses the TUI engine's clean architectural separation with `Page`, `Card`, and `Assembly` components working together to create an interactive card-based interface.