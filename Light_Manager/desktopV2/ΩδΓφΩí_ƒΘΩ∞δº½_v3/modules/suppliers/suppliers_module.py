#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
وحدة إدارة الموردين
تدير بيانات الموردين، الفواتير، والمدفوعات
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

class SuppliersModule(BaseModule):
    """
    وحدة إدارة الموردين
    تدير جميع عمليات الموردين والمشتريات
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        تهيئة وحدة الموردين
        
        Args:
            db_manager: مدير قاعدة البيانات
        """
        super().__init__(db_manager, "الموردين")
        
        # قائمة الجداول التي تديرها الوحدة
        self.tables = [
            'الموردين',
            'معاملات_الموردين_المالية',
            'تفاصيل_فواتير_الموردين',
            'مردودات_الموردين'
        ]
    
    def create_tables(self) -> bool:
        """
        إنشاء جداول الموردين
        
        Returns:
            True إذا تم الإنشاء بنجاح
        """
        try:
            logger.info("إنشاء جداول الموردين...")
            
            # جدول الموردين الرئيسي
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS `الموردين` (
                    `id` INT PRIMARY KEY AUTO_INCREMENT,
                    `رقم_المورد` VARCHAR(50) NOT NULL UNIQUE,
                    `اسم_المورد` VARCHAR(255) NOT NULL,
                    `نوع_المورد` ENUM('فرد', 'شركة', 'مؤسسة') DEFAULT 'شركة',
                    `رقم_السجل_التجاري` VARCHAR(50),
                    `الرقم_الضريبي` VARCHAR(50),
                    `العنوان` TEXT,
                    `المدينة` VARCHAR(100),
                    `رقم_الهاتف` VARCHAR(50),
                    `البريد_الإلكتروني` VARCHAR(100),
                    `نوع_النشاط` VARCHAR(100),
                    `تصنيف_المورد` ENUM('محلي', 'إقليمي', 'دولي') DEFAULT 'محلي',
                    `درجة_التقييم` ENUM('ممتاز', 'جيد_جداً', 'جيد', 'مقبول', 'ضعيف') DEFAULT 'جيد',
                    `حد_الائتمان` DECIMAL(15,2) DEFAULT 0,
                    `رصيد_المورد` DECIMAL(15,2) DEFAULT 0,
                    `إجمالي_المشتريات` DECIMAL(15,2) DEFAULT 0,
                    `تاريخ_آخر_معاملة` DATE,
                    `الحالة` ENUM('نشط', 'معطل', 'محذوف') DEFAULT 'نشط',
                    `ملاحظات` TEXT,
                    `المستخدم` VARCHAR(50),
                    `تاريخ_الإضافة` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `تاريخ_التحديث` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX `idx_supplier_number` (`رقم_المورد`),
                    INDEX `idx_supplier_name` (`اسم_المورد`),
                    INDEX `idx_supplier_type` (`نوع_المورد`),
                    INDEX `idx_classification` (`تصنيف_المورد`),
                    INDEX `idx_rating` (`درجة_التقييم`),
                    INDEX `idx_status` (`الحالة`)
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            self.db.commit()
            logger.info("تم إنشاء جداول الموردين بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء جداول الموردين: {e}")
            self.db.rollback()
            return False
    
    def get_module_info(self) -> Dict[str, Any]:
        """
        الحصول على معلومات وحدة الموردين
        
        Returns:
            معلومات الوحدة
        """
        try:
            return {
                'اسم_الوحدة': self.module_name,
                'الوصف': 'وحدة إدارة الموردين والمشتريات',
                'الإصدار': '1.0.0',
                'الجداول': self.tables,
                'الوظائف_الرئيسية': [
                    'إدارة بيانات الموردين',
                    'إدارة الفواتير والمدفوعات',
                    'متابعة المردودات',
                    'تقييم الموردين',
                    'تقارير المشتريات'
                ]
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على معلومات الوحدة: {e}")
            return {'خطأ': str(e)}