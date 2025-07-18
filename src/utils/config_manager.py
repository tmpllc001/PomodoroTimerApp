"""
Configuration Manager for Pomodoro Timer
Handles UI and backend configuration settings.
"""

import json
import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class TimerConfig:
    """Timer configuration settings."""
    work_duration: int = 25 * 60  # 25 minutes
    short_break_duration: int = 5 * 60  # 5 minutes
    long_break_duration: int = 15 * 60  # 15 minutes
    long_break_interval: int = 4  # Every 4 work sessions


@dataclass
class AudioConfig:
    """Audio configuration settings."""
    volume: float = 0.7
    sound_enabled: bool = True
    work_complete_sound: str = "work_complete.wav"
    break_complete_sound: str = "break_complete.wav"
    long_break_complete_sound: str = "long_break_complete.wav"
    notification_sound: str = "notification.wav"


@dataclass
class UIConfig:
    """UI configuration settings."""
    # Window settings
    window_width: int = 400
    window_height: int = 600
    window_x: int = 100
    window_y: int = 100
    always_on_top: bool = True
    
    # Transparency settings
    window_opacity: float = 0.9
    background_opacity: float = 0.8
    
    # Theme settings
    theme: str = "dark"  # "light" or "dark"
    primary_color: str = "#2196F3"
    secondary_color: str = "#FFC107"
    accent_color: str = "#FF5722"
    
    # Font settings
    font_family: str = "Arial"
    font_size: int = 14
    timer_font_size: int = 48
    
    # Animation settings
    enable_animations: bool = True
    animation_duration: int = 300
    
    # Display settings
    show_progress_bar: bool = True
    show_session_count: bool = True
    show_daily_stats: bool = True
    
    # Notification settings
    show_desktop_notifications: bool = True
    notification_duration: int = 5000  # milliseconds
    
    # Minimization settings
    minimize_to_tray: bool = True
    start_minimized: bool = False
    close_to_tray: bool = True


@dataclass
class AppConfig:
    """Application configuration settings."""
    # Data settings
    data_directory: str = "data"
    sessions_file: str = "sessions.json"
    backup_enabled: bool = True
    backup_interval: int = 24  # hours
    
    # Logging settings
    log_level: str = "INFO"
    log_file: str = "pomodoro_app.log"
    max_log_size: int = 10 * 1024 * 1024  # 10MB
    
    # Performance settings
    ui_update_interval: int = 100  # milliseconds
    auto_save_interval: int = 300  # seconds
    
    # Feature flags
    enable_statistics: bool = True
    enable_export: bool = True
    enable_themes: bool = True
    enable_plugins: bool = False
    
    # Startup settings
    auto_start: bool = False
    check_for_updates: bool = True
    
    # Language settings
    language: str = "en"
    date_format: str = "%Y-%m-%d"
    time_format: str = "%H:%M:%S"


