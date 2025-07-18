# 🎵 音楽ファイル配置ガイド

## 📁 ファイル配置場所
```
PomodoroTimerApp/
└── assets/
    └── music/
        ├── README.md (このファイル)
        ├── work_bgm.mp3          # 作業用BGM
        ├── break_bgm.mp3         # 休憩用BGM
        ├── alert_1min.mp3        # 1分前アラート音
        ├── alert_30sec.mp3       # 30秒前アラート音
        └── countdown_tick.mp3    # 5秒前からの時報
```

## 🎼 必要な音楽ファイル

### 1. **作業用BGM**
- **ファイル名**: `work_bgm.mp3`
- **用途**: 作業中のループBGM
- **推奨**: 集中できる環境音やインストゥルメンタル
- **長さ**: 3-5分程度（自動ループ）

### 2. **休憩用BGM**
- **ファイル名**: `break_bgm.mp3`
- **用途**: 休憩中のリラックスBGM
- **推奨**: 癒し系音楽、自然音
- **長さ**: 2-3分程度（自動ループ）

### 3. **1分前アラート音**
- **ファイル名**: `alert_1min.mp3`
- **用途**: セッション終了1分前の通知
- **推奨**: 控えめなチャイム音
- **長さ**: 1-3秒

### 4. **30秒前アラート音**
- **ファイル名**: `alert_30sec.mp3`
- **用途**: セッション終了30秒前の通知
- **推奨**: 少し強めのアラート音
- **長さ**: 1-3秒

### 5. **5秒前からの時報**
- **ファイル名**: `countdown_tick.mp3`
- **用途**: 最後の5秒間の時報音
- **推奨**: 時計のチクタク音、メトロノーム音
- **長さ**: 1秒（毎秒再生）

## 📋 ファイル形式仕様

### 推奨設定
- **フォーマット**: MP3形式
- **ビットレート**: 192kbps以上推奨
- **サンプリングレート**: 44.1kHz
- **チャンネル**: ステレオ（2ch）

### 代替形式（対応済み）
- **WAV**: 非圧縮形式
- **OGG**: Vorbis形式

## 🎚️ 音量レベル推奨

### BGM系
- **作業用BGM**: -18dB から -12dB
- **休憩用BGM**: -20dB から -15dB

### アラート系
- **1分前アラート**: -10dB から -6dB
- **30秒前アラート**: -8dB から -4dB
- **時報音**: -12dB から -8dB

## 🔧 追加設定

### 現在のプリセット更新
```python
PRESETS = {
    'work': {
        'bgm': 'work_bgm.wav',
        'alerts': {
            '1min': 'alert_1min.wav',
            '30sec': 'alert_30sec.wav',
            '5sec': 'countdown_tick.wav'
        }
    },
    'break': {
        'bgm': 'break_bgm.wav',
        'alerts': {
            '1min': 'alert_1min.wav',
            '30sec': 'alert_30sec.wav',
            '5sec': 'countdown_tick.wav'
        }
    }
}
```

## 🎵 音楽ファイルの入手先

### 無料音源サイト
- **Freesound**: https://freesound.org/
- **DOVA-SYNDROME**: https://dova-s.jp/
- **魔王魂**: https://maou.audio/

### 商用利用可能
- **Epidemic Sound**: https://www.epidemicsound.com/
- **AudioJungle**: https://audiojungle.net/

## 🚀 使用方法

1. 上記のファイル名で音楽ファイルを配置
2. `python3 main_phase2.py` でアプリを起動
3. 設定タブで各種音楽機能を調整

## ⚠️ 注意事項

- ファイル名は正確に入力してください
- 著作権に注意してください
- 大きすぎるファイルは避けてください（50MB以下推奨）

---

**音楽ファイルを配置後、アプリを再起動してください**