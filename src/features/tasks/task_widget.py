#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
タスク管理ウィジェット
PyQt6を使用したタスク管理UI
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                           QListWidgetItem, QLabel, QPushButton, QLineEdit,
                           QTextEdit, QSpinBox, QComboBox, QDialog, QDialogButtonBox,
                           QProgressBar, QGroupBox, QGridLayout, QCheckBox,
                           QMessageBox, QMenu, QHeaderView, QTreeWidget,
                           QTreeWidgetItem, QFrame, QSplitter, QTabWidget,
                           QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QAction, QPixmap, QPainter, QPen, QBrush, QColor

from .task_manager import TaskManager, Task, TaskStatus, TaskPriority
from typing import Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TaskItemWidget(QWidget):
    """タスクアイテム表示ウィジェット"""
    
    taskSelected = pyqtSignal(str)  # task_id
    taskUpdated = pyqtSignal(str)   # task_id
    
    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.task = task
        self.setup_ui()
    
    def setup_ui(self):
        """UI設定"""
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 8, 10, 8)
        
        # メイン情報行
        main_layout = QHBoxLayout()
        
        # 優先度インジケータ
        priority_label = QLabel("●")
        priority_label.setStyleSheet(f"color: {self.task.get_priority_color()}; font-size: 16px;")
        priority_label.setFixedWidth(20)
        main_layout.addWidget(priority_label)
        
        # タスクタイトル
        title_label = QLabel(self.task.title)
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        main_layout.addWidget(title_label)
        
        # スペーサー
        main_layout.addStretch()
        
        # ポモドーロ進捗
        pomodoro_label = QLabel(f"{self.task.actual_pomodoros}/{self.task.estimated_pomodoros}🍅")
        pomodoro_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        main_layout.addWidget(pomodoro_label)
        
        # ステータス
        status_map = {
            'pending': '⏳',
            'in_progress': '🔄',
            'completed': '✅',
            'cancelled': '❌'
        }
        # ステータス値を正規化
        status_value = self.task.status
        if hasattr(status_value, 'value'):
            status_value = status_value.value
        status_label = QLabel(status_map.get(status_value, '❓'))
        status_label.setFixedWidth(20)
        main_layout.addWidget(status_label)
        
        layout.addLayout(main_layout)
        
        # 進捗バー
        progress_bar = QProgressBar()
        progress_bar.setMaximum(100)
        progress_bar.setValue(int(self.task.get_completion_percentage()))
        progress_bar.setMaximumHeight(6)
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 2px;
            }
        """)
        layout.addWidget(progress_bar)
        
        # 説明（最初の50文字）
        if self.task.description:
            desc_label = QLabel(self.task.description[:50] + "..." if len(self.task.description) > 50 else self.task.description)
            desc_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
        
        # クリック可能にする
        self.setStyleSheet("""
            TaskItemWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                margin: 2px;
            }
            TaskItemWidget:hover {
                border: 2px solid #3498db;
                background-color: #f8f9fa;
            }
        """)
        
    def mousePressEvent(self, event):
        """マウスクリックイベント"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.taskSelected.emit(self.task.task_id)
        super().mousePressEvent(event)

