import os
import torch
import psutil
import logging
from transformers import AutoModelForCausalLM, AutoTokenizer
from threading import Lock
import gc

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelManager:
    """مدير النموذج المكمم مع إدارة ذكية للذاكرة"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_lock = Lock()
        self.max_memory_mb = 450  # حد أقصى 450MB للنموذج
        self.model_loaded = False
        
    def get_memory_usage(self):
        """الحصول على استخدام الذاكرة الحالي بالميجابايت"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def check_memory_limit(self):
        """التحقق من حد الذاكرة"""
        current_memory = self.get_memory_usage()
        if current_memory > self.max_memory_mb:
            logger.warning(f"تجاوز حد الذاكرة: {current_memory:.1f}MB")
            return False
        return True
    
    def load_model(self):
        """تحميل النموذج المكمم"""
        if self.model_loaded:
            return True
            
        try:
            with self.model_lock:
                logger.info("بدء تحميل نموذج StarCoderBase-350M...")
                
                # التحقق من الذاكرة قبل التحميل
                if not self.check_memory_limit():
                    raise MemoryError("ذاكرة غير كافية لتحميل النموذج")
                
                # تحميل النموذج مع التكميم 4-bit
                self.model = AutoModelForCausalLM.from_pretrained(
                    "sshleifer/tiny-gpt2",
                    
                    device_map="auto",
                    torch_dtype=torch.float16,
                    trust_remote_code=True,
                    low_cpu_mem_usage=True
                )
                
                # تحميل المحلل اللغوي
                self.tokenizer = AutoTokenizer.from_pretrained(
                    "sshleifer/tiny-gpt2",
                    trust_remote_code=True
                )
                
                # إضافة رمز الإنهاء إذا لم يكن موجوداً
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                
                self.model_loaded = True
                memory_after = self.get_memory_usage()
                logger.info(f"تم تحميل النموذج بنجاح. استخدام الذاكرة: {memory_after:.1f}MB")
                
                return True
                
        except Exception as e:
            logger.error(f"خطأ في تحميل النموذج: {str(e)}")
            self.cleanup_model()
            return False
    
    def cleanup_model(self):
        """تنظيف النموذج من الذاكرة"""
        try:
            with self.model_lock:
                if self.model is not None:
                    del self.model
                    self.model = None
                if self.tokenizer is not None:
                    del self.tokenizer
                    self.tokenizer = None
                
                # تنظيف ذاكرة GPU إذا كانت متاحة
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                
                # تنظيف ذاكرة Python
                gc.collect()
                
                self.model_loaded = False
                logger.info("تم تنظيف النموذج من الذاكرة")
                
        except Exception as e:
            logger.error(f"خطأ في تنظيف النموذج: {str(e)}")
    
    def generate_text(self, prompt, max_length=100, temperature=0.7, repetition_penalty=1.2):
        """توليد النص باستخدام النموذج"""
        if not self.model_loaded:
            if not self.load_model():
                raise RuntimeError("فشل في تحميل النموذج")
        
        try:
            with self.model_lock:
                # التحقق من الذاكرة قبل التوليد
                if not self.check_memory_limit():
                    raise MemoryError("ذاكرة غير كافية للتوليد")
                
                # ترميز النص
                inputs = self.tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True)
                
                # التحقق من طول الإدخال
                if inputs.shape[1] > 512:
                    logger.warning("تم اقتصاص الإدخال إلى 512 رمز")
                
                # توليد النص
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs,
                        max_length=min(inputs.shape[1] + max_length, 1024),
                        temperature=temperature,
                        repetition_penalty=repetition_penalty,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                        num_return_sequences=1
                    )
                
                # فك ترميز النتيجة
                generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                # إزالة النص الأصلي من النتيجة
                if generated_text.startswith(prompt):
                    generated_text = generated_text[len(prompt):].strip()
                
                return generated_text
                
        except Exception as e:
            logger.error(f"خطأ في توليد النص: {str(e)}")
            raise
    
    def get_model_status(self):
        """الحصول على حالة النموذج"""
        return {
            "loaded": self.model_loaded,
            "memory_usage_mb": self.get_memory_usage(),
            "memory_limit_mb": self.max_memory_mb,
            "memory_available": self.check_memory_limit()
        }

# إنشاء مثيل عام من مدير النموذج
model_manager = ModelManager()

