#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
カスタムテーママネージャー
アプリケーションの外観テーマを管理
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class ThemeType(Enum):
    """テーマタイプ"""
    LIGHT = "light"
    DARK = "dark"
    CUSTOM = "custom"

@dataclass
class ColorScheme:
    """カラースキーム"""
    primary: str = "#3498db"
    secondary: str = "#2ecc71"
    accent: str = "#e74c3c"
    background: str = "#ffffff"
    surface: str = "#f8f9fa"
    text_primary: str = "#2c3e50"
    text_secondary: str = "#7f8c8d"
    border: str = "#bdc3c7"
    success: str = "#27ae60"
    warning: str = "#f39c12"
    error: str = "#e74c3c"
    info: str = "#3498db"

@dataclass
class Theme:
    """テーマデータクラス"""
    name: str
    type: str
    colors: ColorScheme
    font_family: str = "Arial"
    font_size: int = 12
    border_radius: int = 8
    transparency: float = 0.9
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Theme':
        """辞書からThemeインスタンスを作成"""
        color_data = data.get('colors', {})
        colors = ColorScheme(**color_data)
        
        return cls(
            name=data['name'],
            type=data['type'],
            colors=colors,
            font_family=data.get('font_family', 'Arial'),
            font_size=data.get('font_size', 12),
            border_radius=data.get('border_radius', 8),
            transparency=data.get('transparency', 0.9)
        )
    
    def to_dict(self) -> Dict:
        """ThemeをJSON形式の辞書に変換"""
        return {
            'name': self.name,
            'type': self.type,
            'colors': asdict(self.colors),
            'font_family': self.font_family,
            'font_size': self.font_size,
            'border_radius': self.border_radius,
            'transparency': self.transparency
        }

