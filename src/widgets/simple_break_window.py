#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Break Window - minimal_timer_demo風のさりげない休憩ウィンドウ
画面中央に小さく表示される控えめな休憩通知
"""

import json
import random
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QApplication)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QMouseEvent, QAction, QMenu

logger = logging.getLogger(__name__)


class SimpleBreakContentManager:
    """シンプルな休憩コンテンツ管理"""
    
    def __init__(self):
        self.content_file = Path("data/break_content.json")
        self.content = self.load_content()
    
    def load_content(self) -> Dict[str, Any]:
        """コンテンツデータを読み込み"""
        try:
            if self.content_file.exists():
                with open(self.content_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self.get_default_content()
        except Exception as e:
            logger.error(f"コンテンツ読み込みエラー: {e}")
            return self.get_default_content()
    
    def get_default_content(self) -> Dict[str, Any]:
        """デフォルトコンテンツ"""
        return {
            "simple_tips": [
                "💧 水分補給をお忘れなく",
                "🤸 軽く首を回してみましょう",
                "👁️ 遠くを見て目を休めましょう",
                "🌬️ 深呼吸でリラックス",
                "🚶 少し歩いてみませんか？",
                "😊 笑顔でリフレッシュ"
            ],
            "break_activities": [
                "💧 水を飲む",
                "🤸 ストレッチ",
                "👁️ 目を休める",
                "🌬️ 深呼吸",
                "🚶 軽い運動",
                "😌 リラックス"
            ]
        }
    
    def get_random_tip(self) -> str:
        """ランダムなアドバイスを取得"""
        tips = self.content.get("simple_tips", self.get_default_content()["simple_tips"])
        return random.choice(tips)
    
    def get_random_activity(self) -> str:
        """ランダムな活動を取得"""
        activities = self.content.get("break_activities", self.get_default_content()["break_activities"])
        return random.choice(activities)


class SimpleBreakWindow(QMainWindow):
    """minimal_timer_demo風のシンプルな休憩ウィンドウ"""
    
    break_finished = pyqtSignal()
    break_skipped = pyqtSignal()
    
    def __init__(self, break_type: str = "short", duration_minutes: int = 5):
        super().__init__()
        
        self.break_type = break_type
        self.duration_minutes = duration_minutes
        self.time_left = duration_minutes * 60
        self.content_manager = SimpleBreakContentManager()
        
        # ドラッグ用
        self.dragging = False
        self.drag_position = None
        
        self.init_ui()
        self.setup_timer()
        self.center_on_screen()
        
        logger.info(f"🛌 シンプル休憩ウィンドウ表示: {break_type} ({duration_minutes}分)")
    
    def init_ui(self):
        """UI初期化 - minimal_timer_demo風"""
        break_name = "長い休憩" if self.break_type == "long" else "休憩"
        self.setWindowTitle(f"🛌 {break_name}の時間です")
        self.setFixedSize(280, 140)
        
        # フレームレス・最前面（minimal_timer_demo風）
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        # メインウィジェット
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        # 休憩メッセージ
        break_emoji = "🌸" if self.break_type == "long" else "☕"
        break_message = f"{break_emoji} {break_name}の時間です！"
        
        self.message_label = QLabel(break_message)
        self.message_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("color: white; background: transparent;")
        layout.addWidget(self.message_label)
        
        # カウントダウン表示
        self.time_label = QLabel(f"{self.duration_minutes:02d}:00")
        self.time_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("color: #FFD700; background: transparent;")
        layout.addWidget(self.time_label)
        
        # アドバイス
        tip = self.content_manager.get_random_tip()
        self.tip_label = QLabel(tip)
        self.tip_label.setFont(QFont("Arial", 10))
        self.tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tip_label.setStyleSheet("color: #cccccc; background: transparent;")
        self.tip_label.setWordWrap(True)
        layout.addWidget(self.tip_label)
        
        # コントロールボタン（小さく）
        button_layout = QHBoxLayout()
        
        self.skip_btn = QPushButton("⏩")
        self.skip_btn.setMaximumSize(30, 25)
        self.skip_btn.setToolTip("休憩をスキップ")
        self.skip_btn.clicked.connect(self.skip_break)
        self.skip_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.5);
                border-radius: 3px;
                color: white;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.5);
            }
        """)
        
        self.extend_btn = QPushButton("+1")
        self.extend_btn.setMaximumSize(30, 25)
        self.extend_btn.setToolTip("1分延長")
        self.extend_btn.clicked.connect(self.extend_break)
        self.extend_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.5);
                border-radius: 3px;
                color: white;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.5);
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(self.extend_btn)
        button_layout.addWidget(self.skip_btn)
        layout.addLayout(button_layout)
        
        # minimal_timer_demo風のスタイル
        main_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(40, 40, 40, 220);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        """)
    
    def setup_timer(self):
        """タイマー設定"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)
    
    def update_countdown(self):
        """カウントダウン更新"""
        self.time_left -= 1
        
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
        
        # 残り30秒でアドバイスを更新
        if self.time_left == 30:
            activity = self.content_manager.get_random_activity()
            self.tip_label.setText(f"まもなく終了 {activity}")
        
        # 終了
        if self.time_left <= 0:
            self.timer.stop()
            self.break_finished.emit()
            self.close()
    
    def extend_break(self):
        """1分延長"""
        self.time_left += 60
        logger.info("⏰ 休憩を1分延長")
    
    def skip_break(self):
        """休憩をスキップ"""
        self.timer.stop()
        self.break_skipped.emit()
        self.close()
        logger.info("⏩ 休憩をスキップ")
    
    def center_on_screen(self):
        """画面中央に配置"""
        screen = QApplication.primaryScreen().geometry()
        window_rect = self.frameGeometry()
        center_point = screen.center()
        window_rect.moveCenter(center_point)
        self.move(window_rect.topLeft())
    
    # マウスイベント（ドラッグ移動）- minimal_timer_demo準拠
    def mousePressEvent(self, event: QMouseEvent):
        """マウス押下"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """マウス移動"""
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """マウスリリース"""
        self.dragging = False
    
    def contextMenuEvent(self, event):
        """右クリックメニュー"""
        menu = QMenu(self)
        
        # アドバイス更新
        refresh_tip = QAction("💡 別のアドバイス", self)
        refresh_tip.triggered.connect(self.refresh_tip)
        menu.addAction(refresh_tip)
        
        menu.addSeparator()
        
        # 延長・スキップ
        extend_action = QAction("⏰ 1分延長", self)
        extend_action.triggered.connect(self.extend_break)
        menu.addAction(extend_action)
        
        skip_action = QAction("⏩ スキップ", self)
        skip_action.triggered.connect(self.skip_break)
        menu.addAction(skip_action)
        
        menu.exec(event.globalPos())
    
    def refresh_tip(self):
        """アドバイスを更新"""
        tip = self.content_manager.get_random_tip()
        self.tip_label.setText(tip)
    
    def closeEvent(self, event):
        """ウィンドウ終了時"""
        if hasattr(self, 'timer'):
            self.timer.stop()
        event.accept()


def show_simple_break_window(break_type: str = "short", duration_minutes: int = 5) -> SimpleBreakWindow:
    """シンプル休憩ウィンドウを表示"""
    window = SimpleBreakWindow(break_type, duration_minutes)
    window.show()
    return window


# テスト用
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    # テスト表示
    window = show_simple_break_window("short", 1)  # 1分の短い休憩
    
    sys.exit(app.exec())