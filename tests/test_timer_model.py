"""
Unit tests for TimerModel class.
Tests timer state management, time tracking, and session statistics.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta


class MockTimerModel:
    """Mock implementation of TimerModel for testing."""
    
    def __init__(self):
        self.current_time = 25 * 60  # 25 minutes in seconds
        self.original_time = 25 * 60
        self.is_running = False
        self.is_paused = False
        self.session_type = "work"  # work, short_break, long_break
        self.cycle_count = 0
        self.start_time = None
        self.pause_time = None
        self.total_pause_duration = 0
        self.sessions_completed = 0
        self.total_focus_time = 0
        self.session_start_time = None
        
        # Configuration
        self.work_duration = 25 * 60
        self.short_break_duration = 5 * 60
        self.long_break_duration = 15 * 60
        self.cycles_until_long_break = 4
        
    def start(self):
        """Start the timer."""
        self.is_running = True
        self.is_paused = False
        self.start_time = time.time()
        self.session_start_time = self.start_time
        
    def pause(self):
        """Pause the timer."""
        if self.is_running:
            self.is_paused = True
            self.pause_time = time.time()
            
    def resume(self):
        """Resume the timer."""
        if self.is_paused:
            self.is_paused = False
            if self.pause_time:
                self.total_pause_duration += time.time() - self.pause_time
                self.pause_time = None
                
    def stop(self):
        """Stop the timer."""
        self.is_running = False
        self.is_paused = False
        self.start_time = None
        self.pause_time = None
        self.total_pause_duration = 0
        
    def reset(self):
        """Reset the timer to original settings."""
        self.stop()
        self.current_time = self.original_time
        
    def tick(self):
        """Decrement timer by one second."""
        if self.is_running and not self.is_paused and self.current_time > 0:
            self.current_time -= 1
            
    def is_finished(self):
        """Check if timer has finished."""
        return self.current_time <= 0
        
    def get_remaining_time(self):
        """Get remaining time in seconds."""
        return self.current_time
        
    def get_elapsed_time(self):
        """Get elapsed time in seconds."""
        if not self.start_time:
            return 0
        current = time.time()
        if self.pause_time:
            current = self.pause_time
        return current - self.start_time - self.total_pause_duration
        
    def get_progress_percentage(self):
        """Get progress as percentage."""
        if self.original_time == 0:
            return 100
        return ((self.original_time - self.current_time) / self.original_time) * 100
        
    def complete_session(self):
        """Mark current session as complete."""
        self.sessions_completed += 1
        if self.session_type == "work":
            self.total_focus_time += self.original_time
            self.cycle_count += 1
            
    def get_next_session_type(self):
        """Determine next session type."""
        if self.session_type == "work":
            if self.cycle_count % self.cycles_until_long_break == 0:
                return "long_break"
            return "short_break"
        return "work"
        
    def set_session_type(self, session_type):
        """Set current session type."""
        self.session_type = session_type
        if session_type == "work":
            self.current_time = self.work_duration
            self.original_time = self.work_duration
        elif session_type == "short_break":
            self.current_time = self.short_break_duration
            self.original_time = self.short_break_duration
        elif session_type == "long_break":
            self.current_time = self.long_break_duration
            self.original_time = self.long_break_duration
            
    def get_formatted_time(self):
        """Get formatted time string."""
        minutes = self.current_time // 60
        seconds = self.current_time % 60
        return f"{minutes:02d}:{seconds:02d}"
        
    def get_session_stats(self):
        """Get session statistics."""
        return {
            'sessions_completed': self.sessions_completed,
            'total_focus_time': self.total_focus_time,
            'current_cycle': self.cycle_count,
            'session_type': self.session_type
        }


class TestTimerModel:
    """Test suite for TimerModel class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.timer_model = MockTimerModel()
        
    def test_initialization(self):
        """Test timer model initialization."""
        assert self.timer_model.current_time == 25 * 60
        assert self.timer_model.original_time == 25 * 60
        assert not self.timer_model.is_running
        assert not self.timer_model.is_paused
        assert self.timer_model.session_type == "work"
        assert self.timer_model.cycle_count == 0
        
    def test_start_timer(self):
        """Test starting the timer."""
        self.timer_model.start()
        assert self.timer_model.is_running
        assert not self.timer_model.is_paused
        assert self.timer_model.start_time is not None
        
    def test_pause_timer(self):
        """Test pausing the timer."""
        self.timer_model.start()
        self.timer_model.pause()
        assert self.timer_model.is_paused
        assert self.timer_model.pause_time is not None
        
    def test_resume_timer(self):
        """Test resuming the timer."""
        self.timer_model.start()
        self.timer_model.pause()
        time.sleep(0.1)  # Small delay to test pause duration
        self.timer_model.resume()
        assert not self.timer_model.is_paused
        assert self.timer_model.pause_time is None
        assert self.timer_model.total_pause_duration > 0
        
    def test_stop_timer(self):
        """Test stopping the timer."""
        self.timer_model.start()
        self.timer_model.stop()
        assert not self.timer_model.is_running
        assert not self.timer_model.is_paused
        assert self.timer_model.start_time is None
        assert self.timer_model.total_pause_duration == 0
        
    def test_reset_timer(self):
        """Test resetting the timer."""
        self.timer_model.start()
        self.timer_model.tick()
        self.timer_model.reset()
        assert self.timer_model.current_time == self.timer_model.original_time
        assert not self.timer_model.is_running
        
    def test_tick_function(self):
        """Test timer tick functionality."""
        initial_time = self.timer_model.current_time
        self.timer_model.start()
        self.timer_model.tick()
        assert self.timer_model.current_time == initial_time - 1
        
    def test_tick_when_paused(self):
        """Test tick doesn't decrement when paused."""
        self.timer_model.start()
        self.timer_model.pause()
        initial_time = self.timer_model.current_time
        self.timer_model.tick()
        assert self.timer_model.current_time == initial_time
        
    def test_tick_when_stopped(self):
        """Test tick doesn't decrement when stopped."""
        initial_time = self.timer_model.current_time
        self.timer_model.tick()
        assert self.timer_model.current_time == initial_time
        
    def test_is_finished(self):
        """Test timer finished detection."""
        assert not self.timer_model.is_finished()
        self.timer_model.current_time = 0
        assert self.timer_model.is_finished()
        
    def test_get_remaining_time(self):
        """Test getting remaining time."""
        assert self.timer_model.get_remaining_time() == 25 * 60
        self.timer_model.current_time = 300  # 5 minutes
        assert self.timer_model.get_remaining_time() == 300
        
    def test_get_elapsed_time(self):
        """Test getting elapsed time."""
        assert self.timer_model.get_elapsed_time() == 0
        self.timer_model.start()
        time.sleep(0.1)
        elapsed = self.timer_model.get_elapsed_time()
        assert elapsed > 0
        assert elapsed < 1  # Should be less than 1 second
        
    def test_get_progress_percentage(self):
        """Test getting progress percentage."""
        assert self.timer_model.get_progress_percentage() == 0
        self.timer_model.current_time = 15 * 60  # 15 minutes remaining
        progress = self.timer_model.get_progress_percentage()
        expected = ((25 * 60 - 15 * 60) / (25 * 60)) * 100
        assert progress == expected
        
    def test_complete_session(self):
        """Test completing a session."""
        initial_sessions = self.timer_model.sessions_completed
        initial_focus_time = self.timer_model.total_focus_time
        self.timer_model.complete_session()
        assert self.timer_model.sessions_completed == initial_sessions + 1
        assert self.timer_model.total_focus_time == initial_focus_time + self.timer_model.original_time
        assert self.timer_model.cycle_count == 1
        
    def test_get_next_session_type_work_to_short_break(self):
        """Test getting next session type from work to short break."""
        self.timer_model.session_type = "work"
        self.timer_model.cycle_count = 1
        assert self.timer_model.get_next_session_type() == "short_break"
        
    def test_get_next_session_type_work_to_long_break(self):
        """Test getting next session type from work to long break."""
        self.timer_model.session_type = "work"
        self.timer_model.cycle_count = 4
        assert self.timer_model.get_next_session_type() == "long_break"
        
    def test_get_next_session_type_break_to_work(self):
        """Test getting next session type from break to work."""
        self.timer_model.session_type = "short_break"
        assert self.timer_model.get_next_session_type() == "work"
        
    def test_set_session_type_work(self):
        """Test setting session type to work."""
        self.timer_model.set_session_type("work")
        assert self.timer_model.session_type == "work"
        assert self.timer_model.current_time == self.timer_model.work_duration
        
    def test_set_session_type_short_break(self):
        """Test setting session type to short break."""
        self.timer_model.set_session_type("short_break")
        assert self.timer_model.session_type == "short_break"
        assert self.timer_model.current_time == self.timer_model.short_break_duration
        
    def test_set_session_type_long_break(self):
        """Test setting session type to long break."""
        self.timer_model.set_session_type("long_break")
        assert self.timer_model.session_type == "long_break"
        assert self.timer_model.current_time == self.timer_model.long_break_duration
        
    def test_get_formatted_time(self):
        """Test getting formatted time string."""
        self.timer_model.current_time = 25 * 60  # 25:00
        assert self.timer_model.get_formatted_time() == "25:00"
        
        self.timer_model.current_time = 5 * 60 + 30  # 5:30
        assert self.timer_model.get_formatted_time() == "05:30"
        
        self.timer_model.current_time = 65  # 1:05
        assert self.timer_model.get_formatted_time() == "01:05"
        
    def test_get_session_stats(self):
        """Test getting session statistics."""
        stats = self.timer_model.get_session_stats()
        assert stats['sessions_completed'] == 0
        assert stats['total_focus_time'] == 0
        assert stats['current_cycle'] == 0
        assert stats['session_type'] == "work"
        
    def test_multiple_session_completion(self):
        """Test completing multiple sessions."""
        for i in range(3):
            self.timer_model.complete_session()
        stats = self.timer_model.get_session_stats()
        assert stats['sessions_completed'] == 3
        assert stats['total_focus_time'] == 3 * self.timer_model.work_duration
        assert stats['current_cycle'] == 3
        
    def test_pause_resume_duration_tracking(self):
        """Test pause and resume duration tracking."""
        self.timer_model.start()
        time.sleep(0.1)
        self.timer_model.pause()
        time.sleep(0.1)
        self.timer_model.resume()
        assert self.timer_model.total_pause_duration > 0
        
    def test_elapsed_time_with_pause(self):
        """Test elapsed time calculation with pause."""
        self.timer_model.start()
        time.sleep(0.1)
        self.timer_model.pause()
        time.sleep(0.1)
        elapsed_paused = self.timer_model.get_elapsed_time()
        self.timer_model.resume()
        elapsed_resumed = self.timer_model.get_elapsed_time()
        # Elapsed time should be similar before and after pause
        assert abs(elapsed_paused - elapsed_resumed) < 0.2
        
    def test_timer_finish_condition(self):
        """Test timer finishing condition."""
        self.timer_model.start()
        self.timer_model.current_time = 1
        self.timer_model.tick()
        assert self.timer_model.is_finished()
        
    def test_progress_calculation_edge_cases(self):
        """Test progress calculation edge cases."""
        # Test with zero original time
        self.timer_model.original_time = 0
        assert self.timer_model.get_progress_percentage() == 100
        
        # Test with completed timer
        self.timer_model.original_time = 1500
        self.timer_model.current_time = 0
        assert self.timer_model.get_progress_percentage() == 100