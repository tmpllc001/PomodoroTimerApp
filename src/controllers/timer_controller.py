from datetime import datetime
from typing import Optional, Callable
import json
import os

from ..models.timer_model import TimerModel, TimerState, SessionType
from ..models.session_model import SessionModel, Session
from ..utils.audio_manager import AudioManager
from ..features.statistics import PomodoroStatistics


class TimerController:
    def __init__(self, config_path: str = "config.json"):
        self.timer_model = TimerModel()
        self.session_model = SessionModel()
        
        # 統計機能初期化
        try:
            self.statistics = PomodoroStatistics()
        except Exception as e:
            print(f"⚠️  統計機能初期化失敗: {e}")
            self.statistics = None
        
        # 音声管理の安全な初期化
        try:
            self.audio_manager = AudioManager()
        except Exception as e:
            print(f"⚠️  音声管理初期化失敗: {e}")
            # ダミー音声管理クラスを作成
            self.audio_manager = self._create_dummy_audio_manager()
            
        self.config_path = config_path
        
        self.on_timer_update: Optional[Callable[[dict], None]] = None
        self.on_session_complete: Optional[Callable[[SessionType], None]] = None
        self.on_state_change: Optional[Callable[[TimerState], None]] = None
        
        self._setup_callbacks()
        self._load_config()
        
    def _create_dummy_audio_manager(self):
        """音声が利用できない環境用のダミー音声管理."""
        class DummyAudioManager:
            def __init__(self):
                self.volume = 0.0
                self.sound_enabled = False
                
            def play_work_complete_sound(self): pass
            def play_break_complete_sound(self): pass  
            def play_long_break_complete_sound(self): pass
            def play_notification_sound(self): pass
            def set_volume(self, volume): self.volume = volume
            def get_volume(self): return self.volume
            def set_sound_enabled(self, enabled): self.sound_enabled = enabled
            def is_sound_enabled(self): return self.sound_enabled
            def cleanup(self): pass
            
        return DummyAudioManager()
        
    def _setup_callbacks(self):
        self.timer_model.on_tick = self._handle_timer_tick
        self.timer_model.on_session_complete = self._handle_session_complete
        self.timer_model.on_state_change = self._handle_state_change
        
    def _load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    
                self.timer_model.set_durations(
                    config.get('work_duration', 25 * 60),
                    config.get('short_break_duration', 5 * 60),
                    config.get('long_break_duration', 15 * 60),
                    config.get('long_break_interval', 4)
                )
                
                try:
                    self.audio_manager.set_volume(config.get('volume', 0.7))
                    self.audio_manager.set_sound_enabled(config.get('sound_enabled', True))
                except Exception as e:
                    print(f"⚠️  音声設定読み込み失敗: {e}")
                    # 音声が利用できない場合は無効化
                    if hasattr(self.audio_manager, 'set_sound_enabled'):
                        self.audio_manager.set_sound_enabled(False)
                
        except Exception as e:
            print(f"Error loading config: {e}")
            
    def save_config(self):
        try:
            config = {
                'work_duration': self.timer_model.work_duration,
                'short_break_duration': self.timer_model.short_break_duration,
                'long_break_duration': self.timer_model.long_break_duration,
                'long_break_interval': self.timer_model.long_break_interval,
                'volume': self.audio_manager.get_volume(),
                'sound_enabled': self.audio_manager.is_sound_enabled()
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def start_timer(self):
        if self.timer_model.state == TimerState.STOPPED:
            self._start_new_session()
        elif self.timer_model.state == TimerState.PAUSED:
            self.timer_model.resume()
        else:
            self.timer_model.start()
            
    def pause_timer(self):
        self.timer_model.pause()
        
    def stop_timer(self):
        if self.timer_model.state != TimerState.STOPPED:
            self._save_current_session()
        self.timer_model.stop()
        
    def reset_timer(self):
        self.timer_model.reset()
        
    def skip_session(self):
        self.timer_model.skip_session()
        
    def _start_new_session(self):
        session = Session(
            session_type=self.timer_model.current_session_type,
            start_time=datetime.now(),
            planned_duration=self._get_session_duration()
        )
        
        self.session_model.start_session(session)
        self.timer_model.start()
        
    def _get_session_duration(self) -> int:
        if self.timer_model.current_session_type == SessionType.WORK:
            return self.timer_model.work_duration
        elif self.timer_model.current_session_type == SessionType.SHORT_BREAK:
            return self.timer_model.short_break_duration
        else:
            return self.timer_model.long_break_duration
            
    def _save_current_session(self):
        if self.session_model.current_session:
            self.session_model.complete_session(
                actual_duration=self._get_session_duration() - self.timer_model.remaining_time,
                completed=False
            )
            
    def _handle_timer_tick(self, remaining_time: int):
        if self.on_timer_update:
            session_info = self.timer_model.get_session_info()
            self.on_timer_update(session_info)
            
    def _handle_session_complete(self, session_type: SessionType):
        if self.session_model.current_session:
            self.session_model.complete_session(
                actual_duration=self._get_session_duration(),
                completed=True
            )
            
        # 統計機能にセッションを記録
        if self.statistics:
            try:
                session_type_str = 'work' if session_type == SessionType.WORK else 'break'
                duration_minutes = self._get_session_duration() // 60  # 秒を分に変換
                self.statistics.record_session(session_type_str, duration_minutes, completed=True)
            except Exception as e:
                print(f"⚠️  統計記録エラー: {e}")
            
        self._play_completion_sound(session_type)
        
        if self.on_session_complete:
            self.on_session_complete(session_type)
            
    def _handle_state_change(self, state: TimerState):
        if self.on_state_change:
            self.on_state_change(state)
            
    def _play_completion_sound(self, session_type: SessionType):
        """セッション完了音の安全な再生."""
        try:
            if not self.audio_manager.is_sound_enabled():
                return
                
            if session_type == SessionType.WORK:
                self.audio_manager.play_work_complete_sound()
            elif session_type == SessionType.SHORT_BREAK:
                self.audio_manager.play_break_complete_sound()
            else:
                self.audio_manager.play_long_break_complete_sound()
                
        except Exception as e:
            print(f"⚠️  音声再生エラー: {e}")
            # 音声エラーが発生した場合は音声を無効化
            try:
                self.audio_manager.set_sound_enabled(False)
            except:
                pass
            
    def get_timer_info(self) -> dict:
        return self.timer_model.get_session_info()
        
    def get_session_stats(self) -> dict:
        return self.session_model.get_session_stats()
        
    def get_today_sessions(self) -> list:
        return self.session_model.get_today_sessions()
        
    def get_weekly_stats(self) -> dict:
        return self.session_model.get_weekly_stats()
        
    def set_durations(self, work_duration: int, short_break_duration: int, 
                     long_break_duration: int, long_break_interval: int):
        self.timer_model.set_durations(
            work_duration, short_break_duration, 
            long_break_duration, long_break_interval
        )
        self.save_config()
        
    def set_volume(self, volume: float):
        self.audio_manager.set_volume(volume)
        self.save_config()
        
    def set_sound_enabled(self, enabled: bool):
        self.audio_manager.set_sound_enabled(enabled)
        self.save_config()
        
    def get_volume(self) -> float:
        return self.audio_manager.get_volume()
        
    def is_sound_enabled(self) -> bool:
        return self.audio_manager.is_sound_enabled()
        
    def get_statistics(self):
        """統計オブジェクトを取得"""
        return self.statistics
    
    def get_statistics_summary(self) -> dict:
        """統計サマリーを取得"""
        if self.statistics:
            try:
                summary = {
                    'today': self.statistics.get_today_stats(),
                    'week': self.statistics.get_week_stats(),
                    'total': self.statistics.get_total_stats(),
                    'productivity_score': self.statistics.get_productivity_score(),
                    'recent_sessions': self.statistics.get_recent_sessions(5)
                }
                return summary
            except Exception as e:
                print(f"⚠️  統計サマリー取得エラー: {e}")
                return {}
        return {}
    
    def cleanup(self):
        self.timer_model.stop()
        if self.session_model.current_session:
            self.session_model.complete_session(
                actual_duration=self._get_session_duration() - self.timer_model.remaining_time,
                completed=False
            )
        self.audio_manager.cleanup()