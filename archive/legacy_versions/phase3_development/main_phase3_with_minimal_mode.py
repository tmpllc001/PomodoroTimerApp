#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pomodoro Timer Phase 3 - 同一ウィンドウでのミニマルモード切り替え版
main_phase3_with_tasks.pyをベースに、同じウィンドウ内でモード切り替えを実装
"""

import sys
import os
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMenu
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSignal
from PyQt6.QtGui import QFont, QMouseEvent, QAction

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# main_phase3_with_tasks.pyから必要な部分を読み込み
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
with open('main_phase3_with_tasks.py', 'r', encoding='utf-8') as f:
    exec(f.read(), {'__name__': '__phase3__'})


class DualModeTimerWindow(PomodoroTimerPhase3):
    """Phase 3タイマーにミニマルモード機能を追加"""
    
    mode_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # モード管理
        self.is_minimal_mode = False
        self.transparent_mode = False
        
        # ドラッグ用
        self.dragging = False
        self.drag_position = QPoint()
        
        # ミニマルモード用のウィジェット（事前作成）
        self.minimal_widget = QWidget()
        self.setup_minimal_widget()
        self.minimal_widget.hide()
        
        # オリジナルのセントラルウィジェットを保存
        self.full_widget = self.centralWidget()
        
        # メニューバーに表示メニューを追加
        self.add_view_menu()
        
        logger.info("✅ デュアルモードタイマー初期化完了")
    
    def setup_minimal_widget(self):
        """ミニマルモード用ウィジェットの設定"""
        layout = QVBoxLayout(self.minimal_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # タイマー表示（大きめ）
        self.minimal_time_label = QLabel()
        self.minimal_time_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.minimal_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.minimal_time_label.setStyleSheet("color: white; background: transparent;")
        layout.addWidget(self.minimal_time_label)
        
        # ステータス表示（小さめ）
        self.minimal_status_label = QLabel()
        self.minimal_status_label.setFont(QFont("Arial", 10))
        self.minimal_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.minimal_status_label.setStyleSheet("color: #cccccc; background: transparent;")
        layout.addWidget(self.minimal_status_label)
        
        # 透明化設定
        self.minimal_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 200);
                border-radius: 10px;
            }
        """)
        
        # マウスイベントを設定
        self.minimal_widget.mousePressEvent = self.minimal_mouse_press
        self.minimal_widget.mouseMoveEvent = self.minimal_mouse_move
        self.minimal_widget.mouseReleaseEvent = self.minimal_mouse_release
        self.minimal_widget.contextMenuEvent = self.minimal_context_menu
    
    def add_view_menu(self):
        """表示メニューを追加"""
        view_menu = self.menuBar().addMenu('表示(&V)')
        
        # ミニマルモード切り替え
        self.minimal_action = QAction('ミニマルモード', self)
        self.minimal_action.setCheckable(True)
        self.minimal_action.setShortcut('Ctrl+M')
        self.minimal_action.triggered.connect(self.toggle_minimal_mode)
        view_menu.addAction(self.minimal_action)
        
        # 透明化切り替え
        self.transparent_action = QAction('透明化', self)
        self.transparent_action.setCheckable(True)
        self.transparent_action.setShortcut('Ctrl+T')
        self.transparent_action.triggered.connect(self.toggle_transparency)
        view_menu.addAction(self.transparent_action)
    
    def toggle_minimal_mode(self):
        """ミニマルモード切り替え"""
        self.is_minimal_mode = not self.is_minimal_mode
        
        if self.is_minimal_mode:
            # ミニマルモードへ
            self.switch_to_minimal()
        else:
            # フルモードへ
            self.switch_to_full()
    
    def switch_to_minimal(self):
        """ミニマルモードへ切り替え"""
        # 現在のウィンドウ位置を記憶
        self.full_mode_geometry = self.geometry()
        
        # メニューバーとステータスバーを非表示
        self.menuBar().hide()
        self.statusBar().hide()
        
        # フルウィジェットを非表示、ミニマルウィジェットを表示
        self.full_widget.hide()
        self.setCentralWidget(self.minimal_widget)
        self.minimal_widget.show()
        
        # タイマー表示を更新
        self.update_minimal_display()
        
        # ウィンドウサイズを小さく
        self.resize(200, 80)
        
        # フレームレスウィンドウに
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.show()
        
        # 透明化が有効なら適用
        if self.transparent_mode:
            self.apply_transparency()
        
        self.mode_changed.emit("minimal")
        logger.info("🔽 ミニマルモードへ切り替え")
    
    def switch_to_full(self):
        """フルモードへ切り替え"""
        # ミニマルウィジェットを非表示、フルウィジェットを表示
        self.minimal_widget.hide()
        self.setCentralWidget(self.full_widget)
        self.full_widget.show()
        
        # メニューバーとステータスバーを表示
        self.menuBar().show()
        self.statusBar().show()
        
        # ウィンドウフラグを元に戻す
        self.setWindowFlags(Qt.WindowType.Window)
        
        # 元のサイズに戻す
        if hasattr(self, 'full_mode_geometry'):
            self.setGeometry(self.full_mode_geometry)
        else:
            self.resize(450, 500)
        
        self.show()
        
        # 透明化を解除
        self.setWindowOpacity(1.0)
        self.setStyleSheet("")
        
        self.mode_changed.emit("full")
        logger.info("🔼 フルモードへ切り替え")
    
    def toggle_transparency(self):
        """透明化切り替え"""
        self.transparent_mode = not self.transparent_mode
        
        if self.transparent_mode:
            self.apply_transparency()
        else:
            self.remove_transparency()
    
    def apply_transparency(self):
        """透明化を適用"""
        if self.is_minimal_mode:
            # ミニマルモードでの透明化
            self.setWindowOpacity(0.8)
            self.minimal_widget.setStyleSheet("""
                QWidget {
                    background-color: rgba(0, 0, 0, 100);
                    border: none;
                }
                QLabel {
                    background: transparent;
                }
            """)
            # 左クリック透過（右クリックは残す）
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        else:
            # フルモードでの透明化
            self.setWindowOpacity(0.9)
    
    def remove_transparency(self):
        """透明化を解除"""
        self.setWindowOpacity(1.0)
        if self.is_minimal_mode:
            self.minimal_widget.setStyleSheet("""
                QWidget {
                    background-color: rgba(30, 30, 30, 200);
                    border-radius: 10px;
                }
            """)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
    
    def update_minimal_display(self):
        """ミニマルモードの表示を更新"""
        if hasattr(self, 'timer_display'):
            time_text = self.timer_display.text()
            self.minimal_time_label.setText(time_text)
            
            # セッション情報
            session_type = "作業中" if getattr(self, 'is_work_session', True) else "休憩中"
            session_num = getattr(self, 'pomodoro_count', 0) + 1
            self.minimal_status_label.setText(f"{session_type} #{session_num}")
    
    def update_timer_display(self):
        """タイマー表示を更新（オーバーライド）"""
        super().update_timer_display()
        
        # ミニマルモードの表示も更新
        if self.is_minimal_mode:
            self.update_minimal_display()
    
    def on_timer_finished(self):
        """タイマー完了時の処理（オーバーライド）"""
        super().on_timer_finished()
        
        # ミニマルモードの場合、3秒前からカウントダウン表示
        # （今回は簡略化のため省略）
    
    # ミニマルモード用のマウスイベント
    def minimal_mouse_press(self, event: QMouseEvent):
        """マウス押下（ミニマルモード）"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def minimal_mouse_move(self, event: QMouseEvent):
        """マウス移動（ミニマルモード）"""
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
    
    def minimal_mouse_release(self, event: QMouseEvent):
        """マウスリリース（ミニマルモード）"""
        self.dragging = False
    
    def minimal_context_menu(self, event):
        """右クリックメニュー（ミニマルモード）"""
        menu = QMenu(self)
        
        # フルモードへ
        full_action = QAction("フルモードへ", self)
        full_action.triggered.connect(self.toggle_minimal_mode)
        menu.addAction(full_action)
        
        menu.addSeparator()
        
        # 透明化切り替え
        trans_action = QAction("透明化", self)
        trans_action.setCheckable(True)
        trans_action.setChecked(self.transparent_mode)
        trans_action.triggered.connect(self.toggle_transparency)
        menu.addAction(trans_action)
        
        menu.addSeparator()
        
        # タイマー制御
        if hasattr(self, 'timer') and self.timer.isActive():
            pause_action = QAction("一時停止", self)
            pause_action.triggered.connect(self.pause_timer)
            menu.addAction(pause_action)
        else:
            start_action = QAction("開始", self)
            start_action.triggered.connect(self.start_timer)
            menu.addAction(start_action)
        
        reset_action = QAction("リセット", self)
        reset_action.triggered.connect(self.reset_timer)
        menu.addAction(reset_action)
        
        menu.exec(event.globalPos())


def main():
    """メイン関数"""
    logger.info("🚀 Phase 3 デュアルモード版アプリケーション開始")
    
    # 環境変数設定
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    
    # QApplication作成
    app = QApplication(sys.argv)
    app.setApplicationName("Pomodoro Timer Phase 3 - Dual Mode")
    app.setApplicationVersion("3.1.0")
    
    # メインウィンドウ作成
    window = DualModeTimerWindow()
    window.show()
    
    logger.info("✅ Phase 3 デュアルモード版アプリケーション初期化完了")
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())