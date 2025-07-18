# ウィンドウサイズ制御機能 設計書

## 概要
ポモドーロタイマーのセッション状態に応じて、ウィンドウサイズを自動的に変更する機能の設計書です。

## 目的
- **作業中**: 集中を妨げないよう最小限のサイズで表示
- **休憩中**: 休憩を促すため大きく表示（注意喚起）

## 機能要件

### 1. ウィンドウサイズ定義
```python
# サイズ定義
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
    'minimized': {
        'width': 150,
        'height': 60,
        'opacity': 0.5
    }
}
```

### 2. 状態遷移
```
作業開始 → 小サイズ（200x100）
    ↓
作業終了 → アニメーション
    ↓
休憩開始 → 大サイズ（600x400）
    ↓
休憩終了 → アニメーション
    ↓
作業開始 → 小サイズに戻る
```

### 3. アニメーション仕様
- 遷移時間: 0.5秒
- イージング: ease-in-out
- 中心点固定でリサイズ

## 実装設計

### 1. PomodoroTimerクラスへの追加メソッド
```python
def resize_window(self, session_type):
    """セッションタイプに応じてウィンドウをリサイズ"""
    target_size = WINDOW_SIZES[session_type]
    
    # アニメーション実装
    self.animate_resize(
        target_width=target_size['width'],
        target_height=target_size['height'],
        target_opacity=target_size['opacity'],
        duration=500  # ms
    )

def animate_resize(self, target_width, target_height, target_opacity, duration):
    """ウィンドウリサイズアニメーション"""
    # QPropertyAnimationを使用
    # 幅、高さ、透明度を同時にアニメーション
    pass

def center_window(self):
    """ウィンドウを画面中央に配置"""
    screen = QApplication.primaryScreen()
    screen_geometry = screen.geometry()
    window_geometry = self.frameGeometry()
    
    center_point = screen_geometry.center()
    window_geometry.moveCenter(center_point)
    self.move(window_geometry.topLeft())
```

### 2. セッション切り替え時の処理
```python
def timer_finished_handler(self):
    """タイマー完了処理（既存メソッドの拡張）"""
    # 既存の処理...
    
    if self.is_work_session:
        # 作業完了 → 休憩モードへ
        self.resize_window('break')
        self.show_break_notification()
    else:
        # 休憩完了 → 作業モードへ
        self.resize_window('work')
    
    # 既存の処理...
```

### 3. 追加UI要素
```python
# 設定メニューに追加
self.auto_resize_checkbox = QCheckBox("自動リサイズ")
self.auto_resize_checkbox.setChecked(True)
self.auto_resize_checkbox.stateChanged.connect(self.toggle_auto_resize)

# 手動リサイズボタン
self.minimize_btn = QPushButton("最小化")
self.minimize_btn.clicked.connect(lambda: self.resize_window('minimized'))
```

## 技術的考慮事項

### 1. PyQt6でのアニメーション実装
```python
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QRect

def create_resize_animation(self):
    # ジオメトリアニメーション
    self.resize_anim = QPropertyAnimation(self, b"geometry")
    self.resize_anim.setDuration(500)
    self.resize_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    # 透明度アニメーション
    self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
    self.opacity_anim.setDuration(500)
    self.opacity_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
```

### 2. マルチモニター対応
```python
def get_current_screen(self):
    """現在のウィンドウが表示されている画面を取得"""
    current_center = self.geometry().center()
    
    for screen in QApplication.screens():
        if screen.geometry().contains(current_center):
            return screen
    
    return QApplication.primaryScreen()
```

### 3. ユーザー設定の保存
```json
{
    "window_settings": {
        "auto_resize": true,
        "custom_sizes": {
            "work": {"width": 200, "height": 100},
            "break": {"width": 600, "height": 400}
        },
        "animation_duration": 500,
        "keep_on_top": true
    }
}
```

## UI/UXガイドライン

### 1. 視覚的フィードバック
- リサイズ開始時に軽いフェード効果
- サイズ変更中は内容を固定（ちらつき防止）
- 完了時に軽いバウンス効果（オプション）

### 2. ユーザーコントロール
- 自動リサイズのON/OFF切り替え
- 手動でのサイズ調整も可能
- ダブルクリックで元のサイズに戻る

### 3. アクセシビリティ
- アニメーション無効化オプション
- 最小サイズでも重要情報が見える
- キーボードショートカット対応

## 実装優先順位

### Phase 1（MVP後の最初の実装）
1. 基本的なリサイズ機能（アニメーションなし）
2. 作業/休憩での自動切り替え
3. 設定のON/OFF

### Phase 2（改善）
1. スムーズなアニメーション追加
2. カスタムサイズ設定
3. マルチモニター対応

### Phase 3（高度な機能）
1. ジェスチャー操作
2. AI学習による最適サイズ提案
3. 他アプリとの連携

## テスト項目
- [ ] 各セッション切り替え時のリサイズ動作
- [ ] マルチモニター環境での動作
- [ ] 最小化/最大化との競合
- [ ] パフォーマンス影響測定
- [ ] 異なる解像度での表示確認

## 参考実装コード
```python
# 将来の実装時に使用
def implement_window_resize():
    """
    TODO: この設計書に基づいて実装
    main_mvp_fixed.py の PomodoroTimer クラスに
    上記メソッドを追加する
    """
    pass
```

---

**作成日**: 2025年1月18日  
**作成者**: PRESIDENT  
**ステータス**: 設計完了（実装はPhase 2で予定）