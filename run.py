#!/usr/bin/env python3
"""
تشغيل سريع لـ StarCoder API Server
"""

import os
import sys
import subprocess
import platform

def check_requirements():
    """التحقق من المتطلبات"""
    print("🔍 التحقق من المتطلبات...")
    
    # التحقق من Python
    if sys.version_info < (3, 9):
        print("❌ يتطلب Python 3.9 أو أحدث")
        return False
    
    # التحقق من ملف requirements.txt
    if not os.path.exists("requirements.txt"):
        print("❌ ملف requirements.txt غير موجود")
        return False
    
    # التحقق من المجلد src
    if not os.path.exists("src"):
        print("❌ مجلد src غير موجود")
        return False
    
    print("✅ جميع المتطلبات متوفرة")
    return True

def install_dependencies():
    """تثبيت المتطلبات"""
    print("📦 تثبيت المتطلبات...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ تم تثبيت المتطلبات بنجاح")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ فشل في تثبيت المتطلبات: {e}")
        return False

def setup_environment():
    """إعداد البيئة"""
    print("⚙️ إعداد البيئة...")
    
    # إنشاء المجلدات المطلوبة
    directories = ["logs", "data", "cache"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 تم إنشاء مجلد {directory}")
    
    # إنشاء ملف .env إذا لم يكن موجوداً
    if not os.path.exists(".env"):
        env_content = """# متغيرات البيئة
PORT=5000
FLASK_ENV=development
API_KEYS=dev-key-12345:developer:100,test-key:tester:10
SECRET_KEY=starcoder-secret-key-2024
MAX_MEMORY_MB=450
MAX_CONCURRENT_JOBS=3
"""
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        print("📄 تم إنشاء ملف .env")
    
    print("✅ تم إعداد البيئة")

def run_server():
    """تشغيل الخادم"""
    print("🚀 بدء تشغيل الخادم...")
    print("=" * 50)
    print("StarCoder API Server")
    print("الرابط: http://localhost:5000")
    print("مفتاح API للاختبار: dev-key-12345")
    print("=" * 50)
    print("اضغط Ctrl+C لإيقاف الخادم")
    print()
    
    try:
        # تشغيل الخادم
        subprocess.run([sys.executable, "src/main.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف الخادم")
    except subprocess.CalledProcessError as e:
        print(f"❌ خطأ في تشغيل الخادم: {e}")

def main():
    """الدالة الرئيسية"""
    print("🎯 StarCoder API Server - تشغيل سريع")
    print("=" * 50)
    
    # التحقق من المتطلبات
    if not check_requirements():
        print("\n💡 نصائح:")
        print("1. تأكد من تثبيت Python 3.9+")
        print("2. تأكد من وجود جميع ملفات المشروع")
        sys.exit(1)
    
    # تثبيت المتطلبات
    print("\n📦 هل تريد تثبيت/تحديث المتطلبات؟ (y/n): ", end="")
    if input().lower() in ['y', 'yes', 'نعم', '']:
        if not install_dependencies():
            sys.exit(1)
    
    # إعداد البيئة
    setup_environment()
    
    # تشغيل الخادم
    print("\n🚀 هل تريد تشغيل الخادم الآن؟ (y/n): ", end="")
    if input().lower() in ['y', 'yes', 'نعم', '']:
        run_server()
    else:
        print("\n✅ الإعداد مكتمل!")
        print("لتشغيل الخادم لاحقاً:")
        print("python src/main.py")

if __name__ == "__main__":
    main()

