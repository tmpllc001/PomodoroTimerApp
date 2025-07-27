#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音楽機能統合テスト
MockMusicPlayerを使用したPhase 2音楽機能のテスト
"""

import sys
import time
import logging
from pathlib import Path

# プロジェクトパス追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(message)s',
    datefmt='%H:%M:%S'
)

print("🎵 音楽機能統合テスト")
print("=" * 50)

# 音楽ファイルの準備
print("\n1️⃣ 音楽ファイルの準備...")
music_dir = Path("assets/music")
music_dir.mkdir(parents=True, exist_ok=True)

music_files = [
    'work_bgm.mp3',
    'break_bgm.mp3', 
    'alert_1min.mp3',
    'alert_30sec.mp3',
    'countdown_tick.mp3'
]

for file in music_files:
    file_path = music_dir / file
    if not file_path.exists():
        file_path.touch()
        print(f"  ✅ {file} 作成")
    else:
        print(f"  ✅ {file} 存在")

# MusicPresetsSimpleのインポートとテスト
print("\n2️⃣ MusicPresetsSimple インポート...")
try:
    from features.music_presets import MusicPresetsSimple
    music = MusicPresetsSimple()
    print("  ✅ インポート成功")
except Exception as e:
    print(f"  ❌ インポート失敗: {e}")
    sys.exit(1)

# 基本機能テスト
print("\n3️⃣ 基本機能テスト...")

print("\n  📍 作業モード設定")
music.set_preset('work')
time.sleep(0.5)

print("\n  📍 音楽再生開始")
music.play()
time.sleep(2)

print("\n  📍 音量調整（30%）")
music.set_volume(0.3)
time.sleep(1)

print("\n  📍 アラート音テスト")
music.play_alert('1min')
time.sleep(0.5)
music.play_alert('30sec')
time.sleep(0.5)
music.play_alert('5sec')
time.sleep(0.5)

print("\n  📍 一時停止")
music.pause()
time.sleep(1)

print("\n  📍 休憩モードに切り替え")
music.set_preset('break')
time.sleep(1)

print("\n  📍 再生再開")
music.play()
time.sleep(2)

print("\n  📍 停止")
music.stop()

print("\n  📍 音楽機能無効化")
music.enable(False)
time.sleep(0.5)

print("\n  📍 音楽機能有効化")
music.enable(True)

# セッションタイプ確認
print("\n4️⃣ プリセット情報確認...")
presets = music.get_available_presets()
for key, name in presets.items():
    info = music.get_preset_info(key)
    print(f"  - {key}: {name}")
    if 'file' in info:
        print(f"    ファイル: {info['file']}")
        print(f"    存在: {'✅' if info.get('exists', False) else '❌'}")

# ステータス確認
print("\n5️⃣ 最終ステータス...")
status = music.get_session_status()
print(f"  - アクティブ: {status['is_active']}")
print(f"  - 再生中: {status['is_playing']}")
print(f"  - 音量: {int(status['volume'] * 100)}%")
print(f"  - 音楽有効: {status['music_enabled']}")

print("\n✅ 音楽機能統合テスト完了！")
print("\n📝 備考:")
print("  - MockMusicPlayerを使用しているため、実際の音は出ません")
print("  - ログで動作を確認できます")
print("  - 実際の音楽再生にはpygameまたは他の音楽ライブラリが必要です")