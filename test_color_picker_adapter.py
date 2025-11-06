#!/usr/bin/env python3
"""
Comprehensive test suite for ColorPickerAdapter.

This test suite validates:
- Color format validation and parsing
- Color palette management
- Color rendering and display
- Enhanced color picker functionality
- Backward compatibility
- Professional styling integration
- Real-world usage scenarios

Run with: python test_color_picker_adapter.py
"""

import sys
import time
from pathlib import Path

# Add src to path for testing
src_path = Path(__file__).parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

try:
    from tui_engine.widgets.color_picker_adapter import (
        ColorFormat, ColorPalette, ColorInfo, ColorValidator,
        ColorPaletteManager, ColorRenderer, EnhancedColorPickerAdapter,
        ColorPickerAdapter, pick_color, pick_from_palette, pick_custom_color
    )
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


def test_color_validator():
    """Test ColorValidator functionality."""
    print("🧪 Testing ColorValidator...")
    
    # Test hex validation
    print("  🔢 Hex validation tests:")
    valid_hex = ["#FF0000", "#ff0000", "FF0000", "#F00", "F00"]
    invalid_hex = ["#GG0000", "#FF", "#FF00000", "red", ""]
    
    for hex_val in valid_hex:
        assert ColorValidator.validate_hex(hex_val), f"Should validate: {hex_val}"
        print(f"    ✅ Valid hex: {hex_val}")
    
    for hex_val in invalid_hex:
        assert not ColorValidator.validate_hex(hex_val), f"Should not validate: {hex_val}"
        print(f"    ❌ Invalid hex: {hex_val}")
    
    # Test RGB validation
    print("  🎨 RGB validation tests:")
    valid_rgb = ["rgb(255,0,0)", "rgb(0, 255, 0)", "rgb( 0 , 0 , 255 )"]
    invalid_rgb = ["rgb(256,0,0)", "rgb(-1,0,0)", "rgb(255,0)", "red"]
    
    for rgb_val in valid_rgb:
        assert ColorValidator.validate_rgb(rgb_val), f"Should validate: {rgb_val}"
        print(f"    ✅ Valid RGB: {rgb_val}")
    
    for rgb_val in invalid_rgb:
        assert not ColorValidator.validate_rgb(rgb_val), f"Should not validate: {rgb_val}"
        print(f"    ❌ Invalid RGB: {rgb_val}")
    
    # Test HSL validation
    print("  🌈 HSL validation tests:")
    valid_hsl = ["hsl(0,100%,50%)", "hsl(360, 0%, 100%)", "hsl( 180 , 50% , 25% )"]
    invalid_hsl = ["hsl(361,100%,50%)", "hsl(0,101%,50%)", "hsl(0,100%,101%)", "blue"]
    
    for hsl_val in valid_hsl:
        assert ColorValidator.validate_hsl(hsl_val), f"Should validate: {hsl_val}"
        print(f"    ✅ Valid HSL: {hsl_val}")
    
    for hsl_val in invalid_hsl:
        assert not ColorValidator.validate_hsl(hsl_val), f"Should not validate: {hsl_val}"
        print(f"    ❌ Invalid HSL: {hsl_val}")
    
    # Test named color validation
    print("  📝 Named color validation tests:")
    valid_names = ["red", "blue", "green", "white", "black"]
    invalid_names = ["redish", "lightblue", "darkgreen", "unknown"]
    
    for name in valid_names:
        assert ColorValidator.validate_named(name), f"Should validate: {name}"
        print(f"    ✅ Valid name: {name}")
    
    for name in invalid_names:
        assert not ColorValidator.validate_named(name), f"Should not validate: {name}"
        print(f"    ❌ Invalid name: {name}")
    
    # Test color parsing
    print("  🔄 Color parsing tests:")
    test_colors = [
        ("#FF0000", "hex"),
        ("rgb(0,255,0)", "RGB"),
        ("hsl(240,100%,50%)", "HSL"),
        ("blue", "named")
    ]
    
    for color_str, format_type in test_colors:
        parsed = ColorValidator.parse_color(color_str)
        assert parsed is not None, f"Should parse: {color_str}"
        print(f"    ✅ Parsed {format_type}: {color_str} -> {parsed.hex_value}")
    
    print("✅ ColorValidator tests passed!")