class TaskEditDialog(QDialog):
    """タスク編集ダイアログ"""
    
    def __init__(self, task: Optional[Task] = None, parent=None):
        super().__init__(parent)
        self.task = task
        self.setWindowTitle("タスク編集" if task else "新規タスク")
        self.setFixedSize(400, 300)
        self.setup_ui()
        
        if task:
            self.load_task_data()
    
    def setup_ui(self):
        """UI設定"""
        layout = QVBoxLayout(self)
        
        # タイトル
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("タイトル:"))
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("タスクのタイトルを入力")
        title_layout.addWidget(self.title_edit)
        layout.addLayout(title_layout)
        
        # 説明
        layout.addWidget(QLabel("説明:"))
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("タスクの詳細説明（省略可）")
        self.description_edit.setMaximumHeight(80)
        layout.addWidget(self.description_edit)
        
        # 優先度と予定ポモドーロ
        settings_layout = QGridLayout()
        
        # 優先度
        settings_layout.addWidget(QLabel("優先度:"), 0, 0)
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["最低", "低", "中", "高", "最高"])
        self.priority_combo.setCurrentIndex(2)  # デフォルト: 中
        settings_layout.addWidget(self.priority_combo, 0, 1)
        
        # 予定ポモドーロ数
        settings_layout.addWidget(QLabel("予定ポモドーロ:"), 1, 0)
        self.pomodoro_spin = QSpinBox()
        self.pomodoro_spin.setRange(1, 50)
        self.pomodoro_spin.setValue(1)
        self.pomodoro_spin.setSuffix(" 回")
        settings_layout.addWidget(self.pomodoro_spin, 1, 1)
        
        layout.addLayout(settings_layout)
        
        # タグ
        tags_layout = QHBoxLayout()
        tags_layout.addWidget(QLabel("タグ:"))
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("タグをカンマ区切りで入力")
        tags_layout.addWidget(self.tags_edit)
        layout.addLayout(tags_layout)
        
        # ボタン
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def load_task_data(self):
        """タスクデータを読み込み"""
        if not self.task:
            return
            
        self.title_edit.setText(self.task.title)
        self.description_edit.setText(self.task.description)
        self.priority_combo.setCurrentIndex(self.task.priority - 1)
        self.pomodoro_spin.setValue(self.task.estimated_pomodoros)
        self.tags_edit.setText(", ".join(self.task.tags))
        
    def get_task_data(self) -> dict:
        """入力されたタスクデータを取得"""
        tags = [tag.strip() for tag in self.tags_edit.text().split(",") if tag.strip()]
        
        return {
            'title': self.title_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'priority': self.priority_combo.currentIndex() + 1,
            'estimated_pomodoros': self.pomodoro_spin.value(),
            'tags': tags
        }

class TaskStatsWidget(QWidget):
    """タスク統計表示ウィジェット"""
    
    def __init__(self, task_manager: TaskManager, parent=None):
        super().__init__(parent)
        self.task_manager = task_manager
        self.setup_ui()
        self.update_stats()
    
    def setup_ui(self):
        """UI設定"""
        layout = QVBoxLayout(self)
        
        # タイトル
        title_label = QLabel("📊 タスク統計")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 統計グリッド
        stats_layout = QGridLayout()
        
        # 統計ラベル
        self.stats_labels = {}
        stats_config = [
            ('total_tasks', '総タスク数', 0, 0),
            ('completed_tasks', '完了済み', 0, 1),
            ('pending_tasks', '保留中', 1, 0),
            ('in_progress_tasks', '進行中', 1, 1),
            ('total_pomodoros', '総ポモドーロ', 2, 0),
            ('completion_rate', '完了率(%)', 2, 1)
        ]
        
        for key, label, row, col in stats_config:
            group = QGroupBox(label)
            group_layout = QVBoxLayout(group)
            
            value_label = QLabel("0")
            value_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value_label.setStyleSheet("color: #2c3e50;")
            group_layout.addWidget(value_label)
            
            self.stats_labels[key] = value_label
            stats_layout.addWidget(group, row, col)
        
        layout.addLayout(stats_layout)
        
        # 更新ボタン
        refresh_btn = QPushButton("🔄 更新")
        refresh_btn.clicked.connect(self.update_stats)
        layout.addWidget(refresh_btn)
        
    def update_stats(self):
        """統計を更新"""
        stats = self.task_manager.get_task_statistics()
        
        self.stats_labels['total_tasks'].setText(str(stats['total_tasks']))
        self.stats_labels['completed_tasks'].setText(str(stats['completed_tasks']))
        self.stats_labels['pending_tasks'].setText(str(stats['pending_tasks']))
        self.stats_labels['in_progress_tasks'].setText(str(stats['in_progress_tasks']))
        self.stats_labels['total_pomodoros'].setText(str(stats['total_pomodoros']))
        self.stats_labels['completion_rate'].setText(f"{stats['completion_rate']:.1f}")

