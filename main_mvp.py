#!/usr/bin/env python3
"""
ポモドーロタイマー MVP版
15分で統合完成版
"""

import sys
import os
from pathlib import Path

# プロジェクトパス追加
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

def main():
    """MVP メイン実行."""
    print("🚀 ポモドーロタイマー MVP 起動中...")
    
    # QApplication作成
    app = QApplication(sys.argv)
    app.setApplicationName("Pomodoro Timer MVP")
    app.setApplicationVersion("0.1.0")
    
    try:
        # メインウィンドウ読み込み
        from src.views.main_window_template import MainWindow
        
        # ウィンドウ作成・表示
        window = MainWindow()
        window.show()
        
        print("✅ MVP起動完了！")
        print("⏰ ポモドーロタイマーを開始してください")
        
        # アプリ実行
        return app.exec()
        
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        print("PyQt6がインストールされていない可能性があります")
        print("pip install PyQt6 を実行してください")
        return 1
        
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    # WSL/Linux環境での表示設定
    if 'DISPLAY' not in os.environ:
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        print("⚠️  GUI環境が検出されません。オフスクリーンモードで実行します")
    
    sys.exit(main())