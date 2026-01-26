#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
وحدة إدارة المشاريع
تدير المشاريع، المراحل، المهام، العهد المالية، والدفعات
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

class ProjectsModule(BaseModule):
    """
    وحدة إدارة المشاريع
    تدير جميع عمليات المشاريع والمقاولات
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        تهيئة وحدة المشاريع
        
        Args:
            db_manager: مدير قاعدة البيانات
        """
        super().__init__(db_manager, "المشاريع")
        
        # قائمة الجداول التي تديرها الوحدة
        self.tables = [
            'المشاريع',
            'مراحل_المشروع',
            'مهام_فريق_العمل',
            'عهد_مالية_المشاريع',
            'دفعات_المشاريع',
            'مصروفات_المشاريع',
            'عقود_المشاريع',
            'الجدول_الزمني_للمراحل',
            'مردودات_مواد_المشاريع',
            'خسائر_المشاريع'
        ]
    
    def create_tables(self) -> bool:
        """
        إنشاء جداول المشاريع
        
        Returns:
            True إذا تم الإنشاء بنجاح
        """
        try:
            logger.info("إنشاء جداول المشاريع...")
            
            # جدول المشاريع الرئيسي
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS `المشاريع` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `رقم_المشروع` VARCHAR(50) NOT NULL UNIQUE,
                    `معرف_العميل` INT NOT NULL,
                    `معرف_المدير` INT,
                    `اسم_المشروع` VARCHAR(255) NOT NULL,
                    `الوصف` TEXT,
                    `نوع_المشروع` ENUM('مباني_سكنية', 'مباني_تجارية', 'مباني_صناعية', 'طرق_وجسور', 'مرافق_عامة', 'أخرى') DEFAULT 'مباني_سكنية',
                    `الموقع` VARCHAR(255),
                    `المساحة` DECIMAL(10,2),
                    `وحدة_المساحة` VARCHAR(20) DEFAULT 'متر مربع',
                    `قيمة_المشروع` DECIMAL(15,2) NOT NULL,
                    `العملة` VARCHAR(10) DEFAULT 'ريال سعودي',
                    `تاريخ_البداية` DATE NOT NULL,
                    `تاريخ_النهاية_المخطط` DATE NOT NULL,
                    `تاريخ_النهاية_الفعلي` DATE,
                    `نسبة_الإنجاز` DECIMAL(5,2) DEFAULT 0 CHECK (`نسبة_الإنجاز` BETWEEN 0 AND 100),
                    `الحالة` ENUM('مخطط', 'قيد_التنفيذ', 'معلق', 'مكتمل', 'ملغي', 'متأخر') DEFAULT 'مخطط',
                    `سبب_التأخير` TEXT,
                    `الأولوية` ENUM('منخفضة', 'متوسطة', 'عالية', 'عاجلة') DEFAULT 'متوسطة',
                    `معرف_مركز_التكلفة` INT,
                    `الميزانية_المخططة` DECIMAL(15,2),
                    `الميزانية_المستخدمة` DECIMAL(15,2) DEFAULT 0,
                    `نسبة_استخدام_الميزانية` DECIMAL(5,2) GENERATED ALWAYS AS (
                        CASE 
                            WHEN `الميزانية_المخططة` > 0 
                            THEN (`الميزانية_المستخدمة` / `الميزانية_المخططة`) * 100
                            ELSE 0
                        END
                    ) STORED,
                    `ملاحظات` TEXT,
                    `المستخدم` VARCHAR(50),
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_البداية`)) STORED,
                    INDEX `idx_project_number` (`رقم_المشروع`),
                    INDEX `idx_client_id` (`معرف_العميل`),
                    INDEX `idx_manager_id` (`معرف_المدير`),
                    INDEX `idx_project_type` (`نوع_المشروع`),
                    INDEX `idx_status` (`الحالة`),
                    INDEX `idx_priority` (`الأولوية`),
                    INDEX `idx_start_date` (`تاريخ_البداية`),
                    INDEX `idx_end_date` (`تاريخ_النهاية_المخطط`),
                    INDEX `idx_progress` (`نسبة_الإنجاز`),
                    INDEX `idx_year` (`السنة`)
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # جدول مراحل المشروع
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS `مراحل_المشروع` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `معرف_المشروع` INT NOT NULL,
                    `اسم_المرحلة` VARCHAR(255) NOT NULL,
                    `الوصف` TEXT,
                    `ترتيب_المرحلة` INT NOT NULL,
                    `تاريخ_البداية_المخطط` DATE NOT NULL,
                    `تاريخ_النهاية_المخطط` DATE NOT NULL,
                    `تاريخ_البداية_الفعلي` DATE,
                    `تاريخ_النهاية_الفعلي` DATE,
                    `المدة_المخططة` INT GENERATED ALWAYS AS (DATEDIFF(`تاريخ_النهاية_المخطط`, `تاريخ_البداية_المخطط`)) STORED,
                    `المدة_الفعلية` INT GENERATED ALWAYS AS (
                        CASE 
                            WHEN `تاريخ_البداية_الفعلي` IS NOT NULL AND `تاريخ_النهاية_الفعلي` IS NOT NULL
                            THEN DATEDIFF(`تاريخ_النهاية_الفعلي`, `تاريخ_البداية_الفعلي`)
                            ELSE NULL
                        END
                    ) STORED,
                    `نسبة_الإنجاز` DECIMAL(5,2) DEFAULT 0 CHECK (`نسبة_الإنجاز` BETWEEN 0 AND 100),
                    `الحالة` ENUM('لم_تبدأ', 'قيد_التنفيذ', 'مكتملة', 'معلقة', 'ملغية') DEFAULT 'لم_تبدأ',
                    `المسؤول` VARCHAR(255),
                    `الميزانية_المخططة` DECIMAL(15,2),
                    `الميزانية_المستخدمة` DECIMAL(15,2) DEFAULT 0,
                    `ملاحظات` TEXT,
                    `المستخدم` VARCHAR(50),
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX `idx_project_id` (`معرف_المشروع`),
                    INDEX `idx_phase_order` (`ترتيب_المرحلة`),
                    INDEX `idx_status` (`الحالة`),
                    INDEX `idx_progress` (`نسبة_الإنجاز`),
                    INDEX `idx_planned_start` (`تاريخ_البداية_المخطط`),
                    INDEX `idx_planned_end` (`تاريخ_النهاية_المخطط`),
                    FOREIGN KEY (`معرف_المشروع`) REFERENCES `المشاريع`(`id`) ON DELETE CASCADE
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # جدول مهام فريق العمل
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS `مهام_فريق_العمل` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `معرف_المشروع` INT NOT NULL,
                    `معرف_المرحلة` INT,
                    `معرف_الموظف` INT NOT NULL,
                    `اسم_المهمة` VARCHAR(255) NOT NULL,
                    `الوصف` TEXT,
                    `نوع_المهمة` ENUM('تصميم', 'تنفيذ', 'إشراف', 'مراجعة', 'اختبار', 'تسليم', 'أخرى') DEFAULT 'تنفيذ',
                    `الأولوية` ENUM('منخفضة', 'متوسطة', 'عالية', 'عاجلة') DEFAULT 'متوسطة',
                    `تاريخ_البداية_المخطط` DATE NOT NULL,
                    `تاريخ_النهاية_المخطط` DATE NOT NULL,
                    `تاريخ_البداية_الفعلي` DATE,
                    `تاريخ_النهاية_الفعلي` DATE,
                    `الساعات_المخططة` DECIMAL(8,2),
                    `الساعات_الفعلية` DECIMAL(8,2) DEFAULT 0,
                    `نسبة_الإنجاز` DECIMAL(5,2) DEFAULT 0 CHECK (`نسبة_الإنجاز` BETWEEN 0 AND 100),
                    `الحالة` ENUM('جديدة', 'قيد_التنفيذ', 'مكتملة', 'متأخرة', 'ملغية', 'معلقة') DEFAULT 'جديدة',
                    `التقييم` INT CHECK (`التقييم` BETWEEN 1 AND 5),
                    `ملاحظات` TEXT,
                    `المستخدم` VARCHAR(50),
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX `idx_project_id` (`معرف_المشروع`),
                    INDEX `idx_phase_id` (`معرف_المرحلة`),
                    INDEX `idx_employee_id` (`معرف_الموظف`),
                    INDEX `idx_task_type` (`نوع_المهمة`),
                    INDEX `idx_priority` (`الأولوية`),
                    INDEX `idx_status` (`الحالة`),
                    INDEX `idx_planned_start` (`تاريخ_البداية_المخطط`),
                    INDEX `idx_planned_end` (`تاريخ_النهاية_المخطط`),
                    FOREIGN KEY (`معرف_المشروع`) REFERENCES `المشاريع`(`id`) ON DELETE CASCADE,
                    FOREIGN KEY (`معرف_المرحلة`) REFERENCES `مراحل_المشروع`(`id`) ON DELETE SET NULL
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # جدول العهد المالية للمشاريع
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS `عهد_مالية_المشاريع` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `رقم_العهدة` VARCHAR(50) NOT NULL UNIQUE,
                    `معرف_المشروع` INT NOT NULL,
                    `معرف_الموظف` INT NOT NULL,
                    `نوع_العهدة` ENUM('نقدية', 'مواد', 'معدات', 'مختلطة') DEFAULT 'نقدية',
                    `الغرض` VARCHAR(255) NOT NULL,
                    `المبلغ` DECIMAL(15,2) NOT NULL,
                    `تاريخ_الصرف` DATE NOT NULL,
                    `تاريخ_الاستحقاق` DATE NOT NULL,
                    `المبلغ_المستخدم` DECIMAL(15,2) DEFAULT 0,
                    `المبلغ_المتبقي` DECIMAL(15,2) GENERATED ALWAYS AS (`المبلغ` - `المبلغ_المستخدم`) STORED,
                    `الحالة` ENUM('نشطة', 'مسددة', 'متأخرة', 'ملغية') DEFAULT 'نشطة',
                    `تاريخ_التسديد` DATE,
                    `ملاحظات` TEXT,
                    `المستخدم` VARCHAR(50),
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX `idx_custody_number` (`رقم_العهدة`),
                    INDEX `idx_project_id` (`معرف_المشروع`),
                    INDEX `idx_employee_id` (`معرف_الموظف`),
                    INDEX `idx_custody_type` (`نوع_العهدة`),
                    INDEX `idx_status` (`الحالة`),
                    INDEX `idx_issue_date` (`تاريخ_الصرف`),
                    INDEX `idx_due_date` (`تاريخ_الاستحقاق`),
                    FOREIGN KEY (`معرف_المشروع`) REFERENCES `المشاريع`(`id`) ON DELETE CASCADE
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # جدول دفعات المشاريع
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS `دفعات_المشاريع` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `رقم_الدفعة` VARCHAR(50) NOT NULL UNIQUE,
                    `معرف_المشروع` INT NOT NULL,
                    `معرف_العهدة` INT,
                    `نوع_الدفعة` ENUM('دفعة_مقدمة', 'دفعة_تقدم', 'دفعة_نهائية', 'دفعة_إضافية') DEFAULT 'دفعة_تقدم',
                    `المبلغ` DECIMAL(15,2) NOT NULL,
                    `نسبة_الدفعة` DECIMAL(5,2),
                    `تاريخ_الاستحقاق` DATE NOT NULL,
                    `تاريخ_الدفع` DATE,
                    `طريقة_الدفع` ENUM('نقدي', 'شيك', 'تحويل_بنكي', 'بطاقة') DEFAULT 'تحويل_بنكي',
                    `رقم_المرجع` VARCHAR(100),
                    `الحالة` ENUM('مستحقة', 'مدفوعة', 'متأخرة', 'ملغية') DEFAULT 'مستحقة',
                    `معرف_القيد_المحاسبي` INT,
                    `ملاحظات` TEXT,
                    `المستخدم` VARCHAR(50),
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX `idx_payment_number` (`رقم_الدفعة`),
                    INDEX `idx_project_id` (`معرف_المشروع`),
                    INDEX `idx_custody_id` (`معرف_العهدة`),
                    INDEX `idx_payment_type` (`نوع_الدفعة`),
                    INDEX `idx_status` (`الحالة`),
                    INDEX `idx_due_date` (`تاريخ_الاستحقاق`),
                    INDEX `idx_payment_date` (`تاريخ_الدفع`),
                    FOREIGN KEY (`معرف_المشروع`) REFERENCES `المشاريع`(`id`) ON DELETE CASCADE,
                    FOREIGN KEY (`معرف_العهدة`) REFERENCES `عهد_مالية_المشاريع`(`id`) ON DELETE SET NULL
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # جدول مصروفات المشاريع
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS `مصروفات_المشاريع` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `رقم_المصروف` VARCHAR(50) NOT NULL UNIQUE,
                    `معرف_المشروع` INT NOT NULL,
                    `معرف_المرحلة` INT,
                    `نوع_المصروف` ENUM('مواد', 'عمالة', 'معدات', 'نقل', 'إشراف', 'تصاريح', 'أخرى') NOT NULL,
                    `الوصف` VARCHAR(255) NOT NULL,
                    `المبلغ` DECIMAL(15,2) NOT NULL,
                    `تاريخ_المصروف` DATE NOT NULL,
                    `معرف_المورد` INT,
                    `رقم_الفاتورة` VARCHAR(100),
                    `طريقة_الدفع` ENUM('نقدي', 'شيك', 'تحويل_بنكي', 'بطاقة', 'آجل') DEFAULT 'نقدي',
                    `معرف_القيد_المحاسبي` INT,
                    `الحالة` ENUM('مدفوع', 'معلق', 'ملغي') DEFAULT 'مدفوع',
                    `ملاحظات` TEXT,
                    `المستخدم` VARCHAR(50),
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_المصروف`)) STORED,
                    `الشهر` INT GENERATED ALWAYS AS (MONTH(`تاريخ_المصروف`)) STORED,
                    INDEX `idx_expense_number` (`رقم_المصروف`),
                    INDEX `idx_project_id` (`معرف_المشروع`),
                    INDEX `idx_phase_id` (`معرف_المرحلة`),
                    INDEX `idx_expense_type` (`نوع_المصروف`),
                    INDEX `idx_expense_date` (`تاريخ_المصروف`),
                    INDEX `idx_supplier_id` (`معرف_المورد`),
                    INDEX `idx_status` (`الحالة`),
                    INDEX `idx_year` (`السنة`),
                    INDEX `idx_month` (`الشهر`),
                    FOREIGN KEY (`معرف_المشروع`) REFERENCES `المشاريع`(`id`) ON DELETE CASCADE,
                    FOREIGN KEY (`معرف_المرحلة`) REFERENCES `مراحل_المشروع`(`id`) ON DELETE SET NULL
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # جدول عقود المشاريع
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS `عقود_المشاريع` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `رقم_العقد` VARCHAR(50) NOT NULL UNIQUE,
                    `معرف_المشروع` INT NOT NULL,
                    `نوع_العقد` ENUM('مقاولة_عامة', 'مقاولة_فرعية', 'استشارات', 'توريد', 'صيانة') NOT NULL,
                    `اسم_المقاول` VARCHAR(255) NOT NULL,
                    `قيمة_العقد` DECIMAL(15,2) NOT NULL,
                    `تاريخ_التوقيع` DATE NOT NULL,
                    `تاريخ_البداية` DATE NOT NULL,
                    `تاريخ_النهاية` DATE NOT NULL,
                    `مدة_العقد_بالأيام` INT GENERATED ALWAYS AS (DATEDIFF(`تاريخ_النهاية`, `تاريخ_البداية`)) STORED,
                    `نسبة_الإنجاز` DECIMAL(5,2) DEFAULT 0,
                    `المبلغ_المدفوع` DECIMAL(15,2) DEFAULT 0,
                    `المبلغ_المتبقي` DECIMAL(15,2) GENERATED ALWAYS AS (`قيمة_العقد` - `المبلغ_المدفوع`) STORED,
                    `الحالة` ENUM('نشط', 'مكتمل', 'معلق', 'ملغي', 'منتهي') DEFAULT 'نشط',
                    `شروط_الدفع` TEXT,
                    `ملاحظات` TEXT,
                    `المستخدم` VARCHAR(50),
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX `idx_contract_number` (`رقم_العقد`),
                    INDEX `idx_project_id` (`معرف_المشروع`),
                    INDEX `idx_contract_type` (`نوع_العقد`),
                    INDEX `idx_contractor` (`اسم_المقاول`),
                    INDEX `idx_status` (`الحالة`),
                    INDEX `idx_sign_date` (`تاريخ_التوقيع`),
                    INDEX `idx_start_date` (`تاريخ_البداية`),
                    INDEX `idx_end_date` (`تاريخ_النهاية`),
                    FOREIGN KEY (`معرف_المشروع`) REFERENCES `المشاريع`(`id`) ON DELETE CASCADE
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # جدول الجدول الزمني للمراحل
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS `الجدول_الزمني_للمراحل` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `معرف_المرحلة` INT NOT NULL,
                    `التاريخ` DATE NOT NULL,
                    `نوع_الحدث` ENUM('بداية_مخططة', 'نهاية_مخططة', 'بداية_فعلية', 'نهاية_فعلية', 'معلم_مهم', 'تأخير', 'تعديل') NOT NULL,
                    `الوصف` VARCHAR(255) NOT NULL,
                    `التفاصيل` TEXT,
                    `المسؤول` VARCHAR(255),
                    `الحالة` ENUM('مخطط', 'منجز', 'متأخر', 'ملغي') DEFAULT 'مخطط',
                    `ملاحظات` TEXT,
                    `المستخدم` VARCHAR(50),
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX `idx_phase_id` (`معرف_المرحلة`),
                    INDEX `idx_event_date` (`التاريخ`),
                    INDEX `idx_event_type` (`نوع_الحدث`),
                    INDEX `idx_status` (`الحالة`),
                    FOREIGN KEY (`معرف_المرحلة`) REFERENCES `مراحل_المشروع`(`id`) ON DELETE CASCADE
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # جدول مردودات مواد المشاريع
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS `مردودات_مواد_المشاريع` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `رقم_المردود` VARCHAR(50) NOT NULL UNIQUE,
                    `معرف_المشروع` INT NOT NULL,
                    `معرف_المصروف_الأصلي` INT,
                    `نوع_المردود` ENUM('مواد_زائدة', 'مواد_معيبة', 'إلغاء_طلب', 'تعديل_كمية') NOT NULL,
                    `الوصف` VARCHAR(255) NOT NULL,
                    `المبلغ` DECIMAL(15,2) NOT NULL,
                    `تاريخ_المردود` DATE NOT NULL,
                    `معرف_المورد` INT,
                    `رقم_المرجع` VARCHAR(100),
                    `الحالة` ENUM('معلق', 'مؤكد', 'مستلم', 'ملغي') DEFAULT 'معلق',
                    `معرف_القيد_المحاسبي` INT,
                    `ملاحظات` TEXT,
                    `المستخدم` VARCHAR(50),
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX `idx_return_number` (`رقم_المردود`),
                    INDEX `idx_project_id` (`معرف_المشروع`),
                    INDEX `idx_original_expense` (`معرف_المصروف_الأصلي`),
                    INDEX `idx_return_type` (`نوع_المردود`),
                    INDEX `idx_return_date` (`تاريخ_المردود`),
                    INDEX `idx_supplier_id` (`معرف_المورد`),
                    INDEX `idx_status` (`الحالة`),
                    FOREIGN KEY (`معرف_المشروع`) REFERENCES `المشاريع`(`id`) ON DELETE CASCADE,
                    FOREIGN KEY (`معرف_المصروف_الأصلي`) REFERENCES `مصروفات_المشاريع`(`id`) ON DELETE SET NULL
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # جدول خسائر المشاريع
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS `خسائر_المشاريع` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `رقم_الخسارة` VARCHAR(50) NOT NULL UNIQUE,
                    `معرف_المشروع` INT NOT NULL,
                    `نوع_الخسارة` ENUM('تلف_مواد', 'حوادث', 'سرقة', 'أخطاء_تنفيذ', 'تغيير_تصميم', 'ظروف_جوية', 'أخرى') NOT NULL,
                    `الوصف` VARCHAR(255) NOT NULL,
                    `المبلغ` DECIMAL(15,2) NOT NULL,
                    `تاريخ_الخسارة` DATE NOT NULL,
                    `المسؤول` VARCHAR(255),
                    `قابلة_للاسترداد` BOOLEAN DEFAULT FALSE,
                    `مبلغ_الاسترداد` DECIMAL(15,2) DEFAULT 0,
                    `تاريخ_الاسترداد` DATE,
                    `مصدر_الاسترداد` VARCHAR(255),
                    `الحالة` ENUM('مؤكدة', 'قيد_المراجعة', 'مستردة_جزئياً', 'مستردة_كاملاً', 'غير_قابلة_للاسترداد') DEFAULT 'مؤكدة',
                    `معرف_القيد_المحاسبي` INT,
                    `ملاحظات` TEXT,
                    `المستخدم` VARCHAR(50),
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX `idx_loss_number` (`رقم_الخسارة`),
                    INDEX `idx_project_id` (`معرف_المشروع`),
                    INDEX `idx_loss_type` (`نوع_الخسارة`),
                    INDEX `idx_loss_date` (`تاريخ_الخسارة`),
                    INDEX `idx_recoverable` (`قابلة_للاسترداد`),
                    INDEX `idx_status` (`الحالة`),
                    FOREIGN KEY (`معرف_المشروع`) REFERENCES `المشاريع`(`id`) ON DELETE CASCADE
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            self.db.commit()
            logger.info("تم إنشاء جداول المشاريع بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء جداول المشاريع: {e}")
            self.db.rollback()
            return False
    
    def create_project(self, project_data: Dict[str, Any]) -> Optional[int]:
        """
        إنشاء مشروع جديد
        
        Args:
            project_data: بيانات المشروع
            
        Returns:
            معرف المشروع الجديد أو None
        """
        try:
            # التحقق من البيانات المطلوبة
            required_fields = ['اسم_المشروع', 'معرف_العميل', 'قيمة_المشروع', 'تاريخ_البداية', 'تاريخ_النهاية_المخطط']
            is_valid, error_msg = self.validate_data(project_data, required_fields)
            
            if not is_valid:
                logger.error(f"بيانات المشروع غير صحيحة: {error_msg}")
                return None
            
            # توليد رقم المشروع
            if 'رقم_المشروع' not in project_data:
                project_data['رقم_المشروع'] = self.generate_number('PRJ', 'المشاريع', 'رقم_المشروع')
            
            # إدراج المشروع
            project_id = self.insert_record('المشاريع', project_data)
            
            if project_id:
                self.log_operation('إنشاء_مشروع', 'المشاريع', project_id, f"رقم المشروع: {project_data['رقم_المشروع']}")
                logger.info(f"تم إنشاء مشروع جديد: {project_data['رقم_المشروع']}")
            
            return project_id
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء المشروع: {e}")
            return None
    
    def create_project_phase(self, phase_data: Dict[str, Any]) -> Optional[int]:
        """
        إنشاء مرحلة مشروع جديدة
        
        Args:
            phase_data: بيانات المرحلة
            
        Returns:
            معرف المرحلة الجديدة أو None
        """
        try:
            # التحقق من البيانات المطلوبة
            required_fields = ['معرف_المشروع', 'اسم_المرحلة', 'ترتيب_المرحلة', 'تاريخ_البداية_المخطط', 'تاريخ_النهاية_المخطط']
            is_valid, error_msg = self.validate_data(phase_data, required_fields)
            
            if not is_valid:
                logger.error(f"بيانات المرحلة غير صحيحة: {error_msg}")
                return None
            
            # إدراج المرحلة
            phase_id = self.insert_record('مراحل_المشروع', phase_data)
            
            if phase_id:
                self.log_operation('إنشاء_مرحلة_مشروع', 'مراحل_المشروع', phase_id, f"المرحلة: {phase_data['اسم_المرحلة']}")
                logger.info(f"تم إنشاء مرحلة مشروع جديدة: {phase_data['اسم_المرحلة']}")
            
            return phase_id
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء مرحلة المشروع: {e}")
            return None
    
    def update_project_progress(self, project_id: int, progress_percentage: float) -> bool:
        """
        تحديث نسبة إنجاز المشروع
        
        Args:
            project_id: معرف المشروع
            progress_percentage: نسبة الإنجاز (0-100)
            
        Returns:
            True إذا تم التحديث بنجاح
        """
        try:
            if not (0 <= progress_percentage <= 100):
                logger.error("نسبة الإنجاز يجب أن تكون بين 0 و 100")
                return False
            
            # تحديث نسبة الإنجاز
            update_data = {'نسبة_الإنجاز': progress_percentage}
            
            # تحديث الحالة حسب نسبة الإنجاز
            if progress_percentage == 0:
                update_data['الحالة'] = 'مخطط'
            elif progress_percentage == 100:
                update_data['الحالة'] = 'مكتمل'
                update_data['تاريخ_النهاية_الفعلي'] = date.today()
            else:
                update_data['الحالة'] = 'قيد_التنفيذ'
            
            success = self.update_record('المشاريع', update_data, project_id)
            
            if success:
                self.log_operation('تحديث_تقدم_مشروع', 'المشاريع', project_id, f"نسبة الإنجاز: {progress_percentage}%")
                logger.info(f"تم تحديث نسبة إنجاز المشروع {project_id} إلى {progress_percentage}%")
            
            return success
            
        except Exception as e:
            logger.error(f"خطأ في تحديث نسبة إنجاز المشروع: {e}")
            return False
    
    def get_project_summary(self, project_id: int) -> Dict[str, Any]:
        """
        الحصول على ملخص المشروع
        
        Args:
            project_id: معرف المشروع
            
        Returns:
            ملخص المشروع
        """
        try:
            # بيانات المشروع الأساسية
            project = self.get_record('المشاريع', project_id)
            if not project:
                return {'خطأ': 'المشروع غير موجود'}
            
            # إحصائيات المراحل
            phases_stats = self.execute_custom_query("""
                SELECT 
                    COUNT(*) as total_phases,
                    COUNT(CASE WHEN الحالة = 'مكتملة' THEN 1 END) as completed_phases,
                    AVG(نسبة_الإنجاز) as avg_progress,
                    SUM(الميزانية_المخططة) as total_budget,
                    SUM(الميزانية_المستخدمة) as used_budget
                FROM مراحل_المشروع 
                WHERE معرف_المشروع = %s
            """, (project_id,))
            
            # إحصائيات المهام
            tasks_stats = self.execute_custom_query("""
                SELECT 
                    COUNT(*) as total_tasks,
                    COUNT(CASE WHEN الحالة = 'مكتملة' THEN 1 END) as completed_tasks,
                    SUM(الساعات_المخططة) as planned_hours,
                    SUM(الساعات_الفعلية) as actual_hours
                FROM مهام_فريق_العمل 
                WHERE معرف_المشروع = %s
            """, (project_id,))
            
            # إحصائيات المصروفات
            expenses_stats = self.execute_custom_query("""
                SELECT 
                    COUNT(*) as total_expenses,
                    SUM(المبلغ) as total_amount
                FROM مصروفات_المشاريع 
                WHERE معرف_المشروع = %s AND الحالة = 'مدفوع'
            """, (project_id,))
            
            # إحصائيات الدفعات
            payments_stats = self.execute_custom_query("""
                SELECT 
                    COUNT(*) as total_payments,
                    SUM(المبلغ) as total_amount,
                    COUNT(CASE WHEN الحالة = 'مدفوعة' THEN 1 END) as paid_payments
                FROM دفعات_المشاريع 
                WHERE معرف_المشروع = %s
            """, (project_id,))
            
            return {
                'بيانات_المشروع': project,
                'إحصائيات_المراحل': phases_stats[0] if phases_stats else {},
                'إحصائيات_المهام': tasks_stats[0] if tasks_stats else {},
                'إحصائيات_المصروفات': expenses_stats[0] if expenses_stats else {},
                'إحصائيات_الدفعات': payments_stats[0] if payments_stats else {},
                'تاريخ_التقرير': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على ملخص المشروع: {e}")
            return {'خطأ': str(e)}
    
    def get_module_info(self) -> Dict[str, Any]:
        """
        الحصول على معلومات وحدة المشاريع
        
        Returns:
            معلومات الوحدة
        """
        try:
            return {
                'اسم_الوحدة': self.module_name,
                'الوصف': 'وحدة إدارة المشاريع والمقاولات',
                'الإصدار': '1.0.0',
                'الجداول': self.tables,
                'الوظائف_الرئيسية': [
                    'إدارة المشاريع',
                    'إدارة مراحل المشاريع',
                    'إدارة مهام فريق العمل',
                    'إدارة العهد المالية',
                    'إدارة دفعات المشاريع',
                    'إدارة مصروفات المشاريع',
                    'إدارة عقود المشاريع',
                    'متابعة الجدول الزمني',
                    'إدارة المردودات والخسائر'
                ]
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على معلومات الوحدة: {e}")
            return {'خطأ': str(e)}