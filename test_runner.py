#!/usr/bin/env python3
"""
Test runner for Pomodoro Timer tests that can run without PyQt6 dependencies.
"""

import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

def run_basic_tests():
    """Run basic tests without GUI dependencies."""
    print("Running basic unit tests...")
    
    # Test timer model
    print("\n=== Testing TimerModel ===")
    try:
        from tests.test_timer_model import MockTimerModel, TestTimerModel
        test_suite = TestTimerModel()
        test_suite.setup_method()
        
        # Run key tests
        test_methods = [
            'test_initialization',
            'test_start_timer',
            'test_pause_timer',
            'test_resume_timer',
            'test_stop_timer',
            'test_reset_timer',
            'test_tick_function',
            'test_get_formatted_time',
            'test_get_progress_percentage'
        ]
        
        passed = 0
        total = len(test_methods)
        
        for method_name in test_methods:
            try:
                method = getattr(test_suite, method_name)
                method()
                print(f"✅ {method_name}")
                passed += 1
            except Exception as e:
                print(f"❌ {method_name}: {str(e)}")
                
        print(f"\nTimerModel Tests: {passed}/{total} passed")
        
    except Exception as e:
        print(f"Failed to run TimerModel tests: {e}")
    
    # Test audio manager
    print("\n=== Testing AudioManager ===")
    try:
        from tests.test_audio_manager import MockAudioManager, TestAudioManager
        test_suite = TestAudioManager()
        test_suite.setup_method()
        
        test_methods = [
            'test_initialization',
            'test_play_notification_success',
            'test_play_bgm_success',
            'test_pause_bgm_success',
            'test_resume_bgm_success',
            'test_stop_bgm_success',
            'test_set_volume_valid',
            'test_toggle_sound',
            'test_get_audio_info'
        ]
        
        passed = 0
        total = len(test_methods)
        
        for method_name in test_methods:
            try:
                method = getattr(test_suite, method_name)
                method()
                print(f"✅ {method_name}")
                passed += 1
            except Exception as e:
                print(f"❌ {method_name}: {str(e)}")
                
        print(f"\nAudioManager Tests: {passed}/{total} passed")
        
    except Exception as e:
        print(f"Failed to run AudioManager tests: {e}")
    
    print("\n=== Test Summary ===")
    print("✅ Basic unit tests completed")
    print("Note: GUI tests require PyQt6 to be installed")
    print("Run 'pip install -r requirements.txt' to install all dependencies")

if __name__ == "__main__":
    run_basic_tests()