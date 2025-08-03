#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pomodoro Timer App ビルドスクリプト

このスクリプトはPyInstallerを使用してアプリケーションをパッケージ化します。
開発者が簡単に修正・再ビルドできるよう設計されています。
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import argparse

def clean_build_dirs():
    """ビルドディレクトリをクリーンアップ"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            print(f"🧹 {dir_name} ディレクトリを削除中...")
            shutil.rmtree(dir_name)
    
    # .specファイルも削除（指定されたものは除く）
    for spec_file in Path('.').glob('*.spec'):
        if spec_file.name not in ['pomodoro_timer.spec', 'pomodoro_timer_onefile.spec']:
            print(f"🧹 {spec_file} を削除中...")
            spec_file.unlink()

def check_requirements():
    """必要なパッケージがインストールされているか確認"""
    required_packages = {
        'PyInstaller': 'PyInstaller',
        'PyQt6': 'PyQt6.QtWidgets',
        'pygame': 'pygame',
        'matplotlib': 'matplotlib'
    }
    missing_packages = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("❌ 以下のパッケージがインストールされていません:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\n以下のコマンドでインストールしてください:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def create_resources_dir():
    """リソースディレクトリを作成（将来の拡張用）"""
    resources_dir = Path('resources')
    if not resources_dir.exists():
        resources_dir.mkdir()
        print("📁 resources ディレクトリを作成しました")
        
        # READMEファイルを作成
        readme_content = """# Resources Directory

このディレクトリには以下のリソースを配置できます：

- icon.ico : Windowsアプリケーションアイコン
- icon.icns : macOSアプリケーションアイコン
- icon.png : Linuxアプリケーションアイコン
- sounds/ : カスタムサウンドファイル
- images/ : UIで使用する画像ファイル

リソースを追加した後は、.specファイルを更新してビルドに含めてください。
"""
        (resources_dir / 'README.md').write_text(readme_content, encoding='utf-8')

def find_pyinstaller():
    """PyInstallerの実行パスを取得"""
    # まず通常のPATHから探す
    try:
        result = subprocess.run(['pyinstaller', '--version'], 
                              capture_output=True, text=True, check=True)
        return 'pyinstaller'
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Pythonモジュールとして実行を試す
    try:
        result = subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'], 
                              capture_output=True, text=True, check=True)
        return [sys.executable, '-m', 'PyInstaller']
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Windowsの場合、ユーザーディレクトリのScriptsを確認
    if sys.platform == 'win32':
        import os
        user_scripts = Path(os.path.expanduser('~')) / 'AppData/Roaming/Python' / f'Python{sys.version_info.major}{sys.version_info.minor}' / 'Scripts' / 'pyinstaller.exe'
        if user_scripts.exists():
            return str(user_scripts)
    
    return None

def build_app(mode='dir', debug=False):
    """アプリケーションをビルド"""
    if mode == 'dir':
        spec_file = 'pomodoro_timer.spec'
        print("📦 ディレクトリ形式でビルドします（開発・デバッグ向け）")
    else:
        spec_file = 'pomodoro_timer_onefile.spec'
        print("📦 単一ファイル形式でビルドします（配布向け）")
    
    # PyInstallerのパスを取得
    pyinstaller_cmd = find_pyinstaller()
    if pyinstaller_cmd is None:
        print("❌ PyInstallerが見つかりません")
        print("以下を試してください:")
        print("1. pip install PyInstaller")
        print("2. PATHにPyInstallerを追加")
        print("3. 仮想環境をアクティベート")
        return False
    
    # PyInstallerコマンドを構築
    if isinstance(pyinstaller_cmd, list):
        cmd = pyinstaller_cmd + ['--clean']
    else:
        cmd = [pyinstaller_cmd, '--clean']
    
    if debug:
        cmd.append('--debug=all')
        print("🐛 デバッグモードでビルドします")
    
    cmd.append(spec_file)
    
    print(f"🔨 ビルドコマンド: {' '.join(cmd)}")
    
    # ビルド実行
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ ビルドが成功しました！")
        
        if mode == 'dir':
            print(f"\n実行ファイル: dist/PomodoroTimer/PomodoroTimer{'.exe' if sys.platform == 'win32' else ''}")
        else:
            print(f"\n実行ファイル: dist/PomodoroTimer{'.exe' if sys.platform == 'win32' else ''}")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ ビルドエラーが発生しました: {e}")
        return False
    
    return True

def post_build_setup():
    """ビルド後の設定"""
    # dataディレクトリの確認
    if Path('dist/PomodoroTimer/data').exists():
        print("✅ dataディレクトリが正しくコピーされました")
    else:
        # dataディレクトリを手動でコピー
        print("📁 dataディレクトリをコピー中...")
        if Path('data').exists():
            shutil.copytree('data', 'dist/PomodoroTimer/data', dirs_exist_ok=True)

def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description='Pomodoro Timer App ビルドスクリプト')
    parser.add_argument('--mode', choices=['dir', 'onefile'], default='dir',
                        help='ビルドモード: dir=ディレクトリ形式（デフォルト）, onefile=単一ファイル')
    parser.add_argument('--clean', action='store_true',
                        help='ビルド前にクリーンアップを実行')
    parser.add_argument('--debug', action='store_true',
                        help='デバッグモードでビルド')
    
    args = parser.parse_args()
    
    print("🚀 Pomodoro Timer App ビルドツール")
    print("=" * 50)
    
    # クリーンアップ
    if args.clean:
        clean_build_dirs()
    
    # 必要パッケージの確認
    print("📋 必要パッケージを確認中...")
    if not check_requirements():
        return 1
    print("✅ 全ての必要パッケージがインストールされています")
    
    # リソースディレクトリの作成
    create_resources_dir()
    
    # ビルド実行
    print("\n🔨 ビルドを開始します...")
    if build_app(mode=args.mode, debug=args.debug):
        if args.mode == 'dir':
            post_build_setup()
        
        print("\n🎉 ビルドが完了しました！")
        print("\n💡 ヒント:")
        print("  - 設定ファイルは data/ ディレクトリに保存されます")
        print("  - アイコンを追加する場合は resources/icon.ico を作成してください")
        print("  - カスタマイズする場合は .spec ファイルを編集してください")
        
        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())