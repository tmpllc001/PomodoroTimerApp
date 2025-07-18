"""
MainWindow 統合テンプレート - 即座使用可能
Worker1用 - 15分でMVP完成
"""

from PyQt6.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout,
                             QWidget, QLabel, QProgressBar, QGroupBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from ..bridge.ui_bridge import UIBridge
from ..controllers.timer_controller import TimerController
from ..models.timer_model import TimerState, SessionType


class MainWindow(QMainWindow):
    """メインウィンドウ - 統合済みテンプレート."""
    
    def __init__(self):
        super().__init__()
        
        # バックエンド初期化
        self.timer_controller = TimerController()
        self.timer_controller.set_sound_enabled(False)  # WSL対応
        
        # UIBridge初期化
        self.ui_bridge = UIBridge(self.timer_controller, self)
        
        # UI構築
        self.setup_ui()
        self.setup_connections()
        
        # 初期表示更新
        self.update_display()
        
        print("🎯 ポモドーロタイマー起動完了")
        
    def setup_ui(self):
        """UI構築."""
        self.setWindowTitle("Pomodoro Timer MVP")
        self.setGeometry(100, 100, 400, 600)
        
        # メインウィジェット
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # タイマー表示セクション
        timer_group = QGroupBox("Timer")
        timer_layout = QVBoxLayout(timer_group)
        
        # Worker1の透明TimerDisplayを統合
        from .components.timer_display import TimerDisplay
        self.timer_display = TimerDisplay()
        timer_layout.addWidget(self.timer_display)
        
        # バックアップ用のシンプルラベル（統合テスト用）
        self.timer_label = QLabel("25:00")
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.timer_label.setFont(font)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("color: #666; background: transparent; padding: 10px;")
        timer_layout.addWidget(self.timer_label)
        
        # セッション情報
        self.session_label = QLabel("Work Session")
        self.session_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.session_label.setStyleSheet("font-size: 18px; color: #666; margin: 10px;")
        timer_layout.addWidget(self.session_label)
        
        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 3px;
            }
        """)
        timer_layout.addWidget(self.progress_bar)
        
        layout.addWidget(timer_group)
        
        # 制御ボタンセクション
        control_group = QGroupBox("Controls")
        control_layout = QVBoxLayout(control_group)
        
        # Worker1のControlPanelを統合
        from .components.control_panel import ControlPanel
        self.control_panel = ControlPanel()
        control_layout.addWidget(self.control_panel)
        
        # バックアップ用のシンプルボタン（統合テスト用）
        main_buttons_layout = QHBoxLayout()
        
        self.start_button = QPushButton("▶ Start")
        self.start_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-size: 16px; padding: 10px; border-radius: 5px; }")
        
        self.pause_button = QPushButton("⏸ Pause")
        self.pause_button.setStyleSheet("QPushButton { background-color: #FF9800; color: white; font-size: 16px; padding: 10px; border-radius: 5px; }")
        
        main_buttons_layout.addWidget(self.start_button)
        main_buttons_layout.addWidget(self.pause_button)
        control_layout.addLayout(main_buttons_layout)
        
        # 追加制御ボタン
        extra_buttons_layout = QHBoxLayout()
        
        self.stop_button = QPushButton("⏹ Stop")
        self.stop_button.setStyleSheet("QPushButton { background-color: #F44336; color: white; font-size: 14px; padding: 8px; border-radius: 5px; }")
        
        self.reset_button = QPushButton("🔄 Reset")
        self.reset_button.setStyleSheet("QPushButton { background-color: #9C27B0; color: white; font-size: 14px; padding: 8px; border-radius: 5px; }")
        
        self.skip_button = QPushButton("⏭ Skip")
        self.skip_button.setStyleSheet("QPushButton { background-color: #607D8B; color: white; font-size: 14px; padding: 8px; border-radius: 5px; }")
        
        extra_buttons_layout.addWidget(self.stop_button)
        extra_buttons_layout.addWidget(self.reset_button)
        extra_buttons_layout.addWidget(self.skip_button)
        control_layout.addLayout(extra_buttons_layout)
        
        layout.addWidget(control_group)
        
        # 統計セクション
        stats_group = QGroupBox("Today's Stats")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_label = QLabel("Sessions: 0 | Completed: 0 | Focus Time: 0min")
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stats_label.setStyleSheet("font-size: 14px; color: #333; padding: 10px;")
        stats_layout.addWidget(self.stats_label)
        
        layout.addWidget(stats_group)
        
    def setup_connections(self):
        """シグナル接続."""
        # UIBridgeが自動的にボタンを接続
        # 追加のシグナル接続
        self.ui_bridge.timer_updated.connect(self.update_display)
        self.ui_bridge.state_changed.connect(self.update_button_states)
        self.ui_bridge.session_completed.connect(self.on_session_complete)
        
        # Worker1コンポーネントとの連携
        if hasattr(self, 'control_panel'):
            self.control_panel.start_clicked.connect(self.timer_display.start_timer)
            self.control_panel.pause_clicked.connect(self.timer_display.pause_timer)
            self.control_panel.reset_clicked.connect(self.timer_display.reset_timer)
            
        # TimerDisplayのシグナル接続
        if hasattr(self, 'timer_display'):
            self.timer_display.timer_finished.connect(self.on_session_complete)
            self.timer_display.time_updated.connect(self.sync_timer_display)
        
    def update_display(self, timer_info=None):
        """表示更新."""
        if timer_info is None:
            timer_info = self.ui_bridge.get_timer_info()
            
        # タイマー表示（Worker1 TimerDisplayと連携）
        formatted_time = self.ui_bridge.format_time(timer_info['remaining_time'])
        self.timer_label.setText(formatted_time)
        
        # Worker1 TimerDisplayも更新
        if hasattr(self, 'timer_display'):
            self.timer_display.time_remaining = timer_info['remaining_time']
            self.timer_display.update_display()
        
        # セッション表示
        session_display = self.ui_bridge.get_session_type_display(timer_info['type'])
        self.session_label.setText(session_display)
        
        # プログレスバー
        progress = int(timer_info.get('progress', 0) * 100)
        self.progress_bar.setValue(progress)
        
        # 統計表示
        self.update_stats_display()
        
    def update_button_states(self, state):
        """ボタン状態更新."""
        if state == TimerState.STOPPED:
            self.start_button.setText("▶ Start")
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            
        elif state == TimerState.RUNNING:
            self.start_button.setEnabled(False)
            self.pause_button.setText("⏸ Pause")
            self.pause_button.setEnabled(True)
            
        elif state == TimerState.PAUSED:
            self.start_button.setText("▶ Resume")
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            
    def update_stats_display(self):
        """統計表示更新."""
        try:
            stats = self.ui_bridge.get_session_stats()
            today_sessions = self.ui_bridge.get_today_sessions()
            
            total_sessions = len(today_sessions)
            completed_sessions = len([s for s in today_sessions if s.completed])
            total_focus_time = sum(s.actual_duration or 0 for s in today_sessions 
                                  if s.session_type == SessionType.WORK and s.completed) // 60
            
            stats_text = f"Sessions: {total_sessions} | Completed: {completed_sessions} | Focus Time: {total_focus_time}min"
            self.stats_label.setText(stats_text)
            
        except Exception as e:
            print(f"統計表示エラー: {e}")
            
    def on_session_complete(self, session_type):
        """セッション完了時の処理."""
        session_name = self.ui_bridge.get_session_type_display(session_type)
        print(f"🎉 {session_name} 完了!")
        
        # 次のセッション情報表示
        timer_info = self.ui_bridge.get_timer_info()
        next_session = self.ui_bridge.get_session_type_display(timer_info['type'])
        print(f"次: {next_session}")
        
    def sync_timer_display(self, time_remaining):
        """Worker1 TimerDisplayとバックエンドの同期."""
        # Worker1のタイマーとバックエンドを同期
        try:
            if hasattr(self.ui_bridge, 'sync_time'):
                self.ui_bridge.sync_time(time_remaining)
        except Exception as e:
            print(f"タイマー同期エラー: {e}")
        
    def closeEvent(self, event):
        """アプリ終了時のクリーンアップ."""
        print("🔄 アプリ終了処理中...")
        self.ui_bridge.cleanup()
        self.timer_controller.cleanup()
        event.accept()
        print("✅ クリーンアップ完了")