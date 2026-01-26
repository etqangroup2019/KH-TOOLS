# -*- coding: utf-8 -*-
"""
منظومة المهندس v3 - نظام محاسبي شامل وقابل للتوسع
نظام إدارة المشاريع والمقاولات والموارد البشرية والمحاسبة
تم تطويره باللغة العربية مع دعم كامل للتوسع المستقبلي
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List, Tuple, Any, Union
import logging
import json
import hashlib
import uuid
from decimal import Decimal
import os
from contextlib import contextmanager

# إعداد نظام السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('منظومة_المهندس.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class منظومة_المهندس_v3:
    """
    الكلاس الرئيسي لمنظومة المهندس v3
    نظام محاسبي شامل وقابل للتوسع مع دعم كامل للمشاريع والمقاولات
    """
    
    def __init__(self, host='localhost', user='root', password='kh123456'):
        """
        تهيئة النظام
        
        Args:
            host (str): عنوان الخادم
            user (str): اسم المستخدم
            password (str): كلمة المرور
        """
        self.host = host
        self.user = user
        self.password = password
        self.db_name = 'منظومة_المهندس_v3'
        self.connection = None
        self.cursor = None
        self.current_user = None
        self.session_id = None
        
        # إعدادات النظام
        self.settings = {}
        self.load_system_settings()
        
        logger.info("تم تهيئة منظومة المهندس v3")
    
    # ==================== دوال الاتصال بقاعدة البيانات ====================
    
    def انشاء_اتصال(self) -> bool:
        """
        إنشاء اتصال بقاعدة البيانات
        
        Returns:
            bool: True إذا تم الاتصال بنجاح، False في حالة الفشل
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.db_name,
                    charset='utf8mb4',
                    collation='utf8mb4_unicode_ci',
                    autocommit=False,
                    use_unicode=True
                )
                self.cursor = self.connection.cursor(dictionary=True, buffered=True)
                logger.info("تم إنشاء الاتصال بقاعدة البيانات بنجاح")
                return True
        except Error as e:
            logger.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
            return False
    
    def اغلاق_اتصال(self):
        """إغلاق الاتصال بقاعدة البيانات"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
            logger.info("تم إغلاق الاتصال بقاعدة البيانات")
        except Error as e:
            logger.error(f"خطأ في إغلاق الاتصال: {e}")
    
    @contextmanager
    def اتصال_مؤقت(self):
        """
        إنشاء اتصال مؤقت باستخدام context manager
        """
        connection_created = False
        try:
            if not self.connection or not self.connection.is_connected():
                self.انشاء_اتصال()
                connection_created = True
            yield self
        finally:
            if connection_created:
                self.اغلاق_اتصال()
    
    # ==================== دوال قاعدة البيانات العامة ====================
    
    def استعلام(self, query: str, params: tuple = None) -> List[Dict]:
        """
        تنفيذ استعلام SELECT
        
        Args:
            query (str): الاستعلام
            params (tuple): المعاملات
            
        Returns:
            List[Dict]: نتائج الاستعلام
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.انشاء_اتصال()
            
            self.cursor.execute(query, params or ())
            results = self.cursor.fetchall()
            
            # تسجيل النشاط
            self._تسجيل_نشاط('استعلام', query[:100])
            
            return results
        except Error as e:
            logger.error(f"خطأ في الاستعلام: {e}")
            logger.error(f"الاستعلام: {query}")
            return []
    
    def تحديث(self, query: str, params: tuple = None) -> bool:
        """
        تنفيذ استعلام UPDATE/INSERT/DELETE
        
        Args:
            query (str): الاستعلام
            params (tuple): المعاملات
            
        Returns:
            bool: True إذا تم التحديث بنجاح
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.انشاء_اتصال()
            
            self.cursor.execute(query, params or ())
            self.connection.commit()
            
            # تسجيل النشاط
            self._تسجيل_نشاط('تحديث', query[:100])
            
            return True
        except Error as e:
            logger.error(f"خطأ في التحديث: {e}")
            logger.error(f"الاستعلام: {query}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def حذف(self, table: str, condition: str, params: tuple = None) -> bool:
        """
        حذف سجل من جدول
        
        Args:
            table (str): اسم الجدول
            condition (str): شرط الحذف
            params (tuple): المعاملات
            
        Returns:
            bool: True إذا تم الحذف بنجاح
        """
        query = f"DELETE FROM `{table}` WHERE {condition}"
        return self.تحديث(query, params)
    
    def تحميل_بيانات(self, table: str, condition: str = None, params: tuple = None, 
                      order_by: str = None, limit: int = None) -> List[Dict]:
        """
        تحميل بيانات من جدول
        
        Args:
            table (str): اسم الجدول
            condition (str): شرط البحث
            params (tuple): المعاملات
            order_by (str): ترتيب النتائج
            limit (int): حد النتائج
            
        Returns:
            List[Dict]: البيانات المحملة
        """
        query = f"SELECT * FROM `{table}`"
        
        if condition:
            query += f" WHERE {condition}"
        if order_by:
            query += f" ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit}"
        
        return self.استعلام(query, params)
    
    def احصل_على_معرف_جديد(self, table: str) -> int:
        """
        الحصول على معرف جديد للإدراج
        
        Args:
            table (str): اسم الجدول
            
        Returns:
            int: المعرف الجديد
        """
        result = self.استعلام(f"SELECT MAX(id) as max_id FROM `{table}`")
        if result and result[0]['max_id']:
            return result[0]['max_id'] + 1
        return 1
    
    def احصل_على_رقم_تسلسلي(self, prefix: str, table: str, field: str) -> str:
        """
        إنشاء رقم تسلسلي جديد
        
        Args:
            prefix (str): البادئة
            table (str): اسم الجدول
            field (str): اسم الحقل
            
        Returns:
            str: الرقم التسلسلي الجديد
        """
        current_year = datetime.now().year
        query = f"""
            SELECT MAX(CAST(SUBSTRING(`{field}`, LENGTH(%s) + 1) AS UNSIGNED)) as max_num
            FROM `{table}` 
            WHERE `{field}` LIKE %s AND YEAR(تاريخ_الإضافة) = %s
        """
        
        result = self.استعلام(query, (prefix, f"{prefix}%", current_year))
        
        if result and result[0]['max_num']:
            next_num = result[0]['max_num'] + 1
        else:
            next_num = 1
        
        return f"{prefix}{next_num:06d}"
    
    # ==================== إدارة المستخدمين والجلسات ====================
    
    def تسجيل_دخول(self, username: str, password: str) -> Dict:
        """
        تسجيل دخول المستخدم
        
        Args:
            username (str): اسم المستخدم
            password (str): كلمة المرور
            
        Returns:
            Dict: معلومات المستخدم أو رسالة خطأ
        """
        try:
            # تشفير كلمة المرور
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # البحث عن المستخدم
            user = self.استعلام("""
                SELECT u.*, e.اسم_الموظف, e.الوظيفة
                FROM المستخدمون u
                LEFT JOIN الموظفين e ON u.معرف_الموظف = e.id
                WHERE u.اسم_المستخدم = %s AND u.كلمة_المرور = %s AND u.الحالة = 'نشط'
            """, (username, hashed_password))
            
            if not user:
                return {'success': False, 'message': 'اسم المستخدم أو كلمة المرور غير صحيحة'}
            
            user_data = user[0]
            
            # إنشاء جلسة جديدة
            self.session_id = str(uuid.uuid4())
            self.current_user = user_data
            
            # تحديث آخر تسجيل دخول
            self.تحديث("""
                UPDATE المستخدمون 
                SET آخر_تسجيل_دخول = NOW(), معرف_الجلسة = %s
                WHERE id = %s
            """, (self.session_id, user_data['id']))
            
            # تسجيل النشاط
            self._تسجيل_نشاط('تسجيل_دخول', f"تسجيل دخول المستخدم: {username}")
            
            return {
                'success': True,
                'user': user_data,
                'session_id': self.session_id
            }
            
        except Exception as e:
            logger.error(f"خطأ في تسجيل الدخول: {e}")
            return {'success': False, 'message': 'خطأ في النظام'}
    
    def تسجيل_خروج(self) -> bool:
        """
        تسجيل خروج المستخدم
        
        Returns:
            bool: True إذا تم تسجيل الخروج بنجاح
        """
        try:
            if self.current_user:
                # تسجيل النشاط
                self._تسجيل_نشاط('تسجيل_خروج', f"تسجيل خروج المستخدم: {self.current_user['اسم_المستخدم']}")
                
                # مسح معرف الجلسة
                self.تحديث("""
                    UPDATE المستخدمون 
                    SET معرف_الجلسة = NULL
                    WHERE id = %s
                """, (self.current_user['id'],))
                
                self.current_user = None
                self.session_id = None
                
            return True
        except Exception as e:
            logger.error(f"خطأ في تسجيل الخروج: {e}")
            return False
    
    def التحقق_من_الصلاحية(self, permission: str) -> bool:
        """
        التحقق من صلاحية المستخدم
        
        Args:
            permission (str): اسم الصلاحية
            
        Returns:
            bool: True إذا كان المستخدم يملك الصلاحية
        """
        if not self.current_user:
            return False
        
        # المدير العام يملك جميع الصلاحيات
        if self.current_user.get('نوع_المستخدم') == 'مدير_عام':
            return True
        
        # التحقق من الصلاحيات المحددة
        permissions = self.استعلام("""
            SELECT COUNT(*) as count
            FROM صلاحيات_المستخدمين sp
            JOIN الصلاحيات p ON sp.معرف_الصلاحية = p.id
            WHERE sp.معرف_المستخدم = %s AND p.اسم_الصلاحية = %s AND sp.الحالة = 'نشط'
        """, (self.current_user['id'], permission))
        
        return permissions[0]['count'] > 0 if permissions else False
    
    # ==================== إدارة الإعدادات ====================
    
    def load_system_settings(self):
        """تحميل إعدادات النظام"""
        try:
            if self.انشاء_اتصال():
                settings = self.استعلام("SELECT المفتاح, القيمة, نوع_البيانات FROM إعدادات_النظام")
                for setting in settings:
                    key = setting['المفتاح']
                    value = setting['القيمة']
                    data_type = setting['نوع_البيانات']
                    
                    # تحويل القيمة حسب نوع البيانات
                    if data_type == 'number':
                        value = float(value) if '.' in value else int(value)
                    elif data_type == 'boolean':
                        value = value.lower() in ('true', '1', 'yes')
                    elif data_type == 'json':
                        value = json.loads(value) if value else {}
                    
                    self.settings[key] = value
        except Exception as e:
            logger.error(f"خطأ في تحميل الإعدادات: {e}")
    
    def احصل_على_إعداد(self, key: str, default=None):
        """
        الحصول على قيمة إعداد
        
        Args:
            key (str): مفتاح الإعداد
            default: القيمة الافتراضية
            
        Returns:
            القيمة المطلوبة أو القيمة الافتراضية
        """
        return self.settings.get(key, default)
    
    def تحديث_إعداد(self, key: str, value: Any) -> bool:
        """
        تحديث قيمة إعداد
        
        Args:
            key (str): مفتاح الإعداد
            value: القيمة الجديدة
            
        Returns:
            bool: True إذا تم التحديث بنجاح
        """
        try:
            # تحديد نوع البيانات
            if isinstance(value, bool):
                data_type = 'boolean'
                value_str = str(value).lower()
            elif isinstance(value, (int, float)):
                data_type = 'number'
                value_str = str(value)
            elif isinstance(value, (dict, list)):
                data_type = 'json'
                value_str = json.dumps(value, ensure_ascii=False)
            else:
                data_type = 'string'
                value_str = str(value)
            
            # تحديث في قاعدة البيانات
            success = self.تحديث("""
                UPDATE إعدادات_النظام 
                SET القيمة = %s, نوع_البيانات = %s, تاريخ_التحديث = NOW()
                WHERE المفتاح = %s
            """, (value_str, data_type, key))
            
            if success:
                self.settings[key] = value
                self._تسجيل_نشاط('تحديث_إعداد', f"تحديث الإعداد: {key}")
            
            return success
        except Exception as e:
            logger.error(f"خطأ في تحديث الإعداد: {e}")
            return False
    
    # ==================== تسجيل الأنشطة ====================
    
    def _تسجيل_نشاط(self, activity: str, description: str, table: str = None, record_id: int = None):
        """
        تسجيل نشاط في سجل الأنشطة
        
        Args:
            activity (str): نوع النشاط
            description (str): وصف النشاط
            table (str): اسم الجدول المتأثر
            record_id (int): معرف السجل المتأثر
        """
        try:
            user = self.current_user['اسم_المستخدم'] if self.current_user else 'نظام'
            
            self.تحديث("""
                INSERT INTO سجل_الأنشطة 
                (المستخدم, النشاط, الوصف, الجدول, معرف_السجل, التاريخ_والوقت)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (user, activity, description, table, record_id))
        except Exception as e:
            logger.error(f"خطأ في تسجيل النشاط: {e}")
    
    # ==================== إدارة المشاريع ====================
    
    def اضافة_مشروع(self, بيانات_المشروع: Dict) -> Dict:
        """
        إضافة مشروع جديد
        
        Args:
            بيانات_المشروع (Dict): بيانات المشروع
            
        Returns:
            Dict: نتيجة العملية
        """
        try:
            # التحقق من الصلاحية
            if not self.التحقق_من_الصلاحية('اضافة_مشروع'):
                return {'success': False, 'message': 'ليس لديك صلاحية لإضافة المشاريع'}
            
            # إنشاء رقم المشروع
            رقم_المشروع = self.احصل_على_رقم_تسلسلي(
                self.احصل_على_إعداد('project_prefix', 'PRJ-'),
                'المشاريع',
                'رقم_المشروع'
            )
            
            # إدراج المشروع
            query = """
                INSERT INTO المشاريع (
                    رقم_المشروع, القسم, معرف_التصنيف, معرف_العميل, معرف_المدير,
                    اسم_المشروع, الوصف, الموقع, المساحة, قيمة_العقد,
                    تاريخ_البداية, تاريخ_النهاية_المخطط, الحالة, الأولوية,
                    ملاحظات, المستخدم
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            
            params = (
                رقم_المشروع,
                بيانات_المشروع.get('القسم', 'المشاريع'),
                بيانات_المشروع.get('معرف_التصنيف'),
                بيانات_المشروع['معرف_العميل'],
                بيانات_المشروع.get('معرف_المدير'),
                بيانات_المشروع['اسم_��لمشروع'],
                بيانات_المشروع.get('الوصف'),
                بيانات_المشروع.get('الموقع'),
                بيانات_المشروع.get('المساحة', 0),
                بيانات_المشروع.get('قيمة_العقد', 0),
                بيانات_المشروع.get('تاريخ_البداية'),
                بيانات_المشروع.get('تاريخ_النهاية_المخطط'),
                بيانات_المشروع.get('الحالة', 'جديد'),
                بيانات_المشروع.get('الأولوية', 'متوسطة'),
                بيانات_المشروع.get('ملاحظات'),
                self.current_user['اسم_المستخدم'] if self.current_user else 'نظام'
            )
            
            if self.تحديث(query, params):
                # الحصول على معرف المشروع الجديد
                معرف_المشروع = self.cursor.lastrowid
                
                # تسجيل النشاط
                self._تسجيل_نشاط(
                    'اضافة_مشروع',
                    f"إضافة مشروع جديد: {بيانات_المشروع['اسم_المشروع']}",
                    'المشاريع',
                    معرف_المشروع
                )
                
                return {
                    'success': True,
                    'message': 'تم إضافة المشروع بنجاح',
                    'project_id': معرف_المشروع,
                    'project_number': رقم_المشروع
                }
            else:
                return {'success': False, 'message': 'فشل في إضافة المشروع'}
                
        except Exception as e:
            logger.error(f"خطأ في إضافة المشروع: {e}")
            return {'success': False, 'message': 'خطأ في النظام'}
    
    def تحديث_مشروع(self, معرف_المشروع: int, بيانات_جديدة: Dict) -> Dict:
        """
        تحديث بيانات مشروع
        
        Args:
            معرف_المشروع (int): معرف المشروع
            بيانات_جديدة (Dict): البيانات الجديدة
            
        Returns:
            Dict: نتيجة العملية
        """
        try:
            # التحقق من الصلاحية
            if not self.التحقق_من_الصلاحية('تحديث_مشروع'):
                return {'success': False, 'message': 'ليس لديك صلاحية لتحديث المشاريع'}
            
            # بناء استعلام التحديث
            set_clauses = []
            params = []
            
            updatable_fields = [
                'معرف_التصنيف', 'معرف_العميل', 'معرف_المدير', 'اسم_المشروع',
                'الوصف', 'الموقع', 'المساحة', 'قيمة_العقد', 'تاريخ_البداية',
                'تاريخ_النهاية_المخطط', 'الحالة', 'الأولوية', 'ملاحظات'
            ]
            
            for field in updatable_fields:
                if field in بيانات_جديدة:
                    set_clauses.append(f"`{field}` = %s")
                    params.append(بيانات_جديدة[field])
            
            if not set_clauses:
                return {'success': False, 'message': 'لا توجد بيانات للتحديث'}
            
            # إضافة معلومات التحديث
            set_clauses.append("`المستخدم` = %s")
            set_clauses.append("`تاريخ_التحديث` = NOW()")
            params.append(self.current_user['اسم_المستخدم'] if self.current_user else 'نظام')
            params.append(معرف_المشروع)
            
            query = f"""
                UPDATE المش��ريع 
                SET {', '.join(set_clauses)}
                WHERE id = %s
            """
            
            if self.تحديث(query, params):
                # تسج��ل النشاط
                self._تسجيل_نشاط(
                    'تحديث_مشروع',
                    f"تحديث المشروع رقم: {معرف_المشروع}",
                    'المشاريع',
                    معرف_المشروع
                )
                
                return {'success': True, 'message': 'تم تحديث المشروع بنجاح'}
            else:
                return {'success': False, 'message': 'فشل في تحديث المشروع'}
                
        except Exception as e:
            logger.error(f"خطأ في تحديث المشروع: {e}")
            return {'success': False, 'message': 'خطأ في النظام'}
    
    def احصل_على_مشاريع(self, filters: Dict = None, page: int = 1, per_page: int = 50) -> Dict:
        """
        الحصول على قائمة المشاريع مع الفلترة والترقيم
        
        Args:
            filters (Dict): فلاتر البحث
            page (int): رقم الصفحة
            per_page (int): عدد السجلات في الصفحة
            
        Returns:
            Dict: قائمة المشاريع والمعلومات الإضافية
        """
        try:
            # بناء شروط البحث
            where_clauses = []
            params = []
            
            if filters:
                if filters.get('الحالة'):
                    where_clauses.append("p.الحالة = %s")
                    params.append(filters['الحالة'])
                
                if filters.get('معرف_العميل'):
                    where_clauses.append("p.معرف_العميل = %s")
                    params.append(filters['معرف_العميل'])
                
                if filters.get('السنة'):
                    where_clauses.append("YEAR(p.تاريخ_البداية) = %s")
                    params.append(filters['السنة'])
                
                if filters.get('البحث'):
                    where_clauses.append("(p.اسم_المشروع LIKE %s OR p.رقم_المشروع LIKE %s)")
                    search_term = f"%{filters['البحث']}%"
                    params.extend([search_term, search_term])
            
            where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
            
            # حساب العدد الإجمالي
            count_query = f"""
                SELECT COUNT(*) as total
                FROM المشاريع p
                WHERE {where_clause}
            """
            
            total_result = self.استعلام(count_query, params)
            total_count = total_result[0]['total'] if total_result else 0
            
            # حساب الترقيم
            offset = (page - 1) * per_page
            
            # استعلام البيانات
            query = f"""
                SELECT 
                    p.*,
                    c.اسم_العميل,
                    e.اسم_الموظف as اسم_المدير,
                    cat.الاسم as اسم_التصنيف,
                    cat.اللون as لون_التصنيف
                FROM المشاريع p
                LEFT JOIN العملاء c ON p.معرف_العميل = c.id
                LEFT JOIN الموظفين e ON p.معرف_المدير = e.id
                LEFT JOIN التصنيفات cat ON p.معرف_التصنيف = cat.id
                WHERE {where_clause}
                ORDER BY p.تاريخ_الإضافة DESC
                LIMIT %s OFFSET %s
            """
            
            params.extend([per_page, offset])
            projects = self.استعلام(query, params)
            
            # حساب معلومات الترقيم
            total_pages = (total_count + per_page - 1) // per_page
            
            return {
                'success': True,
                'projects': projects,
                'pagination': {
                    'current_page': page,
                    'per_page': per_page,
                    'total_count': total_count,
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_prev': page > 1
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على المشاريع: {e}")
            return {'success': False, 'message': 'خطأ في النظام'}
    
    def احصل_على_مشروع(self, معرف_المشروع: int) -> Dict:
        """
        الحصول على تفاصيل مشروع محدد
        
        Args:
            معرف_المشروع (int): معرف المشروع
            
        Returns:
            Dict: تفاصيل المشروع
        """
        try:
            query = """
                SELECT 
                    p.*,
                    c.اسم_العميل, c.رقم_الهاتف as هاتف_العميل,
                    e.اسم_الموظف as اسم_المدير,
                    cat.الاسم as اسم_التصنيف, cat.اللون as لون_التصنيف
                FROM المشاريع p
                LEFT JOIN العملاء c ON p.معرف_العميل = c.id
                LEFT JOIN الموظف��ن e ON p.معرف_المدير = e.id
                LEFT JOIN التصنيفات cat ON p.معرف_التصنيف = cat.id
                WHERE p.id = %s
            """
            
            project = self.استعلام(query, (معرف_المشروع,))
            
            if not project:
                return {'success': False, 'message': 'المشروع غير موجود'}
            
            project_data = project[0]
            
            # الحصول على المراحل
            stages = self.استعلام("""
                SELECT * FROM المشاريع_المراحل 
                WHERE معرف_المشروع = %s 
                ORDER BY الترتيب, تاريخ_البداية
            """, (معرف_المشروع,))
            
            # الحصول على فريق العمل
            team = self.استعلام("""
                SELECT 
                    pt.*,
                    e.اسم_الموظف, e.الوظيفة
                FROM المشاريع_الفريق pt
                JOIN الموظفين e ON pt.معرف_الموظف = e.id
                WHERE pt.معرف_المرجع = %s AND pt.نوع_المهمة IN ('مشروع', 'مرحلة في مشروع')
                ORDER BY pt.تاريخ_الإضافة
            """, (��عرف_المشروع,))
            
            # الحصول على المدفوعات
            payments = self.استعلام("""
                SELECT * FROM المدفوعات 
                WHERE النوع = 'دفعة_مشروع' AND معرف_المرجع = %s
                ORDER BY تاريخ_الدفع DESC
            """, (معرف_المشروع,))
            
            # الحصول على المصروفات
            expenses = self.استعلام("""
                SELECT * FROM المصروفات 
                WHERE النوع = 'مصروف_مشروع' AND معرف_المرجع = %s
                ORDER BY تاريخ_المصروف DESC
            """, (معرف_المشروع,))
            
            return {
                'success': True,
                'project': project_data,
                'stages': stages,
                'team': team,
                'payments': payments,
                'expenses': expenses
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على المشروع: {e}")
            return {'success': False, 'message': 'خطأ في النظام'}
    
    # ==================== إدارة العملاء ====================
    
    def اضافة_عميل(self, بيانات_العمي��: Dict) -> Dict:
        """
        إضافة عميل جديد
        
        Args:
            بيانات_العميل (Dict): بيانات العميل
            
        Returns:
            Dict: نتيجة العملية
        """
        try:
            # التحقق من الصلاحية
            if not self.التحقق_من_الصلاحية('اضافة_عميل'):
                return {'success': False, 'message': 'ليس لديك صلاحية لإضافة العملاء'}
            
            # إنشاء رقم العميل
            رقم_العميل = self.احصل_على_رقم_تسلسلي(
                self.احصل_على_إعداد('customer_prefix', 'CUS-'),
                'العملاء',
                'رقم_العميل'
            )
            
            # إدراج العميل
            query = """
                INSERT INTO العملاء (
                    رقم_العميل, معرف_التصنيف, اسم_العميل, العنوان,
                    رقم_الهاتف, الايميل, تاريخ_الحساب, التقييم,
                    ملاحظات, المستخدم
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            
            params = (
                رقم_العميل,
                بيانات_العميل.get('معرف_التصنيف'),
                بيانات_العميل['اسم_العميل'],
                بيانات_العميل.get('العنوان'),
                بيانات_العميل.get('رقم_الهاتف'),
                بيانات_العميل.get('الايميل'),
                بيانات_العميل.get('تاريخ_الحساب', date.today()),
                بيانات_العميل.get('التقييم', 0),
                بيانات_العميل.get('ملاحظات'),
                self.current_user['اسم_المستخدم'] if self.current_user else 'نظام'
            )
            
            if self.تحديث(query, params):
                معرف_العميل = self.cursor.lastrowid
                
                # تسجيل النشاط
                self._تسجيل_نشاط(
                    'اضافة_عميل',
                    f"إضافة عميل جديد: {بيانات_العميل['اسم_العميل']}",
                    'العملاء',
                    معرف_العميل
                )
                
                return {
                    'success': True,
                    'message': 'تم إضافة العميل بنجاح',
                    'customer_id': معرف_العميل,
                    'customer_number': رقم_العميل
                }
            else:
                return {'success': False, 'message': 'فشل في إضافة العميل'}
                
        except Exception as e:
            logger.error(f"خطأ في إضافة العميل: {e}")
            return {'success': False, 'message': 'خطأ في النظام'}
    
    # ==================== إدارة الموظفين ====================
    
    def اضافة_موظف(self, بيانات_الموظف: Dict) -> Dict:
        """
        إضافة موظف جديد
        
        Args:
            بيانات_الموظف (Dict): بيانات الموظف
            
        Returns:
            Dict: نتيجة العملية
        """
        try:
            # التحقق من الصلاحية
            if not self.التحقق_من_الصلاحية('اضافة_موظف'):
                return {'success': False, 'message': 'ليس لديك صلاحية لإضافة الموظفين'}
            
            # إنشاء رقم الموظف
            رقم_الموظف = self.احصل_على_رقم_تسلسلي(
                self.احصل_على_إعداد('employee_prefix', 'EMP-'),
                'الموظفين',
                'رقم_الموظف'
            )
            
            # إدراج الموظف
            query = """
                INSERT INTO الموظفين (
                    رقم_الموظف, معرف_التصنيف, اسم_الموظف, العنوان,
                    رقم_الهاتف, الايميل, الوظيفة, تاريخ_التوظيف,
                    المرتب, نسبة_العمولة, الحالة, ملاحظات,
                    جدولة_المرتب_تلقائية, خاضع_لنظام_الحضور, المستخدم
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            
            params = (
                رقم_الموظف,
                بيانات_الموظف.get('معرف_التصنيف'),
                بيانات_الموظف['اسم_الموظف'],
                بيانات_الموظف.get('العنوان'),
                بيانات_الموظف.get('رقم_الهاتف'),
                بيانات_الموظف.get('الايميل'),
                بيانات_الموظف.get('الوظيفة'),
                بيانات_الموظف.get('تاريخ_التوظيف', date.today()),
                بيانات_الموظف.get('المرتب', 0),
                بيانات_الموظف.get('نسب��_العمولة', 0),
                بيانات_الموظف.get('الحالة', 'نشط'),
                بيانات_الموظف.get('ملاحظات'),
                بيانات_الموظف.get('جدولة_المرتب_تلقائية', False),
                بيانات_الموظف.get('خاضع_لنظام_الحضور', True),
                self.current_user['اسم_المستخدم'] if self.current_user else 'نظام'
            )
            
            if self.تحديث(query, params):
                معرف_الموظف = self.cursor.lastrowid
                
                # تسجيل النشاط
                self._تسجيل_نشاط(
                    'اضافة_موظف',
                    f"إضافة موظف جديد: {بيانات_الموظف['اسم_الموظف']}",
                    'الموظفين',
                    معرف_الموظف
                )
                
                return {
                    'success': True,
                    'message': 'تم إضافة الموظف بنجاح',
                    'employee_id': معرف_الموظف,
                    'employee_number': رقم_الموظف
                }
            else:
                return {'success': False, 'message': 'فشل في إضافة ال��وظف'}
                
        except Exception as e:
            logger.error(f"خطأ في إضافة الموظف: {e}")
            return {'success': False, 'message': 'خطأ في النظام'}
    
    # ==================== إدارة المالية والمحاسبة ====================
    
    def اضافة_قيد_محاسبي(self, بيانات_القيد: Dict) -> Dict:
        """
        إضافة قيد محاسبي جديد
        
        Args:
            بيانات_القيد (Dict): بيانات القيد المحاسبي
            
        Returns:
            Dict: نتيجة العملية
        """
        try:
            # التحقق من الصلاحية
            if not self.التحقق_من_الصلاحية('اضافة_قيد_محاسبي'):
                return {'success': False, 'message': 'ليس لديك صلاحية لإضافة القيود المحاسبية'}
            
            # التحقق من توازن القيد
            تفاصيل_القيد = بيانات_القيد.get('تفاصيل_القيد', [])
            if not تفاصيل_القيد:
                return {'success': False, 'message': 'يجب إضافة تفاصيل القيد'}
            
            إجمالي_المدين = sum(float(detail.get('المبلغ_المدين', 0)) for detail in تفاصيل_القيد)
            إجمالي_الدا��ن = sum(float(detail.get('المبلغ_الدائن', 0)) for detail in تفاصيل_القيد)
            
            if abs(إجمالي_المدين - إجمالي_الدائن) > 0.01:
                return {'success': False, 'message': 'القيد المحاسبي غير متوازن'}
            
            # إنشاء رقم القيد
            رقم_القيد = self.احصل_على_رقم_تسلسلي('JE-', 'القيود_المحاسبية', 'رقم_القيد')
            
            # بدء المعاملة
            self.connection.start_transaction()
            
            try:
                # إدراج القيد الرئيسي
                query_main = """
                    INSERT INTO القيود_المحاسبية (
                        رقم_القيد, تاريخ_القيد, نوع_القيد, مصدر_القيد,
                        البيان, إجمالي_المدين, إجمالي_الدائن, حالة_القيد,
                        معرف_المعاملة_الأصلية, نوع_المعاملة_الأصلية, المستخدم
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """
                
                params_main = (
                    رقم_القيد,
                    بيانات_القيد.get('تاريخ_القيد', date.today()),
                    بيانات_القيد.get('نوع_القيد', 'يومي'),
                    بيانات_القيد.get('مصدر_القيد', 'يدوي'),
                    بيانات_القيد['البيان'],
                    إجمالي_المدين,
                    إجمالي_الدائن,
                    بيانات_القيد.get('حالة_القيد', 'مسودة'),
                    بيانات_القيد.get('معرف_المعاملة_الأصلية'),
                    بيانات_القيد.get('نوع_المعاملة_الأصلية'),
                    self.current_user['اسم_المستخدم'] if self.current_user else 'نظام'
                )
                
                self.cursor.execute(query_main, params_main)
                معرف_القيد = self.cursor.lastrowid
                
                # إدراج تفاصيل القيد
                query_detail = """
                    INSERT INTO تفاصيل_القيود (
                        معرف_القيد, معرف_الحساب, المبلغ_المدين, المبلغ_الدائن,
                        البيان, مركز_التكلفة, المشروع, العملة, سعر_الصرف,
                        المبلغ_بالعملة_الأجنبية, الترتيب
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """
                
                for i, detail in enumerate(تفاصيل_القيد):
                    params_detail = (
                        معرف_القيد,
                        detail['معرف_الحساب'],
                        detail.get('المبلغ_المدين', 0),
                        detail.get('المبلغ_الدائن', 0),
                        detail.get('البيان'),
                        detail.get('مركز_التكلفة'),
                        detail.get('المشروع'),
                        detail.get('العملة', 'SAR'),
                        detail.get('سعر_الصرف', 1),
                        detail.get('المبلغ_بالعملة_الأجنبية'),
                        i + 1
                    )
                    
                    self.cursor.execute(query_detail, params_detail)
                
                # تأكيد المعاملة
                self.connection.commit()
                
                # تسجيل النشاط
                self._تسجيل_نشاط(
                    'اضافة_قيد_محاسبي',
                    f"إضافة قيد محاسبي: {رقم_القيد}",
                    'القيود_المحاسبية',
                    معرف_القيد
                )
                
                return {
                    'success': True,
                    'message': 'تم إضافة القيد المحاسبي بنجاح',
                    'journal_id': معرف_القيد,
                    'journal_number': رقم_القيد
                }
                
            except Exception as e:
                self.connection.rollback()
                raise e
                
        except Exception as e:
            logger.error(f"خطأ في إضافة القيد المحاسبي: {e}")
            return {'success': False, 'message': 'خطأ في النظام'}
    
    # ==================== التقارير والإحصائيات ====================
    
    def تقرير_المشاريع_حسب_الحالة(self, السنة: int = None) -> Dict:
        """
        تقرير المشاريع حسب الحالة
        
        Args:
            السنة (int): السنة المطلوبة (افتراضي: السنة الحالية)
            
        Returns:
            Dict: تقرير المشاريع
        """
        try:
            if السنة is None:
                ا��سنة = datetime.now().year
            
            query = """
                SELECT 
                    الحالة,
                    COUNT(*) as عدد_المشاريع,
                    SUM(قيمة_العقد) as إجمالي_القيمة,
                    SUM(المدفوع) as إجمالي_المدفوع,
                    SUM(قيمة_العقد - المدفوع) as إجمالي_المتبقي
                FROM المشاريع
                WHERE YEAR(تاريخ_البداية) = %s
                GROUP BY الحالة
                ORDER BY عدد_المشاريع DESC
            """
            
            results = self.استعلام(query, (السنة,))
            
            # حساب الإجماليات
            إجمالي_المشاريع = sum(row['عدد_المشاريع'] for row in results)
            إجمالي_القيمة = sum(row['إجمالي_القيمة'] or 0 for row in results)
            إجمالي_المدفوع = sum(row['إجمالي_المدفوع'] or 0 for row in results)
            
            return {
                'success': True,
                'year': السنة,
                'data': results,
                'summary': {
                    'إجمالي_المشاريع': إجمالي_المشاريع,
                    'إجمالي_القيمة': إجمالي_القيمة,
                    'إجمالي_المدفوع': إجمالي_المدفوع,
                    'إجمالي_المتبقي': إجمالي_القيمة - إجمالي_المدفوع
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في تقرير المشاريع: {e}")
            return {'success': False, 'message': 'خطأ في النظام'}
    
    def تقرير_الإيرادات_الشهرية(self, السنة: int = None) -> Dict:
        """
        تقرير الإيرادات الشهرية
        
        Args:
            السنة (int): السنة المطلوبة
            
        Returns:
            Dict: تقرير الإيرادات
        """
        try:
            if السنة is None:
                السنة = datetime.now().year
            
            query = """
                SELECT 
                    MONTH(تاريخ_الدفع) as الشهر,
                    MONTHNAME(تاريخ_الدفع) as اسم_الشهر,
                    SUM(صافي_المبلغ) as إجمالي_الإيرادات,
                    COUNT(*) as عدد_المدفوعات
                FROM المدفوعات
                WHERE YEAR(تاريخ_الدفع) = %s 
                AND النوع IN ('دفعة_مشروع', 'دفعة_تدريب')
                GROUP BY MONTH(تاريخ_الدفع)
                ORDER BY الشهر
            """
            
            results = self.استعلام(query, (السنة,))
            
            # إنشاء بيانات لجميع الشهور
            monthly_data = {}
            for i in range(1, 13):
                monthly_data[i] = {
                    'الشهر': i,
                    'اسم_الشهر': datetime(2000, i, 1).strftime('%B'),
                    'إجمالي_الإيرادات': 0,
                    'عدد_المدفوعات': 0
                }
            
            # تحديث البيانات الموجودة
            for row in results:
                monthly_data[row['الشهر']] = row
            
            # تحويل إلى قائمة
            final_data = list(monthly_data.values())
            
            # حساب الإجماليات
            إجمالي_الإيرادات = sum(row['إجمالي_الإيرادات'] or 0 for row in final_data)
            إجمالي_المدفوعات = sum(row['عدد_المدفوعات'] or 0 for row in final_data)
            
            return {
                'success': True,
                'year': السنة,
                'data': final_data,
                'summary': {
                    'إجمالي_الإيرادات': إجمالي_الإيرادات,
                    'إجمالي_المدفوعات': إجمالي_المدفوعات,
                    'متوسط_الإيرادات_الشهرية': إجمالي_الإيرادات / 12
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في تقرير الإيرادات: {e}")
            return {'success': False, 'message': 'خطأ في النظام'}
    
    # ==================== أدوات مساعدة ====================
    
    def نسخ_احتياطي(self, مسار_الحفظ: str = None) -> Dict:
        """
        إنشاء نسخة احتياطية من قاعدة البيانات
        
        Args:
            مسار_الحفظ (str): مسار حفظ النسخة الاحتياطية
            
        Returns:
            Dict: نتيجة العملية
        """
        try:
            if not مسار_الحفظ:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                مسار_الحفظ = f"backup_{self.db_name}_{timestamp}.sql"
            
            # تنفيذ أمر النسخ الاحتياطي
            import subprocess
            
            command = [
                'mysqldump',
                f'--host={self.host}',
                f'--user={self.user}',
                f'--password={self.password}',
                '--single-transaction',
                '--routines',
                '--triggers',
                self.db_name
            ]
            
            with open(مسار_الحفظ, 'w', encoding='utf-8') as f:
                result = subprocess.run(command, stdout=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                # تسجيل النشاط
                self._تسجيل_نشاط('نسخ_احتياطي', f"إنشاء نسخة احتياطية: {مسار_الحفظ}")
                
                return {
                    'success': True,
                    'message': 'تم إنشاء النسخة الاحتياطية بنجاح',
                    'backup_path': مسار_الحفظ
                }
            else:
                return {
                    'success': False,
                    'message': f'فشل في إنشاء النسخة الاحتياطية: {result.stderr}'
                }
                
        except Exception as e:
            logger.error(f"خطأ في النسخ الاحتياطي: {e}")
            return {'success': False, 'message': 'خطأ في النظام'}
    
    def تحقق_من_سلامة_البيانات(self) -> Dict:
        """
        التحقق من سلامة البيانات في قاعدة البيانات
        
        Returns:
            Dict: تقرير سلامة البيانات
        """
        try:
            issues = []
            
            # التحقق من المشاريع بدون عملاء
            orphaned_projects = self.استعلام("""
                SELECT COUNT(*) as count FROM المشاريع p
                LEFT JOIN العملاء c ON p.معرف_العميل = c.id
                WHERE c.id IS NULL
            """)
            
            if orphaned_projects[0]['count'] > 0:
                issues.append({
                    'type': 'مشاريع_بدون_عملاء',
                    'count': orphaned_projects[0]['count'],
                    'description': 'مشاريع مرتبطة بعملاء غير موجودين'
                })
            
            # التحقق من القيود المحاسبية غير المتوازنة
            unbalanced_entries = self.استعلام("""
                SELECT COUNT(*) as count FROM القيود_المحاسبية
                WHERE ABS(إجمالي_المدين - إجمالي_الدائن) > 0.01
            """)
            
            if unbalanced_entries[0]['count'] > 0:
                issues.append({
                    'type': 'قيود_غير_متوازنة',
                    'count': unbalanced_entries[0]['count'],
                    'description': 'قيود محاسبية غير متوازنة'
                })
            
            # التحقق من المدفوعات بدون مراجع
            orphaned_payments = self.استعلام("""
                SELECT COUNT(*) as count FROM المدفوعات p
                WHERE (p.النوع = 'دفعة_مشروع' AND NOT EXISTS (
                    SELECT 1 FROM المشاريع pr WHERE pr.id = p.معرف_المرجع
                ))
            """)
            
            if orphaned_payments[0]['count'] > 0:
                issues.append({
                    'type': 'مدفوعات_بدون_مراجع',
                    'count': orphaned_payments[0]['count'],
                    'description': 'مدفوعات مرتبطة بمراجع غير موجودة'
                })
            
            return {
                'success': True,
                'issues_count': len(issues),
                'issues': issues,
                'status': 'سليم' if not issues else 'يحتاج_مراجعة'
            }
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من سلامة البيانات: {e}")
            return {'success': False, 'message': 'خطأ في النظام'}
    
    def __del__(self):
        """تنظيف الموارد عند حذف الكائن"""
        self.اغلاق_اتصال()


# ==================== دوال مساعدة خارجية ====================

def انشاء_منظومة_جديدة(host='localhost', user='root', password='kh123456') -> 'منظومة_المهندس_v3':
    """
    إنشاء منظومة جديدة مع إعداد قاعدة البيانات
    
    Args:
        host (str): عنوان الخادم
        user (str): اسم المستخدم
        password (str): كلمة المرور
        
    Returns:
        منظومة_المهندس_v3: كائن المنظومة
    """
    try:
        # إنشاء كائن المنظومة
        منظومة = منظومة_المهندس_v3(host, user, password)
        
        # إنشاء قاعدة البيانات إذا لم تكن موجودة
        from منظومة_المهندس_v3_database import انشاء_قاعدة_البيانات_الكاملة
        
        success = انشاء_قاعدة_البيانات_الكاملة(host, user, password, منظومة.db_name)
        
        if success:
            logger.info("تم إنشاء المنظومة بنجاح")
            return منظومة
        else:
            logger.error("فشل في إنشاء قاعدة البيانات")
            return None
            
    except Exception as e:
        logger.error(f"خطأ في إنشاء المنظومة: {e}")
        return None


# ==================== مثال على الاستخدام ====================

if __name__ == "__main__":
    # إنشاء منظومة جديدة
    منظومة = انشاء_منظومة_جديدة()
    
    if منظومة:
        print("تم إنشاء منظومة المهندس v3 بنجاح!")
        
        # مثال على تسجيل الدخول
        نتيجة_الدخول = منظومة.تسجيل_دخول('admin', 'admin123')
        if نتيجة_الدخول['success']:
            print(f"مرحباً {نتيجة_الدخول['user']['اسم_المستخدم']}")
            
            # مثال على إضافة عميل
            بيانات_عميل = {
                'اسم_العميل': 'شركة الأمل للمقاولات',
                'رقم_الهاتف': '0501234567',
                'الايميل': 'info@alamal.com',
                'العنوان': 'الرياض، المملكة العربية السعودية'
            }
            
            نتيجة_العميل = منظومة.اضافة_عميل(بيانات_عميل)
            if نتيجة_العميل['success']:
                print(f"تم إضافة العميل برقم: {نتيجة_العميل['customer_number']}")
            
            # مثال على إضافة مشروع
            بيانات_مشروع = {
                'معرف_العميل': نتيجة_العميل['customer_id'],
                'اسم_المشروع': 'تصميم فيلا سكنية',
                'الوصف': 'تصميم معماري وإنشائي لفيلا سكنية',
                'الموقع': 'الرياض',
                'المساحة': 500.0,
                'قيمة_العقد': 150000.0,
                'تاريخ_البداية': date.today(),
                'تاريخ_النهاية_المخطط': date.today() + timedelta(days=90)
            }
            
            نتيجة_المشروع = منظومة.اضافة_مشروع(بيانات_مشروع)
            if نتيجة_المشروع['success']:
                print(f"تم إضافة المشروع برقم: {نتيجة_المشروع['project_number']}")
            
            # مثال على التقارير
            تقرير_المشاريع = منظومة.تقرير_المشاريع_حسب_الحالة()
            if تقرير_الم��اريع['success']:
                print("تقرير المشاريع:")
                for حالة in تقرير_المشاريع['data']:
                    print(f"  {حالة['الحالة']}: {حالة['عدد_المشاريع']} مشروع")
        
        # تسجيل الخروج
        منظومة.تسجيل_خروج()
        print("تم تسجيل الخروج بنجاح")
    else:
        print("فشل في إنشاء المنظومة")