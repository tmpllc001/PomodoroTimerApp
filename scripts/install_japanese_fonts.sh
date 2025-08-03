#!/bin/bash
# ========================================
# Japanese Font Installation Script for Linux
# ========================================

echo "🔧 日本語フォントインストールスクリプト"
echo "========================================="

# OSの種類を検出
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    echo "❌ OS情報を取得できません"
    exit 1
fi

echo "📍 検出されたOS: $OS $VER"

# Debian/Ubuntu系
if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    echo "🔄 Ubuntu/Debian用フォントをインストール中..."
    sudo apt-get update
    sudo apt-get install -y fonts-noto-cjk fonts-ipafont fonts-takao
    
# RHEL/CentOS/Fedora系
elif [[ "$OS" == *"Red Hat"* ]] || [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Fedora"* ]]; then
    echo "🔄 RHEL/CentOS/Fedora用フォントをインストール中..."
    sudo yum install -y google-noto-cjk-fonts ipa-gothic-fonts ipa-mincho-fonts
    
# Arch Linux
elif [[ "$OS" == *"Arch"* ]]; then
    echo "🔄 Arch Linux用フォントをインストール中..."
    sudo pacman -S --noconfirm noto-fonts-cjk adobe-source-han-sans-jp-fonts
    
# openSUSE
elif [[ "$OS" == *"openSUSE"* ]]; then
    echo "🔄 openSUSE用フォントをインストール中..."
    sudo zypper install -y google-noto-sans-cjk-fonts
    
else
    echo "⚠️ サポートされていないOSです: $OS"
    echo "手動でNoto CJKフォントをインストールしてください"
    exit 1
fi

# フォントキャッシュを更新
echo "🔄 フォントキャッシュを更新中..."
fc-cache -fv

echo "✅ 日本語フォントのインストールが完了しました！"
echo ""
echo "📝 確認方法:"
echo "  fc-list | grep -i 'noto.*cjk'"
echo "  fc-list | grep -i 'ipa'"
echo ""
echo "🔄 matplotlibのフォントキャッシュをリセットする場合:"
echo "  rm -rf ~/.cache/matplotlib