#!/usr/bin/env python3
"""
Requirements o'rnatish va FFmpeg setup skripti
"""

import subprocess
import sys
import os
from pathlib import Path


def install_python_requirements():
    """Python requirements o'rnatish"""
    print("📦 Python requirements o'rnatilmoqda...")
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], check=True, capture_output=True, text=True)
        print("✅ Python requirements muvaffaqiyatli o'rnatildi!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Python requirements o'rnatishda xato: {e.stderr}")
        return False


def setup_ffmpeg():
    """FFmpeg setup skriptini chaqirish"""
    print("\n🎵 FFmpeg setup boshlanyapti...")
    try:
        result = subprocess.run([sys.executable, 'setup_ffmpeg.py'], check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ FFmpeg setup muvaffaqiyatsiz")
        return False


def main():
    """Asosiy setup jarayoni"""
    print("🚀 Audio To Voice Bot - Full Setup")
    print("=" * 50)
    
    # Python requirements
    if not install_python_requirements():
        print("❌ Python requirements o'rnatib bo'lmadi")
        return False
    
    # FFmpeg setup
    if not setup_ffmpeg():
        print("❌ FFmpeg setup muvaffaqiyatsiz")
        return False
    
    print("\n🎉 Barcha setup'lar muvaffaqiyatli yakunlandi!")
    print("ℹ️  Endi botni ishga tushirishingiz mumkin: python main.py")
    return True


if __name__ == "__main__":
    try:
        success = main()
        if not success:
            input("\nEnter tugmasini bosing...")
            sys.exit(1)
        input("\nEnter tugmasini bosing...")
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup bekor qilindi")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Kutilmagan xato: {e}")
        input("Enter tugmasini bosing...")
        sys.exit(1)
