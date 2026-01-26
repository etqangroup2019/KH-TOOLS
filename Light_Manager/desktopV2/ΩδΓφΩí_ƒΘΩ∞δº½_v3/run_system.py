#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
تشغيل منظومة المهندس v3 - النظام الكامل
"""

import sys
from pathlib import Path

# إضافة مسار المشروع
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.database import DatabaseManager
from core.system_manager import SystemManager

def main():
    """تشغيل النظام الكامل"""
    print("="*60)
    print("منظومة المهندس v3 - نظام المحاسبة الشامل")
    print("="*60)
    
    try:
        # إنشاء مدير قاعدة البيانات
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'kh123456',
            'database': 'منظومة_المهندس_v3'
        }
        
        print("🔄 جاري تهيئة النظام...")
        db_manager = DatabaseManager(**db_config)
        
        # اختبار الاتصال
        if not db_manager.connect():
            print("❌ فشل الاتصال بقاعدة البيانات")
            return False
        
        print("✅ تم الاتصال بقاعدة البيانات بنجاح")
        
        # إنشاء مدير النظام
        system_manager = SystemManager(db_manager)
        
        # تهيئة النظام
        print("🔄 جاري تهيئة الوحدات...")
        if not system_manager.initialize_system():
            print("❌ فشل في تهيئة النظام")
            return False
        
        print("✅ تم تهيئة النظام بنجاح")
        
        # عرض معلومات النظام
        system_info = system_manager.get_system_info()
        modules_info = system_manager.get_modules_info()
        
        print("\n" + "="*60)
        print("معلومات النظام:")
        print("="*60)
        print(f"📋 اسم النظام: {system_info.get('اسم_النظام')}")
        print(f"🔢 الإصدار: {system_info.get('إصدار_النظام')}")
        print(f"📝 الوصف: {system_info.get('وصف_النظام')}")
        print(f"📊 عدد الوحدات المفعلة: {len(system_info.get('الوحدات_المتاحة', []))}")
        print(f"🕐 تاريخ التهيئة: {system_info.get('تاريخ_التهيئة', 'غير محدد')}")
        
        print("\n" + "="*60)
        print("الوحدات المتاحة:")
        print("="*60)
        
        for i, module_name in enumerate(system_info.get('الوحدات_المتاحة', []), 1):
            module_info = modules_info.get(module_name, {})
            if 'خطأ' not in module_info:
                print(f"{i:2d}. 📦 {module_name}")
                print(f"     📄 الوصف: {module_info.get('الوصف', 'غير محدد')}")
                print(f"     🗃️  عدد الجداول: {len(module_info.get('الجداول', []))}")
                print(f"     🔧 الإصدار: {module_info.get('الإصدار', 'غير محدد')}")
                print()
        
        print("="*60)
        print("🎉 النظام جاهز للاستخدام!")
        print("="*60)
        
        # عرض إحصائيات سريعة
        total_tables = sum(len(info.get('الجداول', [])) for info in modules_info.values() if 'خطأ' not in info)
        print(f"📊 إجمالي الجداول في النظام: {total_tables}")
        print(f"🔗 حالة قاعدة البيانات: {'متصلة ✅' if db_manager.is_connected() else 'غير متصلة ❌'}")
        
        print("\n💡 يمكنك الآن:")
        print("   - تطوير وحدات جديدة")
        print("   - إضافة وظائف للوحدات الموجودة")
        print("   - إنشاء تقارير مخصصة")
        print("   - تطوير واجهة المستخدم")
        
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

if __name__ == "__main__":
    success = main()
    print("\n" + "="*60)
    if success:
        print("✅ تم تشغيل النظام بنجاح")
    else:
        print("❌ فشل في تشغيل النظام")
    print("="*60)
    sys.exit(0 if success else 1)