import os
import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from threading import Lock
from collections import defaultdict, deque

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemMonitor:
    """نظام مراقبة الخادم والموارد"""
    
    def __init__(self, max_history_size=1000):
        self.max_history_size = max_history_size
        self.metrics_history = deque(maxlen=max_history_size)
        self.request_stats = defaultdict(int)
        self.error_stats = defaultdict(int)
        self.response_times = deque(maxlen=100)  # آخر 100 طلب
        self.start_time = datetime.now()
        self.lock = Lock()
        
        # حدود التحذير
        self.memory_warning_threshold = 400  # MB
        self.memory_critical_threshold = 480  # MB
        self.cpu_warning_threshold = 80  # %
        self.response_time_warning = 10  # seconds
        
    def get_system_health(self) -> Dict[str, Any]:
        """الحصول على حالة النظام الصحية"""
        try:
            # معلومات الذاكرة
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            # معلومات المعالج
            cpu_percent = process.cpu_percent()
            
            # معلومات القرص
            disk_usage = psutil.disk_usage('/')
            disk_free_gb = disk_usage.free / 1024 / 1024 / 1024
            
            # حالة الصحة العامة
            health_status = self._calculate_health_status(memory_mb, cpu_percent, disk_free_gb)
            
            # وقت التشغيل
            uptime = datetime.now() - self.start_time
            
            health_data = {
                "status": health_status,
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": int(uptime.total_seconds()),
                "uptime_human": str(uptime).split('.')[0],
                "memory": {
                    "used_mb": round(memory_mb, 2),
                    "limit_mb": 512,
                    "usage_percent": round((memory_mb / 512) * 100, 2),
                    "status": self._get_memory_status(memory_mb)
                },
                "cpu": {
                    "usage_percent": round(cpu_percent, 2),
                    "status": self._get_cpu_status(cpu_percent)
                },
                "disk": {
                    "free_gb": round(disk_free_gb, 2),
                    "total_gb": round(disk_usage.total / 1024 / 1024 / 1024, 2),
                    "usage_percent": round((disk_usage.used / disk_usage.total) * 100, 2)
                },
                "process": {
                    "pid": os.getpid(),
                    "threads": process.num_threads(),
                    "connections": len(process.connections()) if hasattr(process, 'connections') else 0
                }
            }
            
            # حفظ المقاييس في التاريخ
            with self.lock:
                self.metrics_history.append({
                    "timestamp": datetime.now(),
                    "memory_mb": memory_mb,
                    "cpu_percent": cpu_percent,
                    "disk_free_gb": disk_free_gb
                })
            
            return health_data
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على حالة النظام: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات النظام"""
        try:
            with self.lock:
                # إحصائيات الطلبات
                total_requests = sum(self.request_stats.values())
                total_errors = sum(self.error_stats.values())
                
                # متوسط وقت الاستجابة
                avg_response_time = (
                    sum(self.response_times) / len(self.response_times)
                    if self.response_times else 0
                )
                
                # إحصائيات الذاكرة من التاريخ
                memory_stats = self._calculate_memory_stats()
                
                # معدل الطلبات
                uptime_hours = (datetime.now() - self.start_time).total_seconds() / 3600
                requests_per_hour = total_requests / uptime_hours if uptime_hours > 0 else 0
                
                return {
                    "timestamp": datetime.now().isoformat(),
                    "uptime_hours": round(uptime_hours, 2),
                    "requests": {
                        "total": total_requests,
                        "by_endpoint": dict(self.request_stats),
                        "per_hour": round(requests_per_hour, 2),
                        "success_rate": round(
                            ((total_requests - total_errors) / total_requests * 100)
                            if total_requests > 0 else 100, 2
                        )
                    },
                    "errors": {
                        "total": total_errors,
                        "by_type": dict(self.error_stats),
                        "error_rate": round(
                            (total_errors / total_requests * 100)
                            if total_requests > 0 else 0, 2
                        )
                    },
                    "performance": {
                        "avg_response_time": round(avg_response_time, 3),
                        "min_response_time": round(min(self.response_times), 3) if self.response_times else 0,
                        "max_response_time": round(max(self.response_times), 3) if self.response_times else 0,
                        "recent_requests": len(self.response_times)
                    },
                    "memory": memory_stats,
                    "alerts": self._get_active_alerts()
                }
                
        except Exception as e:
            logger.error(f"خطأ في الحصول على الإحصائيات: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def record_request(self, endpoint: str, response_time: float, success: bool = True):
        """تسجيل طلب جديد"""
        with self.lock:
            self.request_stats[endpoint] += 1
            self.response_times.append(response_time)
            
            if not success:
                self.error_stats[endpoint] += 1
    
    def record_error(self, error_type: str, endpoint: str = "unknown"):
        """تسجيل خطأ"""
        with self.lock:
            self.error_stats[f"{error_type}:{endpoint}"] += 1
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """الحصول على التحذيرات النشطة"""
        alerts = []
        
        try:
            # فحص الذاكرة
            current_health = self.get_system_health()
            memory_mb = current_health.get("memory", {}).get("used_mb", 0)
            
            if memory_mb > self.memory_critical_threshold:
                alerts.append({
                    "type": "critical",
                    "category": "memory",
                    "message": f"استخدام الذاكرة حرج: {memory_mb:.1f}MB",
                    "timestamp": datetime.now().isoformat(),
                    "threshold": self.memory_critical_threshold
                })
            elif memory_mb > self.memory_warning_threshold:
                alerts.append({
                    "type": "warning",
                    "category": "memory",
                    "message": f"استخدام الذاكرة مرتفع: {memory_mb:.1f}MB",
                    "timestamp": datetime.now().isoformat(),
                    "threshold": self.memory_warning_threshold
                })
            
            # فحص وقت الاستجابة
            if self.response_times:
                recent_avg = sum(list(self.response_times)[-10:]) / min(10, len(self.response_times))
                if recent_avg > self.response_time_warning:
                    alerts.append({
                        "type": "warning",
                        "category": "performance",
                        "message": f"وقت الاستجابة بطيء: {recent_avg:.2f}s",
                        "timestamp": datetime.now().isoformat(),
                        "threshold": self.response_time_warning
                    })
            
            # فحص معدل الأخطاء
            total_requests = sum(self.request_stats.values())
            total_errors = sum(self.error_stats.values())
            
            if total_requests > 10:  # فقط إذا كان هناك طلبات كافية
                error_rate = (total_errors / total_requests) * 100
                if error_rate > 20:  # أكثر من 20% أخطاء
                    alerts.append({
                        "type": "warning",
                        "category": "errors",
                        "message": f"معدل أخطاء مرتفع: {error_rate:.1f}%",
                        "timestamp": datetime.now().isoformat(),
                        "threshold": 20
                    })
            
        except Exception as e:
            logger.error(f"خطأ في فحص التحذيرات: {str(e)}")
            alerts.append({
                "type": "error",
                "category": "system",
                "message": f"خطأ في نظام المراقبة: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts
    
    def cleanup_old_data(self, max_age_hours: int = 24):
        """تنظيف البيانات القديمة"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        with self.lock:
            # تنظيف تاريخ المقاييس
            while (self.metrics_history and 
                   self.metrics_history[0]["timestamp"] < cutoff_time):
                self.metrics_history.popleft()
            
            logger.info(f"تم تنظيف البيانات الأقدم من {max_age_hours} ساعة")
    
    # الدوال المساعدة
    def _calculate_health_status(self, memory_mb: float, cpu_percent: float, disk_free_gb: float) -> str:
        """حساب حالة الصحة العامة"""
        if memory_mb > self.memory_critical_threshold:
            return "critical"
        elif (memory_mb > self.memory_warning_threshold or 
              cpu_percent > self.cpu_warning_threshold or 
              disk_free_gb < 0.1):
            return "warning"
        else:
            return "healthy"
    
    def _get_memory_status(self, memory_mb: float) -> str:
        """تحديد حالة الذاكرة"""
        if memory_mb > self.memory_critical_threshold:
            return "critical"
        elif memory_mb > self.memory_warning_threshold:
            return "warning"
        else:
            return "normal"
    
    def _get_cpu_status(self, cpu_percent: float) -> str:
        """تحديد حالة المعالج"""
        if cpu_percent > self.cpu_warning_threshold:
            return "warning"
        else:
            return "normal"
    
    def _calculate_memory_stats(self) -> Dict[str, Any]:
        """حساب إحصائيات الذاكرة من التاريخ"""
        if not self.metrics_history:
            return {"avg_mb": 0, "min_mb": 0, "max_mb": 0, "trend": "stable"}
        
        memory_values = [m["memory_mb"] for m in self.metrics_history]
        
        avg_memory = sum(memory_values) / len(memory_values)
        min_memory = min(memory_values)
        max_memory = max(memory_values)
        
        # تحديد الاتجاه
        if len(memory_values) >= 10:
            recent_avg = sum(memory_values[-10:]) / 10
            older_avg = sum(memory_values[-20:-10]) / 10 if len(memory_values) >= 20 else avg_memory
            
            if recent_avg > older_avg * 1.1:
                trend = "increasing"
            elif recent_avg < older_avg * 0.9:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "avg_mb": round(avg_memory, 2),
            "min_mb": round(min_memory, 2),
            "max_mb": round(max_memory, 2),
            "trend": trend,
            "data_points": len(memory_values)
        }
    
    def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """الحصول على التحذيرات النشطة"""
        return self.get_alerts()

