#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pomodoro Timer Phase 3 - シンプル統合版
Phase 3の機能 + minimal_timer_demoの透明化機能を段階的に統合
"""

import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                           QWidget, QLabel, QPushButton, QTabWidget, QMenu, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QSettings, QPoint
from PyQt6.QtGui import QFont, QAction, QMouseEvent

# Phase 3モジュールをインポート
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.models.timer_model import TimerModel
from src.utils.audio_manager import AudioManager
from src.features.tasks.task_widget import TaskWidget
from src.features.tasks.task_manager import TaskManager
from src.features.statistics import PomodoroStatistics

# ダッシュボード（オプション）
try:
    from src.features.dashboard.dashboard_widget import DashboardWidget
    DASHBOARD_AVAILABLE = True
except ImportError:
    logger.warning("📊 ダッシュボードモジュールが見つかりません")
    DASHBOARD_AVAILABLE = False

# テーマ（オプション）
try:
    from src.features.themes.theme_widget import ThemeWidget
    THEME_AVAILABLE = True
except ImportError:
    logger.warning("🎨 テーマモジュールが見つかりません")
    THEME_AVAILABLE = False


class SimpleIntegratedTimer(QMainWindow):
    """シンプル統合版タイマー"""
    
    def __init__(self):
        super().__init__()
        
        # 基本設定
        self.work_minutes = 25
        self.break_minutes = 5
        self.is_work_session = True
        self.session_count = 0
        
        # タイマー
        self.timer_model = TimerModel()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.time_left = self.work_minutes * 60
        
        # 音声
        self.audio_manager = AudioManager()
        
        # 統計
        self.statistics = PomodoroStatistics()
        
        # タスク管理
        self.task_manager = TaskManager()
        self.task_widget = TaskWidget()
        
        # ダッシュボード
        if DASHBOARD_AVAILABLE:
            self.dashboard = DashboardWidget()
        
        # テーマ
        if THEME_AVAILABLE:
            self.theme_widget = ThemeWidget()
            self.theme_widget.themeChanged.connect(self.apply_theme)
        
        # 透明モード設定
        self.transparent_mode = False
        self.minimal_mode = False
        
        # ドラッグ用
        self.dragging = False
        self.drag_position = QPoint()
        
        # UI初期化
        self.setup_ui()
        
        # 設定読み込み
        self.load_settings()
        
        logger.info("✅ シンプル統合版タイマー初期化完了")
    
    def setup_ui(self):
        """UI構築"""
        self.setWindowTitle("🍅 Pomodoro Timer Phase 3 - Simple Integration")
        self.setGeometry(100, 100, 450, 350)
        
        # メインウィジェット
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # レイアウト
        layout = QVBoxLayout(main_widget)
        
        # ツールバー
        self.setup_toolbar(layout)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # タイマータブ
        self.setup_timer_tab()
        
        # タスクタブ
        self.tab_widget.addTab(self.task_widget, "📋 タスク")
        
        # ダッシュボードタブ
        if DASHBOARD_AVAILABLE:
            self.tab_widget.addTab(self.dashboard, "📊 ダッシュボード")
        
        # テーマタブ
        if THEME_AVAILABLE:
            self.tab_widget.addTab(self.theme_widget, "🎨 テーマ")
    
    def setup_toolbar(self, parent_layout):
        """ツールバー設定"""
        toolbar_layout = QHBoxLayout()
        
        # ミニマルモードボタン
        self.minimal_btn = QPushButton("🔽 ミニマルモード")
        self.minimal_btn.clicked.connect(self.toggle_minimal_mode)
        toolbar_layout.addWidget(self.minimal_btn)
        
        # 透明化ボタン
        self.transparent_btn = QPushButton("👻 透明化")
        self.transparent_btn.setCheckable(True)
        self.transparent_btn.clicked.connect(self.toggle_transparency)
        toolbar_layout.addWidget(self.transparent_btn)
        
        toolbar_layout.addStretch()
        parent_layout.addLayout(toolbar_layout)
    
    def setup_timer_tab(self):
        """タイマータブ設定"""
        timer_widget = QWidget()
        layout = QVBoxLayout(timer_widget)
        
        # タイマー表示
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Arial", 48))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.time_label)
        
        # 状態表示
        self.status_label = QLabel()
        self.status_label.setFont(QFont("Arial", 16))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # コントロールボタン
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶️ 開始")
        self.start_btn.clicked.connect(self.start_timer)
        button_layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("⏸️ 一時停止")
        self.pause_btn.clicked.connect(self.pause_timer)
        self.pause_btn.setEnabled(False)
        button_layout.addWidget(self.pause_btn)
        
        self.reset_btn = QPushButton("🔄 リセット")
        self.reset_btn.clicked.connect(self.reset_timer)
        button_layout.addWidget(self.reset_btn)
        
        layout.addLayout(button_layout)
        
        self.tab_widget.addTab(timer_widget, "⏱️ タイマー")
        
        # 初期表示更新
        self.update_display()
    
    def toggle_minimal_mode(self):
        """ミニマルモード切り替え"""
        self.minimal_mode = not self.minimal_mode
        
        if self.minimal_mode:
            # ミニマルモードへ
            self.tab_widget.hide()
            self.resize(150, 100)
            self.minimal_btn.setText("🔼 フルモード")
            
            # タイトルバーを非表示
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
            self.show()
        else:
            # フルモードへ
            self.tab_widget.show()
            self.resize(450, 350)
            self.minimal_btn.setText("🔽 ミニマルモード")
            
            # タイトルバーを表示
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.FramelessWindowHint)
            self.show()
    
    def toggle_transparency(self):
        """透明化切り替え"""
        self.transparent_mode = self.transparent_btn.isChecked()
        
        if self.transparent_mode:
            self.setWindowOpacity(0.3)
            self.setStyleSheet("""
                QWidget {
                    background-color: rgba(0, 0, 0, 0);
                }
                QLabel {
                    color: white;
                    background-color: rgba(0, 0, 0, 0);
                }
            """)
        else:
            self.setWindowOpacity(1.0)
            self.setStyleSheet("")
    
    def start_timer(self):
        """タイマー開始"""
        self.timer.start(1000)  # 1秒ごとに更新
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        
        # ミニマルモードへ自動切り替え（オプション）
        if self.minimal_mode:
            self.toggle_minimal_mode()
    
    def pause_timer(self):
        """タイマー一時停止"""
        self.timer.stop()
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
    
    def reset_timer(self):
        """タイマーリセット"""
        self.timer.stop()
        self.time_left = self.work_minutes * 60 if self.is_work_session else self.break_minutes * 60
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.update_display()
    
    def update_timer(self):
        """タイマー更新"""
        self.time_left -= 1
        self.update_display(self.time_left)
        
        if self.time_left <= 0:
            self.timer.stop()
            self.on_timer_finished()
    
    def on_timer_finished(self):
        """タイマー完了"""
        # 音声再生
        try:
            self.audio_manager.play_sound("session_end")
        except:
            pass
        
        # セッション記録
        self.statistics.record_session(
            session_type="work" if self.is_work_session else "break",
            duration=self.work_minutes if self.is_work_session else self.break_minutes,
            completed=True
        )
        
        # セッション切り替え
        self.is_work_session = not self.is_work_session
        if self.is_work_session:
            self.session_count += 1
        
        # 自動開始（オプション）
        if self.minimal_mode:
            self.start_timer()
        else:
            self.reset_timer()
            QMessageBox.information(self, "完了", 
                f"{'作業' if not self.is_work_session else '休憩'}時間が終了しました！")
    
    def update_display(self, time_left=None):
        """表示更新"""
        if time_left is None:
            time_left = self.work_minutes * 60 if self.is_work_session else self.break_minutes * 60
        
        minutes = time_left // 60
        seconds = time_left % 60
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
        
        session_type = "作業中" if self.is_work_session else "休憩中"
        self.status_label.setText(f"{session_type} - セッション #{self.session_count + 1}")
    
    def apply_theme(self, theme_name):
        """テーマ適用"""
        if THEME_AVAILABLE:
            theme_manager = self.theme_widget.get_theme_manager()
            stylesheet = theme_manager.get_stylesheet()
            self.setStyleSheet(stylesheet)
    
    def mousePressEvent(self, event: QMouseEvent):
        """マウス押下イベント（ミニマルモード時のドラッグ用）"""
        if self.minimal_mode and event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """マウス移動イベント"""
        if self.dragging and self.minimal_mode:
            self.move(event.globalPosition().toPoint() - self.drag_position)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """マウスリリースイベント"""
        self.dragging = False
    
    def contextMenuEvent(self, event):
        """右クリックメニュー（ミニマルモード時）"""
        if self.minimal_mode:
            menu = QMenu(self)
            
            # フルモードへ
            full_action = QAction("🔼 フルモードへ", self)
            full_action.triggered.connect(self.toggle_minimal_mode)
            menu.addAction(full_action)
            
            menu.addSeparator()
            
            # 終了
            quit_action = QAction("❌ 終了", self)
            quit_action.triggered.connect(self.close)
            menu.addAction(quit_action)
            
            menu.exec(event.globalPos())
    
    def load_settings(self):
        """設定読み込み"""
        settings = QSettings("PomodoroTimer", "SimpleIntegration")
        
        # ウィンドウ位置
        pos = settings.value("window_position", self.pos())
        self.move(pos)
        
        # タイマー設定
        self.work_minutes = settings.value("work_minutes", 25, type=int)
        self.break_minutes = settings.value("break_minutes", 5, type=int)
    
    def save_settings(self):
        """設定保存"""
        settings = QSettings("PomodoroTimer", "SimpleIntegration")
        settings.setValue("window_position", self.pos())
        settings.setValue("work_minutes", self.work_minutes)
        settings.setValue("break_minutes", self.break_minutes)
    
    def closeEvent(self, event):
        """終了イベント"""
        self.save_settings()
        event.accept()


def main():
    """メイン関数"""
    app = QApplication(sys.argv)
    app.setApplicationName("Pomodoro Timer Simple Integration")
    
    window = SimpleIntegratedTimer()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())