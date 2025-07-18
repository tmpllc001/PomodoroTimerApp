#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pomodoro Timer Phase 2 - 最終統合版
全機能統合完成版
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
        logging.FileHandler('phase2_final.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                           QWidget, QLabel, QPushButton, QSpinBox, QCheckBox, 
                           QSlider, QComboBox, QTextEdit, QGroupBox, QTabWidget,
                           QProgressBar, QFrame)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QPropertyAnimation, QRect
from PyQt6.QtGui import QFont, QPalette, QColor

# Phase 2 機能インポート
try:
    from features.window_resizer import WindowResizer
    from features.statistics import PomodoroStatistics
    from features.music_presets import MusicPresets, SessionType
    
    logger.info("✅ Phase 2 機能インポート成功")
except ImportError as e:
    logger.error(f"❌ Phase 2 機能インポートエラー: {e}")
    # フォールバック用の空クラス
    class WindowResizer:
        def __init__(self, window): pass
        def resize_window(self, session_type, animate=True): pass
        def toggle_auto_resize(self, enabled): pass
    
    class PomodoroStatistics:
        def __init__(self, data_file="statistics.json"): pass
        def record_session(self, session_type, duration_minutes): pass
        def get_stats_summary(self): return "統計機能利用不可"
    
    class MusicPresets:
        def __init__(self): pass
        def start_session(self, session_type, duration_minutes): return True
        def stop_session(self): return True
        def set_volume(self, volume): return True
        def get_session_status(self): return {}
    
    class SessionType:
        WORK = "work"
        BREAK = "break"

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

