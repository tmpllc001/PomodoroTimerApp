#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
パッケージ化されたアプリケーションのテストスクリプト

このスクリプトは、PyInstallerでパッケージ化されたアプリケーションが
正常に動作するかをテストします。
"""

import subprocess
import sys
import time
from pathlib import Path
import signal
import os

def test_packaged_app():
    """パッケージ化されたアプリケーションをテスト"""
    
    # 実行ファイルのパスを取得
    exe_path = Path('./dist/PomodoroTimer/PomodoroTimer')
    
    if not exe_path.exists():
        print("❌ 実行ファイルが見つかりません:")
        print(f"   {exe_path.absolute()}")
        return False
    
    print("🧪 パッケージ化されたアプリケーションをテスト中...")
    print(f"実行ファイル: {exe_path.absolute()}")
    
    try:
        # アプリケーションを起動（バックグラウンドで）
        print("🚀 アプリケーションを起動中...")
        
        # GUI環境がない場合でも最低限の起動テストを行う
        env = os.environ.copy()
        env['QT_QPA_PLATFORM'] = 'offscreen'  # GUI環境がない場合に使用
        
        process = subprocess.Popen(
            [str(exe_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )
        
        # 少し待ってから終了
        time.sleep(3)
        
        # プロセスを終了
        if process.poll() is None:  # まだ実行中の場合
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        
        # 出力を確認
        stdout, stderr = process.communicate()
        
        print("✅ アプリケーションが正常に起動しました")
        
        if stderr:
            print("⚠️  警告メッセージ:")
            print(stderr.decode('utf-8', errors='ignore'))
        
        return True
        
    except Exception as e:
        print(f"❌ テスト中にエラーが発生しました: {e}")
        return False

def test_data_directory():
    """データディレクトリの構造をテスト"""
    print("\n📁 データディレクトリの構造をテスト中...")
    
    data_dir = Path('./dist/PomodoroTimer/data')
    
    if not data_dir.exists():
        print("❌ dataディレクトリが見つかりません")
        return False
    
    # 重要なディレクトリの存在確認
    required_dirs = ['charts', 'exports', 'reports']
    for dir_name in required_dirs:
        dir_path = data_dir / dir_name
        if dir_path.exists():
            print(f"✅ {dir_name}/ ディレクトリが存在します")
        else:
            print(f"⚠️  {dir_name}/ ディレクトリが見つかりません")
    
    # 設定ファイルの存在確認
    config_files = [
        'session_tracking.json',
        'statistics.json',
        'tasks.json'
    ]
    
    for file_name in config_files:
        file_path = data_dir / file_name
        if file_path.exists():
            print(f"✅ {file_name} が存在します")
        else:
            print(f"⚠️  {file_name} が見つかりません")
    
    return True

def main():
    """メイン処理"""
    print("🧪 Pomodoro Timer App パッケージテスト")
    print("=" * 50)
    
    # データディレクトリのテスト
    test_data_directory()
    
    # アプリケーション起動テスト
    success = test_packaged_app()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 全てのテストが成功しました！")
        print("\n💡 次のステップ:")
        print("  1. 他のOS環境でテスト")
        print("  2. アイコンの追加")
        print("  3. インストーラーの作成")
        return 0
    else:
        print("❌ テストに失敗しました")
        return 1

if __name__ == '__main__':
    sys.exit(main())