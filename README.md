# StarCoder API Server

خادم API متكامل للبرمجة باستخدام الذكاء الاصطناعي، مبني على نموذج StarCoderBase-350M المكمم (4-bit) ومصمم للعمل على الخطة المجانية لـ Render.com.

## 🎯 المميزات الرئيسية

### خدمات البرمجة الأساسية
- **إكمال الكود**: إكمال تلقائي للأكواد في 80+ لغة برمجة
- **شرح الكود**: شرح الأكواد بلغة طبيعية مع تحليل التعقيد
- **تحويل اللغات**: تحويل الكود بين لغات البرمجة المختلفة
- **إعادة الهيكلة**: تحسين وإعادة هيكلة الأكواد

### خدمات محسنة للمحرر
- **اقتراح الأسماء**: اقتراح أسماء أفضل للمتغيرات والدوال
- **كشف الأخطاء**: اكتشاف أخطاء بناء الجملة والأخطاء الشائعة
- **تنسيق الكود**: تنسيق تلقائي للأكواد
- **توليد التوثيق**: إنشاء توثيق تلقائي للدوال والفئات
- **شرح المفاهيم**: شرح المفاهيم البرمجية للمبتدئين
- **تبسيط الكود**: تبسيط الأكواد المعقدة

### أدوات المشاريع
- **إنشاء المقاطع**: توليد مقاطع كود جاهزة للاستخدام
- **اكتشاف الأنماط**: تحليل الأنماط المتكررة في الكود
- **توليد cURL**: تحويل كود Python إلى أوامر cURL
- **JSON إلى نموذج**: تحويل JSON إلى نماذج كائنات

### نظام إدارة متقدم
- **طابور ذكي**: إدارة الطلبات المتزامنة مع تتبع الحالة
- **مراقبة الموارد**: مراقبة استخدام الذاكرة والأداء
- **نظام مصادقة**: إدارة مفاتيح API مع تحديد معدل الطلبات
- **إحصائيات شاملة**: تتبع الاستخدام والأداء

## 🚀 التثبيت والتشغيل

### المتطلبات
- Python 3.9+
- 512MB RAM (للنشر على Render.com)
- 1GB مساحة تخزين

### التثبيت المحلي

```bash
# استنساخ المشروع
git clone <repository-url>
cd starcoder-api-server

# إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate  # Windows

# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل الخادم
python src/main.py
```

### النشر على Render.com

1. **إنشاء مستودع Git**:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

2. **ربط Render.com**:
   - اذهب إلى [Render.com](https://render.com)
   - أنشئ حساب جديد أو سجل دخول
   - اختر "New Web Service"
   - اربط مستودع GitHub/GitLab
   - اختر المستودع

3. **إعدادات النشر**:
   - **Name**: `starcoder-api-server`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python src/main.py`
   - **Plan**: `Free`

4. **متغيرات البيئة**:
```
PORT=10000
FLASK_ENV=production
API_KEYS=your-key-1:user1:100,your-key-2:user2:10
SECRET_KEY=your-secret-key
MAX_MEMORY_MB=450
MAX_CONCURRENT_JOBS=3
```

## 📖 استخدام API

### المصادقة
جميع الطلبات تتطلب مفتاح API:

```bash
# في الرأس
curl -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     https://your-app.onrender.com/api/v1/info

# أو في المعاملات
curl "https://your-app.onrender.com/api/v1/info?api_key=your-api-key"
```

### أمثلة الاستخدام

#### إكمال الكود
```bash
curl -X POST \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def fibonacci(n):",
    "lang": "python",
    "max_tokens": 100
  }' \
  https://your-app.onrender.com/api/v1/completions
```

#### شرح الكود
```bash
curl -X POST \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def quicksort(arr): return arr if len(arr) <= 1 else quicksort([x for x in arr[1:] if x < arr[0]]) + [arr[0]] + quicksort([x for x in arr[1:] if x >= arr[0]])",
    "lang": "python",
    "detail_level": "medium"
  }' \
  https://your-app.onrender.com/api/v1/explanations
```

#### تحويل اللغات
```bash
curl -X POST \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "function greet(name) { return `Hello, ${name}!`; }",
    "from": "javascript",
    "to": "python"
  }' \
  https://your-app.onrender.com/api/v1/conversions
```

#### كشف الأخطاء
```bash
curl -X POST \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "for i in rang(10):\n    print(i)",
    "lang": "python"
  }' \
  https://your-app.onrender.com/api/v1/detect_errors
