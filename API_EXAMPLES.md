# أمثلة شاملة لاستخدام StarCoder API

## 🔑 المصادقة

جميع الطلبات تتطلب مفتاح API في الرأس:

```bash
X-API-Key: your-api-key-here
```

أو في المعاملات:
```bash
?api_key=your-api-key-here
```

## 📊 معلومات عامة

### الحصول على معلومات API

```bash
curl -H "X-API-Key: dev-key-12345" \
     https://your-app.onrender.com/api/v1/info
```

**الاستجابة:**
```json
{
  "name": "StarCoder API Server",
  "version": "1.0.0",
  "description": "خادم API متكامل للبرمجة باستخدام نموذج StarCoderBase-350M",
  "supported_languages": ["python", "javascript", "java", "cpp", "..."],
  "endpoints": {
    "core_services": ["/v1/completions", "/v1/explanations", "..."],
    "enhanced_services": ["/v1/suggest_names", "/v1/detect_errors", "..."]
  }
}
```

### فحص حالة النظام

```bash
curl https://your-app.onrender.com/health
```

**الاستجابة:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "components": {
    "model": {
      "status": "loaded",
      "memory_usage": "320.5MB"
    },
    "queue": {
      "status": "running",
      "active_tasks": 1,
      "waiting_tasks": 0
    },
    "system": {
      "status": "healthy",
      "memory_usage": "75.2%",
      "uptime": "2:15:30"
    }
  }
}
```

## 🔧 الخدمات الأساسية

### 1. إكمال الكود

#### Python - دالة بسيطة

```bash
curl -X POST \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def fibonacci(n):",
    "lang": "python",
    "max_tokens": 100,
    "temperature": 0.7
  }' \
  https://your-app.onrender.com/api/v1/completions
