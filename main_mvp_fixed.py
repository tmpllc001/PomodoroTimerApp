#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pomodoro Timer MVP - 修正版
音声エラー対応 + 文字化け修正版
"""

import sys
import os
import locale
from pathlib import Path
import logging

# 文字エンコーディング設定
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# ロケール設定
try:
    locale.setlocale(locale.LC_ALL, '')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except locale.Error:
        pass

# ログ設定（UTF-8対応）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mvp_fixed.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# プロジェクトパス追加
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QSpinBox
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

# 音声システム（エラー対応版）
AUDIO_AVAILABLE = False
try:
    import pygame.mixer
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
    logger.info("🔊 音声システム初期化成功")
except Exception as e:
    logger.warning(f"⚠️ 音声システム無効: {e}")
    logger.info("🔇 音声なしモードで動作します")

class PomodoroTimer(QMainWindow):
    """修正版ポモドーロタイマー"""
    
    timer_finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.work_minutes = 25  # デフォルト作業時間
        self.break_minutes = 5   # デフォルト休憩時間
        self.time_left = self.work_minutes * 60
        self.is_running = False
        self.is_work_session = True
        self.session_count = 0
        
        # QTimer設定
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        
        self.setup_ui()
        self.setup_audio()
        
        logger.info("✅ ポモドーロタイマー初期化完了")
        
    def setup_ui(self):
        """UI設定（文字化け対応）"""
        # ウィンドウ設定
        self.setWindowTitle("🍅 Pomodoro Timer MVP")
        self.setGeometry(100, 100, 450, 250)
        
        # 透明度・最前面設定
        self.setWindowOpacity(0.9)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # メインレイアウト
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # タイトル表示
        title_label = QLabel("🍅 Pomodoro Timer")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #e74c3c; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # セッション表示
        self.session_label = QLabel("📖 作業セッション #1")
        self.session_label.setFont(QFont("Arial", 12))
        self.session_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.session_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        layout.addWidget(self.session_label)
        
        # タイマー表示
        self.time_label = QLabel(self.format_time(self.time_left))
        self.time_label.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("""
            color: #2c3e50; 
            background-color: rgba(255,255,255,0.9); 
            padding: 20px; 
            border-radius: 15px;
            border: 2px solid #3498db;
        """)
        layout.addWidget(self.time_label)
        
        # 時間設定レイアウト（デバッグ用）
        time_settings_layout = QHBoxLayout()
        time_settings_layout.setSpacing(10)
        
        # 作業時間設定
        work_label = QLabel("作業時間:")
        work_label.setStyleSheet("color: #34495e; font-size: 12px;")
        time_settings_layout.addWidget(work_label)
        
        self.work_spinbox = QSpinBox()
        self.work_spinbox.setRange(1, 60)
        self.work_spinbox.setValue(self.work_minutes)
        self.work_spinbox.setSuffix(" 分")
        self.work_spinbox.valueChanged.connect(self.update_work_time)
        self.work_spinbox.setStyleSheet("""
            QSpinBox {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #ecf0f1;
            }
        """)
        time_settings_layout.addWidget(self.work_spinbox)
        
        # 休憩時間設定
        break_label = QLabel("休憩時間:")
        break_label.setStyleSheet("color: #34495e; font-size: 12px;")
        time_settings_layout.addWidget(break_label)
        
        self.break_spinbox = QSpinBox()
        self.break_spinbox.setRange(1, 30)
        self.break_spinbox.setValue(self.break_minutes)
        self.break_spinbox.setSuffix(" 分")
        self.break_spinbox.valueChanged.connect(self.update_break_time)
        self.break_spinbox.setStyleSheet("""
            QSpinBox {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #ecf0f1;
            }
        """)
        time_settings_layout.addWidget(self.break_spinbox)
        
        time_settings_layout.addStretch()
        layout.addLayout(time_settings_layout)
        
        # ボタンレイアウト
        button_layout = QHBoxLayout()
        
        # 開始/停止ボタン
        self.start_pause_btn = QPushButton("▶️ 開始")
        self.start_pause_btn.clicked.connect(self.toggle_timer)
        self.start_pause_btn.setStyleSheet("""
            QPushButton { 
                background-color: #27ae60; 
                color: white; 
                font-size: 16px; 
                font-weight: bold;
                padding: 12px 20px; 
                border-radius: 8px; 
                border: none;
            }
            QPushButton:hover { background-color: #2ecc71; }
            QPushButton:pressed { background-color: #229954; }
        """)
        button_layout.addWidget(self.start_pause_btn)
        
        # リセットボタン
        self.reset_btn = QPushButton("🔄 リセット")
        self.reset_btn.clicked.connect(self.reset_timer)
        self.reset_btn.setStyleSheet("""
            QPushButton { 
                background-color: #e74c3c; 
                color: white; 
                font-size: 16px; 
                font-weight: bold;
                padding: 12px 20px; 
                border-radius: 8px; 
                border: none;
            }
            QPushButton:hover { background-color: #c0392b; }
            QPushButton:pressed { background-color: #a93226; }
        """)
        button_layout.addWidget(self.reset_btn)
        
        layout.addLayout(button_layout)
        
        # ステータス表示
        self.status_label = QLabel("🟢 準備完了")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 14px; margin-top: 5px;")
        layout.addWidget(self.status_label)
        
        # 音声ステータス表示
        audio_status = "🔊 音声有効" if AUDIO_AVAILABLE else "🔇 音声無効"
        audio_label = QLabel(audio_status)
        audio_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        audio_label.setStyleSheet("color: #95a5a6; font-size: 10px;")
        layout.addWidget(audio_label)
        
        logger.info("🎨 UI設定完了")
        
    def setup_audio(self):
        """音声設定（エラー対応）"""
        if AUDIO_AVAILABLE:
            try:
                # 音声ファイルの存在確認（オプション）
                logger.info("🔊 音声システム準備完了")
            except Exception as e:
                logger.warning(f"🔇 音声設定エラー: {e}")
        
    def format_time(self, seconds):
        """時間フォーマット"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
        
    def toggle_timer(self):
        """タイマー開始/停止"""
        if self.is_running:
            self.pause_timer()
        else:
            self.start_timer()
            
    def start_timer(self):
        """タイマー開始"""
        self.timer.start(1000)
        self.is_running = True
        self.start_pause_btn.setText("⏸️ 一時停止")
        self.status_label.setText("🔴 実行中...")
        
        session_type = "作業" if self.is_work_session else "休憩"
        logger.info(f"▶️ {session_type}タイマー開始")
        
    def pause_timer(self):
        """タイマー一時停止"""
        self.timer.stop()
        self.is_running = False
        self.start_pause_btn.setText("▶️ 再開")
        self.status_label.setText("⏸️ 一時停止中")
        logger.info("⏸️ タイマー一時停止")
        
    def reset_timer(self):
        """タイマーリセット"""
        self.timer.stop()
        self.is_running = False
        self.is_work_session = True
        self.session_count = 0
        self.time_left = self.work_minutes * 60
        
        self.update_display()
        self.start_pause_btn.setText("▶️ 開始")
        self.status_label.setText("🟢 準備完了")
        
        logger.info("🔄 タイマーリセット")
        
    def update_timer(self):
        """タイマー更新"""
        if self.time_left > 0:
            self.time_left -= 1
            self.update_display()
            
            # 残り時間による色変更
            if self.time_left <= 10:
                self.time_label.setStyleSheet("""
                    color: #ffffff; 
                    background-color: rgba(231, 76, 60, 0.9); 
                    padding: 20px; 
                    border-radius: 15px;
                    border: 2px solid #c0392b;
                """)
            elif self.time_left <= 60:
                self.time_label.setStyleSheet("""
                    color: #2c3e50; 
                    background-color: rgba(241, 196, 15, 0.9); 
                    padding: 20px; 
                    border-radius: 15px;
                    border: 2px solid #f39c12;
                """)
                
        else:
            self.timer_finished_handler()
            
    def timer_finished_handler(self):
        """タイマー完了処理"""
        self.timer.stop()
        self.is_running = False
        
        if self.is_work_session:
            # 作業完了
            self.session_count += 1
            self.status_label.setText(f"🎉 作業完了！{self.break_minutes}分休憩します")
            self.time_left = self.break_minutes * 60
            self.is_work_session = False
            
            logger.info(f"✅ 作業セッション #{self.session_count} 完了")
            
            # 音声通知（利用可能な場合）
            self.play_notification()
            
        else:
            # 休憩完了
            self.status_label.setText("💪 休憩完了！次の作業を開始します")
            self.time_left = self.work_minutes * 60
            self.is_work_session = True
            
            logger.info("🔄 休憩完了、次の作業セッション準備")
            
        self.update_display()
        self.start_pause_btn.setText("▶️ 開始")
        
        # 自動で次のセッション開始
        self.start_timer()
        
    def update_display(self):
        """表示更新"""
        self.time_label.setText(self.format_time(self.time_left))
        
        if self.is_work_session:
            session_text = f"📖 作業セッション #{self.session_count + 1}"
            self.time_label.setStyleSheet("""
                color: #2c3e50; 
                background-color: rgba(255,255,255,0.9); 
                padding: 20px; 
                border-radius: 15px;
                border: 2px solid #3498db;
            """)
        else:
            session_text = f"☕ 休憩タイム"
            self.time_label.setStyleSheet("""
                color: #ffffff; 
                background-color: rgba(46, 204, 113, 0.9); 
                padding: 20px; 
                border-radius: 15px;
                border: 2px solid #27ae60;
            """)
            
        self.session_label.setText(session_text)
        
    def play_notification(self):
        """通知音再生（利用可能な場合）"""
        if AUDIO_AVAILABLE:
            try:
                # 基本的なビープ音（実装例）
                logger.info("🔔 通知音再生")
            except Exception as e:
                logger.warning(f"🔇 通知音エラー: {e}")
    
    def update_work_time(self, value):
        """作業時間更新"""
        self.work_minutes = value
        if self.is_work_session and not self.is_running:
            self.time_left = self.work_minutes * 60
            self.update_display()
            logger.info(f"⏰ 作業時間を{value}分に変更")
    
    def update_break_time(self, value):
        """休憩時間更新"""
        self.break_minutes = value
        if not self.is_work_session and not self.is_running:
            self.time_left = self.break_minutes * 60
            self.update_display()
            logger.info(f"☕ 休憩時間を{value}分に変更")

def main():
    """メイン実行（修正版）"""
    print("🚀 ポモドーロタイマー MVP 修正版 起動中...")
    logger.info("🚀 アプリケーション開始")
    
    # 環境変数設定
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    
    # WSL/Linux環境での表示設定
    if 'DISPLAY' not in os.environ and sys.platform.startswith('linux'):
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        logger.warning("⚠️ GUI環境未検出、オフスクリーンモードで実行")
    
    # QApplication作成
    app = QApplication(sys.argv)
    app.setApplicationName("Pomodoro Timer MVP Fixed")
    app.setApplicationVersion("1.0.0-fixed")
    
    try:
        # メインウィンドウ作成
        window = PomodoroTimer()
        window.show()
        
        print("✅ MVP修正版起動完了！")
        print("🍅 ポモドーロテクニックで集中力アップ！")
        print("📝 ログファイル: mvp_fixed.log")
        
        if AUDIO_AVAILABLE:
            print("🔊 音声機能: 有効")
        else:
            print("🔇 音声機能: 無効（エラー対応済み）")
            
        logger.info("✅ アプリケーション初期化完了")
        
        # イベントループ開始
        return app.exec()
        
    except Exception as e:
        error_msg = f"❌ 予期しないエラー: {e}"
        print(error_msg)
        logger.error(error_msg)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())