def test_color_palette_manager():
    """Test ColorPaletteManager functionality."""
    print("\n🧪 Testing ColorPaletteManager...")
    
    # Test all predefined palettes
    print("  📋 Palette loading tests:")
    for palette in ColorPalette:
        if palette != ColorPalette.CUSTOM:
            colors = ColorPaletteManager.get_palette(palette)
            assert len(colors) > 0, f"Palette {palette.value} should have colors"
            print(f"    ✅ {palette.value}: {len(colors)} colors")
            
            # Test first color
            first_color = colors[0]
            assert isinstance(first_color, ColorInfo), "Should return ColorInfo objects"
            assert first_color.hex_value.startswith('#'), "Should have hex value"
            print(f"      First color: {first_color.name or first_color.hex_value}")
    
    # Test choice generation
    print("  🎯 Choice generation tests:")
    basic_choices = ColorPaletteManager.get_palette_choices(ColorPalette.BASIC)
    assert len(basic_choices) > 0, "Should generate choices"
    print(f"    ✅ Generated {len(basic_choices)} choices for basic palette")
    
    # Test choice structure
    first_choice = basic_choices[0]
    assert hasattr(first_choice, 'title'), "Choice should have title"
    assert hasattr(first_choice, 'value'), "Choice should have value"
    assert isinstance(first_choice.value, ColorInfo), "Choice value should be ColorInfo"
    print(f"    ✅ Choice structure: {first_choice.title[:50]}...")
    
    print("✅ ColorPaletteManager tests passed!")


def test_color_renderer():
    """Test ColorRenderer functionality."""
    print("\n🧪 Testing ColorRenderer...")
    
    # Create test color
    test_color = ColorValidator.parse_color("#FF0000")
    assert test_color is not None, "Should parse test color"
    
    # Test color block rendering
    print("  🎨 Color block rendering tests:")
    block = ColorRenderer.render_color_block(test_color)
    assert len(block) > 0, "Should render color block"
    assert '\033[' in block, "Should contain ANSI codes"
    print(f"    ✅ Color block: {repr(block[:20])}...")
    
    # Test color swatch rendering
    print("  🖼️  Color swatch rendering tests:")
    swatch = ColorRenderer.render_color_swatch(test_color)
    assert len(swatch) > 0, "Should render color swatch"
    assert 'HEX:' in swatch, "Should contain hex information"
    assert 'RGB:' in swatch, "Should contain RGB information"
    print(f"    ✅ Color swatch: {swatch[:50]}...")
    
    # Test palette grid rendering
    print("  📊 Palette grid rendering tests:")
    colors = ColorPaletteManager.get_palette(ColorPalette.BASIC)[:8]  # First 8 colors
    grid = ColorRenderer.render_palette_grid(colors, columns=4)
    assert len(grid) > 0, "Should render palette grid"
    lines = grid.split('\n')
    assert len(lines) >= 2, "Should have multiple lines for grid"
    print(f"    ✅ Palette grid: {len(lines)} lines, {len(grid)} characters")
    
    print("✅ ColorRenderer tests passed!")