```

**الاستجابة:**
```json
{
  "success": true,
  "data": {
    "completion": "    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
    "original_code": "def fibonacci(n):",
    "language": "python",
    "tokens_generated": 15
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### JavaScript - دالة سهم

```bash
curl -X POST \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "const calculateArea = (radius) =>",
    "lang": "javascript",
    "max_tokens": 50
  }' \
  https://your-app.onrender.com/api/v1/completions
```

**الاستجابة:**
```json
{
  "success": true,
  "data": {
    "completion": " Math.PI * radius * radius;",
    "original_code": "const calculateArea = (radius) =>",
    "language": "javascript",
    "tokens_generated": 8
  }
}
```

### 2. شرح الكود

#### شرح خوارزمية معقدة

```bash
curl -X POST \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def quicksort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quicksort(left) + middle + quicksort(right)",
    "lang": "python",
    "detail_level": "detailed"
  }' \
  https://your-app.onrender.com/api/v1/explanations
```

**الاستجابة:**
```json
{
  "success": true,
  "data": {
    "explanation": "هذه دالة تطبق خوارزمية الترتيب السريع (QuickSort). تعمل الخوارزمية بتقسيم المصفوفة إلى ثلاثة أجزاء حول عنصر محوري: العناصر الأصغر، المساوية، والأكبر من المحور، ثم تطبق نفس العملية بشكل تكراري على الأجزاء الفرعية.",
    "complexity": "O(n log n) في المتوسط، O(n²) في أسوأ الحالات",
    "suggestions": [
      "يمكن تحسين اختيار المحور لتجنب أسوأ الحالات",
      "استخدام الترتيب في المكان لتوفير الذاكرة"
    ],
    "language": "python",
    "detail_level": "detailed"
  }
}
```

#### شرح مبسط

```bash
curl -X POST \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "x = [i**2 for i in range(10)]",
    "lang": "python",
    "detail_level": "basic"
  }' \
  https://your-app.onrender.com/api/v1/explanations
```

**الاستجابة:**
```json
{
  "success": true,
  "data": {
    "explanation": "هذا السطر ينشئ قائمة تحتوي على مربعات الأرقام من 0 إلى 9",
    "complexity": "O(n)",
    "suggestions": ["الكود واضح ومقروء"],
    "language": "python",
    "detail_level": "basic"
  }
}
```

### 3. تحويل اللغات

#### JavaScript إلى Python

```bash
curl -X POST \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "function greet(name) {\n    return `Hello, ${name}!`;\n}",
    "from": "javascript",
    "to": "python"
  }' \
  https://your-app.onrender.com/api/v1/conversions
```

**الاستجابة:**
```json
{
  "success": true,
  "data": {
    "converted_code": "def greet(name):\n    return f\"Hello, {name}!\"",
    "original_code": "function greet(name) {\n    return `Hello, ${name}!`;\n}",
    "from_language": "javascript",
    "to_language": "python",
    "conversion_notes": "تم التحويل من javascript إلى python"
  }
}
```

#### Python إلى Java

```bash
curl -X POST \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "class Calculator:\n    def add(self, a, b):\n        return a + b",
    "from": "python",
    "to": "java"
  }' \
  https://your-app.onrender.com/api/v1/conversions
```

**الاستجابة:**
```json
{
  "success": true,
  "data": {
    "converted_code": "public class Calculator {\n    public int add(int a, int b) {\n        return a + b;\n    }\n}",
    "original_code": "class Calculator:\n    def add(self, a, b):\n        return a + b",
    "from_language": "python",
    "to_language": "java"
  }
}
```

### 4. إعادة هيكلة الكود

#### تحسين الأداء

```bash
curl -X POST \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def find_max(numbers):\n    max_val = numbers[0]\n    for num in numbers:\n        if num > max_val:\n            max_val = num\n    return max_val",
    "lang": "python",
    "type": "performance"
  }' \
  https://your-app.onrender.com/api/v1/refactors
```

**الاستجابة:**
```json
{
  "success": true,
  "data": {
    "refactored_code": "def find_max(numbers):\n    return max(numbers)",
    "original_code": "def find_max(numbers):\n    max_val = numbers[0]\n    for num in numbers:\n        if num > max_val:\n            max_val = num\n    return max_val",
    "language": "python",
    "refactor_type": "performance",
    "improvements": [
      "تقليل عدد الأسطر من 5 إلى 1",
      "استخدام دالة مدمجة محسنة",
      "تحسين قابلية القراءة"
    ]
  }
}
```

## ⚡ الخدمات المحسنة

### 1. اقتراح أسماء أفضل

```bash
curl -X POST \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def foo(a, b):\n    x = a + b\n    y = a * b\n    return x, y",
    "lang": "python"
  }' \
  https://your-app.onrender.com/api/v1/suggest_names
```

**الاستجابة:**
```json
{
  "success": true,
  "data": {
    "suggestions": [
      {
        "original": "foo",
        "suggested": "calculate_sum_and_product",
        "type": "function",
        "line": 1,
        "reason": "اسم placeholder يجب استبداله"
      },
      {
        "original": "x",
        "suggested": "sum_result",
        "type": "variable",
        "line": 2,
        "reason": "اسم قصير جداً وغير وصفي"
      },
      {
        "original": "y",
        "suggested": "product_result",
        "type": "variable",
        "line": 3,
        "reason": "اسم قصير جداً وغير وصفي"
      }
    ],
    "total_names_analyzed": 5,
    "language": "python"
  }
}
```

### 2. كشف الأخطاء

```bash
curl -X POST \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "for i in rang(10):\n    print(i)\n    if i = 5:\n        break",
    "lang": "python"
  }' \
  https://your-app.onrender.com/api/v1/detect_errors
```

**الاستجابة:**
```json
{
  "success": true,
  "data": {
    "errors": [
      {
        "type": "common_error",
        "message": "خطأ إملائي في range",
        "line": 1,
        "suggestion": "range(",
        "severity": "error"
      },
      {
        "type": "syntax_error",
        "message": "خطأ نحوي: استخدام = بدلاً من == في الشرط",
        "line": 3,
        "severity": "error"
      }
    ],
    "warnings": [
      {
        "type": "style",
        "message": "يفضل استخدام مسافات حول العوامل",
        "line": 3,
        "severity": "warning"
      }
    ],
    "error_count": 2,
    "warning_count": 1,
    "is_valid": false,
    "language": "python"
  }
}
```

### 3. تنسيق الكود

```bash
curl -X POST \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def calculate(x,y,z):return x+y*z",
    "lang": "python",
    "style": "standard"
  }' \
  https://your-app.onrender.com/api/v1/format_code
```

**الاستجابة:**
```json
{
  "success": true,
  "data": {
    "formatted_code": "def calculate(x, y, z):\n    return x + y * z",
    "original_code": "def calculate(x,y,z):return x+y*z",
    "language": "python",
    "style": "standard",
    "improvements": [
      "تحسين المسافات البادئة",
      "إضافة مسافات حول العوامل",
      "تطبيق معايير التنسيق"
    ]
  }
}
```

### 4. توليد التوثيق

```bash
curl -X POST \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def calculate_area(radius):\n    return 3.14159 * radius * radius\n\ndef calculate_circumference(radius):\n    return 2 * 3.14159 * radius",
    "lang": "python",
    "style": "detailed"
  }' \
  https://your-app.onrender.com/api/v1/generate_docs
```

**الاستجابة:**
```json
{
  "success": true,
  "data": {
    "documented_code": "def calculate_area(radius):\n    \"\"\"\n    حساب مساحة الدائرة\n    \n    المعاملات:\n    radius: نصف قطر الدائرة\n    \n    القيمة المرجعة:\n    مساحة الدائرة\n    \"\"\"\n    return 3.14159 * radius * radius\n\ndef calculate_circumference(radius):\n    \"\"\"\n    حساب محيط الدائرة\n    \n    المعاملات:\n    radius: نصف قطر الدائرة\n    \n    القيمة المرجعة:\n    محيط الدائرة\n    \"\"\"\n    return 2 * 3.14159 * radius",
    "documentation": [
      {
        "function": "calculate_area",
        "documentation": "حساب مساحة الدائرة",
        "line": 1
      },
      {
        "function": "calculate_circumference", 
        "documentation": "حساب محيط الدائرة",
        "line": 4
      }
    ],
    "functions_documented": 2,
    "language": "python"
  }
}
```

### 5. شرح المفاهيم

```bash
curl -X POST \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "concept": "Closure",
    "lang": "javascript",
    "level": "intermediate"
  }' \
  https://your-app.onrender.com/api/v1/explain_concept
```

**الاستجابة:**
```json
{
  "success": true,
  "data": {
    "concept": "Closure",
    "explanation": "الـ Closure في JavaScript هو دالة لها إمكانية الوصول إلى المتغيرات في النطاق الخارجي حتى بعد انتهاء تنفيذ الدالة الخارجية. يسمح هذا بإنشاء متغيرات خاصة وحفظ الحالة.",
    "example": "function outerFunction(x) {\n  return function(y) {\n    return x + y;\n  };\n}\nconst addFive = outerFunction(5);\nconsole.log(addFive(3)); // 8",
    "language": "javascript",
    "level": "intermediate",
    "related_concepts": ["scope", "function", "lexical environment"]
  }
}
```

### 6. تبسيط الكود

```bash
curl -X POST \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "result = [item for sublist in [[1,2], [3,4], [5,6]] for item in sublist if item % 2 == 0]",
    "lang": "python"
  }' \
  https://your-app.onrender.com/api/v1/simplify_code
```

**الاستجابة:**
```json
{
  "success": true,
  "data": {
    "simplified_code": "nested_lists = [[1,2], [3,4], [5,6]]\nresult = []\nfor sublist in nested_lists:\n    for item in sublist:\n        if item % 2 == 0:\n            result.append(item)",
    "original_code": "result = [item for sublist in [[1,2], [3,4], [5,6]] for item in sublist if item % 2 == 0]",
    "language": "python",
    "simplifications": [
      "تحويل List Comprehension إلى حلقات عادية",
      "تقسيم العملية إلى خطوات واضحة",
      "تحسين قابلية القراءة"
    ],
    "complexity_reduction": "60.0%"
  }
}
```

## 🛠️ أدوات المشاريع

### 1. إنشاء مقاطع الكود

```bash
curl -X POST \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "HTTP GET request",
    "lang": "python",
    "style": "detailed"
  }' \
  https://your-app.onrender.com/api/v1/create_snippet
```

**الاستجابة:**
```json
{
  "success": true,
  "data": {
    "snippet": "\"\"\"\nHTTP GET request\n\"\"\"\nimport requests\n\ndef make_get_request(url, headers=None):\n    \"\"\"إرسال طلب GET HTTP\"\"\"\n    try:\n        response = requests.get(url, headers=headers)\n        response.raise_for_status()\n        return response.json()\n    except requests.exceptions.RequestException as e:\n        print(f\"خطأ في الطلب: {e}\")\n        return None",
    "task": "HTTP GET request",
    "language": "python",
    "style": "detailed",
    "source": "template",
    "usage_example": "# مثال على الاستخدام\nresult = make_get_request('https://api.example.com/data')\nprint(result)"
  }
}
```

### 2. اكتشاف الأنماط

```bash
curl -X POST \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def process_data1(data):\n    return data.upper()\n\ndef process_data2(data):\n    return data.lower()\n\ndef process_data3(data):\n    return data.strip()",
    "lang": "python",
    "type": "functions"
  }' \
  https://your-app.onrender.com/api/v1/find_patterns
```

**الاستجابة:**
```json
{
  "success": true,
  "data": {
    "patterns": [
      {
        "type": "similar_functions",
        "pattern": "دوال متشابهة: process_data1, process_data2, process_data3",
        "count": 3,
        "suggestion": "يمكن دمج هذه الدوال في دالة واحدة مع معاملات"
      }
    ],
    "pattern_count": 1,
    "suggestions": [
      "يمكن دمج هذه الدوال في دالة واحدة مع معاملات"
    ],
    "language": "python",
    "analysis_type": "functions"
  }
}
```

### 3. توليد أوامر cURL

```bash
curl -X POST \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import requests\nresponse = requests.get(\"https://api.github.com/users/octocat\", headers={\"Authorization\": \"token abc123\"})",
    "lang": "python"
  }' \
  https://your-app.onrender.com/api/v1/generate_curl
```

**الاستجابة:**
```json
{
  "success": true,
  "data": {
    "curl_command": "curl -H \"Authorization: token abc123\" \"https://api.github.com/users/octocat\"",
    "original_code": "import requests\nresponse = requests.get(\"https://api.github.com/users/octocat\", headers={\"Authorization\": \"token abc123\"})",
    "request_info": {
      "method": "GET",
      "url": "https://api.github.com/users/octocat",
      "headers": {
        "Authorization": "token abc123"
      }
    },
    "language": "python"
  }
}
```

### 4. تحويل JSON إلى نماذج

```bash
curl -X POST \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "json": {
      "name": "أحمد محمد",
      "age": 30,
      "email": "ahmed@example.com",
      "active": true
    },
    "lang": "python",
    "class_name": "User"
  }' \
  https://your-app.onrender.com/api/v1/json_to_model
```

**الاستجابة:**
```json
{
  "success": true,
  "data": {
    "model_code": "class User:\n    \"\"\"نموذج البيانات المولد تلقائياً\"\"\"\n    # name: str\n    # age: int\n    # email: str\n    # active: bool\n    \n    def __init__(self, name, age, email, active):\n        self.name = name\n        self.age = age\n        self.email = email\n        self.active = active\n    \n    def to_dict(self):\n        return {\n            \"name\": self.name,\n            \"age\": self.age,\n            \"email\": self.email,\n            \"active\": self.active,\n        }\n    \n    def __str__(self):\n        return f\"User(name={self.name}, age={self.age}, email={self.email}, active={self.active})\"",
    "usage_example": "# مثال على الاستخدام\nobj = User(\"أحمد محمد\", 30, \"ahmed@example.com\", True)\nprint(obj)\nprint(obj.to_dict())",
    "class_name": "User",
    "language": "python",
    "json_structure": {
      "field_count": 4,
      "field_types": {
        "name": "str",
        "age": "int", 
        "email": "str",
        "active": "bool"
      },
      "complexity": "بسيط"
    }
  }
}
```

## 📊 إدارة النظام

### 1. حالة الطابور

```bash
# حالة عامة للطابور
curl -H "X-API-Key: dev-key-12345" \
     https://your-app.onrender.com/api/v1/queue/status
```

**الاستجابة:**
```json
{
  "success": true,
  "queue": {
    "active_tasks": 2,
    "waiting_tasks": 1,
    "max_concurrent": 3,
    "max_queue_size": 50,
    "total_processed": 156,
    "total_failed": 3,
    "average_processing_time": 2.34,
    "queue_utilization": 2.0
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

```bash
# حالة مهمة محددة
curl -H "X-API-Key: dev-key-12345" \
     "https://your-app.onrender.com/api/v1/queue/status?task_id=abc123"
```

**الاستجابة:**
```json
{
  "success": true,
  "task": {
    "task_id": "abc123",
    "status": "completed",
    "endpoint": "completions",
    "created_at": "2024-01-15T10:25:00Z",
    "started_at": "2024-01-15T10:25:05Z",
    "completed_at": "2024-01-15T10:25:08Z",
    "result": {
      "completion": "    return x + y",
      "success": true
    }
  }
}
```

### 2. إلغاء مهمة

```bash
curl -X POST \
  -H "X-API-Key: dev-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "abc123"
  }' \
  https://your-app.onrender.com/api/v1/queue/cancel
```

**الاستجابة:**
```json
{
  "success": true,
  "message": "تم إلغاء المهمة بنجاح",
  "task_id": "abc123",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 3. إحصائيات النظام

```bash
curl -H "X-API-Key: dev-key-12345" \
     https://your-app.onrender.com/api/v1/system/stats
```

**الاستجابة:**
```json
{
  "success": true,
  "stats": {
    "timestamp": "2024-01-15T10:30:00Z",
    "uptime_hours": 12.5,
    "requests": {
      "total": 1250,
      "by_endpoint": {
        "completions": 450,
        "explanations": 320,
        "conversions": 180,
        "detect_errors": 150,
        "other": 150
      },
      "per_hour": 100.0,
      "success_rate": 97.6
    },
    "errors": {
      "total": 30,
      "by_type": {
        "validation_error": 15,
        "timeout_error": 8,
        "memory_error": 4,
        "other": 3
      },
      "error_rate": 2.4
    },
    "performance": {
      "avg_response_time": 2.45,
      "min_response_time": 0.8,
      "max_response_time": 8.2,
      "recent_requests": 100
    },
    "memory": {
      "avg_mb": 380.5,
      "min_mb": 320.2,
      "max_mb": 445.8,
      "trend": "stable",
      "data_points": 750
    },
    "alerts": []
  }
}
```

### 4. حالة النموذج

```bash
curl -H "X-API-Key: dev-key-12345" \
     https://your-app.onrender.com/api/v1/model/status
```

**الاستجابة:**
```json
{
  "success": true,
  "model": {
    "loaded": true,
    "memory_usage_mb": 325.4,
    "memory_limit_mb": 450,
    "memory_available": true
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🚨 معالجة الأخطاء

### خطأ في المصادقة

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"code": "test"}' \
  https://your-app.onrender.com/api/v1/completions
```

**الاستجابة:**
```json
{
  "error": "مفتاح API مطلوب",
  "hint": "أضف X-API-Key في الرأس أو api_key في المعاملات"
}
```

### تجاوز حد الطلبات

```json
{
  "error": "تم تجاوز حد الطلبات",
  "rate_limit_info": {
    "allowed": false,
    "current_requests": 10,
    "limit": 10,
    "window_minutes": 1,
    "retry_after": 45
  }
}
```

### خطأ في التحقق من البيانات

```json
{
  "success": false,
  "error": "الكود المدخل فارغ",
  "completion": "",
  "original_code": "",
  "language": "python"
}
```

### خطأ في النظام

```json
{
  "error": "خطأ داخلي في الخادم",
  "message": "يرجى المحاولة لاحقاً أو التواصل مع الدعم"
}
```

## 📱 أمثلة بلغات برمجة مختلفة

### Python

```python
import requests

API_KEY = "dev-key-12345"
BASE_URL = "https://your-app.onrender.com/api/v1"

def complete_code(code, lang="python"):
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "code": code,
        "lang": lang,
        "max_tokens": 100
    }
    
    response = requests.post(f"{BASE_URL}/completions", 
                           headers=headers, json=data)
    return response.json()

# استخدام
result = complete_code("def fibonacci(n):")
print(result["data"]["completion"])
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

const API_KEY = 'dev-key-12345';
const BASE_URL = 'https://your-app.onrender.com/api/v1';

async function completeCode(code, lang = 'javascript') {
    try {
        const response = await axios.post(`${BASE_URL}/completions`, {
            code: code,
            lang: lang,
            max_tokens: 100
        }, {
            headers: {
                'X-API-Key': API_KEY,
                'Content-Type': 'application/json'
            }
        });
        
        return response.data;
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
        return null;
    }
}

// استخدام
completeCode('const calculateArea = (radius) =>')
    .then(result => {
        if (result && result.success) {
            console.log(result.data.completion);
        }
    });
```

### PHP

```php
<?php
function completeCode($code, $lang = 'php') {
    $apiKey = 'dev-key-12345';
    $baseUrl = 'https://your-app.onrender.com/api/v1';
    
    $data = json_encode([
        'code' => $code,
        'lang' => $lang,
        'max_tokens' => 100
    ]);
    
    $context = stream_context_create([
        'http' => [
            'method' => 'POST',
            'header' => [
                'X-API-Key: ' . $apiKey,
                'Content-Type: application/json',
                'Content-Length: ' . strlen($data)
            ],
            'content' => $data
        ]
    ]);
    
    $response = file_get_contents($baseUrl . '/completions', false, $context);
    return json_decode($response, true);
}

// استخدام
$result = completeCode('function calculateSum($a, $b) {');
if ($result['success']) {
    echo $result['data']['completion'];
}
?>
```

---

**ملاحظة**: استبدل `your-app.onrender.com` برابط تطبيقك الفعلي و `dev-key-12345` بمفتاح API الخاص بك.

