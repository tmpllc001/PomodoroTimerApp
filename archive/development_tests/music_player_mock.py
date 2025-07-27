#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音楽プレイヤーのモック実装
実際の音は出ないが、音楽再生の動作をシミュレート
"""

import time
import threading
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class MockMusicPlayer:
    """音楽再生をシミュレートするモッククラス"""
    
    def __init__(self):
        self.is_playing = False
        self.is_paused = False
        self.current_file = None
        self.volume = 0.7
        self.position = 0.0  # 再生位置（秒）
        self.duration = 0.0  # 曲の長さ（秒）
        self._thread = None
        self._stop_event = threading.Event()
        
        logger.info("🎵 MockMusicPlayer初期化")
    
    def load(self, file_path: str) -> bool:
        """音楽ファイルを読み込む"""
        path = Path(file_path)
        if not path.exists():
            logger.error(f"❌ ファイルが見つかりません: {file_path}")
            return False
        
        self.current_file = file_path
        # ファイルサイズから適当な長さを設定（実際は音楽ファイルのメタデータから取得）
        self.duration = 180.0  # 3分と仮定
        self.position = 0.0
        
        logger.info(f"✅ ファイル読み込み成功: {path.name}")
        return True
    
    def play(self) -> bool:
        """再生開始"""
        if not self.current_file:
            logger.error("❌ ファイルが読み込まれていません")
            return False
        
        if self.is_playing and not self.is_paused:
            logger.warning("⚠️  既に再生中です")
            return True
        
        if self.is_paused:
            # 一時停止からの再開
            self.is_paused = False
            logger.info("▶️  再生再開")
        else:
            # 新規再生
            self.is_playing = True
            self.is_paused = False
            self._stop_event.clear()
            
            # 再生スレッド開始
            self._thread = threading.Thread(target=self._play_thread, daemon=True)
            self._thread.start()
            
            logger.info(f"▶️  再生開始: {Path(self.current_file).name}")
        
        return True
    
    def pause(self) -> bool:
        """一時停止"""
        if not self.is_playing:
            logger.warning("⚠️  再生中ではありません")
            return False
        
        self.is_paused = True
        logger.info("⏸️  一時停止")
        return True
    
    def stop(self) -> bool:
        """停止"""
        if self.is_playing:
            self._stop_event.set()
            self.is_playing = False
            self.is_paused = False
            self.position = 0.0
            
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=1.0)
            
            logger.info("⏹️  停止")
        
        return True
    
    def set_volume(self, volume: float) -> bool:
        """音量設定（0.0〜1.0）"""
        if not 0.0 <= volume <= 1.0:
            logger.error(f"❌ 無効な音量: {volume}")
            return False
        
        self.volume = volume
        logger.info(f"🔊 音量設定: {int(volume * 100)}%")
        return True
    
    def get_position(self) -> float:
        """現在の再生位置を取得（秒）"""
        return self.position
    
    def seek(self, position: float) -> bool:
        """再生位置を設定（秒）"""
        if not 0.0 <= position <= self.duration:
            logger.error(f"❌ 無効な再生位置: {position}")
            return False
        
        self.position = position
        logger.info(f"⏩ シーク: {position:.1f}秒")
        return True
    
    def _play_thread(self):
        """再生をシミュレートするスレッド"""
        logger.info(f"🎵 再生スレッド開始（長さ: {self.duration}秒）")
        
        while not self._stop_event.is_set() and self.position < self.duration:
            if not self.is_paused:
                # 0.1秒ごとに位置を更新
                time.sleep(0.1)
                self.position += 0.1
                
                # 10秒ごとに進捗を報告
                if int(self.position) % 10 == 0 and self.position % 1.0 < 0.2:
                    progress = (self.position / self.duration) * 100
                    logger.info(f"🎵 再生中: {self.position:.0f}/{self.duration:.0f}秒 ({progress:.0f}%)")
            else:
                # 一時停止中
                time.sleep(0.1)
        
        if self.position >= self.duration:
            logger.info("🎵 再生完了")
            self.is_playing = False
            self.position = 0.0

# グローバルインスタンス
_mock_player = None

def get_mock_player() -> MockMusicPlayer:
    """モックプレイヤーのインスタンスを取得"""
    global _mock_player
    if _mock_player is None:
        _mock_player = MockMusicPlayer()
    return _mock_player

# 使用例
if __name__ == "__main__":
    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    print("🎵 MockMusicPlayer デモ")
    print("-" * 40)
    
    player = get_mock_player()
    
    # テスト用の仮想ファイル
    test_file = "assets/music/work_bgm.mp3"
    
    # ファイルが存在しない場合は作成
    Path("assets/music").mkdir(parents=True, exist_ok=True)
    Path(test_file).touch(exist_ok=True)
    
    # 再生テスト
    print("\n1. ファイル読み込み")
    player.load(test_file)
    
    print("\n2. 再生開始（5秒間）")
    player.play()
    time.sleep(5)
    
    print("\n3. 一時停止（2秒間）")
    player.pause()
    time.sleep(2)
    
    print("\n4. 再生再開（3秒間）")
    player.play()
    time.sleep(3)
    
    print("\n5. 音量変更")
    player.set_volume(0.3)
    time.sleep(2)
    
    print("\n6. 停止")
    player.stop()
    
    print("\n✅ デモ完了！")