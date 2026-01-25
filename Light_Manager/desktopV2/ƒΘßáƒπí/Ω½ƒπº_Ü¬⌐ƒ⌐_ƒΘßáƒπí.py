#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مساعد إضافة أزرار الطباعة للنوافذ الإدارية
يوفر دوال مساعدة لإضافة أزرار الطباعة بشكل موحد لجميع النوافذ
"""

import sys
import os
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import qtawesome as qta

# إضافة المسار الحالي
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from الطباعة_والتصدير import print_manager


# إضافة زر طباعة للتخطيط
def add_print_button_to_layout(layout, parent_window, tab_widget=None, position="end"):
    """
    إضافة زر الطباعة إلى تخطيط معين
    
    Args:
        layout: التخطيط المراد إضافة الزر إليه
        parent_window: النافذة الأب
        tab_widget: ويدجت التابات (اختياري)
        position: موضع الزر ("start", "end", "after_actions")
    """
    try:
        # إنشاء زر الطباعة
        print_btn = QPushButton("طباعة")
        print_btn.setObjectName("print_button")
        print_btn.setIcon(qta.icon('fa5s.print', color='white'))
        print_btn.setToolTip("طباعة وتصدير البيانات")
        
        # ربط الزر بوظيفة الطباعة
        # على طباعة النقر
        def on_print_clicked():
            current_tab_index = None
            if tab_widget:
                current_tab_index = tab_widget.currentIndex()
            print_manager.open_print_dialog(parent_window, tab_widget, current_tab_index)
        
        print_btn.clicked.connect(on_print_clicked)
        
        # إضافة الزر حسب الموضع المحدد
        if isinstance(layout, QHBoxLayout):
            if position == "start":
                layout.insertWidget(0, print_btn)
            elif position == "after_actions":
                # البحث عن آخر زر إجراء وإضافة الزر بعده
                action_buttons_count = 0
                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    if item and isinstance(item.widget(), QPushButton):
                        widget = item.widget()
                        if (hasattr(widget, 'objectName') and 
                            any(name in widget.objectName() for name in ['add', 'edit', 'delete', 'إضافة', 'تعديل', 'حذف'])):
                            action_buttons_count = i + 1
                
                layout.insertWidget(action_buttons_count, print_btn)
            else:  # end
                layout.addWidget(print_btn)
        else:
            layout.addWidget(print_btn)
        
        return print_btn
        
    except Exception as e:
        print(f"خطأ في إضافة زر الطباعة: {e}")
        return None


# أضف أزرار طباعة إلى أداة علامة التبويب
def add_print_buttons_to_tab_widget(tab_widget, parent_window):
    """
    إضافة أزرار الطباعة لجميع التابات في ويدجت التابات
    
    Args:
        tab_widget: ويدجت التابات
        parent_window: النافذة الأب
    """
    try:
        for tab_index in range(tab_widget.count()):
            tab = tab_widget.widget(tab_index)
            add_print_button_to_tab(tab, parent_window, tab_widget, tab_index)
            
    except Exception as e:
        print(f"خطأ في إضافة أزرار الطباعة للتابات: {e}")


# إضافة زر طباعة إلى علامة التبويب
def add_print_button_to_tab(tab_widget, parent_window, tab_container=None, tab_index=None):
    """
    إضافة زر الطباعة لتاب واحد
    
    Args:
        tab_widget: ويدجت التاب
        parent_window: النافذة الأب
        tab_container: حاوية التابات
        tab_index: فهرس التاب
    """
    try:
        # البحث عن التخطيط الأول في التاب
        main_layout = tab_widget.layout()
        if not main_layout:
            return None
        
        # البحث عن تخطيط الأزرار (عادة يكون QHBoxLayout في الأعلى)
        buttons_layout = find_buttons_layout(main_layout)
        
        if buttons_layout:
            # إضافة زر الطباعة
            print_btn = add_print_button_to_layout(
                buttons_layout, 
                parent_window, 
                tab_container, 
                "after_actions"
            )
            return print_btn
        else:
            # إنشاء تخطيط جديد للأزرار إذا لم يوجد
            new_buttons_layout = QHBoxLayout()
            print_btn = add_print_button_to_layout(
                new_buttons_layout, 
                parent_window, 
                tab_container
            )
            
            # إضافة التخطيط الجديد في أعلى التاب
            main_layout.insertLayout(0, new_buttons_layout)
            return print_btn
            
    except Exception as e:
        print(f"خطأ في إضافة زر الطباعة للتاب: {e}")
        return None


# العثور على تخطيط الأزرار
def find_buttons_layout(layout):
    """
    البحث عن تخطيط الأزرار في التخطيط الرئيسي
    
    Args:
        layout: التخطيط المراد البحث فيه
        
    Returns:
        QHBoxLayout: تخطيط الأزرار أو None
    """
    try:
        # البحث في العناصر المباشرة
        for i in range(layout.count()):
            item = layout.itemAt(i)
            
            if item:
                # إذا كان العنصر تخطيط أفقي
                if isinstance(item, QHBoxLayout) or (hasattr(item, 'layout') and isinstance(item.layout(), QHBoxLayout)):
                    sub_layout = item if isinstance(item, QHBoxLayout) else item.layout()
                    
                    # التحقق من وجود أزرار في هذا التخطيط
                    button_count = 0
                    for j in range(sub_layout.count()):
                        sub_item = sub_layout.itemAt(j)
                        if sub_item and isinstance(sub_item.widget(), QPushButton):
                            button_count += 1
                    
                    # إذا وجد أزرار، فهذا على الأرجح تخطيط الأزرار
                    if button_count > 0:
                        return sub_layout
                
                # البحث المتداخل في التخطيطات الفرعية
                elif hasattr(item, 'layout') and item.layout():
                    result = find_buttons_layout(item.layout())
                    if result:
                        return result
        
        return None
        
    except Exception as e:
        print(f"خطأ في البحث عن تخطيط الأزرار: {e}")
        return None


# تطبيق نمط زر الطباعة
def apply_print_button_style(button):
    """
    تطبيق ستايل زر الطباعة
    
    Args:
        button: زر الطباعة
    """
    try:
        # تطبيق الستايل البرتقالي للطباعة
        button.setStyleSheet("""
            QPushButton#print_button {
                background-color: #e67e22;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
                min-width: 80px;
            }
            QPushButton#print_button:hover {
                background-color: #d35400;
            }
            QPushButton#print_button:pressed {
                background-color: #c0392b;
            }
            QPushButton#print_button:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        
    except Exception as e:
        print(f"خطأ في تطبيق ستايل زر الطباعة: {e}")


