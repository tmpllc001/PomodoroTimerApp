#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統計ダッシュボードウィジェット
PyQt6を使用したダッシュボードUI
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                           QLabel, QPushButton, QComboBox, QGroupBox,
                           QScrollArea, QGridLayout, QFrame, QFileDialog,
                           QMessageBox, QProgressBar, QSpinBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QRect
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QPen, QBrush

# matplotlib 強制使用
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
HAS_MATPLOTLIB = True

from .stats_visualizer import StatsVisualizer
from typing import Dict, Optional, List, Tuple
import logging
from pathlib import Path
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SimpleChartWidget(QWidget):
    """matplotlib代替の簡易チャートウィジェット"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chart_type = ""
        self.chart_data = {}
        self.setMinimumSize(800, 600)
        self.setStyleSheet("background-color: white;")
        
    def set_chart_data(self, chart_type: str, data: Dict):
        """チャートデータを設定"""
        self.chart_type = chart_type
        self.chart_data = data
        self.update()  # 再描画
        
    def paintEvent(self, event):
        """QPainterでグラフ描画"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 背景を白で塗りつぶし
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        # 枠線を描画
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        
        # チャートタイプに応じて描画
        if self.chart_type == "daily":
            self._draw_daily_chart(painter)
        elif self.chart_type == "weekly":
            self._draw_weekly_chart(painter)
        elif self.chart_type == "heatmap":
            self._draw_heatmap(painter)
        elif self.chart_type == "productivity":
            self._draw_productivity_chart(painter)
        elif self.chart_type == "error":
            self._draw_error_message(painter)
        else:
            self._draw_no_data(painter)
            
    def _draw_daily_chart(self, painter: QPainter):
        """日別チャートを描画"""
        if not self.chart_data:
            self._draw_no_data(painter)
            return
            
        # マージンを設定
        margin = 60
        width = self.width() - 2 * margin
        height = self.height() - 2 * margin
        
        # タイトルを描画
        painter.setPen(QPen(QColor(44, 62, 80), 2))
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.drawText(QRect(0, 10, self.width(), 30), Qt.AlignmentFlag.AlignCenter, 
                        self.chart_data.get('title', '日別統計'))
        
        # データを取得
        dates = self.chart_data.get('dates', [])
        work_sessions = self.chart_data.get('work_sessions', [])
        break_sessions = self.chart_data.get('break_sessions', [])
        
        if not dates:
            self._draw_no_data(painter)
            return
            
        # 最大値を計算
        max_value = max(max(work_sessions) if work_sessions else 0, 
                       max(break_sessions) if break_sessions else 0, 1)
        
        # バーの幅を計算
        bar_width = width / len(dates) * 0.8
        spacing = width / len(dates) * 0.2
        
        # Y軸を描画
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.drawLine(margin, margin, margin, self.height() - margin)
        
        # X軸を描画
        painter.drawLine(margin, self.height() - margin, 
                        self.width() - margin, self.height() - margin)
        
        # Y軸ラベルを描画
        painter.setFont(QFont("Arial", 10))
        for i in range(6):
            y = margin + height * i / 5
            value = int(max_value * (5 - i) / 5)
            painter.drawText(QRect(5, int(y) - 10, margin - 10, 20), 
                           Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, 
                           str(value))
            # グリッド線
            painter.setPen(QPen(QColor(230, 230, 230), 1, Qt.PenStyle.DashLine))
            painter.drawLine(margin, int(y), self.width() - margin, int(y))
            painter.setPen(QPen(QColor(100, 100, 100), 1))
            
        # バーを描画
        for i, (date, work, brk) in enumerate(zip(dates, work_sessions, break_sessions)):
            x = margin + i * (bar_width + spacing) + spacing / 2
            
            # 作業セッション（青）
            if work > 0:
                work_height = height * work / max_value
                painter.fillRect(QRect(int(x), int(self.height() - margin - work_height), 
                                     int(bar_width / 2 - 2), int(work_height)), 
                               QColor(52, 152, 219, 200))
                
            # 休憩セッション（緑）
            if brk > 0:
                break_height = height * brk / max_value
                painter.fillRect(QRect(int(x + bar_width / 2), 
                                     int(self.height() - margin - break_height), 
                                     int(bar_width / 2 - 2), int(break_height)), 
                               QColor(46, 204, 113, 200))
                
            # X軸ラベル（日付）
            painter.setPen(QPen(QColor(100, 100, 100), 1))
            painter.setFont(QFont("Arial", 9))
            painter.save()
            painter.translate(x + bar_width / 2, self.height() - margin + 20)
            painter.rotate(45)
            painter.drawText(QRect(0, 0, 100, 20), Qt.AlignmentFlag.AlignLeft, date)
            painter.restore()
            
        # 凡例を描画
        self._draw_legend(painter, [("作業", QColor(52, 152, 219, 200)), 
                                   ("休憩", QColor(46, 204, 113, 200))])
                                   
    def _draw_weekly_chart(self, painter: QPainter):
        """週別チャートを描画"""
        if not self.chart_data:
            self._draw_no_data(painter)
            return
            
        # マージンを設定
        margin = 60
        width = self.width() - 2 * margin
        height = self.height() - 2 * margin
        
        # タイトルを描画
        painter.setPen(QPen(QColor(44, 62, 80), 2))
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.drawText(QRect(0, 10, self.width(), 30), Qt.AlignmentFlag.AlignCenter, 
                        self.chart_data.get('title', '週別統計'))
        
        # データを取得
        weeks = self.chart_data.get('weeks', [])
        values = self.chart_data.get('values', [])
        
        if not weeks:
            self._draw_no_data(painter)
            return
            
        # 最大値を計算
        max_value = max(values) if values else 1
        
        # バーの幅を計算
        bar_width = width / len(weeks) * 0.6
        spacing = width / len(weeks) * 0.4
        
        # 軸を描画
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.drawLine(margin, margin, margin, self.height() - margin)
        painter.drawLine(margin, self.height() - margin, 
                        self.width() - margin, self.height() - margin)
        
        # バーを描画
        for i, (week, value) in enumerate(zip(weeks, values)):
            x = margin + i * (bar_width + spacing) + spacing / 2
            bar_height = height * value / max_value
            
            painter.fillRect(QRect(int(x), int(self.height() - margin - bar_height), 
                                 int(bar_width), int(bar_height)), 
                           QColor(52, 152, 219, 200))
            
            # 値を表示
            painter.setPen(QPen(QColor(44, 62, 80), 1))
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            painter.drawText(QRect(int(x), int(self.height() - margin - bar_height - 20), 
                                 int(bar_width), 20), 
                           Qt.AlignmentFlag.AlignCenter, str(int(value)))
            
            # X軸ラベル
            painter.setFont(QFont("Arial", 9))
            painter.drawText(QRect(int(x), int(self.height() - margin + 5), 
                                 int(bar_width), 30), 
                           Qt.AlignmentFlag.AlignCenter, week)
                           
    def _draw_heatmap(self, painter: QPainter):
        """ヒートマップを描画"""
        if not self.chart_data:
            self._draw_no_data(painter)
            return
            
        # タイトルを描画
        painter.setPen(QPen(QColor(44, 62, 80), 2))
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.drawText(QRect(0, 10, self.width(), 30), Qt.AlignmentFlag.AlignCenter, 
                        self.chart_data.get('title', '時間別ヒートマップ'))
        
        # データを取得
        hours = self.chart_data.get('hours', list(range(24)))
        days = self.chart_data.get('days', ['月', '火', '水', '木', '金', '土', '日'])
        data = self.chart_data.get('data', [[0] * 24 for _ in range(7)])
        
        # マージンとセルサイズを計算
        margin = 60
        cell_width = (self.width() - 2 * margin) / 24
        cell_height = (self.height() - 2 * margin - 40) / 7
        
        # 最大値を計算
        max_value = max(max(row) for row in data) if data else 1
        
        # ヒートマップを描画
        for row, day_data in enumerate(data):
            for col, value in enumerate(day_data):
                x = margin + col * cell_width
                y = margin + 40 + row * cell_height
                
                # 色の濃さを計算
                intensity = int(255 * (1 - value / max_value)) if max_value > 0 else 255
                color = QColor(255, intensity, intensity)
                
                painter.fillRect(QRect(int(x), int(y), int(cell_width), int(cell_height)), color)
                
                # 値を表示（値が0より大きい場合）
                if value > 0:
                    painter.setPen(QPen(QColor(0, 0, 0) if intensity > 127 else QColor(255, 255, 255)))
                    painter.setFont(QFont("Arial", 8))
                    painter.drawText(QRect(int(x), int(y), int(cell_width), int(cell_height)), 
                                   Qt.AlignmentFlag.AlignCenter, str(int(value)))
                    
        # 軸ラベルを描画
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.setFont(QFont("Arial", 9))
        
        # 時間ラベル（X軸）
        for i, hour in enumerate(hours):
            x = margin + i * cell_width + cell_width / 2
            painter.drawText(QRect(int(x - 20), int(self.height() - margin + 10), 40, 20), 
                           Qt.AlignmentFlag.AlignCenter, f"{hour:02d}")
                           
        # 曜日ラベル（Y軸）
        for i, day in enumerate(days):
            y = margin + 40 + i * cell_height + cell_height / 2
            painter.drawText(QRect(5, int(y - 10), margin - 10, 20), 
                           Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, day)
                           
    def _draw_productivity_chart(self, painter: QPainter):
        """生産性チャートを描画"""
        if not self.chart_data:
            self._draw_no_data(painter)
            return
            
        # タイトルを描画
        painter.setPen(QPen(QColor(44, 62, 80), 2))
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.drawText(QRect(0, 10, self.width(), 30), Qt.AlignmentFlag.AlignCenter, 
                        self.chart_data.get('title', '生産性指標'))
        
        # データを取得
        completion_rate = self.chart_data.get('completion_rate', 0)
        avg_duration = self.chart_data.get('avg_duration', 0)
        total_sessions = self.chart_data.get('total_sessions', 0)
        
        # 円グラフエリア
        circle_x = self.width() // 4
        circle_y = self.height() // 2
        circle_radius = min(self.width() // 4, self.height() // 3) - 40
        
        # 完了率円グラフ
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.drawText(QRect(circle_x - circle_radius, circle_y - circle_radius - 40, 
                             circle_radius * 2, 30), 
                       Qt.AlignmentFlag.AlignCenter, "完了率")
        
        # 背景円
        painter.setBrush(QBrush(QColor(236, 240, 241)))
        painter.setPen(QPen(QColor(189, 195, 199), 2))
        painter.drawEllipse(circle_x - circle_radius, circle_y - circle_radius, 
                          circle_radius * 2, circle_radius * 2)
        
        # 完了率の扇形
        angle = int(completion_rate * 360 / 100)
        painter.setBrush(QBrush(QColor(46, 204, 113)))
        painter.setPen(QPen(QColor(39, 174, 96), 2))
        painter.drawPie(circle_x - circle_radius, circle_y - circle_radius, 
                       circle_radius * 2, circle_radius * 2, 90 * 16, -angle * 16)
        
        # パーセンテージ表示
        painter.setPen(QPen(QColor(44, 62, 80), 2))
        painter.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        painter.drawText(QRect(circle_x - circle_radius, circle_y - 20, 
                             circle_radius * 2, 40), 
                       Qt.AlignmentFlag.AlignCenter, f"{completion_rate:.1f}%")
        
        # 統計情報を右側に表示
        stats_x = self.width() // 2 + 50
        stats_y = 100
        
        painter.setFont(QFont("Arial", 12))
        stats_data = [
            ("総セッション数", f"{total_sessions}回"),
            ("平均セッション時間", f"{avg_duration:.1f}分"),
            ("目標達成率", f"{completion_rate:.1f}%")
        ]
        
        for i, (label, value) in enumerate(stats_data):
            y = stats_y + i * 60
            
            # ラベル
            painter.setPen(QPen(QColor(127, 140, 141)))
            painter.drawText(QRect(stats_x, y, 200, 25), Qt.AlignmentFlag.AlignLeft, label)
            
            # 値
            painter.setPen(QPen(QColor(44, 62, 80), 2))
            painter.setFont(QFont("Arial", 18, QFont.Weight.Bold))
            painter.drawText(QRect(stats_x, y + 25, 200, 30), Qt.AlignmentFlag.AlignLeft, value)
            painter.setFont(QFont("Arial", 12))
            
    def _draw_legend(self, painter: QPainter, items: List[Tuple[str, QColor]]):
        """凡例を描画"""
        legend_x = self.width() - 150
        legend_y = 60
        
        painter.setFont(QFont("Arial", 10))
        
        for i, (label, color) in enumerate(items):
            y = legend_y + i * 25
            
            # 色の四角
            painter.fillRect(QRect(legend_x, y, 15, 15), color)
            painter.setPen(QPen(QColor(100, 100, 100), 1))
            painter.drawRect(QRect(legend_x, y, 15, 15))
            
            # ラベル
            painter.drawText(QRect(legend_x + 20, y, 100, 20), 
                           Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, label)
                           
    def _draw_no_data(self, painter: QPainter):
        """データなしメッセージを描画"""
        painter.setPen(QPen(QColor(127, 140, 141), 2))
        painter.setFont(QFont("Arial", 16))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "データがありません")
        
    def _draw_error_message(self, painter: QPainter):
        """エラーメッセージを描画"""
        painter.setPen(QPen(QColor(231, 76, 60), 2))
        painter.setFont(QFont("Arial", 14))
        error_msg = self.chart_data.get('error', 'エラーが発生しました')
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, error_msg)

