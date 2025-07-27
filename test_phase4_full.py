#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 4 全機能テストスクリプト（フル機能版）
"""

import sys
import subprocess
from pathlib import Path

def test_imports():
    """全依存ライブラリのテスト"""
    print("🔍 Phase 4 依存ライブラリテスト")
    print("=" * 40)
    
    libraries = {
        'PyQt6': 'PyQt6',
        'matplotlib': 'matplotlib',
        'pandas': 'pandas', 
        'numpy': 'numpy',
        'seaborn': 'seaborn',
        'scikit-learn': 'sklearn',
        'reportlab': 'reportlab',
        'openpyxl': 'openpyxl',
        'apscheduler': 'apscheduler'
    }
    
    missing = []
    for name, module in libraries.items():
        try:
            __import__(module)
            print(f"✅ {name}: インストール済み")
        except ImportError:
            print(f"❌ {name}: 未インストール")
            missing.append(name)
    
    if missing:
        print(f"\n❌ 不足: {', '.join(missing)}")
        return False
    else:
        print("\n🎉 全ライブラリインストール完了！")
        return True

def test_app_startup():
    """アプリケーション起動テスト"""
    print("\n🚀 アプリケーション起動テスト")
    print("=" * 40)
    
    app_path = Path("pomodoro_phase3_final_integrated_simple_break.py")
    if not app_path.exists():
        print("❌ アプリファイルが見つかりません")
        return False
    
    print("📱 アプリを起動しています...")
    print("⚠️ 起動後は手動で機能をテストしてください")
    print("\n📋 テスト手順:")
    print("1. 「分析・可視化」タブをクリック")
    print("2. ドロップダウンから「comprehensive」を選択")
    print("3. 「生成」ボタンをクリック")
    print("4. AI予測タブでAI機能をテスト")
    print("5. PDFエクスポート機能をテスト")
    
    input("\nEnterキーでアプリを起動...")
    
    try:
        subprocess.run([sys.executable, str(app_path)])
        return True
    except KeyboardInterrupt:
        print("\n👋 テスト終了")
        return True

def create_quick_test_data():
    """クイックテストデータ作成"""
    print("\n📊 追加テストデータを作成中...")
    
    import json
    from datetime import datetime, timedelta
    import random
    
    # より多くのテストデータを生成
    sessions = []
    base_date = datetime.now() - timedelta(days=30)  # 30日間分
    
    for day in range(30):
        date = base_date + timedelta(days=day)
        # 1日2-6セッション
        num_sessions = random.randint(2, 6)
        
        for session in range(num_sessions):
            session_time = date.replace(
                hour=random.randint(8, 18),
                minute=random.randint(0, 59)
            )
            
            # より現実的なデータを生成
            focus_score = random.uniform(50, 95)
            efficiency = focus_score + random.uniform(-15, 15)
            efficiency = max(30, min(100, efficiency))  # 30-100の範囲
            
            session_data = {
                "session_id": f"work_{session_time.strftime('%Y%m%d_%H%M%S')}",
                "type": "work",
                "planned_duration": 25,
                "start_time": session_time.isoformat(),
                "actual_duration": random.uniform(15, 25),
                "completed": random.random() > 0.15,  # 85%完了率
                "efficiency_score": efficiency,
                "focus_score": focus_score,
                "interruptions": random.randint(0, 4),
                "environment_data": {
                    "hour_of_day": session_time.hour,
                    "day_of_week": session_time.weekday(),
                    "time_period": "morning" if session_time.hour < 12 else "afternoon" if session_time.hour < 17 else "evening"
                }
            }
            sessions.append(session_data)
    
    # データファイルを更新
    data_path = Path("data/rich_test_data.json")
    data_path.parent.mkdir(exist_ok=True)
    
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump({
            "sessions": sessions,
            "generated_at": datetime.now().isoformat(),
            "total_sessions": len(sessions),
            "description": "30日間の豊富なテストデータ - Phase 4全機能テスト用"
        }, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {len(sessions)}個の豊富なテストセッションを生成")
    print(f"📁 保存場所: {data_path}")
    
    # 統計サマリー
    completed = sum(1 for s in sessions if s['completed'])
    avg_focus = sum(s['focus_score'] for s in sessions) / len(sessions)
    avg_efficiency = sum(s['efficiency_score'] for s in sessions) / len(sessions)
    
    print(f"\n📈 生成データ統計:")
    print(f"  - 期間: 30日間")
    print(f"  - 総セッション: {len(sessions)}")
    print(f"  - 完了率: {completed/len(sessions)*100:.1f}%")
    print(f"  - 平均集中度: {avg_focus:.1f}")
    print(f"  - 平均効率: {avg_efficiency:.1f}")

def main():
    print("🎯 Phase 4 フル機能テストスクリプト")
    print("=" * 50)
    
    # 1. ライブラリテスト
    if not test_imports():
        print("\n❌ 必要なライブラリがインストールされていません")
        print("以下のコマンドを実行してください:")
        print("pip install scikit-learn reportlab openpyxl apscheduler")
        return
    
    # 2. テストデータ作成
    create_quick_test_data()
    
    # 3. アプリケーション起動
    print("\n🚀 Phase 4 完全版でアプリを起動します")
    print("全ての高度統計機能が利用可能です！")
    
    test_app_startup()

if __name__ == "__main__":
    main()