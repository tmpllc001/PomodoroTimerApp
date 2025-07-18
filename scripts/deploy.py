#!/usr/bin/env python3
"""
Deployment script for Pomodoro Timer Application.
Handles uploading releases, updating repositories, and distribution.
"""

import os
import sys
import subprocess
import json
import hashlib
import zipfile
from pathlib import Path
import argparse
import requests
from datetime import datetime


class PomodoroDeployer:
    """Deployment manager for Pomodoro Timer Application."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.dist_dir = self.project_root / "dist"
        self.version = self.get_version()
        
    def get_version(self):
        """Get application version."""
        try:
            # Try to get version from git tags
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            # Fallback to default version
            return "1.0.0"
            
    def calculate_checksums(self):
        """Calculate checksums for all distribution files."""
        print("Calculating checksums...")
        
        checksums = {}
        
        for file_path in self.dist_dir.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                # Calculate SHA256
                sha256_hash = hashlib.sha256()
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(chunk)
                        
                relative_path = file_path.relative_to(self.dist_dir)
                checksums[str(relative_path)] = {
                    'sha256': sha256_hash.hexdigest(),
                    'size': file_path.stat().st_size
                }
                
        # Save checksums file
        checksums_file = self.dist_dir / "checksums.json"
        with open(checksums_file, 'w') as f:
            json.dump(checksums, f, indent=2)
            
        print(f"✅ Checksums saved to {checksums_file}")
        return checksums
        
    def create_release_archives(self):
        """Create release archives for each platform."""
        print("Creating release archives...")
        
        archives = []
        
        # Find platform-specific builds
        platforms = {
            'windows': ['windows', 'portable'],
            'linux': ['linux', 'portable'],
            'macos': ['macos']
        }
        
        for platform, subdirs in platforms.items():
            for subdir in subdirs:
                platform_dir = self.dist_dir / subdir
                if not platform_dir.exists():
                    continue
                    
                # Create archive name
                archive_name = f"PomodoroTimer-{self.version}-{platform}"
                if subdir == "portable":
                    archive_name += "-portable"
                    
                if platform == 'windows':
                    archive_path = self.dist_dir / f"{archive_name}.zip"
                    self.create_zip_archive(platform_dir, archive_path)
                else:
                    archive_path = self.dist_dir / f"{archive_name}.tar.gz"
                    self.create_tar_archive(platform_dir, archive_path)
                    
                archives.append(archive_path)
                print(f"✅ Created {archive_path}")
                
        return archives
        
    def create_zip_archive(self, source_dir, archive_path):
        """Create ZIP archive."""
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir)
                    zipf.write(file_path, arcname)
                    
    def create_tar_archive(self, source_dir, archive_path):
        """Create TAR.GZ archive."""
        import tarfile
        
        with tarfile.open(archive_path, 'w:gz') as tarf:
            for file_path in source_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir)
                    tarf.add(file_path, arcname)
                    
    def generate_release_notes(self):
        """Generate release notes from git commits."""
        print("Generating release notes...")
        
        try:
            # Get commits since last tag
            result = subprocess.run([
                "git", "log", "--pretty=format:- %s", 
                f"{self.get_previous_version()}..HEAD"
            ], capture_output=True, text=True, check=True)
            
            commits = result.stdout.strip()
            
        except subprocess.CalledProcessError:
            commits = "- Initial release"
            
        release_notes = f"""# Pomodoro Timer {self.version}

## Changes
{commits}

## Downloads
- **Windows**: PomodoroTimer-{self.version}-windows.zip
- **Linux**: PomodoroTimer-{self.version}-linux.tar.gz  
- **macOS**: PomodoroTimer-{self.version}-macos.tar.gz

## Installation
1. Download the appropriate package for your platform
2. Extract the archive
3. Run the executable

## System Requirements
- **Windows**: Windows 10/11 (64-bit)
- **Linux**: Ubuntu 20.04+ or equivalent
- **macOS**: macOS 10.15+ (64-bit)

## Checksums
See `checksums.json` for file verification.

