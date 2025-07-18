#!/usr/bin/env python3
"""
Resizable Window Component for Pomodoro Timer Application
Enhanced MainWindow with automatic resizing capabilities.
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QApplication, QGroupBox)
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont, QPalette, QMouseEvent

try:
    from ..features.window_resizer import WindowResizer
    from .components.timer_display import TimerDisplay
    from .components.control_panel import ControlPanel
except ImportError:
    # Alternative import for direct execution
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from features.window_resizer import WindowResizer
    from views.components.timer_display import TimerDisplay
    from views.components.control_panel import ControlPanel
import logging


class ResizableWindow(QMainWindow):
    """Enhanced MainWindow with automatic resizing capabilities."""
    
    # Bridge communication signals
    start_requested = pyqtSignal()
    pause_requested = pyqtSignal()
    reset_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    
    # Resizer signals
    resize_mode_changed = pyqtSignal(str)  # work, break, default
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.drag_position = QPoint()
        self.timer_display = None
        self.control_panel = None
        self.window_resizer = None
        
        # Current session state
        self.current_session_type = 'default'
        self.is_work_session = False
        
        self.setup_ui()
        self.setup_window_properties()
        self.setup_window_resizer()
        
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
        
        # Connect timer state changes
        self.timer_display.timer_finished.connect(self.on_timer_finished)
        self.control_panel.start_clicked.connect(self.on_session_started)
        
    def setup_window_properties(self):
        """Setup window properties for transparency and always-on-top."""
        # Set window flags
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Set initial window size (default)
        self.setFixedSize(450, 350)
        
        # Set window transparency
        self.setWindowOpacity(0.9)
        
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
        
    def setup_window_resizer(self):
        """Setup the automatic window resizer."""
        self.window_resizer = WindowResizer(self)
        self.resize_mode_changed.connect(self.window_resizer.resize_window)
        
        self.logger.info("Window resizer initialized")
        
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
    
    def on_session_started(self):
        """Handle session start - switch to work mode."""
        self.is_work_session = True
        self.current_session_type = 'work'
        self.resize_mode_changed.emit('work')
        self.logger.info("Session started - switched to work mode")
        
    def on_timer_finished(self):
        """Handle timer finished - switch to break mode."""
        if self.is_work_session:
            self.is_work_session = False
            self.current_session_type = 'break'
            self.resize_mode_changed.emit('break')
            self.logger.info("Timer finished - switched to break mode")
    
    def set_session_type(self, session_type):
        """Manually set session type and trigger resize."""
        self.current_session_type = session_type
        self.is_work_session = (session_type == 'work')
        self.resize_mode_changed.emit(session_type)
        self.logger.info(f"Session type set to: {session_type}")
    
    def toggle_auto_resize(self, enabled):
        """Enable or disable automatic window resizing."""
        if self.window_resizer:
            self.window_resizer.toggle_auto_resize(enabled)
            self.logger.info(f"Auto resize {'enabled' if enabled else 'disabled'}")
    
    def is_auto_resize_enabled(self):
        """Check if auto resize is enabled."""
        return self.window_resizer.is_auto_resize_enabled() if self.window_resizer else False
    
    def get_current_session_type(self):
        """Get current session type."""
        return self.current_session_type
    
    def resize_to_work_mode(self):
        """Manually resize to work mode."""
        self.set_session_type('work')
    
    def resize_to_break_mode(self):
        """Manually resize to break mode."""
        self.set_session_type('break')
    
    def resize_to_default_mode(self):
        """Manually resize to default mode."""
        self.set_session_type('default')
    
    def center_window(self):
        """Center the window on screen."""
        if self.window_resizer:
            self.window_resizer.center_window()
    
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
    
    def get_window_resizer(self):
        """Get window resizer component for external access."""
        return self.window_resizer
    
    def get_resize_config(self):
        """Get current resize configuration."""
        if self.window_resizer:
            return {
                'current_session_type': self.current_session_type,
                'is_work_session': self.is_work_session,
                'auto_resize_enabled': self.window_resizer.is_auto_resize_enabled(),
                'current_size': self.window_resizer.get_current_size()
            }
        return None
    
    def cleanup(self):
        """Clean up resources."""
        if self.window_resizer:
            # Stop any ongoing animations
            if hasattr(self.window_resizer, 'resize_animation') and self.window_resizer.resize_animation:
                self.window_resizer.resize_animation.stop()
            if hasattr(self.window_resizer, 'opacity_animation') and self.window_resizer.opacity_animation:
                self.window_resizer.opacity_animation.stop()
        
        self.logger.info("ResizableWindow cleaned up")
    
    def closeEvent(self, event):
        """Handle close event."""
        self.cleanup()
        event.accept()