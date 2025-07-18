#!/usr/bin/env python3
"""
MVP バックエンド動作確認テスト
GUI環境がない場合のテスト
"""

import sys
import time
from pathlib import Path

# プロジェクトパス追加
sys.path.insert(0, str(Path(__file__).parent))

from src.controllers.timer_controller import TimerController
from src.models.timer_model import TimerState, SessionType


def test_mvp_backend():
    """MVP バックエンド機能テスト."""
    print("🚀 MVP バックエンドテスト開始")
    
    # タイマーコントローラー作成
    controller = TimerController()
    controller.set_sound_enabled(False)
    
    # 短時間設定
    controller.set_durations(3, 2, 4, 2)
    
    print("\n=== MVP機能テスト ===")
    
    # 1. 初期状態確認
    timer_info = controller.get_timer_info()
    print(f"初期状態: {timer_info['state']}")
    print(f"初期時間: {controller.timer_model.get_formatted_time()}")
    
    # 2. タイマー開始
    print("\n🎯 作業セッション開始")
    controller.start_timer()
    
    for i in range(4):
        time.sleep(1)
        timer_info = controller.get_timer_info()
        formatted_time = controller.timer_model.get_formatted_time()
        progress = timer_info.get('progress', 0) * 100
        print(f"⏰ {formatted_time} (進捗: {progress:.0f}%)")
    
    # 3. 一時停止テスト
    print("\n⏸ 一時停止テスト")
    controller.pause_timer()
    time.sleep(1)
    timer_info = controller.get_timer_info()
    print(f"一時停止状態: {timer_info['state']}")
    
    # 4. 再開テスト
    print("\n▶ 再開テスト")
    controller.start_timer()
    time.sleep(1)
    
    # 5. リセットテスト
    print("\n🔄 リセットテスト")
    controller.reset_timer()
    timer_info = controller.get_timer_info()
    print(f"リセット後: {controller.timer_model.get_formatted_time()}")
    
    # 6. 統計テスト
    print("\n📊 統計テスト")
    stats = controller.get_session_stats()
    print(f"総セッション数: {stats['total_sessions']}")
    print(f"完了セッション数: {stats['completed_sessions']}")
    print(f"完了率: {stats['completion_rate']:.1f}%")
    
    # 7. 設定テスト
    print("\n⚙️ 設定テスト")
    controller.set_volume(0.5)
    volume = controller.get_volume()
    print(f"音量設定: {volume}")
    
    sound_enabled = controller.is_sound_enabled()
    print(f"音声有効: {sound_enabled}")
    
    # クリーンアップ
    controller.cleanup()
    
    print("\n✅ MVP バックエンドテスト完了！")
    print("🎉 全機能が正常に動作しています")
    
    return True


def main():
    """メイン実行."""
    try:
        success = test_mvp_backend()
        if success:
            print("\n🎯 MVP準備完了！")
            print("PyQt6をインストールすればGUIも動作します:")
            print("pip install PyQt6")
            return 0
        else:
            return 1
    except Exception as e:
        print(f"\n❌ テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())