#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音楽再生機能のテストプログラム
"""

import sys
import os
from pathlib import Path
import time

# 環境設定
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

print("🎵 音楽再生テスト開始...")

# 1. pygame.mixerの初期化テスト
print("\n1️⃣ pygame.mixer初期化テスト...")
try:
    import pygame.mixer
    pygame.mixer.init()
    print("✅ pygame.mixer初期化成功")
    print(f"   - 周波数: {pygame.mixer.get_init()[0]} Hz")
    print(f"   - チャンネル: {pygame.mixer.get_init()[2]}")
except Exception as e:
    print(f"❌ pygame.mixer初期化失敗: {e}")
    sys.exit(1)

# 2. 音楽ファイルの確認
print("\n2️⃣ 音楽ファイル確認...")
audio_dir = Path(__file__).parent / "assets" / "music"
audio_files = {
    'work_bgm.mp3': audio_dir / 'work_bgm.mp3',
    'break_bgm.mp3': audio_dir / 'break_bgm.mp3',
    'alert_1min.mp3': audio_dir / 'alert_1min.mp3',
    'alert_30sec.mp3': audio_dir / 'alert_30sec.mp3',
    'countdown_tick.mp3': audio_dir / 'countdown_tick.mp3'
}

existing_files = []
for name, path in audio_files.items():
    if path.exists():
        print(f"✅ {name} - 存在")
        existing_files.append((name, path))
    else:
        print(f"❌ {name} - 見つかりません")

if not existing_files:
    print("\n⚠️  音楽ファイルが見つかりません。デモ音楽を作成します...")
    
    # デモ音楽作成
    try:
        import numpy as np
        import wave
        
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        # 簡単なビープ音を作成
        sample_rate = 22050
        duration = 2.0
        frequency = 440  # A4
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        wave_data = (np.sin(frequency * 2 * np.pi * t) * 0.3 * 32767).astype(np.int16)
        
        # WAVファイルとして保存
        demo_file = audio_dir / "demo_beep.wav"
        with wave.open(str(demo_file), 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(wave_data.tobytes())
        
        print(f"✅ デモ音楽作成: {demo_file}")
        existing_files.append(("demo_beep.wav", demo_file))
        
    except ImportError:
        print("❌ numpy/waveが見つかりません。pygame内蔵音を使用します。")
        
        # pygame内蔵のサウンド生成
        try:
            # 単純なビープ音を生成
            frequency = 440
            sample_rate = 22050
            duration = 1
            n_samples = int(sample_rate * duration)
            
            # サイン波を生成
            buf = bytes([int(127.5 * (1 + pygame.math.Vector2(0, 1).rotate(360 * frequency * i / sample_rate).y)) 
                        for i in range(n_samples)])
            
            # Soundオブジェクトを作成
            sound = pygame.mixer.Sound(buffer=buf)
            demo_file = audio_dir / "demo_pygame.wav"
            
            print("✅ pygame内蔵サウンド生成")
            
        except Exception as e:
            print(f"❌ サウンド生成失敗: {e}")

# 3. 音楽再生テスト
if existing_files or 'sound' in locals():
    print("\n3️⃣ 音楽再生テスト...")
    
    # ファイルベースの再生
    if existing_files:
        test_file = existing_files[0][1]
        print(f"テストファイル: {test_file.name}")
        
        try:
            # pygame.mixer.musicを使用（MP3/OGG対応）
            if test_file.suffix in ['.mp3', '.ogg']:
                pygame.mixer.music.load(str(test_file))
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play()
                print("✅ 音楽再生開始（pygame.mixer.music）")
                print("   3秒間再生します...")
                time.sleep(3)
                pygame.mixer.music.stop()
                print("✅ 音楽停止")
            else:
                # WAVファイルはSoundオブジェクトで再生
                sound = pygame.mixer.Sound(str(test_file))
                sound.set_volume(0.5)
                channel = sound.play()
                print("✅ 音楽再生開始（pygame.mixer.Sound）")
                print("   3秒間再生します...")
                time.sleep(3)
                if channel:
                    channel.stop()
                print("✅ 音楽停止")
                
        except Exception as e:
            print(f"❌ 音楽再生エラー: {e}")
    
    # 内蔵サウンドの再生
    elif 'sound' in locals():
        try:
            channel = sound.play()
            print("✅ 内蔵サウンド再生開始")
            print("   2秒間再生します...")
            time.sleep(2)
            if channel:
                channel.stop()
            print("✅ サウンド停止")
        except Exception as e:
            print(f"❌ サウンド再生エラー: {e}")

# 4. 複数音声の同時再生テスト
print("\n4️⃣ 効果音テスト...")
try:
    # チャンネル数を増やす
    pygame.mixer.set_num_channels(8)
    
    # 簡単なクリック音を生成
    click_sound = pygame.mixer.Sound(buffer=bytes([
        int(127.5 * (1 + (-1 if i < 100 else 1))) 
        for i in range(200)
    ]))
    click_sound.set_volume(0.3)
    
    print("クリック音を3回再生...")
    for i in range(3):
        click_sound.play()
        print(f"  {i+1}回目")
        time.sleep(0.5)
    
    print("✅ 効果音テスト完了")
    
except Exception as e:
    print(f"❌ 効果音テストエラー: {e}")

# クリーンアップ
pygame.mixer.quit()
print("\n✅ 音楽再生テスト完了！")

# 推奨事項
print("\n📝 推奨事項:")
print("1. MP3ファイルを assets/music/ フォルダに配置してください")
print("2. ファイル名:")
print("   - work_bgm.mp3 (作業用BGM)")
print("   - break_bgm.mp3 (休憩用BGM)")
print("   - alert_1min.mp3 (1分前アラート)")
print("   - alert_30sec.mp3 (30秒前アラート)")
print("   - countdown_tick.mp3 (カウントダウン音)")