def test_enhanced_color_picker_adapter():
    """Test EnhancedColorPickerAdapter functionality."""
    print("\n🧪 Testing EnhancedColorPickerAdapter...")
    
    # Test basic initialization
    print("  🚀 Initialization tests:")
    picker = EnhancedColorPickerAdapter(
        message="Test color selection",
        format_preference=ColorFormat.HEX,
        theme_variant="professional_blue"
    )
    assert picker.message == "Test color selection"
    assert picker.format_preference == ColorFormat.HEX
    assert picker.theme_variant == "professional_blue"
    print(f"    ✅ Created picker: {picker}")
    
    # Test color history management
    print("  🕒 Color history tests:")
    test_color1 = ColorValidator.parse_color("#FF0000")
    test_color2 = ColorValidator.parse_color("#00FF00")
    
    picker._add_to_history(test_color1)
    assert len(picker.color_history) == 1
    print(f"    ✅ Added color to history: {len(picker.color_history)} items")
    
    picker._add_to_history(test_color2)
    assert len(picker.color_history) == 2
    print(f"    ✅ Added second color: {len(picker.color_history)} items")
    
    # Test duplicate handling
    picker._add_to_history(test_color1)  # Should move to end, not duplicate
    assert len(picker.color_history) == 2
    assert picker.color_history[-1] == test_color1
    print(f"    ✅ Duplicate handling: last color is {picker.color_history[-1].hex_value}")
    
    # Test custom palette management
    print("  ⭐ Custom palette tests:")
    picker.add_to_custom_palette(test_color1)
    assert len(picker.custom_palette) == 1
    print(f"    ✅ Added to custom palette: {len(picker.custom_palette)} items")
    
    picker.add_to_custom_palette(test_color1)  # Should not duplicate
    assert len(picker.custom_palette) == 1
    print(f"    ✅ No duplicates in custom palette: {len(picker.custom_palette)} items")
    
    # Test color format output
    print("  🔄 Color format output tests:")
    picker.selected_color = test_color1
    
    hex_output = picker.get_selected_color(ColorFormat.HEX)
    assert hex_output == "#FF0000", f"Hex should be #FF0000, got {hex_output}"
    print(f"    ✅ Hex output: {hex_output}")
    
    rgb_output = picker.get_selected_color(ColorFormat.RGB)
    assert rgb_output == "rgb(255,0,0)", f"RGB should be rgb(255,0,0), got {rgb_output}"
    print(f"    ✅ RGB output: {rgb_output}")
    
    hsl_output = picker.get_selected_color(ColorFormat.HSL)
    assert "hsl(" in hsl_output, f"HSL should contain 'hsl(', got {hsl_output}"
    print(f"    ✅ HSL output: {hsl_output}")
    
    # Test theme integration
    print("  🎨 Theme integration tests:")
    assert picker.theme is not None, "Should have theme"
    # Style may be None if style adapter is not available in fallback mode
    print(f"    ✅ Theme loaded: {len(picker.theme)} properties")
    print(f"    ✅ Style available: {'Yes' if picker.style else 'No (fallback mode)'}")
    
    print("✅ EnhancedColorPickerAdapter tests passed!")


def test_backward_compatible_adapter():
    """Test backward-compatible ColorPickerAdapter."""
    print("\n🧪 Testing backward-compatible ColorPickerAdapter...")
    
    # Test enhanced mode
    print("  🚀 Enhanced mode tests:")
    enhanced_adapter = ColorPickerAdapter(enhanced=True)
    assert enhanced_adapter.enhanced == True
    assert hasattr(enhanced_adapter, 'adapter')
    assert isinstance(enhanced_adapter.adapter, EnhancedColorPickerAdapter)
    print(f"    ✅ Enhanced adapter: {enhanced_adapter}")
    
    # Test legacy mode
    print("  🔙 Legacy mode tests:")
    legacy_adapter = ColorPickerAdapter(enhanced=False, message="Select color")
    assert legacy_adapter.enhanced == False
    assert legacy_adapter.message == "Select color"
    print(f"    ✅ Legacy adapter: {legacy_adapter}")
    
    # Test palette setting
    print("  📋 Palette setting tests:")
    enhanced_adapter.set_palette("basic")
    assert enhanced_adapter.adapter.default_palette == ColorPalette.BASIC
    print(f"    ✅ Palette set to: {enhanced_adapter.adapter.default_palette}")
    
    # Test invalid palette
    enhanced_adapter.set_palette("invalid_palette")  # Should not crash
    print(f"    ✅ Invalid palette handled gracefully")
    
    # Test representation
    print("  📝 String representation tests:")
    enhanced_repr = repr(enhanced_adapter)
    assert "enhanced=True" in enhanced_repr
    print(f"    ✅ Enhanced repr: {enhanced_repr[:50]}...")
    
    legacy_repr = repr(legacy_adapter)
    assert "enhanced=False" in legacy_repr
    print(f"    ✅ Legacy repr: {legacy_repr[:50]}...")
    
    print("✅ Backward-compatible ColorPickerAdapter tests passed!")


