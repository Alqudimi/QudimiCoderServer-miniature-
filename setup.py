#!/usr/bin/env python3
"""
إعداد سريع لـ StarCoder API Server
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """تشغيل أمر مع معالجة الأخطاء"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - تم بنجاح")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - فشل")
        print(f"الخطأ: {e.stderr}")
        return False

def check_python_version():
    """التحقق من إصدار Python"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - مدعوم")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - غير مدعوم")
        print("يرجى استخدام Python 3.9 أو أحدث")
        return False

def create_virtual_environment():
    """إنشاء بيئة افتراضية"""
    if os.path.exists("venv"):
        print("📁 البيئة الافتراضية موجودة بالفعل")
        return True
    
    return run_command("python -m venv venv", "إنشاء البيئة الافتراضية")

def activate_and_install():
    """تفعيل البيئة وتثبيت المتطلبات"""
    system = platform.system()
    
    if system == "Windows":
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    # تحديث pip
    if not run_command(f"{pip_cmd} install --upgrade pip", "تحديث pip"):
        return False
    
    # تثبيت المتطلبات
    if not run_command(f"{pip_cmd} install -r requirements.txt", "تثبيت المتطلبات"):
        return False
    
    return True

def create_env_file():
    """إنشاء ملف متغيرات البيئة"""
    env_content = """# متغيرات البيئة لـ StarCoder API Server
PORT=5000
FLASK_ENV=development
API_KEYS=dev-key-12345:developer:100,test-key:tester:10
SECRET_KEY=your-secret-key-here
MAX_MEMORY_MB=450
MAX_CONCURRENT_JOBS=3

# للنشر على Render.com
# PORT=10000
# FLASK_ENV=production
"""
    
    if not os.path.exists(".env"):
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        print("✅ تم إنشاء ملف .env")
    else:
        print("📁 ملف .env موجود بالفعل")

def create_directories():
    """إنشاء المجلدات المطلوبة"""
    directories = ["logs", "data", "cache"]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ تم إنشاء مجلد {directory}")
        else:
            print(f"📁 مجلد {directory} موجود بالفعل")

def main():
    """الدالة الرئيسية للإعداد"""
    print("🚀 إعداد StarCoder API Server")
    print("=" * 50)
    
    # التحقق من إصدار Python
    if not check_python_version():
        sys.exit(1)
    
    # إنشاء البيئة الافتراضية
    if not create_virtual_environment():
        sys.exit(1)
    
    # تثبيت المتطلبات
    if not activate_and_install():
        sys.exit(1)
    
    # إنشاء ملف البيئة
    create_env_file()
    
    # إنشاء المجلدات
    create_directories()
    
    print("\n" + "=" * 50)
    print("✅ تم الإعداد بنجاح!")
    print("\nخطوات التشغيل:")
    
    system = platform.system()
    if system == "Windows":
        print("1. venv\\Scripts\\activate")
    else:
        print("1. source venv/bin/activate")
    
    print("2. python src/main.py")
    print("3. افتح المتصفح على: http://localhost:5000")
    print("4. اختبر API: python test_api.py")
    
    print("\nمفتاح API الافتراضي: dev-key-12345")
    print("راجع README.md للمزيد من التفاصيل")

if __name__ == "__main__":
    main()

