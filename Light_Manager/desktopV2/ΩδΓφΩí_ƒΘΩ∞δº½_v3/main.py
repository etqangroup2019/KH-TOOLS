#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
الملف الرئيسي لتشغيل منظومة المهندس v3
نقطة الدخول الرئيسية للنظام
"""

import sys
import argparse
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.database import DatabaseManager
from core.system_manager import SystemManager
from config.settings import get_database_config, SYSTEM_CONFIG
import logging

def setup_logging():
    """إعداد نظام السجلات"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(project_root / 'logs' / 'main.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def run_system(test_mode=False, create_tables=True):
    """
    تشغيل النظام الكامل
    
    Args:
        test_mode: تشغيل في وضع الاختبار
        create_tables: إنشاء الجداول إذا لم تكن موجودة
        
    Returns:
        bool: True إذا تم التشغيل بنجاح
    """
    print("="*70)
    print(f"🚀 {SYSTEM_CONFIG['name']} - {SYSTEM_CONFIG['description']}")
    print(f"📋 الإصدار: {SYSTEM_CONFIG['version']}")
    print("="*70)
    
    try:
        # إعداد قاعدة البيانات
        db_config = get_database_config(test_mode=test_mode)
        
        print("🔄 جاري تهيئة النظام...")
        db_manager = DatabaseManager(**db_config)
        
        # اختبار الاتصال
        if not db_manager.connect():
            print("❌ فشل الاتصال بقاعدة البيانات")
            return False
        
        print("✅ تم الاتصال بقاعدة البيانات بنجاح")
        
        # إنشاء قاعدة البيانات إذا لم تكن موجودة
        if not db_manager.create_database():
            print("❌ فشل في إنشاء قاعدة البيانات")
            return False
        
        # إنشاء مدير النظام
        system_manager = SystemManager(db_manager)
        
        # تهيئة النظام
        print("🔄 جاري تهيئة الوحدات...")
        if not system_manager.initialize_system():
            print("❌ فشل في تهيئة النظام")
            return False
        
        print("✅ تم تهيئة النظام بنجاح")
        
        # عرض معلومات النظام
        display_system_info(system_manager)
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تشغيل النظام: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if 'db_manager' in locals():
            db_manager.close_connection()
            print("\n🔒 تم إغلاق الاتصال بقاعدة البيانات")

def display_system_info(system_manager):
    """
    عرض معلومات النظام
    
    Args:
        system_manager: مدير النظام
    """
    system_info = system_manager.get_system_info()
    modules_info = system_manager.get_modules_info()
    
    print("\n" + "="*70)
    print("📊 معلومات النظام:")
    print("="*70)
    print(f"📋 اسم النظام: {system_info.get('اسم_النظام')}")
    print(f"🔢 الإصدار: {system_info.get('إصدار_النظام')}")
    print(f"📝 الوصف: {system_info.get('وصف_النظام')}")
    print(f"📦 عدد الوحدات المفعلة: {len(system_info.get('الوحدات_المتاحة', []))}")
    print(f"🕐 تاريخ التهيئة: {system_info.get('تاريخ_التهيئة', 'غير محدد')}")
    
    print("\n" + "="*70)
    print("📦 الوحدات المتاحة:")
    print("="*70)
    
    total_tables = 0
    for i, module_name in enumerate(system_info.get('الوحدات_المتاحة', []), 1):
        module_info = modules_info.get(module_name, {})
        if 'خطأ' not in module_info:
            tables_count = len(module_info.get('الجداول', []))
            total_tables += tables_count
            
            print(f"{i:2d}. 📦 {module_name}")
            print(f"     📄 الوصف: {module_info.get('الوصف', 'غير محدد')}")
            print(f"     🗃️  عدد الجداول: {tables_count}")
            print(f"     🔧 الإصدار: {module_info.get('الإصدار', 'غير محدد')}")
            
            # عرض الوظائف الرئيسية إذا كانت متاحة
            functions = module_info.get('الوظائف_الرئيسية', [])
            if functions:
                print(f"     ⚙️  الوظائف: {', '.join(functions[:3])}")
                if len(functions) > 3:
                    print(f"              {'و ' + str(len(functions) - 3) + ' وظائف أخرى'}")
            print()
    
    print("="*70)
    print("📊 إحصائيات النظام:")
    print("="*70)
    print(f"🗃️  إجمالي الجداول: {total_tables}")
    print(f"📦 الوحدات النشطة: {len(system_info.get('الوحدات_المتاحة', []))}")
    print(f"🔗 حالة قاعدة البيانات: متصلة ✅")
    
    print("\n💡 الخطوات التالية:")
    print("   🔧 تطوير وحدات جديدة")
    print("   ➕ إضافة وظائف للوحدات الموجودة")
    print("   📊 إنشاء تقارير مخصصة")
    print("   🖥️  تطوير واجهة المستخدم")
    print("   🔒 تطبيق نظام الصلاحيات")

