#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2 機能の簡単なテスト
"""

import sys
from pathlib import Path

# プロジェクトパス追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

print("🧪 Phase 2 機能テスト開始...")

try:
    # 各機能のインポート確認
    print("\n1️⃣ WindowResizer インポート...")
    from features.window_resizer import WindowResizer
    print("✅ WindowResizer OK")
    
    print("\n2️⃣ PomodoroStatistics インポート...")
    from features.statistics import PomodoroStatistics
    print("✅ PomodoroStatistics OK")
    
    print("\n3️⃣ MusicPresets インポート...")
    from features.music_presets import MusicPresetsSimple
    print("✅ MusicPresets OK")
    
    # 基本的な機能テスト
    print("\n4️⃣ 統計機能テスト...")
    stats = PomodoroStatistics()
    stats.record_session("work", 25)
    stats.record_session("break", 5)
    summary = stats.get_stats_summary()
    print("✅ 統計機能 OK")
    print(f"セッション数: {stats.get_total_stats()['total_sessions']}")
    
    print("\n5️⃣ 音楽プリセット機能テスト...")
    music = MusicPresetsSimple()
    music.set_preset("work")
    music.play()
    music.stop()
    print("✅ 音楽プリセット機能 OK")
    
    print("\n✅ すべてのテストが成功しました！")
    print("Phase 2 機能は正常に動作しています。")
    
except Exception as e:
    print(f"\n❌ エラーが発生しました: {e}")
    import traceback
    traceback.print_exc()