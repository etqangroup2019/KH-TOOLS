#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
الكلاس الأساسي لجميع وحدات النظام
يوفر الوظائف المشتركة والواجهة الموحدة
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
from .database import DatabaseManager

logger = logging.getLogger(__name__)

class BaseModule(ABC):
    """
    الكلاس الأساسي لجميع وحدات النظام
    يوفر الوظائف المشتركة والواجهة الموحدة
    """
    
    def __init__(self, db_manager: DatabaseManager, module_name: str):
        """
        تهيئة الوحدة الأساسية
        
        Args:
            db_manager: مدير قاعدة البيانات
            module_name: اسم الوحدة
        """
        self.db = db_manager
        self.module_name = module_name
        self.tables = []  # قائمة الجداول التي تديرها الوحدة
        self.created_tables = set()
        
        logger.info(f"تم تهيئة وحدة {module_name}")
    
    @abstractmethod
    def create_tables(self) -> bool:
        """
        إنشاء جداول الوحدة
        يجب تنفيذها في كل وحدة فرعية
        
        Returns:
            True إذا تم الإنشاء بنجاح
        """
        pass
    
    @abstractmethod
    def get_module_info(self) -> Dict[str, Any]:
        """
        الحصول على معلومات الوحدة
        يجب تنفيذها في كل وحدة فرعية
        
        Returns:
            معلومات الوحدة
        """
        pass
    
    def insert_record(self, table: str, data: Dict[str, Any]) -> Optional[int]:
        """
        إدراج سجل جديد
        
        Args:
            table: اسم الجدول
            data: البيانات
            
        Returns:
            معرف السجل الجديد
        """
        try:
            # إضافة بيانات التتبع
            if 'تاريخ_الإضافة' not in data:
                data['تاريخ_الإضافة'] = datetime.now()
            
            if 'المستخدم' not in data:
                data['المستخدم'] = 'system'
            
            return self.db.insert_data(table, data)
            
        except Exception as e:
            logger.error(f"خطأ في إدراج السجل في {table}: {e}")
            return None
    
    def update_record(self, table: str, data: Dict[str, Any], record_id: int) -> bool:
        """
        تحديث سجل موجود
        
        Args:
            table: اسم الجدول
            data: البيانات الجديدة
            record_id: معرف السجل
            
        Returns:
            True إذا تم التحديث بنجاح
        """
        try:
            # إضافة تاريخ التحديث
            data['تاريخ_التحديث'] = datetime.now()
            
            return self.db.update_data(table, data, "id = %s", (record_id,))
            
        except Exception as e:
            logger.error(f"خطأ في تحديث السجل في {table}: {e}")
            return False
    
    def delete_record(self, table: str, record_id: int) -> bool:
        """
        حذف سجل
        
        Args:
            table: اسم الجدول
            record_id: معرف السجل
            
        Returns:
            True إذا تم الحذف بنجاح
        """
        try:
            return self.db.delete_data(table, "id = %s", (record_id,))
            
        except Exception as e:
            logger.error(f"خطأ في حذف السجل من {table}: {e}")
            return False
    
    def get_record(self, table: str, record_id: int) -> Optional[Dict[str, Any]]:
        """
        الحصول على سجل واحد
        
        Args:
            table: اسم الجدول
            record_id: معرف السجل
            
        Returns:
            بيانات السجل أو None
        """
        try:
            results = self.db.fetch_data(table, "*", "id = %s", (record_id,))
            return results[0] if results else None
            
        except Exception as e:
            logger.error(f"خطأ في جلب السجل من {table}: {e}")
            return None
    
    def get_records(self, table: str, where_clause: str = None, where_params: tuple = None,
                   order_by: str = None, limit: int = None) -> List[Dict[str, Any]]:
        """
        الحصول على عدة سجلات
        
        Args:
            table: اسم الجدول
            where_clause: شرط البحث
            where_params: معاملات الشرط
            order_by: ترتيب النتائج
            limit: حد النتائج
            
        Returns:
            قائمة السجلات
        """
        try:
            return self.db.fetch_data(table, "*", where_clause, where_params, order_by, limit)
            
        except Exception as e:
            logger.error(f"خطأ في جلب السجلات من {table}: {e}")
            return []
    
    def count_records(self, table: str, where_clause: str = None, where_params: tuple = None) -> int:
        """
        عد السجلات
        
        Args:
            table: اسم الجدول
            where_clause: شرط البحث
            where_params: معاملات الشرط
            
        Returns:
            عدد السجلات
        """
        try:
            results = self.db.fetch_data(table, "COUNT(*) as count", where_clause, where_params)
            return results[0]['count'] if results else 0
            
        except Exception as e:
            logger.error(f"خطأ في عد السجلات من {table}: {e}")
            return 0
    
    def execute_custom_query(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        تنفيذ استعلام مخصص
        
        Args:
            sql: الاستعلام
            params: المعاملات
            
        Returns:
            النتائج
        """
        try:
            self.db.cursor.execute(sql, params or ())
            
            # الحصول على أسماء الأعمدة
            column_names = [desc[0] for desc in self.db.cursor.description]
            
            # تحويل النتائج إلى قواميس
            results = []
            for row in self.db.cursor.fetchall():
                results.append(dict(zip(column_names, row)))
            
            return results
            
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الاستعلام المخصص: {e}")
            return []
    
    def generate_number(self, prefix: str, table: str, field: str, year: int = None) -> str:
        """
        توليد رقم تسلسلي
        
        Args:
            prefix: البادئة
            table: اسم الجدول
            field: اسم الحقل
            year: السنة (اختياري)
            
        Returns:
            الرقم المولد
        """
        try:
            if year is None:
                year = datetime.now().year
            
            # البحث عن آخر رقم
            sql = f"SELECT MAX(CAST(SUBSTRING(`{field}`, LENGTH('{prefix}-{year}-') + 1) AS UNSIGNED)) as max_num FROM `{table}` WHERE `{field}` LIKE '{prefix}-{year}-%'"
            results = self.execute_custom_query(sql)
            
            max_num = results[0]['max_num'] if results and results[0]['max_num'] else 0
            new_num = max_num + 1
            
            return f"{prefix}-{year}-{new_num:06d}"
            
        except Exception as e:
            logger.error(f"خطأ في توليد الرقم: {e}")
            return f"{prefix}-{year}-000001"
    
    def validate_data(self, data: Dict[str, Any], required_fields: List[str]) -> tuple[bool, str]:
        """
        التحقق من صحة البيانات
        
        Args:
            data: البيانات
            required_fields: الحقول المطلوبة
            
        Returns:
            (صحيح/خطأ, رسالة الخطأ)
        """
        try:
            # التحقق من الحقول المطلوبة
            for field in required_fields:
                if field not in data or data[field] is None or data[field] == '':
                    return False, f"الحقل '{field}' مطلوب"
            
            return True, ""
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من البيانات: {e}")
            return False, str(e)
    
    def log_operation(self, operation: str, table: str, record_id: int = None, details: str = None):
        """
        تسجيل العملية في السجل
        
        Args:
            operation: نوع العملية
            table: اسم الجدول
            record_id: معرف السجل
            details: تفاصيل إضافية
        """
        try:
            log_data = {
                'الوحدة': self.module_name,
                'العملية': operation,
                'الجدول': table,
                'معرف_السجل': record_id,
                'التفاصيل': details,
                'التاريخ': datetime.now(),
                'المستخدم': 'system'
            }
            
            # محاولة إدراج في جدول السجلات إذا كان موجوداً
            try:
                self.db.insert_data('سجلات_النظام', log_data)
            except:
                # إذا لم يكن الجدول موجوداً، نسجل في logger فقط
                logger.info(f"عملية {operation} على {table} - السجل: {record_id}")
                
        except Exception as e:
            logger.error(f"خطأ في تسجيل العملية: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        الحصول على إحصائيات الوحدة
        
        Returns:
            إحصائيات الوحدة
        """
        try:
            stats = {
                'اسم_الوحدة': self.module_name,
                'عدد_الجداول': len(self.tables),
                'الجداول': self.tables,
                'تاريخ_الإحصائيات': datetime.now().isoformat()
            }
            
            # إضافة إحصائيات كل جدول
            for table in self.tables:
                try:
                    count = self.count_records(table)
                    stats[f'عدد_سجلات_{table}'] = count
                except:
                    stats[f'عدد_سجلات_{table}'] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"خطأ في حساب الإحصائيات: {e}")
            return {'خطأ': str(e)}
    
    def backup_module_data(self, backup_path: str) -> bool:
        """
        نسخ احتياطي لبيانات الوحدة
        
        Args:
            backup_path: مسار النسخة الاحتياطية
            
        Returns:
            True إذا تم النسخ بنجاح
        """
        try:
            # سيتم تنفيذها في الوحدات الفرعية حسب الحاجة
            logger.info(f"نسخ احتياطي لوحدة {self.module_name}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في النسخ الاحتياطي: {e}")
            return False