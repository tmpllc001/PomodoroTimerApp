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
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPainter

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from .stats_visualizer import StatsVisualizer
from typing import Dict, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ChartGeneratorThread(QThread):
    """バックグラウンドでグラフを生成するスレッド"""
    chartReady = pyqtSignal(Figure, str)  # figure, chart_type
    
    def __init__(self, visualizer: StatsVisualizer, chart_type: str, **kwargs):
        super().__init__()
        self.visualizer = visualizer
        self.chart_type = chart_type
        self.kwargs = kwargs
        
    def run(self):
        """グラフ生成を実行"""
        try:
            if self.chart_type == 'daily':
                days = self.kwargs.get('days', 7)
                figure = self.visualizer.create_daily_chart(days)
            elif self.chart_type == 'weekly':
                weeks = self.kwargs.get('weeks', 4)
                figure = self.visualizer.create_weekly_chart(weeks)
            elif self.chart_type == 'heatmap':
                figure = self.visualizer.create_hourly_heatmap()
            elif self.chart_type == 'productivity':
                figure = self.visualizer.create_productivity_chart()
            else:
                figure = Figure()
                
            self.chartReady.emit(figure, self.chart_type)
            
        except Exception as e:
            logger.error(f"❌ グラフ生成エラー: {e}")
            # エラー用の空のFigureを送信
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
            self.chart_thread.chartReady.connect(self.on_chart_ready)
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
                current_chart.figure.savefig(filename, dpi=self.dpi_spinbox.value(), 
                                            bbox_inches='tight')
                
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
                    filename = Path(export_dir) / f"{name}.{file_format}"
                    figure.savefig(filename, dpi=dpi, bbox_inches='tight')
                    
                    plt.close(figure)  # メモリ解放
                    
                except Exception as e:
                    logger.error(f"❌ {name} エクスポートエラー: {e}")
                    
            QMessageBox.information(self, "成功", f"全グラフのエクスポートが完了しました")
            logger.info(f"📊 全グラフエクスポート完了: {export_dir}")
            
        except Exception as e:
            logger.error(f"❌ 全グラフエクスポートエラー: {e}")
            QMessageBox.critical(self, "エラー", f"エクスポートに失敗しました: {e}")