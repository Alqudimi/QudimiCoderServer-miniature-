# دليل النشر السريع - StarCoder API Server

## 🚀 النشر على Render.com (مجاني)

### الخطوة 1: إعداد المستودع

```bash
# استنساخ أو تحميل المشروع
git clone <your-repo-url>
cd starcoder-api-server

# إنشاء مستودع Git جديد (إذا لم يكن موجوداً)
git init
git add .
git commit -m "Initial commit: StarCoder API Server"

# ربط بـ GitHub/GitLab
git remote add origin <your-repo-url>
git push -u origin main
```

### الخطوة 2: إنشاء خدمة على Render.com

1. **إنشاء حساب**:
   - اذهب إلى [render.com](https://render.com)
   - أنشئ حساب جديد أو سجل دخول

2. **إنشاء Web Service**:
   - اضغط "New +" → "Web Service"
   - اختر "Build and deploy from a Git repository"
   - اربط حساب GitHub/GitLab
   - اختر المستودع

3. **إعدادات الخدمة**:
   ```
   Name: starcoder-api-server
   Environment: Python 3
   Region: اختر الأقرب لك
   Branch: main
   Root Directory: (اتركه فارغ)
   Build Command: pip install -r requirements.txt
   Start Command: python src/main.py
   ```

4. **خطة الاستضافة**:
   - اختر "Free" للخطة المجانية
   - الموارد: 512MB RAM, 1GB Storage

### الخطوة 3: متغيرات البيئة

أضف المتغيرات التالية في قسم "Environment Variables":

```
PORT=10000
FLASK_ENV=production
API_KEYS=your-secure-key-1:admin:100,public-key:user:10
SECRET_KEY=your-very-secure-secret-key-here
MAX_MEMORY_MB=450
MAX_CONCURRENT_JOBS=3
```

**مهم**: غير مفاتيح API إلى مفاتيح آمنة!

### الخطوة 4: النشر

1. اضغط "Create Web Service"
2. انتظر اكتمال البناء (5-10 دقائق)
3. ستحصل على رابط مثل: `https://your-app-name.onrender.com`

### الخطوة 5: التحقق من النشر

```bash
# فحص حالة الخادم
curl https://your-app-name.onrender.com/health

# اختبار API
curl -H "X-API-Key: your-secure-key-1" \
     https://your-app-name.onrender.com/api/v1/info
```

## 🐳 النشر باستخدام Docker

### إنشاء الصورة

```bash
# بناء الصورة
docker build -t starcoder-api .

# تشغيل الحاوية
docker run -p 5000:10000 \
  -e API_KEYS="your-key:user:100" \
  -e SECRET_KEY="your-secret" \
  starcoder-api
```

### Docker Compose

إنشاء ملف `docker-compose.yml`:

```yaml
version: '3.8'
services:
  starcoder-api:
    build: .
    ports:
      - "5000:10000"
    environment:
      - PORT=10000
      - FLASK_ENV=production
      - API_KEYS=your-key:user:100
      - SECRET_KEY=your-secret-key
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:10000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

```bash
# تشغيل باستخدام Docker Compose
docker-compose up -d
```

## ☁️ النشر على منصات أخرى

### Heroku

1. **إنشاء ملف `Procfile`**:
```
web: python src/main.py
```

2. **النشر**:
```bash
heroku create your-app-name
heroku config:set API_KEYS="your-key:user:100"
heroku config:set SECRET_KEY="your-secret"
git push heroku main
```

### Railway

1. **ربط المستودع**:
   - اذهب إلى [railway.app](https://railway.app)
   - اربط مستودع GitHub

2. **إعدادات**:
   - Start Command: `python src/main.py`
   - أضف متغيرات البيئة

### DigitalOcean App Platform

1. **إنشاء ملف `.do/app.yaml`**:
```yaml
name: starcoder-api
services:
- name: api
  source_dir: /
  github:
    repo: your-username/starcoder-api-server
    branch: main
  run_command: python src/main.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: API_KEYS
    value: your-key:user:100
  - key: SECRET_KEY
    value: your-secret
```

## 🔧 تحسين الأداء للنشر

### 1. تحسين الذاكرة

في `src/model_manager.py`:
```python
# تقليل حجم النموذج
self.max_memory_mb = 400  # بدلاً من 450

# تنظيف أكثر تكراراً
def cleanup_model(self):
    # إضافة تنظيف إضافي
    import gc
    gc.collect()
```

### 2. تحسين الطابور

في `src/queue_manager.py`:
```python
# تقليل عدد المهام المتزامنة
self.max_concurrent_tasks = 2  # بدلاً من 3

# تقليل حجم الطابور
self.max_queue_size = 20  # بدلاً من 50
```

### 3. تحسين النموذج

```python
# استخدام نموذج أصغر إذا لزم الأمر
model = AutoModelForCausalLM.from_pretrained(
    "bigcode/starcoderbase-350m",
    load_in_8bit=True,  # بدلاً من 4bit للاستقرار
    device_map="auto",
    torch_dtype=torch.float16
)
```

## 📊 مراقبة النشر

### 1. فحص الصحة

```bash
# فحص دوري
curl https://your-app.onrender.com/health

# مراقبة الموارد
curl -H "X-API-Key: your-key" \
     https://your-app.onrender.com/api/v1/system/stats
```

### 2. السجلات

```bash
# عرض السجلات على Render.com
# Dashboard → Service → Logs

# تحميل السجلات
curl -H "X-API-Key: your-key" \
     https://your-app.onrender.com/api/v1/system/health
```

### 3. التنبيهات

إعداد تنبيهات للمراقبة:
- استخدام UptimeRobot للمراقبة الخارجية
- إعداد webhooks للتنبيهات
- مراقبة استخدام الذاكرة

## 🚨 استكشاف الأخطاء

### مشاكل شائعة

1. **خطأ في تحميل النموذج**:
```bash
# فحص الذاكرة المتاحة
curl https://your-app.onrender.com/api/v1/system/health
```

2. **تجاوز حد الذاكرة**:
   - قلل `MAX_CONCURRENT_JOBS` إلى 1 أو 2
   - استخدم تكميم 8-bit بدلاً من 4-bit

3. **بطء في الاستجابة**:
   - تحقق من حالة النموذج
   - راجع إحصائيات الطابور

4. **أخطاء المصادقة**:
   - تأكد من صحة متغيرات البيئة
   - تحقق من مفاتيح API

### أوامر التشخيص

```bash
# فحص شامل
curl -H "X-API-Key: your-key" \
     https://your-app.onrender.com/api/v1/system/stats

# اختبار الوظائف الأساسية
curl -X POST \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"code":"def test():", "lang":"python"}' \
  https://your-app.onrender.com/api/v1/completions
```

## 📈 تحسينات مستقبلية

### 1. ترقية الخطة
- الترقية إلى خطة مدفوعة للحصول على موارد أكبر
- استخدام نماذج أكبر وأكثر دقة

### 2. إضافة ميزات
- دعم المزيد من اللغات
- تحسين خوارزميات التكميم
- إضافة واجهة ويب تفاعلية

### 3. التحسين
- استخدام Redis للتخزين المؤقت
- إضافة قاعدة بيانات للإحصائيات
- تحسين خوارزميات الطابور

---

**ملاحظة**: هذا الدليل مصمم للنشر على الخطة المجانية. للحصول على أداء أفضل، فكر في الترقية إلى خطة مدفوعة.

