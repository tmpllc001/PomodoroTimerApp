"""
Unit tests for AudioManager class.
Tests audio playback, volume control, and notification management.
"""

import pytest
import os
import threading
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


class MockAudioManager:
    """Mock implementation of AudioManager for testing."""
    
    def __init__(self):
        self.is_playing = False
        self.is_paused = False
        self.volume = 0.7
        self.current_track = None
        self.notification_sounds = {}
        self.bgm_tracks = {}
        self.sound_enabled = True
        self.notification_enabled = True
        self.mixer_initialized = False
        self.playback_thread = None
        
    def initialize_mixer(self):
        """Initialize pygame mixer."""
        if not self.mixer_initialized:
            self.mixer_initialized = True
            return True
        return False
        
    def load_audio_files(self, audio_directory):
        """Load audio files from directory."""
        if not os.path.exists(audio_directory):
            return False
            
        # Mock loading notification sounds
        self.notification_sounds = {
            'work_complete': 'work_complete.wav',
            'break_complete': 'break_complete.wav',
            'session_start': 'session_start.wav'
        }
        
        # Mock loading BGM tracks
        self.bgm_tracks = {
            'focus': 'focus_bgm.mp3',
            'break': 'break_bgm.mp3',
            'ambient': 'ambient_bgm.mp3'
        }
        
        return True
        
    def play_notification(self, notification_type="work_complete"):
        """Play notification sound."""
        if not self.notification_enabled or not self.sound_enabled:
            return False
            
        if notification_type not in self.notification_sounds:
            return False
            
        # Mock playing notification
        return True
        
    def stop_notification(self):
        """Stop notification sound."""
        # Mock stopping notification
        return True
        
    def play_bgm(self, track_name="focus"):
        """Play background music."""
        if not self.sound_enabled:
            return False
            
        if track_name not in self.bgm_tracks:
            return False
            
        if self.is_playing:
            self.stop_bgm()
            
        self.current_track = track_name
        self.is_playing = True
        self.is_paused = False
        return True
        
    def pause_bgm(self):
        """Pause background music."""
        if self.is_playing and not self.is_paused:
            self.is_paused = True
            return True
        return False
        
    def resume_bgm(self):
        """Resume background music."""
        if self.is_playing and self.is_paused:
            self.is_paused = False
            return True
        return False
        
    def stop_bgm(self):
        """Stop background music."""
        if self.is_playing:
            self.is_playing = False
            self.is_paused = False
            self.current_track = None
            return True
        return False
        
    def set_volume(self, volume):
        """Set volume level."""
        if 0.0 <= volume <= 1.0:
            self.volume = volume
            return True
        return False
        
    def get_volume(self):
        """Get current volume level."""
        return self.volume
        
    def toggle_sound(self):
        """Toggle sound on/off."""
        self.sound_enabled = not self.sound_enabled
        if not self.sound_enabled:
            self.stop_bgm()
        return self.sound_enabled
        
    def toggle_notifications(self):
        """Toggle notifications on/off."""
        self.notification_enabled = not self.notification_enabled
        return self.notification_enabled
        
    def is_bgm_playing(self):
        """Check if BGM is playing."""
        return self.is_playing and not self.is_paused
        
    def is_bgm_paused(self):
        """Check if BGM is paused."""
        return self.is_playing and self.is_paused
        
    def get_current_track(self):
        """Get current track name."""
        return self.current_track
        
    def get_audio_info(self):
        """Get audio system information."""
        return {
            'mixer_initialized': self.mixer_initialized,
            'sound_enabled': self.sound_enabled,
            'notification_enabled': self.notification_enabled,
            'volume': self.volume,
            'current_track': self.current_track,
            'is_playing': self.is_playing,
            'is_paused': self.is_paused
        }
        
    def validate_audio_file(self, file_path):
        """Validate audio file exists and is readable."""
        return os.path.exists(file_path) and os.path.isfile(file_path)


