#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نافذة إدارة الديون الشاملة
تحتوي على 4 تابات: حسابات الديون، سجل الديون، مدفوعات الديون، التقارير
"""

import sys
import os
from datetime import datetime, date, timedelta
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import mysql.connector
import qtawesome as qta

# إضافة المسار الحالي
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from الإعدادات_العامة import *
from ستايل import apply_stylesheet
from قائمة_الجداول import setup_table_context_menu
from متغيرات import *
from نظام_البطاقات import ModernCard, ModernCardsContainer
from أزرار_الواجهة import table_setting
from مساعد_أزرار_الطباعة import quick_add_print_button
from ستايل_نوافذ_الإدارة import (
    apply_to_debt_management, setup_table_style, create_stat_card,
    get_status_color, format_currency, format_date, apply_management_style,apply_to_project_management
)

# نافذة إدارة الديون الشاملة
class DebtsManagementWindow(QMainWindow):
    
    # init
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("إدارة الديون")
        self.setGeometry(100, 100, 1400, 800)
        self.setLayoutDirection(Qt.RightToLeft)
        
        # إعداد النافذة الرئيسية
        self.setup_ui()
        self.create_tabs()
        #apply_to_debt_management(self)
        apply_to_project_management(self)
        self.load_all_data()

        # إضافة أزرار الطباعة لجميع التابات
        self.add_print_buttons()
        
    # إعداد واجهة المستخدم الرئيسية
    def setup_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("main_central_widget")
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # العنوان الرئيسي
        self.title_label = QLabel()
        self.title_label.setObjectName("main_title")
        self.title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title_label)
        
        # إنشاء التابات
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("debts_tab_widget")
        self.tab_widget.setLayoutDirection(Qt.RightToLeft)
        main_layout.addWidget(self.tab_widget)
        
    # تحديث العنوان الرئيسي ليعكس التاب الحالي
    def update_title(self):
        try:
            current_tab_index = self.tab_widget.currentIndex()
            
            if current_tab_index >= 0:
                tab_text = self.tab_widget.tabText(current_tab_index)
                # إزالة أيقونات HTML من نص التاب إذا كانت موجودة
                import re
                clean_tab_text = re.sub(r'<[^>]+>', '', tab_text)
                title_text = f"إدارة الديون - {clean_tab_text}"
            else:
                title_text = "إدارة الديون"
            
            self.title_label.setText(title_text)
            
        except Exception as e:
            print(f"خطأ في تحديث العنوان: {e}")
            self.title_label.setText("إدارة الديون")
        
    # إنشاء التابات الأربعة
    def create_tabs(self):
        # تاب حسابات الديون
        self.create_debt_accounts_tab()
        
        # تاب سجل الديون
        self.create_debt_records_tab()
        
        # تاب مدفوعات الديون
        self.create_debt_payments_tab()
        
        # تاب التقارير
        self.create_reports_tab()
        
        # تحديث العنوان الأولي
        self.update_title()
        
    # إنشاء تاب حسابات الديون
    def create_debt_accounts_tab(self):
        tab = QWidget()
        tab.setObjectName("debt_accounts_tab")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # الصف الأول: أزرار الإجراءات والفلاتر
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        
        # أزرار الإجراءات
        self.add_account_btn = QPushButton("إضافة حساب")
        self.add_account_btn.setObjectName("action_button")
        self.add_account_btn.clicked.connect(self.add_debt_account)
        
        self.edit_account_btn = QPushButton("تعديل حساب")
        self.edit_account_btn.setObjectName("action_button")
        self.edit_account_btn.clicked.connect(self.edit_debt_account)
        
        self.delete_account_btn = QPushButton("حذف حساب")
        self.delete_account_btn.setObjectName("action_button")
        self.delete_account_btn.clicked.connect(self.delete_debt_account)
        
        # فلاتر
        self.account_type_filter = QComboBox()
        self.account_type_filter.setObjectName("filter_combo")
        self.account_type_filter.addItems(["جميع الأنواع", "مدين", "دائن"])
        self.account_type_filter.currentTextChanged.connect(self.filter_debt_accounts)
        
        self.account_search = QLineEdit()
        self.account_search.setObjectName("search_input")
        self.account_search.setPlaceholderText("البحث في حسابات الديون...")
        self.account_search.textChanged.connect(self.search_debt_accounts)
        
        # ترتيب العناصر
        actions_layout.addWidget(self.add_account_btn)
        actions_layout.addWidget(self.edit_account_btn)
        actions_layout.addWidget(self.delete_account_btn)
        actions_layout.addStretch()
        actions_layout.addWidget(QLabel("نوع الحساب:"))
        actions_layout.addWidget(self.account_type_filter)
        actions_layout.addWidget(self.account_search)
        
        layout.addLayout(actions_layout)
        
        # الصف الثاني: البطاقات الإحصائية
        self.create_accounts_stats_cards(layout)
        
        # الجدول
        self.accounts_table = QTableWidget()
        self.accounts_table.setObjectName("data_table")
        self.accounts_table.setLayoutDirection(Qt.RightToLeft)
        self.setup_accounts_table()
        layout.addWidget(self.accounts_table)
        
        self.tab_widget.addTab(tab, qta.icon('fa5s.users', color='#3498db'), "حسابات الديون")
        
    # إنشاء تاب سجل الديون
    def create_debt_records_tab(self):
        tab = QWidget()
        tab.setObjectName("debt_records_tab")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # الصف الأول: أزرار الإجراءات والفلاتر
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        
        # أزرار الإجراءات
        self.add_debt_btn = QPushButton("إضافة دين")
        self.add_debt_btn.setObjectName("action_button")
        self.add_debt_btn.clicked.connect(self.add_debt_record)
        
        self.edit_debt_btn = QPushButton("تعديل دين")
        self.edit_debt_btn.setObjectName("action_button")
        self.edit_debt_btn.clicked.connect(self.edit_debt_record)
        
        self.delete_debt_btn = QPushButton("حذف دين")
        self.delete_debt_btn.setObjectName("action_button")
        self.delete_debt_btn.clicked.connect(self.delete_debt_record)
        
        # فلاتر
        self.debt_account_filter = QComboBox()
        self.debt_account_filter.setObjectName("filter_combo")
        self.debt_account_filter.currentTextChanged.connect(self.filter_debt_records)
        
        self.debt_search = QLineEdit()
        self.debt_search.setObjectName("search_input")
        self.debt_search.setPlaceholderText("البحث في سجل الديون...")
        self.debt_search.textChanged.connect(self.search_debt_records)
        
        # ترتيب العناصر
        actions_layout.addWidget(self.add_debt_btn)
        actions_layout.addWidget(self.edit_debt_btn)
        actions_layout.addWidget(self.delete_debt_btn)
        actions_layout.addStretch()
        actions_layout.addWidget(QLabel("الحساب:"))
        actions_layout.addWidget(self.debt_account_filter)
        actions_layout.addWidget(self.debt_search)
        
        layout.addLayout(actions_layout)
        
        # الصف الثاني: البطاقات الإحصائية
        self.create_records_stats_cards(layout)
        
        # الجدول
        self.records_table = QTableWidget()
        self.records_table.setObjectName("data_table")
        self.records_table.setLayoutDirection(Qt.RightToLeft)
        self.setup_records_table()
        layout.addWidget(self.records_table)
        
        self.tab_widget.addTab(tab, qta.icon('fa5s.file-invoice', color='#e74c3c'), "سجل الديون")
        
    # إنشاء تاب مدفوعات الديون
    def create_debt_payments_tab(self):
        tab = QWidget()
        tab.setObjectName("debt_payments_tab")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # الصف الأول: أزرار الإجراءات والفلاتر
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        
        # أزرار الإجراءات
        self.add_payment_btn = QPushButton("إضافة دفعة")
        self.add_payment_btn.setObjectName("action_button")
        self.add_payment_btn.clicked.connect(self.add_debt_payment)
        
        self.edit_payment_btn = QPushButton("تعديل دفعة")
        self.edit_payment_btn.setObjectName("action_button")
        self.edit_payment_btn.clicked.connect(self.edit_debt_payment)
        
        self.delete_payment_btn = QPushButton("حذف دفعة")
        self.delete_payment_btn.setObjectName("action_button")
        self.delete_payment_btn.clicked.connect(self.delete_debt_payment)
        
        # فلاتر
        self.payment_account_filter = QComboBox()
        self.payment_account_filter.setObjectName("filter_combo")
        self.payment_account_filter.currentTextChanged.connect(self.filter_debt_payments)
        
        self.payment_search = QLineEdit()
        self.payment_search.setObjectName("search_input")
        self.payment_search.setPlaceholderText("البحث في مدفوعات الديون...")
        self.payment_search.textChanged.connect(self.search_debt_payments)
        
        # ترتيب العناصر
        actions_layout.addWidget(self.add_payment_btn)
        actions_layout.addWidget(self.edit_payment_btn)
        actions_layout.addWidget(self.delete_payment_btn)
        actions_layout.addStretch()
        actions_layout.addWidget(QLabel("الحساب:"))
        actions_layout.addWidget(self.payment_account_filter)
        actions_layout.addWidget(self.payment_search)
        
        layout.addLayout(actions_layout)
        
        # الصف الثاني: البطاقات الإحصائية
        self.create_payments_stats_cards(layout)
        
        # الجدول
        self.payments_table = QTableWidget()
        self.payments_table.setObjectName("data_table")
        self.payments_table.setLayoutDirection(Qt.RightToLeft)
        self.setup_payments_table()
        layout.addWidget(self.payments_table)
        
        self.tab_widget.addTab(tab, qta.icon('fa5s.money-bill-wave', color='#27ae60'), "مدفوعات الديون")
        
    # إنشاء تاب التقارير
    def create_reports_tab(self):
        tab = QWidget()
        tab.setObjectName("reports_tab")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # عنوان التقارير
        title = QLabel("تقارير الديون")
        title.setObjectName("reports_title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # مجموعة أزرار التقارير
        reports_group = QGroupBox("أنواع التقارير")
        reports_group.setObjectName("reports_group")
        reports_layout = QGridLayout(reports_group)
        reports_layout.setSpacing(15)
        
        # تقارير مختلفة
        report_buttons = [
            ("تقرير حسابات الديون", "fa5s.file-alt", "#3498db", self.generate_accounts_report),
            ("تقرير سجل الديون", "fa5s.list", "#e74c3c", self.generate_records_report),
            ("تقرير المدفوعات", "fa5s.money-check", "#27ae60", self.generate_payments_report),
            ("تقرير الديون المستحقة", "fa5s.exclamation-triangle", "#f39c12", self.generate_overdue_report),
            ("تقرير إجمالي الديون", "fa5s.chart-pie", "#9b59b6", self.generate_summary_report),
            ("تقرير مخصص", "fa5s.cogs", "#34495e", self.generate_custom_report)
        ]
        
        for i, (text, icon, color, callback) in enumerate(report_buttons):
            btn = QPushButton(text)
            btn.setObjectName("report_button")
            btn.setIcon(qta.icon(icon, color=color))
            btn.setMinimumHeight(60)
            btn.clicked.connect(callback)
            reports_layout.addWidget(btn, i // 2, i % 2)
        
        layout.addWidget(reports_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, qta.icon('fa5s.chart-bar', color='#9b59b6'), "التقارير")

    # إنشاء بطاقات إحصائيات حسابات الديون
    def create_accounts_stats_cards(self, layout):
        stats_frame = QFrame()
        stats_frame.setObjectName("accounts_stats_container")
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(15)

        # بطاقة إجمالي الديون علينا
        self.total_debts_on_us_card = create_stat_card(
            "إجمالي الديون علينا", "0.00", "#e74c3c"
        )
        stats_layout.addWidget(self.total_debts_on_us_card)

        # بطاقة إجمالي الديون لنا
        self.total_debts_for_us_card = create_stat_card(
            "إجمالي الديون لنا", "0.00", "#27ae60"
        )
        stats_layout.addWidget(self.total_debts_for_us_card)

        # بطاقة عدد الحسابات
        self.total_accounts_card = create_stat_card(
            "عدد الحسابات", "0", "#3498db"
        )
        stats_layout.addWidget(self.total_accounts_card)

        # بطاقة الحسابات المستحقة
        self.overdue_accounts_card = create_stat_card(
            "الحسابات المستحقة", "0", "#f39c12"
        )
        stats_layout.addWidget(self.overdue_accounts_card)

        layout.addWidget(stats_frame)

    # إنشاء بطاقات إحصائيات سجل الديون
    def create_records_stats_cards(self, layout):
        stats_frame = QFrame()
        stats_frame.setObjectName("records_stats_container")
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(15)

        # بطاقة إجمالي قيمة الديون
        self.total_debt_value_card = create_stat_card(
            "إجمالي قيمة الديون", "0.00", "#9b59b6"
        )
        stats_layout.addWidget(self.total_debt_value_card)

        # بطاقة عدد سجلات الديون
        self.total_records_card = create_stat_card(
            "عدد سجلات الديون", "0", "#34495e"
        )
        stats_layout.addWidget(self.total_records_card)

        # بطاقة الديون المسددة
        self.paid_debts_card = create_stat_card(
            "الديون المسددة", "0", "#27ae60"
        )
        stats_layout.addWidget(self.paid_debts_card)

        # بطاقة الديون المعلقة
        self.pending_debts_card = create_stat_card(
            "الديون المعلقة", "0", "#e74c3c"
        )
        stats_layout.addWidget(self.pending_debts_card)

        layout.addWidget(stats_frame)

    # إنشاء بطاقات إحصائيات مدفوعات الديون
    def create_payments_stats_cards(self, layout):
        stats_frame = QFrame()
        stats_frame.setObjectName("payments_stats_container")
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(15)

        # بطاقة إجمالي المدفوعات
        self.total_payments_card = create_stat_card(
            "إجمالي المدفوعات", "0.00", "#27ae60"
        )
        stats_layout.addWidget(self.total_payments_card)

        # بطاقة عدد المدفوعات
        self.payments_count_card = create_stat_card(
            "عدد المدفوعات", "0", "#3498db"
        )
        stats_layout.addWidget(self.payments_count_card)

        # بطاقة مدفوعات هذا الشهر
        self.monthly_payments_card = create_stat_card(
            "مدفوعات هذا الشهر", "0.00", "#f39c12"
        )
        stats_layout.addWidget(self.monthly_payments_card)

        # بطاقة متوسط الدفعة
        self.avg_payment_card = create_stat_card(
            "متوسط الدفعة", "0.00", "#9b59b6"
        )
        stats_layout.addWidget(self.avg_payment_card)

        layout.addWidget(stats_frame)



    # إعداد جدول حسابات الديون
    def setup_accounts_table(self):
        headers = ["المعرف", "اسم الحساب", "نوع الحساب", "رقم الهاتف", "العنوان",
                  "إجمالي الدين", "المدفوع", "الباقي", "تاريخ الإضافة", "ملاحظات"]

        self.accounts_table.setColumnCount(len(headers))
        self.accounts_table.setHorizontalHeaderLabels(headers)
        self.accounts_table.horizontalHeader().setStretchLastSection(True)
        self.accounts_table.setAlternatingRowColors(True)
        self.accounts_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # إعداد قائمة السياق
        setup_table_context_menu(self.accounts_table, self, "حسابات الديون", is_main_table=True)

        # ربط النقر المزدوج بالتعديل
        self.accounts_table.itemDoubleClicked.connect(self.edit_debt_account)

    # إعداد جدول سجل الديون
    def setup_records_table(self):
        headers = ["المعرف", "الحساب", "وصف الدين", "المبلغ", "تاريخ الدين",
                  "تاريخ الاستحقاق", "حالة_الدين", "ملاحظات"]

        self.records_table.setColumnCount(len(headers))
        self.records_table.setHorizontalHeaderLabels(headers)
        self.records_table.horizontalHeader().setStretchLastSection(True)
        self.records_table.setAlternatingRowColors(True)
        self.records_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # إعداد قائمة السياق
        setup_table_context_menu(self.records_table, self, "سجل الديون", is_main_table=True)

        # ربط النقر المزدوج بالتعديل
        self.records_table.itemDoubleClicked.connect(self.edit_debt_record)

    # إعداد جدول مدفوعات الديون
    def setup_payments_table(self):
        headers = ["المعرف", "الحساب", "وصف الدفعة", "المبلغ", "تاريخ الدفعة",
                  "طريقة الدفع", "المستلم", "ملاحظات"]

        self.payments_table.setColumnCount(len(headers))
        self.payments_table.setHorizontalHeaderLabels(headers)
        self.payments_table.horizontalHeader().setStretchLastSection(True)
        self.payments_table.setAlternatingRowColors(True)
        self.payments_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # إعداد قائمة السياق
        setup_table_context_menu(self.payments_table, self, "مدفوعات الديون", is_main_table=True)

        # ربط النقر المزدوج بالتعديل
        self.payments_table.itemDoubleClicked.connect(self.edit_debt_payment)

    # إنشاء اتصال بقاعدة البيانات
    def get_db_connection(self):
        try:
            from DB import host, user_r, password_r
            conn = mysql.connector.connect(
                host=host,
                user=user_r,
                password=password_r,
                database="project_manager_V2"
            )
            return conn
        except Exception as e:
            print(f"خطأ في الاتصال بقاعدة البيانات: {e}")
            return None

    # تحميل جميع البيانات
    def load_all_data(self):
        self.load_filter_data()
        self.load_debt_accounts()
        self.load_debt_records()
        self.load_debt_payments()
        self.update_all_statistics()

    # تحميل بيانات الفلاتر
    def load_filter_data(self):
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()

            # تحميل حسابات الديون للفلاتر
            cursor.execute("SELECT اسم_الحساب FROM الحسابات_الديون ORDER BY اسم_الحساب")
            accounts = cursor.fetchall()

            # تحديث فلاتر الحسابات
            self.debt_account_filter.clear()
            self.debt_account_filter.addItem("جميع الحسابات")
            for account in accounts:
                self.debt_account_filter.addItem(account[0])

            self.payment_account_filter.clear()
            self.payment_account_filter.addItem("جميع الحسابات")
            for account in accounts:
                self.payment_account_filter.addItem(account[0])

        except Exception as e:
            print(f"خطأ في تحميل بيانات الفلاتر: {e}")
        finally:
            if conn:
                conn.close()

    # تحميل بيانات حسابات الديون
    def load_debt_accounts(self):
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, اسم_الحساب, نوع_الحساب, رقم_الهاتف, العنوان,
                       مبلغ_الدين, المدفوع, (مبلغ_الدين - المدفوع) as الباقي,
                       `تاريخ _الإنشاء`, ملاحظات
                FROM الحسابات_الديون
                ORDER BY `تاريخ _الإنشاء` DESC
            """)

            data = cursor.fetchall()
            self.populate_accounts_table(data)

        except Exception as e:
            print(f"خطأ في تحميل حسابات الديون: {e}")
            QMessageBox.warning(self, "خطأ", f"فشل في تحميل حسابات الديون: {str(e)}")
        finally:
            if conn:
                conn.close()

    # ملء جدول حسابات الديون
    def populate_accounts_table(self, data):
        self.accounts_table.setRowCount(len(data))

        for row, record in enumerate(data):
            for col, value in enumerate(record):
                item = QTableWidgetItem(str(value) if value is not None else "")

                # تلوين الخلايا حسب نوع الحساب
                if col == 2:  # عمود نوع الحساب
                    if value == "مدين":
                        item.setForeground(QBrush(QColor(231, 76, 60)))  # أحمر
                    elif value == "دائن":
                        item.setForeground(QBrush(QColor(46, 125, 50)))  # أخضر

                # تلوين المبالغ
                elif col in [5, 6, 7]:  # أعمدة المبالغ
                    if col == 7 and float(value or 0) > 0:  # الباقي
                        item.setForeground(QBrush(QColor(231, 76, 60)))  # أحمر للمبالغ المستحقة
                    elif col == 6:  # المدفوع
                        item.setForeground(QBrush(QColor(46, 125, 50)))  # أخضر للمدفوع

                self.accounts_table.setItem(row, col, item)

    # تحميل بيانات سجل الديون
    def load_debt_records(self):
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sdr.id, hd.اسم_الحساب, sdr.`وصف _الدين`, sdr.المبلغ,
                       sdr.`تاريخ _الدين`, sdr.تاريخ_السداد, 'معلق' as حالة_الدين, sdr.ملاحظات
                FROM الحسابات_سجل_الديون sdr
                JOIN الحسابات_الديون hd ON sdr.معرف_الحساب = hd.id
                ORDER BY sdr.`تاريخ _الدين` DESC
            """)

            data = cursor.fetchall()
            self.populate_records_table(data)

        except Exception as e:
            print(f"خطأ في تحميل سجل الديون: {e}")
            QMessageBox.warning(self, "خطأ", f"فشل في تحميل سجل الديون: {str(e)}")
        finally:
            if conn:
                conn.close()

    # ملء جدول سجل الديون
    def populate_records_table(self, data):
        self.records_table.setRowCount(len(data))

        for row, record in enumerate(data):
            for col, value in enumerate(record):
                item = QTableWidgetItem(str(value) if value is not None else "")

                # تلوين حالة_الدين
                if col == 6:  # عمود حالة_الدين
                    if value == "مسدد":
                        item.setForeground(QBrush(QColor(46, 125, 50)))  # أخضر
                    elif value == "معلق":
                        item.setForeground(QBrush(QColor(231, 76, 60)))  # أحمر
                    elif value == "مستحق":
                        item.setForeground(QBrush(QColor(243, 156, 18)))  # برتقالي

                self.records_table.setItem(row, col, item)

    # تحميل بيانات مدفوعات الديون
    def load_debt_payments(self):
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sds.id, hd.اسم_الحساب, sds.`وصف_المدفوع`, sds.المبلغ,
                       sds.`تاريخ_السداد`, sds.طريقة_الدفع, 'غير محدد' as المستلم, sds.ملاحظات
                FROM الحسابات_سجل_سداد_الديون sds
                JOIN الحسابات_الديون hd ON sds.معرف_الحساب = hd.id
                ORDER BY sds.`تاريخ_السداد` DESC
            """)

            data = cursor.fetchall()
            self.populate_payments_table(data)

        except Exception as e:
            print(f"خطأ في تحميل مدفوعات الديون: {e}")
            QMessageBox.warning(self, "خطأ", f"فشل في تحميل مدفوعات الديون: {str(e)}")
        finally:
            if conn:
                conn.close()

    # ملء جدول مدفوعات الديون
    def populate_payments_table(self, data):
        self.payments_table.setRowCount(len(data))

        for row, record in enumerate(data):
            for col, value in enumerate(record):
                item = QTableWidgetItem(str(value) if value is not None else "")

                # تلوين المبالغ
                if col == 3:  # عمود المبلغ
                    item.setForeground(QBrush(QColor(46, 125, 50)))  # أخضر للمدفوعات

                self.payments_table.setItem(row, col, item)

    # تحديث جميع الإحصائيات
    def update_all_statistics(self):
        self.update_accounts_statistics()
        self.update_records_statistics()
        self.update_payments_statistics()

    # تحديث إحصائيات حسابات الديون
    def update_accounts_statistics(self):
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()

            # إجمالي الديون علينا
            cursor.execute("""
                SELECT COALESCE(SUM(مبلغ_الدين - المدفوع), 0)
                FROM الحسابات_الديون
                WHERE نوع_الحساب = 'مدين'
            """)
            debts_on_us = cursor.fetchone()[0]

            # إجمالي الديون لنا
            cursor.execute("""
                SELECT COALESCE(SUM(مبلغ_الدين - المدفوع), 0)
                FROM الحسابات_الديون
                WHERE نوع_الحساب = 'دائن'
            """)
            debts_for_us = cursor.fetchone()[0]

            # عدد الحسابات
            cursor.execute("SELECT COUNT(*) FROM الحسابات_الديون")
            total_accounts = cursor.fetchone()[0]

            # الحسابات المستحقة
            cursor.execute("""
                SELECT COUNT(*) FROM الحسابات_الديون
                WHERE (مبلغ_الدين - المدفوع) > 0
            """)
            overdue_accounts = cursor.fetchone()[0]

            # تحديث البطاقات
            self.update_stat_card_value(self.total_debts_on_us_card, f"{debts_on_us:,.2f}")
            self.update_stat_card_value(self.total_debts_for_us_card, f"{debts_for_us:,.2f}")
            self.update_stat_card_value(self.total_accounts_card, str(total_accounts))
            self.update_stat_card_value(self.overdue_accounts_card, str(overdue_accounts))

        except Exception as e:
            print(f"خطأ في تحديث إحصائيات الحسابات: {e}")
        finally:
            if conn:
                conn.close()

    # تحديث إحصائيات سجل الديون
    def update_records_statistics(self):
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()

            # إجمالي قيمة الديون
            cursor.execute("SELECT COALESCE(SUM(المبلغ), 0) FROM الحسابات_سجل_الديون")
            total_debt_value = cursor.fetchone()[0]

            # عدد سجلات الديون
            cursor.execute("SELECT COUNT(*) FROM الحسابات_سجل_الديون")
            total_records = cursor.fetchone()[0]

            # الديون المسددة
            cursor.execute("""
                SELECT COUNT(*) FROM الحسابات_سجل_الديون
                WHERE حالة_الدين = 'مسدد'
            """)
            paid_debts = cursor.fetchone()[0]

            # الديون المعلقة
            cursor.execute("""
                SELECT COUNT(*) FROM الحسابات_سجل_الديون
                WHERE حالة_الدين = 'معلق'
            """)
            pending_debts = cursor.fetchone()[0]

            # تحديث البطاقات
            self.update_stat_card_value(self.total_debt_value_card, f"{total_debt_value:,.2f}")
            self.update_stat_card_value(self.total_records_card, str(total_records))
            self.update_stat_card_value(self.paid_debts_card, str(paid_debts))
            self.update_stat_card_value(self.pending_debts_card, str(pending_debts))

        except Exception as e:
            print(f"خطأ في تحديث إحصائيات السجلات: {e}")
        finally:
            if conn:
                conn.close()

    # تحديث إحصائيات مدفوعات الديون
    def update_payments_statistics(self):
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()

            # إجمالي المدفوعات
            cursor.execute("SELECT COALESCE(SUM(المبلغ), 0) FROM الحسابات_سجل_سداد_الديون")
            total_payments = cursor.fetchone()[0]

            # عدد المدفوعات
            cursor.execute("SELECT COUNT(*) FROM الحسابات_سجل_سداد_الديون")
            payments_count = cursor.fetchone()[0]

            # مدفوعات هذا الشهر
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0) FROM الحسابات_سجل_سداد_الديون
                WHERE MONTH(تاريخ_السداد) = MONTH(CURDATE())
                AND YEAR(تاريخ_السداد) = YEAR(CURDATE())
            """)
            monthly_payments = cursor.fetchone()[0]

            # متوسط الدفعة
            avg_payment = total_payments / payments_count if payments_count > 0 else 0

            # تحديث البطاقات
            self.update_stat_card_value(self.total_payments_card, f"{total_payments:,.2f}")
            self.update_stat_card_value(self.payments_count_card, str(payments_count))
            self.update_stat_card_value(self.monthly_payments_card, f"{monthly_payments:,.2f}")
            self.update_stat_card_value(self.avg_payment_card, f"{avg_payment:,.2f}")

        except Exception as e:
            print(f"خطأ في تحديث إحصائيات المدفوعات: {e}")
        finally:
            if conn:
                conn.close()

    # تحديث قيمة بطاقة إحصائية
    def update_stat_card_value(self, card, value):
        value_label = card.findChild(QLabel, "stat_value")
        if value_label:
            value_label.setText(value)

    # دوال الإضافة والتعديل والحذف
    # إضافة حساب دين جديد
    def add_debt_account(self):
        dialog = DebtAccountDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if self.save_debt_account(data):
                self.load_debt_accounts()
                self.load_filter_data()
                self.update_accounts_statistics()
                QMessageBox.information(self, "نجح", "تم إضافة حساب الدين بنجاح")

    # تعديل حساب دين
    def edit_debt_account(self):
        current_row = self.accounts_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "الرجاء اختيار حساب للتعديل")
            return

        account_id = self.accounts_table.item(current_row, 0).text()
        account_data = self.get_debt_account_data(account_id)

        if account_data:
            dialog = DebtAccountDialog(self, account_data)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                if self.update_debt_account(account_id, data):
                    self.load_debt_accounts()
                    self.update_accounts_statistics()
                    QMessageBox.information(self, "نجح", "تم تعديل حساب الدين بنجاح")

    # حذف حساب دين
    def delete_debt_account(self):
        current_row = self.accounts_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "الرجاء اختيار حساب للحذف")
            return

        account_id = self.accounts_table.item(current_row, 0).text()
        account_name = self.accounts_table.item(current_row, 1).text()

        reply = QMessageBox.question(
            self, "تأكيد الحذف",
            f"هل أنت متأكد من حذف حساب '{account_name}'؟\nسيتم حذف جميع السجلات والمدفوعات المرتبطة به.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.delete_debt_account_from_db(account_id):
                self.load_debt_accounts()
                self.load_debt_records()
                self.load_debt_payments()
                self.load_filter_data()
                self.update_all_statistics()
                QMessageBox.information(self, "نجح", "تم حذف حساب الدين بنجاح")

    # إضافة سجل دين جديد
    def add_debt_record(self):
        dialog = DebtRecordDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if self.save_debt_record(data):
                # تحديث إجمالي الدين في جدول الحسابات
                self.update_account_total_debt(data['معرف_الحساب'])
                self.load_debt_records()
                self.load_debt_accounts()
                self.update_all_statistics()
                QMessageBox.information(self, "نجح", "تم إضافة سجل الدين بنجاح")

    # تعديل سجل دين
    def edit_debt_record(self):
        current_row = self.records_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "الرجاء اختيار سجل للتعديل")
            return

        record_id = self.records_table.item(current_row, 0).text()
        record_data = self.get_debt_record_data(record_id)

        if record_data:
            old_account_id = record_data['معرف_الحساب']
            old_amount = record_data['المبلغ']

            dialog = DebtRecordDialog(self, record_data)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                if self.update_debt_record(record_id, data):
                    # تحديث إجمالي الدين في الحسابات المتأثرة
                    self.update_account_total_debt(old_account_id)
                    if data['معرف_الحساب'] != old_account_id:
                        self.update_account_total_debt(data['معرف_الحساب'])

                    self.load_debt_records()
                    self.load_debt_accounts()
                    self.update_all_statistics()
                    QMessageBox.information(self, "نجح", "تم تعديل سجل الدين بنجاح")

    # حذف سجل دين
    def delete_debt_record(self):
        current_row = self.records_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "الرجاء اختيار سجل للحذف")
            return

        record_id = self.records_table.item(current_row, 0).text()
        debt_description = self.records_table.item(current_row, 2).text()

        reply = QMessageBox.question(
            self, "تأكيد الحذف",
            f"هل أنت متأكد من حذف سجل الدين '{debt_description}'؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            record_data = self.get_debt_record_data(record_id)
            if record_data and self.delete_debt_record_from_db(record_id):
                # تحديث إجمالي الدين في جدول الحسابات
                self.update_account_total_debt(record_data['معرف_الحساب'])
                self.load_debt_records()
                self.load_debt_accounts()
                self.update_all_statistics()
                QMessageBox.information(self, "نجح", "تم حذف سجل الدين بنجاح")

    # إضافة دفعة دين جديدة
    def add_debt_payment(self):
        dialog = DebtPaymentDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if self.save_debt_payment(data):
                # تحديث المدفوع في جدول الحسابات
                self.update_account_paid_amount(data['معرف_الحساب'])
                self.load_debt_payments()
                self.load_debt_accounts()
                self.update_all_statistics()
                QMessageBox.information(self, "نجح", "تم إضافة دفعة الدين بنجاح")

    # تعديل دفعة دين
    def edit_debt_payment(self):
        current_row = self.payments_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "الرجاء اختيار دفعة للتعديل")
            return

        payment_id = self.payments_table.item(current_row, 0).text()
        payment_data = self.get_debt_payment_data(payment_id)

        if payment_data:
            old_account_id = payment_data['معرف_الحساب']

            dialog = DebtPaymentDialog(self, payment_data)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                if self.update_debt_payment(payment_id, data):
                    # تحديث المدفوع في الحسابات المتأثرة
                    self.update_account_paid_amount(old_account_id)
                    if data['معرف_الحساب'] != old_account_id:
                        self.update_account_paid_amount(data['معرف_الحساب'])

                    self.load_debt_payments()
                    self.load_debt_accounts()
                    self.update_all_statistics()
                    QMessageBox.information(self, "نجح", "تم تعديل دفعة الدين بنجاح")

    # حذف دفعة دين
    def delete_debt_payment(self):
        current_row = self.payments_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تحذير", "الرجاء اختيار دفعة للحذف")
            return

        payment_id = self.payments_table.item(current_row, 0).text()
        payment_description = self.payments_table.item(current_row, 2).text()

        reply = QMessageBox.question(
            self, "تأكيد الحذف",
            f"هل أنت متأكد من حذف دفعة '{payment_description}'؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            payment_data = self.get_debt_payment_data(payment_id)
            if payment_data and self.delete_debt_payment_from_db(payment_id):
                # تحديث المدفوع في جدول الحسابات
                self.update_account_paid_amount(payment_data['معرف_الحساب'])
                self.load_debt_payments()
                self.load_debt_accounts()
                self.update_all_statistics()
                QMessageBox.information(self, "نجح", "تم حذف دفعة الدين بنجاح")

    # دوال قاعدة البيانات
    # حفظ حساب دين جديد
    def save_debt_account(self, data):
        conn = self.get_db_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            # نوع الحساب كما هو
            account_type = data['نوع_الحساب']

            cursor.execute("""
                INSERT INTO الحسابات_الديون
                (اسم_الحساب, نوع_الحساب, رقم_الهاتف, العنوان, مبلغ_الدين, المدفوع, `تاريخ _الإنشاء`, ملاحظات)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['اسم_الحساب'], account_type, data['رقم_الهاتف'],
                data['العنوان'], 0.0, 0.0, datetime.now().date(), data['ملاحظات']
            ))
            conn.commit()
            return True

        except Exception as e:
            print(f"خطأ في حفظ حساب الدين: {e}")
            QMessageBox.warning(self, "خطأ", f"فشل في حفظ حساب الدين: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()

    # الحصول على بيانات حساب دين
    def get_debt_account_data(self, account_id):
        conn = self.get_db_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT اسم_الحساب, نوع_الحساب, رقم_الهاتف, العنوان, ملاحظات
                FROM الحسابات_الديون WHERE id = %s
            """, (account_id,))

            result = cursor.fetchone()
            if result:
                return {
                    'اسم_الحساب': result[0],
                    'نوع_الحساب': result[1],
                    'رقم_الهاتف': result[2],
                    'العنوان': result[3],
                    'ملاحظات': result[4]
                }
            return None

        except Exception as e:
            print(f"خطأ في الحصول على بيانات الحساب: {e}")
            return None
        finally:
            if conn:
                conn.close()

    # تحديث حساب دين
    def update_debt_account(self, account_id, data):
        conn = self.get_db_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            # نوع الحساب كما هو
            account_type = data['نوع_الحساب']

            cursor.execute("""
                UPDATE الحسابات_الديون
                SET اسم_الحساب = %s, نوع_الحساب = %s, رقم_الهاتف = %s,
                    العنوان = %s, ملاحظات = %s
                WHERE id = %s
            """, (
                data['اسم_الحساب'], account_type, data['رقم_الهاتف'],
                data['العنوان'], data['ملاحظات'], account_id
            ))
            conn.commit()
            return True

        except Exception as e:
            print(f"خطأ في تحديث حساب الدين: {e}")
            QMessageBox.warning(self, "خطأ", f"فشل في تحديث حساب الدين: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()

    # حذف حساب دين من قاعدة البيانات
    def delete_debt_account_from_db(self, account_id):
        conn = self.get_db_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()

            # حذف السجلات والمدفوعات المرتبطة أولاً
            cursor.execute("DELETE FROM الحسابات_سجل_سداد_الديون WHERE معرف_الحساب = %s", (account_id,))
            cursor.execute("DELETE FROM الحسابات_سجل_الديون WHERE معرف_الحساب = %s", (account_id,))
            cursor.execute("DELETE FROM الحسابات_الديون WHERE id = %s", (account_id,))

            conn.commit()
            return True

        except Exception as e:
            print(f"خطأ في حذف حساب الدين: {e}")
            QMessageBox.warning(self, "خطأ", f"فشل في حذف حساب الدين: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()

    # تحديث إجمالي الدين في حساب معين
    def update_account_total_debt(self, account_id):
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE الحسابات_الديون
                SET مبلغ_الدين = (
                    SELECT COALESCE(SUM(المبلغ), 0)
                    FROM الحسابات_سجل_الديون
                    WHERE معرف_الحساب = %s
                )
                WHERE id = %s
            """, (account_id, account_id))
            conn.commit()

        except Exception as e:
            print(f"خطأ في تحديث إجمالي الدين: {e}")
        finally:
            if conn:
                conn.close()

    # تحديث المبلغ المدفوع في حساب معين
    def update_account_paid_amount(self, account_id):
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE الحسابات_الديون
                SET المدفوع = (
                    SELECT COALESCE(SUM(المبلغ), 0)
                    FROM الحسابات_سجل_سداد_الديون
                    WHERE معرف_الحساب = %s
                )
                WHERE id = %s
            """, (account_id, account_id))
            conn.commit()

        except Exception as e:
            print(f"خطأ في تحديث المبلغ المدفوع: {e}")
        finally:
            if conn:
                conn.close()

    # دوال البحث والفلترة
    # فلترة حسابات الديون
    def filter_debt_accounts(self):
        filter_text = self.account_type_filter.currentText()

        for row in range(self.accounts_table.rowCount()):
            show_row = True

            if filter_text != "جميع الأنواع":
                account_type = self.accounts_table.item(row, 2).text()
                if account_type != filter_text:
                    show_row = False

            self.accounts_table.setRowHidden(row, not show_row)

    # البحث في حسابات الديون
    def search_debt_accounts(self):
        search_text = self.account_search.text().lower()

        for row in range(self.accounts_table.rowCount()):
            show_row = False

            for col in range(self.accounts_table.columnCount()):
                item = self.accounts_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break

            self.accounts_table.setRowHidden(row, not show_row)

    # فلترة سجل الديون
    def filter_debt_records(self):
        filter_text = self.debt_account_filter.currentText()

        for row in range(self.records_table.rowCount()):
            show_row = True

            if filter_text != "جميع الحسابات":
                account_name = self.records_table.item(row, 1).text()
                if account_name != filter_text:
                    show_row = False

            self.records_table.setRowHidden(row, not show_row)

    # البحث في سجل الديون
    def search_debt_records(self):
        search_text = self.debt_search.text().lower()

        for row in range(self.records_table.rowCount()):
            show_row = False

            for col in range(self.records_table.columnCount()):
                item = self.records_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break

            self.records_table.setRowHidden(row, not show_row)

    # فلترة مدفوعات الديون
    def filter_debt_payments(self):
        filter_text = self.payment_account_filter.currentText()

        for row in range(self.payments_table.rowCount()):
            show_row = True

            if filter_text != "جميع الحسابات":
                account_name = self.payments_table.item(row, 1).text()
                if account_name != filter_text:
                    show_row = False

            self.payments_table.setRowHidden(row, not show_row)

    # البحث في مدفوعات الديون
    def search_debt_payments(self):
        search_text = self.payment_search.text().lower()

        for row in range(self.payments_table.rowCount()):
            show_row = False

            for col in range(self.payments_table.columnCount()):
                item = self.payments_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break

            self.payments_table.setRowHidden(row, not show_row)

    # دوال التقارير
    # إنتاج تقرير حسابات الديون
    def generate_accounts_report(self):
        QMessageBox.information(self, "تقرير حسابات الديون", "سيتم إنتاج تقرير حسابات الديون قريباً")

    # إنتاج تقرير سجل الديون
    def generate_records_report(self):
        QMessageBox.information(self, "تقرير سجل الديون", "سيتم إنتاج تقرير سجل الديون قريباً")

    # إنتاج تقرير المدفوعات
    def generate_payments_report(self):
        QMessageBox.information(self, "تقرير المدفوعات", "سيتم إنتاج تقرير المدفوعات قريباً")

    # إنتاج تقرير الديون المستحقة
    def generate_overdue_report(self):
        QMessageBox.information(self, "تقرير الديون المستحقة", "سيتم إنتاج تقرير الديون المستحقة قريباً")

    # إنتاج تقرير إجمالي الديون
    def generate_summary_report(self):
        QMessageBox.information(self, "تقرير إجمالي الديون", "سيتم إنتاج تقرير إجمالي الديون قريباً")

    # إنتاج تقرير مخصص
    def generate_custom_report(self):
        QMessageBox.information(self, "تقرير مخصص", "سيتم إنتاج التقرير المخصص قريباً")

    # ربط الإشارات
    def connect_signals(self):
        # ربط تغيير التاب بتحديث البيانات
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

    # معالجة تغيير التاب
    def on_tab_changed(self, index):
        # تحديث العنوان الرئيسي
        self.update_title()
        
        if index == 0:  # تاب حسابات الديون
            self.load_debt_accounts()
            self.update_accounts_statistics()
        elif index == 1:  # تاب سجل الديون
            self.load_debt_records()
            self.update_records_statistics()
        elif index == 2:  # تاب مدفوعات الديون
            self.load_debt_payments()
            self.update_payments_statistics()



    # إضافة أزرار الطباعة لجميع التابات
    def add_print_buttons(self):
        try:
            # إضافة أزرار الطباعة تلقائياً لجميع التابات
            quick_add_print_button(self, self.tab_widget)

        except Exception as e:
            print(f"خطأ في إضافة أزرار الطباعة: {e}")


# حوارات الإضافة والتعديل
# حوار إضافة/تعديل حساب دين
class DebtAccountDialog(QDialog):

    # init
    def __init__(self, parent=None, account_data=None):
        super().__init__(parent)
        self.account_data = account_data
        self.setWindowTitle("إضافة حساب دين" if not account_data else "تعديل حساب دين")
        self.setModal(True)
        self.setFixedSize(500, 400)
        self.setLayoutDirection(Qt.RightToLeft)

        self.setup_ui()
        if account_data:
            self.load_data()

    # إعداد واجهة المستخدم
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # اسم الحساب
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("اسم الحساب:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("أدخل اسم الحساب...")
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # نوع الحساب
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("نوع الحساب:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["مدين", "دائن"])
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)

        # رقم الهاتف
        phone_layout = QHBoxLayout()
        phone_layout.addWidget(QLabel("رقم الهاتف:"))
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("أدخل رقم الهاتف...")
        phone_layout.addWidget(self.phone_input)
        layout.addLayout(phone_layout)

        # العنوان
        address_layout = QVBoxLayout()
        address_layout.addWidget(QLabel("العنوان:"))
        self.address_input = QTextEdit()
        self.address_input.setPlaceholderText("أدخل العنوان...")
        self.address_input.setMaximumHeight(80)
        address_layout.addWidget(self.address_input)
        layout.addLayout(address_layout)

        # الملاحظات
        notes_layout = QVBoxLayout()
        notes_layout.addWidget(QLabel("ملاحظات:"))
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("أدخل ملاحظات...")
        self.notes_input.setMaximumHeight(80)
        notes_layout.addWidget(self.notes_input)
        layout.addLayout(notes_layout)

        # أزرار الحفظ والإلغاء
        buttons_layout = QHBoxLayout()
        self.save_btn = QPushButton("حفظ")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.clicked.connect(self.reject)

        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)
        layout.addLayout(buttons_layout)

    # تحميل البيانات للتعديل
    def load_data(self):
        if self.account_data:
            self.name_input.setText(self.account_data.get('اسم_الحساب', ''))
            self.type_combo.setCurrentText(self.account_data.get('نوع_الحساب', 'دين علينا'))
            self.phone_input.setText(self.account_data.get('رقم_الهاتف', ''))
            self.address_input.setPlainText(self.account_data.get('العنوان', ''))
            self.notes_input.setPlainText(self.account_data.get('ملاحظات', ''))

    # الحصول على البيانات المدخلة
    def get_data(self):
        return {
            'اسم_الحساب': self.name_input.text().strip(),
            'نوع_الحساب': self.type_combo.currentText(),
            'رقم_الهاتف': self.phone_input.text().strip(),
            'العنوان': self.address_input.toPlainText().strip(),
            'ملاحظات': self.notes_input.toPlainText().strip()
        }

    # التحقق من صحة البيانات قبل الحفظ
    def accept(self):
        data = self.get_data()

        if not data['اسم_الحساب']:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم الحساب")
            return

        super().accept()


# حوار إضافة/تعديل سجل دين
class DebtRecordDialog(QDialog):

    # init
    def __init__(self, parent=None, record_data=None):
        super().__init__(parent)
        self.parent_window = parent
        self.record_data = record_data
        self.setWindowTitle("إضافة سجل دين" if not record_data else "تعديل سجل دين")
        self.setModal(True)
        self.setFixedSize(500, 450)
        self.setLayoutDirection(Qt.RightToLeft)

        self.setup_ui()
        self.load_accounts()
        if record_data:
            self.load_data()

    # إعداد واجهة المستخدم
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # الحساب
        account_layout = QHBoxLayout()
        account_layout.addWidget(QLabel("الحساب:"))
        self.account_combo = QComboBox()
        account_layout.addWidget(self.account_combo)
        layout.addLayout(account_layout)

        # وصف الدين
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("وصف الدين:"))
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("أدخل وصف الدين...")
        desc_layout.addWidget(self.desc_input)
        layout.addLayout(desc_layout)

        # المبلغ
        amount_layout = QHBoxLayout()
        amount_layout.addWidget(QLabel("المبلغ:"))
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("أدخل المبلغ...")
        amount_layout.addWidget(self.amount_input)
        layout.addLayout(amount_layout)

        # تاريخ الدين
        debt_date_layout = QHBoxLayout()
        debt_date_layout.addWidget(QLabel("تاريخ الدين:"))
        self.debt_date = QDateEdit()
        self.debt_date.setDate(QDate.currentDate())
        self.debt_date.setDisplayFormat("dd/MM/yyyy")
        self.debt_date.setCalendarPopup(True)
        debt_date_layout.addWidget(self.debt_date)
        layout.addLayout(debt_date_layout)

        # تاريخ الاستحقاق
        due_date_layout = QHBoxLayout()
        due_date_layout.addWidget(QLabel("تاريخ الاستحقاق:"))
        self.due_date = QDateEdit()
        self.due_date.setDate(QDate.currentDate().addDays(30))
        self.due_date.setDisplayFormat("dd/MM/yyyy")
        self.due_date.setCalendarPopup(True)
        due_date_layout.addWidget(self.due_date)
        layout.addLayout(due_date_layout)

        # حالة الدين
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("حالة الدين:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["معلق", "غير مسدد", "مسدد"])
        status_layout.addWidget(self.status_combo)
        layout.addLayout(status_layout)

        # الملاحظات
        notes_layout = QVBoxLayout()
        notes_layout.addWidget(QLabel("ملاحظات:"))
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("أدخل ملاحظات...")
        self.notes_input.setMaximumHeight(80)
        notes_layout.addWidget(self.notes_input)
        layout.addLayout(notes_layout)

        # أزرار الحفظ والإلغاء
        buttons_layout = QHBoxLayout()
        self.save_btn = QPushButton("حفظ")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.clicked.connect(self.reject)

        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)
        layout.addLayout(buttons_layout)

    # تحميل قائمة الحسابات
    def load_accounts(self):
        if self.parent_window:
            conn = self.parent_window.get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, اسم_الحساب FROM الحسابات_الديون ORDER BY اسم_الحساب")
                    accounts = cursor.fetchall()

                    self.account_combo.clear()
                    for account_id, account_name in accounts:
                        self.account_combo.addItem(account_name, account_id)

                except Exception as e:
                    print(f"خطأ في تحميل الحسابات: {e}")
                finally:
                    conn.close()

    # تحميل البيانات للتعديل
    def load_data(self):
        if self.record_data:
            # تحديد الحساب
            account_id = self.record_data.get('معرف_الحساب')
            for i in range(self.account_combo.count()):
                if self.account_combo.itemData(i) == account_id:
                    self.account_combo.setCurrentIndex(i)
                    break

            self.desc_input.setText(self.record_data.get('وصف_الدين', ''))
            self.amount_input.setText(str(self.record_data.get('المبلغ', '')))

            # تحديد التواريخ
            debt_date = self.record_data.get('تاريخ_الدين')
            if debt_date:
                self.debt_date.setDate(QDate.fromString(str(debt_date), "yyyy-MM-dd"))

            due_date = self.record_data.get('تاريخ_الاستحقاق')
            if due_date:
                self.due_date.setDate(QDate.fromString(str(due_date), "yyyy-MM-dd"))

            self.status_combo.setCurrentText(self.record_data.get('حالة_الدين', 'معلق'))
            self.notes_input.setPlainText(self.record_data.get('ملاحظات', ''))

    # الحصول على البيانات المدخلة
    def get_data(self):
        return {
            'معرف_الحساب': self.account_combo.currentData(),
            'وصف_الدين': self.desc_input.text().strip(),
            'المبلغ': float(self.amount_input.text().strip() or 0),
            'تاريخ_الدين': self.debt_date.date().toString("yyyy-MM-dd"),
            'تاريخ_الاستحقاق': self.due_date.date().toString("yyyy-MM-dd"),
            'حالة_الدين': self.status_combo.currentText(),
            'ملاحظات': self.notes_input.toPlainText().strip()
        }

    # التحقق من صحة البيانات قبل الحفظ
    def accept(self):
        try:
            data = self.get_data()

            if not data['وصف_الدين']:
                QMessageBox.warning(self, "خطأ", "يرجى إدخال وصف الدين")
                return

            if data['المبلغ'] <= 0:
                QMessageBox.warning(self, "خطأ", "يرجى إدخال مبلغ صحيح")
                return

            if not data['معرف_الحساب']:
                QMessageBox.warning(self, "خطأ", "يرجى اختيار الحساب")
                return

            super().accept()

        except ValueError:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال مبلغ صحيح")


# حوار إضافة/تعديل دفعة دين
class DebtPaymentDialog(QDialog):

    # init
    def __init__(self, parent=None, payment_data=None):
        super().__init__(parent)
        self.parent_window = parent
        self.payment_data = payment_data
        self.setWindowTitle("إضافة دفعة دين" if not payment_data else "تعديل دفعة دين")
        self.setModal(True)
        self.setFixedSize(500, 400)
        self.setLayoutDirection(Qt.RightToLeft)

        self.setup_ui()
        self.load_accounts()
        if payment_data:
            self.load_data()

    # إعداد واجهة المستخدم
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # الحساب
        account_layout = QHBoxLayout()
        account_layout.addWidget(QLabel("الحساب:"))
        self.account_combo = QComboBox()
        account_layout.addWidget(self.account_combo)
        layout.addLayout(account_layout)

        # وصف الدفعة
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("وصف الدفعة:"))
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("أدخل وصف الدفعة...")
        desc_layout.addWidget(self.desc_input)
        layout.addLayout(desc_layout)

        # المبلغ
        amount_layout = QHBoxLayout()
        amount_layout.addWidget(QLabel("المبلغ:"))
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("أدخل المبلغ...")
        amount_layout.addWidget(self.amount_input)
        layout.addLayout(amount_layout)

        # تاريخ الدفعة
        payment_date_layout = QHBoxLayout()
        payment_date_layout.addWidget(QLabel("تاريخ الدفعة:"))
        self.payment_date = QDateEdit()
        self.payment_date.setDate(QDate.currentDate())
        self.payment_date.setDisplayFormat("dd/MM/yyyy")
        self.payment_date.setCalendarPopup(True)
        payment_date_layout.addWidget(self.payment_date)
        layout.addLayout(payment_date_layout)

        # طريقة الدفع
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("طريقة الدفع:"))
        self.method_combo = QComboBox()
        self.method_combo.addItems(["نقدي", "شيك", "تحويل بنكي", "بطاقة ائتمان", "أخرى"])
        method_layout.addWidget(self.method_combo)
        layout.addLayout(method_layout)

        # المستلم
        receiver_layout = QHBoxLayout()
        receiver_layout.addWidget(QLabel("المستلم:"))
        self.receiver_input = QLineEdit()
        self.receiver_input.setPlaceholderText("أدخل اسم المستلم...")
        receiver_layout.addWidget(self.receiver_input)
        layout.addLayout(receiver_layout)

        # الملاحظات
        notes_layout = QVBoxLayout()
        notes_layout.addWidget(QLabel("ملاحظات:"))
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("أدخل ملاحظات...")
        self.notes_input.setMaximumHeight(80)
        notes_layout.addWidget(self.notes_input)
        layout.addLayout(notes_layout)

        # أزرار الحفظ والإلغاء
        buttons_layout = QHBoxLayout()
        self.save_btn = QPushButton("حفظ")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.clicked.connect(self.reject)

        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)
        layout.addLayout(buttons_layout)

    # تحميل قائمة الحسابات
    def load_accounts(self):
        if self.parent_window:
            conn = self.parent_window.get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, اسم_الحساب FROM الحسابات_الديون ORDER BY اسم_الحساب")
                    accounts = cursor.fetchall()

                    self.account_combo.clear()
                    for account_id, account_name in accounts:
                        self.account_combo.addItem(account_name, account_id)

                except Exception as e:
                    print(f"خطأ في تحميل الحسابات: {e}")
                finally:
                    conn.close()

    # تحميل البيانات للتعديل
    def load_data(self):
        if self.payment_data:
            # تحديد الحساب
            account_id = self.payment_data.get('معرف_الحساب')
            for i in range(self.account_combo.count()):
                if self.account_combo.itemData(i) == account_id:
                    self.account_combo.setCurrentIndex(i)
                    break

            self.desc_input.setText(self.payment_data.get('وصف_الدفعة', ''))
            self.amount_input.setText(str(self.payment_data.get('المبلغ', '')))

            # تحديد تاريخ الدفعة
            payment_date = self.payment_data.get('تاريخ_السداد')
            if payment_date:
                self.payment_date.setDate(QDate.fromString(str(payment_date), "yyyy-MM-dd"))

            self.method_combo.setCurrentText(self.payment_data.get('طريقة_الدفع', 'نقدي'))
            self.receiver_input.setText(self.payment_data.get('المستلم', ''))
            self.notes_input.setPlainText(self.payment_data.get('ملاحظات', ''))

    # الحصول على البيانات المدخلة
    def get_data(self):
        return {
            'معرف_الحساب': self.account_combo.currentData(),
            'وصف_الدفعة': self.desc_input.text().strip(),
            'المبلغ': float(self.amount_input.text().strip() or 0),
            'تاريخ_السداد': self.payment_date.date().toString("yyyy-MM-dd"),
            'طريقة_الدفع': self.method_combo.currentText(),
            'المستلم': self.receiver_input.text().strip(),
            'ملاحظات': self.notes_input.toPlainText().strip()
        }

    # التحقق من صحة البيانات قبل الحفظ
    def accept(self):
        try:
            data = self.get_data()

            if not data['وصف_الدفعة']:
                QMessageBox.warning(self, "خطأ", "يرجى إدخال وصف الدفعة")
                return

            if data['المبلغ'] <= 0:
                QMessageBox.warning(self, "خطأ", "يرجى إدخال مبلغ صحيح")
                return

            if not data['معرف_الحساب']:
                QMessageBox.warning(self, "خطأ", "يرجى اختيار الحساب")
                return

            super().accept()

        except ValueError:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال مبلغ صحيح")


# إضافة الدوال المفقودة لكلاس DebtsManagementWindow
# حفظ سجل دين جديد
def save_debt_record(self, data):
    conn = self.get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO الحسابات_سجل_الديون
            (معرف_الحساب, `وصف _الدين`, المبلغ, `تاريخ _الدين`, تاريخ_السداد, ملاحظات)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data['معرف_الحساب'], data['وصف_الدين'], data['المبلغ'],
            data['تاريخ_الدين'], data['تاريخ_الاستحقاق'], data['ملاحظات']
        ))
        conn.commit()
        return True

    except Exception as e:
        print(f"خطأ في حفظ سجل الدين: {e}")
        QMessageBox.warning(self, "خطأ", f"فشل في حفظ سجل الدين: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

# الحصول على بيانات سجل دين
def get_debt_record_data(self, record_id):
    conn = self.get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT معرف_الحساب, `وصف _الدين`, المبلغ, `تاريخ _الدين`,
                   تاريخ_السداد, 'معلق' as حالة_الدين, ملاحظات
            FROM الحسابات_سجل_الديون WHERE id = %s
        """, (record_id,))

        result = cursor.fetchone()
        if result:
            return {
                'معرف_الحساب': result[0],
                'وصف_الدين': result[1],
                'المبلغ': result[2],
                'تاريخ_الدين': result[3],
                'تاريخ_الاستحقاق': result[4],
                'حالة_الدين': result[5],
                'ملاحظات': result[6]
            }
        return None

    except Exception as e:
        print(f"خطأ في الحصول على بيانات السجل: {e}")
        return None
    finally:
        if conn:
            conn.close()

