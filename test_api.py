#!/usr/bin/env python3
"""
اختبار بسيط لـ StarCoder API Server
"""

import requests
import json
import time

# إعدادات الاختبار
BASE_URL = "http://localhost:5000/api/v1"
API_KEY = "dev-key-12345"  # المفتاح الافتراضي

def test_api_endpoint(endpoint, method="GET", data=None):
    """اختبار نقطة API"""
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        if method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=30)
        else:
            response = requests.get(url, headers=headers, timeout=30)
        
        print(f"\n{'='*50}")
        print(f"اختبار: {method} {endpoint}")
        print(f"الحالة: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"النجاح: ✅")
            if 'data' in result:
                print(f"البيانات: {json.dumps(result['data'], ensure_ascii=False, indent=2)}")
            else:
                print(f"الاستجابة: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"الفشل: ❌")
            print(f"الخطأ: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n{'='*50}")
        print(f"اختبار: {method} {endpoint}")
        print(f"خطأ في الاتصال: ❌")
        print(f"التفاصيل: {str(e)}")

def main():
    """تشغيل جميع الاختبارات"""
    print("🚀 بدء اختبار StarCoder API Server")
    print("=" * 60)
    
    # اختبار معلومات API
    test_api_endpoint("/info")
    
    # اختبار حالة النظام
    test_api_endpoint("/system/health")
    
    # اختبار حالة النموذج
    test_api_endpoint("/model/status")
    
    # اختبار إكمال الكود
    test_api_endpoint("/completions", "POST", {
        "code": "def hello_world():",
        "lang": "python",
        "max_tokens": 50
    })
    
    # اختبار شرح الكود
    test_api_endpoint("/explanations", "POST", {
        "code": "x = [i**2 for i in range(10)]",
        "lang": "python",
        "detail_level": "medium"
    })
    
    # اختبار تحويل اللغات
    test_api_endpoint("/conversions", "POST", {
        "code": "function add(a, b) { return a + b; }",
        "from": "javascript",
        "to": "python"
    })
    
    # اختبار كشف الأخطاء
    test_api_endpoint("/detect_errors", "POST", {
        "code": "for i in rang(5):\n    print(i)",
        "lang": "python"
    })
    
    # اختبار تنسيق الكود
    test_api_endpoint("/format_code", "POST", {
        "code": "x=5;y=10;z=x+y",
        "lang": "python"
    })
    
    # اختبار إنشاء مقطع كود
    test_api_endpoint("/create_snippet", "POST", {
        "task": "HTTP GET request",
        "lang": "python"
    })
    
    # اختبار حالة الطابور
    test_api_endpoint("/queue/status")
    
    print(f"\n{'='*60}")
    print("✅ انتهى الاختبار")

if __name__ == "__main__":
    main()

