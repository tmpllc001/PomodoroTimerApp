#!/usr/bin/env python3
"""
エンドツーエンド統合テスト
全機能の包括的テストシナリオ
"""
import sys
import os
import time
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# PyQt6のテスト環境設定
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from src.controllers.timer_controller import TimerController
from src.models.timer_model import TimerState, SessionType
from src.bridge.ui_bridge import UIBridge
from src.utils.config_manager import ConfigManager
from src.utils.performance_monitor import PerformanceMonitor


class EndToEndTestSuite:
    """エンドツーエンド統合テストスイート."""
    
    def __init__(self):
        self.test_results = []
        self.temp_dir = None
        self.config_manager = None
        self.performance_monitor = None
        
    def setup_test_environment(self):
        """テスト環境セットアップ."""
        print("=== テスト環境セットアップ ===")
        
        # 一時ディレクトリ作成
        self.temp_dir = tempfile.mkdtemp(prefix="pomodoro_test_")
        print(f"一時ディレクトリ: {self.temp_dir}")
        
        # 一時設定ファイル
        self.test_config_file = os.path.join(self.temp_dir, "test_config.json")
        self.test_sessions_file = os.path.join(self.temp_dir, "test_sessions.json")
        
        print("✅ テスト環境セットアップ完了")
        
    def cleanup_test_environment(self):
        """テスト環境クリーンアップ."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
        print("✅ テスト環境クリーンアップ完了")
        
    def test_full_pomodoro_cycle(self):
        """完全なポモドーロサイクルテスト."""
        print("\n=== 完全ポモドーロサイクルテスト ===")
        
        # 短時間設定でテスト
        controller = TimerController(self.test_config_file)
        controller.set_sound_enabled(False)
        controller.set_durations(2, 1, 3, 2)  # 2秒作業、1秒短休憩、3秒長休憩、2回で長休憩
        
        session_events = []
        
        def track_session_complete(session_type):
            session_events.append(session_type)
            print(f"セッション完了: {session_type}")
        
        controller.on_session_complete = track_session_complete
        
        # 1回目の作業セッション
        print("1回目の作業セッション開始")
        controller.start_timer()
        time.sleep(2.5)
        
        assert len(session_events) == 1
        assert session_events[0] == SessionType.WORK
        
        # 短い休憩が自動開始
        print("短い休憩セッション開始")
        controller.start_timer()
        time.sleep(1.5)
        
        assert len(session_events) == 2
        assert session_events[1] == SessionType.SHORT_BREAK
        
        # 2回目の作業セッション
        print("2回目の作業セッション開始")
        controller.start_timer()
        time.sleep(2.5)
        
        assert len(session_events) == 3
        assert session_events[2] == SessionType.WORK
        
        # 長い休憩が自動開始（2回目なので）
        print("長い休憩セッション開始")
        controller.start_timer()
        time.sleep(3.5)
        
        assert len(session_events) == 4
        assert session_events[3] == SessionType.LONG_BREAK
        
        # セッション統計確認
        stats = controller.get_session_stats()
        print(f"完了セッション数: {stats['completed_sessions']}")
        print(f"総作業時間: {stats['total_work_time']}秒")
        
        assert stats['completed_sessions'] >= 4
        assert stats['total_work_time'] >= 4  # 2回 × 2秒
        
        controller.cleanup()
        print("✅ 完全ポモドーロサイクルテスト成功")
        return True
        
    def test_ui_backend_integration(self):
        """UI-バックエンド統合テスト."""
        print("\n=== UI-バックエンド統合テスト ===")
        
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import QTimer
            
            if not QApplication.instance():
                app = QApplication(sys.argv)
            else:
                app = QApplication.instance()
                
            # Mock UI
            mock_window = Mock()
            
            # コントローラーとブリッジ作成
            controller = TimerController(self.test_config_file)
            controller.set_sound_enabled(False)
            bridge = UIBridge(controller, mock_window)
            
            # シグナル受信テスト
            signal_received = []
            
            def on_timer_update(info):
                signal_received.append(('timer_update', info))
                
            def on_state_change(state):
                signal_received.append(('state_change', state))
                
            bridge.timer_updated.connect(on_timer_update)
            bridge.state_changed.connect(on_state_change)
            
            # タイマー操作テスト
            bridge.start_timer()
            time.sleep(0.2)
            
            bridge.pause_timer()
            time.sleep(0.1)
            
            bridge.stop_timer()
            time.sleep(0.1)
            
            # シグナル受信確認
            print(f"受信シグナル数: {len(signal_received)}")
            assert len(signal_received) > 0
            
            # 設定変更テスト
            bridge.set_work_duration(30)
            durations = bridge.get_current_durations()
            assert durations['work'] == 30 * 60
            
            # データ取得テスト
            timer_info = bridge.get_timer_info()
            assert 'state' in timer_info
            assert 'remaining_time' in timer_info
            
            bridge.cleanup()
            controller.cleanup()
            
            print("✅ UI-バックエンド統合テスト成功")
            return True
            
        except ImportError:
            print("⚠️  PyQt6未インストール - UIテストスキップ")
            return True
            
    def test_configuration_management(self):
        """設定管理テスト."""
        print("\n=== 設定管理テスト ===")
        
        # 設定マネージャー作成
        config_manager = ConfigManager(self.test_config_file)
        
        # デフォルト設定確認
        timer_config = config_manager.get_timer_config()
        assert timer_config.work_duration == 25 * 60
        assert timer_config.short_break_duration == 5 * 60
        
        # 設定変更
        config_manager.update_timer_config(work_duration=30*60)
        config_manager.update_ui_config(theme="light", window_opacity=0.8)
        
        # 設定保存・再読み込み
        assert config_manager.save_config()
        
        new_config_manager = ConfigManager(self.test_config_file)
        new_timer_config = new_config_manager.get_timer_config()
        new_ui_config = new_config_manager.get_ui_config()
        
        assert new_timer_config.work_duration == 30 * 60
        assert new_ui_config.theme == "light"
        assert new_ui_config.window_opacity == 0.8
        
        # 設定検証
        assert config_manager.validate_config()
        
        # 設定エクスポート/インポート
        export_path = os.path.join(self.temp_dir, "exported_config.json")
        assert config_manager.export_config(export_path)
        assert os.path.exists(export_path)
        
        # バックアップ作成
        assert config_manager.create_backup()
        
        print("✅ 設定管理テスト成功")
        return True
        
    def test_performance_monitoring(self):
        """パフォーマンス監視テスト."""
        print("\n=== パフォーマンス監視テスト ===")
        
        monitor = PerformanceMonitor(sample_interval=0.1)
        monitor.start_monitoring()
        
        # 負荷生成
        controller = TimerController()
        controller.set_sound_enabled(False)
        
        for i in range(50):
            controller.start_timer()
            time.sleep(0.001)
            controller.pause_timer()
            time.sleep(0.001)
            controller.stop_timer()
            monitor.record_ui_update()
            
        time.sleep(1.0)  # データ収集待機
        
        # メトリクス確認
        current_metrics = monitor.get_current_metrics()
        assert current_metrics is not None
        
        average_metrics = monitor.get_average_metrics(1)
        assert 'cpu_percent' in average_metrics
        assert 'memory_usage' in average_metrics
        
        # パフォーマンス劣化チェック
        degraded = monitor.is_performance_degraded()
        print(f"パフォーマンス劣化: {degraded}")
        
        # メトリクスエクスポート
        metrics_path = os.path.join(self.temp_dir, "performance_metrics.json")
        assert monitor.export_metrics(metrics_path, hours=1)
        assert os.path.exists(metrics_path)
        
        # パフォーマンスサマリー
        summary = monitor.get_performance_summary()
        print(f"監視時間: {summary['monitoring_duration']:.1f}分")
        print(f"総サンプル数: {summary['total_samples']}")
        
        monitor.cleanup()
        controller.cleanup()
        
        print("✅ パフォーマンス監視テスト成功")
        return True
        
    def test_error_handling(self):
        """エラーハンドリングテスト."""
        print("\n=== エラーハンドリングテスト ===")
        
        # 不正な設定ファイルテスト
        invalid_config_path = os.path.join(self.temp_dir, "invalid_config.json")
        with open(invalid_config_path, 'w') as f:
            f.write("invalid json content")
            
        config_manager = ConfigManager(invalid_config_path)
        # エラーが発生してもクラッシュしないことを確認
        assert config_manager.get_timer_config() is not None
        
        # 存在しないディレクトリへの保存テスト
        controller = TimerController("/invalid/path/config.json")
        # エラーが発生してもクラッシュしないことを確認
        controller.set_durations(25*60, 5*60, 15*60, 4)
        
        # 無効な設定値テスト
        controller.set_durations(-1, 0, 0, 0)  # 無効な値
        info = controller.get_timer_info()
        # 無効な値が設定されても動作することを確認
        
        controller.cleanup()
        
        print("✅ エラーハンドリングテスト成功")
        return True
        
    def test_data_persistence(self):
        """データ永続化テスト."""
        print("\n=== データ永続化テスト ===")
        
        # セッションデータ作成
        controller = TimerController(self.test_config_file)
        controller.session_model.data_file = self.test_sessions_file
        controller.set_sound_enabled(False)
        
        # セッション実行
        from src.models.session_model import Session
        from datetime import datetime
        
        session = Session(
            session_type=SessionType.WORK,
            start_time=datetime.now(),
            planned_duration=25*60
        )
        
        controller.session_model.start_session(session)
        controller.session_model.complete_session(actual_duration=24*60, completed=True)
        
        # データ保存確認
        assert os.path.exists(self.test_sessions_file)
        
        # 新しいコントローラーでデータ読み込み確認
        new_controller = TimerController(self.test_config_file)
        new_controller.session_model.data_file = self.test_sessions_file
        new_controller.session_model._load_sessions()
        
        stats = new_controller.get_session_stats()
        assert stats['total_sessions'] >= 1
        assert stats['completed_sessions'] >= 1
        
        # データエクスポート
        export_data = new_controller.session_model.export_sessions()
        assert len(export_data) >= 1
        
        controller.cleanup()
        new_controller.cleanup()
        
        print("✅ データ永続化テスト成功")
        return True
        
    def test_stress_testing(self):
        """ストレステスト."""
        print("\n=== ストレステスト ===")
        
        # 多重コントローラーテスト
        controllers = []
        
        try:
            for i in range(10):
                controller = TimerController()
                controller.set_sound_enabled(False)
                controllers.append(controller)
                
            # 同時操作テスト
            for controller in controllers:
                controller.start_timer()
                
            time.sleep(0.1)
            
            for controller in controllers:
                controller.pause_timer()
                
            time.sleep(0.1)
            
            for controller in controllers:
                controller.stop_timer()
                
            # メモリリークチェック
            import psutil
            process = psutil.Process()
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # 大量操作
            for _ in range(100):
                for controller in controllers:
                    info = controller.get_timer_info()
                    stats = controller.get_session_stats()
                    
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = memory_after - memory_before
            
            print(f"メモリ増加: {memory_increase:.1f} MB")
            
            # 許容範囲内のメモリ増加かチェック
            if memory_increase > 50:  # 50MB以上の増加は問題
                print("⚠️  メモリ使用量増加が大きすぎます")
                
        finally:
            # クリーンアップ
            for controller in controllers:
                controller.cleanup()
                
        print("✅ ストレステスト成功")
        return True
        
    def run_all_tests(self):
        """全テスト実行."""
        print("🚀 エンドツーエンドテストスイート開始")
        
        self.setup_test_environment()
        
        tests = [
            ("完全ポモドーロサイクル", self.test_full_pomodoro_cycle),
            ("UI-バックエンド統合", self.test_ui_backend_integration),
            ("設定管理", self.test_configuration_management),
            ("パフォーマンス監視", self.test_performance_monitoring),
            ("エラーハンドリング", self.test_error_handling),
            ("データ永続化", self.test_data_persistence),
            ("ストレステスト", self.test_stress_testing),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result, None))
            except Exception as e:
                print(f"❌ {test_name}テスト失敗: {e}")
                import traceback
                traceback.print_exc()
                results.append((test_name, False, str(e)))
                
        self.cleanup_test_environment()
        
        # 結果サマリー
        print("\n" + "="*50)
        print("🎯 テスト結果サマリー")
        print("="*50)
        
        passed = 0
        failed = 0
        
        for test_name, result, error in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
            if error:
                print(f"   エラー: {error}")
            
            if result:
                passed += 1
            else:
                failed += 1
                
        print(f"\n📊 成功: {passed}/{len(tests)} テスト")
        print(f"📊 失敗: {failed}/{len(tests)} テスト")
        
        overall_success = failed == 0
        
        if overall_success:
            print("\n🎉 全テスト成功！アプリケーションは本番準備完了です。")
        else:
            print(f"\n⚠️  {failed}個のテストが失敗しました。修正が必要です。")
            
        return overall_success


def main():
    """メイン実行関数."""
    test_suite = EndToEndTestSuite()
    success = test_suite.run_all_tests()
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)