#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal Pomodoro Timer - Demo Version (Enhanced)
30秒作業、10秒休憩の短縮版デモ（透明化・カスタマイズ対応）
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# スタンドアロン版をインポート
from minimal_timer_standalone import MinimalTimerWindow


def main():
    """デモ実行"""
    app = QApplication(sys.argv)
    app.setApplicationName("Minimal Timer Demo")
    
    # メインウィンドウ
    window = MinimalTimerWindow()
    
    # デモ用に時間を短縮
    window.model.work_duration = 30    # 30秒作業
    window.model.break_duration = 10   # 10秒休憩
    window.model.remaining_time = 30
    
    # 時刻表示を有効化
    window.toggle_time()
    
    window.show()
    
    # 画面右上に配置
    if QApplication.primaryScreen():
        screen = QApplication.primaryScreen().geometry()
        window.move(screen.width() - window.width() - 20, 20)
    
    # 3秒後に自動開始
    QTimer.singleShot(3000, window.controller.start)
    
    print("=" * 60)
    print("🕐 ミニマルポモドーロタイマー デモ (Enhanced版)")
    print("=" * 60)
    print("📍 画面右上に小さなタイマーが表示されます")
    print("⏱️  30秒作業 → 10秒休憩のサイクル")
    print("🖱️  右クリック：メニュー表示（位置・色・設定変更可能）")
    print("👻 左クリック：透過モード（下のアプリを操作可能）")
    print("🎯 Alt+ドラッグ：ウィンドウ移動")
    print("💾 設定は自動保存されます")
    print("📌 3秒後に自動的にタイマーが開始されます")
    print("=" * 60)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()