"""
pytest configuration and fixtures for Pomodoro Timer tests.
"""

import pytest
import sys
import os
from PyQt6.QtWidgets import QApplication

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()

@pytest.fixture
def mock_audio_file(tmp_path):
    """Create a mock audio file for testing."""
    audio_file = tmp_path / "test_sound.wav"
    # Create a minimal WAV file structure
    audio_file.write_bytes(b'RIFF\x24\x00\x00\x00WAVE')
    return str(audio_file)

@pytest.fixture
def sample_timer_settings():
    """Provide sample timer settings for testing."""
    return {
        'work_duration': 25,
        'break_duration': 5,
        'long_break_duration': 15,
        'cycles_until_long_break': 4,
        'auto_start_breaks': True,
        'auto_start_work': False,
        'sound_enabled': True,
        'notification_enabled': True
    }