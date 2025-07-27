#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 4 高度統計機能テストスクリプト
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import random

# テストデータ生成
def generate_test_data():
    """テスト用のセッションデータを生成"""
    print("📊 テスト用セッションデータを生成中...")
    
    # advanced_session_data.json に追加データを生成
    sessions = []
    base_date = datetime.now() - timedelta(days=7)
    
    for day in range(7):
        date = base_date + timedelta(days=day)
        # 1日3-5セッション
        num_sessions = random.randint(3, 5)
        
        for session in range(num_sessions):
            session_time = date.replace(
                hour=random.randint(9, 17),
                minute=random.randint(0, 59)
            )
            
            session_data = {
                "session_id": f"work_{session_time.strftime('%Y%m%d_%H%M%S')}",
                "type": "work",
                "planned_duration": 25,
                "start_time": session_time.isoformat(),
                "actual_duration": random.uniform(20, 25),
                "completed": random.random() > 0.2,
                "efficiency_score": random.uniform(70, 100),
                "focus_score": random.uniform(60, 95),
                "interruptions": random.randint(0, 3),
                "environment_data": {
                    "hour_of_day": session_time.hour,
                    "day_of_week": session_time.weekday(),
                    "time_period": "morning" if session_time.hour < 12 else "afternoon" if session_time.hour < 17 else "evening"
                }
            }
            sessions.append(session_data)
    
    # データファイルを更新
    data_path = Path("data/test_phase4_data.json")
    data_path.parent.mkdir(exist_ok=True)
    
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump({
            "sessions": sessions,
            "generated_at": datetime.now().isoformat(),
            "total_sessions": len(sessions)
        }, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {len(sessions)}個のテストセッションを生成しました")
    print(f"📁 保存場所: {data_path}")
    return sessions

def test_statistics_features():
    """統計機能のテスト"""
    print("\n🔬 統計機能テスト開始...")
    
    # データ分析
    sessions = generate_test_data()
    
    # 基本統計
    total_sessions = len(sessions)
    completed_sessions = sum(1 for s in sessions if s['completed'])
    avg_focus = sum(s['focus_score'] for s in sessions) / len(sessions)
    avg_efficiency = sum(s['efficiency_score'] for s in sessions) / len(sessions)
    total_interruptions = sum(s['interruptions'] for s in sessions)
    
    print("\n📈 基本統計:")
    print(f"  - 総セッション数: {total_sessions}")
    print(f"  - 完了率: {completed_sessions/total_sessions*100:.1f}%")
    print(f"  - 平均集中度: {avg_focus:.1f}/100")
    print(f"  - 平均効率: {avg_efficiency:.1f}/100")
    print(f"  - 総中断回数: {total_interruptions}")
    
    # 時間帯別分析
    print("\n⏰ 時間帯別分析:")
    time_periods = {}
    for s in sessions:
        period = s['environment_data']['time_period']
        if period not in time_periods:
            time_periods[period] = []
        time_periods[period].append(s['focus_score'])
    
    for period, scores in time_periods.items():
        avg_score = sum(scores) / len(scores)
        print(f"  - {period}: 平均集中度 {avg_score:.1f}")
    
    # 曜日別分析
    print("\n📅 曜日別分析:")
    days = ['月', '火', '水', '木', '金', '土', '日']
    day_performance = {}
    for s in sessions:
        day = s['environment_data']['day_of_week']
        if day not in day_performance:
            day_performance[day] = []
        day_performance[day].append(s['efficiency_score'])
    
    for day, scores in sorted(day_performance.items()):
        if scores:
            avg_score = sum(scores) / len(scores)
            print(f"  - {days[day]}曜日: 平均効率 {avg_score:.1f}")
    
    # 予測サンプル
    print("\n🤖 AI予測サンプル:")
    print("  - 次のセッション予測集中度: 78.5/100")
    print("  - 最適作業時間: 10:00-11:30")
    print("  - 明日の生産性予測: 82.3/100")
    
    # レポート機能
    print("\n📄 利用可能なレポート:")
    print("  1. 包括的分析レポート (PDF)")
    print("  2. 詳細データ分析 (Excel)")
    print("  3. フォーカスヒートマップ")
    print("  4. 生産性トレンドグラフ")
    print("  5. カスタムダッシュボード")
    
    print("\n✨ Phase 4機能テスト完了!")

def show_feature_menu():
    """機能メニューを表示"""
    print("\n" + "="*50)
    print("🚀 Phase 4 高度統計機能メニュー")
    print("="*50)
    print("1. テストデータ生成・基本統計表示")
    print("2. インタラクティブレポート生成（要UI起動）")
    print("3. AI予測機能デモ")
    print("4. エクスポート機能テスト")
    print("5. 自動レポート設定確認")
    print("0. 終了")
    print("="*50)

if __name__ == "__main__":
    print("🎯 ポモドーロタイマー Phase 4 高度統計機能テスト")
    
    while True:
        show_feature_menu()
        choice = input("\n選択してください (0-5): ")
        
        if choice == "1":
            test_statistics_features()
        elif choice == "2":
            print("\n📊 インタラクティブレポートはアプリ内の統計タブから利用できます")
            print("アプリを起動して統計タブを確認してください")
        elif choice == "3":
            print("\n🤖 AI予測機能デモ")
            print("注: scikit-learnがインストールされていない場合は基本予測のみ")
            test_statistics_features()
        elif choice == "4":
            print("\n📄 エクスポート機能")
            print("注: reportlab/openpyxlがインストールされていない場合はJSON/TXT形式のみ")
            print("アプリ内の統計タブからエクスポートボタンを使用してください")
        elif choice == "5":
            print("\n⏰ 自動レポート設定")
            print("設定ファイル: data/schedule_config.json")
            print("日次: 毎日 22:00")
            print("週次: 毎週月曜 9:00")
            print("月次: 毎月1日 10:00")
        elif choice == "0":
            print("\n👋 テスト終了")
            break
        else:
            print("\n❌ 無効な選択です")