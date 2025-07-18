#!/usr/bin/env python3
"""
Timer Display Component for Pomodoro Timer Application
Displays countdown timer with digital clock-style font.
"""

from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor


class TimerDisplay(QWidget):
    """Digital timer display widget."""
    
    timer_finished = pyqtSignal()
    time_updated = pyqtSignal(int)  # Emit remaining time for bridge
    
    def __init__(self):
        super().__init__()
        self.time_remaining = 25 * 60  # 25 minutes in seconds
        self.timer = QTimer()
        self.is_running = False
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the timer display UI."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create time label
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Set digital clock font
        font = QFont("Courier New", 36, QFont.Weight.Bold)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.time_label.setFont(font)
        
        # Set text color for dark theme
        self.time_label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                background-color: transparent;
                padding: 10px;
                border: 1px solid rgba(0, 255, 0, 50);
                border-radius: 5px;
            }
        """)
        
        layout.addWidget(self.time_label)
        
        # Connect timer signal
        self.timer.timeout.connect(self.update_display)
        
        # Initial display update
        self.update_display()
        
    def update_display(self):
        """Update the timer display."""
        if self.is_running and self.time_remaining > 0:
            self.time_remaining -= 1
            
        # Format time as MM:SS
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        time_text = f"{minutes:02d}:{seconds:02d}"
        
        self.time_label.setText(time_text)
        
        # Change color based on remaining time
        if self.time_remaining <= 300:  # Last 5 minutes
            self.time_label.setStyleSheet("""
                QLabel {
                    color: #ff6600;
                    background-color: transparent;
                    padding: 10px;
                    border: 1px solid rgba(255, 102, 0, 50);
                    border-radius: 5px;
                }
            """)
        elif self.time_remaining <= 60:  # Last minute
            self.time_label.setStyleSheet("""
                QLabel {
                    color: #ff0000;
                    background-color: transparent;
                    padding: 10px;
                    border: 1px solid rgba(255, 0, 0, 50);
                    border-radius: 5px;
                }
            """)
        
        # Emit time update for bridge
        self.time_updated.emit(self.time_remaining)
        
        # Check if timer finished
        if self.time_remaining <= 0:
            self.is_running = False
            self.timer.stop()
            self.timer_finished.emit()
            
    def start_timer(self):
        """Start the countdown timer."""
        if not self.is_running:
            self.is_running = True
            self.timer.start(1000)  # Update every second
            
    def pause_timer(self):
        """Pause the countdown timer."""
        self.is_running = False
        self.timer.stop()
        
    def reset_timer(self):
        """Reset the timer to 25 minutes."""
        self.is_running = False
        self.timer.stop()
        self.time_remaining = 25 * 60
        
        # Reset color to green
        self.time_label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                background-color: transparent;
                padding: 10px;
                border: 1px solid rgba(0, 255, 0, 50);
                border-radius: 5px;
            }
        """)
        
        self.update_display()
        
    def set_time(self, minutes):
        """Set custom time in minutes."""
        self.time_remaining = minutes * 60
        self.update_display()
        
    def get_remaining_time(self):
        """Get remaining time in seconds."""
        return self.time_remaining
        
    def is_timer_running(self):
        """Check if timer is currently running."""
        return self.is_running