#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pomodoro Timer Phase 2 - 統合版
Phase 2 追加機能統合版
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
        logging.FileHandler('phase2.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                           QWidget, QLabel, QPushButton, QSpinBox, QCheckBox, 
                           QSlider, QComboBox, QTextEdit, QGroupBox, QTabWidget)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

# Phase 2 機能インポート
from features.window_resizer import WindowResizer
from features.statistics import PomodoroStatistics
from features.music_presets import MusicPresetsSimple as MusicPresets

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

class PomodoroTimerPhase2(QMainWindow):
    """Phase 2 統合版ポモドーロタイマー"""
    
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
        
        self.setup_ui()
        
        logger.info("✅ Phase 2 ポモドーロタイマー初期化完了")
        
    def setup_ui(self):
        """UI設定"""
        self.setWindowTitle("🍅 Pomodoro Timer Phase 2")
        self.setGeometry(100, 100, 600, 500)
        
        # 透明度・最前面設定
        self.setWindowOpacity(0.9)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # メインタブ
        self.setup_main_tab()
        
        # 統計タブ
        self.setup_stats_tab()
        
        # 設定タブ
        self.setup_settings_tab()
        
        logger.info("🎨 Phase 2 UI設定完了")
    
    def setup_main_tab(self):
        """メインタブ設定"""
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # タイトル
        title_label = QLabel("🍅 Pomodoro Timer Phase 2")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #e74c3c; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # セッション表示
        self.session_label = QLabel("📖 作業セッション #1")
        self.session_label.setFont(QFont("Arial", 12))
        self.session_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.session_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        layout.addWidget(self.session_label)
        
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
        layout.addWidget(self.time_label)
        
        # 時間設定
        self.setup_time_settings(layout)
        
        # ボタン
        self.setup_buttons(layout)
        
        # ステータス
        self.status_label = QLabel("🟢 準備完了")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 14px; margin-top: 5px;")
        layout.addWidget(self.status_label)
        
        # 音楽プリセット選択
        self.setup_music_controls(layout)
        
        self.tab_widget.addTab(main_widget, "メイン")
    
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
                elif self.time_left <= 3 and self.time_left > 0:  # 5秒前から毎秒
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
        
        # 統計記録
        session_type = 'work' if self.is_work_session else 'break'
        duration = self.work_minutes if self.is_work_session else self.break_minutes
        self.statistics.record_session(session_type, duration)
        
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

def main():
    """メイン実行"""
    print("🚀 Pomodoro Timer Phase 2 起動中...")
    logger.info("🚀 Phase 2 アプリケーション開始")
    
    # 環境変数設定
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    
    # WSL/Linux環境での表示設定
    if 'DISPLAY' not in os.environ and sys.platform.startswith('linux'):
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        logger.warning("⚠️ GUI環境未検出、オフスクリーンモードで実行")
    
    # QApplication作成
    app = QApplication(sys.argv)
    app.setApplicationName("Pomodoro Timer Phase 2")
    app.setApplicationVersion("2.0.0")
    
    try:
        # メインウィンドウ作成
        window = PomodoroTimerPhase2()
        window.show()
        
        print("✅ Phase 2 起動完了！")
        print("🍅 新機能:")
        print("  - 🪟 ウィンドウサイズ自動制御")
        print("  - 📊 統計機能")
        print("  - 🎵 音楽プリセット")
        
        logger.info("✅ Phase 2 アプリケーション初期化完了")
        
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