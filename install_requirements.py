#!/usr/bin/env python3
"""
Requirements o'rnatish va FFmpeg setup skripti
"""

import subprocess
import sys
import os
from pathlib import Path


def check_requirements_installed():
    """O'rnatilgan paketlarni tekshirish"""
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            requirements = f.read().strip().split('\n')
        
        missing_packages = []
        for req in requirements:
            if req.strip() and not req.startswith('#'):
                package_name = req.split('==')[0].split('>=')[0].split('<=')[0].strip()
                try:
                    __import__(package_name.replace('-', '_'))
                except ImportError:
                    missing_packages.append(package_name)
        
        return len(missing_packages) == 0, missing_packages
    except Exception:
        return False, []


def install_python_requirements():
    """Python requirements o'rnatish"""
    print("🔍 Python requirements tekshirilmoqda...")
    
    # Avval tekshirish
    is_installed, missing = check_requirements_installed()
    
    if is_installed:
        print("✅ Barcha Python paketlar allaqachon o'rnatilgan!")
        return True
    
    if missing:
        print(f"📦 {len(missing)} ta paket o'rnatilishi kerak: {', '.join(missing[:3])}{'...' if len(missing) > 3 else ''}")
    
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


def is_ffmpeg_available():
    """FFmpeg mavjudligini tekshirish"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return False


def setup_ffmpeg():
    """FFmpeg setup skriptini chaqirish"""
    print("\n🔍 FFmpeg tekshirilmoqda...")
    
    if is_ffmpeg_available():
        print("✅ FFmpeg allaqachon o'rnatilgan va ishlayapti!")
        return True
    
    print("📦 FFmpeg topilmadi. O'rnatish boshlanyapti...")
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
    
    setup_success = True
    
    # Python requirements
    python_result = install_python_requirements()
    if not python_result:
        print("❌ Python requirements o'rnatib bo'lmadi")
        setup_success = False
    
    # FFmpeg setup
    ffmpeg_result = setup_ffmpeg()
    if not ffmpeg_result:
        print("❌ FFmpeg setup muvaffaqiyatsiz")
        setup_success = False
    
    print("\n" + "=" * 50)
    if setup_success:
        print("🎉 Barcha setup'lar muvaffaqiyatli yakunlandi!")
        print("✅ Python paketlar: O'rnatilgan")
        print("✅ FFmpeg: Tayyor")
        print("\nℹ️  Endi botni ishga tushirishingiz mumkin:")
        print("   python main.py")
    else:
        print("⚠️  Ba'zi setup'lar muvaffaqiyatsiz bo'ldi")
        if not python_result:
            print("❌ Python paketlar: Muammo bor")
        if not ffmpeg_result:
            print("❌ FFmpeg: Muammo bor")
    
    return setup_success


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