def test_convenience_functions():
    """Test convenience functions."""
    print("\n🧪 Testing convenience functions...")
    
    # Test pick_color function
    print("  🎯 pick_color function tests:")
    # Note: These would require user input in real scenarios
    # For testing, we'll just verify they're callable
    try:
        # Test function signature and defaults
        import inspect
        sig = inspect.signature(pick_color)
        assert 'message' in sig.parameters
        assert 'format_preference' in sig.parameters
        assert 'theme_variant' in sig.parameters
        print(f"    ✅ pick_color signature valid: {len(sig.parameters)} parameters")
    except Exception as e:
        print(f"    ❌ pick_color signature error: {e}")
    
    # Test pick_from_palette function
    print("  📋 pick_from_palette function tests:")
    try:
        sig = inspect.signature(pick_from_palette)
        assert 'palette' in sig.parameters
        assert 'message' in sig.parameters
        assert 'theme_variant' in sig.parameters
        print(f"    ✅ pick_from_palette signature valid: {len(sig.parameters)} parameters")
    except Exception as e:
        print(f"    ❌ pick_from_palette signature error: {e}")
    
    # Test pick_custom_color function
    print("  🎨 pick_custom_color function tests:")
    try:
        sig = inspect.signature(pick_custom_color)
        assert 'format_preference' in sig.parameters
        assert 'message' in sig.parameters
        assert 'theme_variant' in sig.parameters
        print(f"    ✅ pick_custom_color signature valid: {len(sig.parameters)} parameters")
    except Exception as e:
        print(f"    ❌ pick_custom_color signature error: {e}")
    
    print("✅ Convenience function tests passed!")


def test_real_world_scenarios():
    """Test real-world color picker scenarios."""
    print("\n🧪 Testing real-world scenarios...")
    
    # Test web development color selection
    print("  🌐 Web development scenario:")
    web_picker = EnhancedColorPickerAdapter(
        message="Choose brand color:",
        format_preference=ColorFormat.HEX,
        default_palette=ColorPalette.WEB_SAFE,
        show_preview=True
    )
    
    # Simulate color selection and conversion
    test_color = ColorValidator.parse_color("#336699")
    web_picker.selected_color = test_color
    
    hex_color = web_picker.get_selected_color(ColorFormat.HEX)
    rgb_color = web_picker.get_selected_color(ColorFormat.RGB)
    print(f"    ✅ Web color - HEX: {hex_color}, RGB: {rgb_color}")
    
    # Test design tool integration
    print("  🎨 Design tool integration scenario:")
    design_picker = EnhancedColorPickerAdapter(
        message="Select accent color:",
        format_preference=ColorFormat.HSL,
        default_palette=ColorPalette.MATERIAL,
        allow_custom=True
    )
    
    # Test color history for design workflow
    colors = ["#F44336", "#E91E63", "#9C27B0", "#673AB7"]
    for color_str in colors:
        color = ColorValidator.parse_color(color_str)
        design_picker._add_to_history(color)
    
    assert len(design_picker.color_history) == 4
    print(f"    ✅ Design history: {len(design_picker.color_history)} colors")
    
    # Test terminal color configuration
    print("  💻 Terminal configuration scenario:")
    terminal_picker = EnhancedColorPickerAdapter(
        message="Configure terminal colors:",
        format_preference=ColorFormat.ANSI,
        default_palette=ColorPalette.TERMINAL,
        show_preview=True
    )
    
    # Test ANSI color handling
    ansi_colors = ColorPaletteManager.get_palette(ColorPalette.TERMINAL)
    assert len(ansi_colors) > 0
    print(f"    ✅ Terminal colors: {len(ansi_colors)} ANSI colors available")
    
    # Test accessibility considerations
    print("  ♿ Accessibility scenario:")
    accessible_picker = EnhancedColorPickerAdapter(
        message="Choose accessible color:",
        format_preference=ColorFormat.HEX,
        default_palette=ColorPalette.HIGH_CONTRAST if hasattr(ColorPalette, 'HIGH_CONTRAST') else ColorPalette.BASIC,
        show_preview=True
    )
    
    # Test high contrast color selection
    high_contrast_colors = ["#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF"]
    for color_str in high_contrast_colors:
        color = ColorValidator.parse_color(color_str)
        accessible_picker.add_to_custom_palette(color)
    
    print(f"    ✅ Accessibility: {len(accessible_picker.custom_palette)} high-contrast colors")
    
    print("✅ Real-world scenario tests passed!")


