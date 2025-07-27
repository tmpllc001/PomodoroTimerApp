#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
タスク管理システム
タスクの作成、編集、削除、進捗管理を行う
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """タスクのステータス"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    """タスクの優先度"""
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5

@dataclass
class Task:
    """タスクデータクラス"""
    task_id: str
    title: str
    description: str
    priority: int
    estimated_pomodoros: int
    actual_pomodoros: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        """辞書からTaskインスタンスを作成"""
        # datetime文字列をdatetimeオブジェクトに変換
        created_at = datetime.fromisoformat(data['created_at'])
        completed_at = None
        if data.get('completed_at'):
            completed_at = datetime.fromisoformat(data['completed_at'])
        
        return cls(
            task_id=data['task_id'],
            title=data['title'],
            description=data['description'],
            priority=data['priority'],
            estimated_pomodoros=data['estimated_pomodoros'],
            actual_pomodoros=data['actual_pomodoros'],
            status=data['status'],
            created_at=created_at,
            completed_at=completed_at,
            tags=data.get('tags', [])
        )
    
    def to_dict(self) -> Dict:
        """TaskインスタンスをJSON形式の辞書に変換"""
        try:
            # ステータスが文字列でない場合のエラーハンドリング
            status_value = self.status
            if hasattr(self.status, 'value'):
                status_value = self.status.value
            elif not isinstance(self.status, str):
                status_value = str(self.status)
                
            return {
                'task_id': self.task_id,
                'title': self.title,
                'description': self.description,
                'priority': self.priority,
                'estimated_pomodoros': self.estimated_pomodoros,
                'actual_pomodoros': self.actual_pomodoros,
                'status': status_value,
                'created_at': self.created_at.isoformat(),
                'completed_at': self.completed_at.isoformat() if self.completed_at else None,
                'tags': self.tags or []
            }
        except Exception as e:
            logger.error(f"❌ タスク辞書変換エラー: {e}")
            # デフォルト値で復旧
            return {
                'task_id': self.task_id,
                'title': self.title,
                'description': self.description,
                'priority': self.priority,
                'estimated_pomodoros': self.estimated_pomodoros,
                'actual_pomodoros': self.actual_pomodoros,
                'status': TaskStatus.PENDING.value,
                'created_at': self.created_at.isoformat(),
                'completed_at': self.completed_at.isoformat() if self.completed_at else None,
                'tags': self.tags or []
            }
    
    def get_completion_percentage(self) -> float:
        """完了率を計算"""
        if self.estimated_pomodoros == 0:
            return 0.0
        return min(100.0, (self.actual_pomodoros / self.estimated_pomodoros) * 100)
    
    def get_priority_color(self) -> str:
        """優先度に対応する色を取得"""
        colors = {
            1: "#95a5a6",  # VERY_LOW - グレー
            2: "#3498db",  # LOW - ブルー
            3: "#f39c12",  # MEDIUM - オレンジ
            4: "#e74c3c",  # HIGH - レッド
            5: "#9b59b6"   # VERY_HIGH - パープル
        }
        return colors.get(self.priority, "#95a5a6")
    
    def get_priority_name(self) -> str:
        """優先度の名前を取得"""
        names = {
            1: "最低",
            2: "低",
            3: "中",
            4: "高",
            5: "最高"
        }
        return names.get(self.priority, "中")

class TaskManager:
    """タスク管理クラス"""
    
    def __init__(self, data_file: str = "data/tasks.json"):
        self.data_file = Path(data_file)
        self.tasks: Dict[str, Task] = {}
        self.current_task_id: Optional[str] = None
        self.load_data()
        
    def load_data(self):
        """データファイルからタスクを読み込み"""
        try:
            if not self.data_file.exists():
                self.data_file.parent.mkdir(parents=True, exist_ok=True)
                self.save_data()
                logger.info(f"📋 新規タスクデータファイルを作成: {self.data_file}")
                return
            
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # タスクデータを読み込み
            for task_data in data.get('tasks', []):
                task = Task.from_dict(task_data)
                self.tasks[task.task_id] = task
            
            # 現在のタスクID
            self.current_task_id = data.get('current_task_id')
            
            logger.info(f"📋 タスクデータ読み込み完了: {len(self.tasks)}タスク")
            
        except Exception as e:
            logger.error(f"❌ タスクデータ読み込みエラー: {e}")
            self.tasks = {}
            self.current_task_id = None
    
    def save_data(self):
        """データファイルにタスクを保存"""
        try:
            data = {
                'tasks': [task.to_dict() for task in self.tasks.values()],
                'current_task_id': self.current_task_id,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📋 タスクデータ保存完了: {len(self.tasks)}タスク")
            
        except Exception as e:
            logger.error(f"❌ タスクデータ保存エラー: {e}")
    
    def create_task(self, title: str, description: str = "", 
                   priority: int = 3, estimated_pomodoros: int = 1,
                   tags: List[str] = None) -> str:
        """新しいタスクを作成"""
        task_id = str(uuid.uuid4())
        
        task = Task(
            task_id=task_id,
            title=title,
            description=description,
            priority=priority,
            estimated_pomodoros=estimated_pomodoros,
            actual_pomodoros=0,
            status=TaskStatus.PENDING.value,
            created_at=datetime.now(),
            tags=tags or []
        )
        
        self.tasks[task_id] = task
        self.save_data()
        
        logger.info(f"📋 新規タスク作成: {title} (ID: {task_id[:8]})")
        return task_id
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """タスクを更新"""
        try:
            if task_id not in self.tasks:
                logger.warning(f"⚠️ タスクが見つかりません: {task_id}")
                return False
            
            task = self.tasks[task_id]
            
            # 更新可能な属性
            updatable_attrs = ['title', 'description', 'priority', 'estimated_pomodoros', 
                              'actual_pomodoros', 'status', 'tags']
            
            for attr, value in kwargs.items():
                if attr in updatable_attrs:
                    # ステータス値の正規化
                    if attr == 'status':
                        if hasattr(value, 'value'):
                            value = value.value
                        elif not isinstance(value, str):
                            value = str(value)
                    setattr(task, attr, value)
            
            # 完了ステータスの場合は完了時刻を設定
            status_value = task.status
            if hasattr(task.status, 'value'):
                status_value = task.status.value
            
            if status_value == TaskStatus.COMPLETED.value and not task.completed_at:
                task.completed_at = datetime.now()
            
            self.save_data()
            logger.info(f"📋 タスク更新: {task.title} (ID: {task_id[:8]})")
            return True
            
        except Exception as e:
            logger.error(f"❌ タスク更新エラー: {e}")
            return False
    
    def delete_task(self, task_id: str) -> bool:
        """タスクを削除"""
        if task_id not in self.tasks:
            logger.warning(f"⚠️ タスクが見つかりません: {task_id}")
            return False
        
        task = self.tasks[task_id]
        title = task.title
        
        # 現在のタスクを削除する場合はクリア
        if self.current_task_id == task_id:
            self.current_task_id = None
        
        del self.tasks[task_id]
        self.save_data()
        
        logger.info(f"📋 タスク削除: {title} (ID: {task_id[:8]})")
        return True
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """タスクを取得"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        """すべてのタスクを取得"""
        return list(self.tasks.values())
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """ステータス別タスクを取得"""
        return [task for task in self.tasks.values() if task.status == status.value]
    
    def get_tasks_by_priority(self, priority: int) -> List[Task]:
        """優先度別タスクを取得"""
        return [task for task in self.tasks.values() if task.priority == priority]
    
    def get_current_task(self) -> Optional[Task]:
        """現在のタスクを取得"""
        if self.current_task_id:
            return self.tasks.get(self.current_task_id)
        return None
    
    def set_current_task(self, task_id: Optional[str]) -> bool:
        """現在のタスクを設定"""
        try:
            if task_id and task_id not in self.tasks:
                logger.warning(f"⚠️ タスクが見つかりません: {task_id}")
                return False
            
            # 前の現在タスクを進行中から保留に戻す
            if self.current_task_id and self.current_task_id in self.tasks:
                old_task = self.tasks[self.current_task_id]
                old_status = old_task.status
                if hasattr(old_status, 'value'):
                    old_status = old_status.value
                    
                if old_status == TaskStatus.IN_PROGRESS.value:
                    old_task.status = TaskStatus.PENDING.value
            
            self.current_task_id = task_id
            
            # 新しい現在タスクを進行中に設定
            if task_id:
                self.tasks[task_id].status = TaskStatus.IN_PROGRESS.value
                logger.info(f"📋 現在のタスク設定: {self.tasks[task_id].title}")
            else:
                logger.info("📋 現在のタスクをクリア")
            
            self.save_data()
            return True
            
        except Exception as e:
            logger.error(f"❌ 現在タスク設定エラー: {e}")
            return False
    
    def add_pomodoro_to_task(self, task_id: str, pomodoros: int = 1) -> bool:
        """タスクにポモドーロを追加"""
        try:
            if task_id not in self.tasks:
                logger.warning(f"⚠️ タスクが見つかりません: {task_id}")
                return False
            
            task = self.tasks[task_id]
            task.actual_pomodoros += pomodoros
            
            # 現在のステータスを確認
            current_status = task.status
            if hasattr(current_status, 'value'):
                current_status = current_status.value
            
            # 予定ポモドーロ数に達した場合は完了に設定
            if task.actual_pomodoros >= task.estimated_pomodoros:
                if current_status != TaskStatus.COMPLETED.value:
                    task.status = TaskStatus.COMPLETED.value
                    task.completed_at = datetime.now()
                    logger.info(f"🎉 タスク完了: {task.title}")
            
            self.save_data()
            logger.info(f"📋 ポモドーロ追加: {task.title} ({task.actual_pomodoros}/{task.estimated_pomodoros})")
            return True
            
        except Exception as e:
            logger.error(f"❌ ポモドーロ追加エラー: {e}")
            return False
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """タスク統計を取得"""
        all_tasks = self.get_all_tasks()
        
        if not all_tasks:
            return {
                'total_tasks': 0,
                'completed_tasks': 0,
                'pending_tasks': 0,
                'in_progress_tasks': 0,
                'total_pomodoros': 0,
                'completion_rate': 0.0,
                'average_pomodoros_per_task': 0.0
            }
        
        completed_tasks = self.get_tasks_by_status(TaskStatus.COMPLETED)
        pending_tasks = self.get_tasks_by_status(TaskStatus.PENDING)
        in_progress_tasks = self.get_tasks_by_status(TaskStatus.IN_PROGRESS)
        
        total_pomodoros = sum(task.actual_pomodoros for task in all_tasks)
        completion_rate = (len(completed_tasks) / len(all_tasks)) * 100 if all_tasks else 0
        
        return {
            'total_tasks': len(all_tasks),
            'completed_tasks': len(completed_tasks),
            'pending_tasks': len(pending_tasks),
            'in_progress_tasks': len(in_progress_tasks),
            'total_pomodoros': total_pomodoros,
            'completion_rate': completion_rate,
            'average_pomodoros_per_task': total_pomodoros / len(all_tasks) if all_tasks else 0
        }
    
    def get_tasks_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Task]:
        """日付範囲でタスクを取得"""
        return [
            task for task in self.tasks.values()
            if start_date <= task.created_at <= end_date
        ]
    
    def search_tasks(self, query: str) -> List[Task]:
        """タスクを検索"""
        query_lower = query.lower()
        results = []
        
        for task in self.tasks.values():
            if (query_lower in task.title.lower() or 
                query_lower in task.description.lower() or
                any(query_lower in tag.lower() for tag in task.tags)):
                results.append(task)
        
        return results
    
    def get_overdue_tasks(self) -> List[Task]:
        """期限切れタスクを取得（実装予定）"""
        # 現在は期限機能がないため空のリストを返す
        return []
    
    def export_tasks_to_csv(self, filename: str) -> bool:
        """タスクをCSVファイルにエクスポート"""
        try:
            import csv
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # ヘッダー
                writer.writerow([
                    'ID', 'タイトル', '説明', '優先度', '予定ポモドーロ', 
                    '実績ポモドーロ', 'ステータス', '作成日', '完了日', 'タグ'
                ])
                
                # データ
                for task in self.tasks.values():
                    writer.writerow([
                        task.task_id,
                        task.title,
                        task.description,
                        task.get_priority_name(),
                        task.estimated_pomodoros,
                        task.actual_pomodoros,
                        task.status,
                        task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        task.completed_at.strftime('%Y-%m-%d %H:%M:%S') if task.completed_at else '',
                        ', '.join(task.tags)
                    ])
            
            logger.info(f"📋 タスクCSVエクスポート完了: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ CSVエクスポートエラー: {e}")
            return False