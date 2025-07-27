#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pomodoro Timer Phase 3 - デュアルモード版
動作確認済みのmain_phase3_with_tasks.pyに直接ミニマルモード機能を追加
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
                           QWidget, QLabel, QPushButton, QSpinBox, QCheckBox, 
                           QSlider, QComboBox, QTextEdit, QGroupBox, QTabWidget,
                           QMessageBox, QFrame, QSplitter, QMenu)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint, QSettings
from PyQt6.QtGui import QFont, QAction, QMouseEvent
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl

# 音声プレイヤー（pygame代替）
try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

# Phase 3モジュールをインポート
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.features.tasks.task_widget import TaskWidget
from src.features.tasks.task_manager import TaskManager
from src.features.tasks.task_integration import TaskIntegration
from src.features.statistics import PomodoroStatistics
from src.features.stats_widget import StatsWidget
from src.features.music_presets import MusicPresets
from src.features.music_controls import MusicControlsWidget
from src.features.window_resizer import WindowResizer

# ダッシュボード機能
try:
    from src.features.dashboard.dashboard_widget import DashboardWidget
    DASHBOARD_AVAILABLE = True
    logger.info("📊 ダッシュボード機能: 利用可能")
except ImportError:
    logger.warning("📊 ダッシュボード機能: 利用不可")
    DASHBOARD_AVAILABLE = False

# テーマ機能
try:
    from src.features.themes.theme_widget import ThemeWidget
    THEME_AVAILABLE = True
except ImportError:
    logger.warning("🎨 テーマ機能: 利用不可")
    THEME_AVAILABLE = False


