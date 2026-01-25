#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبارات النظام الأساسية
"""

import unittest
import sys
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.database import DatabaseManager
from core.system_manager import SystemManager

class TestSystem(unittest.TestCase):
    """
    اختبارات النظام الأساسية
    """
    
    def setUp(self):
        """إعداد الاختبارات"""
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'kh123456',
            'database': 'test_منظومة_المهندس_v3',
            'charset': 'utf8mb4'
        }
        
    def test_database_connection(self):
        """اختبار الاتصال بقاعدة البيانات"""
        db_manager = DatabaseManager(**self.db_config)
        self.assertTrue(db_manager.connect())
        db_manager.close_connection()
        
    def test_system_initialization(self):
        """اختبار تهيئة النظام"""
        db_manager = DatabaseManager(**self.db_config)
        system_manager = SystemManager(db_manager)
        
        # محاولة تهيئة النظام
        result = system_manager.initialize_system()
        self.assertTrue(result)
        
        # التحقق من معلومات النظام
        system_info = system_manager.get_system_info()
        self.assertIsInstance(system_info, dict)
        self.assertIn('إصدار_النظام', system_info)
        
        db_manager.close_connection()

if __name__ == '__main__':
    unittest.main()