#!/usr/bin/env python3
"""
Pomodoro Timer Application
Main entry point for the application.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Pomodoro Timer")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("PomodoroTeam")
    
    # TODO: Import and create main window
    # from views.main_window import MainWindow
    # window = MainWindow()
    # window.show()
    
    print("Pomodoro Timer App - Development Version")
    print("Application initialized successfully!")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())