# تلقائي إضافة أزرار طباعة إلى النافذة
def auto_add_print_buttons_to_window(window):
    """
    إضافة أزرار الطباعة تلقائياً لنافذة إدارية
    
    Args:
        window: النافذة الإدارية
    """
    try:
        # البحث عن ويدجت التابات في النافذة
        tab_widgets = window.findChildren(QTabWidget)
        
        for tab_widget in tab_widgets:
            add_print_buttons_to_tab_widget(tab_widget, window)
        
        # تطبيق الأنماط على جميع أزرار الطباعة
        print_buttons = window.findChildren(QPushButton)
        for button in print_buttons:
            if hasattr(button, 'objectName') and button.objectName() == 'print_button':
                apply_print_button_style(button)
                
    except Exception as e:
        print(f"خطأ في الإضافة التلقائية لأزرار الطباعة: {e}")


# أضف أزرار طباعة مخصصة
def add_custom_print_buttons(parent_window, tab_widget):
    """
    إضافة أزرار الطباعة بطريقة مخصصة حسب نوع التاب
    
    Args:
        parent_window: النافذة الأب
        tab_widget: ويدجت التابات
    """
    try:
        for tab_index in range(tab_widget.count()):
            tab = tab_widget.widget(tab_index)
            tab_text = tab_widget.tabText(tab_index)
            
            # تحديد موقع زر الطباعة حسب نوع التاب
            if ("معلومات" in tab_text or 
                "المشروع" in tab_text and tab_index == 0 or
                "العميل" in tab_text and tab_index == 0 or
                "الموظف" in tab_text and tab_index == 0 or
                "الدورة" in tab_text and tab_index == 0):
                # للتاب الأول (المعلومات)، ضع زر الطباعة في الأسفل
                add_print_button_to_bottom(tab, parent_window, tab_widget, tab_index)
            else:
                # للتابات الأخرى، ضع زر الطباعة مع الأزرار الأخرى
                add_print_button_to_actions_row(tab, parent_window, tab_widget, tab_index)
                
    except Exception as e:
        print(f"خطأ في إضافة أزرار الطباعة المخصصة: {e}")


# إضافة زر طباعة إلى أسفل
def add_print_button_to_bottom(tab_widget, parent_window, tab_container, tab_index):
    """
    إضافة زر الطباعة في أسفل التاب
    
    Args:
        tab_widget: ويدجت التاب
        parent_window: النافذة الأب
        tab_container: حاوية التابات
        tab_index: فهرس التاب
    """
    try:
        main_layout = tab_widget.layout()
        if not main_layout:
            return None
        
        # التحقق من وجود زر طباعة مسبقاً
        existing_btn = check_existing_print_button(tab_widget)
        if existing_btn:
            return existing_btn
        
        # إنشاء تخطيط أفقي لزر الطباعة
        print_layout = QHBoxLayout()
        print_layout.setContentsMargins(20, 10, 20, 20)
        
        # إضافة مساحة فارغة على اليسار
        print_layout.addStretch()
        
        # إنشاء زر الطباعة
        print_btn = QPushButton("طباعة")
        print_btn.setObjectName("print_button")
        print_btn.setIcon(qta.icon('fa5s.print', color='white'))
        print_btn.setToolTip("طباعة وتصدير البيانات")
        print_btn.setMinimumHeight(35)
        print_btn.setMinimumWidth(120)
        
        # ربط الزر بوظيفة الطباعة
        # على طباعة النقر
        def on_print_clicked():
            print_manager.open_print_dialog(parent_window, tab_container, tab_index)
        
        print_btn.clicked.connect(on_print_clicked)
        
        # تطبيق الستايل
        apply_print_button_style(print_btn)
        
        print_layout.addWidget(print_btn)
        
        # إضافة مساحة فارغة على اليمين
        print_layout.addStretch()
        
        # إضافة التخطيط في أسفل التاب
        main_layout.addLayout(print_layout)
        
        return print_btn
        
    except Exception as e:
        print(f"خطأ في إضافة زر الطباعة في الأسفل: {e}")
        return None


