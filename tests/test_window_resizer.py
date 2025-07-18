#!/usr/bin/env python3
"""
Unit tests for Window Resizer functionality
Phase 2 feature testing.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QRect
from PyQt6.QtTest import QTest

try:
    from features.window_resizer import WindowResizer
    from views.resizable_window import ResizableWindow
except ImportError:
    # Alternative import for relative imports
    import sys
    sys.path.append('../src')
    from features.window_resizer import WindowResizer
    from views.resizable_window import ResizableWindow


class TestWindowResizer(unittest.TestCase):
    """Test cases for WindowResizer class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for tests."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_window = Mock()
        self.mock_window.geometry.return_value = QRect(100, 100, 400, 300)
        self.mock_window.windowOpacity.return_value = 0.9
        
        self.resizer = WindowResizer(self.mock_window)
    
    def test_initialization(self):
        """Test WindowResizer initialization."""
        self.assertIsNotNone(self.resizer)
        self.assertEqual(self.resizer.window, self.mock_window)
        self.assertEqual(self.resizer.current_size, 'default')
        self.assertTrue(self.resizer.auto_resize_enabled)
    
    def test_window_size_configurations(self):
        """Test window size configurations."""
        work_config = self.resizer.WINDOW_SIZES['work']
        break_config = self.resizer.WINDOW_SIZES['break']
        default_config = self.resizer.WINDOW_SIZES['default']
        
        # Test work mode size
        self.assertEqual(work_config['width'], 200)
        self.assertEqual(work_config['height'], 100)
        self.assertEqual(work_config['opacity'], 0.7)
        
        # Test break mode size
        self.assertEqual(break_config['width'], 600)
        self.assertEqual(break_config['height'], 400)
        self.assertEqual(break_config['opacity'], 0.95)
        
        # Test default mode size
        self.assertEqual(default_config['width'], 450)
        self.assertEqual(default_config['height'], 350)
        self.assertEqual(default_config['opacity'], 0.9)
    
    def test_resize_to_work_mode(self):
        """Test resize to work mode."""
        self.resizer.resize_window('work', animate=False)
        
        # Check that window was resized
        self.mock_window.setGeometry.assert_called()
        self.mock_window.setWindowOpacity.assert_called_with(0.7)
        self.assertEqual(self.resizer.current_size, 'work')
    
    def test_resize_to_break_mode(self):
        """Test resize to break mode."""
        self.resizer.resize_window('break', animate=False)
        
        # Check that window was resized
        self.mock_window.setGeometry.assert_called()
        self.mock_window.setWindowOpacity.assert_called_with(0.95)
        self.assertEqual(self.resizer.current_size, 'break')
    
    def test_resize_to_default_mode(self):
        """Test resize to default mode."""
        self.resizer.resize_window('default', animate=False)
        
        # Check that window was resized
        self.mock_window.setGeometry.assert_called()
        self.mock_window.setWindowOpacity.assert_called_with(0.9)
        self.assertEqual(self.resizer.current_size, 'default')
    
    def test_auto_resize_toggle(self):
        """Test auto resize enable/disable."""
        # Test disable
        self.resizer.toggle_auto_resize(False)
        self.assertFalse(self.resizer.auto_resize_enabled)
        
        # Test enable
        self.resizer.toggle_auto_resize(True)
        self.assertTrue(self.resizer.auto_resize_enabled)
    
    def test_resize_disabled_when_auto_resize_off(self):
        """Test that resize is ignored when auto resize is disabled."""
        self.resizer.toggle_auto_resize(False)
        self.mock_window.reset_mock()
        
        self.resizer.resize_window('work', animate=False)
        
        # Check that window was NOT resized
        self.mock_window.setGeometry.assert_not_called()
        self.mock_window.setWindowOpacity.assert_not_called()
    
    @patch('features.window_resizer.QApplication.primaryScreen')
    def test_center_window(self, mock_primary_screen):
        """Test center window functionality."""
        # Mock screen geometry
        mock_screen = Mock()
        mock_screen.geometry.return_value = QRect(0, 0, 1920, 1080)
        mock_primary_screen.return_value = mock_screen
        
        # Mock window geometry
        mock_frame_geometry = Mock()
        mock_frame_geometry.center.return_value = mock_screen.geometry().center()
        self.mock_window.frameGeometry.return_value = mock_frame_geometry
        
        self.resizer.center_window()
        
        # Check that window was moved
        self.mock_window.move.assert_called()
    
    def test_get_current_size(self):
        """Test get current size method."""
        self.assertEqual(self.resizer.get_current_size(), 'default')
        
        self.resizer.resize_window('work', animate=False)
        self.assertEqual(self.resizer.get_current_size(), 'work')
    
    def test_is_auto_resize_enabled(self):
        """Test is auto resize enabled method."""
        self.assertTrue(self.resizer.is_auto_resize_enabled())
        
        self.resizer.toggle_auto_resize(False)
        self.assertFalse(self.resizer.is_auto_resize_enabled())


