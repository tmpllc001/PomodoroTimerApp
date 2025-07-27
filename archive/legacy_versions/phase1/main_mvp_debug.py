#!/usr/bin/env python3
"""
ポモドーロタイマー MVP版 - デバッグ版
音声なしでタイマー機能をテスト
"""

import sys
import os
from pathlib import Path
import logging

# ログ設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mvp_debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# プロジェクトパス追加
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer, QTime, pyqtSignal
from PyQt6.QtGui import QFont

class DebugTimer(QMainWindow):
    """デバッグ用シンプルタイマー"""
    
    def __init__(self):
        super().__init__()
        self.time_left = 25 * 60  # 25分（秒）
        self.is_running = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        
        self.setup_ui()
        logger.info("デバッグタイマー初期化完了")
        
    def setup_ui(self):
        """UI設定"""
        # メインウィンドウ設定
        self.setWindowTitle("ポモドーロタイマー MVP - デバッグ版")
        self.setGeometry(100, 100, 400, 200)
        
        # 透明度設定（オプション）
        self.setWindowOpacity(0.9)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # レイアウト
        layout = QVBoxLayout(central_widget)
        
        # タイマー表示
        self.time_label = QLabel(self.format_time(self.time_left))
        self.time_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("color: #2c3e50; background-color: rgba(255,255,255,0.8); padding: 20px; border-radius: 10px;")
        layout.addWidget(self.time_label)
        
        # ボタンレイアウト
        button_layout = QHBoxLayout()
        
        # 開始/停止ボタン
        self.start_pause_btn = QPushButton("開始")
        self.start_pause_btn.clicked.connect(self.toggle_timer)
        self.start_pause_btn.setStyleSheet("QPushButton { background-color: #27ae60; color: white; font-size: 14px; padding: 10px; border-radius: 5px; }")
        button_layout.addWidget(self.start_pause_btn)
        
        # リセットボタン
        self.reset_btn = QPushButton("リセット")
        self.reset_btn.clicked.connect(self.reset_timer)
        self.reset_btn.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; font-size: 14px; padding: 10px; border-radius: 5px; }")
        button_layout.addWidget(self.reset_btn)
        
        layout.addLayout(button_layout)
        
        # ステータス表示
        self.status_label = QLabel("準備完了")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        logger.info("UI設定完了")
        
    def format_time(self, seconds):
        """時間をMM:SS形式でフォーマット"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
        
    def toggle_timer(self):
        """タイマー開始/停止"""
        if self.is_running:
            self.timer.stop()
            self.is_running = False
            self.start_pause_btn.setText("再開")
            self.status_label.setText("一時停止中")
            logger.info("タイマー一時停止")
        else:
            self.timer.start(1000)  # 1秒間隔
            self.is_running = True
            self.start_pause_btn.setText("一時停止")
            self.status_label.setText("実行中...")
            logger.info("タイマー開始")
            
    def reset_timer(self):
        """タイマーリセット"""
        self.timer.stop()
        self.is_running = False
        self.time_left = 25 * 60
        self.time_label.setText(self.format_time(self.time_left))
        self.start_pause_btn.setText("開始")
        self.status_label.setText("準備完了")
        logger.info("タイマーリセット")
        
    def update_timer(self):
        """タイマー更新"""
        if self.time_left > 0:
            self.time_left -= 1
            self.time_label.setText(self.format_time(self.time_left))
            logger.debug(f"タイマー更新: {self.format_time(self.time_left)}")
            
            if self.time_left <= 10:
                # 残り10秒でアラート色
                self.time_label.setStyleSheet("color: #e74c3c; background-color: rgba(255,255,255,0.9); padding: 20px; border-radius: 10px;")
        else:
            # タイマー終了
            self.timer.stop()
            self.is_running = False
            self.start_pause_btn.setText("開始")
            self.status_label.setText("🎉 ポモドーロ完了！")
            self.time_label.setText("00:00")
            self.time_label.setStyleSheet("color: #27ae60; background-color: rgba(255,255,255,0.9); padding: 20px; border-radius: 10px;")
            logger.info("ポモドーロ完了")

def main():
    """メイン実行"""
    logger.info("🚀 ポモドーロタイマー MVP デバッグ版 起動中...")
    
    # QApplication作成
    app = QApplication(sys.argv)
    app.setApplicationName("Pomodoro Timer MVP Debug")
    app.setApplicationVersion("0.1.0-debug")
    
    # WSL環境での表示設定
    if 'DISPLAY' not in os.environ:
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        logger.warning("GUI環境が検出されません。オフスクリーンモードで実行します")
    
    try:
        # ウィンドウ作成・表示
        window = DebugTimer()
        window.show()
        
        logger.info("✅ MVP デバッグ版起動完了！")
        print("✅ MVP デバッグ版起動完了！")
        print("⏰ 開始ボタンをクリックしてタイマーを開始してください")
        print("📝 ログファイル: mvp_debug.log")
        
        # アプリ実行
        return app.exec()
        
    except Exception as e:
        logger.error(f"❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())