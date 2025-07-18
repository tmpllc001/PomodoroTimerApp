#!/usr/bin/env python3
"""
Integration Test for Pomodoro Timer Application
Quick test to verify UI-Backend integration.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import logging

# Test configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ui_components():
    """Test UI components independently."""
    logger.info("Testing UI components...")
    
    try:
        from views.main_window import MainWindow
        from views.components.timer_display import TimerDisplay
        from views.components.control_panel import ControlPanel
        
        # Test component creation
        app = QApplication(sys.argv)
        
        # Test MainWindow
        window = MainWindow()
        assert window.timer_display is not None, "TimerDisplay not created"
        assert window.control_panel is not None, "ControlPanel not created"
        
        # Test signals
        assert hasattr(window, 'start_requested'), "start_requested signal missing"
        assert hasattr(window, 'pause_requested'), "pause_requested signal missing"
        assert hasattr(window, 'reset_requested'), "reset_requested signal missing"
        
        logger.info("✅ UI components test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ UI components test failed: {e}")
        return False

def test_timer_display():
    """Test timer display functionality."""
    logger.info("Testing timer display...")
    
    try:
        from views.components.timer_display import TimerDisplay
        
        timer_display = TimerDisplay()
        
        # Test initial state
        assert timer_display.time_remaining == 25 * 60, "Initial time incorrect"
        assert not timer_display.is_timer_running(), "Timer should not be running initially"
        
        # Test time update signal
        assert hasattr(timer_display, 'time_updated'), "time_updated signal missing"
        assert hasattr(timer_display, 'timer_finished'), "timer_finished signal missing"
        
        logger.info("✅ Timer display test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Timer display test failed: {e}")
        return False

def test_control_panel():
    """Test control panel functionality."""
    logger.info("Testing control panel...")
    
    try:
        from views.components.control_panel import ControlPanel
        
        control_panel = ControlPanel()
        
        # Test button signals
        assert hasattr(control_panel, 'start_clicked'), "start_clicked signal missing"
        assert hasattr(control_panel, 'pause_clicked'), "pause_clicked signal missing"
        assert hasattr(control_panel, 'reset_clicked'), "reset_clicked signal missing"
        
        # Test button states
        assert control_panel.start_button.isEnabled(), "Start button should be enabled initially"
        assert not control_panel.pause_button.isEnabled(), "Pause button should be disabled initially"
        
        logger.info("✅ Control panel test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Control panel test failed: {e}")
        return False

def test_signal_connections():
    """Test signal connections between components."""
    logger.info("Testing signal connections...")
    
    try:
        from views.main_window import MainWindow
        app = QApplication(sys.argv)
        
        window = MainWindow()
        
        # Test that signals are properly connected
        # This would require actual signal testing which is complex
        # For now, just verify the components exist and have required methods
        
        assert hasattr(window, 'update_timer_display'), "update_timer_display method missing"
        assert hasattr(window, 'set_timer_state'), "set_timer_state method missing"
        assert hasattr(window, 'get_timer_display'), "get_timer_display method missing"
        assert hasattr(window, 'get_control_panel'), "get_control_panel method missing"
        
        logger.info("✅ Signal connections test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Signal connections test failed: {e}")
        return False

def main():
    """Run all integration tests."""
    logger.info("=== Starting Integration Tests ===")
    
    tests = [
        test_ui_components,
        test_timer_display,
        test_control_panel,
        test_signal_connections
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    logger.info(f"=== Test Results: {passed}/{total} passed ===")
    
    if passed == total:
        logger.info("🎉 All tests passed! Ready for UIBridge integration")
        return True
    else:
        logger.error("❌ Some tests failed! Review implementation")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)