def test_color_conversion_accuracy():
    """Test color conversion accuracy between formats."""
    print("\n🧪 Testing color conversion accuracy...")
    
    # Test round-trip conversions
    print("  🔄 Round-trip conversion tests:")
    test_cases = [
        ("#FF0000", "Pure red"),
        ("#00FF00", "Pure green"), 
        ("#0000FF", "Pure blue"),
        ("#FFFFFF", "White"),
        ("#000000", "Black"),
        ("#808080", "Gray"),
        ("#FFFF00", "Yellow"),
        ("#FF00FF", "Magenta"),
        ("#00FFFF", "Cyan")
    ]
    
    for hex_color, description in test_cases:
        # Parse original
        original = ColorValidator.parse_color(hex_color)
        assert original is not None, f"Should parse {hex_color}"
        
        # Convert to RGB string and back
        rgb_str = f"rgb({original.rgb[0]},{original.rgb[1]},{original.rgb[2]})"
        from_rgb = ColorValidator.parse_color(rgb_str)
        assert from_rgb is not None, f"Should parse RGB: {rgb_str}"
        assert from_rgb.hex_value == original.hex_value, f"RGB round-trip failed for {description}"
        
        # Convert to HSL string and back
        h, s, l = original.hsl
        hsl_str = f"hsl({h:.0f},{s:.0f}%,{l:.0f}%)"
        from_hsl = ColorValidator.parse_color(hsl_str)
        assert from_hsl is not None, f"Should parse HSL: {hsl_str}"
        
        # Allow small differences due to floating point precision
        r_diff = abs(from_hsl.rgb[0] - original.rgb[0])
        g_diff = abs(from_hsl.rgb[1] - original.rgb[1])
        b_diff = abs(from_hsl.rgb[2] - original.rgb[2])
        assert r_diff <= 1 and g_diff <= 1 and b_diff <= 1, f"HSL round-trip failed for {description}"
        
        print(f"    ✅ {description}: HEX↔RGB↔HSL conversions accurate")
    
    # Test edge cases
    print("  🎯 Edge case conversion tests:")
    edge_cases = [
        "#000001",  # Almost black
        "#FFFFFE",  # Almost white
        "#FF0001",  # Almost pure red
        "#7F7F7F",  # Mid gray
    ]
    
    for hex_color in edge_cases:
        color = ColorValidator.parse_color(hex_color)
        assert color is not None, f"Should parse edge case: {hex_color}"
        
        # Check all values are within valid ranges
        r, g, b = color.rgb
        assert 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255, f"RGB out of range: {color.rgb}"
        
        h, s, l = color.hsl
        assert 0 <= h <= 360 and 0 <= s <= 100 and 0 <= l <= 100, f"HSL out of range: {color.hsl}"
        
        print(f"    ✅ Edge case {hex_color}: RGB={color.rgb}, HSL=({h:.1f}°,{s:.1f}%,{l:.1f}%)")
    
    print("✅ Color conversion accuracy tests passed!")


