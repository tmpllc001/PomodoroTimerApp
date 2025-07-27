#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統計可視化機能
matplotlib強制使用版
"""

# matplotlib強制使用
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
import numpy as np
HAS_MATPLOTLIB = True

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# matplotlib使用のStatsVisualizerクラス

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
        duration_pivot = daily_stats.pivot(index='date', columns='session_type', values='actual_duration').fillna(0)
        
        # 全日付で統一（データがない日は0）
        session_pivot = session_pivot.reindex(date_range.date, fill_value=0)
        duration_pivot = duration_pivot.reindex(date_range.date, fill_value=0)
        
        # グラフ1: セッション数
        ax1.bar(range(len(session_pivot.index)), session_pivot.get('work', 0), 
               alpha=0.7, label='作業セッション', color='#3498db')
        ax1.bar(range(len(session_pivot.index)), session_pivot.get('break', 0), 
               bottom=session_pivot.get('work', 0), alpha=0.7, label='休憩セッション', color='#2ecc71')
        
        ax1.set_title(f'過去{days}日間の日別セッション数')
        ax1.set_xlabel('日付')
        ax1.set_ylabel('セッション数')
        ax1.legend()
        ax1.set_xticks(range(len(session_pivot.index)))
        ax1.set_xticklabels([d.strftime('%m/%d') for d in session_pivot.index], rotation=45)
        ax1.grid(True, alpha=0.3)
        
        # グラフ2: 作業時間
        ax2.bar(range(len(duration_pivot.index)), 
               duration_pivot.get('work', 0) / 60,  # 分に変換
               alpha=0.7, label='作業時間', color='#e74c3c')
        
        ax2.set_title(f'過去{days}日間の日別作業時間')
        ax2.set_xlabel('日付')
        ax2.set_ylabel('作業時間（分）')
        ax2.legend()
        ax2.set_xticks(range(len(duration_pivot.index)))
        ax2.set_xticklabels([d.strftime('%m/%d') for d in duration_pivot.index], rotation=45)
        ax2.grid(True, alpha=0.3)
        
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
        work_df = self.df[self.df['session_type'] == 'work'].copy()
        work_df['week'] = work_df['start_time'].dt.to_period('W')
        
        weekly_stats = work_df.groupby('week').agg({
            'session_id': 'count',
            'actual_duration': 'sum'
        }).reset_index()
        
        # 最新のN週間
        weekly_stats = weekly_stats.tail(weeks)
        
        # グラフ作成
        x_pos = range(len(weekly_stats))
        ax.bar(x_pos, weekly_stats['actual_duration'] / 60, alpha=0.7, color='#9b59b6')
        
        ax.set_title(f'過去{weeks}週間の週別作業時間')
        ax.set_xlabel('週')
        ax.set_ylabel('作業時間（分）')
        ax.set_xticks(x_pos)
        ax.set_xticklabels([str(w) for w in weekly_stats['week']], rotation=45)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
        
    def create_heatmap_chart(self) -> Figure:
        """時間帯×曜日のヒートマップを作成"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        if self.df.empty:
            ax.text(0.5, 0.5, 'データがありません', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=16)
            return fig
            
        # 作業セッションのみ
        work_df = self.df[self.df['session_type'] == 'work'].copy()
        
        # 時間帯と曜日を追加
        work_df['hour'] = work_df['start_time'].dt.hour
        work_df['weekday'] = work_df['start_time'].dt.dayofweek
        
        # ヒートマップデータを作成
        heatmap_data = np.zeros((24, 7))
        
        for _, row in work_df.iterrows():
            heatmap_data[row['hour'], row['weekday']] += 1
            
        # ヒートマップを描画
        im = ax.imshow(heatmap_data, cmap='YlOrRd', aspect='auto')
        
        # 軸設定
        ax.set_xticks(range(7))
        ax.set_xticklabels(['月', '火', '水', '木', '金', '土', '日'])
        ax.set_yticks(range(0, 24, 2))
        ax.set_yticklabels([f'{h:02d}:00' for h in range(0, 24, 2)])
        
        ax.set_title('時間帯別活動ヒートマップ')
        ax.set_xlabel('曜日')
        ax.set_ylabel('時間帯')
        
        # カラーバー
        plt.colorbar(im, ax=ax, label='セッション数')
        
        plt.tight_layout()
        return fig
        
    def create_productivity_chart(self) -> Figure:
        """時間帯別生産性グラフを作成"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if self.df.empty:
            ax.text(0.5, 0.5, 'データがありません', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=16)
            return fig
            
        # 作業セッションのみ
        work_df = self.df[self.df['session_type'] == 'work'].copy()
        work_df['hour'] = work_df['start_time'].dt.hour
        
        # 時間帯別平均作業時間
        hourly_avg = work_df.groupby('hour')['actual_duration'].mean() / 60  # 分に変換
        
        # グラフ作成
        ax.plot(hourly_avg.index, hourly_avg.values, marker='o', linewidth=2, markersize=6, color='#e67e22')
        ax.fill_between(hourly_avg.index, hourly_avg.values, alpha=0.3, color='#e67e22')
        
        ax.set_title('時間帯別平均セッション時間')
        ax.set_xlabel('時間帯')
        ax.set_ylabel('平均セッション時間（分）')
        ax.set_xticks(range(0, 24, 2))
        ax.set_xticklabels([f'{h:02d}:00' for h in range(0, 24, 2)])
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
        
    def save_chart(self, figure: Figure, filepath: str, dpi: int = 300) -> Optional[str]:
        """グラフを画像ファイルとして保存"""
        try:
            figure.savefig(filepath, dpi=dpi, bbox_inches='tight')
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
            
        # 最も生産的な日を計算
        if not work_sessions.empty:
            daily_work_time = work_sessions.groupby('date')['actual_duration'].sum()
            best_day = daily_work_time.idxmax() if not daily_work_time.empty else None
        else:
            best_day = None
            
        total_sessions = len(self.df)
        completed_sessions = sum(self.df.get('completed', [False] * len(self.df)))
        
        return {
            'total_sessions': total_sessions,
            'total_work_time': work_sessions['actual_duration'].sum() if not work_sessions.empty else 0,
            'total_break_time': break_sessions['actual_duration'].sum() if not break_sessions.empty else 0,
            'average_session_length': self.df['actual_duration'].mean() if not self.df.empty else 0,
            'completion_rate': (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0,
            'best_day': str(best_day) if best_day else None,
            'most_productive_hour': f"{most_productive_hour:02d}:00" if most_productive_hour is not None else None
        }

# matplotlib使用のQt用グラフウィジェット
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