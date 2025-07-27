#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pomodoro Timer - Phase 3とMinimal Timerの最小限統合版
動作確認済みのmain_phase3_with_tasks.pyをベースに透明化機能を追加
"""

import sys
import os

# main_phase3_with_tasks.pyの内容をベースに使用
exec(open('main_phase3_with_tasks.py').read(), globals())

# 追加の透明化機能
def add_transparency_features():
    """既存のメインウィンドウに透明化機能を追加"""
    
    # メインウィンドウクラスを拡張
    original_init = PomodoroTimerPhase3.__init__
    
    def new_init(self):
        original_init(self)
        
        # 透明化設定を追加
        self.transparent_mode = False
        
        # ビューメニューに透明化オプションを追加
        if hasattr(self, 'menuBar'):
            view_menu = self.menuBar().addMenu('表示')
            
            # 透明化アクション
            transparent_action = view_menu.addAction('透明化モード')
            transparent_action.setCheckable(True)
            transparent_action.triggered.connect(self.toggle_transparency)
            
            # ミニマルモードアクション
            minimal_action = view_menu.addAction('ミニマルモード')
            minimal_action.triggered.connect(self.switch_to_minimal)
    
    def toggle_transparency(self):
        """透明化切り替え"""
        self.transparent_mode = not self.transparent_mode
        
        if self.transparent_mode:
            self.setWindowOpacity(0.5)
            self.setStyleSheet("""
                QMainWindow {
                    background-color: rgba(0, 0, 0, 50);
                }
                QLabel {
                    color: white;
                    font-weight: bold;
                }
            """)
        else:
            self.setWindowOpacity(1.0)
            self.setStyleSheet("")
    
    def switch_to_minimal(self):
        """ミニマルモードへ切り替え"""
        # 現在のタイマー状態を保存
        from minimal_timer_standalone import MinimalTimer
        
        # ミニマルタイマーを起動
        self.minimal_window = MinimalTimer()
        self.minimal_window.work_minutes = self.work_duration_spin.value()
        self.minimal_window.break_minutes = self.break_duration_spin.value()
        self.minimal_window.show()
        
        # メインウィンドウを隠す
        self.hide()
        
        # ミニマルウィンドウが閉じられたらメインウィンドウを再表示
        self.minimal_window.destroyed.connect(self.show)
    
    # メソッドを追加
    PomodoroTimerPhase3.__init__ = new_init
    PomodoroTimerPhase3.toggle_transparency = toggle_transparency
    PomodoroTimerPhase3.switch_to_minimal = switch_to_minimal


# 透明化機能を追加してから実行
if __name__ == "__main__":
    add_transparency_features()
    # 元のmain関数は既に実行される