class TaskWidget(QWidget):
    """メインタスク管理ウィジェット"""
    
    taskSelected = pyqtSignal(str)  # task_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.task_manager = TaskManager()
        self.current_task_id = None
        self.task_items = {}  # task_id -> TaskItemWidget
        self.setup_ui()
        self.refresh_tasks()
        
        # 自動更新タイマー
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_tasks)
        self.refresh_timer.start(30000)  # 30秒ごと
        
    def setup_ui(self):
        """UI設定"""
        layout = QVBoxLayout(self)
        
        # タイトル
        title_label = QLabel("📋 タスク管理")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # タスクリストタブ
        self.setup_task_list_tab()
        
        # 統計タブ
        self.setup_stats_tab()
        
    def setup_task_list_tab(self):
        """タスクリストタブ"""
        task_widget = QWidget()
        layout = QVBoxLayout(task_widget)
        
        # ツールバー
        toolbar_layout = QHBoxLayout()
        
        # 新規作成ボタン
        new_btn = QPushButton("➕ 新規タスク")
        new_btn.clicked.connect(self.create_new_task)
        new_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        toolbar_layout.addWidget(new_btn)
        
        # 削除ボタン
        delete_btn = QPushButton("🗑️ 削除")
        delete_btn.clicked.connect(self.delete_selected_task)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        toolbar_layout.addWidget(delete_btn)
        
        # 編集ボタン
        edit_btn = QPushButton("✏️ 編集")
        edit_btn.clicked.connect(self.edit_selected_task)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        toolbar_layout.addWidget(edit_btn)
        
        # 検索
        search_edit = QLineEdit()
        search_edit.setPlaceholderText("🔍 タスクを検索...")
        search_edit.textChanged.connect(self.filter_tasks)
        toolbar_layout.addWidget(search_edit)
        
        # エクスポート
        export_btn = QPushButton("📤 エクスポート")
        export_btn.clicked.connect(self.export_tasks)
        toolbar_layout.addWidget(export_btn)
        
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # 現在のタスク表示
        current_task_group = QGroupBox("🎯 現在のタスク")
        current_task_layout = QVBoxLayout(current_task_group)
        
        self.current_task_label = QLabel("タスクが選択されていません")
        self.current_task_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        current_task_layout.addWidget(self.current_task_label)
        
        current_task_btn_layout = QHBoxLayout()
        
        set_current_btn = QPushButton("🎯 現在のタスクに設定")
        set_current_btn.clicked.connect(self.set_current_task)
        current_task_btn_layout.addWidget(set_current_btn)
        
        clear_current_btn = QPushButton("❌ クリア")
        clear_current_btn.clicked.connect(self.clear_current_task)
        current_task_btn_layout.addWidget(clear_current_btn)
        
        current_task_layout.addLayout(current_task_btn_layout)
        layout.addWidget(current_task_group)
        
        # タスクリスト
        self.task_list_widget = QWidget()
        self.task_list_layout = QVBoxLayout(self.task_list_widget)
        self.task_list_layout.setSpacing(5)
        
        # スクロールエリア
        from PyQt6.QtWidgets import QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.task_list_widget)
        scroll_area.setMinimumHeight(300)
        layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(task_widget, "タスク一覧")
        
    def setup_stats_tab(self):
        """統計タブ"""
        self.stats_widget = TaskStatsWidget(self.task_manager)
        self.tab_widget.addTab(self.stats_widget, "統計")
        
    def refresh_tasks(self):
        """タスクリストを更新"""
        try:
            # 既存のタスクアイテムを削除
            for item in self.task_items.values():
                item.setParent(None)
            self.task_items.clear()
            
            # データを再読み込み
            self.task_manager.load_data()
            
            # タスクを取得してソート
            tasks = self.task_manager.get_all_tasks()
            tasks.sort(key=lambda t: (
                # ステータス値を正規化してからソート
                (t.status.value if hasattr(t.status, 'value') else t.status) == 'completed', 
                -t.priority, 
                t.created_at
            ))
            
            # タスクアイテムを作成
            for task in tasks:
                item_widget = TaskItemWidget(task)
                item_widget.taskSelected.connect(self.on_task_selected)
                self.task_items[task.task_id] = item_widget
                self.task_list_layout.addWidget(item_widget)
            
            # 空のスペースを追加
            self.task_list_layout.addStretch()
            
            # 現在のタスクを更新
            self.update_current_task_display()
            
            # 統計を更新
            if hasattr(self, 'stats_widget'):
                self.stats_widget.update_stats()
                
            logger.info(f"📋 タスクリスト更新: {len(tasks)}タスク")
            
        except Exception as e:
            logger.error(f"❌ タスクリスト更新エラー: {e}")
            
    def filter_tasks(self, query: str):
        """タスクをフィルタリング"""
        if not query:
            # すべてのタスクを表示
            for item in self.task_items.values():
                item.setVisible(True)
        else:
            # 検索結果に一致するタスクのみ表示
            results = self.task_manager.search_tasks(query)
            result_ids = {task.task_id for task in results}
            
            for task_id, item in self.task_items.items():
                item.setVisible(task_id in result_ids)
    
    def on_task_selected(self, task_id: str):
        """タスクが選択された時の処理"""
        self.current_task_id = task_id
        self.update_current_task_display()
        self.taskSelected.emit(task_id)
        
    def update_current_task_display(self):
        """現在のタスクの表示を更新"""
        current_task = self.task_manager.get_current_task()
        if current_task:
            self.current_task_label.setText(f"🎯 {current_task.title}")
            self.current_task_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        else:
            self.current_task_label.setText("タスクが選択されていません")
            self.current_task_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
    
    def create_new_task(self):
        """新規タスクを作成"""
        dialog = TaskEditDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_task_data()
            if data['title']:
                self.task_manager.create_task(**data)
                self.refresh_tasks()
            else:
                QMessageBox.warning(self, "警告", "タイトルを入力してください")
    
    def edit_selected_task(self):
        """選択されたタスクを編集"""
        if not self.current_task_id:
            QMessageBox.information(self, "情報", "編集するタスクを選択してください")
            return
            
        task = self.task_manager.get_task(self.current_task_id)
        if not task:
            QMessageBox.warning(self, "警告", "タスクが見つかりません")
            return
            
        dialog = TaskEditDialog(task, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_task_data()
            if data['title']:
                self.task_manager.update_task(self.current_task_id, **data)
                self.refresh_tasks()
            else:
                QMessageBox.warning(self, "警告", "タイトルを入力してください")
    
    def delete_selected_task(self):
        """選択されたタスクを削除"""
        if not self.current_task_id:
            QMessageBox.information(self, "情報", "削除するタスクを選択してください")
            return
            
        task = self.task_manager.get_task(self.current_task_id)
        if not task:
            QMessageBox.warning(self, "警告", "タスクが見つかりません")
            return
            
        reply = QMessageBox.question(
            self, "確認", 
            f"タスク '{task.title}' を削除しますか？\n\nこの操作は取り消せません。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.task_manager.delete_task(self.current_task_id)
            self.current_task_id = None
            self.refresh_tasks()
    
    def set_current_task(self):
        """現在のタスクを設定"""
        if not self.current_task_id:
            QMessageBox.information(self, "情報", "設定するタスクを選択してください")
            return
            
        self.task_manager.set_current_task(self.current_task_id)
        self.update_current_task_display()
        
        task = self.task_manager.get_task(self.current_task_id)
        QMessageBox.information(self, "設定完了", f"現在のタスクを '{task.title}' に設定しました")
    
    def clear_current_task(self):
        """現在のタスクをクリア"""
        self.task_manager.set_current_task(None)
        self.update_current_task_display()
        QMessageBox.information(self, "クリア完了", "現在のタスクをクリアしました")
    
    def export_tasks(self):
        """タスクをエクスポート"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "タスクをエクスポート", 
            f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV files (*.csv)"
        )
        
        if filename:
            if self.task_manager.export_tasks_to_csv(filename):
                QMessageBox.information(self, "成功", f"タスクをエクスポートしました: {filename}")
            else:
                QMessageBox.critical(self, "エラー", "エクスポートに失敗しました")
    
    def get_current_task(self) -> Optional[Task]:
        """現在のタスクを取得"""
        return self.task_manager.get_current_task()
    
    def add_pomodoro_to_current_task(self):
        """現在のタスクにポモドーロを追加"""
        current_task = self.task_manager.get_current_task()
        if current_task:
            self.task_manager.add_pomodoro_to_task(current_task.task_id)
            self.refresh_tasks()
            return True
        return False