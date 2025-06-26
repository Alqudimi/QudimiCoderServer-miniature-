import os
import sys
import logging
import threading
import atexit
from datetime import datetime

# إضافة مسار المشروع
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.routes.api_routes import api_bp
from src.model_manager import model_manager
from src.queue_manager import queue_manager
from src.monitoring import system_monitor
from src.auth import api_key_manager

# إعداد نظام السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('starcoder_api.log')
    ]
)
logger = logging.getLogger(__name__)

def create_app():
    """إنشاء تطبيق Flask"""
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # إعدادات التطبيق
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'starcoder-api-secret-key-2024')
    app.config['JSON_AS_ASCII'] = False  # دعم النصوص العربية
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    # تمكين CORS للسماح بالطلبات من جميع المصادر
    CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # تسجيل Blueprint
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app

def initialize_services():
    """تهيئة الخدمات"""
    logger.info("بدء تهيئة الخدمات...")
    
    try:
        # بدء مدير الطابور
        queue_manager.start_worker()
        logger.info("تم بدء مدير الطابور")
        
        # تحميل النموذج في خيط منفصل لتجنب حظر التطبيق
        def load_model():
            try:
                logger.info("بدء تحميل النموذج...")
                success = model_manager.load_model()
                if success:
                    logger.info("تم تحميل النموذج بنجاح")
                else:
                    logger.error("فشل في تحميل النموذج")
            except Exception as e:
                logger.error(f"خطأ في تحميل النموذج: {str(e)}")
        
        model_thread = threading.Thread(target=load_model, daemon=True)
        model_thread.start()
        
        logger.info("تم بدء تهيئة الخدمات")
        
    except Exception as e:
        logger.error(f"خطأ في تهيئة الخدمات: {str(e)}")

def cleanup_services():
    """تنظيف الخدمات عند الإغلاق"""
    logger.info("بدء تنظيف الخدمات...")
    
    try:
        # إيقاف مدير الطابور
        queue_manager.stop_worker()
        logger.info("تم إيقاف مدير الطابور")
        
        # تنظيف النموذج
        model_manager.cleanup_model()
        logger.info("تم تنظيف النموذج")
        
        # تنظيف البيانات القديمة
        system_monitor.cleanup_old_data()
        logger.info("تم تنظيف بيانات المراقبة")
        
        logger.info("تم تنظيف جميع الخدمات")
        
    except Exception as e:
        logger.error(f"خطأ في تنظيف الخدمات: {str(e)}")

# إنشاء التطبيق
app = create_app()

