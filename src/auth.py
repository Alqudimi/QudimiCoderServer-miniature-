import os
import time
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from threading import Lock
from collections import defaultdict
from functools import wraps
from flask import request, jsonify

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateLimiter:
    """نظام تحديد معدل الطلبات"""
    
    def __init__(self):
        self.requests = defaultdict(list)  # {api_key: [timestamps]}
        self.lock = Lock()
        self.cleanup_interval = 300  # تنظيف كل 5 دقائق
        self.last_cleanup = time.time()
    
    def is_allowed(self, api_key: str, limit: int, window_minutes: int = 1) -> tuple[bool, Dict[str, Any]]:
        """التحقق من السماح بالطلب"""
        current_time = time.time()
        window_start = current_time - (window_minutes * 60)
        
        with self.lock:
            # تنظيف دوري
            if current_time - self.last_cleanup > self.cleanup_interval:
                self._cleanup_old_requests()
                self.last_cleanup = current_time
            
            # تنظيف الطلبات القديمة لهذا المفتاح
            self.requests[api_key] = [
                req_time for req_time in self.requests[api_key]
                if req_time > window_start
            ]
            
            # عدد الطلبات الحالية
            current_requests = len(self.requests[api_key])
            
            # التحقق من الحد
            if current_requests >= limit:
                return False, {
                    "allowed": False,
                    "current_requests": current_requests,
                    "limit": limit,
                    "window_minutes": window_minutes,
                    "reset_time": window_start + (window_minutes * 60),
                    "retry_after": int((self.requests[api_key][0] + (window_minutes * 60)) - current_time)
                }
            
            # إضافة الطلب الحالي
            self.requests[api_key].append(current_time)
            
            return True, {
                "allowed": True,
                "current_requests": current_requests + 1,
                "limit": limit,
                "window_minutes": window_minutes,
                "remaining": limit - current_requests - 1
            }
    
    def _cleanup_old_requests(self):
        """تنظيف الطلبات القديمة"""
        current_time = time.time()
        cutoff_time = current_time - 3600  # ساعة واحدة
        
        for api_key in list(self.requests.keys()):
            self.requests[api_key] = [
                req_time for req_time in self.requests[api_key]
                if req_time > cutoff_time
            ]
            
            # حذف المفاتيح الفارغة
            if not self.requests[api_key]:
                del self.requests[api_key]

class APIKeyManager:
    """مدير مفاتيح API"""
    
    def __init__(self):
        self.api_keys = {}
        self.load_api_keys()
        self.rate_limiter = RateLimiter()
        self.lock = Lock()
    
    def load_api_keys(self):
        """تحميل مفاتيح API من متغيرات البيئة"""
        # تحميل من متغير البيئة
        api_keys_env = os.getenv('API_KEYS', '')
        
        if api_keys_env:
            try:
                # تنسيق: key1:user1:10,key2:user2:5
                for key_info in api_keys_env.split(','):
                    parts = key_info.strip().split(':')
                    if len(parts) >= 3:
                        key, user, rate_limit = parts[0], parts[1], int(parts[2])
                        self.api_keys[key] = {
                            'user': user,
                            'rate_limit': rate_limit,
                            'created_at': datetime.now(),
                            'last_used': None,
                            'total_requests': 0,
                            'allowed_endpoints': ['*']  # جميع النقاط
                        }
            except Exception as e:
                logger.error(f"خطأ في تحميل مفاتيح API: {str(e)}")
        
        # إضافة مفتاح افتراضي للتطوير
        if not self.api_keys:
            default_key = "dev-key-12345"
            self.api_keys[default_key] = {
                'user': 'developer',
                'rate_limit': 100,
                'created_at': datetime.now(),
                'last_used': None,
                'total_requests': 0,
                'allowed_endpoints': ['*']
            }
            logger.info(f"تم إنشاء مفتاح تطوير افتراضي: {default_key}")
    
    def validate_api_key(self, api_key: str) -> tuple[bool, Dict[str, Any]]:
        """التحقق من صحة مفتاح API"""
        if not api_key:
            return False, {"error": "مفتاح API مطلوب"}
        
        with self.lock:
            key_info = self.api_keys.get(api_key)
            
            if not key_info:
                return False, {"error": "مفتاح API غير صحيح"}
            
            # التحقق من معدل الطلبات
            allowed, rate_info = self.rate_limiter.is_allowed(
                api_key, 
                key_info['rate_limit']
            )
            
            if not allowed:
                return False, {
                    "error": "تم تجاوز حد الطلبات",
                    "rate_limit_info": rate_info
                }
            
            # تحديث إحصائيات الاستخدام
            key_info['last_used'] = datetime.now()
            key_info['total_requests'] += 1
            
            return True, {
                "valid": True,
                "user": key_info['user'],
                "rate_limit_info": rate_info,
                "allowed_endpoints": key_info['allowed_endpoints']
            }
    
    def check_endpoint_permission(self, api_key: str, endpoint: str) -> bool:
        """التحقق من صلاحية الوصول للنقطة"""
        key_info = self.api_keys.get(api_key)
        if not key_info:
            return False
        
        allowed_endpoints = key_info.get('allowed_endpoints', [])
        
        # إذا كان '*' موجود، فالوصول مسموح لجميع النقاط
        if '*' in allowed_endpoints:
            return True
        
        # التحقق من النقطة المحددة
        return endpoint in allowed_endpoints
    
    def get_api_key_stats(self, api_key: str) -> Optional[Dict[str, Any]]:
        """الحصول على إحصائيات مفتاح API"""
        key_info = self.api_keys.get(api_key)
        if not key_info:
            return None
        
        return {
            "api_key": api_key[:8] + "...",  # إخفاء جزء من المفتاح
            "user": key_info['user'],
            "rate_limit": key_info['rate_limit'],
            "total_requests": key_info['total_requests'],
            "created_at": key_info['created_at'].isoformat(),
            "last_used": key_info['last_used'].isoformat() if key_info['last_used'] else None,
            "allowed_endpoints": key_info['allowed_endpoints']
        }
    
    def get_all_keys_stats(self) -> List[Dict[str, Any]]:
        """الحصول على إحصائيات جميع المفاتيح"""
        stats = []
        for api_key in self.api_keys:
            key_stats = self.get_api_key_stats(api_key)
            if key_stats:
                stats.append(key_stats)
        return stats
    
    def create_api_key(self, user: str, rate_limit: int = 10, endpoints: List[str] = None) -> str:
        """إنشاء مفتاح API جديد"""
        if endpoints is None:
            endpoints = ['*']
        
        # توليد مفتاح فريد
        timestamp = str(int(time.time()))
        hash_input = f"{user}:{timestamp}:{rate_limit}"
        api_key = hashlib.sha256(hash_input.encode()).hexdigest()[:32]
        
        with self.lock:
            self.api_keys[api_key] = {
                'user': user,
                'rate_limit': rate_limit,
                'created_at': datetime.now(),
                'last_used': None,
                'total_requests': 0,
                'allowed_endpoints': endpoints
            }
        
        logger.info(f"تم إنشاء مفتاح API جديد للمستخدم: {user}")
        return api_key
    
    def revoke_api_key(self, api_key: str) -> bool:
        """إلغاء مفتاح API"""
        with self.lock:
            if api_key in self.api_keys:
                user = self.api_keys[api_key]['user']
                del self.api_keys[api_key]
                logger.info(f"تم إلغاء مفتاح API للمستخدم: {user}")
                return True
            return False

