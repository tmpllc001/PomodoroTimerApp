#!/usr/bin/env python3
"""
ポモドーロタイマー統合テスト
"""
import sys
import os
import time
import threading
from pathlib import Path

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.controllers.timer_controller import TimerController
from src.models.timer_model import TimerState, SessionType


def test_timer_basic_operations():
    print("=== タイマー基本操作テスト ===")
    
    controller = TimerController()
    
    # 初期状態確認
    info = controller.get_timer_info()
    print(f"初期状態: {info['state']}")
    print(f"初期時間: {controller.timer_model.get_formatted_time()}")
    assert info['state'] == TimerState.STOPPED
    
    # タイマー開始
    controller.start_timer()
    time.sleep(0.1)
    info = controller.get_timer_info()
    print(f"開始後状態: {info['state']}")
    assert info['state'] == TimerState.RUNNING
    
    # 一時停止
    controller.pause_timer()
    time.sleep(0.1)
    info = controller.get_timer_info()
    print(f"一時停止後状態: {info['state']}")
    assert info['state'] == TimerState.PAUSED
    
    # 再開
    controller.start_timer()
    time.sleep(0.1)
    info = controller.get_timer_info()
    print(f"再開後状態: {info['state']}")
    assert info['state'] == TimerState.RUNNING
    
    # 停止
    controller.stop_timer()
    time.sleep(0.1)
    info = controller.get_timer_info()
    print(f"停止後状態: {info['state']}")
    assert info['state'] == TimerState.STOPPED
    
    # リセット
    controller.reset_timer()
    info = controller.get_timer_info()
    print(f"リセット後: {info['remaining_time']}秒")
    assert info['remaining_time'] == 25 * 60
    
    controller.cleanup()
    print("✅ 基本操作テスト完了")


def test_session_model():
    print("\n=== セッションモデルテスト ===")
    
    from src.models.session_model import SessionModel, Session
    from datetime import datetime
    
    # テスト用のセッションファイル
    test_file = "test_sessions.json"
    if os.path.exists(test_file):
        os.remove(test_file)
    
    session_model = SessionModel(test_file)
    
    # セッション作成
    session = Session(
        session_type=SessionType.WORK,
        start_time=datetime.now(),
        planned_duration=25 * 60
    )
    
    session_model.start_session(session)
    print(f"セッション開始: {session.session_type}")
    
    # セッション完了
    session_model.complete_session(actual_duration=24 * 60, completed=True)
    print("セッション完了")
    
    # 統計取得
    stats = session_model.get_session_stats()
    print(f"総セッション数: {stats['total_sessions']}")
    print(f"完了セッション数: {stats['completed_sessions']}")
    print(f"完了率: {stats['completion_rate']:.1f}%")
    
    assert stats['total_sessions'] == 1
    assert stats['completed_sessions'] == 1
    
    # クリーンアップ
    if os.path.exists(test_file):
        os.remove(test_file)
    
    print("✅ セッションモデルテスト完了")


def test_audio_manager():
    print("\n=== 音声管理テスト ===")
    
    from src.utils.audio_manager import AudioManager
    
    audio_manager = AudioManager()
    
    # 音声設定テスト
    audio_manager.set_volume(0.5)
    assert audio_manager.get_volume() == 0.5
    
    audio_manager.set_sound_enabled(False)
    assert not audio_manager.is_sound_enabled()
    
    audio_manager.set_sound_enabled(True)
    assert audio_manager.is_sound_enabled()
    
    # 音声情報取得
    info = audio_manager.get_audio_info()
    print(f"音声情報: {info}")
    
    # 音声テスト（実際の音は出力されない設定で）
    audio_manager.set_sound_enabled(False)
    audio_manager.play_work_complete_sound()
    audio_manager.play_break_complete_sound()
    
    audio_manager.cleanup()
    print("✅ 音声管理テスト完了")


def test_timer_integration():
    print("\n=== タイマー統合テスト ===")
    
    # 短い時間設定でテスト
    controller = TimerController()
    controller.set_durations(
        work_duration=3,  # 3秒
        short_break_duration=2,  # 2秒
        long_break_duration=4,  # 4秒
        long_break_interval=2  # 2回後に長い休憩
    )
    
    # 音声無効化
    controller.set_sound_enabled(False)
    
    session_complete_count = 0
    
    def on_session_complete(session_type):
        nonlocal session_complete_count
        session_complete_count += 1
        print(f"セッション完了: {session_type}")
    
    def on_timer_update(info):
        print(f"タイマー更新: {info['remaining_time']}秒, 進捗: {info['progress']:.1%}")
    
    controller.on_session_complete = on_session_complete
    controller.on_timer_update = on_timer_update
    
    # 短いワークセッション実行
    print("ワークセッション開始")
    controller.start_timer()
    time.sleep(3.5)  # 3秒より少し長く待機
    
    # セッション完了を確認
    assert session_complete_count == 1
    
    controller.cleanup()
    print("✅ 統合テスト完了")


def test_configuration():
    print("\n=== 設定テスト ===")
    
    test_config = "test_config.json"
    if os.path.exists(test_config):
        os.remove(test_config)
    
    controller = TimerController(test_config)
    
    # デフォルト設定確認
    info = controller.get_timer_info()
    assert info['remaining_time'] == 25 * 60
    
    # 設定変更
    controller.set_durations(
        work_duration=30 * 60,
        short_break_duration=10 * 60,
        long_break_duration=20 * 60,
        long_break_interval=3
    )
    
    controller.set_volume(0.8)
    controller.save_config()
    
    # 新しいコントローラーで設定読み込み
    controller2 = TimerController(test_config)
    assert controller2.get_volume() == 0.8
    
    controller.cleanup()
    controller2.cleanup()
    
    # クリーンアップ
    if os.path.exists(test_config):
        os.remove(test_config)
    
    print("✅ 設定テスト完了")


def main():
    print("ポモドーロタイマー統合テストを開始します...")
    
    try:
        test_timer_basic_operations()
        test_session_model()
        test_audio_manager()
        test_timer_integration()
        test_configuration()
        
        print("\n🎉 全てのテストが成功しました！")
        return True
        
    except Exception as e:
        print(f"\n❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)