class PomodoroTimerPhase2Final(QMainWindow):
    """Phase 2 最終統合版ポモドーロタイマー"""
    
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
        self.statistics = PomodoroStatistics("data/statistics.json")
        self.music_presets = MusicPresets()
        
        # UI設定
        self.setup_ui()
        
        # 統計更新タイマー
        self.stats_update_timer = QTimer()
        self.stats_update_timer.timeout.connect(self.update_stats_display)
        self.stats_update_timer.start(5000)  # 5秒ごとに更新
        
        logger.info("✅ Phase 2 最終版ポモドーロタイマー初期化完了")
        
    def setup_ui(self):
        """UI設定"""
        self.setWindowTitle("🍅 Pomodoro Timer Phase 2 Final")
        self.setGeometry(100, 100, 700, 600)
        
        # スタイル設定
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                padding: 10px 20px;
                margin: 2px;
                border-radius: 5px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #007bff;
                color: white;
            }
        """)
        
        # 透明度・最前面設定
        self.setWindowOpacity(0.95)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # タブ作成
        self.setup_main_tab()
        self.setup_stats_tab()
        self.setup_music_tab()
        self.setup_settings_tab()
        
        logger.info("🎨 Phase 2 最終版UI設定完了")
    
    def setup_main_tab(self):
        """メインタブ設定"""
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # タイトル
        title_label = QLabel("🍅 Pomodoro Timer Phase 2")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            color: #e74c3c; 
            margin-bottom: 15px;
            background-color: rgba(255,255,255,0.8);
            padding: 15px;
            border-radius: 10px;
        """)
        layout.addWidget(title_label)
        
        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # セッション表示
        self.session_label = QLabel("📖 作業セッション #1")
        self.session_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.session_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.session_label.setStyleSheet("""
            color: #2c3e50; 
            margin-bottom: 10px;
            background-color: rgba(255,255,255,0.9);
            padding: 10px;
            border-radius: 8px;
        """)
        layout.addWidget(self.session_label)
        
        # タイマー表示
        self.time_label = QLabel(self.format_time(self.time_left))
        self.time_label.setFont(QFont("Arial", 48, QFont.Weight.Bold))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("""
            color: #2c3e50; 
            background-color: rgba(255,255,255,0.95); 
            padding: 30px; 
            border-radius: 20px;
            border: 3px solid #3498db;
            margin: 15px;
        """)
        layout.addWidget(self.time_label)
        
        # 時間設定
        self.setup_time_settings(layout)
        
        # ボタン
        self.setup_buttons(layout)
        
        # ステータス
        self.status_label = QLabel("🟢 準備完了")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            color: #7f8c8d; 
            font-size: 16px; 
            margin-top: 10px;
            background-color: rgba(255,255,255,0.8);
            padding: 10px;
            border-radius: 8px;
        """)
        layout.addWidget(self.status_label)
        
        self.tab_widget.addTab(main_widget, "🍅 メイン")
    
    def setup_time_settings(self, layout):
        """時間設定UI"""
        settings_group = QGroupBox("⏰ 時間設定")
        settings_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: rgba(255,255,255,0.9);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        settings_layout = QHBoxLayout(settings_group)
        
        # 作業時間
        work_label = QLabel("作業時間:")
        work_label.setStyleSheet("color: #34495e; font-size: 14px; font-weight: bold;")
        settings_layout.addWidget(work_label)
        
        self.work_spinbox = QSpinBox()
        self.work_spinbox.setRange(1, 60)
        self.work_spinbox.setValue(self.work_minutes)
        self.work_spinbox.setSuffix(" 分")
        self.work_spinbox.valueChanged.connect(self.update_work_time)
        self.work_spinbox.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
                font-size: 14px;
            }
        """)
        settings_layout.addWidget(self.work_spinbox)
        
        # 休憩時間
        break_label = QLabel("休憩時間:")
        break_label.setStyleSheet("color: #34495e; font-size: 14px; font-weight: bold;")
        settings_layout.addWidget(break_label)
        
        self.break_spinbox = QSpinBox()
        self.break_spinbox.setRange(1, 30)
        self.break_spinbox.setValue(self.break_minutes)
        self.break_spinbox.setSuffix(" 分")
        self.break_spinbox.valueChanged.connect(self.update_break_time)
        self.break_spinbox.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
                font-size: 14px;
            }
        """)
        settings_layout.addWidget(self.break_spinbox)
        
        layout.addWidget(settings_group)
    
    def setup_buttons(self, layout):
        """ボタン設定"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        # 開始/停止ボタン
        self.start_pause_btn = QPushButton("▶️ 開始")
        self.start_pause_btn.clicked.connect(self.toggle_timer)
        self.start_pause_btn.setStyleSheet("""
            QPushButton { 
                background-color: #27ae60; 
                color: white; 
                font-size: 18px; 
                font-weight: bold;
                padding: 15px 30px; 
                border-radius: 10px; 
                border: none;
                min-width: 120px;
            }
            QPushButton:hover { 
                background-color: #2ecc71; 
                transform: translateY(-2px);
            }
            QPushButton:pressed { 
                background-color: #229954; 
                transform: translateY(0px);
            }
        """)
        button_layout.addWidget(self.start_pause_btn)
        
        # リセットボタン
        self.reset_btn = QPushButton("🔄 リセット")
        self.reset_btn.clicked.connect(self.reset_timer)
        self.reset_btn.setStyleSheet("""
            QPushButton { 
                background-color: #e74c3c; 
                color: white; 
                font-size: 18px; 
                font-weight: bold;
                padding: 15px 30px; 
                border-radius: 10px; 
                border: none;
                min-width: 120px;
            }
            QPushButton:hover { 
                background-color: #c0392b; 
                transform: translateY(-2px);
            }
            QPushButton:pressed { 
                background-color: #a93226; 
                transform: translateY(0px);
            }
        """)
        button_layout.addWidget(self.reset_btn)
        
        layout.addLayout(button_layout)
    
    def setup_stats_tab(self):
        """統計タブ設定"""
        stats_widget = QWidget()
        layout = QVBoxLayout(stats_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 統計サマリー
        self.stats_summary_label = QLabel("📊 統計サマリー")
        self.stats_summary_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.stats_summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stats_summary_label.setStyleSheet("""
            color: #2c3e50;
            background-color: rgba(255,255,255,0.9);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
        """)
        layout.addWidget(self.stats_summary_label)
        
        # 統計表示
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setFont(QFont("Courier New", 12))
        self.stats_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 8px;
                padding: 15px;
                font-family: 'Courier New', monospace;
            }
        """)
        layout.addWidget(self.stats_text)
        
        # 更新ボタン
        refresh_btn = QPushButton("🔄 統計更新")
        refresh_btn.clicked.connect(self.update_stats_display)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 12px 24px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addWidget(refresh_btn)
        
        self.tab_widget.addTab(stats_widget, "📊 統計")
        
        # 初期表示
        self.update_stats_display()
    
    def setup_music_tab(self):
        """音楽タブ設定"""
        music_widget = QWidget()
        layout = QVBoxLayout(music_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 音楽コントロール
        music_group = QGroupBox("🎵 音楽コントロール")
        music_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: rgba(255,255,255,0.9);
            }
        """)
        music_layout = QVBoxLayout(music_group)
        
        # 音量調整
        volume_layout = QHBoxLayout()
        volume_label = QLabel("音量:")
        volume_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        volume_layout.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #bdc3c7;
                height: 8px;
                background: #ecf0f1;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                border: 1px solid #2980b9;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
        """)
        volume_layout.addWidget(self.volume_slider)
        
        self.volume_label = QLabel("70%")
        self.volume_label.setStyleSheet("font-weight: bold; color: #2c3e50; min-width: 40px;")
        volume_layout.addWidget(self.volume_label)
        
        music_layout.addLayout(volume_layout)
        
        # 音楽ステータス
        self.music_status_label = QLabel("🎵 音楽機能準備完了")
        self.music_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.music_status_label.setStyleSheet("""
            color: #27ae60;
            font-weight: bold;
            background-color: rgba(255,255,255,0.8);
            padding: 10px;
            border-radius: 8px;
            margin: 10px 0;
        """)
        music_layout.addWidget(self.music_status_label)
        
        layout.addWidget(music_group)
        
        # 音楽プリセット情報
        preset_info = QTextEdit()
        preset_info.setReadOnly(True)
        preset_info.setMaximumHeight(200)
        preset_info.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
            }
        """)
        preset_info.setHtml("""
        <h3>🎵 音楽プリセット情報</h3>
        <p><strong>作業用BGM:</strong> work_bgm.mp3</p>
        <p><strong>休憩用BGM:</strong> break_bgm.mp3</p>
        <p><strong>アラート音:</strong> alert_1min.mp3, alert_30sec.mp3</p>
        <p><strong>時報音:</strong> countdown_tick.mp3</p>
        <p><em>音楽ファイルは assets/music/ フォルダに配置してください。</em></p>
        """)
        layout.addWidget(preset_info)
        
        layout.addStretch()
        self.tab_widget.addTab(music_widget, "🎵 音楽")
    
    def setup_settings_tab(self):
        """設定タブ設定"""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ウィンドウリサイズ設定
        resize_group = QGroupBox("🪟 ウィンドウ設定")
        resize_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: rgba(255,255,255,0.9);
            }
        """)
        resize_layout = QVBoxLayout(resize_group)
        
        self.auto_resize_checkbox = QCheckBox("自動リサイズを有効にする")
        self.auto_resize_checkbox.setChecked(True)
        self.auto_resize_checkbox.stateChanged.connect(self.on_auto_resize_changed)
        self.auto_resize_checkbox.setStyleSheet("""
            QCheckBox {
                font-weight: bold;
                color: #2c3e50;
                padding: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        resize_layout.addWidget(self.auto_resize_checkbox)
        
        resize_info = QLabel("作業中: 右上角（200x100px）\n休憩中: 中央（600x400px）")
        resize_info.setStyleSheet("""
            color: #7f8c8d;
            font-size: 12px;
            margin-left: 25px;
            background-color: rgba(255,255,255,0.7);
            padding: 8px;
            border-radius: 4px;
        """)
        resize_layout.addWidget(resize_info)
        
        layout.addWidget(resize_group)
        
        # 音楽設定
        music_group = QGroupBox("🎵 音楽設定")
        music_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: rgba(255,255,255,0.9);
            }
        """)
        music_layout = QVBoxLayout(music_group)
        
        self.music_enabled_checkbox = QCheckBox("音楽機能を有効にする")
        self.music_enabled_checkbox.setChecked(True)
        self.music_enabled_checkbox.stateChanged.connect(self.on_music_enabled_changed)
        self.music_enabled_checkbox.setStyleSheet("""
            QCheckBox {
                font-weight: bold;
                color: #2c3e50;
                padding: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        music_layout.addWidget(self.music_enabled_checkbox)
        
        layout.addWidget(music_group)
        
        # 統計設定
        stats_group = QGroupBox("📊 統計設定")
        stats_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: rgba(255,255,255,0.9);
            }
        """)
        stats_layout = QVBoxLayout(stats_group)
        
        stats_info = QLabel("統計データは data/statistics.json に保存されます。")
        stats_info.setStyleSheet("""
            color: #7f8c8d;
            font-size: 12px;
            padding: 8px;
            background-color: rgba(255,255,255,0.7);
            border-radius: 4px;
        """)
        stats_layout.addWidget(stats_info)
        
        layout.addWidget(stats_group)
        
        layout.addStretch()
        self.tab_widget.addTab(settings_widget, "⚙️ 設定")
    
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
        self.timer.start(1000)
        self.is_running = True
        self.start_pause_btn.setText("⏸️ 一時停止")
        self.status_label.setText("🔴 実行中...")
        
        # 音楽開始
        try:
            if self.is_work_session:
                self.music_presets.start_session(SessionType.WORK, self.work_minutes)
                self.window_resizer.resize_window('work')
            else:
                self.music_presets.start_session(SessionType.BREAK, self.break_minutes)
                self.window_resizer.resize_window('break')
        except Exception as e:
            logger.warning(f"音楽/リサイズ機能エラー: {e}")
        
        session_type = "作業" if self.is_work_session else "休憩"
        logger.info(f"▶️ {session_type}タイマー開始")
        
        # 音楽ステータス更新
        self.update_music_status()
    
    def pause_timer(self):
        """タイマー一時停止"""
        self.timer.stop()
        self.is_running = False
        self.start_pause_btn.setText("▶️ 再開")
        self.status_label.setText("⏸️ 一時停止中")
        
        # 音楽一時停止
        try:
            self.music_presets.pause_session()
        except Exception as e:
            logger.warning(f"音楽一時停止エラー: {e}")
        
        logger.info("⏸️ タイマー一時停止")
        
        # 音楽ステータス更新
        self.update_music_status()
    
    def reset_timer(self):
        """タイマーリセット"""
        self.timer.stop()
        self.is_running = False
        self.is_work_session = True
        self.session_count = 0
        self.time_left = self.work_minutes * 60
        
        # 音楽停止
        try:
            self.music_presets.stop_session()
        except Exception as e:
            logger.warning(f"音楽停止エラー: {e}")
        
        self.update_display()
        self.start_pause_btn.setText("▶️ 開始")
        self.status_label.setText("🟢 準備完了")
        
        # ウィンドウサイズをデフォルトに
        try:
            self.window_resizer.resize_window('default')
        except Exception as e:
            logger.warning(f"ウィンドウリサイズエラー: {e}")
        
        # プログレスバーリセット
        self.progress_bar.setValue(0)
        
        logger.info("🔄 タイマーリセット")
        
        # 音楽ステータス更新
        self.update_music_status()
    
    def update_timer(self):
        """タイマー更新"""
        if self.time_left > 0:
            self.time_left -= 1
            self.update_display()
            
            # プログレスバー更新
            total_time = self.work_minutes * 60 if self.is_work_session else self.break_minutes * 60
            progress = ((total_time - self.time_left) / total_time) * 100
            self.progress_bar.setValue(int(progress))
            
            # 残り時間による色変更
            if self.time_left <= 10:
                self.time_label.setStyleSheet("""
                    color: #ffffff; 
                    background-color: rgba(231, 76, 60, 0.95); 
                    padding: 30px; 
                    border-radius: 20px;
                    border: 3px solid #c0392b;
                    margin: 15px;
                """)
            elif self.time_left <= 60:
                self.time_label.setStyleSheet("""
                    color: #2c3e50; 
                    background-color: rgba(241, 196, 15, 0.95); 
                    padding: 30px; 
                    border-radius: 20px;
                    border: 3px solid #f39c12;
                    margin: 15px;
                """)
        else:
            self.timer_finished_handler()
    
    def timer_finished_handler(self):
        """タイマー完了処理"""
        self.timer.stop()
        self.is_running = False
        
        # 統計記録
        session_type = 'work' if self.is_work_session else 'break'
        duration = self.work_minutes if self.is_work_session else self.break_minutes
        
        try:
            self.statistics.record_session(session_type, duration)
        except Exception as e:
            logger.warning(f"統計記録エラー: {e}")
        
        if self.is_work_session:
            # 作業完了
            self.session_count += 1
            self.status_label.setText(f"🎉 作業完了！{self.break_minutes}分休憩します")
            self.time_left = self.break_minutes * 60
            self.is_work_session = False
            
            # 休憩用音楽・ウィンドウサイズ
            try:
                self.music_presets.start_session(SessionType.BREAK, self.break_minutes)
                self.window_resizer.resize_window('break')
            except Exception as e:
                logger.warning(f"休憩モード設定エラー: {e}")
            
            logger.info(f"✅ 作業セッション #{self.session_count} 完了")
        else:
            # 休憩完了
            self.status_label.setText("💪 休憩完了！次の作業を開始します")
            self.time_left = self.work_minutes * 60
            self.is_work_session = True
            
            # 作業用音楽・ウィンドウサイズ
            try:
                self.music_presets.start_session(SessionType.WORK, self.work_minutes)
                self.window_resizer.resize_window('work')
            except Exception as e:
                logger.warning(f"作業モード設定エラー: {e}")
            
            logger.info("🔄 休憩完了、次の作業セッション準備")
        
        self.update_display()
        self.start_pause_btn.setText("▶️ 開始")
        
        # プログレスバーリセット
        self.progress_bar.setValue(0)
        
        # 自動で次のセッション開始
        self.start_timer()
        
        # 統計更新
        self.update_stats_display()
        
        # 音楽ステータス更新
        self.update_music_status()
    
    def update_display(self):
        """表示更新"""
        self.time_label.setText(self.format_time(self.time_left))
        
        if self.is_work_session:
            session_text = f"📖 作業セッション #{self.session_count + 1}"
            if self.time_left > 60:
                self.time_label.setStyleSheet("""
                    color: #2c3e50; 
                    background-color: rgba(255,255,255,0.95); 
                    padding: 30px; 
                    border-radius: 20px;
                    border: 3px solid #3498db;
                    margin: 15px;
                """)
        else:
            session_text = f"☕ 休憩タイム"
            if self.time_left > 60:
                self.time_label.setStyleSheet("""
                    color: #ffffff; 
                    background-color: rgba(46, 204, 113, 0.95); 
                    padding: 30px; 
                    border-radius: 20px;
                    border: 3px solid #27ae60;
                    margin: 15px;
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
    
    def on_volume_changed(self, value):
        """音量変更"""
        volume = value / 100.0
        try:
            self.music_presets.set_volume(volume)
        except Exception as e:
            logger.warning(f"音量変更エラー: {e}")
        
        self.volume_label.setText(f"{value}%")
    
    def on_auto_resize_changed(self, state):
        """自動リサイズ設定変更"""
        enabled = state == Qt.CheckState.Checked.value
        try:
            self.window_resizer.toggle_auto_resize(enabled)
        except Exception as e:
            logger.warning(f"自動リサイズ設定エラー: {e}")
    
    def on_music_enabled_changed(self, state):
        """音楽機能設定変更"""
        enabled = state == Qt.CheckState.Checked.value
        try:
            self.music_presets.enable_music(enabled)
        except Exception as e:
            logger.warning(f"音楽機能設定エラー: {e}")
        
        self.update_music_status()
    
    def update_stats_display(self):
        """統計表示更新"""
        try:
            stats_summary = self.statistics.get_stats_summary()
            self.stats_text.setText(stats_summary)
        except Exception as e:
            logger.warning(f"統計表示更新エラー: {e}")
            self.stats_text.setText(f"統計データ取得エラー: {e}")
    
    def update_music_status(self):
        """音楽ステータス更新"""
        try:
            status = self.music_presets.get_session_status()
            if status.get('is_playing', False):
                session_type = status.get('session_type', 'unknown')
                self.music_status_label.setText(f"🎵 {session_type.title()} BGM再生中")
                self.music_status_label.setStyleSheet("""
                    color: #27ae60;
                    font-weight: bold;
                    background-color: rgba(255,255,255,0.8);
                    padding: 10px;
                    border-radius: 8px;
                    margin: 10px 0;
                """)
            else:
                self.music_status_label.setText("🎵 音楽停止中")
                self.music_status_label.setStyleSheet("""
                    color: #7f8c8d;
                    font-weight: bold;
                    background-color: rgba(255,255,255,0.8);
                    padding: 10px;
                    border-radius: 8px;
                    margin: 10px 0;
                """)
        except Exception as e:
            logger.warning(f"音楽ステータス更新エラー: {e}")
            self.music_status_label.setText("🎵 音楽ステータス取得エラー")

