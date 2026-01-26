#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نافذة إدارة الموردين الشاملة
تحتوي على 4 تابات: حسابات الموردين، فواتير الموردين، المدفوعات للموردين، التقارير
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

# إعدادات قاعدة البيانات
db_config = {
    'host': host,
    'user': user,
    'password': password,
    'database': f"project_manager_V2"
}

# استيراد نوافذ الحوار
try:
    from نوافذ_حوار_الموردين import InvoiceDialog, PaymentDialog
except ImportError:
    # في حالة عدم وجود الملف، سيتم إنشاء نوافذ بسيطة
    InvoiceDialog = None
    PaymentDialog = None

# نافذة إدارة الموردين الشاملة
class SuppliersManagementWindow(QMainWindow):
    
    # init
    def __init__(self):
        super().__init__()
        self.setup_window()
        self.create_tabs()
        self.apply_suppliers_styles()
        self.load_all_data()

        # إضافة أزرار الطباعة لجميع التابات
        self.add_print_buttons()
        
    # إعداد النافذة الأساسية
    def setup_window(self):
        self.setWindowTitle("إدارة الموردين")
        self.setGeometry(100, 100, 1600, 1000)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setWindowFlags(Qt.Window | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        
        # التخطيط الرئيسي
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # العنوان الرئيسي
        self.title_label = QLabel()
        self.title_label.setObjectName("main_title")
        self.title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title_label)
        
        # إنشاء التابات
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("suppliers_tab_widget")
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
                title_text = f"إدارة الموردين - {clean_tab_text}"
            else:
                title_text = "إدارة الموردين"
            
            self.title_label.setText(title_text)
            
        except Exception as e:
            print(f"خطأ في تحديث العنوان: {e}")
            self.title_label.setText("إدارة الموردين")
        
    # إنشاء التابات الأربعة
    def create_tabs(self):
        # تاب حسابات الموردين
        self.create_suppliers_accounts_tab()
        
        # تاب فواتير الموردين
        self.create_suppliers_invoices_tab()
        
        # تاب المدفوعات للموردين
        self.create_suppliers_payments_tab()
        
        # تاب التقارير
        self.create_reports_tab()
        
        # تحديث العنوان الأولي
        self.update_title()
        
    # إنشاء تاب حسابات الموردين
    def create_suppliers_accounts_tab(self):
        tab = QWidget()
        tab.setObjectName("suppliers_accounts_tab")
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # الصف الأول: أزرار الإجراءات والفلاتر
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        
        # أزرار الإجراءات
        self.add_supplier_btn = QPushButton("إضافة مورد")
        self.add_supplier_btn.setObjectName("action_button")
        self.add_supplier_btn.setIcon(qta.icon('fa5s.plus', color='white'))
        
        self.edit_supplier_btn = QPushButton("تعديل مورد")
        self.edit_supplier_btn.setObjectName("action_button")
        self.edit_supplier_btn.setIcon(qta.icon('fa5s.edit', color='white'))
        
        self.delete_supplier_btn = QPushButton("حذف مورد")
        self.delete_supplier_btn.setObjectName("action_button")
        self.delete_supplier_btn.setIcon(qta.icon('fa5s.trash', color='white'))
        
        # فلاتر البحث
        self.supplier_category_filter = QComboBox()
        self.supplier_category_filter.setObjectName("filter_combo")
        self.supplier_category_filter.addItem("جميع التصنيفات")
        
        self.supplier_search = QLineEdit()
        self.supplier_search.setObjectName("search_input")
        self.supplier_search.setPlaceholderText("البحث في الموردين...")
        
        # ترتيب العناصر
        actions_layout.addWidget(self.add_supplier_btn)
        actions_layout.addWidget(self.edit_supplier_btn)
        actions_layout.addWidget(self.delete_supplier_btn)
        actions_layout.addStretch()
        actions_layout.addWidget(QLabel("التصنيف:"))
        actions_layout.addWidget(self.supplier_category_filter)
        actions_layout.addWidget(self.supplier_search)
        
        layout.addLayout(actions_layout)
        
        # الصف الثاني: البطاقات الإحصائية
        self.create_suppliers_stats_cards(layout)
        
        # الجدول
        self.suppliers_table = QTableWidget()
        self.suppliers_table.setObjectName("data_table")
        self.suppliers_table.setLayoutDirection(Qt.RightToLeft)
        self.setup_suppliers_table()
        layout.addWidget(self.suppliers_table)
        
        self.tab_widget.addTab(tab, qta.icon('fa5s.users', color='#3498db'), "حسابات الموردين")
        
    # إنشاء تاب فواتير الموردين
    def create_suppliers_invoices_tab(self):
        tab = QWidget()
        tab.setObjectName("suppliers_invoices_tab")
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # الصف الأول: أزرار الإجراءات والفلاتر
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        
        # أزرار الإجراءات
        self.add_invoice_btn = QPushButton("إضافة فاتورة")
        self.add_invoice_btn.setObjectName("action_button")
        self.add_invoice_btn.setIcon(qta.icon('fa5s.plus', color='white'))
        
        self.edit_invoice_btn = QPushButton("تعديل فاتورة")
        self.edit_invoice_btn.setObjectName("action_button")
        self.edit_invoice_btn.setIcon(qta.icon('fa5s.edit', color='white'))
        
        self.delete_invoice_btn = QPushButton("حذف فاتورة")
        self.delete_invoice_btn.setObjectName("action_button")
        self.delete_invoice_btn.setIcon(qta.icon('fa5s.trash', color='white'))
        
        # فلاتر البحث
        self.invoice_supplier_filter = QComboBox()
        self.invoice_supplier_filter.setObjectName("filter_combo")
        self.invoice_supplier_filter.addItem("جميع الموردين")
        
        self.invoice_search = QLineEdit()
        self.invoice_search.setObjectName("search_input")
        self.invoice_search.setPlaceholderText("البحث في الفواتير...")
        
        # ترتيب العناصر
        actions_layout.addWidget(self.add_invoice_btn)
        actions_layout.addWidget(self.edit_invoice_btn)
        actions_layout.addWidget(self.delete_invoice_btn)
        actions_layout.addStretch()
        actions_layout.addWidget(QLabel("المورد:"))
        actions_layout.addWidget(self.invoice_supplier_filter)
        actions_layout.addWidget(self.invoice_search)
        
        layout.addLayout(actions_layout)
        
        # الصف الثاني: البطاقات الإحصائية
        self.create_invoices_stats_cards(layout)
        
        # الجدول
        self.invoices_table = QTableWidget()
        self.invoices_table.setObjectName("data_table")
        self.invoices_table.setLayoutDirection(Qt.RightToLeft)
        self.setup_invoices_table()
        layout.addWidget(self.invoices_table)
        
        self.tab_widget.addTab(tab, qta.icon('fa5s.file-invoice', color='#e74c3c'), "فواتير الموردين")
        
    # إنشاء تاب المدفوعات للموردين
    def create_suppliers_payments_tab(self):
        tab = QWidget()
        tab.setObjectName("suppliers_payments_tab")
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # الصف الأول: أزرار الإجراءات والفلاتر
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        
        # أزرار الإجراءات
        self.add_payment_btn = QPushButton("إضافة دفعة")
        self.add_payment_btn.setObjectName("action_button")
        self.add_payment_btn.setIcon(qta.icon('fa5s.plus', color='white'))
        
        self.edit_payment_btn = QPushButton("تعديل دفعة")
        self.edit_payment_btn.setObjectName("action_button")
        self.edit_payment_btn.setIcon(qta.icon('fa5s.edit', color='white'))
        
        self.delete_payment_btn = QPushButton("حذف دفعة")
        self.delete_payment_btn.setObjectName("action_button")
        self.delete_payment_btn.setIcon(qta.icon('fa5s.trash', color='white'))
        
        # فلاتر البحث
        self.payment_supplier_filter = QComboBox()
        self.payment_supplier_filter.setObjectName("filter_combo")
        self.payment_supplier_filter.addItem("جميع الموردين")
        
        self.payment_method_filter = QComboBox()
        self.payment_method_filter.setObjectName("filter_combo")
        self.payment_method_filter.addItems(["جميع الطرق", "نقدي", "شيك", "تحويل بنكي"])
        
        self.payment_search = QLineEdit()
        self.payment_search.setObjectName("search_input")
        self.payment_search.setPlaceholderText("البحث في المدفوعات...")
        
        # ترتيب العناصر
        actions_layout.addWidget(self.add_payment_btn)
        actions_layout.addWidget(self.edit_payment_btn)
        actions_layout.addWidget(self.delete_payment_btn)
        actions_layout.addStretch()
        actions_layout.addWidget(QLabel("المورد:"))
        actions_layout.addWidget(self.payment_supplier_filter)
        actions_layout.addWidget(QLabel("طريقة الدفع:"))
        actions_layout.addWidget(self.payment_method_filter)
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
        
        self.tab_widget.addTab(tab, qta.icon('fa5s.money-bill-wave', color='#27ae60'), "المدفوعات للموردين")
        
    # إنشاء تاب التقارير
    def create_reports_tab(self):
        tab = QWidget()
        tab.setObjectName("reports_tab")
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # عنوان التقارير
        reports_title = QLabel("تقارير الموردين")
        reports_title.setObjectName("section_title")
        reports_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(reports_title)
        
        # أزرار التقارير
        reports_layout = QGridLayout()
        reports_layout.setSpacing(15)
        
        # تقرير حسابات الموردين
        suppliers_report_btn = QPushButton("تقرير حسابات الموردين")
        suppliers_report_btn.setObjectName("report_button")
        suppliers_report_btn.setIcon(qta.icon('fa5s.chart-bar', color='white'))
        reports_layout.addWidget(suppliers_report_btn, 0, 0)
        
        # تقرير فواتير الموردين
        invoices_report_btn = QPushButton("تقرير فواتير الموردين")
        invoices_report_btn.setObjectName("report_button")
        invoices_report_btn.setIcon(qta.icon('fa5s.chart-line', color='white'))
        reports_layout.addWidget(invoices_report_btn, 0, 1)
        
        # تقرير المدفوعات
        payments_report_btn = QPushButton("تقرير المدفوعات")
        payments_report_btn.setObjectName("report_button")
        payments_report_btn.setIcon(qta.icon('fa5s.chart-pie', color='white'))
        reports_layout.addWidget(payments_report_btn, 1, 0)
        
        # تقرير شامل
        comprehensive_report_btn = QPushButton("التقرير الشامل")
        comprehensive_report_btn.setObjectName("report_button")
        comprehensive_report_btn.setIcon(qta.icon('fa5s.file-alt', color='white'))
        reports_layout.addWidget(comprehensive_report_btn, 1, 1)
        
        layout.addLayout(reports_layout)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, qta.icon('fa5s.chart-bar', color='#f39c12'), "التقارير")

    # تطبيق الأنماط المركزية لنافذة إدارة الموردين
    def apply_suppliers_styles(self):
        # استخدام الستايل الموحد
        from ستايل_نوافذ_الإدارة import apply_to_supplier_management
        apply_to_supplier_management(self)
        
        # تطبيق دعم RTL شامل
        self.apply_rtl_to_all_widgets()

    # تطبيق دعم RTL على جميع العناصر
    def apply_rtl_to_all_widgets(self):
        try:
            # تطبيق RTL على التابات
            if hasattr(self, 'tab_widget'):
                self.tab_widget.setLayoutDirection(Qt.RightToLeft)

            # تطبيق RTL على الجداول
            tables = [
                getattr(self, 'suppliers_table', None),
                getattr(self, 'invoices_table', None),
                getattr(self, 'payments_table', None)
            ]

            for table in tables:
                if table is not None:
                    table.setLayoutDirection(Qt.RightToLeft)
                    # تحسين رؤوس الجداول
                    header = table.horizontalHeader()
                    if header:
                        header.setLayoutDirection(Qt.RightToLeft)
                        header.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)

            # تطبيق RTL على الكومبو بوكسات
            combo_boxes = [
                getattr(self, 'supplier_category_filter', None),
                getattr(self, 'invoice_supplier_filter', None),
                getattr(self, 'payment_supplier_filter', None),
                getattr(self, 'payment_method_filter', None)
            ]

            for combo in combo_boxes:
                if combo is not None:
                    combo.setLayoutDirection(Qt.RightToLeft)

            # تطبيق RTL على حقول البحث
            search_fields = [
                getattr(self, 'supplier_search', None),
                getattr(self, 'invoice_search', None),
                getattr(self, 'payment_search', None)
            ]

            for field in search_fields:
                if field is not None:
                    field.setLayoutDirection(Qt.RightToLeft)

        except Exception as e:
            print(f"خطأ في تطبيق RTL: {e}")

    # إضافة أزرار الطباعة لجميع التابات
    def add_print_buttons(self):
        try:
            # إضافة أزرار الطباعة تلقائياً لجميع التابات
            quick_add_print_button(self, self.tab_widget)

        except Exception as e:
            print(f"خطأ في إضافة أزرار الطباعة: {e}")

    # إنشاء بطاقات إحصائيات الموردين
    def create_suppliers_stats_cards(self, parent_layout):
        stats_container = QWidget()
        stats_container.setObjectName("stats_container")
        stats_layout = QHBoxLayout(stats_container)
        stats_layout.setSpacing(15)

        # بطاقة إجمالي الموردين
        self.total_suppliers_card = self.create_stat_card("إجمالي الموردين", "0", "#3498db")
        stats_layout.addWidget(self.total_suppliers_card)

        # بطاقة إجمالي التوريد
        self.total_supply_card = self.create_stat_card("إجمالي التوريد", f"0 {Currency_type}", "#e74c3c")
        stats_layout.addWidget(self.total_supply_card)

        # بطاقة المدفوع للموردين
        self.total_paid_card = self.create_stat_card("المدفوع للموردين", f"0 {Currency_type}", "#27ae60")
        stats_layout.addWidget(self.total_paid_card)

        # بطاقة الباقي للموردين
        self.total_remaining_card = self.create_stat_card("الباقي للموردين", f"0 {Currency_type}", "#f39c12")
        stats_layout.addWidget(self.total_remaining_card)

        parent_layout.addWidget(stats_container)

    # إنشاء بطاقات إحصائيات الفواتير
    def create_invoices_stats_cards(self, parent_layout):
        stats_container = QWidget()
        stats_container.setObjectName("stats_container")
        stats_layout = QHBoxLayout(stats_container)
        stats_layout.setSpacing(15)

        # بطاقة إجمالي الفواتير
        total_invoices_card = self.create_stat_card("إجمالي الفواتير", "0", "#3498db")
        stats_layout.addWidget(total_invoices_card)

        # بطاقة قيمة الفواتير
        invoices_value_card = self.create_stat_card("قيمة الفواتير", f"0 {Currency_type}", "#e74c3c")
        stats_layout.addWidget(invoices_value_card)

        # بطاقة فواتير هذا الشهر
        this_month_card = self.create_stat_card("فواتير هذا الشهر", "0", "#27ae60")
        stats_layout.addWidget(this_month_card)

        # بطاقة متوسط قيمة الفاتورة
        avg_invoice_card = self.create_stat_card("متوسط قيمة الفاتورة", f"0 {Currency_type}", "#f39c12")
        stats_layout.addWidget(avg_invoice_card)

        parent_layout.addWidget(stats_container)

    # إنشاء بطاقات إحصائيات المدفوعات
    def create_payments_stats_cards(self, parent_layout):
        stats_container = QWidget()
        stats_container.setObjectName("stats_container")
        stats_layout = QHBoxLayout(stats_container)
        stats_layout.setSpacing(15)

        # بطاقة إجمالي المدفوعات
        total_payments_card = self.create_stat_card("إجمالي المدفوعات", "0", "#3498db")
        stats_layout.addWidget(total_payments_card)

        # بطاقة قيمة المدفوعات
        payments_value_card = self.create_stat_card("قيمة المدفوعات", f"0 {Currency_type}", "#e74c3c")
        stats_layout.addWidget(payments_value_card)

        # بطاقة مدفوعات هذا الشهر
        this_month_payments_card = self.create_stat_card("مدفوعات هذا الشهر", f"0 {Currency_type}", "#27ae60")
        stats_layout.addWidget(this_month_payments_card)

        # بطاقة متوسط المدفوعات
        avg_payment_card = self.create_stat_card("متوسط المدفوعات", f"0 {Currency_type}", "#f39c12")
        stats_layout.addWidget(avg_payment_card)

        parent_layout.addWidget(stats_container)

    # إنشاء بطاقة إحصائية
    def create_stat_card(self, title, value, color):
        card = QFrame()
        card.setObjectName("stat_card")
        card.setFrameStyle(QFrame.Box)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)

        # العنوان والقيمة
        title_label = QLabel(title)
        title_label.setObjectName("stat_title")

        value_label = QLabel(value)
        value_label.setObjectName("stat_value")

        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(value_label)

        return card

    # إعداد جدول الموردين
    def setup_suppliers_table(self):
        headers = ["المعرف", "التصنيف", "اسم المورد", "رقم الهاتف", "العنوان",
                  "إجمالي التوريد", "المدفوع للمورد", "الباقي للمورد", "تاريخ الإضافة", "ملاحظات"]

        self.suppliers_table.setColumnCount(len(headers))
        self.suppliers_table.setHorizontalHeaderLabels(headers)
        self.suppliers_table.horizontalHeader().setStretchLastSection(True)
        self.suppliers_table.setAlternatingRowColors(True)
        self.suppliers_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # إعداد قائمة السياق
        setup_table_context_menu(self.suppliers_table, self, "حسابات الموردين", is_main_table=True)

    # إعداد جدول الفواتير
    def setup_invoices_table(self):
        headers = ["المعرف", "المورد", "رقم الفاتورة", "وصف الفاتورة",
                  "المبلغ", "التاريخ", "ملاحظات"]

        self.invoices_table.setColumnCount(len(headers))
        self.invoices_table.setHorizontalHeaderLabels(headers)
        self.invoices_table.horizontalHeader().setStretchLastSection(True)
        self.invoices_table.setAlternatingRowColors(True)
        self.invoices_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # إعداد قائمة السياق
        setup_table_context_menu(self.invoices_table, self, "فواتير الموردين", is_main_table=True)

    # إعداد جدول المدفوعات
    def setup_payments_table(self):
        headers = ["المعرف", "المورد", "وصف الدفعة", "المبلغ", "تاريخ الدفعة",
                  "طريقة الدفع", "المستلم", "ملاحظات"]

        self.payments_table.setColumnCount(len(headers))
        self.payments_table.setHorizontalHeaderLabels(headers)
        self.payments_table.horizontalHeader().setStretchLastSection(True)
        self.payments_table.setAlternatingRowColors(True)
        self.payments_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # إعداد قائمة السياق
        setup_table_context_menu(self.payments_table, self, "مدفوعات الموردين", is_main_table=True)

    # تحميل جميع البيانات
    def load_all_data(self):
        self.load_filter_data()
        self.load_suppliers_data()
        self.load_invoices_data()
        self.load_payments_data()
        self.update_all_statistics()

    # تحميل بيانات الفلاتر
    def load_filter_data(self):
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # تحميل تصنيفات الموردين
            cursor.execute("SELECT DISTINCT التصنيف FROM الموردين WHERE التصنيف IS NOT NULL ORDER BY التصنيف")
            categories = cursor.fetchall()

            if hasattr(self, 'supplier_category_filter'):
                self.supplier_category_filter.clear()
                self.supplier_category_filter.addItem("جميع التصنيفات")
                for category in categories:
                    if category[0]:
                        self.supplier_category_filter.addItem(category[0])

            # تحميل أسماء الموردين للفلاتر
            cursor.execute("SELECT id, اسم_المورد FROM الموردين ORDER BY اسم_المورد")
            suppliers = cursor.fetchall()

            # تحديث فلتر الموردين في تاب الفواتير
            if hasattr(self, 'invoice_supplier_filter'):
                self.invoice_supplier_filter.clear()
                self.invoice_supplier_filter.addItem("جميع الموردين")
                for supplier in suppliers:
                    if supplier[1]:
                        self.invoice_supplier_filter.addItem(supplier[1])

            # تحديث فلتر الموردين في تاب المدفوعات
            if hasattr(self, 'payment_supplier_filter'):
                self.payment_supplier_filter.clear()
                self.payment_supplier_filter.addItem("جميع الموردين")
                for supplier in suppliers:
                    if supplier[1]:
                        self.payment_supplier_filter.addItem(supplier[1])

            conn.close()

        except Exception as e:
            print(f"خطأ في تحميل بيانات الفلاتر: {e}")

    # تحميل بيانات الموردين
    def load_suppliers_data(self):
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, التصنيف, اسم_المورد, رقم_الهاتف, العنوان,
                       اجمالي_التوريد, المدفوع_للمورد, الباقي_للمورد,
                       تاريخ_الإنشاء, ملاحظات
                FROM الموردين
                ORDER BY تاريخ_الإنشاء DESC
            """)

            data = cursor.fetchall()
            self.suppliers_table.setRowCount(len(data))

            for row, record in enumerate(data):
                for col, value in enumerate(record):
                    if value is None:
                        value = ""
                    elif col in [5, 6, 7]:  # أعمدة المبالغ
                        value = f"{value:,.2f} {Currency_type}" if value else f"0.00 {Currency_type}"
                    elif col == 8 and value:  # تاريخ الإضافة
                        value = value.strftime("%Y-%m-%d") if hasattr(value, 'strftime') else str(value)

                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.suppliers_table.setItem(row, col, item)

            conn.close()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في تحميل بيانات الموردين: {str(e)}")

    # تحميل بيانات الفواتير
    def load_invoices_data(self):
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT f.id, m.اسم_المورد, f.رقم_الفاتورة, f.وصف_الفاتورة,
                       f.المبلغ, f.التاريخ, f.ملاحظات
                FROM الحسابات_فواتير_الموردين f
                LEFT JOIN الموردين m ON f.معرف_المورد = m.id
                ORDER BY f.التاريخ DESC
            """)

            data = cursor.fetchall()
            self.invoices_table.setRowCount(len(data))

            for row, record in enumerate(data):
                for col, value in enumerate(record):
                    if value is None:
                        value = ""
                    elif col == 4:  # عمود المبلغ
                        value = f"{value:,.2f} {Currency_type}" if value else f"0.00 {Currency_type}"
                    elif col == 5 and value:  # التاريخ
                        value = value.strftime("%Y-%m-%d") if hasattr(value, 'strftime') else str(value)

                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.invoices_table.setItem(row, col, item)

            conn.close()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في تحميل بيانات الفواتير: {str(e)}")

    # تحميل بيانات المدفوعات
    def load_payments_data(self):
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT d.id, m.اسم_المورد, d.وصف_الدفعة, d.المبلغ,
                       d.تاريخ_الدفعة, d.طريقة_الدفع, d.المستلم, d.ملاحظات
                FROM الحسابات_دفعات_الموردين d
                LEFT JOIN الموردين m ON d.معرف_المورد = m.id
                ORDER BY d.تاريخ_الدفعة DESC
            """)

            data = cursor.fetchall()
            self.payments_table.setRowCount(len(data))

            for row, record in enumerate(data):
                for col, value in enumerate(record):
                    if value is None:
                        value = ""
                    elif col == 3:  # عمود المبلغ
                        value = f"{value:,.2f} {Currency_type}" if value else f"0.00 {Currency_type}"
                    elif col == 4 and value:  # تاريخ الدفعة
                        value = value.strftime("%Y-%m-%d") if hasattr(value, 'strftime') else str(value)

                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.payments_table.setItem(row, col, item)

            conn.close()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في تحميل بيانات المدفوعات: {str(e)}")

    # تحديث جميع الإحصائيات
    def update_all_statistics(self):
        self.update_suppliers_statistics()
        self.update_invoices_statistics()
        self.update_payments_statistics()

    # تحديث إحصائيات الموردين
    def update_suppliers_statistics(self):
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    COUNT(*) as total_suppliers,
                    COALESCE(SUM(اجمالي_التوريد), 0) as total_supply,
                    COALESCE(SUM(المدفوع_للمورد), 0) as total_paid,
                    COALESCE(SUM(الباقي_للمورد), 0) as total_remaining
                FROM الموردين
            """)

            result = cursor.fetchone()
            if result:
                total_suppliers, total_supply, total_paid, total_remaining = result

                # تحديث البطاقات
                if hasattr(self, 'total_suppliers_card'):
                    self.update_stat_card_value(self.total_suppliers_card, str(total_suppliers))

                if hasattr(self, 'total_supply_card'):
                    self.update_stat_card_value(self.total_supply_card, f"{total_supply:,.2f} {Currency_type}")

                if hasattr(self, 'total_paid_card'):
                    self.update_stat_card_value(self.total_paid_card, f"{total_paid:,.2f} {Currency_type}")

                if hasattr(self, 'total_remaining_card'):
                    self.update_stat_card_value(self.total_remaining_card, f"{total_remaining:,.2f} {Currency_type}")

            conn.close()

        except Exception as e:
            print(f"خطأ في تحديث إحصائيات الموردين: {e}")

    # تحديث قيمة البطاقة الإحصائية
    def update_stat_card_value(self, card, new_value):
        try:
            # البحث عن QLabel الذي يحتوي على القيمة
            for child in card.findChildren(QLabel):
                if child.objectName() == "stat_value":
                    child.setText(new_value)
                    break
        except Exception as e:
            print(f"خطأ في تحديث قيمة البطاقة: {e}")

    # تحديث إحصائيات الفواتير
    def update_invoices_statistics(self):
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    COUNT(*) as total_invoices,
                    COALESCE(SUM(المبلغ), 0) as total_value,
                    COUNT(CASE WHEN MONTH(التاريخ) = MONTH(CURDATE())
                              AND YEAR(التاريخ) = YEAR(CURDATE()) THEN 1 END) as this_month_count,
                    COALESCE(AVG(المبلغ), 0) as avg_value
                FROM الحسابات_فواتير_الموردين
            """)

            result = cursor.fetchone()
            if result:
                # تحديث البطاقات (سيتم تنفيذها لاحقاً)
                pass

            conn.close()

        except Exception as e:
            print(f"خطأ في تحديث إحصائيات الفواتير: {e}")

    # تحديث إحصائيات المدفوعات
    def update_payments_statistics(self):
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    COUNT(*) as total_payments,
                    COALESCE(SUM(المبلغ), 0) as total_value,
                    COALESCE(SUM(CASE WHEN MONTH(تاريخ_الدفعة) = MONTH(CURDATE())
                                     AND YEAR(تاريخ_الدفعة) = YEAR(CURDATE())
                                     THEN المبلغ ELSE 0 END), 0) as this_month_value,
                    COALESCE(AVG(المبلغ), 0) as avg_value
                FROM الحسابات_دفعات_الموردين
            """)

            result = cursor.fetchone()
            if result:
                # تحديث البطاقات (سيتم تنفيذها لاحقاً)
                pass

            conn.close()

        except Exception as e:
            print(f"خطأ في تحديث إحصائيات المدفوعات: {e}")

    # ربط الإشارات بالوظائف
    def connect_signals(self):
        try:
            # أزرار حسابات الموردين
            if hasattr(self, 'add_supplier_btn'):
                self.add_supplier_btn.clicked.connect(self.add_supplier)
            if hasattr(self, 'edit_supplier_btn'):
                self.edit_supplier_btn.clicked.connect(self.edit_supplier)
            if hasattr(self, 'delete_supplier_btn'):
                self.delete_supplier_btn.clicked.connect(self.delete_supplier)

            # أزرار الفواتير
            if hasattr(self, 'add_invoice_btn'):
                self.add_invoice_btn.clicked.connect(self.add_invoice)
            if hasattr(self, 'edit_invoice_btn'):
                self.edit_invoice_btn.clicked.connect(self.edit_invoice)
            if hasattr(self, 'delete_invoice_btn'):
                self.delete_invoice_btn.clicked.connect(self.delete_invoice)

            # أزرار المدفوعات
            if hasattr(self, 'add_payment_btn'):
                self.add_payment_btn.clicked.connect(self.add_payment)
            if hasattr(self, 'edit_payment_btn'):
                self.edit_payment_btn.clicked.connect(self.edit_payment)
            if hasattr(self, 'delete_payment_btn'):
                self.delete_payment_btn.clicked.connect(self.delete_payment)

            # فلاتر البحث
            if hasattr(self, 'supplier_search'):
                self.supplier_search.textChanged.connect(self.filter_suppliers)
            if hasattr(self, 'invoice_search'):
                self.invoice_search.textChanged.connect(self.filter_invoices)
            if hasattr(self, 'payment_search'):
                self.payment_search.textChanged.connect(self.filter_payments)

            # فلاتر الكومبو بوكس
            if hasattr(self, 'supplier_category_filter'):
                self.supplier_category_filter.currentTextChanged.connect(self.filter_suppliers)
            if hasattr(self, 'invoice_supplier_filter'):
                self.invoice_supplier_filter.currentTextChanged.connect(self.filter_invoices)
            if hasattr(self, 'payment_supplier_filter'):
                self.payment_supplier_filter.currentTextChanged.connect(self.filter_payments)
            if hasattr(self, 'payment_method_filter'):
                self.payment_method_filter.currentTextChanged.connect(self.filter_payments)

            # النقر المزدوج على الجداول
            if hasattr(self, 'suppliers_table'):
                self.suppliers_table.itemDoubleClicked.connect(self.edit_supplier)
            if hasattr(self, 'invoices_table'):
                self.invoices_table.itemDoubleClicked.connect(self.edit_invoice)
            if hasattr(self, 'payments_table'):
                self.payments_table.itemDoubleClicked.connect(self.edit_payment)

            # تغيير التاب
            if hasattr(self, 'tab_widget'):
                self.tab_widget.currentChanged.connect(self.on_tab_changed)

        except Exception as e:
            print(f"خطأ في ربط الإشارات: {e}")

    # عند تغيير التاب
    def on_tab_changed(self, index):
        try:
            # تحديث العنوان الرئيسي
            self.update_title()
            
            if index == 0:  # تاب الموردين
                self.load_suppliers_data()
                self.update_suppliers_statistics()
            elif index == 1:  # تاب الفواتير
                self.load_invoices_data()
                self.update_invoices_statistics()
            elif index == 2:  # تاب المدفوعات
                self.load_payments_data()
                self.update_payments_statistics()
        except Exception as e:
            print(f"خطأ في تغيير التاب: {e}")

    # وظائف الموردين
    # إضافة مورد جديد
    def add_supplier(self):
        dialog = SupplierDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.load_suppliers_data()
            self.load_filter_data()
            self.update_suppliers_statistics()

    # تعديل مورد
    def edit_supplier(self):
        current_row = self.suppliers_table.currentRow()
        if current_row >= 0:
            row_data = self.get_selected_row_data(self.suppliers_table)
            if row_data:
                dialog = SupplierDialog(self, row_data)
                if dialog.exec() == QDialog.Accepted:
                    self.load_suppliers_data()
                    self.load_filter_data()
                    self.update_suppliers_statistics()
        else:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار مورد للتعديل")

    # حذف مورد
    def delete_supplier(self):
        current_row = self.suppliers_table.currentRow()
        if current_row >= 0:
            row_data = self.get_selected_row_data(self.suppliers_table)
            if row_data:
                supplier_name = row_data.get('اسم_المورد', 'غير محدد')
                reply = QMessageBox.question(self, "تأكيد الحذف",
                                           f"هل أنت متأكد من حذف المورد:\n{supplier_name}؟\n\nسيتم حذف جميع الفواتير والمدفوعات المرتبطة به.",
                                           QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    try:
                        conn = mysql.connector.connect(**db_config)
                        cursor = conn.cursor()

                        supplier_id = row_data.get('المعرف')

                        # حذف المدفوعات المرتبطة
                        cursor.execute("DELETE FROM الحسابات_دفعات_الموردين WHERE معرف_المورد = %s", (supplier_id,))

                        # حذف الفواتير المرتبطة
                        cursor.execute("DELETE FROM الحسابات_فواتير_الموردين WHERE معرف_المورد = %s", (supplier_id,))

                        # حذف المورد
                        cursor.execute("DELETE FROM الموردين WHERE id = %s", (supplier_id,))

                        conn.commit()
                        conn.close()

                        QMessageBox.information(self, "نجح", "تم حذف المورد بنجاح")
                        self.load_suppliers_data()
                        self.load_filter_data()
                        self.update_suppliers_statistics()

                    except Exception as e:
                        QMessageBox.critical(self, "خطأ", f"فشل في حذف المورد: {str(e)}")
        else:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار مورد للحذف")

    # وظائف الفواتير
    # إضافة فاتورة جديدة
    def add_invoice(self):
        if InvoiceDialog is None:
            QMessageBox.information(self, "إضافة فاتورة", "نافذة إضافة الفواتير غير متوفرة حالياً")
            return

        dialog = InvoiceDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.load_invoices_data()
            self.load_suppliers_data()  # تحديث جدول الموردين
            self.update_all_statistics()

    # تعديل فاتورة
    def edit_invoice(self):
        if InvoiceDialog is None:
            QMessageBox.information(self, "تعديل فاتورة", "نافذة تعديل الفواتير غير متوفرة حالياً")
            return

        current_row = self.invoices_table.currentRow()
        if current_row >= 0:
            row_data = self.get_selected_row_data(self.invoices_table)
            if row_data:
                dialog = InvoiceDialog(self, row_data)
                if dialog.exec() == QDialog.Accepted:
                    self.load_invoices_data()
                    self.load_suppliers_data()  # تحديث جدول الموردين
                    self.update_all_statistics()
        else:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار فاتورة للتعديل")

    # حذف فاتورة
    def delete_invoice(self):
        current_row = self.invoices_table.currentRow()
        if current_row >= 0:
            row_data = self.get_selected_row_data(self.invoices_table)
            if row_data:
                invoice_desc = row_data.get('وصف_الفاتورة', 'غير محدد')
                reply = QMessageBox.question(self, "تأكيد الحذف",
                                           f"هل أنت متأكد من حذف الفاتورة:\n{invoice_desc}؟",
                                           QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    try:
                        conn = mysql.connector.connect(**db_config)
                        cursor = conn.cursor()

                        invoice_id = row_data.get('المعرف')
                        supplier_id = None
                        old_amount = 0

                        # الحصول على معرف المورد والمبلغ القديم
                        cursor.execute("SELECT معرف_المورد, المبلغ FROM الحسابات_فواتير_الموردين WHERE id = %s", (invoice_id,))
                        result = cursor.fetchone()
                        if result:
                            supplier_id, old_amount = result

                        # حذف الفاتورة
                        cursor.execute("DELETE FROM الحسابات_فواتير_الموردين WHERE id = %s", (invoice_id,))

                        # تحديث إجمالي التوريد للمورد
                        if supplier_id:
                            self.update_supplier_totals(cursor, supplier_id)

                        conn.commit()
                        conn.close()

                        QMessageBox.information(self, "نجح", "تم حذف الفاتورة بنجاح")
                        self.load_invoices_data()
                        self.load_suppliers_data()
                        self.update_all_statistics()

                    except Exception as e:
                        QMessageBox.critical(self, "خطأ", f"فشل في حذف الفاتورة: {str(e)}")
        else:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار فاتورة للحذف")

    # وظائف المدفوعات
    # إضافة دفعة جديدة
    def add_payment(self):
        if PaymentDialog is None:
            QMessageBox.information(self, "إضافة دفعة", "نافذة إضافة المدفوعات غير متوفرة حالياً")
            return

        dialog = PaymentDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.load_payments_data()
            self.load_suppliers_data()  # تحديث جدول الموردين
            self.update_all_statistics()

    # تعديل دفعة
    def edit_payment(self):
        if PaymentDialog is None:
            QMessageBox.information(self, "تعديل دفعة", "نافذة تعديل المدفوعات غير متوفرة حالياً")
            return

        current_row = self.payments_table.currentRow()
        if current_row >= 0:
            row_data = self.get_selected_row_data(self.payments_table)
            if row_data:
                dialog = PaymentDialog(self, row_data)
                if dialog.exec() == QDialog.Accepted:
                    self.load_payments_data()
                    self.load_suppliers_data()  # تحديث جدول الموردين
                    self.update_all_statistics()
        else:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار دفعة للتعديل")

    # حذف دفعة
    def delete_payment(self):
        current_row = self.payments_table.currentRow()
        if current_row >= 0:
            row_data = self.get_selected_row_data(self.payments_table)
            if row_data:
                payment_desc = row_data.get('وصف_الدفعة', 'غير محدد')
                reply = QMessageBox.question(self, "تأكيد الحذف",
                                           f"هل أنت متأكد من حذف الدفعة:\n{payment_desc}؟",
                                           QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    try:
                        conn = mysql.connector.connect(**db_config)
                        cursor = conn.cursor()

                        payment_id = row_data.get('المعرف')
                        supplier_id = None

                        # الحصول على معرف المورد
                        cursor.execute("SELECT معرف_المورد FROM الحسابات_دفعات_الموردين WHERE id = %s", (payment_id,))
                        result = cursor.fetchone()
                        if result:
                            supplier_id = result[0]

                        # حذف الدفعة
                        cursor.execute("DELETE FROM الحسابات_دفعات_الموردين WHERE id = %s", (payment_id,))

                        # تحديث إجمالي المدفوعات للمورد
                        if supplier_id:
                            self.update_supplier_totals(cursor, supplier_id)

                        conn.commit()
                        conn.close()

                        QMessageBox.information(self, "نجح", "تم حذف الدفعة بنجاح")
                        self.load_payments_data()
                        self.load_suppliers_data()
                        self.update_all_statistics()

                    except Exception as e:
                        QMessageBox.critical(self, "خطأ", f"فشل في حذف الدفعة: {str(e)}")
        else:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار دفعة للحذف")

    # وظائف الفلترة
    # فلترة الموردين
    def filter_suppliers(self):
        search_text = self.supplier_search.text().lower()
        category_filter = self.supplier_category_filter.currentText()

        for row in range(self.suppliers_table.rowCount()):
            show_row = True

            # فلترة النص
            if search_text:
                row_text = ""
                for col in range(self.suppliers_table.columnCount()):
                    item = self.suppliers_table.item(row, col)
                    if item:
                        row_text += item.text().lower() + " "
                if search_text not in row_text:
                    show_row = False

            # فلترة التصنيف
            if category_filter != "جميع التصنيفات":
                category_item = self.suppliers_table.item(row, 1)  # عمود التصنيف
                if category_item and category_item.text() != category_filter:
                    show_row = False

            self.suppliers_table.setRowHidden(row, not show_row)

    # فلترة الفواتير
    def filter_invoices(self):
        search_text = self.invoice_search.text().lower()
        supplier_filter = self.invoice_supplier_filter.currentText()

        for row in range(self.invoices_table.rowCount()):
            show_row = True

            # فلترة النص
            if search_text:
                row_text = ""
                for col in range(self.invoices_table.columnCount()):
                    item = self.invoices_table.item(row, col)
                    if item:
                        row_text += item.text().lower() + " "
                if search_text not in row_text:
                    show_row = False

            # فلترة المورد
            if supplier_filter != "جميع الموردين":
                supplier_item = self.invoices_table.item(row, 1)  # عمود المورد
                if supplier_item and supplier_item.text() != supplier_filter:
                    show_row = False

            self.invoices_table.setRowHidden(row, not show_row)

    # فلترة المدفوعات
    def filter_payments(self):
        search_text = self.payment_search.text().lower()
        supplier_filter = self.payment_supplier_filter.currentText()
        method_filter = self.payment_method_filter.currentText()

        for row in range(self.payments_table.rowCount()):
            show_row = True

            # فلترة النص
            if search_text:
                row_text = ""
                for col in range(self.payments_table.columnCount()):
                    item = self.payments_table.item(row, col)
                    if item:
                        row_text += item.text().lower() + " "
                if search_text not in row_text:
                    show_row = False

            # فلترة المورد
            if supplier_filter != "جميع الموردين":
                supplier_item = self.payments_table.item(row, 1)  # عمود المورد
                if supplier_item and supplier_item.text() != supplier_filter:
                    show_row = False

            # فلترة طريقة الدفع
            if method_filter != "جميع الطرق":
                method_item = self.payments_table.item(row, 5)  # عمود طريقة الدفع
                if method_item and method_item.text() != method_filter:
                    show_row = False

            self.payments_table.setRowHidden(row, not show_row)

    # تحديث إجماليات المورد (إجمالي التوريد والمدفوع)
    def update_supplier_totals(self, cursor, supplier_id):
        try:
            # حساب إجمالي التوريد من الفواتير
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0)
                FROM الحسابات_فواتير_الموردين
                WHERE معرف_المورد = %s
            """, (supplier_id,))
            total_supply = cursor.fetchone()[0] or 0

            # حساب إجمالي المدفوع من الدفعات
            cursor.execute("""
                SELECT COALESCE(SUM(المبلغ), 0)
                FROM الحسابات_دفعات_الموردين
                WHERE معرف_المورد = %s
            """, (supplier_id,))
            total_paid = cursor.fetchone()[0] or 0

            # تحديث جدول الموردين
            cursor.execute("""
                UPDATE الموردين
                SET اجمالي_التوريد = %s, المدفوع_للمورد = %s
                WHERE id = %s
            """, (total_supply, total_paid, supplier_id))

        except Exception as e:
            print(f"خطأ في تحديث إجماليات المورد: {e}")

    # معالجة النقر المزدوج على الجدول
    def handle_table_double_click(self, item):
        try:
            # تحديد الجدول الذي تم النقر عليه
            table = item.tableWidget()
            current_row = table.currentRow()

            if current_row < 0:
                return

            # تحديد نوع الجدول والإجراء المناسب
            if table == self.suppliers_table:
                self.edit_supplier()
            elif table == self.invoices_table:
                self.edit_invoice()
            elif table == self.payments_table:
                self.edit_payment()

        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في معالجة النقر المزدوج: {str(e)}")

    # الحصول على بيانات الصف المحدد
    def get_selected_row_data(self, table):
        try:
            current_row = table.currentRow()
            if current_row < 0:
                return None

            row_data = {}
            for col in range(table.columnCount()):
                header_item = table.horizontalHeaderItem(col)
                if header_item:
                    header_text = header_item.text().strip()
                    item = table.item(current_row, col)
                    if item:
                        # محاولة الحصول على البيانات الأصلية أولاً
                        value = item.data(Qt.UserRole)
                        if value is None:
                            value = item.text()
                        row_data[header_text] = value

            return row_data

        except Exception as e:
            print(f"خطأ في الحصول على بيانات الصف: {e}")
            return None

# نافذة إضافة/تعديل مورد
class SupplierDialog(QDialog):

    # init
    def __init__(self, parent=None, supplier_data=None):
        super().__init__(parent)
        self.supplier_data = supplier_data
        self.is_edit_mode = supplier_data is not None
        self.setup_ui()
        self.apply_dialog_styles()

        if self.is_edit_mode:
            self.load_supplier_data()

    # إعداد واجهة النافذة
    def setup_ui(self):
        title = "تعديل مورد" if self.is_edit_mode else "إضافة مورد جديد"
        self.setWindowTitle(title)
        self.setFixedSize(500, 400)
        self.setLayoutDirection(Qt.RightToLeft)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # العنوان
        title_label = QLabel(title)
        title_label.setObjectName("dialog_title")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # النموذج
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # التصنيف
        self.category_combo = QComboBox()
        self.category_combo.setObjectName("form_input")
        self.category_combo.setEditable(True)
        self.load_categories()
        form_layout.addRow("التصنيف:", self.category_combo)

        # اسم المورد
        self.name_input = QLineEdit()
        self.name_input.setObjectName("form_input")
        form_layout.addRow("اسم المورد:", self.name_input)

        # رقم الهاتف
        self.phone_input = QLineEdit()
        self.phone_input.setObjectName("form_input")
        form_layout.addRow("رقم الهاتف:", self.phone_input)

        # العنوان
        self.address_input = QLineEdit()
        self.address_input.setObjectName("form_input")
        form_layout.addRow("العنوان:", self.address_input)

        # الملاحظات
        self.notes_input = QTextEdit()
        self.notes_input.setObjectName("form_input")
        self.notes_input.setMaximumHeight(80)
        form_layout.addRow("ملاحظات:", self.notes_input)

        layout.addLayout(form_layout)

        # الأزرار
        buttons_layout = QHBoxLayout()

        self.save_btn = QPushButton("حفظ")
        self.save_btn.setObjectName("save_button")
        self.save_btn.clicked.connect(self.save_supplier)

        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setObjectName("cancel_button")
        self.cancel_btn.clicked.connect(self.reject)

        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)
        layout.addLayout(buttons_layout)

    # تحميل التصنيفات
    def load_categories(self):
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            cursor.execute("SELECT DISTINCT التصنيف FROM الموردين WHERE التصنيف IS NOT NULL ORDER BY التصنيف")
            categories = cursor.fetchall()

            self.category_combo.addItem("")  # خيار فارغ
            for category in categories:
                if category[0]:
                    self.category_combo.addItem(category[0])

            conn.close()

        except Exception as e:
            print(f"خطأ في تحميل التصنيفات: {e}")

    # تحميل بيانات المورد للتعديل
    def load_supplier_data(self):
        if self.supplier_data:
            self.category_combo.setCurrentText(str(self.supplier_data.get('التصنيف', '')))
            self.name_input.setText(str(self.supplier_data.get('اسم_المورد', '')))
            self.phone_input.setText(str(self.supplier_data.get('رقم_الهاتف', '')))
            self.address_input.setText(str(self.supplier_data.get('العنوان', '')))
            self.notes_input.setPlainText(str(self.supplier_data.get('ملاحظات', '')))

    # حفظ بيانات المورد
    def save_supplier(self):
        # التحقق من صحة البيانات
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم المورد")
            return

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            category = self.category_combo.currentText().strip()
            name = self.name_input.text().strip()
            phone = self.phone_input.text().strip()
            address = self.address_input.text().strip()
            notes = self.notes_input.toPlainText().strip()

            if self.is_edit_mode:
                # تعديل مورد موجود
                supplier_id = self.supplier_data.get('المعرف')
                cursor.execute("""
                    UPDATE الموردين
                    SET التصنيف = %s, اسم_المورد = %s, رقم_الهاتف = %s,
                        العنوان = %s, ملاحظات = %s
                    WHERE id = %s
                """, (category, name, phone, address, notes, supplier_id))

                message = "تم تعديل المورد بنجاح"
            else:
                # إضافة مورد جديد
                cursor.execute("""
                    INSERT INTO الموردين
                    (التصنيف, اسم_المورد, رقم_الهاتف, العنوان, ملاحظات, تاريخ_الإنشاء)
                    VALUES (%s, %s, %s, %s, %s, CURDATE())
                """, (category, name, phone, address, notes))

                message = "تم إضافة المورد بنجاح"

            conn.commit()
            conn.close()

            QMessageBox.information(self, "نجح", message)
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ المورد: {str(e)}")

    # تطبيق الأنماط الموحدة للنافذة
    def apply_dialog_styles(self):
        # استخدام النظام الموحد للستايل
        from ستايل_نوافذ_الإدارة import apply_to_supplier_management
        apply_to_supplier_management(self)
        
        # تطبيق دعم RTL
        self.setLayoutDirection(Qt.RightToLeft)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SuppliersManagementWindow()
    window.connect_signals()  # ربط الإشارات
    window.show()
    sys.exit(app.exec())
