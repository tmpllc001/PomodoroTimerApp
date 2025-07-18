#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統計可視化機能
matplotlib/plotlyを使用したグラフ生成
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class StatsVisualizer:
    """統計データの可視化を行うクラス"""
    
    def __init__(self, data_file: str = "data/statistics.json"):
        self.data_file = Path(data_file)
        self.df = None
        self.load_data()
        
        # 日本語フォント設定（利用可能な場合）
        self.setup_japanese_font()
        
    def setup_japanese_font(self):
        """日本語フォントの設定"""
        try:
            # Windows環境での日本語フォント設定
            import matplotlib.font_manager as fm
            
            # 利用可能なフォントを確認
            font_paths = [
                "C:/Windows/Fonts/msgothic.ttc",  # MS Gothic
                "C:/Windows/Fonts/meiryo.ttc",    # Meiryo
                "C:/Windows/Fonts/NotoSansCJK-Regular.ttc"  # Noto Sans CJK
            ]
            
            for font_path in font_paths:
                if Path(font_path).exists():
                    plt.rcParams['font.family'] = fm.FontProperties(fname=font_path).get_name()
                    logger.info(f"✅ 日本語フォント設定: {font_path}")
                    break
            else:
                logger.warning("⚠️  日本語フォントが見つかりません")
                
        except Exception as e:
            logger.warning(f"⚠️  フォント設定エラー: {e}")
            
    def load_data(self):
        """統計データの読み込み"""
        try:
            if not self.data_file.exists():
                logger.warning(f"⚠️  データファイルが見つかりません: {self.data_file}")
                self.df = pd.DataFrame()
                return
                
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # セッションデータをDataFrameに変換
            sessions = data.get('sessions', [])
            if not sessions:
                logger.warning("⚠️  セッションデータがありません")
                self.df = pd.DataFrame()
                return
                
            # DataFrameを作成
            self.df = pd.DataFrame(sessions)
            
            # 日時データを変換
            self.df['start_time'] = pd.to_datetime(self.df['start_time'])
            self.df['end_time'] = pd.to_datetime(self.df['end_time'])
            self.df['date'] = self.df['start_time'].dt.date
            
            logger.info(f"📊 統計データ読み込み完了: {len(self.df)}セッション")
            
        except Exception as e:
            logger.error(f"❌ データ読み込みエラー: {e}")
            self.df = pd.DataFrame()
            
    def create_daily_chart(self, days: int = 7) -> Figure:
        """日別セッション数のグラフを作成"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        if self.df.empty:
            ax1.text(0.5, 0.5, 'データがありません', ha='center', va='center', 
                    transform=ax1.transAxes, fontsize=16)
            ax2.text(0.5, 0.5, 'データがありません', ha='center', va='center', 
                    transform=ax2.transAxes, fontsize=16)
            return fig
            
        # 過去N日間のデータを取得
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # 日付範囲を作成
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # 日別集計
        daily_stats = self.df[self.df['date'].isin(date_range.date)].groupby(['date', 'session_type']).agg({
            'session_id': 'count',
            'actual_duration': 'sum'
        }).reset_index()
        
        # ピボットテーブルを作成
        session_pivot = daily_stats.pivot(index='date', columns='session_type', values='session_id').fillna(0)
        time_pivot = daily_stats.pivot(index='date', columns='session_type', values='actual_duration').fillna(0)
        
        # 全ての日付を含むようにreindex
        session_pivot = session_pivot.reindex(date_range.date, fill_value=0)
        time_pivot = time_pivot.reindex(date_range.date, fill_value=0)
        
        # セッション数のグラフ
        ax1.bar(session_pivot.index, session_pivot.get('work', 0), label='作業', color='#3498db', alpha=0.8)
        ax1.bar(session_pivot.index, session_pivot.get('break', 0), 
                bottom=session_pivot.get('work', 0), label='休憩', color='#2ecc71', alpha=0.8)
        
        ax1.set_title(f'過去{days}日間のセッション数', fontsize=14, fontweight='bold')
        ax1.set_ylabel('セッション数')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 時間のグラフ
        ax2.bar(time_pivot.index, time_pivot.get('work', 0), label='作業時間', color='#e74c3c', alpha=0.8)
        ax2.bar(time_pivot.index, time_pivot.get('break', 0), 
                bottom=time_pivot.get('work', 0), label='休憩時間', color='#f39c12', alpha=0.8)
        
        ax2.set_title(f'過去{days}日間の作業時間 (分)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('時間 (分)')
        ax2.set_xlabel('日付')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # X軸の日付フォーマット
        for ax in [ax1, ax2]:
            ax.tick_params(axis='x', rotation=45)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            
        plt.tight_layout()
        return fig
        
    def create_weekly_chart(self, weeks: int = 4) -> Figure:
        """週別統計のグラフを作成"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if self.df.empty:
            ax.text(0.5, 0.5, 'データがありません', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=16)
            return fig
            
        # 週別集計
        self.df['week'] = self.df['start_time'].dt.isocalendar().week
        self.df['year'] = self.df['start_time'].dt.year
        self.df['week_key'] = self.df['year'].astype(str) + '-W' + self.df['week'].astype(str).str.zfill(2)
        
        weekly_stats = self.df.groupby(['week_key', 'session_type']).agg({
            'session_id': 'count',
            'actual_duration': 'sum'
        }).reset_index()
        
        # 作業時間のみでグラフを作成
        work_stats = weekly_stats[weekly_stats['session_type'] == 'work']
        
        if not work_stats.empty:
            ax.bar(work_stats['week_key'], work_stats['actual_duration'], 
                   color='#3498db', alpha=0.8, label='作業時間')
            
            # トレンドラインを追加
            x_pos = range(len(work_stats))
            z = np.polyfit(x_pos, work_stats['actual_duration'], 1)
            p = np.poly1d(z)
            ax.plot(x_pos, p(x_pos), "r--", alpha=0.8, label='トレンド')
            
        ax.set_title('週別作業時間の推移', fontsize=14, fontweight='bold')
        ax.set_ylabel('作業時間 (分)')
        ax.set_xlabel('週')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return fig
        
    def create_hourly_heatmap(self) -> Figure:
        """時間別作業パターンのヒートマップ"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        if self.df.empty:
            ax.text(0.5, 0.5, 'データがありません', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=16)
            return fig
            
        # 時間と曜日を取得
        work_sessions = self.df[self.df['session_type'] == 'work'].copy()
        work_sessions['hour'] = work_sessions['start_time'].dt.hour
        work_sessions['weekday'] = work_sessions['start_time'].dt.day_name()
        
        # 時間別・曜日別の集計
        heatmap_data = work_sessions.groupby(['weekday', 'hour']).size().unstack(fill_value=0)
        
        # 曜日の順序を設定
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_data = heatmap_data.reindex(weekday_order, fill_value=0)
        
        # ヒートマップを作成
        im = ax.imshow(heatmap_data.values, cmap='YlOrRd', aspect='auto')
        
        # カラーバーを追加
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('セッション数', rotation=270, labelpad=20)
        
        # 軸ラベルを設定
        ax.set_xticks(range(24))
        ax.set_xticklabels([f'{h:02d}:00' for h in range(24)])
        ax.set_yticks(range(len(weekday_order)))
        ax.set_yticklabels(['月', '火', '水', '木', '金', '土', '日'])
        
        ax.set_title('時間別作業パターン', fontsize=14, fontweight='bold')
        ax.set_xlabel('時間')
        ax.set_ylabel('曜日')
        
        # 値をヒートマップに表示
        for i in range(len(weekday_order)):
            for j in range(24):
                value = heatmap_data.iloc[i, j] if j < len(heatmap_data.columns) else 0
                if value > 0:
                    ax.text(j, i, str(int(value)), ha='center', va='center', 
                           color='white' if value > heatmap_data.values.max() * 0.7 else 'black')
                    
        plt.tight_layout()
        return fig
        
    def create_productivity_chart(self) -> Figure:
        """生産性指標のグラフ"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        if self.df.empty:
            for ax in [ax1, ax2]:
                ax.text(0.5, 0.5, 'データがありません', ha='center', va='center', 
                       transform=ax.transAxes, fontsize=16)
            return fig
            
        # 完了率の計算
        completion_stats = self.df.groupby('date').agg({
            'completed': ['count', 'sum'],
            'session_id': 'count'
        }).reset_index()
        
        completion_stats.columns = ['date', 'total_sessions', 'completed_sessions', 'session_count']
        completion_stats['completion_rate'] = (completion_stats['completed_sessions'] / 
                                               completion_stats['total_sessions'] * 100)
        
        # 完了率のグラフ
        ax1.plot(completion_stats['date'], completion_stats['completion_rate'], 
                 marker='o', linewidth=2, markersize=6, color='#2ecc71')
        ax1.axhline(y=100, color='r', linestyle='--', alpha=0.7, label='目標 (100%)')
        ax1.set_title('セッション完了率の推移', fontsize=14, fontweight='bold')
        ax1.set_ylabel('完了率 (%)')
        ax1.set_xlabel('日付')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # 平均セッション時間
        avg_duration = self.df.groupby('date')['actual_duration'].mean().reset_index()
        ax2.bar(avg_duration['date'], avg_duration['actual_duration'], 
                color='#3498db', alpha=0.8)
        ax2.axhline(y=25, color='r', linestyle='--', alpha=0.7, label='目標 (25分)')
        ax2.set_title('平均セッション時間', fontsize=14, fontweight='bold')
        ax2.set_ylabel('平均時間 (分)')
        ax2.set_xlabel('日付')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return fig
        
    def export_chart(self, figure: Figure, filename: str, format: str = 'png'):
        """グラフを画像ファイルとして保存"""
        try:
            output_dir = Path("exports")
            output_dir.mkdir(exist_ok=True)
            
            filepath = output_dir / f"{filename}.{format}"
            figure.savefig(filepath, dpi=300, bbox_inches='tight')
            logger.info(f"📊 グラフ保存完了: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ グラフ保存エラー: {e}")
            return None
            
    def get_summary_stats(self) -> Dict:
        """統計サマリーを取得"""
        if self.df.empty:
            return {
                'total_sessions': 0,
                'total_work_time': 0,
                'total_break_time': 0,
                'average_session_length': 0,
                'completion_rate': 0,
                'best_day': None,
                'most_productive_hour': None
            }
            
        work_sessions = self.df[self.df['session_type'] == 'work']
        break_sessions = self.df[self.df['session_type'] == 'break']
        
        # 最も生産的な時間帯を計算
        if not work_sessions.empty:
            hourly_counts = work_sessions['start_time'].dt.hour.value_counts()
            most_productive_hour = hourly_counts.index[0] if not hourly_counts.empty else None
        else:
            most_productive_hour = None
            
        # 最も良い日を計算
        daily_work_time = work_sessions.groupby('date')['actual_duration'].sum()
        best_day = daily_work_time.idxmax() if not daily_work_time.empty else None
        
        return {
            'total_sessions': len(self.df),
            'total_work_time': work_sessions['actual_duration'].sum(),
            'total_break_time': break_sessions['actual_duration'].sum(),
            'average_session_length': self.df['actual_duration'].mean(),
            'completion_rate': (self.df['completed'].sum() / len(self.df) * 100) if len(self.df) > 0 else 0,
            'best_day': best_day.strftime('%Y-%m-%d') if best_day else None,
            'most_productive_hour': f"{most_productive_hour:02d}:00" if most_productive_hour is not None else None
        }

# Qt用のグラフウィジェット
class StatsCanvas(FigureCanvas):
    """matplotlibのFigureをQtウィジェットとして表示"""
    
    def __init__(self, figure: Figure, parent=None):
        super().__init__(figure)
        self.setParent(parent)
        self.figure = figure
        
    def update_figure(self, new_figure: Figure):
        """新しいFigureで表示を更新"""
        self.figure.clear()
        # 新しいFigureの内容をコピー
        for i, ax in enumerate(new_figure.axes):
            new_ax = self.figure.add_subplot(len(new_figure.axes), 1, i+1)
            # 軸の内容をコピー（簡略化）
            new_ax.clear()
            
        self.draw()