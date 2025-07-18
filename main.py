#!/usr/bin/env python3
"""
Pomodoro Timer Application
Main entry point for the application.
"""

import sys
import os
import signal
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, QThread, pyqtSignal

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 音声システム初期化チェック
AUDIO_AVAILABLE = False
try:
    import pygame
    pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
    print("✅ 音声システム初期化成功")
except Exception as e:
    print(f"⚠️  音声システム利用不可 (WSL/Linux環境): {e}")
    print("🔇 音声機能を無効化して続行します")

# Import backend components
try:
    from controllers.timer_controller import TimerController
    from models.timer_model import TimerState, SessionType
except ImportError:
    # 相対インポート対応
    from src.controllers.timer_controller import TimerController
    from src.models.timer_model import TimerState, SessionType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pomodoro_app.log'),
        logging.StreamHandler()
    ]
)


class PomodoroApplication(QApplication):
    """Enhanced QApplication with integrated timer controller."""
    
    def __init__(self, args):
        super().__init__(args)
        self.timer_controller = None
        self.main_window = None
        self.bridge = None
        self.logger = logging.getLogger(__name__)
        
        # Set application properties
        self.setApplicationName("Pomodoro Timer")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("PomodoroTeam")
        self.setOrganizationDomain("pomodorotimer.app")
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Timer for processing Qt events during signal handling
        self.signal_timer = QTimer()
        self.signal_timer.timeout.connect(lambda: None)
        self.signal_timer.start(100)
        
    def initialize_backend(self):
        """Initialize the timer controller and backend systems."""
        try:
            self.timer_controller = TimerController()
            
            # 音声システムが利用不可の場合は音声を無効化
            if not AUDIO_AVAILABLE:
                self.timer_controller.set_sound_enabled(False)
                self.logger.info("Audio system disabled due to environment limitations")
            
            self.logger.info("Timer controller initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize timer controller: {e}")
            return False
            
    def initialize_ui(self):
        """Initialize the user interface."""
        try:
            # UIインポートの安全な実行
            try:
                from views.main_window import MainWindow
                from bridge.ui_bridge import UIBridge
            except ImportError:
                # 相対インポート対応
                from src.views.main_window_template import MainWindow
                from src.bridge.ui_bridge import UIBridge
            
            self.main_window = MainWindow()
            self.bridge = UIBridge(self.timer_controller, self.main_window)
            
            self.logger.info("UI initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize UI: {e}")
            self.logger.error(f"GUI環境が利用できない可能性があります")
            return False
            
    def signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.cleanup()
        self.quit()
        
    def cleanup(self):
        """Clean up resources before shutdown."""
        try:
            if self.timer_controller:
                self.timer_controller.cleanup()
                self.logger.info("Timer controller cleaned up")
                
            if self.bridge:
                self.bridge.cleanup()
                self.logger.info("UI bridge cleaned up")
                
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


def setup_exception_handler():
    """Setup global exception handler."""
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logging.error(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
    
    sys.excepthook = handle_exception


def main():
    """Main application entry point."""
    setup_exception_handler()
    
    app = PomodoroApplication(sys.argv)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize backend first
        if not app.initialize_backend():
            logger.error("Failed to initialize backend, exiting")
            return 1
            
        # Initialize UI
        if not app.initialize_ui():
            logger.error("Failed to initialize UI, exiting")
            return 1
            
        # Show main window
        app.main_window.show()
        
        logger.info("Pomodoro Timer App - Transparent UI Version")
        logger.info("Application initialized successfully!")
        
        # Start the application event loop
        result = app.exec()
        
        # Cleanup
        app.cleanup()
        
        return result
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())