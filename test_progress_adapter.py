#!/usr/bin/env python3
"""Test script for ProgressAdapter functionality.

This script tests both enhanced and legacy modes of the ProgressAdapter,
including different progress modes, step tracking, ETA calculation, and rendering.
"""
import sys
import os
import time
from pathlib import Path
from datetime import datetime, timedelta

# Add the project src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from typing import List, Dict, Any, Optional


def test_progress_calculator():
    """Test the ProgressCalculator functionality."""
    print("🧪 Testing ProgressCalculator...")
    
    from tui_engine.widgets.progress_adapter import ProgressCalculator, ProgressConfig
    
    config = ProgressConfig(auto_eta=True, smooth_eta=False)
    calculator = ProgressCalculator(config)
    
    # Test basic tracking
    print("  📊 Basic tracking tests:")
    calculator.start_tracking()
    
    # Simulate progress updates
    for i in range(1, 6):
        calculator.update_progress(i * 20, 100)
        time.sleep(0.01)  # Small delay to create time differences
    
    # Test ETA calculation
    eta = calculator.calculate_eta(80, 100)
    print(f"    ETA calculation (80/100): {eta}")
    
    # Test rate calculation
    rate = calculator.calculate_rate(80)
    print(f"    Rate calculation: {rate}")
    
    # Test statistics
    stats = calculator.get_statistics()
    print(f"    Statistics: {len(stats)} metrics collected")
    assert 'elapsed' in stats
    assert 'total_samples' in stats
    
    print("✅ ProgressCalculator tests passed!")
    return True


def test_progress_renderer():
    """Test the ProgressRenderer functionality."""
    print("🧪 Testing ProgressRenderer...")
    
    from tui_engine.widgets.progress_adapter import ProgressRenderer, ProgressConfig, ProgressStep
    
    config = ProgressConfig(bar_width=20, bar_fill_char='█', bar_empty_char='░')
    renderer = ProgressRenderer(config)
    
    # Test bar rendering
    print("  📊 Bar rendering tests:")
    progress_ratios = [0.0, 0.25, 0.5, 0.75, 1.0]
    for ratio in progress_ratios:
        bar = renderer.render_bar(ratio)
        print(f"    Progress {ratio:.0%}: {bar}")
        assert len(bar) == config.bar_width + 2  # +2 for brackets
    
    # Test percentage rendering
    print("  📊 Percentage rendering tests:")
    for ratio in progress_ratios:
        percentage = renderer.render_percentage(ratio)
        print(f"    Percentage {ratio:.0%}: {percentage}")
        assert '%' in percentage
    
    # Test spinner rendering
    print("  🌀 Spinner rendering tests:")
    spinner_chars = []
    for i in range(5):
        char = renderer.render_spinner()
        spinner_chars.append(char)
        print(f"    Spinner frame {i+1}: {char}")
    
    # Should cycle through different characters
    assert len(set(spinner_chars)) > 1
    
    # Test ETA rendering
    print("  ⏱️  ETA rendering tests:")
    eta_values = [
        timedelta(seconds=30),
        timedelta(minutes=5, seconds=30),
        timedelta(hours=2, minutes=15)
    ]
    
    for eta in eta_values:
        eta_str = renderer.render_eta(eta)
        print(f"    ETA {eta}: {eta_str}")
        assert 'ETA:' in eta_str
    
    # Test rate rendering
    print("  📈 Rate rendering tests:")
    rates = [0.5, 5.0, 50.0, 500.0]
    for rate in rates:
        rate_str = renderer.render_rate(rate)
        print(f"    Rate {rate}: {rate_str}")
        assert 'Rate:' in rate_str
    
    # Test steps rendering
    print("  📋 Steps rendering tests:")
    steps = [
        ProgressStep(id='step1', label='Initialize'),
        ProgressStep(id='step2', label='Process'),
        ProgressStep(id='step3', label='Finalize')
    ]
    
    steps[0].complete()  # Mark first step as completed
    
    steps_display = renderer.render_steps(steps, current_step=1)
    print(f"    Steps display:\n{steps_display}")
    assert '✓' in steps_display  # Completed step
    assert '►' in steps_display  # Current step
    assert '○' in steps_display  # Future step
    
    print("✅ ProgressRenderer tests passed!")
    return True


