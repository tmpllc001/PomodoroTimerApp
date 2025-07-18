from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json
import os
from dataclasses import dataclass, asdict
from enum import Enum

from .timer_model import SessionType


@dataclass
class Session:
    session_type: SessionType
    start_time: datetime
    planned_duration: int
    end_time: Optional[datetime] = None
    actual_duration: Optional[int] = None
    completed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'session_type': self.session_type.value,
            'start_time': self.start_time.isoformat(),
            'planned_duration': self.planned_duration,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'actual_duration': self.actual_duration,
            'completed': self.completed
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        return cls(
            session_type=SessionType(data['session_type']),
            start_time=datetime.fromisoformat(data['start_time']),
            planned_duration=data['planned_duration'],
            end_time=datetime.fromisoformat(data['end_time']) if data['end_time'] else None,
            actual_duration=data['actual_duration'],
            completed=data['completed']
        )


class SessionModel:
    def __init__(self, data_file: str = "sessions.json"):
        self.data_file = data_file
        self.sessions: List[Session] = []
        self.current_session: Optional[Session] = None
        self._load_sessions()
        
    def _load_sessions(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.sessions = [Session.from_dict(session_data) for session_data in data]
        except Exception as e:
            print(f"Error loading sessions: {e}")
            self.sessions = []
            
    def _save_sessions(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump([session.to_dict() for session in self.sessions], f, indent=2)
        except Exception as e:
            print(f"Error saving sessions: {e}")
            
    def start_session(self, session: Session):
        self.current_session = session
        
    def complete_session(self, actual_duration: int, completed: bool):
        if self.current_session:
            self.current_session.end_time = datetime.now()
            self.current_session.actual_duration = actual_duration
            self.current_session.completed = completed
            
            self.sessions.append(self.current_session)
            self._save_sessions()
            self.current_session = None
            
    def get_session_stats(self) -> Dict[str, Any]:
        if not self.sessions:
            return {
                'total_sessions': 0,
                'completed_sessions': 0,
                'total_work_time': 0,
                'total_break_time': 0,
                'completion_rate': 0.0,
                'average_work_duration': 0,
                'longest_streak': 0
            }
            
        total_sessions = len(self.sessions)
        completed_sessions = sum(1 for session in self.sessions if session.completed)
        
        total_work_time = sum(
            session.actual_duration or 0 
            for session in self.sessions 
            if session.session_type == SessionType.WORK
        )
        
        total_break_time = sum(
            session.actual_duration or 0 
            for session in self.sessions 
            if session.session_type in [SessionType.SHORT_BREAK, SessionType.LONG_BREAK]
        )
        
        completion_rate = (completed_sessions / total_sessions) * 100 if total_sessions > 0 else 0
        
        work_sessions = [s for s in self.sessions if s.session_type == SessionType.WORK and s.actual_duration]
        average_work_duration = (
            sum(s.actual_duration for s in work_sessions) / len(work_sessions) 
            if work_sessions else 0
        )
        
        longest_streak = self._calculate_longest_streak()
        
        return {
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'total_work_time': total_work_time,
            'total_break_time': total_break_time,
            'completion_rate': completion_rate,
            'average_work_duration': average_work_duration,
            'longest_streak': longest_streak
        }
        
    def get_today_sessions(self) -> List[Session]:
        today = datetime.now().date()
        return [
            session for session in self.sessions 
            if session.start_time.date() == today
        ]
        
    def get_weekly_stats(self) -> Dict[str, Any]:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=6)
        
        weekly_sessions = [
            session for session in self.sessions 
            if start_date <= session.start_time.date() <= end_date
        ]
        
        daily_stats = {}
        for i in range(7):
            date = start_date + timedelta(days=i)
            daily_sessions = [s for s in weekly_sessions if s.start_time.date() == date]
            
            work_sessions = [s for s in daily_sessions if s.session_type == SessionType.WORK and s.completed]
            total_work_time = sum(s.actual_duration or 0 for s in work_sessions)
            
            daily_stats[date.strftime('%Y-%m-%d')] = {
                'total_sessions': len(daily_sessions),
                'completed_work_sessions': len(work_sessions),
                'total_work_time': total_work_time
            }
            
        return daily_stats
        
    def get_monthly_stats(self) -> Dict[str, Any]:
        end_date = datetime.now().date()
        start_date = end_date.replace(day=1)
        
        monthly_sessions = [
            session for session in self.sessions 
            if start_date <= session.start_time.date() <= end_date
        ]
        
        work_sessions = [s for s in monthly_sessions if s.session_type == SessionType.WORK]
        completed_work_sessions = [s for s in work_sessions if s.completed]
        
        total_work_time = sum(s.actual_duration or 0 for s in completed_work_sessions)
        average_daily_work = total_work_time / (end_date - start_date).days if (end_date - start_date).days > 0 else 0
        
        return {
            'total_sessions': len(monthly_sessions),
            'work_sessions': len(work_sessions),
            'completed_work_sessions': len(completed_work_sessions),
            'total_work_time': total_work_time,
            'average_daily_work': average_daily_work,
            'completion_rate': (len(completed_work_sessions) / len(work_sessions)) * 100 if work_sessions else 0
        }
        
    def _calculate_longest_streak(self) -> int:
        if not self.sessions:
            return 0
            
        work_sessions = [s for s in self.sessions if s.session_type == SessionType.WORK]
        if not work_sessions:
            return 0
            
        work_sessions.sort(key=lambda x: x.start_time)
        
        current_streak = 0
        longest_streak = 0
        last_date = None
        
        for session in work_sessions:
            if session.completed:
                session_date = session.start_time.date()
                
                if last_date is None or session_date == last_date:
                    current_streak += 1
                elif session_date == last_date + timedelta(days=1):
                    current_streak += 1
                else:
                    current_streak = 1
                    
                longest_streak = max(longest_streak, current_streak)
                last_date = session_date
            else:
                current_streak = 0
                
        return longest_streak
        
    def get_productivity_score(self) -> float:
        recent_sessions = self.get_recent_sessions(days=7)
        if not recent_sessions:
            return 0.0
            
        work_sessions = [s for s in recent_sessions if s.session_type == SessionType.WORK]
        if not work_sessions:
            return 0.0
            
        completed_work = sum(1 for s in work_sessions if s.completed)
        completion_rate = completed_work / len(work_sessions)
        
        total_work_time = sum(s.actual_duration or 0 for s in work_sessions if s.completed)
        planned_work_time = sum(s.planned_duration for s in work_sessions if s.completed)
        
        efficiency = (total_work_time / planned_work_time) if planned_work_time > 0 else 0
        
        score = (completion_rate * 0.6 + efficiency * 0.4) * 100
        return min(100, max(0, score))
        
    def get_recent_sessions(self, days: int = 7) -> List[Session]:
        cutoff_date = datetime.now() - timedelta(days=days)
        return [
            session for session in self.sessions 
            if session.start_time >= cutoff_date
        ]
        
    def delete_session(self, session_index: int) -> bool:
        if 0 <= session_index < len(self.sessions):
            del self.sessions[session_index]
            self._save_sessions()
            return True
        return False
        
    def export_sessions(self, start_date: Optional[datetime] = None, 
                       end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        filtered_sessions = self.sessions
        
        if start_date:
            filtered_sessions = [s for s in filtered_sessions if s.start_time >= start_date]
        if end_date:
            filtered_sessions = [s for s in filtered_sessions if s.start_time <= end_date]
            
        return [session.to_dict() for session in filtered_sessions]