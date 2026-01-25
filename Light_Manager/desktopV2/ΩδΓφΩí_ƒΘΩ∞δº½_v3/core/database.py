#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مدير قاعدة البيانات الأساسي
يوفر الاتصال وإدارة قاعدة البيانات لجميع الوحدات
"""

import mysql.connector
from mysql.connector import Error
from typing import Optional, Dict, List, Tuple, Any, Union
import logging
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    مدير قاعدة البيانات الأساسي
    يوفر جميع العمليات الأساسية لقاعدة البيانات
    """
    
    def __init__(self, host="localhost", user="root", password="kh123456", database="منظومة_المهندس_v3"):
        """
        تهيئة مدير قاعدة البيانات
        
        Args:
            host: عنوان الخادم
            user: اسم المستخدم
            password: كلمة المرور
            database: اسم قاعدة البيانات
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
        
        # إعدادات النظام
        self.encoding = 'utf8mb4'
        self.collation = 'utf8mb4_unicode_ci'
        
        logger.info(f"تم تهيئة مدير قاعدة البيانات - قاعدة البيانات: {database}")
    
    def connect(self) -> bool:
        """
        إنشاء اتصال جديد بقاعدة البيانات
        
        Returns:
            True إذا تم الاتصال بنجاح
        """
        try:
            # الاتصال بدون تحديد قاعدة البيانات أولاً
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                charset=self.encoding,
                collation=self.collation,
                autocommit=False
            )
            
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(buffered=True)
                logger.info("تم إنشاء الاتصال بقاعدة البيانات بنجاح")
                return True
            
        except Error as e:
            logger.error(f"خطأ في إنشاء الاتصال: {e}")
            return False
        
        return False
    
    def disconnect(self):
        """إغلاق الاتصال بقاعدة البيانات"""
        try:
            if self.cursor:
                self.cursor.close()
                self.cursor = None
            
            if self.connection and self.connection.is_connected():
                self.connection.close()
                self.connection = None
                
            logger.info("تم إغلاق الاتصال بقاعدة البيانات")
            
        except Error as e:
            logger.error(f"خطأ في إغلاق الاتصال: {e}")
    
    def close_connection(self):
        """alias لـ disconnect"""
        self.disconnect()
    
    def is_connected(self) -> bool:
        """
        فحص حالة الاتصال
        
        Returns:
            True إذا كان الاتصال نشطاً
        """
        try:
            if self.connection and self.connection.is_connected():
                self.connection.ping(reconnect=True, attempts=3, delay=1)
                return True
        except:
            pass
        return False
    
    def reconnect(self) -> bool:
        """
        إعادة الاتصال في حالة انقطاعه
        
        Returns:
            True إذا تم إعادة الاتصال بنجاح
        """
        self.disconnect()
        return self.connect()
    
    def create_database(self) -> bool:
        """
        إنشاء قاعدة البيانات إذا لم تكن موجودة
        
        Returns:
            True إذا تم الإنشاء بنجاح
        """
        try:
            if not self.connect():
                return False
            
            # إنشاء قاعدة البيانات
            create_db_sql = f"""
                CREATE DATABASE IF NOT EXISTS `{self.database}` 
                CHARACTER SET {self.encoding} 
                COLLATE {self.collation}
            """
            
            self.cursor.execute(create_db_sql)
            self.cursor.execute(f"USE `{self.database}`")
            self.connection.commit()
            
            logger.info(f"تم إنشاء/استخدام قاعدة البيانات: {self.database}")
            return True
            
        except Error as e:
            logger.error(f"خطأ في إنشاء قاعدة البيانات: {e}")
            return False
    
    def execute_query(self, sql: str, params: tuple = None, fetch: bool = False) -> Any:
        """
        تنفيذ استعلام SQL
        
        Args:
            sql: الاستعلام
            params: معاملات الاستعلام
            fetch: هل نريد استرجاع النتائج
            
        Returns:
            النتائج إذا كان fetch=True
        """
        try:
            if not self.is_connected():
                if not self.reconnect():
                    raise Exception("فشل في إعادة الاتصال بقاعدة البيانات")
            
            self.cursor.execute(sql, params or ())
            
            if fetch:
                if sql.strip().upper().startswith('SELECT'):
                    return self.cursor.fetchall()
                else:
                    return self.cursor.rowcount
            
            return True
            
        except Error as e:
            logger.error(f"خطأ في تنفيذ الاستعلام: {e}")
            logger.debug(f"الاستعلام: {sql}")
            if params:
                logger.debug(f"المعاملات: {params}")
            raise
    
    def insert_data(self, table: str, data: Dict[str, Any]) -> Optional[int]:
        """
        إدراج بيانات جديدة في جدول
        
        Args:
            table: اسم الجدول
            data: البيانات المراد إدراجها
            
        Returns:
            معرف السجل الجديد أو None
        """
        try:
            if not data:
                return None
            
            # بناء استعلام الإدراج
            columns = ", ".join([f"`{key}`" for key in data.keys()])
            placeholders = ", ".join(["%s"] * len(data))
            sql = f"INSERT INTO `{table}` ({columns}) VALUES ({placeholders})"
            
            self.execute_query(sql, tuple(data.values()))
            self.connection.commit()
            
            # الحصول على معرف السجل الجديد
            new_id = self.cursor.lastrowid
            
            logger.info(f"تم إدراج بيانات جديدة في جدول {table} - المعرف: {new_id}")
            return new_id
            
        except Exception as e:
            logger.error(f"خطأ في إدراج البيانات: {e}")
            self.connection.rollback()
            return None
    
    def update_data(self, table: str, data: Dict[str, Any], where_clause: str, where_params: tuple = None) -> bool:
        """
        تحديث البيانات في جدول
        
        Args:
            table: اسم الجدول
            data: البيانات المراد تحديثها
            where_clause: شرط التحديث
            where_params: معاملات الشرط
            
        Returns:
            True إذا تم التحديث بنجاح
        """
        try:
            if not data:
                return False
            
            # بناء استعلام التحديث
            set_clause = ", ".join([f"`{key}` = %s" for key in data.keys()])
            sql = f"UPDATE `{table}` SET {set_clause} WHERE {where_clause}"
            
            # تجميع المعاملات
            params = list(data.values())
            if where_params:
                params.extend(where_params)
            
            self.execute_query(sql, tuple(params))
            self.connection.commit()
            
            logger.info(f"تم تحديث البيانات في جدول {table}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحديث البيانات: {e}")
            self.connection.rollback()
            return False
    
    def delete_data(self, table: str, where_clause: str, where_params: tuple = None) -> bool:
        """
        حذف البيانات من جدول
        
        Args:
            table: اسم الجدول
            where_clause: شرط الحذف
            where_params: معاملات الشرط
            
        Returns:
            True إذا تم الحذف بنجاح
        """
        try:
            sql = f"DELETE FROM `{table}` WHERE {where_clause}"
            self.execute_query(sql, where_params)
            self.connection.commit()
            
            logger.info(f"تم حذف البيانات من جدول {table}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في حذف البيانات: {e}")
            self.connection.rollback()
            return False
    
    def fetch_data(self, table: str, columns: str = "*", where_clause: str = None, 
                   where_params: tuple = None, order_by: str = None, limit: int = None) -> List[Dict]:
        """
        تحميل البيانات من جدول
        
        Args:
            table: اسم الجدول
            columns: الأعمدة المطلوبة
            where_clause: شرط الاستعلام
            where_params: معاملات الشرط
            order_by: ترتيب النتائج
            limit: حد النتائج
            
        Returns:
            قائمة بالنتائج
        """
        try:
            sql = f"SELECT {columns} FROM `{table}`"
            
            if where_clause:
                sql += f" WHERE {where_clause}"
            
            if order_by:
                sql += f" ORDER BY {order_by}"
            
            if limit:
                sql += f" LIMIT {limit}"
            
            self.cursor.execute(sql, where_params or ())
            
            # الحصول على أسماء الأعمدة
            column_names = [desc[0] for desc in self.cursor.description]
            
            # تحويل النتائج إلى قواميس
            results = []
            for row in self.cursor.fetchall():
                results.append(dict(zip(column_names, row)))
            
            return results
            
        except Exception as e:
            logger.error(f"خطأ في تحميل البيانات: {e}")
            return []
    
    def commit(self):
        """تأكيد المعاملة"""
        if self.connection:
            self.connection.commit()
    
    def rollback(self):
        """إلغاء المعاملة"""
        if self.connection:
            self.connection.rollback()
    
    def __enter__(self):
        """دعم context manager"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """إغلاق الاتصال عند الخروج"""
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.disconnect()