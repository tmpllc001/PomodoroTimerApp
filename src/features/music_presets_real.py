#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
実際の音声再生を行うMusicPresetsクラス
Windows環境で使用
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# pygame.mixerのインポートと初期化
AUDIO_AVAILABLE = False
try:
    import pygame.mixer
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    AUDIO_AVAILABLE = True
    logger.info("🔊 音声システム初期化成功")
except Exception as e:
    logger.warning(f"⚠️ 音声システム利用不可: {e}")

class MusicPresetsReal:
    """実際の音声再生を行うクラス"""
    
    def __init__(self):
        self.current_preset = None
        self.music_enabled = True
        self.volume = 0.7
        self.is_playing = False
        
        # 音楽ファイルのパス
        self.base_path = Path(__file__).parent.parent.parent / "assets" / "music"
        self.presets = {
            'work': self.base_path / 'work_bgm.mp3',
            'break': self.base_path / 'break_bgm.mp3'
        }
        
        self.alerts = {
            '1min': self.base_path / 'alert_1min.mp3',
            '30sec': self.base_path / 'alert_30sec.mp3',
            '5sec': self.base_path / 'countdown_tick.mp3',
            '3sec': self.base_path / 'countdown_tick.mp3'
        }
        
        # アラート音用のSoundオブジェクトをキャッシュ
        self.alert_sounds = {}
        if AUDIO_AVAILABLE:
            self._load_alert_sounds()
        
        self.logger = logger
        
    def _load_alert_sounds(self):
        """アラート音を事前に読み込む"""
        for key, path in self.alerts.items():
            if path.exists():
                try:
                    self.alert_sounds[key] = pygame.mixer.Sound(str(path))
                    self.alert_sounds[key].set_volume(0.8)
                    logger.info(f"✅ アラート音読み込み: {key}")
                except Exception as e:
                    logger.warning(f"⚠️ アラート音読み込み失敗 {key}: {e}")
    
    def play(self):
        """現在のプリセットを再生"""
        if not AUDIO_AVAILABLE or not self.music_enabled:
            return
        
        if self.current_preset and self.current_preset in self.presets:
            music_file = self.presets[self.current_preset]
            if music_file.exists():
                try:
                    pygame.mixer.music.load(str(music_file))
                    pygame.mixer.music.set_volume(self.volume)
                    pygame.mixer.music.play(-1)  # ループ再生
                    self.is_playing = True
                    logger.info(f"🎵 音楽再生開始: {self.current_preset}")
                except Exception as e:
                    logger.error(f"❌ 音楽再生エラー: {e}")
            else:
                logger.warning(f"⚠️ 音楽ファイルが見つかりません: {music_file}")
    
    def pause(self):
        """一時停止"""
        if AUDIO_AVAILABLE and self.is_playing:
            try:
                pygame.mixer.music.pause()
                logger.info("⏸️ 音楽一時停止")
            except Exception as e:
                logger.error(f"❌ 一時停止エラー: {e}")
    
    def stop(self):
        """停止"""
        if AUDIO_AVAILABLE:
            try:
                pygame.mixer.music.stop()
                self.is_playing = False
                logger.info("⏹️ 音楽停止")
            except Exception as e:
                logger.error(f"❌ 停止エラー: {e}")
    
    def set_preset(self, preset_name):
        """プリセット設定"""
        self.current_preset = preset_name
        logger.info(f"🎵 プリセット変更: {preset_name}")
        
        # 既に再生中の場合は新しいプリセットで再生開始
        if self.is_playing:
            self.play()
    
    def play_alert(self, alert_type):
        """アラート音再生"""
        if not AUDIO_AVAILABLE or not self.music_enabled:
            return
        
        if alert_type in self.alert_sounds:
            try:
                # 音楽の音量を一時的に下げる
                current_volume = pygame.mixer.music.get_volume()
                pygame.mixer.music.set_volume(current_volume * 0.3)
                
                # アラート音を再生
                self.alert_sounds[alert_type].play()
                logger.info(f"🔔 アラート音再生: {alert_type}")
                
                # 音量を戻す（アラート音の長さ後）
                def restore_volume():
                    pygame.mixer.music.set_volume(current_volume)
                
                # 簡易的に1秒後に音量を戻す
                import threading
                threading.Timer(1.0, restore_volume).start()
                
            except Exception as e:
                logger.error(f"❌ アラート音再生エラー: {e}")
        else:
            logger.warning(f"⚠️ アラート音が見つかりません: {alert_type}")
    
    def set_volume(self, volume):
        """音量設定（0.0-1.0）"""
        self.volume = max(0.0, min(1.0, volume))
        if AUDIO_AVAILABLE:
            try:
                pygame.mixer.music.set_volume(self.volume)
                logger.info(f"🔊 音量設定: {int(self.volume * 100)}%")
            except Exception as e:
                logger.error(f"❌ 音量設定エラー: {e}")
    
    def enable(self, enabled):
        """音楽機能の有効/無効"""
        self.music_enabled = enabled
        if not enabled:
            self.stop()
        logger.info(f"🎵 音楽機能: {'有効' if enabled else '無効'}")
    
    def get_available_presets(self):
        """利用可能なプリセット"""
        return {
            'work': 'Work BGM (25 min focus music)',
            'break': 'Break BGM (5 min relaxation)'
        }
    
    def get_preset_info(self, preset_name):
        """プリセット情報"""
        preset_path = self.presets.get(preset_name)
        return {
            'name': preset_name.title() + ' Mode',
            'file': str(preset_path) if preset_path else '',
            'exists': preset_path.exists() if preset_path else False
        }
    
    def get_session_status(self):
        """セッション状態"""
        return {
            'is_active': self.is_playing,
            'session_type': self.current_preset,
            'is_playing': self.is_playing,
            'is_muted': not self.music_enabled,
            'volume': self.volume,
            'music_enabled': self.music_enabled,
            'current_preset': self.current_preset
        }

# MusicPresetsSimpleと同じインターフェースを提供
MusicPresetsSimple = MusicPresetsReal