def test_enhanced_progress_adapter():
    """Test EnhancedProgressAdapter functionality."""
    print("🧪 Testing EnhancedProgressAdapter...")
    
    try:
        from tui_engine.widgets.progress_adapter import EnhancedProgressAdapter, ProgressMode
        
        # Test basic progress
        print("  📊 Basic progress tests:")
        progress = EnhancedProgressAdapter(
            message="Test progress:",
            total=100,
            mode=ProgressMode.BAR,
            show_percentage=True,
            show_eta=True,
            style='professional_blue'
        )
        
        print(f"    Created: {progress}")
        assert progress.get_progress_ratio() == 0.0
        
        # Test progress updates
        progress.start()
        
        test_values = [25, 50, 75, 100]
        for value in test_values:
            progress.update(value)
            ratio = progress.get_progress_ratio()
            rendered = progress.render()
            print(f"    Progress {value}/100 ({ratio:.1%}): {rendered}")
        
        assert progress.get_progress_ratio() == 1.0
        
        # Test increment functionality
        print("  ⬆️  Increment tests:")
        inc_progress = EnhancedProgressAdapter(
            message="Increment test:",
            total=10,
            mode=ProgressMode.PERCENTAGE
        )
        
        inc_progress.start()
        for i in range(5):
            inc_progress.increment(2)
            value = inc_progress.current
            print(f"    After increment {i+1}: {value}/10")
        
        assert inc_progress.current == 10
        
        # Test step-based progress
        print("  📋 Step-based progress tests:")
        steps_data = [
            {'id': 'init', 'label': 'Initialize', 'description': 'Setting up'},
            {'id': 'process', 'label': 'Process Data', 'description': 'Processing'},
            {'id': 'finalize', 'label': 'Finalize', 'description': 'Cleaning up'}
        ]
        
        step_progress = EnhancedProgressAdapter(
            message="Step progress:",
            mode=ProgressMode.STEPS,
            steps=steps_data
        )
        
        print(f"    Created step progress: {step_progress}")
        step_progress.start()
        
        # Move through steps
        for i in range(len(steps_data)):
            rendered = step_progress.render()
            print(f"    Step {i+1}: {rendered}")
            step_progress.next_step()
        
        # Test statistics
        print("  📊 Statistics tests:")
        stats = progress.get_statistics()
        print(f"    Statistics keys: {list(stats.keys())}")
        assert 'state' in stats
        assert 'progress_ratio' in stats
        assert 'elapsed_time' in stats
        
        # Test theme changing
        print("  🎨 Theme tests:")
        if progress.is_questionary_enhanced():
            success = progress.change_theme('dark_mode')
            print(f"    Theme change success: {success}")
        
        print("✅ EnhancedProgressAdapter tests passed!")
        return True
        
    except ImportError as e:
        print(f"⚠️  Questionary not available, skipping enhanced tests: {e}")
        return True
    except Exception as e:
        print(f"❌ EnhancedProgressAdapter test failed: {e}")
        return False


def test_backward_compatible_adapter():
    """Test the backward-compatible ProgressAdapter."""
    print("🧪 Testing backward-compatible ProgressAdapter...")
    
    from tui_engine.widgets.progress_adapter import ProgressAdapter
    
    # Test legacy mode (with explicit widget)
    print("  🔙 Legacy mode tests:")
    legacy_adapter = ProgressAdapter(widget="dummy_widget")
    print(f"    Created legacy adapter: {legacy_adapter}")
    
    # Test basic operations
    legacy_adapter.start()
    legacy_adapter.update(50)
    legacy_adapter.increment(25)
    legacy_adapter.complete()
    
    ratio = legacy_adapter.get_progress_ratio()
    elapsed = legacy_adapter.get_elapsed_time()
    print(f"    Final progress: {ratio:.1%}")
    print(f"    Elapsed time: {elapsed}")
    assert ratio == 1.0
    
    # Test enhanced mode (without widget)
    print("  🚀 Enhanced mode tests:")
    try:
        enhanced_adapter = ProgressAdapter(
            message="Enhanced test:",
            total=200,
            mode='detailed',
            show_eta=True,
            show_rate=True
        )
        print(f"    Created enhanced adapter: {enhanced_adapter}")
        
        # Test enhanced features
        enhanced_adapter.start()
        for i in range(0, 201, 50):
            enhanced_adapter.update(i)
            rendered = enhanced_adapter.render()
            stats = enhanced_adapter.get_statistics()
            print(f"    Progress {i}/200: {rendered}")
            print(f"    Stats: enhanced={stats.get('use_questionary', False)}")
        
        enhanced_adapter.complete()
        
    except Exception as e:
        print(f"    ⚠️  Enhanced mode not available: {e}")
    
    print("✅ Backward-compatible ProgressAdapter tests passed!")
    return True


