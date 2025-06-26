import re
import json
import ast
import logging
from typing import Dict, Any, List, Optional, Tuple
from src.model_manager import model_manager

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedServices:
    """الخدمات المحسنة للمحرر"""
    
    def __init__(self):
        self.common_errors = {
            'python': [
                (r'rang\(', 'range(', 'خطأ إملائي في range'),
                (r'lenght\(', 'len(', 'خطأ إملائي في len'),
                (r'def\s+\w+\([^)]*\)\s*$', '', 'دالة بدون محتوى'),
                (r'if\s+.*:\s*$', '', 'شرط if بدون محتوى'),
            ],
            'javascript': [
                (r'lenght', 'length', 'خطأ إملائي في length'),
                (r'fucntion', 'function', 'خطأ إملائي في function'),
                (r'consol\.log', 'console.log', 'خطأ إملائي في console'),
            ]
        }
    
    def suggest_names(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """اقتراح أسماء متغيرات ودوال أفضل"""
        try:
            code = data.get('code', '').strip()
            lang = data.get('lang', 'python').lower()
            
            if not code:
                raise ValueError("الكود المدخل فارغ")
            
            # تحليل الأسماء الحالية
            current_names = self._extract_names(code, lang)
            
            # توليد اقتراحات
            suggestions = []
            for name_info in current_names:
                if self._is_poor_name(name_info['name']):
                    suggestion = self._generate_better_name(name_info, code, lang)
                    if suggestion:
                        suggestions.append({
                            'original': name_info['name'],
                            'suggested': suggestion,
                            'type': name_info['type'],
                            'line': name_info['line'],
                            'reason': self._get_suggestion_reason(name_info['name'])
                        })
            
            return {
                "success": True,
                "suggestions": suggestions,
                "total_names_analyzed": len(current_names),
                "language": lang
            }
            
        except Exception as e:
            logger.error(f"خطأ في اقتراح الأسماء: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "suggestions": []
            }
    
    def detect_errors(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """كشف أخطاء بناء الجملة والأخطاء الشائعة"""
        try:
            code = data.get('code', '').strip()
            lang = data.get('lang', 'python').lower()
            
            if not code:
                raise ValueError("الكود المدخل فارغ")
            
            errors = []
            warnings = []
            
            # كشف الأخطاء النحوية
            syntax_errors = self._check_syntax_errors(code, lang)
            errors.extend(syntax_errors)
            
            # كشف الأخطاء الشائعة
            common_errors = self._check_common_errors(code, lang)
            errors.extend(common_errors)
            
            # كشف التحذيرات
            code_warnings = self._check_warnings(code, lang)
            warnings.extend(code_warnings)
            
            return {
                "success": True,
                "errors": errors,
                "warnings": warnings,
                "error_count": len(errors),
                "warning_count": len(warnings),
                "language": lang,
                "is_valid": len(errors) == 0
            }
            
        except Exception as e:
            logger.error(f"خطأ في كشف الأخطاء: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "errors": [],
                "warnings": []
            }
    
    def format_code(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """تنسيق الكود تلقائياً"""
        try:
            code = data.get('code', '').strip()
            lang = data.get('lang', 'python').lower()
            style = data.get('style', 'standard')  # standard, compact, verbose
            
            if not code:
                raise ValueError("الكود المدخل فارغ")
            
            # تطبيق التنسيق حسب اللغة
            formatted_code = self._apply_formatting(code, lang, style)
            
            # حساب التحسينات
            improvements = self._calculate_formatting_improvements(code, formatted_code)
            
            return {
                "success": True,
                "formatted_code": formatted_code,
                "original_code": code,
                "language": lang,
                "style": style,
                "improvements": improvements
            }
            
        except Exception as e:
            logger.error(f"خطأ في تنسيق الكود: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "formatted_code": data.get('code', ''),
                "language": data.get('lang', 'python')
            }
    
    def generate_docs(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """إنشاء توثيق تلقائي"""
        try:
            code = data.get('code', '').strip()
            lang = data.get('lang', 'python').lower()
            doc_style = data.get('style', 'standard')  # standard, detailed, minimal
            
            if not code:
                raise ValueError("الكود المدخل فارغ")
            
            # استخراج الدوال والفئات
            functions = self._extract_functions(code, lang)
            
            # توليد التوثيق
            documentation = []
            for func in functions:
                doc = self._generate_function_doc(func, lang, doc_style)
                documentation.append(doc)
            
            # إنشاء الكود مع التوثيق
            documented_code = self._insert_documentation(code, documentation, lang)
            
            return {
                "success": True,
                "documented_code": documented_code,
                "original_code": code,
                "documentation": documentation,
                "functions_documented": len(functions),
                "language": lang,
                "style": doc_style
            }
            
        except Exception as e:
            logger.error(f"خطأ في توليد التوثيق: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "documented_code": data.get('code', ''),
                "documentation": []
            }
    
    def explain_concept(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """شرح مفهوم برمجي"""
        try:
            concept = data.get('concept', '').strip()
            lang = data.get('lang', 'python').lower()
            level = data.get('level', 'beginner')  # beginner, intermediate, advanced
            
            if not concept:
                raise ValueError("المفهوم المطلوب شرحه فارغ")
            
            # إنشاء prompt للشرح
            if level == 'beginner':
                prompt = f"Explain the concept of '{concept}' in {lang} programming for beginners in Arabic with simple examples:"
            elif level == 'advanced':
                prompt = f"Provide an advanced explanation of '{concept}' in {lang} programming in Arabic with complex examples:"
            else:
                prompt = f"Explain the concept of '{concept}' in {lang} programming in Arabic with examples:"
            
            # توليد الشرح
            explanation = model_manager.generate_text(
                prompt=prompt,
                max_length=250,
                temperature=0.6
            )
            
            # إنشاء مثال عملي
            example = self._generate_concept_example(concept, lang)
            
            return {
                "success": True,
                "concept": concept,
                "explanation": explanation.strip(),
                "example": example,
                "language": lang,
                "level": level,
                "related_concepts": self._get_related_concepts(concept, lang)
            }
            
        except Exception as e:
            logger.error(f"خطأ في شرح المفهوم: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "explanation": "",
                "concept": data.get('concept', '')
            }
    
    def simplify_code(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """تبسيط الكود المعقد"""
        try:
            code = data.get('code', '').strip()
            lang = data.get('lang', 'python').lower()
            
            if not code:
                raise ValueError("الكود المدخل فارغ")
            
            # إنشاء prompt للتبسيط
            prompt = f"Simplify this {lang} code to make it easier to understand:\n{code}\nSimplified version:"
            
            # توليد النسخة المبسطة
            simplified_code = model_manager.generate_text(
                prompt=prompt,
                max_length=150,
                temperature=0.4
            )
            
            # تنظيف النتيجة
            simplified_code = self._clean_generated_code(simplified_code)
            
            # تحليل التبسيطات
            simplifications = self._analyze_simplifications(code, simplified_code, lang)
            
            return {
                "success": True,
                "simplified_code": simplified_code,
                "original_code": code,
                "language": lang,
                "simplifications": simplifications,
                "complexity_reduction": self._calculate_complexity_reduction(code, simplified_code)
            }
            
        except Exception as e:
            logger.error(f"خطأ في تبسيط الكود: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "simplified_code": data.get('code', ''),
                "language": data.get('lang', 'python')
            }
    
    # الدوال المساعدة
    def _extract_names(self, code: str, lang: str) -> List[Dict[str, Any]]:
        """استخراج أسماء المتغيرات والدوال"""
        names = []
        lines = code.split('\n')
        
        if lang == 'python':
            for i, line in enumerate(lines, 1):
                # البحث عن تعريف المتغيرات
                var_matches = re.findall(r'(\w+)\s*=', line)
                for var in var_matches:
                    if not var.startswith('_'):
                        names.append({'name': var, 'type': 'variable', 'line': i})
                
                # البحث عن تعريف الدوال
                func_matches = re.findall(r'def\s+(\w+)', line)
                for func in func_matches:
                    names.append({'name': func, 'type': 'function', 'line': i})
        
        return names
    
    def _is_poor_name(self, name: str) -> bool:
        """التحقق من جودة الاسم"""
        poor_patterns = [
            r'^[a-z]$',  # حرف واحد
            r'^(a|b|c|x|y|z)$',  # أحرف شائعة
            r'^(temp|tmp|data|info|val|var)$',  # أسماء عامة
            r'^(foo|bar|baz)$'  # أسماء placeholder
        ]
        
        for pattern in poor_patterns:
            if re.match(pattern, name, re.IGNORECASE):
                return True
        return False
    
    def _generate_better_name(self, name_info: Dict[str, Any], code: str, lang: str) -> Optional[str]:
        """توليد اسم أفضل"""
        # هذه دالة مبسطة - يمكن تحسينها باستخدام النموذج
        name_type = name_info['type']
        current_name = name_info['name']
        
        if name_type == 'variable':
            if current_name in ['x', 'y']:
                return 'coordinate'
            elif current_name in ['a', 'b']:
                return 'value'
            elif current_name == 'temp':
                return 'temporary_result'
        elif name_type == 'function':
            if current_name == 'foo':
                return 'process_data'
        
        return None
    
    def _get_suggestion_reason(self, name: str) -> str:
        """الحصول على سبب الاقتراح"""
        if len(name) == 1:
            return "اسم قصير جداً وغير وصفي"
        elif name in ['temp', 'tmp']:
            return "اسم عام جداً"
        elif name in ['foo', 'bar']:
            return "اسم placeholder يجب استبداله"
        else:
            return "يمكن تحسين وضوح الاسم"
    
    def _check_syntax_errors(self, code: str, lang: str) -> List[Dict[str, Any]]:
        """فحص الأخطاء النحوية"""
        errors = []
        
        if lang == 'python':
            try:
                ast.parse(code)
            except SyntaxError as e:
                errors.append({
                    'type': 'syntax_error',
                    'message': f"خطأ نحوي: {str(e)}",
                    'line': e.lineno if e.lineno else 1,
                    'severity': 'error'
                })
        
        return errors
    
    def _check_common_errors(self, code: str, lang: str) -> List[Dict[str, Any]]:
        """فحص الأخطاء الشائعة"""
        errors = []
        
        if lang in self.common_errors:
            for pattern, correction, message in self.common_errors[lang]:
                matches = re.finditer(pattern, code, re.MULTILINE)
                for match in matches:
                    line_num = code[:match.start()].count('\n') + 1
                    errors.append({
                        'type': 'common_error',
                        'message': message,
                        'line': line_num,
                        'suggestion': correction,
                        'severity': 'error'
                    })
        
        return errors
    
    def _check_warnings(self, code: str, lang: str) -> List[Dict[str, Any]]:
        """فحص التحذيرات"""
        warnings = []
        
        if lang == 'python':
            # فحص الأسطر الطويلة
            lines = code.split('\n')
            for i, line in enumerate(lines, 1):
                if len(line) > 79:
                    warnings.append({
                        'type': 'line_length',
                        'message': f"السطر طويل جداً ({len(line)} حرف)",
                        'line': i,
                        'severity': 'warning'
                    })
        
        return warnings
    
    def _apply_formatting(self, code: str, lang: str, style: str) -> str:
        """تطبيق التنسيق"""
        if lang == 'python':
            try:
                import autopep8
                return autopep8.fix_code(code)
            except:
                pass
        
        # تنسيق أساسي
        lines = code.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append('')
                continue
            
            if stripped.startswith('}') or stripped.startswith(']'):
                indent_level = max(0, indent_level - 1)
            
            formatted_lines.append('    ' * indent_level + stripped)
            
            if stripped.endswith('{') or stripped.endswith('['):
                indent_level += 1
        
        return '\n'.join(formatted_lines)
    
    def _calculate_formatting_improvements(self, original: str, formatted: str) -> List[str]:
        """حساب تحسينات التنسيق"""
        improvements = []
        
        original_lines = original.split('\n')
        formatted_lines = formatted.split('\n')
        
        # فحص المسافات البادئة
        original_indented = sum(1 for line in original_lines if line.startswith('    '))
        formatted_indented = sum(1 for line in formatted_lines if line.startswith('    '))
        
        if formatted_indented > original_indented:
            improvements.append("تحسين المسافات البادئة")
        
        improvements.append("تطبيق معايير التنسيق")
        
        return improvements
    
    def _extract_functions(self, code: str, lang: str) -> List[Dict[str, Any]]:
        """استخراج الدوال من الكود"""
        functions = []
        
        if lang == 'python':
            lines = code.split('\n')
            for i, line in enumerate(lines):
                match = re.match(r'def\s+(\w+)\s*\(([^)]*)\):', line.strip())
                if match:
                    functions.append({
                        'name': match.group(1),
                        'params': match.group(2),
                        'line': i + 1,
                        'signature': line.strip()
                    })
        
        return functions
    
    def _generate_function_doc(self, func: Dict[str, Any], lang: str, style: str) -> Dict[str, Any]:
        """توليد توثيق للدالة"""
        if style == 'minimal':
            doc = f"وصف مختصر للدالة {func['name']}"
        elif style == 'detailed':
            doc = f"""
            وصف تفصيلي للدالة {func['name']}
            
            المعاملات:
            {func['params'] if func['params'] else 'لا توجد معاملات'}
            
            القيمة المرجعة:
            يرجع نتيجة العملية
            """
        else:
            doc = f"وصف الدالة {func['name']}"
        
        return {
            'function': func['name'],
            'documentation': doc.strip(),
            'line': func['line']
        }
    
    def _insert_documentation(self, code: str, docs: List[Dict[str, Any]], lang: str) -> str:
        """إدراج التوثيق في الكود"""
        lines = code.split('\n')
        
        # إدراج التوثيق للدوال
        for doc in reversed(docs):  # البدء من النهاية لتجنب تغيير أرقام الأسطر
            line_index = doc['line'] - 1
            if line_index < len(lines):
                if lang == 'python':
                    doc_lines = [f'    """', f'    {doc["documentation"]}', f'    """']
                    lines[line_index:line_index] = doc_lines
        
        return '\n'.join(lines)
    
    def _generate_concept_example(self, concept: str, lang: str) -> str:
        """توليد مثال للمفهوم"""
        examples = {
            'python': {
                'loop': 'for i in range(5):\n    print(i)',
                'function': 'def greet(name):\n    return f"Hello, {name}!"',
                'class': 'class Person:\n    def __init__(self, name):\n        self.name = name'
            }
        }
        
        if lang in examples and concept.lower() in examples[lang]:
            return examples[lang][concept.lower()]
        
        return f"# مثال على {concept} في {lang}\n# سيتم إضافة المثال هنا"
    
    def _get_related_concepts(self, concept: str, lang: str) -> List[str]:
        """الحصول على مفاهيم ذات صلة"""
        related = {
            'loop': ['iteration', 'for', 'while', 'break', 'continue'],
            'function': ['parameter', 'return', 'scope', 'recursion'],
            'class': ['object', 'inheritance', 'method', 'attribute']
        }
        
        return related.get(concept.lower(), [])
    
    def _clean_generated_code(self, code: str) -> str:
        """تنظيف الكود المولد"""
        # إزالة الرموز غير المرغوبة
        code = re.sub(r'```\w*', '', code)
        code = re.sub(r'```', '', code)
        return code.strip()
    
    def _analyze_simplifications(self, original: str, simplified: str, lang: str) -> List[str]:
        """تحليل التبسيطات المطبقة"""
        simplifications = []
        
        original_lines = len(original.split('\n'))
        simplified_lines = len(simplified.split('\n'))
        
        if simplified_lines < original_lines:
            simplifications.append(f"تقليل عدد الأسطر من {original_lines} إلى {simplified_lines}")
        
        simplifications.append("تبسيط البنية")
        simplifications.append("تحسين قابلية القراءة")
        
        return simplifications
    
    def _calculate_complexity_reduction(self, original: str, simplified: str) -> str:
        """حساب تقليل التعقيد"""
        original_complexity = len(original.split('\n'))
        simplified_complexity = len(simplified.split('\n'))
        
        if simplified_complexity < original_complexity:
            reduction = ((original_complexity - simplified_complexity) / original_complexity) * 100
            return f"{reduction:.1f}%"
        
        return "0%"

# إنشاء مثيل عام من الخدمات المحسنة
enhanced_services = EnhancedServices()

