#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ウィンドウサイズ自動制御機能
Phase 2 追加機能
"""

import logging
from PyQt6.QtCore import QPropertyAnimation, QRect, QEasingCurve, QTimer
from PyQt6.QtWidgets import QApplication

logger = logging.getLogger(__name__)

class WindowResizer:
    """ウィンドウサイズ自動制御クラス"""
    
    WINDOW_SIZES = {
        'work': {
            'width': 200,
            'height': 100,
            'opacity': 0.7
        },
        'break': {
            'width': 600,
            'height': 400,
            'opacity': 0.95
        },
        'default': {
            'width': 450,
            'height': 350,
            'opacity': 0.9
        }
    }
    
    def __init__(self, window):
        self.window = window
        self.current_size = 'default'
        self.auto_resize_enabled = True
        self.resize_animation = None
        self.opacity_animation = None
        
        logger.info("🪟 ウィンドウリサイザー初期化完了")
    
    def resize_window(self, session_type, animate=True):
        """セッションタイプに応じてウィンドウをリサイズ"""
        if not self.auto_resize_enabled:
            return
            
        if session_type == 'work':
            target_config = self.WINDOW_SIZES['work']
        elif session_type == 'break':
            target_config = self.WINDOW_SIZES['break']
        else:
            target_config = self.WINDOW_SIZES['default']
        
        if animate:
            self._animate_resize(target_config)
        else:
            self._instant_resize(target_config)
        
        self.current_size = session_type
        logger.info(f"🪟 ウィンドウサイズ変更: {session_type} ({target_config['width']}x{target_config['height']})")
    
    def _animate_resize(self, target_config):
        """アニメーション付きリサイズ"""
        current_geometry = self.window.geometry()
        
        # 作業中は右上、休憩中は中央に配置
        if self.current_size == 'work':
            # 右上角配置
            screen = QApplication.primaryScreen()
            screen_geometry = screen.geometry()
            new_x = screen_geometry.width() - target_config['width'] - 20
            new_y = 20
        else:
            # 中央配置
            screen = QApplication.primaryScreen()
            screen_geometry = screen.geometry()
            new_x = (screen_geometry.width() - target_config['width']) // 2
            new_y = (screen_geometry.height() - target_config['height']) // 2
        
        target_geometry = QRect(
            new_x, new_y,
            target_config['width'],
            target_config['height']
        )
        
        # ジオメトリアニメーション
        self.resize_animation = QPropertyAnimation(self.window, b"geometry")
        self.resize_animation.setDuration(500)
        self.resize_animation.setStartValue(current_geometry)
        self.resize_animation.setEndValue(target_geometry)
        self.resize_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # 透明度アニメーション
        self.opacity_animation = QPropertyAnimation(self.window, b"windowOpacity")
        self.opacity_animation.setDuration(500)
        self.opacity_animation.setStartValue(self.window.windowOpacity())
        self.opacity_animation.setEndValue(target_config['opacity'])
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # アニメーション開始
        self.resize_animation.start()
        self.opacity_animation.start()
    
    def _instant_resize(self, target_config):
        """即座にリサイズ"""
        current_geometry = self.window.geometry()
        
        # 作業中は右上、休憩中は中央に配置
        if self.current_size == 'work':
            # 右上角配置
            screen = QApplication.primaryScreen()
            screen_geometry = screen.geometry()
            new_x = screen_geometry.width() - target_config['width'] - 20
            new_y = 20
        else:
            # 中央配置
            screen = QApplication.primaryScreen()
            screen_geometry = screen.geometry()
            new_x = (screen_geometry.width() - target_config['width']) // 2
            new_y = (screen_geometry.height() - target_config['height']) // 2
        
        self.window.setGeometry(
            new_x, new_y,
            target_config['width'],
            target_config['height']
        )
        self.window.setWindowOpacity(target_config['opacity'])
    
    def center_window(self):
        """ウィンドウを画面中央に配置"""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        window_geometry = self.window.frameGeometry()
        
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.window.move(window_geometry.topLeft())
    
    def toggle_auto_resize(self, enabled):
        """自動リサイズのON/OFF"""
        self.auto_resize_enabled = enabled
        logger.info(f"🪟 自動リサイズ: {'有効' if enabled else '無効'}")
    
    def get_current_size(self):
        """現在のサイズタイプを取得"""
        return self.current_size
    
    def is_auto_resize_enabled(self):
        """自動リサイズが有効かどうか"""
        return self.auto_resize_enabled