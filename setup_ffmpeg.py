#!/usr/bin/env python3
"""
FFmpeg avtomatik o'rnatish va PATH sozlash skripti
Windows uchun winget orqali FFmpeg o'rnatadi va PATH'ga qo'shadi
"""

import os
import sys
import subprocess
import platform
import winreg
from pathlib import Path
import shutil


def is_windows():
    """Windows OS ekanligini tekshirish"""
    return platform.system().lower() == 'windows'


def is_ffmpeg_installed():
    """FFmpeg o'rnatilganligini tekshirish"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return False


def is_winget_available():
    """Winget mavjudligini tekshirish"""
    try:
        result = subprocess.run(['winget', '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return False


def install_ffmpeg_with_winget():
    """Winget orqali FFmpeg o'rnatish"""
    print("📦 FFmpeg o'rnatilmoqda...")
    try:
        result = subprocess.run([
            'winget', 'install', 'ffmpeg', '--accept-package-agreements', '--accept-source-agreements'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ FFmpeg muvaffaqiyatli o'rnatildi!")
            return True
        else:
            print(f"❌ FFmpeg o'rnatishda xato: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ FFmpeg o'rnatish vaqti tugadi")
        return False
    except Exception as e:
        print(f"❌ FFmpeg o'rnatishda xato: {e}")
        return False


def find_ffmpeg_path():
    """FFmpeg o'rnatilgan joyni topish"""
    possible_paths = [
        # Winget standard path
        os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Packages"),
        # Chocolatey path
        r"C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin",
        # Manual installation paths
        r"C:\ffmpeg\bin",
        r"C:\Program Files\ffmpeg\bin",
        r"C:\Program Files (x86)\ffmpeg\bin",
    ]
    
    # Winget packages ichidan qidirish
    winget_packages = os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Packages")
    if os.path.exists(winget_packages):
        for item in os.listdir(winget_packages):
            if 'ffmpeg' in item.lower():
                ffmpeg_bin = os.path.join(winget_packages, item, "ffmpeg-8.0-full_build", "bin")
                if os.path.exists(ffmpeg_bin):
                    possible_paths.insert(0, ffmpeg_bin)
    
    # Har bir path'ni tekshirish
    for path in possible_paths:
        if os.path.exists(path):
            ffmpeg_exe = os.path.join(path, "ffmpeg.exe")
            if os.path.exists(ffmpeg_exe):
                return path
    
    return None


def add_to_system_path(path):
    """PATH'ga qo'shish (Windows Registry orqali)"""
    try:
        # System PATH'ni o'qish
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                           r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                           0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            
            current_path, _ = winreg.QueryValueEx(key, "PATH")
            
            # Agar allaqachon PATH'da bo'lsa
            if path.lower() in current_path.lower():
                print(f"✅ PATH allaqachon mavjud: {path}")
                return True
            
            # PATH'ga qo'shish
            new_path = current_path + ";" + path
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            print(f"✅ PATH'ga qo'shildi: {path}")
            return True
            
    except PermissionError:
        print("❌ Admin huquqlari kerak. User PATH'ga qo'shilmoqda...")
        return add_to_user_path(path)
    except Exception as e:
        print(f"❌ PATH'ga qo'shishda xato: {e}")
        return False


def add_to_user_path(path):
    """User PATH'ga qo'shish"""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment",
                           0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            
            try:
                current_path, _ = winreg.QueryValueEx(key, "PATH")
            except FileNotFoundError:
                current_path = ""
            
            if path.lower() in current_path.lower():
                print(f"✅ User PATH allaqachon mavjud: {path}")
                return True
            
            new_path = current_path + ";" + path if current_path else path
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            print(f"✅ User PATH'ga qo'shildi: {path}")
            return True
            
    except Exception as e:
        print(f"❌ User PATH'ga qo'shishda xato: {e}")
        return False


def setup_ffmpeg():
    """FFmpeg o'rnatish va sozlash"""
    print("🎵 FFmpeg Setup - Audio To Voice Bot")
    print("=" * 50)
    
    # OS tekshiruvi
    if not is_windows():
        print("❌ Bu skript faqat Windows uchun mo'ljallangan")
        return False
    
    # FFmpeg allaqachon o'rnatilganligini tekshirish
    if is_ffmpeg_installed():
        print("✅ FFmpeg allaqachon o'rnatilgan va ishlayapti!")
        return True
    
    print("📋 FFmpeg topilmadi. O'rnatish boshlanyapti...")
    
    # Winget mavjudligini tekshirish
    if not is_winget_available():
        print("❌ Winget topilmadi. Windows 10/11 da winget o'rnatilgan bo'lishi kerak.")
        print("💡 Winget o'rnatish uchun: https://aka.ms/getwinget")
        return False
    
    # FFmpeg o'rnatish
    if not install_ffmpeg_with_winget():
        print("❌ FFmpeg o'rnatib bo'lmadi")
        return False
    
    # FFmpeg path'ni topish
    ffmpeg_path = find_ffmpeg_path()
    if not ffmpeg_path:
        print("❌ FFmpeg o'rnatildi, lekin path topilmadi")
        return False
    
    print(f"📍 FFmpeg topildi: {ffmpeg_path}")
    
    # PATH'ga qo'shish
    if not add_to_system_path(ffmpeg_path):
        print("❌ PATH'ga qo'shib bo'lmadi")
        return False
    
    # Tekshirish
    print("\n🔄 FFmpeg tekshirilmoqda...")
    if is_ffmpeg_installed():
        print("✅ FFmpeg muvaffaqiyatli o'rnatildi va sozlandi!")
        print("ℹ️  Terminal'ni restart qiling yoki yangi terminal oching")
        return True
    else:
        print("⚠️  FFmpeg o'rnatildi, lekin PATH yangilanishi uchun terminal restart kerak")
        return True


if __name__ == "__main__":
    try:
        success = setup_ffmpeg()
        if success:
            print("\n🎉 Setup yakunlandi!")
            input("Enter tugmasini bosing...")
        else:
            print("\n❌ Setup muvaffaqiyatsiz")
            input("Enter tugmasini bosing...")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup bekor qilindi")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Kutilmagan xato: {e}")
        input("Enter tugmasini bosing...")
        sys.exit(1)
