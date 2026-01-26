#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نافذة إدارة الموظفين الشاملة
تحتوي على جميع التابات المطلوبة لإدارة الموظف بشكل كامل

التحسينات المطبقة على الأنماط:
- تجميع جميع الأنماط (styles) في دالة مركزية واحدة
- استخدام setObjectName() لتعيين أسماء فريدة للعناصر
- إزالة جميع استدعاءات setStyleSheet() المتناثرة
- تطبيق أنماط ديناميكية بناءً على قيم البيانات
- دعم كامل للغة العربية والتخطيط من اليمين إلى اليسار (RTL)
- تنظيم الأنماط حسب نوع العنصر (أزرار، إطارات، جداول، إلخ)
- تقليل التكرار في الكود وتحسين قابلية الصيانة
- استخدام أسماء كائنات موحدة للعناصر المتشابهة
"""

import sys
import os
from datetime import datetime, date, timedelta
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import mysql.connector

# إضافة المسار الحالي
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from الإعدادات_العامة import *
from ستايل import apply_stylesheet
from ستايل_نوافذ_الإدارة import (
    apply_to_employee_management, setup_table_style, create_stat_card,
    get_status_color, format_currency, format_date, apply_management_style
)
from قائمة_الجداول import setup_table_context_menu
from متغيرات import *
from مساعد_أزرار_الطباعة import quick_add_print_button

# نافذة شاملة لإدارة الموظف
class EmployeeManagementWindow(QDialog):
    
    # init
    def __init__(self, parent=None, employee_data=None):
        super().__init__(parent)
        self.parent = parent
        self.employee_data = employee_data or {}
        self.employee_id = self.employee_data.get('id', None)
        
        # إعداد النافذة الأساسية
        self.setup_window()
        
        # إنشاء التابات
        self.create_tabs()
        
        # تحميل البيانات
        self.load_employee_info()
        
        # تطبيق الأنماط الموحدة
        apply_to_employee_management(self)

        # إضافة أزرار الطباعة لجميع التابات
        self.add_print_buttons()

    # إعداد النافذة الأساسية
    def setup_window(self):
        employee_name = self.employee_data.get('اسم_الموظف', 'موظف جديد')
        self.setWindowTitle(f"إدارة الموظف - {employee_name}")
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
        
    # تحديث العنوان الرئيسي ليعكس التاب الحالي
    def update_title(self):
        try:
            employee_name = self.employee_data.get('اسم_الموظف', 'موظف جديد')
            current_tab_index = self.tab_widget.currentIndex()
            
            if current_tab_index >= 0:
                tab_text = self.tab_widget.tabText(current_tab_index)
                # إزالة أيقونات HTML من نص التاب إذا كانت موجودة
                import re
                clean_tab_text = re.sub(r'<[^>]+>', '', tab_text)
                title_text = f"إدارة موظف {employee_name} - {clean_tab_text}"
            else:
                title_text = f"إدارة موظف {employee_name}"
            
            self.title_label.setText(title_text)
            
        except Exception as e:
            print(f"خطأ في تحديث العنوان: {e}")
            self.title_label.setText("إدارة الموظفين")
        
    # إنشاء التابات
    def create_tabs(self):
        # تاب معلومات الموظف
        self.create_employee_info_tab()
        
        # تاب المعاملات المالية
        self.create_financial_transactions_tab()
        
        # تاب مهام الموظف
        self.create_employee_tasks_tab()
        
        # تاب الحضور والانصراف
        self.create_attendance_tab()
        
        # تاب التقييم
        self.create_evaluation_tab()

        # ربط إشارة تغيير التاب بدالة التحديث التلقائي
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # تحديث العنوان الأولي
        self.update_title()

    # معالج تغيير التاب - تحديث البيانات تلقائياً
    def on_tab_changed(self, index):
        try:
            # تحديث العنوان الرئيسي
            self.update_title()
            
            tab_name = self.tab_widget.tabText(index)
            
            if tab_name == "معلومات الموظف":
                self.load_employee_info()
            elif tab_name == "المعاملات المالية":
                self.load_financial_transactions_data()
            elif tab_name == "مهام الموظف":
                self.load_employee_tasks_data()
                self.load_tasks_stats()  # تحديث إحصائيات المهام
            elif tab_name == "الحضور والانصراف":
                self.load_attendance_data()
                self.update_attendance_stats()  # تحديث إحصائيات الحضور
            elif tab_name == "التقييم":
                self.load_evaluation_data()
                self.update_evaluation_stats()  # تحديث إحصائيات التقييم
                
        except Exception as e:
            print(f"خطأ في تحديث التاب: {e}")

    # إنشاء تاب معلومات الموظف
    def create_employee_info_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # إنشاء منطقة التمرير
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # الحاوية الرئيسية للمحتوى
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(20)

        # الحاويات الثلاث الأفقية
        self.create_three_containers_section(content_layout)

        # قسم آخر العمليات وأزرار الحضور السريعة
        self.create_recent_activities_section(content_layout)

        # قسم الإحصائيات
        self.create_employee_info_stats_section(content_layout)

        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        self.tab_widget.addTab(tab, "معلومات الموظف")

    # إنشاء الحاويات الثلاث الأفقية
    def create_three_containers_section(self, parent_layout):
        containers_layout = QHBoxLayout()
        containers_layout.setSpacing(15)

        # الحاوية الأولى - المعلومات الأساسية
        self.create_basic_info_container(containers_layout)

        # الحاوية الثانية - المعلومات المالية
        self.create_financial_info_container(containers_layout)

        # الحاوية الثالثة - المعلومات الإضافية
        self.create_additional_info_container(containers_layout)

        parent_layout.addLayout(containers_layout)

    # إنشاء حاوية المعلومات الأساسية
    def create_basic_info_container(self, parent_layout):
        group_box = QGroupBox("المعلومات الأساسية")
        group_box.setObjectName("info-group")

        layout = QVBoxLayout(group_box)
        layout.setSpacing(12)

        # المعلومات الأساسية
        self.employee_name_label = QLabel("غير محدد")
        self.employee_job_label = QLabel("غير محدد")
        self.employee_phone_label = QLabel("غير محدد")
        self.employee_address_label = QLabel("غير محدد")

        # تنسيق التسميات
        basic_info_items = [
            ("اسم الموظف:", self.employee_name_label),
            ("الوظيفة:", self.employee_job_label),
            ("رقم الهاتف:", self.employee_phone_label),
            ("العنوان:", self.employee_address_label),
        ]

        for label_text, value_label in basic_info_items:
            item_layout = QHBoxLayout()
            item_layout.setSpacing(10)

            title_label = QLabel(label_text)
            title_label.setObjectName("title-label")
            title_label.setFixedWidth(80)

            value_label.setObjectName("value-label")

            item_layout.addWidget(title_label)
            item_layout.addWidget(value_label)
            layout.addLayout(item_layout)

        # زر تعديل بيانات الموظف
        edit_employee_btn = QPushButton("تعديل بيانات الموظف")
        edit_employee_btn.setIcon(QIcon("icons/edit.png") if os.path.exists("icons/edit.png") else self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        edit_employee_btn.clicked.connect(self.edit_employee_data)
        edit_employee_btn.setObjectName("edit-btn")

        layout.addStretch()
        layout.addWidget(edit_employee_btn)

        parent_layout.addWidget(group_box)

    # إنشاء حاوية المعلومات المالية
    def create_financial_info_container(self, parent_layout):
        group_box = QGroupBox("المعلومات المالية")
        group_box.setObjectName("info-group")

        layout = QVBoxLayout(group_box)
        layout.setSpacing(12)

        # المعلومات المالية
        self.employee_hire_date_label = QLabel("غير محدد")
        self.employee_salary_label = QLabel("غير محدد")
        self.employee_percentage_label = QLabel("غير محدد")
        self.employee_balance_label = QLabel("غير محدد")

        # تنسيق التسميات
        financial_info_items = [
            ("تاريخ المباشرة:", self.employee_hire_date_label),
            ("المرتب:", self.employee_salary_label),
            ("النسبة:", self.employee_percentage_label),
            ("الرصيد الحالي:", self.employee_balance_label),
        ]

        for label_text, value_label in financial_info_items:
            item_layout = QHBoxLayout()
            item_layout.setSpacing(10)

            title_label = QLabel(label_text)
            title_label.setObjectName("title-label")
            title_label.setFixedWidth(100)

            value_label.setObjectName("value_label")

            item_layout.addWidget(title_label)
            item_layout.addWidget(value_label)
            layout.addLayout(item_layout)

        # زر إضافة معاملة مالية
        add_transaction_btn = QPushButton("إضافة معاملة مالية")
        add_transaction_btn.setIcon(QIcon("icons/add.png") if os.path.exists("icons/add.png") else self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        add_transaction_btn.clicked.connect(self.add_financial_transaction)
        add_transaction_btn.setObjectName("success_button")

        layout.addStretch()
        layout.addWidget(add_transaction_btn)

        parent_layout.addWidget(group_box)

    # إنشاء حاوية المعلومات الإضافية
    def create_additional_info_container(self, parent_layout):
        group_box = QGroupBox("المعلومات الإضافية")
        group_box.setObjectName("info_group")

        layout = QVBoxLayout(group_box)
        layout.setSpacing(12)

        # المعلومات الإضافية
        self.employee_notes_label = QLabel("غير محدد")
        self.employee_last_task_time_label = QLabel("غير محدد")
        self.employee_last_attendance_label = QLabel("غير محدد")
        self.employee_status_label = QLabel("غير محدد")

        # تنسيق التسميات
        additional_info_items = [
            ("الملاحظات:", self.employee_notes_label),
            ("الوقت المتبقي لآخر مهمة:", self.employee_last_task_time_label),
            ("آخر حضور:", self.employee_last_attendance_label),
            ("الحالة الحالية:", self.employee_status_label),
        ]

        for label_text, value_label in additional_info_items:
            item_layout = QHBoxLayout()
            item_layout.setSpacing(10)

            title_label = QLabel(label_text)
            title_label.setObjectName("title-label")
            title_label.setFixedWidth(120)

            value_label.setObjectName("value_label")

            item_layout.addWidget(title_label)
            item_layout.addWidget(value_label)
            layout.addLayout(item_layout)

        # زر تغيير الحالة
        change_status_btn = QPushButton("تغيير الحالة")
        change_status_btn.setIcon(QIcon("icons/status.png") if os.path.exists("icons/status.png") else self.style().standardIcon(QStyle.SP_ComputerIcon))
        change_status_btn.clicked.connect(self.change_employee_status)
        change_status_btn.setObjectName("info_button")

        layout.addStretch()
        layout.addWidget(change_status_btn)

        parent_layout.addWidget(group_box)

    # إنشاء قسم آخر العمليات وأزرار الحضور السريعة
    def create_recent_activities_section(self, parent_layout):
        # الحاوية الرئيسية
        main_frame = QFrame()
        main_frame.setObjectName("activities_frame")

        main_layout = QVBoxLayout(main_frame)
        main_layout.setSpacing(15)

        # العنوان
        title_label = QLabel("العمليات السريعة وآخر الأنشطة")
        title_label.setObjectName("section_title")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # قسم أزرار الحضور السريعة
        self.create_quick_attendance_buttons(main_layout)

        # قسم آخر العمليات
        self.create_recent_activities_display(main_layout)

        parent_layout.addWidget(main_frame)

    # إنشاء أزرار الحضور والانصراف السريعة
    def create_quick_attendance_buttons(self, parent_layout):
        buttons_frame = QFrame()
        buttons_frame.setObjectName("buttons_frame")

        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setSpacing(15)

        # زر تسجيل الحضور
        self.quick_checkin_btn = QPushButton("تسجيل حضور")
        self.quick_checkin_btn.setIcon(QIcon("icons/checkin.png") if os.path.exists("icons/checkin.png") else self.style().standardIcon(QStyle.SP_MediaPlay))
        self.quick_checkin_btn.clicked.connect(self.quick_register_checkin)
        self.quick_checkin_btn.setObjectName("checkin_button")

        # زر تسجيل الانصراف
        self.quick_checkout_btn = QPushButton("تسجيل انصراف")
        self.quick_checkout_btn.setIcon(QIcon("icons/checkout.png") if os.path.exists("icons/checkout.png") else self.style().standardIcon(QStyle.SP_MediaStop))
        self.quick_checkout_btn.clicked.connect(self.quick_register_checkout)
        self.quick_checkout_btn.setObjectName("checkout_button")

        # تسمية حالة الحضور اليوم
        self.attendance_status_label = QLabel("جاري التحقق...")
        self.attendance_status_label.setObjectName("attendance-status")
        self.attendance_status_label.setAlignment(Qt.AlignCenter)

        buttons_layout.addWidget(self.quick_checkin_btn)
        buttons_layout.addWidget(self.quick_checkout_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.attendance_status_label)

        parent_layout.addWidget(buttons_frame)

    # إنشاء عرض آخر الأنشطة
    def create_recent_activities_display(self, parent_layout):
        activities_frame = QFrame()
        activities_frame.setObjectName("recent_activities_frame")

        activities_layout = QVBoxLayout(activities_frame)
        activities_layout.setSpacing(10)

        # آخر عملية حضور وانصراف
        attendance_frame = QFrame()
        attendance_frame.setObjectName("attendance_frame")

        attendance_layout = QHBoxLayout(attendance_frame)
        attendance_layout.setSpacing(10)

        attendance_icon = QLabel("🕐")
        attendance_icon.setObjectName("icon-label")

        self.last_attendance_info_label = QLabel("آخر حضور وانصراف: جاري التحميل...")
        self.last_attendance_info_label.setObjectName("attendance_info")

        attendance_layout.addWidget(attendance_icon)
        attendance_layout.addWidget(self.last_attendance_info_label)
        attendance_layout.addStretch()

        activities_layout.addWidget(attendance_frame)

        # آخر معاملة مالية
        financial_frame = QFrame()
        financial_frame.setObjectName("financial_frame")

        financial_layout = QHBoxLayout(financial_frame)
        financial_layout.setSpacing(10)

        financial_icon = QLabel("💰")
        financial_icon.setObjectName("icon-label")

        self.last_financial_info_label = QLabel("آخر معاملة مالية: جاري التحميل...")
        self.last_financial_info_label.setObjectName("financial_info")

        financial_layout.addWidget(financial_icon)
        financial_layout.addWidget(self.last_financial_info_label)
        financial_layout.addStretch()

        activities_layout.addWidget(financial_frame)

        # آخر مهمة
        task_frame = QFrame()
        task_frame.setObjectName("task_frame")

        task_layout = QHBoxLayout(task_frame)
        task_layout.setSpacing(10)

        task_icon = QLabel("📋")
        task_icon.setObjectName("icon-label")

        self.last_task_info_label = QLabel("آخر مهمة: جاري التحميل...")
        self.last_task_info_label.setObjectName("task_info")

        task_layout.addWidget(task_icon)
        task_layout.addWidget(self.last_task_info_label)
        task_layout.addStretch()

        activities_layout.addWidget(task_frame)

        parent_layout.addWidget(activities_frame)

    # إنشاء قسم الإحصائيات لتاب معلومات الموظف
    def create_employee_info_stats_section(self, parent_layout):
        group_box = QGroupBox("الإحصائيات")
        group_box.setObjectName("stats_group")

        layout = QHBoxLayout(group_box)
        layout.setSpacing(20)

        # إحصائيات مالية
        self.total_deposits_label = QLabel("0")
        self.total_withdrawals_label = QLabel("0")
        self.transactions_count_label = QLabel("0")

        # إحصائيات المهام
        self.total_tasks_label = QLabel("0")
        self.completed_tasks_label = QLabel("0")
        self.pending_tasks_label = QLabel("0")

        stats = [
            ("إجمالي الإيداعات", self.total_deposits_label, "#27ae60"),
            ("إجمالي السحوبات", self.total_withdrawals_label, "#e74c3c"),
            ("عدد المعاملات", self.transactions_count_label, "#3498db"),
            ("إجمالي المهام", self.total_tasks_label, "#9b59b6"),
            ("المهام المكتملة", self.completed_tasks_label, "#27ae60"),
            ("المهام قيد التنفيذ", self.pending_tasks_label, "#f39c12"),
        ]

        for title, label, color in stats:
            stat_widget = QFrame()
            stat_widget.setObjectName("stat_widget")

            stat_layout = QHBoxLayout(stat_widget)
            stat_layout.setAlignment(Qt.AlignCenter)
            stat_layout.setSpacing(5)

            title_label = QLabel(f"{title}:")
            title_label.setObjectName("stat-title")

            label.setObjectName("stat-value")

            stat_layout.addWidget(title_label)
            stat_layout.addWidget(label)

            layout.addWidget(stat_widget)

        parent_layout.addWidget(group_box)

    # إنشاء تاب المعاملات المالية
    def create_financial_transactions_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # شريط البحث والفلاتر مع زر الإضافة
        self.create_financial_transactions_filters(layout)

        # قسم الإحصائيات
        self.create_financial_transactions_stats(layout)

        # جدول المعاملات المالية
        self.financial_transactions_table = QTableWidget()
        self.setup_financial_transactions_table()
        layout.addWidget(self.financial_transactions_table)

        self.tab_widget.addTab(tab, "المعاملات المالية")

    # إنشاء شريط البحث والفلاتر لتاب المعاملات المالية
    def create_financial_transactions_filters(self, parent_layout):
        filters_frame = QFrame()
        filters_frame.setObjectName("filters_frame")

        filters_layout = QHBoxLayout(filters_frame)
        filters_layout.setSpacing(15)

        # خانة البحث
        search_label = QLabel("البحث:")
        search_label.setObjectName("filter-label")
        self.financial_search_edit = QLineEdit()
        self.financial_search_edit.setPlaceholderText("البحث في المعاملات المالية...")
        self.financial_search_edit.setObjectName("search_input")

        # فلتر نوع العملية
        operation_label = QLabel("نوع العملية:")
        operation_label.setObjectName("filter_label")
        self.financial_operation_combo = QComboBox()
        self.financial_operation_combo.addItems(["جميع العمليات", "إيداع", "سحب", "خصم"])
        self.financial_operation_combo.setObjectName("filter_combo")

        # فلتر نوع المعاملة
        transaction_label = QLabel("نوع المعاملة:")
        transaction_label.setObjectName("filter_label")
        self.financial_transaction_combo = QComboBox()
        self.financial_transaction_combo.addItems([
            "جميع المعاملات", "إيداع مرتب", "إيداع مبلغ", "إيداع نسبة%",
            "سحب مبلغ", "خصم مبلغ", "خصم نسبة%"
        ])
        self.financial_transaction_combo.setObjectName("filter_combo")

        # زر إضافة معاملة مالية
        add_transaction_btn = QPushButton("إضافة معاملة مالية")
        add_transaction_btn.setIcon(QIcon("icons/add.png") if os.path.exists("icons/add.png") else self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        add_transaction_btn.clicked.connect(self.add_financial_transaction)
        add_transaction_btn.setObjectName("add_button")

        filters_layout.addWidget(add_transaction_btn)
        filters_layout.addWidget(search_label)
        filters_layout.addWidget(self.financial_search_edit)
        filters_layout.addWidget(operation_label)
        filters_layout.addWidget(self.financial_operation_combo)
        filters_layout.addWidget(transaction_label)
        filters_layout.addWidget(self.financial_transaction_combo)
        filters_layout.addStretch()

        # ربط الفلاتر بدوال التصفية
        self.financial_search_edit.textChanged.connect(self.filter_financial_transactions)
        self.financial_operation_combo.currentTextChanged.connect(self.filter_financial_transactions)
        self.financial_transaction_combo.currentTextChanged.connect(self.filter_financial_transactions)

        parent_layout.addWidget(filters_frame)

    # إنشاء قسم الإحصائيات للمعاملات المالية
    def create_financial_transactions_stats(self, parent_layout):
        stats_frame = QFrame()
        stats_frame.setObjectName("stats_frame")

        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(20)

        # إحصائيات المعاملات المالية
        self.financial_total_deposits_label = QLabel("0.00")
        self.financial_total_withdrawals_label = QLabel("0.00")
        self.financial_net_balance_label = QLabel("0.00")
        self.financial_transactions_count_label = QLabel("0")

        stats = [
            ("إجمالي الإيداعات", self.financial_total_deposits_label, "#27ae60"),
            ("إجمالي السحوبات", self.financial_total_withdrawals_label, "#e74c3c"),
            ("الرصيد الصافي", self.financial_net_balance_label, "#3498db"),
            ("عدد المعاملات", self.financial_transactions_count_label, "#9b59b6"),
        ]

        for title, label, color in stats:
            stat_widget = QFrame()
            stat_widget.setObjectName("stat_widget")

            stat_layout_inner = QHBoxLayout(stat_widget)
            stat_layout_inner.setAlignment(Qt.AlignCenter)
            stat_layout_inner.setSpacing(5)

            title_label = QLabel(f"{title}:")
            title_label.setObjectName("section_title")

            label.setObjectName("styled_element")

            stat_layout_inner.addWidget(title_label)
            stat_layout_inner.addWidget(label)

            stats_layout.addWidget(stat_widget)

        parent_layout.addWidget(stats_frame)

    # إعداد جدول المعاملات المالية
    def setup_financial_transactions_table(self):
        headers = ["ID", "الرقم", "نوع العملية", "نوع المعاملة", "النسبة", "المبلغ", "التاريخ", "الوصف"]
        self.financial_transactions_table.setColumnCount(len(headers))
        self.financial_transactions_table.setHorizontalHeaderLabels(headers)
        self.financial_transactions_table.hideColumn(0)  # إخفاء عمود ID

        # تطبيق إعدادات الجدول
        table_setting(self.financial_transactions_table)

        # إضافة قائمة السياق للجدول
        setup_table_context_menu(self.financial_transactions_table, self, "المعاملات المالية", is_main_table=False)

        # إضافة وظيفة النقر المزدوج لفتح حوار التعديل
        self.financial_transactions_table.itemDoubleClicked.connect(self.on_financial_transactions_table_double_click)

    # إنشاء تاب مهام الموظف
    def create_employee_tasks_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # شريط البحث والفلاتر مع زر الإضافة
        self.create_employee_tasks_filters(layout)

        # قسم الإحصائيات
        self.create_employee_tasks_stats(layout)

        # جدول مهام الموظف
        self.employee_tasks_table = QTableWidget()
        self.setup_employee_tasks_table()
        layout.addWidget(self.employee_tasks_table)

        self.tab_widget.addTab(tab, "مهام الموظف")

    # إنشاء شريط البحث والفلاتر لتاب مهام الموظف
    def create_employee_tasks_filters(self, parent_layout):
        filters_frame = QFrame()
        filters_frame.setObjectName("filters_frame")

        filters_layout = QHBoxLayout(filters_frame)
        filters_layout.setSpacing(15)

        # خانة البحث
        search_label = QLabel("البحث:")
        search_label.setObjectName("filter_label")
        self.tasks_search_edit = QLineEdit()
        self.tasks_search_edit.setPlaceholderText("البحث في المهام...")
        self.tasks_search_edit.setObjectName("search_input")

        # فلتر الحالة
        status_label = QLabel("حالة المهمة:")
        status_label.setObjectName("filter_label")
        self.tasks_status_combo = QComboBox()
        self.tasks_status_combo.addItems(["جميع الحالات", "لم يبدأ", "قيد التنفيذ", "مكتملة", "ملغاة", "متأخرة", "متوقف"])
        self.tasks_status_combo.setObjectName("filter_combo")

        # فلتر نوع المهمة
        task_type_label = QLabel("نوع المهمة:")
        task_type_label.setObjectName("filter_label")
        self.tasks_type_combo = QComboBox()
        self.tasks_type_combo.addItems(["جميع الأنواع", "مهمة عامة", "مشروع", "مقاولات"])
        self.tasks_type_combo.setObjectName("filter_combo")

        # زر إضافة مهمة جديدة
        add_task_btn = QPushButton("إضافة مهمة جديدة")
        add_task_btn.setIcon(QIcon("icons/add.png") if os.path.exists("icons/add.png") else self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        add_task_btn.clicked.connect(self.add_employee_task)
        add_task_btn.setObjectName("add_button")

        # زر إدراج رصيد مهمة محددة
        insert_selected_btn = QPushButton("إدراج رصيد المهمة المحددة")
        insert_selected_btn.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))
        insert_selected_btn.clicked.connect(self.insert_selected_task_balance)
        insert_selected_btn.setObjectName("success_button")

        # زر إدراج جميع الأرصدة
        insert_all_btn = QPushButton("إدراج جميع الأرصدة")
        insert_all_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))
        insert_all_btn.clicked.connect(self.insert_all_task_balances)
        insert_all_btn.setObjectName("warning_button")

        filters_layout.addWidget(add_task_btn)
        filters_layout.addWidget(insert_selected_btn)
        filters_layout.addWidget(insert_all_btn)
        filters_layout.addWidget(search_label)
        filters_layout.addWidget(self.tasks_search_edit)
        filters_layout.addWidget(status_label)
        filters_layout.addWidget(self.tasks_status_combo)
        filters_layout.addWidget(task_type_label)
        filters_layout.addWidget(self.tasks_type_combo)
        filters_layout.addStretch()

        # ربط الفلاتر بدوال التصفية
        self.tasks_search_edit.textChanged.connect(self.filter_employee_tasks)
        self.tasks_status_combo.currentTextChanged.connect(self.filter_employee_tasks)
        self.tasks_type_combo.currentTextChanged.connect(self.filter_employee_tasks)

        parent_layout.addWidget(filters_frame)

    # إنشاء قسم الإحصائيات لمهام الموظف
    def create_employee_tasks_stats(self, parent_layout):
        stats_frame = QFrame()
        stats_frame.setObjectName("stats_frame")

        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(20)

        # إحصائيات المهام
        self.tasks_total_label = QLabel("0")
        self.tasks_completed_label = QLabel("0")
        self.tasks_pending_label = QLabel("0")
        self.tasks_overdue_label = QLabel("0")

        stats = [
            ("إجمالي المهام", self.tasks_total_label, "#9b59b6"),
            ("المهام المكتملة", self.tasks_completed_label, "#27ae60"),
            ("المهام قيد التنفيذ", self.tasks_pending_label, "#f39c12"),
            ("المهام المتأخرة", self.tasks_overdue_label, "#e74c3c"),
        ]

        for title, label, color in stats:
            stat_widget = QFrame()
            stat_widget.setObjectName("stat_widget")

            stat_layout_inner = QHBoxLayout(stat_widget)
            stat_layout_inner.setAlignment(Qt.AlignCenter)
            stat_layout_inner.setSpacing(5)

            title_label = QLabel(f"{title}:")
            title_label.setObjectName("section_title")

            label.setObjectName("styled_element")

            stat_layout_inner.addWidget(title_label)
            stat_layout_inner.addWidget(label)

            stats_layout.addWidget(stat_widget)

        parent_layout.addWidget(stats_frame)

    # إعداد جدول مهام الموظف
    def setup_employee_tasks_table(self):
        headers = [
            "ID", "الرقم", "اسم المشروع", "العميل", "اسم المهمة", "وصف المهمة",
            "النسبة %", "المبلغ", "حالة المبلغ", "تاريخ البدء", "تاريخ الانتهاء",
            "الحالة", "ملاحظات", "نوع المهمة"
        ]
        self.employee_tasks_table.setColumnCount(len(headers))
        self.employee_tasks_table.setHorizontalHeaderLabels(headers)
        self.employee_tasks_table.hideColumn(0)  # إخفاء عمود ID

        # تطبيق إعدادات الجدول
        table_setting(self.employee_tasks_table)

        # إضافة قائمة السياق للجدول
        setup_table_context_menu(self.employee_tasks_table, self, "مهام الموظف", is_main_table=False)

        # إضافة وظيفة النقر المزدوج لفتح حوار التعديل
        self.employee_tasks_table.itemDoubleClicked.connect(self.on_employee_tasks_table_double_click)

    # إنشاء تاب الحضور والانصراف
    def create_attendance_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # شريط البحث والفلاتر مع زر الإضافة
        self.create_attendance_filters(layout)

        # قسم الإحصائيات
        self.create_attendance_stats(layout)

        # جدول الحضور والانصراف
        self.attendance_table = QTableWidget()
        self.setup_attendance_table()
        layout.addWidget(self.attendance_table)

        self.tab_widget.addTab(tab, "الحضور والانصراف")

    # إنشاء شريط البحث والفلاتر لتاب الحضور والانصراف
    def create_attendance_filters(self, parent_layout):
        filters_frame = QFrame()
        filters_frame.setObjectName("filters_frame")

        filters_layout = QHBoxLayout(filters_frame)
        filters_layout.setSpacing(15)

        # خانة البحث
        search_label = QLabel("البحث:")
        search_label.setObjectName("filter_label")
        self.attendance_search_edit = QLineEdit()
        self.attendance_search_edit.setPlaceholderText("البحث في سجلات الحضور...")
        self.attendance_search_edit.setObjectName("search_input")

        # فلتر الشهر
        month_label = QLabel("الشهر:")
        month_label.setObjectName("filter_label")
        self.attendance_month_combo = QComboBox()
        months = ["جميع الشهور", "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
                 "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
        self.attendance_month_combo.addItems(months)
        self.attendance_month_combo.setObjectName("filter_combo")

        # زر تسجيل حضور/انصراف
        add_attendance_btn = QPushButton("تسجيل حضور/انصراف")
        add_attendance_btn.setIcon(QIcon("icons/add.png") if os.path.exists("icons/add.png") else self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        add_attendance_btn.clicked.connect(self.add_attendance_record)
        add_attendance_btn.setObjectName("add_button")

        filters_layout.addWidget(add_attendance_btn)
        filters_layout.addWidget(search_label)
        filters_layout.addWidget(self.attendance_search_edit)
        filters_layout.addWidget(month_label)
        filters_layout.addWidget(self.attendance_month_combo)
        filters_layout.addStretch()

        # ربط الفلاتر بدوال التصفية
        self.attendance_search_edit.textChanged.connect(self.filter_attendance)
        self.attendance_month_combo.currentTextChanged.connect(self.filter_attendance)

        parent_layout.addWidget(filters_frame)

    # إنشاء قسم الإحصائيات للحضور والانصراف
    def create_attendance_stats(self, parent_layout):
        stats_frame = QFrame()
        stats_frame.setObjectName("stats_frame")

        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(20)

        # إحصائيات الحضور
        self.attendance_total_days_label = QLabel("0")
        self.attendance_present_days_label = QLabel("0")
        self.attendance_late_days_label = QLabel("0")
        self.attendance_early_leave_label = QLabel("0")

        stats = [
            ("إجمالي الأيام", self.attendance_total_days_label, "#3498db"),
            ("أيام الحضور", self.attendance_present_days_label, "#27ae60"),
            ("أيام التأخير", self.attendance_late_days_label, "#e74c3c"),
            ("انصراف مبكر", self.attendance_early_leave_label, "#f39c12"),
        ]

        for title, label, color in stats:
            stat_widget = QFrame()
            stat_widget.setObjectName("stat_widget")

            stat_layout_inner = QHBoxLayout(stat_widget)
            stat_layout_inner.setAlignment(Qt.AlignCenter)
            stat_layout_inner.setSpacing(5)

            title_label = QLabel(f"{title}:")
            title_label.setObjectName("section_title")

            label.setObjectName("styled_element")

            stat_layout_inner.addWidget(title_label)
            stat_layout_inner.addWidget(label)

            stats_layout.addWidget(stat_widget)

        parent_layout.addWidget(stats_frame)

    # إعداد جدول الحضور والانصراف
    def setup_attendance_table(self):
        headers = [
            "ID", "الرقم", "التاريخ", "اليوم", "وقت الحضور", "وقت الانصراف",
            "حالة الحضور", "مدة التأخير/التبكير", "حالة الانصراف", "مدة التأخير/التبكير", "ملاحظات"
        ]
        self.attendance_table.setColumnCount(len(headers))
        self.attendance_table.setHorizontalHeaderLabels(headers)
        self.attendance_table.hideColumn(0)  # إخفاء عمود ID

        # تطبيق إعدادات الجدول
        table_setting(self.attendance_table)

        # إضافة قائمة السياق للجدول
        setup_table_context_menu(self.attendance_table, self, "الحضور والانصراف", is_main_table=False)

        # إضافة وظيفة النقر المزدوج لفتح حوار التعديل
        self.attendance_table.itemDoubleClicked.connect(self.on_attendance_table_double_click)

    # إنشاء تاب التقييم
    def create_evaluation_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # شريط البحث والفلاتر مع زر الإضافة
        self.create_evaluation_filters(layout)

        # قسم الإحصائيات
        self.create_evaluation_stats(layout)

        # جدول التقييم
        self.evaluation_table = QTableWidget()
        self.setup_evaluation_table()
        layout.addWidget(self.evaluation_table)

        self.tab_widget.addTab(tab, "التقييم")

    # إنشاء شريط البحث والفلاتر لتاب التقييم
    def create_evaluation_filters(self, parent_layout):
        filters_frame = QFrame()
        filters_frame.setObjectName("filters_frame")

        filters_layout = QHBoxLayout(filters_frame)
        filters_layout.setSpacing(15)

        # خانة البحث
        search_label = QLabel("البحث:")
        search_label.setObjectName("filter_label")
        self.evaluation_search_edit = QLineEdit()
        self.evaluation_search_edit.setPlaceholderText("البحث في التقييمات...")
        self.evaluation_search_edit.setObjectName("search_input")

        # فلتر حالة التسليم
        delivery_label = QLabel("حالة التسليم:")
        delivery_label.setObjectName("filter_label")
        self.evaluation_delivery_combo = QComboBox()
        self.evaluation_delivery_combo.addItems([
            "جميع الحالات", "قبل الموعد", "في الموعد", "تسليم متأخر", "لم يتم التسليم"
        ])
        self.evaluation_delivery_combo.setObjectName("filter_combo")

        # زر إضافة تقييم جديد
        add_evaluation_btn = QPushButton("إضافة تقييم جديد")
        add_evaluation_btn.setIcon(QIcon("icons/add.png") if os.path.exists("icons/add.png") else self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        add_evaluation_btn.clicked.connect(self.add_evaluation)
        add_evaluation_btn.setObjectName("add_button")

        filters_layout.addWidget(add_evaluation_btn)
        filters_layout.addWidget(search_label)
        filters_layout.addWidget(self.evaluation_search_edit)
        filters_layout.addWidget(delivery_label)
        filters_layout.addWidget(self.evaluation_delivery_combo)
        filters_layout.addStretch()

        # ربط الفلاتر بدوال التصفية
        self.evaluation_search_edit.textChanged.connect(self.filter_evaluation)
        self.evaluation_delivery_combo.currentTextChanged.connect(self.filter_evaluation)

        parent_layout.addWidget(filters_frame)

    # إنشاء قسم الإحصائيات للتقييم
    def create_evaluation_stats(self, parent_layout):
        stats_frame = QFrame()
        stats_frame.setObjectName("stats_frame")

        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(20)

        # إحصائيات التقييم
        self.evaluation_total_label = QLabel("0")
        self.evaluation_on_time_label = QLabel("0")
        self.evaluation_late_label = QLabel("0")
        self.evaluation_avg_points_label = QLabel("0")

        stats = [
            ("إجمالي التقييمات", self.evaluation_total_label, "#9b59b6"),
            ("في الموعد", self.evaluation_on_time_label, "#27ae60"),
            ("متأخر", self.evaluation_late_label, "#e74c3c"),
            ("متوسط النقاط", self.evaluation_avg_points_label, "#3498db"),
        ]

        for title, label, color in stats:
            stat_widget = QFrame()
            stat_widget.setObjectName("stat_widget")

            stat_layout_inner = QHBoxLayout(stat_widget)
            stat_layout_inner.setAlignment(Qt.AlignCenter)
            stat_layout_inner.setSpacing(5)

            title_label = QLabel(f"{title}:")
            title_label.setObjectName("section_title")

            label.setObjectName("styled_element")

            stat_layout_inner.addWidget(title_label)
            stat_layout_inner.addWidget(label)

            stats_layout.addWidget(stat_widget)

        parent_layout.addWidget(stats_frame)

    # إعداد جدول التقييم
    def setup_evaluation_table(self):
        headers = ["ID", "الرقم", "حالة التسليم", "النقاط", "تاريخ التقييم"]
        self.evaluation_table.setColumnCount(len(headers))
        self.evaluation_table.setHorizontalHeaderLabels(headers)
        self.evaluation_table.hideColumn(0)  # إخفاء عمود ID

        # تطبيق إعدادات الجدول
        table_setting(self.evaluation_table)

        # إضافة قائمة السياق للجدول
        setup_table_context_menu(self.evaluation_table, self, "التقييم", is_main_table=False)

        # إضافة وظيفة النقر المزدوج لفتح حوار التعديل
        self.evaluation_table.itemDoubleClicked.connect(self.on_evaluation_table_double_click)

    # ==================== دوال تحميل البيانات ====================

    # تحميل معلومات الموظف الأساسية
    def load_employee_info(self):
        try:
            if not self.employee_id:
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # تحميل بيانات الموظف الأساسية
            cursor.execute("""
                SELECT اسم_الموظف, الوظيفة, الهاتف, العنوان, تاريخ_التوظيف,
                       الحالة, المرتب, النسبة, الرصيد, التصنيف, ملاحظات,
                       جدولة_المرتب_تلقائية, خاضع_لنظام_الحضور_والانصراف
                FROM الموظفين
                WHERE id = %s
            """, (self.employee_id,))

            employee_data = cursor.fetchone()
            if employee_data:
                # المعلومات الأساسية
                self.employee_name_label.setText(str(employee_data[0] or "غير محدد"))
                self.employee_job_label.setText(str(employee_data[1] or "غير محدد"))
                self.employee_phone_label.setText(str(employee_data[2] or "غير محدد"))
                self.employee_address_label.setText(str(employee_data[3] or "غير محدد"))

                # المعلومات المالية
                self.employee_hire_date_label.setText(str(employee_data[4] or "غير محدد"))
                self.employee_salary_label.setText(f"{employee_data[6] or 0:,.2f} {Currency_type}")
                self.employee_percentage_label.setText(f"{employee_data[7] or 0}%")

                # تنسيق الرصيد مع لون
                balance = employee_data[8] or 0
                self.employee_balance_label.setText(f"{balance:,.2f} {Currency_type}")
                # تطبيق الأنماط الديناميكية للرصيد
                self.employee_balance_label._is_balance = True
                apply_dynamic_label_styles(self.employee_balance_label, f"{balance:,.2f} {Currency_type}")

                # المعلومات الإضافية
                self.employee_notes_label.setText(str(employee_data[10] or "لا توجد ملاحظات"))

                # تنسيق الحالة مع لون
                status = employee_data[5] or "غير محدد"
                self.employee_status_label.setText(status)
                # تطبيق الأنماط الديناميكية للحالة
                self.employee_status_label._is_status = True
                apply_dynamic_label_styles(self.employee_status_label, status)

                # معالجة الحقول الجديدة
                auto_salary_schedule = employee_data[11] if len(employee_data) > 11 else False
                attendance_system = employee_data[12] if len(employee_data) > 12 else True

                # إخفاء/إظهار تاب الحضور والانصراف بناءً على إعداد الموظف
                self.update_attendance_tab_visibility(attendance_system)

            # تحميل الوقت المتبقي لآخر مهمة
            self.load_last_task_remaining_time()

            # تحميل آخر حضور
            self.load_last_attendance()

            # تحميل الإحصائيات المالية
            self.load_financial_stats()

            # تحميل إحصائيات المهام
            self.load_tasks_stats()

            # تحديث إحصائيات التابات الأخرى
            self.update_attendance_stats()
            self.update_evaluation_stats()

            # تحديث أزرار الحضور والأنشطة الحديثة
            self.update_attendance_buttons_status()
            self.load_recent_activities()

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل معلومات الموظف: {str(e)}")

    # تحديث إظهار/إخفاء تاب الحضور والانصراف والعمليات السريعة
    def update_attendance_tab_visibility(self, attendance_system_enabled):
        try:
            # البحث عن تاب الحضور والانصراف
            attendance_tab_index = -1
            for i in range(self.tab_widget.count()):
                if self.tab_widget.tabText(i) == "الحضور والانصراف":
                    attendance_tab_index = i
                    break

            if attendance_tab_index != -1:
                # إخفاء أو إظهار التاب
                self.tab_widget.setTabVisible(attendance_tab_index, attendance_system_enabled)

            # إخفاء/إظهار أزرار الحضور السريعة
            self.update_quick_attendance_buttons_visibility(attendance_system_enabled)

        except Exception as e:
            print(f"خطأ في تحديث إظهار تاب الحضور والانصراف: {str(e)}")

    # تحديث إظهار/إخفاء أزرار الحضور السريعة وإحصائية آخر حضور وانصراف
    def update_quick_attendance_buttons_visibility(self, attendance_system_enabled):
        try:
            # إخفاء/إظهار أزرار الحضور السريعة
            if hasattr(self, 'quick_checkin_btn'):
                self.quick_checkin_btn.setVisible(attendance_system_enabled)

            if hasattr(self, 'quick_checkout_btn'):
                self.quick_checkout_btn.setVisible(attendance_system_enabled)

            if hasattr(self, 'attendance_status_label'):
                if attendance_system_enabled:
                    self.attendance_status_label.setVisible(True)
                else:
                    # إخفاء تسمية حالة الحضور وإظهار رسالة بديلة
                    self.attendance_status_label.setVisible(True)
                    self.attendance_status_label.setText("الموظف غير خاضع لنظام الحضور والانصراف")
                    self.attendance_status_label.setObjectName("attendance_status")

            # إخفاء/إظهار إحصائية آخر حضور وانصراف في قسم الأنشطة الحديثة
            self.update_last_attendance_info_visibility(attendance_system_enabled)

        except Exception as e:
            print(f"خطأ في تحديث إظهار أزرار الحضور السريعة: {str(e)}")

    # تحديث إظهار/إخفاء إحصائية آخر حضور وانصراف
    def update_last_attendance_info_visibility(self, attendance_system_enabled):
        try:
            # البحث عن إطار آخر حضور وانصراف في قسم الأنشطة الحديثة
            if hasattr(self, 'last_attendance_info_label'):
                if attendance_system_enabled:
                    # إظهار المعلومات العادية
                    self.last_attendance_info_label.setVisible(True)
                    # إعادة تحميل البيانات إذا كانت مخفية سابقاً
                    if self.last_attendance_info_label.text() == "الموظف غير خاضع لنظام الحضور والانصراف":
                        self.load_last_attendance_info()
                else:
                    # إظهار رسالة بديلة
                    self.last_attendance_info_label.setVisible(True)
                    self.last_attendance_info_label.setText("الموظف غير خاضع لنظام الحضور والانصراف")
                    self.last_attendance_info_label.setObjectName("attendance_info")

            # إخفاء/إظهار إطار آخر حضور وانصراف بالكامل إذا أردنا إخفاءه تماماً
            # يمكن البحث عن الإطار الأب للـ label وإخفاءه
            if hasattr(self, 'last_attendance_info_label') and self.last_attendance_info_label.parent():
                attendance_frame = self.last_attendance_info_label.parent()
                if attendance_frame:
                    if not attendance_system_enabled:
                        # تغيير لون الإطار ليبدو معطلاً
                        attendance_frame.setObjectName("attendance_frame")
                    else:
                        # إعادة اللون الأصلي
                        attendance_frame.setObjectName("attendance_frame")

        except Exception as e:
            print(f"خطأ في تحديث إظهار إحصائية آخر حضور وانصراف: {str(e)}")

    # تحديث حالة أزرار الحضور والانصراف
    def update_attendance_buttons_status(self):
        try:
            if not self.employee_id:
                return

            # التحقق من حالة نظام الحضور والانصراف للموظف
            attendance_system_enabled = self.is_employee_attendance_system_enabled()

            if not attendance_system_enabled:
                # إذا كان الموظف غير خاضع لنظام الحضور والانصراف، لا نحدث الأزرار
                return

            from نظام_الحضور_المطور import AdvancedAttendanceSystem
            from datetime import date

            # التحقق من حالة الحضور اليوم
            today = date.today()
            existing = AdvancedAttendanceSystem.check_existing_attendance(self.employee_id, today)

            if not existing:
                # لم يتم تسجيل أي شيء اليوم
                self.quick_checkin_btn.setEnabled(True)
                self.quick_checkout_btn.setEnabled(False)
                self.attendance_status_label.setText("لم يتم تسجيل الحضور اليوم")
                self.attendance_status_label.setObjectName("attendance-status")
            elif existing.get('وقت_الحضور') and not existing.get('وقت_الانصراف'):
                # تم تسجيل الحضور ولم يتم تسجيل الانصراف
                self.quick_checkin_btn.setEnabled(False)
                self.quick_checkout_btn.setEnabled(True)
                self.attendance_status_label.setText("تم تسجيل الحضور - في انتظار الانصراف")
                self.attendance_status_label.setObjectName("attendance-status")
            elif existing.get('وقت_الحضور') and existing.get('وقت_الانصراف'):
                # تم تسجيل الحضور والانصراف
                self.quick_checkin_btn.setEnabled(False)
                self.quick_checkout_btn.setEnabled(False)
                self.attendance_status_label.setText("تم تسجيل الحضور والانصراف اليوم")
                self.attendance_status_label.setObjectName("attendance-status")
            else:
                # حالة غير متوقعة
                self.quick_checkin_btn.setEnabled(True)
                self.quick_checkout_btn.setEnabled(False)
                self.attendance_status_label.setText("حالة غير محددة")

        except Exception as e:
            print(f"خطأ في تحديث حالة أزرار الحضور: {e}")

    # التحقق من حالة نظام الحضور والانصراف للموظف
    def is_employee_attendance_system_enabled(self):
        try:
            if not self.employee_id:
                return True  # افتراضي

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT خاضع_لنظام_الحضور_والانصراف
                FROM الموظفين
                WHERE id = %s
            """, (self.employee_id,))

            result = cursor.fetchone()
            conn.close()

            if result:
                return bool(result[0])
            else:
                return True  # افتراضي إذا لم توجد بيانات

        except Exception as e:
            print(f"خطأ في التحقق من حالة نظام الحضور والانصراف: {e}")
            return True  # افتراضي في حالة الخطأ

    # تحميل آخر الأنشطة
    def load_recent_activities(self):
        try:
            if not self.employee_id:
                return

            # تحميل آخر حضور وانصراف فقط إذا كان الموظف خاضعاً لنظام الحضور والانصراف
            attendance_system_enabled = self.is_employee_attendance_system_enabled()
            if attendance_system_enabled:
                self.load_last_attendance_info()
            else:
                # إظهار رسالة بديلة لآخر حضور وانصراف
                if hasattr(self, 'last_attendance_info_label'):
                    self.last_attendance_info_label.setText("الموظف غير خاضع لنظام الحضور والانصراف")
                    self.last_attendance_info_label.setObjectName("attendance_info")

            # تحميل آخر معاملة مالية
            self.load_last_financial_info()

            # تحميل آخر مهمة
            self.load_last_task_info()

        except Exception as e:
            print(f"خطأ في تحميل آخر الأنشطة: {e}")

    # تحميل معلومات آخر حضور وانصراف
    def load_last_attendance_info(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT التاريخ, وقت_الحضور, وقت_الانصراف, حالة_الحضور, حالة_الانصراف
                FROM الموظفين_الحضور_والانصراف
                WHERE معرف_الموظف = %s
                ORDER BY التاريخ DESC, id DESC
                LIMIT 1
            """, (self.employee_id,))

            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result:
                date_str = str(result[0])
                checkin_time = str(result[1]) if result[1] else "لم يسجل"
                checkout_time = str(result[2]) if result[2] else "لم يسجل"
                checkin_status = result[3] if result[3] else ""
                checkout_status = result[4] if result[4] else ""

                # تحويل الأوقات إلى نظام 12 ساعة
                if result[1]:
                    try:
                        from datetime import datetime
                        time_obj = datetime.strptime(str(result[1]), '%H:%M:%S')
                        checkin_time = time_obj.strftime('%I:%M %p').replace('AM', 'ص').replace('PM', 'م')
                    except:
                        pass

                if result[2]:
                    try:
                        from datetime import datetime
                        time_obj = datetime.strptime(str(result[2]), '%H:%M:%S')
                        checkout_time = time_obj.strftime('%I:%M %p').replace('AM', 'ص').replace('PM', 'م')
                    except:
                        pass

                info_text = f"التاريخ: {date_str} | الحضور: {checkin_time}"
                if checkin_status:
                    info_text += f" ({checkin_status})"
                info_text += f" | الانصراف: {checkout_time}"
                if checkout_status:
                    info_text += f" ({checkout_status})"

                self.last_attendance_info_label.setText(info_text)
            else:
                self.last_attendance_info_label.setText("لا توجد سجلات حضور وانصراف")

        except Exception as e:
            self.last_attendance_info_label.setText(f"خطأ في تحميل بيانات الحضور: {str(e)}")

    # تحميل معلومات آخر معاملة مالية
    def load_last_financial_info(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT التاريخ, نوع_العملية, نوع_المعاملة, المبلغ
                FROM الموظفين_معاملات_مالية
                WHERE معرف_الموظف = %s
                ORDER BY التاريخ DESC, id DESC
                LIMIT 1
            """, (self.employee_id,))

            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result:
                date_str = str(result[0])
                operation_type = result[1]
                transaction_type = result[2]
                amount = result[3]

                info_text = f"التاريخ: {date_str} | النوع: {transaction_type} | المبلغ: {amount} {Currency_type}"
                self.last_financial_info_label.setText(info_text)
            else:
                self.last_financial_info_label.setText("لا توجد معاملات مالية")

        except Exception as e:
            self.last_financial_info_label.setText(f"خطأ في تحميل البيانات المالية: {str(e)}")

    # تحميل معلومات آخر مهمة
    def load_last_task_info(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT وصف_المهمة, الحالة, تاريخ_البدء, تاريخ_الانتهاء
                FROM المشاريع_مهام_الفريق
                WHERE معرف_الموظف = %s
                ORDER BY تاريخ_الإضافة DESC, id DESC
                LIMIT 1
            """, (self.employee_id,))

            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result:
                task_desc = result[0]
                status = result[1]
                start_date = str(result[2]) if result[2] else "غير محدد"
                end_date = str(result[3]) if result[3] else "غير محدد"

                info_text = f"المهمة: {task_desc} | الحالة: {status} | الانتهاء: {end_date}"
                self.last_task_info_label.setText(info_text)
            else:
                self.last_task_info_label.setText("لا توجد مهام مسجلة")

        except Exception as e:
            self.last_task_info_label.setText(f"خطأ في تحميل بيانات المهام: {str(e)}")

    # تسجيل حضور سريع
    def quick_register_checkin(self):
        try:
            from نظام_الحضور_المطور import AdvancedAttendanceSystem
            from datetime import datetime, date

            # الحصول على الوقت الحالي
            current_time = datetime.now().time()
            today = date.today()

            # تسجيل الحضور
            result = AdvancedAttendanceSystem.register_checkin(
                self.employee_id, current_time, today, "تسجيل سريع"
            )

            if result['success']:
                QMessageBox.information(self, "نجح التسجيل", result['message'])
                # تحديث الواجهة
                self.update_attendance_buttons_status()
                self.load_recent_activities()
                self.load_attendance_data()  # تحديث جدول الحضور
            else:
                QMessageBox.warning(self, "فشل التسجيل", result['message'])

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تسجيل الحضور: {str(e)}")

    # تسجيل انصراف سريع
    def quick_register_checkout(self):
        try:
            from نظام_الحضور_المطور import AdvancedAttendanceSystem
            from datetime import datetime, date

            # الحصول على الوقت الحالي
            current_time = datetime.now().time()
            today = date.today()

            # تسجيل الانصراف
            result = AdvancedAttendanceSystem.register_checkout(
                self.employee_id, current_time, today, "تسجيل سريع"
            )

            if result['success']:
                QMessageBox.information(self, "نجح التسجيل", result['message'])
                # تحديث الواجهة
                self.update_attendance_buttons_status()
                self.load_recent_activities()
                self.load_attendance_data()  # تحديث جدول الحضور
            else:
                QMessageBox.warning(self, "فشل التسجيل", result['message'])

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تسجيل الانصراف: {str(e)}")

    # تحميل الوقت المتبقي لآخر مهمة
    def load_last_task_remaining_time(self):
        try:
            if not self.employee_id:
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT تاريخ_الانتهاء, الحالة, عنوان_المهمة
                FROM المشاريع_مهام_الفريق
                WHERE معرف_الموظف = %s AND الحالة IN ('قيد التنفيذ', 'لم يبدأ')
                ORDER BY تاريخ_الانتهاء ASC
                LIMIT 1
            """, (self.employee_id,))

            task_data = cursor.fetchone()
            if task_data and task_data[0]:
                from datetime import datetime, date
                end_date = task_data[0]
                if isinstance(end_date, str):
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

                today = date.today()
                remaining_days = (end_date - today).days

                if remaining_days > 0:
                    remaining_text = f"{remaining_days} يوم متبقي"
                elif remaining_days == 0:
                    remaining_text = "ينتهي اليوم"
                else:
                    remaining_text = f"متأخر بـ {abs(remaining_days)} يوم"

                self.employee_last_task_time_label.setText(remaining_text)
                # تطبيق الأنماط الديناميكية للوقت المتبقي
                self.employee_last_task_time_label._is_time = True
                apply_dynamic_label_styles(self.employee_last_task_time_label, remaining_text)
            else:
                self.employee_last_task_time_label.setText("لا توجد مهام نشطة")

            conn.close()

        except Exception as e:
            print(f"خطأ في تحميل الوقت المتبقي للمهمة: {e}")
            self.employee_last_task_time_label.setText("غير محدد")

    # تحميل آخر حضور
    def load_last_attendance(self):
        try:
            if not self.employee_id:
                return

            # التحقق من حالة نظام الحضور والانصراف للموظف
            attendance_system_enabled = self.is_employee_attendance_system_enabled()

            if not attendance_system_enabled:
                # إذا كان الموظف غير خاضع لنظام الحضور والانصراف
                if hasattr(self, 'employee_last_attendance_label'):
                    self.employee_last_attendance_label.setText("غير خاضع لنظام الحضور والانصراف")
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT التاريخ, وقت_الحضور
                FROM الموظفين_الحضور_والانصراف
                WHERE معرف_الموظف = %s
                ORDER BY التاريخ DESC, وقت_الحضور DESC
                LIMIT 1
            """, (self.employee_id,))

            attendance_data = cursor.fetchone()
            if attendance_data:
                from datetime import datetime

                # تحويل التاريخ والوقت إلى نص مقروء
                attendance_date = attendance_data[0]
                attendance_time = attendance_data[1]

                if attendance_date and attendance_time:
                    # تحويل التاريخ إلى اسم اليوم
                    if isinstance(attendance_date, str):
                        date_obj = datetime.strptime(attendance_date, '%Y-%m-%d').date()
                    else:
                        date_obj = attendance_date

                    # أسماء الأيام بالعربية
                    days_arabic = {
                        0: "الاثنين", 1: "الثلاثاء", 2: "الأربعاء", 3: "الخميس",
                        4: "الجمعة", 5: "السبت", 6: "الأحد"
                    }

                    day_name = days_arabic.get(date_obj.weekday(), "غير محدد")
                    formatted_date = date_obj.strftime('%Y-%m-%d')

                    attendance_text = f"{day_name} {formatted_date} - {attendance_time}"
                    self.employee_last_attendance_label.setText(attendance_text)
                else:
                    self.employee_last_attendance_label.setText("لم يسجل حضور")
            else:
                self.employee_last_attendance_label.setText("لا يوجد سجل حضور")

            conn.close()

        except Exception as e:
            print(f"خطأ في تحميل آخر حضور: {e}")
            self.employee_last_attendance_label.setText("غير محدد")

    # الحصول على لون الحالة
    def get_status_color(self, status):
        status_colors = {
            "نشط": "#27ae60",
            "غير نشط": "#95a5a6",
            "إجازة": "#f39c12",
            "مستقيل": "#e74c3c",
            "تم فصله": "#c0392b"
        }
        return status_colors.get(status, "#34495e")

    # تحميل الإحصائيات المالية
    def load_financial_stats(self):
        try:
            if not self.employee_id:
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # إجمالي الإيداعات
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0)
                FROM الموظفين_معاملات_مالية
                WHERE معرف_الموظف = %s AND نوع_العملية = 'إيداع'
            """, (self.employee_id,))
            result = cursor.fetchone()
            total_deposits = result[0] if result else 0
            self.total_deposits_label.setText(f"{total_deposits:,.2f}  {Currency_type}")

            # إجمالي السحوبات
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0)
                FROM الموظفين_معاملات_مالية
                WHERE معرف_الموظف = %s AND نوع_العملية IN ('سحب', 'خصم')
            """, (self.employee_id,))
            result = cursor.fetchone()
            total_withdrawals = result[0] if result else 0
            self.total_withdrawals_label.setText(f"{total_withdrawals:,.2f}  {Currency_type}")

            # عدد المعاملات
            cursor.execute("""
                SELECT COUNT(*)
                FROM الموظفين_معاملات_مالية
                WHERE معرف_الموظف = %s
            """, (self.employee_id,))
            result = cursor.fetchone()
            transactions_count = result[0] if result else 0
            self.transactions_count_label.setText(str(transactions_count))

            conn.close()

        except Exception as e:
            print(f"خطأ في تحميل الإحصائيات المالية: {e}")

    # تحميل إحصائيات المهام
    def load_tasks_stats(self):
        try:
            if not self.employee_id:
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # إجمالي المهام
            cursor.execute("""
                SELECT COUNT(*)
                FROM المشاريع_مهام_الفريق
                WHERE معرف_الموظف = %s
            """, (self.employee_id,))
            result = cursor.fetchone()
            total_tasks = result[0] if result else 0
            self.total_tasks_label.setText(str(total_tasks))

            # المهام المكتملة
            cursor.execute("""
                SELECT COUNT(*)
                FROM المشاريع_مهام_الفريق
                WHERE معرف_الموظف = %s AND الحالة IN ('مكتملة', 'منتهي')
            """, (self.employee_id,))
            result = cursor.fetchone()
            completed_tasks = result[0] if result else 0
            self.completed_tasks_label.setText(str(completed_tasks))

            # المهام قيد التنفيذ
            cursor.execute("""
                SELECT COUNT(*)
                FROM المشاريع_مهام_الفريق
                WHERE معرف_الموظف = %s AND الحالة = 'قيد التنفيذ'
            """, (self.employee_id,))
            result = cursor.fetchone()
            pending_tasks = result[0] if result else 0
            self.pending_tasks_label.setText(str(pending_tasks))

            # المهام المتأخرة - حساب المهام التي تجاوزت تاريخ الانتهاء
            from datetime import date
            cursor.execute("""
                SELECT COUNT(*)
                FROM المشاريع_مهام_الفريق
                WHERE معرف_الموظف = %s
                AND الحالة IN ('قيد التنفيذ', 'لم يبدأ', 'متأخرة')
                AND تاريخ_الانتهاء < %s
            """, (self.employee_id, date.today()))
            overdue_tasks = cursor.fetchone()[0]

            # تحديث تسميات تاب معلومات الموظف
            if hasattr(self, 'overdue_tasks_label'):
                self.overdue_tasks_label.setText(str(overdue_tasks))

            # تحديث تسميات تاب المهام
            if hasattr(self, 'tasks_total_label'):
                self.tasks_total_label.setText(str(total_tasks))
            if hasattr(self, 'tasks_completed_label'):
                self.tasks_completed_label.setText(str(completed_tasks))
            if hasattr(self, 'tasks_pending_label'):
                self.tasks_pending_label.setText(str(pending_tasks))
            if hasattr(self, 'tasks_overdue_label'):
                self.tasks_overdue_label.setText(str(overdue_tasks))

            conn.close()

        except Exception as e:
            print(f"خطأ في تحميل إحصائيات المهام: {e}")

    # تحديث إحصائيات الحضور والانصراف
    def update_attendance_stats(self):
        try:
            if not self.employee_id:
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # إجمالي أيام الحضور
            cursor.execute("""
                SELECT COUNT(*)
                FROM الموظفين_الحضور_والانصراف
                WHERE معرف_الموظف = %s
            """, (self.employee_id,))
            result = cursor.fetchone()
            total_days = result[0] if result else 0
            if hasattr(self, 'attendance_total_days_label'):
                self.attendance_total_days_label.setText(str(total_days))

            # أيام الحضور الفعلي
            cursor.execute("""
                SELECT COUNT(*)
                FROM الموظفين_الحضور_والانصراف
                WHERE معرف_الموظف = %s AND وقت_الحضور IS NOT NULL
            """, (self.employee_id,))
            result = cursor.fetchone()
            present_days = result[0] if result else 0
            if hasattr(self, 'attendance_present_days_label'):
                self.attendance_present_days_label.setText(str(present_days))

            # أيام التأخير
            cursor.execute("""
                SELECT COUNT(*)
                FROM الموظفين_الحضور_والانصراف
                WHERE معرف_الموظف = %s AND حضور_متأخر = TRUE
            """, (self.employee_id,))
            result = cursor.fetchone()
            late_days = result[0] if result else 0
            if hasattr(self, 'attendance_late_days_label'):
                self.attendance_late_days_label.setText(str(late_days))

            # انصراف مبكر
            cursor.execute("""
                SELECT COUNT(*)
                FROM الموظفين_الحضور_والانصراف
                WHERE معرف_الموظف = %s AND انصراف_مبكر = TRUE
            """, (self.employee_id,))
            result = cursor.fetchone()
            early_leave = result[0] if result else 0
            if hasattr(self, 'attendance_early_leave_label'):
                self.attendance_early_leave_label.setText(str(early_leave))

            conn.close()

        except Exception as e:
            print(f"خطأ في تحديث إحصائيات الحضور: {e}")

    # تحديث إحصائيات التقييم
    def update_evaluation_stats(self):
        try:
            if not self.employee_id:
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # إجمالي التقييمات
            cursor.execute("""
                SELECT COUNT(*)
                FROM الموظفين_التقييم
                WHERE معرف_الموظف = %s
            """, (self.employee_id,))
            total_evaluations = cursor.fetchone()[0]
            if hasattr(self, 'evaluation_total_label'):
                self.evaluation_total_label.setText(str(total_evaluations))

            # التقييمات في الموعد
            cursor.execute("""
                SELECT COUNT(*)
                FROM الموظفين_التقييم
                WHERE معرف_الموظف = %s AND حالة_التسليم IN ('قبل الموعد', 'في الموعد')
            """, (self.employee_id,))
            on_time = cursor.fetchone()[0]
            if hasattr(self, 'evaluation_on_time_label'):
                self.evaluation_on_time_label.setText(str(on_time))

            # التقييمات المتأخرة
            cursor.execute("""
                SELECT COUNT(*)
                FROM الموظفين_التقييم
                WHERE معرف_الموظف = %s AND حالة_التسليم IN ('تسليم متأخر', 'لم يتم التسليم')
            """, (self.employee_id,))
            late_evaluations = cursor.fetchone()[0]
            if hasattr(self, 'evaluation_late_label'):
                self.evaluation_late_label.setText(str(late_evaluations))

            # متوسط النقاط
            cursor.execute("""
                SELECT AVG(النقاط)
                FROM الموظفين_التقييم
                WHERE معرف_الموظف = %s
            """, (self.employee_id,))
            avg_points = cursor.fetchone()[0] or 0
            if hasattr(self, 'evaluation_avg_points_label'):
                self.evaluation_avg_points_label.setText(f"{avg_points:.1f}")

            conn.close()

        except Exception as e:
            print(f"خطأ في تحديث إحصائيات التقييم: {e}")

    # تحميل بيانات المعاملات المالية
    def load_financial_transactions_data(self):
        try:
            if not self.employee_id:
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, نوع_العملية, نوع_المعاملة, النسبة, المبلغ, التاريخ, الوصف
                FROM الموظفين_معاملات_مالية
                WHERE معرف_الموظف = %s
                ORDER BY التاريخ DESC, id DESC
            """, (self.employee_id,))

            rows = cursor.fetchall()
            self.financial_transactions_table.setRowCount(len(rows))

            for row_index, row_data in enumerate(rows):
                # ID (مخفي)
                id_item = QTableWidgetItem(str(row_data[0]))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.financial_transactions_table.setItem(row_index, 0, id_item)

                # الرقم
                number_item = QTableWidgetItem(str(row_index + 1))
                number_item.setTextAlignment(Qt.AlignCenter)
                self.financial_transactions_table.setItem(row_index, 1, number_item)

                # نوع العملية
                operation_type_item = QTableWidgetItem(str(row_data[1] or ""))
                operation_type_item.setTextAlignment(Qt.AlignCenter)
                # تلوين نوع العملية
                if row_data[1] == "إيداع":
                    operation_type_item.setForeground(QBrush(QColor(46, 125, 50)))  # أخضر
                elif row_data[1] in ["سحب", "خصم"]:
                    operation_type_item.setForeground(QBrush(QColor(231, 76, 60)))  # أحمر
                self.financial_transactions_table.setItem(row_index, 2, operation_type_item)

                # نوع المعاملة
                transaction_type_item = QTableWidgetItem(str(row_data[2] or ""))
                transaction_type_item.setTextAlignment(Qt.AlignCenter)
                self.financial_transactions_table.setItem(row_index, 3, transaction_type_item)

                # النسبة
                percentage = row_data[3] or 0
                if percentage == 0:
                    percentage_item = QTableWidgetItem("لا يوجد نسبة")
                    percentage_item.setForeground(QBrush(QColor(149, 165, 166)))  # رمادي
                else:
                    percentage_item = QTableWidgetItem(f"{percentage}%")
                    percentage_item.setForeground(QBrush(QColor(52, 152, 219)))  # أزرق
                percentage_item.setTextAlignment(Qt.AlignCenter)
                self.financial_transactions_table.setItem(row_index, 4, percentage_item)

                # المبلغ
                amount_item = QTableWidgetItem(f"{row_data[4]:,.2f}" if row_data[4] else "0.00")
                amount_item.setTextAlignment(Qt.AlignCenter)
                self.financial_transactions_table.setItem(row_index, 5, amount_item)

                # التاريخ
                date_item = QTableWidgetItem(str(row_data[5]) if row_data[5] else "")
                date_item.setTextAlignment(Qt.AlignCenter)
                self.financial_transactions_table.setItem(row_index, 6, date_item)

                # الوصف
                description_item = QTableWidgetItem(str(row_data[6] or ""))
                description_item.setTextAlignment(Qt.AlignCenter)
                self.financial_transactions_table.setItem(row_index, 7, description_item)

            # تحديث إحصائيات المعاملات المالية
            self.update_financial_transactions_stats()

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل المعاملات المالية: {str(e)}")

    # تحديث إحصائيات المعاملات المالية
    def update_financial_transactions_stats(self):
        try:
            if not self.employee_id:
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # إجمالي الإيداعات
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0)
                FROM الموظفين_معاملات_مالية
                WHERE معرف_الموظف = %s AND نوع_العملية = 'إيداع'
            """, (self.employee_id,))
            total_deposits = cursor.fetchone()[0]
            self.financial_total_deposits_label.setText(f"{total_deposits:,.2f}  {Currency_type}")

            # إجمالي السحوبات
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0)
                FROM الموظفين_معاملات_مالية
                WHERE معرف_الموظف = %s AND نوع_العملية IN ('سحب', 'خصم')
            """, (self.employee_id,))
            total_withdrawals = cursor.fetchone()[0]
            self.financial_total_withdrawals_label.setText(f"{total_withdrawals:,.2f}  {Currency_type}")

            # الرصيد الصافي
            net_balance = total_deposits - total_withdrawals
            self.financial_net_balance_label.setText(f"{net_balance:,.2f}  {Currency_type}")
            # تطبيق الأنماط الديناميكية للرصيد الصافي
            self.financial_net_balance_label._is_balance = True
            apply_dynamic_label_styles(self.financial_net_balance_label, f"{net_balance:,.2f}  {Currency_type}")

            # عدد المعاملات
            cursor.execute("""
                SELECT COUNT(*)
                FROM الموظفين_معاملات_مالية
                WHERE معرف_الموظف = %s
            """, (self.employee_id,))
            transactions_count = cursor.fetchone()[0]
            self.financial_transactions_count_label.setText(str(transactions_count))

            conn.close()

        except Exception as e:
            print(f"خطأ في تحديث إحصائيات المعاملات المالية: {e}")

    # تحميل بيانات مهام الموظف
    def load_employee_tasks_data(self):
        try:
            if not self.employee_id:
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    مم.id,
                    CASE
                        WHEN مم.نوع_المهمة = 'مهمة عامة' THEN 'غير مرتبطة بمشروع'
                        ELSE COALESCE(مش.اسم_المشروع, 'غير محدد')
                    END as اسم_المشروع,
                    CASE
                        WHEN مم.نوع_المهمة = 'مهمة عامة' THEN 'غير مرتبطة بمشروع'
                        ELSE COALESCE(ع.اسم_العميل, 'غير محدد')
                    END as اسم_العميل,
                    CASE
                        WHEN COALESCE(مم.نوع_دور_المهمة, 'دور_عام') = 'ربط_بمرحلة'
                        THEN COALESCE(مر.اسم_المرحلة, مم.عنوان_المهمة, 'غير محدد')
                        ELSE COALESCE(مم.عنوان_المهمة, 'غير محدد')
                    END as اسم_المهمة,
                    CASE
                        WHEN COALESCE(مم.نوع_دور_المهمة, 'دور_عام') = 'ربط_بمرحلة'
                        THEN COALESCE(مر.وصف_المرحلة, مم.وصف_المهمة, '')
                        ELSE COALESCE(مم.وصف_المهمة, '')
                    END as وصف_المهمة,
                    COALESCE(مم.نسبة_الموظف, 0) as النسبة,
                    COALESCE(مم.مبلغ_الموظف, 0) as المبلغ,
                    COALESCE(مم.حالة_مبلغ_الموظف, 'غير مدرج') as حالة_المبلغ,
                    مم.تاريخ_البدء,
                    مم.تاريخ_الانتهاء,
                    مم.الحالة,
                    مم.ملاحظات,
                    CASE
                        WHEN مم.نوع_المهمة = 'مهمة عامة' THEN 'مهمة عامة'
                        WHEN مم.نوع_المهمة = 'مهمة مشروع' THEN CONCAT('مشروع: ', COALESCE(مش.اسم_المشروع, 'غير محدد'))
                        WHEN مم.نوع_المهمة = 'مهمة مقاولات' THEN CONCAT('مقاولات: ', COALESCE(مش.اسم_المشروع, 'غير محدد'))
                        ELSE 'غير محدد'
                    END as نوع_المهمة_عرض
                FROM المشاريع_مهام_الفريق مم
                LEFT JOIN المشاريع مش ON مم.معرف_المشروع = مش.id
                LEFT JOIN العملاء ع ON مش.معرف_العميل = ع.id
                LEFT JOIN المشاريع_المراحل مر ON مم.معرف_المرحلة = مر.id
                WHERE مم.معرف_الموظف = %s
                ORDER BY مم.تاريخ_البدء DESC, مم.id DESC
            """, (self.employee_id,))

            rows = cursor.fetchall()
            self.employee_tasks_table.setRowCount(len(rows))

            for row_index, row_data in enumerate(rows):
                # ID (مخفي)
                id_item = QTableWidgetItem(str(row_data[0]))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.employee_tasks_table.setItem(row_index, 0, id_item)

                # الرقم
                number_item = QTableWidgetItem(str(row_index + 1))
                number_item.setTextAlignment(Qt.AlignCenter)
                self.employee_tasks_table.setItem(row_index, 1, number_item)

                # اسم المشروع
                project_item = QTableWidgetItem(str(row_data[1] or ""))
                project_item.setTextAlignment(Qt.AlignCenter)
                self.employee_tasks_table.setItem(row_index, 2, project_item)

                # العميل
                client_item = QTableWidgetItem(str(row_data[2] or ""))
                client_item.setTextAlignment(Qt.AlignCenter)
                self.employee_tasks_table.setItem(row_index, 3, client_item)

                # اسم المهمة
                task_name_item = QTableWidgetItem(str(row_data[3] or ""))
                task_name_item.setTextAlignment(Qt.AlignCenter)
                self.employee_tasks_table.setItem(row_index, 4, task_name_item)

                # وصف المهمة
                task_desc_item = QTableWidgetItem(str(row_data[4] or ""))
                task_desc_item.setTextAlignment(Qt.AlignCenter)
                self.employee_tasks_table.setItem(row_index, 5, task_desc_item)

                # النسبة
                percentage_item = QTableWidgetItem(f"{row_data[5]}%" if row_data[5] else "0%")
                percentage_item.setTextAlignment(Qt.AlignCenter)
                self.employee_tasks_table.setItem(row_index, 6, percentage_item)

                # المبلغ
                amount_item = QTableWidgetItem(f"{row_data[6]:.2f}" if row_data[6] else "0.00")
                amount_item.setTextAlignment(Qt.AlignCenter)
                self.employee_tasks_table.setItem(row_index, 7, amount_item)

                # حالة المبلغ مع تلوين
                amount_status_item = QTableWidgetItem(str(row_data[7] or "غير مدرج"))
                amount_status_item.setTextAlignment(Qt.AlignCenter)
                if row_data[7] == "غير مدرج":
                    amount_status_item.setForeground(QBrush(QColor(231, 76, 60)))  # أحمر
                elif row_data[7] == "تم الإدراج":
                    amount_status_item.setForeground(QBrush(QColor(46, 125, 50)))  # أخضر
                self.employee_tasks_table.setItem(row_index, 8, amount_status_item)

                # تاريخ البدء
                start_date_item = QTableWidgetItem(str(row_data[8]) if row_data[8] else "")
                start_date_item.setTextAlignment(Qt.AlignCenter)
                self.employee_tasks_table.setItem(row_index, 9, start_date_item)

                # تاريخ الانتهاء
                end_date_item = QTableWidgetItem(str(row_data[9]) if row_data[9] else "")
                end_date_item.setTextAlignment(Qt.AlignCenter)
                self.employee_tasks_table.setItem(row_index, 10, end_date_item)

                # الحالة مع تلوين
                status_item = QTableWidgetItem(str(row_data[10] or ""))
                status_item.setTextAlignment(Qt.AlignCenter)
                status_color = self.get_task_status_color(row_data[10])
                status_item.setForeground(QBrush(QColor(status_color)))
                self.employee_tasks_table.setItem(row_index, 11, status_item)

                # ملاحظات
                notes_item = QTableWidgetItem(str(row_data[11] or ""))
                notes_item.setTextAlignment(Qt.AlignCenter)
                self.employee_tasks_table.setItem(row_index, 12, notes_item)

                # نوع المهمة
                task_type_item = QTableWidgetItem(str(row_data[12] or ""))
                task_type_item.setTextAlignment(Qt.AlignCenter)
                self.employee_tasks_table.setItem(row_index, 13, task_type_item)

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل مهام الموظف: {str(e)}")

    # إدراج رصيد المهمة المحددة إلى حساب الموظف
    def insert_selected_task_balance(self):
        try:
            current_row = self.employee_tasks_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "تحذير", "يرجى تحديد مهمة لإدراج رصيدها")
                return

            # الحصول على معرف المهمة
            task_id_item = self.employee_tasks_table.item(current_row, 0)
            if not task_id_item:
                QMessageBox.warning(self, "تحذير", "لا يمكن الحصول على معرف المهمة")
                return

            task_id = int(task_id_item.text())

            # التحقق من حالة المبلغ
            amount_status_item = self.employee_tasks_table.item(current_row, 8)
            if amount_status_item and amount_status_item.text() == "تم الإدراج":
                QMessageBox.information(self, "معلومات", "تم إدراج رصيد هذه المهمة مسبقاً")
                return

            # الحصول على بيانات المهمة
            task_name = self.employee_tasks_table.item(current_row, 4).text()
            amount_item = self.employee_tasks_table.item(current_row, 7)
            amount = float(amount_item.text()) if amount_item.text() else 0.0

            if amount <= 0:
                QMessageBox.warning(self, "تحذير", "لا يوجد مبلغ لإدراجه في هذه المهمة")
                return

            # تأكيد الإدراج
            reply = QMessageBox.question(
                self, "تأكيد الإدراج",
                f"هل تريد إدراج رصيد المهمة '{task_name}' بمبلغ {amount:.2f} إلى حساب الموظف؟",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self._insert_task_balance(task_id, task_name, amount)

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في إدراج رصيد المهمة: {str(e)}")

    # إدراج جميع أرصدة المهام غير المدرجة إلى حساب الموظف
    def insert_all_task_balances(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # جلب المهام غير المدرجة
            cursor.execute("""
                SELECT id, عنوان_المهمة, مبلغ_الموظف
                FROM المشاريع_مهام_الفريق
                WHERE معرف_الموظف = %s
                AND حالة_مبلغ_الموظف = 'غير مدرج'
                AND مبلغ_الموظف > 0
            """, (self.employee_id,))

            tasks = cursor.fetchall()
            conn.close()

            if not tasks:
                QMessageBox.information(self, "معلومات", "جميع أرصدة المهام تم إدراجها مسبقاً أو لا توجد مهام بمبالغ")
                return

            # حساب إجمالي المبلغ
            total_amount = sum(task[2] for task in tasks)
            task_count = len(tasks)

            # تأكيد الإدراج
            reply = QMessageBox.question(
                self, "تأكيد الإدراج",
                f"هل تريد إدراج أرصدة {task_count} مهمة بإجمالي {total_amount:.2f} إلى حساب الموظف؟",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                for task_id, task_name, amount in tasks:
                    self._insert_task_balance(task_id, task_name, amount)

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في إدراج أرصدة المهام: {str(e)}")

    # دالة مساعدة لإدراج رصيد مهمة واحدة
    def _insert_task_balance(self, task_id, task_name, amount):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # إضافة معاملة مالية للموظف
            cursor.execute("""
                INSERT INTO الموظفين_معاملات_مالية
                (معرف_الموظف, نوع_العملية, نوع_المعاملة, المبلغ, الوصف, المستخدم)
                VALUES (%s, 'إيداع', 'رصيد مهمة', %s, %s, 'admin')
            """, (self.employee_id, amount, f"رصيد مهمة: {task_name}"))

            # تحديث حالة المبلغ في المهمة
            cursor.execute("""
                UPDATE المشاريع_مهام_الفريق
                SET حالة_مبلغ_الموظف = 'تم الإدراج'
                WHERE id = %s
            """, (task_id,))

            conn.commit()
            conn.close()

            # تحديث البيانات في الواجهة
            self.load_employee_tasks_data()
            self.load_financial_transactions_data()

            QMessageBox.information(self, "نجح", f"تم إدراج رصيد المهمة '{task_name}' بنجاح")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في إدراج رصيد المهمة: {str(e)}")

    # الحصول على لون حالة المهمة
    def get_task_status_color(self, status):
        status_colors = {
            "مكتملة": "#27ae60",
            "قيد التنفيذ": "#f39c12",
            "ملغاة": "#95a5a6",
            "متأخرة": "#e74c3c"
        }
        return status_colors.get(status, "#34495e")

    # تحميل بيانات الحضور والانصراف
    def load_attendance_data(self):
        try:
            if not self.employee_id:
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, التاريخ, وقت_الحضور, وقت_الانصراف,
                       حالة_الحضور, مدة_تأخير_الحضور, مدة_تبكير_الحضور,
                       حالة_الانصراف, مدة_تأخير_الانصراف, مدة_تبكير_الانصراف,
                       ملاحظات
                FROM الموظفين_الحضور_والانصراف
                WHERE معرف_الموظف = %s
                ORDER BY التاريخ DESC, id DESC
            """, (self.employee_id,))

            rows = cursor.fetchall()
            self.attendance_table.setRowCount(len(rows))

            # أسماء الأيام بالعربية
            day_names = {
                0: 'الاثنين',
                1: 'الثلاثاء',
                2: 'الأربعاء',
                3: 'الخميس',
                4: 'الجمعة',
                5: 'السبت',
                6: 'الأحد'
            }

            for row_index, row_data in enumerate(rows):
                # ID (مخفي)
                id_item = QTableWidgetItem(str(row_data[0]))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.attendance_table.setItem(row_index, 0, id_item)

                # الرقم
                number_item = QTableWidgetItem(str(row_index + 1))
                number_item.setTextAlignment(Qt.AlignCenter)
                self.attendance_table.setItem(row_index, 1, number_item)

                # التاريخ
                date_item = QTableWidgetItem(str(row_data[1]) if row_data[1] else "")
                date_item.setTextAlignment(Qt.AlignCenter)
                self.attendance_table.setItem(row_index, 2, date_item)

                # اليوم
                day_name = ""
                if row_data[1]:  # إذا كان هناك تاريخ
                    try:
                        from datetime import datetime
                        date_obj = datetime.strptime(str(row_data[1]), '%Y-%m-%d')
                        day_name = day_names.get(date_obj.weekday(), "غير محدد")
                    except:
                        day_name = "غير محدد"

                day_item = QTableWidgetItem(day_name)
                day_item.setTextAlignment(Qt.AlignCenter)
                self.attendance_table.setItem(row_index, 3, day_item)

                # وقت الحضور - تحويل إلى نظام 12 ساعة
                checkin_time_str = "لم يسجل"
                if row_data[2]:
                    try:
                        from datetime import datetime
                        time_obj = datetime.strptime(str(row_data[2]), '%H:%M:%S')
                        checkin_time_str = time_obj.strftime('%I:%M %p')
                        # تحويل AM/PM إلى العربية
                        checkin_time_str = checkin_time_str.replace('AM', 'ص').replace('PM', 'م')
                    except:
                        checkin_time_str = str(row_data[2])

                checkin_item = QTableWidgetItem(checkin_time_str)
                checkin_item.setTextAlignment(Qt.AlignCenter)
                self.attendance_table.setItem(row_index, 4, checkin_item)

                # وقت الانصراف - تحويل إلى نظام 12 ساعة
                checkout_time_str = "لم يسجل"
                if row_data[3]:
                    try:
                        from datetime import datetime
                        time_obj = datetime.strptime(str(row_data[3]), '%H:%M:%S')
                        checkout_time_str = time_obj.strftime('%I:%M %p')
                        # تحويل AM/PM إلى العربية
                        checkout_time_str = checkout_time_str.replace('AM', 'ص').replace('PM', 'م')
                    except:
                        checkout_time_str = str(row_data[3])

                checkout_item = QTableWidgetItem(checkout_time_str)
                checkout_item.setTextAlignment(Qt.AlignCenter)
                self.attendance_table.setItem(row_index, 5, checkout_item)

                # حالة الحضور والمدة
                checkin_status = row_data[4] if row_data[4] else "غير محدد"
                checkin_late_minutes = row_data[5] or 0
                checkin_early_minutes = row_data[6] or 0

                # تحديد لون حالة الحضور
                checkin_status_item = QTableWidgetItem(checkin_status)
                checkin_status_item.setTextAlignment(Qt.AlignCenter)

                if checkin_status == "مبكر":
                    checkin_status_item.setForeground(QBrush(QColor(46, 125, 50)))  # أخضر
                elif checkin_status == "متأخر":
                    checkin_status_item.setForeground(QBrush(QColor(231, 76, 60)))  # أحمر
                else:
                    checkin_status_item.setForeground(QBrush(QColor(52, 73, 94)))  # رمادي

                self.attendance_table.setItem(row_index, 6, checkin_status_item)

                # مدة التأخير/التبكير للحضور
                from نظام_الحضور_المطور import AdvancedAttendanceSystem

                if checkin_status == "متأخر" and checkin_late_minutes > 0:
                    duration_text = AdvancedAttendanceSystem.format_duration(checkin_late_minutes)
                    duration_text = f"تأخير: {duration_text}"
                    color = QColor(231, 76, 60)  # أحمر
                elif checkin_status == "مبكر" and checkin_early_minutes > 0:
                    duration_text = AdvancedAttendanceSystem.format_duration(checkin_early_minutes)
                    duration_text = f"تبكير: {duration_text}"
                    color = QColor(46, 125, 50)  # أخضر
                else:
                    duration_text = "في الموعد"
                    color = QColor(52, 73, 94)  # رمادي

                checkin_duration_item = QTableWidgetItem(duration_text)
                checkin_duration_item.setTextAlignment(Qt.AlignCenter)
                checkin_duration_item.setForeground(QBrush(color))
                self.attendance_table.setItem(row_index, 7, checkin_duration_item)

                # حالة الانصراف والمدة
                checkout_status = row_data[7] if row_data[7] else "غير محدد"
                checkout_late_minutes = row_data[8] or 0
                checkout_early_minutes = row_data[9] or 0

                # تحديد لون حالة الانصراف
                checkout_status_item = QTableWidgetItem(checkout_status)
                checkout_status_item.setTextAlignment(Qt.AlignCenter)

                if checkout_status == "متأخر":
                    checkout_status_item.setForeground(QBrush(QColor(46, 125, 50)))  # أخضر
                elif checkout_status == "مبكر":
                    checkout_status_item.setForeground(QBrush(QColor(231, 76, 60)))  # أحمر
                else:
                    checkout_status_item.setForeground(QBrush(QColor(52, 73, 94)))  # رمادي

                self.attendance_table.setItem(row_index, 8, checkout_status_item)

                # مدة التأخير/التبكير للانصراف
                if checkout_status == "متأخر" and checkout_late_minutes > 0:
                    duration_text = AdvancedAttendanceSystem.format_duration(checkout_late_minutes)
                    duration_text = f"تأخير: {duration_text}"
                    color = QColor(46, 125, 50)  # أخضر
                elif checkout_status == "مبكر" and checkout_early_minutes > 0:
                    duration_text = AdvancedAttendanceSystem.format_duration(checkout_early_minutes)
                    duration_text = f"تبكير: {duration_text}"
                    color = QColor(231, 76, 60)  # أحمر
                else:
                    duration_text = "في الموعد"
                    color = QColor(52, 73, 94)  # رمادي

                checkout_duration_item = QTableWidgetItem(duration_text)
                checkout_duration_item.setTextAlignment(Qt.AlignCenter)
                checkout_duration_item.setForeground(QBrush(color))
                self.attendance_table.setItem(row_index, 9, checkout_duration_item)

                # ملاحظات
                notes_item = QTableWidgetItem(str(row_data[10] or ""))
                notes_item.setTextAlignment(Qt.AlignCenter)
                self.attendance_table.setItem(row_index, 10, notes_item)

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل بيانات الحضور والانصراف: {str(e)}")

    # تحميل بيانات التقييم
    def load_evaluation_data(self):
        try:
            if not self.employee_id:
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, حالة_التسليم, النقاط
                FROM الموظفين_التقييم
                WHERE معرف_الموظف = %s
                ORDER BY id DESC
            """, (self.employee_id,))

            rows = cursor.fetchall()
            self.evaluation_table.setRowCount(len(rows))

            for row_index, row_data in enumerate(rows):
                # ID (مخفي)
                id_item = QTableWidgetItem(str(row_data[0]))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.evaluation_table.setItem(row_index, 0, id_item)

                # الرقم
                number_item = QTableWidgetItem(str(row_index + 1))
                number_item.setTextAlignment(Qt.AlignCenter)
                self.evaluation_table.setItem(row_index, 1, number_item)

                # حالة التسليم مع تلوين
                delivery_status_item = QTableWidgetItem(str(row_data[1] or ""))
                delivery_status_item.setTextAlignment(Qt.AlignCenter)
                status_color = self.get_delivery_status_color(row_data[1])
                delivery_status_item.setForeground(QBrush(QColor(status_color)))
                self.evaluation_table.setItem(row_index, 2, delivery_status_item)

                # النقاط
                points_item = QTableWidgetItem(str(row_data[2] or "0"))
                points_item.setTextAlignment(Qt.AlignCenter)
                self.evaluation_table.setItem(row_index, 3, points_item)

                # تاريخ التقييم (افتراضي - يمكن إضافة عمود للتاريخ في قاعدة البيانات لاحقاً)
                eval_date_item = QTableWidgetItem("غير محدد")
                eval_date_item.setTextAlignment(Qt.AlignCenter)
                self.evaluation_table.setItem(row_index, 4, eval_date_item)

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل بيانات التقييم: {str(e)}")

    # الحصول على لون حالة التسليم
    def get_delivery_status_color(self, status):
        status_colors = {
            "قبل الموعد": "#27ae60",
            "في الموعد": "#2ecc71",
            "تسليم متأخر": "#f39c12",
            "لم يتم التسليم": "#e74c3c"
        }
        return status_colors.get(status, "#34495e")

    # ==================== دوال النقر المزدوج للجداول ====================

    # معالج النقر المزدوج على جدول المعاملات المالية
    def on_financial_transactions_table_double_click(self, item):
        if item is not None:
            self.edit_financial_transaction()

    # معالج النقر المزدوج على جدول مهام الموظف
    def on_employee_tasks_table_double_click(self, item):
        if item is not None:
            self.edit_employee_task()

    # معالج النقر المزدوج على جدول الحضور والانصراف
    def on_attendance_table_double_click(self, item):
        if item is not None:
            self.edit_attendance_record()

    # معالج النقر المزدوج على جدول التقييم
    def on_evaluation_table_double_click(self, item):
        if item is not None:
            self.edit_evaluation()

    # ==================== دوال الإجراءات ====================

    # إضافة معاملة مالية جديدة
    def add_financial_transaction(self):
        try:
            dialog = FinancialTransactionDialog(self, employee_id=self.employee_id)
            if dialog.exec() == QDialog.Accepted:
                self.load_financial_transactions_data()
                self.load_financial_stats()  # تحديث الإحصائيات
                self.load_employee_info()  # تحديث الرصيد
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في فتح حوار إضافة المعاملة المالية: {str(e)}")

    # تعديل معاملة مالية موجودة
    def edit_financial_transaction(self):
        try:
            current_row = self.financial_transactions_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "تحذير", "يرجى تحديد معاملة مالية للتعديل")
                return

            transaction_id_item = self.financial_transactions_table.item(current_row, 0)
            if not transaction_id_item:
                QMessageBox.warning(self, "تحذير", "لا يمكن الحصول على معرف المعاملة المالية")
                return

            transaction_id = int(transaction_id_item.text())
            dialog = FinancialTransactionDialog(self, employee_id=self.employee_id, transaction_id=transaction_id)
            if dialog.exec() == QDialog.Accepted:
                self.load_financial_transactions_data()
                self.load_financial_stats()  # تحديث الإحصائيات
                self.load_employee_info()  # تحديث الرصيد
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في فتح حوار تعديل المعاملة المالية: {str(e)}")

    # إضافة مهمة جديدة للموظف
    def add_employee_task(self):
        try:
            dialog = UnifiedTaskDialog(self, employee_id=self.employee_id, context="employee")
            if dialog.exec() == QDialog.Accepted:
                self.load_employee_tasks_data()
                self.load_tasks_stats()  # تحديث إحصائيات المهام
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في فتح حوار إضافة المهمة: {str(e)}")

    # تعديل مهمة موجودة للموظف
    def edit_employee_task(self):
        try:
            current_row = self.employee_tasks_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "تحذير", "يرجى تحديد مهمة للتعديل")
                return

            task_id_item = self.employee_tasks_table.item(current_row, 0)
            if not task_id_item:
                QMessageBox.warning(self, "تحذير", "لا يمكن الحصول على معرف المهمة")
                return

            task_id = int(task_id_item.text())
            dialog = UnifiedTaskDialog(self, employee_id=self.employee_id, task_id=task_id, context="employee")
            if dialog.exec() == QDialog.Accepted:
                self.load_employee_tasks_data()
                self.load_tasks_stats()  # تحديث إحصائيات المهام
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في فتح حوار تعديل المهمة: {str(e)}")

    # إضافة سجل حضور وانصراف جديد
    def add_attendance_record(self):
        try:
            dialog = AttendanceDialog(self, employee_id=self.employee_id)
            if dialog.exec() == QDialog.Accepted:
                self.load_attendance_data()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في فتح حوار إضافة سجل الحضور: {str(e)}")

    # تعديل سجل حضور وانصراف موجود
    def edit_attendance_record(self):
        try:
            current_row = self.attendance_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "تحذير", "يرجى تحديد سجل حضور للتعديل")
                return

            attendance_id_item = self.attendance_table.item(current_row, 0)
            if not attendance_id_item:
                QMessageBox.warning(self, "تحذير", "لا يمكن الحصول على معرف سجل الحضور")
                return

            attendance_id = int(attendance_id_item.text())
            dialog = AttendanceDialog(self, employee_id=self.employee_id, attendance_id=attendance_id)
            if dialog.exec() == QDialog.Accepted:
                self.load_attendance_data()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في فتح حوار تعديل سجل الحضور: {str(e)}")

    # إضافة تقييم جديد
    def add_evaluation(self):
        try:
            dialog = EvaluationDialog(self, employee_id=self.employee_id)
            if dialog.exec() == QDialog.Accepted:
                self.load_evaluation_data()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في فتح حوار إضافة التقييم: {str(e)}")

    # تعديل تقييم موجود
    def edit_evaluation(self):
        try:
            current_row = self.evaluation_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "تحذير", "يرجى تحديد تقييم للتعديل")
                return

            evaluation_id_item = self.evaluation_table.item(current_row, 0)
            if not evaluation_id_item:
                QMessageBox.warning(self, "تحذير", "لا يمكن الحصول على معرف التقييم")
                return

            evaluation_id = int(evaluation_id_item.text())
            dialog = EvaluationDialog(self, employee_id=self.employee_id, evaluation_id=evaluation_id)
            if dialog.exec() == QDialog.Accepted:
                self.load_evaluation_data()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في فتح حوار تعديل التقييم: {str(e)}")

    # تعديل بيانات الموظف الأساسية
    def edit_employee_data(self):
        try:
            # فتح نافذة تعديل الموظف باستخدام AddEntryDialog
            from الأدوات import AddEntryDialog

            dialog = AddEntryDialog(
                main_window=self.parent,
                section_name="الموظفين",
                parent=self,
                entry_data=self.employee_data,
                row_id=self.employee_id
            )

            if dialog.exec() == QDialog.Accepted:
                # إعادة تحميل بيانات الموظف بعد التعديل
                self.load_employee_info()
                # تحديث البيانات في النافذة الأب إذا كانت موجودة
                if hasattr(self.parent, 'show_section'):
                    self.parent.show_section("الموظفين")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في فتح نافذة تعديل الموظف: {str(e)}")

    # تغيير حالة الموظف
    def change_employee_status(self):
        try:
            # إنشاء حوار تغيير الحالة
            dialog = QDialog(self)
            dialog.setWindowTitle("تغيير حالة الموظف")
            dialog.setGeometry(300, 300, 400, 200)
            dialog.setLayoutDirection(Qt.RightToLeft)
            dialog.setModal(True)

            layout = QVBoxLayout(dialog)
            layout.setSpacing(15)

            # تسمية توضيحية
            info_label = QLabel("اختر الحالة الجديدة للموظف:")
            info_label.setObjectName("info-label")
            layout.addWidget(info_label)

            # قائمة الحالات
            status_combo = QComboBox()
            status_combo.addItems(["نشط", "غير نشط", "إجازة", "مستقيل", "تم فصله"])
            status_combo.setObjectName("status-combo")

            # تحديد الحالة الحالية
            current_status = self.employee_status_label.text()
            if current_status in ["نشط", "غير نشط", "إجازة", "مستقيل", "تم فصله"]:
                status_combo.setCurrentText(current_status)

            layout.addWidget(status_combo)

            # أزرار الحوار
            buttons_layout = QHBoxLayout()

            save_btn = QPushButton("حفظ")
            save_btn.setObjectName("save-btn")

            cancel_btn = QPushButton("إلغاء")
            cancel_btn.setObjectName("cancel-btn")

            save_btn.clicked.connect(dialog.accept)
            cancel_btn.clicked.connect(dialog.reject)

            buttons_layout.addWidget(save_btn)
            buttons_layout.addWidget(cancel_btn)
            layout.addLayout(buttons_layout)

            # تطبيق الأنماط المركزية على الحوار
            apply_dialog_styles(dialog)

            if dialog.exec() == QDialog.Accepted:
                # حفظ الحالة الجديدة
                new_status = status_combo.currentText()
                self.save_employee_status(new_status)

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في فتح حوار تغيير الحالة: {str(e)}")

    # حفظ حالة الموظف الجديدة
    def save_employee_status(self, new_status):
        try:
            conn = mysql.connector.connect(
                host=host, user=user, password=password,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE الموظفين
                SET الحالة = %s
                WHERE id = %s
            """, (new_status, self.employee_id))

            conn.commit()
            conn.close()

            # تحديث العرض
            self.load_employee_info()

            QMessageBox.information(self, "نجح", f"تم تغيير حالة الموظف إلى: {new_status}")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ حالة الموظف: {str(e)}")

    # تصفية المعاملات المالية
    def filter_financial_transactions(self):
        try:
            search_text = self.financial_search_edit.text().lower()
            operation_filter = self.financial_operation_combo.currentText()
            transaction_filter = self.financial_transaction_combo.currentText()

            for row in range(self.financial_transactions_table.rowCount()):
                show_row = True

                # فلتر البحث
                if search_text:
                    row_text = ""
                    for col in range(self.financial_transactions_table.columnCount()):
                        item = self.financial_transactions_table.item(row, col)
                        if item:
                            row_text += item.text().lower() + " "

                    if search_text not in row_text:
                        show_row = False

                # فلتر نوع العملية
                if operation_filter != "جميع العمليات" and show_row:
                    operation_item = self.financial_transactions_table.item(row, 2)
                    if operation_item and operation_item.text() != operation_filter:
                        show_row = False

                # فلتر نوع المعاملة
                if transaction_filter != "جميع المعاملات" and show_row:
                    transaction_item = self.financial_transactions_table.item(row, 3)
                    if transaction_item and transaction_item.text() != transaction_filter:
                        show_row = False

                self.financial_transactions_table.setRowHidden(row, not show_row)

        except Exception as e:
            print(f"خطأ في تصفية المعاملات المالية: {e}")

    # تصفية مهام الموظف
    def filter_employee_tasks(self):
        try:
            search_text = self.tasks_search_edit.text().lower()
            status_filter = self.tasks_status_combo.currentText()
            type_filter = self.tasks_type_combo.currentText() if hasattr(self, 'tasks_type_combo') else "جميع الأنواع"

            for row in range(self.employee_tasks_table.rowCount()):
                show_row = True

                # فلتر البحث
                if search_text:
                    row_text = ""
                    for col in range(self.employee_tasks_table.columnCount()):
                        item = self.employee_tasks_table.item(row, col)
                        if item:
                            row_text += item.text().lower() + " "

                    if search_text not in row_text:
                        show_row = False

                # فلتر الحالة
                if status_filter != "جميع الحالات" and show_row:
                    status_item = self.employee_tasks_table.item(row, 6)
                    if status_item and status_item.text() != status_filter:
                        show_row = False

                # فلتر نوع المهمة
                if type_filter != "جميع الأنواع" and show_row:
                    type_item = self.employee_tasks_table.item(row, 8)  # عمود نوع المهمة
                    if type_item:
                        task_type = type_item.text()
                        # تحويل نوع المهمة للعرض
                        display_type = ""
                        if "مهمة عامة" in task_type:
                            display_type = "مهمة عامة"
                        elif "مهمة مشروع" in task_type:
                            display_type = "مشروع"
                        elif "مهمة مقاولات" in task_type:
                            display_type = "مقاولات"

                        if type_filter != display_type:
                            show_row = False

                self.employee_tasks_table.setRowHidden(row, not show_row)

        except Exception as e:
            print(f"خطأ في تصفية مهام الموظف: {e}")

    # تصفية الحضور والانصراف
    def filter_attendance(self):
        try:
            search_text = self.attendance_search_edit.text().lower()
            month_filter = self.attendance_month_combo.currentText()

            # تحويل أسماء الشهور العربية إلى أرقام
            months_map = {
                "يناير": "01", "فبراير": "02", "مارس": "03", "أبريل": "04",
                "مايو": "05", "يونيو": "06", "يوليو": "07", "أغسطس": "08",
                "سبتمبر": "09", "أكتوبر": "10", "نوفمبر": "11", "ديسمبر": "12"
            }

            for row in range(self.attendance_table.rowCount()):
                show_row = True

                # فلتر البحث
                if search_text:
                    row_text = ""
                    for col in range(self.attendance_table.columnCount()):
                        item = self.attendance_table.item(row, col)
                        if item:
                            row_text += item.text().lower() + " "

                    if search_text not in row_text:
                        show_row = False

                # فلتر الشهر
                if month_filter != "جميع الشهور" and show_row:
                    date_item = self.attendance_table.item(row, 2)
                    if date_item and date_item.text():
                        try:
                            date_parts = date_item.text().split('-')
                            if len(date_parts) >= 2:
                                month_num = date_parts[1]
                                if month_num != months_map.get(month_filter, ""):
                                    show_row = False
                        except:
                            pass

                self.attendance_table.setRowHidden(row, not show_row)

        except Exception as e:
            print(f"خطأ في تصفية الحضور والانصراف: {e}")

    # تصفية التقييمات
    def filter_evaluation(self):
        try:
            search_text = self.evaluation_search_edit.text().lower()
            delivery_filter = self.evaluation_delivery_combo.currentText()

            for row in range(self.evaluation_table.rowCount()):
                show_row = True

                # فلتر البحث
                if search_text:
                    row_text = ""
                    for col in range(self.evaluation_table.columnCount()):
                        item = self.evaluation_table.item(row, col)
                        if item:
                            row_text += item.text().lower() + " "

                    if search_text not in row_text:
                        show_row = False

                # فلتر حالة التسليم
                if delivery_filter != "جميع الحالات" and show_row:
                    delivery_item = self.evaluation_table.item(row, 2)
                    if delivery_item and delivery_item.text() != delivery_filter:
                        show_row = False

                self.evaluation_table.setRowHidden(row, not show_row)

        except Exception as e:
            print(f"خطأ في تصفية التقييمات: {e}")

    # ==================== الأنماط المركزية ====================

    # إضافة أزرار الطباعة لجميع التابات
    def add_print_buttons(self):
        try:
            # إضافة أزرار الطباعة تلقائياً لجميع التابات
            quick_add_print_button(self, self.tab_widget)

        except Exception as e:
            print(f"خطأ في إضافة أزرار الطباعة: {e}")

