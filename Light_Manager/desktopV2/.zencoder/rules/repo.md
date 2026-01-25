# Repository Overview

هذا الملف يُساعد المساعد الذكي على فهم مكونات المشروع بسرعة لتحسين جودة التحليل والإجابات.

## معلومات عامة
- **اسم المشروع**: desktopV2
- **النظام الفرعي الرئيسي**: منظومة المهندس v3 (Python)
- **الغرض**: نظام محاسبي/إداري معياري مع وحدات (محاسبة، مشاريع، عملاء، موظفون، موردون...)
- **لغة الواجهة**: العربية
- **المنصة**: Windows 11

## أهم المسارات
- **ル الجذر**: d:\\ProjectManager\\desktopV2
- **منظومة المهندس v3**: d:\\ProjectManager\\desktopV2\\منظومة_المهندس_v3
  - **النقطة الرئيسية**: main.py
  - **النواة (Core)**: core\
    - system_manager.py: إدارة الوحدات وتحميلها ديناميكياً
    - database.py: إدارة قاعدة البيانات
    - base_module.py: واجهة مشتركة للوحدات (إن وجدت)
  - **الإعدادات**: config\settings.py
  - **الوحدات**: modules\ (accounting, projects, clients, employees, suppliers, contracts, training, expenses, revenues, reports)
  - **السجلات**: logs\main.log
  - **الاختبارات**: tests\ و test_basic.py و test_modules.py
  - **التشغيل**: run_system.py / run_test.py

## طريقة التشغيل السريعة
- تشغيل النظام:
  ```powershell
  python "d:\ProjectManager\desktopV2\منظومة_المهندس_v3\main.py" --mode run
  ```
- معلومات فقط:
  ```powershell
  python "d:\ProjectManager\desktopV2\منظومة_المهندس_v3\main.py" --mode info
  ```
- الاختبارات:
  ```powershell
  python "d:\ProjectManager\desktopV2\منظومة_المهندس_v3\main.py" --mode test
  ```

## الملاحظات التصميمية (واجهة المستخدم)
- v3 حالياً بلا واجهة رسومية جاهزة؛ يتم التحضير لإطار واجهة يشابه v2 مع دعم:
  - شريط جانبي للوحدات
  - مساحة عمل مركزية
  - تخصيص عرض الوحدات عبر إعدادات محفوظة (JSON/DB)

## سجلات وتخصيص
- **سجل عام**: d:\\ProjectManager\\desktopV2\\accounting_system.log
- **ملفات تخصيص**: Customize.json وغيرها في الجذر

## إرشادات للمساعد
- استعمل المسار المطلق دائماً من d:\\ProjectManager\\desktopV2
- لا تُغيّر ملفات الإنتاج إلا بطلب المستخدم
- عند إنشاء/تعديل ملفات، قدّم ملخصاً واضحاً للتغييرات وأسبابها