class ThemeManager:
    """テーママネージャー"""
    
    def __init__(self, themes_file: str = "data/themes.json"):
        self.themes_file = Path(themes_file)
        self.themes: Dict[str, Theme] = {}
        self.current_theme_name: str = "light"
        self.load_themes()
    
    def load_themes(self):
        """テーマを読み込み"""
        try:
            # デフォルトテーマを作成
            self.create_default_themes()
            
            # カスタムテーマを読み込み
            if self.themes_file.exists():
                with open(self.themes_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # カスタムテーマを追加
                for theme_data in data.get('themes', []):
                    theme = Theme.from_dict(theme_data)
                    self.themes[theme.name] = theme
                
                self.current_theme_name = data.get('current_theme', 'light')
                logger.info(f"🎨 テーマ読み込み完了: {len(self.themes)}テーマ")
            else:
                self.save_themes()
                logger.info("🎨 デフォルトテーマファイルを作成")
                
        except Exception as e:
            logger.error(f"❌ テーマ読み込みエラー: {e}")
            self.create_default_themes()
    
    def create_default_themes(self):
        """デフォルトテーマを作成"""
        # ライトテーマ
        light_colors = ColorScheme(
            primary="#3498db",
            secondary="#2ecc71",
            accent="#e74c3c",
            background="#ffffff",
            surface="#f8f9fa",
            text_primary="#2c3e50",
            text_secondary="#7f8c8d",
            border="#bdc3c7",
            success="#27ae60",
            warning="#f39c12",
            error="#e74c3c",
            info="#3498db"
        )
        
        light_theme = Theme(
            name="light",
            type=ThemeType.LIGHT.value,
            colors=light_colors,
            font_family="Arial",
            font_size=12,
            border_radius=8,
            transparency=0.9
        )
        
        # ダークテーマ
        dark_colors = ColorScheme(
            primary="#5dade2",
            secondary="#58d68d",
            accent="#ec7063",
            background="#2c3e50",
            surface="#34495e",
            text_primary="#ecf0f1",
            text_secondary="#bdc3c7",
            border="#566573",
            success="#58d68d",
            warning="#f4d03f",
            error="#ec7063",
            info="#5dade2"
        )
        
        dark_theme = Theme(
            name="dark",
            type=ThemeType.DARK.value,
            colors=dark_colors,
            font_family="Arial",
            font_size=12,
            border_radius=8,
            transparency=0.9
        )
        
        # ポモドーロテーマ（赤基調）
        pomodoro_colors = ColorScheme(
            primary="#e74c3c",
            secondary="#c0392b",
            accent="#f39c12",
            background="#fdf2e9",
            surface="#fff5f5",
            text_primary="#2c3e50",
            text_secondary="#7f8c8d",
            border="#fadbd8",
            success="#27ae60",
            warning="#f39c12",
            error="#e74c3c",
            info="#3498db"
        )
        
        pomodoro_theme = Theme(
            name="pomodoro",
            type=ThemeType.CUSTOM.value,
            colors=pomodoro_colors,
            font_family="Arial",
            font_size=12,
            border_radius=10,
            transparency=0.95
        )
        
        # フォーカステーマ（青基調）
        focus_colors = ColorScheme(
            primary="#3498db",
            secondary="#2980b9",
            accent="#1abc9c",
            background="#eef4f7",
            surface="#f8fbfc",
            text_primary="#2c3e50",
            text_secondary="#7f8c8d",
            border="#d6e9f0",
            success="#27ae60",
            warning="#f39c12",
            error="#e74c3c",
            info="#3498db"
        )
        
        focus_theme = Theme(
            name="focus",
            type=ThemeType.CUSTOM.value,
            colors=focus_colors,
            font_family="Arial",
            font_size=12,
            border_radius=6,
            transparency=0.92
        )
        
        # テーマを登録
        self.themes = {
            "light": light_theme,
            "dark": dark_theme,
            "pomodoro": pomodoro_theme,
            "focus": focus_theme
        }
    
    def save_themes(self):
        """テーマを保存"""
        try:
            self.themes_file.parent.mkdir(parents=True, exist_ok=True)
            
            # カスタムテーマのみを保存
            custom_themes = [
                theme.to_dict() for theme in self.themes.values()
                if theme.type == ThemeType.CUSTOM.value
            ]
            
            data = {
                'themes': custom_themes,
                'current_theme': self.current_theme_name
            }
            
            with open(self.themes_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"🎨 テーマ保存完了: {len(custom_themes)}カスタムテーマ")
            
        except Exception as e:
            logger.error(f"❌ テーマ保存エラー: {e}")
    
    def get_theme(self, name: str) -> Optional[Theme]:
        """テーマを取得"""
        return self.themes.get(name)
    
    def get_current_theme(self) -> Theme:
        """現在のテーマを取得"""
        return self.themes.get(self.current_theme_name, self.themes["light"])
    
    def set_current_theme(self, name: str) -> bool:
        """現在のテーマを設定"""
        if name not in self.themes:
            logger.warning(f"⚠️ テーマが見つかりません: {name}")
            return False
        
        self.current_theme_name = name
        self.save_themes()
        logger.info(f"🎨 テーマ変更: {name}")
        return True
    
    def get_available_themes(self) -> List[str]:
        """利用可能なテーマのリストを取得"""
        return list(self.themes.keys())
    
    def create_custom_theme(self, name: str, base_theme: str = "light", 
                          **overrides) -> bool:
        """カスタムテーマを作成"""
        if name in self.themes:
            logger.warning(f"⚠️ テーマが既に存在します: {name}")
            return False
        
        # ベーステーマを取得
        base = self.themes.get(base_theme)
        if not base:
            logger.error(f"❌ ベーステーマが見つかりません: {base_theme}")
            return False
        
        # カスタムテーマを作成
        theme_data = base.to_dict()
        theme_data['name'] = name
        theme_data['type'] = ThemeType.CUSTOM.value
        
        # オーバーライドを適用
        if 'colors' in overrides:
            theme_data['colors'].update(overrides['colors'])
        
        for key, value in overrides.items():
            if key != 'colors':
                theme_data[key] = value
        
        # テーマを作成
        try:
            custom_theme = Theme.from_dict(theme_data)
            self.themes[name] = custom_theme
            self.save_themes()
            logger.info(f"🎨 カスタムテーマ作成: {name}")
            return True
        except Exception as e:
            logger.error(f"❌ カスタムテーマ作成エラー: {e}")
            return False
    
    def delete_theme(self, name: str) -> bool:
        """テーマを削除"""
        if name not in self.themes:
            logger.warning(f"⚠️ テーマが見つかりません: {name}")
            return False
        
        theme = self.themes[name]
        if theme.type != ThemeType.CUSTOM.value:
            logger.warning(f"⚠️ デフォルトテーマは削除できません: {name}")
            return False
        
        # 現在のテーマを削除する場合はライトテーマに変更
        if self.current_theme_name == name:
            self.current_theme_name = "light"
        
        del self.themes[name]
        self.save_themes()
        logger.info(f"🎨 テーマ削除: {name}")
        return True
    
    def get_stylesheet(self, theme_name: Optional[str] = None) -> str:
        """テーマのスタイルシートを生成"""
        theme = self.get_theme(theme_name) if theme_name else self.get_current_theme()
        colors = theme.colors
        
        return f"""
        QMainWindow {{
            background-color: {colors.background};
            color: {colors.text_primary};
            font-family: {theme.font_family};
            font-size: {theme.font_size}px;
        }}
        
        QWidget {{
            background-color: {colors.background};
            color: {colors.text_primary};
            font-family: {theme.font_family};
        }}
        
        QLabel {{
            color: {colors.text_primary};
            background-color: transparent;
        }}
        
        QPushButton {{
            background-color: {colors.primary};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: {theme.border_radius}px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {colors.secondary};
        }}
        
        QPushButton:pressed {{
            background-color: {colors.accent};
        }}
        
        QLineEdit {{
            background-color: {colors.surface};
            border: 2px solid {colors.border};
            border-radius: {theme.border_radius}px;
            padding: 8px;
            color: {colors.text_primary};
        }}
        
        QLineEdit:focus {{
            border-color: {colors.primary};
        }}
        
        QTextEdit {{
            background-color: {colors.surface};
            border: 2px solid {colors.border};
            border-radius: {theme.border_radius}px;
            padding: 8px;
            color: {colors.text_primary};
        }}
        
        QComboBox {{
            background-color: {colors.surface};
            border: 2px solid {colors.border};
            border-radius: {theme.border_radius}px;
            padding: 8px;
            color: {colors.text_primary};
        }}
        
        QComboBox:focus {{
            border-color: {colors.primary};
        }}
        
        QGroupBox {{
            font-weight: bold;
            border: 2px solid {colors.border};
            border-radius: {theme.border_radius}px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: {colors.surface};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: {colors.text_primary};
        }}
        
        QTabWidget::pane {{
            border: 2px solid {colors.border};
            border-radius: {theme.border_radius}px;
            background-color: {colors.surface};
        }}
        
        QTabWidget::tab-bar {{
            alignment: center;
        }}
        
        QTabBar::tab {{
            background-color: {colors.background};
            color: {colors.text_secondary};
            border: 2px solid {colors.border};
            border-bottom: none;
            border-radius: {theme.border_radius}px;
            padding: 8px 16px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors.primary};
            color: white;
        }}
        
        QTabBar::tab:hover {{
            background-color: {colors.secondary};
            color: white;
        }}
        
        QProgressBar {{
            border: 2px solid {colors.border};
            border-radius: {theme.border_radius}px;
            text-align: center;
            background-color: {colors.surface};
        }}
        
        QProgressBar::chunk {{
            background-color: {colors.success};
            border-radius: {theme.border_radius}px;
        }}
        
        QCheckBox {{
            color: {colors.text_primary};
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 2px solid {colors.border};
            border-radius: 3px;
            background-color: {colors.surface};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {colors.primary};
            border-color: {colors.primary};
        }}
        
        QSlider::groove:horizontal {{
            border: 1px solid {colors.border};
            height: 8px;
            background-color: {colors.surface};
            border-radius: 4px;
        }}
        
        QSlider::handle:horizontal {{
            background-color: {colors.primary};
            border: 1px solid {colors.border};
            width: 18px;
            border-radius: 9px;
            margin: -5px 0;
        }}
        
        QSlider::sub-page:horizontal {{
            background-color: {colors.primary};
            border-radius: 4px;
        }}
        """
    
    def get_theme_preview(self, theme_name: str) -> Dict:
        """テーマのプレビュー情報を取得"""
        theme = self.get_theme(theme_name)
        if not theme:
            return {}
        
        return {
            'name': theme.name,
            'type': theme.type,
            'primary_color': theme.colors.primary,
            'background_color': theme.colors.background,
            'text_color': theme.colors.text_primary,
            'font_family': theme.font_family,
            'font_size': theme.font_size,
            'border_radius': theme.border_radius
        }
    
    def export_theme(self, theme_name: str, filename: str) -> bool:
        """テーマをファイルにエクスポート"""
        theme = self.get_theme(theme_name)
        if not theme:
            logger.error(f"❌ テーマが見つかりません: {theme_name}")
            return False
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(theme.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"🎨 テーマエクスポート完了: {theme_name} -> {filename}")
            return True
        except Exception as e:
            logger.error(f"❌ テーマエクスポートエラー: {e}")
            return False
    
    def import_theme(self, filename: str) -> bool:
        """ファイルからテーマをインポート"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            theme = Theme.from_dict(data)
            theme.type = ThemeType.CUSTOM.value  # インポートしたテーマはカスタムテーマとして扱う
            
            self.themes[theme.name] = theme
            self.save_themes()
            
            logger.info(f"🎨 テーマインポート完了: {theme.name} <- {filename}")
            return True
        except Exception as e:
            logger.error(f"❌ テーマインポートエラー: {e}")
            return False