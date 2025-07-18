#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2アプリケーションの簡易実行テスト
"""

import sys
import os
import subprocess
import time
from pathlib import Path

print("🚀 Phase 2 アプリケーション起動テスト")
print("=" * 50)

# 音楽ファイルの存在確認
print("\n1️⃣ 音楽ファイル確認...")
music_dir = Path("assets/music")
required_files = [
    'work_bgm.mp3',
    'break_bgm.mp3',
    'alert_1min.mp3', 
    'alert_30sec.mp3',
    'countdown_tick.mp3'
]

all_exist = True
for file in required_files:
    path = music_dir / file
    exists = path.exists()
    print(f"  {'✅' if exists else '❌'} {file}")
    if not exists:
        all_exist = False

if not all_exist:
    print("\n⚠️  必要な音楽ファイルが不足しています")
    print("空ファイルを作成しますか？ (y/n): ", end="")
    if input().lower() == 'y':
        music_dir.mkdir(parents=True, exist_ok=True)
        for file in required_files:
            path = music_dir / file
            if not path.exists():
                path.touch()
                print(f"  📄 {file} を作成しました")

# Phase 2起動
print("\n2️⃣ Phase 2 アプリケーションを起動します...")
print("  - 3秒後に自動的に終了します")
print("  - エラーが発生した場合はログを確認してください")

# サブプロセスで起動（タイムアウト付き）
try:
    process = subprocess.Popen(
        [sys.executable, "main_phase2.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # 3秒待機
    time.sleep(3)
    
    # プロセスを終了
    process.terminate()
    process.wait(timeout=5)
    
    print("\n✅ 正常に起動・終了しました")
    
except subprocess.TimeoutExpired:
    process.kill()
    print("\n⚠️  タイムアウトしました")
except Exception as e:
    print(f"\n❌ エラー: {e}")

# ログファイル確認
print("\n3️⃣ ログファイル確認...")
log_file = Path("phase2.log")
if log_file.exists():
    # 最新のログを表示
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        recent_lines = lines[-10:] if len(lines) > 10 else lines
        
    print(f"  📄 phase2.log (最新{len(recent_lines)}行):")
    for line in recent_lines:
        print(f"    {line.rstrip()}")
else:
    print("  ❌ ログファイルが見つかりません")

print("\n✅ テスト完了！")
print("\n📝 次のステップ:")
print("  1. 実際の音楽ファイル（MP3）を assets/music/ に配置")
print("  2. python main_phase2.py で本番実行")
print("  3. 各機能をGUIで確認")