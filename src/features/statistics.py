#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本的な統計機能
Phase 2 追加機能
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import uuid

# 相対インポートから絶対インポートに変更
try:
    from ..models.session_data import SessionData, SessionDataManager, DailyStats, WeeklyStats
except ImportError:
    # 直接実行の場合の代替インポート
    try:
        from models.session_data import SessionData, SessionDataManager, DailyStats, WeeklyStats
    except ImportError:
        # session_dataモジュールが存在しない場合のフォールバック
        logger.warning("SessionDataManager not found, using fallback implementation")
        
        # 簡単なフォールバック実装
        class SessionData:
            def __init__(self, session_id, session_type, start_time, end_time, planned_duration, actual_duration, completed):
                self.session_id = session_id
                self.session_type = session_type
                self.start_time = start_time
                self.end_time = end_time
                self.planned_duration = planned_duration
                self.actual_duration = actual_duration
                self.completed = completed
        
        class DailyStats:
            def __init__(self):
                self.work_sessions = 0
                self.break_sessions = 0
                self.work_time = 0
                self.break_time = 0
        
        class WeeklyStats:
            def __init__(self):
                self.work_sessions = 0
                self.break_sessions = 0
                self.work_time = 0
                self.break_time = 0
        
        class SessionDataManager:
            def __init__(self, data_file):
                self.data_file = data_file
                self.sessions = []
                self._load_data()
            
            def _load_data(self):
                try:
                    import json
                    from pathlib import Path
                    
                    if Path(self.data_file).exists():
                        with open(self.data_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # 基本的なデータ構造を想定
                            self.sessions = []
                except Exception as e:
                    logger.warning(f"Failed to load session data: {e}")
                    self.sessions = []
            
            def add_session(self, session):
                self.sessions.append(session)
                self._save_data()
            
            def _save_data(self):
                try:
                    import json
                    from pathlib import Path
                    
                    # 基本的なデータ保存
                    data = {
                        'sessions': [
                            {
                                'session_id': s.session_id,
                                'session_type': s.session_type,
                                'start_time': s.start_time.isoformat(),
                                'end_time': s.end_time.isoformat(),
                                'planned_duration': s.planned_duration,
                                'actual_duration': s.actual_duration,
                                'completed': s.completed
                            }
                            for s in self.sessions
                        ]
                    }
                    
                    Path(self.data_file).parent.mkdir(parents=True, exist_ok=True)
                    with open(self.data_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                except Exception as e:
                    logger.warning(f"Failed to save session data: {e}")
            
            def get_today_stats(self):
                stats = DailyStats()
                today = datetime.now().date()
                
                for session in self.sessions:
                    if session.start_time.date() == today:
                        if session.session_type == 'work':
                            stats.work_sessions += 1
                            stats.work_time += session.actual_duration
                        else:
                            stats.break_sessions += 1
                            stats.break_time += session.actual_duration
                
                return stats
            
            def get_week_stats(self):
                stats = WeeklyStats()
                today = datetime.now().date()
                week_start = today - timedelta(days=today.weekday())
                
                for session in self.sessions:
                    if session.start_time.date() >= week_start:
                        if session.session_type == 'work':
                            stats.work_sessions += 1
                            stats.work_time += session.actual_duration
                        else:
                            stats.break_sessions += 1
                            stats.break_time += session.actual_duration
                
                return stats
            
            def get_recent_sessions(self, limit=10):
                return sorted(self.sessions, key=lambda x: x.start_time, reverse=True)[:limit]
            
            def calculate_productivity_score(self, date_str):
                today_stats = self.get_today_stats()
                work_sessions = today_stats.work_sessions
                if work_sessions == 0:
                    return 0.0
                ideal_sessions = 8
                return min(100.0, (work_sessions / ideal_sessions) * 100)

logger = logging.getLogger(__name__)

class PomodoroStatistics:
    """ポモドーロ統計管理クラス（SessionDataManager統合版）"""
    
    def __init__(self, data_file: str = "data/statistics.json"):
        # SessionDataManagerを使用してデータを管理
        self.session_manager = SessionDataManager(data_file)
        
        # 後方互換性のため、古いファイルがある場合は移行
        old_file = Path("pomodoro_stats.json")
        if old_file.exists() and not Path(data_file).exists():
            self._migrate_old_data(old_file)
        
        logger.info(f"📊 統計システム初期化完了 (データファイル: {data_file})")
    
    def _migrate_old_data(self, old_file: Path):
        """古いデータ形式から新しい形式に移行"""
        try:
            with open(old_file, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
            
            # 旧形式のセッション履歴を新形式に変換
            for session_data in old_data.get('session_history', []):
                session = SessionData(
                    session_id=str(uuid.uuid4()),
                    session_type=session_data['type'],
                    start_time=datetime.fromisoformat(session_data['timestamp']),
                    end_time=datetime.fromisoformat(session_data['timestamp']) + timedelta(minutes=session_data['duration']),
                    planned_duration=session_data['duration'],
                    actual_duration=session_data['duration'],
                    completed=True
                )
                self.session_manager.add_session(session)
            
            # 移行完了後、古いファイルをバックアップ
            old_file.rename(old_file.with_suffix('.json.backup'))
            logger.info(f"📊 古いデータを移行完了: {len(old_data.get('session_history', []))}セッション")
            
        except Exception as e:
            logger.error(f"📊 データ移行エラー: {e}")
    
    def record_session(self, session_type: str, duration_minutes: int, completed: bool = True):
        """セッションを記録"""
        now = datetime.now()
        session = SessionData(
            session_id=str(uuid.uuid4()),
            session_type=session_type,
            start_time=now - timedelta(minutes=duration_minutes),
            end_time=now,
            planned_duration=duration_minutes,
            actual_duration=duration_minutes,
            completed=completed
        )
        
        self.session_manager.add_session(session)
        logger.info(f"📊 セッション記録: {session_type} ({duration_minutes}分)")
    
    def get_today_stats(self) -> Dict:
        """今日の統計を取得"""
        daily_stats = self.session_manager.get_today_stats()
        return {
            'work_sessions': daily_stats.work_sessions,
            'break_sessions': daily_stats.break_sessions,
            'work_time': daily_stats.work_time,
            'break_time': daily_stats.break_time
        }
    
    def get_week_stats(self) -> Dict:
        """今週の統計を取得"""
        weekly_stats = self.session_manager.get_week_stats()
        return {
            'work_sessions': weekly_stats.work_sessions,
            'break_sessions': weekly_stats.break_sessions,
            'work_time': weekly_stats.work_time,
            'break_time': weekly_stats.break_time
        }
    
    def get_total_stats(self) -> Dict:
        """全体統計を取得"""
        all_sessions = self.session_manager.sessions
        total_work_time = sum(s.actual_duration for s in all_sessions if s.session_type == 'work')
        total_break_time = sum(s.actual_duration for s in all_sessions if s.session_type != 'work')
        
        return {
            'total_sessions': len(all_sessions),
            'total_work_time': total_work_time,
            'total_break_time': total_break_time,
            'total_time': total_work_time + total_break_time
        }
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict]:
        """最近のセッション履歴を取得"""
        recent_sessions = self.session_manager.get_recent_sessions(limit)
        return [
            {
                'timestamp': session.start_time.isoformat(),
                'type': session.session_type,
                'duration': session.actual_duration,
                'completed': session.completed
            }
            for session in recent_sessions
        ]
    
    def get_productivity_score(self) -> float:
        """生産性スコアを計算（0-100）"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.session_manager.calculate_productivity_score(today)
    
    def format_time(self, minutes: int) -> str:
        """時間を読みやすい形式にフォーマット"""
        if minutes < 60:
            return f"{minutes}分"
        
        hours = minutes // 60
        mins = minutes % 60
        
        if mins == 0:
            return f"{hours}時間"
        else:
            return f"{hours}時間{mins}分"
    
    def get_stats_summary(self) -> str:
        """統計サマリーを文字列で取得"""
        today = self.get_today_stats()
        week = self.get_week_stats()
        total = self.get_total_stats()
        productivity = self.get_productivity_score()
        
        return f"""📊 統計サマリー
        
今日の実績:
  作業セッション: {today.get('work_sessions', 0)}回
  作業時間: {self.format_time(today.get('work_time', 0))}
  休憩時間: {self.format_time(today.get('break_time', 0))}
  生産性スコア: {productivity}%

今週の実績:
  作業セッション: {week.get('work_sessions', 0)}回
  作業時間: {self.format_time(week.get('work_time', 0))}

全体の実績:
  総セッション数: {total['total_sessions']}回
  総作業時間: {self.format_time(total['total_work_time'])}
  総時間: {self.format_time(total['total_time'])}"""