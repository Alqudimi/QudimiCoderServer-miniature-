# استخدام صورة Python الرسمية المحسنة
FROM python:3.9-slim

# تعيين متغيرات البيئة
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# تحديث النظام وتثبيت المتطلبات الأساسية
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# إنشاء مجلد العمل
WORKDIR /app

# نسخ ملف المتطلبات أولاً للاستفادة من Docker cache
COPY requirements.txt .

# تثبيت المتطلبات Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY download_model.py .

# تحميل النموذج مسبقًا
RUN python download_model.py
# نسخ كامل المشروع
COPY . .

# إنشاء مجلد السجلات
RUN mkdir -p /app/logs

# تعيين الصلاحيات
RUN chmod +x /app/src/main.py

# تعريض المنفذ
EXPOSE 10000

# متغيرات البيئة الافتراضية
ENV PORT=10000
ENV FLASK_ENV=production
ENV API_KEYS=dev-key-12345:developer:100

# فحص الصحة
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# أمر التشغيل
CMD ["python", "src/main.py"]

