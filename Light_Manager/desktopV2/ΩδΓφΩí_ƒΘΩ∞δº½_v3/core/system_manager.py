#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مدير النظام الرئيسي
يدير جميع الوحدات ويوفر واجهة موحدة للنظام
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import sys
from pathlib import Path

from .database import DatabaseManager

logger = logging.getLogger(__name__)

class SystemManager:
    """
    مدير النظام الرئيسي
    يدير جميع الوحدات ويوفر واجهة موحدة للنظام
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        تهيئة مدير النظام
        
        Args:
            db_manager: مدير قاعدة البيانات
        """
        self.db_manager = db_manager
        self.modules = {}
        self.system_info = {
            'اسم_النظام': 'منظومة المهندس v3',
            'إصدار_النظام': '3.0.0',
            'وصف_النظام': 'نظام المحاسبة الشامل',
            'تاريخ_التهيئة': None,
            'الوحدات_المتاحة': []
        }
        
        logger.info("تم تهيئة مدير النظام")
    
    def _import_modules(self):
        """استيراد الوحدات المتاحة"""
        try:
            # إضافة مسار المشروع إلى sys.path إذا لم يكن موجوداً
            project_root = Path(__file__).parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            
            # استيراد الوحدات المتاحة
            available_modules = {}
            
            # قائمة الوحدات المتاحة
            modules_to_import = [
                ('المحاسبة', 'modules.accounting.accounting_module', 'AccountingModule'),
                ('المشاريع', 'modules.projects.projects_module', 'ProjectsModule'),
                ('العملاء', 'modules.clients.clients_module', 'ClientsModule'),
                ('الموظفين', 'modules.employees.employees_module', 'EmployeesModule'),
                ('الموردين', 'modules.suppliers.suppliers_module', 'SuppliersModule'),
                ('المقاولات', 'modules.contracts.contracts_module', 'ContractsModule'),
                ('التدريب', 'modules.training.training_module', 'TrainingModule'),
                ('المصروفات', 'modules.expenses.expenses_module', 'ExpensesModule'),
                ('الإيرادات', 'modules.revenues.revenues_module', 'RevenuesModule'),
                ('التقارير', 'modules.reports.reports_module', 'ReportsModule')
            ]
            
            for module_name_ar, module_path, class_name in modules_to_import:
                try:
                    # استيراد الوحدة ديناميكياً
                    import importlib
                    module = importlib.import_module(module_path)
                    module_class = getattr(module, class_name)
                    available_modules[module_name_ar] = module_class
                    logger.info(f"تم استيراد وحدة {module_name_ar} بنجاح")
                except ImportError as e:
                    logger.warning(f"لم يتم العثور على وحدة {module_name_ar}: {e}")
                except AttributeError as e:
                    logger.warning(f"لم يتم العثور على كلاس {class_name} في وحدة {module_name_ar}: {e}")
                except Exception as e:
                    logger.warning(f"خطأ في استيراد وحدة {module_name_ar}: {e}")
            
            return available_modules
            
        except Exception as e:
            logger.error(f"خطأ في استيراد الوحدات: {e}")
            return {}
    
    def initialize_system(self) -> bool:
        """
        تهيئة النظام وجميع الوحدات
        
        Returns:
            True إذا تم التهيئة بنجاح
        """
        try:
            logger.info("بدء تهيئة النظام...")
            
            # التأكد من الاتصال بقاعدة البيانات
            if not self.db_manager.is_connected():
                if not self.db_manager.connect():
                    logger.error("فشل في الاتصال بقاعدة البيانات")
                    return False
            
            # إنشاء قاعدة البيانات إذا لم تكن موجودة
            if not self.db_manager.create_database():
                logger.error("فشل في إنشاء قاعدة البيانات")
                return False
            
            # استيراد الوحدات
            available_modules = self._import_modules()
            
            if not available_modules:
                logger.warning("لم يتم العثور على أي وحدات")
                return False
            
            # تهيئة الوحدات
            for module_name, module_class in available_modules.items():
                try:
                    logger.info(f"تهيئة وحدة {module_name}...")
                    module_instance = module_class(self.db_manager)
                    
                    # إنشاء جداول الوحدة
                    if module_instance.create_tables():
                        self.modules[module_name] = module_instance
                        self.system_info['الوحدات_المتاحة'].append(module_name)
                        logger.info(f"تم تهيئة وحدة {module_name} بنجاح")
                    else:
                        logger.error(f"فشل في إنشاء جداول وحدة {module_name}")
                        
                except Exception as e:
                    logger.error(f"خطأ في تهيئة وحدة {module_name}: {e}")
                    continue
            
            # تحديث معلومات النظام
            self.system_info['تاريخ_التهيئة'] = datetime.now().isoformat()
            
            logger.info(f"تم تهيئة النظام بنجاح - عدد الوحدات: {len(self.modules)}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تهيئة النظام: {e}")
            return False
    
    def get_module(self, module_name: str):
        """
        الحصول على وحدة معينة
        
        Args:
            module_name: اسم الوحدة
            
        Returns:
            الوحدة المطلوبة أو None
        """
        return self.modules.get(module_name)
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        الحصول على معلومات النظام
        
        Returns:
            معلومات النظام
        """
        return self.system_info.copy()
    
    def get_modules_info(self) -> Dict[str, Any]:
        """
        الحصول على معلومات جميع الوحدات
        
        Returns:
            معلومات الوحدات
        """
        modules_info = {}
        for module_name, module_instance in self.modules.items():
            try:
                modules_info[module_name] = module_instance.get_module_info()
            except Exception as e:
                logger.error(f"خطأ في الحصول على معلومات وحدة {module_name}: {e}")
                modules_info[module_name] = {'خطأ': str(e)}
        
        return modules_info
    
    def shutdown(self):
        """إغلاق النظام وتنظيف الموارد"""
        try:
            logger.info("إغلاق النظام...")
            
            # إغلاق الوحدات
            for module_name in self.modules:
                logger.info(f"إغلاق وحدة {module_name}")
            
            # إغلاق قاعدة البيانات
            self.db_manager.close_connection()
            
            logger.info("تم إغلاق النظام بنجاح")
            
        except Exception as e:
            logger.error(f"خطأ في إغلاق النظام: {e}")
    
    def __enter__(self):
        """دعم context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """دعم context manager"""
        self.shutdown()