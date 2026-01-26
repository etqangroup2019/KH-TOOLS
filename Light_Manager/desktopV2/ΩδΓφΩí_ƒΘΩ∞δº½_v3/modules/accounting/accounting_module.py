#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
وحدة المحاسبة الرئيسية
تدير شجرة الحسابات، القيود المحاسبية، مراكز التكلفة، والسنوات المالية
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

class AccountingModule(BaseModule):
    """
    وحدة المحاسبة الرئيسية
    تدير جميع العمليات المحاسبية الأساسية
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        تهيئة وحدة المحاسبة
        
        Args:
            db_manager: مدير قاعدة البيانات
        """
        super().__init__(db_manager, "المحاسبة")
        
        # قائمة الجداول التي تديرها الوحدة (بالترتيب الصحيح للإنشاء)
        self.tables = [
            'شجرة_الحسابات',
            'مراكز_التكلفة',
            'القيود_المحاسبية',
            'تفاصيل_القيود_المحاسبية',
            'السنوات_المالية',
            'أرصدة_الحسابات'
        ]
    
    def create_tables(self) -> bool:
        """
        إنشاء جداول المحاسبة
        
        Returns:
            True إذا تم الإنشاء بنجاح
        """
        try:
            logger.info("إنشاء جداول المحاسبة...")
            
            # جدول شجرة الحسابات (يجب إنشاؤه أولاً)
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS `شجرة_الحسابات` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `رقم_الحساب` VARCHAR(20) NOT NULL UNIQUE,
                    `اسم_الحساب` VARCHAR(255) NOT NULL,
                    `نوع_الحساب` ENUM('أصول', 'خصوم', 'حقوق_ملكية', 'إيرادات', 'مصروفات') NOT NULL,
                    `تصنيف_فرعي` VARCHAR(100),
                    `الحساب_الأب` INT,
                    `مستوى_الحساب` INT DEFAULT 1,
                    `قابل_للترحيل` BOOLEAN DEFAULT TRUE,
                    `الرصيد_الافتتاحي` DECIMAL(15,2) DEFAULT 0,
                    `الرصيد_الحالي` DECIMAL(15,2) DEFAULT 0,
                    `طبيعة_الرصيد` ENUM('مدين', 'دائن') NOT NULL,
                    `نشط` BOOLEAN DEFAULT TRUE,
                    `ملاحظات` TEXT,
                    `المستخدم` VARCHAR(50),
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX `idx_account_number` (`رقم_الحساب`),
                    INDEX `idx_account_type` (`نوع_الحساب`),
                    INDEX `idx_parent_account` (`الحساب_الأب`),
                    INDEX `idx_level` (`مستوى_الحساب`),
                    INDEX `idx_active` (`نشط`),
                    FOREIGN KEY (`الحساب_الأب`) REFERENCES `شجرة_الحسابات`(`id`) ON DELETE SET NULL
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # جدول مراكز التكلفة (يجب إنشاؤه قبل القيود المحاسبية)
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS `مراكز_التكلفة` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `رقم_مركز_التكلفة` VARCHAR(20) NOT NULL UNIQUE,
                    `اسم_مركز_التكلفة` VARCHAR(255) NOT NULL,
                    `نوع_المركز` ENUM('إنتاجي', 'خدمي', 'إداري', 'تسويقي', 'مشروع', 'قسم') NOT NULL,
                    `المركز_الأب` INT,
                    `مستوى_المركز` INT DEFAULT 1,
                    `المدير_المسؤول` VARCHAR(255),
                    `الميزانية_المخططة` DECIMAL(15,2) DEFAULT 0,
                    `الميزانية_المستخدمة` DECIMAL(15,2) DEFAULT 0,
                    `نسبة_الاستخدام` DECIMAL(5,2) GENERATED ALWAYS AS (
                        CASE 
                            WHEN `الميزانية_المخططة` > 0 
                            THEN (`الميزانية_المستخدمة` / `الميزانية_المخططة`) * 100
                            ELSE 0
                        END
                    ) STORED,
                    `تاريخ_البداية` DATE,
                    `تاريخ_النهاية` DATE,
                    `نشط` BOOLEAN DEFAULT TRUE,
                    `ملاحظات` TEXT,
                    `المستخدم` VARCHAR(50),
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX `idx_center_number` (`رقم_مركز_التكلفة`),
                    INDEX `idx_center_type` (`نوع_المركز`),
                    INDEX `idx_parent_center` (`المركز_الأب`),
                    INDEX `idx_level` (`مستوى_المركز`),
                    INDEX `idx_active` (`نشط`),
                    FOREIGN KEY (`المركز_الأب`) REFERENCES `مراكز_التكلفة`(`id`) ON DELETE SET NULL
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # جدول القيود المحاسبية (الآن يمكن إنشاؤه بأمان)
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS `القيود_المحاسبية` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `رقم_القيد` VARCHAR(50) NOT NULL UNIQUE,
                    `تاريخ_القيد` DATE NOT NULL,
                    `نوع_القيد` ENUM('افتتاحي', 'يومي', 'تسوية', 'إقفال', 'تصحيحي') DEFAULT 'يومي',
                    `البيان` TEXT NOT NULL,
                    `إجمالي_المدين` DECIMAL(15,2) NOT NULL DEFAULT 0,
                    `إجمالي_الدائن` DECIMAL(15,2) NOT NULL DEFAULT 0,
                    `متوازن` BOOLEAN GENERATED ALWAYS AS (`إجمالي_المدين` = `إجمالي_الدائن`) STORED,
                    `معرف_مركز_التكلفة` INT,
                    `معرف_المرجع` INT COMMENT 'معرف السجل المرجعي',
                    `نوع_المرجع` VARCHAR(50) COMMENT 'نوع السجل المرجعي',
                    `الحالة` ENUM('مسودة', 'مؤكد', 'مرحل', 'ملغي') DEFAULT 'مسودة',
                    `تاريخ_الترحيل` DATETIME,
                    `مرحل_بواسطة` VARCHAR(50),
                    `ملاحظات` TEXT,
                    `المستخدم` VARCHAR(50),
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    `السنة` INT GENERATED ALWAYS AS (YEAR(`تاريخ_القيد`)) STORED,
                    `الشهر` INT GENERATED ALWAYS AS (MONTH(`تاريخ_القيد`)) STORED,
                    INDEX `idx_entry_number` (`رقم_القيد`),
                    INDEX `idx_entry_date` (`تاريخ_القيد`),
                    INDEX `idx_entry_type` (`نوع_القيد`),
                    INDEX `idx_status` (`الحالة`),
                    INDEX `idx_cost_center` (`معرف_مركز_التكلفة`),
                    INDEX `idx_reference` (`معرف_المرجع`, `نوع_المرجع`),
                    INDEX `idx_year` (`السنة`),
                    INDEX `idx_month` (`الشهر`),
                    FOREIGN KEY (`معرف_مركز_التكلفة`) REFERENCES `مراكز_التكلفة`(`id`) ON DELETE SET NULL
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # جدول تفاصيل القيود المحاسبية
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS `تفاصيل_القيود_المحاسبية` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `معرف_القيد` INT NOT NULL,
                    `معرف_الحساب` INT NOT NULL,
                    `البيان` VARCHAR(255) NOT NULL,
                    `مدين` DECIMAL(15,2) DEFAULT 0,
                    `دائن` DECIMAL(15,2) DEFAULT 0,
                    `معرف_مركز_التكلفة` INT,
                    `ملاحظات` TEXT,
                    `ترتيب_السطر` INT DEFAULT 0,
                    INDEX `idx_entry_id` (`معرف_القيد`),
                    INDEX `idx_account_id` (`معرف_الحساب`),
                    INDEX `idx_cost_center` (`معرف_مركز_التكلفة`),
                    INDEX `idx_line_order` (`ترتيب_السطر`),
                    FOREIGN KEY (`معرف_القيد`) REFERENCES `القيود_المحاسبية`(`id`) ON DELETE CASCADE,
                    FOREIGN KEY (`معرف_الحساب`) REFERENCES `شجرة_الحسابات`(`id`) ON DELETE RESTRICT,
                    FOREIGN KEY (`معرف_مركز_التكلفة`) REFERENCES `مراكز_التكلفة`(`id`) ON DELETE SET NULL
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # جدول السنوات المالية
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS `السنوات_المالية` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `السنة` INT NOT NULL UNIQUE,
                    `تاريخ_البداية` DATE NOT NULL,
                    `تاريخ_النهاية` DATE NOT NULL,
                    `الحالة` ENUM('مفتوحة', 'مغلقة', 'مؤرشفة') DEFAULT 'مفتوحة',
                    `تاريخ_الإغلاق` DATETIME,
                    `مغلقة_بواسطة` VARCHAR(50),
                    `ملاحظات` TEXT,
                    `المستخدم` VARCHAR(50),
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX `idx_year` (`السنة`),
                    INDEX `idx_status` (`الحالة`),
                    INDEX `idx_start_date` (`تاريخ_البداية`),
                    INDEX `idx_end_date` (`تاريخ_النهاية`)
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # جدول أرصدة الحسابات
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS `أرصدة_الحسابات` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `معرف_الحساب` INT NOT NULL,
                    `السنة` INT NOT NULL,
                    `الشهر` INT NOT NULL,
                    `الرصيد_الافتتاحي` DECIMAL(15,2) DEFAULT 0,
                    `إجمالي_المدين` DECIMAL(15,2) DEFAULT 0,
                    `إجمالي_الدائن` DECIMAL(15,2) DEFAULT 0,
                    `الرصيد_الختامي` DECIMAL(15,2) GENERATED ALWAYS AS (
                        `الرصيد_الافتتاحي` + `إجمالي_المدين` - `إجمالي_الدائن`
                    ) STORED,
                    `تاريخ_آخر_تحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY `unique_account_period` (`معرف_الحساب`, `السنة`, `الشهر`),
                    INDEX `idx_account` (`معرف_الحساب`),
                    INDEX `idx_period` (`السنة`, `الشهر`),
                    INDEX `idx_last_update` (`تاريخ_آخر_تحديث`),
                    FOREIGN KEY (`معرف_الحساب`) REFERENCES `شجرة_الحسابات`(`id`) ON DELETE CASCADE
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # إدراج البيانات الافتراضية
            self._insert_default_accounting_data()
            
            self.db.commit()
            logger.info("تم إنشاء جداول المحاسبة بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء جداول المحاسبة: {e}")
            self.db.rollback()
            return False
    
    def _insert_default_accounting_data(self):
        """إدراج البيانات الافتراضية للمحاسبة"""
        logger.info("إدراج البيانات الافتراضية للمحاسبة...")
        
        # شجرة الحسابات الافتراضية
        default_accounts = [
            # الأصول
            {'رقم_الحساب': '1000', 'اسم_الحساب': 'الأصول', 'نوع_الحساب': 'أصول', 'طبيعة_الرصيد': 'مدين', 'قابل_للترحيل': False},
            {'رقم_الحساب': '1100', 'اسم_الحساب': 'الأصول المتداولة', 'نوع_الحساب': 'أصول', 'طبيعة_الرصيد': 'مدين', 'قابل_للترحيل': False, 'الحساب_الأب': 1},
            {'رقم_الحساب': '1101', 'اسم_الحساب': 'النقدية', 'نوع_الحساب': 'أصول', 'طبيعة_الرصيد': 'مدين', 'الحساب_الأب': 2},
            {'رقم_الحساب': '1102', 'اسم_الحساب': 'البنوك', 'نوع_الحساب': 'أصول', 'طبيعة_الرصيد': 'مدين', 'الحساب_الأب': 2},
            {'رقم_الحساب': '1103', 'اسم_الحساب': 'العملاء', 'نوع_الحساب': 'أصول', 'طبيعة_الرصيد': 'مدين', 'الحساب_الأب': 2},
            {'رقم_الحساب': '1200', 'اسم_الحساب': 'الأصول الثابتة', 'نوع_الحساب': 'أصول', 'طبيعة_الرصيد': 'مدين', 'قابل_للترحيل': False, 'الحساب_الأب': 1},
            {'رقم_الحساب': '1201', 'اسم_الحساب': 'الأراضي والمباني', 'نوع_الحساب': 'أصول', 'طبيعة_الرصيد': 'مدين', 'الحساب_الأب': 6},
            {'رقم_الحساب': '1202', 'اسم_الحساب': 'المعدات والآلات', 'نوع_الحساب': 'أصول', 'طبيعة_الرصيد': 'مدين', 'الحساب_الأب': 6},
            
            # الخصوم
            {'رقم_الحساب': '2000', 'اسم_الحساب': 'الخصوم', 'نوع_الحساب': 'خصوم', 'طبيعة_الرصيد': 'دائن', 'قابل_للترحيل': False},
            {'رقم_الحساب': '2100', 'اسم_الحساب': 'الخصوم المتداولة', 'نوع_الحساب': 'خصوم', 'طبيعة_الرصيد': 'دائن', 'قابل_للترحيل': False, 'الحساب_الأب': 9},
            {'رقم_الحساب': '2101', 'اسم_الحساب': 'الموردين', 'نوع_الحساب': 'خصوم', 'طبيعة_الرصيد': 'دائن', 'الحساب_الأب': 10},
            {'رقم_الحساب': '2102', 'اسم_الحساب': 'رواتب مستحقة', 'نوع_الحساب': 'خصوم', 'طبيعة_الرصيد': 'دائن', 'الحساب_الأب': 10},
            
            # حقوق الملكية
            {'رقم_الحساب': '3000', 'اسم_الحساب': 'حقوق الملكية', 'نوع_الحساب': 'حقوق_ملكية', 'طبيعة_الرصيد': 'دائن', 'قابل_للترحيل': False},
            {'رقم_الحساب': '3001', 'اسم_الحساب': 'رأس المال', 'نوع_الحساب': 'حقوق_ملكية', 'طبيعة_الرصيد': 'دائن', 'الحساب_الأب': 13},
            {'رقم_الحساب': '3002', 'اسم_الحساب': 'الأرباح المحتجزة', 'نوع_الحساب': 'حقوق_ملكية', 'طبيعة_الرصيد': 'دائن', 'الحساب_الأب': 13},
            
            # الإيرادات
            {'رقم_الحساب': '4000', 'اسم_الحساب': 'الإيرادات', 'نوع_الحساب': 'إيرادات', 'طبيعة_الرصيد': 'دائن', 'قابل_للترحيل': False},
            {'رقم_الحساب': '4001', 'اسم_الحساب': 'إيرادات المشاريع', 'نوع_الحساب': 'إيرادات', 'طبيعة_الرصيد': 'دائن', 'الحساب_الأب': 16},
            {'رقم_الحساب': '4002', 'اسم_الحساب': 'إيرادات التدريب', 'نوع_الحساب': 'إيرادات', 'طبيعة_الرصيد': 'دائن', 'الحساب_الأب': 16},
            
            # المصروفات
            {'رقم_الحساب': '5000', 'اسم_الحساب': 'المصروفات', 'نوع_الحساب': 'مصروفات', 'طبيعة_الرصيد': 'مدين', 'قابل_للترحيل': False},
            {'رقم_الحساب': '5001', 'اسم_الحساب': 'مصروفات المشاريع', 'نوع_الحساب': 'مصروفات', 'طبيعة_الرصيد': 'مدين', 'الحساب_الأب': 19},
            {'رقم_الحساب': '5002', 'اسم_الحساب': 'الرواتب والأجور', 'نوع_الحساب': 'مصروفات', 'طبيعة_الرصيد': 'مدين', 'الحساب_الأب': 19},
            {'رقم_الحساب': '5003', 'اسم_الحساب': 'مصروفات إدارية', 'نوع_الحساب': 'مصروفات', 'طبيعة_الرصيد': 'مدين', 'الحساب_الأب': 19}
        ]
        
        for account in default_accounts:
            account['المستخدم'] = 'system'
            try:
                self.db.insert_data('شجرة_الحسابات', account)
            except:
                pass  # تجاهل الأخطاء إذا كانت البيانات موجودة
        
        # مراكز التكلفة الافتراضية
        default_cost_centers = [
            {'رقم_مركز_التكلفة': 'CC001', 'اسم_مركز_التكلفة': 'الإدارة العامة', 'نوع_المركز': 'إداري'},
            {'رقم_مركز_التكلفة': 'CC002', 'اسم_مركز_التكلفة': 'قسم المشاريع', 'نوع_المركز': 'إنتاجي'},
            {'رقم_مركز_التكلفة': 'CC003', 'اسم_مركز_التكلفة': 'قسم التدريب', 'نوع_المركز': 'خدمي'},
            {'رقم_مركز_التكلفة': 'CC004', 'اسم_مركز_التكلفة': 'قسم التسويق', 'نوع_المركز': 'تسويقي'}
        ]
        
        for center in default_cost_centers:
            center['المستخدم'] = 'system'
            try:
                self.db.insert_data('مراكز_التكلفة', center)
            except:
                pass
        
        # السنة المالية الحالية
        current_year = datetime.now().year
        default_financial_year = {
            'السنة': current_year,
            'تاريخ_البداية': f'{current_year}-01-01',
            'تاريخ_النهاية': f'{current_year}-12-31',
            'الحالة': 'مفتوحة',
            'المستخدم': 'system'
        }
        
        try:
            self.db.insert_data('السنوات_المالية', default_financial_year)
        except:
            pass
    
    def create_journal_entry(self, description: str, entry_details: List[Dict], entry_type: str = 'يومي',
                           cost_center_id: int = None, reference_id: int = None, reference_type: str = None) -> Optional[int]:
        """
        إنشاء قيد محاسبي جديد
        
        Args:
            description: وصف القيد
            entry_details: تفاصيل القيد [{'معرف_الحساب': int, 'البيان': str, 'مدين': float, 'دائن': float}]
            entry_type: نوع القيد
            cost_center_id: معرف مركز التكلفة
            reference_id: معرف المرجع
            reference_type: نوع المرجع
            
        Returns:
            معرف القيد الجديد أو None
        """
        try:
            # التحقق من صحة البيانات
            if not entry_details:
                logger.error("تفاصيل القيد مطلوبة")
                return None
            
            # حساب الإجماليات
            total_debit = sum(detail.get('مدين', 0) for detail in entry_details)
            total_credit = sum(detail.get('دائن', 0) for detail in entry_details)
            
            if total_debit != total_credit:
                logger.error(f"القيد غير متوازن - المدين: {total_debit}, الدائن: {total_credit}")
                return None
            
            # توليد رقم القيد
            entry_number = self.generate_number('JE', 'القيود_المحاسبية', 'رقم_القيد')
            
            # إنشاء القيد الرئيسي
            entry_data = {
                'رقم_القيد': entry_number,
                'تاريخ_القيد': date.today(),
                'نوع_القيد': entry_type,
                'البيان': description,
                'إجمالي_المدين': total_debit,
                'إجمالي_الدائن': total_credit,
                'معرف_مركز_التكلفة': cost_center_id,
                'معرف_المرجع': reference_id,
                'نوع_المرجع': reference_type,
                'الحالة': 'مؤكد',
                'المستخدم': 'system'
            }
            
            entry_id = self.insert_record('القيود_المحاسبية', entry_data)
            if not entry_id:
                return None
            
            # إنشاء تفاصيل القيد
            for i, detail in enumerate(entry_details):
                detail_data = {
                    'معرف_القيد': entry_id,
                    'معرف_الحساب': detail['معرف_الحساب'],
                    'البيان': detail['البيان'],
                    'مدين': detail.get('مدين', 0),
                    'دائن': detail.get('دائن', 0),
                    'معرف_مركز_التكلفة': detail.get('معرف_مركز_التكلفة', cost_center_id),
                    'ملاحظات': detail.get('ملاحظات'),
                    'ترتيب_السطر': i + 1
                }
                
                if not self.insert_record('تفاصيل_القيود_المحاسبية', detail_data):
                    # في حالة فشل إدراج التفاصيل، احذف القيد الرئيسي
                    self.delete_record('القيود_المحاسبية', entry_id)
                    return None
            
            # تحديث أرصدة الحسابات
            self._update_account_balances(entry_details)
            
            self.log_operation('إنشاء_قيد_محاسبي', 'القيود_المحاسبية', entry_id, f'رقم القيد: {entry_number}')
            logger.info(f"تم إنشاء قيد محاسبي جديد: {entry_number}")
            
            return entry_id
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء القيد المحاسبي: {e}")
            return None
    
    def _update_account_balances(self, entry_details: List[Dict]):
        """تحديث أرصدة الحسابات"""
        try:
            current_year = datetime.now().year
            current_month = datetime.now().month
            
            for detail in entry_details:
                account_id = detail['معرف_الحساب']
                debit = detail.get('مدين', 0)
                credit = detail.get('دائن', 0)
                
                # البحث عن رصيد الحساب للفترة الحالية
                existing_balance = self.db.fetch_data(
                    'أرصدة_الحسابات',
                    '*',
                    'معرف_الحساب = %s AND السنة = %s AND الشهر = %s',
                    (account_id, current_year, current_month)
                )
                
                if existing_balance:
                    # تحديث الرصيد الموجود
                    balance_data = {
                        'إجمالي_المدين': existing_balance[0]['إجمالي_المدين'] + debit,
                        'إجمالي_الدائن': existing_balance[0]['إجمالي_الدائن'] + credit
                    }
                    
                    self.db.update_data(
                        'أرصدة_الحسابات',
                        balance_data,
                        'id = %s',
                        (existing_balance[0]['id'],)
                    )
                else:
                    # إنشاء رصيد جديد
                    balance_data = {
                        'معرف_الحساب': account_id,
                        'السنة': current_year,
                        'الشهر': current_month,
                        'الرصيد_الافتتاحي': 0,
                        'إجمالي_المدين': debit,
                        'إجمالي_الدائن': credit
                    }
                    
                    self.db.insert_data('أرصدة_الحسابات', balance_data)
                
                # تحديث الرصيد الحالي في شجرة الحسابات
                account_info = self.get_record('شجرة_الحسابات', account_id)
                if account_info:
                    if account_info['طبيعة_الرصيد'] == 'مدين':
                        new_balance = account_info['الرصيد_الحالي'] + debit - credit
                    else:
                        new_balance = account_info['الرصيد_الحالي'] + credit - debit
                    
                    self.update_record('شجرة_الحسابات', {'الرصيد_الحالي': new_balance}, account_id)
                    
        except Exception as e:
            logger.error(f"خطأ في تحديث أرصدة الحسابات: {e}")
    
    def calculate_account_balance(self, account_id: int, as_of_date: date = None) -> Decimal:
        """
        حساب رصيد حساب معين
        
        Args:
            account_id: معرف الحساب
            as_of_date: التاريخ المطلوب حساب الرصيد إليه
            
        Returns:
            رصيد الحساب
        """
        try:
            if as_of_date is None:
                as_of_date = date.today()
            
            # الحصول على معلومات الحساب
            account = self.get_record('شجرة_الحسابات', account_id)
            if not account:
                return Decimal('0')
            
            # حساب إجمالي المدين والدائن
            sql = """
                SELECT 
                    COALESCE(SUM(d.مدين), 0) as total_debit,
                    COALESCE(SUM(d.دائن), 0) as total_credit
                FROM تفاصيل_القيود_المحاسبية d
                JOIN القيود_المحاسبية e ON d.معرف_القيد = e.id
                WHERE d.معرف_الحساب = %s 
                AND e.تاريخ_القيد <= %s 
                AND e.الحالة IN ('مؤكد', 'مرحل')
            """
            
            results = self.execute_custom_query(sql, (account_id, as_of_date))
            
            if results:
                total_debit = Decimal(str(results[0]['total_debit']))
                total_credit = Decimal(str(results[0]['total_credit']))
                
                # حساب الرصيد حسب طبيعة الحساب
                if account['طبيعة_الرصيد'] == 'مدين':
                    balance = Decimal(str(account['الرصيد_الافتتاحي'])) + total_debit - total_credit
                else:
                    balance = Decimal(str(account['الرصيد_الافتتاحي'])) + total_credit - total_debit
                
                return balance
            
            return Decimal(str(account['الرصيد_الافتتاحي']))
            
        except Exception as e:
            logger.error(f"خطأ في حساب رصيد الحساب: {e}")
            return Decimal('0')
    
    def get_module_info(self) -> Dict[str, Any]:
        """
        الحصول على معلومات وحدة المحاسبة
        
        Returns:
            معلومات الوحدة
        """
        try:
            return {
                'اسم_الوحدة': self.module_name,
                'الوصف': 'وحدة المحاسبة والتقارير المالية',
                'الإصدار': '1.0.0',
                'الجداول': self.tables,
                'الوظائف_الرئيسية': [
                    'إدارة شجرة الحسابات',
                    'إنشاء القيود المحاسبية',
                    'إدارة مراكز التكلفة',
                    'إدارة السنوات المالية',
                    'حساب أرصدة الحسابات',
                    'التقارير المالية'
                ]
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على معلومات الوحدة: {e}")
            return {'خطأ': str(e)}