def run_tests():
    """تشغيل اختبارات النظام"""
    print("🧪 تشغيل اختبارات النظام...")
    
    # اختبار أساسي
    from tests.test_basic import test_basic
    if not test_basic():
        print("❌ فشل الاختبار الأساسي")
        return False
    
    # اختبار الوحدات
    from tests.test_modules import test_with_modules
    if not test_with_modules():
        print("❌ فشل اختبار الوحدات")
        return False
    
    print("✅ تم اجتياز جميع الاختبارات")
    return True

def create_backup():
    """إنشاء نسخة احتياطية"""
    print("💾 إنشاء نسخة احتياطية...")
    
    try:
        
        from scripts.backup import DatabaseBackup
        backup_system = DatabaseBackup()
        backup_file = backup_system.create_backup()
        
        if backup_file:
            print(f"✅ تم إنشاء النسخة الاحتياطية: {backup_file}")
            return True
        else:
            print("❌ فشل في إنشاء النسخة الاحتياطية")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في النسخ الاحتياطي: {e}")
        return False

def run_ui() -> bool:
    """تشغيل واجهة المستخدم PySide6"""
    try:
        from ui.app import Application
        app = Application(project_root)
        app.run()
        return True
    except Exception as e:
        print(f"❌ خطأ في تشغيل الواجهة: {e}")
        import traceback; traceback.print_exc()
        return False


def main():
    """الدالة الرئيسية"""
    parser = argparse.ArgumentParser(
        description='منظومة المهندس v3 - نظام المحاسبة الشامل',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--mode', 
        choices=['run', 'test', 'backup', 'info', 'ui'],
        default='run',
        help='وضع التشغيل (run: تشغيل عادي, test: اختبار, backup: نسخ احتياطي, info: معلومات, ui: واجهة المستخدم)'
    )
    
    parser.add_argument(
        '--test-mode',
        action='store_true',
        help='تشغيل في وضع الاختبار'
    )
    
    parser.add_argument(
        '--no-create-tables',
        action='store_true',
        help='عدم إنشاء الجداول'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='تفعيل وضع التطوير'
    )
    
    args = parser.parse_args()
    
    # إعداد السجلات
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    setup_logging()
    
    success = False
    
    if args.mode == 'run':
        success = run_system(
            test_mode=args.test_mode,
            create_tables=not args.no_create_tables
        )
    elif args.mode == 'test':
        success = run_tests()
    elif args.mode == 'backup':
        success = create_backup()
    elif args.mode == 'info':
        success = run_system(
            test_mode=args.test_mode,
            create_tables=False
        )
    elif args.mode == 'ui':
        success = run_ui()
    
    print("\n" + "="*70)
    if success:
        print("✅ تم تنفيذ العملية بنجاح")
    else:
        print("❌ فشل في تنفيذ العملية")
    print("="*70)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)