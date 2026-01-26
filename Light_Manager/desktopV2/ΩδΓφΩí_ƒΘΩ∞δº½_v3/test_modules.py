#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار النظام مع الوحدات
"""

import sys
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.database import DatabaseManager
from core.system_manager import SystemManager

def test_with_modules():
    """اختبار النظام مع الوحدات"""
    print("بدء اختبار النظام مع الوحدات...")
    
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
        
        # إنشاء مدير النظام
        system_manager = SystemManager(db_manager)
        print("✓ تم إنشاء مدير النظام")
        
        # اختبار تهيئة النظام
        if system_manager.initialize_system():
            print("✓ تم تهيئة النظام بنجاح")
        else:
            print("✗ فشل في تهيئة النظام")
            return False
        
        # عرض معلومات النظام
        system_info = system_manager.get_system_info()
        print(f"✓ إصدار النظام: {system_info.get('إصدار_النظام')}")
        print(f"✓ عدد الوحدات: {len(system_info.get('الوحدات_المتاحة', []))}")
        
        # عرض الوحدات
        print("\nالوحدات المتاحة:")
        for module_name in system_info.get('الوحدات_المتاحة', []):
            print(f"  - {module_name}")
        
        # عرض معلومات الوحدات
        modules_info = system_manager.get_modules_info()
        print(f"\nتفاصيل الوحدات:")
        for module_name, info in modules_info.items():
            if 'خطأ' not in info:
                print(f"  {module_name}:")
                print(f"    - الوصف: {info.get('الوصف', 'غير محدد')}")
                print(f"    - عدد الجداول: {len(info.get('الجداول', []))}")
        
        print("\n✓ اختبار النظام مع الوحدات مكتمل بنجاح!")
        return True
        
    except Exception as e:
        print(f"✗ خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if 'db_manager' in locals():
            db_manager.close_connection()
            print("✓ تم إغلاق الاتصال")

if __name__ == "__main__":
    success = test_with_modules()
    sys.exit(0 if success else 1)