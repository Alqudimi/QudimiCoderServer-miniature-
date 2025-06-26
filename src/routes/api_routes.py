import time
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from src.auth import require_api_key, admin_required
from src.model_manager import model_manager
from src.queue_manager import queue_manager
from src.code_services import code_services
from src.enhanced_services import enhanced_services
from src.project_services import project_services
from src.monitoring import system_monitor, performance_profiler
from src.auth import api_key_manager, security_manager

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# إنشاء Blueprint
api_bp = Blueprint('api', __name__)

# ديكوريتر لقياس الأداء
def measure_performance(endpoint_name):
    def decorator(f):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = f(*args, **kwargs)
                success = True
            except Exception as e:
                result = jsonify({"error": str(e)}), 500
                success = False
            
            end_time = time.time()
            duration = end_time - start_time
            
            # تسجيل الأداء
            performance_profiler.record_operation(endpoint_name, duration)
            system_monitor.record_request(endpoint_name, duration, success)
            
            return result
        
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

# ===== نقاط الخدمات الأساسية =====

@api_bp.route('/v1/completions', methods=['POST'])
@require_api_key
@measure_performance('completions')
def complete_code():
    """إكمال الكود تلقائياً"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "بيانات JSON مطلوبة"}), 400
        
        # معالجة متزامنة للطلبات البسيطة
        result = code_services.complete_code(data)
        
        return jsonify({
            "success": result["success"],
            "data": result,
            "timestamp": datetime.now().isoformat(),
            "processing_time": performance_profiler.get_operation_stats('completions').get('avg_time', 0)
        })
        
    except Exception as e:
        logger.error(f"خطأ في إكمال الكود: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/v1/explanations', methods=['POST'])
@require_api_key
@measure_performance('explanations')
def explain_code():
    """شرح الكود بلغة طبيعية"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "بيانات JSON مطلوبة"}), 400
        
        result = code_services.explain_code(data)
        
        return jsonify({
            "success": result["success"],
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"خطأ في شرح الكود: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/v1/conversions', methods=['POST'])
@require_api_key
@measure_performance('conversions')
def convert_language():
    """تحويل الكود بين اللغات"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "بيانات JSON مطلوبة"}), 400
        
        result = code_services.convert_language(data)
        
        return jsonify({
            "success": result["success"],
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"خطأ في تحويل اللغة: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/v1/refactors', methods=['POST'])
@require_api_key
@measure_performance('refactors')
def refactor_code():
    """إعادة هيكلة الكود"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "بيانات JSON مطلوبة"}), 400
        
        result = code_services.refactor_code(data)
        
        return jsonify({
            "success": result["success"],
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"خطأ في إعادة الهيكلة: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ===== الخدمات المحسنة =====

@api_bp.route('/v1/suggest_names', methods=['POST'])
@require_api_key
@measure_performance('suggest_names')
def suggest_names():
    """اقتراح أسماء متغيرات ودوال أفضل"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "بيانات JSON مطلوبة"}), 400
        
        result = enhanced_services.suggest_names(data)
        
        return jsonify({
            "success": result["success"],
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"خطأ في اقتراح الأسماء: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/v1/detect_errors', methods=['POST'])
@require_api_key
@measure_performance('detect_errors')
def detect_errors():
    """كشف أخطاء بناء الجملة والأخطاء الشائعة"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "بيانات JSON مطلوبة"}), 400
        
        result = enhanced_services.detect_errors(data)
        
        return jsonify({
            "success": result["success"],
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"خطأ في كشف الأخطاء: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/v1/format_code', methods=['POST'])
@require_api_key
@measure_performance('format_code')
def format_code():
    """تنسيق الكود تلقائياً"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "بيانات JSON مطلوبة"}), 400
        
        result = enhanced_services.format_code(data)
        
        return jsonify({
            "success": result["success"],
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"خطأ في تنسيق الكود: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/v1/generate_docs', methods=['POST'])
@require_api_key
@measure_performance('generate_docs')
def generate_docs():
    """إنشاء توثيق تلقائي"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "بيانات JSON مطلوبة"}), 400
        
        result = enhanced_services.generate_docs(data)
        
        return jsonify({
            "success": result["success"],
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"خطأ في توليد التوثيق: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/v1/explain_concept', methods=['POST'])
@require_api_key
@measure_performance('explain_concept')
def explain_concept():
    """شرح مفهوم برمجي"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "بيانات JSON مطلوبة"}), 400
        
        result = enhanced_services.explain_concept(data)
        
        return jsonify({
            "success": result["success"],
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"خطأ في شرح المفهوم: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/v1/simplify_code', methods=['POST'])
@require_api_key
@measure_performance('simplify_code')
def simplify_code():
    """تبسيط الكود المعقد"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "بيانات JSON مطلوبة"}), 400
        
        result = enhanced_services.simplify_code(data)
        
        return jsonify({
            "success": result["success"],
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"خطأ في تبسيط الكود: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ===== خدمات المشاريع =====

@api_bp.route('/v1/create_snippet', methods=['POST'])
@require_api_key
@measure_performance('create_snippet')
def create_snippet():
    """إنشاء مقطع كود جاهز للاستخدام"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "بيانات JSON مطلوبة"}), 400
        
        result = project_services.create_snippet(data)
        
        return jsonify({
            "success": result["success"],
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"خطأ في إنشاء المقطع: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/v1/find_patterns', methods=['POST'])
@require_api_key
@measure_performance('find_patterns')
def find_patterns():
    """اكتشاف الأنماط المتكررة في الكود"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "بيانات JSON مطلوبة"}), 400
        
        result = project_services.find_patterns(data)
        
        return jsonify({
            "success": result["success"],
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"خطأ في اكتشاف الأنماط: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/v1/generate_curl', methods=['POST'])
@require_api_key
@measure_performance('generate_curl')
def generate_curl():
    """تحويل كود Python لطلب HTTP إلى أمر cURL"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "بيانات JSON مطلوبة"}), 400
        
        result = project_services.generate_curl(data)
        
        return jsonify({
            "success": result["success"],
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"خطأ في توليد cURL: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/v1/json_to_model', methods=['POST'])
@require_api_key
@measure_performance('json_to_model')
def json_to_model():
    """تحويل JSON إلى نموذج كائن"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "بيانات JSON مطلوبة"}), 400
        
        result = project_services.json_to_model(data)
        
        return jsonify({
            "success": result["success"],
            "data": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"خطأ في تحويل JSON: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ===== إدارة الطابور =====

@api_bp.route('/v1/queue/status', methods=['GET'])
@require_api_key
@measure_performance('queue_status')
def get_queue_status():
    """الحصول على حالة الطابور"""
    try:
        task_id = request.args.get('task_id')
        
        if task_id:
            # حالة مهمة محددة
            task_status = queue_manager.get_task_status(task_id)
            if not task_status:
                return jsonify({"error": "المهمة غير موجودة"}), 404
            
            return jsonify({
                "success": True,
                "task": task_status,
                "timestamp": datetime.now().isoformat()
            })
        else:
            # حالة الطابور العامة
            queue_status = queue_manager.get_queue_status()
            return jsonify({
                "success": True,
                "queue": queue_status,
                "timestamp": datetime.now().isoformat()
            })
        
    except Exception as e:
        logger.error(f"خطأ في الحصول على حالة الطابور: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/v1/queue/cancel', methods=['POST'])
@require_api_key
@measure_performance('queue_cancel')
def cancel_task():
    """إلغاء مهمة في الطابور"""
    try:
        data = request.get_json()
        if not data or 'task_id' not in data:
            return jsonify({"error": "task_id مطلوب"}), 400
        
        task_id = data['task_id']
        cancelled = queue_manager.cancel_task(task_id)
        
        if cancelled:
            return jsonify({
                "success": True,
                "message": "تم إلغاء المهمة بنجاح",
                "task_id": task_id,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "success": False,
                "error": "لا يمكن إلغاء المهمة (غير موجودة أو قيد التنفيذ)",
                "task_id": task_id
            }), 400
        
    except Exception as e:
        logger.error(f"خطأ في إلغاء المهمة: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ===== نظام المراقبة =====

@api_bp.route('/v1/system/health', methods=['GET'])
@measure_performance('system_health')
def get_system_health():
    """الحصول على حالة النظام الصحية"""
    try:
        health_data = system_monitor.get_system_health()
        
        return jsonify({
            "success": True,
            "health": health_data,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"خطأ في الحصول على حالة النظام: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/v1/system/stats', methods=['GET'])
@require_api_key
@measure_performance('system_stats')
def get_system_stats():
    """الحصول على إحصائيات النظام"""
    try:
        stats_data = system_monitor.get_system_stats()
        
        return jsonify({
            "success": True,
            "stats": stats_data,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"خطأ في الحصول على الإحصائيات: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/v1/system/performance', methods=['GET'])
@require_api_key
@measure_performance('system_performance')
def get_performance_stats():
    """الحصول على إحصائيات الأداء"""
    try:
        performance_data = performance_profiler.get_all_stats()
        
        return jsonify({
            "success": True,
            "performance": performance_data,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"خطأ في الحصول على إحصائيات الأداء: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ===== إدارة API Keys (للإدارة فقط) =====

@api_bp.route('/v1/admin/api_keys', methods=['GET'])
@require_api_key
@admin_required
@measure_performance('admin_api_keys')
def get_api_keys():
    """الحصول على قائمة مفاتيح API"""
    try:
        keys_stats = api_key_manager.get_all_keys_stats()
        
        return jsonify({
            "success": True,
            "api_keys": keys_stats,
            "total_keys": len(keys_stats),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"خطأ في الحصول على مفاتيح API: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/v1/admin/security', methods=['GET'])
@require_api_key
@admin_required
@measure_performance('admin_security')
def get_security_stats():
    """الحصول على إحصائيات الأمان"""
    try:
        security_data = security_manager.get_security_stats()
        
        return jsonify({
            "success": True,
            "security": security_data,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"خطأ في الحصول على إحصائيات الأمان: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ===== نقاط المساعدة =====

@api_bp.route('/v1/info', methods=['GET'])
def get_api_info():
    """معلومات عن API"""
    return jsonify({
        "name": "StarCoder API Server",
        "version": "1.0.0",
        "description": "خادم API متكامل للبرمجة باستخدام نموذج StarCoderBase-350M",
        "model": "bigcode/starcoderbase-350m (4-bit quantized)",
        "supported_languages": [
            "python", "javascript", "java", "cpp", "c", "csharp", 
            "php", "ruby", "go", "rust", "typescript", "html", 
            "css", "sql", "bash"
        ],
        "endpoints": {
            "core_services": [
                "/v1/completions",
                "/v1/explanations", 
                "/v1/conversions",
                "/v1/refactors"
            ],
            "enhanced_services": [
                "/v1/suggest_names",
                "/v1/detect_errors",
                "/v1/format_code",
                "/v1/generate_docs",
                "/v1/explain_concept",
                "/v1/simplify_code"
            ],
            "project_services": [
                "/v1/create_snippet",
                "/v1/find_patterns",
                "/v1/generate_curl",
                "/v1/json_to_model"
            ],
            "system": [
                "/v1/system/health",
                "/v1/system/stats",
                "/v1/queue/status"
            ]
        },
        "authentication": "API Key required (X-API-Key header)",
        "rate_limits": "Varies by API key",
        "timestamp": datetime.now().isoformat()
    })

@api_bp.route('/v1/model/status', methods=['GET'])
@require_api_key
@measure_performance('model_status')
def get_model_status():
    """حالة النموذج"""
    try:
        model_status = model_manager.get_model_status()
        
        return jsonify({
            "success": True,
            "model": model_status,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"خطأ في الحصول على حالة النموذج: {str(e)}")
        return jsonify({"error": str(e)}), 500

# معالج الأخطاء
@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "النقطة غير موجودة",
        "message": "تحقق من صحة URL والطريقة المستخدمة",
        "available_endpoints": "/v1/info"
    }), 404

@api_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "error": "الطريقة غير مسموحة",
        "message": "تحقق من الطريقة المستخدمة (GET/POST)"
    }), 405

@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "خطأ داخلي في الخادم",
        "message": "يرجى المحاولة لاحقاً أو التواصل مع الدعم"
    }), 500

