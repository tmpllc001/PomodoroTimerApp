#!/usr/bin/env python3
"""
Music Controls UI Component for Pomodoro Timer
Provides UI controls for music presets functionality.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QSlider, QLabel, QComboBox, QGroupBox, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

# Import music presets
sys.path.append(str(Path(__file__).parent))
from music_presets import get_music_presets, SessionType


class MusicControlsWidget(QWidget):
    """Music controls widget for the Pomodoro Timer."""
    
    # Signals
    session_started = pyqtSignal(str, int)  # session_type, duration
    session_stopped = pyqtSignal()
    volume_changed = pyqtSignal(float)  # volume (0.0-1.0)
    mute_toggled = pyqtSignal(bool)  # is_muted
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.music_presets = get_music_presets()
        self.status_update_timer = QTimer()
        self.status_update_timer.timeout.connect(self.update_status)
        self.status_update_timer.start(1000)  # Update every second
        
        self.setup_ui()
        self.connect_signals()
        self.update_status()
        
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Music controls group
        music_group = QGroupBox("🎵 Music Controls")
        music_layout = QVBoxLayout()
        music_group.setLayout(music_layout)
        
        # Enable/disable music
        self.music_enabled_checkbox = QCheckBox("Enable Background Music")
        self.music_enabled_checkbox.setChecked(True)
        music_layout.addWidget(self.music_enabled_checkbox)
        
        # Session controls
        session_layout = QHBoxLayout()
        
        # Work session button
        self.work_button = QPushButton("🎯 Start Work Session")
        self.work_button.setMinimumHeight(40)
        self.work_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        session_layout.addWidget(self.work_button)
        
        # Break session button
        self.break_button = QPushButton("☕ Start Break Session")
        self.break_button.setMinimumHeight(40)
        self.break_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        session_layout.addWidget(self.break_button)
        
        # Stop session button
        self.stop_button = QPushButton("⏹️ Stop Session")
        self.stop_button.setMinimumHeight(40)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        session_layout.addWidget(self.stop_button)
        
        music_layout.addLayout(session_layout)
        
        # Volume controls
        volume_layout = QHBoxLayout()
        
        volume_label = QLabel("🔊 Volume:")
        volume_layout.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(70)
        self.volume_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.volume_slider.setTickInterval(25)
        volume_layout.addWidget(self.volume_slider)
        
        self.volume_value_label = QLabel("70%")
        self.volume_value_label.setMinimumWidth(40)
        volume_layout.addWidget(self.volume_value_label)
        
        # Mute button
        self.mute_button = QPushButton("🔇 Mute")
        self.mute_button.setMaximumWidth(80)
        self.mute_button.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
            QPushButton:pressed {
                background-color: #424242;
            }
        """)
        volume_layout.addWidget(self.mute_button)
        
        music_layout.addLayout(volume_layout)
        
        # Session pause/resume controls
        control_layout = QHBoxLayout()
        
        self.pause_button = QPushButton("⏸️ Pause")
        self.pause_button.setEnabled(False)
        control_layout.addWidget(self.pause_button)
        
        self.resume_button = QPushButton("▶️ Resume")
        self.resume_button.setEnabled(False)
        control_layout.addWidget(self.resume_button)
        
        music_layout.addLayout(control_layout)
        
        # Status display
        self.status_label = QLabel("🎵 Status: Ready")
        self.status_label.setFont(QFont("Arial", 9))
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #e8f5e8;
                border: 1px solid #4CAF50;
                border-radius: 3px;
                padding: 5px;
                margin-top: 5px;
            }
        """)
        music_layout.addWidget(self.status_label)
        
        layout.addWidget(music_group)
        
        # Set widget properties
        self.setMaximumHeight(300)
        self.setMinimumWidth(400)
        
    def connect_signals(self):
        """Connect UI signals to handlers."""
        # Session control buttons
        self.work_button.clicked.connect(self.start_work_session)
        self.break_button.clicked.connect(self.start_break_session)
        self.stop_button.clicked.connect(self.stop_session)
        
        # Playback controls
        self.pause_button.clicked.connect(self.pause_session)
        self.resume_button.clicked.connect(self.resume_session)
        
        # Volume controls
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        self.mute_button.clicked.connect(self.toggle_mute)
        
        # Music enable/disable
        self.music_enabled_checkbox.stateChanged.connect(self.on_music_enabled_changed)
        
    def start_work_session(self):
        """Start a work session with music."""
        try:
            success = self.music_presets.start_session(SessionType.WORK, 25)
            if success:
                self.session_started.emit("work", 25)
                self.update_button_states(session_active=True)
                print("🎯 Work session started")
            else:
                print("❌ Failed to start work session")
        except Exception as e:
            print(f"💥 Error starting work session: {e}")
            
    def start_break_session(self):
        """Start a break session with music."""
        try:
            success = self.music_presets.start_session(SessionType.BREAK, 5)
            if success:
                self.session_started.emit("break", 5)
                self.update_button_states(session_active=True)
                print("☕ Break session started")
            else:
                print("❌ Failed to start break session")
        except Exception as e:
            print(f"💥 Error starting break session: {e}")
            
    def stop_session(self):
        """Stop current music session."""
        try:
            success = self.music_presets.stop_session()
            if success:
                self.session_stopped.emit()
                self.update_button_states(session_active=False)
                print("⏹️ Session stopped")
            else:
                print("❌ Failed to stop session")
        except Exception as e:
            print(f"💥 Error stopping session: {e}")
            
    def pause_session(self):
        """Pause current music session."""
        try:
            success = self.music_presets.pause_session()
            if success:
                self.update_button_states(session_paused=True)
                print("⏸️ Session paused")
            else:
                print("❌ Failed to pause session")
        except Exception as e:
            print(f"💥 Error pausing session: {e}")
            
    def resume_session(self):
        """Resume paused music session."""
        try:
            success = self.music_presets.resume_session()
            if success:
                self.update_button_states(session_paused=False)
                print("▶️ Session resumed")
            else:
                print("❌ Failed to resume session")
        except Exception as e:
            print(f"💥 Error resuming session: {e}")
            
    def on_volume_changed(self, value):
        """Handle volume slider changes."""
        try:
            volume = value / 100.0
            success = self.music_presets.set_volume(volume)
            if success:
                self.volume_value_label.setText(f"{value}%")
                self.volume_changed.emit(volume)
            else:
                print("❌ Failed to set volume")
        except Exception as e:
            print(f"💥 Error setting volume: {e}")
            
    def toggle_mute(self):
        """Toggle mute state."""
        try:
            is_muted = self.music_presets.toggle_mute()
            self.mute_toggled.emit(is_muted)
            
            if is_muted:
                self.mute_button.setText("🔊 Unmute")
                self.mute_button.setStyleSheet("""
                    QPushButton {
                        background-color: #ff9800;
                        color: white;
                        border: none;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #f57c00;
                    }
                    QPushButton:pressed {
                        background-color: #e65100;
                    }
                """)
            else:
                self.mute_button.setText("🔇 Mute")
                self.mute_button.setStyleSheet("""
                    QPushButton {
                        background-color: #757575;
                        color: white;
                        border: none;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #616161;
                    }
                    QPushButton:pressed {
                        background-color: #424242;
                    }
                """)
        except Exception as e:
            print(f"💥 Error toggling mute: {e}")
            
    def on_music_enabled_changed(self, state):
        """Handle music enabled checkbox changes."""
        try:
            enabled = state == Qt.CheckState.Checked.value
            self.music_presets.enable_music(enabled)
            
            # Enable/disable all music controls
            self.work_button.setEnabled(enabled)
            self.break_button.setEnabled(enabled)
            self.stop_button.setEnabled(enabled)
            self.pause_button.setEnabled(enabled)
            self.resume_button.setEnabled(enabled)
            self.volume_slider.setEnabled(enabled)
            self.mute_button.setEnabled(enabled)
            
            if not enabled:
                # Stop any active session
                self.music_presets.stop_session()
                self.update_button_states(session_active=False)
                
        except Exception as e:
            print(f"💥 Error changing music enabled state: {e}")
            
    def update_button_states(self, session_active: bool = None, session_paused: bool = None):
        """Update button states based on session status."""
        try:
            status = self.music_presets.get_session_status()
            
            if session_active is None:
                session_active = status['is_active']
            if session_paused is None:
                session_paused = not status['is_playing'] and status['is_active']
                
            # Session control buttons
            self.work_button.setEnabled(not session_active)
            self.break_button.setEnabled(not session_active)
            self.stop_button.setEnabled(session_active)
            
            # Playback controls
            self.pause_button.setEnabled(session_active and not session_paused)
            self.resume_button.setEnabled(session_active and session_paused)
            
        except Exception as e:
            print(f"💥 Error updating button states: {e}")
            
    def update_status(self):
        """Update status display."""
        try:
            status = self.music_presets.get_session_status()
            
            if not status['music_enabled']:
                status_text = "🎵 Status: Music Disabled"
                status_color = "#ffecb3"
                border_color = "#ff9800"
            elif status['is_active']:
                session_type = status['session_type']
                if status['is_playing']:
                    if status['is_muted']:
                        status_text = f"🔇 Status: {session_type.title()} session (Muted)"
                        status_color = "#fff3e0"
                        border_color = "#ff9800"
                    else:
                        status_text = f"🎵 Status: {session_type.title()} session playing"
                        status_color = "#e8f5e8"
                        border_color = "#4CAF50"
                else:
                    status_text = f"⏸️ Status: {session_type.title()} session paused"
                    status_color = "#e3f2fd"
                    border_color = "#2196F3"
            else:
                status_text = "🎵 Status: Ready"
                status_color = "#f3e5f5"
                border_color = "#9c27b0"
                
            self.status_label.setText(status_text)
            self.status_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {status_color};
                    border: 1px solid {border_color};
                    border-radius: 3px;
                    padding: 5px;
                    margin-top: 5px;
                }}
            """)
            
            # Update volume slider if not being dragged
            if not self.volume_slider.isSliderDown():
                volume_percent = int(status['volume'] * 100)
                self.volume_slider.setValue(volume_percent)
                self.volume_value_label.setText(f"{volume_percent}%")
                
            # Update mute button
            if status['is_muted']:
                self.mute_button.setText("🔊 Unmute")
            else:
                self.mute_button.setText("🔇 Mute")
                
        except Exception as e:
            print(f"💥 Error updating status: {e}")
            
    def get_music_presets(self):
        """Get the music presets instance."""
        return self.music_presets
        
    def cleanup(self):
        """Clean up resources."""
        try:
            self.status_update_timer.stop()
            self.music_presets.cleanup()
            print("🧹 Music controls cleaned up")
        except Exception as e:
            print(f"💥 Error during cleanup: {e}")