# تحديث سجل دين
def update_debt_record(self, record_id, data):
    conn = self.get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE الحسابات_سجل_الديون
            SET معرف_الحساب = %s, `وصف _الدين` = %s, المبلغ = %s,
                `تاريخ _الدين` = %s, تاريخ_السداد = %s, ملاحظات = %s
            WHERE id = %s
        """, (
            data['معرف_الحساب'], data['وصف_الدين'], data['المبلغ'],
            data['تاريخ_الدين'], data['تاريخ_الاستحقاق'],
            data['ملاحظات'], record_id
        ))
        conn.commit()
        return True

    except Exception as e:
        print(f"خطأ في تحديث سجل الدين: {e}")
        QMessageBox.warning(self, "خطأ", f"فشل في تحديث سجل الدين: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

# حذف سجل دين من قاعدة البيانات
def delete_debt_record_from_db(self, record_id):
    conn = self.get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM الحسابات_سجل_الديون WHERE id = %s", (record_id,))
        conn.commit()
        return True

    except Exception as e:
        print(f"خطأ في حذف سجل الدين: {e}")
        QMessageBox.warning(self, "خطأ", f"فشل في حذف سجل الدين: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

# حفظ دفعة دين جديدة
def save_debt_payment(self, data):
    conn = self.get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO الحسابات_سجل_سداد_الديون
            (معرف_الحساب, `وصف_المدفوع`, المبلغ, `تاريخ_السداد`, طريقة_الدفع, ملاحظات)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data['معرف_الحساب'], data['وصف_الدفعة'], data['المبلغ'],
            data['تاريخ_السداد'], data['طريقة_الدفع'], data['ملاحظات']
        ))
        conn.commit()
        return True

    except Exception as e:
        print(f"خطأ في حفظ دفعة الدين: {e}")
        QMessageBox.warning(self, "خطأ", f"فشل في حفظ دفعة الدين: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

# الحصول على بيانات دفعة دين
def get_debt_payment_data(self, payment_id):
    conn = self.get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT معرف_الحساب, `وصف_المدفوع`, المبلغ, `تاريخ_السداد`,
                   طريقة_الدفع, 'غير محدد' as المستلم, ملاحظات
            FROM الحسابات_سجل_سداد_الديون WHERE id = %s
        """, (payment_id,))

        result = cursor.fetchone()
        if result:
            return {
                'معرف_الحساب': result[0],
                'وصف_الدفعة': result[1],
                'المبلغ': result[2],
                'تاريخ_السداد': result[3],
                'طريقة_الدفع': result[4],
                'المستلم': result[5],
                'ملاحظات': result[6]
            }
        return None

    except Exception as e:
        print(f"خطأ في الحصول على بيانات الدفعة: {e}")
        return None
    finally:
        if conn:
            conn.close()