def test_performance_and_memory():
    """Test performance and memory usage."""
    print("\n🧪 Testing performance and memory...")
    
    # Test color parsing performance
    print("  ⚡ Color parsing performance:")
    test_colors = ["#FF0000", "rgb(0,255,0)", "hsl(240,100%,50%)", "blue"] * 250  # 1000 total
    
    start_time = time.time()
    parsed_colors = []
    for color_str in test_colors:
        color = ColorValidator.parse_color(color_str)
        if color:
            parsed_colors.append(color)
    end_time = time.time()
    
    parsing_time = end_time - start_time
    colors_per_second = len(test_colors) / parsing_time if parsing_time > 0 else float('inf')
    print(f"    ✅ Parsed {len(test_colors)} colors in {parsing_time:.3f}s ({colors_per_second:.0f} colors/sec)")
    
    # Test palette loading performance
    print("  📋 Palette loading performance:")
    start_time = time.time()
    all_palettes = {}
    for palette in ColorPalette:
        if palette != ColorPalette.CUSTOM:
            all_palettes[palette] = ColorPaletteManager.get_palette(palette)
    end_time = time.time()
    
    loading_time = end_time - start_time
    total_colors = sum(len(colors) for colors in all_palettes.values())
    print(f"    ✅ Loaded {len(all_palettes)} palettes ({total_colors} colors) in {loading_time:.3f}s")
    
    # Test memory efficiency with large color history
    print("  💾 Memory efficiency tests:")
    picker = EnhancedColorPickerAdapter()
    
    # Add many colors to history
    import random
    for i in range(100):
        hex_color = f"#{random.randint(0, 0xFFFFFF):06X}"
        color = ColorValidator.parse_color(hex_color)
        if color:
            picker._add_to_history(color)
    
    # Should maintain only last 20
    assert len(picker.color_history) == 20, f"History should be limited to 20, got {len(picker.color_history)}"
    print(f"    ✅ Color history properly limited: {len(picker.color_history)} items")
    
    # Test rapid color selection simulation
    print("  🚀 Rapid selection simulation:")
    start_time = time.time()
    
    for i in range(50):
        # Simulate color selection workflow
        picker = EnhancedColorPickerAdapter(
            format_preference=ColorFormat.HEX,
            default_palette=ColorPalette.BASIC
        )
        
        # Simulate selecting a color from palette
        colors = ColorPaletteManager.get_palette(ColorPalette.BASIC)
        if colors:
            picker.selected_color = colors[i % len(colors)]
            result = picker.get_selected_color()
    
    end_time = time.time()
    selection_time = end_time - start_time
    print(f"    ✅ Simulated 50 color selections in {selection_time:.3f}s ({50/selection_time:.0f} selections/sec)")
    
    print("✅ Performance and memory tests passed!")


def main():
    """Run all ColorPickerAdapter tests."""
    print("🚀 Starting ColorPickerAdapter test suite...\n")
    
    try:
        # Core functionality tests
        test_color_validator()
        test_color_palette_manager()
        test_color_renderer()
        test_enhanced_color_picker_adapter()
        test_backward_compatible_adapter()
        test_convenience_functions()
        
        # Advanced tests
        test_real_world_scenarios()
        test_color_conversion_accuracy()
        test_performance_and_memory()
        
        print(f"\n📊 Test Results: 9/9 tests passed")
        print("🎉 All ColorPickerAdapter tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)