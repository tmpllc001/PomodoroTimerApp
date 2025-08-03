#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
アプリケーションパス管理モジュール

開発環境と実行ファイル環境の両方で正しく動作するパス管理を提供します。
"""

import sys
from pathlib import Path

def get_base_path() -> Path:
    """
    アプリケーションのベースパスを取得
    
    Returns:
        Path: アプリケーションのベースディレクトリ
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # PyInstallerでパッケージ化されている場合
        return Path(sys._MEIPASS)
    else:
        # 開発環境（スクリプトとして実行されている場合）
        return Path(__file__).parent

def get_data_dir() -> Path:
    """
    データディレクトリのパスを取得
    
    Returns:
        Path: データディレクトリのパス
    """
    if getattr(sys, 'frozen', False):
        # 実行ファイルの場合、実行ファイルと同じディレクトリ
        return Path(sys.executable).parent / 'data'
    else:
        # 開発環境
        return get_base_path() / 'data'

def get_resource_path(relative_path: str) -> Path:
    """
    リソースファイルのパスを取得
    
    Args:
        relative_path: ベースパスからの相対パス
        
    Returns:
        Path: リソースファイルの絶対パス
    """
    return get_base_path() / relative_path

def ensure_data_dirs():
    """
    必要なデータディレクトリを作成
    """
    data_dir = get_data_dir()
    data_dir.mkdir(exist_ok=True)
    
    # サブディレクトリも作成
    (data_dir / 'charts').mkdir(exist_ok=True)
    (data_dir / 'reports').mkdir(exist_ok=True)
    (data_dir / 'exports').mkdir(exist_ok=True)

# アプリケーション情報
APP_NAME = "Pomodoro Timer"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Your Name"
APP_DESCRIPTION = "高機能ポモドーロタイマー with AI分析機能"