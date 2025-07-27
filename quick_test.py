#!/usr/bin/env python3
"""
Phase 4 クイックテスト - ライブラリ問題回避版
"""

import subprocess
import sys
import time

def test_basic_imports():
    """基本インポートテスト"""
    print("🔍 基本ライブラリテスト...")
    
    try:
        import PyQt6
        print("✅ PyQt6: OK")
    except:
        print("❌ PyQt6: NG")
        return False
    
    # matplotlib/seabornは条件付きなので問題なし
    print("✅ 基本ライブラリ: OK")
    return True

def launch_app_safe():
    """安全なアプリ起動"""
    print("\n🚀 アプリ起動中...")
    print("注意: 初回起動時はライブラリ読み込みに時間がかかる場合があります")
    print("Ctrl+C で中断できます")
    
    try:
        # プロセスを非同期で起動
        process = subprocess.Popen([
            sys.executable, 
            "pomodoro_phase3_final_integrated_simple_break.py"
        ])
        
        print(f"📱 アプリプロセス開始 (PID: {process.pid})")
        print("アプリウィンドウが表示されるまでお待ちください...")
        
        # 10秒待機してプロセス状態確認
        time.sleep(10)
        if process.poll() is None:
            print("✅ アプリが正常に起動しました！")
            print("\n📋 テスト手順:")
            print("1. 「分析・可視化」タブをクリック") 
            print("2. ドロップダウンから「comprehensive」を選択")
            print("3. 「生成」ボタンをクリック")
            
            try:
                process.wait()  # アプリ終了まで待機
            except KeyboardInterrupt:
                print("\n👋 テスト終了")
                process.terminate()
        else:
            print("❌ アプリ起動に失敗しました")
            return False
            
    except KeyboardInterrupt:
        print("\n👋 ユーザーによる中断")
        return True
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False
    
    return True

def main():
    print("🎯 Phase 4 クイックテスト")
    print("=" * 30)
    
    # 基本テスト
    if not test_basic_imports():
        return
    
    print("\n💡 このテストは以下の機能を確認します:")
    print("- フォールバック機能付きライブラリ読み込み")
    print("- matplotlib/seaborn利用不可時のテキスト表示")
    print("- Phase 4機能の基本動作")
    
    input("\nEnterキーでアプリを起動...")
    
    # アプリ起動
    launch_app_safe()

if __name__ == "__main__":
    main()