class SecurityManager:
    """مدير الأمان"""
    
    def __init__(self):
        self.blocked_ips = set()
        self.suspicious_activity = defaultdict(int)
        self.lock = Lock()
        
        # حدود الأمان
        self.max_requests_per_ip = 1000  # في الساعة
        self.max_failed_attempts = 10
        self.block_duration_hours = 24
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """التحقق من حظر IP"""
        return ip_address in self.blocked_ips
    
    def record_failed_attempt(self, ip_address: str, reason: str = "invalid_api_key"):
        """تسجيل محاولة فاشلة"""
        with self.lock:
            self.suspicious_activity[f"{ip_address}:{reason}"] += 1
            
            # حظر IP إذا تجاوز الحد
            total_failures = sum(
                count for key, count in self.suspicious_activity.items()
                if key.startswith(ip_address)
            )
            
            if total_failures >= self.max_failed_attempts:
                self.blocked_ips.add(ip_address)
                logger.warning(f"تم حظر IP: {ip_address} بسبب النشاط المشبوه")
    
    def unblock_ip(self, ip_address: str):
        """إلغاء حظر IP"""
        with self.lock:
            self.blocked_ips.discard(ip_address)
            # مسح السجلات المشبوهة
            keys_to_remove = [
                key for key in self.suspicious_activity.keys()
                if key.startswith(ip_address)
            ]
            for key in keys_to_remove:
                del self.suspicious_activity[key]
    
    def get_security_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات الأمان"""
        with self.lock:
            return {
                "blocked_ips": list(self.blocked_ips),
                "blocked_count": len(self.blocked_ips),
                "suspicious_activity": dict(self.suspicious_activity),
                "total_suspicious_events": sum(self.suspicious_activity.values())
            }

# إنشاء مثيلات عامة
api_key_manager = APIKeyManager()
security_manager = SecurityManager()

def require_api_key(f):
    """ديكوريتر للتحقق من مفتاح API"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # الحصول على IP العميل
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        
        # التحقق من حظر IP
        if security_manager.is_ip_blocked(client_ip):
            return jsonify({
                "error": "IP محظور بسبب النشاط المشبوه",
                "blocked": True
            }), 403
        
        # الحصول على مفتاح API
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not api_key:
            security_manager.record_failed_attempt(client_ip, "missing_api_key")
            return jsonify({
                "error": "مفتاح API مطلوب",
                "hint": "أضف X-API-Key في الرأس أو api_key في المعاملات"
            }), 401
        
        # التحقق من صحة المفتاح
        valid, validation_info = api_key_manager.validate_api_key(api_key)
        
        if not valid:
            security_manager.record_failed_attempt(client_ip, "invalid_api_key")
            return jsonify(validation_info), 401
        
        # التحقق من صلاحية النقطة
        endpoint = request.endpoint or request.path
        if not api_key_manager.check_endpoint_permission(api_key, endpoint):
            return jsonify({
                "error": "غير مصرح بالوصول لهذه النقطة",
                "endpoint": endpoint
            }), 403
        
        # إضافة معلومات المصادقة للطلب
        request.api_key = api_key
        request.user = validation_info['user']
        request.rate_limit_info = validation_info['rate_limit_info']
        
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """ديكوريتر للتحقق من صلاحيات الإدارة"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'user') or request.user != 'admin':
            return jsonify({
                "error": "صلاحيات إدارة مطلوبة"
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

