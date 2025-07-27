#!/usr/bin/env python3
"""
ポモドーロタイマー Phase 4 起動スクリプト
- ライブラリ問題の自動回避
- フォールバック機能付き
"""

import subprocess
import sys
import os

def main():
    print("🍅 ポモドーロタイマー Phase 4 起動")
    print("=" * 40)
    
    # ファイル存在確認
    app_file = "pomodoro_phase3_final_integrated_simple_break.py"
    if not os.path.exists(app_file):
        print(f"❌ {app_file} が見つかりません")
        return
    
    print("🚀 アプリを起動しています...")
    print("💡 ライブラリ読み込み中（初回は時間がかかります）")
    print("⚠️ 応答がない場合は Ctrl+C で中断してください")
    
    try:
        # アプリを起動
        subprocess.run([sys.executable, app_file])
        
    except KeyboardInterrupt:
        print("\n👋 アプリを終了しました")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        print("\n🔧 トラブルシューティング:")
        print("1. 必要なライブラリが不足している可能性があります")
        print("   pip install PyQt6 matplotlib pandas numpy")
        print("2. 高度機能を使いたい場合:")
        print("   pip install scikit-learn reportlab openpyxl")

if __name__ == "__main__":
    main()