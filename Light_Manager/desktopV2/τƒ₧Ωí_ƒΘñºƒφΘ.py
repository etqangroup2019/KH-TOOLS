#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نظام قائمة السياق للجداول
يوفر قائمة سياق موحدة لجميع الجداول في النظام
"""

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# قائمة سياق جدول الإعداد
def setup_table_context_menu(table, main_window, section_name, is_main_table=True):
    """
    إعداد قائمة السياق للجدول
    
    Args:
        table: الجدول المراد إضافة قائمة السياق له
        main_window: النافذة الرئيسية
        section_name: اسم القسم
        is_main_table: هل هو جدول رئيسي أم فرعي (الجداول الفرعية لا تحتوي على خيار عرض)
    """
    # تعيين سياسة قائمة السياق
    table.setContextMenuPolicy(Qt.CustomContextMenu)
    
    # ربط الإشارة بدالة عرض قائمة السياق
    table.customContextMenuRequested.connect(
        lambda position: show_table_context_menu(table, main_window, section_name, position, is_main_table)
    )

# عرض قائمة سياق الجدول
def show_table_context_menu(table, main_window, section_name, position, is_main_table=True):
    """
    عرض قائمة السياق للجدول
    
    Args:
        table: الجدول
        main_window: النافذة الرئيسية
        section_name: اسم القسم
        position: موضع النقر
        is_main_table: هل هو جدول رئيسي أم فرعي
    """
    # التحقق من وجود صف محدد
    current_row = table.currentRow()
    if current_row < 0:
        return
    
    # إنشاء قائمة السياق
    context_menu = QMenu(table)
    
    # إضافة الخيارات حسب نوع الجدول
    if is_main_table:
        # للجداول الرئيسية: عرض، تعديل، حذف
        view_action = QAction("👁️ عرض", table)
        view_action.triggered.connect(lambda: handle_table_view_action(table, main_window, section_name))
        context_menu.addAction(view_action)
        
        edit_action = QAction("✏️ تعديل", table)
        edit_action.triggered.connect(lambda: handle_table_edit_action(table, main_window, section_name))
        context_menu.addAction(edit_action)
        
        delete_action = QAction("🗑️ حذف", table)
        delete_action.triggered.connect(lambda: handle_table_delete_action(table, main_window, section_name))
        context_menu.addAction(delete_action)
    else:
        # للجداول الفرعية: تعديل، حذف فقط
        edit_action = QAction("✏️ تعديل", table)
        edit_action.triggered.connect(lambda: handle_table_edit_action(table, main_window, section_name))
        context_menu.addAction(edit_action)
        
        delete_action = QAction("🗑️ حذف", table)
        delete_action.triggered.connect(lambda: handle_table_delete_action(table, main_window, section_name))
        context_menu.addAction(delete_action)
    
    # عرض القائمة في الموضع المحدد
    context_menu.exec(table.mapToGlobal(position))

# معالجة إجراء العرض
def handle_table_view_action(table, main_window, section_name):
    try:
        current_row = table.currentRow()
        if current_row < 0:
            return
        
        # الحصول على البيانات من الصف المحدد
        row_data = get_row_data(table, current_row)
        
        # استدعاء دالة العرض المناسبة حسب القسم
        if section_name == "المشاريع" or section_name == "المقاولات":
            handle_project_view(main_window, row_data, section_name)
        elif section_name == "العملاء":
            handle_client_view(main_window, row_data)
        elif section_name == "الموظفين":
            handle_employee_view(main_window, row_data)
        elif section_name == "الحسابات":
            handle_expense_view(main_window, row_data)
        elif section_name == "التدريب":
            handle_training_view(main_window, row_data)
        elif section_name == "الموردين":
            handle_supplier_view(main_window, row_data)
        else:
            QMessageBox.information(table, "عرض", f"عرض تفاصيل {section_name}")
            
    except Exception as e:
        QMessageBox.warning(table, "خطأ", f"فشل في عرض التفاصيل: {str(e)}")

# معالجة إجراء التعديل
def handle_table_edit_action(table, main_window, section_name):
    try:
        current_row = table.currentRow()
        if current_row < 0:
            return
        
        # استخدام دالة التعديل الموجودة في النظام
        if hasattr(main_window, 'handle_table_double_click'):
            # محاكاة النقر المزدوج لفتح نافذة التعديل
            item = table.item(current_row, 0)
            if item:
                main_window.handle_table_double_click(item)
        else:
            QMessageBox.information(table, "تعديل", f"تعديل عنصر من {section_name}")
            
    except Exception as e:
        QMessageBox.warning(table, "خطأ", f"فشل في التعديل: {str(e)}")

# معالجة إجراء الحذف
def handle_table_delete_action(table, main_window, section_name):
    try:
        current_row = table.currentRow()
        if current_row < 0:
            return
        
        # الحصول على البيانات من الصف المحدد
        row_data = get_row_data(table, current_row)
        
        # تحديد نوع العنصر للرسالة
        item_type = get_item_type_name(section_name)
        item_name = get_item_display_name(row_data, section_name)
        
        # رسالة التأكيد
        reply = QMessageBox.question(
            table,
            "تأكيد الحذف",
            f"هل أنت متأكد من حذف {item_type}:\n{item_name}؟\n\nهذا الإجراء لا يمكن التراجع عنه.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # تنفيذ الحذف
            perform_delete_action(table, main_window, section_name, row_data, current_row)
            
    except Exception as e:
        QMessageBox.warning(table, "خطأ", f"فشل في الحذف: {str(e)}")

# الحصول على بيانات الصف
def get_row_data(table, row_index):
    row_data = {}
    for col in range(table.columnCount()):
        header_item = table.horizontalHeaderItem(col)
        if header_item:
            header_text = header_item.text().strip()
            item = table.item(row_index, col)
            if item:
                row_data[header_text] = item.data(Qt.UserRole) if item.data(Qt.UserRole) is not None else item.text()
    return row_data

# الحصول على اسم نوع العنصر
def get_item_type_name(section_name):
    type_names = {
        "المشاريع": "المشروع",
        "المقاولات": "المقاولات", 
        "العملاء": "العميل",
        "الموظفين": "الموظف",
        "الحسابات": "الحساب",
        "التدريب": "الدورة التدريبية",
        "الموردين": "المورد"
    }
    return type_names.get(section_name, "العنصر")

# الحصول على اسم العنصر للعرض
def get_item_display_name(row_data, section_name):
    if section_name == "المشاريع" or section_name == "المقاولات":
        return row_data.get("اسم المشروع", row_data.get("           اسم المشروع          ", "غير محدد"))
    elif section_name == "العملاء":
        return row_data.get("اسم العميل", row_data.get("          اسم العميل          ", "غير محدد"))
    elif section_name == "الموظفين":
        return row_data.get("اسم الموظف", row_data.get("          اسم الموظف          ", "غير محدد"))
    elif section_name == "الحسابات":
        return row_data.get("البيان", row_data.get("          البيان          ", "غير محدد"))
    elif section_name == "التدريب":
        return row_data.get("اسم الدورة", row_data.get("          اسم الدورة          ", "غير محدد"))
    elif section_name == "الموردين":
        return row_data.get("اسم المورد", row_data.get("          اسم المورد          ", "غير محدد"))
    else:
        return "غير محدد"

# تنفيذ عملية الحذف
def perform_delete_action(table, main_window, section_name, row_data, row_index):
    try:
        # الحصول على ID العنصر
        item_id = row_data.get("id")
        if not item_id:
            QMessageBox.warning(table, "خطأ", "لا يمكن تحديد معرف العنصر")
            return
        
        # استخدام دالة الحذف الموجودة في النظام إذا كانت متوفرة
        if hasattr(main_window, 'delete_entry'):
            main_window.delete_entry(section_name, item_id)
            # تحديث الجدول
            if hasattr(main_window, 'show_section'):
                main_window.show_section(section_name)
        else:
            # حذف الصف من الجدول مؤقتاً
            table.removeRow(row_index)
            QMessageBox.information(table, "تم الحذف", "تم حذف العنصر بنجاح")
            
    except Exception as e:
        QMessageBox.warning(table, "خطأ", f"فشل في حذف العنصر: {str(e)}")

# دوال العرض المخصصة لكل قسم
# عرض تفاصيل المشروع
def handle_project_view(main_window, row_data, section_name):
    try:
        #from إدارة_المشروع import open_project_phases_window
        from المشاريع.إدارة_المشروع import open_project_phases_window
        project_type = "المشاريع" if section_name == "المشاريع" else "المقاولات"
        open_project_phases_window(main_window, row_data, project_type)
    except Exception as e:
        QMessageBox.information(main_window, "عرض المشروع", f"عرض تفاصيل المشروع: {row_data.get('اسم المشروع', 'غير محدد')}")

# عرض تفاصيل العميل
def handle_client_view(main_window, row_data):
    QMessageBox.information(main_window, "عرض العميل", f"عرض تفاصيل العميل: {row_data.get('اسم العميل', 'غير محدد')}")

# عرض تفاصيل الموظف
def handle_employee_view(main_window, row_data):
    QMessageBox.information(main_window, "عرض الموظف", f"عرض تفاصيل الموظف: {row_data.get('اسم الموظف', 'غير محدد')}")

# عرض تفاصيل الحساب
def handle_expense_view(main_window, row_data):
    QMessageBox.information(main_window, "عرض الحساب", f"عرض تفاصيل الحساب: {row_data.get('البيان', 'غير محدد')}")


# عرض تفاصيل الدورة التدريبية
def handle_training_view(main_window, row_data):
    QMessageBox.information(main_window, "عرض الدورة", f"عرض تفاصيل الدورة: {row_data.get('اسم الدورة', 'غير محدد')}")

# عرض تفاصيل المورد
def handle_supplier_view(main_window, row_data):
    QMessageBox.information(main_window, "عرض المورد", f"عرض تفاصيل المورد: {row_data.get('اسم المورد', 'غير محدد')}")