class CompactMusicControls(QWidget):
    """Compact version of music controls for minimal UI."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.music_presets = get_music_presets()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup compact UI."""
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # Work session button
        self.work_button = QPushButton("🎯")
        self.work_button.setMaximumSize(30, 30)
        self.work_button.setToolTip("Start work session with music")
        self.work_button.clicked.connect(self.start_work_session)
        layout.addWidget(self.work_button)
        
        # Break session button
        self.break_button = QPushButton("☕")
        self.break_button.setMaximumSize(30, 30)
        self.break_button.setToolTip("Start break session with music")
        self.break_button.clicked.connect(self.start_break_session)
        layout.addWidget(self.break_button)
        
        # Stop button
        self.stop_button = QPushButton("⏹️")
        self.stop_button.setMaximumSize(30, 30)
        self.stop_button.setToolTip("Stop music session")
        self.stop_button.clicked.connect(self.stop_session)
        layout.addWidget(self.stop_button)
        
        # Volume control
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(70)
        self.volume_slider.setToolTip("Volume")
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        layout.addWidget(self.volume_slider)
        
        # Mute button
        self.mute_button = QPushButton("🔇")
        self.mute_button.setMaximumSize(30, 30)
        self.mute_button.setToolTip("Toggle mute")
        self.mute_button.clicked.connect(self.toggle_mute)
        layout.addWidget(self.mute_button)
        
        self.setMaximumHeight(40)
        
    def start_work_session(self):
        """Start work session."""
        self.music_presets.start_session(SessionType.WORK, 25)
        
    def start_break_session(self):
        """Start break session."""
        self.music_presets.start_session(SessionType.BREAK, 5)
        
    def stop_session(self):
        """Stop session."""
        self.music_presets.stop_session()
        
    def on_volume_changed(self, value):
        """Handle volume changes."""
        self.music_presets.set_volume(value / 100.0)
        
    def toggle_mute(self):
        """Toggle mute."""
        is_muted = self.music_presets.toggle_mute()
        self.mute_button.setText("🔊" if is_muted else "🔇")


# Integration functions for easy import
def create_music_controls_widget(parent=None, compact=False):
    """Create music controls widget."""
    if compact:
        return CompactMusicControls(parent)
    else:
        return MusicControlsWidget(parent)


def integrate_with_main_window(main_window):
    """Integrate music controls with main window."""
    try:
        # Create music controls
        music_controls = create_music_controls_widget(main_window)
        
        # Add to main window layout if it has one
        if hasattr(main_window, 'layout') and main_window.layout():
            main_window.layout().addWidget(music_controls)
        
        # Connect signals if main window has timer controller
        if hasattr(main_window, 'timer_controller'):
            music_controls.session_started.connect(
                lambda session_type, duration: print(f"Timer integration: {session_type} for {duration} min")
            )
            music_controls.session_stopped.connect(
                lambda: print("Timer integration: Session stopped")
            )
            
        return music_controls
        
    except Exception as e:
        print(f"💥 Error integrating music controls: {e}")
        return None