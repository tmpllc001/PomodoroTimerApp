#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統計表示ウィジェット
PyQt6を使用した統計データの表示
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTabWidget, QFrame, QScrollArea, QProgressBar,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .statistics import PomodoroStatistics

logger = logging.getLogger(__name__)


class StatsCard(QFrame):
    """統計情報カード"""
    
    def __init__(self, title: str, value: str, subtitle: str = ""):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # タイトル
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #6c757d;")
        
        # 値
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #495057;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        # サブタイトル
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            subtitle_label.setStyleSheet("font-size: 10px; color: #6c757d;")
            layout.addWidget(subtitle_label)
        
        self.setLayout(layout)
        
        # 値を更新するためのラベル参照を保持
        self.value_label = value_label
    
    def update_value(self, value: str):
        """値を更新"""
        self.value_label.setText(value)


class ProductivityMeter(QWidget):
    """生産性メーター"""
    
    def __init__(self):
        super().__init__()
        self.setupUI()
        self.score = 0.0
    
    def setupUI(self):
        layout = QVBoxLayout()
        
        # タイトル
        title = QLabel("生産性スコア")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
        
        # プログレスバー
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #dee2e6;
                border-radius: 10px;
                text-align: center;
                background-color: #f8f9fa;
            }
            QProgressBar::chunk {
                background-color: #28a745;
                border-radius: 8px;
            }
        """)
        
        # スコアラベル
        self.score_label = QLabel("0%")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #495057;")
        
        layout.addWidget(title)
        layout.addWidget(self.progress)
        layout.addWidget(self.score_label)
        
        self.setLayout(layout)
    
    def update_score(self, score: float):
        """スコアを更新"""
        self.score = score
        self.progress.setValue(int(score))
        self.score_label.setText(f"{score:.1f}%")
        
        # スコアに応じて色を変更
        if score >= 80:
            color = "#28a745"  # 緑
        elif score >= 60:
            color = "#ffc107"  # 黄
        elif score >= 40:
            color = "#fd7e14"  # オレンジ
        else:
            color = "#dc3545"  # 赤
        
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid #dee2e6;
                border-radius: 10px;
                text-align: center;
                background-color: #f8f9fa;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 8px;
            }}
        """)


class SessionHistoryTable(QTableWidget):
    """セッション履歴テーブル"""
    
    def __init__(self):
        super().__init__()
        self.setupUI()
    
    def setupUI(self):
        # カラム設定
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["時刻", "タイプ", "時間", "完了"])
        
        # ヘッダー設定
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)
        
        # スタイル
        self.setStyleSheet("""
            QTableWidget {
                gridline-color: #dee2e6;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QHeaderView::section {
                background-color: #e9ecef;
                padding: 5px;
                border: 1px solid #dee2e6;
                font-weight: bold;
            }
        """)
        
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    
    def update_sessions(self, sessions: List[Dict]):
        """セッションデータを更新"""
        self.setRowCount(len(sessions))
        
        for row, session in enumerate(sessions):
            # 時刻
            time_str = datetime.fromisoformat(session['timestamp']).strftime('%H:%M')
            self.setItem(row, 0, QTableWidgetItem(time_str))
            
            # タイプ
            type_str = "作業" if session['type'] == 'work' else "休憩"
            self.setItem(row, 1, QTableWidgetItem(type_str))
            
            # 時間
            duration_str = f"{session['duration']}分"
            self.setItem(row, 2, QTableWidgetItem(duration_str))
            
            # 完了
            completed_str = "✓" if session.get('completed', True) else "✗"
            self.setItem(row, 3, QTableWidgetItem(completed_str))


