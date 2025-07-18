#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
セッションデータモデル
統計機能用のデータ構造定義
"""

import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class SessionData:
    """セッションデータの基本構造"""
    session_id: str
    session_type: str  # 'work', 'short_break', 'long_break'
    start_time: datetime
    end_time: Optional[datetime] = None
    planned_duration: int = 0  # 分
    actual_duration: int = 0   # 分
    completed: bool = False
    productivity_rating: Optional[int] = None  # 1-5
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'session_id': self.session_id,
            'session_type': self.session_type,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'planned_duration': self.planned_duration,
            'actual_duration': self.actual_duration,
            'completed': self.completed,
            'productivity_rating': self.productivity_rating,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionData':
        """辞書からセッションデータを作成"""
        return cls(
            session_id=data['session_id'],
            session_type=data['session_type'],
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']) if data['end_time'] else None,
            planned_duration=data.get('planned_duration', 0),
            actual_duration=data.get('actual_duration', 0),
            completed=data.get('completed', False),
            productivity_rating=data.get('productivity_rating'),
            notes=data.get('notes')
        )
    
    def get_duration_minutes(self) -> int:
        """実際の継続時間を分単位で取得"""
        if self.end_time and self.start_time:
            duration = self.end_time - self.start_time
            return int(duration.total_seconds() / 60)
        return self.actual_duration


@dataclass
class DailyStats:
    """日別統計データ"""
    date: str  # YYYY-MM-DD
    work_sessions: int = 0
    break_sessions: int = 0
    work_time: int = 0  # 分
    break_time: int = 0  # 分
    completed_sessions: int = 0
    productivity_score: float = 0.0
    focus_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DailyStats':
        """辞書から日別統計を作成"""
        return cls(**data)


@dataclass
class WeeklyStats:
    """週別統計データ"""
    week_key: str  # YYYY-WNN
    work_sessions: int = 0
    break_sessions: int = 0
    work_time: int = 0  # 分
    break_time: int = 0  # 分
    completed_sessions: int = 0
    productivity_score: float = 0.0
    focus_score: float = 0.0
    best_day: Optional[str] = None
    streak_days: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WeeklyStats':
        """辞書から週別統計を作成"""
        return cls(**data)


class SessionDataManager:
    """セッションデータの管理クラス"""
    
    def __init__(self, data_file: str = "data/statistics.json"):
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.sessions: List[SessionData] = []
        self.daily_stats: Dict[str, DailyStats] = {}
        self.weekly_stats: Dict[str, WeeklyStats] = {}
        
        self._load_data()
        logger.info(f"📊 セッションデータ管理初期化完了 (ファイル: {data_file})")
    
    def _load_data(self):
        """データファイルから読み込み"""
        if not self.data_file.exists():
            logger.info("📊 新規データファイルを作成")
            self._save_data()
            return
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # セッションデータ読み込み
            self.sessions = [
                SessionData.from_dict(session_data) 
                for session_data in data.get('sessions', [])
            ]
            
            # 日別統計読み込み
            self.daily_stats = {
                date: DailyStats.from_dict(stats_data)
                for date, stats_data in data.get('daily_stats', {}).items()
            }
            
            # 週別統計読み込み
            self.weekly_stats = {
                week: WeeklyStats.from_dict(stats_data)
                for week, stats_data in data.get('weekly_stats', {}).items()
            }
            
            logger.info(f"📊 データ読み込み完了: {len(self.sessions)}セッション")
            
        except Exception as e:
            logger.error(f"📊 データ読み込みエラー: {e}")
            self._initialize_empty_data()
    
    def _save_data(self):
        """データファイルに保存"""
        try:
            data = {
                'sessions': [session.to_dict() for session in self.sessions],
                'daily_stats': {
                    date: stats.to_dict() 
                    for date, stats in self.daily_stats.items()
                },
                'weekly_stats': {
                    week: stats.to_dict() 
                    for week, stats in self.weekly_stats.items()
                },
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug("📊 データ保存完了")
            
        except Exception as e:
            logger.error(f"📊 データ保存エラー: {e}")
    
    def _initialize_empty_data(self):
        """空のデータで初期化"""
        self.sessions = []
        self.daily_stats = {}
        self.weekly_stats = {}
    
    def add_session(self, session: SessionData):
        """セッションを追加"""
        self.sessions.append(session)
        self._update_stats(session)
        self._save_data()
        logger.info(f"📊 セッション追加: {session.session_type} ({session.actual_duration}分)")
    
    def update_session(self, session_id: str, **kwargs):
        """セッションを更新"""
        for session in self.sessions:
            if session.session_id == session_id:
                for key, value in kwargs.items():
                    if hasattr(session, key):
                        setattr(session, key, value)
                
                self._update_stats(session)
                self._save_data()
                logger.info(f"📊 セッション更新: {session_id}")
                return True
        
        logger.warning(f"📊 セッション未発見: {session_id}")
        return False
    
    def _update_stats(self, session: SessionData):
        """統計データを更新"""
        if not session.start_time:
            return
        
        date_key = session.start_time.strftime('%Y-%m-%d')
        week_key = f"{session.start_time.year}-W{session.start_time.isocalendar()[1]:02d}"
        
        # 日別統計更新
        if date_key not in self.daily_stats:
            self.daily_stats[date_key] = DailyStats(date=date_key)
        
        daily = self.daily_stats[date_key]
        if session.session_type == 'work':
            daily.work_sessions += 1
            daily.work_time += session.actual_duration
        else:  # break
            daily.break_sessions += 1
            daily.break_time += session.actual_duration
        
        if session.completed:
            daily.completed_sessions += 1
        
        # 週別統計更新
        if week_key not in self.weekly_stats:
            self.weekly_stats[week_key] = WeeklyStats(week_key=week_key)
        
        weekly = self.weekly_stats[week_key]
        if session.session_type == 'work':
            weekly.work_sessions += 1
            weekly.work_time += session.actual_duration
        else:  # break
            weekly.break_sessions += 1
            weekly.break_time += session.actual_duration
        
        if session.completed:
            weekly.completed_sessions += 1
    
    def get_today_stats(self) -> DailyStats:
        """今日の統計を取得"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.daily_stats.get(today, DailyStats(date=today))
    
    def get_week_stats(self) -> WeeklyStats:
        """今週の統計を取得"""
        now = datetime.now()
        week_key = f"{now.year}-W{now.isocalendar()[1]:02d}"
        return self.weekly_stats.get(week_key, WeeklyStats(week_key=week_key))
    
    def get_recent_sessions(self, limit: int = 10) -> List[SessionData]:
        """最近のセッションを取得"""
        return sorted(self.sessions, key=lambda s: s.start_time, reverse=True)[:limit]
    
    def get_sessions_by_date(self, date: str) -> List[SessionData]:
        """指定日のセッションを取得"""
        return [
            session for session in self.sessions
            if session.start_time.strftime('%Y-%m-%d') == date
        ]
    
    def get_sessions_by_week(self, week_key: str) -> List[SessionData]:
        """指定週のセッションを取得"""
        return [
            session for session in self.sessions
            if f"{session.start_time.year}-W{session.start_time.isocalendar()[1]:02d}" == week_key
        ]
    
    def calculate_productivity_score(self, date: str) -> float:
        """生産性スコアを計算"""
        sessions = self.get_sessions_by_date(date)
        if not sessions:
            return 0.0
        
        work_sessions = [s for s in sessions if s.session_type == 'work' and s.completed]
        if not work_sessions:
            return 0.0
        
        # 完了率とセッション数を考慮
        completion_rate = len(work_sessions) / len([s for s in sessions if s.session_type == 'work'])
        session_score = min(1.0, len(work_sessions) / 8)  # 8セッションを理想とする
        
        return round((completion_rate * 0.6 + session_score * 0.4) * 100, 1)
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """統計サマリーを取得"""
        today = self.get_today_stats()
        week = self.get_week_stats()
        total_sessions = len(self.sessions)
        total_work_time = sum(s.actual_duration for s in self.sessions if s.session_type == 'work')
        
        return {
            'today': {
                'work_sessions': today.work_sessions,
                'work_time': today.work_time,
                'break_time': today.break_time,
                'productivity_score': self.calculate_productivity_score(today.date)
            },
            'week': {
                'work_sessions': week.work_sessions,
                'work_time': week.work_time,
                'break_time': week.break_time
            },
            'total': {
                'sessions': total_sessions,
                'work_time': total_work_time
            }
        }
    
    def cleanup_old_data(self, days_to_keep: int = 90):
        """古いデータをクリーンアップ"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # 古いセッションを削除
        old_count = len(self.sessions)
        self.sessions = [s for s in self.sessions if s.start_time >= cutoff_date]
        new_count = len(self.sessions)
        
        if old_count > new_count:
            logger.info(f"📊 古いデータクリーンアップ: {old_count - new_count}セッション削除")
            self._save_data()
    
    def export_data(self, export_path: str) -> bool:
        """データをエクスポート"""
        try:
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            export_data = {
                'export_date': datetime.now().isoformat(),
                'sessions': [session.to_dict() for session in self.sessions],
                'daily_stats': {date: stats.to_dict() for date, stats in self.daily_stats.items()},
                'weekly_stats': {week: stats.to_dict() for week, stats in self.weekly_stats.items()},
                'summary': self.get_stats_summary()
            }
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📊 データエクスポート完了: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"📊 データエクスポートエラー: {e}")
            return False