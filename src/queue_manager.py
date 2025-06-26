import uuid
import time
import asyncio
import threading
import logging
from collections import deque
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, Optional, Callable

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """حالات المهام"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Task:
    """فئة المهمة"""
    def __init__(self, task_id: str, endpoint: str, data: Dict[str, Any], callback: Callable):
        self.task_id = task_id
        self.endpoint = endpoint
        self.data = data
        self.callback = callback
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.error = None
        self.priority = 1  # أولوية افتراضية

class QueueManager:
    """مدير الطابور الذكي"""
    
    def __init__(self, max_concurrent_tasks=3, max_queue_size=50):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.max_queue_size = max_queue_size
        self.active_tasks = 0
        self.waiting_queue = deque()
        self.tasks: Dict[str, Task] = {}
        self.queue_lock = threading.Lock()
        self.worker_thread = None
        self.running = False
        
        # إحصائيات
        self.total_processed = 0
        self.total_failed = 0
        self.average_processing_time = 0
        
    def start_worker(self):
        """بدء خيط العامل لمعالجة الطابور"""
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            logger.info("تم بدء خيط معالجة الطابور")
    
    def stop_worker(self):
        """إيقاف خيط العامل"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        logger.info("تم إيقاف خيط معالجة الطابور")
    
    def _worker_loop(self):
        """حلقة العامل الرئيسية"""
        while self.running:
            try:
                self._process_queue()
                time.sleep(0.1)  # فترة انتظار قصيرة
            except Exception as e:
                logger.error(f"خطأ في حلقة العامل: {str(e)}")
                time.sleep(1)
    
    def _process_queue(self):
        """معالجة الطابور"""
        with self.queue_lock:
            # التحقق من إمكانية معالجة مهام جديدة
            if self.active_tasks >= self.max_concurrent_tasks:
                return
            
            # البحث عن مهمة في الانتظار
            if not self.waiting_queue:
                return
            
            # أخذ المهمة التالية
            task = self.waiting_queue.popleft()
            self.active_tasks += 1
            task.status = TaskStatus.PROCESSING
            task.started_at = datetime.now()
        
        # معالجة المهمة في خيط منفصل
        processing_thread = threading.Thread(
            target=self._execute_task, 
            args=(task,), 
            daemon=True
        )
        processing_thread.start()
    
    def _execute_task(self, task: Task):
        """تنفيذ مهمة واحدة"""
        try:
            logger.info(f"بدء معالجة المهمة {task.task_id}")
            
            # تنفيذ المهمة
            result = task.callback(task.data)
            
            # تحديث حالة المهمة
            with self.queue_lock:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                task.result = result
                self.active_tasks -= 1
                self.total_processed += 1
                
                # حساب متوسط وقت المعالجة
                processing_time = (task.completed_at - task.started_at).total_seconds()
                self.average_processing_time = (
                    (self.average_processing_time * (self.total_processed - 1) + processing_time) 
                    / self.total_processed
                )
            
            logger.info(f"تمت معالجة المهمة {task.task_id} بنجاح")
            
        except Exception as e:
            logger.error(f"خطأ في معالجة المهمة {task.task_id}: {str(e)}")
            
            with self.queue_lock:
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now()
                task.error = str(e)
                self.active_tasks -= 1
                self.total_failed += 1
    
    def submit_task(self, endpoint: str, data: Dict[str, Any], callback: Callable) -> str:
        """إرسال مهمة جديدة"""
        # إنشاء معرف فريد للمهمة
        task_id = str(uuid.uuid4())
        
        with self.queue_lock:
            # التحقق من حد الطابور
            if len(self.waiting_queue) >= self.max_queue_size:
                raise RuntimeError("الطابور ممتلئ، يرجى المحاولة لاحقاً")
            
            # إنشاء المهمة
            task = Task(task_id, endpoint, data, callback)
            self.tasks[task_id] = task
            
            # إضافة المهمة للطابور
            self.waiting_queue.append(task)
            
        logger.info(f"تم إرسال المهمة {task_id} إلى الطابور")
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """الحصول على حالة مهمة"""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        status_info = {
            "task_id": task.task_id,
            "status": task.status.value,
            "endpoint": task.endpoint,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        }
        
        if task.status == TaskStatus.COMPLETED:
            status_info["result"] = task.result
        elif task.status == TaskStatus.FAILED:
            status_info["error"] = task.error
        
        return status_info
    
    def cancel_task(self, task_id: str) -> bool:
        """إلغاء مهمة"""
        with self.queue_lock:
            task = self.tasks.get(task_id)
            if not task:
                return False
            
            if task.status == TaskStatus.PENDING:
                # إزالة من الطابور
                try:
                    self.waiting_queue.remove(task)
                    task.status = TaskStatus.CANCELLED
                    task.completed_at = datetime.now()
                    logger.info(f"تم إلغاء المهمة {task_id}")
                    return True
                except ValueError:
                    return False
            
            return False
    
    def get_queue_status(self) -> Dict[str, Any]:
        """الحصول على حالة الطابور"""
        with self.queue_lock:
            return {
                "active_tasks": self.active_tasks,
                "waiting_tasks": len(self.waiting_queue),
                "max_concurrent": self.max_concurrent_tasks,
                "max_queue_size": self.max_queue_size,
                "total_processed": self.total_processed,
                "total_failed": self.total_failed,
                "average_processing_time": round(self.average_processing_time, 2),
                "queue_utilization": len(self.waiting_queue) / self.max_queue_size * 100
            }
    
    def cleanup_old_tasks(self, max_age_hours=24):
        """تنظيف المهام القديمة"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        with self.queue_lock:
            old_task_ids = [
                task_id for task_id, task in self.tasks.items()
                if task.created_at < cutoff_time and task.status in [
                    TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED
                ]
            ]
            
            for task_id in old_task_ids:
                del self.tasks[task_id]
            
            if old_task_ids:
                logger.info(f"تم تنظيف {len(old_task_ids)} مهمة قديمة")

# إنشاء مثيل عام من مدير الطابور
queue_manager = QueueManager()