# تحديث دفعة دين
def update_debt_payment(self, payment_id, data):
    conn = self.get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE الحسابات_سجل_سداد_الديون
            SET معرف_الحساب = %s, `وصف_المدفوع` = %s, المبلغ = %s,
                `تاريخ_السداد` = %s, طريقة_الدفع = %s, ملاحظات = %s
            WHERE id = %s
        """, (
            data['معرف_الحساب'], data['وصف_الدفعة'], data['المبلغ'],
            data['تاريخ_السداد'], data['طريقة_الدفع'],
            data['ملاحظات'], payment_id
        ))
        conn.commit()
        return True

    except Exception as e:
        print(f"خطأ في تحديث دفعة الدين: {e}")
        QMessageBox.warning(self, "خطأ", f"فشل في تحديث دفعة الدين: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

# حذف دفعة دين من قاعدة البيانات
def delete_debt_payment_from_db(self, payment_id):
    conn = self.get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM الحسابات_سجل_سداد_الديون WHERE id = %s", (payment_id,))
        conn.commit()
        return True

    except Exception as e:
        print(f"خطأ في حذف دفعة الدين: {e}")
        QMessageBox.warning(self, "خطأ", f"فشل في حذف دفعة الدين: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

# إضافة الدوال كطرق للكلاس
DebtsManagementWindow.save_debt_record = save_debt_record
DebtsManagementWindow.get_debt_record_data = get_debt_record_data
DebtsManagementWindow.update_debt_record = update_debt_record
DebtsManagementWindow.delete_debt_record_from_db = delete_debt_record_from_db
DebtsManagementWindow.save_debt_payment = save_debt_payment
DebtsManagementWindow.get_debt_payment_data = get_debt_payment_data
DebtsManagementWindow.update_debt_payment = update_debt_payment
DebtsManagementWindow.delete_debt_payment_from_db = delete_debt_payment_from_db



