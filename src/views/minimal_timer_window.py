#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal Timer Window - FavDesktopClock風のミニマルなタイマー表示
作業中は小さくタイマーのみ、休憩時は大きなウィンドウに切り替え
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QPushButton, QMenu, QApplication)
from PyQt6.QtCore import Qt, QTimer, QTime, QSize, QPoint, pyqtSignal
from PyQt6.QtGui import QFont, QAction, QPalette, QColor, QMouseEvent
import datetime


class MinimalTimerWindow(QMainWindow):
    """ミニマルなタイマーウィンドウ"""
    
    # シグナル定義
    settingsRequested = pyqtSignal()
    breakStarted = pyqtSignal()
    workStarted = pyqtSignal()
    
    def __init__(self, timer_controller=None, parent=None):
        super().__init__(parent)
        self.timer_controller = timer_controller
        self.is_minimal_mode = True
        self.show_current_time = False
        self.dragging = False
        self.drag_position = QPoint()
        
        self.setup_ui()
        self.setup_context_menu()
        self.apply_minimal_style()
        
        # タイマー更新用
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000)  # 1秒ごと更新
        
    def setup_ui(self):
        """UI初期設定"""
        # メインウィジェット
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # メインレイアウト
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 5, 10, 5)
        self.main_layout.setSpacing(2)
        
        # 現在時刻ラベル（オプション）
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setVisible(self.show_current_time)
        
        # タイマー表示ラベル
        self.timer_label = QLabel("25:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # セッション情報ラベル（作業中/休憩中）
        self.session_label = QLabel("作業中")
        self.session_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # レイアウトに追加
        self.main_layout.addWidget(self.time_label)
        self.main_layout.addWidget(self.timer_label)
        self.main_layout.addWidget(self.session_label)
        
        # ウィンドウ設定
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 初期サイズ（ミニマル）
        self.resize(120, 60)
        
    def setup_context_menu(self):
        """右クリックメニューの設定"""
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def show_context_menu(self, position):
        """コンテキストメニュー表示"""
        menu = QMenu(self)
        
        # 時刻表示切り替え
        time_action = QAction("現在時刻を表示", self)
        time_action.setCheckable(True)
        time_action.setChecked(self.show_current_time)
        time_action.triggered.connect(self.toggle_time_display)
        menu.addAction(time_action)
        
        menu.addSeparator()
        
        # 開始/停止
        if self.timer_controller:
            if self.timer_controller.is_running():
                pause_action = QAction("一時停止", self)
                pause_action.triggered.connect(self.timer_controller.pause_timer)
                menu.addAction(pause_action)
            else:
                start_action = QAction("開始", self)
                start_action.triggered.connect(self.timer_controller.start_timer)
                menu.addAction(start_action)
            
            reset_action = QAction("リセット", self)
            reset_action.triggered.connect(self.timer_controller.reset_timer)
            menu.addAction(reset_action)
        
        menu.addSeparator()
        
        # 設定
        settings_action = QAction("設定...", self)
        settings_action.triggered.connect(self.settingsRequested.emit)
        menu.addAction(settings_action)
        
        # 終了
        menu.addSeparator()
        quit_action = QAction("終了", self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)
        
        menu.exec(self.mapToGlobal(position))
        
    def toggle_time_display(self):
        """現在時刻表示の切り替え"""
        self.show_current_time = not self.show_current_time
        self.time_label.setVisible(self.show_current_time)
        self.adjust_window_size()
        
    def adjust_window_size(self):
        """表示内容に応じてウィンドウサイズ調整"""
        if self.is_minimal_mode:
            if self.show_current_time:
                self.resize(120, 80)
            else:
                self.resize(120, 60)
        
    def apply_minimal_style(self):
        """ミニマルスタイル適用"""
        style = """
            QWidget {
                background-color: rgba(40, 40, 40, 230);
                border-radius: 10px;
            }
            QLabel {
                color: #FFFFFF;
                background-color: transparent;
            }
            #timerLabel {
                font-size: 24px;
                font-weight: bold;
                color: #00FF00;
            }
            #timeLabel {
                font-size: 14px;
                color: #CCCCCC;
            }
            #sessionLabel {
                font-size: 12px;
                color: #FFAA00;
            }
        """
        self.setStyleSheet(style)
        
        # フォント設定
        timer_font = QFont("Arial", 24, QFont.Weight.Bold)
        self.timer_label.setFont(timer_font)
        self.timer_label.setObjectName("timerLabel")
        
        time_font = QFont("Arial", 14)
        self.time_label.setFont(time_font)
        self.time_label.setObjectName("timeLabel")
        
        session_font = QFont("Arial", 12)
        self.session_label.setFont(session_font)
        self.session_label.setObjectName("sessionLabel")
        
    def update_display(self):
        """表示更新"""
        # 現在時刻
        if self.show_current_time:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            self.time_label.setText(current_time)
        
        # タイマー
        if self.timer_controller:
            minutes = self.timer_controller.remaining_time // 60
            seconds = self.timer_controller.remaining_time % 60
            self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")
            
            # セッション状態
            if self.timer_controller.current_session_type == "work":
                self.session_label.setText("作業中")
                self.session_label.setStyleSheet("color: #00FF00;")
            else:
                self.session_label.setText("休憩中")
                self.session_label.setStyleSheet("color: #00AAFF;")
                
    def switch_to_break_mode(self):
        """休憩モードに切り替え（大きなウィンドウ）"""
        self.is_minimal_mode = False
        self.breakStarted.emit()
        
    def switch_to_work_mode(self):
        """作業モードに切り替え（ミニマルウィンドウ）"""
        self.is_minimal_mode = True
        self.adjust_window_size()
        self.workStarted.emit()
        
    # ドラッグ移動機能
    def mousePressEvent(self, event: QMouseEvent):
        """マウス押下時"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            
    def mouseMoveEvent(self, event: QMouseEvent):
        """マウス移動時"""
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        """マウスリリース時"""
        self.dragging = False
        
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """ダブルクリックで設定画面を開く"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.settingsRequested.emit()


class BreakWindow(QMainWindow):
    """休憩時の大きなウィンドウ"""
    
    backToWork = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """UI設定"""
        # メインウィジェット
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # レイアウト
        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # 休憩メッセージ
        self.message_label = QLabel("休憩時間です！")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_font = QFont("Arial", 32, QFont.Weight.Bold)
        self.message_label.setFont(message_font)
        
        # タイマー表示
        self.timer_label = QLabel("05:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_font = QFont("Arial", 48, QFont.Weight.Bold)
        self.timer_label.setFont(timer_font)
        
        # 休憩の提案
        self.suggestion_label = QLabel("ストレッチをしたり、水を飲んだりしましょう")
        self.suggestion_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        suggestion_font = QFont("Arial", 16)
        self.suggestion_label.setFont(suggestion_font)
        
        # スキップボタン
        self.skip_button = QPushButton("休憩をスキップ")
        self.skip_button.clicked.connect(self.backToWork.emit)
        
        # レイアウトに追加
        layout.addStretch()
        layout.addWidget(self.message_label)
        layout.addWidget(self.timer_label)
        layout.addWidget(self.suggestion_label)
        layout.addStretch()
        layout.addWidget(self.skip_button)
        
        # ウィンドウ設定
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # スタイル
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 240);
                border-radius: 20px;
            }
            QLabel {
                color: #FFFFFF;
            }
            #messageLabel {
                color: #00AAFF;
            }
            #timerLabel {
                color: #00FF00;
            }
            QPushButton {
                background-color: #555555;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)
        
        self.message_label.setObjectName("messageLabel")
        self.timer_label.setObjectName("timerLabel")
        
        # サイズ設定
        self.resize(500, 400)
        
    def update_timer(self, minutes, seconds):
        """タイマー更新"""
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")