def main():
    """メイン実行"""
    print("🚀 Pomodoro Timer Phase 2 Final 起動中...")
    logger.info("🚀 Phase 2 Final アプリケーション開始")
    
    # 環境変数設定
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    
    # WSL/Linux環境での表示設定
    if 'DISPLAY' not in os.environ and sys.platform.startswith('linux'):
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        logger.warning("⚠️ GUI環境未検出、オフスクリーンモードで実行")
    
    # QApplication作成
    app = QApplication(sys.argv)
    app.setApplicationName("Pomodoro Timer Phase 2 Final")
    app.setApplicationVersion("2.0.0-final")
    
    try:
        # メインウィンドウ作成
        window = PomodoroTimerPhase2Final()
        window.show()
        
        print("✅ Phase 2 Final 起動完了！")
        print("🎉 新機能:")
        print("  - 🪟 ウィンドウサイズ自動制御（作業中：右上角、休憩中：中央）")
        print("  - 📊 統計機能（セッション数、時間、生産性スコア）")
        print("  - 🎵 音楽プリセット（BGM自動切り替え）")
        print("  - 🎨 改良されたUI（プログレスバー、タブ、スタイル）")
        
        if AUDIO_AVAILABLE:
            print("  - 🔊 音声機能: 有効")
        else:
            print("  - 🔇 音声機能: 無効（エラー対応済み）")
        
        logger.info("✅ Phase 2 Final アプリケーション初期化完了")
        
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