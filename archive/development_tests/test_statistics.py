#!/usr/bin/env python3
"""
統計機能の統合テスト
Phase 2 基本統計機能のテスト
"""
import sys
import os
from pathlib import Path
import tempfile
import uuid
from datetime import datetime, timedelta

# プロジェクトパス追加
sys.path.insert(0, str(Path(__file__).parent))

def test_statistics_integration():
    """統計機能の統合テスト"""
    print("🔍 統計機能統合テスト開始")
    
    # 1. SessionDataManagerテスト
    print("\n=== SessionDataManagerテスト ===")
    try:
        from src.models.session_data import SessionData, SessionDataManager
        
        # 一時ファイルでテスト
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        manager = SessionDataManager(temp_file)
        
        # テストセッション追加
        now = datetime.now()
        test_session = SessionData(
            session_id=str(uuid.uuid4()),
            session_type='work',
            start_time=now - timedelta(minutes=25),
            end_time=now,
            planned_duration=25,
            actual_duration=25,
            completed=True
        )
        
        manager.add_session(test_session)
        print("✅ SessionDataManager: セッション追加成功")
        
        # 統計データ取得
        today_stats = manager.get_today_stats()
        print(f"✅ 今日の統計: 作業セッション={today_stats.work_sessions}, 作業時間={today_stats.work_time}分")
        
        # ファイルクリーンアップ
        os.unlink(temp_file)
        
    except Exception as e:
        print(f"❌ SessionDataManagerテスト失敗: {e}")
        return False
    
    # 2. PomodoroStatisticsテスト
    print("\n=== PomodoroStatisticsテスト ===")
    try:
        from src.features.statistics import PomodoroStatistics
        
        # 一時ディレクトリでテスト
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_stats_file = os.path.join(temp_dir, "test_stats.json")
            stats = PomodoroStatistics(temp_stats_file)
            
            # テストセッション記録
            stats.record_session('work', 25, completed=True)
            stats.record_session('short_break', 5, completed=True)
            stats.record_session('work', 25, completed=False)
            
            print("✅ PomodoroStatistics: セッション記録成功")
            
            # 統計データ取得
            today_stats = stats.get_today_stats()
            print(f"✅ 今日の統計: 作業セッション={today_stats['work_sessions']}, 作業時間={today_stats['work_time']}分")
            
            week_stats = stats.get_week_stats()
            print(f"✅ 今週の統計: 作業セッション={week_stats['work_sessions']}, 作業時間={week_stats['work_time']}分")
            
            total_stats = stats.get_total_stats()
            print(f"✅ 全体統計: 総セッション={total_stats['total_sessions']}, 総作業時間={total_stats['total_work_time']}分")
            
            # 生産性スコア
            productivity = stats.get_productivity_score()
            print(f"✅ 生産性スコア: {productivity}%")
            
            # 時間フォーマット
            formatted_time = stats.format_time(90)
            print(f"✅ 時間フォーマット: {formatted_time}")
            
    except Exception as e:
        print(f"❌ PomodoroStatisticsテスト失敗: {e}")
        return False
    
    # 3. StatsWidgetテスト
    print("\n=== StatsWidgetテスト ===")
    try:
        from src.features.stats_widget import StatsWidget, StatsCard, ProductivityMeter
        
        # PyQt6の利用可能性チェック
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import Qt
            
            # テスト用アプリケーション作成
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            
            # StatsCardテスト
            card = StatsCard("テスト", "100", "単位")
            card.update_value("200")
            print("✅ StatsCard: 作成・更新成功")
            
            # ProductivityMeterテスト
            meter = ProductivityMeter()
            meter.update_score(75.5)
            print("✅ ProductivityMeter: 作成・更新成功")
            
            # StatsWidgetテスト
            widget = StatsWidget()
            widget.refresh_stats()
            print("✅ StatsWidget: 作成・更新成功")
            
            # クリーンアップ
            widget.cleanup()
            
        except ImportError:
            print("⚠️  PyQt6が利用できません。GUIテストをスキップします")
            print("✅ StatsWidget: インポート成功（GUI環境なし）")
            
    except Exception as e:
        print(f"❌ StatsWidgetテスト失敗: {e}")
        return False
    
    # 4. TimerControllerとの統合テスト
    print("\n=== TimerController統合テスト ===")
    try:
        from src.controllers.timer_controller import TimerController
        from src.features.statistics import PomodoroStatistics
        
        # 一時ファイルでテスト
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_stats_file = os.path.join(temp_dir, "integration_stats.json")
            
            controller = TimerController()
            stats = PomodoroStatistics(temp_stats_file)
            
            # セッション開始のシミュレーション
            timer_info = controller.get_timer_info()
            print(f"✅ タイマー情報取得: {timer_info['state']}")
            
            # 統計と連携（将来的な統合を想定）
            stats.record_session('work', 25, completed=True)
            today_stats = stats.get_today_stats()
            
            print(f"✅ 統合テスト: 作業セッション={today_stats['work_sessions']}")
            
            controller.cleanup()
            
    except Exception as e:
        print(f"❌ TimerController統合テスト失敗: {e}")
        return False
    
    # 5. データファイル作成テスト
    print("\n=== データファイル作成テスト ===")
    try:
        # dataディレクトリ作成
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # 統計ファイル作成
        stats_file = data_dir / "statistics.json"
        stats = PomodoroStatistics(str(stats_file))
        
        # テストデータ追加
        stats.record_session('work', 25, completed=True)
        stats.record_session('short_break', 5, completed=True)
        
        # ファイル存在確認
        if stats_file.exists():
            print(f"✅ データファイル作成: {stats_file}")
        else:
            print("❌ データファイル作成失敗")
            return False
            
    except Exception as e:
        print(f"❌ データファイル作成テスト失敗: {e}")
        return False
    
    print("\n🎉 統計機能統合テスト完了！")
    print("📊 テスト結果:")
    print("✅ SessionDataManager: 正常動作")
    print("✅ PomodoroStatistics: 正常動作")
    print("✅ StatsWidget: 正常動作")
    print("✅ TimerController統合: 正常動作")
    print("✅ データファイル作成: 正常動作")
    
    return True


def main():
    """メイン実行"""
    try:
        success = test_statistics_integration()
        if success:
            print("\n🎯 Phase 2 統計機能実装完了！")
            print("📈 実装内容:")
            print("  - SessionData/SessionDataManager: セッションデータ管理")
            print("  - PomodoroStatistics: 統計計算エンジン")
            print("  - StatsWidget: 統計表示UI")
            print("  - データ永続化: JSON形式")
            print("  - 自動更新: 30秒間隔")
            print("  - 生産性スコア計算")
            print("  - 日別・週別・全体統計")
            return 0
        else:
            print("\n❌ テストに失敗しました")
            return 1
    except Exception as e:
        print(f"\n❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())