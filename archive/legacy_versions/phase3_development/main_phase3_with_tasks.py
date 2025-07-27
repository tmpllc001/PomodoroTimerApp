#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pomodoro Timer Phase 3 - タスク管理統合版
統計ダッシュボード + タスク管理システム
"""

import sys
import os
import locale
from pathlib import Path
import logging

# 文字エンコーディング設定
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# ロケール設定
try:
    locale.setlocale(locale.LC_ALL, '')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except locale.Error:
        pass

# プロジェクトパス追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase3_full.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                           QWidget, QLabel, QPushButton, QSpinBox, QCheckBox, 
                           QSlider, QComboBox, QTextEdit, QGroupBox, QTabWidget,
                           QMessageBox, QFrame, QSplitter)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

# Phase 2 機能インポート
from features.window_resizer import WindowResizer
from features.statistics import PomodoroStatistics
from features.music_presets import MusicPresetsSimple as MusicPresets

# Phase 3 機能インポート
from features.dashboard.dashboard_widget import DashboardWidget
from features.tasks.task_widget import TaskWidget
from features.tasks.task_integration import TaskIntegration
from features.themes.theme_widget import ThemeWidget

# matplotlib強制使用版
import matplotlib.pyplot as plt
import pandas as pd
DASHBOARD_AVAILABLE = True
logger.info("📊 ダッシュボード機能: matplotlibモード利用可能")

# 音声システム（エラー対応版）
AUDIO_AVAILABLE = False
try:
    import pygame.mixer
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
    logger.info("🔊 音声システム初期化成功")
except Exception as e:
    logger.warning(f"⚠️ 音声システム利用不可: {e}")
    logger.info("🔇 音声なしモードで動作します")

class TaskSelectionWidget(QWidget):
    """現在のタスク選択ウィジェット"""
    
    taskChanged = pyqtSignal(str)  # task_id
    
    def __init__(self, task_integration, parent=None):
        super().__init__(parent)
        self.task_integration = task_integration
        self.setup_ui()
        self.update_task_info()
    
    def setup_ui(self):
        """UI設定"""
        layout = QVBoxLayout(self)
        
        # 現在のタスク表示
        self.current_task_frame = QFrame()
        self.current_task_frame.setFrameStyle(QFrame.Shape.Box)
        self.current_task_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #3498db;
                border-radius: 8px;
                background-color: #f8f9fa;
                padding: 10px;
            }
        """)
        
        frame_layout = QVBoxLayout(self.current_task_frame)
        
        # タスクタイトル
        self.task_title_label = QLabel("🎯 現在のタスク: 未選択")
        self.task_title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.task_title_label.setStyleSheet("color: #2c3e50;")
        frame_layout.addWidget(self.task_title_label)
        
        # 進捗情報
        self.progress_label = QLabel("進捗: 0/0 ポモドーロ")
        self.progress_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        frame_layout.addWidget(self.progress_label)
        
        # 優先度
        self.priority_label = QLabel("優先度: -")
        self.priority_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        frame_layout.addWidget(self.priority_label)
        
        layout.addWidget(self.current_task_frame)
        
        # ボタン
        button_layout = QHBoxLayout()
        
        change_task_btn = QPushButton("📋 タスク変更")
        change_task_btn.clicked.connect(self.change_task)
        change_task_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                border: none;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        button_layout.addWidget(change_task_btn)
        
        no_task_btn = QPushButton("🚫 タスクなし")
        no_task_btn.clicked.connect(self.clear_task)
        no_task_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                border: none;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        button_layout.addWidget(no_task_btn)
        
        layout.addLayout(button_layout)
        
    def update_task_info(self):
        """タスク情報を更新"""
        task_info = self.task_integration.get_current_task_info()
        
        if task_info:
            self.task_title_label.setText(f"🎯 現在のタスク: {task_info['title']}")
            self.progress_label.setText(f"進捗: {task_info['actual_pomodoros']}/{task_info['estimated_pomodoros']} ポモドーロ")
            self.priority_label.setText(f"優先度: {task_info['priority_name']}")
            
            # 優先度の色を設定
            self.priority_label.setStyleSheet(f"color: {task_info['priority_color']}; font-size: 10px; font-weight: bold;")
            
            # 進捗に応じてフレームの色を変更
            completion = task_info['completion_percentage']
            if completion >= 100:
                border_color = "#27ae60"  # 完了: 緑
            elif completion >= 50:
                border_color = "#f39c12"  # 進行中: オレンジ
            else:
                border_color = "#3498db"  # 開始: 青
                
            self.current_task_frame.setStyleSheet(f"""
                QFrame {{
                    border: 2px solid {border_color};
                    border-radius: 8px;
                    background-color: #f8f9fa;
                    padding: 10px;
                }}
            """)
        else:
            self.task_title_label.setText("🎯 現在のタスク: 未選択")
            self.progress_label.setText("進捗: -")
            self.priority_label.setText("優先度: -")
            self.priority_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
            
            self.current_task_frame.setStyleSheet("""
                QFrame {
                    border: 2px solid #bdc3c7;
                    border-radius: 8px;
                    background-color: #f8f9fa;
                    padding: 10px;
                }
            """)
    
    def change_task(self):
        """タスク変更ボタンをクリック"""
        # タスクタブに切り替えるシグナルを発行
        self.taskChanged.emit("select_task")
    
    def clear_task(self):
        """タスクをクリア"""
        self.task_integration.get_task_manager().set_current_task(None)
        self.update_task_info()