class PomodoroTimerDualMode(QMainWindow):
    """Phase 3 + ミニマルモード統合版"""
    
    timer_finished = pyqtSignal()
    mode_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # 基本設定
        self.work_duration = 25
        self.break_duration = 5
        self.long_break_duration = 15
        self.pomodoros_until_long_break = 4
        self.time_left = 0
        self.is_running = False
        self.is_work_session = True
        self.pomodoro_count = 0
        
        # モード管理
        self.is_minimal_mode = False
        self.transparent_mode = False
        
        # ドラッグ用
        self.dragging = False
        self.drag_position = QPoint()
        
        # 設定
        self.settings = QSettings('PomodoroTimer', 'DualMode')
        
        # タイマー
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        
        # 統計
        self.statistics = PomodoroStatistics()
        
        # タスク管理
        self.task_manager = TaskManager()
        self.task_integration = TaskIntegration(self)
        # self.task_integration.pomodoroCompleted.connect(self.on_pomodoro_completed)
        
        # 音楽プリセット
        self.music_presets = MusicPresets()
        
        # ウィンドウリサイザー
        self.window_resizer = WindowResizer(self)
        
        # UI初期化
        self.init_ui()
        
        # 初期設定読み込み
        self.load_settings()
        
        # 初期表示更新
        self.update_display()
        
        logger.info("✅ Phase 3 デュアルモード版初期化完了")
    
    def init_ui(self):
        """UI初期化"""
        self.setWindowTitle('🍅 Pomodoro Timer - Phase 3 Dual Mode')
        self.setGeometry(100, 100, 450, 500)
        
        # メインウィジェット
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        
        # ミニマルモード用ウィジェット（事前作成）
        self.minimal_widget = QWidget()
        self.setup_minimal_widget()
        self.minimal_widget.hide()
        
        # フルモード用レイアウト
        self.setup_full_mode()
        
        # メニューバー
        self.setup_menu_bar()
        
        # ステータスバー
        self.statusBar().showMessage('準備完了')
    
    def setup_minimal_widget(self):
        """ミニマルモード用ウィジェット設定"""
        layout = QVBoxLayout(self.minimal_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # タイマー表示
        self.minimal_time_label = QLabel('25:00')
        self.minimal_time_label.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        self.minimal_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.minimal_time_label.setStyleSheet("color: white;")
        layout.addWidget(self.minimal_time_label)
        
        # ステータス表示
        self.minimal_status_label = QLabel('作業中 #1')
        self.minimal_status_label.setFont(QFont('Arial', 10))
        self.minimal_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.minimal_status_label.setStyleSheet("color: #cccccc;")
        layout.addWidget(self.minimal_status_label)
        
        # スタイル設定
        self.minimal_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 200);
                border-radius: 10px;
            }
        """)
    
    def setup_full_mode(self):
        """フルモード用UI設定"""
        layout = QVBoxLayout(self.main_widget)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # メインタブ
        self.setup_main_tab()
        
        # タスクタブ
        self.task_widget = TaskWidget()
        self.task_widget.taskSelected.connect(self.on_task_selected)
        self.tab_widget.addTab(self.task_widget, '📋 タスク管理')
        
        # 統計タブ
        self.stats_widget = StatsWidget()
        self.tab_widget.addTab(self.stats_widget, '📊 統計')
        
        # ダッシュボードタブ
        if DASHBOARD_AVAILABLE:
            self.dashboard = DashboardWidget()
            self.tab_widget.addTab(self.dashboard, '📈 ダッシュボード')
        
        # テーマタブ
        if THEME_AVAILABLE:
            self.theme_widget = ThemeWidget()
            self.theme_widget.themeChanged.connect(self.on_theme_changed)
            self.tab_widget.addTab(self.theme_widget, '🎨 テーマ')
    
    def setup_main_tab(self):
        """メインタブ設定"""
        main_tab = QWidget()
        layout = QVBoxLayout(main_tab)
        
        # タイマー表示
        self.timer_display = QLabel('25:00')
        self.timer_display.setFont(QFont('Arial', 48))
        self.timer_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.timer_display)
        
        # セッション情報
        self.session_info = QLabel('作業セッション #1')
        self.session_info.setFont(QFont('Arial', 16))
        self.session_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.session_info)
        
        # コントロールボタン
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton('▶️ 開始')
        self.start_button.clicked.connect(self.start_timer)
        button_layout.addWidget(self.start_button)
        
        self.pause_button = QPushButton('⏸️ 一時停止')
        self.pause_button.clicked.connect(self.pause_timer)
        self.pause_button.setEnabled(False)
        button_layout.addWidget(self.pause_button)
        
        self.reset_button = QPushButton('🔄 リセット')
        self.reset_button.clicked.connect(self.reset_timer)
        button_layout.addWidget(self.reset_button)
        
        layout.addLayout(button_layout)
        
        # 設定
        settings_group = QGroupBox('設定')
        settings_layout = QVBoxLayout()
        
        # 作業時間設定
        work_layout = QHBoxLayout()
        work_layout.addWidget(QLabel('作業時間:'))
        self.work_duration_spin = QSpinBox()
        self.work_duration_spin.setRange(1, 60)
        self.work_duration_spin.setValue(self.work_duration)
        self.work_duration_spin.setSuffix(' 分')
        self.work_duration_spin.valueChanged.connect(self.on_duration_changed)
        work_layout.addWidget(self.work_duration_spin)
        settings_layout.addLayout(work_layout)
        
        # 休憩時間設定
        break_layout = QHBoxLayout()
        break_layout.addWidget(QLabel('休憩時間:'))
        self.break_duration_spin = QSpinBox()
        self.break_duration_spin.setRange(1, 30)
        self.break_duration_spin.setValue(self.break_duration)
        self.break_duration_spin.setSuffix(' 分')
        self.break_duration_spin.valueChanged.connect(self.on_duration_changed)
        break_layout.addWidget(self.break_duration_spin)
        settings_layout.addLayout(break_layout)
        
        # 音楽コントロール
        self.music_control = MusicControlsWidget()
        settings_layout.addWidget(self.music_control)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        self.tab_widget.addTab(main_tab, '⏱️ タイマー')
    
    def setup_menu_bar(self):
        """メニューバー設定"""
        menubar = self.menuBar()
        
        # ファイルメニュー
        file_menu = menubar.addMenu('ファイル(&F)')
        
        export_action = QAction('統計をエクスポート', self)
        export_action.triggered.connect(self.export_statistics)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('終了(&X)', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 表示メニュー
        view_menu = menubar.addMenu('表示(&V)')
        
        # ミニマルモード
        self.minimal_action = QAction('ミニマルモード(&M)', self)
        self.minimal_action.setCheckable(True)
        self.minimal_action.setShortcut('Ctrl+M')
        self.minimal_action.triggered.connect(self.toggle_minimal_mode)
        view_menu.addAction(self.minimal_action)
        
        # 透明化
        self.transparent_action = QAction('透明化(&T)', self)
        self.transparent_action.setCheckable(True)
        self.transparent_action.setShortcut('Ctrl+T')
        self.transparent_action.triggered.connect(self.toggle_transparency)
        view_menu.addAction(self.transparent_action)
        
        view_menu.addSeparator()
        
        # 常に最前面
        always_on_top = QAction('常に最前面(&A)', self)
        always_on_top.setCheckable(True)
        always_on_top.triggered.connect(self.toggle_always_on_top)
        view_menu.addAction(always_on_top)
    
    def toggle_minimal_mode(self):
        """ミニマルモード切り替え"""
        self.is_minimal_mode = not self.is_minimal_mode
        
        if self.is_minimal_mode:
            self.switch_to_minimal()
        else:
            self.switch_to_full()
    
    def switch_to_minimal(self):
        """ミニマルモードへ切り替え"""
        # 現在の位置を記憶
        self.full_geometry = self.geometry()
        
        # フルモードUIを非表示
        self.main_widget.hide()
        
        # ミニマルモードUIを表示（レイアウトを使わずに直接配置）
        self.minimal_widget.setParent(self)
        self.minimal_widget.show()
        
        # メニューバーとステータスバーを非表示
        self.menuBar().hide()
        self.statusBar().hide()
        
        # ウィンドウ設定
        self.resize(200, 80)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.show()
        
        # ミニマルウィジェットを中央に配置
        self.minimal_widget.resize(180, 60)
        self.minimal_widget.move(10, 10)
        
        # マウスイベント設定
        self.minimal_widget.mousePressEvent = self.minimal_mouse_press
        self.minimal_widget.mouseMoveEvent = self.minimal_mouse_move
        self.minimal_widget.mouseReleaseEvent = self.minimal_mouse_release
        self.minimal_widget.contextMenuEvent = self.minimal_context_menu
        
        # 透明化適用
        if self.transparent_mode:
            self.apply_transparency()
        
        # 表示更新
        self.update_minimal_display()
        
        self.mode_changed.emit('minimal')
        logger.info('🔽 ミニマルモードへ切り替え')
    
    def switch_to_full(self):
        """フルモードへ切り替え"""
        try:
            # ミニマルモードUIを非表示
            self.minimal_widget.hide()
            
            # フルモードUIを表示
            self.setCentralWidget(self.main_widget)
            self.main_widget.show()
            
            # メニューバーとステータスバーを表示
            self.menuBar().show()
            self.statusBar().show()
            
            # ウィンドウ設定を戻す
            self.setWindowFlags(Qt.WindowType.Window)
            
            # 元のサイズに戻す
            if hasattr(self, 'full_geometry'):
                self.setGeometry(self.full_geometry)
            else:
                self.resize(450, 500)
            
            self.show()
            
            # 透明化解除
            self.setWindowOpacity(1.0)
            
            self.mode_changed.emit('full')
            logger.info('🔼 フルモードへ切り替え')
            
        except Exception as e:
            logger.error(f"フルモード切り替えエラー: {e}")
            import traceback
            traceback.print_exc()
            # エラー時は強制的にウィンドウをリセット
            try:
                self.setWindowFlags(Qt.WindowType.Window)
                self.resize(450, 500)
                self.show()
            except:
                pass
    
    def toggle_transparency(self):
        """透明化切り替え"""
        self.transparent_mode = not self.transparent_mode
        
        if self.transparent_mode:
            self.apply_transparency()
        else:
            self.remove_transparency()
    
    def apply_transparency(self):
        """透明化適用"""
        if self.is_minimal_mode:
            self.setWindowOpacity(0.8)
            self.minimal_widget.setStyleSheet("""
                QWidget {
                    background-color: rgba(0, 0, 0, 100);
                    border: none;
                }
            """)
        else:
            self.setWindowOpacity(0.9)
    
    def remove_transparency(self):
        """透明化解除"""
        self.setWindowOpacity(1.0)
        if self.is_minimal_mode:
            self.minimal_widget.setStyleSheet("""
                QWidget {
                    background-color: rgba(30, 30, 30, 200);
                    border-radius: 10px;
                }
            """)
    
    def toggle_always_on_top(self, checked):
        """常に最前面切り替え"""
        if checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()
    
    # タイマー機能
    def start_timer(self):
        """タイマー開始"""
        if self.time_left == 0:
            self.time_left = self.work_duration * 60 if self.is_work_session else self.break_duration * 60
        
        self.timer.start(1000)
        self.is_running = True
        
        # ボタン状態更新（フルモード時のみ）
        if not self.is_minimal_mode and hasattr(self, 'start_button'):
            try:
                self.start_button.setEnabled(False)
                self.pause_button.setEnabled(True)
            except RuntimeError:
                pass
        
        try:
            self.statusBar().showMessage('タイマー実行中...')
        except RuntimeError:
            pass
    
    def pause_timer(self):
        """タイマー一時停止"""
        self.timer.stop()
        self.is_running = False
        
        # ボタン状態更新（フルモード時のみ）
        if not self.is_minimal_mode and hasattr(self, 'start_button'):
            try:
                self.start_button.setEnabled(True)
                self.pause_button.setEnabled(False)
            except RuntimeError:
                pass
        
        try:
            self.statusBar().showMessage('一時停止中')
        except RuntimeError:
            pass
    
    def reset_timer(self):
        """タイマーリセット"""
        self.timer.stop()
        self.is_running = False
        self.time_left = 0
        
        # ボタン状態更新（フルモード時のみ）
        if not self.is_minimal_mode and hasattr(self, 'start_button'):
            try:
                self.start_button.setEnabled(True)
                self.pause_button.setEnabled(False)
            except RuntimeError:
                pass
        
        self.update_display()
        
        try:
            self.statusBar().showMessage('リセット完了')
        except RuntimeError:
            pass
    
    def update_timer(self):
        """タイマー更新"""
        self.time_left -= 1
        self.update_display()
        
        if self.time_left <= 0:
            self.on_timer_finished()
    
    def update_display(self):
        """表示更新"""
        if self.time_left == 0:
            minutes = self.work_duration if self.is_work_session else self.break_duration
            seconds = 0
        else:
            minutes = self.time_left // 60
            seconds = self.time_left % 60
        
        time_str = f'{minutes:02d}:{seconds:02d}'
        
        # フルモードの表示更新
        if not self.is_minimal_mode and hasattr(self, 'timer_display'):
            try:
                self.timer_display.setText(time_str)
                
                session_type = '作業' if self.is_work_session else '休憩'
                session_num = self.pomodoro_count + 1 if self.is_work_session else self.pomodoro_count
                self.session_info.setText(f'{session_type}セッション #{session_num}')
            except RuntimeError:
                # ウィジェットが削除されている場合は無視
                pass
        
        # ミニマルモードの表示更新
        if self.is_minimal_mode:
            self.update_minimal_display()
    
    def update_minimal_display(self):
        """ミニマルモード表示更新"""
        # 時間を直接計算
        if self.time_left == 0:
            minutes = self.work_duration if self.is_work_session else self.break_duration
            seconds = 0
        else:
            minutes = self.time_left // 60
            seconds = self.time_left % 60
        
        time_str = f'{minutes:02d}:{seconds:02d}'
        
        try:
            self.minimal_time_label.setText(time_str)
            
            session_type = '作業中' if self.is_work_session else '休憩中'
            session_num = self.pomodoro_count + 1 if self.is_work_session else self.pomodoro_count
            self.minimal_status_label.setText(f'{session_type} #{session_num}')
        except RuntimeError:
            # ウィジェットが削除されている場合は無視
            pass
    
    def on_timer_finished(self):
        """タイマー完了時の処理"""
        self.timer.stop()
        self.is_running = False
        self.time_left = 0
        
        # 音声再生
        self.play_notification_sound()
        
        # 統計記録
        session_type = 'work' if self.is_work_session else 'break'
        duration_minutes = self.work_duration if self.is_work_session else self.break_duration
        self.statistics.record_session(
            session_type=session_type,
            duration_minutes=duration_minutes,
            completed=True
        )
        
        # タスク統合
        if self.is_work_session:
            self.task_integration.complete_session('work', duration_minutes)
        
        # セッション切り替え
        if self.is_work_session:
            self.pomodoro_count += 1
            if self.pomodoro_count % self.pomodoros_until_long_break == 0:
                self.is_work_session = False
                self.time_left = self.long_break_duration * 60
                msg = '長い休憩の時間です！'
            else:
                self.is_work_session = False
                self.time_left = self.break_duration * 60
                msg = '休憩の時間です！'
        else:
            self.is_work_session = True
            self.time_left = self.work_duration * 60
            msg = '作業を再開しましょう！'
        
        # 通知
        QMessageBox.information(self, 'タイマー完了', msg)
        
        # ボタン状態更新（フルモード時のみ）
        if not self.is_minimal_mode and hasattr(self, 'start_button'):
            try:
                self.start_button.setEnabled(True)
                self.pause_button.setEnabled(False)
            except RuntimeError:
                # ウィジェットが削除されている場合は無視
                pass
        
        # 表示更新
        self.update_display()
        
        # 統計更新（フルモード時のみ）
        if not self.is_minimal_mode:
            try:
                # ダッシュボードのみ更新（StatsWidgetは一時的に無効化）
                if DASHBOARD_AVAILABLE and hasattr(self, 'dashboard'):
                    self.dashboard.update_stats()
            except (RuntimeError, AttributeError) as e:
                # ウィジェットが削除されている場合やメソッドが存在しない場合は無視
                logger.warning(f"統計更新エラー: {e}")
                pass
        
        self.timer_finished.emit()
    
    def play_notification_sound(self):
        """通知音再生"""
        try:
            if PYGAME_AVAILABLE:
                pygame.mixer.music.load('assets/sounds/bell.mp3')
                pygame.mixer.music.play()
            else:
                # QtMultimedia使用
                player = QMediaPlayer()
                audio_output = QAudioOutput()
                player.setAudioOutput(audio_output)
                player.setSource(QUrl.fromLocalFile('assets/sounds/bell.mp3'))
                player.play()
        except Exception as e:
            logger.warning(f'音声再生エラー: {e}')
    
    # ミニマルモード用イベント
    def minimal_mouse_press(self, event: QMouseEvent):
        """マウス押下（ミニマル）"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def minimal_mouse_move(self, event: QMouseEvent):
        """マウス移動（ミニマル）"""
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
    
    def minimal_mouse_release(self, event: QMouseEvent):
        """マウスリリース（ミニマル）"""
        self.dragging = False
    
    def minimal_context_menu(self, event):
        """右クリックメニュー（ミニマル）"""
        menu = QMenu(self)
        
        # フルモードへ
        full_action = QAction('フルモードへ', self)
        full_action.triggered.connect(self.toggle_minimal_mode)
        menu.addAction(full_action)
        
        menu.addSeparator()
        
        # タイマー制御
        if self.is_running:
            pause_action = QAction('一時停止', self)
            pause_action.triggered.connect(self.pause_timer)
            menu.addAction(pause_action)
        else:
            start_action = QAction('開始', self)
            start_action.triggered.connect(self.start_timer)
            menu.addAction(start_action)
        
        reset_action = QAction('リセット', self)
        reset_action.triggered.connect(self.reset_timer)
        menu.addAction(reset_action)
        
        menu.exec(event.globalPos())
    
    # その他の機能
    def on_duration_changed(self):
        """時間設定変更"""
        self.work_duration = self.work_duration_spin.value()
        self.break_duration = self.break_duration_spin.value()
        
        if not self.is_running and self.time_left == 0:
            self.update_display()
    
    def on_task_selected(self, task_id):
        """タスク選択"""
        self.task_integration.set_current_task(task_id)
        logger.info(f'タスク選択: {task_id}')
    
    def on_pomodoro_completed(self, task_id):
        """ポモドーロ完了"""
        logger.info(f'タスク {task_id} のポモドーロ完了')
    
    def on_theme_changed(self, theme_name):
        """テーマ変更"""
        if THEME_AVAILABLE:
            theme_manager = self.theme_widget.get_theme_manager()
            stylesheet = theme_manager.get_stylesheet()
            self.setStyleSheet(stylesheet)
    
    def export_statistics(self):
        """統計エクスポート"""
        # 実装省略
        QMessageBox.information(self, '情報', '統計のエクスポート機能は準備中です')
    
    def load_settings(self):
        """設定読み込み"""
        self.work_duration = self.settings.value('work_duration', 25, type=int)
        self.break_duration = self.settings.value('break_duration', 5, type=int)
        self.long_break_duration = self.settings.value('long_break_duration', 15, type=int)
        
        # UIに反映
        if hasattr(self, 'work_duration_spin'):
            self.work_duration_spin.setValue(self.work_duration)
            self.break_duration_spin.setValue(self.break_duration)
    
    def save_settings(self):
        """設定保存"""
        self.settings.setValue('work_duration', self.work_duration)
        self.settings.setValue('break_duration', self.break_duration)
        self.settings.setValue('long_break_duration', self.long_break_duration)
    
    def closeEvent(self, event):
        """終了イベント"""
        self.save_settings()
        event.accept()


def main():
    """メイン関数"""
    logger.info('🚀 Phase 3 デュアルモード版アプリケーション開始')
    
    app = QApplication(sys.argv)
    app.setApplicationName('Pomodoro Timer - Dual Mode')
    
    window = PomodoroTimerDualMode()
    window.show()
    
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())