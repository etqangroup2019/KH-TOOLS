#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
وحدة إدارة الموظفين
تدير بيانات الموظفين، الرواتب، الحضور، والتقييم
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

class EmployeesModule(BaseModule):
    """
    وحدة إدارة الموظفين
    تدير جميع عمليات الموظفين والموارد البشرية
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        تهيئة وحدة الموظفين
        
        Args:
            db_manager: مدير قاعدة البيانات
        """
        super().__init__(db_manager, "الموظفين")
        
        # قائمة الجداول التي تديرها الوحدة
        self.tables = [
            'الموظفين',
            'معاملات_الموظفين_المالية',
            'حضور_وانصراف_الموظفين',
            'تقييم_الموظفين',
            'العهد_الداخلية_للموظفين',
            'عقود_الموظفين',
            'مهام_الموظفين'
        ]
    
    def create_tables(self) -> bool:
        """
        إنشاء جداول الموظفين
        
        Returns:
            True إذا تم الإنشاء بنجاح
        """
        try:
            logger.info("إنشاء جداول الموظفين...")
            
            # جدول الموظفين الرئيسي
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS `الموظفين` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `رقم_الموظف` VARCHAR(50) NOT NULL UNIQUE,
                    `الاسم_الكامل` VARCHAR(255) NOT NULL,
                    `رقم_الهوية` VARCHAR(50) UNIQUE,
                    `تاريخ_الميلاد` DATE,
                    `الجنسية` VARCHAR(100),
                    `المنصب` VARCHAR(100),
                    `القسم` VARCHAR(100),
                    `تاريخ_التوظيف` DATE NOT NULL,
                    `الراتب_الأساسي` DECIMAL(10,2) DEFAULT 0,
                    `البدلات` DECIMAL(10,2) DEFAULT 0,
                    `رقم_الهاتف` VARCHAR(50),
                    `البريد_الإلكتروني` VARCHAR(100),
                    `العنوان` TEXT,
                    `الحالة` ENUM('نشط', 'معطل', 'مستقيل', 'مفصول') DEFAULT 'نشط',
                    `ملاحظات` TEXT,
                    `المستخدم` VARCHAR(50),
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX `idx_employee_number` (`رقم_الموظف`),
                    INDEX `idx_name` (`الاسم_الكامل`),
                    INDEX `idx_id_number` (`رقم_الهوية`),
                    INDEX `idx_department` (`القسم`),
                    INDEX `idx_position` (`المنصب`),
                    INDEX `idx_status` (`الحالة`)
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            self.db.commit()
            logger.info("تم إنشاء جداول الموظفين بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء جداول الموظفين: {e}")
            self.db.rollback()
            return False
    
    def get_module_info(self) -> Dict[str, Any]:
        """
        الحصول على معلومات وحدة الموظفين
        
        Returns:
            معلومات الوحدة
        """
        try:
            return {
                'اسم_الوحدة': self.module_name,
                'الوصف': 'وحدة إدارة الموظفين والموارد البشرية',
                'الإصدار': '1.0.0',
                'الجداول': self.tables,
                'الوظائف_الرئيسية': [
                    'إدارة بيانات الموظفين',
                    'إدارة الرواتب والبدلات',
                    'متابعة الحضور والانصراف',
                    'تقييم الأداء',
                    'إدارة العهد الداخلية',
                    'إدارة العقود'
                ]
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على معلومات الوحدة: {e}")
            return {'خطأ': str(e)}