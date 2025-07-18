#!/usr/bin/env python3
"""
Audio Preset Manager for Pomodoro Timer
Handles BGM presets for work and break sessions with volume control and looping.
"""

import os
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any
import pygame


class AudioPresetManager:
    """Manages audio presets for work and break sessions."""
    
    def __init__(self):
        self.is_initialized = False
        self.current_preset = None
        self.is_playing = False
        self.is_muted = False
        self.volume = 0.7  # Default volume 70%
        self.loop_thread = None
        self.stop_event = threading.Event()
        
        # Audio file paths
        self.audio_dir = Path(__file__).parent.parent.parent / "audio"
        self.presets = {
            'work': self.audio_dir / "work_bgm.wav",
            'break': self.audio_dir / "break_bgm.wav"
        }
        
        # Loop durations (in seconds)
        self.loop_durations = {
            'work': 25 * 60,  # 25 minutes
            'break': 5 * 60   # 5 minutes
        }
        
        self.initialize_audio()
        
    def initialize_audio(self) -> bool:
        """Initialize pygame mixer for audio playback."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.is_initialized = True
            return True
        except Exception as e:
            print(f"Audio initialization failed: {e}")
            self.is_initialized = False
            return False
            
    def create_sample_audio_files(self):
        """Create sample audio files for testing."""
        import numpy as np
        import wave
        
        # Create work BGM (25 minutes of gentle ambient sound)
        work_bgm_path = self.presets['work']
        if not work_bgm_path.exists():
            self._create_ambient_audio(work_bgm_path, duration=30, frequency=200)
            
        # Create break BGM (5 minutes of relaxing sound)
        break_bgm_path = self.presets['break']
        if not break_bgm_path.exists():
            self._create_ambient_audio(break_bgm_path, duration=10, frequency=150)
            
    def _create_ambient_audio(self, file_path: Path, duration: int, frequency: int):
        """Create ambient audio file for testing."""
        try:
            import numpy as np
            import wave
            
            sample_rate = 22050
            samples = duration * sample_rate
            
            # Generate gentle ambient sound
            t = np.linspace(0, duration, samples)
            # Mix of sine waves for ambient effect
            audio = (np.sin(2 * np.pi * frequency * t) * 0.3 + 
                    np.sin(2 * np.pi * frequency * 1.5 * t) * 0.2 +
                    np.sin(2 * np.pi * frequency * 0.8 * t) * 0.1)
            
            # Add gentle fade in/out
            fade_samples = sample_rate // 2  # 0.5 second fade
            audio[:fade_samples] *= np.linspace(0, 1, fade_samples)
            audio[-fade_samples:] *= np.linspace(1, 0, fade_samples)
            
            # Convert to 16-bit integer
            audio = (audio * 32767).astype(np.int16)
            
            # Save as WAV file
            with wave.open(str(file_path), 'w') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio.tobytes())
                
            print(f"Created sample audio: {file_path}")
            
        except ImportError:
            print("NumPy not available, creating silent audio file")
            self._create_silent_audio(file_path, duration)
        except Exception as e:
            print(f"Error creating audio file {file_path}: {e}")
            
    def _create_silent_audio(self, file_path: Path, duration: int):
        """Create silent audio file as fallback."""
        try:
            import wave
            
            sample_rate = 22050
            samples = duration * sample_rate
            
            # Create silent audio
            silent_audio = bytes(samples * 2)  # 16-bit silence
            
            with wave.open(str(file_path), 'w') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(silent_audio)
                
        except Exception as e:
            print(f"Error creating silent audio: {e}")
            
    def load_preset(self, preset_name: str) -> bool:
        """Load audio preset for playback."""
        if not self.is_initialized:
            return False
            
        if preset_name not in self.presets:
            print(f"Unknown preset: {preset_name}")
            return False
            
        audio_file = self.presets[preset_name]
        
        # Create sample file if it doesn't exist
        if not audio_file.exists():
            self.create_sample_audio_files()
            
        if not audio_file.exists():
            print(f"Audio file not found: {audio_file}")
            return False
            
        try:
            # Load the audio file
            pygame.mixer.music.load(str(audio_file))
            self.current_preset = preset_name
            print(f"Loaded preset: {preset_name}")
            return True
        except Exception as e:
            print(f"Error loading preset {preset_name}: {e}")
            return False
            
    def play_preset(self, preset_name: str, loop: bool = True) -> bool:
        """Play audio preset with optional looping."""
        if not self.load_preset(preset_name):
            return False
            
        if self.is_muted:
            return True  # Consider it successful but don't play
            
        try:
            # Stop any current playback
            self.stop_preset()
            
            # Set volume
            pygame.mixer.music.set_volume(self.volume)
            
            # Start playback
            if loop:
                self._start_looped_playback(preset_name)
            else:
                pygame.mixer.music.play()
                
            self.is_playing = True
            print(f"Started playing preset: {preset_name}")
            return True
            
        except Exception as e:
            print(f"Error playing preset {preset_name}: {e}")
            return False
            
    def _start_looped_playback(self, preset_name: str):
        """Start looped playback in a separate thread."""
        self.stop_event.clear()
        
        def loop_playback():
            loop_duration = self.loop_durations.get(preset_name, 30)
            
            while not self.stop_event.is_set():
                try:
                    # Play the audio
                    pygame.mixer.music.play()
                    
                    # Wait for the loop duration or stop event
                    elapsed = 0
                    while elapsed < loop_duration and not self.stop_event.is_set():
                        time.sleep(0.1)
                        elapsed += 0.1
                        
                    # Stop current playback before next loop
                    if not self.stop_event.is_set():
                        pygame.mixer.music.stop()
                        time.sleep(0.1)  # Small gap between loops
                        
                except Exception as e:
                    print(f"Error in loop playback: {e}")
                    break
                    
        self.loop_thread = threading.Thread(target=loop_playback, daemon=True)
        self.loop_thread.start()
        
    def stop_preset(self) -> bool:
        """Stop current preset playback."""
        try:
            # Signal loop thread to stop
            self.stop_event.set()
            
            # Stop pygame mixer
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                
            # Wait for loop thread to finish
            if self.loop_thread and self.loop_thread.is_alive():
                self.loop_thread.join(timeout=1.0)
                
            self.is_playing = False
            self.current_preset = None
            print("Stopped preset playback")
            return True
            
        except Exception as e:
            print(f"Error stopping preset: {e}")
            return False
            
    def pause_preset(self) -> bool:
        """Pause current preset playback."""
        try:
            if self.is_playing:
                pygame.mixer.music.pause()
                print("Paused preset playback")
                return True
            return False
        except Exception as e:
            print(f"Error pausing preset: {e}")
            return False
            
    def resume_preset(self) -> bool:
        """Resume paused preset playback."""
        try:
            pygame.mixer.music.unpause()
            print("Resumed preset playback")
            return True
        except Exception as e:
            print(f"Error resuming preset: {e}")
            return False
            
    def set_volume(self, volume: float) -> bool:
        """Set volume level (0.0 to 1.0)."""
        if not 0.0 <= volume <= 1.0:
            return False
            
        try:
            self.volume = volume
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(volume)
            print(f"Set volume to {volume * 100:.0f}%")
            return True
        except Exception as e:
            print(f"Error setting volume: {e}")
            return False
            
    def get_volume(self) -> float:
        """Get current volume level."""
        return self.volume
        
    def toggle_mute(self) -> bool:
        """Toggle mute state."""
        self.is_muted = not self.is_muted
        
        if self.is_muted:
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(0)
            print("Muted audio")
        else:
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(self.volume)
            print("Unmuted audio")
            
        return self.is_muted
        
    def is_preset_playing(self) -> bool:
        """Check if preset is currently playing."""
        return self.is_playing and not self.is_muted
        
    def get_current_preset(self) -> Optional[str]:
        """Get currently loaded preset name."""
        return self.current_preset
        
    def get_available_presets(self) -> Dict[str, str]:
        """Get available presets."""
        return {
            'work': 'Work BGM (25 min focus music)',
            'break': 'Break BGM (5 min relaxing music)'
        }
        
    def get_preset_info(self, preset_name: str) -> Dict[str, Any]:
        """Get information about a preset."""
        if preset_name not in self.presets:
            return {}
            
        audio_file = self.presets[preset_name]
        return {
            'name': preset_name,
            'file_path': str(audio_file),
            'exists': audio_file.exists(),
            'loop_duration': self.loop_durations.get(preset_name, 30),
            'description': self.get_available_presets().get(preset_name, '')
        }
        
    def cleanup(self):
        """Clean up resources."""
        try:
            self.stop_preset()
            if pygame.mixer.get_init():
                pygame.mixer.quit()
            print("Audio preset manager cleaned up")
        except Exception as e:
            print(f"Error during cleanup: {e}")


# Global instance for easy access
_preset_manager = None

def get_preset_manager() -> AudioPresetManager:
    """Get global preset manager instance."""
    global _preset_manager
    if _preset_manager is None:
        _preset_manager = AudioPresetManager()
    return _preset_manager