# تحقق من زر الطباعة الحالي
def check_existing_print_button(tab_widget):
    """
    التحقق من وجود زر طباعة مسبقاً في التاب
    
    Args:
        tab_widget: ويدجت التاب
        
    Returns:
        QPushButton أو None: زر الطباعة الموجود أو None
    """
    try:
        existing_print_buttons = tab_widget.findChildren(QPushButton)
        for btn in existing_print_buttons:
            if hasattr(btn, 'objectName') and btn.objectName() == 'print_button':
                return btn
        return None
    except Exception as e:
        print(f"خطأ في التحقق من زر الطباعة الموجود: {e}")
        return None


# إضافة زر طباعة إلى صف الإجراءات
def add_print_button_to_actions_row(tab_widget, parent_window, tab_container, tab_index):
    """
    إضافة زر الطباعة مع صف الأزرار والفلاتر
    
    Args:
        tab_widget: ويدجت التاب
        parent_window: النافذة الأب
        tab_container: حاوية التابات
        tab_index: فهرس التاب
    """
    try:
        # التحقق من وجود زر طباعة مسبقاً
        existing_btn = check_existing_print_button(tab_widget)
        if existing_btn:
            return existing_btn
        
        main_layout = tab_widget.layout()
        if not main_layout:
            return None
        
        # البحث عن التخطيط الأول (الذي يحتوي على الأزرار والفلاتر)
        first_layout = None
        for i in range(main_layout.count()):
            item = main_layout.itemAt(i)
            if item and hasattr(item, 'layout') and item.layout():
                layout = item.layout()
                if isinstance(layout, QHBoxLayout):
                    first_layout = layout
                    break
        
        if not first_layout:
            return None
        
        # البحث عن تخطيط الأزرار (أول تخطيط فرعي يحتوي على أزرار)
        actions_layout = None
        
        # أولاً: البحث في التخطيطات الفرعية
        for i in range(first_layout.count()):
            item = first_layout.itemAt(i)
            if item and hasattr(item, 'layout') and item.layout():
                sub_layout = item.layout()
                if isinstance(sub_layout, QHBoxLayout):
                    # التحقق من وجود أزرار في هذا التخطيط
                    button_count = 0
                    for j in range(sub_layout.count()):
                        sub_item = sub_layout.itemAt(j)
                        if sub_item and isinstance(sub_item.widget(), QPushButton):
                            button_count += 1
                    
                    if button_count > 0:
                        actions_layout = sub_layout
                        break
        
        # ثانياً: إذا لم نجد تخطيط فرعي، ابحث في التخطيط الرئيسي نفسه
        if not actions_layout:
            button_count = 0
            for i in range(first_layout.count()):
                item = first_layout.itemAt(i)
                if item and isinstance(item.widget(), QPushButton):
                    button_count += 1
            
            if button_count > 0:
                actions_layout = first_layout
        
        if not actions_layout:
            return None
        
        # إنشاء زر الطباعة
        print_btn = QPushButton("طباعة")
        print_btn.setObjectName("print_button")
        print_btn.setIcon(qta.icon('fa5s.print', color='white'))
        print_btn.setToolTip("طباعة وتصدير البيانات")
        
        # ربط الزر بوظيفة الطباعة
        # على طباعة النقر
        def on_print_clicked():
            print_manager.open_print_dialog(parent_window, tab_container, tab_index)
        
        print_btn.clicked.connect(on_print_clicked)
        
        # تطبيق الستايل
        apply_print_button_style(print_btn)
        
        # إضافة الزر في نهاية تخطيط الأزرار
        actions_layout.addWidget(print_btn)
        
        return print_btn
        
    except Exception as e:
        print(f"خطأ في إضافة زر الطباعة لصف الأزرار: {e}")
        return None


# دالة مساعدة للاستخدام السريع
# إضافة زر الطباعة السريع
def quick_add_print_button(parent_window, tab_widget=None):
    """
    إضافة سريعة لزر الطباعة
    
    Args:
        parent_window: النافذة الأب
        tab_widget: ويدجت التابات (اختياري)
        
    Returns:
        QPushButton: زر الطباعة المضاف
    """
    try:
        if tab_widget:
            add_custom_print_buttons(parent_window, tab_widget)
        else:
            auto_add_print_buttons_to_window(parent_window)
            
    except Exception as e:
        print(f"خطأ في الإضافة السريعة لزر الطباعة: {e}")
        return None