class PerformanceProfiler:
    """أداة قياس الأداء"""
    
    def __init__(self):
        self.operation_times = defaultdict(list)
        self.lock = Lock()
    
    def record_operation(self, operation_name: str, duration: float):
        """تسجيل وقت عملية"""
        with self.lock:
            self.operation_times[operation_name].append(duration)
            
            # الاحتفاظ بآخر 100 قياس فقط
            if len(self.operation_times[operation_name]) > 100:
                self.operation_times[operation_name] = self.operation_times[operation_name][-100:]
    
    def get_operation_stats(self, operation_name: str) -> Dict[str, Any]:
        """الحصول على إحصائيات عملية"""
        with self.lock:
            times = self.operation_times.get(operation_name, [])
            
            if not times:
                return {"error": "لا توجد بيانات لهذه العملية"}
            
            return {
                "operation": operation_name,
                "count": len(times),
                "avg_time": round(sum(times) / len(times), 4),
                "min_time": round(min(times), 4),
                "max_time": round(max(times), 4),
                "total_time": round(sum(times), 4)
            }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات جميع العمليات"""
        with self.lock:
            stats = {}
            for operation in self.operation_times:
                stats[operation] = self.get_operation_stats(operation)
            return stats

# إنشاء مثيلات عامة
system_monitor = SystemMonitor()
performance_profiler = PerformanceProfiler()

