#!/usr/bin/env python3
"""
Build script for Pomodoro Timer Application.
Handles cross-platform building, packaging, and distribution.
"""

import os
import sys
import subprocess
import platform
import shutil
import json
from pathlib import Path
import argparse


class PomodoroBuilder:
    """Build manager for Pomodoro Timer Application."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.platform = platform.system()
        self.arch = platform.machine()
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        
    def clean_build_dirs(self):
        """Clean build and dist directories."""
        print("Cleaning build directories...")
        
        for directory in [self.build_dir, self.dist_dir]:
            if directory.exists():
                shutil.rmtree(directory)
                print(f"Removed {directory}")
            directory.mkdir(parents=True, exist_ok=True)
            print(f"Created {directory}")
            
    def install_build_dependencies(self):
        """Install build dependencies."""
        print("Installing build dependencies...")
        
        dependencies = [
            "PyInstaller>=5.0.0",
            "auto-py-to-exe>=2.0.0"
        ]
        
        for dep in dependencies:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                              check=True, capture_output=True)
                print(f"✅ Installed {dep}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {dep}: {e}")
                return False
                
        return True
        
    def create_pyinstaller_spec(self):
        """Create PyInstaller spec file."""
        print("Creating PyInstaller spec file...")
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['{self.project_root}'],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('config', 'config'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'pygame',
        'pygame.mixer',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PomodoroTimer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{"assets/images/icon.ico" if self.platform == "Windows" else "assets/images/icon.icns"}',
)
'''
        
        spec_file = self.project_root / "PomodoroTimer.spec"
        with open(spec_file, 'w') as f:
            f.write(spec_content)
            
        print(f"✅ Created {spec_file}")
        return spec_file
        
    def build_executable(self, debug=False):
        """Build executable using PyInstaller."""
        print(f"Building executable for {self.platform}...")
        
        # Create spec file
        spec_file = self.create_pyinstaller_spec()
        
        # Prepare PyInstaller command
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            f"--distpath={self.dist_dir}",
            f"--workpath={self.build_dir}",
        ]
        
        if debug:
            cmd.append("--debug=all")
        else:
            cmd.extend(["--onefile", "--windowed"])
            
        # Platform-specific options
        if self.platform == "Windows":
            cmd.extend([
                "--icon=assets/images/icon.ico",
                "--add-data=assets;assets",
                "--add-data=config;config",
            ])
        else:
            cmd.extend([
                "--add-data=assets:assets",
                "--add-data=config:config",
            ])
            
        # Add main script
        cmd.append("main.py")
        
        try:
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ Build completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed: {e}")
            print(f"Output: {e.stdout}")
            print(f"Error: {e.stderr}")
            return False
            
    def create_installer_windows(self):
        """Create Windows installer using NSIS."""
        print("Creating Windows installer...")
        
        nsis_script = self.project_root / "installer.nsi"
        nsis_content = f'''!define APPNAME "Pomodoro Timer"
!define COMPANYNAME "Pomodoro Timer Team"
!define DESCRIPTION "Productivity timer application"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0

!define HELPURL "https://github.com/your-repo/pomodoro-timer"
!define UPDATEURL "https://github.com/your-repo/pomodoro-timer/releases"
!define ABOUTURL "https://github.com/your-repo/pomodoro-timer"

!define INSTALLSIZE 50000  # 50MB

RequestExecutionLevel user

InstallDir "$LOCALAPPDATA\\${{APPNAME}}"

Name "${{APPNAME}}"
outFile "dist\\PomodoroTimer-Setup.exe"

!include LogicLib.nsh

page directory
page instfiles

!macro VerifyUserIsAdmin
UserInfo::GetAccountType
pop $0
${{If}} $0 != "admin"
        messageBox mb_iconstop "Administrator rights required!"
        setErrorLevel 740
        quit
${{EndIf}}
!macroend

section "install"
    setOutPath $INSTDIR
    
    file "dist\\PomodoroTimer.exe"
    file /r "assets"
    file /r "config"
    file "README.md"
    file "LICENSE"
    
    createShortcut "$SMPROGRAMS\\${{APPNAME}}.lnk" "$INSTDIR\\PomodoroTimer.exe"
    createShortcut "$DESKTOP\\${{APPNAME}}.lnk" "$INSTDIR\\PomodoroTimer.exe"
    
    writeUninstaller "$INSTDIR\\uninstall.exe"
    
    # Registry entries
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "DisplayName" "${{APPNAME}}"
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "UninstallString" "$INSTDIR\\uninstall.exe"
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "DisplayIcon" "$INSTDIR\\PomodoroTimer.exe"
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "Publisher" "${{COMPANYNAME}}"
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "HelpLink" "${{HELPURL}}"
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "URLUpdateInfo" "${{UPDATEURL}}"
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "URLInfoAbout" "${{ABOUTURL}}"
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "DisplayVersion" "${{VERSIONMAJOR}}.${{VERSIONMINOR}}.${{VERSIONBUILD}}"
    WriteRegDWORD HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "VersionMajor" ${{VERSIONMAJOR}}
    WriteRegDWORD HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "VersionMinor" ${{VERSIONMINOR}}
    WriteRegDWORD HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "EstimatedSize" ${{INSTALLSIZE}}
sectionEnd

section "uninstall"
    delete "$INSTDIR\\PomodoroTimer.exe"
    delete "$INSTDIR\\uninstall.exe"
    rmDir /r "$INSTDIR\\assets"
    rmDir /r "$INSTDIR\\config"
    rmDir "$INSTDIR"
    
    delete "$SMPROGRAMS\\${{APPNAME}}.lnk"
    delete "$DESKTOP\\${{APPNAME}}.lnk"
    
    DeleteRegKey HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}"
sectionEnd
'''
        
        with open(nsis_script, 'w') as f:
            f.write(nsis_content)
            
        # Try to build installer
        try:
            subprocess.run(["makensis", str(nsis_script)], check=True)
            print("✅ Windows installer created")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ NSIS not found, skipping installer creation")
            return False
            
    def create_portable_package(self):
        """Create portable package."""
        print("Creating portable package...")
        
        portable_dir = self.dist_dir / "portable"
        portable_dir.mkdir(exist_ok=True)
        
        # Copy executable
        if self.platform == "Windows":
            exe_name = "PomodoroTimer.exe"
        else:
            exe_name = "PomodoroTimer"
            
        exe_path = self.dist_dir / exe_name
        if exe_path.exists():
            shutil.copy2(exe_path, portable_dir)
            
        # Copy assets and config
        for folder in ["assets", "config"]:
            src = self.project_root / folder
            dst = portable_dir / folder
            if src.exists():
                shutil.copytree(src, dst, dirs_exist_ok=True)
                
        # Copy documentation
        for file in ["README.md", "LICENSE"]:
            src = self.project_root / file
            dst = portable_dir / file
            if src.exists():
                shutil.copy2(src, dst)
                
        # Create run script
        if self.platform == "Windows":
            run_script = portable_dir / "run.bat"
            with open(run_script, 'w') as f:
                f.write('@echo off\nstart "" "%~dp0PomodoroTimer.exe"\n')
        else:
            run_script = portable_dir / "run.sh"
            with open(run_script, 'w') as f:
                f.write('#!/bin/bash\ncd "$(dirname "$0")"\n./PomodoroTimer\n')
            run_script.chmod(0o755)
            
        # Make executable file executable on Unix
        if self.platform != "Windows":
            exe_portable = portable_dir / exe_name
            if exe_portable.exists():
                exe_portable.chmod(0o755)
                
        print(f"✅ Portable package created in {portable_dir}")
        return True
        
    def create_dmg_macos(self):
        """Create DMG package for macOS."""
        if self.platform != "Darwin":
            return False
            
        print("Creating macOS DMG package...")
        
        try:
            dmg_path = self.dist_dir / "PomodoroTimer.dmg"
            app_path = self.dist_dir / "PomodoroTimer.app"
            
            # Create DMG
            cmd = [
                "hdiutil", "create",
                "-srcfolder", str(app_path),
                "-volname", "Pomodoro Timer",
                "-fs", "HFS+",
                "-fsargs", "-c c=64,a=16,e=16",
                "-format", "UDZO",
                str(dmg_path)
            ]
            
            subprocess.run(cmd, check=True)
            print(f"✅ DMG package created: {dmg_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create DMG: {e}")
            return False
            
    def create_deb_package(self):
        """Create DEB package for Ubuntu/Debian."""
        if self.platform != "Linux":
            return False
            
        print("Creating DEB package...")
        
        package_dir = self.dist_dir / "deb"
        package_dir.mkdir(exist_ok=True)
        
        # Create package structure
        debian_dir = package_dir / "DEBIAN"
        usr_dir = package_dir / "usr"
        bin_dir = usr_dir / "bin"
        share_dir = usr_dir / "share"
        app_dir = share_dir / "pomodoro-timer"
        desktop_dir = share_dir / "applications"
        
        for directory in [debian_dir, bin_dir, app_dir, desktop_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            
        # Create control file
        control_content = f'''Package: pomodoro-timer
Version: 1.0.0
Section: utils
Priority: optional
Architecture: amd64
Depends: libc6, libqt6core6, libqt6gui6, libqt6widgets6
Maintainer: Pomodoro Timer Team <team@pomodoro-timer.com>
Description: Productivity timer application
 A simple and effective Pomodoro timer application built with PyQt6.
 Features transparent window, audio notifications, and session tracking.
'''
        
        with open(debian_dir / "control", 'w') as f:
            f.write(control_content)
            
        # Copy files
        exe_path = self.dist_dir / "PomodoroTimer"
        if exe_path.exists():
            shutil.copy2(exe_path, bin_dir)
            
        # Copy app files
        for folder in ["assets", "config"]:
            src = self.project_root / folder
            dst = app_dir / folder
            if src.exists():
                shutil.copytree(src, dst, dirs_exist_ok=True)
                
        # Create desktop file
        desktop_content = f'''[Desktop Entry]
Version=1.0
Type=Application
Name=Pomodoro Timer
Comment=Productivity timer application
Exec=/usr/bin/PomodoroTimer
Icon=/usr/share/pomodoro-timer/assets/images/icon.png
Terminal=false
Categories=Utility;
'''
        
        with open(desktop_dir / "pomodoro-timer.desktop", 'w') as f:
            f.write(desktop_content)
            
        # Build package
        try:
            subprocess.run(["dpkg-deb", "--build", str(package_dir), 
                           str(self.dist_dir / "pomodoro-timer_1.0.0_amd64.deb")], 
                          check=True)
            print("✅ DEB package created")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ dpkg-deb not found, skipping DEB creation")
            return False
            
    def run_tests_before_build(self):
        """Run tests before building."""
        print("Running tests before build...")
        
        try:
            result = subprocess.run([sys.executable, "test_runner.py"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ All tests passed")
                return True
            else:
                print(f"❌ Tests failed:")
                print(result.stdout)
                print(result.stderr)
                return False
                
        except FileNotFoundError:
            print("⚠️ test_runner.py not found, skipping tests")
            return True
            
    def build_all(self, debug=False, skip_tests=False):
        """Build complete distribution."""
        print(f"🍅 Building Pomodoro Timer for {self.platform}")
        print("="*50)
        
        steps = [
            ("Cleaning build directories", self.clean_build_dirs),
            ("Installing build dependencies", self.install_build_dependencies),
        ]
        
        if not skip_tests:
            steps.append(("Running tests", self.run_tests_before_build))
            
        steps.extend([
            ("Building executable", lambda: self.build_executable(debug)),
            ("Creating portable package", self.create_portable_package),
        ])
        
        # Platform-specific packaging
        if self.platform == "Windows":
            steps.append(("Creating Windows installer", self.create_installer_windows))
        elif self.platform == "Darwin":
            steps.append(("Creating macOS DMG", self.create_dmg_macos))
        elif self.platform == "Linux":
            steps.append(("Creating DEB package", self.create_deb_package))
            
        # Execute all steps
        for step_name, step_func in steps:
            print(f"\n{step_name}...")
            if not step_func():
                print(f"❌ Failed at: {step_name}")
                return False
                
        print("\n" + "="*50)
        print("🎉 Build completed successfully!")
        print(f"📦 Output directory: {self.dist_dir}")
        self.show_build_summary()
        
    def show_build_summary(self):
        """Show build summary."""
        print("\n📋 Build Summary:")
        
        for item in self.dist_dir.rglob("*"):
            if item.is_file():
                size = item.stat().st_size
                size_mb = size / (1024 * 1024)
                print(f"  📄 {item.relative_to(self.dist_dir)} ({size_mb:.1f} MB)")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build Pomodoro Timer Application")
    parser.add_argument("--debug", action="store_true", 
                       help="Build with debug information")
    parser.add_argument("--skip-tests", action="store_true",
                       help="Skip running tests before build")
    parser.add_argument("--clean", action="store_true",
                       help="Only clean build directories")
    
    args = parser.parse_args()
    
    builder = PomodoroBuilder()
    
    if args.clean:
        builder.clean_build_dirs()
        return
        
    builder.build_all(debug=args.debug, skip_tests=args.skip_tests)


if __name__ == "__main__":
    main()