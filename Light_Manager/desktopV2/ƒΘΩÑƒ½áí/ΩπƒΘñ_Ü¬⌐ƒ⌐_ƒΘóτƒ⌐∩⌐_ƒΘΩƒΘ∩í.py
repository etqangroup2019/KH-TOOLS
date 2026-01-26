#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
معالج الأزرار المخصصة لقسم التقارير المالية
يحتوي على جميع وظائف الأزرار المالية
"""

import sys
import os
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# إضافة المسار الحالي
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)


# معالج الأزرار المخصصة لقسم التقارير المالية
def handle_financial_custom_action(main_window, action_name, section_name):
    try:
        # استخدام النظام المحاسبي المحسن الجديد لجميع الإجراءات
        if action_name in ["شجرة_الحسابات", "القيود_المحاسبية", "ربط_المعاملات",
                          "قائمة_الدخل", "الميزانية_العمومية", "التدفقات_النقدية", "إعدادات_النظام"]:
            open_unified_accounting_system_enhanced(main_window, action_name)

        elif action_name == "التقارير_المالية":
            open_financial_reports_menu(main_window)

        elif action_name == "طباعة":
            open_print_reports(main_window)

        else:
            QMessageBox.information(main_window, "معلومات", f"الإجراء '{action_name}' قيد التطوير")

    except Exception as e:
        QMessageBox.critical(main_window, "خطأ", f"فشل في تنفيذ الإجراء '{action_name}':\n{str(e)}")


# فتح النظام المحاسبي المحسن مع التبويب المناسب
def open_unified_accounting_system_enhanced(main_window, action_name):
    try:
        # استخدام النظام المحاسبي المحسن الجديد
        from النظام_المحاسبي_المحسن import open_unified_accounting_window

        # فتح النافذة أو إحضارها إذا كانت مفتوحة
        if not hasattr(main_window, 'enhanced_accounting_window') or main_window.enhanced_accounting_window is None:
            main_window.enhanced_accounting_window = open_unified_accounting_window(main_window)

        if main_window.enhanced_accounting_window:
            # إظهار النافذة وإحضارها للمقدمة
            main_window.enhanced_accounting_window.show()
            main_window.enhanced_accounting_window.raise_()
            main_window.enhanced_accounting_window.activateWindow()

            # التنقل إلى التبويب المناسب
            tab_mapping = {
                "شجرة_الحسابات": 1,      # تبويب شجرة الحسابات
                "القيود_المحاسبية": 2,     # تبويب القيود المحاسبية
                "ربط_المعاملات": 3,        # تبويب الربط التلقائي
                "قائمة_الدخل": 4,          # تبويب التقارير المالية
                "الميزانية_العمومية": 4,   # تبويب التقارير المالية
                "التدفقات_النقدية": 4,     # تبويب التقارير المالية
                "إعدادات_النظام": 5        # تبويب إعدادات النظام
            }

            if action_name in tab_mapping:
                main_window.enhanced_accounting_window.tab_widget.setCurrentIndex(tab_mapping[action_name])

                # إذا كان التبويب هو التقارير المالية، قم بتشغيل التقرير المناسب
                if action_name == "قائمة_الدخل":
                    main_window.enhanced_accounting_window.generate_income_statement()
                elif action_name == "الميزانية_العمومية":
                    main_window.enhanced_accounting_window.generate_balance_sheet()
                elif action_name == "التدفقات_النقدية":
                    main_window.enhanced_accounting_window.generate_cash_flow()

    except Exception as e:
        # في حالة فشل النظام المحسن، استخدم النظام القديم كخيار احتياطي
        QMessageBox.warning(main_window, "تحذير", 
                           f"فشل في فتح النظام المحاسبي المحسن: {str(e)}\n"
                           "سيتم استخدام النظام القديم كخيار احتياطي.")
        open_unified_accounting_system_fallback(main_window, action_name)


# فتح النظام المحاسبي القديم كخيار احتياطي
def open_unified_accounting_system_fallback(main_window, action_name):
    try:
        from إدارة_المحاسبة import open_accounting_management_window

        # فتح النافذة أو إحضارها إذا كانت مفتوحة
        if not hasattr(main_window, 'accounting_window') or main_window.accounting_window is None:
            main_window.accounting_window = open_accounting_management_window(main_window)

        if main_window.accounting_window:
            # إظهار النافذة وإحضارها للمقدمة
            main_window.accounting_window.show()
            main_window.accounting_window.raise_()
            main_window.accounting_window.activateWindow()

            # التنقل إلى التبويب المناسب
            tab_mapping = {
                "شجرة_الحسابات": 0,      # تبويب شجرة الحسابات
                "القيود_المحاسبية": 1,     # تبويب القيود المحاسبية
                "ربط_المعاملات": 3,        # تبويب ربط المعاملات
                "قائمة_الدخل": 4,          # تبويب التقارير المالية
                "الميزانية_العمومية": 4,   # تبويب التقارير المالية
                "التدفقات_النقدية": 4,     # تبويب التقارير المالية
                "إعدادات_النظام": 7        # تبويب إعدادات النظام
            }

            if action_name in tab_mapping:
                main_window.accounting_window.tab_widget.setCurrentIndex(tab_mapping[action_name])

    except Exception as e:
        QMessageBox.critical(main_window, "خطأ", f"فشل في فتح النظام المحاسبي: {str(e)}")


# فتح النظام المحاسبي المتكامل مع التبويب المناسب - الدالة القديمة للتوافق
def open_unified_accounting_system(main_window, action_name):
    # إعادة توجيه إلى النظام الجديد
    open_unified_accounting_system_enhanced(main_window, action_name)


# فتح نافذة شجرة الحسابات - استخدام النظام المتكامل
def open_chart_of_accounts(main_window):
    open_unified_accounting_system(main_window, "شجرة_الحسابات")


# فتح نافذة القيود المحاسبية - استخدام النظام المتكامل
def open_journal_entries(main_window):
    open_unified_accounting_system(main_window, "القيود_المحاسبية")


# فتح نافذة ربط المعاملات - استخدام النظام المتكامل
def open_transaction_linking(main_window):
    open_unified_accounting_system(main_window, "ربط_المعاملات")


# فتح قائمة التقارير المالية
def open_financial_reports_menu(main_window):
    try:
        # إنشاء قائمة منبثقة للتقارير المالية
        menu = QMenu("التقارير المالية", main_window)
        menu.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # إضافة عناصر القائمة
        income_action = menu.addAction("📊 قائمة الدخل")
        income_action.triggered.connect(lambda: open_income_statement(main_window))
        
        balance_action = menu.addAction("📋 الميزانية العمومية")
        balance_action.triggered.connect(lambda: open_balance_sheet(main_window))
        
        cash_flow_action = menu.addAction("💰 التدفقات النقدية")
        cash_flow_action.triggered.connect(lambda: open_cash_flow_statement(main_window))
        
        menu.addSeparator()
        
        trial_balance_action = menu.addAction("⚖️ ميزان المراجعة")
        trial_balance_action.triggered.connect(lambda: open_trial_balance(main_window))
        
        ledger_action = menu.addAction("📖 دفتر الأستاذ")
        ledger_action.triggered.connect(lambda: open_general_ledger(main_window))
        
        # عرض القائمة
        menu.exec_(QCursor.pos())
        
    except Exception as e:
        QMessageBox.critical(main_window, "خطأ", f"فشل في فتح قائمة التقارير المالية:\n{str(e)}")


# فتح قائمة الدخل - استخدام النظام المتكامل
def open_income_statement(main_window):
    open_unified_accounting_system(main_window, "قائمة_الدخل")


# فتح الميزانية العمومية - استخدام النظام المتكامل
def open_balance_sheet(main_window):
    open_unified_accounting_system(main_window, "الميزانية_العمومية")


# فتح قائمة التدفقات النقدية - استخدام النظام المتكامل
def open_cash_flow_statement(main_window):
    open_unified_accounting_system(main_window, "التدفقات_النقدية")


# فتح ميزان المراجعة
def open_trial_balance(main_window):
    try:
        QMessageBox.information(main_window, "معلومات", "ميزان المراجعة قيد التطوير")
        
    except Exception as e:
        QMessageBox.critical(main_window, "خطأ", f"فشل في فتح ميزان المراجعة:\n{str(e)}")


# فتح دفتر الأستاذ
def open_general_ledger(main_window):
    try:
        QMessageBox.information(main_window, "معلومات", "دفتر الأستاذ قيد التطوير")
        
    except Exception as e:
        QMessageBox.critical(main_window, "خطأ", f"فشل في فتح دفتر الأستاذ:\n{str(e)}")


# فتح إعدادات النظام المحاسبي - استخدام النظام المتكامل
def open_accounting_settings(main_window):
    open_unified_accounting_system(main_window, "إعدادات_النظام")


# فتح نافذة طباعة التقارير
def open_print_reports(main_window):
    try:
        # إنشاء قائمة منبثقة لخيارات الطباعة
        menu = QMenu("طباعة التقارير", main_window)
        menu.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # إضافة خيارات الطباعة
        print_summary_action = menu.addAction("🖨️ طباعة الملخص المالي")
        print_summary_action.triggered.connect(lambda: print_financial_summary(main_window))
        
        print_income_action = menu.addAction("🖨️ طباعة قائمة الدخل")
        print_income_action.triggered.connect(lambda: print_income_statement(main_window))
        
        print_balance_action = menu.addAction("🖨️ طباعة الميزانية العمومية")
        print_balance_action.triggered.connect(lambda: print_balance_sheet(main_window))
        
        print_cash_flow_action = menu.addAction("🖨️ طباعة التدفقات النقدية")
        print_cash_flow_action.triggered.connect(lambda: print_cash_flow(main_window))
        
        menu.addSeparator()
        
        export_excel_action = menu.addAction("📊 تصدير إلى Excel")
        export_excel_action.triggered.connect(lambda: export_to_excel(main_window))
        
        export_pdf_action = menu.addAction("📄 تصدير إلى PDF")
        export_pdf_action.triggered.connect(lambda: export_to_pdf(main_window))
        
        # عرض القائمة
        menu.exec_(QCursor.pos())
        
    except Exception as e:
        QMessageBox.critical(main_window, "خطأ", f"فشل في فتح خيارات الطباعة:\n{str(e)}")


# طباعة الملخص المالي
def print_financial_summary(main_window):
    try:
        QMessageBox.information(main_window, "معلومات", "طباعة الملخص المالي قيد التطوير")
        
    except Exception as e:
        QMessageBox.critical(main_window, "خطأ", f"فشل في طباعة الملخص المالي:\n{str(e)}")


# طباعة قائمة الدخل
def print_income_statement(main_window):
    try:
        QMessageBox.information(main_window, "معلومات", "طباعة قائمة الدخل قيد التطوير")
        
    except Exception as e:
        QMessageBox.critical(main_window, "خطأ", f"فشل في طباعة قائمة الدخل:\n{str(e)}")


# طباعة الميزانية العمومية
def print_balance_sheet(main_window):
    try:
        QMessageBox.information(main_window, "معلومات", "طباعة الميزانية العمومية قيد التطوير")
        
    except Exception as e:
        QMessageBox.critical(main_window, "خطأ", f"فشل في طباعة الميزانية العمومية:\n{str(e)}")


# طباعة التدفقات النقدية
def print_cash_flow(main_window):
    try:
        QMessageBox.information(main_window, "معلومات", "طباعة التدفقات النقدية قيد التطوير")
        
    except Exception as e:
        QMessageBox.critical(main_window, "خطأ", f"فشل في طباعة التدفقات النقدية:\n{str(e)}")


# تصدير إلى Excel
def export_to_excel(main_window):
    try:
        QMessageBox.information(main_window, "معلومات", "تصدير إلى Excel قيد التطوير")
        
    except Exception as e:
        QMessageBox.critical(main_window, "خطأ", f"فشل في التصدير إلى Excel:\n{str(e)}")


# تصدير إلى PDF
def export_to_pdf(main_window):
    try:
        QMessageBox.information(main_window, "معلومات", "تصدير إلى PDF قيد التطوير")
        
    except Exception as e:
        QMessageBox.critical(main_window, "خطأ", f"فشل في التصدير إلى PDF:\n{str(e)}")


# تحديث البيانات المالية في المنطقة الرئيسية
def refresh_financial_data(main_window):
    try:
        # البحث عن قسم التقارير في الأقسام المحفوظة
        if hasattr(main_window, 'sections') and "التقارير" in main_window.sections:
            section_info = main_window.sections["التقارير"]
            
            # تحديث الإحصائيات
            if "stats" in section_info:
                from محتوى_التقارير_المالية import get_financial_stats_data
                stats_data = get_financial_stats_data()
                
                for i, (title, value, color, icon) in enumerate(stats_data):
                    if i < len(section_info["stats"]):
                        stat_name = list(section_info["stats"].keys())[i]
                        section_info["stats"][stat_name].update_value(value)
            
            # تحديث الجدول إذا كان موجوداً
            if "table" in section_info:
                # إعادة تحميل البيانات
                main_window._load_data_from_db(section_info["table"], "التقارير")
        
    except Exception as e:
        print(f"خطأ في تحديث البيانات المالية: {e}")
