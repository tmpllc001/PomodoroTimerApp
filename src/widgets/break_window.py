#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Break Window - 休憩時専用ウィンドウ
画面中央に表示される休憩ガイドウィンドウ
"""

import json
import random
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QTabWidget, QTextEdit,
                           QScrollArea, QFrame, QProgressBar, QGroupBox,
                           QApplication)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QLinearGradient, QPen

logger = logging.getLogger(__name__)


class BreakContentManager:
    """休憩コンテンツ管理クラス"""
    
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
                logger.warning(f"コンテンツファイルが見つかりません: {self.content_file}")
                return self.get_default_content()
        except Exception as e:
            logger.error(f"コンテンツ読み込みエラー: {e}")
            return self.get_default_content()
    
    def get_default_content(self) -> Dict[str, Any]:
        """デフォルトコンテンツ"""
        return {
            "quotes": [
                {"text": "休息は怠惰ではない。それは必要なものだ。", "author": "作者不明"}
            ],
            "tips": [
                {"title": "💧 水分補給", "content": "休憩時には水分補給を忘れずに！"}
            ],
            "stretches": [
                {
                    "name": "首のストレッチ",
                    "duration": "30秒",
                    "steps": ["ゆっくりと首を左右に傾ける"],
                    "benefits": "首の緊張を和らげる",
                    "ascii_art": "   o\n  /|\\\n  / \\\n首をゆっくり回す"
                }
            ],
            "short_break_activities": ["深呼吸", "水分補給", "軽いストレッチ"],
            "long_break_activities": ["散歩", "お茶", "軽食"]
        }
    
    def get_random_quote(self) -> Dict[str, str]:
        """ランダムな名言を取得"""
        quotes = self.content.get("quotes", [])
        return random.choice(quotes) if quotes else {"text": "頑張りましょう！", "author": ""}
    
    def get_random_tip(self) -> Dict[str, str]:
        """ランダムな豆知識を取得"""
        tips = self.content.get("tips", [])
        return random.choice(tips) if tips else {"title": "休憩のコツ", "content": "深呼吸をしましょう"}
    
    def get_random_stretch(self) -> Dict[str, Any]:
        """ランダムなストレッチを取得"""
        stretches = self.content.get("stretches", [])
        return random.choice(stretches) if stretches else {
            "name": "基本ストレッチ",
            "duration": "30秒",
            "steps": ["軽く体を伸ばす"],
            "benefits": "体をリフレッシュ",
            "ascii_art": "体を伸ばしましょう"
        }
    
    def get_random_activity(self, break_type: str = "short") -> str:
        """ランダムな活動を取得"""
        key = f"{break_type}_break_activities"
        activities = self.content.get(key, [])
        return random.choice(activities) if activities else "休憩を楽しみましょう"
    
    def get_breathing_exercise(self) -> Dict[str, Any]:
        """呼吸法を取得"""
        exercises = self.content.get("breathing_exercises", [])
        return random.choice(exercises) if exercises else {
            "name": "基本呼吸法",
            "duration": "1分",
            "steps": ["ゆっくり深呼吸"],
            "benefits": "リラックス効果"
        }


class StretchVisualizerWidget(QWidget):
    """ストレッチ図示ウィジェット"""
    
    def __init__(self, stretch_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.stretch_data = stretch_data
        self.setMinimumSize(300, 200)
        self.setup_ui()
    
    def setup_ui(self):
        """UI設定"""
        layout = QVBoxLayout(self)
        
        # ストレッチ名
        name_label = QLabel(self.stretch_data.get("name", "ストレッチ"))
        name_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(name_label)
        
        # ASCII アート表示
        art_widget = QWidget()
        art_widget.setMinimumHeight(80)
        art_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 8px;
            }
        """)
        art_layout = QVBoxLayout(art_widget)
        
        ascii_art = self.stretch_data.get("ascii_art", "")
        art_label = QLabel(ascii_art)
        art_label.setFont(QFont("Courier", 12))
        art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        art_label.setStyleSheet("color: #495057; background: transparent; border: none;")
        art_layout.addWidget(art_label)
        
        layout.addWidget(art_widget)
        
        # 手順
        steps_label = QLabel("🔄 手順:")
        steps_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(steps_label)
        
        steps = self.stretch_data.get("steps", [])
        for i, step in enumerate(steps, 1):
            step_label = QLabel(f"{i}. {step}")
            step_label.setWordWrap(True)
            step_label.setStyleSheet("margin-left: 10px; margin-bottom: 5px; color: #495057;")
            layout.addWidget(step_label)
        
        # 効果
        benefits = self.stretch_data.get("benefits", "")
        if benefits:
            benefits_label = QLabel(f"✨ 効果: {benefits}")
            benefits_label.setWordWrap(True)
            benefits_label.setStyleSheet("color: #28a745; font-weight: bold; margin-top: 10px;")
            layout.addWidget(benefits_label)
        
        # 時間
        duration = self.stretch_data.get("duration", "")
        if duration:
            duration_label = QLabel(f"⏱️ 時間: {duration}")
            duration_label.setStyleSheet("color: #6c757d; font-style: italic;")
            layout.addWidget(duration_label)


