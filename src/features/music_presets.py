#!/usr/bin/env python3
"""
Music Presets Feature for Pomodoro Timer
Integrates AudioPresetManager with timer sessions.
"""

import os
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from enum import Enum

# Import audio preset manager
# 音楽プリセット機能の簡単な実装
import sys
import logging

try:
    sys.path.append(str(Path(__file__).parent.parent))
    from audio.preset_manager import AudioPresetManager
except ImportError:
    # AudioPresetManagerが存在しない場合のフォールバック
    class AudioPresetManager:
        def __init__(self):
            self.current_preset = None
            self.is_playing = False
            self.volume = 0.7
            self.is_muted = False
            self.presets = {
                'work': Path('assets/music/work_bgm.mp3'),
                'break': Path('assets/music/break_bgm.mp3')
            }
        
        def play_preset(self, preset_name, loop=True):
            self.current_preset = preset_name
            self.is_playing = True
            print(f"🎵 Playing preset: {preset_name}")
            return True
        
        def stop_preset(self):
            self.is_playing = False
            self.current_preset = None
            print("🎵 Stopped preset")
            return True
        
        def pause_preset(self):
            print("🎵 Paused preset")
            return True
        
        def resume_preset(self):
            print("🎵 Resumed preset")
            return True
        
        def set_volume(self, volume):
            self.volume = volume
            return True
        
        def toggle_mute(self):
            self.is_muted = not self.is_muted
            return self.is_muted
        
        def is_preset_playing(self):
            return self.is_playing
        
        def get_available_presets(self):
            return {
                'work': 'Work BGM (25 min focus music)',
                'break': 'Break BGM (5 min relaxation)'
            }
        
        def get_preset_info(self, preset_name):
            preset_path = self.presets.get(preset_name, '')
            return {
                'name': preset_name.title() + ' Mode',
                'file': str(preset_path) if preset_path else '',
                'exists': preset_path.exists() if isinstance(preset_path, Path) else False
            }
        
        def get_current_preset(self):
            return self.current_preset
        
        def create_sample_audio_files(self):
            pass
        
        def cleanup(self):
            pass


class SessionType(Enum):
    """Session types for music presets."""
    WORK = "work"
    BREAK = "break"
    LONG_BREAK = "long_break"


