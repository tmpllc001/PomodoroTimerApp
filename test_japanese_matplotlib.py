#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Matplotlib日本語表示テストスクリプト
"""

import matplotlib
matplotlib.use('Agg')  # バックエンド設定（GUIなし）
import matplotlib.pyplot as plt
import platform
import sys

def setup_japanese_font():
    """日本語フォントの設定"""
    system = platform.system()
    
    if system == 'Windows':
        plt.rcParams['font.family'] = ['MS Gothic', 'Yu Gothic', 'Meiryo', 'sans-serif']
    elif system == 'Darwin':  # macOS
        plt.rcParams['font.family'] = ['Hiragino Sans', 'Hiragino Kaku Gothic Pro', 'sans-serif']
    else:  # Linux
        plt.rcParams['font.family'] = ['Noto Sans CJK JP', 'IPAGothic', 'TakaoGothic', 'sans-serif']
    
    plt.rcParams['axes.unicode_minus'] = False

def test_japanese_plot():
    """日本語グラフのテスト"""
    print("📊 Matplotlib日本語表示テスト")
    print(f"🖥️ OS: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")
    print(f"📦 Matplotlib: {matplotlib.__version__}")
    
    # フォント設定
    setup_japanese_font()
    
    # テストデータ
    categories = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日']
    work_sessions = [8, 6, 7, 5, 9]
    break_sessions = [4, 3, 4, 3, 5]
    
    # グラフ作成
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # 棒グラフ
    x = range(len(categories))
    width = 0.35
    ax1.bar([i - width/2 for i in x], work_sessions, width, label='作業セッション', color='#4CAF50')
    ax1.bar([i + width/2 for i in x], break_sessions, width, label='休憩セッション', color='#FF9800')
    ax1.set_xlabel('曜日')
    ax1.set_ylabel('セッション数')
    ax1.set_title('週間ポモドーロ統計')
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 円グラフ
    task_types = ['プログラミング', '会議', 'メール処理', '資料作成', 'その他']
    task_hours = [35, 15, 10, 25, 15]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    
    ax2.pie(task_hours, labels=task_types, colors=colors, autopct='%1.1f%%', startangle=90)
    ax2.set_title('タスク別時間配分')
    
    plt.tight_layout()
    
    # ファイルに保存
    output_file = 'test_japanese_matplotlib.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✅ テストグラフを保存しました: {output_file}")
    
    # 使用可能なフォントをリスト
    print("\n📝 現在の設定:")
    print(f"  フォントファミリー: {plt.rcParams['font.family']}")
    print(f"  マイナス記号: {plt.rcParams['axes.unicode_minus']}")
    
    # matplotlibで利用可能な日本語フォントを検索
    import matplotlib.font_manager as fm
    print("\n🔍 利用可能な日本語フォント:")
    japanese_fonts = []
    for font in fm.fontManager.ttflist:
        if any(jp in font.name for jp in ['Gothic', 'Mincho', 'Meiryo', 'Yu', 'Hiragino', 'Noto', 'IPA', 'Takao']):
            if font.name not in japanese_fonts:
                japanese_fonts.append(font.name)
    
    for font in sorted(japanese_fonts)[:10]:  # 最初の10個のみ表示
        print(f"  - {font}")
    
    if len(japanese_fonts) > 10:
        print(f"  ... 他 {len(japanese_fonts) - 10} フォント")

if __name__ == '__main__':
    test_japanese_plot()