class ChartGeneratorThread(QThread):
    """バックグラウンドでグラフを生成するスレッド"""
    chartReady = pyqtSignal(object, str)  # figure or dict, chart_type
    simpleChartReady = pyqtSignal(str, dict)  # chart_type, data
    
    def __init__(self, visualizer, chart_type: str, **kwargs):
        super().__init__()
        self.visualizer = visualizer
        self.chart_type = chart_type
        self.kwargs = kwargs
        
    def run(self):
        """グラフ生成を実行"""
        try:
            # matplotlib使用でグラフ生成
            if self.chart_type == 'daily':
                days = self.kwargs.get('days', 7)
                figure = self.visualizer.create_daily_chart(days)
            elif self.chart_type == 'weekly':
                weeks = self.kwargs.get('weeks', 4)
                figure = self.visualizer.create_weekly_chart(weeks)
            elif self.chart_type == 'heatmap':
                figure = self.visualizer.create_heatmap_chart()
            elif self.chart_type == 'productivity':
                figure = self.visualizer.create_productivity_chart()
            else:
                figure = Figure()
                
            self.chartReady.emit(figure, self.chart_type)
                
        except Exception as e:
            logger.error(f"❌ グラフ生成エラー: {e}")
            # matplotlib使用時のエラー
            error_figure = Figure()
            ax = error_figure.add_subplot(111)
            ax.text(0.5, 0.5, f'エラー: {str(e)}', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12, color='red')
            self.chartReady.emit(error_figure, self.chart_type)