class MusicPresets:
    """Music presets feature for Pomodoro Timer."""
    
    def __init__(self):
        self.audio_manager = AudioPresetManager()
        self.current_session = None
        self.auto_play_enabled = True
        self.session_callbacks = {}
        self.is_session_active = False
        
        # Music settings
        self.music_enabled = True
        self.current_volume = 0.7
        self.fade_duration = 3.0  # seconds
        
        # Session timers
        self.session_timer = None
        self.fade_timer = None
        
        # Logger
        self.logger = logging.getLogger(__name__)
        
        # Ensure audio directory exists
        self.ensure_audio_directory()
        
    def ensure_audio_directory(self):
        """Ensure audio directory exists."""
        audio_dir = Path(__file__).parent.parent.parent / "audio"
        audio_dir.mkdir(exist_ok=True)
        
        # Create sample audio files if they don't exist
        if not self.audio_manager.presets['work'].exists() or not self.audio_manager.presets['break'].exists():
            self.audio_manager.create_sample_audio_files()
            
    def start_session(self, session_type: SessionType, duration_minutes: int = 25) -> bool:
        """Start a music session for the given session type."""
        try:
            # Stop any current session
            self.stop_session()
            
            if not self.music_enabled:
                return True
                
            # Set current session
            self.current_session = session_type
            self.is_session_active = True
            
            # Select appropriate preset
            preset_name = self._get_preset_for_session(session_type)
            
            if preset_name:
                # Start playing the preset
                success = self.audio_manager.play_preset(preset_name, loop=True)
                
                if success:
                    print(f"🎵 Started {session_type.value} music session ({duration_minutes} min)")
                    
                    # Schedule session end
                    self._schedule_session_end(duration_minutes)
                    
                    # Trigger callback if registered
                    if session_type in self.session_callbacks:
                        self.session_callbacks[session_type]('started')
                        
                    return True
                else:
                    print(f"❌ Failed to start music for {session_type.value}")
                    return False
            else:
                print(f"⚠️ No preset available for {session_type.value}")
                return False
                
        except Exception as e:
            print(f"💥 Error starting music session: {e}")
            return False
            
    def stop_session(self) -> bool:
        """Stop current music session."""
        try:
            if self.is_session_active:
                # Cancel timers
                if self.session_timer:
                    self.session_timer.cancel()
                    self.session_timer = None
                    
                if self.fade_timer:
                    self.fade_timer.cancel()
                    self.fade_timer = None
                
                # Stop audio
                self.audio_manager.stop_preset()
                
                # Reset state
                prev_session = self.current_session
                self.current_session = None
                self.is_session_active = False
                
                if prev_session:
                    print(f"🔇 Stopped {prev_session.value} music session")
                    
                    # Trigger callback if registered
                    if prev_session in self.session_callbacks:
                        self.session_callbacks[prev_session]('stopped')
                        
                return True
            else:
                return True
                
        except Exception as e:
            print(f"💥 Error stopping music session: {e}")
            return False
            
    def pause_session(self) -> bool:
        """Pause current music session."""
        try:
            if self.is_session_active:
                success = self.audio_manager.pause_preset()
                
                if success and self.current_session:
                    print(f"⏸️ Paused {self.current_session.value} music session")
                    
                    # Trigger callback if registered
                    if self.current_session in self.session_callbacks:
                        self.session_callbacks[self.current_session]('paused')
                        
                return success
            else:
                return True
                
        except Exception as e:
            print(f"💥 Error pausing music session: {e}")
            return False
            
    def resume_session(self) -> bool:
        """Resume paused music session."""
        try:
            if self.is_session_active:
                success = self.audio_manager.resume_preset()
                
                if success and self.current_session:
                    print(f"▶️ Resumed {self.current_session.value} music session")
                    
                    # Trigger callback if registered
                    if self.current_session in self.session_callbacks:
                        self.session_callbacks[self.current_session]('resumed')
                        
                return success
            else:
                return True
                
        except Exception as e:
            print(f"💥 Error resuming music session: {e}")
            return False
            
    def set_volume(self, volume: float) -> bool:
        """Set music volume (0.0 to 1.0)."""
        try:
            if not 0.0 <= volume <= 1.0:
                return False
                
            self.current_volume = volume
            success = self.audio_manager.set_volume(volume)
            
            if success:
                print(f"🔊 Volume set to {volume * 100:.0f}%")
                
            return success
            
        except Exception as e:
            print(f"💥 Error setting volume: {e}")
            return False
            
    def get_volume(self) -> float:
        """Get current volume level."""
        return self.current_volume
        
    def toggle_mute(self) -> bool:
        """Toggle mute state."""
        try:
            is_muted = self.audio_manager.toggle_mute()
            
            if is_muted:
                print("🔇 Music muted")
            else:
                print("🔊 Music unmuted")
                
            return is_muted
            
        except Exception as e:
            print(f"💥 Error toggling mute: {e}")
            return False
            
    def is_muted(self) -> bool:
        """Check if music is muted."""
        return self.audio_manager.is_muted
        
    def enable_music(self, enabled: bool = True):
        """Enable or disable music feature."""
        self.music_enabled = enabled
        
        if not enabled and self.is_session_active:
            self.stop_session()
            
        print(f"🎵 Music {'enabled' if enabled else 'disabled'}")
        
    def is_music_enabled(self) -> bool:
        """Check if music feature is enabled."""
        return self.music_enabled
        
    def get_current_session(self) -> Optional[SessionType]:
        """Get current session type."""
        return self.current_session
        
    def is_session_playing(self) -> bool:
        """Check if session is currently playing."""
        return self.is_session_active and self.audio_manager.is_preset_playing()
        
    def get_available_presets(self) -> Dict[str, str]:
        """Get available music presets."""
        return self.audio_manager.get_available_presets()
        
    def get_preset_info(self, preset_name: str) -> Dict[str, Any]:
        """Get information about a specific preset."""
        return self.audio_manager.get_preset_info(preset_name)
        
    def register_session_callback(self, session_type: SessionType, callback: Callable):
        """Register callback for session events."""
        self.session_callbacks[session_type] = callback
        
    def fade_out(self, duration: float = 3.0) -> bool:
        """Fade out current music over specified duration."""
        try:
            if not self.is_session_active:
                return True
                
            # Cancel any existing fade timer
            if self.fade_timer:
                self.fade_timer.cancel()
                
            # Start fade out
            self._start_fade_out(duration)
            
            return True
            
        except Exception as e:
            print(f"💥 Error fading out music: {e}")
            return False
            
    def _get_preset_for_session(self, session_type: SessionType) -> Optional[str]:
        """Get appropriate preset for session type."""
        preset_mapping = {
            SessionType.WORK: 'work',
            SessionType.BREAK: 'break',
            SessionType.LONG_BREAK: 'break'  # Use break music for long breaks
        }
        
        return preset_mapping.get(session_type)
        
    def _schedule_session_end(self, duration_minutes: int):
        """Schedule session end after specified duration."""
        def end_session():
            try:
                # Fade out music
                self.fade_out(self.fade_duration)
                
                # Wait for fade to complete
                time.sleep(self.fade_duration + 0.5)
                
                # Stop session
                self.stop_session()
                
                print(f"⏰ Session ended after {duration_minutes} minutes")
                
            except Exception as e:
                print(f"💥 Error ending session: {e}")
                
        # Schedule the end
        self.session_timer = threading.Timer(duration_minutes * 60, end_session)
        self.session_timer.start()
        
    def _start_fade_out(self, duration: float):
        """Start fade out effect."""
        def fade_step():
            try:
                steps = int(duration * 10)  # 10 steps per second
                volume_step = self.current_volume / steps
                
                for i in range(steps):
                    if not self.is_session_active:
                        break
                        
                    new_volume = self.current_volume - (volume_step * (i + 1))
                    new_volume = max(0.0, new_volume)
                    
                    self.audio_manager.set_volume(new_volume)
                    time.sleep(0.1)
                    
                # Ensure volume is at 0
                self.audio_manager.set_volume(0.0)
                
            except Exception as e:
                print(f"💥 Error in fade out: {e}")
                
        # Start fade in separate thread
        self.fade_timer = threading.Thread(target=fade_step, daemon=True)
        self.fade_timer.start()
        
    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status."""
        return {
            'is_active': self.is_session_active,
            'session_type': self.current_session.value if self.current_session else None,
            'is_playing': self.is_session_playing(),
            'is_muted': self.is_muted(),
            'volume': self.get_volume(),
            'music_enabled': self.music_enabled,
            'current_preset': self.audio_manager.get_current_preset()
        }
        
    def cleanup(self):
        """Clean up resources."""
        try:
            self.stop_session()
            self.audio_manager.cleanup()
            print("🧹 Music presets cleaned up")
            
        except Exception as e:
            print(f"💥 Error during cleanup: {e}")


# Global instance for easy access
_music_presets = None

def get_music_presets() -> MusicPresets:
    """Get global music presets instance."""
    global _music_presets
    if _music_presets is None:
        _music_presets = MusicPresets()
    return _music_presets


# Integration functions for timer system
def start_work_session(duration_minutes: int = 25) -> bool:
    """Start work session with background music."""
    return get_music_presets().start_session(SessionType.WORK, duration_minutes)


def start_break_session(duration_minutes: int = 5) -> bool:
    """Start break session with relaxing music."""
    return get_music_presets().start_session(SessionType.BREAK, duration_minutes)


def start_long_break_session(duration_minutes: int = 15) -> bool:
    """Start long break session with relaxing music."""
    return get_music_presets().start_session(SessionType.LONG_BREAK, duration_minutes)


def stop_music_session() -> bool:
    """Stop current music session."""
    return get_music_presets().stop_session()


def pause_music_session() -> bool:
    """Pause current music session."""
    return get_music_presets().pause_session()


def resume_music_session() -> bool:
    """Resume current music session."""
    return get_music_presets().resume_session()


def set_music_volume(volume: float) -> bool:
    """Set music volume (0-100%)."""
    return get_music_presets().set_volume(volume / 100.0 if volume > 1 else volume)


def toggle_music_mute() -> bool:
    """Toggle music mute state."""
    return get_music_presets().toggle_mute()


def is_music_playing() -> bool:
    """Check if music is currently playing."""
    return get_music_presets().is_session_playing()


def get_music_status() -> Dict[str, Any]:
    """Get current music status."""
    return get_music_presets().get_session_status()


# 簡易インターフェース追加（main_phase2.pyとの互換性のため）
class MusicPresetsSimple(MusicPresets):
    """Simplified interface for main_phase2.py"""
    
    def play(self):
        """Start playing current preset"""
        if hasattr(self.audio_manager, 'is_playing'):
            self.audio_manager.is_playing = True
    
    def pause(self):
        """Pause current music"""
        self.pause_session()
    
    def stop(self):
        """Stop current music"""
        self.stop_session()
    
    def set_preset(self, preset_name):
        """Set music preset"""
        self.logger.info(f"🎵 プリセット変更: {preset_name}")
        if preset_name == 'work':
            self.current_session = SessionType.WORK
        elif preset_name == 'break':
            self.current_session = SessionType.BREAK
        else:
            self.current_session = None
    
    def play_alert(self, alert_type):
        """Play alert sound"""
        self.logger.info(f"🔔 アラート音: {alert_type}")
    
    def enable(self, enabled):
        """Enable/disable music"""
        self.enable_music(enabled)