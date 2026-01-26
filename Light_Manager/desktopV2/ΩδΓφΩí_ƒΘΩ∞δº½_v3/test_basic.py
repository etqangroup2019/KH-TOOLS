#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار أساسي للنظام
"""

import sys
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.database import DatabaseManager

def test_basic():
    """اختبار أساسي لقاعدة البيانات"""
    print("بدء الاختبار الأساسي...")
    
    try:
        # إنشاء مدير قاعدة البيانات
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'kh123456',
            'database': 'منظومة_المهندس_v3_test'
        }
        
        db_manager = DatabaseManager(**db_config)
        print("✓ تم إنشاء مدير قاعدة البيانات")
        
        # اختبار الاتصال
        if db_manager.connect():
            print("✓ تم الاتصال بقاعدة البيانات")
        else:
            print("✗ فشل الاتصال بقاعدة البيانات")
            return False
        
        # اختبار إنشاء قاعدة البيانات
        if db_manager.create_database():
            print("✓ تم إنشاء/التحقق من قاعدة البيانات")
        else:
            print("✗ فشل في إنشاء قاعدة البيانات")
            return False
        
        # اختبار تنفيذ استعلام بسيط
        try:
            db_manager.execute_query("SELECT 1 as test")
            print("✓ تم تنفيذ استعلام تجريبي")
        except Exception as e:
            print(f"✗ فشل في تنفيذ الاستعلام: {e}")
            return False
        
        print("\n✓ الاختبار الأساسي مكتمل بنجاح!")
        return True
        
    except Exception as e:
        print(f"✗ خطأ في الاختبار: {e}")
        return False
    
    finally:
        if 'db_manager' in locals():
            db_manager.close_connection()
            print("✓ تم إغلاق الاتصال")

if __name__ == "__main__":
    success = test_basic()
    sys.exit(0 if success else 1)