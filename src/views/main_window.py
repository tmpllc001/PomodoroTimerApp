#!/usr/bin/env python3
"""
Main Window for Pomodoro Timer Application
Implements transparent window with always-on-top functionality.
"""

import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QApplication)
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont, QPalette, QMouseEvent

from .components.timer_display import TimerDisplay
from .components.control_panel import ControlPanel


class MainWindow(QMainWindow):
    """Main transparent window for Pomodoro Timer."""
    
    # Bridge communication signals
    start_requested = pyqtSignal()
    pause_requested = pyqtSignal()
    reset_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.drag_position = QPoint()
        self.timer_display = None
        self.control_panel = None
        self.setup_ui()
        self.setup_window_properties()
        
    def setup_ui(self):
        """Setup the main UI layout."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Create timer display
        self.timer_display = TimerDisplay()
        main_layout.addWidget(self.timer_display)
        
        # Create control panel
        self.control_panel = ControlPanel()
        main_layout.addWidget(self.control_panel)
        
        # Connect internal UI signals
        self.control_panel.start_clicked.connect(self.timer_display.start_timer)
        self.control_panel.pause_clicked.connect(self.timer_display.pause_timer)
        self.control_panel.reset_clicked.connect(self.timer_display.reset_timer)
        
        # Connect bridge signals for backend communication
        self.control_panel.start_clicked.connect(self.start_requested)
        self.control_panel.pause_clicked.connect(self.pause_requested)
        self.control_panel.reset_clicked.connect(self.reset_requested)
        
    def setup_window_properties(self):
        """Setup window properties for transparency and always-on-top."""
        # Set window flags
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Set window size
        self.setFixedSize(300, 200)
        
        # Set window transparency
        self.setWindowOpacity(0.8)
        
        # Set background color
        self.setStyleSheet("""
            QMainWindow {
                background-color: rgba(30, 30, 30, 200);
                border: 2px solid rgba(100, 100, 100, 150);
                border-radius: 10px;
            }
        """)
        
        # Enable mouse tracking for drag functionality
        self.setMouseTracking(True)
        
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for window dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for window dragging."""
        if event.buttons() == Qt.MouseButton.LeftButton and not self.drag_position.isNull():
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release for window dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = QPoint()
            event.accept()
    
    def paintEvent(self, event):
        """Custom paint event for enhanced transparency effects."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background with gradient
        gradient_color = QColor(30, 30, 30, 200)
        painter.fillRect(self.rect(), gradient_color)
        
        super().paintEvent(event)
    
    def update_timer_display(self, time_remaining):
        """Update timer display from external source (UIBridge)."""
        if self.timer_display:
            self.timer_display.time_remaining = time_remaining
            self.timer_display.update_display()
    
    def set_timer_state(self, is_running):
        """Update UI state based on timer state."""
        if self.control_panel:
            self.control_panel.set_timer_state(is_running)
    
    def get_timer_display(self):
        """Get timer display component for external access."""
        return self.timer_display
    
    def get_control_panel(self):
        """Get control panel component for external access."""
        return self.control_panel