# إضافة طرق إضافية للتطبيق الرئيسي
@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return jsonify({
        "message": "مرحباً بك في StarCoder API Server",
        "status": "running",
        "version": "1.0.0",
        "model": "StarCoderBase-350M (4-bit quantized)",
        "endpoints": {
            "api_info": "/api/v1/info",
            "system_health": "/api/v1/system/health",
            "documentation": "/docs"
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/docs')
def documentation():
    """توثيق API"""
    return jsonify({
        "title": "StarCoder API Documentation",
        "description": "خادم API متكامل للبرمجة باستخدام الذكاء الاصطناعي",
        "version": "1.0.0",
        "base_url": "/api/v1",
        "authentication": {
            "type": "API Key",
            "header": "X-API-Key",
            "description": "مطلوب مفتاح API صحيح لجميع الطلبات"
        },
        "endpoints": {
            "core_services": {
                "completions": {
                    "method": "POST",
                    "url": "/api/v1/completions",
                    "description": "إكمال الكود تلقائياً",
                    "parameters": {
                        "code": "الكود المراد إكماله",
                        "lang": "لغة البرمجة",
                        "max_tokens": "عدد الرموز الأقصى (اختياري)",
                        "temperature": "درجة الإبداع (اختياري)"
                    }
                },
                "explanations": {
                    "method": "POST",
                    "url": "/api/v1/explanations",
                    "description": "شرح الكود بلغة طبيعية",
                    "parameters": {
                        "code": "الكود المراد شرحه",
                        "lang": "لغة البرمجة",
                        "detail_level": "مستوى التفصيل (basic/medium/detailed)"
                    }
                },
                "conversions": {
                    "method": "POST",
                    "url": "/api/v1/conversions",
                    "description": "تحويل الكود بين اللغات",
                    "parameters": {
                        "code": "الكود المراد تحويله",
                        "from": "اللغة المصدر",
                        "to": "اللغة الهدف"
                    }
                },
                "refactors": {
                    "method": "POST",
                    "url": "/api/v1/refactors",
                    "description": "إعادة هيكلة الكود",
                    "parameters": {
                        "code": "الكود المراد إعادة هيكلته",
                        "lang": "لغة البرمجة",
                        "type": "نوع إعادة الهيكلة (general/performance/readability)"
                    }
                }
            },
            "enhanced_services": {
                "suggest_names": {
                    "method": "POST",
                    "url": "/api/v1/suggest_names",
                    "description": "اقتراح أسماء أفضل للمتغيرات والدوال"
                },
                "detect_errors": {
                    "method": "POST",
                    "url": "/api/v1/detect_errors",
                    "description": "كشف الأخطاء في الكود"
                },
                "format_code": {
                    "method": "POST",
                    "url": "/api/v1/format_code",
                    "description": "تنسيق الكود تلقائياً"
                },
                "generate_docs": {
                    "method": "POST",
                    "url": "/api/v1/generate_docs",
                    "description": "إنشاء توثيق تلقائي"
                }
            },
            "system": {
                "health": {
                    "method": "GET",
                    "url": "/api/v1/system/health",
                    "description": "حالة النظام الصحية"
                },
                "stats": {
                    "method": "GET",
                    "url": "/api/v1/system/stats",
                    "description": "إحصائيات النظام"
                }
            }
        },
        "examples": {
            "completion": {
                "request": {
                    "code": "def fibonacci(n):",
                    "lang": "python",
                    "max_tokens": 100
                },
                "response": {
                    "success": True,
                    "data": {
                        "completion": "    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"
                    }
                }
            }
        },
        "rate_limits": {
            "default": "10 requests per minute",
            "premium": "100 requests per minute"
        },
        "supported_languages": [
            "python", "javascript", "java", "cpp", "c", "csharp",
            "php", "ruby", "go", "rust", "typescript", "html",
            "css", "sql", "bash"
        ]
    })

@app.route('/health')
def health_check():
    """فحص صحة التطبيق (للاستخدام مع Render.com)"""
    try:
        # فحص حالة النموذج
        model_status = model_manager.get_model_status()
        
        # فحص حالة الطابور
        queue_status = queue_manager.get_queue_status()
        
        # فحص حالة النظام
        system_health = system_monitor.get_system_health()
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "model": {
                    "status": "loaded" if model_status["loaded"] else "loading",
                    "memory_usage": f"{model_status['memory_usage_mb']:.1f}MB"
                },
                "queue": {
                    "status": "running",
                    "active_tasks": queue_status["active_tasks"],
                    "waiting_tasks": queue_status["waiting_tasks"]
                },
                "system": {
                    "status": system_health["status"],
                    "memory_usage": f"{system_health['memory']['usage_percent']:.1f}%",
                    "uptime": system_health["uptime_human"]
                }
            }
        }
        
        # تحديد الحالة العامة
        if (system_health["status"] == "critical" or 
            system_health["memory"]["usage_percent"] > 95):
            health_status["status"] = "unhealthy"
            return jsonify(health_status), 503
        elif system_health["status"] == "warning":
            health_status["status"] = "degraded"
        
        return jsonify(health_status), 200
        
    except Exception as e:
        logger.error(f"خطأ في فحص الصحة: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 503

@app.route('/<path:path>')
def serve_static(path):
    """خدمة الملفات الثابتة"""
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return jsonify({"error": "Static folder not configured"}), 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        # إرجاع معلومات API بدلاً من 404
        return jsonify({
            "message": "الصفحة غير موجودة",
            "api_info": "/api/v1/info",
            "documentation": "/docs",
            "health": "/health"
        }), 404

# معالجات الأخطاء العامة
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        "error": "الصفحة غير موجودة",
        "message": "تحقق من صحة الرابط",
        "available_endpoints": {
            "api": "/api/v1/info",
            "docs": "/docs",
            "health": "/health"
        }
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"خطأ داخلي: {str(error)}")
    return jsonify({
        "error": "خطأ داخلي في الخادم",
        "message": "يرجى المحاولة لاحقاً"
    }), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"خطأ غير متوقع: {str(e)}")
    return jsonify({
        "error": "خطأ غير متوقع",
        "message": "يرجى التواصل مع الدعم الفني"
    }), 500

if __name__ == '__main__':
    # تسجيل دالة التنظيف عند الإغلاق
    atexit.register(cleanup_services)
    
    # تهيئة الخدمات
    initialize_services()
    
    # معلومات البدء
    logger.info("=" * 50)
    logger.info("StarCoder API Server")
    logger.info("Version: 1.0.0")
    logger.info("Model: StarCoderBase-350M (4-bit quantized)")
    logger.info("=" * 50)
    
    # الحصول على المنفذ من متغير البيئة (Render.com يستخدم PORT)
    port = int(os.getenv('PORT', 5000))
    host = '0.0.0.0'  # ضروري للنشر على Render.com
    
    logger.info(f"بدء الخادم على {host}:{port}")
    
    # تشغيل التطبيق
    app.run(
        host=host,
        port=port,
        debug=os.getenv('FLASK_ENV') == 'development',
        threaded=True  # تمكين المعالجة المتوازية
    )

