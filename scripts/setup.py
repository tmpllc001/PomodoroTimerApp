#!/usr/bin/env python3
"""
Setup script for Pomodoro Timer Application
Handles environment setup, dependency installation, and project configuration.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path


class PomodoroSetup:
    """Setup manager for Pomodoro Timer Application."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.python_version = sys.version_info
        self.platform = platform.system()
        
    def check_python_version(self):
        """Check if Python version is compatible."""
        print("Checking Python version...")
        if self.python_version < (3, 8):
            print("❌ Python 3.8 or higher is required")
            print(f"Current version: {sys.version}")
            return False
        print(f"✅ Python {sys.version} is compatible")
        return True
        
    def check_system_dependencies(self):
        """Check system-specific dependencies."""
        print("Checking system dependencies...")
        
        if self.platform == "Linux":
            # Check for required libraries
            try:
                import distro
                dist = distro.id()
                print(f"Detected Linux distribution: {dist}")
                
                if dist in ["ubuntu", "debian"]:
                    print("Note: Make sure to install: sudo apt-get install libasound2-dev")
                elif dist in ["fedora", "centos", "rhel"]:
                    print("Note: Make sure to install: sudo yum install alsa-lib-devel")
                    
            except ImportError:
                print("Note: Install system audio libraries if needed")
                
        elif self.platform == "Darwin":
            print("✅ macOS detected - no additional system dependencies needed")
            
        elif self.platform == "Windows":
            print("✅ Windows detected - no additional system dependencies needed")
            
        return True
        
    def create_virtual_environment(self):
        """Create Python virtual environment."""
        print("Setting up virtual environment...")
        
        venv_path = self.project_root / "venv"
        if venv_path.exists():
            print("Virtual environment already exists")
            return True
            
        try:
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], 
                          check=True, capture_output=True)
            print("✅ Virtual environment created successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
            
    def install_dependencies(self):
        """Install Python dependencies."""
        print("Installing dependencies...")
        
        # Determine pip executable path
        venv_path = self.project_root / "venv"
        if venv_path.exists():
            if self.platform == "Windows":
                pip_path = venv_path / "Scripts" / "pip.exe"
            else:
                pip_path = venv_path / "bin" / "pip"
        else:
            pip_path = "pip"
            
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            print("❌ requirements.txt not found")
            return False
            
        try:
            subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], 
                          check=True, capture_output=True)
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
            
    def setup_directories(self):
        """Create necessary directories."""
        print("Setting up directories...")
        
        directories = [
            self.project_root / "logs",
            self.project_root / "config",
            self.project_root / "data",
            self.project_root / "temp",
            self.project_root / "assets" / "audio",
            self.project_root / "assets" / "images",
            self.project_root / "assets" / "styles"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory}")
            
        return True
        
    def create_config_files(self):
        """Create default configuration files."""
        print("Creating configuration files...")
        
        # Create default settings
        config_file = self.project_root / "config" / "settings.json"
        if not config_file.exists():
            default_config = {
                "timer": {
                    "work_duration": 25,
                    "short_break_duration": 5,
                    "long_break_duration": 15,
                    "cycles_until_long_break": 4
                },
                "audio": {
                    "sound_enabled": True,
                    "notification_enabled": True,
                    "volume": 0.7
                },
                "ui": {
                    "theme": "dark",
                    "opacity": 0.8,
                    "always_on_top": True
                }
            }
            
            import json
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print("✅ Created default settings.json")
            
        # Create logging configuration
        log_config = self.project_root / "config" / "logging.conf"
        if not log_config.exists():
            log_content = """
[loggers]
keys=root,app

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=DEBUG
handlers=consoleHandler

[logger_app]
level=INFO
handlers=consoleHandler,fileHandler
qualname=app
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=DEBUG
formatter=simpleFormatter
args=('logs/pomodoro.log',)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
"""
            with open(log_config, 'w') as f:
                f.write(log_content.strip())
            print("✅ Created logging configuration")
            
        return True
        
    def setup_git_hooks(self):
        """Set up Git hooks for development."""
        print("Setting up Git hooks...")
        
        git_dir = self.project_root / ".git"
        if not git_dir.exists():
            print("No Git repository found - skipping Git hooks")
            return True
            
        hooks_dir = git_dir / "hooks"
        pre_commit_hook = hooks_dir / "pre-commit"
        
        if not pre_commit_hook.exists():
            hook_content = """#!/bin/bash
# Pre-commit hook for code quality checks

echo "Running pre-commit checks..."

# Run tests
python -m pytest tests/ --tb=short
if [ $? -ne 0 ]; then
    echo "❌ Tests failed. Commit aborted."
    exit 1
fi

# Run linting
python -m flake8 src tests
if [ $? -ne 0 ]; then
    echo "❌ Linting failed. Commit aborted."
    exit 1
fi

# Run formatting check
python -m black --check src tests
if [ $? -ne 0 ]; then
    echo "❌ Code formatting check failed. Run 'black src tests' to fix."
    exit 1
fi

echo "✅ Pre-commit checks passed"
"""
            with open(pre_commit_hook, 'w') as f:
                f.write(hook_content)
            pre_commit_hook.chmod(0o755)
            print("✅ Created pre-commit hook")
            
        return True
        
    def run_tests(self):
        """Run test suite to verify setup."""
        print("Running tests to verify setup...")
        
        try:
            result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "--tb=short"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ All tests passed")
                return True
            else:
                print(f"❌ Some tests failed:")
                print(result.stdout)
                print(result.stderr)
                return False
                
        except FileNotFoundError:
            print("❌ pytest not found. Make sure dependencies are installed.")
            return False
            
    def print_usage_instructions(self):
        """Print usage instructions."""
        print("\n" + "="*50)
        print("🍅 Pomodoro Timer Setup Complete!")
        print("="*50)
        print("\nUsage Instructions:")
        print("1. Activate virtual environment:")
        
        if self.platform == "Windows":
            print("   .\\venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
            
        print("2. Run the application:")
        print("   python main.py")
        print("\n3. Run tests:")
        print("   pytest tests/")
        print("\n4. Configuration:")
        print("   Edit config/settings.json for custom settings")
        print("\n5. Development:")
        print("   - Use 'black src tests' for code formatting")
        print("   - Use 'flake8 src tests' for linting")
        print("   - Pre-commit hooks are installed for quality checks")
        print("\n" + "="*50)
        
    def run_setup(self):
        """Run complete setup process."""
        print("🍅 Pomodoro Timer Application Setup")
        print("="*40)
        
        steps = [
            ("Checking Python version", self.check_python_version),
            ("Checking system dependencies", self.check_system_dependencies),
            ("Creating virtual environment", self.create_virtual_environment),
            ("Installing dependencies", self.install_dependencies),
            ("Setting up directories", self.setup_directories),
            ("Creating configuration files", self.create_config_files),
            ("Setting up Git hooks", self.setup_git_hooks),
            ("Running tests", self.run_tests)
        ]
        
        for step_name, step_func in steps:
            print(f"\n{step_name}...")
            if not step_func():
                print(f"❌ Setup failed at: {step_name}")
                sys.exit(1)
                
        self.print_usage_instructions()


def main():
    """Main entry point."""
    setup = PomodoroSetup()
    setup.run_setup()


if __name__ == "__main__":
    main()