from enum import Enum
from datetime import datetime, timedelta
from typing import Optional, Callable
import threading
import time


class TimerState(Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"


class SessionType(Enum):
    WORK = "work"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"


class TimerModel:
    def __init__(self):
        self.work_duration = 25 * 60  # 25 minutes in seconds
        self.short_break_duration = 5 * 60  # 5 minutes in seconds
        self.long_break_duration = 15 * 60  # 15 minutes in seconds
        self.long_break_interval = 4  # After every 4 work sessions
        
        self.current_session_type = SessionType.WORK
        self.current_session_count = 0
        self.remaining_time = self.work_duration
        self.state = TimerState.STOPPED
        
        self.timer_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Callbacks
        self.on_tick: Optional[Callable[[int], None]] = None
        self.on_session_complete: Optional[Callable[[SessionType], None]] = None
        self.on_state_change: Optional[Callable[[TimerState], None]] = None
        
    def start(self):
        if self.state == TimerState.RUNNING:
            return
            
        self.state = TimerState.RUNNING
        self.stop_event.clear()
        
        if self.timer_thread is None or not self.timer_thread.is_alive():
            self.timer_thread = threading.Thread(target=self._timer_loop)
            self.timer_thread.daemon = True
            self.timer_thread.start()
            
        self._notify_state_change()
        
    def pause(self):
        if self.state == TimerState.RUNNING:
            self.state = TimerState.PAUSED
            self._notify_state_change()
            
    def resume(self):
        if self.state == TimerState.PAUSED:
            self.state = TimerState.RUNNING
            self._notify_state_change()
            
    def stop(self):
        self.state = TimerState.STOPPED
        self.stop_event.set()
        self._notify_state_change()
        
    def reset(self):
        self.stop()
        self.current_session_count = 0
        self.current_session_type = SessionType.WORK
        self.remaining_time = self.work_duration
        self._notify_tick()
        
    def skip_session(self):
        if self.state == TimerState.RUNNING:
            self.remaining_time = 0
            
    def _timer_loop(self):
        while not self.stop_event.is_set():
            if self.state == TimerState.RUNNING:
                if self.remaining_time > 0:
                    self.remaining_time -= 1
                    self._notify_tick()
                    
                    if self.remaining_time == 0:
                        self._handle_session_complete()
                        
                time.sleep(1)
            else:
                time.sleep(0.1)
                
    def _handle_session_complete(self):
        completed_session = self.current_session_type
        self._notify_session_complete(completed_session)
        
        if self.current_session_type == SessionType.WORK:
            self.current_session_count += 1
            
            if self.current_session_count % self.long_break_interval == 0:
                self.current_session_type = SessionType.LONG_BREAK
                self.remaining_time = self.long_break_duration
            else:
                self.current_session_type = SessionType.SHORT_BREAK
                self.remaining_time = self.short_break_duration
        else:
            self.current_session_type = SessionType.WORK
            self.remaining_time = self.work_duration
            
        self.state = TimerState.STOPPED
        self._notify_state_change()
        
    def _notify_tick(self):
        if self.on_tick:
            self.on_tick(self.remaining_time)
            
    def _notify_session_complete(self, session_type: SessionType):
        if self.on_session_complete:
            self.on_session_complete(session_type)
            
    def _notify_state_change(self):
        if self.on_state_change:
            self.on_state_change(self.state)
            
    def get_session_info(self) -> dict:
        return {
            'type': self.current_session_type,
            'count': self.current_session_count,
            'remaining_time': self.remaining_time,
            'state': self.state,
            'progress': self._calculate_progress()
        }
        
    def _calculate_progress(self) -> float:
        if self.current_session_type == SessionType.WORK:
            total_time = self.work_duration
        elif self.current_session_type == SessionType.SHORT_BREAK:
            total_time = self.short_break_duration
        else:
            total_time = self.long_break_duration
            
        return (total_time - self.remaining_time) / total_time
        
    def set_durations(self, work_duration: int, short_break_duration: int, 
                     long_break_duration: int, long_break_interval: int):
        if self.state == TimerState.STOPPED:
            self.work_duration = work_duration
            self.short_break_duration = short_break_duration
            self.long_break_duration = long_break_duration
            self.long_break_interval = long_break_interval
            
            if self.current_session_type == SessionType.WORK:
                self.remaining_time = self.work_duration
            elif self.current_session_type == SessionType.SHORT_BREAK:
                self.remaining_time = self.short_break_duration
            else:
                self.remaining_time = self.long_break_duration
                
    def format_time(self, seconds: int) -> str:
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
        
    def get_formatted_time(self) -> str:
        return self.format_time(self.remaining_time)