class StatsWidget(QWidget):
    """統計表示メインウィジェット"""
    
    # シグナル定義
    refresh_requested = pyqtSignal()
    
    def __init__(self, statistics: Optional[PomodoroStatistics] = None):
        super().__init__()
        self.statistics = statistics or PomodoroStatistics()
        self.setupUI()
        self.setupTimer()
        self.refresh_stats()
    
    def setupUI(self):
        """UI初期化"""
        layout = QVBoxLayout()
        
        # タイトル
        title = QLabel("📊 統計ダッシュボード")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        
        # 今日の統計タブ
        self.today_tab = self.create_today_tab()
        self.tab_widget.addTab(self.today_tab, "今日")
        
        # 週間統計タブ
        self.week_tab = self.create_week_tab()
        self.tab_widget.addTab(self.week_tab, "今週")
        
        # 全体統計タブ
        self.total_tab = self.create_total_tab()
        self.tab_widget.addTab(self.total_tab, "全体")
        
        # 履歴タブ
        self.history_tab = self.create_history_tab()
        self.tab_widget.addTab(self.history_tab, "履歴")
        
        layout.addWidget(self.tab_widget)
        
        # 更新ボタン
        refresh_label = QLabel("自動更新: 30秒間隔")
        refresh_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        refresh_label.setStyleSheet("font-size: 10px; color: #6c757d; margin: 5px;")
        layout.addWidget(refresh_label)
        
        self.setLayout(layout)
    
    def create_today_tab(self) -> QWidget:
        """今日の統計タブ作成"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 統計カード
        cards_layout = QHBoxLayout()
        
        self.today_work_card = StatsCard("作業セッション", "0", "回")
        self.today_work_time_card = StatsCard("作業時間", "0分", "")
        self.today_break_time_card = StatsCard("休憩時間", "0分", "")
        
        cards_layout.addWidget(self.today_work_card)
        cards_layout.addWidget(self.today_work_time_card)
        cards_layout.addWidget(self.today_break_time_card)
        
        layout.addLayout(cards_layout)
        
        # 生産性メーター
        self.productivity_meter = ProductivityMeter()
        layout.addWidget(self.productivity_meter)
        
        widget.setLayout(layout)
        return widget
    
    def create_week_tab(self) -> QWidget:
        """週間統計タブ作成"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 統計カード
        cards_layout = QHBoxLayout()
        
        self.week_work_card = StatsCard("作業セッション", "0", "回")
        self.week_work_time_card = StatsCard("作業時間", "0分", "")
        self.week_break_time_card = StatsCard("休憩時間", "0分", "")
        
        cards_layout.addWidget(self.week_work_card)
        cards_layout.addWidget(self.week_work_time_card)
        cards_layout.addWidget(self.week_break_time_card)
        
        layout.addLayout(cards_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_total_tab(self) -> QWidget:
        """全体統計タブ作成"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 統計カード
        cards_layout = QHBoxLayout()
        
        self.total_sessions_card = StatsCard("総セッション", "0", "回")
        self.total_work_time_card = StatsCard("総作業時間", "0時間", "")
        self.total_time_card = StatsCard("総時間", "0時間", "")
        
        cards_layout.addWidget(self.total_sessions_card)
        cards_layout.addWidget(self.total_work_time_card)
        cards_layout.addWidget(self.total_time_card)
        
        layout.addLayout(cards_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_history_tab(self) -> QWidget:
        """履歴タブ作成"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # セッション履歴テーブル
        self.history_table = SessionHistoryTable()
        layout.addWidget(self.history_table)
        
        widget.setLayout(layout)
        return widget
    
    def setupTimer(self):
        """更新タイマー設定"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_stats)
        self.refresh_timer.start(30000)  # 30秒間隔
    
    def refresh_stats(self):
        """統計データを更新"""
        try:
            # 今日の統計
            today_stats = self.statistics.get_today_stats()
            self.today_work_card.update_value(str(today_stats['work_sessions']))
            self.today_work_time_card.update_value(
                self.statistics.format_time(today_stats['work_time'])
            )
            self.today_break_time_card.update_value(
                self.statistics.format_time(today_stats['break_time'])
            )
            
            # 生産性スコア
            productivity_score = self.statistics.get_productivity_score()
            self.productivity_meter.update_score(productivity_score)
            
            # 週間統計
            week_stats = self.statistics.get_week_stats()
            self.week_work_card.update_value(str(week_stats['work_sessions']))
            self.week_work_time_card.update_value(
                self.statistics.format_time(week_stats['work_time'])
            )
            self.week_break_time_card.update_value(
                self.statistics.format_time(week_stats['break_time'])
            )
            
            # 全体統計
            total_stats = self.statistics.get_total_stats()
            self.total_sessions_card.update_value(str(total_stats['total_sessions']))
            self.total_work_time_card.update_value(
                self.statistics.format_time(total_stats['total_work_time'])
            )
            self.total_time_card.update_value(
                self.statistics.format_time(total_stats['total_time'])
            )
            
            # 履歴
            recent_sessions = self.statistics.get_recent_sessions(20)
            self.history_table.update_sessions(recent_sessions)
            
            logger.debug("📊 統計データ更新完了")
            
        except Exception as e:
            logger.error(f"📊 統計データ更新エラー: {e}")
    
    def set_statistics(self, statistics: PomodoroStatistics):
        """統計オブジェクトを設定"""
        self.statistics = statistics
        self.refresh_stats()
    
    def cleanup(self):
        """クリーンアップ"""
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()