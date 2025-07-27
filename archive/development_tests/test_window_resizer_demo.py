#!/usr/bin/env python3
"""
Window Resizer Demo and Test
Phase 2 feature demonstration.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QLabel
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont

from views.resizable_window import ResizableWindow
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WindowResizerDemo(QWidget):
    """Demo window to test window resizer functionality."""
    
    def __init__(self):
        super().__init__()
        self.resizable_window = None
        self.setup_ui()
        self.setup_demo_window()
        
    def setup_ui(self):
        """Setup demo control UI."""
        self.setWindowTitle("Window Resizer Demo Controller")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title = QLabel("Window Resizer Demo")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Status
        self.status_label = QLabel("Status: Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Control buttons
        button_layout = QVBoxLayout()
        
        # Mode buttons
        mode_layout = QHBoxLayout()
        
        self.work_button = QPushButton("Work Mode (200x100)")
        self.work_button.clicked.connect(self.set_work_mode)
        mode_layout.addWidget(self.work_button)
        
        self.break_button = QPushButton("Break Mode (600x400)")
        self.break_button.clicked.connect(self.set_break_mode)
        mode_layout.addWidget(self.break_button)
        
        self.default_button = QPushButton("Default Mode (450x350)")
        self.default_button.clicked.connect(self.set_default_mode)
        mode_layout.addWidget(self.default_button)
        
        button_layout.addLayout(mode_layout)
        
        # Toggle buttons
        toggle_layout = QHBoxLayout()
        
        self.auto_resize_button = QPushButton("Disable Auto Resize")
        self.auto_resize_button.clicked.connect(self.toggle_auto_resize)
        toggle_layout.addWidget(self.auto_resize_button)
        
        self.center_button = QPushButton("Center Window")
        self.center_button.clicked.connect(self.center_window)
        toggle_layout.addWidget(self.center_button)
        
        button_layout.addLayout(toggle_layout)
        
        # Test buttons
        test_layout = QHBoxLayout()
        
        self.simulate_session_button = QPushButton("Simulate Session")
        self.simulate_session_button.clicked.connect(self.simulate_session)
        test_layout.addWidget(self.simulate_session_button)
        
        self.reset_button = QPushButton("Reset Demo")
        self.reset_button.clicked.connect(self.reset_demo)
        test_layout.addWidget(self.reset_button)
        
        button_layout.addLayout(test_layout)
        
        layout.addLayout(button_layout)
        
        # Info text
        info_text = QLabel("""
Instructions:
1. Click mode buttons to test window resizing
2. Work mode: Small window, top-right corner
3. Break mode: Large window, center screen
4. Default mode: Medium window, center screen
5. Toggle auto-resize to disable/enable
6. Simulate session to test automatic workflow
        """)
        info_text.setWordWrap(True)
        layout.addWidget(info_text)
        
    def setup_demo_window(self):
        """Setup the resizable window for demo."""
        self.resizable_window = ResizableWindow()
        self.resizable_window.show()
        
        # Connect signals
        self.resizable_window.resize_mode_changed.connect(self.on_resize_mode_changed)
        
        self.update_status("Demo window created")
        logger.info("Demo window setup complete")
        
    def set_work_mode(self):
        """Set window to work mode."""
        if self.resizable_window:
            self.resizable_window.resize_to_work_mode()
            self.update_status("Work mode activated")
            
    def set_break_mode(self):
        """Set window to break mode."""
        if self.resizable_window:
            self.resizable_window.resize_to_break_mode()
            self.update_status("Break mode activated")
            
    def set_default_mode(self):
        """Set window to default mode."""
        if self.resizable_window:
            self.resizable_window.resize_to_default_mode()
            self.update_status("Default mode activated")
            
    def toggle_auto_resize(self):
        """Toggle auto resize on/off."""
        if self.resizable_window:
            current_state = self.resizable_window.is_auto_resize_enabled()
            self.resizable_window.toggle_auto_resize(not current_state)
            
            if current_state:
                self.auto_resize_button.setText("Enable Auto Resize")
                self.update_status("Auto resize disabled")
            else:
                self.auto_resize_button.setText("Disable Auto Resize")
                self.update_status("Auto resize enabled")
                
    def center_window(self):
        """Center the window."""
        if self.resizable_window:
            self.resizable_window.center_window()
            self.update_status("Window centered")
            
    def simulate_session(self):
        """Simulate a work session workflow."""
        if not self.resizable_window:
            return
            
        self.update_status("Simulating session...")
        logger.info("Starting session simulation")
        
        # Start work session
        self.resizable_window.on_session_started()
        
        # Simulate timer finishing after 3 seconds
        QTimer.singleShot(3000, self.simulate_timer_finish)
        
    def simulate_timer_finish(self):
        """Simulate timer finishing."""
        if self.resizable_window:
            self.resizable_window.on_timer_finished()
            self.update_status("Session simulation complete")
            logger.info("Session simulation finished")
            
    def reset_demo(self):
        """Reset demo to initial state."""
        if self.resizable_window:
            self.resizable_window.resize_to_default_mode()
            self.resizable_window.toggle_auto_resize(True)
            self.auto_resize_button.setText("Disable Auto Resize")
            self.update_status("Demo reset to default")
            
    def on_resize_mode_changed(self, mode):
        """Handle resize mode change."""
        self.update_status(f"Resize mode changed to: {mode}")
        
    def update_status(self, message):
        """Update status label."""
        self.status_label.setText(f"Status: {message}")
        logger.info(f"Status: {message}")
        
    def closeEvent(self, event):
        """Handle close event."""
        if self.resizable_window:
            self.resizable_window.close()
        event.accept()


def main():
    """Main demo application."""
    print("🚀 Window Resizer Demo Starting...")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Window Resizer Demo")
    
    try:
        demo = WindowResizerDemo()
        demo.show()
        
        print("✅ Demo started successfully!")
        print("📋 Use the control window to test window resizing")
        print("🎯 Features to test:")
        print("   - Work mode: 200x100px, top-right")
        print("   - Break mode: 600x400px, center")
        print("   - Default mode: 450x350px, center")
        print("   - Auto resize toggle")
        print("   - Session simulation")
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    # WSL/Linux GUI support
    if 'DISPLAY' not in os.environ:
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        print("⚠️  No display detected, running in offscreen mode")
    
    sys.exit(main())