#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal Pomodoro Timer - Standalone Version with Transparency
FavDesktopClock風のミニマルなタイマー（透明化改修版）
"""

import sys
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QLabel, QMenu, QMessageBox, QInputDialog, QColorDialog)
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSignal, QObject, QSettings, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QAction, QMouseEvent, QColor


class SimpleTimerModel:
    """シンプルなタイマーモデル"""
    def __init__(self):
        self.work_duration = 25 * 60  # 25分
        self.break_duration = 5 * 60   # 5分
        self.remaining_time = self.work_duration
        self.is_work_session = True
        self.is_running = False
        

class SimpleTimerController(QObject):
    """シンプルなタイマーコントローラー"""
    
    state_changed = pyqtSignal(str)
    time_updated = pyqtSignal(int)
    session_changed = pyqtSignal(bool)  # True=work, False=break
    countdown_triggered = pyqtSignal(int)  # カウントダウン数値
    
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        
    def start(self):
        """タイマー開始"""
        self.model.is_running = True
        self.timer.start(1000)  # 1秒ごと
        self.state_changed.emit("running")
        
    def pause(self):
        """一時停止"""
        self.model.is_running = False
        self.timer.stop()
        self.state_changed.emit("paused")
        
    def reset(self):
        """リセット"""
        self.pause()
        self.model.remaining_time = self.model.work_duration
        self.model.is_work_session = True
        self.time_updated.emit(self.model.remaining_time)
        self.state_changed.emit("reset")
        
    def tick(self):
        """タイマー更新（カウントダウン対応）"""
        if self.model.remaining_time > 0:
            # 作業セッション且つ残り3秒以下でカウントダウン
            if (self.model.is_work_session and 
                self.model.remaining_time <= 3 and 
                self.model.remaining_time > 0):
                self.countdown_triggered.emit(self.model.remaining_time)
            
            self.model.remaining_time -= 1
            self.time_updated.emit(self.model.remaining_time)
        else:
            # セッション切り替え
            self.switch_session()
            
    def switch_session(self):
        """セッション切り替え"""
        self.model.is_work_session = not self.model.is_work_session
        
        if self.model.is_work_session:
            self.model.remaining_time = self.model.work_duration
        else:
            self.model.remaining_time = self.model.break_duration
            
        self.session_changed.emit(self.model.is_work_session)
        self.time_updated.emit(self.model.remaining_time)


class MinimalTimerWindow(QMainWindow):
    """ミニマルタイマーウィンドウ（透明化改修版）"""
    
    def __init__(self):
        super().__init__()
        self.show_time = False
        self.dragging = False
        self.drag_position = QPoint()
        self.transparent_mode = True  # 透明モードフラグ
        
        # 設定管理
        self.settings = QSettings("MinimalTimer", "PomodoroTimer")
        
        # デフォルト表示設定（カウントダウン機能追加）
        self.default_settings = {
            'window_x': 1200,
            'window_y': 20,
            'text_color_r': 255,
            'text_color_g': 255,
            'text_color_b': 255,
            'text_alpha': 255,
            'font_size': 20,
            'show_time': False,
            'transparent_mode': True,
            'countdown_enabled': True,
            'countdown_duration': 3
        }
        
        # 表示設定（デフォルト値で初期化）
        self.text_color = QColor(255, 255, 255)  # デフォルト：白
        self.text_opacity = 255  # デフォルト：不透明
        self.font_size = 20  # デフォルト：20pt
        
        # カウントダウン関連設定
        self.countdown_enabled = True  # カウントダウン有効/無効
        self.countdown_duration = 3    # カウントダウン開始秒数
        self.countdown_animation = None  # アニメーション参照保持
        
        # モデルとコントローラー
        self.model = SimpleTimerModel()
        self.controller = SimpleTimerController(self.model)
        
        self.setup_ui()
        self.setup_connections()
        
        # 設定を読み込み適用
        self.load_settings()
        self.apply_loaded_settings()
        
        self.update_display()
        
    def setup_ui(self):
        """UI設定"""
        # メインウィジェット
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # レイアウト
        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(2)
        
        # 現在時刻
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setVisible(False)
        
        # タイマー
        self.timer_label = QLabel("25:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # カウントダウンラベル（通常は非表示）
        self.countdown_label = QLabel()
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setVisible(False)
        self.countdown_label.setObjectName("countdown_label")
        
        # 状態
        self.status_label = QLabel("作業")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.time_label)
        layout.addWidget(self.timer_label)
        layout.addWidget(self.countdown_label)
        layout.addWidget(self.status_label)
        
        # ウィンドウ設定
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # フォント（初期設定）
        self.update_fonts()
        
        # サイズ
        self.resize(110, 60)
        
        # 透明化設定の初期化
        self.apply_transparent_style()
        
        # コンテキストメニュー
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # 時刻更新タイマー
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        
    def apply_transparent_style(self):
        """透明化スタイルの適用（カウントダウン対応統合版）"""
        # 文字色設定を文字列に変換
        color_str = f"rgba({self.text_color.red()}, {self.text_color.green()}, {self.text_color.blue()}, {self.text_opacity})"
        
        if self.transparent_mode:
            # 完全透明化＋マウスイベント透過（カウントダウン中も維持）
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: rgba(0, 0, 0, 0);
                    border: none;
                }}
                QLabel {{
                    color: {color_str};
                    background-color: rgba(0, 0, 0, 0);
                    font-weight: bold;
                }}
                QLabel#countdown_label {{
                    background-color: rgba(50, 50, 50, 200);
                    border: 2px solid rgba(255, 255, 255, 100);
                    border-radius: 50px;
                    min-width: 100px;
                    min-height: 100px;
                    font-size: {self.font_size * 2}pt;
                    font-weight: bold;
                }}
            """)
        else:
            # 通常表示モード
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: rgba(40, 40, 40, 230);
                    border-radius: 10px;
                }}
                QLabel {{
                    color: {color_str};
                    background-color: rgba(0, 0, 0, 0);
                }}
                QLabel#countdown_label {{
                    background-color: rgba(70, 70, 70, 220);
                    border: 2px solid rgba(255, 255, 255, 150);
                    border-radius: 50px;
                    min-width: 100px;
                    min-height: 100px;
                    font-size: {self.font_size * 2}pt;
                    font-weight: bold;
                }}
            """)
        
    def setup_connections(self):
        """シグナル接続"""
        self.controller.time_updated.connect(self.update_timer)
        self.controller.session_changed.connect(self.on_session_changed)
        self.controller.countdown_triggered.connect(self.show_countdown)
        
    def show_context_menu(self, pos):
        """拡張コンテキストメニュー"""
        # 右クリック時は一時的に透明化を無効にする
        self.set_transparent_mode(False)
        
        menu = QMenu(self)
        
        # 時刻表示
        time_action = QAction("時刻表示", self)
        time_action.setCheckable(True)
        time_action.setChecked(self.show_time)
        time_action.triggered.connect(self.toggle_time)
        menu.addAction(time_action)
        
        # 透明化モード切り替え
        transparent_action = QAction("透明化モード", self)
        transparent_action.setCheckable(True)
        transparent_action.setChecked(self.transparent_mode)
        transparent_action.triggered.connect(self.toggle_transparent_mode)
        menu.addAction(transparent_action)
        
        menu.addSeparator()
        
        # 位置設定メニュー
        position_menu = QMenu("位置設定", self)
        
        # プリセット位置
        position_presets = [
            ("右上", lambda: self.move_to_preset("top_right")),
            ("左上", lambda: self.move_to_preset("top_left")),
            ("右下", lambda: self.move_to_preset("bottom_right")),
            ("左下", lambda: self.move_to_preset("bottom_left"))
        ]
        
        for name, callback in position_presets:
            action = QAction(name, self)
            action.triggered.connect(callback)
            position_menu.addAction(action)
            
        position_menu.addSeparator()
        
        # カスタム位置設定
        custom_pos_action = QAction("カスタム位置...", self)
        custom_pos_action.triggered.connect(self.set_custom_position)
        position_menu.addAction(custom_pos_action)
        
        menu.addMenu(position_menu)
        
        # 表示設定メニュー
        display_menu = QMenu("表示設定", self)
        
        # 文字色設定サブメニュー
        color_menu = QMenu("文字色", self)
        
        # プリセット色サブメニュー
        preset_color_menu = QMenu("プリセット色", self)
        
        preset_colors = [
            ("赤", QColor(255, 0, 0)),
            ("緑", QColor(0, 255, 0)),
            ("青", QColor(0, 0, 255)),
            ("黄", QColor(255, 255, 0)),
            ("白", QColor(255, 255, 255)),
            ("シアン", QColor(0, 255, 255)),
            ("マゼンタ", QColor(255, 0, 255))
        ]
        
        for name, color in preset_colors:
            action = QAction(name, self)
            action.triggered.connect(lambda checked, c=color: self.set_text_color(c))
            preset_color_menu.addAction(action)
            
        color_menu.addMenu(preset_color_menu)
        
        # カスタム色選択
        custom_color_action = QAction("カスタム色...", self)
        custom_color_action.triggered.connect(self.set_custom_color)
        color_menu.addAction(custom_color_action)
        
        display_menu.addMenu(color_menu)
        
        # 透明度設定
        opacity_action = QAction("透明度...", self)
        opacity_action.triggered.connect(self.set_text_opacity)
        display_menu.addAction(opacity_action)
        
        # フォントサイズ設定
        font_size_action = QAction("フォントサイズ...", self)
        font_size_action.triggered.connect(self.set_font_size)
        display_menu.addAction(font_size_action)
        
        menu.addMenu(display_menu)
        
        menu.addSeparator()
        
        # タイマー制御
        if self.model.is_running:
            pause_action = QAction("一時停止", self)
            pause_action.triggered.connect(self.controller.pause)
            menu.addAction(pause_action)
        else:
            start_action = QAction("開始", self)
            start_action.triggered.connect(self.controller.start)
            menu.addAction(start_action)
            
        reset_action = QAction("リセット", self)
        reset_action.triggered.connect(self.controller.reset)
        menu.addAction(reset_action)
        
        # カウントダウン設定サブメニュー
        countdown_menu = QMenu("カウントダウン設定", self)
        
        # カウントダウン有効/無効
        countdown_toggle_action = QAction("カウントダウン有効", self)
        countdown_toggle_action.setCheckable(True)
        countdown_toggle_action.setChecked(self.countdown_enabled)
        countdown_toggle_action.triggered.connect(self.toggle_countdown_enabled)
        countdown_menu.addAction(countdown_toggle_action)
        
        # カウントダウン秒数設定
        countdown_duration_action = QAction("カウントダウン秒数...", self)
        countdown_duration_action.triggered.connect(self.set_countdown_duration)
        countdown_menu.addAction(countdown_duration_action)
        
        countdown_menu.addSeparator()
        
        # デバッグ用：カウントダウンテスト
        countdown_test_action = QAction("カウントダウンテスト", self)
        countdown_test_action.triggered.connect(lambda: self.show_countdown(self.countdown_duration))
        countdown_menu.addAction(countdown_test_action)
        
        menu.addMenu(countdown_menu)
        
        # デモモード切り替え（30秒）
        demo_action = QAction("30秒デモモード", self)
        demo_action.setCheckable(True)
        demo_action.setChecked(self.model.work_duration == 30)
        demo_action.triggered.connect(self.toggle_demo_mode)
        menu.addAction(demo_action)
        
        menu.addSeparator()
        
        # 設定管理
        reset_settings_action = QAction("設定をリセット", self)
        reset_settings_action.triggered.connect(self.reset_to_defaults)
        menu.addAction(reset_settings_action)
        
        # 設定ファイルの場所を開く（デバッグ用）
        show_settings_action = QAction("設定ファイル場所", self)
        show_settings_action.triggered.connect(self.show_settings_location)
        menu.addAction(show_settings_action)
        
        menu.addSeparator()
        
        # 終了
        quit_action = QAction("終了", self)
        quit_action.triggered.connect(self.close_app)
        menu.addAction(quit_action)
        
        # メニュー閉じた後に元のモードに戻す
        menu.aboutToHide.connect(lambda: self.apply_transparent_style())
        menu.exec(self.mapToGlobal(pos))
        
    def toggle_time(self):
        """時刻表示切り替え"""
        self.show_time = not self.show_time
        self.time_label.setVisible(self.show_time)
        
        if self.show_time:
            self.resize(110, 80)
        else:
            self.resize(110, 60)
        
        # 設定保存
        self.save_settings()
    
    def toggle_transparent_mode(self):
        """透明化モード切り替え"""
        self.transparent_mode = not self.transparent_mode
        self.apply_transparent_style()
        # 設定保存
        self.save_settings()
    
    def set_transparent_mode(self, enabled):
        """透明化モードの一時設定（カウントダウン中も適切に処理）"""
        old_mode = self.transparent_mode
        self.transparent_mode = enabled
        self.apply_transparent_style()
        
        # カウントダウン表示中の場合、スタイルを再適用
        if self.countdown_label.isVisible():
            self.update_countdown_style()
        
        # 元の設定を復元（一時的な変更の場合）
        if not enabled and old_mode:
            QTimer.singleShot(100, lambda: setattr(self, 'transparent_mode', old_mode))
    
    def update_countdown_style(self):
        """カウントダウンラベルのスタイル更新"""
        color_str = f"rgba({self.text_color.red()}, {self.text_color.green()}, {self.text_color.blue()}, {self.text_opacity})"
        
        if self.transparent_mode:
            bg_color = "rgba(50, 50, 50, 200)"
            border_color = "rgba(255, 255, 255, 100)"
        else:
            bg_color = "rgba(70, 70, 70, 220)"
            border_color = "rgba(255, 255, 255, 150)"
            
        self.countdown_label.setStyleSheet(f"""
            QLabel {{
                color: {color_str};
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 50px;
                min-width: 100px;
                min-height: 100px;
                font-size: {self.font_size * 2}pt;
                font-weight: bold;
            }}
        """)
    
    def toggle_demo_mode(self):
        """30秒デモモード切り替え"""
        if self.model.work_duration == 30:
            # 通常モードに戻す
            self.model.work_duration = 25 * 60  # 25分
            self.model.break_duration = 5 * 60   # 5分
        else:
            # デモモードに切り替え
            self.model.work_duration = 30  # 30秒
            self.model.break_duration = 10  # 10秒
        
        # タイマーをリセット
        self.controller.reset()
        QMessageBox.information(
            self, "デモモード",
            f"{'30秒デモモード' if self.model.work_duration == 30 else '通常モード'}に切り替えました。"
        )
    
    def update_fonts(self):
        """フォント更新"""
        timer_font = QFont("Arial", self.font_size, QFont.Weight.Bold)
        self.timer_label.setFont(timer_font)
        
        # カウントダウンフォント（通常の2倍サイズ）
        countdown_font = QFont("Arial", self.font_size * 2, QFont.Weight.Bold)
        self.countdown_label.setFont(countdown_font)
        
        time_font = QFont("Arial", int(self.font_size * 0.6))
        self.time_label.setFont(time_font)
        
        status_font = QFont("Arial", int(self.font_size * 0.55))
        self.status_label.setFont(status_font)
    
    def show_countdown(self, count):
        """カウントダウン表示（統合版）"""
        # カウントダウンが無効の場合はスキップ
        if not self.countdown_enabled:
            return
            
        # カウントダウン表示の条件チェック
        if count > self.countdown_duration or count <= 0:
            return
            
        self.countdown_label.setText(str(count))
        self.countdown_label.setVisible(True)
        
        # 透明化モードに応じたスタイル設定
        self.update_countdown_style()
        
        # アニメーション開始（メモリリーク対策）
        self.animate_countdown(count)
    
    def hide_countdown(self):
        """カウントダウン非表示（メモリリーク対策強化）"""
        self.countdown_label.setVisible(False)
        
        # アニメーションを安全に停止・削除
        if self.countdown_animation is not None:
            try:
                self.countdown_animation.stop()
                self.countdown_animation.deleteLater()
            except Exception as e:
                print(f"カウントダウンアニメーション停止エラー: {e}")
            finally:
                self.countdown_animation = None
    
    def animate_countdown(self, count):
        """カウントダウンアニメーション（メモリ効率最適化版）"""
        try:
            # 既存アニメーションを停止
            if self.countdown_animation is not None:
                self.countdown_animation.stop()
                self.countdown_animation.deleteLater()
            
            # スケールアニメーション作成
            self.countdown_animation = QPropertyAnimation(self.countdown_label, b"geometry")
            self.countdown_animation.setDuration(800)  # 0.8秒
            self.countdown_animation.setEasingCurve(QEasingCurve.Type.OutElastic)
            
            # 開始と終了のサイズを設定
            current_rect = self.countdown_label.geometry()
            start_size = 60  # 小さく開始
            end_size = 120   # 大きく表示
            
            # アニメーション設定
            start_rect = current_rect
            start_rect.setSize(start_rect.size())
            
            end_rect = current_rect
            end_rect.setWidth(end_size)
            end_rect.setHeight(end_size)
            end_rect.moveCenter(current_rect.center())
            
            self.countdown_animation.setStartValue(start_rect)
            self.countdown_animation.setEndValue(end_rect)
            
            # アニメーション開始
            self.countdown_animation.start()
            
            # 1秒後に次のカウントまたは終了（エラーハンドリング付き）
            if count > 1:
                QTimer.singleShot(1000, lambda: self.show_countdown(count - 1))
            else:
                QTimer.singleShot(1000, self.hide_countdown)
                
        except Exception as e:
            print(f"カウントダウンアニメーションエラー: {e}")
            # エラー時はアニメーションなしで表示継続
            if count > 1:
                QTimer.singleShot(1000, lambda: self.show_countdown(count - 1))
            else:
                QTimer.singleShot(1000, self.hide_countdown)
    
    def move_to_preset(self, position):
        """プリセット位置に移動"""
        if not QApplication.primaryScreen():
            return
            
        screen = QApplication.primaryScreen().geometry()
        window_size = self.size()
        margin = 20
        
        positions = {
            "top_right": (screen.width() - window_size.width() - margin, margin),
            "top_left": (margin, margin),
            "bottom_right": (screen.width() - window_size.width() - margin, 
                           screen.height() - window_size.height() - margin),
            "bottom_left": (margin, screen.height() - window_size.height() - margin)
        }
        
        if position in positions:
            x, y = positions[position]
            self.move(x, y)
            # 設定保存
            self.save_settings()
    
    def set_custom_position(self):
        """カスタム位置設定ダイアログ"""
        current_pos = self.pos()
        
        # X座標入力
        x, ok = QInputDialog.getInt(
            self, "カスタム位置設定", "X座標:", 
            current_pos.x(), 0, 9999
        )
        if not ok:
            return
            
        # Y座標入力
        y, ok = QInputDialog.getInt(
            self, "カスタム位置設定", "Y座標:", 
            current_pos.y(), 0, 9999
        )
        if ok:
            self.move(x, y)
            # 設定保存
            self.save_settings()
    
    def set_text_color(self, color):
        """文字色設定"""
        self.text_color = color
        self.apply_transparent_style()
        # 設定保存
        self.save_settings()
    
    def set_custom_color(self):
        """カスタム色選択ダイアログ"""
        color = QColorDialog.getColor(self.text_color, self, "文字色を選択")
        if color.isValid():
            self.set_text_color(color)
    
    def set_text_opacity(self):
        """透明度設定ダイアログ"""
        opacity, ok = QInputDialog.getInt(
            self, "透明度設定", "透明度 (0-255):", 
            self.text_opacity, 0, 255
        )
        if ok:
            self.text_opacity = opacity
            self.apply_transparent_style()
            # 設定保存
            self.save_settings()
    
    def set_font_size(self):
        """フォントサイズ設定ダイアログ"""
        size, ok = QInputDialog.getInt(
            self, "フォントサイズ設定", "フォントサイズ (10-36):", 
            self.font_size, 10, 36
        )
        if ok:
            self.font_size = size
            self.update_fonts()
            # 設定保存
            self.save_settings()
    
    def toggle_countdown_enabled(self):
        """カウントダウン有効/無効切り替え"""
        self.countdown_enabled = not self.countdown_enabled
        # 設定保存
        self.save_settings()
        
        # カウントダウンが無効になった場合は表示を隠す
        if not self.countdown_enabled and self.countdown_label.isVisible():
            self.hide_countdown()
    
    def set_countdown_duration(self):
        """カウントダウン秒数設定ダイアログ"""
        duration, ok = QInputDialog.getInt(
            self, "カウントダウン秒数設定", "カウントダウン開始秒数 (1-10):", 
            self.countdown_duration, 1, 10
        )
        if ok:
            self.countdown_duration = duration
            # 設定保存
            self.save_settings()
            
    def update_display(self):
        """表示更新"""
        minutes = self.model.remaining_time // 60
        seconds = self.model.remaining_time % 60
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")
        
        if self.model.is_work_session:
            self.status_label.setText("作業")
            self.timer_label.setStyleSheet("color: #00FF00;")
        else:
            self.status_label.setText("休憩")
            self.timer_label.setStyleSheet("color: #00AAFF;")
            
    def update_timer(self, remaining):
        """タイマー更新"""
        self.model.remaining_time = remaining
        self.update_display()
        
    def update_clock(self):
        """時刻更新"""
        if self.show_time:
            current = datetime.now().strftime("%H:%M:%S")
            self.time_label.setText(current)
            
    def on_session_changed(self, is_work):
        """セッション変更"""
        # セッション変更時はカウントダウンを隠す
        self.hide_countdown()
        
        if not is_work:
            # 休憩開始
            self.show_break_window()
        else:
            # 作業再開
            if hasattr(self, 'break_window'):
                self.break_window.close()
                
    def show_break_window(self):
        """休憩ウィンドウ表示"""
        self.break_window = BreakWindow(self.controller)
        self.break_window.show()
        
    # マウスイベント（Alt+クリックでドラッグ可能、右クリックでメニュー）
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.RightButton:
            # 右クリック時：メニュー表示のため一時的に透明化を無効
            pass  # show_context_menuで処理
        elif (event.button() == Qt.MouseButton.LeftButton and 
              event.modifiers() == Qt.KeyboardModifier.AltModifier):
            # Alt+左クリック時：ドラッグモード
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.set_transparent_mode(False)  # ドラッグ中は透明化を無効
            
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.dragging:
            self.dragging = False
            # ドラッグ終了後、透明化を再有効化
            self.apply_transparent_style()
            # 位置変更の設定保存
            self.save_settings()

    # ========================================
    # 設定管理メソッド
    # ========================================
    
    def save_settings(self):
        """設定を保存"""
        try:
            # ウィンドウ位置
            pos = self.pos()
            self.settings.setValue("Position/x", pos.x())
            self.settings.setValue("Position/y", pos.y())
            
            # 表示設定
            self.settings.setValue("Display/text_color_r", self.text_color.red())
            self.settings.setValue("Display/text_color_g", self.text_color.green())
            self.settings.setValue("Display/text_color_b", self.text_color.blue())
            self.settings.setValue("Display/text_alpha", self.text_opacity)
            self.settings.setValue("Display/font_size", self.font_size)
            
            # UI設定
            self.settings.setValue("UI/show_time", self.show_time)
            self.settings.setValue("UI/transparent_mode", self.transparent_mode)
            
            # カウントダウン設定
            self.settings.setValue("Countdown/enabled", self.countdown_enabled)
            self.settings.setValue("Countdown/duration", self.countdown_duration)
            
            # 設定を即座にファイルに書き込み
            self.settings.sync()
            
        except Exception as e:
            print(f"設定保存エラー: {e}")

    def load_settings(self):
        """設定を読み込み"""
        try:
            # デフォルト値を使用して設定を読み込み
            self.loaded_x = int(self.settings.value("Position/x", self.default_settings['window_x']))
            self.loaded_y = int(self.settings.value("Position/y", self.default_settings['window_y']))
            
            # 文字色
            r = int(self.settings.value("Display/text_color_r", self.default_settings['text_color_r']))
            g = int(self.settings.value("Display/text_color_g", self.default_settings['text_color_g']))
            b = int(self.settings.value("Display/text_color_b", self.default_settings['text_color_b']))
            self.text_color = QColor(r, g, b)
            
            self.text_opacity = int(self.settings.value("Display/text_alpha", self.default_settings['text_alpha']))
            self.font_size = int(self.settings.value("Display/font_size", self.default_settings['font_size']))
            
            # UI設定（文字列から bool に変換）
            show_time_str = self.settings.value("UI/show_time", str(self.default_settings['show_time']))
            self.show_time = show_time_str.lower() == 'true' if isinstance(show_time_str, str) else bool(show_time_str)
            
            transparent_mode_str = self.settings.value("UI/transparent_mode", str(self.default_settings['transparent_mode']))
            self.transparent_mode = transparent_mode_str.lower() == 'true' if isinstance(transparent_mode_str, str) else bool(transparent_mode_str)
            
            # カウントダウン設定
            countdown_enabled_str = self.settings.value("Countdown/enabled", str(self.default_settings['countdown_enabled']))
            self.countdown_enabled = countdown_enabled_str.lower() == 'true' if isinstance(countdown_enabled_str, str) else bool(countdown_enabled_str)
            
            self.countdown_duration = int(self.settings.value("Countdown/duration", self.default_settings['countdown_duration']))
            
        except Exception as e:
            print(f"設定読み込みエラー: {e}")
            # エラー時はデフォルト値を使用
            self.reset_to_defaults()

    def apply_loaded_settings(self):
        """読み込んだ設定をUIに適用"""
        try:
            # ウィンドウ位置
            self.move(self.loaded_x, self.loaded_y)
            
            # フォント設定を適用
            self.update_fonts()
            
            # 時刻表示設定
            self.time_label.setVisible(self.show_time)
            if self.show_time:
                self.resize(110, 80)
            else:
                self.resize(110, 60)
            
            # 透明化設定を適用
            self.apply_transparent_style()
            
        except Exception as e:
            print(f"設定適用エラー: {e}")

    def reset_to_defaults(self):
        """デフォルト設定にリセット"""
        try:
            # 確認ダイアログ
            reply = QMessageBox.question(
                self, "設定リセット確認", 
                "すべての設定をデフォルトに戻しますか？", 
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # 設定ファイルをクリア
                self.settings.clear()
                
                # デフォルト値を設定
                self.text_color = QColor(
                    self.default_settings['text_color_r'],
                    self.default_settings['text_color_g'], 
                    self.default_settings['text_color_b']
                )
                self.text_opacity = self.default_settings['text_alpha']
                self.font_size = self.default_settings['font_size']
                self.show_time = self.default_settings['show_time']
                self.transparent_mode = self.default_settings['transparent_mode']
                self.countdown_enabled = self.default_settings['countdown_enabled']
                self.countdown_duration = self.default_settings['countdown_duration']
                
                # デフォルト位置に移動
                self.move(self.default_settings['window_x'], self.default_settings['window_y'])
                
                # UI更新
                self.update_fonts()
                self.time_label.setVisible(self.show_time)
                if self.show_time:
                    self.resize(110, 80)
                else:
                    self.resize(110, 60)
                self.apply_transparent_style()
                
                # 設定保存
                self.save_settings()
                
                # 完了メッセージ
                QMessageBox.information(self, "設定リセット", "設定をデフォルトに戻しました。")
                
        except Exception as e:
            print(f"設定リセットエラー: {e}")
            QMessageBox.warning(self, "エラー", f"設定リセット中にエラーが発生しました：{e}")

    def show_settings_location(self):
        """設定ファイルの場所を表示"""
        try:
            import os
            settings_path = self.settings.fileName()
            
            # 設定ファイルが存在するかチェック
            if os.path.exists(settings_path):
                message = f"設定ファイル場所:\n{settings_path}\n\n設定内容:\n"
                
                # 現在の設定値を表示
                message += f"位置: ({self.pos().x()}, {self.pos().y()})\n"
                message += f"文字色: RGB({self.text_color.red()}, {self.text_color.green()}, {self.text_color.blue()})\n"
                message += f"透明度: {self.text_opacity}\n"
                message += f"フォントサイズ: {self.font_size}pt\n"
                message += f"時刻表示: {'ON' if self.show_time else 'OFF'}\n"
                message += f"透明化モード: {'ON' if self.transparent_mode else 'OFF'}\n"
                message += f"カウントダウン: {'ON' if self.countdown_enabled else 'OFF'} ({self.countdown_duration}秒)"
            else:
                message = f"設定ファイル（予定場所）:\n{settings_path}\n\n設定を変更すると作成されます。"
            
            QMessageBox.information(self, "設定ファイル情報", message)
            
        except Exception as e:
            QMessageBox.warning(self, "エラー", f"設定ファイル情報の取得中にエラーが発生しました：{e}")

    def close_app(self):
        """アプリケーション終了前の処理"""
        try:
            # 最新の設定を保存
            self.save_settings()
        except Exception as e:
            print(f"終了時設定保存エラー: {e}")
        finally:
            QApplication.quit()


class BreakWindow(QMainWindow):
    """休憩ウィンドウ"""
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()
        
        # タイマー更新
        self.controller.time_updated.connect(self.update_timer)
        
    def setup_ui(self):
        """UI設定"""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # メインウィジェット
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # メッセージ
        self.message = QLabel("休憩時間です！")
        self.message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        
        # タイマー
        self.timer_label = QLabel("05:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setFont(QFont("Arial", 48, QFont.Weight.Bold))
        
        # ヒント
        self.hint = QLabel("ストレッチをしたり、水を飲みましょう")
        self.hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint.setFont(QFont("Arial", 14))
        
        layout.addStretch()
        layout.addWidget(self.message)
        layout.addWidget(self.timer_label)
        layout.addWidget(self.hint)
        layout.addStretch()
        
        # スタイル
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 240);
                border-radius: 20px;
            }
            QLabel {
                color: white;
            }
        """)
        
        self.resize(500, 400)
        
        # 中央配置
        if QApplication.primaryScreen():
            center = QApplication.primaryScreen().geometry().center()
            self.move(center.x() - 250, center.y() - 200)
            
    def update_timer(self, remaining):
        """タイマー更新"""
        minutes = remaining // 60
        seconds = remaining % 60
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")
        

def main():
    """メイン関数"""
    app = QApplication(sys.argv)
    app.setApplicationName("Minimal Pomodoro (Transparent)")
    
    # メインウィンドウ
    window = MinimalTimerWindow()
    window.show()
    
    # 画面右上に配置
    if QApplication.primaryScreen():
        screen = QApplication.primaryScreen().geometry()
        window.move(screen.width() - window.width() - 20, 20)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()