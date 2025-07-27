#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pomodoro Timer - Clean Dual Window Design
設計思想：
1. 設定ウィンドウ（メイン）と ミニマルウィンドウ（独立）でデータ共有
2. タスクリスト更新は必要時のみ（イベント駆動）
"""

import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                           QWidget, QLabel, QPushButton, QSpinBox, QTabWidget,
                           QListWidget, QListWidgetItem, QLineEdit, QTextEdit,
                           QMenu, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QPoint
from PyQt6.QtGui import QFont, QAction, QMouseEvent

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TimerDataManager(QObject):
    """タイマーデータの共有管理クラス"""
    
    # シグナル - データ変更時に両ウィンドウに通知
    time_updated = pyqtSignal(int)  # 残り時間（秒）
    session_changed = pyqtSignal(str, int)  # (session_type, session_number)
    timer_state_changed = pyqtSignal(bool)  # is_running
    session_completed = pyqtSignal(str, int)  # (session_type, duration_minutes)
    
    def __init__(self):
        super().__init__()
        
        # タイマー設定
        self.work_minutes = 25
        self.break_minutes = 5
        self.long_break_minutes = 15
        self.sessions_until_long_break = 4
        
        # タイマー状態
        self.time_left = 0
        self.is_running = False
        self.is_work_session = True
        self.session_count = 0
        
        # 内部タイマー
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_timer)
        
        logger.info("📊 タイマーデータマネージャー初期化完了")
    
    def start_timer(self):
        """タイマー開始"""
        if self.time_left == 0:
            # 新しいセッション開始
            duration = self.work_minutes if self.is_work_session else self.break_minutes
            self.time_left = duration * 60
        
        self.timer.start(1000)
        self.is_running = True
        
        # 状態変更を通知
        self.timer_state_changed.emit(True)
        self.time_updated.emit(self.time_left)
        
        session_type = "作業" if self.is_work_session else "休憩"
        session_num = self.session_count + 1 if self.is_work_session else self.session_count
        self.session_changed.emit(session_type, session_num)
        
        logger.info(f"⏰ タイマー開始: {session_type}セッション #{session_num}")
    
    def pause_timer(self):
        """タイマー一時停止"""
        self.timer.stop()
        self.is_running = False
        self.timer_state_changed.emit(False)
        logger.info("⏸️ タイマー一時停止")
    
    def reset_timer(self):
        """タイマーリセット"""
        self.timer.stop()
        self.is_running = False
        self.time_left = 0
        
        self.timer_state_changed.emit(False)
        self.time_updated.emit(0)
        logger.info("🔄 タイマーリセット")
    
    def _update_timer(self):
        """内部タイマー更新"""
        self.time_left -= 1
        self.time_updated.emit(self.time_left)
        
        if self.time_left <= 0:
            self._on_session_finished()
    
    def _on_session_finished(self):
        """セッション完了処理"""
        self.timer.stop()
        self.is_running = False
        
        # 統計記録
        session_type = "work" if self.is_work_session else "break"
        duration = self.work_minutes if self.is_work_session else self.break_minutes
        self.session_completed.emit(session_type, duration)
        
        # セッション切り替え
        if self.is_work_session:
            self.session_count += 1
            self.is_work_session = False
            
            # 長い休憩判定
            if self.session_count % self.sessions_until_long_break == 0:
                self.time_left = self.long_break_minutes * 60
                logger.info(f"🎉 ポモドーロ {self.session_count}回完了！長い休憩の時間です")
            else:
                self.time_left = self.break_minutes * 60
                logger.info(f"✅ 作業セッション完了！休憩の時間です")
        else:
            self.is_work_session = True
            self.time_left = self.work_minutes * 60
            logger.info("🔄 休憩終了！次の作業セッションを開始しましょう")
        
        # 状態更新を通知
        self.timer_state_changed.emit(False)
        session_type = "作業" if self.is_work_session else "休憩"
        session_num = self.session_count + 1 if self.is_work_session else self.session_count
        self.session_changed.emit(session_type, session_num)
        self.time_updated.emit(self.time_left)


class TaskManager(QObject):
    """タスク管理（シンプル版）"""
    
    # シグナル - タスク変更時のみ通知
    task_added = pyqtSignal(str)  # task_text
    task_completed = pyqtSignal(str)  # task_text
    task_deleted = pyqtSignal(str)  # task_text
    
    def __init__(self):
        super().__init__()
        self.tasks_file = Path("data/tasks_clean.json")
        self.tasks_file.parent.mkdir(exist_ok=True)
        self.tasks = []
        self.load_tasks()
    
    def load_tasks(self):
        """タスク読み込み（起動時のみ）"""
        try:
            if self.tasks_file.exists():
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
            logger.info(f"📋 タスク読み込み: {len(self.tasks)}件")
        except Exception as e:
            logger.error(f"タスク読み込みエラー: {e}")
            self.tasks = []
    
    def save_tasks(self):
        """タスク保存"""
        try:
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"タスク保存エラー: {e}")
    
    def add_task(self, text: str):
        """タスク追加（イベント駆動更新）"""
        task = {
            'id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'text': text,
            'completed': False,
            'created_at': datetime.now().isoformat()
        }
        self.tasks.append(task)
        self.save_tasks()
        self.task_added.emit(text)
        logger.info(f"📋 タスク追加: {text}")
    
    def complete_task(self, task_id: str):
        """タスク完了（イベント駆動更新）"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['completed'] = True
                task['completed_at'] = datetime.now().isoformat()
                self.save_tasks()
                self.task_completed.emit(task['text'])
                logger.info(f"✅ タスク完了: {task['text']}")
                break
    
    def delete_task(self, task_id: str):
        """タスク削除（イベント駆動更新）"""
        for i, task in enumerate(self.tasks):
            if task['id'] == task_id:
                deleted_text = task['text']
                del self.tasks[i]
                self.save_tasks()
                self.task_deleted.emit(deleted_text)
                logger.info(f"🗑️ タスク削除: {deleted_text}")
                break
    
    def get_active_tasks(self):
        """アクティブなタスク一覧取得"""
        return [task for task in self.tasks if not task['completed']]


