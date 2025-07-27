#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ミニマルモード デモ
短い時間でテスト（作業30秒、休憩10秒）
"""

import sys
import os
from pathlib import Path

# プロジェクトパス追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import logging

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# メインアプリインポート
from main_minimal import MinimalPomodoroApp

def main():
    """デモ実行"""
    app = QApplication(sys.argv)
    app.setApplicationName("Minimal Timer Demo")
    
    # アプリケーション起動
    pomodoro_app = MinimalPomodoroApp()
    
    # デモ用に時間を短縮
    pomodoro_app.timer_model.work_duration = 30  # 30秒
    pomodoro_app.timer_model.short_break_duration = 10  # 10秒
    
    # 初期位置（画面右上）
    if QApplication.primaryScreen():
        screen = QApplication.primaryScreen().geometry()
        pomodoro_app.minimal_window.move(
            screen.width() - pomodoro_app.minimal_window.width() - 20,
            20
        )
    
    # 自動開始（3秒後）
    QTimer.singleShot(3000, lambda: start_demo(pomodoro_app))
    
    logger.info("🚀 ミニマルモードデモ開始")
    logger.info("📍 画面右上に小さなタイマーが表示されます")
    logger.info("⏱️  30秒作業 → 10秒休憩のサイクル")
    logger.info("🖱️  右クリックでメニュー、ダブルクリックで設定")
    
    sys.exit(app.exec())

def start_demo(app):
    """デモ開始"""
    logger.info("▶️  タイマー開始")
    app.timer_controller.start_timer()
    
    # 時刻表示も有効化
    app.minimal_window.toggle_time_display()

if __name__ == "__main__":
    main()