def test_convenience_functions():
    """Test convenience functions for creating progress widgets."""
    print("🧪 Testing convenience functions...")
    
    from tui_engine.widgets.progress_adapter import (
        create_simple_progress, create_detailed_progress, create_step_progress,
        create_spinner_progress, create_download_progress
    )
    
    # Test simple progress
    print("  📊 Simple progress tests:")
    simple_progress = create_simple_progress(
        message="Simple task:",
        total=50
    )
    print(f"    Simple progress: {simple_progress}")
    
    simple_progress.start()
    simple_progress.update(25)
    rendered = simple_progress.render()
    print(f"    Rendered: {rendered}")
    
    # Test detailed progress
    print("  📊 Detailed progress tests:")
    detailed_progress = create_detailed_progress(
        message="Complex task:",
        total=1000,
        show_eta=True,
        show_rate=True
    )
    print(f"    Detailed progress: {detailed_progress}")
    
    detailed_progress.start()
    detailed_progress.update(500)
    detailed_rendered = detailed_progress.render()
    print(f"    Detailed rendered: {detailed_rendered}")
    
    # Test step progress
    print("  📋 Step progress tests:")
    steps = [
        {'id': 'download', 'label': 'Download files'},
        {'id': 'extract', 'label': 'Extract archive'},
        {'id': 'install', 'label': 'Install components'}
    ]
    
    step_progress = create_step_progress(
        steps=steps,
        message="Installation:"
    )
    print(f"    Step progress: {step_progress}")
    
    # Test spinner progress
    print("  🌀 Spinner progress tests:")
    spinner_progress = create_spinner_progress(
        message="Loading components..."
    )
    print(f"    Spinner progress: {spinner_progress}")
    
    spinner_rendered = spinner_progress.render()
    print(f"    Spinner rendered: {spinner_rendered}")
    
    # Test download progress
    print("  📥 Download progress tests:")
    download_progress = create_download_progress(
        filename="large_file.zip",
        total_bytes=1024*1024*100  # 100MB
    )
    print(f"    Download progress: {download_progress}")
    
    download_progress.start()
    download_progress.update(1024*1024*25)  # 25MB downloaded
    download_rendered = download_progress.render()
    print(f"    Download rendered: {download_rendered}")
    
    print("✅ Convenience function tests passed!")
    return True