class CountdownWidget(QWidget):
    """カウントダウンウィジェット"""
    
    countdown_finished = pyqtSignal()
    
    def __init__(self, duration_seconds: int, parent=None):
        super().__init__(parent)
        self.duration = duration_seconds
        self.remaining = duration_seconds
        self.setMinimumSize(200, 200)
        
        # タイマー設定
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)
        
    def start_countdown(self):
        """カウントダウン開始"""
        self.timer.start(1000)
        self.update()
    
    def update_countdown(self):
        """カウントダウン更新"""
        self.remaining -= 1
        self.update()
        
        if self.remaining <= 0:
            self.timer.stop()
            self.countdown_finished.emit()
    
    def paintEvent(self, event):
        """カスタム描画"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 背景円
        center = self.rect().center()
        radius = min(self.width(), self.height()) // 2 - 10
        
        # 背景円
        painter.setPen(QPen(QColor(0xde, 0xe2, 0xe6), 8))
        painter.drawEllipse(center.x() - radius, center.y() - radius, radius * 2, radius * 2)
        
        # 進捗円
        progress = (self.duration - self.remaining) / self.duration
        angle = int(progress * 360)
        
        painter.setPen(QPen(QColor(0x28, 0xa7, 0x45), 8))
        painter.drawArc(center.x() - radius, center.y() - radius, radius * 2, radius * 2,
                       90 * 16, -angle * 16)
        
        # 時間表示
        minutes = self.remaining // 60
        seconds = self.remaining % 60
        time_text = f"{minutes:02d}:{seconds:02d}"
        
        painter.setPen(QColor(0x2c, 0x3e, 0x50))
        painter.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, time_text)


class BreakWindow(QMainWindow):
    """休憩ウィンドウメイン"""
    
    break_finished = pyqtSignal()
    skip_break = pyqtSignal()
    
    def __init__(self, break_type: str = "short", duration_minutes: int = 5):
        super().__init__()
        
        self.break_type = break_type  # "short" or "long"
        self.duration_minutes = duration_minutes
        self.content_manager = BreakContentManager()
        
        self.init_ui()
        self.setup_animations()
        self.show_content()
        
        # ウィンドウを画面中央に配置
        self.center_on_screen()
        
        logger.info(f"🛌 休憩ウィンドウ表示: {break_type} ({duration_minutes}分)")
    
    def init_ui(self):
        """UI初期化"""
        self.setWindowTitle(f"🛌 {'短い休憩' if self.break_type == 'short' else '長い休憩'}の時間です！")
        self.setFixedSize(600, 500)
        
        # ウィンドウフラグ設定（常に最前面、フレーム付き）
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        
        # メインウィジェット
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # グラデーション背景
        main_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #667eea,
                    stop: 1 #764ba2
                );
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # タイトル
        title_text = "🌸 長い休憩の時間です！" if self.break_type == "long" else "☕ 短い休憩の時間です！"
        self.title_label = QLabel(title_text)
        self.title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("color: white; background: transparent;")
        layout.addWidget(self.title_label)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid white;
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.9);
            }
            QTabBar::tab {
                background-color: rgba(255, 255, 255, 0.7);
                border: 1px solid #ccc;
                padding: 8px 16px;
                margin-right: 2px;
                border-radius: 4px 4px 0 0;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: none;
            }
        """)
        layout.addWidget(self.tab_widget)
        
        # タブを設定
        self.setup_quote_tab()
        self.setup_stretch_tab()
        self.setup_tips_tab()
        self.setup_activity_tab()
        
        # コントロールボタン
        button_layout = QHBoxLayout()
        
        # カウントダウン表示
        self.countdown_widget = CountdownWidget(self.duration_minutes * 60)
        self.countdown_widget.countdown_finished.connect(self.on_break_finished)
        button_layout.addWidget(self.countdown_widget)
        
        # ボタンレイアウト
        btn_layout = QVBoxLayout()
        
        self.skip_btn = QPushButton("⏩ 休憩をスキップ")
        self.skip_btn.clicked.connect(self.on_skip_break)
        self.skip_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.8);
                border: 2px solid white;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
            QPushButton:hover {
                background-color: white;
            }
        """)
        btn_layout.addWidget(self.skip_btn)
        
        self.extend_btn = QPushButton("⏰ 1分延長")
        self.extend_btn.clicked.connect(self.extend_break)
        self.extend_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.6);
                border: 2px solid white;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 12px;
                color: #555;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.8);
            }
        """)
        btn_layout.addWidget(self.extend_btn)
        
        button_layout.addLayout(btn_layout)
        layout.addLayout(button_layout)
        
        # カウントダウン開始
        self.countdown_widget.start_countdown()
    
    def setup_quote_tab(self):
        """名言タブ"""
        quote_widget = QWidget()
        layout = QVBoxLayout(quote_widget)
        
        quote_data = self.content_manager.get_random_quote()
        
        # 名言本文
        quote_label = QLabel(f'"{quote_data["text"]}"')
        quote_label.setFont(QFont("Arial", 16, QFont.Weight.Normal))
        quote_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        quote_label.setWordWrap(True)
        quote_label.setStyleSheet("color: #2c3e50; font-style: italic; margin: 20px;")
        layout.addWidget(quote_label)
        
        # 作者
        author_text = quote_data.get("author", "")
        if author_text:
            author_label = QLabel(f"— {author_text}")
            author_label.setFont(QFont("Arial", 12))
            author_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            author_label.setStyleSheet("color: #6c757d; margin-right: 20px;")
            layout.addWidget(author_label)
        
        layout.addStretch()
        
        # 新しい名言ボタン
        new_quote_btn = QPushButton("✨ 別の名言を見る")
        new_quote_btn.clicked.connect(self.refresh_quote)
        new_quote_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addWidget(new_quote_btn)
        
        self.tab_widget.addTab(quote_widget, "💭 名言")
        self.quote_widget = quote_widget
    
    def setup_stretch_tab(self):
        """ストレッチタブ"""
        stretch_widget = QWidget()
        layout = QVBoxLayout(stretch_widget)
        
        # スクロールエリア
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        # ストレッチ表示
        self.stretch_visualizer = StretchVisualizerWidget(
            self.content_manager.get_random_stretch()
        )
        scroll.setWidget(self.stretch_visualizer)
        layout.addWidget(scroll)
        
        # 新しいストレッチボタン
        new_stretch_btn = QPushButton("🔄 別のストレッチ")
        new_stretch_btn.clicked.connect(self.refresh_stretch)
        new_stretch_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        layout.addWidget(new_stretch_btn)
        
        self.tab_widget.addTab(stretch_widget, "🤸 ストレッチ")
    
    def setup_tips_tab(self):
        """豆知識タブ"""
        tips_widget = QWidget()
        layout = QVBoxLayout(tips_widget)
        
        tip_data = self.content_manager.get_random_tip()
        
        # タイトル
        title_label = QLabel(tip_data["title"])
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # 内容
        content_label = QLabel(tip_data["content"])
        content_label.setFont(QFont("Arial", 12))
        content_label.setWordWrap(True)
        content_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        content_label.setStyleSheet("color: #495057; line-height: 1.6; margin: 10px;")
        layout.addWidget(content_label)
        
        layout.addStretch()
        
        # 新しい豆知識ボタン
        new_tip_btn = QPushButton("🧠 別の豆知識")
        new_tip_btn.clicked.connect(self.refresh_tip)
        new_tip_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #212529;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """)
        layout.addWidget(new_tip_btn)
        
        self.tab_widget.addTab(tips_widget, "🧠 豆知識")
        self.tips_widget = tips_widget
    
    def setup_activity_tab(self):
        """おすすめ活動タブ"""
        activity_widget = QWidget()
        layout = QVBoxLayout(activity_widget)
        
        # タイトル
        title_label = QLabel("🎯 おすすめの休憩活動")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        layout.addWidget(title_label)
        
        # 活動リスト
        activities = self.content_manager.content.get(f"{self.break_type}_break_activities", [])
        
        for i, activity in enumerate(activities[:5]):  # 最初の5つを表示
            activity_label = QLabel(f"{i+1}. {activity}")
            activity_label.setFont(QFont("Arial", 12))
            activity_label.setStyleSheet("color: #495057; margin: 5px 10px; padding: 5px;")
            layout.addWidget(activity_label)
        
        layout.addStretch()
        
        # 呼吸法ガイド
        breathing_data = self.content_manager.get_breathing_exercise()
        breathing_group = QGroupBox(f"🌬️ {breathing_data['name']}")
        breathing_layout = QVBoxLayout(breathing_group)
        
        for step in breathing_data["steps"]:
            step_label = QLabel(f"• {step}")
            step_label.setWordWrap(True)
            step_label.setStyleSheet("color: #495057; margin: 2px;")
            breathing_layout.addWidget(step_label)
        
        layout.addWidget(breathing_group)
        
        self.tab_widget.addTab(activity_widget, "🎯 活動")
    
    def setup_animations(self):
        """アニメーション設定"""
        # ウィンドウフェードイン
        self.setWindowOpacity(0)
        self.fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_animation.setDuration(500)
        self.fade_in_animation.setStartValue(0)
        self.fade_in_animation.setEndValue(1)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # タイトルアニメーション
        self.title_animation = QPropertyAnimation(self.title_label, b"geometry")
        self.title_animation.setDuration(800)
        self.title_animation.setEasingCurve(QEasingCurve.Type.OutBounce)
    
    def show_content(self):
        """コンテンツ表示アニメーション"""
        # フェードイン
        self.fade_in_animation.start()
        
        # タイトルバウンス
        original_rect = self.title_label.geometry()
        self.title_animation.setStartValue(QRect(original_rect.x(), original_rect.y() - 20, 
                                                original_rect.width(), original_rect.height()))
        self.title_animation.setEndValue(original_rect)
        self.title_animation.start()
    
    def center_on_screen(self):
        """画面中央に配置"""
        screen = QApplication.primaryScreen().geometry()
        window_rect = self.frameGeometry()
        center_point = screen.center()
        window_rect.moveCenter(center_point)
        self.move(window_rect.topLeft())
    
    def refresh_quote(self):
        """名言を更新"""
        quote_data = self.content_manager.get_random_quote()
        
        # ウィジェットを再作成
        self.tab_widget.removeTab(0)
        self.setup_quote_tab()
        self.tab_widget.setCurrentIndex(0)
    
    def refresh_stretch(self):
        """ストレッチを更新"""
        new_stretch = self.content_manager.get_random_stretch()
        
        # 新しいストレッチビジュアライザーを作成
        new_visualizer = StretchVisualizerWidget(new_stretch)
        
        # スクロールエリアのウィジェットを更新
        stretch_tab = self.tab_widget.widget(1)
        scroll = stretch_tab.findChild(QScrollArea)
        if scroll:
            scroll.setWidget(new_visualizer)
            self.stretch_visualizer = new_visualizer
    
    def refresh_tip(self):
        """豆知識を更新"""
        tip_data = self.content_manager.get_random_tip()
        
        # ウィジェットを再作成
        current_index = self.tab_widget.currentIndex()
        self.tab_widget.removeTab(2)
        self.setup_tips_tab()
        self.tab_widget.setCurrentIndex(current_index)
    
    def extend_break(self):
        """休憩を1分延長"""
        self.countdown_widget.remaining += 60
        self.countdown_widget.duration += 60
        logger.info("⏰ 休憩を1分延長")
    
    def on_skip_break(self):
        """休憩をスキップ"""
        self.countdown_widget.timer.stop()
        self.skip_break.emit()
        self.close()
        logger.info("⏩ 休憩をスキップ")
    
    def on_break_finished(self):
        """休憩終了"""
        self.break_finished.emit()
        self.close()
        logger.info("✅ 休憩時間終了")
    
    def closeEvent(self, event):
        """クローズイベント"""
        # アニメーション停止
        if hasattr(self, 'countdown_widget'):
            self.countdown_widget.timer.stop()
        
        event.accept()


def show_break_window(break_type: str = "short", duration_minutes: int = 5) -> BreakWindow:
    """休憩ウィンドウを表示"""
    window = BreakWindow(break_type, duration_minutes)
    window.show()
    return window


# テスト用
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    # テスト表示
    window = show_break_window("short", 1)  # 1分の短い休憩
    
    sys.exit(app.exec())