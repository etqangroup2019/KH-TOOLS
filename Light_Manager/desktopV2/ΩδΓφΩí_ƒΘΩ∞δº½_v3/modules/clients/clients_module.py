#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
وحدة إدارة العملاء
تدير بيانات العملاء، المعاملات المالية، وجهات الاتصال
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from decimal import Decimal

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.base_module import BaseModule
from core.database import DatabaseManager

logger = logging.getLogger(__name__)

class ClientsModule(BaseModule):
    """
    وحدة إدارة العملاء
    تدير جميع عمليات العملاء والمعاملات المالية
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        تهيئة وحدة العملاء
        
        Args:
            db_manager: مدير قاعدة البيانات
        """
        super().__init__(db_manager, "العملاء")
        
        # قائمة الجداول التي تديرها الوحدة
        self.tables = [
            'العملاء',
            'معاملات_العملاء_المالية',
            'جهات_اتصال_العملاء'
        ]
    
    def create_tables(self) -> bool:
        """
        إنشاء جداول العملاء
        
        Returns:
            True إذا تم الإنشاء بنجاح
        """
        try:
            logger.info("إنشاء جداول العملاء...")
            
            # جدول العملاء الرئيسي
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS `العملاء` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `رقم_العميل` VARCHAR(50) NOT NULL UNIQUE,
                    `اسم_العميل` VARCHAR(255) NOT NULL,
                    `نوع_العميل` ENUM('فرد', 'شركة', 'مؤسسة', 'جهة_حكومية') DEFAULT 'فرد',
                    `رقم_الهوية_السجل` VARCHAR(50) UNIQUE,
                    `العنوان` TEXT,
                    `المدينة` VARCHAR(100),
                    `المنطقة` VARCHAR(100),
                    `الرمز_البريدي` VARCHAR(20),
                    `رقم_الهاتف` VARCHAR(50),
                    `رقم_الجوال` VARCHAR(50),
                    `البريد_الإلكتروني` VARCHAR(100),
                    `الموقع_الإلكتروني` VARCHAR(255),
                    `نوع_النشاط` VARCHAR(100),
                    `تاريخ_التسجيل` DATE DEFAULT (CURRENT_DATE),
                    `مصدر_العميل` ENUM('تسويق_مباشر', 'إحالة', 'موقع_إلكتروني', 'معارض', 'إعلانات', 'أخرى') DEFAULT 'تسويق_مباشر',
                    `درجة_الأهمية` ENUM('عادي', 'مهم', 'مهم_جداً', 'استراتيجي') DEFAULT 'عادي',
                    `حد_الائتمان` DECIMAL(15,2) DEFAULT 0,
                    `رصيد_العميل` DECIMAL(15,2) DEFAULT 0,
                    `إجمالي_المبيعات` DECIMAL(15,2) DEFAULT 0,
                    `عدد_المشاريع` INT DEFAULT 0,
                    `تاريخ_آخر_معاملة` DATE,
                    `الحالة` ENUM('نشط', 'معطل', 'محذوف') DEFAULT 'نشط',
                    `ملاحظات` TEXT,
                    `المستخدم` VARCHAR(50),
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX `idx_client_number` (`رقم_العميل`),
                    INDEX `idx_client_name` (`اسم_العميل`),
                    INDEX `idx_client_type` (`نوع_العميل`),
                    INDEX `idx_id_number` (`رقم_الهوية_السجل`),
                    INDEX `idx_city` (`المدينة`),
                    INDEX `idx_phone` (`رقم_الهاتف`),
                    INDEX `idx_mobile` (`رقم_الجوال`),
                    INDEX `idx_email` (`البريد_الإلكتروني`),
                    INDEX `idx_importance` (`درجة_الأهمية`),
                    INDEX `idx_status` (`الحالة`),
                    INDEX `idx_registration_date` (`تاريخ_التسجيل`)
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # جدول معاملات العملاء المالية
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS `معاملات_العملاء_المالية` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `رقم_المعاملة` VARCHAR(50) NOT NULL UNIQUE,
                    `معرف_العميل` INT NOT NULL,
                    `نوع_المعاملة` ENUM('دفعة', 'فاتورة', 'خصم', 'إضافة', 'تسوية') NOT NULL,
                    `المبلغ` DECIMAL(15,2) NOT NULL,
                    `الوصف` VARCHAR(255),
                    `تاريخ_المعاملة` DATE NOT NULL,
                    `طريقة_الدفع` ENUM('نقدي', 'شيك', 'تحويل_بنكي', 'بطاقة', 'آجل') DEFAULT 'نقدي',
                    `رقم_المرجع` VARCHAR(100),
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
                    INDEX `idx_الحالة` (`الحالة`),
                    INDEX `idx_السنة` (`السنة`),
                    FOREIGN KEY (`معرف_العميل`) REFERENCES `العملاء`(`id`) ON DELETE CASCADE
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # جدول جهات اتصال العملاء
            self.db.execute_query("""
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
                    INDEX `idx_client_id` (`معرف_العميل`),
                    INDEX `idx_name` (`الاسم`),
                    INDEX `idx_contact_type` (`نوع_الاتصال`),
                    INDEX `idx_phone` (`رقم_الهاتف`),
                    INDEX `idx_mobile` (`رقم_الجوال`),
                    INDEX `idx_email` (`البريد_الإلكتروني`),
                    FOREIGN KEY (`معرف_العميل`) REFERENCES `العملاء`(`id`) ON DELETE CASCADE
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            self.db.commit()
            logger.info("تم إنشاء جداول العملاء بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء جداول العملاء: {e}")
            self.db.rollback()
            return False
    
    def create_client(self, client_data: Dict[str, Any]) -> Optional[int]:
        """
        إنشاء عميل جديد
        
        Args:
            client_data: بيانات العميل
            
        Returns:
            معرف العميل الجديد أو None
        """
        try:
            # التحقق من البيانات المطلوبة
            required_fields = ['اسم_العميل']
            is_valid, error_msg = self.validate_data(client_data, required_fields)
            
            if not is_valid:
                logger.error(f"بيانات العميل غير صحيحة: {error_msg}")
                return None
            
            # توليد رقم العميل
            if 'رقم_العميل' not in client_data:
                client_data['رقم_العميل'] = self.generate_number('C', 'العملاء', 'رقم_العميل')
            
            # إدراج العميل
            client_id = self.insert_record('العملاء', client_data)
            
            if client_id:
                self.log_operation('إنشاء_عميل', 'العملاء', client_id, f"رقم العميل: {client_data['رقم_العميل']}")
                logger.info(f"تم إنشاء عميل جديد: {client_data['رقم_العميل']}")
            
            return client_id
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء العميل: {e}")
            return None
    
    def get_module_info(self) -> Dict[str, Any]:
        """
        الحصول على معلومات وحدة العملاء
        
        Returns:
            معلومات الوحدة
        """
        try:
            return {
                'اسم_الوحدة': self.module_name,
                'الوصف': 'وحدة إدارة العملاء والمعاملات المالية',
                'الإصدار': '1.0.0',
                'الجداول': self.tables,
                'الوظائف_الرئيسية': [
                    'إدارة بيانات العملاء',
                    'إدارة المعاملات المالية',
                    'إدارة جهات الاتصال',
                    'متابعة أرصدة العملاء',
                    'تقارير العملاء'
                ]
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على معلومات الوحدة: {e}")
            return {'خطأ': str(e)}