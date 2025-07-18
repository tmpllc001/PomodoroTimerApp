"""
UI Bridge - Connects UI components with backend logic
"""

import logging
from typing import Optional, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QWidget

from ..controllers.timer_controller import TimerController
from ..models.timer_model import TimerState, SessionType


class UIBridge(QObject):
    """Bridge class connecting UI components with backend timer controller."""
    
    # Signals for UI updates
    timer_updated = pyqtSignal(dict)
    state_changed = pyqtSignal(TimerState)
    session_completed = pyqtSignal(SessionType)
    session_stats_updated = pyqtSignal(dict)
    
    def __init__(self, timer_controller: TimerController, main_window: QWidget):
        super().__init__()
        self.timer_controller = timer_controller
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        
        # Update timer for UI refresh
        self.ui_update_timer = QTimer()
        self.ui_update_timer.timeout.connect(self._update_ui_timer)
        self.ui_update_timer.start(100)  # Update every 100ms for smooth UI
        
        # Setup backend callbacks
        self._setup_backend_callbacks()
        
        # Connect UI signals
        self._connect_ui_signals()
        
        self.logger.info("UI Bridge initialized")
        
    def _setup_backend_callbacks(self):
        """Setup callbacks from backend to UI."""
        self.timer_controller.on_timer_update = self._handle_timer_update
        self.timer_controller.on_state_change = self._handle_state_change
        self.timer_controller.on_session_complete = self._handle_session_complete
        
    def _connect_ui_signals(self):
        """Connect UI component signals to backend methods."""
        try:
            # Connect timer control signals
            if hasattr(self.main_window, 'start_button'):
                self.main_window.start_button.clicked.connect(self.start_timer)
            if hasattr(self.main_window, 'pause_button'):
                self.main_window.pause_button.clicked.connect(self.pause_timer)
            if hasattr(self.main_window, 'stop_button'):
                self.main_window.stop_button.clicked.connect(self.stop_timer)
            if hasattr(self.main_window, 'reset_button'):
                self.main_window.reset_button.clicked.connect(self.reset_timer)
            if hasattr(self.main_window, 'skip_button'):
                self.main_window.skip_button.clicked.connect(self.skip_session)
                
            # Connect settings signals
            if hasattr(self.main_window, 'volume_slider'):
                self.main_window.volume_slider.valueChanged.connect(self.set_volume)
            if hasattr(self.main_window, 'sound_toggle'):
                self.main_window.sound_toggle.toggled.connect(self.toggle_sound)
                
            self.logger.info("UI signals connected")
            
        except Exception as e:
            self.logger.warning(f"Some UI signals could not be connected: {e}")
            
    def _update_ui_timer(self):
        """Update UI with current timer information."""
        try:
            timer_info = self.timer_controller.get_timer_info()
            self.timer_updated.emit(timer_info)
        except Exception as e:
            self.logger.error(f"Error updating UI timer: {e}")
            
    def _handle_timer_update(self, timer_info: dict):
        """Handle timer update from backend."""
        self.timer_updated.emit(timer_info)
        
    def _handle_state_change(self, state: TimerState):
        """Handle state change from backend."""
        self.state_changed.emit(state)
        self.logger.info(f"Timer state changed to: {state}")
        
    def _handle_session_complete(self, session_type: SessionType):
        """Handle session completion from backend."""
        self.session_completed.emit(session_type)
        self.logger.info(f"Session completed: {session_type}")
        
        # Update session stats
        stats = self.timer_controller.get_session_stats()
        self.session_stats_updated.emit(stats)
        
    # Timer control methods
    def start_timer(self):
        """Start the timer."""
        try:
            self.timer_controller.start_timer()
            self.logger.info("Timer started via UI")
        except Exception as e:
            self.logger.error(f"Error starting timer: {e}")
            
    def pause_timer(self):
        """Pause the timer."""
        try:
            self.timer_controller.pause_timer()
            self.logger.info("Timer paused via UI")
        except Exception as e:
            self.logger.error(f"Error pausing timer: {e}")
            
    def stop_timer(self):
        """Stop the timer."""
        try:
            self.timer_controller.stop_timer()
            self.logger.info("Timer stopped via UI")
        except Exception as e:
            self.logger.error(f"Error stopping timer: {e}")
            
    def reset_timer(self):
        """Reset the timer."""
        try:
            self.timer_controller.reset_timer()
            self.logger.info("Timer reset via UI")
        except Exception as e:
            self.logger.error(f"Error resetting timer: {e}")
            
    def skip_session(self):
        """Skip current session."""
        try:
            self.timer_controller.skip_session()
            self.logger.info("Session skipped via UI")
        except Exception as e:
            self.logger.error(f"Error skipping session: {e}")
            
    # Settings methods
    def set_volume(self, volume: int):
        """Set audio volume (0-100)."""
        try:
            volume_float = volume / 100.0
            self.timer_controller.set_volume(volume_float)
            self.logger.info(f"Volume set to {volume}%")
        except Exception as e:
            self.logger.error(f"Error setting volume: {e}")
            
    def toggle_sound(self, enabled: bool):
        """Toggle sound on/off."""
        try:
            self.timer_controller.set_sound_enabled(enabled)
            self.logger.info(f"Sound {'enabled' if enabled else 'disabled'}")
        except Exception as e:
            self.logger.error(f"Error toggling sound: {e}")
            
    def set_work_duration(self, minutes: int):
        """Set work session duration."""
        try:
            current_settings = self.get_current_durations()
            self.timer_controller.set_durations(
                minutes * 60,
                current_settings['short_break'],
                current_settings['long_break'],
                current_settings['long_break_interval']
            )
            self.logger.info(f"Work duration set to {minutes} minutes")
        except Exception as e:
            self.logger.error(f"Error setting work duration: {e}")
            
    def set_short_break_duration(self, minutes: int):
        """Set short break duration."""
        try:
            current_settings = self.get_current_durations()
            self.timer_controller.set_durations(
                current_settings['work'],
                minutes * 60,
                current_settings['long_break'],
                current_settings['long_break_interval']
            )
            self.logger.info(f"Short break duration set to {minutes} minutes")
        except Exception as e:
            self.logger.error(f"Error setting short break duration: {e}")
            
    def set_long_break_duration(self, minutes: int):
        """Set long break duration."""
        try:
            current_settings = self.get_current_durations()
            self.timer_controller.set_durations(
                current_settings['work'],
                current_settings['short_break'],
                minutes * 60,
                current_settings['long_break_interval']
            )
            self.logger.info(f"Long break duration set to {minutes} minutes")
        except Exception as e:
            self.logger.error(f"Error setting long break duration: {e}")
            
    def set_long_break_interval(self, interval: int):
        """Set long break interval."""
        try:
            current_settings = self.get_current_durations()
            self.timer_controller.set_durations(
                current_settings['work'],
                current_settings['short_break'],
                current_settings['long_break'],
                interval
            )
            self.logger.info(f"Long break interval set to {interval}")
        except Exception as e:
            self.logger.error(f"Error setting long break interval: {e}")
            
    # Data retrieval methods
    def get_timer_info(self) -> dict:
        """Get current timer information."""
        return self.timer_controller.get_timer_info()
        
    def get_session_stats(self) -> dict:
        """Get session statistics."""
        return self.timer_controller.get_session_stats()
        
    def get_today_sessions(self) -> list:
        """Get today's sessions."""
        return self.timer_controller.get_today_sessions()
        
    def get_weekly_stats(self) -> dict:
        """Get weekly statistics."""
        return self.timer_controller.get_weekly_stats()
        
    def get_current_durations(self) -> dict:
        """Get current duration settings."""
        return {
            'work': self.timer_controller.timer_model.work_duration,
            'short_break': self.timer_controller.timer_model.short_break_duration,
            'long_break': self.timer_controller.timer_model.long_break_duration,
            'long_break_interval': self.timer_controller.timer_model.long_break_interval
        }
        
    def get_current_volume(self) -> int:
        """Get current volume (0-100)."""
        return int(self.timer_controller.get_volume() * 100)
        
    def is_sound_enabled(self) -> bool:
        """Check if sound is enabled."""
        return self.timer_controller.is_sound_enabled()
        
    def format_time(self, seconds: int) -> str:
        """Format time in MM:SS format."""
        return self.timer_controller.timer_model.format_time(seconds)
        
    def get_session_type_display(self, session_type: SessionType) -> str:
        """Get display text for session type."""
        type_mapping = {
            SessionType.WORK: "Work Session",
            SessionType.SHORT_BREAK: "Short Break",
            SessionType.LONG_BREAK: "Long Break"
        }
        return type_mapping.get(session_type, "Unknown")
        
    def get_state_display(self, state: TimerState) -> str:
        """Get display text for timer state."""
        state_mapping = {
            TimerState.STOPPED: "Stopped",
            TimerState.RUNNING: "Running",
            TimerState.PAUSED: "Paused"
        }
        return state_mapping.get(state, "Unknown")
        
    def test_sound(self):
        """Test sound playback."""
        try:
            self.timer_controller.audio_manager.play_notification_sound()
            self.logger.info("Sound test triggered")
        except Exception as e:
            self.logger.error(f"Error testing sound: {e}")
            
    def export_session_data(self, file_path: str) -> bool:
        """Export session data to file."""
        try:
            import json
            from datetime import datetime
            
            data = {
                'export_date': datetime.now().isoformat(),
                'sessions': self.timer_controller.session_model.export_sessions(),
                'stats': self.get_session_stats()
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            self.logger.info(f"Session data exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting session data: {e}")
            return False
            
    def cleanup(self):
        """Clean up resources."""
        try:
            self.ui_update_timer.stop()
            self.logger.info("UI Bridge cleaned up")
        except Exception as e:
            self.logger.error(f"Error during UI bridge cleanup: {e}")
            
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()