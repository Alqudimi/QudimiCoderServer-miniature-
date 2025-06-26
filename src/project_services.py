import re
import json
import logging
from typing import Dict, Any, List, Optional
from src.model_manager import model_manager

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProjectServices:
    """خدمات المشاريع والأدوات المساعدة"""
    
    def __init__(self):
        self.code_templates = {
            'python': {
                'http_get': '''import requests

def make_get_request(url, headers=None):
    """إرسال طلب GET HTTP"""
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"خطأ في الطلب: {e}")
        return None''',
                
                'file_reader': '''def read_file(filename):
    """قراءة ملف نصي"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"الملف {filename} غير موجود")
        return None''',
                
                'data_processor': '''import pandas as pd

def process_csv_data(filename):
    """معالجة بيانات CSV"""
    try:
        df = pd.read_csv(filename)
        # معالجة البيانات هنا
        return df.describe()
    except Exception as e:
        print(f"خطأ في معالجة البيانات: {e}")
        return None'''
            },
            'javascript': {
                'http_get': '''async function makeGetRequest(url, headers = {}) {
    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: headers
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('خطأ في الطلب:', error);
        return null;
    }
}''',
                
                'dom_manipulator': '''function updateElement(elementId, content) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = content;
    } else {
        console.error(`العنصر ${elementId} غير موجود`);
    }
}

function addClickListener(elementId, callback) {
    const element = document.getElementById(elementId);
    if (element) {
        element.addEventListener('click', callback);
    }
}'''
            }
        }
    
    def create_snippet(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """إنشاء مقطع كود جاهز للاستخدام"""
        try:
            task = data.get('task', '').strip()
            lang = data.get('lang', 'python').lower()
            style = data.get('style', 'standard')  # standard, minimal, detailed
            
            if not task:
                raise ValueError("المهمة المطلوبة فارغة")
            
            # البحث في القوالب المحفوظة
            template = self._find_template(task, lang)
            
            if template:
                # استخدام القالب الموجود
                snippet = template
                source = "template"
            else:
                # توليد مقطع جديد باستخدام النموذج
                snippet = self._generate_snippet(task, lang, style)
                source = "generated"
            
            # إضافة تعليقات وتوثيق
            documented_snippet = self._add_documentation(snippet, task, lang)
            
            return {
                "success": True,
                "snippet": documented_snippet,
                "task": task,
                "language": lang,
                "style": style,
                "source": source,
                "usage_example": self._generate_usage_example(documented_snippet, lang)
            }
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء المقطع: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "snippet": "",
                "task": data.get('task', '')
            }
    
    def find_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """اكتشاف الأنماط المتكررة في الكود"""
        try:
            code = data.get('code', '').strip()
            lang = data.get('lang', 'python').lower()
            pattern_type = data.get('type', 'all')  # all, functions, variables, structures
            
            if not code:
                raise ValueError("الكود المدخل فارغ")
            
            patterns = []
            
            if pattern_type in ['all', 'functions']:
                function_patterns = self._find_function_patterns(code, lang)
                patterns.extend(function_patterns)
            
            if pattern_type in ['all', 'variables']:
                variable_patterns = self._find_variable_patterns(code, lang)
                patterns.extend(variable_patterns)
            
            if pattern_type in ['all', 'structures']:
                structure_patterns = self._find_structure_patterns(code, lang)
                patterns.extend(structure_patterns)
            
            # تحليل الأنماط وتقديم اقتراحات
            suggestions = self._analyze_patterns(patterns, lang)
            
            return {
                "success": True,
                "patterns": patterns,
                "pattern_count": len(patterns),
                "suggestions": suggestions,
                "language": lang,
                "analysis_type": pattern_type
            }
            
        except Exception as e:
            logger.error(f"خطأ في اكتشاف الأنماط: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "patterns": [],
                "suggestions": []
            }
    
    def generate_curl(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """تحويل كود Python لطلب HTTP إلى أمر cURL"""
        try:
            code = data.get('code', '').strip()
            lang = data.get('lang', 'python').lower()
            
            if not code:
                raise ValueError("الكود المدخل فارغ")
            
            if lang != 'python':
                raise ValueError("هذه الخدمة تدعم Python فقط حالياً")
            
            # استخراج معلومات الطلب
            request_info = self._extract_request_info(code)
            
            if not request_info:
                raise ValueError("لم يتم العثور على طلب HTTP في الكود")
            
            # توليد أمر cURL
            curl_command = self._generate_curl_command(request_info)
            
            return {
                "success": True,
                "curl_command": curl_command,
                "original_code": code,
                "request_info": request_info,
                "language": lang
            }
            
        except Exception as e:
            logger.error(f"خطأ في توليد cURL: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "curl_command": "",
                "original_code": data.get('code', '')
            }
    
    def json_to_model(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """تحويل JSON إلى نموذج كائن"""
        try:
            json_data = data.get('json', {})
            lang = data.get('lang', 'python').lower()
            class_name = data.get('class_name', 'DataModel')
            
            if not json_data:
                raise ValueError("بيانات JSON فارغة")
            
            # توليد نموذج الكائن
            if lang == 'python':
                model_code = self._generate_python_model(json_data, class_name)
            elif lang == 'javascript':
                model_code = self._generate_javascript_model(json_data, class_name)
            elif lang == 'java':
                model_code = self._generate_java_model(json_data, class_name)
            else:
                raise ValueError(f"اللغة {lang} غير مدعومة لتوليد النماذج")
            
            # توليد مثال على الاستخدام
            usage_example = self._generate_model_usage(json_data, class_name, lang)
            
            return {
                "success": True,
                "model_code": model_code,
                "usage_example": usage_example,
                "class_name": class_name,
                "language": lang,
                "json_structure": self._analyze_json_structure(json_data)
            }
            
        except Exception as e:
            logger.error(f"خطأ في تحويل JSON إلى نموذج: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "model_code": "",
                "language": data.get('lang', 'python')
            }
    
    # الدوال المساعدة
    def _find_template(self, task: str, lang: str) -> Optional[str]:
        """البحث عن قالب مناسب"""
        task_lower = task.lower()
        
        if lang in self.code_templates:
            templates = self.code_templates[lang]
            
            # البحث بالكلمات المفتاحية
            if 'http' in task_lower or 'request' in task_lower or 'get' in task_lower:
                return templates.get('http_get')
            elif 'file' in task_lower or 'read' in task_lower:
                return templates.get('file_reader')
            elif 'data' in task_lower or 'csv' in task_lower:
                return templates.get('data_processor')
            elif 'dom' in task_lower or 'element' in task_lower:
                return templates.get('dom_manipulator')
        
        return None
    
    def _generate_snippet(self, task: str, lang: str, style: str) -> str:
        """توليد مقطع كود جديد"""
        if style == 'minimal':
            prompt = f"Create a minimal {lang} code snippet for: {task}"
        elif style == 'detailed':
            prompt = f"Create a detailed {lang} code snippet with error handling for: {task}"
        else:
            prompt = f"Create a {lang} code snippet for: {task}"
        
        snippet = model_manager.generate_text(
            prompt=prompt,
            max_length=150,
            temperature=0.5
        )
        
        return self._clean_generated_code(snippet)
    
    def _add_documentation(self, snippet: str, task: str, lang: str) -> str:
        """إضافة توثيق للمقطع"""
        if lang == 'python':
            doc_comment = f'"""\n{task}\n"""'
            return f"{doc_comment}\n{snippet}"
        elif lang == 'javascript':
            doc_comment = f'/**\n * {task}\n */'
            return f"{doc_comment}\n{snippet}"
        else:
            return snippet
    
    def _generate_usage_example(self, snippet: str, lang: str) -> str:
        """توليد مثال على الاستخدام"""
        if lang == 'python':
            if 'def ' in snippet:
                # استخراج اسم الدالة
                match = re.search(r'def\s+(\w+)', snippet)
                if match:
                    func_name = match.group(1)
                    return f"# مثال على الاستخدام\nresult = {func_name}()\nprint(result)"
        
        return "# مثال على الاستخدام\n# استخدم الكود هنا"
    
    def _find_function_patterns(self, code: str, lang: str) -> List[Dict[str, Any]]:
        """البحث عن أنماط الدوال"""
        patterns = []
        
        if lang == 'python':
            # البحث عن دوال متشابهة
            functions = re.findall(r'def\s+(\w+)\s*\([^)]*\):', code)
            
            # تجميع الدوال المتشابهة
            similar_functions = {}
            for func in functions:
                # تحليل بسيط للتشابه
                base_name = re.sub(r'\d+$', '', func)  # إزالة الأرقام من النهاية
                if base_name in similar_functions:
                    similar_functions[base_name].append(func)
                else:
                    similar_functions[base_name] = [func]
            
            # إضافة الأنماط المكتشفة
            for base_name, funcs in similar_functions.items():
                if len(funcs) > 1:
                    patterns.append({
                        'type': 'similar_functions',
                        'pattern': f"دوال متشابهة: {', '.join(funcs)}",
                        'count': len(funcs),
                        'suggestion': f"يمكن دمج هذه الدوال في دالة واحدة مع معاملات"
                    })
        
        return patterns
    
    def _find_variable_patterns(self, code: str, lang: str) -> List[Dict[str, Any]]:
        """البحث عن أنماط المتغيرات"""
        patterns = []
        
        # البحث عن متغيرات متشابهة
        variables = re.findall(r'(\w+)\s*=', code)
        
        # تجميع المتغيرات المتشابهة
        similar_vars = {}
        for var in variables:
            base_name = re.sub(r'\d+$', '', var)
            if base_name in similar_vars:
                similar_vars[base_name].append(var)
            else:
                similar_vars[base_name] = [var]
        
        for base_name, vars in similar_vars.items():
            if len(vars) > 2:
                patterns.append({
                    'type': 'similar_variables',
                    'pattern': f"متغيرات متشابهة: {', '.join(vars)}",
                    'count': len(vars),
                    'suggestion': "يمكن استخدام قائمة أو قاموس بدلاً من متغيرات منفصلة"
                })
        
        return patterns
    
    def _find_structure_patterns(self, code: str, lang: str) -> List[Dict[str, Any]]:
        """البحث عن أنماط البنية"""
        patterns = []
        
        # البحث عن حلقات متكررة
        if_count = len(re.findall(r'\bif\b', code))
        for_count = len(re.findall(r'\bfor\b', code))
        while_count = len(re.findall(r'\bwhile\b', code))
        
        if if_count > 5:
            patterns.append({
                'type': 'excessive_conditionals',
                'pattern': f"عدد كبير من الشروط: {if_count}",
                'count': if_count,
                'suggestion': "فكر في استخدام قاموس أو switch case"
            })
        
        if for_count > 3:
            patterns.append({
                'type': 'multiple_loops',
                'pattern': f"حلقات متعددة: {for_count}",
                'count': for_count,
                'suggestion': "يمكن دمج بعض الحلقات لتحسين الأداء"
            })
        
        return patterns
    
    def _analyze_patterns(self, patterns: List[Dict[str, Any]], lang: str) -> List[str]:
        """تحليل الأنماط وتقديم اقتراحات"""
        suggestions = []
        
        for pattern in patterns:
            suggestions.append(pattern.get('suggestion', 'لا توجد اقتراحات'))
        
        if not suggestions:
            suggestions.append("الكود يبدو منظماً ولا توجد أنماط مشكوك فيها")
        
        return suggestions
    
    def _extract_request_info(self, code: str) -> Optional[Dict[str, Any]]:
        """استخراج معلومات طلب HTTP من الكود"""
        request_info = {}
        
        # البحث عن requests.get
        get_match = re.search(r'requests\.get\s*\(\s*["\']([^"\']+)["\']', code)
        if get_match:
            request_info['method'] = 'GET'
            request_info['url'] = get_match.group(1)
        
        # البحث عن requests.post
        post_match = re.search(r'requests\.post\s*\(\s*["\']([^"\']+)["\']', code)
        if post_match:
            request_info['method'] = 'POST'
            request_info['url'] = post_match.group(1)
        
        # البحث عن headers
        headers_match = re.search(r'headers\s*=\s*({[^}]+})', code)
        if headers_match:
            try:
                headers_str = headers_match.group(1)
                # تحويل بسيط للقاموس
                headers_str = headers_str.replace("'", '"')
                request_info['headers'] = json.loads(headers_str)
            except:
                request_info['headers'] = {}
        
        return request_info if request_info else None
    
    def _generate_curl_command(self, request_info: Dict[str, Any]) -> str:
        """توليد أمر cURL"""
        method = request_info.get('method', 'GET')
        url = request_info.get('url', '')
        headers = request_info.get('headers', {})
        
        curl_parts = ['curl']
        
        if method != 'GET':
            curl_parts.append(f'-X {method}')
        
        for key, value in headers.items():
            curl_parts.append(f'-H "{key}: {value}"')
        
        curl_parts.append(f'"{url}"')
        
        return ' '.join(curl_parts)
    
    def _generate_python_model(self, json_data: Dict[str, Any], class_name: str) -> str:
        """توليد نموذج Python"""
        fields = []
        init_params = []
        init_assignments = []
        
        for key, value in json_data.items():
            field_type = type(value).__name__
            fields.append(f"    # {key}: {field_type}")
            init_params.append(f"{key}")
            init_assignments.append(f"        self.{key} = {key}")
        
        model_code = f"""class {class_name}:
    \"\"\"نموذج البيانات المولد تلقائياً\"\"\"
{chr(10).join(fields)}
    
    def __init__(self, {', '.join(init_params)}):
{chr(10).join(init_assignments)}
    
    def to_dict(self):
        return {{
{chr(10).join([f'            "{key}": self.{key},' for key in json_data.keys()])}
        }}
    
    def __str__(self):
        return f"{class_name}({', '.join([f'{key}={{self.{key}}}' for key in json_data.keys()])})"
"""
        
        return model_code
    
    def _generate_javascript_model(self, json_data: Dict[str, Any], class_name: str) -> str:
        """توليد نموذج JavaScript"""
        constructor_params = list(json_data.keys())
        assignments = [f"        this.{key} = {key};" for key in json_data.keys()]
        
        model_code = f"""class {class_name} {{
    /**
     * نموذج البيانات المولد تلقائياً
     */
    constructor({', '.join(constructor_params)}) {{
{chr(10).join(assignments)}
    }}
    
    toJSON() {{
        return {{
{chr(10).join([f'            {key}: this.{key},' for key in json_data.keys()])}
        }};
    }}
    
    toString() {{
        return `{class_name}(${{{', '.join([f'{key}: ${{this.{key}}}' for key in json_data.keys()])}}})`;
    }}
}}"""
        
        return model_code
    
    def _generate_java_model(self, json_data: Dict[str, Any], class_name: str) -> str:
        """توليد نموذج Java"""
        fields = []
        constructor_params = []
        constructor_assignments = []
        getters_setters = []
        
        for key, value in json_data.items():
            java_type = self._get_java_type(value)
            fields.append(f"    private {java_type} {key};")
            constructor_params.append(f"{java_type} {key}")
            constructor_assignments.append(f"        this.{key} = {key};")
            
            # Getter
            getters_setters.append(f"""    public {java_type} get{key.capitalize()}() {{
        return {key};
    }}""")
            
            # Setter
            getters_setters.append(f"""    public void set{key.capitalize()}({java_type} {key}) {{
        this.{key} = {key};
    }}""")
        
        model_code = f"""public class {class_name} {{
    // الحقول
{chr(10).join(fields)}
    
    // المنشئ
    public {class_name}({', '.join(constructor_params)}) {{
{chr(10).join(constructor_assignments)}
    }}
    
    // Getters and Setters
{chr(10).join(getters_setters)}
    
    @Override
    public String toString() {{
        return "{class_name}{{" +
{chr(10).join([f'                "{key}=" + {key} +' for key in json_data.keys()])}
                '}}';
    }}
}}"""
        
        return model_code
    
    def _get_java_type(self, value: Any) -> str:
        """تحديد نوع Java المناسب"""
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "double"
        elif isinstance(value, str):
            return "String"
        elif isinstance(value, list):
            return "List<Object>"
        elif isinstance(value, dict):
            return "Map<String, Object>"
        else:
            return "Object"
    
    def _generate_model_usage(self, json_data: Dict[str, Any], class_name: str, lang: str) -> str:
        """توليد مثال على استخدام النموذج"""
        if lang == 'python':
            values = [f'"{v}"' if isinstance(v, str) else str(v) for v in json_data.values()]
            return f"""# مثال على الاستخدام
obj = {class_name}({', '.join(values)})
print(obj)
print(obj.to_dict())"""
        
        elif lang == 'javascript':
            values = [f'"{v}"' if isinstance(v, str) else str(v).lower() for v in json_data.values()]
            return f"""// مثال على الاستخدام
const obj = new {class_name}({', '.join(values)});
console.log(obj.toString());
console.log(obj.toJSON());"""
        
        return "// مثال على الاستخدام"
    
    def _analyze_json_structure(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """تحليل بنية JSON"""
        return {
            "field_count": len(json_data),
            "field_types": {key: type(value).__name__ for key, value in json_data.items()},
            "complexity": "بسيط" if len(json_data) <= 5 else "معقد"
        }
    
    def _clean_generated_code(self, code: str) -> str:
        """تنظيف الكود المولد"""
        code = re.sub(r'```\w*', '', code)
        code = re.sub(r'```', '', code)
        return code.strip()

# إنشاء مثيل عام من خدمات المشاريع
project_services = ProjectServices()

