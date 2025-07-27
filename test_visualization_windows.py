#!/usr/bin/env python3
"""
可視化ウィンドウテストスクリプト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from pomodoro_phase3_final_integrated_simple_break import PomodoroApp
import time

def test_visualization_windows():
    """可視化ウィンドウのテスト"""
    
    app = QApplication(sys.argv)
    
    # メインアプリ作成
    pomodoro_app = PomodoroApp()
    pomodoro_app.show()
    
    # 少し待って初期化完了
    QApplication.processEvents()
    time.sleep(2)
    
    print("🧪 可視化ウィンドウテスト開始")
    
    # 統計タブに切り替え
    if hasattr(pomodoro_app, 'tab_widget'):
        for i in range(pomodoro_app.tab_widget.count()):
            if '統計' in pomodoro_app.tab_widget.tabText(i):
                pomodoro_app.tab_widget.setCurrentIndex(i)
                print(f"📊 統計タブに切り替えました (インデックス: {i})")
                break
    
    QApplication.processEvents()
    time.sleep(1)
    
    # 可視化システムが利用可能かチェック
    if hasattr(pomodoro_app, 'visualization') and pomodoro_app.visualization:
        print("✅ 可視化システム利用可能")
        
        # テスト用チャート生成
        try:
            print("📈 生産性タイムライン生成テスト...")
            canvas1 = pomodoro_app.visualization.create_productivity_timeline()
            print("✅ 生産性タイムライン生成完了")
            
            print("🎯 フォーカスヒートマップ生成テスト...")
            canvas2 = pomodoro_app.visualization.create_focus_heatmap()
            print("✅ フォーカスヒートマップ生成完了")
            
            print("🏆 セッションパフォーマンス分析テスト...")
            canvas3 = pomodoro_app.visualization.create_session_performance_chart()
            print("✅ セッションパフォーマンス分析完了")
            
        except Exception as e:
            print(f"❌ チャート生成エラー: {e}")
    else:
        print("❌ 可視化システムが利用できません")
    
    print("🧪 テスト完了 - ウィンドウが別途表示されているか確認してください")
    print("💡 ウィンドウを閉じるには各チャートウィンドウの '❌ 閉じる' ボタンを使用してください")
    
    # アプリケーション実行
    sys.exit(app.exec())

if __name__ == "__main__":
    test_visualization_windows()