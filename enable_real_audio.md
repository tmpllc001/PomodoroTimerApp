# 🔊 実際の音声を有効にする方法

## 現在の状況
- **MockMusicPlayer**を使用しているため、音は出ません
- WSL環境では通常、音声デバイスへのアクセスが制限されています

## 音声を有効にする方法

### 方法1: Windows環境で実行
```bash
# WindowsのコマンドプロンプトまたはPowerShellで実行
cd D:\00_tmpllc\12_pomodoro\PomodoroTimerApp
python main_phase2.py
```

### 方法2: WSL2で音声を有効化（PulseAudio使用）

1. **Windowsに音声サーバーをインストール**
   - [VcXsrv](https://sourceforge.net/projects/vcxsrv/)をダウンロード
   - または[PulseAudio for Windows](https://www.freedesktop.org/wiki/Software/PulseAudio/Ports/Windows/)

2. **WSL2側の設定**
   ```bash
   # PulseAudioクライアントをインストール
   sudo apt update
   sudo apt install pulseaudio pavucontrol
   
   # 環境変数を設定
   export PULSE_SERVER=tcp:$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
   ```

3. **~/.bashrcに追加**
   ```bash
   echo "export PULSE_SERVER=tcp:$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')" >> ~/.bashrc
   ```

### 方法3: 実際の音楽ファイルでテスト

1. **MP3ファイルを配置**
   ```
   assets/music/
   ├── work_bgm.mp3      # 作業用BGM（25分程度のループ音楽）
   ├── break_bgm.mp3     # 休憩用BGM（リラックス音楽）
   ├── alert_1min.mp3    # 1分前警告音
   ├── alert_30sec.mp3   # 30秒前警告音
   └── countdown_tick.mp3 # カウントダウン音
   ```

2. **pygame.mixerを直接使用（Windows環境）**
   music_presets.pyのAudioPresetManagerを本物のpygame実装に置き換え

### 方法4: 音声確認用スクリプト

```python
# test_real_audio.py
import pygame.mixer
import time

try:
    pygame.mixer.init()
    print("✅ 音声システム初期化成功")
    
    # テスト音を生成
    frequency = 440  # A4
    duration = 1.0
    sample_rate = 22050
    
    # サイン波を生成
    import numpy as np
    samples = int(sample_rate * duration)
    waves = np.sin(frequency * 2 * np.pi * np.arange(samples) / sample_rate)
    sound_array = np.array(waves * 32767, dtype=np.int16)
    
    # ステレオに変換
    stereo_array = np.zeros((samples, 2), dtype=np.int16)
    stereo_array[:, 0] = sound_array
    stereo_array[:, 1] = sound_array
    
    # サウンドオブジェクト作成
    sound = pygame.mixer.Sound(stereo_array)
    sound.play()
    
    print("🔊 テスト音再生中...")
    time.sleep(2)
    
except Exception as e:
    print(f"❌ エラー: {e}")
```

## 推奨される解決策

### 開発環境では
- MockMusicPlayerを使用（現在の実装）
- ログで動作を確認

### 本番環境では
- Windows環境で実行
- 実際のMP3ファイルを配置
- pygame.mixerが正常に動作することを確認

## 音楽ファイルの入手先
- フリーBGM素材サイト
- [魔王魂](https://maoudamashii.jokersounds.com/)
- [DOVA-SYNDROME](https://dova-s.jp/)
- [甘茶の音楽工房](http://amachamusic.chagasi.com/)