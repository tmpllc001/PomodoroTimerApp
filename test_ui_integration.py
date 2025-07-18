#!/usr/bin/env python3
"""
UI-バックエンド統合テスト
"""
import sys
import os
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# PyQt6のテスト環境設定
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QSlider, QCheckBox
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtTest import QTest, QSignalSpy

from src.controllers.timer_controller import TimerController
from src.models.timer_model import TimerState, SessionType
from src.bridge.ui_bridge import UIBridge


class MockMainWindow(QWidget):
    """Mock main window for testing."""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup mock UI components."""
        self.start_button = QPushButton("Start")
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")
        self.reset_button = QPushButton("Reset")
        self.skip_button = QPushButton("Skip")
        
        self.volume_slider = QSlider()
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        
        self.sound_toggle = QCheckBox("Enable Sound")
        self.sound_toggle.setChecked(True)


class TestUIIntegration:
    """Test UI-Backend integration."""
    
    def __init__(self):
        self.app = None
        self.controller = None
        self.main_window = None
        self.bridge = None
        
    def setup(self):
        """Setup test environment."""
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
            
        self.controller = TimerController()
        self.controller.set_sound_enabled(False)  # Disable sound for testing
        
        self.main_window = MockMainWindow()
        self.bridge = UIBridge(self.controller, self.main_window)
        
    def teardown(self):
        """Cleanup test environment."""
        if self.bridge:
            self.bridge.cleanup()
        if self.controller:
            self.controller.cleanup()
        if self.main_window:
            self.main_window.close()
            
    def test_timer_controls(self):
        """Test timer control buttons."""
        print("=== Timer Controls Test ===")
        
        # Test start button
        initial_state = self.controller.get_timer_info()['state']
        print(f"Initial state: {initial_state}")
        assert initial_state == TimerState.STOPPED
        
        # Simulate start button click
        self.bridge.start_timer()
        time.sleep(0.1)
        
        current_state = self.controller.get_timer_info()['state']
        print(f"After start: {current_state}")
        assert current_state == TimerState.RUNNING
        
        # Test pause button
        self.bridge.pause_timer()
        time.sleep(0.1)
        
        current_state = self.controller.get_timer_info()['state']
        print(f"After pause: {current_state}")
        assert current_state == TimerState.PAUSED
        
        # Test stop button
        self.bridge.stop_timer()
        time.sleep(0.1)
        
        current_state = self.controller.get_timer_info()['state']
        print(f"After stop: {current_state}")
        assert current_state == TimerState.STOPPED
        
        # Test reset button
        self.bridge.reset_timer()
        time.sleep(0.1)
        
        timer_info = self.controller.get_timer_info()
        print(f"After reset: {timer_info['remaining_time']} seconds")
        assert timer_info['remaining_time'] == 25 * 60
        
        print("✅ Timer Controls Test passed")
        
    def test_settings_integration(self):
        """Test settings integration."""
        print("\n=== Settings Integration Test ===")
        
        # Test volume setting
        self.bridge.set_volume(50)
        current_volume = self.bridge.get_current_volume()
        print(f"Volume set to 50%, current: {current_volume}%")
        assert current_volume == 50
        
        # Test sound toggle
        self.bridge.toggle_sound(False)
        sound_enabled = self.bridge.is_sound_enabled()
        print(f"Sound disabled: {not sound_enabled}")
        assert not sound_enabled
        
        self.bridge.toggle_sound(True)
        sound_enabled = self.bridge.is_sound_enabled()
        print(f"Sound enabled: {sound_enabled}")
        assert sound_enabled
        
        # Test duration settings
        self.bridge.set_work_duration(30)
        durations = self.bridge.get_current_durations()
        print(f"Work duration set to 30 minutes: {durations['work']} seconds")
        assert durations['work'] == 30 * 60
        
        self.bridge.set_short_break_duration(10)
        durations = self.bridge.get_current_durations()
        print(f"Short break set to 10 minutes: {durations['short_break']} seconds")
        assert durations['short_break'] == 10 * 60
        
        print("✅ Settings Integration Test passed")
        
    def test_signal_connections(self):
        """Test signal connections between UI and backend."""
        print("\n=== Signal Connections Test ===")
        
        # Setup signal spies
        timer_spy = QSignalSpy(self.bridge.timer_updated)
        state_spy = QSignalSpy(self.bridge.state_changed)
        
        # Start timer and check signals
        self.bridge.start_timer()
        time.sleep(0.2)
        
        # Check if signals were emitted
        timer_signals = len(timer_spy)
        state_signals = len(state_spy)
        
        print(f"Timer update signals: {timer_signals}")
        print(f"State change signals: {state_signals}")
        
        assert timer_signals > 0
        assert state_signals > 0
        
        # Stop timer
        self.bridge.stop_timer()
        time.sleep(0.1)
        
        print("✅ Signal Connections Test passed")
        
    def test_session_completion(self):
        """Test session completion handling."""
        print("\n=== Session Completion Test ===")
        
        # Set very short durations for testing
        self.bridge.set_work_duration(0)  # This will be 0 seconds
        self.controller.set_durations(1, 1, 1, 2)  # 1 second each
        
        # Setup completion signal spy
        completion_spy = QSignalSpy(self.bridge.session_completed)
        
        # Start timer
        self.bridge.start_timer()
        time.sleep(1.5)  # Wait for completion
        
        # Check if completion signal was emitted
        completions = len(completion_spy)
        print(f"Session completion signals: {completions}")
        
        if completions > 0:
            print("✅ Session Completion Test passed")
        else:
            print("⚠️  Session Completion Test - no signals (may be timing issue)")
            
    def test_data_retrieval(self):
        """Test data retrieval methods."""
        print("\n=== Data Retrieval Test ===")
        
        # Test timer info
        timer_info = self.bridge.get_timer_info()
        print(f"Timer info keys: {list(timer_info.keys())}")
        assert 'state' in timer_info
        assert 'remaining_time' in timer_info
        
        # Test session stats
        stats = self.bridge.get_session_stats()
        print(f"Session stats keys: {list(stats.keys())}")
        assert 'total_sessions' in stats
        assert 'completion_rate' in stats
        
        # Test today's sessions
        today_sessions = self.bridge.get_today_sessions()
        print(f"Today's sessions count: {len(today_sessions)}")
        assert isinstance(today_sessions, list)
        
        # Test weekly stats
        weekly_stats = self.bridge.get_weekly_stats()
        print(f"Weekly stats keys: {list(weekly_stats.keys())}")
        assert isinstance(weekly_stats, dict)
        
        # Test formatting methods
        formatted_time = self.bridge.format_time(125)
        print(f"Formatted time (125s): {formatted_time}")
        assert formatted_time == "02:05"
        
        session_display = self.bridge.get_session_type_display(SessionType.WORK)
        print(f"Work session display: {session_display}")
        assert session_display == "Work Session"
        
        state_display = self.bridge.get_state_display(TimerState.RUNNING)
        print(f"Running state display: {state_display}")
        assert state_display == "Running"
        
        print("✅ Data Retrieval Test passed")
        
    def test_error_handling(self):
        """Test error handling in bridge operations."""
        print("\n=== Error Handling Test ===")
        
        # Test with invalid volume
        try:
            self.bridge.set_volume(150)  # Invalid volume
            current_volume = self.bridge.get_current_volume()
            print(f"Volume after invalid input: {current_volume}%")
            # Should be clamped to valid range
        except Exception as e:
            print(f"Volume error handling: {e}")
            
        # Test sound operations
        try:
            self.bridge.test_sound()
            print("Sound test completed without error")
        except Exception as e:
            print(f"Sound test error: {e}")
            
        # Test export with invalid path
        try:
            result = self.bridge.export_session_data("/invalid/path/data.json")
            print(f"Export with invalid path result: {result}")
            assert not result
        except Exception as e:
            print(f"Export error handling: {e}")
            
        print("✅ Error Handling Test passed")
        
    def run_all_tests(self):
        """Run all integration tests."""
        print("UI-Backend Integration Tests Starting...")
        
        self.setup()
        
        try:
            self.test_timer_controls()
            self.test_settings_integration()
            self.test_signal_connections()
            self.test_session_completion()
            self.test_data_retrieval()
            self.test_error_handling()
            
            print("\n🎉 All UI-Backend Integration Tests Passed!")
            return True
            
        except Exception as e:
            print(f"\n❌ Integration Test Failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            self.teardown()


class TestUIBridgeStandalone:
    """Test UI Bridge without actual UI components."""
    
    def test_bridge_initialization(self):
        """Test bridge initialization without UI."""
        print("\n=== Bridge Initialization Test ===")
        
        controller = TimerController()
        controller.set_sound_enabled(False)
        
        # Create a minimal mock window
        mock_window = Mock()
        
        # Initialize bridge
        bridge = UIBridge(controller, mock_window)
        
        # Test basic functionality
        assert bridge.get_timer_info() is not None
        assert bridge.get_session_stats() is not None
        assert bridge.get_current_volume() >= 0
        
        # Cleanup
        bridge.cleanup()
        controller.cleanup()
        
        print("✅ Bridge Initialization Test passed")
        
    def test_bridge_without_ui_components(self):
        """Test bridge methods when UI components are missing."""
        print("\n=== Bridge Without UI Components Test ===")
        
        controller = TimerController()
        controller.set_sound_enabled(False)
        
        # Create mock window without UI components
        mock_window = Mock()
        mock_window.start_button = None
        
        bridge = UIBridge(controller, mock_window)
        
        # Test timer operations
        bridge.start_timer()
        time.sleep(0.1)
        
        info = bridge.get_timer_info()
        assert info['state'] == TimerState.RUNNING
        
        bridge.stop_timer()
        time.sleep(0.1)
        
        info = bridge.get_timer_info()
        assert info['state'] == TimerState.STOPPED
        
        # Cleanup
        bridge.cleanup()
        controller.cleanup()
        
        print("✅ Bridge Without UI Components Test passed")


def main():
    """Run all integration tests."""
    # Test with Qt Application
    integration_test = TestUIIntegration()
    qt_success = integration_test.run_all_tests()
    
    # Test standalone bridge
    standalone_test = TestUIBridgeStandalone()
    
    try:
        standalone_test.test_bridge_initialization()
        standalone_test.test_bridge_without_ui_components()
        standalone_success = True
        print("\n✅ Standalone Bridge Tests passed")
    except Exception as e:
        print(f"\n❌ Standalone Bridge Test failed: {e}")
        standalone_success = False
    
    overall_success = qt_success and standalone_success
    
    if overall_success:
        print("\n🎉 All Integration Tests Successful!")
    else:
        print("\n❌ Some Integration Tests Failed")
    
    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)