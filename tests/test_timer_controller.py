"""
Unit tests for TimerController class.
Tests timer control logic, state management, and session handling.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtCore import QTimer, pyqtSignal, QObject


class MockTimerController(QObject):
    """Mock implementation of TimerController for testing."""
    
    # Signals
    timer_updated = pyqtSignal(str)  # Emits formatted time
    session_completed = pyqtSignal(str)  # Emits session type
    timer_finished = pyqtSignal()
    session_started = pyqtSignal(str)  # Emits session type
    
    def __init__(self, timer_model=None, audio_manager=None):
        super().__init__()
        self.timer_model = timer_model or self._create_mock_timer_model()
        self.audio_manager = audio_manager or self._create_mock_audio_manager()
        self.qt_timer = QTimer()
        self.qt_timer.timeout.connect(self._on_timer_tick)
        self.qt_timer.setInterval(1000)  # 1 second
        self.is_active = False
        
    def _create_mock_timer_model(self):
        """Create a mock timer model."""
        mock_model = Mock()
        mock_model.is_running = False
        mock_model.is_paused = False
        mock_model.current_time = 25 * 60
        mock_model.session_type = "work"
        mock_model.get_formatted_time.return_value = "25:00"
        mock_model.is_finished.return_value = False
        mock_model.get_next_session_type.return_value = "short_break"
        return mock_model
        
    def _create_mock_audio_manager(self):
        """Create a mock audio manager."""
        mock_audio = Mock()
        mock_audio.play_notification.return_value = True
        mock_audio.stop_notification.return_value = True
        return mock_audio
        
    def start_timer(self):
        """Start the timer."""
        if not self.is_active:
            self.timer_model.start()
            self.qt_timer.start()
            self.is_active = True
            self.session_started.emit(self.timer_model.session_type)
            return True
        return False
        
    def pause_timer(self):
        """Pause the timer."""
        if self.is_active and not self.timer_model.is_paused:
            self.timer_model.pause()
            self.qt_timer.stop()
            return True
        return False
        
    def resume_timer(self):
        """Resume the timer."""
        if self.is_active and self.timer_model.is_paused:
            self.timer_model.resume()
            self.qt_timer.start()
            return True
        return False
        
    def stop_timer(self):
        """Stop the timer."""
        if self.is_active:
            self.timer_model.stop()
            self.qt_timer.stop()
            self.is_active = False
            self.audio_manager.stop_notification()
            return True
        return False
        
    def reset_timer(self):
        """Reset the timer."""
        self.stop_timer()
        self.timer_model.reset()
        self.timer_updated.emit(self.timer_model.get_formatted_time())
        return True
        
    def toggle_timer(self):
        """Toggle between start/pause."""
        if not self.is_active:
            return self.start_timer()
        elif self.timer_model.is_paused:
            return self.resume_timer()
        else:
            return self.pause_timer()
            
    def _on_timer_tick(self):
        """Handle timer tick."""
        if self.is_active and not self.timer_model.is_paused:
            self.timer_model.tick()
            self.timer_updated.emit(self.timer_model.get_formatted_time())
            
            if self.timer_model.is_finished():
                self._handle_session_completion()
                
    def _handle_session_completion(self):
        """Handle session completion."""
        self.timer_model.complete_session()
        self.session_completed.emit(self.timer_model.session_type)
        self.audio_manager.play_notification()
        self.timer_finished.emit()
        
        # Auto-transition to next session
        next_session = self.timer_model.get_next_session_type()
        self.timer_model.set_session_type(next_session)
        self.stop_timer()
        
    def set_session_type(self, session_type):
        """Set the session type."""
        if session_type in ["work", "short_break", "long_break"]:
            self.timer_model.set_session_type(session_type)
            self.timer_updated.emit(self.timer_model.get_formatted_time())
            return True
        return False
        
    def get_timer_state(self):
        """Get current timer state."""
        return {
            'is_active': self.is_active,
            'is_paused': self.timer_model.is_paused,
            'current_time': self.timer_model.current_time,
            'session_type': self.timer_model.session_type,
            'formatted_time': self.timer_model.get_formatted_time(),
            'progress': self.timer_model.get_progress_percentage()
        }
        
    def get_session_stats(self):
        """Get session statistics."""
        return self.timer_model.get_session_stats()


class TestTimerController:
    """Test suite for TimerController class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_timer_model = Mock()
        self.mock_audio_manager = Mock()
        self.controller = MockTimerController(self.mock_timer_model, self.mock_audio_manager)
        
        # Set up mock timer model defaults
        self.mock_timer_model.is_running = False
        self.mock_timer_model.is_paused = False
        self.mock_timer_model.current_time = 25 * 60
        self.mock_timer_model.session_type = "work"
        self.mock_timer_model.get_formatted_time.return_value = "25:00"
        self.mock_timer_model.is_finished.return_value = False
        self.mock_timer_model.get_next_session_type.return_value = "short_break"
        self.mock_timer_model.get_progress_percentage.return_value = 0
        
    def test_initialization(self):
        """Test controller initialization."""
        assert self.controller.timer_model == self.mock_timer_model
        assert self.controller.audio_manager == self.mock_audio_manager
        assert not self.controller.is_active
        assert self.controller.qt_timer.interval() == 1000
        
    def test_start_timer_success(self):
        """Test successful timer start."""
        result = self.controller.start_timer()
        assert result is True
        assert self.controller.is_active
        self.mock_timer_model.start.assert_called_once()
        
    def test_start_timer_already_active(self):
        """Test starting timer when already active."""
        self.controller.is_active = True
        result = self.controller.start_timer()
        assert result is False
        self.mock_timer_model.start.assert_not_called()
        
    def test_pause_timer_success(self):
        """Test successful timer pause."""
        self.controller.is_active = True
        self.mock_timer_model.is_paused = False
        result = self.controller.pause_timer()
        assert result is True
        self.mock_timer_model.pause.assert_called_once()
        
    def test_pause_timer_not_active(self):
        """Test pausing timer when not active."""
        self.controller.is_active = False
        result = self.controller.pause_timer()
        assert result is False
        self.mock_timer_model.pause.assert_not_called()
        
    def test_resume_timer_success(self):
        """Test successful timer resume."""
        self.controller.is_active = True
        self.mock_timer_model.is_paused = True
        result = self.controller.resume_timer()
        assert result is True
        self.mock_timer_model.resume.assert_called_once()
        
    def test_resume_timer_not_paused(self):
        """Test resuming timer when not paused."""
        self.controller.is_active = True
        self.mock_timer_model.is_paused = False
        result = self.controller.resume_timer()
        assert result is False
        self.mock_timer_model.resume.assert_not_called()
        
    def test_stop_timer_success(self):
        """Test successful timer stop."""
        self.controller.is_active = True
        result = self.controller.stop_timer()
        assert result is True
        assert not self.controller.is_active
        self.mock_timer_model.stop.assert_called_once()
        self.mock_audio_manager.stop_notification.assert_called_once()
        
    def test_stop_timer_not_active(self):
        """Test stopping timer when not active."""
        self.controller.is_active = False
        result = self.controller.stop_timer()
        assert result is False
        self.mock_timer_model.stop.assert_not_called()
        
    def test_reset_timer(self):
        """Test timer reset."""
        self.controller.is_active = True
        result = self.controller.reset_timer()
        assert result is True
        assert not self.controller.is_active
        self.mock_timer_model.reset.assert_called_once()
        
    def test_toggle_timer_start(self):
        """Test toggle timer from stopped state."""
        self.controller.is_active = False
        result = self.controller.toggle_timer()
        assert result is True
        assert self.controller.is_active
        self.mock_timer_model.start.assert_called_once()
        
    def test_toggle_timer_pause(self):
        """Test toggle timer from running state."""
        self.controller.is_active = True
        self.mock_timer_model.is_paused = False
        result = self.controller.toggle_timer()
        assert result is True
        self.mock_timer_model.pause.assert_called_once()
        
    def test_toggle_timer_resume(self):
        """Test toggle timer from paused state."""
        self.controller.is_active = True
        self.mock_timer_model.is_paused = True
        result = self.controller.toggle_timer()
        assert result is True
        self.mock_timer_model.resume.assert_called_once()
        
    def test_timer_tick_normal(self):
        """Test normal timer tick."""
        self.controller.is_active = True
        self.mock_timer_model.is_paused = False
        self.mock_timer_model.is_finished.return_value = False
        
        with patch.object(self.controller, 'timer_updated') as mock_signal:
            self.controller._on_timer_tick()
            self.mock_timer_model.tick.assert_called_once()
            mock_signal.emit.assert_called_once_with("25:00")
            
    def test_timer_tick_paused(self):
        """Test timer tick when paused."""
        self.controller.is_active = True
        self.mock_timer_model.is_paused = True
        
        self.controller._on_timer_tick()
        self.mock_timer_model.tick.assert_not_called()
        
    def test_timer_tick_finished(self):
        """Test timer tick when finished."""
        self.controller.is_active = True
        self.mock_timer_model.is_paused = False
        self.mock_timer_model.is_finished.return_value = True
        
        with patch.object(self.controller, '_handle_session_completion') as mock_handler:
            self.controller._on_timer_tick()
            mock_handler.assert_called_once()
            
    def test_session_completion_handling(self):
        """Test session completion handling."""
        self.mock_timer_model.session_type = "work"
        self.mock_timer_model.get_next_session_type.return_value = "short_break"
        
        with patch.object(self.controller, 'session_completed') as mock_signal:
            with patch.object(self.controller, 'timer_finished') as mock_finished:
                self.controller._handle_session_completion()
                
                self.mock_timer_model.complete_session.assert_called_once()
                self.mock_audio_manager.play_notification.assert_called_once()
                mock_signal.emit.assert_called_once_with("work")
                mock_finished.emit.assert_called_once()
                
    def test_set_session_type_valid(self):
        """Test setting valid session type."""
        result = self.controller.set_session_type("short_break")
        assert result is True
        self.mock_timer_model.set_session_type.assert_called_once_with("short_break")
        
    def test_set_session_type_invalid(self):
        """Test setting invalid session type."""
        result = self.controller.set_session_type("invalid_type")
        assert result is False
        self.mock_timer_model.set_session_type.assert_not_called()
        
    def test_get_timer_state(self):
        """Test getting timer state."""
        self.controller.is_active = True
        self.mock_timer_model.is_paused = False
        self.mock_timer_model.current_time = 1500
        self.mock_timer_model.session_type = "work"
        self.mock_timer_model.get_formatted_time.return_value = "25:00"
        self.mock_timer_model.get_progress_percentage.return_value = 50.0
        
        state = self.controller.get_timer_state()
        
        assert state['is_active'] is True
        assert state['is_paused'] is False
        assert state['current_time'] == 1500
        assert state['session_type'] == "work"
        assert state['formatted_time'] == "25:00"
        assert state['progress'] == 50.0
        
    def test_get_session_stats(self):
        """Test getting session statistics."""
        expected_stats = {
            'sessions_completed': 5,
            'total_focus_time': 7500,
            'current_cycle': 5
        }
        self.mock_timer_model.get_session_stats.return_value = expected_stats
        
        stats = self.controller.get_session_stats()
        assert stats == expected_stats
        self.mock_timer_model.get_session_stats.assert_called_once()
        
    def test_signal_emission_on_session_start(self):
        """Test signal emission when session starts."""
        with patch.object(self.controller, 'session_started') as mock_signal:
            self.controller.start_timer()
            mock_signal.emit.assert_called_once_with("work")
            
    def test_work_to_short_break_transition(self):
        """Test transition from work to short break."""
        self.mock_timer_model.session_type = "work"
        self.mock_timer_model.get_next_session_type.return_value = "short_break"
        
        self.controller._handle_session_completion()
        
        self.mock_timer_model.set_session_type.assert_called_once_with("short_break")
        
    def test_work_to_long_break_transition(self):
        """Test transition from work to long break."""
        self.mock_timer_model.session_type = "work"
        self.mock_timer_model.get_next_session_type.return_value = "long_break"
        
        self.controller._handle_session_completion()
        
        self.mock_timer_model.set_session_type.assert_called_once_with("long_break")
        
    def test_break_to_work_transition(self):
        """Test transition from break to work."""
        self.mock_timer_model.session_type = "short_break"
        self.mock_timer_model.get_next_session_type.return_value = "work"
        
        self.controller._handle_session_completion()
        
        self.mock_timer_model.set_session_type.assert_called_once_with("work")
        
    def test_timer_controller_cleanup(self):
        """Test proper cleanup when stopping timer."""
        self.controller.is_active = True
        self.controller.stop_timer()
        
        assert not self.controller.is_active
        self.mock_timer_model.stop.assert_called_once()
        self.mock_audio_manager.stop_notification.assert_called_once()
        
    def test_multiple_session_completions(self):
        """Test multiple session completions."""
        for i in range(3):
            self.controller._handle_session_completion()
            
        assert self.mock_timer_model.complete_session.call_count == 3
        assert self.mock_audio_manager.play_notification.call_count == 3