# ==================== حوارات الإدارة ====================

# حوار إضافة/تعديل معاملة مالية
class FinancialTransactionDialog(QDialog):

    # init
    def __init__(self, parent=None, employee_id=None, transaction_id=None):
        super().__init__(parent)
        self.employee_id = employee_id
        self.transaction_id = transaction_id
        self.is_edit_mode = transaction_id is not None
        self.employee_data = {}

        self.setup_dialog()
        self.load_employee_data()
        self.create_ui()
        self.setup_connections()

        if self.is_edit_mode:
            self.load_transaction_data()
        else:
            # تحديث خيارات نوع المعاملة عند فتح الحوار لأول مرة
            self.update_transaction_type_options()

        # تطبيق الأنماط المركزية
        apply_dialog_styles(self)

        apply_stylesheet(self)

    # إعداد الحوار
    def setup_dialog(self):
        title = "تعديل معاملة مالية" if self.is_edit_mode else "إضافة معاملة مالية جديدة"
        self.setWindowTitle(title)
        self.setGeometry(200, 200, 600, 550)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setModal(True)

    # تحميل بيانات الموظف
    def load_employee_data(self):
        try:
            if not self.employee_id:
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT اسم_الموظف, المرتب, النسبة, الرصيد
                FROM الموظفين
                WHERE id = %s
            """, (self.employee_id,))

            data = cursor.fetchone()
            if data:
                self.employee_data = {
                    'اسم_الموظف': data[0],
                    'المرتب': float(data[1] or 0),
                    'النسبة': float(data[2] or 0),
                    'الرصيد': float(data[3] or 0)
                }

            conn.close()

        except Exception as e:
            print(f"خطأ في تحميل بيانات الموظف: {e}")
            self.employee_data = {
                'اسم_الموظف': 'غير محدد',
                'المرتب': 0.0,
                'النسبة': 0.0,
                'الرصيد': 0.0
            }

    # إنشاء واجهة المستخدم
    def create_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # معلومات الموظف
        # employee_info_layout = QHBoxLayout()
        # employee_name_label = QLabel(f"الموظف: {self.employee_data.get('اسم_الموظف', 'غير محدد')}")

        # employee_info_layout.addWidget(employee_name_label)
        # employee_info_layout.addStretch()
        # layout.addLayout(employee_info_layout)

        # نموذج البيانات
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # نوع العملية
        self.operation_type_combo = QComboBox()
        self.operation_type_combo.addItems(["إيداع", "سحب", "خصم"])
        form_layout.addRow("نوع العملية:", self.operation_type_combo)

        # نوع المعاملة
        self.transaction_type_combo = QComboBox()
        form_layout.addRow("نوع المعاملة:", self.transaction_type_combo)

        # حقل النسبة (مخفي افتراضياً)

        self.percentage_spinbox = QDoubleSpinBox()
        self.percentage_spinbox.setRange(0, 100)
        self.percentage_spinbox.setDecimals(2)
        self.percentage_spinbox.setSuffix("%")
        self.percentage_spinbox.setValue(self.employee_data.get('النسبة', 0))        

        form_layout.addRow("النسبة:", self.percentage_spinbox)
        self.percentage_spinbox.setVisible(False)

        # المبلغ
        amount_layout = QHBoxLayout()
        self.amount_spinbox = QDoubleSpinBox()
        self.amount_spinbox.setRange(0, 999999999)
        self.amount_spinbox.setDecimals(2)
        self.amount_spinbox.setSuffix(f" {Currency_type}")

        # self.auto_fill_btn = QPushButton("تعبئة تلقائية")
        # self.auto_fill_btn.setMaximumWidth(100)


        amount_layout.addWidget(self.amount_spinbox)
        #amount_layout.addWidget(self.auto_fill_btn)
        form_layout.addRow("المبلغ:", amount_layout)

        # التاريخ
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("التاريخ:", self.date_edit)

        # الوصف (تم تغييره إلى QLineEdit)
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("أدخل وصف المعاملة...")
        form_layout.addRow("الوصف:", self.description_edit)

        layout.addLayout(form_layout)

        # أزرار الحوار
        buttons_layout = QHBoxLayout()

        save_btn = QPushButton("حفظ")
        save_btn.clicked.connect(self.save_transaction)
        save_btn.setObjectName("save-btn")

        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setObjectName("cancel-btn")

        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)

    # إعداد الاتصالات بين العناصر
    def setup_connections(self):
        # ربط تغيير نوع العملية بتحديث خيارات نوع المعاملة
        self.operation_type_combo.currentTextChanged.connect(self.update_transaction_type_options)

        # ربط تغيير نوع المعاملة بالتعبئة التلقائية
        self.transaction_type_combo.currentTextChanged.connect(self.on_transaction_type_changed)

        # ربط زر التعبئة التلقائية
        #self.auto_fill_btn.clicked.connect(self.auto_fill_amount)

        # ربط تغيير النسبة بحساب المبلغ
        self.percentage_spinbox.valueChanged.connect(self.calculate_percentage_amount)

    # تحديث خيارات نوع المعاملة حسب نوع العملية
    def update_transaction_type_options(self):
        operation_type = self.operation_type_combo.currentText()

        # مسح الخيارات الحالية
        self.transaction_type_combo.clear()

        if operation_type == "إيداع":
            self.transaction_type_combo.addItems([
                "إيداع مبلغ",
                "إيداع مرتب",
                "إيداع نسبة%"
            ])
        elif operation_type == "سحب":
            self.transaction_type_combo.addItems([
                "سحب مبلغ"
            ])
        elif operation_type == "خصم":
            self.transaction_type_combo.addItems([
                "خصم مبلغ",
                "خصم نسبة%"
            ])

        # تحديث حالة العناصر
        self.on_transaction_type_changed()

    # معالج تغيير نوع المعاملة
    def on_transaction_type_changed(self):
        transaction_type = self.transaction_type_combo.currentText()

        # إظهار/إخفاء حقل النسبة
        if "نسبة%" in transaction_type:
            self.percentage_spinbox.setVisible(True)
            self.calculate_percentage_amount()
        else:
            self.percentage_spinbox.setVisible(False)

        # تحديث الوصف التلقائي
        self.update_description()

        # التعبئة التلقائية للمبلغ
        self.auto_fill_amount()

    # تحديث الوصف التلقائي
    def update_description(self):
        if self.is_edit_mode:
            return  # لا نحدث الوصف في وضع التعديل

        transaction_type = self.transaction_type_combo.currentText()
        employee_name = self.employee_data.get('اسم_الموظف', 'الموظف')

        descriptions = {
            "إيداع مرتب": f"إيداع مرتب شهري للموظف {employee_name}",
            "إيداع مبلغ": f"إيداع مبلغ محدد للموظف {employee_name}",
            "إيداع نسبة%": f"إيداع نسبة مئوية للموظف {employee_name}",
            "سحب مبلغ": f"سحب مبلغ محدد للموظف {employee_name}",
            "خصم مبلغ": f"خصم مبلغ محدد من الموظف {employee_name}",
            "خصم نسبة%": f"خصم نسبة مئوية من الموظف {employee_name}"
        }

        description = descriptions.get(transaction_type, "")
        if description and not self.description_edit.text():
            self.description_edit.setText(description)

    # التعبئة التلقائية للمبلغ
    def auto_fill_amount(self):
        transaction_type = self.transaction_type_combo.currentText()

        if transaction_type == "إيداع مرتب":
            salary = self.employee_data.get('المرتب', 0)
            if salary > 0:
                self.amount_spinbox.setValue(salary)
        elif transaction_type == "سحب مبلغ":
            balance = self.employee_data.get('الرصيد', 0)
            if balance > 0:
                self.amount_spinbox.setValue(min(balance, 1000))  # حد أقصى 1000 للسحب
        elif "نسبة%" in transaction_type:
            self.calculate_percentage_amount()

    # حساب المبلغ من النسبة
    def calculate_percentage_amount(self):
        transaction_type = self.transaction_type_combo.currentText()

        if "نسبة%" not in transaction_type:
            return

        percentage = self.percentage_spinbox.value()

        if transaction_type == "إيداع نسبة%":
            # حساب النسبة من المرتب
            salary = self.employee_data.get('المرتب', 0)
            if salary > 0 and percentage > 0:
                amount = (salary * percentage) / 100
                self.amount_spinbox.setValue(amount)
        elif transaction_type == "خصم نسبة%":
            # حساب النسبة من الرصيد أو المرتب
            base_amount = max(self.employee_data.get('الرصيد', 0), self.employee_data.get('المرتب', 0))
            if base_amount > 0 and percentage > 0:
                amount = (base_amount * percentage) / 100
                self.amount_spinbox.setValue(amount)

    # تحميل بيانات المعاملة للتعديل
    def load_transaction_data(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT نوع_العملية, نوع_المعاملة, النسبة, المبلغ, التاريخ, الوصف
                FROM الموظفين_معاملات_مالية
                WHERE id = %s
            """, (self.transaction_id,))

            data = cursor.fetchone()
            if data:
                # تعيين نوع العملية أولاً لتحديث الخيارات
                self.operation_type_combo.setCurrentText(data[0] or "إيداع")

                # تحديث خيارات نوع المعاملة
                self.update_transaction_type_options()

                # تعيين باقي القيم
                self.transaction_type_combo.setCurrentText(data[1] or "")

                # تعيين النسبة
                percentage = data[2] or 0
                self.percentage_spinbox.setValue(percentage)

                # إظهار حقل النسبة إذا كانت المعاملة تتطلب نسبة
                if "نسبة%" in (data[1] or ""):
                    self.percentage_spinbox.setVisible(True)

                self.amount_spinbox.setValue(float(data[3] or 0))
                if data[4]:
                    self.date_edit.setDate(QDate.fromString(str(data[4]), "yyyy-MM-dd"))
                self.description_edit.setText(data[5] or "")

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل بيانات المعاملة: {str(e)}")

    # حساب النسبة من المبلغ (للتعديل)
    def calculate_percentage_from_amount(self, amount):
        transaction_type = self.transaction_type_combo.currentText()

        if "نسبة%" not in transaction_type:
            return

        if transaction_type == "إيداع نسبة%":
            salary = self.employee_data.get('المرتب', 0)
            if salary > 0:
                percentage = (amount * 100) / salary
                self.percentage_spinbox.setValue(percentage)
        elif transaction_type == "خصم نسبة%":
            base_amount = max(self.employee_data.get('الرصيد', 0), self.employee_data.get('المرتب', 0))
            if base_amount > 0:
                percentage = (amount * 100) / base_amount
                self.percentage_spinbox.setValue(percentage)

    # حفظ المعاملة المالية
    def save_transaction(self):
        #try:
            # التحقق من صحة البيانات
            if self.amount_spinbox.value() <= 0:
                QMessageBox.warning(self, "تحذير", "يجب إدخال مبلغ صحيح")
                return

            if not self.description_edit.text().strip():
                QMessageBox.warning(self, "تحذير", "يجب إدخال وصف للمعاملة")
                return
            
            operation_type = self.operation_type_combo.currentText()
            transaction_type = self.transaction_type_combo.currentText()
            amount = self.amount_spinbox.value()
            date = self.date_edit.date().toString("yyyy-MM-dd")
            description = self.description_edit.text().strip()
                        
            conn = mysql.connector.connect(
                host=host, user=user, password=password,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # الحصول على النسبة إذا كانت المعاملة تتطلب نسبة
            percentage = 0
            if "نسبة%" in transaction_type:
                percentage = self.percentage_spinbox.value()

            if self.is_edit_mode:
                # تحديث المعاملة الموجودة
                cursor.execute("""
                    UPDATE الموظفين_معاملات_مالية
                    SET نوع_العملية = %s, نوع_المعاملة = %s, النسبة = %s, المبلغ = %s,
                        التاريخ = %s, الوصف = %s
                    WHERE id = %s
                """, (operation_type, transaction_type, percentage, amount, date, description, self.transaction_id))
            else:
                # إضافة معاملة جديدة
                cursor.execute("""
                    INSERT INTO الموظفين_معاملات_مالية
                    (معرف_الموظف, نوع_العملية, نوع_المعاملة, النسبة, المبلغ, التاريخ, الوصف, المستخدم)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (self.employee_id, operation_type, transaction_type, percentage, amount, date, description, "النظام"))
        
            # تحديث رصيد الموظف
            self.update_employee_balance(cursor, operation_type, amount)

            conn.commit()
            conn.close()

            QMessageBox.information(self, "نجح", "تم حفظ المعاملة المالية بنجاح")
            self.accept()

        # except Exception as e:
        #     QMessageBox.critical(self, "خطأ", f"فشل في حفظ المعاملة المالية: {str(e)}")

    # تحديث رصيد الموظف
    def update_employee_balance(self, cursor, operation_type, amount):
        try:
            if operation_type == "إيداع":
                # زيادة الرصيد
                cursor.execute("""
                    UPDATE الموظفين
                    SET الرصيد = الرصيد + %s
                    WHERE id = %s
                """, (amount, self.employee_id))
            elif operation_type in ["سحب", "خصم"]:
                # تقليل الرصيد
                cursor.execute("""
                    UPDATE الموظفين
                    SET الرصيد = الرصيد - %s
                    WHERE id = %s
                """, (amount, self.employee_id))
        except Exception as e:
            print(f"خطأ في تحديث رصيد الموظف: {e}")

# حوار موحد لإضافة/تعديل المهام - يدعم المهام العامة والمرتبطة بالمشاريع
class UnifiedTaskDialog(QDialog):

    # init
    def __init__(self, parent=None, employee_id=None, task_id=None, project_id=None, context="employee"):
        super().__init__(parent)
        self.employee_id = employee_id
        self.task_id = task_id
        self.project_id = project_id
        self.context = context  # "employee" أو "project"
        self.is_edit_mode = task_id is not None
        self.project_type = None

        # تحديد نوع المشروع إذا كان السياق مشروع
        if self.context == "project" and self.project_id:
            self.project_type = self.get_project_type()

        self.setup_dialog()
        self.create_ui()
        self.setup_connections()

        if self.is_edit_mode:
            self.load_task_data()
        else:
            self.set_default_values()

        # تطبيق الأنماط المركزية
        apply_dialog_styles(self)

    # تحديد نوع المشروع (المشاريع/المقاولات)
    def get_project_type(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("SELECT اسم_القسم FROM المشاريع WHERE id = %s", (self.project_id,))
            result = cursor.fetchone()
            conn.close()

            return result[0] if result else "المشاريع"
        except Exception as e:
            print(f"خطأ في تحديد نوع المشروع: {e}")
            return "المشاريع"

    # إعداد الحوار
    def setup_dialog(self):
        if self.context == "employee":
            title = "تعديل مهمة الموظف" if self.is_edit_mode else "إضافة مهمة جديدة للموظف"
        else:
            title = "تعديل عضو فريق العمل" if self.is_edit_mode else "إضافة عضو فريق عمل"

        self.setWindowTitle(title)
        self.setGeometry(200, 200, 700, 600)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setModal(True)

    # إنشاء واجهة المستخدم
    def create_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # عنوان الحوار
        title_label = QLabel()
        if self.context == "employee":
            title_label.setText("تعديل مهمة الموظف" if self.is_edit_mode else "إضافة مهمة جديدة للموظف")
        else:
            title_label.setText("تعديل عضو فريق العمل" if self.is_edit_mode else "إضافة عضو فريق عمل")

        title_label.setObjectName("section_title")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # إنشاء المحتوى في نافذة واحدة
        self.create_unified_content(layout)

        # أزرار الحفظ والإلغاء
        self.create_buttons(layout)

    # إنشاء المحتوى الموحد في نافذة واحدة
    def create_unified_content(self, parent_layout):
        # إنشاء scroll area للمحتوى
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # إنشاء widget المحتوى
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(15, 15, 15, 15)

        # إضافة المعلومات الأساسية
        self.create_basic_info_section(content_layout)

        # إضافة معلومات المشروع (إذا كانت مطلوبة)
        self.create_project_info_section(content_layout)

        # إضافة المعلومات المالية (فقط في سياق المشروع)
        if self.context == "project":
            self.create_financial_info_section(content_layout)

        # إضافة معلومات الجدولة الزمنية
        self.create_scheduling_info_section(content_layout)

        scroll_area.setWidget(content_widget)
        parent_layout.addWidget(scroll_area)

    # إنشاء قسم المعلومات الأساسية
    def create_basic_info_section(self, parent_layout):
        # إنشاء مجموعة للمعلومات الأساسية
        basic_group = QGroupBox("المعلومات الأساسية")
        basic_layout = QFormLayout(basic_group)
        basic_layout.setSpacing(10)

        # نوع العضو واختيار الموظف (فقط في سياق المشروع)
        if self.context == "project":
            # نوع العضو
            self.member_type_combo = QComboBox()
            self.member_type_combo.addItems(["مهندس", "مقاول", "عامل", "موظف"])
            self.member_type_combo.currentTextChanged.connect(self.on_member_type_changed)
            basic_layout.addRow("نوع العضو:", self.member_type_combo)

            # اختيار عضو فريق العمل
            self.employee_combo = QComboBox()
            self.employee_combo.addItem("-- اختر عضو فريق العمل --", None)
            basic_layout.addRow("عضو فريق العمل:", self.employee_combo)
        else:
            # في سياق الموظف، إنشاء الحقول مخفية للاستخدام الداخلي
            self.member_type_combo = QComboBox()
            self.member_type_combo.addItems(["مهندس", "مقاول", "عامل", "موظف"])
            self.member_type_combo.setVisible(False)  # مخفي

            self.employee_combo = QComboBox()
            self.employee_combo.setVisible(False)  # مخفي

        # نوع المهمة (فقط في سياق الموظف)
        if self.context == "employee":
            self.task_type_combo = QComboBox()
            self.task_type_combo.addItems(["مهمة عامة", "مهمة مرتبطة بمشروع", "مهمة مرتبطة بمقاولات"])
            self.task_type_combo.currentTextChanged.connect(self.on_task_type_changed)
            basic_layout.addRow("نوع المهمة:", self.task_type_combo)

        # عنوان المهمة
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("أدخل عنوان المهمة...")
        basic_layout.addRow("عنوان المهمة:", self.title_edit)

        # وصف المهمة
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        self.description_edit.setPlaceholderText("أدخل وصف المهمة...")
        basic_layout.addRow("وصف المهمة:", self.description_edit)

        parent_layout.addWidget(basic_group)

    # إنشاء قسم معلومات المشروع
    def create_project_info_section(self, parent_layout):
        # إنشاء مجموعة لمعلومات المشروع
        self.project_group = QGroupBox("معلومات المشروع")
        project_layout = QFormLayout(self.project_group)
        project_layout.setSpacing(10)

        # اختيار المشروع (فقط في سياق الموظف)
        if self.context == "employee":
            self.project_combo = QComboBox()
            self.project_combo.addItem("-- اختر مشروع --", None)
            self.load_projects()
            self.project_combo.currentIndexChanged.connect(self.on_project_changed)
            project_layout.addRow("المشروع:", self.project_combo)

        # اختيار المرحلة
        self.phase_combo = QComboBox()
        self.phase_combo.addItem("-- اختر مرحلة --", None)
        project_layout.addRow("المرحلة:", self.phase_combo)

        parent_layout.addWidget(self.project_group)

    # إنشاء قسم المعلومات المالية
    def create_financial_info_section(self, parent_layout):
        # إنشاء مجموعة للمعلومات المالية
        financial_group = QGroupBox("المعلومات المالية")
        financial_layout = QFormLayout(financial_group)
        financial_layout.setSpacing(10)

        # نسبة الموظف
        self.percentage_spin = QDoubleSpinBox()
        self.percentage_spin.setRange(0, 100)
        self.percentage_spin.setSuffix("%")
        financial_layout.addRow("نسبة الموظف:", self.percentage_spin)

        # مبلغ الموظف
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, 999999999)
        self.amount_spin.setSuffix(" ريال")
        financial_layout.addRow("مبلغ الموظف:", self.amount_spin)

        # حالة المبلغ
        self.amount_status_combo = QComboBox()
        self.amount_status_combo.addItems(["غير مدرج", "تم الإدراج"])
        financial_layout.addRow("حالة المبلغ:", self.amount_status_combo)

        parent_layout.addWidget(financial_group)

    # إنشاء قسم معلومات الجدولة الزمنية
    def create_scheduling_info_section(self, parent_layout):
        # إنشاء مجموعة لمعلومات الجدولة
        schedule_group = QGroupBox("الجدولة الزمنية")
        schedule_layout = QFormLayout(schedule_group)
        schedule_layout.setSpacing(10)

        # تاريخ البدء
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("dd/MM/yyyy")
        schedule_layout.addRow("تاريخ البدء:", self.start_date)

        # تاريخ الانتهاء
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate().addDays(30))
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        schedule_layout.addRow("تاريخ الانتهاء:", self.end_date)

        # حالة المهمة
        self.status_combo = QComboBox()
        self.status_combo.addItems(["لم يبدأ", "قيد التنفيذ", "مكتملة", "ملغاة", "متأخرة", "متوقف"])
        schedule_layout.addRow("الحالة:", self.status_combo)

        # ملاحظات
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlaceholderText("أدخل ملاحظات إضافية...")
        schedule_layout.addRow("ملاحظات:", self.notes_edit)

        parent_layout.addWidget(schedule_group)

    # الحصول على نوع المشروع
    def get_project_type(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("SELECT اسم_القسم FROM المشاريع WHERE id = %s", (self.project_id,))
            result = cursor.fetchone()
            conn.close()

            return result[0] if result else "المشاريع"
        except Exception:
            return "المشاريع"

    # تحميل قائمة الموظفين مفلترة حسب نوع العضو
    def load_employees(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # الحصول على نوع العضو المحدد
            member_type = self.member_type_combo.currentText()

            # تحميل الموظفين مفلترين حسب التصنيف
            cursor.execute("""
                SELECT id, اسم_الموظف, الوظيفة, النسبة, التصنيف
                FROM الموظفين
                WHERE الحالة = 'نشط' AND التصنيف = %s
                ORDER BY اسم_الموظف
            """, (member_type,))

            employees = cursor.fetchall()

            # الاحتفاظ بالاختيار الحالي إذا وجد
            current_selection = self.employee_combo.currentData()
            self.employee_combo.clear()

            # تحديد النص المناسب للخيار الفارغ
            if self.context == "project":
                empty_text = "-- اختر عضو فريق العمل --"
            else:
                empty_text = "-- اختر الموظف --"

            self.employee_combo.addItem(empty_text, None)

            for emp_id, name, job, default_percentage, classification in employees:
                # تنسيق العرض: اسم الموظف - الوظيفة
                if job:
                    display_text = f"{name} - {job}"
                else:
                    display_text = name

                self.employee_combo.addItem(display_text, emp_id)

                # حفظ البيانات الإضافية للتعبئة التلقائية
                self.employee_combo.setItemData(self.employee_combo.count() - 1,
                                              {
                                                  'id': emp_id,
                                                  'default_percentage': default_percentage or 0,
                                                  'classification': classification
                                              },
                                              Qt.UserRole + 1)

            # استعادة الاختيار السابق إذا كان متاحاً
            if current_selection:
                for i in range(self.employee_combo.count()):
                    if self.employee_combo.itemData(i) == current_selection:
                        self.employee_combo.setCurrentIndex(i)
                        break

            # ربط إشارة تغيير الاختيار للتعبئة التلقائية
            if not hasattr(self, '_employee_combo_connected'):
                self.employee_combo.currentIndexChanged.connect(self.on_employee_changed)
                self._employee_combo_connected = True

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل قائمة الموظفين: {str(e)}")

    # معالج تغيير نوع العضو - تحديث قائمة الموظفين
    def on_member_type_changed(self):
        self.load_employees()

    # معالج تغيير الموظف - تعبئة النسبة الافتراضية
    def on_employee_changed(self):
        try:
            # الحصول على البيانات الإضافية للموظف المحدد
            current_data = self.employee_combo.currentData(Qt.UserRole + 1)

            if current_data and isinstance(current_data, dict) and self.context == "project":
                default_percentage = current_data.get('default_percentage', 0)

                # تعبئة النسبة الافتراضية فقط إذا كانت أكبر من صفر
                if default_percentage > 0:
                    # في وضع الإضافة، أو في وضع التعديل عند تغيير الموظف
                    if not self.is_edit_mode or getattr(self, '_employee_changed_manually', True):
                        self.percentage_spin.setValue(default_percentage)

        except Exception as e:
            print(f"خطأ في تعبئة النسبة الافتراضية: {e}")

    # تحميل قائمة المشاريع والمقاولات
    def load_projects(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # تحميل المشاريع والمقاولات من نفس الجدول
            cursor.execute("""
                SELECT id, اسم_المشروع, اسم_القسم
                FROM المشاريع
                WHERE اسم_القسم IN ('المشاريع', 'المقاولات')
                ORDER BY اسم_القسم, اسم_المشروع
            """)

            projects = cursor.fetchall()
            self.project_combo.clear()
            self.project_combo.addItem("-- اختر مشروع --", None)

            for proj_id, name, section in projects:
                display_text = f"[{section}] {name}"
                self.project_combo.addItem(display_text, proj_id)

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل قائمة المشاريع: {str(e)}")

    # تحميل مراحل المشروع
    def load_project_phases(self, project_id):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, اسم_المرحلة, وصف_المرحلة
                FROM المشاريع_المراحل
                WHERE معرف_المشروع = %s
                ORDER BY اسم_المرحلة
            """, (project_id,))

            phases = cursor.fetchall()
            self.phase_combo.clear()
            self.phase_combo.addItem("-- اختر مرحلة --", None)

            for phase_id, name, description in phases:
                display_text = f"{name}"
                if description:
                    display_text += f" - {description}"
                self.phase_combo.addItem(display_text, phase_id)

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل مراحل المشروع: {str(e)}")

    # إعداد الاتصالات بين العناصر
    def setup_connections(self):
        # ربط إشارة تغيير المشروع
        if hasattr(self, 'project_combo'):
            self.project_combo.currentIndexChanged.connect(self.on_project_changed)

        # ربط إشارة تغيير نوع المهمة
        if hasattr(self, 'task_type_combo'):
            self.task_type_combo.currentTextChanged.connect(self.on_task_type_changed)

    # تحميل بيانات المهمة للتعديل
    def load_task_data(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT مم.معرف_الموظف, مم.نوع_المهمة, مم.معرف_المشروع, مم.معرف_المرحلة, مم.عنوان_المهمة,
                       مم.وصف_المهمة, م.التصنيف as نوع_العضو, مم.نسبة_الموظف, مم.مبلغ_الموظف,
                       مم.حالة_مبلغ_الموظف, مم.تاريخ_البدء, مم.تاريخ_الانتهاء, مم.الحالة, مم.ملاحظات
                FROM المشاريع_مهام_الفريق مم
                JOIN الموظفين م ON مم.معرف_الموظف = م.id
                WHERE مم.id = %s
            """, (self.task_id,))

            data = cursor.fetchone()
            if data:
                employee_id, task_type, project_id, phase_id, title, description, member_type, percentage, amount, amount_status, start_date, end_date, status, notes = data

                # تعيين البيانات الأساسية
                self.title_edit.setText(title or "")
                self.description_edit.setPlainText(description or "")

                # تعيين نوع المهمة (في سياق الموظف)
                if self.context == "employee" and hasattr(self, 'task_type_combo'):
                    if task_type == "مهمة عامة":
                        self.task_type_combo.setCurrentText("مهمة عامة")
                    elif task_type == "مهمة مشروع":
                        self.task_type_combo.setCurrentText("مهمة مرتبطة بمشروع")
                    elif task_type == "مهمة مقاولات":
                        self.task_type_combo.setCurrentText("مهمة مرتبطة بمقاولات")

                # تعيين نوع العضو والموظف حسب السياق
                if self.context == "project":
                    # في سياق المشروع، تعيين نوع العضو وإعادة تحميل الموظفين
                    self.member_type_combo.setCurrentText(member_type or "موظف")
                    self.load_employees()  # إعادة تحميل الموظفين بناءً على النوع

                    # تعيين الموظف
                    self._employee_changed_manually = False  # تعطيل التعبئة التلقائية مؤقتاً
                    for i in range(self.employee_combo.count()):
                        if self.employee_combo.itemData(i) == employee_id:
                            self.employee_combo.setCurrentIndex(i)
                            break
                    self._employee_changed_manually = True  # تفعيل التعبئة التلقائية مرة أخرى
                else:
                    # في سياق الموظف، تعيين القيم مخفية
                    self.member_type_combo.setCurrentText(member_type or "موظف")
                    self.employee_combo.clear()
                    self.employee_combo.addItem("الموظف الحالي", employee_id)

                # تعيين المشروع والمرحلة
                if project_id and hasattr(self, 'project_combo'):
                    for i in range(self.project_combo.count()):
                        if self.project_combo.itemData(i) == project_id:
                            self.project_combo.setCurrentIndex(i)
                            self.load_project_phases(project_id)
                            break

                if phase_id and hasattr(self, 'phase_combo'):
                    for i in range(self.phase_combo.count()):
                        if self.phase_combo.itemData(i) == phase_id:
                            self.phase_combo.setCurrentIndex(i)
                            break

                # تعيين المعلومات المالية
                if hasattr(self, 'percentage_spin'):
                    self.percentage_spin.setValue(float(percentage) if percentage else 0.0)
                if hasattr(self, 'amount_spin'):
                    self.amount_spin.setValue(float(amount) if amount else 0.0)
                if hasattr(self, 'amount_status_combo'):
                    self.amount_status_combo.setCurrentText(amount_status or "غير مدرج")

                # تعيين التواريخ
                if start_date:
                    self.start_date.setDate(QDate.fromString(str(start_date), "yyyy-MM-dd"))
                if end_date:
                    self.end_date.setDate(QDate.fromString(str(end_date), "yyyy-MM-dd"))

                # تعيين الحالة والملاحظات
                self.status_combo.setCurrentText(status or "قيد التنفيذ")
                self.notes_edit.setPlainText(notes or "")

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل بيانات المهمة: {str(e)}")

    # تعيين القيم الافتراضية
    def set_default_values(self):
        # تعيين التواريخ الافتراضية
        self.start_date.setDate(QDate.currentDate())
        self.end_date.setDate(QDate.currentDate().addDays(30))

        # تعيين الحالة الافتراضية
        self.status_combo.setCurrentText("قيد التنفيذ")

        # إخفاء قسم معلومات المشروع في البداية (للمهام العامة)
        if self.context == "employee" and hasattr(self, 'project_group'):
            self.project_group.setVisible(False)

    # إنشاء أزرار الحفظ والإلغاء
    def create_buttons(self, parent_layout):
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        # زر الحفظ
        save_button = QPushButton("حفظ")
        save_button.setObjectName("save_button")
        save_button.clicked.connect(self.save_task)
        buttons_layout.addWidget(save_button)

        # زر الإلغاء
        cancel_button = QPushButton("إلغاء")
        cancel_button.setObjectName("cancel_button")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        # إضافة مساحة فارغة لدفع الأزرار إلى اليمين
        buttons_layout.addStretch()

        parent_layout.addLayout(buttons_layout)

    # إنشاء تاب المعلومات الأساسية
    def create_basic_info_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # نموذج البيانات الأساسية
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # نوع المهمة (فقط في سياق الموظف)
        if self.context == "employee":
            self.task_type_combo = QComboBox()
            self.task_type_combo.addItems(["مهمة عامة", "مهمة مرتبطة بمشروع", "مهمة مرتبطة بمقاولات"])
            self.task_type_combo.currentTextChanged.connect(self.on_task_type_changed)
            form_layout.addRow("نوع المهمة:", self.task_type_combo)

        # اختيار الموظف (فقط في سياق المشروع)
        if self.context == "project":
            self.employee_combo = QComboBox()
            self.load_employees()
            form_layout.addRow("عضو فريق العمل:", self.employee_combo)

        # عنوان المهمة
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("أدخل عنوان المهمة...")
        form_layout.addRow("عنوان المهمة:", self.title_edit)

        # وصف المهمة
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        self.description_edit.setPlaceholderText("أدخل وصف المهمة...")
        form_layout.addRow("وصف المهمة:", self.description_edit)

        # تاريخ البدء
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow("تاريخ البدء:", self.start_date_edit)

        # تاريخ الانتهاء
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate().addDays(30))
        self.end_date_edit.setCalendarPopup(True)
        form_layout.addRow("تاريخ الانتهاء:", self.end_date_edit)

        # الحالة
        self.status_combo = QComboBox()
        self.status_combo.addItems(["قيد التنفيذ", "مكتملة", "ملغاة", "متأخرة"])
        form_layout.addRow("الحالة:", self.status_combo)

        # ملاحظات
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        form_layout.addRow("ملاحظات:", self.notes_edit)

        layout.addLayout(form_layout)
        self.tab_widget.addTab(tab, "المعلومات الأساسية")

    # إنشاء تاب معلومات المشروع
    def create_project_info_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # اختيار المشروع/المقاولات (في سياق الموظف)
        if self.context == "employee":
            self.project_combo = QComboBox()
            self.project_combo.addItem("-- اختر مشروع/مقاولات --", None)
            self.load_projects_contracts()
            self.project_combo.currentIndexChanged.connect(self.on_project_changed)
            form_layout.addRow("المشروع/المقاولات:", self.project_combo)

        # اختيار المرحلة
        self.phase_combo = QComboBox()
        self.phase_combo.addItem("-- اختر مرحلة --", None)
        form_layout.addRow("المرحلة:", self.phase_combo)

        layout.addLayout(form_layout)
        self.tab_widget.addTab(tab, "معلومات المشروع")

    # إنشاء تاب المعلومات المالية (فقط للمشاريع)
    def create_financial_info_tab(self):
        if self.context != "project":
            return

        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # نوع العضو
        self.member_type_combo = QComboBox()
        self.member_type_combo.addItems(["مهندس", "مقاول", "عامل", "موظف"])
        form_layout.addRow("نوع العضو:", self.member_type_combo)

        # نسبة الموظف
        self.percentage_spin = QSpinBox()
        self.percentage_spin.setRange(0, 100)
        self.percentage_spin.setSuffix("%")
        form_layout.addRow("نسبة الموظف:", self.percentage_spin)

        # مبلغ الموظف
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, 999999999)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setSuffix(f" {Currency_type}")
        form_layout.addRow("مبلغ الموظف:", self.amount_spin)

        # حالة المبلغ
        self.amount_status_combo = QComboBox()
        self.amount_status_combo.addItems(["غير مدرج", "تم الإدراج"])
        form_layout.addRow("حالة المبلغ:", self.amount_status_combo)

        layout.addLayout(form_layout)
        self.tab_widget.addTab(tab, "المعلومات المالية")

    # إنشاء أزرار الحفظ والإلغاء
    def create_buttons(self, parent_layout):
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        save_btn = QPushButton("حفظ")
        save_btn.clicked.connect(self.save_task)
        save_btn.setObjectName("save-btn")

        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setObjectName("cancel-btn")

        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        parent_layout.addLayout(buttons_layout)

    # إعداد الاتصالات
    def setup_connections(self):
        if self.context == "employee" and hasattr(self, 'task_type_combo'):
            self.task_type_combo.currentTextChanged.connect(self.on_task_type_changed)

    # تعيين القيم الافتراضية
    def set_default_values(self):
        if self.context == "project":
            # للمشاريع، تعيين "مهندس" كافتراضي وتحميل الموظفين
            self.member_type_combo.setCurrentText("مهندس")
            self.load_employees()
        elif self.context == "employee":
            # في سياق الموظف، تحديد نوع العضو والموظف تلقائياً
            self.set_employee_defaults()

        if self.context == "employee" and hasattr(self, 'task_type_combo'):
            self.task_type_combo.setCurrentText("مهمة عامة")
            self.on_task_type_changed("مهمة عامة")

        # تعيين القيم الافتراضية للمشاريع
        if self.context == "project":
            if hasattr(self, 'member_type_combo'):
                self.member_type_combo.setCurrentText("موظف")
            if hasattr(self, 'amount_status_combo'):
                self.amount_status_combo.setCurrentText("غير مدرج")

    # تحديد نوع العضو والموظف تلقائياً في سياق الموظف
    def set_employee_defaults(self):
        try:
            if not hasattr(self, 'employee_id') or not self.employee_id:
                return

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # جلب بيانات الموظف الحالي
            cursor.execute("""
                SELECT اسم_الموظف, الوظيفة, التصنيف
                FROM الموظفين
                WHERE id = %s
            """, (self.employee_id,))

            result = cursor.fetchone()
            if result:
                employee_name, job_title, classification = result

                # تحديد نوع العضو بناءً على تصنيف الموظف
                member_type = classification or "موظف"
                self.member_type_combo.setCurrentText(member_type)

                # إضافة الموظف الحالي إلى الكومبو بوكس
                self.employee_combo.clear()
                display_text = f"{employee_name} - {job_title}" if job_title else employee_name
                self.employee_combo.addItem(display_text, self.employee_id)
                self.employee_combo.setCurrentIndex(0)

            conn.close()

        except Exception as e:
            print(f"خطأ في تحديد بيانات الموظف الافتراضية: {e}")
            # في حالة الخطأ، استخدام القيم الافتراضية
            self.member_type_combo.setCurrentText("موظف")
            self.employee_combo.clear()
            self.employee_combo.addItem("موظف غير محدد", self.employee_id if hasattr(self, 'employee_id') else None)

    # تغيير نوع المهمة
    def on_task_type_changed(self, task_type):
        if not hasattr(self, 'project_group'):
            return

        if task_type == "مهمة عامة":
            # إخفاء قسم معلومات المشروع
            self.project_group.setVisible(False)
        else:
            # إظهار قسم معلومات المشروع
            self.project_group.setVisible(True)

    # تغيير المشروع المحدد
    def on_project_changed(self):
        if hasattr(self, 'project_combo'):
            project_id = self.project_combo.currentData()
            if project_id:
                self.load_project_phases(project_id)
            else:
                self.phase_combo.clear()
                self.phase_combo.addItem("-- اختر مرحلة --", None)

    # تحميل قائمة الموظفين مفلترة حسب نوع العضو المحدد
    def load_employees(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # الحصول على نوع العضو المحدد للتصفية
            member_type = self.member_type_combo.currentText()

            # الاحتفاظ بالاختيار الحالي إذا وجد
            current_selection = self.employee_combo.currentData()

            # استعلام مفلتر حسب التصنيف المحدد
            cursor.execute("""
                SELECT id, اسم_الموظف, الوظيفة, النسبة, التصنيف
                FROM الموظفين
                WHERE الحالة = 'نشط' AND التصنيف = %s
                ORDER BY اسم_الموظف
            """, (member_type,))

            employees = cursor.fetchall()
            self.employee_combo.clear()

            # تحديد النص المناسب للخيار الفارغ حسب السياق
            if self.context == "project":
                empty_text = "-- اختر عضو فريق العمل --"
            else:
                empty_text = "-- اختر الموظف --"

            self.employee_combo.addItem(empty_text, None)

            for emp_id, name, job, default_percentage, classification in employees:
                # تنسيق العرض: اسم_الموظف - الوظيفة (بدون التصنيف لأنه مفلتر مسبقاً)
                if job:
                    display_text = f"{name} - {job}"
                else:
                    display_text = name

                self.employee_combo.addItem(display_text, emp_id)

                # حفظ البيانات الإضافية للتعبئة التلقائية
                self.employee_combo.setItemData(self.employee_combo.count() - 1,
                                              {
                                                  'id': emp_id,
                                                  'default_percentage': default_percentage or 0,
                                                  'classification': classification
                                              },
                                              Qt.UserRole + 1)

            # استعادة الاختيار السابق إذا كان متاحاً في القائمة المفلترة
            if current_selection:
                for i in range(self.employee_combo.count()):
                    if self.employee_combo.itemData(i) == current_selection:
                        self.employee_combo.setCurrentIndex(i)
                        break

            # ربط إشارة تغيير الاختيار للتعبئة التلقائية (تجنب الربط المتكرر)
            if not hasattr(self, '_employee_combo_connected'):
                self.employee_combo.currentIndexChanged.connect(self.on_employee_changed)
                self._employee_combo_connected = True

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل قائمة الموظفين: {str(e)}")

    # تحميل قائمة المشاريع والمقاولات
    def load_projects_contracts(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # تحميل المشاريع والمقاولات من نفس الجدول
            # في سياق المشروع، نحمل فقط المشاريع من نفس القسم
            if self.context == "project" and self.project_type:
                cursor.execute("""
                    SELECT id, اسم_المشروع, اسم_القسم
                    FROM المشاريع
                    WHERE اسم_القسم = %s
                    ORDER BY اسم_المشروع
                """, (self.project_type,))
            else:
                # في سياق الموظف، نحمل جميع المشاريع والمقاولات
                cursor.execute("""
                    SELECT id, اسم_المشروع, اسم_القسم
                    FROM المشاريع
                    WHERE اسم_القسم IN ('المشاريع', 'المقاولات')
                    ORDER BY اسم_القسم, اسم_المشروع
                """)

            projects = cursor.fetchall()
            self.project_combo.clear()
            self.project_combo.addItem("-- اختر مشروع/مقاولات --", None)

            for proj_id, name, section in projects:
                display_text = f"[{section}] {name}"
                self.project_combo.addItem(display_text, proj_id)

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل قائمة المشاريع: {str(e)}")

    # تحميل مراحل المشروع
    def load_project_phases(self, project_id):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, اسم_المرحلة, وصف_المرحلة
                FROM المشاريع_المراحل
                WHERE معرف_المشروع = %s
                ORDER BY اسم_المرحلة
            """, (project_id,))

            phases = cursor.fetchall()
            self.phase_combo.clear()
            self.phase_combo.addItem("-- اختر مرحلة --", None)

            for phase_id, name, description in phases:
                display_text = f"{name}"
                if description:
                    display_text += f" - {description}"
                self.phase_combo.addItem(display_text, phase_id)

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل مراحل المشروع: {str(e)}")

    # تحميل بيانات المهمة للتعديل
    def load_task_data(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT عنوان_المهمة, وصف_المهمة, تاريخ_البدء, تاريخ_الانتهاء, الحالة, ملاحظات
                FROM المشاريع_مهام_الفريق
                WHERE id = %s
            """, (self.task_id,))

            data = cursor.fetchone()
            if data:
                self.title_edit.setText(data[0] or "")
                self.description_edit.setPlainText(data[1] or "")
                if data[2]:
                    self.start_date_edit.setDate(QDate.fromString(str(data[2]), "yyyy-MM-dd"))
                if data[3]:
                    self.end_date_edit.setDate(QDate.fromString(str(data[3]), "yyyy-MM-dd"))
                self.status_combo.setCurrentText(data[4] or "قيد التنفيذ")
                self.notes_edit.setPlainText(data[5] or "")

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل بيانات المهمة: {str(e)}")

    # حفظ المهمة الموحدة
    def save_task(self):
        try:
            # التحقق من صحة البيانات
            if not self.title_edit.text().strip():
                QMessageBox.warning(self, "تحذير", "يجب إدخال عنوان المهمة")
                return

            # التحقق من التواريخ
            start_date = self.start_date.date()
            end_date = self.end_date.date()
            if start_date > end_date:
                QMessageBox.warning(self, "تحذير", "تاريخ البدء يجب أن يكون قبل تاريخ الانتهاء")
                return

            conn = mysql.connector.connect(
                host=host, user=user, password=password,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            # جمع البيانات الأساسية
            title = self.title_edit.text().strip()
            description = self.description_edit.toPlainText()
            start_date_str = start_date.toString("yyyy-MM-dd")
            end_date_str = end_date.toString("yyyy-MM-dd")
            status = self.status_combo.currentText()
            notes = self.notes_edit.toPlainText()

            # تحديد نوع المهمة والمعرفات
            if self.context == "employee":
                # في سياق الموظف، استخدام معرف الموظف الحالي
                employee_id = self.employee_id

                if hasattr(self, 'task_type_combo'):
                    task_type_text = self.task_type_combo.currentText()
                    if task_type_text == "مهمة عامة":
                        task_type = 'مهمة عامة'
                        project_id = None
                        phase_id = None
                    elif task_type_text in ["مهمة مرتبطة بمشروع", "مهمة مرتبطة بمقاولات"]:
                        project_id = self.project_combo.currentData() if hasattr(self, 'project_combo') else None
                        phase_id = self.phase_combo.currentData() if hasattr(self, 'phase_combo') else None

                        if project_id:
                            # تحديد نوع المهمة بناءً على نوع المشروع/المقاولات المحدد
                            conn_temp = mysql.connector.connect(
                                host=host, user=user_r, password=password_r,
                                database="project_manager_V2"
                            )
                            cursor_temp = conn_temp.cursor()
                            cursor_temp.execute("SELECT اسم_القسم FROM المشاريع WHERE id = %s", (project_id,))
                            result = cursor_temp.fetchone()
                            conn_temp.close()

                            if result and result[0] == 'المقاولات':
                                task_type = 'مهمة مقاولات'
                            else:
                                task_type = 'مهمة مشروع'
                        else:
                            task_type = 'مهمة مشروع'  # افتراضي
                    else:
                        task_type = 'مهمة عامة'
                        project_id = None
                        phase_id = None
                else:
                    task_type = 'مهمة عامة'
                    project_id = None
                    phase_id = None

                # معلومات إضافية للمهام العامة
                role_type = None
                percentage = None
                amount = None
                amount_status = None

            else:
                # في سياق المشروع
                employee_id = self.employee_combo.currentData()
                if not employee_id:
                    QMessageBox.warning(self, "تحذير", "يجب اختيار عضو فريق العمل")
                    return

                # تحديد نوع المهمة بناءً على نوع المشروع
                task_type = 'مهمة مقاولات' if self.project_type == "المقاولات" else 'مهمة مشروع'
                project_id = self.project_id
                phase_id = self.phase_combo.currentData() if hasattr(self, 'phase_combo') else None

                # معلومات إضافية للمشاريع
                role_type = 'ربط_بمرحلة' if phase_id else 'دور_عام'
                percentage = self.percentage_spin.value() if hasattr(self, 'percentage_spin') else None
                amount = self.amount_spin.value() if hasattr(self, 'amount_spin') else None
                amount_status = self.amount_status_combo.currentText() if hasattr(self, 'amount_status_combo') else 'غير مدرج'

            if self.is_edit_mode:
                # تحديث المهمة الموجودة
                cursor.execute("""
                    UPDATE المشاريع_مهام_الفريق
                    SET معرف_الموظف = %s, نوع_المهمة = %s, معرف_القسم = %s, معرف_المرحلة = %s,
                        عنوان_المهمة = %s, وصف_المهمة = %s, نوع_دور_المهمة = %s,
                        نسبة_الموظف = %s, مبلغ_الموظف = %s, حالة_مبلغ_الموظف = %s,
                        تاريخ_البدء = %s, تاريخ_الانتهاء = %s, الحالة = %s, ملاحظات = %s
                    WHERE id = %s
                """, (employee_id, task_type, project_id, phase_id, title, description,
                      role_type, percentage, amount, amount_status,
                      start_date_str, end_date_str, status, notes, self.task_id))
            else:
                # إضافة مهمة جديدة
                cursor.execute("""
                    INSERT INTO المشاريع_مهام_الفريق
                    (معرف_الموظف, نوع_المهمة, معرف_المشروع, معرف_المرحلة, عنوان_المهمة,
                     وصف_المهمة, نوع_دور_المهمة, نسبة_الموظف,
                     مبلغ_الموظف, حالة_مبلغ_الموظف, تاريخ_البدء, تاريخ_الانتهاء, الحالة,
                     ملاحظات, المستخدم)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (employee_id, task_type, project_id, phase_id, title, description,
                      role_type, percentage, amount, amount_status,
                      start_date_str, end_date_str, status, notes, 'admin'))

            conn.commit()
            conn.close()

            success_message = "تم حفظ المهمة بنجاح" if self.context == "employee" else "تم حفظ عضو فريق العمل بنجاح"
            QMessageBox.information(self, "نجح", success_message)
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ المهمة: {str(e)}")

# حوار إضافة/تعديل سجل الحضور والانصراف
class AttendanceDialog(QDialog):

    # init
    def __init__(self, parent=None, employee_id=None, attendance_id=None):
        super().__init__(parent)
        self.employee_id = employee_id
        self.attendance_id = attendance_id
        self.is_edit_mode = attendance_id is not None

        self.setup_dialog()
        self.create_ui()

        if self.is_edit_mode:
            self.load_attendance_data()

        # تطبيق الأنماط المركزية
        apply_dialog_styles(self)

    # تحديث تسمية اليوم
    def update_day_label(self):
        try:
            date = self.date_edit.date().toPython()
            day_names = {
                0: 'الاثنين',
                1: 'الثلاثاء',
                2: 'الأربعاء',
                3: 'الخميس',
                4: 'الجمعة',
                5: 'السبت',
                6: 'الأحد'
            }
            day_name = day_names.get(date.weekday(), "غير محدد")
            self.day_label.setText(f"({day_name})")
        except Exception:
            self.day_label.setText("(غير محدد)")

    # معالج تغيير التاريخ
    def on_date_changed(self):
        self.update_day_label()
        self.check_duplicate_attendance()
        self.on_time_changed()  # إعادة حساب الحالات

    # معالج تغيير الوقت - حساب الحالات تلقائياً
    def on_time_changed(self):
        try:
            # استيراد نظام الحضور المطور
            from نظام_الحضور_المطور import AdvancedAttendanceSystem

            checkin_time = self.checkin_time_edit.time().toPython()
            checkout_time = self.checkout_time_edit.time().toPython()
            date_obj = self.date_edit.date().toPython()

            # حساب الحالات
            details = AdvancedAttendanceSystem.calculate_attendance_details(checkin_time, checkout_time, date_obj)

            if details:
                # تحديث حالة الحضور
                checkin_status = details['checkin_status'] or "غير محدد"
                if checkin_status == "مبكر":
                    duration = AdvancedAttendanceSystem.format_duration(details['checkin_early_minutes'])
                    status_text = f"مبكر ({duration})"
                    color = "#28a745"
                elif checkin_status == "متأخر":
                    duration = AdvancedAttendanceSystem.format_duration(details['checkin_late_minutes'])
                    status_text = f"متأخر ({duration})"
                    color = "#dc3545"
                else:
                    status_text = "في الموعد"
                    color = "#6c757d"

                self.checkin_status_label.setText(status_text)
                self.checkin_status_label.setObjectName("status_label")

                # تحديث حالة الانصراف
                checkout_status = details['checkout_status'] or "غير محدد"
                if checkout_status == "متأخر":
                    duration = AdvancedAttendanceSystem.format_duration(details['checkout_late_minutes'])
                    status_text = f"متأخر ({duration})"
                    color = "#28a745"  # أخضر للانصراف المتأخر
                elif checkout_status == "مبكر":
                    duration = AdvancedAttendanceSystem.format_duration(details['checkout_early_minutes'])
                    status_text = f"مبكر ({duration})"
                    color = "#dc3545"  # أحمر للانصراف المبكر
                else:
                    status_text = "في الموعد"
                    color = "#6c757d"

                self.checkout_status_label.setText(status_text)
                self.checkout_status_label.setObjectName("status_label")
            else:
                self.checkin_status_label.setText("غير محدد")
                self.checkout_status_label.setText("غير محدد")

        except Exception as e:
            print(f"خطأ في حساب حالة الحضور: {e}")
            self.checkin_status_label.setText("خطأ في الحساب")
            self.checkout_status_label.setText("خطأ في الحساب")

    # التحقق من وجود سجل حضور مضاعف
    def check_duplicate_attendance(self):
        try:
            if self.is_edit_mode:
                return  # لا نتحقق في وضع التعديل

            date = self.date_edit.date().toString("yyyy-MM-dd")

            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*) FROM الموظفين_الحضور_والانصراف
                WHERE معرف_الموظف = %s AND التاريخ = %s
            """, (self.employee_id, date))

            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()

            if count > 0:
                QMessageBox.warning(self, "تحذير",
                    f"يوجد بالفعل سجل حضور وانصراف لهذا الموظف في تاريخ {date}.\n"
                    "لا يمكن إضافة سجل مضاعف لنفس اليوم.")
                return False

            return True

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في التحقق من السجلات المضاعفة: {str(e)}")
            return True

    # إعداد الحوار
    def setup_dialog(self):
        title = "تعديل سجل الحضور" if self.is_edit_mode else "إضافة سجل حضور جديد"
        self.setWindowTitle(title)
        self.setGeometry(200, 200, 500, 450)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setModal(True)

    # إنشاء واجهة المستخدم
    def create_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # نموذج البيانات
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # التاريخ مع عرض اسم اليوم
        date_container = QWidget()
        date_layout = QHBoxLayout(date_container)
        date_layout.setContentsMargins(0, 0, 0, 0)

        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.dateChanged.connect(self.on_date_changed)

        self.day_label = QLabel()
        self.day_label.setObjectName("day_label")
        self.update_day_label()

        date_layout.addWidget(self.date_edit)
        date_layout.addWidget(self.day_label)
        date_layout.addStretch()

        form_layout.addRow("التاريخ:", date_container)

        # وقت الحضور مع نظام 12 ساعة
        self.checkin_time_edit = QTimeEdit()
        self.checkin_time_edit.setTime(QTime(8, 0))  # 8:00 AM افتراضي
        self.checkin_time_edit.setDisplayFormat("hh:mm AP")
        self.checkin_time_edit.timeChanged.connect(self.on_time_changed)
        form_layout.addRow("وقت الحضور:", self.checkin_time_edit)

        # وقت الانصراف مع نظام 12 ساعة
        self.checkout_time_edit = QTimeEdit()
        self.checkout_time_edit.setTime(QTime(17, 0))  # 5:00 PM افتراضي
        self.checkout_time_edit.setDisplayFormat("hh:mm AP")
        self.checkout_time_edit.timeChanged.connect(self.on_time_changed)
        form_layout.addRow("وقت الانصراف:", self.checkout_time_edit)

        # عرض حالة الحضور والانصراف (للقراءة فقط - يتم تحديدها تلقائياً)
        status_group = QGroupBox("حالة الحضور والانصراف (تحديد تلقائي)")
        status_layout = QVBoxLayout(status_group)

        # حالة الحضور
        checkin_frame = QFrame()
        checkin_frame.setObjectName("status_frame")
        checkin_layout = QHBoxLayout(checkin_frame)

        checkin_title = QLabel("حالة الحضور:")
        checkin_title.setObjectName("filter_label")
        self.checkin_status_label = QLabel("غير محدد")
        self.checkin_status_label.setObjectName("status_label")

        checkin_layout.addWidget(checkin_title)
        checkin_layout.addWidget(self.checkin_status_label)
        checkin_layout.addStretch()

        status_layout.addWidget(checkin_frame)

        # حالة الانصراف
        checkout_frame = QFrame()
        checkout_frame.setObjectName("status_frame")
        checkout_layout = QHBoxLayout(checkout_frame)

        checkout_title = QLabel("حالة الانصراف:")
        checkout_title.setObjectName("filter_label")
        self.checkout_status_label = QLabel("غير محدد")
        self.checkout_status_label.setObjectName("status_label")

        checkout_layout.addWidget(checkout_title)
        checkout_layout.addWidget(self.checkout_status_label)
        checkout_layout.addStretch()

        status_layout.addWidget(checkout_frame)

        layout.addWidget(status_group)

        # ملاحظات
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        form_layout.addRow("ملاحظات:", self.notes_edit)

        layout.addLayout(form_layout)

        # أزرار الحوار
        buttons_layout = QHBoxLayout()

        save_btn = QPushButton("حفظ")
        save_btn.clicked.connect(self.save_attendance)
        save_btn.setObjectName("attendance-btn")

        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setObjectName("cancel-btn")

        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)

    # تحميل بيانات الحضور للتعديل
    def load_attendance_data(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT التاريخ, وقت_الحضور, وقت_الانصراف,
                       حالة_الحضور, مدة_تأخير_الحضور, مدة_تبكير_الحضور,
                       حالة_الانصراف, مدة_تأخير_الانصراف, مدة_تبكير_الانصراف,
                       ملاحظات
                FROM الموظفين_الحضور_والانصراف
                WHERE id = %s
            """, (self.attendance_id,))

            data = cursor.fetchone()
            if data:
                if data[0]:
                    self.date_edit.setDate(QDate.fromString(str(data[0]), "yyyy-MM-dd"))
                if data[1]:
                    self.checkin_time_edit.setTime(QTime.fromString(str(data[1]), "hh:mm:ss"))
                if data[2]:
                    self.checkout_time_edit.setTime(QTime.fromString(str(data[2]), "hh:mm:ss"))

                # تحديث عرض الحالات
                self.on_time_changed()

                self.notes_edit.setPlainText(data[9] or "")

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل بيانات الحضور: {str(e)}")

    # حفظ سجل الحضور والانصراف
    def save_attendance(self):
        try:
            # التحقق من التسجيل المضاعف قبل الحفظ
            if not self.is_edit_mode and not self.check_duplicate_attendance():
                return

            # الحصول على البيانات
            date_obj = self.date_edit.date().toPython()
            checkin_time = self.checkin_time_edit.time().toPython()
            checkout_time = self.checkout_time_edit.time().toPython()
            notes = self.notes_edit.toPlainText()

            # حساب الحالات والمدد باستخدام النظام الجديد
            from نظام_الحضور_المطور import AdvancedAttendanceSystem
            details = AdvancedAttendanceSystem.calculate_attendance_details(checkin_time, checkout_time, date_obj)

            if not details:
                QMessageBox.warning(self, "تحذير", "فشل في حساب تفاصيل الحضور والانصراف")
                return

            conn = mysql.connector.connect(
                host=host, user=user, password=password,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            if self.is_edit_mode:
                # تحديث السجل الموجود
                cursor.execute("""
                    UPDATE الموظفين_الحضور_والانصراف
                    SET التاريخ = %s, وقت_الحضور = %s, وقت_الانصراف = %s,
                        حالة_الحضور = %s, مدة_تأخير_الحضور = %s, مدة_تبكير_الحضور = %s,
                        حالة_الانصراف = %s, مدة_تأخير_الانصراف = %s, مدة_تبكير_الانصراف = %s,
                        ملاحظات = %s, تاريخ_التحديث = NOW()
                    WHERE id = %s
                """, (
                    date_obj, checkin_time, checkout_time,
                    details['checkin_status'], details['checkin_late_minutes'], details['checkin_early_minutes'],
                    details['checkout_status'], details['checkout_late_minutes'], details['checkout_early_minutes'],
                    notes, self.attendance_id
                ))
            else:
                # إضافة سجل جديد
                cursor.execute("""
                    INSERT INTO الموظفين_الحضور_والانصراف
                    (معرف_الموظف, التاريخ, وقت_الحضور, وقت_الانصراف,
                     حالة_الحضور, مدة_تأخير_الحضور, مدة_تبكير_الحضور,
                     حالة_الانصراف, مدة_تأخير_الانصراف, مدة_تبكير_الانصراف, ملاحظات)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    self.employee_id, date_obj, checkin_time, checkout_time,
                    details['checkin_status'], details['checkin_late_minutes'], details['checkin_early_minutes'],
                    details['checkout_status'], details['checkout_late_minutes'], details['checkout_early_minutes'],
                    notes
                ))

            conn.commit()
            conn.close()

            QMessageBox.information(self, "نجح", "تم حفظ سجل الحضور والانصراف بنجاح")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ سجل الحضور والانصراف: {str(e)}")

# حوار إضافة/تعديل تقييم الموظف
class EvaluationDialog(QDialog):

    # init
    def __init__(self, parent=None, employee_id=None, evaluation_id=None):
        super().__init__(parent)
        self.employee_id = employee_id
        self.evaluation_id = evaluation_id
        self.is_edit_mode = evaluation_id is not None

        self.setup_dialog()
        self.create_ui()

        if self.is_edit_mode:
            self.load_evaluation_data()

        # تطبيق الأنماط المركزية
        apply_dialog_styles(self)

    # إعداد الحوار
    def setup_dialog(self):
        title = "تعديل تقييم الموظف" if self.is_edit_mode else "إضافة تقييم جديد للموظف"
        self.setWindowTitle(title)
        self.setGeometry(200, 200, 400, 300)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setModal(True)

    # إنشاء واجهة المستخدم
    def create_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # نموذج البيانات
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # حالة التسليم
        self.delivery_status_combo = QComboBox()
        self.delivery_status_combo.addItems([
            "قبل الموعد", "في الموعد", "تسليم متأخر", "لم يتم التسليم"
        ])
        form_layout.addRow("حالة التسليم:", self.delivery_status_combo)

        # النقاط
        self.points_spinbox = QSpinBox()
        self.points_spinbox.setRange(0, 100)
        self.points_spinbox.setValue(0)
        self.points_spinbox.setSuffix(" نقطة")
        form_layout.addRow("النقاط:", self.points_spinbox)

        layout.addLayout(form_layout)

        # أزرار الحوار
        buttons_layout = QHBoxLayout()

        save_btn = QPushButton("حفظ")
        save_btn.clicked.connect(self.save_evaluation)
        save_btn.setObjectName("evaluation-btn")

        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setObjectName("cancel-btn")

        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)

    # تحميل بيانات التقييم للتعديل
    def load_evaluation_data(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user_r, password=password_r,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            cursor.execute("""
                SELECT حالة_التسليم, النقاط
                FROM الموظفين_التقييم
                WHERE id = %s
            """, (self.evaluation_id,))

            data = cursor.fetchone()
            if data:
                self.delivery_status_combo.setCurrentText(data[0] or "في الموعد")
                self.points_spinbox.setValue(int(data[1] or 0))

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل بيانات التقييم: {str(e)}")

    # حفظ تقييم الموظف
    def save_evaluation(self):
        try:
            conn = mysql.connector.connect(
                host=host, user=user, password=password,
                database="project_manager_V2"
            )
            cursor = conn.cursor()

            delivery_status = self.delivery_status_combo.currentText()
            points = self.points_spinbox.value()

            if self.is_edit_mode:
                # تحديث التقييم الموجود
                cursor.execute("""
                    UPDATE الموظفين_التقييم
                    SET حالة_التسليم = %s, النقاط = %s
                    WHERE id = %s
                """, (delivery_status, points, self.evaluation_id))
            else:
                # إضافة تقييم جديد
                cursor.execute("""
                    INSERT INTO الموظفين_التقييم
                    (معرف_الموظف, حالة_التسليم, النقاط)
                    VALUES (%s, %s, %s)
                """, (self.employee_id, delivery_status, points))

            conn.commit()
            conn.close()

            QMessageBox.information(self, "نجح", "تم حفظ تقييم الموظف بنجاح")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ تقييم الموظف: {str(e)}")



# تطبيق الأنماط المركزية على الحوارات
def apply_dialog_styles(dialog):

    # تعيين أسماء الكائنات للحوارات
    for button in dialog.findChildren(QPushButton):
        button_text = button.text()
        if "حفظ" in button_text:
            button.setObjectName("save-btn")
        elif "إلغاء" in button_text:
            button.setObjectName("cancel-btn")
        elif "حذف" in button_text:
            button.setObjectName("delete-btn")

    for combo in dialog.findChildren(QComboBox):
        if not combo.objectName():
            combo.setObjectName("status-combo")

    for label in dialog.findChildren(QLabel):
        if not label.objectName():
            label.setObjectName("info-label")

    # تطبيق الأنماط
    dialog.setObjectName("styled_element")

# تطبيق الأنماط الديناميكية على التسميات بناءً على قيمها
def apply_dynamic_label_styles(label, value=None):

    if value is None:
        value = label.text()

    # تطبيق أنماط الرصيد
    if "رصيد" in label.objectName() or hasattr(label, '_is_balance'):
        try:
            # استخراج القيمة الرقمية من النص
            import re
            numbers = re.findall(r'-?\d+\.?\d*', value)
            if numbers:
                balance = float(numbers[0])
                if balance >= 0:
                    label.setObjectName("balance-positive")
                else:
                    label.setObjectName("balance-negative")
        except:
            pass

    # تطبيق أنماط الحالة
    elif "حالة" in label.objectName() or hasattr(label, '_is_status'):
        if "نشط" in value:
            label.setObjectName("status-active")
        elif any(status in value for status in ["غير نشط", "مستقيل", "تم فصله"]):
            label.setObjectName("status-inactive")

    # تطبيق أنماط الوقت المتبقي
    elif "وقت" in label.objectName() or "متبقي" in value or hasattr(label, '_is_time'):
        label.setObjectName("time-remaining")

# ==================== دالة فتح النافذة ====================

# فتح نافذة إدارة الموظفين
def open_employee_management_window(parent, employee_data):
    """
    فتح نافذة إدارة الموظف الجديدة

    Args:
        parent: النافذة الأب
        employee_data: بيانات الموظف (dict)

    Returns:
        EmployeeManagementWindow: نافذة إدارة الموظف
    """
    window = EmployeeManagementWindow(parent, employee_data)
    window.show()
    return window

