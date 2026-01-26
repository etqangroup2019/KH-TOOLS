#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نافذة إدارة العملاء الشاملة
تحتوي على جميع الوظائف المطلوبة لإدارة العملاء بشكل كامل
"""

import sys
import os
from datetime import datetime, date, timedelta
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTabWidget, QWidget, QFrame, QLabel, QPushButton, QLineEdit,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox,
    QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QBrush, QColor, QFont
import mysql.connector
import qtawesome as qta

# إضافة المسار الحالي
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from الإعدادات_العامة import *
from ستايل import apply_stylesheet
from قائمة_الجداول import setup_table_context_menu
from متغيرات import *
from مساعد_أزرار_الطباعة import quick_add_print_button
from نظام_البطاقات import ModernCard, ModernCardsContainer
from أزرار_الواجهة import table_setting
from ستايل_نوافذ_الإدارة import (
    apply_management_style, apply_to_client_management,
    setup_table_style, create_stat_card, get_status_color,
    format_currency, format_date
)
from المشاريع.إدارة_المشروع import*

# إعدادات قاعدة البيانات
db_config = {
    'host': host,
    'user': user,
    'password': password,
    'database': f"project_manager_V2"
}

# نافذة شاملة لإدارة العميل
class ClientManagementWindow(QDialog):
    
    # init
    def __init__(self, parent=None, client_data=None):
        super().__init__(parent)
        self.parent = parent
        self.client_data = client_data or {}
        self.client_id = self.client_data.get('id', None)
        
        # تهيئة متغيرات الجداول
        self.projects_table = None
        self.phases_table = None
        self.tasks_table = None
        self.custody_table = None
        self.payments_table = None
        self.expenses_table = None
        
        # إعداد النافذة الأساسية
        self.setup_window()
        
        # إنشاء التابات
        self.create_tabs()
        
        # تحميل البيانات
        self.load_client_info()

        # تحديث عرض معلومات العميل
        self.update_client_info_display()

        # إضافة أزرار الطباعة لجميع التابات
        self.add_print_buttons()

        # تطبيق الستايل الموحد
        apply_to_client_management(self)

    # إعداد النافذة الأساسية
    def setup_window(self):
        client_name = self.client_data.get('اسم_العميل', 'عميل جديد')
        self.setWindowTitle(f"إدارة العميل - {client_name}")
        self.setGeometry(100, 100, 1600, 900)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setWindowFlags(Qt.Window | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # العنوان الرئيسي
        self.title_label = QLabel()
        self.title_label.setObjectName("main_title")
        self.title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title_label)
        
        # إنشاء التابات
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # تطبيق الستايل الموحد
        apply_to_client_management(self)

    # تحديث العنوان الرئيسي ليعكس التاب الحالي
    def update_title(self):
        try:
            client_name = self.client_data.get('اسم_العميل', 'عميل جديد')
            current_tab_index = self.tab_widget.currentIndex()
            
            if current_tab_index >= 0:
                tab_text = self.tab_widget.tabText(current_tab_index)
                # إزالة أيقونات HTML من نص التاب إذا كانت موجودة
                import re
                clean_tab_text = re.sub(r'<[^>]+>', '', tab_text)
                title_text = f"إدارة عميل {client_name} - {clean_tab_text}"
            else:
                title_text = f"إدارة عميل {client_name}"
            
            self.title_label.setText(title_text)
            
        except Exception as e:
            print(f"خطأ في تحديث العنوان: {e}")
            self.title_label.setText(f"إدارة عميل {self.client_data.get('اسم_العميل', 'عميل جديد')}")

    # إنشاء التابات
    def create_tabs(self):

        # تاب معلومات العميل (أقصى اليمين)
        self.create_client_info_tab()

        # تاب المشاريع والمقاولات
        self.create_projects_contracts_tab()

        # تاب مراحل المشاريع
        self.create_project_phases_tab()

        # تاب المهام والجداول الزمنية
        self.create_tasks_schedules_tab()

        # تاب العهد
        self.create_custody_tab()

        # تاب الدفعات
        self.create_payments_tab()

        # تاب المصروفات
        self.create_expenses_tab()

        # تعيين التاب الأول (معلومات العميل) كتاب افتراضي
        self.tab_widget.setCurrentIndex(0)

        # ربط إشارة تغيير التاب بدالة التحديث التلقائي
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        # تحديث العنوان الأولي
        self.update_title()

        # تطبيق الستايل الموحد
        apply_to_client_management(self)

    # إنشاء تاب معلومات العميل
    def create_client_info_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)

        # الصف الأول: المعلومات الأساسية والمالية
        self.create_client_top_section(layout)

        # الصف الثاني: المعلومات الإضافية
        self.create_client_additional_info(layout)

        # إضافة مساحة فارغة في النهاية
        layout.addStretch()

        self.tab_widget.addTab(tab, qta.icon('fa5s.user', color='#3498db'), "معلومات العميل")

        # تطبيق الستايل الموحد
        apply_to_client_management(self)

    # إنشاء الصف العلوي للمعلومات الأساسية والمالية
    def create_client_top_section(self, parent_layout):
        # تخطيط أفقي للصف العلوي
        top_row_layout = QHBoxLayout()
        top_row_layout.setSpacing(15)

        # الحاوية الأولى: المعلومات الأساسية مع زر التعديل
        self.create_basic_info_container(top_row_layout)

        # الحاوية الثانية: المعلومات المالية مع زر الدفعات
        self.create_financial_info_container(top_row_layout)

        parent_layout.addLayout(top_row_layout)

    # إنشاء حاوية المعلومات الأساسية
    def create_basic_info_container(self, parent_layout):
        # إنشاء الحاوية
        basic_info_frame = QFrame()
        basic_info_frame.setObjectName("info_card")
        basic_info_frame.setFrameStyle(QFrame.StyledPanel)

        basic_layout = QVBoxLayout(basic_info_frame)

        # عنوان القسم
        title_label = QLabel("المعلومات الأساسية")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        basic_layout.addWidget(title_label)

        # المعلومات الأساسية
        info_layout = QVBoxLayout()

        # اسم العميل
        self.client_name_display = QLabel("غير محدد")
        self.client_name_display.setObjectName("value_label")
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("اسم العميل:"))
        name_layout.addWidget(self.client_name_display)
        name_layout.addStretch()
        info_layout.addLayout(name_layout)

        # التصنيف
        self.client_classification_display = QLabel("غير محدد")
        self.client_classification_display.setObjectName("value_label")
        classification_layout = QHBoxLayout()
        classification_layout.addWidget(QLabel("التصنيف:"))
        classification_layout.addWidget(self.client_classification_display)
        classification_layout.addStretch()
        info_layout.addLayout(classification_layout)

        # رقم الهاتف
        self.client_phone_display = QLabel("غير محدد")
        self.client_phone_display.setObjectName("value_label")
        phone_layout = QHBoxLayout()
        phone_layout.addWidget(QLabel("رقم الهاتف:"))
        phone_layout.addWidget(self.client_phone_display)
        phone_layout.addStretch()
        info_layout.addLayout(phone_layout)

        # الإيميل
        self.client_email_display = QLabel("غير محدد")
        self.client_email_display.setObjectName("value_label")
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("الإيميل:"))
        email_layout.addWidget(self.client_email_display)
        email_layout.addStretch()
        info_layout.addLayout(email_layout)

        basic_layout.addLayout(info_layout)

        # زر تعديل بيانات العميل
        edit_client_btn = QPushButton("تعديل بيانات العميل")
        edit_client_btn.setIcon(qta.icon('fa5s.edit', color='#ffffff'))
        edit_client_btn.setObjectName("edit_button")
        edit_client_btn.clicked.connect(self.edit_client_data)
        basic_layout.addWidget(edit_client_btn)

        parent_layout.addWidget(basic_info_frame)

    # إنشاء حاوية المعلومات المالية
    def create_financial_info_container(self, parent_layout):
        # إنشاء الحاوية
        financial_info_frame = QFrame()
        financial_info_frame.setObjectName("success_card")
        financial_info_frame.setFrameStyle(QFrame.StyledPanel)

        financial_layout = QVBoxLayout(financial_info_frame)

        # عنوان القسم
        title_label = QLabel("المعلومات المالية")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        financial_layout.addWidget(title_label)

        # المعلومات المالية
        financial_stats_layout = QVBoxLayout()

        # إجمالي المشاريع
        self.total_projects_display = QLabel("0")
        self.total_projects_display.setObjectName("stat_value")
        projects_layout = QHBoxLayout()
        projects_layout.addWidget(QLabel("إجمالي المشاريع:"))
        projects_layout.addWidget(self.total_projects_display)
        projects_layout.addStretch()
        financial_stats_layout.addLayout(projects_layout)

        # إجمالي المدفوع
        self.total_paid_display = QLabel(f"0 {Currency_type}")
        self.total_paid_display.setObjectName("stat_value")
        paid_layout = QHBoxLayout()
        paid_layout.addWidget(QLabel("إجمالي المدفوع:"))
        paid_layout.addWidget(self.total_paid_display)
        paid_layout.addStretch()
        financial_stats_layout.addLayout(paid_layout)

        # إجمالي الباقي
        self.total_remaining_display = QLabel(f"0 {Currency_type}")
        self.total_remaining_display.setObjectName("stat_value")
        remaining_layout = QHBoxLayout()
        remaining_layout.addWidget(QLabel("إجمالي الباقي:"))
        remaining_layout.addWidget(self.total_remaining_display)
        remaining_layout.addStretch()
        financial_stats_layout.addLayout(remaining_layout)

        financial_layout.addLayout(financial_stats_layout)

        # زر دفعات العميل
        payments_btn = QPushButton("دفعات العميل")
        payments_btn.setIcon(qta.icon('fa5s.money-bill-wave', color='#ffffff'))
        payments_btn.setObjectName("info_button")
        payments_btn.clicked.connect(self.show_client_payments)
        financial_layout.addWidget(payments_btn)

        parent_layout.addWidget(financial_info_frame)

    # إنشاء حاوية المعلومات الإضافية
    def create_client_additional_info(self, parent_layout):
        # إنشاء الحاوية
        additional_info_frame = QFrame()
        additional_info_frame.setObjectName("warning_card")
        additional_info_frame.setFrameStyle(QFrame.StyledPanel)

        additional_layout = QVBoxLayout(additional_info_frame)

        # عنوان القسم
        title_label = QLabel("المعلومات الإضافية")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        additional_layout.addWidget(title_label)

        # تخطيط شبكي للمعلومات الإضافية
        grid_layout = QGridLayout()

        # العنوان
        self.client_address_display = QLabel("غير محدد")
        self.client_address_display.setObjectName("value_label")
        grid_layout.addWidget(QLabel("العنوان:"), 0, 0)
        grid_layout.addWidget(self.client_address_display, 0, 1, 1, 3)

        # تاريخ الإنشاء
        self.client_creation_date_display = QLabel("غير محدد")
        self.client_creation_date_display.setObjectName("value_label")
        grid_layout.addWidget(QLabel("تاريخ الإنشاء:"), 1, 0)
        grid_layout.addWidget(self.client_creation_date_display, 1, 1)

        # آخر تحديث
        self.client_last_update_display = QLabel("غير محدد")
        self.client_last_update_display.setObjectName("value_label")
        grid_layout.addWidget(QLabel("آخر تحديث:"), 1, 2)
        grid_layout.addWidget(self.client_last_update_display, 1, 3)

        # الملاحظات
        self.client_notes_display = QLabel("غير محدد")
        self.client_notes_display.setObjectName("value_label")
        self.client_notes_display.setWordWrap(True)
        grid_layout.addWidget(QLabel("ملاحظات:"), 2, 0)
        grid_layout.addWidget(self.client_notes_display, 2, 1, 1, 3)

        additional_layout.addLayout(grid_layout)
        parent_layout.addWidget(additional_info_frame)

    # فتح نافذة تعديل بيانات العميل
    def edit_client_data(self):
        try:
            QMessageBox.information(self, "تعديل البيانات", "سيتم تطوير نافذة تعديل بيانات العميل قريباً")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة التعديل: {str(e)}")

    # عرض جدول دفعات العميل
    def show_client_payments(self):
        try:
            # إنشاء نافذة جديدة لعرض دفعات العميل
            payments_dialog = QDialog(self)
            payments_dialog.setWindowTitle(f"دفعات العميل - {self.client_data.get('اسم_العميل', 'غير محدد')}")
            payments_dialog.setGeometry(200, 200, 1000, 600)
            payments_dialog.setLayoutDirection(Qt.RightToLeft)

            layout = QVBoxLayout(payments_dialog)

            # عنوان النافذة
            title_label = QLabel("جميع دفعات المشاريع المرتبطة بالعميل")
            title_label.setObjectName("dialog_title")
            title_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(title_label)

            # جدول الدفعات
            payments_table = QTableWidget()
            headers = ["ID", "المشروع", "المبلغ المدفوع", "تاريخ الدفع", "طريقة الدفع", "وصف الدفعة", "ملاحظات"]
            payments_table.setColumnCount(len(headers))
            payments_table.setHorizontalHeaderLabels(headers)
            payments_table.hideColumn(0)  # إخفاء عمود ID

            # تطبيق إعدادات الجدول
            table_setting(payments_table)
            setup_table_style(payments_table)

            layout.addWidget(payments_table)

            # تحميل بيانات الدفعات
            self.load_client_payments_data(payments_table)

            # أزرار الإجراءات
            buttons_layout = QHBoxLayout()

            close_btn = QPushButton("إغلاق")
            close_btn.setIcon(qta.icon('fa5s.times', color='#ffffff'))
            close_btn.clicked.connect(payments_dialog.close)

            buttons_layout.addStretch()
            buttons_layout.addWidget(close_btn)
            layout.addLayout(buttons_layout)

            # تطبيق الستايل الموحد على النافذة
            apply_management_style(payments_dialog)
            payments_dialog.exec()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في عرض دفعات العميل: {str(e)}")

    # تحميل بيانات دفعات العميل
    def load_client_payments_data(self, table):
        try:
            if not self.client_id:
                return

            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # استعلام لجلب جميع دفعات المشاريع المرتبطة بالعميل
            cursor.execute("""
                SELECT
                    d.id,
                    p.اسم_المشروع as project_name,
                    d.المبلغ_المدفوع,
                    d.تاريخ_الدفع,
                    d.طريقة_الدفع,
                    d.وصف_المدفوع,
                    COALESCE(d.ملاحظات, '') as ملاحظات
                FROM المشاريع_المدفوعات d
                LEFT JOIN المشاريع p ON d.معرف_المشروع = p.id
                WHERE p.معرف_العميل = %s
                ORDER BY d.تاريخ_الدفع DESC
            """, (self.client_id,))

            payments = cursor.fetchall()

            table.setRowCount(len(payments))

            for row, payment in enumerate(payments):
                table.setItem(row, 0, QTableWidgetItem(str(payment[0])))  # ID
                table.setItem(row, 1, QTableWidgetItem(str(payment[1] or "غير محدد")))  # المشروع
                table.setItem(row, 2, QTableWidgetItem(f"{payment[2]:,.0f} {Currency_type}"))  # المبلغ
                table.setItem(row, 3, QTableWidgetItem(str(payment[3] or "غير محدد")))  # التاريخ
                table.setItem(row, 4, QTableWidgetItem(str(payment[4] or "غير محدد")))  # طريقة الدفع
                table.setItem(row, 5, QTableWidgetItem(str(payment[5] or "غير محدد")))  # وصف الدفعة
                table.setItem(row, 6, QTableWidgetItem(str(payment[6] or "غير محدد")))  # ملاحظات

            conn.close()

        except Exception as e:
            print(f"خطأ في تحميل بيانات دفعات العميل: {e}")

    # تحديث عرض معلومات العميل
    def update_client_info_display(self):
        try:
            if not self.client_data:
                return

            # تحديث المعلومات الأساسية
            self.client_name_display.setText(self.client_data.get('اسم_العميل', 'غير محدد'))
            self.client_classification_display.setText(self.client_data.get('التصنيف', 'غير محدد'))
            self.client_phone_display.setText(self.client_data.get('رقم_الهاتف', 'غير محدد'))
            self.client_email_display.setText(self.client_data.get('الإيميل', 'غير محدد'))

            # تحديث المعلومات الإضافية
            self.client_address_display.setText(self.client_data.get('العنوان', 'غير محدد'))
            self.client_creation_date_display.setText(str(self.client_data.get('تاريخ_الإنشاء', 'غير محدد')))
            self.client_last_update_display.setText(str(self.client_data.get('آخر_تحديث', 'غير محدد')))
            self.client_notes_display.setText(self.client_data.get('ملاحظات', 'غير محدد'))

            # تحديث المعلومات المالية
            self.update_financial_summary()

        except Exception as e:
            print(f"خطأ في تحديث عرض معلومات العميل: {e}")

    # تحديث الملخص المالي للعميل
    def update_financial_summary(self):
        try:
            if not self.client_id:
                return

            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # حساب إجمالي المشاريع والمقاولات من جدول واحد
            cursor.execute("""
                SELECT
                    COUNT(*) as total_projects,
                    COALESCE(SUM(المبلغ), 0) as total_amount,
                    COALESCE(SUM(المدفوع), 0) as total_paid,
                    COALESCE(SUM(الباقي), 0) as total_remaining
                FROM المشاريع
                WHERE معرف_العميل = %s
            """, (self.client_id,))

            result = cursor.fetchone()

            if result:
                total_projects = result[0]
                total_amount = result[1]
                total_paid = result[2]
                total_remaining = result[3]

                # تحديث العرض
                self.total_projects_display.setText(str(total_projects))
                self.total_paid_display.setText(f"{total_paid:,.0f} {Currency_type}")

                # تلوين المبلغ الباقي حسب الحالة
                if total_remaining <= 0:
                    self.total_remaining_display.setText("خالص")
                    self.total_remaining_display.setObjectName("status_label")
                    # استخدام create_colored_label من ملف الستايلات
                    color = get_status_color("مكتمل")
                    self.total_remaining_display.setProperty("status_color", color)
                else:
                    self.total_remaining_display.setText(f"{total_remaining:,.0f} {Currency_type}")
                    self.total_remaining_display.setObjectName("status_label")
                    color = get_status_color("غير مدفوع")
                    self.total_remaining_display.setProperty("status_color", color)

            conn.close()

        except Exception as e:
            print(f"خطأ في تحديث الملخص المالي: {e}")





    # حذف دالة create_client_stat_card - يتم استخدام create_stat_card من ملف الستايلات

    # إنشاء قسم الإجراءات السريعة
    def create_client_quick_actions(self, parent_layout):
        actions_frame = QFrame()
        actions_frame.setFrameStyle(QFrame.StyledPanel)
        actions_layout = QVBoxLayout(actions_frame)
        
        # عنوان القسم
        title_label = QLabel("الإجراءات السريعة")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        actions_layout.addWidget(title_label)
        
        # تخطيط أفقي للأزرار
        buttons_layout = QHBoxLayout()
        
        # أزرار الإجراءات السريعة
        edit_client_btn = QPushButton("تعديل بيانات العميل")
        edit_client_btn.setIcon(qta.icon('fa5s.edit', color='#3498db'))
        edit_client_btn.clicked.connect(self.edit_client_data)
        
        add_project_btn = QPushButton("إضافة مشروع جديد")
        add_project_btn.setIcon(qta.icon('fa5s.plus', color='#27ae60'))
        add_project_btn.clicked.connect(self.add_new_project)
        
        view_reports_btn = QPushButton("عرض التقارير")
        view_reports_btn.setIcon(qta.icon('fa5s.chart-bar', color='#f39c12'))
        view_reports_btn.clicked.connect(self.view_client_reports)
        
        buttons_layout.addWidget(edit_client_btn)
        buttons_layout.addWidget(add_project_btn)
        buttons_layout.addWidget(view_reports_btn)
        buttons_layout.addStretch()
        
        actions_layout.addLayout(buttons_layout)
        parent_layout.addWidget(actions_frame)

    # تحميل معلومات العميل
    def load_client_info(self):
        if not self.client_id:
            return
            
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            
            # جلب معلومات العميل
            cursor.execute("""
                SELECT * FROM العملاء WHERE id = %s
            """, (self.client_id,))
            
            client_info = cursor.fetchone()
            if client_info:
                self.client_data = client_info
                self.update_client_info_display()
            
            conn.close()
            
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في تحميل معلومات العميل: {str(e)}")



    # حذف دالة apply_centralized_styles - يتم استخدام apply_management_style من ملف الستايلات

    # حذف دالة apply_rtl_to_widgets - يتم تطبيق RTL من خلال apply_management_style

    # إضافة أزرار الطباعة لجميع التابات
    def add_print_buttons(self):
        try:
            # إضافة أزرار الطباعة تلقائياً لجميع التابات
            quick_add_print_button(self, self.tab_widget)

        except Exception as e:
            print(f"خطأ في إضافة أزرار الطباعة: {e}")

    # حذف دالة enhance_table_headers - يتم استخدام setup_table_style من ملف الستايلات

    # حذف دالة apply_enhanced_table_styling - يتم استخدام setup_table_style من ملف الستايلات

    # إنشاء تاب المشاريع والمقاولات
    def create_projects_contracts_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # الصف الأول: شريط البحث والفلاتر والأزرار
        top_layout = QHBoxLayout()

        # أزرار الإجراءات
        actions_layout = QHBoxLayout()

        add_project_btn = QPushButton("إضافة مشروع")
        add_project_btn.setIcon(qta.icon('fa5s.plus', color='#27ae60'))
        add_project_btn.clicked.connect(self.add_project_for_client)

        add_contract_btn = QPushButton("إضافة مقاولات")
        add_contract_btn.setIcon(qta.icon('fa5s.plus', color='#3498db'))
        add_contract_btn.clicked.connect(self.add_contract_for_client)

        actions_layout.addWidget(add_project_btn)
        actions_layout.addWidget(add_contract_btn)
        actions_layout.addStretch()

        # فلاتر متقدمة
        filter_layout = QHBoxLayout()

        # فلتر نوع المشروع
        self.project_type_filter = QComboBox()
        self.project_type_filter.addItems(["الكل", "المشاريع", "المقاولات"])
        self.project_type_filter.currentTextChanged.connect(self.filter_projects_contracts)
        type_label = QLabel("النوع:")
        filter_layout.addWidget(type_label)
        filter_layout.addWidget(self.project_type_filter)

        # فلتر الحالة
        self.project_status_filter = QComboBox()
        self.project_status_filter.addItems(["الكل", "قيد الإنجاز", "معلق", "منتهي", "تم التسليم", "متوقف", "تأكيد التسليم"])
        self.project_status_filter.currentTextChanged.connect(self.filter_projects_contracts)
        status_label = QLabel("الحالة:")
        filter_layout.addWidget(status_label)
        filter_layout.addWidget(self.project_status_filter)

        # شريط البحث
        search_layout = QHBoxLayout()
        search_label = QLabel("البحث:")
        search_layout.addWidget(search_label)
        self.projects_search = QLineEdit()
        self.projects_search.setPlaceholderText("ابحث في المشاريع والمقاولات...")
        self.projects_search.textChanged.connect(self.filter_projects_contracts)
        search_layout.addWidget(self.projects_search)

        top_layout.addLayout(actions_layout)
        top_layout.addLayout(filter_layout)
        top_layout.addLayout(search_layout)
        layout.addLayout(top_layout)

        # الصف الثاني: البطاقات الإحصائية للمشاريع والمقاولات
        self.create_projects_statistics_cards(layout)

        # جدول المشاريع والمقاولات
        self.projects_table = QTableWidget()
        self.setup_projects_table()
        layout.addWidget(self.projects_table)

        self.tab_widget.addTab(tab, qta.icon('fa5s.project-diagram', color='#8e44ad'), "المشاريع والمقاولات")

    # إعداد جدول المشاريع والمقاولات
    def setup_projects_table(self):
        headers = ["ID", "النوع", "اسم المشروع", "التصنيف", "المبلغ", "المدفوع", "الباقي", "تاريخ الاستلام", "تاريخ التسليم", "الحالة", "ملاحظات"]
        self.projects_table.setColumnCount(len(headers))
        self.projects_table.setHorizontalHeaderLabels(headers)
        self.projects_table.hideColumn(0)  # إخفاء عمود ID

        # تطبيق إعدادات الجدول
        table_setting(self.projects_table)
        setup_table_style(self.projects_table)

        # إضافة قائمة السياق للجدول
        setup_table_context_menu(self.projects_table, self, "المشاريع والمقاولات", is_main_table=False)

        # إضافة وظيفة النقر المزدوج لفتح نافذة إدارة المشروع
        self.projects_table.itemDoubleClicked.connect(self.on_projects_table_double_click)

    # إنشاء البطاقات الإحصائية للمشاريع والمقاولات
    def create_projects_statistics_cards(self, parent_layout):
        # إنشاء حاوية للبطاقات الإحصائية
        stats_container = QFrame()
        stats_container.setObjectName("stats_container")

        # تخطيط أفقي للبطاقات
        stats_layout = QHBoxLayout(stats_container)

        # إنشاء متغيرات للقيم
        self.projects_total_count = 0
        self.projects_total_amount = f"0 {Currency_type}"
        self.projects_paid_amount = f"0 {Currency_type}"
        self.projects_remaining_amount = f"0 {Currency_type}"
        self.contracts_count = 0
        self.active_projects_count = 0

        # تعريف البطاقات
        stats = [
            ("إجمالي المشاريع", self.projects_total_count, "#3498db"),
            ("إجمالي المقاولات", self.contracts_count, "#9b59b6"),
            ("المشاريع النشطة", self.active_projects_count, "#27ae60"),
            ("إجمالي المبالغ", self.projects_total_amount, "#8e44ad"),
            ("المبالغ المدفوعة", self.projects_paid_amount, "#27ae60"),
            ("المبالغ المتبقية", self.projects_remaining_amount, "#e74c3c"),
        ]

        # إنشاء البطاقات وحفظها
        self.projects_stat_cards = []
        for title, value, color in stats:
            card = create_stat_card(title, value, color)
            self.projects_stat_cards.append(card)
            stats_layout.addWidget(card)

        parent_layout.addWidget(stats_container)

    # إنشاء تاب مراحل المشاريع
    def create_project_phases_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # الصف الأول: الفلاتر وشريط البحث
        top_layout = QHBoxLayout()

        # فلتر المشروع
        filter_layout = QHBoxLayout()
        self.phases_project_filter = QComboBox()
        self.phases_project_filter.addItem("جميع المشاريع")
        self.phases_project_filter.currentTextChanged.connect(self.filter_project_phases)
        filter_layout.addWidget(QLabel("المشروع:"))
        filter_layout.addWidget(self.phases_project_filter)

        # فلتر حالة المبلغ
        self.phases_amount_status_filter = QComboBox()
        self.phases_amount_status_filter.addItems(["الكل", "تم الإدراج", "غير مدرج"])
        self.phases_amount_status_filter.currentTextChanged.connect(self.filter_project_phases)
        filter_layout.addWidget(QLabel("حالة المبلغ:"))
        filter_layout.addWidget(self.phases_amount_status_filter)

        # شريط البحث
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("البحث:"))
        self.phases_search = QLineEdit()
        self.phases_search.setPlaceholderText("ابحث في مراحل المشاريع...")
        self.phases_search.textChanged.connect(self.filter_project_phases)
        search_layout.addWidget(self.phases_search)

        top_layout.addLayout(filter_layout)
        top_layout.addLayout(search_layout)
        layout.addLayout(top_layout)

        # الصف الثاني: البطاقات الإحصائية للمراحل
        self.create_phases_statistics_cards(layout)

        # جدول مراحل المشاريع
        self.phases_table = QTableWidget()
        self.setup_phases_table()
        layout.addWidget(self.phases_table)

        self.tab_widget.addTab(tab, qta.icon('fa5s.tasks', color='#f39c12'), "مراحل المشاريع")

    # إعداد جدول مراحل المشاريع
    def setup_phases_table(self):
        headers = ["ID", "المشروع", "الرقم", "اسم المرحلة", "وصف المرحلة", "الوحدة", "الكمية", "السعر", "الإجمالي", "حالة المبلغ", "ملاحظات"]
        self.phases_table.setColumnCount(len(headers))
        self.phases_table.setHorizontalHeaderLabels(headers)
        self.phases_table.hideColumn(0)  # إخفاء عمود ID

        # تطبيق إعدادات الجدول
        table_setting(self.phases_table)
        setup_table_style(self.phases_table)

        # إضافة قائمة السياق للجدول
        setup_table_context_menu(self.phases_table, self, "مراحل المشاريع", is_main_table=False)

        # إضافة وظيفة النقر المزدوج
        self.phases_table.itemDoubleClicked.connect(self.on_phases_table_double_click)

    # إنشاء البطاقات الإحصائية لمراحل المشاريع
    def create_phases_statistics_cards(self, parent_layout):
        # إنشاء حاوية للبطاقات الإحصائية
        stats_container = QFrame()
        stats_container.setObjectName("phases_stats_container")

        # تخطيط أفقي للبطاقات
        stats_layout = QHBoxLayout(stats_container)

        # إنشاء البطاقات بقيم افتراضية
        stats = [
            ("إجمالي المراحل", "0", "#3498db"),
            ("إجمالي المبالغ", f"0 {Currency_type}", "#8e44ad"),
            ("المبالغ المدرجة", f"0 {Currency_type}", "#27ae60"),
            ("المبالغ غير المدرجة", f"0 {Currency_type}", "#e74c3c"),
        ]

        # إنشاء البطاقات
        for title, value, color in stats:
            card = create_stat_card(title, value, color)
            stats_layout.addWidget(card)

        parent_layout.addWidget(stats_container)

    # إنشاء تاب المهام والجداول الزمنية
    def create_tasks_schedules_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # الصف الأول: الفلاتر وشريط البحث
        top_layout = QHBoxLayout()

        # فلاتر
        filter_layout = QHBoxLayout()

        # فلتر المشروع
        self.tasks_project_filter = QComboBox()
        self.tasks_project_filter.addItem("جميع المشاريع")
        self.tasks_project_filter.currentTextChanged.connect(self.filter_tasks)
        filter_layout.addWidget(QLabel("المشروع:"))
        filter_layout.addWidget(self.tasks_project_filter)

        # فلتر حالة المهمة
        self.tasks_status_filter = QComboBox()
        self.tasks_status_filter.addItems(["الكل", "لم يبدأ", "قيد التنفيذ", "مكتمل", "متوقف"])
        self.tasks_status_filter.currentTextChanged.connect(self.filter_tasks)
        filter_layout.addWidget(QLabel("الحالة:"))
        filter_layout.addWidget(self.tasks_status_filter)

        # شريط البحث
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("البحث:"))
        self.tasks_search = QLineEdit()
        self.tasks_search.setPlaceholderText("ابحث في المهام...")
        self.tasks_search.textChanged.connect(self.filter_tasks)
        search_layout.addWidget(self.tasks_search)

        top_layout.addLayout(filter_layout)
        top_layout.addLayout(search_layout)
        layout.addLayout(top_layout)

        # الصف الثاني: البطاقات الإحصائية للمهام
        self.create_tasks_statistics_cards(layout)

        # جدول المهام
        self.tasks_table = QTableWidget()
        self.setup_tasks_table()
        layout.addWidget(self.tasks_table)

        self.tab_widget.addTab(tab, qta.icon('fa5s.calendar-alt', color='#16a085'), "المهام والجداول الزمنية")

    # إعداد جدول المهام
    def setup_tasks_table(self):
        headers = ["ID", "المشروع", "عنوان المهمة", "الموظف", "تاريخ البداية", "تاريخ النهاية", "الحالة", "المبلغ", "النسبة", "ملاحظات"]
        self.tasks_table.setColumnCount(len(headers))
        self.tasks_table.setHorizontalHeaderLabels(headers)
        self.tasks_table.hideColumn(0)  # إخفاء عمود ID

        # تطبيق إعدادات الجدول
        table_setting(self.tasks_table)
        setup_table_style(self.tasks_table)

        # إضافة قائمة السياق للجدول
        setup_table_context_menu(self.tasks_table, self, "المهام", is_main_table=False)

        # إضافة وظيفة النقر المزدوج
        self.tasks_table.itemDoubleClicked.connect(self.on_tasks_table_double_click)

    # إنشاء البطاقات الإحصائية للمهام
    def create_tasks_statistics_cards(self, parent_layout):
        # إنشاء حاوية للبطاقات الإحصائية
        stats_container = QFrame()
        stats_container.setObjectName("tasks_stats_container")

        # تخطيط أفقي للبطاقات
        stats_layout = QHBoxLayout(stats_container)

        # إنشاء البطاقات بقيم افتراضية
        stats = [
            ("إجمالي المهام", "0", "#3498db"),
            ("المهام المكتملة", "0", "#27ae60"),
            ("المهام قيد التنفيذ", "0", "#f39c12"),
            ("المهام المعلقة", "0", "#e74c3c"),
            ("إجمالي المبالغ", f"0 {Currency_type}", "#8e44ad"),
        ]

        # إنشاء البطاقات
        for title, value, color in stats:
            card = create_stat_card(title, value, color)
            stats_layout.addWidget(card)

        parent_layout.addWidget(stats_container)

    # إنشاء تاب العهد
    def create_custody_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # الصف الأول: الفلاتر وشريط البحث
        top_layout = QHBoxLayout()

        # فلاتر
        filter_layout = QHBoxLayout()

        # فلتر المشروع
        self.custody_project_filter = QComboBox()
        self.custody_project_filter.addItem("جميع المشاريع")
        self.custody_project_filter.currentTextChanged.connect(self.filter_custody)
        filter_layout.addWidget(QLabel("المشروع:"))
        filter_layout.addWidget(self.custody_project_filter)

        # فلتر حالة العهدة
        self.custody_status_filter = QComboBox()
        self.custody_status_filter.addItems(["الكل", "نشطة", "مسترجعة", "مفقودة"])
        self.custody_status_filter.currentTextChanged.connect(self.filter_custody)
        filter_layout.addWidget(QLabel("الحالة:"))
        filter_layout.addWidget(self.custody_status_filter)

        # شريط البحث
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("البحث:"))
        self.custody_search = QLineEdit()
        self.custody_search.setPlaceholderText("ابحث في العهد...")
        self.custody_search.textChanged.connect(self.filter_custody)
        search_layout.addWidget(self.custody_search)

        top_layout.addLayout(filter_layout)
        top_layout.addLayout(search_layout)
        layout.addLayout(top_layout)

        # الصف الثاني: البطاقات الإحصائية للعهد
        self.create_custody_statistics_cards(layout)

        # جدول العهد
        self.custody_table = QTableWidget()
        self.setup_custody_table()
        layout.addWidget(self.custody_table)

        self.tab_widget.addTab(tab, qta.icon('fa5s.handshake', color='#e67e22'), "العهد")

    # إعداد جدول العهد
    def setup_custody_table(self):
        headers = ["ID", "المشروع", "وصف العهدة", "المبلغ", "المصروف", "المتبقي", "المسؤول", "تاريخ الاستلام", "تاريخ الإرجاع", "الحالة", "ملاحظات"]
        self.custody_table.setColumnCount(len(headers))
        self.custody_table.setHorizontalHeaderLabels(headers)
        self.custody_table.hideColumn(0)  # إخفاء عمود ID

        # تطبيق إعدادات الجدول
        table_setting(self.custody_table)
        setup_table_style(self.custody_table)

        # إضافة قائمة السياق للجدول
        setup_table_context_menu(self.custody_table, self, "العهد", is_main_table=False)

        # إضافة وظيفة النقر المزدوج
        self.custody_table.itemDoubleClicked.connect(self.on_custody_table_double_click)

    # إنشاء البطاقات الإحصائية للعهد
    def create_custody_statistics_cards(self, parent_layout):
        # إنشاء حاوية للبطاقات الإحصائية
        stats_container = QFrame()
        stats_container.setObjectName("custody_stats_container")

        # تخطيط أفقي للبطاقات
        stats_layout = QHBoxLayout(stats_container)

        # إنشاء البطاقات بقيم افتراضية
        stats = [
            ("إجمالي العهد", "0", "#3498db"),
            ("العهد النشطة", "0", "#27ae60"),
            ("إجمالي المبالغ", f"0 {Currency_type}", "#8e44ad"),
            ("إجمالي المصروفات", f"0 {Currency_type}", "#e74c3c"),
            ("إجمالي المتبقي", f"0 {Currency_type}", "#f39c12"),
        ]

        # إنشاء البطاقات
        for title, value, color in stats:
            card = create_stat_card(title, value, color)
            stats_layout.addWidget(card)

        parent_layout.addWidget(stats_container)

    # إنشاء تاب الدفعات
    def create_payments_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # الصف الأول: الفلاتر وشريط البحث
        top_layout = QHBoxLayout()

        # فلاتر
        filter_layout = QHBoxLayout()

        # فلتر المشروع
        self.payments_project_filter = QComboBox()
        self.payments_project_filter.addItem("جميع المشاريع")
        self.payments_project_filter.currentTextChanged.connect(self.filter_payments)
        filter_layout.addWidget(QLabel("المشروع:"))
        filter_layout.addWidget(self.payments_project_filter)

        # فلتر طريقة الدفع
        self.payment_method_filter = QComboBox()
        self.payment_method_filter.addItems(["الكل", "نقدي", "شيك", "تحويل بنكي", "بطاقة ائتمان"])
        self.payment_method_filter.currentTextChanged.connect(self.filter_payments)
        filter_layout.addWidget(QLabel("طريقة الدفع:"))
        filter_layout.addWidget(self.payment_method_filter)

        # شريط البحث
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("البحث:"))
        self.payments_search = QLineEdit()
        self.payments_search.setPlaceholderText("ابحث في الدفعات...")
        self.payments_search.textChanged.connect(self.filter_payments)
        search_layout.addWidget(self.payments_search)

        top_layout.addLayout(filter_layout)
        top_layout.addLayout(search_layout)
        layout.addLayout(top_layout)

        # الصف الثاني: البطاقات الإحصائية للدفعات
        self.create_payments_statistics_cards(layout)

        # جدول الدفعات
        self.payments_table = QTableWidget()
        self.setup_payments_table()
        layout.addWidget(self.payments_table)

        self.tab_widget.addTab(tab, qta.icon('fa5s.money-bill-wave', color='#27ae60'), "الدفعات")

    # إعداد جدول الدفعات
    def setup_payments_table(self):
        headers = ["ID", "المشروع", "المبلغ", "تاريخ الدفع", "طريقة الدفع", "رقم المرجع", "الحالة", "وصف الدفعة"]
        self.payments_table.setColumnCount(len(headers))
        self.payments_table.setHorizontalHeaderLabels(headers)
        self.payments_table.hideColumn(0)  # إخفاء عمود ID

        # تطبيق إعدادات الجدول
        table_setting(self.payments_table)
        setup_table_style(self.payments_table)

        # إضافة قائمة السياق للجدول
        setup_table_context_menu(self.payments_table, self, "الدفعات", is_main_table=False)

        # إضافة وظيفة النقر المزدوج
        self.payments_table.itemDoubleClicked.connect(self.on_payments_table_double_click)

    # إنشاء البطاقات الإحصائية للدفعات
    def create_payments_statistics_cards(self, parent_layout):
        # إنشاء حاوية للبطاقات الإحصائية
        stats_container = QFrame()
        stats_container.setObjectName("payments_stats_container")

        # تخطيط أفقي للبطاقات
        stats_layout = QHBoxLayout(stats_container)

        # إنشاء البطاقات بقيم افتراضية
        stats = [
            ("إجمالي الدفعات", "0", "#3498db"),
            ("إجمالي المبالغ", f"0 {Currency_type}", "#27ae60"),
            ("الدفعات النقدية", f"0 {Currency_type}", "#f39c12"),
            ("التحويلات البنكية", f"0 {Currency_type}", "#8e44ad"),
            ("دفعات هذا الشهر", f"0 {Currency_type}", "#16a085"),
        ]

        # إنشاء البطاقات
        for title, value, color in stats:
            card = create_stat_card(title, value, color)
            stats_layout.addWidget(card)

        parent_layout.addWidget(stats_container)

    # إنشاء تاب المصروفات
    def create_expenses_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # الصف الأول: الفلاتر وشريط البحث
        top_layout = QHBoxLayout()

        # فلاتر
        filter_layout = QHBoxLayout()

        # فلتر المشروع
        self.expenses_project_filter = QComboBox()
        self.expenses_project_filter.addItem("جميع المشاريع")
        self.expenses_project_filter.currentTextChanged.connect(self.filter_expenses)
        filter_layout.addWidget(QLabel("المشروع:"))
        filter_layout.addWidget(self.expenses_project_filter)

        # فلتر نوع المصروف
        self.expense_type_filter = QComboBox()
        self.expense_type_filter.addItems(["الكل", "مواد", "عمالة", "معدات", "نقل", "أخرى"])
        self.expense_type_filter.currentTextChanged.connect(self.filter_expenses)
        filter_layout.addWidget(QLabel("النوع:"))
        filter_layout.addWidget(self.expense_type_filter)

        # فلتر حالة الموافقة
        self.expense_approval_filter = QComboBox()
        self.expense_approval_filter.addItems(["الكل", "معتمد", "قيد المراجعة", "مرفوض"])
        self.expense_approval_filter.currentTextChanged.connect(self.filter_expenses)
        filter_layout.addWidget(QLabel("الحالة:"))
        filter_layout.addWidget(self.expense_approval_filter)

        # شريط البحث
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("البحث:"))
        self.expenses_search = QLineEdit()
        self.expenses_search.setPlaceholderText("ابحث في المصروفات...")
        self.expenses_search.textChanged.connect(self.filter_expenses)
        search_layout.addWidget(self.expenses_search)

        top_layout.addLayout(filter_layout)
        top_layout.addLayout(search_layout)
        layout.addLayout(top_layout)

        # الصف الثاني: البطاقات الإحصائية للمصروفات
        self.create_expenses_statistics_cards(layout)

        # جدول المصروفات
        self.expenses_table = QTableWidget()
        self.setup_expenses_table()
        layout.addWidget(self.expenses_table)

        self.tab_widget.addTab(tab, qta.icon('fa5s.receipt', color='#e74c3c'), "المصروفات")

    # إعداد جدول المصروفات
    def setup_expenses_table(self):
        headers = ["ID", "المشروع", "وصف المصروف", "المبلغ", "التاريخ", "النوع", "رقم الفاتورة", "الحالة", "ملاحظات"]
        self.expenses_table.setColumnCount(len(headers))
        self.expenses_table.setHorizontalHeaderLabels(headers)
        self.expenses_table.hideColumn(0)  # إخفاء عمود ID

        # تطبيق إعدادات الجدول
        table_setting(self.expenses_table)
        setup_table_style(self.expenses_table)

        # إضافة قائمة السياق للجدول
        setup_table_context_menu(self.expenses_table, self, "المصروفات", is_main_table=False)

        # إضافة وظيفة النقر المزدوج
        self.expenses_table.itemDoubleClicked.connect(self.on_expenses_table_double_click)

    # إنشاء البطاقات الإحصائية للمصروفات
    def create_expenses_statistics_cards(self, parent_layout):
        # إنشاء حاوية للبطاقات الإحصائية
        stats_container = QFrame()
        stats_container.setObjectName("expenses_stats_container")

        # تخطيط أفقي للبطاقات
        stats_layout = QHBoxLayout(stats_container)

        # إنشاء البطاقات بقيم افتراضية
        stats = [
            ("إجمالي المصروفات", "0", "#3498db"),
            ("إجمالي المبالغ", f"0 {Currency_type}", "#e74c3c"),
            ("المصروفات المعتمدة", f"0 {Currency_type}", "#27ae60"),
            ("المصروفات المعلقة", f"0 {Currency_type}", "#f39c12"),
            ("مصروفات هذا الشهر", f"0 {Currency_type}", "#8e44ad"),
        ]

        # إنشاء البطاقات
        for title, value, color in stats:
            card = create_stat_card(title, value, color)
            stats_layout.addWidget(card)

        parent_layout.addWidget(stats_container)



    # تحميل بيانات المشاريع والمقاولات
    def load_projects_contracts_data(self):
        if not self.client_id:
            return

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # جلب المشاريع والمقاولات للعميل
            cursor.execute("""
                SELECT
                    id, اسم_القسم, اسم_المشروع, التصنيف, المبلغ, المدفوع, الباقي,
                    تاريخ_الإستلام, تاريخ_التسليم, الحالة, ملاحظات
                FROM المشاريع
                WHERE معرف_العميل = %s
                ORDER BY تاريخ_الإضافة DESC
            """, (self.client_id,))

            projects_data = cursor.fetchall()

            # تحديث الجدول
            self.projects_table.setRowCount(len(projects_data))

            for row, project in enumerate(projects_data):
                for col, value in enumerate(project):
                    if col in [4, 5, 6]:  # أعمدة المبالغ
                        if value is not None:
                            item = QTableWidgetItem(f"{value:,.0f}")
                        else:
                            item = QTableWidgetItem("0")
                    elif col in [7, 8]:  # أعمدة التواريخ
                        if value:
                            if isinstance(value, str):
                                try:
                                    value = datetime.strptime(value, '%Y-%m-%d').date()
                                except:
                                    pass
                            if isinstance(value, date):
                                item = QTableWidgetItem(value.strftime('%d/%m/%Y'))
                            else:
                                item = QTableWidgetItem(str(value) if value else "")
                        else:
                            item = QTableWidgetItem("")
                    else:
                        item = QTableWidgetItem(str(value) if value else "")

                    self.projects_table.setItem(row, col, item)

            # تحديث فلاتر المشاريع في التابات الأخرى
            self.update_project_filters()

            # تحديث الإحصائيات
            self.update_projects_statistics()

            conn.close()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في تحميل بيانات المشاريع والمقاولات: {str(e)}")

    # تحديث فلاتر المشاريع في جميع التابات
    def update_project_filters(self):
        if not self.client_id:
            return

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # جلب قائمة المشاريع للعميل
            cursor.execute("""
                SELECT id, اسم_المشروع, اسم_القسم
                FROM المشاريع
                WHERE معرف_العميل = %s
                ORDER BY اسم_المشروع
            """, (self.client_id,))

            projects = cursor.fetchall()

            # تحديث فلاتر المشاريع في جميع التابات
            filter_combos = [
                self.phases_project_filter,
                self.tasks_project_filter,
                self.custody_project_filter,
                self.payments_project_filter,
                self.expenses_project_filter
            ]

            for combo in filter_combos:
                if combo:
                    current_text = combo.currentText()
                    combo.clear()
                    combo.addItem("جميع المشاريع")

                    for project in projects:
                        project_display = f"{project[1]} ({project[2]})"
                        combo.addItem(project_display, project[0])

                    # استعادة الاختيار السابق
                    index = combo.findText(current_text)
                    if index >= 0:
                        combo.setCurrentIndex(index)

            conn.close()

        except Exception as e:
            print(f"خطأ في تحديث فلاتر المشاريع: {e}")

    # تحديث إحصائيات المشاريع والمقاولات
    def update_projects_statistics(self):
        if not self.client_id:
            return

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # إحصائيات المشاريع والمقاولات
            cursor.execute("""
                SELECT
                    COUNT(*) as total_count,
                    SUM(CASE WHEN اسم_القسم = 'المقاولات' THEN 1 ELSE 0 END) as contracts_count,
                    SUM(CASE WHEN الحالة = 'قيد الإنجاز' THEN 1 ELSE 0 END) as active_count,
                    COALESCE(SUM(المبلغ), 0) as total_amount,
                    COALESCE(SUM(المدفوع), 0) as paid_amount,
                    COALESCE(SUM(الباقي), 0) as remaining_amount
                FROM المشاريع
                WHERE معرف_العميل = %s
            """, (self.client_id,))

            stats = cursor.fetchone()

            if stats:
                # إعادة إنشاء البطاقات بالقيم الجديدة
                if hasattr(self, 'projects_stat_cards'):
                    # البحث عن حاوية البطاقات
                    for i in range(self.tab_widget.widget(1).layout().count()):
                        item = self.tab_widget.widget(1).layout().itemAt(i)
                        if item and item.widget() and item.widget().objectName() == "stats_container":
                            stats_container = item.widget()
                            # حذف البطاقات القديمة
                            while stats_container.layout().count():
                                child = stats_container.layout().takeAt(0)
                                if child.widget():
                                    child.widget().deleteLater()
                            
                            # إنشاء بطاقات جديدة بالقيم المحدثة
                            new_stats = [
                                ("إجمالي المشاريع", str(stats[0]), "#3498db"),
                                ("إجمالي المقاولات", str(stats[1]), "#9b59b6"),
                                ("المشاريع النشطة", str(stats[2]), "#27ae60"),
                                ("إجمالي المبالغ", f"{stats[3]:,.0f} {Currency_type}", "#8e44ad"),
                                ("المبالغ المدفوعة", f"{stats[4]:,.0f} {Currency_type}", "#27ae60"),
                                ("المبالغ المتبقية", f"{stats[5]:,.0f} {Currency_type}", "#e74c3c"),
                            ]
                            
                            for title, value, color in new_stats:
                                card = create_stat_card(title, value, color)
                                stats_container.layout().addWidget(card)
                            break

            conn.close()

        except Exception as e:
            print(f"خطأ في تحديث إحصائيات المشاريع: {e}")

    # معالج تغيير التاب - تحديث البيانات تلقائياً
    def on_tab_changed(self, index):
        try:
            # تحديث العنوان الرئيسي
            self.update_title()
            
            tab_text = self.tab_widget.tabText(index)

            if "معلومات العميل" in tab_text:
                self.load_client_info()
            elif "المشاريع والمقاولات" in tab_text:
                self.load_projects_contracts_data()
            elif "مراحل المشاريع" in tab_text:
                self.load_project_phases_data()
            elif "المهام والجداول الزمنية" in tab_text:
                self.load_tasks_data()
            elif "العهد" in tab_text:
                self.load_custody_data()
            elif "الدفعات" in tab_text:
                self.load_payments_data()
            elif "المصروفات" in tab_text:
                self.load_expenses_data()

        except Exception as e:
            print(f"خطأ في تحديث التاب: {e}")

    # تحميل بيانات مراحل المشاريع
    def load_project_phases_data(self):
        if not self.client_id:
            return

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # جلب مراحل المشاريع للعميل
            cursor.execute("""
                SELECT
                    m.id, p.اسم_المشروع, m.id as الرقم, m.اسم_المرحلة, m.وصف_المرحلة,
                    m.الوحدة, m.الكمية, m.السعر, m.الإجمالي, m.حالة_المبلغ, m.ملاحظات
                FROM المشاريع_المراحل m
                JOIN المشاريع p ON m.معرف_المشروع = p.id
                WHERE p.معرف_العميل = %s
                ORDER BY p.اسم_المشروع, m.id
            """, (self.client_id,))

            phases_data = cursor.fetchall()

            # تحديث الجدول
            self.phases_table.setRowCount(len(phases_data))

            for row, phase in enumerate(phases_data):
                for col, value in enumerate(phase):
                    if col in [6, 7, 8]:  # أعمدة الكمية والسعر والإجمالي
                        if value is not None:
                            item = QTableWidgetItem(f"{value:,.2f}")
                        else:
                            item = QTableWidgetItem("0.00")
                    else:
                        item = QTableWidgetItem(str(value) if value else "")

                    # تلوين حالة المبلغ
                    if col == 9:  # عمود حالة المبلغ
                        if value == "غير مدرج":
                            item.setForeground(QBrush(QColor(231, 76, 60)))  # أحمر
                        elif value == "تم الإدراج":
                            item.setForeground(QBrush(QColor(46, 125, 50)))  # أخضر

                    self.phases_table.setItem(row, col, item)

            # تحديث الإحصائيات
            self.update_phases_statistics()

            conn.close()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في تحميل بيانات مراحل المشاريع: {str(e)}")

    # تحديث إحصائيات مراحل المشاريع
    def update_phases_statistics(self):
        if not self.client_id:
            return

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # إحصائيات المراحل
            cursor.execute("""
                SELECT
                    COUNT(*) as total_phases,
                    COALESCE(SUM(m.الإجمالي), 0) as total_amount,
                    COALESCE(SUM(CASE WHEN m.حالة_المبلغ = 'تم الإدراج' THEN m.الإجمالي ELSE 0 END), 0) as posted_amount,
                    COALESCE(SUM(CASE WHEN m.حالة_المبلغ = 'غير مدرج' THEN m.الإجمالي ELSE 0 END), 0) as unposted_amount
                FROM المشاريع_المراحل m
                JOIN المشاريع p ON m.معرف_المشروع = p.id
                WHERE p.معرف_العميل = %s
            """, (self.client_id,))

            stats = cursor.fetchone()

            if stats:
                # إعادة إنشاء البطاقات بالقيم الجديدة
                for i in range(self.tab_widget.widget(2).layout().count()):
                    item = self.tab_widget.widget(2).layout().itemAt(i)
                    if item and item.widget() and item.widget().objectName() == "phases_stats_container":
                        stats_container = item.widget()
                        # حذف البطاقات القديمة
                        while stats_container.layout().count():
                            child = stats_container.layout().takeAt(0)
                            if child.widget():
                                child.widget().deleteLater()
                        
                        # إنشاء بطاقات جديدة بالقيم المحدثة
                        new_stats = [
                            ("إجمالي المراحل", str(stats[0]), "#3498db"),
                            ("إجمالي المبالغ", f"{stats[1]:,.0f} {Currency_type}", "#8e44ad"),
                            ("المبالغ المدرجة", f"{stats[2]:,.0f} {Currency_type}", "#27ae60"),
                            ("المبالغ غير المدرجة", f"{stats[3]:,.0f} {Currency_type}", "#e74c3c"),
                        ]
                        
                        for title, value, color in new_stats:
                            card = create_stat_card(title, value, color)
                            stats_container.layout().addWidget(card)
                        break

            conn.close()

        except Exception as e:
            print(f"خطأ في تحديث إحصائيات المراحل: {e}")

    # تحميل بيانات المهام
    def load_tasks_data(self):
        if not self.client_id:
            return

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # جلب المهام للعميل
            cursor.execute("""
                SELECT
                    mt.id, p.اسم_المشروع, mt.عنوان_المهمة, e.اسم_الموظف,
                    mt.تاريخ_البدء, mt.تاريخ_الانتهاء, mt.الحالة, mt.مبلغ_الموظف, mt.نسبة_الموظف, mt.ملاحظات
                FROM المشاريع_مهام_الفريق mt
                JOIN المشاريع p ON mt.معرف_المشروع = p.id
                LEFT JOIN الموظفين e ON mt.معرف_الموظف = e.id
                WHERE p.معرف_العميل = %s
                ORDER BY mt.تاريخ_البدء DESC
            """, (self.client_id,))

            tasks_data = cursor.fetchall()

            # تحديث الجدول
            self.tasks_table.setRowCount(len(tasks_data))

            for row, task in enumerate(tasks_data):
                for col, value in enumerate(task):
                    if col in [4, 5]:  # أعمدة التواريخ
                        if value:
                            if isinstance(value, str):
                                try:
                                    value = datetime.strptime(value, '%Y-%m-%d').date()
                                except:
                                    pass
                            if isinstance(value, date):
                                item = QTableWidgetItem(value.strftime('%d/%m/%Y'))
                            else:
                                item = QTableWidgetItem(str(value) if value else "")
                        else:
                            item = QTableWidgetItem("")
                    elif col in [7, 8]:  # أعمدة المبلغ والنسبة
                        if value is not None:
                            if col == 7:  # المبلغ
                                item = QTableWidgetItem(f"{value:,.0f}")
                            else:  # النسبة
                                item = QTableWidgetItem(f"{value}%")
                        else:
                            item = QTableWidgetItem("")
                    else:
                        item = QTableWidgetItem(str(value) if value else "")

                    self.tasks_table.setItem(row, col, item)

            # تحديث الإحصائيات
            self.update_tasks_statistics()

            conn.close()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في تحميل بيانات المهام: {str(e)}")

    # تحديث إحصائيات المهام
    def update_tasks_statistics(self):
        if not self.client_id:
            return

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # إحصائيات المهام
            cursor.execute("""
                SELECT
                    COUNT(*) as total_tasks,
                    SUM(CASE WHEN mt.الحالة = 'مكتمل' THEN 1 ELSE 0 END) as completed_tasks,
                    SUM(CASE WHEN mt.الحالة = 'قيد التنفيذ' THEN 1 ELSE 0 END) as in_progress_tasks,
                    SUM(CASE WHEN mt.الحالة = 'لم يبدأ' THEN 1 ELSE 0 END) as pending_tasks,
                    COALESCE(SUM(mt.مبلغ_الموظف), 0) as total_amount
                FROM المشاريع_مهام_الفريق mt
                JOIN المشاريع p ON mt.معرف_المشروع = p.id
                WHERE p.معرف_العميل = %s
            """, (self.client_id,))

            stats = cursor.fetchone()

            if stats:
                # إعادة إنشاء البطاقات بالقيم الجديدة
                for i in range(self.tab_widget.widget(3).layout().count()):
                    item = self.tab_widget.widget(3).layout().itemAt(i)
                    if item and item.widget() and item.widget().objectName() == "tasks_stats_container":
                        stats_container = item.widget()
                        # حذف البطاقات القديمة
                        while stats_container.layout().count():
                            child = stats_container.layout().takeAt(0)
                            if child.widget():
                                child.widget().deleteLater()
                        
                        # إنشاء بطاقات جديدة بالقيم المحدثة
                        new_stats = [
                            ("إجمالي المهام", str(stats[0]), "#3498db"),
                            ("المهام المكتملة", str(stats[1]), "#27ae60"),
                            ("المهام قيد التنفيذ", str(stats[2]), "#f39c12"),
                            ("المهام المعلقة", str(stats[3]), "#e74c3c"),
                            ("إجمالي المبالغ", f"{stats[4]:,.0f} {Currency_type}", "#8e44ad"),
                        ]
                        
                        for title, value, color in new_stats:
                            card = create_stat_card(title, value, color)
                            stats_container.layout().addWidget(card)
                        break

            conn.close()

        except Exception as e:
            print(f"خطأ في تحديث إحصائيات المهام: {e}")

    # Event handlers for quick actions
    # تعديل بيانات العميل
    def edit_client_data(self):
        try:
            from الأدوات import AddEntryDialog

            dialog = AddEntryDialog(
                main_window=self.parent,
                section_name="العملاء",
                parent=self,
                entry_data=self.client_data,
                row_id=self.client_id
            )

            if dialog.exec() == QDialog.Accepted:
                self.load_client_info()
                if hasattr(self.parent, 'show_section'):
                    self.parent.show_section("العملاء")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في فتح نافذة تعديل العميل: {str(e)}")

    # إضافة مشروع جديد للعميل
    def add_new_project(self):
        try:
            from الأدوات import AddEntryDialog

            # إعداد بيانات المشروع الجديد مع معرف العميل
            project_data = {"معرف_العميل": self.client_id}

            dialog = AddEntryDialog(
                main_window=self.parent,
                section_name="المشاريع",
                parent=self,
                entry_data=project_data
            )

            if dialog.exec() == QDialog.Accepted:
                self.load_projects_contracts_data()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في فتح نافذة إضافة المشروع: {str(e)}")

    # عرض تقارير العميل
    def view_client_reports(self):
        QMessageBox.information(self, "التقارير", "سيتم تطوير نظام التقارير قريباً")

    # تحميل بيانات العهد
    def load_custody_data(self):
        if not self.client_id:
            return

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # جلب العهد للعميل
            cursor.execute("""
                SELECT
                    c.id, p.اسم_المشروع, c.وصف_العهدة, c.مبلغ_العهدة,
                    COALESCE((SELECT SUM(m.المبلغ) FROM المقاولات_مصروفات_العهد m WHERE m.معرف_العهدة = c.id), 0) as المصروف,
                    c.مبلغ_العهدة - COALESCE((SELECT SUM(m.المبلغ) FROM المقاولات_مصروفات_العهد m WHERE m.معرف_العهدة = c.id), 0) as المتبقي,
                    '', c.تاريخ_الإستلام, '', c.حالة_العهدة, c.ملاحظات
                FROM المقاولات_العهد c
                JOIN المشاريع p ON c.معرف_المشروع = p.id
                WHERE p.معرف_العميل = %s
                ORDER BY c.تاريخ_الإستلام DESC
            """, (self.client_id,))

            custody_data = cursor.fetchall()

            # تحديث الجدول
            self.custody_table.setRowCount(len(custody_data))

            for row, custody in enumerate(custody_data):
                for col, value in enumerate(custody):
                    if col in [3, 4, 5]:  # أعمدة المبالغ
                        if value is not None:
                            item = QTableWidgetItem(f"{value:,.0f}")
                        else:
                            item = QTableWidgetItem("0")
                    elif col in [7, 8]:  # أعمدة التواريخ
                        if value:
                            if isinstance(value, str):
                                try:
                                    value = datetime.strptime(value, '%Y-%m-%d').date()
                                except:
                                    pass
                            if isinstance(value, date):
                                item = QTableWidgetItem(value.strftime('%d/%m/%Y'))
                            else:
                                item = QTableWidgetItem(str(value) if value else "")
                        else:
                            item = QTableWidgetItem("")
                    else:
                        item = QTableWidgetItem(str(value) if value else "")

                    self.custody_table.setItem(row, col, item)

            # تحديث الإحصائيات
            self.update_custody_statistics()

            conn.close()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في تحميل بيانات العهد: {str(e)}")

    # تحديث إحصائيات العهد
    def update_custody_statistics(self):
        if not self.client_id:
            return

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # إحصائيات العهد
            cursor.execute("""
                SELECT
                    COUNT(*) as total_custody,
                    SUM(CASE WHEN c.حالة_العهدة = 'مفتوحة' THEN 1 ELSE 0 END) as active_custody,
                    COALESCE(SUM(c.مبلغ_العهدة), 0) as total_amount,
                    COALESCE(SUM((SELECT SUM(m.المبلغ) FROM المقاولات_مصروفات_العهد m WHERE m.معرف_العهدة = c.id)), 0) as total_expenses,
                    COALESCE(SUM(c.مبلغ_العهدة - COALESCE((SELECT SUM(m.المبلغ) FROM المقاولات_مصروفات_العهد m WHERE m.معرف_العهدة = c.id), 0)), 0) as total_remaining
                FROM المقاولات_العهد c
                JOIN المشاريع p ON c.معرف_المشروع = p.id
                WHERE p.معرف_العميل = %s
            """, (self.client_id,))

            stats = cursor.fetchone()

            if stats:
                # إعادة إنشاء البطاقات بالقيم الجديدة
                for i in range(self.tab_widget.widget(4).layout().count()):
                    item = self.tab_widget.widget(4).layout().itemAt(i)
                    if item and item.widget() and item.widget().objectName() == "custody_stats_container":
                        stats_container = item.widget()
                        # حذف البطاقات القديمة
                        while stats_container.layout().count():
                            child = stats_container.layout().takeAt(0)
                            if child.widget():
                                child.widget().deleteLater()
                        
                        # إنشاء بطاقات جديدة بالقيم المحدثة
                        new_stats = [
                            ("إجمالي العهد", str(stats[0]), "#3498db"),
                            ("العهد النشطة", str(stats[1]), "#27ae60"),
                            ("إجمالي المبالغ", f"{stats[2]:,.0f} {Currency_type}", "#8e44ad"),
                            ("إجمالي المصروفات", f"{stats[3]:,.0f} {Currency_type}", "#e74c3c"),
                            ("إجمالي المتبقي", f"{stats[4]:,.0f} {Currency_type}", "#f39c12"),
                        ]
                        
                        for title, value, color in new_stats:
                            card = create_stat_card(title, value, color)
                            stats_container.layout().addWidget(card)
                        break

            conn.close()

        except Exception as e:
            print(f"خطأ في تحديث إحصائيات العهد: {e}")

    # تحميل بيانات الدفعات
    def load_payments_data(self):
        if not self.client_id:
            return

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # جلب الدفعات للعميل
            cursor.execute("""
                SELECT
                    pm.id, p.اسم_المشروع, pm.المبلغ_المدفوع, pm.تاريخ_الدفع, pm.طريقة_الدفع,
                    '', '', pm.وصف_المدفوع
                FROM المشاريع_المدفوعات pm
                JOIN المشاريع p ON pm.معرف_المشروع = p.id
                WHERE p.معرف_العميل = %s
                ORDER BY pm.تاريخ_الدفع DESC
            """, (self.client_id,))

            payments_data = cursor.fetchall()

            # تحديث الجدول
            self.payments_table.setRowCount(len(payments_data))

            for row, payment in enumerate(payments_data):
                for col, value in enumerate(payment):
                    if col == 2:  # عمود المبلغ
                        if value is not None:
                            item = QTableWidgetItem(f"{value:,.0f}")
                        else:
                            item = QTableWidgetItem("0")
                    elif col == 3:  # عمود التاريخ
                        if value:
                            if isinstance(value, str):
                                try:
                                    value = datetime.strptime(value, '%Y-%m-%d').date()
                                except:
                                    pass
                            if isinstance(value, date):
                                item = QTableWidgetItem(value.strftime('%d/%m/%Y'))
                            else:
                                item = QTableWidgetItem(str(value) if value else "")
                        else:
                            item = QTableWidgetItem("")
                    else:
                        item = QTableWidgetItem(str(value) if value else "")

                    self.payments_table.setItem(row, col, item)

            # تحديث الإحصائيات
            self.update_payments_statistics()

            conn.close()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في تحميل بيانات الدفعات: {str(e)}")

    # تحديث إحصائيات الدفعات
    def update_payments_statistics(self):
        if not self.client_id:
            return

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # إحصائيات الدفعات
            cursor.execute("""
                SELECT
                    COUNT(*) as total_payments,
                    COALESCE(SUM(pm.المبلغ_المدفوع), 0) as total_amount,
                    COALESCE(SUM(CASE WHEN pm.طريقة_الدفع = 'نقدي' THEN pm.المبلغ_المدفوع ELSE 0 END), 0) as cash_amount,
                    COALESCE(SUM(CASE WHEN pm.طريقة_الدفع = 'تحويل بنكي' THEN pm.المبلغ_المدفوع ELSE 0 END), 0) as bank_amount,
                    COALESCE(SUM(CASE WHEN MONTH(pm.تاريخ_الدفع) = MONTH(CURDATE()) AND YEAR(pm.تاريخ_الدفع) = YEAR(CURDATE()) THEN pm.المبلغ_المدفوع ELSE 0 END), 0) as this_month_amount
                FROM المشاريع_المدفوعات pm
                JOIN المشاريع p ON pm.معرف_المشروع = p.id
                WHERE p.معرف_العميل = %s
            """, (self.client_id,))

            stats = cursor.fetchone()

            if stats:
                # إعادة إنشاء البطاقات بالقيم الجديدة
                for i in range(self.tab_widget.widget(5).layout().count()):
                    item = self.tab_widget.widget(5).layout().itemAt(i)
                    if item and item.widget() and item.widget().objectName() == "payments_stats_container":
                        stats_container = item.widget()
                        # حذف البطاقات القديمة
                        while stats_container.layout().count():
                            child = stats_container.layout().takeAt(0)
                            if child.widget():
                                child.widget().deleteLater()
                        
                        # إنشاء بطاقات جديدة بالقيم المحدثة
                        new_stats = [
                            ("إجمالي الدفعات", str(stats[0]), "#3498db"),
                            ("إجمالي المبالغ", f"{stats[1]:,.0f} {Currency_type}", "#27ae60"),
                            ("الدفعات النقدية", f"{stats[2]:,.0f} {Currency_type}", "#f39c12"),
                            ("التحويلات البنكية", f"{stats[3]:,.0f} {Currency_type}", "#8e44ad"),
                            ("دفعات هذا الشهر", f"{stats[4]:,.0f} {Currency_type}", "#16a085"),
                        ]
                        
                        for title, value, color in new_stats:
                            card = create_stat_card(title, value, color)
                            stats_container.layout().addWidget(card)
                        break

            conn.close()

        except Exception as e:
            print(f"خطأ في تحديث إحصائيات الدفعات: {e}")

    # تحميل بيانات المصروفات
    def load_expenses_data(self):
        if not self.client_id:
            return

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # جلب المصروفات للعميل (من جدول الحسابات العامة)
            cursor.execute("""
                SELECT
                    h.id, 'عام' as اسم_المشروع, h.المصروف, h.المبلغ, h.تاريخ_المصروف,
                    h.التصنيف, h.رقم_الفاتورة, 'معتمد' as الحالة, h.ملاحظات
                FROM الحسابات h
                WHERE h.المستلم LIKE CONCAT('%', (SELECT اسم_العميل FROM العملاء WHERE id = %s), '%')
                   OR h.ملاحظات LIKE CONCAT('%', (SELECT اسم_العميل FROM العملاء WHERE id = %s), '%')
                ORDER BY h.تاريخ_المصروف DESC
            """, (self.client_id, self.client_id))

            expenses_data = cursor.fetchall()

            # تحديث الجدول
            self.expenses_table.setRowCount(len(expenses_data))

            for row, expense in enumerate(expenses_data):
                for col, value in enumerate(expense):
                    if col == 3:  # عمود المبلغ
                        if value is not None:
                            item = QTableWidgetItem(f"{value:,.0f}")
                        else:
                            item = QTableWidgetItem("0")
                    elif col == 4:  # عمود التاريخ
                        if value:
                            if isinstance(value, str):
                                try:
                                    value = datetime.strptime(value, '%Y-%m-%d').date()
                                except:
                                    pass
                            if isinstance(value, date):
                                item = QTableWidgetItem(value.strftime('%d/%m/%Y'))
                            else:
                                item = QTableWidgetItem(str(value) if value else "")
                        else:
                            item = QTableWidgetItem("")
                    else:
                        item = QTableWidgetItem(str(value) if value else "")

                    self.expenses_table.setItem(row, col, item)

            # تحديث الإحصائيات
            self.update_expenses_statistics()

            conn.close()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في تحميل بيانات المصروفات: {str(e)}")

    # تحديث إحصائيات المصروفات
    def update_expenses_statistics(self):
        if not self.client_id:
            return

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # إحصائيات المصروفات
            cursor.execute("""
                SELECT
                    COUNT(*) as total_expenses,
                    COALESCE(SUM(h.المبلغ), 0) as total_amount,
                    COALESCE(SUM(h.المبلغ), 0) as approved_amount,
                    0 as pending_amount,
                    COALESCE(SUM(CASE WHEN MONTH(h.تاريخ_المصروف) = MONTH(CURDATE()) AND YEAR(h.تاريخ_المصروف) = YEAR(CURDATE()) THEN h.المبلغ ELSE 0 END), 0) as this_month_amount
                FROM الحسابات h
                WHERE h.المستلم LIKE CONCAT('%', (SELECT اسم_العميل FROM العملاء WHERE id = %s), '%')
                   OR h.ملاحظات LIKE CONCAT('%', (SELECT اسم_العميل FROM العملاء WHERE id = %s), '%')
            """, (self.client_id, self.client_id))

            stats = cursor.fetchone()

            if stats:
                # إعادة إنشاء البطاقات بالقيم الجديدة
                for i in range(self.tab_widget.widget(6).layout().count()):
                    item = self.tab_widget.widget(6).layout().itemAt(i)
                    if item and item.widget() and item.widget().objectName() == "expenses_stats_container":
                        stats_container = item.widget()
                        # حذف البطاقات القديمة
                        while stats_container.layout().count():
                            child = stats_container.layout().takeAt(0)
                            if child.widget():
                                child.widget().deleteLater()
                        
                        # إنشاء بطاقات جديدة بالقيم المحدثة
                        new_stats = [
                            ("إجمالي المصروفات", str(stats[0]), "#3498db"),
                            ("إجمالي المبالغ", f"{stats[1]:,.0f} {Currency_type}", "#e74c3c"),
                            ("المصروفات المعتمدة", f"{stats[2]:,.0f} {Currency_type}", "#27ae60"),
                            ("المصروفات المعلقة", f"{stats[3]:,.0f} {Currency_type}", "#f39c12"),
                            ("مصروفات هذا الشهر", f"{stats[4]:,.0f} {Currency_type}", "#8e44ad"),
                        ]
                        
                        for title, value, color in new_stats:
                            card = create_stat_card(title, value, color)
                            stats_container.layout().addWidget(card)
                        break

            conn.close()

        except Exception as e:
            print(f"خطأ في تحديث إحصائيات المصروفات: {e}")

    # Helper function for filtering
    # دالة مساعدة لتطبيق الفلاتر على الجداول مع دعم البحث النصي المحسن
    def apply_table_filter(self, table, search_text="", filters=None, search_columns=None):
        try:
            if table is None:
                return

            # إذا لم يتم تمرير فلاتر، استخدم قاموس فارغ
            if filters is None:
                filters = {}

            # إذا لم يتم تحديد أعمدة البحث، ابحث في جميع الأعمدة
            if search_columns is None:
                search_columns = list(range(table.columnCount()))

            # تطبيق الفلترة على كل صف
            visible_rows = 0
            for row in range(table.rowCount()):
                show_row = True

                # فحص الفلاتر المحددة
                for column, filter_value in filters.items():
                    if filter_value and filter_value != "الكل" and filter_value != "جميع المشاريع":
                        item = table.item(row, column)
                        if item is None:
                            show_row = False
                            break

                        # للمشاريع، تحقق من النص المعروض أو النص الأساسي
                        item_text = item.text()
                        if filter_value not in item_text and item_text != filter_value:
                            show_row = False
                            break

                # فحص البحث النصي إذا كان موجوداً
                if show_row and search_text:
                    search_match = False
                    search_terms = search_text.lower().split()  # دعم البحث بكلمات متعددة

                    for col in search_columns:
                        if col < table.columnCount():
                            item = table.item(row, col)
                            if item:
                                item_text = item.text().lower()
                                # تحقق من وجود جميع كلمات البحث
                                if all(term in item_text for term in search_terms):
                                    search_match = True
                                    break

                    if not search_match:
                        show_row = False

                # إظهار أو إخفاء الصف
                table.setRowHidden(row, not show_row)
                if show_row:
                    visible_rows += 1

            # تحديث شريط الحالة أو عرض عدد النتائج (اختياري)
            # يمكن إضافة هذا لاحقاً إذا لزم الأمر

        except Exception as e:
            print(f"خطأ في تطبيق الفلتر: {e}")

    # Filter functions
    # فلترة المشاريع والمقاولات
    def filter_projects_contracts(self):
        try:
            if not hasattr(self, 'projects_table') or self.projects_table is None:
                return

            # جمع قيم الفلاتر
            project_type = self.project_type_filter.currentText()
            project_status = self.project_status_filter.currentText()
            search_text = self.projects_search.text().strip()

            # تحديد الفلاتر حسب الأعمدة
            filters = {}

            # فلتر نوع المشروع (عمود اسم_القسم - العمود 1)
            if project_type != "الكل":
                if project_type == "المشاريع":
                    filters[1] = "المشاريع"
                elif project_type == "المقاولات":
                    filters[1] = "المقاولات"

            # فلتر الحالة (عمود الحالة - العمود 9)
            if project_status != "الكل":
                filters[9] = project_status

            # تحديد أعمدة البحث (اسم المشروع، التصنيف، ملاحظات)
            search_columns = [2, 3, 10]  # اسم المشروع، التصنيف، ملاحظات

            # تطبيق الفلاتر
            self.apply_table_filter(self.projects_table, search_text, filters, search_columns)

        except Exception as e:
            print(f"خطأ في فلترة المشاريع والمقاولات: {e}")

    # فلترة مراحل المشاريع
    def filter_project_phases(self):
        try:
            if not hasattr(self, 'phases_table') or self.phases_table is None:
                return

            # جمع قيم الفلاتر
            selected_project = self.phases_project_filter.currentText()
            amount_status = self.phases_amount_status_filter.currentText()
            search_text = self.phases_search.text().strip()

            # تحديد الفلاتر حسب الأعمدة
            filters = {}

            # فلتر المشروع (عمود المشروع - العمود 1)
            if selected_project != "جميع المشاريع":
                # استخراج اسم المشروع من النص المعروض
                project_name = selected_project.split(" (")[0] if " (" in selected_project else selected_project
                filters[1] = project_name

            # فلتر حالة المبلغ (عمود حالة_المبلغ - العمود 9)
            if amount_status != "الكل":
                filters[9] = amount_status

            # تحديد أعمدة البحث (اسم المرحلة، وصف المرحلة، ملاحظات)
            search_columns = [3, 4, 10]  # اسم المرحلة، وصف المرحلة، ملاحظات

            # تطبيق الفلاتر
            self.apply_table_filter(self.phases_table, search_text, filters, search_columns)

        except Exception as e:
            print(f"خطأ في فلترة مراحل المشاريع: {e}")

    # فلترة المهام
    def filter_tasks(self):
        try:
            if not hasattr(self, 'tasks_table') or self.tasks_table is None:
                return

            # جمع قيم الفلاتر
            selected_project = self.tasks_project_filter.currentText()
            task_status = self.tasks_status_filter.currentText()
            search_text = self.tasks_search.text().strip()

            # تحديد الفلاتر حسب الأعمدة
            filters = {}

            # فلتر المشروع (عمود المشروع - العمود 1)
            if selected_project != "جميع المشاريع":
                project_name = selected_project.split(" (")[0] if " (" in selected_project else selected_project
                filters[1] = project_name

            # فلتر حالة المهمة (عمود الحالة - العمود 6)
            if task_status != "الكل":
                filters[6] = task_status

            # تحديد أعمدة البحث (عنوان المهمة، الموظف، ملاحظات)
            search_columns = [2, 3, 9]  # عنوان المهمة، الموظف، ملاحظات

            # تطبيق الفلاتر
            self.apply_table_filter(self.tasks_table, search_text, filters, search_columns)

        except Exception as e:
            print(f"خطأ في فلترة المهام: {e}")

    # فلترة العهد
    def filter_custody(self):
        try:
            if not hasattr(self, 'custody_table') or self.custody_table is None:
                return

            # جمع قيم الفلاتر
            selected_project = self.custody_project_filter.currentText()
            custody_status = self.custody_status_filter.currentText()
            search_text = self.custody_search.text().strip()

            # تحديد الفلاتر حسب الأعمدة
            filters = {}

            # فلتر المشروع (عمود المشروع - العمود 1)
            if selected_project != "جميع المشاريع":
                project_name = selected_project.split(" (")[0] if " (" in selected_project else selected_project
                filters[1] = project_name

            # فلتر حالة العهدة (عمود الحالة - العمود 9)
            if custody_status != "الكل":
                filters[9] = custody_status

            # تحديد أعمدة البحث (وصف العهدة، المسؤول، ملاحظات)
            search_columns = [2, 6, 10]  # وصف العهدة، المسؤول، ملاحظات

            # تطبيق الفلاتر
            self.apply_table_filter(self.custody_table, search_text, filters, search_columns)

        except Exception as e:
            print(f"خطأ في فلترة العهد: {e}")

    # فلترة الدفعات
    def filter_payments(self):
        try:
            if not hasattr(self, 'payments_table') or self.payments_table is None:
                return

            # جمع قيم الفلاتر
            selected_project = self.payments_project_filter.currentText()
            payment_method = self.payment_method_filter.currentText()
            search_text = self.payments_search.text().strip()

            # تحديد الفلاتر حسب الأعمدة
            filters = {}

            # فلتر المشروع (عمود المشروع - العمود 1)
            if selected_project != "جميع المشاريع":
                project_name = selected_project.split(" (")[0] if " (" in selected_project else selected_project
                filters[1] = project_name

            # فلتر طريقة الدفع (عمود طريقة الدفع - العمود 4)
            if payment_method != "الكل":
                filters[4] = payment_method

            # تحديد أعمدة البحث (رقم المرجع، وصف الدفعة)
            search_columns = [5, 7]  # رقم المرجع، وصف الدفعة

            # تطبيق الفلاتر
            self.apply_table_filter(self.payments_table, search_text, filters, search_columns)

        except Exception as e:
            print(f"خطأ في فلترة الدفعات: {e}")

    # فلترة المصروفات
    def filter_expenses(self):
        try:
            if not hasattr(self, 'expenses_table') or self.expenses_table is None:
                return

            # جمع قيم الفلاتر
            selected_project = self.expenses_project_filter.currentText()
            expense_type = self.expense_type_filter.currentText()
            expense_approval = self.expense_approval_filter.currentText()
            search_text = self.expenses_search.text().strip()

            # تحديد الفلاتر حسب الأعمدة
            filters = {}

            # فلتر المشروع (عمود المشروع - العمود 1)
            if selected_project != "جميع المشاريع":
                project_name = selected_project.split(" (")[0] if " (" in selected_project else selected_project
                filters[1] = project_name

            # فلتر نوع المصروف (عمود النوع - العمود 5)
            if expense_type != "الكل":
                filters[5] = expense_type

            # فلتر حالة الموافقة (عمود الحالة - العمود 7)
            if expense_approval != "الكل":
                filters[7] = expense_approval

            # تحديد أعمدة البحث (وصف المصروف، رقم الفاتورة، ملاحظات)
            search_columns = [2, 6, 8]  # وصف المصروف، رقم الفاتورة، ملاحظات

            # تطبيق الفلاتر
            self.apply_table_filter(self.expenses_table, search_text, filters, search_columns)

        except Exception as e:
            print(f"خطأ في فلترة المصروفات: {e}")

    # Double-click event handlers
    # معالج النقر المزدوج على جدول المشاريع
    def on_projects_table_double_click(self, item):
        try:
            row = item.row()
            project_id = self.projects_table.item(row, 0).text()

            # جلب بيانات المشروع
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM المشاريع WHERE id = %s", (project_id,))
            project_data = cursor.fetchone()
            conn.close()

            if project_data:
                # فتح نافذة إدارة المشروع
                #from إدارة_المشروع import open_project_phases_window
                project_type = project_data.get('اسم_القسم', 'المشاريع')
                open_project_phases_window(self, project_data, project_type)

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في فتح نافذة المشروع: {str(e)}")

    # معالج النقر المزدوج على جدول المراحل
    def on_phases_table_double_click(self, item):
        QMessageBox.information(self, "المراحل", "سيتم تطوير نافذة تفاصيل المرحلة قريباً")

    # معالج النقر المزدوج على جدول المهام
    def on_tasks_table_double_click(self, item):
        QMessageBox.information(self, "المهام", "سيتم تطوير نافذة تفاصيل المهمة قريباً")

    # معالج النقر المزدوج على جدول العهد
    def on_custody_table_double_click(self, item):
        QMessageBox.information(self, "العهد", "سيتم تطوير نافذة تفاصيل العهدة قريباً")

    # معالج النقر المزدوج على جدول الدفعات
    def on_payments_table_double_click(self, item):
        QMessageBox.information(self, "الدفعات", "سيتم تطوير نافذة تفاصيل الدفعة قريباً")

    # معالج النقر المزدوج على جدول المصروفات
    def on_expenses_table_double_click(self, item):
        QMessageBox.information(self, "المصروفات", "سيتم تطوير نافذة تفاصيل المصروف قريباً")

    # Additional action handlers
    # إضافة مشروع للعميل
    def add_project_for_client(self):
        try:
            from الأدوات import AddEntryDialog

            # إعداد بيانات المشروع الجديد مع معرف العميل
            project_data = {"معرف_العميل": self.client_id, "اسم_القسم": "المشاريع"}

            dialog = AddEntryDialog(
                main_window=self.parent,
                section_name="المشاريع",
                parent=self,
                entry_data=project_data
            )

            if dialog.exec() == QDialog.Accepted:
                self.load_projects_contracts_data()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في فتح نافذة إضافة المشروع: {str(e)}")

    # إضافة مشروع جديد - دالة مساعدة
    def add_new_project(self):
        self.add_project_for_client()

    # إضافة مقاولات للعميل
    def add_contract_for_client(self):
        try:
            from الأدوات import AddEntryDialog

            # إعداد بيانات المقاولات الجديدة مع معرف العميل
            contract_data = {"معرف_العميل": self.client_id, "اسم_القسم": "المقاولات"}

            dialog = AddEntryDialog(
                main_window=self.parent,
                section_name="المقاولات",
                parent=self,
                entry_data=contract_data
            )

            if dialog.exec() == QDialog.Accepted:
                self.load_projects_contracts_data()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في فتح نافذة إضافة المقاولات: {str(e)}")

    # حذف دوال التنسيق المخصصة - يتم استخدام format_currency و format_date من ملف الستايلات

    # عرض رسالة نجاح
    def show_success_message(self, title, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

    # عرض رسالة خطأ
    def show_error_message(self, title, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

    # تأكيد الإجراء
    def confirm_action(self, title, message):
        reply = QMessageBox.question(
            self, title, message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes


# دالة اختبار لنافذة إدارة العملاء
def main():
    app = QApplication(sys.argv)

    # بيانات عميل تجريبية للاختبار
    test_client_data = {
        'id': 1,
        'اسم_العميل': 'عميل تجريبي',
        'التصنيف': 'شركة',
        'رقم_الهاتف': '0501234567',
        'الإيميل': 'test@example.com',
        'العنوان': 'الرياض، المملكة العربية السعودية',
        'تاريخ_الإنشاء': '2024-01-01',
        'آخر_تحديث': '2024-01-15',
        'ملاحظات': 'عميل تجريبي لاختبار النظام'
    }

    window = ClientManagementWindow(client_data=test_client_data)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

# دالة مساعدة لفتح نافذة إدارة العميل
# فتح نافذة إدارة العميل
def open_client_management_window(parent, client_data):
    window = ClientManagementWindow(parent, client_data)
    window.exec()
    return window

# دالة مساعدة لإنشاء بطاقة عميل في النظام الرئيسي
# إنشاء بطاقة عميل للعرض في النظام الرئيسي
def create_client_card(client_data):
    return ModernCard(client_data, card_type="client")

# دالة مساعدة للتحقق من صحة بيانات العميل
# التحقق من صحة بيانات العميل
def validate_client_data(client_data):
    required_fields = ['اسم_العميل']

    for field in required_fields:
        if not client_data.get(field):
            return False, f"الحقل {field} مطلوب"

    # التحقق من صحة الإيميل إذا تم إدخاله
    email = client_data.get('الإيميل')
    if email:
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "صيغة الإيميل غير صحيحة"

    return True, "البيانات صحيحة"
