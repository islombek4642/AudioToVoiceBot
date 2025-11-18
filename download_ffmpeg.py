#!/usr/bin/env python3
"""
FFmpeg avtomatik yuklab olish va o'rnatish skripti
Loyiha papkasiga FFmpeg binary fayllarini yuklab oladi
"""

import os
import sys
import urllib.request
import zipfile
import shutil
from pathlib import Path


def download_file(url, filename):
    """Faylni yuklab olish"""
    print(f"📥 Yuklab olinmoqda: {filename}")
    try:
        def progress_hook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, (downloaded * 100) // total_size)
                print(f"\r📊 Jarayon: {percent}% ({downloaded // 1024 // 1024} MB / {total_size // 1024 // 1024} MB)", end='')
        
        urllib.request.urlretrieve(url, filename, progress_hook)
        print()  # Yangi qator
        return True
    except Exception as e:
        print(f"\n❌ Yuklab olishda xato: {e}")
        return False


def extract_ffmpeg(zip_path, extract_to):
    """FFmpeg zip faylini ochish"""
    print("📂 Zip fayl ochilmoqda...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Faqat bin papkasidagi exe fayllarni chiqarish
            for file_info in zip_ref.filelist:
                if file_info.filename.endswith(('.exe',)) and '/bin/' in file_info.filename:
                    # Fayl nomini olish (path'siz)
                    filename = os.path.basename(file_info.filename)
                    
                    # Faylni ochish va yozish
                    with zip_ref.open(file_info) as source:
                        target_path = os.path.join(extract_to, filename)
                        with open(target_path, 'wb') as target:
                            shutil.copyfileobj(source, target)
                    
                    print(f"✅ Chiqarildi: {filename}")
        
        return True
    except Exception as e:
        print(f"❌ Zip ochishda xato: {e}")
        return False


def verify_ffmpeg(ffmpeg_dir):
    """FFmpeg fayllarini tekshirish"""
    required_files = ['ffmpeg.exe', 'ffprobe.exe', 'ffplay.exe']
    missing_files = []
    
    for file in required_files:
        file_path = os.path.join(ffmpeg_dir, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Quyidagi fayllar topilmadi: {', '.join(missing_files)}")
        return False
    
    print("✅ Barcha FFmpeg fayllar mavjud!")
    return True


def download_and_setup_ffmpeg():
    """FFmpeg yuklab olish va o'rnatish"""
    print("🎵 FFmpeg Yuklab Olish - Audio To Voice Bot")
    print("=" * 60)
    
    # Papkalarni yaratish
    ffmpeg_dir = Path("ffmpeg")
    ffmpeg_dir.mkdir(exist_ok=True)
    
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    # FFmpeg allaqachon mavjudligini tekshirish
    if verify_ffmpeg(ffmpeg_dir):
        print("✅ FFmpeg allaqachon o'rnatilgan!")
        return True
    
    # Yuklab olish URL'i
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    zip_filename = temp_dir / "ffmpeg.zip"
    
    print("📡 FFmpeg yuklab olinmoqda...")
    print(f"🔗 URL: {ffmpeg_url}")
    
    # Yuklab olish
    if not download_file(ffmpeg_url, zip_filename):
        return False
    
    print("✅ Yuklab olish yakunlandi!")
    
    # Zip faylini ochish
    if not extract_ffmpeg(zip_filename, ffmpeg_dir):
        return False
    
    # Temp faylni o'chirish
    try:
        os.remove(zip_filename)
        print("🗑️  Temp fayl o'chirildi")
    except:
        pass
    
    # Tekshirish
    if verify_ffmpeg(ffmpeg_dir):
        print("\n🎉 FFmpeg muvaffaqiyatli yuklab olindi va o'rnatildi!")
        print(f"📁 Joylashgan: {ffmpeg_dir.absolute()}")
        return True
    else:
        return False


if __name__ == "__main__":
    try:
        success = download_and_setup_ffmpeg()
        if success:
            print("\n✅ Setup yakunlandi!")
        else:
            print("\n❌ Setup muvaffaqiyatsiz")
            sys.exit(1)
        
        input("\nEnter tugmasini bosing...")
    except KeyboardInterrupt:
        print("\n\n⏹️  Yuklab olish bekor qilindi")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Kutilmagan xato: {e}")
        input("Enter tugmasini bosing...")
        sys.exit(1)