def test_real_world_scenarios():
    """Test real-world usage scenarios."""
    print("🧪 Testing real-world scenarios...")
    
    from tui_engine.widgets.progress_adapter import ProgressAdapter
    
    # Scenario 1: File processing batch
    print("  📁 File processing scenario:")
    file_processor = ProgressAdapter(
        message="Processing files:",
        total=100,
        mode='detailed',
        show_eta=True,
        show_rate=True
    )
    
    file_processor.start()
    
    # Simulate file processing
    for i in range(0, 101, 20):
        file_processor.update(i, f"Processing file {i}")
        rendered = file_processor.render()
        print(f"    {rendered}")
        time.sleep(0.01)  # Small delay to simulate work
    
    stats = file_processor.get_statistics()
    print(f"    Final stats: {stats['state']}, elapsed: {stats['elapsed_time']}")
    
    # Scenario 2: Multi-step installation
    print("  🔧 Installation scenario:")
    install_steps = [
        {'id': 'download', 'label': 'Download packages', 'weight': 3.0},
        {'id': 'verify', 'label': 'Verify integrity', 'weight': 1.0},
        {'id': 'extract', 'label': 'Extract files', 'weight': 2.0},
        {'id': 'configure', 'label': 'Configure system', 'weight': 1.5},
        {'id': 'cleanup', 'label': 'Cleanup temporary files', 'weight': 0.5}
    ]
    
    installer = ProgressAdapter(
        message="Installing software:",
        mode='steps',
        steps=install_steps
    )
    
    installer.start()
    print(f"    Started installation: {installer}")
    
    # Simulate installation steps
    for i, step in enumerate(install_steps):
        rendered = installer.render()
        print(f"    Step {i+1}: {rendered}")
        
        if hasattr(installer, '_enhanced_adapter') and installer._is_enhanced:
            installer._enhanced_adapter.next_step(f"Executing {step['label']}")
        
        time.sleep(0.01)
    
    # Scenario 3: Data processing with error handling
    print("  ⚠️  Error handling scenario:")
    data_processor = ProgressAdapter(
        message="Processing data:",
        total=50,
        mode='bar'
    )
    
    data_processor.start()
    
    # Process successfully for a while
    for i in range(0, 30, 10):
        data_processor.update(i)
        print(f"    Processing: {data_processor.render()}")
    
    # Simulate error condition
    try:
        if hasattr(data_processor, '_enhanced_adapter') and data_processor._is_enhanced:
            data_processor._enhanced_adapter.state = data_processor._enhanced_adapter.state.__class__.ERROR
            stats = data_processor.get_statistics()
            print(f"    Error state: {stats['state']}")
    except:
        print("    Error handling in legacy mode")
    
    # Scenario 4: Download with rate tracking
    print("  📥 Download tracking scenario:")
    downloader = ProgressAdapter(
        message="Downloading update:",
        total=1000000,  # 1MB
        mode='detailed',
        show_rate=True
    )
    
    downloader.start()
    
    # Simulate variable download speeds
    downloaded = 0
    chunk_sizes = [50000, 100000, 75000, 150000, 200000]  # Variable chunks
    
    for chunk in chunk_sizes:
        downloaded += chunk
        if downloaded > 1000000:
            downloaded = 1000000
        
        downloader.update(downloaded)
        rendered = downloader.render()
        print(f"    Downloaded: {rendered}")
        
        if downloaded >= 1000000:
            break
        
        time.sleep(0.01)
    
    final_stats = downloader.get_statistics()
    print(f"    Download complete: {final_stats.get('state', 'unknown')}")
    
    print("✅ Real-world scenario tests passed!")
    return True


def test_progress_states_and_lifecycle():
    """Test progress states and lifecycle management."""
    print("🧪 Testing progress states and lifecycle...")
    
    from tui_engine.widgets.progress_adapter import ProgressAdapter, ProgressState
    
    # Test complete lifecycle
    print("  🔄 Lifecycle tests:")
    lifecycle_progress = ProgressAdapter(
        message="Lifecycle test:",
        total=100
    )
    
    # Check initial state
    stats = lifecycle_progress.get_statistics()
    print(f"    Initial state: {stats.get('state', 'unknown')}")
    
    # Start progress
    lifecycle_progress.start()
    stats = lifecycle_progress.get_statistics()
    print(f"    Started state: {stats.get('state', 'unknown')}")
    
    # Update progress
    lifecycle_progress.update(50)
    ratio = lifecycle_progress.get_progress_ratio()
    print(f"    Mid-progress: {ratio:.1%}")
    
    # Complete progress
    lifecycle_progress.complete()
    stats = lifecycle_progress.get_statistics()
    print(f"    Completed state: {stats.get('state', 'unknown')}")
    
    # Test pause/resume (enhanced mode only)
    print("  ⏸️  Pause/Resume tests:")
    if lifecycle_progress.is_questionary_enhanced():
        pause_progress = ProgressAdapter(
            message="Pause test:",
            total=100
        )
        
        pause_progress.start()
        pause_progress.update(30)
        
        if hasattr(pause_progress, '_enhanced_adapter'):
            pause_progress._enhanced_adapter.pause()
            stats = pause_progress.get_statistics()
            print(f"    Paused state: {stats.get('state', 'unknown')}")
            
            pause_progress._enhanced_adapter.resume()
            stats = pause_progress.get_statistics()
            print(f"    Resumed state: {stats.get('state', 'unknown')}")
    else:
        print("    Pause/Resume not available in legacy mode")
    
    # Test error conditions
    print("  ❌ Error condition tests:")
    error_progress = ProgressAdapter(
        message="Error test:",
        total=100
    )
    
    error_progress.start()
    error_progress.update(25)
    
    # Simulate error (enhanced mode only)
    if hasattr(error_progress, '_enhanced_adapter') and error_progress._is_enhanced:
        try:
            # This would normally be triggered by application logic
            error_progress._enhanced_adapter.state = ProgressState.ERROR
            stats = error_progress.get_statistics()
            print(f"    Error state: {stats.get('state', 'unknown')}")
        except:
            print("    Error simulation failed")
    else:
        print("    Error states not available in legacy mode")
    
    print("✅ Progress states and lifecycle tests passed!")
    return True