```

## 🔧 نقاط API المتاحة

### الخدمات الأساسية
- `POST /api/v1/completions` - إكمال الكود
- `POST /api/v1/explanations` - شرح الكود
- `POST /api/v1/conversions` - تحويل اللغات
- `POST /api/v1/refactors` - إعادة هيكلة الكود

### الخدمات المحسنة
- `POST /api/v1/suggest_names` - اقتراح أسماء أفضل
- `POST /api/v1/detect_errors` - كشف الأخطاء
- `POST /api/v1/format_code` - تنسيق الكود
- `POST /api/v1/generate_docs` - توليد التوثيق
- `POST /api/v1/explain_concept` - شرح المفاهيم
- `POST /api/v1/simplify_code` - تبسيط الكود

### أدوات المشاريع
- `POST /api/v1/create_snippet` - إنشاء مقاطع كود
- `POST /api/v1/find_patterns` - اكتشاف الأنماط
- `POST /api/v1/generate_curl` - توليد أوامر cURL
- `POST /api/v1/json_to_model` - تحويل JSON إلى نماذج

### إدارة النظام
- `GET /api/v1/system/health` - حالة النظام
- `GET /api/v1/system/stats` - إحصائيات النظام
- `GET /api/v1/queue/status` - حالة الطابور
- `POST /api/v1/queue/cancel` - إلغاء مهمة

### معلومات عامة
- `GET /api/v1/info` - معلومات API
- `GET /api/v1/model/status` - حالة النموذج
- `GET /health` - فحص الصحة
- `GET /docs` - التوثيق

## 🔒 الأمان

### مفاتيح API
- كل طلب يتطلب مفتاح API صحيح
- تحديد معدل الطلبات حسب المفتاح
- تتبع الاستخدام والإحصائيات

### حماية من الهجمات
- حظر IP عند النشاط المشبوه
- تحديد معدل الطلبات
- تسجيل جميع المحاولات الفاشلة

### إدارة الموارد
- مراقبة استخدام الذاكرة
- تنظيف تلقائي للبيانات القديمة
- حدود زمنية للطلبات

## 📊 المراقبة والإحصائيات

### مراقبة النظام
```bash
# حالة النظام
curl -H "X-API-Key: your-api-key" \
     https://your-app.onrender.com/api/v1/system/health

# إحصائيات مفصلة
curl -H "X-API-Key: your-api-key" \
     https://your-app.onrender.com/api/v1/system/stats
```

### مراقبة الأداء
- متوسط وقت الاستجابة
- عدد الطلبات المعالجة
- معدل الأخطاء
- استخدام الذاكرة

## 🛠️ التطوير والمساهمة

### بنية المشروع
```
starcoder-api-server/
├── src/
│   ├── main.py              # نقطة الدخول الرئيسية
│   ├── model_manager.py     # إدارة النموذج المكمم
│   ├── queue_manager.py     # نظام الطابور الذكي
│   ├── code_services.py     # خدمات البرمجة الأساسية
│   ├── enhanced_services.py # الخدمات المحسنة
│   ├── project_services.py  # أدوات المشاريع
│   ├── monitoring.py        # نظام المراقبة
│   ├── auth.py             # نظام المصادقة
│   └── routes/
│       └── api_routes.py   # طرق API
├── requirements.txt        # متطلبات Python
├── Dockerfile             # ملف Docker
├── render.yaml           # تكوين Render.com
└── README.md            # هذا الملف
```

### إضافة ميزات جديدة
1. أنشئ خدمة جديدة في المجلد المناسب
2. أضف الطرق في `api_routes.py`
3. حدث التوثيق في `README.md`
4. اختبر محلياً قبل النشر

## 🐛 استكشاف الأخطاء

### مشاكل شائعة

#### خطأ في تحميل النموذج
```bash
# فحص حالة النموذج
curl https://your-app.onrender.com/api/v1/model/status
```

#### تجاوز حد الذاكرة
```bash
# فحص استخدام الذاكرة
curl https://your-app.onrender.com/api/v1/system/health
```

#### مشاكل المصادقة
- تأكد من وجود مفتاح API في الرأس `X-API-Key`
- تحقق من صحة المفتاح
- تأكد من عدم تجاوز حد الطلبات

### السجلات
```bash
# عرض السجلات على Render.com
# اذهب إلى Dashboard > Service > Logs
```

## 📈 الأداء والحدود

### حدود الخطة المجانية
- **الذاكرة**: 512MB
- **التخزين**: 1GB
- **وقت التشغيل**: 750 ساعة/شهر
- **النطاق الترددي**: 100GB/شهر

### الأداء المتوقع
- **زمن الاستجابة**: < 5 ثواني (طلبات بسيطة)
- **السعة**: 3 طلبات متزامنة
- **معدل النجاح**: > 99%

### تحسين الأداء
- استخدم التخزين المؤقت على مستوى العميل
- قسم المهام الكبيرة إلى طلبات أصغر
- راقب استخدام الذاكرة بانتظام

## 📞 الدعم والتواصل

### الحصول على المساعدة
- راجع التوثيق في `/docs`
- فحص حالة النظام في `/health`
- راجع السجلات للأخطاء التفصيلية

### الإبلاغ عن المشاكل
عند الإبلاغ عن مشكلة، يرجى تضمين:
- رسالة الخطأ الكاملة
- الطلب المرسل (بدون مفتاح API)
- وقت حدوث المشكلة
- معلومات النظام من `/api/v1/system/health`

## 📄 الترخيص

هذا المشروع مرخص تحت رخصة MIT. راجع ملف LICENSE للتفاصيل.

## 🙏 شكر وتقدير

- **Hugging Face**: لنموذج StarCoderBase-350M
- **Render.com**: لمنصة النشر المجانية
- **Flask**: لإطار العمل
- **المجتمع**: لجميع المساهمات والاقتراحات

---

**ملاحظة**: هذا المشروع مصمم للعمل ضمن حدود الخطة المجانية لـ Render.com. للحصول على أداء أفضل وموارد أكبر، فكر في الترقية إلى خطة مدفوعة.

