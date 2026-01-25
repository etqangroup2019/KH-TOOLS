#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
وحدة إدارة التدريب
تدير البرامج التدريبية، المتدربين، والشهادات
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

class TrainingModule(BaseModule):
    """
    وحدة إدارة التدريب
    تدير جميع عمليات التدريب والشهادات
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        تهيئة وحدة التدريب
        
        Args:
            db_manager: مدير قاعدة البيانات
        """
        super().__init__(db_manager, "التدريب")
        
        # قائمة الجداول التي تديرها الوحدة
        self.tables = [
            'البرامج_التدريبية',
            'المجموعات_التدريبية',
            'المدربين',
            'المتدربين',
            'المشتركين_في_التدريب',
            'الشهادات',
            'مصروفات_التدريب'
        ]
    
    def create_tables(self) -> bool:
        """
        إنشاء جداول التدريب
        
        Returns:
            True إذا تم الإنشاء بنجاح
        """
        try:
            logger.info("إنشاء جداول التدريب...")
            
            # جدول البرامج التدريبية
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS `البرامج_التدريبية` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `رقم_البرنامج` VARCHAR(50) NOT NULL UNIQUE,
                    `اسم_البرنامج` VARCHAR(255) NOT NULL,
                    `نوع_البرنامج` ENUM('تقني', 'إداري', 'مهني', 'أكاديمي') DEFAULT 'تقني',
                    `مدة_البرنامج` INT NOT NULL COMMENT 'بالساعات',
                    `رسوم_البرنامج` DECIMAL(10,2) DEFAULT 0,
                    `الحد_الأدنى_للمشتركين` INT DEFAULT 5,
                    `الحد_الأقصى_للمشتركين` INT DEFAULT 25,
                    `وصف_البرنامج` TEXT,
                    `المتطلبات` TEXT,
                    `الحالة` ENUM('نشط', 'معطل', 'محذوف') DEFAULT 'نشط',
                    `ملاحظات` TEXT,
                    `المستخدم` VARCHAR(50),
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX `idx_program_number` (`رقم_البرنامج`),
                    INDEX `idx_program_name` (`اسم_البرنامج`),
                    INDEX `idx_program_type` (`نوع_البرنامج`),
                    INDEX `idx_status` (`الحالة`)
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            self.db.commit()
            logger.info("تم إنشاء جداول التدريب بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء جداول التدريب: {e}")
            self.db.rollback()
            return False
    
    def get_module_info(self) -> Dict[str, Any]:
        """
        الحصول على معلومات وحدة التدريب
        
        Returns:
            معلومات الوحدة
        """
        try:
            return {
                'اسم_الوحدة': self.module_name,
                'الوصف': 'وحدة إدارة التدريب والشهادات',
                'الإصدار': '1.0.0',
                'الجداول': self.tables,
                'الوظائف_الرئيسية': [
                    'إدارة البرامج التدريبية',
                    'إدارة المتدربين والمدربين',
                    'متابعة المجموعات التدريبية',
                    'إصدار الشهادات',
                    'إدارة مصروفات التدريب'
                ]
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على معلومات الوحدة: {e}")
            return {'خطأ': str(e)}