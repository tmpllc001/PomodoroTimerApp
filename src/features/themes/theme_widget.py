#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
テーマ管理ウィジェット
PyQt6を使用したテーマ管理UI
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QComboBox, QGroupBox, QGridLayout,
                           QColorDialog, QSpinBox, QSlider, QDialog, QDialogButtonBox,
                           QLineEdit, QTextEdit, QFrame, QMessageBox, QFileDialog,
                           QTabWidget, QScrollArea, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette, QPixmap, QPainter

from .theme_manager import ThemeManager, Theme, ColorScheme
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class ColorPreviewWidget(QWidget):
    """色プレビューウィジェット"""
    
    colorClicked = pyqtSignal(str)  # color_key
    
    def __init__(self, color_key: str, color: str, label: str, parent=None):
        super().__init__(parent)
        self.color_key = color_key
        self.color = color
        self.label = label
        self.setFixedSize(80, 60)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border: 2px solid #bdc3c7;
                border-radius: 8px;
            }}
            QWidget:hover {{
                border: 2px solid #3498db;
            }}
        """)
        
        # ツールチップ
        self.setToolTip(f"{label}\n{color}")
    
    def mousePressEvent(self, event):
        """マウスクリックイベント"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.colorClicked.emit(self.color_key)
        super().mousePressEvent(event)
    
    def update_color(self, color: str):
        """色を更新"""
        self.color = color
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border: 2px solid #bdc3c7;
                border-radius: 8px;
            }}
            QWidget:hover {{
                border: 2px solid #3498db;
            }}
        """)
        self.setToolTip(f"{self.label}\n{color}")

class ThemePreviewWidget(QWidget):
    """テーマプレビューウィジェット"""
    
    def __init__(self, theme: Theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.setFixedSize(200, 150)
        self.setup_ui()
    
    def setup_ui(self):
        """UI設定"""
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # テーマ名
        name_label = QLabel(self.theme.name)
        name_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)
        
        # カラーパレット
        colors_widget = QWidget()
        colors_layout = QGridLayout(colors_widget)
        colors_layout.setSpacing(2)
        
        # 主要色を表示
        color_info = [
            (self.theme.colors.primary, "Primary"),
            (self.theme.colors.secondary, "Secondary"),
            (self.theme.colors.accent, "Accent"),
            (self.theme.colors.background, "Background"),
            (self.theme.colors.text_primary, "Text"),
            (self.theme.colors.success, "Success")
        ]
        
        for i, (color, label) in enumerate(color_info):
            color_widget = QWidget()
            color_widget.setFixedSize(25, 25)
            color_widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {color};
                    border: 1px solid #bdc3c7;
                    border-radius: 3px;
                }}
            """)
            color_widget.setToolTip(f"{label}: {color}")
            colors_layout.addWidget(color_widget, i // 3, i % 3)
        
        layout.addWidget(colors_widget)
        
        # テーマ情報
        info_label = QLabel(f"Font: {self.theme.font_family}, {self.theme.font_size}px")
        info_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        
        # 枠線
        self.setStyleSheet(f"""
            QWidget {{
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: {self.theme.colors.surface};
            }}
        """)

class ThemeEditDialog(QDialog):
    """テーマ編集ダイアログ"""
    
    def __init__(self, theme: Optional[Theme] = None, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.color_previews = {}
        self.setWindowTitle("テーマ編集" if theme else "新規テーマ")
        self.setFixedSize(600, 500)
        self.setup_ui()
        
        if theme:
            self.load_theme_data()
    
    def setup_ui(self):
        """UI設定"""
        layout = QVBoxLayout(self)
        
        # タブウィジェット
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # 基本情報タブ
        self.setup_basic_tab(tab_widget)
        
        # カラータブ
        self.setup_color_tab(tab_widget)
        
        # フォント・スタイルタブ
        self.setup_style_tab(tab_widget)
        
        # ボタン
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def setup_basic_tab(self, tab_widget):
        """基本情報タブ"""
        basic_widget = QWidget()
        layout = QVBoxLayout(basic_widget)
        
        # テーマ名
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("テーマ名:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("テーマ名を入力")
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # 説明
        layout.addWidget(QLabel("説明:"))
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("テーマの説明（省略可）")
        self.description_edit.setMaximumHeight(100)
        layout.addWidget(self.description_edit)
        
        layout.addStretch()
        tab_widget.addTab(basic_widget, "基本情報")
    
    def setup_color_tab(self, tab_widget):
        """カラータブ"""
        color_widget = QWidget()
        layout = QVBoxLayout(color_widget)
        
        # カラー編集
        colors_group = QGroupBox("カラー設定")
        colors_layout = QGridLayout(colors_group)
        
        # カラー項目
        color_items = [
            ("primary", "プライマリ", "#3498db"),
            ("secondary", "セカンダリ", "#2ecc71"),
            ("accent", "アクセント", "#e74c3c"),
            ("background", "背景", "#ffffff"),
            ("surface", "サーフェス", "#f8f9fa"),
            ("text_primary", "メインテキスト", "#2c3e50"),
            ("text_secondary", "サブテキスト", "#7f8c8d"),
            ("border", "ボーダー", "#bdc3c7"),
            ("success", "成功", "#27ae60"),
            ("warning", "警告", "#f39c12"),
            ("error", "エラー", "#e74c3c"),
            ("info", "情報", "#3498db")
        ]
        
        for i, (key, label, default_color) in enumerate(color_items):
            # ラベル
            label_widget = QLabel(label)
            colors_layout.addWidget(label_widget, i, 0)
            
            # カラープレビュー
            color_preview = ColorPreviewWidget(key, default_color, label)
            color_preview.colorClicked.connect(self.on_color_clicked)
            self.color_previews[key] = color_preview
            colors_layout.addWidget(color_preview, i, 1)
            
            # 色コード
            color_edit = QLineEdit(default_color)
            color_edit.setFixedWidth(80)
            color_edit.textChanged.connect(lambda text, k=key: self.on_color_text_changed(k, text))
            colors_layout.addWidget(color_edit, i, 2)
            setattr(self, f"{key}_edit", color_edit)
        
        layout.addWidget(colors_group)
        
        # プリセット
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("プリセット:"))
        
        preset_combo = QComboBox()
        preset_combo.addItems(["カスタム", "ライト", "ダーク", "ポモドーロ", "フォーカス"])
        preset_combo.currentTextChanged.connect(self.on_preset_changed)
        preset_layout.addWidget(preset_combo)
        
        preset_layout.addStretch()
        layout.addLayout(preset_layout)
        
        tab_widget.addTab(color_widget, "カラー")
    
    def setup_style_tab(self, tab_widget):
        """スタイルタブ"""
        style_widget = QWidget()
        layout = QVBoxLayout(style_widget)
        
        # フォント設定
        font_group = QGroupBox("フォント設定")
        font_layout = QGridLayout(font_group)
        
        # フォントファミリー
        font_layout.addWidget(QLabel("フォント:"), 0, 0)
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Arial", "メイリオ", "游ゴシック", "Times New Roman", "Courier New"])
        font_layout.addWidget(self.font_combo, 0, 1)
        
        # フォントサイズ
        font_layout.addWidget(QLabel("サイズ:"), 1, 0)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(12)
        self.font_size_spin.setSuffix(" px")
        font_layout.addWidget(self.font_size_spin, 1, 1)
        
        layout.addWidget(font_group)
        
        # スタイル設定
        style_group = QGroupBox("スタイル設定")
        style_layout = QGridLayout(style_group)
        
        # ボーダー半径
        style_layout.addWidget(QLabel("角の丸み:"), 0, 0)
        self.border_radius_spin = QSpinBox()
        self.border_radius_spin.setRange(0, 20)
        self.border_radius_spin.setValue(8)
        self.border_radius_spin.setSuffix(" px")
        style_layout.addWidget(self.border_radius_spin, 0, 1)
        
        # 透明度
        style_layout.addWidget(QLabel("透明度:"), 1, 0)
        self.transparency_slider = QSlider(Qt.Orientation.Horizontal)
        self.transparency_slider.setRange(50, 100)
        self.transparency_slider.setValue(90)
        self.transparency_slider.valueChanged.connect(self.on_transparency_changed)
        style_layout.addWidget(self.transparency_slider, 1, 1)
        
        self.transparency_label = QLabel("90%")
        style_layout.addWidget(self.transparency_label, 1, 2)
        
        layout.addWidget(style_group)
        
        layout.addStretch()
        tab_widget.addTab(style_widget, "スタイル")
    
    def on_color_clicked(self, color_key: str):
        """色クリック時の処理"""
        current_color = getattr(self, f"{color_key}_edit").text()
        color = QColorDialog.getColor(QColor(current_color), self)
        
        if color.isValid():
            color_hex = color.name()
            self.color_previews[color_key].update_color(color_hex)
            getattr(self, f"{color_key}_edit").setText(color_hex)
    
    def on_color_text_changed(self, color_key: str, text: str):
        """色テキスト変更時の処理"""
        try:
            if text.startswith('#') and len(text) == 7:
                self.color_previews[color_key].update_color(text)
        except:
            pass
    
    def on_preset_changed(self, preset: str):
        """プリセット変更時の処理"""
        if preset == "カスタム":
            return
        
        presets = {
            "ライト": {
                "primary": "#3498db",
                "secondary": "#2ecc71",
                "accent": "#e74c3c",
                "background": "#ffffff",
                "surface": "#f8f9fa",
                "text_primary": "#2c3e50",
                "text_secondary": "#7f8c8d",
                "border": "#bdc3c7",
                "success": "#27ae60",
                "warning": "#f39c12",
                "error": "#e74c3c",
                "info": "#3498db"
            },
            "ダーク": {
                "primary": "#5dade2",
                "secondary": "#58d68d",
                "accent": "#ec7063",
                "background": "#2c3e50",
                "surface": "#34495e",
                "text_primary": "#ecf0f1",
                "text_secondary": "#bdc3c7",
                "border": "#566573",
                "success": "#58d68d",
                "warning": "#f4d03f",
                "error": "#ec7063",
                "info": "#5dade2"
            },
            "ポモドーロ": {
                "primary": "#e74c3c",
                "secondary": "#c0392b",
                "accent": "#f39c12",
                "background": "#fdf2e9",
                "surface": "#fff5f5",
                "text_primary": "#2c3e50",
                "text_secondary": "#7f8c8d",
                "border": "#fadbd8",
                "success": "#27ae60",
                "warning": "#f39c12",
                "error": "#e74c3c",
                "info": "#3498db"
            },
            "フォーカス": {
                "primary": "#3498db",
                "secondary": "#2980b9",
                "accent": "#1abc9c",
                "background": "#eef4f7",
                "surface": "#f8fbfc",
                "text_primary": "#2c3e50",
                "text_secondary": "#7f8c8d",
                "border": "#d6e9f0",
                "success": "#27ae60",
                "warning": "#f39c12",
                "error": "#e74c3c",
                "info": "#3498db"
            }
        }
        
        if preset in presets:
            colors = presets[preset]
            for key, color in colors.items():
                if hasattr(self, f"{key}_edit"):
                    getattr(self, f"{key}_edit").setText(color)
                    self.color_previews[key].update_color(color)
    
    def on_transparency_changed(self, value):
        """透明度変更時の処理"""
        self.transparency_label.setText(f"{value}%")
    
    def load_theme_data(self):
        """テーマデータを読み込み"""
        if not self.theme:
            return
        
        # 基本情報
        self.name_edit.setText(self.theme.name)
        
        # カラー
        colors = self.theme.colors
        for key in self.color_previews.keys():
            if hasattr(colors, key):
                color = getattr(colors, key)
                getattr(self, f"{key}_edit").setText(color)
                self.color_previews[key].update_color(color)
        
        # スタイル
        self.font_combo.setCurrentText(self.theme.font_family)
        self.font_size_spin.setValue(self.theme.font_size)
        self.border_radius_spin.setValue(self.theme.border_radius)
        self.transparency_slider.setValue(int(self.theme.transparency * 100))
        self.transparency_label.setText(f"{int(self.theme.transparency * 100)}%")
    
    def get_theme_data(self) -> dict:
        """テーマデータを取得"""
        # カラー情報を収集
        colors = {}
        for key in self.color_previews.keys():
            colors[key] = getattr(self, f"{key}_edit").text()
        
        return {
            'name': self.name_edit.text().strip(),
            'colors': colors,
            'font_family': self.font_combo.currentText(),
            'font_size': self.font_size_spin.value(),
            'border_radius': self.border_radius_spin.value(),
            'transparency': self.transparency_slider.value() / 100.0
        }

class ThemeWidget(QWidget):
    """メインテーマ管理ウィジェット"""
    
    themeChanged = pyqtSignal(str)  # theme_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager()
        self.theme_previews = {}
        self.setup_ui()
        self.refresh_themes()
    
    def setup_ui(self):
        """UI設定"""
        layout = QVBoxLayout(self)
        
        # タイトル
        title_label = QLabel("🎨 テーマ管理")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 現在のテーマ
        current_group = QGroupBox("現在のテーマ")
        current_layout = QHBoxLayout(current_group)
        
        self.current_theme_combo = QComboBox()
        self.current_theme_combo.currentTextChanged.connect(self.on_current_theme_changed)
        current_layout.addWidget(self.current_theme_combo)
        
        apply_btn = QPushButton("適用")
        apply_btn.clicked.connect(self.apply_theme)
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        current_layout.addWidget(apply_btn)
        
        layout.addWidget(current_group)
        
        # テーマ一覧
        themes_group = QGroupBox("利用可能なテーマ")
        themes_layout = QVBoxLayout(themes_group)
        
        # ツールバー
        toolbar_layout = QHBoxLayout()
        
        new_btn = QPushButton("➕ 新規作成")
        new_btn.clicked.connect(self.create_new_theme)
        new_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        toolbar_layout.addWidget(new_btn)
        
        edit_btn = QPushButton("✏️ 編集")
        edit_btn.clicked.connect(self.edit_theme)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        toolbar_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ 削除")
        delete_btn.clicked.connect(self.delete_theme)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        toolbar_layout.addWidget(delete_btn)
        
        toolbar_layout.addStretch()
        
        import_btn = QPushButton("📁 インポート")
        import_btn.clicked.connect(self.import_theme)
        toolbar_layout.addWidget(import_btn)
        
        export_btn = QPushButton("📤 エクスポート")
        export_btn.clicked.connect(self.export_theme)
        toolbar_layout.addWidget(export_btn)
        
        themes_layout.addLayout(toolbar_layout)
        
        # テーマプレビュー一覧
        self.themes_scroll = QScrollArea()
        self.themes_scroll.setWidgetResizable(True)
        self.themes_scroll.setMinimumHeight(200)
        
        self.themes_container = QWidget()
        self.themes_layout = QHBoxLayout(self.themes_container)
        self.themes_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.themes_scroll.setWidget(self.themes_container)
        themes_layout.addWidget(self.themes_scroll)
        
        layout.addWidget(themes_group)
        
        # 現在選択されているテーマ
        self.selected_theme = None
    
    def refresh_themes(self):
        """テーマ一覧を更新"""
        # コンボボックスを更新
        self.current_theme_combo.clear()
        themes = self.theme_manager.get_available_themes()
        self.current_theme_combo.addItems(themes)
        
        # 現在のテーマを選択
        current_theme = self.theme_manager.current_theme_name
        if current_theme in themes:
            self.current_theme_combo.setCurrentText(current_theme)
        
        # プレビューを更新
        self.refresh_previews()
    
    def refresh_previews(self):
        """プレビュー一覧を更新"""
        # 既存のプレビューを削除
        for preview in self.theme_previews.values():
            preview.setParent(None)
        self.theme_previews.clear()
        
        # 新しいプレビューを作成
        themes = self.theme_manager.get_available_themes()
        for theme_name in themes:
            theme = self.theme_manager.get_theme(theme_name)
            if theme:
                preview = ThemePreviewWidget(theme)
                preview.mousePressEvent = lambda event, name=theme_name: self.on_theme_selected(name)
                self.theme_previews[theme_name] = preview
                self.themes_layout.addWidget(preview)
    
    def on_current_theme_changed(self, theme_name: str):
        """現在のテーマ変更"""
        self.selected_theme = theme_name
    
    def on_theme_selected(self, theme_name: str):
        """テーマ選択"""
        self.selected_theme = theme_name
        self.current_theme_combo.setCurrentText(theme_name)
        
        # 選択されたテーマをハイライト
        for name, preview in self.theme_previews.items():
            if name == theme_name:
                preview.setStyleSheet(f"""
                    QWidget {{
                        border: 3px solid #3498db;
                        border-radius: 8px;
                        background-color: {preview.theme.colors.surface};
                    }}
                """)
            else:
                preview.setStyleSheet(f"""
                    QWidget {{
                        border: 2px solid #bdc3c7;
                        border-radius: 8px;
                        background-color: {preview.theme.colors.surface};
                    }}
                """)
    
    def apply_theme(self):
        """テーマを適用"""
        if not self.selected_theme:
            QMessageBox.information(self, "情報", "テーマを選択してください")
            return
        
        if self.theme_manager.set_current_theme(self.selected_theme):
            self.themeChanged.emit(self.selected_theme)
            QMessageBox.information(self, "成功", f"テーマ '{self.selected_theme}' を適用しました")
        else:
            QMessageBox.warning(self, "エラー", "テーマの適用に失敗しました")
    
    def create_new_theme(self):
        """新しいテーマを作成"""
        dialog = ThemeEditDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_theme_data()
            if not data['name']:
                QMessageBox.warning(self, "エラー", "テーマ名を入力してください")
                return
            
            if self.theme_manager.create_custom_theme(data['name'], **data):
                self.refresh_themes()
                QMessageBox.information(self, "成功", f"テーマ '{data['name']}' を作成しました")
            else:
                QMessageBox.warning(self, "エラー", "テーマの作成に失敗しました")
    
    def edit_theme(self):
        """テーマを編集"""
        if not self.selected_theme:
            QMessageBox.information(self, "情報", "編集するテーマを選択してください")
            return
        
        theme = self.theme_manager.get_theme(self.selected_theme)
        if not theme:
            QMessageBox.warning(self, "エラー", "テーマが見つかりません")
            return
        
        if theme.type != "custom":
            QMessageBox.warning(self, "エラー", "デフォルトテーマは編集できません")
            return
        
        dialog = ThemeEditDialog(theme, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_theme_data()
            if not data['name']:
                QMessageBox.warning(self, "エラー", "テーマ名を入力してください")
                return
            
            # 既存のテーマを削除して新しく作成
            if self.theme_manager.delete_theme(self.selected_theme):
                if self.theme_manager.create_custom_theme(data['name'], **data):
                    self.refresh_themes()
                    QMessageBox.information(self, "成功", f"テーマ '{data['name']}' を更新しました")
                else:
                    QMessageBox.warning(self, "エラー", "テーマの更新に失敗しました")
    
    def delete_theme(self):
        """テーマを削除"""
        if not self.selected_theme:
            QMessageBox.information(self, "情報", "削除するテーマを選択してください")
            return
        
        theme = self.theme_manager.get_theme(self.selected_theme)
        if not theme:
            QMessageBox.warning(self, "エラー", "テーマが見つかりません")
            return
        
        if theme.type != "custom":
            QMessageBox.warning(self, "エラー", "デフォルトテーマは削除できません")
            return
        
        reply = QMessageBox.question(
            self, "確認",
            f"テーマ '{self.selected_theme}' を削除しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.theme_manager.delete_theme(self.selected_theme):
                self.refresh_themes()
                QMessageBox.information(self, "成功", f"テーマ '{self.selected_theme}' を削除しました")
            else:
                QMessageBox.warning(self, "エラー", "テーマの削除に失敗しました")
    
    def import_theme(self):
        """テーマをインポート"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "テーマをインポート", "", "JSON files (*.json)"
        )
        
        if filename:
            if self.theme_manager.import_theme(filename):
                self.refresh_themes()
                QMessageBox.information(self, "成功", "テーマをインポートしました")
            else:
                QMessageBox.warning(self, "エラー", "テーマのインポートに失敗しました")
    
    def export_theme(self):
        """テーマをエクスポート"""
        if not self.selected_theme:
            QMessageBox.information(self, "情報", "エクスポートするテーマを選択してください")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "テーマをエクスポート", f"{self.selected_theme}.json", "JSON files (*.json)"
        )
        
        if filename:
            if self.theme_manager.export_theme(self.selected_theme, filename):
                QMessageBox.information(self, "成功", f"テーマをエクスポートしました: {filename}")
            else:
                QMessageBox.warning(self, "エラー", "テーマのエクスポートに失敗しました")
    
    def get_theme_manager(self) -> ThemeManager:
        """テーママネージャーを取得"""
        return self.theme_manager