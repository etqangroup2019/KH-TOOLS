#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
وحدة إدارة المقاولات
تدير عقود المقاولات، المراحل، والدفعات
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

class ContractsModule(BaseModule):
    """
    وحدة إدارة المقاولات
    تدير جميع عمليات المقاولات والعقود
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        تهيئة وحدة المقاولات
        
        Args:
            db_manager: مدير قاعدة البيانات
        """
        super().__init__(db_manager, "المقاولات")
        
        # قائمة الجداول التي تديرها الوحدة
        self.tables = [
            'المقاولات',
            'مراحل_المقاولات',
            'دفعات_المقاولات',
            'مصروفات_المقاولات'
        ]
    
    def create_tables(self) -> bool:
        """
        إنشاء جداول المقاولات
        
        Returns:
            True إذا تم الإنشاء بنجاح
        """
        try:
            logger.info("إنشاء جداول المقاولات...")
            
            # جدول المقاولات الرئيسي
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS `المقاولات` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `رقم_المقاولة` VARCHAR(50) NOT NULL UNIQUE,
                    `اسم_المقاولة` VARCHAR(255) NOT NULL,
                    `نوع_المقاولة` ENUM('إنشاءات', 'صيانة', 'تشطيبات', 'أخرى') DEFAULT 'إنشاءات',
                    `معرف_العميل` INT,
                    `قيمة_العقد` DECIMAL(15,2) NOT NULL,
                    `تاريخ_البداية` DATE NOT NULL,
                    `تاريخ_النهاية_المتوقع` DATE NOT NULL,
                    `تاريخ_النهاية_الفعلي` DATE,
                    `نسبة_الإنجاز` DECIMAL(5,2) DEFAULT 0,
                    `الموقع` TEXT,
                    `وصف_المقاولة` TEXT,
                    `الحالة` ENUM('جديدة', 'قيد_التنفيذ', 'معلقة', 'مكتملة', 'ملغية') DEFAULT 'جديدة',
                    `ملاحظات` TEXT,
                    `المستخدم` VARCHAR(50),
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX `idx_contract_number` (`رقم_المقاولة`),
                    INDEX `idx_contract_name` (`اسم_المقاولة`),
                    INDEX `idx_contract_type` (`نوع_المقاولة`),
                    INDEX `idx_client_id` (`معرف_العميل`),
                    INDEX `idx_status` (`الحالة`),
                    INDEX `idx_start_date` (`تاريخ_البداية`)
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            self.db.commit()
            logger.info("تم إنشاء جداول المقاولات بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء جداول المقاولات: {e}")
            self.db.rollback()
            return False
    
    def get_module_info(self) -> Dict[str, Any]:
        """
        الحصول على معلومات وحدة المقاولات
        
        Returns:
            معلومات الوحدة
        """
        try:
            return {
                'اسم_الوحدة': self.module_name,
                'الوصف': 'وحدة إدارة المقاولات والعقود',
                'الإصدار': '1.0.0',
                'الجداول': self.tables,
                'الوظائف_الرئيسية': [
                    'إدارة عقود المقاولات',
                    'متابعة مراحل التنفيذ',
                    'إدارة الدفعات',
                    'متابعة المصروفات',
                    'تقارير الإنجاز'
                ]
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على معلومات الوحدة: {e}")
            return {'خطأ': str(e)}