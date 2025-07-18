# ⚡ 緊急統合ガイド - 15分でMVP完成

## 🚀 UIBridge統合（5分）

### MainWindowに追加するコード

```python
# src/views/main_window.py に追加
from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import QTimer
from ..bridge.ui_bridge import UIBridge
from ..controllers.timer_controller import TimerController

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # バックエンド初期化
        self.timer_controller = TimerController()
        self.ui_bridge = UIBridge(self.timer_controller, self)
        
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        # メインウィジェット
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # タイマー表示
        self.timer_label = QLabel("25:00")
        self.timer_label.setStyleSheet("font-size: 48px; font-weight: bold;")
        layout.addWidget(self.timer_label)
        
        # 制御ボタン
        self.start_button = QPushButton("Start")
        self.pause_button = QPushButton("Pause") 
        self.stop_button = QPushButton("Stop")
        self.reset_button = QPushButton("Reset")
        
        layout.addWidget(self.start_button)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.reset_button)
        
    def setup_connections(self):
        # UIBridgeがボタンを自動接続
        # タイマー更新を接続
        self.ui_bridge.timer_updated.connect(self.update_timer_display)
        
    def update_timer_display(self, timer_info):
        # タイマー表示更新
        formatted_time = self.ui_bridge.format_time(timer_info['remaining_time'])
        self.timer_label.setText(formatted_time)
```

## ⚡ TimerController統合（5分）

### main.pyの統合

```python
# main.py を以下に置き換え
import sys
from PyQt6.QtWidgets import QApplication
from src.views.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
```

## 🎯 即座テスト（5分）

### 動作確認コマンド
```bash
python main.py
```

### 確認事項
- [ ] アプリが起動する
- [ ] タイマー表示される（25:00）
- [ ] Startボタンでカウントダウン開始
- [ ] Pauseボタンで一時停止
- [ ] Stopボタンで停止
- [ ] Resetボタンでリセット

## 🔧 トラブルシューティング

### エラー1: モジュールが見つからない
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### エラー2: PyQt6が見つからない
```bash
pip install PyQt6
```

### エラー3: 音声エラー
```python
# TimerControllerの音声を無効化
self.timer_controller.set_sound_enabled(False)
```

## ✅ MVP完成チェックリスト

- [ ] アプリが起動する
- [ ] タイマーが動作する
- [ ] ボタンが機能する
- [ ] 25分→5分サイクルが動作
- [ ] エラーなく動作継続

**15分でMVP完成！** 🎉