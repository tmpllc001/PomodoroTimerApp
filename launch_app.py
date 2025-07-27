#!/usr/bin/env python3
"""
ポモドーロタイマー Phase 4 起動スクリプト
依存ライブラリがなくても動作するように最適化済み
"""

import subprocess
import sys
from pathlib import Path

def check_dependencies():
    """依存ライブラリの確認"""
    print("🔍 依存ライブラリを確認中...")
    
    missing_libs = []
    
    # 必須ライブラリ
    required = ['PyQt6', 'matplotlib', 'pandas', 'numpy']
    for lib in required:
        try:
            __import__(lib.lower() if lib != 'PyQt6' else 'PyQt6')
            print(f"  ✅ {lib}: インストール済み")
        except ImportError:
            print(f"  ❌ {lib}: 未インストール")
            missing_libs.append(lib)
    
    # オプションライブラリ
    optional = ['sklearn', 'reportlab', 'openpyxl']
    for lib in optional:
        try:
            __import__(lib)
            print(f"  ✅ {lib}: インストール済み (Phase 4高度機能利用可能)")
        except ImportError:
            print(f"  ⚠️ {lib}: 未インストール (基本機能のみ)")
    
    if missing_libs:
        print(f"\n❌ 必須ライブラリが不足しています: {', '.join(missing_libs)}")
        print("以下のコマンドでインストールしてください:")
        print(f"pip install {' '.join(missing_libs)}")
        return False
    
    print("\n✅ 基本動作に必要なライブラリは揃っています！")
    return True

def launch_app():
    """アプリケーションの起動"""
    print("\n🚀 ポモドーロタイマー Phase 4 を起動中...")
    
    app_path = Path("pomodoro_phase3_final_integrated_simple_break.py")
    if not app_path.exists():
        print("❌ アプリケーションファイルが見つかりません")
        return False
    
    try:
        # アプリケーションを起動
        subprocess.run([sys.executable, str(app_path)], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 起動エラー: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 ユーザーによる終了")
        return True

def main():
    print("🍅 ポモドーロタイマー Phase 4 起動スクリプト")
    print("=" * 50)
    
    # 依存関係チェック
    if not check_dependencies():
        return
    
    # 使い方の案内
    print("""
📋 Phase 4 機能の使い方:
1. 基本統計: 「統計」タブ
2. 高度分析: 「分析・可視化」タブ  
3. AI予測: 「AI予測・エクスポート」タブ

💡 ヒント:
- テストデータが30セッション分生成済みです
- 分析・可視化タブでドロップダウンから「comprehensive」を選択
- AI予測機能は基本版でも利用可能

""")
    
    input("Enterキーを押してアプリを起動...")
    
    # アプリ起動
    launch_app()

if __name__ == "__main__":
    main()