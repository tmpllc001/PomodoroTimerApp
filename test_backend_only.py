#!/usr/bin/env python3
"""
バックエンドのみエンドツーエンドテスト（PyQt6なし）
"""
import sys
import os
import time
import json
import tempfile
from pathlib import Path

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.controllers.timer_controller import TimerController
from src.models.timer_model import TimerState, SessionType
from src.utils.config_manager import ConfigManager
from src.utils.performance_monitor import PerformanceMonitor


def test_complete_integration():
    """完全統合テスト（バックエンドのみ）."""
    print("🚀 バックエンド統合テスト開始")
    
    # 一時ディレクトリ
    temp_dir = tempfile.mkdtemp(prefix="pomodoro_test_")
    test_config = os.path.join(temp_dir, "test_config.json")
    
    try:
        # 1. 設定管理テスト
        print("\n=== 設定管理テスト ===")
        config_manager = ConfigManager(test_config)
        config_manager.update_timer_config(work_duration=3, short_break_duration=2, long_break_duration=4)
        assert config_manager.save_config()
        
        # 2. タイマーコントローラーテスト
        print("\n=== タイマーコントローラーテスト ===")
        controller = TimerController(test_config)
        controller.set_sound_enabled(False)
        
        # 直接短い時間設定
        controller.set_durations(3, 2, 4, 2)  # 3秒作業、2秒短休憩、4秒長休憩、2回で長休憩
        
        # 設定確認
        timer_info = controller.get_timer_info()
        assert timer_info['remaining_time'] == 3
        
        # 3. 完全サイクルテスト
        print("\n=== 完全サイクルテスト ===")
        sessions_completed = []
        
        def track_completion(session_type):
            sessions_completed.append(session_type)
            print(f"セッション完了: {session_type}")
        
        controller.on_session_complete = track_completion
        
        # 作業セッション1
        controller.start_timer()
        time.sleep(3.5)
        assert len(sessions_completed) == 1
        assert sessions_completed[0] == SessionType.WORK
        
        # 短休憩
        controller.start_timer()
        time.sleep(2.5)
        assert len(sessions_completed) == 2
        assert sessions_completed[1] == SessionType.SHORT_BREAK
        
        # 作業セッション2
        controller.start_timer()
        time.sleep(3.5)
        assert len(sessions_completed) == 3
        assert sessions_completed[2] == SessionType.WORK
        
        # 長休憩（2回目なので）
        controller.start_timer()
        time.sleep(4.5)
        assert len(sessions_completed) == 4
        assert sessions_completed[3] == SessionType.LONG_BREAK
        
        # 4. 統計確認
        print("\n=== 統計確認 ===")
        stats = controller.get_session_stats()
        print(f"完了セッション: {stats['completed_sessions']}")
        print(f"総作業時間: {stats['total_work_time']}秒")
        print(f"完了率: {stats['completion_rate']:.1f}%")
        
        assert stats['completed_sessions'] >= 4
        assert stats['total_work_time'] >= 6  # 2 × 3秒
        
        # 5. パフォーマンス監視テスト
        print("\n=== パフォーマンス監視テスト ===")
        monitor = PerformanceMonitor(0.1)
        monitor.start_monitoring()
        
        # 負荷生成
        for i in range(100):
            controller.get_timer_info()
            monitor.record_ui_update()
            if i % 20 == 0:
                print(f"処理完了: {i+1}/100")
        
        time.sleep(1.0)
        
        current_metrics = monitor.get_current_metrics()
        print(f"CPU使用率: {current_metrics.cpu_percent:.1f}%")
        print(f"メモリ使用量: {current_metrics.memory_usage:.1f}MB")
        print(f"UI更新レート: {current_metrics.ui_updates_per_second:.1f}/秒")
        
        # パフォーマンス劣化チェック
        assert not monitor.is_performance_degraded()
        
        monitor.cleanup()
        controller.cleanup()
        
        print("\n✅ 全てのバックエンドテスト成功！")
        return True
        
    except Exception as e:
        print(f"\n❌ テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # クリーンアップ
        import shutil
        shutil.rmtree(temp_dir)


def main():
    """メイン実行."""
    return test_complete_integration()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)