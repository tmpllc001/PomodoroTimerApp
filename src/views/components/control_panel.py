#!/usr/bin/env python3
"""
Control Panel Component for Pomodoro Timer Application
Provides start, pause, and reset buttons for timer control.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon


class ControlPanel(QWidget):
    """Control panel widget with timer control buttons."""
    
    start_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    reset_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the control panel UI."""
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # Create buttons
        self.start_button = QPushButton("Start")
        self.pause_button = QPushButton("Pause")
        self.reset_button = QPushButton("Reset")
        
        # Set button properties
        buttons = [self.start_button, self.pause_button, self.reset_button]
        
        for button in buttons:
            button.setMinimumHeight(35)
            button.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            
        # Set button styles
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 150, 0, 180);
                color: white;
                border: 2px solid rgba(0, 200, 0, 100);
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(0, 180, 0, 220);
                border-color: rgba(0, 255, 0, 150);
            }
            QPushButton:pressed {
                background-color: rgba(0, 120, 0, 200);
            }
            QPushButton:disabled {
                background-color: rgba(100, 100, 100, 100);
                color: rgba(200, 200, 200, 150);
                border-color: rgba(150, 150, 150, 80);
            }
        """)
        
        self.pause_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 150, 0, 180);
                color: white;
                border: 2px solid rgba(255, 200, 0, 100);
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 180, 0, 220);
                border-color: rgba(255, 255, 0, 150);
            }
            QPushButton:pressed {
                background-color: rgba(255, 120, 0, 200);
            }
            QPushButton:disabled {
                background-color: rgba(100, 100, 100, 100);
                color: rgba(200, 200, 200, 150);
                border-color: rgba(150, 150, 150, 80);
            }
        """)
        
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(200, 0, 0, 180);
                color: white;
                border: 2px solid rgba(255, 0, 0, 100);
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(220, 0, 0, 220);
                border-color: rgba(255, 100, 100, 150);
            }
            QPushButton:pressed {
                background-color: rgba(180, 0, 0, 200);
            }
            QPushButton:disabled {
                background-color: rgba(100, 100, 100, 100);
                color: rgba(200, 200, 200, 150);
                border-color: rgba(150, 150, 150, 80);
            }
        """)
        
        # Add buttons to layout
        layout.addWidget(self.start_button)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.reset_button)
        
        # Connect button signals
        self.start_button.clicked.connect(self.on_start_clicked)
        self.pause_button.clicked.connect(self.on_pause_clicked)
        self.reset_button.clicked.connect(self.on_reset_clicked)
        
        # Initial button states
        self.pause_button.setEnabled(False)
        
    def on_start_clicked(self):
        """Handle start button click."""
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.start_clicked.emit()
        
    def on_pause_clicked(self):
        """Handle pause button click."""
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.pause_clicked.emit()
        
    def on_reset_clicked(self):
        """Handle reset button click."""
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.reset_clicked.emit()
        
    def set_timer_state(self, is_running):
        """Update button states based on timer state."""
        self.start_button.setEnabled(not is_running)
        self.pause_button.setEnabled(is_running)
        
    def enable_all_buttons(self):
        """Enable all buttons."""
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(True)
        self.reset_button.setEnabled(True)
        
    def disable_all_buttons(self):
        """Disable all buttons."""
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.reset_button.setEnabled(False)