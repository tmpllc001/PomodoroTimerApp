#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
タスク統合機能
ポモドーロタイマーとタスク管理の連携
"""

from PyQt6.QtCore import QObject, pyqtSignal
from typing import Optional
import logging

from .task_manager import TaskManager, Task
from ..statistics import PomodoroStatistics

logger = logging.getLogger(__name__)

class TaskIntegration(QObject):
    """タスクとポモドーロの統合管理クラス"""
    
    # シグナル
    taskStarted = pyqtSignal(str)      # task_id
    taskCompleted = pyqtSignal(str)    # task_id
    pomodoroCompleted = pyqtSignal(str, int)  # task_id, duration
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.task_manager = TaskManager()
        self.statistics = PomodoroStatistics()
        self.current_session_task_id = None
        self.session_start_time = None
        
    def start_session_with_task(self, task_id: Optional[str] = None) -> bool:
        """タスクと連携してセッションを開始"""
        try:
            # 現在のタスクを取得（指定されていない場合）
            if task_id is None:
                current_task = self.task_manager.get_current_task()
                if current_task:
                    task_id = current_task.task_id
            
            # タスクの存在確認
            if task_id:
                task = self.task_manager.get_task(task_id)
                if not task:
                    logger.warning(f"⚠️ タスクが見つかりません: {task_id}")
                    return False
                
                # タスクを現在のタスクに設定
                self.task_manager.set_current_task(task_id)
                self.current_session_task_id = task_id
                
                logger.info(f"🎯 タスクセッション開始: {task.title}")
                self.taskStarted.emit(task_id)
            else:
                # タスクなしでセッション開始
                self.current_session_task_id = None
                logger.info("🍅 タスクなしセッション開始")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ セッション開始エラー: {e}")
            return False
    
    def complete_session(self, session_type: str, duration_minutes: int) -> bool:
        """セッション完了処理"""
        try:
            # 統計にセッションを記録
            self.statistics.record_session(session_type, duration_minutes)
            
            # 作業セッションの場合のみタスクを更新
            if session_type == 'work' and self.current_session_task_id:
                task = self.task_manager.get_task(self.current_session_task_id)
                if task:
                    # タスクにポモドーロを追加
                    self.task_manager.add_pomodoro_to_task(self.current_session_task_id)
                    
                    # 完了チェック
                    updated_task = self.task_manager.get_task(self.current_session_task_id)
                    if updated_task and updated_task.status == 'completed':
                        logger.info(f"🎉 タスク完了: {updated_task.title}")
                        self.taskCompleted.emit(self.current_session_task_id)
                    
                    logger.info(f"📊 ポモドーロ完了: {task.title} ({duration_minutes}分)")
                    self.pomodoroCompleted.emit(self.current_session_task_id, duration_minutes)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ セッション完了処理エラー: {e}")
            return False
    
    def get_current_task_info(self) -> Optional[dict]:
        """現在のタスク情報を取得"""
        current_task = self.task_manager.get_current_task()
        if not current_task:
            return None
            
        return {
            'task_id': current_task.task_id,
            'title': current_task.title,
            'description': current_task.description,
            'priority': current_task.priority,
            'priority_name': current_task.get_priority_name(),
            'priority_color': current_task.get_priority_color(),
            'estimated_pomodoros': current_task.estimated_pomodoros,
            'actual_pomodoros': current_task.actual_pomodoros,
            'completion_percentage': current_task.get_completion_percentage(),
            'status': current_task.status,
            'tags': current_task.tags
        }
    
    def get_session_task_info(self) -> Optional[dict]:
        """セッション中のタスク情報を取得"""
        if not self.current_session_task_id:
            return None
            
        task = self.task_manager.get_task(self.current_session_task_id)
        if not task:
            return None
            
        return {
            'task_id': task.task_id,
            'title': task.title,
            'description': task.description,
            'priority': task.priority,
            'priority_name': task.get_priority_name(),
            'priority_color': task.get_priority_color(),
            'estimated_pomodoros': task.estimated_pomodoros,
            'actual_pomodoros': task.actual_pomodoros,
            'completion_percentage': task.get_completion_percentage(),
            'status': task.status,
            'tags': task.tags
        }
    
    def get_today_task_summary(self) -> dict:
        """今日のタスク概要を取得"""
        try:
            # 今日の統計
            today_stats = self.statistics.get_today_stats()
            
            # タスク統計
            task_stats = self.task_manager.get_task_statistics()
            
            # 進行中のタスク
            in_progress_tasks = self.task_manager.get_tasks_by_status(
                self.task_manager.TaskStatus.IN_PROGRESS
            )
            
            # 完了したタスク
            completed_tasks = self.task_manager.get_tasks_by_status(
                self.task_manager.TaskStatus.COMPLETED
            )
            
            return {
                'work_sessions': today_stats.get('work_sessions', 0),
                'work_time': today_stats.get('work_time', 0),
                'total_tasks': task_stats['total_tasks'],
                'completed_tasks': len(completed_tasks),
                'in_progress_tasks': len(in_progress_tasks),
                'completion_rate': task_stats['completion_rate'],
                'current_task': self.get_current_task_info()
            }
            
        except Exception as e:
            logger.error(f"❌ 今日のタスク概要取得エラー: {e}")
            return {
                'work_sessions': 0,
                'work_time': 0,
                'total_tasks': 0,
                'completed_tasks': 0,
                'in_progress_tasks': 0,
                'completion_rate': 0.0,
                'current_task': None
            }
    
    def get_recommended_tasks(self, limit: int = 5) -> list:
        """推奨タスクを取得"""
        try:
            # 保留中のタスクを優先度順で取得
            pending_tasks = self.task_manager.get_tasks_by_status(
                self.task_manager.TaskStatus.PENDING
            )
            
            # 進行中のタスクを追加
            in_progress_tasks = self.task_manager.get_tasks_by_status(
                self.task_manager.TaskStatus.IN_PROGRESS
            )
            
            # 優先度順でソート
            all_tasks = pending_tasks + in_progress_tasks
            all_tasks.sort(key=lambda t: (-t.priority, t.created_at))
            
            # 推奨タスクの情報を作成
            recommendations = []
            for task in all_tasks[:limit]:
                recommendations.append({
                    'task_id': task.task_id,
                    'title': task.title,
                    'priority': task.priority,
                    'priority_name': task.get_priority_name(),
                    'priority_color': task.get_priority_color(),
                    'estimated_pomodoros': task.estimated_pomodoros,
                    'actual_pomodoros': task.actual_pomodoros,
                    'completion_percentage': task.get_completion_percentage(),
                    'status': task.status
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ 推奨タスク取得エラー: {e}")
            return []
    
    def create_quick_task(self, title: str, priority: int = 3, 
                         estimated_pomodoros: int = 1) -> Optional[str]:
        """クイックタスクを作成"""
        try:
            task_id = self.task_manager.create_task(
                title=title,
                priority=priority,
                estimated_pomodoros=estimated_pomodoros
            )
            logger.info(f"📋 クイックタスク作成: {title}")
            return task_id
            
        except Exception as e:
            logger.error(f"❌ クイックタスク作成エラー: {e}")
            return None
    
    def get_task_analytics(self) -> dict:
        """タスク分析データを取得"""
        try:
            all_tasks = self.task_manager.get_all_tasks()
            
            if not all_tasks:
                return {
                    'total_tasks': 0,
                    'avg_completion_time': 0,
                    'priority_distribution': {},
                    'productivity_trend': []
                }
            
            # 優先度別分布
            priority_dist = {}
            for task in all_tasks:
                priority_name = task.get_priority_name()
                priority_dist[priority_name] = priority_dist.get(priority_name, 0) + 1
            
            # 完了時間の平均
            completed_tasks = [t for t in all_tasks if t.completed_at]
            avg_completion_time = 0
            if completed_tasks:
                total_time = sum(
                    (t.completed_at - t.created_at).total_seconds() / 3600
                    for t in completed_tasks
                )
                avg_completion_time = total_time / len(completed_tasks)
            
            return {
                'total_tasks': len(all_tasks),
                'avg_completion_time': avg_completion_time,
                'priority_distribution': priority_dist,
                'productivity_trend': []  # 後で実装
            }
            
        except Exception as e:
            logger.error(f"❌ タスク分析エラー: {e}")
            return {
                'total_tasks': 0,
                'avg_completion_time': 0,
                'priority_distribution': {},
                'productivity_trend': []
            }
    
    def clear_session_task(self):
        """セッションタスクをクリア"""
        self.current_session_task_id = None
        self.session_start_time = None
        logger.info("🧹 セッションタスククリア")
    
    def get_task_manager(self) -> TaskManager:
        """タスクマネージャーを取得"""
        return self.task_manager