class PomodoroTimerPhase3Full(QMainWindow):
    """Phase 3 完全版ポモドーロタイマー"""
    
    timer_finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.work_minutes = 25
        self.break_minutes = 5
        self.time_left = self.work_minutes * 60
        self.is_running = False
        self.is_work_session = True
        self.session_count = 0
        
        # QTimer設定
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        
        # Phase 2 機能初期化
        self.window_resizer = WindowResizer(self)
        self.statistics = PomodoroStatistics()
        self.music_presets = MusicPresets()
        
        # Phase 3 機能初期化
        self.task_integration = TaskIntegration()
        self.task_integration.taskCompleted.connect(self.on_task_completed)
        self.task_integration.pomodoroCompleted.connect(self.on_pomodoro_completed)
        
        if DASHBOARD_AVAILABLE:
            self.dashboard = DashboardWidget()
        else:
            self.dashboard = None
            
        self.task_widget = TaskWidget()
        self.task_widget.taskSelected.connect(self.on_task_selected)
        
        # テーマ管理
        self.theme_widget = ThemeWidget()
        self.theme_widget.themeChanged.connect(self.on_theme_changed)
        
        self.setup_ui()
        
        logger.info("✅ Phase 3 完全版ポモドーロタイマー初期化完了")
        
    def setup_ui(self):
        """UI設定"""
        self.setWindowTitle("🍅 Pomodoro Timer Phase 3 - Full Edition")
        self.setGeometry(100, 100, 1000, 800)
        
        # 透明度・最前面設定
        self.setWindowOpacity(0.9)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # メインタブ
        self.setup_main_tab()
        
        # タスク管理タブ
        self.tab_widget.addTab(self.task_widget, "📋 タスク管理")
        
        # 統計ダッシュボードタブ
        if DASHBOARD_AVAILABLE:
            self.tab_widget.addTab(self.dashboard, "📊 ダッシュボード")
        else:
            self.setup_dashboard_placeholder()
        
        # テーマ管理タブ
        self.tab_widget.addTab(self.theme_widget, "🎨 テーマ")
        
        # 統計タブ（従来版）
        self.setup_stats_tab()
        
        # 設定タブ
        self.setup_settings_tab()
        
        logger.info("🎨 Phase 3 完全版UI設定完了")
    
    def setup_main_tab(self):
        """メインタブ設定"""
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        
        # 左パネル: タイマー
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)
        left_layout.setContentsMargins(20, 20, 20, 20)
        
        # タイトル
        title_label = QLabel("🍅 Pomodoro Timer Phase 3")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #e74c3c; margin-bottom: 10px;")
        left_layout.addWidget(title_label)
        
        # 新機能バッジ
        badge_label = QLabel("✨ NEW: タスク管理 + 統計ダッシュボード")
        badge_label.setFont(QFont("Arial", 10))
        badge_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge_label.setStyleSheet("""
            background-color: #9b59b6; 
            color: white; 
            padding: 5px 10px; 
            border-radius: 15px; 
            margin-bottom: 10px;
        """)
        left_layout.addWidget(badge_label)
        
        # 現在のタスク選択
        self.task_selection = TaskSelectionWidget(self.task_integration)
        self.task_selection.taskChanged.connect(self.on_task_change_requested)
        left_layout.addWidget(self.task_selection)
        
        # セッション表示
        self.session_label = QLabel("📖 作業セッション #1")
        self.session_label.setFont(QFont("Arial", 12))
        self.session_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.session_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        left_layout.addWidget(self.session_label)
        
        # タイマー表示
        self.time_label = QLabel(self.format_time(self.time_left))
        self.time_label.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("""
            color: #2c3e50; 
            background-color: rgba(255,255,255,0.9); 
            padding: 20px; 
            border-radius: 15px;
            border: 2px solid #3498db;
        """)
        left_layout.addWidget(self.time_label)
        
        # 時間設定
        self.setup_time_settings(left_layout)
        
        # ボタン
        self.setup_buttons(left_layout)
        
        # ステータス
        self.status_label = QLabel("🟢 準備完了")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 14px; margin-top: 5px;")
        left_layout.addWidget(self.status_label)
        
        # 音楽プリセット選択
        self.setup_music_controls(left_layout)
        
        # 右パネル: 今日の概要
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        
        # 今日の概要
        self.setup_today_summary(right_layout)
        
        # 推奨タスク
        self.setup_recommended_tasks(right_layout)
        
        # スプリッターで分割
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([600, 400])
        
        main_layout.addWidget(splitter)
        
        self.tab_widget.addTab(main_widget, "メイン")
        
        # 定期更新タイマー
        self.update_timer_ui = QTimer()
        self.update_timer_ui.timeout.connect(self.update_task_displays)
        self.update_timer_ui.start(10000)  # 10秒ごと
        
        # 現在のテーマを適用
        self.apply_current_theme()
    
    def setup_today_summary(self, layout):
        """今日の概要セクション"""
        summary_group = QGroupBox("📊 今日の概要")
        summary_layout = QVBoxLayout(summary_group)
        
        # 統計ラベル
        self.today_stats_labels = {}
        
        stats_layout = QHBoxLayout()
        
        # 作業時間
        work_frame = QFrame()
        work_frame.setFrameStyle(QFrame.Shape.Box)
        work_frame.setStyleSheet("border: 1px solid #3498db; border-radius: 5px; padding: 10px;")
        work_layout = QVBoxLayout(work_frame)
        
        work_title = QLabel("作業時間")
        work_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        work_title.setStyleSheet("font-weight: bold; color: #3498db;")
        work_layout.addWidget(work_title)
        
        self.today_stats_labels['work_time'] = QLabel("0分")
        self.today_stats_labels['work_time'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.today_stats_labels['work_time'].setFont(QFont("Arial", 16, QFont.Weight.Bold))
        work_layout.addWidget(self.today_stats_labels['work_time'])
        
        stats_layout.addWidget(work_frame)
        
        # セッション数
        session_frame = QFrame()
        session_frame.setFrameStyle(QFrame.Shape.Box)
        session_frame.setStyleSheet("border: 1px solid #e74c3c; border-radius: 5px; padding: 10px;")
        session_layout = QVBoxLayout(session_frame)
        
        session_title = QLabel("セッション")
        session_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        session_title.setStyleSheet("font-weight: bold; color: #e74c3c;")
        session_layout.addWidget(session_title)
        
        self.today_stats_labels['work_sessions'] = QLabel("0回")
        self.today_stats_labels['work_sessions'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.today_stats_labels['work_sessions'].setFont(QFont("Arial", 16, QFont.Weight.Bold))
        session_layout.addWidget(self.today_stats_labels['work_sessions'])
        
        stats_layout.addWidget(session_frame)
        
        # 完了タスク
        task_frame = QFrame()
        task_frame.setFrameStyle(QFrame.Shape.Box)
        task_frame.setStyleSheet("border: 1px solid #27ae60; border-radius: 5px; padding: 10px;")
        task_layout = QVBoxLayout(task_frame)
        
        task_title = QLabel("完了タスク")
        task_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        task_title.setStyleSheet("font-weight: bold; color: #27ae60;")
        task_layout.addWidget(task_title)
        
        self.today_stats_labels['completed_tasks'] = QLabel("0個")
        self.today_stats_labels['completed_tasks'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.today_stats_labels['completed_tasks'].setFont(QFont("Arial", 16, QFont.Weight.Bold))
        task_layout.addWidget(self.today_stats_labels['completed_tasks'])
        
        stats_layout.addWidget(task_frame)
        
        summary_layout.addLayout(stats_layout)
        
        layout.addWidget(summary_group)
        
    def setup_recommended_tasks(self, layout):
        """推奨タスクセクション"""
        rec_group = QGroupBox("⭐ 推奨タスク")
        rec_layout = QVBoxLayout(rec_group)
        
        # 推奨タスクリスト
        self.recommended_tasks_widget = QWidget()
        self.recommended_tasks_layout = QVBoxLayout(self.recommended_tasks_widget)
        self.recommended_tasks_layout.setSpacing(5)
        
        rec_layout.addWidget(self.recommended_tasks_widget)
        
        # 更新ボタン
        refresh_rec_btn = QPushButton("🔄 更新")
        refresh_rec_btn.clicked.connect(self.update_recommended_tasks)
        rec_layout.addWidget(refresh_rec_btn)
        
        layout.addWidget(rec_group)
        
    def setup_dashboard_placeholder(self):
        """ダッシュボード機能が利用できない場合のプレースホルダー"""
        placeholder_widget = QWidget()
        layout = QVBoxLayout(placeholder_widget)
        
        # メッセージ
        message_label = QLabel("📊 ダッシュボード機能")
        message_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message_label)
        
        info_label = QLabel("""
        ダッシュボード機能を使用するには、以下のパッケージが必要です：
        
        • matplotlib (グラフ描画)
        • pandas (データ分析)
        
        インストール方法：
        pip install matplotlib pandas
        """)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        layout.addWidget(info_label)
        
        install_btn = QPushButton("📦 パッケージをインストール")
        install_btn.clicked.connect(self.install_packages)
        install_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addWidget(install_btn)
        
        layout.addStretch()
        self.tab_widget.addTab(placeholder_widget, "📊 ダッシュボード")
        
    def install_packages(self):
        """必要なパッケージのインストール"""
        reply = QMessageBox.question(
            self, "パッケージインストール",
            "必要なパッケージをインストールしますか？\n\n"
            "pip install matplotlib pandas\n\n"
            "インストール後、アプリケーションを再起動してください。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            import subprocess
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "matplotlib", "pandas"], 
                             check=True)
                QMessageBox.information(self, "成功", "パッケージのインストールが完了しました。\n"
                                      "アプリケーションを再起動してください。")
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, "エラー", f"インストールに失敗しました: {e}")
    
    def setup_time_settings(self, layout):
        """時間設定UI"""
        settings_layout = QHBoxLayout()
        
        # 作業時間
        work_label = QLabel("作業時間:")
        work_label.setStyleSheet("color: #34495e; font-size: 12px;")
        settings_layout.addWidget(work_label)
        
        self.work_spinbox = QSpinBox()
        self.work_spinbox.setRange(1, 60)
        self.work_spinbox.setValue(self.work_minutes)
        self.work_spinbox.setSuffix(" 分")
        self.work_spinbox.valueChanged.connect(self.update_work_time)
        settings_layout.addWidget(self.work_spinbox)
        
        # 休憩時間
        break_label = QLabel("休憩時間:")
        break_label.setStyleSheet("color: #34495e; font-size: 12px;")
        settings_layout.addWidget(break_label)
        
        self.break_spinbox = QSpinBox()
        self.break_spinbox.setRange(1, 30)
        self.break_spinbox.setValue(self.break_minutes)
        self.break_spinbox.setSuffix(" 分")
        self.break_spinbox.valueChanged.connect(self.update_break_time)
        settings_layout.addWidget(self.break_spinbox)
        
        settings_layout.addStretch()
        layout.addLayout(settings_layout)
    
    def setup_buttons(self, layout):
        """ボタン設定"""
        button_layout = QHBoxLayout()
        
        # 開始/停止ボタン
        self.start_pause_btn = QPushButton("▶️ 開始")
        self.start_pause_btn.clicked.connect(self.toggle_timer)
        self.start_pause_btn.setStyleSheet("""
            QPushButton { 
                background-color: #27ae60; 
                color: white; 
                font-size: 16px; 
                font-weight: bold;
                padding: 12px 20px; 
                border-radius: 8px; 
                border: none;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        button_layout.addWidget(self.start_pause_btn)
        
        # リセットボタン
        self.reset_btn = QPushButton("🔄 リセット")
        self.reset_btn.clicked.connect(self.reset_timer)
        self.reset_btn.setStyleSheet("""
            QPushButton { 
                background-color: #e74c3c; 
                color: white; 
                font-size: 16px; 
                font-weight: bold;
                padding: 12px 20px; 
                border-radius: 8px; 
                border: none;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        button_layout.addWidget(self.reset_btn)
        
        layout.addLayout(button_layout)
    
    def setup_music_controls(self, layout):
        """音楽コントロール設定"""
        music_group = QGroupBox("🎵 音楽プリセット")
        music_layout = QVBoxLayout(music_group)
        
        # プリセット選択
        preset_layout = QHBoxLayout()
        preset_label = QLabel("プリセット:")
        preset_layout.addWidget(preset_label)
        
        self.preset_combo = QComboBox()
        presets = self.music_presets.get_available_presets()
        for preset in presets:
            info = self.music_presets.get_preset_info(preset)
            self.preset_combo.addItem(info['name'], preset)
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        preset_layout.addWidget(self.preset_combo)
        
        music_layout.addLayout(preset_layout)
        
        # 音量調整
        volume_layout = QHBoxLayout()
        volume_label = QLabel("音量:")
        volume_layout.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        volume_layout.addWidget(self.volume_slider)
        
        self.volume_label = QLabel("50%")
        volume_layout.addWidget(self.volume_label)
        
        music_layout.addLayout(volume_layout)
        
        layout.addWidget(music_group)
    
    def setup_stats_tab(self):
        """統計タブ設定"""
        stats_widget = QWidget()
        layout = QVBoxLayout(stats_widget)
        
        # 統計表示
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setFont(QFont("Courier", 10))
        layout.addWidget(self.stats_text)
        
        # 更新ボタン
        refresh_btn = QPushButton("🔄 統計更新")
        refresh_btn.clicked.connect(self.update_stats_display)
        layout.addWidget(refresh_btn)
        
        self.tab_widget.addTab(stats_widget, "統計")
        
        # 初期表示
        self.update_stats_display()
    
    def setup_settings_tab(self):
        """設定タブ設定"""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        
        # ウィンドウリサイズ設定
        resize_group = QGroupBox("🪟 ウィンドウ設定")
        resize_layout = QVBoxLayout(resize_group)
        
        self.auto_resize_checkbox = QCheckBox("自動リサイズ")
        self.auto_resize_checkbox.setChecked(True)
        self.auto_resize_checkbox.stateChanged.connect(self.on_auto_resize_changed)
        resize_layout.addWidget(self.auto_resize_checkbox)
        
        layout.addWidget(resize_group)
        
        # 音楽設定
        music_group = QGroupBox("🎵 音楽設定")
        music_layout = QVBoxLayout(music_group)
        
        self.music_enabled_checkbox = QCheckBox("音楽機能を有効にする")
        self.music_enabled_checkbox.setChecked(True)
        self.music_enabled_checkbox.stateChanged.connect(self.on_music_enabled_changed)
        music_layout.addWidget(self.music_enabled_checkbox)
        
        layout.addWidget(music_group)
        
        # Phase 3 設定
        phase3_group = QGroupBox("📊 Phase 3 設定")
        phase3_layout = QVBoxLayout(phase3_group)
        
        dashboard_status = "✅ 利用可能" if DASHBOARD_AVAILABLE else "❌ 利用不可"
        dashboard_label = QLabel(f"ダッシュボード機能: {dashboard_status}")
        phase3_layout.addWidget(dashboard_label)
        
        task_status = "✅ 利用可能"
        task_label = QLabel(f"タスク管理機能: {task_status}")
        phase3_layout.addWidget(task_label)
        
        theme_status = "✅ 利用可能"
        theme_label = QLabel(f"テーマ管理機能: {theme_status}")
        phase3_layout.addWidget(theme_label)
        
        if not DASHBOARD_AVAILABLE:
            install_btn = QPushButton("📦 必要なパッケージをインストール")
            install_btn.clicked.connect(self.install_packages)
            phase3_layout.addWidget(install_btn)
        
        layout.addWidget(phase3_group)
        
        layout.addStretch()
        self.tab_widget.addTab(settings_widget, "設定")
    
    def format_time(self, seconds):
        """時間フォーマット"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def toggle_timer(self):
        """タイマー開始/停止"""
        if self.is_running:
            self.pause_timer()
        else:
            self.start_timer()
    
    def start_timer(self):
        """タイマー開始"""
        # タスクと連携してセッションを開始
        self.task_integration.start_session_with_task()
        
        self.timer.start(1000)
        self.is_running = True
        self.start_pause_btn.setText("⏸️ 一時停止")
        self.status_label.setText("🔴 実行中...")
        
        # 音楽開始（エラーハンドリング付き）
        try:
            if self.is_work_session:
                self.music_presets.set_preset('work')
                self.window_resizer.resize_window('work')
            else:
                self.music_presets.set_preset('break')
                self.window_resizer.resize_window('break')
            
            self.music_presets.play()
        except Exception as e:
            logger.warning(f"音楽/ウィンドウ機能エラー: {e}")
        
        session_type = "作業" if self.is_work_session else "休憩"
        logger.info(f"▶️ {session_type}タイマー開始")
    
    def pause_timer(self):
        """タイマー一時停止"""
        self.timer.stop()
        self.is_running = False
        self.start_pause_btn.setText("▶️ 再開")
        self.status_label.setText("⏸️ 一時停止中")
        
        # 音楽一時停止（エラーハンドリング付き）
        try:
            self.music_presets.pause()
        except Exception as e:
            logger.warning(f"音楽一時停止エラー: {e}")
        
        logger.info("⏸️ タイマー一時停止")
    
    def reset_timer(self):
        """タイマーリセット"""
        self.timer.stop()
        self.is_running = False
        self.is_work_session = True
        self.session_count = 0
        self.time_left = self.work_minutes * 60
        
        # セッションタスクをクリア
        self.task_integration.clear_session_task()
        
        # 音楽停止（エラーハンドリング付き）
        try:
            self.music_presets.stop()
        except Exception as e:
            logger.warning(f"音楽停止エラー: {e}")
        
        self.update_display()
        self.start_pause_btn.setText("▶️ 開始")
        self.status_label.setText("🟢 準備完了")
        
        # ウィンドウサイズをデフォルトに（エラーハンドリング付き）
        try:
            self.window_resizer.resize_window('default')
        except Exception as e:
            logger.warning(f"ウィンドウリサイズエラー: {e}")
        
        logger.info("🔄 タイマーリセット")
    
    def update_timer(self):
        """タイマー更新"""
        if self.time_left > 0:
            self.time_left -= 1
            self.update_display()
            
            # アラート音の再生タイミング（エラーハンドリング付き）
            try:
                if self.time_left == 60:  # 1分前
                    self.music_presets.play_alert('1min')
                elif self.time_left == 30:  # 30秒前
                    self.music_presets.play_alert('30sec')
                elif self.time_left <= 3 and self.time_left > 0:  # 3秒前から毎秒
                    self.music_presets.play_alert('3sec')
            except Exception as e:
                logger.warning(f"アラート音再生エラー: {e}")
            
            # 残り時間による色変更
            if self.time_left <= 10:
                self.time_label.setStyleSheet("""
                    color: #ffffff; 
                    background-color: rgba(231, 76, 60, 0.9); 
                    padding: 20px; 
                    border-radius: 15px;
                    border: 2px solid #c0392b;
                """)
            elif self.time_left <= 60:
                self.time_label.setStyleSheet("""
                    color: #2c3e50; 
                    background-color: rgba(241, 196, 15, 0.9); 
                    padding: 20px; 
                    border-radius: 15px;
                    border: 2px solid #f39c12;
                """)
        else:
            self.timer_finished_handler()
    
    def timer_finished_handler(self):
        """タイマー完了処理"""
        self.timer.stop()
        self.is_running = False
        
        # タスクとの連携でセッション完了処理
        session_type = 'work' if self.is_work_session else 'break'
        duration = self.work_minutes if self.is_work_session else self.break_minutes
        self.task_integration.complete_session(session_type, duration)
        
        if self.is_work_session:
            # 作業完了
            self.session_count += 1
            self.status_label.setText(f"🎉 作業完了！{self.break_minutes}分休憩します")
            self.time_left = self.break_minutes * 60
            self.is_work_session = False
            
            # 休憩用音楽・ウィンドウサイズ（エラーハンドリング付き）
            try:
                self.music_presets.set_preset('break')
                self.window_resizer.resize_window('break')
            except Exception as e:
                logger.warning(f"休憩移行時エラー: {e}")
            
            logger.info(f"✅ 作業セッション #{self.session_count} 完了")
        else:
            # 休憩完了
            self.status_label.setText("💪 休憩完了！次の作業を開始します")
            self.time_left = self.work_minutes * 60
            self.is_work_session = True
            
            # 作業用音楽・ウィンドウサイズ（エラーハンドリング付き）
            try:
                self.music_presets.set_preset('work')
                self.window_resizer.resize_window('work')
            except Exception as e:
                logger.warning(f"作業移行時エラー: {e}")
            
            logger.info("🔄 休憩完了、次の作業セッション準備")
        
        self.update_display()
        self.start_pause_btn.setText("▶️ 開始")
        
        # 自動で次のセッション開始（エラーハンドリング付き）
        try:
            self.start_timer()
        except Exception as e:
            logger.warning(f"自動開始エラー: {e}")
        
        # 統計更新（エラーハンドリング付き）
        try:
            self.update_stats_display()
            self.update_task_displays()
        except Exception as e:
            logger.warning(f"統計更新エラー: {e}")
    
    def update_display(self):
        """表示更新"""
        self.time_label.setText(self.format_time(self.time_left))
        
        if self.is_work_session:
            session_text = f"📖 作業セッション #{self.session_count + 1}"
            self.time_label.setStyleSheet("""
                color: #2c3e50; 
                background-color: rgba(255,255,255,0.9); 
                padding: 20px; 
                border-radius: 15px;
                border: 2px solid #3498db;
            """)
        else:
            session_text = f"☕ 休憩タイム"
            self.time_label.setStyleSheet("""
                color: #ffffff; 
                background-color: rgba(46, 204, 113, 0.9); 
                padding: 20px; 
                border-radius: 15px;
                border: 2px solid #27ae60;
            """)
        
        self.session_label.setText(session_text)
    
    def update_work_time(self, value):
        """作業時間更新"""
        self.work_minutes = value
        if self.is_work_session and not self.is_running:
            self.time_left = self.work_minutes * 60
            self.update_display()
    
    def update_break_time(self, value):
        """休憩時間更新"""
        self.break_minutes = value
        if not self.is_work_session and not self.is_running:
            self.time_left = self.break_minutes * 60
            self.update_display()
    
    def on_preset_changed(self):
        """プリセット変更"""
        try:
            preset_key = self.preset_combo.currentData()
            if preset_key:
                self.music_presets.set_preset(preset_key)
        except Exception as e:
            logger.warning(f"プリセット変更エラー: {e}")
    
    def on_volume_changed(self, value):
        """音量変更"""
        try:
            volume = value / 100.0
            self.music_presets.set_volume(volume)
            self.volume_label.setText(f"{value}%")
        except Exception as e:
            logger.warning(f"音量変更エラー: {e}")
    
    def on_auto_resize_changed(self, state):
        """自動リサイズ設定変更"""
        try:
            enabled = state == Qt.CheckState.Checked.value
            self.window_resizer.toggle_auto_resize(enabled)
        except Exception as e:
            logger.warning(f"自動リサイズ設定エラー: {e}")
    
    def on_music_enabled_changed(self, state):
        """音楽機能設定変更"""
        try:
            enabled = state == Qt.CheckState.Checked.value
            self.music_presets.enable(enabled)
        except Exception as e:
            logger.warning(f"音楽機能設定エラー: {e}")
    
    def update_stats_display(self):
        """統計表示更新"""
        try:
            stats_summary = self.statistics.get_stats_summary()
            self.stats_text.setText(stats_summary)
        except Exception as e:
            logger.warning(f"統計表示更新エラー: {e}")
            self.stats_text.setText("統計データの取得に失敗しました")
    
    def update_task_displays(self):
        """タスク関連表示を更新"""
        try:
            # タスク選択ウィジェットを更新
            self.task_selection.update_task_info()
            
            # 今日の概要を更新
            summary = self.task_integration.get_today_task_summary()
            self.today_stats_labels['work_time'].setText(f"{summary['work_time']}分")
            self.today_stats_labels['work_sessions'].setText(f"{summary['work_sessions']}回")
            self.today_stats_labels['completed_tasks'].setText(f"{summary['completed_tasks']}個")
            
            # 推奨タスクを更新
            self.update_recommended_tasks()
            
        except Exception as e:
            logger.warning(f"タスク表示更新エラー: {e}")
    
    def update_recommended_tasks(self):
        """推奨タスクを更新"""
        try:
            # 既存のウィジェットを削除
            for i in reversed(range(self.recommended_tasks_layout.count())):
                child = self.recommended_tasks_layout.itemAt(i).widget()
                if child:
                    child.setParent(None)
            
            # 推奨タスクを取得
            recommendations = self.task_integration.get_recommended_tasks(3)
            
            if not recommendations:
                no_task_label = QLabel("推奨タスクがありません")
                no_task_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
                self.recommended_tasks_layout.addWidget(no_task_label)
                return
            
            # 推奨タスクを表示
            for rec in recommendations:
                task_btn = QPushButton(f"🎯 {rec['title']}")
                task_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {rec['priority_color']};
                        color: white;
                        padding: 8px 12px;
                        border-radius: 4px;
                        border: none;
                        font-size: 12px;
                        text-align: left;
                    }}
                    QPushButton:hover {{
                        background-color: {rec['priority_color']};
                        opacity: 0.8;
                    }}
                """)
                task_btn.clicked.connect(
                    lambda checked, task_id=rec['task_id']: self.set_recommended_task(task_id)
                )
                self.recommended_tasks_layout.addWidget(task_btn)
            
        except Exception as e:
            logger.warning(f"推奨タスク更新エラー: {e}")
    
    def set_recommended_task(self, task_id: str):
        """推奨タスクを現在のタスクに設定"""
        try:
            self.task_integration.get_task_manager().set_current_task(task_id)
            self.update_task_displays()
            
            task = self.task_integration.get_task_manager().get_task(task_id)
            if task:
                QMessageBox.information(self, "タスク設定", f"現在のタスクを '{task.title}' に設定しました")
        except Exception as e:
            logger.error(f"推奨タスク設定エラー: {e}")
    
    def on_task_change_requested(self, request):
        """タスク変更要求"""
        if request == "select_task":
            # タスクタブに切り替え
            for i in range(self.tab_widget.count()):
                if "タスク管理" in self.tab_widget.tabText(i):
                    self.tab_widget.setCurrentIndex(i)
                    break
    
    def on_task_selected(self, task_id: str):
        """タスクが選択された時の処理"""
        self.update_task_displays()
    
    def on_task_completed(self, task_id: str):
        """タスクが完了した時の処理"""
        try:
            task = self.task_integration.get_task_manager().get_task(task_id)
            if task:
                QMessageBox.information(self, "タスク完了", f"🎉 タスク '{task.title}' が完了しました！")
                self.update_task_displays()
        except Exception as e:
            logger.error(f"タスク完了通知エラー: {e}")
    
    def on_pomodoro_completed(self, task_id: str, duration: int):
        """ポモドーロが完了した時の処理"""
        try:
            task = self.task_integration.get_task_manager().get_task(task_id)
            if task:
                logger.info(f"🍅 ポモドーロ完了: {task.title} (+{duration}分)")
                self.update_task_displays()
        except Exception as e:
            logger.error(f"ポモドーロ完了処理エラー: {e}")
    
    def on_theme_changed(self, theme_name: str):
        """テーマが変更された時の処理"""
        try:
            self.apply_current_theme()
            logger.info(f"🎨 テーマ適用: {theme_name}")
        except Exception as e:
            logger.error(f"❌ テーマ適用エラー: {e}")
    
    def apply_current_theme(self):
        """現在のテーマを適用"""
        try:
            theme_manager = self.theme_widget.get_theme_manager()
            stylesheet = theme_manager.get_stylesheet()
            
            # アプリケーション全体にスタイルシートを適用
            self.setStyleSheet(stylesheet)
            
            # 透明度を適用
            current_theme = theme_manager.get_current_theme()
            self.setWindowOpacity(current_theme.transparency)
            
            logger.info(f"🎨 テーマ適用完了: {current_theme.name}")
        except Exception as e:
            logger.error(f"❌ テーマ適用エラー: {e}")

def main():
    """メイン実行"""
    print("🚀 Pomodoro Timer Phase 3 Full Edition 起動中...")
    logger.info("🚀 Phase 3 完全版アプリケーション開始")
    
    # 環境変数設定
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    
    # QApplication作成
    app = QApplication(sys.argv)
    app.setApplicationName("Pomodoro Timer Phase 3 Full")
    app.setApplicationVersion("3.0.0")
    
    try:
        # メインウィンドウ作成
        window = PomodoroTimerPhase3Full()
        window.show()
        
        print("✅ Phase 3 完全版起動完了！")
        print("🍅 統合機能:")
        print("  - 🪟 ウィンドウサイズ自動制御")
        print("  - 📊 統計機能")
        print("  - 🎵 音楽プリセット")
        print("  - 📊 統計ダッシュボード")
        print("  - 📋 タスク管理システム")
        print("  - 🔗 タスク・ポモドーロ連携")
        print("  - 🎨 カスタムテーマ機能")
        
        if DASHBOARD_AVAILABLE:
            print("\n📊 ダッシュボード機能: 有効")
        else:
            print("\n📊 ダッシュボード機能: 無効")
        
        print("\n📋 タスク管理機能: 有効")
        print("  - タスクの作成・編集・削除")
        print("  - 優先度管理")
        print("  - ポモドーロ連携")
        print("  - 進捗追跡")
        
        print("\n🎨 テーマ機能: 有効")
        print("  - ライト・ダークテーマ")
        print("  - カスタムテーマ作成")
        print("  - テーマのインポート・エクスポート")
        print("  - リアルタイム適用")
        
        logger.info("✅ Phase 3 完全版アプリケーション初期化完了")
        
        # イベントループ開始
        return app.exec()
        
    except Exception as e:
        error_msg = f"❌ 予期しないエラー: {e}"
        print(error_msg)
        logger.error(error_msg)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())