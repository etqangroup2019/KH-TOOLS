#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نظام المحاسبة الشامل - منظومة المهندس v3
نظام محاسبي متكامل وقابل للتوسع مع دعم كامل للغة العربية
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime, date
from typing import Optional, Dict, List, Tuple, Any, Union
import logging
import json
import hashlib
from decimal import Decimal
import os
from pathlib import Path

# إعداد نظام السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('accounting_system.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class نظام_المحاسبة_الشامل:
    """
    نظام المحاسبة الشامل - الكلاس الرئيسي
    يوفر إدارة شاملة لقاعدة البيانات المحاسبية مع دعم التوسع المستقبلي
    """
    
    def __init__(self, host="localhost", user="root", password="kh123456", database="منظومة_المهندس_v3"):
        """
        تهيئة النظام المحاسبي
        
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
        
        # متغيرات التتبع
        self.tables_created = set()
        self.indexes_created = set()
        self.triggers_created = set()
        
        logger.info(f"تم تهيئة نظام المحاسبة الشامل - قاعدة البيانات: {database}")
    
    # ==================== دوال الاتصال الأساسية ====================
    
    def انشاء_اتصال(self) -> bool:
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
    
    def اغلاق_اتصال(self):
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
    
    def فحص_الاتصال(self) -> bool:
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
    
    def اعادة_الاتصال(self) -> bool:
        """
        إعادة الاتصال في حالة انقطاعه
        
        Returns:
            True إذا تم إعادة الاتصال بنجاح
        """
        self.اغلاق_اتصال()
        return self.انشاء_اتصال()
    
    # ==================== دوال قاعدة البيانات الأساسية ====================
    
    def انشاء_قاعدة_البيانات(self) -> bool:
        """
        إنشاء قاعدة البيانات إذا لم تكن موجودة
        
        Returns:
            True إذا تم الإنشاء بنجاح
        """
        try:
            if not self.انشاء_اتصال():
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
    
    def تنفيذ_استعلام(self, sql: str, params: tuple = None, fetch: bool = False) -> Any:
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
            if not self.فحص_الاتصال():
                if not self.اعادة_الاتصال():
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
    
    def تحديث_بيانات(self, table: str, data: Dict[str, Any], where_clause: str, where_params: tuple = None) -> bool:
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
            
            self.تنفيذ_استعلام(sql, tuple(params))
            self.connection.commit()
            
            logger.info(f"تم تحديث البيانات في جدول {table}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحديث البيانات: {e}")
            self.connection.rollback()
            return False
    
    def حذف_بيانات(self, table: str, where_clause: str, where_params: tuple = None) -> bool:
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
            self.تنفيذ_استعلام(sql, where_params)
            self.connection.commit()
            
            logger.info(f"تم حذف البيانات من جدول {table}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في حذف البيانات: {e}")
            self.connection.rollback()
            return False
    
    def تحميل_بيانات(self, table: str, columns: str = "*", where_clause: str = None, 
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
    
    def ادراج_بيانات(self, table: str, data: Dict[str, Any]) -> Optional[int]:
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
            
            self.تنفيذ_استعلام(sql, tuple(data.values()))
            self.connection.commit()
            
            # الحصول على معرف السجل الجديد
            new_id = self.cursor.lastrowid
            
            logger.info(f"تم إدراج بيانات جديدة في جدول {table} - المعرف: {new_id}")
            return new_id
            
        except Exception as e:
            logger.error(f"خطأ في إدراج البيانات: {e}")
            self.connection.rollback()
            return None
    
    # ==================== إنشاء الجداول الرئيسية ====================
    
    def انشاء_النظام_الكامل(self) -> bool:
        """
        إنشاء النظام المحاسبي الكامل
        
        Returns:
            True إذا تم الإنشاء بنجاح
        """
        try:
            logger.info("بدء إنشاء النظام المحاسبي الشامل...")
            
            # إنشاء قاعدة البيانات
            if not self.انشاء_قاعدة_البيانات():
                return False
            
            # إنشاء الجداول الأساسية
            self._انشاء_جداول_النظام()
            
            # إنشاء جداول المحاسبة
            self._انشاء_جداول_المحاسبة()
            
            # إنشاء جداول العملاء (قبل المشاريع)
            self._انشاء_جداول_العملاء()
            
            # إنشاء جداول الموظفين (قبل المشاريع)
            self._انشاء_جداول_الموظفين()
            
            # إنشاء جداول المتدربين
            self._انشاء_جداول_المتدربين()
            
            # إنشاء جداول الموردين
            self._انشاء_جداول_الموردين()
            
            # إنشاء جداول المشاريع (بعد العملاء والموظفين)
            self._انشاء_جداول_المشاريع()
            
            # إنشاء جداول المقاولات
            self._انشاء_جداول_المقاولات()
            
            # إنشاء جداول التدريب
            self._انشاء_جداول_التدريب()
            
            # إنشاء جداول الإيرادات
            self._انشاء_جداول_الايرادات()
            
            # إنشاء جداول المصروفات
            self._انشاء_جداول_المصروفات()
            
            # إنشاء جداول الالتزامات
            self._انشاء_جداول_الالتزامات()
            
            # إنشاء الفهارس
            self._انشاء_الفهارس()
            
            # إنشاء المشغلات
            self._انشاء_المشغلات()
            
            # إدراج البيانات الافتراضية
            self._ادراج_البيانات_الافتراضية()
            
            logger.info("تم إنشاء النظام المحاسبي الشامل بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء النظام: {e}")
            return False
    
    def _انشاء_جداول_النظام(self):
        """إنشاء الجداول الأساسية للنظام"""
        logger.info("إنشاء الجداول الأساسية للنظام...")
        
        # جدول إعدادات النظام
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `إعدادات_النظام` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `المفتاح` VARCHAR(100) NOT NULL UNIQUE,
                `القيمة` TEXT,
                `نوع_البيانات` ENUM('string', 'number', 'boolean', 'json', 'date') DEFAULT 'string',
                `الوصف` TEXT,
                `قابل_للتعديل` BOOLEAN DEFAULT TRUE,
                `المجموعة` VARCHAR(50) DEFAULT 'عام',
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_المفتاح` (`المفتاح`),
                INDEX `idx_المجموعة` (`المجموعة`)
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول المستخدمين والصلاحيات
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `المستخدمين` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `اسم_المستخدم` VARCHAR(50) NOT NULL UNIQUE,
                `كلمة_المرور` VARCHAR(255) NOT NULL,
                `الاسم_الكامل` VARCHAR(100),
                `البريد_الإلكتروني` VARCHAR(100),
                `رقم_الهاتف` VARCHAR(20),
                `الدور` ENUM('مدير_عام', 'مدير_مالي', 'محاسب', 'مستخدم', 'مشرف_مشاريع', 'مشرف_تدريب') DEFAULT 'مستخدم',
                `الصلاحيات` JSON,
                `الحالة` ENUM('نشط', 'غير_نشط', 'محظور', 'معلق') DEFAULT 'نشط',
                `آخر_دخول` DATETIME,
                `عدد_محاولات_الدخول` INT DEFAULT 0,
                `تاريخ_انتهاء_كلمة_المرور` DATE,
                `ملاحظات` TEXT,
                `المستخدم_المنشئ` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_اسم_المستخدم` (`اسم_المستخدم`),
                INDEX `idx_الدور` (`الدور`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_آخر_دخول` (`آخر_دخول`)
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول التصنيفات الموحد
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `التصنيفات` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `النوع` ENUM('عملاء', 'موظفين', 'مشاريع', 'مقاولات', 'مصروفات', 'موردين', 'تدريب', 'حسابات') NOT NULL,
                `اسم_التصنيف` VARCHAR(100) NOT NULL,
                `الكود` VARCHAR(20),
                `الوصف` TEXT,
                `اللون` VARCHAR(7) DEFAULT '#007bff',
                `الأيقونة` VARCHAR(50),
                `نشط` BOOLEAN DEFAULT TRUE,
                `ترتيب_العرض` INT DEFAULT 0,
                `التصنيف_الأب` INT,
                `المستوى` INT DEFAULT 1,
                `المسار` VARCHAR(500),
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY `unique_name_type` (`النوع`, `اسم_التصنيف`),
                INDEX `idx_النوع` (`النوع`),
                INDEX `idx_نشط` (`نشط`),
                INDEX `idx_التصنيف_الأب` (`التصنيف_الأب`),
                FOREIGN KEY (`التصنيف_الأب`) REFERENCES `التصنيفات`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول سجلات النظام
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `سجلات_النظام` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `التاريخ` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `المستوى` ENUM('معلومات', 'تحذير', 'خطأ', 'نجاح') NOT NULL,
                `الموديول` VARCHAR(100),
                `العملية` VARCHAR(100),
                `الرسالة` TEXT NOT NULL,
                `المستخدم` VARCHAR(50),
                `عنوان_IP` VARCHAR(45),
                `تفاصيل_إضافية` JSON,
                `معرف_المرجع` INT,
                `نوع_المرجع` VARCHAR(50),
                INDEX `idx_التاريخ` (`التاريخ`),
                INDEX `idx_المستوى` (`المستوى`),
                INDEX `idx_الموديول` (`الموديول`),
                INDEX `idx_المستخدم` (`المستخدم`),
                INDEX `idx_المرجع` (`نوع_المرجع`, `معرف_المرجع`)
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول المرفقات الموحد
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `المرفقات` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `نوع_المرجع` VARCHAR(50) NOT NULL,
                `معرف_المرجع` INT NOT NULL,
                `اسم_الملف` VARCHAR(255) NOT NULL,
                `اسم_الملف_الأصلي` VARCHAR(255),
                `المسار` VARCHAR(500) NOT NULL,
                `نوع_الملف` VARCHAR(50),
                `حجم_الملف` BIGINT DEFAULT 0,
                `الوصف` TEXT,
                `العلامات` JSON,
                `خاص` BOOLEAN DEFAULT FALSE,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX `idx_المرجع` (`نوع_المرجع`, `معرف_المرجع`),
                INDEX `idx_نوع_الملف` (`نوع_الملف`),
                INDEX `idx_حجم_الملف` (`حجم_الملف`)
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول التذكيرات والتنبيهات الموحد
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `التذكيرات_والتنبيهات` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `نوع_المرجع` VARCHAR(50) NOT NULL,
                `معرف_المرجع` INT NOT NULL,
                `العنوان` VARCHAR(255) NOT NULL,
                `الرسالة` TEXT,
                `نوع_التذكير` ENUM('تذكير', 'تنبيه', 'إنذار', 'معلومة') DEFAULT 'تذكير',
                `الأولوية` ENUM('منخفضة', 'متوسطة', 'عالية', 'عاجلة') DEFAULT 'متوسطة',
                `تاريخ_التذكير` DATETIME NOT NULL,
                `تكرار` ENUM('مرة_واحدة', 'يومي', 'أسبوعي', 'شهري', 'سنوي') DEFAULT 'مرة_واحدة',
                `المستخدم_المستهدف` VARCHAR(50),
                `تم_القراءة` BOOLEAN DEFAULT FALSE,
                `تم_الإرسال` BOOLEAN DEFAULT FALSE,
                `نشط` BOOLEAN DEFAULT TRUE,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_المرجع` (`نوع_المرجع`, `معرف_المرجع`),
                INDEX `idx_تاريخ_التذكير` (`تاريخ_التذكير`),
                INDEX `idx_المستخدم_المستهدف` (`المستخدم_المستهدف`),
                INDEX `idx_نشط` (`نشط`)
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        self.tables_created.update(['إعدادات_النظام', 'المستخدمين', 'التصنيفات', 'سجلات_النظام', 'المرفقات', 'التذكيرات_والتنبيهات'])
        logger.info("تم إنشاء الجداول الأساسية للنظام بنجاح")
    
    def _انشاء_جداول_المحاسبة(self):
        """إنشاء جداول المحاسبة الأساسية"""
        logger.info("إنشاء جداول المحاسبة...")
        
        # جدول شجرة الحسابات
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `شجرة_الحسابات` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `رقم_الحساب` VARCHAR(20) NOT NULL UNIQUE,
                `اسم_الحساب` VARCHAR(255) NOT NULL,
                `نوع_الحساب` ENUM('أصول', 'خصوم', 'حقوق_ملكية', 'إيرادات', 'مصروفات') NOT NULL,
                `تصنيف_فرعي` ENUM('أصول_ثابتة', 'أصول_متداولة', 'خصوم_طويلة_الأجل', 'خصوم_قصيرة_الأجل', 'رأس_المال', 'أرباح_محتجزة', 'إيرادات_تشغيلية', 'إيرادات_أخرى', 'مصروفات_تشغيلية', 'مصروفات_إدارية', 'مصروفات_أخرى') NOT NULL,
                `الحساب_الأب` INT,
                `المستوى` INT DEFAULT 1,
                `المسار` VARCHAR(500),
                `طبيعة_الحساب` ENUM('مدين', 'دائن') NOT NULL,
                `الرصيد_الافتتاحي` DECIMAL(15,2) DEFAULT 0,
                `الرصيد_الحالي` DECIMAL(15,2) DEFAULT 0,
                `حساب_رئيسي` BOOLEAN DEFAULT FALSE,
                `يقبل_قيود` BOOLEAN DEFAULT TRUE,
                `نشط` BOOLEAN DEFAULT TRUE,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_رقم_الحساب` (`رقم_الحساب`),
                INDEX `idx_نوع_الحساب` (`نوع_الحساب`),
                INDEX `idx_الحساب_الأب` (`الحساب_الأب`),
                INDEX `idx_نشط` (`نشط`),
                FOREIGN KEY (`الحساب_الأب`) REFERENCES `شجرة_الحسابات`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول القيود المحاسبية
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `القيود_المحاسبية` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `رقم_القيد` VARCHAR(50) NOT NULL UNIQUE,
                `تاريخ_القيد` DATE NOT NULL,
                `نوع_القيد` ENUM('افتتاحي', 'يومي', 'تسوية', 'إقفال') DEFAULT 'يومي',
                `البيان` TEXT NOT NULL,
                `إجمالي_المدين` DECIMAL(15,2) DEFAULT 0,
                `إجمالي_الدائن` DECIMAL(15,2) DEFAULT 0,
                `متوازن` BOOLEAN GENERATED ALWAYS AS (`إجمالي_المدين` = `إجمالي_الدائن`) STORED,
                `مرجع_خارجي` VARCHAR(100),
                `نوع_المرجع` VARCHAR(50),
                `معرف_المرجع` INT,
                `حالة_القيد` ENUM('مسودة', 'معتمد', 'مرحل', 'ملغي') DEFAULT 'مسودة',
                `معتمد_بواسطة` VARCHAR(50),
                `تاريخ_الاعتماد` DATETIME,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة_المالية` INT GENERATED ALWAYS AS (YEAR(`تاريخ_القيد`)) STORED,
                INDEX `idx_رقم_القيد` (`رقم_القيد`),
                INDEX `idx_تاريخ_القيد` (`تاريخ_القيد`),
                INDEX `idx_نوع_القيد` (`نوع_القيد`),
                INDEX `idx_حالة_القيد` (`حالة_القيد`),
                INDEX `idx_المرجع` (`نوع_المرجع`, `معرف_المرجع`),
                INDEX `idx_السنة_المالية` (`السنة_المالية`)
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول مراكز التكلفة (يجب إنشاؤه قبل تفاصيل القيود)
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `مراكز_التكلفة` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `رقم_المركز` VARCHAR(20) NOT NULL UNIQUE,
                `اسم_المركز` VARCHAR(255) NOT NULL,
                `نوع_المركز` ENUM('إنتاجي', 'خدمي', 'إداري', 'تسويقي') NOT NULL,
                `المركز_الأب` INT,
                `المستوى` INT DEFAULT 1,
                `المسار` VARCHAR(500),
                `المسؤول` VARCHAR(100),
                `الميزانية_المخططة` DECIMAL(15,2) DEFAULT 0,
                `التكلفة_الفعلية` DECIMAL(15,2) DEFAULT 0,
                `نشط` BOOLEAN DEFAULT TRUE,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_رقم_المركز` (`رقم_المركز`),
                INDEX `idx_نوع_المركز` (`نوع_المركز`),
                INDEX `idx_المركز_الأب` (`المركز_الأب`),
                INDEX `idx_نشط` (`نشط`),
                FOREIGN KEY (`المركز_الأب`) REFERENCES `مراكز_التكلفة`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول تفاصيل القيود المحاسبية (بعد إنشاء مراكز التكلفة)
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `تفاصيل_القيود_المحاسبية` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_القيد` INT NOT NULL,
                `معرف_الحساب` INT NOT NULL,
                `البيان` VARCHAR(255),
                `المبلغ_المدين` DECIMAL(15,2) DEFAULT 0,
                `المبلغ_الدائن` DECIMAL(15,2) DEFAULT 0,
                `معرف_مركز_التكلفة` INT,
                `ترتيب_السطر` INT DEFAULT 1,
                `ملاحظات` TEXT,
                INDEX `idx_معرف_القيد` (`معرف_القيد`),
                INDEX `idx_معرف_الحساب` (`معرف_الحساب`),
                INDEX `idx_مركز_التكلفة` (`معرف_مركز_التكلفة`),
                FOREIGN KEY (`معرف_القيد`) REFERENCES `القيود_المحاسبية`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_الحساب`) REFERENCES `شجرة_الحسابات`(`id`) ON DELETE RESTRICT,
                FOREIGN KEY (`معرف_مركز_التكلفة`) REFERENCES `مراكز_التكلفة`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول السنوات المالية
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `السنوات_المالية` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `السنة` INT NOT NULL UNIQUE,
                `تاريخ_البداية` DATE NOT NULL,
                `تاريخ_النهاية` DATE NOT NULL,
                `الحالة` ENUM('مفتوحة', 'مغلقة', 'مؤرشفة') DEFAULT 'مفتوحة',
                `تم_الإقفال` BOOLEAN DEFAULT FALSE,
                `تاريخ_الإقفال` DATETIME,
                `المستخدم_المقفل` VARCHAR(50),
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_السنة` (`السنة`),
                INDEX `idx_الحالة` (`الحالة`)
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول أرصدة الحسابات
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `أرصدة_الحسابات` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_الحساب` INT NOT NULL,
                `السنة_المالية` INT NOT NULL,
                `الشهر` INT NOT NULL,
                `الرصيد_الافتتاحي` DECIMAL(15,2) DEFAULT 0,
                `إجمالي_المدين` DECIMAL(15,2) DEFAULT 0,
                `إجمالي_الدائن` DECIMAL(15,2) DEFAULT 0,
                `الرصيد_الختامي` DECIMAL(15,2) GENERATED ALWAYS AS (
                    `الرصيد_الافتتاحي` + `إجمالي_المدين` - `إجمالي_الدائن`
                ) STORED,
                `تاريخ_آخر_تحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY `unique_account_period` (`معرف_الحساب`, `السنة_المالية`, `الشهر`),
                INDEX `idx_معرف_الحساب` (`معرف_الحساب`),
                INDEX `idx_السنة_المالية` (`السنة_المالية`),
                INDEX `idx_الشهر` (`الشهر`),
                FOREIGN KEY (`معرف_الحساب`) REFERENCES `شجرة_الحسابات`(`id`) ON DELETE CASCADE
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        self.tables_created.update(['شجرة_الحسابات', 'القيود_المحاسبية', 'تفاصيل_القيود_المحاسبية', 'مراكز_التكلفة', 'السنوات_المالية', 'أرصدة_الحسابات'])
        logger.info("تم إنشاء جداول المحاسبة بنجاح")
    
    def _انشاء_جداول_المشاريع(self):
        """إنشاء جداول المشاريع وجداولها الفرعية"""
        logger.info("إنشاء جداول المشاريع...")
        
        # جدول المشاريع الرئيسي
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `المشاريع` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `رقم_المشروع` VARCHAR(50) NOT NULL UNIQUE,
                `معرف_التصنيف` INT,
                `معرف_العميل` INT NOT NULL,
                `معرف_المدير` INT,
                `اسم_المشروع` VARCHAR(255) NOT NULL,
                `الوصف` TEXT,
                `الموقع` VARCHAR(255),
                `المساحة` DECIMAL(15,2) DEFAULT 0,
                `وحدة_المساحة` VARCHAR(20) DEFAULT 'متر مربع',
                `قيمة_المشروع` DECIMAL(15,2) DEFAULT 0,
                `المدفوع` DECIMAL(15,2) DEFAULT 0,
                `المتبقي` DECIMAL(15,2) GENERATED ALWAYS AS (`قيمة_المشروع` - `المدفوع`) STORED,
                `تاريخ_البداية` DATE,
                `تاريخ_النهاية_المخطط` DATE,
                `تاريخ_النهاية_الفعلي` DATE,
                `المدة_بالأيام` INT GENERATED ALWAYS AS (DATEDIFF(`تاريخ_النهاية_المخطط`, `تاريخ_البداية`)) STORED,
                `نسبة_الإنجاز` DECIMAL(5,2) DEFAULT 0,
                `الحالة` ENUM('جديد', 'قيد_التخطيط', 'قيد_التنفيذ', 'متوقف', 'مكتمل', 'ملغي', 'قيد_التسليم', 'مسلم') DEFAULT 'جديد',
                `الأولوية` ENUM('منخفضة', 'متوسطة', 'عالية', 'عاجلة') DEFAULT 'متوسطة',
                `نوع_العقد` ENUM('مقطوعية', 'وقت_ومواد', 'نسبة_مئوية') DEFAULT 'مقطوعية',
                `العملة` VARCHAR(10) DEFAULT 'ريال',
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_البداية`)) STORED,
                INDEX `idx_رقم_المشروع` (`رقم_المشروع`),
                INDEX `idx_معرف_العميل` (`معرف_العميل`),
                INDEX `idx_معرف_المدير` (`معرف_المدير`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_تاريخ_البداية` (`تاريخ_البداية`),
                INDEX `idx_السنة` (`السنة`),
                FOREIGN KEY (`معرف_التصنيف`) REFERENCES `التصنيفات`(`id`) ON DELETE SET NULL,
                FOREIGN KEY (`معرف_العميل`) REFERENCES `العملاء`(`id`) ON DELETE RESTRICT,
                FOREIGN KEY (`معرف_المدير`) REFERENCES `الموظفين`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول مراحل المشروع
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `مراحل_المشروع` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_المشروع` INT NOT NULL,
                `رقم_المرحلة` VARCHAR(50),
                `اسم_المرحلة` VARCHAR(255) NOT NULL,
                `الوصف` TEXT,
                `تاريخ_البداية_المخطط` DATE,
                `تاريخ_النهاية_المخطط` DATE,
                `تاريخ_البداية_الفعلي` DATE,
                `تاريخ_النهاية_الفعلي` DATE,
                `المدة_المخططة` INT GENERATED ALWAYS AS (DATEDIFF(`تاريخ_النهاية_المخطط`, `تاريخ_البداية_المخطط`)) STORED,
                `المدة_الفعلية` INT GENERATED ALWAYS AS (DATEDIFF(`تاريخ_النهاية_الفعلي`, `تاريخ_البداية_الفعلي`)) STORED,
                `القيمة_المخططة` DECIMAL(15,2) DEFAULT 0,
                `التكلفة_الفعلية` DECIMAL(15,2) DEFAULT 0,
                `نسبة_الإنجاز` DECIMAL(5,2) DEFAULT 0,
                `الحالة` ENUM('لم_تبدأ', 'قيد_التنفيذ', 'مكتملة', 'متأخرة', 'ملغية') DEFAULT 'لم_تبدأ',
                `المسؤول` INT,
                `الأولوية` ENUM('منخفضة', 'متوسطة', 'عالية', 'عاجلة') DEFAULT 'متوسطة',
                `ترتيب_المرحلة` INT DEFAULT 1,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_معرف_المشروع` (`معرف_المشروع`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_المسؤول` (`المسؤول`),
                INDEX `idx_ترتيب_المرحلة` (`ترتيب_المرحلة`),
                FOREIGN KEY (`معرف_المشروع`) REFERENCES `المشاريع`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`المسؤول`) REFERENCES `الموظفين`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول مهام فريق العمل
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `مهام_فريق_العمل` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_المشروع` INT NOT NULL,
                `معرف_المرحلة` INT,
                `اسم_المهمة` VARCHAR(255) NOT NULL,
                `الوصف` TEXT,
                `معرف_الموظف_المسؤول` INT,
                `تاريخ_البداية` DATE,
                `تاريخ_النهاية_المخطط` DATE,
                `تاريخ_النهاية_الفعلي` DATE,
                `الساعات_المخططة` DECIMAL(8,2) DEFAULT 0,
                `الساعات_الفعلية` DECIMAL(8,2) DEFAULT 0,
                `نسبة_الإنجاز` DECIMAL(5,2) DEFAULT 0,
                `الحالة` ENUM('جديدة', 'قيد_التنفيذ', 'مكتملة', 'متأخرة', 'ملغية', 'معلقة') DEFAULT 'جديدة',
                `الأولوية` ENUM('منخفضة', 'متوسطة', 'عالية', 'عاجلة') DEFAULT 'متوسطة',
                `التقييم` INT CHECK (`التقييم` BETWEEN 1 AND 5),
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_معرف_المشروع` (`معرف_المشروع`),
                INDEX `idx_معرف_المرحلة` (`معرف_المرحلة`),
                INDEX `idx_معرف_الموظف_المسؤول` (`معرف_الموظف_المسؤول`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_تاريخ_النهاية_المخطط` (`تاريخ_النهاية_المخطط`),
                FOREIGN KEY (`معرف_المشروع`) REFERENCES `المشاريع`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_المرحلة`) REFERENCES `مراحل_المشروع`(`id`) ON DELETE SET NULL,
                FOREIGN KEY (`معرف_الموظف_المسؤول`) REFERENCES `الموظفين`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول العهد المالية للمشاريع
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `عهد_مالية_المشاريع` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_المشروع` INT NOT NULL,
                `رقم_العهدة` VARCHAR(50) NOT NULL UNIQUE,
                `معرف_الموظف` INT NOT NULL,
                `المبلغ` DECIMAL(15,2) NOT NULL,
                `الغرض` VARCHAR(255) NOT NULL,
                `تاريخ_الاستلام` DATE NOT NULL,
                `تاريخ_الاستحقاق` DATE,
                `المبلغ_المستخدم` DECIMAL(15,2) DEFAULT 0,
                `المبلغ_المتبقي` DECIMAL(15,2) GENERATED ALWAYS AS (`المبلغ` - `المبلغ_المستخدم`) STORED,
                `الحالة` ENUM('نشطة', 'مسددة', 'متأخرة', 'ملغية') DEFAULT 'نشطة',
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_معرف_المشروع` (`معرف_المشروع`),
                INDEX `idx_رقم_العهدة` (`رقم_العهدة`),
                INDEX `idx_معرف_الموظف` (`معرف_الموظف`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_تاريخ_الاستحقاق` (`تاريخ_الاستحقاق`),
                FOREIGN KEY (`معرف_المشروع`) REFERENCES `المشاريع`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_الموظف`) REFERENCES `الموظفين`(`id`) ON DELETE RESTRICT
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول دفعات العهد المالية
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `دفعات_العهد_المالية` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_العهدة` INT NOT NULL,
                `رقم_الدفعة` VARCHAR(50),
                `المبلغ` DECIMAL(15,2) NOT NULL,
                `الوصف` VARCHAR(255),
                `تاريخ_الدفعة` DATE NOT NULL,
                `طريقة_الدفع` ENUM('نقدي', 'شيك', 'تحويل_بنكي', 'بطاقة') DEFAULT 'نقدي',
                `رقم_المرجع` VARCHAR(100),
                `معرف_القيد_المحاسبي` INT,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX `idx_معرف_العهدة` (`معرف_العهدة`),
                INDEX `idx_تاريخ_الدفعة` (`تاريخ_الدفعة`),
                INDEX `idx_معرف_القيد_المحاسبي` (`معرف_القيد_المحاسبي`),
                FOREIGN KEY (`معرف_العهدة`) REFERENCES `عهد_مالية_المشاريع`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_القيد_المحاسبي`) REFERENCES `القيود_المحاسبية`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول مصروفات المشاريع
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `مصروفات_المشاريع` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_المشروع` INT NOT NULL,
                `معرف_المرحلة` INT,
                `معرف_العهدة` INT,
                `رقم_المصروف` VARCHAR(50),
                `نوع_المصروف` VARCHAR(100) NOT NULL,
                `الوصف` VARCHAR(255) NOT NULL,
                `المبلغ` DECIMAL(15,2) NOT NULL,
                `تاريخ_المصروف` DATE NOT NULL,
                `معرف_المورد` INT,
                `رقم_الفاتورة` VARCHAR(100),
                `طريقة_الدفع` ENUM('نقدي', 'شيك', 'تحويل_بنكي', 'بطاقة', 'آجل') DEFAULT 'نقدي',
                `معرف_القيد_المحاسبي` INT,
                `معتمد` BOOLEAN DEFAULT FALSE,
                `معتمد_بواسطة` VARCHAR(50),
                `تاريخ_الاعتماد` DATETIME,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_معرف_المشروع` (`معرف_المشروع`),
                INDEX `idx_معرف_المرحلة` (`معرف_المرحلة`),
                INDEX `idx_معرف_العهدة` (`معرف_العهدة`),
                INDEX `idx_نوع_المصروف` (`نوع_المصروف`),
                INDEX `idx_تاريخ_المصروف` (`تاريخ_المصروف`),
                INDEX `idx_معرف_المورد` (`معرف_المورد`),
                FOREIGN KEY (`معرف_المشروع`) REFERENCES `المشاريع`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_المرحلة`) REFERENCES `مراحل_المشروع`(`id`) ON DELETE SET NULL,
                FOREIGN KEY (`معرف_العهدة`) REFERENCES `عهد_مالية_المشاريع`(`id`) ON DELETE SET NULL,
                FOREIGN KEY (`معرف_المورد`) REFERENCES `الموردين`(`id`) ON DELETE SET NULL,
                FOREIGN KEY (`معرف_القيد_المحاسبي`) REFERENCES `القيود_المحاسبية`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول دفعات المشاريع
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `دفعات_المشاريع` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_المشروع` INT NOT NULL,
                `رقم_الدفعة` VARCHAR(50) NOT NULL,
                `المبلغ` DECIMAL(15,2) NOT NULL,
                `تاريخ_الدفعة` DATE NOT NULL,
                `تاريخ_الاستحقاق` DATE,
                `نوع_الدفعة` ENUM('دفعة_مقدمة', 'دفعة_تقدم_عمل', 'دفعة_نهائية', 'دفعة_إضافية') DEFAULT 'دفعة_تقدم_عمل',
                `طريقة_الدفع` ENUM('نقدي', 'شيك', 'تحويل_بنكي', 'بطاقة') DEFAULT 'نقدي',
                `رقم_المرجع` VARCHAR(100),
                `الحالة` ENUM('مستحقة', 'مدفوعة', 'متأخرة', 'ملغية') DEFAULT 'مستحقة',
                `معرف_القيد_المحاسبي` INT,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_معرف_المشروع` (`معرف_المشروع`),
                INDEX `idx_رقم_الدفعة` (`رقم_الدفعة`),
                INDEX `idx_تاريخ_الدفعة` (`تاريخ_الدفعة`),
                INDEX `idx_تاريخ_الاستحقاق` (`تاريخ_الاستحقاق`),
                INDEX `idx_الحالة` (`الحالة`),
                FOREIGN KEY (`معرف_المشروع`) REFERENCES `المشاريع`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_القيد_المحاسبي`) REFERENCES `القيود_المحاسبية`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول الجدول الزمني للمراحل
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `الجدول_الزمني_للمراحل` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_المشروع` INT NOT NULL,
                `معرف_المرحلة` INT NOT NULL,
                `النشاط` VARCHAR(255) NOT NULL,
                `الوصف` TEXT,
                `تاريخ_البداية_المخطط` DATE NOT NULL,
                `تاريخ_النهاية_المخطط` DATE NOT NULL,
                `تاريخ_البداية_الفعلي` DATE,
                `تاريخ_النهاية_الفعلي` DATE,
                `المدة_بالأيام` INT GENERATED ALWAYS AS (DATEDIFF(`تاريخ_النهاية_المخطط`, `تاريخ_البداية_المخطط`)) STORED,
                `نسبة_الإنجاز` DECIMAL(5,2) DEFAULT 0,
                `المسؤول` INT,
                `الحالة` ENUM('مخطط', 'قيد_التنفيذ', 'مكتمل', 'متأخر', 'ملغي') DEFAULT 'مخطط',
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_معرف_المشروع` (`معرف_المشروع`),
                INDEX `idx_معرف_المرحلة` (`معرف_المرحلة`),
                INDEX `idx_تاريخ_البداية_المخطط` (`تاريخ_البداية_المخطط`),
                INDEX `idx_المسؤول` (`المسؤول`),
                INDEX `idx_الحالة` (`الحالة`),
                FOREIGN KEY (`معرف_المشروع`) REFERENCES `المشاريع`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_المرحلة`) REFERENCES `مراحل_المشروع`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`المسؤول`) REFERENCES `الموظفين`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول حسابات فريق العمل
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `حسابات_فريق_العمل` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_المشروع` INT NOT NULL,
                `معرف_الموظف` INT NOT NULL,
                `نوع_الحساب` ENUM('راتب', 'عمولة', 'مكافأة', 'بدل', 'خصم') NOT NULL,
                `المبلغ` DECIMAL(15,2) NOT NULL,
                `تاريخ_الاستحقاق` DATE NOT NULL,
                `تاريخ_الدفع` DATE,
                `الوصف` VARCHAR(255),
                `الحالة` ENUM('مستحق', 'مدفوع', 'متأخر', 'ملغي') DEFAULT 'مستحق',
                `معرف_القيد_المحاسبي` INT,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_معرف_المشروع` (`معرف_المشروع`),
                INDEX `idx_معرف_الموظف` (`معرف_الموظف`),
                INDEX `idx_نوع_الحساب` (`نوع_الحساب`),
                INDEX `idx_تاريخ_الاستحقاق` (`تاريخ_الاستحقاق`),
                INDEX `idx_الحالة` (`الحالة`),
                FOREIGN KEY (`معرف_المشروع`) REFERENCES `المشاريع`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_الموظف`) REFERENCES `الموظفين`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_القيد_المحاسبي`) REFERENCES `القيود_المحاسبية`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول عقود المشاريع
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `عقود_المشاريع` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_المشروع` INT NOT NULL,
                `رقم_العقد` VARCHAR(50) NOT NULL UNIQUE,
                `نوع_العقد` ENUM('رئيسي', 'فرعي', 'ملحق', 'تعديل') DEFAULT 'رئيسي',
                `تاريخ_العقد` DATE NOT NULL,
                `تاريخ_البداية` DATE NOT NULL,
                `تاريخ_النهاية` DATE NOT NULL,
                `قيمة_العقد` DECIMAL(15,2) NOT NULL,
                `العملة` VARCHAR(10) DEFAULT 'ريال',
                `شروط_الدفع` TEXT,
                `الضمانات` TEXT,
                `الغرامات` TEXT,
                `الحالة` ENUM('مسودة', 'نشط', 'منتهي', 'ملغي', 'معلق') DEFAULT 'مسودة',
                `مسار_الملف` VARCHAR(500),
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_معرف_المشروع` (`معرف_المشروع`),
                INDEX `idx_رقم_العقد` (`رقم_العقد`),
                INDEX `idx_نوع_العقد` (`نوع_العقد`),
                INDEX `idx_تاريخ_العقد` (`تاريخ_العقد`),
                INDEX `idx_الحالة` (`الحالة`),
                FOREIGN KEY (`معرف_المشروع`) REFERENCES `المشاريع`(`id`) ON DELETE CASCADE
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول خسائر المشاريع
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `خسائر_المشاريع` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_المشروع` INT NOT NULL,
                `نوع_الخسارة` VARCHAR(100) NOT NULL,
                `الوصف` TEXT NOT NULL,
                `المبلغ` DECIMAL(15,2) NOT NULL,
                `تاريخ_الخسارة` DATE NOT NULL,
                `السبب` TEXT,
                `المسؤول` VARCHAR(100),
                `إجراءات_التصحيح` TEXT,
                `معرف_القيد_المحاسبي` INT,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_معرف_المشروع` (`معرف_المشروع`),
                INDEX `idx_نوع_الخسارة` (`نوع_الخسارة`),
                INDEX `idx_تاريخ_الخسارة` (`تاريخ_الخسارة`),
                FOREIGN KEY (`معرف_المشروع`) REFERENCES `المشاريع`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_القيد_المحاسبي`) REFERENCES `القيود_المحاسبية`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول مردودات مواد المشاريع
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `مردودات_مواد_المشاريع` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_المشروع` INT NOT NULL,
                `رقم_المردود` VARCHAR(50) NOT NULL,
                `معرف_المورد` INT,
                `تاريخ_المردود` DATE NOT NULL,
                `سبب_المردود` TEXT NOT NULL,
                `إجمالي_المبلغ` DECIMAL(15,2) DEFAULT 0,
                `الحالة` ENUM('مسودة', 'معتمد', 'مرفوض', 'مكتمل') DEFAULT 'مسودة',
                `معرف_القيد_المحاسبي` INT,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_معرف_المشروع` (`معرف_المشروع`),
                INDEX `idx_رقم_المردود` (`رقم_المردود`),
                INDEX `idx_معرف_المورد` (`معرف_المورد`),
                INDEX `idx_تاريخ_المردود` (`تاريخ_المردود`),
                INDEX `idx_الحالة` (`الحالة`),
                FOREIGN KEY (`معرف_المشروع`) REFERENCES `المشاريع`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_المورد`) REFERENCES `الموردين`(`id`) ON DELETE SET NULL,
                FOREIGN KEY (`معرف_القيد_المحاسبي`) REFERENCES `القيود_المحاسبية`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        self.tables_created.update([
            'المشاريع', 'مراحل_المشروع', 'مهام_فريق_العمل', 'عهد_مالية_المشاريع', 
            'دفعات_العهد_المالية', 'مصروفات_المشاريع', 'دفعات_المشاريع', 
            'الجدول_الزمني_للمراحل', 'حسابات_فريق_العمل', 'عقود_المشاريع', 
            'خسائر_المشاريع', 'مردودات_مواد_المشاريع'
        ])
        logger.info("تم إنشاء جداول المشاريع بنجاح")
    
    def _انشاء_جداول_المقاولات(self):
        """إنشاء جداول المقاولات (نفس جداول المشاريع مع تخصيص)"""
        logger.info("إنشاء جداول المقاولات...")
        
        # جدول المقاولات الرئيسي
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `المقاولات` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `رقم_المقاولة` VARCHAR(50) NOT NULL UNIQUE,
                `معرف_التصنيف` INT,
                `معرف_العميل` INT NOT NULL,
                `معرف_المدير` INT,
                `اسم_المقاولة` VARCHAR(255) NOT NULL,
                `نوع_المقاولة` ENUM('إنشاءات', 'صيانة', 'تشطيبات', 'أخرى') DEFAULT 'إنشاءات',
                `الوصف` TEXT,
                `الموقع` VARCHAR(255),
                `المساحة` DECIMAL(15,2) DEFAULT 0,
                `وحدة_المساحة` VARCHAR(20) DEFAULT 'متر مربع',
                `قيمة_المقاولة` DECIMAL(15,2) DEFAULT 0,
                `المدفوع` DECIMAL(15,2) DEFAULT 0,
                `المتبقي` DECIMAL(15,2) GENERATED ALWAYS AS (`قيمة_المقاولة` - `المدفوع`) STORED,
                `تاريخ_البداية` DATE,
                `تاريخ_النهاية_المخطط` DATE,
                `تاريخ_النهاية_الفعلي` DATE,
                `المدة_بالأيام` INT GENERATED ALWAYS AS (DATEDIFF(`تاريخ_النهاية_المخطط`, `تاريخ_البداية`)) STORED,
                `نسبة_الإنجاز` DECIMAL(5,2) DEFAULT 0,
                `الحالة` ENUM('جديد', 'قيد_التخطيط', 'قيد_التنفيذ', 'متوقف', 'مكتمل', 'ملغي', 'قيد_التسليم', 'مسلم') DEFAULT 'جديد',
                `الأولوية` ENUM('منخفضة', 'متوسطة', 'عالية', 'عاجلة') DEFAULT 'متوسطة',
                `نوع_العقد` ENUM('مقطوعية', 'وقت_ومواد', 'نسبة_مئوية') DEFAULT 'مقطوعية',
                `العملة` VARCHAR(10) DEFAULT 'ريال',
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_البداية`)) STORED,
                INDEX `idx_رقم_المقاولة` (`رقم_المقاولة`),
                INDEX `idx_معرف_العميل` (`معرف_العميل`),
                INDEX `idx_معرف_المدير` (`معرف_المدير`),
                INDEX `idx_نوع_المقاولة` (`نوع_المقاولة`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_تاريخ_البداية` (`تاريخ_البداية`),
                INDEX `idx_السنة` (`السنة`),
                FOREIGN KEY (`معرف_التصنيف`) REFERENCES `التصنيفات`(`id`) ON DELETE SET NULL,
                FOREIGN KEY (`معرف_العميل`) REFERENCES `العملاء`(`id`) ON DELETE RESTRICT,
                FOREIGN KEY (`معرف_المدير`) REFERENCES `الموظفين`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # ملاحظة: باقي جداول المقاولات تستخدم نفس هيكل جداول المشاريع
        # يمكن إنشاء views أو استخدام نفس الجداول مع تمييز النوع
        
        self.tables_created.add('المقاولات')
        logger.info("تم إنشاء جداول المقاولات بنجاح")
    
    def _انشاء_جداول_العملاء(self):
        """إنشاء جداول العملاء"""
        logger.info("إنشاء جداول العملاء...")
        
        # جدول العملاء الرئيسي
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `العملاء` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `رقم_العميل` VARCHAR(50) NOT NULL UNIQUE,
                `معرف_التصنيف` INT,
                `اسم_العميل` VARCHAR(255) NOT NULL,
                `نوع_العميل` ENUM('فرد', 'شركة', 'مؤسسة', 'جهة_حكومية') DEFAULT 'فرد',
                `رقم_الهوية_السجل` VARCHAR(50),
                `العنوان` VARCHAR(255),
                `المدينة` VARCHAR(100),
                `المنطقة` VARCHAR(100),
                `الرمز_البريدي` VARCHAR(20),
                `رقم_الهاتف` VARCHAR(50),
                `رقم_الجوال` VARCHAR(50),
                `البريد_الإلكتروني` VARCHAR(100),
                `الموقع_الإلكتروني` VARCHAR(255),
                `تاريخ_التسجيل` DATE DEFAULT (CURRENT_DATE),
                `رصيد_العميل` DECIMAL(15,2) DEFAULT 0,
                `حد_الائتمان` DECIMAL(15,2) DEFAULT 0,
                `التقييم` INT DEFAULT 0 CHECK (`التقييم` BETWEEN 0 AND 5),
                `مصدر_العميل` VARCHAR(100),
                `الحالة` ENUM('نشط', 'غير_نشط', 'محظور', 'معلق') DEFAULT 'نشط',
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_التسجيل`)) STORED,
                INDEX `idx_رقم_العميل` (`رقم_العميل`),
                INDEX `idx_اسم_العميل` (`اسم_العميل`),
                INDEX `idx_نوع_العميل` (`نوع_العميل`),
                INDEX `idx_رقم_الهوية_السجل` (`رقم_الهوية_السجل`),
                INDEX `idx_رقم_الهاتف` (`رقم_الهاتف`),
                INDEX `idx_البريد_الإلكتروني` (`البريد_الإلكتروني`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_السنة` (`السنة`),
                FOREIGN KEY (`معرف_التصنيف`) REFERENCES `التصنيفات`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول معاملات العملاء المالية
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `معاملات_العملاء_المالية` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_العميل` INT NOT NULL,
                `رقم_المعاملة` VARCHAR(50) UNIQUE,
                `نوع_المعاملة` ENUM('دفعة', 'فاتورة', 'خصم', 'إضافة', 'تسوية') NOT NULL,
                `المبلغ` DECIMAL(15,2) NOT NULL,
                `الوصف` VARCHAR(255),
                `تاريخ_المعاملة` DATE NOT NULL,
                `طريقة_الدفع` ENUM('نقدي', 'شيك', 'تحويل_بنكي', 'بطاقة', 'آجل') DEFAULT 'نقدي',
                `رقم_المرجع` VARCHAR(100),
                `معرف_المشروع` INT,
                `معرف_القيد_المحاسبي` INT,
                `الحالة` ENUM('مكتملة', 'معلقة', 'ملغية') DEFAULT 'مكتملة',
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_المعاملة`)) STORED,
                INDEX `idx_معرف_العميل` (`معرف_العميل`),
                INDEX `idx_رقم_المعاملة` (`رقم_المعاملة`),
                INDEX `idx_نوع_المعاملة` (`نوع_المعاملة`),
                INDEX `idx_تاريخ_المعاملة` (`تاريخ_المعاملة`),
                INDEX `idx_معرف_المشروع` (`معرف_المشروع`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_السنة` (`السنة`),
                FOREIGN KEY (`معرف_العميل`) REFERENCES `العملاء`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_القيد_المحاسبي`) REFERENCES `القيود_المحاسبية`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول جهات اتصال العملاء
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `جهات_اتصال_العملاء` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_العميل` INT NOT NULL,
                `الاسم` VARCHAR(255) NOT NULL,
                `المنصب` VARCHAR(100),
                `رقم_الهاتف` VARCHAR(50),
                `رقم_الجوال` VARCHAR(50),
                `البريد_الإلكتروني` VARCHAR(100),
                `نوع_الاتصال` ENUM('رئيسي', 'فرعي', 'طوارئ', 'مالي', 'فني') DEFAULT 'فرعي',
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_معرف_العميل` (`معرف_العميل`),
                INDEX `idx_الاسم` (`الاسم`),
                INDEX `idx_نوع_الاتصال` (`نوع_الاتصال`),
                FOREIGN KEY (`معرف_العميل`) REFERENCES `العملاء`(`id`) ON DELETE CASCADE
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        self.tables_created.update(['العملاء', 'معاملات_العملاء_المالية', 'جهات_اتصال_العملاء'])
        logger.info("تم إنشاء جداول العملاء بنجاح")
    
    def _انشاء_جداول_الموظفين(self):
        """إنشاء جداول الموظفين وجداولها الفرعية"""
        logger.info("إنشاء جداول الموظفين...")
        
        # جدول الموظفين الرئيسي
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `الموظفين` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `رقم_الموظف` VARCHAR(50) NOT NULL UNIQUE,
                `معرف_التصنيف` INT,
                `اسم_الموظف` VARCHAR(255) NOT NULL,
                `رقم_الهوية` VARCHAR(50) UNIQUE,
                `تاريخ_الميلاد` DATE,
                `الجنسية` VARCHAR(50),
                `الحالة_الاجتماعية` ENUM('أعزب', 'متزوج', 'مطلق', 'أرمل') DEFAULT 'أعزب',
                `العنوان` VARCHAR(255),
                `المدينة` VARCHAR(100),
                `رقم_الهاتف` VARCHAR(50),
                `رقم_الجوال` VARCHAR(50),
                `البريد_الإلكتروني` VARCHAR(100),
                `الوظيفة` VARCHAR(255),
                `القسم` VARCHAR(100),
                `تاريخ_التوظيف` DATE,
                `تاريخ_انتهاء_العقد` DATE,
                `نوع_العقد` ENUM('دائم', 'مؤقت', 'تدريب', 'استشاري') DEFAULT 'دائم',
                `المرتب_الأساسي` DECIMAL(15,2) DEFAULT 0,
                `البدلات` DECIMAL(15,2) DEFAULT 0,
                `نسبة_العمولة` DECIMAL(5,2) DEFAULT 0,
                `الرصيد` DECIMAL(15,2) DEFAULT 0,
                `حد_السلفة` DECIMAL(15,2) DEFAULT 0,
                `الحالة` ENUM('نشط', 'إجازة', 'مستقيل', 'مفصول', 'غير_نشط', 'متقاعد') DEFAULT 'نشط',
                `جدولة_المرتب_تلقائية` BOOLEAN DEFAULT FALSE,
                `خاضع_لنظام_الحضور` BOOLEAN DEFAULT TRUE,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_التوظيف`)) STORED,
                INDEX `idx_رقم_الموظف` (`رقم_الموظف`),
                INDEX `idx_اسم_الموظف` (`اسم_الموظف`),
                INDEX `idx_رقم_الهوية` (`رقم_الهوية`),
                INDEX `idx_الوظيفة` (`الوظيفة`),
                INDEX `idx_القسم` (`القسم`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_تاريخ_التوظيف` (`تاريخ_التوظيف`),
                INDEX `idx_السنة` (`السنة`),
                FOREIGN KEY (`معرف_التصنيف`) REFERENCES `التصنيفات`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول مهام الموظفين
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `مهام_الموظفين` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_الموظف` INT NOT NULL,
                `عنوان_المهمة` VARCHAR(255) NOT NULL,
                `الوصف` TEXT,
                `تاريخ_البداية` DATE,
                `تاريخ_النهاية_المخطط` DATE,
                `تاريخ_النهاية_الفعلي` DATE,
                `الأولوية` ENUM('منخفضة', 'متوسطة', 'عالية', 'عاجلة') DEFAULT 'متوسطة',
                `الحالة` ENUM('جديدة', 'قيد_التنفيذ', 'مكتملة', 'متأخرة', 'ملغية', 'معلقة') DEFAULT 'جديدة',
                `نسبة_الإنجاز` DECIMAL(5,2) DEFAULT 0,
                `معرف_المشروع` INT,
                `معرف_المرحلة` INT,
                `التقييم` INT CHECK (`التقييم` BETWEEN 1 AND 5),
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_معرف_الموظف` (`معرف_الموظف`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_الأولوية` (`الأولوية`),
                INDEX `idx_تاريخ_النهاية_المخطط` (`تاريخ_النهاية_المخطط`),
                INDEX `idx_معرف_المشروع` (`معرف_المشروع`),
                FOREIGN KEY (`معرف_الموظف`) REFERENCES `الموظفين`(`id`) ON DELETE CASCADE
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول تقييم الموظفين
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `تقييم_الموظفين` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_الموظف` INT NOT NULL,
                `معرف_المقيم` INT,
                `نوع_التقييم` ENUM('شهري', 'ربع_سنوي', 'نصف_سنوي', 'سنوي', 'مشروع', 'مهمة') DEFAULT 'شهري',
                `فترة_التقييم` VARCHAR(50),
                `تاريخ_التقييم` DATE NOT NULL,
                `معايير_التقييم` JSON,
                `الدرجة_الإجمالية` DECIMAL(5,2),
                `المعدل` ENUM('ممتاز', 'جيد_جداً', 'جيد', 'مقبول', 'ضعيف') DEFAULT 'مقبول',
                `نقاط_القوة` TEXT,
                `نقاط_التحسين` TEXT,
                `التوصيات` TEXT,
                `الأهداف_المستقبلية` TEXT,
                `معرف_المرجع` INT COMMENT 'معرف المشروع أو المهمة',
                `نوع_المرجع` VARCHAR(50),
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_التقييم`)) STORED,
                INDEX `idx_معرف_الموظف` (`معرف_الموظف`),
                INDEX `idx_معرف_المقيم` (`معرف_المقيم`),
                INDEX `idx_نوع_التقييم` (`نوع_التقييم`),
                INDEX `idx_تاريخ_التقييم` (`تاريخ_التقييم`),
                INDEX `idx_المعدل` (`المعدل`),
                INDEX `idx_السنة` (`السنة`),
                FOREIGN KEY (`معرف_الموظف`) REFERENCES `الموظفين`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_المقيم`) REFERENCES `الموظفين`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول المعاملات المالية للموظفين
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `معاملات_الموظفين_المالية` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_الموظف` INT NOT NULL,
                `رقم_المعاملة` VARCHAR(50) UNIQUE,
                `نوع_المعاملة` ENUM('راتب', 'عمولة', 'مكافأة', 'بدل', 'سلفة', 'خصم', 'استقطاع') NOT NULL,
                `المبلغ` DECIMAL(15,2) NOT NULL,
                `الوصف` VARCHAR(255),
                `تاريخ_المعاملة` DATE NOT NULL,
                `تاريخ_الاستحقاق` DATE,
                `طريقة_الدفع` ENUM('نقدي', 'شيك', 'تحويل_بنكي', 'بطاقة') DEFAULT 'تحويل_بنكي',
                `رقم_المرجع` VARCHAR(100),
                `معرف_المشروع` INT,
                `معرف_القيد_المحاسبي` INT,
                `الحالة` ENUM('مستحقة', 'مدفوعة', 'متأخرة', 'ملغية') DEFAULT 'مستحقة',
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_المعاملة`)) STORED,
                INDEX `idx_معرف_الموظف` (`معرف_الموظف`),
                INDEX `idx_رقم_المعاملة` (`رقم_المعاملة`),
                INDEX `idx_نوع_المعاملة` (`نوع_المعاملة`),
                INDEX `idx_تاريخ_المعاملة` (`تاريخ_المعاملة`),
                INDEX `idx_تاريخ_الاستحقاق` (`تاريخ_الاستحقاق`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_السنة` (`السنة`),
                FOREIGN KEY (`معرف_الموظف`) REFERENCES `الموظفين`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_القيد_المحاسبي`) REFERENCES `القيود_المحاسبية`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول حضور وانصراف الموظفين
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `حضور_وانصراف_الموظفين` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_الموظف` INT NOT NULL,
                `التاريخ` DATE NOT NULL,
                `اليوم` VARCHAR(20) GENERATED ALWAYS AS (DAYNAME(`التاريخ`)) STORED,
                `وقت_الحضور` TIME,
                `وقت_الانصراف` TIME,
                `ساعات_العمل` DECIMAL(4,2) GENERATED ALWAYS AS (
                    CASE 
                        WHEN `وقت_الحضور` IS NOT NULL AND `وقت_الانصراف` IS NOT NULL 
                        THEN TIME_TO_SEC(TIMEDIFF(`وقت_الانصراف`, `وقت_الحضور`)) / 3600
                        ELSE 0
                    END
                ) STORED,
                `حالة_الحضور` ENUM('حاضر', 'متأخر', 'غائب', 'إجازة', 'مرضية', 'مأمورية', 'عمل_خارجي') DEFAULT 'حاضر',
                `دقائق_التأخير` INT DEFAULT 0,
                `دقائق_المغادرة_المبكرة` INT DEFAULT 0,
                `ساعات_إضافية` DECIMAL(4,2) DEFAULT 0,
                `الموقع` VARCHAR(255),
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`التاريخ`)) STORED,
                `الشهر` INT GENERATED ALWAYS AS (MONTH(`التاريخ`)) STORED,
                UNIQUE KEY `unique_attendance` (`معرف_الموظف`, `التاريخ`),
                INDEX `idx_معرف_الموظف` (`معرف_الموظف`),
                INDEX `idx_التاريخ` (`التاريخ`),
                INDEX `idx_حالة_الحضور` (`حالة_الحضور`),
                INDEX `idx_السنة` (`السنة`),
                INDEX `idx_الشهر` (`الشهر`),
                FOREIGN KEY (`معرف_الموظف`) REFERENCES `الموظفين`(`id`) ON DELETE CASCADE
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول بيانات المستخدم وصلاحيات التطبيق
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `بيانات_مستخدمي_التطبيق` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_الموظف` INT NOT NULL UNIQUE,
                `اسم_المستخدم` VARCHAR(50) NOT NULL UNIQUE,
                `كلمة_المرور` VARCHAR(255) NOT NULL,
                `الدور` ENUM('مدير_عام', 'مدير_مالي', 'محاسب', 'مستخدم', 'مشرف_مشاريع', 'مشرف_تدريب') DEFAULT 'مستخدم',
                `الصلاحيات` JSON,
                `الحالة` ENUM('نشط', 'غير_نشط', 'محظور', 'معلق') DEFAULT 'نشط',
                `آخر_دخول` DATETIME,
                `عدد_محاولات_الدخول` INT DEFAULT 0,
                `تاريخ_انتهاء_كلمة_المرور` DATE,
                `إعدادات_المستخدم` JSON,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_معرف_الموظف` (`معرف_الموظف`),
                INDEX `idx_اسم_المستخدم` (`اسم_المستخدم`),
                INDEX `idx_الدور` (`الدور`),
                INDEX `idx_الحالة` (`الحالة`),
                FOREIGN KEY (`معرف_الموظف`) REFERENCES `الموظفين`(`id`) ON DELETE CASCADE
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول العهد الداخلية للموظفين
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `العهد_الداخلية_للموظفين` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_الموظف` INT NOT NULL,
                `رقم_العهدة` VARCHAR(50) NOT NULL UNIQUE,
                `نوع_العهدة` ENUM('مالية', 'عينية', 'معدات', 'مركبة', 'أخرى') NOT NULL,
                `الوصف` VARCHAR(255) NOT NULL,
                `القيمة` DECIMAL(15,2) DEFAULT 0,
                `تاريخ_الاستلام` DATE NOT NULL,
                `تاريخ_الاستحقاق` DATE,
                `تاريخ_الإرجاع` DATE,
                `الحالة` ENUM('نشطة', 'مرجعة', 'متأخرة', 'مفقودة', 'تالفة') DEFAULT 'نشطة',
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_معرف_الموظف` (`معرف_الموظف`),
                INDEX `idx_رقم_العهدة` (`رقم_العهدة`),
                INDEX `idx_نوع_العهدة` (`نوع_العهدة`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_تاريخ_الاستحقاق` (`تاريخ_الاستحقاق`),
                FOREIGN KEY (`معرف_الموظف`) REFERENCES `الموظفين`(`id`) ON DELETE CASCADE
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول عقود الموظفين
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `عقود_الموظفين` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_الموظف` INT NOT NULL,
                `رقم_العقد` VARCHAR(50) NOT NULL UNIQUE,
                `نوع_العقد` ENUM('توظيف', 'تجديد', 'ترقية', 'نقل', 'إنهاء') DEFAULT 'توظيف',
                `تاريخ_العقد` DATE NOT NULL,
                `تاريخ_البداية` DATE NOT NULL,
                `تاريخ_النهاية` DATE,
                `المرتب` DECIMAL(15,2) NOT NULL,
                `البدلات` DECIMAL(15,2) DEFAULT 0,
                `المزايا` TEXT,
                `الشروط` TEXT,
                `الحالة` ENUM('نشط', 'منتهي', 'ملغي', 'معلق') DEFAULT 'نشط',
                `مسار_الملف` VARCHAR(500),
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_معرف_الموظف` (`معرف_الموظف`),
                INDEX `idx_رقم_العقد` (`رقم_العقد`),
                INDEX `idx_نوع_العقد` (`نوع_العقد`),
                INDEX `idx_تاريخ_العقد` (`تاريخ_العقد`),
                INDEX `idx_الحالة` (`الحالة`),
                FOREIGN KEY (`معرف_الموظف`) REFERENCES `الموظفين`(`id`) ON DELETE CASCADE
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        self.tables_created.update([
            'الموظفين', 'مهام_الموظفين', 'تقييم_الموظفين', 'معاملات_الموظفين_المالية',
            'حضور_وانصراف_الموظفين', 'بيانات_مستخدمي_التطبيق', 'العهد_الداخلية_للموظفين', 'عقود_الموظفين'
        ])
        logger.info("تم إنشاء جداول الموظفين بنجاح")
    
    def _انشاء_جداول_المتدربين(self):
        """إنشاء جداول المتدربين"""
        logger.info("إنشاء جداول المتدربين...")
        
        # جدول المتدربين الرئيسي
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `المتدربين` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `رقم_المتدرب` VARCHAR(50) NOT NULL UNIQUE,
                `معرف_التصنيف` INT,
                `اسم_المتدرب` VARCHAR(255) NOT NULL,
                `رقم_الهوية` VARCHAR(50) UNIQUE,
                `تاريخ_الميلاد` DATE,
                `الجنسية` VARCHAR(50),
                `الجنس` ENUM('ذكر', 'أنثى') NOT NULL,
                `العنوان` VARCHAR(255),
                `المدينة` VARCHAR(100),
                `رقم_الهاتف` VARCHAR(50),
                `رقم_الجوال` VARCHAR(50),
                `البريد_الإلكتروني` VARCHAR(100),
                `المؤهل_العلمي` VARCHAR(100),
                `التخصص` VARCHAR(100),
                `الخبرة_السابقة` TEXT,
                `تاريخ_التسجيل` DATE DEFAULT (CURRENT_DATE),
                `الحالة` ENUM('نشط', 'متخرج', 'منسحب', 'معلق', 'غير_نشط') DEFAULT 'نشط',
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_التسجيل`)) STORED,
                INDEX `idx_رقم_المتدرب` (`رقم_المتدرب`),
                INDEX `idx_اسم_المتدرب` (`اسم_المتدرب`),
                INDEX `idx_رقم_الهوية` (`رقم_الهوية`),
                INDEX `idx_التخصص` (`التخصص`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_السنة` (`السنة`),
                FOREIGN KEY (`معرف_التصنيف`) REFERENCES `التصنيفات`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        self.tables_created.add('المتدربين')
        logger.info("تم إنشاء جداول المتدربين بنجاح")
    
    def _انشاء_جداول_الموردين(self):
        """إنشاء جداول الموردين وجداولها الفرعية"""
        logger.info("إنشاء جداول الموردين...")
        
        # جدول الموردين الرئيسي
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `الموردين` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `رقم_المورد` VARCHAR(50) NOT NULL UNIQUE,
                `معرف_التصنيف` INT,
                `اسم_المورد` VARCHAR(255) NOT NULL,
                `نوع_المورد` ENUM('فرد', 'شركة', 'مؤسسة') DEFAULT 'شركة',
                `رقم_السجل_التجاري` VARCHAR(50),
                `الرقم_الضريبي` VARCHAR(50),
                `العنوان` VARCHAR(255),
                `المدينة` VARCHAR(100),
                `المنطقة` VARCHAR(100),
                `الرمز_البريدي` VARCHAR(20),
                `رقم_الهاتف` VARCHAR(50),
                `رقم_الجوال` VARCHAR(50),
                `البريد_الإلكتروني` VARCHAR(100),
                `الموقع_الإلكتروني` VARCHAR(255),
                `نوع_النشاط` VARCHAR(100),
                `تاريخ_التسجيل` DATE DEFAULT (CURRENT_DATE),
                `رصيد_المورد` DECIMAL(15,2) DEFAULT 0,
                `حد_الائتمان` DECIMAL(15,2) DEFAULT 0,
                `التقييم` INT DEFAULT 0 CHECK (`التقييم` BETWEEN 0 AND 5),
                `شروط_الدفع` VARCHAR(100),
                `الحالة` ENUM('نشط', 'غير_نشط', 'محظور', 'معلق') DEFAULT 'نشط',
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_التسجيل`)) STORED,
                INDEX `idx_رقم_المورد` (`رقم_المورد`),
                INDEX `idx_اسم_المورد` (`اسم_المورد`),
                INDEX `idx_نوع_المورد` (`نوع_المورد`),
                INDEX `idx_رقم_السجل_التجاري` (`رقم_السجل_التجاري`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_السنة` (`السنة`),
                FOREIGN KEY (`معرف_التصنيف`) REFERENCES `التصنيفات`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول معاملات الموردين المالية
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `معاملات_الموردين_المالية` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_المورد` INT NOT NULL,
                `رقم_المعاملة` VARCHAR(50) UNIQUE,
                `نوع_المعاملة` ENUM('شراء', 'دفعة', 'مردود', 'خصم', 'إضافة', 'تسوية') NOT NULL,
                `المبلغ` DECIMAL(15,2) NOT NULL,
                `الوصف` VARCHAR(255),
                `تاريخ_المعاملة` DATE NOT NULL,
                `تاريخ_الاستحقاق` DATE,
                `طريقة_الدفع` ENUM('نقدي', 'شيك', 'تحويل_بنكي', 'بطاقة', 'آجل') DEFAULT 'آجل',
                `رقم_المرجع` VARCHAR(100),
                `رقم_الفاتورة` VARCHAR(100),
                `معرف_المشروع` INT,
                `معرف_القيد_المحاسبي` INT,
                `الحالة` ENUM('مكتملة', 'معلقة', 'ملغية') DEFAULT 'مكتملة',
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_المعاملة`)) STORED,
                INDEX `idx_معرف_المورد` (`معرف_المورد`),
                INDEX `idx_رقم_المعاملة` (`رقم_المعاملة`),
                INDEX `idx_نوع_المعاملة` (`نوع_المعاملة`),
                INDEX `idx_تاريخ_المعاملة` (`تاريخ_المعاملة`),
                INDEX `idx_تاريخ_الاستحقاق` (`تاريخ_الاستحقاق`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_السنة` (`السنة`),
                FOREIGN KEY (`معرف_المورد`) REFERENCES `الموردين`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_القيد_المحاسبي`) REFERENCES `القيود_المحاسبية`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول تفاصيل فواتير الموردين
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `تفاصيل_فواتير_الموردين` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_المعاملة` INT NOT NULL,
                `الصنف` VARCHAR(255) NOT NULL,
                `الوصف` TEXT,
                `الكمية` DECIMAL(15,3) NOT NULL,
                `الوحدة` VARCHAR(50),
                `سعر_الوحدة` DECIMAL(15,2) NOT NULL,
                `الإجمالي` DECIMAL(15,2) GENERATED ALWAYS AS (`الكمية` * `سعر_الوحدة`) STORED,
                `نسبة_الخصم` DECIMAL(5,2) DEFAULT 0,
                `مبلغ_الخصم` DECIMAL(15,2) GENERATED ALWAYS AS (`الإجمالي` * `نسبة_الخصم` / 100) STORED,
                `الصافي` DECIMAL(15,2) GENERATED ALWAYS AS (`الإجمالي` - `مبلغ_الخصم`) STORED,
                `ملاحظات` TEXT,
                INDEX `idx_معرف_المعاملة` (`معرف_المعاملة`),
                INDEX `idx_الصنف` (`الصنف`),
                FOREIGN KEY (`معرف_المعاملة`) REFERENCES `معاملات_الموردين_المالية`(`id`) ON DELETE CASCADE
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول مردودات الموردين
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `مردودات_الموردين` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_المورد` INT NOT NULL,
                `رقم_المردود` VARCHAR(50) NOT NULL UNIQUE,
                `تاريخ_المردود` DATE NOT NULL,
                `سبب_المردود` TEXT NOT NULL,
                `إجمالي_المبلغ` DECIMAL(15,2) DEFAULT 0,
                `الحالة` ENUM('مسودة', 'معتمد', 'مرفوض', 'مكتمل') DEFAULT 'مسودة',
                `معرف_القيد_المحاسبي` INT,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_معرف_المورد` (`معرف_المورد`),
                INDEX `idx_رقم_المردود` (`رقم_المردود`),
                INDEX `idx_تاريخ_المردود` (`تاريخ_المردود`),
                INDEX `idx_الحالة` (`الحالة`),
                FOREIGN KEY (`معرف_المورد`) REFERENCES `الموردين`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_القيد_المحاسبي`) REFERENCES `القيود_المحاسبية`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        self.tables_created.update(['الموردين', 'معاملات_الموردين_المالية', 'تفاصيل_فواتير_الموردين', 'مردودات_الموردين'])
        logger.info("تم إنشاء جداول الموردين بنجاح")
    
    def _انشاء_جداول_التدريب(self):
        """إنشاء جداول التدريب وجداولها الفرعية"""
        logger.info("إنشاء جداول التدريب...")
        
        # جدول البرامج التدريبية
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `البرامج_التدريبية` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `رقم_البرنامج` VARCHAR(50) NOT NULL UNIQUE,
                `معرف_التصنيف` INT,
                `اسم_البرنامج` VARCHAR(255) NOT NULL,
                `الوصف` TEXT,
                `نوع_البرنامج` ENUM('تقني', 'إداري', 'مهني', 'أكاديمي', 'تطوير_ذاتي') DEFAULT 'تقني',
                `المستوى` ENUM('مبتدئ', 'متوسط', 'متقدم', 'خبير') DEFAULT 'مبتدئ',
                `المدة_بالساعات` INT DEFAULT 0,
                `عدد_الأيام` INT DEFAULT 0,
                `الرسوم` DECIMAL(15,2) DEFAULT 0,
                `الحد_الأدنى_للمشتركين` INT DEFAULT 1,
                `الحد_الأقصى_للمشتركين` INT DEFAULT 50,
                `متطلبات_القبول` TEXT,
                `المخرجات_المتوقعة` TEXT,
                `نوع_الشهادة` VARCHAR(100),
                `الحالة` ENUM('نشط', 'غير_نشط', 'مؤرشف') DEFAULT 'نشط',
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_رقم_البرنامج` (`رقم_البرنامج`),
                INDEX `idx_اسم_البرنامج` (`اسم_البرنامج`),
                INDEX `idx_نوع_البرنامج` (`نوع_البرنامج`),
                INDEX `idx_المستوى` (`المستوى`),
                INDEX `idx_الحالة` (`الحالة`),
                FOREIGN KEY (`معرف_التصنيف`) REFERENCES `التصنيفات`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول المدربين (يجب إنشاؤه قبل المجموعات التدريبية)
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `المدربين` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `رقم_المدرب` VARCHAR(50) NOT NULL UNIQUE,
                `معرف_التصنيف` INT,
                `اسم_المدرب` VARCHAR(255) NOT NULL,
                `رقم_الهوية` VARCHAR(50),
                `المؤهل_العلمي` VARCHAR(100),
                `التخصص` VARCHAR(100),
                `سنوات_الخبرة` INT DEFAULT 0,
                `الشهادات_المهنية` TEXT,
                `رقم_الهاتف` VARCHAR(50),
                `رقم_الجوال` VARCHAR(50),
                `البريد_الإلكتروني` VARCHAR(100),
                `نوع_المدرب` ENUM('داخلي', 'خارجي', 'استشاري') DEFAULT 'خارجي',
                `أتعاب_الساعة` DECIMAL(15,2) DEFAULT 0,
                `أتعاب_اليوم` DECIMAL(15,2) DEFAULT 0,
                `التقييم` DECIMAL(3,2) DEFAULT 0 CHECK (`التقييم` BETWEEN 0 AND 5),
                `الحالة` ENUM('نشط', 'غير_نشط', 'معلق') DEFAULT 'نشط',
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_رقم_المدرب` (`رقم_المدرب`),
                INDEX `idx_اسم_المدرب` (`اسم_المدرب`),
                INDEX `idx_التخصص` (`التخصص`),
                INDEX `idx_نوع_المدرب` (`نوع_المدرب`),
                INDEX `idx_الحالة` (`الحالة`),
                FOREIGN KEY (`معرف_التصنيف`) REFERENCES `التصنيفات`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول المجموعات التدريبية (بعد إنشاء المدربين)
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `المجموعات_التدريبية` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_البرنامج` INT NOT NULL,
                `رقم_المجموعة` VARCHAR(50) NOT NULL,
                `اسم_المجموعة` VARCHAR(255) NOT NULL,
                `تاريخ_البداية` DATE NOT NULL,
                `تاريخ_النهاية` DATE NOT NULL,
                `أوقات_التدريب` VARCHAR(255),
                `مكان_التدريب` VARCHAR(255),
                `معرف_المدرب_الرئيسي` INT,
                `عدد_المشتركين` INT DEFAULT 0,
                `الحد_الأقصى_للمشتركين` INT DEFAULT 50,
                `رسوم_المجموعة` DECIMAL(15,2) DEFAULT 0,
                `الحالة` ENUM('مخططة', 'جارية', 'مكتملة', 'ملغية', 'معلقة') DEFAULT 'مخططة',
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_البداية`)) STORED,
                INDEX `idx_معرف_البرنامج` (`معرف_البرنامج`),
                INDEX `idx_رقم_المجموعة` (`رقم_المجموعة`),
                INDEX `idx_تاريخ_البداية` (`تاريخ_البداية`),
                INDEX `idx_معرف_المدرب_الرئيسي` (`معرف_المدرب_الرئيسي`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_السنة` (`السنة`),
                FOREIGN KEY (`معرف_البرنامج`) REFERENCES `البرامج_التدريبية`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_المدرب_الرئيسي`) REFERENCES `المدربين`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول المشتركين في التدريب
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `المشتركين_في_التدريب` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_المجموعة` INT NOT NULL,
                `معرف_المتدرب` INT NOT NULL,
                `تاريخ_التسجيل` DATE DEFAULT (CURRENT_DATE),
                `الرسوم_المدفوعة` DECIMAL(15,2) DEFAULT 0,
                `الرسوم_المتبقية` DECIMAL(15,2) DEFAULT 0,
                `حالة_الدفع` ENUM('مدفوع_كاملاً', 'مدفوع_جزئياً', 'غير_مدفوع') DEFAULT 'غير_مدفوع',
                `نسبة_الحضور` DECIMAL(5,2) DEFAULT 0,
                `الدرجة_النهائية` DECIMAL(5,2) DEFAULT 0,
                `حالة_الاجتياز` ENUM('ناجح', 'راسب', 'غير_مكتمل') DEFAULT 'غير_مكتمل',
                `تاريخ_الاجتياز` DATE,
                `رقم_الشهادة` VARCHAR(50),
                `الحالة` ENUM('مسجل', 'حاضر', 'منسحب', 'مكتمل', 'معلق') DEFAULT 'مسجل',
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY `unique_enrollment` (`معرف_المجموعة`, `معرف_المتدرب`),
                INDEX `idx_معرف_المجموعة` (`معرف_المجموعة`),
                INDEX `idx_معرف_المتدرب` (`معرف_المتدرب`),
                INDEX `idx_حالة_الدفع` (`حالة_الدفع`),
                INDEX `idx_الحالة` (`الحالة`),
                FOREIGN KEY (`معرف_المجموعة`) REFERENCES `المجموعات_التدريبية`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_المتدرب`) REFERENCES `المتدربين`(`id`) ON DELETE CASCADE
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول الشهادات
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `الشهادات` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_المشترك` INT NOT NULL,
                `رقم_الشهادة` VARCHAR(50) NOT NULL UNIQUE,
                `نوع_الشهادة` ENUM('حضور', 'اجتياز', 'تميز', 'مشاركة') DEFAULT 'حضور',
                `تاريخ_الإصدار` DATE NOT NULL,
                `تاريخ_الانتهاء` DATE,
                `الدرجة` DECIMAL(5,2),
                `التقدير` VARCHAR(50),
                `مسار_الملف` VARCHAR(500),
                `حالة_الطباعة` ENUM('غير_مطبوعة', 'مطبوعة', 'مسلمة') DEFAULT 'غير_مطبوعة',
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_معرف_المشترك` (`معرف_المشترك`),
                INDEX `idx_رقم_الشهادة` (`رقم_الشهادة`),
                INDEX `idx_نوع_الشهادة` (`نوع_الشهادة`),
                INDEX `idx_تاريخ_الإصدار` (`تاريخ_الإصدار`),
                FOREIGN KEY (`معرف_المشترك`) REFERENCES `المشتركين_في_التدريب`(`id`) ON DELETE CASCADE
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول مصروفات التدريب
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `مصروفات_التدريب` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_المجموعة` INT,
                `معرف_البرنامج` INT,
                `نوع_المصروف` VARCHAR(100) NOT NULL,
                `الوصف` VARCHAR(255) NOT NULL,
                `المبلغ` DECIMAL(15,2) NOT NULL,
                `تاريخ_المصروف` DATE NOT NULL,
                `معرف_المورد` INT,
                `رقم_الفاتورة` VARCHAR(100),
                `طريقة_الدفع` ENUM('نقدي', 'شيك', 'تحويل_بنكي', 'بطاقة') DEFAULT 'نقدي',
                `معرف_القيد_المحاسبي` INT,
                `معتمد` BOOLEAN DEFAULT FALSE,
                `معتمد_بواسطة` VARCHAR(50),
                `تاريخ_الاعتماد` DATETIME,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX `idx_معرف_المجموعة` (`معرف_المجموعة`),
                INDEX `idx_معرف_البرنامج` (`معرف_البرنامج`),
                INDEX `idx_نوع_المصروف` (`نوع_المصروف`),
                INDEX `idx_تاريخ_المصروف` (`تاريخ_المصروف`),
                INDEX `idx_معرف_المورد` (`معرف_المورد`),
                FOREIGN KEY (`معرف_المجموعة`) REFERENCES `المجموعات_التدريبية`(`id`) ON DELETE SET NULL,
                FOREIGN KEY (`معرف_البرنامج`) REFERENCES `البرامج_التدريبية`(`id`) ON DELETE SET NULL,
                FOREIGN KEY (`معرف_المورد`) REFERENCES `الموردين`(`id`) ON DELETE SET NULL,
                FOREIGN KEY (`معرف_القيد_المحاسبي`) REFERENCES `القيود_المحاسبية`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        self.tables_created.update([
            'البرامج_التدريبية', 'المجموعات_التدريبية', 'المدربين', 
            'المشتركين_في_التدريب', 'الشهادات', 'مصروفات_التدريب'
        ])
        logger.info("تم إنشاء جداول التدريب بنجاح")
    
    def _انشاء_جداول_الايرادات(self):
        """إنشاء جداول الإيرادات"""
        logger.info("إنشاء جداول الإيرادات...")
        
        # جدول الإيرادات الرئيسي
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `الإيرادات` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `رقم_الإيراد` VARCHAR(50) NOT NULL UNIQUE,
                `معرف_التصنيف` INT,
                `نوع_الإيراد` ENUM('مشاريع', 'تدريب', 'استشارات', 'إيجارات', 'استثمارات', 'أخرى') NOT NULL,
                `مصدر_الإيراد` VARCHAR(255) NOT NULL,
                `الوصف` VARCHAR(255) NOT NULL,
                `المبلغ` DECIMAL(15,2) NOT NULL,
                `تاريخ_الإيراد` DATE NOT NULL,
                `معرف_العميل` INT,
                `معرف_المشروع` INT,
                `معرف_المجموعة_التدريبية` INT,
                `طريقة_الاستلام` ENUM('نقدي', 'شيك', 'تحويل_بنكي', 'بطاقة') DEFAULT 'تحويل_بنكي',
                `رقم_المرجع` VARCHAR(100),
                `معرف_القيد_المحاسبي` INT,
                `معتمد` BOOLEAN DEFAULT FALSE,
                `معتمد_بواسطة` VARCHAR(50),
                `تاريخ_الاعتماد` DATETIME,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_الإيراد`)) STORED,
                `الشهر` INT GENERATED ALWAYS AS (MONTH(`تاريخ_الإيراد`)) STORED,
                INDEX `idx_رقم_الإيراد` (`رقم_الإيراد`),
                INDEX `idx_نوع_الإيراد` (`نوع_الإيراد`),
                INDEX `idx_تاريخ_الإيراد` (`تاريخ_الإيراد`),
                INDEX `idx_معرف_العميل` (`معرف_العميل`),
                INDEX `idx_معرف_المشروع` (`معرف_المشروع`),
                INDEX `idx_السنة` (`السنة`),
                INDEX `idx_الشهر` (`الشهر`),
                FOREIGN KEY (`معرف_التصنيف`) REFERENCES `التصنيفات`(`id`) ON DELETE SET NULL,
                FOREIGN KEY (`معرف_العميل`) REFERENCES `العملاء`(`id`) ON DELETE SET NULL,
                FOREIGN KEY (`معرف_المجموعة_التدريبية`) REFERENCES `المجموعات_التدريبية`(`id`) ON DELETE SET NULL,
                FOREIGN KEY (`معرف_القيد_المحاسبي`) REFERENCES `القيود_المحاسبية`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        self.tables_created.add('الإيرادات')
        logger.info("تم إنشاء جداول الإيرادات بنجاح")
    
    def _انشاء_جداول_المصروفات(self):
        """إنشاء جداول المصروفات"""
        logger.info("إنشاء جداول المصروفات...")
        
        # جدول المصروفات الرئيسي
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `المصروفات` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `رقم_المصروف` VARCHAR(50) NOT NULL UNIQUE,
                `معرف_التصنيف` INT,
                `نوع_المصروف` ENUM('مصروفات_الشركة', 'مصروفات_إدارية', 'مصروفات_تسويق', 'خسائر_مشاريع', 'مصروفات_تدريب', 'أخرى') NOT NULL,
                `تصنيف_فرعي` VARCHAR(100),
                `الوصف` VARCHAR(255) NOT NULL,
                `المبلغ` DECIMAL(15,2) NOT NULL,
                `تاريخ_المصروف` DATE NOT NULL,
                `معرف_المورد` INT,
                `معرف_المشروع` INT,
                `معرف_المجموعة_التدريبية` INT,
                `رقم_الفاتورة` VARCHAR(100),
                `طريقة_الدفع` ENUM('نقدي', 'شيك', 'تحويل_بنكي', 'بطاقة') DEFAULT 'نقدي',
                `رقم_المرجع` VARCHAR(100),
                `معرف_القيد_المحاسبي` INT,
                `معتمد` BOOLEAN DEFAULT FALSE,
                `معتمد_بواسطة` VARCHAR(50),
                `تاريخ_الاعتماد` DATETIME,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_المصروف`)) STORED,
                `الشهر` INT GENERATED ALWAYS AS (MONTH(`تاريخ_المصروف`)) STORED,
                INDEX `idx_رقم_المصروف` (`رقم_المصروف`),
                INDEX `idx_نوع_المصروف` (`نوع_المصروف`),
                INDEX `idx_تاريخ_المصروف` (`تاريخ_المصروف`),
                INDEX `idx_معرف_المورد` (`معرف_المورد`),
                INDEX `idx_معرف_المشروع` (`معرف_المشروع`),
                INDEX `idx_السنة` (`السنة`),
                INDEX `idx_الشهر` (`الشهر`),
                FOREIGN KEY (`معرف_التصنيف`) REFERENCES `التصنيفات`(`id`) ON DELETE SET NULL,
                FOREIGN KEY (`معرف_المورد`) REFERENCES `الموردين`(`id`) ON DELETE SET NULL,
                FOREIGN KEY (`معرف_المجموعة_التدريبية`) REFERENCES `المجموعات_التدريبية`(`id`) ON DELETE SET NULL,
                FOREIGN KEY (`معرف_القيد_المحاسبي`) REFERENCES `القيود_المحاسبية`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        self.tables_created.add('المصروفات')
        logger.info("تم إنشاء جداول المصروفات بنجاح")
    
    def _انشاء_جداول_الالتزامات(self):
        """إنشاء جداول الالتزامات"""
        logger.info("إنشاء جداول الالتزامات...")
        
        # جدول الالتزامات الرئيسي
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `الالتزامات` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `رقم_الالتزام` VARCHAR(50) NOT NULL UNIQUE,
                `معرف_التصنيف` INT,
                `نوع_الالتزام` ENUM('قروض', 'ديون_موردين', 'رواتب_مستحقة', 'ضرائب', 'تأمينات', 'إيجارات', 'أخرى') NOT NULL,
                `الوصف` VARCHAR(255) NOT NULL,
                `المبلغ_الأصلي` DECIMAL(15,2) NOT NULL,
                `المبلغ_المدفوع` DECIMAL(15,2) DEFAULT 0,
                `المبلغ_المتبقي` DECIMAL(15,2) GENERATED ALWAYS AS (`المبلغ_الأصلي` - `المبلغ_المدفوع`) STORED,
                `تاريخ_الالتزام` DATE NOT NULL,
                `تاريخ_الاستحقاق` DATE NOT NULL,
                `معرف_الدائن` INT,
                `نوع_الدائن` ENUM('مورد', 'موظف', 'عميل', 'جهة_خارجية') DEFAULT 'جهة_خارجية',
                `معدل_الفائدة` DECIMAL(5,2) DEFAULT 0,
                `شروط_السداد` TEXT,
                `الحالة` ENUM('نشط', 'مسدد', 'متأخر', 'معاد_جدولته', 'ملغي') DEFAULT 'نشط',
                `الأولوية` ENUM('منخفضة', 'متوسطة', 'عالية', 'عاجلة') DEFAULT 'متوسطة',
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_الالتزام`)) STORED,
                INDEX `idx_رقم_الالتزام` (`رقم_الالتزام`),
                INDEX `idx_نوع_الالتزام` (`نوع_الالتزام`),
                INDEX `idx_تاريخ_الالتزام` (`تاريخ_الالتزام`),
                INDEX `idx_تاريخ_الاستحقاق` (`تاريخ_الاستحقاق`),
                INDEX `idx_معرف_الدائن` (`معرف_الدائن`),
                INDEX `idx_الحالة` (`الحالة`),
                INDEX `idx_السنة` (`السنة`),
                FOREIGN KEY (`معرف_التصنيف`) REFERENCES `التصنيفات`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # جدول دفعات الالتزامات
        self.تنفيذ_استعلام("""
            CREATE TABLE IF NOT EXISTS `دفعات_الالتزامات` (
                `id` INT PRIMARY KEY AUTO_INCREMENT,
                `معرف_الالتزام` INT NOT NULL,
                `رقم_الدفعة` VARCHAR(50),
                `المبلغ` DECIMAL(15,2) NOT NULL,
                `تاريخ_الدفعة` DATE NOT NULL,
                `طريقة_الدفع` ENUM('نقدي', 'شيك', 'تحويل_بنكي', 'بطاقة') DEFAULT 'تحويل_بنكي',
                `رقم_المرجع` VARCHAR(100),
                `معرف_القيد_المحاسبي` INT,
                `ملاحظات` TEXT,
                `المستخدم` VARCHAR(50),
                `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX `idx_معرف_الالتزام` (`معرف_الالتزام`),
                INDEX `idx_تاريخ_الدفعة` (`تاريخ_الدفعة`),
                INDEX `idx_معرف_القيد_المحاسبي` (`معرف_القيد_المحاسبي`),
                FOREIGN KEY (`معرف_الالتزام`) REFERENCES `الالتزامات`(`id`) ON DELETE CASCADE,
                FOREIGN KEY (`معرف_القيد_المحاسبي`) REFERENCES `القيود_المحاسبية`(`id`) ON DELETE SET NULL
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        self.tables_created.update(['الالتزامات', 'دفعات_الالتزامات'])
        logger.info("تم إنشاء جداول الالتزامات بنجاح")
    
    def _انشاء_الفهارس(self):
        """إنشاء الفهارس المطلوبة لتحسين الأداء"""
        logger.info("إنشاء الفهارس...")
        
        indexes = [
            # فهارس الأداء للجداول الأساسية
            "CREATE INDEX IF NOT EXISTS `idx_users_last_login` ON `المستخدمين`(`آخر_دخول`)",
            "CREATE INDEX IF NOT EXISTS `idx_logs_date_level` ON `سجلات_النظام`(`التاريخ`, `المستوى`)",
            "CREATE INDEX IF NOT EXISTS `idx_attachments_size` ON `المرفقات`(`حجم_الملف`)",
            
            # فهارس المحاسبة
            "CREATE INDEX IF NOT EXISTS `idx_accounts_balance` ON `شجرة_الحسابات`(`الرصيد_الحالي`)",
            "CREATE INDEX IF NOT EXISTS `idx_entries_amount` ON `القيود_المحاسبية`(`إجمالي_المدين`, `إجمالي_الدائن`)",
            "CREATE INDEX IF NOT EXISTS `idx_entry_details_amount` ON `تفاصيل_القيود_المحاسبية`(`المبلغ_المدين`, `المبلغ_الدائن`)",
            
            # فهارس المشاريع
            "CREATE INDEX IF NOT EXISTS `idx_projects_value` ON `المشاريع`(`قيمة_المشروع`)",
            "CREATE INDEX IF NOT EXISTS `idx_projects_progress` ON `المشاريع`(`نسبة_الإنجاز`)",
            "CREATE INDEX IF NOT EXISTS `idx_project_phases_progress` ON `مراحل_المشروع`(`نسبة_الإنجاز`)",
            
            # فهارس العملاء والموردين
            "CREATE INDEX IF NOT EXISTS `idx_clients_balance` ON `العملاء`(`رصيد_العميل`)",
            "CREATE INDEX IF NOT EXISTS `idx_suppliers_balance` ON `الموردين`(`رصيد_المورد`)",
            
            # فهارس الموظفين
            "CREATE INDEX IF NOT EXISTS `idx_employees_salary` ON `الموظفين`(`المرتب_الأساسي`)",
            "CREATE INDEX IF NOT EXISTS `idx_employees_balance` ON `الموظفين`(`الرصيد`)",
            
            # فهارس التدريب
            "CREATE INDEX IF NOT EXISTS `idx_training_fees` ON `البرامج_التدريبية`(`الرسوم`)",
            "CREATE INDEX IF NOT EXISTS `idx_groups_capacity` ON `المجموعات_التدريبية`(`عدد_المشتركين`)",
            
            # فهارس الإيرادات والمصروفات
            "CREATE INDEX IF NOT EXISTS `idx_revenues_amount` ON `الإيرادات`(`المبلغ`)",
            "CREATE INDEX IF NOT EXISTS `idx_expenses_amount` ON `المصروفات`(`المبلغ`)",
            
            # فهارس مركبة للتقارير
            "CREATE INDEX IF NOT EXISTS `idx_projects_client_status` ON `المشاريع`(`معرف_العميل`, `الحالة`)",
            "CREATE INDEX IF NOT EXISTS `idx_expenses_type_date` ON `المصروفات`(`نوع_المصروف`, `تاريخ_المصروف`)",
            "CREATE INDEX IF NOT EXISTS `idx_revenues_type_date` ON `الإيرادات`(`نوع_الإيراد`, `تاريخ_الإيراد`)",
        ]
        
        for index_sql in indexes:
            try:
                self.تنفيذ_استعلام(index_sql)
                self.indexes_created.add(index_sql.split('`')[1])
            except Exception as e:
                logger.warning(f"تعذر إنشاء فهرس: {e}")
        
        logger.info(f"تم إنشاء {len(self.indexes_created)} فهرس بنجاح")
    
    def _انشاء_المشغلات(self):
        """إنشاء المشغلات (Triggers) للحفاظ على تناسق البيانات"""
        logger.info("إنشاء المشغلات...")
        
        triggers = [
            # مشغل تحديث رصيد العميل عند إضافة معاملة مالية
            """
            CREATE TRIGGER IF NOT EXISTS `update_client_balance_after_transaction`
            AFTER INSERT ON `معاملات_العملاء_المالية`
            FOR EACH ROW
            BEGIN
                IF NEW.نوع_المعاملة = 'دفعة' THEN
                    UPDATE `العملاء` SET `رصيد_العميل` = `رصيد_العميل` + NEW.المبلغ WHERE `id` = NEW.معرف_العميل;
                ELSEIF NEW.نوع_المعاملة = 'فاتورة' THEN
                    UPDATE `العملاء` SET `رصيد_العميل` = `رصيد_العميل` - NEW.المبلغ WHERE `id` = NEW.معرف_العميل;
                END IF;
            END
            """,
            
            # مشغل تحديث رصيد المورد عند إضافة معاملة مالية
            """
            CREATE TRIGGER IF NOT EXISTS `update_supplier_balance_after_transaction`
            AFTER INSERT ON `معاملات_الموردين_المالية`
            FOR EACH ROW
            BEGIN
                IF NEW.نوع_المعاملة = 'شراء' THEN
                    UPDATE `الموردين` SET `رصيد_المورد` = `رصيد_المورد` + NEW.المبلغ WHERE `id` = NEW.معرف_المورد;
                ELSEIF NEW.نوع_المعاملة = 'دفعة' THEN
                    UPDATE `الموردين` SET `رصيد_المورد` = `رصيد_المورد` - NEW.المبلغ WHERE `id` = NEW.معرف_المورد;
                END IF;
            END
            """,
            
            # مشغل تحديث رصيد الموظف عند إضافة معاملة مالية
            """
            CREATE TRIGGER IF NOT EXISTS `update_employee_balance_after_transaction`
            AFTER INSERT ON `معاملات_الموظفين_المالية`
            FOR EACH ROW
            BEGIN
                IF NEW.نوع_المعاملة IN ('راتب', 'عمولة', 'مكافأة', 'بدل') THEN
                    UPDATE `الموظفين` SET `الرصيد` = `الرصيد` + NEW.المبلغ WHERE `id` = NEW.معرف_الموظف;
                ELSEIF NEW.نوع_المعاملة IN ('سلفة', 'خصم', 'استقطاع') THEN
                    UPDATE `الموظفين` SET `الرصيد` = `الرصيد` - NEW.المبلغ WHERE `id` = NEW.معرف_الموظف;
                END IF;
            END
            """,
            
            # مشغل تحديث إجماليات القيد المحاسبي
            """
            CREATE TRIGGER IF NOT EXISTS `update_entry_totals_after_detail_insert`
            AFTER INSERT ON `تفاصيل_القيود_المحاسبية`
            FOR EACH ROW
            BEGIN
                UPDATE `القيود_المحاسبية` 
                SET 
                    `إجمالي_المدين` = (SELECT COALESCE(SUM(`المبلغ_المدين`), 0) FROM `تفاصيل_القيود_المحاسبية` WHERE `معرف_القيد` = NEW.معرف_القيد),
                    `إجمالي_الدائن` = (SELECT COALESCE(SUM(`المبلغ_الدائن`), 0) FROM `تفاصيل_القيود_المحاسبية` WHERE `معرف_القيد` = NEW.معرف_القيد)
                WHERE `id` = NEW.معرف_القيد;
            END
            """,
            
            # مشغل تحديث عدد المشتركين في المجموعة التدريبية
            """
            CREATE TRIGGER IF NOT EXISTS `update_group_participants_count`
            AFTER INSERT ON `المشتركين_في_التدريب`
            FOR EACH ROW
            BEGIN
                UPDATE `المجموعات_التدريبية` 
                SET `عدد_المشتركين` = (
                    SELECT COUNT(*) FROM `المشتركين_في_التدريب` 
                    WHERE `معرف_المجموعة` = NEW.معرف_المجموعة AND `الحالة` IN ('مسجل', 'حاضر', 'مكتمل')
                )
                WHERE `id` = NEW.معرف_المجموعة;
            END
            """,
            
            # مشغل تسجيل العمليات في سجل النظام
            """
            CREATE TRIGGER IF NOT EXISTS `log_important_operations`
            AFTER INSERT ON `القيود_المحاسبية`
            FOR EACH ROW
            BEGIN
                INSERT INTO `سجلات_النظام` (`المستوى`, `الموديول`, `العملية`, `الرسالة`, `المستخدم`, `نوع_المرجع`, `معرف_المرجع`)
                VALUES ('معلومات', 'المحاسبة', 'إضافة_قيد', CONCAT('تم إضافة قيد محاسبي جديد رقم: ', NEW.رقم_القيد), NEW.المستخدم, 'قيد_محاسبي', NEW.id);
            END
            """
        ]
        
        for trigger_sql in triggers:
            try:
                self.تنفيذ_استعلام(trigger_sql)
                trigger_name = trigger_sql.split('`')[1]
                self.triggers_created.add(trigger_name)
            except Exception as e:
                logger.warning(f"تعذر إنشاء مشغل: {e}")
        
        logger.info(f"تم إنشاء {len(self.triggers_created)} مشغل بنجاح")
    
    def _ادراج_البيانات_الافتراضية(self):
        """إدراج البيانات الافتراضية"""
        logger.info("إدراج البيانات الافتراضية...")
        
        # إعدادات النظام الافتراضية
        default_settings = [
            ('app_name', 'منظومة المهندس v3', 'string', 'اسم التطبيق', False, 'عام'),
            ('app_version', '3.0.0', 'string', 'إصدار التطبيق', False, 'عام'),
            ('default_currency', 'ريال سعودي', 'string', 'العملة الافتراضية', True, 'مالي'),
            ('backup_enabled', 'true', 'boolean', 'تفعيل النسخ الاحتياطي', True, 'نظام'),
            ('session_timeout', '3600', 'number', 'مهلة انتهاء الجلسة (ثانية)', True, 'أمان'),
            ('decimal_places', '2', 'number', 'عدد الخانات العشرية', True, 'مالي'),
            ('tax_rate', '15', 'number', 'نسبة الضريبة المضافة (%)', True, 'مالي'),
            ('company_name', 'شركة المهندس للمقاولات والتدريب', 'string', 'اسم الشركة', True, 'عام'),
            ('company_address', 'الرياض، المملكة العربية السعودية', 'string', 'عنوان الشركة', True, 'عام'),
            ('company_phone', '+966-11-1234567', 'string', 'هاتف الشركة', True, 'عام'),
            ('company_email', 'info@engineer-company.com', 'string', 'بريد الشركة الإلكتروني', True, 'عام'),
            ('fiscal_year_start', '01-01', 'string', 'بداية السنة المالية (شهر-يوم)', True, 'مالي'),
            ('auto_backup_time', '02:00', 'string', 'وقت النسخ الاحتياطي التلقائي', True, 'نظام'),
            ('max_login_attempts', '5', 'number', 'عدد محاولات الدخول المسموحة', True, 'أمان'),
            ('password_expiry_days', '90', 'number', 'مدة انتهاء كلمة المرور (أيام)', True, 'أمان'),
        ]
        
        for setting in default_settings:
            try:
                self.ادراج_بيانات('إعدادات_النظام', {
                    'المفتاح': setting[0],
                    'القيمة': setting[1],
                    'نوع_البيانات': setting[2],
                    'الوصف': setting[3],
                    'قابل_للتعديل': setting[4],
                    'المجموعة': setting[5],
                    'المستخدم': 'النظام'
                })
            except:
                pass  # تجاهل الأخطاء في حالة وجود البيانات مسبقاً
        
        # مستخدم افتراضي
        try:
            self.ادراج_بيانات('المستخدمين', {
                'اسم_المستخدم': 'admin',
                'كلمة_المرور': hashlib.sha256('admin123'.encode()).hexdigest(),
                'الاسم_الكامل': 'المدير العام',
                'البريد_الإلكتروني': 'admin@engineer-company.com',
                'الدور': 'مدير_عام',
                'الصلاحيات': json.dumps({
                    'المحاسبة': ['قراءة', 'كتابة', 'حذف', 'اعتماد'],
                    'المشاريع': ['قراءة', 'كتابة', 'حذف', 'اعتماد'],
                    'الموظفين': ['قراءة', 'كتابة', 'حذف'],
                    'العملاء': ['قراءة', 'كتابة', 'حذف'],
                    'الموردين': ['قراءة', 'كتابة', 'حذف'],
                    'التدريب': ['قراءة', 'كتابة', 'حذف'],
                    'التقارير': ['قراءة', 'تصدير'],
                    'النظام': ['قراءة', 'كتابة', 'إعدادات']
                }),
                'الحالة': 'نشط',
                'المستخدم_المنشئ': 'النظام'
            })
        except:
            pass
        
        # تصنيفات افتراضية
        default_categories = [
            ('عملاء', 'عملاء عاديين', 'عملاء المشاريع العادية', '#007bff', 'العملاء'),
            ('عملاء', 'عملاء مميزين', 'عملاء ذوي الأولوية العالية', '#28a745', 'العملاء'),
            ('عملاء', 'عملاء حكوميين', 'الجهات والمؤسسات الحكومية', '#6f42c1', 'العملاء'),
            
            ('موظفين', 'مهندسين', 'المهندسين والفنيين', '#17a2b8', 'الموظفين'),
            ('موظفين', 'إداريين', 'الموظفين الإداريين', '#6c757d', 'الموظفين'),
            ('موظفين', 'عمال', 'العمال والحرفيين', '#fd7e14', 'الموظفين'),
            
            ('مشاريع', 'سكني', 'المشاريع السكنية', '#fd7e14', 'المشاريع'),
            ('مشاريع', 'تجاري', 'المشاريع التجارية', '#e83e8c', 'المشاريع'),
            ('مشاريع', 'صناعي', 'المشاريع الصناعية', '#20c997', 'المشاريع'),
            ('مشاريع', 'حكومي', 'المشاريع الحكومية', '#6f42c1', 'المشاريع'),
            
            ('مقاولات', 'إنشاءات', 'مقاولات الإنشاءات', '#dc3545', 'المقاولات'),
            ('مقاولات', 'صيانة', 'مقاولات الصيانة', '#ffc107', 'المقاولات'),
            ('مقاولات', 'تشطيبات', 'مقاولات التشطيبات', '#17a2b8', 'المقاولات'),
            
            ('موردين', 'مواد_بناء', 'موردي مواد البناء', '#6c757d', 'الموردين'),
            ('موردين', 'معدات', 'موردي المعدات', '#fd7e14', 'الموردين'),
            ('موردين', 'خدمات', 'موردي الخدمات', '#20c997', 'الموردين'),
            
            ('تدريب', 'تقني', 'البرامج التقنية', '#007bff', 'التدريب'),
            ('تدريب', 'إداري', 'البرامج الإدارية', '#28a745', 'التدريب'),
            ('تدريب', 'مهني', 'البرامج المهنية', '#dc3545', 'التدريب'),
            
            ('مصروفات', 'تشغيلية', 'المصروفات التشغيلية', '#dc3545', 'المصروفات'),
            ('مصروفات', 'إدارية', 'المصروفات الإدارية', '#6c757d', 'المصروفات'),
            ('مصروفات', 'تسويقية', 'المصروفات التسويقية', '#ffc107', 'المصروفات'),
            
            ('حسابات', 'أصول', 'حسابات الأصول', '#28a745', 'المحاسبة'),
            ('حسابات', 'خصوم', 'حسابات الخصوم', '#dc3545', 'المحاسبة'),
            ('حسابات', 'إيرادات', 'حسابات الإيرادات', '#007bff', 'المحاسبة'),
            ('حسابات', 'مصروفات', 'حسابات المصروفات', '#fd7e14', 'المحاسبة'),
        ]
        
        for category in default_categories:
            try:
                self.ادراج_بيانات('التصنيفات', {
                    'النوع': category[0],
                    'اسم_التصنيف': category[1],
                    'الوصف': category[2],
                    'اللون': category[3],
                    'الأيقونة': category[4],
                    'نشط': True,
                    'المستخدم': 'النظام'
                })
            except:
                pass
        
        # شجرة الحسابات الأساسية
        basic_accounts = [
            # الأصول
            ('1000', 'الأصول', 'أصول', 'أصول_متداولة', None, 1, 'مدين', True, False),
            ('1100', 'الأصول المتداولة', 'أصول', 'أصول_متداولة', 1, 2, 'مدين', True, False),
            ('1110', 'النقدية', 'أصول', 'أصول_متداولة', 2, 3, 'مدين', False, True),
            ('1120', 'البنوك', 'أصول', 'أصول_متداولة', 2, 3, 'مدين', False, True),
            ('1130', 'العملاء', 'أصول', 'أصول_متداولة', 2, 3, 'مدين', False, True),
            ('1200', 'الأصول الثابتة', 'أصول', 'أصول_ثابتة', 1, 2, 'مدين', True, False),
            ('1210', 'المباني', 'أصول', 'أصول_ثابتة', 6, 3, 'مدين', False, True),
            ('1220', 'المعدات', 'أصول', 'أصول_ثابتة', 6, 3, 'مدين', False, True),
            
            # الخصوم
            ('2000', 'الخصوم', 'خصوم', 'خصوم_قصيرة_الأجل', None, 1, 'دائن', True, False),
            ('2100', 'الخصوم المتداولة', 'خصوم', 'خصوم_قصيرة_الأجل', 8, 2, 'دائن', True, False),
            ('2110', 'الموردين', 'خصوم', 'خصوم_قصيرة_الأجل', 9, 3, 'دائن', False, True),
            ('2120', 'المصروفات المستحقة', 'خصوم', 'خصوم_قصيرة_الأجل', 9, 3, 'دائن', False, True),
            
            # حقوق الملكية
            ('3000', 'حقوق الملكية', 'حقوق_ملكية', 'رأس_المال', None, 1, 'دائن', True, False),
            ('3100', 'رأس المال', 'حقوق_ملكية', 'رأس_المال', 12, 2, 'دائن', False, True),
            ('3200', 'الأرباح المحتجزة', 'حقوق_ملكية', 'أرباح_محتجزة', 12, 2, 'دائن', False, True),
            
            # الإيرادات
            ('4000', 'الإيرادات', 'إيرادات', 'إيرادات_تشغيلية', None, 1, 'دائن', True, False),
            ('4100', 'إيرادات المشاريع', 'إيرادات', 'إيرادات_تشغيلية', 15, 2, 'دائن', False, True),
            ('4200', 'إيرادات التدريب', 'إيرادات', 'إيرادات_تشغيلية', 15, 2, 'دائن', False, True),
            
            # المصروفات
            ('5000', 'المصروفات', 'مصروفات', 'مصروفات_تشغيلية', None, 1, 'مدين', True, False),
            ('5100', 'مصروفات المشاريع', 'مصروفات', 'مصروفات_تشغيلية', 18, 2, 'مدين', False, True),
            ('5200', 'المصروفات الإدارية', 'مصروفات', 'مصروفات_إدارية', 18, 2, 'مدين', False, True),
            ('5300', 'مصروفات التسويق', 'مصروفات', 'مصروفات_أخرى', 18, 2, 'مدين', False, True),
        ]
        
        account_ids = {}
        for account in basic_accounts:
            try:
                parent_id = account_ids.get(account[4]) if account[4] else None
                account_id = self.ادراج_بيانات('شجرة_الحسابات', {
                    'رقم_الحساب': account[0],
                    'اسم_الحساب': account[1],
                    'نوع_الحساب': account[2],
                    'تصنيف_فرعي': account[3],
                    'الحساب_الأب': parent_id,
                    'المستوى': account[5],
                    'طبيعة_الحساب': account[6],
                    'حساب_رئيسي': account[7],
                    'يقبل_قيود': account[8],
                    'نشط': True,
                    'المستخدم': 'النظام'
                })
                if account_id:
                    account_ids[len(account_ids) + 1] = account_id
            except:
                pass
        
        # السنة المالية الحالية
        current_year = datetime.now().year
        try:
            self.ادراج_بيانات('السنوات_المالية', {
                'السنة': current_year,
                'تاريخ_البداية': f'{current_year}-01-01',
                'تاريخ_النهاية': f'{current_year}-12-31',
                'الحالة': 'مفتوحة',
                'المستخدم': 'النظام'
            })
        except:
            pass
        
        logger.info("تم إدراج البيانات الافتراضية بنجاح")
    
    # ==================== دوال مساعدة إضافية ====================
    
    def انشاء_قيد_محاسبي(self, بيان: str, تفاصيل: List[Dict], نوع_القيد: str = 'يومي', 
                          مرجع_خارجي: str = None, نوع_المرجع: str = None, معرف_المرجع: int = None) -> Optional[int]:
        """
        إنشاء قيد محاسبي جديد
        
        Args:
            بيان: بيان القيد
            تفاصيل: قائمة بتفاصيل القيد [{'معرف_الحساب': int, 'البيان': str, 'مدين': float, 'دائن': float}]
            نوع_القيد: نوع القيد
            مرجع_خارجي: المرجع الخارجي
            نوع_المرجع: نوع المرجع
            معرف_المرجع: معرف المرجع
            
        Returns:
            معرف القيد الجديد أو None
        """
        try:
            # التحقق من توازن القيد
            إجمالي_المدين = sum([detail.get('مدين', 0) for detail in تفاصيل])
            إجمالي_الدائن = sum([detail.get('دائن', 0) for detail in تفاصيل])
            
            if abs(إجمالي_المدين - إجمالي_الدائن) > 0.01:
                logger.error(f"القيد غير متوازن: مدين={إجمالي_المدين}, دائن={إجمالي_الدائن}")
                return None
            
            # إنشاء رقم القيد
            current_year = datetime.now().year
            count_result = self.تحميل_بيانات(
                'القيود_المحاسبية', 
                'COUNT(*) as count', 
                'YEAR(تاريخ_القيد) = %s', 
                (current_year,)
            )
            next_number = (count_result[0]['count'] if count_result else 0) + 1
            رقم_القيد = f"{current_year}-{next_number:06d}"
            
            # إدراج القيد الرئيسي
            معرف_القيد = self.ادراج_بيانات('القيود_المحاسبية', {
                'رقم_القيد': رقم_القيد,
                'تاريخ_القيد': datetime.now().date(),
                'نوع_القيد': نوع_القيد,
                'البيان': بيان,
                'إجمالي_المدين': إجمالي_المدين,
                'إجمالي_الدائن': إجمالي_الدائن,
                'مرجع_خارجي': مرجع_خارجي,
                'نوع_المرجع': نوع_المرجع,
                'معرف_المرجع': معرف_المرجع,
                'حالة_القيد': 'مسودة',
                'المستخدم': 'النظام'
            })
            
            if not معرف_القيد:
                return None
            
            # إدراج تفاصيل القيد
            for i, detail in enumerate(تفاصيل, 1):
                self.ادراج_بيانات('تفاصيل_القيود_المحاسبية', {
                    'معرف_القيد': معرف_القيد,
                    'معرف_الحساب': detail['معرف_الحساب'],
                    'البيان': detail.get('البيان', بيان),
                    'المبلغ_المدين': detail.get('مدين', 0),
                    'المبلغ_الدائن': detail.get('دائن', 0),
                    'معرف_مركز_التكلفة': detail.get('معرف_مركز_التكلفة'),
                    'ترتيب_السطر': i
                })
            
            logger.info(f"تم إنشاء قيد محاسبي جديد: {رقم_القيد}")
            return معرف_القيد
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء القيد المحاسبي: {e}")
            return None
    
    def حساب_رصيد_حساب(self, معرف_الحساب: int, تاريخ_النهاية: date = None) -> Decimal:
        """
        حساب رصيد حساب معين حتى تاريخ محدد
        
        Args:
            معرف_الحساب: معرف الحساب
            تاريخ_النهاية: تاريخ النهاية (افتراضي: اليوم)
            
        Returns:
            رصيد الحساب
        """
        try:
            if not تاريخ_النهاية:
                تاريخ_النهاية = datetime.now().date()
            
            # الحصول على معلومات الحساب
            account_info = self.تحميل_بيانات(
                'شجرة_الحسابات',
                'طبيعة_الحساب, الرصيد_الافتتاحي',
                'id = %s',
                (معرف_الحساب,)
            )
            
            if not account_info:
                return Decimal('0')
            
            طبيعة_الحساب = account_info[0]['طبيعة_الحساب']
            الرصيد_الافتتاحي = Decimal(str(account_info[0]['الرصيد_الافتتاحي'] or 0))
            
            # حساب مجموع الحركات
            movements = self.تحميل_بيانات(
                'تفاصيل_القيود_المحاسبية td JOIN القيود_المحاسبية te ON td.معرف_القيد = te.id',
                'SUM(td.المبلغ_المدين) as total_debit, SUM(td.المبلغ_الدائن) as total_credit',
                'td.معرف_الحساب = %s AND te.تاريخ_القيد <= %s AND te.حالة_القيد = "معتمد"',
                (معرف_الحساب, تاريخ_النهاية)
            )
            
            إجمالي_المدين = Decimal(str(movements[0]['total_debit'] or 0)) if movements else Decimal('0')
            إجمالي_الدائن = Decimal(str(movements[0]['total_credit'] or 0)) if movements else Decimal('0')
            
            # حساب الرصيد حسب طبيعة الحساب
            if طبيعة_الحساب == 'مدين':
                الرصيد = الرصيد_الافتتاحي + إجمالي_المدين - إجمالي_الدائن
            else:  # دائن
                الرصيد = الرصيد_الافتتاحي + إجمالي_الدائن - إجمالي_المدين
            
            return الرصيد
            
        except Exception as e:
            logger.error(f"خطأ في حساب رصيد الحساب: {e}")
            return Decimal('0')
    
    def انشاء_نسخة_احتياطية(self, مسار_النسخة: str = None) -> bool:
        """
        إنشاء نسخة احتياطية من قاعدة البيانات
        
        Args:
            مسار_النسخة: مسار النسخة الاحتياطية
            
        Returns:
            True إذا تم إنشاء النسخة بنجاح
        """
        try:
            if not مسار_النسخة:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                مسار_النسخة = f"backup_{self.database}_{timestamp}.sql"
            
            # تنفيذ أمر النسخ الاحتياطي
            import subprocess
            
            cmd = [
                'mysqldump',
                '--host', self.host,
                '--user', self.user,
                f'--password={self.password}',
                '--single-transaction',
                '--routines',
                '--triggers',
                '--default-character-set=utf8mb4',
                self.database
            ]
            
            with open(مسار_النسخة, 'w', encoding='utf-8') as backup_file:
                result = subprocess.run(cmd, stdout=backup_file, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                logger.info(f"تم إنشاء النسخة الاحتياطية: {مسار_النسخة}")
                return True
            else:
                logger.error(f"خطأ في إنشاء النسخة الاحتياطية: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"خطأ في إنشاء النسخة الاحتياطية: {e}")
            return False
    
    def استعادة_نسخة_احتياطية(self, مسار_النسخة: str) -> bool:
        """
        استعادة نسخة احتياطية
        
        Args:
            مسار_النسخة: مسار النسخة الاحتياطية
            
        Returns:
            True إذا تم الاستعادة بنجاح
        """
        try:
            if not Path(مسار_النسخة).exists():
                logger.error(f"ملف النسخة الاحتياطية غير موجود: {مسار_النسخة}")
                return False
            
            # تنفيذ أمر الاستعادة
            import subprocess
            
            cmd = [
                'mysql',
                '--host', self.host,
                '--user', self.user,
                f'--password={self.password}',
                '--default-character-set=utf8mb4',
                self.database
            ]
            
            with open(مسار_النسخة, 'r', encoding='utf-8') as backup_file:
                result = subprocess.run(cmd, stdin=backup_file, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                logger.info(f"تم استعادة النسخة الاحتياطية: {مسار_النسخة}")
                return True
            else:
                logger.error(f"خطأ في استعادة النسخة الاحتياطية: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"خطأ في استعادة النسخة الاحتياطية: {e}")
            return False
    
    def احصائيات_النظام(self) -> Dict[str, Any]:
        """
        الحصول على إحصائيات شاملة للنظام
        
        Returns:
            قاموس بالإحصائيات
        """
        try:
            stats = {}
            
            # إحصائيات الجداول
            stats['الجداول'] = {
                'عدد_الجداول_المنشأة': len(self.tables_created),
                'قائمة_الجداول': list(self.tables_created)
            }
            
            # إحصائيات المشاريع
            projects_stats = self.تحميل_بيانات(
                'المشاريع',
                'COUNT(*) as total, SUM(قيمة_المشروع) as total_value, AVG(نسبة_الإنجاز) as avg_progress'
            )
            if projects_stats:
                stats['المشاريع'] = {
                    'العدد_الإجمالي': projects_stats[0]['total'],
                    'القيمة_الإجمالية': float(projects_stats[0]['total_value'] or 0),
                    'متوسط_نسبة_الإنجاز': float(projects_stats[0]['avg_progress'] or 0)
                }
            
            # إحصائيات العملاء
            clients_stats = self.تحميل_بيانات(
                'العملاء',
                'COUNT(*) as total, SUM(رصيد_العميل) as total_balance'
            )
            if clients_stats:
                stats['العملاء'] = {
                    'العدد_الإجمالي': clients_stats[0]['total'],
                    'إجمالي_الأرصدة': float(clients_stats[0]['total_balance'] or 0)
                }
            
            # إحصائيات الموظفين
            employees_stats = self.تحميل_بيانات(
                'الموظفين',
                'COUNT(*) as total, SUM(المرتب_الأساسي) as total_salaries'
            )
            if employees_stats:
                stats['الموظفين'] = {
                    'العدد_الإجمالي': employees_stats[0]['total'],
                    'إجمالي_المرتبات': float(employees_stats[0]['total_salaries'] or 0)
                }
            
            # إحصائيات التدريب
            training_stats = self.تحميل_بيانات(
                'البرامج_التدريبية',
                'COUNT(*) as total_programs'
            )
            groups_stats = self.تحميل_بيانات(
                'المجموعات_التدريبية',
                'COUNT(*) as total_groups, SUM(عدد_المشتركين) as total_participants'
            )
            if training_stats and groups_stats:
                stats['التدريب'] = {
                    'عدد_البرامج': training_stats[0]['total_programs'],
                    'عدد_المجموعات': groups_stats[0]['total_groups'],
                    'عدد_المشتركين': groups_stats[0]['total_participants'] or 0
                }
            
            # إحصائيات المحاسبة
            accounting_stats = self.تحميل_بيانات(
                'القيود_المحاسبية',
                'COUNT(*) as total_entries, SUM(إجمالي_المدين) as total_debits'
            )
            if accounting_stats:
                stats['المحاسبة'] = {
                    'عدد_القيود': accounting_stats[0]['total_entries'],
                    'إجمالي_المبالغ': float(accounting_stats[0]['total_debits'] or 0)
                }
            
            stats['تاريخ_الإحصائيات'] = datetime.now().isoformat()
            
            return stats
            
        except Exception as e:
            logger.error(f"خطأ في جمع الإحصائيات: {e}")
            return {'خطأ': str(e)}
    
    def __del__(self):
        """تنظيف الموارد عند حذف الكائن"""
        self.اغلاق_اتصال()


# ==================== دالة الاختبار ====================

def اختبار_النظام():
    """اختبار النظام المحاسبي الشامل"""
    print("🚀 بدء اختبار النظام المحاسبي الشامل...")
    
    # إنشاء مثيل من النظام
    نظام = نظام_المحاسبة_الشامل()
    
    try:
        # إنشاء النظام الكامل
        print("📊 إنشاء النظام الكامل...")
        if نظام.انشاء_النظام_الكامل():
            print("✅ تم إنشاء النظام بنجاح!")
            
            # عرض الإحصائيات
            print("\n📈 إحصائيات النظام:")
            stats = نظام.احصائيات_النظام()
            for key, value in stats.items():
                print(f"   {key}: {value}")
            
            # اختبار إنشاء قيد محاسبي
            print("\n💰 اختبار إنشاء قيد محاسبي...")
            تفاصيل_القيد = [
                {'معرف_الحساب': 1, 'البيان': 'نقدية', 'مدين': 1000, 'دائن': 0},
                {'معرف_الحساب': 2, 'البيان': 'رأس المال', 'مدين': 0, 'دائن': 1000}
            ]
            
            معرف_القيد = نظام.انشاء_قيد_محاسبي(
                "قيد افتتاحي - رأس المال",
                تفاصيل_القيد,
                'افتتاحي'
            )
            
            if معرف_القيد:
                print(f"✅ تم إنشاء القيد المحاسبي بمعرف: {معرف_القيد}")
            else:
                print("❌ فشل في إنشاء القيد المحاسبي")
            
            print("\n🎉 تم اختبار النظام بنجاح!")
            
        else:
            print("❌ فشل في إنشاء النظام")
            
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
    
    finally:
        نظام.اغلاق_اتصال()


if __name__ == "__main__":
    اختبار_النظام()