class StatsSummaryWidget(QWidget):
    """統計サマリー表示ウィジェット"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.visualizer = StatsVisualizer()
        self.setup_ui()
        self.update_stats()
        
    def setup_ui(self):
        """UI設定"""
        layout = QVBoxLayout(self)
        
        # タイトル
        title_label = QLabel("📊 統計サマリー")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 統計グリッド
        grid_layout = QGridLayout()
        
        # 統計項目を定義
        self.stat_labels = {}
        stats_config = [
            ('total_sessions', '総セッション数', '回'),
            ('total_work_time', '総作業時間', '分'),
            ('completion_rate', '完了率', '%'),
            ('average_session_length', '平均セッション時間', '分'),
            ('best_day', '最も生産的な日', ''),
            ('most_productive_hour', '最も生産的な時間', '')
        ]
        
        for i, (key, label, unit) in enumerate(stats_config):
            row = i // 2
            col = i % 2
            
            # 統計ボックス
            stat_box = QGroupBox(label)
            stat_box.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #3498db;
                    border-radius: 8px;
                    margin-top: 10px;
                    padding: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
            """)
            
            box_layout = QVBoxLayout(stat_box)
            
            # 値表示ラベル
            value_label = QLabel("0")
            value_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value_label.setStyleSheet("color: #2c3e50;")
            box_layout.addWidget(value_label)
            
            # 単位表示
            if unit:
                unit_label = QLabel(unit)
                unit_label.setFont(QFont("Arial", 12))
                unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                unit_label.setStyleSheet("color: #7f8c8d;")
                box_layout.addWidget(unit_label)
            
            self.stat_labels[key] = value_label
            grid_layout.addWidget(stat_box, row, col)
            
        layout.addLayout(grid_layout)
        
        # 更新ボタン
        refresh_btn = QPushButton("🔄 更新")
        refresh_btn.clicked.connect(self.update_stats)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addWidget(refresh_btn)
        
    def update_stats(self):
        """統計を更新"""
        try:
            # データを再読み込み
            self.visualizer.load_data()
            stats = self.visualizer.get_summary_stats()
            
            # 表示を更新
            self.stat_labels['total_sessions'].setText(str(stats['total_sessions']))
            self.stat_labels['total_work_time'].setText(str(int(stats['total_work_time'])))
            self.stat_labels['completion_rate'].setText(f"{stats['completion_rate']:.1f}")
            self.stat_labels['average_session_length'].setText(f"{stats['average_session_length']:.1f}")
            self.stat_labels['best_day'].setText(stats['best_day'] or 'なし')
            self.stat_labels['most_productive_hour'].setText(stats['most_productive_hour'] or 'なし')
            
            logger.info("📊 統計サマリー更新完了")
            
        except Exception as e:
            logger.error(f"❌ 統計更新エラー: {e}")