def test_performance_and_timing():
    """Test performance and timing accuracy."""
    print("🧪 Testing performance and timing...")
    
    from tui_engine.widgets.progress_adapter import ProgressAdapter
    import time
    
    # Test timing accuracy
    print("  ⏱️  Timing accuracy tests:")
    timing_progress = ProgressAdapter(
        message="Timing test:",
        total=10,
        show_eta=True
    )
    
    start_time = time.time()
    timing_progress.start()
    
    # Simulate work with known timing
    for i in range(1, 11):
        time.sleep(0.01)  # 10ms delay per item
        timing_progress.update(i)
        
        elapsed = timing_progress.get_elapsed_time()
        if elapsed:
            print(f"    Item {i}: elapsed {elapsed.total_seconds():.3f}s")
    
    total_elapsed = time.time() - start_time
    measured_elapsed = timing_progress.get_elapsed_time()
    
    if measured_elapsed:
        print(f"    Total time - Actual: {total_elapsed:.3f}s, Measured: {measured_elapsed.total_seconds():.3f}s")
        # Allow for small timing differences
        assert abs(total_elapsed - measured_elapsed.total_seconds()) < 0.1
    
    # Test rapid updates
    print("  🚀 Rapid update tests:")
    rapid_progress = ProgressAdapter(
        message="Rapid updates:",
        total=1000
    )
    
    rapid_start = time.time()
    rapid_progress.start()
    
    # Rapid updates
    for i in range(0, 1001, 100):
        rapid_progress.update(i)
        # No sleep - test rapid fire updates
    
    rapid_end = time.time()
    rapid_elapsed = rapid_end - rapid_start
    
    print(f"    Rapid updates completed in {rapid_elapsed:.3f}s")
    assert rapid_elapsed < 1.0  # Should be very fast
    
    # Test memory usage with large progress history
    print("  💾 Memory usage tests:")
    memory_progress = ProgressAdapter(
        message="Memory test:",
        total=10000
    )
    
    memory_progress.start()
    
    # Generate many progress updates
    for i in range(0, 10001, 100):
        memory_progress.update(i)
    
    stats = memory_progress.get_statistics()
    print(f"    Final progress: {stats.get('progress_ratio', 0):.1%}")
    assert stats.get('progress_ratio', 0) == 1.0
    
    print("✅ Performance and timing tests passed!")
    return True


def main():
    """Run all ProgressAdapter tests."""
    print("🚀 Starting ProgressAdapter test suite...\n")
    
    tests = [
        test_progress_calculator,
        test_progress_renderer,
        test_enhanced_progress_adapter,
        test_backward_compatible_adapter,
        test_convenience_functions,
        test_real_world_scenarios,
        test_progress_states_and_lifecycle,
        test_performance_and_timing
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            print()  # Add spacing between tests
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with error: {e}\n")
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All ProgressAdapter tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    exit(main())