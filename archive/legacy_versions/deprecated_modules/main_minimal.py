#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pomodoro Timer - Minimal Mode
FavDesktopClock風のミニマルなタイマー表示
"""

import sys
import os
from pathlib import Path

# プロジェクトパス追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, pyqtSignal, QObject
import logging

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# コンポーネントインポート
try:
    from views.minimal_timer_window import MinimalTimerWindow, BreakWindow
    from controllers.timer_controller import TimerController
    from models.timer_model import TimerModel, TimerState, SessionType
    from views.main_window import MainWindow  # 設定画面として使用
except ImportError:
    # 直接インポート
    from src.views.minimal_timer_window import MinimalTimerWindow, BreakWindow
    from src.controllers.timer_controller import TimerController
    from src.models.timer_model import TimerModel, TimerState, SessionType
    from src.views.main_window import MainWindow  # 設定画面として使用

# 音声システム（オプション）
AUDIO_AVAILABLE = False
try:
    import pygame.mixer
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
    logger.info("🔊 音声システム: 利用可能")
except:
    logger.info("🔇 音声システム: 利用不可（サイレントモード）")


class MinimalPomodoroApp(QObject):
    """ミニマルポモドーロアプリケーション"""
    
    def __init__(self):
        super().__init__()
        
        # モデルとコントローラー
        self.timer_model = TimerModel()
        self.timer_controller = TimerController(self.timer_model)
        
        # ビュー
        self.minimal_window = MinimalTimerWindow(self.timer_controller)
        self.break_window = BreakWindow()
        self.settings_window = None  # 設定画面（必要時に作成）
        
        # 接続
        self.setup_connections()
        
        # 初期表示
        self.minimal_window.show()
        
        # タイマー監視
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.check_session_change)
        self.monitor_timer.start(100)  # 0.1秒ごとチェック
        
        # 現在のセッション状態
        self.current_session = "work"
        
    def setup_connections(self):
        """シグナル接続"""
        # ミニマルウィンドウ
        self.minimal_window.settingsRequested.connect(self.show_settings)
        self.minimal_window.breakStarted.connect(self.on_break_started)
        self.minimal_window.workStarted.connect(self.on_work_started)
        
        # 休憩ウィンドウ
        self.break_window.backToWork.connect(self.skip_break)
        
        # タイマーコントローラー
        self.timer_controller.state_changed.connect(self.on_timer_state_changed)
        self.timer_controller.session_completed.connect(self.on_session_completed)
        
    def check_session_change(self):
        """セッション変更をチェック"""
        if self.timer_controller.is_running():
            current_type = self.timer_controller.current_session_type
            
            # セッションが変わった場合
            if current_type != self.current_session:
                self.current_session = current_type
                
                if current_type == "break":
                    self.switch_to_break_mode()
                else:
                    self.switch_to_work_mode()
                    
        # 休憩ウィンドウのタイマー更新
        if self.break_window.isVisible() and self.timer_controller.is_running():
            minutes = self.timer_controller.remaining_time // 60
            seconds = self.timer_controller.remaining_time % 60
            self.break_window.update_timer(minutes, seconds)
            
    def switch_to_break_mode(self):
        """休憩モードに切り替え"""
        logger.info("🌙 休憩モードに切り替え")
        
        # ミニマルウィンドウを隠す
        self.minimal_window.hide()
        
        # 休憩ウィンドウを表示
        self.break_window.show()
        
        # 中央に配置
        if QApplication.primaryScreen():
            screen_center = QApplication.primaryScreen().geometry().center()
            self.break_window.move(
                screen_center.x() - self.break_window.width() // 2,
                screen_center.y() - self.break_window.height() // 2
            )
            
        # 音声通知
        if AUDIO_AVAILABLE:
            self.play_break_sound()
            
    def switch_to_work_mode(self):
        """作業モードに切り替え"""
        logger.info("💼 作業モードに切り替え")
        
        # 休憩ウィンドウを隠す
        self.break_window.hide()
        
        # ミニマルウィンドウを表示
        self.minimal_window.show()
        
        # 音声通知
        if AUDIO_AVAILABLE:
            self.play_work_sound()
            
    def show_settings(self):
        """設定画面表示"""
        if not self.settings_window:
            self.settings_window = MainWindow()
            self.settings_window.timer_controller = self.timer_controller
            
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()
        
    def skip_break(self):
        """休憩をスキップ"""
        reply = QMessageBox.question(
            self.break_window,
            "確認",
            "休憩をスキップして作業を開始しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.timer_controller.skip_break()
            self.switch_to_work_mode()
            
    def on_break_started(self):
        """休憩開始シグナル受信"""
        self.switch_to_break_mode()
        
    def on_work_started(self):
        """作業開始シグナル受信"""
        self.switch_to_work_mode()
        
    def on_timer_state_changed(self, state):
        """タイマー状態変更"""
        logger.info(f"タイマー状態変更: {state}")
        
    def on_session_completed(self):
        """セッション完了"""
        logger.info("セッション完了")
        
    def play_break_sound(self):
        """休憩開始音"""
        try:
            # 簡単なビープ音を再生
            pass
        except:
            pass
            
    def play_work_sound(self):
        """作業開始音"""
        try:
            # 簡単なビープ音を再生
            pass
        except:
            pass


def main():
    """メイン関数"""
    app = QApplication(sys.argv)
    app.setApplicationName("Minimal Pomodoro Timer")
    
    # スタイル設定
    app.setStyle("Fusion")
    
    # アプリケーション起動
    pomodoro_app = MinimalPomodoroApp()
    
    # 初期位置（画面右上）
    if QApplication.primaryScreen():
        screen = QApplication.primaryScreen().geometry()
        pomodoro_app.minimal_window.move(
            screen.width() - pomodoro_app.minimal_window.width() - 20,
            20
        )
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()