---
Built on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        notes_file = self.dist_dir / "RELEASE_NOTES.md"
        with open(notes_file, 'w') as f:
            f.write(release_notes)
            
        print(f"✅ Release notes saved to {notes_file}")
        return release_notes
        
    def get_previous_version(self):
        """Get previous version tag."""
        try:
            result = subprocess.run([
                "git", "tag", "--sort=-version:refname"
            ], capture_output=True, text=True, check=True)
            
            tags = result.stdout.strip().split('\n')
            if len(tags) > 1:
                return tags[1]  # Second most recent tag
            return tags[0] if tags else "HEAD~10"
            
        except subprocess.CalledProcessError:
            return "HEAD~10"
            
    def upload_to_github_releases(self, github_token):
        """Upload release to GitHub."""
        print("Uploading to GitHub Releases...")
        
        if not github_token:
            print("⚠️ No GitHub token provided, skipping upload")
            return False
            
        # GitHub API setup
        repo_owner = "your-username"  # Replace with actual
        repo_name = "pomodoro-timer"   # Replace with actual
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Create release
        release_data = {
            "tag_name": self.version,
            "name": f"Pomodoro Timer {self.version}",
            "body": self.generate_release_notes(),
            "draft": False,
            "prerelease": False
        }
        
        try:
            # Create release
            response = requests.post(f"{api_url}/releases", 
                                   headers=headers, json=release_data)
            response.raise_for_status()
            
            release_info = response.json()
            upload_url = release_info["upload_url"].replace("{?name,label}", "")
            
            # Upload assets
            for archive in self.create_release_archives():
                self.upload_release_asset(upload_url, archive, headers)
                
            # Upload checksums
            checksums_file = self.dist_dir / "checksums.json"
            if checksums_file.exists():
                self.upload_release_asset(upload_url, checksums_file, headers)
                
            print(f"✅ Release uploaded: {release_info['html_url']}")
            return True
            
        except requests.RequestException as e:
            print(f"❌ Failed to upload to GitHub: {e}")
            return False
            
    def upload_release_asset(self, upload_url, file_path, headers):
        """Upload a single release asset."""
        print(f"Uploading {file_path.name}...")
        
        upload_headers = headers.copy()
        upload_headers["Content-Type"] = "application/octet-stream"
        
        with open(file_path, 'rb') as f:
            response = requests.post(
                f"{upload_url}?name={file_path.name}",
                headers=upload_headers,
                data=f
            )
            response.raise_for_status()
            
    def update_package_managers(self):
        """Update package manager repositories."""
        print("Updating package managers...")
        
        # Update Chocolatey (Windows)
        self.update_chocolatey()
        
        # Update Homebrew (macOS)
        self.update_homebrew()
        
        # Update PPA (Ubuntu)
        self.update_ppa()
        
    def update_chocolatey(self):
        """Update Chocolatey package."""
        print("Updating Chocolatey package...")
        
        # Create chocolatey package files
        choco_dir = self.dist_dir / "chocolatey"
        choco_dir.mkdir(exist_ok=True)
        
        # Create nuspec file
        nuspec_content = f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://schemas.microsoft.com/packaging/2015/06/nuspec.xsd">
  <metadata>
    <id>pomodoro-timer</id>
    <version>{self.version}</version>
    <packageSourceUrl>https://github.com/your-repo/pomodoro-timer</packageSourceUrl>
    <owners>Pomodoro Timer Team</owners>
    <title>Pomodoro Timer</title>
    <authors>Pomodoro Timer Team</authors>
    <projectUrl>https://github.com/your-repo/pomodoro-timer</projectUrl>
    <iconUrl>https://raw.githubusercontent.com/your-repo/pomodoro-timer/main/assets/images/icon.png</iconUrl>
    <copyright>2024 Pomodoro Timer Team</copyright>
    <licenseUrl>https://github.com/your-repo/pomodoro-timer/blob/main/LICENSE</licenseUrl>
    <requireLicenseAcceptance>false</requireLicenseAcceptance>
    <projectSourceUrl>https://github.com/your-repo/pomodoro-timer</projectSourceUrl>
    <docsUrl>https://github.com/your-repo/pomodoro-timer/wiki</docsUrl>
    <bugTrackerUrl>https://github.com/your-repo/pomodoro-timer/issues</bugTrackerUrl>
    <tags>pomodoro timer productivity</tags>
    <summary>Simple and effective Pomodoro timer</summary>
    <description>A simple and effective Pomodoro timer application with transparent window and audio notifications.</description>
    <releaseNotes>See https://github.com/your-repo/pomodoro-timer/releases/tag/{self.version}</releaseNotes>
  </metadata>
  <files>
    <file src="tools\\**" target="tools" />
  </files>
</package>'''
        
        with open(choco_dir / "pomodoro-timer.nuspec", 'w') as f:
            f.write(nuspec_content)
            
        print("✅ Chocolatey package files created")
        
    def update_homebrew(self):
        """Update Homebrew formula."""
        print("Updating Homebrew formula...")
        
        # Create Homebrew formula
        formula_dir = self.dist_dir / "homebrew"
        formula_dir.mkdir(exist_ok=True)
        
        # Calculate SHA256 for macOS archive
        macos_archive = self.dist_dir / f"PomodoroTimer-{self.version}-macos.tar.gz"
        if macos_archive.exists():
            sha256 = hashlib.sha256()
            with open(macos_archive, 'rb') as f:
                sha256.update(f.read())
            sha256_hex = sha256.hexdigest()
        else:
            sha256_hex = "PLACEHOLDER"
            
        formula_content = f'''class PomodoroTimer < Formula
  desc "Simple and effective Pomodoro timer"
  homepage "https://github.com/your-repo/pomodoro-timer"
  url "https://github.com/your-repo/pomodoro-timer/releases/download/{self.version}/PomodoroTimer-{self.version}-macos.tar.gz"
  sha256 "{sha256_hex}"
  license "MIT"

  def install
    bin.install "PomodoroTimer"
    prefix.install "assets", "config"
  end

  test do
    system "{{bin}}/PomodoroTimer", "--version"
  end