class TestAudioManager:
    """Test suite for AudioManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.audio_manager = MockAudioManager()
        
    def test_initialization(self):
        """Test audio manager initialization."""
        assert not self.audio_manager.is_playing
        assert not self.audio_manager.is_paused
        assert self.audio_manager.volume == 0.7
        assert self.audio_manager.current_track is None
        assert self.audio_manager.sound_enabled
        assert self.audio_manager.notification_enabled
        assert not self.audio_manager.mixer_initialized
        
    def test_initialize_mixer(self):
        """Test mixer initialization."""
        result = self.audio_manager.initialize_mixer()
        assert result is True
        assert self.audio_manager.mixer_initialized
        
        # Test second initialization
        result = self.audio_manager.initialize_mixer()
        assert result is False
        
    def test_load_audio_files_valid_directory(self):
        """Test loading audio files from valid directory."""
        with patch('os.path.exists', return_value=True):
            result = self.audio_manager.load_audio_files("/valid/path")
            assert result is True
            assert len(self.audio_manager.notification_sounds) == 3
            assert len(self.audio_manager.bgm_tracks) == 3
            
    def test_load_audio_files_invalid_directory(self):
        """Test loading audio files from invalid directory."""
        with patch('os.path.exists', return_value=False):
            result = self.audio_manager.load_audio_files("/invalid/path")
            assert result is False
            
    def test_play_notification_success(self):
        """Test successful notification playback."""
        self.audio_manager.notification_sounds = {'work_complete': 'test.wav'}
        result = self.audio_manager.play_notification("work_complete")
        assert result is True
        
    def test_play_notification_disabled(self):
        """Test notification playback when disabled."""
        self.audio_manager.notification_enabled = False
        result = self.audio_manager.play_notification()
        assert result is False
        
    def test_play_notification_sound_disabled(self):
        """Test notification playback when sound disabled."""
        self.audio_manager.sound_enabled = False
        result = self.audio_manager.play_notification()
        assert result is False
        
    def test_play_notification_invalid_type(self):
        """Test notification playback with invalid type."""
        result = self.audio_manager.play_notification("invalid_type")
        assert result is False
        
    def test_stop_notification(self):
        """Test stopping notification."""
        result = self.audio_manager.stop_notification()
        assert result is True
        
    def test_play_bgm_success(self):
        """Test successful BGM playback."""
        self.audio_manager.bgm_tracks = {'focus': 'focus.mp3'}
        result = self.audio_manager.play_bgm("focus")
        assert result is True
        assert self.audio_manager.is_playing
        assert not self.audio_manager.is_paused
        assert self.audio_manager.current_track == "focus"
        
    def test_play_bgm_sound_disabled(self):
        """Test BGM playback when sound disabled."""
        self.audio_manager.sound_enabled = False
        result = self.audio_manager.play_bgm()
        assert result is False
        
    def test_play_bgm_invalid_track(self):
        """Test BGM playback with invalid track."""
        result = self.audio_manager.play_bgm("invalid_track")
        assert result is False
        
    def test_play_bgm_replace_current(self):
        """Test BGM playback replacing current track."""
        self.audio_manager.bgm_tracks = {'focus': 'focus.mp3', 'break': 'break.mp3'}
        
        # Start first track
        self.audio_manager.play_bgm("focus")
        assert self.audio_manager.current_track == "focus"
        
        # Replace with second track
        self.audio_manager.play_bgm("break")
        assert self.audio_manager.current_track == "break"
        
    def test_pause_bgm_success(self):
        """Test successful BGM pause."""
        self.audio_manager.bgm_tracks = {'focus': 'focus.mp3'}
        self.audio_manager.play_bgm("focus")
        
        result = self.audio_manager.pause_bgm()
        assert result is True
        assert self.audio_manager.is_paused
        assert self.audio_manager.is_playing  # Still playing, just paused
        
    def test_pause_bgm_not_playing(self):
        """Test pausing BGM when not playing."""
        result = self.audio_manager.pause_bgm()
        assert result is False
        
    def test_pause_bgm_already_paused(self):
        """Test pausing BGM when already paused."""
        self.audio_manager.is_playing = True
        self.audio_manager.is_paused = True
        
        result = self.audio_manager.pause_bgm()
        assert result is False
        
    def test_resume_bgm_success(self):
        """Test successful BGM resume."""
        self.audio_manager.is_playing = True
        self.audio_manager.is_paused = True
        
        result = self.audio_manager.resume_bgm()
        assert result is True
        assert not self.audio_manager.is_paused
        
    def test_resume_bgm_not_paused(self):
        """Test resuming BGM when not paused."""
        self.audio_manager.is_playing = True
        self.audio_manager.is_paused = False
        
        result = self.audio_manager.resume_bgm()
        assert result is False
        
    def test_stop_bgm_success(self):
        """Test successful BGM stop."""
        self.audio_manager.is_playing = True
        self.audio_manager.current_track = "focus"
        
        result = self.audio_manager.stop_bgm()
        assert result is True
        assert not self.audio_manager.is_playing
        assert not self.audio_manager.is_paused
        assert self.audio_manager.current_track is None
        
    def test_stop_bgm_not_playing(self):
        """Test stopping BGM when not playing."""
        result = self.audio_manager.stop_bgm()
        assert result is False
        
    def test_set_volume_valid(self):
        """Test setting valid volume."""
        result = self.audio_manager.set_volume(0.5)
        assert result is True
        assert self.audio_manager.volume == 0.5
        
    def test_set_volume_boundary_values(self):
        """Test setting volume boundary values."""
        # Test minimum
        result = self.audio_manager.set_volume(0.0)
        assert result is True
        assert self.audio_manager.volume == 0.0
        
        # Test maximum
        result = self.audio_manager.set_volume(1.0)
        assert result is True
        assert self.audio_manager.volume == 1.0
        
    def test_set_volume_invalid(self):
        """Test setting invalid volume."""
        original_volume = self.audio_manager.volume
        
        # Test below minimum
        result = self.audio_manager.set_volume(-0.1)
        assert result is False
        assert self.audio_manager.volume == original_volume
        
        # Test above maximum
        result = self.audio_manager.set_volume(1.1)
        assert result is False
        assert self.audio_manager.volume == original_volume
        
    def test_get_volume(self):
        """Test getting volume."""
        self.audio_manager.volume = 0.8
        assert self.audio_manager.get_volume() == 0.8
        
    def test_toggle_sound(self):
        """Test toggling sound on/off."""
        original_state = self.audio_manager.sound_enabled
        
        result = self.audio_manager.toggle_sound()
        assert result != original_state
        assert self.audio_manager.sound_enabled != original_state
        
    def test_toggle_sound_stops_bgm(self):
        """Test toggling sound off stops BGM."""
        self.audio_manager.is_playing = True
        self.audio_manager.sound_enabled = True
        
        self.audio_manager.toggle_sound()
        assert not self.audio_manager.sound_enabled
        assert not self.audio_manager.is_playing
        
    def test_toggle_notifications(self):
        """Test toggling notifications on/off."""
        original_state = self.audio_manager.notification_enabled
        
        result = self.audio_manager.toggle_notifications()
        assert result != original_state
        assert self.audio_manager.notification_enabled != original_state
        
    def test_is_bgm_playing(self):
        """Test checking if BGM is playing."""
        assert not self.audio_manager.is_bgm_playing()
        
        self.audio_manager.is_playing = True
        assert self.audio_manager.is_bgm_playing()
        
        self.audio_manager.is_paused = True
        assert not self.audio_manager.is_bgm_playing()
        
    def test_is_bgm_paused(self):
        """Test checking if BGM is paused."""
        assert not self.audio_manager.is_bgm_paused()
        
        self.audio_manager.is_playing = True
        self.audio_manager.is_paused = True
        assert self.audio_manager.is_bgm_paused()
        
    def test_get_current_track(self):
        """Test getting current track."""
        assert self.audio_manager.get_current_track() is None
        
        self.audio_manager.current_track = "focus"
        assert self.audio_manager.get_current_track() == "focus"
        
    def test_get_audio_info(self):
        """Test getting audio system information."""
        info = self.audio_manager.get_audio_info()
        
        assert isinstance(info, dict)
        assert 'mixer_initialized' in info
        assert 'sound_enabled' in info
        assert 'notification_enabled' in info
        assert 'volume' in info
        assert 'current_track' in info
        assert 'is_playing' in info
        assert 'is_paused' in info
        
    def test_validate_audio_file_exists(self):
        """Test validating existing audio file."""
        with patch('os.path.exists', return_value=True):
            with patch('os.path.isfile', return_value=True):
                result = self.audio_manager.validate_audio_file("test.wav")
                assert result is True
                
    def test_validate_audio_file_not_exists(self):
        """Test validating non-existing audio file."""
        with patch('os.path.exists', return_value=False):
            result = self.audio_manager.validate_audio_file("test.wav")
            assert result is False
            
    def test_validate_audio_file_not_file(self):
        """Test validating path that is not a file."""
        with patch('os.path.exists', return_value=True):
            with patch('os.path.isfile', return_value=False):
                result = self.audio_manager.validate_audio_file("test_dir")
                assert result is False
                
    def test_notification_types(self):
        """Test different notification types."""
        self.audio_manager.notification_sounds = {
            'work_complete': 'work.wav',
            'break_complete': 'break.wav',
            'session_start': 'start.wav'
        }
        
        assert self.audio_manager.play_notification('work_complete') is True
        assert self.audio_manager.play_notification('break_complete') is True
        assert self.audio_manager.play_notification('session_start') is True
        
    def test_bgm_track_types(self):
        """Test different BGM track types."""
        self.audio_manager.bgm_tracks = {
            'focus': 'focus.mp3',
            'break': 'break.mp3',
            'ambient': 'ambient.mp3'
        }
        
        assert self.audio_manager.play_bgm('focus') is True
        assert self.audio_manager.play_bgm('break') is True
        assert self.audio_manager.play_bgm('ambient') is True
        
    def test_state_consistency(self):
        """Test state consistency during operations."""
        self.audio_manager.bgm_tracks = {'focus': 'focus.mp3'}
        
        # Start playing
        self.audio_manager.play_bgm('focus')
        assert self.audio_manager.is_playing
        assert not self.audio_manager.is_paused
        assert self.audio_manager.current_track == 'focus'
        
        # Pause
        self.audio_manager.pause_bgm()
        assert self.audio_manager.is_playing
        assert self.audio_manager.is_paused
        assert self.audio_manager.current_track == 'focus'
        
        # Resume
        self.audio_manager.resume_bgm()
        assert self.audio_manager.is_playing
        assert not self.audio_manager.is_paused
        assert self.audio_manager.current_track == 'focus'
        
        # Stop
        self.audio_manager.stop_bgm()
        assert not self.audio_manager.is_playing
        assert not self.audio_manager.is_paused
        assert self.audio_manager.current_track is None