class DashboardWidget(QWidget):
    """メインダッシュボードウィジェット"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.visualizer = StatsVisualizer()
        self.current_charts = {}  # chart_type -> FigureCanvas
        self.setup_ui()
        
        # 自動更新タイマー
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self.refresh_current_chart)
        self.auto_refresh_timer.start(300000)  # 5分ごと
        
    def setup_ui(self):
        """UI設定"""
        layout = QVBoxLayout(self)
        
        # タイトル
        title_label = QLabel("📊 統計ダッシュボード")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title_label)
        
        # matplotlib状態表示
        # matplotlibが使用可能なのでこの分岐は不要
        if False:
            status_label = QLabel("⚠️ 簡易グラフモード（matplotlib未インストール）")
            status_label.setStyleSheet("color: #e67e22; font-style: italic; margin-bottom: 10px;")
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(status_label)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 各タブを設定
        self.setup_summary_tab()
        self.setup_charts_tab()
        self.setup_export_tab()
        
    def setup_summary_tab(self):
        """サマリータブ"""
        summary_widget = StatsSummaryWidget()
        self.tab_widget.addTab(summary_widget, "サマリー")
        
    def setup_charts_tab(self):
        """グラフタブ"""
        charts_widget = QWidget()
        layout = QVBoxLayout(charts_widget)
        
        # コントロールパネル
        control_panel = QGroupBox("グラフ設定")
        control_layout = QHBoxLayout(control_panel)
        
        # グラフ種類選択
        chart_type_label = QLabel("グラフの種類:")
        control_layout.addWidget(chart_type_label)
        
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems([
            "日別統計 (7日間)", "日別統計 (30日間)",
            "週別統計", "時間別ヒートマップ", "生産性指標"
        ])
        self.chart_type_combo.currentTextChanged.connect(self.on_chart_type_changed)
        control_layout.addWidget(self.chart_type_combo)
        
        # 更新ボタン
        refresh_btn = QPushButton("🔄 更新")
        refresh_btn.clicked.connect(self.refresh_current_chart)
        control_layout.addWidget(refresh_btn)
        
        # エクスポートボタン
        export_btn = QPushButton("💾 エクスポート")
        export_btn.clicked.connect(self.export_current_chart)
        control_layout.addWidget(export_btn)
        
        control_layout.addStretch()
        layout.addWidget(control_panel)
        
        # グラフ表示エリア
        self.chart_scroll = QScrollArea()
        self.chart_scroll.setWidgetResizable(True)
        self.chart_scroll.setMinimumHeight(400)
        
        # プレースホルダー
        placeholder = QLabel("グラフを選択してください")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: #7f8c8d; font-size: 16px;")
        self.chart_scroll.setWidget(placeholder)
        
        layout.addWidget(self.chart_scroll)
        
        # 進捗バー
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.tab_widget.addTab(charts_widget, "グラフ")
        
    def setup_export_tab(self):
        """エクスポートタブ"""
        export_widget = QWidget()
        layout = QVBoxLayout(export_widget)
        
        # エクスポート設定
        export_group = QGroupBox("エクスポート設定")
        export_layout = QGridLayout(export_group)
        
        # フォーマット選択
        format_label = QLabel("フォーマット:")
        export_layout.addWidget(format_label, 0, 0)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "PDF", "SVG", "JPG"])
        export_layout.addWidget(self.format_combo, 0, 1)
        
        # 解像度設定
        dpi_label = QLabel("解像度 (DPI):")
        export_layout.addWidget(dpi_label, 1, 0)
        
        self.dpi_spinbox = QSpinBox()
        self.dpi_spinbox.setRange(72, 600)
        self.dpi_spinbox.setValue(300)
        export_layout.addWidget(self.dpi_spinbox, 1, 1)
        
        # エクスポートボタン
        export_all_btn = QPushButton("📊 全グラフをエクスポート")
        export_all_btn.clicked.connect(self.export_all_charts)
        export_layout.addWidget(export_all_btn, 2, 0, 1, 2)
        
        layout.addWidget(export_group)
        
        # エクスポート履歴
        history_group = QGroupBox("エクスポート履歴")
        history_layout = QVBoxLayout(history_group)
        
        self.history_label = QLabel("エクスポート履歴はありません")
        self.history_label.setStyleSheet("color: #7f8c8d;")
        history_layout.addWidget(self.history_label)
        
        layout.addWidget(history_group)
        layout.addStretch()
        
        self.tab_widget.addTab(export_widget, "エクスポート")
        
    def on_chart_type_changed(self, text: str):
        """グラフ種類が変更された時の処理"""
        self.generate_chart(text)
        
    def generate_chart(self, chart_type_text: str):
        """グラフを生成"""
        try:
            # 進捗バーを表示
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # 無限進捗
            
            # チャートタイプを決定
            if "日別統計 (7日間)" in chart_type_text:
                chart_type = 'daily'
                kwargs = {'days': 7}
            elif "日別統計 (30日間)" in chart_type_text:
                chart_type = 'daily'
                kwargs = {'days': 30}
            elif "週別統計" in chart_type_text:
                chart_type = 'weekly'
                kwargs = {'weeks': 4}
            elif "時間別ヒートマップ" in chart_type_text:
                chart_type = 'heatmap'
                kwargs = {}
            elif "生産性指標" in chart_type_text:
                chart_type = 'productivity'
                kwargs = {}
            else:
                return
                
            # バックグラウンドでグラフを生成
            self.chart_thread = ChartGeneratorThread(self.visualizer, chart_type, **kwargs)
            # matplotlib使用可能：
                self.chart_thread.chartReady.connect(self.on_chart_ready)
            else:
                self.chart_thread.simpleChartReady.connect(self.on_simple_chart_ready)
            self.chart_thread.start()
            
        except Exception as e:
            logger.error(f"❌ グラフ生成開始エラー: {e}")
            self.progress_bar.setVisible(False)
            
    def on_chart_ready(self, figure: Figure, chart_type: str):
        """グラフが準備完了した時の処理"""
        try:
            # 進捗バーを非表示
            self.progress_bar.setVisible(False)
            
            # 既存のキャンバスを削除
            if chart_type in self.current_charts:
                self.current_charts[chart_type].setParent(None)
                
            # 新しいキャンバスを作成
            canvas = FigureCanvas(figure)
            canvas.setMinimumSize(800, 600)
            self.current_charts[chart_type] = canvas
            
            # スクロールエリアに設定
            self.chart_scroll.setWidget(canvas)
            
            logger.info(f"📊 グラフ表示完了: {chart_type}")
            
        except Exception as e:
            logger.error(f"❌ グラフ表示エラー: {e}")
            
    def on_simple_chart_ready(self, chart_type: str, chart_data: Dict):
        """簡易グラフが準備完了した時の処理"""
        try:
            # 進捗バーを非表示
            self.progress_bar.setVisible(False)
            
            # 既存のキャンバスを削除
            if chart_type in self.current_charts:
                self.current_charts[chart_type].setParent(None)
                
            # 新しい簡易チャートウィジェットを作成
            simple_chart = SimpleChartWidget()
            simple_chart.set_chart_data(chart_type, chart_data)
            self.current_charts[chart_type] = simple_chart
            
            # スクロールエリアに設定
            self.chart_scroll.setWidget(simple_chart)
            
            logger.info(f"📊 簡易グラフ表示完了: {chart_type}")
            
        except Exception as e:
            logger.error(f"❌ 簡易グラフ表示エラー: {e}")
            
    def refresh_current_chart(self):
        """現在のグラフを更新"""
        current_text = self.chart_type_combo.currentText()
        if current_text:
            # データを再読み込み
            self.visualizer.load_data()
            self.generate_chart(current_text)
            
    def export_current_chart(self):
        """現在のグラフをエクスポート"""
        try:
            if not self.current_charts:
                QMessageBox.warning(self, "警告", "エクスポートするグラフがありません")
                return
                
            # ファイル保存ダイアログ
            file_format = self.format_combo.currentText().lower()
            filename, _ = QFileDialog.getSaveFileName(
                self, "グラフを保存", 
                f"chart.{file_format}", 
                f"{file_format.upper()} files (*.{file_format})"
            )
            
            if filename:
                # 現在のグラフを保存
                current_chart = list(self.current_charts.values())[-1]
                
                if hasattr(current_chart, 'figure'):
                    # matplotlibの場合
                    current_chart.figure.savefig(filename, dpi=self.dpi_spinbox.value(), 
                                                bbox_inches='tight')
                else:
                    # 簡易チャートの場合、QPixmapでキャプチャ
                    pixmap = current_chart.grab()
                    pixmap.save(filename, file_format.upper())
                
                QMessageBox.information(self, "成功", f"グラフを保存しました: {filename}")
                logger.info(f"📊 グラフエクスポート完了: {filename}")
                
        except Exception as e:
            logger.error(f"❌ グラフエクスポートエラー: {e}")
            QMessageBox.critical(self, "エラー", f"エクスポートに失敗しました: {e}")
            
    def export_all_charts(self):
        """全てのグラフをエクスポート"""
        try:
            # エクスポートディレクトリを選択
            export_dir = QFileDialog.getExistingDirectory(self, "エクスポート先を選択")
            if not export_dir:
                return
                
            # 全てのグラフタイプを生成・エクスポート
            chart_types = [
                ('daily', {'days': 7}, '日別統計_7日間'),
                ('daily', {'days': 30}, '日別統計_30日間'),
                ('weekly', {'weeks': 4}, '週別統計'),
                ('heatmap', {}, '時間別ヒートマップ'),
                ('productivity', {}, '生産性指標')
            ]
            
            file_format = self.format_combo.currentText().lower()
            dpi = self.dpi_spinbox.value()
            
            for chart_type, kwargs, name in chart_types:
                try:
                    filename = Path(export_dir) / f"{name}.{file_format}"
                    
                    # matplotlib使用可能：
                        # グラフを生成
                        if chart_type == 'daily':
                            figure = self.visualizer.create_daily_chart(kwargs['days'])
                        elif chart_type == 'weekly':
                            figure = self.visualizer.create_weekly_chart(kwargs['weeks'])
                        elif chart_type == 'heatmap':
                            figure = self.visualizer.create_hourly_heatmap()
                        elif chart_type == 'productivity':
                            figure = self.visualizer.create_productivity_chart()
                        
                        # ファイルを保存
                        figure.savefig(filename, dpi=dpi, bbox_inches='tight')
                        plt.close(figure)  # メモリ解放
                    else:
                        # 簡易チャートを生成してエクスポート
                        chart_data = self.visualizer.get_simple_chart_data(chart_type, **kwargs)
                        simple_chart = SimpleChartWidget()
                        simple_chart.set_chart_data(chart_type, chart_data)
                        simple_chart.resize(800, 600)
                        
                        # QPixmapでキャプチャして保存
                        pixmap = simple_chart.grab()
                        pixmap.save(str(filename), file_format.upper())
                    
                except Exception as e:
                    logger.error(f"❌ {name} エクスポートエラー: {e}")
                    
            QMessageBox.information(self, "成功", f"全グラフのエクスポートが完了しました")
            logger.info(f"📊 全グラフエクスポート完了: {export_dir}")
            
        except Exception as e:
            logger.error(f"❌ 全グラフエクスポートエラー: {e}")
            QMessageBox.critical(self, "エラー", f"エクスポートに失敗しました: {e}")