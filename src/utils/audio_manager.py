import pygame
import os
import threading
from typing import Optional, Dict
from pathlib import Path


class AudioManager:
    def __init__(self, audio_dir: str = "assets/audio"):
        self.audio_dir = Path(audio_dir)
        self.volume = 0.7
        self.sound_enabled = True
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        
        self._init_pygame()
        self._load_sounds()
        
    def _init_pygame(self):
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        except pygame.error as e:
            print(f"Error initializing pygame mixer: {e}")
            
    def _load_sounds(self):
        sound_files = {
            'work_complete': 'work_complete.wav',
            'break_complete': 'break_complete.wav',
            'long_break_complete': 'long_break_complete.wav',
            'tick': 'tick.wav',
            'notification': 'notification.wav'
        }
        
        for sound_name, filename in sound_files.items():
            file_path = self.audio_dir / filename
            if file_path.exists():
                try:
                    sound = pygame.mixer.Sound(str(file_path))
                    sound.set_volume(self.volume)
                    self.sounds[sound_name] = sound
                except pygame.error as e:
                    print(f"Error loading sound {filename}: {e}")
            else:
                self._create_default_sound(sound_name)
                
    def _create_default_sound(self, sound_name: str):
        try:
            if sound_name == 'work_complete':
                sound = self._generate_beep_sound(frequency=800, duration=0.3)
            elif sound_name == 'break_complete':
                sound = self._generate_beep_sound(frequency=600, duration=0.3)
            elif sound_name == 'long_break_complete':
                sound = self._generate_beep_sound(frequency=400, duration=0.5)
            elif sound_name == 'tick':
                sound = self._generate_beep_sound(frequency=1000, duration=0.1)
            else:
                sound = self._generate_beep_sound(frequency=700, duration=0.2)
                
            sound.set_volume(self.volume)
            self.sounds[sound_name] = sound
            
        except Exception as e:
            print(f"Error creating default sound for {sound_name}: {e}")
            
    def _generate_beep_sound(self, frequency: int, duration: float) -> pygame.mixer.Sound:
        import numpy as np
        
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        arr = np.zeros((frames, 2), dtype=np.int16)
        
        for i in range(frames):
            wave = int(32767 * np.sin(2 * np.pi * frequency * i / sample_rate))
            arr[i] = [wave, wave]
            
        return pygame.mixer.Sound(arr)
        
    def play_work_complete_sound(self):
        self._play_sound('work_complete')
        
    def play_break_complete_sound(self):
        self._play_sound('break_complete')
        
    def play_long_break_complete_sound(self):
        self._play_sound('long_break_complete')
        
    def play_tick_sound(self):
        self._play_sound('tick')
        
    def play_notification_sound(self):
        self._play_sound('notification')
        
    def _play_sound(self, sound_name: str):
        if not self.sound_enabled:
            return
            
        if sound_name in self.sounds:
            try:
                threading.Thread(
                    target=self._play_sound_thread,
                    args=(sound_name,),
                    daemon=True
                ).start()
            except Exception as e:
                print(f"Error playing sound {sound_name}: {e}")
                
    def _play_sound_thread(self, sound_name: str):
        try:
            self.sounds[sound_name].play()
        except Exception as e:
            print(f"Error in sound thread for {sound_name}: {e}")
            
    def set_volume(self, volume: float):
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.volume)
            
    def get_volume(self) -> float:
        return self.volume
        
    def set_sound_enabled(self, enabled: bool):
        self.sound_enabled = enabled
        
    def is_sound_enabled(self) -> bool:
        return self.sound_enabled
        
    def stop_all_sounds(self):
        try:
            pygame.mixer.stop()
        except Exception as e:
            print(f"Error stopping sounds: {e}")
            
    def load_custom_sound(self, sound_name: str, file_path: str) -> bool:
        try:
            if os.path.exists(file_path):
                sound = pygame.mixer.Sound(file_path)
                sound.set_volume(self.volume)
                self.sounds[sound_name] = sound
                return True
        except Exception as e:
            print(f"Error loading custom sound {file_path}: {e}")
        return False
        
    def remove_sound(self, sound_name: str) -> bool:
        if sound_name in self.sounds:
            del self.sounds[sound_name]
            return True
        return False
        
    def get_available_sounds(self) -> list:
        return list(self.sounds.keys())
        
    def test_sound(self, sound_name: str):
        if sound_name in self.sounds:
            self._play_sound(sound_name)
            
    def fade_out_all_sounds(self, time_ms: int = 1000):
        try:
            pygame.mixer.fadeout(time_ms)
        except Exception as e:
            print(f"Error fading out sounds: {e}")
            
    def create_audio_directory(self):
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        
    def cleanup(self):
        try:
            pygame.mixer.quit()
        except Exception as e:
            print(f"Error during audio cleanup: {e}")
            
    def get_audio_info(self) -> dict:
        return {
            'volume': self.volume,
            'sound_enabled': self.sound_enabled,
            'available_sounds': self.get_available_sounds(),
            'mixer_initialized': pygame.mixer.get_init() is not None
        }
        
    def save_audio_file(self, sound_name: str, file_path: str):
        if sound_name in self.sounds:
            try:
                save_path = self.audio_dir / f"{sound_name}.wav"
                self.create_audio_directory()
                
                import wave
                import numpy as np
                
                # Convert pygame.mixer.Sound to wave file
                # This is a simplified approach - actual implementation would depend on pygame version
                print(f"Audio file would be saved to: {save_path}")
                
            except Exception as e:
                print(f"Error saving audio file: {e}")
                
    def __del__(self):
        self.cleanup()