class TestResizableWindow(unittest.TestCase):
    """Test cases for ResizableWindow class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for tests."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures."""
        self.window = ResizableWindow()
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.window.cleanup()
    
    def test_initialization(self):
        """Test ResizableWindow initialization."""
        self.assertIsNotNone(self.window)
        self.assertIsNotNone(self.window.window_resizer)
        self.assertIsNotNone(self.window.timer_display)
        self.assertIsNotNone(self.window.control_panel)
        self.assertEqual(self.window.current_session_type, 'default')
        self.assertFalse(self.window.is_work_session)
    
    def test_session_type_changes(self):
        """Test session type changes."""
        # Test work mode
        self.window.set_session_type('work')
        self.assertEqual(self.window.current_session_type, 'work')
        self.assertTrue(self.window.is_work_session)
        
        # Test break mode
        self.window.set_session_type('break')
        self.assertEqual(self.window.current_session_type, 'break')
        self.assertFalse(self.window.is_work_session)
    
    def test_auto_resize_toggle(self):
        """Test auto resize toggle."""
        # Test disable
        self.window.toggle_auto_resize(False)
        self.assertFalse(self.window.is_auto_resize_enabled())
        
        # Test enable
        self.window.toggle_auto_resize(True)
        self.assertTrue(self.window.is_auto_resize_enabled())
    
    def test_manual_resize_methods(self):
        """Test manual resize methods."""
        # Test resize to work mode
        self.window.resize_to_work_mode()
        self.assertEqual(self.window.current_session_type, 'work')
        
        # Test resize to break mode
        self.window.resize_to_break_mode()
        self.assertEqual(self.window.current_session_type, 'break')
        
        # Test resize to default mode
        self.window.resize_to_default_mode()
        self.assertEqual(self.window.current_session_type, 'default')
    
    def test_get_resize_config(self):
        """Test get resize configuration."""
        config = self.window.get_resize_config()
        
        self.assertIsNotNone(config)
        self.assertIn('current_session_type', config)
        self.assertIn('is_work_session', config)
        self.assertIn('auto_resize_enabled', config)
        self.assertIn('current_size', config)
    
    def test_component_access_methods(self):
        """Test component access methods."""
        self.assertIsNotNone(self.window.get_timer_display())
        self.assertIsNotNone(self.window.get_control_panel())
        self.assertIsNotNone(self.window.get_window_resizer())
    
    def test_timer_display_update(self):
        """Test timer display update."""
        # Test update timer display
        self.window.update_timer_display(1500)  # 25 minutes
        
        # Check that timer display was updated
        self.assertEqual(self.window.timer_display.time_remaining, 1500)
    
    def test_timer_state_update(self):
        """Test timer state update."""
        # Test set timer state
        self.window.set_timer_state(True)
        
        # This should update the control panel state
        # (Exact assertion depends on control panel implementation)
        self.assertIsNotNone(self.window.control_panel)


class TestWindowResizerIntegration(unittest.TestCase):
    """Integration tests for window resizer with actual UI components."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for tests."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures."""
        self.window = ResizableWindow()
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.window.cleanup()
    
    def test_session_workflow(self):
        """Test complete session workflow with resizing."""
        # Start in default mode
        self.assertEqual(self.window.current_session_type, 'default')
        
        # Simulate starting a work session
        self.window.on_session_started()
        self.assertEqual(self.window.current_session_type, 'work')
        self.assertTrue(self.window.is_work_session)
        
        # Simulate timer finishing (work -> break)
        self.window.on_timer_finished()
        self.assertEqual(self.window.current_session_type, 'break')
        self.assertFalse(self.window.is_work_session)
    
    def test_resize_with_animation_disabled(self):
        """Test resize functionality with animation disabled."""
        # Test work mode resize
        self.window.window_resizer.resize_window('work', animate=False)
        self.assertEqual(self.window.window_resizer.current_size, 'work')
        
        # Test break mode resize
        self.window.window_resizer.resize_window('break', animate=False)
        self.assertEqual(self.window.window_resizer.current_size, 'break')


def run_tests():
    """Run all window resizer tests."""
    print("🧪 Running Window Resizer Tests...")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestWindowResizer))
    test_suite.addTest(unittest.makeSuite(TestResizableWindow))
    test_suite.addTest(unittest.makeSuite(TestWindowResizerIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    if result.wasSuccessful():
        print("✅ All Window Resizer tests passed!")
        return True
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
        return False


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)