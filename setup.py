#!/usr/bin/env python3
"""
Setup script for US Airlines Data Normalization Project
Automates the setup process for the project environment.
"""

import os
import subprocess
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version}")

def create_virtual_environment():
    """Create and activate virtual environment."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists.")
        return
    
    print("📦 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating virtual environment: {e}")
        sys.exit(1)

def install_requirements():
    """Install Python requirements."""
    print("📥 Installing Python requirements...")
    
    # Determine the correct pip path based on OS
    if os.name == 'nt':  # Windows
        pip_path = Path("venv/Scripts/pip")
    else:  # Unix-like systems
        pip_path = Path("venv/bin/pip")
    
    try:
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        print("✅ Requirements installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        sys.exit(1)

def setup_config():
    """Set up configuration file."""
    config_example = Path("config.example.py")
    config_file = Path("config.py")
    
    if config_file.exists():
        print("✅ Configuration file already exists.")
        return
    
    if config_example.exists():
        try:
            import shutil
            shutil.copy(config_example, config_file)
            print("✅ Configuration file created from example.")
            print("⚠️  Please update config.py with your database credentials.")
        except Exception as e:
            print(f"❌ Error creating config file: {e}")
    else:
        print("⚠️  config.example.py not found. Please create config.py manually.")

def check_directory_structure():
    """Check if required directories exist."""
    required_dirs = ["archive", "normalized_data"]
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            print(f"📁 Creating directory: {dir_name}")
            dir_path.mkdir(exist_ok=True)
        else:
            print(f"✅ Directory exists: {dir_name}")

def display_activation_instructions():
    """Display instructions for activating the virtual environment."""
    print("\n" + "="*60)
    print("🎉 Setup completed successfully!")
    print("="*60)
    print("\nTo activate the virtual environment:")
    
    if os.name == 'nt':  # Windows
        print("  .\\venv\\Scripts\\activate")
    else:  # Unix-like systems
        print("  source venv/bin/activate")
    
    print("\nNext steps:")
    print("1. Activate the virtual environment (command above)")
    print("2. Update config.py with your database credentials")
    print("3. Run: python normalize_to_postgres.py")
    print("\nFor more information, see README.md")

def main():
    """Main setup function."""
    print("🚀 Setting up US Airlines Data Normalization Project")
    print("=" * 60)
    
    check_python_version()
    create_virtual_environment()
    install_requirements()
    setup_config()
    check_directory_structure()
    display_activation_instructions()

if __name__ == "__main__":
    main() 