class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.logger = logging.getLogger(__name__)
        
        # Configuration sections
        self.timer_config = TimerConfig()
        self.audio_config = AudioConfig()
        self.ui_config = UIConfig()
        self.app_config = AppConfig()
        
        # Load configuration
        self.load_config()
        
    def load_config(self) -> bool:
        """Load configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    
                # Load timer settings
                if 'timer' in config_data:
                    self._update_dataclass(self.timer_config, config_data['timer'])
                    
                # Load audio settings
                if 'audio' in config_data:
                    self._update_dataclass(self.audio_config, config_data['audio'])
                    
                # Load UI settings
                if 'ui' in config_data:
                    self._update_dataclass(self.ui_config, config_data['ui'])
                    
                # Load app settings
                if 'app' in config_data:
                    self._update_dataclass(self.app_config, config_data['app'])
                    
                self.logger.info(f"Configuration loaded from {self.config_file}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            
        return False
        
    def save_config(self) -> bool:
        """Save configuration to file."""
        try:
            config_data = {
                'timer': asdict(self.timer_config),
                'audio': asdict(self.audio_config),
                'ui': asdict(self.ui_config),
                'app': asdict(self.app_config)
            }
            
            # Create directory if it doesn't exist
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
                
            self.logger.info(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False
            
    def _update_dataclass(self, dataclass_instance, data: Dict[str, Any]):
        """Update dataclass instance with data from dictionary."""
        for key, value in data.items():
            if hasattr(dataclass_instance, key):
                setattr(dataclass_instance, key, value)
                
    def get_timer_config(self) -> TimerConfig:
        """Get timer configuration."""
        return self.timer_config
        
    def get_audio_config(self) -> AudioConfig:
        """Get audio configuration."""
        return self.audio_config
        
    def get_ui_config(self) -> UIConfig:
        """Get UI configuration."""
        return self.ui_config
        
    def get_app_config(self) -> AppConfig:
        """Get application configuration."""
        return self.app_config
        
    def update_timer_config(self, **kwargs):
        """Update timer configuration."""
        for key, value in kwargs.items():
            if hasattr(self.timer_config, key):
                setattr(self.timer_config, key, value)
        self.save_config()
        
    def update_audio_config(self, **kwargs):
        """Update audio configuration."""
        for key, value in kwargs.items():
            if hasattr(self.audio_config, key):
                setattr(self.audio_config, key, value)
        self.save_config()
        
    def update_ui_config(self, **kwargs):
        """Update UI configuration."""
        for key, value in kwargs.items():
            if hasattr(self.ui_config, key):
                setattr(self.ui_config, key, value)
        self.save_config()
        
    def update_app_config(self, **kwargs):
        """Update application configuration."""
        for key, value in kwargs.items():
            if hasattr(self.app_config, key):
                setattr(self.app_config, key, value)
        self.save_config()
        
    def reset_to_defaults(self):
        """Reset all configuration to defaults."""
        self.timer_config = TimerConfig()
        self.audio_config = AudioConfig()
        self.ui_config = UIConfig()
        self.app_config = AppConfig()
        self.save_config()
        self.logger.info("Configuration reset to defaults")
        
    def export_config(self, export_path: str) -> bool:
        """Export configuration to specified path."""
        try:
            import shutil
            shutil.copy2(self.config_file, export_path)
            self.logger.info(f"Configuration exported to {export_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting configuration: {e}")
            return False
            
    def import_config(self, import_path: str) -> bool:
        """Import configuration from specified path."""
        try:
            import shutil
            shutil.copy2(import_path, self.config_file)
            self.load_config()
            self.logger.info(f"Configuration imported from {import_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error importing configuration: {e}")
            return False
            
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all configuration settings as dictionary."""
        return {
            'timer': asdict(self.timer_config),
            'audio': asdict(self.audio_config),
            'ui': asdict(self.ui_config),
            'app': asdict(self.app_config)
        }
        
    def validate_config(self) -> bool:
        """Validate configuration settings."""
        try:
            # Validate timer settings
            if self.timer_config.work_duration <= 0:
                raise ValueError("Work duration must be positive")
            if self.timer_config.short_break_duration <= 0:
                raise ValueError("Short break duration must be positive")
            if self.timer_config.long_break_duration <= 0:
                raise ValueError("Long break duration must be positive")
            if self.timer_config.long_break_interval <= 0:
                raise ValueError("Long break interval must be positive")
                
            # Validate audio settings
            if not (0.0 <= self.audio_config.volume <= 1.0):
                raise ValueError("Volume must be between 0.0 and 1.0")
                
            # Validate UI settings
            if not (0.0 <= self.ui_config.window_opacity <= 1.0):
                raise ValueError("Window opacity must be between 0.0 and 1.0")
            if not (0.0 <= self.ui_config.background_opacity <= 1.0):
                raise ValueError("Background opacity must be between 0.0 and 1.0")
            if self.ui_config.font_size <= 0:
                raise ValueError("Font size must be positive")
            if self.ui_config.timer_font_size <= 0:
                raise ValueError("Timer font size must be positive")
                
            # Validate app settings
            if self.app_config.ui_update_interval <= 0:
                raise ValueError("UI update interval must be positive")
            if self.app_config.auto_save_interval <= 0:
                raise ValueError("Auto save interval must be positive")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False
            
    def create_backup(self) -> bool:
        """Create a backup of the current configuration."""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.config_file.with_suffix(f".backup_{timestamp}.json")
            
            import shutil
            shutil.copy2(self.config_file, backup_path)
            
            self.logger.info(f"Configuration backup created: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating configuration backup: {e}")
            return False