end'''
        
        with open(formula_dir / "pomodoro-timer.rb", 'w') as f:
            f.write(formula_content)
            
        print("✅ Homebrew formula created")
        
    def update_ppa(self):
        """Update Ubuntu PPA."""
        print("Updating Ubuntu PPA...")
        
        # Create debian package files
        ppa_dir = self.dist_dir / "ppa"
        ppa_dir.mkdir(exist_ok=True)
        
        # Copy DEB package if it exists
        deb_file = self.dist_dir / f"pomodoro-timer_{self.version}_amd64.deb"
        if deb_file.exists():
            import shutil
            shutil.copy2(deb_file, ppa_dir)
            print("✅ DEB package copied to PPA directory")
        else:
            print("⚠️ DEB package not found")
            
    def validate_distribution(self):
        """Validate distribution files."""
        print("Validating distribution files...")
        
        required_files = [
            "checksums.json",
            "RELEASE_NOTES.md"
        ]
        
        for file_name in required_files:
            file_path = self.dist_dir / file_name
            if not file_path.exists():
                print(f"❌ Missing required file: {file_name}")
                return False
                
        # Validate checksums
        checksums_file = self.dist_dir / "checksums.json"
        with open(checksums_file) as f:
            checksums = json.load(f)
            
        for file_path, checksum_info in checksums.items():
            full_path = self.dist_dir / file_path
            if not full_path.exists():
                print(f"❌ File missing: {file_path}")
                return False
                
            # Verify file size
            actual_size = full_path.stat().st_size
            expected_size = checksum_info['size']
            
            if actual_size != expected_size:
                print(f"❌ Size mismatch for {file_path}: {actual_size} != {expected_size}")
                return False
                
        print("✅ Distribution validation passed")
        return True
        
    def deploy(self, github_token=None, upload_github=True, update_packages=False):
        """Deploy complete release."""
        print(f"🚀 Deploying Pomodoro Timer {self.version}")
        print("="*50)
        
        steps = [
            ("Calculating checksums", self.calculate_checksums),
            ("Creating release archives", self.create_release_archives),
            ("Generating release notes", self.generate_release_notes),
            ("Validating distribution", self.validate_distribution),
        ]
        
        if upload_github:
            steps.append(("Uploading to GitHub", 
                         lambda: self.upload_to_github_releases(github_token)))
            
        if update_packages:
            steps.append(("Updating package managers", self.update_package_managers))
            
        # Execute deployment steps
        for step_name, step_func in steps:
            print(f"\n{step_name}...")
            if not step_func():
                print(f"❌ Deployment failed at: {step_name}")
                return False
                
        print("\n" + "="*50)
        print("🎉 Deployment completed successfully!")
        self.show_deployment_summary()
        
    def show_deployment_summary(self):
        """Show deployment summary."""
        print(f"\n📋 Deployment Summary for v{self.version}:")
        print(f"📦 Distribution directory: {self.dist_dir}")
        
        total_size = 0
        file_count = 0
        
        for item in self.dist_dir.rglob("*"):
            if item.is_file():
                size = item.stat().st_size
                total_size += size
                file_count += 1
                
        print(f"📄 Total files: {file_count}")
        print(f"💾 Total size: {total_size / (1024 * 1024):.1f} MB")
        
        # Show available downloads
        print("\n📥 Available Downloads:")
        for archive in self.dist_dir.glob("*.zip"):
            print(f"  🪟 {archive.name}")
        for archive in self.dist_dir.glob("*.tar.gz"):
            print(f"  🐧 {archive.name}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Deploy Pomodoro Timer Application")
    parser.add_argument("--github-token", help="GitHub API token for release upload")
    parser.add_argument("--no-github", action="store_true", 
                       help="Skip GitHub release upload")
    parser.add_argument("--update-packages", action="store_true",
                       help="Update package manager repositories")
    parser.add_argument("--validate-only", action="store_true",
                       help="Only validate distribution files")
    
    args = parser.parse_args()
    
    deployer = PomodoroDeployer()
    
    if args.validate_only:
        deployer.validate_distribution()
        return
        
    # Get GitHub token from environment if not provided
    github_token = args.github_token or os.getenv("GITHUB_TOKEN")
    
    deployer.deploy(
        github_token=github_token,
        upload_github=not args.no_github,
        update_packages=args.update_packages
    )


if __name__ == "__main__":
    main()