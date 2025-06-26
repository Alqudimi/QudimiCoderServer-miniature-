import re
import json
import logging
import autopep8
from typing import Dict, Any, List, Optional
from src.model_manager import model_manager

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodeServices:
    """خدمات البرمجة المتكاملة"""
    
    def __init__(self):
        self.supported_languages = {
            'python': {'ext': '.py', 'comment': '#'},
            'javascript': {'ext': '.js', 'comment': '//'},
            'java': {'ext': '.java', 'comment': '//'},
            'cpp': {'ext': '.cpp', 'comment': '//'},
            'c': {'ext': '.c', 'comment': '//'},
            'csharp': {'ext': '.cs', 'comment': '//'},
            'php': {'ext': '.php', 'comment': '//'},
            'ruby': {'ext': '.rb', 'comment': '#'},
            'go': {'ext': '.go', 'comment': '//'},
            'rust': {'ext': '.rs', 'comment': '//'},
            'typescript': {'ext': '.ts', 'comment': '//'},
            'html': {'ext': '.html', 'comment': '<!--'},
            'css': {'ext': '.css', 'comment': '/*'},
            'sql': {'ext': '.sql', 'comment': '--'},
            'bash': {'ext': '.sh', 'comment': '#'}
        }
    
    def validate_language(self, lang: str) -> bool:
        """التحقق من دعم اللغة"""
        return lang.lower() in self.supported_languages
    
    def clean_code(self, code: str) -> str:
        """تنظيف الكود من الرموز غير المرغوبة"""
        # إزالة الرموز الخاصة والمسافات الزائدة
        code = re.sub(r'^\s*```\w*\s*', '', code, flags=re.MULTILINE)
        code = re.sub(r'```\s*$', '', code, flags=re.MULTILINE)
        code = code.strip()
        return code
    
    def format_code(self, code: str, lang: str) -> str:
        """تنسيق الكود حسب اللغة"""
        try:
            if lang.lower() == 'python':
                return autopep8.fix_code(code)
            else:
                # تنسيق أساسي للغات الأخرى
                lines = code.split('\n')
                formatted_lines = []
                indent_level = 0
                
                for line in lines:
                    stripped = line.strip()
                    if not stripped:
                        formatted_lines.append('')
                        continue
                    
                    # تقليل المسافة البادئة للأقواس المغلقة
                    if stripped.startswith('}') or stripped.startswith(']') or stripped.startswith(')'):
                        indent_level = max(0, indent_level - 1)
                    
                    # إضافة المسافة البادئة
                    formatted_lines.append('    ' * indent_level + stripped)
                    
                    # زيادة المسافة البادئة للأقواس المفتوحة
                    if stripped.endswith('{') or stripped.endswith('[') or stripped.endswith('('):
                        indent_level += 1
                
                return '\n'.join(formatted_lines)
        except Exception as e:
            logger.warning(f"فشل في تنسيق الكود: {str(e)}")
            return code
    
    def complete_code(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """إكمال الكود تلقائياً"""
        try:
            code = data.get('code', '').strip()
            lang = data.get('lang', 'python').lower()
            max_tokens = data.get('max_tokens', 100)
            temperature = data.get('temperature', 0.7)
            
            if not code:
                raise ValueError("الكود المدخل فارغ")
            
            if not self.validate_language(lang):
                raise ValueError(f"اللغة {lang} غير مدعومة")
            
            # إنشاء prompt للإكمال
            prompt = f"# Complete this {lang} code:\n{code}"
            
            # توليد الإكمال
            completion = model_manager.generate_text(
                prompt=prompt,
                max_length=max_tokens,
                temperature=temperature
            )
            
            # تنظيف وتنسيق النتيجة
            completion = self.clean_code(completion)
            if completion:
                completion = self.format_code(completion, lang)
            
            return {
                "success": True,
                "completion": completion,
                "original_code": code,
                "language": lang,
                "tokens_generated": len(completion.split()) if completion else 0
            }
            
        except Exception as e:
            logger.error(f"خطأ في إكمال الكود: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "completion": "",
                "original_code": data.get('code', ''),
                "language": data.get('lang', 'python')
            }
    
    def explain_code(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """شرح الكود بلغة طبيعية"""
        try:
            code = data.get('code', '').strip()
            lang = data.get('lang', 'python').lower()
            detail_level = data.get('detail_level', 'medium')  # basic, medium, detailed
            
            if not code:
                raise ValueError("الكود المدخل فارغ")
            
            if not self.validate_language(lang):
                raise ValueError(f"اللغة {lang} غير مدعومة")
            
            # إنشاء prompt للشرح
            if detail_level == 'basic':
                prompt = f"Explain this {lang} code briefly in Arabic:\n{code}\nExplanation:"
            elif detail_level == 'detailed':
                prompt = f"Explain this {lang} code in detail in Arabic, including complexity and best practices:\n{code}\nDetailed explanation:"
            else:
                prompt = f"Explain this {lang} code in Arabic:\n{code}\nExplanation:"
            
            # توليد الشرح
            explanation = model_manager.generate_text(
                prompt=prompt,
                max_length=200,
                temperature=0.5
            )
            
            # تحليل تعقد الكود
            complexity = self._analyze_complexity(code, lang)
            
            # اقتراحات للتحسين
            suggestions = self._generate_suggestions(code, lang)
            
            return {
                "success": True,
                "explanation": explanation.strip(),
                "complexity": complexity,
                "suggestions": suggestions,
                "language": lang,
                "detail_level": detail_level
            }
            
        except Exception as e:
            logger.error(f"خطأ في شرح الكود: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "explanation": "",
                "language": data.get('lang', 'python')
            }
    
    def convert_language(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """تحويل الكود بين اللغات"""
        try:
            code = data.get('code', '').strip()
            from_lang = data.get('from', 'python').lower()
            to_lang = data.get('to', 'javascript').lower()
            
            if not code:
                raise ValueError("الكود المدخل فارغ")
            
            if not self.validate_language(from_lang) or not self.validate_language(to_lang):
                raise ValueError("إحدى اللغات غير مدعومة")
            
            # إنشاء prompt للتحويل
            prompt = f"Convert this {from_lang} code to {to_lang}:\n{code}\n{to_lang} equivalent:"
            
            # توليد التحويل
            converted_code = model_manager.generate_text(
                prompt=prompt,
                max_length=150,
                temperature=0.3
            )
            
            # تنظيف وتنسيق النتيجة
            converted_code = self.clean_code(converted_code)
            if converted_code:
                converted_code = self.format_code(converted_code, to_lang)
            
            return {
                "success": True,
                "converted_code": converted_code,
                "original_code": code,
                "from_language": from_lang,
                "to_language": to_lang,
                "conversion_notes": f"تم التحويل من {from_lang} إلى {to_lang}"
            }
            
        except Exception as e:
            logger.error(f"خطأ في تحويل الكود: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "converted_code": "",
                "from_language": data.get('from', 'python'),
                "to_language": data.get('to', 'javascript')
            }
    
    def refactor_code(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """إعادة هيكلة الكود"""
        try:
            code = data.get('code', '').strip()
            lang = data.get('lang', 'python').lower()
            refactor_type = data.get('type', 'general')  # general, performance, readability
            
            if not code:
                raise ValueError("الكود المدخل فارغ")
            
            if not self.validate_language(lang):
                raise ValueError(f"اللغة {lang} غير مدعومة")
            
            # إنشاء prompt لإعادة الهيكلة
            if refactor_type == 'performance':
                prompt = f"Refactor this {lang} code for better performance:\n{code}\nOptimized code:"
            elif refactor_type == 'readability':
                prompt = f"Refactor this {lang} code for better readability:\n{code}\nCleaner code:"
            else:
                prompt = f"Refactor and improve this {lang} code:\n{code}\nImproved code:"
            
            # توليد الكود المحسن
            refactored_code = model_manager.generate_text(
                prompt=prompt,
                max_length=200,
                temperature=0.4
            )
            
            # تنظيف وتنسيق النتيجة
            refactored_code = self.clean_code(refactored_code)
            if refactored_code:
                refactored_code = self.format_code(refactored_code, lang)
            
            # تحليل التحسينات
            improvements = self._analyze_improvements(code, refactored_code, lang)
            
            return {
                "success": True,
                "refactored_code": refactored_code,
                "original_code": code,
                "language": lang,
                "refactor_type": refactor_type,
                "improvements": improvements
            }
            
        except Exception as e:
            logger.error(f"خطأ في إعادة هيكلة الكود: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "refactored_code": "",
                "language": data.get('lang', 'python')
            }
    
    def _analyze_complexity(self, code: str, lang: str) -> str:
        """تحليل تعقد الكود"""
        lines = len(code.split('\n'))
        if lines <= 5:
            return "بسيط"
        elif lines <= 20:
            return "متوسط"
        else:
            return "معقد"
    
    def _generate_suggestions(self, code: str, lang: str) -> List[str]:
        """توليد اقتراحات للتحسين"""
        suggestions = []
        
        if lang == 'python':
            if 'print(' in code:
                suggestions.append("استخدم logging بدلاً من print للتطبيقات الإنتاجية")
            if 'global ' in code:
                suggestions.append("تجنب استخدام المتغيرات العامة")
        
        if len(code.split('\n')) > 20:
            suggestions.append("فكر في تقسيم الكود إلى دوال أصغر")
        
        if not suggestions:
            suggestions.append("الكود يبدو جيداً")
        
        return suggestions
    
    def _analyze_improvements(self, original: str, refactored: str, lang: str) -> List[str]:
        """تحليل التحسينات المطبقة"""
        improvements = []
        
        original_lines = len(original.split('\n'))
        refactored_lines = len(refactored.split('\n'))
        
        if refactored_lines < original_lines:
            improvements.append(f"تقليل عدد الأسطر من {original_lines} إلى {refactored_lines}")
        
        improvements.append("تحسين قابلية القراءة")
        improvements.append("تطبيق أفضل الممارسات")
        
        return improvements

# إنشاء مثيل عام من خدمات البرمجة
code_services = CodeServices()

