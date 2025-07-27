#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows環境での音声テスト
このスクリプトをWindowsのコマンドプロンプトで実行してください
"""

import sys
import os

print("🔊 Windows音声テスト")
print("=" * 50)

# 1. pygame.mixerのテスト
print("\n1️⃣ pygame.mixerの初期化テスト...")
try:
    import pygame.mixer
    pygame.mixer.init()
    print("✅ pygame.mixer初期化成功！")
    print(f"  - サンプルレート: {pygame.mixer.get_init()[0]} Hz")
    print(f"  - チャンネル数: {pygame.mixer.get_init()[2]}")
    
    # 簡単なビープ音を生成
    print("\n2️⃣ テスト音の生成...")
    import math
    sample_rate = 22050
    duration = 0.5  # 0.5秒
    frequency = 880  # A5
    
    # サンプル数
    n_samples = int(sample_rate * duration)
    
    # 波形データ生成（pygame用）
    max_sample = 2**(16-1) - 1
    wavedata = []
    
    for i in range(n_samples):
        value = int(max_sample * 0.5 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
        # ステレオ（左右同じ音）
        wavedata.append([value, value])
    
    # Soundオブジェクト作成
    import array
    sound_array = array.array('h')  # signed short
    for sample in wavedata:
        sound_array.extend(sample)
    
    sound = pygame.mixer.Sound(sound_array)
    
    print("✅ テスト音生成成功！")
    
    # 音を再生
    print("\n3️⃣ テスト音を再生します（0.5秒）...")
    channel = sound.play()
    
    import time
    time.sleep(1)
    
    print("✅ 音声再生成功！")
    
    # MP3ファイルのテスト
    print("\n4️⃣ MP3ファイルのテスト...")
    test_mp3 = "assets/music/work_bgm.mp3"
    
    if os.path.exists(test_mp3):
        pygame.mixer.music.load(test_mp3)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play()
        print(f"✅ {test_mp3} を再生中...")
        print("  （3秒後に停止します）")
        time.sleep(3)
        pygame.mixer.music.stop()
    else:
        print(f"⚠️  {test_mp3} が見つかりません")
        print("  MP3ファイルを配置してください")
    
    pygame.mixer.quit()
    
except ImportError:
    print("❌ pygameがインストールされていません")
    print("  pip install pygame を実行してください")
except Exception as e:
    print(f"❌ エラー: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("✅ テスト完了！")
print("\nWindows環境でこのスクリプトを実行すると：")
print("  1. ビープ音が聞こえます")
print("  2. MP3ファイルがあれば再生されます")
print("\nWSL環境では音が出ない場合があります。")