class StatisticsManager:
    """統計管理（シンプル版）"""
    
    def __init__(self):
        self.stats_file = Path("data/stats_clean.json")
        self.stats_file.parent.mkdir(exist_ok=True)
        self.sessions = []
        self.load_stats()
    
    def load_stats(self):
        """統計読み込み"""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.sessions = data.get('sessions', [])
            logger.info(f"📊 統計読み込み: {len(self.sessions)}セッション")
        except Exception as e:
            logger.error(f"統計読み込みエラー: {e}")
            self.sessions = []
    
    def record_session(self, session_type: str, duration_minutes: int):
        """セッション記録（セッション完了時のみ）"""
        session = {
            'type': session_type,
            'duration': duration_minutes,
            'completed_at': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        self.sessions.append(session)
        self.save_stats()
        logger.info(f"📊 セッション記録: {session_type} ({duration_minutes}分)")
    
    def save_stats(self):
        """統計保存"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump({'sessions': self.sessions}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"統計保存エラー: {e}")
    
    def get_today_stats(self):
        """今日の統計取得"""
        today = datetime.now().strftime('%Y-%m-%d')
        today_sessions = [s for s in self.sessions if s['date'] == today]
        
        work_count = len([s for s in today_sessions if s['type'] == 'work'])
        break_count = len([s for s in today_sessions if s['type'] == 'break'])
        total_work_time = sum(s['duration'] for s in today_sessions if s['type'] == 'work')
        
        return {
            'work_sessions': work_count,
            'break_sessions': break_count,
            'total_work_minutes': total_work_time
        }


class MainWindow(QMainWindow):
    """設定モード（メインウィンドウ）"""
    
    def __init__(self, timer_data: TimerDataManager, task_manager: TaskManager, stats: StatisticsManager):
        super().__init__()
        
        self.timer_data = timer_data
        self.task_manager = task_manager
        self.stats = stats
        self.minimal_window = None
        
        self.init_ui()
        self.connect_signals()
        
        logger.info("🏠 メインウィンドウ初期化完了")
    
    def init_ui(self):
        """UI初期化"""
        self.setWindowTitle("🍅 Pomodoro Timer - 設定モード")
        self.setGeometry(100, 100, 500, 400)
        
        # メインウィジェット
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # タイマータブ
        self.setup_timer_tab()
        
        # タスクタブ
        self.setup_task_tab()
        
        # 統計タブ
        self.setup_stats_tab()
        
        # ミニマルモードボタン
        minimal_btn = QPushButton("🔽 ミニマルモード表示")
        minimal_btn.clicked.connect(self.show_minimal_mode)
        layout.addWidget(minimal_btn)
    
    def setup_timer_tab(self):
        """タイマータブ設定"""
        timer_widget = QWidget()
        layout = QVBoxLayout(timer_widget)
        
        # タイマー表示
        self.time_display = QLabel("25:00")
        self.time_display.setFont(QFont("Arial", 36))
        self.time_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.time_display)
        
        # セッション情報
        self.session_info = QLabel("作業セッション #1")
        self.session_info.setFont(QFont("Arial", 14))
        self.session_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.session_info)
        
        # コントロールボタン
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶️ 開始")
        self.start_btn.clicked.connect(self.timer_data.start_timer)
        btn_layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("⏸️ 一時停止")
        self.pause_btn.clicked.connect(self.timer_data.pause_timer)
        btn_layout.addWidget(self.pause_btn)
        
        self.reset_btn = QPushButton("🔄 リセット")
        self.reset_btn.clicked.connect(self.timer_data.reset_timer)
        btn_layout.addWidget(self.reset_btn)
        
        layout.addLayout(btn_layout)
        
        # 設定
        settings_layout = QHBoxLayout()
        
        settings_layout.addWidget(QLabel("作業時間:"))
        self.work_spin = QSpinBox()
        self.work_spin.setRange(1, 60)
        self.work_spin.setValue(self.timer_data.work_minutes)
        self.work_spin.setSuffix(" 分")
        self.work_spin.valueChanged.connect(self.on_work_duration_changed)
        settings_layout.addWidget(self.work_spin)
        
        settings_layout.addWidget(QLabel("休憩時間:"))
        self.break_spin = QSpinBox()
        self.break_spin.setRange(1, 30)
        self.break_spin.setValue(self.timer_data.break_minutes)
        self.break_spin.setSuffix(" 分")
        self.break_spin.valueChanged.connect(self.on_break_duration_changed)
        settings_layout.addWidget(self.break_spin)
        
        layout.addLayout(settings_layout)
        
        self.tab_widget.addTab(timer_widget, "⏱️ タイマー")
    
    def setup_task_tab(self):
        """タスクタブ設定"""
        task_widget = QWidget()
        layout = QVBoxLayout(task_widget)
        
        # 新規タスク入力
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("新しいタスクを入力...")
        self.task_input.returnPressed.connect(self.add_task)
        input_layout.addWidget(self.task_input)
        
        add_btn = QPushButton("➕ 追加")
        add_btn.clicked.connect(self.add_task)
        input_layout.addWidget(add_btn)
        
        layout.addLayout(input_layout)
        
        # タスクリスト
        self.task_list = QListWidget()
        layout.addWidget(self.task_list)
        
        # 初期タスク読み込み（起動時のみ）
        self.refresh_task_list()
        
        self.tab_widget.addTab(task_widget, "📋 タスク")
    
    def setup_stats_tab(self):
        """統計タブ設定"""
        stats_widget = QWidget()
        layout = QVBoxLayout(stats_widget)
        
        # 統計表示
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        layout.addWidget(self.stats_display)
        
        # 初期統計表示
        self.refresh_stats_display()
        
        self.tab_widget.addTab(stats_widget, "📊 統計")
    
    def connect_signals(self):
        """シグナル接続"""
        # タイマーデータからの通知
        self.timer_data.time_updated.connect(self.on_time_updated)
        self.timer_data.session_changed.connect(self.on_session_changed)
        self.timer_data.timer_state_changed.connect(self.on_timer_state_changed)
        self.timer_data.session_completed.connect(self.on_session_completed)
        
        # タスクマネージャーからの通知（イベント駆動）
        self.task_manager.task_added.connect(lambda: self.refresh_task_list())
        self.task_manager.task_completed.connect(lambda: self.refresh_task_list())
        self.task_manager.task_deleted.connect(lambda: self.refresh_task_list())
    
    def show_minimal_mode(self):
        """ミニマルモード表示"""
        if not self.minimal_window:
            self.minimal_window = MinimalWindow(self.timer_data)
        
        self.minimal_window.show()
        self.showMinimized()  # メインウィンドウは最小化
        
        logger.info("🔽 ミニマルモード表示、メインウィンドウ最小化")
    
    def add_task(self):
        """タスク追加（イベント駆動更新）"""
        text = self.task_input.text().strip()
        if text:
            self.task_manager.add_task(text)
            self.task_input.clear()
    
    def refresh_task_list(self):
        """タスクリスト更新（必要時のみ）"""
        self.task_list.clear()
        for task in self.task_manager.get_active_tasks():
            item = QListWidgetItem(f"📝 {task['text']}")
            item.setData(Qt.ItemDataRole.UserRole, task['id'])
            self.task_list.addItem(item)
        
        logger.info(f"📋 タスクリスト更新: {self.task_list.count()}件")
    
    def refresh_stats_display(self):
        """統計表示更新（セッション完了時のみ）"""
        today_stats = self.stats.get_today_stats()
        
        stats_text = f"""
今日の統計 ({datetime.now().strftime('%Y-%m-%d')})

🍅 作業セッション: {today_stats['work_sessions']}回
☕ 休憩セッション: {today_stats['break_sessions']}回
⏰ 合計作業時間: {today_stats['total_work_minutes']}分

📈 総セッション数: {len(self.stats.sessions)}回
        """.strip()
        
        self.stats_display.setText(stats_text)
    
    # イベントハンドラー
    def on_time_updated(self, time_left: int):
        """時間更新"""
        minutes = time_left // 60
        seconds = time_left % 60
        self.time_display.setText(f"{minutes:02d}:{seconds:02d}")
    
    def on_session_changed(self, session_type: str, session_number: int):
        """セッション変更"""
        self.session_info.setText(f"{session_type}セッション #{session_number}")
    
    def on_timer_state_changed(self, is_running: bool):
        """タイマー状態変更"""
        self.start_btn.setEnabled(not is_running)
        self.pause_btn.setEnabled(is_running)
    
    def on_session_completed(self, session_type: str, duration: int):
        """セッション完了（統計更新とタスクリスト更新）"""
        # 統計記録
        self.stats.record_session(session_type, duration)
        
        # 統計表示更新
        self.refresh_stats_display()
        
        # タスクリスト更新（セッション完了時のみ）
        self.refresh_task_list()
        
        # 通知
        session_name = "作業" if session_type == "work" else "休憩"
        QMessageBox.information(self, "セッション完了", f"{session_name}セッションが完了しました！")
    
    def on_work_duration_changed(self, value: int):
        """作業時間設定変更"""
        self.timer_data.work_minutes = value
    
    def on_break_duration_changed(self, value: int):
        """休憩時間設定変更"""
        self.timer_data.break_minutes = value


class MinimalWindow(QMainWindow):
    """ミニマルウィンドウ（独立表示）"""
    
    def __init__(self, timer_data: TimerDataManager):
        super().__init__()
        
        self.timer_data = timer_data
        self.dragging = False
        self.drag_position = QPoint()
        
        self.init_ui()
        self.connect_signals()
        
        logger.info("🔽 ミニマルウィンドウ初期化完了")
    
    def init_ui(self):
        """UI初期化"""
        self.setWindowTitle("🍅 Pomodoro")
        self.setGeometry(200, 200, 200, 100)
        
        # フレームレス・最前面
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        # メインウィジェット
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 時間表示
        self.time_label = QLabel("25:00")
        self.time_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("color: white; background: transparent;")
        layout.addWidget(self.time_label)
        
        # セッション情報
        self.session_label = QLabel("作業セッション #1")
        self.session_label.setFont(QFont("Arial", 10))
        self.session_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.session_label.setStyleSheet("color: #cccccc; background: transparent;")
        layout.addWidget(self.session_label)
        
        # スタイル設定
        main_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 200);
                border-radius: 10px;
            }
        """)
        
        # 初期表示設定
        self.update_display()
    
    def connect_signals(self):
        """シグナル接続"""
        self.timer_data.time_updated.connect(self.on_time_updated)
        self.timer_data.session_changed.connect(self.on_session_changed)
    
    def update_display(self):
        """表示更新"""
        # 初期表示
        if self.timer_data.time_left == 0:
            minutes = self.timer_data.work_minutes if self.timer_data.is_work_session else self.timer_data.break_minutes
            self.time_label.setText(f"{minutes:02d}:00")
        
        session_type = "作業" if self.timer_data.is_work_session else "休憩"
        session_num = self.timer_data.session_count + 1 if self.timer_data.is_work_session else self.timer_data.session_count
        self.session_label.setText(f"{session_type}セッション #{session_num}")
    
    def on_time_updated(self, time_left: int):
        """時間更新"""
        minutes = time_left // 60
        seconds = time_left % 60
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
    
    def on_session_changed(self, session_type: str, session_number: int):
        """セッション変更"""
        self.session_label.setText(f"{session_type}セッション #{session_number}")
    
    # マウスイベント（ドラッグ移動）
    def mousePressEvent(self, event: QMouseEvent):
        """マウス押下"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """マウス移動"""
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """マウスリリース"""
        self.dragging = False
    
    def contextMenuEvent(self, event):
        """右クリックメニュー"""
        menu = QMenu(self)
        
        # タイマー制御
        if self.timer_data.is_running:
            pause_action = QAction("⏸️ 一時停止", self)
            pause_action.triggered.connect(self.timer_data.pause_timer)
            menu.addAction(pause_action)
        else:
            start_action = QAction("▶️ 開始", self)
            start_action.triggered.connect(self.timer_data.start_timer)
            menu.addAction(start_action)
        
        reset_action = QAction("🔄 リセット", self)
        reset_action.triggered.connect(self.timer_data.reset_timer)
        menu.addAction(reset_action)
        
        menu.addSeparator()
        
        # 透明化
        transparent_action = QAction("👻 透明化", self)
        transparent_action.setCheckable(True)
        transparent_action.triggered.connect(self.toggle_transparency)
        menu.addAction(transparent_action)
        
        menu.addSeparator()
        
        # 設定モードに戻る
        show_main_action = QAction("🏠 設定モードを復元", self)
        show_main_action.triggered.connect(self.show_main_window)
        menu.addAction(show_main_action)
        
        # 閉じる
        close_action = QAction("❌ 閉じる", self)
        close_action.triggered.connect(self.close)
        menu.addAction(close_action)
        
        menu.exec(event.globalPos())
    
    def toggle_transparency(self):
        """透明化切り替え"""
        current_opacity = self.windowOpacity()
        if current_opacity > 0.5:
            self.setWindowOpacity(0.3)
        else:
            self.setWindowOpacity(1.0)
    
    def show_main_window(self):
        """メインウィンドウを復元"""
        # メインウィンドウを探して復元
        for widget in QApplication.allWidgets():
            if isinstance(widget, MainWindow):
                widget.showNormal()
                widget.raise_()
                widget.activateWindow()
                logger.info("🏠 メインウィンドウ復元")
                break


def main():
    """メイン関数"""
    app = QApplication(sys.argv)
    
    # データ管理オブジェクト作成
    timer_data = TimerDataManager()
    task_manager = TaskManager()
    stats = StatisticsManager()
    
    # メインウィンドウ作成
    main_window = MainWindow(timer_data, task_manager, stats)
    main_window.show()
    
    logger.info("🚀 Clean Dual Window Pomodoro Timer 起動完了")
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())