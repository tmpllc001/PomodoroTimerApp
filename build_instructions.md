# Pomodoro Timer App ビルド手順

## 🔧 事前準備

### 1. 必要なツールのインストール

```bash
# ビルド用依存関係をインストール
pip install -r requirements_build.txt
```

### 2. （オプション）UPXのインストール

実行ファイルサイズを削減したい場合：

- **Windows**: https://github.com/upx/upx/releases からダウンロード
- **Linux**: `sudo apt install upx` または `sudo yum install upx`
- **macOS**: `brew install upx`

## 🚀 ビルド方法

### 開発・デバッグ用ビルド（推奨）

```bash
python build_app.py --mode dir --clean
```

これにより：
- `dist/PomodoroTimer/` ディレクトリに実行ファイルが生成されます
- 設定ファイルやデータファイルの修正が容易です
- デバッグが簡単です

### 配布用ビルド（単一ファイル）

```bash
python build_app.py --mode onefile --clean
```

これにより：
- `dist/PomodoroTimer.exe`（Windows）または `dist/PomodoroTimer`（Linux/Mac）が生成されます
- 配布が簡単ですが、起動が若干遅くなります

### デバッグビルド

問題が発生した場合：

```bash
python build_app.py --mode dir --debug --clean
```

## 📝 カスタマイズ

### アイコンの追加

1. アイコンファイルを用意：
   - Windows: `resources/icon.ico`
   - macOS: `resources/icon.icns`
   - Linux: `resources/icon.png`

2. `.spec` ファイルのコメントを解除：
   ```python
   icon='resources/icon.ico' if sys.platform == 'win32' else None,
   ```

3. 再ビルド

### 追加リソースの含め方

`pomodoro_timer.spec` の `datas` セクションを編集：

```python
datas=[
    ('data', 'data'),
    ('scripts', 'scripts'),
    ('resources', 'resources'),  # 追加
    ('custom_sounds', 'sounds'), # カスタムサウンド追加例
],
```

### ビルドサイズの最適化

1. 不要なパッケージを除外：
   `.spec` ファイルの `excludes` リストに追加

2. 最適化レベルを上げる：
   `optimize=2` に設定

3. UPXを使用：
   `upx=True`（デフォルトで有効）

## 🐛 トラブルシューティング

### "ModuleNotFoundError" エラー

隠しインポートを `.spec` ファイルに追加：

```python
hiddenimports=[
    'your_missing_module',
    # ...
],
```

### アンチウイルスの誤検知

- PyInstallerで作成した実行ファイルは誤検知されることがあります
- 署名証明書を使用するか、ユーザーに説明してください

### パスの問題

実行時のパスを正しく取得するため、コード内で：

```python
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    # PyInstallerでパッケージ化されている場合
    base_path = Path(sys._MEIPASS)
else:
    # 開発環境
    base_path = Path(__file__).parent
```

## 📦 配布

### Windows
- `dist/PomodoroTimer.exe` を配布
- 必要に応じてインストーラー（NSIS、Inno Setup）を作成

### macOS
- `.app` バンドルの作成を検討
- 署名とnotarization が必要な場合があります

### Linux
- AppImageやSnapパッケージの作成を検討
- または単純に実行ファイルを配布

## 🔄 更新時の注意

1. バージョン管理：
   - コード内でバージョン番号を管理
   - リリースノートを作成

2. 互換性：
   - データファイル形式の互換性を維持
   - 設定ファイルの移行処理を実装

3. テスト：
   - 異なるOS環境でテスト
   - クリーンな環境でインストールテスト