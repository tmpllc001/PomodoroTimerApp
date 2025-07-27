#!/usr/bin/env python3
"""
Phase 3 最小動作テスト
依存関係がなくても基本機能を確認
"""

import sys
import os
from pathlib import Path

# プロジェクトパス追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

# Phase 3の実装状況を確認
print("🔍 Phase 3 実装状況確認\n")

# タスク管理機能
try:
    from features.tasks.task_manager import TaskManager
    from features.tasks.task_widget import TaskWidget
    from features.tasks.task_integration import TaskIntegration
    print("✅ タスク管理機能: 実装済み")
    print("   - TaskManager: タスク管理ロジック")
    print("   - TaskWidget: タスクUI")
    print("   - TaskIntegration: ポモドーロ連携")
except ImportError as e:
    print(f"❌ タスク管理機能: {e}")

# 統計ダッシュボード
try:
    from features.dashboard.dashboard_widget import DashboardWidget
    print("✅ ダッシュボード基本: 実装済み")
except ImportError as e:
    print(f"⚠️  ダッシュボード: matplotlib依存のため利用不可")

# テーマ機能
try:
    from features.themes.theme_widget import ThemeWidget
    from features.themes.theme_manager import ThemeManager
    print("✅ テーマ機能: 実装済み")
    print("   - ThemeWidget: テーマ選択UI")
    print("   - ThemeManager: テーマ管理")
except ImportError as e:
    print(f"❌ テーマ機能: {e}")

# 基本ポモドーロ機能
try:
    from controllers.timer_controller import TimerController
    from models.timer_model import TimerModel
    from views.main_window import MainWindow
    print("\n✅ 基本ポモドーロ機能: 実装済み")
    print("   - TimerController: タイマー制御")
    print("   - TimerModel: タイマーデータ")
    print("   - MainWindow: メインUI")
except ImportError as e:
    print(f"\n❌ 基本機能: {e}")

# Phase 2機能
try:
    from features.window_resizer import WindowResizer
    from features.statistics import PomodoroStatistics
    from features.music_presets import MusicPresetsSimple
    print("\n✅ Phase 2機能: 実装済み")
    print("   - WindowResizer: ウィンドウサイズ変更")
    print("   - PomodoroStatistics: 統計機能")
    print("   - MusicPresets: 音楽プリセット")
except ImportError as e:
    print(f"\n❌ Phase 2機能: {e}")

# タスクマネージャーのテスト
print("\n📋 タスクマネージャー動作テスト")
try:
    from features.tasks.task_manager import TaskManager
    
    # タスクマネージャー初期化
    tm = TaskManager()
    
    # タスク追加
    task1 = tm.add_task("Phase 3実装", "ダッシュボード機能を実装", priority=5, estimated_pomodoros=4)
    task2 = tm.add_task("ドキュメント作成", "ユーザーマニュアル作成", priority=3, estimated_pomodoros=2)
    
    print(f"✅ タスク追加成功: {len(tm.get_all_tasks())}個のタスク")
    
    # タスク一覧表示
    for task in tm.get_pending_tasks():
        print(f"   - {task['title']} (優先度: {task['priority']}, 予定: {task['estimated_pomodoros']}ポモドーロ)")
    
    # タスク統計
    stats = tm.get_task_statistics()
    print(f"\n✅ タスク統計:")
    print(f"   - 総タスク数: {stats['total_tasks']}")
    print(f"   - 未完了: {stats['pending_tasks']}")
    print(f"   - 完了: {stats['completed_tasks']}")
    
except Exception as e:
    print(f"❌ タスクマネージャーエラー: {e}")

# 設定ファイル確認
print("\n📁 設定ファイル確認")
config_files = ['config.json', 'data/tasks.json', 'data/themes.json', 'data/statistics.json']
for cf in config_files:
    if Path(cf).exists():
        print(f"✅ {cf}: 存在")
    else:
        print(f"⚠️  {cf}: 未作成")

print("\n✨ Phase 3 実装状況確認完了")
print("\n📌 Phase 3を完全に動作させるには:")
print("   pip install -r requirements_phase3.txt")
print("\n🚀 基本機能は以下で実行可能:")
print("   python main_phase2_final.py  # Phase 2まで")
print("   python main_phase3.py       # Phase 3基本版")